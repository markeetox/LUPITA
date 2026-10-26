from pipeline import closures as C


def test_classify_fishing_restriction_text():
    assert C.classify("Recreational Fishing Prohibited") == "no_fishing"
    assert C.classify("Commercial Fishing Restricted and Recreational Fishing Prohibited") == "no_fishing"
    assert C.classify("Recreational Fishing Restricted") == "restricted"
    assert C.classify("No Site Restrictions") == "other" and C.classify(None) == "other"


def test_clockwise_outer_ring_and_counter_clockwise_hole():
    outer = [[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]          # clockwise
    hole = [[2, 2], [8, 2], [8, 8], [2, 8], [2, 2]]               # counter-clockwise
    mp = C.rings_to_multipolygon([outer, hole, [[20, 20], [20, 22], [22, 22], [22, 20], [20, 20]]])
    assert len(mp) == 2 and len(mp[0]) == 2 and len(mp[1]) == 1


def test_parse_keeps_only_no_fishing_and_cleans_urls():
    feats = [
        {"attributes": {"Site_Name": "A", "Fish_Rstr": "Recreational Fishing Prohibited", "URL": "https://x.org", "Estab_Yr": 1997},
         "geometry": {"rings": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]}},
        {"attributes": {"Site_Name": "B", "Fish_Rstr": "Recreational Fishing Restricted"}, "geometry": {"rings": [[[0, 0]]]}},
        {"attributes": {"Site_Name": "C", "Fish_Rstr": "Recreational Fishing Prohibited", "URL": "javascript:alert(1)"},
         "geometry": {"rings": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]}}]
    areas = C.parse_closures(feats)
    assert [a["name"] for a in areas] == ["A", "C"]
    assert areas[0]["url"] == "https://x.org" and areas[1]["url"] == ""       # only http(s) links survive
    gj = C.to_geojson(areas, "src", True, "t")
    assert gj["loaded"] is True and len(gj["features"]) == 2 and gj["features"][0]["geometry"]["type"] == "MultiPolygon"
