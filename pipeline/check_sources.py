"""Verify that stations and ERDDAP datasets exist and look the way the config expects.
Run this first on a machine with internet access:  python -m pipeline.check_sources"""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path

import requests

from pipeline.sources import ndbc

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    stations = json.loads((ROOT / "config/stations.json").read_text())["stations"]
    sources = json.loads((ROOT / "config/sources.json").read_text())

    print("== NDBC stations ==")
    for st in stations:
        try:
            rows = ndbc.parse_realtime2(ndbc.fetch_realtime(st["id"], sources["ndbc"]["realtime_url"]))
            s = ndbc.summarize(st, rows)
            print(f"  {st['id']:6} rows={len(rows):4} water_temp={s.get('water_temp_c')} "
                  f"wind_kn={s.get('wind_kn')} waves_m={s.get('wave_height_m')} pressure={s.get('pressure_hpa')}")
        except Exception as exc:
            print(f"  {st['id']:6} FAILED: {exc}")

    print("\n== ERDDAP datasets ==")
    for name, cfg in sources["erddap"].items():
        url = f"{cfg['base']}/info/{cfg['dataset']}/index.csv"
        try:
            resp = requests.get(url, timeout=60, headers={"User-Agent": ndbc.USER_AGENT})
            resp.raise_for_status()
            rows = list(csv.DictReader(io.StringIO(resp.text)))
            dims = [r["Variable Name"] for r in rows if r["Row Type"] == "dimension"]
            variables = [r["Variable Name"] for r in rows if r["Row Type"] == "variable"]
            units = {r["Variable Name"]: r["Value"] for r in rows
                     if r["Row Type"] == "attribute" and r["Attribute Name"] == "units"}
            print(f"  {name} ({cfg['dataset']})")
            print(f"    dimensions in config : {cfg['dims']}")
            print(f"    dimensions on server : {dims}   {'OK' if dims == cfg['dims'] else '<-- MISMATCH, fix config'}")
            print(f"    variable {cfg['variable']!r}: {'found' if cfg['variable'] in variables else 'NOT FOUND'}"
                  f" (units: {units.get(cfg['variable'])})")
        except Exception as exc:
            print(f"  {name} ({cfg['dataset']}) FAILED: {exc}")


if __name__ == "__main__":
    main()
