"""Generate labeled bundled demo reference cache for offline first Android launch.
Satisfies T009 & AT-038.
"""
import json
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SEEDS_DIR = ROOT_DIR / "data" / "seeds"
ANDROID_ASSETS_DIR = ROOT_DIR / "apps" / "android" / "app" / "src" / "main" / "assets"
CURATED_DIR = ROOT_DIR / "data" / "curated"

ANDROID_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
CURATED_DIR.mkdir(parents=True, exist_ok=True)


def calculate_sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main():
    with open(SEEDS_DIR / "material_categories.json", "r", encoding="utf-8") as f:
        categories = json.load(f)
    with open(SEEDS_DIR / "materials.json", "r", encoding="utf-8") as f:
        materials = json.load(f)
    with open(SEEDS_DIR / "material_aliases.json", "r", encoding="utf-8") as f:
        aliases = json.load(f)
    with open(SEEDS_DIR / "safety_guides.json", "r", encoding="utf-8") as f:
        safety_guides = json.load(f)

    # Benchmark prices
    benchmark_prices = [
        {"material_id": "MAT-PCB-01", "region_id": "DELHI_NCR", "q1_rate": 35000, "median_rate": 42000, "q3_rate": 48000, "unit": "kg", "confidence": "HIGH"},
        {"material_id": "MAT-PCB-02", "region_id": "DELHI_NCR", "q1_rate": 8000, "median_rate": 11000, "q3_rate": 14000, "unit": "kg", "confidence": "HIGH"},
        {"material_id": "MAT-BAT-01", "region_id": "DELHI_NCR", "q1_rate": 7500, "median_rate": 8200, "q3_rate": 9000, "unit": "kg", "confidence": "HIGH"},
        {"material_id": "MAT-BAT-02", "region_id": "DELHI_NCR", "q1_rate": 12000, "median_rate": 16000, "q3_rate": 20000, "unit": "kg", "confidence": "MEDIUM"},
        {"material_id": "MAT-BAT-03", "region_id": "DELHI_NCR", "q1_rate": 3000, "median_rate": 5000, "q3_rate": 7000, "unit": "kg", "confidence": "LOW"},
        {"material_id": "MAT-BAT-04", "region_id": "DELHI_NCR", "q1_rate": 2000, "median_rate": 3500, "q3_rate": 5000, "unit": "kg", "confidence": "LOW"},
        {"material_id": "MAT-CRT-01", "region_id": "DELHI_NCR", "q1_rate": 500, "median_rate": 1000, "q3_rate": 1500, "unit": "kg", "confidence": "HIGH"},
        {"material_id": "MAT-LCD-01", "region_id": "DELHI_NCR", "q1_rate": 1500, "median_rate": 2500, "q3_rate": 3500, "unit": "kg", "confidence": "MEDIUM"},
        {"material_id": "MAT-CAB-01", "region_id": "DELHI_NCR", "q1_rate": 38000, "median_rate": 45000, "q3_rate": 52000, "unit": "kg", "confidence": "HIGH"},
        {"material_id": "MAT-CAB-02", "region_id": "DELHI_NCR", "q1_rate": 11000, "median_rate": 14000, "q3_rate": 17000, "unit": "kg", "confidence": "MEDIUM"},
        {"material_id": "MAT-MOT-01", "region_id": "DELHI_NCR", "q1_rate": 18000, "median_rate": 22000, "q3_rate": 26000, "unit": "kg", "confidence": "HIGH"},
        {"material_id": "MAT-MOT-02", "region_id": "DELHI_NCR", "q1_rate": 14000, "median_rate": 17000, "q3_rate": 20000, "unit": "kg", "confidence": "MEDIUM"},
        {"material_id": "MAT-PLA-01", "region_id": "DELHI_NCR", "q1_rate": 2000, "median_rate": 2800, "q3_rate": 3500, "unit": "kg", "confidence": "HIGH"},
        {"material_id": "MAT-PLA-02", "region_id": "DELHI_NCR", "q1_rate": 1200, "median_rate": 1800, "q3_rate": 2400, "unit": "kg", "confidence": "MEDIUM"},
        {"material_id": "MAT-MET-01", "region_id": "DELHI_NCR", "q1_rate": 65000, "median_rate": 72000, "q3_rate": 78000, "unit": "kg", "confidence": "HIGH"},
        {"material_id": "MAT-MET-02", "region_id": "DELHI_NCR", "q1_rate": 14000, "median_rate": 17500, "q3_rate": 21000, "unit": "kg", "confidence": "HIGH"},
        {"material_id": "MAT-MET-03", "region_id": "DELHI_NCR", "q1_rate": 2800, "median_rate": 3300, "q3_rate": 3800, "unit": "kg", "confidence": "HIGH"},
        {"material_id": "MAT-MIX-01", "region_id": "DELHI_NCR", "q1_rate": 4000, "median_rate": 6500, "q3_rate": 9000, "unit": "kg", "confidence": "MEDIUM"},
        {"material_id": "MAT-MIX-02", "region_id": "DELHI_NCR", "q1_rate": 2500, "median_rate": 4000, "q3_rate": 5500, "unit": "kg", "confidence": "MEDIUM"},
        {"material_id": "MAT-OTH-01", "region_id": "DELHI_NCR", "q1_rate": 1000, "median_rate": 2000, "q3_rate": 3000, "unit": "kg", "confidence": "LOW"},
        {"material_id": "MAT-UNK-01", "region_id": "DELHI_NCR", "q1_rate": 500, "median_rate": 1000, "q3_rate": 1500, "unit": "kg", "confidence": "INSUFFICIENT_DATA"},
    ]

    # Facilities
    facilities = [
        {
            "facility_id": "fac-dl-01",
            "name": "Greentech Recyclers Pvt Ltd",
            "kind": "RECYCLER",
            "region_id": "DELHI_NCR",
            "district": "Mayapuri Industrial Area",
            "state": "Delhi",
            "address_public": "Phase II, Mayapuri Industrial Area, New Delhi, Delhi 110064",
            "verification_level": "L3",
            "authorized_routes": ["AUTHORIZED_EWASTE", "GENERAL_RECYCLING"],
            "materials_accepted": ["MAT-PCB-01", "MAT-PCB-02", "MAT-LCD-01", "MAT-CAB-01", "MAT-PLA-01"],
            "contact_public": "+91-11-28114400",
            "active": True
        },
        {
            "facility_id": "fac-dl-02",
            "name": "Apex Battery Isolators & Recyclers",
            "kind": "RECYCLER",
            "region_id": "DELHI_NCR",
            "district": "Okhla Industrial Area",
            "state": "Delhi",
            "address_public": "Phase III, Okhla Industrial Area, New Delhi, Delhi 110020",
            "verification_level": "L3",
            "authorized_routes": ["BATTERY_ISOLATION"],
            "materials_accepted": ["MAT-BAT-01", "MAT-BAT-02", "MAT-BAT-03", "MAT-BAT-04"],
            "contact_public": "+91-11-26915500",
            "active": True
        }
    ]

    bundle = {
        "metadata": {
            "snapshot_version": "REF-DEMO-2026-09-29",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=90)).isoformat(),
            "opaque_cursor": "c2FoaXRvbF9jdXJfdjE6MQ==",
            "region": "DELHI_NCR",
            "language": "hi",
            "role": "COLLECTOR",
            "is_demo": True,
            "disclaimer": "Labelled demonstration cache for initial offline activation. Disjoint from real commercial transactions."
        },
        "policy": {
            "policy_version": "POLICY_2026_V1",
            "max_weight_grams": 50000000,
            "max_active_drafts": 100,
            "price_freshness_days": 30,
            "sync_batch_limit": 50,
            "allowed_units": ["kg", "g", "piece"],
            "default_currency": "INR",
            "cash_settlement_enabled": True,
            "disclaimer": "Indicative prices are market estimates, not binding commitments or statutory EPR valuations."
        },
        "categories": categories,
        "materials": materials,
        "aliases": aliases,
        "safety_guides": safety_guides,
        "price_benchmarks": benchmark_prices,
        "facilities": facilities
    }

    raw_json = json.dumps(bundle, indent=2, ensure_ascii=False)

    # Save to curated
    curated_path = CURATED_DIR / "reference_bootstrap_demo.json"
    with open(curated_path, "w", encoding="utf-8") as f:
        f.write(raw_json)

    # Save to android assets
    android_path = ANDROID_ASSETS_DIR / "reference_bootstrap_demo.json"
    with open(android_path, "w", encoding="utf-8") as f:
        f.write(raw_json)

    sha = calculate_sha256_bytes(raw_json.encode("utf-8"))
    print(f"Generated bundled demo reference cache ({len(raw_json.encode('utf-8'))} bytes, SHA-256: {sha})")
    print(f"Saved to: {curated_path}")
    print(f"Saved to: {android_path}")


if __name__ == "__main__":
    main()
