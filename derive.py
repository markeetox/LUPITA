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
