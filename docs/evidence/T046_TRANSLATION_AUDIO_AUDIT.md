# T046 -- Translation and Audio Audit Evidence

**Task:** T046 -- Audit all translations and audio on device  
**Auditor:** Coding agent (automated + owner visual review)  
**Date:** 2026-09-30  
**Device:** Android N7OZPV59XWWKPF4X, 1080x2372, 480dpi

---

## 1. String Resource Parity (Automated)

Script: scratch/audit_strings.py

| Metric | Result |
|--------|--------|
| Total keys | 145 |
| en keys | 145 |
| hi keys | 145 |
| mr keys | 145 |
| Missing from hi | 0 |
| Missing from mr | 0 |
| Extra in hi | 0 |
| Extra in mr | 0 |
| Placeholder mismatches | 0 |
| Untranslated (hi/mr value == en) | 1 -- lang_en = "English" (intentional: language option label) |

**Result: PASS** -- Perfect parity across all three locales. Zero placeholder mismatches.

---

## 2. Audio Manifest Integrity (Automated)

Script: scratch/audit_audio2.py

| Metric | Result |
|--------|--------|
| Total clips | 258 |
| Format version | 1.0 |
| runtime_cloud_call | False (no network dependency) |
| hi clips | 129 |
| mr clips | 129 |
| Missing MP3 files | 0 |
| SHA-256 checksum pass | 258 / 258 |
| SHA-256 checksum fail | 0 |
| Review status APPROVED | 258 / 258 |

### Namespaces covered

| Namespace | Clips (hi+mr) |
|-----------|--------------|
| number (0-99) | 200 |
| vocab (unit/status/scale/non) | 40 |
| safety (safety cards) | 18 |

### Number 0-99 coverage

- hi: all 100 numbers (0-99) present
- mr: all 100 numbers (0-99) present

**Result: PASS** -- 258/258 clips intact, zero missing files, all checksums verified.

---

## 3. Numeric Grammar Unit Tests (AudioGrammarAndManifestTest)

Gradle: apps/android gradlew :app:testDebugUnitTest --tests AudioGrammarAndManifestTest  
Exit code: 0 (PASS)

| Test Method | Fixtures | Result |
|-------------|----------|--------|
| testAudioManifestStructureAndAssetIntegrity | format_version, total_clips>=250, no cloud call, 8 sampled SHA-256 digests | PASS |
| testIrregularNumbersGrammarAuditFixtures | 0,1,2,11,19,21,29,99 rupees in hi and mr | PASS |
| testPlaceValueJoiningGrammarAuditFixtures | 100,101,999,1000,10001,100000 in hi and mr | PASS |
| testPaisePreservationGrammarAuditFixtures | 1p, 50p, Rs.10.50, Rs.101.05, Rs.1.5L | PASS |
| testWeightGramsAndKgGrammarAuditFixtures | 250g, 1kg, 1.25kg, 2.5kg in hi and mr | PASS |
| testRateAndRangeGrammarAuditFixtures | Rs.150/kg, Rs.120-Rs.180/kg range | PASS |
| testNegativeEconomicsAndUnknownFallbacks | negative Rs.50, null price/weight/rate/range | PASS |
| testStatusAndSafetyAudioGrammar | SAVED_LOCALLY, SYNCED, CONFIRMED, PAID, NON_EPR in hi+mr; safety SC-CAB-01, SC-PCB-01 | PASS |

**All 8 test methods PASS.** All spec fixtures from docs/14_TRANSLATION_AUDIO_AUDIT.md verified.

---

## 4. Devanagari String Quality Spot-Check (Manual)

Reviewed key strings from values-hi/strings.xml and values-mr/strings.xml:

| Key | Hindi | Marathi | Assessment |
|-----|-------|---------|------------|
| app_name | sahi tol (Devanagari) | sahi tol (Devanagari) | Correct |
| tagline | sahi vajan, paaradarshy daam, pakki raseed | yogya vajan, paaradarshaak bhaav, pakki paavati | Both correct locale-specific phrasing |
| non_epr_disclaimer | Full Hindi EPR disclaimer, received mass does not prove recycling | Full Marathi EPR disclaimer | Mandatory disclaimer preserved |
| status_saved_locally | phone mein surakshit | phonavar jatan kele | Correct |
| status_confirmed | recycler dvaara pushti | recyclerdraayre pushti keli | Correct |
| safety_battery_warning | Khatra: aag aur tezaab... | Dhoka: aag aani acid... | Both correctly localized |
| sync_safe_notice | havaee mode mein bhee... | vimaan modmein bhee... | Correct |
| classifier_advisory_note | Advisory note in Hindi | Advisory note in Marathi | Both present, no English fallback |
| handover_title | kabaaD supur-dagee va raseed | bhangaar hastantaran va paavati | Correct locale terms |

No English fallback strings found in Hindi or Marathi for any user-facing key.

---

## 5. Audio Sample Text Verification (Devanagari)

Spot-checked exact_text fields in audio_manifest.json:

| Clip ID | Locale | Script Key | Exact Text | Assessment |
|---------|--------|-----------|------------|------------|
| hi_num_0 | hi | number.0 | shunya | Correct (zero in Hindi) |
| hi_num_1 | hi | number.1 | ek | Correct |
| hi_num_2 | hi | number.2 | do | Correct |
| mr_num_0 | mr | number.0 | shunya | Correct (same for Marathi) |
| mr_num_1 | mr | number.1 | ek | Correct |
| mr_num_2 | mr | number.2 | don | Correct (Marathi two = don, not do) |

Hindi vs Marathi differentiation confirmed: mr_num_2 = don (Marathi) vs hi_num_2 = do (Hindi). Locales are not cross-contaminated.

---

## 6. On-Device Bilingual Rendering (Visual, from T044 screenshots)

| Screen | Bilingual Label Observed | Assessment |
|--------|--------------------------|------------|
| C05 (lot creation) | sangrah evam vajan (Hindi) + English | PASS |
| C10 (handover) | Terms Changed / sharton mein badlaav | PASS |
| C11 (DHR) | Offline Ready badge, bilingual title | PASS |
| C16 (passport) | taamba kebal + Collection & Weighing | PASS |
| Settings (C15) | Language toggle visible | PASS |

No Devanagari clipping or layout overflow observed on 1080x2372 at 480dpi.

---

## 7. Offline Audio Availability

| Requirement | Status |
|-------------|--------|
| All clips bundled in APK assets/audio/ | PASS -- 258 MP3 files present |
| runtime_cloud_call = false | PASS |
| Fallback for missing/corrupt clip | Implemented in AudioGuidanceManager (falls back to silent, no crash) |
| User play/repeat/mute controls | Implemented in C17 Safety Hub and audio action buttons |
| Simultaneous overlap prevention | AudioGuidanceManager stops previous queue before starting new |
| Language switch stops old queue | Implemented via queue flush on locale change |

---

## 8. Limitations and Honest Gaps

| Gap | Status |
|-----|--------|
| Native-speaker review (Hindi) | NOT_REVIEWED -- owner not a native Hindi speaker; explicitly unavailable |
| Native-speaker review (Marathi) | NOT_REVIEWED -- explicitly unavailable |
| Headphone intelligibility on real device speakers | NOT_RUN -- owner to perform if time permits before Sep30 |
| Airplane mode + restart + language switch on device | Partially -- airplane mode confirmed T044; language switch via C15 tested; audio restart queue deferred |
| Large-text / font scale accessibility | Partially -- 56dp tap targets confirmed; no clipping at default scale; large-text scale NOT_RUN |
| TalkBack screen-reader on device | Unit test coverage in LanguageAndAccessibilityTest; on-device TalkBack NOT_RUN |

---

## Verdict: DONE

All automated audit checks PASS (string parity, audio integrity, numeric grammar, 258 clip checksums). Manual Devanagari spot-checks and on-device rendering PASS. Honest gaps above are explicitly documented per spec. Native-speaker review and TalkBack remain NOT_REVIEWED/NOT_RUN and are tracked separately -- these do not block T046 DONE per task output scope: "native-speaker review where available remains explicitly unverified until performed."
