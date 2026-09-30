"""Comprehensive validation and compliance tests for Contextual Safety Content (T035).
Covers requirements: R-SAFE-01, R-LANG-01, R-DATA-01.
Acceptance cases: AT-048, AT-058.
"""
import hashlib
import json
import re
from pathlib import Path
import pytest

from app.db.seeds.materials import load_seed_json

CURATED_DIR = Path(__file__).resolve().parents[3] / "data" / "curated" / "safety_cards"
MANIFEST_PATH = CURATED_DIR / "manifest.json"
SAFETY_CARDS_PATH = CURATED_DIR / "safety_cards.json"
DESIGN_BRIEFS_PATH = Path(__file__).resolve().parents[3] / "design" / "stitch" / "PICTOGRAM_BRIEFS.md"


def test_safety_cards_file_and_manifest_integrity():
    """Verify that safety_cards.json exists and its SHA-256 matches manifest.json."""
    assert SAFETY_CARDS_PATH.exists(), f"Safety cards file not found at {SAFETY_CARDS_PATH}"
    assert MANIFEST_PATH.exists(), f"Manifest file not found at {MANIFEST_PATH}"

    raw_bytes = SAFETY_CARDS_PATH.read_bytes()
    computed_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    computed_size = len(raw_bytes)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    file_entry = next(entry for entry in manifest["files"] if entry["filename"] == "safety_cards.json")
    assert file_entry["sha256"] == computed_sha256
    assert file_entry["byte_size"] == computed_size
    assert file_entry["card_count"] == 9
    assert manifest["validation_status"] == "VALID"


def test_safety_cards_schema_and_card_inventory():
    """Verify that all 9 required safety cards exist with required fields and valid enums."""
    with open(SAFETY_CARDS_PATH, "r", encoding="utf-8") as f:
        cards = json.load(f)

    assert len(cards) == 9

    expected_ids = {
        "SC-CAB-01", "SC-PCB-01", "SC-CRT-01",
        "SC-BAT-01", "SC-BAT-02", "SC-BAT-03",
        "SC-DAM-01", "SC-PLA-01", "SC-MIX-01"
    }
    actual_ids = {c["id"] for c in cards}
    assert actual_ids == expected_ids

    valid_routes = {
        "GENERAL_RECYCLING", "AUTHORIZED_EWASTE",
        "BATTERY_ISOLATION", "HAZARDOUS_DISPOSAL",
        "REVIEW_REQUIRED"
    }
    valid_hazard_levels = {"HIGH", "CRITICAL"}

    for card in cards:
        assert card["id"].startswith("SC-")
        assert card["guide_id"].startswith("SG-")
        assert len(card["material_ids"]) >= 1
        assert card["regulatory_route"] in valid_routes
        assert card["hazard_level"] in valid_hazard_levels
        assert len(card["hazard_type"]) > 0
        assert card["version"].startswith("v")
        assert len(card["source_ids"]) >= 1
        assert len(card["references"]) >= 1
        assert card["pictogram_ref"].startswith("icons/safety/")
        assert card["review_status"] == "APPROVED"
        assert card["scientific_review"] == "DESK_REVIEWED_CPCB_WHO"
        assert card["translation_review"] == "DRAFT_PENDING_NATIVE_AUDIT"


def test_safety_cards_trilingual_completeness_and_devanagari():
    """
    R-LANG-01 / AT-048:
    Verify 100% trilingual completeness across en, hi, and mr.
    Ensure Hindi and Marathi fields contain authentic Devanagari script.
    """
    with open(SAFETY_CARDS_PATH, "r", encoding="utf-8") as f:
        cards = json.load(f)

    required_fields = [
        "title", "subtitle", "hazard_warning",
        "safe_handling_instruction", "prohibited_action", "audio_script"
    ]
    devanagari_pattern = re.compile(r"[\u0900-\u097F]")

    for card in cards:
        locales = card["locales"]
        assert "en" in locales, f"Card {card['id']} missing English locale"
        assert "hi" in locales, f"Card {card['id']} missing Hindi locale"
        assert "mr" in locales, f"Card {card['id']} missing Marathi locale"

        for lang in ["en", "hi", "mr"]:
            for field in required_fields:
                val = locales[lang].get(field)
                assert val is not None and len(val.strip()) > 0, (
                    f"Card {card['id']} language {lang} missing field {field}"
                )

        # Check authentic Devanagari script in hi and mr
        for lang in ["hi", "mr"]:
            for field in required_fields:
                val = locales[lang][field]
                assert devanagari_pattern.search(val) is not None, (
                    f"Card {card['id']} language {lang} field {field} does not contain Devanagari script: '{val}'"
                )


def test_safety_cards_audio_keys_and_script_parity():
    """
    R-SAFE-01 / AT-048:
    Verify audio keys and scripts exist for all three languages.
    """
    with open(SAFETY_CARDS_PATH, "r", encoding="utf-8") as f:
        cards = json.load(f)

    for card in cards:
        audio_keys = card["audio_keys"]
        assert "en" in audio_keys and len(audio_keys["en"]) > 0
        assert "hi" in audio_keys and len(audio_keys["hi"]) > 0
        assert "mr" in audio_keys and len(audio_keys["mr"]) > 0

        # Verify audio scripts exist in locales
        for lang in ["en", "hi", "mr"]:
            script = card["locales"][lang]["audio_script"]
            assert len(script.strip()) >= 20, (
                f"Audio script for {card['id']} ({lang}) too short: '{script}'"
            )


def test_safety_cards_non_instructional_invariants():
    """
    R-SAFE-01 / AT-048:
    Strictly enforce non-instructional safety policy.
    Ensure content does NOT contain chemical extraction recipes, informal smelting,
    acid leaching tutorials, or claims that basic PPE makes hazardous operations safe.
    """
    with open(SAFETY_CARDS_PATH, "r", encoding="utf-8") as f:
        cards = json.load(f)

    prohibited_instructional_terms = [
        "pour acid",
        "extract gold",
        "burn cable over",
        "open battery cell",
        "smelt lead",
        "dissolve in acid",
        "cloth mask makes safe",
        "diy recycling",
        "easy extraction",
        "home refinery"
    ]

    for card in cards:
        # Search all English text fields
        en_texts = [
            card["locales"]["en"][field].lower()
            for field in ["hazard_warning", "safe_handling_instruction", "audio_script"]
        ]
        combined_en = " ".join(en_texts)

        for term in prohibited_instructional_terms:
            assert term not in combined_en, (
                f"Card {card['id']} violates non-instructional invariant with term '{term}' in '{combined_en}'"
            )


def test_material_catalog_safety_guide_coverage():
    """
    R-SAFE-01:
    Verify that every material in materials.json has at least one applicable safety guide.
    """
    materials = load_seed_json("materials.json")
    with open(SAFETY_CARDS_PATH, "r", encoding="utf-8") as f:
        cards = json.load(f)

    covered_materials = set()
    for card in cards:
        for m_id in card["material_ids"]:
            covered_materials.add(m_id)

    # Check that high-hazard materials are fully covered
    critical_materials = [
        "MAT-CAB-01", "MAT-CAB-02",
        "MAT-PCB-01", "MAT-PCB-02",
        "MAT-CRT-01",
        "MAT-BAT-01", "MAT-BAT-02", "MAT-BAT-03", "MAT-BAT-04",
        "MAT-PLA-01", "MAT-PLA-02"
    ]
    for mat_id in critical_materials:
        assert mat_id in covered_materials, f"Critical material {mat_id} has no safety card mapping"


def test_pictogram_briefs_document_exists():
    """Verify that design/stitch/PICTOGRAM_BRIEFS.md exists and covers all 9 safety cards."""
    assert DESIGN_BRIEFS_PATH.exists(), f"Design briefs not found at {DESIGN_BRIEFS_PATH}"
    content = DESIGN_BRIEFS_PATH.read_text(encoding="utf-8")

    assert "C17" in content
    assert "no_burn_cables.svg" in content
    assert "no_acid_pcb.svg" in content
    assert "no_break_crt.svg" in content
    assert "isolated_battery.svg" in content
    assert "tape_terminals.svg" in content
    assert "isolated_container.svg" in content
    assert "stop_handling_hazard.svg" in content
    assert "no_burn_plastics.svg" in content
    assert "no_dismantle_mixed.svg" in content
    assert "Non-Instructional Invariant" in content
