# T036: Complete Language Resources, Numeral Preference, and Accessible Interaction

**Task ID**: `T036`  
**Phase**: Phase 5 (Core Collector Flows)  
**Requirements**: [`R-LANG-01`](../15_REQUIREMENTS.md#r-lang-01), [`R-UX-01`](../15_REQUIREMENTS.md#r-ux-01)  
**Acceptance Cases**: [`AT-049`](../20_TEST_ACCEPTANCE.md#at-049) (contributing), [`AT-051`](../20_TEST_ACCEPTANCE.md#at-051) (contributing)  
**Related Specifications**: [`docs/14_TRANSLATION_AUDIO_AUDIT.md`](../14_TRANSLATION_AUDIO_AUDIT.md), [`docs/05_DESIGN_STITCH.md`](../05_DESIGN_STITCH.md)  
**Date**: 2026-09-30  
**Status**: DONE  

---

## 1. Executive Summary

Task `T036` completes full native Android string localization across Hindi (`hi`), Marathi (`mr`), and English (`en`), implement colloquial e-waste scrap aliases from the curated material taxonomy (`T010`), establishes locale-aware Indian numbering and paise preservation formatting, introduces an explicit numeral preference (Latin `0–9` vs Devanagari `०–९`), and ensures TalkBack screen-reader semantics and touch-target accessibility standards.

All implementations strictly adhere to product constraints:
1. **Stable Semantic Keys**: No English text is used as keys. All string keys are categorized across the 13 required namespaces (`auth`, `nav`, `lot`, `classifier`, `price`, `recycler`, `handover`, `payment`, `sync`, `safety`, `economics`, `pref`, `a11y`).
2. **Translation Parity & Audit Integrity**: Exact placeholder and key parity is maintained across `values/strings.xml`, `values-hi/strings.xml`, and `values-mr/strings.xml`. An automated verification engine (`SahiTolStrings.runAudit()`) validates parity; missing translations are tracked in an audit log rather than silently masked by English fallbacks (`AT-049`).
3. **Colloquial Scrap Material Aliases**: Vernacular terminology used by informal scrap workers (e.g., *हरा पत्ता* / *मदरबोर्ड* for PCB, *तांबा तार* / *तांब्याची वायर* for Cable, *गाड़ी की बैटरी* for Lead-Acid, *कूलर मोटर* for Motor, *पुराना टीवी* for CRT) is integrated for instant zero-I/O offline lookup and visual display on lot creation tiles.
4. **Locale-Aware Indian Numbering & Paise Preservation**: Numbers format with Indian comma grouping (`₹1,50,000`, `₹10,00,000`). Exact fractional paise amounts (1 paise $\to$ `₹0.01`, 50 paise $\to$ `₹0.50`, 1050 paise $\to$ `₹10.50`) are preserved without rounding.
5. **Numeral Preference**: Users can toggle between standard Latin digits and authentic Devanagari numerals in settings (`C15`), persisted across app restarts in `SessionManager`.
6. **Accessibility Standards**: Minimum 48dp (and 56dp for primary action CTAs) touch targets, no color-only statuses, and TalkBack announcements formatted according to standard: `label + value + unit + status`.

---

## 2. Architecture & Implementation Details

### 2.1 Complete XML Strings Resources
- `apps/android/app/src/main/res/values/strings.xml` (Base English catalog)
- `apps/android/app/src/main/res/values-hi/strings.xml` (Authentic Hindi catalog)
- `apps/android/app/src/main/res/values-mr/strings.xml` (Authentic Marathi catalog)

The catalog covers all 13 required namespaces:
- **Identity & Status Invariants**:
  - `status_saved_locally` ("Saved on phone" / "फोन में सुरक्षित" / "फोनवर जतन केले")
  - `status_synced` ("Synchronized" / "सर्वर पर सिंक हुआ" / "सर्व्हरवर सिंक केले")
  - `status_confirmed` ("Recycler Confirmed" / "रिसाइकलर द्वारा पुष्टि" / "रिसायकलरद्वारे पुष्टी केली")
  - `status_paid` ("Payment Acknowledged" / "भुगतान स्वीकृत" / "पैसे मिळाल्याची पोच")
  - `non_epr_disclaimer` (Statutory non-EPR disclosure)
- **Auth & Session**: PIN entry, phone masking, zero-PII reassurance, safe logout warning.
- **Lot & Classifier**: AI advisory prompt, confidence rating, confirmation, abstention warning, condition options.
- **Prices & Directory**: Market rates, 30-day trends, authorized facility filters, battery route isolation.
- **Handover & Payments**: Actual weight discrepancy warning, dispute notes, cash-first ledger balance.
- **Safety**: Pictorial warnings for CRT, Battery, PCB, and Cables.

### 2.2 SahiTolStrings Dictionary & Parity Audit Engine
`apps/android/app/src/main/java/com/sahitol/collector/domain/locale/SahiTolStrings.kt`
- Implements `get(key, lang, args...)` providing programmatic string lookup with parameter substitution.
- Integrates `runAudit(): TranslationAuditResult` verifying:
  1. $100\%$ key parity between `STRINGS_EN`, `STRINGS_HI`, and `STRINGS_MR`.
  2. Identical placeholder count and format specifiers (`%1$s`, `%1$d`, etc.) across languages.
- Records missing translation accesses in `missingKeyAccessAudit` to prevent silent English fallbacks (`AT-049`).

### 2.3 Colloquial Material Aliases Provider
`apps/android/app/src/main/java/com/sahitol/collector/domain/locale/MaterialAliases.kt`
- Loaded with curated colloquial aliases from `T010` (`data/curated/material_catalog/material_aliases.json`).
- Bundled into `apps/android/app/src/main/assets/material_aliases.json` for offline asset access.
- Exposes:
  - `getAliasesForCategory(category, lang)`: Returns localized aliases (e.g. `["मदरबोर्ड", "हरा पत्ता", "कंप्यूटर सर्किट बोर्ड"]` for `MaterialCategory.PCB` in Hindi).
  - `searchCategoryByColloquialTerm(term, lang)`: Resolves informal search queries (e.g. "तांबा तार" $\to$ `MaterialCategory.COPPER_CABLE`).
- Visualized directly in `C05_LotEditorScreen` via an interactive vernacular alias pill under the material selection grid.

### 2.4 LocaleFormatter & Numeral Preference
`apps/android/app/src/main/java/com/sahitol/collector/domain/locale/LocaleFormatter.kt`
`apps/android/app/src/main/java/com/sahitol/collector/domain/locale/NumeralPreference.kt`
- `formatIndianNumber(value, preference)`: Generates Indian comma grouping (e.g. `1,50,000`, `1,00,00,000`).
- `formatPaise(paise, lang, preference)`: Preserves paise (`1` $\to$ `₹0.01`, `50` $\to$ `₹0.50`, `1050` $\to$ `₹10.50`, `15000000` $\to$ `₹1,50,000`, `-5000` $\to$ `-₹50`).
- `formatGrams(grams, lang, preference)`: Converts integer grams to localized units (`250g` $\to$ `250 g` / `250 ग्राम` / `250 ग्रॅम`; `1000g` $\to$ `1 kg` / `1 किग्रा` / `1 किलो`; `2500g` $\to$ `2.50 kg`).
- `formatRate(paisePerKg, lang, preference)`: Formats rate (e.g. `₹150 / kg`, `₹150 प्रति किग्रा`).
- `formatRange(min, max, lang, preference)`: Formats range (e.g. `₹120 – ₹180 / kg`).
- `NumeralPreference`: Maps digits `0–9` $\leftrightarrow$ `०–९` (`LATIN` vs `DEVANAGARI`).

### 2.5 Preference Persistence & UI Controls
- `apps/android/app/src/main/java/com/sahitol/collector/data/session/SessionManager.kt`:
  - Added `numeralPreference: NumeralPreference` to `CollectorSession`.
  - Added `setNumeralPreference(pref)` persisting in `SharedPreferences` (`KEY_NUMERAL_PREF`).
  - Added constructor overload `SessionManager(prefs: SharedPreferences)` enabling pure unit testing with `MockSharedPreferences`.
  - Preserved across safe logout (`logoutPreservingData()`).
- `apps/android/app/src/main/java/com/sahitol/collector/ui/collector/C15_SettingsScreen.kt`:
  - Added Numeral Display Preference Card allowing live toggles between "English Digits (1, 2, 3)" and "Devanagari Numerals (१, २, ३)".
  - Wired to `sessionManager.setNumeralPreference` via `CollectorNavHost.kt`.

### 2.6 Accessibility Semantics & Touch Targets
`apps/android/app/src/main/java/com/sahitol/collector/ui/theme/AccessibilityUtils.kt`
- `Modifier.accessibleTouchTarget()`: Enforces minimum $48\text{dp} \times 48\text{dp}$ touch target bounding.
- `Modifier.primaryTouchTarget()`: Enforces $56\text{dp}$ primary CTA height for collectors with gloved or rough hands (`R-UX-01`).
- `Modifier.scrapLotSemantics()`: TalkBack announcement structure enforcing `label + value + unit + status`.
- `LocaleFormatter.formatScreenReader()`: Builds accessible strings (e.g., `"PCB Lot #104, 14.25, kg, Saved on phone"`).

---

## 3. Test Evidence

### 3.1 Automated Test Execution (`LanguageAndAccessibilityTest.kt`)
A comprehensive unit test suite was authored in `apps/android/app/src/test/java/com/sahitol/collector/LanguageAndAccessibilityTest.kt`:

| Test Name | Verified Invariant | Result |
|---|---|---|
| `testTranslationKeyParityAndPlaceholderAudit` | 100% key parity across en/hi/mr; zero missing keys; zero placeholder mismatches | **PASS** |
| `testUnavailableTranslationAuditReporting` | Unavailable translation logged in audit trail rather than silently masked (`AT-049`) | **PASS** |
| `testFourImmutableStatusInvariantsAcrossLanguages` | "Saved on phone", "Synchronized", "Recycler Confirmed", "Payment Acknowledged" + Non-EPR banner | **PASS** |
| `testIndianNumberFormattingAndLakhNotation` | 0, 99, 999, 1,000, 10,001, 1,00,000, 15,50,000, 1,00,00,000 notation | **PASS** |
| `testPaisePreservationAuditFixtures` | 1 paise (`₹0.01`), 50 paise (`₹0.50`), ₹10.50, ₹101.05, ₹1,50,000, negative economics | **PASS** |
| `testWeightGramsAndKilogramsAuditFixtures` | 250g, 1kg, 1.25kg, 2.5kg in English, Hindi (`ग्राम`, `किग्रा`), and Marathi (`ग्रॅम`, `किलो`) | **PASS** |
| `testRateAndRangeFormatting` | ₹150/kg, ₹120–₹180/kg localized units | **PASS** |
| `testDevanagariNumeralPreference` | Devanagari digit conversion (`₹1,50,000` $\to$ `₹१,५०,०००`, `२.५ किग्रा`, `₹१०.५०`) | **PASS** |
| `testColloquialMaterialAliasesLookup` | Colloquial terms (*मदरबोर्ड*, *हरा पत्ता*, *तांबा तार*, *गाड़ी की बैटरी*, *कूलर मोटर*, *पुराना टीवी*) & reverse search | **PASS** |
| `testLanguageAndNumeralPreferencePersistenceInSessionManager` | Language (`hi`/`mr`) and Numeral preference (`LATIN`/`DEVANAGARI`) persist across app restarts and safe logout | **PASS** |
| `testAccessibilityScreenReaderSemantics` | Announcement structure: `Label + Value + Unit + Status` | **PASS** |

### 3.2 Test Suite Execution Output
```text
> Task :app:compileDebugUnitTestKotlin
> Task :app:testDebugUnitTest

BUILD SUCCESSFUL in 1m 25s
29 actionable tasks: 4 executed, 25 up-to-date
```
All 66 Android unit tests passed with 100% success rate.

---

## 4. Acceptance Criteria Compliance

- **`R-LANG-01`**: Complete Hindi (`hi`), Marathi (`mr`), and English (`en`) fallback implemented across all screens. Zero English text used as keys. Missing translations tracked in audit log (`AT-049`).
- **`R-UX-01`**: Low-literacy accessible interactions, large touch targets ($\ge 48$dp, primary 56dp), short vernacular labels, colloquial aliases, TalkBack accessibility semantics, explicit numeral preference (`AT-051`).
- **`T036` Output Contract**: "Implement all collector hi/mr/en strings, material aliases, accessibility labels, plurals/currency/units and numeral preference; preserve chosen language offline/restart; no hardcoded English critical errors." **FULFILLED IN FULL**.
