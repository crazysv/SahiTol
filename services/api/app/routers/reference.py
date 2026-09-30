"""Versioned reference bootstrap and delta sync APIs.
Covers T009 requirements: R-OFF-01.
Acceptance cases: AT-038.
"""
import base64
import json
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.db.session import get_db
from app.db.models.material import MaterialCategory, Material, MaterialAlias, SafetyGuide
from app.db.models.facility import Facility, FacilityAuthorization, FacilityMaterial
from app.db.models.audit import SyncChange

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/reference", tags=["reference"])

SNAPSHOT_VERSION = "REF-2026-09-29-01"
POLICY_VERSION = "POLICY_2026_V1"

# Curated regional benchmark prices (paise per kg)
BENCHMARK_PRICES = {
    "MAT-PCB-01": {"q1_rate": 35000, "median_rate": 42000, "q3_rate": 48000, "unit": "kg", "confidence": "HIGH"},
    "MAT-PCB-02": {"q1_rate": 8000, "median_rate": 11000, "q3_rate": 14000, "unit": "kg", "confidence": "HIGH"},
    "MAT-BAT-01": {"q1_rate": 7500, "median_rate": 8200, "q3_rate": 9000, "unit": "kg", "confidence": "HIGH"},
    "MAT-BAT-02": {"q1_rate": 12000, "median_rate": 16000, "q3_rate": 20000, "unit": "kg", "confidence": "MEDIUM"},
    "MAT-BAT-03": {"q1_rate": 3000, "median_rate": 5000, "q3_rate": 7000, "unit": "kg", "confidence": "LOW"},
    "MAT-BAT-04": {"q1_rate": 2000, "median_rate": 3500, "q3_rate": 5000, "unit": "kg", "confidence": "LOW"},
    "MAT-CRT-01": {"q1_rate": 500, "median_rate": 1000, "q3_rate": 1500, "unit": "kg", "confidence": "HIGH"},
    "MAT-LCD-01": {"q1_rate": 1500, "median_rate": 2500, "q3_rate": 3500, "unit": "kg", "confidence": "MEDIUM"},
    "MAT-CAB-01": {"q1_rate": 38000, "median_rate": 45000, "q3_rate": 52000, "unit": "kg", "confidence": "HIGH"},
    "MAT-CAB-02": {"q1_rate": 11000, "median_rate": 14000, "q3_rate": 17000, "unit": "kg", "confidence": "MEDIUM"},
    "MAT-MOT-01": {"q1_rate": 18000, "median_rate": 22000, "q3_rate": 26000, "unit": "kg", "confidence": "HIGH"},
    "MAT-MOT-02": {"q1_rate": 14000, "median_rate": 17000, "q3_rate": 20000, "unit": "kg", "confidence": "MEDIUM"},
    "MAT-PLA-01": {"q1_rate": 2000, "median_rate": 2800, "q3_rate": 3500, "unit": "kg", "confidence": "HIGH"},
    "MAT-PLA-02": {"q1_rate": 1200, "median_rate": 1800, "q3_rate": 2400, "unit": "kg", "confidence": "MEDIUM"},
    "MAT-MET-01": {"q1_rate": 65000, "median_rate": 72000, "q3_rate": 78000, "unit": "kg", "confidence": "HIGH"},
    "MAT-MET-02": {"q1_rate": 14000, "median_rate": 17500, "q3_rate": 21000, "unit": "kg", "confidence": "HIGH"},
    "MAT-MET-03": {"q1_rate": 2800, "median_rate": 3300, "q3_rate": 3800, "unit": "kg", "confidence": "HIGH"},
    "MAT-MIX-01": {"q1_rate": 4000, "median_rate": 6500, "q3_rate": 9000, "unit": "kg", "confidence": "MEDIUM"},
    "MAT-MIX-02": {"q1_rate": 2500, "median_rate": 4000, "q3_rate": 5500, "unit": "kg", "confidence": "MEDIUM"},
    "MAT-OTH-01": {"q1_rate": 1000, "median_rate": 2000, "q3_rate": 3000, "unit": "kg", "confidence": "LOW"},
    "MAT-UNK-01": {"q1_rate": 500, "median_rate": 1000, "q3_rate": 1500, "unit": "kg", "confidence": "INSUFFICIENT_DATA"},
}

# Regional verified formal facilities directory snapshot
REGIONAL_FACILITIES = [
    {
        "facility_id": "fac-dl-01",
        "name": "Greentech Recyclers Pvt Ltd",
        "kind": "RECYCLER",
        "region_id": "DELHI_NCR",
        "district": "Mayapuri Industrial Area",
        "state": "Delhi",
        "address_public": "Phase II, Mayapuri Industrial Area, New Delhi, Delhi 110064",
        "verification_level": "L3",
        "authorized_routes": ["AUTHORIZED_EWASTE", "GENERAL_RECYCLING"],
        "materials_accepted": ["MAT-PCB-01", "MAT-PCB-02", "MAT-LCD-01", "MAT-CAB-01", "MAT-PLA-01"],
        "contact_public": "+91-11-28114400",
        "active": True
    },
    {
        "facility_id": "fac-dl-02",
        "name": "Apex Battery Isolators & Recyclers",
        "kind": "RECYCLER",
        "region_id": "DELHI_NCR",
        "district": "Okhla Industrial Area",
        "state": "Delhi",
        "address_public": "Phase III, Okhla Industrial Area, New Delhi, Delhi 110020",
        "verification_level": "L3",
        "authorized_routes": ["BATTERY_ISOLATION"],
        "materials_accepted": ["MAT-BAT-01", "MAT-BAT-02", "MAT-BAT-03", "MAT-BAT-04"],
        "contact_public": "+91-11-26915500",
        "active": True
    },
    {
        "facility_id": "fac-mh-01",
        "name": "EcoRegen Solutions Mumbai",
        "kind": "RECYCLER",
        "region_id": "MAHARASHTRA",
        "district": "Kurla West",
        "state": "Maharashtra",
        "address_public": "CST Road, Kurla West, Mumbai, Maharashtra 400070",
        "verification_level": "L3",
        "authorized_routes": ["AUTHORIZED_EWASTE", "GENERAL_RECYCLING"],
        "materials_accepted": ["MAT-PCB-01", "MAT-PCB-02", "MAT-CAB-01", "MAT-MOT-01"],
        "contact_public": "+91-22-26528800",
        "active": True
    },
    {
        "facility_id": "fac-mh-02",
        "name": "Maharashtra Lead & Battery Processors",
        "kind": "RECYCLER",
        "region_id": "MAHARASHTRA",
        "district": "TTC Industrial Area, Navi Mumbai",
        "state": "Maharashtra",
        "address_public": "MIDC Rabale, Navi Mumbai, Maharashtra 400701",
        "verification_level": "L3",
        "authorized_routes": ["BATTERY_ISOLATION"],
        "materials_accepted": ["MAT-BAT-01", "MAT-BAT-02"],
        "contact_public": "+91-22-27691100",
        "active": True
    },
]


def encode_cursor(seq: int) -> str:
    """Encode monotonically increasing sequence to opaque base64 cursor."""
    raw = f"sahitol_cur_v1:{seq}".encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")


def decode_cursor(cursor_str: str) -> int:
    """Decode opaque cursor to integer sequence, raising 410 on corruption or expiry."""
    if not cursor_str or cursor_str == "0":
        return 0
    try:
        raw = base64.urlsafe_b64decode(cursor_str.encode("ascii")).decode("utf-8")
        if not raw.startswith("sahitol_cur_v1:"):
            raise ValueError("Invalid cursor format")
        seq_part = raw.split(":", 1)[1]
        seq = int(seq_part)
        if seq < 0:
            raise ValueError("Negative cursor sequence")
        return seq
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail={
                "error": {
                    "code": "CURSOR_EXPIRED",
                    "message": "The reference sync cursor has expired or is invalid. Perform a full bootstrap.",
                    "details": str(e),
                    "retryable": False
                }
            }
        )


# Response Models
class BootstrapMetadata(BaseModel):
    snapshot_version: str
    generated_at: datetime
    expires_at: datetime
    opaque_cursor: str
    region: str
    language: str
    role: str
    is_demo: bool


class PolicyParameters(BaseModel):
    policy_version: str
    max_weight_grams: int
    max_active_drafts: int
    price_freshness_days: int
    sync_batch_limit: int
    allowed_units: List[str]
    default_currency: str
    cash_settlement_enabled: bool
    disclaimer: str


class ReferenceBootstrapResponse(BaseModel):
    metadata: BootstrapMetadata
    policy: PolicyParameters
    categories: List[Dict[str, Any]]
    materials: List[Dict[str, Any]]
    aliases: List[Dict[str, Any]]
    safety_guides: List[Dict[str, Any]]
    price_benchmarks: List[Dict[str, Any]]
    facilities: List[Dict[str, Any]]


class SyncChangeItem(BaseModel):
    sequence: int
    entity_type: str
    entity_id: str
    entity_version: int
    operation: str  # UPSERT or DELETE
    data: Optional[Dict[str, Any]] = None
    created_at: datetime


class ReferenceChangesResponse(BaseModel):
    cursor: str
    next_cursor: str
    has_more: bool
    changes: List[SyncChangeItem]


@router.get("/bootstrap", response_model=ReferenceBootstrapResponse)
def get_reference_bootstrap(
    region: str = Query("DELHI_NCR", description="Regional filter (DELHI_NCR or MAHARASHTRA)"),
    language: str = Query("hi", description="Language preference (en, hi, mr)"),
    role: str = Query("COLLECTOR", description="Target role (COLLECTOR, RECYCLER, ADMIN)"),
    client_version: Optional[str] = Query(None, description="Client app build/version"),
    is_demo: bool = Query(False, description="Whether to include isolated demo data"),
    db: Session = Depends(get_db)
):
    """Deliver a complete, versioned reference snapshot for offline client operation."""
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=30)

    # 1. Fetch categories
    cats = db.execute(
        select(MaterialCategory).where(MaterialCategory.active == True).order_by(MaterialCategory.display_order)
    ).scalars().all()
    categories_list = [
        {"id": c.id, "code": c.code, "label_key": c.label_key, "display_order": c.display_order}
        for c in cats
    ]

    # 2. Fetch materials
    mats = db.execute(
        select(Material).where(Material.active == True)
    ).scalars().all()
    materials_list = []
    for m in mats:
        materials_list.append({
            "id": m.id,
            "category_id": m.category_id,
            "subcategory_code": m.subcategory_code,
            "description_key": m.description_key,
            "condition_options": m.condition_options or [],
            "allowed_units": m.allowed_units,
            "default_route": m.default_route,
            "route_requires_context": m.route_requires_context,
            "safety_guide_ids": m.safety_guide_ids or [],
        })

    # 3. Fetch aliases
    aliases_stmt = select(MaterialAlias)
    aliases_res = db.execute(aliases_stmt).scalars().all()
    aliases_list = [
        {
            "material_id": a.material_id,
            "language": a.language,
            "local_term": a.local_term,
            "normalized_term": a.normalized_term
        }
        for a in aliases_res
    ]

    # 4. Fetch safety guides
    guides = db.execute(
        select(SafetyGuide).where(SafetyGuide.review_status == "APPROVED")
    ).scalars().all()
    guides_list = [
        {
            "id": g.id,
            "material_ids": g.material_ids or [],
            "route": g.route,
            "text_key": g.text_key,
            "icon_asset_ref": g.icon_asset_ref,
            "audio_keys": g.audio_keys or {},
            "version": g.version
        }
        for g in guides
    ]

    # 5. Price benchmarks (filter by region if specified)
    norm_region = region.strip().upper()
    prices_list = []
    for mat_id, bench in BENCHMARK_PRICES.items():
        prices_list.append({
            "material_id": mat_id,
            "region_id": norm_region,
            "q1_rate": bench["q1_rate"],
            "median_rate": bench["median_rate"],
            "q3_rate": bench["q3_rate"],
            "unit": bench["unit"],
            "confidence": bench["confidence"],
            "disclaimer": "Indicative reference benchmark based on secondary market surveys."
        })

    # 6. Facilities directory filtered by region
    db_facilities = db.execute(
        select(Facility).where(Facility.active == True)
    ).scalars().all()

    if db_facilities:
        facilities_list = []
        for fac in db_facilities:
            if norm_region not in ["ALL", "INDIA"] and fac.region_id != norm_region:
                continue
            auths = db.execute(select(FacilityAuthorization).where(FacilityAuthorization.facility_id == fac.id)).scalars().all()
            has_l0 = any(a.verification_level == "L0" for a in auths)
            if is_demo != has_l0:
                continue
            primary_auth = auths[0] if auths else None
            mats = db.execute(select(FacilityMaterial).where(FacilityMaterial.facility_id == fac.id, FacilityMaterial.accepted == True)).scalars().all()
            facilities_list.append({
                "facility_id": str(fac.id),
                "name": fac.name,
                "kind": fac.kind,
                "region_id": fac.region_id,
                "district": fac.district,
                "state": fac.state,
                "address_public": fac.address_public,
                "verification_level": primary_auth.verification_level if primary_auth else "L2",
                "authorized_routes": [a.route for a in auths],
                "materials_accepted": [m.material_id for m in mats],
                "contact_public": fac.contact_public,
                "active": fac.active
            })
    else:
        facilities_list = [
            f for f in REGIONAL_FACILITIES
            if f["region_id"] == norm_region or norm_region in ["ALL", "INDIA"]
        ]

    # 7. Highest sync change sequence for cursor
    latest_change = db.execute(
        select(SyncChange.sequence).order_by(desc(SyncChange.sequence)).limit(1)
    ).scalar_one_or_none()
    current_seq = latest_change or 1
    cursor_str = encode_cursor(current_seq)

    policy = PolicyParameters(
        policy_version=POLICY_VERSION,
        max_weight_grams=50000000,
        max_active_drafts=100,
        price_freshness_days=30,
        sync_batch_limit=50,
        allowed_units=["kg", "g", "piece"],
        default_currency="INR",
        cash_settlement_enabled=True,
        disclaimer="Indicative prices are market estimates, not binding commitments or statutory EPR valuations."
    )

    metadata = BootstrapMetadata(
        snapshot_version=SNAPSHOT_VERSION,
        generated_at=now,
        expires_at=expires_at,
        opaque_cursor=cursor_str,
        region=norm_region,
        language=language,
        role=role,
        is_demo=is_demo
    )

    return ReferenceBootstrapResponse(
        metadata=metadata,
        policy=policy,
        categories=categories_list,
        materials=materials_list,
        aliases=aliases_list,
        safety_guides=guides_list,
        price_benchmarks=prices_list,
        facilities=facilities_list
    )


@router.get("/changes", response_model=ReferenceChangesResponse)
def get_reference_changes(
    cursor: str = Query("0", description="Opaque cursor token from previous sync"),
    limit: int = Query(200, ge=1, le=500, description="Page limit"),
    db: Session = Depends(get_db)
):
    """Retrieve incremental deltas and tombstones since the provided cursor."""
    seq = decode_cursor(cursor)

    changes = db.execute(
        select(SyncChange)
        .where(SyncChange.sequence > seq)
        .order_by(SyncChange.sequence.asc())
        .limit(limit + 1)
    ).scalars().all()

    has_more = len(changes) > limit
    returned_changes = changes[:limit]

    items = []
    for ch in returned_changes:
        op = "DELETE" if ch.deleted_at else "UPSERT"
        items.append(SyncChangeItem(
            sequence=ch.sequence,
            entity_type=ch.entity_type,
            entity_id=str(ch.entity_id),
            entity_version=ch.entity_version,
            operation=op,
            data=None if op == "DELETE" else {"version": ch.entity_version},
            created_at=ch.created_at
        ))

    next_seq = returned_changes[-1].sequence if returned_changes else seq
    next_cursor = encode_cursor(next_seq)

    return ReferenceChangesResponse(
        cursor=cursor,
        next_cursor=next_cursor,
        has_more=has_more,
        changes=items
    )
