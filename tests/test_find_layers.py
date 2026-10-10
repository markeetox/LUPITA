from pipeline import find_layers as f


def test_parse_layers_and_count():
    info = {"layers": [{"id": 12, "name": "Artificial Reef Locations"}, {"name": "bad"}]}
    assert f.parse_layers(info) == [{"id": 12, "name": "Artificial Reef Locations"}]
    assert f.parse_count({"count": 41}) == 41 and f.parse_count({}) is None


def test_bbox_is_lon_lat_order():
    assert f.bbox_param({"lat": [24.5, 27.0], "lon": [-81.0, -78.5]}) == "-81.0,24.5,-78.5,27.0"
