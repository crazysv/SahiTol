"""Payment Assertions, Offline Settlements, Dues Ledger, and Earnings router.
Implements T026: cash-first payment assertions without bank gateway, optional UPI reference recording,
counterparty acknowledgement, disputes, partial payments, duplicate-safe idempotency,
append-only reversals linking original records, transaction closure verification,
and collector earnings reconciliation with strict demo isolation.

Specifications: docs/16_API_CONTRACT.md, docs/04_APPFLOW.md, docs/06_SCHEMA.md.
Requirements: R-PAY-01, R-PAY-02, R-PAY-03, R-DATA-04.
Acceptance cases: AT-035, AT-036, AT-037, AT-056.
"""
import hashlib
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.audit import DomainEvent
from app.db.models.auth import User
from app.db.models.collector import Collector
from app.db.models.facility import Facility, FacilityUser
from app.db.models.lot import Lot
from app.db.models.price import PriceObservation
from app.db.models.trade import (
    Handover,
    PaymentEntry,
    TermsRevision,
    Transaction,
)
from app.domain.canonical import compute_canonical_hash
from app.security import UserRole, get_current_user, require_roles

router = APIRouter(tags=["payments"])

VALID_PAYMENT_METHODS = {"CASH", "UPI", "OTHER"}
VALID_ASSERTED_ROLES = {"COLLECTOR", "FACILITY", "ADMIN"}


def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Normalize datetime to UTC for safe comparisons."""
    if dt is None:
        return None
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt


def record_payment_event(
    db: Session,
    aggregate_id: uuid.UUID,
    event_type: str,
    actor_id: uuid.UUID,
    role: str,
    previous_state: Optional[str],
    next_state: Optional[str],
    payload: Dict[str, Any]
) -> DomainEvent:
    """Record an append-only domain event on aggregate TRANSACTION with SHA-256 hash chaining."""
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
        aggregate_type="TRANSACTION",
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
    db.flush()
    return event


# --- Helper Functions for Scoping and Balances ---

def get_transaction_or_404(db: Session, tx_id: uuid.UUID) -> Transaction:
    """Retrieve transaction by ID or raise 404."""
    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found.")
    return tx


def is_tx_collector(user: User, tx: Transaction, db: Session) -> bool:
    """Check if authenticated user is the collector of this transaction."""
    if user.role == UserRole.ADMIN.value:
        return True
    collector = db.query(Collector).filter(Collector.id == tx.collector_id).first()
    return bool(collector and collector.user_id == user.id)


def is_tx_facility_member(user: User, tx: Transaction, db: Session) -> bool:
    """Check if authenticated user is an active member of the linked facility."""
    if user.role == UserRole.ADMIN.value:
        return True
    fu = db.query(FacilityUser).filter(
        FacilityUser.facility_id == tx.facility_id,
        FacilityUser.user_id == user.id,
        FacilityUser.active == True
    ).first()
    return fu is not None


def derive_asserted_by(user: User, tx: Transaction, db: Session) -> str:
    """Derive actor role (COLLECTOR or FACILITY) for payment assertion."""
    if user.role == UserRole.ADMIN.value:
        return "ADMIN"
    if user.role == UserRole.COLLECTOR.value or is_tx_collector(user, tx, db):
        return "COLLECTOR"
    if user.role == UserRole.RECYCLER.value or is_tx_facility_member(user, tx, db):
        return "FACILITY"
    return "UNKNOWN"


def compute_transaction_balances(tx: Transaction, db: Session) -> Dict[str, Any]:
    """Compute derived ledger balances and summary for a transaction (R-PAY-02, AT-036)."""
    # 1. Gross agreed amount from latest TermsRevision or transaction agreed/quoted paise
    latest_rev = (
        db.query(TermsRevision)
        .filter(TermsRevision.transaction_id == tx.id)
        .order_by(desc(TermsRevision.proposed_at))
        .first()
    )
    if latest_rev and latest_rev.final_total_paise is not None:
        gross_due_paise = latest_rev.final_total_paise
    elif tx.agreed_total_paise is not None:
        gross_due_paise = tx.agreed_total_paise
    else:
        gross_due_paise = tx.quoted_total_paise

    # 2. Query all payment entries for this transaction
    payments = (
        db.query(PaymentEntry)
        .filter(PaymentEntry.transaction_id == tx.id)
        .order_by(PaymentEntry.asserted_at.asc())
        .all()
    )

    acknowledged_paid_paise = 0
    asserted_pending_paise = 0
    disputed_paise = 0
    has_dispute = False

    for p in payments:
        if p.state == "ACKNOWLEDGED":
            acknowledged_paid_paise += p.amount_paise
        elif p.state == "ASSERTED":
            asserted_pending_paise += p.amount_paise
        elif p.state == "DISPUTED":
            disputed_paise += p.amount_paise
            has_dispute = True

    remaining_due_paise = max(0, gross_due_paise - acknowledged_paid_paise)
    overpaid_paise = max(0, acknowledged_paid_paise - gross_due_paise)
    is_settled = acknowledged_paid_paise >= gross_due_paise if gross_due_paise > 0 else True
    is_overpaid = acknowledged_paid_paise > gross_due_paise

    return {
        "gross_due_paise": gross_due_paise,
        "acknowledged_paid_paise": acknowledged_paid_paise,
        "asserted_pending_paise": asserted_pending_paise,
        "disputed_paise": disputed_paise,
        "remaining_due_paise": remaining_due_paise,
        "overpaid_paise": overpaid_paise,
        "is_settled": is_settled,
        "is_overpaid": is_overpaid,
        "has_dispute": has_dispute,
        "payments": payments
    }


# --- Request and Response Schemas ---

class CreatePaymentAssertionRequest(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Client-generated unique payment entry ID")
    amount_paise: int = Field(gt=0, description="Payment amount in integer paise (strictly > 0)")
    method: str = Field(default="CASH", description="Payment method: CASH, UPI, OTHER")
    private_reference: Optional[str] = Field(None, max_length=100, description="Optional UPI reference or note")
    occurred_at: Optional[datetime] = Field(None, description="Client asserted timestamp (UTC)")


class AcknowledgePaymentRequest(BaseModel):
    expected_amount_paise: Optional[int] = Field(None, description="Optional expected amount to prevent concurrency races")


class DisputePaymentRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=500, description="Mandatory dispute explanation")


class ReversePaymentRequest(BaseModel):
    reversal_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Client-generated ID for offsetting reversal record")
    reason: str = Field(min_length=3, max_length=500, description="Mandatory correction / reversal reason")


class PaymentEntryResponse(BaseModel):
    id: uuid.UUID
    transaction_id: uuid.UUID
    amount_paise: int
    method: str
    private_reference: Optional[str] = None
    asserted_by: str
    asserted_by_user_id: Optional[uuid.UUID] = None
    asserted_at: datetime
    state: str
    counterparty_ack_by: Optional[uuid.UUID] = None
    ack_at: Optional[datetime] = None
    reversal_of: Optional[uuid.UUID] = None
    reason: Optional[str] = None
    is_demo: bool
    created_at: datetime
    updated_at: datetime


class TransactionPaymentsSummary(BaseModel):
    transaction_id: uuid.UUID
    lifecycle: str
    gross_due_paise: int
    acknowledged_paid_paise: int
    asserted_pending_paise: int
    remaining_due_paise: int
    disputed_paise: int
    overpaid_paise: int
    is_settled: bool
    is_overpaid: bool
    has_dispute: bool
    payments: List[PaymentEntryResponse]


class PaymentReversalResponse(BaseModel):
    original_entry: PaymentEntryResponse
    reversal_entry: PaymentEntryResponse
    transaction_summary: TransactionPaymentsSummary


class TransactionCloseResponse(BaseModel):
    transaction_id: uuid.UUID
    lot_id: uuid.UUID
    lifecycle: str
    gross_due_paise: int
    acknowledged_paid_paise: int
    closed_at: datetime
    message: str


class MonthlyEarningsBucket(BaseModel):
    month: str  # YYYY-MM
    transaction_count: int
    gross_agreed_paise: int
    acknowledged_paid_paise: int
    asserted_pending_paise: int
    remaining_dues_paise: int


class CollectorEarningsResponse(BaseModel):
    collector_id: uuid.UUID
    total_transactions: int
    closed_transactions: int
    gross_agreed_paise: int
    acknowledged_paid_paise: int
    asserted_pending_paise: int
    remaining_dues_paise: int
    disputed_paise: int
    is_demo_isolated: bool
    freshness_timestamp: datetime
    monthly_breakdown: List[MonthlyEarningsBucket]


# --- Payment Endpoints ---

@router.post("/transactions/{id}/payments", response_model=PaymentEntryResponse, status_code=status.HTTP_201_CREATED)
@router.post("/api/v1/transactions/{id}/payments", response_model=PaymentEntryResponse, status_code=status.HTTP_201_CREATED)
def assert_payment(
    id: uuid.UUID,
    req: CreatePaymentAssertionRequest,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record cash/UPI/other payment assertion pending counterparty acknowledgement (R-PAY-01, AT-035)."""
    tx = get_transaction_or_404(db, id)

    # 1. Participant validation
    is_col = is_tx_collector(current_user, tx, db)
    is_fac = is_tx_facility_member(current_user, tx, db)
    if not (is_col or is_fac or current_user.role == UserRole.ADMIN.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You are not a participant in this transaction."
        )

    # 2. Method validation
    method_upper = req.method.upper().strip()
    if method_upper not in VALID_PAYMENT_METHODS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid payment method '{req.method}'. Supported methods: {sorted(VALID_PAYMENT_METHODS)}."
        )

    # 3. Transaction state check
    if tx.lifecycle in ("CANCELLED", "CLOSED"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot record payment assertion on transaction in '{tx.lifecycle}' state."
        )

    # 4. Duplicate-Safe Idempotency Check (R-PAY-02, AT-036)
    existing = db.query(PaymentEntry).filter(PaymentEntry.id == req.id).first()
    if existing:
        if existing.transaction_id == tx.id and existing.amount_paise == req.amount_paise:
            response.status_code = status.HTTP_200_OK
            return existing
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflict: Payment entry ID already exists with different transaction or amount."
        )

    # 5. Create PaymentEntry
    asserted_by = derive_asserted_by(current_user, tx, db)
    asserted_at = ensure_utc(req.occurred_at) or datetime.now(timezone.utc)

    entry = PaymentEntry(
        id=req.id,
        transaction_id=tx.id,
        amount_paise=req.amount_paise,
        method=method_upper,
        private_reference=req.private_reference,
        asserted_by=asserted_by,
        asserted_at=asserted_at,
        state="ASSERTED",
        asserted_by_user_id=current_user.id,
        # Demo provenance belongs to the transaction, never a client-controlled
        # payment payload flag.
        is_demo=tx.is_demo
    )
    db.add(entry)

    # 6. Append-only Domain Event
    record_payment_event(
        db=db,
        aggregate_id=tx.id,
        event_type="PAYMENT_ASSERTED",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state=None,
        next_state=entry.state,
        payload={
            "payment_id": str(entry.id),
            "amount_paise": entry.amount_paise,
            "method": entry.method,
            "private_reference": entry.private_reference,
            "asserted_by": entry.asserted_by,
            "asserted_at": entry.asserted_at.isoformat(),
            "state": entry.state
        }
    )
    db.commit()
    db.refresh(entry)

    return entry


@router.post("/payments/{id}/acknowledge", response_model=PaymentEntryResponse)
@router.post("/api/v1/payments/{id}/acknowledge", response_model=PaymentEntryResponse)
def acknowledge_payment(
    id: uuid.UUID,
    req: Optional[AcknowledgePaymentRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Counterparty acknowledges asserted payment (R-PAY-01, AT-035)."""
    entry = db.query(PaymentEntry).filter(PaymentEntry.id == id).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment entry not found.")

    tx = get_transaction_or_404(db, entry.transaction_id)

    # 1. Counterparty validation:
    # If asserted by FACILITY -> collector must acknowledge
    # If asserted by COLLECTOR -> facility member must acknowledge
    is_col = is_tx_collector(current_user, tx, db)
    is_fac = is_tx_facility_member(current_user, tx, db)

    if entry.asserted_by_user_id is not None and entry.asserted_by_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: The user who asserted a payment cannot acknowledge it."
        )

    if current_user.role != UserRole.ADMIN.value:
        if entry.asserted_by == "FACILITY" and not is_col:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: Only the collector counterparty can acknowledge a facility-asserted payment."
            )
        if entry.asserted_by == "COLLECTOR" and not is_fac:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: Only the facility counterparty can acknowledge a collector-asserted payment."
            )

    # 2. Concurrency / State check
    if entry.state == "ACKNOWLEDGED":
        # Idempotent replay
        return entry
    if entry.state in ("DISPUTED", "REVERSED"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot acknowledge payment entry in '{entry.state}' state."
        )

    if req and req.expected_amount_paise is not None:
        if req.expected_amount_paise != entry.amount_paise:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Payment amount mismatch: expected {req.expected_amount_paise}, actual {entry.amount_paise}."
            )

    # 3. Transition to ACKNOWLEDGED
    entry.state = "ACKNOWLEDGED"
    entry.counterparty_ack_by = current_user.id
    entry.ack_at = datetime.now(timezone.utc)
    entry.updated_at = datetime.now(timezone.utc)

    # 4. Domain Event
    record_payment_event(
        db=db,
        aggregate_id=tx.id,
        event_type="PAYMENT_ACKNOWLEDGED",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state="ASSERTED",
        next_state=entry.state,
        payload={
            "payment_id": str(entry.id),
            "amount_paise": entry.amount_paise,
            "acknowledged_by": str(current_user.id),
            "ack_at": entry.ack_at.isoformat()
        }
    )
    db.commit()
    db.refresh(entry)

    return entry


@router.post("/payments/{id}/dispute", response_model=PaymentEntryResponse)
@router.post("/api/v1/payments/{id}/dispute", response_model=PaymentEntryResponse)
def dispute_payment(
    id: uuid.UUID,
    req: DisputePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Participant disputes an asserted or acknowledged payment (R-PAY-01, AT-035)."""
    entry = db.query(PaymentEntry).filter(PaymentEntry.id == id).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment entry not found.")

    tx = get_transaction_or_404(db, entry.transaction_id)

    # 1. Participant check
    is_col = is_tx_collector(current_user, tx, db)
    is_fac = is_tx_facility_member(current_user, tx, db)
    if not (is_col or is_fac or current_user.role == UserRole.ADMIN.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You are not a participant in this transaction."
        )

    # 2. State check
    if entry.state == "REVERSED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot dispute a reversed payment entry."
        )

    # 3. Transition to DISPUTED
    prev_state = entry.state
    entry.state = "DISPUTED"
    entry.reason = req.reason
    entry.updated_at = datetime.now(timezone.utc)

    # 4. Domain event
    record_payment_event(
        db=db,
        aggregate_id=tx.id,
        event_type="PAYMENT_DISPUTED",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state=prev_state,
        next_state=entry.state,
        payload={
            "payment_id": str(entry.id),
            "disputed_by": str(current_user.id),
            "reason": req.reason
        }
    )
    db.commit()
    db.refresh(entry)

    return entry


@router.post("/payments/{id}/reverse", response_model=PaymentReversalResponse)
@router.post("/api/v1/payments/{id}/reverse", response_model=PaymentReversalResponse)
def reverse_payment(
    id: uuid.UUID,
    req: ReversePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Authorized reviewed correction / reversal linking original record without deletion (R-PAY-02, AT-036)."""
    original = db.query(PaymentEntry).filter(PaymentEntry.id == id).first()
    if not original:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment entry not found.")

    tx = get_transaction_or_404(db, original.transaction_id)

    # 1. Participant check
    is_col = is_tx_collector(current_user, tx, db)
    is_fac = is_tx_facility_member(current_user, tx, db)
    if not (is_col or is_fac or current_user.role == UserRole.ADMIN.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You are not a participant in this transaction."
        )

    # 2. Cannot reverse an already reversed entry
    if original.state == "REVERSED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Payment entry is already reversed."
        )

    # 3. Mark original as REVERSED
    original.state = "REVERSED"
    original.reason = req.reason
    original.updated_at = datetime.now(timezone.utc)

    # 4. Append-only reversal entry linking original ID
    asserted_by = derive_asserted_by(current_user, tx, db)
    reversal_entry = PaymentEntry(
        id=req.reversal_id,
        transaction_id=tx.id,
        amount_paise=original.amount_paise,
        method=original.method,
        private_reference=f"REVERSAL:{original.id}",
        asserted_by=asserted_by,
        asserted_at=datetime.now(timezone.utc),
        state="REVERSED",
        reversal_of=original.id,
        reason=f"Reversal of {original.id}: {req.reason}",
        is_demo=original.is_demo
    )
    db.add(reversal_entry)

    # 5. Domain event
    record_payment_event(
        db=db,
        aggregate_id=tx.id,
        event_type="PAYMENT_REVERSED",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state="REVERSED",
        next_state="REVERSED",
        payload={
            "original_payment_id": str(original.id),
            "reversal_payment_id": str(reversal_entry.id),
            "amount_paise": original.amount_paise,
            "reversed_by": str(current_user.id),
            "reason": req.reason
        }
    )
    db.commit()
    db.refresh(original)
    db.refresh(reversal_entry)

    # 6. Recalculate transaction summary
    summary_data = compute_transaction_balances(tx, db)
    tx_summary = TransactionPaymentsSummary(
        transaction_id=tx.id,
        lifecycle=tx.lifecycle,
        gross_due_paise=summary_data["gross_due_paise"],
        acknowledged_paid_paise=summary_data["acknowledged_paid_paise"],
        asserted_pending_paise=summary_data["asserted_pending_paise"],
        remaining_due_paise=summary_data["remaining_due_paise"],
        disputed_paise=summary_data["disputed_paise"],
        overpaid_paise=summary_data["overpaid_paise"],
        is_settled=summary_data["is_settled"],
        is_overpaid=summary_data["is_overpaid"],
        has_dispute=summary_data["has_dispute"],
        payments=[PaymentEntryResponse.model_validate(p, from_attributes=True) for p in summary_data["payments"]]
    )

    return PaymentReversalResponse(
        original_entry=PaymentEntryResponse.model_validate(original, from_attributes=True),
        reversal_entry=PaymentEntryResponse.model_validate(reversal_entry, from_attributes=True),
        transaction_summary=tx_summary
    )


@router.get("/transactions/{id}/payments", response_model=TransactionPaymentsSummary)
@router.get("/api/v1/transactions/{id}/payments", response_model=TransactionPaymentsSummary)
def get_transaction_payments(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve dues and acknowledged payments ledger for a transaction (R-PAY-01, R-PAY-02, AT-035, AT-036)."""
    tx = get_transaction_or_404(db, id)

    # Participant check
    is_col = is_tx_collector(current_user, tx, db)
    is_fac = is_tx_facility_member(current_user, tx, db)
    if not (is_col or is_fac or current_user.role == UserRole.ADMIN.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You are not a participant in this transaction."
        )

    summary_data = compute_transaction_balances(tx, db)
    return TransactionPaymentsSummary(
        transaction_id=tx.id,
        lifecycle=tx.lifecycle,
        gross_due_paise=summary_data["gross_due_paise"],
        acknowledged_paid_paise=summary_data["acknowledged_paid_paise"],
        asserted_pending_paise=summary_data["asserted_pending_paise"],
        remaining_due_paise=summary_data["remaining_due_paise"],
        disputed_paise=summary_data["disputed_paise"],
        overpaid_paise=summary_data["overpaid_paise"],
        is_settled=summary_data["is_settled"],
        is_overpaid=summary_data["is_overpaid"],
        has_dispute=summary_data["has_dispute"],
        payments=[PaymentEntryResponse.model_validate(p, from_attributes=True) for p in summary_data["payments"]]
    )


@router.post("/transactions/{id}/close", response_model=TransactionCloseResponse)
@router.post("/api/v1/transactions/{id}/close", response_model=TransactionCloseResponse)
def close_transaction(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Close transaction only at confirmed receipt and settled undisputed payment (R-PAY-02, AT-036)."""
    tx = get_transaction_or_404(db, id)

    # 1. Participant check
    is_col = is_tx_collector(current_user, tx, db)
    is_fac = is_tx_facility_member(current_user, tx, db)
    if not (is_col or is_fac or current_user.role == UserRole.ADMIN.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You are not a participant in this transaction."
        )

    if tx.lifecycle == "CLOSED":
        # Idempotent return
        lot = db.query(Lot).filter(Lot.id == tx.lot_id).first()
        summary = compute_transaction_balances(tx, db)
        return TransactionCloseResponse(
            transaction_id=tx.id,
            lot_id=tx.lot_id,
            lifecycle="CLOSED",
            gross_due_paise=summary["gross_due_paise"],
            acknowledged_paid_paise=summary["acknowledged_paid_paise"],
            closed_at=tx.updated_at,
            message="Transaction is already closed."
        )

    # 2. Hard Invariant 1: Handover MUST be confirmed
    confirmed_handover = (
        db.query(Handover)
        .filter(Handover.transaction_id == tx.id, Handover.status == "CONFIRMED")
        .first()
    )
    if not confirmed_handover:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Transaction cannot be closed: Confirmed handover receipt is required before closure."
        )

    # 3. Hard Invariant 2: Zero active disputes
    summary = compute_transaction_balances(tx, db)
    if summary["has_dispute"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Transaction cannot be closed: Active payment dispute exists on this transaction."
        )

    disputed_handover = (
        db.query(Handover)
        .filter(Handover.transaction_id == tx.id, Handover.status == "DISPUTED")
        .first()
    )
    if disputed_handover:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Transaction cannot be closed: Handover is marked disputed."
        )

    # 4. Hard Invariant 3: Dues must be fully settled (remaining_due_paise == 0)
    if summary["remaining_due_paise"] > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Transaction cannot be closed: Outstanding dues of {summary['remaining_due_paise']} paise remain."
        )

    # 5. Transition transaction to CLOSED and linked lot to CLOSED
    now = datetime.now(timezone.utc)
    tx.lifecycle = "CLOSED"
    tx.updated_at = now

    lot = db.query(Lot).filter(Lot.id == tx.lot_id).first()
    if lot:
        lot.status = "CLOSED"
        lot.updated_at = now

    # 6. Domain event
    record_payment_event(
        db=db,
        aggregate_id=tx.id,
        event_type="TRANSACTION_CLOSED",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state="CONFIRMED",
        next_state="CLOSED",
        payload={
            "transaction_id": str(tx.id),
            "lot_id": str(tx.lot_id),
            "gross_due_paise": summary["gross_due_paise"],
            "acknowledged_paid_paise": summary["acknowledged_paid_paise"],
            "closed_by": str(current_user.id),
            "closed_at": now.isoformat()
        }
    )

    # 7. Data Lineage Feedback (R-LINE-02, AT-071): Transform closed transaction outcome into platform price observation
    existing_obs = (
        db.query(PriceObservation)
        .filter(PriceObservation.transaction_id == tx.id)
        .first()
    )
    if not existing_obs and lot:
        latest_rev = (
            db.query(TermsRevision)
            .filter(TermsRevision.transaction_id == tx.id)
            .order_by(desc(TermsRevision.proposed_at))
            .first()
        )
        final_mat_id = latest_rev.final_material_id if latest_rev else lot.material_id
        final_weight_grams = (
            latest_rev.measured_weight_g
            if latest_rev
            else (tx.agreed_weight_g or lot.estimated_weight_g or 1000)
        )
        final_amount_paise = (
            latest_rev.final_total_paise
            if latest_rev
            else (tx.agreed_total_paise or summary["gross_due_paise"])
        )

        effective_rate_paise_per_kg = (
            int(round((final_amount_paise * 1000.0) / final_weight_grams))
            if final_weight_grams > 0
            else 0
        )

        if final_mat_id and effective_rate_paise_per_kg > 0:
            price_obs = PriceObservation(
                id=uuid.uuid4(),
                material_id=final_mat_id,
                subcategory_id=None,
                region_id="DELHI_NCR",
                condition=lot.condition or "CLEAN",
                rate_paise_per_unit=effective_rate_paise_per_kg,
                unit="kg",
                price_kind="BUY",
                observed_at=now,
                facility_id=tx.facility_id,
                transaction_id=tx.id,
                source_id=f"TX-{tx.id}",
                review_status="PENDING_REVIEW",
                origin_class="PLATFORM_GENERATED",
                source_kind="VERIFIED_TRANSACTION",
                is_demo=tx.is_demo,
                created_at=now
            )
            db.add(price_obs)
            record_payment_event(
                db=db,
                aggregate_id=tx.id,
                event_type="PRICE_OBSERVATION_CREATED_FROM_TRANSACTION",
                actor_id=current_user.id,
                role=current_user.role,
                previous_state=None,
                next_state="PENDING_REVIEW",
                payload={
                    "price_observation_id": str(price_obs.id),
                    "transaction_id": str(tx.id),
                    "material_id": final_mat_id,
                    "rate_paise_per_kg": effective_rate_paise_per_kg,
                    "source_kind": "VERIFIED_TRANSACTION",
                    "origin_class": "PLATFORM_GENERATED"
                }
            )

    db.commit()
    db.refresh(tx)

    return TransactionCloseResponse(
        transaction_id=tx.id,
        lot_id=tx.lot_id,
        lifecycle="CLOSED",
        gross_due_paise=summary["gross_due_paise"],
        acknowledged_paid_paise=summary["acknowledged_paid_paise"],
        closed_at=now,
        message="Transaction and material lot successfully closed with verified receipt and settled payment."
    )


@router.get("/collector/earnings", response_model=CollectorEarningsResponse)
@router.get("/api/v1/collector/earnings", response_model=CollectorEarningsResponse)
def get_collector_earnings(
    collector_id: Optional[uuid.UUID] = Query(None, description="Admin override: specify collector ID"),
    month: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}$", description="Filter by YYYY-MM"),
    from_date: Optional[datetime] = Query(None, description="Start date filter (UTC)"),
    to_date: Optional[datetime] = Query(None, description="End date filter (UTC)"),
    include_demo: bool = Query(False, description="Whether to include demo transactions (default False for strict isolation)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve collector earnings history, monthly buckets, and outstanding dues with demo isolation (R-PAY-03, AT-037)."""
    # 1. Resolve collector
    if current_user.role == UserRole.COLLECTOR.value:
        collector = db.query(Collector).filter(Collector.user_id == current_user.id).first()
        if not collector:
            raise HTTPException(status_code=404, detail="Collector profile not found.")
        target_collector_id = collector.id
    elif current_user.role == UserRole.ADMIN.value:
        if not collector_id:
            raise HTTPException(status_code=422, detail="Admin query requires 'collector_id' parameter.")
        target_collector_id = collector_id
    else:
        raise HTTPException(status_code=403, detail="Forbidden: Only collectors or admins can access earnings.")

    # 2. Query transactions for this collector
    tx_query = db.query(Transaction).filter(Transaction.collector_id == target_collector_id)
    if not include_demo:
        tx_query = tx_query.filter(Transaction.is_demo == False)

    transactions = tx_query.order_by(Transaction.created_at.desc()).all()

    # 3. Monthly aggregation structures
    monthly_data: Dict[str, Dict[str, int]] = {}

    total_gross = 0
    total_paid = 0
    total_pending = 0
    total_remaining = 0
    total_disputed = 0
    closed_count = 0
    filtered_tx_count = 0

    from_utc = ensure_utc(from_date)
    to_utc = ensure_utc(to_date)

    for tx in transactions:
        tx_created = ensure_utc(tx.created_at)
        tx_month = tx_created.strftime("%Y-%m")

        # Filters
        if month and tx_month != month:
            continue
        if from_utc and tx_created < from_utc:
            continue
        if to_utc and tx_created > to_utc:
            continue

        filtered_tx_count += 1
        if tx.lifecycle == "CLOSED":
            closed_count += 1

        summary = compute_transaction_balances(tx, db)

        # Aggregate monthly
        if tx_month not in monthly_data:
            monthly_data[tx_month] = {
                "count": 0,
                "gross": 0,
                "paid": 0,
                "pending": 0,
                "remaining": 0
            }

        m_entry = monthly_data[tx_month]
        m_entry["count"] += 1
        m_entry["gross"] += summary["gross_due_paise"]
        m_entry["paid"] += summary["acknowledged_paid_paise"]
        m_entry["pending"] += summary["asserted_pending_paise"]
        m_entry["remaining"] += summary["remaining_due_paise"]

        total_gross += summary["gross_due_paise"]
        total_paid += summary["acknowledged_paid_paise"]
        total_pending += summary["asserted_pending_paise"]
        total_remaining += summary["remaining_due_paise"]
        total_disputed += summary["disputed_paise"]

    # Format monthly buckets descending
    buckets = [
        MonthlyEarningsBucket(
            month=k,
            transaction_count=v["count"],
            gross_agreed_paise=v["gross"],
            acknowledged_paid_paise=v["paid"],
            asserted_pending_paise=v["pending"],
            remaining_dues_paise=v["remaining"]
        )
        for k, v in sorted(monthly_data.items(), reverse=True)
    ]

    return CollectorEarningsResponse(
        collector_id=target_collector_id,
        total_transactions=filtered_tx_count,
        closed_transactions=closed_count,
        gross_agreed_paise=total_gross,
        acknowledged_paid_paise=total_paid,
        asserted_pending_paise=total_pending,
        remaining_dues_paise=total_remaining,
        disputed_paise=total_disputed,
        is_demo_isolated=not include_demo,
        freshness_timestamp=datetime.now(timezone.utc),
        monthly_breakdown=buckets
    )
