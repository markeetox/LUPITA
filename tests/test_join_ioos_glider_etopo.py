import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "join_ioos_glider_etopo.py"
spec = importlib.util.spec_from_file_location("join_ioos_glider_etopo", SCRIPT)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def test_parse_etopo_csvp_with_units():
    text = "latitude (degrees_north),longitude (degrees_east),z (m)\n27.5,275.5,-40\n27.508333,275.508333,-41\n"
    cells = module.parse_etopo_csvp(text)
    assert len(cells) == 2
    assert cells[0] == {"latitude": 27.5, "longitude": 275.5, "z": -40.0}


def test_build_etopo_url_converts_negative_longitudes_to_360():
    rows = [{"precise_lat": "27.7", "precise_lon": "-83.3"}]
    url = module.build_etopo_url(rows)
    assert "275." in url
    assert "27." in url
    assert url.startswith(module.ETOPO_BASE + ".csvp?")


def test_join_rows_preserves_negative_separation_and_qc():
    rows = [
        {"profile_id": "p1", "precise_time": "2024-02-16T00:00:00Z", "precise_lat": "27.5",
         "precise_lon": "-84.5", "depth": "45", "temperature": "18.2",
         "qartod_temperature_primary_flag": "1"},
        {"profile_id": "p1", "precise_time": "2024-02-16T00:01:00Z", "precise_lat": "27.5",
         "precise_lon": "-84.5", "depth": "55", "temperature": "18.1",
         "qartod_temperature_primary_flag": "3"},
    ]
    cells = [
        {"latitude": 27.5, "longitude": 275.5, "z": -50},
        {"latitude": 27.5, "longitude": 275.5083333333, "z": -50},
        {"latitude": 27.5083333333, "longitude": 275.5, "z": -50},
        {"latitude": 27.5083333333, "longitude": 275.5083333333, "z": -50},
    ]
    joined, summary = module.join_rows(rows, cells)
    assert joined[0]["bottom_separation_m_screening_only"] == 5
    assert joined[1]["bottom_separation_m_screening_only"] == -5
    assert summary["negative_separation_rows_preserved"] == 1
    assert summary["near_bottom_sensitivity_nonnegative_separation_only"]["5"]["primary_qc_pass_rows"] == 1


def test_join_rows_classifies_land_and_coastal_ambiguous():
    rows = [
        {"profile_id": "p1", "precise_time": "2024-02-16T00:00:00Z", "precise_lat": "27.5",
         "precise_lon": "-84.5", "depth": "5", "temperature": "18.2"},
        {"profile_id": "p2", "precise_time": "2024-02-16T00:01:00Z", "precise_lat": "27.5",
         "precise_lon": "-84.4916666667", "depth": "5", "temperature": "18.1"},
    ]
    cells = [
        {"latitude": 27.5, "longitude": 275.5, "z": 5},
        {"latitude": 27.5, "longitude": 275.5083333333, "z": 0},
        {"latitude": 27.5083333333, "longitude": 275.5, "z": 5},
        {"latitude": 27.5083333333, "longitude": 275.5083333333, "z": 0},
    ]
    joined, summary = module.join_rows(rows, cells)
    assert {row["etopo_class"] for row in joined} == {"land", "coastal_ambiguous"}
    assert summary["ocean_rows_with_separation"] == 0


def test_profile_summary_reports_signed_min_max_and_qc_counts():
    rows = [
        {"profile_id": "p1", "precise_time": "2024-02-16T00:00:00Z", "precise_lat": "27.5",
         "precise_lon": "-84.5", "depth": "45", "temperature": "18.2",
         "qartod_temperature_primary_flag": "1"},
        {"profile_id": "p1", "precise_time": "2024-02-16T00:01:00Z", "precise_lat": "27.5",
         "precise_lon": "-84.5", "depth": "55", "temperature": "18.1",
         "qartod_temperature_primary_flag": "3"},
    ]
    cells = [
        {"latitude": 27.5, "longitude": 275.5, "z": -50},
        {"latitude": 27.5, "longitude": 275.5083333333, "z": -50},
        {"latitude": 27.5083333333, "longitude": 275.5, "z": -50},
        {"latitude": 27.5083333333, "longitude": 275.5083333333, "z": -50},
    ]
    joined, _ = module.join_rows(rows, cells)
    profile = module.build_profile_summary(joined)[0]
    assert profile["minimum_signed_separation_m"] == -5
    assert profile["maximum_signed_separation_m"] == 5
    assert profile["negative_separation_rows"] == 1
    assert profile["within_5m_rows"] == 1
    assert profile["within_5m_primary_qc_pass_rows"] == 1
