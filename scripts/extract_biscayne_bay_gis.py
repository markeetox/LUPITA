"""Research-only extraction of FWC benthic and FDEP preserve GIS polygons."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

SERVICE = "https://gis.myfwc.com/hosting/rest/services/Projects_FWC/UnifiedReefMapProject_v2_2/MapServer"
FDEP_SERVICE = "https://ags.dep.state.fl.us/arcgis/rest/services/OpenData/AQUATIC_PRESERVES/MapServer"
PAGE_SIZE = 500
MAX_PAGES = 100
TIMEOUT = (15, 90)
LAYERS = {
    "statutory_preserve_boundary": {
        "id": 0,
        "service": FDEP_SERVICE,
        "where": "1=1",
        "filter_attribute": "NAME",
        "filter_contains": "BISCAYNE BAY",
        "description": "FDEP aquatic-preserve polygons filtered locally to Biscayne Bay; official mapped boundary is approximate and not for enforcement.",
    },
    "source_footprints": {
        "id": 0,
        "where": "Source LIKE '%Biscayne Bay%'",
        "description": "Footprints of source benthic mapping projects.",
    },
    "unified_benthic_polygons": {
        "id": 7,
        "where": "FIRST_Source LIKE '%Biscayne Bay%' OR FIRST_Source LIKE '%Biscayne/Miami-Dade%'",
        "description": "Integrated Unified Reef Map Level 1 benthic polygons.",
    },
}


def _coordinates(geometry: dict[str, Any]):
    kind = geometry.get("type")
    coords = geometry.get("coordinates")
    if kind == "Point":
        yield coords
    elif kind in {"MultiPoint", "LineString"}:
        yield from coords
    elif kind in {"MultiLineString", "Polygon"}:
        for part in coords:
            yield from part
    elif kind == "MultiPolygon":
        for polygon in coords:
            for ring in polygon:
                yield from ring
    elif kind == "GeometryCollection":
        for child in geometry.get("geometries", []):
            yield from _coordinates(child)
    else:
        raise ValueError(f"Unsupported GeoJSON geometry type: {kind!r}")


def validate_feature(feature: dict[str, Any]) -> None:
    geometry = feature.get("geometry")
    if not isinstance(geometry, dict):
        raise ValueError("Feature is missing geometry")
    if geometry.get("type") not in {"Polygon", "MultiPolygon"}:
        raise ValueError(f"Expected polygon geometry, received {geometry.get('type')!r}")
    points = list(_coordinates(geometry))
    if len(points) < 4:
        raise ValueError("Polygon has fewer than four coordinate positions")
    for point in points:
        if not isinstance(point, (list, tuple)) or len(point) < 2:
            raise ValueError("Invalid coordinate pair")
        lon, lat = float(point[0]), float(point[1])
        if not (-180 <= lon <= 180 and -90 <= lat <= 90):
            raise ValueError(f"Coordinate outside EPSG:4326 bounds: {point!r}")


def _request_page(session, layer_id, where, offset, page_size=PAGE_SIZE, service=SERVICE):
    url = f"{service}/{layer_id}/query"
    params = {
        "where": where, "outFields": "*", "returnGeometry": "true",
        "outSR": "4326", "f": "geojson", "resultOffset": offset,
        "resultRecordCount": page_size, "orderByFields": "OBJECTID ASC",
        "returnExceededLimitFeatures": "true",
    }
    response = session.get(url, params=params, timeout=TIMEOUT)
    response.raise_for_status()
    payload = response.json()
    if payload.get("error"):
        raise RuntimeError(f"ArcGIS layer {layer_id} error: {payload['error']}")
    if not isinstance(payload.get("features"), list):
        raise RuntimeError(f"ArcGIS layer {layer_id} response has no features array")
    return payload


def extract_layer(session, name, definition):
    layer_id = definition["id"]
    offset = 0
    features = []
    pages = 0
    while pages < MAX_PAGES:
        service = definition.get("service", SERVICE)
        payload = _request_page(session, layer_id, definition["where"], offset, service=service)
        page = payload["features"]
        for feature in page:
            validate_feature(feature)
        features.extend(page)
        pages += 1
        offset += len(page)
        if not page or (len(page) < PAGE_SIZE and not payload.get("exceededTransferLimit")):
            break
    else:
        raise RuntimeError(f"Layer {layer_id} exceeded {MAX_PAGES} page safety limit")

    raw_feature_count = len(features)
    filter_attribute = definition.get("filter_attribute")
    filter_contains = definition.get("filter_contains")
    if filter_attribute and filter_contains:
        needle = str(filter_contains).casefold()
        features = [
            feature for feature in features
            if needle in str((feature.get("properties") or {}).get(filter_attribute, "")).casefold()
        ]
    sources, classes = Counter(), Counter()
    bounds = [180.0, 90.0, -180.0, -90.0]
    for feature in features:
        props = feature.get("properties") or {}
        source = props.get("Source") or props.get("FIRST_Source") or props.get("NAME") or "unknown"
        habitat = next((props.get(key) for key in (
            "FIRST_ClassLv1", "FIRST_ClassLv2", "FIRST_ClassLv3",
            "FIRST_ClassLv4", "Legend"
        ) if props.get(key)), "unclassified")
        sources[str(source)] += 1
        classes[str(habitat)] += 1
        for lon, lat, *_ in _coordinates(feature["geometry"]):
            bounds[0] = min(bounds[0], float(lon))
            bounds[1] = min(bounds[1], float(lat))
            bounds[2] = max(bounds[2], float(lon))
            bounds[3] = max(bounds[3], float(lat))

    collection = {"type": "FeatureCollection", "name": name, "features": features}
    summary = {
        "layer_id": layer_id,
        "service_url": f"{service}/{layer_id}",
        "query_where": definition["where"],
        "client_filter": {"attribute": filter_attribute, "contains": filter_contains} if filter_attribute else None,
        "description": definition["description"],
        "output_crs": "EPSG:4326",
        "raw_feature_count": raw_feature_count,
        "feature_count": len(features),
        "pages": pages,
        "geometry_types": dict(Counter(f["geometry"]["type"] for f in features)),
        "source_counts": dict(sources),
        "habitat_class_counts": dict(classes),
        "bbox_wgs84": bounds if features else None,
        "validation": "all features passed polygon and coordinate checks",
    }
    return collection, summary


def run(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": "LUPITA-South-Florida-GIS-Audit/1.0"})
    layers = {}
    for name, definition in LAYERS.items():
        collection, summary = extract_layer(session, name, definition)
        (output_dir / f"{name}.geojson").write_text(
            json.dumps(collection, separators=(",", ":"), ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        layers[name] = summary
    report = {
        "report_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Research-only geometry extraction; not production model input.",
        "services": {"fwc_unified_reef_map": SERVICE, "fdep_aquatic_preserves": FDEP_SERVICE},
        "layers": layers,
        "limitations": [
            "Source-map footprints describe map coverage, not ecological bay boundaries.",
            "Benthic habitat polygons are not automatically flats, channels, or species suitability zones.",
            "The FDEP preserve polygon is an approximate GIS representation and must be reconciled with the statutory description.",
            "No inlet connectivity is inferred from proximity or names.",
            "Output is EPSG:4326; source service metadata reports WKID 6439.",
        ],
    }
    (output_dir / "summary.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts/biscayne-gis")
    args = parser.parse_args()
    try:
        report = run(Path(args.output_dir))
    except Exception as exc:
        print(f"GIS extraction failed: {exc}", file=sys.stderr)
        return 1
    for name, layer in report["layers"].items():
        print(f"{name}: {layer['feature_count']} features, {layer['pages']} pages")
        print(f"  sources: {layer['source_counts']}")
        print(f"  classes: {layer['habitat_class_counts']}")
        print(f"  bbox: {layer['bbox_wgs84']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
