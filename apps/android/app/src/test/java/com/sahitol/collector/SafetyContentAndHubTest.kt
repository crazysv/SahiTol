package com.sahitol.collector

import com.sahitol.collector.domain.audio.AudioGrammar
import com.sahitol.collector.domain.model.MaterialCategory
import com.sahitol.collector.domain.safety.HazardLevel
import com.sahitol.collector.domain.safety.SafetyContentManager
import org.junit.Assert.*
import org.junit.Test

/**
 * Unit tests for Safety Content, Localization, Audio Wiring, and Invariants (T035, T037, T039).
 * Verifies R-SAFE-01, AT-048, and non-instructional hazard policies.
 */
class SafetyContentAndHubTest {

    @Test
    fun testAllNineCardsPresentAndConfigured() {
        val cards = SafetyContentManager.getAllCards()
        assertEquals("Expected exactly 9 curated safety cards", 9, cards.size)

        val cardIds = cards.map { it.id }.toSet()
        val expectedIds = setOf(
            "SC-CAB-01", "SC-PCB-01", "SC-CRT-01",
            "SC-BAT-01", "SC-BAT-02", "SC-BAT-03",
            "SC-DAM-01", "SC-PLA-01", "SC-MIX-01"
        )
        assertEquals("All expected safety card IDs must be present", expectedIds, cardIds)

        for (card in cards) {
            assertTrue("Card ID must start with SC-", card.id.startsWith("SC-"))
            assertTrue("Guide ID must start with SG-", card.guideId.startsWith("SG-"))
            assertTrue("Material IDs must not be empty", card.materialIds.isNotEmpty())
            assertTrue("Hazard type must not be blank", card.hazardType.isNotBlank())
            assertTrue("References must cite official guidelines", card.references.isNotEmpty())
            assertTrue("Audio key must not be blank", card.audioKey.isNotBlank())
        }
    }

    @Test
    fun testTrilingualContentAndDevanagariParity() {
        val cards = SafetyContentManager.getAllCards()
        val devanagariRegex = Regex("[\\u0900-\\u097F]")

        for (card in cards) {
            val en = card.locales["en"]
            val hi = card.locales["hi"]
            val mr = card.locales["mr"]

            assertNotNull("English locale missing for ${card.id}", en)
            assertNotNull("Hindi locale missing for ${card.id}", hi)
            assertNotNull("Marathi locale missing for ${card.id}", mr)

            // Assert non-blank text
            assertTrue("EN title missing for ${card.id}", en!!.title.isNotBlank())
            assertTrue("HI title missing for ${card.id}", hi!!.title.isNotBlank())
            assertTrue("MR title missing for ${card.id}", mr!!.title.isNotBlank())

            assertTrue("EN warning missing for ${card.id}", en.hazardWarning.isNotBlank())
            assertTrue("HI warning missing for ${card.id}", hi.hazardWarning.isNotBlank())
            assertTrue("MR warning missing for ${card.id}", mr.hazardWarning.isNotBlank())

            assertTrue("EN audio script missing for ${card.id}", en.audioScript.isNotBlank())
            assertTrue("HI audio script missing for ${card.id}", hi.audioScript.isNotBlank())
            assertTrue("MR audio script missing for ${card.id}", mr.audioScript.isNotBlank())

            // Assert authentic Devanagari script in Hindi and Marathi
            assertTrue("Hindi title must contain Devanagari script for ${card.id}", devanagariRegex.containsMatchIn(hi.title))
            assertTrue("Marathi title must contain Devanagari script for ${card.id}", devanagariRegex.containsMatchIn(mr.title))
            assertTrue("Hindi warning must contain Devanagari script for ${card.id}", devanagariRegex.containsMatchIn(hi.hazardWarning))
            assertTrue("Marathi warning must contain Devanagari script for ${card.id}", devanagariRegex.containsMatchIn(mr.hazardWarning))
        }
    }

    @Test
    fun testAudioKeysMapToValidClips() {
        val cards = SafetyContentManager.getAllCards()

        for (card in cards) {
            val hiClips = AudioGrammar.speakSafety(card.id, "hi")
            val mrClips = AudioGrammar.speakSafety(card.id, "mr")

            assertEquals(1, hiClips.size)
            assertEquals(1, mrClips.size)

            val expectedHiClip = "hi_safety_" + card.id.lowercase().replace("-", "_")
            val expectedMrClip = "mr_safety_" + card.id.lowercase().replace("-", "_")

            assertEquals(expectedHiClip, hiClips[0])
            assertEquals(expectedMrClip, mrClips[0])
        }
    }

    @Test
    fun testCategoryAndMaterialLookups() {
        // Category lookups
        val pcbCard = SafetyContentManager.getCardForCategory(MaterialCategory.PCB)
        assertNotNull(pcbCard)
        assertEquals("SC-PCB-01", pcbCard?.id)

        val crtCard = SafetyContentManager.getCardForCategory(MaterialCategory.CRT_MONITOR)
        assertNotNull(crtCard)
        assertEquals("SC-CRT-01", crtCard?.id)

        val cableCard = SafetyContentManager.getCardForCategory(MaterialCategory.COPPER_CABLE)
        assertNotNull(cableCard)
        assertEquals("SC-CAB-01", cableCard?.id)

        val batCard = SafetyContentManager.getCardForCategory(MaterialCategory.BATTERY_LI_ION)
        assertNotNull(batCard)
        assertTrue(batCard?.id in listOf("SC-BAT-01", "SC-BAT-02", "SC-BAT-03"))

        // Material ID lookups
        val matPcb = SafetyContentManager.getCardForMaterial("MAT-PCB-01")
        assertEquals("SC-PCB-01", matPcb?.id)

        val matCrt = SafetyContentManager.getCardForMaterial("MAT-CRT-01")
        assertEquals("SC-CRT-01", matCrt?.id)

        val matCab = SafetyContentManager.getCardForMaterial("MAT-CAB-02")
        assertEquals("SC-CAB-01", matCab?.id)

        val matLead = SafetyContentManager.getCardForMaterial("MAT-BAT-01")
        assertEquals("SC-BAT-01", matLead?.id)
    }

    @Test
    fun testProhibitionsAndStepsCompleteness() {
        val cards = SafetyContentManager.getAllCards()

        for (card in cards) {
            assertTrue("Expected at least 3 prohibitions for ${card.id}", card.prohibitions.size >= 3)
            assertTrue("Expected at least 3 steps for ${card.id}", card.steps.size >= 3)

            for (prohib in card.prohibitions) {
                assertTrue("Prohibition label en missing for ${card.id}", prohib.enLabel.isNotBlank())
                assertTrue("Prohibition label hi missing for ${card.id}", prohib.hiLabel.isNotBlank())
                assertTrue("Prohibition label mr missing for ${card.id}", prohib.mrLabel.isNotBlank())
                assertTrue("Prohibition icon missing for ${card.id}", prohib.iconName.isNotBlank())
            }

            for ((index, step) in card.steps.withIndex()) {
                assertEquals(index + 1, step.stepNumber)
                assertTrue("Step title en missing for ${card.id}", step.enTitle.isNotBlank())
                assertTrue("Step title hi missing for ${card.id}", step.hiTitle.isNotBlank())
                assertTrue("Step title mr missing for ${card.id}", step.mrTitle.isNotBlank())
                assertTrue("Step desc en missing for ${card.id}", step.enDesc.isNotBlank())
                assertTrue("Step desc hi missing for ${card.id}", step.hiDesc.isNotBlank())
                assertTrue("Step desc mr missing for ${card.id}", step.mrDesc.isNotBlank())
            }
        }
    }

    @Test
    fun testNonInstructionalSafetyInvariant() {
        val cards = SafetyContentManager.getAllCards()
        val bannedInstructionalTerms = listOf(
            "recipe", "how to extract gold", "smelting procedure",
            "boil in nitric acid", "open the tube with hammer",
            "burn the plastic off"
        )

        for (card in cards) {
            val allText = (
                card.locales.values.map { "${it.title} ${it.subtitle} ${it.hazardWarning} ${it.safeHandlingInstruction} ${it.audioScript}" } +
                card.steps.map { "${it.enDesc} ${it.hiDesc} ${it.mrDesc}" }
            ).joinToString(" ").lowercase()

            for (banned in bannedInstructionalTerms) {
                assertFalse("Card ${card.id} must not contain instructional extraction text: '$banned'", allText.contains(banned))
            }
        }
    }
}
