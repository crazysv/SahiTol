package com.sahitol.collector.data.repository

import androidx.room.withTransaction
import com.sahitol.collector.data.local.SahiTolDatabase
import com.sahitol.collector.data.local.entity.DomainEventEntity
import com.sahitol.collector.data.local.entity.LotEntity
import com.sahitol.collector.data.local.entity.OutboxOperationEntity
import kotlinx.coroutines.flow.Flow
import org.json.JSONObject
import java.security.MessageDigest
import java.util.UUID

data class CreateLotParams(
    val accountId: String,
    val deviceId: String,
    val materialCode: String,
    val estimatedWeightG: Long,
    val estimatedLowPaise: Long? = null,
    val estimatedMedianPaise: Long? = null,
    val estimatedHighPaise: Long? = null,
    val localPhotoPath: String? = null,
    val aiSuggestedCode: String? = null,
    val aiConfidence: Float? = null,
    val aiModelVersion: String? = null
)

class LotRepository(private val database: SahiTolDatabase) {

    private val GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    /**
     * Atomically commits a new lot, its audit event, and its queued outbox operation
     * in a single ACID database transaction.
     */
    suspend fun createLotAtomic(params: CreateLotParams): LotEntity {
        val lotId = UUID.randomUUID().toString()
        val eventId = UUID.randomUUID().toString()
        val operationId = UUID.randomUUID().toString()
        val timestamp = System.currentTimeMillis()

        val lotEntity = LotEntity(
            lotId = lotId,
            accountId = params.accountId,
            materialCode = params.materialCode,
            estimatedWeightG = params.estimatedWeightG,
            measuredWeightG = null,
            estimatedLowPaise = params.estimatedLowPaise,
            estimatedMedianPaise = params.estimatedMedianPaise,
            estimatedHighPaise = params.estimatedHighPaise,
            localPhotoPath = params.localPhotoPath,
            status = "DRAFT",
            syncStatus = "SAVED_LOCAL_ONLY",
            serverVersion = 0,
            aiSuggestedCode = params.aiSuggestedCode,
            aiConfidence = params.aiConfidence,
            aiModelVersion = params.aiModelVersion,
            createdAt = timestamp,
            updatedAt = timestamp
        )

        // Construct canonical payload
        val payloadObj = JSONObject().apply {
            put("lot_id", lotId)
            put("material_code", params.materialCode)
            put("estimated_weight_g", params.estimatedWeightG)
            if (params.estimatedLowPaise != null) put("estimated_low_paise", params.estimatedLowPaise)
            if (params.estimatedMedianPaise != null) put("estimated_median_paise", params.estimatedMedianPaise)
            if (params.estimatedHighPaise != null) put("estimated_high_paise", params.estimatedHighPaise)
            if (params.aiSuggestedCode != null) put("ai_suggested_code", params.aiSuggestedCode)
            if (params.aiConfidence != null) put("ai_confidence", params.aiConfidence)
            if (params.aiModelVersion != null) put("ai_model_version", params.aiModelVersion)
            put("created_at", timestamp)
        }
        val payloadJson = payloadObj.toString()
        val payloadSha256 = sha256(payloadJson)

        val eventHash = sha256("$GENESIS_HASH:LOT_CREATED:$payloadJson")

        val domainEvent = DomainEventEntity(
            eventId = eventId,
            accountId = params.accountId,
            entityType = "LOT",
            entityId = lotId,
            eventType = "LOT_CREATED",
            payloadJson = payloadJson,
            prevHash = GENESIS_HASH,
            currentHash = eventHash,
            createdAt = timestamp
        )

        val outboxOp = OutboxOperationEntity(
            operationId = operationId,
            accountId = params.accountId,
            deviceId = params.deviceId,
            entityType = "LOT",
            entityId = lotId,
            command = "CREATE_LOT",
            expectedVersion = 0,
            payloadJson = payloadJson,
            payloadSha256 = payloadSha256,
            dependsOnJson = "[]",
            mediaIdsJson = if (params.localPhotoPath != null) "[\"${params.localPhotoPath}\"]" else "[]",
            createdAt = timestamp,
            attemptCount = 0,
            nextAttemptAt = timestamp,
            state = "QUEUED",
            lastErrorCode = null
        )

        // Execute atomic commit
        database.withTransaction {
            database.lotDao().insertLot(lotEntity)
            database.domainEventDao().insertEvent(domainEvent)
            database.outboxDao().enqueue(outboxOp)
        }

        return lotEntity
    }

    suspend fun getLotById(lotId: String): LotEntity? {
        return database.lotDao().getLotById(lotId)
    }

    suspend fun getLotsForAccount(accountId: String): List<LotEntity> {
        return database.lotDao().getLotsForAccount(accountId)
    }

    fun getLotsForAccountFlow(accountId: String): Flow<List<LotEntity>> {
        return database.lotDao().getLotsForAccountFlow(accountId)
    }

    suspend fun getUnsyncedCount(accountId: String): Int {
        return database.outboxDao().getUnsyncedCount(accountId)
    }

    suspend fun getPendingOutboxOperations(accountId: String, limit: Int = 50): List<OutboxOperationEntity> {
        return database.outboxDao().getPendingOperations(accountId, limit)
    }

    /**
     * Verifies the cryptographic integrity of an entity's domain event hash-chain.
     */
    suspend fun verifyEntityLineage(entityId: String): Boolean {
        val events = database.domainEventDao().getEventsForEntity("LOT", entityId)
        if (events.isEmpty()) return false

        var expectedPrev = GENESIS_HASH
        for (event in events) {
            if (event.prevHash != expectedPrev) return false
            val calculated = sha256("${event.prevHash}:${event.eventType}:${event.payloadJson}")
            if (event.currentHash != calculated) return false
            expectedPrev = event.currentHash
        }
        return true
    }

    /**
     * Safe logout contract:
     * Unsynced records and outbox operations are preserved in SQLite across sessions.
     * Ephemeral session tokens are revoked, but local user work is NOT deleted.
     */
    suspend fun prepareLogoutPreservingData(accountId: String): Int {
        return database.outboxDao().getUnsyncedCount(accountId)
    }

    companion object {
        fun sha256(input: String): String {
            val bytes = MessageDigest.getInstance("SHA-256").digest(input.toByteArray(Charsets.UTF_8))
            return bytes.joinToString("") { "%02x".format(it) }
        }
    }
}
