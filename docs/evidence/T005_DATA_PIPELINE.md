# Test Evidence: T005 Build Reproducible Data Import and Validation Tools

## Metadata
- **Task ID**: T005
- **Phase**: Stage 1 (Data & Backend Setup)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Reviewer**: SahiTol Engineering & Data Architecture

## Context & Objectives
Implements data ingestion staging, pandas cleaning, field-level lineage, cached geocoding with privacy policy, validation with quarantine routing, multi-stage deduplication, and reproducible synthetic generator with 15 edge scenario fixtures in compliance with [18_DATA_PROVENANCE.md](../18_DATA_PROVENANCE.md) and [06_SCHEMA.md](../06_SCHEMA.md).

## Requirements & Acceptance Case Mapping
| Requirement | Test ID | Scope | Contributing Tasks | Tooling Implementation Status |
|---|---|---|---|---|
| R-DATA-08 | AT-060 | RELEASE | T005, T029, T031, T040 | Implemented `OriginClass`, `SourceKind`, demo isolation rules, formula injection defense, and manifest aggregation with breakdowns. |
| R-DATA-09 | AT-061 | RELEASE | T005, T012, T031 | Implemented `DataValidator` for all 7 families, quarantine logging to JSON-Lines, and `CachedGeocoder` with regional bounds and collector privacy enforcement. |
| R-DATA-10 | AT-062 | RELEASE | T005, T043 | Implemented deterministic `SyntheticGenerator` (seed=42) generating all 7 families and 15 explicit operational and anomaly edge scenarios. |

## Observable Artifact Outputs
1. **Core Provenance & Sanitization** (`scripts/data_tools/provenance.py`):
   - Provenance enums: `OriginClass` (`OFFICIAL`, `EXTERNAL_PUBLIC`, `PLATFORM_GENERATED`, `SYNTHETIC`), `SourceKind` (9 types), `ReviewStatus`, `LocationQuality`.
   - `sanitize_csv_cell()`: Neutralizes spreadsheet formula injection by prepending `'` to strings starting with `=`, `+`, `-`, `@`, `\t`, or `\r`.
   - `DataSource` and `FieldAssertion` models tracking field-level provenance, transformation version, reviewer, and locator.

2. **Ingestion Staging & Conversions** (`scripts/data_tools/staging.py`):
   - `normalize_text()`: Unicode NFC normalization, trimming, and collapsed whitespace.
   - `normalize_phone()`: Strict +91 normalization for 10-digit Indian mobile numbers.
   - `convert_to_paise()`: Exact 64-bit integer paise conversion (rejects NaN/infinite).
   - `convert_to_grams()`: Strictly positive integer grams conversion across kg, g, quintal, and ton.
   - `load_records()` and `save_csv()`: Standardized UTF-8 loading and export.

3. **Validation & Quarantine Engine** (`scripts/data_tools/validation.py`):
   - Validates all 7 dataset families: `material_catalog`, `price_observations`, `recyclers`, `transactions`, `traceability`, `collectors`, `ai_training`.
   - Provenance isolation: Quarantines records if `OFFICIAL` claims source `SYNTHETIC_GENERATOR` (`SYNTHETIC_OFFICIAL_CONFLICT`) or if `SYNTHETIC` has `is_demo=False` (`SYNTHETIC_DEMO_MISMATCH`).
   - Regional bounds check: Validates facility coordinates against India territorial bounds (lat 8.0–37.0, lon 68.0–97.0).
   - `QuarantineRecord` logger writing to inspectable JSON-Lines without losing raw records.

4. **Multi-Stage Deduplication** (`scripts/data_tools/deduplication.py`):
   - Facility deduplication via registration reference exact matching and normalized name+address matching (with manual review queue for differing roles).
   - Price observation deduplication by material cohort, condition, price kind, timestamp, and source.
   - Asset deduplication via exact SHA-256 hash collision checks.

5. **Cached Geocoder with Privacy Policy** (`scripts/data_tools/geocoding.py`):
   - **Privacy Boundary**: Attempting to geocode `entity_type="COLLECTOR"` strictly raises `PermissionError` (collector home residences are never sent to external geocoders).
   - Local JSON cache (`data/cache/geocoding_cache.json`) prevents redundant external queries.
   - Quality labelling (`GEOCODED_ROOFTOP`, `GEOCODED_APPROXIMATE`, `COARSE_DISTRICT`, `UNKNOWN`).
   - Missing coordinates remain explicit `null`, never fabricated.

6. **Reproducible Synthetic Generator & Edge Scenarios** (`scripts/data_tools/synthetic.py`):
   - Seeded deterministic generation across all 7 families with `origin_class=SYNTHETIC`, `source_kind=SYNTHETIC_GENERATOR`, `is_demo=True`.
   - 15 explicit operational and anomaly edge scenario fixtures:
     - `EDGE-01-HAPPY-PATH`: Ordinary successful trade workflow.
     - `EDGE-02-NO-PRICE-COHORT`: Zero or insufficient (<3) price observations; null rate with `INSUFFICIENT_DATA`.
     - `EDGE-03-STALE-EXPIRED-ROUTE`: Expired facility authorization; filtered from matching.
     - `EDGE-04-UNKNOWN-BATTERY-CHEMISTRY`: Battery with unknown chemistry routed to `BATTERY_ISOLATION`.
     - `EDGE-05-LOW-CONFIDENCE-IMAGE`: Classifier score below threshold (0.42 < 0.70) triggers abstention.
     - `EDGE-06-REJECTED-OFFER`: Collector rejects recycler quote; lot returns to available pool.
     - `EDGE-07-EXPIRED-OFFER`: Offer expires before acceptance; server returns 410 Gone.
     - `EDGE-08-CHANGED-WEIGHT`: Scale reading differs from estimate; triggers `TERMS_REVISION`.
     - `EDGE-09-PARTIAL-PAYMENT`: Partial cash settlement; records outstanding balance.
     - `EDGE-10-DISPUTED-PAYMENT`: Recycler asserts cash payment but collector denies receipt; triggers dispute flag.
     - `EDGE-11-DUPLICATE-OPERATION`: Replayed client operation ID handled idempotently.
     - `EDGE-12-CONFLICTING-EDIT`: Version mismatch yields HTTP 409 Conflict.
     - `EDGE-13-MISSING-IMAGE`: Draft lot submitted without photo is blocked.
     - `EDGE-14-DENIED-GPS`: Fallback to `COARSE_DISTRICT` when GPS permission is denied.
     - `EDGE-15-CLOCK-SKEW`: Client clock skewed > 2 hours; server overrides ordering timestamp.

7. **Manifest & Cryptographic Integrity** (`scripts/data_tools/manifest.py`):
   - Computes SHA-256 for all exported CSV and JSON files.
   - Tracks counts by origin class, source kind, demo flag, and review status.

8. **CLI Interface & Test Suite**:
   - `scripts/run_data_pipeline.py`: Commands `generate-synthetic`, `validate`, `dedup`, `geocode`.
   - `scripts/test_data_pipeline.py`: 6 passing unit tests covering all functions.

## Test Results
```text
pytest scripts/test_data_pipeline.py
============================== 6 passed in 0.63s ==============================
```
CLI execution verified:
```text
python scripts/run_data_pipeline.py generate-synthetic --output-dir data/synthetic
  [OK] material_catalog: 10 records exported
  [OK] price_observations: 10 records exported
  [OK] recyclers: 4 records exported
  [OK] collectors: 3 records exported
  [OK] transactions: 2 records exported
  [OK] traceability: 4 records exported
  [OK] ai_training: 4 records exported
  [OK] edge_scenarios: 15 fixtures exported to data\synthetic\edge_scenarios.json
```
