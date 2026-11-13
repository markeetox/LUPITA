import json
import os
from pathlib import Path


CATALOG_PATH = Path(__file__).parents[1] / "data" / "spatial" / "feature-catalog.json"


def test_spatial_catalog_has_unique_stable_ids_and_valid_references():
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    features = catalog["features"]
    ids = [feature["id"] for feature in features]
    assert len(ids) == len(set(ids))
    known = set(ids)
    for feature in features:
        parent_id = feature.get("parent_id")
        assert parent_id is None or parent_id in known
        for relationship in feature.get("relationships", []):
            assert relationship["target_id"] in known


def test_unverified_features_do_not_claim_geometry_or_verified_boundaries():
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    for feature in catalog["features"]:
        if feature.get("geometry") is None:
            assert feature.get("geometry_status")
            assert feature.get("validation_status") != "verified"
        else:
            assert feature["geometry"]["type"] in {
                "Polygon", "MultiPolygon", "LineString",
                "MultiLineString", "Point", "MultiPoint",
            }


def test_legal_preserve_and_ecological_bay_are_distinct_entities():
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    by_id = {feature["id"]: feature for feature in catalog["features"]}
    preserve = by_id["sf-biscayne-bay-aquatic-preserve"]
    bay = by_id["sf-biscayne-bay-ecological-context"]
    assert preserve["feature_type"] == "protected_waterbody_boundary"
    assert bay["feature_type"] == "ecological_waterbody"
    assert preserve["id"] != bay["id"]
    assert preserve["geometry"] is None
    assert bay["geometry"] is None


def test_biscayne_gis_inventory_is_explicitly_source_coverage_not_bay_boundary():
    inventory_path = Path(__file__).parents[1] / "data" / "spatial" / "biscayne-bay-gis-inventory.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    footprints = inventory["source_footprints"]
    assert footprints["feature_count"] == 2
    assert footprints["meaning"].startswith("Source-map coverage footprints")
    benthic = inventory["unified_benthic_polygons"]
    assert benthic["feature_count"] == 7222
    assert benthic["class_counts"]["Seagrass (Continuous)"] > 0
    assert inventory["first_spatial_qa"]["feature_footprint_nonintersection_count"] > 0


def test_cape_florida_preserve_is_separate_from_biscayne_bay_preserve():
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    by_id = {feature["id"]: feature for feature in catalog["features"]}
    biscayne = by_id["sf-biscayne-bay-aquatic-preserve"]
    cape = by_id["sf-cape-florida-aquatic-preserve"]
    assert biscayne["source_geometry"]["objectid"] == 43
    assert cape["source_geometry"]["objectid"] == 25
    assert cape["source_geometry"]["reported_acres"] < biscayne["source_geometry"]["reported_acres"]
    assert "separate preserve" in cape["boundary_scope_note"].lower()
    assert cape["id"] != biscayne["id"]


def test_noaa_charted_features_preserve_source_ids_and_unverified_geometry_states():
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    by_id = {feature["id"]: feature for feature in catalog["features"]}
    bear = by_id["sf-bear-cut"]
    flats = by_id["sf-biscayne-flats"]
    safety = by_id["sf-biscayne-safety-valve-complex"]
    government = by_id["sf-government-cut"]
    harbor = by_id["sf-miami-harbor-channel-system"]
    assert bear["source_geometry_ref"]["objectid"] == 253451
    assert bear["geometry"] is None
    assert "source_geometry_persisted" in bear["geometry_status"]
    assert bear["source_geometry_ref"]["curated_geojson_path"] == "data/spatial/noaa-biscayne-named-water-areas.geojson"
    norris = by_id["sf-norris-cut"]
    if "source_geometry_persisted" in norris["geometry_status"]:
        assert norris["source_geometry_ref"]["geojson_feature_id"] == "253447"
        if os.getenv("LUPITA_REQUIRE_CURATED_GIS") == "1":
            assert norris["source_geometry_ref"]["review_status"] == "direct_named_water_area_polygon_persisted_channel_centerline_pending"
            assert norris["source_geometry_ref"]["source_layer_id"] == 237
            assert norris["source_geometry_ref"]["objectid"] == 253447
            assert norris["source_geometry_ref"]["source_chart"] == "NOAA Chart 11468"
            assert norris["source_geometry_ref"]["source_date"] == "2004-01"
            assert "Norris Cut source polygon is persisted in the curated GeoJSON" in norris["boundary_scope_note"]
    assert flats["source_geometry_ref"]["objectids"] == [246316, 246317, 246323]
    assert flats["source_geometry_ref"]["charted_category"] == "mud flats"
    assert flats["geometry"] is None
    assert safety["source_geometry_ref"]["objectids"] == [246300, 246319, 246322, 253421]
    assert safety["feature_type"] == "named_water_area_complex"
    assert government["geometry"] is None
    assert government["geometry_status"] == "name_documented_no_direct_named_feature_geometry_identified_in_extracted_layers"
    assert government["source_geometry_ref"]["fairway_layer_id"] == 208
    assert government["source_geometry_ref"]["fairway_objectids"] == [42416, 42420, 42422]
    assert harbor["source_geometry_ref"]["objectids"]
    assert len(harbor["source_geometry_ref"]["objectids"]) == 44


def test_noaa_hydrography_index_records_charted_feature_provenance():
    index_path = Path(__file__).parents[1] / "data" / "spatial" / "noaa-biscayne-hydrography-index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    named = index["named_water_features"]
    assert named["Biscayne Bay"]["feature_count"] == 37
    assert named["Safety Valve"]["feature_count"] == 4
    assert named["Biscayne Flats"]["charted_category"] == "mud flats"
    assert named["Bear Cut"]["objectids"] == [253451]
    assert named["Bear Cut"]["geometry_type"] == "Polygon"
    assert named["Norris Cut"]["objectids"] == [253447]
    assert named["Norris Cut"]["source_chart"] == "NOAA Chart 11468"
    assert named["Black Ledge"]["objectids"] == [246297, 246304, 246318]
    assert named["Featherbed Bank"]["objectids"] == [246301]
    assert named["Lewis Cut"]["objectids"] == [246302]
    assert named["Biscayne Channel"]["objectids"] == [253424, 253427]
    assert named["Cape Florida Channel"]["objectids"] == [253420, 253432]
    context_layers = index["charted_context_layer_inventory"]["layers"]
    assert context_layers["harbor_coastline_lines"]["review_window_intersections"] == 47
    assert context_layers["harbor_depth_contour_lines"]["review_window_intersections"] == 294
    assert context_layers["harbor_vegetation_areas"]["charted_category"] == "mangroves"
    assert index["channel_features"]["Miami Harbor Channel fairway"]["feature_count"] == 44
    assert "not_identified" in index["channel_features"]["Government Cut"]["status"]
    assert "direct_named_water_area_polygon_found" in index["channel_features"]["Norris Cut"]["status"]
    route_layers = index["route_layer_inventory"]
    assert route_layers["harbor_fairway_areas"]["feature_count"] == 62
    assert route_layers["harbor_fairway_areas"]["miami_harbor_channel_objectids"] == [42416, 42420, 42422]
    assert route_layers["harbor_deep_water_route_parts"]["feature_count"] == 0
    assert route_layers["harbor_two_way_route_parts"]["feature_count"] == 0
    assert route_layers["harbor_recommended_route_centerlines"]["feature_count"] == 0



def test_curated_noaa_named_water_geometries_and_topology_audit_are_persisted():
    spatial_dir = Path(__file__).parents[1] / "data" / "spatial"
    geojson = json.loads((spatial_dir / "noaa-biscayne-named-water-areas.geojson").read_text(encoding="utf-8"))
    audit = json.loads((spatial_dir / "noaa-biscayne-named-water-topology-audit.json").read_text(encoding="utf-8"))
    catalog = json.loads((spatial_dir / "feature-catalog.json").read_text(encoding="utf-8"))

    norris_persisted = "source_geometry_persisted" in next(
        feature for feature in catalog["features"] if feature["id"] == "sf-norris-cut"
    )["geometry_status"]
    expected_count = 59 if norris_persisted else 58
    assert geojson["metadata"]["source_feature_count"] == expected_count
    assert len(geojson["features"]) == expected_count
    by_name = {}
    for feature in geojson["features"]:
        by_name.setdefault(feature["properties"]["OBJNAM"], []).append(feature)
    assert len(by_name["Biscayne Bay"]) == 37
    assert len(by_name["Safety Valve"]) == 4
    assert len(by_name["Biscayne Flats"]) == 3
    assert len(by_name["Bear Cut"]) == 1
    if norris_persisted:
        assert len(by_name["Norris Cut"]) == 1
    else:
        assert "Norris Cut" not in by_name
    assert len(by_name["Black Ledge"]) == 3
    assert len(by_name["Featherbed Bank"]) == 1
    assert len(by_name["Lewis Cut"]) == 1
    assert len(by_name["Biscayne Channel"]) == 2
    assert len(by_name["Sands Cut"]) == 1
    assert len(by_name["Snapper Creek Canal"]) == 1
    assert len(by_name["Goulds Canal"]) == 1
    assert len(by_name["Deering Channel"]) == 1
    assert len(by_name["Cape Florida Channel"]) == 2

    for feature_name in (
        "Black Ledge", "Featherbed Bank", "Lewis Cut", "Biscayne Channel",
        "Sands Cut", "Snapper Creek Canal", "Goulds Canal", "Deering Channel",
        "Cape Florida Channel",
    ):
        assert audit["groups"][feature_name]["connected_component_count"] == 1
        assert audit["groups"][feature_name]["positive_area_overlap_pairs"] == []
    by_id = {feature["id"]: feature for feature in catalog["features"]}
    for feature_id in (
        "sf-biscayne-black-ledge", "sf-featherbed-bank", "sf-lewis-cut",
        "sf-biscayne-channel", "sf-sands-cut", "sf-snapper-creek-canal",
        "sf-goulds-canal", "sf-deering-channel", "sf-cape-florida-channel",
    ):
        note = by_id[feature_id]["boundary_scope_note"].lower()
        assert "mud-flat class" not in note
        assert by_id[feature_id]["geometry"] is None
        assert by_id[feature_id]["source_geometry_ref"]["source_feature_count"] >= 1
    assert catalog["geometry_policy"]["parent_id_semantics"].startswith("parent_id is a catalog grouping")
    assert by_id["sf-biscayne-black-ledge"]["relationships"][0]["type"] == "located_within"
    assert by_id["sf-biscayne-channel"]["relationships"][0]["type"] == "overlaps"
    for feature_id in ("sf-lewis-cut", "sf-sands-cut", "sf-snapper-creek-canal", "sf-goulds-canal"):
        assert by_id[feature_id]["relationships"][0]["type"] == "adjacent_to"
        assert "no positive-area overlap" in by_id[feature_id]["relationships"][0]["status"]

    bear = by_name["Bear Cut"][0]
    assert str(bear["properties"]["OBJECTID"]) == "253451"
    assert bear["properties"]["lupita_context_id"] == "sf-bear-cut"
    assert bear["geometry"]["type"] == "Polygon"

    assert audit["groups"]["Biscayne Bay"]["connected_component_count"] == 2
    assert audit["groups"]["Biscayne Bay"]["positive_area_overlap_pairs"] == []
    assert audit["groups"]["Safety Valve"]["connected_component_count"] == 1
    assert audit["groups"]["Biscayne Flats"]["connected_component_count"] == 1
    assert audit["groups"]["Bear Cut"]["objectids"] == [253451]
    assert audit["groups"]["Bear Cut"]["dissolved_geometry_persisted"] is False
    if norris_persisted:
        assert audit["groups"]["Norris Cut"]["objectids"] == [253447]
        assert audit["groups"]["Norris Cut"]["connected_component_count"] == 1
