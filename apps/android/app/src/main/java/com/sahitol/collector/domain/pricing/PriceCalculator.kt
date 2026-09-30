package com.sahitol.collector.domain.pricing

import java.math.BigDecimal
import java.math.RoundingMode
import kotlin.math.pow

data class PriceObservation(
    val ratePaisePerUnit: Long,
    val weight: Double = 1.0,
    val observationId: String = ""
)

data class ConfidenceResult(
    val tier: String,
    val reasonCodes: List<String>,
    val isStale: Boolean
)

object PriceCalculator {

    const val POLICY_VERSION = "PRICE_V1"
    const val HALF_LIFE_DAYS = 7.0
    const val MAX_CACHE_HOURS = 24.0

    /**
     * Compute exponential decay weight: w_i = 2^(-age_days / half_life_days).
     */
    fun calculateRecencyWeight(ageDays: Double, halfLifeDays: Double = HALF_LIFE_DAYS): Double {
        val safeAge = if (ageDays < 0.0) 0.0 else ageDays
        return 2.0.pow(-safeAge / halfLifeDays)
    }

    /**
     * Calculate weighted quantiles (Q1, median, Q3) using first-cumulative method.
     * Sorts ascending by rate, then observationId.
     */
    fun calculateWeightedQuantiles(
        observations: List<PriceObservation>,
        quantiles: Triple<Double, Double, Double> = Triple(0.25, 0.50, 0.75)
    ): Triple<Long, Long, Long>? {
        val valid = observations.filter { it.weight > 0 }
        if (valid.isEmpty()) return null

        val sorted = valid.sortedWith(
            compareBy<PriceObservation> { it.ratePaisePerUnit }.thenBy { it.observationId }
        )

        val totalWeight = sorted.sumOf { it.weight }
        if (totalWeight <= 0) return null

        val qList = listOf(quantiles.first, quantiles.second, quantiles.third)
        val results = qList.map { q ->
            val threshold = q * totalWeight
            var cum = 0.0
            var chosen = sorted.last().ratePaisePerUnit
            for (obs in sorted) {
                cum += obs.weight
                if (cum >= threshold - 1e-9) {
                    chosen = obs.ratePaisePerUnit
                    break
                }
            }
            chosen
        }

        return Triple(results[0], results[1], results[2])
    }

    /**
     * Evaluate statistical confidence tier and audit reason codes under PRICE_V1.
     */
    fun evaluateConfidence(
        observationCount: Int,
        sourceCount: Int,
        latestAgeDays: Double,
        isExactRegion: Boolean = true,
        cachedHoursAgo: Double? = null
    ): ConfidenceResult {
        if (observationCount == 0) {
            return ConfidenceResult("INSUFFICIENT_DATA", listOf("NO_OBSERVATIONS_IN_WINDOW"), false)
        }

        val isStale = cachedHoursAgo != null && cachedHoursAgo > MAX_CACHE_HOURS
        val reasons = mutableListOf<String>()

        if (!isExactRegion) reasons.add("BROADER_REGION_COHORT")
        if (observationCount < 3) reasons.add("FEW_OBSERVATIONS")
        if (sourceCount < 2) reasons.add("SINGLE_SOURCE")
        if (latestAgeDays > 7.0) reasons.add("STALE_OBSERVATIONS")
        if (isStale) reasons.add("STALE_CACHED_SUMMARY")

        val isHighEligible = isExactRegion &&
            observationCount >= 10 &&
            sourceCount >= 3 &&
            latestAgeDays <= 3.0

        val isMediumEligible = observationCount >= 3 &&
            sourceCount >= 2 &&
            latestAgeDays <= 7.0

        val confidence = when {
            isStale || !isExactRegion -> "LOW"
            isHighEligible -> "HIGH"
            isMediumEligible -> "MEDIUM"
            else -> "LOW"
        }

        return ConfidenceResult(confidence, reasons, isStale)
    }

    /**
     * Compute total paise: round_half_up(rate_paise_per_kg * weight_g / 1000)
     */
    fun calculateLotValuation(ratePaisePerKg: Long, weightGrams: Long): Long {
        val numerator = BigDecimal.valueOf(ratePaisePerKg).multiply(BigDecimal.valueOf(weightGrams))
        return numerator.divide(BigDecimal.valueOf(1000), 0, RoundingMode.HALF_UP).toLong()
    }

    /**
     * Calculate valuation range (low, median, high) in paise.
     */
    fun calculateLotValuationRange(
        q1Paise: Long,
        medianPaise: Long,
        q3Paise: Long,
        weightGrams: Long
    ): Triple<Long, Long, Long> {
        return Triple(
            calculateLotValuation(q1Paise, weightGrams),
            calculateLotValuation(medianPaise, weightGrams),
            calculateLotValuation(q3Paise, weightGrams)
        )
    }
}
