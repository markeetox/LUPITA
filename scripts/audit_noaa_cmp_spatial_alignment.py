"""Compare NOAA CMP MHW linework with NOAA ENC named-water and FDEP preserve geometry.

Research-only spatial overlay. It does not create, infer, or publish a legal bay
boundary and does not modify production scoring or API data.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import requests
from pyproj import Transformer
from shapely.geometry import shape
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
    query_url = f"{FDEP_LAYER}/query"
    response = session.get(
        query_url,
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
    total = linework.length
    inside = linework.intersection(polygon).length
    outside = linework.difference(polygon).length
    return {
        "total_line_length_km": round(total / 1000, 3),
        "inside_polygon_length_km": round(inside / 1000, 3),
        "outside_polygon_length_km": round(outside / 1000, 3),
        "inside_line_length_pct": round(100 * inside / total, 2) if total else None,
        "minimum_distance_to_polygon_boundary_m": round(
            linework.distance(polygon.boundary), 2
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

    fdep_metric = {}
    for feature in fdep_collection["features"]:
        object_id = int(feature["properties"]["OBJECTID"])
        fdep_metric[object_id] = transform(TO_METRIC, shape(feature["geometry"]))

    named_water_path = repo_root / "data/spatial/noaa-biscayne-named-water-areas.geojson"
    named_water = json.loads(named_water_path.read_text(encoding="utf-8"))
    bay_features = [
        feature for feature in named_water["features"]
        if feature.get("properties", {}).get("OBJNAM") == "Biscayne Bay"
    ]
    if not bay_features:
        raise RuntimeError("NOAA ENC named-water source has no Biscayne Bay polygons")
    noaa_bay = transform(
        TO_METRIC,
        unary_union([shape(feature["geometry"]) for feature in bay_features]),
    )

    fdep_bay = fdep_metric[43]
    fdep_cape_florida = fdep_metric[25]
    area_comparison = polygon_area_comparison(noaa_bay, fdep_bay)

    project_overlays = {}
    project_geometries = {}
    for project_id in PROJECT_IDS:
        path = repo_root / "data/spatial/research/noaa_cmp/geojson" / f"{project_id}_mhw.geojson"
        collection = json.loads(path.read_text(encoding="utf-8"))
        features = collection.get("features", [])
        lines = [
            transform(TO_METRIC, shape(feature["geometry"]))
            for feature in features
        ]
        linework = unary_union(lines) if lines else None
        if linework is not None:
            project_geometries[project_id] = linework
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
            }
        else:
            overlays = {}
        project_overlays[project_id] = {
            "mhw_feature_count": len(features),
            "mhw_line_length_km": round(linework.length / 1000, 3) if linework else 0,
            "overlays": overlays,
            "status": "mhw_linework_retrieved" if features else "no_natural_mhw_features_in_project",
        }

    project_separation = {}
    ids = sorted(project_geometries)
    for index, first in enumerate(ids):
        for second in ids[index + 1:]:
            project_separation[f"{first}__{second}"] = round(
                project_geometries[first].distance(project_geometries[second]) / 1000, 3
            )

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "overlay_metrics_computed",
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
        "fdep_preserves": {
            "Biscayne Bay": {"objectid": 43, "acres": 64607.580491},
            "Biscayne Bay-Cape Florida to Monroe County Line": {
                "objectid": 25, "acres": 4163.903858,
            },
        },
        "noaa_enc_biscayne_bay_charted_polygon_count": len(bay_features),
        "noaa_enc_biscayne_bay_vs_fdep_objectid_43_area_overlay": area_comparison,
        "project_mhw_line_overlays": project_overlays,
        "nearest_mhw_project_separations_km": project_separation,
        "limitations": [
            "NOAA ENC named-water polygons are charted named-water areas, not complete ecological or statutory boundaries.",
            "FDEP Aquatic Preserve polygons are approximate management GIS geometries, not legal survey or enforcement geometry.",
            "MHW project linework is source-specific shoreline evidence, but its segmented coverage does not establish a continuous bay boundary.",
            "Line length inside a preserve or charted water polygon is a spatial overlay statistic, not a shoreline-accuracy score.",
            "The MHHW screening product is not used in this MHW overlay.",
            "No gaps are bridged, no lines are snapped, and separate FDEP preserve designations are not merged.",
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
        "noaa_enc_biscayne_bay_charted_polygon_count": report["noaa_enc_biscayne_bay_charted_polygon_count"],
        "area_overlay": report["noaa_enc_biscayne_bay_vs_fdep_objectid_43_area_overlay"],
        "project_mhw_overlays": report["project_mhw_line_overlays"],
        "nearest_mhw_project_separations_km": report["nearest_mhw_project_separations_km"],
    }, indent=2))
