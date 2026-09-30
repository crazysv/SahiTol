# Seven datasets, provenance and reproducible data work

Implements T005/T010–T012/T031/T047 and [R-DATA requirements](15_REQUIREMENTS.md). Database truth is [schema](06_SCHEMA.md); historical examples are not seed facts. No actual imported records or trained datasets are delivered by this documentation baseline.

## Classification and field lineage

Use `origin_class = OFFICIAL | EXTERNAL_PUBLIC | PLATFORM_GENERATED | SYNTHETIC`, `source_kind` (REGULATOR_LIST, GOVERNMENT_PUBLICATION, PUBLIC_MARKET_QUOTE, SECONDARY_STUDY, PLATFORM_OBSERVATION, USER_SELF_DECLARED, VERIFIED_TRANSACTION, LICENSED_IMAGE_DATASET, SYNTHETIC_GENERATOR), and independent `is_demo`. An official directory with made-up pickup availability must retain official lineage for its address and synthetic lineage for pickup. It is not wholly official. A demo created in the app is PLATFORM_GENERATED and `is_demo=true`; real platform use is not automatically verified physical truth. Derived aggregates retain input IDs, filter policy, computation version and demo partition.

Every field assertion links to source ID, document URL/title/publisher, publication date when available, retrieval time, document hash/local snapshot if redistribution allowed, page/row locator, transformation, reviewer and validation status. Record unknowns as null with reason. Missing publication date is not today's date. Source access/official publication/field verification/current licence are separate properties. Personal contacts should not become public merely because a PDF includes them.

## Dataset contracts

| Family | Producers and core fields | Validation / lifecycle | Product use and export |
|---|---|---|---|
| Material | Curated taxonomy/aliases and separately lot observations: stable material/subcategory/route, condition, estimated/measured grams, image ref, time/general region, source | Admin-reviewed catalog version; observed records emitted on collection/handover with corrections; positive weights on submit; contextual route review | Classification/manual selector, valuation, safety and matching; material catalog plus observation CSV/JSON |
| Price | Public dated observations, recycler quotes and acknowledged transaction outcomes; unit/kind/material/condition/region/rate/time/source | Stage→validate→review→include; compare only compatible cohorts; correction revision; 30-day current window baseline, cache age visible; unique transaction-derived observation | Board/history/range/quality/ranking; price observations and summary manifest |
| Recycler | CPCB plus small DPCC/Delhi-NCR and MPCB sets, source-backed roles/permissions; operational self-declarations separate | Dedup registration/name/address with manual review; coordinates quality; source/current route evidence; refresh before demo and on expiry; admin approval | Directory, route eligibility and explained matching; facility/authorization/operations tables |
| Transaction | Collector request, facility offer, accepted terms, handover/receipt and payment assertions | Legal state machine, actor and version checks, integer amounts, one active agreement, no double count; append corrections | Ledger, procurement export and observed sale price; transaction and payment CSV/JSON |
| Traceability | Immutable local/server events, media checksums, previous/current hash, time/location provenance, confirmation | Canonical serialization, no overwrite, replay-safe writes, consistent ordering, missing-media indicators | Passport/QR/PDF/audit; redacted events and manifest, no claim of physical verification |
| Collector | Consent-aware profile, alias, language, coarse area and platform participation | Minimum data, account-scoped access; no Aadhaar/PAN/bank need; update with version/audit; pseudonymize exports | Personalization/own ledger, aggregate metrics; admin-only minimal export |
| AI/ML Training | Exact licensed public image assets, label, source/license/hash, physical-object group, split, preprocessing and optional condition/region | Licence audit, class relevance, dedup, leakage checks, deterministic split, label audit, versioned dataset/model cards | Training/evaluation; metadata manifest, redistribution only when allowed; missing weight/price/location remain null |

Header-only [templates](../data/templates/README.md) are import/export starting points. They do not substitute for migrations, importer validation or populated data cards. Prefer separate normalized exports over huge repeated mixed rows; each family has a manifest listing its constituent files and relationships.

## Material coverage

Catalog covers PCB (with supported board subtype/grade only if evidenced), CRT, LCD, cables/wires, batteries (lead-acid/lithium-ion/other/unknown chemistry), motors/magnets, mixed electronics and mixed plastics, plus OTHER and UNKNOWN. Add source-supported aluminium/copper/iron/steel and appliance categories as needed by reviewed data; do not invent contained metal percentages. Manual support is mandatory even if classifier coverage is narrower. Local aliases are reviewed language content, not separate commodity IDs. Units: grams/kg with explicit conversion; per-piece kept separate. Condition values must be versioned and explainable, never unvalidated multipliers.

## Import and update pipeline

1. Register source/rights/access dates, acquire allowed snapshot and SHA-256, retain raw bytes outside mutable curated tables. Export raw copyrighted material only if permitted.
2. Extract PDF/CSV/JSON into staging with locator and extraction version. Normalize Unicode, phone display, addresses, units and dates; preserve originals. Manually review OCR ambiguities.
3. Deduplicate using stable registry references when available, then normalized name/address with a review queue. Do not auto-merge similarly named branches or different facility roles.
4. Validate columns/types, positive measurements, route/role, source age, coordinates/bounds, currency, unit and referential integrity. Quarantine rejected rows with error reasons and counts.
5. Geocode only when permitted; cache source/query/result/time/precision, review dubious pins. Unknown location cannot claim nearby distance. Never send collector home locations to a public geocoder.
6. Curator reviews; idempotent upsert uses source record key plus revision. Publish a dataset version and sync tombstones for withdrawn records. Old transaction snapshots remain unchanged.
7. Export deterministic UTF-8 CSV and JSON, UTC ISO timestamps, integer paise/grams, explicit nulls (CSV empty plus data dictionary). Neutralize spreadsheet formula injection in text exports; maintain unmodified canonical raw data separately.
8. Manifest: dataset/schema/version, generated time, counts by status/origin/demo, source IDs, validation report, row-key policy, file SHA-256, transformation/git version and limitations. Reconcile totals to DB queries.

Suggested review cadence (engineering defaults): prices daily when an active source exists; directory before each release and at least every 30 days while operational; authorization immediately on known change; taxonomy/safety on source revision; platform events continuously. A missed refresh lowers freshness or eligibility; it does not silently move timestamps forward.

## Synthetic and demonstration data

Use a fixed seed and stable namespace IDs. Generate plausible but explicitly invented values, disjoint from real people/businesses and official authorizations. Scenarios: ordinary successful trade, small/no-price cohort, stale/expired route, unknown chemistry, low confidence image, rejected/expired offer, changed weight, partial/disputed payment, duplicate operation, conflicting edit, missing image, denied GPS, wrong clock and outage. Invalid fixtures live outside accepted analytics; expected error included. Synthetic sources never enter live-price cohorts or real-impact totals. Test fixtures may model a verified facility only in a clearly isolated simulated environment, not as a claim about an actual business.

The platform data flywheel is demonstrable: lot→observation; quote→dated quote record; receipt→traceability; acknowledged paid trade→reviewable outcome price; corrections→quality event and candidate ML label. User images/corrections are **not** added to the current training dataset because the owner chose public images only. A future consented learning pipeline remains [F004](26_FUTURE_BACKLOG.md).

## Sufficiency and completion

Earlier quantities such as 100–200 images/category, 200–500 total, 20–50 recyclers, 472 facilities and dozens of transactions are planning suggestions or unsupported historical claims, not verified achievements. Choose a feasible audited subset in T005/T032 and record real counts. Cover both requested regions lightly, all manual materials, all seven families and required edge scenarios. For ML insufficient classes, document coverage and abstention; a deadline does not justify fabricated samples/metrics. Each of seven [data cards](templates/DATA_CARD.md) must identify actual contents, limitations, rights and update owner before T047 closes.
