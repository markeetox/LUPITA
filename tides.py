"""NOAA CO-OPS tide predictions (high and low tides) and the tide stage at a given moment."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pipeline import http

API = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
USER_AGENT = "fish-habitat-map/0.1"
SLACK = timedelta(minutes=30)     # within this of a high or low tide counts as slack


def fetch_hilo(station: str, now: datetime, timeout: int = 40) -> dict:
    begin, end = (now - timedelta(days=1)).strftime("%Y%m%d"), (now + timedelta(days=2)).strftime("%Y%m%d")
    return http.get(API, timeout=timeout, attempts=3, base_delay=10, params={
        "product": "predictions", "application": "fish-habitat-map", "begin_date": begin, "end_date": end,
        "datum": "MLLW", "station": station, "time_zone": "gmt", "units": "metric", "interval": "hilo", "format": "json"}).json()


def parse_hilo(payload: dict) -> list[dict]:
    """[{'time': UTC datetime, 'type': 'H'|'L', 'height_m': float}, ...] in time order."""
    if "error" in payload:
        raise RuntimeError(payload["error"].get("message", "CO-OPS error"))
    out = []
    for p in payload.get("predictions", []):
        t = datetime.strptime(p["t"], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        out.append({"time": t, "type": p["type"], "height_m": float(p["v"])})
    return sorted(out, key=lambda e: e["time"])


def stage_at(events: list[dict], now: datetime):
    """'rising', 'falling', 'slack_high' or 'slack_low', or None if the events do not bracket 'now'."""
    prev = [e for e in events if e["time"] <= now]
    nxt = [e for e in events if e["time"] > now]
    if not prev or not nxt:
        return None
    p, n = prev[-1], nxt[0]
    if now - p["time"] <= SLACK:
        return "slack_high" if p["type"] == "H" else "slack_low"
    if n["time"] - now <= SLACK:
        return "slack_high" if n["type"] == "H" else "slack_low"
    return "rising" if p["type"] == "L" else "falling"


def next_events(events: list[dict], now: datetime, count: int = 4) -> list[dict]:
    return [e for e in events if e["time"] > now][:count]
