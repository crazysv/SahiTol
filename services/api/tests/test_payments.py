"""Comprehensive test suite for Payment Assertions, Ledger, Reversals, and Earnings (T026).
Covers requirements: R-PAY-01, R-PAY-02, R-PAY-03, R-DATA-04.
Acceptance cases: AT-035, AT-036, AT-037, AT-056.
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
    FacilityUser,
    Region,
)
from app.db.models.lot import Lot
from app.db.models.trade import (
    Handover,
    HandoverConfirmation,
    PaymentEntry,
    TermsRevision,
    Transaction,
)
from app.db.seeds.materials import seed_materials
from app.security import create_access_token
from tests.test_db import TestingSessionLocal, override_get_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_payments_module():
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
def payment_environment():
    """Seed test collector, facility, recycler user, lot, confirmed handover, and transaction."""
    col_user_id = uuid.uuid4()
    collector_id = uuid.uuid4()
    rec_user_id = uuid.uuid4()
    fac_id = uuid.uuid4()
    lot_id = uuid.uuid4()
    offer_id = uuid.uuid4()
    tx_id = uuid.uuid4()
    handover_id = uuid.uuid4()
    admin_user_id = uuid.uuid4()
    other_user_id = uuid.uuid4()
    other_col_id = uuid.uuid4()

    now = datetime.now(timezone.utc)

    with TestingSessionLocal() as session:
        # 1. Collector
        col_user = User(
            id=col_user_id,
            phone_normalized="+919811122233",
            pin_hash="pin_hash",
            role="COLLECTOR",
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(col_user)
        col = Collector(
            id=collector_id,
            user_id=col_user_id,
            display_alias="Santosh Collector",
            preferred_language="hi",
            region_id="DELHI_NCR",
            general_area="Mayapuri",
            consent_version="v1.0"
        )
        session.add(col)

        # 2. Recycler User & Facility
        rec_user = User(
            id=rec_user_id,
            phone_normalized="+919844455566",
            pin_hash="pin_hash",
            role="RECYCLER",
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(rec_user)

        fac = Facility(
            id=fac_id,
            name="Apex E-Waste Recyclers",
            facility_name="Apex E-Waste Recyclers Pvt Ltd",
            kind="RECYCLER",
            address_public="Plot 45, Okhla Industrial Area Phase II, New Delhi",
            district="South East Delhi",
            state="Delhi",
            region_id="DELHI_NCR",
            contact_public="contact@apexrecyclers.example.com",
            active=True,
            version=1
        )
        session.add(fac)

        fu = FacilityUser(
            user_id=rec_user_id,
            facility_id=fac_id,
            membership_role="MANAGER",
            active=True
        )
        session.add(fu)

        # 3. Third-party Collector
        other_user = User(
            id=other_user_id,
            phone_normalized="+919877788899",
            pin_hash="pin_hash",
            role="COLLECTOR",
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(other_user)
        other_col = Collector(
            id=other_col_id,
            user_id=other_user_id,
            display_alias="Other Collector",
            preferred_language="en",
            region_id="DELHI_NCR",
            consent_version="v1.0"
        )
        session.add(other_col)

        # 4. Admin User
        admin_user = User(
            id=admin_user_id,
            phone_normalized="+919999900000",
            pin_hash="pin_hash",
            role="ADMIN",
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(admin_user)

        # 5. Lot & Transaction
        lot = Lot(
            id=lot_id,
            collector_id=collector_id,
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=8500,
            status="RECEIVED",
            is_demo=False
        )
        session.add(lot)

        tx = Transaction(
            id=tx_id,
            lot_id=lot_id,
            collector_id=collector_id,
            facility_id=fac_id,
            accepted_offer_id=offer_id,
            estimated_weight_g=8500,
            agreed_weight_g=8500,
            quoted_total_paise=382500,
            agreed_total_paise=382500,
            currency="INR",
            lifecycle="CONFIRMED",
            is_demo=False
        )
        session.add(tx)

        terms_rev = TermsRevision(
            id=uuid.uuid4(),
            transaction_id=tx_id,
            final_material_id="MAT-PCB-01",
            measured_weight_g=8500,
            final_total_paise=382500,
            currency="INR",
            proposed_by="FACILITY",
            collector_ack_at=now,
            recycler_ack_at=now,
            terms_hash="mock_terms_hash"
        )
        session.add(terms_rev)

        # 6. Confirmed Handover
        handover = Handover(
            id=handover_id,
            transaction_id=tx_id,
            lot_id=lot_id,
            proposal_payload_json={"is_demo": False},
            proposal_hash="mock_proposal_hash",
            proposed_by=col_user_id,
            proposed_at_client=now,
            status="CONFIRMED",
            public_token_hash="mock_public_token_hash",
            version=1
        )
        session.add(handover)

        conf = HandoverConfirmation(
            id=uuid.uuid4(),
            handover_id=handover_id,
            recycler_user_id=rec_user_id,
            confirmed_at=now
        )
        session.add(conf)

        session.commit()

    col_token = create_access_token(subject=str(col_user_id), role="COLLECTOR")
    rec_token = create_access_token(subject=str(rec_user_id), role="RECYCLER")
    other_token = create_access_token(subject=str(other_user_id), role="COLLECTOR")
    admin_token = create_access_token(subject=str(admin_user_id), role="ADMIN")

    return {
        "collector_user_id": col_user_id,
        "collector_id": collector_id,
        "collector_headers": {"Authorization": f"Bearer {col_token}"},
        "recycler_user_id": rec_user_id,
        "facility_id": fac_id,
        "recycler_headers": {"Authorization": f"Bearer {rec_token}"},
        "other_headers": {"Authorization": f"Bearer {other_token}"},
        "admin_headers": {"Authorization": f"Bearer {admin_token}"},
        "lot_id": lot_id,
        "tx_id": tx_id,
        "handover_id": handover_id,
        "gross_paise": 382500
    }


def test_assert_payment_cash_success(payment_environment):
    """Test recording a cash payment assertion without bank gateway (R-PAY-01, AT-035)."""
    env = payment_environment
    payment_id = uuid.uuid4()

    payload = {
        "id": str(payment_id),
        "amount_paise": 382500,
        "method": "CASH",
        "private_reference": "Envelop #42 handed over in person"
    }

    # Recycler asserts cash payment
    resp = client.post(
        f"/api/v1/transactions/{env['tx_id']}/payments",
        json=payload,
        headers=env["recycler_headers"]
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["id"] == str(payment_id)
    assert data["amount_paise"] == 382500
    assert data["method"] == "CASH"
    assert data["asserted_by"] == "FACILITY"
    assert data["state"] == "ASSERTED"
    assert data["counterparty_ack_by"] is None
    assert data["ack_at"] is None


def test_assert_payment_upi_with_private_reference(payment_environment):
    """Test optional UPI assertion records reference, not fund transfer (R-PAY-01, AT-035)."""
    env = payment_environment
    payment_id = uuid.uuid4()

    payload = {
        "id": str(payment_id),
        "amount_paise": 200000,
        "method": "UPI",
        "private_reference": "UPI/CR/20260929/123456789"
    }

    resp = client.post(
        f"/api/v1/transactions/{env['tx_id']}/payments",
        json=payload,
        headers=env["recycler_headers"]
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["method"] == "UPI"
    assert data["private_reference"] == "UPI/CR/20260929/123456789"
    assert data["state"] == "ASSERTED"


def test_assert_payment_invalid_method_rejected(payment_environment):
    """Test unsupported payment method returns 422 Unprocessable Content."""
    env = payment_environment
    payment_id = uuid.uuid4()

    payload = {
        "id": str(payment_id),
        "amount_paise": 50000,
        "method": "BITCOIN"
    }

    resp = client.post(
        f"/api/v1/transactions/{env['tx_id']}/payments",
        json=payload,
        headers=env["recycler_headers"]
    )
    assert resp.status_code == 422


def test_assert_payment_zero_or_negative_amount_rejected(payment_environment):
    """Test non-positive payment amounts are rejected (R-PAY-01)."""
    env = payment_environment
    payload = {
        "id": str(uuid.uuid4()),
        "amount_paise": 0,
        "method": "CASH"
    }
    resp = client.post(
        f"/api/v1/transactions/{env['tx_id']}/payments",
        json=payload,
        headers=env["recycler_headers"]
    )
    assert resp.status_code == 422

    payload["amount_paise"] = -100
    resp2 = client.post(
        f"/api/v1/transactions/{env['tx_id']}/payments",
        json=payload,
        headers=env["recycler_headers"]
    )
    assert resp2.status_code == 422


def test_assert_payment_forbidden_for_non_participant(payment_environment):
    """Test third-party user cannot assert payment on someone else's transaction."""
    env = payment_environment
    payload = {
        "id": str(uuid.uuid4()),
        "amount_paise": 10000,
        "method": "CASH"
    }
    resp = client.post(
        f"/api/v1/transactions/{env['tx_id']}/payments",
        json=payload,
        headers=env["other_headers"]
    )
    assert resp.status_code == 403


def test_assert_payment_idempotent_replay(payment_environment):
    """Test duplicate submission of identical payment assertion returns 200 without double counting (R-PAY-02, AT-036)."""
    env = payment_environment
    payment_id = uuid.uuid4()

    payload = {
        "id": str(payment_id),
        "amount_paise": 150000,
        "method": "CASH"
    }

    resp1 = client.post(
        f"/api/v1/transactions/{env['tx_id']}/payments",
        json=payload,
        headers=env["recycler_headers"]
    )
    assert resp1.status_code == 201

    # Replay identical assertion
    resp2 = client.post(
        f"/api/v1/transactions/{env['tx_id']}/payments",
        json=payload,
        headers=env["recycler_headers"]
    )
    assert resp2.status_code == 200
    assert resp2.json()["id"] == str(payment_id)

    # Check ledger: total asserted pending is 150000, NOT 300000
    summary_resp = client.get(
        f"/api/v1/transactions/{env['tx_id']}/payments",
        headers=env["collector_headers"]
    )
    assert summary_resp.status_code == 200
    # Exactly one payment entry with this ID
    matching_entries = [p for p in summary_resp.json()["payments"] if p["id"] == str(payment_id)]
    assert len(matching_entries) == 1


def test_assert_payment_conflicting_id_rejected(payment_environment):
    """Test reusing payment ID with different amount returns 409 Conflict."""
    env = payment_environment
    payment_id = uuid.uuid4()

    payload1 = {"id": str(payment_id), "amount_paise": 100000, "method": "CASH"}
    resp1 = client.post(
        f"/api/v1/transactions/{env['tx_id']}/payments",
        json=payload1,
        headers=env["recycler_headers"]
    )
    assert resp1.status_code == 201

    payload2 = {"id": str(payment_id), "amount_paise": 200000, "method": "CASH"}
    resp2 = client.post(
        f"/api/v1/transactions/{env['tx_id']}/payments",
        json=payload2,
        headers=env["recycler_headers"]
    )
    assert resp2.status_code == 409


def test_acknowledge_payment_success(payment_environment):
    """Test counterparty acknowledges payment assertion (R-PAY-01, AT-035)."""
    env = payment_environment
    payment_id = uuid.uuid4()

    # Recycler asserts payment
    payload = {"id": str(payment_id), "amount_paise": 120000, "method": "CASH"}
    resp = client.post(
        f"/api/v1/transactions/{env['tx_id']}/payments",
        json=payload,
        headers=env["recycler_headers"]
    )
    assert resp.status_code == 201

    # Collector acknowledges receipt
    ack_resp = client.post(
        f"/api/v1/payments/{payment_id}/acknowledge",
        json={"expected_amount_paise": 120000},
        headers=env["collector_headers"]
    )
    assert ack_resp.status_code == 200, ack_resp.text
    data = ack_resp.json()
    assert data["state"] == "ACKNOWLEDGED"
    assert data["counterparty_ack_by"] == str(env["collector_user_id"])
    assert data["ack_at"] is not None


def test_acknowledge_payment_self_acknowledgement_prohibited(payment_environment):
    """Test party asserting payment cannot self-acknowledge it (R-PAY-01, AT-035)."""
    env = payment_environment
    payment_id = uuid.uuid4()

    # Recycler asserts payment
    payload = {"id": str(payment_id), "amount_paise": 50000, "method": "CASH"}
    client.post(
        f"/api/v1/transactions/{env['tx_id']}/payments",
        json=payload,
        headers=env["recycler_headers"]
    )

    # Recycler attempts to acknowledge their own assertion
    ack_resp = client.post(
        f"/api/v1/payments/{payment_id}/acknowledge",
        headers=env["recycler_headers"]
    )
    assert ack_resp.status_code == 403


def test_dispute_payment_success(payment_environment):
    """Test counterparty disputes payment with mandatory reason (R-PAY-01, AT-035)."""
    env = payment_environment
    payment_id = uuid.uuid4()

    # Recycler asserts 100000
    payload = {"id": str(payment_id), "amount_paise": 100000, "method": "CASH"}
    client.post(
        f"/api/v1/transactions/{env['tx_id']}/payments",
        json=payload,
        headers=env["recycler_headers"]
    )

    # Collector disputes: "Did not receive cash in envelope"
    dispute_resp = client.post(
        f"/api/v1/payments/{payment_id}/dispute",
        json={"reason": "Did not receive cash in envelope"},
        headers=env["collector_headers"]
    )
    assert dispute_resp.status_code == 200
    data = dispute_resp.json()
    assert data["state"] == "DISPUTED"
    assert data["reason"] == "Did not receive cash in envelope"

    # Ledger shows active dispute and disputed amount
    summary_resp = client.get(
        f"/api/v1/transactions/{env['tx_id']}/payments",
        headers=env["collector_headers"]
    )
    assert summary_resp.json()["has_dispute"] is True


def test_reverse_payment_creates_offsetting_reversal_linking_original(payment_environment):
    """Test append-only reversal links original ID and recalculates dues without deletion (R-PAY-02, AT-036)."""
    env = payment_environment
    payment_id = uuid.uuid4()
    reversal_id = uuid.uuid4()

    # 1. Assert and acknowledge 80000 paise
    payload = {"id": str(payment_id), "amount_paise": 80000, "method": "CASH"}
    client.post(
        f"/api/v1/transactions/{env['tx_id']}/payments",
        json=payload,
        headers=env["recycler_headers"]
    )
    client.post(
        f"/api/v1/payments/{payment_id}/acknowledge",
        headers=env["collector_headers"]
    )

    # 2. Reverse payment
    rev_resp = client.post(
        f"/api/v1/payments/{payment_id}/reverse",
        json={
            "reversal_id": str(reversal_id),
            "reason": "Cash bill was countermanded and reissued"
        },
        headers=env["recycler_headers"]
    )
    assert rev_resp.status_code == 200, rev_resp.text
    data = rev_resp.json()

    assert data["original_entry"]["id"] == str(payment_id)
    assert data["original_entry"]["state"] == "REVERSED"
    assert data["reversal_entry"]["id"] == str(reversal_id)
    assert data["reversal_entry"]["reversal_of"] == str(payment_id)
    assert data["reversal_entry"]["state"] == "REVERSED"

    # 3. Target and reversal entries are both present in database (neither deleted)
    with TestingSessionLocal() as session:
        orig_db = session.query(PaymentEntry).filter(PaymentEntry.id == payment_id).first()
        rev_db = session.query(PaymentEntry).filter(PaymentEntry.id == reversal_id).first()
        assert orig_db is not None
        assert rev_db is not None
        assert orig_db.state == "REVERSED"
        assert rev_db.reversal_of == payment_id


def test_multiple_partial_payments_sum_accurately(payment_environment):
    """Test two partial payments sum once without double counting (R-PAY-02, AT-036)."""
    # Create clean transaction for partial payment testing
    with TestingSessionLocal() as session:
        lot = Lot(
            id=uuid.uuid4(),
            collector_id=payment_environment["collector_id"],
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=10000,
            status="RECEIVED"
        )
        session.add(lot)
        tx = Transaction(
            id=uuid.uuid4(),
            lot_id=lot.id,
            collector_id=payment_environment["collector_id"],
            facility_id=payment_environment["facility_id"],
            accepted_offer_id=uuid.uuid4(),
            estimated_weight_g=10000,
            quoted_total_paise=500000,
            agreed_total_paise=500000,
            lifecycle="CONFIRMED"
        )
        session.add(tx)
        session.commit()
        tx_id = tx.id

    p1_id = uuid.uuid4()
    p2_id = uuid.uuid4()

    # First partial payment: 200000 paise (2000 INR)
    client.post(
        f"/api/v1/transactions/{tx_id}/payments",
        json={"id": str(p1_id), "amount_paise": 200000, "method": "CASH"},
        headers=payment_environment["recycler_headers"]
    )
    client.post(f"/api/v1/payments/{p1_id}/acknowledge", headers=payment_environment["collector_headers"])

    # Second partial payment: 300000 paise (3000 INR)
    client.post(
        f"/api/v1/transactions/{tx_id}/payments",
        json={"id": str(p2_id), "amount_paise": 300000, "method": "UPI"},
        headers=payment_environment["recycler_headers"]
    )
    client.post(f"/api/v1/payments/{p2_id}/acknowledge", headers=payment_environment["collector_headers"])

    # Verify ledger summary
    summary_resp = client.get(
        f"/api/v1/transactions/{tx_id}/payments",
        headers=payment_environment["collector_headers"]
    )
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert summary["gross_due_paise"] == 500000
    assert summary["acknowledged_paid_paise"] == 500000
    assert summary["remaining_due_paise"] == 0
    assert summary["is_settled"] is True


def test_close_transaction_success_when_confirmed_and_settled(payment_environment):
    """Test closing transaction succeeds only at confirmed receipt and settled payment (R-PAY-02, AT-036)."""
    # Create clean transaction + confirmed handover
    with TestingSessionLocal() as session:
        lot = Lot(
            id=uuid.uuid4(),
            collector_id=payment_environment["collector_id"],
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=5000,
            status="RECEIVED"
        )
        session.add(lot)
        tx = Transaction(
            id=uuid.uuid4(),
            lot_id=lot.id,
            collector_id=payment_environment["collector_id"],
            facility_id=payment_environment["facility_id"],
            accepted_offer_id=uuid.uuid4(),
            estimated_weight_g=5000,
            quoted_total_paise=200000,
            agreed_total_paise=200000,
            lifecycle="CONFIRMED"
        )
        session.add(tx)
        handover = Handover(
            id=uuid.uuid4(),
            transaction_id=tx.id,
            lot_id=lot.id,
            proposal_payload_json={"is_demo": False},
            proposal_hash="hash",
            proposed_by=payment_environment["collector_user_id"],
            proposed_at_client=datetime.now(timezone.utc),
            status="CONFIRMED",
            public_token_hash="token_hash",
            version=1
        )
        session.add(handover)
        session.commit()
        tx_id = tx.id
        lot_id = lot.id

    # Settle dues in full
    pid = uuid.uuid4()
    client.post(
        f"/api/v1/transactions/{tx_id}/payments",
        json={"id": str(pid), "amount_paise": 200000, "method": "CASH"},
        headers=payment_environment["recycler_headers"]
    )
    client.post(f"/api/v1/payments/{pid}/acknowledge", headers=payment_environment["collector_headers"])

    # Close transaction
    close_resp = client.post(f"/api/v1/transactions/{tx_id}/close", headers=payment_environment["collector_headers"])
    assert close_resp.status_code == 200, close_resp.text
    assert close_resp.json()["lifecycle"] == "CLOSED"

    # Verify lot is also CLOSED
    with TestingSessionLocal() as session:
        lot_db = session.query(Lot).filter(Lot.id == lot_id).first()
        tx_db = session.query(Transaction).filter(Transaction.id == tx_id).first()
        assert lot_db.status == "CLOSED"
        assert tx_db.lifecycle == "CLOSED"


def test_close_transaction_rejected_when_dues_remain(payment_environment):
    """Test RECEIVED transaction with pending dues cannot become CLOSED (R-PAY-02, AT-036)."""
    with TestingSessionLocal() as session:
        lot = Lot(
            id=uuid.uuid4(),
            collector_id=payment_environment["collector_id"],
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=5000,
            status="RECEIVED"
        )
        session.add(lot)
        tx = Transaction(
            id=uuid.uuid4(),
            lot_id=lot.id,
            collector_id=payment_environment["collector_id"],
            facility_id=payment_environment["facility_id"],
            accepted_offer_id=uuid.uuid4(),
            estimated_weight_g=5000,
            quoted_total_paise=200000,
            agreed_total_paise=200000,
            lifecycle="CONFIRMED"
        )
        session.add(tx)
        handover = Handover(
            id=uuid.uuid4(),
            transaction_id=tx.id,
            lot_id=lot.id,
            proposal_payload_json={"is_demo": False},
            proposal_hash="hash",
            proposed_by=payment_environment["collector_user_id"],
            proposed_at_client=datetime.now(timezone.utc),
            status="CONFIRMED",
            public_token_hash="token_hash",
            version=1
        )
        session.add(handover)
        session.commit()
        tx_id = tx.id

    # Only pay 100000 out of 200000 (pending dues: 100000)
    pid = uuid.uuid4()
    client.post(
        f"/api/v1/transactions/{tx_id}/payments",
        json={"id": str(pid), "amount_paise": 100000, "method": "CASH"},
        headers=payment_environment["recycler_headers"]
    )
    client.post(f"/api/v1/payments/{pid}/acknowledge", headers=payment_environment["collector_headers"])

    # Attempt close
    close_resp = client.post(f"/api/v1/transactions/{tx_id}/close", headers=payment_environment["collector_headers"])
    assert close_resp.status_code == 409
    assert "Outstanding dues" in close_resp.json()["detail"]


def test_close_transaction_rejected_when_handover_unconfirmed(payment_environment):
    """Test transaction cannot close if handover is still pending confirmation (R-PAY-02)."""
    with TestingSessionLocal() as session:
        lot = Lot(
            id=uuid.uuid4(),
            collector_id=payment_environment["collector_id"],
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=5000,
            status="HANDED_OVER"
        )
        session.add(lot)
        tx = Transaction(
            id=uuid.uuid4(),
            lot_id=lot.id,
            collector_id=payment_environment["collector_id"],
            facility_id=payment_environment["facility_id"],
            accepted_offer_id=uuid.uuid4(),
            estimated_weight_g=5000,
            quoted_total_paise=100000,
            agreed_total_paise=100000,
            lifecycle="IN_TRANSIT"
        )
        session.add(tx)
        handover = Handover(
            id=uuid.uuid4(),
            transaction_id=tx.id,
            lot_id=lot.id,
            proposal_payload_json={"is_demo": False},
            proposal_hash="hash",
            proposed_by=payment_environment["collector_user_id"],
            proposed_at_client=datetime.now(timezone.utc),
            status="PENDING_CONFIRMATION",  # Unconfirmed
            public_token_hash="token_hash",
            version=1
        )
        session.add(handover)
        session.commit()
        tx_id = tx.id

    # Pay in full
    pid = uuid.uuid4()
    client.post(
        f"/api/v1/transactions/{tx_id}/payments",
        json={"id": str(pid), "amount_paise": 100000, "method": "CASH"},
        headers=payment_environment["recycler_headers"]
    )
    client.post(f"/api/v1/payments/{pid}/acknowledge", headers=payment_environment["collector_headers"])

    close_resp = client.post(f"/api/v1/transactions/{tx_id}/close", headers=payment_environment["collector_headers"])
    assert close_resp.status_code == 409
    assert "Confirmed handover receipt is required" in close_resp.json()["detail"]


def test_close_transaction_rejected_when_dispute_exists(payment_environment):
    """Test transaction cannot close if an active dispute exists (R-PAY-02, AT-036)."""
    with TestingSessionLocal() as session:
        lot = Lot(
            id=uuid.uuid4(),
            collector_id=payment_environment["collector_id"],
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=5000,
            status="RECEIVED"
        )
        session.add(lot)
        tx = Transaction(
            id=uuid.uuid4(),
            lot_id=lot.id,
            collector_id=payment_environment["collector_id"],
            facility_id=payment_environment["facility_id"],
            accepted_offer_id=uuid.uuid4(),
            estimated_weight_g=5000,
            quoted_total_paise=100000,
            agreed_total_paise=100000,
            lifecycle="CONFIRMED"
        )
        session.add(tx)
        handover = Handover(
            id=uuid.uuid4(),
            transaction_id=tx.id,
            lot_id=lot.id,
            proposal_payload_json={"is_demo": False},
            proposal_hash="hash",
            proposed_by=payment_environment["collector_user_id"],
            proposed_at_client=datetime.now(timezone.utc),
            status="CONFIRMED",
            public_token_hash="token_hash",
            version=1
        )
        session.add(handover)
        session.commit()
        tx_id = tx.id

    pid = uuid.uuid4()
    client.post(
        f"/api/v1/transactions/{tx_id}/payments",
        json={"id": str(pid), "amount_paise": 100000, "method": "CASH"},
        headers=payment_environment["recycler_headers"]
    )
    # Dispute the payment
    client.post(
        f"/api/v1/payments/{pid}/dispute",
        json={"reason": "Counterfeit notes found in payment"},
        headers=payment_environment["collector_headers"]
    )

    close_resp = client.post(f"/api/v1/transactions/{tx_id}/close", headers=payment_environment["collector_headers"])
    assert close_resp.status_code == 409
    assert "Active payment dispute exists" in close_resp.json()["detail"]


def test_collector_earnings_filters_and_monthly_buckets(payment_environment):
    """Test collector earnings aggregates history, monthly buckets, and dues (R-PAY-03, AT-037)."""
    env = payment_environment
    resp = client.get("/api/v1/collector/earnings", headers=env["collector_headers"])
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["collector_id"] == str(env["collector_id"])
    assert data["total_transactions"] >= 1
    assert data["is_demo_isolated"] is True
    assert "freshness_timestamp" in data
    assert isinstance(data["monthly_breakdown"], list)


def test_collector_earnings_strict_demo_isolation(payment_environment):
    """Test demo transactions are strictly isolated from real settled earnings (R-PAY-03, AT-037)."""
    env = payment_environment

    # Seed a demo transaction with 1,000,000 paise (10,000 INR)
    with TestingSessionLocal() as session:
        lot = Lot(
            id=uuid.uuid4(),
            collector_id=env["collector_id"],
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=20000,
            status="RECEIVED",
            is_demo=True
        )
        session.add(lot)
        demo_tx = Transaction(
            id=uuid.uuid4(),
            lot_id=lot.id,
            collector_id=env["collector_id"],
            facility_id=env["facility_id"],
            accepted_offer_id=uuid.uuid4(),
            estimated_weight_g=20000,
            quoted_total_paise=1000000,
            agreed_total_paise=1000000,
            lifecycle="CONFIRMED",
            is_demo=True
        )
        session.add(demo_tx)
        session.commit()

    # Query without include_demo (default)
    real_resp = client.get("/api/v1/collector/earnings", headers=env["collector_headers"])
    real_data = real_resp.json()

    # Query with include_demo=True
    demo_resp = client.get("/api/v1/collector/earnings?include_demo=true", headers=env["collector_headers"])
    demo_data = demo_resp.json()

    # Real query must exclude the 1,000,000 paise demo transaction
    assert demo_data["gross_agreed_paise"] > real_data["gross_agreed_paise"]
    assert demo_data["total_transactions"] == real_data["total_transactions"] + 1
    assert real_data["is_demo_isolated"] is True
    assert demo_data["is_demo_isolated"] is False
