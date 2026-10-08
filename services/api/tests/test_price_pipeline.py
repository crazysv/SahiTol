"""Comprehensive tests for Attributed Price Seed and Observation Pipeline.
Covers T011 requirements: R-PRICE-01, R-DATA-02.
Acceptance cases: AT-016, AT-054.
"""
import uuid
from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_db
from app.db.models.auth import User
from app.db.models.price import PriceObservation
from app.db.seeds.materials import seed_materials
from app.db.seeds.prices import seed_price_observations
from app.security import create_access_token, UserRole
from tests.test_db import TestingSessionLocal, override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_price_database():
    """Seed test database with materials and baseline price observations."""
    app.dependency_overrides[get_db] = override_get_db
    with TestingSessionLocal() as session:
        seed_materials(session)
        seed_price_observations(session)
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_headers():
    user_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        user = User(
            id=user_id,
            phone_normalized="+919876543999",
            pin_hash="pin_admin_hash",
            role=UserRole.ADMIN.value,
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(user)
        session.commit()
    token = create_access_token(subject=str(user_id), role=UserRole.ADMIN.value, is_demo=False)
    headers = {"Authorization": f"Bearer {token}"}
    try:
        yield headers
    finally:
        with TestingSessionLocal() as session:
            session.query(User).filter(User.id == user_id).delete()
            session.commit()


def test_seed_price_observations_loads_data():
    """Verify that seed loader populates price observations and data sources."""
    with TestingSessionLocal() as session:
        obs_count = session.query(PriceObservation).count()
        assert obs_count >= 12


def test_list_price_observations_filtering(client):
    """Test identity-safe listing of verified price observations with filtering."""
    resp = client.get("/api/v1/prices/observations?material_id=MAT-PCB-01&region_id=DELHI_NCR&review_status=VERIFIED")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 3

    for item in items:
        assert item["material_id"] == "MAT-PCB-01"
        assert item["region_id"] == "DELHI_NCR"
        assert item["review_status"] == "VERIFIED"
        assert item["rate_paise_per_unit"] > 0
        assert "user_id" not in item
        assert "phone" not in item
        assert item["source_id"] in ["SRC-01", "SRC-04"]


def test_submit_price_observation_success(client):
    """Test submitting a fresh price observation enters PENDING_REVIEW."""
    now_iso = datetime.now(timezone.utc).isoformat()
    payload = {
        "material_id": "MAT-PCB-01",
        "region_id": "DELHI_NCR",
        "rate_paise_per_unit": 43500,
        "unit": "kg",
        "price_kind": "BUY",
        "condition": "INTACT",
        "observed_at": now_iso,
        "source_id": "SRC-04",
        "is_demo": False
    }
    resp = client.post("/api/v1/prices/observations", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["review_status"] == "PENDING_REVIEW"
    assert data["rate_paise_per_unit"] == 43500
    assert data["origin_class"] == "EXTERNAL_PUBLIC"


def test_submit_price_observation_future_date_rejected(client):
    """Test date integrity check: future observed date must be rejected/quarantined."""
    future_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    payload = {
        "material_id": "MAT-PCB-01",
        "region_id": "DELHI_NCR",
        "rate_paise_per_unit": 45000,
        "unit": "kg",
        "price_kind": "BUY",
        "observed_at": future_date,
        "source_id": "SRC-04",
        "is_demo": False
    }
    resp = client.post("/api/v1/prices/observations", json=payload)
    assert resp.status_code == 422
    assert "future" in resp.json()["detail"].lower()


def test_submit_price_observation_nonpositive_rate_rejected(client):
    """Test validation reject on non-positive rates."""
    now_iso = datetime.now(timezone.utc).isoformat()
    payload = {
        "material_id": "MAT-PCB-01",
        "region_id": "DELHI_NCR",
        "rate_paise_per_unit": 0,
        "unit": "kg",
        "price_kind": "BUY",
        "observed_at": now_iso,
        "source_id": "SRC-04"
    }
    resp = client.post("/api/v1/prices/observations", json=payload)
    assert resp.status_code == 422


def test_submit_price_observation_unknown_material_rejected(client):
    """Test reject when material does not exist in curated catalog."""
    now_iso = datetime.now(timezone.utc).isoformat()
    payload = {
        "material_id": "NON-EXISTENT-MAT",
        "region_id": "DELHI_NCR",
        "rate_paise_per_unit": 10000,
        "unit": "kg",
        "price_kind": "BUY",
        "observed_at": now_iso,
        "source_id": "SRC-04"
    }
    resp = client.post("/api/v1/prices/observations", json=payload)
    assert resp.status_code == 400
    assert "not found" in resp.json()["detail"].lower()


def test_submit_price_observation_invalid_price_kind_rejected(client):
    """Test reject when price_kind is invalid."""
    now_iso = datetime.now(timezone.utc).isoformat()
    payload = {
        "material_id": "MAT-PCB-01",
        "region_id": "DELHI_NCR",
        "rate_paise_per_unit": 10000,
        "unit": "kg",
        "price_kind": "INVALID_KIND",
        "observed_at": now_iso,
        "source_id": "SRC-04"
    }
    resp = client.post("/api/v1/prices/observations", json=payload)
    assert resp.status_code == 422


def test_admin_moderation_workflow(client, admin_headers):
    """Test admin review workflow: submit, review list, approve, and reject."""
    now_iso = datetime.now(timezone.utc).isoformat()
    # 1. Submit for review
    payload = {
        "material_id": "MAT-CAB-01",
        "region_id": "DELHI_NCR",
        "rate_paise_per_unit": 65000,
        "unit": "kg",
        "price_kind": "QUOTE",
        "observed_at": now_iso,
        "source_id": "SRC-04",
        "is_demo": False
    }
    resp = client.post("/api/v1/prices/observations", json=payload)
    assert resp.status_code == 201
    obs_id = resp.json()["id"]

    # 2. List pending in admin router
    resp_pending = client.get("/api/v1/admin/price-review?review_status=PENDING_REVIEW", headers=admin_headers)
    assert resp_pending.status_code == 200
    pending_ids = [p["id"] for p in resp_pending.json()]
    assert obs_id in pending_ids

    # 3. Admin APPROVE decision
    decision_resp = client.post(
        f"/api/v1/admin/price-review/{obs_id}/decision",
        json={"decision": "APPROVE", "reason": "Verified against the cited source."},
        headers=admin_headers
    )
    assert decision_resp.status_code == 200
    assert decision_resp.json()["review_status"] == "VERIFIED"

    # 4. Submit another and REJECT decision
    resp2 = client.post("/api/v1/prices/observations", json=payload)
    obs_id_2 = resp2.json()["id"]
    reject_resp = client.post(
        f"/api/v1/admin/price-review/{obs_id_2}/decision",
        json={"decision": "REJECT", "reason": "Suspicious outlier quote"},
        headers=admin_headers
    )
    assert reject_resp.status_code == 200
    assert reject_resp.json()["review_status"] == "REJECTED"
    assert reject_resp.json()["reason"] == "Suspicious outlier quote"


def test_admin_moderation_not_found(client, admin_headers):
    """Test 404 on decision for non-existent observation."""
    fake_id = str(uuid.uuid4())
    resp = client.post(
        f"/api/v1/admin/price-review/{fake_id}/decision",
        json={"decision": "APPROVE", "reason": "Verified against the cited source."},
        headers=admin_headers
    )
    assert resp.status_code == 404


def test_price_summary_weighted_quantiles(client):
    """Test summary quantile computation for PCB in Delhi-NCR."""
    resp = client.get("/api/v1/prices/summary?material_id=MAT-PCB-01&region_id=DELHI_NCR")
    assert resp.status_code == 200
    data = resp.json()
    assert data["policy_version"] == "PRICE_V1"
    assert data["material_id"] == "MAT-PCB-01"
    assert data["region_id"] == "DELHI_NCR"
    assert data["count"] >= 3
    assert data["independent_sources"] >= 2
    assert data["q1_rate"] is not None
    assert data["median_rate"] is not None
    assert data["q3_rate"] is not None
    assert data["q1_rate"] <= data["median_rate"] <= data["q3_rate"]
    # Confidence reflects the observation timestamps at test time; stale but
    # otherwise valid seeded observations must remain visible as LOW.
    assert data["confidence"] in ["HIGH", "MEDIUM", "LOW"]


def test_price_summary_empty_cohort_returns_insufficient_data(client):
    """
    CRITICAL: Empty cohorts MUST return INSUFFICIENT_DATA with null quantiles.
    Never fabricate zero or substitute synthetic values into live summaries.
    """
    resp = client.get("/api/v1/prices/summary?material_id=MAT-BAT-04&region_id=DELHI_NCR")
    assert resp.status_code == 200
    data = resp.json()
    assert data["confidence"] == "INSUFFICIENT_DATA"
    assert "NO_OBSERVATIONS_IN_WINDOW" in data["reason_codes"]
    assert data["q1_rate"] is None
    assert data["median_rate"] is None
    assert data["q3_rate"] is None
    assert data["count"] == 0


def test_price_trends_preserves_gaps(client):
    """Test trend endpoint returns dated buckets and honestly flags gaps."""
    resp = client.get("/api/v1/prices/trends?material_id=MAT-PCB-01&region_id=DELHI_NCR&days=30")
    assert resp.status_code == 200
    data = resp.json()
    assert data["material_id"] == "MAT-PCB-01"
    assert data["region_id"] == "DELHI_NCR"
    assert data["has_gaps"] is True  # 30-day window has only sparse observations
    assert len(data["data_points"]) >= 2

    # Verify order and structure
    dates = [p["bucket_date"] for p in data["data_points"]]
    assert dates == sorted(dates)
    for p in data["data_points"]:
        assert p["observation_count"] >= 1
        assert p["min_rate_paise"] <= p["median_rate_paise"] <= p["max_rate_paise"]


def test_demo_partition_isolation(client):
    """Test that demo observations do not contaminate live observation listings or summaries."""
    now_iso = datetime.now(timezone.utc).isoformat()
    # Submit demo observation
    demo_payload = {
        "material_id": "MAT-BAT-04",
        "region_id": "DELHI_NCR",
        "rate_paise_per_unit": 999999,
        "unit": "kg",
        "price_kind": "QUOTE",
        "observed_at": now_iso,
        "source_id": "SRC-04",
        "is_demo": True
    }
    resp = client.post("/api/v1/prices/observations", json=demo_payload)
    assert resp.status_code == 201

    # Query live observations (is_demo=False default)
    live_obs = client.get("/api/v1/prices/observations?material_id=MAT-BAT-04&is_demo=false").json()
    assert len(live_obs) == 0

    # Query demo observations (is_demo=True)
    demo_obs = client.get("/api/v1/prices/observations?material_id=MAT-BAT-04&review_status=PENDING_REVIEW&is_demo=true").json()
    assert len(demo_obs) >= 1
    assert demo_obs[0]["rate_paise_per_unit"] == 999999

    # Live summary remains INSUFFICIENT_DATA
    live_sum = client.get("/api/v1/prices/summary?material_id=MAT-BAT-04&is_demo=false").json()
    assert live_sum["confidence"] == "INSUFFICIENT_DATA"
    assert live_sum["median_rate"] is None


def test_estimate_valuation_endpoint(client):
    """Verify estimate valuation endpoint conforms to TECHSPEC line 65."""
    params = {
        "rate_q1": 10000,
        "rate_median": 20000,
        "rate_q3": 30000,
        "weight_g": 2500
    }
    resp = client.post("/api/v1/prices/estimate", params=params)
    assert resp.status_code == 200
    data = resp.json()
    assert data["low_paise"] == 25000
    assert data["median_paise"] == 50000
    assert data["high_paise"] == 75000


def test_daily_source_capping(client):
    """Rule 5: Cap each original source to one representative observation per cohort/day."""
    now = datetime.now(timezone.utc)
    # Insert 3 observations from the SAME source on the same day for a test material
    mat_id = "MAT-LCD-01"
    with TestingSessionLocal() as session:
        for i, rate in enumerate([15000, 16000, 17000]):
            obs = PriceObservation(
                id=uuid.uuid4(),
                material_id=mat_id,
                region_id="DELHI_NCR",
                condition="INTACT",
                rate_paise_per_unit=rate,
                unit="kg",
                price_kind="BUY",
                observed_at=now - timedelta(hours=i + 1),
                source_id="SRC-SINGLE-DAY-CAP",
                review_status="VERIFIED",
                origin_class="EXTERNAL_PUBLIC",
                source_kind="PUBLIC_MARKET_QUOTE",
                is_demo=False,
                created_at=now
            )
            session.add(obs)
        session.commit()

    resp = client.get(f"/api/v1/prices/summary?material_id={mat_id}&region_id=DELHI_NCR&force_refresh=true")
    assert resp.status_code == 200
    data = resp.json()
    # Even though 3 observations were entered for SRC-SINGLE-DAY-CAP today, source capping ensures count = 1
    assert data["independent_sources"] == 1
    assert data["count"] == 1
    assert data["median_rate"] == 15000  # latest observation kept


def test_broader_region_fallback_without_mixing_provinces(client):
    """Rule 3: Fallback from pilot subregion to broader state scope without mixing Delhi & Maharashtra."""
    # MAYAPURI has no direct observations, but broader DELHI_NCR does
    resp = client.get("/api/v1/prices/summary?material_id=MAT-PCB-01&region_id=MAYAPURI&allow_broader=true&force_refresh=true")
    assert resp.status_code == 200
    data = resp.json()
    assert data["coverage_scope"] == "BROADER_REGION"
    assert data["count"] >= 3
    assert data["confidence"] == "LOW"  # Broader region cohort is capped at LOW
    assert "BROADER_REGION_COHORT" in data["reason_codes"]


def test_valuation_snapshot_creation_and_disclaimer(client):
    """Verify POST /api/v1/prices/snapshots computes range, disclaimer, and persists."""
    payload = {
        "material_id": "MAT-PCB-01",
        "region_id": "DELHI_NCR",
        "weight_g": 2500,
        "condition": "INTACT",
        "is_demo": False
    }
    resp = client.post("/api/v1/prices/snapshots", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["material_id"] == "MAT-PCB-01"
    assert data["input_weight_g"] == 2500
    assert data["median_total_paise"] is not None
    assert data["low_total_paise"] <= data["median_total_paise"] <= data["high_total_paise"]
    assert "Indicative valuation range" in data["disclaimer"]
    assert "not a guaranteed purchase offer" in data["disclaimer"]

