package com.sahitol.collector.domain.safety

import com.sahitol.collector.domain.model.MaterialCategory

enum class HazardLevel {
    MODERATE,
    HIGH,
    CRITICAL
}

data class SafetyCardLocale(
    val title: String,
    val subtitle: String,
    val hazardWarning: String,
    val safeHandlingInstruction: String,
    val prohibitedAction: String,
    val audioScript: String
)

data class SafetyProhibition(
    val key: String,
    val enLabel: String,
    val hiLabel: String,
    val mrLabel: String,
    val iconName: String
)

data class SafetyStep(
    val stepNumber: Int,
    val enTitle: String,
    val hiTitle: String,
    val mrTitle: String,
    val enDesc: String,
    val hiDesc: String,
    val mrDesc: String
)

data class SafetyCard(
    val id: String,
    val guideId: String,
    val materialIds: List<String>,
    val category: MaterialCategory,
    val hazardLevel: HazardLevel,
    val hazardType: String,
    val references: List<String>,
    val audioKey: String,
    val locales: Map<String, SafetyCardLocale>,
    val prohibitions: List<SafetyProhibition>,
    val steps: List<SafetyStep>
) {
    fun localized(lang: String): SafetyCardLocale {
        val l = if (lang in listOf("hi", "mr", "en")) lang else "en"
        return locales[l] ?: locales["en"] ?: locales.values.first()
    }
}
