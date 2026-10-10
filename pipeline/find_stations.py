"""List active NDBC stations near South Florida and show which ones report usable data.
Run:  python -m pipeline.find_stations          (only stations with data)
      python -m pipeline.find_stations --all    (include stations with no data file)"""
from __future__ import annotations

import math
import re
import sys
import xml.etree.ElementTree as ET

import requests

from pipeline.sources import ndbc

ACTIVE_URL = "https://www.ndbc.noaa.gov/activestations.xml"
BOX = {"lat": (24.3, 27.8), "lon": (-82.2, -79.3)}
CENTER = (25.75, -80.1)  # Miami


def clean_name(name: str) -> str:
    """Drop NOAA's leading tide-station number, e.g. '8723214 - Virginia Key, FL'."""
    return re.sub(r"^\d{7}\s*-\s*", "", name or "").strip()


def parse_active(xml_text: str) -> list[dict]:
    out = []
    for el in ET.fromstring(xml_text).iter("station"):
        try:
            out.append({"id": el.get("id").upper(), "name": clean_name(el.get("name", "")),
                        "type": el.get("type", ""), "met": el.get("met", ""),
                        "lat": float(el.get("lat")), "lon": float(el.get("lon"))})
        except (AttributeError, TypeError, ValueError):
            continue
    return out


def in_box(s: dict) -> bool:
    return BOX["lat"][0] <= s["lat"] <= BOX["lat"][1] and BOX["lon"][0] <= s["lon"] <= BOX["lon"][1]


def dist_km(s: dict) -> float:
    dlat = (s["lat"] - CENTER[0]) * 111.32
    dlon = (s["lon"] - CENTER[1]) * 111.32 * math.cos(math.radians(CENTER[0]))
    return math.hypot(dlat, dlon)


def main() -> None:
    show_all = "--all" in sys.argv
    resp = requests.get(ACTIVE_URL, timeout=60, headers={"User-Agent": ndbc.USER_AGENT})
    resp.raise_for_status()
    near = sorted((s for s in parse_active(resp.text) if in_box(s) and s["met"] == "y"), key=dist_km)
    print(f"{len(near)} active stations with met data in the box. Testing each...\n")
    print(f"{'ID':7} {'km':>4}  {'lat':>7} {'lon':>8}  {'water C':>7} {'wind kn':>7} {'waves m':>7} {'press':>7}  name")
    shown = 0
    for s in near:
        try:
            rows = ndbc.parse_realtime2(ndbc.fetch_realtime(
                s["id"], "https://www.ndbc.noaa.gov/data/realtime2/{station}.txt", timeout=20))
            m = ndbc.summarize(s, rows)
            vals = [m.get(k) for k in ("water_temp_c", "wind_kn", "wave_height_m", "pressure_hpa")]
        except Exception:
            vals = ["no file"] + [None] * 3
        has_data = any(isinstance(v, (int, float)) for v in vals)
        if not has_data and not show_all:
            continue
        shown += 1
        fmt = lambda v: "-" if v is None else str(v)
        print(f"{s['id']:7} {dist_km(s):4.0f}  {s['lat']:7.2f} {s['lon']:8.2f}  "
              f"{fmt(vals[0]):>7} {fmt(vals[1]):>7} {fmt(vals[2]):>7} {fmt(vals[3]):>7}  {s['name']}")
    print(f"\n{shown} stations returned data.")


if __name__ == "__main__":
    main()
