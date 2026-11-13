import json
from scripts.reconcile_biscayne_landmark_topology import analyze_card_sound, analyze_jewfish, analyze_jewfish_depth, analyze_rickenbacker

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
        feature(246221,"Jewfish Creek",polygon(-80.389,25.184,-80.387,25.186),DSNM="US5FL5GL.000",SORDAT="200304"),
        feature(246228,"Jewfish Creek",polygon(-80.387,25.184,-80.385,25.186),DSNM="US5FL5HL.000",SORDAT="200304"),
        feature(246231,"Barnes Sound",polygon(-80.3855,25.184,-80.383,25.186))])
    write(tmp_path/"jewfish_creek_layer_84.geojson",[feature(1,None,line(-80.39,25.184,-80.388,25.184))])
    result=analyze_jewfish(tmp_path)
    assert result["source_objectids"]==[246221,246228]
    assert result["union_component_count"]==1 and result["polygon_gap_m"]==0
    assert result["station_8723613"]["inside_mapped_creek_polygon"] is False
    assert result["named_water_relations"][0]["name"]=="Barnes Sound"\n    assert result["named_water_relations"][0]["overlap_area_m2"]>0\n    assert result["named_water_relations"][0]["shared_boundary_m"]==0

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

def test_jewfish_depth_context_preserves_chart_depth_classes(tmp_path):
    write(tmp_path/"jewfish_creek_layer_104.geojson",[
        feature(10,None,line(-80.389,25.184,-80.387,25.184),VALDCO=0.9),
        feature(11,None,line(-80.38,25.184,-80.379,25.184),VALDCO=1.8)])
    write(tmp_path/"jewfish_creek_layer_227.geojson",[
        feature(20,None,polygon(-80.389,25.184,-80.388,25.185),DRVAL1=0,DRVAL2=0.9),
        feature(21,None,polygon(-80.38,25.184,-80.379,25.185),DRVAL1=0.9,DRVAL2=1.8)])
    from shapely.geometry import shape
    from pyproj import Transformer
    from shapely.ops import transform
    project=Transformer.from_crs("EPSG:4326","EPSG:26917",always_xy=True).transform
    creek=transform(project,shape(polygon(-80.39,25.183,-80.385,25.186)))
    result=analyze_jewfish_depth(tmp_path,creek)
    assert sum(x["feature_count"] for x in result["depth_contours"])==2
    assert sum(x["feature_count"] for x in result["depth_areas"])==2
    assert result["encoded_depth_unit"]=="metres"
    assert "not populated" in result["vertical_datum"]
    assert result["depth_contours"][0]["line_length_inside_named_creek_m"]>0
