"""Deduplication and duplicate detection tools with review queue output.
Complies with docs/18_DATA_PROVENANCE.md (Section 3).
"""

from __future__ import annotations
import hashlib
import json
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field


class DuplicateCluster(BaseModel):
    """Cluster of potential duplicate records."""
    cluster_key: str
    match_rule: str
    canonical_id: str
    duplicate_ids: List[str]
    records: List[Dict[str, Any]]
    confidence: float
    requires_manual_review: bool = True


class DuplicateReport(BaseModel):
    """Comprehensive duplicate detection report."""
    family: str
    total_records: int
    unique_records_count: int
    duplicate_clusters_count: int
    clusters: List[DuplicateCluster] = Field(default_factory=list)


class Deduplicator:
    """Detects exact and near-duplicates across dataset families."""

    @staticmethod
    def _normalize_name_address(name: str, address: str) -> str:
        """Create normalized composite key for facility matching."""
        clean_name = re.sub(r"[^\w\s]", "", str(name).lower())
        clean_name = re.sub(r"\s+", " ", clean_name).strip()
        clean_addr = re.sub(r"[^\w\s]", "", str(address).lower())
        clean_addr = re.sub(r"\s+", " ", clean_addr).strip()
        return f"{clean_name}|{clean_addr}"

    def deduplicate_facilities(
        self, records: List[Dict[str, Any]], id_field: str = "facility_id"
    ) -> Tuple[List[Dict[str, Any]], DuplicateReport]:
        """Deduplicate recyclers using registration reference first, then normalized name+address.
        Does NOT auto-merge differing facility roles or separate branches.
        """
        seen_refs: Dict[str, Dict[str, Any]] = {}
        seen_names: Dict[str, Dict[str, Any]] = {}
        unique_records: List[Dict[str, Any]] = []
        clusters: List[DuplicateCluster] = []
        seen_ids: Set[str] = set()

        for r in records:
            rec_id = str(r.get(id_field, ""))
            reg_ref = str(r.get("registration_reference", "")).strip().upper()
            name = str(r.get("name", ""))
            addr = str(r.get("public_address", ""))
            name_addr_key = self._normalize_name_address(name, addr)

            # Rule 1: Stable registration reference match
            if reg_ref and reg_ref != "NONE" and reg_ref != "NULL" and reg_ref in seen_refs:
                primary = seen_refs[reg_ref]
                primary_id = str(primary.get(id_field))
                clusters.append(
                    DuplicateCluster(
                        cluster_key=reg_ref,
                        match_rule="REGISTRATION_REFERENCE_EXACT",
                        canonical_id=primary_id,
                        duplicate_ids=[rec_id],
                        records=[primary, r],
                        confidence=1.0,
                        requires_manual_review=False,
                    )
                )
                continue

            # Rule 2: Normalized name + address match (Manual Review queue)
            if name_addr_key and name_addr_key in seen_names:
                primary = seen_names[name_addr_key]
                primary_id = str(primary.get(id_field))
                # If roles differ, preserve both but flag for review
                if primary.get("facility_type") != r.get("facility_type"):
                    clusters.append(
                        DuplicateCluster(
                            cluster_key=name_addr_key,
                            match_rule="NAME_ADDRESS_DIFFERING_ROLES",
                            canonical_id=primary_id,
                            duplicate_ids=[rec_id],
                            records=[primary, r],
                            confidence=0.85,
                            requires_manual_review=True,
                        )
                    )
                    unique_records.append(r)
                    continue
                else:
                    clusters.append(
                        DuplicateCluster(
                            cluster_key=name_addr_key,
                            match_rule="NAME_ADDRESS_EXACT",
                            canonical_id=primary_id,
                            duplicate_ids=[rec_id],
                            records=[primary, r],
                            confidence=0.95,
                            requires_manual_review=True,
                        )
                    )
                    continue

            # Unique record
            if reg_ref and reg_ref != "NONE" and reg_ref != "NULL":
                seen_refs[reg_ref] = r
            if name_addr_key:
                seen_names[name_addr_key] = r
            unique_records.append(r)

        report = DuplicateReport(
            family="recyclers",
            total_records=len(records),
            unique_records_count=len(unique_records),
            duplicate_clusters_count=len(clusters),
            clusters=clusters,
        )
        return unique_records, report

    def deduplicate_price_observations(
        self, records: List[Dict[str, Any]], id_field: str = "id"
    ) -> Tuple[List[Dict[str, Any]], DuplicateReport]:
        """Detect duplicate price observations within the same cohort and timestamp."""
        seen: Dict[str, Dict[str, Any]] = {}
        unique_records: List[Dict[str, Any]] = []
        clusters: List[DuplicateCluster] = []

        for r in records:
            rec_id = str(r.get(id_field, ""))
            key = (
                f"{r.get('material_id')}|{r.get('subcategory_id')}|{r.get('region_id')}|"
                f"{r.get('condition')}|{r.get('rate_paise_per_unit')}|{r.get('price_kind')}|"
                f"{r.get('observed_at')}|{r.get('source_id')}"
            )
            if key in seen:
                primary = seen[key]
                primary_id = str(primary.get(id_field))
                clusters.append(
                    DuplicateCluster(
                        cluster_key=key,
                        match_rule="EXACT_PRICE_COHORT_AND_TIMESTAMP",
                        canonical_id=primary_id,
                        duplicate_ids=[rec_id],
                        records=[primary, r],
                        confidence=1.0,
                        requires_manual_review=False,
                    )
                )
            else:
                seen[key] = r
                unique_records.append(r)

        report = DuplicateReport(
            family="price_observations",
            total_records=len(records),
            unique_records_count=len(unique_records),
            duplicate_clusters_count=len(clusters),
            clusters=clusters,
        )
        return unique_records, report

    def deduplicate_by_sha256(
        self, records: List[Dict[str, Any]], hash_field: str = "sha256", id_field: str = "image_id"
    ) -> Tuple[List[Dict[str, Any]], DuplicateReport]:
        """Deduplicate AI images or assets by exact SHA-256 payload hash."""
        seen: Dict[str, Dict[str, Any]] = {}
        unique_records: List[Dict[str, Any]] = []
        clusters: List[DuplicateCluster] = []

        for r in records:
            rec_id = str(r.get(id_field, ""))
            h = str(r.get(hash_field, "")).strip().lower()
            if h and h in seen:
                primary = seen[h]
                primary_id = str(primary.get(id_field))
                clusters.append(
                    DuplicateCluster(
                        cluster_key=h,
                        match_rule="EXACT_SHA256_COLLISION",
                        canonical_id=primary_id,
                        duplicate_ids=[rec_id],
                        records=[primary, r],
                        confidence=1.0,
                        requires_manual_review=False,
                    )
                )
            else:
                if h:
                    seen[h] = r
                unique_records.append(r)

        report = DuplicateReport(
            family="ai_training",
            total_records=len(records),
            unique_records_count=len(unique_records),
            duplicate_clusters_count=len(clusters),
            clusters=clusters,
        )
        return unique_records, report
