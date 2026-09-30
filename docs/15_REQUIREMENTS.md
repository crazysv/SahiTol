# Complete requirement register

Generated from [catalog](planning/catalog.json) and [status](planning/status.json). Edit those files, then run `python scripts/render_docs.py` and `python scripts/check_docs.py`. Do not edit this view independently.

Each row below has scope, source, detailed specification, implementation tasks and observable acceptance. E/P citations reference physical lines in preserved [Entire_Content](sources/Entire_Content.txt) / [previous_convo](sources/previous_convo.txt). CURRENT_REQUEST means the owner’s present instructions. Historical passages are interpreted through [decisions](09_DECISIONS.md), not executed literally.

## R-GOV-01

**Consistent SahiTol identity and latest scope** — RELEASE.

Source: P:2535-2569; P:2632-2658. Specification: [09_DECISIONS](09_DECISIONS.md).

Implementation: [T001](07_IMPLEMENTATION_PLAN.md#t001), [T048](07_IMPLEMENTATION_PLAN.md#t048). Acceptance: [AT-001](20_TEST_ACCEPTANCE.md#at-001).

Inspect app, package metadata, repository and deck: SahiTol is the product name, the SIH title is retained only as the problem title, and no superseded stack or selected feature is silently substituted.

## R-GOV-02

**Owner-generated Stitch frontend gate** — RELEASE.

Source: CURRENT_REQUEST. Specification: [05_DESIGN_STITCH](05_DESIGN_STITCH.md).

Implementation: [T002](07_IMPLEMENTATION_PLAN.md#t002), [T017](07_IMPLEMENTATION_PLAN.md#t017), [T020](07_IMPLEMENTATION_PLAN.md#t020), [T022](07_IMPLEMENTATION_PLAN.md#t022), [T024](07_IMPLEMENTATION_PLAN.md#t024), [T025](07_IMPLEMENTATION_PLAN.md#t025), [T027](07_IMPLEMENTATION_PLAN.md#t027), [T030](07_IMPLEMENTATION_PLAN.md#t030), [T034](07_IMPLEMENTATION_PLAN.md#t034), [T039](07_IMPLEMENTATION_PLAN.md#t039). Acceptance: [AT-002](20_TEST_ACCEPTANCE.md#at-002).

For each implemented screen/state find owner notification plus Stitch project/screen/revision and approval; a missing design leaves that UI waiting and never produces an invented replacement.

## R-GOV-03

**Traceable continuous agent execution** — RELEASE.

Source: CURRENT_REQUEST. Specification: [13_RECOVERY](13_RECOVERY.md).

Implementation: [T001](07_IMPLEMENTATION_PLAN.md#t001), [T050](07_IMPLEMENTATION_PLAN.md#t050). Acceptance: [AT-003](20_TEST_ACCEPTANCE.md#at-003).

In a fresh session invoke session-start then session-continue: agent reconstructs state, reads task specs, selects an eligible task, preserves blockers and updates status/evidence before progressing without routine next-task permission.

## R-GOV-04

**Deadline and all four deliverables** — RELEASE.

Source: P:2592-2615; P:2634-2647. Specification: [25_RELEASE_CHECKLIST](25_RELEASE_CHECKLIST.md).

Implementation: [T048](07_IMPLEMENTATION_PLAN.md#t048), [T049](07_IMPLEMENTATION_PLAN.md#t049), [T050](07_IMPLEMENTATION_PLAN.md#t050). Acceptance: [AT-004](20_TEST_ACCEPTANCE.md#at-004).

Release handoff contains tested PPT, accessible demo video link, installable APK/prototype link and GitHub repo; portal cutoff/format and actual submission status are explicitly recorded.

## R-ARC-01

**Native Android architecture and feasibility** — RELEASE.

Source: P:1970-1975; P:2602-2607. Specification: [03_TECHSPEC](03_TECHSPEC.md).

Implementation: [T001](07_IMPLEMENTATION_PLAN.md#t001), [T003](07_IMPLEMENTATION_PLAN.md#t003). Acceptance: [AT-005](20_TEST_ACCEPTANCE.md#at-005).

Approved feasibility screen on a named real Android phone captures photo, persists Room data through restart and performs offline LiteRT inference; Kotlin/Compose/Room/WorkManager remain the collector implementation.

## R-ARC-02

**Frozen API web database and storage stack** — RELEASE.

Source: P:2061-2286; P:2295-2316; P:2636-2646. Specification: [03_TECHSPEC](03_TECHSPEC.md).

Implementation: [T001](07_IMPLEMENTATION_PLAN.md#t001), [T006](07_IMPLEMENTATION_PLAN.md#t006), [T008](07_IMPLEMENTATION_PLAN.md#t008). Acceptance: [AT-006](20_TEST_ACCEPTANCE.md#at-006).

Build and inspect API/web/database configuration: FastAPI, React/Vite, PostgreSQL/PostGIS, local volume and hosted private storage work through the documented contracts with dependency locks.

## R-AUTH-01

**Minimal profile and phone/PIN access** — RELEASE.

Source: E:5964-5979; P:1959-1973; P:2494-2495. Specification: [16_API_CONTRACT](16_API_CONTRACT.md).

Implementation: [T007](07_IMPLEMENTATION_PLAN.md#t007), [T017](07_IMPLEMENTATION_PLAN.md#t017). Acceptance: [AT-007](20_TEST_ACCEPTANCE.md#at-007).

Register/login with phone and PIN; store no plaintext PIN; profile uses ID/alias/language/general area, asks for no Aadhaar/PAN/bank details and shows recoverable auth errors.

## R-AUTH-02

**Role and object authorization** — RELEASE.

Source: E:2610-2638; E:6813-6857. Specification: [12_GUARDRAILS](12_GUARDRAILS.md).

Implementation: [T007](07_IMPLEMENTATION_PLAN.md#t007), [T040](07_IMPLEMENTATION_PLAN.md#t040). Acceptance: [AT-008](20_TEST_ACCEPTANCE.md#at-008).

Collector A cannot read/mutate B's lots; recycler A cannot confirm B's facility handover; collector cannot become admin by editing payload; invalid/expired tokens are rejected server-side.

## R-AUTH-03

**Offline session and safe logout** — RELEASE.

Source: P:1611-1626; E:1285-1320. Specification: [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md).

Implementation: [T007](07_IMPLEMENTATION_PLAN.md#t007), [T013](07_IMPLEMENTATION_PLAN.md#t013), [T015](07_IMPLEMENTATION_PLAN.md#t015), [T017](07_IMPLEMENTATION_PLAN.md#t017). Acceptance: [AT-009](20_TEST_ACCEPTANCE.md#at-009).

After successful activation disconnect and restart: local profile/drafts remain usable; expired token pauses authenticated sync; reauth resumes same operations; logout cannot silently discard pending data or expose it to another user.

## R-AUTH-04

**Isolated demo access without SMS** — RELEASE.

Source: P:2005-2014; P:2646-2647. Specification: [12_GUARDRAILS](12_GUARDRAILS.md).

Implementation: [T007](07_IMPLEMENTATION_PLAN.md#t007), [T040](07_IMPLEMENTATION_PLAN.md#t040), [T050](07_IMPLEMENTATION_PLAN.md#t050). Acceptance: [AT-010](20_TEST_ACCEPTANCE.md#at-010).

Bundled demo profile and demo OTP/bypass are explicitly labelled and isolated; public demo credentials cannot access non-demo users, verification controls or unrestricted admin actions.

## R-LOT-01

**Complete material taxonomy and aliases** — RELEASE.

Source: E:509-537; E:2928-2959; E:6030-6049. Specification: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Implementation: [T010](07_IMPLEMENTATION_PLAN.md#t010), [T017](07_IMPLEMENTATION_PLAN.md#t017). Acceptance: [AT-011](20_TEST_ACCEPTANCE.md#at-011).

Create draft lots for CRT,LCD,PCB,cable,battery,motor/magnet,mixed plastics,mixed electronics and UNKNOWN; hi/mr/en local aliases resolve to stable IDs, not hardcoded price values.

## R-LOT-02

**Camera image import compression and privacy** — RELEASE.

Source: E:2664-2675; P:2305-2310. Specification: [06_SCHEMA](06_SCHEMA.md).

Implementation: [T008](07_IMPLEMENTATION_PLAN.md#t008), [T013](07_IMPLEMENTATION_PLAN.md#t013), [T017](07_IMPLEMENTATION_PLAN.md#t017). Acceptance: [AT-012](20_TEST_ACCEPTANCE.md#at-012).

Take/import a photo, deny camera permission, retry capture and restart; saved image remains linked, upload validates type/size and strips EXIF; no-photo draft is allowed but evidence completeness is explicit.

## R-LOT-03

**Weight condition description and validation** — RELEASE.

Source: E:487-505; E:5981-6023. Specification: [04_APPFLOW](04_APPFLOW.md).

Implementation: [T016](07_IMPLEMENTATION_PLAN.md#t016), [T017](07_IMPLEMENTATION_PLAN.md#t017). Acceptance: [AT-013](20_TEST_ACCEPTANCE.md#at-013).

Save a draft then complete category/condition/description/positive finite weight; reject zero/negative/overflow values on submit; fractional kg round-trips as grams; suspicious large weight requires review without invented domain cap.

## R-LOT-04

**Collection and handover location/time provenance** — RELEASE.

Source: E:1003-1035; E:1854-1871. Specification: [06_SCHEMA](06_SCHEMA.md).

Implementation: [T016](07_IMPLEMENTATION_PLAN.md#t016), [T024](07_IMPLEMENTATION_PLAN.md#t024). Acceptance: [AT-014](20_TEST_ACCEPTANCE.md#at-014).

Record timestamps and GPS accuracy/capture age when permitted; denial uses labelled coarse/manual location or missing-data state; never fabricate coordinates or expose a home address in public records.

## R-LOT-05

**Durable draft lot lifecycle and cancellation** — RELEASE.

Source: E:403-461; E:1792-1820. Specification: [04_APPFLOW](04_APPFLOW.md).

Implementation: [T013](07_IMPLEMENTATION_PLAN.md#t013), [T016](07_IMPLEMENTATION_PLAN.md#t016), [T017](07_IMPLEMENTATION_PLAN.md#t017). Acceptance: [AT-015](20_TEST_ACCEPTANCE.md#at-015).

Create/edit/reopen/cancel a lot with stable UUID and legal transitions; restart preserves drafts; attempts to mutate confirmed historical terms or jump CLOSED→COLLECTED fail and are auditable.

## R-PRICE-01

**Price observations and in-app entry** — RELEASE.

Source: E:627-648; P:2491-2492. Specification: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Implementation: [T011](07_IMPLEMENTATION_PLAN.md#t011), [T020](07_IMPLEMENTATION_PLAN.md#t020). Acceptance: [AT-016](20_TEST_ACCEPTANCE.md#at-016).

Enter an observation with material/subcategory, region, date, unit, price kind and source; edit via revision, moderate and export it; unknown dates or unsupported conversions are quarantined.

## R-PRICE-02

**Indicative weighted range and lot valuation** — RELEASE.

Source: E:652-676; E:2457-2488; E:6076-6105. Specification: [03_TECHSPEC](03_TECHSPEC.md).

Implementation: [T018](07_IMPLEMENTATION_PLAN.md#t018), [T020](07_IMPLEMENTATION_PLAN.md#t020). Acceptance: [AT-017](20_TEST_ACCEPTANCE.md#at-017).

A known comparable observation fixture yields specified weighted median/Q1/Q3 and estimate bounds in API and Android; weight changes recompute estimate; screen labels result indicative and retains snapshot/version.

## R-PRICE-03

**Source confidence freshness and empty prices** — RELEASE.

Source: E:568-597; E:710-728. Specification: [03_TECHSPEC](03_TECHSPEC.md).

Implementation: [T018](07_IMPLEMENTATION_PLAN.md#t018), [T020](07_IMPLEMENTATION_PLAN.md#t020). Acceptance: [AT-018](20_TEST_ACCEPTANCE.md#at-018).

Recent/few/stale/no-data fixtures show correct count, sources, timestamp, confidence and reason; no-data is INSUFFICIENT, never zero or a hidden synthetic fallback.

## R-PRICE-04

**History trends and actual offer comparison** — RELEASE.

Source: E:5352-5361; E:3810-3822. Specification: [03_TECHSPEC](03_TECHSPEC.md).

Implementation: [T018](07_IMPLEMENTATION_PLAN.md#t018), [T020](07_IMPLEMENTATION_PLAN.md#t020), [T021](07_IMPLEMENTATION_PLAN.md#t021). Acceptance: [AT-019](20_TEST_ACCEPTANCE.md#at-019).

View dated trend buckets and multiple offers in consistent units/regions; missing history displays a gap, no fabricated points; expired/noncomparable rates are labelled and do not become an agreed price.

## R-PRICE-05

**Quote anomaly review** — RELEASE.

Source: E:682-706; E:6639-6658. Specification: [03_TECHSPEC](03_TECHSPEC.md).

Implementation: [T028](07_IMPLEMENTATION_PLAN.md#t028), [T030](07_IMPLEMENTATION_PLAN.md#t030). Acceptance: [AT-020](20_TEST_ACCEPTANCE.md#at-020).

Known low/high quotes trigger configured review reasons only when enough comparable data exists; alert says review, does not accuse fraud or block collector choice without a separate eligibility violation.

## R-REC-01

**Source-backed Delhi-NCR Maharashtra directory** — RELEASE.

Source: P:2526-2541; P:2646-2647. Specification: [22_REGULATORY_SAFETY](22_REGULATORY_SAFETY.md).

Implementation: [T012](07_IMPLEMENTATION_PLAN.md#t012). Acceptance: [AT-021](20_TEST_ACCEPTANCE.md#at-021).

Import CPCB plus DPCC and MPCB records with facility role/source document/page/date/registration and lineage; do not relabel a collection point as a recycler or claim that a list import creates a partnership.

## R-REC-02

**Verification levels and expiry** — RELEASE.

Source: E:782-805; E:5816-5849. Specification: [22_REGULATORY_SAFETY](22_REGULATORY_SAFETY.md).

Implementation: [T012](07_IMPLEMENTATION_PLAN.md#t012), [T019](07_IMPLEMENTATION_PLAN.md#t019), [T029](07_IMPLEMENTATION_PLAN.md#t029). Acceptance: [AT-022](20_TEST_ACCEPTANCE.md#at-022).

L0/L1/L2 never become verified formal destinations; stale/expired/revoked/unproven route authorization removes strong badge and matching eligibility even if original source was official.

## R-REC-03

**Facility materials rates pickup and service area** — RELEASE.

Source: E:732-778; E:5936-5949. Specification: [06_SCHEMA](06_SCHEMA.md).

Implementation: [T012](07_IMPLEMENTATION_PLAN.md#t012), [T021](07_IMPLEMENTATION_PLAN.md#t021), [T022](07_IMPLEMENTATION_PLAN.md#t022). Acceptance: [AT-023](20_TEST_ACCEPTANCE.md#at-023).

Facility user updates rates/availability/service area with provenance while authorization fields stay admin-controlled; unknown operational data stays unknown; acceptance/minimum-weight terms are visible.

## R-REC-04

**Route-aware eligibility** — RELEASE.

Source: E:249-280; E:830-859. Specification: [22_REGULATORY_SAFETY](22_REGULATORY_SAFETY.md).

Implementation: [T019](07_IMPLEMENTATION_PLAN.md#t019), [T023](07_IMPLEMENTATION_PLAN.md#t023). Acceptance: [AT-024](20_TEST_ACCEPTANCE.md#at-024).

Battery lot cannot match a facility evidenced only for e-waste; incompatible material, unverified current registration or unsupported service/weight constraints exclude before ranking and before confirmation.

## R-REC-05

**Explainable ranking with geography** — RELEASE.

Source: E:2518-2540; P:2297-2301. Specification: [03_TECHSPEC](03_TECHSPEC.md).

Implementation: [T019](07_IMPLEMENTATION_PLAN.md#t019), [T020](07_IMPLEMENTATION_PLAN.md#t020). Acceptance: [AT-025](20_TEST_ACCEPTANCE.md#at-025).

Run fixed candidates: deterministic score and tie-break, PostGIS distance online, cached local parity within tolerance; expose contributions and unknowns; never invent pickup, price or reliability.

## R-REC-06

**Offline list online map and no-match path** — RELEASE.

Source: P:1995-2003; E:3792-3806. Specification: [05_DESIGN_STITCH](05_DESIGN_STITCH.md).

Implementation: [T019](07_IMPLEMENTATION_PLAN.md#t019), [T020](07_IMPLEMENTATION_PLAN.md#t020). Acceptance: [AT-026](20_TEST_ACCEPTANCE.md#at-026).

With network/maps/GPS unavailable directory list works with cached age and distance when possible; no-match can save/widen geography, never switch battery route; online MapLibre includes attribution and permitted tiles.

## R-OFFER-01

**Recycler inbound offer accept reject workflow** — RELEASE.

Source: E:3046-3055; E:5936-5949. Specification: [04_APPFLOW](04_APPFLOW.md).

Implementation: [T021](07_IMPLEMENTATION_PLAN.md#t021), [T022](07_IMPLEMENTATION_PLAN.md#t022). Acceptance: [AT-027](20_TEST_ACCEPTANCE.md#at-027).

Collector submits lot, linked recycler sees evidence and quotes/accepts/rejects; collector selects one live offer; rejected/expired requests preserve history and can return to another compatible match.

## R-OFFER-02

**Immutable agreed terms and offer races** — RELEASE.

Source: E:5485-5487; E:7600-7605. Specification: [04_APPFLOW](04_APPFLOW.md).

Implementation: [T021](07_IMPLEMENTATION_PLAN.md#t021), [T023](07_IMPLEMENTATION_PLAN.md#t023). Acceptance: [AT-028](20_TEST_ACCEPTANCE.md#at-028).

Two simultaneous acceptances leave one active agreement; cached expired offer cannot silently bind; later price-board refresh does not modify accepted terms; material/weight/price changes require explicit acknowledgement.

## R-HAND-01

**Offline pending handover evidence** — RELEASE.

Source: P:2489-2490; E:5120-5169. Specification: [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md).

Implementation: [T023](07_IMPLEMENTATION_PLAN.md#t023), [T024](07_IMPLEMENTATION_PLAN.md#t024). Acceptance: [AT-029](20_TEST_ACCEPTANCE.md#at-029).

In airplane mode create UUID proposal with photo references, grams, location quality, time, parties/terms and hash; restart shows PENDING_CONFIRMATION and sync pending, never recycler-confirmed.

## R-HAND-02

**Two-device recycler confirmation** — RELEASE.

Source: P:2612-2629; P:2641-2644. Specification: [04_APPFLOW](04_APPFLOW.md).

Implementation: [T025](07_IMPLEMENTATION_PLAN.md#t025), [T044](07_IMPLEMENTATION_PLAN.md#t044). Acceptance: [AT-030](20_TEST_ACCEPTANCE.md#at-030).

Borrowed second Android browser scans collector QR over HTTPS, identifies the correct facility/lot, submits authorized confirmation and collector sees it after pull; unsynced reference explains waiting and supports retry/manual reference.

## R-HAND-03

**Canonical hash and append-only event chain** — RELEASE.

Source: E:1081-1109; P:2139-2149. Specification: [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md).

Implementation: [T023](07_IMPLEMENTATION_PLAN.md#t023), [T024](07_IMPLEMENTATION_PLAN.md#t024), [T043](07_IMPLEMENTATION_PLAN.md#t043). Acceptance: [AT-031](20_TEST_ACCEPTANCE.md#at-031).

Same frozen JSON fixture hashes identically in Python/Kotlin/web; one altered byte invalidates expected digest; original proposal and confirmation events remain linked and unchanged; UI never describes bare SHA-256 as a signature.

## R-HAND-04

**Public verification and privacy** — RELEASE.

Source: E:1039-1077; E:2642-2662. Specification: [16_API_CONTRACT](16_API_CONTRACT.md).

Implementation: [T023](07_IMPLEMENTATION_PLAN.md#t023), [T025](07_IMPLEMENTATION_PLAN.md#t025), [T040](07_IMPLEMENTATION_PLAN.md#t040). Acceptance: [AT-032](20_TEST_ACCEPTANCE.md#at-032).

An unguessable receipt link shows current redacted status and record/hash comparison; public visitor cannot fetch phone/GPS/photos/payment details; QR possession alone cannot authorize confirmation.

## R-HAND-05

**Weight grade price disagreement** — RELEASE.

Source: E:3826-3898. Specification: [04_APPFLOW](04_APPFLOW.md).

Implementation: [T023](07_IMPLEMENTATION_PLAN.md#t023), [T025](07_IMPLEMENTATION_PLAN.md#t025), [T027](07_IMPLEMENTATION_PLAN.md#t027), [T028](07_IMPLEMENTATION_PLAN.md#t028). Acceptance: [AT-033](20_TEST_ACCEPTANCE.md#at-033).

Different measured weight/grade/price retains estimate and AI suggestion, sets pending acknowledgement/review and variance reason; neither party overwrites original facts; collector agreement or documented dispute is recorded.

## R-HAND-06

**Receipt PDF passport and procurement exports** — RELEASE.

Source: E:970-1035; P:2305-2310. Specification: [16_API_CONTRACT](16_API_CONTRACT.md).

Implementation: [T024](07_IMPLEMENTATION_PLAN.md#t024), [T025](07_IMPLEMENTATION_PLAN.md#t025), [T031](07_IMPLEMENTATION_PLAN.md#t031). Acceptance: [AT-034](20_TEST_ACCEPTANCE.md#at-034).

Export offline pending PDF and server confirmed PDF/CSV; identifiers/status/hash/provenance agree with timeline; record is called Digital Handover Record and includes non-EPR boundary, never an official manifest claim.

## R-PAY-01

**Cash optional UPI and payment recording** — RELEASE.

Source: E:1143-1167; E:6232-6249. Specification: [04_APPFLOW](04_APPFLOW.md).

Implementation: [T026](07_IMPLEMENTATION_PLAN.md#t026), [T027](07_IMPLEMENTATION_PLAN.md#t027). Acceptance: [AT-035](20_TEST_ACCEPTANCE.md#at-035).

Record cash without bank account/gateway; optional UPI/other records an assertion and reference, not transfer; both sides see actor/time/acknowledgement and can dispute.

## R-PAY-02

**Partial dues reversals and closure** — RELEASE.

Source: E:1113-1139; E:9548-9572. Specification: [06_SCHEMA](06_SCHEMA.md).

Implementation: [T026](07_IMPLEMENTATION_PLAN.md#t026), [T027](07_IMPLEMENTATION_PLAN.md#t027). Acceptance: [AT-036](20_TEST_ACCEPTANCE.md#at-036).

Two partial receipts sum once, duplicate operation does not increase paid total, overpayment is reviewed, reversal links original; RECEIVED with pending dues cannot become CLOSED; disagreement remains visible.

## R-PAY-03

**Collector earnings and transaction history** — RELEASE.

Source: E:1113-1139; E:6206-6230. Specification: [04_APPFLOW](04_APPFLOW.md).

Implementation: [T026](07_IMPLEMENTATION_PLAN.md#t026), [T027](07_IMPLEMENTATION_PLAN.md#t027). Acceptance: [AT-037](20_TEST_ACCEPTANCE.md#at-037).

Filter history/month and reconcile gross, acknowledged paid, asserted pending and remaining dues against transactions; offline view shows freshness; no demo earnings or estimates contaminate real settled totals.

## R-OFF-01

**Offline reference and local core journey** — RELEASE.

Source: E:1285-1320; E:1586-1602. Specification: [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md).

Implementation: [T009](07_IMPLEMENTATION_PLAN.md#t009), [T013](07_IMPLEMENTATION_PLAN.md#t013), [T017](07_IMPLEMENTATION_PLAN.md#t017), [T020](07_IMPLEMENTATION_PLAN.md#t020). Acceptance: [AT-038](20_TEST_ACCEPTANCE.md#at-038).

After bootstrap, airplane mode still allows material/safety/price/directory/history reads and photo/category/weight/lot/pending handover writes; fresh install offers clearly labelled demo reference or activation requirement, never an empty misleading success state.

## R-OFF-02

**Atomic durable outbox and image survival** — RELEASE.

Source: E:1627-1655; P:2123-2137. Specification: [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md).

Implementation: [T013](07_IMPLEMENTATION_PLAN.md#t013), [T043](07_IMPLEMENTATION_PLAN.md#t043). Acceptance: [AT-039](20_TEST_ACCEPTANCE.md#at-039).

Kill process during/after local save and media staging; either fully recover object+event+outbox+file or report unsaved failure; never drop a pending record through migration, cleanup or storage pressure.

## R-OFF-03

**Idempotency and partial batch acknowledgement** — RELEASE.

Source: E:1659-1677; E:6320-6345. Specification: [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md).

Implementation: [T014](07_IMPLEMENTATION_PLAN.md#t014), [T043](07_IMPLEMENTATION_PLAN.md#t043). Acceptance: [AT-040](20_TEST_ACCEPTANCE.md#at-040).

Resend an operation after server commit/ACK loss and in mixed-success batches; each accepted effect occurs once, different payload with reused ID conflicts, successful siblings stay acknowledged.

## R-OFF-04

**Versioned conflicts and dependency order** — RELEASE.

Source: E:1683-1717; E:9031-9053. Specification: [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md).

Implementation: [T014](07_IMPLEMENTATION_PLAN.md#t014), [T015](07_IMPLEMENTATION_PLAN.md#t015), [T043](07_IMPLEMENTATION_PLAN.md#t043). Acceptance: [AT-041](20_TEST_ACCEPTANCE.md#at-041).

Out-of-order lot/media/handover operations wait on parents; concurrent changes return current server version without erasing local proposal; reference tombstones update caches while historical receipts retain snapshots.

## R-OFF-05

**WorkManager retries foreground sync and auth pause** — RELEASE.

Source: P:1472-1483; P:2123-2137. Specification: [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md).

Implementation: [T015](07_IMPLEMENTATION_PLAN.md#t015), [T017](07_IMPLEMENTATION_PLAN.md#t017), [T043](07_IMPLEMENTATION_PLAN.md#t043). Acceptance: [AT-042](20_TEST_ACCEPTANCE.md#at-042).

With intermittent network/reboot/background restriction sync resumes durably or via manual button; 401 pauses for auth, 409 review, 422 repair, 429 backoff and 5xx retry without busy loop or lost records.

## R-OFF-06

**Visible queue and recoverable failure states** — RELEASE.

Source: E:7607-7609. Specification: [05_DESIGN_STITCH](05_DESIGN_STITCH.md).

Implementation: [T015](07_IMPLEMENTATION_PLAN.md#t015), [T017](07_IMPLEMENTATION_PLAN.md#t017), [T043](07_IMPLEMENTATION_PLAN.md#t043). Acceptance: [AT-043](20_TEST_ACCEPTANCE.md#at-043).

Collector can distinguish local/sending/synced/needs-login/conflict/rejected, inspect queue count/last sync, retry safely and retain a support reference; no generic green success on HTTP failure.

## R-ML-01

**Licensed suitable public dataset only** — RELEASE.

Source: P:2628-2629; E:1987-2008. Specification: [19_AI_ML](19_AI_ML.md).

Implementation: [T032](07_IMPLEMENTATION_PLAN.md#t032), [T047](07_IMPLEMENTATION_PLAN.md#t047). Acceptance: [AT-044](20_TEST_ACCEPTANCE.md#at-044).

Every training image has permitted-use evidence, source/license/hash/class/object-group/split; no fabricated field images; class coverage report exposes generic datasets that do not cover actual e-waste taxonomy.

## R-ML-02

**Reproducible leakage-free training and evaluation** — RELEASE.

Source: E:2398-2449; E:6676-6710. Specification: [19_AI_ML](19_AI_ML.md).

Implementation: [T033](07_IMPLEMENTATION_PLAN.md#t033), [T047](07_IMPLEMENTATION_PLAN.md#t047). Acceptance: [AT-045](20_TEST_ACCEPTANCE.md#at-045).

Train from saved configuration with object-group splits and training-only augmentation; report actual untouched-test macro/per-class F1, confusion matrix, counts/limits, calibration threshold and quantization parity.

## R-ML-03

**Bundled offline advisory classifier** — RELEASE.

Source: P:2639-2642; E:2351-2394. Specification: [19_AI_ML](19_AI_ML.md).

Implementation: [T034](07_IMPLEMENTATION_PLAN.md#t034), [T044](07_IMPLEMENTATION_PLAN.md#t044). Acceptance: [AT-046](20_TEST_ACCEPTANCE.md#at-046).

Real SahiTol model predicts offline on phone with versioned preprocessing; user confirms/changes; low-confidence/OOD/corrupt-model fallback stays usable; no automatic certification, pricing or route determination.

## R-ML-04

**Correction data and measured model constraints** — RELEASE.

Source: E:2402-2419; E:3328-3342. Specification: [19_AI_ML](19_AI_ML.md).

Implementation: [T034](07_IMPLEMENTATION_PLAN.md#t034), [T045](07_IMPLEMENTATION_PLAN.md#t045), [T047](07_IMPLEMENTATION_PLAN.md#t047). Acceptance: [AT-047](20_TEST_ACCEPTANCE.md#at-047).

Persist suggestion/confidence/model version separately from human label; report correction/abstention denominators and inference/APK/memory on actual device; no training reuse without documented rights/purpose.

## R-SAFE-01

**Contextual pictorial safety guidance** — RELEASE.

Source: E:1171-1197; E:6251-6267. Specification: [22_REGULATORY_SAFETY](22_REGULATORY_SAFETY.md).

Implementation: [T035](07_IMPLEMENTATION_PLAN.md#t035), [T039](07_IMPLEMENTATION_PLAN.md#t039). Acceptance: [AT-048](20_TEST_ACCEPTANCE.md#at-048).

PCB/cable/CRT/battery selection opens appropriate short pictorial warning in both languages offline; content is sourced/versioned and avoids instructions for unsafe processing.

## R-LANG-01

**Complete Hindi Marathi and English fallback** — RELEASE.

Source: E:1201-1231; P:2636-2643. Specification: [14_TRANSLATION_AUDIO_AUDIT](14_TRANSLATION_AUDIO_AUDIT.md).

Implementation: [T036](07_IMPLEMENTATION_PLAN.md#t036), [T046](07_IMPLEMENTATION_PLAN.md#t046). Acceptance: [AT-049](20_TEST_ACCEPTANCE.md#at-049).

All collector critical keys, labels, validation/denial/conflict/payment states and dynamic material terms work in hi/mr; language persists; unavailable translation is reported in audit, not hidden by English fallback.

## R-LANG-02

**Offline audio prompts and spoken prices** — RELEASE.

Source: P:1949-1950; P:2618-2621; E:5356-5361. Specification: [14_TRANSLATION_AUDIO_AUDIT](14_TRANSLATION_AUDIO_AUDIT.md).

Implementation: [T037](07_IMPLEMENTATION_PLAN.md#t037), [T046](07_IMPLEMENTATION_PLAN.md#t046). Acceptance: [AT-050](20_TEST_ACCEPTANCE.md#at-050).

In airplane mode tap Hindi and Marathi audio for changing price ranges, decimals, rupees/paise/per-kg and safety/pending/success; spoken value exactly matches visible value; asset licences and missing-clip behavior are recorded.

## R-UX-01

**Low-literacy accessible approved interactions** — RELEASE.

Source: E:3057-3117; E:5519-5527. Specification: [05_DESIGN_STITCH](05_DESIGN_STITCH.md).

Implementation: [T017](07_IMPLEMENTATION_PLAN.md#t017), [T036](07_IMPLEMENTATION_PLAN.md#t036), [T044](07_IMPLEMENTATION_PLAN.md#t044), [T046](07_IMPLEMENTATION_PLAN.md#t046). Acceptance: [AT-051](20_TEST_ACCEPTANCE.md#at-051).

Core screens use approved icons/photos, short labels and tap-to-hear, primary 56dp mobile targets, no color-only status, at most three primary inputs per step; large text/TalkBack/numeric input and explicit numeral preference remain usable.

## R-UX-02

**Entry-level Android performance** — RELEASE.

Source: E:3121-3135; E:7279-7300; P:2309-2310. Specification: [03_TECHSPEC](03_TECHSPEC.md).

Implementation: [T045](07_IMPLEMENTATION_PLAN.md#t045). Acceptance: [AT-052](20_TEST_ACCEPTANCE.md#at-052).

Record named device, APK/model/audio sizes, memory and launch/save/compression/API/model timings against documented budgets; any miss stays visible with remediation, no borrowed benchmarks.

## R-DATA-01

**Material dataset reference and observations** — RELEASE.

Source: E:1970-1983; E:5351-5365. Specification: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Implementation: [T010](07_IMPLEMENTATION_PLAN.md#t010), [T016](07_IMPLEMENTATION_PLAN.md#t016), [T031](07_IMPLEMENTATION_PLAN.md#t031), [T047](07_IMPLEMENTATION_PLAN.md#t047). Acceptance: [AT-053](20_TEST_ACCEPTANCE.md#at-053).

Export material observations with category/subcategory/description/image/weight/condition/source/value linked to lots while catalog remains distinct; new lot produces an observation through normal workflow.

## R-DATA-02

**Price dataset lifecycle and feedback** — RELEASE.

Source: E:1905-1922; E:5491-5498. Specification: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Implementation: [T011](07_IMPLEMENTATION_PLAN.md#t011), [T018](07_IMPLEMENTATION_PLAN.md#t018), [T031](07_IMPLEMENTATION_PLAN.md#t031), [T047](07_IMPLEMENTATION_PLAN.md#t047). Acceptance: [AT-054](20_TEST_ACCEPTANCE.md#at-054).

Import→validate→review→aggregate→display→confirmed-transaction feedback→history/export works; one eligible transaction adds one sourced price observation; disputes/demo records do not contaminate real summaries.

## R-DATA-03

**Recycler dataset lifecycle** — RELEASE.

Source: E:1926-1945; E:6533-6541. Specification: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Implementation: [T012](07_IMPLEMENTATION_PLAN.md#t012), [T021](07_IMPLEMENTATION_PLAN.md#t021), [T029](07_IMPLEMENTATION_PLAN.md#t029), [T031](07_IMPLEMENTATION_PLAN.md#t031), [T047](07_IMPLEMENTATION_PLAN.md#t047). Acceptance: [AT-055](20_TEST_ACCEPTANCE.md#at-055).

Import facility, review source/current status, update operational data, refresh/expire verification and export versions; original registry claim and later operational update remain separately attributable.

## R-DATA-04

**Transaction dataset generated by workflow** — RELEASE.

Source: E:1949-1967. Specification: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Implementation: [T026](07_IMPLEMENTATION_PLAN.md#t026), [T031](07_IMPLEMENTATION_PLAN.md#t031), [T047](07_IMPLEMENTATION_PLAN.md#t047). Acceptance: [AT-056](20_TEST_ACCEPTANCE.md#at-056).

A demonstrated lot→offer→handover→payment produces a transaction export with party IDs, original/final weights/values, locations/times and separate payment/lifecycle status without hand-inserting completion rows.

## R-DATA-05

**Traceability dataset generated by events** — RELEASE.

Source: E:1854-1884. Specification: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Implementation: [T023](07_IMPLEMENTATION_PLAN.md#t023), [T031](07_IMPLEMENTATION_PLAN.md#t031), [T047](07_IMPLEMENTATION_PLAN.md#t047). Acceptance: [AT-057](20_TEST_ACCEPTANCE.md#at-057).

Export collection through confirmed receipt/status events with evidence refs, weights, times, location quality, reference and confirmation; verify chain and correction lineage without mutable-history loss.

## R-DATA-06

**Minimal collector dataset and anonymization** — RELEASE.

Source: E:1888-1901. Specification: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Implementation: [T007](07_IMPLEMENTATION_PLAN.md#t007), [T031](07_IMPLEMENTATION_PLAN.md#t031), [T040](07_IMPLEMENTATION_PLAN.md#t040), [T047](07_IMPLEMENTATION_PLAN.md#t047). Acceptance: [AT-058](20_TEST_ACCEPTANCE.md#at-058).

Export collector ID/language/general area/history/totals with PII redacted by purpose; onboarding and transactions generate it; public export excludes phone, exact home location and credentials.

## R-DATA-07

**AI training dataset card and tabular links** — RELEASE.

Source: E:1987-2008; E:6527-6541. Specification: [19_AI_ML](19_AI_ML.md).

Implementation: [T032](07_IMPLEMENTATION_PLAN.md#t032), [T033](07_IMPLEMENTATION_PLAN.md#t033), [T047](07_IMPLEMENTATION_PLAN.md#t047). Acceptance: [AT-059](20_TEST_ACCEPTANCE.md#at-059).

Deliver training manifest/card with source, quality, size, labels, object splits and licensing plus nullable weight/price/location/transaction links where actually observed; absent measurements remain null, never inferred truth.

## R-DATA-08

**Provenance and demo isolation everywhere** — RELEASE.

Source: P:2646-2647; E:2678-2705. Specification: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Implementation: [T005](07_IMPLEMENTATION_PLAN.md#t005), [T029](07_IMPLEMENTATION_PLAN.md#t029), [T031](07_IMPLEMENTATION_PLAN.md#t031), [T040](07_IMPLEMENTATION_PLAN.md#t040). Acceptance: [AT-060](20_TEST_ACCEPTANCE.md#at-060).

Display and export origin_class/source_kind/is_demo/date/version; public commercial data is not OFFICIAL; app-generated demo data is not real trade; mixed datasets disclose breakdown and synthetic lineage propagates.

## R-DATA-09

**Import cleaning geocoding and validation tools** — RELEASE.

Source: P:2312-2313; E:4022-4048. Specification: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Implementation: [T005](07_IMPLEMENTATION_PLAN.md#t005), [T012](07_IMPLEMENTATION_PLAN.md#t012), [T031](07_IMPLEMENTATION_PLAN.md#t031). Acceptance: [AT-061](20_TEST_ACCEPTANCE.md#at-061).

Rerun imports deterministically with checksums, preserve original documents and extraction locators, quarantine malformed rows, cache permitted geocodes and report accuracy; never silently discard or invent values.

## R-DATA-10

**Synthetic generator and edge-case scenarios** — RELEASE.

Source: E:2219-2272. Specification: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Implementation: [T005](07_IMPLEMENTATION_PLAN.md#t005), [T043](07_IMPLEMENTATION_PLAN.md#t043). Acceptance: [AT-062](20_TEST_ACCEPTANCE.md#at-062).

Seeded generator produces labelled valid workflow fixtures and separate invalid/retry/duplicate/mismatch/stale/reject/cancel scenarios; re-running does not duplicate seed identities or label generated records official.

## R-DATA-11

**Seven data cards and versioned exports** — RELEASE.

Source: E:3944-4018; E:5365-5367. Specification: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Implementation: [T031](07_IMPLEMENTATION_PLAN.md#t031), [T047](07_IMPLEMENTATION_PLAN.md#t047). Acceptance: [AT-063](20_TEST_ACCEPTANCE.md#at-063).

For all seven families deliver schema/version/count/source/license/validation/update/use/limitations and export checksum; counts reconcile with stored rows and demo filters; no completed card contains invented values.

## R-ADMIN-01

**Admin CRUD source and verification workflow** — RELEASE.

Source: E:3057-3065; E:5951-5960. Specification: [16_API_CONTRACT](16_API_CONTRACT.md).

Implementation: [T029](07_IMPLEMENTATION_PLAN.md#t029), [T030](07_IMPLEMENTATION_PLAN.md#t030). Acceptance: [AT-064](20_TEST_ACCEPTANCE.md#at-064).

Admin can review facilities, materials/aliases/safety, prices and source revisions; ordinary recycler cannot approve itself; edits are audited and sync to caches without rewriting old receipts.

## R-ADMIN-02

**Data quality review dashboard** — RELEASE.

Source: E:3570-3594; E:4022-4066; P:2644-2645. Specification: [MONITORING](MONITORING.md).

Implementation: [T028](07_IMPLEMENTATION_PLAN.md#t028), [T030](07_IMPLEMENTATION_PLAN.md#t030). Acceptance: [AT-065](20_TEST_ACCEPTANCE.md#at-065).

Dashboard calculates missing/invalid/stale/duplicate/inconsistent/source coverage and demo fractions; drill into a flag and resolve with actor/reason; all percentages have denominators and real query evidence.

## R-ADMIN-03

**Analytics and correct impact metrics** — RELEASE.

Source: E:3260-3342; E:5628-5636. Specification: [MONITORING](MONITORING.md).

Implementation: [T029](07_IMPLEMENTATION_PLAN.md#t029), [T030](07_IMPLEMENTATION_PLAN.md#t030). Acceptance: [AT-066](20_TEST_ACCEPTANCE.md#at-066).

Metrics derive from events with time/region/provenance filters: activity/quotes/matches/dues/disputes/sync/model quality and verified received grams; exclude demo and never equate received material with proven recycling or CO2 savings.

## R-ECON-01

**Illustrative unit-economics screen** — RELEASE.

Source: P:2614-2619; P:2645-2646; E:3183-3218. Specification: [23_UNIT_ECONOMICS](23_UNIT_ECONOMICS.md).

Implementation: [T038](07_IMPLEMENTATION_PLAN.md#t038), [T039](07_IMPLEMENTATION_PLAN.md#t039). Acceptance: [AT-067](20_TEST_ACCEPTANCE.md#at-067).

Change source-linked same-lot input assumptions and observe recalculated current/platform net, delta and valid percentage; show negative/no-benefit cases and explicit illustrative label separate from actual ledger.

## R-ECON-02

**Platform sustainability without collector fees** — RELEASE.

Source: E:3222-3257; E:9597-9603. Specification: [23_UNIT_ECONOMICS](23_UNIT_ECONOMICS.md).

Implementation: [T038](07_IMPLEMENTATION_PLAN.md#t038), [T048](07_IMPLEMENTATION_PLAN.md#t048). Acceptance: [AT-068](20_TEST_ACCEPTANCE.md#at-068).

Show hypothetical downstream fee revenue minus variable/fixed operating costs and break-even sensitivity; no fee actually charged, credit eligibility or guaranteed uplift implied.

## R-RES-01

**Honest secondary research and personas** — RELEASE.

Source: P:2517-2521; P:2646-2647. Specification: [21_RESEARCH_EVIDENCE](21_RESEARCH_EVIDENCE.md).

Implementation: [T004](07_IMPLEMENTATION_PLAN.md#t004), [T047](07_IMPLEMENTATION_PLAN.md#t047), [T048](07_IMPLEMENTATION_PLAN.md#t048). Acceptance: [AT-069](20_TEST_ACCEPTANCE.md#at-069).

Research package identifies each published source, its scope and design inference; personas/scenarios are labelled simulated; deck says no primary interviews completed and never invents participants or quotes.

## R-RES-02

**Two working collector/aggregator field research** — EXTERNAL_GAP.

Source: E:5367-5369; P:2538-2540; P:2647-2647. Specification: [21_RESEARCH_EVIDENCE](21_RESEARCH_EVIDENCE.md).

Implementation: [T004](07_IMPLEMENTATION_PLAN.md#t004), [T047](07_IMPLEMENTATION_PLAN.md#t047), [T048](07_IMPLEMENTATION_PLAN.md#t048), [T050](07_IMPLEMENTATION_PLAN.md#t050). Acceptance: [AT-070](20_TEST_ACCEPTANCE.md#at-070).

This remains UNMET while desk research is the owner choice. Only actual consented engagement with at least two working participants and evidence could satisfy it; documentation or synthetic scenarios cannot mark it passed.

## R-REG-01

**Receipt terminology and no false authorization** — RELEASE.

Source: E:186-245; E:6176-6204; P:2651-2653. Specification: [22_REGULATORY_SAFETY](22_REGULATORY_SAFETY.md).

Implementation: [T023](07_IMPLEMENTATION_PLAN.md#t023), [T024](07_IMPLEMENTATION_PLAN.md#t024), [T031](07_IMPLEMENTATION_PLAN.md#t031), [T048](07_IMPLEMENTATION_PLAN.md#t048). Acceptance: [AT-071](20_TEST_ACCEPTANCE.md#at-071).

App/PDF/CSV/deck call the artifact a platform Digital Handover Record; collector identity is not a licence; no official EPR certificate, government endorsement or established CPCB integration is claimed.

## R-SEC-01

**PIN abuse secrets and transport safety** — RELEASE.

Source: E:2610-2638; P:2301-2301. Specification: [12_GUARDRAILS](12_GUARDRAILS.md).

Implementation: [T007](07_IMPLEMENTATION_PLAN.md#t007), [T040](07_IMPLEMENTATION_PLAN.md#t040), [T041](07_IMPLEMENTATION_PLAN.md#t041). Acceptance: [AT-072](20_TEST_ACCEPTANCE.md#at-072).

Rate-limit PIN attempts, restrict role grants, rotate/revoke sessions, verify release HTTPS and restrictive CORS; APK/web/repo/log/QR contain no server key, PIN or private database credentials.

## R-SEC-02

**Privacy media access retention and audit** — RELEASE.

Source: E:2642-2675; E:6833-6857. Specification: [12_GUARDRAILS](12_GUARDRAILS.md).

Implementation: [T008](07_IMPLEMENTATION_PLAN.md#t008), [T040](07_IMPLEMENTATION_PLAN.md#t040), [T042](07_IMPLEMENTATION_PLAN.md#t042). Acceptance: [AT-073](20_TEST_ACCEPTANCE.md#at-073).

Private images require authorization; signed URLs expire; uploads cannot traverse filesystem; exports redact PII; retention/deletion policy preserves justified audit and pending data while clearing obsolete access safely.

## R-OPS-01

**Hosted remote judge access** — RELEASE.

Source: P:2610-2611; P:2638-2638. Specification: [DEPLOYMENT](DEPLOYMENT.md).

Implementation: [T041](07_IMPLEMENTATION_PLAN.md#t041), [T044](07_IMPLEMENTATION_PLAN.md#t044), [T050](07_IMPLEMENTATION_PLAN.md#t050). Acceptance: [AT-074](20_TEST_ACCEPTANCE.md#at-074).

Install release APK and open web console outside developer Wi-Fi; HTTPS API, PostGIS, private storage and QR work; cold start has recoverable UI; persistent photos survive API redeploy.

## R-OPS-02

**Reproducible local fallback and recovery** — RELEASE.

Source: P:2478-2479; P:2301-2301. Specification: [DEPLOYMENT](DEPLOYMENT.md).

Implementation: [T042](07_IMPLEMENTATION_PLAN.md#t042). Acceptance: [AT-075](20_TEST_ACCEPTANCE.md#at-075).

Fresh local Compose environment runs same schema and fixture journey; Android debug LAN configuration works; database/media restore rehearsed; browser scan fallback handles insecure local camera context without weakening release TLS.

## R-OPS-03

**No required paid runtime dependency** — RELEASE.

Source: P:1764-1806; E:1519-1537. Specification: [11_SECRETS_CHECKLIST](11_SECRETS_CHECKLIST.md).

Implementation: [T001](07_IMPLEMENTATION_PLAN.md#t001), [T037](07_IMPLEMENTATION_PLAN.md#t037), [T041](07_IMPLEMENTATION_PLAN.md#t041). Acceptance: [AT-076](20_TEST_ACCEPTANCE.md#at-076).

Audit dependency/service/config list and execute core with cloud speech/maps/AI unavailable; no mandatory SMS, LLM, payment gateway, custom domain or billing upgrade is required; current free-plan/account limitations documented.

## R-OPS-04

**Monitoring and diagnostics** — RELEASE.

Source: E:3282-3342; E:7607-7609. Specification: [MONITORING](MONITORING.md).

Implementation: [T028](07_IMPLEMENTATION_PLAN.md#t028), [T029](07_IMPLEMENTATION_PLAN.md#t029), [T042](07_IMPLEMENTATION_PLAN.md#t042). Acceptance: [AT-077](20_TEST_ACCEPTANCE.md#at-077).

Health and redacted structured logs expose failed sync/conflicts/media/DB errors with correlation IDs; dashboard denominators and last refresh distinguish outage from empty data; actionable local recovery steps work.

## R-QA-01

**Critical end-to-end and adversarial acceptance** — RELEASE.

Source: E:7217-7277; P:733-788. Specification: [20_TEST_ACCEPTANCE](20_TEST_ACCEPTANCE.md).

Implementation: [T043](07_IMPLEMENTATION_PLAN.md#t043), [T044](07_IMPLEMENTATION_PLAN.md#t044). Acceptance: [AT-078](20_TEST_ACCEPTANCE.md#at-078).

Pass online and airplane-mode lot→price→match→pending QR→sync→second-phone confirmation→payment→ledger→admin plus duplicate/crash/denial/stale/conflict/auth tests with actual logs and device evidence.

## R-QA-02

**Live scenario demonstration and backup** — RELEASE.

Source: E:5367-5369; E:7176-7213. Specification: [24_DEMO_PRESENTATION](24_DEMO_PRESENTATION.md).

Implementation: [T044](07_IMPLEMENTATION_PLAN.md#t044), [T049](07_IMPLEMENTATION_PLAN.md#t049). Acceptance: [AT-079](20_TEST_ACCEPTANCE.md#at-079).

A person actually performs the complete journey on devices, records failures and fixes, and produces playable demo/backups; no unexecuted script or prefilled database is represented as live usability evidence.

## R-DOC-01

**Outsider documentation and presenter readiness** — RELEASE.

Source: CURRENT_REQUEST; P:2585-2605. Specification: [00_README](00_README.md).

Implementation: [T047](07_IMPLEMENTATION_PLAN.md#t047), [T048](07_IMPLEMENTATION_PLAN.md#t048), [T050](07_IMPLEMENTATION_PLAN.md#t050). Acceptance: [AT-080](20_TEST_ACCEPTANCE.md#at-080).

New reader follows README to scope/architecture/decisions/data/run/demo; presenters can explain sources, offline pending vs confirmed, price limits, model limits, battery route and unmet fieldwork without relying on chat history.

## R-FUT-01

**Assisted collector and aggregator accounts** — FUTURE.

Source: E:1257-1284. Specification: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Implementation: [F001](07_IMPLEMENTATION_PLAN.md#f001). Acceptance: [FT-001](20_TEST_ACCEPTANCE.md#ft-001).

Explicit delegation/consent, actor versus beneficial owner, safe phone-less onboarding, separate permissions and offline ownership tests; no admin impersonation shortcut.

## R-FUT-02

**Multi-collector batching and pickup operations** — FUTURE.

Source: E:5920-5934. Specification: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Implementation: [F002](07_IMPLEMENTATION_PLAN.md#f002). Acceptance: [FT-002](20_TEST_ACCEPTANCE.md#ft-002).

Batch membership/weights/provenance and collector-level proceeds reconcile; operational capacity and actual pickup success recorded; no double counting.

## R-FUT-03

**Predictive prices and automated public feeds** — FUTURE.

Source: E:2490-2516; E:4669-4701. Specification: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Implementation: [F003](07_IMPLEMENTATION_PLAN.md#f003). Acceptance: [FT-003](20_TEST_ACCEPTANCE.md#ft-003).

Licensed sustained comparable observations, temporal holdout against statistical baseline, uncertainty/drift monitoring and a permitted refresh pipeline; keep indicative labels.

## R-FUT-04

**Consented active learning and broader classifier** — FUTURE.

Source: E:2278-2455; E:7154-7162. Specification: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Implementation: [F004](07_IMPLEMENTATION_PLAN.md#f004). Acceptance: [FT-004](20_TEST_ACCEPTANCE.md#ft-004).

New consent/rights policy, reviewed correction labels, expanded relevant classes, leakage-safe evaluation and version rollback; current release remains public-images-only.

## R-FUT-05

**Learned recycler ranking and advanced risk detection** — FUTURE.

Source: E:2544-2608. Specification: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Implementation: [F005](07_IMPLEMENTATION_PLAN.md#f005). Acceptance: [FT-005](20_TEST_ACCEPTANCE.md#ft-005).

Enough quality outcome labels, temporal evaluation/fairness/reason codes, human review and safety hard filters; do not learn to override route eligibility or accuse fraud.

## R-FUT-06

**Voice input and multilingual assistant** — FUTURE.

Source: E:2963-2989; E:6631-6637. Specification: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Implementation: [F006](07_IMPLEMENTATION_PLAN.md#f006). Acceptance: [FT-006](20_TEST_ACCEPTANCE.md#ft-006).

Free/licensed offline ASR where viable, hi/mr noisy-environment tests, explicit confirmation of money/material values and manual fallback; no arbitrary autonomous transaction agent.

## R-FUT-07

**Pickup route optimization** — FUTURE.

Source: E:4692-4701; E:4931-4934. Specification: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Implementation: [F007](07_IMPLEMENTATION_PLAN.md#f007). Acceptance: [FT-007](20_TEST_ACCEPTANCE.md#ft-007).

Consented operational locations, realistic vehicle/capacity/time windows, permitted map data and measured routing baseline; no continuous collector tracking by default.

## R-FUT-08

**ERP GST PRO brand and CPCB adapters** — FUTURE.

Source: E:4703-4716; E:7709-7711. Specification: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Implementation: [F008](07_IMPLEMENTATION_PLAN.md#f008). Acceptance: [FT-008](20_TEST_ACCEPTANCE.md#ft-008).

Documented official/partner API contracts, credentials and legal role, validated field mapping/sandbox evidence, access/audit controls; no claim of integration or certificate issuance before verification.

## R-FUT-09

**Downstream processing and material mass balance** — FUTURE.

Source: E:4753-4774; E:530-536. Specification: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Implementation: [F009](07_IMPLEMENTATION_PLAN.md#f009). Acceptance: [FT-009](20_TEST_ACCEPTANCE.md#ft-009).

Recycler processing evidence, batch splits/merges/yield reconciliation and independently supported downstream outcomes before calling received mass recycled.

## R-FUT-10

**Ed25519 server-signed records** — FUTURE.

Source: E:6196-6196; E:8551-8553. Specification: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Implementation: [F010](07_IMPLEMENTATION_PLAN.md#f010). Acceptance: [FT-010](20_TEST_ACCEPTANCE.md#ft-010).

Canonical payload parity, secure signing keys/rotation/revocation/trusted public-key distribution and verification fixtures; signature still does not prove physical facts.

## R-FUT-11

**Recovery indicator and environmental estimates** — FUTURE.

Source: E:5474-5474; E:7632-7632; E:9246-9246. Specification: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Implementation: [F011](07_IMPLEMENTATION_PLAN.md#f011). Acceptance: [FT-011](20_TEST_ACCEPTANCE.md#ft-011).

Exact peer-reviewed composition/LCA sources, material/device-specific uncertainty and defensible model validation; no invented official formula, exact metal yield or unsupported CO2 savings. Owner must explicitly promote this optional idea.

## R-FUT-12

**Supervised real-world pilot and partnerships** — FUTURE.

Source: E:3346-3396; E:4669-4691. Specification: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Implementation: [F012](07_IMPLEMENTATION_PLAN.md#f012). Acceptance: [FT-012](20_TEST_ACCEPTANCE.md#ft-012).

Consented real collectors/facilities, review safety/privacy/retention/support, actual partnership evidence and measured feedback; historical 5–10/20–30 counts are planning suggestions.

## R-FUT-13

**More regions languages and material routes** — FUTURE.

Source: E:4683-4691; E:4776-4790. Specification: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Implementation: [F013](07_IMPLEMENTATION_PLAN.md#f013). Acceptance: [FT-013](20_TEST_ACCEPTANCE.md#ft-013).

Region/language source and review coverage, safe route-specific authorization and model/material validation; preserve e-waste focus until explicit expansion.

## R-FUT-14

**Aggregated sector and government insights** — FUTURE.

Source: E:4718-4774. Specification: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Implementation: [F014](07_IMPLEMENTATION_PLAN.md#f014). Acceptance: [FT-014](20_TEST_ACCEPTANCE.md#ft-014).

Adequate representative data, aggregation/privacy controls and sample/denominator limitations for supply/capacity gaps, volatility/material flows/safety; no prototype national statistics.

## R-FUT-15

**Advanced dispute review and support workflow** — FUTURE.

Source: E:3876-3898. Specification: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Implementation: [F015](07_IMPLEMENTATION_PLAN.md#f015). Acceptance: [FT-015](20_TEST_ACCEPTANCE.md#ft-015).

Evidence submission/reviewer permissions/appeal/resolution timeline, immutable original quote/final terms and policy; basic pending/disputed states already required in release.

## R-FUT-16

**Optional payments messaging and monetization** — FUTURE.

Source: E:3222-3257; E:4917-4939; E:7017-7027. Specification: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Implementation: [F016](07_IMPLEMENTATION_PLAN.md#f016). Acceptance: [FT-016](20_TEST_ACCEPTANCE.md#ft-016).

Separate owner approval, lawful provider terms, fee transparency, webhook idempotency and reconciled settlement; SMS/WhatsApp/email/real UPI/paid SaaS not release dependencies.

## R-FUT-17

**Collector identity sharing and partner services** — FUTURE.

Source: E:7866-7866; E:5576-5576; E:9462-9462. Specification: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Implementation: [F017](07_IMPLEMENTATION_PLAN.md#f017). Acceptance: [FT-017](20_TEST_ACCEPTANCE.md#ft-017).

Minimal revocable identity QR/consent-scoped history sharing; verified partner eligibility rules before any credit/welfare claim; never public financial profiles or guaranteed access.

## R-FUT-18

**Production operations and scale** — FUTURE.

Source: E:4917-4939; E:7607-7609. Specification: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Implementation: [F018](07_IMPLEMENTATION_PLAN.md#f018). Acceptance: [FT-018](20_TEST_ACCEPTANCE.md#ft-018).

Measured bottleneck/load and security requirements justify queues/caching/infra, incident support and disaster recovery; no speculative Kubernetes/microservices or blockchain requirement.

