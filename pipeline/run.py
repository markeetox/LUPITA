"""Full pipeline: buoys + satellite layers -> scores -> data/live/latest.json and fish.json."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from pipeline.layers import load_layers
from pipeline.predict import build_fish_json
from pipeline.run_v1 import pull_buoys, summarize_grid

ROOT = Path(__file__).resolve().parent.parent
log = logging.getLogger("run")


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
    now = datetime.now(timezone.utc).isoformat()

    buoys = pull_buoys(stations, sources["ndbc"]["realtime_url"], errors)
    layers = load_layers(sources, errors)

    sst = chl = None
    fish = {"version": 1, "generated_utc": now, "experimental": True, "species": [], "spots": [],
            "error": "Satellite temperature could not be loaded."}
    if layers is not None:
        cfg = sources["erddap"]
        sst = _grid_report(cfg["sst"], layers["times"]["sst"], layers["lats"], layers["lons"], layers["sst_c"])
        if layers["chl_raw"] is not None:
            clats, clons, cgrid = layers["chl_raw"]
            chl = _grid_report(cfg["chlorophyll"], layers["times"]["chlorophyll"], clats, clons, cgrid)
        fish = build_fish_json(layers, buoys, profiles, registry, now, places)

    live = ROOT / "data/live"
    live.mkdir(parents=True, exist_ok=True)
    latest = {"generated_utc": now, "region": sources["region"]["name"], "buoys": buoys,
              "sst": sst, "chlorophyll": chl, "structure": (layers or {}).get("structure_stats"), "errors": errors}
    (live / "latest.json").write_text(json.dumps(latest, indent=2, allow_nan=False))
    (live / "fish.json").write_text(json.dumps(fish, indent=1, allow_nan=False))

    for s in fish["species"]:
        log.info("%-20s %-20s %s", s["name"], s["status"], s["message"] or f"{s['spots']} area(s)")
    log.info("wrote latest.json and fish.json (%d errors)", len(errors))


if __name__ == "__main__":
    main()
