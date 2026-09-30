"""Data ingestion staging, cleaning, and normalization tools.
Complies with docs/18_DATA_PROVENANCE.md and docs/06_SCHEMA.md.
"""

from __future__ import annotations
import csv
import json
import math
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union
import pandas as pd
from .provenance import sanitize_csv_cell


def normalize_text(val: Optional[str]) -> Optional[str]:
    """Clean and normalize string values using Unicode NFC and collapsed whitespace."""
    if val is None:
        return None
    if not isinstance(val, str):
        val = str(val)
    val = unicodedata.normalize("NFC", val)
    val = re.sub(r"\s+", " ", val).strip()
    return val if val else None


def normalize_phone(val: Optional[str]) -> Optional[str]:
    """Normalize phone numbers to +91XXXXXXXXXX format for Indian 10-digit mobiles.
    Rejects invalid lengths or non-numeric garbage.
    """
    if not val:
        return None
    # Strip spaces, hyphens, parentheses, and leading +
    digits = re.sub(r"\D", "", str(val))
    if len(digits) == 10 and digits[0] in "6789":
        return f"+91{digits}"
    elif len(digits) == 12 and digits.startswith("91") and digits[2] in "6789":
        return f"+{digits}"
    elif len(digits) == 11 and digits.startswith("0") and digits[1] in "6789":
        return f"+91{digits[1:]}"
    return None


def convert_to_paise(val: Any) -> int:
    """Convert decimal rupees or integer paise to 64-bit integer paise.
    1 Rupee = 100 Paise.
    Raises ValueError on invalid numbers, infinity, or NaN.
    """
    if val is None or (isinstance(val, float) and math.isnan(val)):
        raise ValueError("Cannot convert null/NaN to integer paise")
    if isinstance(val, int):
        return val
    try:
        f_val = float(str(val).strip().replace(",", ""))
        if not math.isfinite(f_val):
            raise ValueError("Amount is infinite or NaN")
        # Round half up to avoid floating point inaccuracies
        return int(round(f_val * 100))
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid monetary value: {val}") from e


def convert_to_grams(val: Any, unit: str = "kg") -> int:
    """Convert weight to 64-bit integer grams.
    Supported units: 'g', 'gram', 'grams', 'kg', 'kilogram', 'ton', 'tonne', 'quintal'.
    Raises ValueError if weight is non-positive or invalid.
    """
    if val is None or (isinstance(val, float) and math.isnan(val)):
        raise ValueError("Cannot convert null/NaN to integer grams")
    unit_norm = str(unit).lower().strip()
    try:
        f_val = float(str(val).strip().replace(",", ""))
        if not math.isfinite(f_val):
            raise ValueError("Weight is infinite or NaN")
        if f_val <= 0:
            raise ValueError(f"Weight must be strictly positive (>0), got: {f_val}")
        
        if unit_norm in ("g", "gram", "grams"):
            multiplier = 1.0
        elif unit_norm in ("kg", "kilogram", "kilograms"):
            multiplier = 1000.0
        elif unit_norm in ("quintal", "quintals"):
            multiplier = 100000.0
        elif unit_norm in ("ton", "tonne", "tons", "tonnes"):
            multiplier = 1000000.0
        else:
            raise ValueError(f"Unsupported weight unit: {unit}")
        
        return int(round(f_val * multiplier))
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid weight measurement: {val} {unit}") from e


def load_records(filepath: Union[str, Path]) -> List[Dict[str, Any]]:
    """Load records from CSV, JSON, or JSON-Lines file into a list of dictionaries."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    suffix = path.suffix.lower()
    if suffix == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
            else:
                raise ValueError("JSON file must contain an array or object")
    elif suffix == ".jsonl":
        records = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records
    elif suffix == ".csv":
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        return df.to_dict(orient="records")
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def save_csv(records: Iterable[Dict[str, Any]], filepath: Union[str, Path], sanitize: bool = True) -> None:
    """Save records to UTF-8 CSV with optional spreadsheet formula injection sanitization."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    records_list = list(records)
    if not records_list:
        path.write_text("", encoding="utf-8")
        return
    
    headers = list(records_list[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for r in records_list:
            row_to_write = {}
            for k, v in r.items():
                cell_val = sanitize_csv_cell(v) if sanitize else v
                row_to_write[k] = "" if cell_val is None else cell_val
            writer.writerow(row_to_write)
