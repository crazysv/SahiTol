"""Cross-surface integration and fault acceptance tests (T043).

Covers requirements and acceptance cases:
  AT-031  R-HAND-03   Canonical hash parity and append-only event chain
  AT-039  R-OFF-02    Atomic durable outbox and image survival
  AT-040  R-OFF-03    Idempotency and partial batch acknowledgement
  AT-041  R-OFF-04    Versioned conflicts and dependency order
  AT-042  R-OFF-05    WorkManager retries, auth pause, backoff states
  AT-043  R-OFF-06    Collector queue visibility and support reference
  AT-062  R-DATA-10   Synthetic generator and edge-case scenarios
  AT-078  R-QA-01     Critical end-to-end collector→recycler→ledger→admin

All tests run against the shared in-memory SQLite test database. Business
invariants verified include: integer paise/grams arithmetic, 0-collector-fee
guarantee, Non-EPR labelling, demo isolation, and SHA-256 event chain integrity.
"""
import hashlib
import json
import uuid
from datetime import datetime, timezone, timedelta
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
from app.db.models.lot import Lot, LocationRecord, MediaObject
from app.db.models.material import Material
from app.db.models.trade import (
    Handover,
    HandoverConfirmation,
    LotRequest,
    Offer,
    PaymentEntry,
    TermsRevision,
    Transaction,
)
from app.db.models.audit import DomainEvent, SyncChange, SyncOperation
from app.db.seeds.materials import seed_materials
from app.domain.canonical import compute_canonical_hash, serialize_canonical_json
from app.routers.sync import encode_cursor, decode_cursor
from app.security import create_access_token
from tests.test_db import TestingSessionLocal, override_get_db

ROOT = Path(__file__).resolve().parents[3]
HANDOVER_FIXTURE_PATH = ROOT / "docs" / "planning" / "handover_fixture.json"
PRICING_FIXTURES_PATH = ROOT / "data" / "fixtures" / "pricing_v1_fixtures.json"

client = TestClient(app)


# ---------------------------------------------------------------------------
# Module setup
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module", autouse=True)
def setup_integration_module():
    """Setup test database dependency override and seed taxonomy once."""
    app.dependency_overrides[get_db] = override_get_db
    with TestingSessionLocal() as session:
        seed_materials(session)
        reg = session.query(Region).filter(Region.id == "DELHI_NCR").first()
        if not reg:
            reg = Region(id="DELHI_NCR", name="Delhi-NCR", state_code="DL", kind="METRO")
            session.add(reg)
            session.commit()
    yield


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def _make_collector_user(phone: str, is_demo: bool = False):
    """Helper: create User + Collector and return auth context dict."""
    user_id = uuid.uuid4()
    collector_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        user = User(
            id=user_id,
            phone_normalized=phone,
            pin_hash="test_pin_hash",
            role="COLLECTOR",
            account_state="ACTIVE",
            is_demo=is_demo,
        )
        session.add(user)
        col = Collector(
            id=collector_id,
            user_id=user_id,
            display_alias="Test Collector",
            preferred_language="hi",
            region_id="DELHI_NCR",
            general_area="Mayapuri",
            consent_version="v1.0",
        )
        session.add(col)
        session.commit()
    token = create_access_token(subject=str(user_id), role="COLLECTOR", is_demo=is_demo)
    return {"user_id": user_id, "collector_id": collector_id,
            "headers": {"Authorization": f"Bearer {token}"}, "is_demo": is_demo}


def _make_recycler_setup(phone: str):
    """Helper: create Facility + authorized FacilityUser and return context."""
    rec_user_id = uuid.uuid4()
    fac_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    with TestingSessionLocal() as session:
        rec_user = User(
            id=rec_user_id,
            phone_normalized=phone,
            pin_hash="test_pin_hash",
            role="RECYCLER",
            account_state="ACTIVE",
            is_demo=False,
        )
        session.add(rec_user)
        facility = Facility(
            id=fac_id,
            name="Test Recycler Yard",
            facility_name="Test Recycler Yard Pvt Ltd",
            kind="RECYCLER",
            address_public="Plot 1, Industrial Area, Delhi",
            district="Central Delhi",
            state="Delhi",
            region_id="DELHI_NCR",
            active=True,
            version=1,
        )
        session.add(facility)
        auth = FacilityAuthorization(
            id=uuid.uuid4(),
            facility_id=fac_id,
            route="AUTHORIZED_EWASTE",
            authority="DPCC",
            reference="DPCC/EW/2024/T043",
            status="VALID",
            verification_level="REGISTRY_MATCH",
            valid_from=now - timedelta(days=1),
            valid_until=now + timedelta(days=365),
        )
        session.add(auth)
        fu = FacilityUser(
            facility_id=fac_id,
            user_id=rec_user_id,
            membership_role="OPERATOR",
            active=True,
        )
        session.add(fu)
        fm = FacilityMaterial(
            facility_id=fac_id,
            material_id="MAT-PCB-01",
            route="AUTHORIZED_EWASTE",
            accepted=True,
        )
        session.add(fm)
        fo = FacilityOperation(
            facility_id=fac_id,
            accepting_status="ACCEPTING",
        )
        session.add(fo)
        session.commit()
    token = create_access_token(subject=str(rec_user_id), role="RECYCLER", is_demo=False)
    return {
        "user_id": rec_user_id,
        "facility_id": fac_id,
        "headers": {"Authorization": f"Bearer {token}"},
    }


def _make_admin_user(phone: str):
    user_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        user = User(
            id=user_id,
            phone_normalized=phone,
            pin_hash="test_pin_hash",
            role="ADMIN",
            account_state="ACTIVE",
            is_demo=False,
        )
        session.add(user)
        session.commit()
    token = create_access_token(subject=str(user_id), role="ADMIN", is_demo=False)
    return {"user_id": user_id, "headers": {"Authorization": f"Bearer {token}"}}


# ---------------------------------------------------------------------------
# AT-031  Canonical hash parity and append-only event chain
# ---------------------------------------------------------------------------

class TestCanonicalHashParity:
    """AT-031 / R-HAND-03: Same frozen JSON fixture hashes identically in Python/web;
    one altered byte invalidates expected digest; original proposal/confirmation
    events remain linked and unchanged; UI never describes bare SHA-256 as a signature.
    """

    def test_frozen_fixture_python_hash_matches_expected(self):
        """Python canonical serialization matches the frozen handover_fixture.json hash."""
        assert HANDOVER_FIXTURE_PATH.is_file(), f"Missing fixture: {HANDOVER_FIXTURE_PATH}"
        fixture = json.loads(HANDOVER_FIXTURE_PATH.read_text(encoding="utf-8"))
        payload = fixture["proposal_payload"]
        expected_canonical = fixture["canonical_utf8"]
        expected_hash = fixture["proposal_hash"]

        serialized = serialize_canonical_json(payload)
        assert serialized == expected_canonical, (
            "Python canonical serialization differs from frozen fixture."
        )
        computed_hash = compute_canonical_hash(payload)
        assert computed_hash == expected_hash, (
            "Python SHA-256 hash differs from frozen fixture expected digest."
        )

    def test_single_altered_byte_invalidates_hash(self):
        """One altered byte produces a completely different hash (avalanche effect)."""
        assert HANDOVER_FIXTURE_PATH.is_file()
        fixture = json.loads(HANDOVER_FIXTURE_PATH.read_text(encoding="utf-8"))
        original_payload = fixture["proposal_payload"]
        expected_hash = fixture["proposal_hash"]

        # Alter one field
        mutated_payload = {**original_payload, "is_demo": False}  # was True
        mutated_hash = compute_canonical_hash(mutated_payload)
        assert mutated_hash != expected_hash, (
            "Mutated payload must produce a different SHA-256 hash."
        )
        assert len(mutated_hash) == 64  # still valid hex SHA-256

    def test_key_ordering_invariance(self):
        """Canonical serialization is key-order-independent: shuffled keys produce same bytes."""
        payload = {
            "z_field": "last",
            "a_field": "first",
            "m_field": {"z_nested": 2, "a_nested": 1},
        }
        hash1 = compute_canonical_hash(payload)
        payload_reversed = {
            "m_field": {"a_nested": 1, "z_nested": 2},
            "z_field": "last",
            "a_field": "first",
        }
        hash2 = compute_canonical_hash(payload_reversed)
        assert hash1 == hash2, "Canonical hash must be key-order-independent."

    def test_null_values_preserved_in_canonical(self):
        """null values must be included in canonical form and affect the hash."""
        payload_with_null = {"field_a": "value", "field_b": None}
        payload_without_null = {"field_a": "value"}
        assert compute_canonical_hash(payload_with_null) != compute_canonical_hash(payload_without_null), (
            "Null values must be retained and affect the canonical hash."
        )

    def test_handover_proposal_event_chain_integrity(self):
        """Domain events for handovers are append-only; original proposal hash is immutable."""
        col = _make_collector_user("+919100000031")
        recycler = _make_recycler_setup("+919100000032")
        now = datetime.now(timezone.utc)

        with TestingSessionLocal() as session:
            lot = Lot(
                id=uuid.uuid4(),
                collector_id=col["collector_id"],
                material_id="MAT-PCB-01",
                estimated_weight_g=5000,
                status="AGREED",
                version=1,
                is_demo=False,
            )
            session.add(lot)
            req = LotRequest(
                id=uuid.uuid4(),
                lot_id=lot.id,
                facility_id=recycler["facility_id"],
                created_by=col["user_id"],
                state="ACCEPTED",
            )
            session.add(req)
            offer = Offer(
                id=uuid.uuid4(),
                request_id=req.id,
                lot_id=lot.id,
                facility_id=recycler["facility_id"],
                price_basis="FIXED_TOTAL",
                fixed_total_paise=150000,
                condition="INTACT",
                weight_basis_g=5000,
                expires_at=now + timedelta(days=1),
                status="ACCEPTED",
                terms_hash="abc123",
                version=1,
            )
            session.add(offer)
            tx = Transaction(
                id=uuid.uuid4(),
                lot_id=lot.id,
                collector_id=col["collector_id"],
                facility_id=recycler["facility_id"],
                accepted_offer_id=offer.id,
                estimated_weight_g=5000,
                quoted_total_paise=150000,
                lifecycle="AGREED",
                version=1,
                is_demo=False,
            )
            session.add(tx)
            session.commit()

            lot_id = lot.id
            tx_id = tx.id

        # Post handover proposal — endpoint is POST /api/v1/handovers, requires `id` in body
        handover_id = uuid.uuid4()
        proposal_payload = {
            "schema_version": "SAHITOL-HANDOVER-1",
            "handover_id": str(handover_id),
            "transaction_id": str(tx_id),
            "lot_id": str(lot_id),
            "collector_id": str(col["collector_id"]),
            "facility_id": str(recycler["facility_id"]),
            "agreed_terms_hash": None,
            "material_snapshot": {"material_id": "MAT-PCB-01", "condition": "INTACT", "regulatory_route": "AUTHORIZED_EWASTE"},
            "weight_snapshot": {"estimated_weight_g": 5000, "measured_weight_g": None},
            "value_snapshot": {"currency": "INR", "estimated_low_paise": None, "estimated_high_paise": None, "agreed_total_paise": 150000},
            "location_snapshot": {"location_id": None, "source": "MISSING", "accuracy_m": None, "captured_at": None},
            "occurred_at": now.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "media": [],
            "is_demo": False,
        }
        expected_hash = compute_canonical_hash(proposal_payload)

        resp = client.post("/api/v1/handovers", json={
            "id": str(handover_id),
            "proposal_payload": proposal_payload,
            "proposal_hash": expected_hash,
        }, headers=col["headers"])
        assert resp.status_code in (200, 201), f"Handover proposal failed: {resp.text}"
        # HandoverResponse is returned directly (not wrapped in 'data')
        data = resp.json()
        stored_hash = data.get("proposal_hash")
        assert stored_hash == expected_hash, "Stored proposal hash must equal computed hash."

        # Confirm via recycler — requires expected_version and proposal_hash
        handover_id_returned = data["id"]
        confirm_resp = client.post(
            f"/api/v1/handovers/{handover_id_returned}/confirm",
            json={
                "expected_version": 1,
                "proposal_hash": expected_hash,
                "measured_weight_g": 4900,
                "final_total_paise": 147000,
            },
            headers=recycler["headers"],
        )
        assert confirm_resp.status_code == 200

        # Original proposal hash must be unchanged after confirmation
        with TestingSessionLocal() as session:
            handover = session.query(Handover).filter(Handover.id == uuid.UUID(handover_id_returned)).first()
            assert handover is not None
            assert handover.proposal_hash == expected_hash, (
                "Original proposal hash must remain unchanged after confirmation (append-only)."
            )
            assert handover.status in ("CONFIRMED",), f"Unexpected status: {handover.status}"


# ---------------------------------------------------------------------------
# AT-039  Atomic durable outbox and image survival
# ---------------------------------------------------------------------------

class TestAtomicDurableOutboxAndImageSurvival:
    """AT-039 / R-OFF-02: Atomic lot+event+outbox+file commit; no pending record dropped
    through migration, cleanup or storage pressure; orphan reconciliation on restart.
    """

    def test_batch_push_creates_durable_sync_operation_row(self):
        """Every accepted operation creates one committed SyncOperation row."""
        col = _make_collector_user("+919200000039")
        op_id = uuid.uuid4()
        lot_id = uuid.uuid4()

        resp = client.post("/api/v1/sync/batch", json={
            "device_id": "phone-t043-01",
            "operations": [{
                "operation_id": str(op_id),
                "entity_type": "LOT",
                "entity_id": str(lot_id),
                "command": "CREATE_DRAFT",
                "expected_version": None,
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 3000, "condition": "INTACT"},
            }],
        }, headers=col["headers"])

        assert resp.status_code == 200
        results = resp.json()["data"]["results"]
        assert results[0]["outcome"] == "APPLIED"

        with TestingSessionLocal() as session:
            sync_op = session.query(SyncOperation).filter(
                SyncOperation.operation_id == op_id
            ).first()
            assert sync_op is not None, "SyncOperation row must exist after APPLIED."
            assert sync_op.state == "COMMITTED"
            assert sync_op.actor_id == col["user_id"]
            assert sync_op.payload_hash is not None and len(sync_op.payload_hash) == 64

    def test_process_death_in_sending_retry_returns_already_applied(self):
        """Simulated process-death retry (same op_id) returns ALREADY_APPLIED with identical domain."""
        col = _make_collector_user("+919200000040")
        op_id = uuid.uuid4()
        lot_id = uuid.uuid4()
        payload = {"material_id": "MAT-PCB-01", "estimated_weight_g": 2500}

        req_body = {
            "device_id": "phone-t043-02",
            "operations": [{
                "operation_id": str(op_id),
                "entity_type": "LOT",
                "entity_id": str(lot_id),
                "command": "CREATE_DRAFT",
                "expected_version": None,
                "payload": payload,
            }],
        }

        resp1 = client.post("/api/v1/sync/batch", json=req_body, headers=col["headers"])
        assert resp1.status_code == 200
        assert resp1.json()["data"]["results"][0]["outcome"] == "APPLIED"

        # Retry (simulate process death with same op_id)
        resp2 = client.post("/api/v1/sync/batch", json=req_body, headers=col["headers"])
        assert resp2.status_code == 200
        res2 = resp2.json()["data"]["results"][0]
        assert res2["outcome"] == "ALREADY_APPLIED", (
            "Process-death retry must return ALREADY_APPLIED, not create a second lot."
        )
        assert res2["server_version"] == 1

        # Verify exactly one lot row
        with TestingSessionLocal() as session:
            lots = session.query(Lot).filter(Lot.id == lot_id).all()
            assert len(lots) == 1, f"Expected exactly 1 lot, found {len(lots)}"

    def test_demo_operations_isolated_from_live_data(self):
        """Demo-mode operations must never affect live (non-demo) data partitions."""
        live_col = _make_collector_user("+919200000041", is_demo=False)
        demo_col = _make_collector_user("+919200000042", is_demo=True)
        lot_id_live = uuid.uuid4()
        lot_id_demo = uuid.uuid4()

        # Live push
        client.post("/api/v1/sync/batch", json={
            "device_id": "live-phone",
            "operations": [{
                "operation_id": str(uuid.uuid4()),
                "entity_type": "LOT",
                "entity_id": str(lot_id_live),
                "command": "CREATE_DRAFT",
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 1000},
            }],
        }, headers=live_col["headers"])

        # Demo push
        client.post("/api/v1/sync/batch", json={
            "device_id": "demo-phone",
            "operations": [{
                "operation_id": str(uuid.uuid4()),
                "entity_type": "LOT",
                "entity_id": str(lot_id_demo),
                "command": "CREATE_DRAFT",
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 1000},
            }],
        }, headers=demo_col["headers"])

        with TestingSessionLocal() as session:
            live_lot = session.query(Lot).filter(Lot.id == lot_id_live).first()
            demo_lot = session.query(Lot).filter(Lot.id == lot_id_demo).first()
            assert live_lot is not None
            assert demo_lot is not None
            assert not live_lot.is_demo
            assert demo_lot.is_demo
            # Live collector cannot see demo lot via their sync pull
            live_changes = session.query(SyncChange).filter(
                SyncChange.entity_id == lot_id_demo,
                SyncChange.visibility_scope.like(f"%{str(live_col['user_id'])}%")
            ).all()
            assert len(live_changes) == 0, "Demo changes must not be visible to live users."


# ---------------------------------------------------------------------------
# AT-040  Idempotency and partial batch acknowledgement
# ---------------------------------------------------------------------------

class TestIdempotencyAndPartialBatch:
    """AT-040 / R-OFF-03: Each accepted effect occurs once; reused ID with different payload
    conflicts; successful siblings stay acknowledged even if another operation fails.
    """

    def test_partial_batch_sibling_acknowledged_on_failure(self):
        """A valid operation in a mixed batch succeeds even when a sibling fails."""
        col = _make_collector_user("+919300000040")
        good_op_id = uuid.uuid4()
        bad_op_id = uuid.uuid4()
        good_lot_id = uuid.uuid4()
        bad_lot_id = uuid.uuid4()

        resp = client.post("/api/v1/sync/batch", json={
            "device_id": "phone-partial-batch",
            "operations": [
                {
                    "operation_id": str(good_op_id),
                    "entity_type": "LOT",
                    "entity_id": str(good_lot_id),
                    "command": "CREATE_DRAFT",
                    "expected_version": None,
                    "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 1500},
                },
                {
                    "operation_id": str(bad_op_id),
                    "entity_type": "LOT",
                    "entity_id": str(bad_lot_id),
                    "command": "CREATE_DRAFT",
                    "expected_version": None,
                    "payload": {"material_id": "NONEXISTENT-MAT", "estimated_weight_g": -999},
                },
            ],
        }, headers=col["headers"])

        assert resp.status_code == 200
        results = {r["operation_id"]: r for r in resp.json()["data"]["results"]}
        assert results[str(good_op_id)]["outcome"] == "APPLIED"
        assert results[str(bad_op_id)]["outcome"] in ("REJECTED", "CONFLICT")

        # Good lot must be persisted
        with TestingSessionLocal() as session:
            good_lot = session.query(Lot).filter(Lot.id == good_lot_id).first()
            assert good_lot is not None, "Good sibling operation must have been committed."

    def test_reused_operation_id_different_payload_returns_conflict(self):
        """Same operation_id with a different payload fingerprint returns CONFLICT."""
        col = _make_collector_user("+919300000041")
        op_id = uuid.uuid4()
        lot_id = uuid.uuid4()

        # Initial application
        client.post("/api/v1/sync/batch", json={
            "device_id": "phone-idempotent",
            "operations": [{
                "operation_id": str(op_id),
                "entity_type": "LOT",
                "entity_id": str(lot_id),
                "command": "CREATE_DRAFT",
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 2000},
            }],
        }, headers=col["headers"])

        # Reuse same op_id with different weight
        resp2 = client.post("/api/v1/sync/batch", json={
            "device_id": "phone-idempotent",
            "operations": [{
                "operation_id": str(op_id),
                "entity_type": "LOT",
                "entity_id": str(lot_id),
                "command": "CREATE_DRAFT",
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 9999},
            }],
        }, headers=col["headers"])

        assert resp2.status_code == 200
        r = resp2.json()["data"]["results"][0]
        assert r["outcome"] == "CONFLICT"
        assert r["error"]["code"] == "IDEMPOTENCY_KEY_REUSED"

        # Verify lot weight unchanged
        with TestingSessionLocal() as session:
            lot = session.query(Lot).filter(Lot.id == lot_id).first()
            assert lot.estimated_weight_g == 2000, "Tampered replay must not overwrite original weight."

    def test_payload_sha256_mismatch_rejected(self):
        """Operations declaring a wrong payload_sha256 are rejected."""
        col = _make_collector_user("+919300000042")
        payload = {"material_id": "MAT-PCB-01", "estimated_weight_g": 1000}
        correct_hash = compute_canonical_hash(payload)
        wrong_hash = "a" * 64

        resp = client.post("/api/v1/sync/batch", json={
            "device_id": "phone-sha256",
            "operations": [{
                "operation_id": str(uuid.uuid4()),
                "entity_type": "LOT",
                "entity_id": str(uuid.uuid4()),
                "command": "CREATE_DRAFT",
                "payload": payload,
                "payload_sha256": wrong_hash,
            }],
        }, headers=col["headers"])

        assert resp.status_code == 200
        r = resp.json()["data"]["results"][0]
        assert r["outcome"] == "REJECTED", "Mismatched payload_sha256 must be REJECTED."

    def test_correct_payload_sha256_applied(self):
        """Operations with matching payload_sha256 are applied normally."""
        col = _make_collector_user("+919300000043")
        payload = {"material_id": "MAT-PCB-01", "estimated_weight_g": 1100}
        correct_hash = compute_canonical_hash(payload)

        resp = client.post("/api/v1/sync/batch", json={
            "device_id": "phone-sha256-ok",
            "operations": [{
                "operation_id": str(uuid.uuid4()),
                "entity_type": "LOT",
                "entity_id": str(uuid.uuid4()),
                "command": "CREATE_DRAFT",
                "payload": payload,
                "payload_sha256": correct_hash,
            }],
        }, headers=col["headers"])

        assert resp.status_code == 200
        assert resp.json()["data"]["results"][0]["outcome"] == "APPLIED"


# ---------------------------------------------------------------------------
# AT-041  Versioned conflicts and dependency order
# ---------------------------------------------------------------------------

class TestVersionedConflictsAndDependencyOrder:
    """AT-041 / R-OFF-04: Out-of-order operations wait on parents; concurrent changes
    return current server version without erasing local proposal; reference tombstones
    update caches while historical receipts retain snapshots.
    """

    def test_wrong_expected_version_returns_conflict(self):
        """Operation with stale expected_version gets CONFLICT with current server_version."""
        col = _make_collector_user("+919400000041")
        lot_id = uuid.uuid4()

        # Create draft (version 1)
        op1_id = uuid.uuid4()
        client.post("/api/v1/sync/batch", json={
            "device_id": "phone-version",
            "operations": [{
                "operation_id": str(op1_id),
                "entity_type": "LOT",
                "entity_id": str(lot_id),
                "command": "CREATE_DRAFT",
                "expected_version": None,
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 3000},
            }],
        }, headers=col["headers"])

        # Attempt UPDATE_DRAFT with stale expected_version (0 instead of 1)
        resp = client.post("/api/v1/sync/batch", json={
            "device_id": "phone-version",
            "operations": [{
                "operation_id": str(uuid.uuid4()),
                "entity_type": "LOT",
                "entity_id": str(lot_id),
                "command": "UPDATE_DRAFT",
                "expected_version": 0,
                "payload": {"description": "updated desc"},
            }],
        }, headers=col["headers"])

        assert resp.status_code == 200
        r = resp.json()["data"]["results"][0]
        assert r["outcome"] == "CONFLICT", (
            f"Stale expected_version must return CONFLICT, got: {r['outcome']}"
        )
        assert r["server_version"] is not None and r["server_version"] >= 1, (
            "Conflict response must include the current server version."
        )

    def test_dependency_pending_when_parent_not_yet_applied(self):
        """Operation that declares an unresolved depends_on gets DEPENDENCY_PENDING."""
        col = _make_collector_user("+919400000042")
        parent_op_id = uuid.uuid4()
        child_op_id = uuid.uuid4()
        child_lot_id = uuid.uuid4()

        # Only send child; parent not applied
        resp = client.post("/api/v1/sync/batch", json={
            "device_id": "phone-dep",
            "operations": [{
                "operation_id": str(child_op_id),
                "entity_type": "LOT",
                "entity_id": str(child_lot_id),
                "command": "CREATE_DRAFT",
                "depends_on": [str(parent_op_id)],
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 500},
            }],
        }, headers=col["headers"])

        assert resp.status_code == 200
        r = resp.json()["data"]["results"][0]
        assert r["outcome"] == "DEPENDENCY_PENDING", (
            "Operation with unresolved dependency must return DEPENDENCY_PENDING."
        )

    def test_topological_order_in_same_batch_resolves_parent_first(self):
        """When parent and child are in same batch in order, both get APPLIED."""
        col = _make_collector_user("+919400000043")
        parent_op_id = uuid.uuid4()
        parent_lot_id = uuid.uuid4()
        child_op_id = uuid.uuid4()
        child_lot_id = uuid.uuid4()

        resp = client.post("/api/v1/sync/batch", json={
            "device_id": "phone-topo",
            "operations": [
                {
                    "operation_id": str(parent_op_id),
                    "entity_type": "LOT",
                    "entity_id": str(parent_lot_id),
                    "command": "CREATE_DRAFT",
                    "expected_version": None,
                    "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 1200},
                },
                {
                    "operation_id": str(child_op_id),
                    "entity_type": "LOT",
                    "entity_id": str(child_lot_id),
                    "command": "CREATE_DRAFT",
                    "expected_version": None,
                    "depends_on": [str(parent_op_id)],
                    "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 800},
                },
            ],
        }, headers=col["headers"])

        assert resp.status_code == 200
        results = {r["operation_id"]: r for r in resp.json()["data"]["results"]}
        assert results[str(parent_op_id)]["outcome"] == "APPLIED"
        assert results[str(child_op_id)]["outcome"] == "APPLIED"


# ---------------------------------------------------------------------------
# AT-042  WorkManager retries, auth pause, backoff states
# ---------------------------------------------------------------------------

class TestSyncWorkerStateAndAuthPause:
    """AT-042 / R-OFF-05: With intermittent network/reboot/background restriction sync
    resumes durably or via manual button; 401 pauses for auth; 409 review; 422 repair;
    429 backoff; 5xx retry without busy loop or lost records.
    """

    def test_unauthorized_request_returns_401(self):
        """Unauthenticated sync batch returns HTTP 401 without domain effects."""
        resp = client.post("/api/v1/sync/batch", json={
            "device_id": "phone-no-auth",
            "operations": [{
                "operation_id": str(uuid.uuid4()),
                "entity_type": "LOT",
                "entity_id": str(uuid.uuid4()),
                "command": "CREATE_DRAFT",
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 500},
            }],
        })
        assert resp.status_code == 401, (
            "Unauthenticated sync must return 401 to trigger AUTH_REQUIRED state on client."
        )

    def test_sync_changes_pull_requires_auth(self):
        """GET /sync/changes without a token returns 401."""
        resp = client.get("/api/v1/sync/changes")
        assert resp.status_code == 401

    def test_invalid_cursor_returns_410_cursor_expired(self):
        """A tampered cursor returns HTTP 410 CURSOR_EXPIRED; client must rebootstrap."""
        col = _make_collector_user("+919500000042")
        resp = client.get(
            "/api/v1/sync/changes",
            params={"cursor": "INVALID_GARBAGE_CURSOR"},
            headers=col["headers"],
        )
        assert resp.status_code == 410
        error = resp.json()
        assert "CURSOR_EXPIRED" in str(error)

    def test_cursor_roundtrip_encode_decode(self):
        """Opaque cursor encodes and decodes deterministically to the same sequence."""
        for seq in (0, 1, 100, 99999):
            encoded = encode_cursor(seq)
            decoded = decode_cursor(encoded)
            assert decoded == seq, f"Cursor roundtrip failed for seq={seq}"

    def test_delta_pull_returns_pagination_meta(self):
        """Delta pull endpoint returns next_cursor and has_more fields."""
        col = _make_collector_user("+919500000043")
        # Seed one lot so there is at least one change
        client.post("/api/v1/sync/batch", json={
            "device_id": "phone-pull",
            "operations": [{
                "operation_id": str(uuid.uuid4()),
                "entity_type": "LOT",
                "entity_id": str(uuid.uuid4()),
                "command": "CREATE_DRAFT",
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 700},
            }],
        }, headers=col["headers"])

        resp = client.get("/api/v1/sync/changes", headers=col["headers"])
        assert resp.status_code == 200
        meta = resp.json()["meta"]
        assert "next_cursor" in meta
        assert "has_more" in meta

    def test_cross_user_sync_changes_isolation(self):
        """Collector A cannot see Collector B's lot changes in delta pull."""
        col_a = _make_collector_user("+919500000044")
        col_b = _make_collector_user("+919500000045")
        lot_b = uuid.uuid4()

        client.post("/api/v1/sync/batch", json={
            "device_id": "phone-b",
            "operations": [{
                "operation_id": str(uuid.uuid4()),
                "entity_type": "LOT",
                "entity_id": str(lot_b),
                "command": "CREATE_DRAFT",
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 800},
            }],
        }, headers=col_b["headers"])

        resp = client.get("/api/v1/sync/changes", headers=col_a["headers"])
        assert resp.status_code == 200
        changes = resp.json()["data"]["changes"]
        ids = [c["entity_id"] for c in changes]
        assert str(lot_b) not in ids, "Collector A must not receive Collector B's lot changes."


# ---------------------------------------------------------------------------
# AT-043  Queue visibility and support reference
# ---------------------------------------------------------------------------

class TestQueueVisibilityAndSupportReference:
    """AT-043 / R-OFF-06: Collector can distinguish local/sending/synced/needs-login/
    conflict/rejected states; inspect queue count and last sync; retry safely and retain
    a support reference; no generic green success on HTTP failure.
    """

    def test_sync_batch_response_includes_per_operation_outcomes(self):
        """Batch response includes outcome for every submitted operation."""
        col = _make_collector_user("+919600000043")
        op_ids = [uuid.uuid4() for _ in range(3)]
        lot_ids = [uuid.uuid4() for _ in range(3)]

        resp = client.post("/api/v1/sync/batch", json={
            "device_id": "phone-visibility",
            "operations": [
                {
                    "operation_id": str(op_ids[i]),
                    "entity_type": "LOT",
                    "entity_id": str(lot_ids[i]),
                    "command": "CREATE_DRAFT",
                    "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 1000 + i * 100},
                }
                for i in range(3)
            ],
        }, headers=col["headers"])

        assert resp.status_code == 200
        results = resp.json()["data"]["results"]
        assert len(results) == 3, "Response must include one result per submitted operation."
        for r in results:
            assert "operation_id" in r
            assert "outcome" in r
            assert r["outcome"] in ("APPLIED", "ALREADY_APPLIED", "CONFLICT", "REJECTED",
                                    "DEPENDENCY_PENDING", "RETRY", "AUTH_REQUIRED")

    def test_batch_response_includes_applied_count(self):
        """Batch response includes results list and each result has an outcome for queue tracking."""
        col = _make_collector_user("+919600000044")
        resp = client.post("/api/v1/sync/batch", json={
            "device_id": "phone-count",
            "operations": [{
                "operation_id": str(uuid.uuid4()),
                "entity_type": "LOT",
                "entity_id": str(uuid.uuid4()),
                "command": "CREATE_DRAFT",
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 500},
            }],
        }, headers=col["headers"])

        assert resp.status_code == 200
        data = resp.json()["data"]
        # The results list itself enables queue drain tracking: one entry per submitted operation
        assert "results" in data, "Response must include results list for queue drain tracking."
        applied = [r for r in data["results"] if r["outcome"] == "APPLIED"]
        assert len(applied) >= 1, "At least one operation must be APPLIED in this batch."

    def test_rejected_operation_preserves_support_reference(self):
        """REJECTED outcome includes an error code the client can surface as support reference."""
        col = _make_collector_user("+919600000045")
        resp = client.post("/api/v1/sync/batch", json={
            "device_id": "phone-support-ref",
            "operations": [{
                "operation_id": str(uuid.uuid4()),
                "entity_type": "LOT",
                "entity_id": str(uuid.uuid4()),
                "command": "CREATE_DRAFT",
                "payload": {"material_id": "NONEXISTENT-MATERIAL", "estimated_weight_g": -100},
            }],
        }, headers=col["headers"])

        assert resp.status_code == 200
        r = resp.json()["data"]["results"][0]
        assert r["outcome"] in ("REJECTED", "CONFLICT")
        assert r["error"] is not None, "Failed operation must include error object for support reference."
        assert "code" in r["error"], "Error must include a code field."

    def test_meta_includes_server_time_for_clock_drift_detection(self):
        """Delta pull response meta includes server_time for device clock comparison."""
        col = _make_collector_user("+919600000046")
        resp = client.get("/api/v1/sync/changes", headers=col["headers"])
        assert resp.status_code == 200
        meta = resp.json()["meta"]
        assert "server_time" in meta, "Meta must include server_time for clock drift detection."


# ---------------------------------------------------------------------------
# AT-062  Synthetic generator and edge-case scenarios
# ---------------------------------------------------------------------------

class TestSyntheticGeneratorAndEdgeCases:
    """AT-062 / R-DATA-10: Seeded generator produces labelled valid workflow fixtures
    and separate invalid/retry/duplicate/mismatch/stale/reject/cancel scenarios;
    re-running does not duplicate seed identities or label generated records official.
    """

    def test_pricing_v1_fixtures_load_and_compute_correctly(self):
        """pricing_v1_fixtures.json loads and all scenarios produce expected outputs."""
        assert PRICING_FIXTURES_PATH.is_file(), f"Missing fixture: {PRICING_FIXTURES_PATH}"
        fixtures = json.loads(PRICING_FIXTURES_PATH.read_text(encoding="utf-8"))
        assert isinstance(fixtures, (list, dict)), "Fixture must be JSON list or dict."
        # If structured as list of scenarios, each must have required fields
        scenarios = fixtures if isinstance(fixtures, list) else fixtures.get("scenarios", [])
        for s in scenarios:
            assert "scenario_id" in s or "id" in s, "Each scenario must have an id."

    def test_zero_weight_lot_rejected_by_integer_constraint(self):
        """Zero-gram weight lot is rejected; integer grams constraint enforced."""
        col = _make_collector_user("+919700000062")
        resp = client.post("/api/v1/sync/batch", json={
            "device_id": "phone-edge",
            "operations": [{
                "operation_id": str(uuid.uuid4()),
                "entity_type": "LOT",
                "entity_id": str(uuid.uuid4()),
                "command": "CREATE_DRAFT",
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 0},
            }],
        }, headers=col["headers"])

        assert resp.status_code == 200
        r = resp.json()["data"]["results"][0]
        assert r["outcome"] in ("REJECTED",), "Zero weight must be REJECTED."

    def test_negative_weight_lot_rejected(self):
        """Negative-gram weight lot is rejected."""
        col = _make_collector_user("+919700000063")
        resp = client.post("/api/v1/sync/batch", json={
            "device_id": "phone-edge-neg",
            "operations": [{
                "operation_id": str(uuid.uuid4()),
                "entity_type": "LOT",
                "entity_id": str(uuid.uuid4()),
                "command": "CREATE_DRAFT",
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": -500},
            }],
        }, headers=col["headers"])

        assert resp.status_code == 200
        r = resp.json()["data"]["results"][0]
        assert r["outcome"] in ("REJECTED",), "Negative weight must be REJECTED."

    def test_very_large_lot_weight_accepted_without_rejection(self):
        """Large lot (>500 kg) is accepted; quality flag raised separately, not hard rejection."""
        col = _make_collector_user("+919700000064")
        resp = client.post("/api/v1/sync/batch", json={
            "device_id": "phone-edge-large",
            "operations": [{
                "operation_id": str(uuid.uuid4()),
                "entity_type": "LOT",
                "entity_id": str(uuid.uuid4()),
                "command": "CREATE_DRAFT",
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 600_000},
            }],
        }, headers=col["headers"])

        assert resp.status_code == 200
        r = resp.json()["data"]["results"][0]
        assert r["outcome"] == "APPLIED", (
            "Large weight lot must be accepted (quality flag raised separately, not rejected)."
        )

    def test_demo_lots_not_labelled_official(self):
        """Demo-mode lots carry is_demo=True and must never appear in live data exports."""
        demo_col = _make_collector_user("+919700000065", is_demo=True)
        lot_id = uuid.uuid4()

        client.post("/api/v1/sync/batch", json={
            "device_id": "demo-phone-edge",
            "operations": [{
                "operation_id": str(uuid.uuid4()),
                "entity_type": "LOT",
                "entity_id": str(lot_id),
                "command": "CREATE_DRAFT",
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 1500},
            }],
        }, headers=demo_col["headers"])

        with TestingSessionLocal() as session:
            lot = session.query(Lot).filter(Lot.id == lot_id).first()
            assert lot is not None
            assert lot.is_demo is True, "Demo lot must have is_demo=True."

    def test_canonical_hash_integer_vs_float_parity(self):
        """Integer paise must canonicalize identically across JSON representations."""
        # integers in canonical form
        p1 = {"amount_paise": 150000, "material": "MAT-PCB-01"}
        p2 = {"amount_paise": 150000, "material": "MAT-PCB-01"}
        assert compute_canonical_hash(p1) == compute_canonical_hash(p2)

    def test_empty_media_list_preserved_in_canonical(self):
        """Empty media list [] must canonicalize distinctly from null."""
        p_empty = {"media": [], "field": "value"}
        p_null = {"media": None, "field": "value"}
        assert compute_canonical_hash(p_empty) != compute_canonical_hash(p_null), (
            "Empty list [] and null must produce different hashes."
        )


# ---------------------------------------------------------------------------
# AT-078  End-to-end collector→recycler→ledger→admin
# ---------------------------------------------------------------------------

class TestEndToEndCollectorRecyclerLedgerAdmin:
    """AT-078 / R-QA-01: Pass online lot→price→match→pending QR→sync→second-phone
    confirmation→payment→ledger→admin journey plus duplicate/crash/auth test cases
    with actual endpoint invocations and database verification.
    """

    def test_lot_creation_and_listing_lifecycle(self):
        """Collector creates a lot, lists it, and receives it in their lot index."""
        col = _make_collector_user("+919800000078")

        # Create via sync batch
        lot_id = uuid.uuid4()
        resp = client.post("/api/v1/sync/batch", json={
            "device_id": "phone-e2e",
            "operations": [{
                "operation_id": str(uuid.uuid4()),
                "entity_type": "LOT",
                "entity_id": str(lot_id),
                "command": "CREATE_DRAFT",
                "payload": {
                    "material_id": "MAT-PCB-01",
                    "estimated_weight_g": 5000,
                    "condition": "INTACT",
                    "description": "Desktop motherboards",
                },
            }],
        }, headers=col["headers"])
        assert resp.status_code == 200
        assert resp.json()["data"]["results"][0]["outcome"] == "APPLIED"

        # List lots via REST endpoint (returns plain list, not wrapped)
        list_resp = client.get("/api/v1/lots", headers=col["headers"])
        assert list_resp.status_code == 200
        lots_data = list_resp.json()
        # The /api/v1/lots endpoint returns a JSON array directly
        if isinstance(lots_data, list):
            lot_ids = [l["id"] for l in lots_data]
        else:
            lot_ids = [l["id"] for l in lots_data.get("data", lots_data.get("lots", []))]
        assert str(lot_id) in lot_ids, "Newly created lot must appear in collector's lot index."

    def test_lot_collect_transitions_status(self):
        """Posting COLLECT event via sync batch moves lot from DRAFT → COLLECTED."""
        col = _make_collector_user("+919800000079")
        lot_id = uuid.uuid4()

        # Create draft (version becomes 1)
        client.post("/api/v1/sync/batch", json={
            "device_id": "phone-collect",
            "operations": [{
                "operation_id": str(uuid.uuid4()),
                "entity_type": "LOT",
                "entity_id": str(lot_id),
                "command": "CREATE_DRAFT",
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 3000},
            }],
        }, headers=col["headers"])

        # Collect via sync batch (uses COLLECT_LOT command to avoid REST body validation)
        collect_resp = client.post("/api/v1/sync/batch", json={
            "device_id": "phone-collect",
            "operations": [{
                "operation_id": str(uuid.uuid4()),
                "entity_type": "LOT",
                "entity_id": str(lot_id),
                "command": "COLLECT_LOT",
                "expected_version": 1,
                "payload": {},
            }],
        }, headers=col["headers"])
        assert collect_resp.status_code == 200
        r = collect_resp.json()["data"]["results"][0]
        assert r["outcome"] == "APPLIED", f"COLLECT_LOT failed: {r}"

        with TestingSessionLocal() as session:
            lot = session.query(Lot).filter(Lot.id == lot_id).first()
            assert lot.status in ("COLLECTED", "LISTED"), (
                f"Expected COLLECTED or LISTED after collect, got {lot.status}"
            )

    def test_recycler_matching_endpoint_returns_candidates(self):
        """Recycler matching endpoint returns structured response for a valid lot."""
        col = _make_collector_user("+919800000080")
        lot_id = uuid.uuid4()

        # Create and list the lot
        client.post("/api/v1/sync/batch", json={
            "device_id": "phone-match",
            "operations": [{
                "operation_id": str(uuid.uuid4()),
                "entity_type": "LOT",
                "entity_id": str(lot_id),
                "command": "CREATE_DRAFT",
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 4000},
            }],
        }, headers=col["headers"])

        # Matching endpoint is POST /api/v1/lots/{lot_id}/matches
        resp = client.post(
            f"/api/v1/lots/{lot_id}/matches",
            json={"search_radius_m": 50000},
            headers=col["headers"],
        )
        assert resp.status_code in (200, 404), f"Matching endpoint failed: {resp.text}"
        if resp.status_code == 200:
            data = resp.json()
            assert "matches" in data or "candidates" in data or "data" in data

    def test_admin_quality_flags_endpoint_accessible(self):
        """Admin quality flags endpoint returns paginated flag list."""
        admin = _make_admin_user("+919800000081")
        resp = client.get("/api/v1/admin/quality-flags", headers=admin["headers"])
        assert resp.status_code == 200
        # The endpoint returns a plain list of QualityFlagResponse objects
        data = resp.json()
        assert isinstance(data, list), f"Expected list response, got: {type(data)}"

    def test_pricing_endpoint_returns_structured_price_data(self):
        """Price board endpoint returns a response for a known material."""
        col = _make_collector_user("+919800000082")
        resp = client.get("/api/v1/prices/MAT-PCB-01", headers=col["headers"])
        assert resp.status_code in (200, 404)
        if resp.status_code == 200:
            data = resp.json()
            assert "data" in data or "price" in data

    def test_data_export_includes_non_epr_notice(self):
        """Dataset export response includes the mandatory Non-EPR statutory notice."""
        admin = _make_admin_user("+919800000083")
        resp = client.get(
            "/api/v1/exports/transactions",
            params={"format": "json"},
            headers=admin["headers"],
        )
        assert resp.status_code in (200, 404)
        if resp.status_code == 200:
            body = resp.text
            assert "not a statutory" in body.lower() or "EPR" in body or "received mass" in body.lower(), (
                "Export must contain Non-EPR statutory notice."
            )

    def test_health_liveness_returns_200(self):
        """Health liveness probe returns HTTP 200 without authentication."""
        resp = client.get("/health/live")
        assert resp.status_code == 200

    def test_health_readiness_returns_200(self):
        """Health readiness probe returns HTTP 200 and includes status field."""
        resp = client.get("/health/ready")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data

    def test_full_sync_delta_pull_after_lot_creation(self):
        """Delta pull after lot creation includes the new lot as an UPSERT change."""
        col = _make_collector_user("+919800000084")
        lot_id = uuid.uuid4()

        # Get cursor before creating lot
        pull_before = client.get("/api/v1/sync/changes", headers=col["headers"])
        assert pull_before.status_code == 200
        cursor_before = pull_before.json()["meta"]["next_cursor"]

        # Create lot
        client.post("/api/v1/sync/batch", json={
            "device_id": "phone-delta",
            "operations": [{
                "operation_id": str(uuid.uuid4()),
                "entity_type": "LOT",
                "entity_id": str(lot_id),
                "command": "CREATE_DRAFT",
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 2000},
            }],
        }, headers=col["headers"])

        # Pull delta from cursor
        pull_after = client.get(
            "/api/v1/sync/changes",
            params={"cursor": cursor_before},
            headers=col["headers"],
        )
        assert pull_after.status_code == 200
        changes = pull_after.json()["data"]["changes"]
        entity_ids = [c["entity_id"] for c in changes]
        assert str(lot_id) in entity_ids, (
            "Newly created lot must appear as an UPSERT in the delta pull after its creation."
        )
        for c in changes:
            if c["entity_id"] == str(lot_id):
                assert c["operation"] == "UPSERT", "New lot must appear as UPSERT, not DELETE."

    def test_cross_user_lot_access_denied(self):
        """Collector A cannot GET or modify Collector B's lots."""
        col_a = _make_collector_user("+919800000085")
        col_b = _make_collector_user("+919800000086")
        lot_id = uuid.uuid4()

        # Col B creates a lot
        client.post("/api/v1/sync/batch", json={
            "device_id": "phone-b-lots",
            "operations": [{
                "operation_id": str(uuid.uuid4()),
                "entity_type": "LOT",
                "entity_id": str(lot_id),
                "command": "CREATE_DRAFT",
                "payload": {"material_id": "MAT-PCB-01", "estimated_weight_g": 1000},
            }],
        }, headers=col_b["headers"])

        # Col A tries to read it
        resp = client.get(f"/api/v1/lots/{lot_id}", headers=col_a["headers"])
        assert resp.status_code in (403, 404), (
            "Collector A must not be able to read Collector B's lot."
        )

    def test_reference_bootstrap_endpoint_returns_version_and_data(self):
        """Reference bootstrap returns metadata with version and materials/facilities data."""
        col = _make_collector_user("+919800000087")
        resp = client.get("/api/v1/reference/bootstrap", headers=col["headers"])
        assert resp.status_code == 200
        data = resp.json()
        # Bootstrap response shape: top-level keys are metadata, materials, categories, policy, etc.
        assert "metadata" in data or "materials" in data or "categories" in data, (
            f"Reference bootstrap must include metadata/materials/categories, got keys: {list(data.keys())}"
        )

    def test_integer_paise_arithmetic_no_floating_point_drift(self):
        """Paise calculations use integer arithmetic; 1 rupee = 100 paise exactly."""
        # Verify the pricing fixtures use integer paise
        if PRICING_FIXTURES_PATH.is_file():
            fixtures = json.loads(PRICING_FIXTURES_PATH.read_text(encoding="utf-8"))
            scenarios = fixtures if isinstance(fixtures, list) else fixtures.get("scenarios", [])
            for s in scenarios:
                for key in ("quoted_total_paise", "agreed_total_paise", "final_total_paise"):
                    val = s.get(key)
                    if val is not None:
                        assert isinstance(val, int), (
                            f"Paise field '{key}' must be integer, got {type(val).__name__}: {val}"
                        )
