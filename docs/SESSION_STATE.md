# Current handoff

Handoff date: 2026-09-30 (Asia/Kolkata). Phase: **Phase 7 complete -- all RELEASE tasks DONE**.

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
independently reverified with all 19 `test_trade.py` cases passing. Continue with
T022 after documentation regeneration and validation.
