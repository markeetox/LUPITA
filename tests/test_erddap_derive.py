import numpy as np

from pipeline import derive
from pipeline.sources import erddap

CFG = {"base": "https://example.org/erddap", "dataset": "demo", "variable": "analysed_sst",
       "dims": ["time", "latitude", "longitude"], "stride": {"latitude": 2, "longitude": 3}}
REGION = {"lat": [24.5, 27.0], "lon": [-81.0, -78.5]}


def test_url_shape():
    url = erddap.build_griddap_url(CFG, REGION)
    assert url == ("https://example.org/erddap/griddap/demo.csv?analysed_sst"
                   "[(last)][(24.5):2:(27.0)][(-81.0):3:(-78.5)]")


def test_url_with_altitude():
    cfg = dict(CFG, dims=["time", "altitude", "latitude", "longitude"])
    assert "[(last)][(0.0)][(24.5)" in erddap.build_griddap_url(cfg, REGION)


def _csv(unit="degree_C", base=20.0):
    lines = ["time,latitude,longitude,analysed_sst", f"UTC,degrees_north,degrees_east,{unit}"]
    for i, lat in enumerate([25.0, 25.1, 25.2]):
        for j, lon in enumerate([-80.2, -80.1, -80.0]):
            v = "NaN" if (i, j) == (2, 2) else f"{base + i}"
            lines.append(f"2026-10-09T09:00:00Z,{lat},{lon},{v}")
    return "\n".join(lines)


def test_parse_grid():
    lats, lons, grid, when, unit = erddap.parse_grid_csv(_csv(), "analysed_sst")
    assert grid.shape == (3, 3) and np.isnan(grid[2, 2])
    assert when == "2026-10-09T09:00:00Z" and unit == "degree_C"


def test_kelvin_converted():
    *_, grid, _, _ = (lambda r: (r[2], r[3], r[4]))(erddap.parse_grid_csv(_csv("K", 300.0), "analysed_sst"))
    assert abs(grid[0, 0] - 26.85) < 1e-9


def test_gradient_matches_hand_calc():
    # Temperature rises 1 C per 0.1 deg of latitude -> 1 / (0.1 * 111.32) C/km.
    lats = np.linspace(25.0, 25.5, 6)
    lons = np.linspace(-80.5, -80.0, 6)
    grid = np.tile(((lats - 25.0) / 0.1)[:, None], (1, len(lons)))
    g = derive.gradient_magnitude(grid, lats, lons)
    assert np.allclose(g, 1 / (0.1 * 111.32), rtol=1e-6)


def test_top_cells_orders_and_filters():
    lats = np.array([25.0, 25.1]); lons = np.array([-80.0, -79.9])
    vals = np.array([[0.01, 0.2], [np.nan, 0.1]])
    cells = derive.top_cells(vals, lats, lons, n=5, min_value=0.05)
    assert [c["value"] for c in cells] == [0.2, 0.1]
