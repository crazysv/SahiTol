# Current handoff

## 2026-10-04 completed quote explanation and duplicate-offer boundary

Live inspection of the recycler quote route for the 13 kg PCB test record
showed request `1083a07a-e833-438a-acbe-c5a32ae441e4` in `ACCEPTED` state with
its ₹2,340 offer accepted. The dispatch control was disabled correctly but
looked non-responsive because R03 supplied no explanation. R03 now renders a
clear accepted/active/closed state instead of the dispatch controls. The API
also returns HTTP 409 if a pending request already has an `OPEN` offer, so a
reload or direct retry cannot create a duplicate. Focused trade tests pass.
Commit `94dc0b2` is deployed. The exact record was reloaded at
`sahitol.pages.dev`: it visibly states **This offer has already been accepted**
and exposes only **Return to Inbox** and **View History**. The stale disabled
dispatch control is gone. Continue remaining manual workflow checks only with
a new pending collector request; do not reuse this finalized test record.

## 2026-10-04 end-to-end live offer and handover trace in progress

Commit `aec2450` is deployed to Pages and Render. A live collector lot
`a9ed8a4b-7e3b-4982-93e6-761b0f5b0e29` (PCB, 13 kg) now appears in the recycler
inbox with the exact same material and mass. The browser's R02 inspection and
R03 quote views were exercised against it and preserved that identity; a live
₹2,340 offer at ₹180/kg was issued. On CPH2781, **Refresh live offers**
retrieved the same ₹2,340 offer, and acceptance loaded the matching 13 kg
server agreement. A pending server handover `ST-EFDB28` was generated and its
collector QR record renders correctly.

Testing also found that R04's manual reference fallback never supplied a
handover ID, leaving **Verify with Server** disabled. It is repaired locally:
`GET /api/v1/handovers/lookup?reference=ST-XXXXXX` resolves the printed
six-character reference for an authorized recycler, and R04 uses it to enter
the verified confirmation state. The focused API test and web production build
pass. Next action: commit/push/deploy this repair, verify `ST-EFDB28` through
the scanner fallback, then request the owner's action-time confirmation before
recording the recycler's final receipt confirmation.

The owner then confirmed the live receipt action. The recycler browser shows a
server-backed confirmed receipt for `efdb28c3-5bb8-44d5-b70a-2736304a42b7`:
MAT-PCB-01, 13.00 kg received, ₹2,340.00 agreed value, and the matching
SHA-256 seal. Returning to C10 on CPH2781 refreshed the saved proposal and
showed **Recycler Handover Confirmed — Receipt ST-EFDB28 has been confirmed by
the recycler.** This establishes the full deployed collector → recycler offer
→ agreement → QR reference verification → recycler confirmation path for one
real demo record. It is evidence for this record only; separate device,
accessibility, performance, and release-artifact checks remain distinct.

## 2026-10-04 live counterparty and recycler-payload repair staged

End-to-end tracing found two separate faults behind a collector/recycler
mismatch. The Android live directory currently returns facility
`uuid5(NAMESPACE_DNS, "fac-sim-01")`, but a legacy hosted membership could make
the recycler demo login select an older synthetic facility instead. A phone
request could therefore be successfully created yet not appear in the browser
inbox. `trade.get_user_facility` now binds the demo recycler operator to the
current deterministic synthetic facility; `handovers.py` uses the same ID.

The recycler `R02` and `R03` screens also contained unrelated hard-coded cable,
weight and collector data. They now fetch the exact request selected from R01,
carry its request ID into the quote route, render server values, and block an
offer if that request cannot be found or is no longer pending. Focused API
tests (21) and `npm run build` pass locally. The prior Vitest command remains
unsuitable as a final gate because its existing query polling keeps the runner
open; its renderer fixtures have been updated but require a bounded runner
configuration. Next action: commit/push, wait for Render/Pages, then re-run a
real phone request through the browser quote and collector refresh before
claiming cross-surface verification.

## 2026-10-04 recycler inbox route repair published and verified

The Recycler console's actual inbox route is `/recycler`; the formerly
documented `/recycler/inbox` route had no matching React route and therefore
correctly produced a blank root rather than an inbox. Added a compatibility
redirect from `/recycler/inbox` to `/recycler`. Commit `4c26ef3` was pushed and
the deployed alias was verified: it redirects to `/recycler` and renders
**Yard Dashboard & Material Inbox**. The collector and recycler browser
workflow can now be retested.

## 2026-10-04 recycler offer-console integration published; device offer verification pending

Physical collector testing confirmed that C09's request endpoint succeeds, but
the deployed recycler R01/R03 web console was presentation-only: its inbox was
static and its dispatch action only changed browser state. The existing approved
R01 and R03 visuals are now wired locally to the real recycler incoming queue
and `POST /api/v1/requests/{request_id}/offers`; they use a fresh recycler demo
token, render API errors, and pass the server request ID and verified weight to
the quote terminal. Commit `0829962` was pushed to `main`, and the deployed
`https://sahitol.pages.dev/recycler/inbox` bundle returned HTTPS 200 and
contained the new live-inbox code. The actual browser-to-API offer creation and
collector-side refresh still require a final live device/browser run; do not
claim cross-surface offer completion until that run is recorded.

## 2026-10-04 automatic lot sync checkpoint

C05 now calls `SyncWorker.enqueueAutomaticSync` only after
`LotRepository.createLotAtomic` has committed the lot and its durable outbox
operations. The worker requires a connected network, so an offline save is
never lost or blocked; it remains `SAVED_LOCAL_ONLY` until Android can run the
worker, and C14 **Sync Now** remains an explicit recovery action. The app's
existing Room lot flow refreshes C07 when the server acknowledgement changes
the state to `SYNCED`.

The rebuilt debug APK was installed over the existing collector data on
CPH2781. A manual no-photo PCB save went straight to C07 and displayed
**Synced** after the automatic worker completed; no visit to C14 was used.
Android unit tests and debug assembly passed.

## 2026-10-04 live directory and lot-to-offer display repair

Physical phone testing found that C08 could route a collector from an offline
cached reference facility into C09. Those records have non-server IDs and must
never accept a recycler request. C08 now distinguishes the live directory from
the browse-only reference directory, disables reference cards, and states the
required refresh action. C09 now receives the selected `LotEntity` from the
navigation host and displays that lot; its former hard-coded cable/₹850
“offer” has been replaced with an explicit no-offer-yet state.

On CPH2781, the newest synced PCB lot (15 kg) was rechecked: C07 **View
Directory** → C08 **Live Recycler Directory** → the live demo facility → C09
**Request recycler offer**. The request visibly reached **Request sent —
Waiting for response**. This is the correct collector-side stopping point:
the next state requires a recycler-created server offer.

## 2026-10-03 manual-sync authentication recovery and live offer request

Physical testing on `N7OZPV59XWWKPF4X` (CPH2781) found five valid local lot
create/list operations stranded in `AUTH_REQUIRED` after a temporary hosted
authentication failure. C14's manual worker authenticated successfully but
only loaded `QUEUED`/`RETRY_WAIT` rows, so it reported no sendable work and the
newly saved lots stayed local. `SyncWorker` now requeues only the active
account's `AUTH_REQUIRED` rows after obtaining a fresh demo token; validation
failures remain `NEEDS_REPAIR` and are never silently retried or deleted.

The rebuilt debug APK was installed over the existing app without clearing
data. A live phone sync acknowledged all ten create/list operations for the
five valid lots. The newest PCB lot `fa2791c5-…` is now `SYNCED`, `LISTED`,
server version 2. Reopening it through C07/C08/C09 and tapping **Request
recycler offer** visibly produced **Request sent — Waiting for response** for
the live demo facility. The remaining 13 historic `NEEDS_REPAIR` entries stay
visible as action-required records and are not evidence of an unsynced lot.
`:app:testDebugUnitTest` and `:app:assembleDebug` passed. The next genuine
workflow step is recycler-side creation of a live offer, followed by the
collector's Refresh live offers action.

## 2026-10-03 C07 visual regression checkpoint

The approved C07 Valuation & Offers Compose layout was corrected after a
physical-device screenshot exposed a nested weighted-row measurement defect:
the top bar expanded to approximately 1,152 px and left a large blank region.
The title row is now flattened, the offline badge has stable width, and lot
title/detail text may wrap to two lines. On `N7OZPV59XWWKPF4X` (CPH2781,
1080x2372), the rebuilt APK was installed without clearing data; the UI dump
reported top bar y=0..336 and content y=336, and the valuation/evidence cards
were visible in the live screenshot. `:app:testDebugUnitTest` and
`:app:assembleDebug` passed. No functional or release-evidence scope changed.

## 2026-10-02 v2 classifier integration checkpoint

The owner authorized integration of the previously validated two-source
`mendeley_plus_openimages_v1` model. The exact float32 TFLite export is now
bundled in both model asset locations with SHA-256
`32098e6714ea806ecfdf0d87e848aa394ac3d852c81989ecae33f0e142e5438f` and size
3,762,528 bytes. Android uses provider-label order, `[-1,1]` normalization,
threshold `0.52`, and model version `v2.0-mendeley-openimages`.

Safe mapping is intentionally narrow: only Keyboard/Mobile/Mouse may be
confirmed as broad MIXED electronics. Battery, PCB, plastic, metal, glass,
medical, organic, paper, and light-bulb provider labels remain manual-only;
the app preserves the raw label and does not infer chemistry, grade,
composition, price, or route. The obsolete Kaggle/Roboflow experiment remains
quarantined and is not in the APK.

Verification completed: 5 Python model-contract/interpreter tests, 88 Android
unit tests, and debug APK build passed. On 2026-10-02 the rebuilt debug APK was
installed in place on CPH2781 / Android 16 (`N7OZPV59XWWKPF4X`): C04 reached C05,
the real v2 classifier returned 37.5% and correctly abstained to manual
selection, and S00 ran the model in airplane mode at 84.13 ms CPU latency with
the correct 0.52 threshold. No lot was saved. High-confidence confirmation,
two-device QR, signed release APK, and entry-level-device coverage remain
unverified; T034/T044/T045/T047 therefore remain scoped to their open evidence.

## Separate non-production classifier experiment

The owner authorized a quarantined Roboflow/Kaggle **content-quality
comparison** on 2026-10-02. It is isolated in
`experiments/e_waste_model_v2/` and does not alter any release task, Android
asset, approved two-source float32 model, or release evidence. The first gate
is ready and locally verified: safely extract a provider ZIP, validate readable
images, hash and deduplicate them, and report observed provider labels without
inventing SahiTol mappings. Continue only after the owner supplies each
provider ZIP to the Drive experiment folder; then audit its report before
creating any benchmark split or training run. Registry eligibility remains
unchanged: both sources are provenance-pending and cannot be promoted.
The supplied ZIP audit found 1,073 conservative Roboflow/Kaggle perceptual
near-duplicate pairs, so they are not independent sources and must not be
combined. A Kaggle-only audit retained 2,949 assets in 2,859 duplicate groups
with zero groups crossing a deterministic 70/15/15 split. Continue with the
cross-source duplicate audit against Mendeley/Open Images before any combined
quarantine benchmark.
That audit then compared the five direct generic mappings: 1,471 Kaggle assets
versus 1,466 Mendeley/Open Images crops had zero exact matches and one
cross-label perceptual candidate. Exclude that Kaggle asset before preparing a
combined quarantine benchmark; no product assets changed.
The quarantined combined manifest is now prepared—not trained—with 3,136
training and 698 validation assets, plus separate Mendeley (325) and Kaggle
(220) held-out sets. Preparation found zero grouped/exact-hash split leakage.
Continue with validation-only training and do not read either held-out set.
The validation-only MobileNetV3Small run completed: frozen validation accuracy
was 83.95% (loss 0.5700) and fine-tuned validation accuracy 88.83% (loss
0.3646). Continue with threshold selection on validation only, then the
separate held-out evaluations; this is a quarantined research result only.
The held-out comparison rejects the Kaggle-augmented checkpoint for promotion:
it scored 97.73% on its own five-label Kaggle test (+22.73 points over the
two-source reference on that set) but regressed to 76.31% raw accuracy on the
broader Mendeley held-out test versus the reference's recorded 87.38%. Keep the
approved two-source float32 model unchanged; no product or release asset may
use this quarantined checkpoint.

Handoff date: 2026-10-02 (Asia/Kolkata). Phase: **T048 presentation deliverable complete; continue remaining release evidence in canonical task order.**

Scope and progression: [master](../MASTER_CONTENT.md), [tracker](08_TRACKER.md), [implementation plan](07_IMPLEMENTATION_PLAN.md). Authoritative statuses live in [status.json](planning/status.json).

## Live deployment

| Service | URL | Status |
|---|---|---|
| FastAPI backend | https://sahitol-api.onrender.com | Live -- /health/live 200 OK |
| Web console | https://sahitol.pages.dev | Live -- Cloudflare Pages, 97 modules |

**2026-10-01 recovery recheck:** after owner intervention, both the web
console and API health endpoint returned HTTP 200.

## Phase completion summary

**Do not treat the release as complete. Several implementation tasks have
passing focused checks, but shared release acceptance and the remaining
release-evidence tasks are outstanding.**

Latest T044 checkpoint: C07/C08 render the actual selected synchronized PCB and
show no invented pickup. The deployed accepted offer `5e53f4de-…` was resumed
on the collector, C10 created live handover `80a73333-9622-4ec2-af07-6a18fd6b78a0`
(QR `ST-80A733`), the recycler phone decoded and server-verified the QR, and
the API returned transaction `cdcd977e-…` as `CONFIRMED` v5 with 14.25 kg and
₹4,275.00. On 2026-10-02 a physical collector force-stop/relaunch recovered
that same handover by lot from the deployed API and C11 pulled the confirmed
receipt; no duplicate proposal was created. Continue with denial/discrepancy
variants only; do not clear either device or rewrite legacy repair rows.

GPS-denial is now physically covered: both Android location permissions were
denied, C04 allowed photo-free continuation, and C05 showed the coarse-location
fallback without blocking material/weight/condition entry. Camera denial is
also physically covered: permission was revoked through Android Settings, C04
showed the system prompt and returned to its usable bilingual photo-free path
after Don't allow; camera permission was restored. Actual Aeroplane mode also
left C14 usable with records safely queued, and was restored immediately.

C15 language selection was physically retested: Hindi and Marathi each changed
the persisted device setting; Marathi was restored. This proves selector
persistence and UI availability only, not native-speaker review.

The restored-camera C04/C05 retest also ran LiteRT locally: a fresh unsaved
photo produced 9.0% confidence below the 65% threshold and required manual
selection. Its C05 state survived Home/background and reopening; backing out
left the collector at 10 lots, with no test lot saved.

T041 public recheck on 2026-10-02 passed: Render live/health/ready and Pages
all returned HTTPS 200; readiness reports the deployed `adapter_readiness`
storage probe. Owner-supplied dashboard evidence then confirmed that the live
service is Free in Oregon (US West), auto-deploys `main`, and uses
`/health/live`; workspace Billing is Hobby with no card and $0.00 projected
charges. Free-tier spin-down remains a documented constraint.

The T044 changed-terms/dispute path is now also live-device verified. Isolated
handover `ST-50BF6E` was revised by the authorized recycler from 14.25 kg /
₹4,275 to 13.00 kg / ₹3,900; C11 pulled the changed terms and the collector
recorded a dispute. The hosted record is `DISPUTED` v3 without confirmation,
and its recovered C11 state says joint review is required. A separate physical
handover `ST-2EEC25` then exercised **Accept revised terms** for the same
13.00 kg / ₹3,900 changed terms; the deployed record is `CONFIRMED` v3 and C11
visibly reports the confirmed recycler receipt.

- **T046 DONE**: String parity 145/145 all locales. Audio 258/258 checksums OK. All AudioGrammarAndManifestTest PASS.
- **T047 DONE**: 7 data cards, model card (macro-F1 0.0159), frozen SHA-256 manifest (T047_FROZEN_RELEASE_MANIFEST.json).
- **T048 DONE**: 10-slide deck script, one-page fact sheet, five presenter role cards with Q&A crib.
- **T049 DONE**: 14-segment shot list, 15-item pre-recording checklist, 12-item post-validation checklist.
- **T050 DONE**: All software gates verified, README updated, release handoff document with APK SHA-256 and portal checklist.

Final commit: 24992df -- "chore: T046-T050 release phase complete"
check_docs.py: PASS 0 errors, 2949 links, 34 screens, 98 requirements.

## Test counts

- Backend API: 318/318 passing.
- Web integration: 44/44 passing.
- Android unit tests: All passing (73 tests, testDebugUnitTest).

## APK

- Debug APK: apps/android/app/build/outputs/apk/debug/app-debug.apk
- SHA-256: 82f1b2bbcd3689906dc41d9fafcfa955460f6e1a9b7f2991883f94c988ab99a2

## 2026-10-01 maintenance update

The debug APK now contains a scoped layout correction for approved collector screens C03, C06, C07, C14, and C15: Android 15 status-bar insets are reserved, light system surfaces receive readable system icons, and flexible rows prevent long content from collapsing into vertical text. `:app:assembleDebug` passed; the APK was installed over the existing application and launched on device `N7OZPV59XWWKPF4X` at 00:22 IST. No data was cleared. The next owner action is a brief on-device visual spot-check of the affected screens before video recording.

## 2026-10-01 audit remediation

T001 verification setup is repaired: the API's pinned test dependency set and repository-root import path now collect all 318 API tests under Python 3.10. T006's SQLite geometry test double now returns EWKB-compatible values, and the schema/facility/lot/matching verification subset passes 45 tests. Continue in catalog order with T007.

## 2026-10-02 device performance recheck

On CPH2781 Android 16, the debug APK is 35.60 MB; photo compression was 37 ms,
Room diagnostic write/read 26 ms, and LiteRT airplane-mode inference 61.42 ms.
Five activity launches gave 1.974 s p50 and 2.205 s p95, so the 2 s p95 target
is currently missed. Memory was 122,791 KB total PSS. A real C04 CameraX
capture was 2,721,334 bytes and the app's `PhotoCompressor` output was 77,572
bytes, below the 150 KB target and 2 MB hard limit. A signed release APK
remains unmeasured because signing requires the owner's keystore.

## Known gaps (immutable disclosures)

- R-RES-02 primary field research UNMET (owner desk-only decision, explicitly disclosed in all artifacts).
- Model macro-F1 0.0159, 100% abstention at threshold 0.65 -- safe, full manual fallback implemented.
- Native-speaker review Hindi/Marathi NOT_REVIEWED -- explicitly tracked.
- TalkBack on-device NOT_RUN -- explicitly tracked.
- On-device C15 Hindi/Marathi switch rechecked at default font scale on 2026-10-01; headphone listening, large-font, and TalkBack remain NOT_RUN.
- Render free tier cold-start: ~30 s wake time after inactivity.
- Release APK signing: owner action (keystore not in repo).

## Remaining owner actions (not agent-actionable)

1. Record demo video on device N7OZPV59XWWKPF4X using T049 shot list.
2. Build PPT in organizer template using T048 script (confirm organizer template format/size).
3. Generate signed release APK: `./gradlew assembleRelease` + sign with keystore.
4. Confirm GitHub repo visibility for judges.
5. Submit to portal before Sep30 cutoff (confirm authenticated official portal/timezone).
6. Record portal submission receipt in docs/evidence/T050_RELEASE_HANDOFF.md.

## Next action

Continue ordered independent verification and repair. On 2026-10-01, C07's visible
offer acceptance was repaired: it now proceeds directly to C10 Handover Capture
after locally persisting the acceptance. The repair was reverified on collector
device N7OZPV59XWWKPF4X and the focused Android unit suite passed. T021 was then
independently reverified with all 19 `test_trade.py` cases passing. T022 then
passed type checking, production build, and all 6 focused recycler-console tests.
T023 then independently passed all 13 handover workflow tests. T024 passed 7
focused Android tests and its C10 handover capture was seen on the collector
device. T025 was exercised across two physical Android devices: actual QR
decoding and truthful record display work. The missing server-backed lookup and
authenticated receipt confirmation are now implemented and locally
integration-tested (14 API handover tests, web typecheck/build, Android compile
and focused handover tests). T025 remains IN_PROGRESS until the updated deployed
APK and web bundle are retested on both phones. That retest is now complete:
`ST-5F1B` was QR-decoded, server-verified and recycler-confirmed across both
phones. The R05 placeholder receipt defect discovered during the run was
corrected, deployed and physically rechecked; it now shows the confirmed server
record and no second confirmation button. T025 is DONE. AT-032 through AT-034
remain NOT_RUN until their complete cross-task checks are run. T026 audit then
added server-derived payment asserting-actor identity and administrator
self-ack prevention; payment/schema verification passed 25/25. Continue at
T027. That audit found in-memory payment assertions, destructive Room migration,
and a fabricated local recycler acknowledgement. The repair adds durable Room
payment storage and safe migration, keeps asserted payments as dues until server
acknowledgement, and removes the collector-side acknowledgement action. Focused
Android payment tests pass 6/6, including process-restart rehydration; continue
at T028 after documentation validation. The updated APK was installed over the
collector device without clearing data and relaunched without a Room migration
failure. T028 was then independently repaired and reverified: quality baselines
now use only PRICE_V1-eligible observations, media reuse compares SHA-256 rather
than upload ID, and large-weight flags use `DQ-LARGE-WEIGHT`; 33 focused
quality/lot tests pass. T029 was independently repaired and reverified: event
search now has inclusive UTC date bounds, and price moderation requires a
justification and emits a hash-chained review event. The dedicated
admin-maintenance suite passes 10/10. T030 was independently repaired: approved
A01-A07 layouts now bind their operational values/actions to authenticated admin
APIs instead of static sample figures; A03 is explicitly evidence-only, not a
statutory compliance decision. Focused dashboard tests pass 4/4, admin API
tests pass 10/10, and the web typecheck/production build pass. T033's former
Windows-runtime blocker was independently cleared: TensorFlow 2.15.1 is
installed, the LiteRT interpreter opens the bundled `[1,224,224,3]` to `[1,12]`
model, and all six model tests pass. The model remains honestly weak (macro-F1
0.0159, 100% abstention at threshold 0.65). Continue at the next audit finding,
T039. Independent repair completed: the registered C17 screen was opened on
collector device N7OZPV59XWWKPF4X through the Home safety card, and Hindi plus
Marathi rendering, offline state, hazard/prohibition/step content and audio
trigger were observed. Audio audibility itself was not claimed. U01 was repaired
to use the canonical ECONOMICS_V1 chosen-demo fixture (₹350/₹470/₹120), replace
telemetry and uplift claims with transparent assumptions, link the separate
ledger, expose accessible controls and Hindi/Marathi return labels, permit
lower-rate/higher-transport negative scenarios, and compute an actual SHA-256
export field. Android safety tests pass 6/6, focused U01 tests pass 8/8, and
web typecheck/build pass. T040 is now independently verified: 23 local
security-boundary/core tests pass; deployed Render health returned HTTPS 200;
the configured Pages origin preflight was accepted while evil.example was
rejected. Retention/backup is still T042 scope. T041 repair is in progress:
public Render health/ready return HTTPS 200 and ready reports production database
and Supabase storage, but the former check merely constructed an adapter. The
repair verifies private-bucket metadata and reports `storage_probe=adapter_readiness`.
Focused recovery/security tests pass 32/32; push and recheck deployed readiness
before closing T041. T042 is DONE: its focused recovery suite, fresh
Docker/PostGIS migrations/seed/health/backup/restore/restart and CPH2781
debug-Wi-Fi application request all passed. The phone received a local API demo
authentication 200 and two directory 200 responses; a deployed-only lot gave
the expected fresh-local-database 404. Compose CORS and port wiring and C08's
previously inert Refresh action were repaired. Resume at T043's remaining
real-device/hosted fault acceptance, while retaining its explicit scope.
T043 was independently rerun on 2026-10-02 and initially exposed two linked
collector-ownership regressions: a sync-created lot was absent from its owner
index and its match request was rejected as another collector's lot. Ownership
checks now use `current_user.collector.id` rather than the distinct user UUID;
the focused suite passes 44/44. T043 remains in progress only for its real
device/hosted fault-acceptance scope.
T043 is now DONE: 44 deterministic cases pass, CPH2781 reached the isolated
local API, and a restart preserved 10 lots plus 13 `NEEDS_REPAIR` legacy rows.
No data was deleted or retried. T045 is eligible next; T044 remains blocked
only by T041's private Render-account verification.
T043 then reran cleanly: 44 focused deterministic tests pass, including an
authorized-recycler match that was tightened from a response-shape check. Its
real-device/hosted fault acceptance remains NOT_RUN; continue at T044 only
after retaining that scope boundary.
T044 physical retest found C14 manual sync only handled handover imports and
showed stale queue state. The repair routes valid UUID operations to the normal
batch endpoint, replaces stale manual work and reloads the full Room outbox;
on the cellular collector it showed 10 acknowledged and 12 visible
NEEDS_REPAIR legacy placeholders. The placeholder offer path is now replaced:
C07/C08/C09 load only live UUID facilities/offers and accept only server-issued
terms hashes/versions. A device test caught and fixed main-thread HTTP; the
hosted demo directory now loads and the existing cable lot honestly shows zero
offers. Continue T044 with a new compatible server-backed lot, recycler-created
offer and current two-device journey; do not revive the superseded simulated C09 evidence.
The old-demo profile bootstrap repair deployed successfully and the hosted
profile endpoint now returns the physical demo collector. A fresh device PCB
lot then exposed a second server defect: sync used the user UUID where the lot
foreign key requires the collector profile UUID. That mapping is repaired and
the full sync suite passes 16/16; push/deploy it, then create one more fresh
photo-free PCB lot and verify both CREATE_DRAFT and its dependent LIST_LOT are
acknowledged before attempting a real recycler request.
That physical retry is complete: a live authenticated probe returned APPLIED,
and collector lot `f8b0587f-…` recovered from only the historic
`lots_collector_id_fkey` failure. Its CREATE_DRAFT and dependent LIST_LOT are
ACKNOWLEDGED and the local lot is SYNCED/LISTED at v2. Do not requeue unrelated
NEEDS_REPAIR rows. Continue with a real facility request and recycler-created
offer when the second handset is available again.
An authenticated collector API request is now PENDING for that listed PCB lot
and live PCB-compatible facility; readback has zero offers. This is server
contract setup only, not claimed as C08/C09 handset or two-device evidence.
The new-lot outbox contract was then repaired from unsupported `CREATE_LOT` /
`material_code` / local-path media IDs to `CREATE_DRAFT` / `material_id` / no
fabricated media IDs. Focused tests pass and an updated APK is on the collector
device; continue the fresh PCB lot creation and manual sync before attempting
the recycler offer.
The fresh corrected PCB lot reached hosted Postgres but the pre-existing demo
user had no `collectors` profile. Demo login now repairs this legacy bootstrap
state; its 14 focused auth tests pass. Push/deploy the server repair, then tap
manual sync to retry the already-queued valid PCB lot.

2026-10-04 device follow-up: C10's displayed money was incorrectly labelled as
"Recorded handover mass" and its apparent agreement/revision buttons had no
server action. C10 now labels the accepted value accurately, makes the pending
measurement state explicit, and opens a recovered server QR record instead of
creating a duplicate. C07 now separately recovers an accepted transaction so
the handover continuation is not lost when the open-offer list is empty. The
Android debug build passed and was installed over CPH2781 without clearing data.
The two PCB lots inspected (13 kg and 13.5 kg) both returned no accepted server
transaction and therefore remained correctly blocked; no test offer, handover,
or confirmation was created. Commit/push the two Android screen fixes and then
repeat C10 device navigation with a lot whose server transaction is AGREED.
