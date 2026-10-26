"""NOAA NDBC buoy / C-MAN station readings (parameters: sst_c, wind_speed, wave_height, pressure)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pipeline import http

MS_TO_KN = 1.943844
USER_AGENT = "fish-habitat-map/0.1"


def fetch_realtime(station: str, url_template: str, timeout: int = 30) -> str:
    return http.get(url_template.format(station=station), timeout=timeout, attempts=2, base_delay=5).text


def parse_realtime2(text: str) -> list[dict]:
    """Parse an NDBC realtime2 file. Rows are returned newest first.
    Missing values ("MM") become None. Times are UTC."""
    header = None
    rows: list[dict] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            if header is None and "YY" in line:
                header = line.lstrip("#").split()
            continue
        if header is None:
            continue
        parts = line.split()
        if len(parts) != len(header):
            continue
        rec = {k: (None if v == "MM" else float(v)) for k, v in zip(header, parts)}
        year = int(rec["YY"])
        if year < 100:
            year += 2000
        rec["time"] = datetime(year, int(rec["MM"]), int(rec["DD"]),
                               int(rec["hh"]), int(rec["mm"]), tzinfo=timezone.utc)
        rows.append(rec)
    return rows


def _latest(rows: list[dict], key: str, max_age: timedelta = timedelta(hours=3)):
    if not rows:
        return None, None
    newest = rows[0]["time"]
    for r in rows:
        if newest - r["time"] > max_age:
            break
        if r.get(key) is not None:
            return r[key], r["time"]
    return None, None


def _value_near(rows: list[dict], key: str, target: datetime, tolerance: timedelta):
    best, best_gap = None, None
    for r in rows:
        if r.get(key) is None:
            continue
        gap = abs(r["time"] - target)
        if gap <= tolerance and (best_gap is None or gap < best_gap):
            best, best_gap = r[key], gap
    return best


def summarize(station: dict, rows: list[dict]) -> dict:
    """Latest readings plus 3 h pressure change and 24 h water-temperature change."""
    out = {"station": station["id"], "name": station.get("name"),
           "lat": station.get("lat"), "lon": station.get("lon"), "ok": bool(rows)}
    if not rows:
        return out
    out["time_utc"] = rows[0]["time"].isoformat()

    wtmp, t_w = _latest(rows, "WTMP")
    out["water_temp_c"] = wtmp
    out["air_temp_c"], _ = _latest(rows, "ATMP")
    wspd, _ = _latest(rows, "WSPD")
    gst, _ = _latest(rows, "GST")
    out["wind_kn"] = None if wspd is None else round(wspd * MS_TO_KN, 1)
    out["gust_kn"] = None if gst is None else round(gst * MS_TO_KN, 1)
    out["wind_dir_deg"], _ = _latest(rows, "WDIR")
    out["wave_height_m"], _ = _latest(rows, "WVHT")
    out["wave_period_s"], _ = _latest(rows, "DPD")
    pres, t_p = _latest(rows, "PRES")
    out["pressure_hpa"] = pres

    out["pressure_change_3h_hpa"] = None
    if pres is not None:
        old = _value_near(rows, "PRES", t_p - timedelta(hours=3), timedelta(minutes=40))
        if old is not None:
            out["pressure_change_3h_hpa"] = round(pres - old, 2)

    out["water_temp_change_24h_c"] = None
    if wtmp is not None:
        old = _value_near(rows, "WTMP", t_w - timedelta(hours=24), timedelta(hours=1))
        if old is not None:
            out["water_temp_change_24h_c"] = round(wtmp - old, 2)
    return out
