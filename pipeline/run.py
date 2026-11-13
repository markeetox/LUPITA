"""Full pipeline: buoys + satellite layers -> scores -> data/live/latest.json and fish.json."""
from __future__ import annotations

import json
import logging

import numpy as np
from datetime import datetime, timezone
from pathlib import Path

from pipeline import catalog
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



def _layer_state(enabled: bool, present: bool, errors: list[str], prefix: str | list[str]) -> dict:
    """Report source state without treating missing data as a measured zero."""
    prefixes = [prefix] if isinstance(prefix, str) else prefix
    matching = [item for item in errors if any(item.startswith(item_prefix) for item_prefix in prefixes)]
    if not enabled:
        status = "disabled"
    elif present and matching:
        status = "partial"
    elif present:
        status = "loaded"
    elif matching:
        status = "failed"
    else:
        status = "unavailable"
    result = {"status": status}
    if matching:
        result["errors"] = matching
    return result


def _source_freshness(observed_at: str | None, policy: dict | None, now: datetime | None = None) -> dict:
    """Measure source age against explicit operational thresholds; never infer missing timestamps."""
    policy = policy or {}
    warning, stale = policy.get("warning_age_hours"), policy.get("stale_age_hours")
    result = {"observed_at": observed_at, "warning_age_hours": warning, "stale_age_hours": stale,
              "threshold_basis": policy.get("basis")}
    if not observed_at:
        result.update(status="unknown", age_hours=None)
        return result
    if warning is None or stale is None or float(warning) < 0 or float(stale) <= float(warning):
        result.update(status="unconfigured", age_hours=None)
        return result
    try:
        observed = datetime.fromisoformat(str(observed_at).replace("Z", "+00:00"))
        if observed.tzinfo is None:
            observed = observed.replace(tzinfo=timezone.utc)
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc)
        age = (current.astimezone(timezone.utc) - observed.astimezone(timezone.utc)).total_seconds() / 3600
    except (TypeError, ValueError, OverflowError):
        result.update(status="unknown", age_hours=None, timestamp_error="unparseable_observation_time")
        return result
    result["age_hours"] = round(age, 2)
    result["status"] = ("future" if age < -0.25 else "fresh" if age <= float(warning)
                        else "delayed" if age <= float(stale) else "stale")
    return result


def build_data_quality(layers: dict | None, sources: dict, errors: list[str], now: datetime | None = None) -> dict:
    """Create additive, machine-readable diagnostics for each environmental input."""
    cfg = sources.get("erddap", {})
    arc = sources.get("arcgis", {})
    layers_not_loaded = layers is None
    downstream_not_attempted = layers_not_loaded and any(item.startswith("layers sst:") for item in errors)
    layers = layers or {}
    sst = layers.get("sst_c")
    chl_info = layers.get("chlorophyll_info") or {}
    bathy_info = layers.get("bathymetry_info") or {}
    current_present = layers.get("current_speed") is not None
    structure_present = layers.get("structure_stats") is not None
    habitat_present = bool(layers.get("habitat_info"))
    closure_present = bool(layers.get("closure_checked"))

    sst_state = _layer_state(bool(cfg.get("sst", {}).get("enabled")), sst is not None, errors, "layers sst:")
    if sst is not None:
        sst_state.update({"dataset": cfg.get("sst", {}).get("dataset"),
                          "grid_shape": [int(sst.shape[0]), int(sst.shape[1])],
                          "valid_fraction": round(float(np.isfinite(sst).mean()), 6),
                          "time": layers.get("times", {}).get("sst"),
                          "freshness": _source_freshness(layers.get("times", {}).get("sst"), cfg.get("sst", {}).get("freshness"), now)})

    chl_state = _layer_state(bool(cfg.get("chlorophyll", {}).get("enabled") or cfg.get("chlorophyll_gapfilled", {}).get("enabled")), bool(chl_info.get("primary_loaded") or chl_info.get("gapfilled_used")), errors, ["layers chlorophyll:", "layers chlorophyll_gapfilled:"])
    chl_state.update({key: value for key, value in chl_info.items() if key != "status"})
    if downstream_not_attempted:
        chl_state.update(status="not_attempted", not_attempted_reason="Required SST grid unavailable; downstream gridded layers were not requested.")
        chl_state["freshness"] = {"status": "not_assessed", "observed_at": None, "age_hours": None}
    else:
        chl_state["freshness"] = _source_freshness(chl_info.get("time") or chl_info.get("primary_time") or layers.get("times", {}).get("chlorophyll"), cfg.get("chlorophyll", {}).get("freshness"), now)
    if chl_info.get("primary_time"):
        chl_state["primary_freshness"] = _source_freshness(chl_info.get("primary_time"), cfg.get("chlorophyll", {}).get("freshness"), now)
    if chl_info.get("gapfilled_time"):
        chl_state["gapfilled_freshness"] = _source_freshness(chl_info.get("gapfilled_time"), cfg.get("chlorophyll_gapfilled", {}).get("freshness"), now)

    bathy_state = _layer_state(bool(cfg.get("bathymetry", {}).get("enabled")), layers.get("depth_m") is not None, errors, "layers bathymetry:")
    if downstream_not_attempted:
        bathy_state.update(status="not_attempted", not_attempted_reason="Required SST grid unavailable; downstream gridded layers were not requested.")
    bathy_state.update(bathy_info)
    if layers.get("depth_m") is not None and not bathy_info:
        depth = layers["depth_m"]
        finite = np.isfinite(depth)
        bathy_state.update({"grid_shape": [int(depth.shape[0]), int(depth.shape[1])],
                            "depth_valid_fraction": round(float(finite.mean()), 6),
                            "depth_min_m": round(float(np.nanmin(depth[finite])), 6) if finite.any() else None,
                            "depth_max_m": round(float(np.nanmax(depth[finite])), 6) if finite.any() else None})

    current_cfg = cfg.get("currents", {})
    current_fallback_cfg = cfg.get("currents_fallback", {})
    current_info = layers.get("currents_info") or {}
    current_primary = current_info.get("primary") or {}
    current_fallback = current_info.get("fallback") or {}
    currents_state = _layer_state(bool(current_cfg.get("enabled") or current_fallback_cfg.get("enabled")), current_present, errors,
                                  ["layers currents:", "layers currents primary:", "layers currents fallback:"])
    if downstream_not_attempted:
        currents_state.update(status="not_attempted", not_attempted_reason="Required SST grid unavailable; HF Radar and altimetry requests were never started.")
    currents_state.update(current_info)
    currents_state["dataset"] = layers.get("datasets", {}).get("currents") or current_cfg.get("dataset")
    currents_state["time"] = layers.get("times", {}).get("currents")
    primary_loaded = bool(current_primary.get("loaded")) if current_info else current_present
    fallback_loaded = bool(current_fallback.get("loaded"))
    fallback_used = bool(current_fallback.get("used_for_currents", current_fallback.get("loaded")) )
    currents_state["fallback_used_for_currents"] = fallback_used
    selected_time = current_primary.get("time") if primary_loaded else (current_fallback.get("time") if fallback_used else (currents_state["time"] if not fallback_loaded else None))
    selected_policy = current_cfg.get("freshness") if primary_loaded or not fallback_used else current_fallback_cfg.get("freshness")
    currents_state["freshness"] = ({"status": "not_assessed", "observed_at": None, "age_hours": None}
                                    if downstream_not_attempted else _source_freshness(selected_time, selected_policy, now))
    if primary_loaded:
        currents_state["primary_freshness"] = _source_freshness(current_primary.get("time") or currents_state["time"], current_cfg.get("freshness"), now)
    if fallback_loaded:
        currents_state["fallback_freshness"] = _source_freshness(current_fallback.get("time"), current_fallback_cfg.get("freshness"), now)
    structure_state = _layer_state(bool(arc.get("artificial_reefs", {}).get("enabled") and arc.get("natural_reef", {}).get("enabled")), structure_present, errors, "layers structure:")
    if downstream_not_attempted:
        structure_state.update(status="not_attempted", not_attempted_reason="Required SST grid unavailable; spatial layers were not requested.")
    structure_state.update(layers.get("structure_stats") or {})
    habitat_state = _layer_state(bool(arc.get("unified_benthic", {}).get("enabled")), habitat_present, errors, "layers benthic_habitat:")
    if downstream_not_attempted:
        habitat_state.update(status="not_attempted", not_attempted_reason="Required SST grid unavailable; spatial layers were not requested.")
    habitat_state.update(layers.get("habitat_info") or {})
    closure_state = _layer_state(bool(sources.get("closures", {}).get("enabled")), closure_present, errors, "layers closures:")
    if downstream_not_attempted:
        closure_state.update(status="not_attempted", not_attempted_reason="Required SST grid unavailable; closure request was not reached.")
    closure_state["area_count"] = len(layers.get("closure_areas") or [])

    return {"schema_version": 1, "layers": {
        "sst": sst_state, "chlorophyll": chl_state, "bathymetry": bathy_state,
        "currents": currents_state, "reef_structure": structure_state,
        "benthic_habitat": habitat_state, "closures": closure_state
    }, "semantics": {
        "missing_data": "Unavailable or unmapped cells are unknown, not zero or confirmed absence.",
        "bathymetry_resolution": "ETOPO is sampled at the configured stride and is regional context, not reef-scale navigation data.",
        "chlorophyll": "Cloud-related gaps are expected; gap-filled use is reported separately and does not imply direct observation."
    }}


def build_pipeline_health(data_quality: dict, fish_updated: bool, errors: list[str]) -> dict:
    """Classify a refresh without confusing successful execution with fresh predictions."""
    layer_states = data_quality.get("layers", {})
    sst_status = layer_states.get("sst", {}).get("status", "unavailable")
    critical = []
    if sst_status != "loaded":
        critical.append(f"Required SST layer is {sst_status}.")
    if not fish_updated:
        critical.append("Prediction outputs were not refreshed.")

    freshness_problems = []
    for name in ("sst", "chlorophyll", "currents"):
        state = layer_states.get(name, {})
        checks = [("selected", state.get("freshness", {}))]
        if name == "currents" and state.get("fallback_freshness") and state.get("fallback_used_for_currents", True):
            fallback_freshness = state["fallback_freshness"]
            selected_freshness = state.get("freshness", {})
            differs = any(fallback_freshness.get(key) != selected_freshness.get(key)
                          for key in ("status", "age_hours", "observed_at"))
            if differs:
                checks.append(("satellite-altimetry fallback", fallback_freshness))
        for source_label, freshness in checks:
            status = freshness.get("status")
            if status == "not_assessed":
                continue
            if status in ("delayed", "stale", "unknown", "future"):
                age = freshness.get("age_hours")
                age_text = f" ({age:.1f} hours old)" if isinstance(age, (int, float)) else ""
                suffix = f" [{source_label}]" if source_label != "selected" else ""
                freshness_problems.append(f"{name}{suffix}: {status}{age_text}")

    optional_problems = []
    for name, state in layer_states.items():
        if name == "sst" or state.get("status") == "disabled":
            continue
        if state.get("status") in ("failed", "unavailable", "partial"):
            optional_problems.append(f"{name}: {state.get('status')}")

    if critical:
        status = "failed"
    elif errors or optional_problems or freshness_problems:
        status = "degraded"
    else:
        status = "healthy"

    return {
        "status": status,
        "prediction_refreshed": bool(fish_updated),
        "critical_issues": critical,
        "optional_layer_issues": optional_problems,
        "freshness_issues": freshness_problems,
        "warnings": list(errors),
    }


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

    live = ROOT / "data/live"
    live.mkdir(parents=True, exist_ok=True)
    try:
        cat_data = catalog.build_catalog(ROOT / "data/species", now)
        (live / "species_catalog.json").write_text(json.dumps(cat_data, indent=2, allow_nan=False))
    except Exception as exc:
        errors.append(f"species catalog: {exc}")

    buoys = []
    layers = None
    conditions = {"now": now_dt, "tides": [], "forecast": None, "front": None}

    try:
        history: dict = {}
        buoys = pull_buoys(stations, sources["ndbc"]["realtime_url"], errors, history)
        layers = load_layers(sources, errors)
        conditions = load_conditions(tide_stations, now_dt, errors)
        forecast = load_forecast(errors)
        conditions["forecast"] = forecast
        conditions["front"] = weather.assess(history, forecast, now_dt)
    except Exception as exc:
        errors.append(f"ocean data pull: {exc}")

    sst = chl = None
    fish = None
    heat_json = None
    if layers is None:
        errors.append("kept the last published predictions: satellite temperature could not be loaded")
    else:
        try:
            cfg = sources["erddap"]
            sst = _grid_report(cfg["sst"], layers["times"]["sst"], layers["lats"], layers["lons"], layers["sst_c"])
            if layers["chl_raw"] is not None:
                clats, clons, cgrid = layers["chl_raw"]
                chl = _grid_report(cfg["chlorophyll"], layers["times"]["chlorophyll"], clats, clons, cgrid)
            heat: dict = {}
            fish = build_fish_json(layers, buoys, profiles, registry, now, places, conditions, heat)
            freshness_layers = build_data_quality(layers, sources, errors, now_dt).get("layers", {})
            fish["layers"]["freshness"] = {key: freshness_layers[key].get("freshness") for key in ("sst", "chlorophyll", "currents") if key in freshness_layers}
            current_state = freshness_layers.get("currents", {})
            fish["layers"]["current_sources"] = {
                **((layers or {}).get("currents_info") or {}),
                "primary_freshness": current_state.get("primary_freshness"),
                "fallback_freshness": current_state.get("fallback_freshness"),
                "selected_freshness": current_state.get("freshness")
            }
            fish["layers"]["times"]["stream_edge"] = (layers or {}).get("times", {}).get("stream_edge")
            la, lo = layers["lats"], layers["lons"]
            dlat, dlon = float(la[1] - la[0]), float(lo[1] - lo[0])
            heat_json = {"version": 1, "generated_utc": now, "width": int(len(lo)), "height": int(len(la)),
                         "bounds": [round(float(lo[0]) - dlon / 2, 4), round(float(la[0]) - dlat / 2, 4),
                                    round(float(lo[-1]) + dlon / 2, 4), round(float(la[-1]) + dlat / 2, 4)],
                         "note": "One byte per cell, north row first: 0 = no score, 1-100 = score in percent.", "species": heat}
        except Exception as exc:
            errors.append(f"prediction scoring: {exc}")
            fish = None

    cl_cfg = sources.get("closures", {})
    cl_loaded = bool(layers and layers.get("closure_checked"))
    cl_json = closures_mod.to_geojson((layers or {}).get("closure_areas", []), cl_cfg.get("source_label", "NOAA MPA Inventory"), cl_loaded, now)

    latest = {"generated_utc": now, "region": sources["region"]["name"], "buoys": buoys,
              "sst": sst, "chlorophyll": chl, "structure": (layers or {}).get("structure_stats"),
              "habitat": (layers or {}).get("habitat_info"),
              "bathymetry": (layers or {}).get("bathymetry_info"),
              "data_quality": build_data_quality(layers, sources, errors, now_dt),
              "closures": {"loaded": cl_loaded, "areas": len(cl_json["features"])},
              "conditions": {**timing.summary(conditions), "sea": seastate.summary(buoys, conditions)}, "fish_updated": fish is not None, "errors": errors}
    latest["pipeline_health"] = build_pipeline_health(latest["data_quality"], fish is not None, errors)
    (live / "latest.json").write_text(json.dumps(latest, indent=2, allow_nan=False))

    if fish is not None:      # Staged atomic write so partial outputs are never published
        try:
            import shutil
            stage = ROOT / "data/live_stage"
            if stage.exists():
                shutil.rmtree(stage)
            stage.mkdir(parents=True, exist_ok=True)

            stream = currents.stream_geojson((layers or {}).get("stream_edge_lon"), (layers or {}).get("lats"),
                                             (layers or {}).get("stream_edge_source") or "NOAA satellite-altimetry currents (source unavailable)",
                                             (layers or {}).get("times", {}).get("stream_edge"),
                                             (layers or {}).get("stream_edge_lon") is not None, now)

            (stage / "fish.json").write_text(json.dumps(fish, indent=1, allow_nan=False), encoding="utf-8")
            (stage / "closures.json").write_text(json.dumps(cl_json, allow_nan=False, separators=(",", ":")), encoding="utf-8")
            (stage / "stream.json").write_text(json.dumps(stream, allow_nan=False, separators=(",", ":")), encoding="utf-8")
            images = {f.name: f.read_bytes() for f in sorted((ROOT / "web/fish").glob("*.png"))}
            for rel, data in api_mod.build(fish, heat_json, cl_json, stream, profiles, images).items():
                dest = stage / "api" / "v1" / rel                     # the app-facing copy: see docs/seabound-api.md
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)

            # Split heat.json into a lightweight manifest and per-species heat files under heat/
            heat_manifest = {
                "version": 1,
                "generated_utc": now,
                "width": heat_json["width"],
                "height": heat_json["height"],
                "bounds": heat_json["bounds"],
                "note": heat_json["note"],
                "species": {sid: f"heat/{sid}.json" for sid in heat_json.get("species", {})}
            }
            (stage / "heat.json").write_text(json.dumps(heat_manifest, allow_nan=False, separators=(",", ":")), encoding="utf-8")

            heat_dir = stage / "heat"
            heat_dir.mkdir(parents=True, exist_ok=True)
            for sid, b64_str in heat_json.get("species", {}).items():
                sp_heat = {
                    "width": heat_json["width"],
                    "height": heat_json["height"],
                    "bounds": heat_json["bounds"],
                    "scores_base64": b64_str
                }
                (heat_dir / f"{sid}.json").write_text(json.dumps(sp_heat, allow_nan=False, separators=(",", ":")), encoding="utf-8")

            # Commit staged files atomically
            for src_file in stage.rglob("*"):
                if src_file.is_file():
                    rel_path = src_file.relative_to(stage)
                    dest_path = live / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, dest_path)
            shutil.rmtree(stage)
        except Exception as exc:
            log.error("Failed to commit staged prediction outputs: %s", exc)
            errors.append(f"staging predictions: {exc}")

    for sp in (fish or {}).get("species", []):
        log.info("%-20s %-20s %s", sp["name"], sp["status"], sp["message"] or f"{sp['spots']} area(s)")
    # Rewrite after staging so late preparation errors are reflected in diagnostics.
    latest["errors"] = errors
    latest["pipeline_health"] = build_pipeline_health(latest["data_quality"], fish is not None, errors)
    (live / "latest.json").write_text(json.dumps(latest, indent=2, allow_nan=False))
    log.info("pipeline health: %s", latest["pipeline_health"]["status"])
    log.info("wrote latest.json%s (%d errors)", " and fish.json" if fish is not None else "; fish.json left as it was", len(errors))


if __name__ == "__main__":
    main()
