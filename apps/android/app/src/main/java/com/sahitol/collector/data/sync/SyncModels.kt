package com.sahitol.collector.data.sync

import org.json.JSONArray
import org.json.JSONObject

data class SyncBatchRequest(
    val deviceId: String,
    val operations: List<SyncOperationPayload>
) {
    fun toJson(): String {
        val root = JSONObject()
        root.put("device_id", deviceId)
        val opsArray = JSONArray()
        for (op in operations) {
            opsArray.put(op.toJSONObject())
        }
        root.put("operations", opsArray)
        return root.toString()
    }
}

data class SyncOperationPayload(
    val operationId: String,
    val entityType: String,
    val entityId: String,
    val command: String,
    val expectedVersion: Long,
    val payloadJson: String,
    val dependsOn: List<String> = emptyList(),
    val mediaIds: List<String> = emptyList()
) {
    fun toJSONObject(): JSONObject {
        return JSONObject().apply {
            put("operation_id", operationId)
            put("entity_type", entityType)
            put("entity_id", entityId)
            put("command", command)
            put("expected_version", expectedVersion)
            put("payload", JSONObject(payloadJson))
            put("depends_on", JSONArray(dependsOn))
            put("media_ids", JSONArray(mediaIds))
        }
    }
}

data class SyncBatchResponse(
    val deviceId: String,
    val appliedCount: Int,
    val results: List<SyncOperationResult>
) {
    companion object {
        fun fromJson(jsonStr: String): SyncBatchResponse {
            val root = JSONObject(jsonStr)
            val devId = root.optString("device_id", "")
            val applied = root.optInt("applied_count", 0)
            val resultsArr = root.optJSONArray("results") ?: JSONArray()
            val resList = mutableListOf<SyncOperationResult>()

            for (i in 0 until resultsArr.length()) {
                val item = resultsArr.getJSONObject(i)
                resList.add(
                    SyncOperationResult(
                        operationId = item.getString("operation_id"),
                        outcome = item.getString("outcome"),
                        entityId = item.optString("entity_id", ""),
                        serverVersion = if (item.has("server_version") && !item.isNull("server_version")) item.getLong("server_version") else null,
                        resultJson = item.optJSONObject("result")?.toString(),
                        errorJson = item.optJSONObject("error")?.toString(),
                        retryAfterSeconds = if (item.has("retry_after_seconds") && !item.isNull("retry_after_seconds")) item.getInt("retry_after_seconds") else null
                    )
                )
            }

            return SyncBatchResponse(devId, applied, resList)
        }
    }
}

data class SyncOperationResult(
    val operationId: String,
    val outcome: String, // APPLIED, ALREADY_APPLIED, RETRY, AUTH_REQUIRED, CONFLICT, REJECTED, DEPENDENCY_PENDING
    val entityId: String,
    val serverVersion: Long?,
    val resultJson: String?,
    val errorJson: String?,
    val retryAfterSeconds: Int?
)

data class DeltaChangeItem(
    val entityType: String,
    val entityId: String,
    val version: Long,
    val operation: String, // UPSERT, DELETE
    val dataJson: String
)

data class DeltaChangesResponse(
    val changes: List<DeltaChangeItem>,
    val nextCursor: String?,
    val hasMore: Boolean
) {
    companion object {
        fun fromJson(jsonStr: String): DeltaChangesResponse {
            val root = JSONObject(jsonStr)
            val dataObj = root.optJSONObject("data") ?: JSONObject()
            val metaObj = root.optJSONObject("meta") ?: JSONObject()

            val changesArr = dataObj.optJSONArray("changes") ?: JSONArray()
            val list = mutableListOf<DeltaChangeItem>()
            for (i in 0 until changesArr.length()) {
                val item = changesArr.getJSONObject(i)
                list.add(
                    DeltaChangeItem(
                        entityType = item.getString("entity_type"),
                        entityId = item.getString("entity_id"),
                        version = item.optLong("version", 1L),
                        operation = item.optString("operation", "UPSERT"),
                        dataJson = item.optJSONObject("data")?.toString() ?: "{}"
                    )
                )
            }

            return DeltaChangesResponse(
                changes = list,
                nextCursor = if (metaObj.has("next_cursor") && !metaObj.isNull("next_cursor")) metaObj.getString("next_cursor") else null,
                hasMore = metaObj.optBoolean("has_more", false)
            )
        }
    }
}
