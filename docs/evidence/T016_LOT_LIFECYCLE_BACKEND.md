# Test Evidence: T016 Implement Lot and Lifecycle Backend

## Metadata
- **Task ID**: T016
- **Phase**: Stage 2 (Offline Core & WorkManager Synchronization)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Reviewer**: SahiTol Core Domain & Material Traceability Working Group

## Context & Objectives
Implements the material lot lifecycle and valuation backend as specified in `docs/06_SCHEMA.md`, `docs/04_APPFLOW.md`, and `docs/16_API_CONTRACT.md`, satisfying requirements `R-LOT-03`, `R-LOT-04`, `R-LOT-05`, and `R-DATA-01`:
1. **Command Endpoints & State Machine**:
   - `POST /api/v1/lots`: Create draft lot command validating owner checks, positive integer grams (max 50 metric tonnes), fractional kg round-trip conversion, location provenance, attached photos, and immutable initial domain event.
   - `PATCH /api/v1/lots/{id}`: Update draft lot fields with optimistic version control (`expected_version`). Strictly prohibits direct arbitrary `status` mutation (returning HTTP 422 with `ARBITRARY_STATUS_MUTATION_PROHIBITED`).
   - `POST /api/v1/lots/{id}/collect`: Finalize collection transitioning `DRAFT -> COLLECTED`, enforcing mandatory material classification confirmation and positive finite weight in integer grams.
   - `POST /api/v1/lots/{id}/list`: Market listing command transitioning `COLLECTED -> LISTED`, requiring route revalidation to ensure hazardous/battery/e-waste materials are safely routed before entering recycler matching.
   - `POST /api/v1/lots/{id}/cancel`: Cancellation command with mandatory reason string, verifying lot is not already confirmed received/closed (`RECEIVED`, `CLOSED` return HTTP 409 `CANNOT_CANCEL_CONFIRMED_LOT`), emitting deletion tombstone `SyncChange`.
   - `POST /api/v1/lots/{id}/estimate`: Computes immutable indicative valuation ranges conforming to `PRICE_V1` (rates in paise per kg, weight in grams), persisting a permanent `ValuationSnapshot`.
2. **Weight Precision & Anomaly Detection**:
   - Positive integer grams enforced at both API schema layer and PostgreSQL `CHECK` constraints.
   - Fractional kilograms (e.g. `12.5 kg`) round-trip cleanly to integer grams (`12500 g`) without precision loss.
   - Suspiciously large weights (>500 kg) are not arbitrarily blocked or capped at collection time; instead, they are recorded and automatically flagged via `QualityFlag` (`LARGE_WEIGHT_ANOMALY`) for supervisor/admin review.
3. **Location Quality & Privacy Protection**:
   - Coordinates captured via GPS or manual entry are stored in `location_records` with provenance metadata (`source`, `accuracy_m`, `age_ms`, `coarse_area`, `consent_version`).
   - Detailed lot projections (`GET /api/v1/lots/{id}`) redact exact GPS coordinates, exposing only coarse area and quality provenance to protect collector safety and privacy.
4. **Append-Only Domain Events & Hash Chain**:
   - Every lifecycle transition (`LOT_CREATED`, `LOT_UPDATED`, `LOT_COLLECTED`, `LOT_LISTED`, `LOT_CANCELLED`) appends an immutable record to `domain_events` with monotonic sequence, actor ID, previous/next states, canonical payload hash, and SHA-256 event hash chaining (`prev_hash` -> `event_hash`).
5. **Ownership Isolation & Scoping**:
   - Collectors can only view, update, list, cancel, or estimate their own lots.
   - Recyclers can only query market-eligible lots (`LISTED`, `MATCHED`, `IN_TRANSIT`, `DELIVERED`).
   - Admins retain unrestricted audit and moderation access.

## Requirements & Acceptance Case Mapping
| Requirement | Test ID | Scope | Contributing Tasks | Implementation & Evidence Summary |
|---|---|---|---|---|
| R-LOT-03 | AT-013 | RELEASE | T016, T017 | Collect and sync lot with photo, coarse location provenance, positive weight, and recommended route. Enforced in `POST /api/v1/lots` and `POST /api/v1/lots/{id}/collect`. Automated test: `test_create_lot_draft_and_domain_effects`, `test_location_provenance_gps_and_manual_coarse`, `test_collection_requires_material_and_weight`. (Cross-task case with mobile UI in T017). |
| R-LOT-04 | AT-014 | RELEASE | T016, T024 | Prohibit arbitrary status PATCH, enforce allowed lifecycle transitions (`DRAFT -> COLLECTED -> LISTED`), disallow cancelling confirmed lots, and emit audit domain events. Enforced in `PATCH /api/v1/lots/{id}` and transition endpoints. Automated tests: `test_arbitrary_status_patch_prohibited`, `test_lifecycle_transition_draft_to_collected_and_listed`, `test_illegal_transitions_prevented`, `test_cancel_lot_with_reason_and_tombstone`. (Cross-task case with recycler console in T024). |
| R-LOT-05 | AT-015 | RELEASE | T013, T016, T017 | Material and weight confirmation required before collection finalization; indicative valuation snapshot calculated in paise. Enforced in `POST /api/v1/lots/{id}/collect` and `POST /api/v1/lots/{id}/estimate`. Automated tests: `test_collection_requires_material_and_weight`, `test_estimate_lot_valuation`. (Cross-task case with Android in T013/T017). |
| R-DATA-01 | AT-053 | RELEASE | T010, T016, T031, T047 | Fractional kg to integer gram round-trip conversion without truncation; suspicious large weight (>500kg) flagged in `quality_flags` without rejecting collection arbitrarily. Automated tests: `test_weight_validation_and_fractional_kg_round_trip`, `test_suspicious_large_weight_quality_flag_without_cap`. (Cross-task case with quality dashboard in T031/T047). |

## Observable Artifact Outputs
1. **Lot and Lifecycle Router (`services/api/app/routers/lots.py`)**:
   - `POST /api/v1/lots`: Draft lot creation, positive integer gram validation, fractional kg conversion, location provenance, photo attachments, quality flag generation for large weights, domain event logging, and sync delta emission.
   - `GET /api/v1/lots`: Role-scoped lot listing (collectors see own, recyclers see listed, admins see all).
   - `GET /api/v1/lots/{id}`: Detailed projection redacting private coordinates, returning location quality, images, events, and flags.
   - `PATCH /api/v1/lots/{id}`: Draft updates with optimistic concurrency check (`expected_version`), strictly prohibiting arbitrary status mutations with HTTP 422 `ARBITRARY_STATUS_MUTATION_PROHIBITED`.
   - `POST /api/v1/lots/{id}/collect`: Finalize collection: validates status is `DRAFT`, material is confirmed, weight is positive finite integer grams, emits `LOT_COLLECTED`.
   - `POST /api/v1/lots/{id}/list`: Market listing: validates status is `COLLECTED`, revalidates regulatory route against `ALLOWED_ROUTES`, emits `LOT_LISTED`.
   - `POST /api/v1/lots/{id}/cancel`: Cancellation with mandatory reason string, verifying lot is not already confirmed received/closed, emits `LOT_CANCELLED` and deletion tombstone `SyncChange`.
   - `POST /api/v1/lots/{id}/estimate`: Immutable lot valuation range calculation conforming to `PRICE_V1` benchmark rates in paise per kg, saving immutable `ValuationSnapshot`.

2. **Automated Test Suite (`services/api/tests/test_lots.py`)**:
   - 14 comprehensive automated unit and integration tests passing:
     - `test_create_lot_draft_and_domain_effects`: Creates draft lot with domain event and sync change.
     - `test_weight_validation_and_fractional_kg_round_trip`: Verifies fractional kg to integer grams conversion and rejection of non-positive/excessive weights.
     - `test_suspicious_large_weight_quality_flag_without_cap`: Confirms lots >500 kg are created successfully and flagged via `QualityFlag`.
     - `test_location_provenance_gps_and_manual_coarse`: Verifies GPS and manual location capture with accuracy and age.
     - `test_lot_get_detail_projection_redacts_private_coords`: Confirms private coordinates are redacted while coarse area and quality provenance are exposed.
     - `test_arbitrary_status_patch_prohibited`: Verifies direct status modification in PATCH returns HTTP 422 with `ARBITRARY_STATUS_MUTATION_PROHIBITED`.
     - `test_update_draft_fields_and_version_increment`: Validates optimistic concurrency version increment and field updating.
     - `test_update_draft_version_conflict`: Validates HTTP 409 `VERSION_CONFLICT` on mismatched version.
     - `test_lifecycle_transition_draft_to_collected_and_listed`: Validates full forward transition pipeline (`DRAFT -> COLLECTED -> LISTED`).
     - `test_collection_requires_material_and_weight`: Validates collection fails if material is unassigned or weight is non-positive.
     - `test_illegal_transitions_prevented`: Validates illegal transitions (e.g. `DRAFT -> LISTED`, `COLLECTED -> DRAFT`) return HTTP 409.
     - `test_cancel_lot_with_reason_and_tombstone`: Validates cancellation with reason, deletion tombstone emission, and prohibition of cancelling received lots.
     - `test_owner_isolation_and_scoping`: Verifies cross-collector access is blocked with HTTP 403.
     - `test_estimate_lot_valuation`: Validates indicative valuation range calculation in paise with confidence level and disclaimer.

3. **Test Infrastructure Support (`services/api/tests/test_db.py`)**:
   - Uses the T006 SQLite spatial converter, which normalizes EWKT geometry strings to valid hex EWKB for GeoAlchemy2 reads in the in-memory test database.

## 2026-10-01 independent re-verification

The location-bearing lot flows were re-run after the T006 test-double repair:

```text
PYTHONPATH="services/api:." uv run --python 3.10 --with-requirements services/api/requirements.txt --with pytest==8.3.3 --with pytest-asyncio==0.24.0 --with numpy==1.26.4 --with pandas==2.2.3 --with shapely==2.0.6 pytest services/api/tests/test_lots.py -q
14 passed in 0.68s
```

This covers persisted GPS/manual coarse locations in addition to lifecycle,
ownership, validation, event-chain, and valuation behaviour.
