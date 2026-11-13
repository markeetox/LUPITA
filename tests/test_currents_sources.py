import numpy as np

from pipeline.layers import load_layers

LATS=[25.0,25.1,25.2,25.3]
LONS=[-80.3,-80.2,-80.1,-80.0]

def csv_data(dataset, missing=False):
    rows=[]
    if dataset=="sst-test":
        header="time,latitude,longitude,analysed_sst"; units="UTC,degrees_north,degrees_east,degree_C"
        for la in LATS:
            for lo in LONS: rows.append(f"2026-11-13T12:00:00Z,{la},{lo},28.0")
    elif dataset=="hfr-test":
        header="time,latitude,longitude,water_u,water_v,hdop,number_of_sites,number_of_radials"; units="UTC,degrees_north,degrees_east,m s-1,m s-1,1,count,count"
        for i,la in enumerate(LATS):
            for j,lo in enumerate(LONS):
                u,v=(1.0,0.2)
                if missing and i==1 and j==1: u,v="",""
                rows.append(f"2026-11-13T12:00:00Z,{la},{lo},{u},{v},0.8,3,20")
    else:
        header="time,latitude,longitude,ugos,vgos"; units="UTC,degrees_north,degrees_east,m s-1,m s-1"
        for la in LATS:
            for lo in LONS: rows.append(f"2026-11-13T11:00:00Z,{la},{lo},0.1,0.4")
    return "\n".join([header,units,*rows])

def sources():
    return {"region":{"name":"test","lat":[25.0,25.3],"lon":[-80.3,-80.0]},"erddap":{
        "sst":{"enabled":True,"base":"https://example.test/erddap","dataset":"sst-test","variable":"analysed_sst","dims":["time","latitude","longitude"]},
        "currents":{"enabled":True,"base":"https://example.test/erddap","dataset":"hfr-test","variables":["water_u","water_v","hdop","number_of_sites","number_of_radials"],"dims":["time","latitude","longitude"],"query_region":{"lat":[25.0,25.3],"lon":[-80.3,-80.0]}},
        "currents_fallback":{"enabled":True,"base":"https://example.test/erddap","dataset":"alt-test","variables":["ugos","vgos"],"dims":["time","latitude","longitude"]},
        "chlorophyll":{"enabled":False},"chlorophyll_gapfilled":{"enabled":False},"bathymetry":{"enabled":False}},
        "arcgis":{"artificial_reefs":{"enabled":False},"natural_reef":{"enabled":False},"unified_benthic":{"enabled":False}},"closures":{"enabled":False}}

def test_hfr_vectors_overlay_altimetry_and_report_provenance():
    def fetch(url):
        if "sst-test" in url:return csv_data("sst-test")
        if "hfr-test" in url:return csv_data("hfr-test",True)
        if "alt-test" in url:return csv_data("alt-test")
        raise AssertionError(url)
    layers=load_layers(sources(),[],fetch=fetch)
    info=layers["currents_info"]
    assert info["primary"]["loaded"] and info["fallback"]["loaded"]
    assert info["blend_mode"]=="HF Radar where valid; satellite altimetry elsewhere"
    assert info["primary"]["quality"]["hdop_median"]==0.8
    assert info["combined_aligned_valid_fraction"]==1.0
    assert np.isclose(layers["current_speed"][0,0],np.hypot(1.0,0.2)*1.943844)
    assert np.isclose(layers["current_speed"][1,1],np.hypot(0.1,0.4)*1.943844)
    assert layers["times"]["currents"]=="2026-11-13T12:00:00Z"
    assert layers["times"]["stream_edge"]=="2026-11-13T11:00:00Z"

def test_altimetry_still_loads_when_hf_radar_fails():
    errors=[]
    def fetch(url):
        if "sst-test" in url:return csv_data("sst-test")
        if "hfr-test" in url:raise RuntimeError("HF Radar unavailable")
        if "alt-test" in url:return csv_data("alt-test")
        raise AssertionError(url)
    layers=load_layers(sources(),errors,fetch=fetch)
    assert not layers["currents_info"]["primary"]["loaded"]
    assert layers["currents_info"]["fallback"]["loaded"]
    assert layers["currents_info"]["selected_source"]=="NOAA satellite altimetry fallback"
    assert np.isfinite(layers["current_speed"]).any()
    assert any(e.startswith("layers currents primary:") for e in errors)
