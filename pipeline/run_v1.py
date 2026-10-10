"""First data pull: NDBC buoys + satellite SST and chlorophyll grids -> data/live/latest.json.
Each source fails independently; failures are recorded under "errors"."""
from __future__ import annotations

import json
import logging
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from pipeline import derive
from pipeline.sources import erddap, ndbc

ROOT = Path(__file__).resolve().parent.parent
log = logging.getLogger("run_v1")


def _num(x, digits: int = 3):
    """Round to a plain number, or None if it is NaN/inf (NaN is not valid JSON)."""
    x = float(x)
    return round(x, digits) if math.isfinite(x) else None


def summarize_grid(grid: np.ndarray, lats: np.ndarray, lons: np.ndarray,
                   log_scale: bool = False, gradient_min: float = 0.0, top_n: int = 25) -> dict:
    """Min/max, share of valid cells, and the strongest gradient cells of a lat/lon grid."""
    valid = np.isfinite(grid)
    out = {"valid_fraction": _num(valid.mean()), "value_min": None, "value_max": None,
           "gradient_max": None, "strongest_gradient_cells": []}
    if not valid.any():
        return out
    out["value_min"] = _num(np.nanmin(grid))
    out["value_max"] = _num(np.nanmax(grid))
    work = np.log10(np.where(grid > 0, grid, np.nan)) if log_scale else grid
    grad = derive.gradient_magnitude(work, lats, lons)
    if np.isfinite(grad).any():
        out["gradient_max"] = _num(np.nanmax(grad), 4)
        out["strongest_gradient_cells"] = derive.top_cells(grad, lats, lons, n=top_n, min_value=gradient_min)
    return out


def pull_buoys(stations: list[dict], url_template: str, errors: list[str]) -> list[dict]:
    results = []
    for st in stations:
        try:
            rows = ndbc.parse_realtime2(ndbc.fetch_realtime(st["id"], url_template))
            summary = ndbc.summarize(st, rows)
            summary["zone"] = st.get("zone")
            results.append(summary)
        except Exception as exc:  # one dead station must not stop the run
            errors.append(f"ndbc {st['id']}: {exc}")
            results.append({"station": st["id"], "ok": False})
    return results


def pull_grid(sources: dict, key: str, errors: list[str]):
    cfg = sources["erddap"][key]
    if not cfg.get("enabled"):
        return None
    try:
        url = erddap.build_griddap_url(cfg, sources["region"])
        lats, lons, grid, when, unit = erddap.parse_grid_csv(erddap.fetch_csv(url), cfg["variable"])
        out = {"parameter": cfg["parameter"], "dataset": cfg["dataset"], "time": when, "units": unit,
               "gradient_unit": cfg.get("gradient_unit"), "shape": [int(len(lats)), int(len(lons))]}
        out.update(summarize_grid(grid, lats, lons, cfg.get("log_scale", False), cfg.get("gradient_min", 0.0)))
        return out
    except Exception as exc:
        errors.append(f"erddap {key}: {exc}")
        return None


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    stations = json.loads((ROOT / "config/stations.json").read_text())["stations"]
    sources = json.loads((ROOT / "config/sources.json").read_text())
    errors: list[str] = []

    buoys = pull_buoys(stations, sources["ndbc"]["realtime_url"], errors)
    sst = pull_grid(sources, "sst", errors)
    chl = pull_grid(sources, "chlorophyll", errors)

    out = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "region": sources["region"]["name"],
        "buoys": buoys,
        "sst": sst,
        "chlorophyll": chl,
        "errors": errors,
    }
    dest = ROOT / "data/live/latest.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2, allow_nan=False))
    log.info("wrote %s (%d buoys ok, sst=%s, chlorophyll=%s, %d errors)", dest,
             sum(1 for b in buoys if b.get("ok")), "yes" if sst else "no", "yes" if chl else "no", len(errors))


if __name__ == "__main__":
    main()
