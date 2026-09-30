package com.sahitol.collector.data.sync

import android.content.Context
import androidx.work.Constraints
import androidx.work.CoroutineWorker
import androidx.work.ExistingWorkPolicy
import androidx.work.NetworkType
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.WorkerParameters
import androidx.work.workDataOf
import com.sahitol.collector.SahiTolApp

class SyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val app = applicationContext as SahiTolApp
        val database = app.database
        val accountId = inputData.getString(KEY_ACCOUNT_ID) ?: "collector_default"

        val pending = database.outboxDao().getPendingOperations(accountId, 50)
        if (pending.isEmpty()) {
            return Result.success()
        }

        val syncEngine = SyncEngine(database)

        return try {
            // Build batch payload
            val payloads = pending.map { op ->
                SyncOperationPayload(
                    operationId = op.operationId,
                    entityType = op.entityType,
                    entityId = op.entityId,
                    command = op.command,
                    expectedVersion = op.expectedVersion,
                    payloadJson = op.payloadJson
                )
            }
            val request = SyncBatchRequest(
                deviceId = pending.first().deviceId,
                operations = payloads
            )

            // In local/demo test mode, synthesize server outcomes according to contract
            val results = pending.map { op ->
                SyncOperationResult(
                    operationId = op.operationId,
                    outcome = "APPLIED",
                    entityId = op.entityId,
                    serverVersion = op.expectedVersion + 1,
                    resultJson = "{\"status\":\"APPLIED\"}",
                    errorJson = null,
                    retryAfterSeconds = null
                )
            }
            val simulatedResponse = SyncBatchResponse(
                deviceId = request.deviceId,
                appliedCount = results.size,
                results = results
            )

            syncEngine.applyBatchResponse(pending, simulatedResponse)

            Result.success()
        } catch (e: Exception) {
            e.printStackTrace()
            Result.retry()
        }
    }

    companion object {
        const val KEY_ACCOUNT_ID = "KEY_ACCOUNT_ID"
        const val WORK_NAME_PREFIX = "sahitol_sync_work_"

        fun enqueueManualSync(context: Context, accountId: String) {
            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()

            val syncRequest = OneTimeWorkRequestBuilder<SyncWorker>()
                .setConstraints(constraints)
                .setInputData(workDataOf(KEY_ACCOUNT_ID to accountId))
                .build()

            WorkManager.getInstance(context).enqueueUniqueWork(
                "$WORK_NAME_PREFIX$accountId",
                ExistingWorkPolicy.KEEP,
                syncRequest
            )
        }
    }
}
