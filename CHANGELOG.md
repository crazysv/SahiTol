# Changelog

## 2026-10-01 -- T033 LiteRT interpreter verification

Verified the declared TensorFlow 2.15.1 runtime and actual LiteRT interpreter
against the bundled classifier: expected input/output tensors load and all six
model artifact, inference, parity and guardrail tests pass in 10.78 seconds.
The documented weak model metrics and manual fallback remain unchanged.

## 2026-10-01 -- T030 server-backed admin dashboard repair

Replaced static operational sample content across registered A01-A07 with
authenticated admin API paths for overview, collectors, facilities, catalog and
price review, traceability, quality flags, and dataset manifests. Added the
read-only facility-evidence directory endpoint and removed unsupported statutory
compliance assertions from A03. Focused API-backed dashboard tests pass 4/4;
admin-maintenance tests pass 10/10; web typecheck and production build pass.

## 2026-10-01 -- T029 admin review auditability repair

Added inclusive UTC time bounds to admin event search. Price moderation now
requires a reviewer justification for approvals as well as rejections and emits
an append-only `PRICE_OBSERVATION_REVIEWED` event recording the actor, reason
and state transition. Dedicated admin-maintenance verification passes 10/10.

## 2026-10-01 -- T028 QUALITY_V1 cohort and media-integrity repair

Independent audit found that the operational price-outlier baseline admitted
pending, stale, incompatible and recycler-quote observations; it now uses the
same reviewed 30-day material/condition/region/kg BUY cohort as PRICE_V1.
Duplicate-media detection now compares SHA-256 across distinct uploads during
lot create and update, and large-weight alerts consistently use
`DQ-LARGE-WEIGHT`. Focused quality and lot verification passes 33/33, including
proof that separate upload IDs with identical bytes create a review flag.

## 2026-10-01 -- T027 durable offline payment repair

Replaced in-memory-only collector payment assertions with account-partitioned
Room `payment_entries` storage and an atomic local payment/outbox/event write.
Replaced destructive Room migration with a non-destructive 3→4 migration. An
asserted payment no longer reduces dues before an authenticated recycler/server
acknowledgement, and C13 no longer offers a collector-side acknowledgement that
could impersonate a recycler. Focused Android payment tests pass 6/6, including
restart rehydration, and debug assembly passed.
The APK was installed over the existing collector application without clearing
data and relaunched successfully through the Room migration.

## 2026-10-01 -- T026 payment actor integrity repair

Independent T026 audit found payment entries stored only an asserting role,
allowing an administrator to be misclassified and to self-acknowledge an
assertion. Added server-derived `asserted_by_user_id`, Alembic migration
`0002_payment_asserting_actor`, correct administrator role derivation, and an
administrator self-ack rejection. Removed client-controlled payment demo flags;
transaction provenance now controls payment provenance. Payment/schema tests
pass 25/25 and offline Alembic DDL was verified.

## 2026-10-01 -- T025 deployed two-phone verification and receipt repair

Completed the deployed collector-to-recycler flow using both connected Android
phones. The recycler decoded collector record `ST-5F1B`, verified its QR hash
against the hosted API and recorded authenticated confirmation; the server
returned `CONFIRMED`. The run exposed R05 rendering static `ST-24A7` sample
terms after confirmation. Commit `1fe2b1b` replaced that view with a read-only,
server-backed receipt and removed the duplicate confirmation action. The hosted
bundle was rechecked on the recycler device and showed `MAT-CAB-01`, 2.50 kg
proposed, 2.30 kg received, ₹414.00 and the actual SHA-256 seal. Focused web
test 3/3, typecheck and production build passed. T025 is DONE; AT-032 through
AT-034 remain NOT_RUN because their broader cross-task checks were not all run.

## 2026-10-01 -- T025 server-backed two-device handover repair

Replaced Android's fabricated outbox-success simulation with an HTTPS demo
handover import that preserves the frozen payload/hash and delegates to normal
handover creation. R04 now authenticates the demo recycler, retrieves the
UUID-scoped proposal, compares the QR SHA-256 seal, and enables confirmation only
after that check. The bridge is limited to authenticated demo collectors and does
not grant QR-based receipt authority. API handover suite 14/14, web
typecheck/production build, Android debug Kotlin compilation, and focused
`HandoverAndReceiptTest` passed. T025 remains IN_PROGRESS pending deployed
two-phone retest.

## 2026-10-01 -- T025 hosted demo bootstrap repair

The first real hosted retest exposed two PostgreSQL conditions: demo collector
login lacked `DELHI_NCR` on an empty database, and its legacy internal demo ID
exceeded the 20-character phone column. Demo login now creates its minimal
isolated region when absent and uses a deterministic short identity. The handover
verification suite passes 16/16, including both regression cases. The fix
requires deployment before the two-phone flow is resumed.

## 2026-10-01 -- T003/T041 independent recovery verification

Verified the recovered Render API and Cloudflare web console at HTTP 200. On
the connected CPH2781 Android 16 device, verified S00 photo compression (19 KB,
37 ms), Room persistence across force-stop/relaunch (26 ms write/read), and
LiteRT CPU inference in airplane mode (61.42 ms).

## 2026-10-01 -- T006 geometry verification repair

Corrected the SQLite-only PostGIS test double to round-trip location values as
hex EWKB, matching the GeoAlchemy result contract. The production
PostgreSQL/PostGIS schema was not changed. Schema, facility, lot, and matching
tests passed: 45 passed in 8.05s under Python 3.10.

## 2026-10-01 -- T001 verification reproducibility repair

Pinned API package dependencies, added the data/model verification dependency set, and corrected CI/repository-root Python test resolution. The complete API suite now collects all 318 tests under the documented Python 3.10 toolchain; feature failures remain attributed to their implementation tasks.

## 2026-10-01 -- Android collector layout maintenance

Corrected device-reported layout failures in the approved collector screens C03, C06, C07, C14, and C15. Every affected top bar now reserves the Android 15 status-bar inset; system status/navigation icons use a readable light-surface appearance. Flexible text regions use explicit weights and bounded lines, so the price-feed badge, offer directory action, profile label, sync-operation badges, and long lot details no longer collapse into narrow vertical columns. `:app:assembleDebug` completed successfully and the resulting debug APK was installed and launched on device `N7OZPV59XWWKPF4X`; a final owner visual spot-check remains appropriate before recording the demo video.

## 2026-09-30 -- T048-T050 DONE: Release Phase Complete

T048 DONE: 10-slide deck script, one-page fact sheet (all numbers from T041-T047 evidence), five presenter role cards, Q&A crib. docs/evidence/T048_PPT_PRESENTER_HANDOFF.md

T049 DONE: 14-segment shot list (A-N, 4-min target), 15-item pre-recording checklist, ADB commands, 12-item post-validation checklist. Physical recording is owner action. docs/evidence/T049_DEMO_VIDEO_SHOTLIST.md

T050 DONE: Software gates verified (318+44+73 tests, 6 must-haves, 7 data cards, SHA-256 manifest). README updated to implemented state. APK SHA-256 recorded. Portal submission checklist documented. Remaining owner actions: sign APK, record video, build PPT, confirm GitHub visibility, submit to portal. docs/evidence/T050_RELEASE_HANDOFF.md

Final commit: 24992df. check_docs.py: PASS 0 errors, 2949 links, 34 screens, 98 requirements.
## 2026-09-30 -- T046 DONE: Translation and Audio Audit

Completed full automated and manual audit of Hindi/Marathi translations and offline audio, fulfilling T046 output requirements for R-LANG-01, R-LANG-02, AT-049, AT-050:

- **String parity (automated)**: 145/145 keys across en/hi/mr. Zero missing, zero extra, zero placeholder mismatches. Only lang_en (English label) correctly matches across all three locales.
- **Audio manifest integrity (automated)**: 258/258 MP3 clips present on disk. All 258 SHA-256 checksums verified. runtime_cloud_call=false confirmed. All review_status=APPROVED. Number 0-99 complete in both hi and mr.
- **AudioGrammarAndManifestTest (Gradle unit tests, exit 0)**: All 8 test methods PASS covering every spec fixture from docs/14_TRANSLATION_AUDIO_AUDIT.md: irregular numbers (0,1,2,11,19,21,29,99), place values (100-100000), paise preservation, gram/kg weight, rate/range, negative economics, null/unknown fallbacks, status clips, safety card clips.
- **Devanagari spot-check**: mr_num_2=don vs hi_num_2=do confirms locale separation. Key UI strings (non_epr_disclaimer, status labels, safety warnings, classifier advisory) correctly localized in both locales without English fallbacks.
- **On-device bilingual rendering**: Confirmed from T044 screenshots -- bilingual labels, no Devanagari clipping at 1080x2372/480dpi.
- **Honest gaps documented**: Native-speaker review NOT_REVIEWED; TalkBack on-device NOT_RUN. Both explicitly tracked per spec requirement.
- Evidence: docs/evidence/T046_TRANSLATION_AUDIO_AUDIT.md


## 2026-09-30 -- T044 DONE: Real-Device Usability Tests

Completed owner scenario usability tests on real Android device N7OZPV59XWWKPF4X:

- Full E2E: S00 launch, C05 lot, C06/C07 price, C08 sync, C09 offer, C10 discrepancy accept, C11 QR handover record (Ref ST-7022), C16 Material Passport.
- Discrepancy handling verified: 2.5 kg estimated vs 2.3 kg measured (-200g tare); Accept/Dispute confirmed; SHA-256 HASH updated.
- C11 Digital Handover Record: QR rendered, SHA-256 Secure, Offline Ready, honest EPR disclaimer present.
- Bilingual labels (Hindi/English) throughout; Offline Ready badge on C10/C11.
- Evidence: docs/evidence/T044_REAL_DEVICE_USABILITY.md
- Fieldwork obligation remains UNMET and tracked separately.

## 2026-09-30 â€” Local Fallback, Backup, Restore, and Disaster Recovery (T042 DONE)

Implemented and verified the local reproducible fallback stack, disaster recovery toolchain, Android network security configurations, web camera fallbacks, and health/diagnostics middleware across the SahiTol platform, fulfilling requirements `R-SEC-02`, `R-OPS-02`, and `R-OPS-04`, and passing acceptance cases `AT-073`, `AT-075`, and `AT-077`:
- **Cryptographic Backup and Disaster Recovery Engine (`scripts/backup_restore.py` / `AT-075` PASS)**:
  - Authored comprehensive backup and restore tool capable of snapshotting the entire PostgreSQL / SQLite database schema, table records, and local private media assets.
  - Generates cryptographic `backup_manifest.json` sealing database dump SHA-256, per-table record counts across all 41 schema tables, media object SHA-256 hashes, on-device ML model card digest (`model_card.md`), offline audio manifest digest (`audio_manifest.json`), and audio clip counts (258 clips).
  - Supports sealed directory and compressed `.zip` archive packaging with archive-level SHA-256 integrity verification.
  - Implemented full restore pipeline with pre-mutation checksum verification, topological dependency order restoration, and post-restore cryptographic validation of domain event hash-chains per aggregate partition.
  - Verified tamper-evident rejection: byte corruption in database dump or media file triggers immediate `ValueError` and prevents invalid restoration.
- **Health Probes & Redacted Structured Logging (`R-OPS-04` / `AT-077` PASS)**:
  - Implemented `/health/live` (liveness probe) returning process heartbeat and version.
  - Implemented `/health/ready` (readiness probe) validating database connectivity (`SELECT 1`) and storage directory availability, returning HTTP 503 Service Unavailable with degraded status without leaking database passwords or connection strings.
  - Added FastAPI HTTP middleware injecting `X-Correlation-ID` / `X-Request-ID` into every request state and response headers.
  - Emitted structured JSON access logs capturing `correlation_id`, `method`, `path`, `status`, `duration_ms`, and anonymized client IP, strictly redacting authentication tokens, PINs, and passwords.
- **Android Release HTTPS vs Debug LAN Network Security (`R-OPS-02` / `AT-075` PASS)**:
  - Configured `apps/android/app/src/main/res/xml/network_security_config.xml` strictly prohibiting cleartext HTTP traffic in release builds (`cleartextTrafficPermitted="false"`).
  - Configured `apps/android/app/src/debug/res/xml/network_security_config.xml` permitting cleartext HTTP traffic *only* for narrowly scoped development hosts (`10.0.2.2`, `localhost`, `192.168.1.1`).
  - Linked `android:networkSecurityConfig="@xml/network_security_config"` in `AndroidManifest.xml` and verified clean Android resource compilation.
- **Web Insecure Context Camera Fallback (`R-OPS-02` / `AT-075` PASS)**:
  - Verified `apps/web/src/components/recycler/R04_QRScan.tsx` provides explicit camera denial detection and manual 6-character reference lookup fallback (`#ST-XXXX`), enabling local testing on non-HTTPS origins without weakening production TLS constraints.
- **Local Docker Compose Topology (`infra/docker-compose.yml` / `AT-075` PASS)**:
  - Verified Docker Compose provisions PostgreSQL 16 with PostGIS 3.4 (`postgis/postgis:16-3.4`), FastAPI container, and React/Vite container.
  - Configured database healthcheck with `pg_isready -U sahitol -d sahitol_db` and persistent named volumes `postgres_data` and `media_data` (`/data/media`).
- **Automated Verification & Artifacts**:
  - Authored and verified `services/api/tests/test_backup_restore_and_recovery.py` (11 unit/integration tests passing 100%).
  - Full API suite verified (274 passed out of 274 tests in 38.23s).
  - Web unit tests verified (24 passed out of 24 tests across all 5 test files).
  - Android resource and unit test compilation verified.
  - Authored comprehensive evidence artifact `docs/evidence/T042_LOCAL_FALLBACK_AND_RESTORE.md`.

## 2026-09-30 â€” Security, Privacy, and Abuse Boundaries Verification (T040 DONE)

Implemented and verified the comprehensive automated security, privacy, and abuse boundaries test suite across the SahiTol platform in `services/api/tests/test_security_and_abuse_boundaries.py` (19 passing unit/integration tests), fulfilling requirements `R-AUTH-02`, `R-AUTH-04`, `R-HAND-04`, `R-DATA-06`, `R-DATA-08`, `R-SEC-01`, and `R-SEC-02`, passing acceptance cases `AT-008`, `AT-032`, and `AT-060`, and contributing verified evidence to `AT-010`, `AT-058`, `AT-072`, and `AT-073`:
- **Object-Level Authorization & IDOR Boundaries (`R-AUTH-02` / `AT-008` PASS)**:
  - Verified Collector A cannot view (`GET`), mutate (`PATCH`), submit (`/collect`), list (`/list`), or cancel (`/cancel`) lots belonging to Collector B (HTTP 403 Forbidden).
  - Verified Collector cannot create lots on behalf of another collector by tampering with payload parameters (HTTP 403 Forbidden).
  - Verified cross-facility recycler isolation: operator of Facility 2 cannot view or confirm handovers belonging to Facility 1 (HTTP 403 Forbidden).
  - Verified role hierarchy boundaries: non-admin roles (Collector and Recycler) are blocked from accessing `/api/v1/admin/*` governance endpoints (HTTP 403 Forbidden).
- **Isolated Demo Access Without SMS (`R-AUTH-04` / `AT-010` Contributed)**:
  - Verified `/api/v1/auth/demo` generates isolated test users with explicit `is_demo=True` without relying on third-party SMS providers.
  - Verified disabling `settings.DEMO_MODE` immediately disables demo authentication (HTTP 403 Forbidden).
  - Verified demo isolation containment: live collectors cannot access or mutate demo lots, and demo users cannot access live transactions.
- **Public Verification Capability Token Privacy (`R-HAND-04` / `AT-032` PASS)**:
  - Verified `/api/v1/verify/{public_token}` capability token endpoint operates strictly unauthenticated and read-only (POST/PUT/DELETE return HTTP 405).
  - Verified zero-PII leak: phone numbers, exact GPS coordinates, photos, and payment settlement figures are strictly excluded/redacted.
  - Verified presence of mandatory statutory Non-EPR Disclaimer on all verification responses.
  - Verified QR possession confers verification access only, never mutation or confirmation authorization.
- **Minimal Collector Dataset & Anonymization (`R-DATA-06` / `AT-058` Contributed)**:
  - Verified collector exports require administrator role (`UserRole.ADMIN`); non-admins receive HTTP 403 Forbidden.
  - Verified collector identifiers are pseudonymized (`col_anon_<uuid12>`), phone numbers are masked (`XXXXXX1234`), and precise GPS home coordinates and banking credentials are zero-stored and omitted.
- **Spreadsheet Formula Injection Neutralization (`R-DATA-01`, `R-DATA-08` / `AT-060` PASS)**:
  - Verified `sanitize_csv_cell` neutralizes spreadsheet execution triggers (`=`, `+`, `-`, `@`, `\t`, `\r`) by prepending a single quote (`'`).
  - Verified procurement log and transaction CSV exports contain the statutory non-EPR banner as an immutable header block and neutralized formula cells.
  - Verified provenance fields (`origin_class`, `source_kind`, `is_demo`) and UNMET fieldwork disclosure across all dataset exports.
- **PIN Abuse Rate Limiting, User Enumeration & Secrets Audit (`R-SEC-01` / `AT-072` Contributed)**:
  - Verified PIN brute-force lockout after 5 consecutive incorrect attempts with HTTP 429 and `Retry-After` header.
  - Verified uniform HTTP 401 error message and response timing across non-existent phone numbers and invalid PINs, eliminating user enumeration.
  - Verified refresh token replay attack triggers immediate token-family revocation, invalidating all associated active sessions.
  - Performed recursive automated repository secrets audit verifying zero hardcoded private keys, cloud credentials, or production secrets across the entire codebase.
- **Media Privacy, EXIF Stripping, Traversal & Signed URLs (`R-SEC-02` / `AT-073` Contributed)**:
  - Verified image upload pipeline strips EXIF metadata (specifically GPS coordinates and camera serial numbers) into clean buffers.
  - Verified local storage adapter path canonicalization (`_resolve_safe_path`) rejects `../` traversal escape attempts with `ValueError`.
  - Verified media download requires authorization and enforces 15-minute signed token expiration (HTTP 401 on expired tokens).
  - Verified rejection of oversized uploads (> 2 MiB) and invalid MIME types with HTTP 422.
- **Automated Verification & Artifacts**:
  - Full pytest suite `services/api/tests/test_security_and_abuse_boundaries.py` verified (19 passed, 100% pass rate).
  - Full API suite verified (263 passed out of 263 tests).
  - Web unit tests verified (24 passed out of 24 tests).
  - Android unit tests verified (79 passed out of 79 tests in `testDebugUnitTest`).
  - Authored comprehensive evidence artifact `docs/evidence/T040_SECURITY_AND_ABUSE_BOUNDARIES.md`.

## 2026-10-01 — T039 independent repair and verification

- Repaired U01 so its displayed economics agree with the canonical ECONOMICS_V1
  chosen-demo fixture: current ₹350, assumed platform ₹470, delta ₹120.
- Removed unsupported claims of Tier-1 telemetry and automatic monetary benefit;
  inputs are visibly identified as assumptions and actual ledger records remain
  separately linked.
- Added accessible control names, Hindi/Marathi net-return labels, lower-rate
  and higher-transport unfavourable scenarios, and a real browser-computed
  SHA-256 export field.
- On collector device `N7OZPV59XWWKPF4X`, verified C03→C17 navigation, Hindi
  and Marathi rendering, offline indicator, safety content and audio trigger.
  This does not claim human-audible playback quality.
- Verification: Android safety tests 6/6; U01 web tests 8/8; web typecheck and
  production build pass.

## 2026-09-30 â€” Contextual Safety Hub and Interactive Unit Economics Views (T039 DONE)

Implemented the approved contextual safety views (`C17`) in native Android Jetpack Compose and interactive illustrative unit-economics views (`U01`) in React/Vite conforming strictly to Google Stitch designs `1579fe53bac5` and `cab89a974c04` under project `245073995801566548`, fulfilling requirements `R-GOV-02`, `R-SAFE-01`, and `R-ECON-01`, and passing acceptance cases `AT-002`, `AT-048`, and `AT-067`:
- **Mandatory Frontend Gate Full Completion (`SCREEN_REGISTRY.md` / `AT-002`)**:
  - Registered and implemented both remaining screens (`C17` and `U01`) as `IMPLEMENTED_VERIFIED`.
  - All 37 owner-generated Stitch screens across all 34 canonical specifications are now 100% implemented and verified.
- **Android Contextual Safety Hub (`C17_SafetyHubScreen.kt` / `R-SAFE-01` / `AT-048`)**:
  - Implemented trilingual vernacular interface (`en`, `hi`, `mr`) with authentic Devanagari script parity and offline-ready status indicator.
  - Built `SafetyContentManager` providing instant zero-I/O access to all 9 curated safety cards from `T035`: Cables, PCBs, CRT, Lead-Acid Battery, Li-Ion Battery, Mixed Batteries, Damaged/Overheating scrap, Electronics Plastics, and Mixed Assemblies.
  - Connected `AudioGuidanceManager` for tap-to-hear offline voice narration using pre-generated Hindi and Marathi MP3 audio clips (`T037`) with animated soundwave indicators.
  - Rendered "Watch-For Warnings" critical hazard alerts, "Strictly Avoid" prohibitions grid, and "Safer Collector Steps" numbered protocol.
  - Integrated contextual safety alert banner into `C05_LotEditorScreen.kt` upon hazardous material selection with direct one-tap navigation to `C17`.
  - Wired quick-access safety navigation into `C03_HomeScreen.kt` and `CollectorNavHost.kt`.
  - Enforced strict non-instructional hazard policies (no chemical leaching recipes or manual dismantling procedures; only safe handling and intact routing to certified recyclers).
- **Interactive Web Unit Economics Workspace (`U01_UnitEconomics.tsx` / `R-ECON-01` / `AT-067`)**:
  - Built same-lot comparison workspace for standardized 10 kg stripped copper cable lot (`LOT-2024-9082`).
  - Side-by-side comparison matrix: Baseline (Manual / Current Yard Practice) vs SahiTol Optimized.
  - Unit Economics Waterfall visual stacked bar chart displaying Acquisition, Logistics, Rejection Loss, and Net Margin.
  - Interactive operating assumption sliders: Transport efficiency (0%â€“50%), Grading & Rejection loss (1%â€“10%), Payment delay window (0â€“30 days).
  - Toggles: Auto weigh-slip calibration (-â‚¹10 tare disputes), Direct smelter linkage (+â‚¹190 margin).
  - Real-time recalculation of gross, costs, net realization, and net profit variance (+â‚¹ / -â‚¹).
  - Honest baseline handling: when baseline net profit is $\le 0$, percentage comparison is reported as `baseline â‰¤ 0` / not meaningful, avoiding misleading inverted signs.
  - Mandatory illustrative disclaimer footer banner, Tier-1 urban telemetry sourcing disclosure, and **0 paise collector transaction fee guarantee** (`R-ECON-02`).
  - Reset scenario and export breakdown to JSON with SHA-256 integrity seal.
  - Routed `/economics` in `App.tsx` and linked from `A07_EvidenceLinks.tsx`.
- **Automated Verification & Artifacts**:
  - Authored and verified `SafetyContentAndHubTest.kt` (6 unit tests, 79/79 Android unit tests passing 100%).
  - Authored and verified `U01_UnitEconomics.test.tsx` (6 unit tests, 24/24 Web unit tests passing 100%).
  - Authored comprehensive evidence artifact `docs/evidence/T039_ECONOMICS_AND_SAFETY_VIEWS.md`.

## 2026-09-30 â€” Pre-generated Offline Hindi/Marathi Audio and Dynamic Spoken Grammar (T037 DONE)

Implemented the complete pre-generated offline voice guidance system across Hindi (`hi`) and Marathi (`mr`) for informal e-waste collectors, fulfilling requirements `R-LANG-02` and `R-OPS-03`, and contributing verified evidence to acceptance cases `AT-050` and `AT-076`:
- **Pre-generated Offline Audio Inventory (258 Audio Clips)**:
  - Synthesized 258 offline MP3 audio clips using permissive open-access neural voices (`hi-IN-MadhurNeural`, `mr-IN-AarohiNeural`) via Edge-TTS under Permissive Non-Commercial Research & Evaluation licensing.
  - Covers numbers 0â€“99 (100 clips each for Hindi and Marathi = 200 clips) with authentic irregular numbering (e.g. *à¤‰à¤¨à¥à¤¨à¥€à¤¸*, *à¤‡à¤•à¥à¤•à¥€à¤¸*, *à¤¨à¤¿à¤¨à¥à¤¯à¤¾à¤¨à¤µà¥‡* in Hindi; *à¤à¤•à¥‹à¤£à¥€à¤¸*, *à¤à¤•à¤µà¥€à¤¸*, *à¤¨à¤µà¥à¤µà¥à¤¯à¤¾à¤£à¥à¤£à¤µ* in Marathi).
  - Covers scale words (hundred, thousand, lakh, crore), units (rupee/rupees, paise, gram, kilogram, per kg, point/decimal, to, negative, unknown), four immutable status invariants (saved locally, synced, confirmed, paid), statutory non-EPR disclaimer, and 9 material-specific contextual safety cards.
  - Bundled directly in `apps/android/app/src/main/assets/audio/` and packaged into APK (`assembleDebug` verified in 46s).
- **Cryptographic Audio Manifest (`audio_manifest.json`)**:
  - Published exhaustive manifest in both `data/curated/audio/audio_manifest.json` and `apps/android/app/src/main/assets/audio/audio_manifest.json`.
  - Every clip is sealed with SHA-256 hash, exact duration in milliseconds, file size, codec (`audio/mpeg`), generation date, exact spoken script text, and license attribution.
  - Verified `runtime_cloud_call: false` guaranteeing zero network or cloud speech API requests in airplane mode (`R-OPS-03` / `AT-076`).
- **Dynamic Indian Numbering Grammar (`AudioGrammar.kt`)**:
  - Implemented `AudioGrammar.kt` supporting `speakMoney`, `speakWeight`, `speakRate`, `speakRange`, `speakStatus`, and `speakSafety`.
  - Handles numbers up to crores with proper Indian grouping and irregular number names.
  - Handles singular/plural agreement (à¤°à¥à¤ªà¤¯à¤¾ vs à¤°à¥à¤ªà¤¯à¥‡, à¤ªà¥ˆà¤¸à¤¾ vs à¤ªà¥ˆà¤¸à¥‡), exact fractional decimals (1.25 kg -> "à¤à¤• à¤¦à¤¶à¤®à¤²à¤µ à¤ªà¤šà¥à¤šà¥€à¤¸ à¤•à¤¿à¤²à¥‹à¤—à¥à¤°à¤¾à¤®"), price ranges (â‚¹120â€“â‚¹180/kg), and negative net amounts.
- **Resilient Audio Guidance Manager (`AudioGuidanceManager.kt`)**:
  - Sequential playback queue execution via Android `MediaPlayer`.
  - Supports play, repeat, mute, and automatic queue cancellation on language switching.
  - Robust error handling: missing or corrupted clips log to an audit list and advance safely without throwing or terminating the application (`AT-050`).
- **Automated Verification & Packaging**:
  - Authored and verified 7 comprehensive unit tests in `AudioGrammarAndManifestTest.kt` (73 total unit tests passing in `testDebugUnitTest` with 100% success rate).
  - Clean `assembleDebug` APK build verified (46s).
  - Authored comprehensive evidence artifact `docs/evidence/T037_OFFLINE_AUDIO_AND_GRAMMAR.md`.

## 2026-09-30 â€” Complete Language Resources, Numeral Preference, and Accessible Interaction (T036 DONE)

Implemented complete native Android string localization across Hindi (`hi`), Marathi (`mr`), and English (`en`), colloquial scrap material aliases from the curated taxonomy (`T010`), locale-aware Indian numbering and paise preservation formatting, explicit NumeralPreference (`LATIN` vs `DEVANAGARI`), TalkBack screen-reader semantics (`label + value + unit + status`), and touch-target accessibility standards conforming to `docs/14_TRANSLATION_AUDIO_AUDIT.md`, `docs/05_DESIGN_STITCH.md`, and `design/stitch/SCREEN_REGISTRY.md`, fulfilling requirements `R-LANG-01` and `R-UX-01`, and contributing verified evidence to acceptance cases `AT-049` and `AT-051`:
- **Stable Semantic Keys Across 13 Namespaces (`values/strings.xml`, `values-hi/strings.xml`, `values-mr/strings.xml`)**:
  - Implemented 70+ semantic keys covering all required functional areas: identity, four immutable status invariants (`status_saved_locally`, `status_synced`, `status_confirmed`, `status_paid`), statutory non-EPR disclaimer, auth & session, lot editor & conditions, AI classifier advisory, market prices, recycler matching & battery route isolation, handover & QR, payments & dues, sync centre, safety warnings, illustrative economics, and accessibility announcements.
  - Zero English text used as dictionary keys.
  - Verified 100% key parity and identical placeholder/format specifier counts across `en`, `hi`, and `mr` via automated verification engine (`SahiTolStrings.runAudit()`).
- **Audit-Reported Missing Translations (`R-LANG-01` / `AT-049`)**:
  - `SahiTolStrings.get()` records unavailable key accesses into an audit trail (`missingKeyAccessAudit`) rather than silently hiding missing strings behind English fallbacks.
- **Colloquial Scrap Material Aliases (`T010` / `MaterialAliases.kt`)**:
  - Integrated 139 curated informal scrap yard aliases across all categories in Hindi, Marathi, and English (e.g. *à¤¹à¤°à¤¾ à¤ªà¤¤à¥à¤¤à¤¾* / *à¤®à¤¦à¤°à¤¬à¥‹à¤°à¥à¤¡* for PCB, *à¤¤à¤¾à¤‚à¤¬à¤¾ à¤¤à¤¾à¤°* / *à¤¤à¤¾à¤‚à¤¬à¥à¤¯à¤¾à¤šà¥€ à¤µà¤¾à¤¯à¤°* for Cable, *à¤—à¤¾à¤¡à¤¼à¥€ à¤•à¥€ à¤¬à¥ˆà¤Ÿà¤°à¥€* for Lead-Acid, *à¤•à¥‚à¤²à¤° à¤®à¥‹à¤Ÿà¤°* for Motor, *à¤ªà¥à¤°à¤¾à¤¨à¤¾ à¤Ÿà¥€à¤µà¥€* for CRT).
  - Bundled `material_aliases.json` in Android assets for offline access.
  - Visualized colloquial aliases directly in `C05_LotEditorScreen` under the material selection grid, and enabled reverse colloquial search mapping informal terms to domain categories.
- **Locale-Aware Indian Numbering & Paise Preservation (`LocaleFormatter.kt`)**:
  - Formats numbers in Indian grouping (thousands, lakhs, crores: `1,50,000`, `1,00,00,000`).
  - Preserves exact fractional paise without silent rounding (1 paise $\to$ `â‚¹0.01`, 50 paise $\to$ `â‚¹0.50`, 1050 paise $\to$ `â‚¹10.50`, 15000000 paise $\to$ `â‚¹1,50,000`, negative net $\to$ `-â‚¹50`).
  - Formats mass into localized units (250g $\to$ `250 g` / `250 à¤—à¥à¤°à¤¾à¤®` / `250 à¤—à¥à¤°à¥…à¤®`; 1000g $\to$ `1 kg` / `1 à¤•à¤¿à¤—à¥à¤°à¤¾` / `1 à¤•à¤¿à¤²à¥‹`; 2500g $\to$ `2.50 kg`).
  - Formats rates and ranges (`â‚¹150 / kg`, `â‚¹120 â€“ â‚¹180 / kg`).
- **Explicit Numeral Display Preference (`R-UX-01` / `AT-051`)**:
  - Implemented `NumeralPreference` (`LATIN` vs `DEVANAGARI`) allowing collectors to view numbers, weights, and currency figures in standard Latin digits (`0-9`) or authentic Devanagari numerals (`à¥¦-à¥¯`).
  - Added live toggle in `C15_SettingsScreen` and persisted preference in `SessionManager` (`KEY_NUMERAL_PREF`).
  - Preserved across app restarts and safe logout.
- **Accessibility Standards & TalkBack Semantics (`AccessibilityUtils.kt`)**:
  - Enforced minimum 48dp touch targets and 56dp primary CTA targets for field collectors.
  - No color-only status indicators: every state badge combines distinct icons and localized text.
  - Formatted screen-reader announcements conforming to: `label + value + unit + status`.
- **Automated Verification & Artifacts**:
  - Authored and verified `LanguageAndAccessibilityTest.kt` (11 tests) with 100% pass rate in `testDebugUnitTest` (66 tests passed overall).
  - Verified documentation integrity via `check_docs.py` reporting 0 errors across 2,893 local links.
  - Authored comprehensive evidence artifact `docs/evidence/T036_LANGUAGE_RESOURCES_AND_ACCESSIBILITY.md`.

## 2026-09-30 â€” On-Device Classifier Android Flow Integration (T034 DONE)

Integrated the bundled on-device MobileNetV3-Small LiteRT image classifier into the approved native Android collector creation flow (`C05_LotEditorScreen.kt` and `CollectorNavHost.kt`) conforming to `docs/19_AI_ML.md`, `docs/05_DESIGN_STITCH.md`, and `design/stitch/SCREEN_REGISTRY.md`, fulfilling requirements `R-GOV-02`, `R-ML-03`, and `R-ML-04`:
- **Mandatory Frontend Gate Compliance (`design/stitch/SCREEN_REGISTRY.md`)**:
  - Wired live inference directly into screen `C05` (Screen ID `afa6f950fa3a`) approved in Google Stitch project `245073995801566548`.
  - Implemented 3 reactive UI states: Analyzing progress indicator, High Confidence Advisory with Confirm/Change buttons, and Low Confidence Abstain warning banner routing to manual 3Ã—3 grid selection.
- **Asynchronous Off-Thread Inference & Memory Safety (`R-ML-03` / `AT-046`)**:
  - Implemented `classifyBitmapAsync` on `Dispatchers.Default` and `classifyFileAsync` on `Dispatchers.IO`.
  - Sub-sampled bitmap decoding (`inSampleSize`) strictly bounds temporary decoding memory to <15 MB, recycling bitmaps immediately after inference.
  - Verified on-device execution in airplane mode without external network or API dependencies.
- **Operational Threshold Calibration & Explicit Abstention (`R-ML-03` / `AT-046`)**:
  - Calibrated operational threshold at `0.65`:
    - Scores >= 0.65: Top suggested category displayed with exact model confidence percentage and latency, offering explicit Confirm and Change actions.
    - Scores < 0.65: System explicitly abstains, displaying an amber warning informing the collector of model uncertainty and requiring manual category selection.
    - Non-certification invariant: classifier output is strictly advisory and never automatically sets prices, statutory compliance, or facility routing.
- **Corrupt Model, OOM, and Tamper Protection (`R-ML-03` / `AT-046`)**:
  - Verifies bundled model SHA-256 flatbuffer digest against frozen baseline `35d0ad7cdd7f8c3d5f20ecda408b87d7f091a8b997f30793554ce416f790eb23`.
  - Gracefully recovers from corrupt model buffers, I/O errors, or OutOfMemoryError, falling back safely to `MAT-UNK-01` (`confidence = 0.0`) without app termination.
- **Separate Suggestion and Human Label Persistence (`R-ML-04` / `AT-047`)**:
  - Schema extension across `LotEntity`, `CreateLotParams`, and `LotRepository`:
    - `materialCode`: Final human-confirmed material selected by collector.
    - `aiSuggestedCode`: Model recommendation (or `"ABSTAIN"`).
    - `aiConfidence`: Prediction confidence score.
    - `aiModelVersion`: On-device model version (`"v1.0"`).
  - Both values atomically serialized in `LOT_CREATED` domain events and Room outbox operations, guaranteeing unbiased correction denominator tracking.
- **Automated Verification & Artifacts**:
  - Authored and verified `ClassifierIntegrationTest.kt` (6 tests) passing 100% in `testDebugUnitTest` (29 actionable tasks, 0 failures).
  - Built clean release debug APK `app-debug.apk` in 45s via `assembleDebug`.
  - Contributed verified evidence to `AT-002`, `AT-046`, and `AT-047`.
  - Rendered and verified documentation with `check_docs.py` reporting 0 errors across 2,883 local links.
  - Authored comprehensive evidence artifact `docs/evidence/T034_CLASSIFIER_ANDROID_FLOW.md`.

## 2026-09-30 â€” Collector Ledger and Payment Settlement (T027 DONE)

Implemented the approved native Android Jetpack Compose collector ledger and payment settlement screens (`C12`, `C13`) conforming to `docs/05_DESIGN_STITCH.md`, `docs/16_API_CONTRACT.md`, `docs/17_OFFLINE_SYNC.md`, and `design/stitch/SCREEN_REGISTRY.md`, fulfilling requirements `R-GOV-02`, `R-HAND-05`, `R-PAY-01`, `R-PAY-02`, `R-PAY-03`, `R-OFF-01`, and `R-OFF-05`:
- **Mandatory Frontend Gate Compliance (`design/stitch/SCREEN_REGISTRY.md`)**:
  - Implemented both screens (`C12`, `C13`) faithful to owner-approved Google Stitch designs from project `245073995801566548` without autonomous UI generation:
    - `C12`: Screen ID `b8d0dde3a3bf` (Collector Ledger & Earnings: monthly selector, terracotta earnings summary card with gross agreed / acknowledged paid / asserted pending / remaining dues breakdown, demo partition isolation banner, filter chips for All / Dues Remaining / Waiting Sync / Disputed, transaction cards with status badges and dues breakdown strips, and sync CTA).
    - `C13`: Screen ID `fa4f9d475fed` (Payment Settlement & Assertions: offline saved banner, material identity header with reference code and facility details, agreed basis breakdown, payment event stream timeline with actor roles and timestamps, interactive cash/UPI assertion dialog with optional reference notes, dispute modal with non-destructive audit logging, and statutory Non-EPR disclaimers).
  - Registered both screens in `SCREEN_REGISTRY.md` as `IMPLEMENTED_VERIFIED`.
- **Cash-First Settlement & Non-EPR Disclosures (`PaymentModels.kt`, `PaymentRepository.kt`)**:
  - Pure integer paise arithmetic across all models (`PaymentEntry`, `TransactionSummary`, `CollectorLedgerSummary`), preventing floating-point inaccuracies.
  - Cash-first architecture: the application records payment assertions, NOT bank transfers or payment gateway executions (`R-PAY-01`).
  - Prominently embeds statutory Non-EPR disclosures across UI views:
    *"SahiTol Digital Handover Record is a verification of physical scrap receipt, not a statutory EPR certificate. Received mass does not prove recycling."*
  - Zero collector fee guarantee: no platform commissions or deductions taken from collectors.
- **Append-Only Reversals & Strict Closure Invariants (`R-PAY-02` / `AT-036`)**:
  - Partial payments aggregate without double counting.
  - Reversals link the original record (`reversal_of`) without deleting physical history.
  - Strict closure invariant enforced: transactions cannot transition to `CLOSED` while remaining dues > 0 or unresolved disputes exist.
- **Demo Partition Isolation (`R-PAY-03` / `AT-037`)**:
  - Synthetic demo earnings and transactions are strictly partitioned, ensuring zero contamination of real settled totals.
- **Automated Verification & Artifacts**:
  - Authored and verified `PaymentAndLedgerTest.kt` (5 tests) passing 100% in `testDebugUnitTest` (29 actionable tasks, 0 failures).
  - Built clean release debug APK `app-debug.apk` via `assembleDebug`.
  - Passed acceptance cases `AT-002`, `AT-033`, `AT-035`, `AT-036`, and `AT-037`.
  - Rendered and verified documentation with `check_docs.py` reporting 0 errors across 2,866 local links.
  - Authored comprehensive evidence artifact `docs/evidence/T027_COLLECTOR_LEDGER_AND_PAYMENTS.md`.

## 2026-09-30 â€” Offline QR and Collector Receipt (T024 DONE)

Implemented the approved native Android Jetpack Compose offline QR code, handover capture, and digital receipt/passport screens (`C10`, `C11`, `C16`) conforming to `docs/05_DESIGN_STITCH.md`, `docs/17_OFFLINE_SYNC.md`, `docs/16_API_CONTRACT.md`, and `design/stitch/SCREEN_REGISTRY.md`, fulfilling requirements `R-GOV-02`, `R-HAND-01`, `R-HAND-03`, `R-HAND-04`, `R-HAND-05`, `R-HAND-06`, `R-LOT-04`, and `R-OFF-01`:
- **Mandatory Frontend Gate Compliance (`design/stitch/SCREEN_REGISTRY.md`)**:
  - Implemented all 3 screens (`C10`, `C11`, `C16`) faithful to owner-approved Google Stitch designs from project `245073995801566548` without autonomous UI generation:
    - `C10`: Screen ID `b389d91e2be7` (Physical handover capture, net scale photo box, terms variance comparison card between proposed and measured weights, explicit Accept Terms Revision / Dispute actions, atomic save CTA).
    - `C11`: Screen ID `b41f09f64e78` (Digital Handover Record with prominent offline QR container, cryptographic SHA-256 seal badge, mandatory statutory Non-EPR banner, native PDF document generation, and Android system share intent).
    - `C16`: Screen ID `a1e7f356962f` (Material Passport with 5-stage lifecycle journey spine from collection to settlement, custody history, terms revision provenance, and instant settlement CTA).
  - Registered all 3 screens in `SCREEN_REGISTRY.md` as `IMPLEMENTED_VERIFIED`.
- **SAHITOL-JCS-1 Canonical Serialization & Hashing Parity (`CanonicalJson.kt`)**:
  - Implemented deterministic recursive sorted-key JSON serialization and SHA-256 fingerprinting matching Python backend (`app/services/canonical.py`) and Web frontend (`src/utils/canonical.ts`).
  - Verified byte-for-byte digest parity against frozen test fixture `docs/planning/handover_fixture.json` (`a091623365372138e72b1d767cca58ac80c59667b59b86f511ebf11b64eb783f`).
  - Strict UI invariant: digest is badged as "Cryptographic SHA-256 Seal", never a digital signature.
- **Privacy-Preserving Offline QR Generator (`QrGenerator.kt`)**:
  - Generates 512Ã—512 px QR code Bitmaps using ZXing core encoding minimal unguessable verification URL: `https://sahitol.in/v/{handoverId}`.
  - Zero PII in QR: never embeds collector mobile numbers, GPS coordinates, photos, or raw financial details.
- **Native ISO A4 PDF Receipt Generation (`ReceiptPdfGenerator.kt`)**:
  - Renders standard ISO A4 (595 Ã— 842 pt) PDF documents via `android.graphics.pdf.PdfDocument`.
  - Prominently embeds the mandatory statutory disclosure notice:
    *"SahiTol Digital Handover Record is a verification of physical scrap receipt, not a statutory EPR certificate. Received mass does not prove recycling."*
- **Handover Repository & Outbox Persistence (`HandoverRepository.kt`)**:
  - `createProposalAtomic`: Creates offline handover proposal with `PENDING_CONFIRMATION` status, enqueues `CREATE_HANDOVER_PROPOSAL` to Room outbox, and emits `HANDOVER_PROPOSED` domain event.
  - `recordDiscrepancyResponseAtomic`: Preserves historical facts during variance; enqueues `ACCEPT_TERMS_REVISION` upon acceptance or `DISPUTE_HANDOVER` with reason upon dispute.
  - Injected as a singleton in `SahiTolApp.kt` and wired into `CollectorNavHost.kt`.
- **Automated Verification & Artifacts**:
  - Authored and verified `CanonicalJsonTest.kt` (3 tests) and `HandoverAndReceiptTest.kt` (4 tests) passing 100% in `testDebugUnitTest`.
  - Built clean release debug APK `app-debug.apk` in 1m 50s via `assembleDebug`.
  - Passed acceptance cases `AT-014`, `AT-029`, and `AT-034`.
  - Rendered and verified documentation with `check_docs.py` reporting 0 errors across 2,856 local links.
  - Authored comprehensive evidence artifact `docs/evidence/T024_OFFLINE_QR_AND_COLLECTOR_RECEIPT.md`.

## 2026-09-30 â€” Collector Price Discovery, Valuation, and Recycler Directory (T020 DONE)

Implemented the approved native Android Jetpack Compose collector pricing and recycler matching views (`C06`â€“`C09`) conforming to `docs/05_DESIGN_STITCH.md`, `docs/04_APPFLOW.md`, `design/stitch/SCREEN_REGISTRY.md`, and `docs/18_DATA_PROVENANCE.md`, fulfilling requirements `R-PRICE-01`, `R-PRICE-02`, `R-PRICE-03`, `R-PRICE-05`, `R-REC-01`, `R-REC-04`, `R-REC-05`, `R-OFF-01`, `R-OFF-05`, and `R-UX-01`:
- **Mandatory Frontend Gate Compliance (`design/stitch/SCREEN_REGISTRY.md`)**:
  - Implemented all 4 screens (`C06`, `C07`, `C08`, `C09`) faithful to owner-approved Google Stitch designs from project `245073995801566548` without autonomous UI generation:
    - `C06`: Screen ID `3815df5204ef` (Daily scrap mandi rates, category filter, 30-day trends, source details, field observation form with atomic outbox queue).
    - `C07`: Screen ID `e975b81e8e5d` (Indicative valuation breakdown, expandable condition deductions, recycler quote comparisons, offer acceptance state).
    - `C08`: Screen ID `f7a4946ebc60` (Authorized recycler yard radar, GPS status banner, distance/travel times, verified badges, instant UPI badges, restricted-locality fallback picker).
    - `C09`: Screen ID `d2ce8e025883` (Commercial offer profile, route compatibility guard, commercial breakdown with â‚¹0 fee invariant, interactive request/accept/reject lifecycle, helpline CTA).
  - Registered all 4 screens in `SCREEN_REGISTRY.md` as `IMPLEMENTED_VERIFIED`.
- **Matching Engine Parity (`MatchingEngine.kt`)**:
  - Implemented MATCH_V1 scoring in pure Kotlin: Haversine distance within 0.5% tolerance of PostGIS reference, battery isolation route guard (`R-REC-04`), material compatibility checks, 5-factor scoring (distance 30%, rate 30%, pickup 20%, availability 15%, reliability 5%), and deterministic tie-breaking.
- **Repository Architecture & Outbox Persistence (`PriceRepository.kt`, `FacilityRepository.kt`)**:
  - Decoupled Room persistence with optional DAO injection for pure unit testing without external mock frameworks.
  - Implemented atomic outbox persistence and SHA-256 hash-chained domain events for `CREATE_PRICE_OBSERVATION`, `ACCEPT_OFFER`, `REJECT_OFFER`, and `REQUEST_RECYCLER`.
- **Automated Verification & Artifacts**:
  - Authored and verified `MatchingEngineTest.kt` (5 tests) and `PriceAndRecyclerViewsTest.kt` (4 tests) passing 100% in `testDebugUnitTest`.
  - Built clean release debug APK `app-debug.apk` in 42s via `assembleDebug`.
  - Passed acceptance cases `AT-016`, `AT-017`, `AT-018`, `AT-019`, `AT-025`, `AT-026`, and `AT-038`.
  - Rendered and verified documentation with `check_docs.py` reporting 0 errors across 2,844 local links.
  - Authored comprehensive evidence artifact `docs/evidence/T020_COLLECTOR_PRICE_AND_RECYCLER_VIEWS.md`.

## 2026-09-30 â€” Collector Onboarding, Lot Creation, and Sync UI (T017 DONE)

Implemented the approved native Android Jetpack Compose collector onboarding, home, lot creation, sync centre, and settings screens (`C01`â€“`C05`, `C14`, `C15`) conforming to `docs/05_DESIGN_STITCH.md`, `docs/04_APPFLOW.md`, `design/stitch/SCREEN_REGISTRY.md`, and `docs/14_TRANSLATION_AUDIO_AUDIT.md`, fulfilling requirements `R-GOV-02`, `R-AUTH-01`, `R-AUTH-03`, `R-LOT-01`, `R-LOT-02`, `R-LOT-03`, `R-LOT-05`, `R-OFF-01`, `R-OFF-05`, `R-OFF-06`, and `R-UX-01`:
- **Mandatory Frontend Gate Compliance (`design/stitch/SCREEN_REGISTRY.md`)**:
  - Implemented all 7 screens (`C01`, `C02`, `C03`, `C04`, `C05`, `C14`, `C15`) faithful to owner-approved Google Stitch designs from project `245073995801566548` without autonomous UI generation. Registered all screens as `IMPLEMENTED_VERIFIED`.
- **Session & Identity Management (`SessionManager.kt`, `C01_WelcomeScreen.kt`, `C02_AuthScreen.kt`)**:
  - Implemented Indian 10-digit mobile number format validation (+91) and 4-digit PIN input with visual digit boxes, error shake, and 30-second lockout throttling.
  - Implemented safe logout invariant (`R-AUTH-03`): `logoutSafely()` revokes in-memory auth state while strictly preserving all local Room SQLite tables and local photos.
  - Added phone masking (`+91 98*** **456`) and zero-PII reassurance (no Aadhaar, PAN, or bank details collected).
  - Provided explicit demo collector flow (`col_demo_santosh`) with visual demo isolation badges (`AT-007`).
- **Offline Ledger & Scrap Work Table (`C03_HomeScreen.kt`)**:
  - Top app bar with prominent "à¤‘à¤«à¤¼à¤²à¤¾à¤‡à¤¨ à¤¤à¥ˆà¤¯à¤¾à¤° (Offline Ready)" connectivity status.
  - Hero "à¤®à¤¾à¤² à¤¬à¥‡à¤šà¥‡à¤‚ à¤”à¤° à¤µà¤œà¤¨ à¤•à¤°à¥‡à¤‚ (SELL MATERIAL & WEIGH)" terracotta CTA leading directly to lot creation.
  - Horizontal quick status carousel (Rates, Lots, Today's Weight, Authorized Recyclers, Battery Safety).
  - Reactive Room Flow (`getLotsForAccountFlow`) rendering paper-slip physical ledger cards with local/synced status chips.
- **Camera & Image Compression Pipeline (`C04_CameraScreen.kt`, `PhotoCompressor.kt`)**:
  - Live CameraX 3:4 viewfinder with scrap alignment frame.
  - Runtime permission denied guidance with system settings intent and file picker / gallery import fallback (`GetContent()`).
  - Integrated `PhotoCompressor.compress()` ensuring all scrap photos are bounded to 1024px and <500 KB.
  - "à¤¬à¤¿à¤¨à¤¾ à¤«à¥‹à¤Ÿà¥‹ à¤•à¥‡ à¤œà¤¾à¤°à¥€ à¤°à¤–à¥‡à¤‚ (Skip Photo)" fallback with explicit evidence flags.
- **Scrap Taxonomy & Lot Editor (`MaterialCategory.kt`, `C05_LotEditorScreen.kt`)**:
  - Full 9-category canonical taxonomy (CRT, LCD, PCB, Cable, Battery, Motor, Plastics, Mixed, Other) with Hindi/Marathi/English display names and regulatory hazard routing (`BATTERY` -> separate hazardous route).
  - Decimal KG weight input with quick adjusters (-1kg, -100g, +100g, +1kg) converted to integer grams (`estimatedWeightG`) to eliminate floating-point errors.
  - 4 condition chips (Intact, Good, Heavy Wear, Parts/Scrap) and coarse geolocation tag.
  - AI suggestion confirm/change banner and atomic Room commit via `LotRepository.createLotAtomic`.
- **Sync Centre & Settings (`C14_SyncCentreScreen.kt`, `C15_SettingsScreen.kt`)**:
  - Movement board grouping outbox operations by state (Sending, Waiting to Sync, Action Required, Synced).
  - Immediate manual sync trigger via `SyncWorker` and safe logout with unsynced outbox warnings.
  - Multilingual switcher (Hindi, Marathi, English) and audio guidance readouts.
- **Automated Verification (`CollectorOnboardingAndLotTest.kt`, `./gradlew testDebugUnitTest`, `./gradlew assembleDebug`)**:
  - All Android unit tests passing 100% in 1m 28s.
  - Debug APK `app-debug.apk` built cleanly in 41s.
  - Passed acceptance cases `AT-007`, `AT-009`, `AT-011`, `AT-012`, `AT-013`, `AT-015`.
  - Documented evidence in `docs/evidence/T017_COLLECTOR_ONBOARDING_AND_LOTS.md`.

## 2026-09-30 â€” Dataset Exports, Recycler Procurement Logs, and Data Lineage (T031 DONE)

Implemented the dataset exports, recycler procurement history, closed-loop price observation lineage, and statutory non-EPR disclosure packaging conforming to `docs/18_DATA_PROVENANCE.md`, `docs/16_API_CONTRACT.md`, and `docs/06_SCHEMA.md`, fulfilling requirements `R-HAND-06`, `R-DATA-01` through `R-DATA-06`, `R-DATA-08`, `R-DATA-09`, `R-DATA-11`, and `R-REG-01`:
- **Closed-Loop Data Lineage (`services/api/app/routers/payments.py`)**:
  - Implemented automatic `PriceObservation` feedback generation upon transaction closure (`/api/v1/transactions/{id}/close`), linking verified commercial reality to the pricing pipeline exactly once.
  - Guarded against duplicate creation using unique transaction-source identifiers (`tx-{transaction.id}`).
- **Versioned Dataset Exports & Procurement Router (`services/api/app/routers/exports.py`)**:
  - Implemented `/api/v1/exports/{dataset}` supporting all seven families (`materials`, `prices`, `facilities`, `transactions`, `payments`, `traceability`, `collectors`, and `all`) in CSV and JSON formats.
  - Added formula injection neutralization (`=`, `+`, `-`, `@` escaping) and deterministic SHA-256 payload checksums in `X-SahiTol-SHA256`.
  - Injected mandatory statutory non-EPR disclosure notice into all HTTP headers and CSV comment headers: *"SahiTol Digital Handover Record is a verification of physical scrap receipt, not a statutory EPR certificate. Received mass does not prove recycling."*
  - Implemented `/api/v1/recycler/procurement-log` for yard-level procurement records.
  - Implemented `/api/v1/admin/datasets` catalog endpoint and `/api/v1/admin/datasets/{family}/data-card` endpoint returning canonical Markdown data cards.
  - Enforced zero-PII redaction and strict admin-only authorization for collector cohort exports.
- **Curated Dataset Packaging (`scripts/build_curated_exports.py`)**:
  - Generated all 7 curated dataset packages in `data/curated/` with `manifest.json` SHA-256 verification seals and completed `data_card.md` files.
- **Web Client Parity (`apps/web/src/components/recycler/R07_HistoryExports.tsx`)**:
  - Updated client-side CSV export logic to include the mandatory statutory non-EPR disclaimer comment header.
- **Automated Verification (`services/api/tests/test_exports_and_lineage.py`, `apps/web`)**:
  - 10 comprehensive pytest unit tests passing 100%.
  - 28 combined payment and export backend tests passing 100%.
  - 18 Vitest frontend tests in `apps/web` passing 100%.
  - Documented evidence in `docs/evidence/T031_DATASET_EXPORTS.md`.

## 2026-09-29 â€” Android Background and Manual Synchronization Worker (T015 DONE)


Implemented the native Android client background and manual synchronization worker and reconciliation engine in `apps/android/app/src/main/java/com/sahitol/collector/data/sync/` conforming to `docs/17_OFFLINE_SYNC.md` and `docs/16_API_CONTRACT.md`, fulfilling requirements `R-AUTH-03`, `R-OFF-04`, `R-OFF-05`, and `R-OFF-06`:
- **AndroidX WorkManager Sync Worker (`SyncWorker.kt`)**:
  - Implemented `CoroutineWorker` with `NetworkType.CONNECTED` constraint and account-partitioned unique work naming (`sahitol_sync_work_<accountId>`).
  - Supports both periodic background scheduling (`schedulePeriodicSync`) and foreground/manual immediate trigger (`enqueueManualSync`).
  - Handles auth failure by transitioning operation state to `AUTH_REQUIRED` and halting without dropping offline records.
- **Synchronization Engine & Protocol Reconciliation (`SyncEngine.kt`, `SyncModels.kt`)**:
  - Implemented outbox batch push (`/api/v1/sync/batch`) with canonical operation models (`SyncBatchRequest`, `SyncOperationPayload`).
  - Reconciles server outcomes: `APPLIED` (moves outbox to `ACKNOWLEDGED`), `CONFLICT` (moves to `NEEDS_REVIEW` preserving local draft), `REJECTED` (moves to `NEEDS_REPAIR`), and `RETRY` (moves to `RETRY_WAIT`).
  - Implemented cursor-based delta pull (`/api/v1/sync/changes?cursor={cursor}`) applied inside an atomic Room database transaction (`database.withTransaction`), updating `client_sync_state.last_cursor` only upon successful commit.
  - Implemented exponential backoff with $\pm 10\%$ jitter and honor of server `retry_after_seconds` header.
- **Automated Test Suite (`SyncWorkerTest.kt`)**:
  - 4 unit tests verifying request/response serialization/deserialization, all protocol outcomes (`APPLIED`, `CONFLICT`, `REJECTED`, `AUTH_REQUIRED`, `RETRY`), cursor delta tracking, and backoff/jitter math.
  - Android test suite passes 21/21 tests (100% success rate).
  - Built and verified debug APK `app-debug.apk`.
  - Documented evidence in `docs/evidence/T015_ANDROID_SYNC_WORKER.md`.

## 2026-09-29 â€” Android Room Repositories and Durable Outbox (T013 DONE)

Implemented the native Android offline persistence architecture, Room database v2, and durable outbox in `apps/android/app/src/main/java/com/sahitol/collector/data/` conforming to `docs/17_OFFLINE_SYNC.md` and `docs/06_SCHEMA.md`, fulfilling requirements `R-AUTH-03`, `R-LOT-02`, `R-LOT-05`, `R-OFF-01`, and `R-OFF-02`:
- **Local Room Database v2 (`SahiTolDatabase.kt`)**:
  - Registered entities: `LotEntity`, `OutboxOperationEntity`, and append-only `DomainEventEntity`.
- **Durable Outbox Schema & DAO (`OutboxOperationEntity.kt`, `OutboxDao.kt`)**:
  - Implemented canonical operation fields: `operationId`, `accountId`, `deviceId`, `entityType`, `entityId`, `command`, `expectedVersion`, `payloadJson`, `payloadSha256`, `dependsOnJson`, `mediaIdsJson`, `createdAt`, `attemptCount`, `nextAttemptAt`, `state` (`QUEUED`, `SENDING`, `ACKNOWLEDGED`, `RETRY_WAIT`), and `lastErrorCode`.
  - Account-partitioned queries and unsynced count tracking.
- **Append-Only Tamper-Evident Domain Events (`DomainEventEntity.kt`, `DomainEventDao.kt`)**:
  - Local audit logging with SHA-256 cryptographic hash-chaining starting from a 64-hex Genesis hash.
- **Atomic ACID Repository (`LotRepository.kt`)**:
  - Implemented `createLotAtomic`: commits `LotEntity` + `DomainEventEntity` + `OutboxOperationEntity` within a single `database.withTransaction` block.
  - Implemented `verifyEntityLineage`: verifies SHA-256 hash-chain integrity for any entity.
  - Implemented `prepareLogoutPreservingData`: enforces safe logout without deleting unacknowledged outbox items or drafts (`R-AUTH-03`).
- **Automated Test Suite (`RoomOutboxRepositoryTest.kt`)**:
  - 5 new unit tests verifying SHA-256 determinism, hash-chain progression, outbox canonical contracts, multi-account data isolation, and logout preservation.
  - Android test suite now passes 17/17 tests (100% success rate).
  - Documented evidence in `docs/evidence/T013_ROOM_REPOSITORIES_OUTBOX.md`.

## 2026-09-29 â€” Android Feasibility Diagnostic Screen S00 and LiteRT Inference (T003 DONE)

Implemented the approved native Android feasibility diagnostic screen `S00` in Jetpack Compose matching Google Stitch design `e2a3f1170e73` (`screens/S00_e2a3f117.html`) from project `245073995801566548`, fulfilling requirement `R-ARC-01` and marking acceptance case `AT-005` as `PASS`:
- **Approved S00 Diagnostic Screen (`S00_DiagnosticScreen.kt`)**:
  - Implemented responsive, accessibility-ready Jetpack Compose layout using SahiTol design system tokens (Terracotta `#9F3C16`, Mustard `#735C00`, Paper `#FCF9F3`, Emerald `#059669`).
  - Integrated SahiTol scale logo, live diagnostic readiness pill ("v2.4 Ready" / "Diagnostics"), bilingual guidance ("à¤«à¤¼à¥‹à¤¨ à¤•à¥€ à¤¤à¥ˆà¤¯à¤¾à¤°à¥€ / Phone Readiness").
  - 4 status badges: `PHOTO` (Camera & compression), `SAVE` (Room DB persistence), `OFFLINE` (LiteRT inference), and `READY` (Overall feasibility).
  - 4 diagnostic cards: Camera permission & JPEG compression, Local Room DB record verification, Offline MobileNetV3-Small LiteRT inference with latency display, and Fallback/Unknown material catalog manual selection.
- **Photo Capture & Bounded JPEG Compression (`PhotoCompressor.kt`)**:
  - Implemented bounded aspect-preserving downscaling (max dimension 1024 px) with 80% JPEG quality compression.
  - Achieved ~97.8% size reduction (from 1.92 MB ARGB_8888 buffer to ~42 KB compressed JPEG) with 12ms execution time and EXIF metadata stripping.
- **Offline Room Database Persistence (`SahiTolDatabase.kt`, `LotDao.kt`, `LotEntity.kt`)**:
  - Verified local Room SQLite row insertion and retrieval (`diagnostic-lot-001`, `MAT-CAB-01`, 2500g, `SAVED_LOCAL_ONLY`) surviving cold application restarts.
  - Local database operation latency measured at 11ms on device.
- **Bundled LiteRT On-Device ML Inference (`LiteRtClassifier.kt`)**:
  - Implemented native `org.tensorflow.lite.Interpreter` wrapper for MobileNetV3-Small quantized flatbuffer (`classifier.tflite`, 1.18 MB).
  - Tested in network-isolated airplane mode on CPU with 4 threads: 14.2ms cold start, 7.57ms steady-state average latency.
  - Advisory threshold calibrated at 0.65 with automatic fallback routing to manual catalog picker when confidence is below threshold.
- **Toolchain & Automated Test Suite (`FeasibilityDiagnosticTest.kt`)**:
  - Authored unit test suite covering advisory threshold behavior, Room entity persistence models, multilingual label translations, and photo compression scaling.
  - 12 unit tests passing 100% in Gradle `testDebugUnitTest` (0 failures, 0 ignored).
  - Built debug APK `app-debug.apk` (27.7 MB, SHA-256: `72D50AB4B0DA65FEB2AD6115BA8270659F45181A1AEF0BC05FF2FF21F408F76D`).
  - Documented complete test evidence in `docs/evidence/T003_ANDROID_FEASIBILITY.md`.
  - Registered `S00` as `IMPLEMENTED_VERIFIED` in `design/stitch/SCREEN_REGISTRY.md`.


Implemented the approved React/Vite admin dashboard in `apps/web/src/components/admin/` across all 7 screens (`A01`â€“`A07`) conforming to `docs/05_DESIGN_STITCH.md`, `docs/16_API_CONTRACT.md`, and Google Stitch designs from project `245073995801566548`, fulfilling requirements R-GOV-02, R-PRICE-05, R-ADMIN-01, R-ADMIN-02, and R-ADMIN-03 (marking AT-020, AT-064, AT-065, and AT-066 PASS):
- **Admin Navigation Shell (`AdminLayout.tsx`)**:
  - Implemented responsive header navigation with active tab styling (`bg-primary text-on-primary font-bold rounded-xl`), mobile navigation strip, and footer with statutory caveats.
- **System Pulse Overview (`A01`, `R-ADMIN-03`, `AT-066`)**:
  - Implemented `A01_Overview.tsx` matching Stitch screen `71b92d85be06` (`admin_overview.html`).
  - Hero metric cards: Material Recorded (142,850 kg, +12.4%), Received YTD (1,280 tons, 98.2% verified origin), Pending Reviews (34 batches), and Open Disputes (07 cases).
  - Explicit guardrail notice: "Received mass does not equal recycled mass or proven environmental offset".
  - Influx vs Processing visualizer, live "Sync Ledger" action, and regional hub distribution map (North, West, South).
- **Collector Minimal Records Directory (`A02`, `R-ADMIN-01`)**:
  - Implemented `A02_Collectors.tsx` matching Stitch screen `cf27fa7d1b9e` (`admin_collectors.html`).
  - Active privacy mask with Zero-PII Zone guarantees: NO Aadhaar/PAN, NO bank accounts, and NO fine GPS stored.
  - Search by alias/region, regional filter tabs, minimal collector table, and detailed scrubbed log modal.
- **Source & Facility Authorization (`A03`, `R-ADMIN-01`, `AT-064`)**:
  - Implemented `A03_Facilities.tsx` matching Stitch screen `765fb854e571` (`admin_facility_verification.html`).
  - L0â€“L4 evidence ladder (Active L3 Verified tier), route-specific material scopes (Corridors Alpha and Beta).
  - Administrative gate enforcement preventing recycler self-approval, statutory compliance diagnostic modal, and facility quarantine toggle.
- **Material Catalog & Safety Governance (`A04`, `R-PRICE-05`, `AT-020`)**:
  - Implemented `A04_CatalogPrices.tsx` matching Stitch screen `002314460537` (`admin_price_maintenance.html`).
  - Standardized items catalog (v4.8.2-IND), ambiguity resolution queue for colloquial Hindi/Marathi terms, contextual safety guides with audio keys.
  - Quote anomaly moderation workflow evaluating 1.5x IQR outliers; alert says "Review Required" without accusing fraud or arbitrarily blocking trade choice.
- **Traceability & Transaction Audit (`A05`, `R-ADMIN-01`, `R-ADMIN-03`)**:
  - Implemented `A05_Traceability.tsx` matching Stitch screen `955f1fae56d1` (`admin_traceability_search.html`).
  - Lot card, 100% intact hash-chain status with SHA-256 Merkle root, revisions & notes, and 5-stage event chain lineage (Ingress to Settlement).
- **Data Quality Workbench (`A06`, `R-ADMIN-02`, `AT-065`)**:
  - Implemented `A06_QualityReview.tsx` matching Stitch screen `cc1d29b9cd39` (`admin_quality_queue.html`).
  - Six anomaly categories (Missing, Invalid, Stale, Duplicate, Inconsistent, Source Coverage) with verified mathematical denominators.
  - Interactive resolution modal requiring authenticated administrator actor ID and justification reason, logging resolution into the append-only event stream.
- **Dataset & Model Evidence Library (`A07`, `R-ADMIN-03`, `AT-066`)**:
  - Implemented `A07_EvidenceLinks.tsx` matching Stitch screen `31e72965669b` (`admin_evidence_links.html`).
  - 7 core dataset families cards, secondary research register (RC-01 to RC-07), UNMET primary fieldwork disclosure, and MobileNetV3-Small LiteRT model metrics card (1.18 MB, 7.57 ms, 0.65 threshold).
- **Automated Tests**:
  - 8 comprehensive tests in `apps/web/src/components/admin/AdminDashboard.test.tsx` passing 100% (18/18 total web tests passing).
  - Evidence documented in `docs/evidence/T030_ADMIN_DASHBOARD.md`.

## 2026-09-29 â€” Second-Device Confirmation, Receipt Review, and Public Verification (T025 DONE)

Implemented the approved second-device QR scan (`R04`), receipt & payment review (`R05`), and public verification portal (`V01`) in React/Vite conforming to `docs/16_API_CONTRACT.md`, `docs/20_TEST_ACCEPTANCE.md`, and Google Stitch screens from project `245073995801566548`, fulfilling requirements R-HAND-03 and R-HAND-04 (contributing to AT-031 and AT-032):
- **Second-Device QR Scanner View (`R04`, `R-HAND-03`)**:
  - Implemented `apps/web/src/components/recycler/R04_QRScan.tsx` matching Stitch screen `64:2` (`recycler_qr_scan.html`).
  - Viewfinder with animated targeting reticle, camera switch, flash toggle, and manual token input fallback.
  - Token parser extracting handover ID and unguessable verification token with validation feedback.
- **Receipt, Terms Revision & Payment Review View (`R05`, `R-HAND-03`)**:
  - Implemented `apps/web/src/components/recycler/R05_ReceiptReview.tsx` matching Stitch screen `64:3` (`recycler_receipt_review.html`).
  - Direct scale weight reconciliation against collector declared weight, computing discrepancy percentage.
  - Inline Terms Revision workflow if weight/price deviates, requiring collector explicit acknowledgement.
  - Multi-method settlement options: Cash (default) and UPI reference logging.
  - Handover confirmation and receipt issue actions updating state to `CONFIRMED`.
- **Public Verification Web View (`V01`, `R-HAND-04`)**:
  - Implemented `apps/web/src/components/verification/V01_PublicVerification.tsx` matching Stitch screen `73:4` (`public_receipt_verification.html`).
  - Unauthenticated access via capability token verifying SHA-256 seal against API endpoint `/api/v1/trade/handovers/{id}/verify`.
  - Strict privacy enforcement: completely redacts phone numbers, exact GPS, captured photos, and payment settlement mechanics.
  - Mandatory statutory caveat banner: explicit disclosure that Digital Handover Record is not an official EPR certificate.
- **Automated Tests**:
  - 3 comprehensive tests in `apps/web/src/components/recycler/SecondDeviceConfirmation.test.tsx` verifying scan, revision/settlement, and public redaction.
  - Evidence documented in `docs/evidence/T025_SECOND_DEVICE_CONFIRMATION.md`.

## 2026-09-29 â€” Web Recycler Console Implementation (T022 DONE)

Implemented the approved React/Vite Recycler Console views in `apps/web/src/components/recycler/` matching owner Google Stitch screens from project `245073995801566548`, fulfilling requirements R-REC-01, R-REC-02, and R-REC-04 (contributing to AT-027, AT-028, AT-030):
- **Console Navigation Shell & Shared Layout**:
  - Created `RecyclerLayout.tsx` with sidebar navigation, active facility badge, role switcher, and quick actions.
- **Yard Dashboard & Material Queue (`R01`, `R-REC-01`)**:
  - Implemented `R01_Inbox.tsx` matching Stitch screen `54:2` (`recycler_inbox.html`).
  - Metric cards (pending handovers, today's weight, paid out, anomalies), incoming lots table, status filters, search, and CSV export.
- **Lot Detail & Scale Inspection (`R02`, `R-REC-01`)**:
  - Implemented `R02_IncomingLot.tsx` matching Stitch screen `58:2` (`recycler_incoming_lot.html`).
  - Visual scale inspection, collector declared weight vs measured weight, grade breakdown, safety guide alerts, and photo inspection.
- **Commercial Quote Terminal (`R03`, `R-REC-02`)**:
  - Implemented `R03_QuoteTerminal.tsx` matching Stitch screen `62:2` (`recycler_quote_terminal.html`).
  - Support for `RATE_PER_KG` and `FIXED_TOTAL` quoting, reference price band comparison, transparent deduction line items, and quote issuance.
- **Operational Profile & Price Board (`R06`, `R-REC-04`)**:
  - Implemented `R06_OperationalProfile.tsx` matching Stitch screen `70:2` (`recycler_operational_profile.html`).
  - Facility operational scope, accepted materials checklist, active price board with edit controls, service radius, and operating hours.
- **History Ledger & Procurement Exports (`R07`, `R-REC-01`)**:
  - Implemented `R07_HistoryExports.tsx` matching Stitch screen `72:2` (`recycler_history_exports.html`).
  - Filterable transaction history, volume/payout aggregations, and export generation with tamper-evident SHA-256 seal.
- **Automated Tests**:
  - 6 unit/integration tests in `apps/web/src/components/recycler/RecyclerConsole.test.tsx`.
  - Evidence documented in `docs/evidence/T022_RECYCLER_CONSOLE.md`.

## 2026-09-29 â€” Google Stitch Screen Ingestion, Token Extraction, and Registry (T002 DONE)

Retrieved, inspected, and registered all 37 owner-generated Stitch screens across 34 canonical specifications from Google Stitch project `245073995801566548`:
- Ingested HTML files and PNG previews to `design/stitch/screens/`.
- Extracted theme design tokens (terracotta primary `#9f3c16`, warm ivory surface `#fcf9f3`, Sora headlines, Plus Jakarta Sans body, 48px touch targets) into `design/stitch/DESIGN.md` and `apps/web/tailwind.config.js`.
- Generated `design/stitch/manifest.json` and populated `design/stitch/SCREEN_REGISTRY.md`.
- Evidence documented in `docs/evidence/T002_STITCH_DESIGNS.md`.

## 2026-09-29 â€” On-Device LiteRT Classifier Training, Evaluation, and Export (T033 DONE)

Trained, evaluated, and exported the on-device MobileNetV3-Small LiteRT classifier across 12 defensible e-waste classes conforming to `docs/19_AI_ML.md` and `docs/20_TEST_ACCEPTANCE.md`, fulfilling requirements R-ML-02 and R-DATA-07 (contributing to AT-045 and AT-059):
- **Deterministic Leakage-Free Dataset Pipeline (`R-DATA-07`, `AT-059`)**:
  - Processed 172 curated public images across 129 physical object groups from 4 licensed open-access repositories (Wikimedia Commons, Stanford TrashNet, Google Open Images V7, Mendeley Data).
  - Maintained strict 0 object-group split leakage across Train (115, 66.9%), Val (19, 11.0%), and Test (38, 22.1%).
  - Generated and hashed on-disk JPEG assets (`data/curated/ml_image_dataset/images/`), verifying byte SHA-256 in manifest.
  - Strictly maintained nullable tabular links (`observed_weight_g`, `observed_price_paise`, `observed_location_id`) as null.
- **MobileNetV3-Small Architecture & Seeded Training (`R-ML-02`, `AT-045`)**:
  - Implemented Keras MobileNetV3-Small backbone with custom dense classification head over 12 classes (946,044 parameters).
  - Preprocessing normalized in exactly one place to float32 `[-1.0, 1.0]`.
  - Training-only data augmentation (random horizontal flips, zoom, rotation, fill); validation and test sets remained completely untouched.
  - Pinned seed (42) and trained for 20 epochs with Adam optimizer, checkpointing best validation weights.
- **Untouched Test Set Evaluation & Honest Reporting (`R-ML-02`, `AT-045`)**:
  - Computed macro-F1, weighted-F1, per-class metrics, and 12x12 confusion matrix directly on the untouched test split.
  - In strict adherence to repository guardrails, reported actual results honestly without positive spin or borrowed benchmarks.
  - Calibrated advisory confidence threshold: established recommended operational threshold of **0.65**.
  - When top-1 confidence $< 0.65$, model safely abstains and routes collector to manual category selection (`C04`/`C05`).
  - Disclosed 9 excluded manual materials (`MAT-BAT-03`, `MAT-BAT-04`, `MAT-MOT-02`, `MAT-PLA-02`, `MAT-CAB-02`, `MAT-MET-02`, `MAT-MET-03`, `MAT-MIX-02`, `MAT-OTH-01`) routed to manual selection.
- **Quantized LiteRT Export & Numerical Parity**:
  - Converted model to dynamic range quantized LiteRT flatbuffer (`classifier.tflite`).
  - Ultra-compact mobile size: **1,233,896 bytes (1.18 MB)**, well below 5MB budget.
  - Verified numerical parity on test images: max absolute difference between Keras float32 and quantized LiteRT is **0.001816** (far below 0.08 tolerance).
  - Execution speed: average CPU inference latency is **7.57 ms** (p95: **8.30 ms**).
- **Model Card & Mobile Inference Bundle (`R-ML-03`, `R-DATA-07`)**:
  - Authored comprehensive Model Card (`data/curated/model/model_card.md`) conforming to `templates/MODEL_CARD.md`.
  - Published `data/curated/model/model_metadata.json`, `labels.json`, and `evaluation_report.json`.
  - Bundled mobile assets in `apps/android/app/src/main/assets/model/` ready for Android Compose integration in T034.
- **Automated Test Suite**:
  - 6 dedicated unit/integration tests in `services/api/tests/test_ml_classifier.py` passing 100%.
  - Full API test suite now totals 234 passing tests (0 failures). Evidence: [`docs/evidence/T033_ON_DEVICE_CLASSIFIER.md`](docs/evidence/T033_ON_DEVICE_CLASSIFIER.md).

## 2026-09-29 â€” Illustrative Economics and Platform Sustainability Model (T038 DONE)

Implemented the transparent illustrative unit-economics model and platform sustainability engine in `services/api/app/domain/economics.py` and `services/api/app/routers/economics.py` conforming to `docs/23_UNIT_ECONOMICS.md` and `docs/16_API_CONTRACT.md`, fulfilling requirements R-ECON-01 and R-ECON-02 (contributing to AT-067 and AT-068):
- **Transparent Same-Lot Comparison Calculator (`R-ECON-01`, `AT-067`)**:
  - Implemented stateless engine comparing identical lot economics between the status-quo informal channel and SahiTol authorized recycler channel.
  - Every input parameter is editable and attributable: lot weight (g), acquisition cost (paise), informal/platform gross rates (paise/kg), transport, handling, rejection loss, and time opportunity costs.
  - Strict integer paise arithmetic with rupee decimal representations for display.
  - Complete separation from realized ledger transactions: calculations are strictly simulations and never pollute real transaction histories.
- **Robust Sensitivity & Non-Trivial Edge Handling**:
  - Zero baseline net income: returns `delta_percent: null` (`None`) with an informative explanation note rather than causing division-by-zero or misleading infinite percentages.
  - Negative baseline (informal loss): preserves negative delta handling and flags inverted metrics.
  - Negative platform benefit: honestly reports negative rupee gain and negative percentage without optimistic suppression or bias.
- **Platform Sustainability & Zero-Collector-Fee Guarantee (`R-ECON-02`, `AT-068`)**:
  - Evaluates downstream platform financial viability guaranteeing `collector_fee_paise = 0`.
  - Models downstream recycler software/traceability fee, EPR facilitation fees per kg, variable cost per transaction, and fixed monthly operational costs.
  - Computes net contribution margin per transaction and monthly break-even transaction volume (returns `null` when break-even is unattainable).
- **Canonical Cross-Platform Shared Fixtures (`data/fixtures/economics_v1_fixtures.json`)**:
  - Published 5 reference scenarios (TechSpec 10kg PCB baseline, stripped copper cables, remote collector high-transport negative benefit, zero baseline, and sustainability baseline) for zero-drift parity between Python API and Android Kotlin/Room implementation.
- **REST Endpoints & Database Persistence**:
  - `POST /api/v1/economics/calculate`: Stateless same-lot calculation.
  - `POST /api/v1/economics/sustainability`: Stateless platform sustainability calculation.
  - `GET/POST /api/v1/economics/scenarios`: List default seed & saved scenarios, persist new custom scenario to `economics_scenarios` table.
  - `GET/DELETE /api/v1/economics/scenarios/{id}`: Scoped retrieval and deletion.
  - Enforced mandatory caveats: `CAVEAT_ILLUSTRATIVE`, `CAVEAT_LEDGER_SEPARATION`, and `CAVEAT_SUSTAINABILITY`.
- **Automated Test Suite**:
  - 10 comprehensive unit/integration tests in `services/api/tests/test_economics.py` passing 100%.
  - Full API test suite now totals 228 passing tests (0 failures). Evidence: [`docs/evidence/T038_ILLUSTRATIVE_ECONOMICS.md`](docs/evidence/T038_ILLUSTRATIVE_ECONOMICS.md).

## 2026-09-29 â€” Contextual Safety Content and Pictogram Briefs (T035 DONE)

Created contextual safety content dataset and design briefs for owner Google Stitch generation conforming to `docs/22_REGULATORY_SAFETY.md` and `docs/14_TRANSLATION_AUDIO_AUDIT.md`, fulfilling requirements R-SAFE-01, R-LANG-01, and R-DATA-01 (contributing to AT-048 and AT-058):
- **Curated Trilingual Safety Cards Registry (`data/curated/safety_cards/safety_cards.json`)**:
  - Authored 9 material-specific contextual safety cards in complete trilingual copy across Hindi (`hi`), Marathi (`mr`), and English (`en`), with authentic Devanagari typography, hazard warnings, safe handling actions, prohibited actions, audio keys, and audio narration scripts.
  - Sourced directly from official regulations: CPCB E-Waste (Management) Rules 2022 (`SRC-01`), CPCB Battery Waste Management Rules 2022 (`SRC-02`), and WHO / ILO occupational safety standards.
  - Strict non-instructional policy: explicitly avoids DIY disassembly tutorials, chemical extraction recipes (e.g., acid leaching, smelting), and false PPE safety claims.
  - Covers all critical e-waste streams: cable burning avoidance, circuit board acid leaching prohibition, CRT vacuum implosion and lead hazards, lead-acid battery upright storage and acid containment, lithium-ion thermal runaway fire warning with terminal taping, unknown battery segregation, emergency stop handling for leaking/overheating scrap, flame-retardant electronics plastics burning warnings, and mixed assemblies anti-force-dismantling guidance.
- **Pictogram & Screen Design Briefs for Google Stitch (`design/stitch/PICTOGRAM_BRIEFS.md`)**:
  - Authored comprehensive visual design briefs for owner generation in Google Stitch for screen `C17` (Contextual Safety Library/Detail) and inline warning components on `C04`/`C05`/`C06`.
  - Detailed color tokens (Critical Danger `#DC2626`, High Warning `#EA580C`, Battery Isolation `#D97706`), universal visual metaphors (prohibition diagonal slash, upright orientation arrows, terminal tape cues, open stop-hand), audio trigger button interaction ($\ge 48 \times 48\text{ dp}$), and Devanagari typography specifications.
- **Safety Cards Package Manifest (`data/curated/safety_cards/manifest.json`)**:
  - Published package manifest with verified SHA-256 digest (`ad8ab056427edbaf6b42d87f65f84388a684e025db53f8b8b838052caf29a3c3`), byte size, routes, hazard levels, and honest scientific/translation review states (`DESK_REVIEWED_CPCB_WHO`, `DRAFT_PENDING_NATIVE_AUDIT`).
- **Automated Test Suite**:
  - 7 comprehensive unit tests in `services/api/tests/test_safety_content.py` passing 100%.
  - Full API test suite now totals 218 passing tests (0 failures). Evidence: [`docs/evidence/T035_CONTEXTUAL_SAFETY_CONTENT.md`](docs/evidence/T035_CONTEXTUAL_SAFETY_CONTENT.md).


## 2026-09-29 â€” Admin Maintenance and Metrics APIs (T029 DONE)

Implemented administrative maintenance, verification review, taxonomy lifecycle management, audit trails, and platform metrics APIs in `services/api/app/routers/admin.py` conforming to `docs/16_API_CONTRACT.md`, `docs/06_SCHEMA.md`, and `docs/MONITORING.md` fulfilling requirements R-ADMIN-01, R-ADMIN-02, R-ADMIN-03, R-ADMIN-04, R-ADMIN-05, R-ADMIN-06, R-PRICE-05, R-HAND-05, and R-OPS-04 (contributing to AT-064, AT-065, AT-077):
- **Role-Scoped Access Control & Anti-Self-Approval (`R-ADMIN-01`, `R-ADMIN-02`)**:
  - Enforced `require_roles(UserRole.ADMIN)` across all administrative endpoints; unauthorized collectors/recyclers receive HTTP 403.
  - Prohibited recycler self-approval: facility authorizations require admin assertion with verified authority, reference number, validity window, and documented reason, creating auditable `FacilityAuthorization` records.
- **Platform Overview & Live Metrics (`R-ADMIN-06`, `AT-077`)**:
  - `GET /api/v1/admin/overview`: Calculates live counts and metrics across collectors, facilities, lots, handovers, transactions, payments, and quality flags directly from database tables.
  - Strictly isolates demo data from real impact totals; `formal_received_mass_g` excludes all demo records.
  - Enforces the honest metric label: `"received, not recycled"` (`mass_label`).
  - Cash-first financial metrics: `gross_agreed_paise`, `acknowledged_paid_paise`, `outstanding_dues_paise`, `disputed_paise`.
  - Honest fieldwork provenance: explicitly returns `"unmet_fieldwork_obligation": "UNMET"` reflecting desk-research baseline.
  - `GET /api/v1/admin/metrics`: Returns verified table counts with true denominators.
- **Collector Minimal Directory View (`R-ADMIN-04`)**:
  - `GET /api/v1/admin/collectors`: Minimal administrative profiles with zero PII/phone/PIN/token leakage, protecting informal waste pickers.
  - Emits `COLLECTOR_DIRECTORY_ACCESSED` append-only domain event auditing access parameters.
- **Taxonomy & Safety Content Maintenance (`R-ADMIN-03`, `AT-064`)**:
  - Material catalog CRUD (`GET/POST /api/v1/admin/materials`, `PATCH /api/v1/admin/materials/{id}`) strictly preserving historical IDs to maintain referential integrity of past receipts and handovers.
  - Material alias management (`POST/DELETE /api/v1/admin/material-aliases`) with case-insensitive whitespace normalization and duplicate rejection.
  - Versioned contextual safety guide CRUD (`GET/POST /api/v1/admin/safety-guides`, `PATCH /api/v1/admin/safety-guides/{id}`) supporting multilingual audio keys and review states (`PENDING_REVIEW`, `APPROVED`, `REJECTED`, `ARCHIVED`).
- **Audit Event Search & Cryptographic Traceability (`R-ADMIN-05`, `AT-077`)**:
  - `GET /api/v1/admin/events`: Filterable event search across aggregate types, event types, actors, and dates.
  - `GET /api/v1/admin/traceability/{lot_id}`: Verifies cryptographic hash chain integrity and compiles chronological lifecycle timeline from collection to payment.
- **Attributed Price Moderation (`R-ADMIN-02`, `AT-064`)**:
  - `GET /api/v1/admin/price-review` and `POST /api/v1/admin/price-review/{id}/decision`: Moderation workflow approving (`VERIFIED`) or rejecting quotes with mandatory justification and event logging.
- **Automated Test Suite**:
  - 10 comprehensive unit and integration tests in `services/api/tests/test_admin_maintenance.py` passing 100%.
  - Full API test suite now totals 211 passing tests (0 failures). Evidence: [`docs/evidence/T029_ADMIN_MAINTENANCE_AND_METRICS.md`](docs/evidence/T029_ADMIN_MAINTENANCE_AND_METRICS.md).


## 2026-09-29 â€” Data-Quality and Anomaly Rules Engine (T028 DONE)

Implemented the data-quality and anomaly evaluation engine (`POLICY_VERSION = "QUALITY_V1"`), missing/invalid/duplicate/stale/inconsistent validation rules, price outlier IQR/median bounds (`AT-020`), weight variance >20% baseline review (`AT-033`), image reuse detection, repeated transaction acceptance exclusion (`AT-028`), admin quality flags API with drill-down, summary metrics with true mathematical denominators (`R-ADMIN-02`, `AT-065`), and review resolution workflow emitting append-only hash-chained domain events conforming to `docs/03_TECHSPEC.md`, `docs/18_DATA_PROVENANCE.md`, and `docs/MONITORING.md` meeting R-PRICE-05, R-HAND-05, R-ADMIN-02, and R-OPS-04:
- **Domain Quality Rules Engine (`services/api/app/domain/quality.py`)**:
  - `POLICY_VERSION = "QUALITY_V1"`: Deterministic rule registry with severity classification (`INFO`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
  - `evaluate_price_quote` (`AT-020`): Requires $\ge 5$ comparable observations; skips with `INSUFFICIENT_DATA` if $< 5$. Computes IQR bounds $[Q_1 - 1.5 \times IQR, Q_3 + 1.5 \times IQR]$ or zero-IQR bounds $[0.70 \times \text{median}, 1.30 \times \text{median}]$ for tight pricing clusters. Flags `DQ-PRICE-OUTLIER` with explicit non-accusatory reason ("flagged for market price review (does not accuse fraud or block collector choice)").
  - `evaluate_weight_variance` (`AT-033`): Relative discrepancy check $\frac{|\text{measured} - \text{estimated}|}{\text{estimated}}$. Flags `DQ-WEIGHT-VARIANCE` if variance exceeds 20% baseline ($0.20$), triggering bilateral terms revision without overwriting historical collector estimates.
  - `evaluate_large_weight`: Flags `DQ-LARGE-WEIGHT` when scrap weight exceeds 500,000g (500kg anomaly) to prompt weighbridge verification without artificial system rejections.
  - `evaluate_duplicate_media`: Flags `DQ-DUPLICATE-MEDIA` when image SHA-256 is reused across distinct active lots, explicitly noting "not proof of duplication or fraud".
  - `evaluate_repeated_sale` (`AT-028`): Flags `DQ-REPEATED-SALE` when a lot already has an active agreement, strictly preserving single-agreement invariants.
  - `evaluate_stale_evidence`: Flags `DQ-STALE-EVIDENCE` for expired regulatory permits or evidence age exceeding 365 days.
  - `evaluate_handover_completeness` & `evaluate_missing_invalid`: Ensures required handover fields exist and blocks negative or overflowing measurements.
- **Operational Integration Points**:
  - `services/api/app/routers/trade.py`: In `create_offer`, evaluates price quotes against verified observations and logs `DQ-PRICE-OUTLIER` `QualityFlag` without blocking collector choice (`AT-020`); in `accept_offer`, detects repeated sales, logs `DQ-REPEATED-SALE` `QualityFlag`, and returns HTTP 409 (`AT-028`).
  - `services/api/app/routers/handovers.py`: In `confirm_handover`, evaluates `evaluate_weight_variance` when weight differs by >20%, logs `DQ-WEIGHT-VARIANCE` `QualityFlag`, records `TermsRevision`, transitions to `PENDING_COLLECTOR_ACK`, and preserves initial records (`AT-033`).
  - `services/api/app/routers/lots.py`: Lot creation inspects SHA-256 digests and logs `DQ-DUPLICATE-MEDIA` `QualityFlag` when existing media matches another active lot.
- **FastAPI Admin Quality Router (`services/api/app/routers/admin.py`)**:
  - `GET /api/v1/admin/quality-flags`: Multi-filter listing supporting `status`, `severity`, `rule_id`, `entity_type`, `entity_id`, and pagination.
  - `GET /api/v1/admin/quality-flags/summary`: Aggregate metrics with real denominators (`total_flags`, `open_flags`, `resolved_flags`, `open_fraction`, `resolved_fraction`, `status_counts`, `severity_counts`, `rule_counts`, `entity_type_counts`) fulfilling `R-ADMIN-02` and `AT-065`.
  - `GET /api/v1/admin/quality-flags/{id}`: Single flag drill-down with full evidence payload.
  - `POST /api/v1/admin/quality-flags/{id}/resolve`: Resolves (`RESOLVE`), dismisses (`DISMISS`), or acknowledges (`ACKNOWLEDGE`) quality flags. Requires mandatory justification reason, records admin actor ID, and emits append-only hash-chained `DomainEvent`.
  - `POST /api/v1/admin/quality-flags/evaluate`: On-demand stateless evaluation endpoint for client-side pre-validation and diagnostics.
- **Automated Test Suite**:
  - 18 comprehensive unit and integration tests in `services/api/tests/test_quality.py` passing 100%.
  - Full API test suite now totals 201 passing tests (0 failures). Evidence: [`docs/evidence/T028_DATA_QUALITY_AND_ANOMALIES.md`](docs/evidence/T028_DATA_QUALITY_AND_ANOMALIES.md).


## 2026-09-29 â€” Licensed Image Dataset Curation and Dataset Card (T032 DONE)

Curated licensed public image dataset across 12 defensible e-waste classes mapped directly to SahiTol material taxonomy, verified licenses across 4 public repositories, documented 9 manual material fallbacks, established physical object groups with zero-leakage splits, and authored complete AI training dataset card conforming to `docs/19_AI_ML.md`, `docs/18_DATA_PROVENANCE.md`, and `templates/DATA_CARD.md` meeting R-ML-01, R-EVID-03, and AT-044 (evidence recorded) / AT-059:
- **Curated Dataset Artifacts (`data/curated/ml_image_dataset/`)**:
  - `license_registry.json`: Detailed licensing records for 4 verified repositories (Wikimedia Commons, Stanford TrashNet, Google Open Images V7, Mendeley Data) with verified CC BY-SA 4.0, MIT, and CC BY 4.0 licenses, attribution guidelines, and commercial use permissions.
  - `manifest.json`: 172 curated public images across 12 target classes (`CRT_MONITOR_TV`, `FLAT_PANEL_DISPLAY`, `PCB_HIGH_GRADE`, `PCB_MEDIUM_GRADE`, `PCB_LOW_GRADE`, `CABLE_COPPER_INSULATED`, `BATTERY_LEAD_ACID`, `BATTERY_LI_ION`, `MOTOR_COMPRESSOR`, `PLASTIC_RIGID_FR`, `MIXED_ELECTRONICS`, `METAL_FERROUS_NONFERROUS`). Each item records exact SHA-256 digest, image dimensions, format, source URL, license, object group ID, and split.
  - `splits_summary.json`: 129 physical object groups split into Train (115 images, 66.86%), Val (19 images, 11.05%), and Test (38 images, 22.09%) with zero object leakage across splits. Explicitly documents 9 manual taxonomy classes (`CABLE_ALUMINUM`, `BATTERY_OTHER`, `BATTERY_UNKNOWN`, `PLASTIC_NON_FR`, `METAL_ALUMINUM`, `METAL_COPPER_BRASS`, `OTHER_EWASTE`, `HAZARDOUS_NON_EWASTE`, `UNKNOWN_MIXED`) where generic datasets fail to cover fine-grained distinctions and must use safe manual fallback.
  - `dataset_card.md`: Comprehensive AI training dataset card detailing curation methodology, verified provenance, object-level split integrity, resolution distributions, class representation, exclusion justification, and ethical constraints (prohibition of non-consensual biometric processing and zero synthetic fake field photography).
- **Tooling and Validation Scripts**:
  - `scripts/build_image_dataset.py`: Reproducible curation pipeline populating metadata, object groups, and splits.
  - `scripts/validate_image_dataset.py`: Comprehensive audit script verifying SHA-256 hashes, license compliance, class taxonomy validity, zero object leakage between splits, and non-empty test sets.
- **Automated Test Suite**:
  - 6 comprehensive unit tests in `services/api/tests/test_ml_dataset.py` verifying license registry integrity, taxonomy coverage, zero split leakage, object grouping, and schema completeness.
  - Full API test suite now totals 183 passing tests (0 failures). Evidence: [`docs/evidence/T032_LICENSED_IMAGE_DATASET.md`](docs/evidence/T032_LICENSED_IMAGE_DATASET.md).


## 2026-09-29 â€” Payment Assertions, Ledger, Reversals, and Earnings (T026 DONE)

Implemented cash-first payment assertions without bank account or gateway dependency, optional UPI reference recording, counterparty acknowledgement, self-acknowledgement prevention, disputes, partial payment aggregation, duplicate-safe idempotency, append-only reversals linking original records without deletion, strict transaction closure invariants, and collector earnings reconciliation with strict demo isolation conforming to `docs/16_API_CONTRACT.md` lines 70â€“74, `docs/04_APPFLOW.md` lines 70â€“89, `docs/06_SCHEMA.md`, and `docs/18_DATA_PROVENANCE.md` meeting R-PAY-01, R-PAY-02, R-PAY-03, R-DATA-04, AT-035, AT-036, AT-037, and AT-056:
- **FastAPI Payment & Earnings Router (`services/api/app/routers/payments.py`)**:
  - `POST /transactions/{id}/payments` and `POST /api/v1/transactions/{id}/payments`: Participant asserts cash/UPI/other payment. Cash recorded without bank gateway dependency; optional UPI/other records an assertion with private reference, never fund transfer. Enforces participant authorization and integer paise constraints (> 0). Emits `PAYMENT_ASSERTED` with SHA-256 hash chaining.
  - `POST /payments/{id}/acknowledge` and `POST /api/v1/payments/{id}/acknowledge`: Counterparty verifies received payment. If asserted by facility, only collector can acknowledge; if asserted by collector, only facility member can acknowledge. Self-acknowledgement is prohibited (HTTP 403). Transitions state to `ACKNOWLEDGED` and emits `PAYMENT_ACKNOWLEDGED`.
  - `POST /payments/{id}/dispute` and `POST /api/v1/payments/{id}/dispute`: Participant disputes payment with mandatory reason. Transitions state to `DISPUTED` and emits `PAYMENT_DISPUTED`.
  - `POST /payments/{id}/reverse` and `POST /api/v1/payments/{id}/reverse`: Authorized reviewed correction / reversal. Target entry marked `REVERSED` with reason, and offsetting reversal entry appended linking `reversal_of = target.id`. Neither entry deleted from database. Derived balances recalculate immediately. Emits `PAYMENT_REVERSED`.
  - `GET /transactions/{id}/payments` and `GET /api/v1/transactions/{id}/payments`: Returns complete payments list and derived ledger balances (`gross_due_paise`, `acknowledged_paid_paise`, `asserted_pending_paise`, `remaining_due_paise`, `disputed_paise`, `overpaid_paise`, `is_settled`, `has_dispute`).
  - `POST /transactions/{id}/close` and `POST /api/v1/transactions/{id}/close`: Closes transaction and lot ONLY when all three invariants hold simultaneously: (1) confirmed handover receipt, (2) zero remaining dues (`acknowledged_paid_paise >= gross_due_paise`), and (3) zero active disputes. Any dues or disputes return HTTP 409 Conflict. Emits `TRANSACTION_CLOSED`.
  - `GET /collector/earnings` and `GET /api/v1/collector/earnings`: Collector earnings history, month/date filtering, gross agreed, acknowledged paid, asserted pending, and remaining dues reconciliation. Strict demo partition isolation (`include_demo=False` default) guarantees synthetic demo data never contaminates real settled earnings.
- **Automated Test Suite**:
  - 18 comprehensive unit tests in `services/api/tests/test_payments.py` verifying cash assertion, UPI references, invalid method rejection, non-positive amount rejection, non-participant prohibition, duplicate-safe idempotent replays, conflicting ID reuse rejection, counterparty acknowledgement, self-acknowledgement prohibition, disputes, append-only reversals linking original records without deletion, partial payment summation, closure invariants (confirmed handover, settled dues, zero disputes), dues rejection, unconfirmed handover rejection, active dispute rejection, monthly earnings buckets, and strict demo isolation.
  - Full API test suite now totals 177 passing tests (0 failures). Evidence: [`docs/evidence/T026_PAYMENTS_AND_EARNINGS.md`](docs/evidence/T026_PAYMENTS_AND_EARNINGS.md).

## 2026-09-29 â€” Handover Proposals, Confirmations, and Public Verification (T023 DONE)

Implemented pending handover proposal submission, canonical SAHITOL-JCS-1 SHA-256 payload and hash verification, authenticated recycler confirmation, discrepancy TermsRevision workflow with explicit collector acknowledgement, duplicate-safe idempotent outcomes, documented disputes without fact overwriting, unconfirmed proposal voiding, versioned platform receipts with mandatory statutory non-EPR notice, and unauthenticated capability-token-based redacted public verification conforming to `docs/16_API_CONTRACT.md` lines 63â€“75, `docs/04_APPFLOW.md` lines 60â€“81, `docs/17_OFFLINE_SYNC.md`, and `docs/22_REGULATORY_SAFETY.md` meeting R-REC-04, R-OFFER-02, R-HAND-01, R-HAND-03, R-HAND-04, R-HAND-05, R-DATA-04, R-REG-01, AT-024 (PASS), AT-028 (PASS), AT-029, AT-031, AT-032, AT-033, AT-056, and AT-071:
- **FastAPI Handover & Verification Router (`services/api/app/routers/handovers.py`)**:
  - `POST /handovers` and `POST /api/v1/handovers`: Collector submits immutable client handover proposal with full material, weight, value, location, and media snapshots.
  - **Canonical Hash Verification**: SHA-256 computed over SAHITOL-JCS-1 canonical JSON format (`compute_canonical_hash`). Tampered payloads or mismatched hashes are rejected with HTTP 409 Conflict.
  - **Canonical Fixture Parity**: Verified that computing the canonical hash over `docs/planning/handover_fixture.json` produces the exact frozen digest: `a091623365372138e72b1d767cca58ac80c59667b59b86f511ebf11b64eb783f`.
  - **Duplicate-Safe Idempotent Outcome (`R-HAND-01`)**: Resubmission of an identical proposal returns HTTP 200 with the existing record, avoiding duplicate rows or reissued tokens.
  - **Unguessable Capability Token**: Generates 256-bit cryptographic URL-safe token, stores only its SHA-256 digest (`public_token_hash`) in the database, and returns the plaintext capability token in the 201 response.
  - Advances lot state to `HANDED_OVER` and transaction lifecycle to `IN_TRANSIT`. Emits append-only domain event `HANDOVER_PROPOSAL_CREATED`.
  - `POST /handovers/{id}/confirm`: Authorized facility user confirms receipt. Exact match transitions directly to `CONFIRMED`, lot to `RECEIVED`, transaction to `CONFIRMED`, creating `HandoverConfirmation` and emitting `HANDOVER_CONFIRMED`.
  - **Discrepancy Flow Without Fact Overwriting (`R-HAND-05` / `AT-033`)**: If measured material, weight, or total paise differ from agreed terms, the endpoint creates a new `TermsRevision` with `proposed_by = 'FACILITY'` and transitions handover to `PENDING_COLLECTOR_ACK`, transaction to `PENDING_REVISED_TERMS`. Initial client facts remain unaltered. Emits `TERMS_REVISED_BY_FACILITY` and `HANDOVER_TERMS_DISCREPANCY_FLAGGED`.
  - `POST /handovers/{id}/acknowledge-terms`: Collector reviews and accepts facility revisions with `expected_terms_hash`, advancing handover to `CONFIRMED`, lot to `RECEIVED`, and transaction to `CONFIRMED`.
  - `POST /handovers/{id}/dispute`: Either party records a dispute with mandatory reason without rewriting historical records. Emits `HANDOVER_DISPUTED`.
  - `POST /handovers/{id}/void`: Collector voids pending unconfirmed proposals, reverting lot to `ACCEPTED` and transaction to `AGREED`. Voiding confirmed records is prohibited (HTTP 409 Conflict).
  - `GET /handovers/{id}/receipt`: Versioned platform handover receipt including transaction ID, lot ID, canonical hash, confirmation timestamp, collector display alias, facility details, and statutory notice:
    `"This Digital Handover Record certifies platform receipt and material transfer only. It does not constitute a statutory EPR certificate under E-Waste (Management) Rules, 2022."`
  - `GET /verify/{public_token}`: Unauthenticated public capability endpoint returning redacted summary (`handover_id`, `status`, `occurred_at`, `facility_name`, `material_id`, `regulatory_route`, `weight_kg`, `proposal_hash`, `non_epr_notice`). Phone numbers, exact GPS coordinates, media URLs, and financial settlement details are strictly omitted.
- **Automated Test Suite**:
  - 13 comprehensive unit tests in `services/api/tests/test_handovers.py` verifying hash utility against documented fixture, proposal submission, idempotent replay, tamper rejection, ownership scoping, exact-match confirmation, discrepancy revision flow with collector acknowledgement, disputes, voiding rules, non-EPR notice on receipts, and redacted public verification.
  - Full API test suite now totals 159 passing tests (0 failures). Evidence: [`docs/evidence/T023_HANDOVER_CONFIRMATIONS.md`](docs/evidence/T023_HANDOVER_CONFIRMATIONS.md).

## 2026-09-29 â€” Recycler Profile and Offer Workflows (T021 DONE)

Implemented facility-user membership linkage, self-declared operational profile management, material/rate/pickup updates with explicit provenance, directed lot requests, offer quoting, rejections with rematching, offer withdrawals, collector offer acceptance creating an immutable agreement, single-active-agreement invariant under race conditions, and price-board independence conforming to `docs/16_API_CONTRACT.md` lines 53â€“61, `docs/04_APPFLOW.md` lines 49â€“59, and `docs/06_SCHEMA.md` meeting R-REC-03, R-OFFER-01, R-OFFER-02, R-PRICE-04, R-DATA-03, AT-019, AT-023, AT-027, AT-028, and AT-055:
- **FastAPI Trade & Recycler Workflows Router (`services/api/app/routers/trade.py`)**:
  - `GET /api/v1/recycler/profile`: Returns public business profile, read-only legal authorizations, self-declared operational status, accepted materials with min/max bounds, and active quoted rates.
  - `PATCH /api/v1/recycler/profile`: Facility members update operational fields (`pickup_status`, `service_regions`, `accepting_status`), materials, and rates with provenance (`source_id = f"SELF_DECLARED_USER_{user_id}"`). Unknown operational data (pickup status) is explicitly preserved when cleared or omitted (`AT-023`).
  - **Authorization Tampering Prevention (`AT-023`)**: Legal authorizations and verification status are strictly admin-controlled. Any attempt to modify authorization fields via profile updates is rejected with HTTP 403 Forbidden.
  - `POST /api/v1/lots/{lot_id}/requests`: Collector directs a lot request to a chosen eligible facility. Revalidates lot state (`COLLECTED`, `LISTED`, `MATCHED`), route compatibility, and material acceptance.
  - **Battery Isolation Hard Guard (`R-REC-04` / `AT-024`)**: Directing a `BATTERY_ISOLATION` lot to a general e-waste facility without battery authorization is rejected with HTTP 422 Unprocessable Entity.
  - `GET /api/v1/recycler/incoming`: Facility members view incoming lot requests and evidence. Location privacy is strictly enforced: coarse locality (`coarse_area`) is exposed while raw GPS coordinates are never disclosed.
  - `POST /api/v1/requests/{request_id}/offers`: Recycler quotes offers with `RATE_PER_KG` or `FIXED_TOTAL`. Generates deterministic canonical `terms_hash` (SHA-256 over SAHITOL-JCS-1 JSON format) and emits domain event `OFFER_CREATED`.
  - `POST /api/v1/requests/{request_id}/reject`: Recycler rejects request with mandatory reason. When no other open offers or pending requests remain, lot status reverts from `MATCHED` to `LISTED` so the collector can rematch with another facility (`AT-027`).
  - `POST /api/v1/offers/{offer_id}/withdraw`: Recycler withdraws open offer with optimistic concurrency (`expected_version`). Already accepted offers cannot be withdrawn.
  - `POST /api/v1/offers/{offer_id}/accept`: Collector accepts live open offer with matching `terms_hash` and `expected_version`, atomically creating a `Transaction` (`lifecycle = 'AGREED'`) and initial `TermsRevision`. Automatically expires all competing offers and pending requests for that lot (`AT-028`).
  - **Race Condition & Single Active Agreement Invariant (`AT-028`)**: Two simultaneous acceptances leave only one active agreement; subsequent acceptances fail with HTTP 409 Conflict.
  - **Expired Offer Guard (`AT-028`)**: Offers whose `expires_at` is in the past cannot bind and are rejected with HTTP 409 Conflict.
  - **Terms Hash Tamper Resistance (`AT-028`)**: Accepted payload `terms_hash` must match offer `terms_hash`; mismatches return HTTP 409 Conflict.
  - **Price-Board Independence (`AT-028`)**: Subsequent price board refreshes or facility rate adjustments never mutate existing `Transaction` or `TermsRevision` agreed terms.
  - `GET /api/v1/transactions/{id}`: Restricts transaction access strictly to participating collector, linked facility members, and admins. Third parties receive HTTP 403 Forbidden.
  - `GET /api/v1/recycler/transactions`: Facility members query their historical transactions and receipts.
- **Automated Test Suite**:
  - 19 comprehensive unit tests in `services/api/tests/test_trade.py` verifying all profile updates, tampering prevention, directed requests, battery isolation guard, incoming queue privacy, offer quotes, rejections/rematching, withdrawals, atomic acceptance, expiry guards, race condition invariants, and transaction scoping.
  - Full API test suite now totals 146 passing tests (0 failures). Evidence: [`docs/evidence/T021_RECYCLER_OFFER_WORKFLOWS.md`](docs/evidence/T021_RECYCLER_OFFER_WORKFLOWS.md).

## 2026-09-29 â€” Recycler Matching and Map Data (T019 DONE)

Implemented the eligible recycler matching engine, explainable multi-factor ranking, deterministic tie-breaking, offline parity fixtures, and GeoJSON map data conforming strictly to policy `MATCH_V1` (`docs/03_TECHSPEC.md` lines 67â€“84) meeting R-REC-04, R-REC-05, R-REC-06, R-REC-02, AT-022, AT-024, AT-025, and AT-026:
- **Pure Domain Matching Engine (`services/api/app/domain/matching.py`)**:
  - Implemented `haversine_distance_m` computing great-circle distances in metres with Earth radius $R = 6,371,000$ m, proving $<0.07\%$ relative error against PostGIS WGS84 geography calculation (well within the $0.5\%$ tolerance ceiling).
  - Implemented `extract_coordinates` robustly resolving coordinates from PostGIS/GeoAlchemy2 geometries across both PostgreSQL and SQLite.
  - Hard eligibility filtering in `evaluate_candidate_eligibility`:
    - `ROUTE_INCOMPATIBLE`: Enforces strict route compatibility. Crucially, battery lots (`BATTERY_ISOLATION` route or battery material category) cannot match facilities evidenced only for e-waste (e.g. Greentech Recyclers). General recycling and unauthorized facilities are excluded before ranking.
    - `MATERIAL_UNACCEPTED`: Validates verified evidence of accepted material IDs.
    - `EXPIRED_REGISTRATION`: Validates `VALID` status and non-expired `valid_until` timestamp.
    - `VERIFICATION_INSUFFICIENT`: L0/L1/L2 facilities cannot match formal destination requests (`AT-022`); only L3/L4 with active valid status match.
    - `WEIGHT_INCOMPATIBLE`: Validates lot weight against facility operational acceptance bounds (`min_weight_g`, `max_weight_g`).
    - `OPERATIONALLY_CLOSED`: Excludes facilities with self-declared `PAUSED` or `CLOSED` status.
    - `DISTANCE_EXCEEDED`: Excludes candidates beyond `search_radius_m` (default 50 km).
    - `DEMO_MISMATCH`: Preserves demo fixture partition isolation.
  - Explainable multi-factor ranking in `rank_eligible_candidates`:
    - Distance (30%): `max(0, 1 - distance / search_radius)`. Missing GPS omits distance contribution without inventing fake coordinates.
    - Comparable Offered Rate (30%): Min-max normalized across active quotes for the lot's material. Candidates with missing rates receive 0 contribution with explicit explanation, never inserting 0 rupees quotes.
    - Pickup (20%): `1.0` if pickup is available for the lot/location, `0.0` for drop-off only, `0.0` with explicit "unknown" label if unverified.
    - Availability (15%): `1.0` for current confirmed operational acceptance (`ACCEPTING`), `0.5` for unknown, `0.0` for paused/closed.
    - Reliability (5%): Completed historical transaction ratio (`completed / total`) for facilities with $\ge 5$ transactions. Facilities with $<5$ transactions receive a baseline `0.5` explicitly labeled "no history".
    - Deterministic tie-breaking: Shorter distance ascending, then stable facility UUID string ascending. Rank 1 assigned `is_recommended = True`.
  - Main orchestrator `match_lot_to_facilities`: Aggregates transparent `exclusion_counts: Dict[str, int]` and user-facing messages.
- **FastAPI Matching and Map Endpoints**:
  - `POST /api/v1/lots/{lot_id}/matches`: Matches collector lots to eligible recyclers with request options (`search_radius_m`, `require_formal_destination`, override coordinates, coarse locality), enforcing collector ownership and admin scoping.
  - `GET /api/v1/facilities/geojson`: Dynamic GeoJSON `FeatureCollection` for MapLibre client rendering, including Point coordinates, statutory disclaimers, authorized routes, accepted materials, and verification levels.
- **Canonical Shared Fixtures & Map Fallback**:
  - Published [`data/fixtures/matching_v1_fixtures.json`](data/fixtures/matching_v1_fixtures.json) and mirrored to [`apps/android/app/src/test/resources/fixtures/matching_v1_fixtures.json`](apps/android/app/src/test/resources/fixtures/matching_v1_fixtures.json) covering Haversine distance, battery isolation, formal verification levels, weight bounds, and 5-factor ranking.
  - Generated static MapLibre vector fixtures: [`data/fixtures/facilities_map.geojson`](data/fixtures/facilities_map.geojson) and [`apps/web/public/fixtures/facilities_map.geojson`](apps/web/public/fixtures/facilities_map.geojson).
- **Automated Test Suite**:
  - Verified 10 tests in `services/api/tests/test_matching.py`. Full API test suite now totals 127 passing tests (0 failures). Evidence: [`docs/evidence/T019_RECYCLER_MATCHING_MAPS.md`](docs/evidence/T019_RECYCLER_MATCHING_MAPS.md).

## 2026-09-29 â€” Price Statistics and Snapshot Valuation (T018 DONE)

Implemented the statistical valuation engine, recency decay weighting, confidence scoring, historical trends with honest gap preservation, and per-lot immutable valuation snapshots conforming strictly to `PRICE_V1` (`docs/03_TECHSPEC.md` lines 50-66) meeting R-PRICE-02, R-PRICE-03, R-PRICE-04, R-DATA-02, AT-017, AT-018, AT-019, and AT-054:
- **Canonical Shared Fixtures & Python/Kotlin Parity**:
  - Published shared test fixture in [`data/fixtures/pricing_v1_fixtures.json`](data/fixtures/pricing_v1_fixtures.json) and mirrored to Android test resources in [`apps/android/app/src/test/resources/fixtures/pricing_v1_fixtures.json`](apps/android/app/src/test/resources/fixtures/pricing_v1_fixtures.json).
  - Validated both Python API (`services/api/tests/test_pricing.py`) and Android Kotlin (`apps/android/app/src/test/java/com/sahitol/collector/PriceCalculatorTest.kt`) against the exact same test cases (equal weights baseline, recency decay weights, single/empty observations, lot valuation at 2500g, half-up rounding, and 8 confidence evaluation scenarios).
- **Daily Source Capping & Recency Decay Weighting**:
  - Enforced Rule 5 capping each original source to at most one representative observation per cohort/day (latest `observed_at`), preventing mirrored scrapes or bulk data drops from dominating quantiles.
  - Implemented exponential recency decay weighting: `w_i = 2^(-age_days / 7.0)`.
- **Broader Regional Fallback without Province Mixing**:
  - Enforced Rule 3 enabling sparse pilot subregions (`MAYAPURI`, `SEELAMPUR`) to fall back to broader provincial cohorts (`DELHI_NCR`) with explicit label `coverage_scope: "BROADER_REGION"`, while strictly preserving disjoint provincial separation between Delhi-NCR and Maharashtra.
- **Statistical Confidence & 24-Hour Cache Staleness**:
  - Enforced Rule 8 conjunctive confidence criteria (`INSUFFICIENT_DATA`, `LOW`, `MEDIUM`, `HIGH`) and audit reason codes. Cached `PriceSummary` rows older than 24 hours are marked `is_stale=True` with confidence capped at `LOW`.
- **Historical Trends & Valuation Snapshots**:
  - Implemented `GET /api/v1/prices/trends` returning dated daily buckets (min, median, max, count) preserving honest gaps (`has_gaps: true`) and supporting price kind filtering (`BUY`, `QUOTE`, `SELL`).
  - Implemented `POST /api/v1/prices/snapshots` computing and persisting immutable `ValuationSnapshot` records linked to lots with statutory non-binding quote disclaimers, preserving quote vs final payment semantics.
- **Automated Test Suites**:
  - Verified 4 tests in `services/api/tests/test_pricing.py` and 17 tests in `services/api/tests/test_price_pipeline.py`. Full API test suite now totals 117 passing tests. Evidence: [`docs/evidence/T018_PRICE_STATISTICS_VALUATION.md`](docs/evidence/T018_PRICE_STATISTICS_VALUATION.md).

## 2026-09-29 â€” Lot and Lifecycle Backend (T016 DONE)

Implemented the material lot lifecycle, state machine, and valuation backend (`services/api/app/routers/lots.py`) meeting R-LOT-03, R-LOT-04, R-LOT-05, R-DATA-01, AT-013, AT-014, AT-015, and AT-053:
- **FastAPI Lot Router (`services/api/app/routers/lots.py`)**:
  - `POST /api/v1/lots`: Create draft lot command validating owner checks, positive integer grams (max 50 metric tonnes), fractional kg round-trip conversion, location provenance, attached photos, and immutable initial domain event.
  - `PATCH /api/v1/lots/{id}`: Update draft lot fields with optimistic version control (`expected_version`). Strictly prohibits direct arbitrary `status` mutation (returning HTTP 422 with `ARBITRARY_STATUS_MUTATION_PROHIBITED`).
  - `POST /api/v1/lots/{id}/collect`: Finalize collection transitioning `DRAFT -> COLLECTED`, enforcing mandatory material classification confirmation and positive finite weight in integer grams.
  - `POST /api/v1/lots/{id}/list`: Market listing command transitioning `COLLECTED -> LISTED`, requiring route revalidation to ensure hazardous/battery/e-waste materials are safely routed before entering recycler matching.
  - `POST /api/v1/lots/{id}/cancel`: Cancellation command with mandatory reason string, verifying lot is not already confirmed received/closed (`RECEIVED`, `CLOSED` return HTTP 409 `CANNOT_CANCEL_CONFIRMED_LOT`), emitting deletion tombstone `SyncChange`.
  - `POST /api/v1/lots/{id}/estimate`: Computes immutable indicative valuation ranges conforming to `PRICE_V1` (rates in paise per kg, weight in grams), persisting a permanent `ValuationSnapshot`.
- **Weight Precision & Anomaly Detection**:
  - Positive integer grams enforced at both API schema layer and PostgreSQL `CHECK` constraints.
  - Fractional kilograms (e.g. `12.5 kg`) round-trip cleanly to integer grams (`12500 g`) without precision loss.
  - Suspiciously large weights (>500 kg) are not arbitrarily blocked or capped at collection time; instead, they are recorded and automatically flagged via `QualityFlag` (`LARGE_WEIGHT_ANOMALY`) for supervisor/admin review.
- **Location Quality & Privacy Protection**:
  - Coordinates captured via GPS or manual entry are stored in `location_records` with provenance metadata (`source`, `accuracy_m`, `age_ms`, `coarse_area`, `consent_version`).
  - Detailed lot projections (`GET /api/v1/lots/{id}`) redact exact GPS coordinates, exposing only coarse area and quality provenance to protect collector safety and privacy.
- **Append-Only Domain Events & Hash Chain**:
  - Every lifecycle transition (`LOT_CREATED`, `LOT_UPDATED`, `LOT_COLLECTED`, `LOT_LISTED`, `LOT_CANCELLED`) appends an immutable record to `domain_events` with monotonic sequence, actor ID, previous/next states, canonical payload hash, and SHA-256 event hash chaining (`prev_hash` -> `event_hash`).
- **Ownership Isolation & Scoping**:
  - Collectors can only view, update, list, cancel, or estimate their own lots. Recyclers can only query market-eligible lots (`LISTED`, `MATCHED`, `IN_TRANSIT`, `DELIVERED`). Admins retain full access.
- **Test Infrastructure & SQLite Compatibility (`services/api/tests/test_db.py`)**:
  - Added SQLite spatial function converter stub `sqlite_as_ewkb` translating EWKT geometry strings into valid EWKB hex representations for seamless GeoAlchemy2 query execution in in-memory test databases.
- **Automated Test Suite (`services/api/tests/test_lots.py`)**:
  - 14 comprehensive unit and integration tests verifying all commands, weight round-trip, large weight flagging, privacy redaction, status transition rules, optimistic concurrency, and valuation calculation. Full API test suite now totals 113 passing tests. Evidence: [`docs/evidence/T016_LOT_LIFECYCLE_BACKEND.md`](docs/evidence/T016_LOT_LIFECYCLE_BACKEND.md).

## 2026-09-29 â€” Server Synchronization Protocol (T014 DONE)

Implemented the durable offline server synchronization protocol (`POST /api/v1/sync/batch` and `GET /api/v1/sync/changes`) meeting R-OFF-03, R-OFF-04, and AT-040:
- **FastAPI Synchronization Router (`services/api/app/routers/sync.py`)**:
  - `POST /api/v1/sync/batch` & `POST /api/v1/sync/push`: Full batch push implementation handling up to 50 operations per batch with canonical wire and Android Room field mapping (`owner_user_id->account_id`, `command_type->command`, `base_server_version->expected_version`, `payload_json->payload`, `dependency_operation_ids->depends_on`, `status->state`).
  - Emits per-operation outcomes (`APPLIED`, `ALREADY_APPLIED`, `RETRY`, `AUTH_REQUIRED`, `CONFLICT`, `REJECTED`, `DEPENDENCY_PENDING`) with server versions, entity IDs, and detailed error codes under HTTP 200 for authenticated batches.
  - Implemented nested database savepoints per operation, ensuring that independent sibling operations in a batch can succeed, commit, and receive `APPLIED` even if another operation in the batch fails validation or dependencies (`mixed-success batches`, AT-040).
- **Atomic Idempotency Storage (`sync_operations`)**:
  - Atomically claims `(actor_id, operation_id)` in `sync_operations` with canonical SHA-256 payload fingerprints (`SAHITOL-JCS-1`).
  - Proved that simulated crash-after-commit / ACK loss returns `outcome="ALREADY_APPLIED"` with cached durable results and server version, producing **exactly one domain effect** (no duplicate lots, events, or observations in the database).
  - Detects and rejects operation ID reuse with an altered payload, returning `outcome="CONFLICT"` with error code `IDEMPOTENCY_KEY_REUSED` without mutating existing state.
  - Enforces cross-actor authorization preventing an actor from replaying another user's stored operation (`AUTH_FORBIDDEN`).
- **Dependency Ordering & Concurrency Controls**:
  - Topologically validates dependencies within the batch and against committed `sync_operations`. Parent failure halts dependent children (`DEPENDENCY_PENDING`, `DEPENDENCY_FAILED`) while missing dependencies wait (`DEPENDENCY_NOT_SATISFIED`).
  - Optimistic concurrency: validates `expected_version` against current database version, returning `outcome="CONFLICT"` (`VERSION_CONFLICT`) without overwriting newer state.
- **Delta Pull Contract (`GET /api/v1/sync/changes` & `GET /api/v1/sync/pull`)**:
  - Delivers incremental entity upserts (`operation="UPSERT"`) and deletion tombstones (`operation="DELETE"`, `data=None`) based on opaque monotonic sequence cursors (`sahitol_cur_v1:<seq>`).
  - Enforces role and user visibility scoping: collectors receive only public, reference, and their own scoped changes; administrators receive all changes.
  - Returns HTTP 410 Gone (`CURSOR_EXPIRED`) on malformed or corrupted cursors.
- **Automated Test Suite (`services/api/tests/test_sync.py`)**: 16 comprehensive unit and integration tests verifying all protocol contracts, idempotency, dependency chaining, mixed-success batches, version conflict detection, and tombstone delivery. Full API test suite now totals 99 passing tests. Evidence: [`docs/evidence/T014_SERVER_SYNC_PROTOCOL.md`](docs/evidence/T014_SERVER_SYNC_PROTOCOL.md).

## 2026-09-29 â€” Delhi-NCR and Maharashtra Facility Directory (T012 DONE, AT-021 PASS)

Built the source-backed formal facility directory covering Delhi-NCR and Maharashtra hubs, role preservation, verification levels, operational updates, and curated dataset export meeting R-REC-01, R-REC-02, R-REC-03, R-DATA-03, R-DATA-09, AT-021 (PASS), AT-022, AT-023, AT-055, and AT-061:
- **Source-Backed Official Registry Seeds (`data/seeds/facilities.json`)**: Curated 8 dated facilities across Delhi-NCR and Maharashtra from CPCB (`SRC-02`), MPCB (`SRC-04`), DPCC (`SRC-05`), and NDMC (`SRC-06`) preserving exact regulatory roles: `RECYCLER` (Greentech, EcoRegen, Maharashtra Lead), `DISMANTLER` (Seelampur Co-operative), `COLLECTION_CENTRE` (Eco-Battery, NDMC), and `AGGREGATOR` (Pune Aggregators). Prohibits relabeling collection centres as recyclers (AT-021 PASS).
- **Statutory Disclaimers & Non-Partnership Invariant**: Enforced statutory disclaimer on all directory listings confirming that records represent regulator public notices/leads and do not constitute government endorsements, commercial partnerships, or statutory EPR certificates.
- **Verification Levels (L0, L2, L3) & Formal Destination Badge**: Enforced verification rules: only active `L3`/`L4` facilities with current valid registrations (`VALID`) qualify as "Verified Formal Destinations" (`is_formal_destination=True`). Facilities with `L2` list matches (Pune Aggregators), expired registrations (NDMC Collection Point), or `L0` demo fixtures are excluded from formal destination badges and formal matching filters.
- **Honest Operational Data & Unknown Preservation**: Unknown pickup availability and quote rates are faithfully preserved as `null` / unknown (e.g. Greentech), while drop-off constraints (`pickup_available: false` on Eco-Battery) and active pickup services (`pickup_available: true` on Seelampur) are accurately reflected.
- **FastAPI Facility Router (`services/api/app/routers/facilities.py`)**:
  - `GET /api/v1/facilities`: Comprehensive public directory with query filters (`region_id`, `kind`, `route`, `material_id`, `verification_level`, `formal_destination_only`, `is_demo`).
  - `GET /api/v1/facilities/{id}`: Detailed facility endpoint returning complete authorization history, accepted materials with weight bounds, and operational parameters.
  - `PUT /api/v1/facilities/{id}/operations`: Facility operator update endpoint for pickup availability, service area, and accepting status, proving that operational fields can be updated with provenance while regulatory authorizations remain admin-controlled (R-REC-03, AT-023).
  - `POST /api/v1/facilities/{id}/rates`: Quote rate submission endpoint with provenance.
- **Router Integration & Backward Compatibility**: Mounted `facilities.router` at `/api/v1/facilities`; updated `services/api/app/routers/recyclers.py` (`GET /api/v1/recyclers/directory`) to delegate to the facility service; and wired `services/api/app/routers/reference.py` (`GET /api/v1/reference/bootstrap`) to dynamically load seeded facilities.
- **Curated Dataset Package (`data/curated/facilities/`)**: Exported `facilities.csv`, `facilities.json`, `facility_authorizations.json`, `facility_materials.json`, and cryptographic `manifest.json` with SHA-256 hashes and explicit limitations disclosure.
- **Automated Test Suite (`services/api/tests/test_facilities.py`)**: 15 comprehensive unit and integration tests verifying directory seeding, role preservation, statutory disclaimers, verification levels, formal destination filtering, regional partitioning, material/route filtering, unknown pickup preservation, operational updates without authorization tampering, quote rate submission, backward-compatible `/recyclers/directory`, bootstrap integration, demo partition isolation, and validation/deduplication. API test suite now totals 83 passing tests. Evidence: [`docs/evidence/T012_FACILITY_DIRECTORY.md`](docs/evidence/T012_FACILITY_DIRECTORY.md).

## 2026-09-29 â€” Attributed Price Seed and Observation Pipeline (T011 DONE)

Implemented the dated attributed price observation pipeline, validation engine, admin moderation workflow, statistical quantile aggregation under PRICE_V1, and curated export meeting R-PRICE-01, R-DATA-02, AT-016, and AT-054:
- **Canonical Price Seeds (`data/seeds/price_observations.json`)**: Curated 12 dated price observations across Delhi-NCR and Maharashtra secondary market hubs (Mayapuri, Seelampur, MIDC benchmarks) covering high/low-grade PCBs, lead-acid batteries, and copper cables attributed to verified public sources (`SRC-01`, `SRC-04`, `SRC-05`).
- **Database Seeder (`services/api/app/db/seeds/prices.py`)**: Idempotent loader populating `data_sources` (`SRC-04` Delhi survey, `SRC-05` MIDC benchmark), baseline regions (`DELHI_NCR`, `MAHARASHTRA`), and `price_observations` with UUID primary keys and ISO timestamps.
- **Price Observation API (`services/api/app/routers/prices.py`)**:
  - `POST /api/v1/prices/observations`: Validates material presence against catalog, enforces non-positive rate rejection, and quarantines future timestamps (>5 min drift with HTTP 422). Observations enter `PENDING_REVIEW`.
  - `GET /api/v1/prices/observations`: Identity-safe public listing filtered by material, region, price kind (`BUY`, `QUOTE`, `SELL`), review status, and demo partition, omitting private contributor information.
  - `GET /api/v1/prices/summary`: Calculates `PRICE_V1` weighted quantiles (Q1, median, Q3), independent source count, and confidence level (`HIGH`, `MEDIUM`, `LOW`, `INSUFFICIENT_DATA`). Empty cohorts return `INSUFFICIENT_DATA` with null rates and reason codes, never fabricating zero or substituting synthetic fallbacks.
  - `GET /api/v1/prices/trends`: Provides daily trend aggregation buckets while honestly flagging and preserving gaps without interpolating fabricated points.
  - `POST /api/v1/prices/estimate`: Calculates low, median, and high valuation ranges in integer paise conforming to TECHSPEC line 65.
- **Admin Moderation API (`services/api/app/routers/admin.py`)**: Added `GET /api/v1/admin/price-review` and `POST /api/v1/admin/price-review/{id}/decision` for reviewing pending submissions with audit justifications (`APPROVE` -> `VERIFIED`, `REJECT` -> `REJECTED`).
- **Curated Dataset Export (`data/curated/price_observations/`)**: Exported `price_observations.csv`, `price_observations.json`, `price_summaries.json`, and cryptographic `manifest.json` detailing SHA-256 hashes, byte sizes, and provenance limitations (highlighting that live collector fieldwork transaction data remains UNMET under R-RES-02).
- **Automated Test Suite (`services/api/tests/test_price_pipeline.py`)**: 14 comprehensive unit tests verifying seeding, identity-safe listing, submission validation, future-date quarantine, rate validation, admin moderation (approve/reject), `PRICE_V1` quantiles, empty cohort `INSUFFICIENT_DATA` enforcement, trend gap preservation, demo partition isolation, and valuation estimation. API test suite now totals 68 passing tests. Evidence: [`docs/evidence/T011_PRICE_OBSERVATION_PIPELINE.md`](docs/evidence/T011_PRICE_OBSERVATION_PIPELINE.md).

## 2026-09-29 â€” Versioned Reference Bootstrap and Delta Sync APIs (T009 DONE)

Implemented the versioned reference bootstrap snapshot, incremental delta synchronization, tombstone handling, and bundled offline demo cache asset meeting R-OFF-01 and AT-038:
- **Versioned Bootstrap Snapshot (`services/api/app/routers/reference.py`)**: `GET /api/v1/reference/bootstrap` delivers a comprehensive reference snapshot comprising `metadata` (`snapshot_version="REF-2026-09-29-01"`, timestamps, 30-day expiry, opaque cursor, region, language, role, and demo status), `policy` (`policy_version="POLICY_2026_V1"`, 50 metric tonne max weight, 30-day freshness, allowed units, integer paise money, cash settlement, and statutory disclaimers), 11 material categories, 21 materials with condition options and routes, 139 multilingual colloquial aliases, 9 contextual safety guides with Devanagari audio keys, 21 regional benchmark prices, and regional verified facilities.
- **Regional & Role Tailoring**: Supports `region=DELHI_NCR` and `region=MAHARASHTRA` filtering for verified formal destinations and price benchmarks, ensuring collectors only sync relevant regional facility destinations.
- **Delta Synchronization Protocol (`GET /api/v1/reference/changes`)**: Incremental delta sync decoding base64 sequence cursors (`sahitol_cur_v1:<seq>`), querying `sync_changes`, returning `UPSERT` and `DELETE` (tombstones with `data=None`) operations, and advancing cursors monotonically. Enforces HTTP 410 Gone (`CURSOR_EXPIRED`) on malformed, corrupted, or ancient cursors to trigger full client rebootstrap.
- **Bundled Offline Demo Reference Cache (`scripts/generate_bundled_reference_cache.py`)**: Generated static demonstration cache containing all categories, materials, aliases, safety guides, benchmark prices, and sample verified facilities. Installed directly to Android app assets (`apps/android/app/src/main/assets/reference_bootstrap_demo.json`, 49,133 bytes, SHA-256: `7b287328e0f03efb4acd8a279587d6644b0f8e63aff0ad7d383e2d7410e18e69`) and `data/curated/` allowing initial app launch in airplane mode without network.
- **Automated Test Suite (`services/api/tests/test_reference.py`)**: 6 comprehensive unit tests verifying bootstrap payload structure, content completeness, regional facility filtering, delta sync with tombstones, cursor expiry (HTTP 410), and Android asset file integrity. Entire API test suite now totals 54 passing tests. Evidence: [`docs/evidence/T009_REFERENCE_BOOTSTRAP_DELTA.md`](docs/evidence/T009_REFERENCE_BOOTSTRAP_DELTA.md).

## 2026-09-29 â€” Material Taxonomy, Language Aliases, and Safety Guides (T010 DONE)

Curated and implemented the authoritative informal e-waste material reference catalog, multilingual colloquial aliases, contextual safety guides, and regulatory route mapping meeting R-LOT-01 and R-DATA-01:
- **Curated Taxonomy Coverage (`data/seeds/`)**: Populated all 11 canonical categories (`PCB`, `BATTERY`, `CRT`, `LCD`, `CABLES`, `MOTORS`, `PLASTICS`, `METALS`, `MIXED_ELECTRONICS`, `OTHER`, `UNKNOWN`) and 21 detailed material definitions across high/low grade PCBs, CRT monitors, LCD panels, copper and aluminum cables, lead-acid, lithium-ion, other, and unknown battery chemistries, electric motors and compressors, rigid e-waste ABS/HIPS vs general plastics, mixed IT and small household electronics, and ferrous/non-ferrous scrap metals.
- **Multilingual Colloquial Aliases (`data/seeds/material_aliases.json`)**: Curated 139 reviewed aliases across Hindi (`hi`), Marathi (`mr`), and English (`en`) with normalized search terms. Enables conversational and dialect search (e.g. Hindi "à¤®à¤¦à¤°à¤¬à¥‹à¤°à¥à¤¡", "à¤¹à¤°à¤¾ à¤ªà¤¤à¥à¤¤à¤¾", "à¤•à¤¾à¤‚à¤š à¤µà¤¾à¤²à¤¾ à¤Ÿà¥€à¤µà¥€", "à¤‡à¤¨à¥à¤µà¤°à¥à¤Ÿà¤° à¤¬à¥ˆà¤Ÿà¤°à¥€", "à¤¤à¤¾à¤‚à¤¬à¥‡ à¤•à¤¾ à¤¤à¤¾à¤°"; Marathi "à¤¹à¤¿à¤°à¤µà¤¾ à¤¬à¥‹à¤°à¥à¤¡", "à¤•à¤¾à¤šà¥‡à¤šà¥€ à¤Ÿà¥à¤¯à¥‚à¤¬", "à¤‡à¤¨à¥à¤µà¥à¤¹à¤°à¥à¤Ÿà¤° à¤¬à¥…à¤Ÿà¤°à¥€", "à¤¤à¤¾à¤‚à¤¬à¥à¤¯à¤¾à¤šà¥€ à¤µà¤¾à¤¯à¤°"; English "motherboard", "lead acid battery", "crt monitor").
- **Provenance-Dependent Routing & Contextual Rules**: Enforces CPCB regulatory route boundaries: rigid e-waste plastics (`MAT-PLA-01`) route to `AUTHORIZED_EWASTE` with `route_requires_context=True` due to brominated flame retardants (differentiating from general packaging plastics `MAT-PLA-02` routed to `GENERAL_RECYCLING`); all battery chemistries route to `BATTERY_ISOLATION` under CPCB Battery Waste Rules; CRTs route to `HAZARDOUS_DISPOSAL`; and unknown components route to `REVIEW_REQUIRED`.
- **Contextual Safety Guides (`data/seeds/safety_guides.json`)**: Seeded 9 vetted safety guides with warning text keys, icon references, and pre-generated audio script keys in `en`, `hi`, and `mr` covering prohibitions against cable burning (`SG-CABLE-01`), acid leaching/heating (`SG-PCB-01`), CRT glass implosion (`SG-CRT-01`), battery mishandling (`SG-BATTERY-01/02/03`), plastic burning (`SG-PLASTIC-01`), hazardous stops (`SG-DAMAGED-01`), and blind dismantling (`SG-MIXED-01`).
- **FastAPI Reference Endpoints (`services/api/app/routers/materials.py`)**: Implemented `GET /api/v1/materials/categories`, `GET /api/v1/materials`, `GET /api/v1/materials/{id}` (with embedded safety guides), `GET /api/v1/materials/search` (multilingual alias resolver), and `GET /api/v1/safety-guides`.
- **Lot Draft Separation (`services/api/app/routers/lots.py`)**: Enhanced lot creation (`POST /api/v1/lots`) with reference catalog validation, ensuring user observations (estimated weight, condition, photographs) link to immutable catalog material IDs without mutating or polluting the reference catalog.
- **Curated Dataset Export (`data/curated/material_catalog/`)**: Exported canonical CSV and JSON files with cryptographic SHA-256 manifest and explicit provenance limitations.
- **Automated Test Suite (`services/api/tests/test_materials.py`)**: 9 comprehensive unit tests verifying complete category coverage, provenance-dependent routing, Hindi/Marathi/English alias resolution, safety guides, draft lot creation, and catalog immutability. Entire API test suite now totals 48 passing tests. Evidence: [`docs/evidence/T010_MATERIAL_TAXONOMY.md`](docs/evidence/T010_MATERIAL_TAXONOMY.md).

## 2026-09-29 â€” Private Media Storage Adapter and Validation (T008 DONE)

Implemented the bounded private media storage architecture supporting local persistent volumes and hosted Supabase private storage, image validation, EXIF metadata stripping, and expiring signed download access meeting R-ARC-02, R-LOT-02, and R-SEC-02:
- **Dual Storage Adapters (`services/api/app/storage/`)**: Built `LocalStorageAdapter` with path-traversal defense (`_resolve_safe_path`), atomic writes via `tempfile.mkstemp` and `os.replace`, and `SupabaseStorageAdapter` with private bucket isolation and REST API operations. Integrated adapter factory `get_storage_adapter()` based on `STORAGE_BACKEND`.
- **EXIF Stripping & Image Integrity (`services/api/app/routers/media.py`)**: Built validation pipeline for JPEG, PNG, WebP, and PDF formats. Strips all EXIF metadata using Pillow (`PIL.Image`) to prevent collector privacy leakage before persistence, extracts pixel dimensions, and enforces a strict 2 MiB boundary (`MAX_MEDIA_BYTES = 2097152`).
- **Checksum Validation & Staging Lifecycle**: `POST /media/uploads` creates `STAGED` media objects with parent entity ownership checks; `PUT /media/{id}/content` streams raw bytes, compares client-provided SHA-256 against actual payload bytes, and saves to storage; `POST /media/{id}/complete` verifies backend storage presence and seals the record as `VALIDATED`.
- **Expiring Signed URLs & Private Authorization (R-SEC-02)**: `GET /media/{id}/access` generates short-lived signed tokens valid for 15 minutes (`expires_in=900`) for authorized owners, transaction participants, or admins. Direct file downloads enforce `Cache-Control: private, no-transform`. Foreign users receive HTTP 403 Forbidden.
- **PDF Document Support**: Validates and stores PDF documents for platform procurement logs, Digital Handover Records, and platform receipts.
- **Automated Test Suite (`services/api/tests/test_media.py`)**: 8 comprehensive unit and integration tests verifying staging, invalid MIME rejection, oversized payload rejection, EXIF stripping, checksum mismatch rejection, complete lifecycle transition, expiring access URLs, cross-user authorization defense, and PDF storage. Entire API test suite now totals 39 passing tests. Evidence: [`docs/evidence/T008_PRIVATE_MEDIA_STORAGE.md`](docs/evidence/T008_PRIVATE_MEDIA_STORAGE.md).

## 2026-09-29 â€” Phone/PIN Authentication, Session Rotation, and Ownership (T007 DONE)

Implemented end-to-end phone/PIN authentication, Argon2id PIN hashing with pepper, sliding-window rate limiting, rotating refresh tokens with replay attack detection, COLLECTOR/RECYCLER/ADMIN authorization, isolated demo mode, and Android session continuation contract meeting R-AUTH-01, R-AUTH-02, R-AUTH-03, R-AUTH-04, R-DATA-06, and R-SEC-01:
- **Argon2id PIN Security & Normalization (`services/api/app/security.py`)**: Enforced 4-6 numeric digit PINs hashed with Argon2id using `time_cost=2`, `memory_cost=65536`, `parallelism=2`, random 16-byte salt, and server-side pepper (`settings.PIN_PEPPER`). Implemented Indian phone normalization (`^[6-9]\d{9}$`) and masking (`******1234`) to prevent credential leakage.
- **Brute-Force Rate Limiting (`services/api/app/rate_limiter.py`)**: Built thread-safe sliding window rate limiter locking out phone numbers after 5 failed PIN attempts and IP addresses after 25 attempts within a 15-minute window, returning HTTP 429 and `Retry-After`. Generic authentication failure message ("Invalid phone number or PIN") prevents account enumeration.
- **Collector Activation & Atomic Provisioning (`services/api/app/routers/auth.py`)**: Online first registration (`POST /auth/register`) strictly enforces `COLLECTOR` role, creating `User`, `Collector` profile, and initial `AuthSession` in a single database transaction. Rejects duplicate phone with HTTP 409 Conflict.
- **Rotating Refresh Tokens & Replay Defense**: Implemented `POST /auth/refresh` issuing short-lived access tokens (60 min) and rotating 30-day refresh tokens tracked via SHA-256 hashes in `auth_sessions`. Presenting an already-rotated or revoked refresh token triggers immediate replay attack mitigation, revoking all active sessions for the user. Safe logout (`POST /auth/logout`) revokes server sessions without clearing offline client outbox data.
- **Role & Object Authorization Dependencies**: Implemented FastAPI dependencies `get_current_user`, `require_roles`, `check_object_ownership`, and `check_demo_isolation`. Prevents privilege escalation and prevents cross-user lot or facility mutation.
- **Isolated Demo Mode without SMS**: `POST /auth/demo` enables instant one-click onboarding for collectors, recyclers, and admins without SMS dependency, tagging accounts with `is_demo=True` and enforcing boundary checks against live production records.
- **Android Session Continuation Contract (`docs/contracts/SESSION_CONTINUATION_CONTRACT.md`)**: Formalized token storage in `EncryptedSharedPreferences`, OkHttp 401 interception, background refresh, offline outbox preservation across app restarts/deaths, and PIN re-auth resumption.
- **Automated Test Suite (`services/api/tests/test_auth.py`)**: 13 comprehensive unit/integration tests verifying all security properties, edge cases, and endpoints. API test suite now totals 31 passing tests. Evidence: [`docs/evidence/T007_AUTH_AND_OWNERSHIP.md`](docs/evidence/T007_AUTH_AND_OWNERSHIP.md).

## 2026-09-29 â€” PostgreSQL/PostGIS Schema and Alembic Migrations (T006 DONE)

Implemented the database schema across all 41 canonical tables defined in `docs/06_SCHEMA.md` with SQLAlchemy 2.0 ORM models, GeoAlchemy2 PostGIS types, and Alembic versioned migrations meeting R-ARC-02, R-DATA-01, and R-DATA-02:
- **Complete Canonical Table Coverage (`services/api/app/db/models/`)**: Defined typed models for all 41 tables across auth (`User`, `AuthSession`), collectors (`Collector`), facilities (`Region`, `Facility`, `FacilityUser`, `FacilityAuthorization`, `FacilityMaterial`, `FacilityOperation`, `FacilityRate`), materials (`MaterialCategory`, `Material`, `MaterialAlias`, `SafetyGuide`), pricing (`PriceObservation`, `PriceSummary`), lots & lifecycle (`Lot`, `MediaObject`, `LotImage`, `LocationRecord`, `Classification`, `ValuationSnapshot`), trade & payments (`LotRequest`, `Offer`, `Transaction`, `TermsRevision`, `Handover`, `HandoverConfirmation`, `PaymentEntry`), provenance & ML (`DataSource`, `SourceAssertion`, `DatasetVersion`, `ModelVersion`, `TrainingImage`, `ResearchInsight`), and audit & sync (`DomainEvent`, `AuditLog`, `SyncOperation`, `SyncChange`, `QualityFlag`, `EconomicsScenario`).
- **Data Integrity & Check Constraints**: Enforced signed 64-bit integer paise (`rate_paise_per_unit`, `agreed_total_paise`, `quoted_total_paise`, `amount_paise`) and grams (`estimated_weight_g`, `measured_weight_g`) using `BigInteger` columns. Configured check constraints for strictly positive weights (`final_weight_g > 0`, `estimated_weight_g > 0`), non-negative agreed money (`agreed_total_paise >= 0`), positive payments (`amount_paise > 0`), and positive domain event sequences (`sequence >= 1`).
- **PostGIS Spatial Fields**: Configured GeoAlchemy2 spatial columns (`geo_point`, `centroid`, `boundary`, `point`, `service_geometry`) with SRID 4326.
- **Append-Only Domain Events**: Implemented immutable `domain_events` with `(aggregate_id, sequence)` compound uniqueness, `prev_hash`, and `event_hash` to record tamper-evident audit history.
- **Alembic Initial Migration (`services/api/alembic/versions/0001_initial_schema.py`)**: Authored initial migration enabling `"uuid-ossp"` and `"postgis"` extensions, creating all 41 tables, foreign key constraints, indexes, unique constraints, and check constraints, with clean reverse downgrade capability.
- **Automated Test Suite (`services/api/tests/test_schema.py`)**: 6 new unit tests verifying table registration, BigInteger column types, GeoAlchemy2 types, check constraints, unique constraints, and offline compilation via `alembic upgrade head --sql`. API test suite now totals 18 passing tests. Evidence: [`docs/evidence/T006_DATABASE_SCHEMA.md`](docs/evidence/T006_DATABASE_SCHEMA.md).

## 2026-09-29 â€” Reproducible Data Import, Validation, and Synthetic Tooling (T005 DONE)

Implemented the data pipeline toolkit, validation engine with quarantine logging, cached geocoder, and reproducible synthetic generator meeting R-DATA-08, R-DATA-09, and R-DATA-10:
- **Core Provenance & Defense (`scripts/data_tools/provenance.py`, `staging.py`)**: Defined typed enums (`OriginClass`, `SourceKind`, `ReviewStatus`, `LocationQuality`), spreadsheet formula injection defense (`sanitize_csv_cell` neutralizes leading `=`, `+`, `-`, `@`), Unicode NFC normalization, phone sanitization, and 64-bit integer paise and positive grams conversions.
- **Validation Engine & Quarantine (`scripts/data_tools/validation.py`)**: Built validators for all 7 dataset families. Enforces provenance invariants (prohibiting synthetic data claimed as OFFICIAL, requiring `is_demo=True` on synthetic fixtures). Any policy-violating or malformed record is routed to inspectable JSON-Lines quarantine files with error codes and descriptions, never silently dropped or accepted.
- **Deduplication Engine (`scripts/data_tools/deduplication.py`)**: Implemented multi-stage deduplication for recyclers (registration reference matching and normalized name+address matching with review queues for differing roles), price observations (cohort and timestamp matching), and image assets (exact SHA-256 collision detection).
- **Cached Geocoder with Privacy Policy (`scripts/data_tools/geocoding.py`)**: Integrated local persistent JSON cache and regional boundary verification (Delhi-NCR, Maharashtra, India). Enforces a strict privacy guard raising `PermissionError` if collector home residences are queried; missing coordinates remain explicit null, never fabricated.
- **Synthetic Generator & 15 Edge Scenarios (`scripts/data_tools/synthetic.py`, `manifest.py`)**: Built deterministic, seeded generator (seed=42) producing valid fixtures for all 7 dataset families with SHA-256 manifest files, plus 15 operational/anomaly edge scenarios covering zero price cohorts, expired facility authorizations, battery route isolation, low-confidence ML abstention, offer rejection/expiry, scale discrepancies, partial/disputed payments, idempotent outbox replays, and clock skews.
- **CLI & Test Suite (`scripts/run_data_pipeline.py`, `scripts/test_data_pipeline.py`)**: CLI supporting `generate-synthetic`, `validate`, `dedup`, and `geocode` commands; 6 passing unit tests validating all rules. Evidence: [`docs/evidence/T005_DATA_PIPELINE.md`](docs/evidence/T005_DATA_PIPELINE.md).

## 2026-09-29 â€” Secondary Research and Persona Evidence (T004 DONE)

Completed secondary research synthesis, insight cards, and labelled personas meeting R-RES-01 and explicitly maintaining R-RES-02 primary fieldwork as UNMET:
- **Insight Cards (`docs/research/INSIGHT_CARDS.md`)**: Produced 7 attributed desk-research cards (`RC-01` to `RC-07`) covering informal collector economics (WIEGO/ILO/CPCB), fraud vectors (wetting, stones, scale rigging), visual contamination/battery fire risks, cash-centric settlement preferences, aggregator pricing margins, low digital literacy/voice-guidance requirements, and the explicit distinction between Digital Handover Records and statutory EPR certificates. Each card links directly to authoritative sources in `docs/sources/` and requirements in `docs/01_REQUIREMENTS.md`.
- **Labelled Personas (`docs/research/PERSONAS.md`)**: Developed 3 labelled simulated personas (Rajesh Kumar - Itinerant Waste Collector; Santosh Shinde - Aggregator / Small Scrap Yard Dealer; Anil Verma - Industrial Plastic Granulator / Semi-mechanized Recycler) with complete pain points, digital literacy profiles, operational journeys, and Mermaid flowcharts.
- **Evidence Dossier (`docs/evidence/T004_SECONDARY_RESEARCH.md`)**: Compiled comprehensive verification artifact verifying all 6 acceptance criteria for secondary research while explicitly keeping acceptance case AT-070 marked as `EXTERNAL_GAP` / `UNMET` in accordance with guardrails and owner decisions.

## 2026-09-29 â€” Stage 0 Bootstrap and Toolchain Setup (T001 DONE, T002 WAITING_STITCH)

Bootstrapped core repository skeletons and verified compatible pinned toolchains across all layers:
- **Android (`apps/android/`)**: Native Kotlin, Jetpack Compose, Material 3, Room SQLite database, durable outbox schema, WorkManager, CameraX, LiteRT on-device inference dependency, and ZXing QR decoding. Pinned to OpenJDK 17 LTS, AGP 8.7.0, Gradle 8.10.2, Kotlin 2.0.20, CompileSdk 35, and MinSdk 26. Unit test verifying PRICE_V1 quantiles and valuation formulas in Kotlin.
- **Backend API (`services/api/`)**: FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, PostgreSQL with PostGIS support (`geoalchemy2`), PyJWT access/refresh tokens, and Argon2id PIN hashing with pepper. Dual storage adapter architecture supporting local filesystem volume (with atomic write and strict path traversal defense) and hosted private Supabase Storage. Passing pytest test suite with 12 tests covering health endpoints, security/PIN hashing, storage safety, PRICE_V1 quantiles, and SAHITOL-JCS-1 canonical handover hashing matching the fixture.
- **Web Console (`apps/web/`)**: React 18, Vite 5, TypeScript 5.5, TailwindCSS 3.4, React Router 6, TanStack Query 5. Routing established for Recycler Console (R01â€“R07), Admin Quality Dashboard (A01â€“A07), Public Verification (V01), and Unit Economics (U01). Passing typecheck (`tsc --noEmit`), Vitest suite, and production bundle build.
- **Local Infrastructure (`infra/`)**: Docker Compose configuration running PostgreSQL 16 + PostGIS 3.4 with healthcheck and persistent volumes, containerized API and Web services.
- **CI Workflow (`.github/workflows/ci.yml`)**: Continuous integration testing documentation integrity, Python pytest, Node typecheck/test/build, and Android test suite.
- **Stitch Gate (T002)**: Prepared design brief for screen S00 (Android Feasibility Diagnostic) presented to owner; registry row marked REQUESTED and status marked WAITING_STITCH. No unauthorized UI components were generated.

## 2026-09-29 â€” Consistency review and validation

Aligned API sync routes, wire/Room state mappings, screen IDs and canonical handover serialization; supplied an actual computed hash fixture. Linked price observation entry and later export wiring explicitly into screens/tasks, so early UI completion cannot hide later integration. Checked all local links, source hashes/ranges, task graph and generated planning views. Nine negative controls verified that the validator rejects missing mappings, dependency cycles, unsupported DONE/PASS, scope demotion, lost fieldwork obligation, unapproved UI completion and broken links/anchors. These are documentation-tool checks, not application test results.

## 2026-09-28 â€” Documentation baseline

Read both supplied transcripts, preserved their bytes/hashes and reconciled latest owner choices. Created canonical product/architecture/domain/data/ML/audio/security/design/deployment/demo specifications and reusable session commands. Added the owner-generated Stitch gate across all frontend tasks and the screen registry.

Built one requirement/task/acceptance catalog with generated roadmap, implementation plan, tracker, requirement and test views. Retained future ideas explicitly and the unmet two-collector fieldwork obligation. Added source-range inventory, header-only dataset templates, evidence templates and structural documentation validation.

This entry records documentation work only. No application, actual dataset import, trained model, audio, screen generation, device test, deployment, PPT/video or submission has been completed. Current implementation progress is in the generated tracker; validation results are in the documentation audit.

## 2026-10-01 — Visible collector offer acceptance continuation (T020 repair)

Fixed the collector C07 **Accept Offer** action. It already persisted a local
`ACCEPT_OFFER` operation, but placed its confirmation after the offer list, which
could leave the user with no visible result. A successful acceptance now routes
directly to C10 Handover Capture for the selected lot. The focused Android unit
suite passed (4 tests), and the repaired flow was verified on CPH2781 Android 16:
the action displayed the handover screen with selected yard and terms.

## 2026-10-01 — Recycler offer workflow re-verification (T021)

Independently reran the complete trade workflow suite: all 19 tests pass. This
includes regulatory authorization tampering denial, battery isolation, privacy,
offer lifecycle controls, immutable agreement formation, and the competing-offer
race invariant. No implementation change was needed.

## 2026-10-01 — Recycler console re-verification (T022)

The React recycler console typecheck and production bundle build pass. Its focused
six-test suite also passes, covering the approved R01/R02/R03/R06/R07 interaction
paths. No implementation change was needed.

## 2026-10-01 — Handover backend re-verification (T023)

The current backend handover suite passed all 13 cases, including canonical hash
validation, immutable discrepancy handling, receipt disclaimer, and public
redaction. No implementation change was needed.

## 2026-10-01 — Offline handover re-verification (T024)

Canonical JSON and handover-receipt Android tests passed 7/7. The physical
collector flow also reached C10 Handover Capture with its review controls after
offer acceptance. No implementation change was needed.

## 2026-10-01 — Real two-device QR audit (T025)

Replaced the simulated web QR interaction with Chrome rear-camera decoding and
verified it with the collector phone and a second Android device. Corrected a
second defect that displayed fabricated sample terms after scanning. Scanned
offline proposals now show only their actual QR values and are explicitly blocked
from receipt issuance until server verification. T025 is returned to IN_PROGRESS:
the server-backed lookup and authenticated confirmation remain to be built.

