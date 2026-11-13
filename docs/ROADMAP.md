# LUPITA engineering roadmap

**Last updated:** 2026-11-13 | **Code:** `main` | **Generated-data export:** `data` only

This is the handoff record for future sessions. Read it with [Project Status](PROJECT_STATUS.md) and [Progress Log](PROGRESS_LOG.md). Do not restart completed work or repeat expensive research workflows without a specific reason.

## Project contract
- Run app, tests, pipeline and source configuration from `main`; publish generated JSON/API/PNG assets to `data`.
- Keep unapproved GIS interpretations and candidate geometry out of production inputs.
- Preserve source timestamps, provenance, missing coverage and quality limitations.
- Do not change species biology, prediction weights or scoring gates without evidence and regression tests.
- Make production changes directly on `main` in coherent batches. Update README, Project Status, Progress Log and this roadmap.
- Run focused tests first, full tests for integration milestones, and no unrelated NOAA/FWC extraction workflows.

## Verified baseline
- Freshness diagnostics: `536984e0af96ddf0cc0c7a8edd344a2b4050568c`; chlorophyll fallback correction: `9c7ed75a739652e54f1989b0a224d1a0d3419cb8`.
- Last pre-upgrade production refresh: [workflow #202](https://github.com/markeetox/LUPITA/actions/runs/43469532292), success with predictions refreshed, but currents about 1,121 hours old and health degraded.
- Last pre-upgrade Python tests: [run #404](https://github.com/markeetox/LUPITA/actions/runs/43467354619).
- First HF Radar integration suite after fixture corrections: [run #407](https://github.com/markeetox/LUPITA/actions/runs/43475604949), **254 passed, 0 failed, 115 warnings**. A small follow-up assertion/refinement was committed after that run and still needs a fresh suite.
- HF Radar source/loader commit: `a4e7bcf633a84238723dd250df9f5a1e3f87e159`.

## Environmental sources
| Layer | Primary | Fallback / support | Freshness |
|---|---|---|---|
| SST | NOAA CoastWatch `jplMURSST41` | ERDDAP host fallback | warning 36h, stale 72h |
| Chlorophyll | NOAA-20 VIIRS `nesdisVHNnoaa20chlaDaily` | gap-filled product disabled | warning 72h, stale 120h |
| Coastal currents | NOAA/NESDIS HF Radar `ucsdHfrE2`, hourly 2 km | `nesdisSSH1day` altimetry fills uncovered cells | warning 12h, stale 24h (provisional) |
| Gulf Stream edge | NOAA CoastWatch `nesdisSSH1day`, daily 25 km | no alternate model | warning 36h, stale 72h |
| Bathymetry | NOAA NCEI ETOPO 2022 15s, stride 15 | none | static |

HF Radar request window: 24.0-28.5°N, 83.5-78.0°W. It represents near-surface coastal flow, not full-depth or complete offshore circulation. `hdop`, contributing-site and radial-count metrics are reported but not hard quality gates. Altimetry supplies broad-area context and the approximate Gulf Stream edge. HF Radar is used where valid; altimetry fills remaining cells. Each source's timestamp and coverage are kept distinct.

## Active milestone: production validation of HF Radar
**Status:** configured and committed; live production retrieval not yet verified.

Acceptance criteria:
1. Scheduled production run succeeds from `main` and exports to `data`.
2. `latest.json` shows `ucsdHfrE2` loaded with a parseable timestamp and nonzero raw valid fraction.
3. Inspect South Florida aligned HF Radar coverage; confirm useful map-area coverage and altimetry fill elsewhere.
4. Altimetry has its own timestamp/freshness and remains the source of the `stream.json` Gulf Stream edge.
5. Health degrades on stale/missing selected timestamps or stale supporting altimetry, while predictions continue if a usable feed remains.
6. If HFR is unavailable or coverage negligible, diagnose endpoint, request bounds, latency and coverage before changing sources.
7. Do not change scoring weights or biology during source validation.

## Next sequence
1. Inspect the next Pull Ocean Data run and `latest.json`, `fish.json`, `api/v1/index.json`, and `stream.json`.
2. Record HFR/altimetry timestamps, valid fractions, quality metrics, blend mode and workflow link in this roadmap and progress log.
3. Compare several hourly runs before calibrating freshness thresholds.
4. Add source-quality/coverage context to species explanations without implying catch probability.
5. Audit species evidence before any scoring changes.
6. Continue Biscayne shoreline/inlet work from persisted evidence; do not infer connectivity or mix MHW/MHHW/MLLW geometry.

## Verification
```bash
python -m pytest -q
python -m pipeline.check_sources
python -m pipeline.run
```
A metadata check is not a substitute for inspecting the actual production CSV pull and coverage.
