from datetime import datetime, timezone
from pathlib import Path
import importlib.util

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_south_florida_temperatures.py"
SPEC = importlib.util.spec_from_file_location("temperature_audit", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_parse_usgs_fixed_gmt_minus_four():
    stamp = MODULE.parse_usgs_time("06/01/2024 12:15")
    assert stamp is not None
    assert stamp.utcoffset().total_seconds() == -4 * 3600
    assert stamp.astimezone(timezone.utc).hour == 16


def test_read_usgs_wide_csv_normalizes_known_biscayne_site():
    content = (
        '"Time, GMT-04:00","Brewster","Unknown Site"\n'
        '"06/01/2024 12:15","29.25","28.5"\n'
        '"06/01/2024 12:30","","28.6"\n'
    )
    start = datetime(2024, 6, 1, tzinfo=timezone.utc)
    end = datetime(2024, 6, 2, tzinfo=timezone.utc)
    rows = MODULE.read_usgs_csv(content, start, end)
    brewster = [row for row in rows if row["site"] == "Brewster"]
    assert len(brewster) == 1
    assert brewster[0]["temperature_c"] == 29.25
    assert brewster[0]["latitude"] == 25.56676
    assert brewster[0]["sensor_depth_m"] == 3.9624


def test_parse_float_rejects_fill_and_nonphysical_values():
    assert MODULE.parse_float("-9999") is None
    assert MODULE.parse_float("nan") is None
    assert MODULE.parse_float("29.1") == 29.1



def test_mur_fallback_uses_each_mirror_without_replaying_primary(monkeypatch, tmp_path):
    calls = []

    class FakeResponse:
        def __init__(self, url, status_code, text):
            self.url = url
            self.status_code = status_code
            self.text = text
            self.headers = {}

        def raise_for_status(self):
            if self.status_code >= 400:
                raise MODULE.requests.HTTPError(
                    f"HTTP {self.status_code}", response=self
                )

    def fake_get(url, **kwargs):
        calls.append(url)
        if "coastwatch.pfeg.noaa.gov" in url:
            return FakeResponse(url, 503, "temporary primary outage")
        csv_text = (
            "time,latitude,longitude,analysed_sst\\n"
            "UTC,degrees_north,degrees_east,degree_C\\n"
            "2024-01-01T09:00:00Z,25.57,-80.10,25.4\\n"
        )
        return FakeResponse(url, 200, csv_text)

    monkeypatch.setattr(MODULE.requests, "get", fake_get)
    rows, errors, warnings = MODULE.fetch_mur(
        None, "Brewster", 25.56676, -80.09974,
        datetime(2024, 1, 1, tzinfo=timezone.utc),
        datetime(2024, 1, 1, tzinfo=timezone.utc),
        tmp_path,
    )

    assert len(calls) == 2
    assert "coastwatch.pfeg.noaa.gov" in calls[0]
    assert "erddap.marine.usf.edu" in calls[1]
    assert rows[0]["mur_source_host"] == "erddap.marine.usf.edu"
    assert errors == []
    assert len(warnings) == 1
