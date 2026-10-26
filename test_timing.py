import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pipeline import moon, timing, weather
from pipeline.predict import build_fish_json
from tests.test_predict import make_layers
from tests.test_snook import BUOYS, PLACES, REGISTRY

ROOT = Path(__file__).resolve().parent.parent
PROFILES = {p["id"]: p for p in (json.loads(f.read_text()) for f in sorted((ROOT / "data/species").glob("*.json")))}
UTC = timezone.utc
H = timedelta(hours=1)


def dt(*a):
    return datetime(*a, tzinfo=UTC)


# ---------- moon ----------
def test_moon_times_match_known_dates():
    cases = [(dt(2024, 10, 15), "full", dt(2024, 10, 17, 11, 26)), (dt(2024, 10, 1), "new", dt(2024, 10, 2, 18, 49)),
             (dt(2025, 3, 12), "full", dt(2025, 3, 14, 6, 55))]
    for t, kind, truth in cases:
        assert abs((moon.nearest(t, kind) - truth).total_seconds()) < 30 * 60


def test_moon_description_and_sign():
    full = dt(2024, 10, 17, 11, 26)
    assert moon.illumination(full) > 0.99 and moon.phase_name(full) == "full moon"
    assert moon.days_from_full(full - 2 * 24 * H) < -1.9 and moon.days_from_full(full + 3 * 24 * H) > 2.9
    assert "full moon in 2 days" in moon.describe(full - 2 * 24 * H)


# ---------- cold fronts ----------
def rows(now, front_at=None, hours=60, drop=6.0, rise=5.0, wind_after=340, speed_after=8.0):
    """NDBC-style rows, newest first, 10-minute data. Wind south-west and steady until front_at, then northerly."""
    out = []
    for k in range(hours * 6):
        t = now - timedelta(minutes=10 * k)
        after = front_at is not None and t >= front_at
        h_after = (t - front_at).total_seconds() / 3600 if after else 0
        out.append({"time": t, "WDIR": float(wind_after if after else 200), "WSPD": speed_after if after else 5.0,
                    "ATMP": 27.0 - (drop * min(1, h_after / 6) if after else 0), "PRES": 1012.0 + (rise * min(1, h_after / 6) if after else 0)})
    return out


def test_a_real_front_is_found_near_the_time_the_wind_turned():
    now = dt(2026, 12, 10, 12)
    ft = now - 6 * H
    hist = {s: rows(now, ft) for s in ("VAKF1", "LKWF1", "PEGF1")}
    ev = weather.assess_observed(hist, now)
    assert ev and abs((ev["time"] - ft).total_seconds()) < 3600 and ev["temp_drop_c"] >= 3 and ev["stations"] == 3
    a = weather.assess(hist, None, now)
    assert a["state"] == "just_passed" and a["source"] == "observed" and "passed about 6 h ago" in weather.front_text(a, now)


def test_no_front_when_nothing_changes_or_only_the_wind_turns():
    now = dt(2026, 12, 10, 12)
    assert weather.assess_observed({"VAKF1": rows(now)}, now) is None
    assert weather.assess_observed({"VAKF1": rows(now, now - 6 * H, drop=0.5, rise=0.2)}, now) is None   # wind alone is not a front
    assert weather.assess({"VAKF1": rows(now)}, None, now)["state"] == "none"


def test_two_agreeing_buoys_are_needed_when_several_report():
    now = dt(2026, 12, 10, 12)
    hist = {"VAKF1": rows(now, now - 6 * H), "LKWF1": rows(now), "PEGF1": rows(now)}
    assert weather.assess_observed(hist, now) is None                     # one buoy alone is not trusted


def nws(now, front_in=20):
    periods = []
    for k in range(0, 48):
        t = now + k * H
        after = k >= front_in
        periods.append({"startTime": t.isoformat(), "temperature": round(62 if after else 80), "temperatureUnit": "F",
                        "windSpeed": "15 to 20 mph" if after else "5 to 10 mph", "windDirection": "NNW" if after else "SW"})
    return {"properties": {"periods": periods}}


def test_nws_forecast_parsing_and_an_approaching_front():
    now = dt(2026, 12, 10, 12)
    obs = weather.parse_nws_hourly(nws(now))
    assert abs(obs[0]["atmp"] - (80 - 32) * 5 / 9) < 0.1 and abs(obs[0]["wspd"] - 10 * 0.44704) < 0.01 and obs[0]["wdir"] == 225
    a = weather.assess({"VAKF1": rows(now)}, obs, now)
    assert a["state"] == "approaching" and a["source"] == "forecast" and 19 <= (a["front_time"] - now).total_seconds() / 3600 <= 21
    assert "forecast in about 20 h" in weather.front_text(a, now)


def test_front_states_over_time():
    ft = dt(2026, 12, 10, 12)
    f = lambda h: weather.front_state_at(ft, ft + timedelta(hours=h))
    assert [f(-30), f(-10), f(3), f(20), f(60)] == ["none", "approaching", "just_passed", "lull", "none"]


# ---------- timing windows ----------
def tide_events(t0):
    ev = []
    for k, typ in enumerate("HLHLHL"):
        ev.append({"time": t0 + timedelta(hours=6.2 * k), "type": typ, "height_m": 0.5})
    return ev


def cond(now, hi_at, front=None):
    st = {"id": "8723214", "name": "Virginia Key", "lat": 25.731, "lon": -80.162}
    return {"now": now, "tides": [{"station": st, "events": tide_events(hi_at - 7 * H)[:0] or [
        {"time": hi_at + timedelta(hours=6.2 * k - 6.2), "type": "HL"[(k + 1) % 2], "height_m": 0.5} for k in range(0, 8)]}], "front": front or {"front_time": None, "state": "none"}}


def test_snook_best_window_lands_on_a_falling_tide_at_dusk():
    now = dt(2026, 7, 15, 15)                     # 11 am local; sunset is about 8:10 pm local = 00:10 UTC
    c = cond(now, dt(2026, 7, 15, 22))            # high tide at 22:00 UTC, so it falls from about 22:30 on
    t = timing.for_spot(PROFILES["snook"], 25.767, -80.135, c)
    w = t["window"]
    start, end = datetime.fromisoformat(w["start"]), datetime.fromisoformat(w["end"])
    assert dt(2026, 7, 15, 22, 30) <= start <= dt(2026, 7, 16, 1) and (end - start) <= 3 * H and w["score"] > 0.9
    assert any("dusk" in x for x in t["why"]) and any("falling" in x for x in t["why"])
    assert len(t["scores"]) == 24 and max(t["scores"]) > min(t["scores"]) and t["evidence"] == "angler_lore"


def test_fish_without_timing_evidence_say_nothing_instead_of_guessing():
    c = cond(dt(2026, 7, 15, 15), dt(2026, 7, 15, 22))
    assert timing.for_spot(PROFILES["mahi-mahi"], 25.5, -79.9, c) is None
    assert timing.for_spot(PROFILES["cobia"], 25.5, -79.9, c) is None


def test_moon_window_only_counts_in_season_and_only_near_the_full_moon():
    full = moon.nearest(dt(2026, 10, 20), "full")
    cfg = PROFILES["wahoo"]["timing"]
    near = timing.components(cfg, full - 24 * H, 25.5, -79.9, {})
    far = timing.components(cfg, full + 10 * 24 * H, 25.5, -79.9, {})
    assert near["moon"][0] == 1.0 and near["moon"][1] and far["moon"][0] == 0.6 and far["moon"][1] is None
    jan = timing.components(cfg, dt(2027, 1, 20), 25.5, -79.9, {})
    assert "moon" not in jan                                              # outside the months the report covers


def test_a_front_creates_a_window_for_sailfish_and_nothing_otherwise():
    now = dt(2026, 12, 10, 12)
    none = timing.for_spot(PROFILES["sailfish"], 25.5, -79.9, {"now": now, "tides": [], "front": {"front_time": None, "state": "none"}})
    assert none is None                                                   # no timing information without a front
    c = {"now": now, "tides": [], "front": {"front_time": now + 14 * H, "state": "approaching", "source": "forecast"}}
    t = timing.for_spot(PROFILES["sailfish"], 25.5, -79.9, c)
    assert t and t["window"] and any("windier" in x or "Windier" in x for x in t["why"])
    assert datetime.fromisoformat(t["window"]["start"]) >= now + 12 * H  # the best time is after the front goes through


# ---------- integration and file checks ----------
def test_spots_carry_timing_moon_and_front_context():
    now = dt(2026, 7, 16, 0)
    c = cond(now, dt(2026, 7, 15, 21), front={"front_time": now + 10 * H, "state": "approaching", "source": "forecast"})
    out = build_fish_json(make_layers(), BUOYS, list(PROFILES.values()), REGISTRY, now.isoformat(), PLACES, c)
    json.dumps(out, allow_nan=False)
    assert out["conditions"]["front"]["state"] == "approaching" and "lit" in out["conditions"]["moon"]["text"]
    snook = [s for s in out["spots"] if s["species"] == "snook"]
    assert snook and snook[0]["timing"] and snook[0]["timing"]["scores"]
    rows_ = {r[0]: r[1] for r in snook[0]["location"]}
    assert "lit" in rows_["Moon"] and "forecast in about 10 h" in rows_["Weather"]
    assert all(s["timing"] is None for s in out["spots"] if s["species"] in ("mahi-mahi", "cobia"))


def test_every_timing_block_is_well_formed_and_cites_its_evidence():
    for sid, p in PROFILES.items():
        cfg = p.get("timing")
        if not cfg:
            continue
        assert cfg["status"] == "angler_lore" and cfg["sources"] and cfg["note"], sid
        for name, keys in (("light", {"dawn", "day", "dusk", "night"}), ("tide", {"rising", "falling", "slack_high", "slack_low"}),
                           ("front", {"approaching", "just_passed", "lull"})):
            c = cfg.get(name)
            if not c:
                continue
            assert set(c["map"]) <= keys and all(0 <= v <= 1 for v in c["map"].values()), (sid, name)
            for k, v in c["map"].items():
                if v >= 0.8:
                    assert (c.get("text") or {}).get(k), f"{sid}.{name}.{k} scores high but has no explanation text"
        m = cfg.get("moon")
        if m:
            assert m["from_days"] < m["to_days"] and all(1 <= x <= 12 for x in m["months"]) and m["text"], sid
