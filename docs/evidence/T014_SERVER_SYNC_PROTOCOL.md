# Test Evidence: T014 Implement Server Synchronization Protocol

## Metadata
- **Task ID**: T014
- **Phase**: Stage 2 (Offline Core & WorkManager Synchronization)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Reviewer**: SahiTol Offline Synchronization & Protocol Integrity Working Group

## Context & Objectives
Implements the durable offline server synchronization protocol as specified in `docs/17_OFFLINE_SYNC.md` and `docs/16_API_CONTRACT.md`, addressing:
- **Batch Push Contract (`POST /api/v1/sync/batch` & alias `/push`)**:
  - Accepts at most 50 operations per batch envelope (`{device_id, operations: [...]}`), rejecting oversized batches with HTTP 422 `BATCH_SIZE_EXCEEDED`.
  - Normalizes wire envelope format and Android Room field mappings (`owner_user_id->account_id`, `command_type->command`, `base_server_version->expected_version`, `payload_json->payload`, `dependency_operation_ids->depends_on`, `status->state`).
  - Emits per-operation outcomes (`APPLIED`, `ALREADY_APPLIED`, `RETRY`, `AUTH_REQUIRED`, `CONFLICT`, `REJECTED`, `DEPENDENCY_PENDING`) with server versions, entity IDs, and detailed error codes under HTTP 200 for authenticated batches.
- **Atomic Idempotency Storage (`sync_operations`)**:
  - Atomically claims `(actor_id, operation_id)` in `sync_operations` with canonical SHA-256 payload fingerprints (`SAHITOL-JCS-1`).
  - Proves that a simulated crash-after-commit / ACK loss and subsequent resend returns `outcome="ALREADY_APPLIED"` with cached durable results and server version, producing **exactly one domain effect** (no duplicate lots, events, or observations).
  - Detects and rejects operation ID reuse with a different payload, returning `outcome="CONFLICT"` with error code `IDEMPOTENCY_KEY_REUSED` without mutating existing state.
  - Enforces actor authorization, preventing an unauthorized actor from replaying another user's stored operation (`AUTH_FORBIDDEN`).
- **Dependency Ordering & Mixed-Success Batches**:
  - Processes batch operations with dependency checks: dependent operations wait on parent operations applied earlier in the batch or committed in `sync_operations`.
  - Validates that parent operation failure halts dependent children (`outcome="DEPENDENCY_PENDING"`, code `DEPENDENCY_FAILED`), while independent sibling operations in the same batch execute, succeed, and commit (`outcome="APPLIED"`).
  - Operations referencing unknown or uncommitted dependencies return `DEPENDENCY_PENDING` with code `DEPENDENCY_NOT_SATISFIED`.
- **Optimistic Version Concurrency**:
  - Validates `expected_version` against the current entity aggregate version in the database.
  - Mismatched versions return `outcome="CONFLICT"` with code `VERSION_CONFLICT` and current server version, preserving the client's local draft/proposal without overwriting server state.
- **Delta Pull Contract (`GET /api/v1/sync/changes` & alias `/pull`)**:
  - Provides incremental deltas and tombstones based on opaque monotonic sequence cursors (`sahitol_cur_v1:<seq>`).
  - Delivers `operation="UPSERT"` with role-scoped redacted projections and `operation="DELETE"` with `data=None` (tombstones) for cancelled/deleted entities.
  - Enforces role and user visibility scoping: collectors receive only public, reference, and their own scoped changes; administrators receive all changes.
  - Returns HTTP 410 Gone (`CURSOR_EXPIRED`) on malformed or corrupted cursors to trigger full client rebootstrap.

## Requirements & Acceptance Case Mapping
| Requirement | Test ID | Scope | Contributing Tasks | Implementation & Evidence Summary |
|---|---|---|---|---|
| R-OFF-03 | AT-040 | RELEASE | T014, T043 | Resend an operation after server commit/ACK loss and in mixed-success batches: each accepted effect occurs once (`ALREADY_APPLIED`), different payload with reused ID conflicts (`IDEMPOTENCY_KEY_REUSED`), successful siblings stay acknowledged while failed/dependent items return `DEPENDENCY_PENDING`. Automated tests: `test_idempotent_replay_crash_after_commit_produces_one_domain_effect`, `test_reused_operation_id_with_different_payload_conflicts`, `test_mixed_success_batch_independent_sibling_succeeds`. **PASS**. |
| R-OFF-04 | AT-041 | RELEASE | T014, T015, T043 | Out-of-order and dependent lot/media operations wait on parents (`DEPENDENCY_PENDING`); concurrent changes return current server version without erasing local proposal (`VERSION_CONFLICT`); reference and entity tombstones update caches with `data=None` while historical snapshots remain intact. Automated tests: `test_dependency_ordering_within_batch`, `test_missing_uncommitted_dependency_waits`, `test_optimistic_concurrency_version_conflict`, `test_pull_changes_tombstones_on_delete`. |

## Observable Artifact Outputs
1. **FastAPI Synchronization Router (`services/api/app/routers/sync.py`)**:
   - `POST /api/v1/sync/batch` & `POST /api/v1/sync/push`: Full batch push implementation with nested database savepoints, payload canonical hashing (`SAHITOL-JCS-1`), dependency resolution, version conflict detection, and atomic `sync_operations` recording.
   - `GET /api/v1/sync/changes` & `GET /api/v1/sync/pull`: High-water cursor-based delta pull delivering incremental entity upserts and deletion tombstones, bounded by authenticated visibility scopes.
   - `encode_cursor` & `decode_cursor`: Monotonic sequence cursor encoding with HTTP 410 `CURSOR_EXPIRED` enforcement.

2. **Schema & Model Compatibility (`services/api/app/db/models/audit.py` & `tests/test_db.py`)**:
   - Configured `SyncChange.sequence` with `BigInteger().with_variant(Integer, "sqlite")` to support standard autoincrement sequence allocation across both PostgreSQL and SQLite test environments.
   - Registered `SyncOperation` and `LotImage` in the shared test engine harness.

3. **Automated Test Suite (`services/api/tests/test_sync.py`)**:
   - 16 comprehensive automated unit and integration tests verifying:
     - `test_sync_batch_push_success_and_domain_effects`: Standard single-operation draft lot creation with full database persistence.
     - `test_idempotent_replay_crash_after_commit_produces_one_domain_effect`: Proves crash-after-commit retry returns `ALREADY_APPLIED` and leaves exactly 1 lot in the database.
     - `test_reused_operation_id_with_different_payload_conflicts`: Reused ID with altered payload returns `CONFLICT` (`IDEMPOTENCY_KEY_REUSED`) without mutating stored data.
     - `test_foreign_user_cannot_replay_operation`: Isolation check preventing cross-actor replay attacks.
     - `test_payload_sha256_verification`: Cryptographic check verifying declared `payload_sha256` against canonical JCS hash.
     - `test_dependency_ordering_within_batch`: Topologically ordered chain (create v1 -> update v2 -> collect v3) succeeds sequentially.
     - `test_mixed_success_batch_independent_sibling_succeeds`: Independent sibling lot succeeds while invalid parent and dependent child fail gracefully.
     - `test_missing_uncommitted_dependency_waits`: Unknown dependency returns `DEPENDENCY_PENDING`.
     - `test_optimistic_concurrency_version_conflict`: Stale `expected_version` returns `CONFLICT` (`VERSION_CONFLICT`) without overwriting newer version.
     - `test_batch_size_limit_enforced`: Batch with 51 operations rejected with HTTP 422 `BATCH_SIZE_EXCEEDED`.
     - `test_price_observation_sync_operation`: Synchronization of attributed price observations with `PENDING_REVIEW` state.
     - `test_pull_changes_incremental_delta_and_cursors`: Monotonic cursor navigation and pagination.
     - `test_pull_changes_tombstones_on_delete`: Deletion tombstones return `operation="DELETE"` and `data=None`.
     - `test_pull_changes_cursor_expired_410`: Corrupted cursor triggers HTTP 410 `CURSOR_EXPIRED`.
     - `test_pull_changes_role_scoping`: Collector isolation vs. administrator global visibility.
     - `test_push_and_pull_aliases`: Verification of backward-compatible `/push` and `/pull` route aliases.

## Test Verification Output
```text
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\SahiTol\services\api
configfile: pyproject.toml
plugins: anyio-4.14.1, langsmith-0.10.6, asyncio-1.4.0, cov-7.1.0, mock-3.15.1
asyncio: mode=auto, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 16 items

services\api\tests\test_sync.py ................                         [100%]

======================= 16 passed, 2 warnings in 0.81s ========================
```

Full API test suite verification:
```text
collected 99 items

services\api\tests\test_auth.py .............                            [ 13%]
services\api\tests\test_canonical.py .                                   [ 14%]
services\api\tests\test_facilities.py ...............                    [ 29%]
services\api\tests\test_health.py ..                                     [ 31%]
services\api\tests\test_materials.py .........                           [ 40%]
services\api\tests\test_media.py ........                                [ 48%]
services\api\tests\test_price_pipeline.py ..............                 [ 62%]
services\api\tests\test_pricing.py ...                                   [ 65%]
services\api\tests\test_reference.py ......                              [ 71%]
services\api\tests\test_schema.py ......                                 [ 77%]
services\api\tests\test_security.py ...                                  [ 80%]
services\api\tests\test_storage.py ...                                   [ 83%]
services\api\tests\test_sync.py ................                         [100%]

======================= 99 passed, 5 warnings in 8.10s ========================
```
