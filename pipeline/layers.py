"""Download the satellite and depth grids and put them on one common grid (the SST grid)."""
from __future__ import annotations

import numpy as np

from pipeline import closures, derive, structure
from pipeline.grid import resample
from pipeline.sources import arcgis, erddap


EDGE_MARGIN_CELLS = 2
FRONT_MIN_DEPTH_M = 30.0   # shallow banks and shelves heat up faster; their edges are not ocean fronts


def front_strength(sst, depth, lats, lons, min_depth: float = FRONT_MIN_DEPTH_M):
    """Temperature-break strength that ignores shallow water. Cells next to shallow or missing
    depth are NaN, so bank and shelf edges never count as fronts."""
    if depth is None:
        g = derive.gradient_magnitude(sst, lats, lons)
    else:
        deep_sst = np.where(np.isfinite(depth) & (depth >= min_depth), sst, np.nan)
        g = derive.gradient_magnitude(deep_sst, lats, lons)
    m = EDGE_MARGIN_CELLS                      # gradients at the grid border are one-sided and areas there get clipped
    g[:m, :] = np.nan; g[-m:, :] = np.nan; g[:, :m] = np.nan; g[:, -m:] = np.nan
    return g


def slope_layer(depth, lats, lons):
    """Seafloor slope in metres of depth change per km. None if there is no depth grid."""
    if depth is None:
        return None
    g = derive.gradient_magnitude(depth, lats, lons)
    m = EDGE_MARGIN_CELLS
    g[:m, :] = np.nan; g[-m:, :] = np.nan; g[:, :m] = np.nan; g[:, -m:] = np.nan
    return g


def _fetch_grid(cfg: dict, region: dict, fetch):
    """Try the main ERDDAP server, then any fallback_bases from the config."""
    last = None
    for base in [cfg["base"]] + list(cfg.get("fallback_bases", [])):
        try:
            url = erddap.build_griddap_url({**cfg, "base": base}, region)
            return erddap.parse_grid_csv(fetch(url), cfg["variable"])
        except Exception as exc:
            last = exc
    raise last


def load_layers(sources: dict, errors: list[str], fetch=erddap.fetch_csv, fetch_arc=arcgis.fetch_json):
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
              "bottom_slope": None, "closure_areas": [], "closure_cover": None, "closure_info": {}, "closure_checked": False,
              "structure_type": None, "structure_info": {}, "structure_cover": None, "structure_stats": None,
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
    a = sources.get("arcgis", {})
    art, nat = a.get("artificial_reefs", {}), a.get("natural_reef", {})
    if art.get("enabled") and nat.get("enabled"):
        # Both sources are required: with artificial reefs alone, natural reef would wrongly look empty.
        try:
            art_f = arcgis.query_all(art["url"], region, fetch=fetch_arc)
            nat_f = arcgis.query_all(nat["url"], region, fetch=fetch_arc, return_geometry=True,
                                     simplify=nat.get("simplify_deg", 0.0005), where=nat.get("where", "1=1"),
                                     page_size=nat.get("page_size", 1000))
            types, info, cover = structure.build_structure_layer(art_f, nat_f, lats, lons, nat.get("min_cover", 0.01))
            layers.update(structure_type=types, structure_info=info, structure_cover=cover, structure_stats={
                "artificial_reef_records": len(art_f), "natural_reef_polygons": len(nat_f),
                "cells_wreck": int((types == "wreck").sum()), "cells_artificial_reef": int((types == "artificial_reef").sum()),
                "cells_natural_reef": int((types == "natural_reef").sum())})
            layers["datasets"]["structure"] = "FWC artificial reefs + FWC Unified Reef Map v2.2"
        except Exception as exc:
            errors.append(f"layers structure: {exc}")
    cl = sources.get("closures", {})
    if cl.get("enabled"):
        try:
            feats = arcgis.query_all(cl["url"], region, fetch=fetch_arc, return_geometry=True,
                                     simplify=cl.get("simplify_deg", 0.0005), where=cl.get("where", "1=1"),
                                     page_size=cl.get("page_size", 1000))
            areas = closures.parse_closures(feats)
            if len(areas) < cl.get("min_expected", 0):
                # South Florida certainly has some. Zero usually means the filter no longer matches the data.
                raise RuntimeError(f"only {len(areas)} no-fishing areas returned; the filter may not match the data")
            cover, info = np.zeros(sst.shape), {}
            for a in areas:
                c = structure.rasterize_cover([{"geometry": {"rings": a["rings"]}}], lats, lons)
                cover = np.minimum(1.0, cover + c)
                for i, j in zip(*np.nonzero(c >= 0.01)):
                    info.setdefault((int(i), int(j)), []).append({"name": a["name"], "cover": float(c[i, j])})
            layers.update(closure_areas=areas, closure_cover=cover, closure_info=info, closure_checked=True)
            layers["datasets"]["closures"] = cl.get("source_label", "NOAA MPA Inventory")
        except Exception as exc:
            errors.append(f"layers closures: {exc}")
    layers["sst_gradient"] = front_strength(sst, layers["depth_m"], lats, lons)
    layers["bottom_slope"] = slope_layer(layers["depth_m"], lats, lons)
    return layers
