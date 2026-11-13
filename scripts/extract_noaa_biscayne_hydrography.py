"""Research-only extraction of NOAA coastal maintained channel geometries near Biscayne Bay.

This NOAA theme layer represents USACE-maintained/surveyed coastal channels. It is
not a complete inventory of tidal inlets, and it is not certified for navigation.
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

SERVICE = (
    "https://encdirect.noaa.gov/arcgis/rest/services/"
    "NavigationChartData/MarineTransportation/MapServer"
)
LAYER_ID = 1
BBOX = (-80.55, 25.20, -80.05, 26.10)
TIMEOUT = (15, 90)
GEOMETRY_TYPES = {"Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon"}


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
    if geometry.get("type") not in GEOMETRY_TYPES:
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


def fetch_channels(session: requests.Session) -> tuple[dict[str, Any], dict[str, Any]]:
    url = f"{SERVICE}/{LAYER_ID}/query"
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
        "f": "geojson",
    }
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
        raise RuntimeError(f"NOAA ArcGIS query error: {payload['error']}")
    features = payload.get("features")
    if not isinstance(features, list):
        raise RuntimeError("NOAA response does not contain a GeoJSON features array")
    for feature in features:
        validate_feature(feature)

    names = Counter()
    geometry_types = Counter()
    bounds = [180.0, 90.0, -180.0, -90.0]
    for feature in features:
        props = feature.get("properties") or {}
        name = props.get("OBJNAM") or props.get("FAIRWAY") or "unnamed"
        names[str(name)] += 1
        geometry_types[feature["geometry"]["type"]] += 1
        for lon, lat, *_ in iter_positions(feature["geometry"]):
            bounds[0] = min(bounds[0], float(lon))
            bounds[1] = min(bounds[1], float(lat))
            bounds[2] = max(bounds[2], float(lon))
            bounds[3] = max(bounds[3], float(lat))

    collection = {
        "type": "FeatureCollection",
        "name": "noaa_coastal_maintained_channels_biscayne_aoi",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": features,
    }
    summary = {
        "source": "NOAA ENC Direct to GIS, NavigationChartData/MarineTransportation",
        "service_url": SERVICE,
        "layer_id": LAYER_ID,
        "layer_name": "Coastal Maintained Channels",
        "publisher": "NOAA Office of Coast Survey; source data copyright USACE",
        "source_description": (
            "Coastal channels and waterways maintained and surveyed by USACE. "
            "For coastal/ocean use planning; not for navigation."
        ),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "query_bbox_wgs84": list(BBOX),
        "output_crs": "EPSG:4326",
        "feature_count": len(features),
        "geometry_types": dict(geometry_types),
        "feature_name_counts": dict(names),
        "result_bbox_wgs84": bounds if features else None,
        "validation": "all returned geometries and coordinates passed validation",
        "limitations": [
            "This layer contains only maintained/surveyed coastal channels, not every inlet, pass, creek, or tidal connection.",
            "The layer geometry is not certified for navigation and does not provide current controlling depths.",
            "A channel polygon does not by itself establish ecological connectivity or fish movement.",
            "No Government Cut or Bear Cut identity is assigned unless the source attributes and geometry support it.",
        ],
    }
    return collection, summary


def run(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": "LUPITA-South-Florida-Hydrography-Audit/1.0"})
    collection, summary = fetch_channels(session)
    (output_dir / "noaa_coastal_maintained_channels.geojson").write_text(
        json.dumps(collection, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "noaa_channel_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts/noaa-hydrography")
    args = parser.parse_args()
    try:
        summary = run(Path(args.output_dir))
    except Exception as exc:
        print(f"NOAA hydrography extraction failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
