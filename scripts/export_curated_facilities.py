"""Export curated Delhi-NCR and Maharashtra facilities to data/curated/facilities."""
import csv
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

ROOT_DIR = Path(__file__).resolve().parents[1]
SEEDS_DIR = ROOT_DIR / "data" / "seeds"
OUTPUT_DIR = ROOT_DIR / "data" / "curated" / "facilities"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def calculate_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def main():
    seed_file = SEEDS_DIR / "facilities.json"
    with open(seed_file, "r", encoding="utf-8") as f:
        facilities = json.load(f)

    # 1. Export facilities.json
    fac_json_path = OUTPUT_DIR / "facilities.json"
    with open(fac_json_path, "w", encoding="utf-8") as f:
        json.dump(facilities, f, indent=2, ensure_ascii=False)

    # 2. Export facilities.csv
    fac_csv_path = OUTPUT_DIR / "facilities.csv"
    headers = [
        "facility_id", "name", "facility_type", "region_id", "district", "state",
        "public_address", "latitude", "longitude", "location_quality", "route",
        "registration_reference", "registration_status", "valid_from", "valid_until",
        "last_verified_at", "verification_level", "pickup_available", "service_area",
        "contact_public", "source_id", "origin_class", "source_kind", "is_demo"
    ]
    csv_rows = []
    for fac in facilities:
        row = {k: fac.get(k) for k in headers}
        # Flatten booleans and lists for CSV
        if row["pickup_available"] is None:
            row["pickup_available"] = ""
        csv_rows.append(row)

    with open(fac_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(csv_rows)

    # 3. Export authorizations JSON
    authorizations = []
    for fac in facilities:
        authorizations.append({
            "facility_id": fac["facility_id"],
            "route": fac["route"],
            "registration_reference": fac["registration_reference"],
            "registration_status": fac["registration_status"],
            "valid_from": fac.get("valid_from"),
            "valid_until": fac.get("valid_until"),
            "last_verified_at": fac.get("last_verified_at"),
            "verification_level": fac.get("verification_level"),
            "source_id": fac.get("source_id"),
            "is_demo": fac.get("is_demo", False)
        })

    auth_json_path = OUTPUT_DIR / "facility_authorizations.json"
    with open(auth_json_path, "w", encoding="utf-8") as f:
        json.dump(authorizations, f, indent=2, ensure_ascii=False)

    # 4. Export materials accepted JSON
    fac_materials = []
    for fac in facilities:
        for mat_id in fac.get("materials_accepted", []):
            fac_materials.append({
                "facility_id": fac["facility_id"],
                "material_id": mat_id,
                "route": fac["route"],
                "accepted": True
            })

    mats_json_path = OUTPUT_DIR / "facility_materials.json"
    with open(mats_json_path, "w", encoding="utf-8") as f:
        json.dump(fac_materials, f, indent=2, ensure_ascii=False)

    # 5. Build manifest
    now_iso = datetime.now(timezone.utc).isoformat()
    files_manifest = []
    for p in [fac_csv_path, fac_json_path, auth_json_path, mats_json_path]:
        files_manifest.append({
            "filename": p.name,
            "sha256": calculate_sha256(p),
            "byte_size": p.stat().st_size,
            "row_count": len(facilities) if "facilities" in p.name else (len(authorizations) if "authorizations" in p.name else len(fac_materials))
        })

    manifest = {
        "dataset_family": "facilities",
        "schema_version": "v1.0",
        "data_version": "v1.0-curated",
        "generated_at": now_iso,
        "total_records": len(facilities),
        "files": files_manifest,
        "counts_by_facility_type": {
            "RECYCLER": sum(1 for f in facilities if f.get("facility_type") == "RECYCLER"),
            "DISMANTLER": sum(1 for f in facilities if f.get("facility_type") == "DISMANTLER"),
            "COLLECTION_CENTRE": sum(1 for f in facilities if f.get("facility_type") == "COLLECTION_CENTRE"),
            "AGGREGATOR": sum(1 for f in facilities if f.get("facility_type") == "AGGREGATOR"),
        },
        "counts_by_verification_level": {
            "L3": sum(1 for f in facilities if f.get("verification_level") == "L3"),
            "L2": sum(1 for f in facilities if f.get("verification_level") == "L2"),
            "L0": sum(1 for f in facilities if f.get("verification_level") == "L0"),
        },
        "counts_by_region": {
            "DELHI_NCR": sum(1 for f in facilities if f.get("region_id") == "DELHI_NCR"),
            "MAHARASHTRA": sum(1 for f in facilities if f.get("region_id") == "MAHARASHTRA"),
        },
        "counts_by_origin_class": {
            "OFFICIAL": sum(1 for f in facilities if f.get("origin_class") == "OFFICIAL"),
            "SYNTHETIC": sum(1 for f in facilities if f.get("origin_class") == "SYNTHETIC")
        },
        "counts_by_source_kind": {
            "REGULATOR_LIST": sum(1 for f in facilities if f.get("source_kind") == "REGULATOR_LIST"),
            "GOVERNMENT_PUBLICATION": sum(1 for f in facilities if f.get("source_kind") == "GOVERNMENT_PUBLICATION"),
            "SYNTHETIC_GENERATOR": sum(1 for f in facilities if f.get("source_kind") == "SYNTHETIC_GENERATOR")
        },
        "counts_by_is_demo": {
            "false": sum(1 for f in facilities if not f.get("is_demo", False)),
            "true": sum(1 for f in facilities if f.get("is_demo", False))
        },
        "source_ids": ["SRC-01", "SRC-02", "SRC-04", "SRC-05", "SRC-06"],
        "validation_status": "VALID",
        "limitations": "Source-backed directory leads compiled from CPCB, DPCC, MPCB, and NDMC public registers. Actual operational pickup and quote rates remain unverified or self-declared; collection centres are strictly distinguished from recyclers; no formal commercial partnership or statutory EPR certification is implied or certified."
    }

    manifest_path = OUTPUT_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Exported {len(facilities)} facilities, {len(authorizations)} authorizations, and {len(fac_materials)} material mappings to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
