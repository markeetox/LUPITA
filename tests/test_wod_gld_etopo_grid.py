from __future__ import annotations

import pytest

from scripts.export_wod_gld_etopo_grid import (
    GRID_RESOLUTION_DEG,
    build_request_url,
    parse_etopo_csv,
    validate_grid,
)


def test_request_uses_full_30_arcsecond_stride_and_lon360():
    url = build_request_url()
    assert ".csv?" in url
    assert "):1:(" in url
    assert "278.95" in url
    assert "280.55" in url


def test_parse_normalizes_longitude_and_classifies_elevation():
    lines = ["latitude,longitude,z", "degrees_north,degrees_east,meters"]
    elevations = [-10.0, 2.0, -0.5, -99999.0]
    for iy in range(2):
        for ix in range(2):
            lat = 25.0 + iy * GRID_RESOLUTION_DEG
            lon = 279.0 + ix * GRID_RESOLUTION_DEG
            z = elevations[iy * 2 + ix]
            lines.append(f"{lat},{lon},{z}")

    rows = parse_etopo_csv("\n".join(lines) + "\n")
    assert rows[0]["longitude"] < 0
    assert rows[0]["etopo_class"] == "ocean"
    assert rows[0]["seafloor_depth_m"] == pytest.approx(10.0)
    assert {row["etopo_class"] for row in rows} == {
        "ocean", "land", "coast_ambiguous", "missing"
    }
    assert sum(row["etopo_elevation_m"] is None for row in rows) == 1


def test_validate_grid_rejects_missing_cells():
    rows = []
    for iy in range(2):
        for ix in range(2):
            rows.append({
                "latitude": 25.0 + iy * GRID_RESOLUTION_DEG,
                "longitude": -81.0 + ix * GRID_RESOLUTION_DEG,
                "etopo_elevation_m": -10.0,
                "seafloor_depth_m": 10.0,
                "etopo_class": "ocean",
            })
    with pytest.raises(ValueError, match="Incomplete ETOPO rectangle"):
        validate_grid(rows[:-1])


def test_validate_grid_accepts_complete_regular_grid():
    rows = []
    for iy in range(2):
        for ix in range(2):
            rows.append({
                "latitude": 25.0 + iy * GRID_RESOLUTION_DEG,
                "longitude": -81.0 + ix * GRID_RESOLUTION_DEG,
                "etopo_elevation_m": -10.0,
                "seafloor_depth_m": 10.0,
                "etopo_class": "ocean",
            })
    info = validate_grid(rows)
    assert info["rows"] == 4
    assert info["latitude_count"] == 2
    assert info["longitude_count"] == 2
