from __future__ import annotations

import math

from scripts.join_wod_gld_etopo import bathymetry_at, load_etopo


def make_grid(tmp_path):
    path = tmp_path / "etopo.csv"
    path.write_text(
        "latitude,longitude,etopo_elevation_m,seafloor_depth_m,etopo_class\n"
        "25.000000,-80.000000,-100.0,100.0,ocean\n"
        "25.000000,-79.99166666666667,-120.0,120.0,ocean\n"
        "25.008333333333333,-80.000000,-140.0,140.0,ocean\n"
        "25.008333333333333,-79.99166666666667,-160.0,160.0,ocean\n",
        encoding="utf-8",
    )
    return load_etopo(path)


def test_nearest_cell_and_bilinear_interpolation(tmp_path):
    grid = make_grid(tmp_path)
    result = bathymetry_at(25.0041665, -79.9958335, grid)
    assert result["etopo_class"] == "ocean"
    assert result["seafloor_depth_m"] in (100.0, 120.0, 140.0, 160.0)
    assert math.isclose(result["bilinear_seafloor_depth_m"], 130.0, abs_tol=0.01)
    assert result["grid_cell_offset_m"] >= 0


def test_bilinear_is_not_returned_across_land(tmp_path):
    grid = make_grid(tmp_path)
    cell = grid["cells"][(25.008333333333333, -79.99166666666667)]
    cell["class"] = "land"
    result = bathymetry_at(25.0041665, -79.9958335, grid)
    assert result["bilinear_seafloor_depth_m"] is None
