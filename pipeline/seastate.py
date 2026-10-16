"""Boat conditions from buoy wind and waves, and a wind outlook from the forecast.
Separate from the fish scores: a great spot in rough seas is still rough. Thresholds are a rough guide for a typical
20-30 ft boat (not official advisory levels): always check the National Weather Service marine forecast."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pipeline.grid import haversine_km
from pipeline.sites import _clock
from pipeline.weather import COMPASS

LEVELS = ["good", "fair", "rough", "dangerous"]
WIND_KN = (12.0, 18.0, 25.0)          # below each limit -> good, fair, rough; at or above the last -> dangerous
WAVE_M = (0.6, 1.2, 2.0)              # about 2 ft, 4 ft, 6.5 ft
MS_TO_KN = 1.943844
M_TO_FT = 3.28084
MAX_AGE = timedelta(hours=3)
MAX_KM = 80.0
REGION_POINT = (25.76, -80.19)        # Miami, for the summary shown in the panel
LABEL = {"good": "Good", "fair": "Fair", "rough": "Rough", "dangerous": "Dangerous"}
UTC = timezone.utc


def _tier(value, limits) -> int:
    return sum(value >= x for x in limits)


def rate(wind_kn=None, wave_m=None, period_s=None):
    """Level name from whichever of wind and waves is known (the worse one wins); None if neither is known."""
    tiers = []
    if wind_kn is not None:
        tiers.append(_tier(wind_kn, WIND_KN))
    if wave_m is not None:
        t = _tier(wave_m, WAVE_M)
        if period_s is not None and period_s <= 5 and wave_m >= 0.9:
            t += 1                                        # short, steep waves are rougher than their height says
        tiers.append(min(t, 3))
    return LEVELS[max(tiers)] if tiers else None


def compass(deg) -> str:
    names = list(COMPASS)
    return names[int((deg + 11.25) % 360 // 22.5)] if deg is not None else ""


def _fresh(b, now):
    try:
        return b.get("ok") and now - datetime.fromisoformat(b["time_utc"]) <= MAX_AGE
    except (KeyError, TypeError, ValueError):
        return False


def _nearest(buoys, lat, lon, now, key):
    best = None
    for b in buoys:
        if b.get(key) is not None and b.get("lat") is not None and _fresh(b, now):
            d = haversine_km(lat, lon, b["lat"], b["lon"])
            if d <= MAX_KM and (best is None or d < best[0]):
                best = (d, b)
    return best


def from_buoys(buoys: list[dict], lat: float, lon: float, now: datetime):
    """Current boat conditions near a point, from the nearest fresh buoy readings. None if there is nothing usable."""
    w = _nearest(buoys, lat, lon, now, "wind_kn")
    v = _nearest(buoys, lat, lon, now, "wave_height_m")
    if not w and not v:
        return None
    wind = w[1]["wind_kn"] if w else None
    gust = w[1].get("gust_kn") if w else None
    wave = v[1]["wave_height_m"] if v else None
    period = v[1].get("wave_period_s") if v else None
    level = rate(wind, wave, period)
    bits = []
    if w:
        d = compass(w[1].get("wind_dir_deg"))
        bits.append(f"{d + ' ' if d else ''}wind {wind:.0f} kn" + (f", gusts {gust:.0f}" if gust and gust >= wind + 8 else ""))
    if v:
        bits.append(f"waves {wave * M_TO_FT:.0f} ft" + (f" at {period:.0f} s" if period else ""))
    src = []
    if w:
        src.append(f"{w[1].get('name') or w[1]['station']}, {w[0]:.0f} km away")
    if v and (not w or v[1]["station"] != w[1]["station"]):
        src.append(f"waves: {v[1].get('name') or v[1]['station']}, {v[0]:.0f} km away")
    return {"level": level, "label": LABEL[level], "wind_kn": wind, "wave_ft": None if wave is None else round(wave * M_TO_FT, 1),
            "text": f"{LABEL[level]}: " + ", ".join(bits) + f" ({'; '.join(src)})",
            "missing": ([] if v else ["waves"]) + ([] if w else ["wind"])}


def outlook(forecast_obs, now: datetime):
    """Strongest forecast wind in the next 24 hours, or None."""
    nxt = [o for o in (forecast_obs or []) if now <= o["time"] <= now + timedelta(hours=24) and o.get("wspd") is not None]
    if not nxt:
        return None
    top = max(nxt, key=lambda o: o["wspd"])
    kn = top["wspd"] * MS_TO_KN
    level = rate(kn)
    d = compass(top.get("wdir"))
    return {"level": level, "max_wind_kn": round(kn), "at": top["time"].isoformat(),
            "text": f"Forecast: winds up to {kn:.0f} kn{(' from the ' + d) if d else ''} around {_clock(top['time'])} ({LABEL[level].lower()} for most boats)"}


def rows(buoys, lat, lon, conditions) -> list:
    now = conditions["now"]
    s = from_buoys(buoys, lat, lon, now)
    out = [["Boat conditions", s["text"] if s else "No recent buoy wind or wave reading nearby"]]
    o = outlook(conditions.get("forecast"), now)
    if o:
        out.append(["Wind outlook", o["text"]])
    return out


def summary(buoys, conditions) -> dict:
    now = conditions["now"]
    s = from_buoys(buoys, *REGION_POINT, now)
    o = outlook(conditions.get("forecast"), now)
    return {"now": s, "outlook": o}
