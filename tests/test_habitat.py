import numpy as np

from pipeline import habitat, layers


LATS = np.round(np.arange(25.0, 25.1001, 0.02), 4)
LONS = np.round(np.arange(-80.2, -80.1001, 0.02), 4)


def _square(lon0, lat0, lon1, lat1):
    return [[lon0, lat0], [lon1, lat0], [lon1, lat1], [lon0, lat1], [lon0, lat0]]


def _feature(class_name, ring, source="Test source"):
    return {"attributes": {"FIRST_ClassLv0": class_name, "FIRST_Source": source},
            "geometry": {"rings": [ring]}}


def test_benthic_classes_are_rasterized_without_treating_unknown_as_absent():
    features = [
        _feature("Seagrass", _square(-80.201, 25.019, -80.179, 25.041)),
        _feature("Coral Reef and Hardbottom", _square(-80.181, 25.039, -80.159, 25.061)),
        _feature("Unconsolidated Sediment", _square(-80.161, 25.059, -80.139, 25.081)),
        _feature("Unclassified local habitat", _square(-80.141, 25.079, -80.119, 25.101)),
    ]

    result, stats = habitat.build_habitat_layers(features, LATS, LONS)

    assert set(result["covers"]) == {"seagrass", "hard_bottom", "soft_bottom"}
    assert np.count_nonzero(result["covers"]["seagrass"]) > 0
    assert np.count_nonzero(result["covers"]["hard_bottom"]) > 0
    assert np.count_nonzero(result["covers"]["soft_bottom"]) > 0
    assert np.count_nonzero(result["mapped_cover"]) >= 4
    assert stats["unknown_classes"] == {"Unclassified local habitat": 1}
    assert stats["geometry_feature_count"] == 4


def test_missing_class_field_does_not_drop_geometry_from_mapped_coverage():
    features = [{"attributes": {}, "geometry": {"rings": [
        _square(-80.201, 25.019, -80.179, 25.041)
    ]}}]

    result, stats = habitat.build_habitat_layers(features, LATS, LONS)

    assert result["covers"] == {}
    assert np.count_nonzero(result["mapped_cover"]) > 0
    assert stats["unknown_classes"] == {"<missing class>": 1}


def test_load_layers_records_benthic_source_and_separates_it_from_reef_structure(monkeypatch):
    sst = np.full((len(LATS), len(LONS)), 27.0)
    features = [_feature("Seagrass", _square(-80.201, 25.019, -80.179, 25.041))]
    monkeypatch.setattr(layers, "_fetch_grid",
                        lambda cfg, region, fetch: (LATS, LONS, sst, "2026-11-12T00:00:00Z", None))
    monkeypatch.setattr(layers.arcgis, "query_all",
                        lambda url, region, **kwargs: features)

    sources = {
        "region": {"lat": [24.9, 25.2], "lon": [-80.3, -80.0]},
        "erddap": {"sst": {"dataset": "test-sst"}},
        "arcgis": {"unified_benthic": {
            "enabled": True, "url": "https://example.org/MapServer/10",
            "class_field": "FIRST_ClassLv0", "source_label": "FWC Unified Reef Map v2.2",
            "version": "2.2", "release_date": "2025-01"
        }},
        "closures": {"enabled": False}
    }
    errors = []

    result = layers.load_layers(sources, errors)

    assert errors == []
    assert "seagrass" in result["habitat_features"]
    assert result["habitat_info"]["dataset"] == "FWC Unified Reef Map v2.2"
    assert result["datasets"]["benthic_habitat"] == "FWC Unified Reef Map v2.2"
    assert result["structure_type"] is None
    assert result["habitat_mapped_cover"] is not None
