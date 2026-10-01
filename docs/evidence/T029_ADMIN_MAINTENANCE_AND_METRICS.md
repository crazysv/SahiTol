# Test Evidence: T029 Implement Admin Maintenance and Metrics APIs

## 2026-10-01 independent repair and verification

The T029 audit confirmed role-scoped maintenance, minimal collector data,
persisted-table metrics and hash-chained events, then corrected two missing
audit controls:

1. `GET /api/v1/admin/events` now accepts inclusive `occurred_from` and
   `occurred_to` UTC filters, alongside its existing aggregate/type/actor
   filters.
2. `POST /api/v1/admin/price-review/{id}/decision` now requires a justification
   for **both** approval and rejection, and commits a
   `PRICE_OBSERVATION_REVIEWED` append-only event with actor, decision, reason,
   previous status and resulting status.

Verification after repair:

```text
pytest services/api/tests/test_admin_maintenance.py -q
10 passed, 1 warning in 1.41s
```

The event-search test exercises the date bounds; the price-review test proves a
non-admin is rejected, an admin approval with reason persists the review event,
and a missing reason is rejected. The warning is a third-party Starlette
deprecation; no test failed.

## Metadata
- **Task ID**: T029
- **Phase**: Stage 5 (Data Quality, Anomaly Detection & Admin Governance)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Reviewer**: SahiTol Core Backend & Data Governance Working Group

## Context & Objectives
Implements administrative maintenance, verification review, taxonomy lifecycle management, audit trails, and platform metrics APIs in [`services/api/app/routers/admin.py`](../../services/api/app/routers/admin.py). Fulfills requirements `R-ADMIN-01`, `R-ADMIN-02`, `R-ADMIN-03`, `R-ADMIN-04`, `R-ADMIN-05`, `R-ADMIN-06`, `R-PRICE-05`, `R-HAND-05`, and `R-OPS-04`, contributing to acceptance cases `AT-064`, `AT-065`, and `AT-077`:

1. **Role Scoping & Authorization Protection (`R-ADMIN-01`, `R-ADMIN-02`, `AT-064`)**:
   - All admin endpoints (`/api/v1/admin/*` and `/admin/*`) strictly enforce `require_roles(UserRole.ADMIN)`.
   - Ordinary collectors and recyclers attempting to access admin endpoints receive HTTP 403 Forbidden.
   - Recycler self-approval is architecturally prohibited: facility verification assertions are strictly admin-controlled via `FacilityAuthorization` records with mandatory reviewer ID and justification audit.

2. **Platform Overview & Live Metrics (`R-ADMIN-06`, `AT-077`)**:
   - `GET /api/v1/admin/overview` and `/admin/overview`:
     - Calculates aggregate statistics directly from persisted database tables (`collectors`, `facilities`, `lots`, `handovers`, `transactions`, `payments`, `quality_flags`).
     - Strictly separates demo data from real impact totals; `formal_received_mass_g` excludes all demo lots/transactions.
     - Enforces the honest metric label: `"received, not recycled"` (`mass_label`).
     - Financial tallies reflect cash-first operational assertions: `gross_agreed_paise`, `acknowledged_paid_paise`, `outstanding_dues_paise`, and `disputed_paise`.
     - Explicitly surfaces `"unmet_fieldwork_obligation": "UNMET"` preserving desk-research truthfulness.
   - `GET /api/v1/admin/metrics`: Returns verified live table counts with real denominators (`active_collectors`, `verified_facilities`, `recorded_transactions`).

3. **Minimal Collector Directory View (`R-ADMIN-04`)**:
   - `GET /api/v1/admin/collectors`:
     - Returns minimal administrative summary profiles (`id`, `display_alias`, `preferred_language`, `region_id`, `general_area`, `total_lots_created`, `active_lots_count`, `created_at`).
     - Strictly omits private collector phone numbers, PIN hashes, auth tokens, device fingerprints, and GPS coordinates to protect informal waste pickers.
     - Logs sensitive directory access with an append-only `DomainEvent` (`COLLECTOR_DIRECTORY_ACCESSED`) recording the actor, role, and query filters.

4. **Taxonomy & Safety Guide Maintenance (`R-ADMIN-03`, `AT-064`)**:
   - `GET/POST /api/v1/admin/materials`, `PATCH /api/v1/admin/materials/{id}`:
     - Allows admin creation and updating of material categories and items.
     - Preserves historical material IDs across updates to ensure old digital receipts and handover records never have broken foreign keys.
   - `POST /api/v1/admin/material-aliases`, `DELETE /api/v1/admin/material-aliases/{id}`:
     - Localized term aliasing with case-insensitive whitespace normalization and uniqueness checking.
     - Emits `MATERIAL_ALIAS_CREATED` and `MATERIAL_ALIAS_DELETED` domain events.
   - `GET/POST /api/v1/admin/safety-guides`, `PATCH /api/v1/admin/safety-guides/{id}`:
     - Versioned hazard guides with localized audio key mappings and review state (`PENDING_REVIEW`, `APPROVED`, `REJECTED`, `ARCHIVED`).
     - Emits `SAFETY_GUIDE_CREATED` and `SAFETY_GUIDE_UPDATED` domain events.

5. **Facility Verification Review Workflow (`R-ADMIN-01`, `AT-064`)**:
   - `POST /api/v1/admin/facilities/{id}/verification`:
     - Admin asserts verified regulatory authorization evidence (`authority`, `reference`, `valid_from`, `valid_until`, `verification_level`, `source_id`, `reason`).
     - Creates auditable `FacilityAuthorization` entry rather than arbitrary unverified badges.
     - Emits `FACILITY_VERIFICATION_ASSERTED` domain event.

6. **Audit Trail Search & Cryptographic Traceability (`R-ADMIN-05`, `AT-077`)**:
   - `GET /api/v1/admin/events`:
     - Allows searching append-only domain events by `aggregate_type`, `aggregate_id`, `event_type`, `actor_id`, and date ranges.
   - `GET /api/v1/admin/traceability/{lot_id}`:
     - Verifies cryptographic hash chain integrity for any scrap lot (`is_hash_chain_valid = True`).
     - Assembles chronological lifecycle event timeline linking collection, quotes, negotiations, handover proposals, revisions, and payment assertions.

7. **Attributed Price Moderation Workflow (`R-ADMIN-02`, `AT-064`)**:
   - `GET /api/v1/admin/price-review` and `POST /api/v1/admin/price-review/{id}/decision`:
     - Allows admin review of pending market quote submissions.
     - Transitions status to `VERIFIED` or `REJECTED` with mandatory reasoning, emitting `PRICE_OBSERVATION_REVIEWED` domain events.

## Test Verification
- **Dedicated Test Suite**: [`services/api/tests/test_admin_maintenance.py`](../../services/api/tests/test_admin_maintenance.py)
  - `test_admin_overview_unauthorized_for_collector_and_recycler`: Verifies HTTP 403 Forbidden for non-admin actors.
  - `test_recycler_cannot_approve_itself`: Verifies ordinary recyclers cannot self-approve authorizations.
  - `test_admin_overview_metrics_with_real_denominators`: Verifies live table calculations, demo data isolation, honest mass label, and cash-first payment tallies.
  - `test_collector_minimal_directory_and_access_audit`: Verifies privacy protection, exclusion of PII/PIN/phone, and sensitive access event logging.
  - `test_admin_material_catalog_crud_and_preservation`: Verifies material creation, update, ID retention, and event emission.
  - `test_admin_material_alias_management`: Verifies alias creation, normalization, conflict rejection, deletion, and event emission.
  - `test_admin_safety_guide_maintenance`: Verifies safety guide versioning, review status updates, and event emission.
  - `test_facility_verification_review_asserts_evidence`: Verifies admin authorization assertion with justification and event emission.
  - `test_event_search_and_lot_traceability`: Verifies audit event searching and cryptographic hash chain verification.
  - `test_price_review_moderation_requires_admin_and_updates_status`: Verifies price moderation workflow.
- **Results**: 10/10 passed in 0.85s.
- **Full Test Suite**: 211/211 passed across all modules in 16.87s with 0 regressions.

## Verification Log
```text
pytest services/api/tests/test_admin_maintenance.py -v
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1
collected 10 items

services\api\tests\test_admin_maintenance.py::test_admin_overview_unauthorized_for_collector_and_recycler PASSED [ 10%]
services\api\tests\test_admin_maintenance.py::test_recycler_cannot_approve_itself PASSED [ 20%]
services\api\tests\test_admin_maintenance.py::test_admin_overview_metrics_with_real_denominators PASSED [ 30%]
services\api\tests\test_admin_maintenance.py::test_collector_minimal_directory_and_access_audit PASSED [ 40%]
services\api\tests\test_admin_maintenance.py::test_admin_material_catalog_crud_and_preservation PASSED [ 50%]
services\api\tests\test_admin_maintenance.py::test_admin_material_alias_management PASSED [ 60%]
services\api\tests\test_admin_maintenance.py::test_admin_safety_guide_maintenance PASSED [ 70%]
services\api\tests\test_admin_maintenance.py::test_facility_verification_review_asserts_evidence PASSED [ 80%]
services\api\tests\test_admin_maintenance.py::test_event_search_and_lot_traceability PASSED [ 90%]
services\api\tests\test_admin_maintenance.py::test_price_review_moderation_requires_admin_and_updates_status PASSED [100%]

======================== 10 passed, 1 warning in 0.85s ========================

pytest services/api/tests -q
........................................................................ [ 34%]
........................................................................ [ 68%]
...................................................................      [100%]
211 passed, 10 warnings in 16.87s
```
