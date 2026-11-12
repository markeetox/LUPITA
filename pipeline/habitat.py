"""Normalize and sample benthic habitat from the FWC Unified Reef Map."""
from __future__ import annotations

from collections import Counter
import math

import numpy as np

from pipeline.structure import rasterize_cover


# FWC Unified Reef Map v2.2, Unified Classification Level 0.
# Keep this mapping broad. Do not infer detailed substrate or vegetation types
# from a class that the source does not provide.
CLASS_TO_FEATURE = {
    "coral reef and hardbottom": "hard_bottom",
    "seagrass": "seagrass",
    "unconsolidated sediment": "soft_bottom",
    "artificial": "artificial",
    "dredged/excavated": "dredged",
}


def _class_value(attributes: dict, class_field: str) -> str:
    for key in (class_field, "FIRST_ClassLv0", "ClassLv0", "FIRST_ClassLv1", "ClassLv1"):
        value = attributes.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _feature_bounds(feature: dict):
    rings = (feature.get("geometry") or {}).get("rings") or []
    points = [point for ring in rings for point in ring if len(point) >= 2]
    if not points:
        return None
    return (min(p[0] for p in points), min(p[1] for p in points),
            max(p[0] for p in points), max(p[1] for p in points))


def _rasterize_local(features: list[dict], lats: np.ndarray, lons: np.ndarray,
                     sub: int = 10) -> np.ndarray:
    """Rasterize only the polygon bounding box, then place it on the requested grid.

    The FWC layer covers a small part of the much larger North American SST grid.
    Cropping the supersampled work area avoids allocating a high-resolution array
    across the entire ocean domain for a Florida-only source.
    """
    shape = (len(lats), len(lons))
    out = np.zeros(shape, dtype=float)
    bounds = [_feature_bounds(f) for f in features]
    bounds = [b for b in bounds if b is not None]
    if not bounds or len(lats) < 2 or len(lons) < 2:
        return out

    min_lon = min(b[0] for b in bounds)
    min_lat = min(b[1] for b in bounds)
    max_lon = max(b[2] for b in bounds)
    max_lat = max(b[3] for b in bounds)

    i0 = max(0, int(np.searchsorted(lats, min_lat)) - 1)
    i1 = min(len(lats), int(np.searchsorted(lats, max_lat, side="right")) + 1)
    j0 = max(0, int(np.searchsorted(lons, min_lon)) - 1)
    j1 = min(len(lons), int(np.searchsorted(lons, max_lon, side="right")) + 1)
    if i1 - i0 < 2 or j1 - j0 < 2:
        return out

    out[i0:i1, j0:j1] = rasterize_cover(features, lats[i0:i1], lons[j0:j1], sub=sub)
    return out


def _groups(features: list[dict], class_field: str):
    groups: dict[str, list[dict]] = {}
    class_counts: Counter = Counter()
    unknown_classes: Counter = Counter()
    mapped_features = []

    for feature in features:
        attrs = feature.get("attributes") or {}
        value = _class_value(attrs, class_field)
        if value:
            class_counts[value] += 1
        else:
            unknown_classes["<missing class>"] += 1
        geometry = feature.get("geometry") or {}
        if geometry.get("rings"):
            mapped_features.append(feature)
        category = CLASS_TO_FEATURE.get(value.lower())
        if category and geometry.get("rings"):
            groups.setdefault(category, []).append(feature)
        elif value and geometry.get("rings"):
            unknown_classes[value] += 1
    return groups, class_counts, unknown_classes, mapped_features


def build_habitat_layers(features: list[dict], lats: np.ndarray, lons: np.ndarray,
                         class_field: str = "FIRST_ClassLv0", sub: int = 10) -> tuple[dict, dict]:
    """Rasterize broad categories and all mapped polygons on a common grid.

    A zero category value outside mapped coverage means unknown, not confirmed
    absence. Unknown source classes still contribute to mapped coverage.
    """
    groups, class_counts, unknown_classes, mapped_features = _groups(features, class_field)
    mapped_cover = _rasterize_local(mapped_features, lats, lons, sub) if mapped_features else np.zeros((len(lats), len(lons)))
    covers = {
        category: _rasterize_local(items, lats, lons, sub)
        for category, items in sorted(groups.items())
    }
    stats = {
        "feature_count": len(features),
        "geometry_feature_count": len(mapped_features),
        "class_counts": dict(sorted(class_counts.items())),
        "category_feature_counts": {key: len(value) for key, value in sorted(groups.items())},
        "unknown_classes": dict(sorted(unknown_classes.items())),
        "mapped_cell_count": int(np.count_nonzero(mapped_cover > 0)),
        "category_cell_counts": {key: int(np.count_nonzero(value > 0)) for key, value in covers.items()},
    }
    return {"covers": covers, "mapped_cover": mapped_cover}, stats


def sample_site_habitat(features: list[dict], site: dict, class_field: str = "FIRST_ClassLv0",
                        cell_km: float = 0.25, sub: int = 4) -> dict:
    """Estimate broad mapped habitat cover inside a named site's approximate radius.

    This is descriptive map coverage, not a habitat suitability score. Unmapped
    portions remain unknown and are never treated as confirmed habitat absence.
    """
    lat, lon = float(site["lat"]), float(site["lon"])
    radius = max(0.1, float(site.get("radius_km", 1.5)))
    cos_lat = max(0.1, math.cos(math.radians(lat)))
    dlat, dlon = radius / 111.32, radius / (111.32 * cos_lat)
    prepared = []
    for feature in features:
        bounds = _feature_bounds(feature)
        if bounds and bounds[0] <= lon + dlon and bounds[2] >= lon - dlon and bounds[1] <= lat + dlat and bounds[3] >= lat - dlat:
            prepared.append(feature)

    if not prepared:
        return {
            "status": "unmapped", "mapped_coverage": 0.0, "categories": {},
            "composition": {}, "source_feature_count": 0,
            "sample_resolution_m": int(cell_km * 1000),
            "note": "No FWC habitat polygons intersect this site buffer. Habitat is unknown, not absent."
        }

    dlat_cell = cell_km / 111.32
    dlon_cell = cell_km / (111.32 * cos_lat)
    lats = np.arange(lat - dlat, lat + dlat + dlat_cell * 0.51, dlat_cell)
    lons = np.arange(lon - dlon, lon + dlon + dlon_cell * 0.51, dlon_cell)
    if len(lats) < 2:
        lats = np.array([lat - dlat_cell / 2, lat + dlat_cell / 2])
    if len(lons) < 2:
        lons = np.array([lon - dlon_cell / 2, lon + dlon_cell / 2])

    result, stats = build_habitat_layers(prepared, lats, lons, class_field, sub=sub)
    yy, xx = np.meshgrid(lats, lons, indexing="ij")
    distance = np.sqrt(((yy - lat) * 111.32) ** 2 + ((xx - lon) * 111.32 * cos_lat) ** 2)
    mask = distance <= radius
    if not np.any(mask):
        mask[np.unravel_index(np.argmin(distance), distance.shape)] = True

    mapped = float(np.mean(result["mapped_cover"][mask]))
    categories = {
        key: round(float(np.mean(cover[mask])), 4)
        for key, cover in result["covers"].items()
        if float(np.mean(cover[mask])) > 0
    }
    total_classified = sum(categories.values())
    composition = {
        key: round(value / total_classified, 4)
        for key, value in categories.items()
    } if total_classified > 0 else {}

    return {
        "status": "mapped" if mapped > 0 else "unmapped",
        "mapped_coverage": round(mapped, 4),
        "categories": categories,
        "composition": composition,
        "source_feature_count": stats["geometry_feature_count"],
        "sample_resolution_m": int(cell_km * 1000),
        "note": "Category coverage is the share of the site buffer mapped to each class. Unmapped portions remain unknown."
    }


def sample_sites(features: list[dict], sites: list[dict], class_field: str = "FIRST_ClassLv0",
                 cell_km: float = 0.25, sub: int = 4) -> dict:
    """Return habitat summaries keyed by stable site id or site name."""
    return {
        str(site.get("id") or site["name"]): sample_site_habitat(
            features, site, class_field=class_field, cell_km=cell_km, sub=sub)
        for site in sites
    }
