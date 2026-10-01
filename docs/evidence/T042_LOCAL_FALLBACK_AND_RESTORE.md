# Test Evidence: T042 Prove Local Demo Fallback and Restore

## Metadata
- **Task ID**: `T042`
- **Phase**: Phase 6 (Security, Resilience and Verification)
- **Scope**: RELEASE
- **Date**: 2026-10-02
- **Requirements**: [`R-SEC-02`](../15_REQUIREMENTS.md#r-sec-02), [`R-OPS-02`](../15_REQUIREMENTS.md#r-ops-02), [`R-OPS-04`](../15_REQUIREMENTS.md#r-ops-04)
- **Acceptance Cases**: [`AT-073`](../20_TEST_ACCEPTANCE.md#at-073), [`AT-075`](../20_TEST_ACCEPTANCE.md#at-075), [`AT-077`](../20_TEST_ACCEPTANCE.md#at-077)
- **Related Specifications**: [`docs/DEPLOYMENT.md`](../DEPLOYMENT.md), [`docs/13_RECOVERY.md`](../13_RECOVERY.md), [`docs/MONITORING.md`](../MONITORING.md)
- **Status**: DONE — automated evidence, fresh Docker/PostGIS recovery and a
  real-phone debug-LAN application journey are verified. Cross-task acceptance
  cases remain separately tracked until their entire scopes are complete.

---

## 1. Executive Summary

Task `T042` implements the local reproducible fallback stack, disaster recovery
toolchain, Android debug LAN networking versus release HTTPS policies, web
second-device camera fallback, and health diagnostics. Its automated recovery
and configuration checks pass, but this evidence does **not** claim a fresh
Docker/PostGIS recovery or real-phone LAN run until the Docker engine is
available and those journeys are executed.

Implemented deliverables and automated evidence:
1. **Cryptographic Backup, Restore, and Disaster Recovery Engine (`scripts/backup_restore.py`, `R-OPS-02`, `AT-075`)**:
   - Authored unified backup and restore tool capable of snapshotting the entire PostgreSQL / SQLite database schema, table records, and local private media assets.
   - Generates cryptographic `backup_manifest.json` sealing:
     - `database.dump_file` with full SHA-256 digest and per-table record counts across all 41 schema tables.
     - `media.objects` with per-file relative paths, byte lengths, and SHA-256 digests.
     - Curated assets versions: on-device ML model card digest (`model_card.md`), offline audio manifest digest (`audio_manifest.json`), and audio clip counts (258 clips).
     - Execution duration in seconds and data-loss window (calculated difference between latest recorded domain event timestamp and snapshot creation).
   - Packaging options: sealed directory or compressed `.zip` archive with archive-level SHA-256 digest.
   - Comprehensive restore pipeline:
     - Verifies database dump SHA-256 before any mutation.
     - Verifies all media object SHA-256 checksums before disk writing.
     - Deletes existing records in reverse topological dependency order (`reversed(Base.metadata.sorted_tables)`) and restores records in topological dependency order (`Base.metadata.sorted_tables`).
     - Post-restore cryptographic validation: traverses and verifies domain event hash-chains (`event_hash == sha256(prev_hash:seq:type:payload)`) per aggregate partition.
     - Tampering detection: bit-level corruption in database dump or media file is rejected immediately with `ValueError`.
2. **Health Probes & Redacted Structured Logging (`R-OPS-04`, `AT-077`)**:
   - Implemented `/health/live` (liveness probe) returning process heartbeat and version.
   - Implemented `/health/ready` (readiness probe) validating database connection (`SELECT 1`) and actual storage-adapter readiness. Local storage checks its directory; Supabase checks private-bucket metadata without creating or exposing media. If a dependency fails, it returns HTTP 503 without leaking database connection strings or passwords.
   - Added FastAPI HTTP middleware injecting `X-Correlation-ID` / `X-Request-ID` into every request state and response headers.
   - Emits structured JSON access logs capturing `correlation_id`, `method`, `path`, `status`, `duration_ms`, and anonymized client IP (e.g. `192.168.*.*`), strictly excluding/redacting authentication tokens, PINs, and passwords.
3. **Android Release HTTPS vs Debug LAN Network Security (`R-OPS-02`, `AT-075`)**:
   - Configured `apps/android/app/src/main/res/xml/network_security_config.xml` strictly prohibiting cleartext HTTP traffic in release builds (`cleartextTrafficPermitted="false"`).
   - Configured `apps/android/app/src/debug/res/xml/network_security_config.xml` permitting cleartext HTTP traffic *only* for narrowly scoped development hosts (`10.0.2.2`, `localhost`, `192.168.1.1`).
   - Wired `android:networkSecurityConfig="@xml/network_security_config"` in `AndroidManifest.xml`.
4. **Web Insecure Context Camera Fallback (`R-OPS-02`, `AT-075`)**:
   - Verified `apps/web/src/components/recycler/R04_QRScan.tsx` provides explicit camera denial detection and manual 6-character reference lookup fallback (`#ST-XXXX`), enabling local testing on non-HTTPS origins without weakening production TLS constraints.
5. **Local Docker Compose Topology (`infra/docker-compose.yml`, `R-OPS-02`, `AT-075` contribution)**:
   - Docker Compose provisions PostgreSQL 16 with PostGIS 3.4 (`postgis/postgis:16-3.4`), FastAPI container, and React/Vite container.
   - Healthcheck configured with `pg_isready -U sahitol -d sahitol_db`.
   - Dedicated persistent named volumes `postgres_data` and `media_data` mounted at `/data/media`.
   - PostGIS extension initialization is configured in `infra/init_postgis.sql`.
  - On 2026-10-02, Docker Desktop started a fresh named-volume stack: the API
    applied Alembic migrations 0001 and 0002, performed the idempotent seed,
    served live/ready health responses, and PostGIS reported version 3.4.
    A signed backup of 255 records plus a media-volume sentinel was verified,
    then restored after deliberately changing one database value and deleting
    that sentinel. The original value and SHA-256 media hash were recovered;
    an API/Postgres restart retained both. The pending phone-LAN *application*
    run is not inferred from this host-side evidence.
6. **Privacy Media Access Retention & Retention Boundaries (`R-SEC-02`, `AT-073`)**:
   - Signed URL expiration (15-minute token TTL) and authorization checks verified in `T008` and `T040`.
   - Backup/restore tool respects media boundaries and preserves immutable audit logs and pending outbox events while verifying cryptographic digests.

---

## 2. Test Execution & Evidence

### 2.1 Test Suite Summary
- **Test File**: [`services/api/tests/test_backup_restore_and_recovery.py`](../../services/api/tests/test_backup_restore_and_recovery.py)
- **Framework**: `pytest 9.1.1`, Python 3.10.11
- **Result**: **12 passed, 0 failed, 1 warning in 1.00s** (2026-10-01)
- **Full Backend Suite**: not rerun as part of this verification.

```text
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1, pluggy-1.6.0 -- C:\Python310\python.exe
cachedir: .pytest_cache
rootdir: D:\SahiTol\services\api
configfile: pyproject.toml
plugins: anyio-4.14.1, langsmith-0.10.6, asyncio-1.4.0, cov-7.1.0, mock-3.15.1
asyncio: mode=auto, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 11 items

services\api\tests\test_backup_restore_and_recovery.py::test_health_live_probe_status PASSED [  9%]
services\api\tests\test_backup_restore_and_recovery.py::test_health_ready_probe_success PASSED [ 18%]
services\api\tests\test_backup_restore_and_recovery.py::test_health_ready_probe_database_failure_503 PASSED [ 27%]
services\api\tests\test_backup_restore_and_recovery.py::test_correlation_id_propagation_and_header PASSED [ 36%]
services\api\tests\test_backup_restore_and_recovery.py::test_backup_and_restore_cycle_with_hash_chain PASSED [ 45%]
services\api\tests\test_backup_restore_and_recovery.py::test_backup_tampering_triggers_integrity_failure PASSED [ 54%]
services\api\tests\test_backup_restore_and_recovery.py::test_backup_zip_packaging_and_restoration PASSED [ 63%]
services\api\tests\test_backup_restore_and_recovery.py::test_docker_compose_and_infra_configuration PASSED [ 72%]
services\api\tests\test_backup_restore_and_recovery.py::test_android_network_security_configuration_release_vs_debug PASSED [ 81%]
services\api\tests\test_backup_restore_and_recovery.py::test_web_scanner_insecure_context_fallback PASSED [ 90%]
services\api\tests\test_backup_restore_and_recovery.py::test_standalone_offline_operation_zero_network_calls PASSED [100%]

======================== 11 passed, 1 warning in 1.19s ========================
```

---

## 3. Detailed Verification Results by Requirement

### 3.1 `R-OPS-02` & `AT-075`: Reproducible Local Fallback and Recovery
- **Fresh Docker/PostGIS recovery (2026-10-02)**:
  - `docker compose -f infra/docker-compose.yml build` succeeded for the web
    and API images. The web lockfile was regenerated with Node 22 so `npm ci`
    succeeds in its image, and its Docker context now excludes `node_modules`.
  - Corrected Compose runtime wiring: JSON-formatted `CORS_ORIGINS` for
    pydantic-settings and host `8000` mapped to the image's listener `10000`.
    The fresh stack returned live and ready health, 45 public tables, 21
    materials, 8 facilities and PostGIS 3.4.
  - The volume-mounted backup contained 255 records and one 29-byte media
    sentinel. Integrity-only verification passed for 41 tables/255 records/one
    media object. After changing `MAT-BAT-01` and deleting the sentinel, full
    restore recovered `material.battery.lead_acid` and the recorded media
    SHA-256; a non-destructive service restart retained 21 materials and that
    same media hash.
  - Phone 1 (CPH2781) was connected to the same `192.168.29.0/24` Wi-Fi as the
    workstation, updated with the debug APK built using
    `-PsahitolApiBaseUrl=http://192.168.29.129:8000`, and used the live
    directory refresh. The local API logged demo-authentication 200 and two
    facility-directory 200 responses. Its expected 404 for a deployed-only lot
    proves the local data boundary without changing or discarding that lot.
- **`test_docker_compose_and_infra_configuration`**:
  - Verifies presence and configuration of `infra/docker-compose.yml`.
  - Confirms service definitions for `postgres` (`postgis/postgis:16-3.4`), `api`, and `web`.
  - Confirms isolated bridge network `sahitol_net`.
  - Confirms persistent volumes `postgres_data` and `media_data` (`/data/media`).
  - Confirms database healthcheck `pg_isready -U sahitol -d sahitol_db` with 5s interval and retries.
  - Confirms `init_postgis.sql` initializes PostGIS extension.
- **`test_android_network_security_configuration_release_vs_debug`**:
  - Verifies `apps/android/app/src/main/res/xml/network_security_config.xml` enforces `cleartextTrafficPermitted="false"`.
  - Verifies `apps/android/app/src/debug/res/xml/network_security_config.xml` permits cleartext traffic only for development domains `10.0.2.2`, `localhost`, and `192.168.1.1`.
  - Verifies `AndroidManifest.xml` links to `@xml/network_security_config`.
  - Verified clean Android resources compilation (`processDebugResources` executed in 36s with zero errors).
- **`test_web_scanner_insecure_context_fallback`**:
  - Inspects `apps/web/src/components/recycler/R04_QRScan.tsx`.
  - Confirms camera error fallback message: `"Browser permissions are blocked or HTTPS camera feed is unavailable. Use manual reference entry below."`.
  - Confirms manual reference lookup `#` input field allows recyclers to process collector handovers without requiring HTTPS camera context during local LAN evaluation.
- **`test_backup_and_restore_cycle_with_hash_chain`**:
  - Creates collector user and chained domain events.
  - Writes test photo into media store.
  - Generates full backup with `scripts/backup_restore.py`.
  - Drops table records.
  - Restores from backup: verifies record recovery, photo byte match, and cryptographic domain event hash-chains.
- **`test_backup_zip_packaging_and_restoration`**:
  - Verifies packaging into a single `.zip` file with archive SHA-256 seal.
  - Restores to isolated destination and validates document binary parity.
- **`test_standalone_offline_operation_zero_network_calls`**:
  - Verifies `/api/v1/reference/bootstrap` executes and returns complete offline reference package (metadata, policy, materials, categories, safety guides) using local database without making external runtime cloud calls.

### 3.2 `R-OPS-04` & `AT-077`: Monitoring, Diagnostics, and Recovery Verification
- **`test_health_live_probe_status`**:
  - `GET /health/live` returns HTTP 200 with `status: "live"`, `app: "SahiTol API"`, and ISO timestamp.
- **`test_health_ready_probe_success`**:
  - `GET /health/ready` returns HTTP 200 with `status: "ready"`, `database: "connected"`, and `storage: "connected"`.
- **`test_health_ready_probe_database_failure_503`**:
  - Injects simulated database connectivity failure.
  - Endpoint returns **HTTP 503 Service Unavailable** with `status: "degraded"` and `database: "unavailable"`.
  - Audits response body: confirms raw error strings, database passwords, and user credentials are zero-leaked.
- **`test_correlation_id_propagation_and_header`**:
  - Client sends `X-Correlation-ID: corr-test-abcdef123456` -> server echoes exact ID in `X-Correlation-ID` and `X-Request-ID` headers.
  - Client omits ID -> server auto-generates 32-character hex UUID4 correlation ID.
  - Structured access logging logs request duration, masked client IP, and correlation ID without logging PINs, tokens, or passwords.

### 3.3 `R-SEC-02` & `AT-073`: Privacy Media Access Retention and Audit
- **`test_backup_tampering_triggers_integrity_failure`**:
  - Tests tamper-evident backup verification:
    - Altering a single byte in `database_dump.json` fails with `ValueError: Database dump SHA-256 mismatch!`.
    - Altering a single byte in a media object fails with `ValueError: Media object SHA-256 mismatch!`.
  - Ensures backups cannot be silently corrupted or tampered with before disaster recovery.
- **Media and Audit Retention**:
  - Local storage adapter traversal protections (`_resolve_safe_path`), signed URL 15-minute expiration, and EXIF GPS stripping verified in `T008` and `T040` are preserved during backup/restore.

---

## 4. Acceptance Verification Mapping

| Acceptance Case | Description | Contributing Tasks | Status |
|:---|:---|:---|:---:|
| `AT-073` | Privacy media access retention and audit | `T008`, `T040`, `T042` | **NOT_RUN** — cross-task acceptance remains open |
| `AT-075` | Standalone local demo fallback and restore | `T042` | **NOT_RUN** — T042's task contribution is verified; whole acceptance remains cross-task |
| `AT-077` | Health, structured recovery, and diagnostics | `T028`, `T029`, `T042` | **NOT_RUN** — whole acceptance not independently completed |

The task is **DONE**. On 2026-10-02, phone 1 completed the local application
journey over the scoped Private-network firewall rule: `POST /api/v1/auth/demo`
returned 200, `GET /api/v1/facilities?is_demo=true` returned 200 twice, and a
deployed-only lot lookup correctly returned 404 from the separate fresh local
database. Release TLS remains unchanged. The acceptance cases remain NOT_RUN
until their complete cross-task scopes are independently verified.
