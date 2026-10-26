"""Derived parameters computed from grids (sst_gradient, later chl_gradient)."""
from __future__ import annotations

import numpy as np

KM_PER_DEG = 111.32


def gradient_magnitude(grid: np.ndarray, lats: np.ndarray, lons: np.ndarray) -> np.ndarray:
    """Horizontal gradient magnitude of a lat/lon grid, in grid-value units per km.
    Cells next to missing data are NaN."""
    if grid.shape != (len(lats), len(lons)):
        raise ValueError("grid shape does not match lats/lons")
    dlat_km = np.gradient(lats) * KM_PER_DEG
    dlon_km = np.gradient(lons)[None, :] * KM_PER_DEG * np.cos(np.radians(lats))[:, None]
    d_dy = np.gradient(grid, axis=0) / dlat_km[:, None]
    d_dx = np.gradient(grid, axis=1) / dlon_km
    return np.hypot(d_dx, d_dy)


def distance_to_inlet_grid(lats: np.ndarray, lons: np.ndarray, inlets: list[dict]) -> np.ndarray:
    """Distance (in km) from each cell center on the (lats, lons) grid to the nearest inlet location.
    Inlets is a list of dicts with 'lat' and 'lon' keys."""
    if not inlets:
        return np.full((len(lats), len(lons)), np.nan)
    grid_lats, grid_lons = np.meshgrid(lats, lons, indexing="ij")
    min_dist = np.full(grid_lats.shape, np.inf)
    for inlet in inlets:
        inlet_lat = float(inlet["lat"])
        inlet_lon = float(inlet["lon"])
        dlat_km = (grid_lats - inlet_lat) * KM_PER_DEG
        avg_lat = np.radians((grid_lats + inlet_lat) / 2.0)
        dlon_km = (grid_lons - inlet_lon) * KM_PER_DEG * np.cos(avg_lat)
        dist = np.hypot(dlat_km, dlon_km)
        min_dist = np.minimum(min_dist, dist)
    return min_dist


def chlorophyll_gradient(chl_grid: np.ndarray, lats: np.ndarray, lons: np.ndarray) -> np.ndarray:
    """Gradient magnitude of chlorophyll concentration (mg/m3 per km)."""
    return gradient_magnitude(chl_grid, lats, lons)


def temperature_trend(current_sst: np.ndarray, previous_sst: np.ndarray, hours_diff: float = 24.0) -> np.ndarray:
    """Water temperature change rate in degC per day (24h).
    Positive values mean warming; negative values mean cooling."""
    if current_sst.shape != previous_sst.shape:
        raise ValueError("current_sst and previous_sst shapes must match")
    if hours_diff <= 0:
        return np.full(current_sst.shape, np.nan)
    return (current_sst - previous_sst) * (24.0 / hours_diff)


def top_cells(values: np.ndarray, lats: np.ndarray, lons: np.ndarray,
              n: int = 25, min_value: float = 0.0) -> list[dict]:
    """The n strongest cells at or above min_value, strongest first."""
    flat = np.where(np.isfinite(values), values, -np.inf).ravel()
    order = np.argsort(flat)[::-1][:n]
    out = []
    for k in order:
        v = flat[k]
        if not np.isfinite(v) or v < min_value:
            break
        i, j = np.unravel_index(k, values.shape)
        out.append({"lat": round(float(lats[i]), 4), "lon": round(float(lons[j]), 4),
                    "value": round(float(v), 4)})
    return out
