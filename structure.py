"""Reef and wreck structure on the common grid, from FWC artificial reefs and FWRI coral/hard bottom."""
from __future__ import annotations

import numpy as np

SUB = 10  # sub-samples per cell side when rasterizing polygons (about 200 m)


def _inside(px: np.ndarray, py: np.ndarray, rings: list) -> np.ndarray:
    """Even-odd point-in-polygon over all rings (outer rings and holes)."""
    inside = np.zeros(px.shape, bool)
    for ring in rings:
        n = len(ring)
        for k in range(n):
            x1, y1 = ring[k]
            x2, y2 = ring[(k + 1) % n]
            if y1 == y2:
                continue
            cond = ((y1 > py) != (y2 > py)) & (px < (x2 - x1) * (py - y1) / (y2 - y1) + x1)
            inside ^= cond
    return inside


def rasterize_cover(features: list[dict], lats: np.ndarray, lons: np.ndarray, sub: int = SUB) -> np.ndarray:
    """Fraction (0-1) of each grid cell covered by the polygons."""
    ny, nx = len(lats), len(lons)
    dlat, dlon = float(lats[1] - lats[0]), float(lons[1] - lons[0])
    f_lats = lats[0] - dlat / 2 + (np.arange(ny * sub) + 0.5) * dlat / sub
    f_lons = lons[0] - dlon / 2 + (np.arange(nx * sub) + 0.5) * dlon / sub
    hit = np.zeros((ny * sub, nx * sub), bool)
    for feat in features:
        rings = (feat.get("geometry") or {}).get("rings")
        if not rings:
            continue
        xs = [p[0] for r in rings for p in r]
        ys = [p[1] for r in rings for p in r]
        i0, i1 = np.searchsorted(f_lats, min(ys)), np.searchsorted(f_lats, max(ys), side="right")
        j0, j1 = np.searchsorted(f_lons, min(xs)), np.searchsorted(f_lons, max(xs), side="right")
        if i1 <= i0 or j1 <= j0:
            continue                      # smaller than the sample spacing
        py, px = np.meshgrid(f_lats[i0:i1], f_lons[j0:j1], indexing="ij")
        hit[i0:i1, j0:j1] |= _inside(px, py, rings)
    return hit.reshape(ny, sub, nx, sub).mean(axis=(1, 3))


def artificial_cells(features: list[dict], lats: np.ndarray, lons: np.ndarray) -> dict:
    """Map FWC artificial reef records to grid cells: {(i, j): [structure, ...]}."""
    dlat, dlon = float(lats[1] - lats[0]), float(lons[1] - lons[0])
    out: dict = {}
    for f in features:
        a = f.get("attributes") or {}
        lat, lon = a.get("Lat_DD"), a.get("Long_DD")
        if lat is None or lon is None:
            g = f.get("geometry") or {}
            lat, lon = g.get("y"), g.get("x")
        if lat is None or lon is None:
            continue
        i, j = int(round((lat - lats[0]) / dlat)), int(round((lon - lons[0]) / dlon))
        if not (0 <= i < len(lats) and 0 <= j < len(lons)):
            continue
        kind = "wreck" if str(a.get("MatCat") or "").strip().lower() == "vessel" else "artificial_reef"
        out.setdefault((i, j), []).append({
            "name": a.get("Name") or a.get("Description") or "Artificial reef", "kind": kind,
            "material": a.get("MatDescrip"), "depth_ft": a.get("Depth"), "relief_ft": a.get("Relief"),
            "deployed": a.get("DeployDate")})
    return out


def build_structure_layer(art_features, nat_features, lats, lons, min_cover: float = 0.01):
    """Returns (types, info, cover). types is an object grid of 'wreck', 'artificial_reef',
    'natural_reef' or 'none_mapped'. 'none_mapped' only means no mapped structure."""
    cover = rasterize_cover(nat_features, lats, lons)
    info = artificial_cells(art_features, lats, lons)
    types = np.full(cover.shape, "none_mapped", dtype=object)
    types[cover >= min_cover] = "natural_reef"
    for (i, j), items in info.items():
        types[i, j] = "wreck" if any(x["kind"] == "wreck" for x in items) else "artificial_reef"
    return types, info, cover
