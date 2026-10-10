import json
from pathlib import Path

import numpy as np

from pipeline import layers as L
from pipeline import structure
from pipeline.predict import build_fish_json
from pipeline.sources import arcgis

ROOT = Path(__file__).resolve().parent.parent
REGION = {"lat": [24.5, 27.0], "lon": [-81.0, -78.5]}
LATS = np.round(np.arange(25.0, 25.2001, 0.02), 4)
LONS = np.round(np.arange(-80.2, -80.0001, 0.02), 4)


def test_paging_follows_offsets():
    calls = []

    def fake(url, params):
        calls.append(params["resultOffset"])
        n = 2 if params["resultOffset"] == 0 else 1
        return {"features": [{"attributes": {"k": params["resultOffset"] + i}} for i in range(n)],
                "exceededTransferLimit": params["resultOffset"] == 0}
    feats = arcgis.query_all("https://x/MapServer/1", REGION, fetch=fake, page_size=2)
    assert len(feats) == 3 and calls == [0, 2]


def test_query_asks_for_generalized_geometry_only_when_needed():
    p = arcgis.query_params(REGION, return_geometry=True, simplify=0.0005)
    assert p["returnGeometry"] == "true" and p["maxAllowableOffset"] == 0.0005
    assert "maxAllowableOffset" not in arcgis.query_params(REGION)


def _square(lon0, lat0, lon1, lat1):
    return [[lon0, lat0], [lon1, lat0], [lon1, lat1], [lon0, lat1], [lon0, lat0]]


def test_polygon_cover_and_hole():
    cell = {"geometry": {"rings": [_square(-80.11, 25.09, -80.09, 25.11)]}}       # exactly cell (5, 5)
    cover = structure.rasterize_cover([cell], LATS, LONS)
    i, j = int(np.argmin(abs(LATS - 25.10))), int(np.argmin(abs(LONS - -80.10)))
    assert cover[i, j] > 0.95 and cover.sum() - cover[i, j] < 0.1
    holed = {"geometry": {"rings": [_square(-80.11, 25.09, -80.09, 25.11), _square(-80.105, 25.095, -80.095, 25.105)]}}
    assert 0.6 < structure.rasterize_cover([holed], LATS, LONS)[i, j] < 0.85


def test_artificial_records_map_to_cells_and_wrecks_are_flagged():
    feats = [{"attributes": {"Name": "Wreck A", "MatCat": "Vessel", "Depth": 71, "Relief": 27, "Lat_DD": 25.1, "Long_DD": -80.1}},
             {"attributes": {"Name": "Balls", "MatCat": "Module", "Lat_DD": None, "Long_DD": None}, "geometry": {"x": -80.04, "y": 25.04}},
             {"attributes": {"Name": "Outside", "Lat_DD": 30.0, "Long_DD": -80.1}}]
    cells = structure.artificial_cells(feats, LATS, LONS)
    assert len(cells) == 2 and any(v[0]["kind"] == "wreck" for v in cells.values())
    types, _, _ = structure.build_structure_layer(feats, [], LATS, LONS)
    assert (types == "wreck").sum() == 1 and (types == "artificial_reef").sum() == 1


# ---- end to end with fake NOAA and FWC responses ----
def _csv(lats, lons, name, fn, unit="degree_C", time=True, alt=False):
    head = (["time"] if time else []) + (["altitude"] if alt else []) + ["latitude", "longitude", name]
    unts = (["UTC"] if time else []) + (["m"] if alt else []) + ["degrees_north", "degrees_east", unit]
    rows = [",".join(head), ",".join(unts)]
    for la in lats:
        for lo in lons:
            rows.append(",".join((["2026-10-08T09:00:00Z"] if time else []) + (["0.0"] if alt else []) + [str(la), str(lo), str(fn(la, lo))]))
    return "\n".join(rows)


def fake_erddap(url):
    if "jplMURSST41" in url:
        return _csv(np.round(np.arange(24.5, 27.001, 0.02), 4), np.round(np.arange(-81.0, -78.499, 0.02), 4), "analysed_sst", lambda la, lo: 28.0)
    if "nesdisVHNnoaa20chlaDaily" in url:
        return _csv(np.round(np.arange(24.5, 27.001, 0.08), 4), np.round(np.arange(-81.0, -78.499, 0.08), 4), "chlor_a", lambda la, lo: 0.12, "mg m^-3", alt=True)
    if "ETOPO" in url:
        return _csv(np.round(np.arange(24.5, 27.001, 0.0208), 4), np.round(np.arange(-81.0, -78.499, 0.0208), 4), "z", lambda la, lo: -22.0 if lo > -80.2 else -5.0, "m", time=False)
    raise RuntimeError(url)


def fake_arcgis(url, params):
    if "/12/" in url:
        return {"features": [{"attributes": {"Name": "Miss Dania Beach", "MatCat": "Vessel", "MatDescrip": "Freighter 126'",
                                              "Depth": 71, "Relief": 27, "DeployDate": "04/29/2004", "Lat_DD": 26.01, "Long_DD": -80.0917}}]}
    if "/7/" in url:
        return {"features": [{"attributes": {"DESCRIPT": "Coral"}, "geometry": {"rings": [_square(-80.06, 25.60, -80.04, 25.64)]}}]}
    raise RuntimeError("FWRI server unreachable")


def _sources():
    return json.loads((ROOT / "config/sources.json").read_text())


def _profiles():
    return [json.loads(p.read_text()) for p in sorted((ROOT / "data/species").glob("*.json"))]


def test_yellowtail_finds_the_wreck_and_the_natural_reef():
    errs = []
    lay = L.load_layers(_sources(), errs, fetch=fake_erddap, fetch_arc=fake_arcgis)
    assert errs == [] and lay["structure_stats"]["cells_wreck"] == 1 and lay["structure_stats"]["cells_natural_reef"] >= 1
    registry = json.loads((ROOT / "data/parameters.json").read_text())
    out = build_fish_json(lay, [], _profiles(), registry, "2026-10-10T00:00:00+00:00")
    json.dumps(out, allow_nan=False)
    sp = {s["id"]: s for s in out["species"]}
    assert sp["yellowtail-snapper"]["status"] == "ok"
    yt = [s for s in out["spots"] if s["species"] == "yellowtail-snapper"]
    titles = " | ".join(s["title"] for s in yt)
    assert "Miss Dania Beach" in titles and "Natural reef" in titles
    wreck = [s for s in yt if "Miss Dania" in s["title"]][0]
    assert "rings" in wreck and "ring" not in wreck                      # exact cells, not a hull
    assert any("Miss Dania Beach" in r[1] for r in wreck["reasons"])
    assert any(row[0] == "Miss Dania Beach" for row in wreck["location"])


def test_yellowtail_waits_if_the_natural_reef_server_is_down():
    errs = []

    def half_down(url, params):
        if "/7/" in url:
            raise RuntimeError("FWRI server unreachable")
        return fake_arcgis(url, params)
    lay = L.load_layers(_sources(), errs, fetch=fake_erddap, fetch_arc=half_down)
    assert lay["structure_type"] is None and any("structure" in e for e in errs)
    registry = json.loads((ROOT / "data/parameters.json").read_text())
    out = build_fish_json(lay, [], _profiles(), registry, "2026-10-10T00:00:00+00:00")
    yt = [s for s in out["species"] if s["id"] == "yellowtail-snapper"][0]
    assert yt["status"] == "unavailable" and "reef" in yt["message"]
