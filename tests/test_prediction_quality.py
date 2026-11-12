import json

import numpy as np

from pipeline import api, sites


def _site_profile(factor_count=3):
    factors = [
        {"param": "sst_c", "kind": "range", "weight": 0.4, "active": True,
         "range": [20, 35], "ideal": [25, 30]},
        {"param": "tide_stage", "kind": "category", "weight": 0.3, "active": True,
         "preferred": ["rising"]},
        {"param": "time_of_day", "kind": "category", "weight": 0.3, "active": True,
         "preferred": ["day"]},
    ]
    return {"factors": factors[:factor_count], "site_kinds": ["flat"],
            "min_score_report": 0.5}


def _ctx():
    return {"layers": {"closure_cover": None}, "conditions": None}


def test_site_title_uses_actual_site_kind_and_not_inlet(monkeypatch):
    monkeypatch.setitem(sites.VALUE_FUNCS, "sst_c",
                        lambda site, ctx: (27.0, "measured", {"text": "27 C"}))
    monkeypatch.setitem(sites.VALUE_FUNCS, "tide_stage",
                        lambda site, ctx: ("rising", "modeled", {"text": "Rising tide"}))
    monkeypatch.setitem(sites.VALUE_FUNCS, "time_of_day",
                        lambda site, ctx: ("day", "modeled", {"text": "Daylight"}))
    site = {"name": "Safety Valve Flats", "kind": "flat", "lat": 25.3,
            "lon": -80.2, "radius_km": 1.0}

    result = sites.score_sites(_site_profile(), [site], _ctx(), {})

    assert result["items"]
    assert result["items"][0]["title"] == "Safety Valve Flats (flat)"


def test_single_factor_site_model_has_low_confidence_even_with_full_input_coverage(monkeypatch):
    monkeypatch.setitem(sites.VALUE_FUNCS, "sst_c",
                        lambda site, ctx: (27.0, "measured", {"text": "27 C"}))
    site = {"name": "Government Cut", "kind": "flat", "lat": 25.3,
            "lon": -80.2, "radius_km": 1.0}

    result = sites.score_sites(_site_profile(1), [site], _ctx(), {})
    item = result["items"][0]

    assert item["data_coverage"] == 1.0
    assert item["environmental_data_coverage"] == 1.0
    assert item["confidence"] == "Low"
    assert "limited_model_inputs" in item["confidence_basis"]
    assert item["active_factor_count"] == 1


def test_api_v1_exposes_confidence_basis_and_input_timestamps():
    spot = {"id": "snook-1", "title": "Test cut", "score": 0.8,
            "confidence": "Low", "confidence_basis": ["limited_model_inputs"],
            "active_factor_count": 1, "data_coverage": 1.0,
            "environmental_data_coverage": 1.0, "coords": [-80.2, 25.3],
            "ring": [], "reasons": [], "location": []}
    area = api._area(spot)
    assert area["confidence_basis"] == ["limited_model_inputs"]
    assert area["active_factor_count"] == 1
    assert area["environmental_data_coverage"] == 1.0

    fish = {"generated_utc": "2026-11-12T18:00:00+00:00",
            "layers": {"times": {"sst": "2026-11-10T09:00:00Z"},
                       "datasets": {"sst": "example-dataset"}},
            "species": [], "spots": []}
    files = api.build(fish, None, None, None, [])
    index = json.loads(files["index.json"])
    assert index["data_quality"]["input_times"]["sst"] == "2026-11-10T09:00:00Z"
    assert index["data_quality"]["datasets"]["sst"] == "example-dataset"
