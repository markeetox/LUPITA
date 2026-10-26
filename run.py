"""Full pipeline: buoys + satellite layers -> scores -> data/live/latest.json and fish.json."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from pipeline import closures as closures_mod
from pipeline import api as api_mod, currents, seastate, timing, weather
from pipeline.conditions import load_conditions
from pipeline.layers import load_layers
from pipeline.predict import build_fish_json
from pipeline.run_v1 import pull_buoys, summarize_grid

ROOT = Path(__file__).resolve().parent.parent
log = logging.getLogger("run")


FORECAST_POINT = (25.76, -80.19)      # Miami: one point is enough to see a front coming across South Florida


def load_forecast(errors: list[str]):
    """NWS hourly forecast as observations, or None if it could not be fetched."""
    try:
        return weather.parse_nws_hourly(weather.fetch_forecast(*FORECAST_POINT))
    except Exception as exc:
        errors.append(f"weather forecast: {exc}")
        return None


def _grid_report(cfg: dict, when, lats, lons, grid) -> dict:
    out = {"parameter": cfg["parameter"], "dataset": cfg["dataset"], "time": when,
           "gradient_unit": cfg.get("gradient_unit"), "shape": [int(len(lats)), int(len(lons))]}
    out.update(summarize_grid(grid, lats, lons, cfg.get("log_scale", False), cfg.get("gradient_min", 0.0)))
    return out


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    stations = json.loads((ROOT / "config/stations.json").read_text())["stations"]
    sources = json.loads((ROOT / "config/sources.json").read_text())
    registry = json.loads((ROOT / "data/parameters.json").read_text())
    places_file = ROOT / "config/places.json"
    places = json.loads(places_file.read_text())["places"] if places_file.exists() else []
    profiles = [json.loads(p.read_text()) for p in sorted((ROOT / "data/species").glob("*.json"))]
    errors: list[str] = []
    now_dt = datetime.now(timezone.utc)
    now = now_dt.isoformat()
    tides_file = ROOT / "config/tides.json"
    tide_stations = json.loads(tides_file.read_text())["stations"] if tides_file.exists() else []

    history: dict = {}
    buoys = pull_buoys(stations, sources["ndbc"]["realtime_url"], errors, history)
    layers = load_layers(sources, errors)
    conditions = load_conditions(tide_stations, now_dt, errors)
    forecast = load_forecast(errors)
    conditions["forecast"] = forecast
    conditions["front"] = weather.assess(history, forecast, now_dt)

    sst = chl = None
    fish = None
    heat_json = None
    if layers is None:
        errors.append("kept the last published predictions: satellite temperature could not be loaded")
    else:
        cfg = sources["erddap"]
        sst = _grid_report(cfg["sst"], layers["times"]["sst"], layers["lats"], layers["lons"], layers["sst_c"])
        if layers["chl_raw"] is not None:
            clats, clons, cgrid = layers["chl_raw"]
            chl = _grid_report(cfg["chlorophyll"], layers["times"]["chlorophyll"], clats, clons, cgrid)
        heat: dict = {}
        fish = build_fish_json(layers, buoys, profiles, registry, now, places, conditions, heat)
        la, lo = layers["lats"], layers["lons"]
        dlat, dlon = float(la[1] - la[0]), float(lo[1] - lo[0])
        heat_json = {"version": 1, "generated_utc": now, "width": int(len(lo)), "height": int(len(la)),
                     "bounds": [round(float(lo[0]) - dlon / 2, 4), round(float(la[0]) - dlat / 2, 4),
                                round(float(lo[-1]) + dlon / 2, 4), round(float(la[-1]) + dlat / 2, 4)],
                     "note": "One byte per cell, north row first: 0 = no score, 1-100 = score in percent.", "species": heat}

    cl_cfg = sources.get("closures", {})
    cl_loaded = bool(layers and layers.get("closure_checked"))
    cl_json = closures_mod.to_geojson((layers or {}).get("closure_areas", []), cl_cfg.get("source_label", "NOAA MPA Inventory"), cl_loaded, now)

    live = ROOT / "data/live"
    live.mkdir(parents=True, exist_ok=True)
    latest = {"generated_utc": now, "region": sources["region"]["name"], "buoys": buoys,
              "sst": sst, "chlorophyll": chl, "structure": (layers or {}).get("structure_stats"),
              "closures": {"loaded": cl_loaded, "areas": len(cl_json["features"])},
              "conditions": {**timing.summary(conditions), "sea": seastate.summary(buoys, conditions)}, "fish_updated": fish is not None, "errors": errors}
    (live / "latest.json").write_text(json.dumps(latest, indent=2, allow_nan=False))
    if fish is not None:      # on a failed run these are not written, so the last good copies stay published
        (live / "fish.json").write_text(json.dumps(fish, indent=1, allow_nan=False))
        (live / "closures.json").write_text(json.dumps(cl_json, allow_nan=False, separators=(",", ":")))
        stream = currents.stream_geojson(layers.get("stream_edge_lon"), layers["lats"], "NOAA CoastWatch nesdisSSH1day (satellite altimetry)",
                                         layers["times"].get("currents"), layers.get("current_speed") is not None, now)
        (live / "stream.json").write_text(json.dumps(stream, allow_nan=False, separators=(",", ":")))
        images = {f.name: f.read_bytes() for f in sorted((ROOT / "web/fish").glob("*.png"))}
        for rel, data in api_mod.build(fish, heat_json, cl_json, stream, profiles, images).items():
            dest = live / "api" / "v1" / rel                     # the app-facing copy: see docs/seabound-api.md
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        (live / "heat.json").write_text(json.dumps(heat_json, allow_nan=False, separators=(",", ":")))

    for sp in (fish or {}).get("species", []):
        log.info("%-20s %-20s %s", sp["name"], sp["status"], sp["message"] or f"{sp['spots']} area(s)")
    log.info("wrote latest.json%s (%d errors)", " and fish.json" if fish is not None else "; fish.json left as it was", len(errors))


if __name__ == "__main__":
    main()
