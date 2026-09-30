package com.sahitol.collector.domain.locale

/**
 * Numeral display preference (R-UX-01 / AT-051).
 * Allows collectors to view figures in standard Latin/English digits (1, 2, 3)
 * or authentic Devanagari numerals (१, २, ३).
 */
enum class NumeralPreference(val code: String, val displayNameEn: String, val displayNameHi: String, val displayNameMr: String) {
    LATIN("LATIN", "English Digits (1, 2, 3)", "अंग्रेजी अंक (1, 2, 3)", "इंग्रजी अंक (1, 2, 3)"),
    DEVANAGARI("DEVANAGARI", "Devanagari Numerals (१, २, ३)", "देवनागरी अंक (१, २, ३)", "देवनागरी अंक (१, २, ३)");

    companion object {
        private val LATIN_TO_DEVANAGARI = mapOf(
            '0' to '०',
            '1' to '१',
            '2' to '२',
            '3' to '३',
            '4' to '४',
            '5' to '५',
            '6' to '६',
            '7' to '७',
            '8' to '८',
            '9' to '९'
        )

        fun fromCode(code: String?): NumeralPreference {
            return entries.find { it.code.equals(code, ignoreCase = true) } ?: LATIN
        }

        fun applyPreference(input: String, preference: NumeralPreference): String {
            if (preference == LATIN) return input
            val sb = java.lang.StringBuilder(input.length)
            for (ch in input) {
                sb.append(LATIN_TO_DEVANAGARI[ch] ?: ch)
            }
            return sb.toString()
        }
    }
}
