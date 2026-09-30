"""QUALITY_V1: Data quality review rules, anomaly checks, and evaluation engine.
Technical specification: docs/03_TECHSPEC.md lines 85-100.
Requirements: R-PRICE-05, R-HAND-05, R-ADMIN-02, R-OPS-04.
Acceptance cases: AT-020, AT-033, AT-065, AT-077.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Dict, Any
import uuid


POLICY_VERSION = "QUALITY_V1"

# Rule IDs under QUALITY_V1
RULE_MISSING_INVALID = "DQ-MISSING-INVALID"
RULE_PRICE_OUTLIER = "DQ-PRICE-OUTLIER"
RULE_WEIGHT_VARIANCE = "DQ-WEIGHT-VARIANCE"
RULE_LARGE_WEIGHT = "DQ-LARGE-WEIGHT"
RULE_DUPLICATE_MEDIA = "DQ-DUPLICATE-MEDIA"
RULE_REPEATED_SALE = "DQ-REPEATED-SALE"
RULE_STALE_EVIDENCE = "DQ-STALE-EVIDENCE"
RULE_INCOMPLETE_HANDOVER = "DQ-INCOMPLETE-HANDOVER"
RULE_INCONSISTENT_STATUS = "DQ-INCONSISTENT-STATUS"

# Constants
LARGE_WEIGHT_THRESHOLD_GRAMS = 500_000  # 500 kg
WEIGHT_VARIANCE_THRESHOLD = 0.20  # 20%
MIN_COMPARABLE_OBSERVATIONS = 5
MAX_REASONABLE_WEIGHT_GRAMS = 100_000_000  # 100 tons
MAX_EVIDENCE_AGE_DAYS = 365


class QualitySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class QualityFlagStatus(str, Enum):
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


@dataclass(frozen=True)
class QualityRuleResult:
    passed: bool
    rule_id: str
    severity: QualitySeverity
    reason: str
    details: Dict[str, Any] = field(default_factory=dict)


def evaluate_price_quote(
    rate_paise_per_unit: int,
    comparable_rates: List[int]
) -> QualityRuleResult:
    """
    Evaluate quote against comparable observation cohort under QUALITY_V1.
    - With >= 5 comparable observations and IQR > 0: outside Q1 - 1.5*IQR or Q3 + 1.5*IQR -> review.
    - With IQR == 0: outside 0.70*median or 1.30*median when median > 0 -> review.
    - With < 5 comparable observations: insufficient data to flag as outlier.
    Alert says review needed; does not accuse fraud or invalidate offer (AT-020).
    """
    valid_rates = [r for r in comparable_rates if r > 0]
    n = len(valid_rates)

    if n < MIN_COMPARABLE_OBSERVATIONS:
        return QualityRuleResult(
            passed=True,
            rule_id=RULE_PRICE_OUTLIER,
            severity=QualitySeverity.MEDIUM,
            reason=f"Insufficient comparable observations ({n} < {MIN_COMPARABLE_OBSERVATIONS}); outlier check skipped.",
            details={"count": n, "min_required": MIN_COMPARABLE_OBSERVATIONS}
        )

    sorted_rates = sorted(valid_rates)

    # Compute quartiles (standard rank-based)
    # Q1 at 25th percentile, median at 50th, Q3 at 75th
    def get_percentile(data: List[int], p: float) -> float:
        k = (len(data) - 1) * p
        f = int(k)
        c = f + 1
        if c < len(data):
            d0 = data[f] * (c - k)
            d1 = data[c] * (k - f)
            return d0 + d1
        return float(data[f])

    q1 = get_percentile(sorted_rates, 0.25)
    median = get_percentile(sorted_rates, 0.50)
    q3 = get_percentile(sorted_rates, 0.75)
    iqr = q3 - q1

    if iqr > 0:
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        if rate_paise_per_unit < lower_bound or rate_paise_per_unit > upper_bound:
            return QualityRuleResult(
                passed=False,
                rule_id=RULE_PRICE_OUTLIER,
                severity=QualitySeverity.MEDIUM,
                reason=(
                    f"Quote {rate_paise_per_unit} paise/unit is outside IQR bounds "
                    f"[{lower_bound:.0f}, {upper_bound:.0f}] for {n} comparable observations "
                    f"(review recommended; does not accuse fraud or block collector choice)"
                ),
                details={
                    "rate_paise_per_unit": rate_paise_per_unit,
                    "q1": q1,
                    "median": median,
                    "q3": q3,
                    "iqr": iqr,
                    "lower_bound": lower_bound,
                    "upper_bound": upper_bound,
                    "observation_count": n
                }
            )
    else:
        # IQR is zero (clustered rates)
        if median > 0:
            lower_bound = 0.70 * median
            upper_bound = 1.30 * median
            if rate_paise_per_unit < lower_bound or rate_paise_per_unit > upper_bound:
                return QualityRuleResult(
                    passed=False,
                    rule_id=RULE_PRICE_OUTLIER,
                    severity=QualitySeverity.MEDIUM,
                    reason=(
                        f"Quote {rate_paise_per_unit} paise/unit is outside 30% median bounds "
                        f"[{lower_bound:.0f}, {upper_bound:.0f}] for zero-IQR cohort with median {median:.0f} "
                        f"(review recommended; does not accuse fraud or block collector choice)"
                    ),
                    details={
                        "rate_paise_per_unit": rate_paise_per_unit,
                        "median": median,
                        "lower_bound": lower_bound,
                        "upper_bound": upper_bound,
                        "observation_count": n,
                        "iqr": 0.0
                    }
                )

    return QualityRuleResult(
        passed=True,
        rule_id=RULE_PRICE_OUTLIER,
        severity=QualitySeverity.MEDIUM,
        reason="Quote is within normal price bounds.",
        details={"rate_paise_per_unit": rate_paise_per_unit, "observation_count": n}
    )


def evaluate_weight_variance(
    estimated_weight_g: int,
    received_weight_g: int
) -> QualityRuleResult:
    """
    Evaluate weight variance between estimated and received amounts under QUALITY_V1.
    Rule: abs(received_g - estimated_g) / estimated_g > 0.20 -> review (AT-033).
    Original estimate must be positive.
    """
    if estimated_weight_g <= 0:
        return QualityRuleResult(
            passed=True,
            rule_id=RULE_WEIGHT_VARIANCE,
            severity=QualitySeverity.LOW,
            reason="Estimated weight non-positive or absent; variance rule skipped.",
            details={"estimated_weight_g": estimated_weight_g, "received_weight_g": received_weight_g}
        )

    variance = abs(received_weight_g - estimated_weight_g) / float(estimated_weight_g)
    if variance > WEIGHT_VARIANCE_THRESHOLD:
        variance_pct = variance * 100.0
        return QualityRuleResult(
            passed=False,
            rule_id=RULE_WEIGHT_VARIANCE,
            severity=QualitySeverity.MEDIUM,
            reason=(
                f"Weight variance {variance_pct:.1f}% exceeds 20% baseline "
                f"(estimated: {estimated_weight_g}g, received: {received_weight_g}g). "
                f"Pending review; neither party's original measurement overwritten."
            ),
            details={
                "estimated_weight_g": estimated_weight_g,
                "received_weight_g": received_weight_g,
                "variance_ratio": round(variance, 4),
                "threshold": WEIGHT_VARIANCE_THRESHOLD
            }
        )

    return QualityRuleResult(
        passed=True,
        rule_id=RULE_WEIGHT_VARIANCE,
        severity=QualitySeverity.LOW,
        reason="Weight variance within acceptable 20% tolerance.",
        details={
            "estimated_weight_g": estimated_weight_g,
            "received_weight_g": received_weight_g,
            "variance_ratio": round(variance, 4)
        }
    )


def evaluate_large_weight(weight_g: int) -> QualityRuleResult:
    """
    Flag suspicious large weights (>500kg) for review without artificial rejection (AT-013).
    """
    if weight_g > LARGE_WEIGHT_THRESHOLD_GRAMS:
        return QualityRuleResult(
            passed=False,
            rule_id=RULE_LARGE_WEIGHT,
            severity=QualitySeverity.MEDIUM,
            reason=(
                f"Large weight anomaly: {weight_g}g ({weight_g / 1000.0:.1f}kg) "
                f"exceeds {LARGE_WEIGHT_THRESHOLD_GRAMS / 1000.0:.0f}kg threshold; "
                f"flagged for operational review without artificial rejection."
            ),
            details={"weight_g": weight_g, "threshold_g": LARGE_WEIGHT_THRESHOLD_GRAMS}
        )

    return QualityRuleResult(
        passed=True,
        rule_id=RULE_LARGE_WEIGHT,
        severity=QualitySeverity.LOW,
        reason="Weight is within normal operational bounds.",
        details={"weight_g": weight_g}
    )


def evaluate_duplicate_media(
    media_sha256: str,
    current_lot_id: uuid.UUID,
    existing_lot_ids: List[uuid.UUID]
) -> QualityRuleResult:
    """
    Flag same image SHA-256 referenced across distinct active lots for review.
    Alert notes: not proof of duplication or fraud (docs/03_TECHSPEC.md).
    """
    other_lots = [str(lid) for lid in existing_lot_ids if lid != current_lot_id]
    if other_lots:
        return QualityRuleResult(
            passed=False,
            rule_id=RULE_DUPLICATE_MEDIA,
            severity=QualitySeverity.MEDIUM,
            reason=(
                f"Media SHA-256 {media_sha256[:12]}... previously referenced in "
                f"{len(other_lots)} distinct active lot(s); review recommended "
                f"(not proof of duplicate material or fraud)."
            ),
            details={
                "media_sha256": media_sha256,
                "current_lot_id": str(current_lot_id),
                "other_lot_ids": other_lots
            }
        )

    return QualityRuleResult(
        passed=True,
        rule_id=RULE_DUPLICATE_MEDIA,
        severity=QualitySeverity.LOW,
        reason="Media hash is unique across active lots.",
        details={"media_sha256": media_sha256}
    )


def evaluate_repeated_sale(
    lot_id: uuid.UUID,
    active_transaction_count: int
) -> QualityRuleResult:
    """
    Check for conflicting active accepted transactions for the same lot.
    Rejects second acceptance and flags repeated event for review (AT-028).
    """
    if active_transaction_count > 0:
        return QualityRuleResult(
            passed=False,
            rule_id=RULE_REPEATED_SALE,
            severity=QualitySeverity.HIGH,
            reason=(
                f"Conflicting active transaction detected for lot {lot_id}; "
                f"repeated sale prohibited by single active agreement invariant."
            ),
            details={"lot_id": str(lot_id), "active_transaction_count": active_transaction_count}
        )

    return QualityRuleResult(
        passed=True,
        rule_id=RULE_REPEATED_SALE,
        severity=QualitySeverity.LOW,
        reason="No competing active transaction exists for this lot.",
        details={"lot_id": str(lot_id)}
    )


def evaluate_stale_evidence(
    evidence_date: datetime,
    valid_until: Optional[datetime] = None,
    now: Optional[datetime] = None,
    max_age_days: int = MAX_EVIDENCE_AGE_DAYS
) -> QualityRuleResult:
    """
    Check for expired or freshness-failed verification evidence.
    Expired authorization excludes new matches; flags pending handovers for revalidation.
    """
    current_time = now or datetime.now(timezone.utc)

    # Check legal authorization expiration
    if valid_until is not None:
        if current_time > valid_until:
            return QualityRuleResult(
                passed=False,
                rule_id=RULE_STALE_EVIDENCE,
                severity=QualitySeverity.HIGH,
                reason=(
                    f"Evidence authorization expired on {valid_until.strftime('%Y-%m-%d')}; "
                    f"excluded from new destination matching and flagged for revalidation."
                ),
                details={
                    "valid_until": valid_until.isoformat(),
                    "current_time": current_time.isoformat(),
                    "is_expired": True
                }
            )

    # Check evidence age window
    age_days = (current_time - evidence_date).days
    if age_days > max_age_days:
        return QualityRuleResult(
            passed=False,
            rule_id=RULE_STALE_EVIDENCE,
            severity=QualitySeverity.MEDIUM,
            reason=(
                f"Evidence age ({age_days} days) exceeds {max_age_days}-day validity window; "
                f"routine operational review recommended."
            ),
            details={
                "evidence_date": evidence_date.isoformat(),
                "age_days": age_days,
                "max_age_days": max_age_days
            }
        )

    return QualityRuleResult(
        passed=True,
        rule_id=RULE_STALE_EVIDENCE,
        severity=QualitySeverity.LOW,
        reason="Evidence is within valid temporal window.",
        details={"age_days": age_days}
    )


def evaluate_handover_completeness(
    has_counterparty_confirmation: bool,
    has_location: bool,
    has_evidence: bool
) -> QualityRuleResult:
    """
    Ensure incomplete handover cannot be marked confirmed complete (docs/03_TECHSPEC.md).
    """
    missing = []
    if not has_counterparty_confirmation:
        missing.append("counterparty_confirmation")
    if not has_location:
        missing.append("location_quality")
    if not has_evidence:
        missing.append("material_evidence")

    if missing:
        return QualityRuleResult(
            passed=False,
            rule_id=RULE_INCOMPLETE_HANDOVER,
            severity=QualitySeverity.HIGH,
            reason=f"Incomplete handover: missing required elements ({', '.join(missing)}).",
            details={"missing_fields": missing}
        )

    return QualityRuleResult(
        passed=True,
        rule_id=RULE_INCOMPLETE_HANDOVER,
        severity=QualitySeverity.LOW,
        reason="Handover evidence and party confirmation are complete.",
        details={"missing_fields": []}
    )


def evaluate_missing_invalid(
    weight_g: Optional[int] = None,
    amount_paise: Optional[int] = None,
    rate_paise_per_unit: Optional[int] = None
) -> QualityRuleResult:
    """
    Block structurally impossible submissions (negative, overflow, NaN).
    """
    errors = []
    if weight_g is not None:
        if weight_g < 0:
            errors.append(f"negative weight ({weight_g}g)")
        elif weight_g > MAX_REASONABLE_WEIGHT_GRAMS:
            errors.append(f"overflow weight ({weight_g}g > {MAX_REASONABLE_WEIGHT_GRAMS}g)")

    if amount_paise is not None and amount_paise < 0:
        errors.append(f"negative amount ({amount_paise} paise)")

    if rate_paise_per_unit is not None and rate_paise_per_unit < 0:
        errors.append(f"negative rate ({rate_paise_per_unit} paise/unit)")

    if errors:
        return QualityRuleResult(
            passed=False,
            rule_id=RULE_MISSING_INVALID,
            severity=QualitySeverity.CRITICAL,
            reason=f"Structurally invalid submission: {'; '.join(errors)}.",
            details={"errors": errors}
        )

    return QualityRuleResult(
        passed=True,
        rule_id=RULE_MISSING_INVALID,
        severity=QualitySeverity.LOW,
        reason="Structural validation passed.",
        details={}
    )
