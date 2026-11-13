"""Inspect the NOAA Shoreline Data Explorer National Shoreline project UI.

Research-only browser diagnostic. It records the UI and network endpoints after
filtering by a known project ID; it does not alter NOAA data or click download.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright

URL = "https://nsde.ngs.noaa.gov/cmp.html"
PROJECT_IDS = ["FL1808C-TB-N", "FL1808A-TB-N", "FL2317-CS-N"]


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


async def run(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    network_events = []
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
            "network_events": network_events[-500:],
            "note": "No download button was clicked. This is an interface/network discovery artifact only.",
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
        "project_results": [
            {"project_id": p["project_id"], "error": p.get("error"),
             "body_text_length": len(p.get("body_text", "")),
             "controls_count": len(p.get("controls_after_filter", []))}
            for p in result["project_filter_results"]
        ],
        "network_event_count": len(result["network_events"]),
    }, indent=2))
