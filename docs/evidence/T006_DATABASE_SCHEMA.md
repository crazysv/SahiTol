# Test Evidence: T006 Implement PostgreSQL/PostGIS Schema and Migrations

## Metadata
- **Task ID**: T006
- **Phase**: Stage 1 (Data & Backend Setup)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Reviewer**: SahiTol Engineering & Database Architecture

## Context & Objectives
Implements the canonical database schema across all 41 tables defined in [06_SCHEMA.md](../06_SCHEMA.md) using SQLAlchemy 2.0 ORM models, GeoAlchemy2 PostGIS extensions, and Alembic versioned migrations (`0001_initial_schema.py`). Enforces signed 64-bit integer paise for all monetary values, signed 64-bit integer grams for weights, UUID primary keys, PostGIS `Geometry('POINT', 4326)` and `Geometry('POLYGON', 4326)` types, unique constraints, and database check constraints.

## Requirements & Acceptance Case Mapping
| Requirement | Test ID | Scope | Contributing Tasks | Implementation & Evidence Summary |
|---|---|---|---|---|
| R-ARC-02 | AT-006 | RELEASE | T001, T006 | PostgreSQL 16 + PostGIS 3.4 schema created with Alembic initial migration. 41 tables registered with PostGIS extension creation. |
| R-DATA-01 | AT-053 | RELEASE | T006, T013 | Integer paise (`rate_paise_per_unit`, `quoted_total_paise`, `agreed_total_paise`, `amount_paise`) and integer grams (`estimated_weight_g`, `measured_weight_g`) enforced using `BigInteger` columns and positive check constraints (`amount_paise > 0`, `measured_weight_g > 0`, `agreed_total_paise >= 0`). |
| R-DATA-02 | AT-054 | RELEASE | T006, T013 | Immutable `domain_events` table created with `(aggregate_id, sequence)` uniqueness constraint, positive sequence check constraint (`sequence >= 1`), `prev_hash`, and `event_hash`. Append-only design prevents update/deletion. |

## Observable Artifact Outputs
1. **Declarative Base & Engine Configuration**:
   - `services/api/app/db/base.py`: DeclarativeBase root for SQLAlchemy 2.0.
   - `services/api/app/db/session.py`: Database engine, connection pooling (`pool_pre_ping=True`), and `get_db()` session dependency.
   - `services/api/app/db/__init__.py`: Package initialization registering all models.

2. **Complete 41 Canonical ORM Models** (`services/api/app/db/models/`):
   - `auth.py`: `User` (with unique `phone_normalized` index and Argon2id hash), `AuthSession` (device tracking, rotating refresh token hash).
   - `collector.py`: `Collector` (display alias, preferred language `hi`/`en`/`mr`, coarse region FK, consent version, version).
   - `facility.py`: `Region` (state, centroid, boundary geometry), `Facility` (kind, address, PostGIS `geo_point`, geocode accuracy, active status), `FacilityUser` (compound key user+facility), `FacilityAuthorization` (route, authority, validity dates, verification level), `FacilityMaterial` (accepted route, weight bounds), `FacilityOperation` (pickup status, service area geometry), `FacilityRate` (rate in paise/unit, validity).
   - `material.py`: `MaterialCategory` (unique code), `Material` (subcategory, condition options, allowed units, default route), `MaterialAlias` (unique material+language+term), `SafetyGuide` (route, text, icon/audio keys, source IDs).
   - `price.py`: `PriceObservation` (paise/unit, unit, kind BUY/QUOTE/SELL, observed_at, source ID, composite index), `PriceSummary` (cohort key, policy version, Q1/median/Q3 paise, count, independent sources, confidence).
   - `lot.py`: `Lot` (collector FK, positive weight check, status, version), `MediaObject` (SHA-256, storage key, mime), `LotImage` (purpose, order), `LocationRecord` (PostGIS point, accuracy, coarse area), `Classification` (model ID, SHA-256, scores, threshold, abstained flag), `ValuationSnapshot` (low/median/high total paise).
   - `trade.py`: `LotRequest`, `Offer` (rate or fixed total paise, terms hash, expiry), `Transaction` (quoted/agreed paise, non-negative check, version), `TermsRevision` (measured grams > 0, final paise >= 0, mutual terms hash), `Handover` (frozen proposal payload, hash, public token), `HandoverConfirmation` (unique handover, confirmed at), `PaymentEntry` (amount paise > 0, method CASH/UPI, assertion/ack state).
   - `provenance.py`: `DataSource` (publisher, title, retrieved_at, SHA-256), `SourceAssertion` (field-level assertion with locator and reviewer), `DatasetVersion` (family, manifest key, checksum, origin counts), `ModelVersion` (model/labels SHA-256, licence, metrics), `TrainingImage` (object group, split, SHA-256), `ResearchInsight` (insight card evidence).
   - `audit.py`: `DomainEvent` (aggregate type, sequence >= 1, prev_hash, event_hash), `AuditLog` (redacted changes), `SyncOperation` (idempotent operation UUID), `SyncChange` (bigint sequence for delta cursors), `QualityFlag` (severity, evidence, status), `EconomicsScenario` (illustrative assumptions).

3. **Alembic Initial Migration** (`services/api/alembic/versions/0001_initial_schema.py`):
   - Enables `"uuid-ossp"` and `"postgis"` extensions.
   - Creates all 41 tables with explicit column types, foreign key cascades, unique indexes, and check constraints.
   - Provides clean reverse `downgrade()` dropping all tables in reverse dependency order.

4. **Automated Test Suite** (`services/api/tests/test_schema.py`):
   - `test_all_41_tables_registered`: Confirms exact 41 tables match between metadata and specification.
   - `test_integer_money_and_weight_columns`: Asserts BigInteger types for all money (paise) and weight (grams) columns.
   - `test_postgis_geometry_columns`: Verifies GeoAlchemy2 `Geometry('POINT', 4326)` and `Geometry('POLYGON', 4326)`.
   - `test_check_constraints_positive_weight_and_money`: Asserts SQL check constraints are configured.
   - `test_unique_constraints_and_indices`: Checks compound uniqueness on events, aliases, and users.
   - `test_alembic_offline_migration_generation`: Executes `alembic upgrade head --sql` to verify error-free compilation of PostgreSQL/PostGIS DDL.

## Test Verification Output
```text
pytest services/api/tests/
======================== 18 passed, 1 warning in 3.32s ========================
```
Alembic offline compilation:
```text
python -m alembic upgrade head --sql
...
CREATE TABLE domain_events ( ... CONSTRAINT uq_domain_event_agg_seq UNIQUE (aggregate_id, sequence), CONSTRAINT chk_event_sequence_positive CHECK (sequence >= 1) );
CREATE TABLE transactions ( ... CONSTRAINT chk_tx_non_negative_agreed_paise CHECK (agreed_total_paise IS NULL OR agreed_total_paise >= 0) );
CREATE TABLE payment_entries ( ... CONSTRAINT chk_payment_positive_amount CHECK (amount_paise > 0) );
COMMIT;
[OK] Exited with code 0.
```

## 2026-10-01 verification repair

The prior in-memory SQLite test double returned the EWKT text accepted on a
PostGIS write. GeoAlchemy correctly expects EWKB when reading a `Geometry`
column, so any endpoint that selected a saved location failed before its
application behaviour could be tested. `services/api/tests/test_db.py` now
normalises both test-double write and read paths to hex EWKB using Shapely.
This is test-only compatibility code; the production schema remains
PostgreSQL/PostGIS.

Verified from the repository root with the pinned Python 3.10 dependencies:

```text
PYTHONPATH="services/api:." uv run --python 3.10 --with-requirements services/api/requirements.txt --with pytest==8.3.3 --with pytest-asyncio==0.24.0 --with numpy==1.26.4 --with pandas==2.2.3 --with shapely pytest services/api/tests/test_schema.py services/api/tests/test_facilities.py services/api/tests/test_lots.py services/api/tests/test_matching.py -q
45 passed in 8.05s
```
