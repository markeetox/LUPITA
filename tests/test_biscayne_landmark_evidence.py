from scripts.extract_biscayne_landmark_evidence import CARD_SOUND_OBJECTIDS, REGIONS, fetch_layer, summarize, validate_feature

def feature(objectid=1,name="Example",chart="US5FL000.000"):
    return {"type":"Feature","properties":{"OBJECTID":objectid,"OBJNAM":name,"DSNM":chart,"SORDAT":"2020-01-01"},
            "geometry":{"type":"LineString","coordinates":[[-80.4,25.2],[-80.3,25.3]]}}

def test_exact_card_sound_objectids_are_preserved():
    assert CARD_SOUND_OBJECTIDS == [246233,246243,246247,246258,246267,246284]

def test_regional_queries_are_local_and_layer_classes_separate():
    assert set(REGIONS["rickenbacker_causeway"]["layers"]) == {84,87,118,233}
    assert set(REGIONS["jewfish_creek"]["layers"]) == {41,84,104,132,205,227,237}
    assert REGIONS["jewfish_creek"]["bbox"] == [-80.43,25.14,-80.34,25.23]

def test_fetch_layer_uses_exact_objectids():
    class Response:
        status_code=200
        def raise_for_status(self): pass
        def json(self): return {"features":[feature(246233,"Card Sound")]}
    class Session:
        def __init__(self): self.calls=[]
        def get(self,url,params,timeout): self.calls.append((url,params,timeout)); return Response()
    session=Session()
    rows=fetch_layer(session,237,objectids=[246233])
    url,params,_=session.calls[0]
    assert url.endswith("/MapServer/237/query")
    assert params["objectIds"]=="246233" and "geometry" not in params
    assert rows[0]["properties"]["OBJNAM"]=="Card Sound"

def test_fetch_layer_uses_local_bbox():
    class Response:
        status_code=200
        def raise_for_status(self): pass
        def json(self): return {"features":[feature()]}
    class Session:
        def get(self,url,params,timeout): self.params=params; return Response()
    session=Session()
    assert len(fetch_layer(session,104,bbox=[-80.43,25.14,-80.34,25.23]))==1
    assert session.params["geometry"]=="-80.43,25.14,-80.34,25.23"
    assert session.params["inSR"]=="4326"

def test_validation_rejects_invalid_coordinates():
    bad=feature()
    bad["geometry"]["coordinates"][1]=[-181,25.3]
    try: validate_feature(bad)
    except ValueError as exc: assert "outside EPSG:4326" in str(exc)
    else: raise AssertionError("Expected invalid longitude to be rejected")

def test_summary_keeps_ids_chart_cells_names_and_dates():
    result=summarize([feature(246233,"Card Sound","US5FL5IL.000")])
    assert result["objectids"]==[246233]
    assert result["feature_name_counts"]=={"Card Sound":1}
    assert result["chart_cell_counts"]=={"US5FL5IL.000":1}
    assert result["source_date_counts"]=={"2020-01-01":1}
