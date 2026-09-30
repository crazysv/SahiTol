"""Facility directory, role preservation, and operational management router.
Covers T012 requirements: R-REC-01, R-REC-02, R-REC-03, R-DATA-03, R-DATA-09.
Acceptance cases: AT-021, AT-022, AT-023, AT-055, AT-061.
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.db.session import get_db
from app.db.models.facility import (
    Facility,
    FacilityAuthorization,
    FacilityMaterial,
    FacilityOperation,
    FacilityRate,
    Region
)
from app.domain.matching import extract_coordinates

router = APIRouter(prefix="/api/v1/facilities", tags=["facilities"])

STATUTORY_DISCLAIMER = (
    "Public directory lead sourced from official state/central regulator registries. "
    "Listing does not represent an endorsement, commercial partnership, or EPR fulfillment certificate."
)


# Response Models
class FacilityListItemResponse(BaseModel):
    id: uuid.UUID
    name: str
    kind: str  # RECYCLER, DISMANTLER, COLLECTION_CENTRE, AGGREGATOR
    region_id: str
    district: str
    state: str
    address_public: str
    contact_public: Optional[str] = None
    geocode_accuracy: str
    active: bool
    verification_level: str  # L0, L1, L2, L3, L4
    registration_reference: Optional[str] = None
    registration_status: Optional[str] = None  # VALID, EXPIRED, SUSPENDED
    valid_until: Optional[datetime] = None
    authorized_routes: List[str]
    materials_accepted: List[str]
    pickup_available: Optional[bool] = None  # None = unknown
    service_area: Optional[str] = None
    is_formal_destination: bool
    disclaimer: str = STATUTORY_DISCLAIMER


class FacilityAuthorizationResponse(BaseModel):
    id: uuid.UUID
    route: str
    authority: str
    reference: str
    status: str
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    source_id: Optional[str] = None
    verification_level: str
    last_verified_at: Optional[datetime] = None
    scope_notes: Optional[str] = None


class FacilityMaterialResponse(BaseModel):
    id: uuid.UUID
    material_id: str
    route: str
    accepted: bool
    min_weight_g: Optional[int] = None
    max_weight_g: Optional[int] = None


class FacilityDetailResponse(BaseModel):
    id: uuid.UUID
    name: str
    kind: str
    region_id: str
    district: str
    state: str
    address_public: str
    contact_public: Optional[str] = None
    geocode_accuracy: str
    active: bool
    is_formal_destination: bool
    authorizations: List[FacilityAuthorizationResponse]
    materials: List[FacilityMaterialResponse]
    pickup_available: Optional[bool] = None
    service_area: Optional[str] = None
    accepting_status: str
    operational_updated_at: Optional[datetime] = None
    disclaimer: str = STATUTORY_DISCLAIMER


class UpdateFacilityOperationsRequest(BaseModel):
    pickup_available: Optional[bool] = Field(None, description="Pickup availability (null if unknown, true if available, false if drop-off only)")
    service_area: Optional[str] = Field(None, description="Self-declared operational service area")
    accepting_status: Optional[str] = Field("ACCEPTING", description="ACCEPTING, PAUSED, CLOSED")


class CreateFacilityRateRequest(BaseModel):
    material_id: str
    rate_paise_per_unit: int = Field(..., gt=0)
    unit: str = "kg"
    condition: Optional[str] = None
    price_kind: str = "QUOTE"
    source_id: str


def query_facilities(
    db: Session,
    region_id: Optional[str] = None,
    kind: Optional[str] = None,
    route: Optional[str] = None,
    material_id: Optional[str] = None,
    verification_level: Optional[str] = None,
    formal_destination_only: bool = False,
    is_demo: bool = False,
) -> List[FacilityListItemResponse]:
    """Internal helper to query and filter facilities."""
    stmt = select(Facility).where(Facility.active == True)
    if region_id and isinstance(region_id, str) and region_id.upper() not in ["ALL", "INDIA"]:
        stmt = stmt.where(Facility.region_id == region_id.upper())
    if kind and isinstance(kind, str):
        stmt = stmt.where(Facility.kind == kind.upper())

    facilities = db.execute(stmt).scalars().all()
    results = []

    for fac in facilities:
        # Load authorizations
        auths = db.execute(
            select(FacilityAuthorization).where(FacilityAuthorization.facility_id == fac.id)
        ).scalars().all()

        # Demo partition check
        has_l0 = any(a.verification_level == "L0" for a in auths)
        if is_demo != has_l0:
            continue

        # Route filter
        auth_routes = [a.route for a in auths]
        if route and route.upper() not in [r.upper() for r in auth_routes]:
            continue

        # Verification level filter
        primary_auth = auths[0] if auths else None
        v_level = primary_auth.verification_level if primary_auth else "L1"
        reg_status = primary_auth.status if primary_auth else "UNKNOWN"
        reg_ref = primary_auth.reference if primary_auth else None
        valid_until = primary_auth.valid_until if primary_auth else None
        if valid_until is not None and valid_until.tzinfo is None:
            valid_until = valid_until.replace(tzinfo=timezone.utc)

        if verification_level and v_level != verification_level.upper():
            continue

        # Evaluate strong formal destination badge
        # Requires L3/L4 AND active status == 'VALID' AND not is_demo
        is_formal = (
            v_level in ["L3", "L4"]
            and reg_status == "VALID"
            and not has_l0
            and (valid_until is None or valid_until >= datetime.now(timezone.utc))
        )

        if formal_destination_only and not is_formal:
            continue

        # Materials accepted
        mats = db.execute(
            select(FacilityMaterial).where(
                FacilityMaterial.facility_id == fac.id,
                FacilityMaterial.accepted == True
            )
        ).scalars().all()
        mat_ids = [m.material_id for m in mats]

        if material_id and material_id not in mat_ids:
            continue

        # Operations
        op = db.execute(
            select(FacilityOperation).where(FacilityOperation.facility_id == fac.id)
        ).scalar_one_or_none()

        results.append(FacilityListItemResponse(
            id=fac.id,
            name=fac.name,
            kind=fac.kind,
            region_id=fac.region_id,
            district=fac.district,
            state=fac.state,
            address_public=fac.address_public,
            contact_public=fac.contact_public,
            geocode_accuracy=fac.geocode_accuracy or "UNKNOWN",
            active=fac.active,
            verification_level=v_level,
            registration_reference=reg_ref,
            registration_status=reg_status,
            valid_until=valid_until,
            authorized_routes=auth_routes,
            materials_accepted=mat_ids,
            pickup_available=op.pickup_status if op else None,
            service_area=op.service_regions if op else None,
            is_formal_destination=is_formal,
            disclaimer=STATUTORY_DISCLAIMER
        ))

    return results


@router.get("", response_model=List[FacilityListItemResponse])
def list_facilities(
    region_id: Optional[str] = Query(None, description="Regional cohort filter (DELHI_NCR, MAHARASHTRA)"),
    kind: Optional[str] = Query(None, description="Facility role filter (RECYCLER, DISMANTLER, COLLECTION_CENTRE, AGGREGATOR)"),
    route: Optional[str] = Query(None, description="Regulatory route filter (AUTHORIZED_EWASTE, BATTERY_ISOLATION, GENERAL_RECYCLING)"),
    material_id: Optional[str] = Query(None, description="Target accepted material ID"),
    verification_level: Optional[str] = Query(None, description="Exact verification level (L0, L2, L3)"),
    formal_destination_only: bool = Query(False, description="Filter for strong formal destinations (L3/L4 with active valid status)"),
    is_demo: bool = Query(False, description="Filter demo fixtures"),
    db: Session = Depends(get_db)
):
    """List source-backed facilities preserving exact regulatory roles and verification levels."""
    return query_facilities(
        db=db,
        region_id=region_id,
        kind=kind,
        route=route,
        material_id=material_id,
        verification_level=verification_level,
        formal_destination_only=formal_destination_only,
        is_demo=is_demo
    )


@router.get("/geojson")
def get_facilities_geojson(
    region_id: Optional[str] = Query(None, description="Regional cohort filter (DELHI_NCR, MAHARASHTRA)"),
    kind: Optional[str] = Query(None, description="Facility role filter (RECYCLER, DISMANTLER, COLLECTION_CENTRE, AGGREGATOR)"),
    route: Optional[str] = Query(None, description="Regulatory route filter (AUTHORIZED_EWASTE, BATTERY_ISOLATION, GENERAL_RECYCLING)"),
    material_id: Optional[str] = Query(None, description="Target accepted material ID"),
    verification_level: Optional[str] = Query(None, description="Exact verification level (L0, L2, L3)"),
    formal_destination_only: bool = Query(False, description="Filter for strong formal destinations (L3/L4 with active valid status)"),
    is_demo: bool = Query(False, description="Filter demo fixtures"),
    db: Session = Depends(get_db)
):
    """
    Export facilities as GeoJSON FeatureCollection for MapLibre and spatial mapping.
    Conforms to R-REC-06 and AT-026.
    """
    items = query_facilities(
        db=db,
        region_id=region_id,
        kind=kind,
        route=route,
        material_id=material_id,
        verification_level=verification_level,
        formal_destination_only=formal_destination_only,
        is_demo=is_demo
    )

    features = []
    for item in items:
        fac = db.execute(select(Facility).where(Facility.id == item.id)).scalar_one_or_none()
        coords = extract_coordinates(fac.geo_point) if fac else None
        geometry = None
        if coords:
            lat, lon = coords
            geometry = {
                "type": "Point",
                "coordinates": [round(lon, 6), round(lat, 6)]
            }

        features.append({
            "type": "Feature",
            "id": str(item.id),
            "geometry": geometry,
            "properties": {
                "id": str(item.id),
                "name": item.name,
                "kind": item.kind,
                "region_id": item.region_id,
                "district": item.district,
                "state": item.state,
                "address_public": item.address_public,
                "contact_public": item.contact_public,
                "geocode_accuracy": item.geocode_accuracy,
                "active": item.active,
                "verification_level": item.verification_level,
                "registration_reference": item.registration_reference,
                "registration_status": item.registration_status,
                "valid_until": item.valid_until.isoformat() if item.valid_until else None,
                "authorized_routes": item.authorized_routes,
                "materials_accepted": item.materials_accepted,
                "pickup_available": item.pickup_available,
                "service_area": item.service_area,
                "is_formal_destination": item.is_formal_destination,
                "disclaimer": item.disclaimer
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }


@router.get("/{facility_id}", response_model=FacilityDetailResponse)
def get_facility_detail(
    facility_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Retrieve detailed facility claims, evidence links, and operational status."""
    fac = db.execute(select(Facility).where(Facility.id == facility_id)).scalar_one_or_none()
    if not fac:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Facility '{facility_id}' not found"
        )

    auths = db.execute(
        select(FacilityAuthorization).where(FacilityAuthorization.facility_id == fac.id)
    ).scalars().all()

    mats = db.execute(
        select(FacilityMaterial).where(FacilityMaterial.facility_id == fac.id)
    ).scalars().all()

    op = db.execute(
        select(FacilityOperation).where(FacilityOperation.facility_id == fac.id)
    ).scalar_one_or_none()

    primary_auth = auths[0] if auths else None
    v_level = primary_auth.verification_level if primary_auth else "L1"
    reg_status = primary_auth.status if primary_auth else "UNKNOWN"
    valid_until = primary_auth.valid_until if primary_auth else None
    if valid_until is not None and valid_until.tzinfo is None:
        valid_until = valid_until.replace(tzinfo=timezone.utc)
    has_l0 = any(a.verification_level == "L0" for a in auths)

    is_formal = (
        v_level in ["L3", "L4"]
        and reg_status == "VALID"
        and not has_l0
        and (valid_until is None or valid_until >= datetime.now(timezone.utc))
    )

    return FacilityDetailResponse(
        id=fac.id,
        name=fac.name,
        kind=fac.kind,
        region_id=fac.region_id,
        district=fac.district,
        state=fac.state,
        address_public=fac.address_public,
        contact_public=fac.contact_public,
        geocode_accuracy=fac.geocode_accuracy or "UNKNOWN",
        active=fac.active,
        is_formal_destination=is_formal,
        authorizations=[
            FacilityAuthorizationResponse(
                id=a.id,
                route=a.route,
                authority=a.authority,
                reference=a.reference,
                status=a.status,
                valid_from=a.valid_from,
                valid_until=a.valid_until,
                source_id=a.source_id,
                verification_level=a.verification_level,
                last_verified_at=a.last_verified_at,
                scope_notes=a.scope_notes
            )
            for a in auths
        ],
        materials=[
            FacilityMaterialResponse(
                id=m.id,
                material_id=m.material_id,
                route=m.route,
                accepted=m.accepted,
                min_weight_g=m.min_weight_g,
                max_weight_g=m.max_weight_g
            )
            for m in mats
        ],
        pickup_available=op.pickup_status if op else None,
        service_area=op.service_regions if op else None,
        accepting_status=op.accepting_status if op else "ACCEPTING",
        operational_updated_at=op.operational_updated_at if op else None,
        disclaimer=STATUTORY_DISCLAIMER
    )


@router.put("/{facility_id}/operations")
def update_facility_operations(
    facility_id: uuid.UUID,
    payload: UpdateFacilityOperationsRequest,
    db: Session = Depends(get_db)
):
    """
    Update self-declared operational parameters (pickup, service area, status).
    Per R-REC-03 / AT-023: Facility operations can be updated with provenance
    while regulatory authorization fields remain strictly admin-controlled.
    """
    fac = db.execute(select(Facility).where(Facility.id == facility_id)).scalar_one_or_none()
    if not fac:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Facility '{facility_id}' not found"
        )

    now = datetime.now(timezone.utc)
    op = db.execute(
        select(FacilityOperation).where(FacilityOperation.facility_id == facility_id)
    ).scalar_one_or_none()

    if not op:
        op = FacilityOperation(
            facility_id=facility_id,
            pickup_status=payload.pickup_available,
            service_regions=payload.service_area,
            accepting_status=payload.accepting_status or "ACCEPTING",
            operational_updated_at=now,
            source_id="PLATFORM_OPERATOR_DECLARED"
        )
        db.add(op)
    else:
        op.pickup_status = payload.pickup_available
        if payload.service_area is not None:
            op.service_regions = payload.service_area
        if payload.accepting_status:
            op.accepting_status = payload.accepting_status
        op.operational_updated_at = now
        op.source_id = "PLATFORM_OPERATOR_DECLARED"

    fac.version += 1
    db.commit()

    return {
        "status": "updated",
        "facility_id": str(facility_id),
        "pickup_available": op.pickup_status,
        "service_area": op.service_regions,
        "accepting_status": op.accepting_status,
        "operational_updated_at": op.operational_updated_at.isoformat(),
        "authorization_tampered": False
    }


@router.post("/{facility_id}/rates", status_code=status.HTTP_201_CREATED)
def post_facility_quote_rate(
    facility_id: uuid.UUID,
    payload: CreateFacilityRateRequest,
    db: Session = Depends(get_db)
):
    """Post an indicative facility buying quote for a material."""
    fac = db.execute(select(Facility).where(Facility.id == facility_id)).scalar_one_or_none()
    if not fac:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Facility '{facility_id}' not found"
        )

    now = datetime.now(timezone.utc)
    rate = FacilityRate(
        id=uuid.uuid4(),
        facility_id=facility_id,
        material_id=payload.material_id,
        condition=payload.condition,
        region_id=fac.region_id,
        rate_paise_per_unit=payload.rate_paise_per_unit,
        unit=payload.unit.lower(),
        price_kind=payload.price_kind.upper(),
        observed_at=now,
        source_id=payload.source_id,
        review_status="PENDING_REVIEW",
        is_demo=False
    )
    db.add(rate)
    db.commit()

    return {
        "id": str(rate.id),
        "facility_id": str(facility_id),
        "material_id": rate.material_id,
        "rate_paise_per_unit": rate.rate_paise_per_unit,
        "review_status": rate.review_status
    }
