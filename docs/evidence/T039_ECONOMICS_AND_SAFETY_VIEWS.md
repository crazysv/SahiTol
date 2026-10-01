# Test Evidence: T039 Implement Approved Economics and Safety Views

## Metadata
- **Task ID**: `T039`
- **Phase**: Phase 5 (Core Collector Flows)
- **Scope**: RELEASE
- **Date**: 2026-09-30
- **Requirements**: [`R-GOV-02`](../15_REQUIREMENTS.md#r-gov-02), [`R-SAFE-01`](../15_REQUIREMENTS.md#r-safe-01), [`R-ECON-01`](../15_REQUIREMENTS.md#r-econ-01)
- **Acceptance Cases**: [`AT-002`](../20_TEST_ACCEPTANCE.md#at-002), [`AT-048`](../20_TEST_ACCEPTANCE.md#at-048), [`AT-067`](../20_TEST_ACCEPTANCE.md#at-067)
- **Related Specifications**: [`docs/05_DESIGN_STITCH.md`](../05_DESIGN_STITCH.md), [`docs/23_UNIT_ECONOMICS.md`](../23_UNIT_ECONOMICS.md), [`docs/04_APPFLOW.md`](../04_APPFLOW.md), [`design/stitch/SCREEN_REGISTRY.md`](../../design/stitch/SCREEN_REGISTRY.md)
- **Status**: DONE — independently repaired and reverified on 2026-10-01.

---

## 1. Executive Summary

Task `T039` delivers the production implementation of the approved contextual safety views and interactive illustrative unit-economics views across Android Jetpack Compose and React/Vite web applications. Both views strictly implement approved designs from Google Stitch project `245073995801566548`, conforming to the Mandatory Frontend Gate (`design/stitch/SCREEN_REGISTRY.md`), fulfilling all safety non-instructional invariants (`R-SAFE-01`), and upholding transparent illustrative economics reporting without arbitrary income uplift claims (`R-ECON-01`).

Key accomplishments:
1. **Mandatory Frontend Gate Compliance (`R-GOV-02`, `AT-002`)**:
   - Screen `C17` (Screen ID `1579fe53bac5`) implemented in Android Jetpack Compose and registered in `SCREEN_REGISTRY.md` as `IMPLEMENTED_VERIFIED`.
   - Screen `U01` (Screen ID `cab89a974c04`) implemented in React/Vite and registered in `SCREEN_REGISTRY.md` as `IMPLEMENTED_VERIFIED`.
2. **Contextual Safety Hub & Guidance (`C17_SafetyHubScreen.kt`, `R-SAFE-01`, `AT-048`)**:
   - Implemented trilingual support (`en`, `hi`, `mr`) with Devanagari script parity and "Offline Ready" indicator.
   - Connected `SafetyContentManager` providing instant zero-I/O access to all 9 curated safety cards from `T035`: Cables, PCBs, CRT, Lead-Acid Battery, Li-Ion Battery, Mixed Batteries, Damaged/Overheating scrap, Electronics Plastics, and Mixed Assemblies.
   - Connected `AudioGuidanceManager` for tap-to-hear offline voice narration using pre-generated Hindi and Marathi MP3 audio clips (`T037`) with animated soundwave indicators.
   - Displayed "Watch-For Warnings" critical hazard alerts, "Strictly Avoid" prohibitions (No Dismantling, No Burning, No Acid Bath), and "Safer Collector Steps" numbered handling protocol.
   - Wired contextual safety alert banners into `C05_LotEditorScreen.kt` upon material selection, and quick-access navigation from `C03_HomeScreen.kt`.
   - Enforced non-instructional hazard policies: no chemical leaching recipes or manual dismantling procedures; only safe handling and intact routing to certified recyclers.
3. **Interactive Web Unit Economics Workspace (`U01_UnitEconomics.tsx`, `R-ECON-01`, `AT-067`)**:
   - Canonical ECONOMICS_V1 10 kg stripped-copper-cable *chosen demo assumption* (`LOT-2024-9082`): current net ₹350, assumed platform net ₹470, delta ₹120.
   - Side-by-side comparison cards: Baseline (Manual / Current Yard Practice) vs SahiTol Optimized.
   - Unit Economics Waterfall visual stacked bar chart displaying Acquisition, Logistics, Rejection Loss, and Net Margin.
   - Interactive operating-assumption sliders: transport change (-50% to 50%), platform-rate adjustment (-30% to 30%), grading/rejection loss (0%–10%), and an explicitly stated ₹1/day optional time-value sensitivity (0–30 days). Lower rate/higher transport can visibly produce a negative result.
   - The record-quality and platform-rate controls no longer assert an unsourced monetary benefit. The platform-rate control only toggles the documented ₹160/kg fixture assumption.
   - Real-time recalculation of gross, costs, net realization, and net profit variance (+₹ / -₹).
   - Honest baseline handling: when baseline net profit is $\le 0$, percentage comparison is reported as `baseline ≤ 0` / not meaningful, avoiding misleading inverted signs.
   - Mandatory illustrative disclaimer, source/assumption disclosure, Hindi/Marathi net-return labels, separate actual-ledger link, and **0 paise collector transaction fee guarantee** (`R-ECON-02`).
   - Reset scenario and export breakdown to JSON with a browser-computed SHA-256 integrity field.

---

## 2. Component Architecture & Artifacts

### 2.1 Android Components
- [`SafetyModels.kt`](../../apps/android/app/src/main/java/com/sahitol/collector/domain/safety/SafetyModels.kt): Data structures for `HazardLevel`, `SafetyCardLocale`, `SafetyProhibition`, `SafetyStep`, and `SafetyCard`.
- [`SafetyContentManager.kt`](../../apps/android/app/src/main/java/com/sahitol/collector/domain/safety/SafetyContentManager.kt): Domain repository managing all 9 curated safety cards, trilingual text, audio keys, and category/material resolution.
- [`C17_SafetyHubScreen.kt`](../../apps/android/app/src/main/java/com/sahitol/collector/ui/collector/C17_SafetyHubScreen.kt): Jetpack Compose screen implementing Stitch design `1579fe53bac5`.
- [`CollectorNavHost.kt`](../../apps/android/app/src/main/java/com/sahitol/collector/ui/collector/CollectorNavHost.kt): Added `Screen.SafetyHub` route with card and material query parameters.
- [`C03_HomeScreen.kt`](../../apps/android/app/src/main/java/com/sahitol/collector/ui/collector/C03_HomeScreen.kt): Wired safety status card to open Safety Hub.
- [`C05_LotEditorScreen.kt`](../../apps/android/app/src/main/java/com/sahitol/collector/ui/collector/C05_LotEditorScreen.kt): Integrated contextual safety warning banner on hazardous scrap selection (PCB, CRT, Battery, Cable) with direct navigation to Safety Hub.
- [`SafetyContentAndHubTest.kt`](../../apps/android/app/src/test/java/com/sahitol/collector/SafetyContentAndHubTest.kt): 6 automated unit tests validating cards, locales, audio mappings, lookups, and non-instructional invariants.

### 2.2 Web Components
- [`U01_UnitEconomics.tsx`](../../apps/web/src/components/economics/U01_UnitEconomics.tsx): Interactive React/Vite view implementing Stitch design `cab89a974c04`.
- [`App.tsx`](../../apps/web/src/App.tsx): Wired route `/economics` to `U01_UnitEconomics`.
- [`U01_UnitEconomics.test.tsx`](../../apps/web/src/components/economics/U01_UnitEconomics.test.tsx): 6 Vitest unit tests verifying rendering, interactive recalculation, slider updates, toggle behavior, tab navigation, and scenario reset.

---

## 3. Test Verification & Results

### 3.1 Android Unit Tests (`testDebugUnitTest`)
Command: `.\gradlew.bat testDebugUnitTest`  
Result: **BUILD SUCCESSFUL** (79 passing unit tests across all test suites, 0 failures).

```text
> Task :app:testDebugUnitTest
SafetyContentAndHubTest:
  ✓ testAllNineCardsPresentAndConfigured PASSED
  ✓ testTrilingualContentAndDevanagariParity PASSED
  ✓ testAudioKeysMapToValidClips PASSED
  ✓ testCategoryAndMaterialLookups PASSED
  ✓ testProhibitionsAndStepsCompleteness PASSED
  ✓ testNonInstructionalSafetyInvariant PASSED

BUILD SUCCESSFUL in 1m 52s
29 actionable tasks: 10 executed, 19 up-to-date
```

### 3.2 Focused web verification (`vitest run`, typecheck, production build)
Command: `npx vitest run src/components/economics/U01_UnitEconomics.test.tsx --pool=threads --maxWorkers=1 --minWorkers=1`; `npm run typecheck`; `npm run build`
Result: **8/8 U01 tests passed**, TypeScript passed, and the Vite production build passed (98 modules).

```text
 ✓ src/components/economics/U01_UnitEconomics.test.tsx (8 tests)
 Test Files  1 passed (1)
      Tests  8 passed (8)
```

### 3.3 Physical Android verification (collector `N7OZPV59XWWKPF4X`)

On 2026-10-01, the installed collector app was opened on the connected device. The Home quick-status row navigated to C17; the default CRT card visibly showed offline availability, Hindi safety content, an audio-guide trigger, hazards, prohibitions and safer steps. Switching to Marathi visibly changed the card, audio-guide label, hazards and prohibitions to Marathi. This verifies navigation and locale rendering on hardware. Audio asset mapping remains covered by the Android unit test; this run did not make a claim about human-audible playback quality.

---

## 4. Requirement & Acceptance Traceability

| ID | Specification | Status | Evidence & Verification |
|---|---|---|---|
| `R-GOV-02` | Mandatory Frontend Gate & Design System | SATISFIED | Screens `C17` and `U01` matching owner Google Stitch designs registered as `IMPLEMENTED_VERIFIED` in `design/stitch/SCREEN_REGISTRY.md`. |
| `R-SAFE-01` | Contextual Safety Content & Non-Instructional Advice | SATISFIED | 9 material-specific cards with trilingual warnings, prohibitions, safe steps, and tap-to-hear offline audio. Verified in `SafetyContentAndHubTest`. |
| `R-ECON-01` | Same-Lot Comparison Calculator | SATISFIED | Interactive U01 screen with editable assumption sliders, waterfall chart, zero-baseline safety, and negative-benefit transparency. Verified in `U01_UnitEconomics.test.tsx`. |
| `R-ECON-02` | Zero Collector Fee Guarantee | SATISFIED | Displayed prominently in U01 with `collector_fee_paise = 0` invariant. |
| `AT-002` | Registered Screen Review & Parity | PASS | Both `C17` and `U01` verified against Stitch project `245073995801566548`. |
| `AT-048` | Pictorial Hazard Warning & Audio Trigger | PASS | Android invariant tests pass and a physical connected-device run verified C03→C17 navigation, Hindi/Marathi rendering, visible offline state and audio trigger. Human-audible playback quality is not claimed. |
| `AT-067` | Same-Lot Recalculation & Source Drill-down | PASS | U01 tests verify the canonical ₹350/₹470/₹120 fixture, slider/toggle recalculation, an unfavourable lower-rate/higher-transport case, source/assumption disclosure, ledger separation, reset, and the zero/negative-baseline guard. |
