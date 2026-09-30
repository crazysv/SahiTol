package com.sahitol.collector.domain.locale

import android.content.Context
import com.sahitol.collector.domain.model.MaterialCategory
import org.json.JSONArray
import java.io.InputStreamReader

/**
 * Multilingual Colloquial Scrap Material Aliases (R-LANG-01, T010, T036).
 * Provides colloquial Hindi, Marathi, and English aliases used by informal collectors
 * in field scrap yards (e.g. 'हरा पत्ता' for PCB, 'गाड़ी की बैटरी' for Lead-Acid, 'तांबा तार' for Cables).
 */
object MaterialAliases {

    data class MaterialAlias(
        val materialId: String,
        val category: MaterialCategory,
        val language: String,
        val localTerm: String,
        val normalizedTerm: String
    )

    // Curated core colloquial dictionary for instant, zero-I/O offline resolution
    private val BUILTIN_ALIASES = listOf(
        // PCB
        MaterialAlias("MAT-PCB-01", MaterialCategory.PCB, "hi", "मदरबोर्ड", "मदरबोर्ड"),
        MaterialAlias("MAT-PCB-01", MaterialCategory.PCB, "hi", "हरा पत्ता", "हरा पत्ता"),
        MaterialAlias("MAT-PCB-01", MaterialCategory.PCB, "hi", "कंप्यूटर सर्किट बोर्ड", "कंप्यूटर सर्किट बोर्ड"),
        MaterialAlias("MAT-PCB-01", MaterialCategory.PCB, "hi", "पुर्जा पत्ता", "पुर्जा पत्ता"),
        MaterialAlias("MAT-PCB-01", MaterialCategory.PCB, "mr", "मदरबोर्ड", "मदरबोर्ड"),
        MaterialAlias("MAT-PCB-01", MaterialCategory.PCB, "mr", "हिरवा बोर्ड", "हिरवा बोर्ड"),
        MaterialAlias("MAT-PCB-01", MaterialCategory.PCB, "mr", "कॉम्प्युटर सर्किट बोर्ड", "कॉम्प्युटर सर्किट बोर्ड"),
        MaterialAlias("MAT-PCB-01", MaterialCategory.PCB, "en", "Motherboard / Server PCB", "motherboard server pcb"),
        MaterialAlias("MAT-PCB-01", MaterialCategory.PCB, "en", "Green Board", "green board"),

        // Copper Cable
        MaterialAlias("MAT-CAB-01", MaterialCategory.COPPER_CABLE, "hi", "तांबा तार", "तांबा तार"),
        MaterialAlias("MAT-CAB-01", MaterialCategory.COPPER_CABLE, "hi", "बिजली की तार", "बिजली की तार"),
        MaterialAlias("MAT-CAB-01", MaterialCategory.COPPER_CABLE, "hi", "केबल", "केबल"),
        MaterialAlias("MAT-CAB-01", MaterialCategory.COPPER_CABLE, "mr", "तांब्याची वायर", "तांब्याची वायर"),
        MaterialAlias("MAT-CAB-01", MaterialCategory.COPPER_CABLE, "mr", "विजेची वायर", "विजेची वायर"),
        MaterialAlias("MAT-CAB-01", MaterialCategory.COPPER_CABLE, "mr", "केबल", "केबल"),
        MaterialAlias("MAT-CAB-01", MaterialCategory.COPPER_CABLE, "en", "Copper Cable / Wire", "copper cable wire"),

        // Battery
        MaterialAlias("MAT-BAT-01", MaterialCategory.BATTERY_LI_ION, "hi", "गाड़ी की बैटरी", "गाड़ी की बैटरी"),
        MaterialAlias("MAT-BAT-01", MaterialCategory.BATTERY_LI_ION, "hi", "इन्वर्टर बैटरी", "इन्वर्टर बैटरी"),
        MaterialAlias("MAT-BAT-01", MaterialCategory.BATTERY_LI_ION, "hi", "तेजाब वाली बैटरी", "तेजाब वाली बैटरी"),
        MaterialAlias("MAT-BAT-01", MaterialCategory.BATTERY_LI_ION, "mr", "गाडीची बॅटरी", "गाडीची बॅटरी"),
        MaterialAlias("MAT-BAT-01", MaterialCategory.BATTERY_LI_ION, "mr", "इन्व्हर्टर बॅटरी", "इन्व्हर्टर बॅटरी"),
        MaterialAlias("MAT-BAT-01", MaterialCategory.BATTERY_LI_ION, "mr", "मोठी बॅटरी", "मोठी बॅटरी"),
        MaterialAlias("MAT-BAT-01", MaterialCategory.BATTERY_LI_ION, "en", "Lead-Acid Battery", "lead acid battery"),
        MaterialAlias("MAT-BAT-02", MaterialCategory.BATTERY_LI_ION, "hi", "मोबाइल बैटरी", "मोबाइल बैटरी"),
        MaterialAlias("MAT-BAT-02", MaterialCategory.BATTERY_LI_ION, "hi", "लिथियम बैटरी", "लिथियम बैटरी"),
        MaterialAlias("MAT-BAT-02", MaterialCategory.BATTERY_LI_ION, "mr", "मोबाईल बॅटरी", "मोबाईल बॅटरी"),
        MaterialAlias("MAT-BAT-02", MaterialCategory.BATTERY_LI_ION, "mr", "लिथियम बॅटरी", "लिथियम बॅटरी"),
        MaterialAlias("MAT-BAT-02", MaterialCategory.BATTERY_LI_ION, "en", "Lithium-Ion Battery", "lithium ion battery"),

        // Electric Motor
        MaterialAlias("MAT-MOT-01", MaterialCategory.ELECTRIC_MOTOR, "hi", "मोटर", "मोटर"),
        MaterialAlias("MAT-MOT-01", MaterialCategory.ELECTRIC_MOTOR, "hi", "पंखे की मोटर", "पंखे की मोटर"),
        MaterialAlias("MAT-MOT-01", MaterialCategory.ELECTRIC_MOTOR, "hi", "कूलर मोटर", "कूलर मोटर"),
        MaterialAlias("MAT-MOT-01", MaterialCategory.ELECTRIC_MOTOR, "hi", "तांबा मोटर", "तांबा मोटर"),
        MaterialAlias("MAT-MOT-01", MaterialCategory.ELECTRIC_MOTOR, "mr", "मोटार", "मोटार"),
        MaterialAlias("MAT-MOT-01", MaterialCategory.ELECTRIC_MOTOR, "mr", "पंख्याची मोटार", "पंख्याची मोटार"),
        MaterialAlias("MAT-MOT-01", MaterialCategory.ELECTRIC_MOTOR, "mr", "कूलर मोटार", "कूलर मोटार"),
        MaterialAlias("MAT-MOT-01", MaterialCategory.ELECTRIC_MOTOR, "en", "Electric Motor", "electric motor"),

        // CRT Monitor
        MaterialAlias("MAT-CRT-01", MaterialCategory.CRT_MONITOR, "hi", "पुराना टीवी", "पुराना टीवी"),
        MaterialAlias("MAT-CRT-01", MaterialCategory.CRT_MONITOR, "hi", "कांच का टीवी", "कांच का टीवी"),
        MaterialAlias("MAT-CRT-01", MaterialCategory.CRT_MONITOR, "hi", "पिक्चर ट्यूब", "पिक्चर ट्यूब"),
        MaterialAlias("MAT-CRT-01", MaterialCategory.CRT_MONITOR, "mr", "जुना टीव्ही", "जुना टीव्ही"),
        MaterialAlias("MAT-CRT-01", MaterialCategory.CRT_MONITOR, "mr", "काचेचा टीव्ही", "काचेचा टीव्ही"),
        MaterialAlias("MAT-CRT-01", MaterialCategory.CRT_MONITOR, "mr", "पिक्चर ट्यूब", "पिक्चर ट्यूब"),
        MaterialAlias("MAT-CRT-01", MaterialCategory.CRT_MONITOR, "en", "CRT Monitor / TV Tube", "crt monitor tv tube"),

        // LCD Monitor
        MaterialAlias("MAT-LCD-01", MaterialCategory.LCD_MONITOR, "hi", "पतला टीवी", "पतला टीवी"),
        MaterialAlias("MAT-LCD-01", MaterialCategory.LCD_MONITOR, "hi", "एलसीडी स्क्रीन", "एलसीडी स्क्रीन"),
        MaterialAlias("MAT-LCD-01", MaterialCategory.LCD_MONITOR, "hi", "एलईडी पैनल", "एलईडी पैनल"),
        MaterialAlias("MAT-LCD-01", MaterialCategory.LCD_MONITOR, "mr", "पातळ टीव्ही", "पातळ टीव्ही"),
        MaterialAlias("MAT-LCD-01", MaterialCategory.LCD_MONITOR, "mr", "एलसीडी स्क्रीन", "एलसीडी स्क्रीन"),
        MaterialAlias("MAT-LCD-01", MaterialCategory.LCD_MONITOR, "mr", "एलईडी पॅनेल", "एलईडी पॅनेल"),
        MaterialAlias("MAT-LCD-01", MaterialCategory.LCD_MONITOR, "en", "LCD / LED Screen", "lcd led screen"),

        // Rigid Plastic
        MaterialAlias("MAT-PLA-01", MaterialCategory.RIGID_PLASTIC, "hi", "कठोर प्लास्टिक", "कठोर प्लास्टिक"),
        MaterialAlias("MAT-PLA-01", MaterialCategory.RIGID_PLASTIC, "hi", "टीवी बॉडी प्लास्टिक", "टीवी बॉडी प्लास्टिक"),
        MaterialAlias("MAT-PLA-01", MaterialCategory.RIGID_PLASTIC, "hi", "काला प्लास्टिक", "काला प्लास्टिक"),
        MaterialAlias("MAT-PLA-01", MaterialCategory.RIGID_PLASTIC, "mr", "कडक प्लॅस्टिक", "कडक प्लॅस्टिक"),
        MaterialAlias("MAT-PLA-01", MaterialCategory.RIGID_PLASTIC, "mr", "टीव्ही बॉडी", "टीव्ही बॉडी"),
        MaterialAlias("MAT-PLA-01", MaterialCategory.RIGID_PLASTIC, "en", "Rigid E-Plastic / ABS", "rigid e plastic abs"),

        // Mixed Scrap
        MaterialAlias("MAT-MIX-01", MaterialCategory.MIXED_EWASTE, "hi", "लोहा लक्कड़", "लोहा लक्कड़"),
        MaterialAlias("MAT-MIX-01", MaterialCategory.MIXED_EWASTE, "hi", "मिश्रित धातु", "मिश्रित धातु"),
        MaterialAlias("MAT-MIX-01", MaterialCategory.MIXED_EWASTE, "hi", "कबाड़ धातु", "कबाड़ धातु"),
        MaterialAlias("MAT-MIX-01", MaterialCategory.MIXED_EWASTE, "mr", "मिश्र धातू", "मिश्र धातू"),
        MaterialAlias("MAT-MIX-01", MaterialCategory.MIXED_EWASTE, "mr", "भंगार धातू", "भंगार धातू"),
        MaterialAlias("MAT-MIX-01", MaterialCategory.MIXED_EWASTE, "en", "Mixed Electronics Scrap", "mixed electronics scrap")
    )

    private var loadedAliases: List<MaterialAlias>? = null

    fun loadFromAssets(context: Context): List<MaterialAlias> {
        if (loadedAliases != null) return loadedAliases!!
        return try {
            val assetStream = context.assets.open("material_aliases.json")
            val jsonText = InputStreamReader(assetStream).use { it.readText() }
            val jsonArray = JSONArray(jsonText)
            val list = mutableListOf<MaterialAlias>()
            for (i in 0 until jsonArray.length()) {
                val obj = jsonArray.getJSONObject(i)
                val matId = obj.getString("material_id")
                val lang = obj.getString("language")
                val term = obj.getString("local_term")
                val norm = obj.optString("normalized_term", term.lowercase())
                val cat = mapMaterialIdToCategory(matId)
                list.add(MaterialAlias(matId, cat, lang, term, norm))
            }
            loadedAliases = list
            list
        } catch (e: Exception) {
            loadedAliases = BUILTIN_ALIASES
            BUILTIN_ALIASES
        }
    }

    fun getAllAliases(): List<MaterialAlias> = loadedAliases ?: BUILTIN_ALIASES

    fun getAliasesForCategory(category: MaterialCategory, lang: String = "hi"): List<String> {
        val all = getAllAliases()
        return all.filter { it.category == category && it.language.equals(lang, ignoreCase = true) }
            .map { it.localTerm }
            .distinct()
    }

    fun searchCategoryByColloquialTerm(term: String, lang: String? = null): MaterialCategory? {
        val clean = term.trim().lowercase()
        if (clean.isBlank()) return null

        val all = getAllAliases()
        val match = all.firstOrNull { alias ->
            val langMatch = lang == null || alias.language.equals(lang, ignoreCase = true)
            langMatch && (alias.normalizedTerm.contains(clean) || clean.contains(alias.normalizedTerm) || alias.localTerm.equals(clean, ignoreCase = true))
        }
        return match?.category
    }

    private fun mapMaterialIdToCategory(materialId: String): MaterialCategory {
        return when {
            materialId.startsWith("MAT-PCB") -> MaterialCategory.PCB
            materialId.startsWith("MAT-CAB") -> MaterialCategory.COPPER_CABLE
            materialId.startsWith("MAT-BAT") -> MaterialCategory.BATTERY_LI_ION
            materialId.startsWith("MAT-MOT") -> MaterialCategory.ELECTRIC_MOTOR
            materialId.startsWith("MAT-CRT") -> MaterialCategory.CRT_MONITOR
            materialId.startsWith("MAT-LCD") -> MaterialCategory.LCD_MONITOR
            materialId.startsWith("MAT-PLA") -> MaterialCategory.RIGID_PLASTIC
            materialId.startsWith("MAT-MET") || materialId.startsWith("MAT-MIX") -> MaterialCategory.MIXED_EWASTE
            else -> MaterialCategory.OTHER
        }
    }
}
