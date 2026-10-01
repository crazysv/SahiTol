# T043 Evidence: Cross-Surface Integration and Fault Acceptance

**Task:** T043 — Cross-surface integration and fault acceptance test suite  
**Status:** DONE — deterministic integration coverage and the task's physical
integration contributions are verified. Cross-task acceptance cases remain
separately tracked until their complete scopes are verified.
**Date:** 2026-10-02
**Runner:** Python 3.10.11 / pytest-9.1.1 on Windows (local dev)

## Test Run Result

```
collected 44 items
services\api\tests\test_cross_surface_integration_and_fault_acceptance.py ............................................  [100%]
======================== 44 passed, 1 warning in 4.09s ========================
```

Exit code: 0. The independent 2026-10-02 rerun completed in 3.14 seconds with
44 passed and one dependency deprecation warning. The facility-match test now
creates an authorized recycler and requires that recycler to appear in the
eligible results; it no longer accepts a 404 or merely a response-shaped body.

## Test Classes and Cases Covered

| Class | Tests | Acceptance Cases |
|---|---|---|
| TestCanonicalHashParity | 4 | AT-029, SAHITOL-JCS-1 canonical hash byte parity |
| TestAtomicDurableOutboxAndImageSurvival | 4 | AT-039, R-OFF-02 |
| TestOfflineQueueDrainAndIdempotency | 6 | AT-039, R-SYNC-01, R-SYNC-02 |
| TestVersionedConflictsAndDependencyOrder | 4 | R-SYNC-03, optimistic concurrency |
| TestPaymentIntegrityAndReceiptLedger | 4 | AT-050, R-PAY-01 through R-PAY-04 |
| TestQueueVisibilityAndSupportReference | 5 | AT-039, R-SYNC-05 |
| TestEndToEndCollectorRecyclerLedgerAdmin | 17 | AT-010, AT-019, AT-022, AT-065, AT-077 |

## Key Fixes Applied to Test Suite

The test file was updated to align with implemented API shapes:

1. **Facility model** — removed non-existent fields (`verified`, `verification_level` on Facility, `authorized_route`/`granted_by` on FacilityAuthorization, `role` on FacilityUser, `max_weight_kg`/`accepts_batteries` on FacilityOperation); replaced with correct fields (`facility_name`, `address_public`, `district`, `state`, `active`; `route`, `authority`, `reference`, `status`, `verification_level`; `membership_role`, `active`; `accepting_status`).

2. **Handover proposal** — corrected endpoint from `/api/v1/handovers/propose` → `POST /api/v1/handovers`; added required `id` field; fixed response parsing (direct object, not `data`-wrapped); fixed `confirm` body to include `expected_version` and `proposal_hash`.

3. **Version conflict** — changed command from `MARK_COLLECTED` (unknown) to `UPDATE_DRAFT` (valid sync command that enforces `expected_version`).

4. **Batch applied_count** — removed assertion for non-existent `applied_count` field; now verifies `results` list contains at least one `APPLIED` outcome.

5. **Lot list endpoint** — `/api/v1/lots` returns a plain JSON array; test now handles both plain list and wrapped shapes.

6. **Lot collect** — switched from REST `POST /lots/{id}/collect` (requires request body) to sync batch `COLLECT_LOT` command with `expected_version=1`.

7. **Matching endpoint** — corrected from `GET` to `POST /api/v1/lots/{lot_id}/matches`.

8. **Admin quality flags** — corrected URL from `/api/v1/quality/flags` → `/api/v1/admin/quality-flags`; response is a plain list.

9. **Reference bootstrap** — corrected expected key from `data`/`version` to `metadata`/`materials`/`categories`.

10. **Collector ownership identity** — sync-created lots correctly store the
    collector-profile UUID, whereas access tokens identify the user UUID.
    Corrected lot listing, editing and matching ownership checks to compare the
    lot to `current_user.collector.id`. A newly created lot now appears in its
    own collector index and returns matching candidates rather than a false
    “another collector's lot” rejection.

## Constraints Verified

- ✅ Integer paise arithmetic — no floating-point drift
- ✅ Non-EPR statutory notice present on handover receipts
- ✅ Demo data isolation — demo lots excluded from admin real metrics
- ✅ Canonical hash immutability — proposal hash unchanged after confirmation
- ✅ Optimistic concurrency — stale `expected_version` returns CONFLICT outcome
- ✅ Idempotency — duplicate operation_id returns ALREADY_APPLIED
- ✅ Dependency ordering — dependency-blocked ops return DEPENDENCY_PENDING

## Physical Integration Supplement (2026-10-02)

- CPH2781 ran the collector debug build against the fresh local Docker stack on
  the same Wi-Fi. The API recorded successful demo authentication and live
  facility-directory responses; a deployed-only lot returned the expected
  isolated-local 404.
- A force-stop/relaunch preserved 10 saved lots and all 13 existing
  `NEEDS_REPAIR` queued legacy records. No row was discarded or retried as a
  consequence of the verification.
- T044 supplies the complementary physical offline/background/camera/GPS and
  two-device handover scenarios; T025 supplies the server-backed confirmation.

## Scope boundary

The deterministic tests use an isolated database and the physical checks use
the owner devices. Together they complete T043's integration contribution; no
single task claims the whole release acceptance by itself. Remaining cross-task
acceptance cases retain their canonical `NOT_RUN` status until their complete
required evidence exists.
