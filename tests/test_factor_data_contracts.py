"""End-to-end factor contract checks across active profiles and runtime inputs.

The goal is to catch drift between the species catalog, factor dispatch, and layer builder.
This test inspects layer availability using deterministic fake source responses; it makes no network calls.
"""
import json
from pathlib import Path

from pipeline.layers import load_layers
from pipeline.scoring import factor_score
from pipeline.sites import VALUE_FUNCS, score_value
from pipeline.species_validator import GRID_FACTORS, SITE_FACTORS
from tests.test_structure import _profiles, _sources, fake_arcgis, fake_erddap

ROOT = Path(__file__).resolve().parent.parent
SUPPORTED_GRID_KINDS = {"range", "category", "higher_is_better", "season"}
SUPPORTED_SITE_KINDS = {"range", "category", "season"}


def test_every_active_grid_factor_has_engine_dispatch_and_layer_input():
    profiles = [p for p in _profiles() if p.get("model", "grid") == "grid"]
    assert profiles
    errors = []
    layers = load_layers(_sources(), errors, fetch=fake_erddap, fetch_arc=fake_arcgis)
    assert not errors

    active = [
        (profile["id"], factor)
        for profile in profiles
        for factor in profile["factors"]
        if factor.get("active") and factor.get("weight", 0) > 0
    ]
    assert active
    for species_id, factor in active:
        param, kind = factor["param"], factor["kind"]
        assert param in GRID_FACTORS, f"{species_id}: {param} has no declared grid dispatch"
        assert kind in GRID_FACTORS[param], f"{species_id}: {param}/{kind} is not declared grid-compatible"
        assert kind in SUPPORTED_GRID_KINDS, f"{species_id}: {param}/{kind} has no grid scorer implementation"
        if kind != "season":
            assert param in layers, f"{species_id}: {param} is not exposed by the layer builder"

        # Exercise the real grid scorer with a deterministic synthetic value,
        # independently of whether today's optional source layer is populated.
        synthetic = {"sst_c": __import__("numpy").full((5, 5), 25.0),
                     "depth_m": __import__("numpy").full((5, 5), 100.0),
                     "month": 6}
        if kind == "season":
            pass
        elif kind == "category":
            categories = list((factor.get("map") or {}).keys()) or factor.get("preferred") or ["reef"]
            synthetic[param] = __import__("numpy").full((5, 5), categories[0], dtype=object)
        else:
            synthetic[param] = __import__("numpy").full((5, 5), 25.0)
        result = factor_score(factor, synthetic, {})
        assert result is not None, f"{species_id}: real grid scorer did not dispatch {param}/{kind}"


def test_every_active_site_factor_has_engine_dispatch_and_a_real_value_function():
    profiles = [p for p in _profiles() if p.get("model") == "sites"]
    assert profiles
    active = [
        (profile["id"], factor)
        for profile in profiles
        for factor in profile["factors"]
        if factor.get("active") and factor.get("weight", 0) > 0
    ]
    assert active
    for species_id, factor in active:
        param, kind = factor["param"], factor["kind"]
        assert param in SITE_FACTORS, f"{species_id}: {param} has no declared site dispatch"
        assert kind in SITE_FACTORS[param], f"{species_id}: {param}/{kind} is not declared site-compatible"
        assert kind in SUPPORTED_SITE_KINDS, f"{species_id}: {param}/{kind} has no site scorer implementation"
        assert param in VALUE_FUNCS, f"{species_id}: {param} has no site input function"
        assert callable(VALUE_FUNCS[param])
        if kind == "range":
            value = sum(factor["ideal"]) / 2
        elif kind == "category":
            value = next(iter(factor.get("map") or {}), None)
            if value is None:
                value = (factor.get("preferred") or [""])[0]
        else:
            value = 6
        assert score_value(factor, value) is not None, f"{species_id}: real site scorer did not dispatch {param}/{kind}"
        if param == "distance_to_inlet":
            raise AssertionError(f"{species_id}: placeholder distance_to_inlet must not be active")


def test_grid_layer_builder_exposes_every_declared_factor_input():
    """All declared grid factors must map to a layer key or the calendar context."""
    errors = []
    layers = load_layers(_sources(), errors, fetch=fake_erddap, fetch_arc=fake_arcgis)
    assert not errors
    declared = set(GRID_FACTORS)
    missing = sorted(param for param in declared - {"spawning_season", "season_presence"}
                     if param not in layers)
    assert not missing, f"Grid factors without a layer-builder output: {missing}"
