"""Cached geocoding with strict privacy boundaries and regional validation.
Complies with docs/18_DATA_PROVENANCE.md (Section 5) and R-DATA-09.
"""

from __future__ import annotations
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple
from pydantic import BaseModel, Field
from .provenance import LocationQuality


# Regional bounding boxes: (min_lat, max_lat, min_lon, max_lon)
REGIONAL_BOUNDS: Dict[str, Tuple[float, float, float, float]] = {
    "DELHI_NCR": (28.0, 29.2, 76.5, 77.8),
    "MAHARASHTRA": (15.5, 22.1, 72.5, 80.9),
    "INDIA": (8.0, 37.0, 68.0, 97.0),
}


class GeocodeResult(BaseModel):
    """Normalized geocode result with provenance and quality labelling."""
    query: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_quality: LocationQuality = LocationQuality.UNKNOWN
    accuracy_m: Optional[float] = None
    provider: str = "LOCAL_CACHE"
    cached_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    region_id: Optional[str] = None
    in_bounds: bool = False
    served_from_cache: bool = False
    notes: Optional[str] = None


class CachedGeocoder:
    """Manages address geocoding with local JSON caching and privacy enforcement."""

    def __init__(self, cache_file: Optional[Path | str] = None):
        self.cache_file = Path(cache_file) if cache_file else Path("data/cache/geocoding_cache.json")
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
            except Exception:
                self._cache = {}

    def _save_cache(self) -> None:
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self._cache, f, indent=2, ensure_ascii=False)

    @staticmethod
    def normalize_query(query: str) -> str:
        """Clean and normalize address string for consistent cache keying."""
        q = re.sub(r"[^\w\s]", " ", query.lower())
        return re.sub(r"\s+", " ", q).strip()

    @staticmethod
    def verify_bounds(lat: float, lon: float, region_id: Optional[str] = None) -> bool:
        """Verify that coordinates fall inside the specified region or India territorial bounds."""
        bounds = REGIONAL_BOUNDS.get(str(region_id).upper(), REGIONAL_BOUNDS["INDIA"])
        min_lat, max_lat, min_lon, max_lon = bounds
        return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon

    def geocode(
        self,
        address: str,
        entity_type: str = "FACILITY",
        region_id: Optional[str] = None,
        provider_fn: Optional[Callable[[str], Optional[Tuple[float, float, str]]]] = None,
    ) -> GeocodeResult:
        """Geocode an address with strict privacy enforcement and caching.
        
        PRIVACY GUARD: Collector home addresses must NEVER be sent to external geocoders.
        """
        # Strict privacy protection for informal collectors
        if entity_type.upper() == "COLLECTOR":
            raise PermissionError(
                "Privacy violation: Collector home residences must NEVER be sent to an external geocoder. "
                "Coarse district or manual region selection only."
            )

        norm_key = self.normalize_query(address)
        if not norm_key:
            return GeocodeResult(query=address, location_quality=LocationQuality.UNKNOWN, notes="Empty address query")

        # 1. Check local persistent cache
        if norm_key in self._cache:
            entry = self._cache[norm_key]
            lat = entry.get("latitude")
            lon = entry.get("longitude")
            quality_str = entry.get("location_quality", LocationQuality.UNKNOWN.value)
            in_b = self.verify_bounds(lat, lon, region_id) if (lat is not None and lon is not None) else False
            return GeocodeResult(
                query=address,
                latitude=lat,
                longitude=lon,
                location_quality=LocationQuality(quality_str),
                accuracy_m=entry.get("accuracy_m"),
                provider=entry.get("provider", "LOCAL_CACHE"),
                cached_at=entry.get("cached_at", datetime.now(timezone.utc).isoformat()),
                region_id=region_id,
                in_bounds=in_b,
                served_from_cache=True,
                notes=entry.get("notes"),
            )

        # 2. If provider function supplied (or mock)
        if provider_fn:
            res = provider_fn(norm_key)
            if res:
                lat, lon, quality = res
                in_b = self.verify_bounds(lat, lon, region_id)
                entry = {
                    "latitude": lat,
                    "longitude": lon,
                    "location_quality": quality,
                    "accuracy_m": 50.0 if quality == LocationQuality.GEOCODED_ROOFTOP.value else 1000.0,
                    "provider": "EXTERNAL_PROVIDER",
                    "cached_at": datetime.now(timezone.utc).isoformat(),
                    "region_id": region_id,
                    "in_bounds": in_b,
                    "notes": "Resolved via external provider function",
                }
                self._cache[norm_key] = entry
                self._save_cache()
                return GeocodeResult(
                    query=address,
                    latitude=lat,
                    longitude=lon,
                    location_quality=LocationQuality(quality),
                    accuracy_m=entry["accuracy_m"],
                    provider="EXTERNAL_PROVIDER",
                    cached_at=entry["cached_at"],
                    region_id=region_id,
                    in_bounds=in_b,
                    notes=entry["notes"],
                )

        # 3. Unresolved: return explicit UNKNOWN with null coordinates (never invent coords)
        unresolved_entry = {
            "latitude": None,
            "longitude": None,
            "location_quality": LocationQuality.UNKNOWN.value,
            "accuracy_m": None,
            "provider": "LOCAL_CACHE",
            "cached_at": datetime.now(timezone.utc).isoformat(),
            "region_id": region_id,
            "in_bounds": False,
            "notes": "Unresolved address; coordinates remain explicitly null",
        }
        self._cache[norm_key] = unresolved_entry
        self._save_cache()
        return GeocodeResult(
            query=address,
            location_quality=LocationQuality.UNKNOWN,
            region_id=region_id,
            in_bounds=False,
            notes="Unresolved address; coordinates remain explicitly null",
        )
