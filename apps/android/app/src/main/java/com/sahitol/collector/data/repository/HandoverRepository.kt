package com.sahitol.collector.data.repository

import com.sahitol.collector.data.local.SahiTolDatabase
import com.sahitol.collector.data.local.dao.DomainEventDao
import com.sahitol.collector.data.local.dao.OutboxDao
import com.sahitol.collector.data.local.entity.DomainEventEntity
import com.sahitol.collector.data.local.entity.OutboxOperationEntity
import com.sahitol.collector.domain.canonical.CanonicalJson
import org.json.JSONArray
import org.json.JSONObject
import java.time.Instant
import java.net.URLEncoder
import java.util.UUID

data class HandoverProposal(
    val handoverId: String = UUID.randomUUID().toString(),
    val transactionId: String = UUID.randomUUID().toString(),
    val lotId: String,
    val collectorId: String,
    val facilityId: String,
    val facilityName: String = "Verma Electricals (Mayapuri)",
    val materialId: String,
    val materialName: String = "Copper Wire / Cable",
    val condition: String = "GOOD",
    val estimatedWeightG: Long,
    val measuredWeightG: Long? = null,
    val rateInrPerKg: Double = 745.0,
    val totalPayoutInr: Double,
    val referenceCode: String = "ST-24A7",
    val status: String = "PENDING_CONFIRMATION", // PENDING_CONFIRMATION, SYNCED_PENDING_RECYCLER, CONFIRMED, DISPUTED
    val canonicalHash: String,
    val verificationUrl: String = "https://sahitol.in/v/$handoverId",
    val occurredAt: String = Instant.now().toString(),
    val isDemo: Boolean = true
)

data class PassportTimelineEvent(
    val stageIndex: Int,
    val titleEn: String,
    val titleHi: String,
    val timestamp: String,
    val description: String,
    val iconType: String,
    val isCompleted: Boolean,
    val isWarningOrDispute: Boolean = false,
    val metadataSnippet: String? = null
)

class HandoverRepository(
    private val database: SahiTolDatabase? = null,
    private val outboxDao: OutboxDao? = database?.outboxDao(),
    private val domainEventDao: DomainEventDao? = database?.domainEventDao()
) {

    // In-memory cache for fast local UI preview and offline navigation
    private val proposalsCache = mutableMapOf<String, HandoverProposal>()

    suspend fun createProposalAtomic(
        lotId: String,
        collectorId: String,
        facilityId: String,
        facilityName: String,
        materialId: String,
        materialName: String,
        condition: String,
        estimatedWeightG: Long,
        measuredWeightG: Long?,
        rateInrPerKg: Double,
        totalPayoutInr: Double,
        isDemo: Boolean = true
    ): HandoverProposal {
        val handoverId = UUID.randomUUID().toString()
        val txId = UUID.randomUUID().toString()
        val now = Instant.now().toString()
        val refCode = "ST-" + UUID.randomUUID().toString().take(4).uppercase()

        // Build canonical SAHITOL-HANDOVER-1 payload map
        val payloadMap = mapOf(
            "schema_version" to "SAHITOL-HANDOVER-1",
            "handover_id" to handoverId,
            "transaction_id" to txId,
            "lot_id" to lotId,
            "collector_id" to collectorId,
            "facility_id" to facilityId,
            "agreed_terms_hash" to null,
            "material_snapshot" to mapOf(
                "material_id" to materialId,
                "condition" to condition,
                "regulatory_route" to if (materialId.contains("BAT")) "HAZARDOUS_BATTERY" else "E_WASTE"
            ),
            "weight_snapshot" to mapOf(
                "estimated_weight_g" to estimatedWeightG,
                "measured_weight_g" to measuredWeightG
            ),
            "value_snapshot" to mapOf(
                "currency" to "INR",
                "estimated_low_paise" to ((totalPayoutInr * 0.95) * 100).toLong(),
                "estimated_high_paise" to ((totalPayoutInr * 1.05) * 100).toLong(),
                "agreed_total_paise" to (totalPayoutInr * 100).toLong()
            ),
            "location_snapshot" to mapOf(
                "location_id" to null,
                "source" to "COARSE_GPS",
                "accuracy_m" to 50,
                "captured_at" to now
            ),
            "occurred_at" to now,
            "media" to emptyList<String>(),
            "is_demo" to isDemo
        )

        val canonicalUtf8 = CanonicalJson.serialize(payloadMap)
        val canonicalHash = CanonicalJson.sha256Hex(canonicalUtf8)
        // This offline QR deliberately carries only custody-verification data.
        // It excludes collector PII, GPS, images, and any payment amount.
        val qrMaterial = URLEncoder.encode(materialName, "UTF-8")
        val qrWeightKg = (measuredWeightG ?: estimatedWeightG).toDouble() / 1000.0
        val verificationUrl = "https://sahitol.pages.dev/recycler/scan" +
            "?ref=$refCode&material=$qrMaterial&weight=$qrWeightKg&hash=$canonicalHash"

        val proposal = HandoverProposal(
            handoverId = handoverId,
            transactionId = txId,
            lotId = lotId,
            collectorId = collectorId,
            facilityId = facilityId,
            facilityName = facilityName,
            materialId = materialId,
            materialName = materialName,
            condition = condition,
            estimatedWeightG = estimatedWeightG,
            measuredWeightG = measuredWeightG,
            rateInrPerKg = rateInrPerKg,
            totalPayoutInr = totalPayoutInr,
            referenceCode = refCode,
            status = "PENDING_CONFIRMATION",
            canonicalHash = canonicalHash,
            verificationUrl = verificationUrl,
            occurredAt = now,
            isDemo = isDemo
        )

        proposalsCache[handoverId] = proposal
        proposalsCache[lotId] = proposal

        val outboxOp = OutboxOperationEntity(
            operationId = UUID.randomUUID().toString(),
            accountId = collectorId,
            deviceId = "android_device",
            entityType = "HANDOVER_PROPOSAL",
            entityId = handoverId,
            command = "CREATE_HANDOVER_PROPOSAL",
            expectedVersion = 0,
            payloadJson = canonicalUtf8,
            payloadSha256 = canonicalHash,
            state = "QUEUED",
            createdAt = System.currentTimeMillis()
        )

        val domainEvent = DomainEventEntity(
            eventId = UUID.randomUUID().toString(),
            accountId = collectorId,
            entityType = "HANDOVER_PROPOSAL",
            entityId = handoverId,
            eventType = "HANDOVER_PROPOSED",
            payloadJson = canonicalUtf8,
            prevHash = "0".repeat(64),
            currentHash = canonicalHash,
            createdAt = System.currentTimeMillis()
        )

        outboxDao?.enqueue(outboxOp)
        domainEventDao?.insertEvent(domainEvent)

        return proposal
    }

    suspend fun recordDiscrepancyResponseAtomic(
        handoverId: String,
        action: String, // "ACCEPT_TERMS" or "DISPUTE_TERMS"
        collectorId: String,
        reason: String? = null
    ): HandoverProposal {
        val existing = proposalsCache[handoverId] ?: HandoverProposal(
            handoverId = handoverId,
            lotId = "lot-demo-01",
            collectorId = collectorId,
            facilityId = "fac-verma-01",
            estimatedWeightG = 2500,
            measuredWeightG = 2300,
            totalPayoutInr = 414.0,
            canonicalHash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            materialId = "MAT-CAB-01"
        )

        val newStatus = if (action == "ACCEPT_TERMS") "PENDING_CONFIRMATION" else "DISPUTED"
        val updated = existing.copy(status = newStatus)
        proposalsCache[handoverId] = updated

        val payload = JSONObject().apply {
            put("handover_id", handoverId)
            put("action", action)
            put("collector_id", collectorId)
            put("reason", reason ?: "Scale measured difference")
            put("responded_at", Instant.now().toString())
        }.toString()

        val digest = CanonicalJson.sha256Hex(payload)

        val outboxOp = OutboxOperationEntity(
            operationId = UUID.randomUUID().toString(),
            accountId = collectorId,
            deviceId = "android_device",
            entityType = "HANDOVER_REVISION",
            entityId = handoverId,
            command = if (action == "ACCEPT_TERMS") "ACCEPT_TERMS_REVISION" else "DISPUTE_HANDOVER",
            expectedVersion = 0,
            payloadJson = payload,
            payloadSha256 = digest,
            state = "QUEUED",
            createdAt = System.currentTimeMillis()
        )

        val domainEvent = DomainEventEntity(
            eventId = UUID.randomUUID().toString(),
            accountId = collectorId,
            entityType = "HANDOVER_REVISION",
            entityId = handoverId,
            eventType = if (action == "ACCEPT_TERMS") "TERMS_REVISION_ACCEPTED" else "HANDOVER_DISPUTED",
            payloadJson = payload,
            prevHash = existing.canonicalHash,
            currentHash = digest,
            createdAt = System.currentTimeMillis()
        )

        outboxDao?.enqueue(outboxOp)
        domainEventDao?.insertEvent(domainEvent)

        return updated
    }

    fun getHandoverProposal(id: String): HandoverProposal {
        return proposalsCache[id] ?: HandoverProposal(
            handoverId = id,
            lotId = id,
            collectorId = "col_test_santosh",
            facilityId = "fac-verma-01",
            facilityName = "Verma Electricals (Okhla Hub)",
            materialId = "MAT-CAB-01",
            materialName = "Copper Wire / Cable · तांबा केबल",
            condition = "GOOD",
            estimatedWeightG = 2500,
            measuredWeightG = 2300,
            rateInrPerKg = 180.0,
            totalPayoutInr = 414.0,
            referenceCode = "ST-24A7",
            status = "PENDING_CONFIRMATION",
            canonicalHash = "8f9c1042735d4918e72b1d767cca58ac80c59667b59b86f511ebf11b64e3b21",
            occurredAt = "14 Oct, 02:00 PM",
            isDemo = true
        )
    }

    fun getJourneyTimeline(lotId: String): List<PassportTimelineEvent> {
        return listOf(
            PassportTimelineEvent(
                stageIndex = 1,
                titleEn = "Collection & Weighing",
                titleHi = "संग्रह एवं वजन",
                timestamp = "14 Oct, 09:30 AM",
                description = "Lot drafted with 2.5 kg estimated mass. High-wear cable classification verified.",
                iconType = "SCALE",
                isCompleted = true,
                metadataSnippet = "GPS: 28.5355° N, 77.2810° E · Okhla Phase 2"
            ),
            PassportTimelineEvent(
                stageIndex = 2,
                titleEn = "Commercial Offer Agreed",
                titleHi = "व्यापारिक प्रस्ताव स्वीकृत",
                timestamp = "14 Oct, 10:15 AM",
                description = "Verma Electricals quote accepted at ₹180.00/kg. Zero collector fee guarantee.",
                iconType = "OFFER",
                isCompleted = true,
                metadataSnippet = "Total Value Locked: ₹450.00"
            ),
            PassportTimelineEvent(
                stageIndex = 3,
                titleEn = "Yard Handover & Scale Reconciliation",
                titleHi = "हस्तनांतरण एवं कांटा मिलान",
                timestamp = "14 Oct, 02:00 PM",
                description = "Gross measured weight: 2.3 kg (-200g insulation tare). Terms revision acknowledged.",
                iconType = "HANDOVER",
                isCompleted = true,
                isWarningOrDispute = false,
                metadataSnippet = "Final Scale Tare: 2.3 kg · Net ₹414.00"
            ),
            PassportTimelineEvent(
                stageIndex = 4,
                titleEn = "Digital Handover Record Generated",
                titleHi = "डिजिटल रसीद जारी",
                timestamp = "14 Oct, 02:05 PM",
                description = "Tamper-evident QR and SHA-256 seal issued. Awaiting online sync & confirmation.",
                iconType = "RECEIPT",
                isCompleted = true,
                metadataSnippet = "Reference: ST-24A7 · Hash: 0x8f9c...3b21"
            ),
            PassportTimelineEvent(
                stageIndex = 5,
                titleEn = "Payment Settlement",
                titleHi = "भुगतान निपटान",
                timestamp = "Pending",
                description = "Direct cash or instant UPI settlement pending yard closure. ₹414.00 due.",
                iconType = "PAYMENT",
                isCompleted = false,
                metadataSnippet = "Remaining Due: ₹414.00"
            )
        )
    }
}
