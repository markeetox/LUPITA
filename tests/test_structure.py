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


def _cw_square(lon0, lat0, lon1, lat1):
    """Clockwise ring: how ArcGIS stores an outer boundary."""
    return [[lon0, lat0], [lon0, lat1], [lon1, lat1], [lon1, lat0], [lon0, lat0]]


def _zone(name, ring, rule="Recreational Fishing Prohibited"):
    return {"attributes": {"Site_Name": name, "Mgmt_Agen": "Test Agency", "Fish_Rstr": rule, "URL": "https://example.org",
                           "Estab_Yr": 2001, "Prot_Lvl": "No Take", "Gov_Level": "Federal"}, "geometry": {"rings": [ring]}}


FAR_ZONE = _zone("Far Zone", _cw_square(-80.9, 26.8, -80.8, 26.9))
SEEN = []


def fake_arcgis(url, params):
    SEEN.append((url, params))
    if "NOAA_MPA_Inventory" in url:
        return {"features": [FAR_ZONE]}
    if "/12/" in url:
        return {"features": [{"attributes": {"Name": "Miss Dania Beach", "MatCat": "Vessel", "MatDescrip": "Freighter 126'",
                                              "Depth": 71, "Relief": 27, "DeployDate": "04/29/2004", "Lat_DD": 26.01, "Long_DD": -80.0917}}]}
    if "/16/" in url:
        return {"features": [{"attributes": {"ClassLv1": "Aggregate Reef"}, "geometry": {"rings": [_square(-80.06, 25.60, -80.04, 25.64)]}}]}
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
        if "/16/" in url:
            raise RuntimeError("reef server unreachable")
        return fake_arcgis(url, params)
    lay = L.load_layers(_sources(), errs, fetch=fake_erddap, fetch_arc=half_down)
    assert lay["structure_type"] is None and any("structure" in e for e in errs)
    registry = json.loads((ROOT / "data/parameters.json").read_text())
    out = build_fish_json(lay, [], _profiles(), registry, "2026-10-10T00:00:00+00:00")
    yt = [s for s in out["species"] if s["id"] == "yellowtail-snapper"][0]
    assert yt["status"] == "unavailable" and "reef" in yt["message"]


def test_natural_reef_query_filters_to_reef_classes_only():
    SEEN.clear()
    L.load_layers(_sources(), [], fetch=fake_erddap, fetch_arc=fake_arcgis)
    nat = [p for u, p in SEEN if "/16/" in u][0]
    assert "ClassLv1 IN" in nat["where"] and "Aggregate Reef" in nat["where"]
    assert "Seagrass" not in nat["where"] and "Unconsolidated" not in nat["where"]
    assert nat["returnGeometry"] == "true" and nat["resultRecordCount"] == 2000


# ---- patches and the reef depth gate ----
def fake_arcgis_big(url, params):
    if "NOAA_MPA_Inventory" in url:
        return {"features": [FAR_ZONE]}
    if "/12/" in url:
        return {"features": [
            {"attributes": {"Name": "Bay Reef", "MatCat": "Module", "Depth": 15, "Relief": 3, "Lat_DD": 25.5, "Long_DD": -80.5}},   # shallow bay (5 m)
            {"attributes": {"Name": "Reef A", "MatCat": "Module", "Depth": 60, "Relief": 4, "Lat_DD": 25.02, "Long_DD": -79.9}},
            {"attributes": {"Name": "Reef B", "MatCat": "Module", "Depth": 60, "Relief": 9, "Lat_DD": 25.02, "Long_DD": -79.88}}]}
    if "/16/" in url:   # a reef tract about 15 x 15 cells in size
        return {"features": [{"attributes": {"ClassLv1": "Aggregate Reef"}, "geometry": {"rings": [_square(-80.1, 25.0, -79.8, 25.3)]}}]}
    raise RuntimeError(url)


def test_split_component_caps_patch_size():
    from pipeline.scoring import split_component
    comp = [(i, j) for i in range(10) for j in range(10)]
    parts = split_component(comp, 6)
    assert len(parts) == 4 and sum(len(p) for p in parts) == 100 and max(len(p) for p in parts) <= 36
    assert split_component(comp[:20], 6) == [comp[:20]]          # small areas stay whole
    assert split_component(comp, None) == [comp]


def test_big_reef_tract_becomes_patches_and_shallow_bay_reef_is_excluded():
    lay = L.load_layers(_sources(), [], fetch=fake_erddap, fetch_arc=fake_arcgis_big)
    registry = json.loads((ROOT / "data/parameters.json").read_text())
    out = build_fish_json(lay, [], _profiles(), registry, "2026-10-10T00:00:00+00:00")
    json.dump(out, open("/dev/null", "w"), allow_nan=False)
    yt = [s for s in out["spots"] if s["species"] == "yellowtail-snapper"]
    assert len(yt) > 1                                              # not one giant area
    assert max(len(s["rings"]) for s in yt) <= 36                   # every patch is at most 6 x 6 cells
    assert not any("Bay Reef" in s["title"] for s in yt)            # 5 m deep: gated out
    assert any(s["title"].startswith("Reef") for s in yt)           # a patch is named for the structure in it
    patch = [s for s in yt if s["title"].startswith("Reef B")]
    if patch:                                                       # tallest structure wins the name, the other is counted
        assert "and 1 more" in patch[0]["title"]


def test_position_and_nearest_inlet_rows():
    from pipeline.grid import bearing_deg, compass
    assert compass(bearing_deg(25.0, -80.0, 25.0, -79.9)) == "E"          # due east
    assert compass(bearing_deg(25.0, -80.0, 25.1, -80.0)) == "N"
    places = json.loads((ROOT / "config/places.json").read_text())["places"]
    lay = L.load_layers(_sources(), [], fetch=fake_erddap, fetch_arc=fake_arcgis)
    registry = json.loads((ROOT / "data/parameters.json").read_text())
    out = build_fish_json(lay, [], _profiles(), registry, "t", places)
    row = {r[0]: r[1] for r in out["spots"][0]["location"]}
    assert "N," in row["Position"] and "W" in row["Position"]
    assert "nm" in row["Nearest inlet"] and "approximate" in row["Nearest inlet"]


# ---- no-fishing areas ----
def _with_zones(zones, fail=False):
    def fetch(url, params):
        if "NOAA_MPA_Inventory" in url:
            if fail:
                raise RuntimeError("MPA server unreachable")
            return {"features": zones}
        return fake_arcgis(url, params)
    return fetch


def _run_with(fetch_arc):
    errs = []
    lay = L.load_layers(_sources(), errs, fetch=fake_erddap, fetch_arc=fetch_arc)
    registry = json.loads((ROOT / "data/parameters.json").read_text())
    out = build_fish_json(lay, [], _profiles(), registry, "2026-10-10T00:00:00+00:00")
    json.dumps(out, allow_nan=False)
    return lay, out, errs


def test_wreck_inside_a_no_fishing_zone_is_never_recommended():
    zone = _zone("Test Sanctuary Zone", _cw_square(-80.11, 25.99, -80.07, 26.03))   # covers the wreck's cell
    lay, out, errs = _run_with(_with_zones([FAR_ZONE, zone]))
    assert errs == [] and lay["closure_checked"]
    titles = " | ".join(s["title"] for s in out["spots"] if s["species"] == "yellowtail-snapper")
    assert "Miss Dania Beach" not in titles and "Natural reef" in titles          # the other reef is still offered


def test_areas_clear_of_zones_say_so_and_borderline_areas_warn():
    # the zone swallows the reef cells at lon -80.06 (excluded) and covers about 40% of those at -80.04 (kept, flagged)
    zone = _zone("Edge Zone", _cw_square(-80.075, 25.55, -80.042, 25.70))
    lay, out, _ = _run_with(_with_zones([FAR_ZONE, zone]))
    rows = {s["title"]: {r[0]: r[1] for r in s["location"]} for s in out["spots"] if s["species"] == "yellowtail-snapper"}
    wreck = [v for k, v in rows.items() if "Miss Dania" in k][0]
    assert wreck["No-fishing zones"].startswith("None mapped")
    flagged = [s for s in out["spots"] if any(r[0] == "No-fishing zone" for r in s["location"])]
    assert flagged and any("Edge Zone" in r[1] and "prohibited" in r[1] for r in flagged[0]["reasons"])


def test_if_the_closure_source_is_down_the_popups_say_it_was_not_checked():
    lay, out, errs = _run_with(_with_zones([], fail=True))
    assert any("closures" in e for e in errs) and not lay["closure_checked"]
    spot = out["spots"][0]
    assert any(r[0] == "No-fishing check" and "Could not be checked" in r[1] for r in spot["location"])


def test_zero_zones_is_treated_as_a_broken_filter_not_as_all_clear():
    lay, out, errs = _run_with(_with_zones([]))
    assert any("filter may not match" in e for e in errs) and not lay["closure_checked"]
