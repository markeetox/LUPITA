"""Download the satellite and depth grids and put them on one common grid (the SST grid)."""
from __future__ import annotations

import numpy as np

from pipeline import closures, currents, derive, grid, habitat, structure
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


def curvature_layer(depth, lats, lons):
    """Seafloor curvature (second spatial derivative / Laplacian) in m / km^2. None if there is no depth grid."""
    if depth is None:
        return None
    c = derive.bottom_curvature(depth, lats, lons)
    m = EDGE_MARGIN_CELLS
    c[:m, :] = np.nan; c[-m:, :] = np.nan; c[:, :m] = np.nan; c[:, -m:] = np.nan
    return c


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


def _fetch_multi(cfg: dict, region: dict, fetch):
    """Several variables from one dataset, trying the main server then any fallback_bases."""
    last = None
    for base in [cfg["base"]] + list(cfg.get("fallback_bases", [])):
        try:
            url = erddap.build_griddap_url({**cfg, "base": base}, region)
            return erddap.parse_multi_csv(fetch(url), cfg["variables"])
        except Exception as exc:
            last = exc
    raise last


def load_layers(sources: dict, errors: list[str], fetch=erddap.fetch_csv, fetch_arc=arcgis.fetch_json, places: dict | None = None):
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
              "chlorophyll": None, "chl_gradient": None, "depth_m": None, "chl_raw": None,
              "chlorophyll_gapfilled": False,
              "distance_to_inlet": None, "bottom_slope": None, "bottom_curvature": None,
              "current_speed": None, "current_dir": None, "current_convergence": None,
              "gulf_stream_edge": None, "stream_edge_lon": None,
              "closure_areas": [], "closure_cover": None, "closure_info": {}, "closure_checked": False,
              "structure_type": None, "structure_info": {}, "structure_cover": None, "structure_stats": None,
              "habitat_features": {}, "habitat_mapped_cover": None, "habitat_polygons": [], "habitat_info": {},
              "times": {"sst": sst_time, "chlorophyll": None},
              "datasets": {"sst": cfg["sst"]["dataset"]}}

    if places and places.get("places"):
        inlets = [p for p in places["places"] if p.get("kind") in ("inlet", "pass") or p.get("type") in ("inlet", "pass")]
        if inlets:
            layers["distance_to_inlet"] = derive.distance_to_inlet_grid(lats, lons, inlets)

    c = cfg.get("chlorophyll", {})
    cg = cfg.get("chlorophyll_gapfilled", {})
    primary_chl = None
    primary_resampled = None
    primary_time = None
    primary_valid_frac = 0.0

    if c.get("enabled"):
        try:
            clats, clons, chl, chl_time, _ = _fetch_grid(c, region, fetch)
            layers["chl_raw"] = (clats, clons, chl)
            primary_chl = chl
            primary_time = chl_time
            primary_resampled = resample(chl, clats, clons, lats, lons, min_weight=0.5)
            primary_valid_frac = float(np.isfinite(primary_resampled).sum()) / primary_resampled.size if primary_resampled.size else 0.0
        except Exception as exc:
            errors.append(f"layers chlorophyll: {exc}")

    final_chl = primary_resampled
    used_gapfilled = False
    chl_dataset = c.get("dataset") if primary_resampled is not None else None
    final_time = primary_time

    if (final_chl is None or primary_valid_frac < 0.25) and cg.get("enabled"):
        try:
            glats, glons, gchl, gchl_time, _ = _fetch_grid(cg, region, fetch)
            gapfilled_resampled = resample(gchl, glats, glons, lats, lons, min_weight=0.5)
            if final_chl is not None:
                final_chl = np.where(np.isfinite(final_chl), final_chl, gapfilled_resampled)
            else:
                final_chl = gapfilled_resampled
            used_gapfilled = True
            chl_dataset = f"{c.get('dataset', '')} + {cg.get('dataset', '')} (gap-filled)" if c.get("enabled") else cg.get("dataset")
            final_time = primary_time or gchl_time
        except Exception as exc:
            errors.append(f"layers chlorophyll_gapfilled: {exc}")

    if final_chl is not None:
        layers["chlorophyll"] = final_chl
        layers["chl_gradient"] = derive.chlorophyll_gradient(final_chl, lats, lons)
        layers["times"]["chlorophyll"] = final_time
        layers["datasets"]["chlorophyll"] = chl_dataset
        layers["chlorophyll_gapfilled"] = used_gapfilled

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
    cu = cfg.get("currents", {})
    if cu.get("enabled"):
        try:
            clats, clons, g, ctime = _fetch_multi(cu, region, fetch)
            u_name, v_name = cu["variables"]
            u = resample(g[u_name], clats, clons, lats, lons, min_weight=0.5)
            v = resample(g[v_name], clats, clons, lats, lons, min_weight=0.5)
            layers["current_speed"], layers["current_dir"] = currents.speed_dir(u, v)
            layers["current_convergence"] = derive.current_convergence(u, v, lats, lons)
            edge = currents.edge_on_grid(clats, currents.smooth(currents.edge_longitudes(clats, clons, g[v_name])), lats)
            if edge is not None:
                layers["stream_edge_lon"] = edge
                layers["gulf_stream_edge"] = currents.signed_km(edge, lats, lons)
            layers["times"]["currents"] = ctime
            layers["datasets"]["currents"] = cu["dataset"]
        except Exception as exc:
            errors.append(f"layers currents: {exc}")

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
    hb = a.get("unified_benthic", {})
    if hb.get("enabled"):
        try:
            habitat_region = hb.get("query_region", region)
            features = arcgis.query_all(hb["url"], habitat_region, fetch=fetch_arc, return_geometry=True,
                                        simplify=hb.get("simplify_deg", 0.0005),
                                        where=hb.get("where", "1=1"),
                                        page_size=hb.get("page_size", 2000),
                                        max_pages=hb.get("max_pages", 100))
            habitat_layers, habitat_stats = habitat.build_habitat_layers(
                features, lats, lons, hb.get("class_field", "FIRST_ClassLv0"))
            layers["habitat_features"] = habitat_layers["covers"]
            layers["habitat_mapped_cover"] = habitat_layers["mapped_cover"]
            layers["habitat_polygons"] = features
            layers["habitat_info"] = {
                **habitat_stats,
                "dataset": hb.get("source_label", "FWC Unified Reef Map"),
                "version": hb.get("version"),
                "release_date": hb.get("release_date"),
                "class_field": hb.get("class_field", "FIRST_ClassLv0"),
                "coverage_semantics": "Zero category cover outside mapped polygons means unknown, not confirmed absence.",
                "query_region": habitat_region,
                "sample_cell_km": hb.get("sample_cell_km", 0.25)
            }
            layers["datasets"]["benthic_habitat"] = hb.get("source_label", "FWC Unified Reef Map")
        except Exception as exc:
            errors.append(f"layers benthic_habitat: {exc}")
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
    layers["bottom_curvature"] = curvature_layer(layers["depth_m"], lats, lons)
    layers["marine_mask"] = grid.build_marine_mask(layers["depth_m"])
    return layers
