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
    ):
        for index in range(count):
            features.append(_feature(objectid, name, f"CELL-{index % 2}"))
            objectid += 1

    source = tmp_path / "source.geojson"
    source.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
    audit = curate(source, tmp_path / "spatial")

    curated = json.loads((tmp_path / "spatial" / "noaa-biscayne-named-water-areas.geojson").read_text(encoding="utf-8"))
    assert len(curated["features"]) == 46
    assert {feature["properties"]["OBJNAM"] for feature in curated["features"]} == {
        "Biscayne Bay", "Safety Valve", "Biscayne Flats", "Bear Cut"
    }
    bear = [feature for feature in curated["features"] if feature["properties"]["OBJNAM"] == "Bear Cut"]
    assert bear[0]["properties"]["lupita_context_id"] == "sf-bear-cut"
    assert bear[0]["properties"]["lupita_geometry_role"] == "charted_named_water_area_polygon"
    assert bear[0]["geometry"]["type"] == "Polygon"
    assert audit["source_feature_count"] == 46
    assert audit["groups"]["Biscayne Bay"]["feature_count"] == 37
    assert audit["groups"]["Safety Valve"]["feature_count"] == 4
    assert audit["groups"]["Biscayne Flats"]["feature_count"] == 3
    assert audit["groups"]["Bear Cut"]["objectids"] == [144]
    assert audit["groups"]["Norris Cut"]["objectids"] == [145]
    assert (tmp_path / "spatial" / "noaa-biscayne-named-water-topology-audit.json").exists()
