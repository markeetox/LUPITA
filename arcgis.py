"""ArcGIS REST feature queries (FWC reef and habitat layers)."""
from __future__ import annotations

from pipeline import http

USER_AGENT = "fish-habitat-map/0.1"


def query_params(region: dict, out_fields: str = "*", return_geometry: bool = False,
                 simplify: float | None = None, offset: int = 0, page_size: int = 1000, where: str = "1=1") -> dict:
    (lat0, lat1), (lon0, lon1) = region["lat"], region["lon"]
    p = {"where": where, "geometry": f"{lon0},{lat0},{lon1},{lat1}", "geometryType": "esriGeometryEnvelope",
         "inSR": 4326, "spatialRel": "esriSpatialRelIntersects", "outFields": out_fields,
         "returnGeometry": "true" if return_geometry else "false", "outSR": 4326, "f": "json",
         "resultOffset": offset, "resultRecordCount": page_size}
    if return_geometry and simplify:
        p["maxAllowableOffset"] = simplify      # generalize outlines to this many degrees
        p["geometryPrecision"] = 4
    return p


def fetch_json(url: str, params: dict, timeout: int = 120) -> dict:
    j = http.get(url, params=params, timeout=timeout).json()
    if "error" in j:
        raise RuntimeError(j["error"].get("message", "ArcGIS error"))
    return j


def query_all(layer_url: str, region: dict, fetch=fetch_json, page_size: int = 1000,
              max_pages: int = 40, **kw) -> list[dict]:
    """All features inside the region, following pagination."""
    feats: list[dict] = []
    offset = 0
    for _ in range(max_pages):
        j = fetch(layer_url.rstrip("/") + "/query", query_params(region, offset=offset, page_size=page_size, **kw))
        got = j.get("features", [])
        feats += got
        if not got or not (j.get("exceededTransferLimit") or len(got) >= page_size):
            break
        offset += len(got)
    return feats
