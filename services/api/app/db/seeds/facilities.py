"""Facility and recycler directory seed loader."""
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.facility import (
    Region,
    Facility,
    FacilityAuthorization,
    FacilityMaterial,
    FacilityOperation,
    FacilityRate
)
from app.db.models.provenance import DataSource
from geoalchemy2.elements import WKTElement

logger = logging.getLogger(__name__)


def _find_seeds_dir() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "data" / "seeds"
        if candidate.exists() and candidate.is_dir():
            return candidate
    return Path(__file__).resolve().parents[4] / "data" / "seeds"


SEEDS_DIR = _find_seeds_dir()


def seed_regions(db: Session) -> int:
    """Seed baseline regions."""
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


def seed_facility_sources(db: Session) -> int:
    """Seed regulatory and official data sources for facilities."""
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
            "source_kind": "REGULATOR_LIST",
            "licence": "Government Open Data / Public Notice",
            "review_status": "VERIFIED",
        },
        {
            "id": "SRC-04",
            "publisher": "Maharashtra Pollution Control Board (MPCB)",
            "title": "List of Registered E-Waste Recyclers & Dismantlers in Maharashtra",
            "url": "https://www.mpcb.gov.in/waste-management/electronic-waste",
            "publication_date": datetime(2024, 1, 15, tzinfo=timezone.utc),
            "source_kind": "REGULATOR_LIST",
            "licence": "State Government Public Notice",
            "review_status": "VERIFIED",
        },
        {
            "id": "SRC-05",
            "publisher": "Delhi Pollution Control Committee (DPCC)",
            "title": "DPCC Registered E-Waste Dismantlers and Recyclers Registry",
            "url": "https://dpcc.delhi.gov.in/dpcc/e-wastes",
            "publication_date": datetime(2023, 10, 10, tzinfo=timezone.utc),
            "source_kind": "REGULATOR_LIST",
            "licence": "State Government Public Notice",
            "review_status": "VERIFIED",
        },
        {
            "id": "SRC-06",
            "publisher": "New Delhi Municipal Council (NDMC)",
            "title": "NDMC Approved E-Waste Collection & Vendor Depository List",
            "url": "https://www.ndmc.gov.in/cpcb_approved_e-waste_vendors_list.aspx",
            "publication_date": datetime(2022, 4, 1, tzinfo=timezone.utc),
            "source_kind": "GOVERNMENT_PUBLICATION",
            "licence": "Municipal Public Notice",
            "review_status": "VERIFIED",
        },
    ]
    count = 0
    for src_data in sources:
        existing = db.execute(select(DataSource).where(DataSource.id == src_data["id"])).scalar_one_or_none()
        if not existing:
            db.add(DataSource(**src_data))
            count += 1
        else:
            for k, v in src_data.items():
                setattr(existing, k, v)
    db.flush()
    return count


def seed_facilities(db: Session) -> int:
    """Seed dated source-backed facilities, authorizations, accepted materials, and operations."""
    seed_regions(db)
    seed_facility_sources(db)

    seed_file = SEEDS_DIR / "facilities.json"
    if not seed_file.exists():
        raise FileNotFoundError(f"Missing facilities seed file: {seed_file}")

    with open(seed_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    facility_count = 0
    now = datetime.now(timezone.utc)

    for item in data:
        fac_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, item["facility_id"])
        existing_fac = db.execute(select(Facility).where(Facility.id == fac_uuid)).scalar_one_or_none()

        lat = item.get("latitude")
        lon = item.get("longitude")
        geo_point = WKTElement(f"POINT({lon} {lat})", srid=4326) if lat is not None and lon is not None else None

        if not existing_fac:
            fac = Facility(
                id=fac_uuid,
                name=item["name"],
                facility_name=item["name"],
                kind=item["facility_type"],
                address_public=item["public_address"],
                district=item["district"],
                state=item["state"],
                region_id=item["region_id"],
                geo_point=geo_point,
                geocode_accuracy=item.get("location_quality", "UNKNOWN"),
                contact_public=item.get("contact_public"),
                active=True,
                version=1,
                created_at=now,
                updated_at=now
            )
            db.add(fac)
            db.flush()
            facility_count += 1
        else:
            fac = existing_fac
            fac.name = item["name"]
            fac.facility_name = item["name"]
            fac.kind = item["facility_type"]
            fac.address_public = item["public_address"]
            fac.district = item["district"]
            fac.state = item["state"]
            fac.region_id = item["region_id"]
            if geo_point is not None:
                fac.geo_point = geo_point
            fac.geocode_accuracy = item.get("location_quality", "UNKNOWN")
            fac.contact_public = item.get("contact_public")
            db.flush()

        # Authorization
        auth_existing = db.execute(select(FacilityAuthorization).where(FacilityAuthorization.facility_id == fac_uuid)).scalar_one_or_none()
        valid_from = datetime.fromisoformat(item["valid_from"].replace("Z", "+00:00")) if item.get("valid_from") else None
        valid_until = datetime.fromisoformat(item["valid_until"].replace("Z", "+00:00")) if item.get("valid_until") else None
        last_verified = datetime.fromisoformat(item["last_verified_at"].replace("Z", "+00:00")) if item.get("last_verified_at") else None

        authority_map = {
            "SRC-02": "CPCB",
            "SRC-04": "MPCB",
            "SRC-05": "DPCC",
            "SRC-06": "NDMC",
            "SRC-01": "CPCB"
        }
        authority = authority_map.get(item.get("source_id", ""), "REGULATOR")

        if not auth_existing:
            auth = FacilityAuthorization(
                id=uuid.uuid5(uuid.NAMESPACE_DNS, f"{item['facility_id']}:auth"),
                facility_id=fac_uuid,
                route=item["route"],
                authority=authority,
                reference=item["registration_reference"],
                status=item["registration_status"],
                valid_from=valid_from,
                valid_until=valid_until,
                source_id=item.get("source_id"),
                verification_level=item.get("verification_level", "L2"),
                last_verified_at=last_verified,
                scope_notes=f"Source: {item.get('source_id')}; Status: {item['registration_status']}"
            )
            db.add(auth)
        else:
            auth_existing.route = item["route"]
            auth_existing.authority = authority
            auth_existing.reference = item["registration_reference"]
            auth_existing.status = item["registration_status"]
            auth_existing.valid_from = valid_from
            auth_existing.valid_until = valid_until
            auth_existing.verification_level = item.get("verification_level", "L2")
            auth_existing.last_verified_at = last_verified

        # Accepted materials
        for mat_id in item.get("materials_accepted", []):
            mat_existing = db.execute(
                select(FacilityMaterial).where(
                    FacilityMaterial.facility_id == fac_uuid,
                    FacilityMaterial.material_id == mat_id
                )
            ).scalar_one_or_none()
            if not mat_existing:
                db.add(FacilityMaterial(
                    id=uuid.uuid5(uuid.NAMESPACE_DNS, f"{item['facility_id']}:{mat_id}"),
                    facility_id=fac_uuid,
                    material_id=mat_id,
                    route=item["route"],
                    accepted=True,
                    evidence_source_id=item.get("source_id")
                ))

        # Operations
        op_existing = db.execute(select(FacilityOperation).where(FacilityOperation.facility_id == fac_uuid)).scalar_one_or_none()
        accept_status = "ACCEPTING" if item["registration_status"] == "VALID" else "PAUSED"
        if not op_existing:
            db.add(FacilityOperation(
                facility_id=fac_uuid,
                pickup_status=item.get("pickup_available"),
                service_regions=item.get("service_area"),
                accepting_status=accept_status,
                operational_updated_at=last_verified or now,
                source_id=item.get("source_id")
            ))
        else:
            op_existing.pickup_status = item.get("pickup_available")
            op_existing.service_regions = item.get("service_area")
            op_existing.accepting_status = accept_status
            op_existing.operational_updated_at = last_verified or now

    db.commit()
    return facility_count
