import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pytest

from pipeline import astro, sites, tides
from pipeline.conditions import load_conditions
from pipeline.predict import build_fish_json, closure_rows
from tests.test_predict import make_layers

ROOT = Path(__file__).resolve().parent.parent
REG = {p["key"]: p for p in json.loads((ROOT / "data/parameters.json").read_text())["parameters"]}
REGISTRY = json.loads((ROOT / "data/parameters.json").read_text())
SNOOK = json.loads((ROOT / "data/species/snook.json").read_text())
PLACES = json.loads((ROOT / "config/places.json").read_text())["places"]
UTC = timezone.utc


def dt(*a):
    return datetime(*a, tzinfo=UTC)


# ---------- light ----------
def test_sunrise_and_sunset_match_reference_for_miami():
    sr, ss = astro.sun_times(dt(2026, 10, 11).date(), 25.77, -80.13)
    assert abs((sr - dt(2026, 10, 11, 11, 17)).total_seconds()) < 300
    assert abs((ss - dt(2026, 10, 11, 22, 56)).total_seconds()) < 300


def test_light_phases():
    f = lambda *a: astro.light_phase(dt(*a), 25.77, -80.13)
    assert f(2026, 10, 11, 11, 30) == "dawn" and f(2026, 10, 11, 16, 0) == "day"
    assert f(2026, 10, 11, 22, 30) == "dusk" and f(2026, 10, 12, 3, 0) == "night"


# ---------- tides ----------
def _ev(t, typ):
    return {"time": t, "type": typ, "height_m": 0.5}


EVENTS = [_ev(dt(2026, 10, 11, 6, 0), "L"), _ev(dt(2026, 10, 11, 12, 15), "H"),
          _ev(dt(2026, 10, 11, 18, 30), "L"), _ev(dt(2026, 10, 12, 0, 45), "H")]


def test_tide_stage():
    assert tides.stage_at(EVENTS, dt(2026, 10, 11, 9, 0)) == "rising"
    assert tides.stage_at(EVENTS, dt(2026, 10, 11, 14, 0)) == "falling"
    assert tides.stage_at(EVENTS, dt(2026, 10, 11, 12, 30)) == "slack_high"
    assert tides.stage_at(EVENTS, dt(2026, 10, 11, 18, 10)) == "slack_low"
    assert tides.stage_at(EVENTS, dt(2026, 10, 13, 0, 0)) is None            # events do not reach this moment
    assert [e["type"] for e in tides.next_events(EVENTS, dt(2026, 10, 11, 9, 0), 2)] == ["H", "L"]


def test_parse_hilo_and_errors():
    ev = tides.parse_hilo({"predictions": [{"t": "2026-10-11 09:20", "v": "-0.02", "type": "L"}, {"t": "2026-10-11 03:12", "v": "0.753", "type": "H"}]})
    assert [e["type"] for e in ev] == ["H", "L"] and ev[0]["time"].tzinfo is not None
    with pytest.raises(RuntimeError):
        tides.parse_hilo({"error": {"message": "No data was found"}})


def test_a_tide_station_that_fails_is_recorded_not_fatal():
    errs = []
    cond = load_conditions([{"id": "1", "name": "A", "lat": 25, "lon": -80}, {"id": "2", "name": "B", "lat": 26, "lon": -80}], dt(2026, 10, 11),
                           errs, fetch=lambda sid, now: (_ for _ in ()).throw(RuntimeError("down")) if sid == "1" else {"predictions": [{"t": "2026-10-11 03:12", "v": "0.7", "type": "H"}]})
    assert len(cond["tides"]) == 1 and len(errs) == 1 and "tides 1" in errs[0]


# ---------- site scoring ----------
def conditions(now, falling=True):
    ev = ([_ev(now.replace(hour=21, minute=0) - __import__("datetime").timedelta(days=1), "H"), _ev(now + __import__("datetime").timedelta(hours=3), "L")]
          if falling else
          [_ev(now - __import__("datetime").timedelta(hours=3), "L"), _ev(now + __import__("datetime").timedelta(hours=3), "H")])
    return {"now": now, "tides": [{"station": {"id": "8723214", "name": "Virginia Key", "lat": 25.731, "lon": -80.162}, "events": sorted(ev, key=lambda e: e["time"])}]}


BUOYS = [{"station": "VAKF1", "name": "Virginia Key, FL", "ok": True, "lat": 25.731, "lon": -80.162, "water_temp_c": 29.9}]


def run(now, falling=True, buoys=BUOYS, cond="auto", layers=None):
    ctx = {"layers": layers or make_layers(), "buoys": buoys, "conditions": conditions(now, falling) if cond == "auto" else cond}
    return sites.score_sites(SNOOK, PLACES, ctx, REG, closure_rows)


def test_a_summer_dusk_on_a_falling_tide_scores_much_higher_than_a_winter_midday_rising_tide():
    good = run(dt(2026, 7, 16, 0, 0), falling=True)                     # 8 pm local, July
    bad = run(dt(2026, 1, 15, 17, 0), falling=False)                    # noon local, January
    assert good["best"] > 0.9 and good["best"] > bad["best"] + 0.15
    top = good["items"][0]
    texts = " ".join(r[1] for r in top["reasons"])
    assert "falling" in texts and "dusk" in texts and "spawning" in texts and "inlet" in texts
    rows = {r[0]: r[1] for r in top["location"]}
    assert {"Position", "Water temp", "Tide", "Light", "As of"} <= set(rows) and "Virginia Key" in rows["Tide"]
    assert top["title"].endswith("(inlet)") and len(top["ring"]) == 25 and top["confidence"] == "Low"   # capped until validated


def test_cold_water_is_a_hard_stop_not_just_a_lower_score():
    cold = [dict(BUOYS[0], water_temp_c=12.0)]
    L = make_layers()
    L["sst_c"][:] = np.nan                                  # no satellite fallback: only the cold buoy speaks
    res = run(dt(2026, 7, 16, 0, 0), buoys=cold, layers=L)
    assert res["items"] == [] and "outside the range this fish tolerates" in res["note"] and res["unavailable"] == ""


def test_missing_tides_lowers_coverage_and_says_so():
    res = run(dt(2026, 7, 16, 0, 0), cond={"now": dt(2026, 7, 16, 0, 0), "tides": []})
    assert res["items"] and all(it["data_coverage"] < 1 for it in res["items"])
    assert any("Tide predictions could not be loaded" in r[1] for r in res["items"][0]["reasons"])


def test_site_inside_a_no_fishing_zone_is_never_offered():
    L = make_layers()
    cover = np.zeros(L["sst_c"].shape)
    gc = [p for p in PLACES if p["name"] == "Government Cut"][0]
    i = int(np.argmin(abs(L["lats"] - gc["lat"]))) if gc["lat"] <= L["lats"][-1] else None
    if i is None:                                   # test grid does not reach Government Cut: use a place it does contain
        pytest.skip("test grid does not include the site")
    L["closure_cover"], L["closure_info"], L["closure_checked"] = cover, {}, True
    j = int(np.argmin(abs(L["lons"] - gc["lon"])))
    cover[i, j] = 1.0
    names = [it["title"] for it in run(dt(2026, 7, 16, 0, 0), layers=L)["items"]]
    assert "Government Cut (inlet)" not in names


def test_build_fish_json_includes_snook_spots_and_is_valid_json():
    L = make_layers()
    profiles = [json.loads(p.read_text()) for p in sorted((ROOT / "data/species").glob("*.json"))]
    out = build_fish_json(L, BUOYS, profiles, REGISTRY, "2026-07-16T00:00:00+00:00", PLACES, conditions(dt(2026, 7, 16, 0, 0)))
    json.dumps(out, allow_nan=False)
    sp = {s["id"]: s for s in out["species"]}
    assert sp["snook"]["status"] == "ok" and sp["snook"]["spots"] > 0
    snook = [s for s in out["spots"] if s["species"] == "snook"]
    assert all(s["id"].startswith("snook-") and s["ring"] for s in snook)
    assert any(r[0] == "No-fishing check" for r in snook[0]["location"])      # closure data was not loaded in this fake run


def test_without_site_list_snook_is_unavailable_not_guessed():
    profiles = [json.loads(p.read_text()) for p in sorted((ROOT / "data/species").glob("*.json"))]
    out = build_fish_json(make_layers(), BUOYS, profiles, REGISTRY, "t")
    s = {x["id"]: x for x in out["species"]}["snook"]
    assert s["status"] == "unavailable" and "site" in s["message"]


def test_a_site_with_no_water_temperature_at_all_is_skipped():
    L = make_layers()
    L["sst_c"][:] = np.nan
    res = run(dt(2026, 7, 16, 0, 0), buoys=[], layers=L)
    assert res["items"] == []                                # cannot check the cold limit, so it does not guess
