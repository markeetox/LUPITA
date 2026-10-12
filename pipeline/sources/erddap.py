"""NOAA ERDDAP griddap access (parameters: sst_c, chlorophyll)."""
from __future__ import annotations

import csv
import io

import numpy as np

from pipeline import http

USER_AGENT = "fish-habitat-map/0.1"


def build_griddap_url(cfg: dict, region: dict) -> str:
    """Build a CSV griddap request for the latest time step inside the region.
    ERDDAP slice syntax: [(start):stride:(stop)] with stride counted in grid steps."""
    slices = []
    for dim in cfg["dims"]:
        if dim == "time":
            slices.append("[(last)]")
        elif dim == "altitude":
            slices.append("[(0.0)]")
        elif dim in ("latitude", "longitude"):
            lo, hi = region["lat"] if dim == "latitude" else region["lon"]
            stride = cfg.get("stride", {}).get(dim, 1)
            slices.append(f"[({lo}):{stride}:({hi})]")
        else:
            raise ValueError(f"Unknown dimension {dim!r}")
    return f"{cfg['base']}/griddap/{cfg['dataset']}.csv?{cfg['variable']}{''.join(slices)}"


def fetch_csv(url: str, timeout: int = 120) -> str:
    return http.get(url, timeout=timeout).text


def parse_grid_csv(text: str, variable: str):
    """Turn an ERDDAP CSV (header row + units row + data) into (lats, lons, grid, time, units).
    Missing cells are NaN. Kelvin values are converted to Celsius."""
    reader = csv.reader(io.StringIO(text))
    header = next(reader)
    units = next(reader)
    idx = {name: i for i, name in enumerate(header)}
    for needed in ("latitude", "longitude", variable):
        if needed not in idx:
            raise ValueError(f"Column {needed!r} missing; got {header}")
    unit = units[idx[variable]]
    points, times = [], set()
    for row in reader:
        if not row:
            continue
        try:
            v = float(row[idx[variable]])
        except ValueError:
            v = float("nan")
        points.append((float(row[idx["latitude"]]), float(row[idx["longitude"]]), v))
        if "time" in idx:
            times.add(row[idx["time"]])
    if not points:
        raise ValueError("No data rows returned")
    lats = np.array(sorted({p[0] for p in points}))
    lons = np.array(sorted({p[1] for p in points}))
    grid = np.full((len(lats), len(lons)), np.nan)
    lat_i = {v: i for i, v in enumerate(lats)}
    lon_i = {v: i for i, v in enumerate(lons)}
    for la, lo, v in points:
        grid[lat_i[la], lon_i[lo]] = v
    if unit.strip().lower() in ("k", "kelvin", "degree_k"):
        grid = grid - 273.15
        unit = "degree_C"
    return lats, lons, grid, (sorted(times)[-1] if times else None), unit
