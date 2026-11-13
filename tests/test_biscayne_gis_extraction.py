import pytest

from scripts.extract_biscayne_bay_gis import extract_layer, validate_feature


def polygon_feature():
    return {
        "type": "Feature",
        "properties": {
            "OBJECTID": 1,
            "FIRST_Source": "Biscayne Bay FWC",
            "FIRST_ClassLv1": "Seagrass (Continuous)",
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-80.2, 25.5], [-80.1, 25.5],
                [-80.1, 25.6], [-80.2, 25.5],
            ]],
        },
    }


def test_validate_accepts_wgs84_polygon():
    validate_feature(polygon_feature())


def test_validate_rejects_non_polygon():
    feature = polygon_feature()
    feature["geometry"] = {
        "type": "LineString",
        "coordinates": [[-80.2, 25.5], [-80.1, 25.6]],
    }
    with pytest.raises(ValueError, match="Expected polygon"):
        validate_feature(feature)


def test_validate_rejects_out_of_range_coordinate():
    feature = polygon_feature()
    feature["geometry"]["coordinates"][0][1] = [181, 25.5]
    with pytest.raises(ValueError, match="outside EPSG:4326"):
        validate_feature(feature)


def test_extract_layer_paginates_and_summarizes():
    class Response:
        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self):
            pass

        def json(self):
            return self.payload

    class Session:
        def __init__(self):
            self.calls = []

        def get(self, url, params, timeout):
            self.calls.append(params["resultOffset"])
            if params["resultOffset"] == 0:
                return Response({
                    "features": [polygon_feature()],
                    "exceededTransferLimit": True,
                })
            return Response({"features": []})

    session = Session()
    collection, summary = extract_layer(
        session, "test",
        {"id": 7, "where": "FIRST_Source LIKE '%Biscayne Bay%'",
         "description": "test source"},
    )
    assert session.calls == [0, 1]
    assert collection["type"] == "FeatureCollection"
    assert summary["feature_count"] == 1
    assert summary["output_crs"] == "EPSG:4326"
    assert summary["source_counts"] == {"Biscayne Bay FWC": 1}
    assert summary["habitat_class_counts"] == {"Seagrass (Continuous)": 1}


def test_extract_layer_uses_layer_specific_service_and_name_attribute():
    class Response:
        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self):
            pass

        def json(self):
            return self.payload

    class Session:
        def __init__(self):
            self.url = None

        def get(self, url, params, timeout):
            self.url = url
            assert params["where"] == "1=1"
            feature = polygon_feature()
            feature["properties"] = {"OBJECTID": 9, "NAME": "BISCAYNE BAY AQUATIC PRESERVE"}
            other = polygon_feature()
            other["properties"] = {"OBJECTID": 10, "NAME": "FLORIDA KEYS AQUATIC PRESERVE"}
            return Response({"features": [feature, other]})

    session = Session()
    _, summary = extract_layer(
        session, "preserve",
        {
            "id": 0,
            "service": "https://fdep.example/MapServer",
            "where": "1=1",
            "filter_attribute": "NAME",
            "filter_contains": "BISCAYNE BAY",
            "description": "preserve test",
        },
    )
    assert session.url == "https://fdep.example/MapServer/0/query"
    assert summary["service_url"] == "https://fdep.example/MapServer/0"
    assert summary["raw_feature_count"] == 2
    assert summary["feature_count"] == 1
    assert summary["source_counts"] == {"BISCAYNE BAY AQUATIC PRESERVE": 1}
