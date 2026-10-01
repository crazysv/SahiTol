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
    companion object {
        // Matches the isolated server-side demo recycler.  It is not a live facility ID.
        const val DEMO_RECYCLER_FACILITY_ID = "1aafb3d0-9ef2-4f34-95ca-0e6f3441e851"
    }

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
        val serverLotId = runCatching { UUID.fromString(lotId).toString() }.getOrElse {
            UUID.nameUUIDFromBytes("sahitol-demo-lot:$lotId".toByteArray()).toString()
        }
        val now = Instant.now().toString()
        val refCode = "ST-" + UUID.randomUUID().toString().take(4).uppercase()

        // Build canonical SAHITOL-HANDOVER-1 payload map
        val payloadMap = mapOf(
            "schema_version" to "SAHITOL-HANDOVER-1",
            "handover_id" to handoverId,
            "transaction_id" to txId,
            "lot_id" to serverLotId,
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
            "?handover_id=$handoverId&ref=$refCode&material=$qrMaterial&weight=$qrWeightKg&hash=$canonicalHash"

        val proposal = HandoverProposal(
            handoverId = handoverId,
            transactionId = txId,
            lotId = serverLotId,
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
            facilityId = DEMO_RECYCLER_FACILITY_ID,
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
            transactionId = "",
            collectorId = "",
            facilityId = "",
            facilityName = "Agreement not loaded",
            materialId = "",
            materialName = "No handover proposal available",
            condition = "Not recorded",
            estimatedWeightG = 0,
            measuredWeightG = null,
            rateInrPerKg = 0.0,
            totalPayoutInr = 0.0,
            referenceCode = "Not issued",
            status = "PENDING_CONFIRMATION",
            canonicalHash = "",
            verificationUrl = "",
            occurredAt = Instant.now().toString(),
            isDemo = false
        )
    }

    /** Cache only a proposal that the server accepted and assigned an ID to. */
    fun cacheServerProposal(
        result: LiveHandoverResult,
        agreement: AcceptedTransaction,
        offer: RecyclerOfferItem,
        materialId: String,
        materialName: String,
        facilityName: String
    ): HandoverProposal {
        val reference = "ST-" + result.handoverId.take(6).uppercase()
        val proposal = HandoverProposal(
            handoverId = result.handoverId,
            transactionId = agreement.transactionId,
            lotId = agreement.lotId,
            collectorId = agreement.collectorId,
            facilityId = agreement.facilityId,
            facilityName = facilityName,
            materialId = materialId,
            materialName = materialName,
            condition = "INTACT",
            estimatedWeightG = agreement.agreedWeightG,
            measuredWeightG = agreement.agreedWeightG,
            rateInrPerKg = if (agreement.agreedWeightG > 0) agreement.agreedTotalPaise / 100.0 * 1000 / agreement.agreedWeightG else 0.0,
            totalPayoutInr = agreement.agreedTotalPaise / 100.0,
            referenceCode = reference,
            status = result.status,
            canonicalHash = result.proposalHash,
            verificationUrl = "https://sahitol.pages.dev/recycler/scan?handover_id=${result.handoverId}&ref=$reference&hash=${result.proposalHash}",
            occurredAt = Instant.now().toString(),
            isDemo = agreement.isDemo
        )
        proposalsCache[result.handoverId] = proposal
        proposalsCache[agreement.lotId] = proposal
        return proposal
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
