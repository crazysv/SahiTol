"""Comprehensive test suite for Recycler Profile and Offer Workflows (T021).
Covers requirements: R-OFFER-01, R-OFFER-02, R-REC-03, R-PRICE-04, R-DATA-03.
Acceptance cases: AT-019, AT-023, AT-027, AT-028, AT-055.
"""
import uuid
from datetime import datetime, timedelta, timezone
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
from app.db.models.lot import LocationRecord, Lot, LotImage, MediaObject
from app.db.models.material import Material
from app.db.models.trade import LotRequest, Offer, TermsRevision, Transaction
from app.db.seeds.materials import seed_materials
from app.security import create_access_token
from tests.test_db import TestingSessionLocal, override_get_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_trade_module():
    """Setup test database dependency override and seed taxonomy."""
    app.dependency_overrides[get_db] = override_get_db
    with TestingSessionLocal() as session:
        seed_materials(session)
        # Ensure DELHI_NCR region exists
        reg = session.query(Region).filter(Region.id == "DELHI_NCR").first()
        if not reg:
            reg = Region(id="DELHI_NCR", name="Delhi-NCR", state_code="DL", kind="METRO")
            session.add(reg)
            session.commit()
    yield


@pytest.fixture
def collector_user():
    """Create test collector user with linked collector record."""
    user_id = uuid.uuid4()
    collector_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        user = User(
            id=user_id,
            phone_normalized="+919811111111",
            pin_hash="pin_hash",
            role="COLLECTOR",
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(user)
        col = Collector(
            id=collector_id,
            user_id=user_id,
            display_alias="Rajesh Scrap",
            preferred_language="hi",
            region_id="DELHI_NCR",
            general_area="Mayapuri",
            consent_version="v1.0"
        )
        session.add(col)
        session.commit()

    token = create_access_token(subject=str(user_id), role="COLLECTOR", is_demo=False)
    return {
        "user_id": user_id,
        "collector_id": collector_id,
        "headers": {"Authorization": f"Bearer {token}"}
    }


@pytest.fixture
def other_collector_user():
    """Create a second distinct collector user."""
    user_id = uuid.uuid4()
    collector_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        user = User(
            id=user_id,
            phone_normalized="+919822222222",
            pin_hash="pin_hash",
            role="COLLECTOR",
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(user)
        col = Collector(
            id=collector_id,
            user_id=user_id,
            display_alias="Santosh E-waste",
            preferred_language="hi",
            region_id="DELHI_NCR",
            general_area="Seelampur",
            consent_version="v1.0"
        )
        session.add(col)
        session.commit()

    token = create_access_token(subject=str(user_id), role="COLLECTOR", is_demo=False)
    return {
        "user_id": user_id,
        "collector_id": collector_id,
        "headers": {"Authorization": f"Bearer {token}"}
    }


@pytest.fixture
def recycler_setup():
    """Create test formal e-waste facility and authorized recycler user."""
    fac_id = uuid.uuid4()
    user_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        user = User(
            id=user_id,
            phone_normalized="+919833333333",
            pin_hash="pin_hash",
            role="RECYCLER",
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(user)

        fac = Facility(
            id=fac_id,
            name="GreenEarth Dismantlers",
            facility_name="GreenEarth Dismantlers Pvt Ltd",
            kind="DISMANTLER",
            address_public="Plot 12, Mayapuri Industrial Area Phase II, New Delhi",
            district="West Delhi",
            state="Delhi",
            region_id="DELHI_NCR",
            contact_public="info@greenearth.example.com",
            active=True,
            version=1
        )
        session.add(fac)

        fu = FacilityUser(
            user_id=user_id,
            facility_id=fac_id,
            membership_role="OWNER",
            active=True
        )
        session.add(fu)

        # Authorized for AUTHORIZED_EWASTE
        auth = FacilityAuthorization(
            id=uuid.uuid4(),
            facility_id=fac_id,
            route="AUTHORIZED_EWASTE",
            authority="DPCC",
            reference="DPCC/EW/2024/099",
            status="VALID",
            verification_level="REGISTRY_MATCH",
            valid_from=datetime.now(timezone.utc) - timedelta(days=30),
            valid_until=datetime.now(timezone.utc) + timedelta(days=365)
        )
        session.add(auth)

        # Operational profile (unknown pickup initial state)
        ops = FacilityOperation(
            facility_id=fac_id,
            pickup_status=None,
            service_regions="West Delhi, South Delhi",
            accepting_status="ACCEPTING",
            operational_updated_at=datetime.now(timezone.utc),
            source_id="INITIAL_IMPORT"
        )
        session.add(ops)

        # Accepted materials
        fm = FacilityMaterial(
            id=uuid.uuid4(),
            facility_id=fac_id,
            material_id="MAT-PCB-01",
            route="AUTHORIZED_EWASTE",
            accepted=True,
            min_weight_g=1000,
            max_weight_g=500000,
            updated_at=datetime.now(timezone.utc)
        )
        session.add(fm)

        # Facility rate
        fr = FacilityRate(
            id=uuid.uuid4(),
            facility_id=fac_id,
            material_id="MAT-PCB-01",
            condition="INTACT",
            region_id="DELHI_NCR",
            rate_paise_per_unit=45000,
            unit="kg",
            price_kind="QUOTE",
            observed_at=datetime.now(timezone.utc),
            valid_until=datetime.now(timezone.utc) + timedelta(days=30),
            source_id=f"FACILITY_QUOTE_{fac_id}",
            review_status="VERIFIED",
            is_demo=False
        )
        session.add(fr)

        session.commit()

    token = create_access_token(subject=str(user_id), role="RECYCLER", is_demo=False)
    return {
        "facility_id": fac_id,
        "user_id": user_id,
        "headers": {"Authorization": f"Bearer {token}"}
    }


@pytest.fixture
def battery_facility_setup():
    """Create test specialized battery facility authorized for BATTERY_ISOLATION."""
    fac_id = uuid.uuid4()
    user_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        user = User(
            id=user_id,
            phone_normalized="+919844444444",
            pin_hash="pin_hash",
            role="RECYCLER",
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(user)

        fac = Facility(
            id=fac_id,
            name="SafeBattery Solutions",
            facility_name="SafeBattery Solutions LLP",
            kind="RECYCLER",
            address_public="Plot 88, Okhla Phase I, New Delhi",
            district="South East Delhi",
            state="Delhi",
            region_id="DELHI_NCR",
            contact_public="contact@safebattery.example.com",
            active=True,
            version=1
        )
        session.add(fac)

        fu = FacilityUser(
            user_id=user_id,
            facility_id=fac_id,
            membership_role="MANAGER",
            active=True
        )
        session.add(fu)

        # Authorized for BATTERY_ISOLATION
        auth = FacilityAuthorization(
            id=uuid.uuid4(),
            facility_id=fac_id,
            route="BATTERY_ISOLATION",
            authority="CPCB",
            reference="CPCB/BAT/2024/001",
            status="VALID",
            verification_level="INSPECTION_AUDITED",
            valid_from=datetime.now(timezone.utc) - timedelta(days=60),
            valid_until=datetime.now(timezone.utc) + timedelta(days=700)
        )
        session.add(auth)

        # Accepted materials
        fm = FacilityMaterial(
            id=uuid.uuid4(),
            facility_id=fac_id,
            material_id="MAT-BAT-01",
            route="BATTERY_ISOLATION",
            accepted=True,
            min_weight_g=2000,
            updated_at=datetime.now(timezone.utc)
        )
        session.add(fm)

        session.commit()

    token = create_access_token(subject=str(user_id), role="RECYCLER", is_demo=False)
    return {
        "facility_id": fac_id,
        "user_id": user_id,
        "headers": {"Authorization": f"Bearer {token}"}
    }


@pytest.fixture
def admin_user():
    """Create test admin user."""
    user_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        user = User(
            id=user_id,
            phone_normalized="+919899999999",
            pin_hash="pin_hash",
            role="ADMIN",
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(user)
        session.commit()

    token = create_access_token(subject=str(user_id), role="ADMIN", is_demo=False)
    return {
        "user_id": user_id,
        "headers": {"Authorization": f"Bearer {token}"}
    }


# --- Test Cases ---

def test_recycler_profile_retrieval(recycler_setup):
    """Test recycler views profile with authorizations, operational data, materials, and rates."""
    resp = client.get("/api/v1/recycler/profile", headers=recycler_setup["headers"])
    assert resp.status_code == 200
    data = resp.json()

    assert data["facility_id"] == str(recycler_setup["facility_id"])
    assert data["name"] == "GreenEarth Dismantlers"
    assert data["kind"] == "DISMANTLER"
    assert len(data["authorizations"]) == 1
    assert data["authorizations"][0]["route"] == "AUTHORIZED_EWASTE"
    assert data["authorizations"][0]["authority"] == "DPCC"
    assert data["authorizations"][0]["verification_level"] == "REGISTRY_MATCH"
    assert data["operations"]["pickup_status"] is None  # Unknown preserved
    assert len(data["materials"]) == 1
    assert data["materials"][0]["material_id"] == "MAT-PCB-01"
    assert len(data["rates"]) == 1
    assert data["rates"][0]["rate_paise_per_unit"] == 45000


def test_recycler_profile_operational_update_and_provenance(recycler_setup):
    """Test facility user updates operational data with provenance while authorizations stay intact (AT-023)."""
    payload = {
        "facility_id": str(recycler_setup["facility_id"]),
        "pickup_status": True,
        "service_regions": "All Delhi-NCR, Gurgaon, Noida",
        "accepting_status": "ACCEPTING",
        "materials": [
            {
                "material_id": "MAT-PCB-01",
                "route": "AUTHORIZED_EWASTE",
                "accepted": True,
                "min_weight_g": 500,
                "max_weight_g": 1000000
            }
        ],
        "rates": [
            {
                "material_id": "MAT-PCB-01",
                "condition": "INTACT",
                "rate_paise_per_unit": 47000,
                "unit": "kg"
            }
        ]
    }
    resp = client.patch("/api/v1/recycler/profile", json=payload, headers=recycler_setup["headers"])
    assert resp.status_code == 200
    data = resp.json()

    assert data["operations"]["pickup_status"] is True
    assert data["operations"]["service_regions"] == "All Delhi-NCR, Gurgaon, Noida"
    assert data["operations"]["source_id"] == f"SELF_DECLARED_USER_{recycler_setup['user_id']}"
    assert data["version"] >= 2
    assert data["materials"][0]["min_weight_g"] == 500
    assert data["rates"][0]["rate_paise_per_unit"] == 47000


def test_recycler_profile_unknown_pickup_preserved(recycler_setup):
    """Test clearing pickup status explicitly preserves unknown (AT-023)."""
    payload = {
        "facility_id": str(recycler_setup["facility_id"]),
        "clear_pickup_status": True
    }
    resp = client.patch("/api/v1/recycler/profile", json=payload, headers=recycler_setup["headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert data["operations"]["pickup_status"] is None


def test_recycler_profile_authorization_tampering_prohibited(recycler_setup):
    """Test facility user cannot tamper with legal authorizations or verification status (AT-023)."""
    payload = {
        "facility_id": str(recycler_setup["facility_id"]),
        "authorizations": [
            {
                "route": "HAZARDOUS_DISPOSAL",
                "authority": "DPCC",
                "status": "VALID"
            }
        ]
    }
    resp = client.patch("/api/v1/recycler/profile", json=payload, headers=recycler_setup["headers"])
    assert resp.status_code == 403
    assert "admin-controlled" in resp.json()["detail"].lower()


def test_create_directed_lot_request_success(collector_user, recycler_setup):
    """Test collector submits lot request to compatible facility (R-OFFER-01 / AT-027)."""
    # Create COLLECTED lot for collector_user
    lot_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        lot = Lot(
            id=lot_id,
            collector_id=collector_user["collector_id"],
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=5000,
            condition="INTACT",
            description="Testing e-waste lot",
            status="COLLECTED",
            version=1,
            is_demo=False
        )
        session.add(lot)
        session.commit()

    body = {
        "facility_id": str(recycler_setup["facility_id"]),
        "notes": "Please provide your best rate for 5kg high-grade motherboards."
    }
    resp = client.post(f"/api/v1/lots/{lot_id}/requests", json=body, headers=collector_user["headers"])
    assert resp.status_code == 201
    data = resp.json()

    assert data["lot_id"] == str(lot_id)
    assert data["facility_id"] == str(recycler_setup["facility_id"])
    assert data["state"] == "PENDING"
    assert data["reason"] == body["notes"]

    # Verify lot state advanced to MATCHED
    with TestingSessionLocal() as session:
        updated_lot = session.query(Lot).filter(Lot.id == lot_id).first()
        assert updated_lot.status == "MATCHED"


def test_create_directed_lot_request_battery_isolation_hard_guard(collector_user, recycler_setup):
    """Test battery lot cannot be directed to general e-waste facility (R-REC-04 / AT-024)."""
    lot_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        lot = Lot(
            id=lot_id,
            collector_id=collector_user["collector_id"],
            material_id="MAT-BAT-01",
            regulatory_route="BATTERY_ISOLATION",
            estimated_weight_g=12000,
            condition="INTACT",
            status="COLLECTED",
            version=1,
            is_demo=False
        )
        session.add(lot)
        session.commit()

    body = {
        "facility_id": str(recycler_setup["facility_id"])
    }
    resp = client.post(f"/api/v1/lots/{lot_id}/requests", json=body, headers=collector_user["headers"])
    assert resp.status_code == 422
    assert "battery isolation" in resp.json()["detail"].lower()


def test_create_directed_lot_request_battery_facility_compatible(collector_user, battery_facility_setup):
    """Test battery lot directed to battery-authorized facility succeeds."""
    lot_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        lot = Lot(
            id=lot_id,
            collector_id=collector_user["collector_id"],
            material_id="MAT-BAT-01",
            regulatory_route="BATTERY_ISOLATION",
            estimated_weight_g=12000,
            condition="INTACT",
            status="COLLECTED",
            version=1,
            is_demo=False
        )
        session.add(lot)
        session.commit()

    body = {
        "facility_id": str(battery_facility_setup["facility_id"]),
        "notes": "Lead acid battery 12kg"
    }
    resp = client.post(f"/api/v1/lots/{lot_id}/requests", json=body, headers=collector_user["headers"])
    assert resp.status_code == 201
    assert resp.json()["state"] == "PENDING"


def test_create_directed_lot_request_forbidden_for_other_collector(other_collector_user, recycler_setup):
    """Test collector cannot direct someone else's lot."""
    lot_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        lot = Lot(
            id=lot_id,
            collector_id=uuid.uuid4(),  # Different owner
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=2000,
            status="COLLECTED",
            version=1,
            is_demo=False
        )
        session.add(lot)
        session.commit()

    body = {"facility_id": str(recycler_setup["facility_id"])}
    resp = client.post(f"/api/v1/lots/{lot_id}/requests", json=body, headers=other_collector_user["headers"])
    assert resp.status_code == 403


def test_recycler_incoming_queue_and_privacy(collector_user, recycler_setup):
    """Test recycler views incoming requests with location privacy protection (coarse area only, no exact GPS)."""
    lot_id = uuid.uuid4()
    loc_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        loc = LocationRecord(
            id=loc_id,
            owner_entity_id=lot_id,
            coarse_area="Mayapuri Industrial Area",
            accuracy_m=12.5,
            source="GPS",
            consent_version="v1.0"
        )
        session.add(loc)

        lot = Lot(
            id=lot_id,
            collector_id=collector_user["collector_id"],
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=8000,
            condition="INTACT",
            description="Telecom server boards",
            collection_location_id=loc_id,
            status="COLLECTED",
            version=1,
            is_demo=False
        )
        session.add(lot)
        session.commit()

    # Direct request
    client.post(
        f"/api/v1/lots/{lot_id}/requests",
        json={"facility_id": str(recycler_setup["facility_id"]), "notes": "Need quote"},
        headers=collector_user["headers"]
    )

    # Recycler incoming
    resp = client.get("/api/v1/recycler/incoming", headers=recycler_setup["headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1

    item = next(x for x in data if x["lot_id"] == str(lot_id))
    assert item["lot"]["material_id"] == "MAT-PCB-01"
    assert item["lot"]["estimated_weight_g"] == 8000
    assert item["lot"]["collector_alias"] == "Rajesh Scrap"
    # Verify location privacy: coarse area only, no raw lat/lon exposed in payload
    assert item["lot"]["coarse_area"] == "Mayapuri Industrial Area"
    assert "latitude" not in str(item["lot"])
    assert "longitude" not in str(item["lot"])


def test_quote_offer_rate_per_kg_and_fixed_total(collector_user, recycler_setup):
    """Test recycler quotes offer with RATE_PER_KG and FIXED_TOTAL, canonical terms_hash generation."""
    lot_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        lot = Lot(
            id=lot_id,
            collector_id=collector_user["collector_id"],
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=4000,
            condition="INTACT",
            status="COLLECTED",
            version=1,
            is_demo=False
        )
        session.add(lot)
        session.commit()

    req_resp = client.post(
        f"/api/v1/lots/{lot_id}/requests",
        json={"facility_id": str(recycler_setup["facility_id"])},
        headers=collector_user["headers"]
    )
    req_id = req_resp.json()["id"]

    # 1. Quote offer with RATE_PER_KG
    offer_body = {
        "price_basis": "RATE_PER_KG",
        "rate_paise_per_kg": 46000,
        "condition": "INTACT",
        "weight_basis_g": 4000
    }
    resp = client.post(f"/api/v1/requests/{req_id}/offers", json=offer_body, headers=recycler_setup["headers"])
    assert resp.status_code == 201
    offer_data = resp.json()

    assert offer_data["price_basis"] == "RATE_PER_KG"
    assert offer_data["rate_paise_per_kg"] == 46000
    assert offer_data["status"] == "OPEN"
    assert len(offer_data["terms_hash"]) == 64
    assert offer_data["is_expired"] is False
    assert offer_data["effective_rate_paise_per_kg"] == 46000

    duplicate = client.post(
        f"/api/v1/requests/{req_id}/offers",
        json=offer_body,
        headers=recycler_setup["headers"]
    )
    assert duplicate.status_code == 409
    assert "active offer" in duplicate.json()["detail"]

    # 2. Quote offer with FIXED_TOTAL
    lot_id_2 = uuid.uuid4()
    with TestingSessionLocal() as session:
        lot2 = Lot(
            id=lot_id_2,
            collector_id=collector_user["collector_id"],
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=2000,
            condition="PARTIAL",
            status="COLLECTED",
            version=1,
            is_demo=False
        )
        session.add(lot2)
        session.commit()

    req2 = client.post(
        f"/api/v1/lots/{lot_id_2}/requests",
        json={"facility_id": str(recycler_setup["facility_id"])},
        headers=collector_user["headers"]
    ).json()

    fixed_body = {
        "price_basis": "FIXED_TOTAL",
        "fixed_total_paise": 90000,
        "condition": "PARTIAL",
        "weight_basis_g": 2000
    }
    resp2 = client.post(f"/api/v1/requests/{req2['id']}/offers", json=fixed_body, headers=recycler_setup["headers"])
    assert resp2.status_code == 201
    offer2_data = resp2.json()
    assert offer2_data["price_basis"] == "FIXED_TOTAL"
    assert offer2_data["fixed_total_paise"] == 90000
    assert offer2_data["effective_rate_paise_per_kg"] == 45000  # 90000 / 2kg = 45000/kg


def test_quote_offer_negative_or_zero_rate_rejected(collector_user, recycler_setup):
    """Test negative or zero prices are rejected with HTTP 422."""
    lot_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        lot = Lot(
            id=lot_id,
            collector_id=collector_user["collector_id"],
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=1000,
            status="COLLECTED",
            version=1,
            is_demo=False
        )
        session.add(lot)
        session.commit()

    req_id = client.post(
        f"/api/v1/lots/{lot_id}/requests",
        json={"facility_id": str(recycler_setup["facility_id"])},
        headers=collector_user["headers"]
    ).json()["id"]

    resp = client.post(
        f"/api/v1/requests/{req_id}/offers",
        json={"price_basis": "RATE_PER_KG", "rate_paise_per_kg": -500},
        headers=recycler_setup["headers"]
    )
    assert resp.status_code == 422


def test_recycler_reject_request_allows_collector_rematch(collector_user, recycler_setup):
    """Test recycler rejection leaves request history and returns lot to LISTED so collector can rematch (AT-027)."""
    lot_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        lot = Lot(
            id=lot_id,
            collector_id=collector_user["collector_id"],
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=3000,
            status="COLLECTED",
            version=1,
            is_demo=False
        )
        session.add(lot)
        session.commit()

    req_id = client.post(
        f"/api/v1/lots/{lot_id}/requests",
        json={"facility_id": str(recycler_setup["facility_id"])},
        headers=collector_user["headers"]
    ).json()["id"]

    # Reject
    resp = client.post(
        f"/api/v1/requests/{req_id}/reject",
        json={"reason": "Capacity full for motherboards this week."},
        headers=recycler_setup["headers"]
    )
    assert resp.status_code == 200
    assert resp.json()["state"] == "REJECTED"
    assert resp.json()["lot_status"] == "LISTED"

    # Verify in DB: request history preserved and lot status is LISTED
    with TestingSessionLocal() as session:
        req = session.query(LotRequest).filter(LotRequest.id == uuid.UUID(req_id)).first()
        assert req.state == "REJECTED"
        assert req.reason == "Capacity full for motherboards this week."
        lot = session.query(Lot).filter(Lot.id == lot_id).first()
        assert lot.status == "LISTED"


def test_recycler_withdraw_offer(collector_user, recycler_setup):
    """Test recycler withdraws open offer before collector acceptance."""
    lot_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        lot = Lot(
            id=lot_id,
            collector_id=collector_user["collector_id"],
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=2500,
            status="COLLECTED",
            version=1,
            is_demo=False
        )
        session.add(lot)
        session.commit()

    req_id = client.post(
        f"/api/v1/lots/{lot_id}/requests",
        json={"facility_id": str(recycler_setup["facility_id"])},
        headers=collector_user["headers"]
    ).json()["id"]

    offer_data = client.post(
        f"/api/v1/requests/{req_id}/offers",
        json={"price_basis": "RATE_PER_KG", "rate_paise_per_kg": 44000},
        headers=recycler_setup["headers"]
    ).json()

    # Withdraw offer
    resp = client.post(
        f"/api/v1/offers/{offer_data['id']}/withdraw",
        json={"expected_version": 1, "reason": "Rate adjustment"},
        headers=recycler_setup["headers"]
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "WITHDRAWN"


def test_collector_accept_offer_creates_atomic_transaction(collector_user, recycler_setup):
    """Test collector accepts live offer creating an immutable transaction and initial revision (R-OFFER-02 / AT-028)."""
    lot_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        lot = Lot(
            id=lot_id,
            collector_id=collector_user["collector_id"],
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=5000,
            condition="INTACT",
            status="COLLECTED",
            version=1,
            is_demo=False
        )
        session.add(lot)
        session.commit()

    req_id = client.post(
        f"/api/v1/lots/{lot_id}/requests",
        json={"facility_id": str(recycler_setup["facility_id"])},
        headers=collector_user["headers"]
    ).json()["id"]

    offer = client.post(
        f"/api/v1/requests/{req_id}/offers",
        json={"price_basis": "RATE_PER_KG", "rate_paise_per_kg": 46000, "condition": "INTACT", "weight_basis_g": 5000},
        headers=recycler_setup["headers"]
    ).json()

    # Collector accepts offer
    accept_payload = {
        "terms_hash": offer["terms_hash"],
        "expected_version": 1
    }
    resp = client.post(f"/api/v1/offers/{offer['id']}/accept", json=accept_payload, headers=collector_user["headers"])
    assert resp.status_code == 200
    tx_data = resp.json()

    assert tx_data["lot_id"] == str(lot_id)
    assert tx_data["collector_id"] == str(collector_user["collector_id"])
    assert tx_data["facility_id"] == str(recycler_setup["facility_id"])
    assert tx_data["accepted_offer_id"] == str(offer["id"])
    assert tx_data["estimated_weight_g"] == 5000
    assert tx_data["quoted_total_paise"] == 230000  # 46000 * 5kg = 230000 paise (Rs 2300.00)
    assert tx_data["agreed_total_paise"] == 230000
    assert tx_data["lifecycle"] == "AGREED"
    assert len(tx_data["revisions"]) == 1
    assert tx_data["revisions"][0]["terms_hash"] == offer["terms_hash"]

    # Verify lot in DB is now ACCEPTED
    with TestingSessionLocal() as session:
        updated_lot = session.query(Lot).filter(Lot.id == lot_id).first()
        assert updated_lot.status == "ACCEPTED"


def test_expired_offer_cannot_bind(collector_user, recycler_setup):
    """Test cached expired offer cannot silently bind (R-OFFER-02 / AT-028)."""
    lot_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        lot = Lot(
            id=lot_id,
            collector_id=collector_user["collector_id"],
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=2000,
            status="COLLECTED",
            version=1,
            is_demo=False
        )
        session.add(lot)
        session.commit()

    req_id = client.post(
        f"/api/v1/lots/{lot_id}/requests",
        json={"facility_id": str(recycler_setup["facility_id"])},
        headers=collector_user["headers"]
    ).json()["id"]

    offer = client.post(
        f"/api/v1/requests/{req_id}/offers",
        json={"price_basis": "RATE_PER_KG", "rate_paise_per_kg": 45000},
        headers=recycler_setup["headers"]
    ).json()

    # Manually expire the offer in DB to simulate expired cache
    with TestingSessionLocal() as session:
        off_db = session.query(Offer).filter(Offer.id == uuid.UUID(offer["id"])).first()
        off_db.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        session.commit()

    # Attempt to accept expired offer
    accept_payload = {
        "terms_hash": offer["terms_hash"],
        "expected_version": 1
    }
    resp = client.post(f"/api/v1/offers/{offer['id']}/accept", json=accept_payload, headers=collector_user["headers"])
    assert resp.status_code == 409
    assert "expired" in resp.json()["detail"].lower()


def test_tampered_terms_hash_rejected(collector_user, recycler_setup):
    """Test accepting with tampered terms_hash is rejected (R-OFFER-02 / AT-028)."""
    lot_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        lot = Lot(
            id=lot_id,
            collector_id=collector_user["collector_id"],
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=2000,
            status="COLLECTED",
            version=1,
            is_demo=False
        )
        session.add(lot)
        session.commit()

    req_id = client.post(
        f"/api/v1/lots/{lot_id}/requests",
        json={"facility_id": str(recycler_setup["facility_id"])},
        headers=collector_user["headers"]
    ).json()["id"]

    offer = client.post(
        f"/api/v1/requests/{req_id}/offers",
        json={"price_basis": "RATE_PER_KG", "rate_paise_per_kg": 45000},
        headers=recycler_setup["headers"]
    ).json()

    # Tampered hash
    accept_payload = {
        "terms_hash": "a" * 64,
        "expected_version": 1
    }
    resp = client.post(f"/api/v1/offers/{offer['id']}/accept", json=accept_payload, headers=collector_user["headers"])
    assert resp.status_code == 409
    assert "terms hash mismatch" in resp.json()["detail"].lower()


def test_second_open_offer_is_rejected_and_acceptance_creates_one_agreement(collector_user, recycler_setup, battery_facility_setup):
    """A request has one open offer; accepting it creates exactly one agreement (R-OFFER-02 / AT-028)."""
    lot_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        lot = Lot(
            id=lot_id,
            collector_id=collector_user["collector_id"],
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=10000,
            status="COLLECTED",
            version=1,
            is_demo=False
        )
        session.add(lot)
        session.commit()

    req_id = client.post(
        f"/api/v1/lots/{lot_id}/requests",
        json={"facility_id": str(recycler_setup["facility_id"])},
        headers=collector_user["headers"]
    ).json()["id"]

    # Facility makes Offer 1
    offer1 = client.post(
        f"/api/v1/requests/{req_id}/offers",
        json={"price_basis": "RATE_PER_KG", "rate_paise_per_kg": 45000},
        headers=recycler_setup["headers"]
    ).json()

    # A retry/reload cannot create a competing open offer for the same request.
    offer2 = client.post(
        f"/api/v1/requests/{req_id}/offers",
        json={"price_basis": "RATE_PER_KG", "rate_paise_per_kg": 47000},
        headers=recycler_setup["headers"]
    )
    assert offer2.status_code == 409

    # Accept Offer 1
    resp1 = client.post(
        f"/api/v1/offers/{offer1['id']}/accept",
        json={"terms_hash": offer1["terms_hash"], "expected_version": 1},
        headers=collector_user["headers"]
    )
    assert resp1.status_code == 200

    # Verify exactly one active transaction exists for this lot
    with TestingSessionLocal() as session:
        txs = session.query(Transaction).filter(Transaction.lot_id == lot_id).all()
        assert len(txs) == 1


def test_price_board_refresh_does_not_modify_accepted_terms(collector_user, recycler_setup):
    """Test later price board changes do not mutate accepted transaction terms (R-OFFER-02 / AT-028)."""
    lot_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        lot = Lot(
            id=lot_id,
            collector_id=collector_user["collector_id"],
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=1000,
            status="COLLECTED",
            version=1,
            is_demo=False
        )
        session.add(lot)
        session.commit()

    req_id = client.post(
        f"/api/v1/lots/{lot_id}/requests",
        json={"facility_id": str(recycler_setup["facility_id"])},
        headers=collector_user["headers"]
    ).json()["id"]

    offer = client.post(
        f"/api/v1/requests/{req_id}/offers",
        json={"price_basis": "RATE_PER_KG", "rate_paise_per_kg": 46000},
        headers=recycler_setup["headers"]
    ).json()

    tx_resp = client.post(
        f"/api/v1/offers/{offer['id']}/accept",
        json={"terms_hash": offer["terms_hash"], "expected_version": 1},
        headers=collector_user["headers"]
    )
    tx_id = tx_resp.json()["id"]

    # Facility updates their public rate from 46000 to 20000
    client.patch(
        "/api/v1/recycler/profile",
        json={
            "facility_id": str(recycler_setup["facility_id"]),
            "rates": [{"material_id": "MAT-PCB-01", "rate_paise_per_unit": 20000}]
        },
        headers=recycler_setup["headers"]
    )

    # Check transaction: agreed terms MUST remain 46000 paise (Rs 460.00)
    tx_check = client.get(f"/api/v1/transactions/{tx_id}", headers=collector_user["headers"]).json()
    assert tx_check["quoted_total_paise"] == 46000
    assert tx_check["agreed_total_paise"] == 46000
    assert tx_check["revisions"][0]["terms_hash"] == offer["terms_hash"]


def test_transaction_scoping_and_history(collector_user, other_collector_user, recycler_setup, admin_user):
    """Test transaction access scoping: participants and admin allowed; third-parties forbidden."""
    lot_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        lot = Lot(
            id=lot_id,
            collector_id=collector_user["collector_id"],
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=1000,
            status="COLLECTED",
            version=1,
            is_demo=False
        )
        session.add(lot)
        session.commit()

    req_id = client.post(
        f"/api/v1/lots/{lot_id}/requests",
        json={"facility_id": str(recycler_setup["facility_id"])},
        headers=collector_user["headers"]
    ).json()["id"]

    offer = client.post(
        f"/api/v1/requests/{req_id}/offers",
        json={"price_basis": "RATE_PER_KG", "rate_paise_per_kg": 46000},
        headers=recycler_setup["headers"]
    ).json()

    tx_id = client.post(
        f"/api/v1/offers/{offer['id']}/accept",
        json={"terms_hash": offer["terms_hash"], "expected_version": 1},
        headers=collector_user["headers"]
    ).json()["id"]

    # 1. Collector owner: 200 OK
    resp_col = client.get(f"/api/v1/transactions/{tx_id}", headers=collector_user["headers"])
    assert resp_col.status_code == 200

    # The client can safely recover this transaction from its persisted lot ID
    # after process recreation; it must not need to invent a transaction ID.
    resp_col_by_lot = client.get(f"/api/v1/lots/{lot_id}/transaction", headers=collector_user["headers"])
    assert resp_col_by_lot.status_code == 200
    assert resp_col_by_lot.json()["id"] == tx_id

    # 2. Linked recycler: 200 OK
    resp_rec = client.get(f"/api/v1/transactions/{tx_id}", headers=recycler_setup["headers"])
    assert resp_rec.status_code == 200

    # 3. Admin: 200 OK
    resp_adm = client.get(f"/api/v1/transactions/{tx_id}", headers=admin_user["headers"])
    assert resp_adm.status_code == 200

    # 4. Other collector: 403 Forbidden
    resp_other = client.get(f"/api/v1/transactions/{tx_id}", headers=other_collector_user["headers"])
    assert resp_other.status_code == 403
    assert client.get(f"/api/v1/lots/{lot_id}/transaction", headers=other_collector_user["headers"]).status_code == 403

    # 5. Recycler transactions history
    rec_txs = client.get("/api/v1/recycler/transactions", headers=recycler_setup["headers"]).json()
    assert len(rec_txs) >= 1
    assert any(t["id"] == tx_id for t in rec_txs)
