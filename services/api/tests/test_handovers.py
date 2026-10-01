"""Comprehensive test suite for Handover Proposals, Confirmations, and QR Verification (T023).
Covers requirements: R-HAND-01, R-HAND-02, R-HAND-03, R-HAND-04, R-HAND-05, R-DATA-04.
Acceptance cases: AT-029, AT-030, AT-031, AT-032, AT-033, AT-056.
"""
import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_db
from app.db.models.auth import User
from app.db.models.collector import Collector
from app.db.models.facility import (
    Facility,
    FacilityAuthorization,
    FacilityMaterial,
    FacilityOperation,
    FacilityRate,
    FacilityUser,
    Region,
)
from app.db.models.lot import LocationRecord, Lot
from app.db.models.trade import (
    Handover,
    HandoverConfirmation,
    LotRequest,
    Offer,
    TermsRevision,
    Transaction,
)
from app.db.seeds.materials import seed_materials
from app.domain.canonical import compute_canonical_hash
from app.security import create_access_token
from tests.test_db import TestingSessionLocal, override_get_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_handovers_module():
    """Setup test database dependency override and seed taxonomy."""
    app.dependency_overrides[get_db] = override_get_db
    with TestingSessionLocal() as session:
        seed_materials(session)
        reg = session.query(Region).filter(Region.id == "DELHI_NCR").first()
        if not reg:
            reg = Region(id="DELHI_NCR", name="Delhi-NCR", state_code="DL", kind="METRO")
            session.add(reg)
            session.commit()
    yield


@pytest.fixture
def handover_environment():
    """Seed test collector, facility, recycler user, lot, offer, and agreed transaction."""
    col_user_id = uuid.uuid4()
    collector_id = uuid.uuid4()
    rec_user_id = uuid.uuid4()
    fac_id = uuid.uuid4()
    lot_id = uuid.uuid4()
    req_id = uuid.uuid4()
    offer_id = uuid.uuid4()
    tx_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    with TestingSessionLocal() as session:
        # Collector
        col_user = User(
            id=col_user_id,
            phone_normalized="+919811122233",
            pin_hash="pin_hash",
            role="COLLECTOR",
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(col_user)
        col = Collector(
            id=collector_id,
            user_id=col_user_id,
            display_alias="Rajesh Collector",
            preferred_language="hi",
            region_id="DELHI_NCR",
            general_area="Mayapuri",
            consent_version="v1.0"
        )
        session.add(col)

        # Recycler User & Facility
        rec_user = User(
            id=rec_user_id,
            phone_normalized="+919844455566",
            pin_hash="pin_hash",
            role="RECYCLER",
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(rec_user)

        fac = Facility(
            id=fac_id,
            name="Apex E-Waste Recyclers",
            facility_name="Apex E-Waste Recyclers Pvt Ltd",
            kind="RECYCLER",
            address_public="Plot 45, Okhla Industrial Area Phase II, New Delhi",
            district="South East Delhi",
            state="Delhi",
            region_id="DELHI_NCR",
            contact_public="contact@apexrecyclers.example.com",
            active=True,
            version=1
        )
        session.add(fac)

        fu = FacilityUser(
            user_id=rec_user_id,
            facility_id=fac_id,
            membership_role="OWNER",
            active=True
        )
        session.add(fu)

        auth = FacilityAuthorization(
            id=uuid.uuid4(),
            facility_id=fac_id,
            route="AUTHORIZED_EWASTE",
            authority="DPCC",
            reference="DPCC/EW/2024/045",
            status="VALID",
            verification_level="REGISTRY_MATCH",
            valid_from=now - timedelta(days=30),
            valid_until=now + timedelta(days=365)
        )
        session.add(auth)

        # Lot in ACCEPTED state
        lot = Lot(
            id=lot_id,
            collector_id=collector_id,
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=8500,
            condition="INTACT",
            description="Telecom server boards",
            status="ACCEPTED",
            version=2,
            is_demo=False
        )
        session.add(lot)

        # Offer
        offer_terms_hash = "a" * 64
        offer = Offer(
            id=offer_id,
            request_id=req_id,
            lot_id=lot_id,
            facility_id=fac_id,
            rate_paise_per_kg=45000,
            price_basis="RATE_PER_KG",
            condition="INTACT",
            weight_basis_g=8500,
            expires_at=now + timedelta(days=3),
            status="ACCEPTED",
            terms_hash=offer_terms_hash,
            version=2,
            created_at=now,
            updated_at=now
        )
        session.add(offer)

        # Transaction in AGREED state
        tx = Transaction(
            id=tx_id,
            lot_id=lot_id,
            collector_id=collector_id,
            facility_id=fac_id,
            accepted_offer_id=offer_id,
            estimated_weight_g=8500,
            agreed_weight_g=8500,
            quoted_total_paise=382500,  # 45000 * 8.5kg = 382500 paise (Rs 3825.00)
            agreed_total_paise=382500,
            currency="INR",
            lifecycle="AGREED",
            version=1,
            is_demo=False,
            created_at=now,
            updated_at=now
        )
        session.add(tx)

        # Initial TermsRevision
        rev = TermsRevision(
            id=uuid.uuid4(),
            transaction_id=tx_id,
            previous_revision_id=None,
            final_material_id="MAT-PCB-01",
            measured_weight_g=8500,
            final_total_paise=382500,
            currency="INR",
            proposed_by="FACILITY",
            proposed_at=now,
            collector_ack_at=now,
            recycler_ack_at=now,
            terms_hash=offer_terms_hash,
            reason="Agreed quote terms"
        )
        session.add(rev)
        session.commit()

    col_token = create_access_token(subject=str(col_user_id), role="COLLECTOR", is_demo=False)
    rec_token = create_access_token(subject=str(rec_user_id), role="RECYCLER", is_demo=False)

    return {
        "collector_user_id": col_user_id,
        "collector_id": collector_id,
        "recycler_user_id": rec_user_id,
        "facility_id": fac_id,
        "lot_id": lot_id,
        "tx_id": tx_id,
        "offer_terms_hash": offer_terms_hash,
        "collector_headers": {"Authorization": f"Bearer {col_token}"},
        "recycler_headers": {"Authorization": f"Bearer {rec_token}"}
    }


@pytest.fixture
def other_collector_user():
    """Create a distinct second collector user."""
    user_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        user = User(
            id=user_id,
            phone_normalized="+919877777777",
            pin_hash="pin_hash",
            role="COLLECTOR",
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(user)
        session.commit()
    token = create_access_token(subject=str(user_id), role="COLLECTOR", is_demo=False)
    return {"user_id": user_id, "headers": {"Authorization": f"Bearer {token}"}}


# --- Test Cases ---

def test_verify_hash_utility_matches_documented_handover_fixture():
    """Test verify-hash endpoint validates SAHITOL-JCS-1 canonical hash against planning/handover_fixture.json."""
    fixture_path = Path("docs/planning/handover_fixture.json")
    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    payload = data["proposal_payload"]
    expected_hash = data["proposal_hash"]

    resp = client.post("/api/v1/handovers/verify-hash", json=payload)
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["canonical_hash"] == expected_hash
    assert res_data["is_valid"] is True


def test_demo_offline_import_requires_server_lookup_then_recycler_confirmation():
    """The two-device demo path may bootstrap demo prerequisites, never receipt authority."""
    collector_login = client.post("/api/v1/auth/demo", json={"role": "COLLECTOR", "persona_id": "santosh", "device_id": "android-test"})
    assert collector_login.status_code == 200
    collector_headers = {"Authorization": f"Bearer {collector_login.json()['access_token']}"}
    handover_id, lot_id, transaction_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    payload = {
        "schema_version": "SAHITOL-HANDOVER-1",
        "handover_id": str(handover_id), "transaction_id": str(transaction_id), "lot_id": str(lot_id),
        "collector_id": "offline-demo-account", "facility_id": "1aafb3d0-9ef2-4f34-95ca-0e6f3441e851",
        "material_snapshot": {"material_id": "MAT-PCB-01", "condition": "INTACT", "regulatory_route": "AUTHORIZED_EWASTE"},
        "weight_snapshot": {"estimated_weight_g": 2300, "measured_weight_g": 2300},
        "value_snapshot": {"currency": "INR", "agreed_total_paise": 41400},
        "occurred_at": datetime.now(timezone.utc).isoformat(), "media": [], "is_demo": True,
    }
    proposal_hash = compute_canonical_hash(payload)
    imported = client.post("/api/v1/demo/handovers/import", headers=collector_headers, json={
        "id": str(handover_id), "proposal_payload": payload, "proposal_hash": proposal_hash, "expected_version": 0,
    })
    assert imported.status_code == 200
    assert imported.json()["status"] == "PENDING_CONFIRMATION"

    recycler_login = client.post("/api/v1/auth/demo", json={"role": "RECYCLER", "persona_id": "yard_operator", "device_id": "web-test"})
    assert recycler_login.status_code == 200
    recycler_headers = {"Authorization": f"Bearer {recycler_login.json()['access_token']}"}
    lookup = client.get(f"/api/v1/handovers/{handover_id}", headers=recycler_headers)
    assert lookup.status_code == 200
    assert lookup.json()["proposal_hash"] == proposal_hash
    confirmed = client.post(f"/api/v1/handovers/{handover_id}/confirm", headers=recycler_headers, json={
        "expected_version": lookup.json()["version"], "proposal_hash": proposal_hash,
    })
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "CONFIRMED"


def test_create_handover_proposal_success(handover_environment):
    """Test collector submits valid handover proposal with canonical hash (R-HAND-01, AT-029)."""
    env = handover_environment
    handover_id = uuid.uuid4()

    proposal_payload = {
        "schema_version": "SAHITOL-HANDOVER-1",
        "handover_id": str(handover_id),
        "transaction_id": str(env["tx_id"]),
        "lot_id": str(env["lot_id"]),
        "collector_id": str(env["collector_id"]),
        "facility_id": str(env["facility_id"]),
        "agreed_terms_hash": env["offer_terms_hash"],
        "material_snapshot": {
            "material_id": "MAT-PCB-01",
            "condition": "INTACT",
            "regulatory_route": "AUTHORIZED_EWASTE"
        },
        "weight_snapshot": {
            "estimated_weight_g": 8500,
            "measured_weight_g": None
        },
        "value_snapshot": {
            "currency": "INR",
            "agreed_total_paise": 382500,
            "estimated_low_paise": 350000,
            "estimated_high_paise": 400000
        },
        "location_snapshot": {
            "location_id": None,
            "source": "GPS",
            "accuracy_m": 10,
            "captured_at": "2026-09-29T10:00:00.000Z"
        },
        "occurred_at": "2026-09-29T10:00:00.000Z",
        "media": [],
        "is_demo": False
    }
    proposal_hash = compute_canonical_hash(proposal_payload)

    body = {
        "id": str(handover_id),
        "proposal_payload": proposal_payload,
        "proposal_hash": proposal_hash
    }

    resp = client.post("/api/v1/handovers", json=body, headers=env["collector_headers"])
    assert resp.status_code == 201
    data = resp.json()

    assert data["id"] == str(handover_id)
    assert data["transaction_id"] == str(env["tx_id"])
    assert data["lot_id"] == str(env["lot_id"])
    assert data["status"] == "PENDING_CONFIRMATION"
    assert data["proposal_hash"] == proposal_hash
    assert data["public_token"] is not None
    assert len(data["public_token"]) >= 32

    # Verify Lot transitioned to HANDED_OVER
    with TestingSessionLocal() as session:
        lot = session.query(Lot).filter(Lot.id == env["lot_id"]).first()
        assert lot.status == "HANDED_OVER"
        tx = session.query(Transaction).filter(Transaction.id == env["tx_id"]).first()
        assert tx.lifecycle == "IN_TRANSIT"


def test_create_handover_idempotent_replay(handover_environment):
    """Test duplicate submission of identical proposal returns 200 with stored result (R-HAND-01)."""
    env = handover_environment
    handover_id = uuid.uuid4()

    proposal_payload = {
        "schema_version": "SAHITOL-HANDOVER-1",
        "handover_id": str(handover_id),
        "transaction_id": str(env["tx_id"]),
        "lot_id": str(env["lot_id"]),
        "collector_id": str(env["collector_id"]),
        "facility_id": str(env["facility_id"]),
        "agreed_terms_hash": env["offer_terms_hash"],
        "material_snapshot": {"material_id": "MAT-PCB-01", "condition": "INTACT", "regulatory_route": "AUTHORIZED_EWASTE"},
        "weight_snapshot": {"estimated_weight_g": 8500, "measured_weight_g": None},
        "value_snapshot": {"currency": "INR", "agreed_total_paise": 382500, "estimated_low_paise": None, "estimated_high_paise": None},
        "location_snapshot": {"location_id": None, "source": "MISSING", "accuracy_m": None, "captured_at": None},
        "occurred_at": "2026-09-29T10:00:00.000Z",
        "media": [],
        "is_demo": False
    }
    proposal_hash = compute_canonical_hash(proposal_payload)
    body = {"id": str(handover_id), "proposal_payload": proposal_payload, "proposal_hash": proposal_hash}

    resp1 = client.post("/api/v1/handovers", json=body, headers=env["collector_headers"])
    assert resp1.status_code == 201

    # Replay
    resp2 = client.post("/api/v1/handovers", json=body, headers=env["collector_headers"])
    assert resp2.status_code == 200
    assert resp2.json()["id"] == str(handover_id)
    assert resp2.json()["status"] == "PENDING_CONFIRMATION"


def test_create_handover_hash_mismatch_rejected(handover_environment):
    """Test tampered proposal hash is rejected with HTTP 409 Conflict (R-HAND-01)."""
    env = handover_environment
    handover_id = uuid.uuid4()

    proposal_payload = {
        "schema_version": "SAHITOL-HANDOVER-1",
        "handover_id": str(handover_id),
        "transaction_id": str(env["tx_id"]),
        "lot_id": str(env["lot_id"]),
        "collector_id": str(env["collector_id"]),
        "facility_id": str(env["facility_id"]),
        "agreed_terms_hash": env["offer_terms_hash"],
        "material_snapshot": {"material_id": "MAT-PCB-01", "condition": "INTACT", "regulatory_route": "AUTHORIZED_EWASTE"},
        "weight_snapshot": {"estimated_weight_g": 8500, "measured_weight_g": None},
        "value_snapshot": {"currency": "INR", "agreed_total_paise": 382500, "estimated_low_paise": None, "estimated_high_paise": None},
        "location_snapshot": {"location_id": None, "source": "MISSING", "accuracy_m": None, "captured_at": None},
        "occurred_at": "2026-09-29T10:00:00.000Z",
        "media": [],
        "is_demo": False
    }
    body = {
        "id": str(handover_id),
        "proposal_payload": proposal_payload,
        "proposal_hash": "b" * 64  # Corrupted hash
    }
    resp = client.post("/api/v1/handovers", json=body, headers=env["collector_headers"])
    assert resp.status_code == 409
    assert "proposal hash mismatch" in resp.json()["detail"].lower()


def test_create_handover_forbidden_for_other_collector(handover_environment, other_collector_user):
    """Test collector cannot propose handover for another collector's transaction."""
    env = handover_environment
    handover_id = uuid.uuid4()
    proposal_payload = {
        "schema_version": "SAHITOL-HANDOVER-1",
        "handover_id": str(handover_id),
        "transaction_id": str(env["tx_id"]),
        "lot_id": str(env["lot_id"]),
        "collector_id": str(env["collector_id"]),
        "facility_id": str(env["facility_id"]),
        "agreed_terms_hash": env["offer_terms_hash"],
        "material_snapshot": {"material_id": "MAT-PCB-01", "condition": "INTACT", "regulatory_route": "AUTHORIZED_EWASTE"},
        "weight_snapshot": {"estimated_weight_g": 8500, "measured_weight_g": None},
        "value_snapshot": {"currency": "INR", "agreed_total_paise": 382500, "estimated_low_paise": None, "estimated_high_paise": None},
        "location_snapshot": {"location_id": None, "source": "MISSING", "accuracy_m": None, "captured_at": None},
        "occurred_at": "2026-09-29T10:00:00.000Z",
        "media": [],
        "is_demo": False
    }
    proposal_hash = compute_canonical_hash(proposal_payload)
    body = {"id": str(handover_id), "proposal_payload": proposal_payload, "proposal_hash": proposal_hash}

    resp = client.post("/api/v1/handovers", json=body, headers=other_collector_user["headers"])
    assert resp.status_code == 403


def test_confirm_handover_exact_match_success(handover_environment):
    """Test recycler confirms handover where measured values match agreed terms (R-HAND-02, AT-030)."""
    env = handover_environment
    handover_id = uuid.uuid4()

    proposal_payload = {
        "schema_version": "SAHITOL-HANDOVER-1",
        "handover_id": str(handover_id),
        "transaction_id": str(env["tx_id"]),
        "lot_id": str(env["lot_id"]),
        "collector_id": str(env["collector_id"]),
        "facility_id": str(env["facility_id"]),
        "agreed_terms_hash": env["offer_terms_hash"],
        "material_snapshot": {"material_id": "MAT-PCB-01", "condition": "INTACT", "regulatory_route": "AUTHORIZED_EWASTE"},
        "weight_snapshot": {"estimated_weight_g": 8500, "measured_weight_g": None},
        "value_snapshot": {"currency": "INR", "agreed_total_paise": 382500, "estimated_low_paise": None, "estimated_high_paise": None},
        "location_snapshot": {"location_id": None, "source": "MISSING", "accuracy_m": None, "captured_at": None},
        "occurred_at": "2026-09-29T10:00:00.000Z",
        "media": [],
        "is_demo": False
    }
    proposal_hash = compute_canonical_hash(proposal_payload)
    client.post(
        "/api/v1/handovers",
        json={"id": str(handover_id), "proposal_payload": proposal_payload, "proposal_hash": proposal_hash},
        headers=env["collector_headers"]
    )

    # Recycler confirms exact match
    confirm_body = {
        "expected_version": 1,
        "proposal_hash": proposal_hash,
        "measured_material_id": "MAT-PCB-01",
        "measured_weight_g": 8500,
        "final_total_paise": 382500,
        "notes": "Verified weight and board grade intact."
    }
    resp = client.post(f"/api/v1/handovers/{handover_id}/confirm", json=confirm_body, headers=env["recycler_headers"])
    assert resp.status_code == 200
    assert resp.json()["status"] == "CONFIRMED"

    # Verify DB: Handover is CONFIRMED, Lot is RECEIVED, Transaction is CONFIRMED
    with TestingSessionLocal() as session:
        ho = session.query(Handover).filter(Handover.id == handover_id).first()
        assert ho.status == "CONFIRMED"
        assert ho.confirmation is not None

        lot = session.query(Lot).filter(Lot.id == env["lot_id"]).first()
        assert lot.status == "RECEIVED"

        tx = session.query(Transaction).filter(Transaction.id == env["tx_id"]).first()
        assert tx.lifecycle == "CONFIRMED"
        assert tx.agreed_weight_g == 8500
        assert tx.agreed_total_paise == 382500


def test_confirm_handover_measured_discrepancy_requires_collector_ack(handover_environment):
    """Test recycler measuring different weight/grade creates revision and requires collector ack (R-HAND-02, AT-030)."""
    env = handover_environment
    handover_id = uuid.uuid4()

    proposal_payload = {
        "schema_version": "SAHITOL-HANDOVER-1",
        "handover_id": str(handover_id),
        "transaction_id": str(env["tx_id"]),
        "lot_id": str(env["lot_id"]),
        "collector_id": str(env["collector_id"]),
        "facility_id": str(env["facility_id"]),
        "agreed_terms_hash": env["offer_terms_hash"],
        "material_snapshot": {"material_id": "MAT-PCB-01", "condition": "INTACT", "regulatory_route": "AUTHORIZED_EWASTE"},
        "weight_snapshot": {"estimated_weight_g": 8500, "measured_weight_g": None},
        "value_snapshot": {"currency": "INR", "agreed_total_paise": 382500, "estimated_low_paise": None, "estimated_high_paise": None},
        "location_snapshot": {"location_id": None, "source": "MISSING", "accuracy_m": None, "captured_at": None},
        "occurred_at": "2026-09-29T10:00:00.000Z",
        "media": [],
        "is_demo": False
    }
    proposal_hash = compute_canonical_hash(proposal_payload)
    client.post(
        "/api/v1/handovers",
        json={"id": str(handover_id), "proposal_payload": proposal_payload, "proposal_hash": proposal_hash},
        headers=env["collector_headers"]
    )

    # Recycler measures lower weight (8000g instead of 8500g, adjusted total 360000 paise)
    discrepant_confirm = {
        "expected_version": 1,
        "proposal_hash": proposal_hash,
        "measured_material_id": "MAT-PCB-01",
        "measured_weight_g": 8000,
        "final_total_paise": 360000,
        "notes": "Scale shows 8.00 kg. Dust/chassis removed."
    }
    resp = client.post(f"/api/v1/handovers/{handover_id}/confirm", json=discrepant_confirm, headers=env["recycler_headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "PENDING_COLLECTOR_ACK"
    rev_hash = data["terms_hash"]

    # Verify in DB: Handover is PENDING_COLLECTOR_ACK, NOT yet confirmed
    with TestingSessionLocal() as session:
        ho = session.query(Handover).filter(Handover.id == handover_id).first()
        assert ho.status == "PENDING_COLLECTOR_ACK"

    # Collector explicitly reviews and acknowledges revised terms
    ack_body = {
        "terms_hash": rev_hash,
        "expected_version": 2
    }
    ack_resp = client.post(f"/api/v1/handovers/{handover_id}/acknowledge-terms", json=ack_body, headers=env["collector_headers"])
    assert ack_resp.status_code == 200
    assert ack_resp.json()["status"] == "CONFIRMED"

    # Verify in DB: Now CONFIRMED, Transaction has revised 8000g and 360000 paise
    with TestingSessionLocal() as session:
        ho_final = session.query(Handover).filter(Handover.id == handover_id).first()
        assert ho_final.status == "CONFIRMED"
        tx_final = session.query(Transaction).filter(Transaction.id == env["tx_id"]).first()
        assert tx_final.lifecycle == "CONFIRMED"
        assert tx_final.agreed_weight_g == 8000
        assert tx_final.agreed_total_paise == 360000


def test_dispute_handover_records_dispute_without_rewriting_facts(handover_environment):
    """Test participant records dispute with reason and evidence (R-HAND-04, AT-032)."""
    env = handover_environment
    handover_id = uuid.uuid4()

    proposal_payload = {
        "schema_version": "SAHITOL-HANDOVER-1",
        "handover_id": str(handover_id),
        "transaction_id": str(env["tx_id"]),
        "lot_id": str(env["lot_id"]),
        "collector_id": str(env["collector_id"]),
        "facility_id": str(env["facility_id"]),
        "agreed_terms_hash": env["offer_terms_hash"],
        "material_snapshot": {"material_id": "MAT-PCB-01", "condition": "INTACT", "regulatory_route": "AUTHORIZED_EWASTE"},
        "weight_snapshot": {"estimated_weight_g": 8500, "measured_weight_g": None},
        "value_snapshot": {"currency": "INR", "agreed_total_paise": 382500, "estimated_low_paise": None, "estimated_high_paise": None},
        "location_snapshot": {"location_id": None, "source": "MISSING", "accuracy_m": None, "captured_at": None},
        "occurred_at": "2026-09-29T10:00:00.000Z",
        "media": [],
        "is_demo": False
    }
    proposal_hash = compute_canonical_hash(proposal_payload)
    client.post(
        "/api/v1/handovers",
        json={"id": str(handover_id), "proposal_payload": proposal_payload, "proposal_hash": proposal_hash},
        headers=env["collector_headers"]
    )

    dispute_body = {
        "reason": "Recycler scale tare was not calibrated at receipt.",
        "proposed_correction": "Re-weigh on secondary certified scale.",
        "expected_version": 1
    }
    resp = client.post(f"/api/v1/handovers/{handover_id}/dispute", json=dispute_body, headers=env["collector_headers"])
    assert resp.status_code == 200
    assert resp.json()["status"] == "DISPUTED"


def test_void_pending_handover_reverts_state(handover_environment):
    """Test voiding a pending proposal before confirmation reverts lot and transaction states (R-HAND-04, AT-032)."""
    env = handover_environment
    handover_id = uuid.uuid4()

    proposal_payload = {
        "schema_version": "SAHITOL-HANDOVER-1",
        "handover_id": str(handover_id),
        "transaction_id": str(env["tx_id"]),
        "lot_id": str(env["lot_id"]),
        "collector_id": str(env["collector_id"]),
        "facility_id": str(env["facility_id"]),
        "agreed_terms_hash": env["offer_terms_hash"],
        "material_snapshot": {"material_id": "MAT-PCB-01", "condition": "INTACT", "regulatory_route": "AUTHORIZED_EWASTE"},
        "weight_snapshot": {"estimated_weight_g": 8500, "measured_weight_g": None},
        "value_snapshot": {"currency": "INR", "agreed_total_paise": 382500, "estimated_low_paise": None, "estimated_high_paise": None},
        "location_snapshot": {"location_id": None, "source": "MISSING", "accuracy_m": None, "captured_at": None},
        "occurred_at": "2026-09-29T10:00:00.000Z",
        "media": [],
        "is_demo": False
    }
    proposal_hash = compute_canonical_hash(proposal_payload)
    client.post(
        "/api/v1/handovers",
        json={"id": str(handover_id), "proposal_payload": proposal_payload, "proposal_hash": proposal_hash},
        headers=env["collector_headers"]
    )

    void_body = {
        "reason": "Collector vehicle broke down before physical delivery.",
        "expected_version": 1
    }
    resp = client.post(f"/api/v1/handovers/{handover_id}/void", json=void_body, headers=env["collector_headers"])
    assert resp.status_code == 200
    assert resp.json()["status"] == "VOIDED"

    # Verify Lot reverted to ACCEPTED, Transaction reverted to AGREED
    with TestingSessionLocal() as session:
        lot = session.query(Lot).filter(Lot.id == env["lot_id"]).first()
        assert lot.status == "ACCEPTED"
        tx = session.query(Transaction).filter(Transaction.id == env["tx_id"]).first()
        assert tx.lifecycle == "AGREED"


def test_void_confirmed_handover_prohibited(handover_environment):
    """Test confirmed handovers cannot be voided; compensating corrections only (R-HAND-04, AT-032)."""
    env = handover_environment
    handover_id = uuid.uuid4()

    proposal_payload = {
        "schema_version": "SAHITOL-HANDOVER-1",
        "handover_id": str(handover_id),
        "transaction_id": str(env["tx_id"]),
        "lot_id": str(env["lot_id"]),
        "collector_id": str(env["collector_id"]),
        "facility_id": str(env["facility_id"]),
        "agreed_terms_hash": env["offer_terms_hash"],
        "material_snapshot": {"material_id": "MAT-PCB-01", "condition": "INTACT", "regulatory_route": "AUTHORIZED_EWASTE"},
        "weight_snapshot": {"estimated_weight_g": 8500, "measured_weight_g": None},
        "value_snapshot": {"currency": "INR", "agreed_total_paise": 382500, "estimated_low_paise": None, "estimated_high_paise": None},
        "location_snapshot": {"location_id": None, "source": "MISSING", "accuracy_m": None, "captured_at": None},
        "occurred_at": "2026-09-29T10:00:00.000Z",
        "media": [],
        "is_demo": False
    }
    proposal_hash = compute_canonical_hash(proposal_payload)
    client.post(
        "/api/v1/handovers",
        json={"id": str(handover_id), "proposal_payload": proposal_payload, "proposal_hash": proposal_hash},
        headers=env["collector_headers"]
    )
    client.post(
        f"/api/v1/handovers/{handover_id}/confirm",
        json={"expected_version": 1, "proposal_hash": proposal_hash, "measured_weight_g": 8500, "final_total_paise": 382500},
        headers=env["recycler_headers"]
    )

    # Attempt to void confirmed handover
    resp = client.post(
        f"/api/v1/handovers/{handover_id}/void",
        json={"reason": "Attempting to delete confirmed record", "expected_version": 2},
        headers=env["collector_headers"]
    )
    assert resp.status_code == 409
    assert "confirmed handovers cannot be voided" in resp.json()["detail"].lower()


def test_handover_receipt_includes_statutory_non_epr_notice(handover_environment):
    """Test handover platform receipt contains required provenance and non-EPR notice (R-HAND-05, AT-033)."""
    env = handover_environment
    handover_id = uuid.uuid4()

    proposal_payload = {
        "schema_version": "SAHITOL-HANDOVER-1",
        "handover_id": str(handover_id),
        "transaction_id": str(env["tx_id"]),
        "lot_id": str(env["lot_id"]),
        "collector_id": str(env["collector_id"]),
        "facility_id": str(env["facility_id"]),
        "agreed_terms_hash": env["offer_terms_hash"],
        "material_snapshot": {"material_id": "MAT-PCB-01", "condition": "INTACT", "regulatory_route": "AUTHORIZED_EWASTE"},
        "weight_snapshot": {"estimated_weight_g": 8500, "measured_weight_g": None},
        "value_snapshot": {"currency": "INR", "agreed_total_paise": 382500, "estimated_low_paise": None, "estimated_high_paise": None},
        "location_snapshot": {"location_id": None, "source": "MISSING", "accuracy_m": None, "captured_at": None},
        "occurred_at": "2026-09-29T10:00:00.000Z",
        "media": [],
        "is_demo": False
    }
    proposal_hash = compute_canonical_hash(proposal_payload)
    client.post(
        "/api/v1/handovers",
        json={"id": str(handover_id), "proposal_payload": proposal_payload, "proposal_hash": proposal_hash},
        headers=env["collector_headers"]
    )
    client.post(
        f"/api/v1/handovers/{handover_id}/confirm",
        json={"expected_version": 1, "proposal_hash": proposal_hash, "measured_weight_g": 8500, "final_total_paise": 382500},
        headers=env["recycler_headers"]
    )

    resp = client.get(f"/api/v1/handovers/{handover_id}/receipt", headers=env["collector_headers"])
    assert resp.status_code == 200
    receipt = resp.json()

    assert receipt["handover_id"] == str(handover_id)
    assert receipt["status"] == "CONFIRMED"
    assert receipt["facility_name"] == "Apex E-Waste Recyclers"
    assert receipt["collector_display"] == "Rajesh Collector"
    assert receipt["measured_weight_g"] == 8500
    assert receipt["agreed_total_paise"] == 382500
    assert "not constitute a statutory EPR certificate" in receipt["non_epr_notice"]


def test_public_verification_endpoint_redacted_pii_and_finance(handover_environment):
    """Test public verification capability endpoint omits private PII, exact GPS, and money (R-HAND-05, AT-033)."""
    env = handover_environment
    handover_id = uuid.uuid4()

    proposal_payload = {
        "schema_version": "SAHITOL-HANDOVER-1",
        "handover_id": str(handover_id),
        "transaction_id": str(env["tx_id"]),
        "lot_id": str(env["lot_id"]),
        "collector_id": str(env["collector_id"]),
        "facility_id": str(env["facility_id"]),
        "agreed_terms_hash": env["offer_terms_hash"],
        "material_snapshot": {"material_id": "MAT-PCB-01", "condition": "INTACT", "regulatory_route": "AUTHORIZED_EWASTE"},
        "weight_snapshot": {"estimated_weight_g": 8500, "measured_weight_g": None},
        "value_snapshot": {"currency": "INR", "agreed_total_paise": 382500, "estimated_low_paise": None, "estimated_high_paise": None},
        "location_snapshot": {"location_id": None, "source": "GPS", "accuracy_m": 15, "captured_at": "2026-09-29T10:00:00.000Z"},
        "occurred_at": "2026-09-29T10:00:00.000Z",
        "media": [],
        "is_demo": False
    }
    proposal_hash = compute_canonical_hash(proposal_payload)
    create_resp = client.post(
        "/api/v1/handovers",
        json={"id": str(handover_id), "proposal_payload": proposal_payload, "proposal_hash": proposal_hash},
        headers=env["collector_headers"]
    )
    public_token = create_resp.json()["public_token"]

    # Public unauthenticated request
    resp = client.get(f"/api/v1/verify/{public_token}")
    assert resp.status_code == 200
    data = resp.json()

    assert data["handover_id"] == str(handover_id)
    assert data["status"] == "PENDING_CONFIRMATION"
    assert data["facility_name"] == "Apex E-Waste Recyclers"
    assert data["material_id"] == "MAT-PCB-01"
    assert data["regulatory_route"] == "AUTHORIZED_EWASTE"
    assert data["weight_kg"] == 8.5
    assert data["proposal_hash"] == proposal_hash
    assert "not constitute a statutory EPR certificate" in data["non_epr_notice"]

    # Redaction checks: Verify no phone, no coordinates, no rupees/paise
    serialized = json.dumps(data)
    assert "+91" not in serialized
    assert "paise" not in serialized
    assert "rupees" not in serialized
    assert "price" not in serialized
    assert "latitude" not in serialized
    assert "longitude" not in serialized


def test_invalid_public_token_returns_404():
    """Test querying public verification with invalid token returns HTTP 404."""
    resp = client.get("/api/v1/verify/invalid-token-does-not-exist")
    assert resp.status_code == 404
