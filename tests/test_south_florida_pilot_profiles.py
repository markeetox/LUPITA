"""Regression guards for the South Florida Bonefish and Permit pilot profiles."""
import json
from pathlib import Path

from pipeline.spatial_context import validate_habitat_contexts

ROOT = Path(__file__).resolve().parents[1]
SPECIES = ROOT / "data" / "species"


def load(species_id):
    return json.loads((SPECIES / f"{species_id}.json").read_text(encoding="utf-8"))


def test_pilot_profiles_have_species_specific_source_documented_descriptions():
    bonefish = load("bonefish")
    permit = load("permit")

    assert "northern florida keys" in bonefish["profile"]["behavior"].lower()
    assert "spawning" in bonefish["profile"]["life_history"].lower()
    assert "Bahamas" in bonefish["profile"]["spawning"]
    assert "Florida Reef Tract" in permit["profile"]["behavior"]
    assert "15–40 m" in permit["profile"]["behavior"]
    assert "March through September" in permit["profile"]["spawning"]
    assert bonefish["profile"]["sources"]
    assert permit["profile"]["sources"]
    assert bonefish["profile"]["behavior"] != permit["profile"]["behavior"]


def test_numeric_sst_thresholds_are_explicitly_provisional_not_mislabelled_as_sourced():
    for species_id in ("bonefish", "permit"):
        profile = load(species_id)
        factor = next(f for f in profile["factors"] if f["param"] == "sst_c")
        assert factor["value_status"] == "provisional"
        assert factor["sources"] == []
        assert "not a validated thermal preference" in factor["reason_template"]
        assert "not a validated" in factor["value_notes"].lower()


def test_profile_research_gaps_are_recorded():
    bonefish = load("bonefish")
    permit = load("permit")
    assert bonefish["open_items"]
    assert permit["open_items"]
    assert any("thermal" in item.lower() for item in bonefish["open_items"])
    assert any("reef-tract" in item.lower() for item in permit["open_items"])


def test_existing_production_scoring_configuration_is_unchanged():
    expected = {
        "bonefish": {"range": [20.0, 35.0], "ideal": [25.0, 31.0], "weight": 0.35},
        "permit": {"range": [20.0, 34.0], "ideal": [24.0, 30.0], "weight": 0.35},
    }
    for species_id, values in expected.items():
        profile = load(species_id)
        factor = next(f for f in profile["factors"] if f["param"] == "sst_c")
        assert factor["range"] == values["range"]
        assert factor["ideal"] == values["ideal"]
        assert factor["weight"] == values["weight"]
        assert factor["active"] is True
        assert factor["gate"] is True
        assert factor["required"] is True
        assert profile["timing"]["weights"] == {"light": 0.5, "tide": 0.3, "front": 0.2}



def test_pilot_species_have_distinct_descriptive_habitat_contexts():
    bonefish = load("bonefish")
    permit = load("permit")

    assert validate_habitat_contexts(bonefish["habitat_contexts"]) == []
    assert validate_habitat_contexts(permit["habitat_contexts"]) == []

    bonefish_contexts = {row["id"]: row for row in bonefish["habitat_contexts"]["contexts"]}
    permit_contexts = {row["id"]: row for row in permit["habitat_contexts"]["contexts"]}

    assert "channel-and-refuge-context" in bonefish_contexts
    assert "reef-tract-use" not in bonefish_contexts
    assert "reef-tract-use" in permit_contexts
    assert "flats-to-reef-connectivity" in permit_contexts
    assert all(row["local_validation"] == "required" for row in bonefish["habitat_contexts"]["contexts"])
    assert all(row["local_validation"] == "required" for row in permit["habitat_contexts"]["contexts"])


def test_species_habitat_contexts_are_descriptive_not_active_scoring_factors():
    for species_id in ("bonefish", "permit"):
        profile = load(species_id)
        assert "habitat_contexts" in profile
        assert all("weight" not in row and "active" not in row
                   for row in profile["habitat_contexts"]["contexts"])
