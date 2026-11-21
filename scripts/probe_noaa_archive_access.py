#!/usr/bin/env python3
"""Read-only probe of NOAA NCEI archive endpoints for selected Pulley Ridge datasets."""
from __future__ import annotations
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URLS = {
    "adcp_ncei_landing": "https://www.ncei.noaa.gov/archive/accession/0181331",
    "adcp_ncei_download": "https://www.ncei.noaa.gov/archive/accession/download/181331",
    "adcp_legacy_index": "https://www.nodc.noaa.gov/archive/arc0139/0181331/",
    "logger_ncei_landing": "https://www.ncei.noaa.gov/archive/accession/0190271",
    "logger_ncei_download": "https://www.ncei.noaa.gov/archive/accession/download/190271",
    "logger_legacy_index": "https://www.nodc.noaa.gov/archive/arc0139/0190271/",
    "ctd_ncei_landing": "https://www.ncei.noaa.gov/archive/accession/0190533",
    "ctd_ncei_download": "https://www.ncei.noaa.gov/archive/accession/download/190533",
    "ctd_legacy_index": "https://www.nodc.noaa.gov/archive/arc0141/0190533/",
    "seamap_ncei_landing": "https://www.ncei.noaa.gov/archive/accession/0131259",
    "seamap_oas_download": "https://www.ncei.noaa.gov/archive/archive-management-system/OAS/bin/prd/jquery/accession/download/131259",
}

def probe(name: str, url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "LUPITA-research-archive-probe/1.0", "Range": "bytes=0-4095"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            body = response.read(4096)
            return {
                "name": name, "requested_url": url, "final_url": response.geturl(),
                "status": response.status, "content_type": response.headers.get("Content-Type"),
                "content_length": response.headers.get("Content-Length"),
                "content_range": response.headers.get("Content-Range"),
                "bytes_read": len(body), "preview": body[:1200].decode("utf-8", "replace"),
            }
    except urllib.error.HTTPError as exc:
        body = exc.read(4096)
        return {
            "name": name, "requested_url": url, "final_url": exc.geturl(),
            "status": exc.code, "content_type": exc.headers.get("Content-Type"),
            "content_length": exc.headers.get("Content-Length"),
            "bytes_read": len(body), "preview": body[:1200].decode("utf-8", "replace"),
        }
    except Exception as exc:
        return {"name": name, "requested_url": url, "error": f"{type(exc).__name__}: {exc}"}

def main() -> None:
    results = [probe(name, url) for name, url in URLS.items()]
    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Read-only endpoint and directory-listing discovery; no archive payloads downloaded.",
        "results": results,
    }
    Path("noaa_archive_probe.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    for item in results:
        print(json.dumps({k: v for k, v in item.items() if k != "preview"}))
        if item.get("preview"):
            print("PREVIEW", item["name"], item["preview"][:350].replace("\\n", " "))

if __name__ == "__main__":
    main()
