#!/usr/bin/env python3
"""Research-only extraction of South Florida in-situ temperatures and matching MUR SST."""
from __future__ import annotations
import argparse, csv, io, json, math, re, statistics, zipfile
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote
import requests

USGS_ZIP = "https://coastal.er.usgs.gov/data-release/doi-F71C1TZK/data/FL_coral_underwater_temps_to_Jul2024.zip"
SECOORA_BASE = "https://erddap.secoora.org/erddap/tabledap"
MUR_BASE = "https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41.csv"
USER_AGENT = "LUPITA-South-Florida-Temperature-Research/1.0 (+https://github.com/markeetox/LUPITA)"
USGS_SITES = {
    "brewster reef": {"latitude": 25.56676, "longitude": -80.09974, "depth_m": 3.96},
    "shadow reef": {"latitude": 25.47775, "longitude": -80.14088, "depth_m": 3.66},
    "ball buoy north": {"latitude": 25.31877, "longitude": -80.18426, "depth_m": 3.35},
}
FWC_STATIONS = {
    "HFA04": {"dataset": "org_secoora_flkeys_hfa04", "latitude": 24.6687, "longitude": -82.8926, "z_m": -11.0, "start": "2020-12-11T15:00:00Z", "end": "2022-08-12T14:00:00Z"},
    "RHA54": {"dataset": "org_secoora_flkeys_rha54", "latitude": 24.5056, "longitude": -83.1305, "z_m": -43.0, "start": "2023-09-22T14:00:00Z", "end": "2024-08-14T13:00:00Z"},
    "LKA57": {"dataset": "org_secoora_flkeys_lka57", "latitude": 24.4373, "longitude": -81.9493, "z_m": -23.0, "start": "2021-07-26T16:00:00Z", "end": "2024-06-25T19:00:00Z"},
}

def parse_usgs_time(value):
    value = (value or "").strip()
    for fmt in ("%m/%d/%Y %H:%M", "%m/%d/%Y %H:%M:%S", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone(timedelta(hours=-4)))
        except ValueError:
            pass
    return None

def parse_float(value):
    try:
        number = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and -5 <= number <= 50 else None

def read_usgs_csv(content, start, end):
    reader = csv.DictReader(io.StringIO(content))
    fields = list(reader.fieldnames or [])
    if not fields:
        raise ValueError("USGS CSV has no header row")
    time_field = next((f for f in fields if "time" in f.lower()), None)
    date_field = next((f for f in fields if f.lower().strip() == "date"), None)
    if time_field is None and date_field is None:
        raise ValueError(f"Could not identify USGS date/time columns: {fields[:12]}")
    site_fields = [f for f in fields if f not in {time_field, date_field} and f and f.strip()]
    observations = []
    for row in reader:
        stamp = parse_usgs_time(row.get(time_field, "")) if time_field else None
        if stamp is None and date_field:
            stamp = parse_usgs_time(row.get(date_field, ""))
            time_value = (row.get(time_field, "") if time_field else "").strip()
            if stamp and time_value:
                try:
                    t = datetime.strptime(time_value, "%H:%M").time()
                    stamp = stamp.replace(hour=t.hour, minute=t.minute)
                except ValueError:
                    pass
        if stamp is None or stamp < start or stamp > end:
            continue
        for site_field in site_fields:
            temp = parse_float(row.get(site_field, ""))
            if temp is None:
                continue
            key = re.sub(r"\s+", " ", site_field.strip()).lower()
            meta = USGS_SITES.get(key, {})
            observations.append({
                "timestamp": stamp.isoformat(), "date_utc": stamp.astimezone(timezone.utc).date().isoformat(),
                "source": "USGS CREST v9", "site": site_field.strip(),
                "latitude": meta.get("latitude", ""), "longitude": meta.get("longitude", ""),
                "sensor_depth_m": meta.get("depth_m", ""), "temperature_c": temp,
                "qc_flag": "not_provided_in_release",
            })
    if not observations:
        raise ValueError("No USGS observations found; inspect archive schema/date parsing")
    return observations

def write_csv(path, rows):
    if not rows:
        return
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def fetch_usgs(session, start, end, out_dir):
    response = session.get(USGS_ZIP, timeout=(20, 180))
    response.raise_for_status()
    archive_bytes = response.content
    (out_dir / "usgs_crest_v9_source.zip").write_bytes(archive_bytes)
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        names = [n for n in archive.namelist() if n.lower().endswith(".csv")]
        if not names:
            raise ValueError("USGS archive contains no CSV file")
        name = next((n for n in names if "underwater_temps" in n.lower()), names[0])
        content = archive.read(name).decode("utf-8-sig", errors="replace")
    rows = read_usgs_csv(content, start, end)
    write_csv(out_dir / "usgs_crest_observations.csv", rows)
    return rows

def fetch_fwc(session, station, out_dir):
    meta = FWC_STATIONS[station]
    columns = ["time", "latitude", "longitude", "z", "sea_water_temperature", "sea_water_temperature_qc_agg", "sea_water_temperature_qc_tests"]
    query = ",".join(columns) + f"&time>={meta['start']}&time<={meta['end']}"
    url = f"{SECOORA_BASE}/{meta['dataset']}.csv?" + quote(query, safe=",&=<>:TZ-.")
    response = session.get(url, timeout=(20, 120))
    response.raise_for_status()
    (out_dir / f"fwc_{station.lower()}_raw.csv").write_bytes(response.content)
    raw_rows = list(csv.reader(io.StringIO(response.text)))
    if len(raw_rows) < 3:
        raise ValueError(f"FWC {station} returned no observation rows")
    header, observations = raw_rows[0], []
    for raw in raw_rows[2:]:
        if not raw or len(raw) < len(header):
            continue
        row = dict(zip(header, raw))
        try:
            stamp = datetime.fromisoformat(row["time"].replace("Z", "+00:00"))
            temp = parse_float(row.get("sea_water_temperature"))
            z = float(row.get("z") or meta["z_m"])
            qc = int(float(row.get("sea_water_temperature_qc_agg", "9")))
        except (KeyError, ValueError):
            continue
        if temp is None:
            continue
        observations.append({
            "timestamp": stamp.astimezone(timezone.utc).isoformat(), "date_utc": stamp.astimezone(timezone.utc).date().isoformat(),
            "source": "FWC-FWRI / SECOORA FLKEYS Array", "site": station,
            "latitude": float(row.get("latitude") or meta["latitude"]), "longitude": float(row.get("longitude") or meta["longitude"]),
            "sensor_depth_m": abs(z), "temperature_c": temp, "qc_flag": qc,
            "qc_tests": row.get("sea_water_temperature_qc_tests", ""),
        })
    if not observations:
        raise ValueError(f"FWC {station} returned no parseable observations")
    write_csv(out_dir / f"fwc_{station.lower()}_observations.csv", observations)
    return observations

def fetch_mur(session, site, lat, lon, start, end, out_dir):
    start_utc = start.astimezone(timezone.utc).date().isoformat() + "T09:00:00Z"
    end_utc = end.astimezone(timezone.utc).date().isoformat() + "T09:00:00Z"
    projection = f"analysed_sst[({start_utc}):1:({end_utc})][({lat:.5f})][({lon:.5f})]"
    url = MUR_BASE + "?" + quote(projection, safe="[]():,.-TZ")
    response = session.get(url, timeout=(20, 180))
    response.raise_for_status()
    raw_rows = list(csv.reader(io.StringIO(response.text)))
    if len(raw_rows) < 3:
        raise ValueError(f"MUR returned no rows for {site}: {response.text[:300]}")
    header, output = raw_rows[0], []
    for raw in raw_rows[2:]:
        if not raw or len(raw) < len(header):
            continue
        row = dict(zip(header, raw))
        try:
            stamp = datetime.fromisoformat(row["time"].replace("Z", "+00:00"))
            temp = parse_float(row.get("analysed_sst"))
            grid_lat, grid_lon = float(row["latitude"]), float(row["longitude"])
        except (KeyError, ValueError):
            continue
        if temp is not None:
            output.append({"date_utc": stamp.date().isoformat(), "site": site,
                "logger_latitude": lat, "logger_longitude": lon,
                "mur_grid_latitude": grid_lat, "mur_grid_longitude": grid_lon, "mur_sst_c": temp})
    safe = re.sub(r"[^a-z0-9]+", "-", site.lower()).strip("-")
    write_csv(out_dir / f"mur_{safe}.csv", output)
    return output

def summarize(rows, pass_only=False):
    counts = Counter(str(r.get("qc_flag", "not_provided")) for r in rows)
    selected = [r for r in rows if not pass_only or r.get("qc_flag") in (1, "1", "not_provided_in_release")]
    vals = sorted(float(r["temperature_c"]) for r in selected)
    if not vals:
        return {"records": len(rows), "qc_counts": dict(counts), "valid_records": 0}
    return {"records": len(rows), "qc_counts": dict(counts), "valid_records": len(vals),
        "min_c": round(vals[0], 3), "p05_c": round(vals[int((len(vals)-1)*.05)], 3),
        "median_c": round(statistics.median(vals), 3), "mean_c": round(statistics.fmean(vals), 3),
        "p95_c": round(vals[int((len(vals)-1)*.95)], 3), "max_c": round(vals[-1], 3)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="temperature-research-output")
    args = parser.parse_args()
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    start = datetime(2020, 1, 1, tzinfo=timezone.utc)
    end = datetime(2024, 8, 15, tzinfo=timezone.utc)
    usgs = fetch_usgs(session, start, end, out_dir)
    fwc = [row for station in FWC_STATIONS for row in fetch_fwc(session, station, out_dir)]
    all_rows = usgs + fwc
    locations = {}
    for row in usgs:
        if row["latitude"] != "" and row["longitude"] != "":
            locations[row["site"]] = (float(row["latitude"]), float(row["longitude"]))
    for station, meta in FWC_STATIONS.items():
        locations[station] = (meta["latitude"], meta["longitude"])
    mur = []
    for site, (lat, lon) in locations.items():
        site_rows = [r for r in all_rows if r["site"] == site]
        if site_rows:
            stamps = [datetime.fromisoformat(r["timestamp"]) for r in site_rows]
            mur.extend(fetch_mur(session, site, lat, lon, min(stamps), max(stamps), out_dir))
    write_csv(out_dir / "mur_sst_all_sites.csv", mur)

    # Pair daily in-situ means with the MUR value for the same site/date.
    # FWC uses aggregate QC PASS only; USGS has no per-row QC field in this release.
    insitu_daily = defaultdict(list)
    for row in all_rows:
        if row["source"].startswith("FWC") and row.get("qc_flag") not in (1, "1"):
            continue
        insitu_daily[(row["site"], row["date_utc"])].append(float(row["temperature_c"]))
    mur_daily = {(row["site"], row["date_utc"]): float(row["mur_sst_c"]) for row in mur}
    paired = []
    for key, values in insitu_daily.items():
        if key not in mur_daily:
            continue
        insitu_mean = statistics.fmean(values)
        mur_value = mur_daily[key]
        paired.append({
            "site": key[0], "date_utc": key[1], "insitu_records": len(values),
            "insitu_daily_mean_c": round(insitu_mean, 4), "mur_sst_c": round(mur_value, 4),
            "insitu_minus_mur_c": round(insitu_mean - mur_value, 4),
        })
    write_csv(out_dir / "daily_insitu_mur_comparison.csv", paired)
    pair_groups = defaultdict(list)
    for row in paired:
        pair_groups[row["site"]].append(float(row["insitu_minus_mur_c"]))

    groups = defaultdict(list)
    for row in all_rows:
        groups[(row["source"], row["site"])].append(row)
    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Research only; no production pipeline/model changes",
        "sources": {"usgs": USGS_ZIP, "fwc": SECOORA_BASE, "mur": "https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41.html"},
        "method_notes": [
            "USGS logger timestamps use the documented fixed GMT-04:00 convention.",
            "USGS v9 release does not provide per-observation QARTOD flags; do not treat this as equivalent to FWC QC.",
            "FWC aggregate QC flag 1 (PASS) is used for primary summaries; all returned flags are retained and counted.",
            "MUR is daily analysed sea-surface foundation temperature in degree_C, queried at the nearest native 0.01-degree grid coordinate.",
            "This first comparison uses native-grid MUR, not a reconstruction of LUPITA's stride-5 production sampling.",
            "Sensor temperatures describe the logger environment, not Permit preference or physiological tolerance.",
        ],
        "in_situ_summary": {f"{source} | {site}": summarize(rows, pass_only=True) for (source, site), rows in groups.items()},
        "mur_records": len(mur), "mur_site_summary": {},
        "paired_daily_records": len(paired),
        "paired_daily_difference_summary": {
            site: {
                "paired_days": len(values),
                "mean_insitu_minus_mur_c": round(statistics.fmean(values), 3),
                "mean_absolute_difference_c": round(statistics.fmean(abs(v) for v in values), 3),
                "max_absolute_difference_c": round(max(abs(v) for v in values), 3),
            }
            for site, values in pair_groups.items()
        },
    }
    for site in locations:
        vals = [float(r["mur_sst_c"]) for r in mur if r["site"] == site]
        if vals:
            report["mur_site_summary"][site] = {"records": len(vals), "min_c": round(min(vals), 3),
                "mean_c": round(statistics.fmean(vals), 3), "max_c": round(max(vals), 3)}
    (out_dir / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = ["# South Florida in-situ temperature and MUR comparison", "",
        f"Generated: {report['generated_utc']}", "",
        "> Research artifact only. No production scores, species profiles, or predictions are changed.", "",
        "## Method boundaries", ""]
    lines.extend(f"- {note}" for note in report["method_notes"])
    lines += ["", "## In-situ observations", "",
        "| Source / site | Records | QC counts | Min °C | Median °C | Mean °C | Max °C |",
        "|---|---:|---|---:|---:|---:|---:|"]
    for label, stats in report["in_situ_summary"].items():
        lines.append(f"| {label} | {stats.get('valid_records', 0)} | {stats.get('qc_counts', {})} | {stats.get('min_c', 'n/a')} | {stats.get('median_c', 'n/a')} | {stats.get('mean_c', 'n/a')} | {stats.get('max_c', 'n/a')} |")
    lines += ["", "## MUR SST point extracts", "", f"Total daily MUR records: {len(mur)}", "",
        "| Site | Records | Min °C | Mean °C | Max °C |", "|---|---:|---:|---:|---:|"]
    for site, stats in report["mur_site_summary"].items():
        lines.append(f"| {site} | {stats['records']} | {stats['min_c']} | {stats['mean_c']} | {stats['max_c']} |")
    lines += ["", "## Paired daily comparison", "",
        f"Matched daily records: {len(paired)}", "",
        "| Site | Paired days | Mean in-situ minus MUR °C | Mean absolute difference °C | Max absolute difference °C |",
        "|---|---:|---:|---:|---:|"]
    for site, stats in report["paired_daily_difference_summary"].items():
        lines.append(f"| {site} | {stats['paired_days']} | {stats['mean_insitu_minus_mur_c']} | {stats['mean_absolute_difference_c']} | {stats['max_absolute_difference_c']} |")
    lines += ["", "## Interpretation", "",
        "Compare each sensor only over its own observed dates. Surface-to-sensor differences can reflect vertical gradients, spatial separation, daily analysis/compositing and sensor exposure. They are not Permit preference or tolerance estimates.", "",
        "Raw USGS archive, normalized USGS observations, raw FWC extracts, normalized FWC observations and MUR CSVs are retained with this report.", ""]
    (out_dir / "README.md").write_text("\\n".join(lines), encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
