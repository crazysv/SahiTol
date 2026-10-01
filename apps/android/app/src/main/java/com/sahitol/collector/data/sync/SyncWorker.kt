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
import com.sahitol.collector.BuildConfig
import java.net.HttpURLConnection
import java.net.URL
import org.json.JSONObject

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
            val accessToken = if (accountId.startsWith("col_demo_")) demoAccessToken() else null
            val results = pending.map { operation -> syncOperation(operation, accessToken) }
            syncEngine.applyBatchResponse(
                pending,
                SyncBatchResponse(pending.first().deviceId, results.count { it.outcome in setOf("APPLIED", "ALREADY_APPLIED") }, results)
            )

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

    private fun syncOperation(
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
