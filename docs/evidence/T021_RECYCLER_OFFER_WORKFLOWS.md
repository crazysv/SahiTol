# Test Evidence: T021 Implement Recycler Profile and Offer Workflows

## Metadata
- **Task ID**: T021
- **Phase**: Stage 3 (Intelligence, Matching & Offers)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Reviewer**: SahiTol Trade & Recycler Console Working Group

## Context & Objectives
Implements facility-user membership linkage, self-declared operational profile management, material/rate/pickup updates with explicit provenance, directed lot requests, offer quoting, rejections with rematching, offer withdrawals, collector offer acceptance creating an immutable agreement, and race condition / single-active-agreement enforcement conforming to [16_API_CONTRACT.md](../16_API_CONTRACT.md) lines 53–61, [04_APPFLOW.md](../04_APPFLOW.md) lines 49–59, and [06_SCHEMA.md](../06_SCHEMA.md):
1. **Facility User Membership & Operational Profile (`R-REC-03`, `AT-023`)**:
   - `FacilityUser` links authenticated user IDs with authorized facilities (`OWNER`, `MANAGER`, `OPERATOR`) and `active: bool`.
   - `GET /api/v1/recycler/profile`: Retrieves public business profile, read-only legal authorizations, self-declared operational status, accepted materials with min/max weight bounds, and active quoted rates.
   - `PATCH /api/v1/recycler/profile`: Facility members can update operational fields: `pickup_status` (supports `True`, `False`, or explicitly `None` preserving unknown operational status), `service_regions`, `accepting_status` (`ACCEPTING`, `PAUSED`, `CLOSED`), material acceptance bounds, and rates.
   - **Provenance Guarantee**: Any operational update sets `source_id = f"SELF_DECLARED_USER_{user_id}"` and updates `operational_updated_at`.
   - **Authorization Tampering Prevention (`AT-023`)**: Facility users cannot modify legal authorizations (`FacilityAuthorization`), regulatory routes, or verification levels. Any attempt to pass authorization fields in profile updates is rejected with HTTP 403 Forbidden.
2. **Directed Lot Requests (`R-OFFER-01`, `AT-027`)**:
   - `POST /api/v1/lots/{lot_id}/requests`: Collector owner sends a directed request to a chosen eligible facility.
   - Revalidates lot state: Lot must be in `COLLECTED`, `LISTED`, or `MATCHED` state.
   - **Battery Isolation Hard Guard (`R-REC-04`, `AT-024`)**: If the lot carries `BATTERY_ISOLATION` route, the target facility MUST have a valid authorization for `BATTERY_ISOLATION`. Attempting to direct a battery lot to a general e-waste facility returns HTTP 422 Unprocessable Entity.
   - Advances lot state from `COLLECTED`/`LISTED` to `MATCHED` and creates a `LotRequest` with `state = 'PENDING'`. Emits append-only domain event `REQUEST_CREATED`.
   - `GET /api/v1/lots/{lot_id}/requests`: Collector can view all directed requests sent for their lot.
3. **Recycler Incoming Queue & Location Privacy (`R-OFFER-01`)**:
   - `GET /api/v1/recycler/incoming`: Facility user views permitted incoming lot requests and evidence.
   - **Privacy Protection**: Returns coarse locality (`coarse_area`), masked phone or alias (`display_alias`), materials, estimated weight, and verified media images. Raw GPS coordinates (`latitude`, `longitude`) are NEVER disclosed in incoming requests.
4. **Offer Quoting (`R-OFFER-01`)**:
   - `POST /api/v1/requests/{request_id}/offers`: Facility member quotes an offer for a pending request.
   - Supports `RATE_PER_KG` (with `rate_paise_per_kg`) and `FIXED_TOTAL` (with `fixed_total_paise`). Negative or zero amounts are rejected with HTTP 422.
   - Generates deterministic canonical `terms_hash` (SHA-256 over SAHITOL-JCS-1 JSON format).
   - Creates `Offer` in state `OPEN` and emits domain event `OFFER_CREATED`.
5. **Rejection & Collector Rematching (`R-OFFER-01`, `AT-027`)**:
   - `POST /api/v1/requests/{request_id}/reject`: Facility member rejects the request with a mandatory explanation string.
   - Request transitions to `REJECTED` and preserves history.
   - When no other open offers or pending requests exist for the lot, `lot.status` automatically reverts from `MATCHED` to `LISTED`, allowing the collector to rematch with another compatible facility (`AT-027`).
6. **Offer Withdrawal (`R-OFFER-01`)**:
   - `POST /api/v1/offers/{offer_id}/withdraw`: Facility member withdraws an open offer using optimistic concurrency (`expected_version`).
   - Offer transitions to `WITHDRAWN`. An already accepted offer cannot be withdrawn (returns HTTP 409 Conflict).
7. **Collector Offer Acceptance & Immutable Agreement (`R-OFFER-02`, `AT-028`)**:
   - `POST /api/v1/offers/{offer_id}/accept`: Collector owner accepts a live open offer providing exact `terms_hash` and `expected_version`.
   - **Atomic Mutual Agreement**:
     - Offer state transitions to `ACCEPTED`.
     - Associated `LotRequest` transitions to `ACCEPTED`.
     - All other competing open offers for the same lot are automatically transitioned to `EXPIRED`.
     - Competing pending requests for the same lot are transitioned to `EXPIRED`.
     - Lot transitions to `ACCEPTED`.
     - Creates `Transaction` with `lifecycle = 'AGREED'`, `quoted_total_paise`, `agreed_total_paise`.
     - Creates initial `TermsRevision` recording the agreed material, weight, paise, and `terms_hash`.
     - Emits domain events: `OFFER_ACCEPTED`, `TRANSACTION_CREATED`, `LOT_ACCEPTED`.
8. **Offer Expiration & Tamper Resistance (`R-OFFER-02`, `AT-028`)**:
   - **Expired Offer Guard**: If an offer's `expires_at` is in the past, acceptance is rejected with HTTP 409 Conflict ("Offer has expired and cannot bind. Please request fresh terms."). Cached expired offers cannot silently bind.
   - **Terms Hash Verification**: If the collector submits a modified or tampered `terms_hash`, acceptance is rejected with HTTP 409 Conflict ("Terms hash mismatch").
9. **Simultaneous Acceptance / Race Condition Invariant (`R-OFFER-02`, `AT-028`)**:
   - Enforces the invariant: "Two simultaneous acceptances leave one active agreement".
   - If two competing offers exist on a lot, accepting one automatically expires the other. Any subsequent attempt to accept the second offer fails with HTTP 409 Conflict ("Lot already has an active accepted agreement"). Exactly one active transaction is created.
10. **Price-Board Independence (`R-OFFER-02`, `AT-028`)**:
    - Subsequent price board refreshes or facility rate adjustments never mutate existing `Transaction` or `TermsRevision` agreed terms.
11. **Transaction Scoping & Retrieval**:
    - `GET /api/v1/transactions/{id}`: Restricts access strictly to the participating collector, linked facility members, and admins. Foreign users receive HTTP 403 Forbidden.
    - `GET /api/v1/recycler/transactions`: Facility members can query all their historical transactions and receipts.

---

## Requirements & Acceptance Case Mapping
| Requirement | Test ID | Scope | Contributing Tasks | Implementation & Evidence Summary |
|---|---|---|---|---|
| R-REC-03 | AT-023 | RELEASE | T012, T021 | Facility user updates rates, availability, service area, and accepted materials with provenance (`SELF_DECLARED_USER_{id}`). Authorizations and verification status remain strictly admin-controlled (tampering returns HTTP 403). Unknown operational data (pickup status) stays unknown when cleared/omitted. Automated tests: `test_recycler_profile_retrieval`, `test_recycler_profile_operational_update_and_provenance`, `test_recycler_profile_unknown_pickup_preserved`, `test_recycler_profile_authorization_tampering_prohibited`. |
| R-OFFER-01 | AT-027 | RELEASE | T021, T022 | Collector submits lot to compatible facility; linked recycler sees evidence (with coarse location privacy) and quotes or rejects; collector accepts one live offer; rejected requests preserve history and return lot to `LISTED` for rematching. Automated tests: `test_create_directed_lot_request_success`, `test_recycler_incoming_queue_and_privacy`, `test_quote_offer_rate_per_kg_and_fixed_total`, `test_recycler_reject_request_allows_collector_rematch`, `test_recycler_withdraw_offer`. |
| R-OFFER-02 | AT-028 | RELEASE | T021, T023 | Two simultaneous acceptances leave only one active agreement; cached expired offer cannot silently bind; tampered terms hash rejected; later price-board refreshes do not modify accepted terms; atomic creation of `Transaction` and initial `TermsRevision`. Automated tests: `test_collector_accept_offer_creates_atomic_transaction`, `test_expired_offer_cannot_bind`, `test_tampered_terms_hash_rejected`, `test_simultaneous_acceptance_leaves_only_one_agreement`, `test_price_board_refresh_does_not_modify_accepted_terms`. |
| R-PRICE-04 | AT-019 | RELEASE | T018, T020, T021 | View offers with dynamic expiry checking and comparable unit rates (`effective_rate_paise_per_kg`); expired rates are labelled and do not become an agreed price. Automated tests: `test_quote_offer_rate_per_kg_and_fixed_total`, `test_expired_offer_cannot_bind`. |
| R-DATA-03 | AT-055 | RELEASE | T012, T021, T029 | Facility operational updates and original regulatory registry claims remain separately attributable in separate tables (`facility_operations` vs `facility_authorizations`) with independent source attribution. Automated test: `test_recycler_profile_operational_update_and_provenance`. |

---

## Automated Test Execution Evidence
Ran pytest on `services/api/tests/test_trade.py`:
```text
$env:PYTHONPATH="d:\SahiTol;d:\SahiTol\services\api"; & C:\Python310\python.exe -m pytest services/api/tests/test_trade.py -v

============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1, pluggy-1.6.0 -- C:\Python310\python.exe
rootdir: D:\SahiTol\services\api
configfile: pyproject.toml
plugins: anyio-4.14.1, langsmith-0.10.6, asyncio-1.4.0, cov-7.1.0, mock-3.15.1
collected 19 items

services\api\tests\test_trade.py::test_recycler_profile_retrieval PASSED [  5%]
services\api\tests\test_trade.py::test_recycler_profile_operational_update_and_provenance PASSED [ 10%]
services\api\tests\test_trade.py::test_recycler_profile_unknown_pickup_preserved PASSED [ 15%]
services\api\tests\test_trade.py::test_recycler_profile_authorization_tampering_prohibited PASSED [ 21%]
services\api\tests\test_trade.py::test_create_directed_lot_request_success PASSED [ 26%]
services\api\tests\test_trade.py::test_create_directed_lot_request_battery_isolation_hard_guard PASSED [ 31%]
services\api\tests\test_trade.py::test_create_directed_lot_request_battery_facility_compatible PASSED [ 36%]
services\api\tests\test_trade.py::test_create_directed_lot_request_forbidden_for_other_collector PASSED [ 42%]
services\api\tests\test_trade.py::test_recycler_incoming_queue_and_privacy PASSED [ 47%]
services\api\tests\test_trade.py::test_quote_offer_rate_per_kg_and_fixed_total PASSED [ 52%]
services\api\tests\test_trade.py::test_quote_offer_negative_or_zero_rate_rejected PASSED [ 57%]
services\api\tests\test_trade.py::test_recycler_reject_request_allows_collector_rematch PASSED [ 63%]
services\api\tests\test_trade.py::test_recycler_withdraw_offer PASSED    [ 68%]
services\api\tests\test_trade.py::test_collector_accept_offer_creates_atomic_transaction PASSED [ 73%]
services\api\tests\test_trade.py::test_expired_offer_cannot_bind PASSED  [ 78%]
services\api\tests\test_trade.py::test_tampered_terms_hash_rejected PASSED [ 84%]
services\api\tests\test_trade.py::test_simultaneous_acceptance_leaves_only_one_agreement PASSED [ 89%]
services\api\tests\test_trade.py::test_price_board_refresh_does_not_modify_accepted_terms PASSED [ 94%]
services\api\tests\test_trade.py::test_transaction_scoping_and_history PASSED [100%]

======================= 19 passed, 2 warnings in 1.33s ========================
```

Full backend test suite:
```text
$env:PYTHONPATH="d:\SahiTol;d:\SahiTol\services\api"; & C:\Python310\python.exe -m pytest services/api/tests -q
146 passed, 9 warnings in 10.55s
```

## Traceability & Immutability Guarantees
1. **At most one active transaction per lot**: Enforced at application level via check on `Transaction.lot_id == lot.id` and `lot.status == 'ACCEPTED'` and database constraint `unique=True` on `Transaction.lot_id`.
2. **Deterministic Terms Hash**: Canonical representation using SAHITOL-JCS-1 encoding ensures that neither client nor server can alter agreed quantities, rates, or terms without invalidating `terms_hash`.
3. **Atomic Mutual Binding**: The offer acceptance updates the offer, expires all competing offers, expires pending requests, advances the lot, creates the transaction, and creates the initial terms revision within a single atomic database transaction.
4. **Read-Only Authorizations**: Authorizations are verified through official DPCC/CPCB/MPCB public records and administrative processes; facility users cannot grant or modify their own route authorizations.

## Independent re-verification (2026-10-01)

The current implementation was exercised independently with:

```text
$env:PYTHONPATH="D:\SahiTol;D:\SahiTol\services\api"
C:\Python310\python.exe -m pytest services/api/tests/test_trade.py -v
```

Result: **19 passed** in 1.68 s (two framework deprecation warnings only). This
rechecked profile provenance and authorization tampering denial; battery route
isolation; incoming-request location privacy; rate and fixed-total quoting;
rejection/rematching; withdrawal; acceptance, expiry, and terms-hash guards; the
single-active-agreement invariant; price-board immutability; and transaction
access scoping. No T021 defect was found in this run.
