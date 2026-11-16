from pipeline.run import attach_factor_source_diagnostics


def test_grid_factor_diagnostics_include_layer_freshness_and_static_metadata():
    fish = {"spots": [{"factor_diagnostics": [
        {"param": "sst_c", "available": True},
        {"param": "current_speed", "available": True},
        {"param": "depth_m", "available": False},
    ]}]}
    quality = {"layers": {
        "sst": {"status": "loaded", "dataset": "sst-test", "time": "2026-11-16T12:00:00Z",
                "freshness": {"status": "fresh", "age_hours": 2}},
        "currents": {
            "status": "partial", "blend_mode": "HF Radar where valid; satellite altimetry elsewhere",
            "primary": {"dataset": "hfr-test", "loaded": True, "time": "2026-11-16T10:00:00Z"},
            "fallback": {"dataset": "alt-test", "loaded": True, "time": "2026-11-15T00:00:00Z", "used_for_currents": True},
            "primary_freshness": {"status": "fresh", "age_hours": 2},
            "fallback_freshness": {"status": "delayed", "age_hours": 36},
            "query_region_coverage": {"combined_valid_fraction": 0.2},
        },
        "bathymetry": {"status": "loaded", "dataset": "etopo-test", "static": True,
                       "depth_valid_fraction": 0.8},
    }}

    attach_factor_source_diagnostics(fish, quality)
    factors = {row["param"]: row for row in fish["spots"][0]["factor_diagnostics"]}

    sst = factors["sst_c"]["environmental_source"]
    assert sst["kind"] == "observed_grid"
    assert sst["available_at_prediction"] is True
    assert sst["layers"][0]["freshness"]["status"] == "fresh"

    currents = factors["current_speed"]["environmental_source"]
    assert currents["kind"] == "composite_observation"
    assert currents["layers"][0]["primary"]["freshness"]["status"] == "fresh"
    assert currents["layers"][0]["fallback"]["freshness"]["status"] == "delayed"
    assert "exact provider for this cell is not retained" in currents["explanation"]

    bathymetry = factors["depth_m"]["environmental_source"]
    assert bathymetry["kind"] == "static_dataset"
    assert bathymetry["available_at_prediction"] is False
    assert bathymetry["layers"][0]["static"] is True


def test_named_site_buoy_provenance_reports_observation_without_inventing_freshness():
    fish = {"spots": [{"factor_diagnostics": [{
        "param": "sst_c", "available": True, "input_tag": "measured",
        "input_details": {
            "source_type": "NDBC buoy", "station": "42001", "station_name": "Test Buoy",
            "observed_at": "2026-11-16T18:00:00+00:00", "distance_km": 12.5,
        },
    }]}]}

    attach_factor_source_diagnostics(fish, {"layers": {}})
    source = fish["spots"][0]["factor_diagnostics"][0]["environmental_source"]["source"]

    assert source["kind"] == "measured_buoy"
    assert source["station"] == "42001"
    assert source["observed_at"] == "2026-11-16T18:00:00+00:00"
    assert source["freshness"]["status"] == "unconfigured"
    assert source["freshness"]["age_hours"] is None


def test_named_site_structure_uses_site_catalog_not_grid_reef_layer():
    fish = {"spots": [{"factor_diagnostics": [{
        "param": "structure_type", "available": True, "input_tag": "static",
        "input_details": {"source_type": "site catalog", "site_kind": "inlet"},
    }]}]}

    attach_factor_source_diagnostics(fish, {"layers": {"reef_structure": {"status": "loaded"}}})
    source = fish["spots"][0]["factor_diagnostics"][0]["environmental_source"]

    assert source["kind"] == "static_site_catalog"
    assert source["layers"] == []
    assert "site catalog" in source["explanation"]


def test_missing_factor_is_not_confused_with_missing_source_timestamp():
    fish = {"spots": [{"factor_diagnostics": [{"param": "chlorophyll", "available": False}]}]}
    quality = {"layers": {"chlorophyll": {
        "status": "loaded", "final_dataset": "chl-test",
        "freshness": {"status": "unknown", "observed_at": None, "age_hours": None},
        "primary_freshness": {"status": "unknown", "age_hours": None},
    }}}

    attach_factor_source_diagnostics(fish, quality)
    source = fish["spots"][0]["factor_diagnostics"][0]["environmental_source"]

    assert source["available_at_prediction"] is False
    assert source["layers"][0]["status"] == "loaded"
    assert source["layers"][0]["freshness"]["status"] == "unknown"



def test_gulf_stream_edge_uses_altimetry_freshness_not_selected_current_freshness():
    fish = {"spots": [{"factor_diagnostics": [{"param": "gulf_stream_edge", "available": True}]}]}
    quality = {"layers": {"currents": {
        "status": "loaded",
        "freshness": {"status": "fresh", "age_hours": 2},
        "fallback": {"dataset": "alt-test", "loaded": True, "time": "2026-11-15T00:00:00Z"},
        "fallback_freshness": {"status": "stale", "age_hours": 90},
    }}}

    attach_factor_source_diagnostics(fish, quality)
    source = fish["spots"][0]["factor_diagnostics"][0]["environmental_source"]

    assert source["layers"][0]["layer"] == "satellite_altimetry"
    assert source["layers"][0]["freshness"]["status"] == "stale"
    assert source["layers"][0]["dataset"] == "alt-test"
