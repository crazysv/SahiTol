# Current handoff

Handoff date: 2026-09-30 (Asia/Kolkata). Phase: **Phase 6 complete -- hosted deployment live**.

Scope and progression: [master](../MASTER_CONTENT.md), [tracker](08_TRACKER.md), [implementation plan](07_IMPLEMENTATION_PLAN.md). Authoritative statuses live in [status.json](planning/status.json).

## Live deployment

| Service | URL | Status |
|---|---|---|
| FastAPI backend | https://sahitol-api.onrender.com | Live -- /health/live 200 OK |
| Web console | https://sahitol.pages.dev | Live -- Cloudflare Pages, 97 modules |

## Phase completion summary

T001-T046 all DONE. T044 and T046 completed in this session.
T044 DONE: Full E2E real-device usability on N7OZPV59XWWKPF4X. QR Ref ST-7022, SHA-256 chain, bilingual labels, Offline Ready, honest EPR disclaimer.
T046 DONE: String parity 145/145 all locales. Audio 258/258 checksums OK. All AudioGrammarAndManifestTest PASS. Honest gaps (native-speaker, TalkBack) documented and tracked.

## Remaining RELEASE tasks

- T047: Dataset/model evidence freeze (now eligible -- T046 DONE).
- T048: PPT + presenter handoff pack (blocked on T047).
- T049: Demo video (blocked on T048).
- T050: Release + submission handoff (blocked on T049).

## Test counts

- Backend API: 318/318 passing.
- Web: 24/24 passing.
- Android unit tests: 100% in testDebugUnitTest (73 tests).

## Known gaps

- R-RES-02 primary field research UNMET (owner desk-only decision, explicitly disclosed).
- Fieldwork obligation (two-collector) UNMET -- tracked separately.
- Native-speaker review Hindi/Marathi NOT_REVIEWED -- explicitly tracked.
- TalkBack on-device NOT_RUN -- explicitly tracked.
- Render free tier cold-start: ~30s wake time after inactivity.

## Next action

Proceed to T047: Dataset/model evidence freeze. Read docs/planning/catalog.json for T047 spec, read docs/06_DATA_MODEL.md and the model card at apps/android/app/src/main/assets/model_card.md. Freeze dataset provenance, LiteRT model digest, and audio clip inventory digest into a signed evidence document.
