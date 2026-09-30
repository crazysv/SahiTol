# Test Evidence: T011 Create Attributed Price Seed and Observation Pipeline

## Metadata
- **Task ID**: T011
- **Phase**: Stage 1 (Data & Backend Setup)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Reviewer**: SahiTol Engineering & Pricing Working Group

## Context & Objectives
Implements the attributed price seed and observation pipeline for informal e-waste materials, addressing:
- Importing dated public buying, quoted, and selling observations with complete metadata (material ID, subcategory, region, condition, rate in integer paise per unit, unit of measurement, observed timestamp, source attribution, and usage licence).
- Partitioning demonstration and simulated price series (`is_demo=True`) to prevent contamination of live statistical summaries.
- Observation entry and review pipeline (`POST /api/v1/prices/observations`) with strict validation: rejecting future dates (>5 minutes drift quarantined with HTTP 422), non-positive rates, and uncataloged materials.
- Admin moderation workflow (`GET /api/v1/admin/price-review` and `POST /api/v1/admin/price-review/{id}/decision`) allowing verified review status transitions (`VERIFIED`, `REJECTED` with reason) while safeguarding private contributor identity from public endpoints.
- Real-time statistical aggregation under `PRICE_V1`: calculating weighted quantiles (Q1, median, Q3) using the first-cumulative method, evaluating sample confidence (`HIGH`, `MEDIUM`, `LOW`, `INSUFFICIENT_DATA`), and enforcing that empty cohorts return `INSUFFICIENT_DATA` with null quantiles (never zero or synthetic substitutes).
- Preserving honest historical trend gaps (`GET /api/v1/prices/trends`) without interpolating fabricated points.
- Lot valuation range estimation (`POST /api/v1/prices/estimate`) conforming strictly to TECHSPEC line 65.

## Requirements & Acceptance Case Mapping
| Requirement | Test ID | Scope | Contributing Tasks | Implementation & Evidence Summary |
|---|---|---|---|---|
| R-PRICE-01 | AT-016 | RELEASE | T011, T020 | Public price observation submission (`POST /api/v1/prices/observations`) validates material, region, date, rate in positive paise, unit, price kind (`BUY`, `QUOTE`, `SELL`), and source attribution. Observations enter `PENDING_REVIEW`. Admin moderation (`GET /api/v1/admin/price-review`, `POST /api/v1/admin/price-review/{id}/decision`) enables approval or rejection with documented justification. Future dates are quarantined with HTTP 422. Identity-safe public listing (`GET /api/v1/prices/observations`) redacts contributor personal data. |
| R-DATA-02 | AT-054 | RELEASE | T011, T018, T031, T047 | Full lifecycle: Seed import (`data/seeds/price_observations.json`), database seeder (`services/api/app/db/seeds/prices.py`), validation, moderation, weighted quantile aggregation (`GET /api/v1/prices/summary`), trend reporting with gap preservation (`GET /api/v1/prices/trends`), demo partition isolation (`is_demo=True` excluded from live summaries), and curated dataset export (`data/curated/price_observations/`) with SHA-256 cryptographic manifest. |

## Observable Artifact Outputs
1. **Canonical Dated Seeds (`data/seeds/price_observations.json`)**:
   - 12 dated price observations spanning Delhi-NCR and Maharashtra secondary markets (Mayapuri, Seelampur, MIDC benchmarks) across PCB grades, lead-acid batteries, and copper cables.
   - Attributed to verified secondary sources: `SRC-01` (CPCB/MoEFCC), `SRC-04` (Delhi Scrap Market Survey), and `SRC-05` (MIDC Industrial Metal Benchmark).

2. **Database Seeder (`services/api/app/db/seeds/prices.py`)**:
   - Seeds `DataSource` records (`SRC-04`, `SRC-05`, `SRC-01`), ensures regional reference records exist (`DELHI_NCR`, `MAHARASHTRA`), and populates `PriceObservation` records with UUID primary keys and ISO timestamps.

3. **FastAPI Prices Router (`services/api/app/routers/prices.py`)**:
   - `POST /api/v1/prices/observations`: Validates and ingests dated observations into `PENDING_REVIEW`.
   - `GET /api/v1/prices/observations`: Identity-safe listing filtered by material, region, price kind, review status, and demo partition.
   - `GET /api/v1/prices/summary`: Computes `PRICE_V1` weighted quantiles, confidence rating, independent source counts, and reason codes. Empty cohorts return `INSUFFICIENT_DATA` and null rates.
   - `GET /api/v1/prices/trends`: Daily aggregation buckets with preserved gaps.
   - `POST /api/v1/prices/estimate`: Low, median, and high valuation range in integer paise.

4. **FastAPI Admin Moderation Router (`services/api/app/routers/admin.py`)**:
   - `GET /api/v1/admin/price-review`: Lists pending or rejected observations for moderator action.
   - `POST /api/v1/admin/price-review/{id}/decision`: Sets `VERIFIED` or `REJECTED` with audit reason.

5. **Curated Export Package (`data/curated/price_observations/`)**:
   - `price_observations.csv` (1,961 bytes, SHA-256: `de4d9531ea8705cd2e946d92ec03b7b4ae999c63af35d14342b3a26fd97d5e40`)
   - `price_observations.json` (5,576 bytes, SHA-256: `2256f88a81d66ba7bc3d8f7b93ab79dd6f923e3bcb57a3497047dac9e4fbc852`)
   - `price_summaries.json` (2,359 bytes, SHA-256: `0d3146421a4052099f34b8c61e7e8308cf381d9dd048e4138403477c6c9e5137`)
   - `manifest.json` (1,570 bytes) detailing origin classes, source kinds, demo partition counts, and limitations disclosure.

6. **Automated Test Suite (`services/api/tests/test_price_pipeline.py`)**:
   - 14 automated tests verifying database seeding, identity-safe listing, submission validation, future-date quarantine, rate validation, admin moderation (approve/reject), `PRICE_V1` quantiles, empty cohort `INSUFFICIENT_DATA` enforcement, trend gap preservation, demo partition isolation, and valuation estimation.

## Test Verification Output
```text
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\SahiTol\services\api
configfile: pyproject.toml
plugins: anyio-4.14.1, langsmith-0.10.6, asyncio-1.4.0, cov-7.1.0, mock-3.15.1
asyncio: mode=auto, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 14 items

services\api\tests\test_price_pipeline.py ..............                 [100%]

======================= 14 passed, 3 warnings in 0.59s ========================
```

Full API test suite verification:
```text
collected 68 items

services\api\tests\test_auth.py .............                            [ 19%]
services\api\tests\test_canonical.py .                                   [ 20%]
services\api\tests\test_health.py ..                                     [ 23%]
services\api\tests\test_materials.py .........                           [ 36%]
services\api\tests\test_media.py ........                                [ 48%]
services\api\tests\test_price_pipeline.py ..............                 [ 69%]
services\api\tests\test_pricing.py ...                                   [ 73%]
services\api\tests\test_reference.py ......                              [ 82%]
services\api\tests\test_schema.py ......                                 [ 91%]
services\api\tests\test_security.py ...                                  [ 95%]
services\api\tests\test_storage.py ...                                   [100%]

======================= 68 passed, 4 warnings in 6.55s ========================
```
