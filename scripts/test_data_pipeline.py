"""Unit test suite for SahiTol data import, validation, deduplication, geocoding, and synthetic tooling.
Verifies T005, R-DATA-08, R-DATA-09, R-DATA-10 under docs/18_DATA_PROVENANCE.md.
"""

from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from scripts.data_tools import (
    OriginClass,
    SourceKind,
    ReviewStatus,
    LocationQuality,
    sanitize_csv_cell,
    normalize_text,
    normalize_phone,
    convert_to_paise,
    convert_to_grams,
    DataValidator,
    Deduplicator,
    CachedGeocoder,
    SyntheticGenerator,
    generate_manifest,
)


def test_sanitize_csv_cell():
    """Formula injection triggers are neutralized with leading quote."""
    assert sanitize_csv_cell("=cmd|' /C calc'!A0") == "'=cmd|' /C calc'!A0"
    assert sanitize_csv_cell("@SUM(1,2)") == "'@SUM(1,2)"
    assert sanitize_csv_cell("+12345") == "'+12345"
    assert sanitize_csv_cell("-12345") == "'-12345"
    assert sanitize_csv_cell("\tTABBED") == "'\tTABBED"
    # Safe values unaffected
    assert sanitize_csv_cell("Motherboard PCB") == "Motherboard PCB"
    assert sanitize_csv_cell(12345) == 12345
    assert sanitize_csv_cell(None) is None


def test_normalization_and_conversions():
    """Text, phone, paise, and grams normalization."""
    # Text normalization
    assert normalize_text("  E-Waste   Recycler  \n") == "E-Waste Recycler"
    assert normalize_text(None) is None

    # Phone normalization
    assert normalize_phone("9876543210") == "+919876543210"
    assert normalize_phone("+91 98765-43210") == "+919876543210"
    assert normalize_phone("09876543210") == "+919876543210"
    assert normalize_phone("1234") is None  # Invalid

    # Paise conversions
    assert convert_to_paise(15.50) == 1550
    assert convert_to_paise("320.00") == 32000
    assert convert_to_paise(500) == 500
    with pytest.raises(ValueError):
        convert_to_paise(None)
    with pytest.raises(ValueError):
        convert_to_paise("abc")

    # Grams conversions (strictly positive)
    assert convert_to_grams(1.5, "kg") == 1500
    assert convert_to_grams("250", "g") == 250
    assert convert_to_grams(2.0, "quintal") == 200000
    assert convert_to_grams(1.0, "ton") == 1000000
    with pytest.raises(ValueError):
        convert_to_grams(0, "kg")  # Zero disallowed
    with pytest.raises(ValueError):
        convert_to_grams(-5.0, "kg")  # Negative disallowed


def test_validator_and_quarantine_isolation():
    """Validator quarantines policy violations and malformed data."""
    validator = DataValidator()

    # Rule 1: Official data cannot have source_kind=SYNTHETIC_GENERATOR
    bad_official = [
        {
            "material_id": "MAT-01",
            "category_code": "PCB",
            "subcategory_code": "LOW",
            "label_en": "Test PCB",
            "default_route": "AUTHORIZED_EWASTE",
            "origin_class": OriginClass.OFFICIAL.value,
            "source_kind": SourceKind.SYNTHETIC_GENERATOR.value,
            "is_demo": False,
        }
    ]
    res1 = validator.validate_material_catalog(bad_official)
    assert res1.valid_count == 0
    assert res1.quarantined_count == 1
    assert res1.quarantined_records[0].error_code == "SYNTHETIC_OFFICIAL_CONFLICT"

    # Rule 2: Synthetic data must have is_demo=True
    bad_synthetic = [
        {
            "material_id": "MAT-02",
            "category_code": "PCB",
            "subcategory_code": "LOW",
            "label_en": "Test PCB",
            "default_route": "AUTHORIZED_EWASTE",
            "origin_class": OriginClass.SYNTHETIC.value,
            "source_kind": SourceKind.SYNTHETIC_GENERATOR.value,
            "is_demo": False,
        }
    ]
    res2 = validator.validate_material_catalog(bad_synthetic)
    assert res2.valid_count == 0
    assert res2.quarantined_count == 1
    assert res2.quarantined_records[0].error_code == "SYNTHETIC_DEMO_MISMATCH"

    # Rule 3: Missing date in price observations is quarantined
    undated_price = [
        {
            "id": "P-01",
            "material_id": "MAT-01",
            "rate_paise_per_unit": 35000,
            "unit": "kg",
            "price_kind": "BUY",
            "observed_at": None,
            "source_id": "SRC-01",
            "origin_class": OriginClass.EXTERNAL_PUBLIC.value,
            "source_kind": SourceKind.PUBLIC_MARKET_QUOTE.value,
            "is_demo": False,
        }
    ]
    res3 = validator.validate_price_observations(undated_price)
    assert res3.valid_count == 0
    assert res3.quarantined_count == 1
    assert res3.quarantined_records[0].error_code == "MISSING_REQUIRED_FIELDS"

    # Rule 4: Out of bounds coordinates in facility directory
    oob_facility = [
        {
            "facility_id": "FAC-01",
            "name": "Invalid Coords Recycler",
            "facility_type": "RECYCLER",
            "region_id": "DELHI_NCR",
            "route": "AUTHORIZED_EWASTE",
            "registration_status": "VALID",
            "latitude": 55.7558,  # Moscow coords, not India
            "longitude": 37.6173,
            "origin_class": OriginClass.OFFICIAL.value,
            "source_kind": SourceKind.REGULATOR_LIST.value,
            "is_demo": False,
        }
    ]
    res4 = validator.validate_recyclers(oob_facility)
    assert res4.valid_count == 0
    assert res4.quarantined_count == 1
    assert res4.quarantined_records[0].error_code == "OUT_OF_BOUNDS_COORDINATES"


def test_deduplicator():
    """Deduplicator detects duplicate facility registration references and exact price observations."""
    deduper = Deduplicator()

    # Facility duplicate detection
    facs = [
        {
            "facility_id": "F-01",
            "name": "Alpha Recyclers",
            "facility_type": "RECYCLER",
            "public_address": "Plot 1, Mayapuri",
            "registration_reference": "REG-12345",
        },
        {
            "facility_id": "F-02",
            "name": "Alpha Recyclers Branch",
            "facility_type": "RECYCLER",
            "public_address": "Plot 1, Mayapuri Phase 1",
            "registration_reference": "REG-12345",  # Duplicate reg ref
        },
        {
            "facility_id": "F-03",
            "name": "Beta Dismantler",
            "facility_type": "DISMANTLER",
            "public_address": "Plot 2, Okhla",
            "registration_reference": "REG-67890",
        },
    ]
    unique_facs, report = deduper.deduplicate_facilities(facs)
    assert report.total_records == 3
    assert report.unique_records_count == 2
    assert report.duplicate_clusters_count == 1
    assert report.clusters[0].match_rule == "REGISTRATION_REFERENCE_EXACT"
    assert report.clusters[0].canonical_id == "F-01"


def test_cached_geocoder_and_privacy():
    """Cached geocoder respects collector privacy and caches lookups."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_path = Path(tmpdir) / "test_cache.json"
        geocoder = CachedGeocoder(cache_file=cache_path)

        # PRIVACY TEST: Collector address must raise PermissionError
        with pytest.raises(PermissionError) as exc_info:
            geocoder.geocode("Collector home address, slums near Mayapuri", entity_type="COLLECTOR")
        assert "Privacy violation" in str(exc_info.value)

        # Facility geocode with custom mock provider
        def mock_provider(query: str):
            if "mayapuri" in query:
                return (28.6321, 77.1215, LocationQuality.GEOCODED_ROOFTOP.value)
            return None

        res1 = geocoder.geocode("Plot 42, Mayapuri, New Delhi", entity_type="FACILITY", region_id="DELHI_NCR", provider_fn=mock_provider)
        assert res1.latitude == 28.6321
        assert res1.longitude == 77.1215
        assert res1.in_bounds is True
        assert res1.location_quality == LocationQuality.GEOCODED_ROOFTOP
        assert res1.served_from_cache is False

        # Second lookup should hit local cache
        res2 = geocoder.geocode("Plot 42, Mayapuri, New Delhi", entity_type="FACILITY", region_id="DELHI_NCR")
        assert res2.latitude == 28.6321
        assert res2.served_from_cache is True

        # Unresolved address returns null coordinates (never invented)
        res_unknown = geocoder.geocode("Nonexistent Mars Crater 404", entity_type="FACILITY")
        assert res_unknown.latitude is None
        assert res_unknown.longitude is None
        assert res_unknown.location_quality == LocationQuality.UNKNOWN


def test_synthetic_generator_and_manifest():
    """Seeded generator produces valid records, 15 edge scenarios, and manifest."""
    gen = SyntheticGenerator(seed=42)
    families = gen.generate_all_families()

    # All 7 families present
    assert len(families) == 7
    for fam_name, records in families.items():
        assert len(records) > 0
        for r in records:
            # Provenance isolation invariant
            assert r["origin_class"] == OriginClass.SYNTHETIC.value
            assert r["source_kind"] == SourceKind.SYNTHETIC_GENERATOR.value
            assert r["is_demo"] is True

    # 15 Edge scenarios generated
    scenarios = gen.generate_edge_scenarios()
    assert len(scenarios) == 15
    scenario_ids = [s.scenario_id for s in scenarios]
    assert "EDGE-01-HAPPY-PATH" in scenario_ids
    assert "EDGE-02-NO-PRICE-COHORT" in scenario_ids
    assert "EDGE-03-STALE-EXPIRED-ROUTE" in scenario_ids
    assert "EDGE-04-UNKNOWN-BATTERY-CHEMISTRY" in scenario_ids
    assert "EDGE-05-LOW-CONFIDENCE-IMAGE" in scenario_ids
    assert "EDGE-11-DUPLICATE-OPERATION" in scenario_ids
    assert "EDGE-12-CONFLICTING-EDIT" in scenario_ids
    assert "EDGE-14-DENIED-GPS" in scenario_ids

    # Manifest export test
    with tempfile.TemporaryDirectory() as tmpdir:
        manifest = generate_manifest(
            family="material_catalog",
            records=families["material_catalog"],
            output_dir=tmpdir,
            data_version="v1.0-test",
        )
        assert manifest.total_records == len(families["material_catalog"])
        assert manifest.counts_by_origin_class["SYNTHETIC"] == len(families["material_catalog"])
        assert manifest.counts_by_is_demo["true"] == len(families["material_catalog"])
        assert len(manifest.files) == 2  # CSV and JSON
        assert (Path(tmpdir) / "manifest.json").exists()
