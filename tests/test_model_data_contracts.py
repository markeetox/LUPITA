"""Regression tests for the existing grid and named-site missing-data contracts.

These tests intentionally preserve current behavior; they do not propose a scoring-policy change.
"""
from datetime import datetime, timezone

import numpy as np

from pipeline.scoring import score_species
from pipeline.sites import score_site


def _range_factor(param, weight=0.5, **flags):
    return {
        "param": param,
        "kind": "range",
        "range": [0.0, 40.0],
        "ideal": [20.0, 30.0],
        "weight": weight,
        "active": True,
        **flags,
    }


def test_grid_required_flag_does_not_make_a_missing_optional_layer_fatal():
    profile = {
        "min_coverage": 0.5,
        "factors": [
            _range_factor("sst_c"),
            _range_factor("chlorophyll", required=True),
        ],
    }
    layers = {"sst_c": np.full((2, 2), 25.0), "chlorophyll": None}

    result = score_species(profile, layers)

    assert result["status"] == "ok"
    np.testing.assert_allclose(result["coverage"], 0.5)
    np.testing.assert_allclose(result["score"], 1.0)
    assert [f["param"] for f in result["missing"]] == ["chlorophyll"]


def test_grid_missing_gate_makes_the_species_unavailable():
    profile = {
        "min_coverage": 0.5,
        "factors": [
            _range_factor("sst_c"),
            _range_factor("chlorophyll", gate=True),
        ],
    }
    layers = {"sst_c": np.full((2, 2), 25.0), "chlorophyll": None}

    result = score_species(profile, layers)

    assert result == {
        "status": "unavailable",
        "message": "Waiting for: chlorophyll data",
    }


def test_grid_coverage_is_evaluated_per_cell_and_low_coverage_cells_are_excluded():
    profile = {
        "min_coverage": 0.75,
        "factors": [
            _range_factor("sst_c"),
            _range_factor("chlorophyll"),
        ],
    }
    layers = {
        "sst_c": np.full((2, 2), 25.0),
        "chlorophyll": np.array([[1.0, np.nan], [1.0, np.nan]]),
    }

    result = score_species(profile, layers)

    assert result["status"] == "ok"
    np.testing.assert_allclose(result["coverage"], [[1.0, 0.5], [1.0, 0.5]])
    assert np.isfinite(result["score"][:, 0]).all()
    assert np.isnan(result["score"][:, 1]).all()


def _site_profile(tide_required=False):
    return {
        "factors": [
            _range_factor("sst_c", weight=0.5, required=True),
            {
                "param": "tide_stage",
                "kind": "category",
                "map": {"rising": 1.0},
                "weight": 0.5,
                "active": True,
                "gate": True,
                "required": tide_required,
            },
        ],
    }


def _site_context():
    now = datetime(2026, 11, 16, 12, tzinfo=timezone.utc)
    return {
        "buoys": [{
            "station": "TEST",
            "name": "Test buoy",
            "ok": True,
            "lat": 25.0,
            "lon": -80.0,
            "water_temp_c": 25.0,
        }],
        "conditions": {"now": now, "tides": []},
        "layers": {"sst_c": np.full((2, 2), 25.0), "lats": np.array([25.0, 25.1]),
                   "lons": np.array([-80.0, -79.9])},
    }


def test_site_gate_without_required_is_skipped_when_its_input_is_missing():
    site = {"name": "Test inlet", "kind": "inlet", "lat": 25.0, "lon": -80.0}

    result = score_site(_site_profile(tide_required=False), site, _site_context(), {})

    assert result is not None
    assert result["evaluated_factor_count"] == 1
    assert result["active_factor_count"] == 2
    assert result["coverage"] == 0.5
    assert result["score"] == 1.0


def test_site_missing_required_gate_makes_the_site_unscored():
    site = {"name": "Test inlet", "kind": "inlet", "lat": 25.0, "lon": -80.0}

    result = score_site(_site_profile(tide_required=True), site, _site_context(), {})

    assert result is None
