"""Dataset manifest generation with cryptographic hashes and provenance breakdowns.
Complies with docs/18_DATA_PROVENANCE.md (Section 7-8) and R-DATA-08 / R-DATA-11.
"""

from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .staging import save_csv


class FileManifestEntry(BaseModel):
    filename: str
    sha256: str
    byte_size: int
    row_count: int


class DatasetManifest(BaseModel):
    """Manifest describing a versioned dataset export package."""
    dataset_family: str
    schema_version: str = "v1.0"
    data_version: str = "v1.0"
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_records: int
    files: List[FileManifestEntry] = Field(default_factory=list)
    counts_by_origin_class: Dict[str, int] = Field(default_factory=dict)
    counts_by_source_kind: Dict[str, int] = Field(default_factory=dict)
    counts_by_is_demo: Dict[str, int] = Field(default_factory=dict)
    counts_by_review_status: Dict[str, int] = Field(default_factory=dict)
    quarantined_count: int = 0
    source_ids: List[str] = Field(default_factory=list)
    validation_status: str = "VALID"
    limitations: str = "Prototype data tooling; simulated demo fixtures explicitly partitioned."


def compute_file_sha256(filepath: Path | str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def generate_manifest(
    family: str,
    records: List[Dict[str, Any]],
    output_dir: Path | str,
    data_version: str = "v1.0",
    quarantined_count: int = 0,
    limitations: Optional[str] = None,
) -> DatasetManifest:
    """Export records as sanitized CSV and JSON, compute SHA-256 hashes, and write manifest.json."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    csv_file = out_path / f"{family}.csv"
    json_file = out_path / f"{family}.json"

    # Save CSV with formula injection defense
    save_csv(records, csv_file, sanitize=True)

    # Save canonical JSON
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    # Compute hashes and sizes
    files_manifest = []
    for fpath in (csv_file, json_file):
        files_manifest.append(
            FileManifestEntry(
                filename=fpath.name,
                sha256=compute_file_sha256(fpath),
                byte_size=fpath.stat().st_size,
                row_count=len(records),
            )
        )

    # Aggregate provenance breakdowns
    origin_counts: Dict[str, int] = {}
    source_kind_counts: Dict[str, int] = {}
    demo_counts: Dict[str, int] = {}
    review_counts: Dict[str, int] = {}
    source_ids = set()

    for r in records:
        origin = str(r.get("origin_class", "UNKNOWN"))
        origin_counts[origin] = origin_counts.get(origin, 0) + 1

        skind = str(r.get("source_kind", "UNKNOWN"))
        source_kind_counts[skind] = source_kind_counts.get(skind, 0) + 1

        is_d = str(r.get("is_demo", False)).lower()
        demo_counts[is_d] = demo_counts.get(is_d, 0) + 1

        rstat = str(r.get("review_status", "NOT_REVIEWED"))
        review_counts[rstat] = review_counts.get(rstat, 0) + 1

        sid = r.get("source_id")
        if sid:
            source_ids.add(str(sid))

    val_status = "WITH_QUARANTINE" if quarantined_count > 0 else "VALID"
    lims = limitations or "Reproducible tooling export; demo fixtures partitioned from official references."

    manifest = DatasetManifest(
        dataset_family=family,
        schema_version="v1.0",
        data_version=data_version,
        total_records=len(records),
        files=files_manifest,
        counts_by_origin_class=origin_counts,
        counts_by_source_kind=source_kind_counts,
        counts_by_is_demo=demo_counts,
        counts_by_review_status=review_counts,
        quarantined_count=quarantined_count,
        source_ids=sorted(list(source_ids)),
        validation_status=val_status,
        limitations=lims,
    )

    manifest_path = out_path / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(manifest.model_dump_json(indent=2))

    return manifest
