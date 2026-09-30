"""Validate curated licensed public image dataset manifest and splits (T032).
Checks schema compliance, zero split leakage, license attribution, and taxonomy linkage.
Conforms to R-ML-01, R-DATA-07, AT-044, AT-059.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = ROOT / "data/curated/ml_image_dataset"
CATALOG_PATH = ROOT / "data/curated/material_catalog/material_catalog.json"


def validate_dataset():
    errors = []

    # 1. Load files
    manifest_path = DATASET_DIR / "manifest.json"
    license_path = DATASET_DIR / "license_registry.json"
    splits_path = DATASET_DIR / "splits_summary.json"
    card_path = DATASET_DIR / "dataset_card.md"

    for p in (manifest_path, license_path, splits_path, card_path):
        if not p.is_file():
            errors.append(f"Missing required dataset file: {p.relative_to(ROOT)}")

    if errors:
        print("\n".join(errors))
        return False

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    with open(license_path, "r", encoding="utf-8") as f:
        licenses = json.load(f)
    with open(splits_path, "r", encoding="utf-8") as f:
        summary = json.load(f)
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    valid_materials = {m["material_id"] for m in catalog}
    valid_source_ids = {s["source_id"] for s in licenses}

    print(f"Auditing {len(manifest)} image records across {len(valid_materials)} taxonomy materials...")

    # 2. Check each image record
    groups_to_splits = {}
    seen_image_ids = set()
    seen_filenames = set()

    for idx, rec in enumerate(manifest):
        img_id = rec.get("image_id")
        if not img_id or img_id in seen_image_ids:
            errors.append(f"Record {idx}: Missing or duplicate image_id '{img_id}'")
        seen_image_ids.add(img_id)

        filename = rec.get("filename")
        if not filename or filename in seen_filenames:
            errors.append(f"Record {idx}: Missing or duplicate filename '{filename}'")
        seen_filenames.add(filename)

        sha256 = rec.get("sha256")
        if not sha256 or len(sha256) != 64 or not all(c in "0123456789abcdef" for c in sha256.lower()):
            errors.append(f"Record {idx}: Invalid SHA-256 hash '{sha256}'")

        mat_id = rec.get("material_id")
        if mat_id not in valid_materials:
            errors.append(f"Record {idx}: Unknown material_id '{mat_id}' (not in authoritative taxonomy)")

        src_id = rec.get("source_id")
        if src_id not in valid_source_ids:
            errors.append(f"Record {idx}: Unregistered source_id '{src_id}'")

        split = rec.get("split")
        if split not in ("TRAIN", "VAL", "TEST"):
            errors.append(f"Record {idx}: Invalid split '{split}'")

        # Group leakage check
        obj_group = rec.get("physical_object_group")
        if not obj_group:
            errors.append(f"Record {idx}: Missing physical_object_group")
        else:
            if obj_group in groups_to_splits:
                if groups_to_splits[obj_group] != split:
                    errors.append(
                        f"Split Leakage Detected: Group '{obj_group}' is present in both '{groups_to_splits[obj_group]}' and '{split}'!"
                    )
            else:
                groups_to_splits[obj_group] = split

        # Tabular links must be strictly null (R-DATA-07)
        if rec.get("observed_weight_g") is not None:
            errors.append(f"Record {idx}: observed_weight_g must remain null per R-DATA-07")
        if rec.get("observed_price_paise") is not None:
            errors.append(f"Record {idx}: observed_price_paise must remain null per R-DATA-07")
        if rec.get("observed_location_id") is not None:
            errors.append(f"Record {idx}: observed_location_id must remain null per R-DATA-07")

        # Provenance: no fake field image claims
        if rec.get("origin_class") != "EXTERNAL_PUBLIC":
            errors.append(f"Record {idx}: origin_class must be EXTERNAL_PUBLIC (got '{rec.get('origin_class')}')")
        if rec.get("source_kind") != "LICENSED_IMAGE_DATASET":
            errors.append(f"Record {idx}: source_kind must be LICENSED_IMAGE_DATASET (got '{rec.get('source_kind')}')")

    # 3. Check License Registry
    for lic in licenses:
        for req_field in ("source_id", "dataset_name", "license_name", "license_url", "upstream_url", "permitted_uses"):
            if not lic.get(req_field):
                errors.append(f"License entry {lic.get('source_id')}: Missing required field '{req_field}'")

    if errors:
        print(f"Validation FAILED with {len(errors)} error(s):")
        for err in errors[:20]:
            print(f"  - {err}")
        return False

    print("PASS: 0 errors.")
    print(f"Verified {len(manifest)} images in {len(groups_to_splits)} physical object groups.")
    print("Zero split leakage: all physical object groups are strictly contained within a single split.")
    print("Zero field image claims: all records correctly identified as EXTERNAL_PUBLIC / LICENSED_IMAGE_DATASET.")
    print("Nullable tabular links: observed weight, price, and location remain null without synthetic invention.")
    return True


if __name__ == "__main__":
    ok = validate_dataset()
    sys.exit(0 if ok else 1)
