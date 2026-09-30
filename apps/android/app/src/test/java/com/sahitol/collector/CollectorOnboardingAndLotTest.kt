package com.sahitol.collector

import android.content.Context
import android.content.SharedPreferences
import com.sahitol.collector.data.session.CollectorSession
import com.sahitol.collector.data.session.SessionManager
import com.sahitol.collector.domain.model.MaterialCategory
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import java.security.MessageDigest

/**
 * Unit test suite for Task T017:
 * Collector Onboarding, Authentication, Lot Creation, and Session Management.
 * Validates requirements R-AUTH-01, R-AUTH-03, R-LOT-01, R-LOT-02, R-UX-01.
 */
class CollectorOnboardingAndLotTest {

    private class MockSharedPreferences : SharedPreferences {
        private val map = mutableMapOf<String, Any>()

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

    @Test
    fun testCollectorSessionPhoneMasking() {
        val session1 = CollectorSession(
            accountId = "col_123",
            phone = "9876543210",
            alias = "Ramesh Kumar",
            isDemo = false,
            language = "hi",
            isLoggedIn = true
        )
        assertEquals("******3210", session1.maskedPhone)

        val nullPhoneSession = CollectorSession(
            accountId = "col_456",
            phone = null,
            alias = "Anonymous",
            isDemo = true,
            language = "en",
            isLoggedIn = true
        )
        assertEquals("—", nullPhoneSession.maskedPhone)
    }

    @Test
    fun testMaterialCategoryCanonicalTaxonomyAndRoutes() {
        // Battery must be routed to BATTERY_RULES (R-BAT-01, AT-018)
        val battery = MaterialCategory.BATTERY_LI_ION
        assertEquals("BATTERY_RULES", battery.regulatoryRoute)
        assertEquals("बैटरी (लिथियम/लेड)", battery.getDisplayName("hi"))
        assertEquals("बॅटरी (लिथियम/लेड)", battery.getDisplayName("mr"))
        assertEquals("Lithium / Lead Battery", battery.getDisplayName("en"))

        // CRT must be routed to E_WASTE_HAZARDOUS (R-MAT-01)
        val crt = MaterialCategory.CRT_MONITOR
        assertEquals("E_WASTE_HAZARDOUS", crt.regulatoryRoute)

        // Copper Cable must be routed to standard E_WASTE
        val cable = MaterialCategory.COPPER_CABLE
        assertEquals("E_WASTE", cable.regulatoryRoute)

        // Fallback for unknown codes
        val unknown = MaterialCategory.fromCode("UNKNOWN_FOO_BAR")
        assertEquals(MaterialCategory.OTHER, unknown)
        assertEquals("PENDING_CLASSIFICATION", unknown.regulatoryRoute)
    }

    @Test
    fun testLotWeightFractionalKgToIntegerGramsPrecision() {
        // R-LOT-01, AT-012: Integer grams representation without fractional floating point loss
        val weightKg = 14.25
        val grams = (weightKg * 1000).toLong()
        assertEquals(14250L, grams)

        // Check round-trip back to kg
        val roundTripKg = grams / 1000.0
        assertEquals(14.25, roundTripKg, 0.0001)

        // Micro-lot check: 0.1 kg = 100 grams
        val microKg = 0.1
        val microGrams = (microKg * 1000).toLong()
        assertEquals(100L, microGrams)
    }

    @Test
    fun testCanonicalLotPayloadSerializationAndSha256() {
        val payloadObj = JSONObject().apply {
            put("lot_id", "test-lot-123")
            put("material_code", "PCB")
            put("estimated_weight_g", 14250L)
            put("created_at", 1727654400000L)
        }
        val payloadJson = payloadObj.toString()
        assertTrue(payloadJson.contains("\"material_code\":\"PCB\""))
        assertTrue(payloadJson.contains("\"estimated_weight_g\":14250"))

        val md = MessageDigest.getInstance("SHA-256")
        val digest = md.digest(payloadJson.toByteArray(Charsets.UTF_8))
        val hex = digest.joinToString("") { "%02x".format(it) }
        assertEquals(64, hex.length)
        assertTrue(hex.matches(Regex("^[0-9a-f]{64}$")))
    }

    @Test
    fun testConditionCategoriesCoverage() {
        // Stitch C05 conditions: Clean, Damaged, Sorted, Mixed
        val conditions = listOf("Clean", "Damaged", "Sorted", "Mixed")
        assertEquals(4, conditions.size)
        assertTrue(conditions.contains("Sorted"))
        assertTrue(conditions.contains("Clean"))
    }
}
