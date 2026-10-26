"""List the layers of an ArcGIS REST service and count how many features fall in our region.
Run:  python -m pipeline.find_layers <MapServer or FeatureServer URL>"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import requests

from pipeline.sources import ndbc

ROOT = Path(__file__).resolve().parent.parent


def parse_layers(info: dict) -> list[dict]:
    """Layer id and name from a service's ?f=json response."""
    return [{"id": l["id"], "name": l.get("name", "")} for l in info.get("layers", []) if "id" in l]


def parse_count(resp: dict):
    return resp.get("count")


def bbox_param(region: dict) -> str:
    (lat0, lat1), (lon0, lon1) = region["lat"], region["lon"]
    return f"{lon0},{lat0},{lon1},{lat1}"


def _get(url: str, params: dict) -> dict:
    r = requests.get(url, params={**params, "f": "json"}, timeout=40, headers={"User-Agent": ndbc.USER_AGENT})
    r.raise_for_status()
    return r.json()


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        return
    base = sys.argv[1].rstrip("/")
    region = json.loads((ROOT / "config/sources.json").read_text())["region"]
    info = _get(base, {})
    layers = parse_layers(info)
    print(f"{base}\n{len(layers)} layers. Features inside {region['name']} box:\n")
    for l in layers:
        try:
            meta = _get(f"{base}/{l['id']}", {})
            geom = (meta.get("geometryType") or "?").replace("esriGeometry", "")
            fields = ", ".join(f["name"] for f in meta.get("fields", [])[:8])
            cnt = parse_count(_get(f"{base}/{l['id']}/query", {
                "where": "1=1", "geometry": bbox_param(region), "geometryType": "esriGeometryEnvelope",
                "inSR": 4326, "spatialRel": "esriSpatialRelIntersects", "returnCountOnly": "true"}))
            print(f"  {l['id']:>3}  {l['name'][:44]:44}  {geom:10}  in box: {cnt}")
            if cnt:
                print(f"       fields: {fields}")
        except Exception as exc:
            print(f"  {l['id']:>3}  {l['name'][:44]:44}  could not query ({str(exc)[:60]})")


if __name__ == "__main__":
    main()
