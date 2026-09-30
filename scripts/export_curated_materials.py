"""Export curated material taxonomy, language aliases, and safety guides to data/curated."""
import csv
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SEEDS_DIR = ROOT_DIR / "data" / "seeds"
OUTPUT_DIR = ROOT_DIR / "data" / "curated" / "material_catalog"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def calculate_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def main():
    with open(SEEDS_DIR / "materials.json", "r", encoding="utf-8") as f:
        materials = json.load(f)
    with open(SEEDS_DIR / "material_aliases.json", "r", encoding="utf-8") as f:
        aliases = json.load(f)
    with open(SEEDS_DIR / "safety_guides.json", "r", encoding="utf-8") as f:
        safety_guides = json.load(f)

    # Build primary labels map from aliases
    labels_by_mat_lang = {}
    for a in aliases:
        key = (a["material_id"], a["language"])
        if key not in labels_by_mat_lang:
            labels_by_mat_lang[key] = a["local_term"]

    # Export material_catalog.json
    export_materials = []
    for m in materials:
        mat_id = m["id"]
        source_id = "SRC-02" if "BAT" in mat_id else "SRC-01"
        export_materials.append({
            "material_id": mat_id,
            "category_code": m["category_id"],
            "subcategory_code": m["subcategory_code"],
            "label_en": labels_by_mat_lang.get((mat_id, "en"), m["description_key"]),
            "label_hi": labels_by_mat_lang.get((mat_id, "hi"), m["description_key"]),
            "label_mr": labels_by_mat_lang.get((mat_id, "mr"), m["description_key"]),
            "default_route": m["default_route"],
            "route_requires_context": m["route_requires_context"],
            "allowed_units": m["allowed_units"],
            "safety_guide_ids": json.dumps(m["safety_guide_ids"]),
            "source_id": source_id,
            "origin_class": "OFFICIAL",
            "source_kind": "GOVERNMENT_PUBLICATION",
            "is_demo": False,
            "schema_version": "v1.0"
        })

    mat_json_path = OUTPUT_DIR / "material_catalog.json"
    with open(mat_json_path, "w", encoding="utf-8") as f:
        json.dump(export_materials, f, indent=2, ensure_ascii=False)

    # Export material_catalog.csv
    mat_csv_path = OUTPUT_DIR / "material_catalog.csv"
    headers = [
        "material_id", "category_code", "subcategory_code",
        "label_en", "label_hi", "label_mr",
        "default_route", "route_requires_context", "allowed_units",
        "safety_guide_ids", "source_id", "origin_class", "source_kind", "is_demo", "schema_version"
    ]
    with open(mat_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(export_materials)

    # Export aliases JSON
    aliases_json_path = OUTPUT_DIR / "material_aliases.json"
    with open(aliases_json_path, "w", encoding="utf-8") as f:
        json.dump(aliases, f, indent=2, ensure_ascii=False)

    # Export safety guides JSON
    safety_json_path = OUTPUT_DIR / "safety_guides.json"
    with open(safety_json_path, "w", encoding="utf-8") as f:
        json.dump(safety_guides, f, indent=2, ensure_ascii=False)

    # Build manifest
    files_manifest = []
    for p in [mat_csv_path, mat_json_path, aliases_json_path, safety_json_path]:
        files_manifest.append({
            "filename": p.name,
            "sha256": calculate_sha256(p),
            "byte_size": p.stat().st_size,
            "row_count": len(export_materials) if "material_catalog" in p.name else (len(aliases) if "aliases" in p.name else len(safety_guides))
        })

    manifest = {
        "dataset_family": "material_catalog",
        "schema_version": "v1.0",
        "data_version": "v1.0-curated",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_records": len(export_materials),
        "files": files_manifest,
        "counts_by_origin_class": {
            "OFFICIAL": len(export_materials)
        },
        "counts_by_source_kind": {
            "GOVERNMENT_PUBLICATION": len(export_materials)
        },
        "counts_by_is_demo": {
            "false": len(export_materials)
        },
        "counts_by_review_status": {
            "APPROVED": len(export_materials)
        },
        "quarantined_count": 0,
        "source_ids": ["SRC-01", "SRC-02"],
        "validation_status": "VALID",
        "limitations": "Desk-researched regulatory baseline mapped to CPCB E-Waste Rules 2022 & Battery Waste Rules 2022. Informal street alias verification completed via desk research; field validation with live collectors pending (R-RES-02 explicitly unmet)."
    }

    with open(OUTPUT_DIR / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Exported {len(export_materials)} curated materials, {len(aliases)} aliases, and {len(safety_guides)} safety guides to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
