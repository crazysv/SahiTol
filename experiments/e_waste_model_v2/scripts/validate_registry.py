"""Validate the isolated e-waste-v2 candidate registry.

This script intentionally does not download data or train a model. It makes
the source eligibility decision inspectable before a Colab run begins.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "source_registry.json"
REQUIRED = {"id", "title", "url", "license", "status", "reported_size", "allowed_mappings", "blockers"}


def main() -> int:
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    statuses = payload["policy"]["allowed_training_statuses"]
    errors: list[str] = []
    eligible: list[str] = []
    held: list[str] = []

    seen: set[str] = set()
    for source in payload.get("sources", []):
        source_id = source.get("id", "<missing>")
        missing = REQUIRED - set(source)
        if missing:
            errors.append(f"{source_id}: missing {', '.join(sorted(missing))}")
        if source_id in seen:
            errors.append(f"duplicate source id: {source_id}")
        seen.add(source_id)
        if not str(source.get("url", "")).startswith("https://"):
            errors.append(f"{source_id}: URL must use https")
        if not source.get("blockers"):
            errors.append(f"{source_id}: must explicitly state audit blockers")
        if source.get("status") in statuses:
            eligible.append(source_id)
        else:
            held.append(source_id)

    if len(seen) != 6:
        errors.append(f"expected six candidates, found {len(seen)}")
    print(f"Registry: {REGISTRY}")
    print(f"Eligible only after asset audit: {', '.join(eligible) or 'none'}")
    print(f"Held/pending — prohibited from training: {', '.join(held) or 'none'}")
    if errors:
        print("FAILED")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("PASS — registry policy is internally consistent; this is not a licence clearance for individual files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
