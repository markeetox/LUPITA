"""Research-only extraction of Florida shoreline comparison layers.

The Florida DEP service republishes NOAA-derived MHW composite shoreline and
NOAA MHHW screening linework. Original source records and Biscayne-area clipped
copies are kept separately; no final bay boundary is inferred.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from shapely.geometry import GeometryCollection, LineString, MultiLineString, box, mapping, shape

SERVICE = "https://ca.dep.state.fl.us/arcgis/rest/services/Map_Direct/Program_Support/MapServer"
BBOX = (-80.45, 25.25, -80.05, 26.00)
BATCH_SIZE = 1
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
        "required": True,
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
        "required": False,
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


def esri_feature_to_geojson(feature: dict[str, Any]) -> dict[str, Any]:
    attributes = feature.get("attributes") or {}
    paths = (feature.get("geometry") or {}).get("paths") or []
    if not paths:
        raise ValueError("ArcGIS JSON feature has no polyline paths")
    geometry = {
        "type": "LineString" if len(paths) == 1 else "MultiLineString",
        "coordinates": paths[0] if len(paths) == 1 else paths,
    }
    converted = {
        "type": "Feature",
        "id": attributes.get("OBJECTID"),
        "properties": attributes,
        "geometry": geometry,
    }
    validate_geojson_feature(converted)
    return converted


def clip_line_geometry(geometry: dict[str, Any], aoi):
    clipped = shape(geometry).intersection(aoi)

    def collect_lines(item):
        if item.is_empty:
            return []
        if item.geom_type == "LineString":
            return [item]
        if item.geom_type == "MultiLineString":
            return list(item.geoms)
        if item.geom_type == "GeometryCollection":
            return [line for child in item.geoms for line in collect_lines(child)]
        return []

    lines = collect_lines(clipped)
    if not lines:
        return None
    if len(lines) == 1:
        return mapping(lines[0])
    return mapping(MultiLineString(lines))


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

    source_features = []
    failed_object_ids = []
    for object_id in object_ids:
        params = {
            "objectIds": str(object_id),
            "outFields": "*",
            "returnGeometry": "true",
            "outSR": 4326,
            "f": "geojson",
        }
        response = session.get(query_url, params=params, timeout=TIMEOUT)
        try:
            response.raise_for_status()
            payload = response.json()
            if payload.get("error"):
                raise RuntimeError(str(payload["error"]))
            page = payload.get("features")
            if not isinstance(page, list):
                raise RuntimeError("GeoJSON response has no features array")
            converted = page
        except Exception as geojson_error:
            # Some ArcGIS map services fail GeoJSON serialization for specific
            # features; retry that single object in native ArcGIS JSON format.
            fallback_params = {**params, "f": "json"}
            fallback = session.get(query_url, params=fallback_params, timeout=TIMEOUT)
            try:
                fallback.raise_for_status()
                fallback_payload = fallback.json()
                if fallback_payload.get("error"):
                    raise RuntimeError(str(fallback_payload["error"]))
                converted = [
                    esri_feature_to_geojson(item)
                    for item in fallback_payload.get("features", [])
                ]
            except Exception as fallback_error:
                if definition["required"]:
                    raise RuntimeError(
                        f"Required layer {definition['id']} object {object_id} failed "
                        f"GeoJSON and ArcGIS JSON retrieval: {geojson_error}; {fallback_error}"
                    ) from fallback_error
                failed_object_ids.append({
                    "object_id": object_id,
                    "geojson_error": str(geojson_error),
                    "fallback_error": str(fallback_error),
                })
                continue
        for feature in converted:
            validate_geojson_feature(feature)
        source_features.extend(converted)

    raw_collection = {
        "type": "FeatureCollection",
        "name": f"{definition['name'].replace(' ', '_')}_source_raw",
        "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
        "features": source_features,
    }
    raw_file = f"{Path(definition['output_file']).stem}_source_raw.geojson"
    (output_dir / raw_file).write_text(
        json.dumps(raw_collection, separators=(",", ":")) + "\n", encoding="utf-8"
    )

    aoi = box(xmin, ymin, xmax, ymax)
    clipped_features = []
    for feature in source_features:
        clipped_geometry = clip_line_geometry(feature["geometry"], aoi)
        if clipped_geometry is None:
            continue
        properties = dict(feature.get("properties") or {})
        properties["LUPITA_SOURCE_OBJECTID"] = (
            feature.get("id") or properties.get("OBJECTID")
        )
        properties["LUPITA_SOURCE_LAYER_ID"] = definition["id"]
        properties["LUPITA_CLIP_BBOX_WGS84"] = json.dumps(list(BBOX))
        clipped = {
            "type": "Feature",
            "id": feature.get("id"),
            "properties": properties,
            "geometry": clipped_geometry,
        }
        validate_geojson_feature(clipped)
        clipped_features.append(clipped)

    clipped_collection = {
        "type": "FeatureCollection",
        "name": f"{definition['name'].replace(' ', '_')}_biscayne_bbox_clip",
        "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
        "features": clipped_features,
    }
    (output_dir / definition["output_file"]).write_text(
        json.dumps(clipped_collection, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    field_name = "F_NAME" if "F_NAME" in {
        field.get("name") for field in metadata.get("fields", [])
    } else "OBJECTID"
    attribute_counts: dict[str, int] = {}
    for feature in source_features:
        value = str((feature.get("properties") or {}).get(field_name) or "unknown")
        attribute_counts[value] = attribute_counts.get(value, 0) + 1

    summary = {
        "layer_id": definition["id"],
        "layer_name": metadata.get("name"),
        "datum_or_product": definition["datum"],
        "source_object_id_count": len(object_ids),
        "source_feature_count_retrieved": len(source_features),
        "source_feature_count_failed": len(failed_object_ids),
        "failed_object_ids": failed_object_ids,
        "clipped_feature_count": len(clipped_features),
        "geometry_types": sorted({
            feature["geometry"]["type"] for feature in clipped_features
        }),
        "attribute_field": field_name,
        "source_attribute_counts": attribute_counts,
        "bbox_wgs84": list(BBOX),
        "output_crs": "EPSG:4326",
        "source_spatial_reference": metadata.get("extent", {}).get("spatialReference"),
        "source_extent": metadata.get("extent"),
        "max_record_count": metadata.get("maxRecordCount"),
        "raw_source_file": raw_file,
        "clipped_output_file": definition["output_file"],
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
    layer_errors = {}
    for key, definition in LAYERS.items():
        try:
            metadata, summary = fetch_layer(session, definition, output_dir)
            (output_dir / f"{key}_metadata.json").write_text(
                json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
            )
            summaries[key] = summary
        except Exception as exc:
            if definition["required"]:
                raise
            layer_errors[key] = f"{type(exc).__name__}: {exc}"

    status = "complete" if not layer_errors and not any(
        value["source_feature_count_failed"] for value in summaries.values()
    ) else "partial_optional_layer_or_feature_failures"
    report = {
        "audit_version": 4,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "service": SERVICE,
        "query_bbox_wgs84": list(BBOX),
        "shoreline_layers": summaries,
        "optional_layer_errors": layer_errors,
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
        "status": report["status"],
        "layers": {
            key: {
                "source_feature_count": value["source_feature_count_retrieved"],
                "clipped_feature_count": value["clipped_feature_count"],
                "failed_source_features": value["source_feature_count_failed"],
                "output_file": value["clipped_output_file"],
            }
            for key, value in report["shoreline_layers"].items()
        },
        "optional_layer_errors": report["optional_layer_errors"],
        "output_dir": str(args.output_dir),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
