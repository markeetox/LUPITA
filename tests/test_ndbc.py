from pipeline.sources import ndbc

# Synthetic sample in the NDBC realtime2 layout (newest row first, "MM" = missing).
SAMPLE = """#YY  MM DD hh mm WDIR WSPD GST  WVHT   DPD   APD MWD   PRES  ATMP  WTMP  DEWP  VIS PTDY  TIDE
#yr  mo dy hr mn degT m/s  m/s     m   sec   sec degT   hPa  degC  degC  degC  nmi  hPa    ft
2026 10 09 12 00  90  5.0  6.0   1.2   7.0   5.5  80 1012.0  28.0  27.5  23.0   MM   MM    MM
2026 10 09 11 00  90  4.0  5.0   1.1   7.0   5.5  80 1012.5  28.0  27.4  23.0   MM   MM    MM
2026 10 09 10 00  80  4.0  5.0    MM    MM    MM  MM 1013.0  27.5  27.3  23.0   MM   MM    MM
2026 10 09 09 00  80  3.0  4.0   1.0   7.0   5.5  80 1014.0  27.0  27.2  22.5   MM   MM    MM
2026 10 08 12 00  70  3.0  4.0   1.0   7.0   5.5  80 1016.0  27.0  26.5  22.0   MM   MM    MM
"""
STATION = {"id": "TEST1", "name": "Test", "lat": 25.0, "lon": -80.0}


def test_parse_handles_missing_and_order():
    rows = ndbc.parse_realtime2(SAMPLE)
    assert len(rows) == 5
    assert rows[0]["time"] > rows[-1]["time"]
    assert rows[2]["WVHT"] is None


def test_summary_values_and_conversions():
    s = ndbc.summarize(STATION, ndbc.parse_realtime2(SAMPLE))
    assert s["water_temp_c"] == 27.5
    assert s["wind_kn"] == round(5.0 * 1.943844, 1)
    assert s["wave_height_m"] == 1.2
    # pressure 3 h earlier (09:00) was 1014.0, now 1012.0
    assert s["pressure_change_3h_hpa"] == -2.0
    # water temp 24 h earlier (Oct 8 12:00) was 26.5
    assert s["water_temp_change_24h_c"] == 1.0


def test_empty_file_is_not_ok():
    assert ndbc.summarize(STATION, ndbc.parse_realtime2(""))["ok"] is False
