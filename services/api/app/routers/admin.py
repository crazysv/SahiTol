"""Admin Metrics, Quality Flags, Anomaly Review, and Moderation router.
Technical specification: docs/03_TECHSPEC.md lines 85-100, docs/MONITORING.md, docs/16_API_CONTRACT.md lines 84-87.
Requirements: R-PRICE-05, R-HAND-05, R-ADMIN-02, R-OPS-04.
Acceptance cases: AT-020, AT-033, AT-065, AT-077.
"""
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, select, String, Integer

from app.db.session import get_db
from app.db.models.audit import DomainEvent, QualityFlag
from app.db.models.price import PriceObservation
from app.db.models.auth import User
from app.db.models.collector import Collector
from app.db.models.facility import Facility, FacilityAuthorization
from app.db.models.material import MaterialCategory, Material, MaterialAlias, SafetyGuide
from app.db.models.lot import Lot
from app.db.models.trade import Transaction, Handover, PaymentEntry, LotRequest, Offer, TermsRevision
from app.domain.canonical import compute_canonical_hash
from app.domain.quality import (
    POLICY_VERSION,
    QualitySeverity,
    QualityFlagStatus,
    RULE_PRICE_OUTLIER,
    RULE_WEIGHT_VARIANCE,
    RULE_LARGE_WEIGHT,
    RULE_DUPLICATE_MEDIA,
    RULE_REPEATED_SALE,
    RULE_STALE_EVIDENCE,
    RULE_INCOMPLETE_HANDOVER,
    RULE_MISSING_INVALID,
    evaluate_price_quote,
    evaluate_weight_variance,
    evaluate_large_weight,
    evaluate_duplicate_media,
    evaluate_repeated_sale,
    evaluate_stale_evidence,
    evaluate_handover_completeness,
    evaluate_missing_invalid,
)
from app.routers.materials import normalize_term
from app.security import UserRole, require_roles

ADMIN_UUID_NAMESPACE = uuid.UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")

router = APIRouter(tags=["admin"])



# ---------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------

class PriceReviewDecisionRequest(BaseModel):
    decision: str  # APPROVE, REJECT
    reason: Optional[str] = None


class PriceReviewItemResponse(BaseModel):
    id: uuid.UUID
    material_id: str
    region_id: str
    rate_paise_per_unit: int
    unit: str
    price_kind: str
    observed_at: str
    source_id: str
    review_status: str
    is_demo: bool


class QualityFlagResponse(BaseModel):
    id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID
    entity_version: int
    rule_id: str
    policy_version: str
    severity: str
    evidence_json: Dict[str, Any]
    status: str
    assigned_to: Optional[uuid.UUID] = None
    resolved_by: Optional[uuid.UUID] = None
    resolved_at: Optional[str] = None
    reason: Optional[str] = None
    created_at: str
    updated_at: str


class QualityFlagResolveRequest(BaseModel):
    decision: str = Field(..., description="Resolution decision: RESOLVE, DISMISS, or ACKNOWLEDGE")
    reason: str = Field(..., min_length=3, description="Mandatory justification for resolution or dismissal")
    notes: Optional[str] = Field(None, description="Optional extra notes")


class QualitySummaryResponse(BaseModel):
    policy_version: str
    total_flags: int
    status_counts: Dict[str, int]
    severity_counts: Dict[str, int]
    rule_counts: Dict[str, int]
    entity_type_counts: Dict[str, int]
    open_fraction: float
    resolved_fraction: float
    last_refresh: str
    as_of: str


class EvaluateEntityRequest(BaseModel):
    entity_type: str = Field(..., description="Entity type: LOT, OFFER, HANDOVER, PRICE_OBSERVATION")
    rate_paise_per_unit: Optional[int] = None
    comparable_rates: Optional[List[int]] = None
    estimated_weight_g: Optional[int] = None
    received_weight_g: Optional[int] = None
    weight_g: Optional[int] = None
    amount_paise: Optional[int] = None
    media_sha256: Optional[str] = None
    current_lot_id: Optional[uuid.UUID] = None
    existing_lot_ids: Optional[List[uuid.UUID]] = None
    has_counterparty_confirmation: Optional[bool] = None
    has_location: Optional[bool] = None
    has_evidence: Optional[bool] = None


class EvaluateEntityResponse(BaseModel):
    passed: bool
    rule_id: str
    severity: str
    reason: str
    details: Dict[str, Any]


# ---------------------------------------------------------
# Admin Overview & Maintenance Schemas (T029)
# ---------------------------------------------------------

class CollectorsOverview(BaseModel):
    total_registered: int
    active_in_window: int
    demo_collectors: int


class FacilitiesOverview(BaseModel):
    total_facilities: int
    verified_facilities: int
    by_kind: Dict[str, int]


class LotsOverview(BaseModel):
    total_lots: int
    by_status: Dict[str, int]
    demo_lots_count: int


class TradeOverview(BaseModel):
    total_requests: int
    total_offers: int
    offers_accepted: int
    acceptance_rate: float


class HandoversOverview(BaseModel):
    total_handovers: int
    confirmed_count: int
    disputed_count: int
    formal_received_mass_g: int
    demo_mass_g: int
    mass_label: str = "received, not recycled"


class FinancialsOverview(BaseModel):
    gross_agreed_paise: int
    acknowledged_paid_paise: int
    outstanding_dues_paise: int
    disputed_paise: int


class QualityOverview(BaseModel):
    total_flags: int
    open_flags: int
    resolved_flags: int


class AdminOverviewResponse(BaseModel):
    as_of: str
    last_refresh: str
    include_demo: bool
    region_id: Optional[str] = None
    collectors: CollectorsOverview
    facilities: FacilitiesOverview
    lots: LotsOverview
    trade: TradeOverview
    handovers: HandoversOverview
    financials: FinancialsOverview
    quality: QualityOverview
    unmet_fieldwork_obligation: str = "UNMET"


class CollectorMinimalResponse(BaseModel):
    id: uuid.UUID
    display_alias: Optional[str]
    preferred_language: str
    general_area: Optional[str]
    region_id: Optional[str]
    created_at: str
    lot_count: int
    active_lot_count: int


class AdminMaterialCreateRequest(BaseModel):
    id: str = Field(..., min_length=3, max_length=50, description="Material ID e.g. MAT-NEW-01")
    category_id: str
    subcategory_code: str
    description_key: str
    allowed_units: str = "kg,g"
    default_route: str = "GENERAL_RECYCLING"
    route_requires_context: bool = False
    condition_options: Optional[List[str]] = None
    safety_guide_ids: Optional[List[str]] = None


class AdminMaterialUpdateRequest(BaseModel):
    description_key: Optional[str] = None
    active: Optional[bool] = None
    default_route: Optional[str] = None
    route_requires_context: Optional[bool] = None
    condition_options: Optional[List[str]] = None
    safety_guide_ids: Optional[List[str]] = None


class AdminMaterialResponse(BaseModel):
    id: str
    category_id: str
    subcategory_code: str
    description_key: str
    allowed_units: str
    default_route: str
    route_requires_context: bool
    condition_options: List[str]
    safety_guide_ids: List[str]
    active: bool
    alias_count: int
    created_at: str
    updated_at: str


class AdminMaterialAliasCreateRequest(BaseModel):
    material_id: str
    language: str = Field(..., min_length=2, max_length=10)
    local_term: str = Field(..., min_length=1, max_length=100)


class AdminMaterialAliasResponse(BaseModel):
    id: uuid.UUID
    material_id: str
    language: str
    local_term: str
    normalized_term: str


class AdminSafetyGuideCreateRequest(BaseModel):
    id: str = Field(..., min_length=3, max_length=50)
    material_ids: List[str]
    route: str
    text_key: str
    icon_asset_ref: str
    image_asset_ref: Optional[str] = None
    audio_keys: Optional[Dict[str, str]] = None
    source_ids: Optional[List[str]] = None
    version: str = "v1.0"
    review_status: str = "APPROVED"


class AdminSafetyGuideUpdateRequest(BaseModel):
    route: Optional[str] = None
    text_key: Optional[str] = None
    icon_asset_ref: Optional[str] = None
    image_asset_ref: Optional[str] = None
    audio_keys: Optional[Dict[str, str]] = None
    source_ids: Optional[List[str]] = None
    version: Optional[str] = None
    review_status: Optional[str] = None


class AdminSafetyGuideResponse(BaseModel):
    id: str
    material_ids: List[str]
    route: str
    text_key: str
    icon_asset_ref: str
    image_asset_ref: Optional[str]
    audio_keys: Dict[str, str]
    source_ids: List[str]
    version: str
    review_status: str


class AdminFacilityVerificationRequest(BaseModel):
    route: str = Field(..., description="Regulatory route e.g. GENERAL_RECYCLING, AUTHORIZED_EWASTE, BATTERY_ISOLATION")
    authority: str = Field(..., description="Issuing authority e.g. CPCB, DPCC, MPCB, NDMC")
    reference: str = Field(..., description="Official authorization or registration certificate number")
    status: str = Field("VALID", description="Authorization status: VALID, EXPIRED, SUSPENDED")
    verification_level: str = Field("REGISTRY_MATCH", description="Verification level: REGISTRY_MATCH, PHYSICAL_AUDIT, DESK_REVIEW")
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    source_id: Optional[str] = None
    scope_notes: Optional[str] = None
    reason: str = Field(..., min_length=5, description="Mandatory audit justification for asserting verification")


class AdminFacilityVerificationResponse(BaseModel):
    id: uuid.UUID
    facility_id: uuid.UUID
    route: str
    authority: str
    reference: str
    status: str
    verification_level: str
    valid_from: Optional[str]
    valid_until: Optional[str]
    reviewer_id: uuid.UUID
    last_verified_at: str
    scope_notes: Optional[str]
    reason: str


class DomainEventResponse(BaseModel):
    id: uuid.UUID
    aggregate_type: str
    aggregate_id: uuid.UUID
    sequence: int
    event_type: str
    actor_id: Optional[uuid.UUID]
    role: str
    occurred_at: str
    payload_json: Dict[str, Any]
    prev_hash: str
    event_hash: str


class TraceabilityReportResponse(BaseModel):
    lot_id: uuid.UUID
    lot_status: Optional[str]
    material_id: Optional[str]
    events_count: int
    is_hash_chain_valid: bool
    events: List[DomainEventResponse]


# ---------------------------------------------------------
# Domain Event Helpers
# ---------------------------------------------------------

def record_admin_event(
    db: Session,
    aggregate_type: str,
    aggregate_id: uuid.UUID,
    event_type: str,
    actor_id: uuid.UUID,
    role: str,
    payload: Dict[str, Any],
    previous_state: Optional[str] = None,
    next_state: Optional[str] = None
) -> DomainEvent:
    """Record append-only hash-chained domain event for administrative actions (T029)."""
    now = datetime.now(timezone.utc)
    prev_event = (
        db.query(DomainEvent)
        .filter(DomainEvent.aggregate_id == aggregate_id)
        .order_by(desc(DomainEvent.sequence))
        .first()
    )
    seq = (prev_event.sequence + 1) if prev_event else 1
    prev_hash = prev_event.event_hash if prev_event else "GENESIS"

    event_payload = {
        "event_id": str(uuid.uuid4()),
        "aggregate_type": aggregate_type,
        "aggregate_id": str(aggregate_id),
        "sequence": seq,
        "event_type": event_type,
        "actor_id": str(actor_id),
        "role": role,
        "occurred_at": now.isoformat(),
        "previous_state": previous_state,
        "next_state": next_state,
        "payload": payload,
        "prev_hash": prev_hash
    }
    event_hash = compute_canonical_hash(event_payload)

    event = DomainEvent(
        id=uuid.UUID(event_payload["event_id"]),
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        sequence=seq,
        event_type=event_type,
        actor_id=actor_id,
        role=role,
        received_at_server=now,
        previous_state=previous_state,
        next_state=next_state,
        payload_json=event_payload["payload"],
        prev_hash=prev_hash,
        event_hash=event_hash
    )
    db.add(event)
    return event


def record_quality_event(
    db: Session,
    flag_id: uuid.UUID,
    event_type: str,
    actor_id: uuid.UUID,
    role: str,
    previous_state: Optional[str],
    next_state: str,
    payload: Dict[str, Any]
) -> DomainEvent:
    """Record append-only hash-chained domain event for quality review actions."""
    now = datetime.now(timezone.utc)
    prev_event = (
        db.query(DomainEvent)
        .filter(DomainEvent.aggregate_id == flag_id)
        .order_by(desc(DomainEvent.sequence))
        .first()
    )
    seq = (prev_event.sequence + 1) if prev_event else 1
    prev_hash = prev_event.event_hash if prev_event else "GENESIS"

    event_payload = {
        "event_id": str(uuid.uuid4()),
        "aggregate_type": "QUALITY_FLAG",
        "aggregate_id": str(flag_id),
        "sequence": seq,
        "event_type": event_type,
        "actor_id": str(actor_id),
        "role": role,
        "occurred_at": now.isoformat(),
        "previous_state": previous_state,
        "next_state": next_state,
        "payload": payload,
        "prev_hash": prev_hash
    }
    event_hash = compute_canonical_hash(event_payload)

    event = DomainEvent(
        id=uuid.UUID(event_payload["event_id"]),
        aggregate_type="QUALITY_FLAG",
        aggregate_id=flag_id,
        sequence=seq,
        event_type=event_type,
        actor_id=actor_id,
        role=role,
        received_at_server=now,
        previous_state=previous_state,
        next_state=next_state,
        payload_json=event_payload["payload"],
        prev_hash=prev_hash,
        event_hash=event_hash
    )
    db.add(event)
    return event


# ---------------------------------------------------------
# Quality Flag Endpoints (QUALITY_V1)
# ---------------------------------------------------------

@router.get("/api/v1/admin/quality-flags", response_model=List[QualityFlagResponse])
@router.get("/admin/quality-flags", response_model=List[QualityFlagResponse])
def list_quality_flags(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: OPEN, ACKNOWLEDGED, RESOLVED, DISMISSED"),
    severity: Optional[str] = Query(None, description="Filter by severity: LOW, MEDIUM, HIGH, CRITICAL"),
    rule_id: Optional[str] = Query(None, description="Filter by rule ID: DQ-PRICE-OUTLIER, DQ-WEIGHT-VARIANCE, etc."),
    entity_type: Optional[str] = Query(None, description="Filter by entity type: LOT, OFFER, HANDOVER, etc."),
    entity_id: Optional[uuid.UUID] = Query(None, description="Filter by specific entity UUID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    List data quality and anomaly review flags under QUALITY_V1 with entity drill-down.
    Supports filtering by severity, rule, entity type, and resolution status.
    """
    stmt = select(QualityFlag)
    if status_filter:
        stmt = stmt.where(QualityFlag.status == status_filter.upper())
    if severity:
        stmt = stmt.where(QualityFlag.severity == severity.upper())
    if rule_id:
        stmt = stmt.where(QualityFlag.rule_id == rule_id)
    if entity_type:
        stmt = stmt.where(QualityFlag.entity_type == entity_type.upper())
    if entity_id:
        stmt = stmt.where(QualityFlag.entity_id == entity_id)

    stmt = stmt.order_by(QualityFlag.created_at.desc()).offset(offset).limit(limit)
    rows = db.execute(stmt).scalars().all()

    return [
        QualityFlagResponse(
            id=r.id,
            entity_type=r.entity_type,
            entity_id=r.entity_id,
            entity_version=r.entity_version,
            rule_id=r.rule_id,
            policy_version=r.policy_version,
            severity=r.severity,
            evidence_json=r.evidence_json or {},
            status=r.status,
            assigned_to=r.assigned_to,
            resolved_by=r.resolved_by,
            resolved_at=r.resolved_at.isoformat() if r.resolved_at else None,
            reason=r.reason,
            created_at=r.created_at.isoformat(),
            updated_at=r.updated_at.isoformat()
        )
        for r in rows
    ]


@router.get("/api/v1/admin/quality-flags/summary", response_model=QualitySummaryResponse)
@router.get("/admin/quality-flags/summary", response_model=QualitySummaryResponse)
def get_quality_summary(
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Calculate quality review metrics with real denominators (R-ADMIN-02 / AT-065).
    Computes status, severity, and rule distributions with real query evidence.
    """
    now = datetime.now(timezone.utc)
    flags = db.execute(select(QualityFlag)).scalars().all()
    total = len(flags)

    status_counts: Dict[str, int] = {"OPEN": 0, "ACKNOWLEDGED": 0, "RESOLVED": 0, "DISMISSED": 0}
    severity_counts: Dict[str, int] = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    rule_counts: Dict[str, int] = {}
    entity_type_counts: Dict[str, int] = {}

    for f in flags:
        status_counts[f.status] = status_counts.get(f.status, 0) + 1
        severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1
        rule_counts[f.rule_id] = rule_counts.get(f.rule_id, 0) + 1
        entity_type_counts[f.entity_type] = entity_type_counts.get(f.entity_type, 0) + 1

    open_frac = (status_counts["OPEN"] / float(total)) if total > 0 else 0.0
    resolved_frac = ((status_counts["RESOLVED"] + status_counts["DISMISSED"]) / float(total)) if total > 0 else 0.0

    return QualitySummaryResponse(
        policy_version=POLICY_VERSION,
        total_flags=total,
        status_counts=status_counts,
        severity_counts=severity_counts,
        rule_counts=rule_counts,
        entity_type_counts=entity_type_counts,
        open_fraction=round(open_frac, 4),
        resolved_fraction=round(resolved_frac, 4),
        last_refresh=now.isoformat(),
        as_of=now.isoformat()
    )


@router.get("/api/v1/admin/quality-flags/{flag_id}", response_model=QualityFlagResponse)
@router.get("/admin/quality-flags/{flag_id}", response_model=QualityFlagResponse)
def get_quality_flag_detail(
    flag_id: uuid.UUID,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Retrieve detailed single quality flag with inputs and evidence drill-down."""
    flag = db.execute(select(QualityFlag).where(QualityFlag.id == flag_id)).scalar_one_or_none()
    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quality flag '{flag_id}' not found."
        )

    return QualityFlagResponse(
        id=flag.id,
        entity_type=flag.entity_type,
        entity_id=flag.entity_id,
        entity_version=flag.entity_version,
        rule_id=flag.rule_id,
        policy_version=flag.policy_version,
        severity=flag.severity,
        evidence_json=flag.evidence_json or {},
        status=flag.status,
        assigned_to=flag.assigned_to,
        resolved_by=flag.resolved_by,
        resolved_at=flag.resolved_at.isoformat() if flag.resolved_at else None,
        reason=flag.reason,
        created_at=flag.created_at.isoformat(),
        updated_at=flag.updated_at.isoformat()
    )


@router.post("/api/v1/admin/quality-flags/{flag_id}/resolve", response_model=QualityFlagResponse)
@router.post("/admin/quality-flags/{flag_id}/resolve", response_model=QualityFlagResponse)
def resolve_quality_flag(
    flag_id: uuid.UUID,
    payload: QualityFlagResolveRequest,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Resolve, acknowledge, or dismiss a quality flag with mandatory justification (AT-065).
    Invariants:
    - Dismissal and resolution require non-empty reason.
    - Underlying evidence is immutable; cannot fabricate consent or delete records.
    - Emits append-only hash-chained domain event.
    """
    flag = db.execute(select(QualityFlag).where(QualityFlag.id == flag_id)).scalar_one_or_none()
    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quality flag '{flag_id}' not found."
        )

    decision = payload.decision.upper()
    if decision not in {"RESOLVE", "DISMISS", "ACKNOWLEDGE"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="decision must be 'RESOLVE', 'DISMISS', or 'ACKNOWLEDGE'."
        )

    if not payload.reason or len(payload.reason.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A non-empty justification reason (at least 3 characters) is mandatory."
        )

    now = datetime.now(timezone.utc)
    prev_status = flag.status

    if decision == "RESOLVE":
        next_status = "RESOLVED"
        flag.resolved_by = current_user.id
        flag.resolved_at = now
    elif decision == "DISMISS":
        next_status = "DISMISSED"
        flag.resolved_by = current_user.id
        flag.resolved_at = now
    else:  # ACKNOWLEDGE
        next_status = "ACKNOWLEDGED"
        flag.assigned_to = current_user.id

    flag.status = next_status
    resolution_text = f"[{decision}] {payload.reason.strip()}"
    if payload.notes:
        resolution_text += f" | Notes: {payload.notes.strip()}"
    flag.reason = f"{flag.reason} | {resolution_text}" if flag.reason else resolution_text
    flag.updated_at = now

    record_quality_event(
        db=db,
        flag_id=flag.id,
        event_type=f"QUALITY_FLAG_{next_status}",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state=prev_status,
        next_state=next_status,
        payload={
            "flag_id": str(flag.id),
            "rule_id": flag.rule_id,
            "entity_type": flag.entity_type,
            "entity_id": str(flag.entity_id),
            "decision": decision,
            "reason": payload.reason.strip(),
            "notes": payload.notes
        }
    )

    db.commit()
    db.refresh(flag)

    return QualityFlagResponse(
        id=flag.id,
        entity_type=flag.entity_type,
        entity_id=flag.entity_id,
        entity_version=flag.entity_version,
        rule_id=flag.rule_id,
        policy_version=flag.policy_version,
        severity=flag.severity,
        evidence_json=flag.evidence_json or {},
        status=flag.status,
        assigned_to=flag.assigned_to,
        resolved_by=flag.resolved_by,
        resolved_at=flag.resolved_at.isoformat() if flag.resolved_at else None,
        reason=flag.reason,
        created_at=flag.created_at.isoformat(),
        updated_at=flag.updated_at.isoformat()
    )


@router.post("/api/v1/admin/quality-flags/evaluate", response_model=EvaluateEntityResponse)
def evaluate_entity_quality(
    payload: EvaluateEntityRequest,
    current_user: User = Depends(require_roles(UserRole.ADMIN))
):
    """
    On-demand quality rule evaluation endpoint under QUALITY_V1.
    Evaluates inputs against specified quality rules and returns result without persisting.
    """
    entity = payload.entity_type.upper()

    if entity == "OFFER" and payload.rate_paise_per_unit is not None:
        result = evaluate_price_quote(
            rate_paise_per_unit=payload.rate_paise_per_unit,
            comparable_rates=payload.comparable_rates or []
        )
    elif entity == "HANDOVER" and payload.estimated_weight_g is not None and payload.received_weight_g is not None:
        result = evaluate_weight_variance(
            estimated_weight_g=payload.estimated_weight_g,
            received_weight_g=payload.received_weight_g
        )
    elif payload.weight_g is not None and payload.weight_g > 500_000:
        result = evaluate_large_weight(weight_g=payload.weight_g)
    elif payload.media_sha256 and payload.current_lot_id:
        result = evaluate_duplicate_media(
            media_sha256=payload.media_sha256,
            current_lot_id=payload.current_lot_id,
            existing_lot_ids=payload.existing_lot_ids or []
        )
    elif payload.has_counterparty_confirmation is not None:
        result = evaluate_handover_completeness(
            has_counterparty_confirmation=bool(payload.has_counterparty_confirmation),
            has_location=bool(payload.has_location),
            has_evidence=bool(payload.has_evidence)
        )
    else:
        result = evaluate_missing_invalid(
            weight_g=payload.weight_g,
            amount_paise=payload.amount_paise,
            rate_paise_per_unit=payload.rate_paise_per_unit
        )

    return EvaluateEntityResponse(
        passed=result.passed,
        rule_id=result.rule_id,
        severity=result.severity.value,
        reason=result.reason,
        details=result.details
    )


# ---------------------------------------------------------
# Admin Overview & Platform Metrics (T029)
# ---------------------------------------------------------

@router.get("/api/v1/admin/overview", response_model=AdminOverviewResponse)
@router.get("/admin/overview", response_model=AdminOverviewResponse)
def get_admin_overview(
    region_id: Optional[str] = Query(None, description="Optional region filter"),
    include_demo: bool = Query(False, description="Whether to include demo transactions and lots"),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Calculate platform-wide overview metrics with real denominators from persisted events (R-ADMIN-06, AT-077).
    Real-impact metrics strictly exclude demo data by default; demo tallies are reported separately.
    """
    now = datetime.now(timezone.utc)

    # Collectors
    collector_q = db.query(Collector).filter(Collector.deleted_at.is_(None))
    if region_id:
        collector_q = collector_q.filter(Collector.region_id == region_id)
    all_collectors = collector_q.all()
    total_collectors = len(all_collectors)

    active_collector_ids = set(
        r[0] for r in db.query(Lot.collector_id).filter(Lot.deleted_at.is_(None)).distinct().all()
    )
    active_in_window = sum(1 for c in all_collectors if c.id in active_collector_ids)

    demo_collector_ids = set(
        r[0] for r in db.query(Lot.collector_id).filter(Lot.deleted_at.is_(None), Lot.is_demo == True).distinct().all()
    )
    demo_collectors = sum(1 for c in all_collectors if c.id in demo_collector_ids)

    # Facilities
    fac_q = db.query(Facility).filter(Facility.deleted_at.is_(None))
    if region_id:
        fac_q = fac_q.filter(Facility.region_id == region_id)
    all_facilities = fac_q.all()
    total_facilities = len(all_facilities)

    verified_fac_ids = set(
        r[0] for r in db.query(FacilityAuthorization.facility_id)
        .filter(FacilityAuthorization.status == "VALID")
        .distinct()
        .all()
    )
    verified_facilities = sum(1 for f in all_facilities if f.id in verified_fac_ids)

    by_kind: Dict[str, int] = {}
    for f in all_facilities:
        by_kind[f.kind] = by_kind.get(f.kind, 0) + 1

    # Lots
    lot_q = db.query(Lot).filter(Lot.deleted_at.is_(None))
    demo_lots_count = db.query(Lot).filter(Lot.deleted_at.is_(None), Lot.is_demo == True).count()
    if not include_demo:
        lot_q = lot_q.filter(Lot.is_demo == False)
    all_lots = lot_q.all()
    total_lots = len(all_lots)

    lots_by_status: Dict[str, int] = {}
    for lot in all_lots:
        lots_by_status[lot.status] = lots_by_status.get(lot.status, 0) + 1

    # Trade
    total_requests = db.query(LotRequest).count()
    total_offers = db.query(Offer).count()
    offers_accepted = db.query(Offer).filter(Offer.status == "ACCEPTED").count()
    acceptance_rate = round(offers_accepted / float(total_offers), 4) if total_offers > 0 else 0.0

    # Handovers
    all_handovers = db.query(Handover).all()
    total_handovers = len(all_handovers)
    confirmed_handovers = sum(1 for h in all_handovers if h.status == "CONFIRMED")
    disputed_handovers = sum(1 for h in all_handovers if h.status == "DISPUTED")

    mass_q = (
        db.query(func.coalesce(func.sum(TermsRevision.measured_weight_g), 0))
        .select_from(Handover)
        .join(Transaction, Handover.transaction_id == Transaction.id)
        .join(TermsRevision, Handover.agreed_terms_revision_id == TermsRevision.id)
        .filter(Handover.status == "CONFIRMED", Transaction.is_demo == False)
    )
    formal_received_mass_g = int(mass_q.scalar() or 0)

    demo_mass_q = (
        db.query(func.coalesce(func.sum(TermsRevision.measured_weight_g), 0))
        .select_from(Handover)
        .join(Transaction, Handover.transaction_id == Transaction.id)
        .join(TermsRevision, Handover.agreed_terms_revision_id == TermsRevision.id)
        .filter(Handover.status == "CONFIRMED", Transaction.is_demo == True)
    )
    demo_mass_g = int(demo_mass_q.scalar() or 0)

    # Financials
    tx_q = db.query(Transaction)
    if not include_demo:
        tx_q = tx_q.filter(Transaction.is_demo == False)
    all_txs = tx_q.all()

    gross_agreed_paise = sum(
        t.agreed_total_paise or t.quoted_total_paise or 0
        for t in all_txs
        if t.lifecycle in {"AGREED", "IN_TRANSIT", "CONFIRMED", "CLOSED"}
    )

    pay_q = db.query(PaymentEntry).join(Transaction, PaymentEntry.transaction_id == Transaction.id)
    if not include_demo:
        pay_q = pay_q.filter(Transaction.is_demo == False)
    all_payments = pay_q.all()

    acknowledged_paid_paise = sum(p.amount_paise for p in all_payments if p.state == "ACKNOWLEDGED")
    disputed_paise = sum(p.amount_paise for p in all_payments if p.state == "DISPUTED")
    outstanding_dues_paise = max(0, gross_agreed_paise - acknowledged_paid_paise)

    # Quality Flags
    total_flags = db.query(QualityFlag).count()
    open_flags = db.query(QualityFlag).filter(QualityFlag.status == "OPEN").count()
    resolved_flags = db.query(QualityFlag).filter(QualityFlag.status.in_(["RESOLVED", "DISMISSED"])).count()

    return AdminOverviewResponse(
        as_of=now.isoformat(),
        last_refresh=now.isoformat(),
        include_demo=include_demo,
        region_id=region_id,
        collectors=CollectorsOverview(
            total_registered=total_collectors,
            active_in_window=active_in_window,
            demo_collectors=demo_collectors
        ),
        facilities=FacilitiesOverview(
            total_facilities=total_facilities,
            verified_facilities=verified_facilities,
            by_kind=by_kind
        ),
        lots=LotsOverview(
            total_lots=total_lots,
            by_status=lots_by_status,
            demo_lots_count=demo_lots_count
        ),
        trade=TradeOverview(
            total_requests=total_requests,
            total_offers=total_offers,
            offers_accepted=offers_accepted,
            acceptance_rate=acceptance_rate
        ),
        handovers=HandoversOverview(
            total_handovers=total_handovers,
            confirmed_count=confirmed_handovers,
            disputed_count=disputed_handovers,
            formal_received_mass_g=formal_received_mass_g,
            demo_mass_g=demo_mass_g,
            mass_label="received, not recycled"
        ),
        financials=FinancialsOverview(
            gross_agreed_paise=gross_agreed_paise,
            acknowledged_paid_paise=acknowledged_paid_paise,
            outstanding_dues_paise=outstanding_dues_paise,
            disputed_paise=disputed_paise
        ),
        quality=QualityOverview(
            total_flags=total_flags,
            open_flags=open_flags,
            resolved_flags=resolved_flags
        ),
        unmet_fieldwork_obligation="UNMET"
    )


@router.get("/api/v1/admin/metrics")
def get_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN))
) -> Dict[str, Any]:
    """Retrieve platform metrics with real denominators from database tables."""
    active_collectors = db.query(Collector.id).join(Lot, Lot.collector_id == Collector.id).distinct().count()
    verified_facilities = (
        db.query(Facility.id)
        .join(FacilityAuthorization, FacilityAuthorization.facility_id == Facility.id)
        .filter(FacilityAuthorization.status == "VALID")
        .distinct()
        .count()
    )
    recorded_transactions = db.query(Transaction).filter(Transaction.is_demo == False).count()
    return {
        "active_collectors": active_collectors,
        "verified_facilities": verified_facilities,
        "recorded_transactions": recorded_transactions,
        "unmet_fieldwork_obligation": "UNMET"
    }


# ---------------------------------------------------------
# Collector Minimal Directory (R-ADMIN-04)
# ---------------------------------------------------------

@router.get("/api/v1/admin/collectors", response_model=List[CollectorMinimalResponse])
@router.get("/admin/collectors", response_model=List[CollectorMinimalResponse])
def list_collectors_minimal(
    region_id: Optional[str] = Query(None, description="Filter by region ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Minimal collector profiles for administrative review (R-ADMIN-04).
    Audits access and strictly excludes private phone/PIN/token credentials.
    """
    stmt = select(Collector).where(Collector.deleted_at.is_(None))
    if region_id:
        stmt = stmt.where(Collector.region_id == region_id)
    stmt = stmt.order_by(Collector.created_at.desc()).offset(offset).limit(limit)
    collectors = db.execute(stmt).scalars().all()

    # Sensitive access audit (R-ADMIN-04)
    record_admin_event(
        db=db,
        aggregate_type="COLLECTOR_DIRECTORY",
        aggregate_id=ADMIN_UUID_NAMESPACE,
        event_type="COLLECTOR_DIRECTORY_ACCESSED",
        actor_id=current_user.id,
        role=current_user.role,
        payload={"region_id": region_id, "limit": limit, "offset": offset, "result_count": len(collectors)}
    )
    db.commit()

    results = []
    for c in collectors:
        lot_count = db.query(Lot).filter(Lot.collector_id == c.id, Lot.deleted_at.is_(None)).count()
        active_lot_count = db.query(Lot).filter(
            Lot.collector_id == c.id,
            Lot.deleted_at.is_(None),
            Lot.status.in_(["LISTED", "ACCEPTED", "HANDED_OVER"])
        ).count()
        results.append(
            CollectorMinimalResponse(
                id=c.id,
                display_alias=c.display_alias,
                preferred_language=c.preferred_language,
                general_area=c.general_area,
                region_id=c.region_id,
                created_at=c.created_at.isoformat(),
                lot_count=lot_count,
                active_lot_count=active_lot_count
            )
        )
    return results


# ---------------------------------------------------------
# Material & Taxonomy Maintenance (R-ADMIN-03, AT-064)
# ---------------------------------------------------------

@router.get("/api/v1/admin/materials", response_model=List[AdminMaterialResponse])
@router.get("/admin/materials", response_model=List[AdminMaterialResponse])
def list_admin_materials(
    category_id: Optional[str] = Query(None),
    active_only: bool = Query(False),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """List all materials with category and alias counts for administration."""
    stmt = select(Material)
    if category_id:
        stmt = stmt.where(Material.category_id == category_id)
    if active_only:
        stmt = stmt.where(Material.active == True)
    stmt = stmt.order_by(Material.id.asc())
    materials = db.execute(stmt).scalars().all()

    results = []
    for m in materials:
        alias_count = db.query(MaterialAlias).filter(MaterialAlias.material_id == m.id).count()
        results.append(
            AdminMaterialResponse(
                id=m.id,
                category_id=m.category_id,
                subcategory_code=m.subcategory_code,
                description_key=m.description_key,
                allowed_units=m.allowed_units,
                default_route=m.default_route,
                route_requires_context=m.route_requires_context,
                condition_options=m.condition_options or [],
                safety_guide_ids=m.safety_guide_ids or [],
                active=m.active,
                alias_count=alias_count,
                created_at=m.created_at.isoformat(),
                updated_at=m.updated_at.isoformat()
            )
        )
    return results


@router.post("/api/v1/admin/materials", response_model=AdminMaterialResponse, status_code=status.HTTP_201_CREATED)
@router.post("/admin/materials", response_model=AdminMaterialResponse, status_code=status.HTTP_201_CREATED)
def create_admin_material(
    payload: AdminMaterialCreateRequest,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Create a new material in the catalog with explicit validation (R-ADMIN-03)."""
    existing = db.execute(select(Material).where(Material.id == payload.id)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Material with ID '{payload.id}' already exists."
        )

    cat = db.execute(select(MaterialCategory).where(MaterialCategory.id == payload.category_id)).scalar_one_or_none()
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Material category '{payload.category_id}' does not exist."
        )

    valid_routes = {"GENERAL_RECYCLING", "AUTHORIZED_EWASTE", "BATTERY_ISOLATION", "HAZARDOUS_DISPOSAL"}
    if payload.default_route not in valid_routes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid default_route '{payload.default_route}'. Must be one of {valid_routes}."
        )

    now = datetime.now(timezone.utc)
    m = Material(
        id=payload.id,
        category_id=payload.category_id,
        subcategory_code=payload.subcategory_code,
        description_key=payload.description_key,
        allowed_units=payload.allowed_units,
        default_route=payload.default_route,
        route_requires_context=payload.route_requires_context,
        condition_options=payload.condition_options or [],
        safety_guide_ids=payload.safety_guide_ids or [],
        active=True,
        created_at=now,
        updated_at=now
    )
    db.add(m)

    mat_uuid = uuid.uuid5(ADMIN_UUID_NAMESPACE, m.id)
    record_admin_event(
        db=db,
        aggregate_type="MATERIAL",
        aggregate_id=mat_uuid,
        event_type="MATERIAL_CREATED",
        actor_id=current_user.id,
        role=current_user.role,
        payload={"material_id": m.id, "category_id": m.category_id, "default_route": m.default_route}
    )
    db.commit()
    db.refresh(m)

    return AdminMaterialResponse(
        id=m.id,
        category_id=m.category_id,
        subcategory_code=m.subcategory_code,
        description_key=m.description_key,
        allowed_units=m.allowed_units,
        default_route=m.default_route,
        route_requires_context=m.route_requires_context,
        condition_options=m.condition_options or [],
        safety_guide_ids=m.safety_guide_ids or [],
        active=m.active,
        alias_count=0,
        created_at=m.created_at.isoformat(),
        updated_at=m.updated_at.isoformat()
    )


@router.patch("/api/v1/admin/materials/{material_id}", response_model=AdminMaterialResponse)
@router.patch("/admin/materials/{material_id}", response_model=AdminMaterialResponse)
def update_admin_material(
    material_id: str,
    payload: AdminMaterialUpdateRequest,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Update or deactivate material while strictly retaining historical references (AT-064).
    """
    m = db.execute(select(Material).where(Material.id == material_id)).scalar_one_or_none()
    if not m:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material '{material_id}' not found."
        )

    now = datetime.now(timezone.utc)
    changes: Dict[str, Any] = {}
    if payload.description_key is not None:
        m.description_key = payload.description_key
        changes["description_key"] = payload.description_key
    if payload.active is not None:
        m.active = payload.active
        changes["active"] = payload.active
    if payload.default_route is not None:
        valid_routes = {"GENERAL_RECYCLING", "AUTHORIZED_EWASTE", "BATTERY_ISOLATION", "HAZARDOUS_DISPOSAL"}
        if payload.default_route not in valid_routes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid default_route '{payload.default_route}'."
            )
        m.default_route = payload.default_route
        changes["default_route"] = payload.default_route
    if payload.route_requires_context is not None:
        m.route_requires_context = payload.route_requires_context
        changes["route_requires_context"] = payload.route_requires_context
    if payload.condition_options is not None:
        m.condition_options = payload.condition_options
        changes["condition_options"] = payload.condition_options
    if payload.safety_guide_ids is not None:
        m.safety_guide_ids = payload.safety_guide_ids
        changes["safety_guide_ids"] = payload.safety_guide_ids

    m.updated_at = now

    mat_uuid = uuid.uuid5(ADMIN_UUID_NAMESPACE, m.id)
    record_admin_event(
        db=db,
        aggregate_type="MATERIAL",
        aggregate_id=mat_uuid,
        event_type="MATERIAL_UPDATED",
        actor_id=current_user.id,
        role=current_user.role,
        payload={"material_id": m.id, "changes": changes}
    )
    db.commit()
    db.refresh(m)

    alias_count = db.query(MaterialAlias).filter(MaterialAlias.material_id == m.id).count()
    return AdminMaterialResponse(
        id=m.id,
        category_id=m.category_id,
        subcategory_code=m.subcategory_code,
        description_key=m.description_key,
        allowed_units=m.allowed_units,
        default_route=m.default_route,
        route_requires_context=m.route_requires_context,
        condition_options=m.condition_options or [],
        safety_guide_ids=m.safety_guide_ids or [],
        active=m.active,
        alias_count=alias_count,
        created_at=m.created_at.isoformat(),
        updated_at=m.updated_at.isoformat()
    )


# ---------------------------------------------------------
# Material Alias Maintenance
# ---------------------------------------------------------

@router.post("/api/v1/admin/material-aliases", response_model=AdminMaterialAliasResponse, status_code=status.HTTP_201_CREATED)
@router.post("/admin/material-aliases", response_model=AdminMaterialAliasResponse, status_code=status.HTTP_201_CREATED)
def create_material_alias(
    payload: AdminMaterialAliasCreateRequest,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Add a colloquial material alias with normalization and ambiguity validation (R-ADMIN-03)."""
    mat = db.execute(select(Material).where(Material.id == payload.material_id)).scalar_one_or_none()
    if not mat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material '{payload.material_id}' not found."
        )

    if payload.language not in {"en", "hi", "mr"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Language must be one of 'en', 'hi', 'mr'."
        )

    norm_term = normalize_term(payload.local_term)
    if not norm_term:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Local term produces an empty normalized term."
        )

    existing = db.execute(
        select(MaterialAlias).where(
            MaterialAlias.material_id == payload.material_id,
            MaterialAlias.language == payload.language,
            MaterialAlias.normalized_term == norm_term
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Alias '{norm_term}' for material '{payload.material_id}' ({payload.language}) already exists."
        )

    alias = MaterialAlias(
        id=uuid.uuid4(),
        material_id=payload.material_id,
        language=payload.language,
        local_term=payload.local_term.strip(),
        normalized_term=norm_term
    )
    db.add(alias)

    mat_uuid = uuid.uuid5(ADMIN_UUID_NAMESPACE, payload.material_id)
    record_admin_event(
        db=db,
        aggregate_type="MATERIAL",
        aggregate_id=mat_uuid,
        event_type="MATERIAL_ALIAS_CREATED",
        actor_id=current_user.id,
        role=current_user.role,
        payload={"alias_id": str(alias.id), "material_id": alias.material_id, "language": alias.language, "term": norm_term}
    )
    db.commit()
    db.refresh(alias)

    return AdminMaterialAliasResponse(
        id=alias.id,
        material_id=alias.material_id,
        language=alias.language,
        local_term=alias.local_term,
        normalized_term=alias.normalized_term
    )


@router.delete("/api/v1/admin/material-aliases/{alias_id}")
@router.delete("/admin/material-aliases/{alias_id}")
def delete_material_alias(
    alias_id: uuid.UUID,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Delete a material alias with audit event logging."""
    alias = db.execute(select(MaterialAlias).where(MaterialAlias.id == alias_id)).scalar_one_or_none()
    if not alias:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material alias '{alias_id}' not found."
        )

    mat_uuid = uuid.uuid5(ADMIN_UUID_NAMESPACE, alias.material_id)
    record_admin_event(
        db=db,
        aggregate_type="MATERIAL",
        aggregate_id=mat_uuid,
        event_type="MATERIAL_ALIAS_DELETED",
        actor_id=current_user.id,
        role=current_user.role,
        payload={"alias_id": str(alias.id), "material_id": alias.material_id, "term": alias.normalized_term}
    )
    db.delete(alias)
    db.commit()
    return {"status": "deleted", "alias_id": str(alias_id)}


# ---------------------------------------------------------
# Safety Guide Maintenance (R-ADMIN-03)
# ---------------------------------------------------------

@router.get("/api/v1/admin/safety-guides", response_model=List[AdminSafetyGuideResponse])
@router.get("/admin/safety-guides", response_model=List[AdminSafetyGuideResponse])
def list_admin_safety_guides(
    review_status: Optional[str] = Query(None),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """List safety guides with review status filtering."""
    stmt = select(SafetyGuide)
    if review_status:
        stmt = stmt.where(SafetyGuide.review_status == review_status.upper())
    stmt = stmt.order_by(SafetyGuide.id.asc())
    guides = db.execute(stmt).scalars().all()
    return [
        AdminSafetyGuideResponse(
            id=g.id,
            material_ids=g.material_ids or [],
            route=g.route,
            text_key=g.text_key,
            icon_asset_ref=g.icon_asset_ref,
            image_asset_ref=g.image_asset_ref,
            audio_keys=g.audio_keys or {},
            source_ids=g.source_ids or [],
            version=g.version,
            review_status=g.review_status
        )
        for g in guides
    ]


@router.post("/api/v1/admin/safety-guides", response_model=AdminSafetyGuideResponse, status_code=status.HTTP_201_CREATED)
@router.post("/admin/safety-guides", response_model=AdminSafetyGuideResponse, status_code=status.HTTP_201_CREATED)
def create_admin_safety_guide(
    payload: AdminSafetyGuideCreateRequest,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Create a new contextual safety guide with version tracking (R-ADMIN-03)."""
    existing = db.execute(select(SafetyGuide).where(SafetyGuide.id == payload.id)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Safety guide with ID '{payload.id}' already exists."
        )

    g = SafetyGuide(
        id=payload.id,
        material_ids=payload.material_ids,
        route=payload.route,
        text_key=payload.text_key,
        icon_asset_ref=payload.icon_asset_ref,
        image_asset_ref=payload.image_asset_ref,
        audio_keys=payload.audio_keys or {},
        source_ids=payload.source_ids or [],
        version=payload.version,
        review_status=payload.review_status.upper()
    )
    db.add(g)

    guide_uuid = uuid.uuid5(ADMIN_UUID_NAMESPACE, g.id)
    record_admin_event(
        db=db,
        aggregate_type="SAFETY_GUIDE",
        aggregate_id=guide_uuid,
        event_type="SAFETY_GUIDE_CREATED",
        actor_id=current_user.id,
        role=current_user.role,
        payload={"guide_id": g.id, "route": g.route, "version": g.version}
    )
    db.commit()
    db.refresh(g)

    return AdminSafetyGuideResponse(
        id=g.id,
        material_ids=g.material_ids,
        route=g.route,
        text_key=g.text_key,
        icon_asset_ref=g.icon_asset_ref,
        image_asset_ref=g.image_asset_ref,
        audio_keys=g.audio_keys or {},
        source_ids=g.source_ids or [],
        version=g.version,
        review_status=g.review_status
    )


@router.patch("/api/v1/admin/safety-guides/{guide_id}", response_model=AdminSafetyGuideResponse)
@router.patch("/admin/safety-guides/{guide_id}", response_model=AdminSafetyGuideResponse)
def update_admin_safety_guide(
    guide_id: str,
    payload: AdminSafetyGuideUpdateRequest,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """Update safety guide review status, content keys, or version."""
    g = db.execute(select(SafetyGuide).where(SafetyGuide.id == guide_id)).scalar_one_or_none()
    if not g:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Safety guide '{guide_id}' not found."
        )

    changes: Dict[str, Any] = {}
    if payload.route is not None:
        g.route = payload.route
        changes["route"] = payload.route
    if payload.text_key is not None:
        g.text_key = payload.text_key
        changes["text_key"] = payload.text_key
    if payload.icon_asset_ref is not None:
        g.icon_asset_ref = payload.icon_asset_ref
        changes["icon_asset_ref"] = payload.icon_asset_ref
    if payload.image_asset_ref is not None:
        g.image_asset_ref = payload.image_asset_ref
        changes["image_asset_ref"] = payload.image_asset_ref
    if payload.audio_keys is not None:
        g.audio_keys = payload.audio_keys
        changes["audio_keys"] = payload.audio_keys
    if payload.source_ids is not None:
        g.source_ids = payload.source_ids
        changes["source_ids"] = payload.source_ids
    if payload.version is not None:
        g.version = payload.version
        changes["version"] = payload.version
    if payload.review_status is not None:
        g.review_status = payload.review_status.upper()
        changes["review_status"] = g.review_status

    guide_uuid = uuid.uuid5(ADMIN_UUID_NAMESPACE, g.id)
    record_admin_event(
        db=db,
        aggregate_type="SAFETY_GUIDE",
        aggregate_id=guide_uuid,
        event_type="SAFETY_GUIDE_UPDATED",
        actor_id=current_user.id,
        role=current_user.role,
        payload={"guide_id": g.id, "changes": changes}
    )
    db.commit()
    db.refresh(g)

    return AdminSafetyGuideResponse(
        id=g.id,
        material_ids=g.material_ids or [],
        route=g.route,
        text_key=g.text_key,
        icon_asset_ref=g.icon_asset_ref,
        image_asset_ref=g.image_asset_ref,
        audio_keys=g.audio_keys or {},
        source_ids=g.source_ids or [],
        version=g.version,
        review_status=g.review_status
    )


# ---------------------------------------------------------
# Facility Verification Review (R-ADMIN-01, AT-064)
# ---------------------------------------------------------

@router.post("/api/v1/admin/facilities/{facility_id}/verification", response_model=AdminFacilityVerificationResponse, status_code=status.HTTP_201_CREATED)
@router.post("/admin/facilities/{facility_id}/verification", response_model=AdminFacilityVerificationResponse, status_code=status.HTTP_201_CREATED)
def assert_facility_verification(
    facility_id: uuid.UUID,
    payload: AdminFacilityVerificationRequest,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Admin records verified authorization evidence for a facility (R-ADMIN-01 / AT-064).
    Enforces that ordinary recyclers cannot approve themselves.
    Creates an auditable FacilityAuthorization record rather than an arbitrary badge.
    """
    facility = db.execute(select(Facility).where(Facility.id == facility_id, Facility.deleted_at.is_(None))).scalar_one_or_none()
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Facility '{facility_id}' not found."
        )

    if not payload.reason or len(payload.reason.strip()) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A justification reason (at least 5 characters) is required to assert verification."
        )

    now = datetime.now(timezone.utc)
    auth_entry = FacilityAuthorization(
        id=uuid.uuid4(),
        facility_id=facility_id,
        route=payload.route,
        authority=payload.authority,
        reference=payload.reference,
        status=payload.status.upper(),
        verification_level=payload.verification_level.upper(),
        valid_from=payload.valid_from,
        valid_until=payload.valid_until,
        source_id=payload.source_id,
        scope_notes=payload.scope_notes,
        reviewer_id=current_user.id,
        last_verified_at=now
    )
    db.add(auth_entry)

    record_admin_event(
        db=db,
        aggregate_type="FACILITY",
        aggregate_id=facility_id,
        event_type="FACILITY_VERIFICATION_ASSERTED",
        actor_id=current_user.id,
        role=current_user.role,
        payload={
            "authorization_id": str(auth_entry.id),
            "facility_id": str(facility_id),
            "route": auth_entry.route,
            "authority": auth_entry.authority,
            "reference": auth_entry.reference,
            "status": auth_entry.status,
            "verification_level": auth_entry.verification_level,
            "reason": payload.reason.strip()
        }
    )
    db.commit()
    db.refresh(auth_entry)

    return AdminFacilityVerificationResponse(
        id=auth_entry.id,
        facility_id=auth_entry.facility_id,
        route=auth_entry.route,
        authority=auth_entry.authority,
        reference=auth_entry.reference,
        status=auth_entry.status,
        verification_level=auth_entry.verification_level,
        valid_from=auth_entry.valid_from.isoformat() if auth_entry.valid_from else None,
        valid_until=auth_entry.valid_until.isoformat() if auth_entry.valid_until else None,
        reviewer_id=auth_entry.reviewer_id,
        last_verified_at=auth_entry.last_verified_at.isoformat(),
        scope_notes=auth_entry.scope_notes,
        reason=payload.reason.strip()
    )


# ---------------------------------------------------------
# Audit Trail Search & Traceability (R-ADMIN-05, AT-077)
# ---------------------------------------------------------

@router.get("/api/v1/admin/events", response_model=List[DomainEventResponse])
@router.get("/admin/events", response_model=List[DomainEventResponse])
def search_domain_events(
    aggregate_type: Optional[str] = Query(None, description="Aggregate type: LOT, TRANSACTION, HANDOVER, PAYMENT, etc."),
    aggregate_id: Optional[uuid.UUID] = Query(None, description="Filter by aggregate UUID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    actor_id: Optional[uuid.UUID] = Query(None, description="Filter by actor user UUID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Search immutable append-only domain event log with hash integrity data (R-ADMIN-05).
    """
    stmt = select(DomainEvent)
    if aggregate_type:
        stmt = stmt.where(DomainEvent.aggregate_type == aggregate_type.upper())
    if aggregate_id:
        stmt = stmt.where(DomainEvent.aggregate_id == aggregate_id)
    if event_type:
        stmt = stmt.where(DomainEvent.event_type == event_type)
    if actor_id:
        stmt = stmt.where(DomainEvent.actor_id == actor_id)

    stmt = stmt.order_by(DomainEvent.received_at_server.desc()).offset(offset).limit(limit)
    events = db.execute(stmt).scalars().all()

    return [
        DomainEventResponse(
            id=e.id,
            aggregate_type=e.aggregate_type,
            aggregate_id=e.aggregate_id,
            sequence=e.sequence,
            event_type=e.event_type,
            actor_id=e.actor_id,
            role=e.role,
            occurred_at=e.received_at_server.isoformat(),
            payload_json=e.payload_json or {},
            prev_hash=e.prev_hash,
            event_hash=e.event_hash
        )
        for e in events
    ]


@router.get("/api/v1/admin/traceability/{lot_id}", response_model=TraceabilityReportResponse)
@router.get("/admin/traceability/{lot_id}", response_model=TraceabilityReportResponse)
def get_lot_traceability(
    lot_id: uuid.UUID,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Complete audit timeline and cryptographic hash chain verification for a lot (AT-077).
    Traces from creation through offers, agreements, handovers, payments, and quality reviews.
    """
    lot = db.execute(select(Lot).where(Lot.id == lot_id)).scalar_one_or_none()
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lot '{lot_id}' not found."
        )

    # Direct lot events
    direct_events = db.execute(
        select(DomainEvent)
        .where(DomainEvent.aggregate_id == lot_id)
        .order_by(DomainEvent.sequence.asc())
    ).scalars().all()

    # Verify hash chain continuity on direct lot events
    is_valid = True
    for i in range(len(direct_events)):
        if i == 0:
            if direct_events[i].prev_hash != "GENESIS":
                is_valid = False
        else:
            if direct_events[i].prev_hash != direct_events[i - 1].event_hash:
                is_valid = False

    # Related events where payload contains lot_id
    lot_str = str(lot_id)
    related_events = db.execute(
        select(DomainEvent)
        .where(
            DomainEvent.aggregate_id != lot_id,
            func.cast(DomainEvent.payload_json, String).contains(lot_str)
        )
        .order_by(DomainEvent.received_at_server.asc())
    ).scalars().all()

    all_timeline = sorted(
        direct_events + related_events,
        key=lambda e: (e.received_at_server, e.sequence)
    )

    return TraceabilityReportResponse(
        lot_id=lot_id,
        lot_status=lot.status,
        material_id=lot.material_id,
        events_count=len(all_timeline),
        is_hash_chain_valid=is_valid,
        events=[
            DomainEventResponse(
                id=e.id,
                aggregate_type=e.aggregate_type,
                aggregate_id=e.aggregate_id,
                sequence=e.sequence,
                event_type=e.event_type,
                actor_id=e.actor_id,
                role=e.role,
                occurred_at=e.received_at_server.isoformat(),
                payload_json=e.payload_json or {},
                prev_hash=e.prev_hash,
                event_hash=e.event_hash
            )
            for e in all_timeline
        ]
    )


# ---------------------------------------------------------
# Price Moderation Endpoints (R-PRICE-05, AT-064)
# ---------------------------------------------------------

@router.get("/api/v1/admin/price-review", response_model=List[PriceReviewItemResponse])
@router.get("/admin/price-review", response_model=List[PriceReviewItemResponse])
def list_pending_price_reviews(
    review_status: str = Query("PENDING_REVIEW", description="Status filter (PENDING_REVIEW, REJECTED, VERIFIED)"),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    """List price observations pending admin moderation or quarantine review."""
    stmt = select(PriceObservation).where(PriceObservation.review_status == review_status).order_by(PriceObservation.created_at.desc())
    rows = db.execute(stmt).scalars().all()
    return [
        PriceReviewItemResponse(
            id=r.id,
            material_id=r.material_id,
            region_id=r.region_id,
            rate_paise_per_unit=r.rate_paise_per_unit,
            unit=r.unit,
            price_kind=r.price_kind,
            observed_at=r.observed_at.isoformat(),
            source_id=r.source_id,
            review_status=r.review_status,
            is_demo=r.is_demo,
        )
        for r in rows
    ]


@router.post("/api/v1/admin/price-review/{observation_id}/decision")
@router.post("/admin/price-review/{observation_id}/decision")
def decide_price_review(
    observation_id: uuid.UUID,
    payload: PriceReviewDecisionRequest,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Approve or reject a pending price observation with justification (AT-064)."""
    obs = db.execute(select(PriceObservation).where(PriceObservation.id == observation_id)).scalar_one_or_none()
    if not obs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Price observation '{observation_id}' not found"
        )

    decision = payload.decision.upper()
    if decision == "APPROVE":
        obs.review_status = "VERIFIED"
        obs.rejection_reason = None
    elif decision == "REJECT":
        obs.review_status = "REJECTED"
        obs.rejection_reason = payload.reason or "Rejected by administrator review"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="decision must be 'APPROVE' or 'REJECT'"
        )

    db.commit()
    db.refresh(obs)

    return {
        "status": "updated",
        "observation_id": str(obs.id),
        "review_status": obs.review_status,
        "reason": obs.rejection_reason
    }

