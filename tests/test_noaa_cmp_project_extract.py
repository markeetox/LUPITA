import json
import zipfile
from pathlib import Path

import shapefile
from pyproj import CRS

from scripts.inspect_noaa_nsde_project_ui import extract_project_archives


def make_project_zip(tmp_path: Path) -> Path:
    base = tmp_path / "FLTEST_l1"
    writer = shapefile.Writer(str(base), shapeType=shapefile.POLYLINE)
    writer.field("FEATURE_ID", "N", decimal=0)
    writer.field("CLASS", "C", size=50)
    writer.field("ATTRIBUTE", "C", size=80)
    writer.field("INFORM", "C", size=20)
    writer.field("SRC_DATE", "C", size=8)
    writer.field("HOR_ACC", "C", size=8)
    writer.field("DATA_SOURC", "C", size=1)
    writer.line([[[-80.18, 25.76], [-80.17, 25.77]]])
    writer.record(1, "SHORELINE", "Natural.Mean High Water", "", "20190412", "2.3", "M")
    writer.line([[[-80.18, 25.75], [-80.17, 25.76]]])
    writer.record(2, "CONTOUR", "Depth Contour", "MLLW", "20180726", "3.0", "M")
    writer.close()
    base.with_suffix(".prj").write_text(CRS.from_epsg(4269).to_wkt(), encoding="utf-8")
    archive_path = tmp_path / "FLTEST.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        for ext in (".shp", ".shx", ".dbf", ".prj"):
            archive.write(base.with_suffix(ext), arcname=f"FLTEST_l1{ext}")
    return archive_path


def test_extract_project_archives_creates_separate_mhw_and_mllw_subsets(tmp_path):
    archive = make_project_zip(tmp_path)
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (output_dir / "FLTEST.zip").write_bytes(archive.read_bytes())

    audit = extract_project_archives(
        [{"project_id": "FLTEST", "archive_file": "FLTEST.zip"}],
        output_dir,
    )
    summary = audit["project_summaries"]["FLTEST"]
    geo = output_dir / "geojson"
    all_lines = json.loads((geo / "FLTEST_l1.geojson").read_text())
    mhw = json.loads((geo / "FLTEST_mhw.geojson").read_text())
    mllw = json.loads((geo / "FLTEST_mllw_depth_contours.geojson").read_text())

    assert summary["line_feature_count"] == 2
    assert summary["mhw_feature_count"] == 1
    assert summary["mllw_depth_contour_count"] == 1
    assert len(all_lines["features"]) == 2
    assert mhw["features"][0]["properties"]["ATTRIBUTE"] == "Natural.Mean High Water"
    assert mllw["features"][0]["properties"]["INFORM"] == "MLLW"
    assert mllw["features"][0]["properties"]["ATTRIBUTE"] == "Depth Contour"
    assert all_lines["features"][0]["properties"]["LUPITA_OUTPUT_CRS"] == "EPSG:4326"
