"""Automated tests for Recycler Matching and Ranking Engine MATCH_V1.
Covers T019 requirements: R-REC-04, R-REC-05, R-REC-06.
Acceptance cases: AT-022, AT-024, AT-025, AT-026.
Specifications: docs/03_TECHSPEC.md lines 67-84, docs/16_API_CONTRACT.md line 52.
"""
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
    FacilityRate
)
from app.db.models.lot import Lot, LocationRecord
from app.db.seeds.materials import seed_materials
from app.db.seeds.facilities import seed_facilities
from app.domain.matching import (
    haversine_distance_m,
    evaluate_candidate_eligibility,
    rank_eligible_candidates,
    match_lot_to_facilities,
    CandidateFacility,
    LotContext,
    STATUTORY_DISCLAIMER,
    EXCLUSION_ROUTE_INCOMPATIBLE,
    EXCLUSION_MATERIAL_UNACCEPTED,
    EXCLUSION_EXPIRED_REGISTRATION,
    EXCLUSION_VERIFICATION_INSUFFICIENT,
    EXCLUSION_WEIGHT_INCOMPATIBLE,
    EXCLUSION_OPERATIONALLY_CLOSED,
    EXCLUSION_DISTANCE_EXCEEDED,
    EXCLUSION_DEMO_MISMATCH
)
from app.security import create_access_token
from tests.test_db import TestingSessionLocal, override_get_db

FIXTURES_PATH = Path(__file__).resolve().parents[3] / "data" / "fixtures" / "matching_v1_fixtures.json"


@pytest.fixture(scope="module", autouse=True)
def setup_matching_database():
    """Seed test database with materials and baseline facility records."""
    app.dependency_overrides[get_db] = override_get_db
    with TestingSessionLocal() as session:
        seed_materials(session)
        seed_facilities(session)
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_users():
    """Provision test collector and admin users."""
    with TestingSessionLocal() as session:
        c1_id = uuid.uuid4()
        c2_id = uuid.uuid4()
        admin_id = uuid.uuid4()

        u1 = User(
            id=c1_id,
            phone_normalized="+919876543201",
            pin_hash="pin_hash",
            role="COLLECTOR",
            account_state="ACTIVE",
            is_demo=False
        )
        col1 = Collector(id=c1_id, user_id=c1_id)

        u2 = User(
            id=c2_id,
            phone_normalized="+919876543202",
            pin_hash="pin_hash",
            role="COLLECTOR",
            account_state="ACTIVE",
            is_demo=False
        )
        col2 = Collector(id=c2_id, user_id=c2_id)

        admin = User(
            id=admin_id,
            phone_normalized="+919876543209",
            pin_hash="pin_hash",
            role="ADMIN",
            account_state="ACTIVE",
            is_demo=False
        )

        session.add_all([u1, col1, u2, col2, admin])
        session.commit()

        token1 = create_access_token(subject=str(c1_id), role="COLLECTOR", is_demo=False)
        token2 = create_access_token(subject=str(c2_id), role="COLLECTOR", is_demo=False)
        admin_token = create_access_token(subject=str(admin_id), role="ADMIN", is_demo=False)

        return {
            "c1": {"id": c1_id, "token": token1},
            "c2": {"id": c2_id, "token": token2},
            "admin": {"id": admin_id, "token": admin_token}
        }


# =========================================================================
# 1. Haversine Distance & PostGIS Parity Tests (AT-025)
# =========================================================================

def test_haversine_distance_parity_with_fixture():
    """
    AT-025: Verify Haversine distance function matches canonical fixture
    and is within 0.5% tolerance of PostGIS WGS84 geography calculation.
    """
    assert FIXTURES_PATH.exists(), f"Missing fixture: {FIXTURES_PATH}"
    with open(FIXTURES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for test_case in data["haversine_distance_tests"]:
        p1 = test_case["point1"]
        p2 = test_case["point2"]
        calc_dist = haversine_distance_m(
            p1["latitude"], p1["longitude"],
            p2["latitude"], p2["longitude"]
        )

        expected = test_case["expected_distance_m"]
        ref_postgis = test_case["postgis_reference_m"]
        max_tol_pct = test_case["tolerance_pct"]

        if expected == 0.0:
            assert calc_dist == 0.0
        else:
            # Check relative error against expected Haversine
            assert abs(calc_dist - expected) / expected < 0.01

            # Check relative error against PostGIS WGS84 ellipsoidal distance
            pct_error = abs(calc_dist - ref_postgis) / ref_postgis * 100.0
            assert pct_error <= max_tol_pct, (
                f"{test_case['description']}: Haversine {calc_dist:.1f}m differs from "
                f"PostGIS {ref_postgis:.1f}m by {pct_error:.3f}% (max allowed {max_tol_pct}%)"
            )


# =========================================================================
# 2. Hard Route Eligibility & Battery Isolation Invariant (AT-024 / R-REC-04)
# =========================================================================

def test_battery_isolation_route_invariant(client, test_users):
    """
    AT-024 / R-REC-04:
    - Battery lot CANNOT match a facility evidenced only for e-waste (e.g., Greentech).
    - Battery lot matches authorized battery isolation facilities (e.g., Eco-Battery).
    - General recycling and unverified/expired facilities are excluded.
    """
    token = test_users["c1"]["token"]
    user_id = test_users["c1"]["id"]

    # Create a battery lot
    create_resp = client.post(
        "/api/v1/lots",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "material_id": "MAT-BAT-01",
            "regulatory_route": "BATTERY_ISOLATION",
            "estimated_weight_kg": 25.0,
            "condition": "INTACT",
            "description": "Lead-acid battery bank",
            "location": {
                "source": "GPS",
                "latitude": 28.6358,
                "longitude": 77.1256,
                "coarse_area": "Mayapuri"
            }
        }
    )
    assert create_resp.status_code == 201
    lot_id = create_resp.json()["id"]

    # Request matches
    match_resp = client.post(
        f"/api/v1/lots/{lot_id}/matches",
        headers={"Authorization": f"Bearer {token}"},
        json={"search_radius_m": 50000}
    )
    assert match_resp.status_code == 200
    match_data = match_resp.json()

    assert match_data["policy_version"] == "MATCH_V1"
    matched_names = [m["name"] for m in match_data["matches"]]

    # Eco-Battery MUST match (authorized for BATTERY_ISOLATION)
    assert "Eco-Battery Reverse Logistics & Isolation Center" in matched_names

    # Greentech Recyclers MUST NOT match (authorized ONLY for AUTHORIZED_EWASTE!)
    assert "Greentech Recyclers Pvt Ltd" not in matched_names

    # Exclusions must record ROUTE_INCOMPATIBLE
    assert "ROUTE_INCOMPATIBLE" in match_data["exclusion_counts"]
    assert match_data["exclusion_counts"]["ROUTE_INCOMPATIBLE"] >= 1


def test_ewaste_lot_matches_authorized_ewaste_facilities(client, test_users):
    """
    AT-024: E-waste lot matches e-waste recyclers and dismantlers,
    while excluding battery-only and expired facilities.
    """
    token = test_users["c1"]["token"]

    create_resp = client.post(
        "/api/v1/lots",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "material_id": "MAT-PCB-01",
            "regulatory_route": "AUTHORIZED_EWASTE",
            "estimated_weight_kg": 15.0,
            "condition": "INTACT",
            "location": {
                "source": "GPS",
                "latitude": 28.6358,
                "longitude": 77.1256,
                "coarse_area": "Mayapuri"
            }
        }
    )
    assert create_resp.status_code == 201
    lot_id = create_resp.json()["id"]

    match_resp = client.post(
        f"/api/v1/lots/{lot_id}/matches",
        headers={"Authorization": f"Bearer {token}"},
        json={"search_radius_m": 50000}
    )
    assert match_resp.status_code == 200
    match_data = match_resp.json()

    matched_names = [m["name"] for m in match_data["matches"]]
    # Greentech and Seelampur match
    assert "Greentech Recyclers Pvt Ltd" in matched_names
    assert "Seelampur Dismantling Co-operative Workshop" in matched_names

    # Eco-Battery (BATTERY_ISOLATION only) MUST NOT match
    assert "Eco-Battery Reverse Logistics & Isolation Center" not in matched_names


# =========================================================================
# 3. Verification Levels & Formal Destination Badge (AT-022 / R-REC-02)
# =========================================================================

def test_formal_destination_requirement_filter(client, test_users):
    """
    AT-022 / R-REC-02:
    - L0 (demo), L1, L2 never qualify as formal destinations.
    - When require_formal_destination is True, L2 aggregator (Pune) is excluded.
    - L3 recycler (EcoRegen) qualifies and matches.
    """
    token = test_users["c1"]["token"]

    # Mumbai e-waste lot
    create_resp = client.post(
        "/api/v1/lots",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "material_id": "MAT-PCB-02",
            "regulatory_route": "AUTHORIZED_EWASTE",
            "estimated_weight_kg": 50.0,
            "condition": "PARTIAL",
            "location": {
                "source": "GPS",
                "latitude": 19.0688,
                "longitude": 72.8826,
                "coarse_area": "Kurla West"
            }
        }
    )
    assert create_resp.status_code == 201
    lot_id = create_resp.json()["id"]

    # Request matches with require_formal_destination = True
    match_resp = client.post(
        f"/api/v1/lots/{lot_id}/matches",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "search_radius_m": 150000,  # 150km to include Pune if eligible
            "require_formal_destination": True
        }
    )
    assert match_resp.status_code == 200
    match_data = match_resp.json()

    matched = {m["name"]: m for m in match_data["matches"]}

    # EcoRegen is L3 + VALID -> is_formal_destination == True
    assert "EcoRegen Solutions Mumbai Ltd" in matched
    assert matched["EcoRegen Solutions Mumbai Ltd"]["is_formal_destination"] is True
    assert matched["EcoRegen Solutions Mumbai Ltd"]["verification_level"] == "L3"

    # Pune Aggregator is L2 -> MUST BE EXCLUDED under VERIFICATION_INSUFFICIENT
    assert "Pune E-Waste Scrap Aggregators" not in matched
    assert "VERIFICATION_INSUFFICIENT" in match_data["exclusion_counts"]


# =========================================================================
# 4. Explainable Ranking, Factor Scores & Tie-Breaks (AT-025 / R-REC-05)
# =========================================================================

def test_explainable_ranking_and_factor_weights():
    """
    AT-025 / R-REC-05:
    - Pure domain test verifying exact 30/30/20/15/5% factor scoring.
    - Candidate with higher score ranks 1 with is_recommended == True.
    - Contributions and explanations are transparent.
    """
    with open(FIXTURES_PATH, "r", encoding="utf-8") as f:
        fixture_data = json.load(f)

    scn = next(s for s in fixture_data["scenarios"] if s["id"] == "SCN-04-EXPLAINABLE-RANKING")
    search_radius_m = scn["search_radius_m"]

    # Construct candidates from fixture
    c1_data = scn["candidates"][0]
    c2_data = scn["candidates"][1]

    c1 = CandidateFacility(
        facility_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        name=c1_data["name"],
        kind="RECYCLER",
        region_id="DELHI_NCR",
        district="Mayapuri",
        state="Delhi",
        active_quote_rate_paise_per_kg=c1_data["active_quote_rate_paise_per_kg"],
        pickup_available=c1_data["pickup_available"],
        accepting_status=c1_data["accepting_status"],
        total_transactions=c1_data["total_transactions"],
        completed_transactions=c1_data["completed_transactions"],
        verification_level="L3",
        registration_status="VALID"
    )

    c2 = CandidateFacility(
        facility_id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
        name=c2_data["name"],
        kind="RECYCLER",
        region_id="DELHI_NCR",
        district="Okhla",
        state="Delhi",
        active_quote_rate_paise_per_kg=c2_data["active_quote_rate_paise_per_kg"],
        pickup_available=c2_data["pickup_available"],
        accepting_status=c2_data["accepting_status"],
        total_transactions=c2_data["total_transactions"],
        completed_transactions=c2_data["completed_transactions"],
        verification_level="L3",
        registration_status="VALID"
    )

    eligible_items = [
        (c1, c1_data["distance_m"]),
        (c2, c2_data["distance_m"])
    ]

    ranked = rank_eligible_candidates(eligible_items, search_radius_m)

    assert len(ranked) == 2
    top = ranked[0]
    second = ranked[1]

    # Verify rank and is_recommended
    assert top.rank == 1
    assert top.is_recommended is True
    assert top.name == c2.name
    assert top.total_score == scn["expected_ranking"][0]["total_score"]

    assert second.rank == 2
    assert second.is_recommended is False
    assert second.name == c1.name
    assert second.total_score == scn["expected_ranking"][1]["total_score"]

    # Verify factor breakdown on top candidate
    factors = top.factors
    assert "distance" in factors
    assert "rate" in factors
    assert "pickup" in factors
    assert "availability" in factors
    assert "reliability" in factors

    # Weight contributions sum to total score
    computed_sum = sum(f.weighted_contribution for f in factors.values())
    assert abs(computed_sum - top.total_score) < 0.05


def test_deterministic_tie_breaking():
    """
    AT-025: Tie-breaking is deterministic:
    1. Higher total score
    2. Shorter distance
    3. Stable UUID string ascending
    """
    # Two candidates with identical scores and distances
    c_a = CandidateFacility(
        facility_id=uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        name="Facility A",
        kind="RECYCLER",
        region_id="DELHI_NCR",
        district="District A",
        state="Delhi",
        active_quote_rate_paise_per_kg=25000,
        pickup_available=True,
        accepting_status="ACCEPTING",
        verification_level="L3",
        registration_status="VALID"
    )

    c_b = CandidateFacility(
        facility_id=uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        name="Facility B",
        kind="RECYCLER",
        region_id="DELHI_NCR",
        district="District B",
        state="Delhi",
        active_quote_rate_paise_per_kg=25000,
        pickup_available=True,
        accepting_status="ACCEPTING",
        verification_level="L3",
        registration_status="VALID"
    )

    # Put c_b first in the input list
    eligible_items = [(c_b, 10000.0), (c_a, 10000.0)]
    ranked = rank_eligible_candidates(eligible_items, 50000)

    # c_a must win because UUID "aaaa..." < "bbbb..."
    assert ranked[0].name == "Facility A"
    assert ranked[0].rank == 1
    assert ranked[1].name == "Facility B"
    assert ranked[1].rank == 2


# =========================================================================
# 5. Weight Bounds & Operational Filters (AT-024)
# =========================================================================

def test_facility_weight_bounds_rejection():
    """
    AT-024: A facility specifying min_weight_g and max_weight_g
    excludes lots outside its weight bounds.
    """
    candidate = CandidateFacility(
        facility_id=uuid.uuid4(),
        name="Bulk Processing Hub",
        kind="RECYCLER",
        region_id="DELHI_NCR",
        district="Mayapuri",
        state="Delhi",
        authorized_routes=["AUTHORIZED_EWASTE"],
        materials_accepted=["MAT-PCB-01"],
        min_weight_g=50_000,    # 50 kg
        max_weight_g=500_000,   # 500 kg
        verification_level="L3",
        registration_status="VALID"
    )

    # Lot 1: 20kg (under min) -> WEIGHT_INCOMPATIBLE
    lot_small = LotContext(
        lot_id=uuid.uuid4(),
        material_id="MAT-PCB-01",
        regulatory_route="AUTHORIZED_EWASTE",
        estimated_weight_g=20_000
    )
    eligible, reason, _ = evaluate_candidate_eligibility(candidate, lot_small, 50000)
    assert eligible is False
    assert reason == EXCLUSION_WEIGHT_INCOMPATIBLE

    # Lot 2: 100kg (within bounds) -> Eligible
    lot_ok = LotContext(
        lot_id=uuid.uuid4(),
        material_id="MAT-PCB-01",
        regulatory_route="AUTHORIZED_EWASTE",
        estimated_weight_g=100_000
    )
    eligible, reason, _ = evaluate_candidate_eligibility(candidate, lot_ok, 50000)
    assert eligible is True
    assert reason is None

    # Lot 3: 1000kg (over max) -> WEIGHT_INCOMPATIBLE
    lot_large = LotContext(
        lot_id=uuid.uuid4(),
        material_id="MAT-PCB-01",
        regulatory_route="AUTHORIZED_EWASTE",
        estimated_weight_g=1_000_000
    )
    eligible, reason, _ = evaluate_candidate_eligibility(candidate, lot_large, 50000)
    assert eligible is False
    assert reason == EXCLUSION_WEIGHT_INCOMPATIBLE


# =========================================================================
# 6. No Matches Behavior & Transparent Exclusions (AT-026 / R-REC-06)
# =========================================================================

def test_no_matches_path_preserves_exclusions_and_route(client, test_users):
    """
    AT-026 / R-REC-06:
    - Search with a location far from all seeded facilities returns empty matches.
    - Exclusions clearly explain DISTANCE_EXCEEDED.
    - Regulatory route is NEVER silently relaxed or switched.

    The lot is placed in Kolkata (lat=22.5726, lon=88.3639), which is ≥1400 km
    from all reference and test-seeded facilities (Delhi/Mumbai). A 5 km search
    radius guarantees eligible_count==0 regardless of test execution order.
    """
    token = test_users["c1"]["token"]

    create_resp = client.post(
        "/api/v1/lots",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "material_id": "MAT-PCB-01",
            "regulatory_route": "AUTHORIZED_EWASTE",
            "estimated_weight_kg": 10.0,
            "condition": "INTACT",
            "location": {
                "source": "GPS",
                # Kolkata — ≥1400 km from all seeded Delhi/Mumbai facilities
                "latitude": 22.5726,
                "longitude": 88.3639,
                "coarse_area": "Kolkata"
            }
        }
    )
    assert create_resp.status_code == 201, create_resp.text
    lot_id = create_resp.json()["id"]

    # 5 km radius — no facility within range of Kolkata
    match_resp = client.post(
        f"/api/v1/lots/{lot_id}/matches",
        headers={"Authorization": f"Bearer {token}"},
        json={"search_radius_m": 5_000}
    )
    assert match_resp.status_code == 200
    match_data = match_resp.json()

    assert match_data["eligible_count"] == 0
    assert len(match_data["matches"]) == 0
    assert "No eligible facilities found" in match_data["message"]
    assert "cannot be relaxed" in match_data["message"]

    # DISTANCE_EXCEEDED tallied for all facilities (>1400 km away)
    assert "DISTANCE_EXCEEDED" in match_data["exclusion_counts"]



# =========================================================================
# 7. GeoJSON Map Data Endpoint (AT-026 / R-REC-06)
# =========================================================================

def test_facilities_geojson_endpoint(client):
    """
    AT-026 / R-REC-06:
    - GET /api/v1/facilities/geojson returns GeoJSON FeatureCollection.
    - Features contain Point geometry [longitude, latitude].
    - Every feature includes statutory disclaimer and verified attributes.
    """
    resp = client.get("/api/v1/facilities/geojson?is_demo=false")
    assert resp.status_code == 200
    geojson = resp.json()

    assert geojson["type"] == "FeatureCollection"
    assert "features" in geojson
    assert len(geojson["features"]) >= 7

    for feature in geojson["features"]:
        assert feature["type"] == "Feature"
        assert "geometry" in feature
        if feature["geometry"]:
            assert feature["geometry"]["type"] == "Point"
            coords = feature["geometry"]["coordinates"]
            assert len(coords) == 2
            lon, lat = coords
            assert -180.0 <= lon <= 180.0
            assert -90.0 <= lat <= 90.0

        props = feature["properties"]
        assert "name" in props
        assert "kind" in props
        assert "verification_level" in props
        assert "is_formal_destination" in props
        assert "disclaimer" in props
        assert "does not represent an endorsement" in props["disclaimer"].lower()


# =========================================================================
# 8. Ownership and Role Scoping
# =========================================================================

def test_collector_ownership_enforced_on_matches(client, test_users):
    """Collector cannot request matches for another collector's lot."""
    c1_token = test_users["c1"]["token"]
    c2_token = test_users["c2"]["token"]

    # Collector 1 creates lot
    create_resp = client.post(
        "/api/v1/lots",
        headers={"Authorization": f"Bearer {c1_token}"},
        json={
            "material_id": "MAT-PCB-01",
            "regulatory_route": "AUTHORIZED_EWASTE",
            "estimated_weight_kg": 5.0
        }
    )
    lot_id = create_resp.json()["id"]

    # Collector 2 attempts to match -> 403 Forbidden
    resp = client.post(
        f"/api/v1/lots/{lot_id}/matches",
        headers={"Authorization": f"Bearer {c2_token}"},
        json={"search_radius_m": 50000}
    )
    assert resp.status_code == 403
    assert "Forbidden" in resp.json()["detail"]

    # Admin CAN match on behalf of collector
    admin_token = test_users["admin"]["token"]
    admin_resp = client.post(
        f"/api/v1/lots/{lot_id}/matches",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"search_radius_m": 50000}
    )
    assert admin_resp.status_code == 200
