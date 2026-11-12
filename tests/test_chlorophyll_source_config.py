import json
from pathlib import Path


def test_unvalidated_chlorophyll_gapfill_stays_disabled_without_fallback():
    config = json.loads((Path(__file__).resolve().parents[1] / "config" / "sources.json").read_text())
    gapfilled = config["erddap"]["chlorophyll_gapfilled"]

    assert gapfilled["enabled"] is False
    assert "fallback_bases" not in gapfilled
