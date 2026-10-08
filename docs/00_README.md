# Documentation guide

SahiTol is the product; SIH26229 is the supplied problem statement. These documents reconcile the supplied evidence and turn the agreed scope into linked implementation and acceptance work. Start with the [PRD](01_PRD.md). The screenshots from the prior project guided organization only.

## Reading paths

New reader: master → PRD → [app flow](04_APPFLOW.md) → [architecture](03_TECHSPEC.md) → [demo](24_DEMO_PRESENTATION.md) → [limitations/evidence](21_RESEARCH_EVIDENCE.md).

Implementation contributor: [session state](SESSION_STATE.md) → [tracker](08_TRACKER.md) → [decisions](09_DECISIONS.md)/[questions](10_OPEN_QUESTIONS.md) → selected [task](07_IMPLEMENTATION_PLAN.md) → its linked requirements/specifications/cases. Preserve the documented scope, update evidence honestly, and use the recovery process when continuity is needed.

## Document map

| File | Owns |
|---|---|
| [01_PRD](01_PRD.md) | Users, outcomes, release scope and constraints |
| [02_ROADMAP](02_ROADMAP.md) | Generated dependency stages and gates |
| [03_TECHSPEC](03_TECHSPEC.md) | Native/API/web architecture, exact price/match policies, targets |
| [04_APPFLOW](04_APPFLOW.md) | Roles, user journeys and state transitions |
| [05_DESIGN_STITCH](05_DESIGN_STITCH.md) | Owner-only design gate, 34-screen inventory and briefs |
| [06_SCHEMA](06_SCHEMA.md) | Server/Room entities, constraints, money/weight and canonical hashes |
| [07_IMPLEMENTATION_PLAN](07_IMPLEMENTATION_PLAN.md) | Generated task outputs, dependencies, reading and acceptance mappings |
| [08_TRACKER](08_TRACKER.md) | Generated task/case progress and external gap |
| [09_DECISIONS](09_DECISIONS.md) | Explicit choices, superseded alternatives and labelled defaults |
| [10_OPEN_QUESTIONS](10_OPEN_QUESTIONS.md) | Only missing implementation facts, not re-asking settled choices |
| [11_SECRETS_CHECKLIST](11_SECRETS_CHECKLIST.md) | Config/account names and safe ownership, no secrets |
| [12_GUARDRAILS](12_GUARDRAILS.md) | Product/security/privacy/claim constraints |
| [13_RECOVERY](13_RECOVERY.md) | Context recovery, progress transaction and failure handling |
| [14_TRANSLATION_AUDIO_AUDIT](14_TRANSLATION_AUDIO_AUDIT.md) | hi/mr/en strings, offline clips, numeric grammar and review |
| [15_REQUIREMENTS](15_REQUIREMENTS.md) | Generated atomic requirement/source/task/case graph |
| [16_API_CONTRACT](16_API_CONTRACT.md) | Routes, actor permissions, requests and errors |
| [17_OFFLINE_SYNC](17_OFFLINE_SYNC.md) | Durable outbox, media, retries/idempotency, conflicts, pull cursors |
| [18_DATA_PROVENANCE](18_DATA_PROVENANCE.md) | Seven dataset lifecycles, provenance/import/export |
| [19_AI_ML](19_AI_ML.md) | Licence/split/train/quantize/evaluate/integrate model |
| [20_TEST_ACCEPTANCE](20_TEST_ACCEPTANCE.md) | Generated acceptance checks and real-evidence rules |
| [21_RESEARCH_EVIDENCE](21_RESEARCH_EVIDENCE.md) | Checked sources, secondary inference, claims and fieldwork gap |
| [22_REGULATORY_SAFETY](22_REGULATORY_SAFETY.md) | Facility levels/routes/receipt boundaries and safe content |
| [23_UNIT_ECONOMICS](23_UNIT_ECONOMICS.md) | Editable same-lot formulas, illustrative inputs and sustainability |
| [24_DEMO_PRESENTATION](24_DEMO_PRESENTATION.md) | Two-device script, deck, five presenters, Q&A and video |
| [25_RELEASE_CHECKLIST](25_RELEASE_CHECKLIST.md) | Software gates, four artifacts and actual submission |
| [26_FUTURE_BACKLOG](26_FUTURE_BACKLOG.md) | Explicit deferred ideas with tasks/cases/prerequisites |
| [27_SOURCE_RECONCILIATION](27_SOURCE_RECONCILIATION.md) | Full-file range/heading coverage and conflict dispositions |
| [PROBLEM_STATEMENT](PROBLEM_STATEMENT.md) | Supplied brief mapped to work, official-source verification caveat |
| [DEPLOYMENT](DEPLOYMENT.md) | Hosted/local runs, persistent storage, networking/signing/restore |
| [MONITORING](MONITORING.md) | Real metric denominators, quality review and diagnostics |
| [SESSION_STATE](SESSION_STATE.md) | Current handoff, next steps and blockers |
| [CHANGELOG](../CHANGELOG.md) | Documentation/implementation changes, never fabricated outcomes |
| [DOCUMENTATION_AUDIT](DOCUMENTATION_AUDIT.md) | Automated structural checks and honest limits |

Supporting files: [Stitch registry](../design/stitch/SCREEN_REGISTRY.md), [dataset headers](../data/templates/README.md), [data card](templates/DATA_CARD.md), [model card](templates/MODEL_CARD.md), [research card](templates/RESEARCH_CARD.md), [test evidence](templates/TEST_EVIDENCE.md), [change record](templates/CHANGE_DECISION.md).

## One execution graph

[catalog.json](planning/catalog.json) owns requirements/task definitions/tests; [status.json](planning/status.json) owns progress. `render_docs.py` creates the five planning views. `check_docs.py` validates IDs/mappings/dependencies/status evidence/local links/source hashes and coverage. It cannot prove app correctness or perfect interpretation of prose. Keep specs detailed and update related graph entries in the same change; never leave a feature solely in a narrative document.

`python scripts/test_doc_integrity.py` runs nine negative controls for omission and false-completion protections. The scripts named `build_catalog`, `extend_baseline`, `build_source_inventory` and `prepare_doc_fixtures` are initial documentation-authoring helpers, not normal implementation commands or application data pipelines. The current JSON catalog is authoritative; do not rebuild it from historical helper inputs or overwrite progress.

Baseline: 50 release tasks, 79 RELEASE requirements/cases, one EXTERNAL_GAP fieldwork requirement/case, 18 future tasks/requirements/cases. Everything starts TODO/NOT_RUN, future DEFERRED, fieldwork UNMET. Nothing is falsely marked implemented. Source transcripts remain byte-for-byte copies with original line citations. See the audit for current generated counts and results.
