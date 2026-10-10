"""Download the satellite and depth grids and put them on one common grid (the SST grid)."""
from __future__ import annotations

import numpy as np

from pipeline import derive
from pipeline.grid import resample
from pipeline.sources import erddap


FRONT_MIN_DEPTH_M = 30.0   # shallow banks and shelves heat up faster; their edges are not ocean fronts


def front_strength(sst, depth, lats, lons, min_depth: float = FRONT_MIN_DEPTH_M):
    """Temperature-break strength that ignores shallow water. Cells next to shallow or missing
    depth are NaN, so bank and shelf edges never count as fronts."""
    if depth is None:
        return derive.gradient_magnitude(sst, lats, lons)
    deep_sst = np.where(np.isfinite(depth) & (depth >= min_depth), sst, np.nan)
    return derive.gradient_magnitude(deep_sst, lats, lons)


def _fetch_grid(cfg: dict, region: dict, fetch):
    url = erddap.build_griddap_url(cfg, region)
    return erddap.parse_grid_csv(fetch(url), cfg["variable"])


def load_layers(sources: dict, errors: list[str], fetch=erddap.fetch_csv):
    """Return a dict of layers on the SST grid, or None if SST itself cannot be loaded.
    Chlorophyll and depth are optional; a missing one is None and the scorer copes."""
    region, cfg = sources["region"], sources["erddap"]
    try:
        lats, lons, sst, sst_time, _ = _fetch_grid(cfg["sst"], region, fetch)
    except Exception as exc:
        errors.append(f"layers sst: {exc}")
        return None

    layers = {"lats": lats, "lons": lons, "sst_c": sst,
              "sst_gradient": derive.gradient_magnitude(sst, lats, lons),
              "chlorophyll": None, "depth_m": None, "chl_raw": None,
              "times": {"sst": sst_time, "chlorophyll": None},
              "datasets": {"sst": cfg["sst"]["dataset"]}}

    c = cfg.get("chlorophyll", {})
    if c.get("enabled"):
        try:
            clats, clons, chl, chl_time, _ = _fetch_grid(c, region, fetch)
            layers["chl_raw"] = (clats, clons, chl)
            layers["chlorophyll"] = resample(chl, clats, clons, lats, lons, min_weight=0.5)
            layers["times"]["chlorophyll"] = chl_time
            layers["datasets"]["chlorophyll"] = c["dataset"]
        except Exception as exc:
            errors.append(f"layers chlorophyll: {exc}")

    b = cfg.get("bathymetry", {})
    if b.get("enabled"):
        try:
            blats, blons, z, _, _ = _fetch_grid(b, region, fetch)
            z_on_grid = resample(z, blats, blons, lats, lons, min_weight=0.5)
            depth = -z_on_grid                      # ETOPO: negative z is below sea level
            depth[~(depth > 0)] = np.nan            # land and zero-depth cells
            layers["depth_m"] = depth
            layers["datasets"]["bathymetry"] = b["dataset"]
        except Exception as exc:
            errors.append(f"layers bathymetry: {exc}")
    layers["sst_gradient"] = front_strength(sst, layers["depth_m"], lats, lons)
    return layers