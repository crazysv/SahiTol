package com.sahitol.collector

import android.content.SharedPreferences
import com.sahitol.collector.data.session.SessionManager
import com.sahitol.collector.domain.locale.LocaleFormatter
import com.sahitol.collector.domain.locale.MaterialAliases
import com.sahitol.collector.domain.locale.NumeralPreference
import com.sahitol.collector.domain.locale.SahiTolStrings
import com.sahitol.collector.domain.model.MaterialCategory
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

/**
 * Unit test suite for Task T036:
 * Complete language resources and accessible interaction:
 * - Translation parity across hi, mr, en strings catalog (R-LANG-01).
 * - Unavailable translation audit reporting (AT-049).
 * - Four immutable status invariants across languages.
 * - Indian number formatting and lakh notation.
 * - Exact paise preservation audit fixtures (1 paise, 50 paise, ₹10.50, ₹101.05, ₹1,50,000).
 * - Mass formatting in grams and kilograms (250g, 1kg, 1.25kg, 2.5kg).
 * - Rates and price ranges (₹150/kg, ₹120-₹180/kg).
 * - Numeral preference (English Digits vs Devanagari Numerals).
 * - Colloquial scrap material aliases in Hindi and Marathi (T010).
 * - Language and numeral preference persistence in SessionManager.
 * - TalkBack screen-reader semantics (label + value + unit + status).
 */
class LanguageAndAccessibilityTest {

    private class MockSharedPreferences : SharedPreferences {
        val map = mutableMapOf<String, Any>()

        override fun getAll(): MutableMap<String, *> = map
        override fun getString(key: String?, defValue: String?): String? = (map[key] as? String) ?: defValue
        override fun getStringSet(key: String?, defValues: MutableSet<String>?): MutableSet<String>? = defValues
        override fun getInt(key: String?, defValue: Int): Int = (map[key] as? Int) ?: defValue
        override fun getLong(key: String?, defValue: Long): Long = (map[key] as? Long) ?: defValue
        override fun getFloat(key: String?, defValue: Float): Float = (map[key] as? Float) ?: defValue
        override fun getBoolean(key: String?, defValue: Boolean): Boolean = (map[key] as? Boolean) ?: defValue
        override fun contains(key: String?): Boolean = map.containsKey(key)
        override fun registerOnSharedPreferenceChangeListener(listener: SharedPreferences.OnSharedPreferenceChangeListener?) {}
        override fun unregisterOnSharedPreferenceChangeListener(listener: SharedPreferences.OnSharedPreferenceChangeListener?) {}

        override fun edit(): SharedPreferences.Editor = Editor(map)

        private class Editor(private val map: MutableMap<String, Any>) : SharedPreferences.Editor {
            private val pending = mutableMapOf<String, Any>()

            override fun putString(key: String?, value: String?): SharedPreferences.Editor {
                if (key != null && value != null) pending[key] = value
                return this
            }
            override fun putStringSet(key: String?, values: MutableSet<String>?): SharedPreferences.Editor = this
            override fun putInt(key: String?, value: Int): SharedPreferences.Editor {
                if (key != null) pending[key] = value
                return this
            }
            override fun putLong(key: String?, value: Long): SharedPreferences.Editor {
                if (key != null) pending[key] = value
                return this
            }
            override fun putFloat(key: String?, value: Float): SharedPreferences.Editor {
                if (key != null) pending[key] = value
                return this
            }
            override fun putBoolean(key: String?, value: Boolean): SharedPreferences.Editor {
                if (key != null) pending[key] = value
                return this
            }
            override fun remove(key: String?): SharedPreferences.Editor {
                if (key != null) pending.remove(key)
                return this
            }
            override fun clear(): SharedPreferences.Editor {
                pending.clear()
                return this
            }
            override fun commit(): Boolean {
                map.putAll(pending)
                return true
            }
            override fun apply() {
                map.putAll(pending)
            }
        }
    }

    private lateinit var mockPrefs: MockSharedPreferences

    @Before
    fun setUp() {
        mockPrefs = MockSharedPreferences()
    }

    @Test
    fun testTranslationKeyParityAndPlaceholderAudit() {
        // Run automated audit across en, hi, mr string catalogs
        val auditResult = SahiTolStrings.runAudit()

        assertTrue(
            "Translation audit failed: Missing Hindi keys: ${auditResult.missingHi}",
            auditResult.missingHi.isEmpty()
        )
        assertTrue(
            "Translation audit failed: Missing Marathi keys: ${auditResult.missingMr}",
            auditResult.missingMr.isEmpty()
        )
        assertTrue(
            "Translation audit failed: Placeholder mismatches: ${auditResult.placeholderMismatches}",
            auditResult.placeholderMismatches.isEmpty()
        )
        assertTrue("Audit must verify at least 60 core keys", auditResult.totalKeys >= 60)
        assertTrue("Overall audit must pass", auditResult.isPassed)
    }

    @Test
    fun testUnavailableTranslationAuditReporting() {
        // AT-049: "unavailable translation is reported in audit, not hidden by English fallback"
        val fallbackResult = SahiTolStrings.get("non_existent_key_for_test", "mr")
        assertEquals("non_existent_key_for_test", fallbackResult)

        val recorded = SahiTolStrings.getAuditRecordedMissingAccesses()
        assertTrue("Missing key must be recorded in audit log", recorded.contains("mr:non_existent_key_for_test"))
    }

    @Test
    fun testFourImmutableStatusInvariantsAcrossLanguages() {
        // Verify the 4 mandatory status strings across languages
        // 1. Saved locally
        assertEquals("Saved on phone", SahiTolStrings.get("status_saved_locally", "en"))
        assertEquals("फोन में सुरक्षित", SahiTolStrings.get("status_saved_locally", "hi"))
        assertEquals("फोनवर जतन केले", SahiTolStrings.get("status_saved_locally", "mr"))

        // 2. Synchronized
        assertEquals("Synchronized", SahiTolStrings.get("status_synced", "en"))
        assertEquals("सर्वर पर सिंक हुआ", SahiTolStrings.get("status_synced", "hi"))
        assertEquals("सर्व्हरवर सिंक केले", SahiTolStrings.get("status_synced", "mr"))

        // 3. Recycler Confirmed
        assertEquals("Recycler Confirmed", SahiTolStrings.get("status_confirmed", "en"))
        assertEquals("रिसाइकलर द्वारा पुष्टि", SahiTolStrings.get("status_confirmed", "hi"))
        assertEquals("रिसायकलरद्वारे पुष्टी केली", SahiTolStrings.get("status_confirmed", "mr"))

        // 4. Payment Acknowledged
        assertEquals("Payment Acknowledged", SahiTolStrings.get("status_paid", "en"))
        assertEquals("भुगतान स्वीकृत", SahiTolStrings.get("status_paid", "hi"))
        assertEquals("पैसे मिळाल्याची पोच", SahiTolStrings.get("status_paid", "mr"))

        // Statutory Non-EPR Disclaimer
        val hiDisclaimer = SahiTolStrings.get("non_epr_disclaimer", "hi")
        assertTrue(hiDisclaimer.contains("डिजिटल हैंडओवर रिकॉर्ड"))
        assertTrue(hiDisclaimer.contains("ईपीआर"))
        assertTrue(hiDisclaimer.contains("रिसाइक्लिंग को सिद्ध नहीं करता"))
    }

    @Test
    fun testIndianNumberFormattingAndLakhNotation() {
        assertEquals("0", LocaleFormatter.formatIndianNumber(0L))
        assertEquals("99", LocaleFormatter.formatIndianNumber(99L))
        assertEquals("999", LocaleFormatter.formatIndianNumber(999L))
        assertEquals("1,000", LocaleFormatter.formatIndianNumber(1000L))
        assertEquals("10,001", LocaleFormatter.formatIndianNumber(10001L))
        assertEquals("1,00,000", LocaleFormatter.formatIndianNumber(100000L))
        assertEquals("15,50,000", LocaleFormatter.formatIndianNumber(1550000L))
        assertEquals("1,00,00,000", LocaleFormatter.formatIndianNumber(10000000L))
        assertEquals("-1,50,000", LocaleFormatter.formatIndianNumber(-150000L))
    }

    @Test
    fun testPaisePreservationAuditFixtures() {
        // Exact audit fixtures from docs/14_TRANSLATION_AUDIO_AUDIT.md
        // 1 paise preserved, not rounded away
        assertEquals("₹0.01", LocaleFormatter.formatPaise(1L))
        // 50 paise
        assertEquals("₹0.50", LocaleFormatter.formatPaise(50L))
        // ₹10.50 (1050 paise)
        assertEquals("₹10.50", LocaleFormatter.formatPaise(1050L))
        // ₹101.05 (10105 paise)
        assertEquals("₹101.05", LocaleFormatter.formatPaise(10105L))
        // ₹1,50,000 (15000000 paise)
        assertEquals("₹1,50,000", LocaleFormatter.formatPaise(15000000L))
        // Negative amount (economics net)
        assertEquals("-₹50", LocaleFormatter.formatPaise(-5000L))
        assertEquals("-₹50.50", LocaleFormatter.formatPaise(-5050L))
    }

    @Test
    fun testWeightGramsAndKilogramsAuditFixtures() {
        // Audit fixtures: 250g, 1kg, 1.25kg, 2.5kg
        assertEquals("250 g", LocaleFormatter.formatGrams(250L, "en"))
        assertEquals("250 ग्राम", LocaleFormatter.formatGrams(250L, "hi"))
        assertEquals("250 ग्रॅम", LocaleFormatter.formatGrams(250L, "mr"))

        assertEquals("1 kg", LocaleFormatter.formatGrams(1000L, "en"))
        assertEquals("1 किग्रा", LocaleFormatter.formatGrams(1000L, "hi"))
        assertEquals("1 किलो", LocaleFormatter.formatGrams(1000L, "mr"))

        assertEquals("1.25 kg", LocaleFormatter.formatGrams(1250L, "en"))
        assertEquals("2.5 kg", LocaleFormatter.formatGrams(2500L, "en"))
        assertEquals("500 kg", LocaleFormatter.formatGrams(500000L, "en"))
    }

    @Test
    fun testRateAndRangeFormatting() {
        assertEquals("₹150 / kg", LocaleFormatter.formatRate(15000L, "en"))
        assertEquals("₹150 प्रति किग्रा", LocaleFormatter.formatRate(15000L, "hi"))
        assertEquals("₹150 प्रति किलो", LocaleFormatter.formatRate(15000L, "mr"))

        // ₹120–₹180/kg
        assertEquals("₹120 – ₹180 / kg", LocaleFormatter.formatRange(12000L, 18000L, "en"))
        assertEquals("₹120 – ₹180 प्रति किग्रा", LocaleFormatter.formatRange(12000L, 18000L, "hi"))
    }

    @Test
    fun testDevanagariNumeralPreference() {
        // Test Latin to Devanagari digit conversion
        val latinText = "₹1,50,000"
        val devanagariText = NumeralPreference.applyPreference(latinText, NumeralPreference.DEVANAGARI)
        assertEquals("₹१,५०,०००", devanagariText)

        val devanagariWeight = LocaleFormatter.formatGrams(2500L, "hi", NumeralPreference.DEVANAGARI)
        assertEquals("२.५ किग्रा", devanagariWeight)

        val devanagariPaise = LocaleFormatter.formatPaise(1050L, "hi", NumeralPreference.DEVANAGARI)
        assertEquals("₹१०.५०", devanagariPaise)
    }

    @Test
    fun testColloquialMaterialAliasesLookup() {
        // PCB colloquial aliases
        val pcbHi = MaterialAliases.getAliasesForCategory(MaterialCategory.PCB, "hi")
        assertTrue(pcbHi.contains("मदरबोर्ड"))
        assertTrue(pcbHi.contains("हरा पत्ता"))

        val pcbMr = MaterialAliases.getAliasesForCategory(MaterialCategory.PCB, "mr")
        assertTrue(pcbMr.contains("हिरवा बोर्ड"))

        // Cable aliases
        val cableHi = MaterialAliases.getAliasesForCategory(MaterialCategory.COPPER_CABLE, "hi")
        assertTrue(cableHi.contains("तांबा तार"))

        // Battery aliases
        val batHi = MaterialAliases.getAliasesForCategory(MaterialCategory.BATTERY_LI_ION, "hi")
        assertTrue(batHi.contains("गाड़ी की बैटरी"))

        // Reverse search
        assertEquals(MaterialCategory.PCB, MaterialAliases.searchCategoryByColloquialTerm("हरा पत्ता"))
        assertEquals(MaterialCategory.PCB, MaterialAliases.searchCategoryByColloquialTerm("मदरबोर्ड"))
        assertEquals(MaterialCategory.COPPER_CABLE, MaterialAliases.searchCategoryByColloquialTerm("तांबा तार"))
        assertEquals(MaterialCategory.BATTERY_LI_ION, MaterialAliases.searchCategoryByColloquialTerm("गाडीची बॅटरी"))
        assertEquals(MaterialCategory.ELECTRIC_MOTOR, MaterialAliases.searchCategoryByColloquialTerm("कूलर मोटर"))
        assertEquals(MaterialCategory.CRT_MONITOR, MaterialAliases.searchCategoryByColloquialTerm("पुराना टीवी"))
    }

    @Test
    fun testLanguageAndNumeralPreferencePersistenceInSessionManager() {
        val sessionManager = SessionManager(mockPrefs)

        // Default language is 'hi' and default numeral is 'LATIN'
        assertEquals("hi", sessionManager.session.value.language)
        assertEquals(NumeralPreference.LATIN, sessionManager.session.value.numeralPreference)

        // Switch to Marathi
        sessionManager.setLanguage("mr")
        assertEquals("mr", sessionManager.session.value.language)
        assertEquals("mr", mockPrefs.map["language"])

        // Switch numeral preference to Devanagari
        sessionManager.setNumeralPreference(NumeralPreference.DEVANAGARI)
        assertEquals(NumeralPreference.DEVANAGARI, sessionManager.session.value.numeralPreference)
        assertEquals("DEVANAGARI", mockPrefs.map["numeral_preference"])

        // Safe logout preserves preferences
        sessionManager.logoutPreservingData()
        assertFalse(sessionManager.session.value.isLoggedIn)
        assertEquals("mr", sessionManager.session.value.language)
        assertEquals(NumeralPreference.DEVANAGARI, sessionManager.session.value.numeralPreference)
    }

    @Test
    fun testAccessibilityScreenReaderSemantics() {
        // "Screen-reader content reads label + value + unit + status" (14_TRANSLATION_AUDIO_AUDIT.md)
        val announcement = LocaleFormatter.formatScreenReader(
            label = "PCB Lot #104",
            value = "14.25",
            unit = "kg",
            status = "Saved on phone"
        )
        assertEquals("PCB Lot #104, 14.25, kg, Saved on phone", announcement)

        // Verification in Hindi
        val hiAnnouncement = LocaleFormatter.formatScreenReader(
            label = "पीसीबी लॉट",
            value = "१४.२५",
            unit = "किग्रा",
            status = "फोन में सुरक्षित"
        )
        assertEquals("पीसीबी लॉट, १४.२५, किग्रा, फोन में सुरक्षित", hiAnnouncement)
    }
}
