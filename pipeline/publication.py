"""Prepare a safe static publication after a pipeline refresh."""
from __future__ import annotations
import argparse, json, shutil
from pathlib import Path
PREDICTION_FILES=("fish.json","heat.json","stream.json","closures.json")
PREDICTION_DIRS=("api","heat")
def _read_json(path:Path)->dict:
    try:
        value=json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value,dict) else {}
    except (OSError,json.JSONDecodeError): return {}
def prepare_publication(publish_dir:Path,previous_dir:Path)->dict:
    latest_path=publish_dir/"latest.json"; latest=_read_json(latest_path); health=latest.get("pipeline_health") or {}
    refreshed=bool(health.get("prediction_refreshed",latest.get("fish_updated",False)))
    if not refreshed and previous_dir.exists():
        for name in PREDICTION_FILES:
            src,dst=previous_dir/name,publish_dir/name
            if src.is_file(): dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
        for name in PREDICTION_DIRS:
            src,dst=previous_dir/name,publish_dir/name
            if src.is_dir():
                if dst.exists(): shutil.rmtree(dst)
                shutil.copytree(src,dst)
    index=_read_json(publish_dir/"api"/"v1"/"index.json"); snapshot_time=index.get("generated_utc")
    snapshot_status="refreshed" if refreshed and snapshot_time else ("last_known_good" if snapshot_time else "unavailable")
    snapshot={"status":snapshot_status,"generated_utc":snapshot_time,"source":"current_refresh" if refreshed and snapshot_time else ("previous_data_branch" if snapshot_time else None)}
    latest["prediction_snapshot"]=snapshot; latest_path.parent.mkdir(parents=True,exist_ok=True)
    latest_path.write_text(json.dumps(latest,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    refresh={"api_version":1,"generated_utc":latest.get("generated_utc"),"status":health.get("status","unknown"),"prediction_refreshed":refreshed,
             "prediction_snapshot":snapshot,"critical_issues":health.get("critical_issues",[]),"optional_layer_issues":health.get("optional_layer_issues",[]),
             "freshness_issues":health.get("freshness_issues",[]),"errors":latest.get("errors",[])}
    out=publish_dir/"api"/"v1"/"refresh.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(refresh,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    return refresh
def main():
    p=argparse.ArgumentParser(); p.add_argument("--publish-dir",type=Path,required=True); p.add_argument("--previous-dir",type=Path,required=True); a=p.parse_args()
    r=prepare_publication(a.publish_dir,a.previous_dir); print(f"Publication prepared: refresh={r['status']}, prediction_snapshot={r['prediction_snapshot']['status']}")
if __name__=="__main__": main()
