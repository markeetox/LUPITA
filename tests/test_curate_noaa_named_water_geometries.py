import json

import pytest

pytest.importorskip("shapely")

from scripts.curate_noaa_named_water_geometries import curate


def _feature(objectid, name, cell):
    offset = objectid / 100000
    return {
        "type": "Feature",
        "id": objectid,
        "properties": {
            "OBJECTID": objectid,
            "OBJNAM": name,
            "DSNM": cell,
            "SORDAT": "20021005",
            "CATSEA": "mud flats" if name == "Biscayne Flats" else None,
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-80.2 + offset, 25.6],
                [-80.199 + offset, 25.6],
                [-80.199 + offset, 25.601],
                [-80.2 + offset, 25.601],
                [-80.2 + offset, 25.6],
            ]],
        },
    }


def test_curator_preserves_selected_noaa_source_geometries_and_writes_topology_audit(tmp_path):
    features = []
    objectid = 100
    for name, count in (
        ("Biscayne Bay", 37),
        ("Safety Valve", 4),
        ("Biscayne Flats", 3),
        ("Bear Cut", 1),
        ("Norris Cut", 1),
        ("Black Ledge", 3),
        ("Featherbed Bank", 1),
        ("Lewis Cut", 1),
        ("Biscayne Channel", 2),
        ("Sands Cut", 1),
        ("Snapper Creek Canal", 1),
        ("Goulds Canal", 1),
        ("Deering Channel", 1),
        ("Cape Florida Channel", 2),
    ):
        for index in range(count):
            features.append(_feature(objectid, name, f"CELL-{index % 2}"))
            objectid += 1

    source = tmp_path / "source.geojson"
    source.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
    audit = curate(source, tmp_path / "spatial")

    curated = json.loads((tmp_path / "spatial" / "noaa-biscayne-named-water-areas.geojson").read_text(encoding="utf-8"))
    assert len(curated["features"]) == 59
    assert {feature["properties"]["OBJNAM"] for feature in curated["features"]} == {
        "Biscayne Bay", "Safety Valve", "Biscayne Flats", "Bear Cut", "Norris Cut",
        "Black Ledge", "Featherbed Bank", "Lewis Cut", "Biscayne Channel",
        "Sands Cut", "Snapper Creek Canal", "Goulds Canal", "Deering Channel",
        "Cape Florida Channel",
    }
    bear = [feature for feature in curated["features"] if feature["properties"]["OBJNAM"] == "Bear Cut"]
    assert bear[0]["properties"]["lupita_context_id"] == "sf-bear-cut"
    assert bear[0]["properties"]["lupita_geometry_role"] == "charted_named_water_area_polygon"
    assert bear[0]["geometry"]["type"] == "Polygon"
    norris = [feature for feature in curated["features"] if feature["properties"]["OBJNAM"] == "Norris Cut"]
    assert norris[0]["properties"]["lupita_context_id"] == "sf-norris-cut"
    assert norris[0]["properties"]["OBJECTID"] == 145
    assert audit["source_feature_count"] == 59
    assert audit["groups"]["Biscayne Bay"]["feature_count"] == 37
    assert audit["groups"]["Safety Valve"]["feature_count"] == 4
    assert audit["groups"]["Biscayne Flats"]["feature_count"] == 3
    assert audit["groups"]["Bear Cut"]["objectids"] == [144]
    assert audit["groups"]["Norris Cut"]["objectids"] == [145]
    assert (tmp_path / "spatial" / "noaa-biscayne-named-water-topology-audit.json").exists()
    assert audit["groups"]["Black Ledge"]["feature_count"] == 3
    assert audit["groups"]["Featherbed Bank"]["feature_count"] == 1
    assert audit["groups"]["Biscayne Channel"]["feature_count"] == 2
    assert audit["groups"]["Cape Florida Channel"]["feature_count"] == 2
