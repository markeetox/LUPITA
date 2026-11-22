#!/usr/bin/env python3
"""Download checksum-verified, targeted Pulley Ridge NOAA source files for research."""
from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

SOURCES = {
    "adcp_0181331": {
        "manifest": "https://www.nodc.noaa.gov/archive/arc0139/0181331/0181331.1.1.xml",
        "root": "https://www.nodc.noaa.gov/archive/arc0139/0181331/1.1/",
        "select": lambda p: (
            ("/Data/ADCP_Data" in p and p.endswith(".asc"))
            or p.endswith("/Documentation/ADCP_DataDocumentation.pdf")
        ),
    },
    "temperature_logger_0190271": {
        "manifest": "https://www.nodc.noaa.gov/archive/arc0139/0190271/0190271.1.1.xml",
        "root": "https://www.nodc.noaa.gov/archive/arc0139/0190271/1.1/",
        "select": lambda p: (
            p.endswith("/Temperature_Data01_2012-2014_FloridaKeys.csv")
            or p.endswith("/Documentation/Temperature_DataDocumentation.pdf")
            or p == "about/0190271_lonlat.txt"
        ),
    },
    "ctd_0190533": {
        "manifest": "https://www.nodc.noaa.gov/archive/arc0141/0190533/0190533.1.1.xml",
        "root": "https://www.nodc.noaa.gov/archive/arc0141/0190533/1.1/",
        "select": lambda p: (
            ("/Data/Processed_Data/" in p and p.endswith(".cnv"))
            or ("/Data/CTD_Raw_Data/" in p and p.endswith((".hdr", ".XMLCON")))
            or p.endswith("/Documentation/CTD_DataDocumentation.pdf")
        ),
    },
}

OUT = Path("noaa-pulley-ridge-research")
USER_AGENT = "LUPITA-research-source-audit/1.0"


def fetch(url: str, attempts: int = 4) -> bytes:
    last = None
    for attempt in range(attempts):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            last = exc
            if attempt + 1 < attempts:
                time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"Download failed after {attempts} attempts: {url}: {last}")


def manifest_files(xml_bytes: bytes) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    records = []
    for node in root.findall(".//file"):
        path = node.findtext("path")
        if not path:
            continue
        digests = {d.attrib.get("algorithm", "").lower(): (d.text or "").strip()
                   for d in node.findall("digest")}
        records.append({
            "path": path,
            "size": int(node.findtext("size") or 0),
            "sha256": digests.get("sha256"),
            "type": node.findtext("type"),
        })
    return records


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "purpose": "Targeted, checksum-verified research download; no files are committed to the repository.",
        "sources": {},
    }
    failures = []
    for source_name, config in SOURCES.items():
        print(f"Reading manifest: {source_name}", flush=True)
        manifest = fetch(config["manifest"])
        records = manifest_files(manifest)
        selected = [r for r in records if r["type"] != "directory" and config["select"](r["path"])]
        source_dir = OUT / source_name
        source_dir.mkdir(parents=True, exist_ok=True)
        source_result = {
            "manifest_url": config["manifest"],
            "manifest_sha256": hashlib.sha256(manifest).hexdigest(),
            "selected_count": len(selected),
            "files": [],
        }
        for record in selected:
            url = config["root"] + record["path"]
            try:
                payload = fetch(url)
                actual = hashlib.sha256(payload).hexdigest()
                if len(payload) != record["size"]:
                    raise ValueError(f"size mismatch: expected {record['size']}, got {len(payload)}")
                if not record["sha256"] or actual.lower() != record["sha256"].lower():
                    raise ValueError(f"SHA-256 mismatch: expected {record['sha256']}, got {actual}")
                destination = source_dir / record["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(payload)
                source_result["files"].append({
                    **record, "download_url": url, "downloaded_bytes": len(payload),
                    "verified_sha256": actual, "local_path": str(destination),
                    "status": "verified",
                })
                print(f"VERIFIED {source_name}: {record['path']} ({len(payload)} bytes)", flush=True)
            except Exception as exc:
                failures.append({"source": source_name, "path": record["path"], "error": str(exc)})
                source_result["files"].append({**record, "download_url": url, "status": "failed", "error": str(exc)})
                print(f"FAILED {source_name}: {record['path']}: {exc}", flush=True)
        report["sources"][source_name] = source_result
    report["failures"] = failures
    (OUT / "download_manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if failures:
        raise SystemExit(f"{len(failures)} source files failed verification; see download_manifest.json")
    print(f"Complete: {sum(s['selected_count'] for s in report['sources'].values())} files verified.", flush=True)


if __name__ == "__main__":
    main()
