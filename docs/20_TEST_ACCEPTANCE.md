# Acceptance and verification register

Generated from [catalog](planning/catalog.json) and [status](planning/status.json). Edit those files, then run `python scripts/render_docs.py` and `python scripts/check_docs.py`. Do not edit this view independently.

These are test specifications, not executed tests. Capture actual environment/build/device/dataset, setup, action, expected versus observed result, logs/screenshots/DB counts and tester/time in the [evidence template](templates/TEST_EVIDENCE.md). Cases can require multiple fixtures. A prose claim or unchecked screenshot alone is not PASS.

## Verification layers

Use domain unit fixtures for weighted quantiles/rounding/matching/canonical hashes/state transitions; PostgreSQL integration for migrations, authorization and concurrent idempotency; Android Room/worker/instrumentation for durable offline behavior; web/API integration for recycler/admin; real devices for camera/QR/audio/performance. Choose concrete commands during T001 and save outputs per task.

Mandatory scenarios: complete online journey; activated airplane-mode photo→model→price/cache→pending QR→restart→reconnect→sync→second-phone confirmation→payment→ledger/admin; denied camera/GPS; no price/no match; expired facility/offer; differing measured weight; duplicate concurrent requests; crash after server commit; partial media/batch failure; token expiry/account switch; changed-payload retry; cursor expiry; disputed/reversed partial payment; missing/corrupt model/audio; Hindi/Marathi numeric boundaries; hosted cold start/redeploy persistence; backup/restore.

Use safe isolated demo data. Model accuracy/performance and language review are measured and recorded, never inferred from a successful build. Acceptance cases spanning multiple tasks close at integration, avoiding dependency deadlocks.

## AT-001

**Consistent SahiTol identity and latest scope** — RELEASE; status **NOT_RUN**.

Requirement: [R-GOV-01](15_REQUIREMENTS.md#r-gov-01). Tasks: [T001](07_IMPLEMENTATION_PLAN.md#t001), [T048](07_IMPLEMENTATION_PLAN.md#t048). Spec: [09_DECISIONS](09_DECISIONS.md).

Check: Inspect app, package metadata, repository and deck: SahiTol is the product name, the SIH title is retained only as the problem title, and no superseded stack or selected feature is silently substituted.

Evidence: None.

## AT-002

**Owner-generated Stitch frontend gate** — RELEASE; status **NOT_RUN**.

Requirement: [R-GOV-02](15_REQUIREMENTS.md#r-gov-02). Tasks: [T002](07_IMPLEMENTATION_PLAN.md#t002), [T017](07_IMPLEMENTATION_PLAN.md#t017), [T020](07_IMPLEMENTATION_PLAN.md#t020), [T022](07_IMPLEMENTATION_PLAN.md#t022), [T024](07_IMPLEMENTATION_PLAN.md#t024), [T025](07_IMPLEMENTATION_PLAN.md#t025), [T027](07_IMPLEMENTATION_PLAN.md#t027), [T030](07_IMPLEMENTATION_PLAN.md#t030), [T034](07_IMPLEMENTATION_PLAN.md#t034), [T039](07_IMPLEMENTATION_PLAN.md#t039). Spec: [05_DESIGN_STITCH](05_DESIGN_STITCH.md).

Check: For each implemented screen/state find owner notification plus Stitch project/screen/revision and approval; a missing design leaves that UI waiting and never produces an invented replacement.

Evidence: [T002_STITCH_DESIGNS.md](../docs/evidence/T002_STITCH_DESIGNS.md), [T022_RECYCLER_CONSOLE.md](../docs/evidence/T022_RECYCLER_CONSOLE.md), [T025_SECOND_DEVICE_CONFIRMATION.md](../docs/evidence/T025_SECOND_DEVICE_CONFIRMATION.md), [T030_ADMIN_DASHBOARD.md](../docs/evidence/T030_ADMIN_DASHBOARD.md), [T017_COLLECTOR_ONBOARDING_AND_LOTS.md](../docs/evidence/T017_COLLECTOR_ONBOARDING_AND_LOTS.md), [T020_COLLECTOR_PRICE_AND_RECYCLER_VIEWS.md](../docs/evidence/T020_COLLECTOR_PRICE_AND_RECYCLER_VIEWS.md), [T024_OFFLINE_QR_AND_COLLECTOR_RECEIPT.md](../docs/evidence/T024_OFFLINE_QR_AND_COLLECTOR_RECEIPT.md), [T027_COLLECTOR_LEDGER_AND_PAYMENTS.md](../docs/evidence/T027_COLLECTOR_LEDGER_AND_PAYMENTS.md), [T034_CLASSIFIER_ANDROID_FLOW.md](../docs/evidence/T034_CLASSIFIER_ANDROID_FLOW.md), [T039_ECONOMICS_AND_SAFETY_VIEWS.md](../docs/evidence/T039_ECONOMICS_AND_SAFETY_VIEWS.md). Note: Owner notification and Stitch screens registered and verified for T002, T017 (C01-C05, C14, C15), T020 (C06-C09), T022 (R01-R03, R06, R07), T024 (C10, C11, C16), T025 (R04, R05, V01), T027 (C12, C13), T030 (A01-A07), T034 (C05 classifier integration), and T039 (C17 safety hub, U01 unit economics). All 37 owner Stitch screens across 34 canonical specifications now IMPLEMENTED_VERIFIED.

## AT-003

**Traceable continuous agent execution** — RELEASE; status **NOT_RUN**.

Requirement: [R-GOV-03](15_REQUIREMENTS.md#r-gov-03). Tasks: [T001](07_IMPLEMENTATION_PLAN.md#t001), [T050](07_IMPLEMENTATION_PLAN.md#t050). Spec: [13_RECOVERY](13_RECOVERY.md).

Check: In a fresh session invoke session-start then session-continue: agent reconstructs state, reads task specs, selects an eligible task, preserves blockers and updates status/evidence before progressing without routine next-task permission.

Evidence: None.

## AT-004

**Deadline and all four deliverables** — RELEASE; status **NOT_RUN**.

Requirement: [R-GOV-04](15_REQUIREMENTS.md#r-gov-04). Tasks: [T048](07_IMPLEMENTATION_PLAN.md#t048), [T049](07_IMPLEMENTATION_PLAN.md#t049), [T050](07_IMPLEMENTATION_PLAN.md#t050). Spec: [25_RELEASE_CHECKLIST](25_RELEASE_CHECKLIST.md).

Check: Release handoff contains tested PPT, accessible demo video link, installable APK/prototype link and GitHub repo; portal cutoff/format and actual submission status are explicitly recorded.

Evidence: None.

## AT-005

**Native Android architecture and feasibility** — RELEASE; status **PASS**.

Requirement: [R-ARC-01](15_REQUIREMENTS.md#r-arc-01). Tasks: [T001](07_IMPLEMENTATION_PLAN.md#t001), [T003](07_IMPLEMENTATION_PLAN.md#t003). Spec: [03_TECHSPEC](03_TECHSPEC.md).

Check: Approved feasibility screen on a named real Android phone captures photo, persists Room data through restart and performs offline LiteRT inference; Kotlin/Compose/Room/WorkManager remain the collector implementation.

Evidence: [T003_ANDROID_FEASIBILITY.md](../docs/evidence/T003_ANDROID_FEASIBILITY.md). Note: Verified native Android Compose/Room/WorkManager/LiteRT architecture on named Android device; photo capture, local Room storage, and offline inference verified.

## AT-006

**Frozen API web database and storage stack** — RELEASE; status **NOT_RUN**.

Requirement: [R-ARC-02](15_REQUIREMENTS.md#r-arc-02). Tasks: [T001](07_IMPLEMENTATION_PLAN.md#t001), [T006](07_IMPLEMENTATION_PLAN.md#t006), [T008](07_IMPLEMENTATION_PLAN.md#t008). Spec: [03_TECHSPEC](03_TECHSPEC.md).

Check: Build and inspect API/web/database configuration: FastAPI, React/Vite, PostgreSQL/PostGIS, local volume and hosted private storage work through the documented contracts with dependency locks.

Evidence: None.

## AT-007

**Minimal profile and phone/PIN access** — RELEASE; status **PASS**.

Requirement: [R-AUTH-01](15_REQUIREMENTS.md#r-auth-01). Tasks: [T007](07_IMPLEMENTATION_PLAN.md#t007), [T017](07_IMPLEMENTATION_PLAN.md#t017). Spec: [16_API_CONTRACT](16_API_CONTRACT.md).

Check: Register/login with phone and PIN; store no plaintext PIN; profile uses ID/alias/language/general area, asks for no Aadhaar/PAN/bank details and shows recoverable auth errors.

Evidence: [T007_AUTH_AND_OWNERSHIP.md](../docs/evidence/T007_AUTH_AND_OWNERSHIP.md), [T017_COLLECTOR_ONBOARDING_AND_LOTS.md](../docs/evidence/T017_COLLECTOR_ONBOARDING_AND_LOTS.md). Note: Phone/PIN access verified across backend (T007) and Android Compose screens C01, C02, C15 (T017). Indian 10-digit mobile format, SHA-256 PIN hashing, 30s rate-limiting on failure, zero Aadhaar/bank PII collected, and isolated demo collector flow verified.

## AT-008

**Role and object authorization** — RELEASE; status **NOT_RUN**.

Requirement: [R-AUTH-02](15_REQUIREMENTS.md#r-auth-02). Tasks: [T007](07_IMPLEMENTATION_PLAN.md#t007), [T040](07_IMPLEMENTATION_PLAN.md#t040). Spec: [12_GUARDRAILS](12_GUARDRAILS.md).

Check: Collector A cannot read/mutate B's lots; recycler A cannot confirm B's facility handover; collector cannot become admin by editing payload; invalid/expired tokens are rejected server-side.

Evidence: [T040_SECURITY_AND_ABUSE_BOUNDARIES.md](../docs/evidence/T040_SECURITY_AND_ABUSE_BOUNDARIES.md). Note: Collector and recycler IDOR boundaries, cross-facility handover isolation, role escalation prevention, and invalid/expired token rejections verified in T040.

## AT-009

**Offline session and safe logout** — RELEASE; status **PASS**.

Requirement: [R-AUTH-03](15_REQUIREMENTS.md#r-auth-03). Tasks: [T007](07_IMPLEMENTATION_PLAN.md#t007), [T013](07_IMPLEMENTATION_PLAN.md#t013), [T015](07_IMPLEMENTATION_PLAN.md#t015), [T017](07_IMPLEMENTATION_PLAN.md#t017). Spec: [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md).

Check: After successful activation disconnect and restart: local profile/drafts remain usable; expired token pauses authenticated sync; reauth resumes same operations; logout cannot silently discard pending data or expose it to another user.

Evidence: [T007_AUTH_AND_OWNERSHIP.md](../docs/evidence/T007_AUTH_AND_OWNERSHIP.md), [T013_ROOM_REPOSITORIES_OUTBOX.md](../docs/evidence/T013_ROOM_REPOSITORIES_OUTBOX.md), [T015_ANDROID_SYNC_WORKER.md](../docs/evidence/T015_ANDROID_SYNC_WORKER.md), [T017_COLLECTOR_ONBOARDING_AND_LOTS.md](../docs/evidence/T017_COLLECTOR_ONBOARDING_AND_LOTS.md). Note: Offline session and safe logout verified across backend, Room, WorkManager, and Compose UI (T017). App operates offline; token expiration pauses sync gracefully; reauth resumes pending queue; safe logout revokes memory session without erasing local SQLite drafts or outbox operations.

## AT-010

**Isolated demo access without SMS** — RELEASE; status **NOT_RUN**.

Requirement: [R-AUTH-04](15_REQUIREMENTS.md#r-auth-04). Tasks: [T007](07_IMPLEMENTATION_PLAN.md#t007), [T040](07_IMPLEMENTATION_PLAN.md#t040), [T050](07_IMPLEMENTATION_PLAN.md#t050). Spec: [12_GUARDRAILS](12_GUARDRAILS.md).

Check: Bundled demo profile and demo OTP/bypass are explicitly labelled and isolated; public demo credentials cannot access non-demo users, verification controls or unrestricted admin actions.

Evidence: [T040_SECURITY_AND_ABUSE_BOUNDARIES.md](../docs/evidence/T040_SECURITY_AND_ABUSE_BOUNDARIES.md). Note: Demo access without SMS, DEMO_MODE toggle, explicit is_demo labelling, and live/demo boundary isolation verified in T040. Final packaging handoff in T050.

## AT-011

**Complete material taxonomy and aliases** — RELEASE; status **PASS**.

Requirement: [R-LOT-01](15_REQUIREMENTS.md#r-lot-01). Tasks: [T010](07_IMPLEMENTATION_PLAN.md#t010), [T017](07_IMPLEMENTATION_PLAN.md#t017). Spec: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Check: Create draft lots for CRT,LCD,PCB,cable,battery,motor/magnet,mixed plastics,mixed electronics and UNKNOWN; hi/mr/en local aliases resolve to stable IDs, not hardcoded price values.

Evidence: [T010_MATERIAL_TAXONOMY.md](../docs/evidence/T010_MATERIAL_TAXONOMY.md), [T017_COLLECTOR_ONBOARDING_AND_LOTS.md](../docs/evidence/T017_COLLECTOR_ONBOARDING_AND_LOTS.md). Note: Canonical 9-category scrap taxonomy (CRT, LCD, PCB, Cable, Battery, Motor, Plastics, Mixed, Other) verified across seed data (T010) and Compose screens C03, C05 (T017) with Hindi/Marathi/English aliases and hazardous regulatory routing.

## AT-012

**Camera image import compression and privacy** — RELEASE; status **PASS**.

Requirement: [R-LOT-02](15_REQUIREMENTS.md#r-lot-02). Tasks: [T008](07_IMPLEMENTATION_PLAN.md#t008), [T013](07_IMPLEMENTATION_PLAN.md#t013), [T017](07_IMPLEMENTATION_PLAN.md#t017). Spec: [06_SCHEMA](06_SCHEMA.md).

Check: Take/import a photo, deny camera permission, retry capture and restart; saved image remains linked, upload validates type/size and strips EXIF; no-photo draft is allowed but evidence completeness is explicit.

Evidence: [T008_PRIVATE_MEDIA_STORAGE.md](../docs/evidence/T008_PRIVATE_MEDIA_STORAGE.md), [T013_ROOM_REPOSITORIES_OUTBOX.md](../docs/evidence/T013_ROOM_REPOSITORIES_OUTBOX.md), [T017_COLLECTOR_ONBOARDING_AND_LOTS.md](../docs/evidence/T017_COLLECTOR_ONBOARDING_AND_LOTS.md). Note: CameraX image capture, permission denial rationale, gallery import fallback, and on-device photo compression (<500 KB, 1024px) verified in C04 (T017). Storage adapter upload and EXIF sanitization verified in T008; no-photo draft logging supported with explicit evidence flag.

## AT-013

**Weight condition description and validation** — RELEASE; status **PASS**.

Requirement: [R-LOT-03](15_REQUIREMENTS.md#r-lot-03). Tasks: [T016](07_IMPLEMENTATION_PLAN.md#t016), [T017](07_IMPLEMENTATION_PLAN.md#t017). Spec: [04_APPFLOW](04_APPFLOW.md).

Check: Save a draft then complete category/condition/description/positive finite weight; reject zero/negative/overflow values on submit; fractional kg round-trips as grams; suspicious large weight requires review without invented domain cap.

Evidence: [T016_LOT_LIFECYCLE_BACKEND.md](../docs/evidence/T016_LOT_LIFECYCLE_BACKEND.md), [T017_COLLECTOR_ONBOARDING_AND_LOTS.md](../docs/evidence/T017_COLLECTOR_ONBOARDING_AND_LOTS.md). Note: Draft lot creation and validation verified across backend (T016) and Android lot editor C05 (T017). Decimal KG weight input with high-contrast stepper converts to exact integer grams; condition chips, coarse location provenance, and AI suggestion confirm/change verified.

## AT-014

**Collection and handover location/time provenance** — RELEASE; status **PASS**.

Requirement: [R-LOT-04](15_REQUIREMENTS.md#r-lot-04). Tasks: [T016](07_IMPLEMENTATION_PLAN.md#t016), [T024](07_IMPLEMENTATION_PLAN.md#t024). Spec: [06_SCHEMA](06_SCHEMA.md).

Check: Record timestamps and GPS accuracy/capture age when permitted; denial uses labelled coarse/manual location or missing-data state; never fabricate coordinates or expose a home address in public records.

Evidence: [T016_LOT_LIFECYCLE_BACKEND.md](../docs/evidence/T016_LOT_LIFECYCLE_BACKEND.md), [T024_OFFLINE_QR_AND_COLLECTOR_RECEIPT.md](../docs/evidence/T024_OFFLINE_QR_AND_COLLECTOR_RECEIPT.md). Note: Backend GPS accuracy, capture age, coarse location fallback, and PII redaction verified in T016; mobile location capture, missing evidence handling, and privacy preservation in C10/C11 verified in T024.

## AT-015

**Durable draft lot lifecycle and cancellation** — RELEASE; status **PASS**.

Requirement: [R-LOT-05](15_REQUIREMENTS.md#r-lot-05). Tasks: [T013](07_IMPLEMENTATION_PLAN.md#t013), [T016](07_IMPLEMENTATION_PLAN.md#t016), [T017](07_IMPLEMENTATION_PLAN.md#t017). Spec: [04_APPFLOW](04_APPFLOW.md).

Check: Create/edit/reopen/cancel a lot with stable UUID and legal transitions; restart preserves drafts; attempts to mutate confirmed historical terms or jump CLOSED→COLLECTED fail and are auditable.

Evidence: [T013_ROOM_REPOSITORIES_OUTBOX.md](../docs/evidence/T013_ROOM_REPOSITORIES_OUTBOX.md), [T016_LOT_LIFECYCLE_BACKEND.md](../docs/evidence/T016_LOT_LIFECYCLE_BACKEND.md), [T017_COLLECTOR_ONBOARDING_AND_LOTS.md](../docs/evidence/T017_COLLECTOR_ONBOARDING_AND_LOTS.md). Note: Durable lot lifecycle verified across Room SQLite (T013), FastAPI backend (T016), and Compose UI C03, C05, C14 (T017). Atomic ACID transaction commits LotEntity (SAVED_LOCAL_ONLY), tamper-evident DomainEventEntity with SHA-256 hash chaining, and queued OutboxOperationEntity.

## AT-016

**Price observations and in-app entry** — RELEASE; status **PASS**.

Requirement: [R-PRICE-01](15_REQUIREMENTS.md#r-price-01). Tasks: [T011](07_IMPLEMENTATION_PLAN.md#t011), [T020](07_IMPLEMENTATION_PLAN.md#t020). Spec: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Check: Enter an observation with material/subcategory, region, date, unit, price kind and source; edit via revision, moderate and export it; unknown dates or unsupported conversions are quarantined.

Evidence: [T011_PRICE_OBSERVATION_PIPELINE.md](../docs/evidence/T011_PRICE_OBSERVATION_PIPELINE.md), [T020_COLLECTOR_PRICE_AND_RECYCLER_VIEWS.md](../docs/evidence/T020_COLLECTOR_PRICE_AND_RECYCLER_VIEWS.md). Note: Price observation entry verified across backend ingestion/quarantine (T011) and collector field observation form in C06 (T020). Atomic outbox enqueue and domain event SHA-256 hash chaining verified.

## AT-017

**Indicative weighted range and lot valuation** — RELEASE; status **PASS**.

Requirement: [R-PRICE-02](15_REQUIREMENTS.md#r-price-02). Tasks: [T018](07_IMPLEMENTATION_PLAN.md#t018), [T020](07_IMPLEMENTATION_PLAN.md#t020). Spec: [03_TECHSPEC](03_TECHSPEC.md).

Check: A known comparable observation fixture yields specified weighted median/Q1/Q3 and estimate bounds in API and Android; weight changes recompute estimate; screen labels result indicative and retains snapshot/version.

Evidence: [T018_PRICE_STATISTICS_VALUATION.md](../docs/evidence/T018_PRICE_STATISTICS_VALUATION.md), [T020_COLLECTOR_PRICE_AND_RECYCLER_VIEWS.md](../docs/evidence/T020_COLLECTOR_PRICE_AND_RECYCLER_VIEWS.md). Note: Indicative weighted range and lot valuation verified with exact parity across Python API, Room local calculator, and Compose screens C06 & C07. Weight adjustments and condition deductions update bounds reactively with snapshot retention.

## AT-018

**Source confidence freshness and empty prices** — RELEASE; status **PASS**.

Requirement: [R-PRICE-03](15_REQUIREMENTS.md#r-price-03). Tasks: [T018](07_IMPLEMENTATION_PLAN.md#t018), [T020](07_IMPLEMENTATION_PLAN.md#t020). Spec: [03_TECHSPEC](03_TECHSPEC.md).

Check: Recent/few/stale/no-data fixtures show correct count, sources, timestamp, confidence and reason; no-data is INSUFFICIENT, never zero or a hidden synthetic fallback.

Evidence: [T018_PRICE_STATISTICS_VALUATION.md](../docs/evidence/T018_PRICE_STATISTICS_VALUATION.md), [T020_COLLECTOR_PRICE_AND_RECYCLER_VIEWS.md](../docs/evidence/T020_COLLECTOR_PRICE_AND_RECYCLER_VIEWS.md). Note: Confidence tiers (HIGH, MEDIUM, LOW, INSUFFICIENT_DATA) and reason codes verified across statistics engine and C06/C07 UI. Insufficient data surfaces transparently without zero or synthetic fallbacks.

## AT-019

**History trends and actual offer comparison** — RELEASE; status **PASS**.

Requirement: [R-PRICE-04](15_REQUIREMENTS.md#r-price-04). Tasks: [T018](07_IMPLEMENTATION_PLAN.md#t018), [T020](07_IMPLEMENTATION_PLAN.md#t020), [T021](07_IMPLEMENTATION_PLAN.md#t021). Spec: [03_TECHSPEC](03_TECHSPEC.md).

Check: View dated trend buckets and multiple offers in consistent units/regions; missing history displays a gap, no fabricated points; expired/noncomparable rates are labelled and do not become an agreed price.

Evidence: [T018_PRICE_STATISTICS_VALUATION.md](../docs/evidence/T018_PRICE_STATISTICS_VALUATION.md), [T020_COLLECTOR_PRICE_AND_RECYCLER_VIEWS.md](../docs/evidence/T020_COLLECTOR_PRICE_AND_RECYCLER_VIEWS.md), [T021_RECYCLER_OFFER_WORKFLOWS.md](../docs/evidence/T021_RECYCLER_OFFER_WORKFLOWS.md). Note: Dated 30-day trend series with honest gap preservation, price benchmark cards, and offer expiration checks verified across backend and C06 price board.

## AT-020

**Quote anomaly review** — RELEASE; status **PASS**.

Requirement: [R-PRICE-05](15_REQUIREMENTS.md#r-price-05). Tasks: [T028](07_IMPLEMENTATION_PLAN.md#t028), [T030](07_IMPLEMENTATION_PLAN.md#t030). Spec: [03_TECHSPEC](03_TECHSPEC.md).

Check: Known low/high quotes trigger configured review reasons only when enough comparable data exists; alert says review, does not accuse fraud or block collector choice without a separate eligibility violation.

Evidence: [T028_DATA_QUALITY_AND_ANOMALIES.md](../docs/evidence/T028_DATA_QUALITY_AND_ANOMALIES.md), [T030_ADMIN_DASHBOARD.md](../docs/evidence/T030_ADMIN_DASHBOARD.md). Note: Domain outlier evaluation using 1.5x IQR bounds without fraud accusation or collector choice blocking verified in T028; admin quote moderation UI and triage workflows verified in T030.

## AT-021

**Source-backed Delhi-NCR Maharashtra directory** — RELEASE; status **PASS**.

Requirement: [R-REC-01](15_REQUIREMENTS.md#r-rec-01). Tasks: [T012](07_IMPLEMENTATION_PLAN.md#t012). Spec: [22_REGULATORY_SAFETY](22_REGULATORY_SAFETY.md).

Check: Import CPCB plus DPCC and MPCB records with facility role/source document/page/date/registration and lineage; do not relabel a collection point as a recycler or claim that a list import creates a partnership.

Evidence: [T012_FACILITY_DIRECTORY.md](../docs/evidence/T012_FACILITY_DIRECTORY.md). Note: Verified CPCB, DPCC, MPCB, and NDMC source-backed records, facility role preservation, disclaimers, and that collection points are never relabeled as recyclers.

## AT-022

**Verification levels and expiry** — RELEASE; status **NOT_RUN**.

Requirement: [R-REC-02](15_REQUIREMENTS.md#r-rec-02). Tasks: [T012](07_IMPLEMENTATION_PLAN.md#t012), [T019](07_IMPLEMENTATION_PLAN.md#t019), [T029](07_IMPLEMENTATION_PLAN.md#t029). Spec: [22_REGULATORY_SAFETY](22_REGULATORY_SAFETY.md).

Check: L0/L1/L2 never become verified formal destinations; stale/expired/revoked/unproven route authorization removes strong badge and matching eligibility even if original source was official.

Evidence: [T012_FACILITY_DIRECTORY.md](../docs/evidence/T012_FACILITY_DIRECTORY.md), [T019_RECYCLER_MATCHING_MAPS.md](../docs/evidence/T019_RECYCLER_MATCHING_MAPS.md). Note: L0/L1/L2 facilities excluded from formal destination matches (VERIFICATION_INSUFFICIENT); L3/L4 with active valid status match with is_formal_destination=True. Awaiting admin quality dashboard verification in T029.

## AT-023

**Facility materials rates pickup and service area** — RELEASE; status **NOT_RUN**.

Requirement: [R-REC-03](15_REQUIREMENTS.md#r-rec-03). Tasks: [T012](07_IMPLEMENTATION_PLAN.md#t012), [T021](07_IMPLEMENTATION_PLAN.md#t021), [T022](07_IMPLEMENTATION_PLAN.md#t022). Spec: [06_SCHEMA](06_SCHEMA.md).

Check: Facility user updates rates/availability/service area with provenance while authorization fields stay admin-controlled; unknown operational data stays unknown; acceptance/minimum-weight terms are visible.

Evidence: [T012_FACILITY_DIRECTORY.md](../docs/evidence/T012_FACILITY_DIRECTORY.md), [T021_RECYCLER_OFFER_WORKFLOWS.md](../docs/evidence/T021_RECYCLER_OFFER_WORKFLOWS.md). Note: Facility user operational profile updates (rates, availability, service area, materials) with provenance, strict admin-controlled authorizations (tampering blocked with HTTP 403), and unknown operational data preservation verified in T021. Awaiting UI in T022.

## AT-024

**Route-aware eligibility** — RELEASE; status **PASS**.

Requirement: [R-REC-04](15_REQUIREMENTS.md#r-rec-04). Tasks: [T019](07_IMPLEMENTATION_PLAN.md#t019), [T023](07_IMPLEMENTATION_PLAN.md#t023). Spec: [22_REGULATORY_SAFETY](22_REGULATORY_SAFETY.md).

Check: Battery lot cannot match a facility evidenced only for e-waste; incompatible material, unverified current registration or unsupported service/weight constraints exclude before ranking and before confirmation.

Evidence: [T019_RECYCLER_MATCHING_MAPS.md](../docs/evidence/T019_RECYCLER_MATCHING_MAPS.md), [T023_HANDOVER_CONFIRMATIONS.md](../docs/evidence/T023_HANDOVER_CONFIRMATIONS.md). Note: Route-aware eligibility and battery isolation invariant verified: battery lot matches Eco-Battery while general e-waste (Greentech) is excluded with ROUTE_INCOMPATIBLE. Material, registration, and weight constraints exclude before ranking and before confirmation in T019 and T023.

## AT-025

**Explainable ranking with geography** — RELEASE; status **PASS**.

Requirement: [R-REC-05](15_REQUIREMENTS.md#r-rec-05). Tasks: [T019](07_IMPLEMENTATION_PLAN.md#t019), [T020](07_IMPLEMENTATION_PLAN.md#t020). Spec: [03_TECHSPEC](03_TECHSPEC.md).

Check: Run fixed candidates: deterministic score and tie-break, PostGIS distance online, cached local parity within tolerance; expose contributions and unknowns; never invent pickup, price or reliability.

Evidence: [T019_RECYCLER_MATCHING_MAPS.md](../docs/evidence/T019_RECYCLER_MATCHING_MAPS.md), [T020_COLLECTOR_PRICE_AND_RECYCLER_VIEWS.md](../docs/evidence/T020_COLLECTOR_PRICE_AND_RECYCLER_VIEWS.md). Note: Deterministic 5-factor scoring (distance 30%, rate 30%, pickup 20%, availability 15%, reliability 5%), stable tie-breaking, and transparent factor explanations verified in Kotlin MatchingEngine and C07/C08/C09 recycler views.

## AT-026

**Offline list online map and no-match path** — RELEASE; status **PASS**.

Requirement: [R-REC-06](15_REQUIREMENTS.md#r-rec-06). Tasks: [T019](07_IMPLEMENTATION_PLAN.md#t019), [T020](07_IMPLEMENTATION_PLAN.md#t020). Spec: [05_DESIGN_STITCH](05_DESIGN_STITCH.md).

Check: With network/maps/GPS unavailable directory list works with cached age and distance when possible; no-match can save/widen geography, never switch battery route; online MapLibre includes attribution and permitted tiles.

Evidence: [T019_RECYCLER_MATCHING_MAPS.md](../docs/evidence/T019_RECYCLER_MATCHING_MAPS.md), [T020_COLLECTOR_PRICE_AND_RECYCLER_VIEWS.md](../docs/evidence/T020_COLLECTOR_PRICE_AND_RECYCLER_VIEWS.md). Note: Empty-state matching preserves transparent exclusion counts without route switching. Offline list fallback and MapLibre geo markers verified in C08 directory.

## AT-027

**Recycler inbound offer accept reject workflow** — RELEASE; status **NOT_RUN**.

Requirement: [R-OFFER-01](15_REQUIREMENTS.md#r-offer-01). Tasks: [T021](07_IMPLEMENTATION_PLAN.md#t021), [T022](07_IMPLEMENTATION_PLAN.md#t022). Spec: [04_APPFLOW](04_APPFLOW.md).

Check: Collector submits lot, linked recycler sees evidence and quotes/accepts/rejects; collector selects one live offer; rejected/expired requests preserve history and can return to another compatible match.

Evidence: [T021_RECYCLER_OFFER_WORKFLOWS.md](../docs/evidence/T021_RECYCLER_OFFER_WORKFLOWS.md). Note: Directed lot requests with battery isolation route guard, recycler incoming queue with location privacy (coarse area only), offer quotes, rejection with reason and collector rematching to LISTED verified in T021. Awaiting recycler console UI in T022.

## AT-028

**Immutable agreed terms and offer races** — RELEASE; status **PASS**.

Requirement: [R-OFFER-02](15_REQUIREMENTS.md#r-offer-02). Tasks: [T021](07_IMPLEMENTATION_PLAN.md#t021), [T023](07_IMPLEMENTATION_PLAN.md#t023). Spec: [04_APPFLOW](04_APPFLOW.md).

Check: Two simultaneous acceptances leave one active agreement; cached expired offer cannot silently bind; later price-board refresh does not modify accepted terms; material/weight/price changes require explicit acknowledgement.

Evidence: [T021_RECYCLER_OFFER_WORKFLOWS.md](../docs/evidence/T021_RECYCLER_OFFER_WORKFLOWS.md), [T023_HANDOVER_CONFIRMATIONS.md](../docs/evidence/T023_HANDOVER_CONFIRMATIONS.md). Note: Collector offer acceptance creating atomic Transaction and initial TermsRevision, single-active-agreement invariant under race conditions, expired offer rejection, terms hash mismatch guard, price-board independence, and explicit collector acknowledgement of changed terms verified in T021 and T023.

## AT-029

**Offline pending handover evidence** — RELEASE; status **PASS**.

Requirement: [R-HAND-01](15_REQUIREMENTS.md#r-hand-01). Tasks: [T023](07_IMPLEMENTATION_PLAN.md#t023), [T024](07_IMPLEMENTATION_PLAN.md#t024). Spec: [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md).

Check: In airplane mode create UUID proposal with photo references, grams, location quality, time, parties/terms and hash; restart shows PENDING_CONFIRMATION and sync pending, never recycler-confirmed.

Evidence: [T023_HANDOVER_CONFIRMATIONS.md](../docs/evidence/T023_HANDOVER_CONFIRMATIONS.md), [T024_OFFLINE_QR_AND_COLLECTOR_RECEIPT.md](../docs/evidence/T024_OFFLINE_QR_AND_COLLECTOR_RECEIPT.md). Note: Backend proposal validation and canonical hash in T023; offline UUID proposal creation with photo references, grams, location quality, timestamp, terms, and SHA-256 seal badge with PENDING_CONFIRMATION status verified in T024 via HandoverAndReceiptTest.

## AT-030

**Two-device recycler confirmation** — RELEASE; status **NOT_RUN**.

Requirement: [R-HAND-02](15_REQUIREMENTS.md#r-hand-02). Tasks: [T025](07_IMPLEMENTATION_PLAN.md#t025), [T044](07_IMPLEMENTATION_PLAN.md#t044). Spec: [04_APPFLOW](04_APPFLOW.md).

Check: Borrowed second Android browser scans collector QR over HTTPS, identifies the correct facility/lot, submits authorized confirmation and collector sees it after pull; unsynced reference explains waiting and supports retry/manual reference.

Evidence: None.

## AT-031

**Canonical hash and append-only event chain** — RELEASE; status **NOT_RUN**.

Requirement: [R-HAND-03](15_REQUIREMENTS.md#r-hand-03). Tasks: [T023](07_IMPLEMENTATION_PLAN.md#t023), [T024](07_IMPLEMENTATION_PLAN.md#t024), [T043](07_IMPLEMENTATION_PLAN.md#t043). Spec: [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md).

Check: Same frozen JSON fixture hashes identically in Python/Kotlin/web; one altered byte invalidates expected digest; original proposal and confirmation events remain linked and unchanged; UI never describes bare SHA-256 as a signature.

Evidence: [T023_HANDOVER_CONFIRMATIONS.md](../docs/evidence/T023_HANDOVER_CONFIRMATIONS.md), [T024_OFFLINE_QR_AND_COLLECTOR_RECEIPT.md](../docs/evidence/T024_OFFLINE_QR_AND_COLLECTOR_RECEIPT.md). Note: Canonical hash matches frozen fixture handover_fixture.json in both Python (T023) and Kotlin (T024); tamper rejection, key ordering, and SHA-256 seal verified. Awaiting integration test runner in T043.

## AT-032

**Public verification and privacy** — RELEASE; status **NOT_RUN**.

Requirement: [R-HAND-04](15_REQUIREMENTS.md#r-hand-04). Tasks: [T023](07_IMPLEMENTATION_PLAN.md#t023), [T025](07_IMPLEMENTATION_PLAN.md#t025), [T040](07_IMPLEMENTATION_PLAN.md#t040). Spec: [16_API_CONTRACT](16_API_CONTRACT.md).

Check: An unguessable receipt link shows current redacted status and record/hash comparison; public visitor cannot fetch phone/GPS/photos/payment details; QR possession alone cannot authorize confirmation.

Evidence: [T023_HANDOVER_CONFIRMATIONS.md](../docs/evidence/T023_HANDOVER_CONFIRMATIONS.md), [T025_SECOND_DEVICE_CONFIRMATION.md](../docs/evidence/T025_SECOND_DEVICE_CONFIRMATION.md), [T024_OFFLINE_QR_AND_COLLECTOR_RECEIPT.md](../docs/evidence/T024_OFFLINE_QR_AND_COLLECTOR_RECEIPT.md), [T040_SECURITY_AND_ABUSE_BOUNDARIES.md](../docs/evidence/T040_SECURITY_AND_ABUSE_BOUNDARIES.md). Note: Local integration verifies authenticated server lookup and QR hash comparison without PII. Full deployed cross-surface two-device verification remains NOT_RUN pending the physical retest.

## AT-033

**Weight grade price disagreement** — RELEASE; status **NOT_RUN**.

Requirement: [R-HAND-05](15_REQUIREMENTS.md#r-hand-05). Tasks: [T023](07_IMPLEMENTATION_PLAN.md#t023), [T025](07_IMPLEMENTATION_PLAN.md#t025), [T027](07_IMPLEMENTATION_PLAN.md#t027), [T028](07_IMPLEMENTATION_PLAN.md#t028). Spec: [04_APPFLOW](04_APPFLOW.md).

Check: Different measured weight/grade/price retains estimate and AI suggestion, sets pending acknowledgement/review and variance reason; neither party overwrites original facts; collector agreement or documented dispute is recorded.

Evidence: [T023_HANDOVER_CONFIRMATIONS.md](../docs/evidence/T023_HANDOVER_CONFIRMATIONS.md), [T028_DATA_QUALITY_AND_ANOMALIES.md](../docs/evidence/T028_DATA_QUALITY_AND_ANOMALIES.md), [T027_COLLECTOR_LEDGER_AND_PAYMENTS.md](../docs/evidence/T027_COLLECTOR_LEDGER_AND_PAYMENTS.md). Note: Server-backed demo confirmation is integration-tested, but the complete deployed second-device discrepancy flow remains NOT_RUN pending the physical retest.

## AT-034

**Receipt PDF passport and procurement exports** — RELEASE; status **NOT_RUN**.

Requirement: [R-HAND-06](15_REQUIREMENTS.md#r-hand-06). Tasks: [T024](07_IMPLEMENTATION_PLAN.md#t024), [T025](07_IMPLEMENTATION_PLAN.md#t025), [T031](07_IMPLEMENTATION_PLAN.md#t031). Spec: [16_API_CONTRACT](16_API_CONTRACT.md).

Check: Export offline pending PDF and server confirmed PDF/CSV; identifiers/status/hash/provenance agree with timeline; record is called Digital Handover Record and includes non-EPR boundary, never an official manifest claim.

Evidence: [T024_OFFLINE_QR_AND_COLLECTOR_RECEIPT.md](../docs/evidence/T024_OFFLINE_QR_AND_COLLECTOR_RECEIPT.md), [T031_DATASET_EXPORTS.md](../docs/evidence/T031_DATASET_EXPORTS.md). Note: The server now permits authenticated recycler confirmation only after lookup/hash verification; the deployed receipt transition has not yet been physically retested, so full acceptance remains NOT_RUN.

## AT-035

**Cash optional UPI and payment recording** — RELEASE; status **PASS**.

Requirement: [R-PAY-01](15_REQUIREMENTS.md#r-pay-01). Tasks: [T026](07_IMPLEMENTATION_PLAN.md#t026), [T027](07_IMPLEMENTATION_PLAN.md#t027). Spec: [04_APPFLOW](04_APPFLOW.md).

Check: Record cash without bank account/gateway; optional UPI/other records an assertion and reference, not transfer; both sides see actor/time/acknowledgement and can dispute.

Evidence: [T026_PAYMENTS_AND_EARNINGS.md](../docs/evidence/T026_PAYMENTS_AND_EARNINGS.md), [T027_COLLECTOR_LEDGER_AND_PAYMENTS.md](../docs/evidence/T027_COLLECTOR_LEDGER_AND_PAYMENTS.md). Note: Cash-first assertions without bank gateway, optional UPI reference recording, counterparty acknowledgement, self-acknowledgement prevention, and disputes verified in backend (T026) and mobile Compose screens C12, C13 (T027).

## AT-036

**Partial dues reversals and closure** — RELEASE; status **PASS**.

Requirement: [R-PAY-02](15_REQUIREMENTS.md#r-pay-02). Tasks: [T026](07_IMPLEMENTATION_PLAN.md#t026), [T027](07_IMPLEMENTATION_PLAN.md#t027). Spec: [06_SCHEMA](06_SCHEMA.md).

Check: Two partial receipts sum once, duplicate operation does not increase paid total, overpayment is reviewed, reversal links original; RECEIVED with pending dues cannot become CLOSED; disagreement remains visible.

Evidence: [T026_PAYMENTS_AND_EARNINGS.md](../docs/evidence/T026_PAYMENTS_AND_EARNINGS.md), [T027_COLLECTOR_LEDGER_AND_PAYMENTS.md](../docs/evidence/T027_COLLECTOR_LEDGER_AND_PAYMENTS.md). Note: Partial payment aggregation without double counting, duplicate-safe idempotency, append-only reversals linking original records without deletion, and strict closure invariants verified across T026 and T027.

## AT-037

**Collector earnings and transaction history** — RELEASE; status **PASS**.

Requirement: [R-PAY-03](15_REQUIREMENTS.md#r-pay-03). Tasks: [T026](07_IMPLEMENTATION_PLAN.md#t026), [T027](07_IMPLEMENTATION_PLAN.md#t027). Spec: [04_APPFLOW](04_APPFLOW.md).

Check: Filter history/month and reconcile gross, acknowledged paid, asserted pending and remaining dues against transactions; offline view shows freshness; no demo earnings or estimates contaminate real settled totals.

Evidence: [T026_PAYMENTS_AND_EARNINGS.md](../docs/evidence/T026_PAYMENTS_AND_EARNINGS.md), [T027_COLLECTOR_LEDGER_AND_PAYMENTS.md](../docs/evidence/T027_COLLECTOR_LEDGER_AND_PAYMENTS.md). Note: Filter history/month and reconcile gross, acknowledged paid, asserted pending, and remaining dues against transactions; offline view freshness; demo partition isolation verified in T026 and T027.

## AT-038

**Offline reference and local core journey** — RELEASE; status **PASS**.

Requirement: [R-OFF-01](15_REQUIREMENTS.md#r-off-01). Tasks: [T009](07_IMPLEMENTATION_PLAN.md#t009), [T013](07_IMPLEMENTATION_PLAN.md#t013), [T017](07_IMPLEMENTATION_PLAN.md#t017), [T020](07_IMPLEMENTATION_PLAN.md#t020). Spec: [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md).

Check: After bootstrap, airplane mode still allows material/safety/price/directory/history reads and photo/category/weight/lot/pending handover writes; fresh install offers clearly labelled demo reference or activation requirement, never an empty misleading success state.

Evidence: [T017_COLLECTOR_ONBOARDING_AND_LOTS.md](../docs/evidence/T017_COLLECTOR_ONBOARDING_AND_LOTS.md), [T020_COLLECTOR_PRICE_AND_RECYCLER_VIEWS.md](../docs/evidence/T020_COLLECTOR_PRICE_AND_RECYCLER_VIEWS.md). Note: Offline reference and local core journey verified across onboarding, lot drafting, price discovery, offline offer queuing, and outbox persistence in C01-C09, C14, C15.

## AT-039

**Atomic durable outbox and image survival** — RELEASE; status **NOT_RUN**.

Requirement: [R-OFF-02](15_REQUIREMENTS.md#r-off-02). Tasks: [T013](07_IMPLEMENTATION_PLAN.md#t013), [T043](07_IMPLEMENTATION_PLAN.md#t043). Spec: [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md).

Check: Kill process during/after local save and media staging; either fully recover object+event+outbox+file or report unsaved failure; never drop a pending record through migration, cleanup or storage pressure.

Evidence: None.

## AT-040

**Idempotency and partial batch acknowledgement** — RELEASE; status **NOT_RUN**.

Requirement: [R-OFF-03](15_REQUIREMENTS.md#r-off-03). Tasks: [T014](07_IMPLEMENTATION_PLAN.md#t014), [T043](07_IMPLEMENTATION_PLAN.md#t043). Spec: [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md).

Check: Resend an operation after server commit/ACK loss and in mixed-success batches; each accepted effect occurs once, different payload with reused ID conflicts, successful siblings stay acknowledged.

Evidence: [T014_SERVER_SYNC_PROTOCOL.md](../docs/evidence/T014_SERVER_SYNC_PROTOCOL.md). Note: Backend protocol verified in T014 (idempotent replay, conflict detection, mixed-success batches). Awaiting cross-task mobile integration in T043.

## AT-041

**Versioned conflicts and dependency order** — RELEASE; status **NOT_RUN**.

Requirement: [R-OFF-04](15_REQUIREMENTS.md#r-off-04). Tasks: [T014](07_IMPLEMENTATION_PLAN.md#t014), [T015](07_IMPLEMENTATION_PLAN.md#t015), [T043](07_IMPLEMENTATION_PLAN.md#t043). Spec: [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md).

Check: Out-of-order lot/media/handover operations wait on parents; concurrent changes return current server version without erasing local proposal; reference tombstones update caches while historical receipts retain snapshots.

Evidence: [T014_SERVER_SYNC_PROTOCOL.md](../docs/evidence/T014_SERVER_SYNC_PROTOCOL.md), [T015_ANDROID_SYNC_WORKER.md](../docs/evidence/T015_ANDROID_SYNC_WORKER.md). Note: Server batch push protocol and Android SyncEngine delta transaction commit with 409 conflict handling verified in T014 and T015. Awaiting integration in T043.

## AT-042

**WorkManager retries foreground sync and auth pause** — RELEASE; status **NOT_RUN**.

Requirement: [R-OFF-05](15_REQUIREMENTS.md#r-off-05). Tasks: [T015](07_IMPLEMENTATION_PLAN.md#t015), [T017](07_IMPLEMENTATION_PLAN.md#t017), [T043](07_IMPLEMENTATION_PLAN.md#t043). Spec: [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md).

Check: With intermittent network/reboot/background restriction sync resumes durably or via manual button; 401 pauses for auth, 409 review, 422 repair, 429 backoff and 5xx retry without busy loop or lost records.

Evidence: [T015_ANDROID_SYNC_WORKER.md](../docs/evidence/T015_ANDROID_SYNC_WORKER.md), [T017_COLLECTOR_ONBOARDING_AND_LOTS.md](../docs/evidence/T017_COLLECTOR_ONBOARDING_AND_LOTS.md). Note: WorkManager CoroutineWorker with backoff and retry in T015 connected to C14 Sync Centre UI in T017. Awaiting full fault acceptance in T043.

## AT-043

**Visible queue and recoverable failure states** — RELEASE; status **NOT_RUN**.

Requirement: [R-OFF-06](15_REQUIREMENTS.md#r-off-06). Tasks: [T015](07_IMPLEMENTATION_PLAN.md#t015), [T017](07_IMPLEMENTATION_PLAN.md#t017), [T043](07_IMPLEMENTATION_PLAN.md#t043). Spec: [05_DESIGN_STITCH](05_DESIGN_STITCH.md).

Check: Collector can distinguish local/sending/synced/needs-login/conflict/rejected, inspect queue count/last sync, retry safely and retain a support reference; no generic green success on HTTP failure.

Evidence: [T015_ANDROID_SYNC_WORKER.md](../docs/evidence/T015_ANDROID_SYNC_WORKER.md), [T017_COLLECTOR_ONBOARDING_AND_LOTS.md](../docs/evidence/T017_COLLECTOR_ONBOARDING_AND_LOTS.md). Note: Outbox state transitions verified in T015 and movement board visual breakdown with itemized retries implemented in C14 (T017). Awaiting full fault acceptance testing in T043.

## AT-044

**Licensed suitable public dataset only** — RELEASE; status **NOT_RUN**.

Requirement: [R-ML-01](15_REQUIREMENTS.md#r-ml-01). Tasks: [T032](07_IMPLEMENTATION_PLAN.md#t032), [T047](07_IMPLEMENTATION_PLAN.md#t047). Spec: [19_AI_ML](19_AI_ML.md).

Check: Every training image has permitted-use evidence, source/license/hash/class/object-group/split; no fabricated field images; class coverage report exposes generic datasets that do not cover actual e-waste taxonomy.

Evidence: [T032_LICENSED_IMAGE_DATASET.md](../docs/evidence/T032_LICENSED_IMAGE_DATASET.md). Note: Verified 172 curated public images across 12 defensible e-waste classes from 4 verified sources (Wikimedia Commons, Stanford TrashNet, Open Images V7, Mendeley) under CC BY-SA 4.0, MIT, and CC BY 4.0 in T032. Exact SHA-256 hashes, object-group splits with zero leakage, no fabricated field photos, and explicit coverage report documenting 9 manual fallbacks. Awaiting integration verification in T047.

## AT-045

**Reproducible leakage-free training and evaluation** — RELEASE; status **NOT_RUN**.

Requirement: [R-ML-02](15_REQUIREMENTS.md#r-ml-02). Tasks: [T033](07_IMPLEMENTATION_PLAN.md#t033), [T047](07_IMPLEMENTATION_PLAN.md#t047). Spec: [19_AI_ML](19_AI_ML.md).

Check: Train from saved configuration with object-group splits and training-only augmentation; report actual untouched-test macro/per-class F1, confusion matrix, counts/limits, calibration threshold and quantization parity.

Evidence: [T033_ON_DEVICE_CLASSIFIER.md](../docs/evidence/T033_ON_DEVICE_CLASSIFIER.md). Note: Trained MobileNetV3-Small from saved configuration with leakage-free object splits, training-only augmentation, untouched-test evaluation metrics, confusion matrix, advisory threshold calibration, quantized LiteRT export, and numerical parity verified in T033. Awaiting evidence freeze in T047.

## AT-046

**Bundled offline advisory classifier** — RELEASE; status **NOT_RUN**.

Requirement: [R-ML-03](15_REQUIREMENTS.md#r-ml-03). Tasks: [T034](07_IMPLEMENTATION_PLAN.md#t034), [T044](07_IMPLEMENTATION_PLAN.md#t044). Spec: [19_AI_ML](19_AI_ML.md).

Check: Real SahiTol model predicts offline on phone with versioned preprocessing; user confirms/changes; low-confidence/OOD/corrupt-model fallback stays usable; no automatic certification, pricing or route determination.

Evidence: [T034_CLASSIFIER_ANDROID_FLOW.md](../docs/evidence/T034_CLASSIFIER_ANDROID_FLOW.md). Note: Bundled offline advisory LiteRT model predicts on phone with versioned preprocessing and checksum verification; advisory threshold (0.65) routes low-confidence/OOD inputs to explicit abstention; corrupt model and OOM fallback safely recoverable without crash (T034); awaiting Phase 6 evaluation in T044.

## AT-047

**Correction data and measured model constraints** — RELEASE; status **NOT_RUN**.

Requirement: [R-ML-04](15_REQUIREMENTS.md#r-ml-04). Tasks: [T034](07_IMPLEMENTATION_PLAN.md#t034), [T045](07_IMPLEMENTATION_PLAN.md#t045), [T047](07_IMPLEMENTATION_PLAN.md#t047). Spec: [19_AI_ML](19_AI_ML.md).

Check: Persist suggestion/confidence/model version separately from human label; report correction/abstention denominators and inference/APK/memory on actual device; no training reuse without documented rights/purpose.

Evidence: [T034_CLASSIFIER_ANDROID_FLOW.md](../docs/evidence/T034_CLASSIFIER_ANDROID_FLOW.md). Note: Separate persistence of suggestion, confidence, and model version from human label implemented in LotEntity, CreateLotParams, and LOT_CREATED domain event and outbox payloads in T034; awaiting Phase 6 reporting in T045, T047.

## AT-048

**Contextual pictorial safety guidance** — RELEASE; status **PASS**.

Requirement: [R-SAFE-01](15_REQUIREMENTS.md#r-safe-01). Tasks: [T035](07_IMPLEMENTATION_PLAN.md#t035), [T039](07_IMPLEMENTATION_PLAN.md#t039). Spec: [22_REGULATORY_SAFETY](22_REGULATORY_SAFETY.md).

Check: PCB/cable/CRT/battery selection opens appropriate short pictorial warning in both languages offline; content is sourced/versioned and avoids instructions for unsafe processing.

Evidence: [T035_CONTEXTUAL_SAFETY_CONTENT.md](../docs/evidence/T035_CONTEXTUAL_SAFETY_CONTENT.md), [T039_ECONOMICS_AND_SAFETY_VIEWS.md](../docs/evidence/T039_ECONOMICS_AND_SAFETY_VIEWS.md). Note: Source-backed trilingual safety cards, non-instructional hazard copy, audio scripts, and Stitch pictogram briefs implemented in T035; Android offline Compose safety screen C17 and C05 contextual safety alert banner verified in T039 with tap-to-hear offline audio and non-instructional invariant checks passing cleanly in SafetyContentAndHubTest.

## AT-049

**Complete Hindi Marathi and English fallback** — RELEASE; status **NOT_RUN**.

Requirement: [R-LANG-01](15_REQUIREMENTS.md#r-lang-01). Tasks: [T036](07_IMPLEMENTATION_PLAN.md#t036), [T046](07_IMPLEMENTATION_PLAN.md#t046). Spec: [14_TRANSLATION_AUDIO_AUDIT](14_TRANSLATION_AUDIO_AUDIT.md).

Check: All collector critical keys, labels, validation/denial/conflict/payment states and dynamic material terms work in hi/mr; language persists; unavailable translation is reported in audit, not hidden by English fallback.

Evidence: [T036_LANGUAGE_RESOURCES_AND_ACCESSIBILITY.md](../docs/evidence/T036_LANGUAGE_RESOURCES_AND_ACCESSIBILITY.md). Note: Language parity across hi, mr, en verified with 0 missing keys; missing translations recorded in audit log; colloquial material aliases in place; awaiting audio clip integration in T037 and end-to-end device audit in T046.

## AT-050

**Offline audio prompts and spoken prices** — RELEASE; status **NOT_RUN**.

Requirement: [R-LANG-02](15_REQUIREMENTS.md#r-lang-02). Tasks: [T037](07_IMPLEMENTATION_PLAN.md#t037), [T046](07_IMPLEMENTATION_PLAN.md#t046). Spec: [14_TRANSLATION_AUDIO_AUDIT](14_TRANSLATION_AUDIO_AUDIT.md).

Check: In airplane mode tap Hindi and Marathi audio for changing price ranges, decimals, rupees/paise/per-kg and safety/pending/success; spoken value exactly matches visible value; asset licences and missing-clip behavior are recorded.

Evidence: [T037_OFFLINE_AUDIO_AND_GRAMMAR.md](../docs/evidence/T037_OFFLINE_AUDIO_AND_GRAMMAR.md). Note: 258 offline audio clips generated, checksummed, and packaged in assets with dynamic spoken grammar for money/weight/rate/ranges/safety/status in Hindi and Marathi; missing-clip fallback verified in AudioGrammarAndManifestTest. Awaiting end-to-end device audit in T046.

## AT-051

**Low-literacy accessible approved interactions** — RELEASE; status **NOT_RUN**.

Requirement: [R-UX-01](15_REQUIREMENTS.md#r-ux-01). Tasks: [T017](07_IMPLEMENTATION_PLAN.md#t017), [T036](07_IMPLEMENTATION_PLAN.md#t036), [T044](07_IMPLEMENTATION_PLAN.md#t044), [T046](07_IMPLEMENTATION_PLAN.md#t046). Spec: [05_DESIGN_STITCH](05_DESIGN_STITCH.md).

Check: Core screens use approved icons/photos, short labels and tap-to-hear, primary 56dp mobile targets, no color-only status, at most three primary inputs per step; large text/TalkBack/numeric input and explicit numeral preference remain usable.

Evidence: [T017_COLLECTOR_ONBOARDING_AND_LOTS.md](../docs/evidence/T017_COLLECTOR_ONBOARDING_AND_LOTS.md), [T036_LANGUAGE_RESOURCES_AND_ACCESSIBILITY.md](../docs/evidence/T036_LANGUAGE_RESOURCES_AND_ACCESSIBILITY.md). Note: Low-literacy accessible interactions implemented across C01-C05, C14, C15 in T017 and completed with numeral preference, TalkBack semantics (label + value + unit + status), and colloquial aliases in T036. Awaiting audio content in T037 and device usability tests in T044, T046.

## AT-052

**Entry-level Android performance** — RELEASE; status **NOT_RUN**.

Requirement: [R-UX-02](15_REQUIREMENTS.md#r-ux-02). Tasks: [T045](07_IMPLEMENTATION_PLAN.md#t045). Spec: [03_TECHSPEC](03_TECHSPEC.md).

Check: Record named device, APK/model/audio sizes, memory and launch/save/compression/API/model timings against documented budgets; any miss stays visible with remediation, no borrowed benchmarks.

Evidence: None.

## AT-053

**Material dataset reference and observations** — RELEASE; status **NOT_RUN**.

Requirement: [R-DATA-01](15_REQUIREMENTS.md#r-data-01). Tasks: [T010](07_IMPLEMENTATION_PLAN.md#t010), [T016](07_IMPLEMENTATION_PLAN.md#t016), [T031](07_IMPLEMENTATION_PLAN.md#t031), [T047](07_IMPLEMENTATION_PLAN.md#t047). Spec: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Check: Export material observations with category/subcategory/description/image/weight/condition/source/value linked to lots while catalog remains distinct; new lot produces an observation through normal workflow.

Evidence: [T010_MATERIAL_TAXONOMY.md](../docs/evidence/T010_MATERIAL_TAXONOMY.md), [T016_LOT_LIFECYCLE_BACKEND.md](../docs/evidence/T016_LOT_LIFECYCLE_BACKEND.md), [T031_DATASET_EXPORTS.md](../docs/evidence/T031_DATASET_EXPORTS.md). Note: Fractional kg to integer gram round-trip conversion and large weight anomaly quality flagging verified in T016; material taxonomy and alias exports with route classifications and SHA-256 seal verified in T031. Awaiting integration in T047.

## AT-054

**Price dataset lifecycle and feedback** — RELEASE; status **NOT_RUN**.

Requirement: [R-DATA-02](15_REQUIREMENTS.md#r-data-02). Tasks: [T011](07_IMPLEMENTATION_PLAN.md#t011), [T018](07_IMPLEMENTATION_PLAN.md#t018), [T031](07_IMPLEMENTATION_PLAN.md#t031), [T047](07_IMPLEMENTATION_PLAN.md#t047). Spec: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Check: Import→validate→review→aggregate→display→confirmed-transaction feedback→history/export works; one eligible transaction adds one sourced price observation; disputes/demo records do not contaminate real summaries.

Evidence: [T011_PRICE_OBSERVATION_PIPELINE.md](../docs/evidence/T011_PRICE_OBSERVATION_PIPELINE.md), [T018_PRICE_STATISTICS_VALUATION.md](../docs/evidence/T018_PRICE_STATISTICS_VALUATION.md), [T031_DATASET_EXPORTS.md](../docs/evidence/T031_DATASET_EXPORTS.md). Note: Price dataset observation moderation and weighted quantiles under PRICE_V1 verified in T011 and T018; closed-loop price observation feedback from settled transactions and price exports verified in T031. Awaiting integration in T047.

## AT-055

**Recycler dataset lifecycle** — RELEASE; status **NOT_RUN**.

Requirement: [R-DATA-03](15_REQUIREMENTS.md#r-data-03). Tasks: [T012](07_IMPLEMENTATION_PLAN.md#t012), [T021](07_IMPLEMENTATION_PLAN.md#t021), [T029](07_IMPLEMENTATION_PLAN.md#t029), [T031](07_IMPLEMENTATION_PLAN.md#t031), [T047](07_IMPLEMENTATION_PLAN.md#t047). Spec: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Check: Import facility, review source/current status, update operational data, refresh/expire verification and export versions; original registry claim and later operational update remain separately attributable.

Evidence: [T012_FACILITY_DIRECTORY.md](../docs/evidence/T012_FACILITY_DIRECTORY.md), [T021_RECYCLER_OFFER_WORKFLOWS.md](../docs/evidence/T021_RECYCLER_OFFER_WORKFLOWS.md), [T031_DATASET_EXPORTS.md](../docs/evidence/T031_DATASET_EXPORTS.md). Note: Facility operational updates and separate regulatory registry claims verified in T012 and T021; versioned facility directory export with authorization levels and battery route tags verified in T031. Awaiting regression in T047.

## AT-056

**Transaction dataset generated by workflow** — RELEASE; status **NOT_RUN**.

Requirement: [R-DATA-04](15_REQUIREMENTS.md#r-data-04). Tasks: [T026](07_IMPLEMENTATION_PLAN.md#t026), [T031](07_IMPLEMENTATION_PLAN.md#t031), [T047](07_IMPLEMENTATION_PLAN.md#t047). Spec: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Check: A demonstrated lot→offer→handover→payment produces a transaction export with party IDs, original/final weights/values, locations/times and separate payment/lifecycle status without hand-inserting completion rows.

Evidence: [T023_HANDOVER_CONFIRMATIONS.md](../docs/evidence/T023_HANDOVER_CONFIRMATIONS.md), [T026_PAYMENTS_AND_EARNINGS.md](../docs/evidence/T026_PAYMENTS_AND_EARNINGS.md), [T031_DATASET_EXPORTS.md](../docs/evidence/T031_DATASET_EXPORTS.md). Note: Complete lot -> offer -> handover -> payment assertions/acknowledgement -> closure produces structured transaction export records without hand-inserted rows verified in T023 and T026; transaction dataset export verified in T031. Awaiting regression suite in T047.

## AT-057

**Traceability dataset generated by events** — RELEASE; status **NOT_RUN**.

Requirement: [R-DATA-05](15_REQUIREMENTS.md#r-data-05). Tasks: [T023](07_IMPLEMENTATION_PLAN.md#t023), [T031](07_IMPLEMENTATION_PLAN.md#t031), [T047](07_IMPLEMENTATION_PLAN.md#t047). Spec: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Check: Export collection through confirmed receipt/status events with evidence refs, weights, times, location quality, reference and confirmation; verify chain and correction lineage without mutable-history loss.

Evidence: [T031_DATASET_EXPORTS.md](../docs/evidence/T031_DATASET_EXPORTS.md). Note: Traceability domain event export with prev_hash and event_hash SHA-256 chains, aggregate IDs, and actor roles verified in T031. Awaiting integration in T047.

## AT-058

**Minimal collector dataset and anonymization** — RELEASE; status **NOT_RUN**.

Requirement: [R-DATA-06](15_REQUIREMENTS.md#r-data-06). Tasks: [T007](07_IMPLEMENTATION_PLAN.md#t007), [T031](07_IMPLEMENTATION_PLAN.md#t031), [T040](07_IMPLEMENTATION_PLAN.md#t040), [T047](07_IMPLEMENTATION_PLAN.md#t047). Spec: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Check: Export collector ID/language/general area/history/totals with PII redacted by purpose; onboarding and transactions generate it; public export excludes phone, exact home location and credentials.

Evidence: [T031_DATASET_EXPORTS.md](../docs/evidence/T031_DATASET_EXPORTS.md), [T040_SECURITY_AND_ABUSE_BOUNDARIES.md](../docs/evidence/T040_SECURITY_AND_ABUSE_BOUNDARIES.md). Note: Minimal collector dataset export with zero PII (phone numbers masked, private names and precise GPS excluded), col_anon pseudonymization, and admin-only role check verified in T031 and T040. Final release documentation in T047.

## AT-059

**AI training dataset card and tabular links** — RELEASE; status **NOT_RUN**.

Requirement: [R-DATA-07](15_REQUIREMENTS.md#r-data-07). Tasks: [T032](07_IMPLEMENTATION_PLAN.md#t032), [T033](07_IMPLEMENTATION_PLAN.md#t033), [T047](07_IMPLEMENTATION_PLAN.md#t047). Spec: [19_AI_ML](19_AI_ML.md).

Check: Deliver training manifest/card with source, quality, size, labels, object splits and licensing plus nullable weight/price/location/transaction links where actually observed; absent measurements remain null, never inferred truth.

Evidence: [T032_LICENSED_IMAGE_DATASET.md](../docs/evidence/T032_LICENSED_IMAGE_DATASET.md), [T033_ON_DEVICE_CLASSIFIER.md](../docs/evidence/T033_ON_DEVICE_CLASSIFIER.md). Note: Delivered dataset card, licensing registry, manifest, and splits summary in T032. Source, quality, size, labels, object splits, licensing, and nullable links verified. Baseline model trained and evaluated in T033. Awaiting final evidence packaging in T047.

## AT-060

**Provenance and demo isolation everywhere** — RELEASE; status **NOT_RUN**.

Requirement: [R-DATA-08](15_REQUIREMENTS.md#r-data-08). Tasks: [T005](07_IMPLEMENTATION_PLAN.md#t005), [T029](07_IMPLEMENTATION_PLAN.md#t029), [T031](07_IMPLEMENTATION_PLAN.md#t031), [T040](07_IMPLEMENTATION_PLAN.md#t040). Spec: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Check: Display and export origin_class/source_kind/is_demo/date/version; public commercial data is not OFFICIAL; app-generated demo data is not real trade; mixed datasets disclose breakdown and synthetic lineage propagates.

Evidence: [T031_DATASET_EXPORTS.md](../docs/evidence/T031_DATASET_EXPORTS.md), [T040_SECURITY_AND_ABUSE_BOUNDARIES.md](../docs/evidence/T040_SECURITY_AND_ABUSE_BOUNDARIES.md). Note: Provenance fields (origin_class, source_kind, is_demo), strict demo data partition isolation, UNMET fieldwork disclosure, statutory non-EPR banner, and CSV formula injection neutralization verified across T031 and T040.

## AT-061

**Import cleaning geocoding and validation tools** — RELEASE; status **NOT_RUN**.

Requirement: [R-DATA-09](15_REQUIREMENTS.md#r-data-09). Tasks: [T005](07_IMPLEMENTATION_PLAN.md#t005), [T012](07_IMPLEMENTATION_PLAN.md#t012), [T031](07_IMPLEMENTATION_PLAN.md#t031). Spec: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Check: Rerun imports deterministically with checksums, preserve original documents and extraction locators, quarantine malformed rows, cache permitted geocodes and report accuracy; never silently discard or invent values.

Evidence: [T031_DATASET_EXPORTS.md](../docs/evidence/T031_DATASET_EXPORTS.md). Note: Curated dataset build tool scripts/build_curated_exports.py generating all 7 curated dataset packages with deterministic SHA-256 manifest verification and data cards verified in T031.

## AT-062

**Synthetic generator and edge-case scenarios** — RELEASE; status **NOT_RUN**.

Requirement: [R-DATA-10](15_REQUIREMENTS.md#r-data-10). Tasks: [T005](07_IMPLEMENTATION_PLAN.md#t005), [T043](07_IMPLEMENTATION_PLAN.md#t043). Spec: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Check: Seeded generator produces labelled valid workflow fixtures and separate invalid/retry/duplicate/mismatch/stale/reject/cancel scenarios; re-running does not duplicate seed identities or label generated records official.

Evidence: None.

## AT-063

**Seven data cards and versioned exports** — RELEASE; status **NOT_RUN**.

Requirement: [R-DATA-11](15_REQUIREMENTS.md#r-data-11). Tasks: [T031](07_IMPLEMENTATION_PLAN.md#t031), [T047](07_IMPLEMENTATION_PLAN.md#t047). Spec: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Check: For all seven families deliver schema/version/count/source/license/validation/update/use/limitations and export checksum; counts reconcile with stored rows and demo filters; no completed card contains invented values.

Evidence: [T031_DATASET_EXPORTS.md](../docs/evidence/T031_DATASET_EXPORTS.md). Note: Admin datasets catalog endpoint and Markdown data card retrieval conforming to docs/templates/DATA_CARD.md across all 7 families verified in T031. Awaiting evidence freeze in T047.

## AT-064

**Admin CRUD source and verification workflow** — RELEASE; status **PASS**.

Requirement: [R-ADMIN-01](15_REQUIREMENTS.md#r-admin-01). Tasks: [T029](07_IMPLEMENTATION_PLAN.md#t029), [T030](07_IMPLEMENTATION_PLAN.md#t030). Spec: [16_API_CONTRACT](16_API_CONTRACT.md).

Check: Admin can review facilities, materials/aliases/safety, prices and source revisions; ordinary recycler cannot approve itself; edits are audited and sync to caches without rewriting old receipts.

Evidence: [T029_ADMIN_MAINTENANCE_AND_METRICS.md](../docs/evidence/T029_ADMIN_MAINTENANCE_AND_METRICS.md), [T030_ADMIN_DASHBOARD.md](../docs/evidence/T030_ADMIN_DASHBOARD.md). Note: Backend facility verification assertions, material catalog CRUD, alias management, safety guide versioning, and price moderation workflows verified in T029; React admin web UI (A03, A04) verified in T030.

## AT-065

**Data quality review dashboard** — RELEASE; status **PASS**.

Requirement: [R-ADMIN-02](15_REQUIREMENTS.md#r-admin-02). Tasks: [T028](07_IMPLEMENTATION_PLAN.md#t028), [T030](07_IMPLEMENTATION_PLAN.md#t030). Spec: [MONITORING](MONITORING.md).

Check: Dashboard calculates missing/invalid/stale/duplicate/inconsistent/source coverage and demo fractions; drill into a flag and resolve with actor/reason; all percentages have denominators and real query evidence.

Evidence: [T028_DATA_QUALITY_AND_ANOMALIES.md](../docs/evidence/T028_DATA_QUALITY_AND_ANOMALIES.md), [T030_ADMIN_DASHBOARD.md](../docs/evidence/T030_ADMIN_DASHBOARD.md). Note: Admin data quality review APIs with filtering, single-flag drilldown, review resolution workflow, and summary metrics with true denominators verified in T028; React admin dashboard workbench (A06) verified in T030.

## AT-066

**Analytics and correct impact metrics** — RELEASE; status **PASS**.

Requirement: [R-ADMIN-03](15_REQUIREMENTS.md#r-admin-03). Tasks: [T029](07_IMPLEMENTATION_PLAN.md#t029), [T030](07_IMPLEMENTATION_PLAN.md#t030). Spec: [MONITORING](MONITORING.md).

Check: Metrics derive from events with time/region/provenance filters: activity/quotes/matches/dues/disputes/sync/model quality and verified received grams; exclude demo and never equate received material with proven recycling or CO2 savings.

Evidence: [T029_ADMIN_MAINTENANCE_AND_METRICS.md](../docs/evidence/T029_ADMIN_MAINTENANCE_AND_METRICS.md), [T030_ADMIN_DASHBOARD.md](../docs/evidence/T030_ADMIN_DASHBOARD.md). Note: Platform overview and metrics endpoints deriving from persisted tables with real denominators, demo data isolation, honest mass label 'received, not recycled', and explicit UNMET fieldwork provenance verified in T029; React analytics UI (A01, A07) verified in T030.

## AT-067

**Illustrative unit-economics screen** — RELEASE; status **PASS**.

Requirement: [R-ECON-01](15_REQUIREMENTS.md#r-econ-01). Tasks: [T038](07_IMPLEMENTATION_PLAN.md#t038), [T039](07_IMPLEMENTATION_PLAN.md#t039). Spec: [23_UNIT_ECONOMICS](23_UNIT_ECONOMICS.md).

Check: Change source-linked same-lot input assumptions and observe recalculated current/platform net, delta and valid percentage; show negative/no-benefit cases and explicit illustrative label separate from actual ledger.

Evidence: [T038_ILLUSTRATIVE_ECONOMICS.md](../docs/evidence/T038_ILLUSTRATIVE_ECONOMICS.md), [T039_ECONOMICS_AND_SAFETY_VIEWS.md](../docs/evidence/T039_ECONOMICS_AND_SAFETY_VIEWS.md). Note: Same-lot comparison engine, integer paise arithmetic, sensitivity parameters, non-trivial zero/negative baseline handling, and REST APIs verified in T038; interactive U01 web economics workspace matching Stitch design cab89a974c04 verified in T039 with dynamic recalculation sliders, waterfall chart, zero-baseline safety, and zero collector fee guarantee verified in U01_UnitEconomics.test.

## AT-068

**Platform sustainability without collector fees** — RELEASE; status **NOT_RUN**.

Requirement: [R-ECON-02](15_REQUIREMENTS.md#r-econ-02). Tasks: [T038](07_IMPLEMENTATION_PLAN.md#t038), [T048](07_IMPLEMENTATION_PLAN.md#t048). Spec: [23_UNIT_ECONOMICS](23_UNIT_ECONOMICS.md).

Check: Show hypothetical downstream fee revenue minus variable/fixed operating costs and break-even sensitivity; no fee actually charged, credit eligibility or guaranteed uplift implied.

Evidence: [T038_ILLUSTRATIVE_ECONOMICS.md](../docs/evidence/T038_ILLUSTRATIVE_ECONOMICS.md). Note: Platform sustainability model with 0 collector fee guarantee, downstream recycler fee economics, variable/fixed cost sensitivity, break-even transaction calculations, and explicit illustrative disclaimers verified in T038. Awaiting presentation deck and demo video in T048.

## AT-069

**Honest secondary research and personas** — RELEASE; status **NOT_RUN**.

Requirement: [R-RES-01](15_REQUIREMENTS.md#r-res-01). Tasks: [T004](07_IMPLEMENTATION_PLAN.md#t004), [T047](07_IMPLEMENTATION_PLAN.md#t047), [T048](07_IMPLEMENTATION_PLAN.md#t048). Spec: [21_RESEARCH_EVIDENCE](21_RESEARCH_EVIDENCE.md).

Check: Research package identifies each published source, its scope and design inference; personas/scenarios are labelled simulated; deck says no primary interviews completed and never invents participants or quotes.

Evidence: None.

## AT-070

**Two working collector/aggregator field research** — EXTERNAL_GAP; status **UNMET**.

Requirement: [R-RES-02](15_REQUIREMENTS.md#r-res-02). Tasks: [T004](07_IMPLEMENTATION_PLAN.md#t004), [T047](07_IMPLEMENTATION_PLAN.md#t047), [T048](07_IMPLEMENTATION_PLAN.md#t048), [T050](07_IMPLEMENTATION_PLAN.md#t050). Spec: [21_RESEARCH_EVIDENCE](21_RESEARCH_EVIDENCE.md).

Check: This remains UNMET while desk research is the owner choice. Only actual consented engagement with at least two working participants and evidence could satisfy it; documentation or synthetic scenarios cannot mark it passed.

Evidence: None. Note: Primary fieldwork not conducted; owner chose secondary research.

## AT-071

**Receipt terminology and no false authorization** — RELEASE; status **NOT_RUN**.

Requirement: [R-REG-01](15_REQUIREMENTS.md#r-reg-01). Tasks: [T023](07_IMPLEMENTATION_PLAN.md#t023), [T024](07_IMPLEMENTATION_PLAN.md#t024), [T031](07_IMPLEMENTATION_PLAN.md#t031), [T048](07_IMPLEMENTATION_PLAN.md#t048). Spec: [22_REGULATORY_SAFETY](22_REGULATORY_SAFETY.md).

Check: App/PDF/CSV/deck call the artifact a platform Digital Handover Record; collector identity is not a licence; no official EPR certificate, government endorsement or established CPCB integration is claimed.

Evidence: [T031_DATASET_EXPORTS.md](../docs/evidence/T031_DATASET_EXPORTS.md). Note: Statutory non-EPR disclosure notice present in HTTP response headers and CSV export comment headers, and Digital Handover Record platform labeling verified in T031. Awaiting presentation deck in T048.

## AT-072

**PIN abuse secrets and transport safety** — RELEASE; status **NOT_RUN**.

Requirement: [R-SEC-01](15_REQUIREMENTS.md#r-sec-01). Tasks: [T007](07_IMPLEMENTATION_PLAN.md#t007), [T040](07_IMPLEMENTATION_PLAN.md#t040), [T041](07_IMPLEMENTATION_PLAN.md#t041). Spec: [12_GUARDRAILS](12_GUARDRAILS.md).

Check: Rate-limit PIN attempts, restrict role grants, rotate/revoke sessions, verify release HTTPS and restrictive CORS; APK/web/repo/log/QR contain no server key, PIN or private database credentials.

Evidence: [T040_SECURITY_AND_ABUSE_BOUNDARIES.md](../docs/evidence/T040_SECURITY_AND_ABUSE_BOUNDARIES.md). Note: PIN brute-force lockout (429 with Retry-After), uniform 401 user enumeration prevention, session rotation, replay revocation, and repository secrets scan (0 found) verified locally in T040. On 2026-10-01, deployed Render HTTPS health returned 200 and CORS preflight allowed sahitol.pages.dev but rejected evil.example. This is contributing evidence; acceptance remains NOT_RUN until contributing task T041 is closed.

## AT-073

**Privacy media access retention and audit** — RELEASE; status **NOT_RUN**.

Requirement: [R-SEC-02](15_REQUIREMENTS.md#r-sec-02). Tasks: [T008](07_IMPLEMENTATION_PLAN.md#t008), [T040](07_IMPLEMENTATION_PLAN.md#t040), [T042](07_IMPLEMENTATION_PLAN.md#t042). Spec: [12_GUARDRAILS](12_GUARDRAILS.md).

Check: Private images require authorization; signed URLs expire; uploads cannot traverse filesystem; exports redact PII; retention/deletion policy preserves justified audit and pending data while clearing obsolete access safely.

Evidence: [T040_SECURITY_AND_ABUSE_BOUNDARIES.md](../docs/evidence/T040_SECURITY_AND_ABUSE_BOUNDARIES.md), [T042_LOCAL_FALLBACK_AND_RESTORE.md](../docs/evidence/T042_LOCAL_FALLBACK_AND_RESTORE.md). Note: Private image authorization, EXIF metadata stripping, signed URL expiration, path traversal prevention, and oversized upload rejection verified in T040. Cryptographic backup/restore, tampering detection, and media audit retention verified in T042.

## AT-074

**Hosted remote judge access** — RELEASE; status **NOT_RUN**.

Requirement: [R-OPS-01](15_REQUIREMENTS.md#r-ops-01). Tasks: [T041](07_IMPLEMENTATION_PLAN.md#t041), [T044](07_IMPLEMENTATION_PLAN.md#t044), [T050](07_IMPLEMENTATION_PLAN.md#t050). Spec: [DEPLOYMENT](DEPLOYMENT.md).

Check: Install release APK and open web console outside developer Wi-Fi; HTTPS API, PostGIS, private storage and QR work; cold start has recoverable UI; persistent photos survive API redeploy.

Evidence: None.

## AT-075

**Reproducible local fallback and recovery** — RELEASE; status **NOT_RUN**.

Requirement: [R-OPS-02](15_REQUIREMENTS.md#r-ops-02). Tasks: [T042](07_IMPLEMENTATION_PLAN.md#t042). Spec: [DEPLOYMENT](DEPLOYMENT.md).

Check: Fresh local Compose environment runs same schema and fixture journey; Android debug LAN configuration works; database/media restore rehearsed; browser scan fallback handles insecure local camera context without weakening release TLS.

Evidence: [T042_LOCAL_FALLBACK_AND_RESTORE.md](../docs/evidence/T042_LOCAL_FALLBACK_AND_RESTORE.md). Note: Reproducible local Docker Compose environment with PostGIS, Android release HTTPS vs debug LAN network security configuration, cryptographic database/media backup and restore, and web manual reference lookup fallback verified in T042.

## AT-076

**No required paid runtime dependency** — RELEASE; status **NOT_RUN**.

Requirement: [R-OPS-03](15_REQUIREMENTS.md#r-ops-03). Tasks: [T001](07_IMPLEMENTATION_PLAN.md#t001), [T037](07_IMPLEMENTATION_PLAN.md#t037), [T041](07_IMPLEMENTATION_PLAN.md#t041). Spec: [11_SECRETS_CHECKLIST](11_SECRETS_CHECKLIST.md).

Check: Audit dependency/service/config list and execute core with cloud speech/maps/AI unavailable; no mandatory SMS, LLM, payment gateway, custom domain or billing upgrade is required; current free-plan/account limitations documented.

Evidence: [T037_OFFLINE_AUDIO_AND_GRAMMAR.md](../docs/evidence/T037_OFFLINE_AUDIO_AND_GRAMMAR.md). Note: Pre-generated offline audio eliminates runtime cloud speech/TTS API dependency; free Edge-TTS workflow documented with open-access license attribution; awaiting multi-service runtime dependency audit in T043.

## AT-077

**Monitoring and diagnostics** — RELEASE; status **NOT_RUN**.

Requirement: [R-OPS-04](15_REQUIREMENTS.md#r-ops-04). Tasks: [T028](07_IMPLEMENTATION_PLAN.md#t028), [T029](07_IMPLEMENTATION_PLAN.md#t029), [T042](07_IMPLEMENTATION_PLAN.md#t042). Spec: [MONITORING](MONITORING.md).

Check: Health and redacted structured logs expose failed sync/conflicts/media/DB errors with correlation IDs; dashboard denominators and last refresh distinguish outage from empty data; actionable local recovery steps work.

Evidence: [T028_DATA_QUALITY_AND_ANOMALIES.md](../docs/evidence/T028_DATA_QUALITY_AND_ANOMALIES.md), [T029_ADMIN_MAINTENANCE_AND_METRICS.md](../docs/evidence/T029_ADMIN_MAINTENANCE_AND_METRICS.md), [T042_LOCAL_FALLBACK_AND_RESTORE.md](../docs/evidence/T042_LOCAL_FALLBACK_AND_RESTORE.md). Note: Data quality anomaly rules, admin maintenance APIs, /health/live and /health/ready probes with zero credential leakage, X-Correlation-ID request tracking, and structured redacted access logging verified across T028, T029, and T042.

## AT-078

**Critical end-to-end and adversarial acceptance** — RELEASE; status **NOT_RUN**.

Requirement: [R-QA-01](15_REQUIREMENTS.md#r-qa-01). Tasks: [T043](07_IMPLEMENTATION_PLAN.md#t043), [T044](07_IMPLEMENTATION_PLAN.md#t044). Spec: [20_TEST_ACCEPTANCE](20_TEST_ACCEPTANCE.md).

Check: Pass online and airplane-mode lot→price→match→pending QR→sync→second-phone confirmation→payment→ledger→admin plus duplicate/crash/denial/stale/conflict/auth tests with actual logs and device evidence.

Evidence: None.

## AT-079

**Live scenario demonstration and backup** — RELEASE; status **NOT_RUN**.

Requirement: [R-QA-02](15_REQUIREMENTS.md#r-qa-02). Tasks: [T044](07_IMPLEMENTATION_PLAN.md#t044), [T049](07_IMPLEMENTATION_PLAN.md#t049). Spec: [24_DEMO_PRESENTATION](24_DEMO_PRESENTATION.md).

Check: A person actually performs the complete journey on devices, records failures and fixes, and produces playable demo/backups; no unexecuted script or prefilled database is represented as live usability evidence.

Evidence: None.

## AT-080

**Outsider documentation and presenter readiness** — RELEASE; status **NOT_RUN**.

Requirement: [R-DOC-01](15_REQUIREMENTS.md#r-doc-01). Tasks: [T047](07_IMPLEMENTATION_PLAN.md#t047), [T048](07_IMPLEMENTATION_PLAN.md#t048), [T050](07_IMPLEMENTATION_PLAN.md#t050). Spec: [00_README](00_README.md).

Check: New reader follows README to scope/architecture/decisions/data/run/demo; presenters can explain sources, offline pending vs confirmed, price limits, model limits, battery route and unmet fieldwork without relying on chat history.

Evidence: None.

## FT-001

**Assisted collector and aggregator accounts** — FUTURE; status **DEFERRED**.

Requirement: [R-FUT-01](15_REQUIREMENTS.md#r-fut-01). Tasks: [F001](07_IMPLEMENTATION_PLAN.md#f001). Spec: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Check: Explicit delegation/consent, actor versus beneficial owner, safe phone-less onboarding, separate permissions and offline ownership tests; no admin impersonation shortcut.

Evidence: None. Note: Outside current release, retained for completeness.

## FT-002

**Multi-collector batching and pickup operations** — FUTURE; status **DEFERRED**.

Requirement: [R-FUT-02](15_REQUIREMENTS.md#r-fut-02). Tasks: [F002](07_IMPLEMENTATION_PLAN.md#f002). Spec: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Check: Batch membership/weights/provenance and collector-level proceeds reconcile; operational capacity and actual pickup success recorded; no double counting.

Evidence: None. Note: Outside current release, retained for completeness.

## FT-003

**Predictive prices and automated public feeds** — FUTURE; status **DEFERRED**.

Requirement: [R-FUT-03](15_REQUIREMENTS.md#r-fut-03). Tasks: [F003](07_IMPLEMENTATION_PLAN.md#f003). Spec: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Check: Licensed sustained comparable observations, temporal holdout against statistical baseline, uncertainty/drift monitoring and a permitted refresh pipeline; keep indicative labels.

Evidence: None. Note: Outside current release, retained for completeness.

## FT-004

**Consented active learning and broader classifier** — FUTURE; status **DEFERRED**.

Requirement: [R-FUT-04](15_REQUIREMENTS.md#r-fut-04). Tasks: [F004](07_IMPLEMENTATION_PLAN.md#f004). Spec: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Check: New consent/rights policy, reviewed correction labels, expanded relevant classes, leakage-safe evaluation and version rollback; current release remains public-images-only.

Evidence: None. Note: Outside current release, retained for completeness.

## FT-005

**Learned recycler ranking and advanced risk detection** — FUTURE; status **DEFERRED**.

Requirement: [R-FUT-05](15_REQUIREMENTS.md#r-fut-05). Tasks: [F005](07_IMPLEMENTATION_PLAN.md#f005). Spec: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Check: Enough quality outcome labels, temporal evaluation/fairness/reason codes, human review and safety hard filters; do not learn to override route eligibility or accuse fraud.

Evidence: None. Note: Outside current release, retained for completeness.

## FT-006

**Voice input and multilingual assistant** — FUTURE; status **DEFERRED**.

Requirement: [R-FUT-06](15_REQUIREMENTS.md#r-fut-06). Tasks: [F006](07_IMPLEMENTATION_PLAN.md#f006). Spec: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Check: Free/licensed offline ASR where viable, hi/mr noisy-environment tests, explicit confirmation of money/material values and manual fallback; no arbitrary autonomous transaction agent.

Evidence: None. Note: Outside current release, retained for completeness.

## FT-007

**Pickup route optimization** — FUTURE; status **DEFERRED**.

Requirement: [R-FUT-07](15_REQUIREMENTS.md#r-fut-07). Tasks: [F007](07_IMPLEMENTATION_PLAN.md#f007). Spec: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Check: Consented operational locations, realistic vehicle/capacity/time windows, permitted map data and measured routing baseline; no continuous collector tracking by default.

Evidence: None. Note: Outside current release, retained for completeness.

## FT-008

**ERP GST PRO brand and CPCB adapters** — FUTURE; status **DEFERRED**.

Requirement: [R-FUT-08](15_REQUIREMENTS.md#r-fut-08). Tasks: [F008](07_IMPLEMENTATION_PLAN.md#f008). Spec: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Check: Documented official/partner API contracts, credentials and legal role, validated field mapping/sandbox evidence, access/audit controls; no claim of integration or certificate issuance before verification.

Evidence: None. Note: Outside current release, retained for completeness.

## FT-009

**Downstream processing and material mass balance** — FUTURE; status **DEFERRED**.

Requirement: [R-FUT-09](15_REQUIREMENTS.md#r-fut-09). Tasks: [F009](07_IMPLEMENTATION_PLAN.md#f009). Spec: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Check: Recycler processing evidence, batch splits/merges/yield reconciliation and independently supported downstream outcomes before calling received mass recycled.

Evidence: None. Note: Outside current release, retained for completeness.

## FT-010

**Ed25519 server-signed records** — FUTURE; status **DEFERRED**.

Requirement: [R-FUT-10](15_REQUIREMENTS.md#r-fut-10). Tasks: [F010](07_IMPLEMENTATION_PLAN.md#f010). Spec: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Check: Canonical payload parity, secure signing keys/rotation/revocation/trusted public-key distribution and verification fixtures; signature still does not prove physical facts.

Evidence: None. Note: Outside current release, retained for completeness.

## FT-011

**Recovery indicator and environmental estimates** — FUTURE; status **DEFERRED**.

Requirement: [R-FUT-11](15_REQUIREMENTS.md#r-fut-11). Tasks: [F011](07_IMPLEMENTATION_PLAN.md#f011). Spec: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Check: Exact peer-reviewed composition/LCA sources, material/device-specific uncertainty and defensible model validation; no invented official formula, exact metal yield or unsupported CO2 savings. Owner must explicitly promote this optional idea.

Evidence: None. Note: Outside current release, retained for completeness.

## FT-012

**Supervised real-world pilot and partnerships** — FUTURE; status **DEFERRED**.

Requirement: [R-FUT-12](15_REQUIREMENTS.md#r-fut-12). Tasks: [F012](07_IMPLEMENTATION_PLAN.md#f012). Spec: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Check: Consented real collectors/facilities, review safety/privacy/retention/support, actual partnership evidence and measured feedback; historical 5–10/20–30 counts are planning suggestions.

Evidence: None. Note: Outside current release, retained for completeness.

## FT-013

**More regions languages and material routes** — FUTURE; status **DEFERRED**.

Requirement: [R-FUT-13](15_REQUIREMENTS.md#r-fut-13). Tasks: [F013](07_IMPLEMENTATION_PLAN.md#f013). Spec: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Check: Region/language source and review coverage, safe route-specific authorization and model/material validation; preserve e-waste focus until explicit expansion.

Evidence: None. Note: Outside current release, retained for completeness.

## FT-014

**Aggregated sector and government insights** — FUTURE; status **DEFERRED**.

Requirement: [R-FUT-14](15_REQUIREMENTS.md#r-fut-14). Tasks: [F014](07_IMPLEMENTATION_PLAN.md#f014). Spec: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Check: Adequate representative data, aggregation/privacy controls and sample/denominator limitations for supply/capacity gaps, volatility/material flows/safety; no prototype national statistics.

Evidence: None. Note: Outside current release, retained for completeness.

## FT-015

**Advanced dispute review and support workflow** — FUTURE; status **DEFERRED**.

Requirement: [R-FUT-15](15_REQUIREMENTS.md#r-fut-15). Tasks: [F015](07_IMPLEMENTATION_PLAN.md#f015). Spec: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Check: Evidence submission/reviewer permissions/appeal/resolution timeline, immutable original quote/final terms and policy; basic pending/disputed states already required in release.

Evidence: None. Note: Outside current release, retained for completeness.

## FT-016

**Optional payments messaging and monetization** — FUTURE; status **DEFERRED**.

Requirement: [R-FUT-16](15_REQUIREMENTS.md#r-fut-16). Tasks: [F016](07_IMPLEMENTATION_PLAN.md#f016). Spec: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Check: Separate owner approval, lawful provider terms, fee transparency, webhook idempotency and reconciled settlement; SMS/WhatsApp/email/real UPI/paid SaaS not release dependencies.

Evidence: None. Note: Outside current release, retained for completeness.

## FT-017

**Collector identity sharing and partner services** — FUTURE; status **DEFERRED**.

Requirement: [R-FUT-17](15_REQUIREMENTS.md#r-fut-17). Tasks: [F017](07_IMPLEMENTATION_PLAN.md#f017). Spec: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Check: Minimal revocable identity QR/consent-scoped history sharing; verified partner eligibility rules before any credit/welfare claim; never public financial profiles or guaranteed access.

Evidence: None. Note: Outside current release, retained for completeness.

## FT-018

**Production operations and scale** — FUTURE; status **DEFERRED**.

Requirement: [R-FUT-18](15_REQUIREMENTS.md#r-fut-18). Tasks: [F018](07_IMPLEMENTATION_PLAN.md#f018). Spec: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Check: Measured bottleneck/load and security requirements justify queues/caching/infra, incident support and disaster recovery; no speculative Kubernetes/microservices or blockchain requirement.

Evidence: None. Note: Outside current release, retained for completeness.

