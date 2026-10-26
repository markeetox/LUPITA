"""Surface currents and the Gulf Stream's inshore edge, from satellite altimetry (geostrophic currents, 25 km grid).
The edge is approximate: good to roughly 20 km, and weaker close to shore where altimetry is unreliable."""
from __future__ import annotations

import math

import numpy as np

MS_TO_KN = 1.943844
KM_PER_DEG = 111.32
EDGE_FRACTION = 0.5          # the edge is where northward flow reaches this share of the row's strongest flow ...
MIN_STREAM_MS = 0.4          # ... and at least this fast (about 0.8 kn), so rows with no real stream give no edge


def speed_dir(u: np.ndarray, v: np.ndarray):
    """Speed in knots and the compass direction the water is moving TOWARD (0 = north, 90 = east)."""
    return np.hypot(u, v) * MS_TO_KN, np.degrees(np.arctan2(u, v)) % 360


def edge_longitudes(lats, lons, v) -> np.ndarray:
    """For each latitude row, the westernmost longitude where northward flow v (m/s) is strong enough: the stream's inshore edge."""
    edge = np.full(len(lats), np.nan)
    for i in range(len(lats)):
        row = np.nan_to_num(np.asarray(v[i], float), nan=-9.0)
        mx = row.max() if row.size else -9.0
        if mx < MIN_STREAM_MS:
            continue
        thr = max(MIN_STREAM_MS, EDGE_FRACTION * mx)
        j = int(np.argmax(row >= thr))                     # first (westernmost) cell at or above the threshold
        if j == 0 or row[j - 1] < -8:                      # edge is at or beyond the west side of the data (or land)
            edge[i] = lons[j]
        else:
            frac = (thr - row[j - 1]) / (row[j] - row[j - 1])
            edge[i] = lons[j - 1] + frac * (lons[j] - lons[j - 1])
    return edge


def smooth(edge: np.ndarray) -> np.ndarray:
    """Three-row moving average that ignores missing rows."""
    out = np.full(edge.shape, np.nan)
    for i in range(len(edge)):
        w = edge[max(0, i - 1): i + 2]
        w = w[np.isfinite(w)]
        if w.size and np.isfinite(edge[i]):
            out[i] = w.mean()
    return out


def edge_on_grid(src_lats, edge, dst_lats):
    """Edge longitude at the map's latitudes (NaN outside the rows that had a stream). None if too little to use."""
    ok = np.isfinite(edge)
    if ok.sum() < 3:
        return None
    out = np.interp(dst_lats, np.asarray(src_lats)[ok], edge[ok], left=np.nan, right=np.nan)
    return out if np.isfinite(out).any() else None


def signed_km(edge_lon: np.ndarray, lats, lons) -> np.ndarray:
    """Distance east-west from the edge in km, positive east of it (inside the stream), negative inshore of it."""
    return (np.asarray(lons)[None, :] - edge_lon[:, None]) * KM_PER_DEG * np.cos(np.radians(np.asarray(lats)))[:, None]


def stream_geojson(edge_lon, lats, source, time, loaded: bool, generated_utc: str, every: int = 4) -> dict:
    """The inshore edge as a line for the map (every few rows is plenty for a 25 km source)."""
    pts = []
    if edge_lon is not None:
        pts = [[round(float(edge_lon[i]), 3), round(float(lats[i]), 3)] for i in range(0, len(lats), every) if np.isfinite(edge_lon[i])]
    feats = [{"type": "Feature", "properties": {"name": "Gulf Stream inshore edge (approximate)", "source": source, "time": time},
              "geometry": {"type": "LineString", "coordinates": pts}}] if len(pts) >= 2 else []
    return {"type": "FeatureCollection", "loaded": loaded, "generated_utc": generated_utc, "features": feats}
