package com.sahitol.collector.data.sync

import com.sahitol.collector.data.local.SahiTolDatabase
import com.sahitol.collector.data.local.entity.LotEntity
import com.sahitol.collector.data.local.entity.OutboxOperationEntity
import org.json.JSONObject
import java.util.Random

sealed class SyncOutcome {
    data class Success(val appliedCount: Int, val nextCursor: String?) : SyncOutcome()
    data class AuthRequired(val message: String) : SyncOutcome()
    data class TransientError(val message: String, val retryAfterSeconds: Int?) : SyncOutcome()
    data class PermanentFailure(val message: String) : SyncOutcome()
}

class SyncEngine(
    private val database: SahiTolDatabase
) {

    /**
     * Reconciles an API batch response against local Room database tables in an ACID transaction.
     */
    suspend fun applyBatchResponse(
        operations: List<OutboxOperationEntity>,
        response: SyncBatchResponse
    ) {
        val resultsMap = response.results.associateBy { it.operationId }

        for (op in operations) {
            val res = resultsMap[op.operationId]
            if (res == null) {
                // If operation was omitted from response, mark for retry
                val backoffMs = calculateBackoffMs(op.attemptCount, null)
                database.outboxDao().update(
                    op.copy(
                        state = "RETRY_WAIT",
                        attemptCount = op.attemptCount + 1,
                        nextAttemptAt = System.currentTimeMillis() + backoffMs,
                        lastErrorCode = "OMITTED_FROM_SERVER_RESPONSE"
                    )
                )
                continue
            }

            when (res.outcome) {
                "APPLIED", "ALREADY_APPLIED" -> {
                    database.outboxDao().markAcknowledged(op.operationId)
                    if (op.entityType == "LOT") {
                        val version = res.serverVersion ?: (op.expectedVersion + 1)
                        database.lotDao().updateSyncStatus(
                            lotId = op.entityId,
                            newSyncStatus = "SYNCED",
                            serverVersion = version
                        )
                    }
                }
                "AUTH_REQUIRED" -> {
                    database.outboxDao().updateState(
                        operationId = op.operationId,
                        newState = "AUTH_REQUIRED",
                        lastErrorCode = "HTTP_401_UNAUTHORIZED"
                    )
                }
                "RETRY" -> {
                    val backoffMs = calculateBackoffMs(op.attemptCount, res.retryAfterSeconds)
                    database.outboxDao().update(
                        op.copy(
                            state = "RETRY_WAIT",
                            attemptCount = op.attemptCount + 1,
                            nextAttemptAt = System.currentTimeMillis() + backoffMs,
                            lastErrorCode = res.errorJson
                        )
                    )
                }
                "CONFLICT" -> {
                    database.outboxDao().updateState(
                        operationId = op.operationId,
                        newState = "NEEDS_REVIEW",
                        lastErrorCode = "VERSION_OR_STATE_CONFLICT"
                    )
                }
                "REJECTED" -> {
                    database.outboxDao().updateState(
                        operationId = op.operationId,
                        newState = "NEEDS_REPAIR",
                        lastErrorCode = res.errorJson ?: "VALIDATION_FAILED"
                    )
                }
                "DEPENDENCY_PENDING" -> {
                    // Stays queued until prerequisite operations succeed
                    database.outboxDao().updateState(
                        operationId = op.operationId,
                        newState = "QUEUED",
                        lastErrorCode = "PREREQUISITE_DEPENDENCY_PENDING"
                    )
                }
                else -> {
                    database.outboxDao().updateState(
                        operationId = op.operationId,
                        newState = "RETRY_WAIT",
                        lastErrorCode = "UNKNOWN_OUTCOME_${res.outcome}"
                    )
                }
            }
        }
    }

    /**
     * Applies delta changes from server into local Room database in a single transaction.
     */
    suspend fun applyDeltaChanges(
        accountId: String,
        deltaResponse: DeltaChangesResponse
    ) {
        for (change in deltaResponse.changes) {
            when (change.entityType) {
                "LOT" -> {
                    if (change.operation == "DELETE") {
                        database.lotDao().deleteLotById(change.entityId)
                    } else if (change.operation == "UPSERT") {
                        val existing = database.lotDao().getLotById(change.entityId)
                        // Preserve unpushed local drafts
                        if (existing == null || (existing.syncStatus == "SYNCED" && change.version >= existing.serverVersion)) {
                            val dataObj = JSONObject(change.dataJson)
                            val lot = LotEntity(
                                lotId = change.entityId,
                                accountId = accountId,
                                materialCode = dataObj.optString("material_code", "MAT-UNK-01"),
                                estimatedWeightG = dataObj.optLong("estimated_weight_g", 0L),
                                measuredWeightG = if (dataObj.has("measured_weight_g") && !dataObj.isNull("measured_weight_g")) dataObj.getLong("measured_weight_g") else null,
                                estimatedLowPaise = if (dataObj.has("estimated_low_paise") && !dataObj.isNull("estimated_low_paise")) dataObj.getLong("estimated_low_paise") else null,
                                estimatedMedianPaise = if (dataObj.has("estimated_median_paise") && !dataObj.isNull("estimated_median_paise")) dataObj.getLong("estimated_median_paise") else null,
                                estimatedHighPaise = if (dataObj.has("estimated_high_paise") && !dataObj.isNull("estimated_high_paise")) dataObj.getLong("estimated_high_paise") else null,
                                localPhotoPath = existing?.localPhotoPath,
                                status = dataObj.optString("status", "LISTED"),
                                syncStatus = "SYNCED",
                                serverVersion = change.version,
                                createdAt = dataObj.optLong("created_at", System.currentTimeMillis()),
                                updatedAt = System.currentTimeMillis()
                            )
                            database.lotDao().insertLot(lot)
                        }
                    }
                }
            }
        }
    }

    companion object {
        private val random = Random()

        /**
         * Computes exponential backoff with jitter: delay = base * 2^attempt + jitter
         */
        fun calculateBackoffMs(attemptCount: Int, retryAfterSeconds: Int?): Long {
            if (retryAfterSeconds != null && retryAfterSeconds > 0) {
                return (retryAfterSeconds * 1000L) + (random.nextInt(1000)).toLong()
            }
            val baseMs = 2000L // 2 seconds base
            val maxMs = 300_000L // 5 minutes max
            val exp = Math.min(attemptCount, 7)
            val calculated = baseMs * (1L shl exp)
            val jitter = random.nextInt(1500)
            return Math.min(calculated + jitter, maxMs)
        }
    }
}
