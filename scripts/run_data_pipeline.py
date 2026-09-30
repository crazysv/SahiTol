#!/usr/bin/env python3
"""CLI utility for SahiTol data import staging, validation, deduplication, and synthetic generation.
Complies with T005, R-DATA-08, R-DATA-09, R-DATA-10.
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.data_tools import (
    DataValidator,
    Deduplicator,
    CachedGeocoder,
    SyntheticGenerator,
    generate_manifest,
    load_records,
)


def cmd_generate_synthetic(args: argparse.Namespace) -> int:
    """Generate reproducible seeded synthetic datasets and 15 edge scenarios."""
    out_dir = Path(args.output_dir)
    print(f"Generating reproducible synthetic datasets with seed={args.seed} into {out_dir}...")

    gen = SyntheticGenerator(seed=args.seed)
    families = gen.generate_all_families()
    validator = DataValidator()

    for fam_name, records in families.items():
        # Validate generated records
        val_res = validator.validate_family(fam_name, records)
        if val_res.quarantined_count > 0:
            print(f"ERROR: Synthetic generator produced quarantined rows in {fam_name}: {val_res.error_summary}")
            return 1
        
        fam_dir = out_dir / fam_name
        manifest = generate_manifest(
            family=fam_name,
            records=records,
            output_dir=fam_dir,
            data_version="v1.0-demo",
            quarantined_count=0,
            limitations="Purely synthetic demonstration fixtures; disjoint from real entities."
        )
        print(f"  [OK] {fam_name}: {manifest.total_records} records exported (Manifest: {fam_dir / 'manifest.json'})")

    # Generate edge scenarios fixture
    scenarios = gen.generate_edge_scenarios()
    scenarios_file = out_dir / "edge_scenarios.json"
    scenarios_data = [s.model_dump() for s in scenarios]
    with open(scenarios_file, "w", encoding="utf-8") as f:
        json.dump(scenarios_data, f, indent=2)
    print(f"  [OK] edge_scenarios: {len(scenarios)} fixtures exported to {scenarios_file}")

    print("Synthetic generation complete.")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate a dataset file and route invalid rows to quarantine."""
    input_file = Path(args.input_file)
    print(f"Validating {input_file} for family '{args.family}'...")

    records = load_records(input_file)
    validator = DataValidator()
    result = validator.validate_family(args.family, records)

    print(f"Validation summary: Total={result.total_count}, Valid={result.valid_count}, Quarantined={result.quarantined_count}")
    if result.error_summary:
        print("Error breakdown:")
        for code, count in result.error_summary.items():
            print(f"  - {code}: {count}")

    if result.quarantined_count > 0:
        quarantine_file = Path(args.quarantine_file or f"data/quarantine/{args.family}_quarantine.jsonl")
        result.write_quarantine_log(quarantine_file)
        print(f"Quarantined records written to: {quarantine_file}")

    return 0 if result.quarantined_count == 0 else 2


def cmd_dedup(args: argparse.Namespace) -> int:
    """Run duplicate detection on a dataset."""
    input_file = Path(args.input_file)
    print(f"Checking duplicates in {input_file} for family '{args.family}'...")

    records = load_records(input_file)
    deduper = Deduplicator()

    if args.family in ("recyclers", "facilities"):
        unique, report = deduper.deduplicate_facilities(records)
    elif args.family in ("prices", "price_observations"):
        unique, report = deduper.deduplicate_price_observations(records)
    elif args.family in ("ai_training", "images"):
        unique, report = deduper.deduplicate_by_sha256(records)
    else:
        print(f"Deduplication rule not configured for family: {args.family}")
        return 1

    print(f"Dedup summary: Total={report.total_records}, Unique={report.unique_records_count}, Clusters={report.duplicate_clusters_count}")
    if report.duplicate_clusters_count > 0:
        for c in report.clusters:
            print(f"  Cluster '{c.cluster_key}': canonical={c.canonical_id}, duplicates={c.duplicate_ids} (Rule: {c.match_rule}, Review: {c.requires_manual_review})")

    return 0


def cmd_geocode(args: argparse.Namespace) -> int:
    """Geocode an address with caching and regional boundary checks."""
    geocoder = CachedGeocoder(cache_file=args.cache_file)
    try:
        res = geocoder.geocode(
            address=args.address,
            entity_type=args.entity_type,
            region_id=args.region,
        )
        print(json.dumps(res.model_dump(), indent=2))
        return 0
    except PermissionError as e:
        print(f"SECURITY/PRIVACY VIOLATION: {e}", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="SahiTol Data Tools CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: generate-synthetic
    p_gen = subparsers.add_parser("generate-synthetic", help="Generate seeded synthetic fixtures and edge cases")
    p_gen.add_argument("--output-dir", default="data/synthetic", help="Output directory")
    p_gen.add_argument("--seed", type=int, default=42, help="RNG seed")
    p_gen.set_defaults(func=cmd_generate_synthetic)

    # Subcommand: validate
    p_val = subparsers.add_parser("validate", help="Validate dataset and quarantine rejected records")
    p_val.add_argument("--family", required=True, help="Dataset family name")
    p_val.add_argument("--input-file", required=True, help="Input CSV or JSON path")
    p_val.add_argument("--quarantine-file", help="Quarantine output path")
    p_val.set_defaults(func=cmd_validate)

    # Subcommand: dedup
    p_dup = subparsers.add_parser("dedup", help="Detect duplicates and generate review cluster report")
    p_dup.add_argument("--family", required=True, help="Dataset family name")
    p_dup.add_argument("--input-file", required=True, help="Input CSV or JSON path")
    p_dup.set_defaults(func=cmd_dedup)

    # Subcommand: geocode
    p_geo = subparsers.add_parser("geocode", help="Geocode address with caching and privacy boundaries")
    p_geo.add_argument("--address", required=True, help="Address to geocode")
    p_geo.add_argument("--entity-type", default="FACILITY", help="FACILITY or COLLECTOR")
    p_geo.add_argument("--region", default="DELHI_NCR", help="Target region ID")
    p_geo.add_argument("--cache-file", help="Optional cache file path")
    p_geo.set_defaults(func=cmd_geocode)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
