package com.sahitol.collector.data.repository

import com.sahitol.collector.data.local.SahiTolDatabase
import com.sahitol.collector.data.local.dao.DomainEventDao
import com.sahitol.collector.data.local.dao.OutboxDao
import com.sahitol.collector.data.local.entity.DomainEventEntity
import com.sahitol.collector.data.local.entity.OutboxOperationEntity
import com.sahitol.collector.domain.matching.MatchingEngine
import com.sahitol.collector.domain.matching.MatchingEngine.LotParameters
import com.sahitol.collector.domain.matching.MatchingEngine.MatchingCandidate
import com.sahitol.collector.domain.matching.MatchingEngine.MatchOutcome
import org.json.JSONObject
import java.security.MessageDigest
import java.util.UUID

data class RecyclerFacilityItem(
    val facilityId: String,
    val nameEn: String,
    val nameLocal: String,
    val address: String,
    val distanceKm: Double,
    val travelTimeMinutes: Int,
    val materialsAccepted: List<String>,
    val instantUpi: Boolean,
    val operatingHours: String,
    val rateInrPerKg: Double,
    val verificationLevel: String,
    val routeCode: String,
    val trustScorePct: Double = 99.4,
    val offersPickup: Boolean = true,
    val latitude: Double? = 28.6358,
    val longitude: Double? = 77.1256
)

data class RecyclerOfferItem(
    val offerId: String,
    val facilityId: String,
    val facilityName: String,
    val routeDescription: String,
    val distanceKm: Double,
    val rateInrPerKg: Double,
    val totalPayoutInr: Double,
    val offerType: String, // "RATE_PER_KG" or "FIXED_TOTAL"
    val isBestMatch: Boolean = false,
    val isOfflinePending: Boolean = false,
    val status: String = "ACTIVE" // ACTIVE, ACCEPTED, REJECTED, EXPIRED
)

class FacilityRepository(
    private val database: SahiTolDatabase? = null,
    private val outboxDao: OutboxDao? = database?.outboxDao(),
    private val domainEventDao: DomainEventDao? = database?.domainEventDao()
) {

    private val defaultFacilities = listOf(
        RecyclerFacilityItem(
            facilityId = "fac-verma-01",
            nameEn = "Verma Electricals",
            nameLocal = "वर्मा इलेक्ट्रिकल्स",
            address = "Delhi Central Scrap Hub, Mayapuri Phase II",
            distanceKm = 1.2,
            travelTimeMinutes = 5,
            materialsAccepted = listOf("MAT-CAB-01", "MAT-CAB-02", "MAT-PCB-01"),
            instantUpi = true,
            operatingHours = "Open till 8:00 PM",
            rateInrPerKg = 190.0,
            verificationLevel = "L3",
            routeCode = "DL-408-C",
            trustScorePct = 99.4,
            latitude = 28.6380,
            longitude = 77.1280
        ),
        RecyclerFacilityItem(
            facilityId = "fac-shreeji-02",
            nameEn = "Shreeji Metal & Cable Yard",
            nameLocal = "श्रीमल डिपो",
            address = "Sector 4, Iron Market Lane, Dadar West",
            distanceKm = 1.8,
            travelTimeMinutes = 6,
            materialsAccepted = listOf("MAT-CAB-01", "MAT-MET-01"),
            instantUpi = true,
            operatingHours = "Open till 8:00 PM",
            rateInrPerKg = 480.0,
            verificationLevel = "L3",
            routeCode = "MH-DDR-01",
            trustScorePct = 98.7,
            latitude = 19.0178,
            longitude = 72.8478
        ),
        RecyclerFacilityItem(
            facilityId = "fac-navbharat-03",
            nameEn = "Navbharat Scrap Traders",
            nameLocal = "नवभारत ट्रेडर्स",
            address = "Plot 12, Station Road, Matunga West",
            distanceKm = 3.4,
            travelTimeMinutes = 12,
            materialsAccepted = listOf("MAT-CAB-01", "MAT-CAB-02", "MAT-PLA-01"),
            instantUpi = false,
            operatingHours = "Open till 7:30 PM",
            rateInrPerKg = 475.0,
            verificationLevel = "L2",
            routeCode = "MH-MTG-04",
            trustScorePct = 96.2,
            latitude = 19.0280,
            longitude = 72.8440
        ),
        RecyclerFacilityItem(
            facilityId = "fac-city-kabadi-04",
            nameEn = "City Kabadi Yard",
            nameLocal = "सिटी कबाड़ी यार्ड",
            address = "Direct Yard Drop, Okhla Industrial Area",
            distanceKm = 4.5,
            travelTimeMinutes = 18,
            materialsAccepted = listOf("MAT-CAB-01", "MAT-PCB-01", "MAT-MET-01"),
            instantUpi = true,
            operatingHours = "Open till 7:00 PM",
            rateInrPerKg = 170.0,
            verificationLevel = "L3",
            routeCode = "DL-OKH-12",
            trustScorePct = 97.5,
            latitude = 28.5355,
            longitude = 77.2718
        )
    )

    fun getFacilities(areaFilter: String? = null): List<RecyclerFacilityItem> {
        if (areaFilter.isNullOrBlank() || areaFilter.equals("ALL", ignoreCase = true)) {
            return defaultFacilities
        }
        return defaultFacilities.filter {
            it.address.contains(areaFilter, ignoreCase = true) ||
            it.nameEn.contains(areaFilter, ignoreCase = true)
        }
    }

    fun getFacilityDetails(facilityId: String): RecyclerFacilityItem? {
        return defaultFacilities.firstOrNull { it.facilityId == facilityId } ?: defaultFacilities.first()
    }

    fun getActiveOffers(lotWeightKg: Double = 2.5): List<RecyclerOfferItem> {
        return listOf(
            RecyclerOfferItem(
                offerId = "off-verma-01",
                facilityId = "fac-verma-01",
                facilityName = "Verma Electricals",
                routeDescription = "Standard Scrap Route #2 · 1.2 km away",
                distanceKm = 1.2,
                rateInrPerKg = 190.0,
                totalPayoutInr = 190.0 * lotWeightKg,
                offerType = "RATE_PER_KG",
                isBestMatch = true
            ),
            RecyclerOfferItem(
                offerId = "off-city-02",
                facilityId = "fac-city-kabadi-04",
                facilityName = "City Kabadi Yard",
                routeDescription = "Direct Yard Drop · 4.5 km away",
                distanceKm = 4.5,
                rateInrPerKg = 170.0,
                totalPayoutInr = 170.0 * lotWeightKg,
                offerType = "FIXED_TOTAL"
            ),
            RecyclerOfferItem(
                offerId = "off-patel-03",
                facilityId = "fac-patel-05",
                facilityName = "Patel Scrap Traders",
                routeDescription = "Saved offline · Waiting to sync",
                distanceKm = 2.8,
                rateInrPerKg = 180.0,
                totalPayoutInr = 180.0 * lotWeightKg,
                offerType = "RATE_PER_KG",
                isOfflinePending = true
            )
        )
    }

    suspend fun respondToOfferAtomic(
        offerId: String,
        action: String, // "ACCEPT_OFFER" or "REJECT_OFFER"
        accountId: String
    ): OutboxOperationEntity {
        val opId = UUID.randomUUID().toString()
        val now = System.currentTimeMillis()

        val payload = JSONObject().apply {
            put("offer_id", offerId)
            put("action", action)
            put("account_id", accountId)
            put("timestamp", now)
        }.toString()

        val digest = MessageDigest.getInstance("SHA-256")
            .digest(payload.toByteArray())
            .joinToString("") { "%02x".format(it) }

        val outboxOp = OutboxOperationEntity(
            operationId = opId,
            accountId = accountId,
            deviceId = "android_device",
            entityType = "OFFER",
            entityId = offerId,
            command = action,
            expectedVersion = 0,
            payloadJson = payload,
            payloadSha256 = digest,
            state = "QUEUED",
            createdAt = now
        )

        val domainEvent = DomainEventEntity(
            eventId = UUID.randomUUID().toString(),
            accountId = accountId,
            entityType = "OFFER",
            entityId = offerId,
            eventType = if (action == "ACCEPT_OFFER") "OFFER_ACCEPTED" else "OFFER_REJECTED",
            payloadJson = payload,
            prevHash = "0".repeat(64),
            currentHash = digest,
            createdAt = now
        )

        outboxDao?.enqueue(outboxOp)
        domainEventDao?.insertEvent(domainEvent)

        return outboxOp
    }
}
