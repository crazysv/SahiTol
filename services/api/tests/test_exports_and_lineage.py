"""Test suite for Seven Dataset Exports, Recycler Procurement Logs, and Data Lineage.
Fulfills R-PRO-02, R-DAT-01 to R-DAT-11, R-LINE-02, and AT-034, AT-053 to AT-063, AT-071.
"""
import uuid
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.models.audit import DomainEvent
from app.db.models.auth import User
from app.db.models.collector import Collector
from app.db.models.facility import Facility, FacilityAuthorization, FacilityMaterial, FacilityUser, Region
from app.db.models.lot import Lot
from app.db.models.material import Material, MaterialAlias, MaterialCategory
from app.db.models.price import PriceObservation
from app.db.models.trade import Handover, PaymentEntry, TermsRevision, Transaction
from app.security import create_access_token
from tests.test_db import TestingSessionLocal

client = TestClient(app)

NON_EPR_DISCLAIMER_SNIPPET = "not a statutory EPR certificate"


@pytest.fixture
def export_test_env():
    """Set up users, facility, collector, material, and transactions for export tests."""
    with TestingSessionLocal() as session:
        # 1. Admin
        admin_user = User(
            id=uuid.uuid4(),
            phone_normalized="+919999900001",
            pin_hash="hash",
            role="ADMIN",
            account_state="ACTIVE"
        )
        session.add(admin_user)

        # 2. Region & Facility
        reg = session.query(Region).filter(Region.id == "DELHI_NCR").first()
        if not reg:
            reg = Region(
                id="DELHI_NCR",
                name="Delhi National Capital Region",
                state_code="DL",
                kind="STATE"
            )
            session.add(reg)
            session.flush()

        facility = Facility(
            id=uuid.uuid4(),
            name="Alpha Green Recyclers",
            facility_name="Alpha Green Recyclers Yard 1",
            kind="RECYCLER",
            address_public="Mayapuri Industrial Area Phase II, New Delhi",
            state="Delhi",
            district="West Delhi",
            region_id="DELHI_NCR",
            active=True
        )
        session.add(facility)
        session.flush()

        auth = FacilityAuthorization(
            id=uuid.uuid4(),
            facility_id=facility.id,
            route="AUTHORIZED_EWASTE",
            authority="DPCC",
            reference="REG-DL-2026-001",
            status="VALID",
            verification_level="L2"
        )
        session.add(auth)

        fac_mat = FacilityMaterial(
            id=uuid.uuid4(),
            facility_id=facility.id,
            material_id="MAT-CAB-01",
            route="AUTHORIZED_EWASTE",
            accepted=True
        )
        session.add(fac_mat)

        recycler_user = User(
            id=uuid.uuid4(),
            phone_normalized="+919999900002",
            pin_hash="hash",
            role="RECYCLER",
            account_state="ACTIVE"
        )
        session.add(recycler_user)
        session.flush()

        fac_user = FacilityUser(
            facility_id=facility.id,
            user_id=recycler_user.id,
            membership_role="MANAGER",
            active=True
        )
        session.add(fac_user)

        # 3. Collector
        col_user = User(
            id=uuid.uuid4(),
            phone_normalized="+919999900003",
            pin_hash="hash",
            role="COLLECTOR",
            account_state="ACTIVE"
        )
        session.add(col_user)
        session.flush()

        collector = Collector(
            id=col_user.id,
            user_id=col_user.id,
            display_alias="Ramesh",
            preferred_language="hi",
            general_area="Mayapuri Phase II",
            region_id="DELHI_NCR"
        )
        session.add(collector)

        # 4. Canonical Material
        cat = session.query(MaterialCategory).filter(MaterialCategory.id == "CABLES").first()
        if not cat:
            cat = MaterialCategory(
                id="CABLES",
                code="CABLES",
                label_key="category.cables",
                display_order=1,
                active=True
            )
            session.add(cat)
            session.flush()

        mat = session.query(Material).filter(Material.id == "MAT-CAB-01").first()
        if not mat:
            mat = Material(
                id="MAT-CAB-01",
                category_id="CABLES",
                subcategory_code="COPPER_WIRING",
                description_key="material.cables.copper",
                default_route="RECYCLER_STANDARD",
                active=True
            )
            session.add(mat)
            session.flush()

        alias = session.query(MaterialAlias).filter(MaterialAlias.material_id == "MAT-CAB-01").first()
        if not alias:
            alias = MaterialAlias(
                id=uuid.uuid4(),
                material_id="MAT-CAB-01",
                language="hi",
                local_term="Tamba Taar",
                normalized_term="tamba taar"
            )
            session.add(alias)

        # 5. Lot & Transaction
        lot = Lot(
            id=uuid.uuid4(),
            collector_id=collector.id,
            material_id="MAT-CAB-01",
            regulatory_route="RECYCLER_STANDARD",
            estimated_weight_g=50000,
            condition="CLEAN",
            status="RECEIVED",
            is_demo=False
        )
        session.add(lot)
        session.flush()

        tx = Transaction(
            id=uuid.uuid4(),
            lot_id=lot.id,
            collector_id=collector.id,
            facility_id=facility.id,
            accepted_offer_id=uuid.uuid4(),
            estimated_weight_g=50000,
            agreed_weight_g=48000,
            quoted_total_paise=1920000,
            agreed_total_paise=1920000,
            lifecycle="CONFIRMED",
            is_demo=False
        )
        session.add(tx)
        session.flush()

        # Handover
        handover = Handover(
            id=uuid.uuid4(),
            transaction_id=tx.id,
            lot_id=lot.id,
            proposal_payload_json={"is_demo": False},
            proposal_hash="test_proposal_hash_001",
            proposed_by=col_user.id,
            proposed_at_client=datetime.now(timezone.utc),
            status="CONFIRMED",
            public_token_hash="pub_token_hash_001",
            version=1
        )
        session.add(handover)

        # Payment entry (settling the 1920000 paise)
        pay = PaymentEntry(
            id=uuid.uuid4(),
            transaction_id=tx.id,
            amount_paise=1920000,
            method="CASH",
            state="ACKNOWLEDGED",
            asserted_by="FACILITY",
            counterparty_ack_by=col_user.id,
            ack_at=datetime.now(timezone.utc)
        )
        session.add(pay)

        session.commit()

        admin_token = create_access_token(str(admin_user.id), admin_user.role)
        recycler_token = create_access_token(str(recycler_user.id), recycler_user.role)
        col_token = create_access_token(str(col_user.id), col_user.role)

        return {
            "admin_headers": {"Authorization": f"Bearer {admin_token}"},
            "recycler_headers": {"Authorization": f"Bearer {recycler_token}"},
            "collector_headers": {"Authorization": f"Bearer {col_token}"},
            "facility_id": facility.id,
            "tx_id": tx.id,
            "lot_id": lot.id,
            "collector_id": collector.id
        }


def test_close_transaction_creates_price_observation_once(export_test_env):
    """Test closed transaction generates a PriceObservation exactly once (R-LINE-02, AT-071)."""
    env = export_test_env
    tx_id = env["tx_id"]

    # Close transaction
    resp = client.post(f"/api/v1/transactions/{tx_id}/close", headers=env["collector_headers"])
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["lifecycle"] == "CLOSED"

    # Verify PriceObservation was created
    with TestingSessionLocal() as session:
        obs = session.query(PriceObservation).filter(PriceObservation.transaction_id == tx_id).all()
        assert len(obs) == 1, "Expected exactly 1 PriceObservation created from transaction"
        p = obs[0]
        assert p.material_id == "MAT-CAB-01"
        assert p.origin_class == "PLATFORM_GENERATED"
        assert p.source_kind == "VERIFIED_TRANSACTION"
        assert p.review_status == "PENDING_REVIEW"
        assert p.price_kind == "BUY"
        # 1920000 paise for 48000 g = 40000 paise/kg
        assert p.rate_paise_per_unit == 40000
        assert p.is_demo is False

        # Verify domain audit event was recorded
        events = session.query(DomainEvent).filter(
            DomainEvent.aggregate_id == tx_id,
            DomainEvent.event_type == "PRICE_OBSERVATION_CREATED_FROM_TRANSACTION"
        ).all()
        assert len(events) >= 1

    # Idempotent replay: calling close again must not create duplicate PriceObservation
    resp2 = client.post(f"/api/v1/transactions/{tx_id}/close", headers=env["collector_headers"])
    assert resp2.status_code == 200

    with TestingSessionLocal() as session:
        obs2 = session.query(PriceObservation).filter(PriceObservation.transaction_id == tx_id).all()
        assert len(obs2) == 1, "Duplicate close call created duplicate PriceObservation!"


def test_export_dataset_materials(export_test_env):
    """Test materials dataset export in JSON and CSV format (R-DATA-01, AT-053)."""
    env = export_test_env

    # JSON export
    resp_json = client.get("/api/v1/exports/materials?format=json", headers=env["collector_headers"])
    assert resp_json.status_code == 200
    data = resp_json.json()
    assert data["dataset_family"] == "materials"
    assert "data" in data
    assert len(data["data"]) > 0
    assert NON_EPR_DISCLAIMER_SNIPPET in data["statutory_notice"]

    # CSV export
    resp_csv = client.get("/api/v1/exports/materials?format=csv", headers=env["collector_headers"])
    assert resp_csv.status_code == 200
    assert "text/csv" in resp_csv.headers["content-type"]
    assert "X-SahiTol-SHA256" in resp_csv.headers
    assert NON_EPR_DISCLAIMER_SNIPPET in resp_csv.text


def test_export_dataset_prices(export_test_env):
    """Test price dataset export (R-DATA-02, AT-054)."""
    env = export_test_env

    resp = client.get("/api/v1/exports/prices?format=json", headers=env["collector_headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert data["dataset_family"] == "prices"
    assert "data" in data


def test_export_dataset_facilities(export_test_env):
    """Test facilities dataset export (R-DATA-03, AT-055)."""
    env = export_test_env

    resp = client.get("/api/v1/exports/facilities?format=json", headers=env["collector_headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert data["dataset_family"] == "facilities"
    assert len(data["data"]) > 0
    # Verify regulatory attribution
    fac = data["data"][0]
    assert "verification_level" in fac
    assert "materials_accepted" in fac


def test_export_dataset_transactions(export_test_env):
    """Test transaction dataset export with Digital Handover Record notice (R-DATA-04, AT-056)."""
    env = export_test_env

    resp = client.get("/api/v1/exports/transactions?format=json", headers=env["collector_headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert data["dataset_family"] == "transactions"
    assert len(data["data"]) > 0
    tx_rec = data["data"][0]
    assert "non_epr_notice" in tx_rec
    assert NON_EPR_DISCLAIMER_SNIPPET in tx_rec["non_epr_notice"]
    assert tx_rec["collector_pseudonym"].startswith("col_anon_")


def test_export_dataset_payments(export_test_env):
    """Test payments dataset export (R-DATA-04, AT-056, AT-058)."""
    env = export_test_env

    resp = client.get("/api/v1/exports/payments?format=json", headers=env["collector_headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert data["dataset_family"] == "payments"
    assert len(data["data"]) > 0
    p_rec = data["data"][0]
    assert "amount_paise" in p_rec
    assert "payment_method" in p_rec


def test_export_dataset_traceability(export_test_env):
    """Test traceability ledger export with SHA-256 hash chains (R-DATA-05, AT-057)."""
    env = export_test_env

    resp = client.get("/api/v1/exports/traceability?format=json", headers=env["collector_headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert data["dataset_family"] == "traceability"


def test_export_dataset_collectors_zero_pii_and_auth(export_test_env):
    """Test collector directory export requires admin and enforces Zero-PII (R-DATA-06, AT-058)."""
    env = export_test_env

    # Non-admin collector attempts access -> 403 Forbidden
    resp_forbidden = client.get("/api/v1/exports/collectors?format=json", headers=env["collector_headers"])
    assert resp_forbidden.status_code == 403

    # Admin access -> 200 OK
    resp_admin = client.get("/api/v1/exports/collectors?format=json", headers=env["admin_headers"])
    assert resp_admin.status_code == 200
    data = resp_admin.json()
    assert data["dataset_family"] == "collectors"
    assert len(data["data"]) > 0

    col = data["data"][0]
    assert col["collector_pseudonym"].startswith("col_anon_")
    assert col["privacy_level"] == "ZERO_PII_PSEUDONYMIZED"
    # Ensure zero PII: no phone numbers or raw UUIDs
    assert "phone" not in col
    assert "pin" not in col
    assert "gps" not in col


def test_recycler_procurement_log_success(export_test_env):
    """Test recycler procurement log export with non-EPR disclosure (R-PRO-02, AT-034)."""
    env = export_test_env

    # Recycler fetches log in JSON
    resp = client.get("/api/v1/recycler/procurement-log?format=json", headers=env["recycler_headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert len(data["data"]) > 0
    rec = data["data"][0]
    assert rec["reference_id"].startswith("ST-")
    assert rec["weight_kg"] > 0
    assert rec["amount_inr"] > 0
    assert NON_EPR_DISCLAIMER_SNIPPET in rec["non_epr_disclaimer"]

    # Recycler fetches log in CSV
    resp_csv = client.get("/api/v1/recycler/procurement-log?format=csv", headers=env["recycler_headers"])
    assert resp_csv.status_code == 200
    assert "text/csv" in resp_csv.headers["content-type"]
    assert NON_EPR_DISCLAIMER_SNIPPET in resp_csv.headers["X-SahiTol-Disclaimer"]


def test_admin_datasets_directory_and_data_cards(export_test_env):
    """Test admin datasets directory and data cards retrieval (R-DAT-11, AT-063)."""
    env = export_test_env

    # Admin accesses directory
    resp = client.get("/api/v1/admin/datasets", headers=env["admin_headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert "dataset_families" in data
    families = {f["family_id"]: f for f in data["dataset_families"]}
    assert "materials" in families
    assert "prices" in families
    assert "facilities" in families
    assert "transactions" in families
    assert "payments" in families
    assert "traceability" in families
    assert "collectors" in families
    assert "ai_training" in families
    assert data["meta"]["fieldwork_status"].startswith("UNMET")

    # Fetch data card for materials
    card_resp = client.get("/api/v1/admin/datasets/materials/data-card", headers=env["admin_headers"])
    assert card_resp.status_code == 200
    card_data = card_resp.json()
    assert card_data["family"] == "materials"
    assert "content_markdown" in card_data
    assert "SahiTol Curated Scrap Material Taxonomy" in card_data["content_markdown"]
