package com.sahitol.collector.domain.audio

/**
 * AudioGrammar implements the dynamic audio queue composition grammar conforming to
 * docs/14_TRANSLATION_AUDIO_AUDIT.md and R-LANG-02:
 *
 * "Define speakMoney(paise), speakWeight(grams), speakRate(paisePerKg),
 *  speakRange(low, high, unit) and speakStatus(key, args) as grammar outputs to clip queues.
 *  Dynamic values use an explicitly tested grammar, not concatenated English digit names.
 *  Build and review localized clips/rules for 0–99 (including irregular number names),
 *  hundreds, thousands, lakh/crore if supported by app bounds; currencies rupee/paise,
 *  decimal amounts, gram/kilogram, 'per kilogram', low-to-high range, plus/minus and
 *  unknown/insufficient values. Handle plural/word order separately for Hindi and Marathi."
 */
object AudioGrammar {

    private const val MAX_SUPPORTED_PAISE = 10_000_000_000_00L // 100 crore rupees

    /**
     * Decomposes any integer up to 100 crore into localized clip IDs using Indian numbering rules.
     */
    fun decomposeInteger(value: Long, lang: String = "hi"): List<String> {
        val l = if (lang == "mr") "mr" else "hi"
        if (value == 0L) return listOf("${l}_num_0")
        if (value < 0L) return listOf("${l}_unit_negative") + decomposeInteger(-value, lang)

        val clips = mutableListOf<String>()
        var rem = value

        // 1. Crores (1,00,00,000)
        val crores = rem / 10_000_000L
        if (crores > 0) {
            clips.addAll(decomposeSubHundred(crores, l))
            clips.add("${l}_scale_crore")
            rem %= 10_000_000L
        }

        // 2. Lakhs (1,00,000)
        val lakhs = rem / 100_000L
        if (lakhs > 0) {
            clips.addAll(decomposeSubHundred(lakhs, l))
            clips.add("${l}_scale_lakh")
            rem %= 100_000L
        }

        // 3. Thousands (1,000)
        val thousands = rem / 1_000L
        if (thousands > 0) {
            clips.addAll(decomposeSubHundred(thousands, l))
            clips.add("${l}_scale_thousand")
            rem %= 1_000L
        }

        // 4. Hundreds (100)
        val hundreds = rem / 100L
        if (hundreds > 0) {
            clips.addAll(decomposeSubHundred(hundreds, l))
            clips.add("${l}_scale_hundred")
            rem %= 100L
        }

        // 5. Remainder 1-99
        if (rem > 0) {
            clips.add("${l}_num_$rem")
        }

        return clips
    }

    private fun decomposeSubHundred(valBelowHundred: Long, l: String): List<String> {
        return if (valBelowHundred in 1..99) {
            listOf("${l}_num_$valBelowHundred")
        } else {
            decomposeInteger(valBelowHundred, l)
        }
    }

    /**
     * Spoken money grammar conforming to docs/14_TRANSLATION_AUDIO_AUDIT.md:
     * - Preserves exact paise (1 paise, 50 paise, ₹10.50, ₹101.05, ₹1,50,000)
     * - Handles pluralization (rupee vs rupees, paise)
     * - Handles negative net income
     */
    fun speakMoney(paise: Long?, lang: String = "hi"): List<String> {
        val l = if (lang == "mr") "mr" else "hi"
        if (paise == null) return listOf("${l}_unit_unknown")
        if (paise > MAX_SUPPORTED_PAISE) return listOf("${l}_unit_unknown")

        if (paise == 0L) {
            return listOf("${l}_num_0", "${l}_unit_rupee")
        }

        val clips = mutableListOf<String>()
        val isNegative = paise < 0
        if (isNegative) {
            clips.add("${l}_unit_negative")
        }

        val absPaise = if (isNegative) -paise else paise
        val rupees = absPaise / 100L
        val remPaise = absPaise % 100L

        if (rupees > 0) {
            clips.addAll(decomposeInteger(rupees, l))
            clips.add(if (rupees == 1L) "${l}_unit_rupee" else "${l}_unit_rupees")
        }

        if (remPaise > 0) {
            clips.add("${l}_num_$remPaise")
            clips.add("${l}_unit_paise")
        }

        return clips
    }

    /**
     * Spoken mass grammar:
     * - 250g -> 250 grams
     * - 1000g -> 1 kilogram
     * - 1250g -> 1 point 25 kilograms
     * - 2500g -> 2 point 5 kilograms
     */
    fun speakWeight(grams: Long?, lang: String = "hi"): List<String> {
        val l = if (lang == "mr") "mr" else "hi"
        if (grams == null) return listOf("${l}_unit_unknown")
        if (grams == 0L) return listOf("${l}_num_0", "${l}_unit_kg")

        val clips = mutableListOf<String>()
        val isNegative = grams < 0
        if (isNegative) {
            clips.add("${l}_unit_negative")
        }

        val absGrams = if (isNegative) -grams else grams

        if (absGrams < 1000L) {
            clips.addAll(decomposeInteger(absGrams, l))
            clips.add("${l}_unit_gram")
        } else {
            val kg = absGrams / 1000L
            val rem = absGrams % 1000L

            clips.addAll(decomposeInteger(kg, l))
            if (rem > 0) {
                clips.add("${l}_unit_point")
                // Format fraction (e.g. 250g -> 25, 500g -> 5, 50g -> 05)
                if (rem % 100L == 0L) {
                    val dec = rem / 100L
                    clips.add("${l}_num_$dec")
                } else if (rem % 10L == 0L) {
                    val dec = rem / 10L
                    clips.add("${l}_num_$dec")
                } else {
                    clips.addAll(decomposeInteger(rem, l))
                }
            }
            clips.add("${l}_unit_kg")
        }

        return clips
    }

    /**
     * Spoken rate grammar:
     * e.g. 15000 paise/kg -> ₹150 / kg
     */
    fun speakRate(paisePerKg: Long?, lang: String = "hi"): List<String> {
        val l = if (lang == "mr") "mr" else "hi"
        if (paisePerKg == null) return listOf("${l}_unit_unknown")

        val moneyClips = speakMoney(paisePerKg, l)
        return moneyClips + listOf("${l}_unit_per_kg")
    }

    /**
     * Spoken rate range grammar:
     * e.g. 12000 to 18000 paise/kg -> ₹120 to ₹180 / kg
     */
    fun speakRange(lowPaise: Long?, highPaise: Long?, lang: String = "hi"): List<String> {
        val l = if (lang == "mr") "mr" else "hi"
        if (lowPaise == null || highPaise == null) return listOf("${l}_unit_unknown")

        val lowRupees = lowPaise / 100L
        val highRupees = highPaise / 100L

        val clips = mutableListOf<String>()
        clips.addAll(decomposeInteger(lowRupees, l))
        clips.add("${l}_unit_to")
        clips.addAll(decomposeInteger(highRupees, l))
        clips.add("${l}_unit_rupees")
        clips.add("${l}_unit_per_kg")

        return clips
    }

    /**
     * Spoken status grammar:
     */
    fun speakStatus(statusKey: String, lang: String = "hi"): List<String> {
        val l = if (lang == "mr") "mr" else "hi"
        val normalized = statusKey.uppercase()
        val clipKey = when (normalized) {
            "SAVED_LOCALLY", "STATUS_SAVED_LOCALLY" -> "status_saved_locally"
            "SYNCED", "STATUS_SYNCED" -> "status_synced"
            "CONFIRMED", "STATUS_CONFIRMED" -> "status_confirmed"
            "PAID", "STATUS_PAID" -> "status_paid"
            "NON_EPR", "NON_EPR_DISCLAIMER" -> "non_epr_disclaimer"
            else -> return listOf("${l}_unit_unknown")
        }
        return listOf("${l}_$clipKey")
    }

    /**
     * Spoken safety card guidance script clip ID:
     */
    fun speakSafety(safetyCardId: String, lang: String = "hi"): List<String> {
        val l = if (lang == "mr") "mr" else "hi"
        val cid = safetyCardId.lowercase().replace("-", "_")
        return listOf("${l}_safety_$cid")
    }
}
