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


import math


def flow_velocity_at(events: list[dict], now: datetime) -> dict:
    """Returns continuous flow velocity (0.0 to 1.0), direction ('incoming', 'outgoing'), and stage."""
    prev = [e for e in events if e["time"] <= now]
    nxt = [e for e in events if e["time"] > now]
    if not prev or not nxt:
        return {"flow": 0.5, "stage": "moving", "direction": "unknown"}
    p, n = prev[-1], nxt[0]
    dt_total = (n["time"] - p["time"]).total_seconds()
    if dt_total <= 0:
        return {"flow": 0.5, "stage": "moving", "direction": "unknown"}
    fraction = (now - p["time"]).total_seconds() / dt_total
    # Sinusoidal flow profile: 0 at peaks/troughs, 1.0 at mid-tide
    flow = math.sin(math.pi * fraction)
    range_m = abs(n["height_m"] - p["height_m"])
    amp_factor = min(1.0, max(0.2, range_m / 1.5)) if range_m > 0 else 1.0
    flow_strength = flow * amp_factor
    is_slack = flow < 0.25
    direction = "incoming" if p["type"] == "L" else "outgoing"
    stage = ("slack_high" if p["type"] == "H" else "slack_low") if is_slack else direction
    return {"flow": round(flow_strength, 3), "direction": direction, "stage": stage}


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
