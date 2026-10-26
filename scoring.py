"""Score every map cell for a species from its profile, and turn the best cells into areas."""
from __future__ import annotations

import numpy as np

from pipeline.grid import cell_km2, components, convex_hull

OFFSHORE_MIN_DEPTH_M = 50.0   # cells at least this deep define "offshore" for relative scales
MIN_SCORE_REPORT = 0.55       # never report areas scoring below this
TOP_FRACTION = 0.15           # report the best 15% of eligible cells
MIN_CELLS = 6                 # smallest area worth showing (about 25 km2)
MAX_SPOTS = 5
DEFAULT_MIN_COVERAGE = 0.7    # share of the profile's weight that must have data

FRIENDLY = {
    "structure_type": "reef and wreck map", "tide_stage": "tide predictions",
    "current_speed": "ocean current data", "time_of_day": "sunrise and sunset times",
    "salinity": "salinity data", "depth_m": "depth data", "bottom_slope": "seafloor depth data", "chlorophyll": "chlorophyll data",
    "sst_c": "sea surface temperature", "sst_gradient": "sea surface temperature",
}


def trapezoid(values, rng, ideal) -> np.ndarray:
    """1 inside the ideal band, falling linearly to 0 at the edges of the allowed range.
    A None bound means 'no limit' on that side."""
    v = np.asarray(values, float)
    lo = -np.inf if rng[0] is None else float(rng[0])
    hi = np.inf if rng[1] is None else float(rng[1])
    a = -np.inf if ideal[0] is None else float(ideal[0])
    b = np.inf if ideal[1] is None else float(ideal[1])
    s = np.zeros(v.shape)
    with np.errstate(invalid="ignore"):
        s[(v >= a) & (v <= b)] = 1.0
        if np.isfinite(a) and np.isfinite(lo) and a > lo:
            m = (v >= lo) & (v < a)
            s[m] = (v[m] - lo) / (a - lo)
        elif not np.isfinite(lo):
            s[v < a] = 1.0
        if np.isfinite(b) and np.isfinite(hi) and hi > b:
            m = (v > b) & (v <= hi)
            s[m] = (hi - v[m]) / (hi - b)
        elif not np.isfinite(hi):
            s[v > b] = 1.0
    out = np.full(v.shape, np.nan)
    fin = np.isfinite(v)
    out[fin] = s[fin]
    return out


def season_score(month, f: dict) -> float:
    """1.0 in the peak months, in_score (default 0.7) in the season, off_score (default 0.2) otherwise."""
    if month in f.get("peak_months", []):
        return 1.0
    if month in f.get("months", []):
        return float(f.get("in_score", 0.7))
    return float(f.get("off_score", 0.2))


def offshore_reference(grid: np.ndarray, depth) -> float | None:
    """95th percentile of a layer over offshore cells (a 'strong' value for today's conditions)."""
    ok = np.isfinite(grid)
    if depth is not None:
        ok &= np.isfinite(depth) & (depth >= OFFSHORE_MIN_DEPTH_M)
    if ok.sum() < 20:
        return None
    return float(np.nanpercentile(grid[ok], 95))


def factor_score(f: dict, layers: dict, ref_cache: dict):
    """Score array for one profile factor, or None if there is no layer or no usable settings."""
    p = f["param"]
    if f["kind"] == "season":                      # one value for the whole map, from the calendar month
        month = layers.get("month")
        return None if month is None else np.full(layers["sst_c"].shape, season_score(month, f))
    grid = layers.get(p)
    if grid is None:
        return None
    if f["kind"] == "range":
        if f.get("ideal") is None or f.get("range") is None:
            return None
        v, rng, ideal = grid, list(f["range"]), list(f["ideal"])
        if f.get("scale") == "log":
            with np.errstate(invalid="ignore", divide="ignore"):
                v = np.log10(np.where(grid > 0, grid, np.nan))
            rng = [None if x is None else float(np.log10(x)) for x in rng]
            ideal = [None if x is None else float(np.log10(x)) for x in ideal]
        return trapezoid(v, rng, ideal)
    if f["kind"] == "category":
        preferred = set(f.get("preferred") or [])
        if not preferred:
            return None
        weights = f.get("map") or {}
        return np.vectorize(lambda x: float(weights.get(x, 1.0 if x in preferred else 0.0)) if x is not None else np.nan, otypes=[float])(grid)
    if f["kind"] == "higher_is_better":
        if p not in ref_cache:
            ref_cache[p] = offshore_reference(grid, layers.get("depth_m"))
        ref = ref_cache[p]
        if ref is None:
            return None                      # too few offshore cells to judge what 'strong' means
        ref = max(ref, float(f.get("reference_floor", 0.0)))
        if ref <= 0:                         # flat field: no breaks anywhere today, which is a real result
            return np.where(np.isfinite(grid), 0.0, np.nan)
        return np.clip(grid / ref, 0.0, 1.0)
    return None


def _missing_message(missing: list[dict]) -> str:
    names = []
    for f in sorted(missing, key=lambda x: -x["weight"]):
        label = FRIENDLY.get(f["param"], f["param"])
        if label not in names and f["weight"] >= 0.1:
            names.append(label)
    return "Waiting for: " + (", ".join(names) if names else "more data")


def score_species(profile: dict, layers: dict) -> dict:
    active = [f for f in profile["factors"] if f.get("active") and f.get("weight", 0) > 0]
    total_w = sum(f["weight"] for f in active)
    shape = layers["sst_c"].shape
    num, avail = np.zeros(shape), np.zeros(shape)
    gate_fail = np.zeros(shape, bool)
    scores, missing, ref_cache = {}, [], {}

    for f in active:
        s = factor_score(f, layers, ref_cache)
        if s is None:
            if f.get("gate"):
                return {"status": "unavailable", "message": _missing_message([f])}
            missing.append(f)
            continue
        ok = np.isfinite(s)
        w = f["weight"]
        scores[f["param"]] = s
        num += np.where(ok, s * w, 0.0)
        avail += np.where(ok, w, 0.0)
        if f.get("gate"):
            gate_fail |= ~ok | (s <= 0)

    coverage = avail / total_w if total_w else avail
    min_cov = profile.get("min_coverage", DEFAULT_MIN_COVERAGE)
    if coverage.max() < min_cov:
        return {"status": "unavailable", "message": _missing_message(missing)}

    with np.errstate(invalid="ignore", divide="ignore"):
        score = np.where(avail > 0, num / avail, np.nan)
    eligible = ~gate_fail & (coverage >= min_cov) & np.isfinite(layers["sst_c"])
    score = np.where(eligible, score, np.nan)
    return {"status": "ok", "score": score, "coverage": coverage, "scores": scores,
            "ref": ref_cache, "missing": missing}


def _cell_ring(lat: float, lon: float, dlat: float, dlon: float) -> list[list[float]]:
    a, b, c, d = lon - dlon / 2, lat - dlat / 2, lon + dlon / 2, lat + dlat / 2
    return [[a, b], [c, b], [c, d], [a, d], [a, b]]


def split_component(comp: list, block: int | None) -> list:
    """Split a large connected area into patches of at most block x block cells, so one long reef
    tract is not reported as a single area."""
    if not block or len(comp) <= block * block:
        return [comp]
    groups: dict = {}
    for i, j in comp:
        groups.setdefault((i // block, j // block), []).append((i, j))
    return list(groups.values())


def find_spots(score: np.ndarray, lats: np.ndarray, lons: np.ndarray, min_cells: int = MIN_CELLS,
               max_spots: int = MAX_SPOTS, zone_style: str = "hull", block_cells: int | None = None):
    """Best connected areas. Returns (spots, best_score).
    zone_style 'hull' outlines each area; 'cells' keeps the exact cells (for reefs and other thin features)."""
    ok = np.isfinite(score)
    if not ok.any():
        return [], None
    best = float(np.nanmax(score))
    cutoff = max(MIN_SCORE_REPORT, float(np.nanpercentile(score[ok], 100 * (1 - TOP_FRACTION))))
    dlat, dlon = abs(float(lats[1] - lats[0])), abs(float(lons[1] - lons[0]))
    spots = []
    patches = [c for comp in components(ok & (score >= cutoff)) for c in split_component(comp, block_cells)]
    for comp in patches:
        if len(comp) < min_cells:
            continue
        vals = [score[i, j] for i, j in comp]
        bi, bj = comp[int(np.argmax(vals))]
        spot = {"cell": (bi, bj), "score": float(max(vals)), "mean": float(np.mean(vals)), "cells": len(comp),
                "members": comp, "area_km2": len(comp) * cell_km2(float(lats[bi]), dlat, dlon)}
        if zone_style == "cells":
            spot["rings"] = [_cell_ring(float(lats[i]), float(lons[j]), dlat, dlon) for i, j in comp]
        else:
            pts = [(float(lons[j] + sx * dlon / 2), float(lats[i] + sy * dlat / 2))
                   for i, j in comp for sx in (-1, 1) for sy in (-1, 1)]
            ring = convex_hull(pts)
            ring.append(ring[0])
            spot["ring"] = ring
        spots.append(spot)
    spots.sort(key=lambda s: (-round(s["score"], 2), -s["cells"]))
    return spots[:max_spots], best
