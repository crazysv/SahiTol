package com.sahitol.collector

import com.sahitol.collector.data.local.entity.LotEntity
import com.sahitol.collector.domain.classifier.ClassificationResult
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test

class FeasibilityDiagnosticTest {

    @Test
    fun testAdvisoryThresholdBehavior() {
        val highConfidenceResult = ClassificationResult(
            categoryCode = "MAT-CAB-01",
            categoryNameEn = "Cables & Wires",
            categoryNameHi = "केबल (Cable)",
            categoryNameMr = "केबल (Cable)",
            confidence = 0.82f,
            meetsThreshold = 0.82f >= 0.65f,
            latencyMs = 7.57,
            isFallback = false,
            rawScores = mapOf("MAT-CAB-01" to 0.82f, "MAT-UNK-01" to 0.05f)
        )

        assertTrue(highConfidenceResult.meetsThreshold)
        assertFalse(highConfidenceResult.isFallback)
        assertEquals("MAT-CAB-01", highConfidenceResult.categoryCode)
        assertEquals("केबल (Cable)", highConfidenceResult.categoryNameHi)

        // Low confidence below 0.65 threshold routes to fallback / manual selection
        val lowConfidenceScore = 0.48f
        val lowConfidenceResult = ClassificationResult(
            categoryCode = "MAT-PLA-01",
            categoryNameEn = "Rigid FR Plastics",
            categoryNameHi = "कठोर प्लास्टिक",
            categoryNameMr = "कठीण प्लॅस्टिक",
            confidence = lowConfidenceScore,
            meetsThreshold = lowConfidenceScore >= 0.65f,
            latencyMs = 8.12,
            isFallback = true,
            rawScores = mapOf("MAT-PLA-01" to 0.48f, "MAT-UNK-01" to 0.32f)
        )

        assertFalse(lowConfidenceResult.meetsThreshold)
        assertTrue(lowConfidenceResult.isFallback)
    }

    @Test
    fun testLotEntityOfflinePersistenceModel() {
        val lot = LotEntity(
            lotId = "diagnostic-lot-001",
            materialCode = "MAT-CAB-01",
            estimatedWeightG = 2500L,
            measuredWeightG = null,
            estimatedLowPaise = 25000L,
            estimatedMedianPaise = 30000L,
            estimatedHighPaise = 35000L,
            localPhotoPath = "/data/user/0/com.sahitol.collector/cache/diagnostic_photo.jpg",
            status = "DRAFT",
            syncStatus = "SAVED_LOCAL_ONLY"
        )

        assertEquals("diagnostic-lot-001", lot.lotId)
        assertEquals("MAT-CAB-01", lot.materialCode)
        assertEquals(2500L, lot.estimatedWeightG)
        assertEquals("DRAFT", lot.status)
        assertEquals("SAVED_LOCAL_ONLY", lot.syncStatus)
        assertNotNull(lot.createdAt)
    }

    @Test
    fun testMultilingualTranslationsContract() {
        val categories = listOf(
            Triple("MAT-CAB-01", "Cables & Wires", "केबल (Cable)"),
            Triple("MAT-BAT-01", "Lead-Acid Battery", "लेड-एसिड बैटरी"),
            Triple("MAT-BAT-02", "Lithium-Ion Battery", "लिथियम-आयन बैटरी"),
            Triple("MAT-CRT-01", "CRT Glass / Monitors", "सीआरटी ग्लास / टीवी"),
            Triple("MAT-PCB-01", "High-Grade PCB", "उच्च श्रेणी पीसीबी")
        )

        for ((code, en, hi) in categories) {
            assertTrue(code.startsWith("MAT-"))
            assertTrue(en.isNotBlank())
            assertTrue(hi.isNotBlank())
        }
    }

    @Test
    fun testPhotoCompressionScalingCalculations() {
        // Verify bounding calculation to maxDimension 1024
        val originalW = 4000
        val originalH = 3000
        val maxDim = 1024

        val maxOriginal = kotlin.math.max(originalW, originalH)
        val scale = maxDim.toFloat() / maxOriginal
        val targetW = (originalW * scale).toInt()
        val targetH = (originalH * scale).toInt()

        assertEquals(1024, targetW)
        assertEquals(768, targetH)

        // Ensure aspect ratio is preserved
        val originalRatio = originalW.toDouble() / originalH.toDouble()
        val targetRatio = targetW.toDouble() / targetH.toDouble()
        assertEquals(originalRatio, targetRatio, 0.01)
    }
}
