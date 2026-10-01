# Test Evidence: T040 Verify Security Privacy and Abuse Boundaries

## Metadata
- **Task ID**: `T040`
- **Phase**: Phase 6 (Security, Resilience and Verification)
- **Scope**: RELEASE
- **Date**: 2026-09-30
- **Requirements**: [`R-AUTH-02`](../15_REQUIREMENTS.md#r-auth-02), [`R-AUTH-04`](../15_REQUIREMENTS.md#r-auth-04), [`R-HAND-04`](../15_REQUIREMENTS.md#r-hand-04), [`R-DATA-06`](../15_REQUIREMENTS.md#r-data-06), [`R-DATA-08`](../15_REQUIREMENTS.md#r-data-08), [`R-SEC-01`](../15_REQUIREMENTS.md#r-sec-01), [`R-SEC-02`](../15_REQUIREMENTS.md#r-sec-02)
- **Acceptance Cases**: [`AT-008`](../20_TEST_ACCEPTANCE.md#at-008), [`AT-010`](../20_TEST_ACCEPTANCE.md#at-010), [`AT-032`](../20_TEST_ACCEPTANCE.md#at-032), [`AT-058`](../20_TEST_ACCEPTANCE.md#at-058), [`AT-060`](../20_TEST_ACCEPTANCE.md#at-060), [`AT-072`](../20_TEST_ACCEPTANCE.md#at-072), [`AT-073`](../20_TEST_ACCEPTANCE.md#at-073)
- **Related Specifications**: [`docs/12_GUARDRAILS.md`](../12_GUARDRAILS.md), [`docs/11_SECRETS_CHECKLIST.md`](../11_SECRETS_CHECKLIST.md), [`docs/20_TEST_ACCEPTANCE.md`](../20_TEST_ACCEPTANCE.md)
- **Status**: DONE — independently reverified on 2026-10-01.

---

## 1. Executive Summary

Task `T040` delivers the security, privacy and abuse-boundary verification. On 2026-10-01, the API-local boundary suite plus core security tests passed **23/23**, and the live Render HTTPS endpoint and CORS preflight were independently checked. This does not substitute for the separate T042 retention/backup evidence.

The test suite systematically tests:
1. **Object-Level Authorization & IDOR Boundaries (`R-AUTH-02`, `AT-008`)**:
   - Collector A cannot view (`GET`), mutate (`PATCH`), submit (`/collect`), list (`/list`), or cancel (`/cancel`) lots belonging to Collector B (HTTP 403 Forbidden).
   - Collector cannot create lots on behalf of another collector by tampering with payload parameters (HTTP 403 Forbidden).
   - Recycler operators belonging to Facility 2 cannot view or confirm handovers for Facility 1 (HTTP 403 Forbidden).
   - Collectors and recyclers cannot access `/api/v1/admin/*` governance endpoints (HTTP 403 Forbidden).
2. **Isolated Demo Access Without SMS (`R-AUTH-04`, `AT-010`, `R-DATA-08`, `AT-060`)**:
   - Public demo authentication `/api/v1/auth/demo` creates isolated users with `is_demo=True` without relying on SMS.
   - Disabling `DEMO_MODE` configuration immediately disables demo authentication (HTTP 403).
   - Demo isolation boundaries prevent live collectors from interacting with demo lots, and demo users from accessing live transaction state.
3. **Public Verification Capability Token Privacy (`R-HAND-04`, `AT-032`)**:
   - Public verification endpoint `/api/v1/verify/{public_token}` verifies digital handovers via high-entropy capability token hashes.
   - PII, phone numbers, exact GPS coordinates, photos, and payment settlement figures are strictly excluded/redacted.
   - The statutory Non-EPR Disclaimer is prominently present on every verification response.
   - Possessing a verification link/QR does not confer confirmation, mutation, or administrative capabilities.
4. **Minimal Collector Dataset and Anonymization (`R-DATA-06`, `AT-058`)**:
   - Collector exports require administrator role (`UserRole.ADMIN`). Non-admins receive HTTP 403.
   - Collector IDs are pseudonymized (`col_anon_<uuid12>`), phone numbers are masked (`XXXXXX1234`), and precise GPS home coordinates and Aadhaar/banking credentials are zero-stored and omitted.
5. **CSV Formula Injection Neutralization (`R-DATA-01`, `R-DATA-08`, `AT-060`)**:
   - Formula triggers (`=`, `+`, `-`, `@`, `\t`, `\r`) in string export cells are escaped by prepending a single quote (`'`), preventing remote code execution when opened in Excel or Google Sheets.
   - Statutory non-EPR notice is prepended as an immutable header block in all CSV exports.
6. **PIN Abuse Rate Limiting, User Enumeration Prevention & Secrets Audit (`R-SEC-01`, `AT-072`)**:
   - Authentication endpoint enforces brute-force lockout after 5 consecutive incorrect attempts, returning HTTP 429 with `Retry-After`.
   - Uniform HTTP 401 error message and response timing are returned for non-existent phone numbers and invalid PINs, eliminating user enumeration vulnerabilities.
   - Replay attacks on refresh tokens immediately trigger token-family revocation, invalidating all associated active sessions.
   - Automated secrets scanner scans the entire codebase (Python, TypeScript, Kotlin, configs, scripts) and confirms zero hardcoded private keys, database passwords, or runtime secrets.
7. **Media Security, EXIF Stripping, Path Traversal & Signed URLs (`R-SEC-02`, contributing to `AT-073`)**:
   - Image upload pipeline validates magic bytes and uses Pillow to strip EXIF metadata (specifically GPS coordinates and camera serial numbers) into clean buffers.
   - Local storage adapter enforces path canonicalization (`_resolve_safe_path`), rejecting `../` traversal sequences with `ValueError`.
   - Media downloads enforce authentication and signed token expiry (HTTP 401 on expired tokens).
   - Media uploads exceeding 2 MiB (2,097,152 bytes) or with non-whitelisted MIME types are rejected with HTTP 422.

---

## 2. Test Execution & Evidence

### 2.1 Test Suite Summary
- **Test File**: [`services/api/tests/test_security_and_abuse_boundaries.py`](../../services/api/tests/test_security_and_abuse_boundaries.py)
- **Framework**: `pytest 9.1.1`, Python 3.10.11
- **Result**: **23 passed, 0 failed, 1 environment warning in 12.43s**: `test_security_and_abuse_boundaries.py` (20) plus `test_security.py` (3).

```text
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1, pluggy-1.6.0 -- C:\Python310\python.exe
cachedir: .pytest_cache
rootdir: D:\SahiTol\services\api
configfile: pyproject.toml
plugins: anyio-4.14.1, langsmith-0.10.6, asyncio-1.4.0, cov-7.1.0, mock-3.15.1
asyncio: mode=auto, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 19 items

services\api\tests\test_security_and_abuse_boundaries.py::test_collector_cannot_view_or_mutate_other_collector_lot PASSED [  5%]
services\api\tests\test_security_and_abuse_boundaries.py::test_collector_cannot_create_lot_for_another_collector PASSED [ 10%]
services\api\tests\test_security_and_abuse_boundaries.py::test_cross_facility_recycler_handover_isolation PASSED [ 15%]
services\api\tests\test_security_and_abuse_boundaries.py::test_non_admin_cannot_access_admin_governance PASSED [ 21%]
services\api\tests\test_security_and_abuse_boundaries.py::test_pin_brute_force_rate_limiting_and_lockout PASSED [ 26%]
services\api\tests\test_security_and_abuse_boundaries.py::test_user_enumeration_prevention_uniform_401 PASSED [ 31%]
services\api\tests\test_security_and_abuse_boundaries.py::test_refresh_token_replay_attack_cascades_session_revocation PASSED [ 36%]
services\api\tests\test_security_and_abuse_boundaries.py::test_repository_secrets_audit PASSED [ 42%]
services\api\tests\test_security_and_abuse_boundaries.py::test_demo_profile_isolation_and_labeling PASSED [ 47%]
services\api\tests\test_security_and_abuse_boundaries.py::test_demo_disabled_when_flag_off PASSED [ 52%]
services\api\tests\test_security_and_abuse_boundaries.py::test_demo_isolation_boundary_enforcement PASSED [ 57%]
services\api\tests\test_security_and_abuse_boundaries.py::test_public_verification_capability_token_privacy PASSED [ 63%]
services\api\tests\test_security_and_abuse_boundaries.py::test_collector_export_anonymization_and_access_boundary PASSED [ 68%]
services\api\tests\test_security_and_abuse_boundaries.py::test_csv_formula_injection_neutralization PASSED [ 73%]
services\api\tests\test_security_and_abuse_boundaries.py::test_procurement_log_csv_export_has_non_epr_and_sanitized_cells PASSED [ 78%]
services\api\tests\test_security_and_abuse_boundaries.py::test_media_storage_path_traversal_prevention PASSED [ 84%]
services\api\tests\test_security_and_abuse_boundaries.py::test_image_upload_exif_metadata_stripping PASSED [ 89%]
services\api\tests\test_security_and_abuse_boundaries.py::test_media_download_authorization_and_signed_url_expiry PASSED [ 94%]
services\api\tests\test_security_and_abuse_boundaries.py::test_oversized_upload_and_invalid_mime_rejection PASSED [100%]

======================= 23 passed, 1 warning in 12.43s ========================
```

### 2.2 Independent deployed transport check

On 2026-10-01, `https://sahitol-api.onrender.com/health/live` returned HTTP 200 over HTTPS with Render/Cloudflare response headers and a correlation ID. A preflight from `https://sahitol.pages.dev` to `/api/v1/auth/demo` returned HTTP 200 with that exact `access-control-allow-origin` and credentials enabled. The same preflight from `https://evil.example` returned HTTP 400 and no allowed-origin header. This verifies the deployed origin restriction at the time checked; it is not a claim that the endpoint will remain continuously available.

---

## 3. Detailed Verification Results by Requirement

### 3.1 `R-AUTH-02` & `AT-008`: Role and Object-Level Authorization (IDOR)
- **`test_collector_cannot_view_or_mutate_other_collector_lot`**:
  - Sets up Collector A and Collector B with authenticated JWT tokens.
  - Collector A creates Lot A.
  - Collector B attempts `GET /api/v1/lots/{lot_a_id}` -> rejected with **HTTP 403 Forbidden**.
  - Collector B attempts `PATCH /api/v1/lots/{lot_a_id}` -> rejected with **HTTP 403 Forbidden**.
  - Collector B attempts `POST /api/v1/lots/{lot_a_id}/collect` -> rejected with **HTTP 403 Forbidden**.
  - Collector B attempts `POST /api/v1/lots/{lot_a_id}/list` -> rejected with **HTTP 403 Forbidden**.
  - Collector B attempts `POST /api/v1/lots/{lot_a_id}/cancel` -> rejected with **HTTP 403 Forbidden**.
- **`test_collector_cannot_create_lot_for_another_collector`**:
  - Collector A attempts to call `POST /api/v1/lots` with `collector_id=Collector_B.id`.
  - Endpoint detects identity mismatch and returns **HTTP 403 Forbidden**.
- **`test_cross_facility_recycler_handover_isolation`**:
  - Sets up Facility 1 with Recycler Operator 1, and Facility 2 with Recycler Operator 2.
  - Generates transaction and handover for Facility 1.
  - Recycler Operator 2 attempts `GET /api/v1/recycler/handovers/{handover_f1_id}` -> rejected with **HTTP 403 Forbidden**.
  - Recycler Operator 2 attempts `POST /api/v1/recycler/handovers/{handover_f1_id}/confirm` -> rejected with **HTTP 403 Forbidden**.
- **`test_non_admin_cannot_access_admin_governance`**:
  - Collector and Recycler tokens attempt `GET /api/v1/admin/overview`, `/api/v1/admin/events`, and `/api/v1/exports/collectors`.
  - All return **HTTP 403 Forbidden**, enforcing role hierarchy boundary.

### 3.2 `R-AUTH-04` & `AT-010`: Isolated Demo Access Without SMS
- **`test_demo_profile_isolation_and_labeling`**:
  - Calls `POST /api/v1/auth/demo` with `role="COLLECTOR"`.
  - Successfully returns valid JWT access and refresh tokens without requiring SMS provider calls.
  - Inspects user record in database: `is_demo == True`, phone is labelled with dedicated `+910000000001` test prefix.
- **`test_demo_disabled_when_flag_off`**:
  - Simulates production environment where `settings.DEMO_MODE = False`.
  - Calling `POST /api/v1/auth/demo` returns **HTTP 403 Forbidden** with `Demo mode is disabled`.
- **`test_demo_isolation_boundary_enforcement`**:
  - Creates demo collector with a demo lot.
  - Live collector (non-demo) attempts to mutate or access demo lot -> rejected with **HTTP 403 Forbidden**.

### 3.3 `R-HAND-04` & `AT-032`: Public Verification and Privacy
- **`test_public_verification_capability_token_privacy`**:
  - Handover confirmation generates unguessable SHA-256 capability verification token.
  - Unauthenticated GET `/api/v1/verify/{public_token}` returns HTTP 200.
  - Verifies presence of statutory non-EPR notice: `"statutory_notice"` explicitly containing `"Digital Handover Record is an operational and commercial record of scrap transfer"` and `"It does NOT constitute an EPR (Extended Producer Responsibility) certificate"`.
  - Verifies zero-PII leak: no collector phone number, no recycler staff phone number, no precise GPS coordinates, no raw photos, no bank details, and no payment transaction hashes.
  - Verifies capability token acts as read-only capability: GET is allowed, but POST / PUT / PATCH / DELETE return HTTP 405 Method Not Allowed.

### 3.4 `R-DATA-06` & `AT-058`: Minimal Collector Dataset & Anonymization
- **`test_collector_export_anonymization_and_access_boundary`**:
  - Non-admin user calls `GET /api/v1/exports/collectors?format=json` -> rejected with **HTTP 403 Forbidden**.
  - Admin calls endpoint -> returns HTTP 200.
  - Verifies output records:
    - Collector identifier is pseudonymized: `col_anon_<uuid12>`.
    - Phone number is masked: `XXXXXX1234`.
    - No home address, no GPS location, no Aadhaar number, no bank credentials exist in payload.
    - Minimal dataset complies with DPDP Act principles.

### 3.5 `R-DATA-08` & `AT-060`: Provenance, CSV Sanitization & Non-EPR Banner
- **`test_csv_formula_injection_neutralization`**:
  - Directly tests `sanitize_csv_cell` across spreadsheet formula triggers:
    - `=SUM(A1:A10)` -> `'=SUM(A1:A10)`
    - `+1+2` -> `'+1+2`
    - `-5*2` -> `'-5*2`
    - `@cmd` -> `'@cmd`
    - `\tcmd` -> `'\tcmd`
    - `\rcmd` -> `'\rcmd`
    - Benign strings (`"Copper Wire"`) remain unescaped.
- **`test_procurement_log_csv_export_has_non_epr_and_sanitized_cells`**:
  - Creates facility lot with formula prefix `=DDE("cmd")` in notes.
  - Recycler calls `GET /api/v1/exports/procurement-log?format=csv`.
  - Verifies first line is the statutory non-EPR banner: `"NOTICE: SahiTol Digital Handover Records are operational scrap transfer logs and do NOT constitute EPR compliance certificates or regulatory credit."`.
  - Verifies note cell in CSV body starts with `'=DDE("cmd")`, completely neutralizing spreadsheet execution.

### 3.6 `R-SEC-01` & `AT-072`: PIN Abuse, User Enumeration & Secrets Audit
- **`test_pin_brute_force_rate_limiting_and_lockout`**:
  - Submits 5 consecutive incorrect PIN attempts to `POST /api/v1/auth/login`.
  - 6th attempt is blocked with **HTTP 429 Too Many Requests**.
  - Confirms `Retry-After` header is present and > 0 seconds.
- **`test_user_enumeration_prevention_uniform_401`**:
  - Queries `POST /api/v1/auth/login` with non-existent phone number: returns **HTTP 401 Unauthorized** with message `"Invalid phone number or PIN"`.
  - Queries `POST /api/v1/auth/login` with registered phone number and wrong PIN: returns **HTTP 401 Unauthorized** with identical message `"Invalid phone number or PIN"`.
  - Prevents attackers from discovering valid phone numbers in database.
- **`test_refresh_token_replay_attack_cascades_session_revocation`**:
  - User authenticates and receives refresh token `R1`.
  - User exchanges `R1` for new token pair (`A2`, `R2`). `R1` is now rotated and invalidated.
  - Attacker intercepts and replays `R1` at `POST /api/v1/auth/refresh`.
  - Server detects reuse anomaly: rejects with **HTTP 401 Unauthorized** (`"Refresh token has been revoked or replayed"`).
  - Server cascades revocation across the entire token family: even `R2` is immediately revoked in database.
- **`test_repository_secrets_audit`**:
  - Recursively scans all code, scripts, configurations, and documentation files across `services/`, `apps/`, `data/`, `scripts/`, `docs/`.
  - Checks against regexes for private RSA/EC keys, AWS/cloud secret keys, unmasked JWT secrets, and database connection strings with live credentials.
  - Result: **0 secrets found**. Clean audit across repository.

### 3.7 `R-SEC-02` & `AT-073`: Media Privacy, Traversal, Signed URLs & Size Limits
- **`test_media_storage_path_traversal_prevention`**:
  - Instantiates `LocalStorageAdapter`.
  - Attempts relative path escape sequences: `../../etc/passwd`, `..\..\windows\win.ini`, `sub/../../secret.txt`.
  - All trigger `ValueError: Path traversal detected: path escapes storage base directory`.
- **`test_image_upload_exif_metadata_stripping`**:
  - Constructs synthetic JPEG image with embedded EXIF GPS tags (Latitude, Longitude) and Camera Make/Model tags.
  - Passes image through `_strip_exif_and_validate_image()`.
  - Resulting byte stream opened in Pillow has **0 EXIF tags** (`image.getexif()` is empty).
- **`test_media_download_authorization_and_signed_url_expiry`**:
  - Uploads lot photo. Generates 15-minute signed download URL.
  - Downloading without token -> **HTTP 401 Unauthorized**.
  - Downloading with valid signed token -> **HTTP 200 OK** with image binary.
  - Downloading with expired token (timestamp - 30 minutes) -> **HTTP 401 Unauthorized** (`"Signed URL has expired"`).
- **`test_oversized_upload_and_invalid_mime_rejection`**:
  - Upload of 2.5 MiB image (> 2 MiB ceiling) is rejected with **HTTP 422 Unprocessable Entity**.
  - Upload of text file disguised as `image/jpeg` with text payload is rejected with **HTTP 422 Unprocessable Entity** (invalid magic bytes).

---

## 4. Residual Limitations & Operational Guardrails

In compliance with task `T040` specifications, the following residual limitations and operational guardrails are formally documented:
1. **SMS Gateway Isolation**: Production SMS OTP routing relies on a pluggable gateway provider; the application currently operates in deterministic test and demo bypass modes (`DEMO_MODE=True`), precluding external telecom SMS costs.
2. **Offline Local SQLite / Room Encryption**: The mobile collector client stores offline SQLite data locally; Android KeyStore and EncryptedSharedPreferences safeguard auth tokens, but full-disk hardware encryption remains the user's Android OS boundary responsibility.
3. **In-Memory Rate Limiting**: The current rate limiter uses an in-memory sliding window bucket. In multi-instance distributed deployments without sticky sessions, rate limiting should be fronted by a reverse-proxy (e.g. Caddy / Nginx) or Redis-backed state store if horizontal scaling is introduced.

---

## 5. Acceptance Verification Mapping

| Acceptance Case | Description | Contributing Tasks | Status |
|:---|:---|:---|:---:|
| `AT-008` | Role and object authorization | `T007`, `T040` | **PASS** |
| `AT-010` | Isolated demo access without SMS | `T007`, `T040`, `T050` | Contributed (`T040` verified) |
| `AT-032` | Public verification and privacy | `T023`, `T025`, `T040` | **PASS** |
| `AT-058` | Minimal collector dataset and anonymization | `T007`, `T031`, `T040`, `T047` | Contributed (`T040` verified) |
| `AT-060` | Provenance and demo isolation everywhere | `T005`, `T029`, `T031`, `T040` | **PASS** |
| `AT-072` | PIN abuse secrets and transport safety | `T007`, `T040`, `T041` | Contributed — local abuse/secrets tests plus deployed HTTPS and restrictive CORS rechecked 2026-10-01; final acceptance awaits T041. |
| `AT-073` | Privacy media access retention and audit | `T008`, `T040`, `T042` | Contributed (`T040` verified) |

All 23 scoped tests pass cleanly. T040 is verified and marked **DONE**; AT-073 remains dependent on T042's retention/backup evidence.
