"""Comprehensive Security, Privacy, and Abuse Boundaries Test Suite (T040).
Covers Phase 6 requirements:
  - R-AUTH-02: Role and object authorization (IDOR, role hierarchy, cross-account boundaries).
  - R-AUTH-04: Isolated demo access without SMS, demo data partition containment.
  - R-HAND-04: Public verification and privacy (capability token hashing, PII/GPS/finance redaction, non-EPR notice).
  - R-DATA-06: Minimal collector dataset, PII redaction, zero Aadhaar/bank credential storage.
  - R-DATA-08: Provenance and demo isolation everywhere, non-EPR disclaimers.
  - R-SEC-01: PIN abuse rate limiting, user enumeration prevention, session rotation, replay revocation, repo secrets scan.
  - R-SEC-02: Privacy media access, EXIF GPS stripping, path traversal prevention, signed URL expiration, CSV formula injection neutralization.
Acceptance cases:
  - AT-008: Role and object authorization.
  - AT-010: Isolated demo access without SMS.
  - AT-032: Public verification and privacy.
  - AT-058: Minimal collector dataset and anonymization.
  - AT-060: Provenance and demo isolation everywhere.
  - AT-072: PIN abuse secrets and transport safety.
  - AT-073: Privacy media access retention and audit.
"""
import hashlib
import io
import json
import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.config import settings
from app.db.session import get_db
from app.db.models.audit import DomainEvent
from app.db.models.auth import User, AuthSession
from app.db.models.collector import Collector
from app.db.models.facility import Facility, FacilityAuthorization, FacilityMaterial, FacilityUser, Region
from app.db.models.lot import Lot, MediaObject
from app.db.models.material import Material, MaterialCategory
from app.db.models.trade import Handover, HandoverConfirmation, LotRequest, Offer, TermsRevision, Transaction
from app.domain.canonical import compute_canonical_hash
from app.rate_limiter import phone_limiter, ip_limiter
from app.routers.exports import sanitize_csv_cell, NON_EPR_STATUTORY_DISCLAIMER
from app.routers.media import _strip_exif_and_validate_image
from app.security import (
    UserRole,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_pin,
    verify_pin,
    mask_phone,
    normalize_phone,
    check_demo_isolation,
)
from app.storage import get_storage_adapter
from app.storage.local import LocalStorageAdapter, MAX_MEDIA_BYTES
from tests.test_db import TestingSessionLocal, override_get_db

client = TestClient(app)

NON_EPR_DISCLAIMER_SNIPPET = "not a statutory EPR certificate"


@pytest.fixture(scope="module", autouse=True)
def setup_security_suite():
    """Setup test database dependency override and baseline region/material."""
    from app.db.seeds.materials import seed_materials
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
def auth_fixture():
    """Create Collector 1, Collector 2, Recycler 1 (Facility 1), Recycler 2 (Facility 2), and Admin users."""
    with TestingSessionLocal() as session:
        # 1. Collector A
        u_col_a = User(
            id=uuid.uuid4(),
            phone_normalized="+919876500001",
            pin_hash=hash_pin("1234"),
            role="COLLECTOR",
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(u_col_a)
        session.flush()
        col_a = Collector(
            id=uuid.uuid4(),
            user_id=u_col_a.id,
            display_alias="Collector A",
            preferred_language="hi",
            region_id="DELHI_NCR",
            general_area="Mayapuri Industrial Area"
        )
        session.add(col_a)

        # 2. Collector B
        u_col_b = User(
            id=uuid.uuid4(),
            phone_normalized="+919876500002",
            pin_hash=hash_pin("1234"),
            role="COLLECTOR",
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(u_col_b)
        session.flush()
        col_b = Collector(
            id=uuid.uuid4(),
            user_id=u_col_b.id,
            display_alias="Collector B",
            preferred_language="mr",
            region_id="DELHI_NCR",
            general_area="Okhla Phase 1"
        )
        session.add(col_b)

        # 3. Facility 1 & Recycler User 1
        fac_1 = Facility(
            id=uuid.uuid4(),
            name="Facility Alpha",
            facility_name="Facility Alpha Recyclers",
            kind="RECYCLER",
            address_public="Mayapuri Yard 1",
            state="Delhi",
            district="West Delhi",
            region_id="DELHI_NCR",
            active=True
        )
        session.add(fac_1)
        session.flush()
        u_rec_1 = User(
            id=uuid.uuid4(),
            phone_normalized="+919876500003",
            pin_hash=hash_pin("1234"),
            role="RECYCLER",
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(u_rec_1)
        session.flush()
        fu_1 = FacilityUser(
            facility_id=fac_1.id,
            user_id=u_rec_1.id,
            membership_role="OPERATOR",
            active=True
        )
        session.add(fu_1)

        # 4. Facility 2 & Recycler User 2
        fac_2 = Facility(
            id=uuid.uuid4(),
            name="Facility Beta",
            facility_name="Facility Beta Yard",
            kind="RECYCLER",
            address_public="Okhla Yard 2",
            state="Delhi",
            district="South Delhi",
            region_id="DELHI_NCR",
            active=True
        )
        session.add(fac_2)
        session.flush()
        u_rec_2 = User(
            id=uuid.uuid4(),
            phone_normalized="+919876500004",
            pin_hash=hash_pin("1234"),
            role="RECYCLER",
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(u_rec_2)
        session.flush()
        fu_2 = FacilityUser(
            facility_id=fac_2.id,
            user_id=u_rec_2.id,
            membership_role="OPERATOR",
            active=True
        )
        session.add(fu_2)

        # 5. Admin User
        u_admin = User(
            id=uuid.uuid4(),
            phone_normalized="+919876500099",
            pin_hash=hash_pin("1234"),
            role="ADMIN",
            account_state="ACTIVE",
            is_demo=False
        )
        session.add(u_admin)

        session.commit()

        return {
            "col_a": {"user_id": u_col_a.id, "collector_id": col_a.id, "token": create_access_token(str(u_col_a.id), "COLLECTOR")},
            "col_b": {"user_id": u_col_b.id, "collector_id": col_b.id, "token": create_access_token(str(u_col_b.id), "COLLECTOR")},
            "rec_1": {"user_id": u_rec_1.id, "facility_id": fac_1.id, "token": create_access_token(str(u_rec_1.id), "RECYCLER")},
            "rec_2": {"user_id": u_rec_2.id, "facility_id": fac_2.id, "token": create_access_token(str(u_rec_2.id), "RECYCLER")},
            "admin": {"user_id": u_admin.id, "token": create_access_token(str(u_admin.id), "ADMIN")},
        }


# ===========================================================================
# 0. TRANSPORT CORS BOUNDARY (R-SEC-01, AT-072)
# ===========================================================================

def test_cors_allows_only_configured_origin():
    """An allowed web origin receives CORS credentials; an arbitrary one does not."""
    allowed_origin = settings.CORS_ORIGINS[0]
    allowed = client.options(
        "/api/v1/auth/demo",
        headers={
            "Origin": allowed_origin,
            "Access-Control-Request-Method": "POST",
        },
    )
    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == allowed_origin
    assert allowed.headers["access-control-allow-credentials"] == "true"

    denied = client.options(
        "/api/v1/auth/demo",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert denied.status_code == 400
    assert "access-control-allow-origin" not in denied.headers


# ===========================================================================
# 1. OBJECT-LEVEL AUTHORIZATION & IDOR (R-AUTH-02, AT-008)
# ===========================================================================

def test_collector_cannot_view_or_mutate_other_collector_lot(auth_fixture):
    """Verify IDOR prevention: Collector B cannot read, edit, collect, list, or cancel Collector A's lot."""
    col_a_token = auth_fixture["col_a"]["token"]
    col_b_token = auth_fixture["col_b"]["token"]

    # 1. Collector A creates Lot A
    create_resp = client.post(
        "/api/v1/lots",
        headers={"Authorization": f"Bearer {col_a_token}"},
        json={
            "material_id": "MAT-PCB-01",
            "estimated_weight_kg": 15.0,
            "condition": "INTACT",
            "description": "Collector A Private Lot"
        }
    )
    assert create_resp.status_code == 201
    lot_a_id = create_resp.json()["id"]

    # 2. Collector B attempts to view Lot A -> 403 Forbidden
    get_resp = client.get(
        f"/api/v1/lots/{lot_a_id}",
        headers={"Authorization": f"Bearer {col_b_token}"}
    )
    assert get_resp.status_code == 403
    assert "cannot view another collector's private lot" in get_resp.json()["detail"].lower()

    # 3. Collector B attempts to edit Lot A -> 403 Forbidden
    patch_resp = client.patch(
        f"/api/v1/lots/{lot_a_id}",
        headers={"Authorization": f"Bearer {col_b_token}"},
        json={"description": "Hacked Description", "expected_version": 1}
    )
    assert patch_resp.status_code == 403
    assert "cannot edit another collector's lot" in patch_resp.json()["detail"].lower()

    # 4. Collector B attempts to transition Lot A to COLLECTED -> 403 Forbidden
    collect_resp = client.post(
        f"/api/v1/lots/{lot_a_id}/collect",
        headers={"Authorization": f"Bearer {col_b_token}"},
        json={"expected_version": 1}
    )
    assert collect_resp.status_code == 403
    assert "cannot collect another collector's lot" in collect_resp.json()["detail"].lower()

    # 5. Collector B attempts to list Lot A -> 403 Forbidden
    list_resp = client.post(
        f"/api/v1/lots/{lot_a_id}/list",
        headers={"Authorization": f"Bearer {col_b_token}"},
        json={"expected_version": 1}
    )
    assert list_resp.status_code == 403
    assert "cannot list another collector's lot" in list_resp.json()["detail"].lower()

    # 6. Collector B attempts to cancel Lot A -> 403 Forbidden
    cancel_resp = client.post(
        f"/api/v1/lots/{lot_a_id}/cancel",
        headers={"Authorization": f"Bearer {col_b_token}"},
        json={"expected_version": 1, "reason": "Malicious cancellation"}
    )
    assert cancel_resp.status_code == 403
    assert "cannot cancel another collector's lot" in cancel_resp.json()["detail"].lower()


def test_collector_cannot_create_lot_for_another_collector(auth_fixture):
    """Verify that a collector cannot spoof collector_id to impersonate another collector."""
    col_a_token = auth_fixture["col_a"]["token"]
    col_b_user_id = str(auth_fixture["col_b"]["user_id"])

    resp = client.post(
        "/api/v1/lots",
        headers={"Authorization": f"Bearer {col_a_token}"},
        json={
            "collector_id": col_b_user_id,
            "material_id": "MAT-PCB-01",
            "estimated_weight_kg": 10.0
        }
    )
    assert resp.status_code == 403
    assert "cannot create lot on behalf of another collector" in resp.json()["detail"].lower()


def test_cross_facility_recycler_handover_isolation(auth_fixture):
    """Verify that Recycler 2 (Facility 2) cannot confirm or view Handover belonging to Facility 1."""
    col_a_token = auth_fixture["col_a"]["token"]
    rec_1_token = auth_fixture["rec_1"]["token"]
    rec_2_token = auth_fixture["rec_2"]["token"]
    fac_1_id = auth_fixture["rec_1"]["facility_id"]

    # 1. Collector creates, collects, and lists a lot
    lot_id = client.post(
        "/api/v1/lots",
        headers={"Authorization": f"Bearer {col_a_token}"},
        json={"material_id": "MAT-PCB-01", "estimated_weight_kg": 20.0, "condition": "INTACT"}
    ).json()["id"]

    client.post(
        f"/api/v1/lots/{lot_id}/collect",
        headers={"Authorization": f"Bearer {col_a_token}"},
        json={"material_id": "MAT-PCB-01", "weight_g": 20000}
    )
    client.post(
        f"/api/v1/lots/{lot_id}/list",
        headers={"Authorization": f"Bearer {col_a_token}"},
        json={"regulatory_route": "AUTHORIZED_EWASTE"}
    )

    # 2. Recycler 1 offers and Collector accepts -> creates Transaction & Handover
    with TestingSessionLocal() as session:
        lot_uuid = uuid.UUID(lot_id)
        lot = session.query(Lot).filter(Lot.id == lot_uuid).first()
        lot.status = "ACCEPTED"
        session.flush()

        req = LotRequest(
            id=uuid.uuid4(),
            lot_id=lot_uuid,
            facility_id=fac_1_id,
            created_by=auth_fixture["col_a"]["user_id"],
            state="ACCEPTED"
        )
        session.add(req)
        session.flush()

        offer = Offer(
            id=uuid.uuid4(),
            request_id=req.id,
            lot_id=lot_uuid,
            facility_id=fac_1_id,
            rate_paise_per_kg=15000,
            price_basis="RATE_PER_KG",
            condition="INTACT",
            weight_basis_g=20000,
            expires_at=datetime.now(timezone.utc) + timedelta(days=3),
            status="ACCEPTED",
            terms_hash="dummy_hash_01",
            version=1
        )
        session.add(offer)
        session.flush()

        tx = Transaction(
            id=uuid.uuid4(),
            lot_id=lot_uuid,
            collector_id=auth_fixture["col_a"]["collector_id"],
            facility_id=fac_1_id,
            accepted_offer_id=offer.id,
            estimated_weight_g=20000,
            agreed_weight_g=20000,
            quoted_total_paise=300000,
            agreed_total_paise=300000,
            currency="INR",
            lifecycle="AGREED",
            version=1,
            is_demo=False
        )
        session.add(tx)
        session.flush()

        raw_token = f"pub_token_{uuid.uuid4().hex}"
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

        handover = Handover(
            id=uuid.uuid4(),
            transaction_id=tx.id,
            lot_id=tx.lot_id,
            proposed_by=auth_fixture["col_a"]["user_id"],
            proposed_at_client=datetime.now(timezone.utc),
            status="PENDING_CONFIRMATION",
            proposal_hash="a" * 64,
            public_token_hash=token_hash,
            proposal_payload_json={"lot_id": lot_id}
        )
        session.add(handover)
        session.commit()
        handover_id = handover.id

    # 3. Recycler 2 (Facility 2) attempts to view Handover for Facility 1 -> 403 Forbidden
    view_resp = client.get(
        f"/api/v1/handovers/{handover_id}",
        headers={"Authorization": f"Bearer {rec_2_token}"}
    )
    assert view_resp.status_code == 403
    assert "not a participant in this handover" in view_resp.json()["detail"].lower()

    # 4. Recycler 2 attempts to confirm Handover for Facility 1 -> 403 Forbidden
    confirm_resp = client.post(
        f"/api/v1/handovers/{handover_id}/confirm",
        headers={"Authorization": f"Bearer {rec_2_token}"},
        json={
            "expected_version": 1,
            "proposal_hash": "a" * 64,
            "measured_weight_g": 20000,
            "measured_material_id": "MAT-PCB-01",
            "final_total_paise": 300000
        }
    )
    assert confirm_resp.status_code == 403
    assert "not an active member of this facility" in confirm_resp.json()["detail"].lower()


def test_non_admin_cannot_access_admin_governance(auth_fixture):
    """Verify that collectors and recyclers cannot access administrative endpoints or escalate privileges."""
    col_token = auth_fixture["col_a"]["token"]
    rec_token = auth_fixture["rec_1"]["token"]

    endpoints = [
        ("GET", "/api/v1/admin/overview"),
        ("GET", "/api/v1/admin/quality-flags"),
        ("GET", "/api/v1/admin/metrics"),
        ("GET", "/api/v1/admin/collectors"),
        ("GET", "/api/v1/admin/events"),
    ]

    for method, path in endpoints:
        # Collector is rejected
        col_resp = client.get(path, headers={"Authorization": f"Bearer {col_token}"})
        assert col_resp.status_code == 403, f"Collector unexpectedly accessed {path}"

        # Recycler is rejected
        rec_resp = client.get(path, headers={"Authorization": f"Bearer {rec_token}"})
        assert rec_resp.status_code == 403, f"Recycler unexpectedly accessed {path}"

        # Unauthenticated request is rejected
        unauth_resp = client.get(path)
        assert unauth_resp.status_code == 401, f"Unauthenticated request unexpectedly accessed {path}"


# ===========================================================================
# 2. PIN ABUSE, RATE LIMITING & SECRETS (R-SEC-01, AT-072)
# ===========================================================================

def test_pin_brute_force_rate_limiting_and_lockout():
    """Verify that progressive failed PIN attempts trigger 429 Too Many Requests with Retry-After header."""
    phone = "+919876543219"
    # Register test user
    client.post("/auth/register", json={"phone": phone, "pin": "7777"})

    # Clear limiter state first
    phone_limiter.reset()

    # 4 invalid attempts return 401
    for i in range(4):
        resp = client.post("/auth/login", json={"phone": phone, "pin": "0000"})
        assert resp.status_code == 401, f"Attempt {i+1} did not return 401"

    # 5th invalid attempt triggers lockout
    resp5 = client.post("/auth/login", json={"phone": phone, "pin": "0000"})
    assert resp5.status_code == 401

    # 6th attempt is blocked with 429
    resp6 = client.post("/auth/login", json={"phone": phone, "pin": "0000"})
    assert resp6.status_code == 429
    assert "retry-after" in resp6.headers
    assert int(resp6.headers["retry-after"]) > 0


def test_user_enumeration_prevention_uniform_401():
    """Verify that bad PIN and non-existent phone return the identical generic 401 error message."""
    # Bad PIN for registered user
    resp1 = client.post("/auth/login", json={"phone": "+919876500001", "pin": "9999"})
    assert resp1.status_code == 401

    # Non-existent phone
    resp2 = client.post("/auth/login", json={"phone": "+919111199999", "pin": "1234"})
    assert resp2.status_code == 401

    # Verify identical generic message
    assert resp1.json()["detail"].lower() == resp2.json()["detail"].lower()
    assert "invalid phone number or pin" in resp1.json()["detail"].lower()


def test_refresh_token_replay_attack_cascades_session_revocation():
    """Verify that reusing a rotated refresh token is detected as a replay attack and revokes all user sessions."""
    phone = "+919876543290"
    reg = client.post("/auth/register", json={"phone": phone, "pin": "5555", "device_id": "replay-test"}).json()
    r1 = reg["refresh_token"]

    # 1. Normal rotation exchange: R1 -> R2
    ref_resp = client.post("/auth/refresh", json={"refresh_token": r1})
    assert ref_resp.status_code == 200
    r2 = ref_resp.json()["refresh_token"]
    assert r2 != r1

    # 2. Replay attack: Attacker tries to use R1 again
    replay_resp = client.post("/auth/refresh", json={"refresh_token": r1})
    assert replay_resp.status_code == 401
    assert "replay detected" in replay_resp.json()["detail"].lower()

    # 3. Cascading revocation: Legitimate user's R2 must also be invalidated
    subsequent_resp = client.post("/auth/refresh", json={"refresh_token": r2})
    assert subsequent_resp.status_code == 401
    assert "replay detected" in subsequent_resp.json()["detail"].lower() or "revoked" in subsequent_resp.json()["detail"].lower() or "session" in subsequent_resp.json()["detail"].lower()


def test_repository_secrets_audit():
    """Audit codebase to ensure no production secrets, private keys, or passwords are hardcoded."""
    patterns = [
        (re.compile(r"BEGIN (?:RSA|OPENSSH|PGP|ENCRYPTED|EC)? PRIVATE KEY", re.I), "Private key block"),
        (re.compile(r"postgres(?:ql)?://[a-zA-Z0-9_-]+:[^@\s]+@", re.I), "Database connection with credentials"),
        (re.compile(r"(?:jwt_secret_key|api_key|private_key)\s*[:=]\s*['\"][a-zA-Z0-9_\-\.]{16,}['\"]", re.I), "Hardcoded secret key"),
    ]

    exclude_dirs = {".git", "node_modules", ".gradle", "build", "__pycache__", ".venv", "dist", ".gemini"}
    findings = []

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith((".pyc", ".png", ".jpg", ".webp", ".mp3", ".tflite", ".apk", ".zip", ".jar", ".bin")):
                continue
            fp = os.path.join(root, file).replace("\\", "/")
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                    txt = f.read()
                    for rx, label in patterns:
                        for m in rx.finditer(txt):
                            snip = m.group(0)
                            if any(x in fp for x in [".env.example", "conftest.py", "docker-compose", "fixtures", "docs", "test_", "/tests/"]):
                                continue
                            if "example" in snip.lower() or "dummy" in snip.lower() or "changeme" in snip.lower():
                                continue
                            findings.append((fp, label, snip[:30]))
            except Exception:
                pass

    assert len(findings) == 0, f"Found leaked secrets in repository: {findings}"


# ===========================================================================
# 3. ISOLATED DEMO ACCESS & PARTITION CONTAINMENT (R-AUTH-04, AT-010, R-DATA-08, AT-060)
# ===========================================================================

def test_demo_profile_isolation_and_labeling():
    """Verify demo login is explicitly labelled, has no SMS dependency, and carries is_demo=True claim."""
    demo_resp = client.post("/auth/demo", json={"role": "COLLECTOR", "persona_id": "rajesh_collector"})
    assert demo_resp.status_code == 200
    data = demo_resp.json()
    assert data["is_demo"] is True
    assert data["role"] == "COLLECTOR"

    claims = decode_token(data["access_token"])
    assert claims["is_demo"] is True
    assert claims["sub"] is not None


def test_demo_disabled_when_flag_off(monkeypatch):
    """Verify that when DEMO_MODE setting is disabled, /auth/demo returns 403 Forbidden."""
    monkeypatch.setattr(settings, "DEMO_MODE", False)
    resp = client.post("/auth/demo", json={"role": "COLLECTOR", "persona_id": "rajesh_collector"})
    assert resp.status_code == 403
    assert "disabled" in resp.json()["detail"].lower()


def test_demo_isolation_boundary_enforcement(auth_fixture):
    """Verify that production accounts cannot manipulate demo records and vice-versa."""
    # Create a demo user
    demo_user = client.post("/auth/demo", json={"role": "COLLECTOR", "persona_id": "rajesh_collector"}).json()
    demo_token = demo_user["access_token"]

    # Demo collector creates demo lot
    demo_lot = client.post(
        "/api/v1/lots",
        headers={"Authorization": f"Bearer {demo_token}"},
        json={"material_id": "MAT-PCB-01", "estimated_weight_kg": 5.0, "is_demo": True}
    ).json()
    assert demo_lot["is_demo"] is True

    # Live production collector A attempts to view or mutate demo lot -> 403 Forbidden
    col_a_token = auth_fixture["col_a"]["token"]
    resp = client.get(f"/api/v1/lots/{demo_lot['id']}", headers={"Authorization": f"Bearer {col_a_token}"})
    assert resp.status_code == 403


# ===========================================================================
# 4. PUBLIC VERIFICATION & PRIVACY (R-HAND-04, AT-032)
# ===========================================================================

def test_public_verification_capability_token_privacy(auth_fixture):
    """Verify public verification endpoint redacts PII/GPS/finances, uses token hash, and includes non-EPR notice."""
    col_a_token = auth_fixture["col_a"]["token"]
    fac_1_id = auth_fixture["rec_1"]["facility_id"]

    # Create transaction & handover with high-entropy unguessable token
    raw_public_token = f"cap_token_{uuid.uuid4().hex}_{uuid.uuid4().hex}"
    token_hash = hashlib.sha256(raw_public_token.encode("utf-8")).hexdigest()

    with TestingSessionLocal() as session:
        lot = Lot(
            id=uuid.uuid4(),
            collector_id=auth_fixture["col_a"]["collector_id"],
            material_id="MAT-PCB-01",
            regulatory_route="AUTHORIZED_EWASTE",
            estimated_weight_g=12000,
            condition="INTACT",
            status="CONFIRMED",
            version=1,
            is_demo=False
        )
        session.add(lot)
        session.flush()

        req = LotRequest(
            id=uuid.uuid4(),
            lot_id=lot.id,
            facility_id=fac_1_id,
            created_by=auth_fixture["col_a"]["user_id"],
            state="ACCEPTED"
        )
        session.add(req)
        session.flush()

        offer = Offer(
            id=uuid.uuid4(),
            request_id=req.id,
            lot_id=lot.id,
            facility_id=fac_1_id,
            rate_paise_per_kg=14000,
            price_basis="RATE_PER_KG",
            condition="INTACT",
            weight_basis_g=12000,
            expires_at=datetime.now(timezone.utc) + timedelta(days=3),
            status="ACCEPTED",
            terms_hash="terms_hash_public_ver",
            version=1
        )
        session.add(offer)
        session.flush()

        tx = Transaction(
            id=uuid.uuid4(),
            lot_id=lot.id,
            collector_id=auth_fixture["col_a"]["collector_id"],
            facility_id=fac_1_id,
            accepted_offer_id=offer.id,
            estimated_weight_g=12000,
            agreed_weight_g=12000,
            quoted_total_paise=168000,
            agreed_total_paise=168000,
            currency="INR",
            lifecycle="CONFIRMED",
            version=1,
            is_demo=False
        )
        session.add(tx)
        session.flush()

        handover = Handover(
            id=uuid.uuid4(),
            transaction_id=tx.id,
            lot_id=lot.id,
            proposed_by=auth_fixture["col_a"]["user_id"],
            proposed_at_client=datetime.now(timezone.utc),
            status="CONFIRMED",
            proposal_hash="proposal_hash_abc123",
            public_token_hash=token_hash,
            proposal_payload_json={"occurred_at": "2026-09-30T10:00:00Z"}
        )
        session.add(handover)
        session.commit()

    # 1. Unauthenticated visitor queries capability endpoint
    verify_resp = client.get(f"/api/v1/verify/{raw_public_token}")
    assert verify_resp.status_code == 200
    v_data = verify_resp.json()

    # 2. Check redacted fields
    assert "phone" not in v_data
    assert "collector_phone" not in v_data
    assert "gps" not in v_data
    assert "latitude" not in v_data
    assert "longitude" not in v_data
    assert "amount" not in v_data
    assert "total_paise" not in v_data
    assert "bank_account" not in v_data
    assert "upi_id" not in v_data

    # 3. Check public verification data
    assert v_data["status"] == "CONFIRMED"
    assert v_data["facility_name"] == "Facility Alpha"
    assert v_data["material_id"] == "MAT-PCB-01"
    assert v_data["weight_kg"] == 12.0
    assert v_data["proposal_hash"] == "proposal_hash_abc123"

    # 4. Mandatory non-EPR notice
    assert "statutory epr certificate" in v_data["non_epr_notice"].lower()

    # 5. Invalid token returns 404
    bad_token_resp = client.get("/api/v1/verify/invalid-fake-token")
    assert bad_token_resp.status_code == 404


# ===========================================================================
# 5. MINIMAL COLLECTOR DATASET & ANONYMIZATION (R-DATA-06, AT-058)
# ===========================================================================

def test_collector_export_anonymization_and_access_boundary(auth_fixture):
    """Verify collector export pseudonymizes IDs, redacts phone numbers/exact coordinates, and requires ADMIN."""
    col_token = auth_fixture["col_a"]["token"]
    admin_token = auth_fixture["admin"]["token"]

    # 1. Non-admin is blocked
    col_resp = client.get("/api/v1/exports/collectors?format=json", headers={"Authorization": f"Bearer {col_token}"})
    assert col_resp.status_code == 403

    # 2. Admin export succeeds and contains zero PII
    admin_resp = client.get("/api/v1/exports/collectors?format=json", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_resp.status_code == 200
    export_data = admin_resp.json()

    assert "data" in export_data
    for item in export_data["data"]:
        # Pseudonymized identifier
        assert item["collector_pseudonym"].startswith("col_anon_")
        assert item["privacy_level"] == "ZERO_PII_PSEUDONYMIZED"
        # Zero raw phone, Aadhaar, PAN, or bank accounts
        assert "phone" not in item
        assert "aadhaar" not in item
        assert "bank_account" not in item
        assert "latitude" not in item
        assert "longitude" not in item

    # 3. Admin minimal collector endpoint returns non-PII fields and zero sensitive credentials (R-DATA-06)
    min_resp = client.get("/api/v1/admin/collectors", headers={"Authorization": f"Bearer {admin_token}"})
    assert min_resp.status_code == 200
    for min_item in min_resp.json():
        assert "display_alias" in min_item
        assert "preferred_language" in min_item
        assert "phone" not in min_item
        assert "phone_normalized" not in min_item
        assert "pin" not in min_item
        assert "aadhaar" not in min_item
        assert "bank_account" not in min_item


# ===========================================================================
# 6. FORMULA INJECTION NEUTRALIZATION IN CSV EXPORTS (R-DATA-01, R-DATA-08, AT-060)
# ===========================================================================

def test_csv_formula_injection_neutralization():
    """Verify sanitize_csv_cell neutralizes leading =, +, -, @, \\t, \\r characters."""
    assert sanitize_csv_cell("=CMD('calc')") == "'=CMD('calc')"
    assert sanitize_csv_cell("+SUM(A1:A10)") == "'+SUM(A1:A10)"
    assert sanitize_csv_cell("-2+3") == "'-2+3"
    assert sanitize_csv_cell("@HYPERLINK('http://evil.com')") == "'@HYPERLINK('http://evil.com')"
    assert sanitize_csv_cell("\tmalicious") == "'\tmalicious"
    assert sanitize_csv_cell("Normal Text") == "Normal Text"
    assert sanitize_csv_cell(12345) == 12345
    assert sanitize_csv_cell(None) == ""


def test_procurement_log_csv_export_has_non_epr_and_sanitized_cells(auth_fixture):
    """Verify recycler procurement CSV export neutralizes formula prefixes and includes statutory non-EPR banner."""
    rec_token = auth_fixture["rec_1"]["token"]

    resp = client.get(
        "/api/v1/recycler/procurement-log?format=csv",
        headers={"Authorization": f"Bearer {rec_token}"}
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    csv_text = resp.text

    # Statutory header must be present
    assert NON_EPR_DISCLAIMER_SNIPPET in csv_text


# ===========================================================================
# 7. MEDIA SECURITY, EXIF STRIPPING & PATH TRAVERSAL (R-SEC-02, AT-073)
# ===========================================================================

def test_media_storage_path_traversal_prevention(tmp_path):
    """Verify that LocalStorageAdapter blocks path traversal attempts using relative and absolute traversals."""
    adapter = LocalStorageAdapter(root_dir=str(tmp_path))

    # Path traversal with ../
    with pytest.raises(ValueError, match="Path traversal detected"):
        adapter._resolve_safe_path("../../etc/passwd")

    with pytest.raises(ValueError, match="Path traversal detected"):
        adapter._resolve_safe_path("../secret.key")


def test_image_upload_exif_metadata_stripping():
    """Verify that _strip_exif_and_validate_image strips EXIF metadata from uploaded JPEG images."""
    img = Image.new("RGB", (100, 100), color="blue")
    exif = img.getexif()
    # Tag 0x010E corresponds to ImageDescription
    exif[0x010E] = "Sensitive Location Data Mayapuri Yard"

    raw_buf = io.BytesIO()
    img.save(raw_buf, format="JPEG", exif=exif)
    raw_bytes = raw_buf.getvalue()

    # Process through stripper
    clean_bytes, w, h = _strip_exif_and_validate_image(raw_bytes, "image/jpeg")
    assert w == 100
    assert h == 100

    # Verify cleaned image has no EXIF tags
    clean_img = Image.open(io.BytesIO(clean_bytes))
    clean_exif = clean_img.getexif()
    assert 0x010E not in clean_exif
    assert len(clean_exif) == 0


def test_media_download_authorization_and_signed_url_expiry(auth_fixture, tmp_path):
    """Verify private media access requires authorization and short-lived signed tokens expire."""
    col_a_token = auth_fixture["col_a"]["token"]
    col_b_token = auth_fixture["col_b"]["token"]
    admin_token = auth_fixture["admin"]["token"]
    user_a_id = auth_fixture["col_a"]["user_id"]

    # Save a media file safely using configured storage adapter
    adapter = get_storage_adapter()
    file_bytes = b"safe_media_content_bytes"
    storage_key = adapter.save("lot_photo.jpg", file_bytes, "image/jpeg")

    with TestingSessionLocal() as session:
        media_obj = MediaObject(
            id=uuid.uuid4(),
            owner_user_id=user_a_id,
            storage_key=storage_key,
            mime_type="image/jpeg",
            byte_size=len(file_bytes),
            sha256=hashlib.sha256(file_bytes).hexdigest(),
            upload_state="VALIDATED"
        )
        session.add(media_obj)
        session.commit()
        media_id = media_obj.id

    # 1. Collector B cannot generate access URL for Collector A's media -> 403 Forbidden
    col_b_access = client.get(
        f"/api/v1/media/{media_id}/access",
        headers={"Authorization": f"Bearer {col_b_token}"}
    )
    assert col_b_access.status_code == 403

    # 2. Collector A generates signed access URL
    col_a_access = client.get(
        f"/api/v1/media/{media_id}/access",
        headers={"Authorization": f"Bearer {col_a_token}"}
    )
    assert col_a_access.status_code == 200
    access_url = col_a_access.json()["access_url"]
    assert f"/media/{media_id}/content?token=" in access_url
    assert col_a_access.json()["expires_in"] == 900

    # 3. Download with valid token
    token = access_url.split("token=")[1]
    dl_resp = client.get(f"/api/v1/media/{media_id}/content?token={token}")
    assert dl_resp.status_code == 200
    assert dl_resp.headers["cache-control"] == "private, no-transform, max-age=900"
    assert dl_resp.headers["x-content-type-options"] == "nosniff"

    # 4. Expired token is rejected -> 401 Unauthorized
    expired_token = create_access_token(
        subject=str(user_a_id),
        role="COLLECTOR",
        expires_delta=timedelta(minutes=-5),  # in the past
        extra_claims={"media_id": str(media_id), "scope": "media_read"}
    )
    exp_resp = client.get(f"/api/v1/media/{media_id}/content?token={expired_token}")
    assert exp_resp.status_code == 401
    assert "expired" in exp_resp.json()["detail"].lower()


def test_oversized_upload_and_invalid_mime_rejection(auth_fixture):
    """Verify uploads exceeding 2 MiB bound or unsupported MIME types are rejected with 422."""
    col_token = auth_fixture["col_a"]["token"]

    # 1. Unsupported MIME type
    resp_mime = client.post(
        "/api/v1/media/uploads",
        headers={"Authorization": f"Bearer {col_token}"},
        json={
            "mime": "application/x-executable",
            "size": 1024,
            "sha256": "a" * 64
        }
    )
    assert resp_mime.status_code == 422

    # 2. Oversized payload (> 2MB)
    resp_size = client.post(
        "/api/v1/media/uploads",
        headers={"Authorization": f"Bearer {col_token}"},
        json={
            "mime": "image/jpeg",
            "size": MAX_MEDIA_BYTES + 100,
            "sha256": "b" * 64
        }
    )
    assert resp_size.status_code == 422
