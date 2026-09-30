package com.sahitol.collector.domain.locale

import java.text.DecimalFormat
import java.text.DecimalFormatSymbols
import java.util.Locale

/**
 * LocaleFormatter provides locale-aware formatting for currency (Indian Rupees and paise),
 * mass (grams and kilograms), rates, and screen-reader accessibility announcements.
 *
 * Adheres strictly to non-negotiable constraints:
 * - Integer paise arithmetic with zero lost precision (1 paise, 50 paise, ₹10.50, ₹101.05).
 * - Indian number grouping (thousands, lakhs, crores: ₹1,50,000).
 * - Support for explicit NumeralPreference (LATIN digits 0-9 vs DEVANAGARI numerals ०-९).
 * - Screen-reader announcements formatted as: label + value + unit + status.
 */
object LocaleFormatter {

    /**
     * Formats an integer using Indian numbering format (1,00,000 instead of 100,000).
     */
    fun formatIndianNumber(value: Long, preference: NumeralPreference = NumeralPreference.LATIN): String {
        val isNegative = value < 0
        val absVal = if (isNegative) -value else value

        val s = absVal.toString()
        val result = if (s.length <= 3) {
            s
        } else {
            val lastThree = s.takeLast(3)
            val rest = s.dropLast(3)
            val sb = StringBuilder()
            var count = 0
            for (i in rest.length - 1 downTo 0) {
                sb.append(rest[i])
                count++
                if (count == 2 && i != 0) {
                    sb.append(',')
                    count = 0
                }
            }
            sb.reverse().toString() + "," + lastThree
        }

        val formatted = if (isNegative) "-$result" else result
        return NumeralPreference.applyPreference(formatted, preference)
    }

    /**
     * Formats integer paise into Indian Rupee representation.
     * Preserves exact paise without silent rounding.
     * Examples:
     * - 1 paise -> ₹0.01
     * - 50 paise -> ₹0.50
     * - 1050 paise -> ₹10.50
     * - 10105 paise -> ₹101.05
     * - 15000000 paise -> ₹1,50,000
     */
    fun formatPaise(
        paise: Long,
        lang: String = "hi",
        preference: NumeralPreference = NumeralPreference.LATIN,
        includeSymbol: Boolean = true
    ): String {
        val isNegative = paise < 0
        val absPaise = if (isNegative) -paise else paise

        val rupees = absPaise / 100
        val remainderPaise = absPaise % 100

        val rupeePart = formatIndianNumber(rupees, NumeralPreference.LATIN)
        val text = if (remainderPaise == 0L) {
            rupeePart
        } else {
            val paisePart = if (remainderPaise < 10) "0$remainderPaise" else remainderPaise.toString()
            "$rupeePart.$paisePart"
        }

        val prefix = if (isNegative) "-" else ""
        val symbol = if (includeSymbol) "₹" else ""
        val combined = "$prefix$symbol$text"

        return NumeralPreference.applyPreference(combined, preference)
    }

    /**
     * Formats integer grams into locale-appropriate weight representation (g or kg).
     * Examples:
     * - 250 g -> 250 g / 250 ग्राम / 250 ग्रॅम
     * - 1000 g -> 1 kg / 1 किग्रा / 1 किलो
     * - 1250 g -> 1.25 kg
     * - 2500 g -> 2.50 kg
     */
    fun formatGrams(
        grams: Long,
        lang: String = "hi",
        preference: NumeralPreference = NumeralPreference.LATIN
    ): String {
        val isNegative = grams < 0
        val absGrams = if (isNegative) -grams else grams

        val unit = when (lang) {
            "hi" -> if (absGrams < 1000) "ग्राम" else "किग्रा"
            "mr" -> if (absGrams < 1000) "ग्रॅम" else "किलो"
            else -> if (absGrams < 1000) "g" else "kg"
        }

        val valueStr = if (absGrams < 1000) {
            formatIndianNumber(absGrams, NumeralPreference.LATIN)
        } else {
            val kg = absGrams / 1000
            val remGrams = absGrams % 1000
            if (remGrams == 0L) {
                formatIndianNumber(kg, NumeralPreference.LATIN)
            } else {
                // Trim trailing zeros in grams decimal (e.g. 250 -> 2.25, 500 -> 2.5)
                val kgFormatted = formatIndianNumber(kg, NumeralPreference.LATIN)
                val fraction = String.format(Locale.US, "%03d", remGrams).trimEnd('0')
                "$kgFormatted.$fraction"
            }
        }

        val prefix = if (isNegative) "-" else ""
        val formatted = "$prefix$valueStr $unit"
        return NumeralPreference.applyPreference(formatted, preference)
    }

    /**
     * Formats a rate in paise per kg.
     * Example: 15000 paise/kg -> ₹150 / kg (En), ₹150 / किग्रा (Hi), ₹150 / किलो (Mr).
     */
    fun formatRate(
        paisePerKg: Long,
        lang: String = "hi",
        preference: NumeralPreference = NumeralPreference.LATIN
    ): String {
        val formattedAmount = formatPaise(paisePerKg, lang, preference)
        val perUnit = when (lang) {
            "hi" -> "प्रति किग्रा"
            "mr" -> "प्रति किलो"
            else -> "/ kg"
        }
        return "$formattedAmount $perUnit"
    }

    /**
     * Formats a rate range.
     * Example: ₹120 – ₹180 / kg.
     */
    fun formatRange(
        minPaise: Long,
        maxPaise: Long,
        lang: String = "hi",
        preference: NumeralPreference = NumeralPreference.LATIN
    ): String {
        val minStr = formatPaise(minPaise, lang, preference)
        val maxStr = formatPaise(maxPaise, lang, preference)
        val perUnit = when (lang) {
            "hi" -> "प्रति किग्रा"
            "mr" -> "प्रति किलो"
            else -> "/ kg"
        }
        return "$minStr – $maxStr $perUnit"
    }

    /**
     * Formats accessibility screen-reader content description adhering to:
     * "Screen-reader content reads label + value + unit + status" (14_TRANSLATION_AUDIO_AUDIT.md).
     */
    fun formatScreenReader(
        label: String,
        value: String,
        unit: String,
        status: String
    ): String {
        val parts = listOfNotNull(
            label.takeIf { it.isNotBlank() },
            value.takeIf { it.isNotBlank() },
            unit.takeIf { it.isNotBlank() },
            status.takeIf { it.isNotBlank() }
        )
        return parts.joinToString(separator = ", ")
    }
}
