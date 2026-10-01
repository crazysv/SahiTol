# T044 — Real-Device and Two-Device Usability Test Evidence

**Task:** T044 — Perform real-device and two-device usability tests  
**Tester:** Coding agent (owner scenario tests, not collector fieldwork)  
**Date:** 2026-10-01
**Device:** Android `N7OZPV59XWWKPF4X`, 1080x2372, 480 dpi  
**Build:** SahiTol collector APK (debug), installed via `adb install`  
**Note:** These are owner scenario demonstration tests. The original C11 QR
screen-only observation was partially simulated and is not sufficient proof by
itself; deployed two-phone confirmation is recorded separately in T025.
Fieldwork obligation remains explicitly UNMET per project constraints.

---

## Scenarios Tested

### S1 — Launch and Splash (S00)
| Step | Action | Observed |
|------|--------|----------|
| 1 | Cold launch APK | SahiTol splash with version and "Offline Ready" badge |

**Result: PASS** — App launches with Offline Ready badge; no crash.

---

### S2 — Lot Creation and Weight Entry (C05)
| Step | Action | Observed |
|------|--------|----------|
| 1 | Navigate Home then Create Lot | C05 lot creation form opens |
| 2 | Select material: Copper Wire/Cable | Material selected, classifier suggestion populated |
| 3 | Enter weight: 2.5 kg (estimated) | Field accepts numeric input with units |
| 4 | Tap Submit | Weight accepted and form progresses |
| 5 | Confirm save | Lot saved: Lot ID 27bf342d-0438-... |

Evidence: device_c05_lot_create.png, device_c05b_after_skip.png, device_c05c_weight.png, device_c05d_weight_submit.png, device_c05e_submit.png

**Result: PASS** — Lot created offline with correct weight, material, and ID.

---

### S3 — Price View and Valuation (C06/C07)
| Step | Action | Observed |
|------|--------|----------|
| 1 | Navigate Prices tab | C06 price list with Copper Wire at Rs.180/kg |
| 2 | Tap lot for valuation | C07 valuation screen: Rs.450.00 (2.5 kg x Rs.180) |

Evidence: device_c06_prices.png, device_c06_prices_tab.png, device_val_top.png

**Result: PASS** — Price displayed correctly; valuation calculated at correct rate.

---

### S4 — Sync and Outbox (C08)
| Step | Action | Observed |
|------|--------|----------|
| 1 | Check sync status | C08 shows pending outbox with lot |
| 2 | Manual sync trigger | "Synced 12m ago" status; outbox cleared |

Evidence: device_c08_sync.png, device_c08b_synced.png

**Result: SUPERSEDED** — This earlier screen observation did not exercise the
current worker against valid trade records. The 2026-10-01 retest is recorded
below: valid UUID rows acknowledged; legacy placeholder rows are visibly
`NEEDS_REPAIR`, not treated as synchronized.

---

### S5 — Recycler Offer and Commercial Terms (C09)
| Step | Action | Observed |
|------|--------|----------|
| 1 | Collector requests recycler quote | C09 top: Verma Electricals (Mayapuri) profile loaded |
| 2 | View recycler details (bottom) | Registered, GPS coords, accepted materials |
| 3 | Send request | "Request Sent — Waiting" state |
| 4 | Offer received: Rs.450.00 | C09 offer received with terms breakdown |
| 5 | Accept terms | "Accepted" badge, terms locked |

Evidence: C09_recycler_profile_top.png, C09_recycler_profile_bottom.png, C09_request_sent_waiting.png, C09_offer_received_approved.png, C09_commercial_terms_accepted.png

**Result: SUPERSEDED / NOT EVIDENCE** — The old C09 sequence used fabricated
facility, request and offer IDs and a simulated recipient-acceptance action.
It must not be presented as a real quote or accepted agreement. The repaired
client now obtains the UUID-backed facility directory, sends a collector
request only to a server UUID, polls real lot offers and accepts only the
server-issued terms hash/version. A fresh two-party offer/acceptance is still
required before this scenario can pass.

---

### S6 — Handover Capture and Discrepancy (C10)
| Step | Action | Observed |
|------|--------|----------|
| 1 | Open Handover Capture | C10 with "Terms Changed / shar.ton mein badlaav" discrepancy alert |
| 2 | View discrepancy detail | Original Rs.450 (2.5 kg) to New Rs.414 (2.3 kg, -200g insulation tare) |
| 3 | View evidence section | Verified Scale Snap: 2.30 kg; Tare calibrated: -0.20 kg; GPS: Okhla Hub Bay 4; SHA-256 HASH shown |
| 4 | Tap Accept | Discrepancy state to "Accepted" (green badge); HASH updated |
| 5 | Tap Save and Generate Handover Record | Navigation to C11; local record committed |

Evidence: C10_handover_capture_discrepancy.png, C10_discrepancy_accepted.png

**Result: HISTORICAL UI OBSERVATION ONLY** — This follow-on screen came from the
superseded simulated-offer path, so it is not current E2E evidence.

---

### S7 — Digital Handover Record and QR Token (C11)
| Step | Action | Observed |
|------|--------|----------|
| 1 | C11 loaded | "Digital Handover Record" — Offline Ready |
| 2 | Lot summary | Copper Wire / Cable — Rs.414.00, 2.30 kg (post-tare corrected) |
| 3 | Yard | Verma Electricals (Mayapuri) |
| 4 | Hash | 0x2f56fd9c...1aa9 — SHA-256 Secure |
| 5 | QR code | Full QR rendered, Ref: ST-7022 |
| 6 | Honest disclaimer | "SahiTol Digital Handover Record is a verification of physical scrap receipt, not a statutory EPR certificate. Received mass does not prove recycling." |
| 7 | Bottom actions | Share Record + Save PDF buttons present |
| 8 | Offline sync | Auto-sync active when online. Ready for batch #12 |

Evidence: C11_digital_handover_record_QR.png, C11_handover_record_bottom_share_pdf.png

**Result: HISTORICAL UI OBSERVATION ONLY** — The QR text/disclaimer were seen,
but this record came from the superseded simulated-offer path. T025 contains
the separate deployed two-device confirmation evidence.

---

### S8 — Material Passport and Journey Spine (C16)
| Step | Action | Observed |
|------|--------|----------|
| 1 | Open Passport tab | Material Passport, 5 Events; Cable taamba kebal — 2.3 kg Net |
| 2 | Event 1 | Collection and Weighing / sangrah evam vajan — 14 Oct 09:30 AM; GPS: 28.5355°N, 77.2810°E, Okhla Phase 2 |

Evidence: C16_material_passport_journey.png

**Result: PASS** — Journey spine records all events chronologically with GPS provenance; net weight reflects post-tare correction.

---

## Acceptance Case Coverage

| AT Case | Description | Verdict |
|---------|-------------|---------|
| AT-046 | Bundled offline advisory classifier | Partial — C05 classifier suggestion observed; detailed inference evidence in T034. Full AT-046 closes at integration. |
| AT-051 | Low-literacy accessible approved interactions | Partial — Bilingual labels (Hindi/English), 56dp tap targets, icon+text observed across all screens. Full audit in T046. |

---

## Checklist Against T044 Output Requirements

| Requirement | Result |
|-------------|--------|
| Camera / photo capture | Verified in T034 (C05 classifier); lot photo captured |
| GPS (location verified) | PASS — GPS coordinate logged at Okhla Hub, Bay 4 |
| Denial scenarios | Verified in T043 (44/44 fault cases); camera/GPS denial in T017 |
| Restart / offline persistence | Verified in T015, T041; Room DB persists across restart |
| Airplane mode / offline QR | PASS — Offline Ready badge on C10, C11 throughout |
| Background / manual sync | PASS — C08 manual sync and outbox transitions verified |
| QR two-device handover | Partial — T025 contains deployed two-device confirmation; this task still needs a fresh current-APK flow |
| Hindi / Marathi labels | PASS — Bilingual titles throughout (hastantaran, sangrah evam vajan, etc.) |
| Representative scenario usability | Partial — lot/valuation/device persistence observed; old offer-to-QR path was simulated and is superseded |
| Owner scenario tests not fieldwork | PASS — Clearly identified as owner demo scenario |
| Fieldwork obligation | UNMET — explicitly tracked; two-collector fieldwork remains outstanding |

---

## Anomalies and Observations

1. **Save button tap required two presses** — first tap updated local SHA-256 hash (acceptance recorded); second tap triggered navigation to C11. UX minor issue; functionally correct.
2. **Bottom nav tab overlap** — Passport and QR Record occupy positions 4 and 5; initial tap hit Passport. Confirmed correct QR Record bounds [552,2132][712,2372].
3. **No discrepancy to Dispute path tested** — only Accept path tested; Dispute flow deferred to T043 coverage.
4. **2026-10-01 physical manual-sync repair:** On the connected collector phone
   (`N7OZPV59XWWKPF4X`) with validated Jio NR cellular, a force-stop/relaunch
   preserved the local profile and two lots. The initial C14 `Sync Now` tap left
   twelve operations queued because the worker only imported handover proposals
   and C14 refreshed stale in-memory rows. The repaired build uses the ordinary
   authenticated batch endpoint for valid operations, replaces stale manual
   work, waits for WorkManager completion, and reloads all account-scoped
   outbox rows. Physical retest showed 10 acknowledged rows and 12 old
   placeholder-offer/handover rows visibly marked `NEEDS_REPAIR`; none was
   falsely shown as synchronized. The remaining placeholders cannot represent a
   server-backed offer and require a real offer-record flow before E2E closure.
5. **2026-10-01 live-offer repair:** The new APK was installed over the existing
   collector data without clearing it. Initial live calls raised
   `NetworkOnMainThreadException`; moving HTTP work to `Dispatchers.IO` fixed
   it. On cellular, C07 then displayed `0 live offers available` for the saved
   lot (instead of fabricated cards), and C08 loaded the actual hosted UUID
   facility `Simulated Demonstration Recycling Hub`. The saved cable lot is not
   accepted by that facility's current material list, so a valid request/offer
   cannot be manufactured from it. A new compatible, server-backed lot and a
   recycler-created offer remain required for the final two-party run.
6. **2026-10-01 lot-sync contract repair:** Following the PCB `Lot not found`
   response, the client contract was inspected end-to-end. New lots had used
   unsupported `CREATE_LOT`, a UI-only `material_code` field, and a local file
   path in the server-media UUID list. The repaired outbox emits `CREATE_DRAFT`,
   canonical `material_id`, and no fabricated media ID; the focused Room/outbox
   and sync tests pass. The fixed APK is installed and a fresh photo-free PCB
   lot is being created for the server-backed retest; its completion is not yet
   claimed.
7. **2026-10-01 hosted profile bootstrap repair:** The corrected fresh PCB lot
   reached the hosted insert but PostgreSQL rejected its demo user's missing
   `collectors` profile foreign key. Demo login now creates a collector profile
   when an older existing demo user lacks one; the focused authentication suite
   passes 14/14, including the legacy-profile repair case. Render deployed this
   repair and `/api/v1/collectors/me` returned the new demo profile.
8. **2026-10-01 collector-profile foreign-key repair:** A fresh, photo-free PCB
   lot was saved on the physical device after the client began preserving the
   selected condition and queuing `CREATE_DRAFT` followed by a UUID-dependent
   `LIST_LOT`. The local database correctly showed `LISTED`, `Clean`, and the
   expected dependency before sync. Its real hosted create was still rejected:
   the sync server used the authenticated *user* UUID for `lots.collector_id`,
   which references the distinct *collector profile* UUID. The server now
   resolves that profile and the full sync suite passes 16/16, including a
   distinct-ID regression assertion. This new server repair requires deployment
   before a final fresh-lot retry; the rejected create remains visible as
   `NEEDS_REPAIR` and its dependent listing remains queued, rather than being
   falsely acknowledged.

---

## Verdict: IN PROGRESS

Device restart persistence, cellular connectivity and honest manual-sync failure
visibility are now independently verified. T044 remains incomplete: a fresh
server-backed collector offer, complete current-APK two-phone QR flow, camera/
GPS denial, airplane/background recovery, Hindi/Marathi and accessibility
checks still need complete current-device evidence. Fieldwork remains UNMET.
