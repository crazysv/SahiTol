package com.sahitol.collector.domain.model

enum class MaterialCategory(
    val code: String,
    val displayNameEn: String,
    val displayNameHi: String,
    val displayNameMr: String,
    val regulatoryRoute: String,
    val iconName: String = "category"
) {
    CRT_MONITOR("CRT", "CRT Monitor", "सीआरटी मॉनिटर", "सीआरटी मॉनिटर", "E_WASTE_HAZARDOUS", "tv"),
    LCD_MONITOR("LCD", "LCD Screen", "एलसीडी स्क्रीन", "एलसीडी स्क्रीन", "E_WASTE", "monitor"),
    PCB("PCB", "Printed Circuit Board", "सर्किट बोर्ड (पीसीबी)", "सर्किट बोर्ड (पीसीबी)", "E_WASTE", "developer_board"),
    COPPER_CABLE("CABLE", "Copper Cable / Wire", "तांबे की तार (केबल)", "तांब्याची वायर (केबल)", "E_WASTE", "power"),
    BATTERY_LI_ION("BATTERY", "Lithium / Lead Battery", "बैटरी (लिथियम/लेड)", "बॅटरी (लिथियम/लेड)", "BATTERY_RULES", "battery_charging_full"),
    ELECTRIC_MOTOR("MOTOR", "Electric Motor", "इलेक्ट्रिक मोटर", "इलेक्ट्रिक मोटर", "E_WASTE", "settings_input_component"),
    RIGID_PLASTIC("PLASTICS", "Rigid E-Plastics", "प्लास्टिक (कठोर)", "प्लॅस्टिक (कठोर)", "E_WASTE", "category"),
    MIXED_EWASTE("MIXED", "Mixed Scrap", "मिश्रित ई-कचरा", "मिश्रित ई-कचरा", "E_WASTE", "devices"),
    OTHER("OTHER", "Unknown / Other", "अज्ञात / अन्य", "अज्ञात / इतर", "PENDING_CLASSIFICATION", "help");

    fun getDisplayName(lang: String): String = when (lang) {
        "hi" -> displayNameHi
        "mr" -> displayNameMr
        else -> displayNameEn
    }

    companion object {
        fun fromCode(code: String): MaterialCategory {
            return entries.find { it.code.equals(code, ignoreCase = true) } ?: OTHER
        }

        fun fromModelCode(modelCode: String?): MaterialCategory {
            if (modelCode.isNullOrBlank()) return OTHER
            return when (modelCode.uppercase()) {
                "MAT-BAT-01", "MAT-BAT-02", "BATTERY" -> BATTERY_LI_ION
                "MAT-CAB-01", "CABLE" -> COPPER_CABLE
                "MAT-CRT-01", "CRT" -> CRT_MONITOR
                "MAT-LCD-01", "LCD" -> LCD_MONITOR
                "MAT-MET-01", "MAT-MIX-01", "MIXED" -> MIXED_EWASTE
                "MAT-MOT-01", "MOTOR" -> ELECTRIC_MOTOR
                "MAT-PCB-01", "MAT-PCB-02", "PCB" -> PCB
                "MAT-PLA-01", "PLASTICS" -> RIGID_PLASTIC
                else -> fromCode(modelCode)
            }
        }
    }
}

