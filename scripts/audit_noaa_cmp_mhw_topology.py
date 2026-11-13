"""Audit NOAA CMP mean-high-water line topology across Biscayne-area projects.

Research-only. This script measures source linework and endpoint relationships;
it never snaps, bridges, dissolves, or promotes shoreline geometry to a bay boundary.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform, unary_union

PROJECT_FILES = {
    "FL1603A-CM-N": "FL1603A-CM-N_softcopyl1.geojson",
    "FL1808A-TB-N": "FL1808A-TB-N_mhw.geojson",
    "FL1808C-TB-N": "FL1808C-TB-N_mhw.geojson",
    "FL2317-CS-N": "FL2317-CS-N_mhw.geojson",
}
TO_METRIC = Transformer.from_crs(4326, 26917, always_xy=True).transform


def load_mhw_features(path: Path, project_id: str) -> list[dict]:
    collection = json.loads(path.read_text(encoding="utf-8"))
    features = collection.get("features")
    if not isinstance(features, list):
        raise ValueError(f"{path} is not a GeoJSON FeatureCollection")
    if project_id == "FL1603A-CM-N":
        features = [
            feature for feature in features
            if feature.get("properties", {}).get("ATTRIBUTE") == "Natural.Mean High Water"
        ]
    result = []
    for feature in features:
        geometry = feature.get("geometry")
        if not geometry:
            continue
        metric = transform(TO_METRIC, shape(geometry))
        if metric.geom_type != "LineString":
            raise ValueError(f"Unexpected {metric.geom_type} in {path}")
        props = feature.get("properties", {})
        result.append({
            "geometry": metric,
            "feature_id": props.get("FEATURE_ID"),
            "source_id": props.get("SOURCE_ID"),
            "source_date": props.get("SRC_DATE"),
            "horizontal_accuracy_m": props.get("HOR_ACC"),
        })
    return result


def endpoint_component_count(features: list[dict]) -> dict:
    endpoints = []
    for index, item in enumerate(features):
        coords = item["geometry"].coords
        endpoints.extend([(tuple(coords[0]), index), (tuple(coords[-1]), index)])
    parent = list(range(len(features)))

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(first: int, second: int) -> None:
        a, b = find(first), find(second)
        if a != b:
            parent[b] = a

    coordinate_owners: dict[tuple[float, float], list[int]] = {}
    for coordinate, owner in endpoints:
        coordinate_owners.setdefault(coordinate, []).append(owner)
    for owners in coordinate_owners.values():
        for owner in owners[1:]:
            union(owners[0], owner)
    return {
        "component_count_by_exact_shared_endpoints": len({find(i) for i in range(len(features))}) if features else 0,
        "endpoint_coordinate_count": len(coordinate_owners),
        "degree_1_endpoint_coordinate_count": sum(len(v) == 1 for v in coordinate_owners.values()),
        "shared_endpoint_coordinate_count": sum(len(v) == 2 for v in coordinate_owners.values()),
        "branch_endpoint_coordinate_count": sum(len(v) > 2 for v in coordinate_owners.values()),
    }


def summarize_project(features: list[dict]) -> dict:
    lines = [item["geometry"] for item in features]
    return {
        "feature_count": len(features),
        "total_feature_length_km": round(sum(line.length for line in lines) / 1000, 3),
        **endpoint_component_count(features),
        "source_feature_ids": [item["feature_id"] for item in features],
        "source_dates": sorted({str(item["source_date"]) for item in features if item["source_date"]}),
        "reported_horizontal_accuracy_m": sorted({str(item["horizontal_accuracy_m"]) for item in features if item["horizontal_accuracy_m"]}),
    }


def closest_relationship(first: list[dict], second: list[dict]) -> dict:
    if not first or not second:
        return {"status": "not_comparable_no_mhw_features"}
    nearest_geometry = (math.inf, None)
    nearest_endpoints = (math.inf, None)
    for a in first:
        for b in second:
            distance = a["geometry"].distance(b["geometry"])
            if distance < nearest_geometry[0]:
                nearest_geometry = (distance, (a, b))
            ac = a["geometry"].coords
            bc = b["geometry"].coords
            for p in (ac[0], ac[-1]):
                for q in (bc[0], bc[-1]):
                    endpoint_distance = math.dist(p, q)
                    if endpoint_distance < nearest_endpoints[0]:
                        nearest_endpoints = (endpoint_distance, (a, b, p, q))
    ga, gb = nearest_geometry[1]
    ea, eb, p, q = nearest_endpoints[1]
    return {
        "minimum_line_geometry_distance_m": round(nearest_geometry[0], 2),
        "minimum_line_geometry_feature_ids": [ga["feature_id"], gb["feature_id"]],
        "minimum_endpoint_to_endpoint_distance_m": round(nearest_endpoints[0], 2),
        "minimum_endpoint_feature_ids": [ea["feature_id"], eb["feature_id"]],
        "minimum_endpoint_coordinates_epsg26917_m": [[round(v, 3) for v in p], [round(v, 3) for v in q]],
        "interpretation": "measured separation or contact between extracted MHW features only; not proof of a physical inlet, shoreline continuity, or a legal/ecological boundary",
    }


def run(repo_root: Path, output: Path) -> dict:
    data_dir = repo_root / "data/spatial/research/noaa_cmp/geojson"
    projects = {
        pid: load_mhw_features(data_dir / filename, pid)
        for pid, filename in PROJECT_FILES.items()
    }
    pairwise = {}
    ids = list(PROJECT_FILES)
    for i, first_id in enumerate(ids):
        for second_id in ids[i + 1:]:
            pairwise[f"{first_id}__{second_id}"] = closest_relationship(
                projects[first_id], projects[second_id]
            )

    boundary_path = data_dir / "FL1603A-CM-N_projbnd.geojson"
    boundary_collection = json.loads(boundary_path.read_text(encoding="utf-8"))
    boundary = transform(TO_METRIC, shape(boundary_collection["features"][0]["geometry"]))
    local_project_lines = [item["geometry"] for item in projects["FL1603A-CM-N"]]
    local_union = unary_union(local_project_lines) if local_project_lines else None
    boundary_comparison = {
        "boundary_area_km2": round(boundary.area / 1_000_000, 3),
        "mhw_line_length_inside_project_boundary_km": round(local_union.intersection(boundary).length / 1000, 3) if local_union else 0,
        "mhw_line_length_outside_project_boundary_km": round(local_union.difference(boundary).length / 1000, 3) if local_union else 0,
        "minimum_mhw_distance_to_project_boundary_m": round(local_union.distance(boundary.boundary), 2) if local_union else None,
        "note": "FL1603 project boundary is a survey-project extent, not a Biscayne Bay boundary",
    }
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "computed_research_topology_audit",
        "source": "NOAA National Geodetic Survey Coastal Mapping Program project GeoJSON persisted on research branch",
        "measurement_crs": "EPSG:26917",
        "method": "exact source endpoint coordinate matching; pairwise Shapely line geometry distance; no snapping or gap bridging",
        "projects": {pid: summarize_project(features) for pid, features in projects.items()},
        "pairwise_project_relationships": pairwise,
        "fl1603_project_boundary_comparison": boundary_comparison,
        "limitations": [
            "The NOAA CMP project extents are not a continuous coverage promise.",
            "A gap between project linework is a data-coverage separation, not proof that a physical shoreline or inlet is absent.",
            "Exact endpoint matches are coordinate topology only; near matches are reported separately and never snapped.",
            "MHW shoreline, apparent mangrove edges, structures, and depth contours are different feature types and must not be merged.",
            "FL1603A-CM-N is a local Convoy Point survey project and its project boundary is not a bay boundary.",
            "No production scoring, species files, API contracts, or production spatial data are modified.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("artifacts/noaa-cmp-mhw-topology-audit.json"))
    args = parser.parse_args()
    result = run(args.repo_root, args.output)
    print(json.dumps({
        "projects": {
            key: {
                "feature_count": value["feature_count"],
                "components": value["component_count_by_exact_shared_endpoints"],
                "total_km": value["total_feature_length_km"],
            }
            for key, value in result["projects"].items()
        },
        "pairwise_project_relationships": result["pairwise_project_relationships"],
        "fl1603_project_boundary_comparison": result["fl1603_project_boundary_comparison"],
    }, indent=2))
