"""Material Lots and Lifecycle Router.
Implements T016: lot creation, updates, collection, listing, cancellation,
ownership and role scoping, positive integer gram weight constraints,
prohibition of direct arbitrary status PATCH, location provenance, photo attachments,
append-only domain events, and valuation estimation.
Specifications: docs/06_SCHEMA.md, docs/04_APPFLOW.md, docs/16_API_CONTRACT.md.
Requirements: R-LOT-03, R-LOT-04, R-LOT-05, R-DATA-01.
Acceptance cases: AT-013, AT-014, AT-015, AT-053.
"""
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from geoalchemy2.elements import WKTElement
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import desc, select, func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.audit import DomainEvent, QualityFlag, SyncChange
from app.db.models.auth import User
from app.db.models.facility import (
    Facility,
    FacilityAuthorization,
    FacilityMaterial,
    FacilityOperation,
    FacilityRate,
)
from app.db.models.trade import Transaction
from app.db.models.lot import (
    Classification,
    LocationRecord,
    Lot,
    LotImage,
    MediaObject,
    ValuationSnapshot,
)
from app.db.models.material import Material
from app.db.models.price import PriceSummary
from app.domain.canonical import compute_canonical_hash
from app.domain.matching import (
    CandidateFacility,
    LotContext,
    MatchResult,
    MatchedFacility,
    match_lot_to_facilities,
    extract_coordinates,
    STATUTORY_DISCLAIMER,
)
from app.security import get_current_user

router = APIRouter(prefix="/api/v1/lots", tags=["lots"])

ALLOWED_CONDITIONS = {"INTACT", "PARTIAL", "DISASSEMBLED", "SCRAP", "MIXED", "UNKNOWN"}
ALLOWED_ROUTES = {
    "GENERAL_RECYCLING",
    "AUTHORIZED_EWASTE",
    "BATTERY_ISOLATION",
    "HAZARDOUS_DISPOSAL",
}
MAX_ALLOWED_WEIGHT_GRAMS = 50_000_000  # 50 metric tonnes
LARGE_WEIGHT_THRESHOLD_GRAMS = 500_000  # 500 kg anomaly review threshold


# --- Schemas ---

class LocationInput(BaseModel):
    source: str = Field("GPS", description="GPS, MANUAL, REGION, MISSING")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy_m: Optional[float] = None
    age_ms: Optional[int] = None
    coarse_area: Optional[str] = None
    consent_version: Optional[str] = "v1.0"


class LocationSummary(BaseModel):
    source: str
    coarse_area: Optional[str] = None
    accuracy_m: Optional[float] = None
    age_ms: Optional[int] = None
    captured_at: Optional[datetime] = None


class CreateLotRequest(BaseModel):
    id: Optional[uuid.UUID] = None
    collector_id: Optional[uuid.UUID] = None
    material_id: Optional[str] = None
    material_context: Optional[str] = None
    regulatory_route: Optional[str] = None
    estimated_weight_g: Optional[int] = Field(None, gt=0, le=MAX_ALLOWED_WEIGHT_GRAMS)
    estimated_weight_kg: Optional[float] = Field(None, gt=0)
    condition: Optional[str] = None
    description: Optional[str] = None
    location: Optional[LocationInput] = None
    media_ids: Optional[List[uuid.UUID]] = Field(default_factory=list)
    is_demo: Optional[bool] = None

    @model_validator(mode="before")
    @classmethod
    def round_trip_weight(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Round-trip fractional kg to integer grams
            if data.get("estimated_weight_kg") is not None and data.get("estimated_weight_g") is None:
                kg_val = float(data["estimated_weight_kg"])
                data["estimated_weight_g"] = int(round(kg_val * 1000))
        return data


class UpdateLotRequest(BaseModel):
    expected_version: int
    estimated_weight_g: Optional[int] = Field(None, gt=0, le=MAX_ALLOWED_WEIGHT_GRAMS)
    estimated_weight_kg: Optional[float] = Field(None, gt=0)
    condition: Optional[str] = None
    description: Optional[str] = None
    material_id: Optional[str] = None
    material_context: Optional[str] = None
    regulatory_route: Optional[str] = None
    location: Optional[LocationInput] = None
    media_ids: Optional[List[uuid.UUID]] = None

    @model_validator(mode="before")
    @classmethod
    def round_trip_weight(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if data.get("estimated_weight_kg") is not None and data.get("estimated_weight_g") is None:
                kg_val = float(data["estimated_weight_kg"])
                data["estimated_weight_g"] = int(round(kg_val * 1000))
        return data


class CollectLotRequest(BaseModel):
    expected_version: int
    location: Optional[LocationInput] = None


class ListLotRequest(BaseModel):
    expected_version: int
    directed_facility_id: Optional[uuid.UUID] = None


class CancelLotRequest(BaseModel):
    expected_version: int
    reason: str = Field(..., min_length=3, description="Cancellation reason")


class LotImageSummary(BaseModel):
    media_id: uuid.UUID
    purpose: str
    order_index: int
    captured_at: Optional[datetime] = None


class DomainEventSummary(BaseModel):
    sequence: int
    event_type: str
    actor_id: uuid.UUID
    role: str
    previous_state: Optional[str] = None
    next_state: Optional[str] = None
    received_at_server: datetime


class QualityFlagSummary(BaseModel):
    rule_id: str
    severity: str
    status: str


class LotResponse(BaseModel):
    id: uuid.UUID
    collector_id: uuid.UUID
    material_id: Optional[str] = None
    material_context: Optional[str] = None
    regulatory_route: Optional[str] = None
    estimated_weight_g: Optional[int] = None
    condition: Optional[str] = None
    description: Optional[str] = None
    status: str
    version: int
    is_demo: bool
    created_at: datetime
    updated_at: datetime


class LotDetailResponse(LotResponse):
    collection_location_id: Optional[uuid.UUID] = None
    collected_at: Optional[datetime] = None
    location: Optional[LocationSummary] = None
    images: List[LotImageSummary] = Field(default_factory=list)
    events: List[DomainEventSummary] = Field(default_factory=list)
    quality_flags: List[QualityFlagSummary] = Field(default_factory=list)


class ValuationEstimateResponse(BaseModel):
    lot_id: uuid.UUID
    policy_version: str
    currency: str
    input_weight_g: int
    condition: str
    low_total_paise: Optional[int] = None
    median_total_paise: Optional[int] = None
    high_total_paise: Optional[int] = None
    confidence: str
    disclaimer: str


# --- Helper Functions ---

def record_domain_event(
    db: Session,
    lot: Lot,
    event_type: str,
    actor_id: uuid.UUID,
    role: str,
    previous_state: Optional[str],
    next_state: Optional[str],
    payload: Dict[str, Any]
) -> DomainEvent:
    last_event = db.execute(
        select(DomainEvent)
        .where(DomainEvent.aggregate_id == lot.id)
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
        aggregate_type="LOT",
        aggregate_id=lot.id,
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


def attach_or_update_location(
    db: Session,
    lot_id: uuid.UUID,
    loc_input: LocationInput
) -> LocationRecord:
    """Create a verified location record with coarse privacy protection."""
    now = datetime.now(timezone.utc)
    point_geom = None
    coarse = loc_input.coarse_area

    if loc_input.source == "GPS" and loc_input.latitude is not None and loc_input.longitude is not None:
        # Validate India bounding coordinates
        lat, lon = loc_input.latitude, loc_input.longitude
        if not (8.0 <= lat <= 37.0 and 68.0 <= lon <= 97.0):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"GPS coordinates ({lat}, {lon}) are outside India bounding territory."
            )
        point_geom = WKTElement(f"POINT({lon} {lat})", srid=4326)
        if not coarse:
            coarse = f"GPS location (accuracy: {loc_input.accuracy_m or 'unknown'}m)"
    elif not coarse:
        coarse = "Coarse municipal area"

    loc_record = LocationRecord(
        owner_entity_id=lot_id,
        point=point_geom,
        coarse_area=coarse,
        accuracy_m=loc_input.accuracy_m,
        source=loc_input.source,
        captured_at=now,
        age_ms=loc_input.age_ms,
        consent_version=loc_input.consent_version or "v1.0"
    )
    db.add(loc_record)
    db.flush()
    return loc_record


# --- Endpoints ---

@router.post("", response_model=LotResponse, status_code=status.HTTP_201_CREATED)
def create_lot(
    payload: CreateLotRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or stage a new material lot in DRAFT status with owner checks and validation."""
    effective_collector_id = payload.collector_id or current_user.id
    if effective_collector_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cannot create lot on behalf of another collector."
        )

    mat_route = payload.regulatory_route
    if payload.material_id:
        material = db.execute(select(Material).where(Material.id == payload.material_id)).scalar_one_or_none()
        if not material:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Material ID '{payload.material_id}' not found in curated catalog."
            )
        if not mat_route:
            mat_route = material.default_route

    lot_id = payload.id or uuid.uuid4()

    # Idempotent check
    existing_lot = db.execute(select(Lot).where(Lot.id == lot_id)).scalar_one_or_none()
    if existing_lot:
        return existing_lot

    now = datetime.now(timezone.utc)
    is_demo = payload.is_demo if payload.is_demo is not None else current_user.is_demo

    lot = Lot(
        id=lot_id,
        collector_id=effective_collector_id,
        material_id=payload.material_id,
        material_context=payload.material_context,
        regulatory_route=mat_route,
        estimated_weight_g=payload.estimated_weight_g,
        condition=payload.condition,
        description=payload.description,
        status="DRAFT",
        version=1,
        origin_class="PLATFORM_GENERATED",
        source_kind="PLATFORM_OBSERVATION",
        is_demo=is_demo,
        created_at=now,
        updated_at=now,
    )
    db.add(lot)

    # Attach location if provided
    if payload.location:
        loc = attach_or_update_location(db, lot_id, payload.location)
        lot.collection_location_id = loc.id

    # Attach images if provided
    if payload.media_ids:
        for idx, media_id in enumerate(payload.media_ids):
            db.add(LotImage(
                lot_id=lot.id,
                media_id=media_id,
                order_index=idx,
                purpose="PHOTO",
                captured_at=now
            ))
            # Check duplicate media across active lots under QUALITY_V1
            existing_lots = (
                db.query(LotImage.lot_id)
                .join(Lot, Lot.id == LotImage.lot_id)
                .filter(
                    LotImage.media_id == media_id,
                    LotImage.lot_id != lot.id,
                    Lot.status.notin_(["CANCELLED", "CLOSED"])
                )
                .distinct()
                .all()
            )
            if existing_lots:
                other_ids = [str(r[0]) for r in existing_lots]
                db.add(QualityFlag(
                    id=uuid.uuid4(),
                    entity_type="LOT",
                    entity_id=lot.id,
                    entity_version=1,
                    rule_id="DQ-DUPLICATE-MEDIA",
                    policy_version="QUALITY_V1",
                    severity="MEDIUM",
                    evidence_json={
                        "media_id": str(media_id),
                        "other_lot_ids": other_ids
                    },
                    reason=(
                        f"Media {media_id} previously referenced in {len(other_ids)} "
                        f"distinct active lot(s); review recommended (not proof of duplicate material or fraud)."
                    ),
                    status="OPEN",
                    created_at=now,
                    updated_at=now
                ))

    # Flag suspicious large weight for review without rejecting arbitrarily
    if payload.estimated_weight_g and payload.estimated_weight_g > LARGE_WEIGHT_THRESHOLD_GRAMS:
        db.add(QualityFlag(
            id=uuid.uuid4(),
            entity_type="LOT",
            entity_id=lot.id,
            entity_version=1,
            rule_id="LARGE_WEIGHT_ANOMALY",
            policy_version="QUALITY_V1",
            severity="MEDIUM",
            evidence_json={
                "estimated_weight_g": payload.estimated_weight_g,
                "threshold_g": LARGE_WEIGHT_THRESHOLD_GRAMS
            },
            reason=f"Large weight anomaly: {payload.estimated_weight_g}g exceeds 500kg threshold; flagged for review without artificial rejection.",
            status="OPEN",
            created_at=now,
            updated_at=now
        ))

    # Record append-only lifecycle event
    record_domain_event(
        db=db,
        lot=lot,
        event_type="LOT_CREATED",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state=None,
        next_state="DRAFT",
        payload={
            "material_id": payload.material_id,
            "estimated_weight_g": payload.estimated_weight_g,
            "condition": payload.condition
        }
    )

    # Record sync change delta
    db.add(SyncChange(
        entity_type="LOT",
        entity_id=lot.id,
        entity_version=1,
        visibility_scope=f"collector:{effective_collector_id}",
        created_at=now
    ))

    db.commit()
    db.refresh(lot)
    return lot


@router.get("", response_model=List[LotResponse])
def list_lots(
    collector_id: Optional[uuid.UUID] = Query(None, description="Filter lots by collector"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter lots by status"),
    material_id: Optional[str] = Query(None, description="Filter lots by material"),
    regulatory_route: Optional[str] = Query(None, description="Filter lots by route"),
    is_demo: Optional[bool] = Query(None, description="Filter demo partition"),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List lots with role-scoped ownership boundaries."""
    stmt = select(Lot)

    # Ownership scoping: collectors see only own lots; recyclers see market-eligible lots; admins see all
    if current_user.role == "COLLECTOR":
        stmt = stmt.where(Lot.collector_id == current_user.id)
    elif current_user.role == "RECYCLER":
        stmt = stmt.where(Lot.status.in_(["LISTED", "MATCHED", "IN_TRANSIT", "DELIVERED"]))
    elif collector_id:
        stmt = stmt.where(Lot.collector_id == collector_id)

    if status_filter:
        stmt = stmt.where(Lot.status == status_filter.upper())
    if material_id:
        stmt = stmt.where(Lot.material_id == material_id)
    if regulatory_route:
        stmt = stmt.where(Lot.regulatory_route == regulatory_route)
    if is_demo is not None:
        stmt = stmt.where(Lot.is_demo == is_demo)

    stmt = stmt.order_by(desc(Lot.updated_at)).limit(limit)
    return db.execute(stmt).scalars().all()


@router.get("/{lot_id}", response_model=LotDetailResponse)
def get_lot(
    lot_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full lot projection with events, media, and location quality."""
    lot = db.execute(select(Lot).where(Lot.id == lot_id)).scalar_one_or_none()
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lot '{lot_id}' not found."
        )

    # Scoping check
    if current_user.role == "COLLECTOR" and lot.collector_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cannot view another collector's private lot."
        )

    # Attached images
    images = db.execute(
        select(LotImage).where(LotImage.lot_id == lot.id).order_by(LotImage.order_index)
    ).scalars().all()
    img_summaries = [
        LotImageSummary(
            media_id=img.media_id,
            purpose=img.purpose,
            order_index=img.order_index,
            captured_at=img.captured_at
        )
        for img in images
    ]

    # Location quality
    loc_summary = None
    if lot.collection_location_id:
        loc = db.execute(
            select(LocationRecord).where(LocationRecord.id == lot.collection_location_id)
        ).scalar_one_or_none()
        if loc:
            loc_summary = LocationSummary(
                source=loc.source,
                coarse_area=loc.coarse_area,
                accuracy_m=loc.accuracy_m,
                age_ms=loc.age_ms,
                captured_at=loc.captured_at
            )

    # Event history
    events = db.execute(
        select(DomainEvent).where(DomainEvent.aggregate_id == lot.id).order_by(DomainEvent.sequence)
    ).scalars().all()
    event_summaries = [
        DomainEventSummary(
            sequence=ev.sequence,
            event_type=ev.event_type,
            actor_id=ev.actor_id,
            role=ev.role,
            previous_state=ev.previous_state,
            next_state=ev.next_state,
            received_at_server=ev.received_at_server
        )
        for ev in events
    ]

    # Quality flags
    flags = db.execute(
        select(QualityFlag).where(QualityFlag.entity_id == lot.id)
    ).scalars().all()
    flag_summaries = [
        QualityFlagSummary(rule_id=f.rule_id, severity=f.severity, status=f.status)
        for f in flags
    ]

    return LotDetailResponse(
        id=lot.id,
        collector_id=lot.collector_id,
        material_id=lot.material_id,
        material_context=lot.material_context,
        regulatory_route=lot.regulatory_route,
        estimated_weight_g=lot.estimated_weight_g,
        condition=lot.condition,
        description=lot.description,
        status=lot.status,
        version=lot.version,
        is_demo=lot.is_demo,
        created_at=lot.created_at,
        updated_at=lot.updated_at,
        collection_location_id=lot.collection_location_id,
        collected_at=lot.collected_at,
        location=loc_summary,
        images=img_summaries,
        events=event_summaries,
        quality_flags=flag_summaries
    )


@router.patch("/{lot_id}", response_model=LotResponse)
async def patch_lot(
    lot_id: uuid.UUID,
    payload: UpdateLotRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update lot draft fields with optimistic version concurrency. Arbitrary status PATCH is prohibited."""
    raw_json = await request.json()
    if "status" in raw_json:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "ARBITRARY_STATUS_MUTATION_PROHIBITED",
                    "message": "Direct status modification via PATCH is prohibited. Use explicit lifecycle endpoints (/collect, /list, /cancel).",
                    "retryable": False
                }
            }
        )

    lot = db.execute(select(Lot).where(Lot.id == lot_id)).scalar_one_or_none()
    if not lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lot '{lot_id}' not found.")

    if lot.collector_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: Cannot edit another collector's lot.")

    if lot.status != "DRAFT":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "IMMUTABLE_AGREEMENT",
                    "message": f"Cannot edit lot with status '{lot.status}'. Edits are only permitted while in DRAFT.",
                    "details": {"current_status": lot.status}
                }
            }
        )

    if lot.version != payload.expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "VERSION_CONFLICT",
                    "message": f"Expected version {payload.expected_version} does not match server version {lot.version}.",
                    "details": {"current_version": lot.version, "expected_version": payload.expected_version}
                }
            }
        )

    now = datetime.now(timezone.utc)
    if payload.material_id:
        material = db.execute(select(Material).where(Material.id == payload.material_id)).scalar_one_or_none()
        if not material:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Material ID '{payload.material_id}' not found.")
        lot.material_id = payload.material_id
        if payload.regulatory_route:
            lot.regulatory_route = payload.regulatory_route
        elif not lot.regulatory_route:
            lot.regulatory_route = material.default_route

    if payload.estimated_weight_g is not None:
        lot.estimated_weight_g = payload.estimated_weight_g
        if payload.estimated_weight_g > LARGE_WEIGHT_THRESHOLD_GRAMS:
            db.add(QualityFlag(
                entity_type="LOT",
                entity_id=lot.id,
                entity_version=lot.version + 1,
                rule_id="LARGE_WEIGHT_ANOMALY",
                severity="MEDIUM",
                evidence_json={"estimated_weight_g": payload.estimated_weight_g},
                status="OPEN"
            ))

    if payload.condition is not None:
        lot.condition = payload.condition
    if payload.description is not None:
        lot.description = payload.description
    if payload.material_context is not None:
        lot.material_context = payload.material_context

    if payload.location:
        loc = attach_or_update_location(db, lot.id, payload.location)
        lot.collection_location_id = loc.id

    if payload.media_ids is not None:
        # Replace or add images
        db.execute(LotImage.__table__.delete().where(LotImage.lot_id == lot.id))
        for idx, media_id in enumerate(payload.media_ids):
            db.add(LotImage(
                lot_id=lot.id,
                media_id=media_id,
                order_index=idx,
                purpose="PHOTO",
                captured_at=now
            ))

    lot.version += 1
    lot.updated_at = now

    record_domain_event(
        db=db,
        lot=lot,
        event_type="LOT_UPDATED",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state="DRAFT",
        next_state="DRAFT",
        payload={"version": lot.version, "estimated_weight_g": lot.estimated_weight_g}
    )

    db.add(SyncChange(
        entity_type="LOT",
        entity_id=lot.id,
        entity_version=lot.version,
        visibility_scope=f"collector:{lot.collector_id}",
        created_at=now
    ))

    db.commit()
    db.refresh(lot)
    return lot


@router.post("/{lot_id}/collect", response_model=LotResponse)
def collect_lot(
    lot_id: uuid.UUID,
    payload: CollectLotRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Finalize collection: transitions DRAFT to COLLECTED with mandatory material and weight confirmation."""
    lot = db.execute(select(Lot).where(Lot.id == lot_id)).scalar_one_or_none()
    if not lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lot '{lot_id}' not found.")

    if lot.collector_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: Cannot collect another collector's lot.")

    if lot.status != "DRAFT":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "INVALID_TRANSITION",
                    "message": f"Cannot transition lot from '{lot.status}' to COLLECTED. Lot must be in DRAFT.",
                    "details": {"current_status": lot.status}
                }
            }
        )

    if lot.version != payload.expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "VERSION_CONFLICT",
                    "message": f"Expected version {payload.expected_version} does not match server version {lot.version}.",
                    "details": {"current_version": lot.version, "expected_version": payload.expected_version}
                }
            }
        )

    if not lot.material_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "MATERIAL_REQUIRED",
                    "message": "A confirmed material category must be selected before finalizing collection."
                }
            }
        )

    if not lot.estimated_weight_g or lot.estimated_weight_g <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "WEIGHT_REQUIRED",
                    "message": "A positive finite estimated weight in grams is required before collection."
                }
            }
        )

    now = datetime.now(timezone.utc)
    if payload.location:
        loc = attach_or_update_location(db, lot.id, payload.location)
        lot.collection_location_id = loc.id

    lot.status = "COLLECTED"
    lot.collected_at = now
    lot.version += 1
    lot.updated_at = now

    record_domain_event(
        db=db,
        lot=lot,
        event_type="LOT_COLLECTED",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state="DRAFT",
        next_state="COLLECTED",
        payload={"material_id": lot.material_id, "estimated_weight_g": lot.estimated_weight_g}
    )

    db.add(SyncChange(
        entity_type="LOT",
        entity_id=lot.id,
        entity_version=lot.version,
        visibility_scope=f"collector:{lot.collector_id}",
        created_at=now
    ))

    db.commit()
    db.refresh(lot)
    return lot


@router.post("/{lot_id}/list", response_model=LotResponse)
def list_lot(
    lot_id: uuid.UUID,
    payload: ListLotRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List lot for recycler matching: transitions COLLECTED to LISTED with route revalidation."""
    lot = db.execute(select(Lot).where(Lot.id == lot_id)).scalar_one_or_none()
    if not lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lot '{lot_id}' not found.")

    if lot.collector_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: Cannot list another collector's lot.")

    if lot.status != "COLLECTED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "INVALID_TRANSITION",
                    "message": f"Cannot list lot with status '{lot.status}'. Lot must be COLLECTED before it can be LISTED.",
                    "details": {"current_status": lot.status}
                }
            }
        )

    if lot.version != payload.expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "VERSION_CONFLICT",
                    "message": f"Expected version {payload.expected_version} does not match server version {lot.version}.",
                    "details": {"current_version": lot.version, "expected_version": payload.expected_version}
                }
            }
        )

    if not lot.regulatory_route or lot.regulatory_route not in ALLOWED_ROUTES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "UNKNOWN_ROUTE",
                    "message": f"Lot has invalid or unknown route '{lot.regulatory_route}'; cannot enter matching without route revalidation."
                }
            }
        )

    now = datetime.now(timezone.utc)
    lot.status = "LISTED"
    lot.version += 1
    lot.updated_at = now

    record_domain_event(
        db=db,
        lot=lot,
        event_type="LOT_LISTED",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state="COLLECTED",
        next_state="LISTED",
        payload={"regulatory_route": lot.regulatory_route, "directed_facility_id": str(payload.directed_facility_id) if payload.directed_facility_id else None}
    )

    db.add(SyncChange(
        entity_type="LOT",
        entity_id=lot.id,
        entity_version=lot.version,
        visibility_scope=f"collector:{lot.collector_id}",
        created_at=now
    ))

    db.commit()
    db.refresh(lot)
    return lot


@router.post("/{lot_id}/cancel", response_model=LotResponse)
def cancel_lot(
    lot_id: uuid.UUID,
    payload: CancelLotRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel lot with explicit reason before confirmed physical receipt."""
    lot = db.execute(select(Lot).where(Lot.id == lot_id)).scalar_one_or_none()
    if not lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lot '{lot_id}' not found.")

    if lot.collector_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: Cannot cancel another collector's lot.")

    if lot.status in ("RECEIVED", "CLOSED"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "CANNOT_CANCEL_CONFIRMED_LOT",
                    "message": f"Cannot cancel lot in '{lot.status}' status. Physical receipt has already been confirmed.",
                    "details": {"current_status": lot.status}
                }
            }
        )

    if lot.status == "CANCELLED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "ALREADY_CANCELLED",
                    "message": "Lot is already cancelled."
                }
            }
        )

    if lot.version != payload.expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "VERSION_CONFLICT",
                    "message": f"Expected version {payload.expected_version} does not match server version {lot.version}.",
                    "details": {"current_version": lot.version, "expected_version": payload.expected_version}
                }
            }
        )

    now = datetime.now(timezone.utc)
    previous_status = lot.status
    lot.status = "CANCELLED"
    lot.version += 1
    lot.updated_at = now

    record_domain_event(
        db=db,
        lot=lot,
        event_type="LOT_CANCELLED",
        actor_id=current_user.id,
        role=current_user.role,
        previous_state=previous_status,
        next_state="CANCELLED",
        payload={"reason": payload.reason}
    )

    db.add(SyncChange(
        entity_type="LOT",
        entity_id=lot.id,
        entity_version=lot.version,
        visibility_scope=f"collector:{lot.collector_id}",
        deleted_at=now,
        created_at=now
    ))

    db.commit()
    db.refresh(lot)
    return lot


@router.post("/{lot_id}/estimate", response_model=ValuationEstimateResponse)
def estimate_lot_valuation(
    lot_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compute immutable lot valuation range conforming strictly to PRICE_V1."""
    lot = db.execute(select(Lot).where(Lot.id == lot_id)).scalar_one_or_none()
    if not lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lot '{lot_id}' not found.")

    if lot.collector_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: Cannot value another collector's lot.")

    if not lot.material_id or not lot.estimated_weight_g:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Lot must have confirmed material_id and positive estimated_weight_g to compute estimate."
        )

    # Check for price summary benchmark
    summary = db.execute(
        select(PriceSummary)
        .where(PriceSummary.cohort_key.like(f"{lot.material_id}:%"))
        .order_by(desc(PriceSummary.computed_at))
        .limit(1)
    ).scalar_one_or_none()

    low_total = None
    med_total = None
    high_total = None
    confidence = "INSUFFICIENT_DATA"

    if summary and summary.median_rate:
        confidence = summary.confidence
        # Rates are in paise per kg. Weight is in grams.
        kg = lot.estimated_weight_g / 1000.0
        if summary.q1_rate:
            low_total = int(round(summary.q1_rate * kg))
        else:
            low_total = int(round(summary.median_rate * 0.9 * kg))
        med_total = int(round(summary.median_rate * kg))
        if summary.q3_rate:
            high_total = int(round(summary.q3_rate * kg))
        else:
            high_total = int(round(summary.median_rate * 1.1 * kg))

    # Persist ValuationSnapshot
    snapshot = ValuationSnapshot(
        lot_id=lot.id,
        price_summary_id=summary.id if summary else None,
        input_weight_g=lot.estimated_weight_g,
        condition=lot.condition or "INTACT",
        low_total_paise=low_total,
        median_total_paise=med_total,
        high_total_paise=high_total,
        policy_version="PRICE_V1",
        currency="INR",
        created_at=datetime.now(timezone.utc)
    )
    db.add(snapshot)
    db.commit()

    return ValuationEstimateResponse(
        lot_id=lot.id,
        policy_version="PRICE_V1",
        currency="INR",
        input_weight_g=lot.estimated_weight_g,
        condition=lot.condition or "INTACT",
        low_total_paise=low_total,
        median_total_paise=med_total,
        high_total_paise=high_total,
        confidence=confidence,
        disclaimer="Indicative valuation range based on regional benchmarks; not a guaranteed purchase offer or EPR valuation."
    )


# --- Match Schemas ---

class LotMatchRequest(BaseModel):
    search_radius_m: int = Field(50_000, gt=0, le=500_000, description="Search radius in metres (default 50,000m / 50km)")
    policy_version: str = Field("MATCH_V1", description="Matching policy version")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Optional override latitude")
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Optional override longitude")
    coarse_area: Optional[str] = Field(None, description="Optional coarse locality or district")
    require_formal_destination: bool = Field(False, description="Require L3/L4 verified formal destination")


class FactorScoreResponse(BaseModel):
    score: float
    weight: float
    weighted_contribution: float
    explanation: str
    details: Dict[str, Any] = Field(default_factory=dict)


class MatchedFacilityResponse(BaseModel):
    facility_id: uuid.UUID
    name: str
    kind: str
    region_id: str
    district: str
    state: str
    verification_level: str
    is_formal_destination: bool
    rank: int
    total_score: float
    is_recommended: bool
    distance_m: Optional[float] = None
    active_quote_rate_paise_per_kg: Optional[int] = None
    factors: Dict[str, FactorScoreResponse]
    authorized_routes: List[str]
    materials_accepted: List[str]
    pickup_available: Optional[bool] = None
    accepting_status: str
    service_area: Optional[str] = None
    disclaimer: str


class LotMatchResponse(BaseModel):
    lot_id: uuid.UUID
    policy_version: str
    search_radius_m: int
    total_candidates_evaluated: int
    eligible_count: int
    matches: List[MatchedFacilityResponse]
    exclusion_counts: Dict[str, int]
    message: str
    disclaimer: str


@router.post("/{lot_id}/matches", response_model=LotMatchResponse)
def match_lot_recyclers(
    lot_id: uuid.UUID,
    payload: LotMatchRequest = LotMatchRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Find and rank eligible recyclers for a lot conforming to MATCH_V1.
    Evaluates hard regulatory, material, registration, operational, and distance filters.
    Computes explainable weighted factor scores (distance, rate, pickup, availability, reliability)
    with deterministic tie-breaking and transparent exclusion tallies.
    Specifications: docs/03_TECHSPEC.md lines 67-84, docs/16_API_CONTRACT.md line 52.
    Requirements: R-REC-04, R-REC-05, R-REC-06.
    Acceptance cases: AT-022, AT-024, AT-025, AT-026.
    """
    lot = db.execute(select(Lot).where(Lot.id == lot_id)).scalar_one_or_none()
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lot '{lot_id}' not found."
        )

    if lot.collector_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cannot match recyclers for another collector's lot."
        )

    if not lot.material_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Lot must have confirmed material_id to match facilities."
        )

    # Determine coordinates
    lat: Optional[float] = payload.latitude
    lon: Optional[float] = payload.longitude
    if lat is None or lon is None:
        if lot.collection_location_id:
            loc = db.execute(
                select(LocationRecord).where(LocationRecord.id == lot.collection_location_id)
            ).scalar_one_or_none()
            if loc and loc.point:
                coords = extract_coordinates(loc.point)
                if coords:
                    lat, lon = coords

    # Regulatory route
    regulatory_route = lot.regulatory_route
    if not regulatory_route:
        mat = db.execute(select(Material).where(Material.id == lot.material_id)).scalar_one_or_none()
        regulatory_route = mat.regulatory_route if mat else "AUTHORIZED_EWASTE"

    # Query all active facilities
    facs = db.execute(select(Facility).where(Facility.active == True)).scalars().all()
    candidates: List[CandidateFacility] = []

    for fac in facs:
        # Load authorizations
        auths = db.execute(
            select(FacilityAuthorization).where(FacilityAuthorization.facility_id == fac.id)
        ).scalars().all()

        has_l0 = any(a.verification_level == "L0" for a in auths)
        candidate_is_demo = has_l0 or "demo" in fac.name.lower() or "simulat" in fac.name.lower()

        # Load accepted materials
        mats = db.execute(
            select(FacilityMaterial).where(
                FacilityMaterial.facility_id == fac.id,
                FacilityMaterial.accepted == True
            )
        ).scalars().all()

        mat_ids = [m.material_id for m in mats]
        lot_mat_entry = next((m for m in mats if m.material_id == lot.material_id), None)
        min_w = lot_mat_entry.min_weight_g if lot_mat_entry else None
        max_w = lot_mat_entry.max_weight_g if lot_mat_entry else None

        # Operation details
        op = db.execute(
            select(FacilityOperation).where(FacilityOperation.facility_id == fac.id)
        ).scalar_one_or_none()

        pickup_status = op.pickup_status if op else None
        accepting_status = op.accepting_status if op else "ACCEPTING"
        service_area = op.service_regions if op else None

        # Primary authorization for route/status
        matching_auth = next((a for a in auths if a.route == regulatory_route), None)
        primary_auth = matching_auth or (auths[0] if auths else None)

        v_level = primary_auth.verification_level if primary_auth else "L1"
        reg_status = primary_auth.status if primary_auth else "UNKNOWN"
        val_until = primary_auth.valid_until if primary_auth else None

        # Active quote rate
        rate_rec = db.execute(
            select(FacilityRate).where(
                FacilityRate.facility_id == fac.id,
                FacilityRate.material_id == lot.material_id,
                FacilityRate.price_kind == "QUOTE"
            ).order_by(desc(FacilityRate.observed_at)).limit(1)
        ).scalar_one_or_none()
        quote_rate = rate_rec.rate_paise_per_unit if rate_rec else None

        # Transaction reliability counts
        total_tx = db.execute(
            select(func.count(Transaction.id)).where(Transaction.facility_id == fac.id)
        ).scalar() or 0
        completed_tx = db.execute(
            select(func.count(Transaction.id)).where(
                Transaction.facility_id == fac.id,
                Transaction.lifecycle.in_(["CONFIRMED", "CLOSED"])
            )
        ).scalar() or 0

        # Coordinates
        fac_coords = extract_coordinates(fac.geo_point)
        fac_lat, fac_lon = fac_coords if fac_coords else (None, None)

        candidates.append(CandidateFacility(
            facility_id=fac.id,
            name=fac.name,
            kind=fac.kind,
            region_id=fac.region_id,
            district=fac.district,
            state=fac.state,
            latitude=fac_lat,
            longitude=fac_lon,
            authorized_routes=[a.route for a in auths],
            materials_accepted=mat_ids,
            verification_level=v_level,
            registration_status=reg_status,
            valid_until=val_until,
            pickup_available=pickup_status,
            accepting_status=accepting_status,
            service_area=service_area,
            is_demo=candidate_is_demo,
            min_weight_g=min_w,
            max_weight_g=max_w,
            active_quote_rate_paise_per_kg=quote_rate,
            completed_transactions=completed_tx,
            total_transactions=total_tx
        ))

    lot_context = LotContext(
        lot_id=lot.id,
        material_id=lot.material_id,
        regulatory_route=regulatory_route,
        estimated_weight_g=lot.estimated_weight_g,
        condition=lot.condition,
        latitude=lat,
        longitude=lon,
        coarse_area=payload.coarse_area,
        region_id=None,
        is_demo=lot.is_demo,
        require_formal_destination=payload.require_formal_destination
    )

    domain_result = match_lot_to_facilities(
        lot=lot_context,
        candidates=candidates,
        search_radius_m=payload.search_radius_m
    )

    # Convert domain result to API response
    response_matches = []
    for m in domain_result.matches:
        factors_resp = {
            fname: FactorScoreResponse(
                score=f.score,
                weight=f.weight,
                weighted_contribution=f.weighted_contribution,
                explanation=f.explanation,
                details=f.details
            )
            for fname, f in m.factors.items()
        }
        response_matches.append(MatchedFacilityResponse(
            facility_id=m.facility_id,
            name=m.name,
            kind=m.kind,
            region_id=m.region_id,
            district=m.district,
            state=m.state,
            verification_level=m.verification_level,
            is_formal_destination=m.is_formal_destination,
            rank=m.rank,
            total_score=m.total_score,
            is_recommended=m.is_recommended,
            distance_m=m.distance_m,
            active_quote_rate_paise_per_kg=m.active_quote_rate_paise_per_kg,
            factors=factors_resp,
            authorized_routes=m.authorized_routes,
            materials_accepted=m.materials_accepted,
            pickup_available=m.pickup_available,
            accepting_status=m.accepting_status,
            service_area=m.service_area,
            disclaimer=m.disclaimer
        ))

    return LotMatchResponse(
        lot_id=domain_result.lot_id,
        policy_version=domain_result.policy_version,
        search_radius_m=domain_result.search_radius_m,
        total_candidates_evaluated=domain_result.total_candidates_evaluated,
        eligible_count=domain_result.eligible_count,
        matches=response_matches,
        exclusion_counts=domain_result.exclusion_counts,
        message=domain_result.message,
        disclaimer=domain_result.disclaimer
    )
