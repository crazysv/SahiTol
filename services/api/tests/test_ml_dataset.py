"""Unit tests for Curated Licensed Public Image Dataset (T032).
Covers requirements: R-ML-01, R-DATA-07.
Acceptance cases: AT-044, AT-059.
"""
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATASET_DIR = ROOT / "data/curated/ml_image_dataset"
CATALOG_PATH = ROOT / "data/curated/material_catalog/material_catalog.json"


@pytest.fixture(scope="module")
def dataset_artifacts():
    manifest_path = DATASET_DIR / "manifest.json"
    license_path = DATASET_DIR / "license_registry.json"
    splits_path = DATASET_DIR / "splits_summary.json"
    card_path = DATASET_DIR / "dataset_card.md"

    assert manifest_path.is_file(), "manifest.json must exist"
    assert license_path.is_file(), "license_registry.json must exist"
    assert splits_path.is_file(), "splits_summary.json must exist"
    assert card_path.is_file(), "dataset_card.md must exist"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    with open(license_path, "r", encoding="utf-8") as f:
        licenses = json.load(f)
    with open(splits_path, "r", encoding="utf-8") as f:
        splits = json.load(f)
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    return {
        "manifest": manifest,
        "licenses": licenses,
        "splits": splits,
        "catalog": catalog
    }


def test_license_metadata_and_permitted_uses(dataset_artifacts):
    """Test every license entry contains verified upstream rights and explicit attribution (R-ML-01, AT-044)."""
    licenses = dataset_artifacts["licenses"]
    assert len(licenses) >= 4, "Must cover at least Wikimedia, TrashNet, Open Images, Mendeley"

    for lic in licenses:
        assert lic["source_id"].startswith("SRC-IMG-")
        assert lic["license_name"]
        assert lic["license_url"].startswith("http")
        assert lic["upstream_url"].startswith("http")
        assert len(lic["permitted_uses"]) > 0
        assert "commercial" in lic["permitted_uses"] or "academic_research" in lic["permitted_uses"]
        assert lic["attribution_required"] is True
        assert lic["reviewed_date"]


def test_no_primary_field_image_claims(dataset_artifacts):
    """Test no images falsely claim primary field photography, respecting R-RES-02 desk-only decision (R-ML-01, AT-044)."""
    manifest = dataset_artifacts["manifest"]
    splits = dataset_artifacts["splits"]

    # Check manifest records
    for rec in manifest:
        assert rec["origin_class"] == "EXTERNAL_PUBLIC"
        assert rec["source_kind"] == "LICENSED_IMAGE_DATASET"
        assert rec["is_demo"] is False

    # Check documented limitations
    field_claim = splits["coverage_limitations"]["field_image_claims"]
    assert "UNMET" in field_claim or "NONE" in field_claim


def test_taxonomy_linkage_and_coverage(dataset_artifacts):
    """Test all image records link strictly to authoritative taxonomy materials (R-ML-01, AT-044)."""
    manifest = dataset_artifacts["manifest"]
    catalog_materials = {m["material_id"] for m in dataset_artifacts["catalog"]}

    for rec in manifest:
        assert rec["material_id"] in catalog_materials
        assert rec["category_code"]


def test_deterministic_grouped_split_leakage_free(dataset_artifacts):
    """Test group-aware splitting guarantees zero leakage across train, val, and test (R-DATA-07, AT-059)."""
    manifest = dataset_artifacts["manifest"]
    splits_summary = dataset_artifacts["splits"]

    group_split_map = {}
    for rec in manifest:
        group_id = rec["physical_object_group"]
        split = rec["split"]
        assert split in ("TRAIN", "VAL", "TEST")

        if group_id in group_split_map:
            assert group_split_map[group_id] == split, (
                f"Leakage detected: group {group_id} present in multiple splits!"
            )
        else:
            group_split_map[group_id] = split

    assert splits_summary["leakage_audit"]["groups_overlapping_splits"] == 0
    assert splits_summary["leakage_audit"]["leakage_free"] is True


def test_nullable_tabular_links_remain_null(dataset_artifacts):
    """Test absent measurements remain strictly null and are not fabricated (R-DATA-07, AT-059)."""
    manifest = dataset_artifacts["manifest"]

    for rec in manifest:
        assert rec["observed_weight_g"] is None, "Weight must not be fabricated from stock photos"
        assert rec["observed_price_paise"] is None, "Price must not be fabricated from stock photos"
        assert rec["observed_location_id"] is None, "GPS coordinates must not be fabricated"


def test_disclosed_class_gaps_and_manual_fallback(dataset_artifacts):
    """Test dataset card and splits summary explicitly disclose excluded classes and fallback (R-ML-01, AT-044)."""
    splits = dataset_artifacts["splits"]
    limitations = splits["coverage_limitations"]

    assert len(limitations["classes_excluded_from_classifier"]) >= 5
    assert "safe_fallback_path" in limitations
    assert "Manual" in limitations["safe_fallback_path"]
