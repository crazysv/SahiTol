"""Automated tests for Facility Directory, Role Preservation, and Verification Levels.
Covers T012 requirements: R-REC-01, R-REC-02, R-REC-03, R-DATA-03, R-DATA-09.
Acceptance cases: AT-021, AT-022, AT-023, AT-055, AT-061.
"""
import json
import uuid
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_db
from app.db.models.facility import (
    Facility,
    FacilityAuthorization,
    FacilityMaterial,
    FacilityOperation
)
from app.db.seeds.materials import seed_materials
from app.db.seeds.facilities import seed_facilities
from scripts.data_tools.validation import DataValidator
from scripts.data_tools.deduplication import Deduplicator
from tests.test_db import TestingSessionLocal, override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_facilities_database():
    """Seed test database with materials and baseline facility records."""
    app.dependency_overrides[get_db] = override_get_db
    with TestingSessionLocal() as session:
        seed_materials(session)
        seed_facilities(session)
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_seed_facilities_loads_directory():
    """Verify that seed loader populates facilities, authorizations, materials, and operations."""
    with TestingSessionLocal() as session:
        fac_count = session.query(Facility).count()
        auth_count = session.query(FacilityAuthorization).count()
        mat_count = session.query(FacilityMaterial).count()
        op_count = session.query(FacilityOperation).count()

        assert fac_count >= 8
        assert auth_count >= 8
        assert mat_count >= 30
        assert op_count >= 8


def test_list_facilities_role_preservation_and_disclaimer(client):
    """
    AT-021 / R-REC-01:
    - Sourced from official authority lists (CPCB, DPCC, MPCB, NDMC).
    - Facility roles are preserved: RECYCLER, DISMANTLER, COLLECTION_CENTRE, AGGREGATOR.
    - Collection centres are NEVER relabeled as recyclers.
    - Statutory disclaimer is returned on every item (no partnership claim).
    """
    resp = client.get("/api/v1/facilities")
    assert resp.status_code == 200
    facilities = resp.json()
    assert len(facilities) >= 7

    roles = {f["name"]: f["kind"] for f in facilities}
    # Greentech is a Recycler
    assert roles.get("Greentech Recyclers Pvt Ltd") == "RECYCLER"
    # Eco-Battery is a Collection Centre, NOT a Recycler!
    assert roles.get("Eco-Battery Reverse Logistics & Isolation Center") == "COLLECTION_CENTRE"
    # NDMC is a Collection Centre
    assert roles.get("North Delhi Municipal E-Waste Collection Point") == "COLLECTION_CENTRE"
    # Seelampur is a Dismantler
    assert roles.get("Seelampur Dismantling Co-operative Workshop") == "DISMANTLER"
    # Pune is an Aggregator
    assert roles.get("Pune E-Waste Scrap Aggregators") == "AGGREGATOR"

    # Verify statutory disclaimer is present on all records
    for f in facilities:
        assert "disclaimer" in f
        assert "does not represent an endorsement" in f["disclaimer"].lower()
        assert "epr fulfillment certificate" in f["disclaimer"].lower()


def test_verification_levels_and_formal_destination_badge(client):
    """
    AT-022 / R-REC-02:
    - L3/L4 with active valid registration qualifies as formal destination.
    - L0 (demo), L2 (list matches), and EXPIRED registrations NEVER qualify as formal destinations.
    """
    resp = client.get("/api/v1/facilities?is_demo=false")
    assert resp.status_code == 200
    facilities = {f["name"]: f for f in resp.json()}

    # Greentech: L3 + VALID -> is_formal_destination == True
    greentech = facilities["Greentech Recyclers Pvt Ltd"]
    assert greentech["verification_level"] == "L3"
    assert greentech["registration_status"] == "VALID"
    assert greentech["is_formal_destination"] is True

    # Pune Aggregators: L2 + VALID -> is_formal_destination == False (L2 cannot be formal destination)
    pune = facilities["Pune E-Waste Scrap Aggregators"]
    assert pune["verification_level"] == "L2"
    assert pune["is_formal_destination"] is False

    # NDMC Collection Centre: L2 + EXPIRED -> is_formal_destination == False
    ndmc = facilities["North Delhi Municipal E-Waste Collection Point"]
    assert ndmc["registration_status"] == "EXPIRED"
    assert ndmc["is_formal_destination"] is False


def test_formal_destination_filter(client):
    """Test filtering strictly for verified formal destinations."""
    resp = client.get("/api/v1/facilities?formal_destination_only=true")
    assert resp.status_code == 200
    facilities = resp.json()
    assert len(facilities) >= 4

    for f in facilities:
        assert f["is_formal_destination"] is True
        assert f["verification_level"] in ["L3", "L4"]
        assert f["registration_status"] == "VALID"
        assert "EXPIRED" not in f["registration_status"]


def test_regional_filtering(client):
    """Verify regional cohorts strictly partition Delhi-NCR and Maharashtra."""
    dl_resp = client.get("/api/v1/facilities?region_id=DELHI_NCR")
    assert dl_resp.status_code == 200
    dl_facs = dl_resp.json()
    for f in dl_facs:
        assert f["region_id"] == "DELHI_NCR"

    mh_resp = client.get("/api/v1/facilities?region_id=MAHARASHTRA")
    assert mh_resp.status_code == 200
    mh_facs = mh_resp.json()
    for f in mh_facs:
        assert f["region_id"] == "MAHARASHTRA"


def test_material_and_route_filtering(client):
    """Verify filtering by accepted material and regulatory route."""
    # Filter by lead-acid battery
    bat_resp = client.get("/api/v1/facilities?material_id=MAT-BAT-01")
    assert bat_resp.status_code == 200
    bat_facs = bat_resp.json()
    names = [f["name"] for f in bat_facs]
    assert "Eco-Battery Reverse Logistics & Isolation Center" in names
    assert "Maharashtra Lead & Battery Processors" in names
    assert "Greentech Recyclers Pvt Ltd" not in names  # Greentech does not accept batteries

    # Filter by BATTERY_ISOLATION route
    route_resp = client.get("/api/v1/facilities?route=BATTERY_ISOLATION")
    assert route_resp.status_code == 200
    for f in route_resp.json():
        assert "BATTERY_ISOLATION" in f["authorized_routes"]


def test_unknown_pickup_and_rates_preserved_as_unknown(client):
    """
    R-REC-03 / AT-023:
    - Unknown pickup availability is preserved as null (never fabricated true/false).
    - Documented pickup availability is faithfully reflected.
    """
    resp = client.get("/api/v1/facilities")
    assert resp.status_code == 200
    facs = {f["name"]: f for f in resp.json()}

    # Greentech has unknown pickup
    assert facs["Greentech Recyclers Pvt Ltd"]["pickup_available"] is None

    # Eco-Battery is drop-off only
    assert facs["Eco-Battery Reverse Logistics & Isolation Center"]["pickup_available"] is False

    # Seelampur offers pickup
    assert facs["Seelampur Dismantling Co-operative Workshop"]["pickup_available"] is True


def test_facility_detail_endpoint(client):
    """Verify detailed facility endpoint returning authorizations, materials, and operations."""
    facs = client.get("/api/v1/facilities").json()
    target = next((f for f in facs if len(client.get(f"/api/v1/facilities/{f['id']}").json().get("authorizations", [])) >= 1), facs[0])
    target_id = target["id"]

    resp = client.get(f"/api/v1/facilities/{target_id}")
    assert resp.status_code == 200
    detail = resp.json()
    assert detail["id"] == target_id
    assert len(detail["authorizations"]) >= 1
    assert len(detail["materials"]) >= 1
    assert "disclaimer" in detail


def test_facility_detail_not_found(client):
    """Verify 404 for nonexistent facility ID."""
    fake_id = str(uuid.uuid4())
    resp = client.get(f"/api/v1/facilities/{fake_id}")
    assert resp.status_code == 404


def test_update_facility_operations_does_not_mutate_authorizations(client):
    """
    R-REC-03 / AT-023:
    Facility user can update operational parameters (pickup, service area, status)
    while regulatory authorization fields remain strictly admin-controlled.
    """
    facs = client.get("/api/v1/facilities").json()
    target = next((f for f in facs if len(client.get(f"/api/v1/facilities/{f['id']}").json().get("authorizations", [])) >= 1), facs[0])
    target_id = target["id"]
    orig_detail = client.get(f"/api/v1/facilities/{target_id}").json()
    orig_auth = orig_detail["authorizations"][0]

    # Perform operational update
    update_payload = {
        "pickup_available": True,
        "service_area": "Updated Greater Delhi-NCR Region",
        "accepting_status": "ACCEPTING"
    }
    put_resp = client.put(f"/api/v1/facilities/{target_id}/operations", json=update_payload)
    assert put_resp.status_code == 200
    assert put_resp.json()["pickup_available"] is True
    assert put_resp.json()["service_area"] == "Updated Greater Delhi-NCR Region"
    assert put_resp.json()["authorization_tampered"] is False

    # Verify authorizations are untouched
    after_detail = client.get(f"/api/v1/facilities/{target_id}").json()
    after_auth = after_detail["authorizations"][0]
    assert after_auth["verification_level"] == orig_auth["verification_level"]
    assert after_auth["reference"] == orig_auth["reference"]
    assert after_auth["authority"] == orig_auth["authority"]
    assert after_auth["status"] == orig_auth["status"]


def test_post_facility_quote_rate(client):
    """Test facility quote rate entry with provenance."""
    facs = client.get("/api/v1/facilities").json()
    target_id = facs[0]["id"]

    payload = {
        "material_id": "MAT-PCB-01",
        "rate_paise_per_unit": 45000,
        "unit": "kg",
        "condition": "INTACT",
        "price_kind": "QUOTE",
        "source_id": "SRC-05"
    }
    resp = client.post(f"/api/v1/facilities/{target_id}/rates", json=payload)
    assert resp.status_code == 201
    assert resp.json()["rate_paise_per_unit"] == 45000
    assert resp.json()["review_status"] == "PENDING_REVIEW"


def test_recyclers_directory_backward_compatibility(client):
    """Test that /api/v1/recyclers/directory delegates correctly to the facility service."""
    resp = client.get("/api/v1/recyclers/directory?region_id=DELHI_NCR")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 3
    for f in data:
        assert f["region_id"] == "DELHI_NCR"


def test_reference_bootstrap_integration(client):
    """Verify that reference bootstrap reflects seeded facilities dynamically."""
    resp = client.get("/api/v1/reference/bootstrap?region=DELHI_NCR")
    assert resp.status_code == 200
    data = resp.json()
    assert "facilities" in data
    assert len(data["facilities"]) >= 3
    for f in data["facilities"]:
        assert f["region_id"] == "DELHI_NCR"


def test_demo_partition_isolation(client):
    """Test that simulated L0 demo facilities do not contaminate production listings."""
    prod_facs = client.get("/api/v1/facilities?is_demo=false").json()
    prod_names = [f["name"] for f in prod_facs]
    assert "Simulated Demonstration Recycling Hub" not in prod_names

    demo_facs = client.get("/api/v1/facilities?is_demo=true").json()
    demo_names = [f["name"] for f in demo_facs]
    assert "Simulated Demonstration Recycling Hub" in demo_names


def test_data_validation_and_deduplication():
    """
    AT-055 / AT-061:
    - Run DataValidator on facility seed records.
    - Run Deduplicator to verify detection of duplicate registration references.
    """
    with open("data/seeds/facilities.json", "r", encoding="utf-8") as f:
        records = json.load(f)

    # 1. Validation
    validator = DataValidator()
    val_res = validator.validate_recyclers(records)
    assert val_res.valid_count == len(records)
    assert val_res.quarantined_count == 0

    # 2. Deduplication on clean dataset
    deduplicator = Deduplicator()
    unique, rep = deduplicator.deduplicate_facilities(records)
    assert rep.total_records == len(records)
    assert rep.unique_records_count == len(records)
    assert rep.duplicate_clusters_count == 0

    # 3. Inject duplicate registration reference
    dup_records = records + [
        {
            "facility_id": "fac-dup-01",
            "name": "Greentech Copycat",
            "facility_type": "RECYCLER",
            "region_id": "DELHI_NCR",
            "registration_reference": "DPCC/EW/REC-2023/042",  # Duplicate of fac-dl-01
            "public_address": "Some other address",
            "route": "AUTHORIZED_EWASTE",
            "registration_status": "VALID",
            "is_demo": False,
            "origin_class": "OFFICIAL",
            "source_kind": "REGULATOR_LIST"
        }
    ]
    _, dup_rep = deduplicator.deduplicate_facilities(dup_records)
    assert dup_rep.duplicate_clusters_count == 1
    assert dup_rep.clusters[0].cluster_key == "DPCC/EW/REC-2023/042"
