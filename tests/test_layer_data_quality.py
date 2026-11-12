import numpy as np

from pipeline.run import build_data_quality


def _sources():
    return {
        "erddap": {
            "sst": {"enabled": True, "dataset": "sst-test"},
            "chlorophyll": {"enabled": True, "dataset": "chl-test"},
            "bathymetry": {"enabled": True, "dataset": "etopo-test", "stride": {"latitude": 15, "longitude": 15}},
            "currents": {"enabled": True, "dataset": "currents-test"},
        },
        "arcgis": {
            "artificial_reefs": {"enabled": True},
            "natural_reef": {"enabled": True},
            "unified_benthic": {"enabled": True},
        },
        "closures": {"enabled": True},
    }


def test_data_quality_reports_loaded_layers_and_gapfilled_usage():
    layers = {
        "sst_c": np.array([[28.0, 29.0], [np.nan, 30.0]]),
        "times": {"sst": "2026-11-12T12:00:00Z"},
        "chlorophyll_info": {
            "primary_dataset": "chl-test", "primary_loaded": True,
            "primary_source_grid_shape": [4, 4], "primary_source_valid_fraction": 0.2,
            "primary_aligned_grid_shape": [2, 2], "primary_aligned_valid_fraction": 0.2,
            "gapfilled_dataset": "chl-gapfilled-test", "gapfilled_attempted": True,
            "gapfilled_loaded": True, "gapfilled_used": True,
            "primary_time": "2026-11-10T12:00:00Z",
            "gapfilled_time": "2026-11-11T12:00:00Z",
            "final_dataset": "chl-test + chl-gapfilled-test (gap-filled)",
            "final_grid_shape": [2, 2], "final_valid_fraction": 0.9,
            "status": "loaded",
        },
        "bathymetry_info": {
            "dataset": "etopo-test", "source_grid_shape": [10, 10],
            "source_valid_fraction": 1.0, "aligned_grid_shape": [2, 2],
            "depth_valid_fraction": 0.75, "depth_min_m": 4.0, "depth_max_m": 120.0,
            "stride": {"latitude": 15, "longitude": 15},
        },
        "depth_m": np.array([[4.0, 20.0], [120.0, np.nan]]),
        "current_speed": None,
        "structure_stats": {"artificial_reef_records": 4},
        "habitat_info": {"feature_count": 12},
        "closure_checked": True,
        "closure_areas": [{"name": "test"}],
    }

    report = build_data_quality(layers, _sources(), ["layers currents: endpoint unavailable"])
    result = report["layers"]

    assert result["sst"]["status"] == "loaded"
    assert result["sst"]["valid_fraction"] == 0.75
    assert result["chlorophyll"]["status"] == "loaded"
    assert result["chlorophyll"]["gapfilled_used"] is True
    assert result["chlorophyll"]["primary_time"] == "2026-11-10T12:00:00Z"
    assert result["chlorophyll"]["gapfilled_time"] == "2026-11-11T12:00:00Z"
    assert result["chlorophyll"]["final_valid_fraction"] == 0.9
    assert result["bathymetry"]["status"] == "loaded"
    assert result["bathymetry"]["depth_valid_fraction"] == 0.75
    assert result["currents"]["status"] == "failed"
    assert result["reef_structure"]["status"] == "loaded"
    assert result["benthic_habitat"]["status"] == "loaded"
    assert result["closures"]["area_count"] == 1
    assert "unknown, not zero" in report["semantics"]["missing_data"]


def test_missing_enabled_layer_is_unavailable_not_zero_or_loaded():
    report = build_data_quality(None, _sources(), [])
    result = report["layers"]

    assert result["sst"]["status"] == "unavailable"
    assert result["chlorophyll"]["status"] == "unavailable"
    assert result["bathymetry"]["status"] == "unavailable"
    assert result["currents"]["status"] == "unavailable"
    assert result["benthic_habitat"]["status"] == "unavailable"


def test_bathymetry_minimum_preserves_sub_millimeter_positive_depth():
    layers = {
        "depth_m": np.array([[0.0004, 2.0], [np.nan, 10.0]]),
    }
    report = build_data_quality(layers, _sources(), [])
    assert report["layers"]["bathymetry"]["depth_min_m"] == 0.0004
