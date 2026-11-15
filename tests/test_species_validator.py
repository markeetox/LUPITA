from __future__ import annotations

import json
from pathlib import Path

from pipeline.species_validator import audit_species, validate_profile, write_reports

REGISTRY = {
    "sst_c": {"key": "sst_c", "status": "active"},
    "tide_stage": {"key": "tide_stage", "status": "active", "values": ["rising", "falling"]},
    "structure_type": {"key": "structure_type", "status": "active", "values": ["reef", "seagrass", "inlet", "cut", "flat", "mangrove_edge"]},
    "spawning_season": {"key": "spawning_season", "status": "planned"},
    "unknown_planned": {"key": "unknown_planned", "status": "planned"},
    "distance_to_inlet": {"key": "distance_to_inlet", "status": "active"},
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
         "active": True, "value_status": "sourced", "sources": ["https://example.org/source"]},
        {"param": "spawning_season", "kind": "season", "months": [4, 5, 6], "peak_months": [5], "weight": 0.5,
         "active": True, "value_status": "provisional", "sources": ["https://example.org/source"]},
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


def test_min_coverage_must_be_between_zero_and_one():
    result = validate_profile(profile(min_coverage=1.2), REGISTRY)
    assert "invalid_min_coverage" in {x["code"] for x in result["findings"]}


def test_category_map_is_valid_without_preferred_and_checks_scores_and_keys():
    good = profile(factors=[{
        "param": "structure_type", "kind": "category", "map": {"reef": 1.0, "seagrass": 0.4},
        "weight": 1.0, "active": True, "value_status": "sourced",
        "sources": ["https://example.org/habitat"],
    }])
    result = validate_profile(good, REGISTRY)
    codes = {x["code"] for x in result["findings"]}
    assert "missing_preferred_categories" not in codes
    assert "invalid_category_map" not in codes

    bad = profile(factors=[{
        "param": "structure_type", "kind": "category", "map": {"reef": 1.4, "unknown_bottom": 0.2},
        "weight": 1.0, "active": True,
    }])
    codes = {x["code"] for x in validate_profile(bad, REGISTRY)["findings"]}
    assert {"invalid_category_map_score", "category_registry_mismatch"} <= codes


def test_grid_required_flag_and_site_gate_contract_are_reported():
    grid = profile(factors=[{
        "param": "sst_c", "kind": "range", "range": [10, 30], "ideal": [20, 25],
        "weight": 1.0, "active": True, "required": True,
    }])
    assert "required_ignored_by_grid" in {x["code"] for x in validate_profile(grid, REGISTRY)["findings"]}

    site = profile(model="sites", factors=[{
        "param": "sst_c", "kind": "range", "range": [10, 30], "ideal": [20, 25],
        "weight": 1.0, "active": True, "gate": True,
    }])
    assert "site_gate_missing_required" in {x["code"] for x in validate_profile(site, REGISTRY)["findings"]}


def test_factor_flags_must_be_booleans():
    bad = profile(factors=[{
        "param": "sst_c", "kind": "range", "range": [10, 30], "ideal": [20, 25],
        "weight": 1.0, "active": True, "required": "yes",
    }])
    assert "invalid_factor_flag" in {x["code"] for x in validate_profile(bad, REGISTRY)["findings"]}


def test_active_evidence_risk_is_reported_separately_from_data_coverage():
    bad = profile(factors=[
        {"param": "sst_c", "kind": "range", "range": [10, 30], "ideal": [20, 25],
         "weight": 0.6, "active": True, "value_status": "sourced",
         "sources": ["https://example.org/temp"]},
        {"param": "spawning_season", "kind": "season", "months": [4, 5, 6], "peak_months": [5],
         "weight": 0.4, "active": True, "value_status": "provisional",
         "sources": ["https://example.org/season"]},
    ])
    result = validate_profile(bad, REGISTRY)
    assert result["active_uncertain_weight"] == 0.4
    assert result["evidence_risk"] == "elevated"
    assert "active_evidence_uncertainty" in {x["code"] for x in result["findings"]}


def test_active_evidence_uncertainty_is_not_double_counted_when_sources_are_missing():
    bad = profile(factors=[{
        "param": "sst_c", "kind": "range", "range": [10, 30], "ideal": [20, 25],
        "weight": 1.0, "active": True, "value_status": "provisional",
    }])
    result = validate_profile(bad, REGISTRY)
    assert result["active_uncertain_weight"] == 1.0
    assert result["active_uncertain_weight"] <= result["active_weight_sum"]


def test_malformed_evidence_status_is_reported_without_crashing():
    bad = profile(factors=[{
        "param": "sst_c", "kind": "range", "range": [10, 30], "ideal": [20, 25],
        "weight": 1.0, "active": True, "value_status": ["not", "a", "status"],
    }])
    codes = {x["code"] for x in validate_profile(bad, REGISTRY)["findings"]}
    assert "missing_or_unknown_evidence_status" in codes


def test_catalog_summary_counts_temperature_only_site_pilots_and_evidence_risk(tmp_path: Path):
    species = tmp_path / "species"
    species.mkdir()
    pilot = profile(model="sites", factors=[{
        "param": "sst_c", "kind": "range", "range": [10, 30], "ideal": [20, 25],
        "weight": 1.0, "active": True, "value_status": "provisional",
        "sources": ["https://example.org/temperature"],
    }])
    (species / "test-fish.json").write_text(json.dumps(pilot), encoding="utf-8")
    params = tmp_path / "parameters.json"
    params.write_text(json.dumps({"parameters": list(REGISTRY.values())}), encoding="utf-8")

    report = audit_species(species, params)
    assert report["report_version"] == 2
    assert report["summary"]["temperature_only_site_pilots"] == 1
    assert report["summary"]["elevated_active_evidence_profiles"] == 1
    assert report["species"][0]["model_scope"] == "temperature_only_pilot"


def test_inactive_incomplete_range_is_a_warning_not_a_scoring_error():
    incomplete = profile()
    incomplete["factors"].append({
        "param": "spawning_season", "kind": "range", "range": None, "ideal": None,
        "weight": 0.0, "active": False, "value_status": "needs_source", "sources": [],
    })
    result = validate_profile(incomplete, REGISTRY)
    findings = [x for x in result["findings"] if x.get("factor") == "spawning_season"]
    assert {x["code"]: x["severity"] for x in findings}["invalid_range"] == "WARNING"
    assert {x["code"]: x["severity"] for x in findings}["invalid_ideal"] == "WARNING"
    assert result["schema_valid"] is True


def test_needs_source_is_recognized_and_counts_as_uncertain_when_active():
    incomplete = profile(factors=[{
        "param": "sst_c", "kind": "range", "range": [10, 30], "ideal": [20, 25],
        "weight": 1.0, "active": True, "value_status": "needs_source", "sources": [],
    }])
    result = validate_profile(incomplete, REGISTRY)
    assert "missing_or_unknown_evidence_status" not in {x["code"] for x in result["findings"]}
    assert result["active_uncertain_weight"] == 1.0
    assert result["evidence_risk"] == "elevated"


def test_generic_homepage_reference_does_not_count_as_specific_evidence():
    bad = profile(factors=[{
        "param": "sst_c", "kind": "range", "range": [10, 30], "ideal": [20, 25],
        "weight": 1.0, "active": True, "value_status": "sourced",
        "sources": ["https://www.fisheries.noaa.gov/?utm_source=generic-homepage-test"],
    }])
    result = validate_profile(bad, REGISTRY)
    codes = {x["code"] for x in result["findings"]}
    assert "generic_source_reference" in codes
    assert result["active_sourced_weight"] == 0.0
    assert result["active_uncertain_weight"] == 1.0
    assert result["evidence_risk"] == "elevated"


def test_specific_source_page_counts_as_evidence_reference():
    good = profile(factors=[{
        "param": "sst_c", "kind": "range", "range": [10, 30], "ideal": [20, 25],
        "weight": 1.0, "active": True, "value_status": "sourced",
        "sources": ["https://www.fisheries.noaa.gov/species/test-fish"],
    }])
    result = validate_profile(good, REGISTRY)
    codes = {x["code"] for x in result["findings"]}
    assert "generic_source_reference" not in codes
    assert result["active_sourced_weight"] == 1.0
    assert result["active_uncertain_weight"] == 0.0


def test_site_distance_to_inlet_placeholder_is_not_treated_as_reliable_input():
    pilot = profile(model="sites", factors=[{
        "param": "distance_to_inlet", "kind": "range", "range": [0, 25], "ideal": [0, 5],
        "weight": 1.0, "active": True, "value_status": "sourced",
        "sources": ["https://example.org/distance-method"],
    }])
    result = validate_profile(pilot, REGISTRY)
    codes = {x["code"] for x in result["findings"]}
    assert "placeholder_site_factor" in codes
    assert result["schema_valid"] is False
    assert result["model_compatible"] is False
    assert result["active_uncertain_weight"] == 1.0
    assert result["evidence_risk"] == "elevated"


def test_site_structure_factor_flags_unreachable_and_unmapped_site_kinds():
    pilot = profile(
        model="sites",
        site_kinds=["inlet", "cut", "flat"],
        factors=[{
            "param": "structure_type", "kind": "category",
            "preferred": ["inlet", "mangrove_edge", "seagrass"],
            "map": {"inlet": 1.0},
            "weight": 1.0, "active": True, "value_status": "sourced",
            "sources": ["https://example.org/site-structure"],
        }],
    )
    result = validate_profile(pilot, REGISTRY)
    findings = {x["code"]: x["message"] for x in result["findings"]}
    assert "site_structure_categories_unreachable" in findings
    assert "mangrove_edge" in findings["site_structure_categories_unreachable"]
    assert "site_structure_kinds_unmapped" in findings
    assert "cut" in findings["site_structure_kinds_unmapped"]
    assert "flat" in findings["site_structure_kinds_unmapped"]


def test_malformed_site_structure_preferred_values_do_not_crash_validator():
    malformed = profile(
        model="sites",
        site_kinds=["inlet"],
        factors=[{
            "param": "structure_type", "kind": "category",
            "preferred": 123, "map": {"inlet": 1.0},
            "weight": 1.0, "active": True, "value_status": "sourced",
            "sources": ["https://example.org/site-structure"],
        }],
    )
    result = validate_profile(malformed, REGISTRY)
    assert "invalid_preferred_categories" in {x["code"] for x in result["findings"]}
