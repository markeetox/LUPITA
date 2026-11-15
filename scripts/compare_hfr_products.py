#!/usr/bin/env python3
"""Read-only, same-time comparison of NOAA CoastWatch HF Radar products.

Requests native grids for a common timestamp and geographic window. It does not
regrid, interpolate, modify LUPITA source configuration, or publish production data.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import statistics
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

BASES = (
    "https://coastwatch.pfeg.noaa.gov/erddap",
    "https://upwell.pfeg.noaa.gov/erddap",
)
REGION = {"lat": (24.0, 28.5), "lon": (-83.5, -78.0)}
VARIABLES = ("water_u", "water_v", "hdop", "number_of_sites", "number_of_radials")
FILL_VALUES = (-327.67, -9999.0)
PRODUCTS = (
    {"id": "1km", "dataset": "ucsdHfrE1", "spacing_km": 1.0, "representative_depth_m": 0.5},
    {"id": "2km", "dataset": "ucsdHfrE2", "spacing_km": 2.0, "representative_depth_m": 1.0},
    {"id": "6km", "dataset": "ucsdHfrE6", "spacing_km": 6.0, "representative_depth_m": 2.4},
)
# Exploratory reporting windows only, not official NOAA coverage polygons.
SUBREGIONS = {
    "Florida Keys": {"lat": (24.4, 25.4), "lon": (-82.0, -80.1)},
    "Biscayne Bay": {"lat": (25.3, 26.2), "lon": (-80.7, -79.9)},
    "Offshore grounds": {"lat": (24.5, 28.5), "lon": (-80.5, -78.0)},
}


@dataclass
class Grid:
    product: dict[str, Any]
    requested_time: str
    observed_times: list[str]
    latitudes: list[float]
    longitudes: list[float]
    values: dict[str, list[list[float]]]
    returned_pairs: int
    source_url: str


def _number(value: str | None) -> float:
    if value is None or not value.strip():
        return math.nan
    try:
        number = float(value)
    except ValueError:
        return math.nan
    if not math.isfinite(number) or number in FILL_VALUES:
        return math.nan
    return number


def build_url(base: str, dataset: str, timestamp: str, region: dict = REGION) -> str:
    """Build one ERDDAP CSV request for paired vectors and quality fields."""
    slices = (
        f"[({timestamp})]"
        f"[({region['lat'][0]}):1:({region['lat'][1]})]"
        f"[({region['lon'][0]}):1:({region['lon'][1]})]"
    )
    variables = ",".join(f"{name}{slices}" for name in VARIABLES)
    return f"{base}/griddap/{dataset}.csv?{quote(variables, safe='[],():.-')}"


def parse_csv(text: str, product: dict, requested_time: str, source_url: str) -> Grid:
    reader = csv.reader(io.StringIO(text))
    try:
        header = next(reader)
        next(reader)  # ERDDAP units row
    except StopIteration as exc:
        raise ValueError("ERDDAP response did not contain a header and units row") from exc
    indexes = {name.strip(): i for i, name in enumerate(header)}
    required = ("time", "latitude", "longitude", *VARIABLES)
    missing = [name for name in required if name not in indexes]
    if missing:
        raise ValueError(f"ERDDAP response is missing columns: {', '.join(missing)}")
    rows: dict[tuple[float, float], dict[str, float]] = {}
    observed_times: set[str] = set()
    latitudes: set[float] = set()
    longitudes: set[float] = set()
    for row in reader:
        if not row:
            continue
        try:
            timestamp = row[indexes["time"]].strip()
            lat = float(row[indexes["latitude"]])
            lon = float(row[indexes["longitude"]])
        except (ValueError, IndexError) as exc:
            raise ValueError(f"Malformed coordinate row: {row!r}") from exc
        observed_times.add(timestamp)
        latitudes.add(lat)
        longitudes.add(lon)
        rows[(lat, lon)] = {name: _number(row[indexes[name]]) for name in VARIABLES}
    if not rows:
        raise ValueError("ERDDAP returned no grid cells for this timestamp and region")
    if observed_times != {requested_time}:
        raise ValueError(
            f"Requested exact timestamp {requested_time}, but ERDDAP returned "
            f"{sorted(observed_times)}. No nearest-time substitution is allowed."
        )
    lats, lons = sorted(latitudes), sorted(longitudes)
    grids = {name: [[math.nan for _ in lons] for _ in lats] for name in VARIABLES}
    lat_index, lon_index = {v: i for i, v in enumerate(lats)}, {v: i for i, v in enumerate(lons)}
    for (lat, lon), values in rows.items():
        for name, value in values.items():
            grids[name][lat_index[lat]][lon_index[lon]] = value
    return Grid(product, requested_time, sorted(observed_times), lats, lons, grids, len(rows), source_url)


def _finite(value: float) -> bool:
    return math.isfinite(value)


def _median(values: list[float]) -> float | None:
    clean = [v for v in values if _finite(v)]
    return round(statistics.median(clean), 4) if clean else None


def summarize(grid: Grid) -> dict[str, Any]:
    lats, lons, data = grid.latitudes, grid.longitudes, grid.values
    total = len(lats) * len(lons)
    valid = []
    for i, lat in enumerate(lats):
        for j, lon in enumerate(lons):
            if _finite(data["water_u"][i][j]) and _finite(data["water_v"][i][j]):
                valid.append((lat, lon, i, j))
    valid_count = len(valid)

    def regional_stats(bounds: dict) -> dict[str, Any]:
        lat_lo, lat_hi = bounds["lat"]
        lon_lo, lon_hi = bounds["lon"]
        candidate = [(i, j) for i, lat in enumerate(lats) if lat_lo <= lat <= lat_hi
                     for j, lon in enumerate(lons) if lon_lo <= lon <= lon_hi]
        available = sum(
            _finite(data["water_u"][i][j]) and _finite(data["water_v"][i][j])
            for i, j in candidate
        )
        return {
            "grid_cells": len(candidate),
            "valid_vector_cells": int(available),
            "valid_vector_fraction": round(available / len(candidate), 6) if candidate else None,
        }

    # Clamp tiny coordinate rounding excursions to the requested bounds before
    # binning. Use one fixed set of half-degree bins for every product so a
    # product's native grid edge cannot change the denominator.
    lat_min, lat_max = REGION["lat"]
    lon_min, lon_max = REGION["lon"]
    occupied_tiles = {
        (math.floor(min(max(lat, lat_min), lat_max) * 2) / 2,
         math.floor(min(max(lon, lon_min), lon_max) * 2) / 2)
        for lat, lon, _, _ in valid
    }
    lat_tile_starts = range(math.floor(lat_min * 2), math.ceil(lat_max * 2))
    lon_tile_starts = range(math.floor(lon_min * 2), math.ceil(lon_max * 2))
    possible_tiles = {(lat_i / 2, lon_i / 2) for lat_i in lat_tile_starts for lon_i in lon_tile_starts}
    return {
        "product": grid.product,
        "dataset": grid.product["dataset"],
        "requested_time": grid.requested_time,
        "observed_times": grid.observed_times,
        "source_url": grid.source_url,
        "grid": {
            "latitude_count": len(lats),
            "longitude_count": len(lons),
            "nominal_grid_cells": total,
            "returned_coordinate_pairs": grid.returned_pairs,
            "valid_vector_cells": valid_count,
            "valid_vector_fraction": round(valid_count / total, 6) if total else None,
            "valid_vector_percent": round(100 * valid_count / total, 3) if total else None,
        },
        "quality": {
            "hdop_median_valid_vectors": _median([data["hdop"][i][j] for _, _, i, j in valid]),
            "number_of_sites_median_valid_vectors": _median([data["number_of_sites"][i][j] for _, _, i, j in valid]),
            "number_of_radials_median_valid_vectors": _median([data["number_of_radials"][i][j] for _, _, i, j in valid]),
            "hdop_available_fraction": round(sum(_finite(data["hdop"][i][j]) for _, _, i, j in valid) / valid_count, 6) if valid_count else None,
            "site_count_available_fraction": round(sum(_finite(data["number_of_sites"][i][j]) for _, _, i, j in valid) / valid_count, 6) if valid_count else None,
            "radial_count_available_fraction": round(sum(_finite(data["number_of_radials"][i][j]) for _, _, i, j in valid) / valid_count, 6) if valid_count else None,
        },
        "subregions": {name: regional_stats(bounds) for name, bounds in SUBREGIONS.items()},
        "spatial_distribution": {
            "occupied_half_degree_tiles": len(occupied_tiles),
            "possible_half_degree_tiles": len(possible_tiles),
            "occupied_tile_fraction": round(len(occupied_tiles) / len(possible_tiles), 6) if possible_tiles else None,
            "tile_size_degrees": 0.5,
            "denominator_scope": "fixed requested region, shared by all products",
        },
        "native_grid": {
            "latitude_min": min(lats), "latitude_max": max(lats),
            "longitude_min": min(lons), "longitude_max": max(lons),
            "median_latitude_step_degrees": _median([b-a for a, b in zip(lats, lats[1:])]),
            "median_longitude_step_degrees": _median([b-a for a, b in zip(lons, lons[1:])]),
        },
    }


def fetch_product(session: requests.Session, product: dict, timestamp: str, timeout: int) -> Grid:
    failures = []
    for base in BASES:
        url = build_url(base, product["dataset"], timestamp)
        try:
            response = session.get(url, timeout=timeout, headers={"User-Agent": "LUPITA-HFR-compare/1.0"})
            response.raise_for_status()
            return parse_csv(response.text, product, timestamp, url)
        except (requests.RequestException, ValueError) as exc:
            failures.append(f"{base}: {exc}")
    raise RuntimeError(f"{product['id']} ({product['dataset']}) failed on all ERDDAP hosts: " + " | ".join(failures))


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NOAA HF Radar same-time South Florida comparison", "",
        f"- Requested timestamp: \`{report['requested_time']}\`",
        f"- Region: \`{REGION['lat'][0]}–{REGION['lat'][1]}°N\`, \`{abs(REGION['lon'][1])}–{abs(REGION['lon'][0])}°W\`",
        "- Method: native-grid paired \`water_u\` + \`water_v\` validity; no interpolation or regridding.",
        "- Quality fields: \`hdop\`, \`number_of_sites\`, \`number_of_radials\`; diagnostics only, no hard rejection thresholds.", "",
        "## Product comparison", "",
        "| Product | Nominal spacing | Representative depth | Grid cells | Returned pairs | Valid vectors | Coverage | Median HDOP | Median sites | Median radials |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in report["products"]:
        g, q, p = item["grid"], item["quality"], item["product"]
        pct = f"{g['valid_vector_percent']:.3f}%" if g["valid_vector_percent"] is not None else "n/a"
        lines.append(
            f"| {p['id']} | {p['spacing_km']:g} km | {p['representative_depth_m']:g} m | "
            f"{g['nominal_grid_cells']} | {g['returned_coordinate_pairs']} | {g['valid_vector_cells']} | {pct} | "
            f"{q['hdop_median_valid_vectors'] if q['hdop_median_valid_vectors'] is not None else 'n/a'} | "
            f"{q['number_of_sites_median_valid_vectors'] if q['number_of_sites_median_valid_vectors'] is not None else 'n/a'} | "
            f"{q['number_of_radials_median_valid_vectors'] if q['number_of_radials_median_valid_vectors'] is not None else 'n/a'} |"
        )
    lines += ["", "## Named diagnostic subregions", "",
        "These are approximate reporting boxes for comparison, not official NOAA coverage boundaries.", "",
        "| Product | Subregion | Grid cells | Valid vectors | Coverage |",
        "|---|---|---:|---:|---:|"]
    for item in report["products"]:
        for name, stats in item["subregions"].items():
            pct = f"{100*stats['valid_vector_fraction']:.3f}%" if stats["valid_vector_fraction"] is not None else "n/a"
            lines.append(f"| {item['product']['id']} | {name} | {stats['grid_cells']} | {stats['valid_vector_cells']} | {pct} |")
    lines += ["", "## Interpretation limits", "",
        "- Products are compared at the same requested timestamp and geographic bounds, but each retains its native grid. Coverage percentages use each product's own native grid-cell denominator.",
        "- Nominal resolution and representative depth differ. These products are not interchangeable measurements of the same vertical layer.",
        "- A valid paired vector is not automatically a high-quality vector. Review HDOP and contributing site/radial diagnostics before interpreting coverage.",
        "- A grid cell's presence does not prove continuous coverage between cells. Half-degree occupied-tile counts use a fixed requested-region denominator shared by all products; they expose broad clustering but are not a continuous-area estimate.",
        "- Missing or unavailable products are reported as failures; the script never silently substitutes a nearby timestamp.", "", "## Per-product detail", ""]
    for item in report["products"]:
        lines += [f"### {item['product']['id']} (\`{item['dataset']}\`)", "",
            f"- Source: \`{item['source_url']}\`", f"- Returned time: \`{', '.join(item['observed_times'])}\`",
            f"- Spatial tiles occupied: {item['spatial_distribution']['occupied_half_degree_tiles']} / {item['spatial_distribution']['possible_half_degree_tiles']} (shared fixed region)", ""]
    if report.get("failures"):
        lines += ["## Retrieval failures", ""] + [f"- {failure}" for failure in report["failures"]] + [""]
    return "\n".join(lines)


def compare(timestamp: str, timeout: int = 120) -> dict[str, Any]:
    parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timestamp must include a timezone, preferably Z (UTC)")
    timestamp = parsed.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    report: dict[str, Any] = {
        "requested_time": timestamp,
        "region": {"lat": list(REGION["lat"]), "lon": list(REGION["lon"])},
        "method": "native_grid_paired_vector_validity",
        "products": [],
        "failures": [],
    }
    with requests.Session() as session:
        for product in PRODUCTS:
            try:
                report["products"].append(summarize(fetch_product(session, product, timestamp, timeout)))
            except Exception as exc:  # keep successful products if one endpoint is unavailable
                report["failures"].append(f"{product['id']} ({product['dataset']}): {exc}")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--time", default="2026-11-13T04:00:00Z", help="Exact common UTC timestamp")
    parser.add_argument("--timeout", type=int, default=120, help="HTTP timeout in seconds per request")
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/hfr-comparison"), help="Directory for JSON and Markdown reports")
    args = parser.parse_args(argv)
    try:
        report = compare(args.time, args.timeout)
    except ValueError as exc:
        parser.error(str(exc))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = report["requested_time"].replace(":", "").replace("-", "")
    json_path = args.output_dir / f"hfr-comparison-{stamp}.json"
    md_path = args.output_dir / f"hfr-comparison-{stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(report) + "\n", encoding="utf-8")
    print(render_markdown(report))
    print(f"\nWrote: {json_path}\nWrote: {md_path}")
    return 0 if len(report["products"]) == len(PRODUCTS) else 1


if __name__ == "__main__":
    sys.exit(main())
