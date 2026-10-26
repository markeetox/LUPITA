"""A small, versioned, read-only API for other apps (Seabound): static JSON and PNG files under api/v1/.
Everything is relative to the API's base URL, so the files can be hosted anywhere. Changes inside v1 only ever add
fields; anything that breaks an existing field goes to a new /v2/ folder."""
from __future__ import annotations

import base64
import json
import struct
import zlib

import numpy as np

from pipeline.grid import _weights

API_VERSION = 1
HEAT_MIN = 0.45            # cells scoring below this are not drawn (same as the web map)
EDGE_CELLS = 6             # the glow fades to nothing over this many cells at the edge of the data
SCALE = 5                  # overlay pixels per grid cell: smooth on a phone without a large file

ABOUT_KEYS = ["size", "diet", "swimming_depth", "depth", "behavior", "spawning", "lifespan", "regulations_note", "regulations_link", "sources"]
ATTRIBUTION = [
    "NOAA National Data Buoy Center (buoy readings)", "NOAA CO-OPS (tide predictions)", "NOAA National Weather Service (forecasts)",
    "NASA JPL MUR sea surface temperature via NOAA CoastWatch", "NOAA CoastWatch (VIIRS chlorophyll, altimetry currents, ETOPO depth)",
    "NOAA National MPA Center (no-fishing areas)", "Florida Fish and Wildlife Conservation Commission (artificial reefs, Unified Reef Map)"]
DISCLAIMER = ("Experimental. Scores show where conditions match published habitat preferences and have not been checked against catch reports. "
              "Timing comes from angler reports. Boundaries and sea conditions are rough guides: check FWC rules, closed areas and the NWS marine forecast.")


# ---------------- heat overlay as a ready-to-draw PNG ----------------
def _rgb(hex_color: str):
    n = int(hex_color.lstrip("#"), 16)
    return np.array([(n >> 16) & 255, (n >> 8) & 255, n & 255], float)


def heat_rgba(scores: np.ndarray, color: str) -> np.ndarray:
    """Per-cell RGBA (uint8) from score bytes (0 = none, 1-100 = percent). Same look as the web map."""
    h, w = scores.shape
    v = scores / 100.0
    t = np.clip((v - HEAT_MIN) / (1 - HEAT_MIN), 0, 1)
    glow = 0.35 * t * t
    base = _rgb(color)
    rgb = base[None, None, :] + (255 - base)[None, None, :] * glow[:, :, None]
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.minimum(np.minimum(xx, yy), np.minimum(w - 1 - xx, h - 1 - yy))
    e = np.minimum(1.0, d / EDGE_CELLS)
    edge = e * e * (3 - 2 * e)
    alpha = np.where(v >= HEAT_MIN, 255 * edge * (0.12 + 0.70 * t ** 0.9), 0.0)
    return np.dstack([rgb, alpha]).clip(0, 255)


def upscale(rgba: np.ndarray, scale: int) -> np.ndarray:
    """Smooth bilinear upscale in premultiplied colour, so a glow does not get dark edges."""
    h, w, _ = rgba.shape
    a = rgba[:, :, 3] / 255.0
    pre = np.dstack([rgba[:, :, :3] * a[:, :, None], a])
    wy = _weights(np.arange(h, dtype=float), (np.arange(h * scale) + 0.5) / scale - 0.5)
    wx = _weights(np.arange(w, dtype=float), (np.arange(w * scale) + 0.5) / scale - 0.5)
    up = np.stack([wy @ pre[:, :, c] @ wx.T for c in range(4)], axis=2)
    alpha = up[:, :, 3]
    rgb = np.divide(up[:, :, :3], alpha[:, :, None], out=np.zeros_like(up[:, :, :3]), where=alpha[:, :, None] > 1e-6)
    return np.dstack([rgb, alpha * 255]).clip(0, 255).round().astype(np.uint8)


def png_bytes(rgba: np.ndarray) -> bytes:
    h, w, _ = rgba.shape
    raw = b"".join(b"\x00" + rgba[y].tobytes() for y in range(h))             # filter type 0 on every row

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def heat_png(scores_b64: str, width: int, height: int, color: str, scale: int = SCALE) -> bytes:
    scores = np.frombuffer(base64.b64decode(scores_b64), dtype=np.uint8).reshape(height, width).astype(float)
    return png_bytes(upscale(heat_rgba(scores, color), scale))


# ---------------- JSON files ----------------
def _dump(obj) -> bytes:
    return json.dumps(obj, separators=(",", ":"), allow_nan=False).encode("utf-8")


def zone_geometry(spot: dict):
    """GeoJSON geometry for the area outline."""
    if spot.get("rings"):
        return {"type": "MultiPolygon", "coordinates": [[r] for r in spot["rings"]]}
    if spot.get("ring"):
        return {"type": "Polygon", "coordinates": [spot["ring"]]}
    return None


def _image(species: dict, image_files: dict) -> dict:
    img = dict(species.get("image") or {})
    url = img.get("url") or ""
    name = url.rsplit("/", 1)[-1]
    if url.startswith("fish/") and name in image_files:
        url = f"img/{name}"                                       # the copy published alongside this API
    return {"url": url, "kind": img.get("kind", "illustration"), "credit": img.get("credit", ""), "license": img.get("license", "")}


def _area(spot: dict) -> dict:
    return {"id": spot["id"], "title": spot["title"], "score": spot["score"], "confidence": spot["confidence"],
            "coords": spot["coords"], "zone": zone_geometry(spot),
            "reasons": [{"tag": r[0], "text": r[1]} for r in spot.get("reasons", [])],
            "details": [{"label": r[0], "value": r[1]} for r in spot.get("location", [])],
            "timing": spot.get("timing"), "sea": spot.get("sea")}


def build(fish: dict, heat: dict | None, closures: dict | None, stream: dict | None, profiles: list[dict],
          image_files: dict | None = None) -> dict:
    """Everything under api/v1/ as {relative path: bytes}."""
    image_files = image_files or {}
    by_id = {p["id"]: p for p in profiles}
    heat_species = (heat or {}).get("species", {})
    files: dict = {}
    index_species = []
    for sp in fish.get("species", []):
        sid = sp["id"]
        prof = by_id.get(sid, {})
        about = {k: prof.get("profile", {}).get(k) for k in ABOUT_KEYS if prof.get("profile", {}).get(k)}
        if prof.get("timing", {}).get("note"):
            about["timing_note"] = prof["timing"]["note"]
        areas = sorted((s for s in fish.get("spots", []) if s["species"] == sid), key=lambda s: -s["score"])
        heat_info = None
        if sid in heat_species and heat:
            heat_info = {"bounds": heat["bounds"], "width": heat["width"], "height": heat["height"],
                         "png": f"heat/{sid}.png", "scores": f"heat/{sid}.json",
                         "legend": {"min_score": HEAT_MIN, "note": "Brighter means a better match. Cells below the minimum are transparent."}}
            files[f"heat/{sid}.png"] = heat_png(heat_species[sid], heat["width"], heat["height"], sp["color"])
            files[f"heat/{sid}.json"] = _dump({"width": heat["width"], "height": heat["height"], "bounds": heat["bounds"],
                                               "note": heat.get("note"), "scores_base64": heat_species[sid]})
        image = _image(sp, image_files)
        files[f"species/{sid}.json"] = _dump({
            "api_version": API_VERSION, "generated_utc": fish["generated_utc"], "id": sid, "name": sp["name"], "scientific_name": sp["sci"],
            "color": sp["color"], "image": image, "about": about,
            "today": {"status": sp["status"], "message": sp.get("message", ""), "area_count": len(areas), "areas": [_area(a) for a in areas]},
            "heat": heat_info})
        index_species.append({"id": sid, "name": sp["name"], "scientific_name": sp["sci"], "color": sp["color"], "image": image,
                              "status": sp["status"], "message": sp.get("message", ""), "area_count": len(areas),
                              "has_timing": any(a.get("timing") for a in areas), "heat": heat_info and {"png": heat_info["png"], "bounds": heat_info["bounds"]},
                              "details": f"species/{sid}.json"})
    for name, data in image_files.items():
        files[f"img/{name}"] = data
    layers = {}
    for key, name, obj in (("closures", "closures.json", closures), ("gulf_stream_edge", "stream.json", stream)):
        if obj is not None:
            files[name] = _dump(obj)
            layers[key] = name
    files["index.json"] = _dump({
        "api_version": API_VERSION, "generated_utc": fish["generated_utc"], "experimental": True, "disclaimer": DISCLAIMER,
        "region": {"name": "south_florida", "bounds": (heat or {}).get("bounds")},
        "conditions": fish.get("conditions"), "species": index_species, "layers": layers, "attribution": ATTRIBUTION})
    return files
