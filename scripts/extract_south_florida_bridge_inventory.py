"""Extract official South Florida bridge inventory geometry for research crosswalks.

This is transportation infrastructure context only. It is not a bay boundary,
navigation channel, ecological connectivity layer, or production model input.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

BBOX = (-80.55, 25.20, -80.05, 26.10)
TIMEOUT = (15, 90)
SOURCES = {
    "miamidade_dtpw_bridge_lines": {
        "service": "https://gisweb.miamidade.gov/arcgis/rest/services/EAMS/EAMS_Map/MapServer",
        "layer_id": 1,
        "layer_name": "Miami-Dade DTPWBridge",
        "publisher": "Miami-Dade County Department of Transportation and Public Works",
        "description": (
            "County-maintained bridge polylines from the DTPW EAMS GIS view. "
            "Source feature class is updated as needed by DTPW. Infrastructure reference only."
        ),
    },
    "fdot_rci_bridge_lines": {
        "service": "https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer",
        "layer_id": 1,
        "layer_name": "FDOT Roadway Characteristics Inventory Bridges",
        "publisher": "Florida Department of Transportation, Transportation Data and Analytics Office",
        "description": (
            "Bridge polylines derived from FDOT RCI Feature 258 / BRIDGENO event mapping. "
            "Inventory geometry may not reflect current conditions. Infrastructure reference only."
        ),
    },
}


def validate_feature(feature: dict[str, Any]) -> None:
    geometry = feature.get("geometry")
    if not isinstance(geometry, dict) or geometry.get("type") not in {
        "Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon"
    }:
        raise ValueError("Feature has missing or unsupported geometry")
    coordinates = geometry.get("coordinates")
    if not coordinates:
        raise ValueError("Feature has empty coordinates")

    def walk(value):
        if isinstance(value, (list, tuple)) and len(value) >= 2 and all(
            isinstance(v, (int, float)) for v in value[:2]
        ):
            lon, lat = float(value[0]), float(value[1])
            if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                raise ValueError(f"Coordinate outside EPSG:4326 bounds: {value!r}")
            return
        if isinstance(value, (list, tuple)):
            for child in value:
                walk(child)
        else:
            raise ValueError(f"Invalid coordinate structure: {value!r}")

    walk(coordinates)


def fetch_source(session: requests.Session, definition: dict[str, Any]):
    url = f"{definition['service']}/{definition['layer_id']}/query"
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
        "resultRecordCount": 1000,
        "orderByFields": "OBJECTID ASC",
        "f": "geojson",
    }
    response = session.get(url, params=params, timeout=TIMEOUT)
    response.raise_for_status()
    payload = response.json()
    if payload.get("error"):
        raise RuntimeError(f"ArcGIS layer error: {payload['error']}")
    features = payload.get("features")
    if not isinstance(features, list):
        raise RuntimeError("ArcGIS response has no features array")
    if payload.get("exceededTransferLimit"):
        raise RuntimeError("Bridge query exceeded transfer limit; pagination is required")
    for feature in features:
        validate_feature(feature)

    collection = {
        "type": "FeatureCollection",
        "name": definition["layer_name"].lower().replace(" ", "_"),
        "features": features,
    }
    summary = {
        "source": definition["publisher"],
        "service_url": definition["service"],
        "layer_id": definition["layer_id"],
        "layer_name": definition["layer_name"],
        "source_description": definition["description"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "query_bbox_wgs84": list(BBOX),
        "output_crs": "EPSG:4326",
        "feature_count": len(features),
        "geometry_types": sorted({f["geometry"]["type"] for f in features}),
        "validation": "all returned geometries and coordinates passed validation",
    }
    return collection, summary


def run(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": "LUPITA-South-Florida-Bridge-Crosswalk/1.0"})
    summaries, errors = {}, {}
    for key, definition in SOURCES.items():
        try:
            collection, summary = fetch_source(session, definition)
            (output_dir / f"{key}.geojson").write_text(
                json.dumps(collection, separators=(",", ":"), ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            summaries[key] = summary
        except Exception as exc:
            errors[key] = f"{type(exc).__name__}: {exc}"
    report = {
        "report_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Research-only transportation infrastructure crosswalk; not ecological or navigation geometry.",
        "status": "degraded" if errors else "healthy",
        "query_bbox_wgs84": list(BBOX),
        "output_crs": "EPSG:4326",
        "sources": summaries,
        "errors": errors,
        "limitations": [
            "Bridge inventory features describe transportation structures, not ecological boundaries.",
            "Inventory and chart source dates must be retained; service refresh does not guarantee current field verification.",
            "No bridge geometry is extended or snapped to create a cross-bay boundary.",
        ],
    }
    (output_dir / "bridge_inventory_summary.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if errors:
        raise RuntimeError(f"One or more bridge inventory sources failed: {errors}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/bridge-inventory"))
    args = parser.parse_args()
    report = run(args.output_dir)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
