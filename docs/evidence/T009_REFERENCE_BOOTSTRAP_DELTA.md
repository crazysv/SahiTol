# Test Evidence: T009 Implement Versioned Reference Bootstrap and Delta APIs

## Metadata
- **Task ID**: T009
- **Phase**: Stage 1 (Data & Backend Setup)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Reviewer**: SahiTol Engineering & Offline Synchronization Architecture

## Context & Objectives
Implements the versioned reference bootstrap and delta pull synchronization APIs supporting offline client onboarding, regional filtering, policy enforcement, tombstones, and opaque sequence cursors meeting R-OFF-01. Provides a labelled bundled demo reference cache in the Android app assets (`apps/android/app/src/main/assets/reference_bootstrap_demo.json`) and `data/curated/` allowing first-time app launch in airplane mode without network connection, directly satisfying acceptance case AT-038 preconditions.

## Requirements & Acceptance Case Mapping
| Requirement | Test ID | Scope | Contributing Tasks | Implementation & Evidence Summary |
|---|---|---|---|---|
| R-OFF-01 | AT-038 | RELEASE | T009, T013, T017, T020 | `GET /api/v1/reference/bootstrap` serves versioned snapshots of categories, materials, multilingual aliases, safety guides, indicative price benchmarks, and regional verified facilities with opaque cursor. `GET /api/v1/reference/changes` serves incremental UPSERT/DELETE delta streams with HTTP 410 `CURSOR_EXPIRED` recovery. Bundled demo cache enables offline airplane mode startup. |

## Observable Artifact Outputs
1. **Reference Bootstrap Router (`services/api/app/routers/reference.py`)**:
   - `GET /api/v1/reference/bootstrap`: Delivers snapshot bundle including `metadata` (snapshot version `REF-2026-09-29-01`, timestamps, opaque cursor, expiry, region, role, is_demo), `policy` (max weight 50 metric tonnes, 30-day freshness, allowed units, disclaimer), 11 material categories, 21 materials, 139 multilingual aliases, 9 contextual safety guides with audio keys, regional price benchmarks, and regional verified facilities.
   - `GET /api/v1/reference/changes`: Delta sync endpoint decoding base64 cursors, querying `sync_changes` table, returning changes with `UPSERT` and `DELETE` (tombstone with `data=None`) operations, next cursor, and has_more flag. Malformed/corrupted cursor triggers HTTP 410 Gone (`CURSOR_EXPIRED`) to force full rebootstrap.

2. **Bundled Offline Demo Cache Generator (`scripts/generate_bundled_reference_cache.py`)**:
   - Compiles static demonstration cache containing all categories, materials, aliases, safety guides, prices, and facilities.
   - Saved to `apps/android/app/src/main/assets/reference_bootstrap_demo.json` (49,133 bytes, SHA-256: `7b287328e0f03efb4acd8a279587d6644b0f8e63aff0ad7d383e2d7410e18e69`) and `data/curated/reference_bootstrap_demo.json`.
   - Labeled with `is_demo=True` and demonstration disclaimers.

3. **Database Integration (`services/api/app/db/models/audit.py`, `services/api/tests/test_db.py`)**:
   - Configured `SyncChange` table in test database metadata to support incremental synchronization testing.

4. **Automated Test Suite (`services/api/tests/test_reference.py`)**:
   - 6 comprehensive tests verifying bootstrap payload structure, content completeness, regional facility directory filtering (Delhi-NCR vs Maharashtra), delta sync incremental changes, tombstone handling, cursor expiration (HTTP 410), and Android asset file integrity.

## Test Verification Output
```text
python -m pytest tests/test_reference.py -v
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1, pluggy-1.6.0 -- C:\Python310\python.exe
cachedir: .pytest_cache
rootdir: D:\SahiTol\services\api
configfile: pyproject.toml
plugins: anyio-4.14.1, langsmith-0.10.6, asyncio-1.4.0, cov-7.1.0, mock-3.15.1
asyncio: mode=auto, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 6 items

tests/test_reference.py::test_reference_bootstrap_payload_structure PASSED [ 16%]
tests/test_reference.py::test_reference_bootstrap_content_completeness PASSED [ 33%]
tests/test_reference.py::test_reference_bootstrap_regional_facility_filter PASSED [ 50%]
tests/test_reference.py::test_reference_changes_incremental_deltas PASSED [ 66%]
tests/test_reference.py::test_reference_changes_cursor_expired PASSED    [ 83%]
tests/test_reference.py::test_bundled_demo_cache_asset_validity PASSED   [100%]

======================== 6 passed, 1 warning in 0.40s =========================
```

Full API test suite verification:
```text
python -m pytest
======================= 54 passed, 2 warnings in 6.11s ========================
```
