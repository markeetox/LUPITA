"""Detailed NOAA CMP MHW feature overlays against NOAA ENC and FDEP polygons.

Research-only. This audit does not construct a bay boundary, infer channels,
or change production scoring.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import requests
from pyproj import Transformer
from shapely.geometry import Point, shape
from shapely.ops import transform, unary_union

FDEP_LAYER = "https://ca.dep.state.fl.us/arcgis/rest/services/OpenData/AQUATIC_PRESERVES/MapServer/0"
PROJECT_IDS = ["FL1808A-TB-N", "FL1808C-TB-N", "FL2317-CS-N"]
PRESERVES = {
    43: "Biscayne Bay",
    25: "Biscayne Bay-Cape Florida to Monroe County Line",
}
TO_METRIC = Transformer.from_crs(4326, 26917, always_xy=True).transform


def fetch_fdep_preserves(session: requests.Session) -> tuple[dict, dict]:
    metadata_response = session.get(FDEP_LAYER, params={"f": "pjson"}, timeout=(15, 90))
    metadata_response.raise_for_status()
    metadata = metadata_response.json()
    response = session.get(
        f"{FDEP_LAYER}/query",
        params={
            "where": "OBJECTID IN (43,25)",
            "outFields": "*",
            "returnGeometry": "true",
            "outSR": 4326,
            "f": "geojson",
        },
        timeout=(15, 120),
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("error"):
        raise RuntimeError(f"FDEP preserve query failed: {payload['error']}")
    features = payload.get("features")
    if not isinstance(features, list):
        raise RuntimeError("FDEP preserve response did not contain GeoJSON features")
    by_id = {int(feature["properties"]["OBJECTID"]): feature for feature in features}
    missing = sorted(set(PRESERVES) - set(by_id))
    if missing:
        raise RuntimeError(f"FDEP preserve features missing expected OBJECTIDs: {missing}")
    for feature in features:
        geometry = feature.get("geometry") or {}
        if geometry.get("type") not in {"Polygon", "MultiPolygon"}:
            raise ValueError(f"Unexpected FDEP preserve geometry type: {geometry.get('type')}")
    collection = {
        "type": "FeatureCollection",
        "name": "fdep_biscayne_aquatic_preserves",
        "features": [
            {
                **by_id[object_id],
                "properties": {
                    **by_id[object_id]["properties"],
                    "LUPITA_CONTEXT_NAME": name,
                    "LUPITA_SOURCE_LAYER_ID": 0,
                    "LUPITA_SOURCE_OBJECTID": object_id,
                },
            }
            for object_id, name in PRESERVES.items()
        ],
    }
    return metadata, collection


def line_only_length(geometry) -> float:
    """Return length only for linear members of a geometry or collection."""
    if geometry is None or geometry.is_empty:
        return 0.0
    if geometry.geom_type in {"LineString", "MultiLineString", "LinearRing"}:
        return geometry.length
    if geometry.geom_type == "GeometryCollection":
        return sum(line_only_length(part) for part in geometry.geoms)
    return 0.0


def polygon_area_comparison(first, second) -> dict:
    intersection = first.intersection(second)
    first_area = first.area
    second_area = second.area
    overlap = intersection.area
    return {
        "first_area_km2": round(first_area / 1_000_000, 3),
        "second_area_km2": round(second_area / 1_000_000, 3),
        "intersection_area_km2": round(overlap / 1_000_000, 3),
        "first_area_intersection_pct": round(100 * overlap / first_area, 2) if first_area else None,
        "second_area_intersection_pct": round(100 * overlap / second_area, 2) if second_area else None,
    }


def line_polygon_overlay(linework, polygon) -> dict:
    total = line_only_length(linework)
    inside = line_only_length(linework.intersection(polygon))
    outside = line_only_length(linework.difference(polygon))
    return {
        "total_line_length_km": round(total / 1000, 3),
        "inside_polygon_length_km": round(inside / 1000, 3),
        "outside_polygon_length_km": round(outside / 1000, 3),
        "inside_line_length_pct": round(100 * inside / total, 2) if total else None,
        "minimum_distance_to_polygon_boundary_m": round(
            linework.distance(polygon.boundary), 2
        ),
    }


def partitioned_line_overlay(linework, charted_bay, preserve) -> dict:
    """Partition source line length into mutually exclusive overlay classes."""
    chart_intersection = linework.intersection(charted_bay)
    preserve_intersection = linework.intersection(preserve)
    both = chart_intersection.intersection(preserve)
    chart_only = chart_intersection.difference(preserve)
    preserve_only = preserve_intersection.difference(charted_bay)
    outside_both = linework.difference(charted_bay.union(preserve))
    result = {
        "inside_both_km": round(line_only_length(both) / 1000, 3),
        "charted_bay_only_km": round(line_only_length(chart_only) / 1000, 3),
        "fdep_preserve_only_km": round(line_only_length(preserve_only) / 1000, 3),
        "outside_both_km": round(line_only_length(outside_both) / 1000, 3),
    }
    result["partition_total_km"] = round(sum(result.values()), 3)
    return result


def _line_endpoints(geometry) -> list[Point]:
    if geometry is None or geometry.is_empty:
        return []
    if geometry.geom_type == "LineString":
        coords = list(geometry.coords)
        return [Point(coords[0]), Point(coords[-1])] if len(coords) >= 2 else []
    if geometry.geom_type in {"MultiLineString", "GeometryCollection"}:
        return [point for part in geometry.geoms for point in _line_endpoints(part)]
    return []


def _feature_overlay(feature, charted_bay, preserve, named_water_metric) -> tuple[dict, object]:
    line = transform(TO_METRIC, shape(feature["geometry"]))
    props = feature.get("properties", {})
    total = line_only_length(line)
    chart = line.intersection(charted_bay)
    fdep = line.intersection(preserve)
    both = chart.intersection(preserve)
    chart_only = chart.difference(preserve)
    fdep_only = fdep.difference(charted_bay)
    outside = line.difference(charted_bay.union(preserve))

    hits = []
    for water_id, water_geometry, water_properties in named_water_metric:
        hit_length = line_only_length(line.intersection(water_geometry))
        if hit_length >= 25:
            hits.append({
                "objectid": water_id,
                "name": water_properties.get("OBJNAM"),
                "chart_cell": water_properties.get("DSNM"),
                "intersection_length_m": round(hit_length, 1),
            })
    hits.sort(key=lambda item: item["intersection_length_m"], reverse=True)

    result = {
        "feature_id": int(props["FEATURE_ID"]),
        "source_id": props.get("SOURCE_ID"),
        "source_date": props.get("SRC_DATE"),
        "horizontal_accuracy_m": props.get("HOR_ACC"),
        "length_m": round(total, 1),
        "inside_noaa_charted_biscayne_bay_m": round(line_only_length(chart), 1),
        "inside_fdep_biscayne_bay_preserve_m": round(line_only_length(fdep), 1),
        "partition_m": {
            "inside_both": round(line_only_length(both), 1),
            "charted_bay_only": round(line_only_length(chart_only), 1),
            "fdep_preserve_only": round(line_only_length(fdep_only), 1),
            "outside_both": round(line_only_length(outside), 1),
        },
        "named_water_context_hits": hits[:3],
    }
    return result, line


def _project_pair_separation(first_features: list[tuple], second_features: list[tuple]]) -> dict:
    best_distance = float("inf")
    best_pair = None
    best_endpoint_distance = float("inf")
    for first_id, first_line in first_features:
        first_endpoints = _line_endpoints(first_line)
        for second_id, second_line in second_features:
            distance = first_line.distance(second_line)
            if distance < best_distance:
                best_distance = distance
                best_pair = [first_id, second_id]
            second_endpoints = _line_endpoints(second_line)
            for first_point in first_endpoints:
                for second_point in second_endpoints:
                    endpoint_distance = first_point.distance(second_point)
                    if endpoint_distance < best_endpoint_distance:
                        best_endpoint_distance = endpoint_distance
    return {
        "minimum_line_geometry_distance_m": round(best_distance, 2) if best_pair else None,
        "minimum_distance_feature_ids": best_pair,
        "minimum_endpoint_to_endpoint_distance_m": (
            round(best_endpoint_distance, 2) if best_pair else None
        ),
        "interpretation": (
            "separate extracted project coverage; not an alongshore gap or physical water connection"
            if best_pair else "not comparable because one project has no MHW features"
        ),
    }


def run_audit(repo_root: Path, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": "LUPITA-research-spatial-overlay/1.0"})
    fdep_metadata, fdep_collection = fetch_fdep_preserves(session)
    (output_dir / "fdep_biscayne_aquatic_preserves.geojson").write_text(
        json.dumps(fdep_collection, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    (output_dir / "fdep_aquatic_preserves_layer_metadata.json").write_text(
        json.dumps(fdep_metadata, indent=2) + "\n", encoding="utf-8"
    )

    fdep_metric = {
        int(feature["properties"]["OBJECTID"]): transform(
            TO_METRIC, shape(feature["geometry"])
        )
        for feature in fdep_collection["features"]
    }
    named_water_path = repo_root / "data/spatial/noaa-biscayne-named-water-areas.geojson"
    named_water = json.loads(named_water_path.read_text(encoding="utf-8"))
    bay_features = [
        feature for feature in named_water["features"]
        if feature.get("properties", {}).get("OBJNAM") == "Biscayne Bay"
    ]
    if len(bay_features) != 37:
        raise RuntimeError(
            f"Expected 37 curated NOAA ENC Biscayne Bay chart polygons, found {len(bay_features)}"
        )
    noaa_bay = transform(
        TO_METRIC,
        unary_union([shape(feature["geometry"]) for feature in bay_features]),
    )
    named_water_metric = [
        (
            int(feature["properties"]["OBJECTID"]),
            transform(TO_METRIC, shape(feature["geometry"])),
            feature["properties"],
        )
        for feature in named_water["features"]
        if feature.get("geometry")
    ]
    fdep_bay = fdep_metric[43]
    fdep_cape_florida = fdep_metric[25]

    project_overlays = {}
    feature_overlays = {}
    project_feature_lines = {}
    for project_id in PROJECT_IDS:
        path = repo_root / "data/spatial/research/noaa_cmp/geojson" / f"{project_id}_mhw.geojson"
        collection = json.loads(path.read_text(encoding="utf-8"))
        features = collection.get("features", [])
        details = []
        lines = []
        for feature in features:
            detail, metric_line = _feature_overlay(
                feature, noaa_bay, fdep_bay, named_water_metric
            )
            details.append(detail)
            lines.append((detail["feature_id"], metric_line))
        linework = unary_union([line for _, line in lines]) if lines else None
        project_feature_lines[project_id] = lines
        if linework is not None:
            partition = partitioned_line_overlay(linework, noaa_bay, fdep_bay)
            overlays = {
                "noaa_charted_biscayne_bay_named_water_union": line_polygon_overlay(
                    linework, noaa_bay
                ),
                "fdep_biscayne_bay_aquatic_preserve_objectid_43": line_polygon_overlay(
                    linework, fdep_bay
                ),
                "fdep_cape_florida_preserve_objectid_25": line_polygon_overlay(
                    linework, fdep_cape_florida
                ),
                "mutually_exclusive_chart_and_preserve_partition": partition,
            }
            source_dates = sorted({item["source_date"] for item in details if item["source_date"]})
            horizontal_accuracy = sorted({
                item["horizontal_accuracy_m"] for item in details
                if item["horizontal_accuracy_m"] is not None
            })
        else:
            overlays = {}
            source_dates = []
            horizontal_accuracy = []
        project_overlays[project_id] = {
            "mhw_feature_count": len(features),
            "mhw_line_length_km": round(line_only_length(linework) / 1000, 3) if linework else 0,
            "source_dates": source_dates,
            "horizontal_accuracy_m": horizontal_accuracy,
            "features_intersecting_charted_bay": sum(
                item["inside_noaa_charted_biscayne_bay_m"] > 1 for item in details
            ),
            "features_intersecting_fdep_preserve": sum(
                item["inside_fdep_biscayne_bay_preserve_m"] > 1 for item in details
            ),
            "overlays": overlays,
            "status": "mhw_linework_retrieved" if features else "no_natural_mhw_features_in_project",
        }
        feature_overlays[project_id] = details

    project_separation = {}
    populated = [project_id for project_id in PROJECT_IDS if project_feature_lines[project_id]]
    for index, first in enumerate(populated):
        for second in populated[index + 1:]:
            key = f"{first}__{second}"
            project_separation[key] = _project_pair_separation(
                project_feature_lines[first], project_feature_lines[second]
            )

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "feature_level_overlay_metrics_computed",
        "output_crs_for_measurements": "EPSG:26917",
        "sources": {
            "noaa_cmp_projects": [
                "https://www.fisheries.noaa.gov/inport/item/74866",
                "https://www.fisheries.noaa.gov/inport/item/73241",
                "https://www.fisheries.noaa.gov/inport/item/76789",
            ],
            "noaa_enc_named_water": "https://encdirect.noaa.gov/arcgis/rest/services/encdirect/enc_harbour/MapServer/237",
            "fdep_aquatic_preserves": FDEP_LAYER,
        },
        "comparison_geometry": {
            "noaa_enc_biscayne_bay_polygon_count": len(bay_features),
            "noaa_enc_biscayne_bay_objectids": sorted(
                int(feature["properties"]["OBJECTID"]) for feature in bay_features
            ),
            "fdep_biscayne_bay_objectid": 43,
            "fdep_cape_florida_preserve_objectid": 25,
            "interpretation": (
                "NOAA charted named-water polygons and FDEP management preserves are separate "
                "comparison contexts, not substitutes for a shoreline or ecological boundary."
            ),
        },
        "fdep_preserves": {
            "Biscayne Bay": {"objectid": 43, "acres": 64607.580491},
            "Biscayne Bay-Cape Florida to Monroe County Line": {
                "objectid": 25, "acres": 4163.903858,
            },
        },
        "noaa_enc_biscayne_bay_vs_fdep_objectid_43_area_overlay": polygon_area_comparison(
            noaa_bay, fdep_bay
        ),
        "project_mhw_line_overlays": project_overlays,
        "feature_level_mhw_overlays": feature_overlays,
        "nearest_mhw_project_separations": project_separation,
        "limitations": [
            "NOAA ENC named-water polygons are charted named-water areas, not complete ecological or statutory boundaries.",
            "FDEP Aquatic Preserve polygons are approximate management GIS geometries, not legal survey or enforcement geometry.",
            "MHW project linework is source-specific shoreline evidence, but its segmented coverage does not establish a continuous bay boundary.",
            "Line length inside a preserve or charted water polygon is a spatial overlay statistic, not a shoreline-accuracy score.",
            "MHW lines outside both comparison polygons are not automatically errors or missing shoreline.",
            "The MHHW screening product is not used in this MHW overlay.",
            "No gaps are bridged, no lines are snapped, and separate FDEP preserve designations are not merged.",
            "The FL1808A/FL1808C project separation is a distance between extracted source line sets, not an alongshore gap or evidence of an inlet connection.",
            "No production scoring, species profile values, or API v1 behavior is changed.",
        ],
    }
    (output_dir / "noaa_cmp_fdep_spatial_alignment_audit.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/noaa-cmp-overlay"))
    args = parser.parse_args()
    report = run_audit(args.repo_root, args.output_dir)
    print(json.dumps({
        "comparison_geometry": report["comparison_geometry"],
        "project_mhw_line_overlays": report["project_mhw_line_overlays"],
        "nearest_mhw_project_separations": report["nearest_mhw_project_separations"],
    }, indent=2))
