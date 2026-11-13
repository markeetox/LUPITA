import pytest
from shapely.geometry import LineString

from scripts.audit_noaa_cmp_mhw_topology import endpoint_component_count, closest_relationship


def test_exact_endpoint_components_do_not_snap_nearby_lines():
    features = [
        {"geometry": LineString([(0, 0), (1, 0)])},
        {"geometry": LineString([(1, 0), (2, 0)])},
        {"geometry": LineString([(2.0001, 0), (3, 0)])},
    ]
    result = endpoint_component_count(features)
    assert result["component_count_by_exact_shared_endpoints"] == 2
    assert result["shared_endpoint_coordinate_count"] == 1
    assert result["degree_1_endpoint_coordinate_count"] == 4


def test_closest_relationship_reports_geometry_and_endpoint_separately():
    first = [{"geometry": LineString([(0, 0), (10, 0)]), "feature_id": "A"}]
    second = [{"geometry": LineString([(10, 0.01), (20, 0.01)]), "feature_id": "B"}]
    result = closest_relationship(first, second)
    assert result["minimum_line_geometry_distance_m"] == pytest.approx(0.01)
    assert result["minimum_endpoint_to_endpoint_distance_m"] == pytest.approx(0.01)
    assert result["minimum_endpoint_feature_ids"] == ["A", "B"]


def test_missing_mhw_features_are_not_reported_as_zero_gap():
    assert closest_relationship([], [{"geometry": LineString([(0, 0), (1, 0)])}]) == {
        "status": "not_comparable_no_mhw_features"
    }
