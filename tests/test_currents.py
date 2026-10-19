import json
from datetime import timezone
from pathlib import Path

import numpy as np

from pipeline import currents
from pipeline.predict import build_fish_json
from pipeline.sources import erddap
from tests import test_structure as TS
from tests.test_species_v2 import PLACES, PROFILES, REGISTRY, when

LATS = np.round(np.arange(24.5, 27.001, 0.25), 3)
LONS = np.round(np.arange(-81.0, -78.499, 0.25), 3)
CENTRE, WIDTH, PEAK = -79.7, 0.35, 1.5
HALF_MAX_EDGE = CENTRE - WIDTH * np.sqrt(np.log(2))            # where a Gaussian stream falls to half its peak: -79.991


def stream(la, lo):
    return (0.0, PEAK * float(np.exp(-(((lo - CENTRE) / WIDTH) ** 2))))


def test_edge_is_found_where_the_flow_reaches_half_its_peak():
    v = np.array([[stream(la, lo)[1] for lo in LONS] for la in LATS])
    edge = currents.edge_longitudes(LATS, LONS, v)
    assert np.all(np.abs(edge - HALF_MAX_EDGE) < 0.05)
    assert np.all(np.isfinite(currents.smooth(edge)))


def test_rows_without_a_real_stream_give_no_edge_and_land_is_ignored():
    v = np.full((3, 6), 0.1); v[1, 3:] = 1.0
    v[1, :2] = np.nan                                   # land on the west side
    edge = currents.edge_longitudes([25, 25.25, 25.5], np.arange(6) * 0.25 - 80, v)
    assert np.isnan(edge[0]) and np.isnan(edge[2]) and np.isfinite(edge[1])


def test_speed_direction_and_signed_distance():
    s, d = currents.speed_dir(np.array([0.0, 1.0]), np.array([1.0, 0.0]))
    assert np.allclose(s, 1.943844) and np.allclose(d, [0, 90])                     # north, then east
    km = currents.signed_km(np.array([-80.0, -80.0]), np.array([25.0, 26.0]), np.array([-80.1, -79.9]))
    assert km[0, 0] < 0 < km[0, 1] and abs(km[0, 1] - 0.1 * 111.32 * np.cos(np.radians(25))) < 0.01


def test_too_few_rows_with_a_stream_is_not_trusted():
    assert currents.edge_on_grid([25, 25.25, 25.5], np.array([-80.0, np.nan, np.nan]), [25.0]) is None
    out = currents.edge_on_grid([25, 25.5, 26], np.array([-80.0, -80.2, -80.4]), [25.25, 27.0])
    assert abs(out[0] - -80.1) < 1e-9 and np.isnan(out[1])                         # interpolates inside, nothing beyond


def test_several_variables_in_one_request_and_one_parse():
    cfg = {"base": "https://x/erddap", "dataset": "d", "variables": ["ugos", "vgos"], "dims": ["time", "latitude", "longitude"], "stride": {"latitude": 1, "longitude": 1}}
    url = erddap.build_griddap_url(cfg, {"lat": [24.5, 27.0], "lon": [-81.0, -78.5]})
    assert url.count("[(last)]") == 2 and "ugos[(last)][(24.5):1:(27.0)][(-81.0):1:(-78.5)],vgos[" in url
    text = "time,latitude,longitude,ugos,vgos\nUTC,degrees_north,degrees_east,m s-1,m s-1\nt,25.0,-80.0,0.1,0.9\nt,25.0,-79.75,NaN,1.2\n"
    la, lo, g, t = erddap.parse_multi_csv(text, ["ugos", "vgos"])
    assert g["vgos"].tolist() == [[0.9, 1.2]] and np.isnan(g["ugos"][0, 1]) and t == "t"


def test_stream_line_for_the_map():
    edge = np.linspace(-80.0, -79.8, 11); lats = np.linspace(25, 26, 11)
    gj = currents.stream_geojson(edge, lats, "src", "2026-10-11", True, "now", every=2)
    line = gj["features"][0]["geometry"]
    assert line["type"] == "LineString" and len(line["coordinates"]) == 6 and gj["loaded"] is True
    assert currents.stream_geojson(None, lats, "src", None, False, "now")["features"] == []
    json.dumps(gj, allow_nan=False)


def test_layers_carry_currents_and_the_edge(monkeypatch):
    monkeypatch.setattr(TS, "CURRENT_FN", stream)
    errs = []
    lay = TS.L.load_layers(TS._sources(), errs, fetch=TS.fake_erddap, fetch_arc=TS.fake_arcgis)
    assert errs == [] and lay["datasets"]["currents"] == "nesdisSSH1day"
    ed = lay["gulf_stream_edge"]; j = int(np.argmin(abs(lay["lons"] - HALF_MAX_EDGE)))
    assert abs(ed[60, j]) < 3 and ed[60, j + 20] > 0 and ed[60, j - 20] < 0         # zero at the edge, east positive, west negative
    assert np.nanmax(lay["current_speed"]) > 2.5                                    # a 1.5 m/s stream is about 2.9 kn


def test_sailfish_gather_at_the_edge_and_the_popup_says_so(monkeypatch):
    monkeypatch.setattr(TS, "CURRENT_FN", stream)
    lay = TS.L.load_layers(TS._sources(), [], fetch=TS.fake_erddap, fetch_arc=TS.fake_arcgis)
    out = build_fish_json(lay, [], PROFILES, REGISTRY, "t", PLACES, when(2027, 1, 15, 17))
    json.dumps(out, allow_nan=False)
    sail = [s for s in out["spots"] if s["species"] == "sailfish"]
    assert sail and all(-80.35 <= s["coords"][0] <= -79.65 for s in sail)
    assert any("inshore edge is close" in r[1] for r in sail[0]["reasons"])
    rows = {r[0]: r[1] for r in sail[0]["location"]}
    assert "kn toward the" in rows["Current"] and "inshore edge" in rows["Gulf Stream"]


def test_without_currents_the_fish_still_score_and_the_error_is_recorded():
    def fetch(url):
        if "nesdisSSH1day" in url:
            raise RuntimeError("403 Client Error")
        return TS.fake_erddap(url)
    errs = []
    lay = TS.L.load_layers(TS._sources(), errs, fetch=fetch, fetch_arc=TS.fake_arcgis)
    assert any("layers currents" in e for e in errs) and lay["gulf_stream_edge"] is None
    lon = np.meshgrid(lay["lons"], lay["lats"])[0]                      # realistic offshore depth, so fronts can be judged
    lay["depth_m"] = np.where(lon < -80.2, 8.0, 100.0)
    lay["sst_gradient"] = TS.L.front_strength(lay["sst_c"], lay["depth_m"], lay["lats"], lay["lons"])
    out = build_fish_json(lay, [], PROFILES, REGISTRY, "t", PLACES, when(2027, 1, 15, 17))
    sail = {s["id"]: s for s in out["species"]}["sailfish"]
    spots = [s for s in out["spots"] if s["species"] == "sailfish"]
    assert sail["status"] == "ok" and spots and spots[0]["confidence"] == "Low"          # scored without the edge, flagged Low
    assert not any("inshore edge" in r[1] for s in spots for r in s["reasons"])
