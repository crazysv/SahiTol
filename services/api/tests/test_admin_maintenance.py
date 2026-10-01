"""Comprehensive unit and integration tests for Admin Maintenance, Overview Metrics,
Directory Review, Taxonomy Maintenance, and Event Traceability (T029).
Technical specification: docs/16_API_CONTRACT.md lines 77-93, docs/MONITORING.md, docs/06_SCHEMA.md.
Requirements: R-ADMIN-01, R-ADMIN-02, R-ADMIN-03, R-ADMIN-04, R-ADMIN-05, R-ADMIN-06, R-PRICE-05, R-HAND-05, R-OPS-04.
Acceptance cases: AT-064, AT-065, AT-077.
"""
from datetime import datetime, timedelta, timezone
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import get_db
from app.db.models.audit import DomainEvent, QualityFlag
from app.db.models.auth import User
from app.db.models.price import PriceObservation
from app.db.models.collector import Collector
from app.db.models.facility import Facility, FacilityAuthorization, FacilityUser, Region
from app.db.models.material import MaterialCategory, Material, MaterialAlias, SafetyGuide
from app.db.models.lot import Lot
from app.db.models.trade import LotRequest, Offer, Transaction, Handover, TermsRevision, PaymentEntry
from app.db.seeds.materials import seed_materials
from app.security import UserRole, create_access_token
from app.routers.admin import ADMIN_UUID_NAMESPACE
from tests.test_db import TestingSessionLocal, override_get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_admin_module():
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
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def admin_user(db: Session):
    """Create an admin user and return (user, auth_headers)."""
    user = User(
        id=uuid.uuid4(),
        phone_normalized="+919876543110",
        pin_hash="pin_admin_hash",
        role=UserRole.ADMIN.value,
        account_state="ACTIVE",
        is_demo=False
    )
    db.add(user)
    db.commit()
    token = create_access_token(subject=str(user.id), role=user.role, is_demo=False)
    headers = {"Authorization": f"Bearer {token}"}
    try:
        yield user, headers
    finally:
        db.query(User).filter(User.id == user.id).delete()
        db.commit()


@pytest.fixture
def collector_user(db: Session):
    """Create a collector user and return (user, auth_headers)."""
    user = User(
        id=uuid.uuid4(),
        phone_normalized="+919876543111",
        pin_hash="pin_collector_hash",
        role=UserRole.COLLECTOR.value,
        account_state="ACTIVE",
        is_demo=False
    )
    collector = Collector(
        id=user.id,
        user_id=user.id,
        display_alias="Santosh_Kabadi",
        preferred_language="hi",
        region_id="DELHI_NCR",
        general_area="Mayapuri",
        consent_version="v1.0"
    )
    db.add_all([user, collector])
    db.commit()
    token = create_access_token(subject=str(user.id), role=user.role, is_demo=False)
    headers = {"Authorization": f"Bearer {token}"}
    try:
        yield user, headers
    finally:
        db.query(Collector).filter(Collector.id == user.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()


@pytest.fixture
def recycler_user(db: Session):
    """Create a recycler facility and user, returning (user, facility, auth_headers)."""
    user = User(
        id=uuid.uuid4(),
        phone_normalized="+919876543112",
        pin_hash="pin_recycler_hash",
        role=UserRole.RECYCLER.value,
        account_state="ACTIVE",
        is_demo=False
    )
    facility = Facility(
        id=uuid.uuid4(),
        name="Mayapuri Clean Dismantlers",
        facility_name="Mayapuri Clean Dismantlers",
        kind="DISMANTLER",
        address_public="Mayapuri Phase II, New Delhi",
        district="West Delhi",
        state="Delhi",
        region_id="DELHI_NCR",
        active=True,
        version=1
    )
    fac_user = FacilityUser(
        user_id=user.id,
        facility_id=facility.id,
        membership_role="OWNER",
        active=True
    )
    db.add_all([user, facility, fac_user])
    db.commit()
    token = create_access_token(subject=str(user.id), role=user.role, is_demo=False)
    headers = {"Authorization": f"Bearer {token}"}
    try:
        yield user, facility, headers
    finally:
        db.query(FacilityUser).filter(FacilityUser.user_id == user.id).delete()
        db.query(FacilityAuthorization).filter(FacilityAuthorization.facility_id == facility.id).delete()
        db.query(Facility).filter(Facility.id == facility.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()


# =============================================================================
# 1. Authorization & Role Scoping Tests (AT-064)
# =============================================================================

def test_admin_overview_unauthorized_for_collector_and_recycler(
    client: TestClient,
    collector_user,
    recycler_user
):
    """Ordinary collectors and recyclers cannot access administrative overview (HTTP 403)."""
    _, c_headers = collector_user
    _, _, r_headers = recycler_user

    # Collector rejected
    resp_c = client.get("/api/v1/admin/overview", headers=c_headers)
    assert resp_c.status_code == 403

    # Recycler rejected
    resp_r = client.get("/api/v1/admin/overview", headers=r_headers)
    assert resp_r.status_code == 403

    # Unauthenticated rejected
    resp_anon = client.get("/api/v1/admin/overview")
    assert resp_anon.status_code in {401, 403}


def test_recycler_cannot_approve_itself(
    client: TestClient,
    recycler_user
):
    """
    AT-064: Ordinary recycler cannot approve itself or assert facility verification.
    Requires ADMIN role; returns HTTP 403.
    """
    _, facility, r_headers = recycler_user
    payload = {
        "route": "AUTHORIZED_EWASTE",
        "authority": "CPCB",
        "reference": "CPCB/EW/SELF/999",
        "reason": "Self verification attempt"
    }
    resp = client.post(
        f"/api/v1/admin/facilities/{facility.id}/verification",
        json=payload,
        headers=r_headers
    )
    assert resp.status_code == 403


# =============================================================================
# 2. Overview Metrics with Real Denominators & Demo Isolation (R-ADMIN-06, AT-077)
# =============================================================================

def test_admin_overview_metrics_with_real_denominators(
    client: TestClient,
    admin_user,
    collector_user,
    recycler_user,
    db: Session
):
    """
    R-ADMIN-06 / AT-077: Platform overview metrics derive from persisted tables with real denominators.
    Strictly separates demo data from real impact totals; formal received mass carries 'received, not recycled' label.
    """
    _, a_headers = admin_user
    c_user, _ = collector_user
    _, facility, _ = recycler_user
    now = datetime.now(timezone.utc)

    # 1. Facility Authorization
    auth = FacilityAuthorization(
        id=uuid.uuid4(),
        facility_id=facility.id,
        route="GENERAL_RECYCLING",
        authority="DPCC",
        reference="DPCC/2026/001",
        status="VALID",
        verification_level="REGISTRY_MATCH",
        reviewer_id=uuid.uuid4(),
        last_verified_at=now
    )
    db.add(auth)

    # 2. Real Lot & Transaction
    real_lot = Lot(
        id=uuid.uuid4(),
        collector_id=c_user.id,
        material_id="MAT-PCB-01",
        regulatory_route="GENERAL_RECYCLING",
        estimated_weight_g=15000,
        status="RECEIVED",
        is_demo=False
    )
    real_offer = Offer(
        id=uuid.uuid4(),
        request_id=uuid.uuid4(),
        lot_id=real_lot.id,
        facility_id=facility.id,
        rate_paise_per_kg=20000,
        condition="INTACT",
        expires_at=now + timedelta(days=2),
        status="ACCEPTED",
        terms_hash="a" * 64
    )
    real_tx = Transaction(
        id=uuid.uuid4(),
        lot_id=real_lot.id,
        collector_id=c_user.id,
        facility_id=facility.id,
        accepted_offer_id=real_offer.id,
        estimated_weight_g=15000,
        agreed_weight_g=15000,
        quoted_total_paise=300000,
        agreed_total_paise=300000,
        lifecycle="CONFIRMED",
        is_demo=False
    )
    real_rev = TermsRevision(
        id=uuid.uuid4(),
        transaction_id=real_tx.id,
        final_material_id="MAT-PCB-01",
        measured_weight_g=15000,
        final_total_paise=300000,
        proposed_by="FACILITY",
        proposed_at=now,
        collector_ack_at=now,
        recycler_ack_at=now,
        terms_hash="a" * 64
    )
    real_ho = Handover(
        id=uuid.uuid4(),
        transaction_id=real_tx.id,
        lot_id=real_lot.id,
        status="CONFIRMED",
        proposed_by=c_user.id,
        proposed_at_client=now,
        proposal_payload_json={"lot_id": str(real_lot.id)},
        proposal_hash="b" * 64,
        agreed_terms_revision_id=real_rev.id,
        public_token_hash="c" * 64
    )
    real_payment = PaymentEntry(
        id=uuid.uuid4(),
        transaction_id=real_tx.id,
        amount_paise=250000,
        method="CASH",
        asserted_by="FACILITY",
        asserted_at=now,
        state="ACKNOWLEDGED",
        counterparty_ack_by=c_user.id
    )

    # 3. Demo Lot & Transaction (must NOT contaminate real formal totals!)
    demo_lot = Lot(
        id=uuid.uuid4(),
        collector_id=c_user.id,
        material_id="MAT-PCB-01",
        regulatory_route="GENERAL_RECYCLING",
        estimated_weight_g=50000,
        status="RECEIVED",
        is_demo=True
    )
    demo_offer = Offer(
        id=uuid.uuid4(),
        request_id=uuid.uuid4(),
        lot_id=demo_lot.id,
        facility_id=facility.id,
        rate_paise_per_kg=20000,
        condition="INTACT",
        expires_at=now + timedelta(days=2),
        status="ACCEPTED",
        terms_hash="d" * 64
    )
    demo_tx = Transaction(
        id=uuid.uuid4(),
        lot_id=demo_lot.id,
        collector_id=c_user.id,
        facility_id=facility.id,
        accepted_offer_id=demo_offer.id,
        estimated_weight_g=50000,
        agreed_weight_g=50000,
        quoted_total_paise=1000000,
        agreed_total_paise=1000000,
        lifecycle="CONFIRMED",
        is_demo=True
    )
    demo_rev = TermsRevision(
        id=uuid.uuid4(),
        transaction_id=demo_tx.id,
        final_material_id="MAT-PCB-01",
        measured_weight_g=50000,
        final_total_paise=1000000,
        proposed_by="FACILITY",
        proposed_at=now,
        collector_ack_at=now,
        recycler_ack_at=now,
        terms_hash="d" * 64
    )
    demo_ho = Handover(
        id=uuid.uuid4(),
        transaction_id=demo_tx.id,
        lot_id=demo_lot.id,
        status="CONFIRMED",
        proposed_by=c_user.id,
        proposed_at_client=now,
        proposal_payload_json={"lot_id": str(demo_lot.id)},
        proposal_hash="e" * 64,
        agreed_terms_revision_id=demo_rev.id,
        public_token_hash="f" * 64
    )

    db.add_all([
        real_lot, real_offer, real_tx, real_rev, real_ho, real_payment,
        demo_lot, demo_offer, demo_tx, demo_rev, demo_ho
    ])
    db.commit()

    resp = client.get("/api/v1/admin/overview?include_demo=false", headers=a_headers)
    assert resp.status_code == 200
    data = resp.json()

    # Collectors & Facilities
    assert data["collectors"]["total_registered"] >= 1
    assert data["facilities"]["verified_facilities"] >= 1

    # Demo lot is reported in demo_lots_count, not in total_lots when include_demo=false
    assert data["lots"]["total_lots"] == 1
    assert data["lots"]["demo_lots_count"] == 1

    # Handovers & Received Mass
    # Real mass is strictly 15,000g, NOT 65,000g (demo isolated!)
    assert data["handovers"]["formal_received_mass_g"] == 15000
    assert data["handovers"]["demo_mass_g"] == 50000
    assert data["handovers"]["mass_label"] == "received, not recycled"

    # Financials
    assert data["financials"]["gross_agreed_paise"] == 300000
    assert data["financials"]["acknowledged_paid_paise"] == 250000
    assert data["financials"]["outstanding_dues_paise"] == 50000

    # Honest Fieldwork Provenance
    assert data["unmet_fieldwork_obligation"] == "UNMET"

    # Check /api/v1/admin/metrics returns live table counts
    metrics_resp = client.get("/api/v1/admin/metrics", headers=a_headers)
    assert metrics_resp.status_code == 200
    metrics_data = metrics_resp.json()
    assert metrics_data["verified_facilities"] >= 1
    assert metrics_data["recorded_transactions"] >= 1
    assert metrics_data["unmet_fieldwork_obligation"] == "UNMET"

    # Clean up test entities so other tests have clean tables
    db.query(PaymentEntry).filter(PaymentEntry.transaction_id.in_([real_tx.id, demo_tx.id])).delete()
    db.query(Handover).filter(Handover.transaction_id.in_([real_tx.id, demo_tx.id])).delete()
    db.query(TermsRevision).filter(TermsRevision.transaction_id.in_([real_tx.id, demo_tx.id])).delete()
    db.query(Transaction).filter(Transaction.id.in_([real_tx.id, demo_tx.id])).delete()
    db.query(Offer).filter(Offer.id.in_([real_offer.id, demo_offer.id])).delete()
    db.query(Lot).filter(Lot.id.in_([real_lot.id, demo_lot.id])).delete()
    db.query(FacilityAuthorization).filter(FacilityAuthorization.id == auth.id).delete()
    db.commit()


# =============================================================================
# 3. Collector Minimal Profiles & Sensitive Audit (R-ADMIN-04)
# =============================================================================

def test_collector_minimal_directory_and_access_audit(
    client: TestClient,
    admin_user,
    collector_user,
    db: Session
):
    """
    R-ADMIN-04: Minimal collector view protects privacy, emits audit event, and avoids PII leaks.
    """
    admin, a_headers = admin_user
    c_user, _ = collector_user

    resp = client.get("/api/v1/admin/collectors", headers=a_headers)
    assert resp.status_code == 200
    collectors = resp.json()
    assert len(collectors) >= 1

    target = next((c for c in collectors if c["id"] == str(c_user.id)), None)
    assert target is not None
    assert target["display_alias"] == "Santosh_Kabadi"
    assert target["preferred_language"] == "hi"
    assert target["general_area"] == "Mayapuri"

    # Zero PII leakage verification
    assert "phone" not in target
    assert "phone_normalized" not in target
    assert "pin_hash" not in target
    assert "token" not in target

    # Sensitive access audit verification
    audit_ev = db.query(DomainEvent).filter(
        DomainEvent.event_type == "COLLECTOR_DIRECTORY_ACCESSED",
        DomainEvent.actor_id == admin.id
    ).first()
    assert audit_ev is not None
    assert audit_ev.payload_json["result_count"] >= 1


# =============================================================================
# 4. Material Catalog & Alias Maintenance (R-ADMIN-03, AT-064)
# =============================================================================

def test_admin_material_catalog_crud_and_preservation(
    client: TestClient,
    admin_user,
    db: Session
):
    """
    R-ADMIN-03 / AT-064: Material catalog CRUD preserves historical material IDs
    and emits hash-chained audit events.
    """
    admin, a_headers = admin_user

    # 1. Create new material
    create_payload = {
        "id": "MAT-PCB-TEST",
        "category_id": "PCB",
        "subcategory_code": "HIGH_GRADE_SERVER",
        "description_key": "material.pcb.server_boards",
        "allowed_units": "kg,g",
        "default_route": "AUTHORIZED_EWASTE",
        "route_requires_context": False,
        "condition_options": ["INTACT", "BURNED"],
        "safety_guide_ids": ["SG-EWASTE-01"]
    }
    resp = client.post("/api/v1/admin/materials", json=create_payload, headers=a_headers)
    assert resp.status_code == 201
    mat_data = resp.json()
    assert mat_data["id"] == "MAT-PCB-TEST"
    assert mat_data["active"] is True

    # Duplicate rejected
    resp_dup = client.post("/api/v1/admin/materials", json=create_payload, headers=a_headers)
    assert resp_dup.status_code == 409

    # Verify event emitted
    ev_create = db.query(DomainEvent).filter(
        DomainEvent.aggregate_id == uuid.uuid5(ADMIN_UUID_NAMESPACE, "MAT-PCB-TEST"),
        DomainEvent.event_type == "MATERIAL_CREATED"
    ).first()
    assert ev_create is not None
    assert ev_create.actor_id == admin.id

    # 2. Update material (deactivate / change description)
    update_payload = {
        "description_key": "material.pcb.server_boards_v2",
        "active": False
    }
    resp_patch = client.patch(f"/api/v1/admin/materials/MAT-PCB-TEST", json=update_payload, headers=a_headers)
    assert resp_patch.status_code == 200
    patched_data = resp_patch.json()
    assert patched_data["active"] is False
    assert patched_data["description_key"] == "material.pcb.server_boards_v2"
    # Material ID is strictly retained
    assert patched_data["id"] == "MAT-PCB-TEST"

    # Verify update event emitted
    ev_update = db.query(DomainEvent).filter(
        DomainEvent.aggregate_id == uuid.uuid5(ADMIN_UUID_NAMESPACE, "MAT-PCB-TEST"),
        DomainEvent.event_type == "MATERIAL_UPDATED"
    ).first()
    assert ev_update is not None

    # Cleanup created material
    db.query(Material).filter(Material.id == "MAT-PCB-TEST").delete()
    db.commit()


def test_admin_material_alias_management(
    client: TestClient,
    admin_user,
    db: Session
):
    """
    R-ADMIN-03: Material alias addition with normalization and deletion.
    """
    admin, a_headers = admin_user

    # Add alias
    alias_payload = {
        "material_id": "MAT-PCB-01",
        "language": "hi",
        "local_term": "पुराना कंप्यूटर बोर्ड"
    }
    resp = client.post("/api/v1/admin/material-aliases", json=alias_payload, headers=a_headers)
    assert resp.status_code == 201
    data = resp.json()
    alias_id = data["id"]
    assert data["material_id"] == "MAT-PCB-01"
    assert data["language"] == "hi"
    assert len(data["normalized_term"]) > 0

    # Duplicate alias rejected
    resp_dup = client.post("/api/v1/admin/material-aliases", json=alias_payload, headers=a_headers)
    assert resp_dup.status_code == 409

    # Verify creation event
    ev = db.query(DomainEvent).filter(
        DomainEvent.aggregate_id == uuid.uuid5(ADMIN_UUID_NAMESPACE, "MAT-PCB-01"),
        DomainEvent.event_type == "MATERIAL_ALIAS_CREATED"
    ).first()
    assert ev is not None
    assert ev.payload_json["alias_id"] == alias_id

    # Delete alias
    resp_del = client.delete(f"/api/v1/admin/material-aliases/{alias_id}", headers=a_headers)
    assert resp_del.status_code == 200

    # Verify deletion event
    ev_del = db.query(DomainEvent).filter(
        DomainEvent.aggregate_id == uuid.uuid5(ADMIN_UUID_NAMESPACE, "MAT-PCB-01"),
        DomainEvent.event_type == "MATERIAL_ALIAS_DELETED"
    ).first()
    assert ev_del is not None
    assert ev_del.payload_json["alias_id"] == alias_id


# =============================================================================
# 5. Safety Guide Maintenance (R-ADMIN-03)
# =============================================================================

def test_admin_safety_guide_maintenance(
    client: TestClient,
    admin_user,
    db: Session
):
    """
    R-ADMIN-03: Contextual safety guide creation, review status update, and audit tracking.
    """
    admin, a_headers = admin_user

    # Create safety guide
    guide_payload = {
        "id": "SG-BATTERY-LITHIUM-TEST",
        "material_ids": ["MAT-BAT-02"],
        "route": "BATTERY_ISOLATION",
        "text_key": "safety.battery.lithium_hazard",
        "icon_asset_ref": "icons/safety_li_ion.svg",
        "audio_keys": {"en": "audio/safety_li_en.mp3", "hi": "audio/safety_li_hi.mp3", "mr": "audio/safety_li_mr.mp3"},
        "source_ids": ["SRC-REG-01"],
        "version": "v1.0",
        "review_status": "APPROVED"
    }
    resp = client.post("/api/v1/admin/safety-guides", json=guide_payload, headers=a_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] == "SG-BATTERY-LITHIUM-TEST"
    assert data["review_status"] == "APPROVED"

    # List safety guides
    resp_list = client.get("/api/v1/admin/safety-guides?review_status=APPROVED", headers=a_headers)
    assert resp_list.status_code == 200
    assert any(g["id"] == "SG-BATTERY-LITHIUM-TEST" for g in resp_list.json())

    # Update safety guide
    update_payload = {
        "version": "v1.1",
        "audio_keys": {"en": "audio/safety_li_en.mp3", "hi": "audio/safety_li_hi.mp3", "mr": "audio/safety_li_mr.mp3"}
    }
    resp_patch = client.patch(
        "/api/v1/admin/safety-guides/SG-BATTERY-LITHIUM-TEST",
        json=update_payload,
        headers=a_headers
    )
    assert resp_patch.status_code == 200
    assert resp_patch.json()["version"] == "v1.1"

    # Verify update event
    ev = db.query(DomainEvent).filter(
        DomainEvent.aggregate_id == uuid.uuid5(ADMIN_UUID_NAMESPACE, "SG-BATTERY-LITHIUM-TEST"),
        DomainEvent.event_type == "SAFETY_GUIDE_UPDATED"
    ).first()
    assert ev is not None

    # Cleanup created guide
    db.query(SafetyGuide).filter(SafetyGuide.id == "SG-BATTERY-LITHIUM-TEST").delete()
    db.commit()


# =============================================================================
# 6. Facility Verification Review (R-ADMIN-01, AT-064)
# =============================================================================

def test_facility_verification_review_asserts_evidence(
    client: TestClient,
    admin_user,
    recycler_user,
    db: Session
):
    """
    R-ADMIN-01 / AT-064: Admin records verified authorization evidence for a facility.
    Requires justification reason; creates auditable FacilityAuthorization record rather than arbitrary badge.
    """
    admin, a_headers = admin_user
    _, facility, _ = recycler_user
    now = datetime.now(timezone.utc)

    # Attempt without sufficient reason (< 5 chars)
    bad_payload = {
        "route": "AUTHORIZED_EWASTE",
        "authority": "CPCB",
        "reference": "CPCB/EW/VALID/2026",
        "reason": "bad"
    }
    resp_bad = client.post(
        f"/api/v1/admin/facilities/{facility.id}/verification",
        json=bad_payload,
        headers=a_headers
    )
    assert resp_bad.status_code in (400, 422)

    # Valid assertion
    good_payload = {
        "route": "AUTHORIZED_EWASTE",
        "authority": "CPCB",
        "reference": "CPCB/EW/REG/2026/042",
        "status": "VALID",
        "verification_level": "REGISTRY_MATCH",
        "valid_from": now.isoformat(),
        "valid_until": (now + timedelta(days=365)).isoformat(),
        "source_id": "SRC-FACILITY-CPCB",
        "scope_notes": "Authorized for dismantling electronics up to 500 MT/year",
        "reason": "Matched against official CPCB online EPR authorization portal"
    }
    resp = client.post(
        f"/api/v1/admin/facilities/{facility.id}/verification",
        json=good_payload,
        headers=a_headers
    )
    assert resp.status_code == 201
    auth_data = resp.json()
    assert auth_data["facility_id"] == str(facility.id)
    assert auth_data["status"] == "VALID"
    assert auth_data["reviewer_id"] == str(admin.id)
    assert "CPCB online EPR" in auth_data["reason"]

    # Verify authorization row in DB
    auth_row = db.query(FacilityAuthorization).filter(
        FacilityAuthorization.facility_id == facility.id,
        FacilityAuthorization.reference == "CPCB/EW/REG/2026/042"
    ).first()
    assert auth_row is not None
    assert auth_row.reviewer_id == admin.id

    # Verify domain event emitted
    ev = db.query(DomainEvent).filter(
        DomainEvent.aggregate_id == facility.id,
        DomainEvent.event_type == "FACILITY_VERIFICATION_ASSERTED"
    ).first()
    assert ev is not None


# =============================================================================
# 7. Domain Event Search & Traceability (R-ADMIN-05, AT-077)
# =============================================================================

def test_event_search_and_lot_traceability(
    client: TestClient,
    admin_user,
    collector_user,
    db: Session
):
    """
    R-ADMIN-05 / AT-077: Event search across types and full lot traceability timeline
    with cryptographic hash chain integrity validation.
    """
    admin, a_headers = admin_user
    c_user, _ = collector_user
    now = datetime.now(timezone.utc)

    # Create lot
    lot = Lot(
        id=uuid.uuid4(),
        collector_id=c_user.id,
        material_id="MAT-PCB-01",
        status="LISTED"
    )
    db.add(lot)
    db.commit()

    # Create sequence of domain events for lot
    ev1 = DomainEvent(
        id=uuid.uuid4(),
        aggregate_type="LOT",
        aggregate_id=lot.id,
        sequence=1,
        event_type="LOT_CREATED",
        actor_id=c_user.id,
        role="COLLECTOR",
        received_at_server=now,
        payload_json={"lot_id": str(lot.id)},
        prev_hash="GENESIS",
        event_hash="hash_lot_1"
    )
    ev2 = DomainEvent(
        id=uuid.uuid4(),
        aggregate_type="LOT",
        aggregate_id=lot.id,
        sequence=2,
        event_type="LOT_ESTIMATED",
        actor_id=c_user.id,
        role="COLLECTOR",
        received_at_server=now + timedelta(seconds=10),
        payload_json={"lot_id": str(lot.id), "weight_g": 5000},
        prev_hash="hash_lot_1",
        event_hash="hash_lot_2"
    )
    db.add_all([ev1, ev2])
    db.commit()

    # 1. Search domain events
    resp_search = client.get(
        "/api/v1/admin/events",
        params={
            "aggregate_type": "LOT",
            "occurred_from": now.isoformat(),
            "occurred_to": (now + timedelta(seconds=20)).isoformat(),
        },
        headers=a_headers,
    )
    assert resp_search.status_code == 200
    events_data = resp_search.json()
    assert len(events_data) >= 2

    # 2. Get lot traceability report
    resp_trace = client.get(f"/api/v1/admin/traceability/{lot.id}", headers=a_headers)
    assert resp_trace.status_code == 200
    trace_data = resp_trace.json()
    assert trace_data["lot_id"] == str(lot.id)
    assert trace_data["events_count"] == 2
    assert trace_data["is_hash_chain_valid"] is True
    assert len(trace_data["events"]) == 2
    assert trace_data["events"][0]["event_type"] == "LOT_CREATED"
    assert trace_data["events"][1]["event_type"] == "LOT_ESTIMATED"


# =============================================================================
# 8. Price Review Moderation (R-PRICE-05, AT-064)
# =============================================================================

def test_price_review_moderation_requires_admin_and_updates_status(
    client: TestClient,
    admin_user,
    recycler_user,
    db: Session
):
    """
    R-PRICE-05 / AT-064: Admin price moderation approves/rejects pending observations.
    Ordinary recycler rejected with 403.
    """
    _, a_headers = admin_user
    _, _, r_headers = recycler_user
    now = datetime.now(timezone.utc)

    # Seed pending price observation
    obs = PriceObservation(
        id=uuid.uuid4(),
        material_id="MAT-PCB-01",
        region_id="DL",
        rate_paise_per_unit=18000,
        unit="KG",
        price_kind="INDICATIVE",
        source_id="SRC-PENDING-01",
        observed_at=now,
        review_status="PENDING_REVIEW",
        is_demo=False
    )
    db.add(obs)
    db.commit()

    # Recycler rejected
    resp_r = client.post(
        f"/api/v1/admin/price-review/{obs.id}/decision",
        json={"decision": "APPROVE", "reason": "Recycler is not an authorized reviewer"},
        headers=r_headers
    )
    assert resp_r.status_code == 403

    # Admin approves
    resp_a = client.post(
        f"/api/v1/admin/price-review/{obs.id}/decision",
        json={"decision": "APPROVE", "reason": "Source and units checked against the submitted evidence"},
        headers=a_headers
    )
    assert resp_a.status_code == 200
    assert resp_a.json()["review_status"] == "VERIFIED"

    # Verify in DB
    db.refresh(obs)
    assert obs.review_status == "VERIFIED"
    event = db.query(DomainEvent).filter(
        DomainEvent.aggregate_id == obs.id,
        DomainEvent.event_type == "PRICE_OBSERVATION_REVIEWED",
    ).one()
    assert event.payload_json["decision"] == "APPROVE"

    missing_reason = client.post(
        f"/api/v1/admin/price-review/{obs.id}/decision",
        json={"decision": "REJECT"},
        headers=a_headers,
    )
    assert missing_reason.status_code == 422
