#!/usr/bin/env python3
"""Read-only extraction of Southern flounder observations from NOAA DisMAP point layers.

Downloads only target-species observations and same-SampleID context rows.
It does not infer absence, survey effort, occupancy, or geographic masks.
All downloaded data are written to a temporary workflow artifact directory.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "data/species/southern-flounder.json"
OUT = Path(os.environ.get("NOAA_DISMAP_OUT", "noaa-southern-flounder-research"))
BASE = "https://services2.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services"
SERVICES = {
    "Gulf of Mexico": f"{BASE}/GMEX_Sample_Locations_CURRENT/FeatureServer",
    "Southeast Fall": f"{BASE}/SEUS_FAL_Sample_Locations_CURRENT/FeatureServer",
    "Southeast Spring": f"{BASE}/SEUS_SPR_Sample_Locations_CURRENT/FeatureServer",
    "Southeast Summer": f"{BASE}/SEUS_SUM_Sample_Locations_CURRENT/FeatureServer",
}
MATCH_FIELDS = ("Species", "CommonName", "SpeciesCommonName", "CommonNameSpecies")
OUTPUT_FIELDS = (
    "OBJECTID", "DatasetCode", "Region", "Season", "DistributionProjectName",
    "SummaryProduct", "SampleID", "Year", "StdTime", "Species", "WTCPUE",
    "MapValue", "TransformUnit", "CommonName", "SpeciesCommonName",
    "CommonNameSpecies", "CoreSpecies", "Stratum", "StratumArea",
    "Latitude", "Longitude", "Depth",
)
USER_AGENT = "LUPITA-read-only-DisMAP-research/1.0"


def normalize(value: Any) -> str:
    """Normalize a text value for exact taxon-name matching."""
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def target_terms(profile: dict[str, Any]) -> set[str]:
    terms = {normalize(profile.get("scientific_name")), normalize(profile.get("common_name"))}
    terms.update(
        normalize(alias) for alias in profile.get("aliases", [])
        if len(normalize(alias).split()) >= 2
    )
    return {term for term in terms if term}


def is_target_record(attributes: dict[str, Any], terms: set[str]) -> bool:
    """Match the complete scientific/common name, never generic 'flounder' alone."""
    values = {normalize(attributes.get(field)) for field in MATCH_FIELDS}
    values.discard("")
    for term in terms:
        if term in values:
            return True
        # Scientific names may be accompanied by authority strings; common names
        # must remain exact so unrelated flounder species are not swept in.
        if " " in term and any(value.startswith(term + " ") for value in values):
            return True
    return False


def request_json(url: str, params: dict[str, Any], attempts: int = 4) -> dict[str, Any]:
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{url}?{query}",
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if "error" in payload:
                raise RuntimeError(f"ArcGIS error: {payload['error']}")
            return payload
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, RuntimeError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"Request failed after {attempts} attempts: {url}: {last_error}")


def query_all(
    layer_url: str, params: dict[str, Any], page_size: int,
    order_by: str = "OBJECTID ASC",
) -> list[dict[str, Any]]:
    """Fetch a query result with offset pagination and guard against repeated pages."""
    rows: list[dict[str, Any]] = []
    offset = 0
    seen_page_ids: set[tuple[Any, ...]] = set()
    while True:
        page = request_json(
            f"{layer_url}/query",
            {
                **params,
                "resultOffset": offset,
                "resultRecordCount": page_size,
                "orderByFields": order_by,
                "f": "json",
            },
        )
        features = page.get("features", [])
        if not features:
            break
        page_ids = tuple(
            feature.get("attributes", {}).get("OBJECTID")
            if feature.get("attributes", {}).get("OBJECTID") is not None
            else tuple(sorted(feature.get("attributes", {}).items()))
            for feature in features
        )
        if page_ids in seen_page_ids:
            raise RuntimeError(f"ArcGIS repeated a page at resultOffset={offset}")
        seen_page_ids.add(page_ids)
        rows.extend(features)
        offset += len(features)
        if not page.get("exceededTransferLimit", False) and len(features) < page_size:
            break
        if offset > 2_000_000:
            raise RuntimeError("Safety stop: query exceeded two million records")
    return rows


def attrs(features: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [feature.get("attributes", {}) for feature in features]


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    fields = list(OUTPUT_FIELDS)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    years = Counter(str(row.get("Year")) for row in records if row.get("Year") is not None)
    seasons = Counter(str(row.get("Season")) for row in records if row.get("Season"))
    strata = Counter(str(row.get("Stratum")) for row in records if row.get("Stratum"))
    sample_ids = {str(row["SampleID"]) for row in records if row.get("SampleID") not in (None, "")}
    wtcpue = [float(row["WTCPUE"]) for row in records if isinstance(row.get("WTCPUE"), (int, float))]
    return {
        "observation_rows": len(records),
        "unique_sample_ids_with_target_record": len(sample_ids),
        "years": dict(sorted(years.items())),
        "seasons": dict(sorted(seasons.items())),
        "strata": dict(sorted(strata.items())),
        "null_latitude_rows": sum(row.get("Latitude") is None for row in records),
        "null_longitude_rows": sum(row.get("Longitude") is None for row in records),
        "null_depth_rows": sum(row.get("Depth") is None for row in records),
        "null_wtcpue_rows": sum(row.get("WTCPUE") is None for row in records),
        "wtcpue_min": min(wtcpue) if wtcpue else None,
        "wtcpue_max": max(wtcpue) if wtcpue else None,
        "wtcpue_mean": sum(wtcpue) / len(wtcpue) if wtcpue else None,
    }


def main() -> int:
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    terms = target_terms(profile)
    if normalize(profile.get("scientific_name")) != "paralichthys lethostigma":
        raise SystemExit("Unexpected species profile scientific_name; refusing extraction")

    OUT.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "purpose": "Read-only NOAA DisMAP target-species observation extraction.",
        "target": {
            "profile": str(PROFILE_PATH.relative_to(ROOT)),
            "common_name": profile.get("common_name"),
            "scientific_name": profile.get("scientific_name"),
            "exact_match_terms": sorted(terms),
        },
        "sources": {},
        "limitations": [
            "A record represents a target-species observation in this DisMAP point layer.",
            "Same-SampleID context rows are not proof of complete tow effort or valid non-detections.",
            "No catch at an unsampled location cannot be inferred from these records.",
            "No interpolated surface, occupancy polygon, or geographic mask is generated.",
            "No model, species profile, scoring, or production data is modified.",
        ],
    }

    total_target_rows = 0
    for label, service_url in SERVICES.items():
        print(f"Inspecting {label}", flush=True)
        service = request_json(service_url, {"f": "json"})
        layers = service.get("layers", [])
        if not layers:
            raise RuntimeError(f"No layers advertised by {service_url}")
        layer_id = int(layers[0]["id"])
        layer_url = f"{service_url}/{layer_id}"
        metadata = request_json(layer_url, {"f": "json"})
        fields = {field["name"] for field in metadata.get("fields", [])}
        missing = set(MATCH_FIELDS) - fields
        if missing:
            raise RuntimeError(f"{label}: required species fields missing: {sorted(missing)}")
        page_size = min(int(metadata.get("maxRecordCount", 1000)), 10000)

        # Discover the layer's distinct species/name combinations first. This
        # avoids assuming NOAA's Species field uses a particular taxonomy code.
        distinct = query_all(
            layer_url,
            {
                "where": "1=1",
                "outFields": ",".join(MATCH_FIELDS),
                "returnDistinctValues": "true",
                "returnGeometry": "false",
            },
            page_size,
            order_by=",".join(f"{field} ASC" for field in MATCH_FIELDS),
        )
        matched_combinations = [
            row for row in attrs(distinct) if is_target_record(row, terms)
        ]
        if not matched_combinations:
            report["sources"][label] = {
                "service_url": service_url,
                "layer_id": layer_id,
                "layer_name": metadata.get("name"),
                "distinct_name_combinations": len(distinct),
                "matched_name_combinations": [],
                "status": "no exact target name found",
                "observation_summary": summarize([]),
                "sample_context_rows": 0,
            }
            continue

        # Build exact-value predicates from NOAA's own distinct field values.
        clauses: set[str] = set()
        for row in matched_combinations:
            for field in MATCH_FIELDS:
                value = row.get(field)
                if value not in (None, ""):
                    safe = str(value).replace("'", "''")
                    clauses.add(f"{field} = '{safe}'")
        where = " OR ".join(sorted(clauses))
        target_features = query_all(
            layer_url,
            {
                "where": where,
                "outFields": ",".join(OUTPUT_FIELDS),
                "returnGeometry": "false",
            },
            page_size,
        )
        target_records = [
            row for row in attrs(target_features) if is_target_record(row, terms)
        ]
        total_target_rows += len(target_records)

        # Context records share SampleID with a target catch. They expose the
        # other rows NOAA associates with that same sample, but do not establish
        # the complete universe of attempted tows or non-detection effort.
        sample_ids = sorted({
            str(row["SampleID"]) for row in target_records
            if row.get("SampleID") not in (None, "")
        })
        context_records: list[dict[str, Any]] = []
        for start in range(0, len(sample_ids), 40):
            batch = sample_ids[start:start + 40]
            in_values = ",".join("'" + value.replace("'", "''") + "'" for value in batch)
            context_features = query_all(
                layer_url,
                {
                    "where": f"SampleID IN ({in_values})",
                    "outFields": ",".join(OUTPUT_FIELDS),
                    "returnGeometry": "false",
                },
                page_size,
            )
            context_records.extend(attrs(context_features))

        safe_label = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
        write_csv(OUT / f"{safe_label}-southern-flounder-observations.csv", target_records)
        write_csv(OUT / f"{safe_label}-same-sample-context.csv", context_records)

        report["sources"][label] = {
            "service_url": service_url,
            "layer_id": layer_id,
            "layer_name": metadata.get("name"),
            "layer_last_edit_date_ms": metadata.get("editingInfo", {}).get("lastEditDate"),
            "max_record_count": metadata.get("maxRecordCount"),
            "distinct_name_combinations": len(distinct),
            "matched_name_combinations": matched_combinations,
            "where_clause": where,
            "observation_summary": summarize(target_records),
            "sample_context_rows": len(context_records),
            "sample_context_unique_sample_ids": len({
                str(row["SampleID"]) for row in context_records
                if row.get("SampleID") not in (None, "")
            }),
            "outputs": [
                f"{safe_label}-southern-flounder-observations.csv",
                f"{safe_label}-same-sample-context.csv",
            ],
        }
        print(
            f"{label}: {len(target_records)} target rows, "
            f"{len(sample_ids)} target SampleIDs, {len(context_records)} context rows",
            flush=True,
        )

    report["total_target_observation_rows"] = total_target_rows
    report["generated_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (OUT / "extraction_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if total_target_rows == 0:
        print("No exact Southern flounder records found in the four configured layers.", file=sys.stderr)
        return 2
    print(f"Complete: {total_target_rows} target observation rows extracted.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
