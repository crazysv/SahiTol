package com.sahitol.collector.data.repository

import com.sahitol.collector.BuildConfig
import android.util.Log
import com.sahitol.collector.data.local.SahiTolDatabase
import com.sahitol.collector.data.local.dao.DomainEventDao
import com.sahitol.collector.data.local.dao.OutboxDao
import com.sahitol.collector.data.local.entity.DomainEventEntity
import com.sahitol.collector.data.local.entity.OutboxOperationEntity
import com.sahitol.collector.domain.matching.MatchingEngine
import com.sahitol.collector.domain.matching.MatchingEngine.LotParameters
import com.sahitol.collector.domain.matching.MatchingEngine.MatchingCandidate
import com.sahitol.collector.domain.matching.MatchingEngine.MatchOutcome
import com.sahitol.collector.domain.canonical.CanonicalJson
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest
import java.time.Instant
import java.util.UUID
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

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
    val status: String = "ACTIVE", // ACTIVE, ACCEPTED, REJECTED, EXPIRED
    val termsHash: String? = null,
    val version: Int? = null
)

/** Server-authoritative agreement recovered from a persisted lot ID. */
data class AcceptedTransaction(
    val transactionId: String,
    val lotId: String,
    val collectorId: String,
    val facilityId: String,
    val acceptedOfferId: String,
    val agreedWeightG: Long,
    val agreedTotalPaise: Long,
    val currency: String,
    val lifecycle: String,
    val isDemo: Boolean
)

data class LiveHandoverStatus(
    val handoverId: String,
    val status: String,
    val proposalHash: String,
    val version: Int,
    val confirmedAt: String?
)

data class LiveHandoverResult(
    val handoverId: String,
    val transactionId: String,
    val status: String,
    val proposalHash: String,
    val publicToken: String?,
    val version: Int
)

internal fun offerTotalInr(
    priceBasis: String,
    ratePaisePerKg: Int,
    fixedTotalPaise: Int,
    weightBasisG: Long
): Double = when (priceBasis) {
    "RATE_PER_KG" -> ratePaisePerKg.toDouble() * weightBasisG / 100_000.0
    "FIXED_TOTAL" -> fixedTotalPaise / 100.0
    else -> 0.0
}

sealed interface TradeResult<out T> {
    data class Success<T>(val value: T) : TradeResult<T>
    data class Failure(val message: String) : TradeResult<Nothing>
}

class FacilityRepository(
    private val database: SahiTolDatabase? = null,
    private val outboxDao: OutboxDao? = database?.outboxDao(),
    private val domainEventDao: DomainEventDao? = database?.domainEventDao()
) {

    // Reference-only cache for offline browsing. These identifiers are intentionally
    // never used to create or accept a trade: actionable trade calls use server UUIDs.
    private val cachedReferenceFacilities = listOf(
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
            return cachedReferenceFacilities
        }
        return cachedReferenceFacilities.filter {
            it.address.contains(areaFilter, ignoreCase = true) ||
            it.nameEn.contains(areaFilter, ignoreCase = true)
        }
    }

    fun getFacilityDetails(facilityId: String): RecyclerFacilityItem? {
        return cachedReferenceFacilities.firstOrNull { it.facilityId == facilityId }
    }

    suspend fun fetchLiveFacilities(): TradeResult<List<RecyclerFacilityItem>> {
        val response = requestJson("GET", "/api/v1/facilities?is_demo=true") ?: return TradeResult.Failure("Could not reach the facility directory. Cached reference entries cannot receive a trade request.")
        if (response.first !in 200..299) return TradeResult.Failure(apiMessage(response.second))
        return try {
            val facilities = org.json.JSONArray(response.second)
            TradeResult.Success((0 until facilities.length()).map { index ->
                val item = facilities.getJSONObject(index)
                RecyclerFacilityItem(
                    facilityId = item.getString("id"), nameEn = item.getString("name"), nameLocal = item.getString("name"),
                    address = item.getString("address_public"), distanceKm = 0.0, travelTimeMinutes = 0,
                    materialsAccepted = item.getJSONArray("materials_accepted").toStringList(), instantUpi = false,
                    operatingHours = "Check with facility", rateInrPerKg = 0.0,
                    verificationLevel = item.getString("verification_level"), routeCode = item.getJSONArray("authorized_routes").optString(0),
                    offersPickup = item.optBoolean("pickup_available", false), latitude = null, longitude = null
                )
            })
        } catch (_: Exception) { TradeResult.Failure("The facility directory returned an unreadable response.") }
    }

    suspend fun requestRecycler(lotId: String, facilityId: String, accountId: String): TradeResult<Unit> {
        if (!isUuid(lotId) || !isUuid(facilityId)) return TradeResult.Failure("Sync this saved lot and choose a live directory facility before sending a request.")
        val token = collectorDemoToken(accountId) ?: return TradeResult.Failure("Sign in again before sending a request.")
        val body = JSONObject().put("facility_id", facilityId).put("notes", "Collector request from Android").toString()
        val response = requestJson("POST", "/api/v1/lots/$lotId/requests", body, token) ?: return TradeResult.Failure("Could not send the request. Check the connection and try again.")
        return if (response.first in 200..299) TradeResult.Success(Unit) else TradeResult.Failure(apiMessage(response.second))
    }

    suspend fun fetchLiveOffers(lotId: String, accountId: String): TradeResult<List<RecyclerOfferItem>> {
        if (!isUuid(lotId)) return TradeResult.Failure("This saved lot has not been synchronized yet.")
        val token = collectorDemoToken(accountId) ?: return TradeResult.Failure("Sign in again to check offers.")
        val response = requestJson("GET", "/api/v1/lots/$lotId/offers", accessToken = token) ?: return TradeResult.Failure("Could not refresh offers. Check the connection and try again.")
        Log.i("SahiTolTrade", "Live offer refresh for $lotId returned HTTP ${response.first}")
        if (response.first !in 200..299) return TradeResult.Failure(apiMessage(response.second))
        return try {
            val offers = org.json.JSONArray(response.second)
            Log.i("SahiTolTrade", "Live offer refresh parsed ${offers.length()} offers for $lotId")
            TradeResult.Success((0 until offers.length()).map { index ->
                val item = offers.getJSONObject(index)
                val ratePaise = item.optInt("effective_rate_paise_per_kg", 0)
                val totalPaise = item.optInt("fixed_total_paise", 0)
                val weightBasisG = item.optLong("weight_basis_g", 0L)
                val priceBasis = item.getString("price_basis")
                RecyclerOfferItem(item.getString("id"), item.getString("facility_id"), "Recycler offer", "Live offer", 0.0,
                    ratePaise / 100.0,
                    offerTotalInr(priceBasis, ratePaise, totalPaise, weightBasisG),
                    priceBasis, status = item.getString("status"),
                    termsHash = item.getString("terms_hash"), version = item.getInt("version"))
            })
        } catch (_: Exception) { TradeResult.Failure("The offer list returned an unreadable response.") }
    }

    suspend fun acceptLiveOffer(offer: RecyclerOfferItem, accountId: String): TradeResult<Unit> {
        if (!isUuid(offer.offerId) || offer.termsHash.isNullOrBlank() || offer.version == null) return TradeResult.Failure("This offer is incomplete. Refresh it before accepting.")
        val token = collectorDemoToken(accountId) ?: return TradeResult.Failure("Sign in again before accepting the offer.")
        val body = JSONObject().put("terms_hash", offer.termsHash).put("expected_version", offer.version).toString()
        val response = requestJson("POST", "/api/v1/offers/${offer.offerId}/accept", body, token) ?: return TradeResult.Failure("Could not accept the offer. Check the connection and try again.")
        return if (response.first in 200..299) TradeResult.Success(Unit) else TradeResult.Failure(apiMessage(response.second))
    }

    suspend fun fetchAcceptedTransaction(lotId: String, accountId: String): TradeResult<AcceptedTransaction> {
        if (!isUuid(lotId)) return TradeResult.Failure("This saved lot has not been synchronized yet.")
        val token = collectorDemoToken(accountId) ?: return TradeResult.Failure("Sign in again to resume the accepted offer.")
        val response = requestJson("GET", "/api/v1/lots/$lotId/transaction", accessToken = token)
            ?: return TradeResult.Failure("Could not retrieve the accepted agreement. Check the connection and try again.")
        if (response.first !in 200..299) return TradeResult.Failure(apiMessage(response.second))
        return try {
            val item = JSONObject(response.second)
            TradeResult.Success(
                AcceptedTransaction(
                    transactionId = item.getString("id"),
                    lotId = item.getString("lot_id"),
                    collectorId = item.getString("collector_id"),
                    facilityId = item.getString("facility_id"),
                    acceptedOfferId = item.getString("accepted_offer_id"),
                    agreedWeightG = item.getLong("agreed_weight_g"),
                    agreedTotalPaise = item.getLong("agreed_total_paise"),
                    currency = item.getString("currency"),
                    lifecycle = item.getString("lifecycle"),
                    isDemo = item.getBoolean("is_demo")
                )
            )
        } catch (_: Exception) { TradeResult.Failure("The accepted agreement returned an unreadable response.") }
    }

    suspend fun createLiveHandover(
        agreement: AcceptedTransaction,
        offer: RecyclerOfferItem,
        materialId: String,
        accountId: String,
        measuredWeightG: Long = agreement.agreedWeightG
    ): TradeResult<LiveHandoverResult> {
        if (agreement.lifecycle !in setOf("AGREED", "IN_TRANSIT")) {
            return TradeResult.Failure("This agreement is not eligible for a handover proposal.")
        }
        val token = collectorDemoToken(accountId) ?: return TradeResult.Failure("Sign in again before creating the handover.")
        val handoverId = UUID.randomUUID().toString()
        val now = Instant.now().toString()
        val payload = mapOf(
            "schema_version" to "SAHITOL-HANDOVER-1",
            "handover_id" to handoverId,
            "transaction_id" to agreement.transactionId,
            "lot_id" to agreement.lotId,
            "collector_id" to agreement.collectorId,
            "facility_id" to agreement.facilityId,
            "agreed_terms_hash" to offer.termsHash,
            "material_snapshot" to mapOf(
                "material_id" to materialId,
                "condition" to "INTACT",
                "regulatory_route" to if (materialId.contains("BAT")) "HAZARDOUS_BATTERY" else "AUTHORIZED_EWASTE"
            ),
            "weight_snapshot" to mapOf(
                "estimated_weight_g" to agreement.agreedWeightG,
                "measured_weight_g" to measuredWeightG
            ),
            "value_snapshot" to mapOf(
                "currency" to agreement.currency,
                "agreed_total_paise" to agreement.agreedTotalPaise
            ),
            "occurred_at" to now,
            "media" to emptyList<String>(),
            "is_demo" to agreement.isDemo
        )
        val canonicalPayload = CanonicalJson.serialize(payload)
        val proposalHash = CanonicalJson.sha256Hex(canonicalPayload)
        val body = JSONObject()
            .put("id", handoverId)
            .put("proposal_payload", JSONObject(canonicalPayload))
            .put("proposal_hash", proposalHash)
            .toString()
        val response = requestJson("POST", "/api/v1/handovers", body, token)
            ?: return TradeResult.Failure("Could not create the handover proposal. Check the connection and try again.")
        if (response.first !in 200..299) return TradeResult.Failure(apiMessage(response.second))
        return try {
            val item = JSONObject(response.second)
            TradeResult.Success(LiveHandoverResult(
                handoverId = item.getString("id"), transactionId = item.getString("transaction_id"),
                status = item.getString("status"), proposalHash = item.getString("proposal_hash"),
                publicToken = item.optString("public_token").ifBlank { null }, version = item.getInt("version")
            ))
        } catch (_: Exception) { TradeResult.Failure("The handover response returned an unreadable response.") }
    }

    /** Pull the authoritative handover state after the recycler acts on the second device. */
    suspend fun fetchLiveHandoverStatus(handoverId: String, accountId: String): TradeResult<LiveHandoverStatus> {
        if (!isUuid(handoverId)) return TradeResult.Failure("This handover has not been issued by the server.")
        val token = collectorDemoToken(accountId) ?: return TradeResult.Failure("Sign in again to refresh the handover status.")
        val response = requestJson("GET", "/api/v1/handovers/$handoverId", accessToken = token)
            ?: return TradeResult.Failure("Could not refresh the handover status. Check the connection and retry.")
        if (response.first !in 200..299) return TradeResult.Failure(apiMessage(response.second))
        return parseLiveHandoverStatus(response.second)
    }

    /** Recover the most recent handover from the durable lot ID after process restart. */
    suspend fun fetchLiveHandoverForLot(lotId: String, accountId: String): TradeResult<LiveHandoverStatus> {
        if (!isUuid(lotId)) return TradeResult.Failure("This saved lot has not been synchronized yet.")
        val token = collectorDemoToken(accountId) ?: return TradeResult.Failure("Sign in again to resume the handover.")
        val response = requestJson("GET", "/api/v1/lots/$lotId/handover", accessToken = token)
            ?: return TradeResult.Failure("Could not retrieve the handover record. Check the connection and retry.")
        if (response.first !in 200..299) return TradeResult.Failure(apiMessage(response.second))
        return parseLiveHandoverStatus(response.second)
    }

    private fun parseLiveHandoverStatus(body: String): TradeResult<LiveHandoverStatus> = try {
        val item = JSONObject(body)
        val confirmation = item.optJSONObject("confirmation")
        TradeResult.Success(
            LiveHandoverStatus(
                handoverId = item.getString("id"),
                status = item.getString("status"),
                proposalHash = item.getString("proposal_hash"),
                version = item.getInt("version"),
                confirmedAt = confirmation?.optString("confirmed_at")?.ifBlank { null }
            )
        )
    } catch (_: Exception) { TradeResult.Failure("The handover status returned an unreadable response.") }

    private suspend fun collectorDemoToken(accountId: String): String? {
        if (!accountId.startsWith("col_demo_")) {
            Log.w("SahiTolTrade", "Live trade rejected for a non-demo local account")
            return null
        }
        val response = requestJson("POST", "/api/v1/auth/demo", JSONObject().put("role", "COLLECTOR").put("persona_id", "santosh").put("device_id", "android-device").toString()) ?: return null
        return if (response.first in 200..299) runCatching { JSONObject(response.second).getString("access_token") }.getOrNull() else null
    }

    private suspend fun requestJson(method: String, path: String, body: String? = null, accessToken: String? = null): Pair<Int, String>? = withContext(Dispatchers.IO) { try {
        val connection = (URL(BuildConfig.API_BASE_URL.trimEnd('/') + path).openConnection() as HttpURLConnection).apply {
            requestMethod = method; connectTimeout = 15_000; readTimeout = 15_000; setRequestProperty("Accept", "application/json")
            if (accessToken != null) setRequestProperty("Authorization", "Bearer $accessToken")
            if (body != null) { doOutput = true; setRequestProperty("Content-Type", "application/json"); outputStream.bufferedWriter().use { it.write(body) } }
        }
        val code = connection.responseCode
        val text = (if (code in 200..299) connection.inputStream else connection.errorStream)?.bufferedReader()?.use { it.readText() }.orEmpty()
        connection.disconnect(); code to text
    } catch (error: Exception) {
        Log.w("SahiTolTrade", "Live trade request failed for $method $path", error)
        null
    } }

    private fun apiMessage(body: String): String = runCatching { JSONObject(body).optString("detail").ifBlank { "The server rejected this request." } }.getOrDefault("The server rejected this request.")
    private fun isUuid(value: String): Boolean = runCatching { UUID.fromString(value) }.isSuccess
    private fun org.json.JSONArray.toStringList(): List<String> = (0 until length()).map { getString(it) }
}
