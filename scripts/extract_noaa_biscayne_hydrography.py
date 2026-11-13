"""Research-only extraction of NOAA ENC hydrographic features near Biscayne Bay.

The Harbour ENC service is intended for GIS/research display, not navigation.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

SERVICE = "https://encdirect.noaa.gov/arcgis/rest/services/encdirect/enc_harbour/MapServer"
MARINE_TRANSPORTATION_SERVICE = (
    "https://encdirect.noaa.gov/arcgis/rest/services/"
    "NavigationChartData/MarineTransportation/MapServer"
)
BBOX = (-80.55, 25.20, -80.05, 26.10)
TIMEOUT = (15, 90)
PAGE_SIZE = 1000
MAX_PAGES = 100
LAYERS = {
    "coastal_maintained_channels": {
        "service": MARINE_TRANSPORTATION_SERVICE,
        "id": 1,
        "name": "Coastal Maintained Channels",
        "publisher": "NOAA Office of Coast Survey; source data copyright USACE",
        "description": "USACE-maintained and surveyed coastal channels and waterways.",
    },
    "harbor_coastline_lines": {
        "service": SERVICE,
        "id": 84,
        "name": "Harbor.Coastline_line",
        "publisher": "NOAA Office of Coast Survey",
        "description": "Chart-derived coastline linework from Harbour-scale ENC cells; source-chart positional quality and dates must be retained.",
    },
    "harbor_depth_contour_lines": {
        "service": SERVICE,
        "id": 104,
        "name": "Harbor.Depth_Contour_line",
        "publisher": "NOAA Office of Coast Survey",
        "description": "Charted depth-contour lines; retain sounding datum, contour value, source chart, and date; not a substitute for current survey soundings.",
    },
    "harbor_land_areas": {
        "service": SERVICE,
        "id": 233,
        "name": "Harbor.Land_Area",
        "publisher": "NOAA Office of Coast Survey",
        "description": "Charted land-area polygons used as shoreline-context geometry; not a legal cadastral or surveyed MHW boundary.",
    },
    "harbor_depth_areas": {
        "service": SERVICE,
        "id": 227,
        "name": "Harbor.Depth_Area",
        "publisher": "NOAA Office of Coast Survey",
        "description": "Charted depth-area polygons; preserve depth range and vertical datum attributes and do not infer current controlling depths.",
    },
    "harbor_unsurveyed_areas": {
        "service": SERVICE,
        "id": 230,
        "name": "Harbor.Unsurveyed_Area",
        "publisher": "NOAA Office of Coast Survey",
        "description": "Charted unsurveyed-area polygons; explicit data-quality context, not evidence of zero depth or absent water.",
    },
    "harbor_seabed_areas": {
        "service": SERVICE,
        "id": 200,
        "name": "Harbor.Seabed_Area",
        "publisher": "NOAA Office of Coast Survey",
        "description": "Charted seabed classification polygons; retain source category and date and do not treat as current biological habitat verification.",
    },
    "harbor_vegetation_areas": {
        "service": SERVICE,
        "id": 239,
        "name": "Harbor.Vegetation_area",
        "publisher": "NOAA Office of Coast Survey",
        "description": "Charted vegetation polygons; source-chart observations only, not current seagrass or habitat ground-truth.",
    },
    "harbor_named_water_area_points": {
        "service": SERVICE,
        "id": 41,
        "name": "Harbor.Sea_Area_Named_Water_Area_point",
        "publisher": "NOAA Office of Coast Survey",
        "description": "Point features labeling named water areas in large-scale Harbour ENC compilation; labels only, not boundary geometry.",
    },
    "harbor_navigation_lines": {
        "service": SERVICE,
        "id": 132,
        "name": "Harbor.Navigation_Line",
        "publisher": "NOAA Office of Coast Survey",
        "description": "Charted navigation-line features in large-scale Harbour ENC compilation; not necessarily channel centerlines.",
    },
    "harbor_dredged_areas": {
        "service": SERVICE,
        "id": 228,
        "name": "Harbor.Dredged_Area",
        "publisher": "NOAA Office of Coast Survey",
        "description": "Dredged-area polygons in large-scale Harbour ENC compilation.",
    },
    "harbor_named_water_areas": {
        "service": SERVICE,
        "id": 237,
        "name": "Harbor.Sea_Area_Named_Water_Area",
        "publisher": "NOAA Office of Coast Survey",
        "description": "Named water-area polygons in large-scale Harbour ENC compilation.",
    },
    "harbor_canal_areas": {
        "service": SERVICE,
        "id": 170,
        "name": "Harbor.Canal_area",
        "publisher": "NOAA Office of Coast Survey",
        "description": "Canal-area polygons in large-scale Harbour ENC compilation.",
    },
    "harbor_tideway_areas": {
        "service": SERVICE,
        "id": 205,
        "name": "Harbor.Tideway_area",
        "publisher": "NOAA Office of Coast Survey",
        "description": "Tideway-area polygons in large-scale Harbour ENC compilation.",
    },
    "harbor_fairway_areas": {
        "service": SERVICE,
        "id": 208,
        "name": "Harbor.Fairway_area",
        "publisher": "NOAA Office of Coast Survey",
        "description": "Charted fairway polygons; navigation-route context only, not ecological corridors or habitat.",
    },
    "harbor_deep_water_route_areas": {
        "service": SERVICE,
        "id": 207,
        "name": "Harbor.Deep_Water_Route_Part_area",
        "publisher": "NOAA Office of Coast Survey",
        "description": "Charted deep-water route polygons; navigation context only, not ecological corridors or current depth guarantees.",
    },
    "harbor_two_way_route_areas": {
        "service": SERVICE,
        "id": 216,
        "name": "Harbor.Two_Way_Route_Part_area",
        "publisher": "NOAA Office of Coast Survey",
        "description": "Charted two-way route polygons; navigation context only, not ecological connectivity.",
    },
    "harbor_recommended_route_centerlines": {
        "service": SERVICE,
        "id": 133,
        "name": "Harbor.Recommended_Route_Centerline_line",
        "publisher": "NOAA Office of Coast Survey",
        "description": "Charted recommended-route centerlines; navigation route geometry, not channel or fish-movement centerlines.",
    },
}


def iter_positions(geometry: dict[str, Any]):
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
            yield from iter_positions(child)
    else:
        raise ValueError(f"Unsupported geometry type: {kind!r}")


def validate_feature(feature: dict[str, Any]) -> None:
    geometry = feature.get("geometry")
    if not isinstance(geometry, dict):
        raise ValueError("Feature has no geometry")
    if geometry.get("type") not in {"Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon"}:
        raise ValueError(f"Unsupported NOAA geometry type: {geometry.get('type')!r}")
    positions = list(iter_positions(geometry))
    if not positions:
        raise ValueError("Feature has empty coordinates")
    for position in positions:
        if not isinstance(position, (list, tuple)) or len(position) < 2:
            raise ValueError(f"Invalid coordinate position: {position!r}")
        lon, lat = float(position[0]), float(position[1])
        if not (-180 <= lon <= 180 and -90 <= lat <= 90):
            raise ValueError(f"Coordinate outside EPSG:4326 bounds: {position!r}")


def fetch_layer(session: requests.Session, definition: dict[str, Any]):
    service = definition["service"]
    layer_id = definition["id"]
    url = f"{service}/{layer_id}/query"
    xmin, ymin, xmax, ymax = BBOX
    params = {
        "where": "1=1",
        "geometry": f"{xmin},{ymin},{xmax},{ymax}",
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "*",
        "returnGeometry": "true",
        "outSR": "4326",
        "returnZ": "false",
        "returnM": "false",
        "resultOffset": 0,
        "resultRecordCount": PAGE_SIZE,
        "orderByFields": "OBJECTID ASC",
        "returnExceededLimitFeatures": "true",
        "f": "geojson",
    }
    features = []
    pages = 0
    while pages < MAX_PAGES:
        response = None
        for attempt in range(3):
            response = session.get(url, params=params, timeout=TIMEOUT)
            if response.status_code in {429, 500, 502, 503, 504} and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            break
        response.raise_for_status()
        payload = response.json()
        if payload.get("error"):
            raise RuntimeError(f"NOAA ArcGIS layer {layer_id} error: {payload['error']}")
        page = payload.get("features")
        if not isinstance(page, list):
            raise RuntimeError(f"NOAA layer {layer_id} response has no features array")
        for feature in page:
            validate_feature(feature)
        features.extend(page)
        pages += 1
        params["resultOffset"] += len(page)
        if not page or (len(page) < PAGE_SIZE and not payload.get("exceededTransferLimit")):
            break
    else:
        raise RuntimeError(f"NOAA layer {layer_id} exceeded {MAX_PAGES} page safety limit")

    names, geometry_types = Counter(), Counter()
    bounds = [180.0, 90.0, -180.0, -90.0]
    for feature in features:
        props = feature.get("properties") or {}
        name = props.get("OBJNAM") or props.get("FAIRWAY") or props.get("CATSEA") or "unnamed"
        names[str(name)] += 1
        geometry_types[feature["geometry"]["type"]] += 1
        for lon, lat, *_ in iter_positions(feature["geometry"]):
            bounds[0] = min(bounds[0], float(lon))
            bounds[1] = min(bounds[1], float(lat))
            bounds[2] = max(bounds[2], float(lon))
            bounds[3] = max(bounds[3], float(lat))

    collection = {
        "type": "FeatureCollection",
        "name": f"noaa_{definition['name'].lower().replace('.', '_').replace(' ', '_')}",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": features,
    }
    summary = {
        "source": "NOAA ENC Direct to GIS",
        "service_url": service,
        "layer_id": layer_id,
        "layer_name": definition["name"],
        "publisher": definition["publisher"],
        "source_description": definition["description"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "query_bbox_wgs84": list(BBOX),
        "output_crs": "EPSG:4326",
        "feature_count": len(features),
        "pages": pages,
        "geometry_types": dict(geometry_types),
        "feature_name_counts": dict(names),
        "result_bbox_wgs84": bounds if features else None,
        "validation": "all returned geometries and coordinates passed validation",
    }
    return collection, summary


def fetch_channels(session: requests.Session):
    """Backward-compatible helper for the maintained-channel theme layer."""
    return fetch_layer(session, LAYERS["coastal_maintained_channels"])


def run(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": "LUPITA-South-Florida-Hydrography-Audit/1.0"})
    summaries, errors = {}, {}
    for key, definition in LAYERS.items():
        try:
            collection, summary = fetch_layer(session, definition)
            (output_dir / f"{key}.geojson").write_text(
                json.dumps(collection, separators=(",", ":"), ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            summaries[key] = summary
        except Exception as exc:
            errors[key] = f"{type(exc).__name__}: {exc}"
            print(f"WARNING: NOAA layer {key} unavailable: {errors[key]}", file=sys.stderr)
    report = {
        "report_version": 2,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Research-only hydrographic geometry extraction; not production model input or navigation data.",
        "status": "degraded" if errors else "healthy",
        "layer_errors": errors,
        "query_bbox_wgs84": list(BBOX),
        "output_crs": "EPSG:4326",
        "layers": summaries,
        "limitations": [
            "NOAA ENC Direct to GIS is not certified for navigation.",
            "The maintained-channel theme layer contains only USACE-maintained/surveyed coastal channels, not every inlet or tidal pass.",
            "ENC hydrographic objects are chart features; their presence does not establish ecological connectivity or fish movement.",
            "No Government Cut or Bear Cut identity is assigned unless source attributes and geometry support it.",
            "Named water-area polygons may not represent a complete bay or inlet boundary.",
            "Named water-area point features are label anchors only, not boundaries.",
            "Navigation lines are chart features and must not be treated as ecological corridors without independent evidence.",
            "Coastline linework and land-area polygons are chart-derived context, not surveyed legal or MHW boundaries.",
            "Depth contours, depth areas, and unsurveyed areas retain their chart attributes and vertical datum; they are not current navigation assurances.",
            "Seabed and vegetation classes are charted observations and require independent current habitat validation.",
            "The Harbour service is updated weekly and reflects the scale band of its source ENC cells.",
        ],
    }
    (output_dir / "noaa_hydrography_summary.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts/noaa-hydrography")
    args = parser.parse_args()
    try:
        report = run(Path(args.output_dir))
    except Exception as exc:
        print(f"NOAA hydrography extraction failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    for key, summary in report["layers"].items():
        print(f"{key}: {summary['feature_count']} features; {summary['feature_name_counts']}")
    if report["layer_errors"]:
        print(f"Completed with optional layer errors: {report['layer_errors']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
