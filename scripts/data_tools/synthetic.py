"""Reproducible synthetic dataset generator and edge-case scenario fixtures.
Complies with docs/18_DATA_PROVENANCE.md (Section 4) and R-DATA-10.
All generated records have origin_class=SYNTHETIC, source_kind=SYNTHETIC_GENERATOR, is_demo=True.
"""

from __future__ import annotations
import hashlib
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .provenance import OriginClass, SourceKind, ReviewStatus, LocationQuality


class EdgeScenario(BaseModel):
    """Specification of an explicit edge/failure scenario fixture."""
    scenario_id: str
    category: str
    title: str
    description: str
    expected_error_or_behavior: str
    fixture_data: Dict[str, Any]


class SyntheticGenerator:
    """Deterministic, seeded synthetic data generator for SahiTol demo workflows and edge tests."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)
        self.source_id = "SRC-SYNTHETIC-GEN-01"
        self.schema_version = "v1.0"
        self.base_time = datetime(2026, 9, 28, 10, 0, 0, tzinfo=timezone.utc)

    def _iso_time(self, offset_minutes: int = 0) -> str:
        t = self.base_time + timedelta(minutes=offset_minutes)
        return t.isoformat()

    def generate_material_catalog(self) -> List[Dict[str, Any]]:
        """Generate demo material catalog entries."""
        materials = [
            ("MAT-PCB-01", "PCB", "PCB_GRADE_A", "Motherboard / Server PCB", "मदरबोर्ड पीसीबी", "मदरबोर्ड पीसीबी", "AUTHORIZED_EWASTE", False, "kg,g", "SG-EWASTE-01"),
            ("MAT-PCB-02", "PCB", "PCB_LOW", "Low-grade appliance board", "लो-ग्रेड सर्किट बोर्ड", "कमी-दर्जा सर्किट बोर्ड", "AUTHORIZED_EWASTE", False, "kg,g", "SG-EWASTE-01"),
            ("MAT-BAT-01", "BATTERY", "BAT_LEAD_ACID", "Lead-Acid Inverter/Auto Battery", "लेड-एसिड बैटरी", "लेड-एसिड बॅटरी", "BATTERY_ISOLATION", True, "kg,piece", "SG-BATTERY-01"),
            ("MAT-BAT-02", "BATTERY", "BAT_LI_ION", "Lithium-Ion Phone/Laptop Battery", "लिथियम-आयन बैटरी", "लिथियम-आयन बॅटरी", "BATTERY_ISOLATION", True, "kg,piece", "SG-BATTERY-02"),
            ("MAT-BAT-03", "BATTERY", "BAT_UNKNOWN", "Unknown Chemistry Battery", "अज्ञात रसायन बैटरी", "अज्ञात रसायन बॅटरी", "BATTERY_ISOLATION", True, "kg,piece", "SG-BATTERY-03"),
            ("MAT-CAB-01", "CABLES", "CAB_COPPER", "Insulated Copper Wire", "कॉपर केबल / तार", "तांबे केबल / वायर", "GENERAL_RECYCLING", False, "kg,g", "SG-GENERAL-01"),
            ("MAT-CRT-01", "CRT", "CRT_MONITOR", "CRT Monitor / Glass Tube", "सीआरटी मॉनिटर", "सीआरटी मॉनिटर", "HAZARDOUS_DISPOSAL", True, "piece,kg", "SG-HAZARD-01"),
            ("MAT-LCD-01", "LCD", "LCD_PANEL", "LCD / LED Flat Screen Panel", "एलसीडी / एलईडी स्क्रीन", "एलसीडी / एलईडी स्क्रीन", "AUTHORIZED_EWASTE", False, "piece,kg", "SG-EWASTE-02"),
            ("MAT-PLA-01", "PLASTICS", "PLA_MIXED_E", "Rigid E-Waste Plastics (ABS/HIPS)", "कठोर प्लास्टिक (ई-कचरा)", "कठीण प्लास्टिक", "GENERAL_RECYCLING", False, "kg", "SG-GENERAL-02"),
            ("MAT-MOT-01", "MOTORS", "MOT_COPPER", "Electric Motor / Copper Coil", "इलेक्ट्रिक मोटर", "इलेक्ट्रिक मोटर", "GENERAL_RECYCLING", False, "kg,piece", "SG-GENERAL-01"),
        ]
        records = []
        for mat_id, cat, subcat, name_en, name_hi, name_mr, route, req_ctx, units, sg in materials:
            records.append({
                "material_id": mat_id,
                "category_code": cat,
                "subcategory_code": subcat,
                "label_en": name_en,
                "label_hi": name_hi,
                "label_mr": name_mr,
                "default_route": route,
                "route_requires_context": req_ctx,
                "allowed_units": units,
                "safety_guide_ids": json.dumps([sg]),
                "source_id": self.source_id,
                "origin_class": OriginClass.SYNTHETIC.value,
                "source_kind": SourceKind.SYNTHETIC_GENERATOR.value,
                "is_demo": True,
                "schema_version": self.schema_version,
            })
        return records

    def generate_price_observations(self) -> List[Dict[str, Any]]:
        """Generate demo price observations across Delhi-NCR and Maharashtra."""
        obs = [
            ("DEMO-PRICE-001", "MAT-PCB-01", "PCB_GRADE_A", "CLEAN_SORTED", "DELHI_NCR", "BUY", 32000, "kg", "INR", -120),
            ("DEMO-PRICE-002", "MAT-PCB-01", "PCB_GRADE_A", "CLEAN_SORTED", "DELHI_NCR", "BUY", 34000, "kg", "INR", -60),
            ("DEMO-PRICE-003", "MAT-PCB-01", "PCB_GRADE_A", "CLEAN_SORTED", "DELHI_NCR", "QUOTE", 35000, "kg", "INR", -30),
            ("DEMO-PRICE-004", "MAT-BAT-01", "BAT_LEAD_ACID", "INTACT", "DELHI_NCR", "BUY", 8200, "kg", "INR", -180),
            ("DEMO-PRICE-005", "MAT-BAT-01", "BAT_LEAD_ACID", "INTACT", "DELHI_NCR", "BUY", 8500, "kg", "INR", -90),
            ("DEMO-PRICE-006", "MAT-BAT-02", "BAT_LI_ION", "INTACT", "DELHI_NCR", "BUY", 14000, "kg", "INR", -45),
            ("DEMO-PRICE-007", "MAT-CAB-01", "CAB_COPPER", "UNSTRIPPED", "DELHI_NCR", "BUY", 38000, "kg", "INR", -15),
            ("DEMO-PRICE-008", "MAT-PCB-01", "PCB_GRADE_A", "CLEAN_SORTED", "MAHARASHTRA", "BUY", 31000, "kg", "INR", -100),
            ("DEMO-PRICE-009", "MAT-PCB-01", "PCB_GRADE_A", "CLEAN_SORTED", "MAHARASHTRA", "BUY", 33500, "kg", "INR", -40),
            ("DEMO-PRICE-010", "MAT-CAB-01", "CAB_COPPER", "UNSTRIPPED", "MAHARASHTRA", "BUY", 37500, "kg", "INR", -20),
        ]
        records = []
        for p_id, mat_id, subcat, cond, reg, pkind, rate, unit, curr, offset in obs:
            records.append({
                "id": p_id,
                "material_id": mat_id,
                "subcategory_id": subcat,
                "condition": cond,
                "region_id": reg,
                "price_kind": pkind,
                "rate_paise_per_unit": rate,
                "unit": unit,
                "currency": curr,
                "observed_at": self._iso_time(offset),
                "facility_id": "DEMO-FAC-001" if reg == "DELHI_NCR" else "DEMO-FAC-002",
                "transaction_id": "",
                "source_id": self.source_id,
                "review_status": ReviewStatus.VERIFIED.value,
                "origin_class": OriginClass.SYNTHETIC.value,
                "source_kind": SourceKind.SYNTHETIC_GENERATOR.value,
                "is_demo": True,
                "schema_version": self.schema_version,
            })
        return records

    def generate_recyclers(self) -> List[Dict[str, Any]]:
        """Generate demo facilities with explicit demo flag and regional coverage."""
        facs = [
            ("DEMO-FAC-001", "Demo Pragati E-Waste Recycler", "RECYCLER", "DELHI_NCR", "Plot 42, Mayapuri Industrial Area Phase II, New Delhi", 28.6321, 77.1215, "GEOCODED_APPROXIMATE", "AUTHORIZED_EWASTE", "CPCB-DEMO-DL-001", "VALID", "2027-12-31", True, "MAT-PCB-01,MAT-BAT-01,MAT-CAB-01"),
            ("DEMO-FAC-002", "Demo Sahyadri Eco Processing", "RECYCLER", "MAHARASHTRA", "MIDC Bhosari, Pimpri-Chinchwad, Pune", 18.6298, 73.8423, "GEOCODED_APPROXIMATE", "AUTHORIZED_EWASTE", "MPCB-DEMO-MH-002", "VALID", "2027-06-30", True, "MAT-PCB-01,MAT-CAB-01,MAT-PLA-01"),
            ("DEMO-FAC-003", "Demo Okhla Battery Dismantler", "DISMANTLER", "DELHI_NCR", "Okhla Industrial Area Phase I, New Delhi", 28.5312, 77.2789, "GEOCODED_APPROXIMATE", "BATTERY_ISOLATION", "DPCC-DEMO-DL-003", "VALID", "2026-11-15", False, "MAT-BAT-01,MAT-BAT-02"),
            ("DEMO-FAC-004", "Demo Marathwada Metal Aggregator", "AGGREGATOR", "MAHARASHTRA", "MIDC Waluj, Chhatrapati Sambhajinagar", 19.8341, 75.2412, "COARSE_DISTRICT", "GENERAL_RECYCLING", "MPCB-DEMO-MH-004", "VALID", "2028-03-31", False, "MAT-CAB-01,MAT-MOT-01"),
        ]
        records = []
        for f_id, name, ftype, reg, addr, lat, lon, qual, route, reg_ref, status, v_until, pickup, mats in facs:
            records.append({
                "facility_id": f_id,
                "name": name,
                "facility_type": ftype,
                "region_id": reg,
                "public_address": addr,
                "latitude": lat,
                "longitude": lon,
                "location_quality": qual,
                "route": route,
                "registration_reference": reg_ref,
                "registration_status": status,
                "valid_until": v_until,
                "last_verified_at": "2026-09-28T00:00:00Z",
                "verification_level": "DEMO_SIMULATED",
                "materials_accepted": mats,
                "pickup_available": pickup,
                "service_area": reg,
                "source_id": self.source_id,
                "origin_class": OriginClass.SYNTHETIC.value,
                "source_kind": SourceKind.SYNTHETIC_GENERATOR.value,
                "is_demo": True,
                "schema_version": self.schema_version,
            })
        return records

    def generate_collectors(self) -> List[Dict[str, Any]]:
        """Generate demo pseudonymized collectors."""
        cols = [
            ("DEMO-COL-001", "Rajesh", "hi", "DELHI_NCR", -1440, 2),
            ("DEMO-COL-002", "Santosh", "mr", "MAHARASHTRA", -2880, 1),
            ("DEMO-COL-003", "Anil", "en", "DELHI_NCR", -4320, 0),
        ]
        records = []
        for c_id, alias, lang, reg, offset, lots in cols:
            records.append({
                "collector_pseudonym": c_id,
                "alias": alias,
                "preferred_language": lang,
                "general_region_id": reg,
                "created_at": self._iso_time(offset),
                "active_lot_count": lots,
                "source_id": self.source_id,
                "origin_class": OriginClass.SYNTHETIC.value,
                "source_kind": SourceKind.SYNTHETIC_GENERATOR.value,
                "is_demo": True,
                "schema_version": self.schema_version,
            })
        return records

    def generate_transactions(self) -> List[Dict[str, Any]]:
        """Generate demo completed transactions."""
        txs = [
            ("DEMO-TX-001", "DEMO-LOT-001", "DEMO-COL-001", "DEMO-FAC-001", "MAT-PCB-01", 12500, 425000, "INR", "COMPLETED", "CONFIRMED", "SETTLED_CASH", 425000, 0, -45),
            ("DEMO-TX-002", "DEMO-LOT-002", "DEMO-COL-002", "DEMO-FAC-002", "MAT-CAB-01", 24000, 900000, "INR", "COMPLETED", "CONFIRMED", "SETTLED_CASH", 900000, 0, -30),
        ]
        records = []
        for tx_id, lot_id, col_id, fac_id, mat_id, wt, agreed, curr, l_stat, h_stat, p_stat, paid, out, offset in txs:
            records.append({
                "transaction_id": tx_id,
                "lot_id": lot_id,
                "collector_pseudonym": col_id,
                "facility_id": fac_id,
                "material_id": mat_id,
                "final_weight_g": wt,
                "agreed_total_paise": agreed,
                "currency": curr,
                "lifecycle_status": l_stat,
                "handover_status": h_stat,
                "payment_status": p_stat,
                "acknowledged_paid_paise": paid,
                "outstanding_paise": out,
                "occurred_at": self._iso_time(offset),
                "source_id": self.source_id,
                "origin_class": OriginClass.SYNTHETIC.value,
                "source_kind": SourceKind.SYNTHETIC_GENERATOR.value,
                "is_demo": True,
                "schema_version": self.schema_version,
            })
        return records

    def generate_traceability(self) -> List[Dict[str, Any]]:
        """Generate demo immutable event traceability records with valid sha256 hashes."""
        events = [
            ("DEMO-EVT-001", "DEMO-TX-001", 1, "LOT_SUBMITTED", "DEMO-COL-001", -120),
            ("DEMO-EVT-002", "DEMO-TX-001", 2, "OFFER_ACCEPTED", "DEMO-COL-001", -90),
            ("DEMO-EVT-003", "DEMO-TX-001", 3, "HANDOVER_CONFIRMED", "DEMO-FAC-001", -50),
            ("DEMO-EVT-004", "DEMO-TX-001", 4, "PAYMENT_ACKNOWLEDGED", "DEMO-COL-001", -45),
        ]
        records = []
        prev_hash = "0" * 64
        for e_id, agg_id, seq, etype, actor, offset in events:
            payload = json.dumps({"event_id": e_id, "agg": agg_id, "type": etype, "seq": seq}, sort_keys=True)
            p_hash = hashlib.sha256(payload.encode()).hexdigest()
            evt_hash = hashlib.sha256(f"{prev_hash}|{p_hash}|{seq}".encode()).hexdigest()
            records.append({
                "event_id": e_id,
                "aggregate_id": agg_id,
                "sequence": seq,
                "event_type": etype,
                "actor_pseudonym": actor,
                "device_occurred_at": self._iso_time(offset),
                "received_at_server": self._iso_time(offset + 1),
                "payload_sha256": p_hash,
                "prev_hash": prev_hash,
                "event_hash": evt_hash,
                "media_checksums": "[]",
                "status": "CONFIRMED",
                "source_id": self.source_id,
                "origin_class": OriginClass.SYNTHETIC.value,
                "source_kind": SourceKind.SYNTHETIC_GENERATOR.value,
                "is_demo": True,
                "schema_version": self.schema_version,
            })
            prev_hash = evt_hash
        return records

    def generate_ai_training(self) -> List[Dict[str, Any]]:
        """Generate demo licensed image metadata records."""
        imgs = [
            ("DEMO-IMG-001", "assets/demo/pcb_01.jpg", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "MAT-PCB-01", "train", "CC-BY-4.0"),
            ("DEMO-IMG-002", "assets/demo/pcb_02.jpg", "ca978112ca1bbdcafac231b39a23dc4da7860814966f07d2f9d1469e38f5f64b", "MAT-PCB-01", "val", "CC-BY-4.0"),
            ("DEMO-IMG-003", "assets/demo/battery_01.jpg", "fb8e20fc2e4c3f248c60c39bd652f3c1347298bb977b8b4d59f62862ee1829b2", "MAT-BAT-01", "train", "CC0"),
            ("DEMO-IMG-004", "assets/demo/cable_01.jpg", "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae", "MAT-CAB-01", "test", "CC-BY-SA-4.0"),
        ]
        records = []
        for img_id, asset_ref, sha, label, split, lic in imgs:
            records.append({
                "image_id": img_id,
                "asset_ref": asset_ref,
                "sha256": sha,
                "material_label": label,
                "object_group_id": f"OBJ-{img_id}",
                "source_group": "PUBLIC_LICENSED",
                "split": split,
                "source_id": self.source_id,
                "license_ref": lic,
                "label_reviewer": "REV-DEMO-01",
                "label_confidence": 0.95,
                "condition": "INTACT",
                "weight_g": 500,
                "region_id": "DELHI_NCR",
                "transaction_id": "",
                "origin_class": OriginClass.SYNTHETIC.value,
                "source_kind": SourceKind.SYNTHETIC_GENERATOR.value,
                "is_demo": True,
                "schema_version": self.schema_version,
            })
        return records

    def generate_all_families(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate all seven dataset families as a dictionary."""
        return {
            "material_catalog": self.generate_material_catalog(),
            "price_observations": self.generate_price_observations(),
            "recyclers": self.generate_recyclers(),
            "collectors": self.generate_collectors(),
            "transactions": self.generate_transactions(),
            "traceability": self.generate_traceability(),
            "ai_training": self.generate_ai_training(),
        }

    def generate_edge_scenarios(self) -> List[EdgeScenario]:
        """Generate the 15 required operational and anomaly edge scenarios.
        Complies with docs/18_DATA_PROVENANCE.md (Section 4).
        """
        scenarios = [
            EdgeScenario(
                scenario_id="EDGE-01-HAPPY-PATH",
                category="WORKFLOW",
                title="Ordinary Successful Trade",
                description="Collector classifies lot, receives quote, accepts, completes QR handover, and acknowledges cash payment.",
                expected_error_or_behavior="All states progress normally; transaction status SETTLED_CASH with zero outstanding balance.",
                fixture_data={"lot_id": "LOT-HAPPY-01", "status": "COMPLETED", "paid_paise": 340000, "agreed_paise": 340000},
            ),
            EdgeScenario(
                scenario_id="EDGE-02-NO-PRICE-COHORT",
                category="PRICING",
                title="Zero or Insufficient Price Cohort",
                description="Rare or unobserved material grade with < 3 recent observations in region.",
                expected_error_or_behavior="Median rate and bounds evaluate to null (never zero placeholder); UI displays INSUFFICIENT_DATA badge.",
                fixture_data={"material_id": "MAT-RARE-01", "observations_count": 0, "expected_rate": None, "reason_code": "INSUFFICIENT_DATA"},
            ),
            EdgeScenario(
                scenario_id="EDGE-03-STALE-EXPIRED-ROUTE",
                category="REGULATION",
                title="Recycler Authorization Expired",
                description="Facility's regulatory authorization expired on 2026-08-31; current date is 2026-09-28.",
                expected_error_or_behavior="Facility is flagged EXPIRED_AUTHORIZATION; filtered out of active matching suggestions.",
                fixture_data={"facility_id": "FAC-EXPIRED-01", "valid_until": "2026-08-31", "current_date": "2026-09-28", "eligible": False},
            ),
            EdgeScenario(
                scenario_id="EDGE-04-UNKNOWN-BATTERY-CHEMISTRY",
                category="SAFETY",
                title="Battery with Unknown Chemistry",
                description="Lot submitted with battery material but unknown chemistry tag (lead-acid vs li-ion ambiguous).",
                expected_error_or_behavior="System routes strictly to BATTERY_ISOLATION route and emits mandatory fire-safety warning guide.",
                fixture_data={"material_id": "MAT-BAT-03", "route": "BATTERY_ISOLATION", "safety_guide": "SG-BATTERY-03"},
            ),
            EdgeScenario(
                scenario_id="EDGE-05-LOW-CONFIDENCE-IMAGE",
                category="ML",
                title="Classifier Low Confidence Abstention",
                description="LiteRT model predicts PCB with top confidence 0.42, below the 0.70 acceptance threshold.",
                expected_error_or_behavior="Model abstains (abstained=true); prompts collector with top-3 manual material selector.",
                fixture_data={"model_confidence": 0.42, "threshold": 0.70, "abstained": True, "top_candidates": ["MAT-PCB-01", "MAT-PCB-02", "OTHER"]},
            ),
            EdgeScenario(
                scenario_id="EDGE-06-REJECTED-OFFER",
                category="NEGOTIATION",
                title="Collector Rejects Recycler Quote",
                description="Recycler quotes rate below collector expectation; collector explicitly rejects.",
                expected_error_or_behavior="Offer status becomes REJECTED; lot returns to AVAILABLE pool without transaction creation.",
                fixture_data={"offer_id": "OFF-REJ-01", "status": "REJECTED", "rejection_reason": "PRICE_TOO_LOW"},
            ),
            EdgeScenario(
                scenario_id="EDGE-07-EXPIRED-OFFER",
                category="NEGOTIATION",
                title="Recycler Quote Expires",
                description="Offer valid for 4 hours expires before collector acts.",
                expected_error_or_behavior="Server rejects acceptance with 410 Gone / OFFER_EXPIRED; lot unreserved.",
                fixture_data={"offer_id": "OFF-EXP-01", "expires_at": "2026-09-28T08:00:00Z", "attempted_at": "2026-09-28T12:00:00Z", "status": "EXPIRED"},
            ),
            EdgeScenario(
                scenario_id="EDGE-08-CHANGED-WEIGHT",
                category="HANDOVER",
                title="Scale Discrepancy at Recycler Facility",
                description="Collector estimated 15,000g; facility certified scale reads 12,000g.",
                expected_error_or_behavior="Emits TERMS_REVISION; both parties must sign updated terms hash before handover confirms.",
                fixture_data={"estimated_g": 15000, "measured_g": 12000, "delta_pct": -20.0, "requires_terms_revision": True},
            ),
            EdgeScenario(
                scenario_id="EDGE-09-PARTIAL-PAYMENT",
                category="PAYMENT",
                title="Partial Cash Settlement",
                description="Agreed total is Rs 1,000 (100,000 paise); recycler pays Rs 600 in cash now.",
                expected_error_or_behavior="Transaction status PARTIALLY_PAID; outstanding_paise remains 40,000; ledger records balance.",
                fixture_data={"agreed_paise": 100000, "paid_paise": 60000, "outstanding_paise": 40000, "payment_status": "PARTIAL"},
            ),
            EdgeScenario(
                scenario_id="EDGE-10-DISPUTED-PAYMENT",
                category="PAYMENT",
                title="Disputed Cash Payment Assertion",
                description="Recycler asserts cash was handed over; collector denies receipt.",
                expected_error_or_behavior="Payment state remains UNACKNOWLEDGED; triggers DISPUTE quality flag; does not settle.",
                fixture_data={"asserted_by": "FACILITY", "acknowledged_by": None, "state": "DISPUTED", "flag": "PAYMENT_UNACKNOWLEDGED"},
            ),
            EdgeScenario(
                scenario_id="EDGE-11-DUPLICATE-OPERATION",
                category="SYNC",
                title="Replayed Outbox Operation ID",
                description="Client network glitch causes identical operation UUID to be submitted twice.",
                expected_error_or_behavior="Server responds idempotently with original commit result; no duplicate entity or event created.",
                fixture_data={"operation_id": "OP-DUP-001", "attempt_count": 2, "idempotent_replay": True, "http_status": 200},
            ),
            EdgeScenario(
                scenario_id="EDGE-12-CONFLICTING-EDIT",
                category="SYNC",
                title="Optimistic Concurrency Version Conflict",
                description="Client pushes update based on server version 1, but server is already at version 2.",
                expected_error_or_behavior="Server rejects mutation with HTTP 409 Conflict; client preserves local draft and prompts merge.",
                fixture_data={"expected_version": 1, "server_version": 2, "error_code": "VERSION_CONFLICT", "http_status": 409},
            ),
            EdgeScenario(
                scenario_id="EDGE-13-MISSING-IMAGE",
                category="MEDIA",
                title="Lot Created Without Photo",
                description="Offline collector submits draft lot without capturing photo.",
                expected_error_or_behavior="Draft saved locally; submit blocked until photo captured or explicit manual reason provided.",
                fixture_data={"lot_id": "LOT-NOIMG-01", "has_photo": False, "status": "DRAFT", "can_submit": False},
            ),
            EdgeScenario(
                scenario_id="EDGE-14-DENIED-GPS",
                category="LOCATION",
                title="Location Captured Without GPS Permission",
                description="Collector denies Android GPS location runtime permission.",
                expected_error_or_behavior="Location record fallback to LocationQuality.COARSE_DISTRICT; never claims precise distance.",
                fixture_data={"gps_enabled": False, "location_quality": "COARSE_DISTRICT", "point": None, "accuracy_m": None},
            ),
            EdgeScenario(
                scenario_id="EDGE-15-CLOCK-SKEW",
                category="INTEGRITY",
                title="Severe Client Clock Skew (> 2 Hours)",
                description="Client device clock is set 4 hours in the future due to incorrect manual time settings.",
                expected_error_or_behavior="Server records occurred_at_client as evidence, but orders transaction by received_at_server.",
                fixture_data={"client_clock_skew_sec": 14400, "server_override_ordering": True, "flag": "SEVERE_CLOCK_SKEW"},
            ),
        ]
        return scenarios
