"""Canonical JSON serialization (SAHITOL-JCS-1) and SHA-256 integrity hashing."""
import hashlib
import json
from typing import Any, Dict


def serialize_canonical_json(payload: Dict[str, Any]) -> str:
    """Serialize dictionary to canonical UTF-8 JSON representation."""
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def compute_canonical_hash(payload: Dict[str, Any]) -> str:
    """Compute SHA-256 hash of the canonical JSON representation."""
    canonical_str = serialize_canonical_json(payload)
    return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
