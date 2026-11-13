import json

import pytest

from scripts.audit_noaa_shoreline_services import (
    ARCGIS_CUSP_LAYER,
    fetch_cusp_shoreline,
    validate_geojson_feature,
)


def line_feature(object_id=1, source_id="FL2317-CS-N"):
    return {
        "type": "Feature",
        "properties": {
            "OBJECTID": object_id,
            "SOURCE_ID": source_id,
            "SRC_DATE": "2023-10-21",
            "ATTRIBUTE": "MHW",
        },
        "geometry": {
            "type": "LineString",
            "coordinates": [[-80.18, 25.76], [-80.17, 25.77]],
        },
    }


def test_validate_cusp_lines_and_reject_bad_geometry():
    validate_geojson_feature(line_feature())
    feature = line_feature()
    feature["geometry"]["coordinates"][0] = [181, 25.76]
    with pytest.raises(ValueError, match="outside EPSG:4326"):
        validate_geojson_feature(feature)
    feature["geometry"] = {"type": "Polygon", "coordinates": []}
    with pytest.raises(ValueError, match="Expected shoreline line geometry"):
        validate_geojson_feature(feature)


def test_fetch_cusp_shoreline_preserves_geometry_and_source_fields(tmp_path):
    class Response:
        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self.payload

    class Session:
        def __init__(self):
            self.headers = {}
            self.calls = []

        def get(self, url, params, timeout):
            self.calls.append((url, params, timeout))
            if url == ARCGIS_CUSP_LAYER:
                return Response({
                    "name": "CUSPLine",
                    "geometryType": "esriGeometryPolyline",
                    "maxRecordCount": 2000,
                    "fields": [{"name": "SOURCE_ID"}, {"name": "SRC_DATE"}],
                    "editingInfo": {"lastEditDate": 123456},
                })
            if params.get("returnIdsOnly") == "true":
                return Response({"objectIds": [1, 2]})
            ids = [int(value) for value in params["objectIds"].split(",")]
            return Response({"features": [line_feature(value) for value in ids]})

    session = Session()
    metadata, summary = fetch_cusp_shoreline(session, tmp_path)
    output = json.loads((tmp_path / "noaa_cusp_biscayne_shoreline.geojson").read_text())
    assert metadata["name"] == "CUSPLine"
    assert summary["feature_count"] == 2
    assert summary["source_id_counts"] == {"FL2317-CS-N": 2}
    assert summary["source_date_counts"] == {"2023-10-21": 2}
    assert output["features"][0]["geometry"]["type"] == "LineString"
    assert output["features"][0]["properties"]["SOURCE_ID"] == "FL2317-CS-N"
    assert session.calls[0][0] == ARCGIS_CUSP_LAYER
    assert session.calls[1][1]["returnIdsOnly"] == "true"


def test_empty_cusp_area_returns_valid_empty_collection(tmp_path):
    class Response:
        def __init__(self, payload):
            self.payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self.payload

    class Session:
        def __init__(self):
            self.headers = {}

        def get(self, url, params, timeout):
            if url == ARCGIS_CUSP_LAYER:
                return Response({"geometryType": "esriGeometryPolyline", "fields": []})
            return Response({"objectIds": []})

    _, summary = fetch_cusp_shoreline(Session(), tmp_path)
    output = json.loads((tmp_path / "noaa_cusp_biscayne_shoreline.geojson").read_text())
    assert summary["feature_count"] == 0
    assert output["features"] == []
