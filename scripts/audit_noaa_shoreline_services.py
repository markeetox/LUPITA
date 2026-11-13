"""Research-only inventory of NOAA NGS shoreline web services.

This first pass discovers published WFS/WMS layers and records authoritative
project metadata. It does not infer shoreline geometry or alter production data.
"""
from __future__ import annotations

import argparse
import json
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

WFS_ENDPOINTS = [
    "https://geodesy.noaa.gov/GeoServer/NSDE/ows",
    "https://geodesy.noaa.gov/GeoServer/NSDE/wfs",
    "https://www.ngs.noaa.gov/GeoServer/NSDE/ows",
    "https://www.ngs.noaa.gov/GeoServer/NSDE/wfs",
    "https://geodesy.noaa.gov/geoserver/NSDE/ows",
]
WMS_ENDPOINTS = [
    "https://geodesy.noaa.gov/GeoServer/NSDE/ows",
    "https://geodesy.noaa.gov/GeoServer/NSDE/wms",
    "https://www.ngs.noaa.gov/GeoServer/NSDE/ows",
    "https://www.ngs.noaa.gov/GeoServer/NSDE/wms",
    "https://geodesy.noaa.gov/geoserver/NSDE/ows",
]
TIMEOUT = (15, 90)
PROJECTS = [
    {
        "project_id": "FL1808C-TB-N",
        "inport_id": 73241,
        "name": "Biscayne Bay, Rickenbacker Island to Snapper Creek Canal",
        "imagery_or_lidar_dates": "2018-07-26 to 2019-04-13",
        "reported_mhw_accuracy_95pct_m": 2.3,
        "reported_mllw_accuracy_95pct_m": 3.0,
        "inport_url": "https://www.fisheries.noaa.gov/inport/item/73241",
        "completion_report": "https://www.ngs.noaa.gov/desc_reports/FL1808C-TB-N.PDF",
        "geographic_extent_wgs84": [-80.3095, 25.63448867, -80.16894, 25.77293],
        "status": "project_metadata_verified_vectors_not_yet_retrieved",
    },
    {
        "project_id": "FL1808A-TB-N",
        "inport_id": 74866,
        "name": "Biscayne Bay, Fender Point to Card Sound",
        "imagery_or_lidar_dates": "2018-07-26 to 2019-04-16",
        "reported_mhw_accuracy_95pct_m": 2.3,
        "reported_mllw_accuracy_95pct_m": 3.0,
        "inport_url": "https://www.fisheries.noaa.gov/inport/item/74866",
        "completion_report": "https://www.ngs.noaa.gov/desc_reports/FL1808A-TB-N.pdf",
        "geographic_extent_wgs84": [-80.40325, 25.32522995, -80.21719, 25.51193995],
        "status": "project_metadata_verified_vectors_not_yet_retrieved",
    },
    {
        "project_id": "FL2317-CS-N",
        "inport_id": 76789,
        "name": "Port of Miami",
        "imagery_or_lidar_dates": "2023-10-21",
        "reported_horizontal_accuracy_95pct_m": 1.2,
        "inport_url": "https://www.fisheries.noaa.gov/inport/item/76789",
        "completion_report": "https://www.ngs.noaa.gov/desc_reports/FL2317-CS-N.pdf",
        "geographic_extent_wgs84": [-80.2157448, 25.73422824, -80.1074168, 25.81199791],
        "status": "newer_port_of_miami_shoreline_candidate_vectors_not_yet_retrieved",
    },
    {
        "project_id": "FL0413",
        "inport_id": 61412,
        "name": "Port of Miami",
        "imagery_or_lidar_dates": "2005-02",
        "inport_url": "https://www.fisheries.noaa.gov/inport/item/61412",
        "geographic_extent_wgs84": [-80.336873, 25.5093105, -80.1019091, 25.9546342],
        "status": "older_port_of_miami_comparison_candidate",
    },
    {
        "project_id": "FL1603A-CM-N",
        "inport_id": 61478,
        "name": "Convoy Point",
        "imagery_or_lidar_dates": "2017-03-19",
        "inport_url": "https://www.fisheries.noaa.gov/inport/item/61478",
        "completion_report": "https://www.ngs.noaa.gov/desc_reports/FL1603A-CM-N.PDF",
        "status": "local_comparison_candidate_vectors_not_yet_retrieved",
    },
]

KEYWORDS = ("shoreline", "cusp", "national", "mhw", "mllw", "coastal")


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].split(":")[-1]


def parse_feature_types(xml_text: str) -> list[dict[str, str]]:
    root = ET.fromstring(xml_text)
    result = []
    for node in root.iter():
        if local_name(node.tag) != "FeatureType":
            continue
        fields: dict[str, str] = {}
        for child in node:
            key = local_name(child.tag)
            if key in {"Name", "Title", "Abstract", "DefaultCRS", "SRS", "DefaultSRS"}:
                fields[key] = (child.text or "").strip()
        if fields.get("Name"):
            result.append(fields)
    return result


def parse_wms_layers(xml_text: str) -> list[dict[str, str]]:
    root = ET.fromstring(xml_text)
    result = []
    for node in root.iter():
        if local_name(node.tag) != "Layer":
            continue
        fields: dict[str, str] = {}
        for child in node:
            key = local_name(child.tag)
            if key in {"Name", "Title", "Abstract"} and child.text:
                fields[key] = child.text.strip()
        if fields.get("Name"):
            result.append(fields)
    return result


def is_candidate(layer: dict[str, str]) -> bool:
    text = " ".join(layer.values()).lower()
    return any(word in text for word in KEYWORDS)


def request_capabilities(
    session: requests.Session, service: str, version: str
) -> tuple[str, str]:
    endpoints = WFS_ENDPOINTS if service.upper() == "WFS" else WMS_ENDPOINTS
    params = {"service": service, "request": "GetCapabilities", "version": version}
    errors = []
    for endpoint in endpoints:
        for attempt in range(2):
            try:
                response = session.get(endpoint, params=params, timeout=TIMEOUT)
                if response.status_code in {429, 500, 502, 503, 504} and attempt == 0:
                    time.sleep(2)
                    continue
                response.raise_for_status()
                # Parse before treating a 200 HTML error page as success.
                ET.fromstring(response.text)
                return response.url, response.text
            except (requests.RequestException, ET.ParseError) as exc:
                body = ""
                if isinstance(exc, requests.HTTPError) and exc.response is not None:
                    body = (exc.response.text or "")[:240].replace("\\n", " ")
                errors.append(
                    f"{endpoint} attempt {attempt + 1}: {type(exc).__name__}: {exc}; body={body!r}"
                )
                break
    raise RuntimeError(f"{service} GetCapabilities failed: {'; '.join(errors)}")


def run_audit(output_dir: Path, session: requests.Session | None = None) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    session = session or requests.Session()
    session.headers.update({"User-Agent": "LUPITA-research-shoreline-audit/1.0 (research-only)"})

    wfs_url, wfs_xml = request_capabilities(session, "WFS", "2.0.0")
    (output_dir / "noaa_nsde_wfs_capabilities.xml").write_text(wfs_xml, encoding="utf-8")
    feature_types = parse_feature_types(wfs_xml)
    candidate_types = [item for item in feature_types if is_candidate(item)]

    wms_url = None
    wms_error = None
    wms_layers: list[dict[str, str]] = []
    try:
        wms_url, wms_xml = request_capabilities(session, "WMS", "1.3.0")
        (output_dir / "noaa_nsde_wms_capabilities.xml").write_text(wms_xml, encoding="utf-8")
        wms_layers = parse_wms_layers(wms_xml)
    except Exception as exc:  # WMS is supplementary; WFS is the required discovery source.
        wms_error = f"{type(exc).__name__}: {exc}"

    report = {
        "audit_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "service_inventory_retrieved",
        "purpose": "Discover NOAA NGS shoreline service layers before selecting and downloading project-specific vectors.",
        "wfs": {
            "candidate_endpoints": WFS_ENDPOINTS,
            "capabilities_url": wfs_url,
            "version": "2.0.0",
            "feature_type_count": len(feature_types),
            "candidate_feature_types": candidate_types,
        },
        "wms": {
            "candidate_endpoints": WMS_ENDPOINTS,
            "capabilities_url": wms_url,
            "layer_count": len(wms_layers),
            "candidate_layers": [item for item in wms_layers if is_candidate(item)],
            "error": wms_error,
        },
        "project_metadata_candidates": PROJECTS,
        "limitations": [
            "A service layer name or title does not prove it contains the project-specific shoreline vectors.",
            "WMS imagery is not a substitute for source vector geometry.",
            "MHW and MLLW features must remain separate and retain their vertical-datum metadata.",
            "Project metadata rectangles are not proof of complete surveyed coverage.",
            "No final Biscayne Bay boundary is created by this audit.",
            "NOAA shoreline products are not navigation products and are not legal survey boundaries.",
        ],
    }
    (output_dir / "noaa_nsde_shoreline_service_inventory.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/noaa-shoreline"))
    args = parser.parse_args()
    report = run_audit(args.output_dir)
    print(json.dumps({
        "wfs_feature_type_count": report["wfs"]["feature_type_count"],
        "wfs_candidate_count": len(report["wfs"]["candidate_feature_types"]),
        "wms_candidate_count": len(report["wms"]["candidate_layers"]),
        "output_dir": str(args.output_dir),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
