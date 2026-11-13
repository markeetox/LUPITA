import json

import pytest

from scripts.audit_noaa_shoreline_services import (
    LAYERS,
    SERVICE,
    fetch_layer,
    validate_geojson_feature,
)


def line_feature(object_id=1, name="historic shoreline"):
    return {
        "type": "Feature",
        "properties": {"OBJECTID": object_id, "F_NAME": name},
        "geometry": {
            "type": "LineString",
            "coordinates": [[-80.18, 25.76], [-80.17, 25.77]],
        },
    }


def test_validate_shoreline_lines_and_reject_bad_geometry():
    validate_geojson_feature(line_feature())
    feature = line_feature()
    feature["geometry"]["coordinates"][0] = [181, 25.76]
    with pytest.raises(ValueError, match="outside EPSG:4326"):
        validate_geojson_feature(feature)
    feature["geometry"] = {"type": "Polygon", "coordinates": []}
    with pytest.raises(ValueError, match="Expected shoreline line geometry"):
        validate_geojson_feature(feature)


def test_fetch_noaa_composite_shoreline_preserves_source_geometry(tmp_path):
    definition = LAYERS["noaa_composite_shoreline_mhw"]

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
            if url == f"{SERVICE}/41":
                return Response({
                    "name": "NOAA Composite Shoreline",
                    "geometryType": "esriGeometryPolyline",
                    "maxRecordCount": 4000,
                    "fields": [{"name": "OBJECTID"}, {"name": "F_NAME"}],
                    "extent": {"spatialReference": {"wkid": 6439}},
                })
            if params.get("returnIdsOnly") == "true":
                envelope = json.loads(params["geometry"])
                assert envelope["spatialReference"]["wkid"] == 4326
                assert envelope["xmin"] == -80.45
                return Response({"objectIds": [1, 2]})
            ids = [int(value) for value in params["objectIds"].split(",")]
            return Response({"features": [line_feature(value) for value in ids]})

    session = Session()
    metadata, summary = fetch_layer(session, definition, tmp_path)
    output = json.loads((tmp_path / definition["output_file"]).read_text())
    assert metadata["name"] == "NOAA Composite Shoreline"
    assert summary["feature_count"] == 2
    assert summary["attribute_counts"] == {"historic shoreline": 2}
    assert output["features"][0]["geometry"]["type"] == "LineString"
    assert output["features"][0]["properties"]["F_NAME"] == "historic shoreline"
    assert session.calls[0][0] == f"{SERVICE}/41"
    assert session.calls[1][1]["returnIdsOnly"] == "true"


def test_noaa_mhhw_layer_is_kept_as_separate_datum_product():
    assert LAYERS["noaa_mhhw_screening_line"]["id"] == 40
    assert LAYERS["noaa_mhhw_screening_line"]["datum"] == "MHHW"
    assert LAYERS["noaa_composite_shoreline_mhw"]["datum"] == "MHW"
    assert LAYERS["noaa_mhhw_screening_line"]["output_file"] != LAYERS[
        "noaa_composite_shoreline_mhw"
    ]["output_file"]
