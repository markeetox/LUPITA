"""Moon phase from true new and full moon times (Meeus, 'Astronomical Algorithms', ch. 49; main terms only,
good to roughly 15 minutes)."""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

UTC = timezone.utc
JD_UNIX = 2440587.5
MONTH = 29.530588861


def _jd_to_dt(jd: float) -> datetime:
    return datetime(1970, 1, 1, tzinfo=UTC) + timedelta(days=jd - JD_UNIX)


def _dt_to_jd(t: datetime) -> float:
    return JD_UNIX + (t - datetime(1970, 1, 1, tzinfo=UTC)).total_seconds() / 86400.0


def phase_time(k: float) -> datetime:
    """UTC time of the new moon (k whole) or full moon (k + 0.5)."""
    T = k / 1236.85
    jde = 2451550.09766 + MONTH * k + 0.00015437 * T ** 2 - 0.00000015 * T ** 3 + 0.00000000073 * T ** 4
    E = 1 - 0.002516 * T - 0.0000074 * T ** 2
    r = math.radians
    M = r(2.5534 + 29.10535670 * k - 0.0000014 * T ** 2)
    Mp = r(201.5643 + 385.81693528 * k + 0.0107582 * T ** 2 + 0.00001238 * T ** 3)
    F = r(160.7108 + 390.67050284 * k - 0.0016118 * T ** 2)
    if abs(k - round(k)) < 0.25:   # new moon
        c = (-0.40720 * math.sin(Mp) + 0.17241 * E * math.sin(M) + 0.01608 * math.sin(2 * Mp) + 0.01039 * math.sin(2 * F)
             + 0.00739 * E * math.sin(Mp - M) - 0.00514 * E * math.sin(Mp + M) + 0.00208 * E * E * math.sin(2 * M))
    else:                           # full moon
        c = (-0.40614 * math.sin(Mp) + 0.17302 * E * math.sin(M) + 0.01614 * math.sin(2 * Mp) + 0.01043 * math.sin(2 * F)
             + 0.00734 * E * math.sin(Mp - M) - 0.00515 * E * math.sin(Mp + M) + 0.00209 * E * E * math.sin(2 * M))
    return _jd_to_dt(jde + c)


def _k_near(t: datetime) -> int:
    return round((_dt_to_jd(t) - 2451550.09766) / MONTH)


def nearest(t: datetime, kind: str) -> datetime:
    """The new ('new') or full ('full') moon closest to t."""
    k0 = _k_near(t) + (0.5 if kind == "full" else 0.0)
    return min((phase_time(k0 + d) for d in (-1, 0, 1)), key=lambda x: abs((x - t).total_seconds()))


def days_from_full(t: datetime) -> float:
    """Signed days from the nearest full moon (negative = full moon still ahead)."""
    return (t - nearest(t, "full")).total_seconds() / 86400.0


def _bracket(t: datetime):
    k = math.floor((_dt_to_jd(t) - 2451550.09766) / MONTH)
    for kk in (k - 1, k, k + 1):
        a, b = phase_time(kk), phase_time(kk + 1)
        if a <= t < b:
            return a, b
    return phase_time(k), phase_time(k + 1)


def illumination(t: datetime) -> float:
    a, b = _bracket(t)
    f = (t - a).total_seconds() / (b - a).total_seconds()
    return (1 - math.cos(2 * math.pi * f)) / 2


def phase_name(t: datetime) -> str:
    a, b = _bracket(t)
    f = (t - a).total_seconds() / (b - a).total_seconds()
    if f < 0.03 or f >= 0.97:
        return "new moon"
    for limit, name in ((0.22, "waxing crescent"), (0.28, "first quarter"), (0.47, "waxing gibbous"), (0.53, "full moon"),
                        (0.72, "waning gibbous"), (0.78, "last quarter")):
        if f < limit:
            return name
    return "waning crescent"


def describe(t: datetime) -> str:
    d = days_from_full(t)
    near = "full moon today" if abs(d) < 0.5 else (f"full moon in {round(-d)} day{'s' if round(-d) != 1 else ''}" if d < 0 else f"full moon was {round(d)} day{'s' if round(d) != 1 else ''} ago")
    return f"{illumination(t):.0%} lit, {phase_name(t)}; {near}"
