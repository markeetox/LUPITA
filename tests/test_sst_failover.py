import json
from pathlib import Path
from pipeline.layers import _fetch_grid

def test_sst_config_has_noaa_erddap_mirror_fallback():
    c=json.loads((Path(__file__).resolve().parents[1]/"config"/"sources.json").read_text()); s=c["erddap"]["sst"]
    assert s["dataset"]=="jplMURSST41" and s["base"]=="https://coastwatch.pfeg.noaa.gov/erddap"
    assert "https://upwell.pfeg.noaa.gov/erddap" in s["fallback_bases"]

def test_grid_fetch_retries_configured_erddap_mirror_after_primary_failure():
    cfg={"base":"https://primary.example/erddap","fallback_bases":["https://mirror.example/erddap"],"dataset":"sample","variable":"analysed_sst","dims":["time","latitude","longitude"]}; calls=[]
    def fetch(url):
        calls.append(url)
        if "primary.example" in url: raise RuntimeError("temporary HTTP 503")
        return ("time,latitude,longitude,analysed_sst\nUTC,degrees_north,degrees_east,degree_C\n2026-11-13T18:00:00Z,25.0,-80.0,28.5\n")
    _,_,grid,stamp,units=_fetch_grid(cfg,{"lat":[25,25],"lon":[-80,-80]},fetch)
    assert len(calls)==2 and "primary.example" in calls[0] and "mirror.example" in calls[1]
    assert grid[0,0]==28.5 and stamp=="2026-11-13T18:00:00Z" and units=="degree_C"
