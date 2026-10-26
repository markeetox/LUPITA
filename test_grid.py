import numpy as np

from pipeline import grid


def test_resample_linear_field_is_exact():
    lats, lons = np.array([25.0, 25.1, 25.2]), np.array([-80.0, -79.9, -79.8])
    field = 2 * lats[:, None] + 3 * lons[None, :]
    dl, dn = np.array([25.05, 25.15]), np.array([-79.95, -79.85])
    out = grid.resample(field, lats, lons, dl, dn)
    assert np.allclose(out, 2 * dl[:, None] + 3 * dn[None, :])


def test_resample_nan_and_outside():
    lats, lons = np.array([25.0, 25.1, 25.2]), np.array([-80.0, -79.9, -79.8])
    field = np.ones((3, 3)); field[1, 1] = np.nan
    out = grid.resample(field, lats, lons, np.array([25.1, 26.0]), np.array([-79.9]))
    assert np.isnan(out[0, 0])      # centre is missing and has no valid neighbours at that exact point
    assert np.isnan(out[1, 0])      # outside the source grid


def test_components_and_hull():
    m = np.zeros((5, 5), bool); m[0, 0:2] = True; m[3:5, 3:5] = True
    sizes = sorted(len(c) for c in grid.components(m))
    assert sizes == [2, 4]
    hull = grid.convex_hull([(0, 0), (1, 0), (1, 1), (0, 1), (0.5, 0.5)])
    assert len(hull) == 4
