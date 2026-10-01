"""Trade router: Recycler Profiles, Lot Requests, Offers, and Transactions.
Implements T021: facility-user membership linkage, self-declared operational profile,
material/rate/pickup updates, incoming requests, offer/reject/expiry, collector acceptance
with one active agreement, cancellation, and immutable agreed terms.

Specifications: docs/16_API_CONTRACT.md, docs/04_APPFLOW.md, docs/06_SCHEMA.md.
Requirements: R-OFFER-01, R-OFFER-02, R-REC-03, R-PRICE-04, R-DATA-03.
Acceptance cases: AT-019, AT-023, AT-027, AT-028, AT-055.
"""
import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import desc, func, select, update
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.audit import DomainEvent, QualityFlag
from app.db.models.auth import User
from app.db.models.collector import Collector
from app.db.models.price import PriceObservation
from app.db.models.facility import (
    Facility,
    FacilityAuthorization,
    FacilityMaterial,
    FacilityOperation,
    FacilityRate,
    FacilityUser,
)
from app.db.models.lot import LocationRecord, Lot, LotImage, MediaObject
from app.db.models.material import Material
from app.db.models.trade import (
    Handover,
    LotRequest,
    Offer,
    PaymentEntry,
    TermsRevision,
    Transaction,
)
from app.domain.canonical import compute_canonical_hash
from app.domain.quality import POLICY_VERSION, evaluate_price_quote, evaluate_repeated_sale
from app.security import UserRole, get_current_user, require_roles

router = APIRouter(tags=["trade"])


def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Normalize datetime to UTC for safe comparisons across SQLite and Postgres."""
    if dt is None:
        return None
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt


def record_trade_event(
    db: Session,
    aggregate_type: str,
    aggregate_id: uuid.UUID,
    event_type: str,
    actor_id: uuid.UUID,
    role: str,
    previous_state: Optional[str],
    next_state: Optional[str],
    payload: Dict[str, Any]
) -> DomainEvent:
    """Record an append-only domain event with SHA-256 hash chaining."""
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
        aggregate_type=aggregate_type,
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


def get_user_facility(
    current_user: User,
    db: Session,
    facility_id: Optional[uuid.UUID] = None
) -> Facility:
    """Resolve facility for authenticated recycler or admin."""
    if current_user.role == UserRole.ADMIN.value:
        if facility_id:
            fac = db.query(Facility).filter(Facility.id == facility_id, Facility.active == True).first()
            if not fac:
                raise HTTPException(status_code=404, detail="Facility not found.")
            return fac
        fac = db.query(Facility).filter(Facility.active == True).first()
        if not fac:
            raise HTTPException(status_code=404, detail="No active facilities found.")
        return fac

    query = (
        db.query(FacilityUser)
        .filter(
            FacilityUser.user_id == current_user.id,
            FacilityUser.active == True
        )
    )
    if facility_id:
        query = query.filter(FacilityUser.facility_id == facility_id)

    fu = query.first()
    if not fu:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user is not an active member of this facility."
        )
    fac = db.query(Facility).filter(Facility.id == fu.facility_id, Facility.active == True).first()
    if not fac:
        raise HTTPException(status_code=404, detail="Facility not found or inactive.")
    return fac


def is_lot_owner(current_user: User, lot: Lot) -> bool:
    """Check if current user is owner of lot (supporting user_id or collector_id)."""
    if current_user.role == UserRole.ADMIN.value:
        return True
    if lot.collector_id == current_user.id:
        return True
    if current_user.collector and lot.collector_id == current_user.collector.id:
        return True
    return False


def is_transaction_collector(current_user: User, tx: Transaction) -> bool:
    """Check if current user is collector party of transaction."""
    if current_user.role == UserRole.ADMIN.value:
        return True
    if tx.collector_id == current_user.id:
        return True
    if current_user.collector and tx.collector_id == current_user.collector.id:
        return True
    return False


def compute_offer_terms_hash(
    offer_id: uuid.UUID,
    request_id: uuid.UUID,
    lot_id: uuid.UUID,
    facility_id: uuid.UUID,
    price_basis: str,
    rate_paise_per_kg: Optional[int],
    fixed_total_paise: Optional[int],
    condition: str,
    weight_basis_g: Optional[int],
    expires_at: datetime
) -> str:
    """Compute canonical hash of offer agreed terms."""
    terms_dict = {
        "offer_id": str(offer_id),
        "request_id": str(request_id),
        "lot_id": str(lot_id),
        "facility_id": str(facility_id),
        "price_basis": str(price_basis),
        "rate_paise_per_kg": int(rate_paise_per_kg) if rate_paise_per_kg is not None else None,
        "fixed_total_paise": int(fixed_total_paise) if fixed_total_paise is not None else None,
        "condition": str(condition),
        "weight_basis_g": int(weight_basis_g) if weight_basis_g is not None else None,
        "expires_at": ensure_utc(expires_at).isoformat(),
    }
    return compute_canonical_hash(terms_dict)


# --- Request & Response Schemas ---

class CreateLotRequestInput(BaseModel):
    facility_id: uuid.UUID
    notes: Optional[str] = None


class LotRequestResponse(BaseModel):
    id: uuid.UUID
    lot_id: uuid.UUID
    facility_id: uuid.UUID
    created_by: uuid.UUID
    state: str
    reason: Optional[str] = None
    created_at: datetime


class CreateOfferInput(BaseModel):
    price_basis: str = Field("RATE_PER_KG", description="RATE_PER_KG or FIXED_TOTAL")
    rate_paise_per_kg: Optional[int] = Field(None, gt=0, description="Paise per kg if RATE_PER_KG")
    fixed_total_paise: Optional[int] = Field(None, gt=0, description="Total paise if FIXED_TOTAL")
    condition: str = Field("INTACT", description="INTACT, PARTIAL, SCRAP, etc.")
    weight_basis_g: Optional[int] = Field(None, gt=0)
    expires_at: Optional[datetime] = Field(None, description="Offer expiration datetime")
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_pricing(self) -> "CreateOfferInput":
        if self.price_basis == "RATE_PER_KG":
            if self.rate_paise_per_kg is None or self.rate_paise_per_kg <= 0:
                raise ValueError("rate_paise_per_kg must be provided and > 0 for RATE_PER_KG price basis.")
        elif self.price_basis == "FIXED_TOTAL":
            if self.fixed_total_paise is None or self.fixed_total_paise <= 0:
                raise ValueError("fixed_total_paise must be provided and > 0 for FIXED_TOTAL price basis.")
        else:
            raise ValueError(f"Unsupported price_basis '{self.price_basis}'. Must be RATE_PER_KG or FIXED_TOTAL.")
        return self


class OfferResponse(BaseModel):
    id: uuid.UUID
    request_id: uuid.UUID
    lot_id: uuid.UUID
    facility_id: uuid.UUID
    price_basis: str
    rate_paise_per_kg: Optional[int] = None
    fixed_total_paise: Optional[int] = None
    condition: str
    weight_basis_g: Optional[int] = None
    expires_at: datetime
    status: str
    is_expired: bool = False
    effective_rate_paise_per_kg: Optional[int] = None
    terms_hash: str
    version: int
    created_at: datetime
    updated_at: datetime


class RejectRequestInput(BaseModel):
    reason: str = Field(..., min_length=3, description="Reason for rejection")


class WithdrawOfferInput(BaseModel):
    expected_version: int
    reason: Optional[str] = None


class AcceptOfferInput(BaseModel):
    terms_hash: str = Field(..., min_length=64, max_length=64, description="Canonical terms SHA-256 hash")
    expected_version: int


class TermsRevisionSummary(BaseModel):
    id: uuid.UUID
    final_material_id: str
    measured_weight_g: int
    final_total_paise: int
    currency: str
    proposed_by: str
    collector_ack_at: Optional[datetime] = None
    recycler_ack_at: Optional[datetime] = None
    terms_hash: str
    reason: Optional[str] = None


class TransactionDetailResponse(BaseModel):
    id: uuid.UUID
    lot_id: uuid.UUID
    collector_id: uuid.UUID
    facility_id: uuid.UUID
    accepted_offer_id: uuid.UUID
    estimated_weight_g: int
    agreed_weight_g: Optional[int] = None
    quoted_total_paise: int
    agreed_total_paise: Optional[int] = None
    currency: str
    lifecycle: str
    version: int
    is_demo: bool
    created_at: datetime
    updated_at: datetime
    revisions: List[TermsRevisionSummary] = Field(default_factory=list)


class IncomingLotSummary(BaseModel):
    lot_id: uuid.UUID
    material_id: Optional[str] = None
    material_name: Optional[str] = None
    material_context: Optional[str] = None
    regulatory_route: Optional[str] = None
    estimated_weight_g: Optional[int] = None
    condition: Optional[str] = None
    description: Optional[str] = None
    coarse_area: Optional[str] = None
    collector_alias: Optional[str] = None
    images: List[Dict[str, Any]] = Field(default_factory=list)


class IncomingRequestItem(BaseModel):
    request_id: uuid.UUID
    lot_id: uuid.UUID
    facility_id: uuid.UUID
    state: str
    reason: Optional[str] = None
    created_at: datetime
    lot: IncomingLotSummary
    offers: List[OfferResponse] = Field(default_factory=list)


class RecyclerMaterialUpdate(BaseModel):
    material_id: str
    route: Optional[str] = None
    accepted: bool = True
    min_weight_g: Optional[int] = Field(None, gt=0)
    max_weight_g: Optional[int] = Field(None, gt=0)


class RecyclerRateUpdate(BaseModel):
    material_id: str
    condition: Optional[str] = "INTACT"
    rate_paise_per_unit: int = Field(..., gt=0)
    unit: str = "kg"
    valid_until: Optional[datetime] = None


class RecyclerProfileUpdateRequest(BaseModel):
    facility_id: Optional[uuid.UUID] = None
    pickup_status: Optional[bool] = None
    clear_pickup_status: Optional[bool] = False
    service_regions: Optional[str] = None
    accepting_status: Optional[str] = None
    materials: Optional[List[RecyclerMaterialUpdate]] = None
    rates: Optional[List[RecyclerRateUpdate]] = None
    expected_version: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def reject_authorization_tampering(cls, data: Any) -> Any:
        if isinstance(data, dict):
            forbidden = {"authorizations", "authorization", "verification_level", "authority", "route_authorization"}
            tampered = forbidden.intersection(data.keys())
            if tampered:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Authorization fields {sorted(tampered)} are admin-controlled and cannot be modified by facility users."
                )
        return data


class RecyclerAuthorizationSummary(BaseModel):
    route: str
    authority: str
    reference: str
    status: str
    verification_level: str
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    scope_notes: Optional[str] = None


class RecyclerMaterialSummary(BaseModel):
    material_id: str
    route: str
    accepted: bool
    min_weight_g: Optional[int] = None
    max_weight_g: Optional[int] = None


class RecyclerRateSummary(BaseModel):
    material_id: str
    condition: Optional[str] = None
    rate_paise_per_unit: int
    unit: str
    price_kind: str
    valid_until: Optional[datetime] = None


class RecyclerOperationSummary(BaseModel):
    pickup_status: Optional[bool] = None
    service_regions: Optional[str] = None
    accepting_status: str
    operational_updated_at: datetime
    source_id: Optional[str] = None


class RecyclerProfileResponse(BaseModel):
    facility_id: uuid.UUID
    name: str
    facility_name: str
    kind: str
    address_public: str
    district: str
    state: str
    region_id: str
    contact_public: Optional[str] = None
    version: int
    operations: Optional[RecyclerOperationSummary] = None
    authorizations: List[RecyclerAuthorizationSummary] = Field(default_factory=list)
    materials: List[RecyclerMaterialSummary] = Field(default_factory=list)
    rates: List[RecyclerRateSummary] = Field(default_factory=list)


# --- Lot Request Endpoints ---

@router.post("/lots/{lot_id}/requests", response_model=LotRequestResponse, status_code=status.HTTP_201_CREATED)
@router.post("/api/v1/lots/{lot_id}/requests", response_model=LotRequestResponse, status_code=status.HTTP_201_CREATED)
def create_lot_request(
    lot_id: uuid.UUID,
    payload: CreateLotRequestInput,
    current_user: User = Depends(require_roles(UserRole.COLLECTOR, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Direct lot to a chosen eligible facility. Revalidates lot state, route compatibility, and material acceptance."""
    lot = db.query(Lot).filter(Lot.id == lot_id, Lot.deleted_at.is_(None)).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found.")

    # Ownership check
    if not is_lot_owner(current_user, lot):
        raise HTTPException(status_code=403, detail="Forbidden: you do not own this lot.")

    # Validate lot state
    if lot.status not in {"COLLECTED", "LISTED", "MATCHED"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lot in state '{lot.status}' cannot request new destinations."
        )

    # Validate target facility
    facility = db.query(Facility).filter(Facility.id == payload.facility_id, Facility.active == True).first()
    if not facility:
        raise HTTPException(status_code=404, detail="Target facility not found or inactive.")

    # Route and Battery Isolation check (R-REC-04 / AT-024)
    if lot.regulatory_route:
        matching_auth = (
            db.query(FacilityAuthorization)
            .filter(
                FacilityAuthorization.facility_id == facility.id,
                FacilityAuthorization.route == lot.regulatory_route,
                FacilityAuthorization.status == "VALID"
            )
            .first()
        )
        if not matching_auth:
            if lot.regulatory_route == "BATTERY_ISOLATION":
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Incompatible route: battery isolation lots cannot be directed to general e-waste facilities."
                )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Facility lacks valid authorization for route '{lot.regulatory_route}'."
            )

    # Check material acceptance if lot has material assigned
    if lot.material_id:
        mat_entry = (
            db.query(FacilityMaterial)
            .filter(
                FacilityMaterial.facility_id == facility.id,
                FacilityMaterial.material_id == lot.material_id
            )
            .first()
        )
        if mat_entry and not mat_entry.accepted:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Facility does not accept material '{lot.material_id}'."
            )

    now = datetime.now(timezone.utc)
    req = LotRequest(
        id=uuid.uuid4(),
        lot_id=lot.id,
        facility_id=facility.id,
        created_by=current_user.id,
        state="PENDING",
        reason=payload.notes,
        created_at=now
    )
    db.add(req)

    # Advance lot state if previously COLLECTED
    prev_state = lot.status
    if lot.status == "COLLECTED":
        lot.status = "MATCHED"
        lot.updated_at = now
        lot.version += 1
    elif lot.status == "LISTED":
        lot.status = "MATCHED"
        lot.updated_at = now
        lot.version += 1

    record_trade_event(
        db=db,
        aggregate_type="REQUEST",
        aggregate_id=req.id,
        event_type="REQUEST_CREATED",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state=None,
        next_state="PENDING",
        payload={
            "request_id": str(req.id),
            "lot_id": str(lot.id),
            "facility_id": str(facility.id),
            "lot_previous_state": prev_state,
            "lot_next_state": lot.status,
            "notes": payload.notes
        }
    )

    db.commit()
    db.refresh(req)

    return LotRequestResponse(
        id=req.id,
        lot_id=req.lot_id,
        facility_id=req.facility_id,
        created_by=req.created_by,
        state=req.state,
        reason=req.reason,
        created_at=req.created_at
    )


@router.get("/lots/{lot_id}/requests", response_model=List[LotRequestResponse])
@router.get("/api/v1/lots/{lot_id}/requests", response_model=List[LotRequestResponse])
def get_lot_requests(
    lot_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all directed requests for a given lot."""
    lot = db.query(Lot).filter(Lot.id == lot_id, Lot.deleted_at.is_(None)).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found.")

    if not is_lot_owner(current_user, lot):
        raise HTTPException(status_code=403, detail="Forbidden: you do not own this lot.")

    requests = (
        db.query(LotRequest)
        .filter(LotRequest.lot_id == lot_id)
        .order_by(desc(LotRequest.created_at))
        .all()
    )
    return [
        LotRequestResponse(
            id=r.id,
            lot_id=r.lot_id,
            facility_id=r.facility_id,
            created_by=r.created_by,
            state=r.state,
            reason=r.reason,
            created_at=r.created_at
        )
        for r in requests
    ]


# --- Recycler Incoming Queue & Operational Profile ---

@router.get("/recycler/incoming", response_model=List[IncomingRequestItem])
@router.get("/api/v1/recycler/incoming", response_model=List[IncomingRequestItem])
def get_recycler_incoming(
    facility_id: Optional[uuid.UUID] = Query(None, description="Facility identifier"),
    request_state: Optional[str] = Query("PENDING", description="Filter by state: PENDING, ALL, ACCEPTED, REJECTED, EXPIRED"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_roles(UserRole.RECYCLER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """View permitted incoming requests and lot evidence for authorized facility users."""
    facility = get_user_facility(current_user, db, facility_id)

    query = db.query(LotRequest).filter(LotRequest.facility_id == facility.id)
    if request_state and request_state.upper() != "ALL":
        query = query.filter(LotRequest.state == request_state.upper())

    requests = query.order_by(desc(LotRequest.created_at)).offset(offset).limit(limit).all()

    now = datetime.now(timezone.utc)
    results: List[IncomingRequestItem] = []
    for req in requests:
        lot = db.query(Lot).filter(Lot.id == req.lot_id, Lot.deleted_at.is_(None)).first()
        if not lot:
            continue

        # Location coarse area only - privacy protection
        coarse_area = None
        if lot.collection_location_id:
            loc = db.query(LocationRecord).filter(LocationRecord.id == lot.collection_location_id).first()
            if loc:
                coarse_area = loc.coarse_area

        # Collector display alias
        collector_alias = None
        if lot.collector:
            collector_alias = lot.collector.display_alias

        # Images summary
        images_summary = []
        for img in lot.images:
            if img.media_object:
                images_summary.append({
                    "media_id": str(img.media_id),
                    "storage_key": img.media_object.storage_key,
                    "mime_type": img.media_object.mime_type,
                    "byte_size": img.media_object.byte_size,
                    "sha256": img.media_object.sha256,
                    "purpose": img.purpose
                })

        # Offers for this request
        offers_db = db.query(Offer).filter(Offer.request_id == req.id).order_by(desc(Offer.created_at)).all()
        offers_list: List[OfferResponse] = []
        for off in offers_db:
            is_expired = ensure_utc(off.expires_at) < now or off.status == "EXPIRED"
            eff_rate = None
            if off.price_basis == "RATE_PER_KG" and off.rate_paise_per_kg:
                eff_rate = off.rate_paise_per_kg
            elif off.price_basis == "FIXED_TOTAL" and off.fixed_total_paise and (off.weight_basis_g or lot.estimated_weight_g):
                w = off.weight_basis_g or lot.estimated_weight_g
                eff_rate = int(round((off.fixed_total_paise * 1000.0) / w))

            offers_list.append(OfferResponse(
                id=off.id,
                request_id=off.request_id,
                lot_id=off.lot_id,
                facility_id=off.facility_id,
                price_basis=off.price_basis,
                rate_paise_per_kg=off.rate_paise_per_kg,
                fixed_total_paise=off.fixed_total_paise,
                condition=off.condition,
                weight_basis_g=off.weight_basis_g,
                expires_at=off.expires_at,
                status="EXPIRED" if is_expired and off.status == "OPEN" else off.status,
                is_expired=is_expired,
                effective_rate_paise_per_kg=eff_rate,
                terms_hash=off.terms_hash,
                version=off.version,
                created_at=off.created_at,
                updated_at=off.updated_at
            ))

        results.append(IncomingRequestItem(
            request_id=req.id,
            lot_id=req.lot_id,
            facility_id=req.facility_id,
            state=req.state,
            reason=req.reason,
            created_at=req.created_at,
            lot=IncomingLotSummary(
                lot_id=lot.id,
                material_id=lot.material_id,
                material_name=lot.material_id,
                material_context=lot.material_context,
                regulatory_route=lot.regulatory_route,
                estimated_weight_g=lot.estimated_weight_g,
                condition=lot.condition,
                description=lot.description,
                coarse_area=coarse_area,
                collector_alias=collector_alias,
                images=images_summary
            ),
            offers=offers_list
        ))

    return results


@router.get("/recycler/profile", response_model=RecyclerProfileResponse)
@router.get("/api/v1/recycler/profile", response_model=RecyclerProfileResponse)
def get_recycler_profile(
    facility_id: Optional[uuid.UUID] = Query(None, description="Facility identifier"),
    current_user: User = Depends(require_roles(UserRole.RECYCLER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Retrieve facility self-declared operational profile and admin-controlled authorizations."""
    facility = get_user_facility(current_user, db, facility_id)

    auths_summary = [
        RecyclerAuthorizationSummary(
            route=a.route,
            authority=a.authority,
            reference=a.reference,
            status=a.status,
            verification_level=a.verification_level,
            valid_from=a.valid_from,
            valid_until=a.valid_until,
            scope_notes=a.scope_notes
        )
        for a in facility.authorizations
    ]

    materials_summary = [
        RecyclerMaterialSummary(
            material_id=m.material_id,
            route=m.route,
            accepted=m.accepted,
            min_weight_g=m.min_weight_g,
            max_weight_g=m.max_weight_g
        )
        for m in facility.materials
    ]

    rates_summary = [
        RecyclerRateSummary(
            material_id=r.material_id,
            condition=r.condition,
            rate_paise_per_unit=r.rate_paise_per_unit,
            unit=r.unit,
            price_kind=r.price_kind,
            valid_until=r.valid_until
        )
        for r in facility.rates
    ]

    ops_summary = None
    if facility.operations:
        ops_summary = RecyclerOperationSummary(
            pickup_status=facility.operations.pickup_status,
            service_regions=facility.operations.service_regions,
            accepting_status=facility.operations.accepting_status,
            operational_updated_at=facility.operations.operational_updated_at,
            source_id=facility.operations.source_id
        )

    return RecyclerProfileResponse(
        facility_id=facility.id,
        name=facility.name,
        facility_name=facility.facility_name,
        kind=facility.kind,
        address_public=facility.address_public,
        district=facility.district,
        state=facility.state,
        region_id=facility.region_id,
        contact_public=facility.contact_public,
        version=facility.version,
        operations=ops_summary,
        authorizations=auths_summary,
        materials=materials_summary,
        rates=rates_summary
    )


@router.patch("/recycler/profile", response_model=RecyclerProfileResponse)
@router.patch("/api/v1/recycler/profile", response_model=RecyclerProfileResponse)
def update_recycler_profile(
    payload: RecyclerProfileUpdateRequest,
    current_user: User = Depends(require_roles(UserRole.RECYCLER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Update self-declared operational profile, accepted materials, and rates with provenance (AT-023)."""
    facility = get_user_facility(current_user, db, payload.facility_id)

    if payload.expected_version is not None and facility.version != payload.expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Version conflict: facility is at version {facility.version}, expected {payload.expected_version}."
        )

    now = datetime.now(timezone.utc)

    # Operations update
    ops = facility.operations
    if not ops:
        ops = FacilityOperation(
            facility_id=facility.id,
            accepting_status="ACCEPTING",
            operational_updated_at=now,
            source_id=f"SELF_DECLARED_USER_{current_user.id}"
        )
        db.add(ops)

    if payload.clear_pickup_status:
        ops.pickup_status = None
    elif payload.pickup_status is not None:
        ops.pickup_status = payload.pickup_status

    if payload.service_regions is not None:
        ops.service_regions = payload.service_regions

    if payload.accepting_status is not None:
        if payload.accepting_status not in {"ACCEPTING", "PAUSED", "CLOSED"}:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="accepting_status must be ACCEPTING, PAUSED, or CLOSED."
            )
        ops.accepting_status = payload.accepting_status

    ops.operational_updated_at = now
    ops.source_id = f"SELF_DECLARED_USER_{current_user.id}"

    # Materials update
    if payload.materials is not None:
        for mat_in in payload.materials:
            fm = (
                db.query(FacilityMaterial)
                .filter(
                    FacilityMaterial.facility_id == facility.id,
                    FacilityMaterial.material_id == mat_in.material_id
                )
                .first()
            )
            if fm:
                fm.accepted = mat_in.accepted
                if mat_in.route:
                    fm.route = mat_in.route
                fm.min_weight_g = mat_in.min_weight_g
                fm.max_weight_g = mat_in.max_weight_g
                fm.updated_at = now
            else:
                new_fm = FacilityMaterial(
                    id=uuid.uuid4(),
                    facility_id=facility.id,
                    material_id=mat_in.material_id,
                    route=mat_in.route or "GENERAL_RECYCLING",
                    accepted=mat_in.accepted,
                    min_weight_g=mat_in.min_weight_g,
                    max_weight_g=mat_in.max_weight_g,
                    evidence_source_id=f"SELF_DECLARED_USER_{current_user.id}",
                    updated_at=now
                )
                db.add(new_fm)

    # Rates update
    if payload.rates is not None:
        for rate_in in payload.rates:
            fr = (
                db.query(FacilityRate)
                .filter(
                    FacilityRate.facility_id == facility.id,
                    FacilityRate.material_id == rate_in.material_id,
                    FacilityRate.condition == rate_in.condition
                )
                .first()
            )
            if fr:
                fr.rate_paise_per_unit = rate_in.rate_paise_per_unit
                fr.unit = rate_in.unit
                fr.valid_until = rate_in.valid_until
                fr.observed_at = now
                fr.source_id = f"FACILITY_QUOTE_{facility.id}"
            else:
                new_fr = FacilityRate(
                    id=uuid.uuid4(),
                    facility_id=facility.id,
                    material_id=rate_in.material_id,
                    condition=rate_in.condition,
                    region_id=facility.region_id,
                    rate_paise_per_unit=rate_in.rate_paise_per_unit,
                    unit=rate_in.unit,
                    price_kind="QUOTE",
                    observed_at=now,
                    valid_until=rate_in.valid_until,
                    source_id=f"FACILITY_QUOTE_{facility.id}",
                    review_status="VERIFIED",
                    is_demo=False
                )
                db.add(new_fr)

    facility.version += 1
    facility.updated_at = now

    db.commit()
    db.refresh(facility)

    return get_recycler_profile(facility_id=facility.id, current_user=current_user, db=db)


# --- Offer Workflows (Quote, Reject, Withdraw, Accept) ---

@router.post("/requests/{request_id}/offers", response_model=OfferResponse, status_code=status.HTTP_201_CREATED)
@router.post("/api/v1/requests/{request_id}/offers", response_model=OfferResponse, status_code=status.HTTP_201_CREATED)
def create_offer(
    request_id: uuid.UUID,
    payload: CreateOfferInput,
    current_user: User = Depends(require_roles(UserRole.RECYCLER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Quote an offer on an incoming lot request."""
    req = db.query(LotRequest).filter(LotRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Lot request not found.")

    facility = get_user_facility(current_user, db, req.facility_id)

    if req.state != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot quote on request in state '{req.state}'."
        )

    lot = db.query(Lot).filter(Lot.id == req.lot_id, Lot.deleted_at.is_(None)).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot associated with request not found.")

    now = datetime.now(timezone.utc)
    expires_at = payload.expires_at or (now + timedelta(hours=72))
    if ensure_utc(expires_at) <= now:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="expires_at must be in the future."
        )

    offer_id = uuid.uuid4()
    terms_hash = compute_offer_terms_hash(
        offer_id=offer_id,
        request_id=req.id,
        lot_id=lot.id,
        facility_id=facility.id,
        price_basis=payload.price_basis,
        rate_paise_per_kg=payload.rate_paise_per_kg,
        fixed_total_paise=payload.fixed_total_paise,
        condition=payload.condition,
        weight_basis_g=payload.weight_basis_g or lot.estimated_weight_g,
        expires_at=expires_at
    )

    offer = Offer(
        id=offer_id,
        request_id=req.id,
        lot_id=lot.id,
        facility_id=facility.id,
        rate_paise_per_kg=payload.rate_paise_per_kg,
        fixed_total_paise=payload.fixed_total_paise,
        price_basis=payload.price_basis,
        condition=payload.condition,
        weight_basis_g=payload.weight_basis_g or lot.estimated_weight_g,
        expires_at=expires_at,
        status="OPEN",
        terms_hash=terms_hash,
        version=1,
        created_at=now,
        updated_at=now
    )
    db.add(offer)

    # Ensure lot is marked MATCHED
    if lot.status in {"COLLECTED", "LISTED"}:
        lot.status = "MATCHED"
        lot.updated_at = now
        lot.version += 1

    record_trade_event(
        db=db,
        aggregate_type="OFFER",
        aggregate_id=offer.id,
        event_type="OFFER_CREATED",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state=None,
        next_state="OPEN",
        payload={
            "offer_id": str(offer.id),
            "request_id": str(req.id),
            "lot_id": str(lot.id),
            "facility_id": str(facility.id),
            "price_basis": payload.price_basis,
            "rate_paise_per_kg": payload.rate_paise_per_kg,
            "fixed_total_paise": payload.fixed_total_paise,
            "terms_hash": terms_hash,
            "expires_at": expires_at.isoformat()
        }
    )

    eff_rate = None
    if offer.price_basis == "RATE_PER_KG" and offer.rate_paise_per_kg:
        eff_rate = offer.rate_paise_per_kg
    elif offer.price_basis == "FIXED_TOTAL" and offer.fixed_total_paise and (offer.weight_basis_g or lot.estimated_weight_g):
        w = offer.weight_basis_g or lot.estimated_weight_g
        eff_rate = int(round((offer.fixed_total_paise * 1000.0) / w))

    # Evaluate DQ-PRICE-OUTLIER under QUALITY_V1 without blocking collector choice (AT-020)
    if eff_rate and lot.material_id:
        # Use the same eligible reference cohort as PRICE_V1: reviewed, recent,
        # per-kg BUY observations for this material/condition/region and demo
        # partition.  Pending, stale, piece-based, and recycler quote records
        # must never distort a quality review baseline.
        price_cutoff = now - timedelta(days=30)
        comparable_obs = (
            db.query(PriceObservation)
            .filter(
                PriceObservation.material_id == lot.material_id,
                PriceObservation.region_id == facility.region_id,
                PriceObservation.condition == offer.condition,
                func.lower(PriceObservation.unit) == "kg",
                PriceObservation.price_kind == "BUY",
                PriceObservation.review_status == "VERIFIED",
                PriceObservation.is_demo == lot.is_demo,
                PriceObservation.observed_at >= price_cutoff,
            )
            .all()
        )
        if comparable_obs:
            rule_result = evaluate_price_quote(eff_rate, [obs.rate_paise_per_unit for obs in comparable_obs])
            if not rule_result.passed:
                db.add(QualityFlag(
                    id=uuid.uuid4(),
                    entity_type="OFFER",
                    entity_id=offer.id,
                    entity_version=offer.version,
                    rule_id=rule_result.rule_id,
                    policy_version=POLICY_VERSION,
                    severity=rule_result.severity.value,
                    evidence_json=rule_result.details,
                    reason=rule_result.reason,
                    status="OPEN",
                    created_at=now,
                    updated_at=now
                ))

    db.commit()
    db.refresh(offer)

    return OfferResponse(
        id=offer.id,
        request_id=offer.request_id,
        lot_id=offer.lot_id,
        facility_id=offer.facility_id,
        price_basis=offer.price_basis,
        rate_paise_per_kg=offer.rate_paise_per_kg,
        fixed_total_paise=offer.fixed_total_paise,
        condition=offer.condition,
        weight_basis_g=offer.weight_basis_g,
        expires_at=offer.expires_at,
        status=offer.status,
        is_expired=False,
        effective_rate_paise_per_kg=eff_rate,
        terms_hash=offer.terms_hash,
        version=offer.version,
        created_at=offer.created_at,
        updated_at=offer.updated_at
    )


@router.post("/requests/{request_id}/reject")
@router.post("/api/v1/requests/{request_id}/reject")
def reject_lot_request(
    request_id: uuid.UUID,
    payload: RejectRequestInput,
    current_user: User = Depends(require_roles(UserRole.RECYCLER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Reject an incoming lot request with reason. Collector can rematch with another facility (AT-027)."""
    req = db.query(LotRequest).filter(LotRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Lot request not found.")

    facility = get_user_facility(current_user, db, req.facility_id)

    if req.state != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot reject request in state '{req.state}'."
        )

    req.state = "REJECTED"
    req.reason = payload.reason

    lot = db.query(Lot).filter(Lot.id == req.lot_id, Lot.deleted_at.is_(None)).first()
    now = datetime.now(timezone.utc)

    # Check if other pending requests or open offers exist for this lot
    other_pending = (
        db.query(LotRequest)
        .filter(
            LotRequest.lot_id == req.lot_id,
            LotRequest.id != req.id,
            LotRequest.state == "PENDING"
        )
        .count()
    )
    open_offers = (
        db.query(Offer)
        .filter(
            Offer.lot_id == req.lot_id,
            Offer.status == "OPEN"
        )
        .count()
    )

    if lot and other_pending == 0 and open_offers == 0 and lot.status == "MATCHED":
        lot.status = "LISTED"
        lot.updated_at = now
        lot.version += 1

    record_trade_event(
        db=db,
        aggregate_type="REQUEST",
        aggregate_id=req.id,
        event_type="REQUEST_REJECTED",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state="PENDING",
        next_state="REJECTED",
        payload={
            "request_id": str(req.id),
            "lot_id": str(req.lot_id),
            "reason": payload.reason,
            "lot_status": lot.status if lot else None
        }
    )

    db.commit()
    return {
        "status": "ok",
        "request_id": str(req.id),
        "state": "REJECTED",
        "lot_status": lot.status if lot else None
    }


@router.post("/offers/{offer_id}/withdraw", response_model=OfferResponse)
@router.post("/api/v1/offers/{offer_id}/withdraw", response_model=OfferResponse)
def withdraw_offer(
    offer_id: uuid.UUID,
    payload: WithdrawOfferInput,
    current_user: User = Depends(require_roles(UserRole.RECYCLER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Withdraw an open offer before collector acceptance."""
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found.")

    facility = get_user_facility(current_user, db, offer.facility_id)

    if offer.status == "ACCEPTED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot withdraw an already accepted offer."
        )

    if offer.status != "OPEN":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot withdraw offer in state '{offer.status}'."
        )

    if offer.version != payload.expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Version conflict: offer is at version {offer.version}, expected {payload.expected_version}."
        )

    now = datetime.now(timezone.utc)
    prev_state = offer.status
    offer.status = "WITHDRAWN"
    offer.version += 1
    offer.updated_at = now

    # Check if other open offers exist for this lot
    open_offers = (
        db.query(Offer)
        .filter(
            Offer.lot_id == offer.lot_id,
            Offer.id != offer.id,
            Offer.status == "OPEN"
        )
        .count()
    )
    lot = db.query(Lot).filter(Lot.id == offer.lot_id, Lot.deleted_at.is_(None)).first()
    if lot and open_offers == 0 and lot.status == "MATCHED":
        other_requests = (
            db.query(LotRequest)
            .filter(
                LotRequest.lot_id == lot.id,
                LotRequest.state == "PENDING"
            )
            .count()
        )
        if other_requests == 0:
            lot.status = "LISTED"
            lot.updated_at = now
            lot.version += 1

    record_trade_event(
        db=db,
        aggregate_type="OFFER",
        aggregate_id=offer.id,
        event_type="OFFER_WITHDRAWN",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state=prev_state,
        next_state="WITHDRAWN",
        payload={
            "offer_id": str(offer.id),
            "lot_id": str(offer.lot_id),
            "reason": payload.reason
        }
    )

    db.commit()
    db.refresh(offer)

    return OfferResponse(
        id=offer.id,
        request_id=offer.request_id,
        lot_id=offer.lot_id,
        facility_id=offer.facility_id,
        price_basis=offer.price_basis,
        rate_paise_per_kg=offer.rate_paise_per_kg,
        fixed_total_paise=offer.fixed_total_paise,
        condition=offer.condition,
        weight_basis_g=offer.weight_basis_g,
        expires_at=offer.expires_at,
        status=offer.status,
        is_expired=False,
        terms_hash=offer.terms_hash,
        version=offer.version,
        created_at=offer.created_at,
        updated_at=offer.updated_at
    )


@router.post("/offers/{offer_id}/accept", response_model=TransactionDetailResponse)
@router.post("/api/v1/offers/{offer_id}/accept", response_model=TransactionDetailResponse)
def accept_offer(
    offer_id: uuid.UUID,
    payload: AcceptOfferInput,
    current_user: User = Depends(require_roles(UserRole.COLLECTOR, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Collector accepts one live offer creating an immutable agreement (AT-028).
    Two simultaneous acceptances leave only one active agreement.
    Expired offers cannot bind.
    Later price-board refreshes do not modify accepted terms.
    """
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found.")

    lot = db.query(Lot).filter(Lot.id == offer.lot_id, Lot.deleted_at.is_(None)).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found.")

    # Ownership check
    if not is_lot_owner(current_user, lot):
        raise HTTPException(status_code=403, detail="Forbidden: you do not own this lot.")

    # Version check
    if offer.version != payload.expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Version conflict: offer is at version {offer.version}, expected {payload.expected_version}."
        )

    # Expiration check (AT-028: cached expired offer cannot silently bind)
    now = datetime.now(timezone.utc)
    if ensure_utc(offer.expires_at) <= now or offer.status == "EXPIRED":
        offer.status = "EXPIRED"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Offer has expired and cannot bind. Please request fresh terms."
        )

    # Terms hash verification (AT-028: mutual agreement to exact terms)
    if offer.terms_hash != payload.terms_hash:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Terms hash mismatch. The offered terms do not match the accepted payload."
        )

    # Offer status check
    if offer.status != "OPEN":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Offer cannot be accepted because it is currently '{offer.status}'."
        )

    # AT-028: Mutual exclusion - only one active accepted transaction per lot
    existing_tx = db.query(Transaction).filter(Transaction.lot_id == lot.id).first()
    if existing_tx:
        # Record repeated sale anomaly under QUALITY_V1 (AT-028)
        db.add(QualityFlag(
            id=uuid.uuid4(),
            entity_type="TRANSACTION",
            entity_id=existing_tx.id,
            entity_version=existing_tx.version,
            rule_id="DQ-REPEATED-SALE",
            policy_version=POLICY_VERSION,
            severity="HIGH",
            evidence_json={"lot_id": str(lot.id), "attempted_offer_id": str(offer.id), "existing_tx_id": str(existing_tx.id)},
            reason=f"Conflicting active transaction detected for lot {lot.id}; repeated sale prohibited by single active agreement invariant.",
            status="OPEN",
            created_at=now,
            updated_at=now
        ))
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Lot already has an active accepted agreement. Only one active agreement can exist."
        )

    if lot.status == "ACCEPTED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Lot is already accepted in another agreement."
        )

    # Atomically bind the agreement
    offer.status = "ACCEPTED"
    offer.version += 1
    offer.updated_at = now

    # Update associated request
    lot_req = db.query(LotRequest).filter(LotRequest.id == offer.request_id).first()
    if lot_req:
        lot_req.state = "ACCEPTED"

    # Expire all competing open offers for this lot
    db.query(Offer).filter(
        Offer.lot_id == lot.id,
        Offer.id != offer.id,
        Offer.status == "OPEN"
    ).update({"status": "EXPIRED", "updated_at": now})

    # Expire competing pending requests for this lot
    db.query(LotRequest).filter(
        LotRequest.lot_id == lot.id,
        LotRequest.id != offer.request_id,
        LotRequest.state == "PENDING"
    ).update({"state": "EXPIRED"})

    # Advance lot lifecycle to ACCEPTED
    lot_prev_status = lot.status
    lot.status = "ACCEPTED"
    lot.version += 1
    lot.updated_at = now

    # Compute immutable agreed amounts
    weight_g = lot.estimated_weight_g or 1000
    if offer.price_basis == "RATE_PER_KG":
        rate = offer.rate_paise_per_kg or 0
        quoted_total = int(round((rate * weight_g) / 1000.0))
    else:
        quoted_total = offer.fixed_total_paise or 0

    tx_id = uuid.uuid4()
    tx = Transaction(
        id=tx_id,
        lot_id=lot.id,
        collector_id=lot.collector_id,
        facility_id=offer.facility_id,
        accepted_offer_id=offer.id,
        estimated_weight_g=weight_g,
        agreed_weight_g=weight_g,
        quoted_total_paise=quoted_total,
        agreed_total_paise=quoted_total,
        currency="INR",
        lifecycle="AGREED",
        version=1,
        is_demo=lot.is_demo,
        created_at=now,
        updated_at=now
    )
    db.add(tx)

    # Create initial TermsRevision snapshot
    rev_id = uuid.uuid4()
    revision = TermsRevision(
        id=rev_id,
        transaction_id=tx.id,
        previous_revision_id=None,
        final_material_id=lot.material_id or "UNKNOWN",
        measured_weight_g=weight_g,
        final_total_paise=quoted_total,
        currency="INR",
        proposed_by="FACILITY",
        proposed_at=now,
        collector_ack_at=now,
        recycler_ack_at=offer.created_at,
        terms_hash=offer.terms_hash,
        reason="Initial offer acceptance"
    )
    db.add(revision)

    # Record Domain Events
    record_trade_event(
        db=db,
        aggregate_type="OFFER",
        aggregate_id=offer.id,
        event_type="OFFER_ACCEPTED",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state="OPEN",
        next_state="ACCEPTED",
        payload={
            "offer_id": str(offer.id),
            "lot_id": str(lot.id),
            "transaction_id": str(tx.id),
            "terms_hash": offer.terms_hash
        }
    )

    record_trade_event(
        db=db,
        aggregate_type="LOT",
        aggregate_id=lot.id,
        event_type="LOT_ACCEPTED",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state=lot_prev_status,
        next_state="ACCEPTED",
        payload={
            "lot_id": str(lot.id),
            "transaction_id": str(tx.id),
            "offer_id": str(offer.id)
        }
    )

    record_trade_event(
        db=db,
        aggregate_type="TRANSACTION",
        aggregate_id=tx.id,
        event_type="TRANSACTION_CREATED",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state=None,
        next_state="AGREED",
        payload={
            "transaction_id": str(tx.id),
            "lot_id": str(lot.id),
            "collector_id": str(lot.collector_id),
            "facility_id": str(offer.facility_id),
            "quoted_total_paise": quoted_total,
            "agreed_total_paise": quoted_total,
            "terms_hash": offer.terms_hash
        }
    )

    db.commit()
    db.refresh(tx)

    return TransactionDetailResponse(
        id=tx.id,
        lot_id=tx.lot_id,
        collector_id=tx.collector_id,
        facility_id=tx.facility_id,
        accepted_offer_id=tx.accepted_offer_id,
        estimated_weight_g=tx.estimated_weight_g,
        agreed_weight_g=tx.agreed_weight_g,
        quoted_total_paise=tx.quoted_total_paise,
        agreed_total_paise=tx.agreed_total_paise,
        currency=tx.currency,
        lifecycle=tx.lifecycle,
        version=tx.version,
        is_demo=tx.is_demo,
        created_at=tx.created_at,
        updated_at=tx.updated_at,
        revisions=[
            TermsRevisionSummary(
                id=revision.id,
                final_material_id=revision.final_material_id,
                measured_weight_g=revision.measured_weight_g,
                final_total_paise=revision.final_total_paise,
                currency=revision.currency,
                proposed_by=revision.proposed_by,
                collector_ack_at=revision.collector_ack_at,
                recycler_ack_at=revision.recycler_ack_at,
                terms_hash=revision.terms_hash,
                reason=revision.reason
            )
        ]
    )


# --- Lot Offers Listing & Transactions ---

@router.get("/lots/{lot_id}/offers", response_model=List[OfferResponse])
@router.get("/api/v1/lots/{lot_id}/offers", response_model=List[OfferResponse])
def get_lot_offers(
    lot_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """View offers on a lot with dynamic expiry check and comparable unit rates (AT-019)."""
    lot = db.query(Lot).filter(Lot.id == lot_id, Lot.deleted_at.is_(None)).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found.")

    # Scoped authorization
    if current_user.role == UserRole.COLLECTOR.value:
        if not is_lot_owner(current_user, lot):
            raise HTTPException(status_code=403, detail="Forbidden: you do not own this lot.")

    offers = db.query(Offer).filter(Offer.lot_id == lot_id).order_by(desc(Offer.created_at)).all()
    now = datetime.now(timezone.utc)
    results: List[OfferResponse] = []

    for off in offers:
        is_expired = ensure_utc(off.expires_at) < now or off.status == "EXPIRED"
        eff_rate = None
        if off.price_basis == "RATE_PER_KG" and off.rate_paise_per_kg:
            eff_rate = off.rate_paise_per_kg
        elif off.price_basis == "FIXED_TOTAL" and off.fixed_total_paise and (off.weight_basis_g or lot.estimated_weight_g):
            w = off.weight_basis_g or lot.estimated_weight_g
            eff_rate = int(round((off.fixed_total_paise * 1000.0) / w))

        results.append(OfferResponse(
            id=off.id,
            request_id=off.request_id,
            lot_id=off.lot_id,
            facility_id=off.facility_id,
            price_basis=off.price_basis,
            rate_paise_per_kg=off.rate_paise_per_kg,
            fixed_total_paise=off.fixed_total_paise,
            condition=off.condition,
            weight_basis_g=off.weight_basis_g,
            expires_at=off.expires_at,
            status="EXPIRED" if is_expired and off.status == "OPEN" else off.status,
            is_expired=is_expired,
            effective_rate_paise_per_kg=eff_rate,
            terms_hash=off.terms_hash,
            version=off.version,
            created_at=off.created_at,
            updated_at=off.updated_at
        ))

    return results


@router.get("/transactions/{transaction_id}", response_model=TransactionDetailResponse)
@router.get("/api/v1/transactions/{transaction_id}", response_model=TransactionDetailResponse)
def get_transaction(
    transaction_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve transaction details, agreed terms, and revisions for authorized participants."""
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    # Access scoping
    if current_user.role != UserRole.ADMIN.value:
        is_collector = (
            current_user.role == UserRole.COLLECTOR.value
            and is_transaction_collector(current_user, tx)
        )
        is_facility_member = False
        if current_user.role == UserRole.RECYCLER.value:
            fu = (
                db.query(FacilityUser)
                .filter(
                    FacilityUser.user_id == current_user.id,
                    FacilityUser.facility_id == tx.facility_id,
                    FacilityUser.active == True
                )
                .first()
            )
            if fu:
                is_facility_member = True

        if not (is_collector or is_facility_member):
            raise HTTPException(status_code=403, detail="Forbidden: you are not a participant in this transaction.")

    revisions_summary = [
        TermsRevisionSummary(
            id=r.id,
            final_material_id=r.final_material_id,
            measured_weight_g=r.measured_weight_g,
            final_total_paise=r.final_total_paise,
            currency=r.currency,
            proposed_by=r.proposed_by,
            collector_ack_at=r.collector_ack_at,
            recycler_ack_at=r.recycler_ack_at,
            terms_hash=r.terms_hash,
            reason=r.reason
        )
        for r in tx.terms_revisions
    ]

    return TransactionDetailResponse(
        id=tx.id,
        lot_id=tx.lot_id,
        collector_id=tx.collector_id,
        facility_id=tx.facility_id,
        accepted_offer_id=tx.accepted_offer_id,
        estimated_weight_g=tx.estimated_weight_g,
        agreed_weight_g=tx.agreed_weight_g,
        quoted_total_paise=tx.quoted_total_paise,
        agreed_total_paise=tx.agreed_total_paise,
        currency=tx.currency,
        lifecycle=tx.lifecycle,
        version=tx.version,
        is_demo=tx.is_demo,
        created_at=tx.created_at,
        updated_at=tx.updated_at,
        revisions=revisions_summary
    )


@router.get("/recycler/transactions", response_model=List[TransactionDetailResponse])
@router.get("/api/v1/recycler/transactions", response_model=List[TransactionDetailResponse])
def get_recycler_transactions(
    facility_id: Optional[uuid.UUID] = Query(None, description="Facility identifier"),
    lifecycle: Optional[str] = Query(None, description="Filter by lifecycle status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_roles(UserRole.RECYCLER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """View facility transactions, agreed terms, and receipts."""
    facility = get_user_facility(current_user, db, facility_id)

    query = db.query(Transaction).filter(Transaction.facility_id == facility.id)
    if lifecycle:
        query = query.filter(Transaction.lifecycle == lifecycle.upper())

    txs = query.order_by(desc(Transaction.created_at)).offset(offset).limit(limit).all()

    results: List[TransactionDetailResponse] = []
    for tx in txs:
        revisions_summary = [
            TermsRevisionSummary(
                id=r.id,
                final_material_id=r.final_material_id,
                measured_weight_g=r.measured_weight_g,
                final_total_paise=r.final_total_paise,
                currency=r.currency,
                proposed_by=r.proposed_by,
                collector_ack_at=r.collector_ack_at,
                recycler_ack_at=r.recycler_ack_at,
                terms_hash=r.terms_hash,
                reason=r.reason
            )
            for r in tx.terms_revisions
        ]
        results.append(TransactionDetailResponse(
            id=tx.id,
            lot_id=tx.lot_id,
            collector_id=tx.collector_id,
            facility_id=tx.facility_id,
            accepted_offer_id=tx.accepted_offer_id,
            estimated_weight_g=tx.estimated_weight_g,
            agreed_weight_g=tx.agreed_weight_g,
            quoted_total_paise=tx.quoted_total_paise,
            agreed_total_paise=tx.agreed_total_paise,
            currency=tx.currency,
            lifecycle=tx.lifecycle,
            version=tx.version,
            is_demo=tx.is_demo,
            created_at=tx.created_at,
            updated_at=tx.updated_at,
            revisions=revisions_summary
        ))

    return results
