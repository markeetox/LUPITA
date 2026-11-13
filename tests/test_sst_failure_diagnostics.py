import json
from datetime import datetime,timezone
from pathlib import Path
from pipeline.run import build_data_quality,build_pipeline_health

def test_downstream_layers_are_not_reported_as_failed_when_sst_stops_loading():
    s=json.loads((Path(__file__).resolve().parents[1]/"config"/"sources.json").read_text()); e=["layers sst: temporary HTTP 503"]
    q=build_data_quality(None,s,e,datetime(2026,11,13,tzinfo=timezone.utc)); L=q["layers"]
    assert L["sst"]["status"]=="failed" and L["chlorophyll"]["status"]=="not_attempted" and L["currents"]["status"]=="not_attempted"
    assert L["currents"]["freshness"]["status"]=="not_assessed" and "never started" in L["currents"]["not_attempted_reason"]
    h=build_pipeline_health(q,False,e); assert h["status"]=="failed"
    assert not any("currents" in x or "chlorophyll" in x for x in h["freshness_issues"]+h["optional_layer_issues"])
