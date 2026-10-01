# Test Evidence: T001 Bootstrap Repository and Compatible Toolchain

## Metadata
- **Task ID**: T001
- **Phase**: Stage 0 (Setup & Feasibility)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Environment**:
  - OS: Windows 11 (AMD64)
  - Java: OpenJDK 17.0.20.1 LTS (Microsoft)
  - Python: 3.10.11
  - Node.js: v22.19.0, npm: 11.12.0
  - Docker: 28.3.3
  - Android SDK: Platforms `android-35`, `android-36`; Build tools `35.0.0`, `36.1.0`

## Requirements and Acceptance Coverage
| Requirement | Test ID | Scope | Verification Status | Notes |
|---|---|---|---|---|
| R-GOV-01 | AT-001 | RELEASE | Partially verified (T001 output) | SahiTol identity verified across all packages, configurations, and manifests. SIH26229 retained as problem title only. |
| R-GOV-03 | AT-003 | RELEASE | Verified | Full session-start reconstruct, catalog & status reconciliation, validator clean pass, continuous autonomous progression. |
| R-ARC-01 | AT-005 | RELEASE | Partially verified (T001 output) | Native Android Kotlin/Compose/Room/WorkManager/LiteRT skeleton established. MinSdk 26, CompileSdk 35. Full device test in T003. |
| R-ARC-02 | AT-006 | RELEASE | Verified | FastAPI, React/Vite, PostgreSQL/PostGIS, Docker Compose, Local & Supabase storage adapters, lockfiles created and verified. |
| R-OPS-03 | AT-076 | RELEASE | Verified | Dependency audit confirms zero required paid runtime APIs, SMS, cloud speech, proprietary LLM, or map billing services. |

## Implementation Outputs Created
1. **Android Collector App Skeleton (`apps/android/`)**:
   - `build.gradle.kts`, `settings.gradle.kts`, `gradle.properties`, `local.properties.example`
   - Version catalog `gradle/libs.versions.toml`: pinned AGP 8.7.0, Kotlin 2.0.20, Compose BOM 2024.09.02, Room 2.6.1, WorkManager 2.9.1, LiteRT 1.0.1, CameraX 1.3.4, Hilt 2.51.1
   - `app/build.gradle.kts`: compileSdk 35, minSdk 26, targetSdk 35, Java 17 compatibility
   - `AndroidManifest.xml`: CAMERA, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, INTERNET
   - Room Database & DAOs: `LotEntity`, `OutboxOperationEntity`, `LotDao`, `OutboxDao`, `SahiTolDatabase`
   - Domain & Pricing: `MaterialCategory` (regulatory routes), `LotStatus`, `PriceCalculator`
   - Resources: `strings.xml` with English, Hindi (`values-hi`), and Marathi (`values-mr`) strings
   - Tests: `PriceCalculatorTest.kt` verifying `PRICE_V1` quantiles and valuation formulas

2. **Backend API Service (`services/api/`)**:
   - `pyproject.toml`, `requirements.txt`: FastAPI 0.115.0, Pydantic 2.9.2, SQLAlchemy 2.0.35, Alembic 1.13.3, GeoAlchemy2, PyJWT, Argon2id, HTTPX, ReportLab
   - `app/config.py`: Pydantic BaseSettings loading from `.env`
   - `app/security.py`: Argon2id PIN hashing with pepper, JWT access/refresh token creation & decoding
   - `app/storage/`: Abstract `StorageAdapter`, `LocalStorageAdapter` (path-traversal protection, atomic file replace, 2MB size limit), `SupabaseStorageAdapter`
   - `app/domain/`: `canonical.py` (SAHITOL-JCS-1 canonical JSON & SHA-256), `pricing.py` (PRICE_V1 weighted quantiles and lot valuation)
   - `app/routers/`: health, auth (phone/PIN and demo-login), lots, prices, recyclers, handovers, payments, admin, sync
   - `alembic/`: Alembic migrations configuration with PostGIS extension support
   - `.env.example`: Non-secret configuration template

3. **Web Application Skeleton (`apps/web/`)**:
   - `package.json`, `package-lock.json`: React 18, Vite 5, TypeScript 5.5, TailwindCSS 3.4, React Router 6, TanStack Query 5, Vitest, Testing Library
   - `vite.config.ts`, `tsconfig.json`, `tailwind.config.js`, `postcss.config.js`
   - `src/App.tsx`: Role routes for Recycler Console (R01–R07), Admin Dashboard (A01–A07), Public Verification (V01), Illustrative Economics (U01)
   - Gated placeholders clearly indicating awaiting Stitch screens

4. **Local Infrastructure & Deployment Fallback (`infra/`)**:
   - `docker-compose.yml`: PostgreSQL 16 with PostGIS 3.4 (`postgis/postgis:16-3.4`), healthcheck, persistent `postgres_data` and `media_data` volumes, API container, Nginx Web container
   - `init_postgis.sql`: `CREATE EXTENSION postgis;`, `CREATE EXTENSION "uuid-ossp";`
   - `Dockerfile.api`: Python 3.10 slim, libpq-dev, uvicorn entrypoint
   - `Dockerfile.web`: Multi-stage build (Node 22 builder + Nginx alpine)

5. **CI Workflow (`.github/workflows/ci.yml`)**:
   - `validate-docs`: `check_docs.py` and `test_doc_integrity.py`
   - `test-api`: Python 3.10, pytest
   - `test-web`: Node 22, npm ci, typecheck, vitest, build
   - `test-android`: JDK 17, gradle test

## Test Results and Verification Log

### 0. Reproducible API verification repair — 2026-10-01

The original API command was not reproducible from `services/api`: shared
repository fixtures were outside Python's import path and the full suite's
data/model checks required undeclared verification dependencies. The API
package now pins its runtime dependencies, declares repository-root test
resolution, and provides `requirements-dev.txt` for the data/model verifier
dependencies. CI installs that verification set and runs the tests from the
repository root with both the API and repository root on `PYTHONPATH`.

Verification on Windows/Python 3.10:

```text
318 tests collected in 3.67s
```

This establishes reproducible collection. Functional failures remain recorded
against their owning implementation tasks rather than being hidden as a T001
toolchain result.

### 1. Python API Unit Tests
Command: `python -m pytest services/api/tests`
Result: **12 PASSED** in 1.62s
```text
services/api/tests/test_canonical.py .                                   [  8%]
services/api/tests/test_health.py ..                                     [ 25%]
services/api/tests/test_pricing.py ...                                   [ 50%]
services/api/tests/test_security.py ...                                  [ 75%]
services/api/tests/test_storage.py ...                                   [100%]
12 passed, 1 warning in 1.62s
```
- `test_canonical.py`: Canonical JSON serialization matches `docs/planning/handover_fixture.json` SHA-256 hash `a091623365372138e72b1d767cca58ac80c59667b59b86f511ebf11b64eb783f`.
- `test_pricing.py`: PRICE_V1 quantiles for rates `[10000, 20000, 30000, 40000]` yield Q1=10000, median=20000, Q3=30000; valuation for 2500g yields `[25000, 50000, 75000]` paise.
- `test_storage.py`: LocalStorageAdapter CRUD verified; path traversal `../../../etc/passwd` rejected; files exceeding 2MB rejected.
- `test_security.py`: Argon2id salt+pepper hashing and verify confirmed; JWT access/refresh token generation and claim extraction confirmed.
- `test_health.py`: `/health` and `/` endpoints return 200 OK with correct metadata.

### 2. Web Frontend Typecheck, Tests, and Build
- Command: `npm run typecheck` in `apps/web`
  Result: **0 errors** (`tsc --noEmit` clean exit)
- Command: `npm run test` in `apps/web`
  Result: **1 PASSED** (Vitest in 34.97s, `src/App.test.tsx`)
- Command: `npm run build` in `apps/web`
  Result: **SUCCESS** in 2.26s
  Output: `dist/index.html` (0.53 kB), `dist/assets/index.css` (9.13 kB), `dist/assets/index.js` (196.17 kB)

### 3. Documentation Integrity Audit
Command: `python scripts/check_docs.py`
Result: **PASS** (0 errors; 2452 local links; 34 screens; 98 requirements)

## Stitch Gate Status
- **T002**: Screen S00 (Android Feasibility Diagnostic) requested from owner via prepared brief.
- Registry row updated to `REQUESTED` in `design/stitch/SCREEN_REGISTRY.md`.
- Status marked `WAITING_STITCH` in `docs/planning/status.json`.
- UI views in `apps/android` and `apps/web` maintain placeholder containers awaiting owner-approved Stitch screens. No unauthorized UI was generated.
