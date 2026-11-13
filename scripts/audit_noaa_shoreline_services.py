"""Research-only extraction of Florida shoreline comparison layers.

The Florida DEP service republishes NOAA-derived MHW composite shoreline and
NOAA MHHW screening linework. They are kept as separate source products and
are not treated as project-specific FL1808A/FL1808C vectors.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

SERVICE = "https://ca.dep.state.fl.us/arcgis/rest/services/Map_Direct/Program_Support/MapServer"
BBOX = (-80.45, 25.25, -80.05, 26.00)
BATCH_SIZE = 500
TIMEOUT = (15, 90)

LAYERS = {
    "noaa_composite_shoreline_mhw": {
        "id": 41,
        "name": "NOAA Composite Shoreline",
        "datum": "MHW",
        "geometry_type": "esriGeometryPolyline",
        "description": (
            "NOAA Office for Coastal Management composite shoreline derived from "
            "historic NOAA shoreline manuscripts (T-sheets); MHW shoreline context. "
            "Shoreline may have changed since the source surveys."
        ),
        "publisher": "NOAA Office for Coastal Management; hosted by Florida DEP",
        "output_file": "noaa_composite_shoreline_mhw_biscayne.geojson",
        "metadata_url": "https://ca.dep.state.fl.us/arcgis/rest/services/Map_Direct/Program_Support/MapServer/41",
    },
    "noaa_mhhw_screening_line": {
        "id": 40,
        "name": "NOAA Mean Higher High Water (MHHW)",
        "datum": "MHHW",
        "geometry_type": "esriGeometryPolyline",
        "description": (
            "NOAA Office for Coastal Management screening-level predicted MHHW "
            "extent derived from tidal and elevation data; not a surveyed MHW shoreline."
        ),
        "publisher": "NOAA Office for Coastal Management; hosted by Florida DEP",
        "output_file": "noaa_mhhw_screening_line_biscayne.geojson",
        "metadata_url": "https://ca.dep.state.fl.us/arcgis/rest/services/Map_Direct/Program_Support/MapServer/40",
    },
}

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


def fetch_layer(
    session: requests.Session, definition: dict[str, Any], output_dir: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    layer_url = f"{SERVICE}/{definition['id']}"
    metadata_response = session.get(
        layer_url, params={"f": "pjson"}, timeout=TIMEOUT
    )
    metadata_response.raise_for_status()
    metadata = metadata_response.json()
    if metadata.get("error"):
        raise RuntimeError(f"NOAA-derived layer metadata error: {metadata['error']}")
    if metadata.get("geometryType") != definition["geometry_type"]:
        raise RuntimeError(
            f"Unexpected geometry type for {definition['name']}: "
            f"{metadata.get('geometryType')!r}"
        )

    xmin, ymin, xmax, ymax = BBOX
    query_url = f"{layer_url}/query"
    id_params = {
        "where": "1=1",
        "geometry": json.dumps({
            "xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax,
            "spatialReference": {"wkid": 4326},
        }),
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
        raise RuntimeError(f"NOAA-derived layer ID query error: {ids_payload['error']}")
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
            raise RuntimeError(f"NOAA-derived feature query error: {payload['error']}")
        page = payload.get("features")
        if not isinstance(page, list):
            raise RuntimeError("NOAA-derived layer response has no GeoJSON features array")
        for feature in page:
            validate_geojson_feature(feature)
        features.extend(page)

    if len(features) != len(object_ids):
        raise RuntimeError(
            f"Layer {definition['id']} returned {len(features)} features "
            f"for {len(object_ids)} object IDs"
        )

    collection = {
        "type": "FeatureCollection",
        "name": definition["name"].replace(" ", "_"),
        "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
        "features": features,
    }
    (output_dir / definition["output_file"]).write_text(
        json.dumps(collection, separators=(",", ":")) + "\n", encoding="utf-8"
    )

    attribute_counts: dict[str, int] = {}
    field_name = "F_NAME" if "F_NAME" in {
        field.get("name") for field in metadata.get("fields", [])
    } else "OBJECTID"
    for feature in features:
        value = str((feature.get("properties") or {}).get(field_name) or "unknown")
        attribute_counts[value] = attribute_counts.get(value, 0) + 1

    summary = {
        "layer_id": definition["id"],
        "layer_name": metadata.get("name"),
        "datum_or_product": definition["datum"],
        "feature_count": len(features),
        "object_id_count": len(object_ids),
        "geometry_types": sorted({
            feature["geometry"]["type"] for feature in features
        }),
        "attribute_field": field_name,
        "attribute_counts": attribute_counts,
        "bbox_wgs84": list(BBOX),
        "output_crs": "EPSG:4326",
        "source_spatial_reference": metadata.get("extent", {}).get("spatialReference"),
        "source_extent": metadata.get("extent"),
        "max_record_count": metadata.get("maxRecordCount"),
        "output_file": definition["output_file"],
        "metadata_url": definition["metadata_url"],
        "description": definition["description"],
    }
    return metadata, summary


def run_audit(output_dir: Path, session: requests.Session | None = None) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    session = session or requests.Session()
    session.headers.update({
        "User-Agent": "LUPITA-research-shoreline-audit/1.0 (research-only)"
    })

    summaries = {}
    for key, definition in LAYERS.items():
        metadata, summary = fetch_layer(session, definition, output_dir)
        (output_dir / f"{key}_metadata.json").write_text(
            json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
        )
        summaries[key] = summary

    report = {
        "audit_version": 3,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "florida_noaa_shoreline_comparison_geometry_retrieved",
        "service": SERVICE,
        "query_bbox_wgs84": list(BBOX),
        "shoreline_layers": summaries,
        "project_metadata_candidates": PROJECTS,
        "rejected_cusp_candidate": {
            "url": "https://services.arcgis.com/rD2ylXRs80UroD90/ArcGIS/rest/services/NOAA_Coastal_Shoreline/FeatureServer/0",
            "declared_latest_wkid": 6416,
            "declared_crs_name": "NAD83(2011) / California zone 1 (ftUS)",
            "south_florida_query_feature_count": 0,
            "status": "not_used_spatial_reference_and_extent_not_compatible_with_south_florida_aoi",
        },
        "limitations": [
            "NOAA Composite Shoreline is derived from historic T-sheets and may not represent current shoreline position.",
            "NOAA MHHW is a screening-level predicted tidal extent, not the MHW shoreline and not a legal boundary.",
            "MHW and MHHW products are preserved as separate datums and must not be merged.",
            "Neither Florida comparison layer is a substitute for the FL1808A/FL1808C project-specific MHW and MLLW vectors.",
            "The NOAA Port of Miami FL2317 project remains the newer local project candidate; its actual vector download is still pending.",
            "Project metadata rectangles are not proof of complete surveyed coverage.",
            "No final Biscayne Bay boundary is created by this audit.",
            "These shoreline layers are not navigation products or legal survey boundaries.",
        ],
    }
    (output_dir / "noaa_nsde_shoreline_service_inventory.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/noaa-shoreline"))
    args = parser.parse_args()
    report = run_audit(args.output_dir)
    print(json.dumps({
        "layers": {
            key: {
                "feature_count": value["feature_count"],
                "attribute_counts": value["attribute_counts"],
                "output_file": value["output_file"],
            }
            for key, value in report["shoreline_layers"].items()
        },
        "output_dir": str(args.output_dir),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
