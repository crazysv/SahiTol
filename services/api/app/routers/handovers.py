"""Handover Proposals, Confirmations, Disputes, and QR Verification router.
Implements T023: immutable client proposal and canonical hash (SAHITOL-JCS-1 SHA-256),
authenticated recycler confirmation, collector acknowledgement of revised terms,
duplicate-safe idempotent outcomes, disputes, voiding pending records, versioned receipts,
and public redacted verification responses.

Specifications: docs/16_API_CONTRACT.md, docs/04_APPFLOW.md, docs/06_SCHEMA.md.
Requirements: R-HAND-01, R-HAND-02, R-HAND-03, R-HAND-04, R-HAND-05, R-DATA-04.
Acceptance cases: AT-029, AT-030, AT-031, AT-032, AT-033, AT-056.
"""
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.audit import DomainEvent, QualityFlag
from app.db.models.auth import User
from app.db.models.collector import Collector
from app.db.models.facility import Facility, FacilityUser, Region
from app.db.models.lot import LocationRecord, Lot
from app.db.models.material import Material
from app.db.models.trade import (
    Handover,
    HandoverConfirmation,
    LotRequest,
    Offer,
    TermsRevision,
    Transaction,
)
from app.domain.canonical import compute_canonical_hash
from app.domain.quality import POLICY_VERSION, evaluate_weight_variance
from app.security import UserRole, get_current_user, require_roles

router = APIRouter(tags=["handovers"])

# The only server-created counterparty permitted by the demo import endpoint.
# It deliberately matches auth.py and trade.py so an offline proposal, the
# Android live directory, and the recycler browser console all use one demo
# facility.  This is not used for live accounts.
DEMO_RECYCLER_FACILITY_ID = uuid.uuid5(uuid.NAMESPACE_DNS, "fac-sim-01")

NON_EPR_STATUTORY_NOTICE = (
    "This Digital Handover Record certifies platform receipt and material transfer only. "
    "It does not constitute a statutory EPR certificate under E-Waste (Management) Rules, 2022."
)


def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Normalize datetime to UTC for safe comparisons across SQLite and Postgres."""
    if dt is None:
        return None
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt


def record_handover_event(
    db: Session,
    aggregate_id: uuid.UUID,
    event_type: str,
    actor_id: uuid.UUID,
    role: str,
    previous_state: Optional[str],
    next_state: Optional[str],
    payload: Dict[str, Any]
) -> DomainEvent:
    """Record an append-only domain event on aggregate HANDOVER with SHA-256 hash chaining."""
    last_event = db.execute(
        select(DomainEvent)
        .where(DomainEvent.aggregate_id == aggregate_id)
        .order_by(desc(DomainEvent.sequence))
        .limit(1)
    ).scalar_one_or_none()

    sequence = (last_event.sequence + 1) if last_event else 1
    prev_hash = last_event.event_hash if last_event else "0" * 64

    canonical_payload_hash = compute_canonical_hash(payload)
    event_hash = hashlib.sha256(
        f"{prev_hash}:{sequence}:{event_type}:{canonical_payload_hash}".encode("utf-8")
    ).hexdigest()

    event = DomainEvent(
        aggregate_type="HANDOVER",
        aggregate_id=aggregate_id,
        sequence=sequence,
        event_type=event_type,
        actor_id=actor_id,
        role=role,
        received_at_server=datetime.now(timezone.utc),
        previous_state=previous_state,
        next_state=next_state,
        payload_json=payload,
        prev_hash=prev_hash,
        event_hash=event_hash,
        schema_version="v1.0"
    )
    db.add(event)
    return event


def is_handover_collector(current_user: User, tx: Transaction) -> bool:
    """Verify that current user is the collector of this transaction."""
    if current_user.role == UserRole.ADMIN.value:
        return True
    if tx.collector_id == current_user.id:
        return True
    if current_user.collector and tx.collector_id == current_user.collector.id:
        return True
    return False


def is_handover_facility_member(current_user: User, facility_id: uuid.UUID, db: Session) -> bool:
    """Verify that current user is an active member of this facility."""
    if current_user.role == UserRole.ADMIN.value:
        return True
    fu = (
        db.query(FacilityUser)
        .filter(
            FacilityUser.user_id == current_user.id,
            FacilityUser.facility_id == facility_id,
            FacilityUser.active == True
        )
        .first()
    )
    return fu is not None


# --- Pydantic Schemas ---

class CreateHandoverRequest(BaseModel):
    id: uuid.UUID
    proposal_payload: Dict[str, Any]
    proposal_hash: str = Field(..., min_length=64, max_length=64)
    expected_version: Optional[int] = None


class DemoHandoverImportRequest(CreateHandoverRequest):
    """A demo-only bridge from an offline Android proposal to the real API flow.

    The client payload and hash remain immutable.  The endpoint only provisions
    the prerequisite *demo* lot/offer/transaction records; it then invokes the
    same authenticated handover creation path used by non-demo accounts.
    """


class HandoverResponse(BaseModel):
    id: uuid.UUID
    transaction_id: uuid.UUID
    lot_id: uuid.UUID
    status: str
    proposal_hash: str
    public_token: Optional[str] = None
    version: int
    created_at: datetime
    updated_at: datetime


class ConfirmHandoverInput(BaseModel):
    expected_version: int
    proposal_hash: str = Field(..., min_length=64, max_length=64)
    measured_material_id: Optional[str] = None
    measured_weight_g: Optional[int] = Field(None, gt=0)
    final_total_paise: Optional[int] = Field(None, ge=0)
    condition: Optional[str] = None
    notes: Optional[str] = None


class AcknowledgeTermsInput(BaseModel):
    terms_hash: str = Field(..., min_length=64, max_length=64)
    expected_version: int


class DisputeHandoverInput(BaseModel):
    reason: str = Field(..., min_length=5, description="Dispute explanation")
    proposed_correction: Optional[str] = None
    expected_version: int


class VoidHandoverInput(BaseModel):
    reason: str = Field(..., min_length=5, description="Reason for voiding pending handover")
    expected_version: int


class HandoverConfirmationSummary(BaseModel):
    confirmed_at: datetime
    recycler_user_id: uuid.UUID
    terms_revision_id: Optional[uuid.UUID] = None


class HandoverDetailResponse(BaseModel):
    id: uuid.UUID
    transaction_id: uuid.UUID
    lot_id: uuid.UUID
    status: str
    proposal_hash: str
    proposal_payload: Dict[str, Any]
    version: int
    created_at: datetime
    updated_at: datetime
    confirmation: Optional[HandoverConfirmationSummary] = None
    terms_revisions: List[Dict[str, Any]] = Field(default_factory=list)


class HandoverReceiptResponse(BaseModel):
    handover_id: uuid.UUID
    transaction_id: uuid.UUID
    lot_id: uuid.UUID
    status: str
    proposal_hash: str
    confirmed_at: Optional[datetime] = None
    collector_display: str
    facility_name: str
    facility_kind: str
    facility_address: str
    measured_material_id: Optional[str] = None
    measured_weight_g: Optional[int] = None
    agreed_total_paise: Optional[int] = None
    currency: str = "INR"
    non_epr_notice: str = NON_EPR_STATUTORY_NOTICE
    version: int


class PublicVerificationResponse(BaseModel):
    handover_id: uuid.UUID
    status: str
    occurred_at: Optional[str] = None
    facility_name: str
    material_id: Optional[str] = None
    regulatory_route: Optional[str] = None
    weight_kg: Optional[float] = None
    proposal_hash: str
    non_epr_notice: str = NON_EPR_STATUTORY_NOTICE


# --- Handover Endpoints ---

@router.post("/handovers/verify-hash")
@router.post("/api/v1/handovers/verify-hash")
def verify_proposal_hash(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Verify proposal canonical hash matching SAHITOL-JCS-1 specification."""
    computed_hash = compute_canonical_hash(payload)
    return {
        "canonical_hash": computed_hash,
        "is_valid": True
    }


@router.post("/handovers", response_model=HandoverResponse, status_code=status.HTTP_201_CREATED)
@router.post("/api/v1/handovers", response_model=HandoverResponse, status_code=status.HTTP_201_CREATED)
def create_handover(
    req: CreateHandoverRequest,
    response: Response,
    current_user: User = Depends(require_roles(UserRole.COLLECTOR, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Submit immutable client handover proposal and canonical hash (R-HAND-01, AT-029)."""
    # 1. Wire ID consistency check
    payload = req.proposal_payload
    payload_id_str = payload.get("handover_id")
    if str(req.id) != str(payload_id_str):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Mismatched handover ID: body id '{req.id}' != proposal_payload.handover_id '{payload_id_str}'."
        )

    # 2. Hash integrity verification
    computed_hash = compute_canonical_hash(payload)
    if computed_hash != req.proposal_hash:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Proposal hash mismatch: expected {computed_hash}, but received {req.proposal_hash}."
        )

    # 3. Idempotent check: if already exists
    existing = db.query(Handover).filter(Handover.id == req.id).first()
    if existing:
        if existing.proposal_hash == req.proposal_hash:
            response.status_code = status.HTTP_200_OK
            return HandoverResponse(
                id=existing.id,
                transaction_id=existing.transaction_id,
                lot_id=existing.lot_id,
                status=existing.status,
                proposal_hash=existing.proposal_hash,
                public_token=None,  # Do not reissue token on replay
                version=existing.version,
                created_at=existing.created_at,
                updated_at=existing.updated_at
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflict: Handover ID already exists with different payload hash."
        )

    # 4. Resolve and validate linked Transaction
    tx_id_str = payload.get("transaction_id")
    if not tx_id_str:
        raise HTTPException(status_code=422, detail="Missing required 'transaction_id' in proposal payload.")
    try:
        tx_id = uuid.UUID(tx_id_str)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid 'transaction_id' UUID.")

    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Referenced transaction not found.")

    # 5. Ownership verification
    if not is_handover_collector(current_user, tx):
        raise HTTPException(status_code=403, detail="Forbidden: You are not the collector for this transaction.")

    # 6. Lot validation
    lot_id_str = payload.get("lot_id")
    if str(tx.lot_id) != str(lot_id_str):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Lot ID mismatch: transaction lot '{tx.lot_id}' != proposal lot '{lot_id_str}'."
        )
    lot = db.query(Lot).filter(Lot.id == tx.lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Referenced lot not found.")

    # 7. Facility validation
    facility_id_str = payload.get("facility_id")
    if str(tx.facility_id) != str(facility_id_str):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Facility ID mismatch: transaction facility '{tx.facility_id}' != proposal facility '{facility_id_str}'."
        )

    # 8. Transaction lifecycle check
    if tx.lifecycle not in {"AGREED", "IN_TRANSIT"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Transaction in state '{tx.lifecycle}' is not eligible for handover proposal."
        )

    # 9. Generate public verification token
    raw_public_token = secrets.token_urlsafe(32)
    public_token_hash = hashlib.sha256(raw_public_token.encode("utf-8")).hexdigest()

    now = datetime.now(timezone.utc)
    occurred_at_str = payload.get("occurred_at")
    try:
        occurred_at = datetime.fromisoformat(occurred_at_str.replace("Z", "+00:00")) if occurred_at_str else now
    except Exception:
        occurred_at = now

    handover = Handover(
        id=req.id,
        transaction_id=tx.id,
        lot_id=lot.id,
        proposal_payload_json=payload,
        proposal_hash=req.proposal_hash,
        schema_version=payload.get("schema_version", "SAHITOL-HANDOVER-1"),
        proposed_by=current_user.id,
        proposed_at_client=occurred_at,
        received_at_server=now,
        status="PENDING_CONFIRMATION",
        public_token_hash=public_token_hash,
        version=1,
        created_at=now,
        updated_at=now
    )
    db.add(handover)

    # Advance Lot status to HANDED_OVER
    lot.status = "HANDED_OVER"
    lot.version += 1
    lot.updated_at = now

    # Advance Transaction lifecycle to IN_TRANSIT
    tx.lifecycle = "IN_TRANSIT"
    tx.version += 1
    tx.updated_at = now

    record_handover_event(
        db=db,
        aggregate_id=handover.id,
        event_type="HANDOVER_PROPOSED",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state=None,
        next_state="PENDING_CONFIRMATION",
        payload={
            "handover_id": str(handover.id),
            "transaction_id": str(tx.id),
            "lot_id": str(lot.id),
            "proposal_hash": req.proposal_hash,
            "public_token_hash": public_token_hash
        }
    )

    db.commit()
    db.refresh(handover)

    return HandoverResponse(
        id=handover.id,
        transaction_id=handover.transaction_id,
        lot_id=handover.lot_id,
        status=handover.status,
        proposal_hash=handover.proposal_hash,
        public_token=raw_public_token,
        version=handover.version,
        created_at=handover.created_at,
        updated_at=handover.updated_at
    )


@router.post("/demo/handovers/import", response_model=HandoverResponse)
@router.post("/api/v1/demo/handovers/import", response_model=HandoverResponse)
def import_demo_handover(
    req: DemoHandoverImportRequest,
    response: Response,
    current_user: User = Depends(require_roles(UserRole.COLLECTOR)),
    db: Session = Depends(get_db),
):
    """Synchronize an offline proposal through real handover authorization.

    This is deliberately restricted to a signed-in demo collector.  It creates
    only missing demo prerequisites and then delegates to :func:`create_handover`;
    the QR still has no authority to confirm a receipt.
    """
    if not current_user.is_demo or not current_user.collector:
        raise HTTPException(status_code=403, detail="Demo handover import is available only to demo collectors.")

    payload = req.proposal_payload
    try:
        lot_id = uuid.UUID(str(payload["lot_id"]))
        transaction_id = uuid.UUID(str(payload["transaction_id"]))
        facility_id = uuid.UUID(str(payload["facility_id"]))
    except (KeyError, ValueError, TypeError):
        raise HTTPException(status_code=422, detail="Demo proposal must contain UUID lot, transaction, and facility IDs.")
    if facility_id != DEMO_RECYCLER_FACILITY_ID:
        raise HTTPException(status_code=422, detail="Demo proposal references an unknown demo facility.")
    if not bool(payload.get("is_demo")):
        raise HTTPException(status_code=422, detail="Demo import requires an explicitly demo-labelled proposal.")

    material_id = str(payload.get("material_snapshot", {}).get("material_id", ""))
    material = db.query(Material).filter(Material.id == material_id, Material.active == True).first()
    if not material:
        raise HTTPException(status_code=422, detail="Demo proposal references an unknown active material.")
    weight = payload.get("weight_snapshot", {}).get("measured_weight_g") or payload.get("weight_snapshot", {}).get("estimated_weight_g")
    value = payload.get("value_snapshot", {}).get("agreed_total_paise")
    if not isinstance(weight, int) or weight <= 0 or not isinstance(value, int) or value < 0:
        raise HTTPException(status_code=422, detail="Demo proposal has invalid weight or agreed value.")

    now = datetime.now(timezone.utc)
    region = db.query(Region).filter(Region.id == "DELHI_NCR").first()
    if not region:
        db.add(Region(id="DELHI_NCR", name="Delhi-NCR", state_code="DL", kind="METRO"))
        db.flush()

    recycler = db.query(User).filter(User.phone_normalized == "d_r_yard_operator").first()
    if not recycler:
        recycler = User(
            phone_normalized="d_r_yard_operator",
            pin_hash="demo-only-no-pin-login",
            role=UserRole.RECYCLER.value,
            account_state="ACTIVE",
            is_demo=True,
            version=1,
            created_at=now,
            updated_at=now,
        )
        db.add(recycler)
        db.flush()

    facility = db.query(Facility).filter(Facility.id == facility_id).first()
    if not facility:
        facility = Facility(
            id=facility_id,
            name="SahiTol Demo Recycler Yard",
            facility_name="SahiTol Demo Recycler Yard",
            kind="RECYCLER",
            address_public="Mayapuri Industrial Area (demo)",
            district="West Delhi",
            state="Delhi",
            region_id="DELHI_NCR",
            contact_public=None,
            active=True,
            version=1,
            created_at=now,
            updated_at=now,
        )
        db.add(facility)
    membership = db.query(FacilityUser).filter(
        FacilityUser.user_id == recycler.id, FacilityUser.facility_id == facility_id
    ).first()
    if not membership:
        db.add(FacilityUser(user_id=recycler.id, facility_id=facility_id, membership_role="OPERATOR", active=True))

    lot = db.query(Lot).filter(Lot.id == lot_id).first()
    if not lot:
        lot = Lot(
            id=lot_id,
            collector_id=current_user.collector.id,
            material_id=material_id,
            regulatory_route=payload.get("material_snapshot", {}).get("regulatory_route") or material.default_route,
            estimated_weight_g=weight,
            condition=payload.get("material_snapshot", {}).get("condition"),
            status="MATCHED",
            origin_class="DEMO",
            source_kind="DEMO_SYNTHETIC",
            is_demo=True,
            version=1,
            created_at=now,
            updated_at=now,
        )
        db.add(lot)
        db.flush()
    elif lot.collector_id != current_user.collector.id:
        raise HTTPException(status_code=403, detail="Demo lot belongs to another collector.")

    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        request = LotRequest(
            lot_id=lot_id, facility_id=facility_id, created_by=current_user.id,
            state="ACCEPTED", reason="Demo prerequisite", created_at=now,
        )
        db.add(request)
        db.flush()
        offer = Offer(
            request_id=request.id, lot_id=lot_id, facility_id=facility_id,
            rate_paise_per_kg=None, fixed_total_paise=value, price_basis="FIXED_TOTAL",
            condition=lot.condition or "GOOD", weight_basis_g=weight,
            expires_at=now + timedelta(days=1), status="ACCEPTED",
            terms_hash=compute_canonical_hash({"demo": True, "lot_id": str(lot_id), "value": value, "weight": weight}),
            version=1, created_at=now, updated_at=now,
        )
        db.add(offer)
        db.flush()
        tx = Transaction(
            id=transaction_id, lot_id=lot_id, collector_id=current_user.collector.id,
            facility_id=facility_id, accepted_offer_id=offer.id,
            estimated_weight_g=weight, agreed_weight_g=weight,
            quoted_total_paise=value, agreed_total_paise=value,
            lifecycle="AGREED", is_demo=True, version=1,
            created_at=now, updated_at=now,
        )
        db.add(tx)
        db.flush()
    elif tx.collector_id != current_user.collector.id or tx.facility_id != facility_id or tx.lot_id != lot_id:
        raise HTTPException(status_code=409, detail="Demo transaction conflicts with the proposal linkage.")

    return create_handover(req, response, current_user, db)


@router.get("/lots/{lot_id}/handover", response_model=HandoverDetailResponse)
@router.get("/api/v1/lots/{lot_id}/handover", response_model=HandoverDetailResponse)
def get_latest_lot_handover(
    lot_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Recover the latest authorized handover for a persisted lot after an app restart.

    The client persists a lot ID durably, while a process restart can occur
    before a server-issued handover ID is cached. This lookup is participant
    scoped and delegates detail authorization to the canonical handover read.
    """
    handover = (
        db.query(Handover)
        .filter(Handover.lot_id == lot_id)
        .order_by(desc(Handover.created_at))
        .first()
    )
    if not handover:
        raise HTTPException(status_code=404, detail="No handover exists for this lot.")
    return get_handover(handover.id, current_user, db)


@router.get("/handovers/{id}", response_model=HandoverDetailResponse)
@router.get("/api/v1/handovers/{id}", response_model=HandoverDetailResponse)
def get_handover(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve handover proposal, revisions, confirmation, and status for authorized participants."""
    handover = db.query(Handover).filter(Handover.id == id).first()
    if not handover:
        raise HTTPException(status_code=404, detail="Handover not found.")

    tx = db.query(Transaction).filter(Transaction.id == handover.transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    # Scoped authorization
    if current_user.role != UserRole.ADMIN.value:
        is_col = is_handover_collector(current_user, tx)
        is_fac = is_handover_facility_member(current_user, tx.facility_id, db)
        if not (is_col or is_fac):
            raise HTTPException(status_code=403, detail="Forbidden: You are not a participant in this handover.")

    conf_summary = None
    if handover.confirmation:
        conf_summary = HandoverConfirmationSummary(
            confirmed_at=handover.confirmation.confirmed_at,
            recycler_user_id=handover.confirmation.recycler_user_id,
            terms_revision_id=handover.confirmation.terms_revision_id
        )

    revisions_list = []
    for r in tx.terms_revisions:
        revisions_list.append({
            "id": str(r.id),
            "final_material_id": r.final_material_id,
            "measured_weight_g": r.measured_weight_g,
            "final_total_paise": r.final_total_paise,
            "currency": r.currency,
            "proposed_by": r.proposed_by,
            "collector_ack_at": r.collector_ack_at.isoformat() if r.collector_ack_at else None,
            "recycler_ack_at": r.recycler_ack_at.isoformat() if r.recycler_ack_at else None,
            "terms_hash": r.terms_hash,
            "reason": r.reason
        })

    return HandoverDetailResponse(
        id=handover.id,
        transaction_id=handover.transaction_id,
        lot_id=handover.lot_id,
        status=handover.status,
        proposal_hash=handover.proposal_hash,
        proposal_payload=handover.proposal_payload_json,
        version=handover.version,
        created_at=handover.created_at,
        updated_at=handover.updated_at,
        confirmation=conf_summary,
        terms_revisions=revisions_list
    )


@router.post("/handovers/{id}/confirm")
@router.post("/api/v1/handovers/{id}/confirm")
def confirm_handover(
    id: uuid.UUID,
    payload: ConfirmHandoverInput,
    current_user: User = Depends(require_roles(UserRole.RECYCLER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Recycler confirms receipt or proposes changed terms revision (R-HAND-02, AT-030).
    If measured weight/grade/price differ from agreed terms, transitions to PENDING_COLLECTOR_ACK.
    If measured values match agreed terms, transitions directly to CONFIRMED.
    """
    handover = db.query(Handover).filter(Handover.id == id).first()
    if not handover:
        raise HTTPException(status_code=404, detail="Handover not found.")

    tx = db.query(Transaction).filter(Transaction.id == handover.transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    # Facility membership authorization
    if not is_handover_facility_member(current_user, tx.facility_id, db):
        raise HTTPException(status_code=403, detail="Forbidden: You are not an active member of this facility.")

    # Version check
    if handover.version != payload.expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Version conflict: handover is at version {handover.version}, expected {payload.expected_version}."
        )

    # Hash check
    if handover.proposal_hash != payload.proposal_hash:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Proposal hash mismatch. Cannot confirm against conflicting proposal hash."
        )

    # Allowed initial states
    if handover.status not in {"PENDING_CONFIRMATION", "PENDING_COLLECTOR_ACK"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot confirm handover in state '{handover.status}'."
        )

    now = datetime.now(timezone.utc)
    lot = db.query(Lot).filter(Lot.id == handover.lot_id).first()

    # Determine latest agreed revision
    latest_rev = (
        db.query(TermsRevision)
        .filter(TermsRevision.transaction_id == tx.id)
        .order_by(desc(TermsRevision.proposed_at))
        .first()
    )

    measured_weight = payload.measured_weight_g or (latest_rev.measured_weight_g if latest_rev else tx.estimated_weight_g)
    measured_material = payload.measured_material_id or (latest_rev.final_material_id if latest_rev else (lot.material_id or "UNKNOWN"))
    measured_paise = payload.final_total_paise if payload.final_total_paise is not None else (latest_rev.final_total_paise if latest_rev else tx.quoted_total_paise)

    # Check for discrepancy against current agreed terms
    has_weight_discrepancy = latest_rev and (measured_weight != latest_rev.measured_weight_g)
    has_material_discrepancy = latest_rev and (measured_material != latest_rev.final_material_id)
    has_paise_discrepancy = latest_rev and (measured_paise != latest_rev.final_total_paise)

    if has_weight_discrepancy or has_material_discrepancy or has_paise_discrepancy:
        # Discrepancy detected: Recycler proposes a new terms revision!
        # Collector must explicitly review and acknowledge (R-HAND-02 / AT-030).
        rev_terms_payload = {
            "transaction_id": str(tx.id),
            "handover_id": str(handover.id),
            "final_material_id": measured_material,
            "measured_weight_g": measured_weight,
            "final_total_paise": measured_paise,
            "proposed_by": "FACILITY",
            "proposed_at": now.isoformat(),
            "reason": payload.notes or "Recycler measured differences upon receipt"
        }
        rev_terms_hash = compute_canonical_hash(rev_terms_payload)

        new_rev = TermsRevision(
            id=uuid.uuid4(),
            transaction_id=tx.id,
            previous_revision_id=latest_rev.id if latest_rev else None,
            final_material_id=measured_material,
            measured_weight_g=measured_weight,
            final_total_paise=measured_paise,
            currency="INR",
            proposed_by="FACILITY",
            proposed_at=now,
            recycler_ack_at=now,
            collector_ack_at=None,  # Pending collector review
            terms_hash=rev_terms_hash,
            reason=payload.notes or "Recycler measured differences upon receipt"
        )
        db.add(new_rev)

        # Check weight variance rule under QUALITY_V1 (AT-033)
        if has_weight_discrepancy and tx.estimated_weight_g and tx.estimated_weight_g > 0:
            variance_res = evaluate_weight_variance(tx.estimated_weight_g, measured_weight)
            if not variance_res.passed:
                db.add(QualityFlag(
                    id=uuid.uuid4(),
                    entity_type="HANDOVER",
                    entity_id=handover.id,
                    entity_version=handover.version,
                    rule_id=variance_res.rule_id,
                    policy_version=POLICY_VERSION,
                    severity=variance_res.severity.value,
                    evidence_json=variance_res.details,
                    reason=variance_res.reason,
                    status="OPEN",
                    created_at=now,
                    updated_at=now
                ))

        handover.status = "PENDING_COLLECTOR_ACK"
        handover.agreed_terms_revision_id = new_rev.id
        handover.version += 1
        handover.updated_at = now

        record_handover_event(
            db=db,
            aggregate_id=handover.id,
            event_type="HANDOVER_TERMS_REVISED",
            actor_id=current_user.id,
            role=current_user.role,
            previous_state="PENDING_CONFIRMATION",
            next_state="PENDING_COLLECTOR_ACK",
            payload={
                "handover_id": str(handover.id),
                "terms_revision_id": str(new_rev.id),
                "terms_hash": rev_terms_hash,
                "measured_weight_g": measured_weight,
                "measured_material_id": measured_material,
                "final_total_paise": measured_paise
            }
        )

        db.commit()
        return {
            "status": "PENDING_COLLECTOR_ACK",
            "handover_id": str(handover.id),
            "version": handover.version,
            "terms_revision_id": str(new_rev.id),
            "terms_hash": rev_terms_hash,
            "message": "Measured differences recorded. Awaiting collector acknowledgement of revised terms."
        }

    # No discrepancy: Mutually confirmed!
    prev_handover_status = handover.status
    handover.status = "CONFIRMED"
    handover.version += 1
    handover.updated_at = now

    conf = HandoverConfirmation(
        id=uuid.uuid4(),
        handover_id=handover.id,
        terms_revision_id=latest_rev.id if latest_rev else None,
        recycler_user_id=current_user.id,
        confirmed_at=now
    )
    db.add(conf)

    # Advance Transaction lifecycle
    tx.agreed_weight_g = measured_weight
    tx.agreed_total_paise = measured_paise
    tx.lifecycle = "CONFIRMED"
    tx.version += 1
    tx.updated_at = now

    # Advance Lot status
    if lot:
        lot.status = "RECEIVED"
        lot.version += 1
        lot.updated_at = now

    record_handover_event(
        db=db,
        aggregate_id=handover.id,
        event_type="HANDOVER_CONFIRMED",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state=prev_handover_status,
        next_state="CONFIRMED",
        payload={
            "handover_id": str(handover.id),
            "transaction_id": str(tx.id),
            "lot_id": str(lot.id) if lot else None,
            "confirmed_by": str(current_user.id),
            "measured_weight_g": measured_weight,
            "final_total_paise": measured_paise
        }
    )

    db.commit()
    return {
        "status": "CONFIRMED",
        "handover_id": str(handover.id),
        "version": handover.version,
        "message": "Handover confirmed successfully."
    }


@router.post("/handovers/{id}/acknowledge-terms")
@router.post("/api/v1/handovers/{id}/acknowledge-terms")
def acknowledge_handover_terms(
    id: uuid.UUID,
    payload: AcknowledgeTermsInput,
    current_user: User = Depends(require_roles(UserRole.COLLECTOR, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Collector explicitly acknowledges revised terms proposed by recycler (R-HAND-02, AT-030)."""
    handover = db.query(Handover).filter(Handover.id == id).first()
    if not handover:
        raise HTTPException(status_code=404, detail="Handover not found.")

    tx = db.query(Transaction).filter(Transaction.id == handover.transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    if not is_handover_collector(current_user, tx):
        raise HTTPException(status_code=403, detail="Forbidden: You are not the collector for this handover.")

    if handover.version != payload.expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Version conflict: handover is at version {handover.version}, expected {payload.expected_version}."
        )

    if handover.status != "PENDING_COLLECTOR_ACK":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot acknowledge terms on handover in state '{handover.status}'."
        )

    # Retrieve latest revision
    latest_rev = (
        db.query(TermsRevision)
        .filter(TermsRevision.transaction_id == tx.id)
        .order_by(desc(TermsRevision.proposed_at))
        .first()
    )
    if not latest_rev or latest_rev.terms_hash != payload.terms_hash:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Terms hash mismatch. The acknowledged terms do not match the latest proposed revision."
        )

    now = datetime.now(timezone.utc)
    latest_rev.collector_ack_at = now

    handover.status = "CONFIRMED"
    handover.version += 1
    handover.updated_at = now

    # Ensure HandoverConfirmation is recorded
    if not handover.confirmation:
        conf = HandoverConfirmation(
            id=uuid.uuid4(),
            handover_id=handover.id,
            terms_revision_id=latest_rev.id,
            recycler_user_id=tx.facility_id,
            confirmed_at=now
        )
        db.add(conf)

    # Advance Transaction
    tx.agreed_weight_g = latest_rev.measured_weight_g
    tx.agreed_total_paise = latest_rev.final_total_paise
    tx.lifecycle = "CONFIRMED"
    tx.version += 1
    tx.updated_at = now

    # Advance Lot
    lot = db.query(Lot).filter(Lot.id == handover.lot_id).first()
    if lot:
        lot.status = "RECEIVED"
        lot.version += 1
        lot.updated_at = now

    record_handover_event(
        db=db,
        aggregate_id=handover.id,
        event_type="TERMS_ACKNOWLEDGED",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state="PENDING_COLLECTOR_ACK",
        next_state="CONFIRMED",
        payload={
            "handover_id": str(handover.id),
            "terms_revision_id": str(latest_rev.id),
            "terms_hash": latest_rev.terms_hash,
            "collector_ack_at": now.isoformat()
        }
    )

    db.commit()
    return {
        "status": "CONFIRMED",
        "handover_id": str(handover.id),
        "version": handover.version,
        "message": "Revised terms acknowledged and handover confirmed."
    }


@router.post("/handovers/{id}/dispute")
@router.post("/api/v1/handovers/{id}/dispute")
def dispute_handover(
    id: uuid.UUID,
    payload: DisputeHandoverInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Participant records a dispute without rewriting facts (R-HAND-04, AT-032)."""
    handover = db.query(Handover).filter(Handover.id == id).first()
    if not handover:
        raise HTTPException(status_code=404, detail="Handover not found.")

    tx = db.query(Transaction).filter(Transaction.id == handover.transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    if current_user.role != UserRole.ADMIN.value:
        is_col = is_handover_collector(current_user, tx)
        is_fac = is_handover_facility_member(current_user, tx.facility_id, db)
        if not (is_col or is_fac):
            raise HTTPException(status_code=403, detail="Forbidden: You are not a participant in this handover.")

    if handover.version != payload.expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Version conflict: handover is at version {handover.version}, expected {payload.expected_version}."
        )

    now = datetime.now(timezone.utc)
    prev_state = handover.status
    handover.status = "DISPUTED"
    handover.version += 1
    handover.updated_at = now

    record_handover_event(
        db=db,
        aggregate_id=handover.id,
        event_type="HANDOVER_DISPUTED",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state=prev_state,
        next_state="DISPUTED",
        payload={
            "handover_id": str(handover.id),
            "disputed_by": str(current_user.id),
            "reason": payload.reason,
            "proposed_correction": payload.proposed_correction
        }
    )

    db.commit()
    return {
        "status": "DISPUTED",
        "handover_id": str(handover.id),
        "version": handover.version,
        "reason": payload.reason
    }


@router.post("/handovers/{id}/void")
@router.post("/api/v1/handovers/{id}/void")
def void_handover(
    id: uuid.UUID,
    payload: VoidHandoverInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Void pending handover proposal before confirmation (R-HAND-04, AT-032). Confirmed records cannot be voided."""
    handover = db.query(Handover).filter(Handover.id == id).first()
    if not handover:
        raise HTTPException(status_code=404, detail="Handover not found.")

    tx = db.query(Transaction).filter(Transaction.id == handover.transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    if current_user.role != UserRole.ADMIN.value:
        is_col = is_handover_collector(current_user, tx)
        is_fac = is_handover_facility_member(current_user, tx.facility_id, db)
        if not (is_col or is_fac):
            raise HTTPException(status_code=403, detail="Forbidden: You are not a participant in this handover.")

    if handover.status == "CONFIRMED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Forbidden: Confirmed handovers cannot be voided. Compensating correction or dispute required."
        )

    if handover.version != payload.expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Version conflict: handover is at version {handover.version}, expected {payload.expected_version}."
        )

    now = datetime.now(timezone.utc)
    prev_state = handover.status
    handover.status = "VOIDED"
    handover.version += 1
    handover.updated_at = now

    # Revert Lot status to ACCEPTED
    lot = db.query(Lot).filter(Lot.id == handover.lot_id).first()
    if lot and lot.status == "HANDED_OVER":
        lot.status = "ACCEPTED"
        lot.version += 1
        lot.updated_at = now

    # Revert Transaction lifecycle to AGREED
    if tx.lifecycle == "IN_TRANSIT":
        tx.lifecycle = "AGREED"
        tx.version += 1
        tx.updated_at = now

    record_handover_event(
        db=db,
        aggregate_id=handover.id,
        event_type="HANDOVER_VOIDED",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state=prev_state,
        next_state="VOIDED",
        payload={
            "handover_id": str(handover.id),
            "voided_by": str(current_user.id),
            "reason": payload.reason
        }
    )

    db.commit()
    return {
        "status": "VOIDED",
        "handover_id": str(handover.id),
        "version": handover.version,
        "reason": payload.reason
    }


@router.get("/handovers/{id}/receipt", response_model=HandoverReceiptResponse)
@router.get("/api/v1/handovers/{id}/receipt", response_model=HandoverReceiptResponse)
def get_handover_receipt(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve versioned platform handover receipt with statutory non-EPR notice (R-HAND-05, AT-033)."""
    handover = db.query(Handover).filter(Handover.id == id).first()
    if not handover:
        raise HTTPException(status_code=404, detail="Handover not found.")

    tx = db.query(Transaction).filter(Transaction.id == handover.transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    if current_user.role != UserRole.ADMIN.value:
        is_col = is_handover_collector(current_user, tx)
        is_fac = is_handover_facility_member(current_user, tx.facility_id, db)
        if not (is_col or is_fac):
            raise HTTPException(status_code=403, detail="Forbidden: You are not a participant in this handover.")

    facility = db.query(Facility).filter(Facility.id == tx.facility_id).first()

    # Collector display name/alias
    collector_display = "Collector"
    collector = db.query(Collector).filter(Collector.id == tx.collector_id).first()
    if collector and collector.display_alias:
        collector_display = collector.display_alias

    latest_rev = (
        db.query(TermsRevision)
        .filter(TermsRevision.transaction_id == tx.id)
        .order_by(desc(TermsRevision.proposed_at))
        .first()
    )

    return HandoverReceiptResponse(
        handover_id=handover.id,
        transaction_id=tx.id,
        lot_id=handover.lot_id,
        status=handover.status,
        proposal_hash=handover.proposal_hash,
        confirmed_at=handover.confirmation.confirmed_at if handover.confirmation else None,
        collector_display=collector_display,
        facility_name=facility.name if facility else "Formal Recycler",
        facility_kind=facility.kind if facility else "RECYCLER",
        facility_address=facility.address_public if facility else "Industrial Area",
        measured_material_id=latest_rev.final_material_id if latest_rev else None,
        measured_weight_g=latest_rev.measured_weight_g if latest_rev else tx.agreed_weight_g,
        agreed_total_paise=latest_rev.final_total_paise if latest_rev else tx.agreed_total_paise,
        currency="INR",
        non_epr_notice=NON_EPR_STATUTORY_NOTICE,
        version=handover.version
    )


@router.get("/verify/{public_token}", response_model=PublicVerificationResponse)
@router.get("/api/v1/verify/{public_token}", response_model=PublicVerificationResponse)
def verify_public_token(
    public_token: str,
    db: Session = Depends(get_db)
):
    """Public redacted capability endpoint: verifies receipt without auth, omitting PII and financial terms (R-HAND-05, AT-033)."""
    token_hash = hashlib.sha256(public_token.encode("utf-8")).hexdigest()

    handover = db.query(Handover).filter(Handover.public_token_hash == token_hash).first()
    if not handover:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or unverified handover token."
        )

    tx = db.query(Transaction).filter(Transaction.id == handover.transaction_id).first()
    facility = db.query(Facility).filter(Facility.id == tx.facility_id).first() if tx else None
    lot = db.query(Lot).filter(Lot.id == handover.lot_id).first()

    payload = handover.proposal_payload_json or {}
    occurred_at_str = payload.get("occurred_at")

    latest_rev = None
    if tx:
        latest_rev = (
            db.query(TermsRevision)
            .filter(TermsRevision.transaction_id == tx.id)
            .order_by(desc(TermsRevision.proposed_at))
            .first()
        )

    weight_g = None
    if latest_rev:
        weight_g = latest_rev.measured_weight_g
    elif tx and tx.agreed_weight_g:
        weight_g = tx.agreed_weight_g
    elif lot and lot.estimated_weight_g:
        weight_g = lot.estimated_weight_g

    weight_kg = (round(weight_g / 1000.0, 2)) if weight_g else None

    mat_id = (latest_rev.final_material_id if latest_rev else None) or (lot.material_id if lot else None)
    route = (lot.regulatory_route if lot else None)

    return PublicVerificationResponse(
        handover_id=handover.id,
        status=handover.status,
        occurred_at=occurred_at_str,
        facility_name=facility.name if facility else "Formal Recycler",
        material_id=mat_id,
        regulatory_route=route,
        weight_kg=weight_kg,
        proposal_hash=handover.proposal_hash,
        non_epr_notice=NON_EPR_STATUTORY_NOTICE
    )
