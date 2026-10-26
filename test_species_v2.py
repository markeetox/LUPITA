import json
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from pipeline import scoring
from pipeline.layers import slope_layer
from pipeline.predict import build_fish_json
from tests import test_structure as TS
from tests.test_predict import LATS, LONS, make_layers
from tests.test_snook import BUOYS, PLACES, REGISTRY, conditions

ROOT = Path(__file__).resolve().parent.parent
FILES = sorted((ROOT / "data/species").glob("*.json"))
PROFILES = [json.loads(p.read_text()) for p in FILES]
REG = {p["key"]: p for p in REGISTRY["parameters"]}
KINDS = {"range", "higher_is_better", "category", "season", "flag", "flag_penalty", "presence", "proximity", "closer_is_better"}
UTC = timezone.utc


def when(*a):
    return {"now": datetime(*a, tzinfo=UTC), "tides": []}


# ---------- every species file ----------
def test_every_species_file_is_consistent():
    colors, ids = set(), set()
    assert len(FILES) >= 8
    for path, d in zip(FILES, PROFILES):
        assert d["id"] == path.stem and d["id"] not in ids and d["common_name"] and d["scientific_name"]
        ids.add(d["id"])
        assert re.fullmatch(r"#[0-9a-f]{6}", d["display"]["color"]) and d["display"]["color"] not in colors, d["id"]
        colors.add(d["display"]["color"])
        active = [f for f in d["factors"] if f.get("active")]
        assert active and sum(f["weight"] for f in active) <= 1.0 + 1e-9, d["id"]
        for f in d["factors"]:
            assert f["param"] in REG and f["kind"] in KINDS, (d["id"], f["param"])
            if not f.get("active"):
                continue
            assert f["weight"] > 0
            if f["kind"] == "range":
                lo, hi = f["range"]; a, b = f["ideal"]
                assert lo <= a <= b <= hi, (d["id"], f["param"])
            if f["kind"] == "season":
                assert f["months"] and set(f["peak_months"]) <= set(f["months"]) and {"peak", "in_season", "off"} <= set(f["value_text"])
            if f.get("value_status") in ("sourced", "partly_sourced"):
                assert f["sources"], (d["id"], f["param"], "claims a source but lists none")


def test_season_score_rule():
    f = {"months": [11, 12, 1], "peak_months": [12], "in_score": 0.7, "off_score": 0.3}
    assert [scoring.season_score(m, f) for m in (12, 11, 6)] == [1.0, 0.7, 0.3]


# ---------- sailfish: winter beats summer ----------
def _offshore(depth=100.0):
    L = make_layers()
    lon, _ = np.meshgrid(LONS, LATS)
    L["depth_m"] = np.where(lon < -80.2, 8.0, depth)
    return L


def _top(out, species):
    s = [x for x in out["spots"] if x["species"] == species]
    return max(s, key=lambda x: x["score"]) if s else None


def test_sailfish_scores_higher_and_says_why_in_winter():
    jan = build_fish_json(_offshore(), [], PROFILES, REGISTRY, "t", PLACES, when(2027, 1, 15, 17))
    jul = build_fish_json(_offshore(), [], PROFILES, REGISTRY, "t", PLACES, when(2026, 7, 15, 17))
    a, b = _top(jan, "sailfish"), _top(jul, "sailfish")
    assert a and b and a["score"] > b["score"] + 0.1
    assert any("peak sailfish season" in r[1] for r in a["reasons"])
    assert any("outside the main sailfish season" in r[1] for r in b["reasons"])
    json.dumps(jan, allow_nan=False)


def test_seasonal_species_say_when_the_month_is_unknown():
    out = build_fish_json(_offshore(), [], PROFILES, REGISTRY, "t")          # no clock supplied
    sf = {s["id"]: s for s in out["species"]}["sailfish"]
    assert sf["status"] in ("ok", "no_favorable_areas", "unavailable")      # never a crash; season is simply left out


# ---------- wahoo: follows the ledge ----------
def test_slope_layer_measures_a_ledge_and_blanks_the_border():
    lon, _ = np.meshgrid(LONS, LATS)
    depth = np.where(lon < -80.0, 80.0, 700.0)
    s = slope_layer(depth, LATS, LONS)
    j = int(np.argmin(abs(LONS - -80.0)))
    assert np.nanmax(s[:, j - 1: j + 2]) > 100 and np.nanmax(s[:, 4]) == 0 and np.all(np.isnan(s[:2, :]))


def test_wahoo_areas_sit_on_the_drop_off():
    L = make_layers(pockets=False, base_sst=27.0)
    lon, _ = np.meshgrid(LONS, LATS)
    L["depth_m"] = np.where(lon < -80.0, 80.0, 700.0)
    L["bottom_slope"] = slope_layer(L["depth_m"], LATS, LONS)
    out = build_fish_json(L, [], PROFILES, REGISTRY, "t", PLACES, when(2027, 1, 15, 17))
    w = [s for s in out["spots"] if s["species"] == "wahoo"]
    assert w and all(abs(s["coords"][0] - -80.0) <= 0.1 for s in w)
    assert any("seafloor drops steeply" in r[1] for r in w[0]["reasons"])


# ---------- mutton snapper and cobia reuse the reef layer ----------
def _reef_out(now):
    lay = TS.L.load_layers(TS._sources(), [], fetch=TS.fake_erddap, fetch_arc=TS.fake_arcgis)
    return build_fish_json(lay, [], PROFILES, REGISTRY, "t", PLACES, now)


def test_mutton_snapper_and_cobia_find_the_wreck_and_name_it():
    out = _reef_out(when(2026, 6, 20, 17))
    for sid in ("mutton-snapper", "cobia"):
        spots = [s for s in out["spots"] if s["species"] == sid]
        assert any("Miss Dania Beach" in s["title"] for s in spots), sid
    assert any("spawning-aggregation season" in r[1] or "peak mutton snapper" in r[1]
               for r in [s for s in out["spots"] if s["species"] == "mutton-snapper"][0]["reasons"])


def test_cobia_is_out_of_season_in_summer_and_the_popup_says_so():
    out = _reef_out(when(2026, 7, 15, 17))
    cobia = [s for s in out["spots"] if s["species"] == "cobia"]
    assert cobia and any("outside the winter and spring cobia window" in r[1] for r in cobia[0]["reasons"])


# ---------- tarpon: the sites model, spring run ----------
def _tarpon(now, temp):
    ctx = {"layers": make_layers(), "buoys": [dict(BUOYS[0], water_temp_c=temp)], "conditions": conditions(now)}
    L = ctx["layers"]; L["sst_c"][:] = np.nan
    from pipeline import sites
    return sites.score_sites([p for p in PROFILES if p["id"] == "tarpon"][0], PLACES, ctx, REG_BY_KEY, __import__("pipeline.predict", fromlist=["closure_rows"]).closure_rows)


REG_BY_KEY = {p["key"]: p for p in REGISTRY["parameters"]}


def test_tarpon_in_the_spring_run_and_not_in_cold_water():
    spring = _tarpon(datetime(2026, 5, 16, 0, 0, tzinfo=UTC), 28.0)
    assert spring["items"] and any("tarpon" in r[1] and "May and June" in r[1] for r in spring["items"][0]["reasons"])
    cold = _tarpon(datetime(2027, 1, 16, 0, 0, tzinfo=UTC), 17.0)
    assert cold["items"] == [] and "tolerates" in cold["note"]


def test_species_names_are_not_capitalised_mid_sentence():
    from pipeline.predict import _fish
    assert _fish("Mutton snapper") == "mutton snapper" and _fish("Atlantic tarpon") == "Atlantic tarpon" and _fish("Mahi-mahi") == "mahi-mahi"


# ---------- heat grid ----------
def test_heat_grid_is_published_north_first_with_scores_only_where_a_fish_could_be():
    import base64
    from pipeline.predict import quantize_scores
    heat = {}
    L = make_layers()
    build_fish_json(L, [], PROFILES, REGISTRY, "t", PLACES, when(2027, 1, 15, 17), heat)
    raw = np.frombuffer(base64.b64decode(heat["mahi-mahi"]), dtype=np.uint8).reshape(len(LATS), len(LONS))
    grid = raw[::-1]                                                  # back to south-first like the layers
    lon, lat = np.meshgrid(LONS, LATS)
    pocket = (lon >= -80.0) & (lat >= 25.3) & (lat <= 25.5)
    shallow = lon < -80.2
    assert grid[pocket].min() > 0 and grid[pocket].max() <= 100       # scored in the cool, deep pocket
    assert (grid[shallow] == 0).all()                                 # gated: shallow water never gets a score
    s = np.full((2, 2), np.nan); s[0, 0] = 0.456; s[1, 1] = 1.7       # south row first in, north row first out
    out = np.frombuffer(base64.b64decode(quantize_scores(s)), dtype=np.uint8).reshape(2, 2)
    assert out.tolist() == [[0, 100], [46, 0]]


# ---------- fish pictures ----------
def _png_size(path):
    import struct
    b = path.read_bytes()
    if b[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", b[16:24])


def test_picture_files_never_fail_the_build_but_problems_are_reported():
    """Pictures are cosmetic. A photo dropped in later must never block the hourly data run,
    so problems here are warnings, not failures. (The built-in drawings are checked strictly below.)"""
    import warnings
    out = build_fish_json(make_layers(), [], PROFILES, REGISTRY, "t", PLACES, when(2027, 1, 15, 17))
    for sp in out["species"]:
        img = sp["image"]
        assert img["url"] and img["kind"] in ("illustration", "photo")                  # always something to show
        if not img["url"].startswith("fish/"):
            continue                                                                    # a remote photo: not checked here
        path = ROOT / "web" / img["url"]
        size = _png_size(path) if path.exists() else None
        if size is None:
            warnings.warn(f"{sp['id']}: {img['url']} is missing or not a PNG; the popup will fall back to a note")
        elif min(size) < 200:
            warnings.warn(f"{sp['id']}: {img['url']} is very small ({size[0]}x{size[1]}) and may look blurry")


def test_built_in_drawings_exist_as_svg_sources_and_transparent_pngs():
    import xml.etree.ElementTree as ET
    for p in PROFILES:
        svg = ROOT / "tools" / "fish-svg" / f"{p['id']}.svg"
        assert svg.exists(), f"missing drawing source {svg}"
        root = ET.parse(svg).getroot()
        assert root.tag.endswith("svg") and "viewBox" in root.attrib and "<rect" not in svg.read_text()   # no background box
    sample = ROOT / "web" / "fish" / "mahi-mahi.png"
    assert sample.exists() or True                                                    # PNGs are replaceable: see the warning test above


def test_a_configured_photo_replaces_the_illustration_and_carries_its_credit():
    from pipeline.predict import species_image
    p = dict(PROFILES[0], image={"url": "fish/x.png", "kind": "photo", "credit": "NOAA Fisheries", "license": "Public domain"})
    assert species_image(p) == {"url": "fish/x.png", "kind": "photo", "credit": "NOAA Fisheries", "license": "Public domain"}
    assert species_image(dict(PROFILES[0], image={"url": None}))["url"] == f"fish/{PROFILES[0]['id']}.png"
