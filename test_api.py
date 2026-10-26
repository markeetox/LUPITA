import json
import struct
import zlib
from pathlib import Path

import numpy as np
import pytest

from pipeline import api
from pipeline.predict import build_fish_json
from tests import test_timing as T
from tests.test_predict import LATS, LONS, make_layers

ROOT = Path(__file__).resolve().parent.parent
PROFILES = list(T.PROFILES.values())


def make_files():
    L = make_layers()
    heat = {}
    now = T.dt(2026, 7, 16, 0)
    fish = build_fish_json(L, T.BUOYS, PROFILES, T.REGISTRY, now.isoformat(), T.PLACES, T.cond(now, T.dt(2026, 7, 15, 21)), heat)
    dlat, dlon = float(LATS[1] - LATS[0]), float(LONS[1] - LONS[0])
    hj = {"version": 1, "width": len(LONS), "height": len(LATS), "note": "n",
          "bounds": [float(LONS[0]) - dlon / 2, float(LATS[0]) - dlat / 2, float(LONS[-1]) + dlon / 2, float(LATS[-1]) + dlat / 2], "species": heat}
    closures = {"type": "FeatureCollection", "loaded": True, "features": []}
    stream = {"type": "FeatureCollection", "loaded": False, "features": []}
    images = {f.name: f.read_bytes() for f in sorted((ROOT / "web/fish").glob("*.png"))}
    return api.build(fish, hj, closures, stream, PROFILES, images), fish, hj


FILES, FISH, HJ = make_files()


def load(path):
    return json.loads(FILES[path].decode("utf-8"))


def decode_png(data):
    """Minimal PNG reader for the 8-bit RGBA, filter-0 files this API writes."""
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    pos, idat, w = 8, b"", None
    while pos < len(data):
        n, tag = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8: pos + 8 + n]
        assert zlib.crc32(tag + body) & 0xFFFFFFFF == struct.unpack(">I", data[pos + 8 + n: pos + 12 + n])[0]
        if tag == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", body[:10]); assert (depth, ctype) == (8, 6)
        elif tag == b"IDAT":
            idat += body
        pos += 12 + n
    raw = zlib.decompress(idat)
    rows = [raw[i * (w * 4 + 1): (i + 1) * (w * 4 + 1)] for i in range(h)]
    assert all(r[0] == 0 for r in rows)
    return np.frombuffer(b"".join(r[1:] for r in rows), dtype=np.uint8).reshape(h, w, 4)


# ---------- the files exist and point at each other ----------
def test_every_file_the_index_mentions_exists_and_all_json_is_valid():
    idx = load("index.json")
    assert idx["api_version"] == 1 and idx["generated_utc"] and idx["disclaimer"] and idx["attribution"]
    assert {s["id"] for s in idx["species"]} == {p["id"] for p in PROFILES}
    for sp in idx["species"]:
        assert sp["details"] in FILES and (sp["image"]["url"] in FILES or sp["image"]["url"].startswith("https://"))
        if sp["heat"]:
            assert sp["heat"]["png"] in FILES and len(sp["heat"]["bounds"]) == 4
    for rel in idx["layers"].values():
        assert rel in FILES
    for rel, data in FILES.items():
        if rel.endswith(".json"):
            json.loads(data.decode("utf-8"))                                   # no NaN, valid JSON


def test_species_file_has_what_an_app_needs():
    d = load("species/snook.json")
    assert d["name"] == "Common snook" and d["scientific_name"] and d["color"].startswith("#") and d["image"]["url"] == "img/snook.png"
    assert d["about"]["diet"] and d["about"]["behavior"] and d["about"]["regulations_link"].startswith("https://")
    area = d["today"]["areas"][0]
    assert {"id", "title", "score", "confidence", "coords", "zone", "reasons", "details", "timing", "sea"} <= set(area)
    assert area["zone"]["type"] in ("Polygon", "MultiPolygon") and len(area["coords"]) == 2
    assert area["reasons"][0].keys() == {"tag", "text"} and area["details"][0].keys() == {"label", "value"}
    assert area["timing"]["window"] and len(area["timing"]["scores"]) == 24
    assert [a["score"] for a in d["today"]["areas"]] == sorted((a["score"] for a in d["today"]["areas"]), reverse=True)
    assert d["today"]["area_count"] == len(d["today"]["areas"])


def test_fish_without_data_say_so_and_have_no_heat():
    d = load("species/mahi-mahi.json") if load("index.json") else None
    for sp in load("index.json")["species"]:
        s = load(f"species/{sp['id']}.json")
        assert s["today"]["status"] == sp["status"]
        if sp["status"] == "unavailable":
            assert s["today"]["areas"] == [] and s["today"]["message"]
    snook = load("species/snook.json")
    assert snook["heat"] is None                                  # snook is scored at inlets, not on the grid
    assert load("species/mahi-mahi.json")["heat"]["png"] == "heat/mahi-mahi.png"


# ---------- the overlay picture ----------
def test_heat_overlay_png_is_valid_transparent_at_the_edges_and_glows_where_scored():
    rgba = decode_png(FILES["heat/mahi-mahi.png"])
    assert rgba.shape == (len(LATS) * api.SCALE, len(LONS) * api.SCALE, 4)
    assert rgba[0, 0, 3] == 0 and rgba[-1, -1, 3] == 0                           # fades out at the edges of the data
    lon, lat = np.meshgrid(LONS, LATS)
    pocket = (lon >= -80.0) & (lat >= 25.3) & (lat <= 25.5)
    rows, cols = np.nonzero(pocket)
    i, j = int(rows.mean()), int(cols.mean())                                     # the middle of the cool, deep pocket
    px = rgba[i * api.SCALE + 2, j * api.SCALE + 2]
    assert px[3] > 60 and px[1] > px[0]                                           # visible, and green-dominant like mahi's #34d399
    assert len(FILES["heat/mahi-mahi.png"]) < 400_000


def test_upscaling_keeps_colour_and_does_not_darken_glow_edges():
    flat = np.zeros((6, 6, 4)); flat[:, :] = [52, 211, 153, 200]
    out = api.upscale(flat, 4)
    assert np.all(np.abs(out[8:16, 8:16, :3].astype(int) - [52, 211, 153]) <= 1) and np.all(np.abs(out[:, :, 3].astype(int) - 200) <= 1)
    one = np.zeros((6, 6, 4)); one[3, 3] = [200, 50, 50, 255]                        # a single lit cell on a transparent field
    soft = api.upscale(one, 4)
    edge = soft[(soft[:, :, 3] > 5) & (soft[:, :, 3] < 60)]
    assert len(edge) and np.all(np.abs(edge[:, :3].astype(int) - [200, 50, 50]) <= 3)   # faint pixels keep the colour: no dark fringe


def test_raw_scores_are_published_too_for_apps_that_draw_their_own():
    s = load("heat/mahi-mahi.json")
    raw = np.frombuffer(__import__("base64").b64decode(s["scores_base64"]), dtype=np.uint8)
    assert raw.size == s["width"] * s["height"] and raw.max() <= 100 and s["bounds"] == HJ["bounds"]


def test_images_are_copied_so_the_app_needs_only_one_host():
    assert "img/mahi-mahi.png" in FILES and FILES["img/mahi-mahi.png"][:8] == b"\x89PNG\r\n\x1a\n"
