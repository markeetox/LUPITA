#!/usr/bin/env python3
"""Export a full-resolution NOAA ETOPO 2022 30-arc-second grid for GLD QA."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from urllib.parse import quote

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


def parse_etopo_csv(csv_text: str) -> list[dict[str, float | str | None]]:
    lines = csv_text.splitlines()
    if len(lines) < 3:
        raise ValueError("ETOPO CSV must contain a header, units row, and data")
    reader = csv.DictReader(StringIO("\n".join([lines[0], *lines[2:]])))
    if not reader.fieldnames:
        raise ValueError("ETOPO CSV has no header")
    columns = {name.strip().lower(): name for name in reader.fieldnames}
    if not {"latitude", "longitude", "z"}.issubset(columns):
        raise ValueError(f"Unexpected ETOPO columns: {reader.fieldnames}")

    rows: list[dict[str, float | str | None]] = []
    for raw in reader:
        try:
            latitude = float(raw[columns["latitude"]])
            longitude = float(raw[columns["longitude"]])
        except (TypeError, ValueError):
            continue
        try:
            elevation = float(raw[columns["z"]])
            if not math.isfinite(elevation) or elevation <= FILL_VALUE:
                elevation = None
        except (TypeError, ValueError):
            elevation = None

        # ERDDAP longitude is 0..360; the GLD archive uses -180..180.
        if longitude > 180.0:
            longitude -= 360.0

        if elevation is None:
            seafloor_depth = None
            etopo_class = "missing"
        elif elevation < -COAST_BAND_M:
            seafloor_depth = -elevation
            etopo_class = "ocean"
        elif elevation > COAST_BAND_M:
            seafloor_depth = None
            etopo_class = "land"
        else:
            seafloor_depth = None
            etopo_class = "coast_ambiguous"

        rows.append({
            "latitude": latitude,
            "longitude": longitude,
            "etopo_elevation_m": elevation,
            "seafloor_depth_m": seafloor_depth,
            "etopo_class": etopo_class,
        })

    return sorted(rows, key=lambda row: (row["latitude"], row["longitude"]))


def validate_grid(rows: list[dict[str, float | str | None]]) -> dict[str, int | float]:
    if not rows:
        raise ValueError("ETOPO subset is empty")
    coordinates = [(row["latitude"], row["longitude"]) for row in rows]
    if len(set(coordinates)) != len(coordinates):
        raise ValueError("ETOPO subset contains duplicate coordinate pairs")

    latitudes = sorted({float(row["latitude"]) for row in rows})
    longitudes = sorted({float(row["longitude"]) for row in rows})
    if len(latitudes) < 2 or len(longitudes) < 2:
        raise ValueError("ETOPO subset must contain multiple rows and columns")

    lat_steps = [b - a for a, b in zip(latitudes, latitudes[1:])]
    lon_steps = [b - a for a, b in zip(longitudes, longitudes[1:])]
    if not all(math.isclose(step, GRID_RESOLUTION_DEG, rel_tol=0.0, abs_tol=1e-7) for step in lat_steps):
        raise ValueError(f"Unexpected latitude spacing: {sorted(set(round(x, 10) for x in lat_steps))}")
    if not all(math.isclose(step, GRID_RESOLUTION_DEG, rel_tol=0.0, abs_tol=1e-7) for step in lon_steps):
        raise ValueError(f"Unexpected longitude spacing: {sorted(set(round(x, 10) for x in lon_steps))}")

    expected_cells = len(latitudes) * len(longitudes)
    if len(rows) != expected_cells:
        raise ValueError(
            f"Incomplete ETOPO rectangle: {len(rows)} rows for "
            f"{len(latitudes)} x {len(longitudes)} coordinates"
        )

    return {
        "rows": len(rows),
        "latitude_count": len(latitudes),
        "longitude_count": len(longitudes),
        "latitude_min": latitudes[0],
        "latitude_max": latitudes[-1],
        "longitude_min": longitudes[0],
        "longitude_max": longitudes[-1],
        "resolution_degrees": GRID_RESOLUTION_DEG,
        "missing_elevation_count": sum(row["etopo_elevation_m"] is None for row in rows),
    }


def main() -> None:
    import requests

    url = build_request_url()
    print(f"Requesting full-resolution ETOPO subset: {url}", flush=True)
    response = requests.get(url, timeout=180)
    response.raise_for_status()

    rows = parse_etopo_csv(response.text)
    grid_info = validate_grid(rows)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    csv_path = OUTPUT_ROOT / "wod_gld_south_florida_etopo_30s.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "latitude", "longitude", "etopo_elevation_m",
                "seafloor_depth_m", "etopo_class",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
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
