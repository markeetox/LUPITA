import json
from pathlib import Path
from pipeline.publication import prepare_publication

def put(p,d): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d),encoding="utf-8")
def test_failed_refresh_restores_last_good_snapshot_and_writes_current_status(tmp_path):
    pub,prev=tmp_path/"publish",tmp_path/"previous"
    put(pub/"latest.json",{"generated_utc":"2026-11-13T19:00:00Z","fish_updated":False,"pipeline_health":{"status":"failed","prediction_refreshed":False,"critical_issues":["SST failed"]},"errors":["upstream outage"]})
    put(pub/"fish.json",{"generated_utc":"stale-checkout"}); put(prev/"fish.json",{"generated_utc":"last-good"})
    put(prev/"api/v1/index.json",{"generated_utc":"2026-11-13T18:00:00Z"}); put(prev/"api/v1/species/snook.json",{"id":"snook"})
    r=prepare_publication(pub,prev)
    assert json.loads((pub/"fish.json").read_text())["generated_utc"]=="last-good"
    assert json.loads((pub/"api/v1/index.json").read_text())["generated_utc"]=="2026-11-13T18:00:00Z"
    assert json.loads((pub/"latest.json").read_text())["prediction_snapshot"]["status"]=="last_known_good"
    assert r["prediction_refreshed"] is False and json.loads((pub/"api/v1/refresh.json").read_text())["status"]=="failed"
def test_successful_refresh_keeps_current_snapshot(tmp_path):
    pub,prev=tmp_path/"publish",tmp_path/"previous"
    put(pub/"latest.json",{"generated_utc":"2026-11-13T19:00:00Z","fish_updated":True,"pipeline_health":{"status":"healthy","prediction_refreshed":True},"errors":[]})
    put(pub/"api/v1/index.json",{"generated_utc":"2026-11-13T19:00:00Z"}); put(prev/"fish.json",{"generated_utc":"older"}); put(pub/"fish.json",{"generated_utc":"current"})
    r=prepare_publication(pub,prev)
    assert json.loads((pub/"fish.json").read_text())["generated_utc"]=="current" and r["prediction_snapshot"]["status"]=="refreshed"
