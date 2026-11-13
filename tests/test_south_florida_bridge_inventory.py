from scripts.extract_south_florida_bridge_inventory import (
    BBOX,
    SOURCES,
    fetch_source,
    validate_feature,
)


def line_feature():
    return {
        "type": "Feature",
        "properties": {"OBJECTID": 7, "BRIDGE_NO": 874544, "STREETNAME": "Bear Cut Bridge"},
        "geometry": {
            "type": "LineString",
            "coordinates": [[-80.20, 25.74], [-80.16, 25.74]],
        },
    }


def test_sources_are_official_local_and_state_bridge_inventories():
    assert SOURCES["miamidade_dtpw_bridge_lines"]["layer_id"] == 1
    assert "Miami-Dade" in SOURCES["miamidade_dtpw_bridge_lines"]["publisher"]
    assert SOURCES["fdot_rci_bridge_lines"]["layer_id"] == 1
    assert "Florida Department of Transportation" in SOURCES["fdot_rci_bridge_lines"]["publisher"]


def test_fetch_source_uses_biscayne_extent_and_preserves_bridge_attributes():
    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"features": [line_feature()]}

    class Session:
        def __init__(self):
            self.calls = []

        def get(self, url, params, timeout):
            self.calls.append((url, params, timeout))
            return Response()

    session = Session()
    definition = SOURCES["miamidade_dtpw_bridge_lines"]
    collection, summary = fetch_source(session, definition)
    url, params, _ = session.calls[0]
    assert url.endswith("/EAMS_Map/MapServer/1/query")
    assert params["geometry"] == "-80.55,25.2,-80.05,26.1"
    assert params["geometryType"] == "esriGeometryEnvelope"
    assert params["inSR"] == "4326"
    assert params["outSR"] == "4326"
    assert collection["features"][0]["properties"]["BRIDGE_NO"] == 874544
    assert summary["feature_count"] == 1
    assert summary["output_crs"] == "EPSG:4326"
    assert BBOX == (-80.55, 25.20, -80.05, 26.10)


def test_validate_rejects_out_of_range_coordinates():
    feature = line_feature()
    feature["geometry"]["coordinates"][1] = [-181, 25.74]
    try:
        validate_feature(feature)
    except ValueError as exc:
        assert "outside EPSG:4326" in str(exc)
    else:
        raise AssertionError("Expected invalid longitude to be rejected")
