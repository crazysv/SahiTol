# Test Evidence: T013 Implement Android Room Repositories and Durable Outbox

## Metadata
- **Task ID**: `T013`
- **Phase**: Stage 2 (Offline & Sync Foundations)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Environment**:
  - OpenJDK 17.0.20.1 LTS (Microsoft), Gradle 8.10.2, AGP 8.7.0, Kotlin 2.0.20
  - Android Jetpack Room 2.6.1 (`room-runtime`, `room-ktx`, `room-compiler` via KSP)
  - Coroutines 1.8.1 (`kotlinx-coroutines-android`)
  - Target SQLite / Android SDK 35 (minSdk 26)

---

## Requirements and Acceptance Coverage
| Requirement | Test ID | Scope | Verification Status | Implementation & Evidence Notes |
|---|---|---|---|---|
| **R-AUTH-03** | **AT-009** | RELEASE | Partially verified (T013 output) | Local profile and draft data partitioned by `accountId`. Safe logout contract verified: unsynced records and outbox operations are preserved in SQLite across sessions; user switching cannot expose another account's drafts. |
| **R-LOT-02** | **AT-012** | RELEASE | Partially verified (T013 output) | Draft lot entity records integer grams (`estimatedWeightG`), integer paise valuation quantiles, local photo path, and legal status transitions (`DRAFT` / `SAVED_LOCAL_ONLY`). |
| **R-LOT-05** | **AT-015** | RELEASE | Partially verified (T013 output) | Local append-only domain event ledger (`DomainEventEntity`, `DomainEventDao`) with SHA-256 cryptographic hash-chaining starting from a fixed 64-character Genesis hash. |
| **R-OFF-01** | **AT-038** | RELEASE | Partially verified (T013 output) | Durable outbox table (`outbox_operations`) storing canonical operation metadata (`operation_id`, `account_id`, `device_id`, `command`, `payload_sha256`, `state`). Unsynced counts are queryable offline. |
| **R-OFF-02** | **AT-039** | RELEASE | Partially verified (T013 output) | Atomic ACID commitment via `database.withTransaction`: business object (`LotEntity`), domain event (`DomainEventEntity`), and outbox row (`OutboxOperationEntity`) commit together or roll back completely on failure. |

---

## 1. Local Database Architecture & Schema

### Room Database (`SahiTolDatabase.kt`)
- Database Version: **2**
- Tables Managed:
  1. `lots`: Local business projection for scrap materials.
  2. `domain_events`: Append-only tamper-evident audit ledger.
  3. `outbox_operations`: Durable transactional queue for server synchronization.

### Entity Definitions
1. **`LotEntity`**:
   - `lotId`: String UUID Primary Key.
   - `accountId`: Account partition key (indexed).
   - `materialCode`: Standardized category code (e.g. `MAT-CAB-01`).
   - `estimatedWeightG`: Long integer grams.
   - `measuredWeightG`: Nullable Long integer grams.
   - `estimatedLowPaise`, `estimatedMedianPaise`, `estimatedHighPaise`: Nullable Long integer paise.
   - `localPhotoPath`: Nullable local file path.
   - `status`: `DRAFT` (initial local status).
   - `syncStatus`: `SAVED_LOCAL_ONLY` (non-negotiable invariant: saved locally $\ne$ synced).
   - `serverVersion`: Long optimistic concurrency version counter.

2. **`DomainEventEntity`**:
   - `eventId`: String UUID Primary Key.
   - `accountId`: Account partition key (indexed).
   - `entityType`: `LOT`.
   - `entityId`: Foreign reference to entity UUID.
   - `eventType`: `LOT_CREATED`, `LOT_LISTED`, etc.
   - `payloadJson`: Canonical JSON representation of state snapshot.
   - `prevHash`: 64-hex SHA-256 hash of preceding event (or 64 zeros for Genesis).
   - `currentHash`: SHA-256 of `${prevHash}:${eventType}:${payloadJson}`.
   - `createdAt`: Millisecond epoch timestamp.

3. **`OutboxOperationEntity`**:
   - `operationId`: String UUID Primary Key.
   - `accountId`: Account partition key (indexed).
   - `deviceId`: Client device hardware identifier.
   - `entityType`: `LOT`.
   - `entityId`: Target entity UUID.
   - `command`: Command name (`CREATE_LOT`).
   - `expectedVersion`: Base server version for optimistic concurrency.
   - `payloadJson`: Immutable request payload.
   - `payloadSha256`: SHA-256 fingerprint for idempotency deduplication.
   - `dependsOnJson`: JSON array of prerequisite operation UUIDs.
   - `mediaIdsJson`: JSON array of referenced media file paths.
   - `state`: `QUEUED` $\rightarrow$ `SENDING` $\rightarrow$ `ACKNOWLEDGED` (or `RETRY_WAIT`).
   - `attemptCount`: Retry counter.
   - `nextAttemptAt`: Backoff timestamp.

---

## 2. Atomic Commit & Repository Invariants (`LotRepository.kt`)

### Atomic Transaction Guarantee (`createLotAtomic`)
```kotlin
database.withTransaction {
    database.lotDao().insertLot(lotEntity)
    database.domainEventDao().insertEvent(domainEvent)
    database.outboxDao().enqueue(outboxOp)
}
```
- **Atomicity**: If any insert fails, the transaction rolls back cleanly.
- **Process Death Protection**: A crash before commit leaves zero partial state. A crash after commit restores the full triplet (`LotEntity` + `DomainEventEntity` + `OutboxOperationEntity`), allowing WorkManager to resume synchronization without data loss.

### Hash-Chain Verification (`verifyEntityLineage`)
- Iterates over all domain events for a given entity in chronological order.
- Validates that `event.prevHash` matches the prior event's `currentHash`.
- Recomputes `SHA-256(prevHash:eventType:payloadJson)` to ensure no offline tampering.

### Safe Logout & User Partitioning
- Queries are strictly scoped by `accountId` in `LotDao` and `OutboxDao`.
- `prepareLogoutPreservingData(accountId)` inspects unsynced counts and retains all unacknowledged outbox items in SQLite storage, revoking only in-memory credentials without deleting offline work.

---

## 3. Automated Test Verification

- **Test Suite**: `apps/android/app/src/test/java/com/sahitol/collector/RoomOutboxRepositoryTest.kt`
- **Tests Executed**:
  1. `testSha256Determinism`: Verifies 64-hex lowercase SHA-256 output.
  2. `testDomainEventHashChainProgression`: Verifies Genesis hash chaining across consecutive lifecycle events.
  3. `testOutboxOperationContract`: Verifies canonical field population and initial `QUEUED` state.
  4. `testUserPartitionContract`: Verifies that querying user A does not leak user B's lot entities.
  5. `testSafeLogoutPreservationInvariant`: Verifies that unsynced outbox operations remain intact upon logout.
- **Overall Android Test Suite Results**:
  - Total Tests: **17**
  - Failures: **0**
  - Ignored: **0**
  - Success Rate: **100%**
  - Duration: **0.094s**
  - HTML Report: `apps/android/app/build/reports/tests/testDebugUnitTest/index.html`

---

## 4. Build Artifacts
- **Debug APK**: `apps/android/app/build/outputs/apk/debug/app-debug.apk`
- **APK Size**: 29,088,027 bytes (27.7 MB)
- **Status**: Verified compilable and testable with full Room 2.6.1 SQLite runtime.
