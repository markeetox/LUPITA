#!/usr/bin/env python3
"""Export a full-resolution NOAA ETOPO 2022 30-arc-second grid for GLD QA."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from urllib.parse import quote

import numpy as np
import pandas as pd
import requests

ETOPO_BASE = "https://oceanwatch.pifsc.noaa.gov/erddap/griddap/ETOPO_2022_v1_30s"
GRID_RESOLUTION_DEG = 1.0 / 120.0
FILL_VALUE = -99999.0
COAST_BAND_M = 1.0
OUTPUT_ROOT = Path("artifacts/wod-gld-etopo-grid")

# Includes every verified GLD header and per-observation coordinate, with a small margin.
BBOX = {
    "minimum_latitude": 24.45,
    "maximum_latitude": 26.55,
    "minimum_longitude": -81.05,
    "maximum_longitude": -79.45,
}


def lon360(value: float) -> float:
    return value + 360.0 if value < 0.0 else value


def build_request_url(bbox: dict[str, float] = BBOX) -> str:
    lat0 = float(bbox["minimum_latitude"])
    lat1 = float(bbox["maximum_latitude"])
    lon0 = lon360(float(bbox["minimum_longitude"]))
    lon1 = lon360(float(bbox["maximum_longitude"]))
    # Stride 1 preserves every 30-arc-second ETOPO grid cell.
    query = f"z[({lat0}):1:({lat1})][({lon0}):1:({lon1})]"
    return f"{ETOPO_BASE}.csv?{quote(query, safe='[]():.')}"


def parse_etopo_csv(csv_text: str) -> pd.DataFrame:
    frame = pd.read_csv(StringIO(csv_text), skiprows=[1])
    frame.columns = [str(column).strip().lower() for column in frame.columns]
    required = {"latitude", "longitude", "z"}
    if not required.issubset(frame.columns):
        raise ValueError(f"Unexpected ETOPO columns: {list(frame.columns)}")

    frame = frame[["latitude", "longitude", "z"]].apply(
        pd.to_numeric, errors="coerce"
    )
    frame = frame.dropna(subset=["latitude", "longitude"]).copy()
    frame = frame.rename(columns={"z": "etopo_elevation_m"})
    frame.loc[frame["etopo_elevation_m"] <= FILL_VALUE, "etopo_elevation_m"] = np.nan

    # ERDDAP longitude is 0..360; the GLD archive uses -180..180.
    frame["longitude"] = np.where(
        frame["longitude"] > 180.0,
        frame["longitude"] - 360.0,
        frame["longitude"],
    )

    elevation = frame["etopo_elevation_m"].to_numpy(dtype=float)
    valid = np.isfinite(elevation)
    ocean = valid & (elevation < -COAST_BAND_M)
    land = valid & (elevation > COAST_BAND_M)
    coast = valid & ~(ocean | land)

    frame["seafloor_depth_m"] = np.where(ocean, -elevation, np.nan)
    frame["etopo_class"] = np.select(
        [ocean, land, coast],
        ["ocean", "land", "coast_ambiguous"],
        default="missing",
    )
    return frame.sort_values(["latitude", "longitude"]).reset_index(drop=True)


def validate_grid(frame: pd.DataFrame) -> dict[str, int | float]:
    if frame.empty:
        raise ValueError("ETOPO subset is empty")
    if frame[["latitude", "longitude"]].duplicated().any():
        raise ValueError("ETOPO subset contains duplicate coordinate pairs")

    latitudes = np.sort(frame["latitude"].unique())
    longitudes = np.sort(frame["longitude"].unique())
    if len(latitudes) < 2 or len(longitudes) < 2:
        raise ValueError("ETOPO subset must contain multiple rows and columns")

    lat_steps = np.diff(latitudes)
    lon_steps = np.diff(longitudes)
    if not np.allclose(lat_steps, GRID_RESOLUTION_DEG, rtol=0.0, atol=1e-7):
        raise ValueError(f"Unexpected latitude spacing: {np.unique(np.round(lat_steps, 10))}")
    if not np.allclose(lon_steps, GRID_RESOLUTION_DEG, rtol=0.0, atol=1e-7):
        raise ValueError(f"Unexpected longitude spacing: {np.unique(np.round(lon_steps, 10))}")

    expected_cells = len(latitudes) * len(longitudes)
    if len(frame) != expected_cells:
        raise ValueError(
            f"Incomplete ETOPO rectangle: {len(frame)} rows for "
            f"{len(latitudes)} x {len(longitudes)} coordinates"
        )

    return {
        "rows": int(len(frame)),
        "latitude_count": int(len(latitudes)),
        "longitude_count": int(len(longitudes)),
        "latitude_min": float(latitudes.min()),
        "latitude_max": float(latitudes.max()),
        "longitude_min": float(longitudes.min()),
        "longitude_max": float(longitudes.max()),
        "resolution_degrees": float(GRID_RESOLUTION_DEG),
        "missing_elevation_count": int(frame["etopo_elevation_m"].isna().sum()),
    }


def main() -> None:
    url = build_request_url()
    print(f"Requesting full-resolution ETOPO subset: {url}", flush=True)
    response = requests.get(url, timeout=180)
    response.raise_for_status()

    frame = parse_etopo_csv(response.text)
    grid_info = validate_grid(frame)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    csv_path = OUTPUT_ROOT / "wod_gld_south_florida_etopo_30s.csv"
    frame.to_csv(csv_path, index=False)
    csv_sha256 = hashlib.sha256(csv_path.read_bytes()).hexdigest()

    metadata = {
        "purpose": "research-only seabed-depth join for South Florida WOD GLD profiles",
        "source": "NOAA NCEI ETOPO 2022, 30 arc-second, Ice Surface grid",
        "dataset_id": "ETOPO_2022_v1_30s",
        "base_url": ETOPO_BASE,
        "request_url": url,
        "requested_bbox": BBOX,
        "longitude_input_conversion": "negative longitudes converted to 0..360 for ERDDAP request",
        "longitude_output": "normalized to -180..180",
        "vertical_sign": "ETOPO z is positive up; ocean seafloor depth is -z",
        "ocean_threshold": f"elevation < -{COAST_BAND_M} m",
        "land_threshold": f"elevation > +{COAST_BAND_M} m",
        "coastal_ambiguous_band_m": [-COAST_BAND_M, COAST_BAND_M],
        "grid": grid_info,
        "csv_sha256": csv_sha256,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "caveat": "ETOPO is a global relief model, not a navigation chart; this export does not itself establish near-bottom eligibility.",
    }
    metadata_path = OUTPUT_ROOT / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(metadata, indent=2))
    print(f"Wrote {csv_path} and {metadata_path}")


if __name__ == "__main__":
    main()
