"""Read-only audit of LUPITA species profiles against the current scoring engines."""
from __future__ import annotations

import csv
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
VALID_MODELS = {"grid", "sites"}
VALID_KINDS = {"range", "higher_is_better", "category", "season", "flag", "flag_penalty", "presence", "proximity", "closer_is_better"}
TIMING_COMPONENTS = {"light", "tide", "moon", "front"}
VALID_VALUE_STATUSES = {"sourced", "partly_sourced", "provisional", "unsourced", "estimated"}

# These maps reflect executable code, not registry labels. Update them when
# pipeline/scoring.py, sites.py, or layers.py changes.
GRID_FACTORS = {
    "sst_c": {"range"}, "sst_gradient": {"higher_is_better"},
    "chlorophyll": {"range"}, "chl_gradient": {"higher_is_better"},
    "depth_m": {"range"}, "current_speed": {"range", "higher_is_better"},
    "current_dir": {"range"}, "current_convergence": {"higher_is_better", "range"},
    "gulf_stream_edge": {"range", "higher_is_better"}, "distance_to_inlet": {"range"},
    "structure_type": {"category"}, "bottom_slope": {"range", "higher_is_better"},
    "bottom_curvature": {"range", "higher_is_better"},
    "spawning_season": {"season"}, "season_presence": {"season"},
}
SITE_FACTORS = {
    "sst_c": {"range"}, "tide_stage": {"category"}, "time_of_day": {"category"},
    "spawning_season": {"season"}, "season_presence": {"season"},
    "structure_type": {"category"}, "distance_to_inlet": {"range"},
}
GRID_DATA = {
    "sst_c": "required", "sst_gradient": "required", "chlorophyll": "conditional",
    "chl_gradient": "conditional", "depth_m": "conditional", "current_speed": "conditional",
    "current_dir": "conditional", "current_convergence": "conditional",
    "gulf_stream_edge": "conditional", "distance_to_inlet": "conditional",
    "structure_type": "conditional", "bottom_slope": "conditional", "bottom_curvature": "conditional",
    "spawning_season": "required", "season_presence": "required",
}
SITE_DATA = {
    "sst_c": "required", "tide_stage": "conditional", "time_of_day": "required",
    "spawning_season": "required", "season_presence": "required",
    "structure_type": "required", "distance_to_inlet": "required",
}


def finding(severity: str, code: str, message: str, factor: str | None = None) -> dict[str, Any]:
    row = {"severity": severity, "code": code, "message": message}
    if factor:
        row["factor"] = factor
    return row


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def valid_pair(value: Any, nullable: bool = False) -> bool:
    return isinstance(value, list) and len(value) == 2 and all((x is None and nullable) or is_number(x) for x in value)


def validate_profile(profile: Any, registry: dict[str, dict], filename: str = "", duplicate_ids: set[str] | None = None) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    duplicate_ids = duplicate_ids or set()
    if not isinstance(profile, dict):
        return {"id": Path(filename).stem if filename else "unknown", "common_name": "",
                "classification": "INVALID / UNSUPPORTED", "schema_valid": False, "model_compatible": False,
                "environmental_data_coverage": "not_assessed", "biological_completeness": "not_assessed",
                "evidence_quality": "not_assessed", "active_factor_count": 0, "active_weight_sum": 0.0,
                "active_supported_weight": 0.0, "active_sourced_weight": 0.0, "timing_status": "not_assessed",
                "finding_counts": {"error": 1, "warning": 0, "info": 0},
                "findings": [finding("ERROR", "profile_not_object", "Profile root must be a JSON object.")]}

    sid, name = profile.get("id"), profile.get("common_name", "")
    if not isinstance(sid, str) or not sid or any(not (c.islower() or c.isdigit() or c == "-") for c in sid):
        findings.append(finding("ERROR", "invalid_id", "id must contain lowercase letters, digits, and hyphens."))
    if sid in duplicate_ids:
        findings.append(finding("ERROR", "duplicate_id", f"Duplicate species id '{sid}' across profile files."))
    if filename and sid and Path(filename).stem != sid:
        findings.append(finding("WARNING", "filename_id_mismatch", f"Filename {Path(filename).name} does not match id {sid}."))
    if not isinstance(name, str) or not name.strip():
        findings.append(finding("ERROR", "missing_common_name", "common_name is required."))
    if not isinstance(profile.get("scientific_name"), str) or not profile.get("scientific_name", "").strip():
        findings.append(finding("ERROR", "missing_scientific_name", "scientific_name is required."))
    if not isinstance(profile.get("display"), dict) or not isinstance(profile.get("display", {}).get("color"), str):
        findings.append(finding("WARNING", "missing_display_color", "display.color is missing; catalog rendering may use a fallback."))

    model = profile.get("model", "grid")
    if model not in VALID_MODELS:
        findings.append(finding("ERROR", "unknown_model", f"Unsupported model '{model}'; expected grid or sites."))
        model = "grid"
    for key in ("lat_range", "lon_range"):
        bounds = profile.get(key)
        if bounds is not None and (not valid_pair(bounds) or bounds[0] > bounds[1]):
            findings.append(finding("ERROR", "invalid_geographic_range", f"{key} must contain two finite ascending bounds."))

    factors = profile.get("factors")
    if not isinstance(factors, list):
        findings.append(finding("ERROR", "invalid_factors", "factors must be an array."))
        factors = []
    if not factors:
        findings.append(finding("ERROR", "empty_factors", "No factors are configured."))

    active, factor_params = [], set()
    active_weight = supported_weight = sourced_weight = 0.0
    registry_keys = set(registry)
    evidence_statuses = Counter()
    engine = SITE_FACTORS if model == "sites" else GRID_FACTORS

    for index, factor in enumerate(factors):
        if not isinstance(factor, dict):
            findings.append(finding("ERROR", "factor_not_object", f"Factor #{index + 1} must be an object."))
            continue
        param, kind = factor.get("param"), factor.get("kind")
        if not isinstance(param, str) or not param:
            findings.append(finding("ERROR", "missing_factor_parameter", f"Factor #{index + 1} has no parameter key."))
            continue
        if param in factor_params:
            findings.append(finding("WARNING", "duplicate_factor", f"Parameter '{param}' appears more than once.", param))
        factor_params.add(param)
        if param not in registry_keys:
            findings.append(finding("ERROR", "unknown_parameter", f"'{param}' is not registered in data/parameters.json.", param))
        if kind not in VALID_KINDS:
            findings.append(finding("ERROR", "unknown_factor_kind", f"'{param}' uses unknown kind '{kind}'.", param))
        weight = factor.get("weight", 0)
        if not is_number(weight) or weight < 0:
            findings.append(finding("ERROR", "invalid_weight", f"'{param}' weight must be finite and non-negative.", param))
            weight = 0.0
        if factor.get("active") is True:
            active.append(factor)
            active_weight += float(weight)
            if weight <= 0:
                findings.append(finding("ERROR", "active_nonpositive_weight", f"Active factor '{param}' must have positive weight.", param))
            if kind in engine.get(param, set()):
                supported_weight += float(weight)
            else:
                findings.append(finding("ERROR", "unsupported_active_factor", f"The {model} scorer cannot evaluate active factor '{param}' with kind '{kind}'.", param))
            if registry.get(param, {}).get("status") == "planned":
                findings.append(finding("WARNING", "planned_parameter_active", f"'{param}' is marked planned in the registry but active in this profile.", param))
            if factor.get("value_status") == "sourced" and factor.get("sources"):
                sourced_weight += float(weight)

        status = factor.get("value_status")
        evidence_statuses[status if isinstance(status, str) else "missing"] += 1
        if status not in VALID_VALUE_STATUSES:
            findings.append(finding("WARNING", "missing_or_unknown_evidence_status", f"'{param}' has no recognized value_status.", param))
        sources = factor.get("sources")
        if not isinstance(sources, list) or not sources or not all(isinstance(x, str) and x.strip() for x in sources):
            findings.append(finding("WARNING", "missing_factor_sources", f"'{param}' has no usable source references.", param))
        if status in {"provisional", "estimated", "unsourced"}:
            findings.append(finding("WARNING", "provisional_factor", f"'{param}' is marked {status}; its contribution is provisional.", param))

        if kind == "range":
            rng, ideal = factor.get("range"), factor.get("ideal")
            if not valid_pair(rng, nullable=True):
                findings.append(finding("ERROR", "invalid_range", f"'{param}' requires a two-value range; null bounds are allowed.", param))
            elif rng[0] is not None and rng[1] is not None and rng[0] > rng[1]:
                findings.append(finding("ERROR", "reversed_range", f"'{param}' has reversed range bounds.", param))
            if not valid_pair(ideal, nullable=True):
                findings.append(finding("ERROR", "invalid_ideal", f"'{param}' requires a two-value ideal range.", param))
            elif valid_pair(rng, nullable=True):
                lo, hi = rng
                ilo, ihi = ideal
                if ilo is not None and ihi is not None and ilo > ihi:
                    findings.append(finding("ERROR", "reversed_ideal", f"'{param}' has reversed ideal bounds.", param))
                if (lo is not None and ilo is not None and ilo < lo) or (hi is not None and ihi is not None and ihi > hi):
                    findings.append(finding("ERROR", "ideal_outside_range", f"'{param}' ideal range falls outside its allowed range.", param))
        if kind == "season":
            months, peaks = factor.get("months", []), factor.get("peak_months", [])
            if not isinstance(months, list) or not months or any(not isinstance(m, int) or isinstance(m, bool) or not 1 <= m <= 12 for m in months):
                findings.append(finding("ERROR", "invalid_season_months", f"'{param}' months must be integers from 1 to 12.", param))
            if not isinstance(peaks, list) or not isinstance(months, list) or any(m not in months for m in peaks):
                findings.append(finding("ERROR", "invalid_peak_months", f"'{param}' peak_months must be a subset of months.", param))
        if kind == "category":
            preferred = factor.get("preferred")
            if not isinstance(preferred, list) or not preferred:
                findings.append(finding("WARNING", "missing_preferred_categories", f"'{param}' has no preferred category values.", param))
            values = registry.get(param, {}).get("values")
            if values and isinstance(preferred, list):
                unknown = sorted(set(preferred) - set(values))
                if unknown:
                    findings.append(finding("WARNING", "category_registry_mismatch", f"'{param}' uses values absent from the registry: {', '.join(unknown)}.", param))

    if active_weight <= 0:
        findings.append(finding("ERROR", "no_active_weight", "Profile has no positive active factor weight."))
    if active_weight > 1.000001:
        findings.append(finding("ERROR", "active_weight_overflow", f"Active weights sum to {active_weight:.3f}, above 1.0."))
    if len(active) == 1:
        findings.append(finding("WARNING", "single_factor_model", "Only one active factor; full input coverage does not imply biological completeness."))

    data_map = SITE_DATA if model == "sites" else GRID_DATA
    if any(f.get("param") not in data_map for f in active):
        data_availability = "unsupported"
    elif any(data_map.get(f.get("param")) == "conditional" for f in active):
        data_availability = "conditional"
    else:
        data_availability = "available_by_design"

    dimensions = {
        "temperature": "sst_c", "depth": "depth_m", "structure": "structure_type",
        "seasonality": "season_presence" if "season_presence" in factor_params else "spawning_season",
        "tides": "tide_stage", "light": "time_of_day",
    }
    represented = [dimension for dimension, param in dimensions.items() if param in factor_params]
    bio = profile.get("profile") if isinstance(profile.get("profile"), dict) else {}
    if not profile.get("habitat_zone"):
        findings.append(finding("WARNING", "missing_habitat_zone", "habitat_zone is missing."))
    if not bio.get("behavior"):
        findings.append(finding("WARNING", "missing_behavior_description", "profile.behavior is missing."))
    if not bio.get("sources"):
        findings.append(finding("WARNING", "missing_profile_sources", "profile.sources is missing or empty."))
    if not profile.get("open_items"):
        findings.append(finding("INFO", "no_open_items_recorded", "No open_items are recorded; this does not prove research is complete."))
    if len(represented) <= 1:
        findings.append(finding("WARNING", "limited_biological_dimensions", f"Only {len(represented)} of 6 review dimensions are represented."))
    elif len(represented) < 4:
        findings.append(finding("WARNING", "partial_biological_dimensions", f"Only {len(represented)} of 6 review dimensions are represented."))

    timing = profile.get("timing")
    timing_status = "not_configured"
    if timing is not None:
        timing_status = "configured"
        if not isinstance(timing, dict):
            findings.append(finding("ERROR", "invalid_timing_config", "timing must be an object."))
            timing_status = "invalid"
        else:
            unknown = sorted(set(timing) - TIMING_COMPONENTS - {"status", "note", "sources", "weights"})
            if unknown:
                findings.append(finding("WARNING", "unknown_timing_components", f"Unsupported timing keys: {', '.join(unknown)}."))
            weights = timing.get("weights", {})
            if not isinstance(weights, dict) or any(k not in TIMING_COMPONENTS for k in weights):
                findings.append(finding("ERROR", "invalid_timing_weights", "Timing weights may contain only light, tide, moon, and front."))
            elif any(not is_number(v) or v < 0 for v in weights.values()):
                findings.append(finding("ERROR", "invalid_timing_weights", "Timing weights must be finite and non-negative."))
            for component in TIMING_COMPONENTS:
                cfg = timing.get(component)
                if cfg is None:
                    continue
                if not isinstance(cfg, dict):
                    findings.append(finding("ERROR", "invalid_timing_component", f"Timing component '{component}' must be an object."))
                elif component in {"light", "tide", "front"} and (not isinstance(cfg.get("map"), dict) or not cfg.get("map")):
                    findings.append(finding("ERROR", "missing_timing_map", f"Timing component '{component}' requires a map."))
                elif component == "moon" and any(not is_number(cfg.get(k)) for k in ("from_days", "to_days", "in_score", "out_score")):
                    findings.append(finding("ERROR", "invalid_moon_timing", "Moon timing requires numeric day bounds and scores."))
            if not isinstance(timing.get("sources"), list) or not timing.get("sources"):
                findings.append(finding("WARNING", "missing_timing_sources", "Timing has no supporting sources."))
            if timing.get("status") in {"angler_lore", "provisional", "estimated"}:
                findings.append(finding("WARNING", "provisional_timing", f"Timing status '{timing.get('status')}' is not an empirically calibrated feeding model."))
    else:
        findings.append(finding("INFO", "timing_not_configured", "No species-specific timing configuration is present."))

    errors = sum(x["severity"] == "ERROR" for x in findings)
    warnings = sum(x["severity"] == "WARNING" for x in findings)
    compatible = not any(x["code"] == "unsupported_active_factor" for x in findings)
    if errors:
        classification = "INVALID / UNSUPPORTED"
    elif any(x["code"] in {"single_factor_model", "limited_biological_dimensions", "partial_biological_dimensions", "category_registry_mismatch"} for x in findings):
        classification = "NEEDS MODEL REBUILD"
    elif warnings:
        classification = "NEEDS RESEARCH"
    else:
        classification = "READY FOR REVIEW"
    sourced_count = evidence_statuses.get("sourced", 0)
    factor_count = len([x for x in factors if isinstance(x, dict)])
    evidence = "low" if not sourced_count else "moderate" if sourced_count < factor_count else "source_documented"

    return {
        "id": sid or Path(filename).stem or "unknown", "common_name": name,
        "scientific_name": profile.get("scientific_name", ""), "model": profile.get("model", "grid"),
        "classification": classification, "schema_valid": errors == 0, "model_compatible": compatible,
        "environmental_data_coverage": data_availability,
        "biological_completeness": f"{len(represented)}/6 dimensions represented (structural proxy only)",
        "biological_dimensions": represented, "evidence_quality": evidence,
        "active_factor_count": len(active), "active_weight_sum": round(active_weight, 6),
        "active_supported_weight": round(supported_weight, 6), "active_sourced_weight": round(sourced_weight, 6),
        "timing_status": timing_status,
        "finding_counts": {"error": errors, "warning": warnings, "info": len(findings) - errors - warnings},
        "findings": findings,
    }


def audit_species(species_dir: Path, parameters_file: Path, generated_utc: str | None = None) -> dict[str, Any]:
    registry_doc = json.loads(parameters_file.read_text(encoding="utf-8"))
    registry = {p["key"]: p for p in registry_doc.get("parameters", []) if isinstance(p, dict) and isinstance(p.get("key"), str)}
    files = sorted(species_dir.glob("*.json"))
    parsed, results = [], []
    for path in files:
        try:
            parsed.append((path.name, json.loads(path.read_text(encoding="utf-8"))))
        except Exception as exc:
            results.append({
                "id": path.stem, "common_name": "", "scientific_name": "", "model": "unknown",
                "classification": "INVALID / UNSUPPORTED", "schema_valid": False, "model_compatible": False,
                "environmental_data_coverage": "not_assessed", "biological_completeness": "not_assessed",
                "evidence_quality": "not_assessed", "active_factor_count": 0, "active_weight_sum": 0.0,
                "active_supported_weight": 0.0, "active_sourced_weight": 0.0, "timing_status": "not_assessed",
                "finding_counts": {"error": 1, "warning": 0, "info": 0},
                "findings": [finding("ERROR", "json_parse_error", f"Could not parse JSON: {exc}")],
            })
    ids = [p.get("id") for _, p in parsed if isinstance(p, dict) and isinstance(p.get("id"), str)]
    duplicates = {sid for sid, count in Counter(ids).items() if count > 1}
    results.extend(validate_profile(profile, registry, filename, duplicates) for filename, profile in parsed)
    results.sort(key=lambda x: (str(x.get("common_name", "")).casefold(), str(x.get("id", ""))))
    classes = Counter(x["classification"] for x in results)
    summary = {
        "profiles_inspected": len(files), "profiles_parsed": len(parsed), "json_parse_errors": len(files) - len(parsed),
        "structurally_valid": sum(bool(x["schema_valid"]) for x in results),
        "model_compatibility_issues": sum(not x["model_compatible"] for x in results),
        "needs_biological_research_or_rebuild": sum(x["classification"] in {"NEEDS RESEARCH", "NEEDS MODEL REBUILD"} for x in results),
        "classification_counts": dict(sorted(classes.items())),
        "severity_counts": {level: sum(x["finding_counts"].get(level, 0) for x in results) for level in ("error", "warning", "info")},
    }
    return {
        "report_version": 1,
        "generated_utc": generated_utc or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": {"species_directory": "data/species", "parameter_registry": "data/parameters.json"},
        "interpretation": {
            "environmental_data_coverage": "Input availability class based on current pipeline support; not a per-run coverage percentage.",
            "biological_completeness": "Six-dimension structural review proxy, not a scientific validity score.",
            "evidence_quality": "Source metadata coverage; source presence does not establish source quality.",
            "prediction_probability": "Prediction scores and confidence are not calibrated probabilities of fish presence.",
        },
        "summary": summary, "species": results,
    }


def write_reports(report: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "species-audit.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    fields = ["id", "common_name", "scientific_name", "model", "classification", "schema_valid", "model_compatible",
              "environmental_data_coverage", "biological_completeness", "evidence_quality", "active_factor_count",
              "active_weight_sum", "active_supported_weight", "active_sourced_weight", "timing_status"]
    with (output_dir / "species-audit.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(report["species"])
    summary = report["summary"]
    lines = ["# LUPITA Species Profile Audit", "", f"Generated: {report['generated_utc']}", "", "## Summary", "",
             f"- Profiles inspected: **{summary['profiles_inspected']}**",
             f"- Profiles parsed: **{summary['profiles_parsed']}**",
             f"- JSON parse errors: **{summary['json_parse_errors']}**",
             f"- Structurally valid: **{summary['structurally_valid']}**",
             f"- Model compatibility issues: **{summary['model_compatibility_issues']}**",
             f"- Need research or model rebuilding: **{summary['needs_biological_research_or_rebuild']}**",
             "", "| Classification | Count |", "|---|---:|"]
    lines.extend(f"| {key} | {value} |" for key, value in summary["classification_counts"].items())
    lines += ["", "## Interpretation", "",
              "- Schema validity does not establish scientific validity.",
              "- Environmental input availability is separate from biological model completeness.",
              "- Biological dimensions are a review aid, not a completeness score.",
              "- Source metadata does not prove source credibility or correct interpretation.",
              "- Prediction scores and confidence are not calibrated probabilities of fish presence.",
              "", "## Species findings", ""]
    for row in report["species"]:
        lines.append(f"### {row['common_name'] or row['id']} ({row['id']})")
        lines.append(f"- {row['classification']} | model: {row['model']} | active factors: {row['active_factor_count']} | weight: {row['active_weight_sum']:.3f}")
        lines.append(f"- Data: {row['environmental_data_coverage']} | Biology: {row['biological_completeness']} | Evidence: {row['evidence_quality']}")
        lines.extend(f"- **{item['severity']} / {item['code']}**: {item['message']}" for item in row["findings"])
        lines.append("")
    lines += ["## Limitations", "",
              "This is an automated engineering audit. It does not independently verify biological claims, source credibility, local stock differences, or empirical prediction accuracy. Missing evidence is reported as a research gap; no biological values or sources are invented.", ""]
    (output_dir / "species-audit.md").write_text("\n".join(lines), encoding="utf-8")
