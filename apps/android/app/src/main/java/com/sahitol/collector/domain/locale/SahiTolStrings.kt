package com.sahitol.collector.domain.locale

import java.util.regex.Pattern

/**
 * Audit result report conforming to R-LANG-01 and AT-049:
 * "Unavailable translation is reported in audit, not hidden by English fallback."
 */
data class TranslationAuditResult(
    val totalKeys: Int,
    val missingHi: List<String>,
    val missingMr: List<String>,
    val placeholderMismatches: List<String>
) {
    val isPassed: Boolean
        get() = missingHi.isEmpty() && missingMr.isEmpty() && placeholderMismatches.isEmpty()
}

/**
 * Centralized string dictionary for SahiTol.
 * Allows programmatic access in Compose and domain layers with stable semantic keys,
 * verified parameter interpolation, and strict translation audit verification.
 */
object SahiTolStrings {

    private val STRINGS_EN = mapOf(
        // App & Identity
        "app_name" to "SahiTol",
        "tagline" to "Fair weight, transparent price, documented handover",
        "demo_mode_label" to "DEMO MODE — Test Data Only",
        "demo_subtext" to "Isolated partition. Does not record real commercial transactions.",

        // Language Selection
        "lang_select_title" to "Choose Language",
        "lang_en" to "English",
        "lang_hi" to "हिंदी (Hindi)",
        "lang_mr" to "मराठी (Marathi)",

        // Actions & Buttons
        "btn_continue" to "Continue",
        "btn_cancel" to "Cancel",
        "btn_confirm" to "Confirm",
        "btn_back" to "Back",
        "btn_retry" to "Retry",
        "btn_dismiss" to "Dismiss",
        "btn_save" to "Save",
        "btn_close" to "Close",
        "btn_delete" to "Delete",
        "btn_capture_photo" to "Capture Photo",
        "btn_save_draft" to "Save Draft",
        "btn_sync_now" to "Sync Now",

        // Four Immutable Status Invariants
        "status_saved_locally" to "Saved on phone",
        "status_saved_locally_desc" to "Stored in local phone memory. Not yet uploaded to server.",
        "status_synced" to "Synchronized",
        "status_synced_desc" to "Uploaded and safely stored on server.",
        "status_confirmed" to "Recycler Confirmed",
        "status_confirmed_desc" to "Registered recycler inspected weight and confirmed physical handover.",
        "status_paid" to "Payment Acknowledged",
        "status_paid_desc" to "Cash or UPI receipt acknowledged by counterparty. Not an automated bank settlement.",
        "non_epr_disclaimer" to "SahiTol Digital Handover Record is a verification of physical scrap receipt, not a statutory EPR certificate. Received mass does not prove recycling.",

        // Onboarding, Auth & Profile
        "auth_title" to "Collector Login",
        "auth_phone_label" to "Mobile Number",
        "auth_phone_hint" to "Enter 10-digit mobile number",
        "auth_pin_label" to "4-Digit PIN",
        "auth_pin_hint" to "Enter secret PIN",
        "auth_login_btn" to "Log In",
        "auth_demo_btn" to "Explore Demo Account (Santosh)",
        "auth_zero_pii" to "Zero-PII Zone: No Aadhaar or bank credentials required.",
        "auth_err_invalid_pin" to "Incorrect PIN. Please try again.",
        "auth_err_throttled" to "Too many attempts. Locked for %1\$d seconds.",
        "auth_logout_title" to "Safe Logout",
        "auth_logout_confirm" to "Log Out",
        "auth_logout_warning" to "You have %1\$d unsynchronized items. They will remain safely stored on this phone and will not be lost.",

        // Navigation & Home
        "nav_home" to "Home",
        "nav_lots" to "Scrap Lots",
        "nav_prices" to "Price Board",
        "nav_recyclers" to "Recyclers",
        "nav_ledger" to "Ledger & Dues",
        "nav_sync" to "Sync Centre",
        "nav_settings" to "Settings",
        "nav_safety" to "Safety Guides",
        "home_greeting" to "Welcome, %1\$s",
        "home_quick_add" to "Create Scrap Lot",
        "home_pending_sync" to "%1\$d records waiting to sync",
        "home_recent_lots" to "Recent Activity",
        "home_empty_lots" to "No scrap lots created yet. Tap '+' to create your first lot.",

        // Lot Creation & Editor
        "lot_editor_title" to "Scrap Lot Details",
        "lot_material_label" to "Scrap Material",
        "lot_weight_label" to "Weight",
        "lot_unit_kg" to "kg",
        "lot_unit_g" to "grams",
        "lot_unit_piece" to "pieces",
        "lot_condition_label" to "Condition",
        "lot_cond_intact" to "Intact / Working",
        "lot_cond_damaged" to "Damaged / Broken",
        "lot_cond_depopulated" to "Depopulated / Stripped",
        "lot_cond_burnt" to "Burnt / Charred",
        "lot_cond_leaking" to "Leaking / Corroded",
        "lot_photo_tap_to_capture" to "Take Photo of Scrap",
        "lot_photo_retake" to "Retake Photo",
        "lot_save_draft" to "Save on Phone",
        "lot_submit_action" to "Save & Continue",
        "lot_err_no_material" to "Please select a scrap material.",
        "lot_err_invalid_weight" to "Please enter a valid weight greater than zero.",
        "lot_warning_heavy_weight" to "Weight exceeds 500 kg. Marked for data quality review.",

        // AI Classifier & Advisory
        "classifier_analyzing" to "Analyzing scrap image with LiteRT on-device AI…",
        "classifier_high_confidence" to "AI Suggestion: %1\$s (%2\$d%% match)",
        "classifier_advisory_note" to "Advisory only. You decide the true material category.",
        "classifier_confirm_btn" to "Accept Suggestion",
        "classifier_change_btn" to "Select Manually",
        "classifier_abstain_warning" to "AI Not Confident (%1\$d%% match). Please choose material manually.",

        // Prices & Units
        "price_title" to "Market Scrap Prices",
        "price_indicative_notice" to "Indicative prices from public sources. Not binding price promises.",
        "price_per_kg" to "₹%1\$s / kg",
        "price_range_format" to "₹%1\$s – ₹%2\$s / kg",
        "price_confidence_high" to "High Confidence (%1\$d quotes)",
        "price_confidence_med" to "Moderate Confidence",
        "price_confidence_low" to "Low Data / Region Fallback",
        "price_insufficient_data" to "Insufficient Price Data",
        "price_add_observation" to "Report Market Rate",
        "price_obs_submitted" to "Price report submitted for moderation.",

        // Recycler Directory & Matching
        "recycler_dir_title" to "Authorized Recyclers",
        "recycler_distance" to "%1$.1f km away",
        "recycler_route_authorized" to "CPCB / SPCB Authorized",
        "recycler_route_battery" to "Battery Rules 2022 Registered",
        "recycler_battery_isolation" to "Hazardous batteries require dedicated isolated processing.",
        "recycler_request_quote" to "Request Quote",
        "recycler_offer_received" to "Offer: ₹%1\$s / kg",
        "recycler_offer_accept" to "Accept Offer",
        "recycler_offer_reject" to "Decline",
        "recycler_no_match" to "No authorized facility found for this scrap in your area.",

        // Handover, QR & Digital Record
        "handover_title" to "Scrap Handover & Receipt",
        "handover_qr_title" to "Show QR to Recycler",
        "handover_qr_desc" to "Recycler scans this code to confirm receipt on their device.",
        "handover_actual_weight" to "Measured Yard Weight",
        "handover_weight_diff" to "Weight difference: %1\$s",
        "handover_variance_warning" to "Weight discrepancy > 20%%. Please review before confirming.",
        "handover_dispute_reason" to "Reason for disagreement / dispute",
        "handover_btn_confirm" to "Accept Measured Terms",
        "handover_pdf_share" to "Download / Share Receipt PDF",
        "handover_public_seal" to "Cryptographic Hash: %1\$s",

        // Payments & Ledger
        "ledger_title" to "Earnings & Dues Ledger",
        "ledger_total_earned" to "Total Value",
        "ledger_acknowledged_paid" to "Cash Received",
        "ledger_dues_pending" to "Remaining Dues",
        "payment_record_cash" to "Record Cash Payment",
        "payment_upi_ref_optional" to "UPI Reference (Optional)",
        "payment_counterparty_ack" to "Counterparty has acknowledged cash receipt.",
        "payment_reversal_notice" to "This payment was reversed: %1\$s",
        "payment_empty_ledger" to "No transactions yet.",

        // Synchronization & Offline
        "sync_title" to "Sync Centre",
        "sync_pending_count" to "%1\$d operations queued on phone",
        "sync_all_synced" to "All records synchronized with server",
        "sync_syncing_progress" to "Synchronizing batch %1\$d of %2\$d…",
        "sync_btn_start" to "Sync Now",
        "sync_err_network" to "Offline. Waiting for internet connection.",
        "sync_err_conflict" to "Terms updated on server. Local draft refreshed.",
        "sync_safe_notice" to "All data stays safely stored on this phone in airplane mode.",

        // Safety Warnings
        "safety_title" to "Scrap Safety Instructions",
        "safety_crt_warning" to "CAUTION: CRT Glass Implosion & Toxic Phosphors. Do not break tube.",
        "safety_battery_warning" to "DANGER: Fire & Acid Burn Hazard. Keep terminals insulated. Do not crush.",
        "safety_pcb_warning" to "NOTICE: Toxic heavy metals. Do not burn or acid-wash in open air.",
        "safety_cable_warning" to "NOTICE: Copper cable burning is illegal under environmental rules.",

        // Economics & Preferences
        "econ_title" to "Illustrative Earnings Comparison",
        "econ_current_net" to "Current Informal Net",
        "econ_platform_net" to "SahiTol Platform Net",
        "econ_zero_fee" to "Zero Platform Fee for Collectors",
        "econ_disclaimer" to "Illustrative model based on desk research. Actual income varies with local yard rates.",
        "pref_numeral_title" to "Numeral Display Preference",
        "pref_numeral_latin" to "English Digits (1, 2, 3)",
        "pref_numeral_devanagari" to "Devanagari Numerals (१, २, ३)",
        "pref_language_title" to "App Language",

        // Accessibility & Screen Reader Labels
        "a11y_tap_to_hear" to "Tap to listen to audio guidance",
        "a11y_weight_readout" to "Weight: %1\$s, Material: %2\$s, Status: %3\$s",
        "a11y_price_readout" to "Price: %1\$s per kilogram, Confidence: %2\$s",
        "a11y_qr_code" to "Handover verification QR code for recycler scan"
    )

    private val STRINGS_HI = mapOf(
        // App & Identity
        "app_name" to "सही तोल",
        "tagline" to "सही वजन, पारदर्शी दाम, पक्की रसीद",
        "demo_mode_label" to "डेमो मोड — केवल परीक्षण डेटा",
        "demo_subtext" to "अलग पार्टीशन। कोई वास्तविक लेन-देन दर्ज नहीं होता।",

        // Language Selection
        "lang_select_title" to "भाषा चुनें",
        "lang_en" to "English",
        "lang_hi" to "हिंदी",
        "lang_mr" to "मराठी",

        // Actions & Buttons
        "btn_continue" to "आगे बढ़ें",
        "btn_cancel" to "रद्द करें",
        "btn_confirm" to "पुष्टि करें",
        "btn_back" to "पीछे जाएं",
        "btn_retry" to "पुनः प्रयास करें",
        "btn_dismiss" to "खारिज करें",
        "btn_save" to "सुरक्षित करें",
        "btn_close" to "बंद करें",
        "btn_delete" to "हटाएं",
        "btn_capture_photo" to "फोटो खींचें",
        "btn_save_draft" to "ड्राफ्ट सुरक्षित करें",
        "btn_sync_now" to "सिंक करें",

        // Four Immutable Status Invariants
        "status_saved_locally" to "फोन में सुरक्षित",
        "status_saved_locally_desc" to "फ़ोन की मेमोरी में सुरक्षित। अभी सर्वर पर नहीं भेजा गया।",
        "status_synced" to "सर्वर पर सिंक हुआ",
        "status_synced_desc" to "सर्वर पर अपलोड और सुरक्षित किया गया।",
        "status_confirmed" to "रिसाइकलर द्वारा पुष्टि",
        "status_confirmed_desc" to "पंजीकृत रिसाइकलर ने वजन जांच कर रसीद की पुष्टि की।",
        "status_paid" to "भुगतान स्वीकृत",
        "status_paid_desc" to "नकद या यूपीआई भुगतान दोनों पक्षों द्वारा स्वीकृत। बैंक निपटान नहीं।",
        "non_epr_disclaimer" to "सही तोल डिजिटल हैंडओवर रिकॉर्ड केवल कबाड़ प्राप्ति का प्रमाण है, यह कोई वैधानिक ईपीआर प्रमाण पत्र नहीं है। प्राप्त वजन रिसाइक्लिंग को सिद्ध नहीं करता।",

        // Onboarding, Auth & Profile
        "auth_title" to "कबाड़ी साथी लॉगिन",
        "auth_phone_label" to "मोबाइल नंबर",
        "auth_phone_hint" to "10 अंकों का मोबाइल नंबर दर्ज करें",
        "auth_pin_label" to "4 अंकों का सुरक्षा पिन",
        "auth_pin_hint" to "अपना गुप्त पिन दर्ज करें",
        "auth_login_btn" to "लॉगिन करें",
        "auth_demo_btn" to "डेमो खाता देखें (संतोष यादव)",
        "auth_zero_pii" to "गोपनीयता सुरक्षा: आधार या बैंक खाते की कोई जानकारी नहीं मांगी जाती।",
        "auth_err_invalid_pin" to "गलत पिन। कृपया पुनः प्रयास करें।",
        "auth_err_throttled" to "कई बार गलत प्रयास। %1\$d सेकंड के लिए लॉक किया गया।",
        "auth_logout_title" to "सुरक्षित लॉगआउट",
        "auth_logout_confirm" to "लॉगआउट करें",
        "auth_logout_warning" to "आपके पास %1\$d असिंक रिकॉर्ड हैं। वे इस फोन में सुरक्षित रहेंगे और हटेंगे नहीं।",

        // Navigation & Home
        "nav_home" to "होम",
        "nav_lots" to "कबाड़ लॉट",
        "nav_prices" to "बाजार भाव",
        "nav_recyclers" to "रिसाइकलर यार्ड",
        "nav_ledger" to "खाता बही",
        "nav_sync" to "सिंक केंद्र",
        "nav_settings" to "सेटिंग्स",
        "nav_safety" to "सुरक्षा निर्देश",
        "home_greeting" to "नमस्ते, %1\$s",
        "home_quick_add" to "नया कबाड़ जोड़ें",
        "home_pending_sync" to "%1\$d रिकॉर्ड सिंक होना बाकी",
        "home_recent_lots" to "हाल की गतिविधियां",
        "home_empty_lots" to "अभी कोई कबाड़ लॉट नहीं बना है। पहला लॉट जोड़ने के लिए '+' दबाएं।",

        // Lot Creation & Editor
        "lot_editor_title" to "कबाड़ लॉट विवरण",
        "lot_material_label" to "कबाड़ का प्रकार",
        "lot_weight_label" to "वजन",
        "lot_unit_kg" to "किग्रा",
        "lot_unit_g" to "ग्राम",
        "lot_unit_piece" to "नग (पीस)",
        "lot_condition_label" to "हालत / स्थिति",
        "lot_cond_intact" to "साबुत / सही सलामत",
        "lot_cond_damaged" to "टूटा-फूटा / क्षतिग्रस्त",
        "lot_cond_depopulated" to "पुर्जे निकाले हुए",
        "lot_cond_burnt" to "जला हुआ",
        "lot_cond_leaking" to "रिसाव / तेजाब जंग",
        "lot_photo_tap_to_capture" to "कबाड़ की फोटो खींचें",
        "lot_photo_retake" to "दोबारा फोटो लें",
        "lot_save_draft" to "फोन में सुरक्षित करें",
        "lot_submit_action" to "सुरक्षित कर आगे बढ़ें",
        "lot_err_no_material" to "कृपया कबाड़ का प्रकार चुनें।",
        "lot_err_invalid_weight" to "कृपया शून्य से अधिक मान्य वजन दर्ज करें।",
        "lot_warning_heavy_weight" to "वजन 500 किग्रा से अधिक है। गुणवत्ता समीक्षा हेतु चिन्हित किया गया।",

        // AI Classifier & Advisory
        "classifier_analyzing" to "ऑन-डिवाइस एआई द्वारा फोटो की पहचान की जा रही है…",
        "classifier_high_confidence" to "एआई सुझाव: %1\$s (%2\$d%% अनुमान)",
        "classifier_advisory_note" to "यह केवल सहायता सुझाव है। कबाड़ का सही प्रकार आप तय करें।",
        "classifier_confirm_btn" to "सुझाव स्वीकारें",
        "classifier_change_btn" to "स्वयं दूसरा चुनें",
        "classifier_abstain_warning" to "एआई स्पष्ट पहचान नहीं कर सका (%1\$d%% अनुमान)। कृपया स्वयं सामग्री चुनें।",

        // Prices & Units
        "price_title" to "मंडी भाव व दर",
        "price_indicative_notice" to "सार्वजनिक स्रोतों पर आधारित सांकेतिक भाव। कोई बाध्यकारी वादा नहीं।",
        "price_per_kg" to "₹%1\$s / किग्रा",
        "price_range_format" to "₹%1\$s – ₹%2\$s / किग्रा",
        "price_confidence_high" to "उच्च विश्वसनीयता (%1\$d भाव दर्ज)",
        "price_confidence_med" to "मध्यम विश्वसनीयता",
        "price_confidence_low" to "कम डेटा / क्षेत्रीय अनुमान",
        "price_insufficient_data" to "पर्याप्त भाव उपलब्ध नहीं",
        "price_add_observation" to "मंडी का नया भाव बताएं",
        "price_obs_submitted" to "भाव रिपोर्ट समीक्षा के लिए भेजा गया।",

        // Recycler Directory & Matching
        "recycler_dir_title" to "अधिकृत रिसाइकलर यार्ड",
        "recycler_distance" to "%1$.1f किमी दूर",
        "recycler_route_authorized" to "प्रदूषण नियंत्रण बोर्ड अधिकृत",
        "recycler_route_battery" to "बैटरी नियम 2022 पंजीकृत",
        "recycler_battery_isolation" to "खतरनाक बैटरी का अलग अधिकृत निपटान अनिवार्य है।",
        "recycler_request_quote" to "भाव मांगें",
        "recycler_offer_received" to "प्रस्ताव: ₹%1\$s / किग्रा",
        "recycler_offer_accept" to "प्रस्ताव स्वीकारें",
        "recycler_offer_reject" to "अस्वीकार करें",
        "recycler_no_match" to "आपके क्षेत्र में इस कबाड़ के लिए कोई अधिकृत यार्ड नहीं मिला।",

        // Handover, QR & Digital Record
        "handover_title" to "कबाड़ सुपुर्दगी व रसीद",
        "handover_qr_title" to "रिसाइकलर को क्यूआर दिखाएं",
        "handover_qr_desc" to "रिसाइकलर अपने फोन से इसे स्कैन कर रसीद की पुष्टि करेंगे।",
        "handover_actual_weight" to "यार्ड में तौला गया वजन",
        "handover_weight_diff" to "वजन में अंतर: %1\$s",
        "handover_variance_warning" to "वजन में 20%% से अधिक अंतर है। पुष्टि से पहले जांच लें।",
        "handover_dispute_reason" to "आपत्ति या विवाद का कारण",
        "handover_btn_confirm" to "नये वजन व शर्तों की पुष्टि करें",
        "handover_pdf_share" to "रसीद पीडीएफ डाउनलोड / शेयर करें",
        "handover_public_seal" to "डिजिटल सील हैश: %1\$s",

        // Payments & Ledger
        "ledger_title" to "कमाई व बकाया हिसाब",
        "ledger_total_earned" to "कुल कबाड़ मूल्य",
        "ledger_acknowledged_paid" to "प्राप्त नकद भुगतान",
        "ledger_dues_pending" to "बकाया रकम",
        "payment_record_cash" to "नकद भुगतान दर्ज करें",
        "payment_upi_ref_optional" to "यूपीआई संदर्भ नंबर (वैकल्पिक)",
        "payment_counterparty_ack" to "सामने वाले पक्ष ने नकद प्राप्ति की पुष्टि की है।",
        "payment_reversal_notice" to "यह भुगतान निरस्त किया गया: %1\$s",
        "payment_empty_ledger" to "अभी कोई लेन-देन नहीं है।",

        // Synchronization & Offline
        "sync_title" to "सिंक केंद्र",
        "sync_pending_count" to "फोन में %1\$d कार्य लंबित",
        "sync_all_synced" to "सभी रिकॉर्ड सर्वर पर सुरक्षित सिंक हैं",
        "sync_syncing_progress" to "सर्वर से सिंक हो रहा है (%1\$d / %2\$d)…",
        "sync_btn_start" to "अभी सिंक करें",
        "sync_err_network" to "ऑफलाइन। इंटरनेट का इंतजार है।",
        "sync_err_conflict" to "सर्वर पर शर्तें अपडेट हुईं। लोकल कॉपी अपडेट की गई।",
        "sync_safe_notice" to "हवाई मोड में भी सारा डेटा आपके फोन में पूरी तरह सुरक्षित रहता है।",

        // Safety Warnings
        "safety_title" to "कबाड़ सुरक्षा निर्देश",
        "safety_crt_warning" to "चेतावनी: सीआरटी कांच फटने का खतरा व जहरीला लेड/फॉस्फोरस। ट्यूब को न तोड़ें।",
        "safety_battery_warning" to "खतरा: आग और तेजाब से जलने का जोखिम। दोनों सिरों को अलग रखें। दबाएं नहीं।",
        "safety_pcb_warning" to "सावधानी: जहरीली धातुएं। खुले में आग न लगाएं और तेजाब से न धोएं।",
        "safety_cable_warning" to "सूचना: तार को जलाना कानूनन अपराध है। कटर से छीलें।",

        // Economics & Preferences
        "econ_title" to "अनुमानित कमाई तुलना",
        "econ_current_net" to "वर्तमान असंगठित कमाई",
        "econ_platform_net" to "सही तोल अनुमानित कमाई",
        "econ_zero_fee" to "कबाड़ी साथियों से कोई शुल्क नहीं (0%)",
        "econ_disclaimer" to "अनुसंधान पर आधारित सांकेतिक मॉडल। वास्तविक कमाई स्थानीय भाव पर निर्भर करती है।",
        "pref_numeral_title" to "संख्या प्रदर्शन प्राथमिकता",
        "pref_numeral_latin" to "अंग्रेजी अंक (1, 2, 3)",
        "pref_numeral_devanagari" to "देवनागरी अंक (१, २, ३)",
        "pref_language_title" to "ऐप की भाषा",

        // Accessibility & Screen Reader Labels
        "a11y_tap_to_hear" to "बोलकर सुनने के लिए टैप करें",
        "a11y_weight_readout" to "वजन: %1\$s, सामग्री: %2\$s, स्थिति: %3\$s",
        "a11y_price_readout" to "भाव: %1\$s प्रति किग्रा, विश्वसनीयता: %2\$s",
        "a11y_qr_code" to "रिसाइकलर स्कैन के लिए हैंडओवर क्यूआर कोड"
    )

    private val STRINGS_MR = mapOf(
        // App & Identity
        "app_name" to "सही तोल",
        "tagline" to "योग्य वजन, पारदर्शक भाव, पक्की पावती",
        "demo_mode_label" to "डेमो मोड — फक्त चाचणी डेटा",
        "demo_subtext" to "वेगळे पार्टीशन. कोणतेही प्रत्यक्ष आर्थिक व्यवहार नोंदवले जात नाहीत.",

        // Language Selection
        "lang_select_title" to "भाषा निवडा",
        "lang_en" to "English",
        "lang_hi" to "हिंदी",
        "lang_mr" to "मराठी",

        // Actions & Buttons
        "btn_continue" to "पुढे जा",
        "btn_cancel" to "रद्द करा",
        "btn_confirm" to "पुष्टी करा",
        "btn_back" to "मागे जा",
        "btn_retry" to "पुन्हा प्रयत्न करा",
        "btn_dismiss" to "बंद करा",
        "btn_save" to "जतन करा",
        "btn_close" to "बंद करा",
        "btn_delete" to "हटवा",
        "btn_capture_photo" to "फोटो काढा",
        "btn_save_draft" to "ड्राफ्ट जतन करा",
        "btn_sync_now" to "सिंक करा",

        // Four Immutable Status Invariants
        "status_saved_locally" to "फोनवर जतन केले",
        "status_saved_locally_desc" to "फोनच्या मेमरीमध्ये जतन केले. अद्याप सर्व्हरवर पाठवले नाही.",
        "status_synced" to "सर्व्हरवर सिंक केले",
        "status_synced_desc" to "सर्व्हरवर सुरक्षितपणे पाठवले गेले.",
        "status_confirmed" to "रिसायकलरद्वारे पुष्टी केली",
        "status_confirmed_desc" to "नोंदणीकृत रिसायकलरने वजन तपासून प्रत्यक्ष पावती निश्चित केली.",
        "status_paid" to "पैसे मिळाल्याची पोच",
        "status_paid_desc" to "दोन्ही पक्षांनी रोख किंवा यूपीआय पावती स्वीकारली. हे बँक सेटलमेंट नाही.",
        "non_epr_disclaimer" to "सही तोल डिजिटल हँडओव्हर रेकॉर्ड हा केवळ भंगार मिळाल्याचा पुरावा आहे, हा कोणताही अधिकृत ईपीआर दाखला नाही. मिळालेले वजन पुनर्प्रक्रिया झाल्याचे सिद्ध करत नाही.",

        // Onboarding, Auth & Profile
        "auth_title" to "कबाडी साथी लॉगिन",
        "auth_phone_label" to "मोबाईल नंबर",
        "auth_phone_hint" to "10 अंकी मोबाईल नंबर टाका",
        "auth_pin_label" to "4 अंकी सुरक्षा पिन",
        "auth_pin_hint" to "तुमचा गुप्त पिन टाका",
        "auth_login_btn" to "लॉगिन करा",
        "auth_demo_btn" to "डेमो खाते पहा (संतोष यादव)",
        "auth_zero_pii" to "गोपनीयता सुरक्षा: आधार किंवा बँक खात्याची माहिती आवश्यक नाही.",
        "auth_err_invalid_pin" to "चुकीचा पिन. कृपया पुन्हा प्रयत्न करा.",
        "auth_err_throttled" to "वारंवार चुकीचे प्रयत्न. %1\$d सेकंदांसाठी लॉक केले गेले.",
        "auth_logout_title" to "सुरक्षित लॉगआउट",
        "auth_logout_confirm" to "लॉगआउट करा",
        "auth_logout_warning" to "तुमच्याकडे %1\$d अनसिंक नोंदी आहेत. त्या फोनवर सुरक्षित राहतील आणि नष्ट होणार नाहीत.",

        // Navigation & Home
        "nav_home" to "मुख्यपृष्ठ",
        "nav_lots" to "भंगार लॉट",
        "nav_prices" to "बाजार भाव",
        "nav_recyclers" to "रिसायकलर यार्ड",
        "nav_ledger" to "खातावही",
        "nav_sync" to "सिंक केंद्र",
        "nav_settings" to "सेटिंग्ज",
        "nav_safety" to "सुरक्षा मार्गदर्शक",
        "home_greeting" to "नमस्कार, %1\$s",
        "home_quick_add" to "नवीन भंगार जोडा",
        "home_pending_sync" to "%1\$d नोंदी सिंक होणे बाकी",
        "home_recent_lots" to "अलीकडील व्यवहार",
        "home_empty_lots" to "अद्याप कोणताही भंगार लॉट नाही. नवीन लॉट जोडण्यासाठी '+' दाबा.",

        // Lot Creation & Editor
        "lot_editor_title" to "भंगार लॉट तपशील",
        "lot_material_label" to "भंगाराचा प्रकार",
        "lot_weight_label" to "वजन",
        "lot_unit_kg" to "किलो",
        "lot_unit_g" to "ग्रॅम",
        "lot_unit_piece" to "नग (पीस)",
        "lot_condition_label" to "स्थिती",
        "lot_cond_intact" to "अखंड / चांगल्या स्थितीत",
        "lot_cond_damaged" to "तुटलेले / खराब",
        "lot_cond_depopulated" to "सुटे भाग काढलेले",
        "lot_cond_burnt" to "जळालेले",
        "lot_cond_leaking" to "गळती / गंजलेले",
        "lot_photo_tap_to_capture" to "भंगाराचा फोटो काढा",
        "lot_photo_retake" to "पुन्हा फोटो काढा",
        "lot_save_draft" to "फोनवर जतन करा",
        "lot_submit_action" to "जतन करून पुढे जा",
        "lot_err_no_material" to "कृपया भंगाराचा प्रकार निवडा.",
        "lot_err_invalid_weight" to "कृपया शून्यापेक्षा जास्त वैध वजन टाका.",
        "lot_warning_heavy_weight" to "वजन 500 किलोपेक्षा जास्त आहे. गुणवत्ता पुनरावलोकनासाठी चिन्हांकित केले.",

        // AI Classifier & Advisory
        "classifier_analyzing" to "ऑन-डिव्हाइस एआय फोटोची तपासणी करत आहे…",
        "classifier_high_confidence" to "एआय सल्ला: %1\$s (%2\$d%% जुळणी)",
        "classifier_advisory_note" to "हा फक्त सल्ला आहे. भंगाराचा खरा प्रकार तुम्ही ठरवा.",
        "classifier_confirm_btn" to "सल्ला स्वीकारा",
        "classifier_change_btn" to "स्वतः निवडा",
        "classifier_abstain_warning" to "एआय खात्री करू शकले नाही (%1\$d%%). कृपया स्वतः प्रकार निवडा.",

        // Prices & Units
        "price_title" to "बाजार भाव व दर",
        "price_indicative_notice" to "सार्वजनिक माहितीवर आधारित अंदाजे भाव. कोणतीही सक्ती नाही.",
        "price_per_kg" to "₹%1\$s / किलो",
        "price_range_format" to "₹%1\$s – ₹%2\$s / किलो",
        "price_confidence_high" to "उच्च विश्वासार्हता (%1\$d भाव नोंदवले)",
        "price_confidence_med" to "मध्यम विश्वासार्हता",
        "price_confidence_low" to "कमी डेटा / प्रादेशिक अंदाज",
        "price_insufficient_data" to "पुरेसा भाव उपलब्ध नाही",
        "price_add_observation" to "बाजारातील नवीन भाव सांगा",
        "price_obs_submitted" to "भावाची नोंद पुनरावलोकनासाठी पाठवली.",

        // Recycler Directory & Matching
        "recycler_dir_title" to "नोंदणीकृत रिसायकलर यार्ड",
        "recycler_distance" to "%1$.1f किमी अंतर",
        "recycler_route_authorized" to "प्रदूषण नियंत्रण मंडळ अधिकृत",
        "recycler_route_battery" to "बॅटरी नियम २०२२ नोंदणीकृत",
        "recycler_battery_isolation" to "धोकादायक बॅटरीची स्वतंत्र प्रक्रिया आवश्यक आहे.",
        "recycler_request_quote" to "भाव मागा",
        "recycler_offer_received" to "प्रस्ताव: ₹%1\$s / किलो",
        "recycler_offer_accept" to "प्रस्ताव स्वीकारा",
        "recycler_offer_reject" to "नाकारा",
        "recycler_no_match" to "तुमच्या परिसरात या भंगारासाठी कोणताही अधिकृत यार्ड सापडला नाही.",

        // Handover, QR & Digital Record
        "handover_title" to "भंगार हस्तांतरण व पावती",
        "handover_qr_title" to "रिसायकलरला क्यूआर दाखवा",
        "handover_qr_desc" to "रिसायकलर त्यांच्या फोनने स्कॅन करून पावती निश्चित करतील.",
        "handover_actual_weight" to "यार्डमध्ये मोजलेले वजन",
        "handover_weight_diff" to "वजनातील फरक: %1\$s",
        "handover_variance_warning" to "वजनात २०%% पेक्षा जास्त फरक आहे. पुष्टी करण्यापूर्वी तपासा.",
        "handover_dispute_reason" to "तक्रारीचे कारण",
        "handover_btn_confirm" to "नवीन वजन व अटी मान्य करा",
        "handover_pdf_share" to "पावती पीडीएफ डाउनलोड / शेअर करा",
        "handover_public_seal" to "डिजिटल सील हॅश: %1\$s",

        // Payments & Ledger
        "ledger_title" to "कमाई आणि बाकी हिशोब",
        "ledger_total_earned" to "एकूण भंगार मूल्य",
        "ledger_acknowledged_paid" to "मिळालेली रोख रक्कम",
        "ledger_dues_pending" to "उर्वरित बाकी",
        "payment_record_cash" to "रोख पावती नोंदवा",
        "payment_upi_ref_optional" to "यूपीआय संदर्भ क्रमांक (पर्यायी)",
        "payment_counterparty_ack" to "दुसऱ्या पक्षाने रोख रक्कम मिळाल्याची पुष्टी केली आहे.",
        "payment_reversal_notice" to "हा व्यवहार रद्द करण्यात आला: %1\$s",
        "payment_empty_ledger" to "अद्याप कोणतेही व्यवहार नाहीत.",

        // Synchronization & Offline
        "sync_title" to "सिंक केंद्र",
        "sync_pending_count" to "फोनवर %1\$d व्यवहार प्रलंबित",
        "sync_all_synced" to "सर्व नोंदी सर्व्हरवर सुरक्षित आहेत",
        "sync_syncing_progress" to "सर्व्हरशी सिंक होत आहे (%1\$d / %2\$d)…",
        "sync_btn_start" to "आता सिंक करा",
        "sync_err_network" to "ऑफलाइन. इंटरनेटची प्रतीक्षा आहे.",
        "sync_err_conflict" to "सर्व्हरवरील अटी बदलल्या. स्थानिक माहिती ताजी केली.",
        "sync_safe_notice" to "विमान मोडमध्येही सर्व माहिती फोनवर पूर्णपणे सुरक्षित राहते.",

        // Safety Warnings
        "safety_title" to "भंगार हाताळणी सुरक्षा",
        "safety_crt_warning" to "सावधान: सीआरटी काच फुटण्याचा धोका व विषारी फॉस्फरस. ट्यूब फोडू नका.",
        "safety_battery_warning" to "धोका: आग आणि ॲसिडने भाजण्याचा धोका. टोके वेगळी ठेवा. दाबू नका.",
        "safety_pcb_warning" to "सावधान: विषारी जड धातू. उघड्यावर जाळू नका किंवा ॲसिडने धुवू नका.",
        "safety_cable_warning" to "सूचना: केबल जाळणे कायद्याने गुन्हा आहे. कटरने सोला.",

        // Economics & Preferences
        "econ_title" to "अंदाजे कमाई तुलना",
        "econ_current_net" to "सध्याची असंघटित कमाई",
        "econ_platform_net" to "सही तोल अंदाजे कमाई",
        "econ_zero_fee" to "कबाडी बांधवांसाठी कोणतेही शुल्क नाही (०%)",
        "econ_disclaimer" to "संशोधनावर आधारित मॉडेल. प्रत्यक्ष कमाई स्थानिक भावावर अवलंबून असते.",
        "pref_numeral_title" to "अंक प्रदर्शन पसंती",
        "pref_numeral_latin" to "इंग्रजी अंक (1, 2, 3)",
        "pref_numeral_devanagari" to "देवनागरी अंक (१, २, ३)",
        "pref_language_title" to "ॲपची भाषा",

        // Accessibility & Screen Reader Labels
        "a11y_tap_to_hear" to "ऐकण्यासाठी टॅप करा",
        "a11y_weight_readout" to "वजन: %1\$s, प्रकार: %2\$s, स्थिती: %3\$s",
        "a11y_price_readout" to "भाव: %1\$s प्रति किलो, विश्वासार्हता: %2\$s",
        "a11y_qr_code" to "रिसायकलर स्कॅनसाठी हस्तांतरण क्यूआर कोड"
    )

    private val missingKeyAccessAudit = mutableListOf<String>()

    /**
     * Retrieve localized string by key and language code.
     * Reports missing keys to audit list rather than silently falling back.
     */
    fun get(key: String, lang: String = "hi", vararg args: Any): String {
        val map = when (lang) {
            "hi" -> STRINGS_HI
            "mr" -> STRINGS_MR
            else -> STRINGS_EN
        }

        val template = map[key] ?: run {
            synchronized(missingKeyAccessAudit) {
                missingKeyAccessAudit.add("$lang:$key")
            }
            // Strict fallback order: hi -> en
            STRINGS_HI[key] ?: STRINGS_EN[key] ?: key
        }

        return if (args.isEmpty()) {
            template
        } else {
            try {
                String.format(template, *args)
            } catch (e: Exception) {
                template
            }
        }
    }

    fun getAuditRecordedMissingAccesses(): List<String> {
        return synchronized(missingKeyAccessAudit) {
            missingKeyAccessAudit.toList()
        }
    }

    /**
     * Verification engine running automated parity check across all languages.
     * Checks:
     * 1. Every key in STRINGS_EN exists in STRINGS_HI.
     * 2. Every key in STRINGS_EN exists in STRINGS_MR.
     * 3. Number of format specifiers (%1$s, %2$d, etc.) matches identically.
     */
    fun runAudit(): TranslationAuditResult {
        val totalKeys = STRINGS_EN.size
        val missingHi = mutableListOf<String>()
        val missingMr = mutableListOf<String>()
        val placeholderMismatches = mutableListOf<String>()

        val specifierPattern = Pattern.compile("%(?:\\d+\\$)?[\\d.]*[a-zA-Z%]")

        for ((key, enText) in STRINGS_EN) {
            val hiText = STRINGS_HI[key]
            if (hiText == null) {
                missingHi.add(key)
            } else {
                val enSpecifiers = countSpecifiers(enText, specifierPattern)
                val hiSpecifiers = countSpecifiers(hiText, specifierPattern)
                if (enSpecifiers != hiSpecifiers) {
                    placeholderMismatches.add("HI key '$key': expected $enSpecifiers specifiers, found $hiSpecifiers")
                }
            }

            val mrText = STRINGS_MR[key]
            if (mrText == null) {
                missingMr.add(key)
            } else {
                val enSpecifiers = countSpecifiers(enText, specifierPattern)
                val mrSpecifiers = countSpecifiers(mrText, specifierPattern)
                if (enSpecifiers != mrSpecifiers) {
                    placeholderMismatches.add("MR key '$key': expected $enSpecifiers specifiers, found $mrSpecifiers")
                }
            }
        }

        return TranslationAuditResult(
            totalKeys = totalKeys,
            missingHi = missingHi,
            missingMr = missingMr,
            placeholderMismatches = placeholderMismatches
        )
    }

    private fun countSpecifiers(text: String, pattern: Pattern): Int {
        val matcher = pattern.matcher(text)
        var count = 0
        while (matcher.find()) {
            // %% is an escaped percent, not an argument specifier
            if (matcher.group() != "%%") {
                count++
            }
        }
        return count
    }
}
