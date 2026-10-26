"""Grid helpers: resampling onto a common grid, connected areas, polygons."""
from __future__ import annotations

import math
from collections import deque

import numpy as np


def _weights(src: np.ndarray, dst: np.ndarray) -> np.ndarray:
    """Linear-interpolation weight matrix (len(dst) x len(src)); rows outside src are all zero."""
    src = np.asarray(src, float)
    dst = np.asarray(dst, float)
    w = np.zeros((len(dst), len(src)))
    if len(src) < 2:
        return w
    step = float(np.median(np.abs(np.diff(src))))
    for k, x in enumerate(dst):
        # allow a small overshoot at the edges (within 0.6 of a source cell)
        if x < src[0] - 0.6 * step or x > src[-1] + 0.6 * step:
            continue
        x = min(max(x, src[0]), src[-1])
        i = int(np.clip(np.searchsorted(src, x) - 1, 0, len(src) - 2))
        t = (x - src[i]) / (src[i + 1] - src[i])
        w[k, i], w[k, i + 1] = 1 - t, t
    return w


def resample(grid, src_lats, src_lons, dst_lats, dst_lons, min_weight: float = 0.5) -> np.ndarray:
    """Bilinear resample that ignores NaN cells. A target cell is NaN if too little valid data
    contributes (min_weight) or if it lies outside the source grid."""
    grid = np.asarray(grid, float)
    mask = np.isfinite(grid).astype(float)
    vals = np.where(mask > 0, grid, 0.0)
    wy, wx = _weights(src_lats, dst_lats), _weights(src_lons, dst_lons)
    num = wy @ vals @ wx.T
    den = wy @ mask @ wx.T
    cover = wy.sum(axis=1)[:, None] * wx.sum(axis=1)[None, :]
    out = np.full(num.shape, np.nan)
    ok = (cover > 0.999) & (den >= min_weight)
    out[ok] = num[ok] / den[ok]
    return out


def components(mask: np.ndarray) -> list[list[tuple[int, int]]]:
    """4-connected groups of True cells."""
    seen = np.zeros(mask.shape, bool)
    groups = []
    for i0, j0 in zip(*np.nonzero(mask)):
        if seen[i0, j0]:
            continue
        queue, group = deque([(i0, j0)]), []
        seen[i0, j0] = True
        while queue:
            i, j = queue.popleft()
            group.append((int(i), int(j)))
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                a, b = i + di, j + dj
                if 0 <= a < mask.shape[0] and 0 <= b < mask.shape[1] and mask[a, b] and not seen[a, b]:
                    seen[a, b] = True
                    queue.append((a, b))
        groups.append(group)
    return groups


def convex_hull(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def cell_km2(lat: float, dlat_deg: float, dlon_deg: float) -> float:
    return dlat_deg * 111.32 * dlon_deg * 111.32 * math.cos(math.radians(lat))


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(a))


COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


def bearing_deg(lat1, lon1, lat2, lon2) -> float:
    """Initial compass bearing from point 1 to point 2, 0-360 degrees."""
    p1, p2, dl = math.radians(lat1), math.radians(lat2), math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def compass(deg: float) -> str:
    return COMPASS[int((deg + 11.25) % 360 // 22.5)]
