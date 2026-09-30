"""PRICE_V1: Indicative price policy calculation, weighted quantiles, recency decay weighting, and lot valuation.
Technical specification: docs/03_TECHSPEC.md lines 50-66.
Requirements: R-PRICE-02, R-PRICE-03, R-PRICE-04, R-DATA-02.
Acceptance cases: AT-017, AT-018, AT-019, AT-054.
"""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Tuple, Optional


POLICY_VERSION = "PRICE_V1"
HALF_LIFE_DAYS = 7.0
MAX_CACHE_HOURS = 24.0


@dataclass(frozen=True)
class PriceObservation:
    rate_paise_per_unit: int
    weight: float = 1.0
    observation_id: str = ""


def calculate_recency_weight(age_days: float, half_life_days: float = HALF_LIFE_DAYS) -> float:
    """Compute exponential decay weight: w_i = 2^(-age_days / half_life_days)."""
    if age_days < 0:
        age_days = 0.0
    return float(2.0 ** (-age_days / half_life_days))


def calculate_weighted_quantiles(
    observations: List[PriceObservation],
    quantiles: Tuple[float, float, float] = (0.25, 0.50, 0.75)
) -> Optional[Tuple[int, int, int]]:
    """
    Calculate weighted quantiles (Q1, median, Q3) using the first-cumulative weight rule.
    Sort by rate ascending, stable by observation_id.
    Select first rate whose cumulative weight >= q * total_weight.
    """
    if not observations:
        return None

    # Filter positive weights
    valid_obs = [obs for obs in observations if obs.weight > 0]
    if not valid_obs:
        return None

    # Sort ascending by rate, then observation_id for stability
    sorted_obs = sorted(valid_obs, key=lambda x: (x.rate_paise_per_unit, x.observation_id))

    total_weight = sum(obs.weight for obs in sorted_obs)
    if total_weight <= 0:
        return None

    results = []
    for q in quantiles:
        threshold = q * total_weight
        cum = 0.0
        chosen = sorted_obs[-1].rate_paise_per_unit
        for obs in sorted_obs:
            cum += obs.weight
            if cum >= threshold - 1e-9:
                chosen = obs.rate_paise_per_unit
                break
        results.append(chosen)

    return (results[0], results[1], results[2])


def evaluate_confidence(
    observation_count: int,
    source_count: int,
    latest_age_days: float,
    is_exact_region: bool = True,
    cached_hours_ago: Optional[float] = None
) -> Tuple[str, List[str], bool]:
    """
    Evaluate statistical confidence tier and audit reason codes under PRICE_V1.
    - INSUFFICIENT: 0 eligible observations.
    - LOW: 1-2 observations, single independent source, or broader/stale cohort.
    - MEDIUM: >=3 observations from >=2 independent sources with latest age <=7 days.
    - HIGH: >=10 observations, >=3 sources, exact region, and latest age <=3 days.
    - A cached summary >24h old is visibly stale and capped at LOW.
    """
    if observation_count == 0:
        return ("INSUFFICIENT_DATA", ["NO_OBSERVATIONS_IN_WINDOW"], False)

    is_stale = bool(cached_hours_ago is not None and cached_hours_ago > MAX_CACHE_HOURS)
    reasons: List[str] = []

    if not is_exact_region:
        reasons.append("BROADER_REGION_COHORT")
    if observation_count < 3:
        reasons.append("FEW_OBSERVATIONS")
    if source_count < 2:
        reasons.append("SINGLE_SOURCE")
    if latest_age_days > 7.0:
        reasons.append("STALE_OBSERVATIONS")
    if is_stale:
        reasons.append("STALE_CACHED_SUMMARY")

    # Determine base tier
    is_high_eligible = (
        is_exact_region and
        observation_count >= 10 and
        source_count >= 3 and
        latest_age_days <= 3.0
    )
    is_medium_eligible = (
        observation_count >= 3 and
        source_count >= 2 and
        latest_age_days <= 7.0
    )

    if is_stale or not is_exact_region:
        confidence = "LOW"
    elif is_high_eligible:
        confidence = "HIGH"
    elif is_medium_eligible:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    return (confidence, reasons, is_stale)


def calculate_lot_valuation(
    rate_paise_per_kg: int,
    weight_g: int
) -> int:
    """
    Compute total paise using round_half_up(rate_paise_per_kg * weight_g / 1000).
    """
    numerator = Decimal(rate_paise_per_kg) * Decimal(weight_g)
    val = (numerator / Decimal(1000)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(val)


def calculate_lot_valuation_range(
    q1_paise: int,
    median_paise: int,
    q3_paise: int,
    weight_g: int
) -> Tuple[int, int, int]:
    """Calculate low, median, high valuation in paise for given weight in grams."""
    return (
        calculate_lot_valuation(q1_paise, weight_g),
        calculate_lot_valuation(median_paise, weight_g),
        calculate_lot_valuation(q3_paise, weight_g)
    )
