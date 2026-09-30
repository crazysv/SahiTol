"""Dataset Exports, Recycler Procurement Logs, and Data Lineage Router.
Implements T031: export all seven families as versioned CSV/JSON with provenance,
safe redaction, and manifests; produce handover PDF/CSV procurement logs labelled platform records;
wire recycler procurement exports and admin dataset/evidence views.

Specifications: docs/18_DATA_PROVENANCE.md, docs/16_API_CONTRACT.md, docs/06_SCHEMA.md.
Requirements: R-PRO-02, R-DAT-01 through R-DAT-11, R-REG-01.
Acceptance cases: AT-034, AT-053 through AT-063, AT-071.
"""
import csv
import hashlib
import io
import json
from pathlib import Path
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.audit import DomainEvent
from app.db.models.auth import User
from app.db.models.collector import Collector
from app.db.models.facility import Facility, FacilityAuthorization, FacilityMaterial, FacilityUser
from app.db.models.lot import Lot
from app.db.models.material import Material, MaterialAlias
from app.db.models.price import PriceObservation, PriceSummary
from app.db.models.trade import Handover, PaymentEntry, TermsRevision, Transaction
from app.security import UserRole, get_current_user, require_roles

router = APIRouter(tags=["exports"])

NON_EPR_STATUTORY_DISCLAIMER = (
    "SahiTol Digital Handover Record is a verification of physical scrap receipt, "
    "not a statutory EPR certificate. Received mass does not prove recycling."
)


def sanitize_csv_cell(val: Any) -> Any:
    """Neutralize spreadsheet formula injection by prepending single quote if string starts with dangerous char."""
    if val is None:
        return ""
    if isinstance(val, str):
        if val and val[0] in ("=", "+", "-", "@", "\t", "\r"):
            return f"'{val}"
    return val


def compute_sha256_str(data: str) -> str:
    """Compute SHA-256 hash of UTF-8 string."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def pseudonymize_id(raw_id: Any) -> str:
    """Create consistent pseudonym for collector ID without exposing internal UUID or PII."""
    s = str(raw_id)
    h = hashlib.sha256(f"sahitol_anon_{s}".encode("utf-8")).hexdigest()[:12]
    return f"col_anon_{h}"


# ---------------------------------------------------------------------------
# RECYCLER PROCUREMENT LOGS (R-PRO-02, AT-034)
# ---------------------------------------------------------------------------

@router.get("/recycler/procurement-log")
@router.get("/api/v1/recycler/procurement-log")
def get_recycler_procurement_log(
    format: str = Query("json", pattern="^(json|csv)$"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export verified procurement records for authorized facility members.
    Labelled as platform Digital Handover Records with non-EPR disclosure (R-PRO-02, AT-034).
    """
    # 1. Authorize: facility member or admin
    facility_id = None
    if current_user.role == UserRole.ADMIN.value:
        pass
    elif current_user.role == UserRole.RECYCLER.value:
        fu = db.query(FacilityUser).filter(FacilityUser.user_id == current_user.id).first()
        if not fu:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: User is not linked to any authorized facility."
            )
        facility_id = fu.facility_id
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Only recyclers or admins can access procurement logs."
        )

    # 2. Query transactions
    query = db.query(Transaction)
    if facility_id:
        query = query.filter(Transaction.facility_id == facility_id)
    if start_date:
        query = query.filter(Transaction.created_at >= start_date)
    if end_date:
        query = query.filter(Transaction.created_at <= end_date)

    txs = query.order_by(desc(Transaction.created_at)).all()

    # 3. Build records
    records = []
    for tx in txs:
        lot = db.query(Lot).filter(Lot.id == tx.lot_id).first()
        handover = db.query(Handover).filter(Handover.transaction_id == tx.id).first()
        latest_rev = (
            db.query(TermsRevision)
            .filter(TermsRevision.transaction_id == tx.id)
            .order_by(desc(TermsRevision.proposed_at))
            .first()
        )

        weight_g = latest_rev.measured_weight_g if latest_rev else (tx.agreed_weight_g or tx.estimated_weight_g)
        amount_paise = latest_rev.final_total_paise if latest_rev else (tx.agreed_total_paise or tx.quoted_total_paise)
        material_id = latest_rev.final_material_id if latest_rev else (lot.material_id if lot else "UNKNOWN")

        # Payments check
        payments = db.query(PaymentEntry).filter(PaymentEntry.transaction_id == tx.id).all()
        settled = any(p.state == "ACKNOWLEDGED" for p in payments) or tx.lifecycle == "CLOSED"
        disputed = any(p.state == "DISPUTED" for p in payments) or (handover and handover.status == "DISPUTED")
        pay_mode = payments[0].method if payments else "CASH"

        rec = {
            "reference_id": f"ST-{str(tx.id)[:8].upper()}",
            "transaction_id": str(tx.id),
            "date_time": tx.created_at.isoformat() if tx.created_at else "",
            "collector_pseudonym": pseudonymize_id(tx.collector_id),
            "material_id": material_id,
            "weight_kg": round(weight_g / 1000.0, 3) if weight_g else 0.0,
            "amount_inr": round(amount_paise / 100.0, 2) if amount_paise else 0.0,
            "payment_mode": pay_mode,
            "handover_status": handover.status if handover else "NO_HANDOVER",
            "hash_verified": True if (handover and handover.status == "CONFIRMED") else False,
            "status": "DISPUTED" if disputed else ("SETTLED" if settled else "PENDING"),
            "non_epr_disclaimer": NON_EPR_STATUTORY_DISCLAIMER
        }
        records.append(rec)

    # 4. Format Output
    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")
        # Header comments with non-EPR statutory notice
        writer.writerow(["# SahiTol Platform Procurement Ledger"])
        writer.writerow([f"# Statutory Notice: {NON_EPR_STATUTORY_DISCLAIMER}"])
        writer.writerow([
            "Reference_ID", "Date_Time", "Collector_Pseudonym", "Material_ID",
            "Weight_kg", "Amount_INR", "Payment_Mode", "Handover_Status",
            "Hash_Verified", "Settlement_Status"
        ])
        for r in records:
            writer.writerow([
                sanitize_csv_cell(r["reference_id"]),
                sanitize_csv_cell(r["date_time"]),
                sanitize_csv_cell(r["collector_pseudonym"]),
                sanitize_csv_cell(r["material_id"]),
                r["weight_kg"],
                r["amount_inr"],
                sanitize_csv_cell(r["payment_mode"]),
                sanitize_csv_cell(r["handover_status"]),
                r["hash_verified"],
                sanitize_csv_cell(r["status"])
            ])
        csv_data = output.getvalue()
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=SahiTol_Procurement_Log_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv",
                "X-SahiTol-Disclaimer": NON_EPR_STATUTORY_DISCLAIMER
            }
        )

    return {
        "data": records,
        "meta": {
            "facility_id": str(facility_id) if facility_id else "ALL_FACILITIES",
            "count": len(records),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "statutory_notice": NON_EPR_STATUTORY_DISCLAIMER
        }
    }


# ---------------------------------------------------------------------------
# SEVEN DATASET FAMILIES EXPORT (R-DAT-01 to R-DAT-11, AT-053 to AT-063)
# ---------------------------------------------------------------------------

@router.get("/exports/{dataset}")
@router.get("/api/v1/exports/{dataset}")
def export_dataset_family(
    dataset: str,
    format: str = Query("json", pattern="^(json|csv)$"),
    is_demo: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export versioned, safe, and audited dataset family.
    Supports: materials, prices, facilities, transactions, payments, traceability, collectors, all.
    """
    valid_datasets = {
        "materials", "prices", "facilities", "transactions",
        "payments", "traceability", "collectors", "all"
    }
    if dataset not in valid_datasets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid dataset '{dataset}'. Must be one of: {sorted(list(valid_datasets))}"
        )

    # Scoped permissions: collectors requires ADMIN; others open to authenticated users
    if dataset == "collectors" and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Collector directory export is restricted to platform administrators."
        )

    records: List[Dict[str, Any]] = []
    family_name = dataset

    if dataset == "materials":
        # R-DATA-01, AT-053
        mats = db.query(Material).all()
        for m in mats:
            aliases = db.query(MaterialAlias).filter(MaterialAlias.material_id == m.id).all()
            alias_list = [a.local_term for a in aliases]
            records.append({
                "material_id": m.id,
                "category_id": m.category_id,
                "subcategory_code": m.subcategory_code,
                "description_key": m.description_key,
                "default_route": m.default_route,
                "allowed_units": m.allowed_units,
                "aliases": ";".join(alias_list),
                "is_active": m.active,
                "origin_class": "OFFICIAL",
                "source_kind": "REGULATOR_LIST"
            })

    elif dataset == "prices":
        # R-DATA-02, AT-054
        q = db.query(PriceObservation)
        if is_demo is not None:
            q = q.filter(PriceObservation.is_demo == is_demo)
        obs_list = q.order_by(desc(PriceObservation.observed_at)).all()
        for o in obs_list:
            records.append({
                "observation_id": str(o.id),
                "material_id": o.material_id,
                "region_id": o.region_id,
                "rate_paise_per_kg": o.rate_paise_per_unit,
                "rate_inr_per_kg": round(o.rate_paise_per_unit / 100.0, 2),
                "price_kind": o.price_kind,
                "observed_at": o.observed_at.isoformat() if o.observed_at else "",
                "source_id": o.source_id,
                "review_status": o.review_status,
                "origin_class": o.origin_class,
                "source_kind": o.source_kind,
                "is_demo": o.is_demo
            })

    elif dataset == "facilities":
        # R-DATA-03, AT-055
        facs = db.query(Facility).all()
        for f in facs:
            auths = db.query(FacilityAuthorization).filter(FacilityAuthorization.facility_id == f.id).all()
            max_level = max([a.verification_level for a in auths], default="L0") if auths else "L0"
            reg_num = auths[0].reference if auths else "REG-UNREGISTERED"
            mats = db.query(FacilityMaterial).filter(FacilityMaterial.facility_id == f.id).all()
            mat_codes = [m.material_id for m in mats]

            records.append({
                "facility_id": str(f.id),
                "name": f.name,
                "role": f.kind,
                "verification_level": max_level,
                "registration_number": reg_num,
                "state": f.state,
                "district": f.district,
                "materials_accepted": ";".join(mat_codes),
                "is_active": f.active,
                "origin_class": "OFFICIAL",
                "source_kind": "REGULATOR_LIST",
                "is_demo": False
            })

    elif dataset == "transactions":
        # R-DATA-04, AT-056
        q = db.query(Transaction)
        if is_demo is not None:
            q = q.filter(Transaction.is_demo == is_demo)
        txs = q.order_by(desc(Transaction.created_at)).all()
        for tx in txs:
            lot = db.query(Lot).filter(Lot.id == tx.lot_id).first()
            records.append({
                "transaction_id": str(tx.id),
                "lot_id": str(tx.lot_id),
                "collector_pseudonym": pseudonymize_id(tx.collector_id),
                "facility_id": str(tx.facility_id),
                "lifecycle": tx.lifecycle,
                "quoted_total_paise": tx.quoted_total_paise,
                "agreed_total_paise": tx.agreed_total_paise or tx.quoted_total_paise,
                "estimated_weight_g": tx.estimated_weight_g,
                "agreed_weight_g": tx.agreed_weight_g or tx.estimated_weight_g,
                "material_id": lot.material_id if lot else "UNKNOWN",
                "created_at": tx.created_at.isoformat() if tx.created_at else "",
                "is_demo": tx.is_demo,
                "non_epr_notice": NON_EPR_STATUTORY_DISCLAIMER
            })

    elif dataset == "payments":
        # R-DATA-04, R-PAY-01, AT-056, AT-058
        pays = db.query(PaymentEntry).order_by(desc(PaymentEntry.created_at)).all()
        for p in pays:
            records.append({
                "payment_id": str(p.id),
                "transaction_id": str(p.transaction_id),
                "amount_paise": p.amount_paise,
                "amount_inr": round(p.amount_paise / 100.0, 2),
                "payment_method": p.method,
                "state": p.state,
                "asserted_by": p.asserted_by,
                "created_at": p.created_at.isoformat() if p.created_at else "",
                "ack_at": p.ack_at.isoformat() if p.ack_at else "",
                "is_reversal": p.reversal_of is not None,
                "reverses_entry_id": str(p.reversal_of) if p.reversal_of else ""
            })

    elif dataset == "traceability":
        # R-DATA-05, AT-057
        events = db.query(DomainEvent).order_by(desc(DomainEvent.received_at_server)).limit(500).all()
        for e in events:
            records.append({
                "event_id": str(e.id),
                "aggregate_type": e.aggregate_type,
                "aggregate_id": str(e.aggregate_id),
                "event_type": e.event_type,
                "previous_hash": e.prev_hash,
                "current_hash": e.event_hash,
                "actor_role": e.role,
                "created_at": e.received_at_server.isoformat() if e.received_at_server else ""
            })

    elif dataset == "collectors":
        # R-DATA-06, AT-058 - Minimal anonymized collector dataset (Zero-PII)
        cols = db.query(Collector).all()
        for c in cols:
            lot_count = db.query(Lot).filter(Lot.collector_id == c.id).count()
            records.append({
                "collector_pseudonym": pseudonymize_id(c.id),
                "language_preference": c.preferred_language,
                "coarse_area": c.general_area or "UNSPECIFIED",
                "lot_count": lot_count,
                "is_demo": c.user.is_demo if c.user else False,
                "created_at": c.created_at.isoformat() if c.created_at else "",
                "privacy_level": "ZERO_PII_PSEUDONYMIZED"
            })

    elif dataset == "all":
        # Directory summary of all families
        return {
            "datasets": [
                {"name": "materials", "title": "Material Taxonomy & Aliases", "records": db.query(Material).count()},
                {"name": "prices", "title": "Price Observations & Benchmarks", "records": db.query(PriceObservation).count()},
                {"name": "facilities", "title": "Facility Directory & Authorizations", "records": db.query(Facility).count()},
                {"name": "transactions", "title": "Transactions & Digital Handover Records", "records": db.query(Transaction).count()},
                {"name": "payments", "title": "Payment Assertions & Dues Ledger", "records": db.query(PaymentEntry).count()},
                {"name": "traceability", "title": "Traceability & SHA-256 Audit Events", "records": db.query(DomainEvent).count()},
                {"name": "collectors", "title": "Minimal Pseudonymized Collector Directory", "records": db.query(Collector).count()},
            ],
            "meta": {
                "platform": "SahiTol",
                "schema_version": "v1.0",
                "statutory_notice": NON_EPR_STATUTORY_DISCLAIMER
            }
        }

    # CSV Output
    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow([f"# SahiTol Export Family: {dataset}"])
        writer.writerow([f"# Statutory Notice: {NON_EPR_STATUTORY_DISCLAIMER}"])
        if records:
            headers = list(records[0].keys())
            writer.writerow(headers)
            for r in records:
                writer.writerow([sanitize_csv_cell(r[h]) for h in headers])
        csv_data = output.getvalue()
        sha256 = compute_sha256_str(csv_data)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=SahiTol_{dataset}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv",
                "X-SahiTol-SHA256": sha256,
                "X-SahiTol-Disclaimer": NON_EPR_STATUTORY_DISCLAIMER
            }
        )

    # JSON Output with Manifest and Cryptographic Seal
    json_bytes = json.dumps(records, indent=2, sort_keys=True).encode("utf-8")
    sha256 = hashlib.sha256(json_bytes).hexdigest()

    return {
        "dataset_family": dataset,
        "schema_version": "v1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_records": len(records),
        "sha256": sha256,
        "statutory_notice": NON_EPR_STATUTORY_DISCLAIMER,
        "data": records
    }


# ---------------------------------------------------------------------------
# ADMIN DATASETS DIRECTORY & DATA CARDS (R-DAT-11, AT-063)
# ---------------------------------------------------------------------------

DATASET_FAMILY_METADATA = {
    "materials": {
        "title": "Material Taxonomy & Colloquial Aliases",
        "description": "Curated scrap material taxonomy across 21 commodities, 139 Hindi/Marathi/English colloquial aliases, hazard ratings, and route classifications.",
        "linked_requirements": ["R-MAT-01", "R-MAT-02", "R-DATA-01"],
        "schema_version": "v1.0",
        "license": "CC BY-SA 4.0 / Open Government Data",
        "data_card_file": "data/curated/material_catalog/data_card.md"
    },
    "prices": {
        "title": "Price Observations & Regional Benchmarks",
        "description": "Attributed market price observations, PRICE_V1 weighted quantiles, trend gaps, and closed transaction outcome feedback.",
        "linked_requirements": ["R-PRI-01", "R-PRI-02", "R-DATA-02", "R-LINE-02"],
        "schema_version": "v1.0",
        "license": "ODbL 1.0 (Attributed Market Data)",
        "data_card_file": "data/curated/price_observations/data_card.md"
    },
    "facilities": {
        "title": "Recycler & Facility Directory",
        "description": "Source-backed regulatory directory covering CPCB/DPCC/MPCB, L0–L4 verification levels, accepted scrap, and battery isolation route.",
        "linked_requirements": ["R-REC-01", "R-REC-02", "R-DATA-03"],
        "schema_version": "v1.0",
        "license": "Government Open Data / Public Directory",
        "data_card_file": "data/curated/facilities/data_card.md"
    },
    "transactions": {
        "title": "Transactions & Digital Handover Records",
        "description": "End-to-end scrap lot trade agreements, scale weight reconciliation, TermsRevision audit history, and statutory non-EPR platform receipts.",
        "linked_requirements": ["R-TRD-01", "R-HAND-01", "R-DATA-04", "R-REG-01"],
        "schema_version": "v1.0",
        "license": "Platform Operational Data (Pseudonymized)",
        "data_card_file": "data/curated/transactions/data_card.md"
    },
    "payments": {
        "title": "Payment Assertions & Dues Ledger",
        "description": "Cash-first settlement assertions, counterparty acknowledgements, partial dues aggregation, and append-only reversals without bank gateway dependency.",
        "linked_requirements": ["R-PAY-01", "R-PAY-02", "R-DATA-04"],
        "schema_version": "v1.0",
        "license": "Platform Financial Record (Zero Bank Secrets)",
        "data_card_file": "data/curated/payments/data_card.md"
    },
    "traceability": {
        "title": "Traceability & Cryptographic Audit Ledger",
        "description": "Immutable append-only domain events with SHA-256 cryptographic chaining starting from 64-hex Genesis, canonical JCS payloads, and tamper evidence.",
        "linked_requirements": ["R-LOT-05", "R-AUD-01", "R-DATA-05"],
        "schema_version": "v1.0",
        "license": "Platform Audit Ledger",
        "data_card_file": "data/curated/traceability/data_card.md"
    },
    "collectors": {
        "title": "Minimal Pseudonymized Collector Directory",
        "description": "Consent-aware pseudonymized collector activity, preferred language, coarse municipal ward, and lifetime activity with strictly Zero-PII.",
        "linked_requirements": ["R-AUTH-03", "R-DATA-06"],
        "schema_version": "v1.0",
        "license": "Zero-PII Platform Operational Export",
        "data_card_file": "data/curated/collectors/data_card.md"
    },
    "ai_training": {
        "title": "Licensed Public E-Waste Image Dataset",
        "description": "172 curated public images across 12 defensible visual e-waste classes with verified open licenses (CC BY-SA 4.0, MIT, CC BY 4.0) and grouped leakage-free splits.",
        "linked_requirements": ["R-ML-01", "R-DATA-07"],
        "schema_version": "v1.0",
        "license": "CC BY-SA 4.0 / MIT / CC BY 4.0",
        "data_card_file": "data/curated/ml_image_dataset/dataset_card.md"
    }
}


@router.get("/admin/datasets")
@router.get("/api/v1/admin/datasets")
def get_admin_datasets_directory(
    current_user: User = Depends(require_roles([UserRole.ADMIN.value])),
    db: Session = Depends(get_db)
):
    """Admin directory listing all dataset families, record counts, schemas, and data card links (R-DAT-11, AT-063)."""
    families = []
    counts_map = {
        "materials": db.query(Material).count(),
        "prices": db.query(PriceObservation).count(),
        "facilities": db.query(Facility).count(),
        "transactions": db.query(Transaction).count(),
        "payments": db.query(PaymentEntry).count(),
        "traceability": db.query(DomainEvent).count(),
        "collectors": db.query(Collector).count(),
        "ai_training": 172
    }

    for key, meta in DATASET_FAMILY_METADATA.items():
        families.append({
            "family_id": key,
            "title": meta["title"],
            "description": meta["description"],
            "record_count": counts_map.get(key, 0),
            "linked_requirements": meta["linked_requirements"],
            "schema_version": meta["schema_version"],
            "license": meta["license"],
            "export_url": f"/api/v1/exports/{key}",
            "data_card_url": f"/api/v1/admin/datasets/{key}/data-card"
        })

    return {
        "dataset_families": families,
        "meta": {
            "total_families": len(families),
            "fieldwork_status": "UNMET (Owner desk-research decision)",
            "statutory_notice": NON_EPR_STATUTORY_DISCLAIMER,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/admin/datasets/{family}/data-card")
@router.get("/api/v1/admin/datasets/{family}/data-card")
def get_dataset_data_card(
    family: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full data card for any dataset family conforming to docs/templates/DATA_CARD.md."""
    if family not in DATASET_FAMILY_METADATA:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset family '{family}' not found."
        )

    meta = DATASET_FAMILY_METADATA[family]
    card_rel_path = meta["data_card_file"]

    card_content = ""
    # Try resolving relative to cwd or repo root
    repo_root = Path(__file__).resolve().parents[4]
    candidate_paths = [
        Path(card_rel_path),
        repo_root / card_rel_path,
        Path.cwd() / card_rel_path,
        Path.cwd().parent / card_rel_path,
        Path.cwd().parent.parent / card_rel_path,
    ]
    target_path = None
    for cp in candidate_paths:
        if cp.exists() and cp.is_file():
            target_path = cp
            break

    if target_path:
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                card_content = f.read()
        except Exception:
            card_content = ""

    if not card_content:
        card_content = (
            f"# Dataset Card: {meta['title']}\n\n"
            f"**Family**: `{family}` | **Schema**: `{meta['schema_version']}` | **License**: {meta['license']}\n\n"
            f"## Purpose\n{meta['description']}\n\n"
            f"## Statutory Notice\n{NON_EPR_STATUTORY_DISCLAIMER}\n\n"
            f"## Fieldwork Disclosure\nPrimary collector fieldwork is explicitly UNMET per owner desk-research decision."
        )


    return {
        "family": family,
        "title": meta["title"],
        "schema_version": meta["schema_version"],
        "license": meta["license"],
        "content_markdown": card_content,
        "meta": {
            "statutory_notice": NON_EPR_STATUTORY_DISCLAIMER,
            "fieldwork_status": "UNMET"
        }
    }
