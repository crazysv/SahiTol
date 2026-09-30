"""Comprehensive tests for Durable Offline Synchronization Protocol (T014).
Covers requirements: R-OFF-03, R-OFF-04.
Acceptance cases: AT-040, AT-041.
"""
import uuid
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_db
from app.db.models.auth import User
from app.db.models.lot import Lot
from app.db.models.audit import SyncOperation, SyncChange
from app.db.models.price import PriceObservation
from app.db.seeds.materials import seed_materials
from app.domain.canonical import compute_canonical_hash
from app.routers.sync import encode_cursor, decode_cursor
from app.security import create_access_token
from tests.test_db import TestingSessionLocal, override_get_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_sync_test_database():
    """Seed test database with materials for sync tests."""
    app.dependency_overrides[get_db] = override_get_db
    with TestingSessionLocal() as session:
        seed_materials(session)
    yield


@pytest.fixture
def collector_user():
    """Create and return a test collector user with bearer auth headers."""
    user_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        user = User(
            id=user_id,
            phone_normalized="+919876543210",
            pin_hash="test_pin_hash",
            role="COLLECTOR",
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(user)
        session.commit()

    token = create_access_token(subject=str(user_id), role="COLLECTOR", is_demo=False)
    headers = {"Authorization": f"Bearer {token}"}
    return {"id": user_id, "headers": headers}


@pytest.fixture
def other_collector_user():
    """Create a second collector user for permission/replay isolation tests."""
    user_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        user = User(
            id=user_id,
            phone_normalized="+919876543211",
            pin_hash="test_pin_hash",
            role="COLLECTOR",
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(user)
        session.commit()

    token = create_access_token(subject=str(user_id), role="COLLECTOR", is_demo=False)
    headers = {"Authorization": f"Bearer {token}"}
    return {"id": user_id, "headers": headers}


@pytest.fixture
def admin_user():
    """Create and return an admin user with bearer auth headers."""
    user_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        user = User(
            id=user_id,
            phone_normalized="+919876543299",
            pin_hash="test_pin_hash",
            role="ADMIN",
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(user)
        session.commit()

    token = create_access_token(subject=str(user_id), role="ADMIN", is_demo=False)
    headers = {"Authorization": f"Bearer {token}"}
    return {"id": user_id, "headers": headers}


# --- Test Cases ---

def test_sync_batch_push_success_and_domain_effects(collector_user):
    """Test standard single operation push resulting in APPLIED and DB domain mutations."""
    op_id = uuid.uuid4()
    lot_id = uuid.uuid4()
    payload = {
        "material_id": "MAT-PCB-01",
        "estimated_weight_g": 3500,
        "condition": "INTACT",
        "description": "Desktop motherboard lot"
    }

    req_body = {
        "device_id": "phone-redmi-01",
        "operations": [
            {
                "operation_id": str(op_id),
                "entity_type": "LOT",
                "entity_id": str(lot_id),
                "command": "CREATE_DRAFT",
                "expected_version": None,
                "payload": payload
            }
        ]
    }

    resp = client.post("/api/v1/sync/batch", json=req_body, headers=collector_user["headers"])
    assert resp.status_code == 200
    data = resp.json()

    assert "data" in data
    assert "meta" in data
    results = data["data"]["results"]
    assert len(results) == 1

    r0 = results[0]
    assert r0["operation_id"] == str(op_id)
    assert r0["outcome"] == "APPLIED"
    assert r0["entity_id"] == str(lot_id)
    assert r0["server_version"] == 1
    assert r0["result"]["status"] == "DRAFT"
    assert r0["result"]["estimated_weight_g"] == 3500
    assert r0["error"] is None

    # Verify database persistence
    with TestingSessionLocal() as session:
        lot = session.execute(Lot.__table__.select().where(Lot.id == lot_id)).first()
        assert lot is not None
        assert lot.status == "DRAFT"
        assert lot.estimated_weight_g == 3500

        sync_op = session.execute(SyncOperation.__table__.select().where(SyncOperation.operation_id == op_id)).first()
        assert sync_op is not None
        assert sync_op.state == "COMMITTED"
        assert sync_op.actor_id == collector_user["id"]

        sync_ch = session.execute(SyncChange.__table__.select().where(SyncChange.entity_id == lot_id)).first()
        assert sync_ch is not None
        assert sync_ch.entity_type == "LOT"
        assert sync_ch.entity_version == 1


def test_idempotent_replay_crash_after_commit_produces_one_domain_effect(collector_user):
    """AT-040: Prove crash-after-commit retry produces exactly one domain effect."""
    op_id = uuid.uuid4()
    lot_id = uuid.uuid4()
    payload = {
        "material_id": "MAT-BAT-01",
        "estimated_weight_g": 8200,
        "condition": "INTACT"
    }

    req_body = {
        "device_id": "phone-redmi-01",
        "operations": [
            {
                "operation_id": str(op_id),
                "entity_type": "LOT",
                "entity_id": str(lot_id),
                "command": "CREATE_DRAFT",
                "expected_version": None,
                "payload": payload
            }
        ]
    }

    # First send: successfully applied
    resp1 = client.post("/api/v1/sync/batch", json=req_body, headers=collector_user["headers"])
    assert resp1.status_code == 200
    assert resp1.json()["data"]["results"][0]["outcome"] == "APPLIED"

    # Count rows before retry
    with TestingSessionLocal() as session:
        initial_lots_count = len(session.execute(Lot.__table__.select().where(Lot.id == lot_id)).all())
        initial_sync_ops_count = len(session.execute(SyncOperation.__table__.select().where(SyncOperation.operation_id == op_id)).all())
        initial_sync_changes_count = len(session.execute(SyncChange.__table__.select().where(SyncChange.entity_id == lot_id)).all())

    assert initial_lots_count == 1
    assert initial_sync_ops_count == 1
    assert initial_sync_changes_count == 1

    # Simulate client crash / ACK loss: client retries the exact same operation
    resp2 = client.post("/api/v1/sync/batch", json=req_body, headers=collector_user["headers"])
    assert resp2.status_code == 200
    res2 = resp2.json()["data"]["results"][0]
    assert res2["operation_id"] == str(op_id)
    assert res2["outcome"] == "ALREADY_APPLIED"
    assert res2["entity_id"] == str(lot_id)
    assert res2["server_version"] == 1
    assert res2["result"] is not None

    # Verify no second domain effect occurred
    with TestingSessionLocal() as session:
        final_lots = session.execute(Lot.__table__.select().where(Lot.id == lot_id)).all()
        final_sync_ops = session.execute(SyncOperation.__table__.select().where(SyncOperation.operation_id == op_id)).all()
        final_sync_changes = session.execute(SyncChange.__table__.select().where(SyncChange.entity_id == lot_id)).all()

    assert len(final_lots) == 1, "Expected exactly 1 lot in database, not duplicates"
    assert len(final_sync_ops) == 1, "Expected exactly 1 sync_operations row"
    assert len(final_sync_changes) == 1, "Expected exactly 1 sync_changes row"


def test_reused_operation_id_with_different_payload_conflicts(collector_user):
    """AT-040: Same operation_id with a different payload returns CONFLICT (IDEMPOTENCY_KEY_REUSED)."""
    op_id = uuid.uuid4()
    lot_id = uuid.uuid4()

    # Initial operation
    initial_payload = {"material_id": "MAT-PCB-01", "estimated_weight_g": 2000}
    resp1 = client.post("/api/v1/sync/batch", json={
        "device_id": "device-1",
        "operations": [{
            "operation_id": str(op_id),
            "entity_type": "LOT",
            "entity_id": str(lot_id),
            "command": "CREATE_DRAFT",
            "payload": initial_payload
        }]
    }, headers=collector_user["headers"])
    assert resp1.status_code == 200
    assert resp1.json()["data"]["results"][0]["outcome"] == "APPLIED"

    # Reused operation_id with different payload (altered weight)
    tampered_payload = {"material_id": "MAT-PCB-01", "estimated_weight_g": 9999}
    resp2 = client.post("/api/v1/sync/batch", json={
        "device_id": "device-1",
        "operations": [{
            "operation_id": str(op_id),
            "entity_type": "LOT",
            "entity_id": str(lot_id),
            "command": "CREATE_DRAFT",
            "payload": tampered_payload
        }]
    }, headers=collector_user["headers"])
    assert resp2.status_code == 200
    res2 = resp2.json()["data"]["results"][0]
    assert res2["outcome"] == "CONFLICT"
    assert res2["error"]["code"] == "IDEMPOTENCY_KEY_REUSED"

    # Verify lot weight was NOT modified to 9999
    with TestingSessionLocal() as session:
        lot = session.execute(Lot.__table__.select().where(Lot.id == lot_id)).first()
        assert lot.estimated_weight_g == 2000


def test_foreign_user_cannot_replay_operation(collector_user, other_collector_user):
    """Security check: Another user cannot replay another actor's operation."""
    op_id = uuid.uuid4()
    lot_id = uuid.uuid4()

    # User 1 submits operation
    resp1 = client.post("/api/v1/sync/batch", json={
        "device_id": "device-1",
        "operations": [{
            "operation_id": str(op_id),
            "entity_type": "LOT",
            "entity_id": str(lot_id),
            "command": "CREATE_DRAFT",
            "payload": {"material_id": "MAT-CAB-01", "estimated_weight_g": 1000}
        }]
    }, headers=collector_user["headers"])
    assert resp1.status_code == 200
    assert resp1.json()["data"]["results"][0]["outcome"] == "APPLIED"

    # User 2 attempts to replay User 1's operation
    resp2 = client.post("/api/v1/sync/batch", json={
        "device_id": "device-2",
        "operations": [{
            "operation_id": str(op_id),
            "entity_type": "LOT",
            "entity_id": str(lot_id),
            "command": "CREATE_DRAFT",
            "payload": {"material_id": "MAT-CAB-01", "estimated_weight_g": 1000}
        }]
    }, headers=other_collector_user["headers"])
    assert resp2.status_code == 200
    res2 = resp2.json()["data"]["results"][0]
    assert res2["outcome"] == "CONFLICT"
    assert res2["error"]["code"] == "AUTH_FORBIDDEN"


def test_payload_sha256_verification(collector_user):
    """Verify cryptographic check on declared payload_sha256."""
    payload = {"material_id": "MAT-CAB-01", "estimated_weight_g": 1500}
    correct_hash = compute_canonical_hash(payload)

    # 1. Matching declared payload_sha256 -> APPLIED
    resp1 = client.post("/api/v1/sync/batch", json={
        "device_id": "device-1",
        "operations": [{
            "operation_id": str(uuid.uuid4()),
            "entity_type": "LOT",
            "entity_id": str(uuid.uuid4()),
            "command": "CREATE_DRAFT",
            "payload": payload,
            "payload_sha256": correct_hash
        }]
    }, headers=collector_user["headers"])
    assert resp1.status_code == 200
    assert resp1.json()["data"]["results"][0]["outcome"] == "APPLIED"

    # 2. Tampered declared payload_sha256 -> REJECTED
    resp2 = client.post("/api/v1/sync/batch", json={
        "device_id": "device-1",
        "operations": [{
            "operation_id": str(uuid.uuid4()),
            "entity_type": "LOT",
            "entity_id": str(uuid.uuid4()),
            "command": "CREATE_DRAFT",
            "payload": payload,
            "payload_sha256": "0000000000000000000000000000000000000000000000000000000000000000"
        }]
    }, headers=collector_user["headers"])
    assert resp2.status_code == 200
    res2 = resp2.json()["data"]["results"][0]
    assert res2["outcome"] == "REJECTED"
    assert res2["error"]["code"] == "PAYLOAD_HASH_MISMATCH"


def test_dependency_ordering_within_batch(collector_user):
    """AT-041: Topologically ordered batch executes parent before dependent children."""
    op1_id = uuid.uuid4()
    op2_id = uuid.uuid4()
    op3_id = uuid.uuid4()
    lot_id = uuid.uuid4()

    req_body = {
        "device_id": "device-dep-01",
        "operations": [
            # 1. Parent: Create draft (v1)
            {
                "operation_id": str(op1_id),
                "entity_type": "LOT",
                "entity_id": str(lot_id),
                "command": "CREATE_DRAFT",
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 5000}
            },
            # 2. Child 1: Update draft (v2, depends on op1)
            {
                "operation_id": str(op2_id),
                "entity_type": "LOT",
                "entity_id": str(lot_id),
                "command": "UPDATE_DRAFT",
                "expected_version": 1,
                "payload": {"estimated_weight_g": 5500},
                "depends_on": [str(op1_id)]
            },
            # 3. Child 2: Collect lot (v3, depends on op2)
            {
                "operation_id": str(op3_id),
                "entity_type": "LOT",
                "entity_id": str(lot_id),
                "command": "COLLECT_LOT",
                "expected_version": 2,
                "payload": {},
                "depends_on": [str(op2_id)]
            }
        ]
    }

    resp = client.post("/api/v1/sync/batch", json=req_body, headers=collector_user["headers"])
    assert resp.status_code == 200
    results = resp.json()["data"]["results"]
    assert len(results) == 3

    assert results[0]["outcome"] == "APPLIED"
    assert results[0]["server_version"] == 1

    assert results[1]["outcome"] == "APPLIED"
    assert results[1]["server_version"] == 2

    assert results[2]["outcome"] == "APPLIED"
    assert results[2]["server_version"] == 3

    # Check final lot state
    with TestingSessionLocal() as session:
        lot = session.execute(Lot.__table__.select().where(Lot.id == lot_id)).first()
        assert lot.status == "COLLECTED"
        assert lot.estimated_weight_g == 5500
        assert lot.version == 3


def test_mixed_success_batch_independent_sibling_succeeds(collector_user):
    """AT-040 / AT-041: Parent failure halts dependent child while independent sibling succeeds."""
    op_fail_id = uuid.uuid4()
    op_child_id = uuid.uuid4()
    op_sibling_id = uuid.uuid4()

    lot_fail_id = uuid.uuid4()
    lot_sibling_id = uuid.uuid4()

    req_body = {
        "device_id": "device-mixed-01",
        "operations": [
            # 1. Op fails validation (negative weight)
            {
                "operation_id": str(op_fail_id),
                "entity_type": "LOT",
                "entity_id": str(lot_fail_id),
                "command": "CREATE_DRAFT",
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": -500}
            },
            # 2. Dependent child waits on op_fail_id
            {
                "operation_id": str(op_child_id),
                "entity_type": "LOT",
                "entity_id": str(lot_fail_id),
                "command": "COLLECT_LOT",
                "payload": {},
                "depends_on": [str(op_fail_id)]
            },
            # 3. Independent sibling is valid
            {
                "operation_id": str(op_sibling_id),
                "entity_type": "LOT",
                "entity_id": str(lot_sibling_id),
                "command": "CREATE_DRAFT",
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 3000}
            }
        ]
    }

    resp = client.post("/api/v1/sync/batch", json=req_body, headers=collector_user["headers"])
    assert resp.status_code == 200
    results = resp.json()["data"]["results"]
    assert len(results) == 3

    # Op 1 rejected due to invalid weight
    assert results[0]["outcome"] == "REJECTED"
    assert results[0]["error"]["code"] == "INVALID_WEIGHT"

    # Op 2 pending dependency
    assert results[1]["outcome"] == "DEPENDENCY_PENDING"
    assert results[1]["error"]["code"] == "DEPENDENCY_FAILED"

    # Op 3 APPLIED and committed!
    assert results[2]["outcome"] == "APPLIED"
    assert results[2]["server_version"] == 1

    # Verify sibling lot was persisted, but failed lot was not
    with TestingSessionLocal() as session:
        lot_fail = session.execute(Lot.__table__.select().where(Lot.id == lot_fail_id)).first()
        lot_sibling = session.execute(Lot.__table__.select().where(Lot.id == lot_sibling_id)).first()

    assert lot_fail is None
    assert lot_sibling is not None
    assert lot_sibling.estimated_weight_g == 3000


def test_missing_uncommitted_dependency_waits(collector_user):
    """AT-041: Operation referencing unknown uncommitted dependency returns DEPENDENCY_PENDING."""
    uncommitted_dep_id = uuid.uuid4()
    op_id = uuid.uuid4()
    lot_id = uuid.uuid4()

    req_body = {
        "device_id": "device-1",
        "operations": [
            {
                "operation_id": str(op_id),
                "entity_type": "LOT",
                "entity_id": str(lot_id),
                "command": "CREATE_DRAFT",
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 1200},
                "depends_on": [str(uncommitted_dep_id)]
            }
        ]
    }

    resp = client.post("/api/v1/sync/batch", json=req_body, headers=collector_user["headers"])
    assert resp.status_code == 200
    res = resp.json()["data"]["results"][0]
    assert res["outcome"] == "DEPENDENCY_PENDING"
    assert res["error"]["code"] == "DEPENDENCY_NOT_SATISFIED"


def test_optimistic_concurrency_version_conflict(collector_user):
    """AT-041: Stale expected_version returns CONFLICT without overwriting server state."""
    lot_id = uuid.uuid4()
    # Step 1: Create draft (version 1)
    client.post("/api/v1/sync/batch", json={
        "device_id": "device-1",
        "operations": [{
            "operation_id": str(uuid.uuid4()),
            "entity_type": "LOT",
            "entity_id": str(lot_id),
            "command": "CREATE_DRAFT",
            "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 1000}
        }]
    }, headers=collector_user["headers"])

    # Step 2: Update to version 2
    client.post("/api/v1/sync/batch", json={
        "device_id": "device-1",
        "operations": [{
            "operation_id": str(uuid.uuid4()),
            "entity_type": "LOT",
            "entity_id": str(lot_id),
            "command": "UPDATE_DRAFT",
            "expected_version": 1,
            "payload": {"estimated_weight_g": 2000}
        }]
    }, headers=collector_user["headers"])

    # Step 3: Concurrent edit sending stale expected_version = 1
    resp = client.post("/api/v1/sync/batch", json={
        "device_id": "device-2",
        "operations": [{
            "operation_id": str(uuid.uuid4()),
            "entity_type": "LOT",
            "entity_id": str(lot_id),
            "command": "UPDATE_DRAFT",
            "expected_version": 1,
            "payload": {"estimated_weight_g": 9999}
        }]
    }, headers=collector_user["headers"])

    assert resp.status_code == 200
    res = resp.json()["data"]["results"][0]
    assert res["outcome"] == "CONFLICT"
    assert res["error"]["code"] == "VERSION_CONFLICT"
    assert res["server_version"] == 2
    assert res["error"]["details"]["current_version"] == 2

    # Verify database state was preserved at version 2 (weight 2000)
    with TestingSessionLocal() as session:
        lot = session.execute(Lot.__table__.select().where(Lot.id == lot_id)).first()
        assert lot.version == 2
        assert lot.estimated_weight_g == 2000


def test_batch_size_limit_enforced(collector_user):
    """Enforce max 50 operations per batch limit (422 BATCH_SIZE_EXCEEDED)."""
    ops = [
        {
            "operation_id": str(uuid.uuid4()),
            "entity_type": "LOT",
            "entity_id": str(uuid.uuid4()),
            "command": "CREATE_DRAFT",
            "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 100}
        }
        for _ in range(51)
    ]

    resp = client.post("/api/v1/sync/batch", json={
        "device_id": "device-overload",
        "operations": ops
    }, headers=collector_user["headers"])

    assert resp.status_code == 422
    err = resp.json()["detail"]["error"]
    assert err["code"] == "BATCH_SIZE_EXCEEDED"
    assert err["details"]["max_limit"] == 50
    assert err["details"]["received_count"] == 51


def test_price_observation_sync_operation(collector_user):
    """Test sync push for PRICE_OBSERVATION entity."""
    op_id = uuid.uuid4()
    obs_id = uuid.uuid4()

    resp = client.post("/api/v1/sync/batch", json={
        "device_id": "device-1",
        "operations": [{
            "operation_id": str(op_id),
            "entity_type": "PRICE_OBSERVATION",
            "entity_id": str(obs_id),
            "command": "CREATE_OBSERVATION",
            "payload": {
                "material_id": "MAT-PCB-01",
                "rate_paise_per_unit": 45000,
                "unit": "kg",
                "price_kind": "BUY",
                "region_id": "DELHI_NCR"
            }
        }]
    }, headers=collector_user["headers"])

    assert resp.status_code == 200
    res = resp.json()["data"]["results"][0]
    assert res["outcome"] == "APPLIED"
    assert res["server_version"] == 1

    with TestingSessionLocal() as session:
        obs = session.execute(PriceObservation.__table__.select().where(PriceObservation.id == obs_id)).first()
        assert obs is not None
        assert obs.rate_paise_per_unit == 45000
        assert obs.review_status == "PENDING_REVIEW"


def test_pull_changes_incremental_delta_and_cursors(collector_user):
    """Test cursor-based delta pull retrieving incremental changes."""
    # Seed a lot via sync
    lot_id = uuid.uuid4()
    client.post("/api/v1/sync/batch", json={
        "device_id": "device-1",
        "operations": [{
            "operation_id": str(uuid.uuid4()),
            "entity_type": "LOT",
            "entity_id": str(lot_id),
            "command": "CREATE_DRAFT",
            "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 4000}
        }]
    }, headers=collector_user["headers"])

    # Pull changes starting at cursor 0
    resp1 = client.get("/api/v1/sync/changes?cursor=0", headers=collector_user["headers"])
    assert resp1.status_code == 200
    data1 = resp1.json()

    assert "data" in data1
    assert "changes" in data1["data"]
    assert len(data1["data"]["changes"]) >= 1

    lot_change = next((c for c in data1["data"]["changes"] if c["entity_id"] == str(lot_id)), None)
    assert lot_change is not None
    assert lot_change["entity_type"] == "LOT"
    assert lot_change["operation"] == "UPSERT"
    assert lot_change["data"]["estimated_weight_g"] == 4000

    next_cursor = data1["meta"]["next_cursor"]
    assert next_cursor != "0"

    # Pull changes again with next_cursor -> should yield no new changes
    resp2 = client.get(f"/api/v1/sync/changes?cursor={next_cursor}", headers=collector_user["headers"])
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert len(data2["data"]["changes"]) == 0
    assert data2["meta"]["has_more"] is False


def test_pull_changes_tombstones_on_delete(collector_user):
    """AT-041: Deleted entity emits a tombstone with operation DELETE and data None."""
    lot_id = uuid.uuid4()
    # 1. Create lot
    client.post("/api/v1/sync/batch", json={
        "device_id": "device-1",
        "operations": [{
            "operation_id": str(uuid.uuid4()),
            "entity_type": "LOT",
            "entity_id": str(lot_id),
            "command": "CREATE_DRAFT",
            "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 2000}
        }]
    }, headers=collector_user["headers"])

    # 2. Delete lot
    client.post("/api/v1/sync/batch", json={
        "device_id": "device-1",
        "operations": [{
            "operation_id": str(uuid.uuid4()),
            "entity_type": "LOT",
            "entity_id": str(lot_id),
            "command": "DELETE",
            "payload": {}
        }]
    }, headers=collector_user["headers"])

    # 3. Pull changes
    resp = client.get("/api/v1/sync/changes?cursor=0", headers=collector_user["headers"])
    assert resp.status_code == 200
    changes = resp.json()["data"]["changes"]

    del_change = next((c for c in changes if c["entity_id"] == str(lot_id) and c["operation"] == "DELETE"), None)
    assert del_change is not None
    assert del_change["operation"] == "DELETE"
    assert del_change["data"] is None, "Tombstone data must be None"


def test_pull_changes_cursor_expired_410(collector_user):
    """Malformed or invalid cursor returns HTTP 410 CURSOR_EXPIRED."""
    resp = client.get("/api/v1/sync/changes?cursor=invalid_not_base64!", headers=collector_user["headers"])
    assert resp.status_code == 410
    err = resp.json()["detail"]["error"]
    assert err["code"] == "CURSOR_EXPIRED"
    assert err["retryable"] is False


def test_pull_changes_role_scoping(collector_user, other_collector_user, admin_user):
    """Visibility scoping: collector only sees own + public changes; admin sees all."""
    lot_a_id = uuid.uuid4()
    client.post("/api/v1/sync/batch", json={
        "device_id": "device-a",
        "operations": [{
            "operation_id": str(uuid.uuid4()),
            "entity_type": "LOT",
            "entity_id": str(lot_a_id),
            "command": "CREATE_DRAFT",
            "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 1000}
        }]
    }, headers=collector_user["headers"])

    # Collector B pulls changes -> should NOT see lot_a_id
    resp_b = client.get("/api/v1/sync/changes?cursor=0", headers=other_collector_user["headers"])
    assert resp_b.status_code == 200
    changes_b = resp_b.json()["data"]["changes"]
    assert not any(c["entity_id"] == str(lot_a_id) for c in changes_b)

    # Admin pulls changes -> DOES see lot_a_id
    resp_admin = client.get("/api/v1/sync/changes?cursor=0", headers=admin_user["headers"])
    assert resp_admin.status_code == 200
    changes_admin = resp_admin.json()["data"]["changes"]
    assert any(c["entity_id"] == str(lot_a_id) for c in changes_admin)


def test_push_and_pull_aliases(collector_user):
    """Verify backwards-compatible aliases /push and /pull."""
    op_id = uuid.uuid4()
    lot_id = uuid.uuid4()

    push_resp = client.post("/api/v1/sync/push", json={
        "device_id": "alias-device",
        "operations": [{
            "operation_id": str(op_id),
            "entity_type": "LOT",
            "entity_id": str(lot_id),
            "command": "CREATE_DRAFT",
            "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 500}
        }]
    }, headers=collector_user["headers"])
    assert push_resp.status_code == 200
    assert push_resp.json()["data"]["results"][0]["outcome"] == "APPLIED"

    pull_resp = client.get("/api/v1/sync/pull?cursor=0", headers=collector_user["headers"])
    assert pull_resp.status_code == 200
    assert "changes" in pull_resp.json()["data"]
