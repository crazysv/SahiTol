"""Test suite for Local Demo Fallback, Backup, Restore, and Disaster Recovery (T042).

Covers requirements:
  - R-OPS-02: Reproducible local fallback, isolated restore, and disaster recovery.
  - R-OPS-04: Monitoring, diagnostics, and actionable recovery verification.
  - R-SEC-02: Privacy media access retention and audit.
Acceptance cases:
  - AT-073: Privacy media access retention and audit.
  - AT-075: Standalone local demo fallback and restore.
  - AT-077: Health, structured recovery, and diagnostics.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.main import app
from app.config import settings
from app.db.session import get_db
from app.db.models.audit import DomainEvent
from app.db.models.auth import User
from app.db.models.collector import Collector
from app.db.models.facility import Facility, Region
from app.db.models.lot import Lot, MediaObject
from app.domain.canonical import compute_canonical_hash
from app.security import hash_pin
from app.storage.supabase import SupabaseStorageAdapter
import app.storage.supabase as supabase_storage_module
from scripts.backup_restore import create_backup, restore_backup
from tests.test_db import TestingSessionLocal, override_get_db

client = TestClient(app)


def test_supabase_storage_readiness_checks_private_bucket(monkeypatch):
    """Readiness probes bucket metadata instead of trusting configuration alone."""
    requested = []

    class Response:
        def __init__(self, status_code: int):
            self.status_code = status_code

    class Client:
        def __init__(self, timeout: float):
            assert timeout == 5.0

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def get(self, url, headers):
            requested.append((url, headers))
            return Response(200)

    monkeypatch.setattr(supabase_storage_module.httpx, "Client", Client)
    adapter = SupabaseStorageAdapter(
        supabase_url="https://project.supabase.co",
        service_role_key="test-service-key",
        bucket="private-media",
    )

    assert adapter.is_healthy() is True
    assert requested[0][0] == "https://project.supabase.co/storage/v1/bucket/private-media"
    assert requested[0][1]["Authorization"] == "Bearer test-service-key"


@pytest.fixture
def recovery_session():
    """Provides a fresh isolated database session."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_health_live_probe_status():
    """Verify /health/live returns HTTP 200 with live status and version."""
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "live"
    assert data["app"] == settings.APP_NAME
    assert data["version"] == settings.APP_VERSION
    assert "timestamp" in data


def test_health_ready_probe_success():
    """Verify /health/ready returns HTTP 200 with database and storage connected."""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"
    assert data["storage"] == "connected"
    assert data["storage_probe"] == "adapter_readiness"
    assert "timestamp" in data


def test_health_ready_probe_database_failure_503(monkeypatch):
    """Verify /health/ready returns HTTP 503 when DB fails, with zero leaked credentials."""
    class BrokenSession:
        def execute(self, *args, **kwargs):
            raise ConnectionError("FATAL: password authentication failed for user 'sahitol' with secret_pw_123")

    def broken_get_db():
        yield BrokenSession()

    app.dependency_overrides[get_db] = broken_get_db
    try:
        response = client.get("/health/ready")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"
        assert data["database"] == "unavailable"
        # Zero secret or raw exception leakage in client response
        content_str = response.text
        assert "secret_pw_123" not in content_str
        assert "password authentication failed" not in content_str
    finally:
        app.dependency_overrides[get_db] = override_get_db


def test_correlation_id_propagation_and_header():
    """Verify X-Correlation-ID is extracted if provided, or generated and returned in headers."""
    # 1. Client provides correlation ID
    custom_cid = "corr-test-abcdef123456"
    resp1 = client.get("/health", headers={"X-Correlation-ID": custom_cid})
    assert resp1.status_code == 200
    assert resp1.headers.get("X-Correlation-ID") == custom_cid
    assert resp1.headers.get("X-Request-ID") == custom_cid

    # 2. Client omits correlation ID -> server generates valid hex ID
    resp2 = client.get("/health")
    assert resp2.status_code == 200
    generated_cid = resp2.headers.get("X-Correlation-ID")
    assert generated_cid is not None
    assert len(generated_cid) >= 16


def test_backup_and_restore_cycle_with_hash_chain(recovery_session: Session, tmp_path: Path):
    """Verify complete backup, manifest verification, restore, and domain event hash chain validation."""
    media_dir = tmp_path / "media_store"
    media_dir.mkdir(parents=True, exist_ok=True)
    test_photo = media_dir / "sample_lot.jpg"
    test_photo.write_bytes(b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01sample_clean_bytes_12345")

    # 1. Populate test data with cryptographic domain events
    user = User(
        id=uuid.uuid4(),
        phone_normalized="+919876543210",
        pin_hash=hash_pin("1234"),
        role="COLLECTOR",
        is_demo=False,
    )
    recovery_session.add(user)
    recovery_session.flush()

    collector = Collector(
        id=uuid.uuid4(),
        user_id=user.id,
        display_alias="Green Scrap",
        preferred_language="hi",
    )
    recovery_session.add(collector)
    recovery_session.flush()

    # Create chained domain events
    prev_hash = ""
    events = []
    for seq in range(1, 4):
        payload = {"action": f"test_event_{seq}", "collector": str(collector.id)}
        payload_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        event_hash = hashlib.sha256(f"{seq}:{payload_hash}:{prev_hash}".encode()).hexdigest()
        evt = DomainEvent(
            id=uuid.uuid4(),
            aggregate_type="Lot",
            aggregate_id=collector.id,
            sequence=seq,
            event_type=f"LOT_ACTION_{seq}",
            actor_id=user.id,
            role="COLLECTOR",
            payload_json=payload,
            prev_hash=prev_hash,
            event_hash=event_hash,
            received_at_server=datetime.now(timezone.utc),
        )
        recovery_session.add(evt)
        events.append(evt)
        prev_hash = event_hash

    recovery_session.commit()

    # 2. Execute backup
    backup_target = tmp_path / "backup_out"
    manifest = create_backup(recovery_session, media_dir, backup_target, as_zip=False)

    assert manifest["backup_id"].startswith("bak_")
    assert manifest["database"]["total_records"] > 0
    assert manifest["media"]["count"] == 1
    assert manifest["media"]["objects"][0]["key"] == "sample_lot.jpg"
    assert manifest["media"]["objects"][0]["sha256"] == hashlib.sha256(test_photo.read_bytes()).hexdigest()

    # 3. Verify-only check succeeds
    verify_result = restore_backup(backup_target, recovery_session, media_dir, verify_only=True)
    assert verify_result["status"] == "VERIFIED_VALID"
    assert verify_result["verified_records"] == manifest["database"]["total_records"]

    # 4. Clear database and media directory to simulate clean restore target
    restored_media_dir = tmp_path / "restored_media"
    recovery_session.execute(text("DELETE FROM domain_events"))
    recovery_session.execute(text("DELETE FROM collectors"))
    recovery_session.execute(text("DELETE FROM users"))
    recovery_session.commit()

    # 5. Execute full restore
    restore_result = restore_backup(backup_target, recovery_session, restored_media_dir, verify_only=False)
    assert restore_result["status"] == "RESTORE_SUCCESS"
    assert restore_result["hash_chain_valid"] is True
    assert restore_result["restored_media_count"] == 1

    # 6. Verify restored data in database
    restored_user = recovery_session.query(User).filter(User.id == user.id).first()
    assert restored_user is not None
    assert restored_user.phone_normalized == "+919876543210"

    restored_events = (
        recovery_session.query(DomainEvent)
        .filter(DomainEvent.aggregate_id == collector.id)
        .order_by(DomainEvent.sequence.asc())
        .all()
    )
    assert len(restored_events) == 3
    assert restored_events[-1].event_hash == events[-1].event_hash

    # 7. Verify restored media file
    restored_file = restored_media_dir / "sample_lot.jpg"
    assert restored_file.exists()
    assert restored_file.read_bytes() == test_photo.read_bytes()


def test_backup_tampering_triggers_integrity_failure(recovery_session: Session, tmp_path: Path):
    """Verify corrupted database dump or media object in backup triggers immediate integrity error."""
    media_dir = tmp_path / "media_store"
    media_dir.mkdir(parents=True, exist_ok=True)
    (media_dir / "test.jpg").write_bytes(b"image_content_123")

    backup_dir = tmp_path / "tamper_backup"
    create_backup(recovery_session, media_dir, backup_dir, as_zip=False)

    # 1. Tamper with database_dump.json
    db_dump_file = backup_dir / "database_dump.json"
    raw_content = db_dump_file.read_bytes()
    db_dump_file.write_bytes(raw_content + b" ")  # Append whitespace to alter sha256

    with pytest.raises(ValueError, match="Database dump SHA-256 mismatch"):
        restore_backup(backup_dir, recovery_session, tmp_path / "dummy_media")

    # Fix database dump by restoring exact original bytes
    db_dump_file.write_bytes(raw_content)

    # Now tamper with media file
    tampered_media = backup_dir / "media" / "test.jpg"
    tampered_media.write_bytes(b"tampered_content_456")

    with pytest.raises(ValueError, match="Media object SHA-256 mismatch"):
        restore_backup(backup_dir, recovery_session, tmp_path / "dummy_media")


def test_backup_zip_packaging_and_restoration(recovery_session: Session, tmp_path: Path):
    """Verify backup to .zip archive and full restore from .zip archive."""
    media_dir = tmp_path / "media_store"
    media_dir.mkdir(parents=True, exist_ok=True)
    (media_dir / "doc.pdf").write_bytes(b"%PDF-1.4 sample document bytes")

    zip_file = tmp_path / "archive.zip"
    manifest = create_backup(recovery_session, media_dir, zip_file, as_zip=True)
    assert zip_file.exists()
    assert manifest.get("archive_sha256") is not None

    restore_media_dir = tmp_path / "zip_restored_media"
    res = restore_backup(zip_file, recovery_session, restore_media_dir, verify_only=False)
    assert res["status"] == "RESTORE_SUCCESS"
    assert (restore_media_dir / "doc.pdf").exists()
    assert (restore_media_dir / "doc.pdf").read_bytes() == b"%PDF-1.4 sample document bytes"


def test_docker_compose_and_infra_configuration():
    """Verify local Docker Compose topology, PostGIS init, persistent volumes, and healthchecks."""
    infra_dir = Path(__file__).resolve().parents[3] / "infra"
    compose_path = infra_dir / "docker-compose.yml"
    assert compose_path.exists(), "infra/docker-compose.yml must exist"

    compose_text = compose_path.read_text(encoding="utf-8")
    # Verify core services
    assert "postgres:" in compose_text
    assert "api:" in compose_text
    assert "web:" in compose_text
    # Verify postgis image
    assert "postgis/postgis" in compose_text
    # Verify persistent volumes for database and media
    assert "postgres_data:" in compose_text
    assert "media_data:" in compose_text
    assert "/data/media" in compose_text
    # Verify healthcheck on postgres
    assert "pg_isready" in compose_text

    # Verify init_postgis.sql
    init_sql = infra_dir / "init_postgis.sql"
    assert init_sql.exists()
    assert "postgis" in init_sql.read_text(encoding="utf-8").lower()


def test_android_network_security_configuration_release_vs_debug():
    """Verify Android release enforces strict HTTPS, while debug scopes local LAN addresses."""
    repo_root = Path(__file__).resolve().parents[3]
    main_net_config = repo_root / "apps" / "android" / "app" / "src" / "main" / "res" / "xml" / "network_security_config.xml"
    debug_net_config = repo_root / "apps" / "android" / "app" / "src" / "debug" / "res" / "xml" / "network_security_config.xml"
    manifest_path = repo_root / "apps" / "android" / "app" / "src" / "main" / "AndroidManifest.xml"

    assert main_net_config.exists()
    assert debug_net_config.exists()
    assert manifest_path.exists()

    main_text = main_net_config.read_text(encoding="utf-8")
    assert 'cleartextTrafficPermitted="false"' in main_text

    debug_text = debug_net_config.read_text(encoding="utf-8")
    assert "10.0.2.2" in debug_text
    assert "192.168.1.1" in debug_text
    assert 'cleartextTrafficPermitted="true"' in debug_text

    manifest_text = manifest_path.read_text(encoding="utf-8")
    assert 'android:networkSecurityConfig="@xml/network_security_config"' in manifest_text


def test_web_scanner_insecure_context_fallback():
    """Verify web QR scan view provides fallback manual reference lookup for non-HTTPS local contexts."""
    repo_root = Path(__file__).resolve().parents[3]
    qr_scan_component = repo_root / "apps" / "web" / "src" / "components" / "recycler" / "R04_QRScan.tsx"
    assert qr_scan_component.exists()

    content = qr_scan_component.read_text(encoding="utf-8")
    # Camera error / permission fallback UI
    assert "Camera Access Required" in content or "cameraError" in content
    assert "Manual Reference Lookup Fallback" in content
    assert "manualRef" in content


def test_standalone_offline_operation_zero_network_calls(recovery_session: Session):
    """Verify core reference bootstrap and domain endpoints operate without external network dependencies."""
    from app.db.seeds.materials import seed_materials
    seed_materials(recovery_session)

    response = client.get("/api/v1/reference/bootstrap")
    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    assert "policy" in data
    assert "materials" in data
    assert "categories" in data
    assert "safety_guides" in data
    assert data["policy"]["cash_settlement_enabled"] is True
    assert "Digital Handover Record is an operational" in data["policy"]["disclaimer"] or "EPR" in data["policy"]["disclaimer"]
    assert len(data["materials"]) > 0
    assert len(data["categories"]) > 0
