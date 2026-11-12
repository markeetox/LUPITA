"""Normalize broad benthic habitat classes from the FWC Unified Reef Map."""
from __future__ import annotations

from collections import Counter

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


def build_habitat_layers(features: list[dict], lats: np.ndarray, lons: np.ndarray,
                         class_field: str = "FIRST_ClassLv0") -> tuple[dict, dict]:
    """Rasterize mapped habitat categories on the SST grid.

    Returns per-category fractional cover plus an all-mapped cover layer.
    An empty category is not evidence that the habitat is absent: only
    mapped_cover distinguishes mapped source area from unknown/unmapped area.
    """
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

    mapped_cover = rasterize_cover(mapped_features, lats, lons) if mapped_features else np.zeros((len(lats), len(lons)))
    covers = {
        category: rasterize_cover(items, lats, lons)
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
