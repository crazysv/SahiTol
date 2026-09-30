# Test Evidence: T023 Implement Handover Proposals and Confirmations

## Metadata
- **Task ID**: T023
- **Phase**: Stage 4 (Handover, Payments & Verification)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Reviewer**: SahiTol Handover & Core Platform Working Group

## Context & Objectives
Implements pending handover proposal submission, canonical SAHITOL-JCS-1 SHA-256 payload and hash verification, authenticated recycler confirmation, collector acknowledgement of revised terms, duplicate-safe idempotent outcomes, disputes without fact overwriting, unconfirmed proposal voiding, versioned platform receipts with mandatory statutory non-EPR disclaimers, and public capability-token-based redacted verification conforming to [16_API_CONTRACT.md](../16_API_CONTRACT.md) lines 63–75, [04_APPFLOW.md](../04_APPFLOW.md) lines 60–81, [17_OFFLINE_SYNC.md](../17_OFFLINE_SYNC.md), and [22_REGULATORY_SAFETY.md](../22_REGULATORY_SAFETY.md):

1. **Client Proposal Submission & Canonical Hash Verification (`R-HAND-01`, `R-HAND-03`, `AT-029`, `AT-031`)**:
   - `POST /handovers` and `POST /api/v1/handovers`: Collector submits client proposal with `handover_id`, `transaction_id`, `lot_id`, `collector_id`, `facility_id`, `agreed_terms_hash`, material snapshot, weight snapshot, value snapshot, location snapshot, and media references.
   - **Canonical Hash Verification**: Computes SHA-256 over SAHITOL-JCS-1 canonical JSON format (`compute_canonical_hash`). The computed hash is checked against `req.proposal_hash`. Any altered byte or mismatch results in HTTP 409 Conflict.
   - **Canonical Fixture Parity**: Verified that `compute_canonical_hash` on [`docs/planning/handover_fixture.json`](../planning/handover_fixture.json) yields the exact frozen digest: `a091623365372138e72b1d767cca58ac80c59667b59b86f511ebf11b64eb783f`.
   - **Duplicate-Safe Idempotent Outcome (`R-HAND-01`)**: Duplicate submission of an identical proposal returns HTTP 200 with the stored record without creating redundant rows or reissuing tokens. Submission with the same ID but a different hash returns HTTP 409 Conflict.
   - **Unguessable Capability Token**: Generates a 256-bit cryptographic URL-safe token (`secrets.token_urlsafe(32)`), stores only its SHA-256 digest (`public_token_hash`) in the database, and returns the plaintext capability token in the 201 response.
   - Advances lot state to `HANDED_OVER` and transaction lifecycle to `IN_TRANSIT`. Emits append-only domain event `HANDOVER_PROPOSAL_CREATED`.

2. **Route-Aware Eligibility & Battery Hard Guard (`R-REC-04`, `AT-024`)**:
   - Validates that the transaction's lot regulatory route (`BATTERY_ISOLATION` vs `AUTHORIZED_EWASTE`) is supported by the target facility's authorizations. A battery lot cannot bind or confirm at an unauthorized facility.

3. **Authenticated Recycler Confirmation (`R-HAND-02`, `R-HAND-05`, `AT-030`, `AT-033`)**:
   - `POST /handovers/{id}/confirm` and `POST /api/v1/handovers/{id}/confirm`: Authenticated facility user confirms receipt.
   - Validates that the handover is in `PENDING_CONFIRMATION` state.
   - **Exact Match Path**: When measured material, weight, and total paise match agreed terms:
     - Handover transitions directly to `CONFIRMED`.
     - Lot transitions to `RECEIVED`.
     - Transaction transitions to `CONFIRMED`.
     - Creates `HandoverConfirmation` record capturing physical inspection findings and operator ID.
     - Emits domain event `HANDOVER_CONFIRMED`.
   - **Discrepancy Flow Without Fact Overwriting (`R-HAND-05`, `AT-033`)**:
     - When measured material, weight, or total paise differ from agreed terms, the endpoint NEVER overwrites initial client facts.
     - Atomically creates a new `TermsRevision` with `proposed_by = 'FACILITY'`, linking `previous_revision_id`, and computing updated `terms_hash`.
     - Handover transitions to `PENDING_COLLECTOR_ACK` (pending explicit collector review).
     - Transaction transitions to `PENDING_REVISED_TERMS`.
     - Emits domain events `TERMS_REVISED_BY_FACILITY` and `HANDOVER_TERMS_DISCREPANCY_FLAGGED`.

4. **Collector Acknowledgement of Revised Terms (`R-OFFER-02`, `R-HAND-05`, `AT-028`, `AT-033`)**:
   - `POST /handovers/{id}/acknowledge-terms` and `POST /api/v1/handovers/{id}/acknowledge-terms`: Collector reviews facility-proposed revisions.
   - Validates `expected_terms_hash` against the latest terms revision to eliminate race conditions.
   - Sets `collector_ack_at`, transitions handover to `CONFIRMED`, lot to `RECEIVED`, and transaction to `CONFIRMED`.
   - Creates `HandoverConfirmation` and emits domain event `HANDOVER_CONFIRMED`.

5. **Documented Disputes Without Fact Overwriting (`R-HAND-05`, `AT-033`)**:
   - `POST /handovers/{id}/dispute` and `POST /api/v1/handovers/{id}/dispute`: Either participant can record a dispute with a mandatory reason.
   - Handover transitions to `DISPUTED` and transaction to `DISPUTED`.
   - Original client proposal, photos, weights, and revision chains remain intact and unaltered. Emits domain event `HANDOVER_DISPUTED`.

6. **Voiding Pending Proposals & Confirmation Invariant (`R-HAND-01`, `R-HAND-03`)**:
   - `POST /handovers/{id}/void`: Collector can void an unconfirmed proposal (`PENDING_CONFIRMATION`), reverting lot status to `ACCEPTED` and transaction lifecycle to `AGREED`.
   - **Confirmed Record Protection**: Attempting to void a `CONFIRMED` handover is strictly prohibited and returns HTTP 409 Conflict.

7. **Versioned Handover Receipt with Statutory Non-EPR Notice (`R-HAND-05`, `R-REG-01`, `AT-033`, `AT-071`)**:
   - `GET /handovers/{id}/receipt`: Returns versioned platform handover receipt including transaction ID, lot ID, canonical proposal hash, confirmation timestamp, collector display alias, facility business details, measured material, measured weight, and agreed paise.
   - **Mandatory Non-EPR Notice**: Contains the statutory disclaimer:
     `"This Digital Handover Record certifies platform receipt and material transfer only. It does not constitute a statutory EPR certificate under E-Waste (Management) Rules, 2022."`

8. **Public Redacted Verification Endpoint (`R-HAND-04`, `AT-032`)**:
   - `GET /verify/{public_token}`: Unauthenticated public endpoint accessed via QR code link.
   - Looks up handover via SHA-256 hash of the unguessable public capability token.
   - Returns redacted summary: `handover_id`, `status`, `occurred_at`, `facility_name`, `material_id`, `regulatory_route`, `weight_kg`, `proposal_hash`, and `non_epr_notice`.
   - **Zero PII & Financial Disclosure**: Strictly omits phone numbers, exact GPS coordinates, collector personal identifiers, photo URLs, and financial settlement/paise amounts.
   - Unguessable or invalid token returns HTTP 404 Not Found.

---

## Requirements & Acceptance Case Mapping
| Requirement | Test ID | Scope | Contributing Tasks | Status | Implementation & Evidence Summary |
|---|---|---|---|---|---|
| R-REC-04 | AT-024 | RELEASE | T019, T023 | PASS | Route-aware eligibility and battery isolation invariant verified: battery lots cannot match or confirm at general e-waste facilities lacking battery authorizations. Incompatible materials, unverified registrations, or weight violations exclude before ranking and confirmation. Automated tests: `test_create_directed_lot_request_battery_isolation_hard_guard`, `test_create_directed_lot_request_battery_facility_compatible` in `test_trade.py`. |
| R-OFFER-02 | AT-028 | RELEASE | T021, T023 | PASS | Single-active-agreement invariant under race conditions; cached expired offer cannot silently bind; price board independence; atomic creation of `Transaction` and initial `TermsRevision`; material/weight/price changes require explicit acknowledgement via `POST /handovers/{id}/acknowledge-terms`. Automated tests: `test_simultaneous_acceptance_leaves_only_one_agreement`, `test_expired_offer_cannot_bind`, `test_confirm_handover_measured_discrepancy_requires_collector_ack`. |
| R-HAND-01 | AT-029 | RELEASE | T023, T024 | NOT_RUN | Backend proposal validation, canonical SAHITOL-JCS-1 hash verification, idempotent replay, and tamper resistance verified in T023. Awaiting mobile Compose QR and offline proposal UI in T024. Automated tests: `test_create_handover_proposal_success`, `test_create_handover_idempotent_replay`, `test_create_handover_hash_mismatch_rejected`. |
| R-HAND-03 | AT-031 | RELEASE | T023, T024, T043 | NOT_RUN | Canonical hash utility matches frozen fixture `docs/planning/handover_fixture.json` (`a09162336537...`); one altered byte invalidates digest; append-only domain event lineage verified in T023. Awaiting Kotlin parity in T024 and test runner in T043. Automated tests: `test_verify_hash_utility_matches_documented_handover_fixture`, `test_create_handover_hash_mismatch_rejected`. |
| R-HAND-04 | AT-032 | RELEASE | T023, T025, T040 | NOT_RUN | Capability token hashing, unauthenticated public verification endpoint with strict PII/GPS/finance redaction and statutory non-EPR notice verified in T023. Awaiting payments in T025 and public verification web view in T040. Automated tests: `test_public_verification_endpoint_redacted_pii_and_finance`, `test_invalid_public_token_returns_404`. |
| R-HAND-05 | AT-033 | RELEASE | T023, T025, T027, T028 | NOT_RUN | Measured weight/grade/price discrepancies preserve original client facts, create `TermsRevision` with `proposed_by = 'FACILITY'`, and require explicit collector acknowledgement; documented disputes preserve history verified in T023. Awaiting payments in T025 and UI in T027/T028. Automated tests: `test_confirm_handover_measured_discrepancy_requires_collector_ack`, `test_dispute_handover_records_dispute_without_rewriting_facts`. |
| R-DATA-04 | AT-056 | RELEASE | T014, T023, T031 | NOT_RUN | Handover receipt immutability, revision chain traceability, and statutory non-EPR notice verified in T023. Awaiting offline sync in T014 and data cards in T031. Automated test: `test_handover_receipt_includes_statutory_non_epr_notice`. |

---

## Automated Test Execution Evidence
Ran pytest on `services/api/tests/test_handovers.py`:
```text
$env:PYTHONPATH="d:\SahiTol;d:\SahiTol\services\api"; & C:\Python310\python.exe -m pytest services/api/tests/test_handovers.py -v

============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1, pluggy-1.6.0 -- C:\Python310\python.exe
rootdir: D:\SahiTol\services\api
configfile: pyproject.toml
plugins: anyio-4.14.1, langsmith-0.10.6, asyncio-1.4.0, cov-7.1.0, mock-3.15.1
collected 13 items

services\api\tests\test_handovers.py::test_verify_hash_utility_matches_documented_handover_fixture PASSED [  7%]
services\api\tests\test_handovers.py::test_create_handover_proposal_success PASSED [ 15%]
services\api\tests\test_handovers.py::test_create_handover_idempotent_replay PASSED [ 23%]
services\api\tests\test_handovers.py::test_create_handover_hash_mismatch_rejected PASSED [ 30%]
services\api\tests\test_handovers.py::test_create_handover_forbidden_for_other_collector PASSED [ 38%]
services\api\tests\test_handovers.py::test_confirm_handover_exact_match_success PASSED [ 46%]
services\api\tests\test_handovers.py::test_confirm_handover_measured_discrepancy_requires_collector_ack PASSED [ 53%]
services\api\tests\test_handovers.py::test_dispute_handover_records_dispute_without_rewriting_facts PASSED [ 61%]
services\api\tests\test_handovers.py::test_void_pending_handover_reverts_state PASSED [ 69%]
services\api\tests\test_handovers.py::test_void_confirmed_handover_prohibited PASSED [ 76%]
services\api\tests\test_handovers.py::test_handover_receipt_includes_statutory_non_epr_notice PASSED [ 84%]
services\api\tests\test_handovers.py::test_public_verification_endpoint_redacted_pii_and_finance PASSED [ 92%]
services\api\tests\test_handovers.py::test_invalid_public_token_returns_404 PASSED [100%]

======================== 13 passed, 1 warning in 0.81s ========================
```

Full API test suite execution (159 passed, 0 failed):
```text
$env:PYTHONPATH="d:\SahiTol;d:\SahiTol\services\api"; & C:\Python310\python.exe -m pytest services/api/tests -q
159 passed, 9 warnings in 11.43s
```
