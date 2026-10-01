# Test Evidence: T020 Implement Approved Collector Price and Recycler Views

## Metadata
- **Task ID**: `T020`
- **Phase**: Stage 3 (Matching & Core Transactions)
- **Scope**: RELEASE
- **Date**: 2026-09-30
- **Environment**:
  - OpenJDK 17.0.20.1 LTS (Microsoft), Gradle 8.10.2, AGP 8.7.0, Kotlin 2.0.20
  - Jetpack Compose BOM 2024.09.02, Material 3 1.3.0
  - Android Jetpack Room 2.6.1 (`room-runtime`, `room-ktx`)
  - Google Stitch Project ID: `245073995801566548` (*SahiTol Collector Frontend*)

---

## Requirements and Acceptance Coverage

| Requirement | Test ID | Scope | Verification Status | Implementation & Evidence Notes |
|---|---|---|---|---|
| **R-GOV-02** | **AT-002** | RELEASE | Verified (T020) | Strict adherence to mandatory Google Stitch frontend gate: all 4 screens (`C06`, `C07`, `C08`, `C09`) built faithful to approved Stitch revisions in project `245073995801566548` without autonomous UI generation. Registered as `IMPLEMENTED_VERIFIED` in `design/stitch/SCREEN_REGISTRY.md`. |
| **R-PRICE-01** | **AT-016** | RELEASE | Verified (T020) | In-app field price observation entry implemented in `C06_PriceBoardScreen.kt` and `PriceRepository.kt`. Supports material selection, rate in paise, unit (kg, quintal, piece), mandi/location, and source attribution. Atomically commits to Room outbox (`CREATE_PRICE_OBSERVATION`) and append-only domain events with SHA-256 fingerprint. |
| **R-PRICE-02** | **AT-017** | RELEASE | Verified (T020) | Indicative weighted range and lot valuation in `PriceCalculator.kt` and `C07_ValuationScreen.kt`. Dynamically recomputes value range based on lot weight (kg) and material rate quantiles under PRICE_V1. Transparent condition and insulation deduction breakdown. Results clearly labeled "indicative market estimate". |
| **R-PRICE-03** | **AT-018** | RELEASE | Verified (T020) | Source confidence freshness and empty price handling in `C06` and `C07`. Displays confidence badges (HIGH, MEDIUM, LOW, INSUFFICIENT_DATA) and reason codes. Cached pricing age is explicitly badged ("Synced 10m ago", "Updated 2 days ago") with auto-reconcile notices. |
| **R-PRICE-04** | **AT-019** | RELEASE | Verified (T020) | 30-day historical trend indicators (+4.2%, -1.2%, stable) and min-max ranges in `C06`. Multiple active recycler offers in `C07` (Verma Electricals, City Kabadi, Patel Scrap) clearly distinguishing rate per kg vs fixed total. Expired and offline pending offers are prominently badged. |
| **R-REC-05** | **AT-025** | RELEASE | Verified (T020) | Explainable candidate ranking engine `MatchingEngine.kt` conforming strictly to MATCH_V1: 5-factor scoring (distance 30%, rate 30%, pickup 20%, availability 15%, reliability 5%) and deterministic tie-breaking (score descending, then facility ID string ascending). Verified against canonical shared fixtures. |
| **R-REC-06** | **AT-026** | RELEASE | Verified (T020) | Offline directory, map radar, and restricted GPS fallback in `C08_RecyclerDirectoryScreen.kt`. Operates 100% offline using cached directory data with freshness indicator. GPS location denial fallback enables manual locality selection (Dadar/Matunga, Mayapuri, Okhla, Kurla) without breaking route invariants. |
| **R-OFF-01** | **AT-038** | RELEASE | Verified (T020) | Complete offline capability across price discovery, valuation, directory, and offer review. All user actions (record observation, request facility, accept offer, counter offer) commit atomically to Room SQLite outbox with deferred synchronization. |

---

## 1. Implemented Components & Screen Inventory

### Architecture Overview
```
CollectorNavHost (Navigation Controller)
├── C06_PriceBoardScreen (Market Benchmarks, 30-day Trends, Field Observation Form)
├── C07_ValuationScreen (Indicative Range, Deduction Breakdown, Active Offers)
├── C08_RecyclerDirectoryScreen (Live Yard Radar, Filter Chips, Locality Fallback)
└── C09_RecyclerProfileOfferScreen (Compatibility Match, Commercial Offer, Request Lifecycle)
```

### Screen Details & Stitch Alignment
1. **`C06_PriceBoardScreen.kt`** (Stitch `3815df526486`):
   - Category filter tabs: All Materials, Cable (केबल), PCB (पीसीबी), Iron (लोहा), PET (प्लास्टिक).
   - Market rate cards with 30-day trend ranges, percentage changes (+4.2% up, -1.2% down, stable), yard locations (Delhi Central Yard, Okhla, Mayapuri, Seelampur), and last-updated timestamps.
   - Interactive field observation form: material selection, observed rate input, unit dropdown (kg, quintal, piece), mandi location, and source attribution.
   - Atomically records observations to local Room outbox (`CREATE_PRICE_OBSERVATION`) with SHA-256 payload digest.

2. **`C07_ValuationScreen.kt`** (Stitch `e975b81e8fd3`):
   - Lot summary header: Copper Cable Lot · 2.5 kg · Good Condition · Verified.
   - Estimated Value Range card: ₹ 425 – ₹ 475 based on 2.5 kg × ₹ 170–₹ 190/kg indicative market rate.
   - Expandable "Rate Basis & Evidence" section detailing base market copper blend rate and condition/insulation deductions.
   - Active commercial offers list:
     - **Verma Electricals**: ₹ 190/kg offered, ₹ 475.00 payout, Best Match chip, [Accept Offer / स्वीकार करें] and [Counter].
     - **City Kabadi Yard**: ₹ 170/kg offered, ₹ 425.00 fixed total payout.
     - **Patel Scrap Traders**: Saved offline, waiting to sync when cellular network restores.
   - Route compatibility notice and vehicle assignment (#UP-14-CZ-8891).

3. **`C08_RecyclerDirectoryScreen.kt`** (Stitch `f7a4946e02c1`):
   - Lot context banner with verified route indication.
   - Search bar with voice search mic icon.
   - Quick filters: All Eligible, < 3 km, Open Now, मराठी / हिंदी.
   - "Live Yard Radar" map simulation banner with "Recenter GPS" action.
   - Offline Cached Directory status with cache age and Refresh trigger.
   - Recycler facility cards (Shreeji Metal & Cable Yard, Navbharat Scrap Traders) with route distance, travel time, accepted specs, instant UPI support, operating hours, and [Navigate] CTA.
   - Restricted GPS / Offline locality fallback selector (Dadar/Matunga, Mayapuri, Okhla, Kurla).

4. **`C09_RecyclerProfileOfferScreen.kt`** (Stitch `d2ce8e021343`):
   - Header with verified recycler credentials: Verma Electricals, 99.4% Trust, Route Auth DL-408-C.
   - 100% Material Compatibility Match card (YOUR LOT vs ACCEPTED HERE).
   - Commercial offer terminal: ₹ 340.00 / kg rate, ₹ 850.00 estimated total payout, digital scale weighing basis.
   - Interactive request lifecycle simulator:
     - State 1: Ready to dispatch -> [Request / Send Lot (₹850.00)]
     - State 2: Request sent — Waiting for response
     - State 3: Offer received -> [Reject] or [Accept Offer]
     - State 4: Offline queued state with local outbox persistence
   - SahiTol Support toll-free helpline banner (1800-SAHI-TOL).

---

## 2. Automated Test Evidence

### Test Execution: `MatchingEngineTest.kt` & `PriceAndRecyclerViewsTest.kt`
Executed via `./gradlew testDebugUnitTest`:
```text
> Task :app:compileDebugKotlin
> Task :app:compileDebugUnitTestKotlin
> Task :app:testDebugUnitTest

BUILD SUCCESSFUL
```

### Verified Test Cases:
1. `haversineDistance_delhiMayapuriToOkhla_matchesFixtureWithinTolerance`:
   - Validates Haversine distance formula parity with PostGIS WGS84 geography within 0.5% tolerance.
2. `haversineDistance_mumbaiKurlaToThaneRabale_matchesFixture`:
   - Validates distance calculation for Mumbai-Thane corridor within tolerance.
3. `evaluateCandidate_batteryIsolationInvariant_blocksGeneralFacilities`:
   - Validates non-negotiable invariant: battery scrap lots (`BATTERY_ISOLATION`) are strictly blocked from general e-waste recyclers (`ROUTE_INCOMPATIBLE`).
4. `rankCandidates_deterministicTieBreaking_sortsScoreThenFacilityId`:
   - Validates deterministic sorting: score descending, then facility ID string ascending.
5. `evaluateCandidate_outsideSearchRadius_excludedWithDistanceExceeded`:
   - Validates 50 km boundary check (`DISTANCE_EXCEEDED`).
6. `getBenchmarks_allAndFilteredCategories`:
   - Validates benchmark retrieval and category filtering.
7. `calculateValuation_integerPaiseAndDeductionMath`:
   - Validates weight × rate valuation and integer paise precision.
8. `recordObservationAtomic_insertsOutboxAndDomainEvent`:
   - Validates atomic persistence of `CREATE_PRICE_OBSERVATION` into Room outbox with SHA-256 fingerprint.
9. `facilityRepository_directoryAndOfferResponses`:
   - Validates directory filtering, offer generation, and atomic `ACCEPT_OFFER` outbox persistence.

---

## 3. Acceptance continuation repair and device verification (2026-10-01)

The original C07 acceptance action persisted `ACCEPT_OFFER` locally, but displayed
its confirmation after the offer list. On a physical device that location was often
outside the viewport, so the action could appear to do nothing. This was reported
during the two-device handover check and reproduced on the collector device.

`C07_ValuationScreen` now routes the accepted lot directly to C10 Handover Capture
after the atomic repository operation completes. `CollectorNavHost` supplies that
explicit navigation callback.

Verification performed on collector device `N7OZPV59XWWKPF4X` (CPH2781, Android 16)
with the updated debug APK installed at 12:14 IST:

1. Opened C07 Valuation & Offers for the seeded Copper Wire / Cable lot.
2. Tapped the visible **Accept Offer / स्वीकार करें** control for Verma Electricals.
3. Confirmed immediate navigation to **Handover Capture / हस्तांतरण** (C10), with
   the lot reference, selected yard, offline-ready state, revised measured term,
   and Review / Accept / Dispute controls visible.

The focused Android unit suite also passed after the repair:

```text
./gradlew.bat --no-daemon :app:testDebugUnitTest \
  --tests "com.sahitol.collector.PriceAndRecyclerViewsTest" :app:assembleDebug

4 tests completed, 0 failed
BUILD SUCCESSFUL
```
