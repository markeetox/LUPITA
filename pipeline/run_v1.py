"""First data pull: NDBC buoys + satellite SST grid -> data/live/latest.json.
Each source fails independently; failures are recorded under "errors"."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from pipeline import derive
from pipeline.sources import erddap, ndbc

ROOT = Path(__file__).resolve().parent.parent
log = logging.getLogger("run_v1")

# Gradient (degC per km) above which a cell is reported as part of a temperature break.
# Placeholder: calibrate against real SST grids before using it for scoring.
SST_BREAK_MIN = 0.05


def pull_buoys(stations: list[dict], url_template: str, errors: list[str]) -> list[dict]:
    results = []
    for st in stations:
        try:
            rows = ndbc.parse_realtime2(ndbc.fetch_realtime(st["id"], url_template))
            results.append(ndbc.summarize(st, rows))
        except Exception as exc:  # one dead station must not stop the run
            errors.append(f"ndbc {st['id']}: {exc}")
            results.append({"station": st["id"], "ok": False})
    return results


def pull_sst(sources: dict, errors: list[str]):
    cfg = sources["erddap"]["sst"]
    if not cfg.get("enabled"):
        return None
    try:
        url = erddap.build_griddap_url(cfg, sources["region"])
        lats, lons, grid, when, unit = erddap.parse_grid_csv(erddap.fetch_csv(url), cfg["variable"])
        grad = derive.gradient_magnitude(grid, lats, lons)
        return {
            "parameter": cfg["parameter"], "dataset": cfg["dataset"], "time": when, "units": unit,
            "shape": [int(len(lats)), int(len(lons))],
            "sst_min_c": round(float(np.nanmin(grid)), 2),
            "sst_max_c": round(float(np.nanmax(grid)), 2),
            "gradient_max_c_per_km": round(float(np.nanmax(grad)), 4),
            "strongest_gradient_cells": derive.top_cells(grad, lats, lons, n=25, min_value=SST_BREAK_MIN),
        }
    except Exception as exc:
        errors.append(f"erddap sst: {exc}")
        return None


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    stations = json.loads((ROOT / "config/stations.json").read_text())["stations"]
    sources = json.loads((ROOT / "config/sources.json").read_text())
    errors: list[str] = []

    buoys = pull_buoys(stations, sources["ndbc"]["realtime_url"], errors)
    sst = pull_sst(sources, errors)

    out = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "region": sources["region"]["name"],
        "buoys": buoys,
        "sst": sst,
        "errors": errors,
    }
    dest = ROOT / "data/live/latest.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2))
    log.info("wrote %s (%d buoys ok, sst=%s, %d errors)", dest,
             sum(1 for b in buoys if b.get("ok")), "yes" if sst else "no", len(errors))


if __name__ == "__main__":
    main()
