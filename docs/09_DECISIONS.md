# Decisions and conflict resolution

Baseline 2026-09-28. Authority: current user request → latest explicit user choices in `previous_convo.txt` → reconciled specification → engineering defaults. An assistant's later suggestion is not a user decision merely because it appears later. Raw files are preserved in [sources](sources/previous_convo.txt); line citations in [requirements](15_REQUIREMENTS.md) use E/P physical lines. Change a settled choice only on explicit owner direction and propagate the change across contracts, tasks and tests.

| ID | Settled decision / reason | Replaced or clarified | Basis |
|---|---|---|---|
| D01 | Product SahiTol; SIH26229 title preserved as problem identity | KabadiSetu/Kabadiwala Connect as product-name variants | P:2535–2569 |
| D02 | One builder; five teammates present | Multi-team parallel development assignments | P:2585–2605 |
| D03 | All deliverables due Sep 30; exact portal time unverified | Three-week implementation plan or assumption time is available after PPT | P:2592–2615 |
| D04 | Native Kotlin/Compose collector, even with deadline risk | PWA/React/Dexie/Capacitor and automatic fallback after spike | P:2602–2607; P:2636–2637 |
| D05 | FastAPI + SQLAlchemy/Alembic + PostgreSQL/PostGIS | Node API, SQLite production, dropping PostGIS | P:2295–2316; P:2638–2640 |
| D06 | React/Vite/TypeScript recycler/admin web | Next.js dashboard and SSR overhead | P:2639–2639 |
| D07 | Phone/PIN JWT backend; isolated demo access | Supabase Auth, mandatory SMS/OTP service | P:1959–1975; P:2646–2647 |
| D08 | Local file volume + hosted private Supabase Storage adapter | MinIO/Redis and ephemeral-host uploads | P:2312–2316; P:2638–2640; provider research |
| D09 | Hosted API/DB for remote judges, local fallback retained | Localhost-only or “cloud later if time” | P:2610–2611 |
| D10 | All six selected features required | Old optional classifier/audio/dashboard/QR/economics cuts | P:2612–2613; P:2641–2646 |
| D11 | Keras MobileNetV3-Small → LiteRT, public licensed images | ONNX/TFJS, runtime cloud classifier, own field images | P:2295–2316; P:2628–2629; P:2641 |
| D12 | Hindi/Marathi pre-generated offline audio via free tool | Runtime paid TTS, one language only, static-only price audio | P:2618–2621; P:2642 |
| D13 | Real second Android device uses recycler web QR | Single-device pretend confirmation / no borrowed phone | P:2626–2627; P:2643 |
| D14 | CPCB + small DPCC/Delhi-NCR and MPCB coverage | Full-India catalogue or only one registry implied complete | P:2526–2541; P:2646 |
| D15 | Secondary research only; primary requirement openly unmet | Invented fieldwork, prescriptive source interview tasks, claimed substitution | P:2517–2540; P:2647 |
| D16 | Editable illustrative economics with public-source context | Fabricated actual earnings/income uplift | P:2614–2619; P:2645–2646 |
| D17 | Statistical valuation, deterministic matching, quality rules now | Calling all rules trained AI; price ML without data | E:2457–2608; P final reconciled scope |
| D18 | Hash-linked Digital Handover Record, pending→confirmed | EPR certificate, blockchain, signatures without key infrastructure | E:970–1170; P:2651–2653 |
| D19 | Owner generates every UI in Stitch; agent only retrieves/implements | Autonomous UI skills/templates/generation and unapproved missing states | Current request |
| D20 | Requirement→task→case graph is execution authority | Features stranded in prose outside tracker/roadmap | Current request |

## Engineering defaults, explicitly not historical owner promises

| ID | Default | Authoritative contract / change impact |
|---|---|---|
| ED01 | Render API, Supabase DB/private storage, Pages web, Docker local | [Deployment](DEPLOYMENT.md); change only to satisfy selected no-paid-runtime/remote-access contracts, record provider terms |
| ED02 | PRICE_V1 dated weighted quartiles, 30-day window, 7-day half-life, count/source freshness confidence | [Techspec](03_TECHSPEC.md); version calculations and preserve snapshots/fixtures |
| ED03 | MATCH_V1 hard eligibility then weights 30/30/20/15/5 and 50km default | Techspec; weights are transparent demo policy, not a learned/validated optimum |
| ED04 | 30-day source recheck plus actual authorization validity | [Regulatory](22_REGULATORY_SAFETY.md); refresh policy never extends licence validity |
| ED05 | Integer paise/grams, UUIDs, restricted canonical JSON, append-only events | [Schema](06_SCHEMA.md); migration and cross-language fixtures required for change |
| ED06 | Payment assertion needs counterparty acknowledgement; revised measured terms need collector acknowledgement | [Flow](04_APPFLOW.md); reliable record semantics, not bank verification |
| ED07 | Separate origin_class/source_kind/is_demo; external public is not official | [Data](18_DATA_PROVENANCE.md); avoids forced mislabelling from older three-label shorthand |
| ED08 | Batch50, pull200, durable per-actor idempotency, isolated demo partitions | [Sync](17_OFFLINE_SYNC.md); configurable only with boundary tests |
| ED09 | Grouped 70/15/15 split when feasible; threshold learned on validation | [ML](19_AI_ML.md); no invented score or minimum accuracy |
| ED10 | Performance/size and image bounds are targets/limits, measured on named hardware | Techspec; missed targets reported rather than hidden |

## Changes and disputed text

When a source proposes a future feature, retain it in [future backlog](26_FUTURE_BACKLOG.md) with prerequisites and completion criteria; don't implement it just because it is mentioned. When text is contradictory or an unsupported claim, mark it superseded/rejected/unverified in [source reconciliation](27_SOURCE_RECONCILIATION.md). An older optional label cannot demote a latest must-have. If an actual contradiction remains, add a specific question and continue unrelated work. Never change a RELEASE requirement to FUTURE to make the completion count look better.
