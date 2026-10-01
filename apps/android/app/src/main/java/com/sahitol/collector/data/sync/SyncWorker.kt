package com.sahitol.collector.data.sync

import android.content.Context
import android.util.Log
import androidx.work.Constraints
import androidx.work.CoroutineWorker
import androidx.work.ExistingWorkPolicy
import androidx.work.NetworkType
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.WorkerParameters
import androidx.work.workDataOf
import com.sahitol.collector.SahiTolApp
import com.sahitol.collector.BuildConfig
import java.net.HttpURLConnection
import java.net.URL
import java.util.UUID
import org.json.JSONArray
import org.json.JSONObject

class SyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val app = applicationContext as SahiTolApp
        val database = app.database
        val accountId = inputData.getString(KEY_ACCOUNT_ID) ?: "collector_default"

        // A deployed server repair changed only this formerly transient
        // collector-profile FK failure into a valid operation. Requeue that
        // exact historic row for an explicit manual sync; do not loosen the
        // treatment of any other repair-required record.
        val repaired = database.outboxDao().requeueLegacyCollectorProfileFailures(accountId)
        if (repaired > 0) Log.i(TAG, "Requeued $repaired legacy collector-profile operation(s)")
        val pending = database.outboxDao().getPendingOperations(accountId, 50)
        Log.i(TAG, "Manual sync loaded ${pending.size} pending operations")
        if (pending.isEmpty()) {
            return Result.success()
        }

        val syncEngine = SyncEngine(database)

        return try {
            val accessToken = if (accountId.startsWith("col_demo_")) demoAccessToken() else null
            val results = if (accessToken == null) {
                pending.map { operation ->
                    SyncOperationResult(operation.operationId, "AUTH_REQUIRED", operation.entityId, null, null, "Authentication required", null)
                }
            } else {
                syncPendingOperations(pending, accessToken)
            }
            syncEngine.applyBatchResponse(
                pending,
                SyncBatchResponse(pending.first().deviceId, results.count { it.outcome in setOf("APPLIED", "ALREADY_APPLIED") }, results)
            )
            Log.i(TAG, "Manual sync applied ${results.size} operation outcomes")

            Result.success()
        } catch (e: Exception) {
            e.printStackTrace()
            Result.retry()
        }
    }

    private fun demoAccessToken(): String? {
        val response = postJson(
            "/api/v1/auth/demo",
            JSONObject().put("role", "COLLECTOR").put("persona_id", "santosh").put("device_id", "android-device")
        ) ?: return null
        return if (response.first in 200..299) JSONObject(response.second).optString("access_token").ifBlank { null } else null
    }

    private fun syncPendingOperations(
        pending: List<com.sahitol.collector.data.local.entity.OutboxOperationEntity>,
        accessToken: String
    ): List<SyncOperationResult> {
        val results = mutableListOf<SyncOperationResult>()
        val normalOperations = mutableListOf<com.sahitol.collector.data.local.entity.OutboxOperationEntity>()

        pending.forEach { operation ->
            if (operation.entityType == "HANDOVER_PROPOSAL" && operation.command == "CREATE_HANDOVER_PROPOSAL") {
                results += syncHandoverProposal(operation, accessToken)
            } else if (!isValidBatchOperation(operation)) {
                // FastAPI validates UUIDs before entering the per-operation
                // handler. Do not let a historical/demo placeholder poison the
                // whole batch; surface a repairable local error instead.
                results += SyncOperationResult(
                    operation.operationId, "REJECTED", operation.entityId, null, null,
                    "Unsupported or malformed local operation; create a corrected replacement.", null
                )
            } else {
                normalOperations += operation
            }
        }

        if (normalOperations.isNotEmpty()) {
            results += syncBatch(normalOperations, accessToken)
        }
        return results
    }

    private fun isValidBatchOperation(operation: com.sahitol.collector.data.local.entity.OutboxOperationEntity): Boolean = try {
        UUID.fromString(operation.operationId)
        UUID.fromString(operation.entityId)
        JSONObject(operation.payloadJson)
        val dependencies = JSONArray(operation.dependsOnJson)
        for (index in 0 until dependencies.length()) UUID.fromString(dependencies.getString(index))
        val mediaIds = JSONArray(operation.mediaIdsJson)
        for (index in 0 until mediaIds.length()) UUID.fromString(mediaIds.getString(index))
        true
    } catch (_: Exception) {
        false
    }

    private fun syncBatch(
        operations: List<com.sahitol.collector.data.local.entity.OutboxOperationEntity>,
        accessToken: String
    ): List<SyncOperationResult> {
        val request = SyncBatchRequest(
            deviceId = operations.first().deviceId,
            operations = operations.map { operation ->
                SyncOperationPayload(
                    operationId = operation.operationId,
                    entityType = operation.entityType,
                    entityId = operation.entityId,
                    command = operation.command,
                    expectedVersion = operation.expectedVersion,
                    payloadJson = operation.payloadJson,
                    dependsOn = JSONArray(operation.dependsOnJson).let { array ->
                        List(array.length()) { index -> array.getString(index) }
                    },
                    mediaIds = JSONArray(operation.mediaIdsJson).let { array ->
                        List(array.length()) { index -> array.getString(index) }
                    }
                )
            }
        )
        val response = postJson("/api/v1/sync/batch", JSONObject(request.toJson()), accessToken)
            ?: return operations.map { operation ->
                SyncOperationResult(operation.operationId, "RETRY", operation.entityId, null, null, "Network request failed", null)
            }
        if (response.first !in 200..299) {
            val outcome = if (response.first == 401 || response.first == 403) "AUTH_REQUIRED" else "RETRY"
            return operations.map { operation ->
                SyncOperationResult(operation.operationId, outcome, operation.entityId, null, null, response.second, null)
            }
        }
        return SyncBatchResponse.fromJson(response.second).results
    }

    private fun syncHandoverProposal(
        operation: com.sahitol.collector.data.local.entity.OutboxOperationEntity,
        accessToken: String?
    ): SyncOperationResult {
        if (operation.entityType != "HANDOVER_PROPOSAL" || operation.command != "CREATE_HANDOVER_PROPOSAL") {
            return SyncOperationResult(operation.operationId, "DEPENDENCY_PENDING", operation.entityId, null, null, null, null)
        }
        if (accessToken == null) {
            return SyncOperationResult(operation.operationId, "AUTH_REQUIRED", operation.entityId, null, null, "Demo authentication failed", null)
        }
        val request = JSONObject()
            .put("id", operation.entityId)
            .put("proposal_payload", JSONObject(operation.payloadJson))
            .put("proposal_hash", operation.payloadSha256)
            .put("expected_version", operation.expectedVersion)
        val response = postJson("/api/v1/demo/handovers/import", request, accessToken)
            ?: return SyncOperationResult(operation.operationId, "RETRY", operation.entityId, null, null, "Network request failed", null)
        return when (response.first) {
            in 200..299 -> {
                val body = JSONObject(response.second)
                SyncOperationResult(operation.operationId, "APPLIED", operation.entityId, body.optLong("version", 1), body.toString(), null, null)
            }
            401, 403 -> SyncOperationResult(operation.operationId, "AUTH_REQUIRED", operation.entityId, null, null, response.second, null)
            409 -> SyncOperationResult(operation.operationId, "CONFLICT", operation.entityId, null, null, response.second, null)
            in 400..499 -> SyncOperationResult(operation.operationId, "REJECTED", operation.entityId, null, null, response.second, null)
            else -> SyncOperationResult(operation.operationId, "RETRY", operation.entityId, null, null, response.second, null)
        }
    }

    private fun postJson(path: String, body: JSONObject, accessToken: String? = null): Pair<Int, String>? = try {
        val connection = (URL(BuildConfig.API_BASE_URL.trimEnd('/') + path).openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            connectTimeout = 15_000
            readTimeout = 20_000
            doOutput = true
            setRequestProperty("Content-Type", "application/json")
            setRequestProperty("Accept", "application/json")
            accessToken?.let { setRequestProperty("Authorization", "Bearer $it") }
        }
        connection.outputStream.bufferedWriter().use { it.write(body.toString()) }
        val code = connection.responseCode
        val stream = if (code in 200..299) connection.inputStream else connection.errorStream
        val text = stream?.bufferedReader()?.use { it.readText() }.orEmpty()
        connection.disconnect()
        code to text
    } catch (_: Exception) {
        null
    }

    companion object {
        const val KEY_ACCOUNT_ID = "KEY_ACCOUNT_ID"
        const val WORK_NAME_PREFIX = "sahitol_sync_work_"
        private const val TAG = "SahiTolSync"

        fun workName(accountId: String) = "$WORK_NAME_PREFIX$accountId"

        fun enqueueManualSync(context: Context, accountId: String) {
            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()

            val syncRequest = OneTimeWorkRequestBuilder<SyncWorker>()
                .setConstraints(constraints)
                .setInputData(workDataOf(KEY_ACCOUNT_ID to accountId))
                .build()

            WorkManager.getInstance(context).enqueueUniqueWork(
                workName(accountId),
                // A foreground manual action must not be silently ignored by a
                // stale retry. The cancelled worker retains its durable outbox;
                // the replacement reuses the same operation IDs.
                ExistingWorkPolicy.REPLACE,
                syncRequest
            )
        }
    }
}
