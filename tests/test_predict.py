import json
from pathlib import Path

import numpy as np

from pipeline import derive, scoring
from pipeline.predict import build_fish_json

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = json.loads((ROOT / "data/parameters.json").read_text())
PROFILES = [json.loads(p.read_text()) for p in sorted((ROOT / "data/species").glob("*.json"))]
LATS = np.round(np.arange(25.0, 25.80, 0.02), 4)
LONS = np.round(np.arange(-80.6, -79.79, 0.02), 4)
BUOYS = [{"station": "T1", "name": "Test buoy", "ok": True, "lat": 25.4, "lon": -79.9, "water_temp_c": 27.2}]


def make_layers(base_sst=29.8, with_depth=True, chl_nan_in_pocket=False, pockets=True, pocket_sst=27.0):
    lon, lat = np.meshgrid(LONS, LATS)
    sst = np.full(lon.shape, base_sst)
    deep_pocket = (lon >= -80.0) & (lat >= 25.3) & (lat <= 25.5)
    shallow_pocket = (lon <= -80.3) & (lat >= 25.3) & (lat <= 25.5)
    if pockets:
        sst[deep_pocket | shallow_pocket] = pocket_sst
    depth = np.where(lon < -80.2, 8.0, 600.0)
    chl = np.full(lon.shape, 0.12)
    if chl_nan_in_pocket:
        chl[deep_pocket] = np.nan
    return {"lats": LATS, "lons": LONS, "sst_c": sst, "sst_gradient": derive.gradient_magnitude(sst, LATS, LONS),
            "chlorophyll": chl, "depth_m": depth if with_depth else None, "chl_raw": None,
            "times": {"sst": "2026-10-08T09:00:00Z", "chlorophyll": "2026-10-07T12:00:00Z"},
            "datasets": {"sst": "demo"}}


def run(layers):
    out = build_fish_json(layers, BUOYS, PROFILES, REGISTRY, "2026-10-09T00:00:00+00:00")
    json.dumps(out, allow_nan=False)       # must be valid JSON
    return out, {s["id"]: s for s in out["species"]}


def test_trapezoid_shapes():
    v = np.array([22.5, 27.0, 29.5, 31.0])
    assert np.allclose(scoring.trapezoid(v, [20, 30], [25, 29]), [0.5, 1.0, 0.5, 0.0])
    assert scoring.trapezoid(np.array([100.0]), [20, None], [25, None])[0] == 1.0


def test_mahi_only_in_deep_cool_water():
    out, sp = run(make_layers())
    assert sp["mahi-mahi"]["status"] == "ok"
    mahi = [s for s in out["spots"] if s["species"] == "mahi-mahi"]
    assert mahi
    for s in mahi:                                   # never in the shallow pocket
        assert s["coords"][0] > -80.2
        assert 25.28 <= s["coords"][1] <= 25.52
        assert all(len(r) == 2 for r in s["reasons"]) and s["reasons"]
    assert any("Water is" in r[1] for r in mahi[0]["reasons"])
    assert any(r[0] == "measured" for r in mahi[0]["reasons"])      # nearest buoy


def test_too_warm_means_no_favorable_areas():
    out, sp = run(make_layers(base_sst=30.5, pockets=False))
    assert sp["mahi-mahi"]["status"] == "no_favorable_areas"
    assert "No favorable" in sp["mahi-mahi"]["message"]
    assert not [s for s in out["spots"] if s["species"] == "mahi-mahi"]


def test_species_without_data_are_marked_unavailable():
    _, sp = run(make_layers())
    assert sp["yellowtail-snapper"]["status"] == "unavailable"
    assert "reef" in sp["yellowtail-snapper"]["message"]
    assert sp["snook"]["status"] == "unavailable"


def test_missing_depth_makes_mahi_unavailable():
    _, sp = run(make_layers(with_depth=False))
    assert sp["mahi-mahi"]["status"] == "unavailable"


def test_cloud_gap_lowers_confidence_and_says_so():
    out, _ = run(make_layers(chl_nan_in_pocket=True))
    mahi = [s for s in out["spots"] if s["species"] == "mahi-mahi"]
    assert mahi and mahi[0]["confidence"] == "Low"
    assert any("No chlorophyll" in r[1] for r in mahi[0]["reasons"])


def test_value_just_outside_ideal_is_described_honestly():
    out, _ = run(make_layers(pocket_sst=29.2))
    mahi = [s for s in out["spots"] if s["species"] == "mahi-mahi"]
    assert mahi
    texts = " ".join(r[1] for r in mahi[0]["reasons"])
    assert "just above" in texts and "inside the 25-29" not in texts


def test_gradient_reason_states_real_size_per_10km():
    from pipeline.predict import _fill
    mahi = [p for p in PROFILES if p["id"] == "mahi-mahi"][0]
    f = [x for x in mahi["factors"] if x["param"] == "sst_gradient"][0]
    text = _fill(f["reason_template"], "sst_gradient", 0.049, f)
    assert "0.5 C every 10 km" in text
