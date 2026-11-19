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
    info_rows = list(csv.DictReader(io.StringIO(info_bytes.decode("utf-8-sig"))))
    available = sorted({
        r.get("variableName", "").strip()
        for r in info_rows
        if r.get("rowName", "").strip().lower() == "variable" and r.get("variableName", "").strip()
    })
    missing = [v for v in CORE if v not in available]
    if missing:
        raise RuntimeError(f"Dataset missing required variables: {missing}; available={available}")
    selected = CORE + [v for v in available if v.startswith(QC_PREFIXES)]
    # Keep deterministic order and avoid duplicates.
    selected = list(dict.fromkeys(selected))
    query = ",".join(selected)
    data_url = f"{BASE}/tabledap/{DATASET}.csvp?{urllib.parse.quote(query, safe=',_')}"
    data_bytes = fetch(data_url)
    raw_path = out / f"{DATASET}_observations.csv"
    raw_path.write_bytes(data_bytes)

    reader = csv.DictReader(io.StringIO(data_bytes.decode("utf-8-sig")))
    rows = list(reader)
    if not reader.fieldnames or "temperature" not in reader.fieldnames:
        raise RuntimeError("ERDDAP CSV response did not contain the expected temperature header")

    qc_counts = {}
    for variable in selected:
        if variable.startswith(QC_PREFIXES):
            counts = Counter((r.get(variable, "") or "").strip() for r in rows)
            qc_counts[variable] = {
                FLAG_MEANINGS.get(k, "UNKNOWN"): v for k, v in sorted(counts.items())
            }

    def present(row, key):
        value = (row.get(key) or "").strip()
        return value not in ("", "NaN", "nan", "null", "None")

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
