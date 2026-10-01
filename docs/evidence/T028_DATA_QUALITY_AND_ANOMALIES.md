# Test Evidence: T028 Implement Data-Quality and Anomaly Rules

## 2026-10-01 independent repair and verification

An independent implementation audit found three gaps in the otherwise-present
QUALITY_V1 wiring:

1. The offer outlier cohort included unreviewed, stale, incompatible-condition
   and recycler-quote observations. It now matches the PRICE_V1 eligible cohort:
   exact material/condition/facility region, `BUY`, kg, `VERIFIED`, same demo
   partition and the last 30 days.
2. Lot media reuse compared `media_id`, which misses a re-upload of identical
   bytes. Create and update now compare `MediaObject.sha256` across active lots.
3. Lot creation/update emitted a non-canonical `LARGE_WEIGHT_ANOMALY` ID. Both
   now use `DQ-LARGE-WEIGHT` and the shared rule result.

Verification after repair:

```text
pytest services/api/tests/test_quality.py services/api/tests/test_lots.py -q
33 passed, 4 warnings in 2.18s
```

The price test includes high-value pending, stale, `QUOTE`, and different-
condition rows and proves they do not suppress a legitimate outlier flag. The
lot test creates two different upload records with the same SHA-256 and proves
the second lot receives `DQ-DUPLICATE-MEDIA`. Warnings are third-party
FastAPI/Starlette deprecations; no test failed.

## Metadata
- **Task ID**: T028
- **Phase**: Stage 5 (Data Quality, Anomaly Detection & Admin Governance)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Reviewer**: SahiTol Core Backend & Data Governance Working Group

## Context & Objectives
Implements the comprehensive data-quality and anomaly evaluation engine (`POLICY_VERSION = "QUALITY_V1"`), missing/invalid/duplicate/stale/inconsistent checks, price outlier IQR/median bounds (`AT-020`), weight variance > 20% baseline (`AT-033`), image reuse detection, repeated transaction acceptance exclusion (`AT-028`), admin quality flags API with drill-down, summary metrics with true denominators (`R-ADMIN-02`, `AT-065`), and review resolution workflow emitting append-only hash-chained domain events. Strictly adheres to [docs/03_TECHSPEC.md](../03_TECHSPEC.md), [docs/18_DATA_PROVENANCE.md](../18_DATA_PROVENANCE.md), and [docs/MONITORING.md](../MONITORING.md), fulfilling requirements `R-PRICE-05`, `R-HAND-05`, `R-ADMIN-02`, and `R-OPS-04`:

1. **Non-Accusatory Anomaly Detection & Honest Provenance**:
   - Anomalies never accuse users of fraud, dishonest conduct, or malicious activity.
   - Price quote outliers are flagged as review reasons for market intelligence and risk management; they never block collector choice or prevent offer creation without a separate eligibility violation (`AT-020`).
   - Weight variance retains the collector's original estimate and the initial proposed terms revision; neither party overwrites historical facts (`AT-033`).

2. **Domain Rules Engine (`POLICY_VERSION = "QUALITY_V1"`)**:
   - Implemented in [`services/api/app/domain/quality.py`](../../services/api/app/domain/quality.py):
     - `evaluate_price_quote`: Requires $\ge 5$ comparable observations for the same material and demo status. If $< 5$, skips evaluation with `INSUFFICIENT_DATA` (`RuleResult(passed=True)`). If $\ge 5$, calculates IQR ($Q_3 - Q_1$). If $IQR > 0$, bounds are $[Q_1 - 1.5 \times IQR, Q_3 + 1.5 \times IQR]$. If $IQR == 0$ (identical prices), bounds are $[0.70 \times \text{median}, 1.30 \times \text{median}]$. Flags `DQ-PRICE-OUTLIER` with severity `MEDIUM` without blocking collector choice (`AT-020`).
     - `evaluate_weight_variance`: Calculates relative discrepancy $\frac{|\text{measured} - \text{estimated}|}{\text{estimated}}$. Flags `DQ-WEIGHT-VARIANCE` if variance exceeds the 20% baseline ($0.20$), triggering mandatory bilateral review (`AT-033`).
     - `evaluate_large_weight`: Flags `DQ-LARGE-WEIGHT` (severity `HIGH`) if scrap weight exceeds 500,000g (500kg anomaly) to prompt manual weighbridge verification without artificial rejection.
     - `evaluate_duplicate_media`: Flags `DQ-DUPLICATE-MEDIA` (severity `MEDIUM`) when media SHA-256 hash matches media on a separate active lot. States explicitly: "not proof of duplication or fraud".
     - `evaluate_repeated_sale`: Flags `DQ-REPEATED-SALE` (severity `HIGH`) when a lot already has an active accepted agreement (`AT-028`).
     - `evaluate_stale_evidence`: Flags `DQ-STALE-EVIDENCE` (severity `MEDIUM`) when authorization permits are expired or evidence age exceeds 365 days.
     - `evaluate_handover_completeness`: Blocks handover confirmation if mandatory fields or counterparty identity are missing.
     - `evaluate_missing_invalid`: Blocks negative weights, overflow rates, or missing foreign key references.

3. **Operational Router Integrations**:
   - **Trade (`services/api/app/routers/trade.py`)**:
     - `POST /api/v1/requests/{id}/offers`: Evaluates `evaluate_price_quote` against verified market observations. If an outlier is detected, creates a `QualityFlag` record linked to the offer without blocking offer creation or response (`AT-020`).
     - `POST /api/v1/offers/{id}/accept`: Evaluates `evaluate_repeated_sale` against active transactions for the same lot. If conflicting agreement exists, logs `DQ-REPEATED-SALE` `QualityFlag` and returns HTTP 409 (`AT-028`).
   - **Handovers (`services/api/app/routers/handovers.py`)**:
     - `POST /api/v1/handovers/{id}/confirm`: Detects measured weight/grade discrepancies. If discrepancy exceeds 20%, evaluates `evaluate_weight_variance`, logs `DQ-WEIGHT-VARIANCE` `QualityFlag`, creates a new `TermsRevision` with `proposed_by="FACILITY"`, transitions handover to `PENDING_COLLECTOR_ACK`, and preserves all original collector estimates and baseline values (`AT-033`).
   - **Lots (`services/api/app/routers/lots.py`)**:
     - Lot creation inspects media object SHA-256 hashes against existing active lots, logging `DQ-DUPLICATE-MEDIA` `QualityFlag` for admin audit when shared media is detected.

4. **Admin Governance & Review APIs (`services/api/app/routers/admin.py`)**:
   - `GET /api/v1/admin/quality-flags`: Multi-filter listing supporting `status`, `severity`, `rule_id`, `entity_type`, `entity_id`, and pagination.
   - `GET /api/v1/admin/quality-flags/summary`: Computes aggregate data quality metrics with true mathematical denominators (`total_flags`, `open_flags`, `resolved_flags`, `open_fraction`, `resolved_fraction`, `status_counts`, `severity_counts`, `rule_counts`, `entity_type_counts`) fulfilling `R-ADMIN-02` and `AT-065`.
   - `GET /api/v1/admin/quality-flags/{id}`: Single flag drill-down with full evidence payload.
   - `POST /api/v1/admin/quality-flags/{id}/resolve`: Resolves (`RESOLVE`), dismisses (`DISMISS`), or acknowledges (`ACKNOWLEDGE`) quality flags. Requires mandatory justification `reason` ($\ge 5$ characters), records admin actor ID, and emits append-only hash-chained `DomainEvent`.
   - `POST /api/v1/admin/quality-flags/evaluate`: On-demand stateless evaluation endpoint for client-side pre-validation and diagnostics.

5. **Test Coverage & Verification**:
   - **Dedicated Test Suite**: [`services/api/tests/test_quality.py`](../../services/api/tests/test_quality.py) contains 18 comprehensive tests:
     - 10 unit tests for all domain rules (insufficient data skip, IQR bounds, zero IQR fallback, weight variance, large weight, duplicate media, repeated sale, stale evidence, completeness, missing/invalid).
     - 5 admin endpoint tests (unauthorized rejection, listing/filtering, summary metrics with real denominators, resolution/dismissal with domain event emission, on-demand evaluation).
     - 3 operational integration tests (price outlier non-blocking offer creation `AT-020`, weight discrepancy handover revision and flag logging `AT-033`, repeated sale conflict rejection and flag logging `AT-028`).
   - **Results**: 18/18 tests passed in 0.98s.
   - **Regression Suite**: Full test suite across `services/api/tests` executed: 201/201 tests passed in 16.84s with 0 regressions.

## Verification Log
```text
pytest services/api/tests/test_quality.py -v
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1
collected 18 items

services/api/tests/test_quality.py::test_price_outlier_insufficient_data PASSED [  5%]
services/api/tests/test_quality.py::test_price_outlier_iqr_bounds PASSED [ 11%]
services/api/tests/test_quality.py::test_price_outlier_zero_iqr PASSED   [ 16%]
services/api/tests/test_quality.py::test_weight_variance_rule PASSED     [ 22%]
services/api/tests/test_quality.py::test_large_weight_rule PASSED        [ 27%]
services/api/tests/test_quality.py::test_duplicate_media_rule PASSED     [ 33%]
services/api/tests/test_quality.py::test_repeated_sale_rule PASSED       [ 38%]
services/api/tests/test_quality.py::test_stale_evidence_rule PASSED      [ 44%]
services/api/tests/test_quality.py::test_handover_completeness_rule PASSED [ 50%]
services/api/tests/test_quality.py::test_missing_invalid_rule PASSED     [ 55%]
services/api/tests/test_quality.py::test_admin_quality_flags_unauthorized PASSED [ 61%]
services/api/tests/test_quality.py::test_admin_quality_flags_listing_and_filtering PASSED [ 66%]
services/api/tests/test_quality.py::test_admin_quality_summary_metrics PASSED [ 72%]
services/api/tests/test_quality.py::test_admin_resolve_and_dismiss_quality_flag PASSED [ 77%]
services/api/tests/test_quality.py::test_on_demand_evaluate_endpoint PASSED [ 83%]
services/api/tests/test_quality.py::test_trade_offer_price_outlier_flagging_without_blocking PASSED [ 88%]
services/api/tests/test_quality.py::test_handover_weight_discrepancy_logs_quality_flag PASSED [ 94%]
services/api/tests/test_quality.py::test_repeated_sale_logs_flag_and_rejects PASSED [100%]

======================== 18 passed, 1 warning in 0.98s ========================

pytest services/api/tests -q
........................................................................ [ 35%]
........................................................................ [ 71%]
.........................................................                [100%]
201 passed, 10 warnings in 16.84s
```
