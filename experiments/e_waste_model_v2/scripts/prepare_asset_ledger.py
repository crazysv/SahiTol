"""Build an auditable experiment ledger from provider-supplied image metadata.

Input is a CSV with these columns:
file_path,source_id,original_url,license,attribution,provider_label,material_id,
provider_object_group

No labels are created here. `material_id` must be a direct, reviewed mapping
from a provider label; ambiguous items are excluded from this classifier
experiment and remain available for the application's manual fallback.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "source_registry.json"
REQUIRED_COLUMNS = {
    "file_path", "source_id", "original_url", "license", "attribution",
    "provider_label", "material_id", "provider_object_group",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data" / "prepared")
    args = parser.parse_args()

    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    allowed = set(registry["policy"]["allowed_training_statuses"])
    source_status = {item["id"]: item["status"] for item in registry["sources"]}

    with args.input.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        print("Input CSV is empty or unreadable.", file=sys.stderr)
        return 2
    missing = REQUIRED_COLUMNS - set(rows[0])
    if missing:
        print(f"Missing input columns: {', '.join(sorted(missing))}", file=sys.stderr)
        return 2

    args.output_dir.mkdir(parents=True, exist_ok=True)
    accepted: list[dict[str, str]] = []
    rejected: list[dict[str, str]] = []
    known_hashes: dict[str, str] = {}
    for row_number, row in enumerate(rows, start=2):
        reason = ""
        image = Path(row["file_path"]).expanduser()
        status = source_status.get(row["source_id"])
        if status not in allowed:
            reason = f"source status {status or 'UNKNOWN'} is not eligible"
        elif not image.is_file():
            reason = "file is missing"
        elif not row["original_url"].startswith("https://"):
            reason = "original_url must use https"
        elif not all(row[name].strip() for name in REQUIRED_COLUMNS - {"file_path"}):
            reason = "required provenance field is blank"
        elif not row["material_id"].startswith("MAT-"):
            reason = "material_id is not a direct SahiTol taxonomy mapping"

        image_hash = sha256(image) if not reason else ""
        if not reason and image_hash in known_hashes:
            reason = f"exact duplicate of accepted row {known_hashes[image_hash]}"
        if reason:
            rejected.append({"row": str(row_number), "file_path": row["file_path"], "reason": reason})
            continue

        known_hashes[image_hash] = str(row_number)
        accepted.append({
            "asset_id": f"EXP2-{len(accepted) + 1:06d}",
            "file_path": str(image.resolve()),
            "sha256": image_hash,
            "source_id": row["source_id"],
            "original_url": row["original_url"],
            "license": row["license"],
            "attribution": row["attribution"],
            "provider_label": row["provider_label"],
            "material_id": row["material_id"],
            "physical_object_group": f"{row['source_id']}::{row['provider_object_group']}",
        })

    columns = list(accepted[0]) if accepted else ["asset_id", "file_path", "sha256", "source_id", "original_url", "license", "attribution", "provider_label", "material_id", "physical_object_group"]
    with (args.output_dir / "asset_ledger.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(accepted)
    with (args.output_dir / "rejected_assets.json").open("w", encoding="utf-8") as stream:
        json.dump(rejected, stream, indent=2)

    print(f"Accepted: {len(accepted)}; rejected: {len(rejected)}")
    print(f"Ledger: {args.output_dir / 'asset_ledger.csv'}")
    return 0 if accepted else 1


if __name__ == "__main__":
    sys.exit(main())
