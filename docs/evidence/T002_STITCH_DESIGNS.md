# Test Evidence: T002 Obtain and Register Owner-Generated Stitch Designs

## Metadata
- **Task ID**: T002
- **Phase**: Stage 0 (Setup & Feasibility Gate)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Status**: DONE
- **Owner Notification Reference**: User prompt 2026-09-29T19:19:11: *"the project name is 'SahiTol Collector Frontend' with project id '245073995801566548'"*
- **Stitch Project ID**: `245073995801566548`
- **Stitch Project Name**: `projects/245073995801566548`
- **Design System Asset**: `assets_3d45108ad1d84d42ba28b62d52fc6e8f` (*SahiTol Design System*)

## Gate and Authority Verification
Per the mandatory frontend gate in `AGENTS.md` and `docs/05_DESIGN_STITCH.md`:
1. The project owner generated every screen in Google Stitch.
2. The agent did not autonomously design, edit, or substitute generic UI templates.
3. Upon receiving the owner's explicit notification, the agent connected via `StitchMCP` tools (`list_projects`, `get_project`, `list_screens`, `get_screen`).
4. Every screen asset, HTML structure, screenshot, and design system token was fetched, inspected, and verified against the canonical screen inventory in `docs/05_DESIGN_STITCH.md`.

## Inventory Coverage: 34 / 34 Required Specifications (37 Total Screens)

| Canonical Code | Canonical Title | Stitch Screen ID | Viewport | Target Surface | Covered States | Local HTML Asset |
|---|---|---|---|---|---|---|
| **S00** | Android feasibility diagnostic | `e2a3f1170e73` | 390 × 1258 | Android (Compose) | Camera permission, saved local row, offline inference result/error | `screens/S00_e2a3f117.html` |
| **C01** | Language / welcome / demo choice | `a98c85771874` | 390 × 861 | Android (Compose) | Hindi, Marathi, English; demo label; first launch offline | `screens/C01_a98c8577.html` |
| **C02** | Phone/PIN registration/login/profile | `a971f50d15e9` | 390 × 530 | Android (Compose) | Invalid PIN, throttled, offline continuation, reauth, privacy | `screens/C02_a971f50d.html` |
| **C03** | Collector home | `89622e073daa` | 390 × 1156 | Android (Compose) | Add lot, prices, directory, ledger, sync status, safety/economics entry | `screens/C03_89622e07.html` |
| **C04** | Photo capture/import | `83f516e48f1a` | 390 × 1112 | Android (Compose) | Camera denied, no photo, compressed preview, retake/delete | `screens/C04_83f516e4.html` |
| **C05** | Material/weight/condition lot editor | `afa6f950fa3a` | 390 × 1580 | Android (Compose) | Manual/unknown, AI suggestion/confidence/abstain/correction, draft vs submit | `screens/C05_afa6f950.html` |
| **C06** | Price board, trends & observation entry | `3815df526486` | 390 × 1958 | Android (Compose) | Category/region/unit, dated range, confidence/source, new observation form | `screens/C06_3815df52.html` |
| **C07** | Lot estimate and offer comparison | `e975b81e8fd3` | 390 × 1523 | Android (Compose) | Weight-based range, price basis, no offer/expired/accepted, source details | `screens/C07_e975b81e.html` |
| **C08** | Recycler directory/map | `f7a4946e02c1` | 390 × 1453 | Android (Compose) | Offline list, online map, permission denied, no match, filter/widen area | `screens/C08_f7a4946e.html` |
| **C09** | Facility details/request/offer | `d2ce8e021343` | 390 × 1430 | Android (Compose) | Role, route authorization, validity, materials/pickup/rates, request/accept/reject | `screens/C09_d2ce8e02.html` |
| **C10** | Handover capture/review | `b389d91e2be7` | 390 × 1141 | Android (Compose) | Actual weight/photo/location, missing evidence, terms changed, save pending | `screens/C10_b389d91e.html` |
| **C11** | QR and Digital Handover Record | `b41f09f64e78` | 390 × 1077 | Android (Compose) | Pending on phone, synced pending recycler, confirmed, disputed; share/PDF | `screens/C11_b41f09f6.html` |
| **C12** | Earnings and dues | `b8d0dde3a3bf` | 390 × 1401 | Android (Compose) | Gross/acknowledged paid/pending, monthly filter, demo, empty | `screens/C12_b8d0dde3.html` |
| **C13** | Payment/transaction detail | `fa4f9d475fed` | 390 × 1191 | Android (Compose) | Cash/UPI assertion, partial, acknowledgement, dispute/reversal, pending sync | `screens/C13_fa4f9d47.html` |
| **C14** | Sync centre (2 variants) | `565a8be33852`, `3f09445d4d5d` | 390 × 1554 / 1344 | Android (Compose) | Queue/retry/conflict/repair/auth-required/progress and safe logout | `screens/C14_565a8be3.html`, `screens/C14_3f09445d.html` |
| **C15** | Settings/help/privacy (2 variants) | `786c12e6beec`, `7bd4f59f2447` | 390 × 1244 / 1703 | Android (Compose) | Locale/audio repeat/mute, offline profile, export/deletion request, demo isolation | `screens/C15_786c12e6.html`, `screens/C15_7bd4f59f.html` |
| **C16** | Material passport/timeline | `a1e7f356962f` | 390 × 1391 | Android (Compose) | Collection->offer->handover->receipt->payment, provenance and linked revisions | `screens/C16_a1e7f356.html` |
| **C17** | Contextual safety library/detail | `1579fe53bac5` | 390 × 1453 | Android (Compose) | CRT/PCB/cable/battery/mixed warning, hi/mr audio, unknown route | `screens/C17_1579fe53.html` |
| **R01** | Recycler login/dashboard/inbox | `a865adccea0c` | 1280 × 1589 | Web (React) | Role-scoped requests, new/accepted/rejected/expired, no requests | `screens/R01_a865adcc.html` |
| **R02** | Incoming lot details | `cd9fc4569350` | 1280 × 1062 | Web (React) | Photo permission/access error, material/weight/source, no fabricated grade | `screens/R02_cd9fc456.html` |
| **R03** | Quote/accept/reject | `c801123f869c` | 1280 × 1112 | Web (React) | Rate vs fixed total, validity, conflict, confirmation of final terms | `screens/R03_c801123f.html` |
| **R04** | QR scan / reference entry | `3fab97e50ca5` | 1280 × 1006 | Web (React) | HTTPS camera denied, unknown/not synced, hash mismatch, wrong facility | `screens/R04_3fab97e5.html` |
| **R05** | Receipt and payment review | `531b40d150ac` | 1280 × 1105 | Web (React) | Measured differences, collector acknowledgement, duplicate, dispute, partial paid | `screens/R05_531b40d1.html` |
| **R06** | Operational profile | `d8a4014f59f6` | 1280 × 1236 | Web (React) | Material/service area/pickup/rate updates; immutable admin verification evidence | `screens/R06_d8a4014f.html` |
| **R07** | History/procurement exports (2 variants) | `ed5141147b18`, `8bd5903f0e8d` | 1280 × 1653 / 1812 | Web (React) | Filters, status, PDF/CSV, empty and access denied | `screens/R07_ed514114.html`, `screens/R07_8bd5903f.html` |
| **A01** | Admin overview | `71b92d85be06` | 1280 × 1476 | Web (React) | Provenance/time/region filters, last refresh, failed query vs zero | `screens/A01_71b92d85.html` |
| **A02** | Collector minimal records | `cf27fa7d1b9e` | 1280 × 1109 | Web (React) | Alias/region/activity; restricted PII; no Aadhaar/bank fields | `screens/A02_cf27fa7d.html` |
| **A03** | Facility/source verification | `765fb854e571` | 1280 × 1824 | Web (React) | L0-L4 evidence, expiry/route review, rejected/quarantined imports | `screens/A03_765fb854.html` |
| **A04** | Prices/materials/aliases/safety maintenance | `002314460537` | 1280 × 1108 | Web (React) | Source field editing, revisions, moderation, translation gaps | `screens/A04_00231446.html` |
| **A05** | Transaction & traceability search | `955f1fae56d1` | 1280 × 1520 | Web (React) | Event chain, disputes, source records, redacted exports | `screens/A05_955f1fae.html` |
| **A06** | Data quality review | `cc1d29b9cd39` | 1280 × 1448 | Web (React) | Missing/invalid/stale/duplicate/inconsistent flags, drilldown, resolution reason | `screens/A06_cc1d29b9.html` |
| **A07** | Research/data/model evidence | `31e72965669b` | 1280 × 1902 | Web (React) | Seven dataset cards/exports, desk-research cards, model metrics, limitations | `screens/A07_31e72965.html` |
| **V01** | Public verification | `2d32708a9c8a` | 1280 × 1088 | Web (React) | Minimal pending/confirmed/disputed/not-found/hash-mismatch; login for details | `screens/V01_2d32708a.html` |
| **U01** | Unit economics | `cab89a974c04` | 1280 × 1076 | Web (React) | Editable assumptions, current/platform net, costs/delta, source and illustrative label | `screens/U01_cab89a97.html` |

## Local Artifacts and Handoff Registration
1. **Design System Tokens ([`design/stitch/DESIGN.md`](../../design/stitch/DESIGN.md))**:
   - Palette: Terracotta Primary (`#9f3c16`), Primary Container (`#bf542c`), Warm Surface (`#fcf9f3`), Surface Variant (`#e5e2dc`), Secondary Yellow/Amber (`#735c00`).
   - Typography: Headlines in **Sora** (xl 36px, lg 28px, md 20px), Body & Labels in **Plus Jakarta Sans** (18px, 16px, 14px).
   - Touch Targets: Min 48px touch targets specified for mobile collectors.
2. **Screen Assets ([`design/stitch/screens/`](../../design/stitch/screens/))**:
   - Complete HTML representations and PNG preview screenshots downloaded locally for all 37 screens.
   - Asset manifest: [`design/stitch/manifest.json`](../../design/stitch/manifest.json).
3. **Screen Registry ([`design/stitch/SCREEN_REGISTRY.md`](../../design/stitch/SCREEN_REGISTRY.md))**:
   - All 34 canonical screen specifications transitioned from `REQUESTED` to `REVIEWED_READY`.
   - Gate satisfied; downstream UI implementation tasks (`T003`, `T013`, `T015`, `T017`, `T020`, `T022`, `T024`, `T025`, `T027`, `T030`, `T031`, `T034`, `T036`, `T037`, `T039`) are unblocked.
