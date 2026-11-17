#!/usr/bin/env python3
"""Read-only Copernicus bottom-temperature coverage assessment using NOAA ETOPO."""
from __future__ import annotations
import json, sys
from io import StringIO
from pathlib import Path
from urllib.parse import quote
import numpy as np
import pandas as pd
import requests
import xarray as xr

SOURCE_ROOT = Path("artifacts/source-pilot")
OUTPUT_ROOT = Path("artifacts/copernicus-bottom-temperature-bathymetry")
ETOPO_BASE = "https://oceanwatch.pifsc.noaa.gov/erddap/griddap/ETOPO_2022_v1_30s"
STRIDE = 10
COAST_BAND_M = 1.0
DEPTH_CLASSES = [
    ("0-10m", 0.0, 10.0), ("10-50m", 10.0, 50.0),
    ("50-200m", 50.0, 200.0), ("200-500m", 200.0, 500.0),
    ("500-2000m", 500.0, 2000.0), (">2000m", 2000.0, float("inf")),
]

def lon360(value):
    return value + 360.0 if value < 0 else value

def fetch_etopo(region, bbox):
    lat0, lat1 = float(bbox["minimum_latitude"]), float(bbox["maximum_latitude"])
    lon0 = lon360(float(bbox["minimum_longitude"]))
    lon1 = lon360(float(bbox["maximum_longitude"]))
    query = f"z[({lat0}):{STRIDE}:({lat1})][({lon0}):{STRIDE}:({lon1})]"
    url = f"{ETOPO_BASE}.csv0?{quote(query, safe='[]():.')}"
    print(f"Fetching ETOPO for {region}: {url}", flush=True)
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    try:
        frame = pd.read_csv(StringIO(response.text))
    except Exception as exc:
        raise RuntimeError(f"{region}: ETOPO CSV parse failed: {response.text[:500]}") from exc
    frame.columns = [str(c).strip().lower() for c in frame.columns]
    if not {"latitude", "longitude", "z"}.issubset(frame.columns):
        raise RuntimeError(f"{region}: unexpected ETOPO columns {list(frame.columns)}: {response.text[:500]}")
    frame = frame[["latitude", "longitude", "z"]].apply(pd.to_numeric, errors="coerce").dropna()
    grid = frame.pivot(index="latitude", columns="longitude", values="z").sort_index().sort_index(axis=1)
    if grid.empty:
        raise RuntimeError(f"{region}: ETOPO returned no cells")
    lat = grid.index.to_numpy(float)
    lon360_values = grid.columns.to_numpy(float)
    lon = np.where(lon360_values > 180.0, lon360_values - 360.0, lon360_values)
    elev = grid.to_numpy(float)
    if not np.isfinite(elev).all():
        raise RuntimeError(f"{region}: ETOPO returned non-finite elevations")
    return lat, lon, elev

def source_path(record):
    prefix = Path("artifacts/copernicus-bottom-temperature-pilot")
    return SOURCE_ROOT / Path(record["file"]).relative_to(prefix)

def depth_label(depth):
    for label, low, high in DEPTH_CLASSES:
        if low <= depth < high:
            return label
    return "unclassified"

def temp_stats(values, mask):
    v = values[mask & np.isfinite(values)]
    return {
        "valid_temperature_cells": int(v.size),
        "temperature_min_c": float(v.min()) if v.size else None,
        "temperature_median_c": float(np.median(v)) if v.size else None,
        "temperature_mean_c": float(v.mean()) if v.size else None,
        "temperature_max_c": float(v.max()) if v.size else None,
    }

def assess(record, bathy):
    path = source_path(record)
    if not path.is_file():
        raise FileNotFoundError(path)
    etopo_lat, etopo_lon, elev = bathy
    variable = record["variable"]
    with xr.open_dataset(path, decode_cf=True, mask_and_scale=True) as ds:
        if variable not in ds.data_vars:
            raise RuntimeError(f"{path}: expected {variable}; found {list(ds.data_vars)}")
        field = ds[variable]
        if not {"latitude", "longitude"}.issubset(field.dims):
            raise RuntimeError(f"{path}: unexpected dimensions {field.dims}")
        values = np.asarray(field.squeeze(drop=True).values, dtype=float)
        model_lat = np.asarray(ds["latitude"].values, dtype=float)
        model_lon = np.asarray(ds["longitude"].values, dtype=float)
    if values.shape != elev.shape:
        raise RuntimeError(f"{path}: model shape {values.shape} != ETOPO shape {elev.shape}")
    if len(model_lat) != len(etopo_lat) or len(model_lon) != len(etopo_lon):
        raise RuntimeError(f"{path}: model and ETOPO coordinate lengths differ")
    model_lon = np.where(model_lon > 180.0, model_lon - 360.0, model_lon)
    dlat = float(np.max(np.abs(model_lat - etopo_lat)))
    dlon = float(np.max(np.abs(model_lon - etopo_lon)))
    if max(dlat, dlon) > 0.006:
        raise RuntimeError(f"{path}: nearest ETOPO centers too far from model grid (lat={dlat}, lon={dlon})")

    finite_elev = np.isfinite(elev)
    land = finite_elev & (elev > COAST_BAND_M)
    ocean = finite_elev & (elev < -COAST_BAND_M)
    coast = finite_elev & ~(land | ocean)
    valid = np.isfinite(values)
    ocean_valid = ocean & valid
    ocean_missing = ocean & ~valid

    rows = []
    for iy, lat in enumerate(model_lat):
        for ix, lon in enumerate(model_lon):
            z = float(elev[iy, ix])
            is_ocean = bool(ocean[iy, ix])
            depth = -z if is_ocean else None
            rows.append({
                "kind": record["kind"], "region": record["region"], "date": record["requested_date"],
                "latitude": float(lat), "longitude": float(lon), "etopo_elevation_m": z,
                "seafloor_depth_m": depth,
                "depth_class": depth_label(depth) if depth is not None else ("land" if land[iy, ix] else "coast_ambiguous"),
                "bottom_temperature_c": float(values[iy, ix]) if valid[iy, ix] else None,
                "temperature_valid": bool(valid[iy, ix]),
                "etopo_class": "ocean" if is_ocean else ("land" if land[iy, ix] else "coast_ambiguous"),
            })
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    csv_path = OUTPUT_ROOT / f"{record['kind']}_{record['region']}_grid.csv"
    pd.DataFrame(rows).to_csv(csv_path, index=False)

    by_depth = {}
    for label, low, high in DEPTH_CLASSES:
        mask = ocean & (-elev >= low) & (-elev < high)
        n = int(mask.sum())
        nvalid = int((mask & valid).sum())
        by_depth[label] = {
            "ocean_cells": n, "valid_temperature_cells": nvalid,
            "missing_temperature_cells": n - nvalid,
            "ocean_only_coverage_fraction": nvalid / n if n else None,
            **temp_stats(values, mask),
        }
    n_ocean, n_ocean_valid = int(ocean.sum()), int(ocean_valid.sum())
    return {
        "kind": record["kind"], "region": record["region"], "date": record["requested_date"],
        "dataset_id": record["dataset_id"], "variable": variable, "grid_shape": list(values.shape),
        "grid_cells_total": int(values.size), "etopo_land_cells_gt_1m": int(land.sum()),
        "etopo_ocean_cells_lt_minus_1m": n_ocean, "etopo_coastal_ambiguous_cells_plus_minus_1m": int(coast.sum()),
        "valid_temperature_on_land_cells": int((land & valid).sum()),
        "missing_temperature_on_land_cells": int((land & ~valid).sum()),
        "valid_temperature_on_ocean_cells": n_ocean_valid,
        "missing_temperature_on_ocean_cells": int(ocean_missing.sum()),
        "ocean_only_coverage_fraction": n_ocean_valid / n_ocean if n_ocean else None,
        "all_grid_valid_fraction_for_reference": float(valid.mean()),
        "max_model_to_etopo_latitude_offset_deg": dlat,
        "max_model_to_etopo_longitude_offset_deg": dlon,
        "depth_class_statistics": by_depth,
        "per_cell_csv": str(csv_path),
        "temperature_statistics_all_valid_cells": temp_stats(values, np.ones(values.shape, dtype=bool)),
        "classification": {
            "land": "ETOPO elevation > +1 m", "ocean": "ETOPO elevation < -1 m",
            "coastal_ambiguous": "ETOPO elevation from -1 m through +1 m",
            "depth_classes_m": [x[0] for x in DEPTH_CLASSES],
            "bathymetry_source": "NOAA NCEI ETOPO 2022, 30 arc-second ERDDAP grid",
            "sampling": "nearest ETOPO grid center, 10-cell stride (~0.083333 degrees)",
        },
    }

def main():
    summary_path = SOURCE_ROOT / "pilot-summary.json"
    if not summary_path.is_file():
        raise FileNotFoundError(summary_path)
    records = json.loads(summary_path.read_text()).get("results", [])
    if len(records) != 8:
        raise RuntimeError(f"Expected 8 pilot records; got {len(records)}")
    grouped = {}
    for rec in records:
        grouped.setdefault(rec["region"], []).append(rec)
    results = []
    for region, region_records in grouped.items():
        bathy = fetch_etopo(region, region_records[0]["requested_bbox"])
        for rec in region_records:
            results.append(assess(rec, bathy))
    output = {
        "purpose": "ocean-only coverage and spatial/depth-pattern assessment; not accuracy validation",
        "source_run_id": 44144656207,
        "bathymetry_source": {
            "name": "NOAA NCEI ETOPO 2022, 30 arc-second global relief model",
            "dataset_id": "ETOPO_2022_v1_30s",
            "url": ETOPO_BASE,
            "vertical_sign": "positive up; ocean depths are negative elevations",
            "caveat": "Global relief model, not a navigation chart; near-zero coastal cells remain ambiguous.",
        },
        "requests": len(results), "results": results,
    }
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    report = OUTPUT_ROOT / "bathymetry-assessment.json"
    report.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))
    print(f"Wrote {report}")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
