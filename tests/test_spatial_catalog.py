import json
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
    assert "static_import_pending" in bear["geometry_status"]
    assert flats["source_geometry_ref"]["objectids"] == [246316, 246317, 246323]
    assert flats["source_geometry_ref"]["charted_category"] == "mud flats"
    assert flats["geometry"] is None
    assert safety["source_geometry_ref"]["objectids"] == [246300, 246319, 246322, 253421]
    assert safety["feature_type"] == "named_water_area_complex"
    assert government["geometry"] is None
    assert government["geometry_status"] == "name_documented_no_direct_named_feature_geometry_identified_in_extracted_layers"
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
    assert index["channel_features"]["Miami Harbor Channel fairway"]["feature_count"] == 44
    assert "not_identified" in index["channel_features"]["Government Cut"]["status"]
