"""Tests for versioned reference bootstrap, delta sync APIs, and bundled offline demo cache.
Covers T009 requirements: R-OFF-01.
Acceptance cases: AT-038.
"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_db
from app.db.models.audit import SyncChange
from app.db.seeds.materials import seed_materials
from app.routers.reference import encode_cursor, decode_cursor
from tests.test_db import TestingSessionLocal, override_get_db

ROOT_DIR = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="module", autouse=True)
def setup_reference_database():
    """Seed test database with materials, categories, safety guides, and aliases."""
    app.dependency_overrides[get_db] = override_get_db
    with TestingSessionLocal() as session:
        seed_materials(session)
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_reference_bootstrap_payload_structure(client):
    """Test full reference bootstrap payload structure and required sections."""
    resp = client.get("/api/v1/reference/bootstrap?region=DELHI_NCR&language=hi&role=COLLECTOR")
    assert resp.status_code == 200
    data = resp.json()

    # Required top-level sections
    assert "metadata" in data
    assert "policy" in data
    assert "categories" in data
    assert "materials" in data
    assert "aliases" in data
    assert "safety_guides" in data
    assert "price_benchmarks" in data
    assert "facilities" in data

    # Metadata checks
    meta = data["metadata"]
    assert meta["snapshot_version"].startswith("REF-")
    assert meta["region"] == "DELHI_NCR"
    assert meta["language"] == "hi"
    assert meta["role"] == "COLLECTOR"
    assert meta["opaque_cursor"]
    assert meta["generated_at"] < meta["expires_at"]

    # Policy parameters checks
    policy = data["policy"]
    assert policy["policy_version"].startswith("POLICY_")
    assert policy["max_weight_grams"] > 0
    assert policy["price_freshness_days"] == 30
    assert policy["sync_batch_limit"] == 50
    assert "kg" in policy["allowed_units"]
    assert policy["default_currency"] == "INR"
    assert policy["cash_settlement_enabled"] is True
    assert "disclaimer" in policy


def test_reference_bootstrap_content_completeness(client):
    """Verify that bootstrap delivers all 11 categories, 21 materials, aliases, and safety guides."""
    resp = client.get("/api/v1/reference/bootstrap")
    assert resp.status_code == 200
    data = resp.json()

    assert len(data["categories"]) == 11
    assert len(data["materials"]) == 21
    assert len(data["aliases"]) >= 130
    assert len(data["safety_guides"]) >= 9
    assert len(data["price_benchmarks"]) == 21

    # Check key material categories
    cat_ids = {c["id"] for c in data["categories"]}
    for exp_cat in ["PCB", "BATTERY", "CRT", "LCD", "CABLES", "MOTORS", "PLASTICS", "METALS", "MIXED_ELECTRONICS", "OTHER", "UNKNOWN"]:
        assert exp_cat in cat_ids

    # Check that safety guides contain multilingual audio keys
    for sg in data["safety_guides"]:
        audio = sg.get("audio_keys", {})
        assert "en" in audio and "hi" in audio and "mr" in audio


def test_reference_bootstrap_regional_facility_filter(client):
    """Test regional directory filtering between Delhi-NCR and Maharashtra."""
    # Delhi-NCR
    resp_dl = client.get("/api/v1/reference/bootstrap?region=DELHI_NCR")
    assert resp_dl.status_code == 200
    facs_dl = resp_dl.json()["facilities"]
    assert len(facs_dl) >= 2
    for f in facs_dl:
        assert f["region_id"] == "DELHI_NCR"

    # Maharashtra
    resp_mh = client.get("/api/v1/reference/bootstrap?region=MAHARASHTRA")
    assert resp_mh.status_code == 200
    facs_mh = resp_mh.json()["facilities"]
    assert len(facs_mh) >= 2
    for f in facs_mh:
        assert f["region_id"] == "MAHARASHTRA"


def test_reference_changes_incremental_deltas(client):
    """Test delta sync endpoint returning entity changes and tombstones."""
    # Insert test sync changes into test DB
    entity_uuid_1 = uuid.uuid4()
    entity_uuid_2 = uuid.uuid4()
    now = datetime.now(timezone.utc)

    with TestingSessionLocal() as session:
        ch1 = SyncChange(
            sequence=101,
            entity_type="MATERIAL",
            entity_id=entity_uuid_1,
            entity_version=2,
            visibility_scope="PUBLIC",
            deleted_at=None,
            created_at=now
        )
        ch2 = SyncChange(
            sequence=102,
            entity_type="MATERIAL",
            entity_id=entity_uuid_2,
            entity_version=3,
            visibility_scope="PUBLIC",
            deleted_at=now,  # Tombstone
            created_at=now
        )
        session.add(ch1)
        session.add(ch2)
        session.commit()

    # Query with cursor for sequence 100
    cursor_100 = encode_cursor(100)
    resp = client.get(f"/api/v1/reference/changes?cursor={cursor_100}")
    assert resp.status_code == 200
    data = resp.json()

    assert data["cursor"] == cursor_100
    assert len(data["changes"]) >= 2

    # Check change 1 (UPSERT)
    c1 = next(c for c in data["changes"] if c["sequence"] == 101)
    assert c1["entity_type"] == "MATERIAL"
    assert c1["entity_id"] == str(entity_uuid_1)
    assert c1["operation"] == "UPSERT"

    # Check change 2 (DELETE tombstone)
    c2 = next(c for c in data["changes"] if c["sequence"] == 102)
    assert c2["entity_id"] == str(entity_uuid_2)
    assert c2["operation"] == "DELETE"
    assert c2["data"] is None

    # Next cursor should decode to at least 102
    next_seq = decode_cursor(data["next_cursor"])
    assert next_seq >= 102


def test_reference_changes_cursor_expired(client):
    """Test that malformed or corrupted cursor returns HTTP 410 CURSOR_EXPIRED (R-OFF-01, 17_OFFLINE_SYNC)."""
    corrupt_cursor = "not_a_valid_base64_cursor!!!"
    resp = client.get(f"/api/v1/reference/changes?cursor={corrupt_cursor}")
    assert resp.status_code == 410
    err = resp.json()["detail"]["error"]
    assert err["code"] == "CURSOR_EXPIRED"
    assert err["retryable"] is False


def test_bundled_demo_cache_asset_validity():
    """Verify bundled demo reference cache exists in Android assets and contains full offline data (AT-038)."""
    asset_path = ROOT_DIR / "apps" / "android" / "app" / "src" / "main" / "assets" / "reference_bootstrap_demo.json"
    assert asset_path.exists(), f"Missing bundled demo asset: {asset_path}"

    with open(asset_path, "r", encoding="utf-8") as f:
        bundle = json.load(f)

    # Labelled demo checks
    assert bundle["metadata"]["is_demo"] is True
    assert "disclaimer" in bundle["metadata"]
    assert bundle["metadata"]["snapshot_version"].startswith("REF-DEMO-")

    # Policy and content
    assert bundle["policy"]["max_weight_grams"] > 0
    assert len(bundle["categories"]) == 11
    assert len(bundle["materials"]) == 21
    assert len(bundle["aliases"]) >= 130
    assert len(bundle["safety_guides"]) >= 9
    assert len(bundle["price_benchmarks"]) == 21
    assert len(bundle["facilities"]) >= 2
