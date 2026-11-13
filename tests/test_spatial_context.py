from __future__ import annotations

import copy

from pipeline.spatial_context import load_catalog, validate_catalog, validate_geometry


def test_south_florida_spatial_catalog_is_valid():
    catalog = load_catalog()
    assert validate_catalog(catalog) == []


def test_catalog_has_distinct_bay_and_monitoring_station_features():
    catalog = load_catalog()
    features = {feature["id"]: feature for feature in catalog["features"]}
    assert features["biscayne-bay"]["feature_type"] == "bay"
    assert features["biscayne-bay"]["geometry"] is None
    assert features["biscayne-bay"]["geometry_status"] == "pending_authoritative_geometry"
    assert features["usgs-crest-brewster-reef"]["feature_type"] == "monitoring_station"
    assert features["fwc-flkeys-lka57"]["feature_type"] == "monitoring_station"
    assert features["fwc-flkeys-lka57"]["vertical_support"]["sensor_depth_m"] == 23


def test_duplicate_feature_ids_are_rejected():
    catalog = load_catalog()
    catalog["features"].append(copy.deepcopy(catalog["features"][0]))
    assert any("duplicate feature id" in error for error in validate_catalog(catalog))


def test_relationship_targets_must_resolve():
    catalog = load_catalog()
    catalog["features"][0]["relationships"] = [{"type": "connects_to", "target_id": "missing-inlet"}]
    assert any("does not resolve" in error for error in validate_catalog(catalog))


def test_verified_geometry_cannot_be_missing():
    catalog = load_catalog()
    catalog["features"][0]["geometry_status"] = "verified"
    assert any("cannot claim verified/provisional" in error for error in validate_catalog(catalog))


def test_geojson_coordinates_are_validated():
    assert validate_geometry({"type": "Point", "coordinates": [-80.1, 25.5]}) == []
    assert validate_geometry({"type": "Point", "coordinates": [181, 25.5]})
    assert validate_geometry({"type": "LineString", "coordinates": [[-80, 25]]})
    assert validate_geometry({
        "type": "Polygon",
        "coordinates": [[[-80, 25], [-79, 25], [-79, 26], [-80, 25]]]
    }) == []
    assert validate_geometry({
        "type": "Polygon",
        "coordinates": [[[-80, 25], [-79, 25], [-79, 26], [-80, 26]]]
    })


def test_unknown_is_not_absence_for_unmapped_bay_geometry():
    catalog = load_catalog()
    bay = next(feature for feature in catalog["features"] if feature["id"] == "biscayne-bay")
    assert bay["geometry"] is None
    assert bay["geometry_status"] == "pending_authoritative_geometry"
    assert "not use for point-in-polygon" in bay["provenance"]["notes"]
