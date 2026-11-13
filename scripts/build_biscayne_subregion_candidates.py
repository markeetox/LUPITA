"""Build research-only Biscayne ecological subregion and habitat candidates.

This deliberately does not manufacture polygon boundaries for literature-defined
North/Central/South Bay regions. It crosswalks named NOAA chart contexts with
FWC/NPS benthic source polygons and preserves mapped tidal-flat patches.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pyproj import Transformer
from shapely import make_valid
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon, shape
from shapely.ops import transform, unary_union

AREA_CRS = "EPSG:26917"
TO_AREA = Transformer.from_crs("EPSG:4326", AREA_CRS, always_xy=True).transform

NAMED_CONTEXTS = {
    "Biscayne Bay": "sf-biscayne-bay-ecological-context",
    "Safety Valve": "sf-biscayne-safety-valve-complex",
    "Biscayne Flats": "sf-biscayne-flats",
    "Bear Cut": "sf-bear-cut",
    "Norris Cut": "sf-norris-cut",
    "Black Ledge": "sf-biscayne-black-ledge",
    "Featherbed Bank": "sf-featherbed-bank",
    "Lewis Cut": "sf-lewis-cut",
    "Biscayne Channel": "sf-biscayne-channel",
    "Sands Cut": "sf-sands-cut",
    "Snapper Creek Canal": "sf-snapper-creek-canal",
    "Goulds Canal": "sf-goulds-canal",
    "Deering Channel": "sf-deering-channel",
    "Cape Florida Channel": "sf-cape-florida-channel",
}

SUBREGIONS = [
    {
        "id": "sf-biscayne-bay-northern-context",
        "name": "North Biscayne Bay",
        "north_limit": "Dumfoundling Bay",
        "south_limit": "Rickenbacker Causeway",
        "boundary_note": "North Biscayne Bay extends from Dumfoundling Bay to the Rickenbacker Causeway in the published ecological segmentation.",
    },
    {
        "id": "sf-biscayne-bay-central-southern-context",
        "name": "Central Biscayne Bay",
        "north_limit": "Rickenbacker Causeway",
        "south_limit": "Featherbed Bank / Black Point",
        "boundary_note": "Central Biscayne Bay extends from the Rickenbacker Causeway to Featherbed Bank / Black Point in the published ecological segmentation.",
    },
    {
        "id": "sf-biscayne-bay-southern-context",
        "name": "South Biscayne Bay",
        "north_limit": "Featherbed Bank / Black Point",
        "south_limit": "Card Sound / Jewfish Creek",
        "boundary_note": "South Biscayne Bay extends from Featherbed Bank / Black Point to Card Sound / Jewfish Creek in the published ecological segmentation.",
    },
]

ARTICLE_URL = "https://doi.org/10.3389/fmars.2022.894663"


def read_collection(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("type") != "FeatureCollection" or not isinstance(payload.get("features"), list):
        raise ValueError(f"{path} is not a GeoJSON FeatureCollection")
    return payload


def valid_polygon(feature: dict[str, Any], source: str, *, repair: bool = False):
    geometry = feature.get("geometry")
    if not geometry or geometry.get("type") not in {"Polygon", "MultiPolygon"}:
        raise ValueError(f"{source}: expected polygon geometry")
    geom = shape(geometry)
    if geom.is_empty or geom.area <= 0:
        raise ValueError(f"{source}: empty or zero-area polygon")
    if not geom.is_valid:
        if not repair:
            raise ValueError(f"{source}: invalid polygon geometry")
        geom = make_valid(geom)
        if isinstance(geom, GeometryCollection):
            polygon_parts = [
                part for part in geom.geoms
                if isinstance(part, (Polygon, MultiPolygon)) and not part.is_empty
            ]
            geom = unary_union(polygon_parts)
        if geom.is_empty or not geom.is_valid or geom.area <= 0:
            raise ValueError(f"{source}: polygon could not be repaired for analysis")
    return geom


def _area_union_km2(geometries) -> float:
    geometries = list(geometries)
    if not geometries:
        return 0.0
    return round(transform(TO_AREA, unary_union(geometries)).area / 1_000_000, 6)


def _intersection_area_km2(geometries) -> float:
    return _area_union_km2(geometries)


def build_audit(
    benthic: dict[str, Any],
    footprints: dict[str, Any],
    preserves: dict[str, Any],
    named_water: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    benthic_features = benthic["features"]
    repaired_benthic_objectids = []
    benthic_geometries = []
    for feature in benthic_features:
        objectid = (feature.get("properties") or {}).get("OBJECTID")
        original = shape(feature["geometry"])
        if not original.is_valid:
            repaired_benthic_objectids.append(int(objectid))
        benthic_geometries.append(
            valid_polygon(feature, f"benthic OBJECTID {objectid}", repair=True)
        )
    footprint_geometries = [
        valid_polygon(feature, f"source footprint OBJECTID {feature.get('properties', {}).get('OBJECTID')}")
        for feature in footprints["features"]
    ]
    footprint_union = unary_union(footprint_geometries)

    preserve_feature = next(
        (
            feature for feature in preserves["features"]
            if (feature.get("properties") or {}).get("OBJECTID") == 43
        ),
        None,
    )
    preserve_geom = valid_polygon(preserve_feature, "FDEP Biscayne Bay preserve OBJECTID 43") if preserve_feature else None

    grouped_named: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for feature in named_water["features"]:
        name = (feature.get("properties") or {}).get("OBJNAM")
        if name in NAMED_CONTEXTS:
            grouped_named[name].append(feature)

    overlays = {}
    for name, context_id in NAMED_CONTEXTS.items():
        source_features = grouped_named.get(name, [])
        source_geometries = [
            valid_polygon(feature, f"NOAA named-water {name} OBJECTID {(feature.get('properties') or {}).get('OBJECTID')}")
            for feature in source_features
        ]
        if not source_geometries:
            overlays[name] = {
                "context_id": context_id,
                "status": "source_feature_not_found",
                "source_feature_count": 0,
                "benthic_overlay": {},
            }
            continue

        named_union = unary_union(source_geometries)
        class_intersections: dict[str, list[Any]] = defaultdict(list)
        class_objectids: dict[str, set[int]] = defaultdict(set)
        all_objectids = set()
        tidal_flat_ids = set()
        for feature, geom in zip(benthic_features, benthic_geometries):
            if not geom.intersects(named_union):
                continue
            props = feature.get("properties") or {}
            objectid = props.get("OBJECTID")
            if objectid is None:
                continue
            objectid = int(objectid)
            habitat_class = str(props.get("FIRST_ClassLv2") or "Not Classified")
            clipped = geom.intersection(named_union)
            if clipped.is_empty or clipped.area <= 0:
                continue
            all_objectids.add(objectid)
            class_objectids[habitat_class].add(objectid)
            class_intersections[habitat_class].append(clipped)
            if habitat_class == "Tidal Flats":
                tidal_flat_ids.add(objectid)

        class_summary = {}
        for habitat_class, geometries in sorted(class_intersections.items()):
            class_summary[habitat_class] = {
                "source_feature_count": len(class_objectids[habitat_class]),
                "unique_intersection_area_km2": _intersection_area_km2(geometries),
                "source_objectids": sorted(class_objectids[habitat_class]),
            }

        overlays[name] = {
            "context_id": context_id,
            "status": "charted_context_with_benthic_overlay_reviewed",
            "source_feature_count": len(source_features),
            "source_objectids": sorted(int((f.get("properties") or {})["OBJECTID"]) for f in source_features),
            "chart_cells": sorted({str((f.get("properties") or {}).get("DSNM")) for f in source_features if (f.get("properties") or {}).get("DSNM")}),
            "source_dates": sorted({str((f.get("properties") or {}).get("SORDAT")) for f in source_features if (f.get("properties") or {}).get("SORDAT")}),
            "charted_categories": sorted({str((f.get("properties") or {}).get("CATSEA")) for f in source_features if (f.get("properties") or {}).get("CATSEA") and str((f.get("properties") or {}).get("CATSEA")).strip()}),
            "charted_source_polygon_area_km2": _area_union_km2(source_geometries),
            "benthic_overlay": {
                "intersecting_source_feature_count": len(all_objectids),
                "habitat_classes": class_summary,
                "tidal_flat_source_feature_count": len(tidal_flat_ids),
                "tidal_flat_source_objectids": sorted(tidal_flat_ids),
            },
            "interpretation": (
                "Overlay describes mapped source polygons intersecting an old charted named-water area. "
                "It does not establish current habitat condition, fish presence, water connectivity, or navigation limits."
            ),
        }

    tidal_flat_features = []
    tidal_flat_inside_preserve = set()
    tidal_flat_outside_preserve = set()
    tidal_flat_area = []
    for feature, geom in zip(benthic_features, benthic_geometries):
        props = feature.get("properties") or {}
        if props.get("FIRST_ClassLv2") != "Tidal Flats" or not geom.intersects(footprint_union):
            continue
        objectid = int(props["OBJECTID"])
        if preserve_geom is not None and geom.intersects(preserve_geom):
            tidal_flat_inside_preserve.add(objectid)
        else:
            tidal_flat_outside_preserve.add(objectid)
        tidal_flat_area.append(geom.intersection(footprint_union))
        output_feature = {
            "type": "Feature",
            "id": f"fwc-tidal-flat-{objectid}",
            "geometry": feature["geometry"],
            "properties": {
                **props,
                "lupita_patch_id": f"fwc-tidal-flat-{objectid}",
                "candidate_status": "mapped_tidal_flat_source_polygon_not_named_flat_or_current_habitat",
                "source_service": "https://gis.myfwc.com/hosting/rest/services/Projects_FWC/UnifiedReefMapProject_v2_2/MapServer/7",
                "source_geometry_preserved": True,
            },
        }
        tidal_flat_features.append(output_feature)

    tidal_collection = {
        "type": "FeatureCollection",
        "name": "lupita_biscayne_tidal_flat_source_patches",
        "metadata": {
            "source": "FWC Unified Reef Map Level 1, source records attributed to Biscayne Bay FWC/NPS",
            "source_layer_id": 7,
            "output_crs": "EPSG:4326",
            "source_feature_count": len(tidal_flat_features),
            "geometry_policy": "Original mapped source polygons are preserved individually. No dissolve, clustering, gap filling, or invented named-flat boundary is performed.",
            "limitations": [
                "Source-map footprints are coverage extents, not ecological bay boundaries.",
                "Mapped Tidal Flats class does not establish present-day substrate, exposure, accessibility, or fish suitability.",
                "A patch outside the FDEP Biscayne Bay Aquatic Preserve is not thereby outside the ecological bay.",
                "Source mapping dates vary by project and must be retained for any later temporal analysis.",
            ],
        },
        "features": tidal_flat_features,
    }

    subregions = []
    for item in SUBREGIONS:
        subregions.append({
            **item,
            "feature_type": "bay_subregion",
            "parent_id": "sf-biscayne-bay-ecological-context",
            "geometry": None,
            "geometry_status": "literature_landmarks_identified_cross_bay_boundary_geometry_pending",
            "boundary_basis": "peer_reviewed_ecological_region_description",
            "boundary_scope_note": (
                item["boundary_note"] + " The cited paper provides landmark limits, not digitized cross-bay boundary lines. "
                "No polygon is fabricated; landmark geometry and boundary placement remain pending GIS validation."
            ),
            "provenance": [{
                "publisher": "Frontiers in Marine Science",
                "title": "Characterizing Nearshore Fish Assemblages From Intact and Altered Mangrove Shorelines in Biscayne Bay, Florida, United States",
                "url": ARTICLE_URL,
                "source_type": "peer_reviewed_ecological_subregion_definition",
                "published": "2022-07-22",
            }],
            "validation_status": "literature_extent_supported_boundary_geometry_pending",
        })

    preserve_intersection_count = len(tidal_flat_inside_preserve)
    report = {
        "audit_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "research_candidate_inventory_boundary_geometry_pending",
        "area_crs": AREA_CRS,
        "benthic_geometry_repairs_for_analysis_only": {
            "count": len(repaired_benthic_objectids),
            "objectids": sorted(repaired_benthic_objectids),
            "note": "Invalid source polygons are preserved unchanged in source records. make_valid() is used only for overlay calculations; repaired geometries are not substituted into the source GeoJSON.",
        },
        "purpose": "Research-only ecological subregion and mapped benthic habitat candidate audit. No production model inputs.",
        "subregions": subregions,
        "named_chart_context_overlays": overlays,
        "tidal_flat_patch_inventory": {
            "source_layer_id": 7,
            "source_feature_count_within_source_footprints": len(tidal_flat_features),
            "unique_intersection_area_km2_with_source_footprints": _intersection_area_km2(tidal_flat_area),
            "feature_count_intersecting_fdep_biscayne_preserve_objectid_43": preserve_intersection_count,
            "feature_count_not_intersecting_fdep_biscayne_preserve_objectid_43": len(tidal_flat_outside_preserve),
            "source_objectids": sorted(int(f["properties"]["OBJECTID"]) for f in tidal_flat_features),
            "geometry_file": "data/spatial/biscayne-tidal-flat-patches.geojson",
            "interpretation": "These are individually mapped source patches, not named or dissolved flat complexes. Preserve boundary intersection is a management overlay only.",
        },
        "source_footprints": {
            "feature_count": len(footprint_geometries),
            "meaning": "Source-map coverage only; not a bay or ecological boundary.",
        },
        "fdep_preserve_reference": {
            "objectid": 43,
            "name": "Biscayne Bay",
            "role": "statutory_management_boundary_reference_only",
            "not_used_as_ecological_subregion_boundary": True,
        },
        "guardrails": [
            "North/Central/South are literature-defined ecological contexts, not statutory or management regions.",
            "Their landmark limits are not yet digitized into cross-bay lines or polygons.",
            "NOAA ENC named-water polygons remain source chart context, not complete ecological boundaries.",
            "FWC/NPS benthic overlays are source mapping evidence, not current species-suitability scores.",
            "No channel, inlet, tidal connection, or fish passage is inferred from polygon proximity.",
            "All outputs are research-only; no species files, prediction weights, thresholds, or production APIs are modified.",
        ],
    }
    return report, tidal_collection


def run(
    benthic_path: Path,
    footprints_path: Path,
    preserves_path: Path,
    named_water_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    report, tidal_collection = build_audit(
        read_collection(benthic_path),
        read_collection(footprints_path),
        read_collection(preserves_path),
        read_collection(named_water_path),
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "biscayne-subregion-habitat-audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (output_dir / "biscayne-tidal-flat-patches.geojson").write_text(
        json.dumps(tidal_collection, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benthic", type=Path, default=Path("artifacts/biscayne-gis/unified_benthic_polygons.geojson"))
    parser.add_argument("--footprints", type=Path, default=Path("artifacts/biscayne-gis/source_footprints.geojson"))
    parser.add_argument("--preserves", type=Path, default=Path("data/spatial/research/noaa_cmp/overlay/fdep_biscayne_aquatic_preserves.geojson"))
    parser.add_argument("--named-water", type=Path, default=Path("data/spatial/noaa-biscayne-named-water-areas.geojson"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/spatial"))
    args = parser.parse_args()
    report = run(args.benthic, args.footprints, args.preserves, args.named_water, args.output_dir)
    print(f"Subregions: {len(report['subregions'])}")
    print(f"Named chart contexts: {len(report['named_chart_context_overlays'])}")
    print(f"Tidal-flat source patches: {report['tidal_flat_patch_inventory']['source_feature_count_within_source_footprints']}")
    print(f"Audit: {args.output_dir / 'biscayne-subregion-habitat-audit.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
