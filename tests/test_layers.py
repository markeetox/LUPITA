import numpy as np

from pipeline import derive
from pipeline.layers import front_strength

LATS = np.round(np.arange(25.0, 25.4, 0.02), 4)
LONS = np.round(np.arange(-80.4, -80.0, 0.02), 4)


def test_shallow_bank_edge_is_not_a_front_but_deep_front_is():
    lon, _ = np.meshgrid(LONS, LATS)
    depth = np.where(lon < -80.3, 10.0, 500.0)               # shallow bank in the west
    sst = np.where(lon < -80.3, 31.0, 29.0)                  # warm bank next to cooler deep water
    sst = np.where(lon > -80.1, 27.0, sst)                   # a real front inside deep water
    plain = derive.gradient_magnitude(sst, LATS, LONS)
    masked = front_strength(sst, depth, LATS, LONS)
    bank_col = int(np.argmin(np.abs(LONS - -80.3)))
    front_col = int(np.argmin(np.abs(LONS - -80.1)))
    assert np.nanmax(plain[:, bank_col - 1: bank_col + 2]) > 0.05      # the false edge exists without masking
    assert np.all(np.isnan(masked[:, bank_col - 1: bank_col + 1]))      # and is removed with it
    assert np.nanmax(masked[:, front_col - 1: front_col + 2]) > 0.05    # the deep front survives


def test_no_depth_falls_back_to_plain_gradient():
    sst = np.tile(np.linspace(27, 30, len(LONS)), (len(LATS), 1))
    inner = (slice(2, -2), slice(2, -2))                      # the outer border is deliberately blanked
    assert np.allclose(front_strength(sst, None, LATS, LONS)[inner], derive.gradient_magnitude(sst, LATS, LONS)[inner])


def test_border_cells_have_no_front_value():
    sst = np.tile(np.linspace(27, 30, len(LONS)), (len(LATS), 1))
    g = front_strength(sst, None, LATS, LONS)
    assert np.all(np.isnan(g[:2, :])) and np.all(np.isnan(g[-2:, :]))
    assert np.all(np.isnan(g[:, :2])) and np.all(np.isnan(g[:, -2:]))
    assert np.isfinite(g[5, 5])
