"""Turn species scores into fish.json: the file the map reads."""
from __future__ import annotations

import numpy as np

from pipeline import scoring
from pipeline.grid import haversine_km

TAGS = {"sst_c": "modeled", "sst_gradient": "modeled", "chlorophyll": "modeled", "depth_m": "static"}
SPEC_ROWS = [("size", "Typical size"), ("diet", "Diet"), ("swimming_depth", "Swimming depth"),
             ("depth", "Adult depth"), ("behavior", "Behavior"), ("spawning", "Spawning"),
             ("lifespan", "Lifespan")]
DIGITS = {"sst_c": 1, "chlorophyll": 2, "sst_gradient": 3, "depth_m": 0}
UNIT_TEXT = {"degC": "C", "mg/m3": "mg/m3", "m": "m"}


def _fmt(param: str, v: float) -> str:
    return f"{float(v):.{DIGITS.get(param, 1)}f}"


def _fill(template: str, param: str, value: float, f: dict) -> str:
    ideal = f.get("ideal") or [None, None]
    try:
        return template.format(value=_fmt(param, value), per10km=f"{float(value) * 10:.1f}",
                               ideal_min=ideal[0], ideal_max=ideal[1])
    except (KeyError, IndexError):
        return template


def _caveat(name: str, param: str, value: float, f: dict, reg: dict) -> str:
    label = reg.get(param, {}).get("label", param)
    if f["kind"] == "higher_is_better":
        return f"{label} here is weak compared with the rest of the area today."
    unit = UNIT_TEXT.get(reg.get(param, {}).get("unit"), reg.get(param, {}).get("unit") or "")
    lo, hi = f["ideal"]
    return f"{label} is {_fmt(param, value)} {unit}, outside the {lo}-{hi} {unit} range {name} prefer."


def _near_edge(name: str, param: str, value: float, f: dict, reg: dict) -> str:
    label = reg.get(param, {}).get("label", param)
    unit = UNIT_TEXT.get(reg.get(param, {}).get("unit"), reg.get(param, {}).get("unit") or "")
    lo, hi = f["ideal"]
    side = "above" if value > hi else "below"
    return f"{label} is {_fmt(param, value)} {unit}, just {side} the {lo}-{hi} {unit} sweet spot for {name}, so it still scores well."


def _ft(v) -> str:
    return "unknown" if v is None else f"{float(v):.0f}"


def structure_reason(layers: dict, cell: tuple):
    i, j = cell
    info = layers.get("structure_info", {}).get(cell)
    if info:
        top = max(info, key=lambda x: float(x.get("relief_ft") or 0))
        more = f" and {len(info) - 1} more" if len(info) > 1 else ""
        what = top.get("material") or top["kind"].replace("_", " ")
        return (f"FWC lists {top['name']}{more} here ({what}), about {_ft(top.get('depth_ft'))} ft deep "
                f"with {_ft(top.get('relief_ft'))} ft of relief.")
    cover = layers.get("structure_cover")
    if cover is not None and cover[i, j] > 0:
        return f"FWC's Unified Reef Map shows reef or hard bottom across about {cover[i, j]:.0%} of this area."
    return None


def structure_title(layers: dict, cell: tuple, members: list, lats) -> str:
    info = layers.get("structure_info", {}).get(cell)
    if info:
        top = max(info, key=lambda x: float(x.get("relief_ft") or 0))
        return top["name"] + (f" and {len(info) - 1} more" if len(info) > 1 else "")
    cover = layers.get("structure_cover")
    dlat = abs(float(lats[1] - lats[0]))
    km2 = 0.0
    if cover is not None:
        from pipeline.grid import cell_km2
        km2 = sum(float(cover[i, j]) * cell_km2(float(lats[i]), dlat, dlat) for i, j in members)
    return f"Natural reef or hard bottom, about {km2:.1f} km2 mapped"


def structure_rows(layers: dict, cell: tuple) -> list:
    i, j = cell
    rows = []
    for x in (layers.get("structure_info", {}).get(cell) or [])[:3]:
        bits = [x.get("material") or x["kind"].replace("_", " "), f"{_ft(x.get('depth_ft'))} ft deep",
                f"{_ft(x.get('relief_ft'))} ft relief"]
        if x.get("deployed"):
            bits.append(f"deployed {x['deployed']}")
        rows.append([x["name"], ", ".join(bits)])
    cover = layers.get("structure_cover")
    if cover is not None and cover[i, j] > 0:
        rows.append(["Natural reef", f"{cover[i, j]:.0%} of this area mapped as coral or hard bottom (FWC Unified Reef Map v2.2, 2025)"])
    return rows


def nearest_buoy(buoys: list[dict], lat: float, lon: float, max_km: float = 60.0):
    best = None
    for b in buoys:
        if not b.get("ok") or b.get("water_temp_c") is None or b.get("lat") is None:
            continue
        d = haversine_km(lat, lon, b["lat"], b["lon"])
        if d <= max_km and (best is None or d < best[0]):
            best = (d, b)
    return best


def build_reasons(profile, name, scored, layers, cell, buoys, reg, lat, lon):
    i, j = cell
    pos, neg = [], []
    for f in profile["factors"]:
        p = f["param"]
        if p not in scored["scores"]:
            continue
        s = float(scored["scores"][p][i, j])
        if not np.isfinite(s):
            continue
        if f["kind"] == "category":
            text = structure_reason(layers, cell) if p == "structure_type" else None
            if s >= 0.6 and text:
                pos.append((f["weight"] * s, "static", text))
            continue
        v = layers[p][i, j]
        tag, w = TAGS.get(p, "modeled"), f["weight"]
        ideal = f.get("ideal")
        outside = (f["kind"] == "range" and ideal is not None and ideal[0] is not None and ideal[1] is not None
                   and (v < ideal[0] or v > ideal[1]))
        if s >= 0.6 and outside:
            pos.append((w * s, tag, _near_edge(name, p, v, f, reg)))
        elif s >= 0.6 and f.get("reason_template"):
            pos.append((w * s, tag, _fill(f["reason_template"], p, v, f)))
        elif s < 0.35:
            neg.append((w * (1 - s), tag, _caveat(name, p, v, f, reg)))
    pos.sort(reverse=True)
    neg.sort(reverse=True)
    reasons = [[t, x] for _, t, x in pos[:4]]

    near = nearest_buoy(buoys, lat, lon)
    if near:
        km, b = near
        reasons.append(["measured", f"The nearest buoy ({b['station']}, {km:.0f} km away) reads {b['water_temp_c']:.1f} C water."])
    reasons += [[t, x] for _, t, x in neg[:2]]

    chl = layers.get("chlorophyll")
    if chl is None or not np.isfinite(chl[i, j]):
        reasons.append(["modeled", "No chlorophyll reading here today (cloud cover or missing scene), so this score leans on temperature and depth."])
    return reasons


def build_location(layers, scored, cell, buoys, lat, lon):
    i, j = cell
    rows = []
    depth = layers.get("depth_m")
    if depth is not None and np.isfinite(depth[i, j]):
        rows.append(["Water depth", f"About {depth[i, j]:.0f} m"])
    rows += structure_rows(layers, cell)
    sst_t = (layers["times"].get("sst") or "")[:10]
    rows.append(["Surface temp", f"{layers['sst_c'][i, j]:.1f} C (satellite, {sst_t})"])
    chl = layers.get("chlorophyll")
    if chl is not None and np.isfinite(chl[i, j]):
        rows.append(["Chlorophyll", f"{chl[i, j]:.2f} mg/m3 ({(layers['times'].get('chlorophyll') or '')[:10]})"])
    else:
        rows.append(["Chlorophyll", "No reading (cloud or no scene)"])
    ref = scored["ref"].get("sst_gradient")
    g = layers["sst_gradient"][i, j]
    if ref and np.isfinite(g):
        ratio = g / ref
        rows.append(["Temp. break", "Strong" if ratio >= 0.75 else "Moderate" if ratio >= 0.35 else "Weak"])
    near = nearest_buoy(buoys, lat, lon)
    if near:
        km, b = near
        rows.append(["Nearest buoy", f"{b.get('name') or b['station']}: {b['water_temp_c']:.1f} C, {km:.0f} km away"])
    return rows


def _specs(profile: dict) -> list[list[str]]:
    p = profile.get("profile", {})
    return [[label, p[key]] for key, label in SPEC_ROWS if p.get(key)]


def _cold_hint(profile, scored, layers) -> str:
    """One-line reason when nothing is favorable, based on the most heavily weighted factor."""
    top = max((f for f in profile["factors"] if f["param"] in scored["scores"]), key=lambda f: f["weight"], default=None)
    if not top:
        return ""
    s, depth = scored["scores"][top["param"]], layers.get("depth_m")
    ok = np.isfinite(s)
    if depth is not None:
        ok &= np.isfinite(depth) & (depth >= scoring.OFFSHORE_MIN_DEPTH_M)
    if ok.sum() and float(np.nanmedian(s[ok])) < 0.3:
        return f" Most offshore cells are outside the preferred range for {top['param'].replace('_', ' ')} today."
    return ""


def build_fish_json(layers, buoys, profiles, registry, generated_utc):
    reg = {p["key"]: p for p in registry["parameters"]}
    lats, lons = layers["lats"], layers["lons"]
    species_out, spots_out = [], []
    for profile in profiles:
        sid, name = profile["id"], profile["common_name"]
        entry = {"id": sid, "name": name, "sci": profile["scientific_name"],
                 "color": profile.get("display", {}).get("color", "#ffffff"),
                 "specs": _specs(profile), "status": "ok", "message": "", "spots": 0}
        scored = scoring.score_species(profile, layers)
        if scored["status"] != "ok":
            entry.update(status="unavailable", message=scored["message"])
            species_out.append(entry)
            continue
        style = profile.get("zone_style", "hull")
        spots, best = scoring.find_spots(scored["score"], lats, lons, min_cells=profile.get("min_cells", scoring.MIN_CELLS),
                                         max_spots=profile.get("max_spots", scoring.MAX_SPOTS), zone_style=style)
        if not spots:
            msg = "No favorable areas right now." + (f" The best score was {best:.0%}." if best is not None else "")
            entry.update(status="no_favorable_areas", message=msg + _cold_hint(profile, scored, layers))
            species_out.append(entry)
            continue
        for k, sp in enumerate(spots, 1):
            i, j = sp["cell"]
            lat, lon = float(lats[i]), float(lons[j])
            cov = float(scored["coverage"][i, j])
            title = (structure_title(layers, (i, j), sp["members"], lats) if profile.get("title_from") == "structure"
                     else f"Favorable area, about {sp['area_km2']:.0f} km2")
            item = {
                "id": f"{sid}-{k}", "species": sid, "title": title,
                "score": round(sp["score"], 3), "confidence": "Medium" if cov >= 0.9 else "Low",
                "data_coverage": round(cov, 2), "coords": [round(lon, 4), round(lat, 4)],
                "reasons": build_reasons(profile, name, scored, layers, (i, j), buoys, reg, lat, lon),
                "location": build_location(layers, scored, (i, j), buoys, lat, lon)}
            if "rings" in sp:
                item["rings"] = [[[round(x, 4), round(y, 4)] for x, y in r] for r in sp["rings"]]
            else:
                item["ring"] = [[round(x, 4), round(y, 4)] for x, y in sp["ring"]]
            spots_out.append(item)
        entry["spots"] = len(spots)
        species_out.append(entry)
    return {
        "version": 1, "generated_utc": generated_utc, "experimental": True,
        "disclaimer": "Scores show where conditions match published habitat preferences. They have not yet been checked against catch reports.",
        "layers": {"times": layers["times"], "datasets": layers["datasets"]},
        "species": species_out, "spots": spots_out}
