"""Schema and constraint validation engine with automatic quarantine logging.
Complies with docs/18_DATA_PROVENANCE.md, docs/06_SCHEMA.md, and R-DATA-08/R-DATA-09.
"""

from __future__ import annotations
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from .provenance import OriginClass, SourceKind, ReviewStatus, LocationQuality


VALID_ROUTES = {
    "GENERAL_RECYCLING",
    "AUTHORIZED_EWASTE",
    "BATTERY_ISOLATION",
    "HAZARDOUS_DISPOSAL",
    "RESTRICTED_RECYCLER",
}

VALID_PRICE_KINDS = {"BUY", "QUOTE", "SELL"}
VALID_SPLITS = {"train", "val", "test"}
VALID_LANGUAGES = {"en", "hi", "mr"}

SHA256_HEX_REGEX = re.compile(r"^[0-9a-fA-F]{64}$")


class QuarantineRecord(BaseModel):
    """Container for a malformed or policy-violating record removed from active data."""
    family: str
    record_id: Optional[str] = None
    error_code: str
    error_message: str
    raw_record: Dict[str, Any]
    quarantined_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ValidationResult(BaseModel):
    """Outcome of validating a dataset batch."""
    family: str
    total_count: int
    valid_count: int
    quarantined_count: int
    valid_records: List[Dict[str, Any]]
    quarantined_records: List[QuarantineRecord]
    error_summary: Dict[str, int] = Field(default_factory=dict)

    def write_quarantine_log(self, output_path: Path | str) -> None:
        """Write quarantined records to an inspectable JSON-Lines file."""
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            for q in self.quarantined_records:
                f.write(q.model_dump_json() + "\n")


class DataValidator:
    """Validates records for the seven SahiTol dataset families."""

    @staticmethod
    def _validate_common_provenance(record: Dict[str, Any]) -> Optional[Tuple[str, str]]:
        """Validate core provenance fields and demo isolation constraints."""
        origin = record.get("origin_class")
        source_kind = record.get("source_kind")
        is_demo_raw = record.get("is_demo")

        if not origin:
            return ("MISSING_ORIGIN_CLASS", "Missing required field: origin_class")
        if not source_kind:
            return ("MISSING_SOURCE_KIND", "Missing required field: source_kind")

        try:
            origin_enum = OriginClass(origin)
        except ValueError:
            return ("INVALID_ORIGIN_CLASS", f"Invalid origin_class: {origin}")

        try:
            source_kind_enum = SourceKind(source_kind)
        except ValueError:
            return ("INVALID_SOURCE_KIND", f"Invalid source_kind: {source_kind}")

        # Check boolean is_demo
        is_demo = is_demo_raw is True or str(is_demo_raw).lower() in ("true", "1")

        # Isolation Rule: Official data can NEVER come from a synthetic generator
        if origin_enum == OriginClass.OFFICIAL and source_kind_enum == SourceKind.SYNTHETIC_GENERATOR:
            return (
                "SYNTHETIC_OFFICIAL_CONFLICT",
                "Records with origin_class=OFFICIAL cannot have source_kind=SYNTHETIC_GENERATOR",
            )

        # Isolation Rule: Synthetic data MUST have is_demo = True
        if origin_enum == OriginClass.SYNTHETIC and not is_demo:
            return (
                "SYNTHETIC_DEMO_MISMATCH",
                "Records with origin_class=SYNTHETIC must have is_demo=true",
            )

        return None

    def validate_material_catalog(self, records: List[Dict[str, Any]]) -> ValidationResult:
        """Validate material catalog reference records."""
        valid, quarantined, errors = [], [], {}

        for idx, r in enumerate(records):
            rec_id = r.get("material_id") or f"row_{idx}"
            prov_err = self._validate_common_provenance(r)
            if prov_err:
                code, msg = prov_err
                quarantined.append(QuarantineRecord(family="material_catalog", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            # Required structural fields
            required = ["material_id", "category_code", "subcategory_code", "label_en", "default_route"]
            missing = [f for f in required if not r.get(f)]
            if missing:
                code = "MISSING_REQUIRED_FIELDS"
                msg = f"Missing required fields: {', '.join(missing)}"
                quarantined.append(QuarantineRecord(family="material_catalog", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            # Validate route
            route = r.get("default_route")
            if route not in VALID_ROUTES:
                code = "INVALID_REGULATORY_ROUTE"
                msg = f"Unknown route: {route}. Must be one of: {VALID_ROUTES}"
                quarantined.append(QuarantineRecord(family="material_catalog", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            valid.append(r)

        return ValidationResult(
            family="material_catalog",
            total_count=len(records),
            valid_count=len(valid),
            quarantined_count=len(quarantined),
            valid_records=valid,
            quarantined_records=quarantined,
            error_summary=errors,
        )

    def validate_price_observations(self, records: List[Dict[str, Any]]) -> ValidationResult:
        """Validate dated price observations."""
        valid, quarantined, errors = [], [], {}

        for idx, r in enumerate(records):
            rec_id = r.get("id") or f"row_{idx}"
            prov_err = self._validate_common_provenance(r)
            if prov_err:
                code, msg = prov_err
                quarantined.append(QuarantineRecord(family="price_observations", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            required = ["id", "material_id", "rate_paise_per_unit", "unit", "price_kind", "observed_at", "source_id"]
            missing = [f for f in required if not r.get(f)]
            if missing:
                code = "MISSING_REQUIRED_FIELDS"
                msg = f"Missing required fields: {', '.join(missing)}"
                quarantined.append(QuarantineRecord(family="price_observations", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            # Rate must be positive integer paise
            try:
                rate = int(r["rate_paise_per_unit"])
                if rate <= 0:
                    raise ValueError("Rate must be strictly positive (> 0)")
            except (ValueError, TypeError):
                code = "NON_POSITIVE_RATE"
                msg = f"Invalid rate_paise_per_unit: {r.get('rate_paise_per_unit')}"
                quarantined.append(QuarantineRecord(family="price_observations", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            # Price kind check
            pkind = r.get("price_kind")
            if pkind not in VALID_PRICE_KINDS:
                code = "INVALID_PRICE_KIND"
                msg = f"Invalid price_kind: {pkind}. Must be BUY, QUOTE, or SELL."
                quarantined.append(QuarantineRecord(family="price_observations", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            # Observation date check: Missing observation date disqualifies current price
            obs_at = r.get("observed_at")
            if not obs_at or obs_at == "null":
                code = "MISSING_OBSERVATION_DATE"
                msg = "Missing observed_at timestamp; undated price cannot enter active cohort."
                quarantined.append(QuarantineRecord(family="price_observations", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            valid.append(r)

        return ValidationResult(
            family="price_observations",
            total_count=len(records),
            valid_count=len(valid),
            quarantined_count=len(quarantined),
            valid_records=valid,
            quarantined_records=quarantined,
            error_summary=errors,
        )

    def validate_recyclers(self, records: List[Dict[str, Any]]) -> ValidationResult:
        """Validate recycler and facility directory entries."""
        valid, quarantined, errors = [], [], {}

        for idx, r in enumerate(records):
            rec_id = r.get("facility_id") or f"row_{idx}"
            prov_err = self._validate_common_provenance(r)
            if prov_err:
                code, msg = prov_err
                quarantined.append(QuarantineRecord(family="recyclers", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            required = ["facility_id", "name", "facility_type", "region_id", "route", "registration_status"]
            missing = [f for f in required if not r.get(f)]
            if missing:
                code = "MISSING_REQUIRED_FIELDS"
                msg = f"Missing required fields: {', '.join(missing)}"
                quarantined.append(QuarantineRecord(family="recyclers", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            # Geolocation bounds check (India territory: lat 8.0-37.0, lon 68.0-97.0)
            lat_raw = r.get("latitude")
            lon_raw = r.get("longitude")
            if lat_raw and lon_raw and lat_raw != "" and lon_raw != "":
                try:
                    lat, lon = float(lat_raw), float(lon_raw)
                    if not (8.0 <= lat <= 37.0 and 68.0 <= lon <= 97.0):
                        code = "OUT_OF_BOUNDS_COORDINATES"
                        msg = f"Coordinates ({lat}, {lon}) outside valid India bounds"
                        quarantined.append(QuarantineRecord(family="recyclers", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                        errors[code] = errors.get(code, 0) + 1
                        continue
                except (ValueError, TypeError):
                    code = "MALFORMED_COORDINATES"
                    msg = f"Could not parse lat/lon: {lat_raw}, {lon_raw}"
                    quarantined.append(QuarantineRecord(family="recyclers", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                    errors[code] = errors.get(code, 0) + 1
                    continue

            valid.append(r)

        return ValidationResult(
            family="recyclers",
            total_count=len(records),
            valid_count=len(valid),
            quarantined_count=len(quarantined),
            valid_records=valid,
            quarantined_records=quarantined,
            error_summary=errors,
        )

    def validate_transactions(self, records: List[Dict[str, Any]]) -> ValidationResult:
        """Validate transaction records."""
        valid, quarantined, errors = [], [], {}

        for idx, r in enumerate(records):
            rec_id = r.get("transaction_id") or f"row_{idx}"
            prov_err = self._validate_common_provenance(r)
            if prov_err:
                code, msg = prov_err
                quarantined.append(QuarantineRecord(family="transactions", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            required = [
                "transaction_id", "lot_id", "collector_pseudonym", "facility_id",
                "material_id", "final_weight_g", "agreed_total_paise", "lifecycle_status",
            ]
            missing = [f for f in required if not r.get(f)]
            if missing:
                code = "MISSING_REQUIRED_FIELDS"
                msg = f"Missing required fields: {', '.join(missing)}"
                quarantined.append(QuarantineRecord(family="transactions", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            # Weight > 0
            try:
                wt = int(r["final_weight_g"])
                if wt <= 0:
                    raise ValueError("Weight must be positive")
            except (ValueError, TypeError):
                code = "NON_POSITIVE_WEIGHT"
                msg = f"Invalid final_weight_g: {r.get('final_weight_g')}"
                quarantined.append(QuarantineRecord(family="transactions", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            # Money: agreed >= 0, acknowledged_paid <= agreed
            try:
                agreed = int(r["agreed_total_paise"])
                if agreed < 0:
                    raise ValueError("Agreed total cannot be negative")
                paid_raw = r.get("acknowledged_paid_paise")
                if paid_raw and paid_raw != "":
                    paid = int(paid_raw)
                    if paid < 0:
                        raise ValueError("Paid amount cannot be negative")
                    if paid > agreed:
                        code = "OVERPAYMENT_OR_INVALID_PAID"
                        msg = f"Acknowledged paid {paid} exceeds agreed total {agreed}"
                        quarantined.append(QuarantineRecord(family="transactions", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                        errors[code] = errors.get(code, 0) + 1
                        continue
            except (ValueError, TypeError) as e:
                code = "INVALID_MONEY_AMOUNT"
                msg = f"Invalid money values: {e}"
                quarantined.append(QuarantineRecord(family="transactions", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            valid.append(r)

        return ValidationResult(
            family="transactions",
            total_count=len(records),
            valid_count=len(valid),
            quarantined_count=len(quarantined),
            valid_records=valid,
            quarantined_records=quarantined,
            error_summary=errors,
        )

    def validate_traceability(self, records: List[Dict[str, Any]]) -> ValidationResult:
        """Validate append-only immutable event traceability records."""
        valid, quarantined, errors = [], [], {}

        for idx, r in enumerate(records):
            rec_id = r.get("event_id") or f"row_{idx}"
            prov_err = self._validate_common_provenance(r)
            if prov_err:
                code, msg = prov_err
                quarantined.append(QuarantineRecord(family="traceability", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            required = ["event_id", "aggregate_id", "sequence", "event_type", "payload_sha256", "event_hash"]
            missing = [f for f in required if not r.get(f)]
            if missing:
                code = "MISSING_REQUIRED_FIELDS"
                msg = f"Missing required fields: {', '.join(missing)}"
                quarantined.append(QuarantineRecord(family="traceability", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            # Sequence >= 1
            try:
                seq = int(r["sequence"])
                if seq < 1:
                    raise ValueError("Sequence must be >= 1")
            except (ValueError, TypeError):
                code = "INVALID_EVENT_SEQUENCE"
                msg = f"Sequence must be >= 1, got: {r.get('sequence')}"
                quarantined.append(QuarantineRecord(family="traceability", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            # SHA-256 validation
            for fld in ("payload_sha256", "event_hash"):
                val = str(r.get(fld, ""))
                if not SHA256_HEX_REGEX.match(val):
                    code = "MALFORMED_HASH"
                    msg = f"Field {fld} is not a valid 64-character SHA-256 hex string: {val}"
                    quarantined.append(QuarantineRecord(family="traceability", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                    errors[code] = errors.get(code, 0) + 1
                    break
            else:
                valid.append(r)

        return ValidationResult(
            family="traceability",
            total_count=len(records),
            valid_count=len(valid),
            quarantined_count=len(quarantined),
            valid_records=valid,
            quarantined_records=quarantined,
            error_summary=errors,
        )

    def validate_collectors(self, records: List[Dict[str, Any]]) -> ValidationResult:
        """Validate pseudonymized collector records."""
        valid, quarantined, errors = [], [], {}

        for idx, r in enumerate(records):
            rec_id = r.get("collector_pseudonym") or f"row_{idx}"
            prov_err = self._validate_common_provenance(r)
            if prov_err:
                code, msg = prov_err
                quarantined.append(QuarantineRecord(family="collectors", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            required = ["collector_pseudonym", "preferred_language", "general_region_id"]
            missing = [f for f in required if not r.get(f)]
            if missing:
                code = "MISSING_REQUIRED_FIELDS"
                msg = f"Missing required fields: {', '.join(missing)}"
                quarantined.append(QuarantineRecord(family="collectors", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            lang = r.get("preferred_language")
            if lang not in VALID_LANGUAGES:
                code = "INVALID_LANGUAGE"
                msg = f"Language must be en, hi, or mr; got: {lang}"
                quarantined.append(QuarantineRecord(family="collectors", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            valid.append(r)

        return ValidationResult(
            family="collectors",
            total_count=len(records),
            valid_count=len(valid),
            quarantined_count=len(quarantined),
            valid_records=valid,
            quarantined_records=quarantined,
            error_summary=errors,
        )

    def validate_ai_training(self, records: List[Dict[str, Any]]) -> ValidationResult:
        """Validate licensed AI/ML training dataset metadata records."""
        valid, quarantined, errors = [], [], {}

        for idx, r in enumerate(records):
            rec_id = r.get("image_id") or f"row_{idx}"
            prov_err = self._validate_common_provenance(r)
            if prov_err:
                code, msg = prov_err
                quarantined.append(QuarantineRecord(family="ai_training", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            required = ["image_id", "asset_ref", "sha256", "material_label", "split", "source_id", "license_ref"]
            missing = [f for f in required if not r.get(f)]
            if missing:
                code = "MISSING_REQUIRED_FIELDS"
                msg = f"Missing required fields: {', '.join(missing)}"
                quarantined.append(QuarantineRecord(family="ai_training", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            # Split validation
            split = r.get("split")
            if split not in VALID_SPLITS:
                code = "INVALID_SPLIT"
                msg = f"Split must be train, val, or test; got: {split}"
                quarantined.append(QuarantineRecord(family="ai_training", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            # SHA-256 check
            val = str(r.get("sha256", ""))
            if not SHA256_HEX_REGEX.match(val):
                code = "MALFORMED_HASH"
                msg = f"sha256 is not a valid 64-character hex string: {val}"
                quarantined.append(QuarantineRecord(family="ai_training", record_id=rec_id, error_code=code, error_message=msg, raw_record=r))
                errors[code] = errors.get(code, 0) + 1
                continue

            valid.append(r)

        return ValidationResult(
            family="ai_training",
            total_count=len(records),
            valid_count=len(valid),
            quarantined_count=len(quarantined),
            valid_records=valid,
            quarantined_records=quarantined,
            error_summary=errors,
        )

    def validate_family(self, family: str, records: List[Dict[str, Any]]) -> ValidationResult:
        """Route to appropriate family validator."""
        method_map = {
            "material_catalog": self.validate_material_catalog,
            "materials": self.validate_material_catalog,
            "price_observations": self.validate_price_observations,
            "prices": self.validate_price_observations,
            "recyclers": self.validate_recyclers,
            "facilities": self.validate_recyclers,
            "transactions": self.validate_transactions,
            "traceability": self.validate_traceability,
            "events": self.validate_traceability,
            "collectors": self.validate_collectors,
            "ai_training": self.validate_ai_training,
        }
        validator = method_map.get(family.lower())
        if not validator:
            raise ValueError(f"Unknown family: {family}. Supported: {list(method_map.keys())}")
        return validator(records)
