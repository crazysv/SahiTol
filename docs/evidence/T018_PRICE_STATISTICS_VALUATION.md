# Test Evidence: T018 Implement Price Statistics and Snapshot Valuation

## Metadata
- **Task ID**: T018
- **Phase**: Stage 3 (Intelligence, Matching & Offers)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Reviewer**: SahiTol Pricing Intelligence & Valuation Parity Working Group

## Context & Objectives
Implements the statistical valuation engine, recency decay weighting, confidence scoring, historical trends with gap preservation, and per-lot immutable valuation snapshots conforming strictly to `PRICE_V1` (`docs/03_TECHSPEC.md` lines 50-66), addressing requirements `R-PRICE-02`, `R-PRICE-03`, `R-PRICE-04`, and `R-DATA-02`:
1. **Shared Fixtures & Python/Kotlin Parity**:
   - Created canonical shared test fixture in [`data/fixtures/pricing_v1_fixtures.json`](file:///d:/SahiTol/data/fixtures/pricing_v1_fixtures.json) and mirrored to Android test resources [`apps/android/app/src/test/resources/fixtures/pricing_v1_fixtures.json`](file:///d:/SahiTol/apps/android/app/src/test/resources/fixtures/pricing_v1_fixtures.json).
   - Validated both Python API (`services/api/tests/test_pricing.py`) and Android Kotlin (`apps/android/app/src/test/java/com/sahitol/collector/PriceCalculatorTest.kt`) against the exact same test cases:
     - Equal weights baseline: rates `[10000, 20000, 30000, 40000]` paise/kg yield `Q1=10000`, `median=20000`, `Q3=30000` using the first-cumulative method.
     - 2500g lot at baseline rates yields low/median/high `[25000, 50000, 75000]` paise.
     - Half-up rounding boundary checks: 1.5 paise rounds to 2 paise; 1.499 paise rounds to 1 paise; 333g at 1000 paise/kg rounds to 333 paise.
     - Recency exponential decay weights: rates `[40000, 30000, 20000, 10000]` with ages `[0, 7, 14, 21]` days yield weights `[1.0, 0.5, 0.25, 0.125]`, resulting in `Q1=30000`, `median=40000`, `Q3=40000`.
     - Confidence evaluation tiers across 8 distinct scenarios (no data, single source, few observations, medium, high, stale observations, broader region, cached summary stale).
2. **Daily Source Capping & Recency Decay Weighting**:
   - Rule 5: Caps each original source to at most one representative observation per cohort/day (latest `observed_at`), preventing mirrored scrapes or bulk data drops from artificially inflating weight or sample size.
   - Rule 6: Exponential recency decay `w_i = 2^(-age_days / 7.0)` where `age_days = (now - obs.observed_at).total_seconds() / 86400.0`.
3. **Broader Regional Fallback without Province Mixing**:
   - Rule 3: Exact pilot subregions (e.g. `MAYAPURI`, `SEELAMPUR`) with sparse data fall back to broader state region (`DELHI_NCR`) with explicit label `coverage_scope: "BROADER_REGION"` (confidence capped at `LOW`, reason `BROADER_REGION_COHORT`).
   - Strict invariant: Delhi-NCR and Maharashtra regional cohorts are disjoint and never mixed without explicit disclosure.
4. **Statistical Confidence & 24-Hour Cache Staleness**:
   - Rule 8: Evaluates conjunctive confidence criteria:
     - `INSUFFICIENT_DATA`: 0 eligible observations (never returns zero or synthetic placeholders).
     - `LOW`: 1-2 observations, single independent source, stale observations (>7d), or broader region cohort.
     - `MEDIUM`: ≥3 observations from ≥2 independent sources with latest age ≤7 days.
     - `HIGH`: ≥10 observations, ≥3 independent sources, exact region, and latest age ≤3 days.
     - Cached `PriceSummary` older than 24 hours is marked `is_stale=True` and capped at `LOW` confidence (`STALE_CACHED_SUMMARY`).
5. **Historical Trends with Gap Preservation**:
   - Rule 10: `GET /api/v1/prices/trends` groups observations into dated daily buckets (min, median, max, count).
   - Preserves honest gaps without fabricating interpolated points (`has_gaps: true`).
   - Supports filtering by `price_kind` (`BUY`, `QUOTE`, `SELL`) to prevent non-comparable quote rates from masquerading as settled purchase amounts.
6. **Immutable Valuation Snapshots & Quote vs Final Semantics**:
   - `POST /api/v1/prices/snapshots`: Computes and persists immutable `ValuationSnapshot` records linked to lots or materials.
   - Preserves non-binding quote disclaimer: *"Indicative valuation range based on regional benchmarks; not a guaranteed purchase offer or EPR valuation."*
   - Clear distinction between indicative quote ranges and actual transaction settlement amounts.

## Requirements & Acceptance Case Mapping
| Requirement | Test ID | Scope | Contributing Tasks | Implementation & Evidence Summary |
|---|---|---|---|---|
| R-PRICE-02 | AT-017 | RELEASE | T018, T020 | Comparable observation filtering, weighted quantiles (Q1, median, Q3), and lot valuation ranges in paise with round-half-up math. Shared test fixtures prove identical results in Python API and Android Kotlin. Automated tests: `test_shared_fixture_weighted_quantiles`, `test_shared_fixture_lot_valuations`, `test_valuation_snapshot_creation_and_disclaimer`. (Cross-task case with Android UI in T020). |
| R-PRICE-03 | AT-018 | RELEASE | T018, T020 | Freshness, observation count, independent sources, confidence tiers (INSUFFICIENT_DATA, LOW, MEDIUM, HIGH), and audit reasons. No-data returns INSUFFICIENT_DATA with null rates, never zero or synthetic fallbacks. 24h cached summary staleness capping. Automated tests: `test_shared_fixture_confidence_evaluations`, `test_price_summary_empty_cohort_returns_insufficient_data`, `test_daily_source_capping`, `test_broader_region_fallback_without_mixing_provinces`. (Cross-task case with Android UI in T020). |
| R-PRICE-04 | AT-019 | RELEASE | T018, T020, T021 | Dated daily trend buckets with median, min, max, count; honest gap preservation without fabricated points (`has_gaps: true`); price kind separation (`BUY`, `QUOTE`, `SELL`) and quote vs final amount disclaimer. Automated tests: `test_price_trends_preserves_gaps`. (Cross-task case with Android in T020 and Recycler in T021). |
| R-DATA-02 | AT-054 | RELEASE | T011, T018, T031, T047 | Price dataset lifecycle, attribution, observation moderation, and statistical quantile aggregation under PRICE_V1. Automated tests: `test_price_summary_weighted_quantiles`, `test_daily_source_capping`. (Cross-task case with quality dashboard in T031/T047). |

## Observable Artifact Outputs
1. **Canonical Shared Fixture (`data/fixtures/pricing_v1_fixtures.json`)**:
   - Complete machine-readable fixtures covering weighted quantiles, recency decay weights, rounding boundaries, single/empty observations, and confidence tier evaluations.
2. **Android Shared Fixture (`apps/android/app/src/test/resources/fixtures/pricing_v1_fixtures.json`)**:
   - Synchronized test resource ensuring Kotlin unit tests execute against the exact same fixture baseline.
3. **Android Price Calculator (`apps/android/app/src/main/java/com/sahitol/collector/domain/pricing/PriceCalculator.kt`)**:
   - `calculateRecencyWeight`, `calculateWeightedQuantiles`, `evaluateConfidence`, `calculateLotValuation`, and `calculateLotValuationRange` matching Python domain logic byte-for-byte.
4. **Android Price Calculator Unit Tests (`apps/android/app/src/test/java/com/sahitol/collector/PriceCalculatorTest.kt`)**:
   - 8 unit tests covering baseline quantiles, recency decay weighting, single observation, empty observations, 2500g valuation, half-up rounding, recency half-life, and 8 confidence evaluation scenarios.
5. **Python Pricing Domain (`services/api/app/domain/pricing.py`)**:
   - Pure domain logic with `calculate_recency_weight`, `calculate_weighted_quantiles`, `evaluate_confidence`, and `calculate_lot_valuation_range`.
6. **Python Pricing Router (`services/api/app/routers/prices.py`)**:
   - `compute_price_summary`: Decoupled core engine with daily source capping, exponential recency weighting, broader region fallback, 24h cache staleness detection, and database `PriceSummary` persistence.
   - `GET /api/v1/prices/summary`: Public endpoint with query parameters (`material_id`, `region_id`, `condition`, `max_age_days`, `allow_broader`, `force_refresh`, `is_demo`).
   - `GET /api/v1/prices/trends`: Daily trend buckets preserving honest gaps (`has_gaps: true`) and supporting price kind filtering (`BUY`, `QUOTE`, `SELL`).
   - `POST /api/v1/prices/snapshots`: Computes and persists immutable `ValuationSnapshot` with non-binding quote disclaimer.
   - `POST /api/v1/prices/estimate`: Direct parameter-based valuation range computation.
7. **Automated Test Suites**:
   - `services/api/tests/test_pricing.py`: 4 tests validating shared fixtures and recency half-life.
   - `services/api/tests/test_price_pipeline.py`: 17 tests validating submission, quarantine, moderation, weighted quantiles, empty cohorts, trend gaps, demo partition isolation, daily source capping, regional fallback, and valuation snapshots.
   - Full API test suite: 117 tests passing cleanly.
