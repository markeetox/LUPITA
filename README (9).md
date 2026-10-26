# Fish habitat map

Scores where fish are likely to be from live ocean conditions plus per-species habitat profiles.
Experimental: scores show where conditions match published habitat preferences; they have not
been checked against catch reports. Seabound will later fetch the output as a map filter.

## Layout
- `data/parameters.json`: registry of every factor (key, unit, source, tier, status)
- `data/species/*.json`: one profile per fish (factors, weights, sources, display color)
- `config/`: buoy stations and ERDDAP dataset settings
- `pipeline/`: data pulls (`sources/`), `layers.py` (common grid), `scoring.py`, `predict.py`, `run.py`
- `web/index.html`: map viewer (deployed on Vercel, root directory `web`)
- `.github/workflows/pipeline.yml`: every 3 hours, runs tests + pipeline, publishes JSON to the `data` branch

## Run locally
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
python -m pipeline.check_sources     # confirms stations, dataset IDs, dimensions, units
python -m pipeline.run               # writes data/live/latest.json and data/live/fish.json
```
Helpers: `python -m pipeline.find_stations`, `python -m pipeline.find_datasets "search words"`.

## How a score is made
Each map cell gets 0-1 per factor from the species profile (ideal band, allowed range), weighted
and re-normalized over the factors that have data. A `gate` factor (mahi: depth) removes cells
outright. Temperature-break strength is judged relative to today's offshore conditions (95th percentile).
Only the best 15% of cells scoring at least 0.55 become areas. Species whose key data is missing
(reef map for yellowtail, tides and shoreline for snook) are reported as "waiting for" instead of guessed.

## Species
Map-based (scored on the grid): mahi-mahi, sailfish, wahoo, yellowtail snapper, mutton snapper, cobia.
Site-based (scored at named inlets): snook, tarpon. Each species file lists every factor with its source and a
`value_status` (sourced, partly_sourced, provisional, needs_source). Seasonal fish (sailfish, wahoo, cobia, mutton snapper,
tarpon) use a calendar-month factor. Wahoo uses seafloor slope from the ETOPO depth grid. The workflow runs hourly.

## Bite timing (when, not where)
Habitat match says where a fish lives. Bite timing says whether it is likely feeding at each moment over the next
24 hours, and picks a best window of up to 3 hours. Each species file can carry a `timing` block with light
(dawn/day/dusk/night), tide stage, moon (a window around the full moon, in certain months) and cold-front parts.
A fish with no `timing` block shows "No reliable time-of-day information" instead of a guess. Every block is tagged
`angler_lore`: patterns reported by local captains and fishing writers, not tested by studies, with sources listed.
- Light: computed sunrise and sunset (`pipeline/astro.py`). Moon: true new/full moon times (`pipeline/moon.py`, within minutes).
- Tide: NOAA CO-OPS predictions. Cold front: seen in the last 48 hours in buoy wind, air temperature and pressure,
  or forecast in the next 36 hours from the National Weather Service hourly forecast (`pipeline/weather.py`).
  A front is a wind shift from the south/west side to a firm northerly, plus an air-temperature fall or pressure rise.
- Barometric pressure is used only as a sign of a front, not as a direct fish factor: studies have not shown a direct effect.

## App API (for Seabound)
The pipeline also writes a small versioned API under `api/v1/` (published on the `data` branch): `index.json`, one JSON file per
fish, ready-to-draw heat overlay PNGs, the fish pictures, no-fishing areas and the Gulf Stream edge. See `docs/seabound-api.md`
for the contract, hosting advice and what is deliberately left out (legal sizes and bag limits), and `docs/seabound_client.dart`
for an untested Flutter starting point (`pipeline/api.py` builds the files; `tests/test_api.py` checks the contract).

## Currents and the Gulf Stream edge
Surface currents come from NOAA CoastWatch geostrophic currents (satellite altimetry, daily, 25 km grid, listed as
experimental; variables `ugos` east and `vgos` north in m/s). The stream's inshore edge is the westernmost point in each
latitude row where northward flow reaches half the row's maximum (and at least about 0.8 kn); eddies are not modeled
(`pipeline/currents.py`). It is approximate: good to roughly 20 km, weaker near shore, and geostrophic flow leaves out
wind-driven and tidal currents. Sailfish, wahoo and mahi score a band around the edge (provisional); the map draws the
edge as a thin line you can toggle and tap (`stream.json`). If the dataset's dimensions or names differ from the config,
run `python -m pipeline.check_sources` and fix `config/sources.json`.

## Boat conditions
A separate sea-state indicator, not part of any fish score. From the nearest fresh buoy readings (within 80 km, under
3 hours old) it rates wind and waves as Good, Fair, Rough or Dangerous (wind limits 12, 18 and 25 kn; wave limits
about 2, 4 and 6.5 ft; short steep waves count one step rougher; the worse of wind and waves wins). The forecast adds the
strongest wind expected in the next 24 hours. The limits are a rough guide for a typical 20-30 ft boat, not official
advisory levels (`pipeline/seastate.py`). Spots in Rough or Dangerous water get a warning banner. Always check the
National Weather Service marine forecast.

## Icons
Rows, headings and reasons in the popups carry small line icons (wind, tide, depth, size, diet and so on), defined inline
in `web/index.html` (`ICONS`, `ROW_ICON`, `REASON_ICONS`). Reasons get their icon from keywords in the text; a row with an
unknown label (such as a reef's name) gets the anchor.

## Fish pictures
Each popup shows a transparent picture above the fish name, read from `web/fish/<species id>.png`. These are
placeholder illustrations (drawn by `tools/make_fish_art.py`, sources in `tools/fish-svg/`). To use a real photo,
replace the PNG with one of the same name (transparent background, cropped tight to the fish, facing left looks
best), then in `data/species/<id>.json` set `image.kind` to `"photo"` and fill in `image.credit` and `image.license`
so the popup credits it. Only use images you have the right to show (public domain, or a license you can credit).
NOAA Fisheries species pages and Wikimedia Commons are good places to look; FWC species illustrations are copyrighted.
A bad or missing picture never stops the data run; the popup just shows a short note instead.

## Snook (site model)
Snook live along inlets, passes and shorelines, which a 2 km grid cannot show. Snook is therefore scored by
site: the inlets in `config/places.json`. Each site is scored from the nearest buoy's water temperature (a hard
stop below the cold limit), NOAA CO-OPS tide predictions (`config/tides.json`), computed sunrise/sunset, and
spawning season. Tide and light weights are angler guidance, so confidence is capped at Low. Not yet included:
mangrove shorelines, bridges, docks, salinity, cold-front detection.

## No-fishing areas
Boundaries come from NOAA's National MPA Center MPA Inventory (2023 edition), filtered to sites whose Fishing
Restrictions text says recreational fishing is prohibited. Fish areas that are at least half inside one are never
recommended; areas that overlap one are flagged; every popup says whether the check ran. Not covered: fishery
management areas, seasonal closures, port and security zones, and anything newer than the 2023 edition.
Always confirm with FWC, NOAA Sanctuaries or the National Park Service.

## Output
- `fish.json`: species status, areas (point, polygon, score, reasons, location facts); read by `web/`
- `heat.json`: each map-based fish's full score grid (one byte per cell), painted by the map as a smooth heat layer
- `closures.json`: no-fishing area outlines and details, drawn in red on the map
- `latest.json`: buoy readings and satellite scene summaries
