import pytest

from scripts.extract_noaa_biscayne_hydrography import LAYERS, fetch_channels, validate_feature


def polygon_feature():
    return {
        "type": "Feature",
        "properties": {"OBJECTID": 12, "OBJNAM": "Example maintained channel", "DSNM": "US5FL??"},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-80.3, 25.5], [-80.2, 25.5],
                [-80.2, 25.6], [-80.3, 25.5],
            ]],
        },
    }


def test_validate_accepts_polygon_and_line_geometries():
    validate_feature(polygon_feature())
    line = polygon_feature()
    line["geometry"] = {"type": "LineString", "coordinates": [[-80.3, 25.5], [-80.2, 25.6]]}
    validate_feature(line)


def test_validate_rejects_bad_coordinates():
    feature = polygon_feature()
    feature["geometry"]["coordinates"][0][1] = [181, 25.5]
    with pytest.raises(ValueError, match="outside EPSG:4326"):
        validate_feature(feature)


def test_fetch_channels_queries_biscayne_bbox_and_preserves_source_attributes():
    class Response:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {"features": [polygon_feature()]}

    class Session:
        def __init__(self):
            self.calls = []

        def get(self, url, params, timeout):
            self.calls.append((url, params, timeout))
            return Response()

    session = Session()
    collection, summary = fetch_channels(session)
    url, params, timeout = session.calls[0]
    assert url.endswith("/MarineTransportation/MapServer/1/query")
    assert params["geometry"] == "-80.55,25.2,-80.05,26.1"
    assert params["geometryType"] == "esriGeometryEnvelope"
    assert params["outSR"] == "4326"
    assert params["outFields"] == "*"
    assert collection["features"][0]["properties"]["OBJNAM"] == "Example maintained channel"
    assert summary["feature_count"] == 1
    assert summary["feature_name_counts"] == {"Example maintained channel": 1}
    assert summary["output_crs"] == "EPSG:4326"



def test_route_crosswalk_layers_are_included_as_navigation_context_only():
    expected = {
        "harbor_fairway_areas": 208,
        "harbor_deep_water_route_areas": 207,
        "harbor_two_way_route_areas": 216,
        "harbor_recommended_route_centerlines": 133,
    }
    assert {key: LAYERS[key]["id"] for key in expected} == expected
    assert all("navigation" in LAYERS[key]["description"].lower() for key in expected)
