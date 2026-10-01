# Current handoff

Handoff date: 2026-10-01 (Asia/Kolkata). Phase: **T025 repaired and physically reverified; continue ordered verification from T026**.

Scope and progression: [master](../MASTER_CONTENT.md), [tracker](08_TRACKER.md), [implementation plan](07_IMPLEMENTATION_PLAN.md). Authoritative statuses live in [status.json](planning/status.json).

## Live deployment

| Service | URL | Status |
|---|---|---|
| FastAPI backend | https://sahitol-api.onrender.com | Live -- /health/live 200 OK |
| Web console | https://sahitol.pages.dev | Live -- Cloudflare Pages, 97 modules |

**2026-10-01 recovery recheck:** after owner intervention, both the web
console and API health endpoint returned HTTP 200.

## Phase completion summary

**All 50 assessed RELEASE tasks DONE. T048-T050 completed in this session.**

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

## 2026-10-01 device performance recheck

On CPH2781 Android 16, the debug APK is 35.60 MB; photo compression was 37 ms,
Room diagnostic write/read 26 ms, and LiteRT airplane-mode inference 61.42 ms.
Five activity launches gave 1.974 s p50 and 2.205 s p95, so the 2 s p95 target
is currently missed. Memory was 122,791 KB total PSS. The release APK and an
actual production-photo upload remain unmeasured.

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
before closing T041.
