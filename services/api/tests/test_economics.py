"""Comprehensive tests for Illustrative Economics Model and Platform Sustainability (T038).
Covers requirements: R-ECON-01, R-ECON-02.
Acceptance cases: AT-067, AT-068.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import get_db
from app.db.models.audit import EconomicsScenario
from app.db.models.auth import User
from app.domain.economics import (
    FORMULA_VERSION,
    SameLotInputs,
    SustainabilityInputs,
    calculate_same_lot_comparison,
    calculate_platform_sustainability,
)
from app.security import UserRole, create_access_token
from tests.test_db import TestingSessionLocal, override_get_db

FIXTURES_PATH = Path(__file__).resolve().parents[3] / "data" / "fixtures" / "economics_v1_fixtures.json"


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def collector_user():
    """Create a test collector user."""
    user_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        user = User(
            id=user_id,
            phone_normalized="+919876543888",
            pin_hash="pin_hash",
            role=UserRole.COLLECTOR.value,
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(user)
        session.commit()
    token = create_access_token(subject=str(user_id), role=UserRole.COLLECTOR.value, is_demo=False)
    headers = {"Authorization": f"Bearer {token}"}
    try:
        yield user_id, headers
    finally:
        with TestingSessionLocal() as session:
            session.query(EconomicsScenario).filter(EconomicsScenario.created_by == user_id).delete()
            session.query(User).filter(User.id == user_id).delete()
            session.commit()


@pytest.fixture
def other_user():
    """Create a second collector user for permission scoping tests."""
    user_id = uuid.uuid4()
    with TestingSessionLocal() as session:
        user = User(
            id=user_id,
            phone_normalized="+919876543889",
            pin_hash="pin_hash",
            role=UserRole.COLLECTOR.value,
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(user)
        session.commit()
    token = create_access_token(subject=str(user_id), role=UserRole.COLLECTOR.value, is_demo=False)
    headers = {"Authorization": f"Bearer {token}"}
    try:
        yield user_id, headers
    finally:
        with TestingSessionLocal() as session:
            session.query(EconomicsScenario).filter(EconomicsScenario.created_by == user_id).delete()
            session.query(User).filter(User.id == user_id).delete()
            session.commit()


# =============================================================================
# 1. Exact TechSpec Baseline & Rounding Parity (R-ECON-01, AT-067)
# =============================================================================

def test_techspec_baseline_exact_arithmetic():
    """
    R-ECON-01 / AT-067:
    Verify exact parity with docs/23_UNIT_ECONOMICS.md line 15:
    10kg, acquisition ₹1,000;
    Current: rate ₹150/kg, transport ₹100, handling ₹50 -> current net ₹350.
    Platform: assumed rate ₹160/kg, transport ₹80, handling ₹50 -> net ₹470.
    Delta: ₹120, 34.29%.
    """
    inputs = SameLotInputs(
        material_id="MAT-PCB-01",
        weight_g=10000,
        acquisition_cost_paise=100000,
        current_rate_paise_per_kg=15000,
        current_transport_paise=10000,
        current_handling_paise=5000,
        platform_rate_paise_per_kg=16000,
        platform_transport_paise=8000,
        platform_handling_paise=5000,
    )
    res = calculate_same_lot_comparison(inputs)

    assert res.current.gross_paise == 150000
    assert res.current.total_costs_paise == 115000
    assert res.current.net_paise == 35000

    assert res.platform.gross_paise == 160000
    assert res.platform.total_costs_paise == 113000
    assert res.platform.net_paise == 47000

    assert res.delta_paise == 12000
    assert res.delta_percent == 34.29
    assert res.delta_percent_display == "+34.29%"
    assert res.is_platform_favorable is True
    assert res.is_illustrative is True
    assert len(res.caveats) >= 2


def test_shared_fixtures_json_parity():
    """
    Verify 100% agreement with canonical shared fixtures file
    data/fixtures/economics_v1_fixtures.json.
    """
    assert FIXTURES_PATH.exists()
    with open(FIXTURES_PATH, "r", encoding="utf-8") as f:
        fixtures_data = json.load(f)

    # 1. Test all same-lot fixtures
    for fix in fixtures_data["same_lot_fixtures"]:
        inputs = SameLotInputs(**fix["inputs"])
        res = calculate_same_lot_comparison(inputs)
        exp = fix["expected"]

        assert res.current.gross_paise == exp["current_gross_paise"], f"Failed {fix['name']} current gross"
        assert res.current.total_costs_paise == exp["current_total_costs_paise"], f"Failed {fix['name']} current costs"
        assert res.current.net_paise == exp["current_net_paise"], f"Failed {fix['name']} current net"

        assert res.platform.gross_paise == exp["platform_gross_paise"], f"Failed {fix['name']} platform gross"
        assert res.platform.total_costs_paise == exp["platform_total_costs_paise"], f"Failed {fix['name']} platform costs"
        assert res.platform.net_paise == exp["platform_net_paise"], f"Failed {fix['name']} platform net"

        assert res.delta_paise == exp["delta_paise"], f"Failed {fix['name']} delta paise"
        assert res.delta_percent == exp["delta_percent"], f"Failed {fix['name']} delta percent"
        assert res.delta_percent_display == exp["delta_percent_display"], f"Failed {fix['name']} delta percent display"
        assert res.is_platform_favorable == exp["is_platform_favorable"], f"Failed {fix['name']} favorability"

    # 2. Test all sustainability fixtures
    for fix in fixtures_data["sustainability_fixtures"]:
        inputs = SustainabilityInputs(**fix["inputs"])
        res = calculate_platform_sustainability(inputs)
        exp = fix["expected"]

        assert res.collector_fee_paise == exp["collector_fee_paise"]
        assert res.contribution_per_transaction_paise == exp["contribution_per_transaction_paise"]
        assert res.total_monthly_fixed_costs_paise == exp["total_monthly_fixed_costs_paise"]
        assert res.total_monthly_revenue_paise == exp["total_monthly_revenue_paise"]
        assert res.monthly_operating_result_paise == exp["monthly_operating_result_paise"]
        assert res.is_operating_positive == exp["is_operating_positive"]
        assert res.break_even_transaction_count == exp["break_even_transaction_count"]
        assert res.break_even_status == exp["break_even_status"]


# =============================================================================
# 2. Zero & Negative Baseline Handling (R-ECON-01, AT-067)
# =============================================================================

def test_zero_baseline_delta_percent_is_none():
    """
    R-ECON-01 / AT-067:
    When baseline current net is ₹0, delta percentage cannot be computed;
    must be None with clear textual explanation.
    """
    inputs = SameLotInputs(
        material_id="MAT-OTH-01",
        weight_g=10000,
        acquisition_cost_paise=50000,
        current_rate_paise_per_kg=5000,
        platform_rate_paise_per_kg=6000,
    )
    res = calculate_same_lot_comparison(inputs)

    assert res.current.net_paise == 0
    assert res.platform.net_paise == 10000
    assert res.delta_paise == 10000
    assert res.delta_percent is None
    assert "not meaningful for zero/negative baseline" in res.delta_percent_display


def test_negative_baseline_loss_handling():
    """
    R-ECON-01 / AT-067:
    When collector buys at a loss in current baseline (negative net),
    delta percentage is None and not misleadingly inflated.
    """
    inputs = SameLotInputs(
        material_id="MAT-PCB-02",
        weight_g=5000,
        acquisition_cost_paise=80000,
        current_rate_paise_per_kg=10000,
        current_transport_paise=5000,
        current_handling_paise=2000,
        platform_rate_paise_per_kg=15000,
        platform_transport_paise=3000,
        platform_handling_paise=2000,
    )
    res = calculate_same_lot_comparison(inputs)

    assert res.current.net_paise == -37000
    assert res.platform.net_paise == -10000
    assert res.delta_paise == 27000
    assert res.delta_percent is None
    assert "not meaningful for zero/negative baseline" in res.delta_percent_display


def test_negative_platform_benefit_displayed_honestly():
    """
    R-ECON-01 / AT-067:
    Model supports and honestly reveals scenarios where platform is less favorable
    (e.g. remote transport costs outweigh slightly higher formal price).
    """
    inputs = SameLotInputs(
        material_id="MAT-PLA-01",
        weight_g=50000,
        acquisition_cost_paise=100000,
        current_rate_paise_per_kg=2500,
        current_transport_paise=3000,
        current_handling_paise=2000,
        platform_rate_paise_per_kg=2700,
        platform_transport_paise=25000,
        platform_handling_paise=2000,
    )
    res = calculate_same_lot_comparison(inputs)

    assert res.current.net_paise == 20000
    assert res.platform.net_paise == 8000
    assert res.delta_paise == -12000
    assert res.delta_percent == -60.0
    assert res.delta_percent_display == "-60.00%"
    assert res.is_platform_favorable is False


# =============================================================================
# 3. Platform Sustainability & Zero Collector Fees (R-ECON-02, AT-068)
# =============================================================================

def test_platform_sustainability_zero_collector_fee_guarantee():
    """
    R-ECON-02 / AT-068:
    Platform sustainability model strictly enforces zero collector fee policy.
    Evaluates downstream recycler fee revenue, contribution, and break-even count.
    """
    inputs = SustainabilityInputs(
        monthly_completed_transactions=1000,
        fee_model="FIXED_PER_TRANSACTION",
        assumed_fee_per_transaction_paise=15000,  # ₹150 downstream fee
        variable_cost_per_transaction_paise=3000, # ₹30 variable cost
        fixed_monthly_hosting_paise=500000,       # ₹5,000 hosting
        fixed_monthly_verification_support_paise=1500000, # ₹15,000 support
        fixed_monthly_administration_paise=1000000        # ₹10,000 admin
    )
    res = calculate_platform_sustainability(inputs)

    assert res.collector_fee_paise == 0
    assert res.collector_fee_policy == "FREE_TO_COLLECTORS"
    assert res.contribution_per_transaction_paise == 12000 # ₹120
    assert res.total_monthly_revenue_paise == 15000000     # ₹150,000
    assert res.total_monthly_fixed_costs_paise == 3000000  # ₹30,000
    assert res.monthly_operating_result_paise == 9000000   # ₹90,000
    assert res.is_operating_positive is True
    # Break-even = ceil(3000000 / 12000) = 250 transactions
    assert res.break_even_transaction_count == 250
    assert res.break_even_status == "FINITE"
    assert "Hypothetical downstream service fee" in res.disclaimer


def test_platform_sustainability_no_finite_break_even():
    """
    When variable cost exceeds fee, contribution is negative and break-even count is null.
    """
    inputs = SustainabilityInputs(
        monthly_completed_transactions=50,
        fee_model="FIXED_PER_TRANSACTION",
        assumed_fee_per_transaction_paise=2000,
        variable_cost_per_transaction_paise=2500,  # Variable cost > fee
        fixed_monthly_hosting_paise=500000,
        fixed_monthly_verification_support_paise=500000,
        fixed_monthly_administration_paise=500000
    )
    res = calculate_platform_sustainability(inputs)

    assert res.contribution_per_transaction_paise == -500
    assert res.break_even_transaction_count is None
    assert res.break_even_status == "NO_FINITE_BREAK_EVEN"
    assert res.is_operating_positive is False


# =============================================================================
# 4. FastAPI Endpoint Integration Tests
# =============================================================================

def test_api_economics_calculate_endpoint(client: TestClient):
    """POST /api/v1/economics/calculate executes stateless calculation without auth or side effects."""
    payload = {
        "material_id": "MAT-PCB-01",
        "weight_g": 10000,
        "acquisition_cost_paise": 100000,
        "current_rate_paise_per_kg": 15000,
        "current_transport_paise": 10000,
        "current_handling_paise": 5000,
        "platform_rate_paise_per_kg": 16000,
        "platform_transport_paise": 8000,
        "platform_handling_paise": 5000
    }
    resp = client.post("/api/v1/economics/calculate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["delta_paise"] == 12000
    assert data["delta_percent"] == 34.29
    assert data["is_illustrative"] is True
    assert len(data["caveats"]) >= 2


def test_api_economics_sustainability_endpoint(client: TestClient):
    """POST /api/v1/economics/sustainability computes platform economics."""
    payload = {
        "monthly_completed_transactions": 500,
        "fee_model": "FIXED_PER_TRANSACTION",
        "assumed_fee_per_transaction_paise": 10000,
        "variable_cost_per_transaction_paise": 2000,
        "fixed_monthly_hosting_paise": 500000,
        "fixed_monthly_verification_support_paise": 1000000,
        "fixed_monthly_administration_paise": 500000
    }
    resp = client.post("/api/v1/economics/sustainability", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["collector_fee_paise"] == 0
    assert data["break_even_transaction_count"] == 250
    assert data["is_operating_positive"] is True


def test_api_economics_scenarios_listing_and_crud(
    client: TestClient,
    collector_user,
    other_user
):
    """
    GET/POST/DELETE /api/v1/economics/scenarios:
    Lists default seed scenarios and tests user-saved scenario persistence and permission isolation.
    """
    user_id, headers = collector_user
    other_id, other_headers = other_user

    # 1. Unauthenticated or collector list returns at least 3 default scenarios
    resp_list = client.get("/api/v1/economics/scenarios", headers=headers)
    assert resp_list.status_code == 200
    scenarios = resp_list.json()
    assert len(scenarios) >= 3
    assert any(s["name"].startswith("TechSpec Baseline") for s in scenarios)

    # 2. Save a custom scenario
    create_payload = {
        "name": "Custom Mayapuri Cable Scenario",
        "inputs": {
            "material_id": "MAT-CAB-01",
            "weight_g": 12000,
            "acquisition_cost_paise": 120000,
            "current_rate_paise_per_kg": 15000,
            "current_transport_paise": 8000,
            "current_handling_paise": 4000,
            "platform_rate_paise_per_kg": 16500,
            "platform_transport_paise": 6000,
            "platform_handling_paise": 4000
        },
        "source_ids": ["SRC-01"]
    }
    resp_create = client.post("/api/v1/economics/scenarios", json=create_payload, headers=headers)
    assert resp_create.status_code == 201
    created_data = resp_create.json()
    scenario_id = created_data["id"]
    assert created_data["name"] == "Custom Mayapuri Cable Scenario"
    assert created_data["is_illustrative"] is True
    assert created_data["created_by"] == str(user_id)

    # 3. Retrieve single scenario
    resp_get = client.get(f"/api/v1/economics/scenarios/{scenario_id}", headers=headers)
    assert resp_get.status_code == 200
    assert resp_get.json()["id"] == scenario_id

    # 4. Other user cannot access or delete private scenario (HTTP 403)
    resp_forbidden_get = client.get(f"/api/v1/economics/scenarios/{scenario_id}", headers=other_headers)
    assert resp_forbidden_get.status_code == 403

    resp_forbidden_del = client.delete(f"/api/v1/economics/scenarios/{scenario_id}", headers=other_headers)
    assert resp_forbidden_del.status_code == 403

    # 5. Creator successfully deletes scenario
    resp_del = client.delete(f"/api/v1/economics/scenarios/{scenario_id}", headers=headers)
    assert resp_del.status_code == 200
    assert resp_del.json()["deleted"] is True
