#!/usr/bin/env python3
"""SahiTol Database & Media Backup, Restore, and Disaster Recovery Tool.

Fulfills requirements:
  - R-OPS-02: Reproducible local fallback, isolated restore, and disaster recovery.
  - R-OPS-04: Monitoring, diagnostics, and actionable recovery verification.
  - R-SEC-02: Privacy, media integrity, checksum validation, and audit preservation.

Acceptance cases:
  - AT-073: Privacy media access retention and audit.
  - AT-075: Standalone local demo fallback and restore.
  - AT-077: Health, structured recovery, and diagnostics.
"""
import argparse
import base64
from datetime import date, datetime, timezone
import hashlib
import json
import logging
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
from typing import Any, Dict, List, Optional
import uuid
import zipfile

# Add services/api to sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
API_DIR = REPO_ROOT / "services" / "api"
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
from app.db.base import Base
# Import all models to populate Base.metadata
import app.db.models  # noqa
from app.config import settings

try:
    from geoalchemy2.elements import WKBElement, WKTElement
    from geoalchemy2.shape import to_shape
except ImportError:
    WKBElement = None
    WKTElement = None
    to_shape = None

logger = logging.getLogger("sahitol.backup_restore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def compute_file_sha256(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_bytes_sha256(data: bytes) -> str:
    """Compute SHA-256 hash of byte buffer."""
    return hashlib.sha256(data).hexdigest()


def serialize_value(val: Any) -> Any:
    """Convert Python / SQLAlchemy column value to JSON-serializable representation."""
    if val is None:
        return None
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    if isinstance(val, uuid.UUID):
        return str(val)
    if isinstance(val, (bytes, memoryview)):
        return {"__b64__": base64.b64encode(bytes(val)).decode("ascii")}
    if WKBElement is not None and isinstance(val, WKBElement):
        try:
            shape = to_shape(val)
            return {"__geom__": shape.wkt, "srid": val.srid}
        except Exception:
            return {"__wkb_hex__": bytes(val.data).hex(), "srid": getattr(val, "srid", 4326)}
    if isinstance(val, (int, float, str, bool, list, dict)):
        return val
    # Fallback to string
    return str(val)


def deserialize_value(val: Any, column: Any) -> Any:
    """Convert JSON representation back to column Python type."""
    if val is None:
        return None
    if isinstance(val, dict):
        if "__b64__" in val:
            return base64.b64decode(val["__b64__"])
        if "__geom__" in val:
            if WKTElement is not None:
                return WKTElement(val["__geom__"], srid=val.get("srid", 4326))
            return val["__geom__"]
        if "__wkb_hex__" in val:
            raw_bytes = bytes.fromhex(val["__wkb_hex__"])
            if WKBElement is not None:
                return WKBElement(raw_bytes, srid=val.get("srid", 4326))
            return raw_bytes

    col_type_str = str(column.type).lower() if hasattr(column, "type") else ""
    if isinstance(val, str):
        if "uuid" in col_type_str:
            try:
                return uuid.UUID(val)
            except Exception:
                return val
        if "datetime" in col_type_str or "timestamp" in col_type_str:
            try:
                return datetime.fromisoformat(val)
            except Exception:
                return val
        if "date" in col_type_str:
            try:
                return date.fromisoformat(val)
            except Exception:
                return val
    return val


def create_backup(
    session: Session,
    media_dir: Path,
    output_target: Path,
    as_zip: bool = False
) -> Dict[str, Any]:
    """Execute complete database and media backup with cryptographic integrity manifest."""
    start_time = time.perf_counter()
    backup_id = f"bak_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

    temp_dir = Path(tempfile.mkdtemp(prefix="sahitol_backup_"))
    try:
        db_dump: Dict[str, List[Dict[str, Any]]] = {}
        table_counts: Dict[str, int] = {}
        total_records = 0

        # 1. Export database tables in topological order
        inspector = inspect(session.bind)
        existing_tables = set(inspector.get_table_names())
        sorted_tables = [t for t in Base.metadata.sorted_tables if t.name in existing_tables]
        for table in sorted_tables:
            table_name = table.name
            cols = [c.name for c in table.columns]
            rows = session.execute(table.select()).mappings().all()
            serialized_rows = []
            for row in rows:
                serialized_rows.append({col: serialize_value(row[col]) for col in cols})
            db_dump[table_name] = serialized_rows
            count = len(serialized_rows)
            table_counts[table_name] = count
            total_records += count

        db_dump_file = temp_dir / "database_dump.json"
        dump_json_bytes = json.dumps(db_dump, indent=2, ensure_ascii=False).encode("utf-8")
        db_dump_file.write_bytes(dump_json_bytes)
        db_dump_sha256 = compute_bytes_sha256(dump_json_bytes)

        # 2. Archive media objects with checksums
        media_records = []
        media_backup_dir = temp_dir / "media"
        media_backup_dir.mkdir(parents=True, exist_ok=True)
        total_media_bytes = 0

        if media_dir.exists() and media_dir.is_dir():
            for item in media_dir.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(media_dir).as_posix()
                    dest_file = media_backup_dir / rel_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_file)
                    file_sha = compute_file_sha256(item)
                    file_size = item.stat().st_size
                    total_media_bytes += file_size
                    media_records.append({
                        "key": rel_path,
                        "size_bytes": file_size,
                        "sha256": file_sha
                    })

        # 3. Read curated version manifests
        model_sha = "unknown"
        model_card = REPO_ROOT / "data" / "curated" / "model" / "model_card.md"
        if model_card.exists():
            model_sha = compute_file_sha256(model_card)

        audio_manifest_sha = "unknown"
        audio_clips_count = 0
        audio_manifest = REPO_ROOT / "data" / "curated" / "audio" / "audio_manifest.json"
        if audio_manifest.exists():
            audio_manifest_sha = compute_file_sha256(audio_manifest)
            try:
                audio_clips_count = len(json.loads(audio_manifest.read_text(encoding="utf-8")).get("clips", []))
            except Exception:
                pass

        duration_sec = round(time.perf_counter() - start_time, 4)

        # 4. Generate backup manifest
        manifest = {
            "manifest_version": "1.0",
            "backup_id": backup_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "demo_mode": settings.DEMO_MODE,
            "duration_seconds": duration_sec,
            "database": {
                "dump_file": "database_dump.json",
                "sha256": db_dump_sha256,
                "size_bytes": len(dump_json_bytes),
                "total_records": total_records,
                "tables": table_counts
            },
            "media": {
                "count": len(media_records),
                "total_bytes": total_media_bytes,
                "objects": media_records
            },
            "curated_versions": {
                "model_card_sha256": model_sha,
                "audio_manifest_sha256": audio_manifest_sha,
                "audio_clips_count": audio_clips_count
            }
        }

        manifest_file = temp_dir / "backup_manifest.json"
        manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

        # 5. Output packaging
        if as_zip or output_target.suffix == ".zip":
            output_target.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(output_target, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        full_path = Path(root) / file
                        arcname = full_path.relative_to(temp_dir).as_posix()
                        zipf.write(full_path, arcname)
            manifest["archive_sha256"] = compute_file_sha256(output_target)
            logger.info("Backup created successfully as zip: %s (SHA-256: %s)", output_target, manifest["archive_sha256"][:12])
        else:
            output_target.mkdir(parents=True, exist_ok=True)
            for item in temp_dir.iterdir():
                dest = output_target / item.name
                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
            logger.info("Backup created successfully in directory: %s", output_target)

        return manifest
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def restore_backup(
    backup_path: Path,
    session: Session,
    target_media_dir: Path,
    verify_only: bool = False
) -> Dict[str, Any]:
    """Restore database and media from a validated backup archive or directory.
    
    Performs full SHA-256 cryptographic verification of the database dump and all media
    objects before any database mutation. Verifies domain event hash-chains post-restore.
    """
    start_time = time.perf_counter()
    temp_dir: Optional[Path] = None

    if backup_path.is_file() and backup_path.suffix == ".zip":
        temp_dir = Path(tempfile.mkdtemp(prefix="sahitol_restore_"))
        with zipfile.ZipFile(backup_path, "r") as zipf:
            zipf.extractall(temp_dir)
        source_dir = temp_dir
    elif backup_path.is_dir():
        source_dir = backup_path
    else:
        raise ValueError(f"Invalid backup source: {backup_path}")

    try:
        manifest_file = source_dir / "backup_manifest.json"
        if not manifest_file.exists():
            raise ValueError(f"Missing backup_manifest.json in backup source: {source_dir}")

        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        backup_id = manifest.get("backup_id", "unknown")

        # 1. Verify Database Dump Integrity
        db_info = manifest["database"]
        dump_file = source_dir / db_info["dump_file"]
        if not dump_file.exists():
            raise ValueError(f"Database dump file missing: {dump_file}")

        computed_db_sha = compute_file_sha256(dump_file)
        if computed_db_sha != db_info["sha256"]:
            raise ValueError(
                f"Database dump SHA-256 mismatch! Expected {db_info['sha256']}, got {computed_db_sha}"
            )

        # 2. Verify All Media Objects Integrity
        media_info = manifest["media"]
        media_source_dir = source_dir / "media"
        for obj in media_info["objects"]:
            obj_path = media_source_dir / obj["key"]
            if not obj_path.exists():
                raise ValueError(f"Media object missing from backup: {obj['key']}")
            computed_obj_sha = compute_file_sha256(obj_path)
            if computed_obj_sha != obj["sha256"]:
                raise ValueError(
                    f"Media object SHA-256 mismatch for {obj['key']}! Expected {obj['sha256']}, got {computed_obj_sha}"
                )

        if verify_only:
            duration = round(time.perf_counter() - start_time, 4)
            return {
                "status": "VERIFIED_VALID",
                "backup_id": backup_id,
                "verified_tables": len(db_info["tables"]),
                "verified_records": db_info["total_records"],
                "verified_media_objects": len(media_info["objects"]),
                "duration_seconds": duration
            }

        # 3. Restore Database
        db_dump = json.loads(dump_file.read_text(encoding="utf-8"))
        inspector = inspect(session.bind)
        existing_tables = set(inspector.get_table_names())
        sorted_tables = [t for t in Base.metadata.sorted_tables if t.name in existing_tables]

        # Clear existing data in reverse dependency order
        for table in reversed(sorted_tables):
            session.execute(table.delete())
        session.flush()

        # Insert rows in topological dependency order
        restored_counts: Dict[str, int] = {}
        for table in sorted_tables:
            table_name = table.name
            rows_data = db_dump.get(table_name, [])
            if not rows_data:
                restored_counts[table_name] = 0
                continue

            col_map = {c.name: c for c in table.columns}
            deserialized_rows = []
            for row in rows_data:
                clean_row = {}
                for k, v in row.items():
                    if k in col_map:
                        clean_row[k] = deserialize_value(v, col_map[k])
                deserialized_rows.append(clean_row)

            session.execute(table.insert(), deserialized_rows)
            restored_counts[table_name] = len(deserialized_rows)
        session.commit()

        # 4. Restore Media Files
        target_media_dir.mkdir(parents=True, exist_ok=True)
        for obj in media_info["objects"]:
            src_file = media_source_dir / obj["key"]
            dest_file = target_media_dir / obj["key"]
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dest_file)

        # 5. Validate Domain Event Hash Chain Integrity per aggregate
        events = session.execute(
            text("SELECT id, aggregate_id, sequence, event_type, prev_hash, event_hash FROM domain_events ORDER BY aggregate_id, sequence ASC")
        ).mappings().all()

        hash_chain_valid = True
        current_agg = None
        prev_hash = None
        for evt in events:
            agg_id = evt["aggregate_id"]
            if agg_id != current_agg:
                current_agg = agg_id
                prev_hash = evt["event_hash"]
                continue

            expected_prev = prev_hash
            actual_prev = evt["prev_hash"]
            if expected_prev != actual_prev:
                hash_chain_valid = False
                logger.error(
                    "Domain event hash chain broken for aggregate %s at seq=%s: prev=%s actual=%s",
                    agg_id, evt["sequence"], expected_prev, actual_prev
                )
                break
            prev_hash = evt["event_hash"]

        duration = round(time.perf_counter() - start_time, 4)

        # Calculate data-loss window (difference between newest domain event timestamp and backup creation)
        data_loss_window_seconds = 0
        latest_event_time = session.execute(
            text("SELECT MAX(received_at_server) FROM domain_events")
        ).scalar()
        if latest_event_time:
            if isinstance(latest_event_time, str):
                latest_dt = datetime.fromisoformat(latest_event_time)
            else:
                latest_dt = latest_event_time
            if latest_dt.tzinfo is None:
                latest_dt = latest_dt.replace(tzinfo=timezone.utc)
            backup_dt = datetime.fromisoformat(manifest["created_at"])
            data_loss_window_seconds = max(0, int((backup_dt - latest_dt).total_seconds()))

        result = {
            "status": "RESTORE_SUCCESS",
            "backup_id": backup_id,
            "manifest_records": db_info["total_records"],
            "restored_records": sum(restored_counts.values()),
            "restored_media_count": len(media_info["objects"]),
            "hash_chain_valid": hash_chain_valid,
            "duration_seconds": duration,
            "data_loss_window_seconds": data_loss_window_seconds,
            "table_counts": restored_counts
        }
        logger.info(
            "Restore completed successfully: %d records, %d media files, duration=%.2fs, hash_chain_valid=%s",
            result["restored_records"], result["restored_media_count"], duration, hash_chain_valid
        )
        return result

    finally:
        if temp_dir is not None:
            shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description="SahiTol Backup and Disaster Recovery Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Backup command
    b_parser = subparsers.add_parser("backup", help="Create a backup snapshot")
    b_parser.add_argument("--output", "-o", required=True, help="Destination directory or .zip path")
    b_parser.add_argument("--media-dir", default=settings.LOCAL_MEDIA_ROOT, help="Media root directory")
    b_parser.add_argument("--zip", action="store_true", help="Package backup into a zip archive")

    # Restore command
    r_parser = subparsers.add_parser("restore", help="Restore from backup")
    r_parser.add_argument("--input", "-i", required=True, help="Backup directory or .zip file path")
    r_parser.add_argument("--media-dir", default=settings.LOCAL_MEDIA_ROOT, help="Media destination directory")
    r_parser.add_argument("--verify-only", action="store_true", help="Only verify cryptographic integrity without mutating database")

    args = parser.parse_args()

    from app.db.session import SessionLocal
    db = SessionLocal()

    try:
        if args.command == "backup":
            target = Path(args.output)
            media = Path(args.media_dir)
            manifest = create_backup(db, media, target, as_zip=args.zip)
            print(json.dumps(manifest, indent=2))
        elif args.command == "restore":
            src = Path(args.input)
            media = Path(args.media_dir)
            res = restore_backup(src, db, media, verify_only=args.verify_only)
            print(json.dumps(res, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()
