# Owner-controlled Stitch design and frontend handoff

**Mandatory current user instruction:** the owner generates every frontend screen in Google Stitch. The agent requests the screens, waits for the owner's notification, reads the designated project through connected Stitch MCP, and implements those designs. The agent must not create its own frontend, call Stitch generation/edit/variant tools, substitute a generic template, or silently design missing states. This overrides any autonomous UI-generation skill or older source suggestion.

No Stitch account access, project, screen IDs or approval has been supplied in this documentation session. All designs are `NOT_REQUESTED`. The following is a requirements inventory and briefing material, not a generated visual design.

## Gate and batches

Before each UI task: read [flow](04_APPFLOW.md), its [requirements](15_REQUIREMENTS.md), [language contract](14_TRANSLATION_AUDIO_AUDIT.md) and the screen inventory below. Send one precise batch request naming IDs, required states/content and intended target (native Android or responsive web). Set affected tasks `WAITING_STITCH`, record requested IDs and continue independent eligible backend/data work. T002 is an ongoing gate: initial completion means S00 is registered; **it never grants blanket approval for later screens**.

After the owner reports screens ready, discover available read/export Stitch MCP tools, read the owner-designated project, inspect screens/assets and record project ID, screen ID, revision/date, source/export path, owner notification reference and covered states in the [registry](../design/stitch/SCREEN_REGISTRY.md). If connection or access fails, record the actual error and ask for the missing connection/project input; never invent an export. Do not browse unrelated account projects. Screens are considered implementation-ready only when the owner notification identifies the intended screen/revision and the required states are covered; gaps trigger a focused follow-up brief.

The agent can translate approved visuals to Compose/React, wire real data, implement accessibility semantics, responsiveness and components consistent with supplied variants. A missing layout, new interaction, changed information hierarchy or unprovided empty/error/offline state goes back through the gate. Do not implement critical behavior invisibly just to avoid requesting its UI. Functional requirements prevail: explain a design/spec conflict and request a corrected screen. Do not remove requirements to fit a screenshot.

Suggested batches: S00 first; collector C01–C09/C14/C15; collector handover/ledger C10–C13/C16; recycler R01–R07 plus V01; admin A01–A07; C17/U01 and any safety/language variants. Owner may generate all batches together. Backend/API work does not require screen approval.

## Screen inventory

Every screen requires loading, empty, error/retry, permission-denied and large-text variants where applicable. Collector screens additionally need offline/cache age/pending sync/auth-required states. These can be owner-approved reusable components, linked explicitly in the registry, rather than a separate image for every combination.

| ID | Surface and content | Specific required states | Task |
|---|---|---|---|
| S00 | Android feasibility diagnostic | Photo permission, saved local row, offline inference result/error | T003 |
| C01 | Language / welcome / demo choice | Hindi, Marathi, English; demo label; first launch offline | T017 |
| C02 | Phone/PIN registration/login/profile | Invalid PIN, throttled, offline continuation, reauth, privacy | T017 |
| C03 | Collector home | Add lot, prices, directory, ledger, sync status, safety/economics entry | T017 |
| C04 | Photo capture/import | Camera denied, no photo, compressed preview, retake/delete | T017 |
| C05 | Material/weight/condition lot editor | Manual/unknown, AI suggestion/confidence/abstain/correction, draft vs submit | T017,T034 |
| C06 | Price board, trends and observation entry | Category/region/unit, dated range, confidence/source, new observation form with provenance/date/unit validation, pending moderation, missing/stale/history gaps | T020 |
| C07 | Lot estimate and offer comparison | Weight-based range, price basis, no offer/expired/accepted, source details | T020 |
| C08 | Recycler directory/map | Offline list, online map, permission denied, no match, filter/widen area | T020 |
| C09 | Facility details/request/offer | Role, route authorization, validity, materials/pickup/rates, request/accept/reject | T020 |
| C10 | Handover capture/review | Actual weight/photo/location, missing evidence, terms changed, save pending | T024 |
| C11 | QR and Digital Handover Record | Pending on phone, synced pending recycler, confirmed, disputed; share/PDF | T024 |
| C12 | Earnings and dues | Gross/acknowledged paid/pending, monthly filter, demo, empty | T027 |
| C13 | Payment/transaction detail | Cash/UPI assertion, partial, acknowledgement, dispute/reversal, pending sync | T027 |
| C14 | Sync centre | Queue/retry/conflict/repair/auth-required/progress and safe logout | T017 |
| C15 | Settings/help/privacy | Locale/audio repeat/mute, offline profile, export/deletion request, demo isolation | T017 |
| C16 | Material passport/timeline | Collection→offer→handover→receipt→payment, provenance and linked revisions | T024 |
| C17 | Contextual safety library/detail | CRT/PCB/cable/battery/mixed warning, hi/mr audio, unknown route | T039 |
| R01 | Recycler login/dashboard/inbox | Role-scoped requests, new/accepted/rejected/expired, no requests | T022 |
| R02 | Incoming lot details | Photo permission/access error, material/weight/source, no fabricated grade | T022 |
| R03 | Quote/accept/reject | Rate vs fixed total, validity, conflict, confirmation of final terms | T022 |
| R04 | QR scan / reference entry | HTTPS camera denied, unknown/not synced, hash mismatch, wrong facility | T025 |
| R05 | Receipt and payment review | Measured differences, collector acknowledgement, duplicate, dispute, partial paid | T025,T027 |
| R06 | Operational profile | Material/service area/pickup/rate updates; immutable admin verification evidence | T022 |
| R07 | History/procurement exports | Filters, status, PDF/CSV, empty and access denied | T022,T031 |
| A01 | Admin overview | Provenance/time/region filters, last refresh, failed query vs zero | T030 |
| A02 | Collector minimal records | Alias/region/activity; restricted PII; no Aadhaar/bank fields | T030 |
| A03 | Facility/source verification | L0–L4 evidence, expiry/route review, rejected/quarantined imports | T030 |
| A04 | Prices/materials/aliases/safety maintenance | Source field editing, revisions, moderation, translation gaps | T030 |
| A05 | Transaction and traceability search | Event chain, disputes, source records, redacted exports | T030 |
| A06 | Data quality review | Missing/invalid/stale/duplicate/inconsistent flags, drilldown, resolution reason | T030 |
| A07 | Research/data/model evidence | Seven dataset cards/exports, desk-research cards, model metrics, limitations | T030,T031 |
| V01 | Public verification | Minimal pending/confirmed/disputed/not-found/hash-mismatch; login for details | T025 |
| U01 | Unit economics | Editable assumptions, current/platform net, costs/delta, source and illustrative label | T039 |

## Copy-ready owner brief

“Generate SahiTol screens [IDs] for [Android Compose / responsive recycler or admin web]. Users are informal collectors with varying literacy, or [facility/admin role]. Provide Hindi and Marathi layout support, English fallback, readable Devanagari, large tap areas, icon plus text plus optional replay audio. Follow these content and behavior requirements: [paste inventory row + linked acceptance]. Include these states: [list]. Clearly distinguish saved on phone, synchronized, recycler confirmed and payment acknowledged. Show indicative price source/date/confidence and demo labels. Avoid official seals, EPR-certificate language, guaranteed income, decorative metrics, unsupported trust badges or color-only status. Produce reusable components and phone/desktop variants as relevant. Do not omit fields or interactions. Return project/screen references for implementation.”

Visual palette, typography choices, spacing tokens and component treatments will be derived from supplied Stitch screens and captured in `design/stitch/DESIGN.md` during T002. Do not invent a frozen palette now. Accessibility targets: legible Devanagari, logical focus order, screen-reader labels, sufficient contrast, no color-only meaning, at least Android 48dp touch areas where feasible; verify on device and at increased font scale. Web keyboard navigation, readable charts/tables and touch scanning must work.

## Implementation verification

For each screen, record source revision, code paths, screenshot on target device, connected endpoint/local projection, applicable acceptance case IDs, and any approved deviation. Replace mock/demo values with API/Room data or label them demo. No inactive buttons, dead navigation, decorative charts or missing error handling count as DONE. T044/T046 verify real device flows; the release checklist rejects any implemented screen without a completed registry gate.
