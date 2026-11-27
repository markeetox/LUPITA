#!/usr/bin/env python3
"""Read-only acquisition of public Southern flounder evidence sources.

Downloads public NPS Everglades creel CSVs, the FWC/FWRI inshore FIM
positive-catch feature records, and the Florida Museum Ichthyology DwC-A.
Writes raw sources and derived exact-name extracts to a temporary directory.
It never infers absence from missing positive-catch or recreational records.
"""
from __future__ import annotations

import csv
import io
import json
import re
import sys
import time
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

import requests

OUT = Path("south-florida-public-evidence")
TARGET_SCIENTIFIC = "Paralichthys lethostigma"
TARGET_COMMON = "Southern Flounder"
USER_AGENT = "LUPITA-read-only-public-evidence/1.0"
NPS_BASE = "https://irma.nps.gov/DataStore/DownloadFile"
NPS_FILES = {
    "catch.csv": "759623",
    "catch_flags.csv": "759624",
    "fishing_areas.csv": "759622",
    "trailer_count.csv": "759626",
    "metadata.xml": "759625",
}
FWC_SERVICE = (
    "https://gis.myfwc.com/hosting/rest/services/Open_Data/"
    "Inshore_Saltwater_FIM_Stratified_Random_Sampling/MapServer"
)
FLMNH_ARCHIVE = "https://ipt.floridamuseum.ufl.edu/ipt/archive.do?r=ichthyology"
NOAA_REPORT = "https://repository.library.noaa.gov/view/noaa/28764/noaa_28764_DS1.pdf"

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})


def normalize(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def get(url: str, *, params: dict[str, Any] | None = None, timeout: int = 120) -> requests.Response:
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            response = SESSION.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            if not response.content:
                raise RuntimeError(f"Empty response from {response.url}")
            return response
        except (requests.RequestException, RuntimeError) as exc:
            last_error = exc
            if attempt < 3:
                time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"Download failed after retries: {url}: {last_error}")


def save_response(url: str, path: Path, *, params: dict[str, Any] | None = None) -> bytes:
    response = get(url, params=params)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(response.content)
    return response.content


def parse_csv_bytes(data: bytes) -> tuple[list[str], list[dict[str, str]]]:
    text = data.decode("utf-8-sig", errors="replace")
    sample = text[:8192]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t;|")
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    if not reader.fieldnames:
        raise RuntimeError("CSV has no recognizable header row")
    return list(reader.fieldnames), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def acquire_nps(report: dict[str, Any]) -> None:
    raw_dir = OUT / "nps"
    raw_dir.mkdir(parents=True, exist_ok=True)
    nps_summary: dict[str, Any] = {}
    for filename, file_id in NPS_FILES.items():
        url = f"{NPS_BASE}/{file_id}?Reference=2318429"
        payload = save_response(url, raw_dir / filename)
        item: dict[str, Any] = {
            "bytes": len(payload),
            "content_type_note": "NPS endpoint may label CSV files as application/vnd.ms-excel",
        }
        if filename.lower().endswith(".csv"):
            fields, rows = parse_csv_bytes(payload)
            item["row_count"] = len(rows)
            item["columns"] = fields
            target_rows = []
            for row in rows:
                if any(normalize(value) in {
                    normalize(TARGET_SCIENTIFIC), normalize(TARGET_COMMON)
                } for value in row.values()):
                    target_rows.append(row)
            item["exact_name_candidate_rows"] = len(target_rows)
            if target_rows:
                write_csv(raw_dir / filename.replace(".csv", "_southern_flounder_candidates.csv"),
                          fields, target_rows)
        nps_summary[filename] = item
    report["nps_everglades_creel"] = {
        "source": "NPS DataStore Reference 2318429; 1980-01 through 2025-04",
        "files": nps_summary,
        "interpretation": (
            "Fisheries-dependent angler-intercept catch and effort data. "
            "Exact-name candidate rows are leads requiring codebook/QA review. "
            "No absence inference from missing rows."
        ),
    }


def arcgis_json(url: str, params: dict[str, Any]) -> dict[str, Any]:
    response = get(url, params=params)
    payload = response.json()
    if "error" in payload:
        raise RuntimeError(f"ArcGIS error: {payload['error']}")
    return payload


def acquire_fwc(report: dict[str, Any]) -> None:
    fwc_dir = OUT / "fwc_fim"
    fwc_dir.mkdir(parents=True, exist_ok=True)
    service = arcgis_json(FWC_SERVICE, {"f": "json"})
    (fwc_dir / "service_metadata.json").write_text(
        json.dumps(service, indent=2), encoding="utf-8"
    )
    layers = service.get("layers") or []
    if not layers:
        raise RuntimeError("FWC service did not advertise any layers")
    layer_id = int(layers[0]["id"])
    layer_url = f"{FWC_SERVICE}/{layer_id}"
    metadata = arcgis_json(layer_url, {"f": "json"})
    (fwc_dir / "layer_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    fields_available = {field["name"] for field in metadata.get("fields", [])}
    required = {"OBJECTID", "Scientificname", "Commonname", "Reference",
                "Sampling_Date", "Latitude", "Longitude", "Gear", "TotalNum"}
    missing = required - fields_available
    if missing:
        raise RuntimeError(f"FWC layer missing expected fields: {sorted(missing)}")

    out_fields = [
        "OBJECTID", "Reference", "Sampling_Date", "Latitude", "Longitude",
        "Gear", "Scientificname", "Commonname", "TotalNum",
        "avg_size", "min_size", "max_size", "Export_Date", "last_edited_date",
    ]
    out_fields = [field for field in out_fields if field in fields_available]
    where = (
        "UPPER(Scientificname) = 'PARALICHTHYS LETHOSTIGMA' "
        "OR UPPER(Commonname) = 'SOUTHERN FLOUNDER'"
    )
    count_payload = arcgis_json(f"{layer_url}/query", {
        "where": where, "returnCountOnly": "true", "f": "json",
    })
    expected_count = int(count_payload.get("count", 0))
    max_records = min(int(metadata.get("maxRecordCount", 1000)), 2000)
    offset = 0
    features: list[dict[str, Any]] = []
    seen_ids: set[int] = set()
    while True:
        page = arcgis_json(f"{layer_url}/query", {
            "where": where,
            "outFields": ",".join(out_fields),
            "returnGeometry": "true",
            "outSR": "4326",
            "resultOffset": offset,
            "resultRecordCount": max_records,
            "orderByFields": "OBJECTID ASC",
            "f": "json",
        })
        batch = page.get("features", [])
        if not batch:
            break
        new_batch = []
        for feature in batch:
            oid = feature.get("attributes", {}).get("OBJECTID")
            if oid is not None:
                oid = int(oid)
                if oid in seen_ids:
                    continue
                seen_ids.add(oid)
            new_batch.append(feature)
        if not new_batch:
            raise RuntimeError(f"FWC pagination repeated records at offset {offset}")
        features.extend(new_batch)
        offset += len(batch)
        if len(batch) < max_records and not page.get("exceededTransferLimit", False):
            break
        if offset > 100_000:
            raise RuntimeError("FWC extraction safety stop exceeded 100,000 rows")

    rows = []
    for feature in features:
        row = dict(feature.get("attributes", {}))
        geometry = feature.get("geometry") or {}
        row["geometry_x"] = geometry.get("x")
        row["geometry_y"] = geometry.get("y")
        rows.append(row)
    fields = out_fields + ["geometry_x", "geometry_y"]
    write_csv(fwc_dir / "southern_flounder_positive_catches.csv", fields, rows)
    (fwc_dir / "southern_flounder_positive_catches.geojson").write_text(
        json.dumps({
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": feature.get("geometry"),
                    "properties": feature.get("attributes", {}),
                }
                for feature in features
            ],
        }, indent=2), encoding="utf-8"
    )
    report["fwc_inshore_fim_srs"] = {
        "service_url": FWC_SERVICE,
        "layer_id": layer_id,
        "metadata_feature_count": metadata.get("maxRecordCount"),
        "exact_name_query_expected_count": expected_count,
        "retrieved_feature_count": len(features),
        "date_min": min((r.get("Sampling_Date") for r in rows if r.get("Sampling_Date") is not None), default=None),
        "date_max": max((r.get("Sampling_Date") for r in rows if r.get("Sampling_Date") is not None), default=None),
        "gear_counts": dict(Counter(str(r.get("Gear")) for r in rows)),
        "note": (
            "Public GIS export contains positive-catch species records only (CNT>0 in source metadata). "
            "No zero-catch denominator or absence inference is possible from missing target rows."
        ),
    }
    if len(features) != expected_count:
        raise RuntimeError(
            f"FWC target query count mismatch: expected {expected_count}, retrieved {len(features)}"
        )


def acquire_museum(report: dict[str, Any]) -> None:
    museum_dir = OUT / "florida_museum"
    museum_dir.mkdir(parents=True, exist_ok=True)
    archive_path = museum_dir / "uf_ichthyology_dwca.zip"
    payload = save_response(FLMNH_ARCHIVE, archive_path)
    museum_summary: dict[str, Any] = {"archive_bytes": len(payload)}
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = archive.namelist()
        museum_summary["archive_members"] = names
        core_name = next((name for name in names if name.lower().endswith("occurrence.txt")), None)
        if core_name is None:
            raise RuntimeError("Florida Museum DwC-A has no occurrence.txt core file")
        raw = archive.read(core_name)
        text = raw.decode("utf-8-sig", errors="replace")
        reader = csv.DictReader(io.StringIO(text), delimiter="\t")
        fields = list(reader.fieldnames or [])
        if not fields:
            raise RuntimeError("Florida Museum occurrence core has no header")
        target_rows = []
        for row in reader:
            scientific = normalize(row.get("scientificName"))
            verbatim = normalize(row.get("verbatimIdentification"))
            accepted = normalize(row.get("acceptedNameUsage"))
            if any(value in {normalize(TARGET_SCIENTIFIC), normalize(TARGET_COMMON)}
                   for value in (scientific, verbatim, accepted)):
                target_rows.append(row)
        write_csv(museum_dir / "southern_flounder_occurrences.csv", fields, target_rows)
        museum_summary.update({
            "core_file": core_name,
            "core_row_count": sum(1 for _ in io.StringIO(text)) - 1,
            "exact_name_candidate_rows": len(target_rows),
            "candidate_catalog_numbers": sorted({
                row.get("catalogNumber", "") for row in target_rows
                if row.get("catalogNumber")
            }),
        })
    report["florida_museum_ichthyology"] = {
        **museum_summary,
        "license_note": "Resource license shown as CC-BY-NC 4.0; retain attribution and non-commercial restrictions.",
        "interpretation": "Museum occurrences document preserved collection records, not standardized abundance or current occupancy.",
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "run_date_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "target": {"scientific_name": TARGET_SCIENTIFIC, "common_name": TARGET_COMMON},
        "sources": {
            "NOAA Florida Bay monitoring report": NOAA_REPORT,
            "FWC/FWRI Inshore FIM SRS": FWC_SERVICE,
            "NPS Everglades creel": "https://catalog.data.gov/dataset/recreational-fishing-catch-and-effort-in-everglades-national-park-1980-2025-data-package",
            "Florida Museum DwC-A": FLMNH_ARCHIVE,
        },
        "limitations": [
            "No absence inference from missing records in positive-catch-only or fisheries-dependent data.",
            "Museum vouchers are occurrence evidence, not abundance estimates.",
            "No model, species profile, geographic mask, scoring, or production data is modified.",
        ],
    }
    failures = {}
    for name, fn in (
        ("nps_everglades_creel", acquire_nps),
        ("fwc_inshore_fim_srs", acquire_fwc),
        ("florida_museum_ichthyology", acquire_museum),
    ):
        try:
            fn(report)
        except Exception as exc:
            failures[name] = f"{type(exc).__name__}: {exc}"
            print(f"ERROR {name}: {failures[name]}", file=sys.stderr, flush=True)
    report["source_failures"] = failures
    (OUT / "acquisition_summary.json").write_text(
        json.dumps(report, indent=2, default=str), encoding="utf-8"
    )
    readme = """# South Florida public evidence acquisition

This artifact contains read-only copies/extracts of public source data for Southern flounder research.

- FWC/FWRI Inshore FIM GIS: positive-catch species records only; missing target rows are not non-detections.
- NPS Everglades creel: fisheries-dependent angler-intercept catch/effort; exact-name candidates require QA and taxonomy review.
- Florida Museum Ichthyology: voucher occurrences; not abundance or current occupancy.

No species profile, model, scoring, geographic mask, or production source was changed.
See acquisition_summary.json for counts, date ranges, schemas, and source failures.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
