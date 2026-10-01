# Test Evidence: T019 Implement Eligible Recycler Matching and Map Data

## Metadata
- **Task ID**: T019
- **Phase**: Stage 3 (Intelligence, Matching & Offers)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Reviewer**: SahiTol Recycler Matching & Spatial Data Working Group

## Context & Objectives
Implements the eligible recycler matching engine, explainable multi-factor ranking, deterministic tie-breaking, offline parity fixtures, and GeoJSON map data conforming strictly to policy `MATCH_V1` ([03_TECHSPEC.md](../03_TECHSPEC.md) lines 67–84), [16_API_CONTRACT.md](../16_API_CONTRACT.md) line 52, and [22_REGULATORY_SAFETY.md](../22_REGULATORY_SAFETY.md):
1. **Hard Eligibility Filters & Battery Isolation Invariant (`R-REC-04`, `AT-024`)**:
   - `ROUTE_INCOMPATIBLE`: Enforces regulatory route compatibility. Crucially, battery lots (`BATTERY_ISOLATION` route or battery material category) cannot match facilities evidenced only for e-waste (e.g. Greentech Recyclers). General recycling and unauthorized facilities are excluded before ranking.
   - `MATERIAL_UNACCEPTED`: Facilities must have verified evidence of accepting the lot's specific material ID.
   - `EXPIRED_REGISTRATION`: Registrations must be in `VALID` status with `valid_until >= now`. Expired authorizations (e.g. NDMC Collection Point) are excluded.
   - `VERIFICATION_INSUFFICIENT` (`AT-022`): L0 (demo), L1, and L2 facilities never qualify as verified formal destinations. When formal destination compliance is required, only L3/L4 with active valid status match.
   - `WEIGHT_INCOMPATIBLE`: Lots with weight below a facility's `min_weight_g` or above `max_weight_g` are excluded.
   - `OPERATIONALLY_CLOSED`: Facilities with self-declared operational status `PAUSED` or `CLOSED` are excluded.
   - `DISTANCE_EXCEEDED`: Straight-line distance from PostGIS / Haversine exceeding `search_radius_m` (default 50 km) excludes the candidate.
   - `DEMO_MISMATCH`: Synthetic demo lots only match demo facilities (`is_demo == True`); real lots only match real facilities.
2. **Explainable Multi-Factor Ranking (`R-REC-05`, `AT-025`)**:
   - Evaluates eligible candidates using five normalized factors:
     - **Distance (30%)**: Straight-line distance in metres, normalized as `max(0, 1 - distance / search_radius)`. Missing GPS omits distance contribution without inventing fake coordinates.
     - **Comparable Offered Rate (30%)**: Min-max normalized across active quotes for the lot's material. Candidates with missing rates receive 0 contribution with explicit explanation, never inserting 0 rupees quotes.
     - **Pickup (20%)**: `1.0` if pickup is available for the lot/location, `0.0` for drop-off only, `0.0` with explicit "unknown" label if unverified.
     - **Availability (15%)**: `1.0` for current confirmed operational acceptance (`ACCEPTING`), `0.5` for unknown, `0.0` for paused/closed.
     - **Reliability (5%)**: Completed historical transaction ratio (`completed / total`) for facilities with $\ge 5$ transactions. Facilities with $<5$ transactions receive a baseline `0.5` explicitly labeled "no history".
   - Total score: $100 \times \text{weighted sum}$.
   - Deterministic tie-breaking: Shorter distance ascending, then stable facility UUID string ascending.
   - Rank 1 candidate is flagged `is_recommended = True`.
3. **No Matches Path & Transparent Exclusions (`R-REC-06`, `AT-026`)**:
   - When no candidates qualify within the search radius, the engine returns an empty match list with transparent `exclusion_counts: Dict[str, int]`.
   - Regulatory routes and material acceptance requirements are never relaxed.
4. **Local Haversine Parity with PostGIS (`AT-025`)**:
   - Pure domain Haversine calculator in `services/api/app/domain/matching.py` with earth radius $R = 6,371,000$ m.
   - Validated against PostGIS WGS84 ellipsoidal reference distances with relative error $< 0.07\%$ (well below the $0.5\%$ tolerance ceiling).
5. **GeoJSON Map Data & Static Fallback Fixtures (`R-REC-06`, `AT-026`)**:
   - `GET /api/v1/facilities/geojson`: Dynamic GeoJSON `FeatureCollection` for MapLibre rendering, including Point coordinates, statutory disclaimers, authorized routes, accepted materials, and verification levels.
   - Generated static vector fixtures: [`data/fixtures/facilities_map.geojson`](file:///d:/SahiTol/data/fixtures/facilities_map.geojson) and [`apps/web/public/fixtures/facilities_map.geojson`](file:///d:/SahiTol/apps/web/public/fixtures/facilities_map.geojson).
6. **Canonical Shared Fixtures**:
   - Published [`data/fixtures/matching_v1_fixtures.json`](file:///d:/SahiTol/data/fixtures/matching_v1_fixtures.json) and mirrored to [`apps/android/app/src/test/resources/fixtures/matching_v1_fixtures.json`](file:///d:/SahiTol/apps/android/app/src/test/resources/fixtures/matching_v1_fixtures.json).

## Requirements & Acceptance Case Mapping
| Requirement | Test ID | Scope | Contributing Tasks | Implementation & Evidence Summary |
|---|---|---|---|---|
| R-REC-04 | AT-024 | RELEASE | T019, T023 | Route-aware eligibility hard filtering: battery lots cannot match general e-waste facilities (`Greentech` excluded with `ROUTE_INCOMPATIBLE`), while authorized battery isolation facilities (`Eco-Battery`) match. Incompatible materials, expired registrations, and out-of-bound weights reject before ranking. Automated tests: `test_battery_isolation_route_invariant`, `test_ewaste_lot_matches_authorized_ewaste_facilities`, `test_facility_weight_bounds_rejection`. |
| R-REC-05 | AT-025 | RELEASE | T019, T020 | Deterministic 5-factor scoring (30/30/20/15/5%), stable tie-breaking, and transparent factor contributions and missing-data explanations. Haversine distance matches canonical fixture within 0.07% of PostGIS. Automated tests: `test_haversine_distance_parity_with_fixture`, `test_explainable_ranking_and_factor_weights`, `test_deterministic_tie_breaking`. |
| R-REC-06 | AT-026 | RELEASE | T019, T020 | Narrow search radius yields empty matches with transparent exclusion counts without switching battery route. Dynamic `GET /api/v1/facilities/geojson` and static MapLibre fixtures provide offline/fallback map capability. Automated tests: `test_no_matches_path_preserves_exclusions_and_route`, `test_facilities_geojson_endpoint`. |
| R-REC-02 | AT-022 | RELEASE | T012, T019, T029 | L0/L1/L2 facilities excluded from formal destination matches (`VERIFICATION_INSUFFICIENT`); L3/L4 with active valid status match with `is_formal_destination=True`. Automated test: `test_formal_destination_requirement_filter`. |

## Observable Artifact Outputs
1. **Pure Domain Matching Engine (`services/api/app/domain/matching.py`)**:
   - `haversine_distance_m`: Haversine formula calculation.
   - `extract_coordinates`: Extracts latitude/longitude from PostGIS/GeoAlchemy2 geometries across PostgreSQL and SQLite.
   - `evaluate_candidate_eligibility`: Hard filters for route, material, registration, verification level, weight, operational status, and distance.
   - `rank_eligible_candidates`: Weighted factor scoring (distance, rate, pickup, availability, reliability) and stable tie-breaking.
   - `match_lot_to_facilities`: Main matching orchestrator with transparent exclusion counts and user-facing messages.
2. **FastAPI Endpoints**:
   - `POST /api/v1/lots/{lot_id}/matches`: Matches lot to eligible recyclers with request options (`search_radius_m`, `require_formal_destination`, `latitude`, `longitude`, `coarse_area`).
   - `GET /api/v1/facilities/geojson`: Returns GeoJSON FeatureCollection with points and verified properties.
3. **Canonical Shared Fixtures**:
   - [`data/fixtures/matching_v1_fixtures.json`](file:///d:/SahiTol/data/fixtures/matching_v1_fixtures.json): Machine-readable tests covering Haversine distance, battery isolation, formal verification levels, weight bounds, and 5-factor ranking.
   - [`apps/android/app/src/test/resources/fixtures/matching_v1_fixtures.json`](file:///d:/SahiTol/apps/android/app/src/test/resources/fixtures/matching_v1_fixtures.json): Mirrored Android test resource.
4. **GeoJSON Map Fixtures**:
   - [`data/fixtures/facilities_map.geojson`](file:///d:/SahiTol/data/fixtures/facilities_map.geojson): GeoJSON FeatureCollection for offline backend and map verification.
   - [`apps/web/public/fixtures/facilities_map.geojson`](file:///d:/SahiTol/apps/web/public/fixtures/facilities_map.geojson): Static web fallback for MapLibre client rendering.
5. **Automated Test Suite (`services/api/tests/test_matching.py`)**:
   - 10 comprehensive tests covering all hard filters, ranking weights, tie-breaking, no-match paths, GeoJSON outputs, and collector ownership scoping.

## Test Verification Output
```text
$env:PYTHONPATH="d:\SahiTol;d:\SahiTol\services\api"; & C:\Python310\python.exe -m pytest services/api/tests/test_matching.py -v

services\api\tests\test_matching.py::test_haversine_distance_parity_with_fixture PASSED [ 10%]
services\api\tests\test_matching.py::test_battery_isolation_route_invariant PASSED [ 20%]
services\api\tests\test_matching.py::test_ewaste_lot_matches_authorized_ewaste_facilities PASSED [ 30%]
services\api\tests\test_matching.py::test_formal_destination_requirement_filter PASSED [ 40%]
services\api\tests\test_matching.py::test_explainable_ranking_and_factor_weights PASSED [ 50%]
services\api\tests\test_matching.py::test_deterministic_tie_breaking PASSED [ 60%]
services\api\tests\test_matching.py::test_facility_weight_bounds_rejection PASSED [ 70%]
services\api\tests\test_matching.py::test_no_matches_path_preserves_exclusions_and_route PASSED [ 80%]
services\api\tests\test_matching.py::test_facilities_geojson_endpoint PASSED [ 90%]
services\api\tests\test_matching.py::test_collector_ownership_enforced_on_matches PASSED [100%]
======================== 10 passed, 1 warning in 0.73s ========================
```

Full API test suite verification:
```text
======================= 127 passed, 8 warnings in 9.43s =======================
```

## 2026-10-01 independent re-verification

The matching engine's location reads were re-run after the T006 SQLite
geometry test-double repair:

```text
PYTHONPATH="services/api:." uv run --python 3.10 --with-requirements services/api/requirements.txt --with pytest==8.3.3 --with pytest-asyncio==0.24.0 --with numpy==1.26.4 --with pandas==2.2.3 --with shapely==2.0.6 pytest services/api/tests/test_matching.py -q
10 passed in 0.56s
```

The successful checks include the battery-route hard guard, formal-destination
filtering, distance/ranking explanations, no-match exclusions, GeoJSON, and
collector ownership isolation.
