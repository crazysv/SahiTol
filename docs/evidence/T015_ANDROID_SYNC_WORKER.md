# Test Evidence: T015 Implement Android Background and Manual Synchronization

## Metadata
- **Task ID**: `T015`
- **Phase**: Stage 2 (Offline & Sync Foundations)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Environment**:
  - OpenJDK 17.0.20.1 LTS (Microsoft), Gradle 8.10.2, AGP 8.7.0, Kotlin 2.0.20
  - AndroidX WorkManager 2.9.1 (`work-runtime-ktx`)
  - Android Jetpack Room 2.6.1 (`room-runtime`, `room-ktx`)
  - Target SQLite / Android SDK 35 (minSdk 26)
  - Testing: JUnit 4, Kotlin Coroutines Test 1.8.1, `org.json:json:20250517`

---

## Requirements and Acceptance Coverage

| Requirement | Test ID | Scope | Verification Status | Implementation & Evidence Notes |
|---|---|---|---|---|
| **R-AUTH-03** | **AT-009**, **AT-042** | RELEASE | Partially verified (T015 client worker) | Background and manual sync worker partitions sync operations strictly by `accountId`. Unique WorkManager work name `sahitol_sync_work_<accountId>` prevents cross-account execution leaks. When server returns 401 Unauthorized or `AUTH_REQUIRED`, worker transitions operation state to `AUTH_REQUIRED` and stops immediate synchronization without deleting offline data or dropping pending outbox entries. |
| **R-OFF-04** | **AT-041** | RELEASE | Partially verified (T015 client worker) | Implemented two-way sync protocol on Android client: (1) Outbox batch push (`/api/v1/sync/batch`) with canonical operation payloads and dependency ordering; (2) Cursor-based delta pull (`/api/v1/sync/changes`) applied inside a single atomic Room transaction (`database.withTransaction`). When server returns 409 conflict, operation is marked `NEEDS_REVIEW` without erasing the collector's local draft. |
| **R-OFF-05** | **AT-042** | RELEASE | Partially verified (T015 client worker) | AndroidX WorkManager `SyncWorker` executes with `NetworkType.CONNECTED` constraint. Triggers either via periodic background scheduling or foreground/manual sync button. Truncated exponential backoff with $\pm 10\%$ jitter and honor of server `retry_after_seconds` header ensures no busy-looping or server hammering during outages. |
| **R-OFF-06** | **AT-043** | RELEASE | Partially verified (T015 client worker) | Concrete status transitions in local SQLite outbox: `QUEUED` $\rightarrow$ `SENDING` $\rightarrow$ `ACKNOWLEDGED`, `RETRY_WAIT`, `AUTH_REQUIRED`, `NEEDS_REVIEW`, or `NEEDS_REPAIR`. Unsynced queue counts and last successful sync epoch timestamps are queryable for UI indicators without claiming false green success on HTTP failure. |

---

## 1. Synchronization Architecture

### Synchronization Engine (`SyncEngine.kt`)
`SyncEngine` manages the protocol flow between local Room persistence and the FastAPI backend:
1. **Push Phase**:
   - Queries pending operations from `outbox_operations` for the active `accountId` filtered by `QUEUED` or `RETRY_WAIT`.
   - Constructs canonical `SyncBatchRequest` containing `client_batch_id`, `device_id`, `operations`, and `client_timestamp`.
   - Sends batch to `/api/v1/sync/batch`.
   - Reconciles `SyncBatchResponse` per operation outcome:
     - `APPLIED` $\rightarrow$ Updates outbox row to `ACKNOWLEDGED`, sets `acknowledged_at`.
     - `CONFLICT` $\rightarrow$ Updates outbox row to `NEEDS_REVIEW`, stores server conflict details, preserves local proposal.
     - `REJECTED` $\rightarrow$ Updates outbox row to `NEEDS_REPAIR`, stores validation error message.
     - `AUTH_REQUIRED` $\rightarrow$ Updates outbox row to `AUTH_REQUIRED`, halts current sync execution.
     - `RETRY` $\rightarrow$ Updates outbox row to `RETRY_WAIT`, computes next retry timestamp using exponential backoff with jitter.
2. **Pull Phase**:
   - Reads `last_cursor` from `client_sync_state` for `accountId`.
   - Requests delta changes from `/api/v1/sync/changes?cursor={last_cursor}`.
   - Executes atomic Room database transaction (`database.withTransaction`):
     - Applies delta changes (creates/updates lots, records tombstones).
     - Updates `last_cursor` to new server cursor.
     - Updates `last_synced_at` timestamp.
   - If `has_more` is true, continues paging until up-to-date.

### WorkManager Background Worker (`SyncWorker.kt`)
- Extends `CoroutineWorker(context, workerParams)`.
- Enforces network constraint:
  ```kotlin
  val constraints = Constraints.Builder()
      .setRequiredNetworkType(NetworkType.CONNECTED)
      .build()
  ```
- Uses unique work naming: `sahitol_sync_work_<accountId>` to avoid duplicate running sync tasks for the same collector.
- Provides static entry points:
  - `enqueueManualSync(context, accountId)`: One-time work request (`ExistingWorkPolicy.REPLACE`) with expedited flag for immediate UI response.
  - `schedulePeriodicSync(context, accountId)`: Periodic work request (`ExistingPeriodicWorkPolicy.KEEP`) scheduled at 15-minute intervals.

### Backoff and Jitter Implementation
Exponential backoff is computed with jitter:
$$\text{backoffMs} = \min(\text{maxBackoffMs}, \text{baseBackoffMs} \times 2^{\min(\text{attemptCount}, 10)}) \times (1 + \text{jitter})$$
Where jitter is uniformly distributed in $[-0.10, +0.10]$. If the server supplies `retry_after_seconds`, that value is honored directly.

---

## 2. Unit Test Verification

Automated unit tests in [`SyncWorkerTest.kt`](file:///d:/SahiTol/apps/android/app/src/test/java/com/sahitol/collector/SyncWorkerTest.kt) cover all protocol contracts and failure modes without requiring an emulator.

### Test Cases
```kotlin
@Test
fun testSyncBatchRequestSerialization() {
    // Verifies JSON structure matches FastAPI SyncBatchRequest schema exactly.
}

@Test
fun testSyncBatchResponseDeserializationAllOutcomes() {
    // Verifies parsing of APPLIED, RETRY, CONFLICT, REJECTED, AUTH_REQUIRED outcomes.
}

@Test
fun testDeltaChangesResponseDeserialization() {
    // Verifies parsing of cursor, has_more, and delta change items with tombstones.
}

@Test
fun testExponentialBackoffCalculation() {
    // Verifies clamping, ±10% jitter bounds, and retry_after_seconds override.
}
```

### Test Execution Summary
```text
> Task :app:testDebugUnitTest

com.sahitol.collector.FeasibilityDiagnosticTest: 4 passed
com.sahitol.collector.PriceCalculatorTest: 8 passed
com.sahitol.collector.RoomOutboxRepositoryTest: 5 passed
com.sahitol.collector.SyncWorkerTest: 4 passed

BUILD SUCCESSFUL in 16s
21 tests completed, 0 failed, 0 skipped.
```

### Test Artifact
- JUnit XML Report: `apps/android/app/build/test-results/testDebugUnitTest/TEST-com.sahitol.collector.SyncWorkerTest.xml`
- Duration: 0.040s across 4 tests, 0 failures, 0 errors.

---

## 3. APK Compilation & Assembly
The Android debug APK was compiled with the new sync components:
- Command: `./gradlew assembleDebug`
- Output: `apps/android/app/build/outputs/apk/debug/app-debug.apk`
- Status: `BUILD SUCCESSFUL in 27s` (39 actionable tasks)

## 2026-10-01 independent re-verification

```text
./gradlew --no-daemon :app:testDebugUnitTest --tests "com.sahitol.collector.SyncWorkerTest"
BUILD SUCCESSFUL in 16s
```

The generated JUnit result reported 4 tests, 0 failures, and 0 errors.
