from __future__ import annotations

import json
from pathlib import Path

from pipeline.species_validator import audit_species, validate_profile, write_reports

REGISTRY = {
    "sst_c": {"key": "sst_c", "status": "active"},
    "tide_stage": {"key": "tide_stage", "status": "active", "values": ["rising", "falling"]},
    "structure_type": {"key": "structure_type", "status": "active", "values": ["reef", "seagrass"]},
    "spawning_season": {"key": "spawning_season", "status": "planned"},
    "unknown_planned": {"key": "unknown_planned", "status": "planned"},
}


def profile(**updates):
    base = {
        "id": "test-fish", "common_name": "Test fish", "scientific_name": "Pisces testus",
        "model": "grid", "habitat_zone": "coastal", "display": {"color": "#abcdef"},
        "profile": {"behavior": "Uses coastal habitat.", "sources": ["https://example.org/fish"]},
        "factors": [{"param": "sst_c", "kind": "range", "range": [10, 30], "ideal": [20, 25],
                     "weight": 1.0, "active": True, "value_status": "sourced",
                     "sources": ["https://example.org/temp"]}],
        "open_items": ["Validate local temperature preference"],
    }
    base.update(updates)
    return base


def test_one_factor_profile_is_not_biologically_complete():
    result = validate_profile(profile(), REGISTRY)
    assert result["schema_valid"] is True
    assert result["model_compatible"] is True
    assert result["classification"] == "NEEDS MODEL REBUILD"
    assert result["biological_completeness"].startswith("1/6")
    assert result["environmental_data_coverage"] == "available_by_design"


def test_missing_required_fields_and_empty_factors_are_errors():
    codes = {x["code"] for x in validate_profile({"id": "bad", "factors": []}, REGISTRY)["findings"]}
    assert {"missing_common_name", "missing_scientific_name", "empty_factors"} <= codes


def test_duplicate_ids_are_detected_across_files(tmp_path: Path):
    species = tmp_path / "species"
    species.mkdir()
    for name in ("one", "two"):
        (species / f"{name}.json").write_text(json.dumps(profile()), encoding="utf-8")
    params = tmp_path / "parameters.json"
    params.write_text(json.dumps({"parameters": list(REGISTRY.values())}), encoding="utf-8")
    report = audit_species(species, params, generated_utc="2026-11-12T00:00:00+00:00")
    assert report["summary"]["profiles_inspected"] == 2
    assert all(any(x["code"] == "duplicate_id" for x in row["findings"]) for row in report["species"])


def test_invalid_weight_and_inconsistent_ranges_are_errors():
    bad = profile(factors=[{"param": "sst_c", "kind": "range", "range": [30, 10], "ideal": [40, 50],
                            "weight": -0.2, "active": True}])
    codes = {x["code"] for x in validate_profile(bad, REGISTRY)["findings"]}
    assert {"invalid_weight", "reversed_range", "ideal_outside_range"} <= codes


def test_active_unsupported_factor_is_flagged():
    bad = profile(factors=[{"param": "unknown_planned", "kind": "range", "range": [1, 10], "ideal": [2, 5],
                            "weight": 1.0, "active": True}])
    result = validate_profile(bad, REGISTRY)
    assert "unsupported_active_factor" in {x["code"] for x in result["findings"]}
    assert result["model_compatible"] is False


def test_site_engine_compatibility_and_planned_registry_warning():
    good = profile(model="sites", factors=[
        {"param": "sst_c", "kind": "range", "range": [10, 30], "ideal": [20, 25], "weight": 0.5,
         "active": True, "value_status": "sourced", "sources": ["https://example.org"]},
        {"param": "spawning_season", "kind": "season", "months": [4, 5, 6], "peak_months": [5], "weight": 0.5,
         "active": True, "value_status": "provisional", "sources": ["https://example.org"]},
    ])
    result = validate_profile(good, REGISTRY)
    codes = {x["code"] for x in result["findings"]}
    assert result["model_compatible"] is True
    assert {"planned_parameter_active", "provisional_factor"} <= codes


def test_missing_evidence_and_timing_configuration_are_reported():
    bad = profile(timing={"weights": {"nonsense": 0.5}, "light": {"map": {}}, "sources": []})
    codes = {x["code"] for x in validate_profile(bad, REGISTRY)["findings"]}
    assert "missing_factor_sources" not in codes
    assert {"invalid_timing_weights", "missing_timing_map", "missing_timing_sources"} <= codes


def test_non_object_profile_is_invalid():
    result = validate_profile([], REGISTRY)
    assert result["classification"] == "INVALID / UNSUPPORTED"
    assert result["schema_valid"] is False


def test_reports_are_written(tmp_path: Path):
    row = validate_profile(profile(), REGISTRY)
    report = {"generated_utc": "2026-11-12T00:00:00+00:00",
              "summary": {"profiles_inspected": 1, "profiles_parsed": 1, "json_parse_errors": 0,
                          "structurally_valid": 1, "model_compatibility_issues": 0,
                          "needs_biological_research_or_rebuild": 1,
                          "classification_counts": {"NEEDS MODEL REBUILD": 1},
                          "severity_counts": {"error": 0, "warning": 1, "info": 0}},
              "species": [row]}
    write_reports(report, tmp_path)
    assert all((tmp_path / f"species-audit.{ext}").exists() for ext in ("json", "md", "csv"))
