package com.sahitol.collector.data.session

import android.content.Context
import android.content.SharedPreferences
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

import com.sahitol.collector.domain.locale.NumeralPreference

data class CollectorSession(
    val accountId: String,
    val phone: String?,
    val alias: String,
    val isDemo: Boolean,
    val language: String,
    val isLoggedIn: Boolean,
    val numeralPreference: NumeralPreference = NumeralPreference.LATIN
) {
    val maskedPhone: String
        get() {
            if (phone == null || phone.length < 4) return "—"
            return "******" + phone.takeLast(4)
        }
}

class SessionManager(private val prefs: SharedPreferences) {
    constructor(context: Context) : this(context.getSharedPreferences("sahitol_session", Context.MODE_PRIVATE))

    private val _session = MutableStateFlow(loadSession())
    val session: StateFlow<CollectorSession> = _session.asStateFlow()

    private fun loadSession(): CollectorSession {
        val isLoggedIn = prefs.getBoolean(KEY_IS_LOGGED_IN, false)
        val isDemo = prefs.getBoolean(KEY_IS_DEMO, false)
        val phone = prefs.getString(KEY_PHONE, null)
        val accountId = prefs.getString(KEY_ACCOUNT_ID, null) ?: if (isDemo) "col_demo_santosh" else "col_live_default"
        val alias = prefs.getString(KEY_ALIAS, null) ?: if (isDemo) "संतोष यादव (Santosh Demo)" else "रमेश कुमार (Ramesh Kumar)"
        val language = prefs.getString(KEY_LANGUAGE, "hi") ?: "hi"
        val numeralCode = prefs.getString(KEY_NUMERAL_PREF, "LATIN")
        val numeralPref = NumeralPreference.fromCode(numeralCode)

        return CollectorSession(
            accountId = accountId,
            phone = phone,
            alias = alias,
            isDemo = isDemo,
            language = language,
            isLoggedIn = isLoggedIn,
            numeralPreference = numeralPref
        )
    }

    fun setLanguage(lang: String) {
        prefs.edit().putString(KEY_LANGUAGE, lang).apply()
        _session.value = _session.value.copy(language = lang)
    }

    fun setNumeralPreference(pref: NumeralPreference) {
        prefs.edit().putString(KEY_NUMERAL_PREF, pref.code).apply()
        _session.value = _session.value.copy(numeralPreference = pref)
    }

    fun loginDemo(alias: String = "संतोष यादव (Santosh Demo)") {
        val accountId = "col_demo_santosh"
        val phone = "9876543210"
        prefs.edit()
            .putBoolean(KEY_IS_LOGGED_IN, true)
            .putBoolean(KEY_IS_DEMO, true)
            .putString(KEY_ACCOUNT_ID, accountId)
            .putString(KEY_PHONE, phone)
            .putString(KEY_ALIAS, alias)
            .apply()

        _session.value = CollectorSession(
            accountId = accountId,
            phone = phone,
            alias = alias,
            isDemo = true,
            language = _session.value.language,
            isLoggedIn = true,
            numeralPreference = _session.value.numeralPreference
        )
    }

    fun login(phone: String, alias: String = "रमेश कुमार (Ramesh Kumar)") {
        val cleanPhone = phone.filter { it.isDigit() }.takeLast(10)
        val accountId = "col_live_${cleanPhone.takeLast(4)}"
        prefs.edit()
            .putBoolean(KEY_IS_LOGGED_IN, true)
            .putBoolean(KEY_IS_DEMO, false)
            .putString(KEY_ACCOUNT_ID, accountId)
            .putString(KEY_PHONE, cleanPhone)
            .putString(KEY_ALIAS, alias)
            .apply()

        _session.value = CollectorSession(
            accountId = accountId,
            phone = cleanPhone,
            alias = alias,
            isDemo = false,
            language = _session.value.language,
            isLoggedIn = true,
            numeralPreference = _session.value.numeralPreference
        )
    }

    /**
     * Safe logout contract (R-AUTH-03):
     * Session auth token and logged-in state are cleared,
     * but offline Room SQLite rows, drafts, and outbox queues are preserved!
     */
    fun logoutPreservingData() {
        prefs.edit()
            .putBoolean(KEY_IS_LOGGED_IN, false)
            .apply()

        _session.value = _session.value.copy(isLoggedIn = false)
    }

    companion object {
        private const val KEY_IS_LOGGED_IN = "is_logged_in"
        private const val KEY_IS_DEMO = "is_demo"
        private const val KEY_ACCOUNT_ID = "account_id"
        private const val KEY_PHONE = "phone"
        private const val KEY_ALIAS = "alias"
        private const val KEY_LANGUAGE = "language"
        private const val KEY_NUMERAL_PREF = "numeral_preference"
    }
}
