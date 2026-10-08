"""Comprehensive unit tests for QUALITY_V1 data quality and anomaly rules.
Technical specification: docs/03_TECHSPEC.md lines 85-100, docs/MONITORING.md, docs/16_API_CONTRACT.md lines 84-87.
Requirements: R-PRICE-05, R-HAND-05, R-ADMIN-02, R-OPS-04.
Acceptance cases: AT-020, AT-033, AT-065, AT-077.
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
from app.db.models.facility import Facility, FacilityUser, Region
from app.db.models.lot import Lot
from app.db.models.trade import LotRequest, Offer, Transaction, Handover, TermsRevision
from app.domain.quality import (
    POLICY_VERSION,
    QualitySeverity,
    QualityFlagStatus,
    RULE_PRICE_OUTLIER,
    RULE_WEIGHT_VARIANCE,
    RULE_LARGE_WEIGHT,
    RULE_DUPLICATE_MEDIA,
    RULE_REPEATED_SALE,
    RULE_STALE_EVIDENCE,
    RULE_INCOMPLETE_HANDOVER,
    RULE_MISSING_INVALID,
    evaluate_price_quote,
    evaluate_weight_variance,
    evaluate_large_weight,
    evaluate_duplicate_media,
    evaluate_repeated_sale,
    evaluate_stale_evidence,
    evaluate_handover_completeness,
    evaluate_missing_invalid,
)
from app.db.seeds.materials import seed_materials
from app.security import UserRole, create_access_token
from tests.test_db import TestingSessionLocal, override_get_db

@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_quality_module():
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
        phone_normalized="+919876543000",
        pin_hash="pin_admin_hash",
        role=UserRole.ADMIN.value,
        account_state="ACTIVE",
        is_demo=False
    )
    db.add(user)
    db.commit()
    token = create_access_token(subject=str(user.id), role=user.role, is_demo=False)
    headers = {"Authorization": f"Bearer {token}"}
    return user, headers


@pytest.fixture
def collector_user(db: Session):
    """Create a collector user and return (user, auth_headers)."""
    user = User(
        id=uuid.uuid4(),
        phone_normalized="+919876543001",
        pin_hash="pin_collector_hash",
        role=UserRole.COLLECTOR.value,
        account_state="ACTIVE",
        is_demo=False
    )
    collector = Collector(
        id=user.id,
        user_id=user.id,
        display_alias="Ramesh_Collector",
        preferred_language="hi",
        general_area="Mayapuri",
        consent_version="v1.0"
    )
    db.add_all([user, collector])
    db.commit()
    token = create_access_token(subject=str(user.id), role=user.role, is_demo=False)
    headers = {"Authorization": f"Bearer {token}"}
    return user, headers


@pytest.fixture
def recycler_user(db: Session):
    """Create a recycler facility and user, returning (user, facility, auth_headers)."""
    user = User(
        id=uuid.uuid4(),
        phone_normalized="+919876543002",
        pin_hash="pin_recycler_hash",
        role=UserRole.RECYCLER.value,
        account_state="ACTIVE",
        is_demo=False
    )
    facility = Facility(
        id=uuid.uuid4(),
        name="Mayapuri Green Recyclers",
        facility_name="Mayapuri Green Recyclers Pvt Ltd",
        kind="RECYCLER",
        address_public="Mayapuri Phase II, New Delhi",
        district="West Delhi",
        state="Delhi",
        region_id="DELHI_NCR",
        active=True,
        version=1
    )
    fu = FacilityUser(
        facility_id=facility.id,
        user_id=user.id,
        membership_role="MANAGER"
    )
    db.add_all([user, facility, fu])
    db.commit()
    token = create_access_token(subject=str(user.id), role=user.role, is_demo=False)
    headers = {"Authorization": f"Bearer {token}"}
    return user, facility, headers


# =============================================================================
# 1. Pure Domain Rule Unit Tests
# =============================================================================

def test_price_outlier_insufficient_data():
    """AT-020: < 5 comparable observations does not flag quote as outlier."""
    res = evaluate_price_quote(rate_paise_per_unit=50000, comparable_rates=[10000, 12000, 11000])
    assert res.passed is True
    assert res.rule_id == RULE_PRICE_OUTLIER
    assert "Insufficient" in res.reason


def test_price_outlier_iqr_bounds():
    """AT-020: >= 5 observations with IQR > 0 flags outliers beyond 1.5*IQR."""
    # Cohort: 100, 105, 110, 115, 120
    # Q1 ~ 105, Median ~ 110, Q3 ~ 115, IQR ~ 10
    # Bounds: [105 - 15 = 90, 115 + 15 = 130]
    cohort = [100, 105, 110, 115, 120]

    # Within bounds
    assert evaluate_price_quote(110, cohort).passed is True
    assert evaluate_price_quote(125, cohort).passed is True

    # High outlier: 200
    res_high = evaluate_price_quote(200, cohort)
    assert res_high.passed is False
    assert res_high.severity == QualitySeverity.MEDIUM
    assert "outside IQR bounds" in res_high.reason
    assert "does not accuse fraud" in res_high.reason

    # Low outlier: 50
    res_low = evaluate_price_quote(50, cohort)
    assert res_low.passed is False
    assert res_low.severity == QualitySeverity.MEDIUM
    assert "outside IQR bounds" in res_low.reason


def test_price_outlier_zero_iqr():
    """AT-020: Zero IQR cohort uses 30% median tolerance bounds."""
    cohort = [100, 100, 100, 100, 100]  # Median = 100, IQR = 0
    # 30% bounds: [70, 130]
    assert evaluate_price_quote(100, cohort).passed is True
    assert evaluate_price_quote(95, cohort).passed is True
    assert evaluate_price_quote(120, cohort).passed is True

    # Outside bounds
    res = evaluate_price_quote(140, cohort)
    assert res.passed is False
    assert "outside 30% median bounds" in res.reason


def test_weight_variance_rule():
    """AT-033: Weight difference > 20% triggers review; <= 20% passes."""
    # 10% variance (1000g vs 1100g) -> pass
    res_pass = evaluate_weight_variance(1000, 1100)
    assert res_pass.passed is True
    assert res_pass.details["variance_ratio"] == 0.1

    # 25% variance (1000g vs 1250g) -> review flag
    res_fail = evaluate_weight_variance(1000, 1250)
    assert res_fail.passed is False
    assert res_fail.rule_id == RULE_WEIGHT_VARIANCE
    assert res_fail.severity == QualitySeverity.MEDIUM
    assert "25.0% exceeds 20% baseline" in res_fail.reason
    assert "neither party's original measurement overwritten" in res_fail.reason


def test_large_weight_rule():
    """AT-013: Suspicious weight > 500kg flags for review without rejection."""
    assert evaluate_large_weight(300_000).passed is True

    res = evaluate_large_weight(600_000)
    assert res.passed is False
    assert res.rule_id == RULE_LARGE_WEIGHT
    assert "exceeds 500kg threshold" in res.reason


def test_duplicate_media_rule():
    """Same media SHA-256 in distinct active lot flags for review."""
    lot_a = uuid.uuid4()
    lot_b = uuid.uuid4()
    sha = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    # Only in lot_a
    assert evaluate_duplicate_media(sha, lot_a, [lot_a]).passed is True

    # Referenced in lot_b as well
    res = evaluate_duplicate_media(sha, lot_a, [lot_a, lot_b])
    assert res.passed is False
    assert res.rule_id == RULE_DUPLICATE_MEDIA
    assert "not proof of duplicate material or fraud" in res.reason


def test_repeated_sale_rule():
    """AT-028: Conflicting active transaction triggers repeated sale anomaly."""
    lot_id = uuid.uuid4()
    assert evaluate_repeated_sale(lot_id, active_transaction_count=0).passed is True

    res = evaluate_repeated_sale(lot_id, active_transaction_count=1)
    assert res.passed is False
    assert res.rule_id == RULE_REPEATED_SALE
    assert res.severity == QualitySeverity.HIGH


def test_stale_evidence_rule():
    """Expired legal authorization or evidence > 365 days triggers flag."""
    now = datetime.now(timezone.utc)

    # Valid future authorization
    res_valid = evaluate_stale_evidence(
        evidence_date=now - timedelta(days=30),
        valid_until=now + timedelta(days=60),
        now=now
    )
    assert res_valid.passed is True

    # Expired authorization
    res_expired = evaluate_stale_evidence(
        evidence_date=now - timedelta(days=300),
        valid_until=now - timedelta(days=5),
        now=now
    )
    assert res_expired.passed is False
    assert res_expired.rule_id == RULE_STALE_EVIDENCE
    assert res_expired.severity == QualitySeverity.HIGH
    assert "authorization expired" in res_expired.reason

    # Stale evidence age > 365 days
    res_stale = evaluate_stale_evidence(
        evidence_date=now - timedelta(days=400),
        valid_until=now + timedelta(days=100),
        now=now
    )
    assert res_stale.passed is False
    assert res_stale.severity == QualitySeverity.MEDIUM
    assert "exceeds 365-day" in res_stale.reason


def test_handover_completeness_rule():
    """Incomplete handover cannot be confirmed complete."""
    assert evaluate_handover_completeness(True, True, True).passed is True

    res = evaluate_handover_completeness(False, True, True)
    assert res.passed is False
    assert res.rule_id == RULE_INCOMPLETE_HANDOVER
    assert "counterparty_confirmation" in res.details["missing_fields"]


def test_missing_invalid_rule():
    """Block structurally impossible submissions."""
    assert evaluate_missing_invalid(weight_g=5000, amount_paise=10000).passed is True

    res_neg_wt = evaluate_missing_invalid(weight_g=-10)
    assert res_neg_wt.passed is False
    assert res_neg_wt.severity == QualitySeverity.CRITICAL

    res_neg_amt = evaluate_missing_invalid(amount_paise=-500)
    assert res_neg_amt.passed is False
    assert res_neg_amt.severity == QualitySeverity.CRITICAL


# =============================================================================
# 2. Admin Quality Flags API Tests (R-ADMIN-02 / AT-065)
# =============================================================================

def test_admin_quality_flags_unauthorized(client: TestClient, collector_user):
    """Non-admin users cannot access admin quality endpoints (HTTP 403)."""
    _, headers = collector_user
    resp = client.get("/api/v1/admin/quality-flags", headers=headers)
    assert resp.status_code == 403


def test_admin_quality_flags_listing_and_filtering(client: TestClient, admin_user, db: Session):
    """Admin can list and filter quality review flags under QUALITY_V1."""
    _, headers = admin_user
    now = datetime.now(timezone.utc)

    # Seed two quality flags
    flag1 = QualityFlag(
        id=uuid.uuid4(),
        entity_type="OFFER",
        entity_id=uuid.uuid4(),
        entity_version=1,
        rule_id="DQ-PRICE-OUTLIER",
        policy_version="QUALITY_V1",
        severity="MEDIUM",
        evidence_json={"rate": 99999},
        status="OPEN",
        reason="Quote outside IQR bounds",
        created_at=now,
        updated_at=now
    )
    flag2 = QualityFlag(
        id=uuid.uuid4(),
        entity_type="HANDOVER",
        entity_id=uuid.uuid4(),
        entity_version=1,
        rule_id="DQ-WEIGHT-VARIANCE",
        policy_version="QUALITY_V1",
        severity="HIGH",
        evidence_json={"variance_pct": 35.0},
        status="OPEN",
        reason="Weight variance 35% exceeds tolerance",
        created_at=now,
        updated_at=now
    )
    db.add_all([flag1, flag2])
    db.commit()

    # Query all
    resp = client.get("/api/v1/admin/quality-flags", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2

    # Filter by rule_id
    resp_rule = client.get("/api/v1/admin/quality-flags?rule_id=DQ-PRICE-OUTLIER", headers=headers)
    assert resp_rule.status_code == 200
    rule_data = resp_rule.json()
    assert all(item["rule_id"] == "DQ-PRICE-OUTLIER" for item in rule_data)

    # Filter by entity_type
    resp_entity = client.get("/api/v1/admin/quality-flags?entity_type=HANDOVER", headers=headers)
    assert resp_entity.status_code == 200
    entity_data = resp_entity.json()
    assert all(item["entity_type"] == "HANDOVER" for item in entity_data)


def test_admin_quality_summary_metrics(client: TestClient, admin_user, db: Session):
    """AT-065: Quality summary returns counts with real query evidence and denominators."""
    _, headers = admin_user
    now = datetime.now(timezone.utc)

    flag = QualityFlag(
        id=uuid.uuid4(),
        entity_type="LOT",
        entity_id=uuid.uuid4(),
        entity_version=1,
        rule_id="DQ-LARGE-WEIGHT",
        policy_version="QUALITY_V1",
        severity="MEDIUM",
        evidence_json={"weight_g": 600000},
        status="OPEN",
        reason="Large weight anomaly",
        created_at=now,
        updated_at=now
    )
    db.add(flag)
    db.commit()

    resp = client.get("/api/v1/admin/quality-flags/summary", headers=headers)
    assert resp.status_code == 200
    summary = resp.json()
    assert summary["policy_version"] == "QUALITY_V1"
    assert summary["total_flags"] >= 1
    assert "status_counts" in summary
    assert "severity_counts" in summary
    assert "open_fraction" in summary
    assert "resolved_fraction" in summary
    assert summary["open_fraction"] > 0.0


def test_admin_resolve_and_dismiss_quality_flag(client: TestClient, admin_user, db: Session):
    """AT-065: Admin can resolve, acknowledge, or dismiss a flag with mandatory justification."""
    admin, headers = admin_user
    now = datetime.now(timezone.utc)

    flag = QualityFlag(
        id=uuid.uuid4(),
        entity_type="LOT",
        entity_id=uuid.uuid4(),
        entity_version=1,
        rule_id="DQ-LARGE-WEIGHT",
        policy_version="QUALITY_V1",
        severity="MEDIUM",
        evidence_json={"weight_g": 650000},
        status="OPEN",
        reason="Large weight anomaly flagged for review",
        created_at=now,
        updated_at=now
    )
    db.add(flag)
    db.commit()

    # Dismissal without reason rejected (HTTP 400 or 422)
    resp_empty = client.post(
        f"/api/v1/admin/quality-flags/{flag.id}/resolve",
        json={"decision": "DISMISS", "reason": ""},
        headers=headers
    )
    assert resp_empty.status_code in (400, 422)

    # Valid dismissal with reason
    resp_dismiss = client.post(
        f"/api/v1/admin/quality-flags/{flag.id}/resolve",
        json={"decision": "DISMISS", "reason": "Verified industrial bulk disposal agreement with NDMC aggregator"},
        headers=headers
    )
    assert resp_dismiss.status_code == 200
    dismiss_data = resp_dismiss.json()
    assert dismiss_data["status"] == "DISMISSED"
    assert dismiss_data["resolved_by"] == str(admin.id)
    assert "Verified industrial bulk" in dismiss_data["reason"]

    # Verify domain event emitted
    ev = db.query(DomainEvent).filter(
        DomainEvent.aggregate_id == flag.id,
        DomainEvent.event_type == "QUALITY_FLAG_DISMISSED"
    ).first()
    assert ev is not None
    assert ev.payload_json["decision"] == "DISMISS"


def test_on_demand_evaluate_endpoint(client: TestClient, admin_user):
    """POST /api/v1/admin/quality-flags/evaluate evaluates entity without persisting."""
    _, headers = admin_user

    # Evaluate weight variance
    resp = client.post(
        "/api/v1/admin/quality-flags/evaluate",
        json={
            "entity_type": "HANDOVER",
            "estimated_weight_g": 1000,
            "received_weight_g": 1350
        },
        headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["passed"] is False
    assert data["rule_id"] == "DQ-WEIGHT-VARIANCE"
    assert data["severity"] == "MEDIUM"


# =============================================================================
# 3. Operational Integration Tests (AT-020, AT-033, AT-028)
# =============================================================================

def test_trade_offer_price_outlier_flagging_without_blocking(
    client: TestClient,
    collector_user,
    recycler_user,
    db: Session
):
    """
    AT-020: Known high quote triggers DQ-PRICE-OUTLIER QualityFlag when >= 5 comparable observations exist.
    Offer creation succeeds without blocking collector choice or accusing fraud.
    """
    collector, c_headers = collector_user
    recycler, facility, r_headers = recycler_user
    now = datetime.now(timezone.utc)

    # Seed 5 eligible PRICE_V1 observations for the exact offer cohort.
    for i, rate in enumerate([9500, 10000, 10200, 10500, 11000]):
        obs = PriceObservation(
            id=uuid.uuid4(),
            material_id="MAT-PCB-01",
            region_id=facility.region_id,
            rate_paise_per_unit=rate,
            unit="KG",
            price_kind="BUY",
            condition="INTACT",
            source_id=f"SRC-COMP-{i}",
            observed_at=now - timedelta(days=2),
            review_status="VERIFIED",
            is_demo=False
        )
        db.add(obs)

    # These records must not enter the benchmark: they are respectively
    # unreviewed, stale, a different price kind, and a different condition.
    # If they were included, their high values would suppress the true outlier.
    for i, overrides in enumerate([
        {"review_status": "PENDING_REVIEW"},
        {"observed_at": now - timedelta(days=31)},
        {"price_kind": "QUOTE"},
        {"condition": "SCRAP"},
    ]):
        values = {
            "id": uuid.uuid4(), "material_id": "MAT-PCB-01", "region_id": facility.region_id,
            "rate_paise_per_unit": 50000, "unit": "KG", "price_kind": "BUY",
            "condition": "INTACT", "source_id": f"SRC-INELIGIBLE-{i}",
            "observed_at": now - timedelta(days=2), "review_status": "VERIFIED", "is_demo": False,
        }
        values.update(overrides)
        db.add(PriceObservation(**values))

    # Create lot and request
    lot = Lot(
        id=uuid.uuid4(),
        collector_id=collector.id,
        material_id="MAT-PCB-01",
        regulatory_route="GENERAL_RECYCLING",
        estimated_weight_g=5000,
        status="LISTED",
        version=1,
        is_demo=False
    )
    lot_req = LotRequest(
        id=uuid.uuid4(),
        lot_id=lot.id,
        facility_id=facility.id,
        created_by=collector.id,
        state="PENDING"
    )
    db.add_all([lot, lot_req])
    db.commit()

    # Recycler quotes an extreme outlier rate (50,000 paise/kg vs ~10,000 baseline)
    offer_payload = {
        "price_basis": "RATE_PER_KG",
        "rate_paise_per_kg": 50000,
        "condition": "INTACT",
        "expires_in_hours": 48
    }
    resp = client.post(
        f"/api/v1/requests/{lot_req.id}/offers",
        json=offer_payload,
        headers=r_headers
    )
    assert resp.status_code == 201
    offer_data = resp.json()
    assert offer_data["status"] == "OPEN"
    assert offer_data["rate_paise_per_kg"] == 50000

    # Verify DQ-PRICE-OUTLIER QualityFlag is logged in DB
    flag = db.query(QualityFlag).filter(
        QualityFlag.entity_type == "OFFER",
        QualityFlag.entity_id == uuid.UUID(offer_data["id"]),
        QualityFlag.rule_id == "DQ-PRICE-OUTLIER"
    ).first()
    assert flag is not None
    assert flag.severity == "MEDIUM"
    assert "outside IQR bounds" in flag.reason
    assert "does not accuse fraud" in flag.reason
    # The suite seeds additional eligible baseline observations. The five
    # observations above must participate, while the deliberately ineligible
    # records remain excluded.
    assert flag.evidence_json["observation_count"] >= 5


def test_handover_weight_discrepancy_logs_quality_flag(
    client: TestClient,
    collector_user,
    recycler_user,
    db: Session
):
    """
    AT-033: Handover confirmation with >20% weight difference triggers TermsRevision
    and records DQ-WEIGHT-VARIANCE QualityFlag for review without overwriting initial facts.
    """
    collector, c_headers = collector_user
    recycler, facility, r_headers = recycler_user
    now = datetime.now(timezone.utc)
    proposal_hash = "a" * 64
    terms_hash = "b" * 64

    # Seed lot, offer, transaction with 10,000g estimated weight
    lot = Lot(
        id=uuid.uuid4(),
        collector_id=collector.id,
        material_id="MAT-PCB-01",
        regulatory_route="GENERAL_RECYCLING",
        estimated_weight_g=10000,
        status="ACCEPTED",
        version=1,
        is_demo=False
    )
    offer = Offer(
        id=uuid.uuid4(),
        request_id=uuid.uuid4(),
        lot_id=lot.id,
        facility_id=facility.id,
        rate_paise_per_kg=10000,
        price_basis="RATE_PER_KG",
        condition="INTACT",
        weight_basis_g=10000,
        expires_at=now + timedelta(days=3),
        status="ACCEPTED",
        terms_hash=terms_hash,
        version=1,
        created_at=now,
        updated_at=now
    )
    tx = Transaction(
        id=uuid.uuid4(),
        lot_id=lot.id,
        collector_id=collector.id,
        facility_id=facility.id,
        accepted_offer_id=offer.id,
        lifecycle="IN_TRANSIT",
        estimated_weight_g=10000,
        agreed_weight_g=10000,
        quoted_total_paise=100000,
        agreed_total_paise=100000,
        currency="INR",
        version=1,
        is_demo=False
    )
    initial_rev = TermsRevision(
        id=uuid.uuid4(),
        transaction_id=tx.id,
        final_material_id="MAT-PCB-01",
        measured_weight_g=10000,
        final_total_paise=100000,
        currency="INR",
        proposed_by="FACILITY",
        proposed_at=now,
        terms_hash=terms_hash,
        collector_ack_at=now,
        recycler_ack_at=now
    )
    handover = Handover(
        id=uuid.uuid4(),
        transaction_id=tx.id,
        lot_id=lot.id,
        status="PENDING_CONFIRMATION",
        proposed_by=collector.id,
        proposed_at_client=now,
        proposal_payload_json={"lot_id": str(lot.id)},
        proposal_hash=proposal_hash,
        agreed_terms_revision_id=initial_rev.id,
        public_token_hash="c" * 64,
        version=1
    )
    db.add_all([lot, offer, tx, initial_rev, handover])
    db.commit()

    # Facility confirms with 13,500g (+35% weight difference)
    confirm_payload = {
        "expected_version": 1,
        "proposal_hash": proposal_hash,
        "measured_material_id": "MAT-PCB-01",
        "measured_weight_g": 13500,
        "final_total_paise": 135000,
        "notes": "Actual weighed scrap on certified weighbridge"
    }
    resp = client.post(
        f"/handovers/{handover.id}/confirm",
        json=confirm_payload,
        headers=r_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "PENDING_COLLECTOR_ACK"

    # Verify QualityFlag for DQ-WEIGHT-VARIANCE is recorded
    flag = db.query(QualityFlag).filter(
        QualityFlag.entity_type == "HANDOVER",
        QualityFlag.entity_id == handover.id,
        QualityFlag.rule_id == "DQ-WEIGHT-VARIANCE"
    ).first()
    assert flag is not None
    assert flag.severity == "MEDIUM"
    assert "35.0% exceeds 20% baseline" in flag.reason


def test_repeated_sale_logs_flag_and_rejects(
    client: TestClient,
    collector_user,
    recycler_user,
    db: Session
):
    """
    AT-028: Attempting to accept a second offer on an already agreed lot rejects with 409
    and logs a DQ-REPEATED-SALE QualityFlag.
    """
    collector, c_headers = collector_user
    recycler, facility, r_headers = recycler_user
    now = datetime.now(timezone.utc)
    terms_hash2 = "e" * 64

    lot = Lot(
        id=uuid.uuid4(),
        collector_id=collector.id,
        material_id="MAT-PCB-01",
        status="ACCEPTED",
        version=2,
        is_demo=False
    )
    existing_offer = Offer(
        id=uuid.uuid4(),
        request_id=uuid.uuid4(),
        lot_id=lot.id,
        facility_id=facility.id,
        rate_paise_per_kg=10000,
        price_basis="RATE_PER_KG",
        condition="INTACT",
        weight_basis_g=10000,
        expires_at=now + timedelta(days=3),
        status="ACCEPTED",
        terms_hash="d" * 64,
        version=1,
        created_at=now,
        updated_at=now
    )
    # Existing active transaction
    existing_tx = Transaction(
        id=uuid.uuid4(),
        lot_id=lot.id,
        collector_id=collector.id,
        facility_id=facility.id,
        accepted_offer_id=existing_offer.id,
        estimated_weight_g=10000,
        agreed_weight_g=10000,
        quoted_total_paise=100000,
        agreed_total_paise=100000,
        currency="INR",
        lifecycle="AGREED",
        version=1,
        is_demo=False
    )
    # Competing offer
    offer2 = Offer(
        id=uuid.uuid4(),
        request_id=uuid.uuid4(),
        lot_id=lot.id,
        facility_id=facility.id,
        rate_paise_per_kg=12000,
        price_basis="RATE_PER_KG",
        condition="INTACT",
        expires_at=now + timedelta(hours=24),
        status="OPEN",
        terms_hash=terms_hash2,
        version=1,
        created_at=now,
        updated_at=now
    )
    db.add_all([lot, existing_offer, existing_tx, offer2])
    db.commit()

    resp = client.post(
        f"/api/v1/offers/{offer2.id}/accept",
        json={"terms_hash": terms_hash2, "expected_version": 1},
        headers=c_headers
    )
    assert resp.status_code == 409
    assert "Lot already has an active accepted agreement" in resp.json()["detail"]

    # Verify DQ-REPEATED-SALE QualityFlag
    flag = db.query(QualityFlag).filter(
        QualityFlag.rule_id == "DQ-REPEATED-SALE"
    ).first()
    assert flag is not None
    assert flag.severity == "HIGH"
    assert str(lot.id) in flag.reason
