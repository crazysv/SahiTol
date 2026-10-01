"""Comprehensive test suite for Material Lots and Lifecycle Backend (T016).
Covers requirements: R-LOT-03, R-LOT-04, R-LOT-05, R-DATA-01.
Acceptance cases: AT-013, AT-014, AT-015, AT-053.
"""
import uuid
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_db
from app.db.models.auth import User
from app.db.models.lot import Lot, LocationRecord, LotImage, MediaObject, ValuationSnapshot
from app.db.models.audit import DomainEvent, QualityFlag, SyncChange
from app.db.models.price import PriceSummary
from app.db.seeds.materials import seed_materials
from app.security import create_access_token
from tests.test_db import TestingSessionLocal, override_get_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_lots_test_database():
    """Seed test database with materials and baseline price summary."""
    app.dependency_overrides[get_db] = override_get_db
    with TestingSessionLocal() as session:
        seed_materials(session)

        # Seed benchmark price summary for MAT-PCB-01
        summary = PriceSummary(
            id=uuid.uuid4(),
            cohort_key="MAT-PCB-01:DELHI_NCR:INTACT",
            policy_version="PRICE_V1",
            computed_at=datetime.now(timezone.utc),
            source_cutoff_at=datetime.now(timezone.utc),
            q1_rate=42000,
            median_rate=45000,
            q3_rate=48000,
            count=10,
            independent_sources=3,
            confidence="HIGH",
            reason_codes=["BENCHMARK_OK"],
            observation_ids=[],
            input_hash="test_hash"
        )
        session.add(summary)
        session.commit()
    yield


@pytest.fixture
def collector_a():
    """Create test collector A."""
    user_id = uuid.uuid4()
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
        session.commit()

    token = create_access_token(subject=str(user_id), role="COLLECTOR", is_demo=False)
    return {"id": user_id, "headers": {"Authorization": f"Bearer {token}"}}


@pytest.fixture
def collector_b():
    """Create test collector B."""
    user_id = uuid.uuid4()
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
        session.commit()

    token = create_access_token(subject=str(user_id), role="COLLECTOR", is_demo=False)
    return {"id": user_id, "headers": {"Authorization": f"Bearer {token}"}}


@pytest.fixture
def admin_user():
    """Create test admin."""
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
    return {"id": user_id, "headers": {"Authorization": f"Bearer {token}"}}


# --- Test Cases ---

def test_create_lot_draft_and_domain_effects(collector_a):
    """Test standard lot draft creation, domain event emission, and sync change."""
    lot_id = uuid.uuid4()
    body = {
        "id": str(lot_id),
        "material_id": "MAT-PCB-01",
        "estimated_weight_g": 3500,
        "condition": "INTACT",
        "description": "Motherboard lot"
    }

    resp = client.post("/api/v1/lots", json=body, headers=collector_a["headers"])
    assert resp.status_code == 201
    data = resp.json()

    assert data["id"] == str(lot_id)
    assert data["collector_id"] == str(collector_a["id"])
    assert data["status"] == "DRAFT"
    assert data["version"] == 1
    assert data["regulatory_route"] == "AUTHORIZED_EWASTE"
    assert data["estimated_weight_g"] == 3500

    # Verify DomainEvent emission
    with TestingSessionLocal() as session:
        ev = session.execute(
            DomainEvent.__table__.select().where(DomainEvent.aggregate_id == lot_id)
        ).first()
        assert ev is not None
        assert ev.event_type == "LOT_CREATED"
        assert ev.next_state == "DRAFT"
        assert ev.actor_id == collector_a["id"]

        ch = session.execute(
            SyncChange.__table__.select().where(SyncChange.entity_id == lot_id)
        ).first()
        assert ch is not None
        assert ch.entity_type == "LOT"
        assert ch.entity_version == 1


def test_weight_validation_and_fractional_kg_round_trip(collector_a):
    """AT-013: Weight validation (positive, finite, max bound, and fractional kg round-trip)."""
    # 1. Negative weight rejected
    resp1 = client.post("/api/v1/lots", json={
        "material_id": "MAT-PCB-01",
        "estimated_weight_g": -500
    }, headers=collector_a["headers"])
    assert resp1.status_code == 422

    # 2. Zero weight rejected
    resp2 = client.post("/api/v1/lots", json={
        "material_id": "MAT-PCB-01",
        "estimated_weight_g": 0
    }, headers=collector_a["headers"])
    assert resp2.status_code == 422

    # 3. Overflow weight (>50MT) rejected
    resp3 = client.post("/api/v1/lots", json={
        "material_id": "MAT-PCB-01",
        "estimated_weight_g": 60_000_000
    }, headers=collector_a["headers"])
    assert resp3.status_code == 422

    # 4. Fractional kg input round-trips to exact grams
    resp4 = client.post("/api/v1/lots", json={
        "material_id": "MAT-PCB-01",
        "estimated_weight_kg": 4.85
    }, headers=collector_a["headers"])
    assert resp4.status_code == 201
    assert resp4.json()["estimated_weight_g"] == 4850


def test_suspicious_large_weight_quality_flag_without_cap(collector_a):
    """AT-013: Suspicious large weight (>500kg) creates a QualityFlag for review without artificial rejection."""
    resp = client.post("/api/v1/lots", json={
        "material_id": "MAT-BAT-01",
        "estimated_weight_g": 850_000,  # 850 kg
        "condition": "INTACT"
    }, headers=collector_a["headers"])
    assert resp.status_code == 201
    lot_id = uuid.UUID(resp.json()["id"])

    # Verify lot is created and QualityFlag is logged
    with TestingSessionLocal() as session:
        flag = session.execute(
            QualityFlag.__table__.select().where(QualityFlag.entity_id == lot_id)
        ).first()
        assert flag is not None
        assert flag.rule_id == "DQ-LARGE-WEIGHT"
        assert flag.severity == "MEDIUM"
        assert flag.status == "OPEN"


def test_duplicate_media_uses_sha256_across_distinct_uploads(collector_a):
    """QUALITY_V1 detects identical image content even when upload IDs differ."""
    shared_sha256 = "a" * 64
    first_media_id = uuid.uuid4()
    second_media_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        first_media = MediaObject(
            id=first_media_id, owner_user_id=collector_a["id"], storage_key="test/first.jpg",
            mime_type="image/jpeg", byte_size=123, sha256=shared_sha256, upload_state="VALIDATED",
        )
        second_media = MediaObject(
            id=second_media_id, owner_user_id=collector_a["id"], storage_key="test/second.jpg",
            mime_type="image/jpeg", byte_size=123, sha256=shared_sha256, upload_state="VALIDATED",
        )
        session.add_all([first_media, second_media])
        session.commit()

    first = client.post("/api/v1/lots", json={
        "material_id": "MAT-PCB-01", "estimated_weight_g": 1000, "media_ids": [str(first_media_id)],
    }, headers=collector_a["headers"])
    assert first.status_code == 201
    second = client.post("/api/v1/lots", json={
        "material_id": "MAT-PCB-01", "estimated_weight_g": 1000, "media_ids": [str(second_media_id)],
    }, headers=collector_a["headers"])
    assert second.status_code == 201

    with TestingSessionLocal() as session:
        flag = session.execute(
            QualityFlag.__table__.select().where(
                QualityFlag.entity_id == uuid.UUID(second.json()["id"]),
                QualityFlag.rule_id == "DQ-DUPLICATE-MEDIA",
            )
        ).first()
        assert flag is not None
        assert flag.evidence_json["media_sha256"] == shared_sha256
        assert str(first.json()["id"]) in flag.evidence_json["other_lot_ids"]


def test_location_provenance_gps_and_manual_coarse(collector_a):
    """AT-014: Location provenance handles permitted GPS vs coarse manual without fabricating coordinates."""
    # 1. Permitted GPS with valid India coordinates
    resp1 = client.post("/api/v1/lots", json={
        "material_id": "MAT-PCB-01",
        "estimated_weight_g": 1000,
        "location": {
            "source": "GPS",
            "latitude": 28.6672,
            "longitude": 77.2778,
            "accuracy_m": 12.5,
            "age_ms": 1500
        }
    }, headers=collector_a["headers"])
    assert resp1.status_code == 201
    lot1_id = uuid.UUID(resp1.json()["id"])

    # 2. Denied GPS with coarse manual locality
    resp2 = client.post("/api/v1/lots", json={
        "material_id": "MAT-PCB-01",
        "estimated_weight_g": 1000,
        "location": {
            "source": "MANUAL",
            "coarse_area": "Seelampur, Delhi"
        }
    }, headers=collector_a["headers"])
    assert resp2.status_code == 201
    lot2_id = uuid.UUID(resp2.json()["id"])

    # 3. Invalid out-of-bounds GPS rejected
    resp3 = client.post("/api/v1/lots", json={
        "material_id": "MAT-PCB-01",
        "estimated_weight_g": 1000,
        "location": {
            "source": "GPS",
            "latitude": 51.5074,  # London
            "longitude": -0.1278
        }
    }, headers=collector_a["headers"])
    assert resp3.status_code == 422

    # Verify stored records
    with TestingSessionLocal() as session:
        loc1 = session.execute(LocationRecord.__table__.select().where(LocationRecord.owner_entity_id == lot1_id)).first()
        loc2 = session.execute(LocationRecord.__table__.select().where(LocationRecord.owner_entity_id == lot2_id)).first()

        assert loc1.source == "GPS"
        assert loc1.accuracy_m == 12.5

        assert loc2.source == "MANUAL"
        assert loc2.coarse_area == "Seelampur, Delhi"
        assert loc2.point is None, "Manual location must never fabricate coordinates"


def test_lot_get_detail_projection_redacts_private_coords(collector_a):
    """AT-014: GET /lots/{id} returns coarse location quality without leaking raw coordinate blobs."""
    resp_create = client.post("/api/v1/lots", json={
        "material_id": "MAT-PCB-01",
        "estimated_weight_g": 2000,
        "location": {
            "source": "GPS",
            "latitude": 28.6672,
            "longitude": 77.2778,
            "accuracy_m": 8.0,
            "coarse_area": "East Delhi Area"
        }
    }, headers=collector_a["headers"])
    lot_id = resp_create.json()["id"]

    resp = client.get(f"/api/v1/lots/{lot_id}", headers=collector_a["headers"])
    assert resp.status_code == 200
    data = resp.json()

    assert data["id"] == lot_id
    assert "location" in data
    loc = data["location"]
    assert loc["source"] == "GPS"
    assert loc["accuracy_m"] == 8.0
    assert loc["coarse_area"] == "East Delhi Area"
    # Ensure exact lat/lon are not exposed in standard public projection
    assert "latitude" not in loc
    assert "longitude" not in loc


def test_arbitrary_status_patch_prohibited(collector_a):
    """AT-015: Direct status PATCH is strictly prohibited."""
    resp_create = client.post("/api/v1/lots", json={
        "material_id": "MAT-PCB-01",
        "estimated_weight_g": 2000
    }, headers=collector_a["headers"])
    lot_id = resp_create.json()["id"]

    # Attempt to bypass lifecycle via PATCH status
    resp = client.patch(f"/api/v1/lots/{lot_id}", json={
        "status": "COLLECTED",
        "expected_version": 1
    }, headers=collector_a["headers"])

    assert resp.status_code == 422
    err = resp.json()["detail"]["error"]
    assert err["code"] == "ARBITRARY_STATUS_MUTATION_PROHIBITED"


def test_update_draft_fields_and_version_increment(collector_a):
    """Test valid draft editing with optimistic version increment."""
    resp_create = client.post("/api/v1/lots", json={
        "material_id": "MAT-PCB-01",
        "estimated_weight_g": 2000,
        "condition": "INTACT"
    }, headers=collector_a["headers"])
    lot_id = resp_create.json()["id"]

    # Update description and weight with expected_version = 1
    resp_update = client.patch(f"/api/v1/lots/{lot_id}", json={
        "expected_version": 1,
        "estimated_weight_g": 2500,
        "description": "Updated description"
    }, headers=collector_a["headers"])

    assert resp_update.status_code == 200
    updated = resp_update.json()
    assert updated["version"] == 2
    assert updated["estimated_weight_g"] == 2500
    assert updated["description"] == "Updated description"


def test_update_draft_version_conflict(collector_a):
    """AT-015: Stale expected_version on draft edit returns 409 VERSION_CONFLICT."""
    resp_create = client.post("/api/v1/lots", json={
        "material_id": "MAT-PCB-01",
        "estimated_weight_g": 2000
    }, headers=collector_a["headers"])
    lot_id = resp_create.json()["id"]

    # Send stale version 99
    resp = client.patch(f"/api/v1/lots/{lot_id}", json={
        "expected_version": 99,
        "estimated_weight_g": 3000
    }, headers=collector_a["headers"])

    assert resp.status_code == 409
    err = resp.json()["detail"]["error"]
    assert err["code"] == "VERSION_CONFLICT"
    assert err["details"]["current_version"] == 1


def test_lifecycle_transition_draft_to_collected_and_listed(collector_a):
    """AT-015: Legal transition flow DRAFT -> COLLECTED -> LISTED."""
    resp_create = client.post("/api/v1/lots", json={
        "material_id": "MAT-PCB-01",
        "estimated_weight_g": 3000,
        "condition": "INTACT"
    }, headers=collector_a["headers"])
    lot_id = resp_create.json()["id"]

    # 1. Finalize collection: DRAFT -> COLLECTED
    resp_collect = client.post(f"/api/v1/lots/{lot_id}/collect", json={
        "expected_version": 1
    }, headers=collector_a["headers"])
    assert resp_collect.status_code == 200
    data_collect = resp_collect.json()
    assert data_collect["status"] == "COLLECTED"
    assert data_collect["version"] == 2

    # 2. List lot: COLLECTED -> LISTED
    resp_list = client.post(f"/api/v1/lots/{lot_id}/list", json={
        "expected_version": 2
    }, headers=collector_a["headers"])
    assert resp_list.status_code == 200
    data_list = resp_list.json()
    assert data_list["status"] == "LISTED"
    assert data_list["version"] == 3

    # Verify event audit trail
    with TestingSessionLocal() as session:
        events = session.execute(
            DomainEvent.__table__.select().where(DomainEvent.aggregate_id == uuid.UUID(lot_id)).order_by(DomainEvent.sequence)
        ).all()
        assert len(events) == 3
        assert events[0].event_type == "LOT_CREATED"
        assert events[1].event_type == "LOT_COLLECTED"
        assert events[2].event_type == "LOT_LISTED"


def test_collection_requires_material_and_weight(collector_a):
    """AT-013: Finalizing collection fails if material or weight are missing."""
    # Lot without material
    resp_no_mat = client.post("/api/v1/lots", json={
        "estimated_weight_g": 1000
    }, headers=collector_a["headers"])
    lot1_id = resp_no_mat.json()["id"]

    resp1 = client.post(f"/api/v1/lots/{lot1_id}/collect", json={"expected_version": 1}, headers=collector_a["headers"])
    assert resp1.status_code == 422
    assert resp1.json()["detail"]["error"]["code"] == "MATERIAL_REQUIRED"

    # Lot without weight
    resp_no_wt = client.post("/api/v1/lots", json={
        "material_id": "MAT-PCB-01"
    }, headers=collector_a["headers"])
    lot2_id = resp_no_wt.json()["id"]

    resp2 = client.post(f"/api/v1/lots/{lot2_id}/collect", json={"expected_version": 1}, headers=collector_a["headers"])
    assert resp2.status_code == 422
    assert resp2.json()["detail"]["error"]["code"] == "WEIGHT_REQUIRED"


def test_illegal_transitions_prevented(collector_a):
    """AT-015: Attempts to jump DRAFT->LISTED or CANCELLED->LISTED are rejected with 409."""
    # 1. Draft trying to jump directly to LISTED
    resp_draft = client.post("/api/v1/lots", json={
        "material_id": "MAT-PCB-01",
        "estimated_weight_g": 2000
    }, headers=collector_a["headers"])
    draft_id = resp_draft.json()["id"]

    resp_jump = client.post(f"/api/v1/lots/{draft_id}/list", json={"expected_version": 1}, headers=collector_a["headers"])
    assert resp_jump.status_code == 409
    assert resp_jump.json()["detail"]["error"]["code"] == "INVALID_TRANSITION"

    # 2. Cancelled lot trying to list
    client.post(f"/api/v1/lots/{draft_id}/cancel", json={"expected_version": 1, "reason": "No longer needed"}, headers=collector_a["headers"])
    resp_cancel_list = client.post(f"/api/v1/lots/{draft_id}/list", json={"expected_version": 2}, headers=collector_a["headers"])
    assert resp_cancel_list.status_code == 409
    assert resp_cancel_list.json()["detail"]["error"]["code"] == "INVALID_TRANSITION"


def test_cancel_lot_with_reason_and_tombstone(collector_a):
    """AT-015: Cancelling a lot logs reason and emits a tombstone sync change."""
    resp_create = client.post("/api/v1/lots", json={
        "material_id": "MAT-PCB-01",
        "estimated_weight_g": 1000
    }, headers=collector_a["headers"])
    lot_id = resp_create.json()["id"]

    resp_cancel = client.post(f"/api/v1/lots/{lot_id}/cancel", json={
        "expected_version": 1,
        "reason": "Customer cancelled scrap pickup"
    }, headers=collector_a["headers"])
    assert resp_cancel.status_code == 200
    assert resp_cancel.json()["status"] == "CANCELLED"

    with TestingSessionLocal() as session:
        ch = session.execute(
            SyncChange.__table__.select().where(
                SyncChange.entity_id == uuid.UUID(lot_id),
                SyncChange.deleted_at.isnot(None)
            )
        ).first()
        assert ch is not None, "Cancelled lot must emit a tombstone sync change"


def test_owner_isolation_and_scoping(collector_a, collector_b, admin_user):
    """Security check: Collector B cannot access or update Collector A's lot."""
    resp = client.post("/api/v1/lots", json={
        "material_id": "MAT-PCB-01",
        "estimated_weight_g": 1000
    }, headers=collector_a["headers"])
    lot_id = resp.json()["id"]

    # Collector B cannot read
    resp_read = client.get(f"/api/v1/lots/{lot_id}", headers=collector_b["headers"])
    assert resp_read.status_code == 403

    # Collector B cannot edit
    resp_edit = client.patch(f"/api/v1/lots/{lot_id}", json={
        "expected_version": 1,
        "estimated_weight_g": 1200
    }, headers=collector_b["headers"])
    assert resp_edit.status_code == 403

    # Admin CAN read
    resp_admin = client.get(f"/api/v1/lots/{lot_id}", headers=admin_user["headers"])
    assert resp_admin.status_code == 200


def test_estimate_lot_valuation(collector_a):
    """Test lot valuation estimation based on weight and benchmark price summaries."""
    resp_create = client.post("/api/v1/lots", json={
        "material_id": "MAT-PCB-01",
        "estimated_weight_g": 2000,
        "condition": "INTACT"
    }, headers=collector_a["headers"])
    lot_id = resp_create.json()["id"]

    resp_est = client.post(f"/api/v1/lots/{lot_id}/estimate", headers=collector_a["headers"])
    assert resp_est.status_code == 200
    est = resp_est.json()

    assert est["lot_id"] == lot_id
    assert est["policy_version"] == "PRICE_V1"
    assert est["currency"] == "INR"
    assert est["input_weight_g"] == 2000
    # Benchmark: Q1=42000 paise/kg, Median=45000 paise/kg, Q3=48000 paise/kg
    # For 2.0 kg:
    # low = 42000 * 2 = 84000 paise
    # med = 45000 * 2 = 90000 paise
    # high = 48000 * 2 = 96000 paise
    assert est["low_total_paise"] == 84000
    assert est["median_total_paise"] == 90000
    assert est["high_total_paise"] == 96000
    assert est["confidence"] == "HIGH"

    # Verify ValuationSnapshot in DB
    with TestingSessionLocal() as session:
        snap = session.execute(
            ValuationSnapshot.__table__.select().where(ValuationSnapshot.lot_id == uuid.UUID(lot_id))
        ).first()
        assert snap is not None
        assert snap.median_total_paise == 90000
