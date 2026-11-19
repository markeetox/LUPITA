#!/usr/bin/env python3
"""Compare a wodpy-based GLD join with the 2026-11-19 preliminary join."""
from __future__ import annotations
import argparse, csv, gzip, json
from pathlib import Path

KEYS = ("uid", "level_index")
FLOAT_FIELDS = {
    "time_hour", "julian_year_day", "latitude", "longitude", "depth_m", "temperature_c",
    "temperature_uncertainty_raw", "etopo_latitude", "etopo_longitude", "seafloor_depth_m",
    "grid_cell_offset_m", "bottom_separation_m", "bilinear_seafloor_depth_m",
    "bilinear_bottom_separation_m",
}
COMPARE_FIELDS = (
    "year", "month", "day", "time_hour", "julian_year_day", "latitude", "longitude",
    "coordinate_source", "depth_m", "temperature_c", "temperature_uncertainty_raw",
    "temperature_profile_qc", "temperature_level_qc", "temperature_originator_qc",
    "depth_level_qc", "depth_originator_qc", "etopo_latitude", "etopo_longitude",
    "etopo_class", "seafloor_depth_m", "grid_cell_offset_m", "bottom_separation_m",
    "bilinear_seafloor_depth_m", "bilinear_bottom_separation_m",
)

def open_text(path: Path):
    return gzip.open(path, "rt", encoding="utf-8", newline="") if path.suffix == ".gz" else path.open("r", encoding="utf-8", newline="")

def load(path: Path):
    rows, duplicates = {}, []
    with open_text(path) as f:
        for row in csv.DictReader(f):
            key = (row["uid"], row["level_index"])
            if key in rows: duplicates.append(key)
            rows[key] = row
    return rows, duplicates

def as_float(value):
    return None if value is None or value == "" else float(value)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--reference", type=Path, required=True)
    p.add_argument("--actual", type=Path, required=True)
    p.add_argument("--json", type=Path, required=True)
    p.add_argument("--tolerance", type=float, default=1e-6)
    a = p.parse_args()
    ref, ref_dupes = load(a.reference)
    act, act_dupes = load(a.actual)
    rk, ak = set(ref), set(act)
    common = rk & ak
    field_report = {}
    for field in COMPARE_FIELDS:
        mismatches, max_abs, examples = 0, 0.0, []
        for key in common:
            x, y = ref[key].get(field, ""), act[key].get(field, "")
            if field in FLOAT_FIELDS:
                xf, yf = as_float(x), as_float(y)
                if xf is None or yf is None:
                    different, delta = xf != yf, None
                else:
                    delta = abs(xf-yf)
                    max_abs = max(max_abs, delta)
                    different = delta > a.tolerance
            else:
                different, delta = (x or "") != (y or ""), None
            if different:
                mismatches += 1
                if len(examples) < 5:
                    examples.append({"key": list(key), "reference": x, "actual": y, "abs_difference": delta})
        field_report[field] = {"mismatches": mismatches, "max_absolute_difference": max_abs if field in FLOAT_FIELDS else None, "examples": examples}
    report = {
        "reference_rows": len(ref), "actual_rows": len(act), "common_rows": len(common),
        "reference_unique_casts": len({k[0] for k in rk}), "actual_unique_casts": len({k[0] for k in ak}),
        "missing_from_actual": len(rk-ak), "extra_in_actual": len(ak-rk),
        "reference_duplicate_keys": len(ref_dupes), "actual_duplicate_keys": len(act_dupes),
        "absolute_numeric_tolerance": a.tolerance, "field_comparisons": field_report,
    }
    report["exact_key_and_field_match"] = (
        not (rk-ak) and not (ak-rk) and not ref_dupes and not act_dupes
        and all(v["mismatches"] == 0 for v in field_report.values())
    )
    a.json.parent.mkdir(parents=True, exist_ok=True)
    a.json.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["missing_from_actual"] or report["extra_in_actual"] or ref_dupes or act_dupes: raise SystemExit(2)
    if any(v["mismatches"] for v in field_report.values()): raise SystemExit(1)

if __name__ == "__main__": main()
