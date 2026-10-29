"""Unit tests for standalone species catalog generation (pipeline/catalog.py)."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile

from pipeline import catalog


ROOT = Path(__file__).resolve().parent.parent


def test_catalog_contains_all_species_profiles():
    species_dir = ROOT / "data/species"
    expected_files = list(species_dir.glob("*.json"))

    cat = catalog.build_catalog(species_dir)

    assert cat["version"] == 1
    assert cat["total"] == len(expected_files)
    assert len(cat["species"]) == len(expected_files)


def test_catalog_species_ids_unique_and_stable():
    cat = catalog.build_catalog(ROOT / "data/species")
    species = cat["species"]

    ids = [s["id"] for s in species]
    assert len(ids) == len(set(ids)), "Species IDs in catalog must be unique"

    names = [s["name"] for s in species]
    assert names == sorted(names, key=lambda n: n.lower()), "Catalog species must be sorted by common name"

    for entry in species:
        assert "id" in entry and entry["id"]
        assert "name" in entry and entry["name"]
        assert "color" in entry
        assert "environment" in entry
        assert "model" in entry


def test_adding_species_profile_updates_catalog():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Copy existing profiles
        for p in (ROOT / "data/species").glob("*.json"):
            (tmp_path / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

        initial_cat = catalog.build_catalog(tmp_path)
        initial_count = initial_cat["total"]

        # Create new profile
        new_profile = {
            "schema_version": 1,
            "id": "test-super-fish",
            "common_name": "Test Super Fish",
            "scientific_name": "Superus pisces",
            "environment": "saltwater",
            "model": "grid",
            "display": {"color": "#ff00ff"},
            "factors": []
        }
        (tmp_path / "test-super-fish.json").write_text(json.dumps(new_profile), encoding="utf-8")

        updated_cat = catalog.build_catalog(tmp_path)
        assert updated_cat["total"] == initial_count + 1
        assert any(s["id"] == "test-super-fish" for s in updated_cat["species"])


def test_catalog_generation_succeeds_without_noaa_data():
    # Catalog builder reads local JSON files and requires no network or ocean satellite grids
    cat = catalog.build_catalog(ROOT / "data/species", generated_utc="2026-01-01T00:00:00+00:00")
    assert cat["generated_utc"] == "2026-01-01T00:00:00+00:00"
    assert cat["total"] == 130
