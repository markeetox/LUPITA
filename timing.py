"""Bite timing: how likely a fish is to be feeding at each moment over the next 24 hours, and the best window.
Separate from habitat match (where the fish lives). Components: light, tide, moon, cold front."""
from __future__ import annotations

from datetime import timedelta

from pipeline import astro, moon, tides, weather
from pipeline.grid import haversine_km
from pipeline.sites import LOCAL

DEFAULT_WEIGHTS = {"light": 0.40, "tide": 0.30, "moon": 0.15, "front": 0.15}
STEP = timedelta(minutes=30)
STEPS = 48                      # 24 hours
TIDE_MAX_KM = 120.0
MIN_SPREAD = 0.12               # if the best and worst moments differ by less than this, there is no clear window
MAX_WINDOW_STEPS = 6            # at most 3 hours


def _tide(lat, lon, conditions, t):
    best = None
    for tt in conditions.get("tides", []):
        d = haversine_km(lat, lon, tt["station"]["lat"], tt["station"]["lon"])
        if d <= TIDE_MAX_KM and (best is None or d < best[0]) and tides.stage_at(tt["events"], t):
            best = (d, tt)
    if not best:
        return None, None
    return tides.stage_at(best[1]["events"], t), best[1]["station"]["name"]


def components(cfg: dict, t, lat: float, lon: float, conditions: dict) -> dict:
    """{component: (score 0-1, text or None)} for the parts of cfg that have information at time t."""
    out = {}
    c = cfg.get("light")
    if c:
        ph = astro.light_phase(t, lat, lon)
        if ph in c["map"]:
            out["light"] = (c["map"][ph], (c.get("text") or {}).get(ph))
    c = cfg.get("tide")
    if c:
        stage, station = _tide(lat, lon, conditions, t)
        if stage in c["map"]:
            out["tide"] = (c["map"][stage], ((c.get("text") or {}).get(stage) or "").format_map({"station": station}) or None)
    c = cfg.get("moon")
    if c and t.astimezone(LOCAL).month in c.get("months", range(1, 13)):
        inside = c["from_days"] <= moon.days_from_full(t) <= c["to_days"]
        out["moon"] = (c["in_score"] if inside else c["out_score"], c.get("text") if inside else None)
    c = cfg.get("front")
    if c:
        st = weather.front_state_at((conditions.get("front") or {}).get("front_time"), t)
        if st != "none" and st in c["map"]:
            out["front"] = (c["map"][st], (c.get("text") or {}).get(st))
    return out


def score_at(cfg, t, lat, lon, conditions):
    comps = components(cfg, t, lat, lon, conditions)
    if not comps:
        return None, comps
    w = {**DEFAULT_WEIGHTS, **(cfg.get("weights") or {})}
    tot = sum(w[k] for k in comps)
    return sum(w[k] * s for k, (s, _) in comps.items()) / tot, comps


def timeline(cfg, lat, lon, conditions, start):
    return [(start + STEP * i, *score_at(cfg, start + STEP * i, lat, lon, conditions)) for i in range(STEPS)]


def best_window(steps):
    """(start, end, middle components) of the best stretch, or None when there is no clear best time."""
    scores = [s for _, s, _ in steps]
    if any(s is None for s in scores):
        return None
    mx, mn = max(scores), min(scores)
    if mx - mn < MIN_SPREAD:
        return None
    smooth = [(scores[i] + scores[min(i + 1, len(scores) - 1)]) / 2 for i in range(len(scores))]
    i0 = smooth.index(max(smooth))
    lo = hi = i0
    while lo > 0 and scores[lo - 1] >= mx - 0.10 and hi - lo + 1 < MAX_WINDOW_STEPS:
        lo -= 1
    while hi < len(scores) - 1 and scores[hi + 1] >= mx - 0.10 and hi - lo + 1 < MAX_WINDOW_STEPS:
        hi += 1
    return steps[lo][0], steps[hi][0] + STEP, steps[(lo + hi) // 2][2], round(mx, 3)


def for_spot(profile: dict, lat: float, lon: float, conditions: dict):
    """The timing block for one map spot, or None if this fish has no timing information."""
    cfg = profile.get("timing")
    now = conditions.get("now") if conditions else None
    if not cfg or now is None:
        return None
    steps = timeline(cfg, lat, lon, conditions, now)
    if all(s is None for _, s, _ in steps):
        return None
    win = best_window(steps)
    why = []
    if win:
        why = [text for _, (s, text) in win[2].items() if text and s >= 0.8]
    return {
        "start": now.isoformat(), "step_min": 60,
        "scores": [0 if steps[i][1] is None else round(steps[i][1] * 100) for i in range(0, STEPS, 2)],
        "window": {"start": win[0].isoformat(), "end": win[1].isoformat(), "score": win[3]} if win else None,
        "why": why, "evidence": cfg.get("status", "angler_lore"),
        "note": "" if win else "Conditions look about the same all day, so no single time stands out."}


def context_rows(conditions: dict) -> list:
    """Moon and cold-front rows for the popup."""
    now = conditions["now"]
    rows = [["Moon", moon.describe(now)]]
    t = weather.front_text(conditions.get("front") or {"front_time": None, "state": "none"}, now)
    if t:
        rows.append(["Weather", t])
    return rows


def summary(conditions: dict) -> dict:
    now = conditions["now"]
    f = conditions.get("front") or {}
    return {"moon": {"illumination": round(moon.illumination(now), 3), "phase": moon.phase_name(now), "text": moon.describe(now)},
            "front": {"state": f.get("state", "none"), "source": f.get("source"),
                      "time": f["front_time"].isoformat() if f.get("front_time") else None,
                      "text": weather.front_text(f, now) if f else None}}
