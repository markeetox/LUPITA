import pytest
from shapely.geometry import LineString, box

from scripts.audit_noaa_cmp_spatial_alignment import (
    line_polygon_overlay,
    polygon_area_comparison,
)


def test_polygon_area_comparison_keeps_overlap_and_denominators_explicit():
    left = box(0, 0, 10, 10)
    right = box(5, 0, 15, 10)
    result = polygon_area_comparison(left, right)
    assert result["first_area_km2"] == 0.0
    assert result["second_area_km2"] == 0.0
    assert result["intersection_area_km2"] == 0.0
    assert result["first_area_intersection_pct"] == 50.0
    assert result["second_area_intersection_pct"] == 50.0


def test_line_polygon_overlay_reports_inside_outside_without_reclassifying():
    line = LineString([(-5, 5), (15, 5)])
    polygon = box(0, 0, 10, 10)
    result = line_polygon_overlay(line, polygon)
    assert result["total_line_length_km"] == 0.02
    assert result["inside_polygon_length_km"] == 0.01
    assert result["outside_polygon_length_km"] == 0.01
    assert result["inside_line_length_pct"] == 50.0
    assert result["minimum_distance_to_polygon_boundary_m"] == 0.0
