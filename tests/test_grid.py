import numpy as np

from pipeline import grid


def test_resample_linear_field_is_exact():
    lats, lons = np.array([25.0, 25.1, 25.2]), np.array([-80.0, -79.9, -79.8])
    field = 2 * lats[:, None] + 3 * lons[None, :]
    dl, dn = np.array([25.05, 25.15]), np.array([-79.95, -79.85])
    out = grid.resample(field, lats, lons, dl, dn)
    assert np.allclose(out, 2 * dl[:, None] + 3 * dn[None, :])


def test_resample_nan_and_outside():
    lats, lons = np.array([25.0, 25.1, 25.2]), np.array([-80.0, -79.9, -79.8])
    field = np.ones((3, 3)); field[1, 1] = np.nan
    out = grid.resample(field, lats, lons, np.array([25.1, 26.0]), np.array([-79.9]))
    assert np.isnan(out[0, 0])      # centre is missing and has no valid neighbours at that exact point
    assert np.isnan(out[1, 0])      # outside the source grid


def test_components_and_hull():
    m = np.zeros((5, 5), bool); m[0, 0:2] = True; m[3:5, 3:5] = True
    sizes = sorted(len(c) for c in grid.components(m))
    assert sizes == [2, 4]
    hull = grid.convex_hull([(0, 0), (1, 0), (1, 1), (0, 1), (0.5, 0.5)])
    assert len(hull) == 4


def test_web_mercator_resampling_peaks_at_known_latitudes():
    import base64
    from pipeline.predict import quantize_scores, resample_latitude_web_mercator

    # 1. Construct synthetic grid spanning 15.0°N to 60.0°N
    lats = np.linspace(15.0, 60.0, 901)   # step 0.05
    lons = np.linspace(-100.0, -70.0, 301)
    H, W = len(lats), len(lons)
    dlat = float(lats[1] - lats[0])

    # Distinctive peaks at ~25.5°N and ~40.0°N
    idx_255 = np.argmin(np.abs(lats - 25.5))
    idx_400 = np.argmin(np.abs(lats - 40.0))

    score = np.zeros((H, W))
    score[idx_255, 100] = 0.95
    score[idx_400, 200] = 0.85

    # Resample to Web Mercator Y rows
    resampled = resample_latitude_web_mercator(score, lats)

    # Calculate expected Mercator Y target rows
    s_lat = float(lats[0]) - dlat / 2.0
    n_lat = float(lats[-1]) + dlat / 2.0
    y_s = np.log(np.tan(np.pi / 4.0 + np.radians(s_lat) / 2.0))
    y_n = np.log(np.tan(np.pi / 4.0 + np.radians(n_lat) / 2.0))

    k = np.arange(H)
    y_k = y_n - (k + 0.5) * (y_n - y_s) / H
    target_lats = np.degrees(2.0 * np.arctan(np.exp(y_k)) - np.pi / 2.0)

    # Verify peak at 25.5°N
    col_255 = resampled[:, 100]
    peak_row_255 = np.argmax(col_255)
    assert abs(target_lats[peak_row_255] - 25.5) < dlat

    # Verify peak at 40.0°N
    col_400 = resampled[:, 200]
    peak_row_400 = np.argmax(col_400)
    assert abs(target_lats[peak_row_400] - 40.0) < dlat

    # Verify North/South orientation: higher latitude peak (40°N) must appear at a smaller row index (closer to North)
    assert peak_row_400 < peak_row_255, "North row first: 40°N row index must be less than 25.5°N row index"


def test_quantize_scores_and_partition_preserves_peaks():
    import base64
    from pipeline.predict import quantize_scores

    lats = np.linspace(15.0, 60.0, 901)
    lons = np.linspace(-100.0, -70.0, 301)
    H, W = len(lats), len(lons)

    idx_peak = np.argmin(np.abs(lats - 25.5))
    score = np.zeros((H, W))
    score[idx_peak:idx_peak+2, 150] = 0.92

    b64_str = quantize_scores(score, lats)
    decoded = np.frombuffer(base64.b64decode(b64_str), dtype=np.uint8).reshape((H, W))

    # Output dimensions preserved
    assert decoded.shape == (H, W)

    # Quantized peak value is ~92
    r, c = np.unravel_index(np.argmax(decoded), decoded.shape)
    assert decoded[r, c] == 92
    assert c == 150, "Longitude column must be exact"


def test_web_mercator_edge_and_nan_handling():
    from pipeline.predict import resample_latitude_web_mercator

    lats = np.linspace(15.0, 60.0, 91)
    score = np.full((91, 10), np.nan)
    score[40, 5] = 0.80

    resampled = resample_latitude_web_mercator(score, lats)
    assert resampled.shape == (91, 10)
    assert not np.isnan(resampled).all()
