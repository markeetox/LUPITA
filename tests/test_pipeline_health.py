from pipeline.run import build_pipeline_health


def _quality(sst="loaded", optional="loaded"):
    return {
        "layers": {
            "sst": {"status": sst},
            "chlorophyll": {"status": optional},
            "bathymetry": {"status": "disabled"},
        }
    }


def test_healthy_requires_fresh_predictions_and_no_source_errors():
    result = build_pipeline_health(_quality(), True, [])
    assert result["status"] == "healthy"
    assert result["prediction_refreshed"] is True
    assert result["critical_issues"] == []


def test_sst_failure_is_critical_even_when_old_predictions_are_preserved():
    result = build_pipeline_health(_quality(sst="failed"), False, ["layers sst: HTTP 503"])
    assert result["status"] == "failed"
    assert result["prediction_refreshed"] is False
    assert any("Required SST" in item for item in result["critical_issues"])


def test_missing_prediction_refresh_is_critical():
    result = build_pipeline_health(_quality(), False, ["prediction scoring: failed"])
    assert result["status"] == "failed"


def test_optional_layer_failure_is_degraded_not_critical():
    result = build_pipeline_health(_quality(optional="failed"), True, ["layers chlorophyll: HTTP 503"])
    assert result["status"] == "degraded"
    assert result["critical_issues"] == []
    assert result["optional_layer_issues"] == ["chlorophyll: failed"]


def test_non_layer_warnings_are_degraded():
    result = build_pipeline_health(_quality(), True, ["weather forecast: unavailable"])
    assert result["status"] == "degraded"
