"""
scripts/seed_production.py — Idempotent reference data seeder for production.

Run AFTER `alembic upgrade head` and BEFORE starting the API server.
Safe to run multiple times (all functions use INSERT OR IGNORE / upsert semantics).
Never drops rows, resets sequences, or truncates tables.

Usage:
    python scripts/seed_production.py

Environment:
    DATABASE_URL must be set (postgresql+psycopg://... with ?sslmode=require for hosted).
    MIGRATION_DATABASE_URL may be used if a separate migration-role URL is needed.
"""
import logging
import sys
import os

# Allow running from repository root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "services", "api"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("sahitol.seed")


def main() -> None:
    from app.db.session import SessionLocal
    from app.db.seeds.materials import (
        seed_sources,
        seed_material_categories,
        seed_materials,
        seed_safety_guides,
    )
    from app.db.seeds.facilities import (
        seed_regions,
        seed_facility_sources,
        seed_facilities,
    )
    from app.db.seeds.prices import (
        seed_regions as seed_price_regions,
        seed_price_sources,
        seed_price_observations,
    )

    logger.info("Starting production reference seed.")

    with SessionLocal() as db:
        try:
            # Materials
            n = seed_sources(db)
            logger.info("seed_sources: %d rows affected.", n)

            counts = seed_material_categories(db)
            logger.info("seed_material_categories: %s", counts)

            counts = seed_materials(db)
            logger.info("seed_materials: %s", counts)

            n = seed_safety_guides(db)
            logger.info("seed_safety_guides: %d rows affected.", n)

            # Facilities
            n = seed_regions(db)
            logger.info("seed_regions (facilities): %d rows affected.", n)

            n = seed_facility_sources(db)
            logger.info("seed_facility_sources: %d rows affected.", n)

            n = seed_facilities(db)
            logger.info("seed_facilities: %d rows affected.", n)

            # Prices
            n = seed_price_regions(db)
            logger.info("seed_price_regions: %d rows affected.", n)

            n = seed_price_sources(db)
            logger.info("seed_price_sources: %d rows affected.", n)

            n = seed_price_observations(db)
            logger.info("seed_price_observations: %d rows affected.", n)

            db.commit()
            logger.info("Production seed complete — all reference data committed.")

        except Exception as exc:
            db.rollback()
            logger.error("Seed failed; rolled back. Error: %s", exc)
            sys.exit(1)


if __name__ == "__main__":
    main()
