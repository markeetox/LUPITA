import numpy as np
from datetime import datetime, timezone
from pipeline import derive, layers, tides

UTC = timezone.utc

def dt(*a):
    return datetime(*a, tzinfo=UTC)

def test_current_convergence():
    lats = np.array([25.0, 25.1, 25.2])
    lons = np.array([-80.2, -80.1, -80.0])
    u = np.tile([1.0, 0.0, -1.0], (3, 1))
    v = np.zeros((3, 3))
    conv = derive.current_convergence(u, v, lats, lons)
    assert conv.shape == (3, 3)
    assert conv[1, 1] > 0

def test_bottom_curvature_flat_vs_ridge():
    lats = np.linspace(25.0, 25.4, 5)
    lons = np.linspace(-80.4, -80.0, 5)
    flat_slope = np.tile(np.linspace(100.0, 500.0, 5), (5, 1))
    curv_flat = derive.bottom_curvature(flat_slope, lats, lons)
    assert np.allclose(curv_flat[1:-1, 1:-1], 0.0, atol=1e-5)

    ridge = np.tile(np.array([100.0, 100.0, 300.0, 500.0, 500.0]), (5, 1))
    curv_ridge = derive.bottom_curvature(ridge, lats, lons)
    # The step transition (columns 1 and 3) has non-zero curvature (change of slope)
    assert curv_ridge[2, 1] > 0
    assert curv_ridge[2, 3] > 0

def test_flow_velocity_at():
    events = [{"time": dt(2026, 10, 11, 6, 0), "type": "L", "height_m": 0.2},
              {"time": dt(2026, 10, 11, 12, 15), "type": "H", "height_m": 1.7}]
    peak = tides.flow_velocity_at(events, dt(2026, 10, 11, 9, 7))
    assert peak["flow"] > 0.95
    assert peak["direction"] == "incoming"

    slack = tides.flow_velocity_at(events, dt(2026, 10, 11, 6, 0))
    assert slack["flow"] == 0.0
    assert "slack" in slack["stage"]

def test_gapfilled_chlorophyll_fallback_blends():
    sources = {
        "region": {"lat": [25.0, 25.4], "lon": [-80.4, -80.0]},
        "erddap": {
            "sst": {"base": "http://mock", "dataset": "sst_ds", "variable": "sst", "dims": ["time", "latitude", "longitude"]},
            "chlorophyll": {"enabled": True, "base": "http://mock", "dataset": "chl_primary", "variable": "chl", "dims": ["time", "latitude", "longitude"]},
            "chlorophyll_gapfilled": {"enabled": True, "base": "http://mock", "dataset": "chl_dineof", "variable": "chl", "dims": ["time", "latitude", "longitude"]}
        }
    }
    lats = np.round(np.arange(25.0, 25.4, 0.02), 4)
    lons = np.round(np.arange(-80.4, -80.0, 0.02), 4)
    sst_csv = "time,latitude,longitude,sst\nUTC,degN,degE,C\n" + "\n".join(
        f"2026-10-11T00:00:00Z,{la},{lo},28.0" for la in lats for lo in lons
    )
    chl_primary_csv = "time,latitude,longitude,chl\nUTC,degN,degE,mg/m3\n" + "\n".join(
        f"2026-10-11T00:00:00Z,{la},{lo},{0.5 if (la==lats[5] and lo==lons[5]) else 'NaN'}" for la in lats for lo in lons
    )
    chl_dineof_csv = "time,latitude,longitude,chl\nUTC,degN,degE,mg/m3\n" + "\n".join(
        f"2026-10-11T00:00:00Z,{la},{lo},0.2" for la in lats for lo in lons
    )

    def mock_fetch(url):
        if "sst_ds" in url:
            return sst_csv
        elif "chl_primary" in url:
            return chl_primary_csv
        elif "chl_dineof" in url:
            return chl_dineof_csv
        raise ValueError(f"unknown url: {url}")

    errors = []
    lay = layers.load_layers(sources, errors, fetch=mock_fetch)
    assert lay is not None
    assert lay["chlorophyll_gapfilled"] is True
    assert np.isclose(lay["chlorophyll"][5, 5], 0.5)
    assert np.isclose(lay["chlorophyll"][0, 0], 0.2)
