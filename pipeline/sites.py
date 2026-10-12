"""Score named sites (inlets) for species whose habitat is thin features, not grid cells."""
from __future__ import annotations

import math
from datetime import timezone

import numpy as np

from pipeline import astro, tides
from pipeline.grid import haversine_km
from pipeline.scoring import DEFAULT_MIN_COVERAGE, MAX_SPOTS, MIN_SCORE_REPORT, season_score, trapezoid

try:
    from zoneinfo import ZoneInfo
    LOCAL = ZoneInfo("America/New_York")
except Exception:                                   # no tz database available: fall back to UTC
    LOCAL = timezone.utc

BUOY_MAX_KM, GRID_MAX_KM, TIDE_MAX_KM = 40.0, 8.0, 120.0
CLOSED_SITE_COVER = 0.5


def _clock(dt) -> str:
    return dt.astimezone(LOCAL).strftime("%I:%M %p").lstrip("0")


# ---- how each parameter is read for a site: (value, tag, info) or None ----
def sst_value(site, ctx):
    best = None
    for b in ctx["buoys"]:
        if b.get("ok") and b.get("water_temp_c") is not None and b.get("lat") is not None:
            d = haversine_km(site["lat"], site["lon"], b["lat"], b["lon"])
            if d <= BUOY_MAX_KM and (best is None or d < best[0]):
                best = (d, b)
    if best:
        d, b = best
        return b["water_temp_c"], "measured", {"text": f"{b['water_temp_c']:.1f} C ({b.get('name') or b['station']} buoy, {d:.0f} km away)"}
    L = ctx["layers"]
    if L.get("sst_c") is not None:
        lats, lons, g = L["lats"], L["lons"], L["sst_c"]
        i0, j0 = int(np.argmin(abs(lats - site["lat"]))), int(np.argmin(abs(lons - site["lon"])))
        cand = []
        for i in range(max(0, i0 - 5), min(len(lats), i0 + 6)):
            for j in range(max(0, j0 - 5), min(len(lons), j0 + 6)):
                if np.isfinite(g[i, j]):
                    d = haversine_km(site["lat"], site["lon"], float(lats[i]), float(lons[j]))
                    if d <= GRID_MAX_KM:
                        cand.append((d, float(g[i, j])))
        if cand:
            d, v = min(cand)
            return v, "modeled", {"text": f"{v:.1f} C (satellite, {d:.0f} km away)"}
    return None


def tide_value(site, ctx):
    cond = ctx.get("conditions") or {}
    best = None
    for t in cond.get("tides", []):
        d = haversine_km(site["lat"], site["lon"], t["station"]["lat"], t["station"]["lon"])
        if d <= TIDE_MAX_KM and (best is None or d < best[0]) and tides.stage_at(t["events"], cond["now"]):
            best = (d, t)
    if not best:
        return None
    d, t = best
    stage = tides.stage_at(t["events"], cond["now"])
    nxt = ", ".join(f"{'High' if e['type'] == 'H' else 'Low'} {_clock(e['time'])}" for e in tides.next_events(t["events"], cond["now"], 3))
    return stage, "modeled", {"station": t["station"]["name"],
                              "text": f"{stage.replace('_', ' ').capitalize()} at {t['station']['name']}. Next: {nxt}"}


def light_value(site, ctx):
    now = ctx["conditions"]["now"] if ctx.get("conditions") else None
    if now is None:
        return None
    phase = astro.light_phase(now, site["lat"], site["lon"])
    sr, ss = astro.sun_times(now.astimezone(LOCAL).date(), site["lat"], site["lon"])
    sun = f" Sunrise {_clock(sr)}, sunset {_clock(ss)}." if sr else ""
    return phase, "modeled", {"text": f"Now: {phase}.{sun}"}


def season_value(site, ctx):
    now = ctx["conditions"]["now"] if ctx.get("conditions") else None
    return None if now is None else (now.astimezone(LOCAL).month, "seasonal", {})


def structure_value(site, ctx):
    return site["kind"], "static", {}


VALUE_FUNCS = {"sst_c": sst_value, "tide_stage": tide_value, "time_of_day": light_value,
               "spawning_season": season_value, "season_presence": season_value, "structure_type": structure_value}


def score_value(f: dict, v):
    if f["kind"] == "range":
        if f.get("range") is None or f.get("ideal") is None:
            return None
        return float(trapezoid(np.array([float(v)]), f["range"], f["ideal"])[0])
    if f["kind"] == "category":
        if "map" in f:
            return float(f["map"].get(v, 0.0))
        return 1.0 if v in set(f.get("preferred") or []) else 0.0
    if f["kind"] == "season":
        return season_score(v, f)
    return None


def _text(f: dict, v, info: dict, reg: dict, positive: bool) -> str | None:
    vt = f.get("value_text")
    if vt:
        key = v
        if f["kind"] == "season":
            key = "peak" if v in f.get("peak_months", []) else "in_season" if v in f.get("months", []) else "off"
        if key in vt:
            return vt[key].format_map({"station": info.get("station", "the nearest station")})
    if f["kind"] == "range":
        ideal = f.get("ideal") or [None, None]
        if positive and f.get("reason_template"):
            return f["reason_template"].format(value=f"{float(v):.1f}", ideal_min=ideal[0], ideal_max=ideal[1])
        label = reg.get(f["param"], {}).get("label", f["param"])
        return f"{label} is {float(v):.1f}, outside the {ideal[0]}-{ideal[1]} range this fish prefers."
    return None


def _ring(lat, lon, radius_km, n=24):
    dlat = radius_km / 111.32
    dlon = radius_km / (111.32 * math.cos(math.radians(lat)))
    pts = [[round(lon + dlon * math.cos(2 * math.pi * k / n), 4), round(lat + dlat * math.sin(2 * math.pi * k / n), 4)] for k in range(n)]
    return pts + [pts[0]]


def score_site(profile, site, ctx, reg):
    active = [f for f in profile["factors"] if f.get("active") and f.get("weight", 0) > 0]
    total = sum(f["weight"] for f in active)
    got, missing = [], []
    for f in active:
        fn = VALUE_FUNCS.get(f["param"])
        res = fn(site, ctx) if fn else None
        s = score_value(f, res[0]) if res else None
        if res is None or s is None:
            if f.get("required"):
                return None               # e.g. no water temperature: the cold-water stop cannot be checked
            missing.append(f)
            continue
        if f.get("gate") and s <= 0:
            label = reg.get(f["param"], {}).get("label", f["param"])
            return {"gated": f"{label} is {float(res[0]):.1f}, outside the range this fish tolerates."}
        got.append((f, res[0], s, res[1], res[2]))
    avail = sum(f["weight"] for f, *_ in got)
    if not avail:
        return None
    pos, neg = [], []
    for f, v, s, tag, info in got:
        if s >= 0.6:
            t = _text(f, v, info, reg, True)
            if t:
                pos.append((f["weight"] * s, tag, t))
        elif s < 0.35:
            t = _text(f, v, info, reg, False)
            if t:
                neg.append((f["weight"] * (1 - s), tag, t))
    pos.sort(reverse=True)
    neg.sort(reverse=True)
    reasons = [[t, x] for _, t, x in pos[:5]] + [[t, x] for _, t, x in neg[:2]]
    if any(f["param"] == "tide_stage" for f in missing):
        reasons.append(["modeled", "Tide predictions could not be loaded in this update, so the score leaves the tide out."])
    rows = [[{"sst_c": "Water temp", "tide_stage": "Tide", "time_of_day": "Light"}[f["param"]], info["text"]]
            for f, v, s, tag, info in got if f["param"] in ("sst_c", "tide_stage", "time_of_day") and info.get("text")]
    return {"score": sum(f["weight"] * s for f, v, s, *_ in got) / avail, "coverage": avail / total,
            "reasons": reasons, "rows": rows, "missing": missing}


def score_sites(profile, sites, ctx, reg, closure_rows_fn=None) -> dict:
    """{'items': finished spot dicts, 'best': best score or None, 'unavailable': message or '', 'note': why nothing qualified}."""
    kinds = profile.get("site_kinds", ["inlet"])
    sites = [s for s in sites if s.get("kind") in kinds]
    if not sites:
        return {"items": [], "best": None, "unavailable": "Waiting for: site locations", "note": ""}
    min_cov = profile.get("min_coverage", DEFAULT_MIN_COVERAGE)
    cap_low = profile.get("confidence_cap") == "Low"
    scored, gated = [], []
    L = ctx["layers"]
    for site in sites:
        cell = None
        if L.get("closure_cover") is not None:
            i = int(np.clip(round((site["lat"] - L["lats"][0]) / (L["lats"][1] - L["lats"][0])), 0, len(L["lats"]) - 1))
            j = int(np.clip(round((site["lon"] - L["lons"][0]) / (L["lons"][1] - L["lons"][0])), 0, len(L["lons"]) - 1))
            cell = (i, j)
            if L["closure_cover"][i, j] >= CLOSED_SITE_COVER:
                continue                                      # inside a no-fishing zone: never offered
        r = score_site(profile, site, ctx, reg)
        if r and "gated" in r:
            gated.append(r["gated"])
            continue
        if r is None or r["coverage"] < min_cov:
            continue
        r.update(site=site, cell=cell)
        scored.append(r)
    if not scored:
        if gated:
            return {"items": [], "best": None, "unavailable": "", "note": gated[0]}
        return {"items": [], "best": None, "unavailable": "Waiting for: water temperature, tide predictions", "note": ""}
    best = max(r["score"] for r in scored)
    keep = sorted((r for r in scored if r["score"] >= profile.get("min_score_report", MIN_SCORE_REPORT)),
                  key=lambda r: -r["score"])[:profile.get("max_spots", MAX_SPOTS)]
    now = ctx["conditions"]["now"] if ctx.get("conditions") else None
    items = []
    for r in keep:
        site = r["site"]
        rows = [["Position", f"{site['lat']:.3f} N, {abs(site['lon']):.3f} W"]] + r["rows"]
        if closure_rows_fn:
            rows += closure_rows_fn(L, [r["cell"]] if r["cell"] else [])
        if now is not None:
            rows.append(["As of", f"{now.astimezone(LOCAL).strftime('%b %d, %I:%M %p').replace(' 0', ' ')} (tide and light change by the hour)"])
        conf = "Low" if (cap_low or r["coverage"] < 0.9) else "Medium"
        items.append({"title": f"{site['name']} (inlet)", "score": round(r["score"], 3), "confidence": conf,
                      "data_coverage": round(r["coverage"], 2), "coords": [site["lon"], site["lat"]],
                      "ring": _ring(site["lat"], site["lon"], site.get("radius_km", 1.5)),
                      "reasons": r["reasons"], "location": rows})
    return {"items": items, "best": best, "unavailable": "", "note": ""}
