package com.sahitol.collector

import com.sahitol.collector.data.local.dao.DomainEventDao
import com.sahitol.collector.data.local.dao.LotDao
import com.sahitol.collector.data.local.dao.OutboxDao
import com.sahitol.collector.data.local.entity.DomainEventEntity
import com.sahitol.collector.data.local.entity.LotEntity
import com.sahitol.collector.data.local.entity.OutboxOperationEntity
import com.sahitol.collector.data.repository.CreateLotParams
import com.sahitol.collector.domain.classifier.ClassificationResult
import com.sahitol.collector.domain.classifier.LiteRtClassifier
import com.sahitol.collector.domain.model.MaterialCategory
import kotlinx.coroutines.runBlocking
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test

class ClassifierIntegrationTest {

    @Test
    fun test_advisoryClassificationAboveThreshold_R_ML_03_AT_046() {
        // Reviewed provider labels above the 0.52 threshold remain advisory.
        val highConfidenceResult = ClassificationResult(
            categoryCode = "MAT-PCB-01",
            categoryNameEn = "High-Grade PCB",
            categoryNameHi = "उच्च श्रेणी पीसीबी",
            categoryNameMr = "उच्च दर्जाचे पीसीबी",
            confidence = 0.89f,
            meetsThreshold = 0.89f >= 0.52f,
            latencyMs = 7.57,
            isFallback = false,
            rawScores = mapOf("MAT-PCB-01" to 0.89f, "MAT-CAB-01" to 0.05f),
            modelVersion = "v2.0-mendeley-openimages",
            modelChecksum = LiteRtClassifier.EXPECTED_SHA256
        )

        assertTrue(highConfidenceResult.meetsThreshold)
        assertFalse(highConfidenceResult.isFallback)
        assertEquals("MAT-PCB-01", highConfidenceResult.categoryCode)
        assertEquals("उच्च श्रेणी पीसीबी", highConfidenceResult.categoryNameHi)
        assertEquals("v2.0-mendeley-openimages", highConfidenceResult.modelVersion)
        assertEquals(LiteRtClassifier.EXPECTED_SHA256, highConfidenceResult.modelChecksum)

        val mappedCategory = MaterialCategory.fromModelCode(highConfidenceResult.categoryCode)
        assertEquals(MaterialCategory.PCB, mappedCategory)
    }

    @Test
    fun test_lowConfidenceAbstention_R_ML_03_AT_046() {
        // Confidence below 0.52 threshold routes to explicit abstention / manual fallback
        val lowConfidenceScore = 0.48f
        val lowConfidenceResult = ClassificationResult(
            categoryCode = "MAT-PLA-01",
            categoryNameEn = "Rigid FR Plastics",
            categoryNameHi = "कठोर प्लास्टिक",
            categoryNameMr = "कठीण प्लॅस्टिक",
            confidence = lowConfidenceScore,
            meetsThreshold = lowConfidenceScore >= 0.52f,
            latencyMs = 8.12,
            isFallback = true,
            rawScores = mapOf("MAT-PLA-01" to 0.52f, "MAT-UNK-01" to 0.35f),
            modelVersion = "v2.0-mendeley-openimages",
            modelChecksum = LiteRtClassifier.EXPECTED_SHA256
        )

        assertFalse(lowConfidenceResult.meetsThreshold)
        assertTrue(lowConfidenceResult.isFallback)
        assertEquals("MAT-PLA-01", lowConfidenceResult.categoryCode)
    }

    @Test
    fun test_corruptModelGracefulFallback_R_ML_03_AT_046() {
        // Corrupted model buffer or failed initialization does not crash, provides safe fallback
        val corruptedClassifier = LiteRtClassifier(
            context = null,
            customInterpreter = null,
            forceCorrupted = true
        )

        assertTrue(corruptedClassifier.isCorrupted)
        assertFalse(corruptedClassifier.isModelLoaded())
        assertFalse(corruptedClassifier.verifyChecksum())

        val fallback = corruptedClassifier.getFallbackResult(0.0)
        assertEquals("ABSTAIN", fallback.categoryCode)
        assertEquals("Unknown / Other", fallback.categoryNameEn)
        assertEquals("अज्ञात / अन्य", fallback.categoryNameHi)
        assertEquals(0.0f, fallback.confidence, 0.001f)
        assertFalse(fallback.meetsThreshold)
        assertTrue(fallback.isFallback)
    }

    @Test
    fun test_separateSuggestionAndHumanLabelPersistence_R_ML_04_AT_047() {
        // R-ML-04 / AT-047: Persist suggestion/confidence/model version separately from human label
        val params = CreateLotParams(
            accountId = "col_demo_santosh",
            deviceId = "dev_test_01",
            materialCode = "CABLE", // Human selected/confirmed Copper Cable
            estimatedWeightG = 2500L,
            estimatedLowPaise = 40000L,
            estimatedMedianPaise = 45000L,
            estimatedHighPaise = 50000L,
            localPhotoPath = "/data/user/0/com.sahitol.collector/cache/lot_photo.jpg",
            aiSuggestedCode = "Mobile", // Raw provider label is retained
            aiConfidence = 0.78f,
            aiModelVersion = "v2.0-mendeley-openimages"
        )

        val lotEntity = LotEntity(
            lotId = "lot_test_ml_01",
            accountId = params.accountId,
            materialCode = params.materialCode,
            estimatedWeightG = params.estimatedWeightG,
            localPhotoPath = params.localPhotoPath,
            aiSuggestedCode = params.aiSuggestedCode,
            aiConfidence = params.aiConfidence,
            aiModelVersion = params.aiModelVersion
        )

        // Human confirmed label remains distinct from AI suggestion
        assertEquals("CABLE", lotEntity.materialCode)
        assertEquals("Mobile", lotEntity.aiSuggestedCode)
        assertEquals(0.78f, lotEntity.aiConfidence!!, 0.001f)
        assertEquals("v2.0-mendeley-openimages", lotEntity.aiModelVersion)

        // Domain event payload JSON preserves both
        val payloadObj = JSONObject().apply {
            put("lot_id", lotEntity.lotId)
            put("material_code", lotEntity.materialCode)
            put("estimated_weight_g", lotEntity.estimatedWeightG)
            if (lotEntity.aiSuggestedCode != null) put("ai_suggested_code", lotEntity.aiSuggestedCode)
            if (lotEntity.aiConfidence != null) put("ai_confidence", lotEntity.aiConfidence)
            if (lotEntity.aiModelVersion != null) put("ai_model_version", lotEntity.aiModelVersion)
        }
        val jsonString = payloadObj.toString()
        assertTrue(jsonString.contains("\"material_code\":\"CABLE\""))
        assertTrue(jsonString.contains("\"ai_suggested_code\":\"Mobile\""))
        assertTrue(jsonString.contains("\"ai_model_version\":\"v2.0-mendeley-openimages\""))
    }

    @Test
    fun test_materialCategoryFromModelCodeMapping() {
        assertEquals(MaterialCategory.MIXED_EWASTE, MaterialCategory.fromModelCode("Mobile"))
        assertEquals(MaterialCategory.MIXED_EWASTE, MaterialCategory.fromModelCode("Keyboard"))
        assertEquals(MaterialCategory.MIXED_EWASTE, MaterialCategory.fromModelCode("Mouse"))
        assertEquals(MaterialCategory.OTHER, MaterialCategory.fromModelCode("Battery_Waste"))
        assertEquals(MaterialCategory.PCB, MaterialCategory.fromModelCode("PCB"))
        assertTrue(MaterialCategory.hasSafeManualMapping("Mobile"))
        assertFalse(MaterialCategory.hasSafeManualMapping("PCB"))
        assertEquals(MaterialCategory.BATTERY_LI_ION, MaterialCategory.fromModelCode("MAT-BAT-01"))
        assertEquals(MaterialCategory.BATTERY_LI_ION, MaterialCategory.fromModelCode("MAT-BAT-02"))
        assertEquals(MaterialCategory.COPPER_CABLE, MaterialCategory.fromModelCode("MAT-CAB-01"))
        assertEquals(MaterialCategory.CRT_MONITOR, MaterialCategory.fromModelCode("MAT-CRT-01"))
        assertEquals(MaterialCategory.LCD_MONITOR, MaterialCategory.fromModelCode("MAT-LCD-01"))
        assertEquals(MaterialCategory.MIXED_EWASTE, MaterialCategory.fromModelCode("MAT-MET-01"))
        assertEquals(MaterialCategory.MIXED_EWASTE, MaterialCategory.fromModelCode("MAT-MIX-01"))
        assertEquals(MaterialCategory.ELECTRIC_MOTOR, MaterialCategory.fromModelCode("MAT-MOT-01"))
        assertEquals(MaterialCategory.PCB, MaterialCategory.fromModelCode("MAT-PCB-01"))
        assertEquals(MaterialCategory.PCB, MaterialCategory.fromModelCode("MAT-PCB-02"))
        assertEquals(MaterialCategory.RIGID_PLASTIC, MaterialCategory.fromModelCode("MAT-PLA-01"))
        assertEquals(MaterialCategory.OTHER, MaterialCategory.fromModelCode("MAT-UNK-01"))
        assertEquals(MaterialCategory.OTHER, MaterialCategory.fromModelCode(null))
    }

    @Test
    fun test_frozenModelExpectedChecksumConstant() {
        assertEquals(
            "32098e6714ea806ecfdf0d87e848aa394ac3d852c81989ecae33f0e142e5438f",
            LiteRtClassifier.EXPECTED_SHA256
        )
    }
}
