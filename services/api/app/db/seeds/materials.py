"""Material taxonomy, aliases, and safety guide seeder."""
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.material import MaterialCategory, Material, MaterialAlias, SafetyGuide
from app.db.models.provenance import DataSource

logger = logging.getLogger(__name__)

# Seeds directory path relative to project root or package
def _find_seeds_dir() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "data" / "seeds"
        if candidate.exists() and candidate.is_dir():
            return candidate
    return Path(__file__).resolve().parents[4] / "data" / "seeds"

SEEDS_DIR = _find_seeds_dir()


def load_seed_json(filename: str) -> List[Dict[str, Any]]:
    """Load JSON seed file safely."""
    seed_file = SEEDS_DIR / filename
    if not seed_file.exists():
        raise FileNotFoundError(f"Seed file not found: {seed_file}")
    with open(seed_file, "r", encoding="utf-8") as f:
        return json.load(f)


def seed_sources(db: Session) -> int:
    """Seed foundational regulatory data sources if not present."""
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
            "id": "SRC-02",
            "publisher": "Central Pollution Control Board (CPCB), MoEFCC",
            "title": "Battery Waste Management Rules, 2022 & EPR Portal Guidance",
            "url": "https://eprbattery.cpcb.gov.in/",
            "publication_date": datetime(2022, 8, 22, tzinfo=timezone.utc),
            "source_kind": "GOVERNMENT_PUBLICATION",
            "licence": "Government Open Data / Public Notice",
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


def seed_material_categories(db: Session) -> int:
    """Seed material categories."""
    categories_data = load_seed_json("material_categories.json")
    count = 0
    for item in categories_data:
        existing = db.execute(select(MaterialCategory).where(MaterialCategory.id == item["id"])).scalar_one_or_none()
        if not existing:
            cat = MaterialCategory(**item)
            db.add(cat)
            count += 1
        else:
            for k, v in item.items():
                setattr(existing, k, v)
    db.flush()
    return count


def seed_safety_guides(db: Session) -> int:
    """Seed contextual safety guides."""
    guides_data = load_seed_json("safety_guides.json")
    count = 0
    for item in guides_data:
        existing = db.execute(select(SafetyGuide).where(SafetyGuide.id == item["id"])).scalar_one_or_none()
        if not existing:
            guide = SafetyGuide(**item)
            db.add(guide)
            count += 1
        else:
            for k, v in item.items():
                setattr(existing, k, v)
    db.flush()
    return count


def seed_materials(db: Session) -> Dict[str, int]:
    """Idempotently seed data sources, categories, safety guides, materials, and language aliases."""
    src_count = seed_sources(db)
    cat_count = seed_material_categories(db)
    guide_count = seed_safety_guides(db)

    # Materials
    materials_data = load_seed_json("materials.json")
    mat_count = 0
    for item in materials_data:
        existing = db.execute(select(Material).where(Material.id == item["id"])).scalar_one_or_none()
        if not existing:
            mat = Material(**item)
            db.add(mat)
            mat_count += 1
        else:
            for k, v in item.items():
                setattr(existing, k, v)
    db.flush()

    # Aliases
    aliases_data = load_seed_json("material_aliases.json")
    alias_count = 0
    for item in aliases_data:
        existing = db.execute(
            select(MaterialAlias).where(
                MaterialAlias.material_id == item["material_id"],
                MaterialAlias.language == item["language"],
                MaterialAlias.normalized_term == item["normalized_term"]
            )
        ).scalar_one_or_none()
        if not existing:
            alias = MaterialAlias(**item)
            db.add(alias)
            alias_count += 1
        else:
            existing.local_term = item["local_term"]

    db.commit()
    return {
        "sources_seeded": src_count,
        "categories_seeded": cat_count,
        "safety_guides_seeded": guide_count,
        "materials_seeded": mat_count,
        "aliases_seeded": alias_count,
    }


if __name__ == "__main__":
    from app.db.session import SessionLocal
    with SessionLocal() as session:
        result = seed_materials(session)
        print("Material seeding completed successfully:", result)
