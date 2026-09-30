package com.sahitol.collector

import com.sahitol.collector.domain.pricing.PriceCalculator
import com.sahitol.collector.domain.pricing.PriceObservation
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class PriceCalculatorTest {

    @Test
    fun testPriceV1QuantilesFixture() {
        // Techspec line 65: rates [10000, 20000, 30000, 40000] paise/kg with equal weights
        val rates = listOf(10000L, 20000L, 30000L, 40000L)
        val obs = rates.mapIndexed { idx, rate ->
            PriceObservation(ratePaisePerUnit = rate, weight = 1.0, observationId = "obs_$idx")
        }

        val quantiles = PriceCalculator.calculateWeightedQuantiles(obs)
        assertNotNull(quantiles)
        val (q1, median, q3) = quantiles!!
        assertEquals(10000L, q1)
        assertEquals(20000L, median)
        assertEquals(30000L, q3)
    }

    @Test
    fun testPriceV1RecencyDecayWeights() {
        // Rates [40000, 30000, 20000, 10000] with weights [1.0, 0.5, 0.25, 0.125]
        val obs = listOf(
            PriceObservation(ratePaisePerUnit = 40000L, weight = 1.0, observationId = "obs_fresh"),
            PriceObservation(ratePaisePerUnit = 30000L, weight = 0.5, observationId = "obs_7d"),
            PriceObservation(ratePaisePerUnit = 20000L, weight = 0.25, observationId = "obs_14d"),
            PriceObservation(ratePaisePerUnit = 10000L, weight = 0.125, observationId = "obs_21d")
        )

        val quantiles = PriceCalculator.calculateWeightedQuantiles(obs)
        assertNotNull(quantiles)
        val (q1, median, q3) = quantiles!!
        assertEquals(30000L, q1)
        assertEquals(40000L, median)
        assertEquals(40000L, q3)
    }

    @Test
    fun testPriceV1SingleObservation() {
        val obs = listOf(PriceObservation(ratePaisePerUnit = 25000L, weight = 1.0, observationId = "obs_single"))
        val quantiles = PriceCalculator.calculateWeightedQuantiles(obs)
        assertNotNull(quantiles)
        val (q1, median, q3) = quantiles!!
        assertEquals(25000L, q1)
        assertEquals(25000L, median)
        assertEquals(25000L, q3)
    }

    @Test
    fun testPriceV1EmptyObservations() {
        assertNull(PriceCalculator.calculateWeightedQuantiles(emptyList()))
    }

    @Test
    fun testPriceV1ValuationFixture() {
        // Techspec line 65: 2500g lot at Q1=10000, med=20000, Q3=30000 -> [25000, 50000, 75000] paise
        val (low, med, high) = PriceCalculator.calculateLotValuationRange(10000L, 20000L, 30000L, 2500L)
        assertEquals(25000L, low)
        assertEquals(50000L, med)
        assertEquals(75000L, high)
    }

    @Test
    fun testPriceV1RoundingHalfUp() {
        // 1500 paise/kg * 1g = 1.5 paise -> rounds up to 2 paise
        assertEquals(2L, PriceCalculator.calculateLotValuation(1500L, 1L))
        // 1499 paise/kg * 1g = 1.499 paise -> rounds down to 1 paise
        assertEquals(1L, PriceCalculator.calculateLotValuation(1499L, 1L))
        // 1000 paise/kg * 333g = 333.0 paise -> 333 paise
        assertEquals(333L, PriceCalculator.calculateLotValuation(1000L, 333L))
    }

    @Test
    fun testPriceV1RecencyWeightDecay() {
        assertEquals(1.0, PriceCalculator.calculateRecencyWeight(0.0), 1e-6)
        assertEquals(0.5, PriceCalculator.calculateRecencyWeight(7.0), 1e-6)
        assertEquals(0.25, PriceCalculator.calculateRecencyWeight(14.0), 1e-6)
    }

    @Test
    fun testPriceV1ConfidenceEvaluations() {
        // 1. No data
        val noData = PriceCalculator.evaluateConfidence(0, 0, 0.0, true)
        assertEquals("INSUFFICIENT_DATA", noData.tier)
        assertTrue(noData.reasonCodes.contains("NO_OBSERVATIONS_IN_WINDOW"))

        // 2. Single source
        val singleSrc = PriceCalculator.evaluateConfidence(4, 1, 1.0, true)
        assertEquals("LOW", singleSrc.tier)
        assertTrue(singleSrc.reasonCodes.contains("SINGLE_SOURCE"))

        // 3. Few observations
        val fewObs = PriceCalculator.evaluateConfidence(2, 2, 1.0, true)
        assertEquals("LOW", fewObs.tier)
        assertTrue(fewObs.reasonCodes.contains("FEW_OBSERVATIONS"))

        // 4. Medium confidence
        val med = PriceCalculator.evaluateConfidence(3, 2, 4.0, true)
        assertEquals("MEDIUM", med.tier)

        // 5. High confidence
        val high = PriceCalculator.evaluateConfidence(10, 3, 2.0, true)
        assertEquals("HIGH", high.tier)

        // 6. Stale observations
        val stale = PriceCalculator.evaluateConfidence(10, 3, 12.0, true)
        assertEquals("LOW", stale.tier)
        assertTrue(stale.reasonCodes.contains("STALE_OBSERVATIONS"))

        // 7. Broader region capped at LOW
        val broader = PriceCalculator.evaluateConfidence(10, 3, 2.0, false)
        assertEquals("LOW", broader.tier)
        assertTrue(broader.reasonCodes.contains("BROADER_REGION_COHORT"))

        // 8. Cached summary >24h stale capped at LOW
        val cachedStale = PriceCalculator.evaluateConfidence(10, 3, 2.0, true, 26.0)
        assertEquals("LOW", cachedStale.tier)
        assertTrue(cachedStale.isStale)
        assertTrue(cachedStale.reasonCodes.contains("STALE_CACHED_SUMMARY"))
    }
}
