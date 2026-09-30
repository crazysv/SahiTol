"""Attributed Price Observations, Statistical Summaries, and Trends Router.
Implements T018: comparable observation filtering, weighted quantiles, recency decay weighting,
confidence scoring, history trends with gap preservation, and per-lot immutable valuation snapshots.
Technical specification: docs/03_TECHSPEC.md lines 50-66 (PRICE_V1).
Requirements: R-PRICE-01, R-PRICE-02, R-PRICE-03, R-PRICE-04, R-DATA-02.
Acceptance cases: AT-016, AT-017, AT-018, AT-019, AT-054.
"""
import hashlib
import uuid
from datetime import datetime, timezone, timedelta, date
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func, desc

from app.db.session import get_db
from app.db.models.price import PriceObservation, PriceSummary
from app.db.models.material import Material
from app.db.models.lot import Lot, ValuationSnapshot
from app.domain.pricing import (
    PriceObservation as DomainObservation,
    calculate_recency_weight,
    calculate_weighted_quantiles,
    calculate_lot_valuation,
    calculate_lot_valuation_range,
    evaluate_confidence,
)

router = APIRouter(prefix="/api/v1/prices", tags=["prices"])

POLICY_VERSION = "PRICE_V1"

# Regional hierarchy for fallback without province mixing (Rule 3)
REGIONAL_BROADER_MAP = {
    "DELHI_NCR": "DELHI_NCR",
    "MAYAPURI": "DELHI_NCR",
    "SEELAMPUR": "DELHI_NCR",
    "DELHI_MAYAPURI": "DELHI_NCR",
    "DELHI_SEELAMPUR": "DELHI_NCR",
    "MAHARASHTRA": "MAHARASHTRA",
    "MUMBAI": "MAHARASHTRA",
    "PUNE": "MAHARASHTRA",
    "MUMBAI_DHARAVI": "MAHARASHTRA",
    "PUNE_MIDC": "MAHARASHTRA",
}


def ensure_utc(dt: datetime) -> datetime:
    """Ensure datetime is offset-aware UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


# Request / Response Models
class CreatePriceObservationRequest(BaseModel):
    material_id: str
    region_id: str
    rate_paise_per_unit: int = Field(..., gt=0, description="Rate in positive integer paise per unit")
    unit: str = Field("kg", description="Unit of measurement (kg, g, piece)")
    price_kind: str = Field("BUY", description="BUY, QUOTE, SELL")
    condition: Optional[str] = None
    subcategory_id: Optional[str] = None
    observed_at: datetime
    source_id: str
    is_demo: bool = False


class PriceObservationResponse(BaseModel):
    id: uuid.UUID
    material_id: str
    subcategory_id: Optional[str] = None
    region_id: str
    condition: Optional[str] = None
    rate_paise_per_unit: int
    unit: str
    price_kind: str
    observed_at: datetime
    source_id: str
    review_status: str
    origin_class: str
    source_kind: str
    is_demo: bool
    created_at: datetime


class PriceSummaryResponse(BaseModel):
    material_id: str
    region_id: str
    condition: Optional[str] = None
    policy_version: str = "PRICE_V1"
    q1_rate: Optional[int] = None
    median_rate: Optional[int] = None
    q3_rate: Optional[int] = None
    count: int
    independent_sources: int
    confidence: str  # HIGH, MEDIUM, LOW, INSUFFICIENT_DATA
    reason_codes: List[str]
    coverage_scope: str = "EXACT_REGION"  # EXACT_REGION, BROADER_REGION
    is_stale: bool = False
    disclaimer: str = "Indicative valuation range based on regional benchmarks; not a guaranteed purchase offer or EPR valuation."
    as_of: datetime
    is_demo: bool


class TrendBucket(BaseModel):
    bucket_date: str  # YYYY-MM-DD
    observation_count: int
    median_rate_paise: int
    min_rate_paise: int
    max_rate_paise: int


class PriceTrendsResponse(BaseModel):
    material_id: str
    region_id: str
    days: int
    is_demo: bool
    data_points: List[TrendBucket]
    has_gaps: bool
    policy_version: str


class CreateValuationSnapshotRequest(BaseModel):
    lot_id: Optional[uuid.UUID] = None
    material_id: str
    weight_g: int = Field(..., gt=0)
    condition: Optional[str] = "INTACT"
    region_id: str = "DELHI_NCR"
    is_demo: bool = False


class ValuationSnapshotResponse(BaseModel):
    id: uuid.UUID
    lot_id: Optional[uuid.UUID] = None
    material_id: str
    region_id: str
    condition: str
    input_weight_g: int
    low_total_paise: Optional[int] = None
    median_total_paise: Optional[int] = None
    high_total_paise: Optional[int] = None
    confidence: str
    policy_version: str = "PRICE_V1"
    currency: str = "INR"
    disclaimer: str = "Indicative valuation range based on regional benchmarks; not a guaranteed purchase offer or EPR valuation."
    created_at: datetime


@router.post("/observations", response_model=PriceObservationResponse, status_code=status.HTTP_201_CREATED)
def submit_price_observation(
    payload: CreatePriceObservationRequest,
    db: Session = Depends(get_db)
):
    """Submit a dated public or platform price observation for review."""
    # 1. Validate material exists in curated catalog
    mat = db.execute(select(Material).where(Material.id == payload.material_id)).scalar_one_or_none()
    if not mat:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Material '{payload.material_id}' not found in curated taxonomy."
        )

    # 2. Reject future-dated observations beyond 5-minute clock tolerance
    now = datetime.now(timezone.utc)
    obs_time = ensure_utc(payload.observed_at)
    if obs_time > now + timedelta(minutes=5):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Future-dated observations beyond 5-minute clock tolerance are quarantined."
        )

    # 3. Validate price_kind in [BUY, QUOTE, SELL]
    valid_kinds = {"BUY", "QUOTE", "SELL"}
    if payload.price_kind.upper() not in valid_kinds:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid price_kind '{payload.price_kind}'. Must be one of {valid_kinds}."
        )

    obs = PriceObservation(
        material_id=payload.material_id,
        subcategory_id=payload.subcategory_id,
        region_id=payload.region_id.upper(),
        condition=payload.condition,
        rate_paise_per_unit=payload.rate_paise_per_unit,
        unit=payload.unit.lower(),
        price_kind=payload.price_kind.upper(),
        observed_at=obs_time,
        source_id=payload.source_id,
        review_status="PENDING_REVIEW",
        origin_class="EXTERNAL_PUBLIC" if not payload.is_demo else "DEMO",
        source_kind="PUBLIC_MARKET_QUOTE",
        is_demo=payload.is_demo,
        created_at=now
    )
    db.add(obs)
    db.commit()
    db.refresh(obs)
    return obs


@router.get("/observations", response_model=List[PriceObservationResponse])
def list_price_observations(
    material_id: Optional[str] = Query(None, description="Filter by material ID"),
    region_id: Optional[str] = Query(None, description="Filter by region (e.g. DELHI_NCR)"),
    price_kind: Optional[str] = Query(None, description="BUY, QUOTE, SELL"),
    review_status: str = Query("VERIFIED", description="VERIFIED, PENDING_REVIEW, REJECTED"),
    is_demo: bool = Query(False, description="Filter demo observations"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List price observations with privacy preservation and source transparency."""
    stmt = select(PriceObservation).where(
        PriceObservation.review_status == review_status,
        PriceObservation.is_demo == is_demo
    )
    if material_id:
        stmt = stmt.where(PriceObservation.material_id == material_id)
    if region_id:
        stmt = stmt.where(PriceObservation.region_id == region_id.upper())
    if price_kind:
        stmt = stmt.where(PriceObservation.price_kind == price_kind.upper())

    stmt = stmt.order_by(PriceObservation.observed_at.desc()).limit(limit)
    rows = db.execute(stmt).scalars().all()
    return rows


def compute_price_summary(
    db: Session,
    material_id: str,
    region_id: str = "DELHI_NCR",
    condition: Optional[str] = None,
    max_age_days: int = 30,
    allow_broader: bool = True,
    force_refresh: bool = False,
    is_demo: bool = False
) -> PriceSummaryResponse:
    """Core calculation engine for PRICE_V1 statistical quantiles and confidence tiers."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=max_age_days)
    norm_region = region_id.upper()
    broader_region = REGIONAL_BROADER_MAP.get(norm_region, norm_region)

    cohort_key = f"{material_id}:{norm_region}:{condition or 'ALL'}"

    # Check for existing cached PriceSummary unless force_refresh is requested
    if not force_refresh:
        cached = db.execute(
            select(PriceSummary)
            .where(PriceSummary.cohort_key == cohort_key)
            .order_by(desc(PriceSummary.computed_at))
            .limit(1)
        ).scalar_one_or_none()

        if cached:
            cached_dt = ensure_utc(cached.computed_at)
            cached_hours = (now - cached_dt).total_seconds() / 3600.0
            if cached_hours <= 24.0:
                return PriceSummaryResponse(
                    material_id=material_id,
                    region_id=norm_region,
                    condition=condition,
                    policy_version=cached.policy_version,
                    q1_rate=cached.q1_rate,
                    median_rate=cached.median_rate,
                    q3_rate=cached.q3_rate,
                    count=cached.count,
                    independent_sources=cached.independent_sources,
                    confidence=cached.confidence,
                    reason_codes=cached.reason_codes,
                    coverage_scope="EXACT_REGION",
                    is_stale=False,
                    as_of=cached_dt,
                    is_demo=is_demo
                )

    # Query raw observations for exact region
    stmt = select(PriceObservation).where(
        PriceObservation.material_id == material_id,
        PriceObservation.region_id == norm_region,
        PriceObservation.review_status == "VERIFIED",
        PriceObservation.is_demo == is_demo,
        PriceObservation.observed_at >= cutoff,
        func.lower(PriceObservation.unit) == "kg"  # Never compare piece quotes with per-kg
    ).order_by(PriceObservation.observed_at.desc())
    if condition:
        stmt = stmt.where(PriceObservation.condition == condition)

    observations = db.execute(stmt).scalars().all()
    coverage_scope = "EXACT_REGION"

    # Broader region fallback if exact region has no observations and allow_broader is true
    if not observations and allow_broader and broader_region != norm_region:
        broader_stmt = select(PriceObservation).where(
            PriceObservation.material_id == material_id,
            PriceObservation.region_id == broader_region,
            PriceObservation.review_status == "VERIFIED",
            PriceObservation.is_demo == is_demo,
            PriceObservation.observed_at >= cutoff,
            func.lower(PriceObservation.unit) == "kg"
        ).order_by(PriceObservation.observed_at.desc())
        if condition:
            broader_stmt = broader_stmt.where(PriceObservation.condition == condition)

        broader_obs = db.execute(broader_stmt).scalars().all()
        if broader_obs:
            observations = broader_obs
            coverage_scope = "BROADER_REGION"

    # If empty, return INSUFFICIENT_DATA - never fabricate zero or fake rates
    if not observations:
        return PriceSummaryResponse(
            material_id=material_id,
            region_id=norm_region,
            condition=condition,
            policy_version=POLICY_VERSION,
            q1_rate=None,
            median_rate=None,
            q3_rate=None,
            count=0,
            independent_sources=0,
            confidence="INSUFFICIENT_DATA",
            reason_codes=["NO_OBSERVATIONS_IN_WINDOW"],
            coverage_scope=coverage_scope,
            is_stale=False,
            as_of=now,
            is_demo=is_demo
        )

    # Rule 5: Cap each original source to one representative observation per cohort/day (latest observed_at)
    seen_source_days = set()
    capped_observations = []
    for obs in observations:
        obs_dt = ensure_utc(obs.observed_at)
        day_key = (obs.source_id, obs_dt.date())
        if day_key not in seen_source_days:
            seen_source_days.add(day_key)
            capped_observations.append(obs)

    # Rule 6: Recency exponential decay weights: w_i = 2^(-age_days / 7.0)
    domain_obs = []
    for obs in capped_observations:
        obs_dt = ensure_utc(obs.observed_at)
        age_days = (now - obs_dt).total_seconds() / 86400.0
        w = calculate_recency_weight(age_days)
        domain_obs.append(
            DomainObservation(
                rate_paise_per_unit=obs.rate_paise_per_unit,
                weight=w,
                observation_id=str(obs.id)
            )
        )

    # Rule 7: Weighted quantiles
    quantiles = calculate_weighted_quantiles(domain_obs)
    if not quantiles:
        return PriceSummaryResponse(
            material_id=material_id,
            region_id=norm_region,
            condition=condition,
            policy_version=POLICY_VERSION,
            q1_rate=None,
            median_rate=None,
            q3_rate=None,
            count=len(capped_observations),
            independent_sources=0,
            confidence="INSUFFICIENT_DATA",
            reason_codes=["QUANTILE_COMPUTATION_FAILED"],
            coverage_scope=coverage_scope,
            is_stale=False,
            as_of=now,
            is_demo=is_demo
        )

    q1, median, q3 = quantiles
    sources = set(obs.source_id for obs in capped_observations)
    source_count = len(sources)
    latest_age_days = min((now - ensure_utc(obs.observed_at)).total_seconds() / 86400.0 for obs in capped_observations)

    # Rule 8: Statistical confidence evaluation
    confidence, reason_codes, is_stale = evaluate_confidence(
        observation_count=len(capped_observations),
        source_count=source_count,
        latest_age_days=latest_age_days,
        is_exact_region=(coverage_scope == "EXACT_REGION"),
        cached_hours_ago=None
    )

    # Persist summary record in database
    input_hash = hashlib.sha256(
        f"{cohort_key}:{len(capped_observations)}:{now.date().isoformat()}".encode("utf-8")
    ).hexdigest()

    summary_record = PriceSummary(
        cohort_key=cohort_key,
        policy_version=POLICY_VERSION,
        computed_at=now,
        source_cutoff_at=cutoff,
        q1_rate=q1,
        median_rate=median,
        q3_rate=q3,
        count=len(capped_observations),
        independent_sources=source_count,
        confidence=confidence,
        reason_codes=reason_codes,
        observation_ids=[str(obs.id) for obs in capped_observations],
        input_hash=input_hash
    )
    db.add(summary_record)
    db.commit()

    return PriceSummaryResponse(
        material_id=material_id,
        region_id=norm_region,
        condition=condition,
        policy_version=POLICY_VERSION,
        q1_rate=q1,
        median_rate=median,
        q3_rate=q3,
        count=len(capped_observations),
        independent_sources=source_count,
        confidence=confidence,
        reason_codes=reason_codes,
        coverage_scope=coverage_scope,
        is_stale=False,
        as_of=now,
        is_demo=is_demo
    )


@router.get("/summary", response_model=PriceSummaryResponse)
def get_price_summary(
    material_id: str = Query(..., description="Target material ID"),
    region_id: str = Query("DELHI_NCR", description="Regional cohort"),
    condition: Optional[str] = Query(None, description="Optional condition filter"),
    max_age_days: int = Query(30, ge=1, le=180, description="Maximum observation age in days"),
    allow_broader: bool = Query(True, description="Allow falling back to broader regional cohort if exact region is sparse"),
    force_refresh: bool = Query(False, description="Bypass cached summary and recompute from raw observations"),
    is_demo: bool = Query(False, description="Filter by demo partition"),
    db: Session = Depends(get_db)
):
    """Retrieve indicative price summary with confidence and regional fallback."""
    return compute_price_summary(
        db=db,
        material_id=material_id,
        region_id=region_id,
        condition=condition,
        max_age_days=max_age_days,
        allow_broader=allow_broader,
        force_refresh=force_refresh,
        is_demo=is_demo
    )


@router.get("/trends", response_model=PriceTrendsResponse)
def get_price_trends(
    material_id: str = Query(..., description="Target material ID"),
    region_id: str = Query("DELHI_NCR", description="Regional cohort"),
    price_kind: Optional[str] = Query(None, description="Filter by price kind (BUY, QUOTE, SELL)"),
    days: int = Query(30, ge=7, le=90, description="Window size in days"),
    is_demo: bool = Query(False, description="Filter by demo partition"),
    db: Session = Depends(get_db)
):
    """Retrieve dated daily trend buckets, preserving honest gaps without fabricated points."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)
    norm_region = region_id.upper()

    stmt = select(PriceObservation).where(
        PriceObservation.material_id == material_id,
        PriceObservation.region_id == norm_region,
        PriceObservation.review_status == "VERIFIED",
        PriceObservation.is_demo == is_demo,
        PriceObservation.observed_at >= cutoff
    )
    if price_kind:
        stmt = stmt.where(PriceObservation.price_kind == price_kind.upper())

    stmt = stmt.order_by(PriceObservation.observed_at.asc())
    observations = db.execute(stmt).scalars().all()

    # Group by date string (YYYY-MM-DD)
    buckets_by_date: Dict[str, List[int]] = {}
    for obs in observations:
        obs_dt = ensure_utc(obs.observed_at)
        d_str = obs_dt.strftime("%Y-%m-%d")
        buckets_by_date.setdefault(d_str, []).append(obs.rate_paise_per_unit)

    trend_points: List[TrendBucket] = []
    for d_str in sorted(buckets_by_date.keys()):
        rates = sorted(buckets_by_date[d_str])
        mid = len(rates) // 2
        med = rates[mid] if len(rates) % 2 != 0 else (rates[mid - 1] + rates[mid]) // 2
        trend_points.append(TrendBucket(
            bucket_date=d_str,
            observation_count=len(rates),
            median_rate_paise=med,
            min_rate_paise=min(rates),
            max_rate_paise=max(rates),
        ))

    # Detect if gaps exist in the window
    has_gaps = len(trend_points) < days if trend_points else True

    return PriceTrendsResponse(
        material_id=material_id,
        region_id=norm_region,
        days=days,
        is_demo=is_demo,
        data_points=trend_points,
        has_gaps=has_gaps,
        policy_version=POLICY_VERSION
    )


@router.post("/estimate")
def estimate_valuation(
    rate_q1: int,
    rate_median: int,
    rate_q3: int,
    weight_g: int
) -> Dict[str, int]:
    """Calculate low, median, and high lot valuation in paise from weight in grams."""
    low, med, high = calculate_lot_valuation_range(rate_q1, rate_median, rate_q3, weight_g)
    return {
        "low_paise": low,
        "median_paise": med,
        "high_paise": high
    }


@router.post("/snapshots", response_model=ValuationSnapshotResponse, status_code=status.HTTP_201_CREATED)
def create_valuation_snapshot(
    payload: CreateValuationSnapshotRequest,
    db: Session = Depends(get_db)
):
    """Compute and persist an immutable ValuationSnapshot per PRICE_V1."""
    now = datetime.now(timezone.utc)
    summary_resp = compute_price_summary(
        db=db,
        material_id=payload.material_id,
        region_id=payload.region_id,
        condition=payload.condition,
        is_demo=payload.is_demo
    )

    low_total = None
    med_total = None
    high_total = None

    if summary_resp.median_rate:
        q1 = summary_resp.q1_rate if summary_resp.q1_rate is not None else int(round(summary_resp.median_rate * 0.9))
        q3 = summary_resp.q3_rate if summary_resp.q3_rate is not None else int(round(summary_resp.median_rate * 1.1))
        low_total, med_total, high_total = calculate_lot_valuation_range(q1, summary_resp.median_rate, q3, payload.weight_g)

    snapshot_id = uuid.uuid4()
    if payload.lot_id:
        lot = db.execute(select(Lot).where(Lot.id == payload.lot_id)).scalar_one_or_none()
        if not lot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lot '{payload.lot_id}' not found.")
        snapshot = ValuationSnapshot(
            id=snapshot_id,
            lot_id=lot.id,
            input_weight_g=payload.weight_g,
            condition=payload.condition or "INTACT",
            low_total_paise=low_total,
            median_total_paise=med_total,
            high_total_paise=high_total,
            policy_version=POLICY_VERSION,
            currency="INR",
            created_at=now
        )
        db.add(snapshot)
        db.commit()

    return ValuationSnapshotResponse(
        id=snapshot_id,
        lot_id=payload.lot_id,
        material_id=payload.material_id,
        region_id=payload.region_id,
        condition=payload.condition or "INTACT",
        input_weight_g=payload.weight_g,
        low_total_paise=low_total,
        median_total_paise=med_total,
        high_total_paise=high_total,
        confidence=summary_resp.confidence,
        policy_version=POLICY_VERSION,
        currency="INR",
        disclaimer="Indicative valuation range based on regional benchmarks; not a guaranteed purchase offer or EPR valuation.",
        created_at=now
    )
