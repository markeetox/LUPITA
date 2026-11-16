import math

import pytest

from requests import HTTPError, Response

from scripts.compare_hfr_products import PRODUCTS, _describe_request_failure, build_url, parse_csv, render_markdown, summarize


def _csv(dataset_time="2026-11-13T04:00:00Z"):
    rows = [
        "time,latitude,longitude,water_u,water_v,hdop,number_of_sites,number_of_radials",
        "UTC,degrees_north,degrees_east,m s-1,m s-1,1,count,count",
        f"{dataset_time},25.5,-80.0,0.2,0.4,0.8,3,18",
        f"{dataset_time},25.5,-79.9,NaN,0.3,1.2,2,9",
        f"{dataset_time},25.6,-80.0,-327.67,0.1,0.9,3,12",
        f"{dataset_time},25.6,-79.9,0.1,0.2,0.7,4,20",
    ]
    return "\n".join(rows)


def test_build_url_requests_exact_time_region_and_all_quality_fields():
    url = build_url("https://example.test/erddap", "ucsdHfrE2", "2026-11-13T04:00:00Z")
    assert "ucsdHfrE2.csv?" in url
    assert "water_u[(2026-11-13T04:00:00Z)]" in url
    assert "water_v[(2026-11-13T04:00:00Z)]" in url
    assert "hdop[" in url and "number_of_sites[" in url and "number_of_radials[" in url
    assert "[(24.0):1:(28.5)]" in url and "[(-83.5):1:(-78.0)]" in url


def test_parser_preserves_missing_vectors_and_rejects_wrong_timestamp():
    product = PRODUCTS[1]
    grid = parse_csv(_csv(), product, "2026-11-13T04:00:00Z", "https://example.test")
    assert grid.values["water_u"][0][0] == 0.2
    assert math.isnan(grid.values["water_u"][0][1])
    assert math.isnan(grid.values["water_u"][1][0])
    with pytest.raises(ValueError, match="No nearest-time substitution"):
        parse_csv(_csv("2026-11-13T05:00:00Z"), product, "2026-11-13T04:00:00Z", "url")


def test_summary_uses_paired_vectors_and_native_grid_denominator():
    grid = parse_csv(_csv(), PRODUCTS[1], "2026-11-13T04:00:00Z", "url")
    summary = summarize(grid)
    assert summary["grid"]["nominal_grid_cells"] == 4
    assert summary["grid"]["valid_vector_cells"] == 2
    assert summary["grid"]["valid_vector_fraction"] == 0.5
    assert summary["quality"]["hdop_median_valid_vectors"] == 0.75
    assert summary["quality"]["number_of_sites_median_valid_vectors"] == 3.5
    assert summary["spatial_distribution"]["possible_half_degree_tiles"] == 99
    assert summary["spatial_distribution"]["denominator_scope"] == "fixed requested region, shared by all products"


def test_summary_includes_keys_biscayne_and_offshore_boxes():
    grid = parse_csv(_csv(), PRODUCTS[1], "2026-11-13T04:00:00Z", "url")
    subregions = summarize(grid)["subregions"]
    assert set(subregions) == {"Florida Keys", "Biscayne Bay", "Offshore grounds"}
    assert subregions["Biscayne Bay"]["grid_cells"] == 4


def test_timestamp_must_include_timezone():
    from scripts.compare_hfr_products import compare
    with pytest.raises(ValueError, match="timezone"):
        compare("2026-11-13T04:00:00")


def test_markdown_report_uses_valid_code_spans_without_escape_warnings():
    grid = parse_csv(_csv(), PRODUCTS[1], "2026-11-13T04:00:00Z", "https://example.test")
    report = {
        "requested_time": "2026-11-13T04:00:00Z",
        "products": [summarize(grid)],
        "failures": [],
    }
    markdown = render_markdown(report)
    assert "\\`" not in markdown
    assert "`2026-11-13T04:00:00Z`" in markdown


def test_http_failure_report_includes_redirect_chain_and_response_body():
    first = Response()
    first.status_code = 302
    first.url = "https://upwell.example/request"
    first.headers["Location"] = "https://coastwatch.example/request"
    final = Response()
    final.status_code = 404
    final.url = "https://coastwatch.example/request"
    final._content = b"dataset ID not found"
    final.history = [first]
    error = HTTPError("404 Client Error", response=final)

    detail = _describe_request_failure("https://upwell.example", error)
    assert "302 https://upwell.example/request -> https://coastwatch.example/request" in detail
    assert "404 https://coastwatch.example/request" in detail
    assert "dataset ID not found" in detail
