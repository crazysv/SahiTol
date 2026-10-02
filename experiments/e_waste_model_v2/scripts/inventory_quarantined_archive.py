"""Safely inventory a non-production, provenance-pending image archive.

This tool is deliberately *not* a training-data importer.  It exists so a
Roboflow or Kaggle archive can be inspected and hashed in an isolated Colab
experiment without weakening ``source_registry.json`` or the approved-model
ledger.  It does not create SahiTol labels, train a model, or copy files into
the product.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath

from PIL import Image, UnidentifiedImageError


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "source_registry.json"
QUARANTINED_SOURCE_IDS = {"ROBOFLOW_EWASTE_2025", "KAGGLE_AKSHAT_EWASTE"}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_extract(archive: Path, destination: Path) -> None:
    """Extract a ZIP only when every member stays inside ``destination``."""
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.infolist():
            member_path = PurePosixPath(member.filename)
            if member_path.is_absolute() or ".." in member_path.parts:
                raise ValueError(f"Unsafe ZIP member: {member.filename}")
        bundle.extractall(destination)


def provider_label(path: Path, extraction_root: Path) -> str:
    """Return the nearest non-generic parent directory as an observed label.

    This is source structure reporting, not semantic classification.  The
    resulting label must be reviewed before it can be mapped to an experiment
    class.
    """
    generic = {"images", "image", "train", "valid", "val", "test", "data", "dataset"}
    for parent in path.relative_to(extraction_root).parents:
        if parent == Path("."):
            break
        if parent.name.lower() not in generic:
            return parent.name
    return "UNRESOLVED_FROM_PATH"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-id", required=True, choices=sorted(QUARANTINED_SOURCE_IDS))
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    source = next(item for item in registry["sources"] if item["id"] == args.source_id)
    if not args.archive.is_file() or not zipfile.is_zipfile(args.archive):
        print("Expected a readable ZIP archive.", file=sys.stderr)
        return 2

    extraction_root = args.output_dir / "extracted"
    if extraction_root.exists():
        print(f"Refusing to overwrite existing extraction: {extraction_root}", file=sys.stderr)
        return 2
    extraction_root.mkdir(parents=True)
    try:
        safe_extract(args.archive, extraction_root)
    except (ValueError, zipfile.BadZipFile) as error:
        shutil.rmtree(extraction_root)
        print(f"Archive rejected: {error}", file=sys.stderr)
        return 2

    accepted: list[dict[str, str]] = []
    rejected: list[dict[str, str]] = []
    exact_hashes: set[str] = set()
    for file_path in sorted(extraction_root.rglob("*")):
        if not file_path.is_file() or file_path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        try:
            with Image.open(file_path) as image:
                image.verify()
        except (UnidentifiedImageError, OSError, ValueError) as error:
            rejected.append({"file_path": str(file_path), "reason": f"unreadable image: {error}"})
            continue
        digest = file_sha256(file_path)
        if digest in exact_hashes:
            rejected.append({"file_path": str(file_path), "reason": "exact duplicate inside archive"})
            continue
        exact_hashes.add(digest)
        accepted.append({
            "asset_id": f"QUAR-{args.source_id[:8]}-{len(accepted) + 1:06d}",
            "file_path": str(file_path.resolve()),
            "sha256": digest,
            "source_id": args.source_id,
            "observed_provider_label": provider_label(file_path, extraction_root),
            "quarantine_status": "PROVENANCE_PENDING_NOT_FOR_PRODUCT",
        })

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output_dir / "quarantined_asset_inventory.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(accepted[0]) if accepted else [
            "asset_id", "file_path", "sha256", "source_id", "observed_provider_label", "quarantine_status",
        ])
        writer.writeheader()
        writer.writerows(accepted)
    (args.output_dir / "quarantined_rejections.json").write_text(json.dumps(rejected, indent=2), encoding="utf-8")
    report = {
        "source_id": args.source_id,
        "source_status_at_inventory": source["status"],
        "archive_sha256": file_sha256(args.archive),
        "accepted_readable_unique_images": len(accepted),
        "rejected_files": len(rejected),
        "observed_provider_label_counts": dict(sorted(Counter(row["observed_provider_label"] for row in accepted).items())),
        "manifest": str(manifest_path),
        "guardrail": "Inventory only. This source remains quarantined and must not enter the approved model, APK, or release evidence.",
    }
    (args.output_dir / "quarantine_inventory_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
