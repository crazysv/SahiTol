# Test Evidence: T010 Curate Material Taxonomy and Language Aliases

## Metadata
- **Task ID**: T010
- **Phase**: Stage 1 (Data & Backend Setup)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Reviewer**: SahiTol Engineering & Taxonomy Working Group

## Context & Objectives
Implements the curated, authoritative reference taxonomy for informal e-waste recycling, covering every problem statement named material:
- CRT (Cathode Ray Tube / Monitor Glass)
- LCD (LCD / LED Flat Display Panels)
- PCB (High-grade motherboard / server PCB, Low-grade appliance board)
- Cables (Insulated copper wire, Aluminum / telecom cable)
- Batteries (Lead-acid, Lithium-ion, Other chemistries, Unknown chemistry)
- Motors & Magnets (Electric motor with copper windings, Compressor / sealed unit / magnets)
- Mixed Plastics (Rigid e-waste plastics ABS/HIPS with flame retardants, General mixed plastics)
- Mixed Electronics (IT & telecom equipment, Small household appliances)
- Sorted Metals (Scrap copper, Scrap aluminum, Iron & steel scrap)
- OTHER (Miscellaneous recyclables)
- UNKNOWN (Unidentified scrap components)

Attaches contextual regulatory routing (distinguishing e-waste flame-retardant plastics requiring context from general packaging plastics, and isolating batteries to separate regulatory treatment under CPCB Battery Waste Rules), contextual safety guides with multilingual audio and text keys, condition options, allowed units, and rich colloquial language aliases in Hindi (`hi`), Marathi (`mr`), and English (`en`). Proves clear separation between the immutable reference catalog and observed lot instances.

## Requirements & Acceptance Case Mapping
| Requirement | Test ID | Scope | Contributing Tasks | Implementation & Evidence Summary |
|---|---|---|---|---|
| R-LOT-01 | AT-011 | RELEASE | T010, T017 | Curated catalog covers CRT, LCD, PCB (high & low grades), cables (Cu & Al), batteries (lead-acid, li-ion, other, unknown), motors/magnets, mixed plastics, mixed electronics, metals, OTHER, and UNKNOWN. Multilingual alias search endpoint (`GET /api/v1/materials/search`) resolves colloquial terms (e.g. Hindi "मदरबोर्ड", "हरा पत्ता", "कांच वाला टीवी"; Marathi "हिरवा बोर्ड", "काचेची ट्यूब", "इन्व्हर्टर बॅटरी"; English "motherboard", "lead acid battery") to stable IDs. |
| R-DATA-01 | AT-053 | RELEASE | T010, T016, T031, T047 | Canonical material catalog and aliases exported with deterministic SHA-256 manifest to `data/curated/material_catalog/`. Lot draft creation (`POST /api/v1/lots`) links to reference material IDs while keeping user observations (weight, condition, photos) strictly separate from the catalog. |

## Observable Artifact Outputs
1. **Canonical Seeds (`data/seeds/`)**:
   - `material_categories.json`: 11 categories (`PCB`, `BATTERY`, `CRT`, `LCD`, `CABLES`, `MOTORS`, `PLASTICS`, `METALS`, `MIXED_ELECTRONICS`, `OTHER`, `UNKNOWN`) with display ordering.
   - `materials.json`: 21 distinct material entries specifying subcategory codes, condition options, units (`kg,g`, `kg,piece`, `piece,kg`), regulatory routes, and safety guide linkage.
   - `material_aliases.json`: 139 verified colloquial and formal aliases across Hindi, Marathi, and English with normalized search terms.
   - `safety_guides.json`: 9 contextual safety guides with warning text keys, icon asset references, and pre-generated audio keys across `en`, `hi`, and `mr`.

2. **Database Seeder (`services/api/app/db/seeds/materials.py`)**:
   - Idempotent upsert logic populating `MaterialCategory`, `Material`, `MaterialAlias`, `SafetyGuide`, and referenced regulatory `DataSource` records (`SRC-01`, `SRC-02`).

3. **FastAPI Materials & Safety Routers (`services/api/app/routers/materials.py`)**:
   - `GET /api/v1/materials/categories`: Lists categories ordered by `display_order`.
   - `GET /api/v1/materials`: Lists materials with filters (`category_id`, `route`, `language`) and associated aliases.
   - `GET /api/v1/materials/{id}`: Detailed view embedding linked contextual safety guides.
   - `GET /api/v1/materials/search`: Alias resolution endpoint matching raw input strings against normalized multilingual terms.
   - `GET /api/v1/safety-guides`: Sourced safety guides filtered by route or material.
   - `GET /api/v1/safety-guides/{id}`: Single safety guide lookup.

4. **Curated Data Export & Manifest (`data/curated/material_catalog/`)**:
   - `material_catalog.csv` & `material_catalog.json`: 21 catalog entries with source linkage.
   - `material_aliases.json`: 139 multilingual aliases.
   - `safety_guides.json`: 9 contextual safety guides.
   - `manifest.json`: Cryptographic manifest detailing file hashes, row counts, and provenance limitations.

5. **Automated Test Suite (`services/api/tests/test_materials.py`)**:
   - 9 test cases verifying complete material coverage, provenance-dependent routing, Hindi/Marathi/English alias search, safety guide multilingual audio keys, lot draft creation across all material classes, and catalog immutability.

## Test Verification Output
```text
python -m pytest tests/test_materials.py -v
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1, pluggy-1.6.0 -- C:\Python310\python.exe
cachedir: .pytest_cache
rootdir: D:\SahiTol\services\api
configfile: pyproject.toml
plugins: anyio-4.14.1, langsmith-0.10.6, asyncio-1.4.0, cov-7.1.0, mock-3.15.1
asyncio: mode=auto, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 9 items

tests/test_materials.py::test_categories_listing PASSED                  [ 11%]
tests/test_materials.py::test_complete_material_coverage PASSED          [ 22%]
tests/test_materials.py::test_provenance_dependent_routing PASSED        [ 33%]
tests/test_materials.py::test_language_alias_resolution_hindi PASSED     [ 44%]
tests/test_materials.py::test_language_alias_resolution_marathi PASSED   [ 55%]
tests/test_materials.py::test_language_alias_resolution_english PASSED   [ 66%]
tests/test_materials.py::test_contextual_safety_guides PASSED            [ 77%]
tests/test_materials.py::test_draft_lot_creation_links_to_catalog PASSED [ 88%]
tests/test_materials.py::test_reference_catalog_distinct_from_observations PASSED [100%]

======================== 9 passed, 1 warning in 1.11s =========================
```

Full API test suite verification:
```text
python -m pytest
======================= 48 passed, 2 warnings in 6.31s ========================
```
