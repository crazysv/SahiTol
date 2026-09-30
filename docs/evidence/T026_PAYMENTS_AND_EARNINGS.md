# Test Evidence: T026 Implement Payment Assertions and Earnings Projections

## Metadata
- **Task ID**: T026
- **Phase**: Stage 4 (Handover, Payments & Verification)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Reviewer**: SahiTol Payment & Ledger Working Group

## Context & Objectives
Implements cash-first payment assertions without bank account or gateway dependency, optional UPI reference recording, counterparty acknowledgement, disputes, partial payment aggregation, duplicate-safe idempotency, append-only reversals linking original records without deletion, strict transaction closure invariants, and collector earnings reconciliation with strict demo isolation conforming to [16_API_CONTRACT.md](../16_API_CONTRACT.md) lines 70–74, [04_APPFLOW.md](../04_APPFLOW.md) lines 70–89, [06_SCHEMA.md](../06_SCHEMA.md), and [18_DATA_PROVENANCE.md](../18_DATA_PROVENANCE.md):

1. **Cash-First Payment Assertions & Optional UPI Recording (`R-PAY-01`, `AT-035`)**:
   - `POST /transactions/{id}/payments` and `POST /api/v1/transactions/{id}/payments`: Participant records payment assertion.
   - **Cash Without Gateway**: Records cash payment assertions directly between parties without third-party bank gateways or accounts.
   - **UPI Reference Tracking**: Optional UPI or other methods record client assertions and private reference strings (`private_reference`), never performing or assuming direct bank settlement.
   - **Participant Authorization**: Only transaction participants (collector owner, linked facility active members) or administrators can assert payments. Third parties receive HTTP 403 Forbidden.
   - **State Machine**: Initial state is `ASSERTED`. Derives `asserted_by` (`COLLECTOR` or `FACILITY`).
   - **Append-Only Domain Event**: Emits `PAYMENT_ASSERTED` on aggregate `TRANSACTION` with SHA-256 hash chaining.

2. **Counterparty Acknowledgement & Dispute Workflow (`R-PAY-01`, `AT-035`)**:
   - `POST /payments/{id}/acknowledge` and `POST /api/v1/payments/{id}/acknowledge`:
     - Counterparty verifies received payment. If asserted by `FACILITY`, only the collector can acknowledge. If asserted by `COLLECTOR`, only facility members can acknowledge.
     - **Self-Acknowledgement Prohibited**: An asserter attempting to acknowledge their own payment receives HTTP 403 Forbidden.
     - Transitions state to `ACKNOWLEDGED`, sets `counterparty_ack_by` and `ack_at`. Emits `PAYMENT_ACKNOWLEDGED`.
   - `POST /payments/{id}/dispute` and `POST /api/v1/payments/{id}/dispute`:
     - Participant records dispute with mandatory reason string (e.g. counterfeit notes, unpaid envelope).
     - Transitions state to `DISPUTED`. Disputed amounts are highlighted in the ledger and prevent transaction closure. Emits `PAYMENT_DISPUTED`.

3. **Partial Dues, Duplicate Idempotency, and Reversals (`R-PAY-02`, `AT-036`)**:
   - **Multiple Partial Payments**: Two or more partial receipts sum accurately into `acknowledged_paid_paise` without double counting.
   - **Duplicate-Safe Idempotent Outcome**: Resubmission of an identical payment assertion ID and amount returns HTTP 200 with the existing record, preserving ledger balances and avoiding duplicate event emission. Reusing the ID with a different amount returns HTTP 409 Conflict.
   - **Append-Only Reversals (`POST /payments/{id}/reverse`)**:
     - When a payment is countermanded or corrected, the original entry transitions to `state = 'REVERSED'` with `reason`.
     - An offsetting reversal entry is appended linking `reversal_of = original.id`.
     - Neither entry is deleted from the database.
     - The transaction balance immediately recalculates: reversed amounts are excluded from `acknowledged_paid_paise`, restoring outstanding dues. Emits `PAYMENT_REVERSED`.

4. **Transaction Closure Invariants (`R-PAY-02`, `AT-036`)**:
   - `POST /transactions/{id}/close` and `POST /api/v1/transactions/{id}/close`:
     - Closes transaction and associated lot ONLY when all three invariants hold simultaneously:
       1. **Confirmed Receipt**: Handover exists and has `status == 'CONFIRMED'`. If unconfirmed or in-transit, returns HTTP 409 Conflict.
       2. **Settled Payment**: `remaining_due_paise == 0` (`acknowledged_paid_paise >= gross_due_paise`). Outstanding dues return HTTP 409 Conflict ("Outstanding dues of X paise remain").
       3. **Zero Active Disputes**: Zero payment entries in `DISPUTED` state, and handover is not marked disputed. Returns HTTP 409 Conflict.
     - When valid: `tx.lifecycle = 'CLOSED'`, `lot.status = 'CLOSED'`. Emits `TRANSACTION_CLOSED`.

5. **Collector Earnings Reconciliation & Strict Demo Isolation (`R-PAY-03`, `AT-037`)**:
   - `GET /collector/earnings` and `GET /api/v1/collector/earnings`:
     - Scoped to authenticated collector (or admin specifying `collector_id`).
     - Supports `month` (e.g. `2026-09`), `from_date`, and `to_date` filters.
     - Reconciles across collector's transactions: total transaction count, closed count, gross agreed paise, acknowledged paid paise, asserted pending paise, remaining dues, and disputed amounts.
     - Returns monthly breakdown buckets (`YYYY-MM`) with freshness timestamp.
     - **Strict Demo Partition Isolation**: By default (`include_demo=False`), all demo transactions are strictly excluded from calculations (`is_demo_isolated = True`), guaranteeing that synthetic demo data never contaminates real settled collector earnings.

---

## Requirements & Acceptance Case Mapping
| Requirement | Test ID | Scope | Contributing Tasks | Status | Implementation & Evidence Summary |
|---|---|---|---|---|---|
| R-PAY-01 | AT-035 | RELEASE | T026, T027 | NOT_RUN | Cash recording without bank gateway, optional UPI reference assertion, counterparty acknowledgement, self-acknowledgement prevention, and disputes with reason verified in T026. Awaiting mobile Compose ledger UI in T027. Automated tests: `test_assert_payment_cash_success`, `test_assert_payment_upi_with_private_reference`, `test_acknowledge_payment_success`, `test_acknowledge_payment_self_acknowledgement_prohibited`, `test_dispute_payment_success`. |
| R-PAY-02 | AT-036 | RELEASE | T026, T027 | NOT_RUN | Partial payment aggregation, duplicate-safe idempotency without inflating paid total, append-only reversals linking original records without deletion, and strict closure invariants (confirmed handover, 0 dues, 0 disputes) verified in T026. Awaiting mobile Compose ledger UI in T027. Automated tests: `test_multiple_partial_payments_sum_accurately`, `test_assert_payment_idempotent_replay`, `test_reverse_payment_creates_offsetting_reversal_linking_original`, `test_close_transaction_success_when_confirmed_and_settled`, `test_close_transaction_rejected_when_dues_remain`, `test_close_transaction_rejected_when_dispute_exists`. |
| R-PAY-03 | AT-037 | RELEASE | T026, T027 | NOT_RUN | Collector earnings history, date/month filtering, reconciliation of gross agreed, acknowledged paid, asserted pending, remaining dues, and strict demo partition isolation verified in T026. Awaiting mobile Compose ledger UI in T027. Automated tests: `test_collector_earnings_filters_and_monthly_buckets`, `test_collector_earnings_strict_demo_isolation`. |
| R-DATA-04 | AT-056 | RELEASE | T026, T031, T047 | NOT_RUN | Complete lifecycle lot -> offer -> handover -> payment assertions/acknowledgement -> closure produces structured transaction export records without hand-inserted rows verified in T026. Awaiting data cards in T031 and regression suite in T047. Automated test: `test_close_transaction_success_when_confirmed_and_settled`. |

---

## Automated Test Execution Evidence
Ran pytest on `services/api/tests/test_payments.py`:
```text
$env:PYTHONPATH="d:\SahiTol;d:\SahiTol\services\api"; & C:\Python310\python.exe -m pytest services/api/tests/test_payments.py -v

============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1, pluggy-1.6.0 -- C:\Python310\python.exe
rootdir: D:\SahiTol\services\api
configfile: pyproject.toml
plugins: anyio-4.14.1, langsmith-0.10.6, asyncio-1.4.0, cov-7.1.0, mock-3.15.1
collected 18 items

services\api\tests\test_payments.py::test_assert_payment_cash_success PASSED [  5%]
services\api\tests\test_payments.py::test_assert_payment_upi_with_private_reference PASSED [ 11%]
services\api\tests\test_payments.py::test_assert_payment_invalid_method_rejected PASSED [ 16%]
services\api\tests\test_payments.py::test_assert_payment_zero_or_negative_amount_rejected PASSED [ 22%]
services\api\tests\test_payments.py::test_assert_payment_forbidden_for_non_participant PASSED [ 27%]
services\api\tests\test_payments.py::test_assert_payment_idempotent_replay PASSED [ 33%]
services\api\tests\test_payments.py::test_assert_payment_conflicting_id_rejected PASSED [ 38%]
services\api\tests\test_payments.py::test_acknowledge_payment_success PASSED [ 44%]
services\api\tests\test_payments.py::test_acknowledge_payment_self_acknowledgement_prohibited PASSED [ 50%]
services\api\tests\test_payments.py::test_dispute_payment_success PASSED [ 55%]
services\api\tests\test_payments.py::test_reverse_payment_creates_offsetting_reversal_linking_original PASSED [ 61%]
services\api\tests\test_payments.py::test_multiple_partial_payments_sum_accurately PASSED [ 66%]
services\api\tests\test_payments.py::test_close_transaction_success_when_confirmed_and_settled PASSED [ 72%]
services\api\tests\test_payments.py::test_close_transaction_rejected_when_dues_remain PASSED [ 77%]
services\api\tests\test_payments.py::test_close_transaction_rejected_when_handover_unconfirmed PASSED [ 83%]
services\api\tests\test_payments.py::test_close_transaction_rejected_when_dispute_exists PASSED [ 88%]
services\api\tests\test_payments.py::test_collector_earnings_filters_and_monthly_buckets PASSED [ 94%]
services\api\tests\test_payments.py::test_collector_earnings_strict_demo_isolation PASSED [100%]

======================= 18 passed, 2 warnings in 1.04s ========================
```

Full API test suite execution (177 passed, 0 failed):
```text
$env:PYTHONPATH="d:\SahiTol;d:\SahiTol\services\api"; & C:\Python310\python.exe -m pytest services/api/tests -q
177 passed, 10 warnings in 10.99s
```
