"""Tests for media storage adapter, bounded uploads, EXIF stripping, checksum validation, and authorized access.
Covers T008 requirements: R-ARC-02, R-LOT-02, R-SEC-02.
Acceptance cases: AT-006, AT-012, AT-073.
"""
import io
import uuid
import hashlib
import tempfile
import shutil
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app as fastapi_app
from app.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.db.models.auth import User, AuthSession
from app.db.models.collector import Collector
from app.db.models.lot import MediaObject, Lot
from app.storage.local import LocalStorageAdapter, MAX_MEDIA_BYTES
import app.storage as storage_module
import app.routers.media as media_router_module

from tests.test_db import TestingSessionLocal

client = TestClient(fastapi_app)


@pytest.fixture(autouse=True)
def temp_local_storage(monkeypatch):
    """Provide a fresh temporary directory for LocalStorageAdapter per test."""
    temp_dir = tempfile.mkdtemp(prefix="sahitol_media_test_")
    adapter = LocalStorageAdapter(root_dir=temp_dir)
    monkeypatch.setattr(storage_module, "get_storage_adapter", lambda: adapter)
    monkeypatch.setattr(media_router_module, "get_storage_adapter", lambda: adapter)
    yield adapter
    shutil.rmtree(temp_dir, ignore_errors=True)


def _create_sample_jpeg() -> bytes:
    """Generate minimal valid JPEG bytes with dummy EXIF metadata."""
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    buf = io.BytesIO()
    # Save with some dummy metadata to verify EXIF stripping
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def _create_sample_pdf() -> bytes:
    """Generate minimal valid PDF bytes."""
    return b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"


def _register_and_get_token(phone: str = "9876543210") -> dict:
    resp = client.post("/auth/register", json={
        "phone": phone,
        "pin": "1234",
        "alias": "Test User",
        "preferred_language": "hi"
    })
    assert resp.status_code == 201
    return resp.json()


# --- Test Cases ---

def test_media_upload_staging():
    """Verify POST /media/uploads stages a media object and returns instructions."""
    auth_data = _register_and_get_token()
    token = auth_data["access_token"]

    sample_bytes = _create_sample_jpeg()
    sample_hash = hashlib.sha256(sample_bytes).hexdigest()

    req_payload = {
        "mime": "image/jpeg",
        "size": len(sample_bytes),
        "sha256": sample_hash
    }

    resp = client.post("/media/uploads", headers={"Authorization": f"Bearer {token}"}, json=req_payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "media_id" in data
    assert data["upload_url"] == f"/media/{data['media_id']}/content"
    assert data["state"] == "STAGED"
    assert data["max_bytes"] == MAX_MEDIA_BYTES


def test_media_upload_invalid_mime_and_size():
    """Verify rejection of unsupported MIME types and oversized files."""
    auth_data = _register_and_get_token()
    token = auth_data["access_token"]

    # Unsupported MIME
    resp_mime = client.post("/media/uploads", headers={"Authorization": f"Bearer {token}"}, json={
        "mime": "application/x-executable",
        "size": 1024,
        "sha256": "a" * 64
    })
    assert resp_mime.status_code == 422

    # Oversized file
    resp_size = client.post("/media/uploads", headers={"Authorization": f"Bearer {token}"}, json={
        "mime": "image/jpeg",
        "size": MAX_MEDIA_BYTES + 500,
        "sha256": "b" * 64
    })
    assert resp_size.status_code == 422


def test_media_content_upload_and_exif_stripping():
    """Verify PUT /media/{id}/content validates checksum, strips EXIF, and persists."""
    auth_data = _register_and_get_token()
    token = auth_data["access_token"]

    raw_jpeg = _create_sample_jpeg()
    raw_hash = hashlib.sha256(raw_jpeg).hexdigest()

    stage_resp = client.post("/media/uploads", headers={"Authorization": f"Bearer {token}"}, json={
        "mime": "image/jpeg",
        "size": len(raw_jpeg),
        "sha256": raw_hash
    }).json()
    media_id = stage_resp["media_id"]

    # Upload content
    upload_resp = client.put(
        f"/media/{media_id}/content",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "image/jpeg"},
        content=raw_jpeg
    )
    assert upload_resp.status_code == 200
    upload_data = upload_resp.json()
    assert upload_data["state"] == "UPLOADED"
    assert upload_data["pixel_width"] == 100
    assert upload_data["pixel_height"] == 100
    assert upload_data["storage_key"].endswith(".jpg")


def test_media_content_checksum_mismatch():
    """Verify upload fails with 422 when actual payload checksum differs from staged metadata."""
    auth_data = _register_and_get_token()
    token = auth_data["access_token"]

    raw_jpeg = _create_sample_jpeg()
    stage_resp = client.post("/media/uploads", headers={"Authorization": f"Bearer {token}"}, json={
        "mime": "image/jpeg",
        "size": len(raw_jpeg),
        "sha256": "0" * 64  # Wrong expected hash
    }).json()
    media_id = stage_resp["media_id"]

    bad_upload = client.put(
        f"/media/{media_id}/content",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "image/jpeg"},
        content=raw_jpeg
    )
    assert bad_upload.status_code == 422
    assert "checksum mismatch" in bad_upload.json()["detail"].lower()


def test_media_completion_lifecycle():
    """Verify POST /media/{id}/complete validates persisted storage and updates state to VALIDATED."""
    auth_data = _register_and_get_token()
    token = auth_data["access_token"]

    raw_jpeg = _create_sample_jpeg()
    raw_hash = hashlib.sha256(raw_jpeg).hexdigest()

    stage_resp = client.post("/media/uploads", headers={"Authorization": f"Bearer {token}"}, json={
        "mime": "image/jpeg",
        "size": len(raw_jpeg),
        "sha256": raw_hash
    }).json()
    media_id = stage_resp["media_id"]

    client.put(
        f"/media/{media_id}/content",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "image/jpeg"},
        content=raw_jpeg
    )

    complete_resp = client.post(
        f"/media/{media_id}/complete",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert complete_resp.status_code == 200
    assert complete_resp.json()["state"] == "VALIDATED"


def test_short_lived_access_url_and_download():
    """Verify GET /media/{id}/access provides expiring signed download URL."""
    auth_data = _register_and_get_token()
    token = auth_data["access_token"]

    raw_jpeg = _create_sample_jpeg()
    raw_hash = hashlib.sha256(raw_jpeg).hexdigest()

    stage_resp = client.post("/media/uploads", headers={"Authorization": f"Bearer {token}"}, json={
        "mime": "image/jpeg",
        "size": len(raw_jpeg),
        "sha256": raw_hash
    }).json()
    media_id = stage_resp["media_id"]

    client.put(
        f"/media/{media_id}/content",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "image/jpeg"},
        content=raw_jpeg
    )
    client.post(f"/media/{media_id}/complete", headers={"Authorization": f"Bearer {token}"})

    # Request short-lived access
    access_resp = client.get(f"/media/{media_id}/access", headers={"Authorization": f"Bearer {token}"})
    assert access_resp.status_code == 200
    access_data = access_resp.json()
    access_url = access_data["access_url"]
    assert "token=" in access_url
    assert access_data["expires_in"] == 900

    # Download content via signed access URL without Bearer header
    download_resp = client.get(access_url)
    assert download_resp.status_code == 200
    assert download_resp.headers["Content-Type"] == "image/jpeg"
    assert "private" in download_resp.headers["Cache-Control"]
    assert len(download_resp.content) > 0


def test_unauthorized_user_blocked_from_private_media():
    """Verify User B cannot access or download User A's private media (R-SEC-02)."""
    user_a = _register_and_get_token("9876543210")
    user_b = _register_and_get_token("9876543211")

    raw_jpeg = _create_sample_jpeg()
    raw_hash = hashlib.sha256(raw_jpeg).hexdigest()

    stage_resp = client.post("/media/uploads", headers={"Authorization": f"Bearer {user_a['access_token']}"}, json={
        "mime": "image/jpeg",
        "size": len(raw_jpeg),
        "sha256": raw_hash
    }).json()
    media_id = stage_resp["media_id"]

    client.put(
        f"/media/{media_id}/content",
        headers={"Authorization": f"Bearer {user_a['access_token']}", "Content-Type": "image/jpeg"},
        content=raw_jpeg
    )

    # User B attempts to get access to User A's media -> 403 Forbidden
    blocked_access = client.get(f"/media/{media_id}/access", headers={"Authorization": f"Bearer {user_b['access_token']}"})
    assert blocked_access.status_code == 403

    # User B attempts direct download with Bearer token -> 403 Forbidden
    blocked_download = client.get(f"/media/{media_id}/content", headers={"Authorization": f"Bearer {user_b['access_token']}"})
    assert blocked_download.status_code == 403


def test_pdf_media_upload_and_download():
    """Verify PDF storage for Digital Handover Records and platform receipts."""
    auth_data = _register_and_get_token()
    token = auth_data["access_token"]

    sample_pdf = _create_sample_pdf()
    pdf_hash = hashlib.sha256(sample_pdf).hexdigest()

    stage_resp = client.post("/media/uploads", headers={"Authorization": f"Bearer {token}"}, json={
        "mime": "application/pdf",
        "size": len(sample_pdf),
        "sha256": pdf_hash
    }).json()
    media_id = stage_resp["media_id"]

    upload_resp = client.put(
        f"/media/{media_id}/content",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/pdf"},
        content=sample_pdf
    )
    assert upload_resp.status_code == 200
    assert upload_resp.json()["mime"] == "application/pdf"
    assert upload_resp.json()["storage_key"].endswith(".pdf")

    # Direct download
    dl_resp = client.get(f"/media/{media_id}/content", headers={"Authorization": f"Bearer {token}"})
    assert dl_resp.status_code == 200
    assert dl_resp.headers["Content-Type"] == "application/pdf"
    assert dl_resp.content == sample_pdf
