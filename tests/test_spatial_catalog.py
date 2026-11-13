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
