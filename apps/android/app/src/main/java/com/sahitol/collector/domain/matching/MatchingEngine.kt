package com.sahitol.collector.domain.matching

import java.math.BigDecimal
import java.math.RoundingMode
import java.time.Instant
import kotlin.math.*

object MatchingEngine {

    const val MATCH_POLICY_VERSION = "MATCH_V1"
    const val DEFAULT_SEARCH_RADIUS_METRES = 50_000.0 // 50 km

    // Weightings per MATCH_V1
    const val WEIGHT_DISTANCE = 0.30
    const val WEIGHT_RATE = 0.30
    const val WEIGHT_PICKUP = 0.20
    const val WEIGHT_AVAILABILITY = 0.15
    const val WEIGHT_RELIABILITY = 0.05

    // Exclusion Reason Codes
    const val EXCLUSION_ROUTE_INCOMPATIBLE = "ROUTE_INCOMPATIBLE"
    const val EXCLUSION_MATERIAL_UNACCEPTED = "MATERIAL_UNACCEPTED"
    const val EXCLUSION_EXPIRED_REGISTRATION = "EXPIRED_REGISTRATION"
    const val EXCLUSION_VERIFICATION_INSUFFICIENT = "VERIFICATION_INSUFFICIENT"
    const val EXCLUSION_WEIGHT_INCOMPATIBLE = "WEIGHT_INCOMPATIBLE"
    const val EXCLUSION_SERVICE_AREA_UNSUPPORTED = "SERVICE_AREA_UNSUPPORTED"
    const val EXCLUSION_OPERATIONALLY_CLOSED = "OPERATIONALLY_CLOSED"
    const val EXCLUSION_DISTANCE_EXCEEDED = "DISTANCE_EXCEEDED"
    const val EXCLUSION_DEMO_MISMATCH = "DEMO_MISMATCH"

    const val STATUTORY_DISCLAIMER =
        "Public directory lead sourced from official state/central regulator registries. " +
        "Listing does not represent an endorsement, commercial partnership, or EPR fulfillment certificate."

    /**
     * Great circle distance in metres using Haversine formula (Earth radius R = 6,371,000 m).
     * Parity with PostGIS within 0.5% tolerance.
     */
    fun haversineDistanceM(lat1: Double, lon1: Double, lat2: Double, lon2: Double): Double {
        val r = 6371000.0
        val phi1 = Math.toRadians(lat1)
        val phi2 = Math.toRadians(lat2)
        val deltaPhi = Math.toRadians(lat2 - lat1)
        val deltaLambda = Math.toRadians(lon2 - lon1)

        val a = sin(deltaPhi / 2.0).pow(2) +
                cos(phi1) * cos(phi2) * sin(deltaLambda / 2.0).pow(2)
        val c = 2.0 * atan2(sqrt(a), sqrt(1.0 - a))
        return r * c
    }

    data class MatchingCandidate(
        val facilityId: String,
        val name: String,
        val kind: String, // RECYCLER, DISMANTLER, COLLECTION_CENTRE
        val latitude: Double?,
        val longitude: Double?,
        val verificationLevel: String, // L0, L1, L2, L3, L4
        val authorizedRoutes: List<String>,
        val materialsAccepted: List<String>,
        val ratePaisePerKg: Long?,
        val offersPickup: Boolean,
        val isOperational: Boolean = true,
        val registrationExpiry: Instant? = null,
        val maxWeightG: Long? = null,
        val minWeightG: Long? = null,
        val historicalReliabilityScore: Double? = null, // 0.0 to 1.0
        val isDemo: Boolean = false
    )

    data class LotParameters(
        val materialId: String,
        val estimatedWeightG: Long,
        val regulatoryRoute: String, // e.g. "BATTERY_ISOLATION", "AUTHORIZED_EWASTE"
        val latitude: Double?,
        val longitude: Double?,
        val requiresPickup: Boolean = false,
        val isDemo: Boolean = false
    )

    data class FactorScores(
        val distanceScore: Double,
        val rateScore: Double,
        val pickupScore: Double,
        val availabilityScore: Double,
        val reliabilityScore: Double
    )

    data class MatchOutcome(
        val facilityId: String,
        val facilityName: String,
        val isEligible: Boolean,
        val totalScore: Double, // 0.0 to 100.0
        val factorScores: FactorScores?,
        val distanceMetres: Double?,
        val offeredRatePaisePerKg: Long?,
        val exclusionReasons: List<String>
    )

    /**
     * Evaluate a candidate against lot parameters under MATCH_V1.
     */
    fun evaluateCandidate(
        lot: LotParameters,
        candidate: MatchingCandidate,
        maxRateInPool: Long? = null,
        searchRadiusM: Double = DEFAULT_SEARCH_RADIUS_METRES
    ): MatchOutcome {
        val exclusions = mutableListOf<String>()

        // 1. Partition Check
        if (lot.isDemo != candidate.isDemo) {
            exclusions.add(EXCLUSION_DEMO_MISMATCH)
        }

        // 2. Route Check (Hard Invariant: Battery Isolation cannot match general e-waste)
        if (lot.regulatoryRoute == "BATTERY_ISOLATION") {
            if (!candidate.authorizedRoutes.contains("BATTERY_ISOLATION")) {
                exclusions.add(EXCLUSION_ROUTE_INCOMPATIBLE)
            }
        } else {
            // General lot cannot match facilities restricted ONLY to BATTERY_ISOLATION
            val isBatteryOnly = candidate.authorizedRoutes.size == 1 &&
                    candidate.authorizedRoutes.contains("BATTERY_ISOLATION")
            if (isBatteryOnly) {
                exclusions.add(EXCLUSION_ROUTE_INCOMPATIBLE)
            }
        }

        // 3. Material Acceptance Check
        if (!candidate.materialsAccepted.contains(lot.materialId)) {
            exclusions.add(EXCLUSION_MATERIAL_UNACCEPTED)
        }

        // 4. Registration Expiry
        if (candidate.registrationExpiry != null && candidate.registrationExpiry.isBefore(Instant.now())) {
            exclusions.add(EXCLUSION_EXPIRED_REGISTRATION)
        }

        // 5. Weight Capacity Check
        if (candidate.maxWeightG != null && lot.estimatedWeightG > candidate.maxWeightG) {
            exclusions.add(EXCLUSION_WEIGHT_INCOMPATIBLE)
        }
        if (candidate.minWeightG != null && lot.estimatedWeightG < candidate.minWeightG) {
            exclusions.add(EXCLUSION_WEIGHT_INCOMPATIBLE)
        }

        // 6. Operational Status
        if (!candidate.isOperational) {
            exclusions.add(EXCLUSION_OPERATIONALLY_CLOSED)
        }

        // 7. Distance Calculation & Boundary Check
        var distanceM: Double? = null
        if (lot.latitude != null && lot.longitude != null &&
            candidate.latitude != null && candidate.longitude != null
        ) {
            val dist = haversineDistanceM(
                lot.latitude, lot.longitude,
                candidate.latitude, candidate.longitude
            )
            distanceM = dist
            if (dist > searchRadiusM) {
                exclusions.add(EXCLUSION_DISTANCE_EXCEEDED)
            }
        }

        if (exclusions.isNotEmpty()) {
            return MatchOutcome(
                facilityId = candidate.facilityId,
                facilityName = candidate.name,
                isEligible = false,
                totalScore = 0.0,
                factorScores = null,
                distanceMetres = distanceM,
                offeredRatePaisePerKg = candidate.ratePaisePerKg,
                exclusionReasons = exclusions
            )
        }

        // --- 5-Factor Scoring (0.0 to 1.0 for each factor) ---
        // Factor 1: Distance (30%) - Inverse linear within search radius
        val distScore = if (distanceM != null) {
            max(0.0, 1.0 - (distanceM / searchRadiusM))
        } else {
            0.5 // Unknown location neutral score
        }

        // Factor 2: Rate (30%) - Relative to max rate in pool
        val rateScore = if (candidate.ratePaisePerKg != null && maxRateInPool != null && maxRateInPool > 0) {
            min(1.0, candidate.ratePaisePerKg.toDouble() / maxRateInPool.toDouble())
        } else if (candidate.ratePaisePerKg != null) {
            0.7
        } else {
            0.0 // No rate published
        }

        // Factor 3: Pickup Capability (20%)
        val pickupScore = if (lot.requiresPickup) {
            if (candidate.offersPickup) 1.0 else 0.0
        } else {
            if (candidate.offersPickup) 1.0 else 0.8 // Bonus for versatile facility
        }

        // Factor 4: Availability / Operating Readiness (15%)
        val availabilityScore = if (candidate.isOperational) 1.0 else 0.0

        // Factor 5: Verification & Historical Reliability (5%)
        val reliabilityScore = candidate.historicalReliabilityScore ?: when (candidate.verificationLevel) {
            "L4" -> 1.0
            "L3" -> 0.9
            "L2" -> 0.75
            "L1" -> 0.5
            else -> 0.3
        }

        val totalScore = (
            (distScore * WEIGHT_DISTANCE) +
            (rateScore * WEIGHT_RATE) +
            (pickupScore * WEIGHT_PICKUP) +
            (availabilityScore * WEIGHT_AVAILABILITY) +
            (reliabilityScore * WEIGHT_RELIABILITY)
        ) * 100.0

        val roundedTotal = BigDecimal(totalScore).setScale(2, RoundingMode.HALF_UP).toDouble()

        return MatchOutcome(
            facilityId = candidate.facilityId,
            facilityName = candidate.name,
            isEligible = true,
            totalScore = roundedTotal,
            factorScores = FactorScores(
                distanceScore = distScore,
                rateScore = rateScore,
                pickupScore = pickupScore,
                availabilityScore = availabilityScore,
                reliabilityScore = reliabilityScore
            ),
            distanceMetres = distanceM,
            offeredRatePaisePerKg = candidate.ratePaisePerKg,
            exclusionReasons = emptyList()
        )
    }

    /**
     * Rank a list of candidates against lot parameters, with deterministic tie-breaking.
     * Sorted descending by totalScore, then ascending by facilityId string.
     */
    fun rankCandidates(
        lot: LotParameters,
        candidates: List<MatchingCandidate>,
        searchRadiusM: Double = DEFAULT_SEARCH_RADIUS_METRES
    ): List<MatchOutcome> {
        val maxRate = candidates.mapNotNull { it.ratePaisePerKg }.maxOrNull()
        val outcomes = candidates.map { evaluateCandidate(lot, it, maxRate, searchRadiusM) }

        return outcomes.sortedWith(
            compareByDescending<MatchOutcome> { it.isEligible }
                .thenByDescending { it.totalScore }
                .thenBy { it.facilityId }
        )
    }
}
