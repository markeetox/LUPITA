"""Turn species scores into fish.json: the file the map reads."""
from __future__ import annotations

import base64

import numpy as np

from pipeline import scoring, sites as sites_mod
from pipeline.grid import bearing_deg, compass, haversine_km

TAGS = {"sst_c": "modeled", "sst_gradient": "modeled", "chlorophyll": "modeled", "depth_m": "static"}
SPEC_ROWS = [("size", "Typical size"), ("diet", "Diet"), ("swimming_depth", "Swimming depth"),
             ("depth", "Adult depth"), ("behavior", "Behavior"), ("spawning", "Spawning"),
             ("lifespan", "Lifespan")]
DIGITS = {"sst_c": 1, "chlorophyll": 2, "sst_gradient": 3, "depth_m": 0}
UNIT_TEXT = {"degC": "C", "mg/m3": "mg/m3", "m": "m"}


def _fish(name: str) -> str:
    """Species name for the middle of a sentence: 'Mutton snapper' -> 'mutton snapper', 'Atlantic tarpon' stays capitalised."""
    return (name[:1].lower() + name[1:]).replace("atlantic", "Atlantic")


def quantize_scores(score: np.ndarray) -> str:
    """Score grid -> base64 of one byte per cell (1-100 = score in percent, 0 = no score), north row first,
    which is the order an image is drawn in."""
    q = np.where(np.isfinite(score), np.clip(np.round(score * 100), 1, 100), 0).astype(np.uint8)
    return base64.b64encode(q[::-1].tobytes()).decode("ascii")


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
        when = "today" if reg.get(param, {}).get("dynamic", True) else "in this area"
        return f"{label} here is weak compared with the rest of the area {when}." if when == "today" else f"{label} here is weak compared with the rest of the area."
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


def _structures(layers: dict, members: list) -> list:
    out = []
    for c in members:
        out += layers.get("structure_info", {}).get(c, [])
    return sorted(out, key=lambda x: -float(x.get("relief_ft") or 0))


def _natural_km2(layers: dict, members: list, lats) -> float:
    cover = layers.get("structure_cover")
    if cover is None:
        return 0.0
    from pipeline.grid import cell_km2
    dlat = abs(float(lats[1] - lats[0]))
    return sum(float(cover[i, j]) * cell_km2(float(lats[i]), dlat, dlat) for i, j in members)


def structure_reasons(layers: dict, members: list, lats) -> list:
    out = []
    items = _structures(layers, members)
    if items:
        top = items[0]
        more = f" and {len(items) - 1} more nearby" if len(items) > 1 else ""
        what = top.get("material") or top["kind"].replace("_", " ")
        out.append(f"FWC lists {top['name']}{more} here ({what}), about {_ft(top.get('depth_ft'))} ft deep "
                   f"with {_ft(top.get('relief_ft'))} ft of relief.")
    km2 = _natural_km2(layers, members, lats)
    if km2 >= 0.05:
        out.append(f"FWC's Unified Reef Map shows about {km2:.1f} km2 of reef or hard bottom in this patch.")
    return out


def structure_title(layers: dict, members: list, lats) -> str:
    items = _structures(layers, members)
    if items:
        return items[0]["name"] + (f" and {len(items) - 1} more" if len(items) > 1 else "")
    return f"Natural reef or hard bottom, about {_natural_km2(layers, members, lats):.1f} km2 mapped"


def structure_rows(layers: dict, members: list, lats) -> list:
    rows = []
    for x in _structures(layers, members)[:3]:
        bits = [x.get("material") or x["kind"].replace("_", " "), f"{_ft(x.get('depth_ft'))} ft deep",
                f"{_ft(x.get('relief_ft'))} ft relief"]
        if x.get("deployed"):
            bits.append(f"deployed {x['deployed']}")
        rows.append([x["name"], ", ".join(bits)])
    km2 = _natural_km2(layers, members, lats)
    if km2 >= 0.05:
        rows.append(["Natural reef", f"About {km2:.1f} km2 mapped as reef or hard bottom (FWC Unified Reef Map v2.2, 2025)"])
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


def build_reasons(profile, name, scored, layers, cell, buoys, reg, lat, lon, members=None):
    name = _fish(name)
    i, j = cell
    pos, neg = [], []
    for f in profile["factors"]:
        p = f["param"]
        if p not in scored["scores"]:
            continue
        s = float(scored["scores"][p][i, j])
        if not np.isfinite(s):
            continue
        if f["kind"] == "season":
            vt, month = f.get("value_text") or {}, layers.get("month")
            key = "peak" if month in f.get("peak_months", []) else "in_season" if month in f.get("months", []) else "off"
            if key in vt and (s >= 0.6 or s < 0.35):
                (pos if s >= 0.6 else neg).append((f["weight"] * (s if s >= 0.6 else 1 - s), "seasonal", vt[key]))
            continue
        if f["kind"] == "category":
            if s >= 0.6 and p == "structure_type":
                for k, text in enumerate(structure_reasons(layers, members or [cell], layers["lats"])):
                    pos.append((f["weight"] * s - k * 1e-6, "static", text))
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

    names = closure_names(layers, members or [cell])
    if names:
        reasons.insert(0, ["static", f"Part of this area overlaps {', '.join(names[:2])}, where recreational fishing is prohibited. Stay outside the marked zone."])

    near = nearest_buoy(buoys, lat, lon)
    if near:
        km, b = near
        reasons.append(["measured", f"The nearest buoy ({b['station']}, {km:.0f} km away) reads {b['water_temp_c']:.1f} C water."])
    reasons += [[t, x] for _, t, x in neg[:2]]

    chl = layers.get("chlorophyll")
    if chl is None or not np.isfinite(chl[i, j]):
        reasons.append(["modeled", "No chlorophyll reading here today (cloud cover or missing scene), so this score leans on temperature and depth."])
    return reasons


CLOSED_CELL_COVER = 0.5   # cells at least this much inside a no-fishing zone are never recommended


def closure_names(layers: dict, members: list) -> list:
    seen = []
    for c in members:
        for x in layers.get("closure_info", {}).get(c, []):
            if x["name"] not in seen:
                seen.append(x["name"])
    return seen


def closure_rows(layers: dict, members: list) -> list:
    if not layers.get("closure_checked"):
        return [["No-fishing check", "Could not be checked in this update. Confirm closed areas before you fish."]]
    names = closure_names(layers, members)
    if names:
        more = f" and {len(names) - 3} more" if len(names) > 3 else ""
        return [["No-fishing zone", "Overlaps or borders " + ", ".join(names[:3]) + more + ". Stay outside the marked zone."]]
    return [["No-fishing zones", "None mapped here (NOAA MPA Inventory, 2023 edition)"]]


def place_row(places, lat, lon):
    """'About 8.2 nm ESE of Government Cut' for the nearest reference place, or None."""
    if not places:
        return None
    km, p = min(((haversine_km(lat, lon, q["lat"], q["lon"]), q) for q in places), key=lambda t: t[0])
    return ["Nearest inlet", f"About {km / 1.852:.1f} nm {compass(bearing_deg(p['lat'], p['lon'], lat, lon))} of {p['name']} (approximate)"]


def build_location(layers, scored, cell, buoys, lat, lon, members=None, places=None):
    i, j = cell
    rows = [["Position", f"{lat:.3f} N, {abs(lon):.3f} W"]]
    pr = place_row(places, lat, lon)
    if pr:
        rows.append(pr)
    depth = layers.get("depth_m")
    if depth is not None and np.isfinite(depth[i, j]):
        rows.append(["Water depth", f"About {depth[i, j]:.0f} m"])
    rows += closure_rows(layers, members or [cell])
    rows += structure_rows(layers, members or [cell], layers["lats"])
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


def species_image(profile: dict) -> dict:
    """The picture for a species popup: its photo if one is configured, otherwise the built-in illustration."""
    img = profile.get("image") or {}
    if img.get("url"):
        return {"url": img["url"], "kind": img.get("kind", "photo"), "credit": img.get("credit") or "", "license": img.get("license") or ""}
    return {"url": f"fish/{profile['id']}.png", "kind": "illustration", "credit": "Original illustration", "license": ""}


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


def build_fish_json(layers, buoys, profiles, registry, generated_utc, places=None, conditions=None, heat=None):
    reg = {p["key"]: p for p in registry["parameters"]}
    if conditions:
        layers = {**layers, "month": conditions["now"].astimezone(sites_mod.LOCAL).month}   # for seasonal factors
    lats, lons = layers["lats"], layers["lons"]
    species_out, spots_out = [], []
    for profile in profiles:
        sid, name = profile["id"], profile["common_name"]
        entry = {"id": sid, "name": name, "sci": profile["scientific_name"],
                 "color": profile.get("display", {}).get("color", "#ffffff"),
                 "specs": _specs(profile), "image": species_image(profile), "status": "ok", "message": "", "spots": 0}
        if profile.get("model") == "sites":
            ctx = {"layers": layers, "buoys": buoys, "conditions": conditions}
            res = sites_mod.score_sites(profile, places or [], ctx, reg, closure_rows)
            if res["unavailable"]:
                entry.update(status="unavailable", message=res["unavailable"])
            elif not res["items"]:
                msg = "No favorable inlets right now."
                if res["note"]:
                    msg += " " + res["note"]
                elif res["best"] is not None:
                    msg += f" The best score was {res['best']:.0%}."
                entry.update(status="no_favorable_areas", message=msg)
            else:
                for k, it in enumerate(res["items"], 1):
                    it.update(id=f"{sid}-{k}", species=sid)
                    spots_out.append(it)
                entry["spots"] = len(res["items"])
            species_out.append(entry)
            continue
        scored = scoring.score_species(profile, layers)
        if scored["status"] != "ok":
            entry.update(status="unavailable", message=scored["message"])
            species_out.append(entry)
            continue
        cc = layers.get("closure_cover")
        if cc is not None:                                   # never recommend cells that are mostly inside a no-fishing zone
            scored["score"] = np.where(cc >= CLOSED_CELL_COVER, np.nan, scored["score"])
        if heat is not None:                                   # the full score surface, for the map's heat layer
            heat[sid] = quantize_scores(scored["score"])
        style = profile.get("zone_style", "hull")
        spots, best = scoring.find_spots(scored["score"], lats, lons, min_cells=profile.get("min_cells", scoring.MIN_CELLS),
                                         max_spots=profile.get("max_spots", scoring.MAX_SPOTS), zone_style=style,
                                         block_cells=profile.get("patch_block_cells"))
        if not spots:
            msg = "No favorable areas right now." + (f" The best score was {best:.0%}." if best is not None else "")
            entry.update(status="no_favorable_areas", message=msg + _cold_hint(profile, scored, layers))
            species_out.append(entry)
            continue
        for k, sp in enumerate(spots, 1):
            i, j = sp["cell"]
            lat, lon = float(lats[i]), float(lons[j])
            cov = float(scored["coverage"][i, j])
            title = (structure_title(layers, sp["members"], lats) if profile.get("title_from") == "structure"
                     else f"Favorable area, about {sp['area_km2']:.0f} km2")
            item = {
                "id": f"{sid}-{k}", "species": sid, "title": title,
                "score": round(sp["score"], 3),
                "confidence": "Low" if (cov < 0.9 or profile.get("confidence_cap") == "Low") else "Medium",
                "data_coverage": round(cov, 2), "coords": [round(lon, 4), round(lat, 4)],
                "reasons": build_reasons(profile, name, scored, layers, (i, j), buoys, reg, lat, lon, sp["members"]),
                "location": build_location(layers, scored, (i, j), buoys, lat, lon, sp["members"], places)}
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
