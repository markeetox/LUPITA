#!/usr/bin/env python3
"""Compare NOAA CoastWatch and Upwell ERDDAP access for the MUR SST dataset.

This is an opt-in diagnostic only. It does not alter production configuration,
publish data, retry requests, or write credentials.
"""
from __future__ import annotations

import csv
import io
import time
from urllib.parse import quote

import requests

DATASET = "jplMURSST41"
VARIABLE = "analysed_sst"
HOSTS = {
    "coastwatch": "https://coastwatch.pfeg.noaa.gov/erddap",
    "upwell": "https://upwell.pfeg.noaa.gov/erddap",
}
USER_AGENT = "LUPITA-SST-diagnostic/1.0 (+https://github.com/markeetox/LUPITA)"
TIMEOUT = 240


def request_url(base: str, suffix: str, query: str | None = None) -> str:
    url = f"{base}/griddap/{DATASET}{suffix}"
    if query:
        url += "?" + quote(query, safe="[],():-.,")
    return url


def selected_headers(response: requests.Response) -> dict[str, str]:
    wanted = ("content-type", "content-length", "date", "server", "retry-after",
              "via", "x-cache", "x-request-id", "cf-ray")
    return {key: value for key, value in response.headers.items()
            if key.lower() in wanted}


def latest_csv_time(body: str) -> str | None:
    try:
        reader = csv.reader(io.StringIO(body))
        header = next(reader)
        if "time" not in header:
            return None
        index = header.index("time")
        next(reader, None)  # units row
        row = next(reader, None)
        return row[index] if row and len(row) > index else None
    except (StopIteration, csv.Error, ValueError):
        return None


def probe(label: str, url: str) -> None:
    print(f"\n=== {label} ===", flush=True)
    started = time.monotonic()
    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT, "Accept": "text/csv, text/plain, */*"},
            timeout=TIMEOUT,
        )
        elapsed = time.monotonic() - started
        print(f"status={response.status_code} elapsed_seconds={elapsed:.2f}", flush=True)
        print(f"content_type={response.headers.get('Content-Type', '')!r}", flush=True)
        print(f"content_length={response.headers.get('Content-Length', '')!r}", flush=True)
        print(f"headers={selected_headers(response)!r}", flush=True)
        if response.ok:
            print(f"body_bytes={len(response.content)}", flush=True)
            if url.endswith(".csv") or ".csv?" in url:
                print(f"first_observation_time={latest_csv_time(response.text)!r}", flush=True)
                print(f"body_preview={response.text[:240].replace(chr(10), ' | ')!r}", flush=True)
            else:
                for key in ("time_coverage_start", "time_coverage_end", "date_created", "testOutOfDate"):
                    marker = key + ' = '
                    pos = response.text.find(marker)
                    if pos >= 0:
                        print(response.text[pos:pos + 120].splitlines()[0], flush=True)
        else:
            print(f"error_body_preview={response.text[:800]!r}", flush=True)
    except requests.RequestException as exc:
        elapsed = time.monotonic() - started
        print(f"request_exception={type(exc).__name__}: {exc}", flush=True)
        print(f"elapsed_seconds={elapsed:.2f}", flush=True)


def main() -> None:
    # Metadata and a tiny South Florida request distinguish general endpoint
    # access from failures that occur only on gridded data requests.
    small_query = f"{VARIABLE}[(last)][(25):5:(26)][(-82):5:(-80)]"
    # Exact geographic bounds and stride used by the current production config.
    production_query = f"{VARIABLE}[(last)][(15):5:(60)][(-138):5:(-50)]"

    for name, base in HOSTS.items():
        print(f"\n######## {name}: {base} ########", flush=True)
        probe(f"{name} metadata", request_url(base, ".das"))
        probe(f"{name} small South Florida grid", request_url(base, ".csv", small_query))
        probe(f"{name} exact production-size grid", request_url(base, ".csv", production_query))


if __name__ == "__main__":
    main()
