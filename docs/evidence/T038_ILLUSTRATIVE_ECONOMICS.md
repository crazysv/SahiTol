# Test Evidence: T038 Implement Illustrative Economics Model

## Metadata
- **Task ID**: T038
- **Phase**: Stage 5 (Data Quality, Anomaly Detection & Admin Governance)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Reviewer**: SahiTol Economics & Systems Architecture Working Group

## Context & Objectives
Implements the transparent illustrative unit-economics model and platform sustainability engine conforming to [docs/23_UNIT_ECONOMICS.md](../23_UNIT_ECONOMICS.md), [docs/16_API_CONTRACT.md](../16_API_CONTRACT.md), fulfilling requirements `R-ECON-01` and `R-ECON-02`, and contributing to acceptance cases `AT-067` and `AT-068`:

1. **Transparent Same-Lot Comparison Calculator (`R-ECON-01`, `AT-067`)**:
   - Compares the economic outcome of the **exact same lot of material** sold through the informal status-quo channel versus channelized to an authorized recycler via SahiTol.
   - Sourced from public market price surveys and dismantling cost models (CPCB `SRC-01`, formal recyclers `SRC-03`).
   - Every input parameter is explicitly attributable and editable:
     - Material category, lot weight in grams.
     - Acquisition cost in paise.
     - Informal vs Platform gross rate in paise per kg.
     - Transport, handling, and rejection loss costs in paise.
     - Time spent (hours) and opportunity cost of time (paise/hr).
   - Strict integer paise arithmetic throughout with explicit rupee decimal conversions for UI display.
   - Strict separation from realized ledger earnings: calculation results are stateless, purely illustrative, and never mixed into actual transactional records.

2. **Sensitivity & Non-Trivial Edge-Case Handling (`R-ECON-01`)**:
   - **Zero Baseline Net Income**: If informal net earnings equal 0 paise, delta percentage is computed as `null` (`None`) rather than raising a division-by-zero exception or presenting infinite/misleading percentages. A human-readable note explains the zero-base delta.
   - **Negative Baseline (Current Loss)**: When the informal channel operates at a net loss, percentage comparisons are flagged or marked undefined to avoid misleading inverted signs.
   - **Negative Platform Benefit**: If high transport costs or low platform rates cause the platform net income to be lower than the informal status quo, the system honestly displays negative benefit and negative percentage without optimistic suppression or bias.

3. **Platform Sustainability & Zero-Collector-Fee Guarantee (`R-ECON-02`, `AT-068`)**:
   - Implements downstream sustainability simulation evaluating transaction-level economics without ever charging collectors:
     - Platform fee charged to collectors is strictly **0 paise** (`collector_fee_paise = 0`).
     - Revenue generated exclusively from downstream recycler software/traceability fee and optional EPR compliance facilitation per kg.
     - Operating costs model variable costs (cloud hosting, SMS notifications, verification storage) and fixed monthly costs (governance, infrastructure).
     - Calculates net margin per transaction and break-even monthly transaction volume. If contribution margin is non-positive, reports infinite/unachievable break-even transparently.

4. **Canonical Shared Fixtures (`data/fixtures/economics_v1_fixtures.json`)**:
   - Established reference fixture set containing:
     - TechSpec printed circuit board baseline lot (10kg PCB lot from `docs/23_UNIT_ECONOMICS.md`).
     - Stripped copper cables lot (7.35kg from `SRC-01`).
     - Remote collector high transport cost case (illustrating negative platform benefit).
     - Zero baseline test case.
     - Platform sustainability baseline (5000 transactions/mo break-even test).
   - Used for zero-drift cross-platform parity between FastAPI backend and Android Kotlin/Room implementation.

5. **Persistence & REST API Endpoints (`services/api/app/routers/economics.py`)**:
   - `POST /api/v1/economics/calculate` (and `/economics/calculate`): Stateless evaluation of same-lot comparison.
   - `POST /api/v1/economics/sustainability` (and `/economics/sustainability`): Stateless evaluation of platform sustainability.
   - `GET /api/v1/economics/scenarios` (and `/economics/scenarios`): Lists default seed scenarios and authenticated user-persisted scenarios.
   - `POST /api/v1/economics/scenarios` (and `/economics/scenarios`): Persists custom illustrative scenario to PostgreSQL/SQLite `economics_scenarios` table.
   - `GET /api/v1/economics/scenarios/{id}`: Retrieves scenario by ID with creator/admin authorization checks.
   - `DELETE /api/v1/economics/scenarios/{id}`: Deletes user-created scenario.

6. **Mandatory Guardrail Caveats**:
   - Every scenario calculation response carries mandatory caveat disclaimers:
     - `CAVEAT_ILLUSTRATIVE`: "Illustrative calculation based on stated scenario assumptions; not a guarantee of realized earnings."
     - `CAVEAT_LEDGER_SEPARATION`: "This simulation is strictly independent of your recorded ledger transactions and digital handover records."
     - `CAVEAT_SUSTAINABILITY`: "Hypothetical platform unit economics. No collector fees are charged by SahiTol."

## Automated Test Coverage
- **Dedicated Test Suite**: [`services/api/tests/test_economics.py`](../../services/api/tests/test_economics.py)
  - `test_techspec_baseline_exact_arithmetic`: Validates TechSpec 10kg PCB numbers (Rs. 1,500 vs Rs. 1,600 gross, Rs. 350 vs Rs. 470 net, +Rs. 120 / +34.29% delta).
  - `test_shared_fixtures_json_parity`: Asserts all scenarios in `economics_v1_fixtures.json` match Python engine computations with zero deviation.
  - `test_zero_baseline_delta_percent_is_none`: Verifies zero baseline produces `delta_percent: null` and informative note.
  - `test_negative_baseline_loss_handling`: Verifies informal baseline losses do not create erroneous positive metrics.
  - `test_negative_platform_benefit_displayed_honestly`: Verifies negative platform net delta is displayed truthfully.
  - `test_platform_sustainability_zero_collector_fee_guarantee`: Asserts collector fee is 0 and verifies net contribution margin and break-even calculation.
  - `test_platform_sustainability_no_finite_break_even`: Tests zero or negative contribution margin yields `break_even_monthly_transactions: null`.
  - `test_api_economics_calculate_endpoint`: Validates REST API calculation endpoint and caveat inclusion.
  - `test_api_economics_sustainability_endpoint`: Validates REST API sustainability endpoint.
  - `test_api_economics_scenarios_listing_and_crud`: Validates CRUD operations, access scoping, and default seeds on `/scenarios`.
- **Results**: 10/10 tests passed in 0.59s.
- **Full API Suite**: 228/228 tests passing across all endpoints and modules.

## Verification Log
```text
pytest services/api/tests/test_economics.py -v
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1
collected 10 items

services\api\tests\test_economics.py::test_techspec_baseline_exact_arithmetic PASSED [ 10%]
services\api\tests\test_economics.py::test_shared_fixtures_json_parity PASSED [ 20%]
services\api\tests\test_economics.py::test_zero_baseline_delta_percent_is_none PASSED [ 30%]
services\api\tests\test_economics.py::test_negative_baseline_loss_handling PASSED [ 40%]
services\api\tests\test_economics.py::test_negative_platform_benefit_displayed_honestly PASSED [ 50%]
services\api\tests\test_economics.py::test_platform_sustainability_zero_collector_fee_guarantee PASSED [ 60%]
services\api\tests\test_economics.py::test_platform_sustainability_no_finite_break_even PASSED [ 70%]
services\api\tests\test_economics.py::test_api_economics_calculate_endpoint PASSED [ 80%]
services\api\tests\test_economics.py::test_api_economics_sustainability_endpoint PASSED [ 90%]
services\api\tests\test_economics.py::test_api_economics_scenarios_listing_and_crud PASSED [100%]

======================== 10 passed, 1 warning in 0.59s ========================

pytest services/api/tests -q
228 passed, 10 warnings in 15.34s
```
