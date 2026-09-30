# Test Evidence: T008 Implement Private Media Storage Adapter

## Metadata
- **Task ID**: T008
- **Phase**: Stage 1 (Data & Backend Setup)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Reviewer**: SahiTol Engineering & Media Storage Architecture

## Context & Objectives
Implements bounded private media storage adapters supporting local persistent volume mounts and private Supabase Storage, strict 2 MiB hard size limits, client-asserted SHA-256 checksum verification, PIL-based image integrity validation and automatic EXIF metadata stripping for collector privacy, bounded PDF document storage for platform receipts and Digital Handover Records, short-lived signed URL access (15-minute expiration), and missing-upload recovery.

## Requirements & Acceptance Case Mapping
| Requirement | Test ID | Scope | Contributing Tasks | Implementation & Evidence Summary |
|---|---|---|---|---|
| R-ARC-02 | AT-006 | RELEASE | T001, T006, T008 | Media objects decoupled from ephemeral API container filesystem: adapter routes files to persistent local directory (`LocalStorageAdapter`) or private bucket (`SupabaseStorageAdapter`). |
| R-LOT-02 | AT-012 | RELEASE | T008, T013, T017 | Bounded image uploads (`PUT /media/{id}/content`) enforce 2 MiB max size, validate format (JPEG/PNG/WebP/PDF), compute and verify SHA-256 checksums, and strip all EXIF metadata using Pillow before storage. |
| R-SEC-02 | AT-073 | RELEASE | T008, T040, T042 | Private media security: `GET /media/{id}/access` generates short-lived signed tokens (15-minute expiry). Unauthorized users cannot download or generate links for foreign media. All file downloads serve `Cache-Control: private, no-transform`. |

## Observable Artifact Outputs
1. **Dual Storage Adapters (`services/api/app/storage/`)**:
   - `base.py`: Abstract `StorageAdapter` defining `save`, `get`, `delete`, and `exists`.
   - `local.py`: `LocalStorageAdapter` with strict path-traversal protection (`_resolve_safe_path`), atomic writes via `tempfile.mkstemp` and `os.replace`, and 2 MiB boundary check (`MAX_MEDIA_BYTES = 2 * 1024 * 1024`).
   - `supabase.py`: `SupabaseStorageAdapter` interacting with private Supabase Storage REST API using service-role credentials and private bucket isolation.
   - `__init__.py`: Factory `get_storage_adapter()` selecting adapter based on `settings.STORAGE_BACKEND`.

2. **Media Router & Validation (`services/api/app/routers/media.py`)**:
   - `POST /media/uploads`: Stages media object, checks parent lot ownership, and returns upload instructions (`method="PUT"`, `upload_url`, `max_bytes=2097152`).
   - `PUT /media/{id}/content`: Streams upload bytes, enforces size boundary, verifies client SHA-256 against actual payload bytes, validates image stream, strips EXIF tags, extracts pixel dimensions, and persists via adapter.
   - `POST /media/{id}/complete`: Validates storage backend presence (`adapter.exists`) and updates state to `VALIDATED`. Handles missing-upload recovery with status updates.
   - `GET /media/{id}/access`: Checks object-level authorization (media owner, linked transaction facility, or admin) and generates short-lived signed access URL with 15-minute lifetime.
   - `GET /media/{id}/content`: Authenticated / signed-token streaming download returning private cache headers.

3. **FastAPI Application Factory Registration (`services/api/app/main.py`)**:
   - Registered `media.router` alongside auth, health, lots, prices, and sync.

4. **Automated Test Suite (`services/api/tests/test_media.py`)**:
   - 8 unit and integration tests verifying staging, invalid MIME rejection, oversized payload rejection, EXIF stripping, checksum mismatch rejection, complete lifecycle transition, expiring access URLs, cross-user authorization defense (R-SEC-02), and PDF storage for handover records.

## Test Verification Output
```text
python -m pytest
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\SahiTol\services\api
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.14.1, langsmith-0.10.6, asyncio-1.4.0, cov-7.1.0, mock-3.15.1
asyncio: mode=auto, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 39 items

tests\test_auth.py .............                                         [ 33%]
tests\test_canonical.py .                                                [ 35%]
tests\test_health.py ..                                                  [ 41%]
tests\test_media.py ........                                             [ 61%]
tests\test_pricing.py ...                                                [ 69%]
tests\test_schema.py ......                                              [ 84%]
tests\test_security.py ...                                               [ 92%]
tests\test_storage.py ...                                                [100%]

======================= 39 passed, 2 warnings in 4.88s ========================
```
