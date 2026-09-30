"""Recycler Matching and Ranking Engine conforming strictly to MATCH_V1.
Specifications: docs/03_TECHSPEC.md lines 67-84, docs/22_REGULATORY_SAFETY.md.
Requirements: R-REC-04, R-REC-05, R-REC-06.
Acceptance cases: AT-022, AT-024, AT-025, AT-026.
"""
import math
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

MATCH_POLICY_VERSION = "MATCH_V1"
DEFAULT_SEARCH_RADIUS_METRES = 50_000  # 50 km default

# Weightings per MATCH_V1
WEIGHT_DISTANCE = 0.30
WEIGHT_RATE = 0.30
WEIGHT_PICKUP = 0.20
WEIGHT_AVAILABILITY = 0.15
WEIGHT_RELIABILITY = 0.05

# Exclusion Reason Codes
EXCLUSION_ROUTE_INCOMPATIBLE = "ROUTE_INCOMPATIBLE"
EXCLUSION_MATERIAL_UNACCEPTED = "MATERIAL_UNACCEPTED"
EXCLUSION_EXPIRED_REGISTRATION = "EXPIRED_REGISTRATION"
EXCLUSION_VERIFICATION_INSUFFICIENT = "VERIFICATION_INSUFFICIENT"
EXCLUSION_WEIGHT_INCOMPATIBLE = "WEIGHT_INCOMPATIBLE"
EXCLUSION_SERVICE_AREA_UNSUPPORTED = "SERVICE_AREA_UNSUPPORTED"
EXCLUSION_OPERATIONALLY_CLOSED = "OPERATIONALLY_CLOSED"
EXCLUSION_DISTANCE_EXCEEDED = "DISTANCE_EXCEEDED"
EXCLUSION_DEMO_MISMATCH = "DEMO_MISMATCH"

ALL_EXCLUSION_CODES = [
    EXCLUSION_ROUTE_INCOMPATIBLE,
    EXCLUSION_MATERIAL_UNACCEPTED,
    EXCLUSION_EXPIRED_REGISTRATION,
    EXCLUSION_VERIFICATION_INSUFFICIENT,
    EXCLUSION_WEIGHT_INCOMPATIBLE,
    EXCLUSION_SERVICE_AREA_UNSUPPORTED,
    EXCLUSION_OPERATIONALLY_CLOSED,
    EXCLUSION_DISTANCE_EXCEEDED,
    EXCLUSION_DEMO_MISMATCH,
]

STATUTORY_DISCLAIMER = (
    "Public directory lead sourced from official state/central regulator registries. "
    "Listing does not represent an endorsement, commercial partnership, or EPR fulfillment certificate."
)


def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on the earth in metres
    using the Haversine formula (Earth radius R = 6,371,000 m).
    Within 0.5% tolerance of PostGIS WGS84 geography calculation.
    """
    r = 6371000.0  # Earth radius in metres
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def extract_coordinates(geom: Any) -> Optional[Tuple[float, float]]:
    """Extract (latitude, longitude) from geometry object or WKT representation."""
    if geom is None:
        return None
    try:
        # Check for GeoAlchemy2 WKTElement or raw string
        s = getattr(geom, "data", None) or str(geom)
        match = re.search(r"POINT\s*\(\s*([-\d\.]+)\s+([-\d\.]+)\s*\)", s, re.IGNORECASE)
        if match:
            lon = float(match.group(1))
            lat = float(match.group(2))
            return (lat, lon)
    except Exception:
        pass

    try:
        from geoalchemy2.shape import to_shape
        shape = to_shape(geom)
        return (float(shape.y), float(shape.x))
    except Exception:
        pass

    if hasattr(geom, "x") and hasattr(geom, "y"):
        return (float(geom.y), float(geom.x))

    return None


@dataclass
class CandidateFacility:
    facility_id: uuid.UUID
    name: str
    kind: str  # RECYCLER, DISMANTLER, COLLECTION_CENTRE, AGGREGATOR
    region_id: str
    district: str
    state: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    authorized_routes: List[str] = field(default_factory=list)
    materials_accepted: List[str] = field(default_factory=list)
    verification_level: str = "L2"
    registration_status: str = "VALID"
    valid_until: Optional[datetime] = None
    pickup_available: Optional[bool] = None
    accepting_status: str = "ACCEPTING"
    service_area: Optional[str] = None
    is_demo: bool = False
    min_weight_g: Optional[int] = None
    max_weight_g: Optional[int] = None
    active_quote_rate_paise_per_kg: Optional[int] = None
    completed_transactions: int = 0
    total_transactions: int = 0


@dataclass
class LotContext:
    lot_id: uuid.UUID
    material_id: str
    regulatory_route: str
    estimated_weight_g: Optional[int] = None
    condition: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    coarse_area: Optional[str] = None
    region_id: Optional[str] = None
    is_demo: bool = False
    require_formal_destination: bool = False


@dataclass
class FactorScore:
    score: float
    weight: float
    weighted_contribution: float
    explanation: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MatchedFacility:
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
    distance_m: Optional[float]
    active_quote_rate_paise_per_kg: Optional[int]
    factors: Dict[str, FactorScore]
    authorized_routes: List[str]
    materials_accepted: List[str]
    pickup_available: Optional[bool]
    accepting_status: str
    service_area: Optional[str]
    disclaimer: str = STATUTORY_DISCLAIMER


@dataclass
class MatchResult:
    lot_id: uuid.UUID
    policy_version: str
    search_radius_m: int
    total_candidates_evaluated: int
    eligible_count: int
    matches: List[MatchedFacility]
    exclusion_counts: Dict[str, int]
    message: str
    disclaimer: str = STATUTORY_DISCLAIMER


def evaluate_candidate_eligibility(
    candidate: CandidateFacility,
    lot: LotContext,
    search_radius_m: int,
    now: Optional[datetime] = None
) -> Tuple[bool, Optional[str], Optional[float]]:
    """
    Evaluate hard eligibility filters per MATCH_V1.
    Returns (is_eligible, exclusion_reason, distance_m).
    """
    if now is None:
        now = datetime.now(timezone.utc)

    # 1. Demo partition isolation
    if candidate.is_demo != lot.is_demo:
        return False, EXCLUSION_DEMO_MISMATCH, None

    # 2. Regulatory route compatibility (R-REC-04 / AT-024)
    # Battery Isolation invariant: Battery lots CANNOT match general e-waste facilities!
    candidate_routes = [r.upper() for r in candidate.authorized_routes]
    lot_route = lot.regulatory_route.upper()

    if lot_route == "BATTERY_ISOLATION":
        if "BATTERY_ISOLATION" not in candidate_routes:
            return False, EXCLUSION_ROUTE_INCOMPATIBLE, None
    elif lot_route == "AUTHORIZED_EWASTE":
        if "AUTHORIZED_EWASTE" not in candidate_routes:
            return False, EXCLUSION_ROUTE_INCOMPATIBLE, None
    elif lot_route == "GENERAL_RECYCLING":
        if not any(r in candidate_routes for r in ["GENERAL_RECYCLING", "AUTHORIZED_EWASTE"]):
            return False, EXCLUSION_ROUTE_INCOMPATIBLE, None
    else:
        if lot_route not in candidate_routes:
            return False, EXCLUSION_ROUTE_INCOMPATIBLE, None

    # 3. Material acceptance
    if lot.material_id not in candidate.materials_accepted:
        return False, EXCLUSION_MATERIAL_UNACCEPTED, None

    # 4. Registration status and expiry
    if candidate.registration_status.upper() != "VALID":
        return False, EXCLUSION_EXPIRED_REGISTRATION, None

    if candidate.valid_until is not None:
        val_until = candidate.valid_until
        if val_until.tzinfo is None:
            val_until = val_until.replace(tzinfo=timezone.utc)
        if val_until < now:
            return False, EXCLUSION_EXPIRED_REGISTRATION, None

    # 5. Verification level formal destination requirement (AT-022)
    # L0/L1/L2 never qualify as formal destinations.
    if lot.require_formal_destination and not candidate.is_demo:
        if candidate.verification_level.upper() not in ["L3", "L4"]:
            return False, EXCLUSION_VERIFICATION_INSUFFICIENT, None

    # 6. Operational status
    if candidate.accepting_status.upper() in ["PAUSED", "CLOSED"]:
        return False, EXCLUSION_OPERATIONALLY_CLOSED, None

    # 7. Weight bounds compatibility
    if lot.estimated_weight_g is not None:
        if candidate.min_weight_g is not None and lot.estimated_weight_g < candidate.min_weight_g:
            return False, EXCLUSION_WEIGHT_INCOMPATIBLE, None
        if candidate.max_weight_g is not None and lot.estimated_weight_g > candidate.max_weight_g:
            return False, EXCLUSION_WEIGHT_INCOMPATIBLE, None

    # 8. Distance calculation and radius bound
    #    If the lot has location data but the candidate has no coordinates,
    #    we cannot determine service area — exclude as SERVICE_AREA_UNSUPPORTED.
    dist_m: Optional[float] = None
    if lot.latitude is not None and lot.longitude is not None:
        if candidate.latitude is None or candidate.longitude is None:
            return False, EXCLUSION_SERVICE_AREA_UNSUPPORTED, None
        dist_m = haversine_distance_m(
            lot.latitude, lot.longitude,
            candidate.latitude, candidate.longitude
        )
        if dist_m > search_radius_m:
            return False, EXCLUSION_DISTANCE_EXCEEDED, dist_m

    return True, None, dist_m



def rank_eligible_candidates(
    eligible_items: List[Tuple[CandidateFacility, Optional[float]]],
    search_radius_m: int
) -> List[MatchedFacility]:
    """
    Rank eligible candidates using MATCH_V1 weighted formula and deterministic tie-breaking.
    """
    if not eligible_items:
        return []

    # 1. Analyze comparable rate quotes
    valid_rates = [
        c.active_quote_rate_paise_per_kg
        for c, _ in eligible_items
        if c.active_quote_rate_paise_per_kg is not None
    ]
    min_rate = min(valid_rates) if valid_rates else None
    max_rate = max(valid_rates) if valid_rates else None

    scored_candidates = []

    for candidate, dist_m in eligible_items:
        # Distance 30%
        if dist_m is not None:
            norm_dist = max(0.0, 1.0 - (dist_m / search_radius_m))
            dist_score = round(norm_dist, 4)
            dist_expl = f"{dist_m / 1000.0:.1f} km straight-line"
            dist_details = {"distance_m": round(dist_m, 1), "distance_km": round(dist_m / 1000.0, 2)}
        else:
            dist_score = 0.0
            dist_expl = "approximate distance omitted / GPS unavailable"
            dist_details = {"distance_m": None, "distance_km": None}

        factor_dist = FactorScore(
            score=dist_score,
            weight=WEIGHT_DISTANCE,
            weighted_contribution=round(dist_score * WEIGHT_DISTANCE * 100.0, 2),
            explanation=dist_expl,
            details=dist_details
        )

        # Rate 30%
        if candidate.active_quote_rate_paise_per_kg is not None:
            if min_rate is not None and max_rate is not None:
                if min_rate == max_rate:
                    rate_score = 1.0
                else:
                    rate_score = round(
                        (candidate.active_quote_rate_paise_per_kg - min_rate) / (max_rate - min_rate), 4
                    )
            else:
                rate_score = 1.0
            rate_expl = f"quoted rate ₹{candidate.active_quote_rate_paise_per_kg / 100.0:.2f}/kg"
            rate_details = {
                "rate_paise_per_kg": candidate.active_quote_rate_paise_per_kg,
                "rate_inr_per_kg": round(candidate.active_quote_rate_paise_per_kg / 100.0, 2)
            }
        else:
            rate_score = 0.0
            rate_expl = "no active quote rate on file"
            rate_details = {"rate_paise_per_kg": None, "rate_inr_per_kg": None}

        factor_rate = FactorScore(
            score=rate_score,
            weight=WEIGHT_RATE,
            weighted_contribution=round(rate_score * WEIGHT_RATE * 100.0, 2),
            explanation=rate_expl,
            details=rate_details
        )

        # Pickup 20%
        if candidate.pickup_available is True:
            pickup_score = 1.0
            pickup_expl = "pickup available"
        elif candidate.pickup_available is False:
            pickup_score = 0.0
            pickup_expl = "drop-off only"
        else:
            pickup_score = 0.0
            pickup_expl = "pickup availability unknown"

        factor_pickup = FactorScore(
            score=pickup_score,
            weight=WEIGHT_PICKUP,
            weighted_contribution=round(pickup_score * WEIGHT_PICKUP * 100.0, 2),
            explanation=pickup_expl,
            details={"pickup_available": candidate.pickup_available}
        )

        # Availability 15%
        if candidate.accepting_status.upper() == "ACCEPTING":
            avail_score = 1.0
            avail_expl = "operationally accepting"
        elif candidate.accepting_status.upper() in ["UNKNOWN", ""]:
            avail_score = 0.5
            avail_expl = "operational availability unknown"
        else:
            avail_score = 0.0
            avail_expl = "operationally paused/closed"

        factor_avail = FactorScore(
            score=avail_score,
            weight=WEIGHT_AVAILABILITY,
            weighted_contribution=round(avail_score * WEIGHT_AVAILABILITY * 100.0, 2),
            explanation=avail_expl,
            details={"accepting_status": candidate.accepting_status}
        )

        # Reliability 5%
        if candidate.total_transactions < 5:
            reliab_score = 0.5
            reliab_expl = f"no history ({candidate.total_transactions}/5 min transactions)"
            reliab_details = {
                "completed": candidate.completed_transactions,
                "total": candidate.total_transactions,
                "status": "INSUFFICIENT_HISTORY"
            }
        else:
            reliab_score = round(
                min(1.0, max(0.0, candidate.completed_transactions / candidate.total_transactions)), 4
            )
            reliab_expl = f"{candidate.completed_transactions}/{candidate.total_transactions} historical completed transactions"
            reliab_details = {
                "completed": candidate.completed_transactions,
                "total": candidate.total_transactions,
                "status": "EVALUATED"
            }

        factor_reliab = FactorScore(
            score=reliab_score,
            weight=WEIGHT_RELIABILITY,
            weighted_contribution=round(reliab_score * WEIGHT_RELIABILITY * 100.0, 2),
            explanation=reliab_expl,
            details=reliab_details
        )

        # Total score: 100 * weighted sum
        total_score = round(
            100.0 * (
                WEIGHT_DISTANCE * dist_score +
                WEIGHT_RATE * rate_score +
                WEIGHT_PICKUP * pickup_score +
                WEIGHT_AVAILABILITY * avail_score +
                WEIGHT_RELIABILITY * reliab_score
            ),
            2
        )

        # Evaluate formal destination badge
        val_until = candidate.valid_until
        if val_until is not None and val_until.tzinfo is None:
            val_until = val_until.replace(tzinfo=timezone.utc)
        is_formal = (
            candidate.verification_level.upper() in ["L3", "L4"]
            and candidate.registration_status.upper() == "VALID"
            and not candidate.is_demo
            and (val_until is None or val_until >= datetime.now(timezone.utc))
        )

        factors = {
            "distance": factor_dist,
            "rate": factor_rate,
            "pickup": factor_pickup,
            "availability": factor_avail,
            "reliability": factor_reliab
        }

        scored_candidates.append({
            "candidate": candidate,
            "distance_m": dist_m,
            "total_score": total_score,
            "factors": factors,
            "is_formal": is_formal
        })

    # Stable deterministic tie-breaking:
    # 1. Total score descending (-score)
    # 2. Distance ascending (dist_m or infinity)
    # 3. Facility UUID string ascending
    scored_candidates.sort(
        key=lambda item: (
            -item["total_score"],
            item["distance_m"] if item["distance_m"] is not None else float("inf"),
            str(item["candidate"].facility_id)
        )
    )

    results: List[MatchedFacility] = []
    for rank_idx, item in enumerate(scored_candidates, start=1):
        c = item["candidate"]
        results.append(MatchedFacility(
            facility_id=c.facility_id,
            name=c.name,
            kind=c.kind,
            region_id=c.region_id,
            district=c.district,
            state=c.state,
            verification_level=c.verification_level,
            is_formal_destination=item["is_formal"],
            rank=rank_idx,
            total_score=item["total_score"],
            is_recommended=(rank_idx == 1),
            distance_m=round(item["distance_m"], 1) if item["distance_m"] is not None else None,
            active_quote_rate_paise_per_kg=c.active_quote_rate_paise_per_kg,
            factors=item["factors"],
            authorized_routes=c.authorized_routes,
            materials_accepted=c.materials_accepted,
            pickup_available=c.pickup_available,
            accepting_status=c.accepting_status,
            service_area=c.service_area,
            disclaimer=STATUTORY_DISCLAIMER
        ))

    return results


def match_lot_to_facilities(
    lot: LotContext,
    candidates: List[CandidateFacility],
    search_radius_m: int = DEFAULT_SEARCH_RADIUS_METRES,
    now: Optional[datetime] = None
) -> MatchResult:
    """
    Main matching engine function. Evaluates all candidate facilities,
    accumulates transparent exclusion counts, and ranks eligible matches.
    """
    exclusion_counts: Dict[str, int] = {code: 0 for code in ALL_EXCLUSION_CODES}
    eligible_items: List[Tuple[CandidateFacility, Optional[float]]] = []

    for candidate in candidates:
        is_eligible, reason, dist_m = evaluate_candidate_eligibility(
            candidate=candidate,
            lot=lot,
            search_radius_m=search_radius_m,
            now=now
        )
        if is_eligible:
            eligible_items.append((candidate, dist_m))
        elif reason:
            exclusion_counts[reason] = exclusion_counts.get(reason, 0) + 1

    ranked_matches = rank_eligible_candidates(eligible_items, search_radius_m)

    # User message
    if ranked_matches:
        rec = ranked_matches[0]
        message = f"Found {len(ranked_matches)} eligible facility match(es). Top recommendation: {rec.name} (Score: {rec.total_score:.1f})."
    else:
        radius_km = search_radius_m / 1000.0
        message = (
            f"No eligible facilities found within {radius_km:.0f} km. "
            "You may widen your search radius, but regulatory route and material requirements cannot be relaxed."
        )

    return MatchResult(
        lot_id=lot.lot_id,
        policy_version=MATCH_POLICY_VERSION,
        search_radius_m=search_radius_m,
        total_candidates_evaluated=len(candidates),
        eligible_count=len(ranked_matches),
        matches=ranked_matches,
        exclusion_counts={k: v for k, v in exclusion_counts.items() if v > 0},
        message=message,
        disclaimer=STATUTORY_DISCLAIMER
    )
