# LUPITA project status

**Last reviewed:** 2026-11-13  
**Production branch:** `main`  
**Canonical application branch:** `main`  
**Generated export branch:** `data`  
**Consolidation staging branch:** `integration/main-consolidation` (merged; no longer active)

## Executive status

LUPITA is being consolidated around one authoritative application branch: `main`. The temporary `integration/main-consolidation` branch was used for staging and is now redundant after PR #72 merged. The `data` branch is reserved for generated application exports and is excluded from code consolidation. GIS research remains separate from production scoring until reviewed and promoted.

PRs #66, #68, and #69 have been squash-merged into `integration/main-consolidation`. The 85 unique/updated paths from PR #70 have also been imported into staging as a consolidated tree commit, removing its stacked dependency. Original PRs #70 and #71 are closed as superseded. Consolidated PR #72 targets `main`; its Python suite, species validator, and focused Biscayne workflow all pass. Only the Vercel preview status is failing due to an external 24-hour deployment rate limit.

## Current workstreams

### 1. Biscayne Bay geographic foundation

**Status:** research evidence assembled; final ecological boundary and subregion geometry not approved.

Persisted research includes:

- NOAA ENC named-water features, original source attributes, and topology audits.
- NOAA NGS Coastal Mapping Program project vectors for FL1808A and FL1808C, with MHW shoreline and MLLW depth-contour subsets kept distinct.
- NOAA composite MHW and predicted MHHW screening layers, kept separate.
- FDEP Aquatic Preserve geometries and spatial overlays.
- FWC/NPS benthic habitat patches and supporting GIS inventories.
- Miami-Dade bridge inventory and NOAA ENC bridge/landmark context.
- Candidate landmark references for Dumfoundling Bay, Rickenbacker Causeway, Featherbed Bank, Black Point, Card Sound, and Jewfish Creek.

Key persisted locations:

- `data/spatial/noaa-biscayne-named-water-areas.geojson`
- `data/spatial/noaa-biscayne-named-water-topology-audit.json`
- `data/spatial/noaa-biscayne-hydrography-index.json`
- `data/spatial/feature-catalog.json`
- `data/spatial/research/noaa_cmp/`
- `data/spatial/research/noaa_enc/`
- `data/spatial/research/transportation/`
- `data/spatial/research/biscayne-landmark-candidates.json`
- `data/spatial/research/biscayne-source-manifest.json`

### 2. Landmark and inlet reconciliation

**Status:** active review; source extraction is not equivalent to verified channel geometry.

- Bear Cut and Norris Cut have directly named NOAA ENC water polygons in the curated set. These are charted named-water areas, not surveyed channel centerlines.
- Card Sound has six exact NOAA ENC OBJECTIDs identified for detailed source-feature review.
- Jewfish Creek has two named-water polygons identified for geometry and depth-context analysis. NOAA CO-OPS station 8723613 remains a tidal benchmark reference, not a creek centerline or mouth.
- Rickenbacker Causeway has a named land polygon plus separate bridge and coastline context. Bridge proximity does not establish a crossing or water connection.
- Government Cut remains unresolved. Broader Miami Harbor Channel fairway and maintained-channel features are not an acceptable substitute for an exact Government Cut crosswalk.

No inferred inlet connections, snapped seams, or synthetic channel centerlines are approved.

### 3. Production fishing prediction system

**Status:** existing production pipeline remains the live app data path.

- The scheduled workflow is `.github/workflows/pipeline.yml`, hourly at 10 minutes past the hour UTC.
- The workflow runs from `main`, executes tests, catalog generation, and the prediction pipeline, then exports app-facing JSON to the `data` branch.
- The optional checkout of the previous `data` publication is only a last-known-good export fallback; it is not required for prediction generation. The intended contract is that `main` can run without `data` and export to it when available.
- The README's prediction, species, bite-timing, boat-condition, closures, and API sections describe the production pipeline. Changes to those processes must be reflected here and in the README.
- Dynamic-source freshness diagnostics are live. NOAA HF Radar 2 km is now the primary coastal-current source over South Florida; satellite altimetry is retained as a spatial fallback and as the Gulf Stream-edge source. Production validation is pending on the next scheduled refresh.
- Spatial research must not be described as affecting fish predictions until it is deliberately integrated, tested, and promoted.

## Open review dependencies

| Pull request | Purpose | Base | State |
|---|---|---|---|
| [#70](https://github.com/markeetox/LUPITA/pull/70) | NOAA hydrography and Biscayne inlet review | imported into integration staging | Closed, superseded |
| [#69](https://github.com/markeetox/LUPITA/pull/69) | Biscayne GIS geometry foundation | integration staging | Merged |
| [#68](https://github.com/markeetox/LUPITA/pull/68) | South Florida spatial-context schema and species habitat contexts | integration staging | Merged |
| [#66](https://github.com/markeetox/LUPITA/pull/66) | South Florida in-situ temperature audit | integration staging | Merged |
| [#71](https://github.com/markeetox/LUPITA/pull/71) | Prediction reliability changes | already present in current codebase | Closed, superseded |
| [#72](https://github.com/markeetox/LUPITA/pull/72) | Single-main runtime and data-export consolidation | `main` | Merged |

PR #70 originated as a stacked branch on #69. Its resulting file tree is now in the staging branch without the old commit chain. PR #71 was reviewed against the current tree and its meaningful API/confidence changes were already present, so it was closed without importing stale versions of core files.

## Current environmental-source quality

- The 2026-11-13 production refresh completed and generated predictions, but the published current observation was about 1,121 hours old. Pipeline health correctly reported degraded rather than healthy.
- NOAA/NESDIS HF Radar dataset `ucsdHfrE2` is configured as the primary near-surface coastal-current feed over 24.0-28.5°N, 83.5-78.0°W. Its hourly 2 km vectors are overlaid where valid; satellite altimetry fills cells outside HF Radar coverage.
- Satellite altimetry remains necessary for broad-area context and the approximate Gulf Stream edge. The two feeds have separate timestamps and freshness diagnostics. HF Radar quality fields are reported but not yet used to reject vectors.
- The HF Radar endpoint has been verified against NOAA ERDDAP metadata, including its variables and dimensions. Python suite passed **255 tests** on [run #409](https://github.com/markeetox/LUPITA/actions/runs/43476053350).
- First live production refresh [#203](https://github.com/markeetox/LUPITA/actions/runs/43476661499) succeeded with predictions refreshed and no pipeline errors. HF Radar timestamp was 2026-11-13 10:00 UTC (7.85 hours old), but raw valid fraction across its South Florida request window was only 2.006%; its aligned valid fraction over the entire North America prediction grid was 0.0123%. The latter denominator is misleading for regional coverage, so a follow-up code change adds explicit query-region coverage counts and fractions. The old satellite fallback was 1,121.85 hours old and chlorophyll was delayed at 77.85 hours. Health correctly remained degraded.
- Live HF Radar retrieval is proven, but useful regional coverage is not yet proven. Do not call the current-source upgrade complete until query-region coverage and a fresher broad-area fallback are evaluated.
- The SoFlo Fish Finder Render page could not be inspected from the available public response, so no assumptions about its implementation or data sources have been imported.

## Known limitations and blockers

1. A defensible continuous ecological Biscayne Bay boundary has not been established.
2. NOAA ENC, FDEP preserve, benthic habitat, MHW, MHHW, and MLLW products represent different concepts and datums; they must not be blended as interchangeable geometry.
3. The 17.691 km nearest separation between FL1808A and FL1808C MHW linework is a measured separation between project vectors, not proof of a missing coastline or permission to interpolate.
4. Government Cut requires an exact source-feature crosswalk.
5. Candidate subregions, flats, channels, and inlet connections must retain confidence/provenance and must not be promoted based on proximity alone.
6. The Jewfish Creek shared-boundary test exposed projection-induced false zero measurements. The implementation now evaluates shared-edge topology in source coordinates and projects the resulting line only for metric length. The focused GitHub workflow now passes all 4 topology tests; the synthetic shared edge measures 100.763 m.
7. Five expensive FWC/NOAA source-acquisition workflows and the in-situ temperature extraction workflow are manual-only so PR synchronization cannot repeatedly trigger downloads and branch-write loops.
8. The first consolidated species-validator run failed during test collection because the full suite now includes GIS tests but the workflow installed only production requirements. Added `requirements-research.txt` and wired it into all full-suite CI workflows; rerun is pending.

## Next implementation milestones

1. Validate the NOAA HF Radar 2 km request in a production refresh; inspect South Florida valid-cell coverage, source timestamps, quality metrics, and the altimetry fallback before accepting the upgrade.
2. Build a source-latency history from repeated production refreshes and calibrate provisional freshness thresholds against actual observation delays.
3. Extend input-quality diagnostics into species-level prediction explanations, preserving the distinction between weighted habitat suitability scores and catch probability.
4. Audit species profile evidence and scorer compatibility before changing any biological preferences or weights.
5. Continue Biscayne boundary and inlet reconciliation within `main` using manual research workflows, without promoting unverified geometry.

## Validation policy

See [Biscayne research pipeline policy](biscayne-research-pipeline-policy-2026-11.md). In short: syntax and focused tests first; source-specific geometry QA only when inputs or logic change; full-suite validation at broad integration and pre-merge checkpoints. Do not rerun every NOAA extraction for an unrelated code or documentation change.


## 2026-11-13 | Source freshness diagnostics milestone

**Branch:** `main`  
**Purpose:** distinguish successful source loading from timely, timestamped observations.

- Added per-source observation age and freshness status for SST, chlorophyll and satellite-altimetry currents in `latest.json`.
- Added explicit unknown status for missing or unparseable timestamps and surfaced the currents observation time, which was previously omitted from the quality report.
- Added provisional, source-specific warning/stale thresholds to `config/sources.json`. These are operational monitoring limits only and must be calibrated against observed source latency before any scoring gate is introduced.
- Pipeline health now degrades when dynamic inputs are delayed, stale, future-dated or missing timestamps, while preserving the distinction between degraded data quality and a failed prediction refresh.
- Added the same freshness diagnostics to `fish.json` layer metadata and the app-facing API index.
- Added regression coverage for source-age calculation, missing timestamps and degraded health.

**Validation:** the first full-suite run reported 250 passed and one failed. The failure exposed a missing fallback from the chlorophyll aggregate timestamp to its primary scene timestamp; the correction is recorded in the progress log. Full-suite rerun and production refresh remain pending. The production prediction formula and species weights are unchanged.

**Next:** compare several hourly refreshes to determine actual latency distributions before adjusting thresholds or using freshness to gate scoring.
