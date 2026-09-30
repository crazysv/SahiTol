"""Export curated price observations and statistical summaries to data/curated."""
import csv
import json
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "services" / "api"))

from app.domain.pricing import PriceObservation as DomainObservation, calculate_weighted_quantiles

SEEDS_DIR = ROOT_DIR / "data" / "seeds"
OUTPUT_DIR = ROOT_DIR / "data" / "curated" / "price_observations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def calculate_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def main():
    seed_file = SEEDS_DIR / "price_observations.json"
    with open(seed_file, "r", encoding="utf-8") as f:
        observations = json.load(f)

    # 1. Export price_observations.json
    obs_json_path = OUTPUT_DIR / "price_observations.json"
    with open(obs_json_path, "w", encoding="utf-8") as f:
        json.dump(observations, f, indent=2, ensure_ascii=False)

    # 2. Export price_observations.csv
    obs_csv_path = OUTPUT_DIR / "price_observations.csv"
    headers = [
        "id", "material_id", "subcategory_id", "region_id", "condition",
        "rate_paise_per_unit", "unit", "price_kind", "observed_at",
        "source_id", "review_status", "origin_class", "source_kind", "is_demo"
    ]
    with open(obs_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(observations)

    # 3. Compute statistical summaries under PRICE_V1 policy
    cohorts: Dict[tuple, List[Dict[str, Any]]] = {}
    for obs in observations:
        if obs.get("review_status") == "VERIFIED" and not obs.get("is_demo", False):
            key = (obs["material_id"], obs["region_id"])
            cohorts.setdefault(key, []).append(obs)

    now_iso = datetime.now(timezone.utc).isoformat()
    summaries = []
    for (mat_id, reg_id), obs_list in cohorts.items():
        domain_obs = [
            DomainObservation(
                rate_paise_per_unit=o["rate_paise_per_unit"],
                weight=1.0,
                observation_id=o["id"]
            )
            for o in obs_list
        ]
        quantiles = calculate_weighted_quantiles(domain_obs)
        sources = set(o["source_id"] for o in obs_list)
        source_count = len(sources)

        reason_codes = []
        if len(obs_list) >= 5 and source_count >= 2:
            confidence = "HIGH"
        elif len(obs_list) >= 3:
            confidence = "MEDIUM"
            if source_count < 2:
                reason_codes.append("FEW_INDEPENDENT_SOURCES")
        else:
            confidence = "LOW"
            reason_codes.append("SMALL_SAMPLE_SIZE")

        q1, med, q3 = quantiles if quantiles else (None, None, None)

        summaries.append({
            "cohort_key": f"{mat_id}:{reg_id}",
            "material_id": mat_id,
            "region_id": reg_id,
            "policy_version": "PRICE_V1",
            "q1_rate": q1,
            "median_rate": med,
            "q3_rate": q3,
            "count": len(obs_list),
            "independent_sources": source_count,
            "confidence": confidence,
            "reason_codes": reason_codes,
            "source_ids": sorted(list(sources)),
            "as_of": now_iso,
            "is_demo": False
        })

    summaries_json_path = OUTPUT_DIR / "price_summaries.json"
    with open(summaries_json_path, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)

    # 4. Manifest
    files_manifest = []
    for p in [obs_csv_path, obs_json_path, summaries_json_path]:
        files_manifest.append({
            "filename": p.name,
            "sha256": calculate_sha256(p),
            "byte_size": p.stat().st_size,
            "row_count": len(observations) if "observations" in p.name else len(summaries)
        })

    manifest = {
        "dataset_family": "price_observations",
        "schema_version": "v1.0",
        "data_version": "v1.0-curated",
        "generated_at": now_iso,
        "total_records": len(observations),
        "files": files_manifest,
        "counts_by_origin_class": {
            "EXTERNAL_PUBLIC": sum(1 for o in observations if o.get("origin_class") == "EXTERNAL_PUBLIC"),
            "OFFICIAL": sum(1 for o in observations if o.get("origin_class") == "OFFICIAL"),
            "SYNTHETIC": sum(1 for o in observations if o.get("origin_class") == "SYNTHETIC")
        },
        "counts_by_source_kind": {
            "PUBLIC_MARKET_QUOTE": sum(1 for o in observations if o.get("source_kind") == "PUBLIC_MARKET_QUOTE"),
            "GOVERNMENT_PUBLICATION": sum(1 for o in observations if o.get("source_kind") == "GOVERNMENT_PUBLICATION"),
            "SYNTHETIC_GENERATOR": sum(1 for o in observations if o.get("source_kind") == "SYNTHETIC_GENERATOR")
        },
        "counts_by_is_demo": {
            "false": sum(1 for o in observations if not o.get("is_demo", False)),
            "true": sum(1 for o in observations if o.get("is_demo", False))
        },
        "counts_by_review_status": {
            "VERIFIED": sum(1 for o in observations if o.get("review_status") == "VERIFIED"),
            "PENDING_REVIEW": sum(1 for o in observations if o.get("review_status") == "PENDING_REVIEW"),
            "REJECTED": sum(1 for o in observations if o.get("review_status") == "REJECTED")
        },
        "quarantined_count": 0,
        "source_ids": ["SRC-01", "SRC-04", "SRC-05"],
        "validation_status": "VALID",
        "limitations": "Secondary market quotes and trade surveys across Delhi-NCR and Maharashtra hubs (Mayapuri, Seelampur, MIDC benchmarks). No live collector fieldwork transaction data included; primary fieldwork obligation R-RES-02 remains UNMET."
    }

    manifest_path = OUTPUT_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Exported {len(observations)} price observations and {len(summaries)} summaries to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
