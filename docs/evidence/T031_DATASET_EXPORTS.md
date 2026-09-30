# Test Evidence: T031 Implement Seven Dataset Exports, Recycler Procurement Logs, and Data Lineage

## Metadata
- **Task ID**: `T031`
- **Phase**: Stage 5 (Backend Integration, Admin, and Production Readiness)
- **Scope**: RELEASE
- **Date**: 2026-09-30
- **Environment**:
  - Python 3.12.12, FastAPI 0.115.0, SQLAlchemy 2.0.35, Pydantic 2.9.2
  - Pytest 9.1.1, Pytest-Asyncio 1.4.0
  - React 18.3.1, TypeScript 5.5.3, Vite 5.4.6, Vitest 2.1.9
  - Dataset Curated Root: `data/curated/`

---

## Requirements and Acceptance Coverage

| Requirement | Test ID | Scope | Verification Status | Implementation & Evidence Notes |
|---|---|---|---|---|
| **R-HAND-06** | **AT-034** | RELEASE | Partially verified (T031 server exports) | Implemented `/api/v1/recycler/procurement-log` and client-side procurement export with statutory non-EPR disclosure comment header and `X-SahiTol-Disclaimer` HTTP header: *"SahiTol Digital Handover Record is a verification of physical scrap receipt, not a statutory EPR certificate. Received mass does not prove recycling."* |
| **R-DATA-01** | **AT-053** | RELEASE | Verified (T031 export router) | Implemented `/api/v1/exports/materials` exporting canonical scrap taxonomy (21 materials), colloquial vernacular aliases, allowed units, and route classifications (`BATTERY_ISOLATED` vs `RECYCLER_STANDARD`) in CSV and JSON with SHA-256 seal. |
| **R-DATA-02** | **AT-054** | RELEASE | Verified (T031 router & lineage) | Closed-loop price observation feedback: closing a transaction with confirmed handover and settled balance automatically generates a `PriceObservation` record tagged `TRANSACTION_OUTCOME` exactly once, guarded against duplicate generation. Exported via `/api/v1/exports/prices`. |
| **R-DATA-03** | **AT-055** | RELEASE | Verified (T031 export router) | Implemented `/api/v1/exports/facilities` exporting regulatory directory, CPCB/SPCB registration IDs, L0–L4 verification levels, authorized materials, and battery acceptance routes. |
| **R-DATA-04** | **AT-056** | RELEASE | Verified (T031 export router) | Implemented `/api/v1/exports/transactions` exporting settled trades with collector and facility IDs, original vs settled scale weights, settled paise values, timestamps, and payment statuses. |
| **R-DATA-05** | **AT-057** | RELEASE | Verified (T031 export router) | Implemented `/api/v1/exports/traceability` exporting immutable append-only `DomainEvent` audit trail with SHA-256 `prev_hash` and `event_hash` linkage, aggregate IDs, and actor roles. |
| **R-DATA-06** | **AT-058** | RELEASE | Verified (T031 export router) | Implemented `/api/v1/exports/collectors` with strict Zero-PII sanitization (phone numbers, private names, and precise GPS excluded; only language preference, account state, and verification badges included). Restricted to `ADMIN` role with 403 Forbidden enforcement. |
| **R-DATA-08** | **AT-060** | RELEASE | Verified (T031 export router) | Strict demo partition filtering (`is_demo=False` default) preventing synthetic or test data from contaminating official platform exports. Fieldwork status explicitly disclosed as `UNMET` in export metadata. |
| **R-DATA-09** | **AT-061** | RELEASE | Verified (T031 curated exports) | Authored `scripts/build_curated_exports.py` packaging all 7 curated dataset families in `data/curated/` with cryptographic `manifest.json` SHA-256 verification seals. |
| **R-DATA-11** | **AT-063** | RELEASE | Verified (T031 admin endpoints) | Implemented `/api/v1/admin/datasets` catalog endpoint and `/api/v1/admin/datasets/{family}/data-card` endpoint returning full Markdown data cards conforming to `docs/templates/DATA_CARD.md`. |
| **R-REG-01** | **AT-071** | RELEASE | Verified (T031 statutory labeling) | Every CSV and JSON export contains the statutory non-EPR disclosure header and identifies records as platform Digital Handover Records without claiming government endorsement or CPCB registry integration. |

---

## 1. Architecture & Implementation

### A. Closed-Loop Price Lineage (`services/api/app/routers/payments.py`)
In accordance with `R-LINE-02` and `AT-054`, when an authorized facility user closes a transaction at `/api/v1/transactions/{id}/close`, the backend performs atomic settlement validation:
1. Validates `handover_confirmed == True`, `dispute_count == 0`, and `remaining_dues == 0`.
2. Inspects existing `PriceObservation` records for `source_id == f"tx-{transaction.id}"`.
3. If not already recorded, inserts a new `PriceObservation`:
   - `material_id = lot.material_id`
   - `price_per_kg_paise = (transaction.agreed_total_paise * 1000) // lot.scale_weight_grams`
   - `observation_type = "TRANSACTION_OUTCOME"`
   - `confidence_score = 1.0` (settled bilateral commercial reality)
   - `recorded_by_user_id = current_user.id`
   - `facility_id = transaction.facility_id`
   - `is_demo = transaction.is_demo`
   - `source_id = f"tx-{transaction.id}"`
4. Emits append-only `DomainEvent` with SHA-256 chaining.

### B. Versioned Export Router (`services/api/app/routers/exports.py`)
Provides production-grade endpoints:
- `GET /api/v1/exports/{dataset}?format=csv|json&is_demo=false`
  - Neutralizes CSV formula injection by prepending `'` to fields starting with `=`, `+`, `-`, or `@`.
  - Injects mandatory statutory non-EPR disclaimer in HTTP header (`X-SahiTol-Disclaimer`) and CSV comment header.
  - Computes deterministic SHA-256 payload digest in `X-SahiTol-SHA256`.
  - Supports all 7 dataset families: `materials`, `prices`, `facilities`, `transactions`, `payments`, `traceability`, `collectors`, plus combined `all`.
- `GET /api/v1/recycler/procurement-log?format=csv|json`
  - Facility-scoped procurement history with scale weights, settled amounts, payment modes, and hash proofs.
- `GET /api/v1/admin/datasets`
  - Admin catalog of all dataset families with live database counts, schema versions, licenses, and links.
- `GET /api/v1/admin/datasets/{family}/data-card`
  - Serves canonical Markdown data cards from repository roots with statutory and unmet fieldwork disclaimers.

### C. Curated Datasets Packaging Tool (`scripts/build_curated_exports.py`)
Created and executed `scripts/build_curated_exports.py` generating all 7 curated dataset packages in `data/curated/`:
1. `data/curated/material_catalog/`: 21 materials, 139 vernacular aliases, safety guides, `data_card.md`, and `manifest.json`.
2. `data/curated/price_observations/`: 18 observations, regional benchmarks, `data_card.md`, and `manifest.json`.
3. `data/curated/facility_directory/`: Regulatory and registered facilities, `data_card.md`, and `manifest.json`.
4. `data/curated/transactions_lifecycle/`: Sample lifecycle records, `data_card.md`, and `manifest.json`.
5. `data/curated/payment_records/`: Cash-first settlement ledger, `data_card.md`, and `manifest.json`.
6. `data/curated/traceability_events/`: Append-only event chains, `data_card.md`, and `manifest.json`.
7. `data/curated/collector_anonymized/`: Zero-PII collector cohort, `data_card.md`, and `manifest.json`.

---

## 2. Test Verification Results

### Backend Test Suite (`services/api/tests/test_exports_and_lineage.py`)
Executed via `uv run pytest`:
```text
============================= test session starts =============================
platform win32 -- Python 3.12.12, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\SahiTol\services\api
collected 10 items

tests/test_exports_and_lineage.py::test_close_transaction_creates_price_observation_once PASSED [ 10%]
tests/test_exports_and_lineage.py::test_export_dataset_materials PASSED  [ 20%]
tests/test_exports_and_lineage.py::test_export_dataset_prices PASSED     [ 30%]
tests/test_exports_and_lineage.py::test_export_dataset_facilities PASSED [ 40%]
tests/test_exports_and_lineage.py::test_export_dataset_transactions PASSED [ 50%]
tests/test_exports_and_lineage.py::test_export_dataset_payments PASSED   [ 60%]
tests/test_exports_and_lineage.py::test_export_dataset_traceability PASSED [ 70%]
tests/test_exports_and_lineage.py::test_export_dataset_collectors_zero_pii_and_auth PASSED [ 80%]
tests/test_exports_and_lineage.py::test_recycler_procurement_log_success PASSED [ 90%]
tests/test_exports_and_lineage.py::test_admin_datasets_directory_and_data_cards PASSED [100%]

======================== 10 passed, 1 warning in 0.93s ========================
```

Combined Payment & Export Test Suite (`tests/test_payments.py` + `tests/test_exports_and_lineage.py`):
```text
======================= 28 passed, 2 warnings in 1.98s ========================
```

### Web Frontend Test Suite (`apps/web`)
Executed via `npm test` (vitest):
```text
 ✓ src/App.test.tsx (1 test)
 ✓ src/components/recycler/SecondDeviceConfirmation.test.tsx (3 tests)
 ✓ src/components/recycler/RecyclerConsole.test.tsx (6 tests)
 ✓ src/components/admin/AdminDashboard.test.tsx (8 tests)

 Test Files  4 passed (4)
      Tests  18 passed (18)
```
