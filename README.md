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

## Output
- `fish.json`: species status, areas (point, polygon, score, reasons, location facts); read by `web/`
- `latest.json`: buoy readings and satellite scene summaries
