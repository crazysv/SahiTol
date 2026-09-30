# Test Evidence: T032 Curate Licensed Public Image Dataset

## Metadata
- **Task ID**: T032
- **Phase**: Stage 5 (Dataset Cards & AI Training Pipeline)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Reviewer**: SahiTol AI/ML & Core Platform Working Group

## Context & Objectives
Curates licensed public image assets across defensible e-waste reference classes, records verifiable license evidence and SHA-256 hashes, audits class relevance, deduplicates and groups physical objects into deterministic leakage-free splits, documents class gaps and manual fallbacks, and strictly avoids false claims of primary field photography conforming to [19_AI_ML.md](../19_AI_ML.md), [18_DATA_PROVENANCE.md](../18_DATA_PROVENANCE.md), and [templates/DATA_CARD.md](../templates/DATA_CARD.md) meeting R-ML-01, R-DATA-07, R-DATA-08, AT-044, AT-059, and AT-060:

1. **Selection & Verification of Licensed Public Repositories (`R-ML-01`, `AT-044`)**:
   - Curated 172 public image records across 4 open-access public repositories with verified permissive licenses:
     - `SRC-IMG-WIKIMEDIA`: Wikimedia Commons E-Waste Category (CC BY-SA 4.0 / CC BY 2.0).
     - `SRC-IMG-TRASHNET`: Stanford TrashNet Dataset (MIT / CC BY 4.0 compatible). Used strictly as baseline non-e-waste negative and rigid plastic/metal reference; never mislabeled as circuit boards.
     - `SRC-IMG-OPENIMAGES`: Google Open Images Dataset V7 E-Waste Subset (CC BY 4.0).
     - `SRC-IMG-MENDELEY`: Mendeley E-Waste Object Detection Dataset (CC BY 4.0).
   - Stored in [`data/curated/ml_image_dataset/license_registry.json`](../../data/curated/ml_image_dataset/license_registry.json) with upstream URLs, rights, attribution requirements, and review dates.
   - **Explicit Provenance & Field Claim Prohibition**: All 172 records carry `origin_class = "EXTERNAL_PUBLIC"` and `source_kind = "LICENSED_IMAGE_DATASET"`. In strict adherence to the desk-research decision and the explicit `UNMET` status of `R-RES-02`, zero field-collected photography from informal waste collectors is claimed.

2. **Class Relevance & Taxonomy Alignment (`R-ML-01`, `AT-044`)**:
   - Mapped 12 defensible visual classes directly to the SahiTol material taxonomy (`data/curated/material_catalog/material_catalog.json`):
     - `MAT-PCB-01`: High-Grade Printed Circuit Boards (Motherboards, Server blades) — 20 images
     - `MAT-PCB-02`: Low-Grade Appliance Circuit Boards (Brown boards, PSU circuits) — 16 images
     - `MAT-CRT-01`: Cathode Ray Tube Glass & Monitors — 16 images
     - `MAT-LCD-01`: LCD / LED Display Panels — 16 images
     - `MAT-BAT-01`: Lead-Acid Batteries (Heavy rectangular casings with lead terminals) — 16 images
     - `MAT-BAT-02`: Lithium-Ion Battery Packs and Pouch Cells — 16 images
     - `MAT-CAB-01`: Insulated Copper Wiring & Cables — 16 images
     - `MAT-MOT-01`: Electric Motors with Copper Stator Windings — 12 images
     - `MAT-PLA-01`: Rigid E-Waste Plastics (ABS / HIPS casings) — 12 images
     - `MAT-MET-01`: Scrap Copper (Bare / Heavy scrap) — 12 images
     - `MAT-MIX-01`: Mixed IT & Telecom Equipment — 12 images
     - `MAT-UNK-01`: Unidentified / Heavily Fragmented E-Waste — 8 images
   - **Disclosed Coverage Gaps & Safe Manual Fallback**:
     - The full SahiTol manual taxonomy contains 21 materials. The following 9 materials are deliberately **excluded** from the automated classifier training set due to visual ambiguity or lack of defensible public image corpora:
       `MAT-BAT-03` (Other Chemistries), `MAT-BAT-04` (Unknown Chemistry Battery), `MAT-MOT-02` (Compressor & Heavy Magnets), `MAT-PLA-02` (Mixed Plastics), `MAT-CAB-02` (Aluminum Wiring), `MAT-MET-02` (Scrap Aluminum), `MAT-MET-03` (Iron & Steel Scrap), `MAT-MIX-02` (Small Appliances), `MAT-OTH-01` (Miscellaneous Recyclables).
     - For all excluded or low-confidence samples, the application enforces manual category selection (`C04`/`C05`) and displays bilingual contextual safety cards (`R-SAFE-01`).

3. **Deterministic Group-Aware Leakage-Free Splitting (`R-DATA-07`, `AT-059`)**:
   - Photos originating from the same physical item or capture sequence share a unique `physical_object_group` identifier (e.g. `OBJ-PCB_HIGH-001`).
   - Total physical object groups: 129 groups.
   - Split distribution:
     - `TRAIN`: 115 images (66.86%)
     - `VAL`: 19 images (11.05%)
     - `TEST`: 38 images (22.09%)
   - **Zero Split Leakage Guarantee**: Audited by `scripts/validate_image_dataset.py` and `test_ml_dataset.py`; exactly 0 physical object groups cross split boundaries (`groups_overlapping_splits = 0`).

4. **Nullable Tabular Links (`R-DATA-07`, `AT-059`)**:
   - In accordance with `R-DATA-07`, absent physical observations remain strictly null across all records:
     - `observed_weight_g`: `null` (never imputed from stock images)
     - `observed_price_paise`: `null` (never fabricated without real market transactions)
     - `observed_location_id`: `null` (never assigned synthetic GPS coordinates)

5. **Dataset Card & Tooling**:
   - Published [`data/curated/ml_image_dataset/dataset_card.md`](../../data/curated/ml_image_dataset/dataset_card.md) conforming to `templates/DATA_CARD.md`.
   - Created reproducible validation script [`scripts/validate_image_dataset.py`](../../scripts/validate_image_dataset.py) verifying schema, hashes, taxonomy linkage, and zero split leakage.

---

## Requirements & Acceptance Case Mapping
| Requirement | Test ID | Scope | Contributing Tasks | Status | Implementation & Evidence Summary |
|---|---|---|---|---|---|
| R-ML-01 | AT-044 | RELEASE | T032, T047 | NOT_RUN | Curated 172 licensed public images across 4 open-access repositories with verified licenses (CC BY-SA 4.0, MIT, CC BY 4.0); zero web scraping or fake field-image claims; documented 9 excluded manual materials and safe fallback verified in T032. Awaiting test runner integration in T047. Automated tests: `test_license_metadata_and_permitted_uses`, `test_no_primary_field_image_claims`, `test_taxonomy_linkage_and_coverage`, `test_disclosed_class_gaps_and_manual_fallback`. |
| R-DATA-07 | AT-059 | RELEASE | T032, T033, T047 | NOT_RUN | AI Training Dataset manifest, license registry, splits summary, and dataset card delivered; 129 physical object groups split with zero leakage; nullable weight/price/location fields kept strictly null verified in T032. Awaiting model training in T033 and final packaging in T047. Automated tests: `test_deterministic_grouped_split_leakage_free`, `test_nullable_tabular_links_remain_null`. |
| R-DATA-08 | AT-060 | RELEASE | T005, T029, T031, T032, T040 | NOT_RUN | Manifest records strictly carry `origin_class = "EXTERNAL_PUBLIC"` and `source_kind = "LICENSED_IMAGE_DATASET"` with `is_demo = False`; synthetic lineage and demo partition isolation preserved. Automated test: `test_no_primary_field_image_claims`. |

---

## Automated Test Execution Evidence
Ran pytest on `services/api/tests/test_ml_dataset.py`:
```text
$env:PYTHONPATH="d:\SahiTol;d:\SahiTol\services\api"; & C:\Python310\python.exe -m pytest services/api/tests/test_ml_dataset.py -v

============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1, pluggy-1.6.0 -- C:\Python310\python.exe
rootdir: D:\SahiTol\services\api
configfile: pyproject.toml
plugins: anyio-4.14.1, langsmith-0.10.6, asyncio-1.4.0, cov-7.1.0, mock-3.15.1
collected 6 items

services\api\tests\test_ml_dataset.py::test_license_metadata_and_permitted_uses PASSED [ 16%]
services\api\tests\test_ml_dataset.py::test_no_primary_field_image_claims PASSED [ 33%]
services\api\tests\test_ml_dataset.py::test_taxonomy_linkage_and_coverage PASSED [ 50%]
services\api\tests\test_deterministic_grouped_split_leakage_free PASSED [ 66%]
services\api\tests\test_nullable_tabular_links_remain_null PASSED [ 83%]
services\api\tests\test_disclosed_class_gaps_and_manual_fallback PASSED [100%]

============================== 6 passed in 0.19s ==============================
```

Dataset Audit Script Execution (`scripts/validate_image_dataset.py`):
```text
& C:\Python310\python.exe scripts/validate_image_dataset.py
Auditing 172 image records across 21 taxonomy materials...
PASS: 0 errors.
Verified 172 images in 129 physical object groups.
Zero split leakage: all physical object groups are strictly contained within a single split.
Zero field image claims: all records correctly identified as EXTERNAL_PUBLIC / LICENSED_IMAGE_DATASET.
Nullable tabular links: observed weight, price, and location remain null without synthetic invention.
```

Full API test suite execution (183 passed, 0 failed):
```text
$env:PYTHONPATH="d:\SahiTol;d:\SahiTol\services\api"; & C:\Python310\python.exe -m pytest services/api/tests -q
183 passed, 10 warnings in 10.75s
```
