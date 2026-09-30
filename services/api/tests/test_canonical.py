"""Tests for canonical serialization and SHA-256 against docs/planning/handover_fixture.json."""
import json
from pathlib import Path
from app.domain.canonical import serialize_canonical_json, compute_canonical_hash

ROOT = Path(__file__).resolve().parents[3]
FIXTURE_PATH = ROOT / "docs" / "planning" / "handover_fixture.json"


def test_handover_fixture_canonicalization_and_hash():
    assert FIXTURE_PATH.is_file(), f"Missing fixture at {FIXTURE_PATH}"
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    payload = fixture["proposal_payload"]
    expected_canonical_utf8 = fixture["canonical_utf8"]
    expected_proposal_hash = fixture["proposal_hash"]

    # Test canonical serialization
    serialized = serialize_canonical_json(payload)
    assert serialized == expected_canonical_utf8

    # Test SHA-256 calculation
    computed_hash = compute_canonical_hash(payload)
    assert computed_hash == expected_proposal_hash
