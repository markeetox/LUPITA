#!/usr/bin/env python3
"""Research-only ETOPO join for IOOS USF Sam glider observations.

Uses point-level interpolated glider coordinates and the NOAA NCEI ETOPO 2022
30-arc-second grid. Results are screening estimates, not a validated vertical
datum match and never feed production prediction.
"""
from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import io
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ETOPO_BASE = "https://oceanwatch.pifsc.noaa.gov/erddap/griddap/ETOPO_2022_v1_30s"
GRID_STEP_DEG = 1.0 / 120.0
EARTH_RADIUS_M = 6_371_008.8
DEPTH_BANDS_M = (5, 10, 20, 50)
FLAG_MEANINGS = {1: "PASS", 2: "NOT_EVALUATED", 3: "SUSPECT", 4: "FAIL", 9: "MISSING"}


def normalize_header(value: str) -> str:
    return value.strip().split(" (", 1)[0].strip()


def read_observations(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError("Observation CSV has no header")
        rows = []
        for raw in reader:
            row = {normalize_header(k): (v or "").strip() for k, v in raw.items() if k}
            if all(row.get(k) for k in ("precise_lat", "precise_lon", "depth", "temperature", "precise_time", "profile_id")):
                rows.append(row)
    if not rows:
        raise ValueError("No rows with coordinates, depth, temperature, time and profile_id")
    return rows


def build_etopo_url(rows: list[dict[str, str]], pad_deg: float = 0.02) -> str:
    lats = [float(r["precise_lat"]) for r in rows]
    lons = [float(r["precise_lon"]) % 360.0 for r in rows]
    lat0 = max(-89.995, min(lats) - pad_deg)
    lat1 = min(89.995, max(lats) + pad_deg)
    lon0 = max(0.004, min(lons) - pad_deg)
    lon1 = min(359.996, max(lons) + pad_deg)
    constraint = f"z[({lat0:.6f}):1:({lat1:.6f})][({lon0:.6f}):1:({lon1:.6f})]"
    return ETOPO_BASE + ".csvp?" + urllib.parse.quote(constraint, safe="[]():.")


def fetch_text(url: str, attempts: int = 4) -> str:
    last_error = None
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "LUPITA-research/1.0"})
            with urllib.request.urlopen(request, timeout=120) as response:
                return response.read().decode("utf-8-sig")
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"ETOPO request failed after {attempts} attempts: {last_error}")


def parse_etopo_csvp(text: str) -> list[dict[str, float]]:
    reader = csv.reader(io.StringIO(text))
    try:
        header = next(reader)
    except StopIteration:
        raise ValueError("ETOPO ERDDAP response is empty")
    names = [normalize_header(x) for x in header]
    required = {"latitude", "longitude", "z"}
    if not required.issubset(names):
        raise ValueError(f"ETOPO response missing columns {sorted(required)}; got {names}")
    indexes = {name: names.index(name) for name in required}
    cells = []
    for line_number, values in enumerate(reader, start=2):
        if not values or len(values) < len(names):
            continue
        try:
            cell = {name: float(values[index]) for name, index in indexes.items()}
        except ValueError:
            # Tolerate a units row if the server returns one in addition to unit-bearing headers.
            if line_number == 2:
                continue
            raise ValueError(f"Non-numeric ETOPO row at line {line_number}: {values[:4]}")
        if all(math.isfinite(v) for v in cell.values()):
            cells.append(cell)
    if not cells:
        raise ValueError("ETOPO response contained no numeric grid cells")
    return cells


def nearest(axis: list[float], value: float) -> float:
    pos = bisect.bisect_left(axis, value)
    if pos <= 0:
        return axis[0]
    if pos >= len(axis):
        return axis[-1]
    return min((axis[pos - 1], axis[pos]), key=lambda candidate: abs(candidate - value))


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def make_grid(cells: list[dict[str, float]]) -> tuple[dict[tuple[float, float], float], list[float], list[float]]:
    grid = {}
    lats, lons = set(), set()
    for cell in cells:
        lat, lon, z = cell["latitude"], cell["longitude"], cell["z"]
        key = (lat, lon)
        if key in grid:
            raise ValueError(f"Duplicate ETOPO coordinate {key}")
        grid[key] = z
        lats.add(lat)
        lons.add(lon)
    return grid, sorted(lats), sorted(lons)


def join_rows(rows: list[dict[str, str]], cells: list[dict[str, float]]) -> tuple[list[dict[str, object]], dict[str, object]]:
    grid, lat_axis, lon_axis = make_grid(cells)
    output = []
    separation_values = []
    classes = Counter()
    profile_summaries: dict[str, list[float]] = {}
    near_bottom = {str(band): {"all_rows": 0, "primary_qc_pass_rows": 0, "profiles": set(), "primary_qc_pass_profiles": set()} for band in DEPTH_BANDS_M}

    for row in rows:
        lat, lon = float(row["precise_lat"]), float(row["precise_lon"])
        lon360 = lon % 360.0
        grid_lat, grid_lon = nearest(lat_axis, lat), nearest(lon_axis, lon360)
        z = grid[(grid_lat, grid_lon)]
        offset = haversine_m(lat, lon, grid_lat, ((grid_lon + 180) % 360) - 180)
        if z < -1.0:
            cell_class = "ocean"
            seafloor_depth = -z
            separation = seafloor_depth - float(row["depth"])
            separation_values.append(separation)
            profile_summaries.setdefault(row["profile_id"], []).append(separation)
        elif z > 1.0:
            cell_class, seafloor_depth, separation = "land", None, None
        else:
            cell_class, seafloor_depth, separation = "coastal_ambiguous", None, None
        classes[cell_class] += 1
        try:
            primary_flag = int(float(row.get("qartod_temperature_primary_flag", "")))
        except (TypeError, ValueError):
            primary_flag = None
        item = {
            "profile_id": row["profile_id"],
            "precise_time_utc": row["precise_time"],
            "precise_lat_interpolated_deg": lat,
            "precise_lon_interpolated_deg": lon,
            "depth_m": float(row["depth"]),
            "temperature_c": float(row["temperature"]),
            "temperature_primary_qc": FLAG_MEANINGS.get(primary_flag, "UNKNOWN"),
            "etopo_latitude_deg": grid_lat,
            "etopo_longitude_0_360_deg": grid_lon,
            "etopo_z_m_positive_up": z,
            "etopo_class": cell_class,
            "seafloor_depth_m_from_negative_z": seafloor_depth,
            "bottom_separation_m_screening_only": separation,
            "nearest_grid_center_offset_m": offset,
        }
        output.append(item)
        if separation is not None and separation >= 0:
            for band in DEPTH_BANDS_M:
                if separation <= band:
                    near_bottom[str(band)]["all_rows"] += 1
                    near_bottom[str(band)]["profiles"].add(row["profile_id"])
                    if primary_flag == 1:
                        near_bottom[str(band)]["primary_qc_pass_rows"] += 1
                        near_bottom[str(band)]["primary_qc_pass_profiles"].add(row["profile_id"])

    profile_min_separation = {pid: min(vals) for pid, vals in profile_summaries.items()}
    profile_max_separation = {pid: max(vals) for pid, vals in profile_summaries.items()}
    near_bottom_json = {
        band: {
            "all_rows": item["all_rows"],
            "profiles_represented": len(item["profiles"]),
            "primary_qc_pass_rows": item["primary_qc_pass_rows"],
            "primary_qc_pass_profiles": len(item["primary_qc_pass_profiles"]),
        }
        for band, item in near_bottom.items()
    }
    summary = {
        "observation_rows_joined": len(output),
        "etopo_grid_cells_downloaded": len(cells),
        "etopo_grid_latitude_count": len(lat_axis),
        "etopo_grid_longitude_count": len(lon_axis),
        "etopo_grid_spacing_expected_deg": GRID_STEP_DEG,
        "etopo_cell_class_counts": dict(classes),
        "ocean_rows_with_separation": len(separation_values),
        "negative_separation_rows_preserved": sum(v < 0 for v in separation_values),
        "bottom_separation_m_screening_only": {
            "min": min(separation_values) if separation_values else None,
            "median": sorted(separation_values)[len(separation_values)//2] if separation_values else None,
            "max": max(separation_values) if separation_values else None,
        },
        "nearest_grid_center_offset_m": {
            "min": min(x["nearest_grid_center_offset_m"] for x in output),
            "median": sorted(x["nearest_grid_center_offset_m"] for x in output)[len(output)//2],
            "max": max(x["nearest_grid_center_offset_m"] for x in output),
        },
        "profiles_with_ocean_cells": len(profile_summaries),
        "profile_minimum_bottom_separation_m": {
            "min": min(profile_min_separation.values()) if profile_min_separation else None,
            "median": sorted(profile_min_separation.values())[len(profile_min_separation)//2] if profile_min_separation else None,
            "max": max(profile_min_separation.values()) if profile_min_separation else None,
        },
        "near_bottom_sensitivity_nonnegative_separation_only": near_bottom_json,
        "limits": [
            "precise_lat/precise_lon are interpolated position estimates, not raw direct GPS fixes",
            "ETOPO z is height positive up in EGM2008; glider depth is sea-surface referenced; vertical datum equivalence is not established",
            "negative bottom separations are retained and are not clipped",
            "pressure is intentionally excluded because ERDDAP metadata has an unresolved unit/transformation inconsistency",
            "near-bottom counts are nested observations within profiles, not independent samples",
            "this is bathymetric screening only, not Copernicus accuracy validation",
        ],
    }
    return output, summary



def build_profile_summary(joined: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in joined:
        grouped.setdefault(str(row["profile_id"]), []).append(row)
    result = []
    for profile_id, rows in sorted(grouped.items()):
        ocean = [r for r in rows if r["bottom_separation_m_screening_only"] is not None]
        separations = [float(r["bottom_separation_m_screening_only"]) for r in ocean]
        nonnegative = [v for v in separations if v >= 0]
        profile = {
            "profile_id": profile_id,
            "temperature_observation_rows": len(rows),
            "ocean_cell_rows": len(ocean),
            "negative_separation_rows": sum(v < 0 for v in separations),
            "minimum_signed_separation_m": min(separations) if separations else None,
            "median_signed_separation_m": sorted(separations)[len(separations)//2] if separations else None,
            "maximum_signed_separation_m": max(separations) if separations else None,
            "minimum_nonnegative_separation_m": min(nonnegative) if nonnegative else None,
            "temperature_primary_qc_pass_rows": sum(r["temperature_primary_qc"] == "PASS" for r in rows),
        }
        for band in DEPTH_BANDS_M:
            within = [r for r in ocean if r["bottom_separation_m_screening_only"] is not None
                      and 0 <= float(r["bottom_separation_m_screening_only"]) <= band]
            profile[f"within_{band}m_rows"] = len(within)
            profile[f"within_{band}m_primary_qc_pass_rows"] = sum(
                r["temperature_primary_qc"] == "PASS" for r in within
            )
        result.append(profile)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-csv", required=True)
    parser.add_argument("--output-dir", default="artifacts/ioos-usf-sam-etopo")
    args = parser.parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    input_path = Path(args.input_csv)
    input_sha = hashlib.sha256(input_path.read_bytes()).hexdigest()
    rows = read_observations(input_path)
    url = build_etopo_url(rows)
    etopo_text = fetch_text(url)
    cells = parse_etopo_csvp(etopo_text)
    output, summary = join_rows(rows, cells)

    joined_path = out_dir / "usf-sam-20240216T0000_etopo_join.csv"
    with joined_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)
    etopo_path = out_dir / "etopo_grid.csv"
    etopo_path.write_text(etopo_text, encoding="utf-8")
    profile_output = build_profile_summary(output)
    profile_path = out_dir / "usf-sam-20240216T0000_profile_bottom_separation.csv"
    with profile_path.open("w", encoding="utf-8", newline="") as stream:
        profile_writer = csv.DictWriter(stream, fieldnames=list(profile_output[0]))
        profile_writer.writeheader()
        profile_writer.writerows(profile_output)
    summary.update({
        "profile_summary_rows": len(profile_output),
        "profile_summary_csv": profile_path.name,
        "dataset_id": "usf-sam-20240216T0000",
        "source_observation_csv": input_path.name,
        "source_observation_csv_sha256": input_sha,
        "etopo_source_url": url,
        "etopo_source_dataset": "NOAA NCEI ETOPO_2022_v1_30s via NOAA ERDDAP",
        "etopo_download_sha256": hashlib.sha256(etopo_text.encode("utf-8")).hexdigest(),
        "depth_variable_used": "depth (m), calculated from CTD m_depth",
        "position_variables_used": "precise_lat/precise_lon (interpolated estimates)",
        "pressure_used": False,
    })
    (out_dir / "etopo_join_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
