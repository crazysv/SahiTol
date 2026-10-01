# Roadmap

Generated from [catalog](planning/catalog.json) and [status](planning/status.json). Edit those files, then run `python scripts/render_docs.py` and `python scripts/check_docs.py`. Do not edit this view independently.

Owner deadline: **2026-09-30** for all four artifacts; exact official cutoff unverified. These are dependency stages, not a claim the remaining work fits the available time. One builder executes; five teammates present. Do not cut required work silently.

Critical chains: T001→T003→T013→T015→collector; T006→T021→T023→T025→T026; T032→T033→T034; T036→T037→T046; all converge at T043–T050. T002 gates each UI batch; T004/T005 enable data work independently.

## Stage 0: Feasibility, sources and owner screen handoff

S00 supplied; real Android spike and source decisions recorded. No automatic fallback.

| Task | Work | Status | Dependencies |
|---|---|---|---|
| [T001](07_IMPLEMENTATION_PLAN.md#t001) | Bootstrap repository and compatible toolchain | DONE | None |
| [T002](07_IMPLEMENTATION_PLAN.md#t002) | Obtain and register owner-generated Stitch designs | DONE | None |
| [T003](07_IMPLEMENTATION_PLAN.md#t003) | Prove Android feasibility on a real phone | DONE | [T001](07_IMPLEMENTATION_PLAN.md#t001), [T002](07_IMPLEMENTATION_PLAN.md#t002) |
| [T004](07_IMPLEMENTATION_PLAN.md#t004) | Complete secondary-research and source register | DONE | None |

## Stage 1: Backend foundation and reviewed reference data

Migrations/auth/private storage and curated source datasets verified; missing facts remain explicit.

| Task | Work | Status | Dependencies |
|---|---|---|---|
| [T005](07_IMPLEMENTATION_PLAN.md#t005) | Build reproducible data import and validation tools | DONE | [T001](07_IMPLEMENTATION_PLAN.md#t001) |
| [T006](07_IMPLEMENTATION_PLAN.md#t006) | Implement PostgreSQL/PostGIS schema and migrations | DONE | [T001](07_IMPLEMENTATION_PLAN.md#t001) |
| [T007](07_IMPLEMENTATION_PLAN.md#t007) | Implement phone/PIN authentication and ownership | DONE | [T006](07_IMPLEMENTATION_PLAN.md#t006) |
| [T008](07_IMPLEMENTATION_PLAN.md#t008) | Implement private media storage adapter | DONE | [T006](07_IMPLEMENTATION_PLAN.md#t006), [T007](07_IMPLEMENTATION_PLAN.md#t007) |
| [T009](07_IMPLEMENTATION_PLAN.md#t009) | Implement versioned reference bootstrap and delta APIs | DONE | [T006](07_IMPLEMENTATION_PLAN.md#t006), [T007](07_IMPLEMENTATION_PLAN.md#t007) |
| [T010](07_IMPLEMENTATION_PLAN.md#t010) | Curate material taxonomy and language aliases | DONE | [T004](07_IMPLEMENTATION_PLAN.md#t004), [T005](07_IMPLEMENTATION_PLAN.md#t005), [T006](07_IMPLEMENTATION_PLAN.md#t006) |
| [T011](07_IMPLEMENTATION_PLAN.md#t011) | Create attributed price seed and observation pipeline | DONE | [T004](07_IMPLEMENTATION_PLAN.md#t004), [T005](07_IMPLEMENTATION_PLAN.md#t005), [T006](07_IMPLEMENTATION_PLAN.md#t006), [T010](07_IMPLEMENTATION_PLAN.md#t010) |
| [T012](07_IMPLEMENTATION_PLAN.md#t012) | Build Delhi-NCR and Maharashtra facility directory | DONE | [T004](07_IMPLEMENTATION_PLAN.md#t004), [T005](07_IMPLEMENTATION_PLAN.md#t005), [T006](07_IMPLEMENTATION_PLAN.md#t006), [T010](07_IMPLEMENTATION_PLAN.md#t010) |

## Stage 2: Durable native collector core and sync

Local restart and retry-safe sync work; C01–C05/C14/C15 supplied and implemented.

| Task | Work | Status | Dependencies |
|---|---|---|---|
| [T013](07_IMPLEMENTATION_PLAN.md#t013) | Implement Android Room repositories and durable outbox | DONE | [T003](07_IMPLEMENTATION_PLAN.md#t003), [T006](07_IMPLEMENTATION_PLAN.md#t006) |
| [T014](07_IMPLEMENTATION_PLAN.md#t014) | Implement server synchronization protocol | DONE | [T006](07_IMPLEMENTATION_PLAN.md#t006), [T007](07_IMPLEMENTATION_PLAN.md#t007), [T008](07_IMPLEMENTATION_PLAN.md#t008), [T009](07_IMPLEMENTATION_PLAN.md#t009) |
| [T015](07_IMPLEMENTATION_PLAN.md#t015) | Implement Android background and manual synchronization | DONE | [T013](07_IMPLEMENTATION_PLAN.md#t013), [T014](07_IMPLEMENTATION_PLAN.md#t014) |
| [T016](07_IMPLEMENTATION_PLAN.md#t016) | Implement lot and lifecycle backend | DONE | [T006](07_IMPLEMENTATION_PLAN.md#t006), [T007](07_IMPLEMENTATION_PLAN.md#t007), [T008](07_IMPLEMENTATION_PLAN.md#t008), [T010](07_IMPLEMENTATION_PLAN.md#t010), [T014](07_IMPLEMENTATION_PLAN.md#t014) |
| [T017](07_IMPLEMENTATION_PLAN.md#t017) | Implement approved collector onboarding and lot screens | DONE | [T002](07_IMPLEMENTATION_PLAN.md#t002), [T007](07_IMPLEMENTATION_PLAN.md#t007), [T009](07_IMPLEMENTATION_PLAN.md#t009), [T013](07_IMPLEMENTATION_PLAN.md#t013), [T015](07_IMPLEMENTATION_PLAN.md#t015), [T016](07_IMPLEMENTATION_PLAN.md#t016) |

## Stage 3: Prices, matching and recycler offers

Dated indicative prices and hard route filters tested; actual offers/acceptance and approved consoles.

| Task | Work | Status | Dependencies |
|---|---|---|---|
| [T018](07_IMPLEMENTATION_PLAN.md#t018) | Implement price statistics and snapshot valuation | DONE | [T011](07_IMPLEMENTATION_PLAN.md#t011), [T016](07_IMPLEMENTATION_PLAN.md#t016) |
| [T019](07_IMPLEMENTATION_PLAN.md#t019) | Implement eligible recycler matching and map data | DONE | [T012](07_IMPLEMENTATION_PLAN.md#t012), [T018](07_IMPLEMENTATION_PLAN.md#t018) |
| [T020](07_IMPLEMENTATION_PLAN.md#t020) | Implement approved collector price and recycler views | DONE | [T002](07_IMPLEMENTATION_PLAN.md#t002), [T017](07_IMPLEMENTATION_PLAN.md#t017), [T018](07_IMPLEMENTATION_PLAN.md#t018), [T019](07_IMPLEMENTATION_PLAN.md#t019), [T021](07_IMPLEMENTATION_PLAN.md#t021) |
| [T021](07_IMPLEMENTATION_PLAN.md#t021) | Implement recycler profile and offer workflows | DONE | [T007](07_IMPLEMENTATION_PLAN.md#t007), [T016](07_IMPLEMENTATION_PLAN.md#t016), [T019](07_IMPLEMENTATION_PLAN.md#t019) |
| [T022](07_IMPLEMENTATION_PLAN.md#t022) | Implement approved recycler console and phone layout | DONE | [T002](07_IMPLEMENTATION_PLAN.md#t002), [T021](07_IMPLEMENTATION_PLAN.md#t021) |

## Stage 4: Handover, confirmation and payment evidence

Two phones confirm one synced proposal; revisions, payment acknowledgements, PDF and ledger agree.

| Task | Work | Status | Dependencies |
|---|---|---|---|
| [T023](07_IMPLEMENTATION_PLAN.md#t023) | Implement handover proposals and confirmations | DONE | [T014](07_IMPLEMENTATION_PLAN.md#t014), [T021](07_IMPLEMENTATION_PLAN.md#t021) |
| [T024](07_IMPLEMENTATION_PLAN.md#t024) | Implement approved offline QR and collector receipt | DONE | [T002](07_IMPLEMENTATION_PLAN.md#t002), [T017](07_IMPLEMENTATION_PLAN.md#t017), [T023](07_IMPLEMENTATION_PLAN.md#t023) |
| [T025](07_IMPLEMENTATION_PLAN.md#t025) | Implement approved second-phone QR confirmation | DONE | [T002](07_IMPLEMENTATION_PLAN.md#t002), [T022](07_IMPLEMENTATION_PLAN.md#t022), [T023](07_IMPLEMENTATION_PLAN.md#t023) |
| [T026](07_IMPLEMENTATION_PLAN.md#t026) | Implement payment assertions and earnings projections | DONE | [T023](07_IMPLEMENTATION_PLAN.md#t023) |
| [T027](07_IMPLEMENTATION_PLAN.md#t027) | Implement approved ledger and payment screens | DONE | [T002](07_IMPLEMENTATION_PLAN.md#t002), [T024](07_IMPLEMENTATION_PLAN.md#t024), [T026](07_IMPLEMENTATION_PLAN.md#t026) |

## Stage 5: AI, languages, datasets, admin and economics

All six selected must-haves, seven dataset lifecycles, model/audio rights and real outputs present.

| Task | Work | Status | Dependencies |
|---|---|---|---|
| [T028](07_IMPLEMENTATION_PLAN.md#t028) | Implement data-quality and anomaly rules | DONE | [T018](07_IMPLEMENTATION_PLAN.md#t018), [T019](07_IMPLEMENTATION_PLAN.md#t019), [T023](07_IMPLEMENTATION_PLAN.md#t023), [T026](07_IMPLEMENTATION_PLAN.md#t026) |
| [T029](07_IMPLEMENTATION_PLAN.md#t029) | Implement admin maintenance and metrics APIs | DONE | [T028](07_IMPLEMENTATION_PLAN.md#t028) |
| [T030](07_IMPLEMENTATION_PLAN.md#t030) | Implement approved admin/data-quality dashboard | DONE | [T002](07_IMPLEMENTATION_PLAN.md#t002), [T029](07_IMPLEMENTATION_PLAN.md#t029) |
| [T031](07_IMPLEMENTATION_PLAN.md#t031) | Implement seven dataset exports and data lineage | DONE | [T010](07_IMPLEMENTATION_PLAN.md#t010), [T011](07_IMPLEMENTATION_PLAN.md#t011), [T012](07_IMPLEMENTATION_PLAN.md#t012), [T023](07_IMPLEMENTATION_PLAN.md#t023), [T026](07_IMPLEMENTATION_PLAN.md#t026), [T029](07_IMPLEMENTATION_PLAN.md#t029), [T002](07_IMPLEMENTATION_PLAN.md#t002), [T022](07_IMPLEMENTATION_PLAN.md#t022), [T030](07_IMPLEMENTATION_PLAN.md#t030) |
| [T032](07_IMPLEMENTATION_PLAN.md#t032) | Curate licensed public image dataset | DONE | [T004](07_IMPLEMENTATION_PLAN.md#t004), [T005](07_IMPLEMENTATION_PLAN.md#t005), [T010](07_IMPLEMENTATION_PLAN.md#t010) |
| [T033](07_IMPLEMENTATION_PLAN.md#t033) | Train evaluate and export on-device model | DONE | [T032](07_IMPLEMENTATION_PLAN.md#t032) |
| [T034](07_IMPLEMENTATION_PLAN.md#t034) | Integrate classifier into approved Android flow | DONE | [T002](07_IMPLEMENTATION_PLAN.md#t002), [T017](07_IMPLEMENTATION_PLAN.md#t017), [T033](07_IMPLEMENTATION_PLAN.md#t033) |
| [T035](07_IMPLEMENTATION_PLAN.md#t035) | Create contextual safety content and review path | DONE | [T004](07_IMPLEMENTATION_PLAN.md#t004), [T010](07_IMPLEMENTATION_PLAN.md#t010) |
| [T036](07_IMPLEMENTATION_PLAN.md#t036) | Complete language resources and accessible interaction | DONE | [T017](07_IMPLEMENTATION_PLAN.md#t017), [T020](07_IMPLEMENTATION_PLAN.md#t020), [T024](07_IMPLEMENTATION_PLAN.md#t024), [T027](07_IMPLEMENTATION_PLAN.md#t027), [T035](07_IMPLEMENTATION_PLAN.md#t035) |
| [T037](07_IMPLEMENTATION_PLAN.md#t037) | Generate and wire offline Hindi/Marathi audio | DONE | [T035](07_IMPLEMENTATION_PLAN.md#t035), [T036](07_IMPLEMENTATION_PLAN.md#t036), [T005](07_IMPLEMENTATION_PLAN.md#t005) |
| [T038](07_IMPLEMENTATION_PLAN.md#t038) | Implement illustrative economics model | DONE | [T004](07_IMPLEMENTATION_PLAN.md#t004), [T011](07_IMPLEMENTATION_PLAN.md#t011), [T026](07_IMPLEMENTATION_PLAN.md#t026) |
| [T039](07_IMPLEMENTATION_PLAN.md#t039) | Implement approved economics and safety views | DONE | [T002](07_IMPLEMENTATION_PLAN.md#t002), [T030](07_IMPLEMENTATION_PLAN.md#t030), [T035](07_IMPLEMENTATION_PLAN.md#t035), [T037](07_IMPLEMENTATION_PLAN.md#t037), [T038](07_IMPLEMENTATION_PLAN.md#t038) |

## Stage 6: Hosted/local operations and full verification

Fault/security/device/language/performance tests, cellular-hosted journey and restore evidence.

| Task | Work | Status | Dependencies |
|---|---|---|---|
| [T040](07_IMPLEMENTATION_PLAN.md#t040) | Verify security privacy and abuse boundaries | DONE | [T025](07_IMPLEMENTATION_PLAN.md#t025), [T027](07_IMPLEMENTATION_PLAN.md#t027), [T030](07_IMPLEMENTATION_PLAN.md#t030), [T031](07_IMPLEMENTATION_PLAN.md#t031) |
| [T041](07_IMPLEMENTATION_PLAN.md#t041) | Deploy hosted API database storage and web | DONE | [T007](07_IMPLEMENTATION_PLAN.md#t007), [T008](07_IMPLEMENTATION_PLAN.md#t008), [T025](07_IMPLEMENTATION_PLAN.md#t025), [T030](07_IMPLEMENTATION_PLAN.md#t030), [T039](07_IMPLEMENTATION_PLAN.md#t039), [T040](07_IMPLEMENTATION_PLAN.md#t040) |
| [T042](07_IMPLEMENTATION_PLAN.md#t042) | Prove local demo fallback and restore | DONE | [T024](07_IMPLEMENTATION_PLAN.md#t024), [T027](07_IMPLEMENTATION_PLAN.md#t027), [T031](07_IMPLEMENTATION_PLAN.md#t031), [T040](07_IMPLEMENTATION_PLAN.md#t040) |
| [T043](07_IMPLEMENTATION_PLAN.md#t043) | Run cross-surface integration and fault acceptance | DONE | [T015](07_IMPLEMENTATION_PLAN.md#t015), [T025](07_IMPLEMENTATION_PLAN.md#t025), [T027](07_IMPLEMENTATION_PLAN.md#t027), [T030](07_IMPLEMENTATION_PLAN.md#t030), [T031](07_IMPLEMENTATION_PLAN.md#t031), [T034](07_IMPLEMENTATION_PLAN.md#t034), [T037](07_IMPLEMENTATION_PLAN.md#t037), [T039](07_IMPLEMENTATION_PLAN.md#t039), [T040](07_IMPLEMENTATION_PLAN.md#t040) |
| [T044](07_IMPLEMENTATION_PLAN.md#t044) | Perform real-device and two-device usability tests | DONE | [T041](07_IMPLEMENTATION_PLAN.md#t041), [T042](07_IMPLEMENTATION_PLAN.md#t042), [T043](07_IMPLEMENTATION_PLAN.md#t043) |
| [T045](07_IMPLEMENTATION_PLAN.md#t045) | Measure entry-level performance and artifact size | DONE | [T034](07_IMPLEMENTATION_PLAN.md#t034), [T037](07_IMPLEMENTATION_PLAN.md#t037), [T043](07_IMPLEMENTATION_PLAN.md#t043) |
| [T046](07_IMPLEMENTATION_PLAN.md#t046) | Audit all translations and audio on device | DONE | [T036](07_IMPLEMENTATION_PLAN.md#t036), [T037](07_IMPLEMENTATION_PLAN.md#t037), [T039](07_IMPLEMENTATION_PLAN.md#t039), [T044](07_IMPLEMENTATION_PLAN.md#t044) |

## Stage 7: Evidence, presentation and submission artifacts

All required task/case evidence plus four accessible artifacts; fieldwork limitation disclosed.

| Task | Work | Status | Dependencies |
|---|---|---|---|
| [T047](07_IMPLEMENTATION_PLAN.md#t047) | Freeze dataset and model evidence package | IN_PROGRESS | [T031](07_IMPLEMENTATION_PLAN.md#t031), [T033](07_IMPLEMENTATION_PLAN.md#t033), [T044](07_IMPLEMENTATION_PLAN.md#t044), [T045](07_IMPLEMENTATION_PLAN.md#t045), [T046](07_IMPLEMENTATION_PLAN.md#t046) |
| [T048](07_IMPLEMENTATION_PLAN.md#t048) | Prepare PPT and presenter handoff | IN_PROGRESS | [T044](07_IMPLEMENTATION_PLAN.md#t044), [T047](07_IMPLEMENTATION_PLAN.md#t047) |
| [T049](07_IMPLEMENTATION_PLAN.md#t049) | Record and validate demo video | IN_PROGRESS | [T044](07_IMPLEMENTATION_PLAN.md#t044), [T045](07_IMPLEMENTATION_PLAN.md#t045), [T046](07_IMPLEMENTATION_PLAN.md#t046), [T048](07_IMPLEMENTATION_PLAN.md#t048) |
| [T050](07_IMPLEMENTATION_PLAN.md#t050) | Package release and submission handoff | IN_PROGRESS | [T041](07_IMPLEMENTATION_PLAN.md#t041), [T042](07_IMPLEMENTATION_PLAN.md#t042), [T043](07_IMPLEMENTATION_PLAN.md#t043), [T044](07_IMPLEMENTATION_PLAN.md#t044), [T045](07_IMPLEMENTATION_PLAN.md#t045), [T046](07_IMPLEMENTATION_PLAN.md#t046), [T047](07_IMPLEMENTATION_PLAN.md#t047), [T048](07_IMPLEMENTATION_PLAN.md#t048), [T049](07_IMPLEMENTATION_PLAN.md#t049) |

## Stage 8: Explicit future scope

Owner promotion and expanded plan required; excluded from current-release percentage.

| Task | Work | Status | Dependencies |
|---|---|---|---|
| [F001](07_IMPLEMENTATION_PLAN.md#f001) | Assisted collector and aggregator accounts | DEFERRED | [T050](07_IMPLEMENTATION_PLAN.md#t050) |
| [F002](07_IMPLEMENTATION_PLAN.md#f002) | Multi-collector batching and pickup operations | DEFERRED | [T050](07_IMPLEMENTATION_PLAN.md#t050) |
| [F003](07_IMPLEMENTATION_PLAN.md#f003) | Predictive prices and automated public feeds | DEFERRED | [T050](07_IMPLEMENTATION_PLAN.md#t050) |
| [F004](07_IMPLEMENTATION_PLAN.md#f004) | Consented active learning and broader classifier | DEFERRED | [T050](07_IMPLEMENTATION_PLAN.md#t050) |
| [F005](07_IMPLEMENTATION_PLAN.md#f005) | Learned recycler ranking and advanced risk detection | DEFERRED | [T050](07_IMPLEMENTATION_PLAN.md#t050) |
| [F006](07_IMPLEMENTATION_PLAN.md#f006) | Voice input and multilingual assistant | DEFERRED | [T050](07_IMPLEMENTATION_PLAN.md#t050) |
| [F007](07_IMPLEMENTATION_PLAN.md#f007) | Pickup route optimization | DEFERRED | [T050](07_IMPLEMENTATION_PLAN.md#t050) |
| [F008](07_IMPLEMENTATION_PLAN.md#f008) | ERP GST PRO brand and CPCB adapters | DEFERRED | [T050](07_IMPLEMENTATION_PLAN.md#t050) |
| [F009](07_IMPLEMENTATION_PLAN.md#f009) | Downstream processing and material mass balance | DEFERRED | [T050](07_IMPLEMENTATION_PLAN.md#t050) |
| [F010](07_IMPLEMENTATION_PLAN.md#f010) | Ed25519 server-signed records | DEFERRED | [T050](07_IMPLEMENTATION_PLAN.md#t050) |
| [F011](07_IMPLEMENTATION_PLAN.md#f011) | Recovery indicator and environmental estimates | DEFERRED | [T050](07_IMPLEMENTATION_PLAN.md#t050) |
| [F012](07_IMPLEMENTATION_PLAN.md#f012) | Supervised real-world pilot and partnerships | DEFERRED | [T050](07_IMPLEMENTATION_PLAN.md#t050) |
| [F013](07_IMPLEMENTATION_PLAN.md#f013) | More regions languages and material routes | DEFERRED | [T050](07_IMPLEMENTATION_PLAN.md#t050) |
| [F014](07_IMPLEMENTATION_PLAN.md#f014) | Aggregated sector and government insights | DEFERRED | [T050](07_IMPLEMENTATION_PLAN.md#t050) |
| [F015](07_IMPLEMENTATION_PLAN.md#f015) | Advanced dispute review and support workflow | DEFERRED | [T050](07_IMPLEMENTATION_PLAN.md#t050) |
| [F016](07_IMPLEMENTATION_PLAN.md#f016) | Optional payments messaging and monetization | DEFERRED | [T050](07_IMPLEMENTATION_PLAN.md#t050) |
| [F017](07_IMPLEMENTATION_PLAN.md#f017) | Collector identity sharing and partner services | DEFERRED | [T050](07_IMPLEMENTATION_PLAN.md#t050) |
| [F018](07_IMPLEMENTATION_PLAN.md#f018) | Production operations and scale | DEFERRED | [T050](07_IMPLEMENTATION_PLAN.md#t050) |

Parallelizable work means independent work by the same builder or explicitly authorized collaborators; it does not change the one-builder assumption. If the deadline becomes infeasible, report exact required gaps and request an owner scope decision while continuing useful authorized work.

Completion rules: [release checklist](25_RELEASE_CHECKLIST.md). Every task below is also linked to requirements and checks; no feature is complete from roadmap status alone.
