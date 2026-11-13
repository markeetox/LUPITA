import json

from scripts.build_biscayne_subregion_candidates import build_audit


def polygon_feature(objectid, name, cls, coords, source="Biscayne Bay FWC"):
    return {
        "type": "Feature",
        "id": objectid,
        "properties": {
            "OBJECTID": objectid,
            "OBJNAM": name,
            "FIRST_Source": source,
            "FIRST_ClassLv2": cls,
            "FIRST_ClassLv4": cls,
            "DSNM": "TEST.000",
            "SORDAT": "2020-01-01",
            "CATSEA": "mud flats" if name == "Biscayne Flats" else "",
        },
        "geometry": {"type": "Polygon", "coordinates": [coords]},
    }


def collection(features):
    return {"type": "FeatureCollection", "features": features}


def test_build_audit_keeps_literature_subregions_without_fabricated_polygons():
    benthic = collection([
        polygon_feature(1, None, "Tidal Flats", [
            [-80.20, 25.50], [-80.19, 25.50], [-80.19, 25.51],
            [-80.20, 25.50],
        ])
    ])
    footprints = collection([
        polygon_feature(100, None, "footprint", [
            [-80.30, 25.40], [-80.10, 25.40], [-80.10, 25.60],
            [-80.30, 25.40],
        ])
    ])
    preserves = collection([
        polygon_feature(43, None, "preserve", [
            [-80.25, 25.45], [-80.15, 25.45], [-80.15, 25.55],
            [-80.25, 25.45],
        ])
    ])
    named = collection([
        polygon_feature(200, "Biscayne Flats", "chart", [
            [-80.22, 25.48], [-80.18, 25.48], [-80.18, 25.53],
            [-80.22, 25.48],
        ])
    ])

    report, patches = build_audit(benthic, footprints, preserves, named)

    assert [item["name"] for item in report["subregions"]] == [
        "North Biscayne Bay", "Central Biscayne Bay", "South Biscayne Bay"
    ]
    assert all(item["geometry"] is None for item in report["subregions"])
    assert report["subregions"][1]["north_limit"] == "Rickenbacker Causeway"
    assert report["subregions"][2]["south_limit"] == "Card Sound / Jewfish Creek"
    assert report["named_chart_context_overlays"]["Biscayne Flats"]["benthic_overlay"]["tidal_flat_source_feature_count"] == 1
    assert patches["metadata"]["source_feature_count"] == 1
    assert patches["features"][0]["id"] == "fwc-tidal-flat-1"
    assert patches["features"][0]["geometry"] == benthic["features"][0]["geometry"]
    assert report["tidal_flat_patch_inventory"]["feature_count_intersecting_fdep_biscayne_preserve_objectid_43"] == 1


def test_build_audit_does_not_promote_unmatched_named_water_context():
    benthic = collection([])
    footprints = collection([
        polygon_feature(100, None, "footprint", [
            [-80.30, 25.40], [-80.10, 25.40], [-80.10, 25.60],
            [-80.30, 25.40],
        ])
    ])
    preserves = collection([])
    named = collection([])
    report, patches = build_audit(benthic, footprints, preserves, named)
    item = report["named_chart_context_overlays"]["Biscayne Flats"]
    assert item["status"] == "source_feature_not_found"
    assert patches["features"] == []
    assert report["tidal_flat_patch_inventory"]["source_feature_count_within_source_footprints"] == 0


def test_invalid_benthic_source_geometry_is_repaired_only_for_analysis():
    benthic = collection([
        polygon_feature(7, None, "Seagrass (Continuous)", [
            [-80.21, 25.49], [-80.19, 25.51], [-80.21, 25.51],
            [-80.19, 25.49], [-80.21, 25.49],
        ])
    ])
    footprints = collection([
        polygon_feature(100, None, "footprint", [
            [-80.30, 25.40], [-80.10, 25.40], [-80.10, 25.60],
            [-80.30, 25.40],
        ])
    ])
    preserves = collection([])
    named = collection([
        polygon_feature(200, "Biscayne Flats", "chart", [
            [-80.22, 25.48], [-80.18, 25.48], [-80.18, 25.53],
            [-80.22, 25.48],
        ])
    ])
    report, _ = build_audit(benthic, footprints, preserves, named)
    assert report["benthic_geometry_repairs_for_analysis_only"]["objectids"] == [7]
    assert report["named_chart_context_overlays"]["Biscayne Flats"]["benthic_overlay"]["intersecting_source_feature_count"] == 1
