"""Inspect staged Mendeley images and emit a source-native candidate CSV.

The output is deliberately *not* an accepted SahiTol asset ledger. It records
provider labels and proposed safe mappings, leaving ambiguous classes unmapped.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ID = "MENDELEY_BANGLADESHI_2025"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}

# Only direct, non-hazardous whole-device mappings get a SahiTol value.  Others
# stay blank, rather than pretending source-native classes distinguish grade or
# battery chemistry.
MAPPING = {
    "keyboard": "MAT-MIX-01",
    "mobile": "MAT-MIX-01",
    "mouse": "MAT-MIX-01",
    "pcb": "",
    "battery waste": "",
    "plastic waste": "",
    "metal waste": "",
    "glass waste": "",
    "light bulb": "",
    "medical waste": "",
    "organic waste": "",
    "paper waste": "",
}


def normalized_label(path: Path) -> str:
    """Use the nearest named folder as a provider label without inventing one."""
    return re.sub(r"[_-]+", " ", path.parent.name).strip().lower()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=ROOT / "data" / "raw" / SOURCE_ID / "extracted")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "prepared" / "mendeley_candidates.csv")
    args = parser.parse_args()
    files = sorted(path for path in args.input_dir.rglob("*") if path.suffix.lower() in IMAGE_SUFFIXES)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    counter: Counter[str] = Counter()
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=[
            "file_path", "source_id", "original_url", "license", "attribution",
            "provider_label", "proposed_sahitol_material_id", "provider_object_group", "status",
        ])
        writer.writeheader()
        for image in files:
            label = normalized_label(image)
            proposed = MAPPING.get(label, "")
            counter[label] += 1
            writer.writerow({
                "file_path": str(image.resolve()),
                "source_id": SOURCE_ID,
                "original_url": "https://data.mendeley.com/datasets/77383kmdnw/1",
                "license": "CC BY 4.0",
                "attribution": "Afrin, Tanzila; Azmi, Azizul Abedin (2025)",
                "provider_label": label,
                "proposed_sahitol_material_id": proposed,
                "provider_object_group": image.stem,
                "status": "DIRECT_MAPPING_CANDIDATE" if proposed else "SOURCE_NATIVE_ONLY",
            })
    report = {"image_count": len(files), "provider_label_counts": dict(sorted(counter.items())), "output": str(args.output)}
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
