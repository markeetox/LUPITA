import json
from scripts.reconcile_biscayne_landmark_topology import analyze_card_sound, analyze_jewfish, analyze_rickenbacker

def feature(oid, name, geom, **props):
    return {"type":"Feature","properties":{"OBJECTID":oid,"OBJNAM":name,**props},"geometry":geom}

def polygon(x1,y1,x2,y2):
    return {"type":"Polygon","coordinates":[[[x1,y1],[x2,y1],[x2,y2],[x1,y2],[x1,y1]]]}

def line(x1,y1,x2,y2):
    return {"type":"LineString","coordinates":[[x1,y1],[x2,y2]]}

def write(path, features):
    path.write_text(json.dumps({"type":"FeatureCollection","features":features}),encoding="utf-8")

def test_jewfish_polygons_contiguous_and_station_not_promoted(tmp_path):
    write(tmp_path/"jewfish_creek_layer_237.geojson",[
        feature(246221,"Jewfish Creek",polygon(-80.391,25.183,-80.389,25.185),DSNM="US5FL5GL.000",SORDAT="200304"),
        feature(246228,"Jewfish Creek",polygon(-80.389,25.183,-80.387,25.185),DSNM="US5FL5HL.000",SORDAT="200304"),
        feature(246231,"Barnes Sound",polygon(-80.387,25.183,-80.385,25.185))])
    write(tmp_path/"jewfish_creek_layer_84.geojson",[feature(1,None,line(-80.39,25.184,-80.388,25.184))])
    result=analyze_jewfish(tmp_path)
    assert result["source_objectids"]==[246221,246228]
    assert result["union_component_count"]==1 and result["polygon_gap_m"]==0
    assert result["station_8723613"]["inside_mapped_creek_polygon"] is False
    assert result["named_water_relations"][0]["name"]=="Barnes Sound"

def test_card_sound_requires_exact_source_objectids(tmp_path):
    ids=[246233,246243,246247,246258,246267,246284]
    write(tmp_path/"noaa_card_sound_named_water.geojson",[
        feature(oid,"Card Sound",polygon(-80.35+i*.001,25.30,-80.349+i*.001,25.301),DSNM="chart",SORDAT="200304")
        for i,oid in enumerate(ids)])
    result=analyze_card_sound(tmp_path)
    assert result["feature_count"]==6
    assert {x["objectid"] for x in result["features"]}==set(ids)

def test_rickenbacker_bridge_lines_remain_separate(tmp_path):
    write(tmp_path/"rickenbacker_causeway_layer_233.geojson",[
        feature(691847,"Rickenbacker Causeway",polygon(-80.20,25.74,-80.19,25.75),DSNM="chart")])
    write(tmp_path/"rickenbacker_causeway_layer_84.geojson",[
        feature(12,None,line(-80.20,25.745,-80.19,25.745),DSNM="chart",SORDAT="20050201")])
    write(tmp_path/"rickenbacker_causeway_layer_87.geojson",[
        feature(21070,"South West 2nd Avenue Bridge",line(-80.18,25.745,-80.17,25.745),DSNM="chart")])
    write(tmp_path/"rickenbacker_causeway_layer_118.geojson",[])
    result=analyze_rickenbacker(tmp_path)
    assert result["objectid"]==691847
    assert result["intersecting_coastline_features"][0]["objectid"]==12
    assert result["bridge_features_in_query_bbox"][0]["name"]=="South West 2nd Avenue Bridge"
    assert result["bridge_features_in_query_bbox"][0]["distance_to_named_land_polygon_m"]>0
