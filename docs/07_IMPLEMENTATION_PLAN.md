# Implementation plan

Generated from [catalog](planning/catalog.json) and [status](planning/status.json). Edit those files, then run `python scripts/render_docs.py` and `python scripts/check_docs.py`. Do not edit this view independently.

All tasks start unimplemented. A task DONE needs its concrete output and task-level evidence; multi-task acceptance may remain pending until integration. Final release requires every RELEASE case PASS. T002 never bypasses per-screen Stitch gates.

## T001

**Bootstrap repository and compatible toolchain** — stage 0; scope RELEASE; status **DONE**.

Dependencies: None.

Read before coding: [03_TECHSPEC](03_TECHSPEC.md), [09_DECISIONS](09_DECISIONS.md), [11_SECRETS_CHECKLIST](11_SECRETS_CHECKLIST.md).

Concrete output: Create Android/API/web project skeletons without inventing UI; pin a tested toolchain and dependency locks; add environment examples, PostGIS Compose service, CI lint/test/build jobs and documented commands.

Requirements: [R-GOV-01](15_REQUIREMENTS.md#r-gov-01), [R-GOV-03](15_REQUIREMENTS.md#r-gov-03), [R-ARC-01](15_REQUIREMENTS.md#r-arc-01), [R-ARC-02](15_REQUIREMENTS.md#r-arc-02), [R-OPS-03](15_REQUIREMENTS.md#r-ops-03).

Acceptance: [AT-001](20_TEST_ACCEPTANCE.md#at-001), [AT-003](20_TEST_ACCEPTANCE.md#at-003), [AT-005](20_TEST_ACCEPTANCE.md#at-005), [AT-006](20_TEST_ACCEPTANCE.md#at-006), [AT-076](20_TEST_ACCEPTANCE.md#at-076).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T002

**Obtain and register owner-generated Stitch designs** — stage 0; scope RELEASE; status **DONE**.

Dependencies: None.

Read before coding: [05_DESIGN_STITCH](05_DESIGN_STITCH.md), [04_APPFLOW](04_APPFLOW.md).

Concrete output: Present the prepared screen briefs by batch; owner generates screens; read the designated Stitch project through MCP; save screen IDs, revisions and approved state coverage in design/stitch/SCREEN_REGISTRY.md. Repeat this gate for later batches; the initial spike needs S00 only.

Requirements: [R-GOV-02](15_REQUIREMENTS.md#r-gov-02).

Acceptance: [AT-002](20_TEST_ACCEPTANCE.md#at-002).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T003

**Prove Android feasibility on a real phone** — stage 0; scope RELEASE; status **DONE**.

Dependencies: [T001](07_IMPLEMENTATION_PLAN.md#t001), [T002](07_IMPLEMENTATION_PLAN.md#t002).

Read before coding: [03_TECHSPEC](03_TECHSPEC.md), [19_AI_ML](19_AI_ML.md), [05_DESIGN_STITCH](05_DESIGN_STITCH.md).

Concrete output: Implement approved S00 diagnostic screen; capture/compress photo, save/read Room row after restart, run a bundled LiteRT baseline prediction in airplane mode, record phone/toolchain/APK evidence. Baseline prediction is not the trained SahiTol classifier. Failure is a visible blocker, never automatic PWA substitution.

Requirements: [R-ARC-01](15_REQUIREMENTS.md#r-arc-01).

Acceptance: [AT-005](20_TEST_ACCEPTANCE.md#at-005).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T004

**Complete secondary-research and source register** — stage 0; scope RELEASE; status **DONE**.

Dependencies: None.

Read before coding: [21_RESEARCH_EVIDENCE](21_RESEARCH_EVIDENCE.md), [22_REGULATORY_SAFETY](22_REGULATORY_SAFETY.md), [PROBLEM_STATEMENT](PROBLEM_STATEMENT.md).

Concrete output: Build 5–7 attributed desk-research insight cards and 2–3 labelled personas; retain source/date/scope/limitations, link insights to requirement IDs; record primary fieldwork as not conducted and check the authenticated official brief/cutoff when available.

Requirements: [R-RES-01](15_REQUIREMENTS.md#r-res-01), [R-RES-02](15_REQUIREMENTS.md#r-res-02).

Acceptance: [AT-069](20_TEST_ACCEPTANCE.md#at-069), [AT-070](20_TEST_ACCEPTANCE.md#at-070).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T005

**Build reproducible data import and validation tools** — stage 1; scope RELEASE; status **DONE**.

Dependencies: [T001](07_IMPLEMENTATION_PLAN.md#t001).

Read before coding: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md), [06_SCHEMA](06_SCHEMA.md).

Concrete output: Implement PDF/CSV/JSON import staging, pandas cleaning, field-level lineage, cached geocoding with provider policy, validation/quarantine, duplicate detection, reproducible seed and synthetic scripts. Invalid records must remain inspectable and never count as accepted.

Requirements: [R-DATA-08](15_REQUIREMENTS.md#r-data-08), [R-DATA-09](15_REQUIREMENTS.md#r-data-09), [R-DATA-10](15_REQUIREMENTS.md#r-data-10).

Acceptance: [AT-060](20_TEST_ACCEPTANCE.md#at-060), [AT-061](20_TEST_ACCEPTANCE.md#at-061), [AT-062](20_TEST_ACCEPTANCE.md#at-062).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T006

**Implement PostgreSQL/PostGIS schema and migrations** — stage 1; scope RELEASE; status **DONE**.

Dependencies: [T001](07_IMPLEMENTATION_PLAN.md#t001).

Read before coding: [06_SCHEMA](06_SCHEMA.md), [16_API_CONTRACT](16_API_CONTRACT.md), [04_APPFLOW](04_APPFLOW.md).

Concrete output: Create tables, indexes, route/role constraints, integer money/weight, immutable events, versions and sync results. Test migration on empty DB and upgrade fixtures; verify extension and private DB permissions locally and hosted.

Requirements: [R-ARC-02](15_REQUIREMENTS.md#r-arc-02).

Acceptance: [AT-006](20_TEST_ACCEPTANCE.md#at-006).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T007

**Implement phone/PIN authentication and ownership** — stage 1; scope RELEASE; status **DONE**.

Dependencies: [T006](07_IMPLEMENTATION_PLAN.md#t006).

Read before coding: [16_API_CONTRACT](16_API_CONTRACT.md), [12_GUARDRAILS](12_GUARDRAILS.md), [11_SECRETS_CHECKLIST](11_SECRETS_CHECKLIST.md).

Concrete output: Implement Argon2id PIN storage, rate-limited phone/PIN login, rotating/revocable session flow, COLLECTOR/RECYCLER/ADMIN authorization, device scoping, explicit isolated demo access, online first activation and secure Android session continuation contract.

Requirements: [R-AUTH-01](15_REQUIREMENTS.md#r-auth-01), [R-AUTH-02](15_REQUIREMENTS.md#r-auth-02), [R-AUTH-03](15_REQUIREMENTS.md#r-auth-03), [R-AUTH-04](15_REQUIREMENTS.md#r-auth-04), [R-DATA-06](15_REQUIREMENTS.md#r-data-06), [R-SEC-01](15_REQUIREMENTS.md#r-sec-01).

Acceptance: [AT-007](20_TEST_ACCEPTANCE.md#at-007), [AT-008](20_TEST_ACCEPTANCE.md#at-008), [AT-009](20_TEST_ACCEPTANCE.md#at-009), [AT-010](20_TEST_ACCEPTANCE.md#at-010), [AT-058](20_TEST_ACCEPTANCE.md#at-058), [AT-072](20_TEST_ACCEPTANCE.md#at-072).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T008

**Implement private media storage adapter** — stage 1; scope RELEASE; status **DONE**.

Dependencies: [T006](07_IMPLEMENTATION_PLAN.md#t006), [T007](07_IMPLEMENTATION_PLAN.md#t007).

Read before coding: [06_SCHEMA](06_SCHEMA.md), [16_API_CONTRACT](16_API_CONTRACT.md), [DEPLOYMENT](DEPLOYMENT.md).

Concrete output: Implement local-volume and Supabase-private-storage adapters; bounded image upload/validation/checksum, short-lived authorized access, missing-upload recovery and PDF storage. No permanent files on the free API host filesystem.

Requirements: [R-ARC-02](15_REQUIREMENTS.md#r-arc-02), [R-LOT-02](15_REQUIREMENTS.md#r-lot-02), [R-SEC-02](15_REQUIREMENTS.md#r-sec-02).

Acceptance: [AT-006](20_TEST_ACCEPTANCE.md#at-006), [AT-012](20_TEST_ACCEPTANCE.md#at-012), [AT-073](20_TEST_ACCEPTANCE.md#at-073).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T009

**Implement versioned reference bootstrap and delta APIs** — stage 1; scope RELEASE; status **DONE**.

Dependencies: [T006](07_IMPLEMENTATION_PLAN.md#t006), [T007](07_IMPLEMENTATION_PLAN.md#t007).

Read before coding: [16_API_CONTRACT](16_API_CONTRACT.md), [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md).

Concrete output: Expose material/alias/safety/price/directory snapshots with versions, policy parameters, source timestamps, tombstones, expiry and opaque cursor; filter by region and role; provide labelled bundled demo cache for first offline launch.

Requirements: [R-OFF-01](15_REQUIREMENTS.md#r-off-01).

Acceptance: [AT-038](20_TEST_ACCEPTANCE.md#at-038).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T010

**Curate material taxonomy and language aliases** — stage 1; scope RELEASE; status **DONE**.

Dependencies: [T004](07_IMPLEMENTATION_PLAN.md#t004), [T005](07_IMPLEMENTATION_PLAN.md#t005), [T006](07_IMPLEMENTATION_PLAN.md#t006).

Read before coding: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md), [22_REGULATORY_SAFETY](22_REGULATORY_SAFETY.md), [14_TRANSLATION_AUDIO_AUDIT](14_TRANSLATION_AUDIO_AUDIT.md).

Concrete output: Seed every PS-named material, battery chemistry and UNKNOWN/OTHER; separate reference catalog from observed lot material; attach route, contextual safety, units, condition and hi/mr/en aliases. Add provenance-dependent routing for plastics/mixed waste.

Requirements: [R-LOT-01](15_REQUIREMENTS.md#r-lot-01), [R-DATA-01](15_REQUIREMENTS.md#r-data-01).

Acceptance: [AT-011](20_TEST_ACCEPTANCE.md#at-011), [AT-053](20_TEST_ACCEPTANCE.md#at-053).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T011

**Create attributed price seed and observation pipeline** — stage 1; scope RELEASE; status **DONE**.

Dependencies: [T004](07_IMPLEMENTATION_PLAN.md#t004), [T005](07_IMPLEMENTATION_PLAN.md#t005), [T006](07_IMPLEMENTATION_PLAN.md#t006), [T010](07_IMPLEMENTATION_PLAN.md#t010).

Read before coding: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md), [03_TECHSPEC](03_TECHSPEC.md).

Concrete output: Import dated public buying/quoted/selling observations, unit/geography/condition/source metadata and licence/usage notes; partition demo series; add authenticated observation entry and review. Never fill missing live prices with synthetic rows.

Requirements: [R-PRICE-01](15_REQUIREMENTS.md#r-price-01), [R-DATA-02](15_REQUIREMENTS.md#r-data-02).

Acceptance: [AT-016](20_TEST_ACCEPTANCE.md#at-016), [AT-054](20_TEST_ACCEPTANCE.md#at-054).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T012

**Build Delhi-NCR and Maharashtra facility directory** — stage 1; scope RELEASE; status **DONE**.

Dependencies: [T004](07_IMPLEMENTATION_PLAN.md#t004), [T005](07_IMPLEMENTATION_PLAN.md#t005), [T006](07_IMPLEMENTATION_PLAN.md#t006), [T010](07_IMPLEMENTATION_PLAN.md#t010).

Read before coding: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md), [22_REGULATORY_SAFETY](22_REGULATORY_SAFETY.md).

Concrete output: Import small CPCB/DPCC/MPCB subsets; preserve facility role, registry/list date, route registration, validity, material acceptance evidence and field lineage; review geocodes, deduplicate facilities, and mark unknown pickup/rates as unknown.

Requirements: [R-REC-01](15_REQUIREMENTS.md#r-rec-01), [R-REC-02](15_REQUIREMENTS.md#r-rec-02), [R-REC-03](15_REQUIREMENTS.md#r-rec-03), [R-DATA-03](15_REQUIREMENTS.md#r-data-03), [R-DATA-09](15_REQUIREMENTS.md#r-data-09).

Acceptance: [AT-021](20_TEST_ACCEPTANCE.md#at-021), [AT-022](20_TEST_ACCEPTANCE.md#at-022), [AT-023](20_TEST_ACCEPTANCE.md#at-023), [AT-055](20_TEST_ACCEPTANCE.md#at-055), [AT-061](20_TEST_ACCEPTANCE.md#at-061).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T013

**Implement Android Room repositories and durable outbox** — stage 2; scope RELEASE; status **DONE**.

Dependencies: [T003](07_IMPLEMENTATION_PLAN.md#t003), [T006](07_IMPLEMENTATION_PLAN.md#t006).

Read before coding: [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md), [06_SCHEMA](06_SCHEMA.md).

Concrete output: Implement local entities, migrations, atomic object+event+outbox write, staged image persistence, cache reads, user partition and logout preservation. Prove process death cannot show a saved record that was lost.

Requirements: [R-AUTH-03](15_REQUIREMENTS.md#r-auth-03), [R-LOT-02](15_REQUIREMENTS.md#r-lot-02), [R-LOT-05](15_REQUIREMENTS.md#r-lot-05), [R-OFF-01](15_REQUIREMENTS.md#r-off-01), [R-OFF-02](15_REQUIREMENTS.md#r-off-02).

Acceptance: [AT-009](20_TEST_ACCEPTANCE.md#at-009), [AT-012](20_TEST_ACCEPTANCE.md#at-012), [AT-015](20_TEST_ACCEPTANCE.md#at-015), [AT-038](20_TEST_ACCEPTANCE.md#at-038), [AT-039](20_TEST_ACCEPTANCE.md#at-039).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T014

**Implement server synchronization protocol** — stage 2; scope RELEASE; status **DONE**.

Dependencies: [T006](07_IMPLEMENTATION_PLAN.md#t006), [T007](07_IMPLEMENTATION_PLAN.md#t007), [T008](07_IMPLEMENTATION_PLAN.md#t008), [T009](07_IMPLEMENTATION_PLAN.md#t009).

Read before coding: [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md), [16_API_CONTRACT](16_API_CONTRACT.md).

Concrete output: Implement push per-operation responses, dependency ordering, expected versions, payload fingerprints, atomic idempotency storage and pull deltas/tombstones. Prove crash-after-commit retry produces one domain effect.

Requirements: [R-OFF-03](15_REQUIREMENTS.md#r-off-03), [R-OFF-04](15_REQUIREMENTS.md#r-off-04).

Acceptance: [AT-040](20_TEST_ACCEPTANCE.md#at-040), [AT-041](20_TEST_ACCEPTANCE.md#at-041).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T015

**Implement Android background and manual synchronization** — stage 2; scope RELEASE; status **DONE**.

Dependencies: [T013](07_IMPLEMENTATION_PLAN.md#t013), [T014](07_IMPLEMENTATION_PLAN.md#t014).

Read before coding: [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md), [04_APPFLOW](04_APPFLOW.md).

Concrete output: Drain durable outbox through unique WorkManager jobs, network constraints/backoff and foreground/manual action; handle 401/409/422/429/5xx, partial media uploads and ACK loss; persist cursors only after local transaction commit.

Requirements: [R-AUTH-03](15_REQUIREMENTS.md#r-auth-03), [R-OFF-04](15_REQUIREMENTS.md#r-off-04), [R-OFF-05](15_REQUIREMENTS.md#r-off-05), [R-OFF-06](15_REQUIREMENTS.md#r-off-06).

Acceptance: [AT-009](20_TEST_ACCEPTANCE.md#at-009), [AT-041](20_TEST_ACCEPTANCE.md#at-041), [AT-042](20_TEST_ACCEPTANCE.md#at-042), [AT-043](20_TEST_ACCEPTANCE.md#at-043).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T016

**Implement lot and lifecycle backend** — stage 2; scope RELEASE; status **DONE**.

Dependencies: [T006](07_IMPLEMENTATION_PLAN.md#t006), [T007](07_IMPLEMENTATION_PLAN.md#t007), [T008](07_IMPLEMENTATION_PLAN.md#t008), [T010](07_IMPLEMENTATION_PLAN.md#t010), [T014](07_IMPLEMENTATION_PLAN.md#t014).

Read before coding: [06_SCHEMA](06_SCHEMA.md), [04_APPFLOW](04_APPFLOW.md), [16_API_CONTRACT](16_API_CONTRACT.md).

Concrete output: Create/update/list/cancel lot commands with owner checks, positive weight and validation, immutable estimates/suggestions, location quality, photos and transition events; prohibit direct arbitrary status PATCH.

Requirements: [R-LOT-03](15_REQUIREMENTS.md#r-lot-03), [R-LOT-04](15_REQUIREMENTS.md#r-lot-04), [R-LOT-05](15_REQUIREMENTS.md#r-lot-05), [R-DATA-01](15_REQUIREMENTS.md#r-data-01).

Acceptance: [AT-013](20_TEST_ACCEPTANCE.md#at-013), [AT-014](20_TEST_ACCEPTANCE.md#at-014), [AT-015](20_TEST_ACCEPTANCE.md#at-015), [AT-053](20_TEST_ACCEPTANCE.md#at-053).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T017

**Implement approved collector onboarding and lot screens** — stage 2; scope RELEASE; status **DONE**.

Dependencies: [T002](07_IMPLEMENTATION_PLAN.md#t002), [T007](07_IMPLEMENTATION_PLAN.md#t007), [T009](07_IMPLEMENTATION_PLAN.md#t009), [T013](07_IMPLEMENTATION_PLAN.md#t013), [T015](07_IMPLEMENTATION_PLAN.md#t015), [T016](07_IMPLEMENTATION_PLAN.md#t016).

Read before coding: [05_DESIGN_STITCH](05_DESIGN_STITCH.md), [04_APPFLOW](04_APPFLOW.md), [14_TRANSLATION_AUDIO_AUDIT](14_TRANSLATION_AUDIO_AUDIT.md).

Concrete output: Implement C01–C05,C14,C15 as approved Compose screens; use Room-only reads, photo permission/import fallback, manual material selection, condition/weight, resumable drafts, local save result, language/session/sync states. Model integration arrives in T034.

Requirements: [R-GOV-02](15_REQUIREMENTS.md#r-gov-02), [R-AUTH-01](15_REQUIREMENTS.md#r-auth-01), [R-AUTH-03](15_REQUIREMENTS.md#r-auth-03), [R-LOT-01](15_REQUIREMENTS.md#r-lot-01), [R-LOT-02](15_REQUIREMENTS.md#r-lot-02), [R-LOT-03](15_REQUIREMENTS.md#r-lot-03), [R-LOT-05](15_REQUIREMENTS.md#r-lot-05), [R-OFF-01](15_REQUIREMENTS.md#r-off-01), [R-OFF-05](15_REQUIREMENTS.md#r-off-05), [R-OFF-06](15_REQUIREMENTS.md#r-off-06), [R-UX-01](15_REQUIREMENTS.md#r-ux-01).

Acceptance: [AT-002](20_TEST_ACCEPTANCE.md#at-002), [AT-007](20_TEST_ACCEPTANCE.md#at-007), [AT-009](20_TEST_ACCEPTANCE.md#at-009), [AT-011](20_TEST_ACCEPTANCE.md#at-011), [AT-012](20_TEST_ACCEPTANCE.md#at-012), [AT-013](20_TEST_ACCEPTANCE.md#at-013), [AT-015](20_TEST_ACCEPTANCE.md#at-015), [AT-038](20_TEST_ACCEPTANCE.md#at-038), [AT-042](20_TEST_ACCEPTANCE.md#at-042), [AT-043](20_TEST_ACCEPTANCE.md#at-043), [AT-051](20_TEST_ACCEPTANCE.md#at-051).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T018

**Implement price statistics and snapshot valuation** — stage 3; scope RELEASE; status **DONE**.

Dependencies: [T011](07_IMPLEMENTATION_PLAN.md#t011), [T016](07_IMPLEMENTATION_PLAN.md#t016).

Read before coding: [03_TECHSPEC](03_TECHSPEC.md), [06_SCHEMA](06_SCHEMA.md), [16_API_CONTRACT](16_API_CONTRACT.md).

Concrete output: Implement comparable observation filtering, weighted quantiles, confidence, history, sparse/stale/missing handling and per-lot immutable valuation snapshots. Publish shared fixtures for Python/Kotlin parity and preserve quote vs final amount semantics.

Requirements: [R-PRICE-02](15_REQUIREMENTS.md#r-price-02), [R-PRICE-03](15_REQUIREMENTS.md#r-price-03), [R-PRICE-04](15_REQUIREMENTS.md#r-price-04), [R-DATA-02](15_REQUIREMENTS.md#r-data-02).

Acceptance: [AT-017](20_TEST_ACCEPTANCE.md#at-017), [AT-018](20_TEST_ACCEPTANCE.md#at-018), [AT-019](20_TEST_ACCEPTANCE.md#at-019), [AT-054](20_TEST_ACCEPTANCE.md#at-054).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T019

**Implement eligible recycler matching and map data** — stage 3; scope RELEASE; status **DONE**.

Dependencies: [T012](07_IMPLEMENTATION_PLAN.md#t012), [T018](07_IMPLEMENTATION_PLAN.md#t018).

Read before coding: [03_TECHSPEC](03_TECHSPEC.md), [22_REGULATORY_SAFETY](22_REGULATORY_SAFETY.md), [16_API_CONTRACT](16_API_CONTRACT.md).

Concrete output: Implement hard route/material/status/service/weight filters, PostGIS distance, normalized scoring and explanation, missing-data rules, top candidates and no-match behavior; publish offline parity fixtures and cache policy.

Requirements: [R-REC-02](15_REQUIREMENTS.md#r-rec-02), [R-REC-04](15_REQUIREMENTS.md#r-rec-04), [R-REC-05](15_REQUIREMENTS.md#r-rec-05), [R-REC-06](15_REQUIREMENTS.md#r-rec-06).

Acceptance: [AT-022](20_TEST_ACCEPTANCE.md#at-022), [AT-024](20_TEST_ACCEPTANCE.md#at-024), [AT-025](20_TEST_ACCEPTANCE.md#at-025), [AT-026](20_TEST_ACCEPTANCE.md#at-026).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T020

**Implement approved collector price and recycler views** — stage 3; scope RELEASE; status **DONE**.

Dependencies: [T002](07_IMPLEMENTATION_PLAN.md#t002), [T017](07_IMPLEMENTATION_PLAN.md#t017), [T018](07_IMPLEMENTATION_PLAN.md#t018), [T019](07_IMPLEMENTATION_PLAN.md#t019), [T021](07_IMPLEMENTATION_PLAN.md#t021).

Read before coding: [05_DESIGN_STITCH](05_DESIGN_STITCH.md), [04_APPFLOW](04_APPFLOW.md).

Concrete output: Implement C06–C09: board/trends, source details, observation entry, estimates, quote comparisons, directory/list/details and online map; cache age, no price/no match and permission-denied states; selection offline is intent only.

Requirements: [R-GOV-02](15_REQUIREMENTS.md#r-gov-02), [R-PRICE-01](15_REQUIREMENTS.md#r-price-01), [R-PRICE-02](15_REQUIREMENTS.md#r-price-02), [R-PRICE-03](15_REQUIREMENTS.md#r-price-03), [R-PRICE-04](15_REQUIREMENTS.md#r-price-04), [R-REC-05](15_REQUIREMENTS.md#r-rec-05), [R-REC-06](15_REQUIREMENTS.md#r-rec-06), [R-OFF-01](15_REQUIREMENTS.md#r-off-01).

Acceptance: [AT-002](20_TEST_ACCEPTANCE.md#at-002), [AT-016](20_TEST_ACCEPTANCE.md#at-016), [AT-017](20_TEST_ACCEPTANCE.md#at-017), [AT-018](20_TEST_ACCEPTANCE.md#at-018), [AT-019](20_TEST_ACCEPTANCE.md#at-019), [AT-025](20_TEST_ACCEPTANCE.md#at-025), [AT-026](20_TEST_ACCEPTANCE.md#at-026), [AT-038](20_TEST_ACCEPTANCE.md#at-038).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T021

**Implement recycler profile and offer workflows** — stage 3; scope RELEASE; status **DONE**.

Dependencies: [T007](07_IMPLEMENTATION_PLAN.md#t007), [T016](07_IMPLEMENTATION_PLAN.md#t016), [T019](07_IMPLEMENTATION_PLAN.md#t019).

Read before coding: [16_API_CONTRACT](16_API_CONTRACT.md), [04_APPFLOW](04_APPFLOW.md), [06_SCHEMA](06_SCHEMA.md).

Concrete output: Implement facility-user linkage, self-declared operational profile, material/rate/pickup updates, incoming requests, offer/reject/expiry, collector acceptance with one active agreement, cancellation and immutable terms.

Requirements: [R-PRICE-04](15_REQUIREMENTS.md#r-price-04), [R-REC-03](15_REQUIREMENTS.md#r-rec-03), [R-OFFER-01](15_REQUIREMENTS.md#r-offer-01), [R-OFFER-02](15_REQUIREMENTS.md#r-offer-02), [R-DATA-03](15_REQUIREMENTS.md#r-data-03).

Acceptance: [AT-019](20_TEST_ACCEPTANCE.md#at-019), [AT-023](20_TEST_ACCEPTANCE.md#at-023), [AT-027](20_TEST_ACCEPTANCE.md#at-027), [AT-028](20_TEST_ACCEPTANCE.md#at-028), [AT-055](20_TEST_ACCEPTANCE.md#at-055).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T022

**Implement approved recycler console and phone layout** — stage 3; scope RELEASE; status **DONE**.

Dependencies: [T002](07_IMPLEMENTATION_PLAN.md#t002), [T021](07_IMPLEMENTATION_PLAN.md#t021).

Read before coding: [05_DESIGN_STITCH](05_DESIGN_STITCH.md), [04_APPFLOW](04_APPFLOW.md), [12_GUARDRAILS](12_GUARDRAILS.md).

Concrete output: Implement R01–R03,R06,R07 responsive React/Vite views for authorized facility users; incoming/lot evidence/offer/profile/history interactions; R07 export wiring is completed in T031; work on borrowed second Android phone without a separate recycler APK.

Requirements: [R-GOV-02](15_REQUIREMENTS.md#r-gov-02), [R-REC-03](15_REQUIREMENTS.md#r-rec-03), [R-OFFER-01](15_REQUIREMENTS.md#r-offer-01).

Acceptance: [AT-002](20_TEST_ACCEPTANCE.md#at-002), [AT-023](20_TEST_ACCEPTANCE.md#at-023), [AT-027](20_TEST_ACCEPTANCE.md#at-027).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T023

**Implement handover proposals and confirmations** — stage 4; scope RELEASE; status **DONE**.

Dependencies: [T014](07_IMPLEMENTATION_PLAN.md#t014), [T021](07_IMPLEMENTATION_PLAN.md#t021).

Read before coding: [04_APPFLOW](04_APPFLOW.md), [16_API_CONTRACT](16_API_CONTRACT.md), [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md).

Concrete output: Implement pending proposal, canonical payload/hash/event chain, authenticated recycler confirmation, collector acknowledgement of changes, duplicate-safe outcome, disputes and immutable revision links; create minimal public verification response.

Requirements: [R-REC-04](15_REQUIREMENTS.md#r-rec-04), [R-OFFER-02](15_REQUIREMENTS.md#r-offer-02), [R-HAND-01](15_REQUIREMENTS.md#r-hand-01), [R-HAND-03](15_REQUIREMENTS.md#r-hand-03), [R-HAND-04](15_REQUIREMENTS.md#r-hand-04), [R-HAND-05](15_REQUIREMENTS.md#r-hand-05), [R-DATA-05](15_REQUIREMENTS.md#r-data-05), [R-REG-01](15_REQUIREMENTS.md#r-reg-01).

Acceptance: [AT-024](20_TEST_ACCEPTANCE.md#at-024), [AT-028](20_TEST_ACCEPTANCE.md#at-028), [AT-029](20_TEST_ACCEPTANCE.md#at-029), [AT-031](20_TEST_ACCEPTANCE.md#at-031), [AT-032](20_TEST_ACCEPTANCE.md#at-032), [AT-033](20_TEST_ACCEPTANCE.md#at-033), [AT-057](20_TEST_ACCEPTANCE.md#at-057), [AT-071](20_TEST_ACCEPTANCE.md#at-071).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T024

**Implement approved offline QR and collector receipt** — stage 4; scope RELEASE; status **DONE**.

Dependencies: [T002](07_IMPLEMENTATION_PLAN.md#t002), [T017](07_IMPLEMENTATION_PLAN.md#t017), [T023](07_IMPLEMENTATION_PLAN.md#t023).

Read before coding: [05_DESIGN_STITCH](05_DESIGN_STITCH.md), [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md), [16_API_CONTRACT](16_API_CONTRACT.md).

Concrete output: Implement C10,C11,C16: local pending handover with photo/weight/location/time, SHA-256 and QR, Android PdfDocument, share and passport timeline. Clearly distinguish pending local hash check from server-confirmed record and protect PII.

Requirements: [R-GOV-02](15_REQUIREMENTS.md#r-gov-02), [R-LOT-04](15_REQUIREMENTS.md#r-lot-04), [R-HAND-01](15_REQUIREMENTS.md#r-hand-01), [R-HAND-03](15_REQUIREMENTS.md#r-hand-03), [R-HAND-06](15_REQUIREMENTS.md#r-hand-06), [R-REG-01](15_REQUIREMENTS.md#r-reg-01).

Acceptance: [AT-002](20_TEST_ACCEPTANCE.md#at-002), [AT-014](20_TEST_ACCEPTANCE.md#at-014), [AT-029](20_TEST_ACCEPTANCE.md#at-029), [AT-031](20_TEST_ACCEPTANCE.md#at-031), [AT-034](20_TEST_ACCEPTANCE.md#at-034), [AT-071](20_TEST_ACCEPTANCE.md#at-071).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T025

**Implement approved second-phone QR confirmation** — stage 4; scope RELEASE; status **DONE**.

Dependencies: [T002](07_IMPLEMENTATION_PLAN.md#t002), [T022](07_IMPLEMENTATION_PLAN.md#t022), [T023](07_IMPLEMENTATION_PLAN.md#t023).

Read before coding: [05_DESIGN_STITCH](05_DESIGN_STITCH.md), [04_APPFLOW](04_APPFLOW.md), [16_API_CONTRACT](16_API_CONTRACT.md).

Concrete output: Implement R04,R05,V01 in responsive web; HTTPS camera scan plus reference-entry fallback, unknown-unsynced QR state, review/confirm measured terms, pending collector acknowledgement, public redacted verification and replay/conflict tests.

Requirements: [R-GOV-02](15_REQUIREMENTS.md#r-gov-02), [R-HAND-02](15_REQUIREMENTS.md#r-hand-02), [R-HAND-04](15_REQUIREMENTS.md#r-hand-04), [R-HAND-05](15_REQUIREMENTS.md#r-hand-05), [R-HAND-06](15_REQUIREMENTS.md#r-hand-06).

Acceptance: [AT-002](20_TEST_ACCEPTANCE.md#at-002), [AT-030](20_TEST_ACCEPTANCE.md#at-030), [AT-032](20_TEST_ACCEPTANCE.md#at-032), [AT-033](20_TEST_ACCEPTANCE.md#at-033), [AT-034](20_TEST_ACCEPTANCE.md#at-034).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T026

**Implement payment assertions and earnings projections** — stage 4; scope RELEASE; status **DONE**.

Dependencies: [T023](07_IMPLEMENTATION_PLAN.md#t023).

Read before coding: [06_SCHEMA](06_SCHEMA.md), [04_APPFLOW](04_APPFLOW.md), [16_API_CONTRACT](16_API_CONTRACT.md).

Concrete output: Record cash/UPI/other payment assertions with actor/time and acknowledgement/dispute; partial amounts and append-only reversals; derive gross/paid/pending totals without double counting; close only at confirmed receipt and acknowledged settled payment.

Requirements: [R-PAY-01](15_REQUIREMENTS.md#r-pay-01), [R-PAY-02](15_REQUIREMENTS.md#r-pay-02), [R-PAY-03](15_REQUIREMENTS.md#r-pay-03), [R-DATA-04](15_REQUIREMENTS.md#r-data-04).

Acceptance: [AT-035](20_TEST_ACCEPTANCE.md#at-035), [AT-036](20_TEST_ACCEPTANCE.md#at-036), [AT-037](20_TEST_ACCEPTANCE.md#at-037), [AT-056](20_TEST_ACCEPTANCE.md#at-056).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T027

**Implement approved ledger and payment screens** — stage 4; scope RELEASE; status **DONE**.

Dependencies: [T002](07_IMPLEMENTATION_PLAN.md#t002), [T024](07_IMPLEMENTATION_PLAN.md#t024), [T026](07_IMPLEMENTATION_PLAN.md#t026).

Read before coding: [05_DESIGN_STITCH](05_DESIGN_STITCH.md), [04_APPFLOW](04_APPFLOW.md).

Concrete output: Implement C12,C13 and R05 payment/history portions; monthly/filter summaries, transaction detail, offline pending payment assertion, dues and disagreement; no implication that the app executes or bank-verifies money transfer.

Requirements: [R-GOV-02](15_REQUIREMENTS.md#r-gov-02), [R-HAND-05](15_REQUIREMENTS.md#r-hand-05), [R-PAY-01](15_REQUIREMENTS.md#r-pay-01), [R-PAY-02](15_REQUIREMENTS.md#r-pay-02), [R-PAY-03](15_REQUIREMENTS.md#r-pay-03).

Acceptance: [AT-002](20_TEST_ACCEPTANCE.md#at-002), [AT-033](20_TEST_ACCEPTANCE.md#at-033), [AT-035](20_TEST_ACCEPTANCE.md#at-035), [AT-036](20_TEST_ACCEPTANCE.md#at-036), [AT-037](20_TEST_ACCEPTANCE.md#at-037).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T028

**Implement data-quality and anomaly rules** — stage 5; scope RELEASE; status **DONE**.

Dependencies: [T018](07_IMPLEMENTATION_PLAN.md#t018), [T019](07_IMPLEMENTATION_PLAN.md#t019), [T023](07_IMPLEMENTATION_PLAN.md#t023), [T026](07_IMPLEMENTATION_PLAN.md#t026).

Read before coding: [03_TECHSPEC](03_TECHSPEC.md), [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md), [MONITORING](MONITORING.md).

Concrete output: Implement missing/invalid/duplicate/stale/inconsistent checks, price bounds, weight variance, image reuse and repeated events; record severity/reason/reviewer/resolution; no fraud accusation or destructive auto-correction.

Requirements: [R-PRICE-05](15_REQUIREMENTS.md#r-price-05), [R-HAND-05](15_REQUIREMENTS.md#r-hand-05), [R-ADMIN-02](15_REQUIREMENTS.md#r-admin-02), [R-OPS-04](15_REQUIREMENTS.md#r-ops-04).

Acceptance: [AT-020](20_TEST_ACCEPTANCE.md#at-020), [AT-033](20_TEST_ACCEPTANCE.md#at-033), [AT-065](20_TEST_ACCEPTANCE.md#at-065), [AT-077](20_TEST_ACCEPTANCE.md#at-077).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T029

**Implement admin maintenance and metrics APIs** — stage 5; scope RELEASE; status **DONE**.

Dependencies: [T028](07_IMPLEMENTATION_PLAN.md#t028).

Read before coding: [16_API_CONTRACT](16_API_CONTRACT.md), [06_SCHEMA](06_SCHEMA.md), [MONITORING](MONITORING.md).

Concrete output: Implement admin directory review, material/alias/safety maintenance, price moderation, collector minimal view, event search, source/quality filters and aggregate metrics from persisted events; exclude demo data from real-impact totals.

Requirements: [R-REC-02](15_REQUIREMENTS.md#r-rec-02), [R-DATA-03](15_REQUIREMENTS.md#r-data-03), [R-DATA-08](15_REQUIREMENTS.md#r-data-08), [R-ADMIN-01](15_REQUIREMENTS.md#r-admin-01), [R-ADMIN-03](15_REQUIREMENTS.md#r-admin-03), [R-OPS-04](15_REQUIREMENTS.md#r-ops-04).

Acceptance: [AT-022](20_TEST_ACCEPTANCE.md#at-022), [AT-055](20_TEST_ACCEPTANCE.md#at-055), [AT-060](20_TEST_ACCEPTANCE.md#at-060), [AT-064](20_TEST_ACCEPTANCE.md#at-064), [AT-066](20_TEST_ACCEPTANCE.md#at-066), [AT-077](20_TEST_ACCEPTANCE.md#at-077).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T030

**Implement approved admin/data-quality dashboard** — stage 5; scope RELEASE; status **DONE**.

Dependencies: [T002](07_IMPLEMENTATION_PLAN.md#t002), [T029](07_IMPLEMENTATION_PLAN.md#t029).

Read before coding: [05_DESIGN_STITCH](05_DESIGN_STITCH.md), [04_APPFLOW](04_APPFLOW.md), [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Concrete output: Implement A01–A07: overview, collectors, facility verification, price/material/safety source editors, traceability search, quality queue and secondary-research evidence links. All counts/drill-downs come from APIs.

Requirements: [R-GOV-02](15_REQUIREMENTS.md#r-gov-02), [R-PRICE-05](15_REQUIREMENTS.md#r-price-05), [R-ADMIN-01](15_REQUIREMENTS.md#r-admin-01), [R-ADMIN-02](15_REQUIREMENTS.md#r-admin-02), [R-ADMIN-03](15_REQUIREMENTS.md#r-admin-03).

Acceptance: [AT-002](20_TEST_ACCEPTANCE.md#at-002), [AT-020](20_TEST_ACCEPTANCE.md#at-020), [AT-064](20_TEST_ACCEPTANCE.md#at-064), [AT-065](20_TEST_ACCEPTANCE.md#at-065), [AT-066](20_TEST_ACCEPTANCE.md#at-066).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T031

**Implement seven dataset exports and data lineage** — stage 5; scope RELEASE; status **DONE**.

Dependencies: [T010](07_IMPLEMENTATION_PLAN.md#t010), [T011](07_IMPLEMENTATION_PLAN.md#t011), [T012](07_IMPLEMENTATION_PLAN.md#t012), [T023](07_IMPLEMENTATION_PLAN.md#t023), [T026](07_IMPLEMENTATION_PLAN.md#t026), [T029](07_IMPLEMENTATION_PLAN.md#t029), [T002](07_IMPLEMENTATION_PLAN.md#t002), [T022](07_IMPLEMENTATION_PLAN.md#t022), [T030](07_IMPLEMENTATION_PLAN.md#t030).

Read before coding: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md), [16_API_CONTRACT](16_API_CONTRACT.md), [06_SCHEMA](06_SCHEMA.md).

Concrete output: Export all seven families as versioned CSV/JSON with provenance, safe redaction and manifests; produce handover PDF/CSV procurement logs labelled platform records; transaction outcomes feed reviewed price observations exactly once. Wire approved R07/A07 export downloads and manifest/data-card views end to end; verify actual files and permissions.

Requirements: [R-HAND-06](15_REQUIREMENTS.md#r-hand-06), [R-DATA-01](15_REQUIREMENTS.md#r-data-01), [R-DATA-02](15_REQUIREMENTS.md#r-data-02), [R-DATA-03](15_REQUIREMENTS.md#r-data-03), [R-DATA-04](15_REQUIREMENTS.md#r-data-04), [R-DATA-05](15_REQUIREMENTS.md#r-data-05), [R-DATA-06](15_REQUIREMENTS.md#r-data-06), [R-DATA-08](15_REQUIREMENTS.md#r-data-08), [R-DATA-09](15_REQUIREMENTS.md#r-data-09), [R-DATA-11](15_REQUIREMENTS.md#r-data-11), [R-REG-01](15_REQUIREMENTS.md#r-reg-01).

Acceptance: [AT-034](20_TEST_ACCEPTANCE.md#at-034), [AT-053](20_TEST_ACCEPTANCE.md#at-053), [AT-054](20_TEST_ACCEPTANCE.md#at-054), [AT-055](20_TEST_ACCEPTANCE.md#at-055), [AT-056](20_TEST_ACCEPTANCE.md#at-056), [AT-057](20_TEST_ACCEPTANCE.md#at-057), [AT-058](20_TEST_ACCEPTANCE.md#at-058), [AT-060](20_TEST_ACCEPTANCE.md#at-060), [AT-061](20_TEST_ACCEPTANCE.md#at-061), [AT-063](20_TEST_ACCEPTANCE.md#at-063), [AT-071](20_TEST_ACCEPTANCE.md#at-071).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T032

**Curate licensed public image dataset** — stage 5; scope RELEASE; status **DONE**.

Dependencies: [T004](07_IMPLEMENTATION_PLAN.md#t004), [T005](07_IMPLEMENTATION_PLAN.md#t005), [T010](07_IMPLEMENTATION_PLAN.md#t010).

Read before coding: [19_AI_ML](19_AI_ML.md), [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md).

Concrete output: Select exact licensed datasets, save licence evidence and hashes, audit class relevance, deduplicate and group physical objects/source sequences into deterministic splits; document class gaps and no field-image claims.

Requirements: [R-ML-01](15_REQUIREMENTS.md#r-ml-01), [R-DATA-07](15_REQUIREMENTS.md#r-data-07).

Acceptance: [AT-044](20_TEST_ACCEPTANCE.md#at-044), [AT-059](20_TEST_ACCEPTANCE.md#at-059).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T033

**Train evaluate and export on-device model** — stage 5; scope RELEASE; status **DONE**.

Dependencies: [T032](07_IMPLEMENTATION_PLAN.md#t032).

Read before coding: [19_AI_ML](19_AI_ML.md), [20_TEST_ACCEPTANCE](20_TEST_ACCEPTANCE.md).

Concrete output: Train Keras MobileNetV3-Small, record seeded configuration, validation threshold, untouched-test metrics/confusion matrix, quantized LiteRT export parity and model card. Record failure honestly; no invented accuracy or borrowed benchmark results.

Requirements: [R-ML-02](15_REQUIREMENTS.md#r-ml-02), [R-DATA-07](15_REQUIREMENTS.md#r-data-07).

Acceptance: [AT-045](20_TEST_ACCEPTANCE.md#at-045), [AT-059](20_TEST_ACCEPTANCE.md#at-059).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T034

**Integrate classifier into approved Android flow** — stage 5; scope RELEASE; status **DONE**.

Dependencies: [T002](07_IMPLEMENTATION_PLAN.md#t002), [T017](07_IMPLEMENTATION_PLAN.md#t017), [T033](07_IMPLEMENTATION_PLAN.md#t033).

Read before coding: [19_AI_ML](19_AI_ML.md), [05_DESIGN_STITCH](05_DESIGN_STITCH.md).

Concrete output: Bundle model/labels/preprocessing/threshold/checksum, run off main thread, show real confidence and confirm/change/abstain; preserve suggestion and correction; test airplane mode, unsupported class, corrupt model and low-memory fallback.

Requirements: [R-GOV-02](15_REQUIREMENTS.md#r-gov-02), [R-ML-03](15_REQUIREMENTS.md#r-ml-03), [R-ML-04](15_REQUIREMENTS.md#r-ml-04).

Acceptance: [AT-002](20_TEST_ACCEPTANCE.md#at-002), [AT-046](20_TEST_ACCEPTANCE.md#at-046), [AT-047](20_TEST_ACCEPTANCE.md#at-047).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T035

**Create contextual safety content and review path** — stage 5; scope RELEASE; status **DONE**.

Dependencies: [T004](07_IMPLEMENTATION_PLAN.md#t004), [T010](07_IMPLEMENTATION_PLAN.md#t010).

Read before coding: [22_REGULATORY_SAFETY](22_REGULATORY_SAFETY.md), [14_TRANSLATION_AUDIO_AUDIT](14_TRANSLATION_AUDIO_AUDIT.md).

Concrete output: Write short source-backed hi/mr/en material-specific safety cards and pictogram briefs for owner Stitch generation; version content, review hazards/routes and provide non-instructional battery/CRT warnings; no unlicensed image assets.

Requirements: [R-SAFE-01](15_REQUIREMENTS.md#r-safe-01).

Acceptance: [AT-048](20_TEST_ACCEPTANCE.md#at-048).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T036

**Complete language resources and accessible interaction** — stage 5; scope RELEASE; status **DONE**.

Dependencies: [T017](07_IMPLEMENTATION_PLAN.md#t017), [T020](07_IMPLEMENTATION_PLAN.md#t020), [T024](07_IMPLEMENTATION_PLAN.md#t024), [T027](07_IMPLEMENTATION_PLAN.md#t027), [T035](07_IMPLEMENTATION_PLAN.md#t035).

Read before coding: [14_TRANSLATION_AUDIO_AUDIT](14_TRANSLATION_AUDIO_AUDIT.md), [05_DESIGN_STITCH](05_DESIGN_STITCH.md).

Concrete output: Implement all collector hi/mr/en strings, material aliases, accessibility labels, plurals/currency/units and numeral preference; preserve chosen language offline/restart; no hardcoded English critical errors.

Requirements: [R-LANG-01](15_REQUIREMENTS.md#r-lang-01), [R-UX-01](15_REQUIREMENTS.md#r-ux-01).

Acceptance: [AT-049](20_TEST_ACCEPTANCE.md#at-049), [AT-051](20_TEST_ACCEPTANCE.md#at-051).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T037

**Generate and wire offline Hindi/Marathi audio** — stage 5; scope RELEASE; status **DONE**.

Dependencies: [T035](07_IMPLEMENTATION_PLAN.md#t035), [T036](07_IMPLEMENTATION_PLAN.md#t036), [T005](07_IMPLEMENTATION_PLAN.md#t005).

Read before coding: [14_TRANSLATION_AUDIO_AUDIT](14_TRANSLATION_AUDIO_AUDIT.md), [19_AI_ML](19_AI_ML.md).

Concrete output: Use free licensed voice workflow for bundled prompts and number/unit grammar; inventory rights/text/checksum/duration; wire tap-to-hear dynamic ranges, rupees/paise, per-kg, pending/success/safety; verify no runtime cloud call. T005 supplies shared licence/source-review tooling; image-dataset work is not an audio dependency.

Requirements: [R-LANG-02](15_REQUIREMENTS.md#r-lang-02), [R-OPS-03](15_REQUIREMENTS.md#r-ops-03).

Acceptance: [AT-050](20_TEST_ACCEPTANCE.md#at-050), [AT-076](20_TEST_ACCEPTANCE.md#at-076).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T038

**Implement illustrative economics model** — stage 5; scope RELEASE; status **DONE**.

Dependencies: [T004](07_IMPLEMENTATION_PLAN.md#t004), [T011](07_IMPLEMENTATION_PLAN.md#t011), [T026](07_IMPLEMENTATION_PLAN.md#t026).

Read before coding: [23_UNIT_ECONOMICS](23_UNIT_ECONOMICS.md), [16_API_CONTRACT](16_API_CONTRACT.md).

Concrete output: Create transparent current/platform same-lot calculator and attributed assumptions; acquisition/transport/handling/rejections/time/payment-delay sensitivity, negative/zero baseline behavior and hypothetical downstream fee/cost sustainability; keep separate from realized earnings.

Requirements: [R-ECON-01](15_REQUIREMENTS.md#r-econ-01), [R-ECON-02](15_REQUIREMENTS.md#r-econ-02).

Acceptance: [AT-067](20_TEST_ACCEPTANCE.md#at-067), [AT-068](20_TEST_ACCEPTANCE.md#at-068).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T039

**Implement approved economics and safety views** — stage 5; scope RELEASE; status **DONE**.

Dependencies: [T002](07_IMPLEMENTATION_PLAN.md#t002), [T030](07_IMPLEMENTATION_PLAN.md#t030), [T035](07_IMPLEMENTATION_PLAN.md#t035), [T037](07_IMPLEMENTATION_PLAN.md#t037), [T038](07_IMPLEMENTATION_PLAN.md#t038).

Read before coding: [05_DESIGN_STITCH](05_DESIGN_STITCH.md), [23_UNIT_ECONOMICS](23_UNIT_ECONOMICS.md), [04_APPFLOW](04_APPFLOW.md).

Concrete output: Implement C17 safety hub/context cards and U01 interactive web economics, linked from admin/collector help where approved; clear illustrative labels and source drill-down; sliders/inputs update results; no preset claimed uplift.

Requirements: [R-GOV-02](15_REQUIREMENTS.md#r-gov-02), [R-SAFE-01](15_REQUIREMENTS.md#r-safe-01), [R-ECON-01](15_REQUIREMENTS.md#r-econ-01).

Acceptance: [AT-002](20_TEST_ACCEPTANCE.md#at-002), [AT-048](20_TEST_ACCEPTANCE.md#at-048), [AT-067](20_TEST_ACCEPTANCE.md#at-067).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T040

**Verify security privacy and abuse boundaries** — stage 6; scope RELEASE; status **DONE**.

Dependencies: [T025](07_IMPLEMENTATION_PLAN.md#t025), [T027](07_IMPLEMENTATION_PLAN.md#t027), [T030](07_IMPLEMENTATION_PLAN.md#t030), [T031](07_IMPLEMENTATION_PLAN.md#t031).

Read before coding: [12_GUARDRAILS](12_GUARDRAILS.md), [11_SECRETS_CHECKLIST](11_SECRETS_CHECKLIST.md), [20_TEST_ACCEPTANCE](20_TEST_ACCEPTANCE.md).

Concrete output: Run owner/role/IDOR/replay/rate-limit/input/file-access tests; validate demo isolation, redacted QR/exports, no client secrets, token expiry/offline behavior, image EXIF removal, retention and backup controls; document residual limitations.

Requirements: [R-AUTH-02](15_REQUIREMENTS.md#r-auth-02), [R-AUTH-04](15_REQUIREMENTS.md#r-auth-04), [R-HAND-04](15_REQUIREMENTS.md#r-hand-04), [R-DATA-06](15_REQUIREMENTS.md#r-data-06), [R-DATA-08](15_REQUIREMENTS.md#r-data-08), [R-SEC-01](15_REQUIREMENTS.md#r-sec-01), [R-SEC-02](15_REQUIREMENTS.md#r-sec-02).

Acceptance: [AT-008](20_TEST_ACCEPTANCE.md#at-008), [AT-010](20_TEST_ACCEPTANCE.md#at-010), [AT-032](20_TEST_ACCEPTANCE.md#at-032), [AT-058](20_TEST_ACCEPTANCE.md#at-058), [AT-060](20_TEST_ACCEPTANCE.md#at-060), [AT-072](20_TEST_ACCEPTANCE.md#at-072), [AT-073](20_TEST_ACCEPTANCE.md#at-073).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T041

**Deploy hosted API database storage and web** — stage 6; scope RELEASE; status **DONE**.

Dependencies: [T007](07_IMPLEMENTATION_PLAN.md#t007), [T008](07_IMPLEMENTATION_PLAN.md#t008), [T025](07_IMPLEMENTATION_PLAN.md#t025), [T030](07_IMPLEMENTATION_PLAN.md#t030), [T039](07_IMPLEMENTATION_PLAN.md#t039), [T040](07_IMPLEMENTATION_PLAN.md#t040).

Read before coding: [DEPLOYMENT](DEPLOYMENT.md), [11_SECRETS_CHECKLIST](11_SECRETS_CHECKLIST.md), [25_RELEASE_CHECKLIST](25_RELEASE_CHECKLIST.md).

Concrete output: Prepare reproducible Render/Supabase/Pages configuration, verify current free-plan terms and account settings, apply migrations, private storage/CORS/TLS, release API URL and health check; validate over cellular/outside LAN. Publishing requires the owner's existing or explicit deployment authorization.

Requirements: [R-SEC-01](15_REQUIREMENTS.md#r-sec-01), [R-OPS-01](15_REQUIREMENTS.md#r-ops-01), [R-OPS-03](15_REQUIREMENTS.md#r-ops-03).

Acceptance: [AT-072](20_TEST_ACCEPTANCE.md#at-072), [AT-074](20_TEST_ACCEPTANCE.md#at-074), [AT-076](20_TEST_ACCEPTANCE.md#at-076).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T042

**Prove local demo fallback and restore** — stage 6; scope RELEASE; status **DONE**.

Dependencies: [T024](07_IMPLEMENTATION_PLAN.md#t024), [T027](07_IMPLEMENTATION_PLAN.md#t027), [T031](07_IMPLEMENTATION_PLAN.md#t031), [T040](07_IMPLEMENTATION_PLAN.md#t040).

Read before coding: [DEPLOYMENT](DEPLOYMENT.md), [13_RECOVERY](13_RECOVERY.md), [MONITORING](MONITORING.md).

Concrete output: Run same contracts with Docker PostgreSQL/PostGIS and media volume, real-phone LAN debug networking, localhost/HTTPS QR fallback; backup and restore database+media+manifests; test without internet. Do not expose debug cleartext in release.

Requirements: [R-SEC-02](15_REQUIREMENTS.md#r-sec-02), [R-OPS-02](15_REQUIREMENTS.md#r-ops-02), [R-OPS-04](15_REQUIREMENTS.md#r-ops-04).

Acceptance: [AT-073](20_TEST_ACCEPTANCE.md#at-073), [AT-075](20_TEST_ACCEPTANCE.md#at-075), [AT-077](20_TEST_ACCEPTANCE.md#at-077).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T043

**Run cross-surface integration and fault acceptance** — stage 6; scope RELEASE; status **DONE**.

Dependencies: [T015](07_IMPLEMENTATION_PLAN.md#t015), [T025](07_IMPLEMENTATION_PLAN.md#t025), [T027](07_IMPLEMENTATION_PLAN.md#t027), [T030](07_IMPLEMENTATION_PLAN.md#t030), [T031](07_IMPLEMENTATION_PLAN.md#t031), [T034](07_IMPLEMENTATION_PLAN.md#t034), [T037](07_IMPLEMENTATION_PLAN.md#t037), [T039](07_IMPLEMENTATION_PLAN.md#t039), [T040](07_IMPLEMENTATION_PLAN.md#t040).

Read before coding: [20_TEST_ACCEPTANCE](20_TEST_ACCEPTANCE.md), [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md).

Concrete output: Run deterministic domain tests, price/match/hash parity, offline crash/retry/media/conflict/auth/device-clock cases and complete collector→recycler→ledger→admin journeys. Store logs and case IDs, fix failures and rerun affected checks.

Requirements: [R-HAND-03](15_REQUIREMENTS.md#r-hand-03), [R-OFF-02](15_REQUIREMENTS.md#r-off-02), [R-OFF-03](15_REQUIREMENTS.md#r-off-03), [R-OFF-04](15_REQUIREMENTS.md#r-off-04), [R-OFF-05](15_REQUIREMENTS.md#r-off-05), [R-OFF-06](15_REQUIREMENTS.md#r-off-06), [R-DATA-10](15_REQUIREMENTS.md#r-data-10), [R-QA-01](15_REQUIREMENTS.md#r-qa-01).

Acceptance: [AT-031](20_TEST_ACCEPTANCE.md#at-031), [AT-039](20_TEST_ACCEPTANCE.md#at-039), [AT-040](20_TEST_ACCEPTANCE.md#at-040), [AT-041](20_TEST_ACCEPTANCE.md#at-041), [AT-042](20_TEST_ACCEPTANCE.md#at-042), [AT-043](20_TEST_ACCEPTANCE.md#at-043), [AT-062](20_TEST_ACCEPTANCE.md#at-062), [AT-078](20_TEST_ACCEPTANCE.md#at-078).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T044

**Perform real-device and two-device usability tests** — stage 6; scope RELEASE; status **DONE**.

Dependencies: [T041](07_IMPLEMENTATION_PLAN.md#t041), [T042](07_IMPLEMENTATION_PLAN.md#t042), [T043](07_IMPLEMENTATION_PLAN.md#t043).

Read before coding: [20_TEST_ACCEPTANCE](20_TEST_ACCEPTANCE.md), [24_DEMO_PRESENTATION](24_DEMO_PRESENTATION.md).

Concrete output: Owner uses real collector phone plus borrowed second Android browser; test camera/GPS/denial/restart/airplane mode/background/manual sync/QR, Hindi/Marathi and representative scenario usability. Identify tests as owner scenario tests, not collector fieldwork.

Requirements: [R-HAND-02](15_REQUIREMENTS.md#r-hand-02), [R-ML-03](15_REQUIREMENTS.md#r-ml-03), [R-UX-01](15_REQUIREMENTS.md#r-ux-01), [R-OPS-01](15_REQUIREMENTS.md#r-ops-01), [R-QA-01](15_REQUIREMENTS.md#r-qa-01), [R-QA-02](15_REQUIREMENTS.md#r-qa-02).

Acceptance: [AT-030](20_TEST_ACCEPTANCE.md#at-030), [AT-046](20_TEST_ACCEPTANCE.md#at-046), [AT-051](20_TEST_ACCEPTANCE.md#at-051), [AT-074](20_TEST_ACCEPTANCE.md#at-074), [AT-078](20_TEST_ACCEPTANCE.md#at-078), [AT-079](20_TEST_ACCEPTANCE.md#at-079).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T045

**Measure entry-level performance and artifact size** — stage 6; scope RELEASE; status **DONE**.

Dependencies: [T034](07_IMPLEMENTATION_PLAN.md#t034), [T037](07_IMPLEMENTATION_PLAN.md#t037), [T043](07_IMPLEMENTATION_PLAN.md#t043).

Read before coding: [03_TECHSPEC](03_TECHSPEC.md), [19_AI_ML](19_AI_ML.md), [20_TEST_ACCEPTANCE](20_TEST_ACCEPTANCE.md).

Concrete output: Measure cold/cached launch, local save, compression, LiteRT latency, memory and APK including model/audio on named device; record p50/p95 and regressions, optimize lazy maps/assets without dropping required content.

Requirements: [R-ML-04](15_REQUIREMENTS.md#r-ml-04), [R-UX-02](15_REQUIREMENTS.md#r-ux-02).

Acceptance: [AT-047](20_TEST_ACCEPTANCE.md#at-047), [AT-052](20_TEST_ACCEPTANCE.md#at-052).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T046

**Audit all translations and audio on device** — stage 6; scope RELEASE; status **IN_PROGRESS**.

Dependencies: [T036](07_IMPLEMENTATION_PLAN.md#t036), [T037](07_IMPLEMENTATION_PLAN.md#t037), [T039](07_IMPLEMENTATION_PLAN.md#t039), [T044](07_IMPLEMENTATION_PLAN.md#t044).

Read before coding: [14_TRANSLATION_AUDIO_AUDIT](14_TRANSLATION_AUDIO_AUDIT.md), [20_TEST_ACCEPTANCE](20_TEST_ACCEPTANCE.md).

Concrete output: Check key parity, Devanagari rendering, large text/TalkBack, numeric/range pronunciation, all error/pending/review states and offline audio; native-speaker review where available remains explicitly unverified until performed.

Requirements: [R-LANG-01](15_REQUIREMENTS.md#r-lang-01), [R-LANG-02](15_REQUIREMENTS.md#r-lang-02), [R-UX-01](15_REQUIREMENTS.md#r-ux-01).

Acceptance: [AT-049](20_TEST_ACCEPTANCE.md#at-049), [AT-050](20_TEST_ACCEPTANCE.md#at-050), [AT-051](20_TEST_ACCEPTANCE.md#at-051).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T047

**Freeze dataset and model evidence package** — stage 7; scope RELEASE; status **IN_PROGRESS**.

Dependencies: [T031](07_IMPLEMENTATION_PLAN.md#t031), [T033](07_IMPLEMENTATION_PLAN.md#t033), [T044](07_IMPLEMENTATION_PLAN.md#t044), [T045](07_IMPLEMENTATION_PLAN.md#t045), [T046](07_IMPLEMENTATION_PLAN.md#t046).

Read before coding: [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md), [19_AI_ML](19_AI_ML.md), [21_RESEARCH_EVIDENCE](21_RESEARCH_EVIDENCE.md).

Concrete output: Produce release manifests, source/licence ledger, seven data cards, model card with actual results, data lifecycle demonstration, limitations and desk-research cards; distinguish facts/assumptions/demo rows and still-unmet primary fieldwork.

Requirements: [R-ML-01](15_REQUIREMENTS.md#r-ml-01), [R-ML-02](15_REQUIREMENTS.md#r-ml-02), [R-ML-04](15_REQUIREMENTS.md#r-ml-04), [R-DATA-01](15_REQUIREMENTS.md#r-data-01), [R-DATA-02](15_REQUIREMENTS.md#r-data-02), [R-DATA-03](15_REQUIREMENTS.md#r-data-03), [R-DATA-04](15_REQUIREMENTS.md#r-data-04), [R-DATA-05](15_REQUIREMENTS.md#r-data-05), [R-DATA-06](15_REQUIREMENTS.md#r-data-06), [R-DATA-07](15_REQUIREMENTS.md#r-data-07), [R-DATA-11](15_REQUIREMENTS.md#r-data-11), [R-RES-01](15_REQUIREMENTS.md#r-res-01), [R-RES-02](15_REQUIREMENTS.md#r-res-02), [R-DOC-01](15_REQUIREMENTS.md#r-doc-01).

Acceptance: [AT-044](20_TEST_ACCEPTANCE.md#at-044), [AT-045](20_TEST_ACCEPTANCE.md#at-045), [AT-047](20_TEST_ACCEPTANCE.md#at-047), [AT-053](20_TEST_ACCEPTANCE.md#at-053), [AT-054](20_TEST_ACCEPTANCE.md#at-054), [AT-055](20_TEST_ACCEPTANCE.md#at-055), [AT-056](20_TEST_ACCEPTANCE.md#at-056), [AT-057](20_TEST_ACCEPTANCE.md#at-057), [AT-058](20_TEST_ACCEPTANCE.md#at-058), [AT-059](20_TEST_ACCEPTANCE.md#at-059), [AT-063](20_TEST_ACCEPTANCE.md#at-063), [AT-069](20_TEST_ACCEPTANCE.md#at-069), [AT-070](20_TEST_ACCEPTANCE.md#at-070), [AT-080](20_TEST_ACCEPTANCE.md#at-080).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T048

**Prepare PPT and presenter handoff** — stage 7; scope RELEASE; status **IN_PROGRESS**.

Dependencies: [T044](07_IMPLEMENTATION_PLAN.md#t044), [T047](07_IMPLEMENTATION_PLAN.md#t047).

Read before coding: [24_DEMO_PRESENTATION](24_DEMO_PRESENTATION.md), [21_RESEARCH_EVIDENCE](21_RESEARCH_EVIDENCE.md), [23_UNIT_ECONOMICS](23_UNIT_ECONOMICS.md).

Concrete output: Create final deck using verified implementation/screens and evidence; fill required organizer template, timing, five-presenter handoff, Q&A and honest limitations; remove stale statistics, EPR/credit/competitor overclaims.

Requirements: [R-GOV-01](15_REQUIREMENTS.md#r-gov-01), [R-GOV-04](15_REQUIREMENTS.md#r-gov-04), [R-ECON-02](15_REQUIREMENTS.md#r-econ-02), [R-RES-01](15_REQUIREMENTS.md#r-res-01), [R-RES-02](15_REQUIREMENTS.md#r-res-02), [R-REG-01](15_REQUIREMENTS.md#r-reg-01), [R-DOC-01](15_REQUIREMENTS.md#r-doc-01).

Acceptance: [AT-001](20_TEST_ACCEPTANCE.md#at-001), [AT-004](20_TEST_ACCEPTANCE.md#at-004), [AT-068](20_TEST_ACCEPTANCE.md#at-068), [AT-069](20_TEST_ACCEPTANCE.md#at-069), [AT-070](20_TEST_ACCEPTANCE.md#at-070), [AT-071](20_TEST_ACCEPTANCE.md#at-071), [AT-080](20_TEST_ACCEPTANCE.md#at-080).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T049

**Record and validate demo video** — stage 7; scope RELEASE; status **IN_PROGRESS**.

Dependencies: [T044](07_IMPLEMENTATION_PLAN.md#t044), [T045](07_IMPLEMENTATION_PLAN.md#t045), [T046](07_IMPLEMENTATION_PLAN.md#t046), [T048](07_IMPLEMENTATION_PLAN.md#t048).

Read before coding: [24_DEMO_PRESENTATION](24_DEMO_PRESENTATION.md), [25_RELEASE_CHECKLIST](25_RELEASE_CHECKLIST.md).

Concrete output: Record actual end-to-end demo with airplane mode, second-phone confirmation, two language audio, data quality and economics; publish/share link only with authorization; test link permissions outside owner account and retain local backup.

Requirements: [R-GOV-04](15_REQUIREMENTS.md#r-gov-04), [R-QA-02](15_REQUIREMENTS.md#r-qa-02).

Acceptance: [AT-004](20_TEST_ACCEPTANCE.md#at-004), [AT-079](20_TEST_ACCEPTANCE.md#at-079).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## T050

**Package release and submission handoff** — stage 7; scope RELEASE; status **IN_PROGRESS**.

Dependencies: [T041](07_IMPLEMENTATION_PLAN.md#t041), [T042](07_IMPLEMENTATION_PLAN.md#t042), [T043](07_IMPLEMENTATION_PLAN.md#t043), [T044](07_IMPLEMENTATION_PLAN.md#t044), [T045](07_IMPLEMENTATION_PLAN.md#t045), [T046](07_IMPLEMENTATION_PLAN.md#t046), [T047](07_IMPLEMENTATION_PLAN.md#t047), [T048](07_IMPLEMENTATION_PLAN.md#t048), [T049](07_IMPLEMENTATION_PLAN.md#t049).

Read before coding: [25_RELEASE_CHECKLIST](25_RELEASE_CHECKLIST.md), [DEPLOYMENT](DEPLOYMENT.md), [08_TRACKER](08_TRACKER.md).

Concrete output: Produce installable signed APK, checksum/version/API URL, prototype web link, GitHub repository, PPT and video link; verify all RELEASE evidence and no missing tasks. Check official portal fields/cutoff and obtain final submission authorization if not already given; record actual submission result separately.

Requirements: [R-GOV-03](15_REQUIREMENTS.md#r-gov-03), [R-GOV-04](15_REQUIREMENTS.md#r-gov-04), [R-AUTH-04](15_REQUIREMENTS.md#r-auth-04), [R-RES-02](15_REQUIREMENTS.md#r-res-02), [R-OPS-01](15_REQUIREMENTS.md#r-ops-01), [R-DOC-01](15_REQUIREMENTS.md#r-doc-01).

Acceptance: [AT-003](20_TEST_ACCEPTANCE.md#at-003), [AT-004](20_TEST_ACCEPTANCE.md#at-004), [AT-010](20_TEST_ACCEPTANCE.md#at-010), [AT-070](20_TEST_ACCEPTANCE.md#at-070), [AT-074](20_TEST_ACCEPTANCE.md#at-074), [AT-080](20_TEST_ACCEPTANCE.md#at-080).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## F001

**Assisted collector and aggregator accounts** — stage 8; scope FUTURE; status **DEFERRED**.

Dependencies: [T050](07_IMPLEMENTATION_PLAN.md#t050).

Read before coding: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Concrete output: Explicit delegation/consent, actor versus beneficial owner, safe phone-less onboarding, separate permissions and offline ownership tests; no admin impersonation shortcut.

Requirements: [R-FUT-01](15_REQUIREMENTS.md#r-fut-01).

Acceptance: [FT-001](20_TEST_ACCEPTANCE.md#ft-001).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## F002

**Multi-collector batching and pickup operations** — stage 8; scope FUTURE; status **DEFERRED**.

Dependencies: [T050](07_IMPLEMENTATION_PLAN.md#t050).

Read before coding: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Concrete output: Batch membership/weights/provenance and collector-level proceeds reconcile; operational capacity and actual pickup success recorded; no double counting.

Requirements: [R-FUT-02](15_REQUIREMENTS.md#r-fut-02).

Acceptance: [FT-002](20_TEST_ACCEPTANCE.md#ft-002).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## F003

**Predictive prices and automated public feeds** — stage 8; scope FUTURE; status **DEFERRED**.

Dependencies: [T050](07_IMPLEMENTATION_PLAN.md#t050).

Read before coding: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Concrete output: Licensed sustained comparable observations, temporal holdout against statistical baseline, uncertainty/drift monitoring and a permitted refresh pipeline; keep indicative labels.

Requirements: [R-FUT-03](15_REQUIREMENTS.md#r-fut-03).

Acceptance: [FT-003](20_TEST_ACCEPTANCE.md#ft-003).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## F004

**Consented active learning and broader classifier** — stage 8; scope FUTURE; status **DEFERRED**.

Dependencies: [T050](07_IMPLEMENTATION_PLAN.md#t050).

Read before coding: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Concrete output: New consent/rights policy, reviewed correction labels, expanded relevant classes, leakage-safe evaluation and version rollback; current release remains public-images-only.

Requirements: [R-FUT-04](15_REQUIREMENTS.md#r-fut-04).

Acceptance: [FT-004](20_TEST_ACCEPTANCE.md#ft-004).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## F005

**Learned recycler ranking and advanced risk detection** — stage 8; scope FUTURE; status **DEFERRED**.

Dependencies: [T050](07_IMPLEMENTATION_PLAN.md#t050).

Read before coding: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Concrete output: Enough quality outcome labels, temporal evaluation/fairness/reason codes, human review and safety hard filters; do not learn to override route eligibility or accuse fraud.

Requirements: [R-FUT-05](15_REQUIREMENTS.md#r-fut-05).

Acceptance: [FT-005](20_TEST_ACCEPTANCE.md#ft-005).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## F006

**Voice input and multilingual assistant** — stage 8; scope FUTURE; status **DEFERRED**.

Dependencies: [T050](07_IMPLEMENTATION_PLAN.md#t050).

Read before coding: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Concrete output: Free/licensed offline ASR where viable, hi/mr noisy-environment tests, explicit confirmation of money/material values and manual fallback; no arbitrary autonomous transaction agent.

Requirements: [R-FUT-06](15_REQUIREMENTS.md#r-fut-06).

Acceptance: [FT-006](20_TEST_ACCEPTANCE.md#ft-006).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## F007

**Pickup route optimization** — stage 8; scope FUTURE; status **DEFERRED**.

Dependencies: [T050](07_IMPLEMENTATION_PLAN.md#t050).

Read before coding: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Concrete output: Consented operational locations, realistic vehicle/capacity/time windows, permitted map data and measured routing baseline; no continuous collector tracking by default.

Requirements: [R-FUT-07](15_REQUIREMENTS.md#r-fut-07).

Acceptance: [FT-007](20_TEST_ACCEPTANCE.md#ft-007).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## F008

**ERP GST PRO brand and CPCB adapters** — stage 8; scope FUTURE; status **DEFERRED**.

Dependencies: [T050](07_IMPLEMENTATION_PLAN.md#t050).

Read before coding: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Concrete output: Documented official/partner API contracts, credentials and legal role, validated field mapping/sandbox evidence, access/audit controls; no claim of integration or certificate issuance before verification.

Requirements: [R-FUT-08](15_REQUIREMENTS.md#r-fut-08).

Acceptance: [FT-008](20_TEST_ACCEPTANCE.md#ft-008).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## F009

**Downstream processing and material mass balance** — stage 8; scope FUTURE; status **DEFERRED**.

Dependencies: [T050](07_IMPLEMENTATION_PLAN.md#t050).

Read before coding: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Concrete output: Recycler processing evidence, batch splits/merges/yield reconciliation and independently supported downstream outcomes before calling received mass recycled.

Requirements: [R-FUT-09](15_REQUIREMENTS.md#r-fut-09).

Acceptance: [FT-009](20_TEST_ACCEPTANCE.md#ft-009).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## F010

**Ed25519 server-signed records** — stage 8; scope FUTURE; status **DEFERRED**.

Dependencies: [T050](07_IMPLEMENTATION_PLAN.md#t050).

Read before coding: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Concrete output: Canonical payload parity, secure signing keys/rotation/revocation/trusted public-key distribution and verification fixtures; signature still does not prove physical facts.

Requirements: [R-FUT-10](15_REQUIREMENTS.md#r-fut-10).

Acceptance: [FT-010](20_TEST_ACCEPTANCE.md#ft-010).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## F011

**Recovery indicator and environmental estimates** — stage 8; scope FUTURE; status **DEFERRED**.

Dependencies: [T050](07_IMPLEMENTATION_PLAN.md#t050).

Read before coding: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Concrete output: Exact peer-reviewed composition/LCA sources, material/device-specific uncertainty and defensible model validation; no invented official formula, exact metal yield or unsupported CO2 savings. Owner must explicitly promote this optional idea.

Requirements: [R-FUT-11](15_REQUIREMENTS.md#r-fut-11).

Acceptance: [FT-011](20_TEST_ACCEPTANCE.md#ft-011).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## F012

**Supervised real-world pilot and partnerships** — stage 8; scope FUTURE; status **DEFERRED**.

Dependencies: [T050](07_IMPLEMENTATION_PLAN.md#t050).

Read before coding: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Concrete output: Consented real collectors/facilities, review safety/privacy/retention/support, actual partnership evidence and measured feedback; historical 5–10/20–30 counts are planning suggestions.

Requirements: [R-FUT-12](15_REQUIREMENTS.md#r-fut-12).

Acceptance: [FT-012](20_TEST_ACCEPTANCE.md#ft-012).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## F013

**More regions languages and material routes** — stage 8; scope FUTURE; status **DEFERRED**.

Dependencies: [T050](07_IMPLEMENTATION_PLAN.md#t050).

Read before coding: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Concrete output: Region/language source and review coverage, safe route-specific authorization and model/material validation; preserve e-waste focus until explicit expansion.

Requirements: [R-FUT-13](15_REQUIREMENTS.md#r-fut-13).

Acceptance: [FT-013](20_TEST_ACCEPTANCE.md#ft-013).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## F014

**Aggregated sector and government insights** — stage 8; scope FUTURE; status **DEFERRED**.

Dependencies: [T050](07_IMPLEMENTATION_PLAN.md#t050).

Read before coding: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Concrete output: Adequate representative data, aggregation/privacy controls and sample/denominator limitations for supply/capacity gaps, volatility/material flows/safety; no prototype national statistics.

Requirements: [R-FUT-14](15_REQUIREMENTS.md#r-fut-14).

Acceptance: [FT-014](20_TEST_ACCEPTANCE.md#ft-014).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## F015

**Advanced dispute review and support workflow** — stage 8; scope FUTURE; status **DEFERRED**.

Dependencies: [T050](07_IMPLEMENTATION_PLAN.md#t050).

Read before coding: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Concrete output: Evidence submission/reviewer permissions/appeal/resolution timeline, immutable original quote/final terms and policy; basic pending/disputed states already required in release.

Requirements: [R-FUT-15](15_REQUIREMENTS.md#r-fut-15).

Acceptance: [FT-015](20_TEST_ACCEPTANCE.md#ft-015).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## F016

**Optional payments messaging and monetization** — stage 8; scope FUTURE; status **DEFERRED**.

Dependencies: [T050](07_IMPLEMENTATION_PLAN.md#t050).

Read before coding: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Concrete output: Separate owner approval, lawful provider terms, fee transparency, webhook idempotency and reconciled settlement; SMS/WhatsApp/email/real UPI/paid SaaS not release dependencies.

Requirements: [R-FUT-16](15_REQUIREMENTS.md#r-fut-16).

Acceptance: [FT-016](20_TEST_ACCEPTANCE.md#ft-016).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## F017

**Collector identity sharing and partner services** — stage 8; scope FUTURE; status **DEFERRED**.

Dependencies: [T050](07_IMPLEMENTATION_PLAN.md#t050).

Read before coding: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Concrete output: Minimal revocable identity QR/consent-scoped history sharing; verified partner eligibility rules before any credit/welfare claim; never public financial profiles or guaranteed access.

Requirements: [R-FUT-17](15_REQUIREMENTS.md#r-fut-17).

Acceptance: [FT-017](20_TEST_ACCEPTANCE.md#ft-017).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

## F018

**Production operations and scale** — stage 8; scope FUTURE; status **DEFERRED**.

Dependencies: [T050](07_IMPLEMENTATION_PLAN.md#t050).

Read before coding: [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md).

Concrete output: Measured bottleneck/load and security requirements justify queues/caching/infra, incident support and disaster recovery; no speculative Kubernetes/microservices or blockchain requirement.

Requirements: [R-FUT-18](15_REQUIREMENTS.md#r-fut-18).

Acceptance: [FT-018](20_TEST_ACCEPTANCE.md#ft-018).

Task closure: implement the output, test relevant paths/failure cases, save reproducible evidence, update status and affected acceptance, regenerate/validate docs and update session state. Future tasks remain deferred until explicitly promoted.

