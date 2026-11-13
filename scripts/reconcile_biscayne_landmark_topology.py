"""Research-only topology checks for NOAA ENC Biscayne landmark evidence."""
from __future__ import annotations
import argparse, json
from itertools import combinations
from pathlib import Path
from pyproj import Transformer
from shapely.geometry import Point, shape
from shapely.ops import transform

PROJECT = Transformer.from_crs("EPSG:4326", "EPSG:26917", always_xy=True).transform
STATION = Point(-80.39, 25.1833)

def load_features(folder: Path, filename: str):
    path = folder / filename
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8")).get("features", [])

def projected(feature):
    return transform(PROJECT, shape(feature["geometry"]))

def properties(feature):
    return feature.get("properties") or {}

def feature_id(feature):
    return properties(feature).get("OBJECTID")

def analyze_jewfish(folder: Path):
    water = load_features(folder, "jewfish_creek_layer_237.geojson")
    creek = [f for f in water if properties(f).get("OBJNAM") == "Jewfish Creek"]
    if len(creek) != 2:
        raise ValueError(f"Expected exactly two Jewfish Creek polygons; found {len(creek)}")
    geoms = [projected(f) for f in creek]
    merged = geoms[0].union(geoms[1])
    if not merged.is_valid:
        raise ValueError("Jewfish Creek union is invalid")
    station = transform(PROJECT, STATION)
    relations = []
    for f in water:
        p = properties(f)
        if p.get("OBJNAM") == "Jewfish Creek":
            continue
        g = projected(f)
        inter = merged.intersection(g)
        if inter.area > 0 or inter.length > 0 or merged.distance(g) < 1:
            relations.append({"objectid": feature_id(f), "name": p.get("OBJNAM"),
                "chart_cell": p.get("DSNM"), "overlap_area_m2": round(inter.area, 2),
                "shared_boundary_m": round(inter.length, 2), "minimum_distance_m": round(merged.distance(g), 2)})
    coast = []
    for f in load_features(folder, "jewfish_creek_layer_84.geojson"):
        inter = merged.intersection(projected(f))
        if not inter.is_empty and inter.length > 0:
            coast.append({"objectid": feature_id(f), "intersection_length_m": round(inter.length, 2),
                "source_date": properties(f).get("SORDAT"), "chart_cell": properties(f).get("DSNM")})
    return {"source_layer": 237, "source_objectids": sorted(feature_id(f) for f in creek),
        "chart_cells": sorted({properties(f).get("DSNM") for f in creek}),
        "source_dates": sorted({properties(f).get("SORDAT") for f in creek}),
        "polygon_count": len(creek), "polygons_touch_or_overlap": geoms[0].intersects(geoms[1]),
        "polygon_gap_m": round(geoms[0].distance(geoms[1]), 3),
        "union_component_count": len(getattr(merged, "geoms", [merged])),
        "union_area_km2": round(merged.area / 1_000_000, 6),
        "union_perimeter_km": round(merged.length / 1000, 4),
        "station_8723613": {"coordinates_wgs84": [-80.39, 25.1833],
            "inside_mapped_creek_polygon": merged.covers(station),
            "distance_to_mapped_polygon_m": round(merged.distance(station), 2),
            "interpretation": "tidal benchmark reference only; not a channel centerline or mouth"},
        "named_water_relations": relations, "intersecting_coastline_features": coast,
        "interpretation": "NOAA charted named-water polygons and coastline context; not surveyed channel geometry"}

def analyze_card_sound(folder: Path):
    features = load_features(folder, "noaa_card_sound_named_water.geojson")
    expected = {246233, 246243, 246247, 246258, 246267, 246284}
    by_id = {feature_id(f): f for f in features}
    if set(by_id) != expected:
        raise ValueError(f"Card Sound OBJECTID set mismatch: {sorted(set(by_id))}")
    pairs = []
    for aid, bid in combinations(sorted(by_id), 2):
        a, b = projected(by_id[aid]), projected(by_id[bid])
        inter = a.intersection(b)
        if a.intersects(b) or a.distance(b) < 1:
            pairs.append({"objectids": [aid, bid], "intersects": a.intersects(b),
                "overlap_area_m2": round(inter.area, 2), "shared_boundary_m": round(inter.length, 2),
                "minimum_distance_m": round(a.distance(b), 3)})
    rows = []
    for oid, f in sorted(by_id.items()):
        p, g = properties(f), projected(f)
        rows.append({"objectid": oid, "chart_cell": p.get("DSNM"), "source_date": p.get("SORDAT"),
            "area_km2": round(g.area / 1_000_000, 6), "valid": g.is_valid})
    return {"feature_count": len(rows), "features": rows, "touching_or_overlapping_pairs": pairs,
        "interpretation": "retain original chart-cell features; adjacency does not establish a navigable connection"}

def analyze_rickenbacker(folder: Path):
    land = load_features(folder, "rickenbacker_causeway_layer_233.geojson")
    named = [f for f in land if properties(f).get("OBJNAM") == "Rickenbacker Causeway"]
    if len(named) != 1:
        raise ValueError(f"Expected one named Rickenbacker Causeway land polygon; found {len(named)}")
    causeway = projected(named[0])
    coast = []
    for f in load_features(folder, "rickenbacker_causeway_layer_84.geojson"):
        inter = causeway.intersection(projected(f))
        if not inter.is_empty and inter.length > 0:
            coast.append({"objectid": feature_id(f), "intersection_length_m": round(inter.length, 2),
                "chart_cell": properties(f).get("DSNM"), "source_date": properties(f).get("SORDAT")})
    bridges = []
    for f in load_features(folder, "rickenbacker_causeway_layer_87.geojson"):
        g = projected(f)
        bridges.append({"objectid": feature_id(f), "name": properties(f).get("OBJNAM"),
            "distance_to_named_land_polygon_m": round(causeway.distance(g), 2),
            "chart_cell": properties(f).get("DSNM"), "source_date": properties(f).get("SORDAT")})
    bridges.sort(key=lambda x: x["distance_to_named_land_polygon_m"])
    return {"source_layer": 233, "objectid": feature_id(named[0]), "name": properties(named[0]).get("OBJNAM"),
        "chart_cell": properties(named[0]).get("DSNM"), "area_km2": round(causeway.area / 1_000_000, 6),
        "intersecting_coastline_features": coast, "bridge_features_in_query_bbox": bridges,
        "causeway_line_layer_118_feature_count": len(load_features(folder, "rickenbacker_causeway_layer_118.geojson")),
        "interpretation": "named land polygon plus coastline context; returned bridge lines are not assumed to be causeway crossings"}

def run(folder: Path):
    return {"report_version": 1, "status": "research_only", "measurement_crs": "EPSG:26917",
        "source": "NOAA ENC Harbour MapServer; source attributes retained in input GeoJSON",
        "jewfish_creek": analyze_jewfish(folder), "card_sound": analyze_card_sound(folder),
        "rickenbacker_causeway": analyze_rickenbacker(folder),
        "limitations": ["ENC geometry is chart context, not certified navigation data.",
            "No geometry is modified, dissolved, snapped, extended, or bridged.",
            "Touching/overlap results do not prove tidal exchange, navigability, or ecological connectivity.",
            "No ecological separator or production model input is generated."]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("biscayne_landmark_topology_report.json"))
    args = parser.parse_args()
    report = run(args.input_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
