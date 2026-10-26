import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pipeline import seastate
from pipeline.predict import build_fish_json
from tests.test_predict import make_layers
from tests.test_snook import PLACES, REGISTRY
from tests.test_timing import PROFILES, cond

ROOT = Path(__file__).resolve().parent.parent
UTC = timezone.utc
NOW = datetime(2026, 12, 10, 15, tzinfo=UTC)


def buoy(station, lat, lon, minutes_old=10, **kw):
    return {"station": station, "name": station, "ok": True, "lat": lat, "lon": lon,
            "time_utc": (NOW - timedelta(minutes=minutes_old)).isoformat(), **kw}


def test_rating_tiers_and_the_worse_of_wind_and_waves_wins():
    assert [seastate.rate(w) for w in (8, 12, 18, 25)] == ["good", "fair", "rough", "dangerous"]
    assert [seastate.rate(None, m) for m in (0.5, 0.6, 1.2, 2.0)] == ["good", "fair", "rough", "dangerous"]
    assert seastate.rate(8, 1.3) == "rough" and seastate.rate(20, 0.3) == "rough"
    assert seastate.rate(None, None) is None


def test_short_steep_waves_count_as_rougher():
    assert seastate.rate(None, 1.0, 9) == "fair" and seastate.rate(None, 1.0, 4) == "rough"
    assert seastate.rate(None, 0.5, 4) == "good"                    # small waves are never bumped


def test_conditions_come_from_the_nearest_fresh_buoys_and_say_where():
    buoys = [buoy("VAKF1", 25.731, -80.162, wind_kn=14.0, gust_kn=16.0, wind_dir_deg=40),
             buoy("41122", 26.0, -80.10, wave_height_m=0.9, wave_period_s=6.0),
             buoy("FAR", 27.5, -80.2, wind_kn=30.0, wave_height_m=3.0)]                    # too far to count
    s = seastate.from_buoys(buoys, 25.76, -80.19, NOW)
    assert s["level"] == "fair" and "NE wind 14 kn" in s["text"] and "waves 3 ft at 6 s" in s["text"]
    assert "VAKF1" in s["text"] and "waves: 41122" in s["text"] and "gusts" not in s["text"]
    assert "gusts 24" in seastate.from_buoys([buoy("A", 25.7, -80.2, wind_kn=14.0, gust_kn=24.0)], 25.76, -80.19, NOW)["text"]


def test_old_or_missing_readings_are_ignored_not_trusted():
    old = [buoy("VAKF1", 25.731, -80.162, minutes_old=400, wind_kn=30.0)]
    assert seastate.from_buoys(old, 25.76, -80.19, NOW) is None
    only_wind = seastate.from_buoys([buoy("VAKF1", 25.731, -80.162, wind_kn=9.0)], 25.76, -80.19, NOW)
    assert only_wind["level"] == "good" and only_wind["missing"] == ["waves"]


def test_wind_outlook_finds_the_strongest_wind_in_the_next_day():
    obs = [{"time": NOW + timedelta(hours=h), "wspd": 12.0 if h == 9 else 5.0, "wdir": 337.5} for h in range(0, 30)]
    o = seastate.outlook(obs, NOW)
    assert o["level"] == "rough" and o["max_wind_kn"] == 23 and "NNW" in o["text"] and "rough for most boats" in o["text"]
    assert seastate.outlook([], NOW) is None
    assert seastate.outlook([{"time": NOW + timedelta(hours=40), "wspd": 20.0, "wdir": 0}], NOW) is None      # beyond 24 h


def test_spots_and_the_summary_carry_boat_conditions():
    now = NOW
    c = cond(now, now - timedelta(hours=1))
    c["forecast"] = [{"time": now + timedelta(hours=h), "wspd": 11.0 if h == 6 else 4.0, "wdir": 315.0} for h in range(24)]
    buoys = [buoy("VAKF1", 25.731, -80.162, wind_kn=22.0, wind_dir_deg=300, water_temp_c=28.0),
             buoy("41122", 26.0, -80.10, wave_height_m=1.5, wave_period_s=7.0)]
    out = build_fish_json(make_layers(), buoys, list(PROFILES.values()), REGISTRY, now.isoformat(), PLACES, c)
    json.dumps(out, allow_nan=False)
    assert out["conditions"]["sea"]["now"]["level"] == "rough" and out["conditions"]["sea"]["outlook"]["max_wind_kn"] == 21
    spot = out["spots"][0]
    rows_ = {r[0]: r[1] for r in spot["location"]}
    assert spot["sea"]["level"] == "rough" and "Rough" in rows_["Boat conditions"] and "Forecast: winds up to 21 kn" in rows_["Wind outlook"]


def test_no_buoy_data_is_said_plainly():
    c = cond(NOW, NOW - timedelta(hours=1))
    out = build_fish_json(make_layers(), [], list(PROFILES.values()), REGISTRY, NOW.isoformat(), PLACES, c)
    spot = out["spots"][0]
    assert spot["sea"] is None and any("No recent buoy" in r[1] for r in spot["location"] if r[0] == "Boat conditions")
