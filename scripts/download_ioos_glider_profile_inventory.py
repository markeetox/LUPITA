#!/usr/bin/env python3
"""Download and inventory one IOOS Glider DAC ERDDAP trajectory-profile dataset.

Research-only: preserves source rows and QC flags. It does not select a near-bottom
cutoff, perform bathymetry joins, or claim Copernicus validation.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

BASE = "https://gliders.ioos.us/erddap"
DATASET = "usf-sam-20240216T0000"
CORE = [
    "trajectory", "wmo_id", "profile_id", "time", "latitude", "longitude",
    "precise_time", "precise_lat", "precise_lon", "depth", "pressure", "temperature",
]
QC_PREFIXES = ("qartod_temperature_", "qartod_pressure_", "qartod_depth_", "qartod_location_")
FLAG_MEANINGS = {
    "1": "PASS", "2": "NOT_EVALUATED", "3": "SUSPECT",
    "4": "FAIL", "9": "MISSING", "-128": "FILL_OR_UNSET",
}


def _header_key(value: str) -> str:
    return "".join(ch.lower() for ch in value.strip().lstrip("\ufeff") if ch.isalnum())


def parse_info_variables(info_text: str) -> tuple[list[str], list[str]]:
    """Read standard ERDDAP info/index.csv variable rows."""
    reader = csv.DictReader(io.StringIO(info_text))
    if not reader.fieldnames:
        raise ValueError("ERDDAP info CSV is empty or has no header row")
    columns = {_header_key(name): name for name in reader.fieldnames}
    row_type_col = columns.get("rowtype") or columns.get("rowname")
    variable_col = columns.get("variablename") or columns.get("variable")
    if not row_type_col or not variable_col:
        raise ValueError(
            "Unrecognized ERDDAP info CSV header; "
            f"expected Row Type and Variable Name, got {reader.fieldnames}"
        )
    variables = {
        (row.get(variable_col) or "").strip()
        for row in reader
        if (row.get(row_type_col) or "").strip().lower() == "variable"
        and (row.get(variable_col) or "").strip()
    }
    return sorted(variables), list(reader.fieldnames)


def normalize_csvp_rows(data_text: str) -> tuple[list[str], list[dict[str, str]]]:
    """Normalize ERDDAP .csvp headers, whose first row is 'name (units)'."""
    reader = csv.DictReader(io.StringIO(data_text))
    if not reader.fieldnames:
        raise ValueError("ERDDAP CSVp response is empty or has no header row")
    canonical = []
    rename = {}
    for header in reader.fieldnames:
        name = header.strip().split(" (", 1)[0].strip()
        canonical.append(name)
        rename[header] = name
    rows = []
    for raw in reader:
        rows.append({rename[k]: (v or "") for k, v in raw.items() if k in rename})
    return canonical, rows


def fetch(url: str, attempts: int = 4) -> bytes:
    last = None
    for n in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "LUPITA-research/1.0"})
            with urllib.request.urlopen(req, timeout=90) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            last = exc
            if n + 1 < attempts:
                time.sleep(3 * (n + 1))
    raise RuntimeError(f"ERDDAP request failed after {attempts} attempts: {url}: {last}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default="artifacts/ioos-usf-sam")
    args = ap.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    info_url = f"{BASE}/info/{DATASET}/index.csv"
    info_bytes = fetch(info_url)
    (out / "dataset_info.csv").write_bytes(info_bytes)
    available, info_headers = parse_info_variables(info_bytes.decode("utf-8-sig"))
    if not available:
        raise RuntimeError(
            "ERDDAP info CSV contained no variable rows; "
            f"headers={info_headers}; saved raw response to {out / 'dataset_info.csv'}"
        )
    missing = [v for v in CORE if v not in available]
    if missing:
        raise RuntimeError(
            f"Dataset missing required variables: {missing}; "
            f"available={available}; info_headers={info_headers}"
        )
    selected = CORE + [v for v in available if v.startswith(QC_PREFIXES)]
    selected = list(dict.fromkeys(selected))
    query = ",".join(selected)
    data_url = f"{BASE}/tabledap/{DATASET}.csvp?{urllib.parse.quote(query, safe=',_')}"
    data_bytes = fetch(data_url)
    raw_path = out / f"{DATASET}_observations.csv"
    raw_path.write_bytes(data_bytes)

    data_text = data_bytes.decode("utf-8-sig")
    fieldnames, rows = normalize_csvp_rows(data_text)
    if "temperature" not in fieldnames:
        preview = "\\n".join(data_text.splitlines()[:4])
        raise RuntimeError(
            "ERDDAP CSVp response did not contain a temperature column after "
            f"stripping unit annotations; headers={fieldnames}; response_preview={preview!r}"
        )

    qc_counts = {}
    for variable in selected:
        if variable.startswith(QC_PREFIXES):
            counts = Counter((r.get(variable, "") or "").strip() for r in rows)
            qc_counts[variable] = {
                FLAG_MEANINGS.get(k, "UNKNOWN"): v for k, v in sorted(counts.items())
            }

    def present(row, key):
        value = (row.get(key) or "").strip()
        return value not in ("", "NaN", "nan", "null", "None", "-9999", "-999")

    profile_ids = {r.get("profile_id", "").strip() for r in rows if present(r, "profile_id")}
    summary = {
        "dataset_id": DATASET,
        "dataset_info_url": info_url,
        "observations_url": data_url,
        "downloaded_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "row_count": len(rows),
        "unique_profile_id_count": len(profile_ids),
        "unique_wmo_ids": sorted({r.get("wmo_id", "").strip() for r in rows if present(r, "wmo_id")}),
        "variables_downloaded": selected,
        "response_headers": fieldnames,
        "qc_flag_counts": qc_counts,
        "nonmissing_counts": {
            k: sum(present(r, k) for r in rows)
            for k in ("profile_id", "precise_time", "precise_lat", "precise_lon",
                      "depth", "pressure", "temperature", "qartod_temperature_primary_flag")
            if k in selected
        },
        "temperature_flag_interpretation": FLAG_MEANINGS,
        "important_limits": [
            "ERDDAP dataset rows are not automatically independent profiles or casts; rows are observations.",
            "Profile-level time/latitude/longitude are calculated/interpolated.",
            "precise_time/precise_lat/precise_lon are also documented as calculated/interpolated point values.",
            "Depth is calculated from the CTD depth sensor; pressure is measured and represented in bar.",
            "QC flag counts are descriptive; NOT_EVALUATED is not PASS.",
            "No near-bottom threshold, ETOPO join, or Copernicus pairing is performed by this inventory.",
        ],
    }
    (out / "inventory_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    if not rows:
        raise RuntimeError("Dataset query returned zero observation rows")


if __name__ == "__main__":
    main()
