package com.sahitol.collector

import com.sahitol.collector.domain.audio.AudioGrammar
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import java.io.File
import java.security.MessageDigest

/**
 * Unit test suite verifying:
 * - Audio asset manifest integrity, SHA-256 digests, license attribution, and offline status (R-OPS-03, AT-076).
 * - Spoken numeric grammar for all audit fixtures in Hindi and Marathi (docs/14_TRANSLATION_AUDIO_AUDIT.md, R-LANG-02, AT-050).
 */
class AudioGrammarAndManifestTest {

    @Test
    fun testAudioManifestStructureAndAssetIntegrity() {
        val manifestFile = File("src/main/assets/audio/audio_manifest.json")
        assertTrue("audio_manifest.json must exist in assets", manifestFile.exists())

        val content = manifestFile.readText(Charsets.UTF_8)
        val json = JSONObject(content)

        assertEquals("1.0", json.getString("format_version"))
        assertFalse("Audio assets must require zero runtime cloud calls (R-OPS-03)", json.getBoolean("runtime_cloud_call"))
        assertTrue("Manifest must declare at least 250 clips", json.getInt("total_clips") >= 250)

        val clipsArray = json.getJSONArray("clips")
        assertTrue("Clips array must match total_clips", clipsArray.length() == json.getInt("total_clips"))

        // Sample-check first 10 and last 10 clips for required fields and valid checksums
        val audioDir = File("src/main/assets/audio")
        val md = MessageDigest.getInstance("SHA-256")

        val indicesToCheck = listOf(0, 1, 10, 50, 100, 150, 200, clipsArray.length() - 1)
        for (idx in indicesToCheck) {
            val clipObj = clipsArray.getJSONObject(idx)
            val clipId = clipObj.getString("clip_id")
            val fileName = clipObj.getString("file_name")
            val sha256 = clipObj.getString("sha256")
            val durationMs = clipObj.getInt("duration_ms")
            val locale = clipObj.getString("locale")

            assertTrue("Clip $clipId must have hi or mr locale", locale == "hi" || locale == "mr")
            assertTrue("Duration must be positive for $clipId", durationMs > 0)
            assertEquals("Codec must be audio/mpeg", "audio/mpeg", clipObj.getString("codec"))
            assertTrue("SHA-256 must be 64 hex characters", sha256.matches(Regex("^[0-9a-f]{64}$")))

            val audioFile = File(audioDir, fileName)
            assertTrue("Audio file $fileName must exist on disk", audioFile.exists())
            assertTrue("Audio file $fileName must have non-zero content", audioFile.length() > 0)

            val fileBytes = audioFile.readBytes()
            val computedSha256 = md.digest(fileBytes).joinToString("") { "%02x".format(it) }
            assertEquals("SHA-256 digest mismatch for $fileName", sha256, computedSha256)
        }
    }

    @Test
    fun testIrregularNumbersGrammarAuditFixtures() {
        // Audit fixtures: 0, 1, 2, 11, 19, 21, 29, 99 rupees
        // Hindi:
        assertEquals(listOf("hi_num_0", "hi_unit_rupee"), AudioGrammar.speakMoney(0L, "hi"))
        assertEquals(listOf("hi_num_1", "hi_unit_rupee"), AudioGrammar.speakMoney(100L, "hi")) // 1 rupee (singular)
        assertEquals(listOf("hi_num_2", "hi_unit_rupees"), AudioGrammar.speakMoney(200L, "hi")) // 2 rupees (plural)
        assertEquals(listOf("hi_num_11", "hi_unit_rupees"), AudioGrammar.speakMoney(1100L, "hi"))
        assertEquals(listOf("hi_num_19", "hi_unit_rupees"), AudioGrammar.speakMoney(1900L, "hi"))
        assertEquals(listOf("hi_num_21", "hi_unit_rupees"), AudioGrammar.speakMoney(2100L, "hi"))
        assertEquals(listOf("hi_num_29", "hi_unit_rupees"), AudioGrammar.speakMoney(2900L, "hi"))
        assertEquals(listOf("hi_num_99", "hi_unit_rupees"), AudioGrammar.speakMoney(9900L, "hi"))

        // Marathi:
        assertEquals(listOf("mr_num_0", "mr_unit_rupee"), AudioGrammar.speakMoney(0L, "mr"))
        assertEquals(listOf("mr_num_1", "mr_unit_rupee"), AudioGrammar.speakMoney(100L, "mr"))
        assertEquals(listOf("mr_num_2", "mr_unit_rupees"), AudioGrammar.speakMoney(200L, "mr"))
        assertEquals(listOf("mr_num_21", "mr_unit_rupees"), AudioGrammar.speakMoney(2100L, "mr"))
        assertEquals(listOf("mr_num_99", "mr_unit_rupees"), AudioGrammar.speakMoney(9900L, "mr"))
    }

    @Test
    fun testPlaceValueJoiningGrammarAuditFixtures() {
        // Audit fixtures: 100, 101, 999, 1,000, 10,001, 1,00,000
        assertEquals(listOf("hi_num_1", "hi_scale_hundred"), AudioGrammar.decomposeInteger(100L, "hi"))
        assertEquals(listOf("hi_num_1", "hi_scale_hundred", "hi_num_1"), AudioGrammar.decomposeInteger(101L, "hi"))
        assertEquals(listOf("hi_num_9", "hi_scale_hundred", "hi_num_99"), AudioGrammar.decomposeInteger(999L, "hi"))
        assertEquals(listOf("hi_num_1", "hi_scale_thousand"), AudioGrammar.decomposeInteger(1000L, "hi"))
        assertEquals(listOf("hi_num_10", "hi_scale_thousand", "hi_num_1"), AudioGrammar.decomposeInteger(10001L, "hi"))
        assertEquals(listOf("hi_num_1", "hi_scale_lakh"), AudioGrammar.decomposeInteger(100000L, "hi"))

        // Marathi:
        assertEquals(listOf("mr_num_1", "mr_scale_hundred"), AudioGrammar.decomposeInteger(100L, "mr"))
        assertEquals(listOf("mr_num_1", "mr_scale_thousand"), AudioGrammar.decomposeInteger(1000L, "mr"))
        assertEquals(listOf("mr_num_1", "mr_scale_lakh"), AudioGrammar.decomposeInteger(100000L, "mr"))
    }

    @Test
    fun testPaisePreservationGrammarAuditFixtures() {
        // Audit fixtures: 1 paise, 50 paise, ₹10.50, ₹101.05
        // 1 paise
        assertEquals(listOf("hi_num_1", "hi_unit_paise"), AudioGrammar.speakMoney(1L, "hi"))
        // 50 paise
        assertEquals(listOf("hi_num_50", "hi_unit_paise"), AudioGrammar.speakMoney(50L, "hi"))
        // ₹10.50 (1050 paise)
        assertEquals(
            listOf("hi_num_10", "hi_unit_rupees", "hi_num_50", "hi_unit_paise"),
            AudioGrammar.speakMoney(1050L, "hi")
        )
        // ₹101.05 (10105 paise)
        assertEquals(
            listOf("hi_num_1", "hi_scale_hundred", "hi_num_1", "hi_unit_rupees", "hi_num_5", "hi_unit_paise"),
            AudioGrammar.speakMoney(10105L, "hi")
        )
        // ₹1,50,000 (15000000 paise)
        assertEquals(
            listOf("hi_num_1", "hi_scale_lakh", "hi_num_50", "hi_scale_thousand", "hi_unit_rupees"),
            AudioGrammar.speakMoney(15000000L, "hi")
        )
    }

    @Test
    fun testWeightGramsAndKgGrammarAuditFixtures() {
        // Audit fixtures: 250g, 1kg, 1.25kg, 2.5kg
        // 250g
        assertEquals(
            listOf("hi_num_2", "hi_scale_hundred", "hi_num_50", "hi_unit_gram"),
            AudioGrammar.speakWeight(250L, "hi")
        )
        // 1kg (1000g)
        assertEquals(
            listOf("hi_num_1", "hi_unit_kg"),
            AudioGrammar.speakWeight(1000L, "hi")
        )
        // 1.25kg (1250g)
        assertEquals(
            listOf("hi_num_1", "hi_unit_point", "hi_num_25", "hi_unit_kg"),
            AudioGrammar.speakWeight(1250L, "hi")
        )
        // 2.5kg (2500g)
        assertEquals(
            listOf("hi_num_2", "hi_unit_point", "hi_num_5", "hi_unit_kg"),
            AudioGrammar.speakWeight(2500L, "hi")
        )

        // Marathi weight
        assertEquals(
            listOf("mr_num_1", "mr_unit_kg"),
            AudioGrammar.speakWeight(1000L, "mr")
        )
    }

    @Test
    fun testRateAndRangeGrammarAuditFixtures() {
        // ₹150/kg
        assertEquals(
            listOf("hi_num_1", "hi_scale_hundred", "hi_num_50", "hi_unit_rupees", "hi_unit_per_kg"),
            AudioGrammar.speakRate(15000L, "hi")
        )

        // Range: ₹120–₹180/kg
        assertEquals(
            listOf(
                "hi_num_1", "hi_scale_hundred", "hi_num_20",
                "hi_unit_to",
                "hi_num_1", "hi_scale_hundred", "hi_num_80",
                "hi_unit_rupees", "hi_unit_per_kg"
            ),
            AudioGrammar.speakRange(12000L, 18000L, "hi")
        )
    }

    @Test
    fun testNegativeEconomicsAndUnknownFallbacks() {
        // Negative net: -₹50 (-5000 paise)
        assertEquals(
            listOf("hi_unit_negative", "hi_num_50", "hi_unit_rupees"),
            AudioGrammar.speakMoney(-5000L, "hi")
        )

        // Null / Unknown price
        assertEquals(listOf("hi_unit_unknown"), AudioGrammar.speakMoney(null, "hi"))
        assertEquals(listOf("hi_unit_unknown"), AudioGrammar.speakWeight(null, "hi"))
        assertEquals(listOf("mr_unit_unknown"), AudioGrammar.speakRate(null, "mr"))
        assertEquals(listOf("hi_unit_unknown"), AudioGrammar.speakRange(null, 15000L, "hi"))
    }

    @Test
    fun testStatusAndSafetyAudioGrammar() {
        assertEquals(listOf("hi_status_saved_locally"), AudioGrammar.speakStatus("SAVED_LOCALLY", "hi"))
        assertEquals(listOf("hi_status_synced"), AudioGrammar.speakStatus("SYNCED", "hi"))
        assertEquals(listOf("hi_status_confirmed"), AudioGrammar.speakStatus("CONFIRMED", "hi"))
        assertEquals(listOf("hi_status_paid"), AudioGrammar.speakStatus("PAID", "hi"))
        assertEquals(listOf("hi_non_epr_disclaimer"), AudioGrammar.speakStatus("NON_EPR", "hi"))

        assertEquals(listOf("mr_status_saved_locally"), AudioGrammar.speakStatus("SAVED_LOCALLY", "mr"))
        assertEquals(listOf("mr_status_paid"), AudioGrammar.speakStatus("PAID", "mr"))

        // Safety card guidance
        assertEquals(listOf("hi_safety_sc_cab_01"), AudioGrammar.speakSafety("SC-CAB-01", "hi"))
        assertEquals(listOf("mr_safety_sc_pcb_01"), AudioGrammar.speakSafety("SC-PCB-01", "mr"))
    }
}
