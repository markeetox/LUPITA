#!/usr/bin/env python3
"""Research-only join of WOD GLD observed levels to NOAA ETOPO 30-arcsecond bathymetry.

The WOD parser is an isolated research dependency pinned in
requirements-research-wod.txt. This script does not feed production prediction.
"""
from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import json
import math
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OCEAN_CLASS = "ocean"
EARTH_RADIUS_M = 6_371_008.8
NEAR_BOTTOM_SENSITIVITY_M = (5, 10, 20, 50)


def load_etopo(path: Path) -> dict[str, Any]:
    cells: dict[tuple[float, float], dict[str, Any]] = {}
    latitudes: set[float] = set()
    longitudes: set[float] = set()
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"latitude", "longitude", "etopo_elevation_m", "seafloor_depth_m", "etopo_class"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"ETOPO CSV must contain columns {sorted(required)}")
        for row in reader:
            lat = float(row["latitude"])
            lon = float(row["longitude"])
            elevation = float(row["etopo_elevation_m"]) if row["etopo_elevation_m"] else None
            depth = float(row["seafloor_depth_m"]) if row["seafloor_depth_m"] else None
            cell = {"latitude": lat, "longitude": lon, "elevation_m": elevation,
                    "depth_m": depth, "class": row["etopo_class"]}
            key = (lat, lon)
            if key in cells:
                raise ValueError(f"Duplicate ETOPO cell {key}")
            cells[key] = cell
            latitudes.add(lat)
            longitudes.add(lon)

    lat_axis = sorted(latitudes)
    lon_axis = sorted(longitudes)
    if len(lat_axis) < 2 or len(lon_axis) < 2:
        raise ValueError("ETOPO grid must contain at least 2 rows and columns")
    lat_step = 1.0 / 120.0
    lon_step = 1.0 / 120.0
    for axis, name in ((lat_axis, "latitude"), (lon_axis, "longitude")):
        for left, right in zip(axis, axis[1:]):
            if not math.isclose(right - left, lat_step if name == "latitude" else lon_step,
                                rel_tol=0.0, abs_tol=1e-7):
                raise ValueError(f"Unexpected {name} grid spacing: {right-left}")
    if len(cells) != len(lat_axis) * len(lon_axis):
        raise ValueError("ETOPO grid is not a complete rectangle")
    return {"cells": cells, "latitudes": lat_axis, "longitudes": lon_axis}


def nearest_axis(axis: list[float], value: float) -> float:
    pos = bisect.bisect_left(axis, value)
    if pos <= 0:
        return axis[0]
    if pos >= len(axis):
        return axis[-1]
    return min((axis[pos - 1], axis[pos]), key=lambda candidate: abs(candidate - value))


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def bathymetry_at(lat: float, lon: float, grid: dict[str, Any]) -> dict[str, Any]:
    cells = grid["cells"]
    lat_axis = grid["latitudes"]
    lon_axis = grid["longitudes"]
    nearest_lat = nearest_axis(lat_axis, lat)
    nearest_lon = nearest_axis(lon_axis, lon)
    nearest = cells[(nearest_lat, nearest_lon)]

    i1 = bisect.bisect_right(lat_axis, lat)
    j1 = bisect.bisect_right(lon_axis, lon)
    bilinear_depth = None
    bilinear_cells: list[str] = []
    if 0 < i1 < len(lat_axis) and 0 < j1 < len(lon_axis):
        y0, y1 = lat_axis[i1 - 1], lat_axis[i1]
        x0, x1 = lon_axis[j1 - 1], lon_axis[j1]
        corners = [
            cells[(y0, x0)], cells[(y0, x1)],
            cells[(y1, x0)], cells[(y1, x1)],
        ]
        bilinear_cells = [item["class"] for item in corners]
        if all(item["class"] == OCEAN_CLASS and item["depth_m"] is not None for item in corners):
            fy = (lat - y0) / (y1 - y0)
            fx = (lon - x0) / (x1 - x0)
            d00, d01, d10, d11 = [item["depth_m"] for item in corners]
            bilinear_depth = (
                (1 - fy) * (1 - fx) * d00
                + (1 - fy) * fx * d01
                + fy * (1 - fx) * d10
                + fy * fx * d11
            )

    return {
        "etopo_latitude": nearest_lat,
        "etopo_longitude": nearest_lon,
        "etopo_class": nearest["class"],
        "seafloor_depth_m": nearest["depth_m"],
        "grid_cell_offset_m": haversine_m(lat, lon, nearest_lat, nearest_lon),
        "bilinear_seafloor_depth_m": bilinear_depth,
        "bilinear_corner_classes": bilinear_cells,
    }


def iter_wod_levels(gld_path: Path):
    # Import only when running this research adapter; production does not depend on wodpy.
    from wodpy.wod import WodProfile

    with gld_path.open("r", encoding="ascii", newline="") as stream:
        file_size = os.fstat(stream.fileno()).st_size
        while stream.tell() < file_size:
            profile = WodProfile(stream)
            header = profile.primary_header
            variables = header["variables"]
            indexes: dict[int, int] = {}
            for index, variable in enumerate(variables):
                code = variable["Variable code"]
                if code in indexes:
                    raise ValueError(f"Duplicate variable code {code} in cast {header['WOD unique cast number']}")
                indexes[code] = index
            if 1 not in indexes:
                raise ValueError(f"Temperature variable code 1 missing in cast {header['WOD unique cast number']}")

            temp_index = indexes[1]
            lat_index, lon_index, jday_index = indexes.get(30), indexes.get(31), indexes.get(32)
            has_track = lat_index is not None and lon_index is not None

            for level_index, level in enumerate(profile.profile_data):
                if level.get("Missing"):
                    continue
                temp = level["variables"][temp_index]
                if temp.get("Missing"):
                    continue

                if has_track:
                    obs_lat = level["variables"][lat_index]["Value"]
                    obs_lon = level["variables"][lon_index]["Value"]
                else:
                    obs_lat = obs_lon = None

                if obs_lat is not None and obs_lon is not None:
                    coordinate_source = "per_observation"
                else:
                    obs_lat = header["Latitude"]
                    obs_lon = header["Longitude"]
                    coordinate_source = "cast_header"

                jday = level["variables"][jday_index]["Value"] if jday_index is not None else None
                yield {
                    "uid": header["WOD unique cast number"],
                    "level_index": level_index,
                    "year": header["Year"],
                    "month": header["Month"],
                    "day": header["Day"],
                    "time_hour": header.get("Time"),
                    "julian_year_day": jday,
                    "latitude": obs_lat,
                    "longitude": obs_lon,
                    "coordinate_source": coordinate_source,
                    "depth_m": level["Depth"],
                    "temperature_c": temp["Value"],
                    "temperature_uncertainty_raw": temp.get("Value_unc"),
                    "temperature_profile_qc": variables[temp_index]["Quality control flag for variable"],
                    "temperature_level_qc": temp.get("Value quality control flag"),
                    "temperature_originator_qc": temp.get("Value originator flag"),
                    "depth_level_qc": level.get("Depth error code"),
                    "depth_originator_qc": level.get("Originator depth error flag"),
                }


def run_join(gld_path: Path, etopo_path: Path, output_path: Path, metadata_path: Path) -> dict[str, Any]:
    grid = load_etopo(etopo_path)
    profile_ids: set[int] = set()
    source_counts: Counter[str] = Counter()
    class_counts: Counter[str] = Counter()
    rows = 0
    negative_nearest = 0
    negative_bilinear = 0
    sensitivity: dict[str, dict[str, int]] = {
        str(limit): {"all_levels": 0, "strict_qc_levels": 0, "all_casts": 0, "strict_qc_casts": 0}
        for limit in NEAR_BOTTOM_SENSITIVITY_M
    }
    all_limit_casts: dict[int, set[int]] = {limit: set() for limit in NEAR_BOTTOM_SENSITIVITY_M}
    strict_limit_casts: dict[int, set[int]] = {limit: set() for limit in NEAR_BOTTOM_SENSITIVITY_M}
    nearest_offsets: list[float] = []
    nearest_separations: list[float] = []
    bilinear_separations: list[float] = []

    fields = [
        "uid", "level_index", "year", "month", "day", "time_hour", "julian_year_day",
        "latitude", "longitude", "coordinate_source", "depth_m", "temperature_c",
        "temperature_uncertainty_raw", "temperature_profile_qc", "temperature_level_qc",
        "temperature_originator_qc", "depth_level_qc", "depth_originator_qc",
        "etopo_latitude", "etopo_longitude", "etopo_class", "seafloor_depth_m",
        "grid_cell_offset_m", "bottom_separation_m", "bilinear_seafloor_depth_m",
        "bilinear_bottom_separation_m",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in iter_wod_levels(gld_path):
            profile_ids.add(int(row["uid"]))
            source_counts[row["coordinate_source"]] += 1
            bathy = bathymetry_at(float(row["latitude"]), float(row["longitude"]), grid)
            row.update(bathy)
            row["bottom_separation_m"] = (
                bathy["seafloor_depth_m"] - row["depth_m"]
                if bathy["etopo_class"] == OCEAN_CLASS and bathy["seafloor_depth_m"] is not None
                else None
            )
            row["bilinear_bottom_separation_m"] = (
                bathy["bilinear_seafloor_depth_m"] - row["depth_m"]
                if bathy["bilinear_seafloor_depth_m"] is not None else None
            )
            row.pop("bilinear_corner_classes", None)
            writer.writerow(row)
            rows += 1
            class_counts[bathy["etopo_class"]] += 1
            nearest_offsets.append(bathy["grid_cell_offset_m"])
            if row["bottom_separation_m"] is not None:
                nearest_separations.append(row["bottom_separation_m"])
                if row["bottom_separation_m"] < 0:
                    negative_nearest += 1
            if row["bilinear_bottom_separation_m"] is not None:
                sep = row["bilinear_bottom_separation_m"]
                bilinear_separations.append(sep)
                if sep < 0:
                    negative_bilinear += 1
                strict = (
                    row["temperature_profile_qc"] == 0
                    and row["temperature_level_qc"] == 0
                    and row["depth_level_qc"] == 0
                )
                if sep >= 0:
                    for limit in NEAR_BOTTOM_SENSITIVITY_M:
                        if sep <= limit:
                            sensitivity[str(limit)]["all_levels"] += 1
                            all_limit_casts[limit].add(int(row["uid"]))
                            if strict:
                                sensitivity[str(limit)]["strict_qc_levels"] += 1
                                strict_limit_casts[limit].add(int(row["uid"]))

    for limit in NEAR_BOTTOM_SENSITIVITY_M:
        sensitivity[str(limit)]["all_casts"] = len(all_limit_casts[limit])
        sensitivity[str(limit)]["strict_qc_casts"] = len(strict_limit_casts[limit])

    def stats(values: list[float]) -> dict[str, float | int | None]:
        if not values:
            return {"count": 0, "min": None, "p01": None, "p05": None, "median": None,
                    "p95": None, "p99": None, "max": None, "mean": None}
        ordered = sorted(values)
        def quantile(q: float) -> float:
            index = (len(ordered) - 1) * q
            lo = math.floor(index)
            hi = math.ceil(index)
            if lo == hi:
                return ordered[lo]
            return ordered[lo] * (hi - index) + ordered[hi] * (index - lo)
        return {
            "count": len(ordered), "min": ordered[0], "p01": quantile(0.01),
            "p05": quantile(0.05), "median": quantile(0.5), "p95": quantile(0.95),
            "p99": quantile(0.99), "max": ordered[-1], "mean": sum(ordered) / len(ordered),
        }

    metadata = {
        "purpose": "research-only GLD observed-level to ETOPO 30-arcsecond join",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "gld_file": gld_path.name,
        "gld_sha256": hashlib.sha256(gld_path.read_bytes()).hexdigest(),
        "etopo_file": etopo_path.name,
        "etopo_sha256": hashlib.sha256(etopo_path.read_bytes()).hexdigest(),
        "parser": "IQuOD/wodpy WodProfile; see pinned research requirements",
        "profile_count": len(profile_ids),
        "level_count": rows,
        "coordinate_source_level_counts": dict(source_counts),
        "etopo_class_level_counts": dict(class_counts),
        "nearest_grid_cell_offset_m": stats(nearest_offsets),
        "nearest_bottom_separation_m": stats(nearest_separations),
        "bilinear_bottom_separation_m": stats(bilinear_separations),
        "negative_nearest_separation_levels": negative_nearest,
        "negative_bilinear_separation_levels": negative_bilinear,
        "nonnegative_bilinear_near_bottom_sensitivity": sensitivity,
        "near_bottom_cutoff_selected": None,
        "caveats": [
            "ETOPO is a global relief model, not a navigation chart.",
            "Nearest-cell and bilinear interpolation are sensitivity views, not independent bathymetry sources.",
            "Negative bottom separation indicates observation depth exceeds the ETOPO seabed estimate; investigate rather than clip or silently discard.",
            "Level counts are not independent sample counts; levels within casts and repeated glider trajectories are autocorrelated.",
            "WOD temperature variable 1 is in degrees Celsius; it has not been established as potential temperature.",
            "No Copernicus model pairing or production prediction change is performed.",
        ],
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gld", type=Path, required=True, help="IQuOD Q-format GLD gzip or decompressed ASCII file")
    parser.add_argument("--etopo", type=Path, required=True, help="ETOPO 30-arcsecond CSV from the export workflow")
    parser.add_argument("--output", type=Path, required=True, help="Joined level CSV output path")
    parser.add_argument("--metadata", type=Path, required=True, help="JSON summary output path")
    args = parser.parse_args()
    metadata = run_join(args.gld, args.etopo, args.output, args.metadata)
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
