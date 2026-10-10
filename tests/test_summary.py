import json

import numpy as np

from pipeline.run_v1 import summarize_grid

LATS = np.linspace(25.0, 25.4, 5)
LONS = np.linspace(-80.4, -80.0, 5)


def test_all_nan_grid_is_valid_json():
    out = summarize_grid(np.full((5, 5), np.nan), LATS, LONS)
    assert out["valid_fraction"] == 0.0 and out["value_min"] is None
    json.dumps(out, allow_nan=False)


def test_partial_cloud_grid():
    grid = np.tile(np.linspace(26, 30, 5)[:, None], (1, 5))
    grid[0, :] = np.nan
    out = summarize_grid(grid, LATS, LONS, gradient_min=0.01)
    assert 0 < out["valid_fraction"] < 1
    assert out["value_min"] == 27.0
    json.dumps(out, allow_nan=False)


def test_log_scale_ignores_zero_and_negative():
    grid = np.array([[0.1, 0.2, -1, 0.4, 0.8]] * 5, dtype=float)
    out = summarize_grid(grid, LATS, LONS, log_scale=True)
    assert out["gradient_max"] is not None
    json.dumps(out, allow_nan=False)
