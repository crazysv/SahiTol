# Test Evidence: T012 Build Delhi-NCR and Maharashtra Facility Directory

## Metadata
- **Task ID**: T012
- **Phase**: Stage 1 (Data & Backend Setup)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Reviewer**: SahiTol Engineering & Regulatory Compliance Working Group

## Context & Objectives
Implements the source-backed facility directory for informal e-waste collectors across Delhi-NCR and Maharashtra, addressing:
- Importing realistic, attributed subsets from CPCB, DPCC (Delhi), MPCB (Maharashtra), and NDMC public registers.
- Preserving exact facility roles: `RECYCLER` (Greentech, EcoRegen, Maharashtra Lead), `DISMANTLER` (Seelampur Co-operative), `COLLECTION_CENTRE` (Eco-Battery, NDMC), and `AGGREGATOR` (Pune Aggregators). Never relabeling a collection point as a recycler.
- Linking each facility to dated registry evidence (`SRC-01`, `SRC-02`, `SRC-04`, `SRC-05`, `SRC-06`) and including explicit statutory disclaimers on every record stating that a directory listing does not constitute an official endorsement, commercial partnership, or EPR fulfillment guarantee.
- Enforcing verification levels (`L0` demo fixture, `L2` listed in official register, `L3` route-verified with active validity, `L4` operational verification) and verifying that `L0`, `L2`, and expired registrations never receive the strong "Verified Formal Destination" badge.
- Faithfully preserving unknown operational parameters: unverified pickup availability and quote rates remain `null` / unknown (never fabricated ticks).
- Enabling facility users to update operational parameters (`PUT /api/v1/facilities/{id}/operations`) while keeping regulatory authorizations strictly admin-controlled.
- Geocoding bounds validation ensuring coordinates lie within India territory (lat 8.0-37.0, lon 68.0-97.0) with accuracy classifications (`ROOFTOP`, `APPROXIMATE`, `DISTRICT_CENTROID`).
- Deduplication pipeline using registration references and normalized address matching.
- Curated export package (`data/curated/facilities/`) with SHA-256 cryptographic manifest.

## Requirements & Acceptance Case Mapping
| Requirement | Test ID | Scope | Contributing Tasks | Implementation & Evidence Summary |
|---|---|---|---|---|
| R-REC-01 | AT-021 | RELEASE | T012 | Source-backed directory imported from CPCB (`SRC-02`), DPCC (`SRC-05`), MPCB (`SRC-04`), and NDMC (`SRC-06`). Real roles are preserved: Eco-Battery and NDMC are classified as `COLLECTION_CENTRE`, Seelampur as `DISMANTLER`, Greentech/EcoRegen as `RECYCLER`, and Pune as `AGGREGATOR`. No collection centre is relabeled as a recycler. Statutory disclaimer ("Does not represent an endorsement, commercial partnership, or EPR fulfillment certificate") is enforced on every returned record. Automated test: `test_list_facilities_role_preservation_and_disclaimer`. **PASS**. |
| R-REC-02 | AT-022 | RELEASE | T012, T019, T029 | Verification level rules enforced: Greentech and EcoRegen (`L3` + `VALID`) are marked `is_formal_destination=True`; Pune Aggregators (`L2`) and NDMC (`L2` + `EXPIRED`) have `is_formal_destination=False`. Filter `GET /api/v1/facilities?formal_destination_only=true` strictly isolates verified formal destinations. Automated tests: `test_verification_levels_and_formal_destination_badge`, `test_formal_destination_filter`. |
| R-REC-03 | AT-023 | RELEASE | T012, T021, T022 | Unknown pickup availability is preserved as `null` (e.g. Greentech), while drop-off only (`False` on Eco-Battery) and pickup enabled (`True` on Seelampur) are faithfully reported. Facility operators can update operational fields (`PUT /api/v1/facilities/{id}/operations`) while regulatory authorization fields remain admin-controlled. Automated tests: `test_unknown_pickup_and_rates_preserved_as_unknown`, `test_update_facility_operations_does_not_mutate_authorizations`. |
| R-DATA-03 | AT-055 | RELEASE | T012, T021, T029, T031, T047 | Full dataset lifecycle: Canonical seed import (`data/seeds/facilities.json`), database seeder (`services/api/app/db/seeds/facilities.py`), operational update logging, and versioned export (`data/curated/facilities/`) with SHA-256 manifest. Automated tests: `test_seed_facilities_loads_directory`, `test_data_validation_and_deduplication`. |
| R-DATA-09 | AT-061 | RELEASE | T005, T012, T031 | Geocode bounding box checks, accuracy classifications, and deduplication verification. Automated test: `test_data_validation_and_deduplication`. |

## Observable Artifact Outputs
1. **Canonical Seeds (`data/seeds/facilities.json`)**:
   - 8 dated facility records covering Delhi-NCR and Maharashtra:
     - 4 Delhi-NCR facilities (Greentech recycler, Eco-Battery collection centre, NDMC collection point, Seelampur dismantler)
     - 3 Maharashtra facilities (EcoRegen Mumbai recycler, Maharashtra Lead Navi Mumbai recycler, Pune Bhosari aggregator)
     - 1 isolated demonstration hub (`is_demo=True`, `L0`)
   - Complete metadata: registration references, validity ranges, verified coordinates, accepted materials, pickup statuses, and regulatory routes.

2. **Database Seeder (`services/api/app/db/seeds/facilities.py`)**:
   - Seeds `DataSource` records (`SRC-02`, `SRC-04`, `SRC-05`, `SRC-06`), ensures baseline regions (`DELHI_NCR`, `MAHARASHTRA`), and populates `facilities`, `facility_authorizations`, `facility_materials`, and `facility_operations`.

3. **FastAPI Facilities Router (`services/api/app/routers/facilities.py`)**:
   - `GET /api/v1/facilities`: Public directory listing with filters (`region_id`, `kind`, `route`, `material_id`, `verification_level`, `formal_destination_only`, `is_demo`).
   - `GET /api/v1/facilities/{id}`: Detailed view with complete authorization history, accepted materials, and operational terms.
   - `PUT /api/v1/facilities/{id}/operations`: Facility operator update endpoint for pickup availability, service area, and accepting status.
   - `POST /api/v1/facilities/{id}/rates`: Quote rate submission endpoint.

4. **Recycler & Bootstrap Integration**:
   - `services/api/app/routers/recyclers.py`: `GET /api/v1/recyclers/directory` routes to the facility query service.
   - `services/api/app/routers/reference.py`: `GET /api/v1/reference/bootstrap` dynamically loads seeded regional facilities.

5. **Curated Export Package (`data/curated/facilities/`)**:
   - `facilities.csv` (3,245 bytes, SHA-256: `35f0f02377b210086c8f93a90aa1fce66264ff4471e95b06f71d5300eb0f9bfe`)
   - `facilities.json` (8,442 bytes, SHA-256: `a937a0916ff25816987c1ddb069d2d4151eef3db836ef0ae601b058c42a2223c`)
   - `facility_authorizations.json` (3,118 bytes, SHA-256: `645d9dbbeba5c754d9c4aa086c4f39e31d4ffbc7a49a9096181f9baefd8eb9db`)
   - `facility_materials.json` (4,325 bytes, SHA-256: `2a98f1f72d5c31f471e164c442cb36a7a72d34a472cbfa1199a54ea7fb4ec03d`)
   - `manifest.json` (1,990 bytes) detailing origin classes, source kinds, facility types, and provenance limitations.

6. **Automated Test Suite (`services/api/tests/test_facilities.py`)**:
   - 15 automated unit and integration tests verifying directory seeding, role preservation, statutory disclaimers, verification levels, formal destination filtering, regional partitioning, material/route filtering, unknown pickup preservation, operational updates without authorization tampering, quote rate submission, backward-compatible `/recyclers/directory`, bootstrap integration, demo partition isolation, and validation/deduplication.

## Test Verification Output
```text
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\SahiTol\services\api
configfile: pyproject.toml
plugins: anyio-4.14.1, langsmith-0.10.6, asyncio-1.4.0, cov-7.1.0, mock-3.15.1
asyncio: mode=auto, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 15 items

services\api\tests\test_facilities.py ...............                    [100%]

======================== 15 passed, 1 warning in 1.15s ========================
```

Full API test suite verification:
```text
collected 83 items

services\api\tests\test_auth.py .............                            [ 15%]
services\api\tests\test_canonical.py .                                   [ 16%]
services\api\tests\test_facilities.py ...............                    [ 34%]
services\api\tests\test_health.py ..                                     [ 37%]
services\api\tests\test_materials.py .........                           [ 48%]
services\api\tests\test_media.py ........                                [ 57%]
services\api\tests\test_price_pipeline.py ..............                 [ 74%]
services\api\tests\test_pricing.py ...                                   [ 78%]
services\api\tests\test_reference.py ......                              [ 85%]
services\api\tests\test_schema.py ......                                 [ 92%]
services\api\tests\test_security.py ...                                  [ 96%]
services\api\tests\test_storage.py ...                                   [100%]

======================= 83 passed, 4 warnings in 7.53s ========================
```
