"""Validation helpers for the versioned spatial context catalog.

This module is intentionally descriptive-only. It does not feed production scoring.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VALID_FEATURE_TYPES = {
    "bay", "bay_subregion", "inlet", "pass", "channel", "flat",
    "nearshore_zone", "reef", "reef_tract", "monitoring_station",
}
VALID_GEOMETRIES = {
    "Point", "MultiPoint", "LineString", "MultiLineString",
    "Polygon", "MultiPolygon",
}
VALID_RELATIONSHIPS = {"part_of", "connects_to", "overlaps", "near"}


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _valid_position(position: Any) -> bool:
    return (
        isinstance(position, list)
        and len(position) >= 2
        and _is_number(position[0])
        and _is_number(position[1])
        and -180 <= position[0] <= 180
        and -90 <= position[1] <= 90
    )


def _valid_line(coordinates: Any) -> bool:
    return isinstance(coordinates, list) and len(coordinates) >= 2 and all(_valid_position(p) for p in coordinates)


def _valid_polygon(coordinates: Any) -> bool:
    if not isinstance(coordinates, list) or not coordinates:
        return False
    for ring in coordinates:
        if not isinstance(ring, list) or len(ring) < 4:
            return False
        if not all(_valid_position(p) for p in ring) or ring[0][:2] != ring[-1][:2]:
            return False
    return True


def validate_geometry(geometry: Any) -> list[str]:
    if geometry is None:
        return []
    if not isinstance(geometry, dict):
        return ["geometry must be a GeoJSON geometry object or null"]
    kind, coords = geometry.get("type"), geometry.get("coordinates")
    if kind not in VALID_GEOMETRIES:
        return [f"unsupported GeoJSON geometry type: {kind!r}"]
    if kind == "Point":
        valid = _valid_position(coords)
    elif kind == "MultiPoint":
        valid = isinstance(coords, list) and bool(coords) and all(_valid_position(p) for p in coords)
    elif kind == "LineString":
        valid = _valid_line(coords)
    elif kind == "MultiLineString":
        valid = isinstance(coords, list) and bool(coords) and all(_valid_line(line) for line in coords)
    elif kind == "Polygon":
        valid = _valid_polygon(coords)
    else:
        valid = isinstance(coords, list) and bool(coords) and all(_valid_polygon(poly) for poly in coords)
    return [] if valid else [f"invalid coordinates for GeoJSON {kind}"]


def validate_catalog(catalog: Any) -> list[str]:
    """Return deterministic validation errors; an empty list means structurally valid."""
    errors: list[str] = []
    if not isinstance(catalog, dict):
        return ["catalog root must be an object"]
    if catalog.get("schema_version") != 1:
        errors.append("schema_version must equal 1")
    if catalog.get("crs") != "EPSG:4326":
        errors.append("crs must be EPSG:4326")
    region = catalog.get("region")
    if not isinstance(region, dict) or not region.get("id") or not region.get("name"):
        errors.append("region must contain non-empty id and name")
    features = catalog.get("features")
    if not isinstance(features, list):
        return errors + ["features must be an array"]

    ids: set[str] = set()
    for index, feature in enumerate(features):
        prefix = f"features[{index}]"
        if not isinstance(feature, dict):
            errors.append(f"{prefix} must be an object")
            continue
        feature_id = feature.get("id")
        if not isinstance(feature_id, str) or not feature_id:
            errors.append(f"{prefix}.id must be a non-empty string")
        elif feature_id in ids:
            errors.append(f"duplicate feature id: {feature_id}")
        else:
            ids.add(feature_id)
        if not isinstance(feature.get("name"), str) or not feature["name"].strip():
            errors.append(f"{prefix}.name must be a non-empty string")
        if feature.get("feature_type") not in VALID_FEATURE_TYPES:
            errors.append(f"{prefix}.feature_type is unsupported")
        if feature.get("region_id") != (region or {}).get("id"):
            errors.append(f"{prefix}.region_id must match the catalog region")
        geometry_status = feature.get("geometry_status")
        if geometry_status not in {"verified", "provisional", "pending_authoritative_geometry", "not_applicable"}:
            errors.append(f"{prefix}.geometry_status is unsupported")
        geometry = feature.get("geometry")
        if geometry is None and geometry_status in {"verified", "provisional"}:
            errors.append(f"{prefix} cannot claim verified/provisional geometry when geometry is null")
        if geometry is not None and geometry_status == "pending_authoritative_geometry":
            errors.append(f"{prefix} has geometry but is marked pending_authoritative_geometry")
        errors.extend(f"{prefix}: {message}" for message in validate_geometry(geometry))
        provenance = feature.get("provenance")
        if not isinstance(provenance, dict) or not isinstance(provenance.get("sources"), list):
            errors.append(f"{prefix}.provenance.sources must be an array")

    for index, feature in enumerate(features):
        if not isinstance(feature, dict):
            continue
        for relationship_index, relationship in enumerate(feature.get("relationships", [])):
            rel_prefix = f"features[{index}].relationships[{relationship_index}]"
            if not isinstance(relationship, dict):
                errors.append(f"{rel_prefix} must be an object")
                continue
            if relationship.get("type") not in VALID_RELATIONSHIPS:
                errors.append(f"{rel_prefix}.type is unsupported")
            target_id = relationship.get("target_id")
            if target_id not in ids:
                errors.append(f"{rel_prefix}.target_id does not resolve: {target_id!r}")

    return errors


def load_catalog(path: Path | None = None) -> dict[str, Any]:
    path = path or ROOT / "data" / "spatial" / "catalog.json"
    return json.loads(path.read_text(encoding="utf-8"))


VALID_HABITAT_ROLES = {
    "foraging", "feeding", "occupancy", "movement", "refuge",
    "spawning_context", "connectivity", "nursery",
}
VALID_EVIDENCE_STATUSES = {
    "supported_general_association", "candidate_association",
}
VALID_LOCAL_VALIDATION = {"required", "in_progress", "validated", "not_applicable"}


def validate_habitat_contexts(value: Any) -> list[str]:
    """Validate optional descriptive species habitat contexts without scoring them."""
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["habitat_contexts must be an object"]
    if value.get("schema_version") != 1:
        errors.append("habitat_contexts.schema_version must equal 1")
    contexts = value.get("contexts")
    if not isinstance(contexts, list):
        return errors + ["habitat_contexts.contexts must be an array"]
    ids: set[str] = set()
    for index, context in enumerate(contexts):
        prefix = f"habitat_contexts.contexts[{index}]"
        if not isinstance(context, dict):
            errors.append(f"{prefix} must be an object")
            continue
        context_id = context.get("id")
        if not isinstance(context_id, str) or not context_id:
            errors.append(f"{prefix}.id must be a non-empty string")
        elif context_id in ids:
            errors.append(f"duplicate habitat context id: {context_id}")
        else:
            ids.add(context_id)
        feature_types = context.get("feature_types")
        if not isinstance(feature_types, list) or not feature_types:
            errors.append(f"{prefix}.feature_types must be a non-empty array")
        elif any(kind not in VALID_FEATURE_TYPES for kind in feature_types):
            errors.append(f"{prefix}.feature_types contains an unsupported feature type")
        roles = context.get("habitat_roles")
        if not isinstance(roles, list) or not roles:
            errors.append(f"{prefix}.habitat_roles must be a non-empty array")
        elif any(role not in VALID_HABITAT_ROLES for role in roles):
            errors.append(f"{prefix}.habitat_roles contains an unsupported role")
        if context.get("evidence_status") not in VALID_EVIDENCE_STATUSES:
            errors.append(f"{prefix}.evidence_status is unsupported")
        if context.get("local_validation") not in VALID_LOCAL_VALIDATION:
            errors.append(f"{prefix}.local_validation is unsupported")
        sources = context.get("sources")
        if not isinstance(sources, list) or not sources or any(not isinstance(source, str) or not source.startswith(("https://", "http://")) for source in sources):
            errors.append(f"{prefix}.sources must contain at least one HTTP(S) reference")
    return errors
