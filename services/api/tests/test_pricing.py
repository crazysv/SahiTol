"""Tests for PRICE_V1 weighted quantiles, recency decay weighting, confidence scoring, and lot valuation.
Validates exact compliance with shared fixture: data/fixtures/pricing_v1_fixtures.json.
Technical specification: docs/03_TECHSPEC.md lines 50-66.
Requirements: R-PRICE-02, R-PRICE-03, R-PRICE-04, R-DATA-02.
Acceptance cases: AT-017, AT-018, AT-019, AT-054.
"""
import json
from pathlib import Path
import pytest

from app.domain.pricing import (
    PriceObservation,
    calculate_recency_weight,
    calculate_weighted_quantiles,
    calculate_lot_valuation,
    calculate_lot_valuation_range,
    evaluate_confidence,
)

FIXTURES_PATH = Path("data/fixtures/pricing_v1_fixtures.json")


@pytest.fixture(scope="module")
def shared_fixtures():
    """Load canonical shared JSON fixture."""
    with open(FIXTURES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_shared_fixture_weighted_quantiles(shared_fixtures):
    """Verify all weighted quantile test cases in the shared fixture."""
    for case in shared_fixtures["weighted_quantiles"]:
        obs = [
            PriceObservation(
                rate_paise_per_unit=item["rate_paise_per_unit"],
                weight=item["weight"],
                observation_id=item["observation_id"],
            )
            for item in case["observations"]
        ]
        result = calculate_weighted_quantiles(obs)
        if case["expected_q1"] is None:
            assert result is None, f"Expected None for case '{case['name']}'"
        else:
            assert result is not None, f"Expected non-null for case '{case['name']}'"
            q1, median, q3 = result
            assert q1 == case["expected_q1"], f"Q1 mismatch in '{case['name']}': got {q1}, expected {case['expected_q1']}"
            assert median == case["expected_median"], f"Median mismatch in '{case['name']}': got {median}, expected {case['expected_median']}"
            assert q3 == case["expected_q3"], f"Q3 mismatch in '{case['name']}': got {q3}, expected {case['expected_q3']}"


def test_shared_fixture_lot_valuations(shared_fixtures):
    """Verify all lot valuation cases in the shared fixture."""
    for case in shared_fixtures["lot_valuations"]:
        low, med, high = calculate_lot_valuation_range(
            q1_paise=case["rate_q1"],
            median_paise=case["rate_median"],
            q3_paise=case["rate_q3"],
            weight_g=case["weight_g"],
        )
        assert low == case["expected_low_paise"], f"Low paise mismatch in '{case['name']}': got {low}, expected {case['expected_low_paise']}"
        assert med == case["expected_median_paise"], f"Median paise mismatch in '{case['name']}': got {med}, expected {case['expected_median_paise']}"
        assert high == case["expected_high_paise"], f"High paise mismatch in '{case['name']}': got {high}, expected {case['expected_high_paise']}"


def test_shared_fixture_confidence_evaluations(shared_fixtures):
    """Verify all confidence evaluation scenarios in the shared fixture."""
    for case in shared_fixtures["confidence_evaluations"]:
        confidence, reasons, is_stale = evaluate_confidence(
            observation_count=case["count"],
            source_count=case["sources"],
            latest_age_days=case["latest_age_days"],
            is_exact_region=case["is_exact_region"],
            cached_hours_ago=case["cached_hours_ago"],
        )
        assert confidence == case["expected_confidence"], (
            f"Confidence mismatch in '{case['name']}': got {confidence}, expected {case['expected_confidence']}"
        )
        assert is_stale == case["expected_is_stale"], (
            f"Stale mismatch in '{case['name']}': got {is_stale}, expected {case['expected_is_stale']}"
        )
        for expected_reason in case["expected_reasons"]:
            assert expected_reason in reasons, (
                f"Missing expected reason '{expected_reason}' in '{case['name']}': actual reasons {reasons}"
            )


def test_recency_weight_half_life():
    """Verify exponential decay half-life at 0, 7, 14, 21 days."""
    assert calculate_recency_weight(0.0) == pytest.approx(1.0, abs=1e-6)
    assert calculate_recency_weight(7.0) == pytest.approx(0.5, abs=1e-6)
    assert calculate_recency_weight(14.0) == pytest.approx(0.25, abs=1e-6)
    assert calculate_recency_weight(21.0) == pytest.approx(0.125, abs=1e-6)
    assert calculate_recency_weight(-5.0) == pytest.approx(1.0, abs=1e-6)
