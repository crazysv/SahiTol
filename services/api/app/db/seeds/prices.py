"""Attributed price seed loader."""
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.price import PriceObservation
from app.db.models.provenance import DataSource
from app.db.models.facility import Region

logger = logging.getLogger(__name__)

def _find_seeds_dir() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "data" / "seeds"
        if candidate.exists() and candidate.is_dir():
            return candidate
    return Path(__file__).resolve().parents[4] / "data" / "seeds"

SEEDS_DIR = _find_seeds_dir()


def seed_regions(db: Session) -> int:
    """Ensure baseline regions exist for price observations in spatial-supported DBs."""
    if db.bind and db.bind.dialect.name == "sqlite":
        return 0

    regions = [
        {"id": "DELHI_NCR", "name": "Delhi National Capital Region", "state_code": "DL", "kind": "STATE"},
        {"id": "MAHARASHTRA", "name": "Maharashtra", "state_code": "MH", "kind": "STATE"},
    ]
    count = 0
    for reg_data in regions:
        existing = db.execute(select(Region).where(Region.id == reg_data["id"])).scalar_one_or_none()
        if not existing:
            db.add(Region(**reg_data))
            count += 1
    db.flush()
    return count


def seed_price_sources(db: Session) -> int:
    """Seed price observation data sources."""
    sources = [
        {
            "id": "SRC-01",
            "publisher": "Central Pollution Control Board (CPCB), MoEFCC",
            "title": "E-Waste (Management) Rules, 2022 & Implementation Guidelines",
            "url": "https://cpcb.nic.in/e-waste/",
            "publication_date": datetime(2022, 11, 2, tzinfo=timezone.utc),
            "source_kind": "GOVERNMENT_PUBLICATION",
            "licence": "Government Open Data / Public Notice",
            "review_status": "VERIFIED",
        },
        {
            "id": "SRC-04",
            "publisher": "Delhi Scrap Traders & Aggregators Market Survey (Secondary)",
            "title": "Delhi-NCR Informal E-Waste Trade Price Index (Mayapuri / Seelampur)",
            "url": "https://delhi.gov.in/waste-market-survey-2026",
            "publication_date": datetime(2026, 8, 15, tzinfo=timezone.utc),
            "source_kind": "PUBLIC_MARKET_QUOTE",
            "licence": "Public Reference Survey / Desk Research",
            "review_status": "VERIFIED",
        },
        {
            "id": "SRC-05",
            "publisher": "Maharashtra Industrial Development Corporation & Metal Trade Reports",
            "title": "Maharashtra Secondary Metals & Scrap Electronic Benchmark Survey",
            "url": "https://midcindia.org/metal-scrap-benchmarks",
            "publication_date": datetime(2026, 8, 20, tzinfo=timezone.utc),
            "source_kind": "PUBLIC_MARKET_QUOTE",
            "licence": "Public Market Report",
            "review_status": "VERIFIED",
        },
    ]
    count = 0
    for src_data in sources:
        existing = db.execute(select(DataSource).where(DataSource.id == src_data["id"])).scalar_one_or_none()
        if not existing:
            source = DataSource(**src_data)
            db.add(source)
            count += 1
        else:
            for k, v in src_data.items():
                setattr(existing, k, v)
    db.flush()
    return count


def seed_price_observations(db: Session) -> int:
    """Seed attributed public price observations."""
    seed_regions(db)
    seed_price_sources(db)
    seed_file = SEEDS_DIR / "price_observations.json"
    if not seed_file.exists():
        raise FileNotFoundError(f"Missing seed file: {seed_file}")

    with open(seed_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    for item in data:
        # Convert string ID to UUID
        obs_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, item["id"])
        existing = db.execute(select(PriceObservation).where(PriceObservation.id == obs_uuid)).scalar_one_or_none()
        obs_date = datetime.fromisoformat(item["observed_at"].replace("Z", "+00:00"))
        if not existing:
            obs = PriceObservation(
                id=obs_uuid,
                material_id=item["material_id"],
                subcategory_id=item.get("subcategory_id"),
                region_id=item["region_id"],
                condition=item.get("condition"),
                rate_paise_per_unit=item["rate_paise_per_unit"],
                unit=item.get("unit", "kg"),
                price_kind=item.get("price_kind", "BUY"),
                observed_at=obs_date,
                source_id=item["source_id"],
                review_status=item.get("review_status", "VERIFIED"),
                origin_class=item.get("origin_class", "EXTERNAL_PUBLIC"),
                source_kind=item.get("source_kind", "PUBLIC_MARKET_QUOTE"),
                is_demo=item.get("is_demo", False),
            )
            db.add(obs)
            count += 1

    db.commit()
    return count
