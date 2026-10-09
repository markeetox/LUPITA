# Fish habitat map

Standalone service that scores where fish are likely to be, from live ocean conditions plus
per-species habitat profiles. Seabound will later fetch the output as a map filter.

## Layout
- `data/parameters.json`: registry of every factor (key, unit, source, tier, status)
- `data/species/*.json`: one profile per fish; factors reference registry keys only
- `config/`: buoy stations and ERDDAP dataset settings
- `pipeline/`: Python data pulls and derived values (`run_v1.py` is the entry point)
- `web/`: map viewer (Vercel), next step
- `.github/workflows/pipeline.yml`: scheduled pull, publishes JSON to a `data` branch

## First run (needs internet)
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q                  # offline unit tests
python -m pipeline.check_sources     # confirms stations, dataset IDs, dimensions and units
python -m pipeline.run_v1            # writes data/live/latest.json
```
Run `check_sources` before anything else. Dataset IDs and station IDs in `config/` were written
from memory of NOAA's catalogs and have not been verified against the live servers.

## Output so far (`data/live/latest.json`)
- `buoys[]`: water temp, wind (kn), waves, pressure, 3 h pressure change, 24 h water-temp change
- `sst`: grid summary and the strongest temperature-break cells (`sst_gradient`)
- `errors[]`: any source that failed this run

## Next
1. Verify sources and tune `SST_BREAK_MIN` against real grids
2. Enable chlorophyll once its dataset is verified
3. Add bathymetry and structure layers
4. Scoring engine: read species profiles, score a grid, write per-species GeoJSON with reasons
5. `web/` viewer with popups
