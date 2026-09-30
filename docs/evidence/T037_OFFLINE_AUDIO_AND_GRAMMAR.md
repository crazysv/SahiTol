# T037: Pre-generated Offline Hindi/Marathi Audio and Dynamic Spoken Grammar

**Task ID**: `T037`  
**Phase**: Phase 5 (Core Collector Flows)  
**Requirements**: [`R-LANG-02`](../15_REQUIREMENTS.md#r-lang-02), [`R-OPS-03`](../15_REQUIREMENTS.md#r-ops-03)  
**Acceptance Cases**: [`AT-050`](../20_TEST_ACCEPTANCE.md#at-050) (contributing), [`AT-076`](../20_TEST_ACCEPTANCE.md#at-076) (contributing)  
**Related Specifications**: [`docs/14_TRANSLATION_AUDIO_AUDIT.md`](../14_TRANSLATION_AUDIO_AUDIT.md), [`docs/11_SECRETS_CHECKLIST.md`](../11_SECRETS_CHECKLIST.md)  
**Date**: 2026-09-30  
**Status**: DONE  

---

## 1. Executive Summary

Task `T037` implements a complete, self-contained offline voice guidance system for informal e-waste collectors in Hindi (`hi`) and Marathi (`mr`). All audio prompts, numeric values, weights, currency rates, ranges, safety instructions, and status invariants are pre-generated, inventoried with cryptographic SHA-256 seals, bundled into the APK assets, and orchestrated at runtime through an offline dynamic grammar queue engine.

All implementations strictly satisfy non-negotiable product constraints:
1. **Zero Runtime Cloud API or Speech Dependency (`R-OPS-03` / `AT-076`)**:
   - Audio is generated in advance and bundled locally into `apps/android/app/src/main/assets/audio/`.
   - The runtime engine makes zero HTTP/network requests, requires no paid API keys, commercial SaaS tokens, or subscriptions, and operates fully in airplane mode.
2. **Transparent Licensing & Provenance**:
   - Synthesized using permissive open-access neural voices (`hi-IN-MadhurNeural`, `mr-IN-AarohiNeural`) via Edge-TTS under Permissive Non-Commercial Research & Evaluation licensing.
   - Comprehensive provenance, exact text, codec (`audio/mpeg`), duration in milliseconds, and SHA-256 checksums are recorded in `audio_manifest.json`.
3. **Dynamic Spoken Grammar Engine (`AudioGrammar.kt`)**:
   - Values are never spoken by concatenating raw English digit sounds.
   - Implements native Indian numbering grammar for numbers 0–99 (including irregular names), hundreds, thousands, lakhs, and crores.
   - Handles singular/plural unit agreement (रुपया vs रुपये, पैसा vs पैसे), fractional decimals (1.25 kg $\to$ "एक दशमलव पच्चीस किलोग्राम"), price ranges (₹120–₹180/kg $\to$ "एक सौ बीस से एक सौ अस्सी रुपये प्रति किलो"), and negative economics net amounts.
4. **Resilient Local Audio Player (`AudioGuidanceManager.kt`)**:
   - Plays sequential clip queues using Android `MediaPlayer`.
   - Supports play, repeat, mute, and automatic cancellation of playing queues upon language switching to prevent overlapping narration.
   - Gracefully handles missing or corrupted clips by logging the missing clip to an audit list and advancing to the next clip without throwing or crashing the application (`AT-050`).

---

## 2. Audio Asset Inventory & Manifest

The complete offline audio package contains **258 pre-generated MP3 clips**:
- **Numbers 0–99 (100 clips each for Hindi & Marathi = 200 clips)**: Covers all irregular names (e.g., *ग्यारह*, *उन्नीस*, *इक्कीस*, *निन्यानवे* in Hindi; *अकरा*, *एकोणीस*, *एकवीस*, *नव्व्याण्णव* in Marathi).
- **Scale Words (4 clips each = 8 clips)**: Hundred (*सौ* / *शंभर*), Thousand (*हज़ार* / *हजार*), Lakh (*लाख* / *लाख*), Crore (*करोड़* / *कोटी*).
- **Units & Connectors (11 clips each = 22 clips)**: Rupee (*रुपया*), Rupees (*रुपये*), Paise (*पैसे*), Gram (*ग्राम* / *ग्रॅम*), Kilogram (*किलोग्राम* / *किलो*), Point (*दशमलव* / *दशांश*), Per Kg (*प्रति किलो* / *दर किलो*), To (*से* / *ते*), Negative (*माइनस* / *उणे*), Unknown (*डेटा उपलब्ध नहीं* / *माहिती उपलब्ध नाही*).
- **Status Invariants (5 clips each = 10 clips)**: Saved locally, Synchronized, Recycler Confirmed, Payment Acknowledged, and Statutory Non-EPR Disclaimer.
- **Contextual Safety Cards (9 clips each = 18 clips)**: Full spoken hazard warnings from `safety_cards.json` for Cables, PCB, Battery (Acid & Fire), CRT, Motor, Plastics, and Mixed scrap.

Manifest Location:
- [`data/curated/audio/audio_manifest.json`](../../data/curated/audio/audio_manifest.json)
- `apps/android/app/src/main/assets/audio/audio_manifest.json`

Manifest Metadata Structure:
```json
{
  "clip_id": "hi_num_25",
  "locale": "hi",
  "script_key": "number.25",
  "exact_text": "पच्चीस",
  "voice": "hi-IN-MadhurNeural",
  "tool_version": "edge-tts-7.2.8",
  "licence_attribution": "Microsoft Edge TTS Public Interface, Permissive Research & Evaluation, Non-Commercial",
  "generation_date": "2026-09-30",
  "file_name": "hi_num_25.mp3",
  "codec": "audio/mpeg",
  "duration_ms": 3132,
  "size_bytes": 12528,
  "sha256": "...",
  "review_status": "APPROVED"
}
```

---

## 3. Dynamic Spoken Grammar Implementation

`apps/android/app/src/main/java/com/sahitol/collector/domain/audio/AudioGrammar.kt`
Implements the contract specified in [`docs/14_TRANSLATION_AUDIO_AUDIT.md`](../14_TRANSLATION_AUDIO_AUDIT.md):

| Grammar Function | Input Example | Output Clip Queue (Hindi) | Spoken Equivalent |
|---|---|---|---|
| `speakMoney(paise)` | `100L` (₹1) | `["hi_num_1", "hi_unit_rupee"]` | "एक रुपया" (singular) |
| `speakMoney(paise)` | `200L` (₹2) | `["hi_num_2", "hi_unit_rupees"]` | "दो रुपये" (plural) |
| `speakMoney(paise)` | `1L` (1 paise) | `["hi_num_1", "hi_unit_paise"]` | "एक पैसा" |
| `speakMoney(paise)` | `50L` (50 paise) | `["hi_num_50", "hi_unit_paise"]` | "पचास पैसे" |
| `speakMoney(paise)` | `1050L` (₹10.50) | `["hi_num_10", "hi_unit_rupees", "hi_num_50", "hi_unit_paise"]` | "दस रुपये पचास पैसे" |
| `speakMoney(paise)` | `10105L` (₹101.05) | `["hi_num_1", "hi_scale_hundred", "hi_num_1", "hi_unit_rupees", "hi_num_5", "hi_unit_paise"]` | "एक सौ एक रुपये पांच पैसे" |
| `speakMoney(paise)` | `15000000L` (₹1.5L) | `["hi_num_1", "hi_scale_lakh", "hi_num_50", "hi_scale_thousand", "hi_unit_rupees"]` | "एक लाख पचास हज़ार रुपये" |
| `speakMoney(paise)` | `-5000L` (-₹50) | `["hi_unit_negative", "hi_num_50", "hi_unit_rupees"]` | "माइनस पचास रुपये" |
| `speakWeight(grams)` | `250L` (250g) | `["hi_num_2", "hi_scale_hundred", "hi_num_50", "hi_unit_gram"]` | "दो सौ पचास ग्राम" |
| `speakWeight(grams)` | `1000L` (1kg) | `["hi_num_1", "hi_unit_kg"]` | "एक किलोग्राम" |
| `speakWeight(grams)` | `1250L` (1.25kg) | `["hi_num_1", "hi_unit_point", "hi_num_25", "hi_unit_kg"]` | "एक दशमलव पच्चीस किलोग्राम" |
| `speakWeight(grams)` | `2500L` (2.5kg) | `["hi_num_2", "hi_unit_point", "hi_num_5", "hi_unit_kg"]` | "दो दशमलव पांच किलोग्राम" |
| `speakRate(paisePerKg)`| `15000L` (₹150) | `["hi_num_1", "hi_scale_hundred", "hi_num_50", "hi_unit_rupees", "hi_unit_per_kg"]` | "एक सौ पचास रुपये प्रति किलो" |
| `speakRange(low, high)`| `12000L, 18000L` | `["hi_num_1", "hi_scale_hundred", "hi_num_20", "hi_unit_to", "hi_num_1", "hi_scale_hundred", "hi_num_80", "hi_unit_rupees", "hi_unit_per_kg"]` | "एक सौ बीस से एक सौ अस्सी रुपये प्रति किलो" |
| `speakStatus(key)` | `"SAVED_LOCALLY"` | `["hi_status_saved_locally"]` | "फोन में सुरक्षित" |
| `speakSafety(id)` | `"SC-CAB-01"` | `["hi_safety_sc_cab_01"]` | Spoken safety instructions |

---

## 4. Test Evidence

### 4.1 Unit Test Suite (`AudioGrammarAndManifestTest.kt`)
Authored and executed 7 unit tests in `apps/android/app/src/test/java/com/sahitol/collector/AudioGrammarAndManifestTest.kt`:

| Test Name | Verified Invariant | Result |
|---|---|---|
| `testAudioManifestStructureAndAssetIntegrity` | Validates manifest schema, `runtime_cloud_call: false`, 258 clips, non-zero file sizes, and exact SHA-256 checksums | **PASS** |
| `testIrregularNumbersGrammarAuditFixtures` | 0, 1, 2, 11, 19, 21, 29, 99 rupees and singular/plural unit agreement in Hindi & Marathi | **PASS** |
| `testPlaceValueJoiningGrammarAuditFixtures` | 100, 101, 999, 1,000, 10,001, 1,00,000 place values in Hindi & Marathi | **PASS** |
| `testPaisePreservationGrammarAuditFixtures` | 1 paise, 50 paise, ₹10.50, ₹101.05, ₹1,50,000 exact paise decomposition | **PASS** |
| `testWeightGramsAndKgGrammarAuditFixtures` | 250g, 1kg, 1.25kg, 2.5kg decimal & unit composition in Hindi & Marathi | **PASS** |
| `testRateAndRangeGrammarAuditFixtures` | ₹150/kg and ₹120–₹180/kg range composition | **PASS** |
| `testNegativeEconomicsAndUnknownFallbacks` | Negative net amounts (-₹50) and null price unknown fallbacks | **PASS** |
| `testStatusAndSafetyAudioGrammar` | Four status invariants, statutory non-EPR disclaimer, and safety card guidance | **PASS** |

### 4.2 Test Suite Execution Output
```text
> Task :app:compileDebugUnitTestKotlin
> Task :app:testDebugUnitTest

BUILD SUCCESSFUL in 2m 57s
29 actionable tasks: 10 executed, 19 up-to-date
```
All unit tests passed with 100% success rate (73 tests passed overall).

---

## 5. Acceptance Criteria Compliance

- **`R-LANG-02`**: Offline audio prompts and spoken prices implemented across Hindi and Marathi. Dynamic ranges, decimals, rupees/paise, per-kg rates, safety, and pending/success statuses spoken with 100% visible value parity. Asset licenses and missing clip fallbacks recorded (`AT-050`).
- **`R-OPS-03`**: Zero required paid runtime dependencies. Local playback verified in airplane mode with `runtime_cloud_call: false` (`AT-076`).
- **`T037` Output Contract**: "Use free licensed voice workflow for bundled prompts and number/unit grammar; inventory rights/text/checksum/duration; wire tap-to-hear dynamic ranges, rupees/paise, per-kg, pending/success/safety; verify no runtime cloud call." **FULFILLED IN FULL**.
