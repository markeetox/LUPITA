"""Sunrise, sunset and light phase (NOAA solar calculation; accurate to a few minutes)."""
from __future__ import annotations

import math
from datetime import date, datetime, timedelta, timezone

ZENITH = 90.833   # standard sunrise/sunset: sun's upper edge at the horizon, with refraction


def sun_times(day: date, lat: float, lon: float):
    """(sunrise, sunset) as UTC datetimes for the given date, or (None, None) in polar day or night.
    lon is degrees east (negative for the western hemisphere)."""
    n = day.timetuple().tm_yday
    g = 2 * math.pi / 365 * (n - 1 + 0.5)
    eqtime = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g)
                       - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))
    decl = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g)
            + 0.000907 * math.sin(2 * g) - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
    la = math.radians(lat)
    c = math.cos(math.radians(ZENITH)) / (math.cos(la) * math.cos(decl)) - math.tan(la) * math.tan(decl)
    if not -1 <= c <= 1:
        return None, None
    ha = math.degrees(math.acos(c))
    midnight = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    return (midnight + timedelta(minutes=720 - 4 * (lon + ha) - eqtime),
            midnight + timedelta(minutes=720 - 4 * (lon - ha) - eqtime))


def light_phase(now: datetime, lat: float, lon: float) -> str:
    """'dawn' (45 min either side of sunrise), 'dusk' (60 min before to 45 after sunset), 'day' or 'night'."""
    for d in (now.date() - timedelta(days=1), now.date(), now.date() + timedelta(days=1)):
        sr, ss = sun_times(d, lat, lon)
        if sr is None:
            continue
        if sr - timedelta(minutes=45) <= now <= sr + timedelta(minutes=45):
            return "dawn"
        if ss - timedelta(minutes=60) <= now <= ss + timedelta(minutes=45):
            return "dusk"
        if sr + timedelta(minutes=45) < now < ss - timedelta(minutes=60):
            return "day"
    return "night"
