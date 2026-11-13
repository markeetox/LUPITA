"""Inspect the NOAA Shoreline Data Explorer National Shoreline project UI.

Research-only browser diagnostic. It records the UI and network endpoints after
filtering by a known project ID; it does not alter NOAA data or click download.
"""
from __future__ import annotations

import asyncio
import json
from io import BytesIO
from pathlib import Path
import zipfile
from collections import Counter

import shapefile
from pyproj import CRS, Transformer
from shapely.geometry import shape as make_shape, mapping
from shapely.ops import transform as transform_geometry

URL = "https://nsde.ngs.noaa.gov/cmp.html"
PROJECT_IDS = ["FL1808C-TB-N", "FL1808A-TB-N", "FL2317-CS-N"]
PROJECT_METADATA = {
    "FL1808A-TB-N": {
        "inport_id": 74866,
        "inport_url": "https://www.fisheries.noaa.gov/inport/item/74866",
        "source_dates": ["2018-07-26", "2019-04-16"],
        "reported_horizontal_accuracy_95pct_m": "1.3-3.0",
        "geographic_extent_wgs84": [-80.40325, 25.3252299521071, -80.2171900246895, 25.5119399520435],
    },
    "FL1808C-TB-N": {
        "inport_id": 73241,
        "inport_url": "https://www.fisheries.noaa.gov/inport/item/73241",
        "source_dates": ["2018-07-26", "2019-04-13"],
        "reported_horizontal_accuracy_95pct_m": "1.3-3.0",
        "geographic_extent_wgs84": [-80.3095, 25.6344886723368, -80.16894, 25.7729300000031],
    },
    "FL2317-CS-N": {
        "inport_id": 76789,
        "inport_url": "https://www.fisheries.noaa.gov/inport/item/76789",
        "source_dates": ["2023-10-21"],
        "reported_horizontal_accuracy_95pct_m": "1.2",
        "geographic_extent_wgs84": [-80.2157448950401, 25.7342282449007, -80.1074168708588, 25.8119979108154],
    },
}


async def inspect_project(page, project_id: str, output_dir: Path) -> dict:
    input_inventory = await page.locator("input").evaluate_all(
        """els => els.map((el, index) => ({
          index, type: el.type, placeholder: el.placeholder, ariaLabel: el.getAttribute('aria-label'),
          value: el.value, outerHTML: el.outerHTML.slice(0, 500)
        }))"""
    )
    project_input = page.get_by_placeholder("e.g. FL1417G-CM-N")
    await project_input.fill(project_id)
    await project_input.press("Enter")
    await page.wait_for_timeout(7000)

    body_text = await page.locator("body").inner_text()
    controls = await page.locator("button, a, select, [role=button], [role=option]").evaluate_all(
        """els => els.map((el, index) => ({
          index, tag: el.tagName, role: el.getAttribute('role'),
          text: (el.innerText || el.textContent || '').trim().slice(0, 240),
          href: el.href || null, disabled: !!el.disabled,
          ariaLabel: el.getAttribute('aria-label'), title: el.title || null
        }))"""
    )
    await page.screenshot(path=str(output_dir / f"{project_id}.png"), full_page=True)
    (output_dir / f"{project_id}.html").write_text(
        await page.content(), encoding="utf-8"
    )
    return {
        "project_id": project_id,
        "body_text": body_text[:12000],
        "inputs_before_filter": input_inventory,
        "controls_after_filter": controls[:300],
    }


async def download_project_archives(page, output_dir: Path) -> list[dict]:
    """Download official project ZIPs using the URL template in NSDE's CMP UI."""
    results = []
    for project_id in PROJECT_IDS:
        url = f"https://nsde.ngs.noaa.gov/downloads/{project_id}.zip"
        record = {"project_id": project_id, "url": url}
        try:
            response = await page.request.get(url, timeout=120000)
            body = await response.body()
            record.update({
                "http_status": response.status,
                "content_type": response.headers.get("content-type"),
                "content_length_header": response.headers.get("content-length"),
                "downloaded_bytes": len(body),
                "final_url": response.url,
            })
            if response.status == 200 and body[:4] == b"PK\x03\x04":
                archive_path = output_dir / f"{project_id}.zip"
                archive_path.write_bytes(body)
                with zipfile.ZipFile(BytesIO(body)) as archive:
                    names = archive.namelist()
                    record["archive_file"] = archive_path.name
                    record["archive_entries"] = names
                    record["shapefile_components"] = [
                        name for name in names if name.lower().endswith((".shp", ".shx", ".dbf", ".prj"))
                    ]
                    record["metadata_entries"] = [
                        name for name in names if name.lower().endswith((".xml", ".txt", ".pdf", ".html"))
                    ]
                    record["zip_integrity"] = "passed"
            else:
                record["download_status"] = "not_a_zip_or_http_error"
                record["body_snippet"] = body[:500].decode("utf-8", errors="replace")
        except Exception as exc:
            record["error"] = f"{type(exc).__name__}: {exc}"
        results.append(record)
    return results


def extract_project_archives(downloads: list[dict], output_dir: Path) -> dict:
    """Convert downloaded NOAA shapefiles to NAD83-to-WGS84 GeoJSON and subsets."""
    extracted_root = output_dir / "extracted"
    extracted_root.mkdir(parents=True, exist_ok=True)
    geojson_root = output_dir / "geojson"
    geojson_root.mkdir(parents=True, exist_ok=True)
    project_summaries = {}

    for download in downloads:
        project_id = download["project_id"]
        archive_name = download.get("archive_file")
        if not archive_name:
            project_summaries[project_id] = {
                "status": "archive_not_downloaded",
                "download_error": download.get("error") or download.get("body_snippet"),
            }
            continue

        archive_path = output_dir / archive_name
        project_dir = extracted_root / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(project_dir)

        project_summary = {
            "status": "converted",
            "metadata": PROJECT_METADATA.get(project_id, {}),
            "archive_file": archive_name,
            "source_crs": None,
            "shapefiles": {},
            "line_feature_count": 0,
            "point_feature_count": 0,
            "mhw_feature_count": 0,
            "mllw_depth_contour_count": 0,
        }

        for shp_path in sorted(project_dir.glob("*.shp")):
            reader = shapefile.Reader(str(shp_path), encoding="utf-8")
            fields = [field[0] for field in reader.fields[1:]]
            prj_path = shp_path.with_suffix(".prj")
            if not prj_path.exists():
                raise RuntimeError(f"Missing CRS sidecar for {shp_path.name}")
            prj_text = prj_path.read_text(encoding="utf-8")
            source_crs = CRS.from_wkt(prj_text)
            # NOAA's legacy WKT carries EPSG:4269 but its TOWGS84 clause can
            # prevent pyproj from resolving to_epsg(); accept explicit authority
            # tags or a normalized EPSG:4269 WKT from a standards-compliant writer.
            epsg_4269_tagged = (
                source_crs.to_epsg() == 4269
                or 'AUTHORITY["EPSG","4269"]' in prj_text
                or 'ID["EPSG",4269]' in prj_text
            )
            if not (
                source_crs.is_geographic
                and source_crs.datum.name == "North American Datum 1983"
                and source_crs.ellipsoid.name == "GRS 1980"
                and epsg_4269_tagged
            ):
                raise RuntimeError(
                    f"Unexpected source CRS for {shp_path.name}: {source_crs.to_string()}"
                )
            project_summary["source_crs"] = "NAD83 (EPSG:4269 per NOAA InPort metadata)"
            to_wgs84 = Transformer.from_crs(source_crs, 4326, always_xy=True).transform
            to_length_crs = Transformer.from_crs(source_crs, 26917, always_xy=True).transform

            all_features = []
            mhw_features = []
            mllw_features = []
            class_counts = Counter()
            attribute_counts = Counter()
            source_date_counts = Counter()
            accuracy_counts = Counter()
            data_source_counts = Counter()
            source_id_counts = Counter()
            mhw_length_m = 0.0
            mllw_length_m = 0.0

            for shape_record in reader.iterShapeRecords():
                properties = shape_record.record.as_dict()
                geometry = make_shape(shape_record.shape.__geo_interface__)
                geometry = transform_geometry(to_wgs84, geometry)
                if geometry.is_empty:
                    continue
                feature = {
                    "type": "Feature",
                    "id": properties.get("FEATURE_ID"),
                    "properties": {
                        **properties,
                        "LUPITA_SOURCE_PROJECT_ID": project_id,
                        "LUPITA_SOURCE_FILE": shp_path.name,
                        "LUPITA_SOURCE_CRS": "EPSG:4269",
                        "LUPITA_OUTPUT_CRS": "EPSG:4326",
                    },
                    "geometry": mapping(geometry),
                }
                all_features.append(feature)
                class_counts[str(properties.get("CLASS") or "unknown")] += 1
                attribute_counts[str(properties.get("ATTRIBUTE") or "unknown")] += 1
                source_date_counts[str(properties.get("SRC_DATE") or "unknown")] += 1
                accuracy_counts[str(properties.get("HOR_ACC") or "unknown")] += 1
                data_source_counts[str(properties.get("DATA_SOURC") or "unknown")] += 1
                source_id_counts[str(properties.get("SOURCE_ID") or "unknown")] += 1

                if shp_path.stem.endswith("_l1"):
                    if (
                        properties.get("CLASS") == "SHORELINE"
                        and properties.get("ATTRIBUTE") == "Natural.Mean High Water"
                    ):
                        mhw_features.append(feature)
                        mhw_length_m += transform_geometry(to_length_crs, make_shape(
                            shape_record.shape.__geo_interface__
                        )).length
                    if (
                        properties.get("CLASS") == "CONTOUR"
                        and properties.get("ATTRIBUTE") == "Depth Contour"
                        and properties.get("INFORM") == "MLLW"
                    ):
                        mllw_features.append(feature)
                        mllw_length_m += transform_geometry(to_length_crs, make_shape(
                            shape_record.shape.__geo_interface__
                        )).length

            output_name = f"{project_id}_{shp_path.stem.split('_')[-1]}.geojson"
            output_path = geojson_root / output_name
            output_path.write_text(json.dumps({
                "type": "FeatureCollection",
                "name": output_name.removesuffix(".geojson"),
                "features": all_features,
            }, separators=(",", ":")) + "\n", encoding="utf-8")

            layer_summary = {
                "source_file": shp_path.name,
                "output_file": f"geojson/{output_name}",
                "feature_count": len(all_features),
                "geometry_types": sorted({f["geometry"]["type"] for f in all_features}),
                "class_counts": dict(class_counts),
                "attribute_counts": dict(attribute_counts),
                "source_date_counts": dict(source_date_counts),
                "horizontal_accuracy_m_counts": dict(accuracy_counts),
                "data_source_counts": dict(data_source_counts),
                "source_id_counts": dict(source_id_counts),
            }
            project_summary["shapefiles"][shp_path.stem] = layer_summary

            if shp_path.stem.endswith("_l1"):
                project_summary["line_feature_count"] += len(all_features)
                project_summary["mhw_feature_count"] += len(mhw_features)
                project_summary["mllw_depth_contour_count"] += len(mllw_features)
                for suffix, subset in (
                    ("mhw", mhw_features),
                    ("mllw_depth_contours", mllw_features),
                ):
                    subset_name = f"{project_id}_{suffix}.geojson"
                    (geojson_root / subset_name).write_text(json.dumps({
                        "type": "FeatureCollection",
                        "name": subset_name.removesuffix(".geojson"),
                        "features": subset,
                    }, separators=(",", ":")) + "\n", encoding="utf-8")
                project_summary["mhw_total_length_km"] = round(mhw_length_m / 1000, 3)
                project_summary["mllw_depth_contour_total_length_km"] = round(
                    mllw_length_m / 1000, 3
                )
            elif shp_path.stem.endswith("_p1"):
                project_summary["point_feature_count"] += len(all_features)

        project_summaries[project_id] = project_summary

    audit = {
        "generated_at_utc": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat(),
        "source": "NOAA National Geodetic Survey Coastal Mapping Program / NOAA Shoreline Data Explorer",
        "source_download_pattern": "https://nsde.ngs.noaa.gov/downloads/{project_id}.zip",
        "output_crs": "EPSG:4326",
        "project_summaries": project_summaries,
        "guardrails": [
            "MHW subset includes only CLASS=SHORELINE and ATTRIBUTE=Natural.Mean High Water.",
            "MLLW subset contains Depth Contour lines with INFORM=MLLW; it is not an MLLW shoreline and contains no numeric contour depth attribute.",
            "Apparent mangrove lines, mangrove extents, man-made shoreline structures, alongshore features, and cartographic limits remain in the full source linework and are not merged into the MHW subset.",
            "Project geographic rectangles are data-management extents and do not prove complete surveyed coverage.",
            "FL2317 is a port-focused source; no Natural.Mean High Water shoreline features were present in its line shapefile.",
            "No production scoring, species profiles, or API v1 fields are changed.",
        ],
    }
    (output_dir / "noaa_cmp_project_geometry_audit.json").write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf-8"
    )
    return audit


async def run(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    network_events = []
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(accept_downloads=True, viewport={"width": 1600, "height": 1100})
        page.on("request", lambda req: network_events.append({
            "type": "request", "method": req.method, "url": req.url[:2000]
        }) if any(k in req.url.lower() for k in (
            "download", ".zip", "api", ".json", "geojson", "shp",
            "featureserver", "mapserver", "geoserver", "ows"
        )) else None)
        page.on("response", lambda res: network_events.append({
            "type": "response", "status": res.status, "url": res.url[:2000]
        }) if any(k in res.url.lower() for k in (
            "download", ".zip", "api", ".json", "geojson", "shp",
            "featureserver", "mapserver", "geoserver", "ows"
        )) else None)
        response = await page.goto(URL, wait_until="domcontentloaded", timeout=90000)
        await page.wait_for_timeout(12000)
        initial = {
            "url": page.url,
            "title": await page.title(),
            "status": response.status if response else None,
            "body_text": (await page.locator("body").inner_text())[:12000],
            "inputs": await page.locator("input").evaluate_all(
                """els => els.map((el, index) => ({
                  index, type: el.type, placeholder: el.placeholder,
                  ariaLabel: el.getAttribute('aria-label'), value: el.value
                }))"""
            ),
        }
        (output_dir / "initial.html").write_text(await page.content(), encoding="utf-8")
        downloads = await download_project_archives(page, output_dir)
        geometry_audit = extract_project_archives(downloads, output_dir)
        projects = []
        for project_id in PROJECT_IDS:
            try:
                projects.append(await inspect_project(page, project_id, output_dir))
            except Exception as exc:
                projects.append({
                    "project_id": project_id,
                    "error": f"{type(exc).__name__}: {exc}",
                })
        report = {
            "url": URL,
            "initial": initial,
            "project_filter_results": projects,
            "project_downloads": downloads,
            "geometry_audit": geometry_audit,
            "network_events": network_events[-500:],
            "note": "Project ZIPs were downloaded using the URL pattern exposed by NOAA NSDE; source shapefiles were converted from EPSG:4269 to EPSG:4326 for research inspection."
        }
        (output_dir / "nsde_cmp_ui_audit.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        await browser.close()
    return report


if __name__ == "__main__":
    result = asyncio.run(run(Path("artifacts/nsde-cmp-ui")))
    print(json.dumps({
        "initial_status": result["initial"]["status"],
        "initial_url": result["initial"]["url"],
        "inputs": result["initial"]["inputs"],
        "project_downloads": [
            {"project_id": d["project_id"], "http_status": d.get("http_status"),
             "downloaded_bytes": d.get("downloaded_bytes"), "archive_file": d.get("archive_file"),
             "error": d.get("error"), "download_status": d.get("download_status")}
            for d in result["project_downloads"]
        ],
        "geometry_audit": result["geometry_audit"]["project_summaries"],
        "project_results": [
            {"project_id": p["project_id"], "error": p.get("error"),
             "body_text_length": len(p.get("body_text", "")),
             "controls_count": len(p.get("controls_after_filter", []))}
            for p in result["project_filter_results"]
        ],
        "network_event_count": len(result["network_events"]),
    }, indent=2))
