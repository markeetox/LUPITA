"""Research-only inventory of NOAA NGS shoreline web services.

This first pass discovers published WFS/WMS layers and records authoritative
project metadata. It does not infer shoreline geometry or alter production data.
"""
from __future__ import annotations

import argparse
import json
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

ARCGIS_CUSP_LAYER = "https://services.arcgis.com/rD2ylXRs80UroD90/ArcGIS/rest/services/NOAA_Coastal_Shoreline/FeatureServer/0"
BBOX = (-80.45, 25.25, -80.05, 26.00)
BATCH_SIZE = 500
TIMEOUT = (15, 90)
PROJECTS = [
    {
        "project_id": "FL1808C-TB-N",
        "inport_id": 73241,
        "name": "Biscayne Bay, Rickenbacker Island to Snapper Creek Canal",
        "imagery_or_lidar_dates": "2018-07-26 to 2019-04-13",
        "reported_mhw_accuracy_95pct_m": 2.3,
        "reported_mllw_accuracy_95pct_m": 3.0,
        "inport_url": "https://www.fisheries.noaa.gov/inport/item/73241",
        "completion_report": "https://www.ngs.noaa.gov/desc_reports/FL1808C-TB-N.PDF",
        "geographic_extent_wgs84": [-80.3095, 25.63448867, -80.16894, 25.77293],
        "status": "project_metadata_verified_vectors_not_yet_retrieved",
    },
    {
        "project_id": "FL1808A-TB-N",
        "inport_id": 74866,
        "name": "Biscayne Bay, Fender Point to Card Sound",
        "imagery_or_lidar_dates": "2018-07-26 to 2019-04-16",
        "reported_mhw_accuracy_95pct_m": 2.3,
        "reported_mllw_accuracy_95pct_m": 3.0,
        "inport_url": "https://www.fisheries.noaa.gov/inport/item/74866",
        "completion_report": "https://www.ngs.noaa.gov/desc_reports/FL1808A-TB-N.pdf",
        "geographic_extent_wgs84": [-80.40325, 25.32522995, -80.21719, 25.51193995],
        "status": "project_metadata_verified_vectors_not_yet_retrieved",
    },
    {
        "project_id": "FL2317-CS-N",
        "inport_id": 76789,
        "name": "Port of Miami",
        "imagery_or_lidar_dates": "2023-10-21",
        "reported_horizontal_accuracy_95pct_m": 1.2,
        "inport_url": "https://www.fisheries.noaa.gov/inport/item/76789",
        "completion_report": "https://www.ngs.noaa.gov/desc_reports/FL2317-CS-N.pdf",
        "geographic_extent_wgs84": [-80.2157448, 25.73422824, -80.1074168, 25.81199791],
        "status": "newer_port_of_miami_shoreline_candidate_vectors_not_yet_retrieved",
    },
    {
        "project_id": "FL0413",
        "inport_id": 61412,
        "name": "Port of Miami",
        "imagery_or_lidar_dates": "2005-02",
        "inport_url": "https://www.fisheries.noaa.gov/inport/item/61412",
        "geographic_extent_wgs84": [-80.336873, 25.5093105, -80.1019091, 25.9546342],
        "status": "older_port_of_miami_comparison_candidate",
    },
    {
        "project_id": "FL1603A-CM-N",
        "inport_id": 61478,
        "name": "Convoy Point",
        "imagery_or_lidar_dates": "2017-03-19",
        "inport_url": "https://www.fisheries.noaa.gov/inport/item/61478",
        "completion_report": "https://www.ngs.noaa.gov/desc_reports/FL1603A-CM-N.PDF",
        "status": "local_comparison_candidate_vectors_not_yet_retrieved",
    },
]

KEYWORDS = ("shoreline", "cusp", "national", "mhw", "mllw", "coastal")
def is_candidate(layer: dict[str, str]) -> bool:
    text = " ".join(layer.values()).lower()
    return any(word in text for word in KEYWORDS)


def validate_geojson_feature(feature: dict[str, Any]) -> None:
    geometry = feature.get("geometry")
    if not isinstance(geometry, dict) or geometry.get("type") not in {
        "LineString", "MultiLineString"
    }:
        raise ValueError(f"Expected shoreline line geometry, got {geometry!r}")
    coords = geometry.get("coordinates") or []
    positions = coords if geometry["type"] == "LineString" else [
        point for part in coords for point in part
    ]
    if not positions:
        raise ValueError("Shoreline feature has empty coordinates")
    for position in positions:
        if len(position) < 2:
            raise ValueError(f"Invalid coordinate position: {position!r}")
        lon, lat = float(position[0]), float(position[1])
        if not (-180 <= lon <= 180 and -90 <= lat <= 90):
            raise ValueError(f"Coordinate outside EPSG:4326 bounds: {position!r}")


def fetch_cusp_shoreline(
    session: requests.Session, output_dir: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    metadata_response = session.get(
        ARCGIS_CUSP_LAYER, params={"f": "pjson"}, timeout=TIMEOUT
    )
    metadata_response.raise_for_status()
    metadata = metadata_response.json()
    if metadata.get("error"):
        raise RuntimeError(f"NOAA CUSP layer metadata error: {metadata['error']}")
    if metadata.get("geometryType") != "esriGeometryPolyline":
        raise RuntimeError(
            f"NOAA CUSP layer is not a polyline layer: {metadata.get('geometryType')!r}"
        )

    xmin, ymin, xmax, ymax = BBOX
    query_url = f"{ARCGIS_CUSP_LAYER}/query"
    id_params = {
        "where": "1=1",
        "geometry": f"{xmin},{ymin},{xmax},{ymax}",
        "geometryType": "esriGeometryEnvelope",
        "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects",
        "returnIdsOnly": "true",
        "f": "json",
    }
    ids_response = session.get(query_url, params=id_params, timeout=TIMEOUT)
    ids_response.raise_for_status()
    ids_payload = ids_response.json()
    if ids_payload.get("error"):
        raise RuntimeError(f"NOAA CUSP object-ID query error: {ids_payload['error']}")
    object_ids = sorted(ids_payload.get("objectIds") or [])
    features = []

    for offset in range(0, len(object_ids), BATCH_SIZE):
        batch = object_ids[offset : offset + BATCH_SIZE]
        params = {
            "objectIds": ",".join(str(value) for value in batch),
            "outFields": "*",
            "returnGeometry": "true",
            "outSR": 4326,
            "f": "geojson",
        }
        response = session.get(query_url, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        payload = response.json()
        if payload.get("error"):
            raise RuntimeError(f"NOAA CUSP feature query error: {payload['error']}")
        page = payload.get("features")
        if not isinstance(page, list):
            raise RuntimeError("NOAA CUSP feature response has no GeoJSON features array")
        for feature in page:
            validate_geojson_feature(feature)
        features.extend(page)

    if len(features) != len(object_ids):
        raise RuntimeError(
            f"NOAA CUSP returned {len(features)} features for {len(object_ids)} object IDs"
        )

    collection = {
        "type": "FeatureCollection",
        "name": "NOAA_CUSP_Biscayne_review_bbox",
        "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
        "features": features,
    }
    (output_dir / "noaa_cusp_biscayne_shoreline.geojson").write_text(
        json.dumps(collection, separators=(",", ":")) + "\\n", encoding="utf-8"
    )

    source_counts: dict[str, int] = {}
    date_counts: dict[str, int] = {}
    attribute_counts: dict[str, int] = {}
    for feature in features:
        props = feature.get("properties") or {}
        for counter, field in (
            (source_counts, "SOURCE_ID"),
            (date_counts, "SRC_DATE"),
            (attribute_counts, "ATTRIBUTE"),
        ):
            value = str(props.get(field) or "unknown")
            counter[value] = counter.get(value, 0) + 1

    summary = {
        "feature_count": len(features),
        "object_id_count": len(object_ids),
        "geometry_types": sorted({
            feature["geometry"]["type"] for feature in features
        }),
        "source_id_counts": source_counts,
        "source_date_counts": date_counts,
        "attribute_counts": attribute_counts,
        "bbox_wgs84": list(BBOX),
        "output_crs": "EPSG:4326",
        "source_fields": [field.get("name") for field in metadata.get("fields", [])],
        "service_last_edit_date": metadata.get("editingInfo", {}).get("lastEditDate"),
        "service_max_record_count": metadata.get("maxRecordCount"),
    }
    return metadata, summary


def run_audit(output_dir: Path, session: requests.Session | None = None) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    session = session or requests.Session()
    session.headers.update({"User-Agent": "LUPITA-research-shoreline-audit/1.0 (research-only)"})

    cusp_metadata, cusp_summary = fetch_cusp_shoreline(session, output_dir)
    (output_dir / "noaa_cusp_layer_metadata.json").write_text(
        json.dumps(cusp_metadata, indent=2) + "\\n", encoding="utf-8"
    )

    report = {
        "audit_version": 2,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "cusp_comparison_geometry_retrieved",
        "purpose": "Retrieve NOAA CUSP shoreline comparison geometry and preserve its source attribution before project-specific shoreline vector acquisition.",
        "cusp": {
            "layer_url": ARCGIS_CUSP_LAYER,
            "service_item_id": "b5a2dc47497642029c2e387119f691ad",
            "layer_name": cusp_metadata.get("name"),
            "geometry_type": cusp_metadata.get("geometryType"),
            "description": "NOAA Continually Updated Shoreline Product. Mean-high-water proxy shoreline; not equivalent to project-specific MHW and MLLW vectors.",
            **cusp_summary,
            "geojson_file": "noaa_cusp_biscayne_shoreline.geojson",
        },
        "project_metadata_candidates": PROJECTS,
        "legacy_wfs_probe": {
            "endpoint": "https://geodesy.noaa.gov/GeoServer/NSDE/ows",
            "status": "http_404_from_github_actions_runner",
            "interpretation": "Historical WFS endpoint documented in older NGS materials was unavailable from this runner; do not assume it is a current vector-download endpoint.",
        },
        "limitations": [
            "CUSP is a mean-high-water proxy and is not interchangeable with project-specific MHW and MLLW vectors.",
            "CUSP is a comparison source with less stringent acquisition and QC than project-based National Shoreline products.",
            "CUSP source attribution must be inspected before assigning features to FL1808A, FL1808C, or FL2317 projects.",
            "A source-date field is not necessarily the date the CUSP service was last updated.",
            "Project metadata rectangles are not proof of complete surveyed coverage.",
            "No final Biscayne Bay boundary is created by this audit.",
            "NOAA shoreline products are not navigation products or legal survey boundaries.",
        ],
    }
    (output_dir / "noaa_nsde_shoreline_service_inventory.json").write_text(
        json.dumps(report, indent=2) + "\\n", encoding="utf-8"
    )
    return report
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/noaa-shoreline"))
    args = parser.parse_args()
    report = run_audit(args.output_dir)
    print(json.dumps({
        "cusp_feature_count": report["cusp"]["feature_count"],
        "source_ids": report["cusp"]["source_id_counts"],
        "source_dates": report["cusp"]["source_date_counts"],
        "output_dir": str(args.output_dir),
    }, indent=2))
    return 0

