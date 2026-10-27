import numpy as np
from pipeline import grid, scoring, sites

def test_marine_mask_excludes_inland_lakes():
    # Grid where boundary is ocean, inner ring is land, inner core is lake
    depth = np.full((50, 50), 30.0) # 30m deep ocean
    depth[10:40, 10:40] = np.nan    # land ring
    depth[20:30, 20:30] = 10.0      # inland lake

    marine = grid.build_marine_mask(depth)
    assert marine[5, 5] is True or marine[5, 5] == 1
    assert marine[25, 25] is False or marine[25, 25] == 0

def test_scoring_marine_mask_and_lat_range_filtering():
    lats = np.array([25.0, 35.0, 45.0])
    lons = np.array([-80.0, -80.0, -80.0])
    sst = np.array([26.0, 26.0, 26.0])

    # marine mask: only lat=25.0 is ocean, others false
    marine_mask = np.array([True, False, False])[:, None] # 3x1
    depth = np.array([20.0, 10.0, 10.0])[:, None]

    layers = {
        "sst_c": sst[:, None],
        "lats": lats,
        "lons": lons,
        "depth_m": depth,
        "marine_mask": marine_mask
    }

    profile = {
        "id": "tropical-snapper",
        "environment": "saltwater",
        "lat_range": [15.0, 30.0],
        "min_coverage": 0.5,
        "factors": [
            {
                "param": "sst_c",
                "kind": "range",
                "range": [20, 30],
                "ideal": [24, 28],
                "weight": 1.0,
                "active": True
            }
        ]
    }

    res = scoring.score_species(profile, layers)
    score = res["score"]
    assert np.isfinite(score[0, 0]) # lat 25 is eligible
    assert np.isnan(score[1, 0])    # lat 35 excluded by lat_range and marine_mask
    assert np.isnan(score[2, 0])    # lat 45 excluded

def test_sites_lat_range_filtering():
    profile = {
        "id": "snook",
        "site_kinds": ["inlet"],
        "lat_range": [15.0, 31.0],
        "factors": []
    }

    all_sites = [
        {"name": "South Florida Inlet", "kind": "inlet", "lat": 25.7, "lon": -80.1},
        {"name": "Halifax Inlet", "kind": "inlet", "lat": 44.6, "lon": -63.5}
    ]

    ctx = {"layers": {}, "conditions": None}
    reg = {}

    res = sites.score_sites(profile, all_sites, ctx, reg)
    # Halifax Inlet at 44.6 N should be excluded by lat_range [15.0, 31.0]
    items = res.get("items", [])
    for item in items:
        assert "Halifax" not in item["title"]
