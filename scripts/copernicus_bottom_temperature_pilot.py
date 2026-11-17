#!/usr/bin/env python3
"""Read-only Copernicus bottom-temperature pilot.

Downloads one daily sea-floor potential-temperature field for each of four
regional bounding boxes from both the forecast and reanalysis datasets.
This is a coverage/structure smoke test, not an accuracy validation.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import xarray as xr

ROOT = Path("artifacts/copernicus-bottom-temperature-pilot")
REGIONS = {
    "south_florida_keys": {"minimum_longitude": -81.0, "maximum_longitude": -79.5, "minimum_latitude": 24.5, "maximum_latitude": 26.5},
    "gulf_shelf": {"minimum_longitude": -90.0, "maximum_longitude": -88.0, "minimum_latitude": 28.0, "maximum_latitude": 29.0},
    "atlantic_shelf": {"minimum_longitude": -75.0, "maximum_longitude": -73.0, "minimum_latitude": 34.0, "maximum_latitude": 36.0},
    "pacific_west_coast": {"minimum_longitude": -123.0, "maximum_longitude": -121.0, "minimum_latitude": 37.0, "maximum_latitude": 39.0},
}
DATASETS = {
    "forecast": {
        "dataset_id": "cmems_mod_glo_phy_anfc_0.083deg_P1D-m",
        "version": "202406",
        "variable": "tob",
        "date_env": "COPERNICUS_PILOT_FORECAST_DATE",
    },
    "reanalysis": {
        "dataset_id": "cmems_mod_glo_phy_my_0.083deg_P1D-m",
        "version": "202311",
        "variable": "bottomT",
        "date_env": "COPERNICUS_PILOT_REANALYSIS_DATE",
    },
}


def subset_one(kind: str, region_name: str, region: dict, config: dict, date: str) -> dict:
    dataset_id = config["dataset_id"]
    variable = config["variable"]
    filename = f"{kind}_{region_name}_{date}.nc"
    output_dir = ROOT / kind / region_name
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename

    command = [
        "copernicusmarine", "subset",
        "--dataset-id", dataset_id,
        "--dataset-version", config["version"],
        "--variable", variable,
        "--start-datetime", date,
        "--end-datetime", date,
        "--minimum-longitude", str(region["minimum_longitude"]),
        "--maximum-longitude", str(region["maximum_longitude"]),
        "--minimum-latitude", str(region["minimum_latitude"]),
        "--maximum-latitude", str(region["maximum_latitude"]),
        "--output-directory", str(output_dir),
        "--output-filename", filename,
    ]
    print(f"\n=== {kind}/{region_name} {date} ===", flush=True)
    subprocess.run(command, check=True)

    if not output_path.is_file():
        matches = list(output_dir.glob("*.nc"))
        if len(matches) != 1:
            raise RuntimeError(f"Expected {output_path}; found NetCDF files: {matches}")
        output_path = matches[0]

    with xr.open_dataset(output_path, decode_cf=True) as ds:
        if variable not in ds.data_vars:
            raise RuntimeError(f"{output_path}: expected {variable}; got {list(ds.data_vars)}")
        field = ds[variable]
        required_coords = {"time", "latitude", "longitude"}
        if not required_coords.issubset(set(ds.coords) | set(ds.dims)):
            raise RuntimeError(f"{output_path}: missing expected coordinates; coords={list(ds.coords)}, dims={list(ds.dims)}")
        if "depth" in field.dims or "depth" in ds.coords:
            raise RuntimeError(f"{output_path}: unexpected vertical depth axis on sea-floor field: {field.dims}")

        values = np.asarray(field.values, dtype="float64")
        valid = np.isfinite(values)
        valid_values = values[valid]
        total = int(values.size)
        valid_count = int(valid.sum())
        report = {
            "kind": kind,
            "dataset_id": dataset_id,
            "dataset_version": config["version"],
            "variable": variable,
            "standard_name": field.attrs.get("standard_name"),
            "units": field.attrs.get("units"),
            "region": region_name,
            "requested_date": date,
            "requested_bbox": region,
            "file": str(output_path),
            "file_bytes": output_path.stat().st_size,
            "dimensions": {key: int(value) for key, value in field.sizes.items()},
            "coordinates": {
                key: {
                    "minimum": str(ds[key].values.min()),
                    "maximum": str(ds[key].values.max()),
                    "count": int(ds[key].size),
                }
                for key in ("time", "latitude", "longitude")
            },
            "total_values": total,
            "valid_values": valid_count,
            "missing_values": total - valid_count,
            "valid_fraction": (valid_count / total) if total else 0.0,
            "minimum_value": float(valid_values.min()) if valid_count else None,
            "maximum_value": float(valid_values.max()) if valid_count else None,
            "mean_value": float(valid_values.mean()) if valid_count else None,
            "field_attributes": {key: str(value) for key, value in field.attrs.items()},
            "fill_value_encoding": str(field.encoding.get("_FillValue")),
            "global_attributes": {
                key: str(ds.attrs[key])
                for key in ("title", "source", "institution", "product", "dataset", "time_coverage_start", "time_coverage_end")
                if key in ds.attrs
            },
        }
    print(json.dumps(report, indent=2), flush=True)
    return report


def main() -> int:
    ROOT.mkdir(parents=True, exist_ok=True)
    results = []
    for kind, config in DATASETS.items():
        date = os.environ[config["date_env"]]
        for region_name, region in REGIONS.items():
            results.append(subset_one(kind, region_name, region, config, date))

    summary = {
        "purpose": "read-only metadata/coverage smoke test; not an accuracy validation",
        "requests": len(results),
        "results": results,
    }
    report_path = ROOT / "pilot-summary.json"
    report_path.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"\nWrote {report_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
