# Test Evidence: T007 Implement Phone/PIN Authentication and Ownership

## Metadata
- **Task ID**: T007
- **Phase**: Stage 1 (Data & Backend Setup)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Reviewer**: SahiTol Engineering & Security Architecture

## Context & Objectives
Implements end-to-end phone and PIN authentication, Argon2id password hashing with server-side pepper and unique random salt, rotating JWT access and refresh token sessions with replay attack detection, thread-safe sliding-window rate limiting for PIN brute-force defense, role and object-level authorization dependencies, isolated demo access without SMS dependencies, and a documented Android session continuation contract.

## Requirements & Acceptance Case Mapping
| Requirement | Test ID | Scope | Contributing Tasks | Implementation & Evidence Summary |
|---|---|---|---|---|
| R-AUTH-01 | AT-007 | RELEASE | T007, T017 | Online activation (`POST /auth/register`) with Indian phone validation (`^[6-9]\d{9}$`), 4-6 digit numeric PIN, Argon2id hashing, and linked Collector profile. Plaintext PIN is never stored or returned. Rejects duplicate phone with 409 Conflict. |
| R-AUTH-02 | AT-008 | RELEASE | T007, T040 | Role-based authorization (`require_roles`) and object-level ownership checks (`check_object_ownership`). Self-registration restricts role strictly to `COLLECTOR` (cannot escalate to `ADMIN` or `RECYCLER`). Expired/invalid tokens rejected server-side with 401. |
| R-AUTH-03 | AT-009 | RELEASE | T007, T013, T015, T017 | Rotating refresh token flow (`POST /auth/refresh`) with SHA-256 session tracking in `auth_sessions`. Replay attack detection revokes all active sessions if a revoked token is re-presented. Safe logout (`POST /auth/logout`) revokes sessions while preserving client-side offline pending data. Documented in [SESSION_CONTINUATION_CONTRACT.md](../contracts/SESSION_CONTINUATION_CONTRACT.md). |
| R-AUTH-04 | AT-010 | RELEASE | T007, T040, T050 | Isolated demo mode (`POST /auth/demo`) provisioned without SMS dependency. Generates demo user and collector profile with `is_demo=True` claim. Enforces demo isolation boundary via `check_demo_isolation`. |
| R-DATA-06 | AT-058 | RELEASE | T007, T031, T040, T047 | Minimal profile access (`GET /auth/me`) returns masked phone (`******3210`), display alias, preferred language, and general area without disclosing plaintext credentials, pepper, or exact home GPS coordinates. |
| R-SEC-01 | AT-072 | RELEASE | T007, T040, T041 | Rate-limiting sliding window (`phone_limiter`, `ip_limiter`) in `app/rate_limiter.py` locks out phone after 5 failed PIN attempts with HTTP 429 and `Retry-After`. Generic authentication failure message ("Invalid phone number or PIN") prevents account enumeration. |

## Observable Artifact Outputs
1. **Security & Cryptography Utilities** (`services/api/app/security.py`):
   - Argon2id PIN hashing (`hash_pin`, `verify_pin`) using `time_cost=2`, `memory_cost=65536`, `parallelism=2`, and `settings.PIN_PEPPER`.
   - Indian phone normalization (`normalize_phone`) and privacy-preserving masking (`mask_phone`).
   - JWT token issuance (`create_access_token`, `create_refresh_token`) with device scoping and unique `jti`.
   - SHA-256 token hashing (`hash_token`) for database session storage.
   - FastAPI dependencies: `get_current_user`, `require_roles`, `check_object_ownership`, and `check_demo_isolation`.

2. **Rate Limiting Engine** (`services/api/app/rate_limiter.py`):
   - Thread-safe sliding window rate limiter tracking failed login attempts per phone (max 5 in 15 min) and per IP (max 25 in 15 min).
   - Resets failure counter upon successful authentication; returns remaining lockout seconds with HTTP 429.

3. **Authentication Router** (`services/api/app/routers/auth.py`):
   - `POST /auth/register` (and `/api/v1/auth/register`): Collector activation with atomic User + Collector profile + initial AuthSession creation.
   - `POST /auth/login` (and `/api/v1/auth/login`): Throttled phone/PIN login issuing access and refresh tokens.
   - `POST /auth/demo` (and `/api/v1/auth/demo`): Instant isolated demo authentication with `is_demo=True`.
   - `POST /auth/refresh` (and `/api/v1/auth/refresh`): Rotating refresh token exchange with token replay attack detection.
   - `POST /auth/logout` (and `/api/v1/auth/logout`): Explicit session revocation.
   - `GET /auth/me` (and `/api/v1/auth/me`): Authenticated user identity, role, and masked phone.
   - `GET/PATCH /collectors/me`: Collector profile inspection and optimistic locking update with `expected_version`.

4. **Android Session Continuation Contract** (`docs/contracts/SESSION_CONTINUATION_CONTRACT.md`):
   - Formal specification of token storage in `EncryptedSharedPreferences`, OkHttp 401 interception, silent background refresh, offline outbox preservation, and PIN re-auth resumption.

5. **Automated Test Suite** (`services/api/tests/test_auth.py`):
   - 13 comprehensive unit and integration tests covering phone validation, Argon2id hashing, collector registration, duplicate rejection, login rate-limiting lockout, token rotation, replay attack detection, safe logout, masked profile, optimistic locking updates, demo isolation, and role authorization.

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
collected 31 items

tests\test_auth.py .............                                         [ 41%]
tests\test_canonical.py .                                                [ 45%]
tests\test_health.py ..                                                  [ 51%]
tests\test_pricing.py ...                                                [ 61%]
tests\test_schema.py ......                                              [ 80%]
tests\test_security.py ...                                               [ 90%]
tests\test_storage.py ...                                                [100%]

======================== 31 passed, 1 warning in 5.10s ========================
```
