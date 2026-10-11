"""No-fishing areas from NOAA's National MPA Center (MPA Inventory)."""
from __future__ import annotations


def classify(fish_rstr) -> str:
    """'no_fishing', 'restricted' or 'other' from the inventory's Fishing Restrictions text."""
    t = (fish_rstr or "").lower()
    if "recreational fishing prohibited" in t:
        return "no_fishing"
    if "recreational fishing restricted" in t:
        return "restricted"
    return "other"


def _signed_area(ring) -> float:
    return sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1])) / 2.0


def rings_to_multipolygon(rings: list) -> list:
    """ArcGIS rings -> GeoJSON MultiPolygon coordinates. Clockwise rings are outer boundaries,
    counter-clockwise rings are holes that belong to the outer ring before them."""
    polys: list = []
    for ring in rings:
        pts = [[float(p[0]), float(p[1])] for p in ring]
        if len(pts) < 4:
            continue
        if _signed_area(pts) <= 0 or not polys:     # outer (or an orphan hole treated as outer)
            polys.append([pts])
        else:
            polys[-1].append(pts)
    return polys


def parse_closures(features: list[dict]) -> list[dict]:
    """Keep the no-fishing areas and tidy their attributes."""
    out = []
    for f in features:
        a = f.get("attributes") or {}
        rings = (f.get("geometry") or {}).get("rings")
        if not rings or classify(a.get("Fish_Rstr")) != "no_fishing":
            continue
        url = str(a.get("URL") or "").strip()
        out.append({
            "name": a.get("Site_Name") or "Protected area", "agency": a.get("Mgmt_Agen") or "",
            "level": a.get("Gov_Level") or "", "protection": a.get("Prot_Lvl") or "",
            "rule": a.get("Fish_Rstr") or "", "year": a.get("Estab_Yr"),
            "url": url if url.lower().startswith(("http://", "https://")) else "",
            "rings": rings})
    return out


def to_geojson(areas: list[dict], source: str, loaded: bool, generated_utc: str) -> dict:
    feats = []
    for a in areas:
        mp = rings_to_multipolygon([[(round(x, 4), round(y, 4)) for x, y in r] for r in a["rings"]])
        if not mp:
            continue
        feats.append({"type": "Feature",
                      "properties": {k: a[k] for k in ("name", "agency", "level", "protection", "rule", "year", "url")},
                      "geometry": {"type": "MultiPolygon", "coordinates": mp}})
    return {"type": "FeatureCollection", "loaded": loaded, "source": source,
            "generated_utc": generated_utc, "features": feats}
