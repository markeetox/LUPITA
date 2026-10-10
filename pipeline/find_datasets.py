"""Search NOAA CoastWatch ERDDAP for datasets and show how recent each one is.
Run:  python -m pipeline.find_datasets "viirs chlorophyll"
      python -m pipeline.find_datasets "bathymetry" --limit 20"""
from __future__ import annotations

import csv
import io
import sys

import requests

from pipeline.sources import ndbc

BASE = "https://coastwatch.pfeg.noaa.gov/erddap"


def parse_search(csv_text: str) -> list[dict]:
    """Dataset ID and title for every result row."""
    rows = []
    for row in csv.DictReader(io.StringIO(csv_text)):
        did = (row.get("Dataset ID") or "").strip()
        if did and did != "allDatasets":
            rows.append({"id": did, "title": (row.get("Title") or "").strip()})
    return rows


def parse_coverage(info_csv: str) -> dict:
    """time_coverage_start / time_coverage_end from an ERDDAP /info/<id>/index.csv response."""
    out = {"start": None, "end": None}
    for row in csv.DictReader(io.StringIO(info_csv)):
        if row.get("Row Type") == "attribute" and row.get("Variable Name") == "NC_GLOBAL":
            if row.get("Attribute Name") == "time_coverage_end":
                out["end"] = row.get("Value")
            elif row.get("Attribute Name") == "time_coverage_start":
                out["start"] = row.get("Value")
    return out


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return
    limit = 40
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
        args = [a for a in args if a != str(limit)]
    headers = {"User-Agent": ndbc.USER_AGENT}
    resp = requests.get(f"{BASE}/search/index.csv", headers=headers, timeout=60,
                        params={"page": 1, "itemsPerPage": limit, "searchFor": args[0]})
    resp.raise_for_status()
    found = []
    for d in parse_search(resp.text):
        try:
            info = requests.get(f"{BASE}/info/{d['id']}/index.csv", headers=headers, timeout=30)
            info.raise_for_status()
            cov = parse_coverage(info.text)
        except Exception:
            cov = {"start": None, "end": None}
        found.append((cov["end"] or "", d["id"], cov["start"] or "?", d["title"]))
    for end, did, start, title in sorted(found, reverse=True):
        print(f"{did:32} ends {end or '?':22} starts {start[:10]:10}  {title[:70]}")


if __name__ == "__main__":
    main()
