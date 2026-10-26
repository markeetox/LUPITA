from pipeline import find_stations as f

XML = """<stations created="2026-10-09T00:00:00UTC" count="3">
<station id="vakf1" lat="25.731" lon="-80.162" name="8723214 - Virginia Key, FL" type="fixed" met="y"/>
<station id="41114" lat="27.551" lon="-80.225" name="Fort Pierce, FL" type="buoy" met="y"/>
<station id="46001" lat="56.3" lon="-148.0" name="Gulf of Alaska" type="buoy" met="y"/>
</stations>"""


def test_ids_uppercased_and_names_cleaned():
    s = {x["id"]: x for x in f.parse_active(XML)}
    assert "VAKF1" in s and s["VAKF1"]["name"] == "Virginia Key, FL"


def test_box_and_distance():
    s = {x["id"]: x for x in f.parse_active(XML)}
    assert f.in_box(s["VAKF1"]) and not f.in_box(s["46001"])
    assert f.dist_km(s["VAKF1"]) < 15
