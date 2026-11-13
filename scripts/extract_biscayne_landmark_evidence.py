"""Focused, research-only NOAA ENC retrieval for Card Sound, Jewfish Creek, and Rickenbacker context."""
from __future__ import annotations
import argparse, json, sys, time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import requests

SERVICE = "https://encdirect.noaa.gov/arcgis/rest/services/encdirect/enc_harbour/MapServer"
TIMEOUT = (15, 90)
PAGE_SIZE = 500
MAX_PAGES = 50
CARD_SOUND_OBJECTIDS = [246233, 246243, 246247, 246258, 246267, 246284]
REGIONS = {
    "rickenbacker_causeway": {
        "bbox": [-80.22, 25.71, -80.14, 25.77],
        "layers": {84: "Harbor.Coastline_line", 87: "Harbor.Bridge_line", 118: "Harbor.Causeway_line", 233: "Harbor.Land_Area"},
        "purpose": "Charted causeway, bridge, coastline, and land-area context; not a reconstructed road alignment."
    },
    "jewfish_creek": {
        "bbox": [-80.43, 25.14, -80.34, 25.23],
        "layers": {41: "Harbor.Sea_Area_Named_Water_Area_point", 84: "Harbor.Coastline_line", 104: "Harbor.Depth_Contour_line", 132: "Harbor.Navigation_Line", 205: "Harbor.Tideway_area", 227: "Harbor.Depth_Area", 237: "Harbor.Sea_Area_Named_Water_Area"},
        "purpose": "Chart hydrography context around NOAA CO-OPS station 8723613; candidates are not automatically identified as Jewfish Creek."
    }
}
LANDMARK_REFERENCES = {
    "jewfish_creek_station_8723613": {
        "publisher": "NOAA CO-OPS",
        "url": "https://tidesandcurrents.noaa.gov/benchmarks/8723613.html",
        "coordinates_wgs84_lon_lat": [-80.39, 25.1833],
        "meaning": "Tidal benchmark reference point only, not a creek centerline, mouth, or ecological boundary."
    },
    "rickenbacker_causeway": {
        "publisher": "Miami-Dade County",
        "url": "https://www.miamidade.gov/global/transportation/public-works/rickenbacker-causeway.page",
        "meaning": "Official corridor reference; ENC features remain chart context."
    }
}

def iter_positions(g):
    kind, coords = g.get("type"), g.get("coordinates")
    if kind == "Point": yield coords
    elif kind in {"MultiPoint", "LineString"}: yield from coords
    elif kind in {"MultiLineString", "Polygon"}:
        for part in coords: yield from part
    elif kind == "MultiPolygon":
        for polygon in coords:
            for ring in polygon: yield from ring
    else: raise ValueError(f"Unsupported geometry type: {kind!r}")

def validate_feature(feature: dict[str, Any]) -> None:
    geometry = feature.get("geometry")
    if not isinstance(geometry, dict): raise ValueError("Feature has no geometry")
    positions = list(iter_positions(geometry))
    if not positions: raise ValueError("Feature has empty coordinates")
    for pos in positions:
        if not isinstance(pos, (list, tuple)) or len(pos) < 2: raise ValueError(f"Invalid coordinate: {pos!r}")
        lon, lat = float(pos[0]), float(pos[1])
        if not (-180 <= lon <= 180 and -90 <= lat <= 90):
            raise ValueError(f"Coordinate outside EPSG:4326 bounds: {pos!r}")

def fetch_layer(session, layer_id, bbox=None, objectids=None):
    if (bbox is None) == (objectids is None): raise ValueError("Provide exactly one of bbox or objectids")
    params = {"outFields":"*", "returnGeometry":"true", "outSR":"4326", "returnZ":"false", "returnM":"false",
              "resultOffset":0, "resultRecordCount":PAGE_SIZE, "orderByFields":"OBJECTID ASC",
              "returnExceededLimitFeatures":"true", "f":"geojson"}
    if objectids is not None: params["objectIds"] = ",".join(map(str, objectids))
    else:
        xmin,ymin,xmax,ymax = bbox
        params.update({"where":"1=1","geometry":f"{xmin},{ymin},{xmax},{ymax}",
                       "geometryType":"esriGeometryEnvelope","inSR":"4326","spatialRel":"esriSpatialRelIntersects"})
    url = f"{SERVICE}/{layer_id}/query"
    features = []
    for _ in range(MAX_PAGES):
        response = None
        for attempt in range(3):
            response = session.get(url, params=params, timeout=TIMEOUT)
            if response.status_code in {429,500,502,503,504} and attempt < 2:
                time.sleep(2 ** attempt); continue
            break
        response.raise_for_status()
        payload = response.json()
        if payload.get("error"): raise RuntimeError(f"NOAA layer {layer_id} error: {payload['error']}")
        page = payload.get("features")
        if not isinstance(page,list): raise RuntimeError(f"NOAA layer {layer_id} response has no features array")
        for feature in page: validate_feature(feature)
        features.extend(page)
        if objectids is not None or not page or (len(page) < PAGE_SIZE and not payload.get("exceededTransferLimit")): break
        params["resultOffset"] += len(page)
    else: raise RuntimeError(f"NOAA layer {layer_id} exceeded {MAX_PAGES} page limit")
    return features

def summarize(features):
    names, types, charts, dates = Counter(), Counter(), Counter(), Counter()
    ids = []
    for f in features:
        p = f.get("properties") or {}
        ids.append(p.get("OBJECTID"))
        names[str(p.get("OBJNAM") or p.get("CATSEA") or "unnamed")] += 1
        types[f["geometry"]["type"]] += 1
        if p.get("DSNM"): charts[str(p["DSNM"])] += 1
        if p.get("SORDAT"): dates[str(p["SORDAT"])] += 1
    return {"feature_count":len(features),"objectids":ids,"geometry_types":dict(types),
            "feature_name_counts":dict(names),"chart_cell_counts":dict(charts),"source_date_counts":dict(dates),
            "geometry_validation":"all returned geometries and EPSG:4326 coordinates passed"}

def write_geojson(path, name, features):
    path.write_text(json.dumps({"type":"FeatureCollection","name":name,
        "crs":{"type":"name","properties":{"name":"urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features":features},separators=(",",":"),ensure_ascii=False)+"\n",encoding="utf-8")

def run(output_dir: Path):
    output_dir.mkdir(parents=True,exist_ok=True)
    session=requests.Session()
    session.headers.update({"User-Agent":"LUPITA-Biscayne-Landmark-Reconciliation/1.0"})
    report={"report_version":1,"generated_at_utc":datetime.now(timezone.utc).isoformat(),
            "purpose":"Focused research-only source retrieval; no ecological boundaries are constructed.",
            "source_service":SERVICE,"output_crs":"EPSG:4326","landmark_references":LANDMARK_REFERENCES,
            "queries":{},"errors":{},"limitations":[
                "NOAA Harbour ENC is chart context and is not certified for navigation.",
                "Card Sound source objects retain original OBJECTIDs and chart-cell attributes; no dissolve is performed.",
                "Jewfish Creek query is localized around a tidal benchmark; features are candidates, not automatic channel identifications.",
                "Rickenbacker ENC layers remain separate source classes and do not independently define an ecological separator.",
                "No geometries are snapped, extended, bridged, or dissolved; no production model inputs are created."]}
    try:
        features=fetch_layer(session,237,objectids=CARD_SOUND_OBJECTIDS)
        returned={int((f.get("properties") or {}).get("OBJECTID")) for f in features}
        missing=sorted(set(CARD_SOUND_OBJECTIDS)-returned)
        if missing: raise RuntimeError(f"Missing exact Card Sound OBJECTIDs: {missing}")
        filename="noaa_card_sound_named_water.geojson"
        write_geojson(output_dir/filename,"noaa_card_sound_named_water",features)
        report["queries"]["card_sound_exact_objects"]={"layer_id":237,"layer_name":"Harbor.Sea_Area_Named_Water_Area",
            "requested_objectids":CARD_SOUND_OBJECTIDS,**summarize(features),"output_file":filename,"status":"complete_exact_objectid_set"}
    except Exception as exc: report["errors"]["card_sound_exact_objects"]=f"{type(exc).__name__}: {exc}"
    for region,definition in REGIONS.items():
        report["queries"][region]={"bbox_wgs84":definition["bbox"],"purpose":definition["purpose"],"layers":{}}
        for layer_id,layer_name in definition["layers"].items():
            key=f"{region}_layer_{layer_id}"
            try:
                features=fetch_layer(session,layer_id,bbox=definition["bbox"])
                filename=f"{region}_layer_{layer_id}.geojson"
                write_geojson(output_dir/filename,filename.removesuffix(".geojson"),features)
                report["queries"][region]["layers"][str(layer_id)]={"layer_name":layer_name,**summarize(features),
                    "output_file":filename,"status":"complete"}
            except Exception as exc:
                message=f"{type(exc).__name__}: {exc}"
                report["errors"][key]=message
                report["queries"][region]["layers"][str(layer_id)]={"layer_name":layer_name,"status":"unavailable","error":message}
    report["status"]="failed" if "card_sound_exact_objects" in report["errors"] else "partial" if report["errors"] else "healthy"
    (output_dir/"biscayne_landmark_extraction_summary.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return report

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,default=Path("artifacts/biscayne-landmarks"))
    args=parser.parse_args()
    try: report=run(args.output_dir)
    except Exception as exc:
        print(f"Focused landmark extraction failed: {type(exc).__name__}: {exc}",file=sys.stderr); return 1
    print(json.dumps(report,indent=2))
    return 0 if report["status"]!="failed" else 1

if __name__=="__main__": raise SystemExit(main())
