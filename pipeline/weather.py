"""Cold-front detection from buoy history and the National Weather Service hourly forecast."""
from __future__ import annotations

import re
import statistics
from datetime import datetime, timedelta, timezone

from pipeline import http

UTC = timezone.utc
COMPASS = {"N": 0, "NNE": 22.5, "NE": 45, "ENE": 67.5, "E": 90, "ESE": 112.5, "SE": 135, "SSE": 157.5, "S": 180,
           "SSW": 202.5, "SW": 225, "WSW": 247.5, "W": 270, "WNW": 292.5, "NW": 315, "NNW": 337.5}
NORTH_MIN_MS = 4.0          # about 8 kn: the wind that follows a front
TEMP_DROP_C = 3.0           # air temperature fall after the wind shift
PRESSURE_RISE_HPA = 1.5     # pressure rise after the front goes through
MPH_TO_MS = 0.44704


def is_northerly(d: float) -> bool:
    return d >= 300 or d <= 60            # NW through NE


def is_southwesterly(d: float) -> bool:
    return 135 <= d <= 300                # SE through W: the wind ahead of a front


def rows_to_obs(rows: list[dict]) -> list[dict]:
    """NDBC rows (newest first) -> observations oldest first."""
    out = [{"time": r["time"], "wdir": r.get("WDIR"), "wspd": r.get("WSPD"), "atmp": r.get("ATMP"), "pres": r.get("PRES")} for r in rows]
    return sorted(out, key=lambda o: o["time"])


def detect_passage(obs: list[dict], t_from: datetime, t_to: datetime):
    """Time a front went through, or None. A front is a wind shift from the south/west side to a firm northerly,
    followed by a fall in air temperature or a rise in pressure. obs must be oldest first."""
    for i, o in enumerate(obs):
        if not (t_from <= o["time"] <= t_to) or o["wdir"] is None or o["wspd"] is None:
            continue
        if not (is_northerly(o["wdir"]) and o["wspd"] >= NORTH_MIN_MS):
            continue
        prior = [p for p in obs if o["time"] - timedelta(hours=12) <= p["time"] < o["time"] and p["wdir"] is not None]
        if len(prior) < 3 or sum(is_southwesterly(p["wdir"]) for p in prior) / len(prior) < 0.5:
            continue
        before = [p["atmp"] for p in prior if p["atmp"] is not None]
        after = [p["atmp"] for p in obs if o["time"] <= p["time"] <= o["time"] + timedelta(hours=12) and p["atmp"] is not None]
        drop = (max(before) - min(after)) if before and after else None
        pb = [p["pres"] for p in prior if p["pres"] is not None]
        pa = [p["pres"] for p in obs if o["time"] <= p["time"] <= o["time"] + timedelta(hours=6) and p["pres"] is not None]
        rise = (max(pa) - min(pb)) if pb and pa else None
        if (drop is not None and drop >= TEMP_DROP_C) or (rise is not None and rise >= PRESSURE_RISE_HPA):
            j = i                                              # report when the wind turned, not when the evidence built up
            while j > 0 and obs[j - 1]["wdir"] is not None and is_northerly(obs[j - 1]["wdir"]):
                j -= 1
            return {"time": obs[j]["time"], "temp_drop_c": drop, "pressure_rise_hpa": rise}
    return None


def assess_observed(history: dict, now: datetime):
    """Front passage seen in the last 48 hours at the buoys. history: {station: ndbc rows}."""
    events, with_data = [], 0
    for rows in history.values():
        obs = rows_to_obs(rows)
        if sum(1 for o in obs if o["wdir"] is not None and o["atmp"] is not None) < 6:
            continue
        with_data += 1
        e = detect_passage(obs, now - timedelta(hours=48), now)
        if e:
            events.append(e)
    if not events or len(events) < min(2, with_data):
        return None                                           # with 2+ stations reporting, at least 2 must agree
    times = sorted(e["time"] for e in events)
    return {"time": times[len(times) // 2], "temp_drop_c": max((e["temp_drop_c"] or 0) for e in events),
            "pressure_rise_hpa": max((e["pressure_rise_hpa"] or 0) for e in events), "stations": len(events)}


def parse_nws_hourly(payload: dict) -> list[dict]:
    out = []
    for p in payload.get("properties", {}).get("periods", []):
        nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", str(p.get("windSpeed", "")))]
        d = COMPASS.get(str(p.get("windDirection", "")).upper())
        temp = p.get("temperature")
        if temp is not None and str(p.get("temperatureUnit", "F")).upper() == "F":
            temp = (float(temp) - 32) * 5 / 9
        t = datetime.fromisoformat(p["startTime"]).astimezone(UTC)
        out.append({"time": t, "wdir": d, "wspd": max(nums) * MPH_TO_MS if nums else None, "atmp": temp, "pres": None})
    return sorted(out, key=lambda o: o["time"])


def fetch_forecast(lat: float, lon: float, fetch=http.get) -> dict:
    h = {"Accept": "application/geo+json"}
    pts = fetch(f"https://api.weather.gov/points/{lat:.4f},{lon:.4f}", headers=h, attempts=2, base_delay=5).json()
    return fetch(pts["properties"]["forecastHourly"], headers=h, attempts=2, base_delay=5).json()


def front_state_at(front_time, t: datetime) -> str:
    """'approaching' (the 24 h before), 'just_passed' (0-12 h after), 'lull' (12-48 h after) or 'none'."""
    if front_time is None:
        return "none"
    h = (t - front_time).total_seconds() / 3600
    return "approaching" if -24 <= h < 0 else "just_passed" if 0 <= h < 12 else "lull" if 12 <= h < 48 else "none"


def assess(history: dict, forecast_obs, now: datetime) -> dict:
    """The front that matters now. A forecast front ahead wins; otherwise one seen in the last 48 hours."""
    observed = assess_observed(history, now)
    forecast = None
    if forecast_obs:
        recent = []
        for rows in history.values():                           # buoy obs give the forecast the 'before' it needs
            recent = [o for o in rows_to_obs(rows) if o["time"] <= now and o["wdir"] is not None]
            if len(recent) >= 6:
                break
        forecast = detect_passage(sorted(recent + forecast_obs, key=lambda o: o["time"]), now, now + timedelta(hours=36))
    ev, src = (forecast, "forecast") if forecast else (observed, "observed") if observed else (None, None)
    ft = ev["time"] if ev else None
    return {"front_time": ft, "source": src, "state": front_state_at(ft, now),
            "temp_drop_c": ev.get("temp_drop_c") if ev else None, "pressure_rise_hpa": ev.get("pressure_rise_hpa") if ev else None}


def front_text(front: dict, now: datetime) -> str | None:
    ft = front.get("front_time")
    if ft is None or front["state"] == "none":
        return None
    h = abs((ft - now).total_seconds()) / 3600
    if front["state"] == "approaching":
        return f"A cold front is forecast in about {round(h)} h"
    return f"A cold front passed about {round(h)} h ago ({front['source']})"
