"""Curate selected NOAA named-water source geometries for the South Florida pilot.

This preserves source features individually. It does not dissolve chart fragments into
an ecological, statutory, habitat, or navigational boundary.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from shapely.geometry import shape
from shapely.ops import unary_union

SOURCE_URL = (
    "https://encdirect.noaa.gov/arcgis/rest/services/"
    "encdirect/enc_harbour/MapServer/237"
)
CONTEXTS = {
    "Biscayne Bay": ("sf-biscayne-bay-ecological-context", "charted_named_water_area_source_fragment"),
    "Safety Valve": ("sf-biscayne-safety-valve-complex", "charted_named_water_area_source_polygon"),
    "Biscayne Flats": ("sf-biscayne-flats", "charted_named_mud_flat_source_polygon"),
    "Bear Cut": ("sf-bear-cut", "charted_named_water_area_polygon"),
    "Norris Cut": ("sf-norris-cut", "charted_named_water_area_polygon"),
    "Black Ledge": ("sf-biscayne-black-ledge", "charted_ledge_source_polygon"),
    "Featherbed Bank": ("sf-featherbed-bank", "charted_bank_source_polygon"),
    "Lewis Cut": ("sf-lewis-cut", "charted_named_waterway_source_polygon"),
    "Biscayne Channel": ("sf-biscayne-channel", "charted_sea_channel_source_polygon"),
    "Sands Cut": ("sf-sands-cut", "charted_named_waterway_source_polygon"),
    "Snapper Creek Canal": ("sf-snapper-creek-canal", "charted_canal_source_polygon"),
    "Goulds Canal": ("sf-goulds-canal", "charted_canal_source_polygon"),
    "Deering Channel": ("sf-deering-channel", "charted_sea_channel_source_polygon"),
    "Cape Florida Channel": ("sf-cape-florida-channel", "charted_sea_channel_source_polygon"),
}
EXPECTED_COUNTS = {
    "Biscayne Bay": 37,
    "Safety Valve": 4,
    "Biscayne Flats": 3,
    "Bear Cut": 1,
    "Norris Cut": 1,
    "Black Ledge": 3,
    "Featherbed Bank": 1,
    "Lewis Cut": 1,
    "Biscayne Channel": 2,
    "Sands Cut": 1,
    "Snapper Creek Canal": 1,
    "Goulds Canal": 1,
    "Deering Channel": 1,
    "Cape Florida Channel": 2,
}


def curate(source_path: Path, output_dir: Path) -> dict[str, Any]:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    selected = []
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for feature in source.get("features", []):
        props = feature.get("properties") or {}
        name = props.get("OBJNAM")
        if name not in CONTEXTS:
            continue
        context_id, role = CONTEXTS[name]
        curated = json.loads(json.dumps(feature))
        curated_props = curated.setdefault("properties", {})
        curated_props["lupita_context_id"] = context_id
        curated_props["lupita_geometry_role"] = role
        selected.append(curated)
        groups[name].append(curated)

    for name, expected in EXPECTED_COUNTS.items():
        if len(groups[name]) != expected:
            raise ValueError(f"{name}: expected {expected} source features, got {len(groups[name])}")

    audit_groups = {}
    for name, features in groups.items():
        geometries = [shape(feature["geometry"]) for feature in features]
        invalid = [
            feature["properties"].get("OBJECTID")
            for feature, geometry in zip(features, geometries)
            if not geometry.is_valid or geometry.is_empty
        ]
        overlaps = []
        for i, left in enumerate(geometries):
            for j in range(i + 1, len(geometries)):
                intersection = left.intersection(geometries[j])
                if not intersection.is_empty and intersection.area > 1e-12:
                    overlaps.append([
                        features[i]["properties"].get("OBJECTID"),
                        features[j]["properties"].get("OBJECTID"),
                    ])
        merged = unary_union(geometries)
        components = list(merged.geoms) if hasattr(merged, "geoms") else [merged]
        audit_groups[name] = {
            "context_id": CONTEXTS[name][0],
            "feature_count": len(features),
            "objectids": sorted(feature["properties"].get("OBJECTID") for feature in features),
            "chart_cells": sorted({feature["properties"].get("DSNM") for feature in features}),
            "source_dates": sorted({feature["properties"].get("SORDAT") for feature in features}),
            "geometry_types": sorted({feature["geometry"]["type"] for feature in features}),
            "invalid_or_empty_objectids": invalid,
            "positive_area_overlap_pairs": overlaps,
            "union_geometry_type": merged.geom_type,
            "connected_component_count": len(components),
            "component_bounds_wgs84": [list(component.bounds) for component in components],
            "dissolved_geometry_persisted": False,
            "interpretation": (
                "Source chart features only; no complete ecological, statutory, habitat, "
                "or navigational boundary is asserted."
            ),
        }

    output_dir.mkdir(parents=True, exist_ok=True)
    collection = {
        "type": "FeatureCollection",
        "name": "lupita_noaa_biscayne_named_water_source_geometries",
        "metadata": {
            "source": "NOAA ENC Direct to GIS, Harbor.Sea_Area_Named_Water_Area",
            "source_url": SOURCE_URL,
            "output_crs": "OGC:CRS84 / EPSG:4326",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "source_feature_count": len(selected),
            "geometry_policy": (
                "Original source geometries are preserved individually. No dissolve, gap filling, "
                "boundary interpolation, or ecological/legal boundary claim is made."
            ),
            "limitations": [
                "NOAA ENC Direct to GIS is not certified for navigation.",
                "Source chart dates range from 2002 to 2011.",
                "Charted named-water polygons are not complete ecological or statutory boundaries.",
                "Charted mud-flat classification does not establish current substrate or habitat suitability.",
            ],
        },
        "features": selected,
    }
    geojson_path = output_dir / "noaa-biscayne-named-water-areas.geojson"
    geojson_path.write_text(json.dumps(collection, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")

    audit = {
        "audit_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_url": SOURCE_URL,
        "source_layer_id": 237,
        "source_crs": "EPSG:4326",
        "curated_geojson_path": "data/spatial/noaa-biscayne-named-water-areas.geojson",
        "source_feature_count": len(selected),
        "groups": audit_groups,
        "guardrails": [
            "Connected components are a geometric precheck, not proof of a complete waterbody boundary.",
            "A one-component union does not establish ecological connectivity or habitat classification.",
            "Disconnected fragments are not bridged or filled.",
            "All source features remain individually available in the curated GeoJSON.",
            "Bear Cut remains a charted named-water polygon, not a channel centerline or controlling-depth boundary.",
        ],
    }
    audit_path = output_dir / "noaa-biscayne-named-water-topology-audit.json"
    audit_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    catalog_path = output_dir / "feature-catalog.json"
    if catalog_path.exists():
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        by_id = {feature["id"]: feature for feature in catalog["features"]}
        for name, group in audit_groups.items():
            feature = by_id[CONTEXTS[name][0]]
            ref = feature.setdefault("source_geometry_ref", {})
            ref["curated_geojson_path"] = "data/spatial/noaa-biscayne-named-water-areas.geojson"
            ref["topology_audit_path"] = "data/spatial/noaa-biscayne-named-water-topology-audit.json"
            ref["source_objectids"] = group["objectids"]
            ref["source_feature_count"] = group["feature_count"]
            ref["chart_cells"] = group["chart_cells"]
            ref["source_dates"] = group["source_dates"]
            ref["connected_component_count"] = group["connected_component_count"]
            ref["positive_area_overlap_pairs"] = group["positive_area_overlap_pairs"]
            if name in {"Bear Cut", "Norris Cut"}:
                ref["geojson_feature_id"] = str(group["objectids"][0])
                feature["geometry_status"] = "source_geometry_persisted_topology_precheck_passed_not_navigation_boundary"
                feature["validation_status"] = "charted_named_water_geometry_persisted_topology_precheck_passed_not_navigation_boundary"
                note = feature["boundary_scope_note"]
                note = note.replace(
                    "Geometry is retrieved and coordinate-validated; static geometry import and topology review remain pending.",
                    ""
                )
                if name == "Norris Cut":
                    ref.update({
                        "review_status": "direct_named_water_area_polygon_persisted_channel_centerline_pending",
                        "source_layer_id": 237,
                        "objectid": 253447,
                        "chart_cell": "US5MIACC.000",
                        "source_chart": "NOAA Chart 11468",
                        "source_date": "2004-01",
                        "geometry_type": "Polygon",
                        "bbox_wgs84": [-80.1498818, 25.7503267, -80.1396955, 25.7620415],
                    })
                    source_provenance = {
                        "publisher": "NOAA Office of Coast Survey",
                        "title": "NOAA Harbour ENC named-water polygon, Norris Cut, OBJECTID 253447, Chart 11468",
                        "url": SOURCE_URL,
                        "source_type": "charted_named_water_area_geometry",
                    }
                    provenance = feature.setdefault("provenance", [])
                    if not any(
                        item.get("source_type") == source_provenance["source_type"]
                        and item.get("title") == source_provenance["title"]
                        for item in provenance
                    ):
                        provenance.append(source_provenance)
                    note = note.replace(
                        "The current structured Harbour ENC extraction did not return a directly named Norris Cut geometry. Do not borrow geometry from nearby channel features.",
                        "NOAA Harbour ENC layer 237 directly returns a named-water polygon for Norris Cut (OBJECTID 253447, Chart 11468, source date 2004-01)."
                    )
                    note = note.replace(
                        " The original source polygon is persisted in the curated GeoJSON and passed geometry validation. It remains a charted named-water area, not a surveyed centerline or depth boundary.",
                        ""
                    )
                    if "Norris Cut source polygon is persisted in the curated GeoJSON" not in note:
                        note = note.rstrip() + (
                            " The Norris Cut source polygon is persisted in the curated GeoJSON and passed geometry validation. "
                            "The full inlet channel centerline and current controlling-depth boundary remain unverified."
                        )
                elif "original source polygon is persisted in the curated geojson" not in note.lower():
                    note = note.rstrip() + (
                        " The original source polygon is persisted in the curated GeoJSON and passed geometry validation. "
                        "It remains a charted named-water area, not a surveyed centerline or depth boundary."
                    )
                feature["boundary_scope_note"] = note
            else:
                feature["geometry_status"] = (
                    "source_chart_fragments_persisted_topology_precheck_passed_complete_boundary_unverified"
                    if name == "Biscayne Bay"
                    else "source_chart_fragments_persisted_topology_precheck_passed_boundary_unverified"
                )
                feature["validation_status"] = "source_fragments_persisted_mosaic_not_promoted_to_boundary"
                note = feature["boundary_scope_note"]
                if name == "Biscayne Bay":
                    if "A first geometric topology precheck is complete:" not in note:
                        note = note.replace(
                            "mosaic and topology review is pending.",
                            "a first geometric topology precheck is complete: the union has two disconnected components, "
                            "one a very small isolated fragment. Full boundary reconciliation remains pending."
                        )
                        note = note.rstrip() + (
                            " Original chart fragments are persisted individually; no dissolved or complete boundary is promoted."
                        )
                elif "A first geometric topology precheck found one connected component" not in note:
                    if name == "Safety Valve":
                        note = note.rstrip() + (
                            " A first geometric topology precheck found one connected component and no material overlaps. "
                            "Source polygons remain separate; this does not establish ecological connectivity or current habitat."
                        )
                    elif name == "Biscayne Flats":
                        note = note.rstrip() + (
                            " A first geometric topology precheck found one connected component and no material overlaps. "
                            "Source polygons remain separate; the charted mud-flat class does not establish current substrate or habitat."
                        )
                    else:
                        note = note.rstrip() + (
                            " A first geometric topology precheck found one connected component and no material overlaps. "
                            "Source polygons remain separate; this does not establish current ecological connectivity, "
                            "habitat condition, channel centerline, or navigation boundary."
                        )
                feature["boundary_scope_note"] = note
        catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return audit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="artifacts/noaa-hydrography/harbor_named_water_areas.geojson")
    parser.add_argument("--output-dir", default="data/spatial")
    args = parser.parse_args()
    audit = curate(Path(args.source), Path(args.output_dir))
    for name, group in audit["groups"].items():
        print(
            f"{name}: {group['feature_count']} source features; "
            f"{group['connected_component_count']} connected component(s); "
            f"{len(group['positive_area_overlap_pairs'])} positive-area overlap pair(s)"
        )
    print(f"Persisted {audit['source_feature_count']} source geometries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
