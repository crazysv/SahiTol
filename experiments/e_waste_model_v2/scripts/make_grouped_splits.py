"""Create deterministic 70/15/15 grouped splits from an accepted asset ledger."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def split_for(group: str, material: str, seed: str) -> str:
    """Stable class-aware group split without letting sibling photos cross sets."""
    value = int(hashlib.sha256(f"{seed}:{material}:{group}".encode()).hexdigest()[:8], 16) % 100
    return "TRAIN" if value < 70 else "VAL" if value < 85 else "TEST"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", default="SAHITOL_EWASTE_V2_20261002")
    args = parser.parse_args()

    with args.ledger.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        print("Ledger is empty.", file=sys.stderr)
        return 2

    group_to_split: dict[str, str] = {}
    class_groups: defaultdict[str, set[str]] = defaultdict(set)
    for row in rows:
        group = row["physical_object_group"]
        material = row["material_id"]
        class_groups[material].add(group)
        proposed = split_for(group, material, args.seed)
        previous = group_to_split.setdefault(group, proposed)
        if previous != proposed:
            print(f"Group {group} has conflicting material labels; require review.", file=sys.stderr)
            return 2

    for row in rows:
        row["split"] = group_to_split[row["physical_object_group"]]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(row["split"] for row in rows)
    overlaps = sum(1 for group in set(group_to_split) if len({row["split"] for row in rows if row["physical_object_group"] == group}) != 1)
    report = {
        "seed": args.seed,
        "asset_count": len(rows),
        "group_count": len(group_to_split),
        "split_counts": counts,
        "groups_crossing_splits": overlaps,
        "groups_per_class": {material: len(groups) for material, groups in sorted(class_groups.items())},
    }
    report_path = args.output.with_suffix(".summary.json")
    report_path.write_text(json.dumps(report, indent=2, default=dict), encoding="utf-8")
    print(json.dumps(report, indent=2, default=dict))
    return 0 if overlaps == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
