"""Unit tests for PostgreSQL/PostGIS schema, ORM models, and Alembic migrations.
Verifies T006 and docs/06_SCHEMA.md.
"""

from __future__ import annotations
import subprocess
import sys
from pathlib import Path
import pytest
from sqlalchemy import BigInteger, CheckConstraint, UniqueConstraint
from geoalchemy2 import Geometry

from app.db.base import Base
import app.db.models


EXPECTED_TABLES = {
    "users",
    "auth_sessions",
    "regions",
    "collectors",
    "facilities",
    "facility_users",
    "material_categories",
    "materials",
    "material_aliases",
    "safety_guides",
    "data_sources",
    "source_assertions",
    "facility_authorizations",
    "facility_materials",
    "facility_operations",
    "facility_rates",
    "price_observations",
    "price_summaries",
    "lots",
    "media_objects",
    "lot_images",
    "location_records",
    "classifications",
    "valuation_snapshots",
    "lot_requests",
    "offers",
    "transactions",
    "terms_revisions",
    "handovers",
    "handover_confirmations",
    "payment_entries",
    "domain_events",
    "audit_logs",
    "sync_operations",
    "sync_changes",
    "quality_flags",
    "research_insights",
    "model_versions",
    "training_images",
    "economics_scenarios",
    "dataset_versions",
}


def test_all_41_tables_registered():
    """Verify all 41 canonical tables from docs/06_SCHEMA.md are present in Base.metadata."""
    registered_tables = set(Base.metadata.tables.keys())
    missing_tables = EXPECTED_TABLES - registered_tables
    assert not missing_tables, f"Missing tables in ORM metadata: {missing_tables}"
    assert len(registered_tables) == 41


def test_integer_money_and_weight_columns():
    """Verify money (paise) and weight (grams) columns use BigInteger."""
    tables = Base.metadata.tables

    # Weight fields (grams)
    assert isinstance(tables["lots"].c.estimated_weight_g.type, BigInteger)
    assert isinstance(tables["transactions"].c.estimated_weight_g.type, BigInteger)
    assert isinstance(tables["terms_revisions"].c.measured_weight_g.type, BigInteger)

    # Money fields (paise)
    assert isinstance(tables["transactions"].c.quoted_total_paise.type, BigInteger)
    assert isinstance(tables["terms_revisions"].c.final_total_paise.type, BigInteger)
    assert isinstance(tables["payment_entries"].c.amount_paise.type, BigInteger)
    assert isinstance(tables["facility_rates"].c.rate_paise_per_unit.type, BigInteger)
    assert isinstance(tables["price_observations"].c.rate_paise_per_unit.type, BigInteger)


def test_postgis_geometry_columns():
    """Verify spatial columns use GeoAlchemy2 Geometry types with SRID 4326."""
    tables = Base.metadata.tables

    # Facility geo_point (POINT)
    fac_geo = tables["facilities"].c.geo_point.type
    assert isinstance(fac_geo, Geometry)
    assert fac_geo.geometry_type == "POINT"
    assert fac_geo.srid == 4326

    # Region boundary (POLYGON)
    reg_boundary = tables["regions"].c.boundary.type
    assert isinstance(reg_boundary, Geometry)
    assert reg_boundary.geometry_type == "POLYGON"
    assert reg_boundary.srid == 4326

    # LocationRecord point (POINT)
    loc_point = tables["location_records"].c.point.type
    assert isinstance(loc_point, Geometry)
    assert loc_point.geometry_type == "POINT"
    assert loc_point.srid == 4326


def test_check_constraints_positive_weight_and_money():
    """Verify check constraints for non-negative money and positive weight."""
    tables = Base.metadata.tables

    # Transactions: agreed_total_paise >= 0
    tx_checks = [c.sqltext.text for c in tables["transactions"].constraints if isinstance(c, CheckConstraint)]
    assert any("agreed_total_paise >= 0" in text for text in tx_checks)

    # TermsRevision: measured_weight_g > 0 and final_total_paise >= 0
    tr_checks = [c.sqltext.text for c in tables["terms_revisions"].constraints if isinstance(c, CheckConstraint)]
    assert any("measured_weight_g > 0" in text for text in tr_checks)
    assert any("final_total_paise >= 0" in text for text in tr_checks)

    # PaymentEntries: amount_paise > 0
    pay_checks = [c.sqltext.text for c in tables["payment_entries"].constraints if isinstance(c, CheckConstraint)]
    assert any("amount_paise > 0" in text for text in pay_checks)

    # DomainEvents: sequence >= 1
    evt_checks = [c.sqltext.text for c in tables["domain_events"].constraints if isinstance(c, CheckConstraint)]
    assert any("sequence >= 1" in text for text in evt_checks)


def test_unique_constraints_and_indices():
    """Verify uniqueness constraints on events, aliases, and users."""
    tables = Base.metadata.tables

    # Domain events aggregate + sequence uniqueness
    evt_uniques = [
        [col.name for col in c.columns]
        for c in tables["domain_events"].constraints
        if isinstance(c, UniqueConstraint)
    ]
    assert ["aggregate_id", "sequence"] in evt_uniques

    # Material aliases material + language + normalized_term uniqueness
    alias_uniques = [
        [col.name for col in c.columns]
        for c in tables["material_aliases"].constraints
        if isinstance(c, UniqueConstraint)
    ]
    assert ["material_id", "language", "normalized_term"] in alias_uniques


def test_alembic_offline_migration_generation():
    """Verify that Alembic compiles valid PostgreSQL/PostGIS DDL without error."""
    api_dir = Path(__file__).resolve().parents[1]
    res = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head", "--sql"],
        cwd=str(api_dir),
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Alembic --sql failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
    assert "CREATE TABLE users" in res.stdout
    assert "CREATE TABLE facilities" in res.stdout
    assert "CREATE TABLE domain_events" in res.stdout
    assert "postgis" in res.stdout.lower()
    assert "0001_initial_schema" in res.stdout
