package com.sahitol.collector

import com.sahitol.collector.domain.matching.MatchingEngine
import com.sahitol.collector.domain.matching.MatchingEngine.LotParameters
import com.sahitol.collector.domain.matching.MatchingEngine.MatchingCandidate
import org.junit.Assert.*
import org.junit.Test
import kotlin.math.abs

class MatchingEngineTest {

    @Test
    fun haversineDistance_delhiMayapuriToOkhla_matchesFixtureWithinTolerance() {
        // Fixture: Delhi Mayapuri (28.6358, 77.1256) to Okhla (28.5355, 77.2718) -> 18,115.3m
        val dist = MatchingEngine.haversineDistanceM(28.6358, 77.1256, 28.5355, 77.2718)
        val expected = 18115.3
        val tolerance = expected * 0.005 // 0.5%
        assertTrue("Distance $dist should be within 0.5% of $expected", abs(dist - expected) < tolerance)
    }

    @Test
    fun haversineDistance_mumbaiKurlaToThaneRabale_matchesFixture() {
        // Fixture: Kurla (19.0688, 72.8826) to Rabale (19.1415, 73.0035) -> 15,002.8m
        val dist = MatchingEngine.haversineDistanceM(19.0688, 72.8826, 19.1415, 73.0035)
        val expected = 15002.8
        val tolerance = expected * 0.005
        assertTrue("Distance $dist should be within 0.5% of $expected", abs(dist - expected) < tolerance)
    }

    @Test
    fun haversineDistance_identicalCoordinates_returnsZero() {
        val dist = MatchingEngine.haversineDistanceM(28.6358, 77.1256, 28.6358, 77.1256)
        assertEquals(0.0, dist, 0.001)
    }

    @Test
    fun evaluateCandidate_batteryIsolationInvariant_blocksGeneralFacilities() {
        val batteryLot = LotParameters(
            materialId = "MAT-BAT-01",
            estimatedWeightG = 12000,
            regulatoryRoute = "BATTERY_ISOLATION",
            latitude = 28.6358,
            longitude = 77.1256
        )

        val generalRecycler = MatchingCandidate(
            facilityId = "fac-gen-01",
            name = "Delhi General Scrap",
            kind = "RECYCLER",
            latitude = 28.6400,
            longitude = 77.1300,
            verificationLevel = "L3",
            authorizedRoutes = listOf("AUTHORIZED_EWASTE", "GENERAL_RECYCLING"),
            materialsAccepted = listOf("MAT-BAT-01", "MAT-CAB-01"),
            ratePaisePerKg = 8500,
            offersPickup = true
        )

        val authorizedBatteryRecycler = MatchingCandidate(
            facilityId = "fac-bat-01",
            name = "EcoSafe Battery Recyclers",
            kind = "RECYCLER",
            latitude = 28.6400,
            longitude = 77.1300,
            verificationLevel = "L4",
            authorizedRoutes = listOf("BATTERY_ISOLATION"),
            materialsAccepted = listOf("MAT-BAT-01"),
            ratePaisePerKg = 9000,
            offersPickup = true
        )

        val generalOutcome = MatchingEngine.evaluateCandidate(batteryLot, generalRecycler)
        assertFalse(generalOutcome.isEligible)
        assertTrue(generalOutcome.exclusionReasons.contains(MatchingEngine.EXCLUSION_ROUTE_INCOMPATIBLE))

        val batteryOutcome = MatchingEngine.evaluateCandidate(batteryLot, authorizedBatteryRecycler)
        assertTrue(batteryOutcome.isEligible)
        assertTrue(batteryOutcome.totalScore > 0.0)
    }

    @Test
    fun evaluateCandidate_materialNotAccepted_excludedWithCorrectReason() {
        val cableLot = LotParameters(
            materialId = "MAT-CAB-01",
            estimatedWeightG = 5000,
            regulatoryRoute = "AUTHORIZED_EWASTE",
            latitude = 28.6358,
            longitude = 77.1256
        )

        val pcbOnlyFacility = MatchingCandidate(
            facilityId = "fac-pcb-01",
            name = "Precision PCB Dismantlers",
            kind = "DISMANTLER",
            latitude = 28.6358,
            longitude = 77.1256,
            verificationLevel = "L3",
            authorizedRoutes = listOf("AUTHORIZED_EWASTE"),
            materialsAccepted = listOf("MAT-PCB-01", "MAT-PCB-02"),
            ratePaisePerKg = 40000,
            offersPickup = false
        )

        val outcome = MatchingEngine.evaluateCandidate(cableLot, pcbOnlyFacility)
        assertFalse(outcome.isEligible)
        assertTrue(outcome.exclusionReasons.contains(MatchingEngine.EXCLUSION_MATERIAL_UNACCEPTED))
    }

    @Test
    fun rankCandidates_deterministicTieBreaking_sortsScoreThenFacilityId() {
        val lot = LotParameters(
            materialId = "MAT-CAB-01",
            estimatedWeightG = 2500,
            regulatoryRoute = "AUTHORIZED_EWASTE",
            latitude = 28.6358,
            longitude = 77.1256
        )

        // Two identical facilities with same score but different IDs
        val facilityB = MatchingCandidate(
            facilityId = "fac-b",
            name = "Beta Scrap",
            kind = "RECYCLER",
            latitude = 28.6358,
            longitude = 77.1256,
            verificationLevel = "L3",
            authorizedRoutes = listOf("AUTHORIZED_EWASTE"),
            materialsAccepted = listOf("MAT-CAB-01"),
            ratePaisePerKg = 19000,
            offersPickup = true
        )

        val facilityA = MatchingCandidate(
            facilityId = "fac-a",
            name = "Alpha Scrap",
            kind = "RECYCLER",
            latitude = 28.6358,
            longitude = 77.1256,
            verificationLevel = "L3",
            authorizedRoutes = listOf("AUTHORIZED_EWASTE"),
            materialsAccepted = listOf("MAT-CAB-01"),
            ratePaisePerKg = 19000,
            offersPickup = true
        )

        val ranked = MatchingEngine.rankCandidates(lot, listOf(facilityB, facilityA))
        assertEquals(2, ranked.size)
        // With identical scores, facilityA must precede facilityB alphabetically by ID
        assertEquals("fac-a", ranked[0].facilityId)
        assertEquals("fac-b", ranked[1].facilityId)
    }

    @Test
    fun evaluateCandidate_outsideSearchRadius_excludedWithDistanceExceeded() {
        val lot = LotParameters(
            materialId = "MAT-CAB-01",
            estimatedWeightG = 2500,
            regulatoryRoute = "AUTHORIZED_EWASTE",
            latitude = 28.6358, // Delhi
            longitude = 77.1256
        )

        val distantFacility = MatchingCandidate(
            facilityId = "fac-mum-01",
            name = "Mumbai Coastal Recyclers",
            kind = "RECYCLER",
            latitude = 19.0760, // Mumbai (~1150 km away)
            longitude = 72.8777,
            verificationLevel = "L3",
            authorizedRoutes = listOf("AUTHORIZED_EWASTE"),
            materialsAccepted = listOf("MAT-CAB-01"),
            ratePaisePerKg = 21000,
            offersPickup = true
        )

        val outcome = MatchingEngine.evaluateCandidate(lot, distantFacility, searchRadiusM = 50_000.0)
        assertFalse(outcome.isEligible)
        assertTrue(outcome.exclusionReasons.contains(MatchingEngine.EXCLUSION_DISTANCE_EXCEEDED))
    }
}
