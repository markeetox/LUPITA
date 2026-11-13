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
- First HF Radar integration suite after fixture corrections: [run #407](https://github.com/markeetox/LUPITA/actions/runs/43475604949), **254 passed, 0 failed, 115 warnings**.
- Run #408 added per-feed freshness assertions; 254 passed and 1 health-test assertion failed because the minimal fixture omitted a separate primary freshness object. The fallback comparison was corrected.
- Final suite: [run #409](https://github.com/markeetox/LUPITA/actions/runs/43476053350), **255 passed, 0 failed, 115 warnings**.
- HF Radar source/loader commit: `a4e7bcf633a84238723dd250df9f5a1e3f87e159`.

## Environmental sources
| Layer | Primary | Fallback / support | Freshness |
|---|---|---|---|
| SST | NOAA CoastWatch `jplMURSST41` | ERDDAP host fallback | warning 36h, stale 72h |
| Chlorophyll | NOAA-20 VIIRS `nesdisVHNnoaa20chlaDaily` | gap-filled product disabled | warning 72h, stale 120h |
| Coastal currents | NOAA/NESDIS HF Radar `ucsdHfrE2`, hourly 2 km | `nesdisSSH1day` only when timestamp-qualified (max age 72h); NOAA RTOFS model ingestion is next | warning 12h, stale 24h (provisional) |
| Gulf Stream edge | NOAA CoastWatch `nesdisSSH1day`, daily 25 km | no alternate model | warning 36h, stale 72h |
| Bathymetry | NOAA NCEI ETOPO 2022 15s, stride 15 | none | static |

HF Radar request window: 24.0-28.5°N, 83.5-78.0°W. It represents near-surface coastal flow, not full-depth or complete offshore circulation. `hdop`, contributing-site and radial-count metrics are reported but not hard quality gates. Satellite altimetry supplies approximate Gulf Stream-edge context. It may fill current-vector gaps only when its timestamp is known, non-future, and no older than 72 hours; otherwise it is excluded from current vectors. HF Radar remains the observation overlay. NOAA S-111 RTOFS East is the preferred broad-area model candidate: public HDF5 tiles, 6-hourly forecast values over a 72-hour horizon, approximately 8.5 km resolution, and currents at 4.5 m depth or half the water column where shallower. The S-111 service is described as preliminary; South Florida tile coverage, catalog freshness, file size, and HDF5 decoding must be validated before use. Raw RTOFS HTTPS/GRIB remains a fallback implementation route. Each source's timestamp, forecast lead, eligibility and coverage must remain distinct.

## Active milestone: validate regional currents and replace stale broad-area fallback
**Status:** HFR live retrieval confirmed, but its spatial contribution is sparse. Production #203 loaded HFR at 7.85 hours old; only 2.006% of requested HFR source cells contained valid vectors. The 0.0123% aligned fraction is calculated against the entire North America grid and is not a useful local percentage. Satellite altimetry supplied most of the 53.4818% combined current coverage but was 1,121.85 hours old. A new fail-closed age guard excludes altimetry older than 72 hours from current vectors while retaining its Gulf Stream-edge role. NOAA RTOFS is the preferred broad-area model candidate; direct NOMADS OPeNDAP was retired in February 2026, so production ingestion must use supported HTTPS model files or GRIB filtering.

Acceptance criteria:
1. Report HFR, fallback and combined valid fractions inside the South Florida HFR request window, alongside whole-grid fractions.
2. Compare HFR 1 km, 2 km and 6 km products on the same South Florida window, including timestamps, valid-cell coverage and quality metrics.
3. Identify a machine-readable broad-area current source with current observation/model initialization time, forecast lead, spatial coverage and units.
4. Evaluate NOAA Global RTOFS NetCDF fields and USF EFCOM coastal FVCOM output. EFCOM is geographically relevant but its public interface currently exposes visual products and labels results research-grade; machine-readable access is not yet verified.
5. Keep satellite altimetry as Gulf Stream-edge context and permit current-vector fallback only when timestamp-qualified (<=72h); never silently present stale data as current.
6. Implement NOAA RTOFS using its supported HTTPS model-file or GRIB-filter route; record model initialization time and forecast lead separately from observation age.
7. Keep HF Radar as a high-value observation overlay where valid, not a full-coverage regional model.
8. Keep Gulf Stream-edge provenance separate from the selected nearshore current source.
9. Do not change scoring weights or biology during source evaluation.

## Next sequence
1. Inspect the next production refresh for query-region coverage metrics.
2. Test candidate data access and subset sizes for NOAA RTOFS and EFCOM before adding production dependencies.
3. Compare model fields against HF Radar and local NOAA buoy/current observations where available.
4. Choose a broad-area fallback only after live timestamp and coverage validation.
5. Calibrate freshness thresholds after multiple production observations.
6. Add source-quality/coverage context to species explanations without implying catch probability.
7. Audit species evidence before any scoring changes.
8. Continue Biscayne shoreline/inlet work from persisted evidence; do not infer connectivity or mix MHW/MHHW/MLLW geometry.

## Verification
```bash
python -m pytest -q
python -m pipeline.check_sources
python -m pipeline.run
```
A metadata check is not a substitute for inspecting the actual production CSV pull and coverage.


## Active milestone: upstream outage resilience and truthful publication
1. Use NOAA CoastWatch `jplMURSST41` first and the documented `upwell` ERDDAP mirror second.
2. Report dependent layers as `not_attempted` when SST prevents their requests from starting.
3. Separate current refresh health from last-known-good prediction data with `latest.json` and `api/v1/refresh.json`.
4. Restore prior `data` branch prediction files/API when a refresh fails.
5. Validate with focused/full tests and a manual production pull. Do not change scoring weights or species biology.
