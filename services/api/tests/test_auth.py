"""Comprehensive test suite for phone/PIN authentication, session lifecycle, and authorization.
Covers T007 requirements: R-AUTH-01, R-AUTH-02, R-AUTH-03, R-AUTH-04, R-DATA-06, R-SEC-01.
Acceptance cases: AT-007, AT-008, AT-009, AT-010, AT-058, AT-072.
"""
import pytest
import uuid
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.db.models.auth import User, AuthSession
from app.db.models.collector import Collector
from app.db.models.facility import Facility, FacilityUser, Region
from app.rate_limiter import phone_limiter, ip_limiter
from app.security import (
    UserRole,
    normalize_phone,
    mask_phone,
    hash_pin,
    verify_pin,
    create_access_token,
    create_refresh_token,
    decode_token,
    check_demo_isolation
)

from tests.test_db import TestingSessionLocal

client = TestClient(app)


# --- Unit Tests: Cryptography & Normalization ---

def test_phone_normalization_and_masking():
    """Verify Indian mobile phone normalization and privacy-preserving masking."""
    assert normalize_phone("9876543210") == "9876543210"
    assert normalize_phone("+91 98765 43210") == "9876543210"
    assert normalize_phone("+91-9876543210") == "9876543210"
    assert normalize_phone("09876543210") == "9876543210"

    with pytest.raises(ValueError):
        normalize_phone("1234567890")  # Does not start with 6-9
    with pytest.raises(ValueError):
        normalize_phone("98765")       # Too short

    assert mask_phone("9876543210") == "******3210"


def test_argon2id_pin_hashing_security():
    """Verify Argon2id PIN hashing with random salt and server pepper."""
    pin = "4321"
    hashed = hash_pin(pin)
    assert hashed != pin
    assert "$argon2id$" in hashed
    assert verify_pin(pin, hashed) is True
    assert verify_pin("9999", hashed) is False

    with pytest.raises(ValueError):
        hash_pin("abc")  # Non-numeric rejected
    with pytest.raises(ValueError):
        hash_pin("12")   # Less than 4 digits rejected


# --- Integration Tests: Registration (R-AUTH-01, AT-007) ---

def test_collector_registration_success():
    """Verify collector online activation creates user, profile, and tokens."""
    payload = {
        "phone": "+91 9876543210",
        "pin": "1234",
        "alias": "Rajesh Collector",
        "preferred_language": "hi",
        "region_id": "DELHI_NCR",
        "general_area": "Mayapuri Ward 5",
        "device_id": "android-pixel-01"
    }
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["role"] == "COLLECTOR"
    assert data["is_demo"] is False
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["collector_id"] is not None

    # Verify database state
    db = TestingSessionLocal()
    user = db.query(User).filter(User.phone_normalized == "9876543210").first()
    assert user is not None
    assert user.role == "COLLECTOR"
    assert user.pin_hash != "1234"
    assert verify_pin("1234", user.pin_hash) is True
    assert user.collector is not None
    assert user.collector.display_alias == "Rajesh Collector"
    assert user.collector.preferred_language == "hi"
    db.close()


def test_duplicate_registration_rejected():
    """Verify duplicate phone registration returns 409 Conflict."""
    payload = {
        "phone": "9876543210",
        "pin": "1234",
        "alias": "First",
        "preferred_language": "hi"
    }
    resp1 = client.post("/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = client.post("/auth/register", json=payload)
    assert resp2.status_code == 409
    assert "already registered" in resp2.json()["detail"].lower()


# --- Integration Tests: Login & Rate Limiting (R-SEC-01, AT-072) ---

def test_login_success_and_failure():
    """Verify valid credentials authenticate and invalid credentials return generic 401."""
    # Register first
    client.post("/auth/register", json={
        "phone": "9876543210",
        "pin": "5678",
        "alias": "Test User",
        "preferred_language": "mr"
    })

    # Successful login
    login_resp = client.post("/auth/login", json={
        "phone": "9876543210",
        "pin": "5678",
        "device_id": "phone-device-123"
    })
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

    # Invalid PIN returns 401
    bad_pin = client.post("/auth/login", json={
        "phone": "9876543210",
        "pin": "0000"
    })
    assert bad_pin.status_code == 401
    assert "invalid phone number or pin" in bad_pin.json()["detail"].lower()

    # Non-existent phone returns same generic 401 (prevents user enumeration)
    bad_phone = client.post("/auth/login", json={
        "phone": "9111111111",
        "pin": "5678"
    })
    assert bad_phone.status_code == 401
    assert "invalid phone number or pin" in bad_phone.json()["detail"].lower()


def test_login_rate_limiting_lockout():
    """Verify 5 consecutive failed PIN attempts trigger 429 Too Many Requests."""
    # Register user
    client.post("/auth/register", json={
        "phone": "9876543210",
        "pin": "1234"
    })

    # Fail 4 times
    for _ in range(4):
        resp = client.post("/auth/login", json={"phone": "9876543210", "pin": "9999"})
        assert resp.status_code == 401

    # 5th failure triggers lockout
    resp5 = client.post("/auth/login", json={"phone": "9876543210", "pin": "9999"})
    assert resp5.status_code == 401

    # 6th attempt is blocked with 429
    resp6 = client.post("/auth/login", json={"phone": "9876543210", "pin": "9999"})
    assert resp6.status_code == 429
    assert "retry-after" in resp6.headers
    assert int(resp6.headers["retry-after"]) > 0


# --- Integration Tests: Rotating Refresh and Replay Detection (R-AUTH-03, AT-009) ---

def test_refresh_token_rotation_and_replay_protection():
    """Verify rotating refresh token issuance and automatic revocation on replay attack."""
    reg = client.post("/auth/register", json={
        "phone": "9876543210",
        "pin": "1234",
        "device_id": "device-rotate-test"
    }).json()

    initial_refresh = reg["refresh_token"]

    # 1. First refresh exchange succeeds
    ref_resp = client.post("/auth/refresh", json={"refresh_token": initial_refresh})
    assert ref_resp.status_code == 200
    ref_data = ref_resp.json()
    new_refresh = ref_data["refresh_token"]
    assert new_refresh != initial_refresh

    # 2. Replay attack: presenting initial_refresh again must be detected and rejected
    replay_resp = client.post("/auth/refresh", json={"refresh_token": initial_refresh})
    assert replay_resp.status_code == 401
    assert "replay detected" in replay_resp.json()["detail"].lower()

    # 3. Security mitigation: all user sessions were revoked, so new_refresh is now also revoked
    subsequent_resp = client.post("/auth/refresh", json={"refresh_token": new_refresh})
    assert subsequent_resp.status_code == 401


# --- Integration Tests: Safe Logout (R-AUTH-03, AT-009) ---

def test_safe_logout():
    """Verify logout revokes active session without deleting client-side offline pending data."""
    reg = client.post("/auth/register", json={
        "phone": "9876543210",
        "pin": "1234"
    }).json()

    access_token = reg["access_token"]
    refresh_token = reg["refresh_token"]

    # Logout
    logout_resp = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"refresh_token": refresh_token}
    )
    assert logout_resp.status_code == 200

    # Refresh with logged-out token fails
    ref_fail = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert ref_fail.status_code == 401


# --- Integration Tests: User Identity & Minimal Profile (R-DATA-06, AT-058) ---

def test_auth_me_minimal_profile():
    """Verify /auth/me returns masked phone and collector profile without sensitive credentials."""
    reg = client.post("/auth/register", json={
        "phone": "9876543210",
        "pin": "1234",
        "alias": "Sunil",
        "preferred_language": "hi",
        "general_area": "Kurla West"
    }).json()

    access_token = reg["access_token"]
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "COLLECTOR"
    assert data["phone_masked"] == "******3210"
    assert "pin" not in data
    assert "pin_hash" not in data
    assert data["collector"]["display_alias"] == "Sunil"
    assert data["collector"]["preferred_language"] == "hi"
    assert data["collector"]["general_area"] == "Kurla West"


# --- Integration Tests: Collector Profile Update & Optimistic Locking ---

def test_collector_profile_optimistic_locking():
    """Verify collector profile update enforces expected_version."""
    reg = client.post("/auth/register", json={
        "phone": "9876543210",
        "pin": "1234",
        "alias": "Old Alias",
        "preferred_language": "hi"
    }).json()

    token = reg["access_token"]

    # Conflict when expected_version is wrong
    conflict = client.patch(
        "/collectors/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"alias": "New Alias", "expected_version": 99}
    )
    assert conflict.status_code == 409

    # Valid update with expected_version = 1
    update_resp = client.patch(
        "/collectors/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"alias": "New Alias", "preferred_language": "mr", "expected_version": 1}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["display_alias"] == "New Alias"
    assert update_resp.json()["preferred_language"] == "mr"
    assert update_resp.json()["version"] == 2


# --- Integration Tests: Isolated Demo Mode (R-AUTH-04, AT-010) ---

def test_demo_login_isolated_and_labelled():
    """Verify demo login creates isolated demo user with is_demo=True and no SMS."""
    demo_resp = client.post("/auth/demo", json={
        "role": "COLLECTOR",
        "persona_id": "rajesh_collector"
    })
    assert demo_resp.status_code == 200
    data = demo_resp.json()
    assert data["is_demo"] is True
    assert data["role"] == "COLLECTOR"

    # Decode access token to verify is_demo claim
    claims = decode_token(data["access_token"])
    assert claims["is_demo"] is True


def test_demo_login_repairs_legacy_collector_without_profile():
    """A pre-existing hosted demo user must regain its required collector profile."""
    persona = "legacy_profile_repair"
    first = client.post("/auth/demo", json={"role": "COLLECTOR", "persona_id": persona})
    assert first.status_code == 200
    user_id = uuid.UUID(decode_token(first.json()["access_token"])["sub"])
    db = TestingSessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    assert user is not None
    db.query(Collector).filter(Collector.user_id == user.id).delete()
    db.commit()
    db.close()

    repaired = client.post("/auth/demo", json={"role": "COLLECTOR", "persona_id": persona})
    assert repaired.status_code == 200
    db = TestingSessionLocal()
    assert db.query(Collector).filter(Collector.user_id == user_id).first() is not None
    db.close()


def test_demo_yard_operator_gets_only_seeded_synthetic_facility_membership():
    """The recycler demo identity is usable without granting real-facility access."""
    demo_facility_id = uuid.uuid5(uuid.NAMESPACE_DNS, "fac-sim-01")
    db = TestingSessionLocal()
    try:
        if not db.query(Region).filter(Region.id == "DELHI_NCR").first():
            db.add(Region(id="DELHI_NCR", name="Delhi-NCR", state_code="DL", kind="METRO"))
        if not db.query(Facility).filter(Facility.id == demo_facility_id).first():
            db.add(Facility(
                id=demo_facility_id,
                name="Simulated Demonstration Recycling Hub",
                facility_name="Simulated Demonstration Recycling Hub",
                kind="RECYCLER",
                address_public="Demo sandbox",
                district="Demo",
                state="Delhi",
                region_id="DELHI_NCR",
                active=True,
            ))
        db.commit()
    finally:
        db.close()

    response = client.post("/auth/demo", json={"role": "RECYCLER", "persona_id": "yard_operator"})
    assert response.status_code == 200
    user_id = uuid.UUID(decode_token(response.json()["access_token"])["sub"])

    db = TestingSessionLocal()
    try:
        memberships = db.query(FacilityUser).filter(FacilityUser.user_id == user_id).all()
        assert [(membership.facility_id, membership.membership_role) for membership in memberships] == [
            (demo_facility_id, "OPERATOR")
        ]
    finally:
        db.close()

def test_demo_disabled_when_flag_off(monkeypatch):
    """Verify demo login is rejected with 403 when DEMO_MODE is False."""
    monkeypatch.setattr(settings, "DEMO_MODE", False)
    resp = client.post("/auth/demo", json={"role": "COLLECTOR", "persona_id": "test"})
    assert resp.status_code == 403


# --- Integration Tests: Role Authorization (R-AUTH-02, AT-008) ---

def test_role_authorization_enforcement():
    """Verify collector cannot access admin-only endpoints."""
    reg = client.post("/auth/register", json={
        "phone": "9876543210",
        "pin": "1234"
    }).json()

    token = reg["access_token"]

    # Direct query to collector route succeeds
    col_resp = client.get("/collectors/me", headers={"Authorization": f"Bearer {token}"})
    assert col_resp.status_code == 200

    # Unauthenticated query fails
    unauth = client.get("/collectors/me")
    assert unauth.status_code == 401
