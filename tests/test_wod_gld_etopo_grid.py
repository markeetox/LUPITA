from __future__ import annotations

import numpy as np
import pandas as pd
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
    rows = []
    elevations = [-10.0, 2.0, -0.5, -99999.0]
    for iy in range(2):
        for ix in range(2):
            lat = 25.0 + iy * GRID_RESOLUTION_DEG
            lon = 279.0 + ix * GRID_RESOLUTION_DEG
            z = elevations[iy * 2 + ix]
            rows.append(f"{lat},{lon},{z}")
    csv_text = (
        "latitude,longitude,z\n"
        "degrees_north,degrees_east,meters\n"
        + "\n".join(rows)
        + "\n"
    )

    frame = parse_etopo_csv(csv_text)
    assert frame.longitude.min() < 0
    assert frame.loc[0, "etopo_class"] == "ocean"
    assert frame.loc[0, "seafloor_depth_m"] == pytest.approx(10.0)
    assert "land" in set(frame.etopo_class)
    assert "coast_ambiguous" in set(frame.etopo_class)
    assert "missing" in set(frame.etopo_class)
    assert frame.etopo_elevation_m.isna().sum() == 1


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
    frame = pd.DataFrame(rows[:-1])
    with pytest.raises(ValueError, match="Incomplete ETOPO rectangle"):
        validate_grid(frame)


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
    info = validate_grid(pd.DataFrame(rows))
    assert info["rows"] == 4
    assert info["latitude_count"] == 2
    assert info["longitude_count"] == 2
