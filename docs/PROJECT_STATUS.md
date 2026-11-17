# LUPITA project status

**Last reviewed:** 2026-11-17  
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
- Dynamic-source freshness diagnostics are live. NOAA HF Radar 2 km is the primary coastal-current observation source over South Florida. Satellite altimetry remains available for Gulf Stream-edge context, but is excluded from current-vector filling when its timestamp is missing, future-dated, or older than 72 hours. The preferred broad-area candidate is NOAA's S-111 HDF5 surface-current product derived from RTOFS East, which provides tiled Atlantic forecast guidance at vessel-relevant depth. Its current South Florida tile/catalog access and HDF5 contents still require live verification before production enablement; raw RTOFS HTTPS/GRIB remains the alternative path.
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
- NOAA/NESDIS HF Radar dataset `ucsdHfrE2` is the primary near-surface coastal-current feed over 24.0-28.5°N, 83.5-78.0°W. Its hourly 2 km vectors are used only where valid.
- Satellite altimetry `nesdisSSH1day` remains available for approximate Gulf Stream-edge context. Its current-vector fallback is age-gated at 72 hours and is not used when its timestamp is missing, future-dated, or stale. Source timestamps, eligibility, use, and coverage remain separately reported. HF Radar quality fields are diagnostic only and are not yet hard rejection gates.
- The HF Radar endpoint has been verified against NOAA ERDDAP metadata, including its variables and dimensions. Python suite passed **255 tests** on [run #409](https://github.com/markeetox/LUPITA/actions/runs/43476053350), then **257 tests** including the stale-fallback regression coverage on [run #415](https://github.com/markeetox/LUPITA/actions/runs/43484934310).
- First live production refresh [#203](https://github.com/markeetox/LUPITA/actions/runs/43476661499) succeeded with predictions refreshed and no pipeline errors. HF Radar timestamp was 2026-11-13 10:00 UTC (7.85 hours old), but raw valid fraction across its South Florida request window was only 2.006%; its aligned valid fraction over the entire North America prediction grid was 0.0123%. The latter denominator is misleading for regional coverage, so a follow-up code change adds explicit query-region coverage counts and fractions. The old satellite fallback was 1,121.85 hours old and chlorophyll was delayed at 77.85 hours. Health correctly remained degraded.
- Live HF Radar retrieval is proven, but useful regional coverage is not yet proven. The stale altimetry current-vector fallback is now fail-closed: it cannot fill current cells beyond 72 hours. The production refresh after this guard must confirm that stale vectors are excluded while the Gulf Stream-edge provenance remains visible. NOAA S-111 RTOFS East is the preferred broad-area model candidate because its HDF5 tiles provide 6-hourly surface-current forecast guidance at approximately 8.5 km resolution and a vessel-relevant depth. Tile coverage, latest catalog contents, and HDF5 decoding must be verified before production enablement.
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

1. Validate the HF Radar freshness guard in production; confirm stale altimetry no longer fills current vectors and inspect regional coverage and Gulf Stream-edge provenance.
2. Implement a supported NOAA RTOFS HTTPS/GRIB subset downloader, including model initialization time and forecast lead, then compare it with HF Radar and local observations before enabling it as broad-area current guidance.
3. Build a source-latency history from repeated production refreshes and calibrate provisional freshness thresholds against actual observation delays.
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


## 2026-11-13 | SST host failover and refresh/prediction separation

- Pull Ocean Data [#204](https://github.com/markeetox/LUPITA/actions/runs/43486365838) failed at the final health gate after the required MUR SST request returned HTTP 503 from CoastWatch ERDDAP after four attempts. The full suite passed (257 tests).
- Diagnostic correction: `load_layers` returns immediately when SST cannot load. HF Radar, satellite altimetry, chlorophyll, bathymetry and spatial layers were not requested. Their states should be `not_attempted`, not source failures or unknown freshness.
- NOAA's `upwell.pfeg.noaa.gov/erddap` documents access to the same `jplMURSST41` dataset and is being added as a host fallback, not a different SST product.
- Failed refresh publication will preserve the last-known-good prediction files/API snapshot and expose current health through `latest.json` plus `api/v1/refresh.json`.
- Validate mirror retry, diagnostic states and publication restoration with focused/full tests, then one manual production pull.


### Validation update
- The first test run found one compatibility regression in the new `not_attempted` state: a test fixture uses `layers=None` without an SST error to mean no layer report. The implementation was narrowed so downstream layers are marked not attempted only when an actual `layers sst:` error is present.
- Corrected full Python suite: **262 passed, 0 failed, 115 warnings** on [run #43493987730](https://github.com/markeetox/LUPITA/actions/runs/43493987730), commit `735f888b02ab3ddb8065277c4758e00097778ce6`.
- Code and regression coverage are validated. A manual Pull Ocean Data run is still required to verify that the live `upwell` mirror returns a current MUR scene and that the publication step preserves the previous API snapshot correctly.


### Final source-provenance validation
- The selected ERDDAP host is now recorded in SST diagnostics as `source_endpoint`, so the next production run will show whether CoastWatch or the upwell mirror supplied the grid.
- Latest full Python suite: **262 passed, 0 failed, 115 warnings** on [run #43494256052](https://github.com/markeetox/LUPITA/actions/runs/43494256052), commit `5da0dc56470975216e032b98b0f230a586d8102c`.
- Remaining validation is live only: dispatch Pull Ocean Data and inspect the source endpoint, SST timestamp, HF Radar request result, and published refresh/snapshot metadata.


## Species profile accuracy work | 2026-11-14

**Status:** first South Florida accuracy batch committed to `main`; NOAA source troubleshooting remains paused by user direction.

Four records were improved: black grouper, great barracuda, gray/mangrove snapper and yellowtail snapper. Profiles now use species-specific FWC/NOAA/regional evidence, and Florida recreational regulation summaries distinguish Atlantic state waters, federal waters, county-specific rules and Biscayne National Park caveats. The barracuda SST evidence label is now provisional; no numeric factor, weight, active flag, prediction logic or ocean-data source was changed.

See `docs/PROGRESS_LOG.md` for source links, commit SHAs and validation limits. The JSON records were parsed before and after commit. The dedicated species audit and test suite remain pending; no Actions workflow or NOAA request was run.


## Species profile accuracy work | batch 2 | 2026-11-14

**Status:** six additional South Florida species records reviewed and committed to `main`: common snook, Atlantic tarpon, Permit, bonefish, hogfish and mutton snapper. Biology and harvest summaries now use current FWC and relevant Florida Museum/research sources. Region-specific rules and protected-area caveats are explicit. Unsupported hogfish and mutton snapper numeric SST/depth settings are marked provisional; no numeric scoring configuration, weights, active flags or prediction logic were changed.

Together with batch 1, **10 species records have been reviewed**: black grouper, great barracuda, mangrove snapper, yellowtail snapper, common snook, Atlantic tarpon, Permit, bonefish, hogfish and mutton snapper. See `docs/PROGRESS_LOG.md` for per-species scope, source links, commit SHAs and validation limits. All ten records have been fetched and parsed as JSON after commit. The dedicated species audit and Python suite remain pending; no NOAA workflow or endpoint was used.


## 4. Species catalog and scoring integrity

**Status:** full static catalog audit completed on 2026-11-14; follow-up validator and confidence work remains.

- All 130 species JSON profiles were fetched and parsed: 105 grid models and 25 named-site models.
- No missing core identity/model fields, duplicate factor parameters within a profile, unregistered factor parameters, unsupported active parameter/kind combinations, or active-weight overflow were found in the static cross-check.
- Twelve profiles contain 33 active factors marked provisional, estimated, or unsourced. Eight active factors lack source references across six profiles.
- Twenty-three of the 25 site models are currently temperature-only (one active SST factor). Snook and tarpon are the only five-factor site models. Scores are normalized over available active weights, so a single-factor score is entirely an SST score, not 35% of a larger model.
- Prediction confidence does not directly incorporate active factor evidence status. Evidence-aware confidence policy needs to be defined before changing output labels.
- Grid and site scoring differ in missing `required` / `gate` behavior. Both skip optional missing factors and enforce minimum coverage, but their contracts need explicit documentation and tests.
- The existing validator needs coverage-bound, category-map, and missing-data semantics checks.

Full audit: [Species Catalog Audit](SPECIES_CATALOG_AUDIT_2026-11-14.md). Historical decisions and the static inspection boundary are in [Progress Log](PROGRESS_LOG.md).

**Next:** strengthen the read-only validator and tests, define evidence-aware confidence policy, then prioritize South Florida temperature-only site pilots for evidence-backed expansion. No scoring weights or prediction behavior are changed by the audit.

**NOAA boundary:** environmental ingestion/source troubleshooting remains paused until explicit project-owner clearance. This catalog audit did not contact NOAA or run data workflows.


## Species validator follow-up | 2026-11-14

**Status:** implementation committed and validated on 2026-11-14.

- Validator now checks `min_coverage` bounds, category map values/keys, boolean factor flags, and grid/site `required` / `gate` semantics.
- Active evidence weight is reported separately from environmental coverage, including uncertain and partly sourced weight.
- Audit output explicitly labels SST-only site profiles as `temperature_only_pilot`.
- Eight new regression tests cover the added checks and evidence summaries.
- Main-branch Python CI now runs the species validator after tests when species profiles or the parameter registry change, and uploads the generated audit files.
- Proposed confidence policy is in [Species Model Confidence Policy](SPECIES_MODEL_CONFIDENCE_POLICY.md). It is not active. Prediction confidence and scoring remain unchanged pending review.

Current validation run: [#43621667713](https://github.com/markeetox/LUPITA/actions/runs/43621667713). NOAA ingestion remains paused.


### Final validation
- Full Python suite: **272 passed, 0 failed, 115 warnings**.
- Species validator: **130 profiles parsed, 130 structurally valid, 0 active model compatibility issues, 0 validator errors**.
- Model scope: 23 temperature-only site pilots, 27 other single-factor models, 80 multi-factor models.
- Evidence diagnostics: 12 profiles have elevated active evidence risk.
- CI run and report artifact: [#43622006765](https://github.com/markeetox/LUPITA/actions/runs/43622006765).

The 130 profiles classified as needing research or model rebuilding reflect a structural review proxy, not an empirical finding that every profile is scientifically invalid. The proposed confidence policy remains inactive pending review. Prediction scoring and confidence output are unchanged.


## Active factor evidence review | 2026-11-14

**Status:** source review and profile annotations committed; final CI validation passed on 2026-11-14.

- Eight previously source-missing active factors across six species now have factor-level source references and explicit limitations.
- All remain marked `provisional`. Sources that are contextual, model-derived, age-specific, or geographically limited were not treated as numeric validation.
- No factor values, weights, active flags, gates, required flags, or scoring behavior changed.
- Full review: [Active Factor Evidence Review](ACTIVE_FACTOR_EVIDENCE_REVIEW_2026-11-14.md).
- Latest validation run: [#43622375109](https://github.com/markeetox/LUPITA/actions/runs/43622375109).

NOAA remains paused.


### Final validation
- Full Python suite: **272 passed, 0 failed, 115 warnings**.
- Species validator: 130 parsed, 130 structurally valid, 0 active compatibility issues, 0 validator errors.
- All eight reviewed active factors now have factor-level source references. No missing-source findings remain for those eight; inactive/planned factors elsewhere may still lack references.
- All eight factors remain provisional and the catalog-wide active evidence risk remains elevated for 12 profiles.
- Final CI run: [#43622573953](https://github.com/markeetox/LUPITA/actions/runs/43622573953).


## 2026-11-14 | Category-map scorer compatibility fix

A mismatch was found between the species validator contract and the grid scorer: a valid category map without a `preferred` list passed validation but produced no grid score. The grid scorer now evaluates map-only category factors consistently with the site scorer. Regression tests cover map-only and preferred-list configurations.

Commits: `8cabaa7c9dab8034388980fd096d471cb6aff21a`, `e0c0512643b68ed703d22d914a9d4ab34fcc58a5`.

**Validation:** automatic Python test workflow triggered by the pushes; result pending. No NOAA activity, species profile edits, biological parameter changes, or confidence-policy activation.


## Named-site model triage | 2026-11-15

Static review of all 25 site-model profiles identified 23 temperature-only pilots. Three South Florida pilots (bonefish, great barracuda, Permit) retain provisional SST bands; 20 other one-factor profiles mark SST sourced but cite only the generic NOAA Fisheries homepage. Snook and tarpon are the only five-factor site models, with structure-kind mapping questions requiring review. The site engine's `distance_to_inlet` function is currently a constant-zero placeholder.

The validator now warns on homepage-only references, rejects active use of the placeholder distance factor as model-incompatible, and reports site structure categories that are unreachable or fall through to zero for allowed site kinds. Regression tests were added. See [Named-site model triage](SITE_MODEL_TRIAGE_2026-11-15.md).

**Validation:** automatic Python CI result pending. No prediction behavior, species numeric values, or NOAA ingestion was changed.


## Production data refresh recovery check | 2026-11-15

**Latest inspected run:** [Pull Ocean Data #211](https://github.com/markeetox/LUPITA/actions/runs/43664658831), scheduled on `main` at commit `16ae66cd6247ce8eb30b05770f16f605423cc16c`.

- Workflow, full Python test step, catalog generation, production pipeline, and publication to `data` all completed successfully.
- `latest.json` generated at `2026-11-15T01:47:27Z`; prediction snapshot refreshed from the current run; no recorded errors or critical issues.
- Overall health is **degraded**, not healthy, because SST was 40.8 hours old and crossed its provisional 36-hour warning threshold (but not its 72-hour stale threshold).
- Chlorophyll loaded at 61.8 hours old (fresh by configured thresholds), but valid source coverage was only 15.8%.
- HF Radar loaded at 5.8 hours old, but South Florida query-window coverage was only 94/10,101 cells (0.93%). Stale altimetry (1,153.8 hours old) was correctly excluded from current vectors.
- Bathymetry, reef structure, benthic habitat, closures, and buoy observations loaded successfully.

**Interpretation:** this confirms that the live production ingestion and publication path is operating again. It does not establish sustained NOAA recovery or adequate spatial coverage. Monitor later scheduled runs and compare freshness/coverage before changing thresholds, sources, or prediction behavior. No code or configuration changes were made during this validation.

Full diagnostics are recorded in [Progress Log](PROGRESS_LOG.md), including per-layer timestamps and coverage.


## 2026-11-15 | HF Radar coverage and latest CI check

- Python CI run [#462](https://github.com/markeetox/LUPITA/actions/runs/43669158015) passed **279 tests, 0 failures** on the latest code-changing commit `ee25d79c163323f5fa17b35471a147730e22a7ff`. The later documentation-only commits do not alter that tested code.
- Production refresh #211 reports HF Radar `ucsdHfrE2` fresh at 5.79 hours old, but only **94/10,101 cells (0.9306%)** in the configured South Florida window have valid aligned vectors.
- The raw HFR source grid valid-vector fraction was 0.9059%, close to the aligned regional fraction. Current evidence therefore points to sparse upstream spatial availability, not a major interpolation loss in LUPITA. This remains a diagnosis, not a final root-cause determination.
- NOAA also publishes a 6 km hourly East/Gulf Coast HFR product (`ucsdHfrE6`). It is a comparison candidate only; no source change has been made. Compare 1 km/2 km/6 km products over the same region and times before choosing one.
- Stale altimetry remains excluded from current-vector filling. Do not widen or alter the current source policy to make coverage percentages look better.
- No ingestion run, code change, source-config change, biological change, or scoring change was made during this inspection.

Detailed findings and NOAA references: [Progress Log](PROGRESS_LOG.md#2026-11-15--hf-radar-coverage-diagnosis-and-ci-verification).


## NOAA HF Radar comparison utility and first numerical result | 2026-11-15

**Status:** read-only diagnostic implemented and first same-time NOAA comparison completed. Workflow [run #43727859776](https://github.com/markeetox/LUPITA/actions/runs/43727859776) succeeded; artifact [hfr-product-comparison](https://github.com/markeetox/LUPITA/actions/runs/43727859776/artifacts/14166714348) was retrieved and reviewed.

- Added scripts/compare_hfr_products.py for 1 km (ucsdHfrE1), 2 km (ucsdHfrE2), and 6 km (ucsdHfrE6), plus focused tests and manual-only workflow .github/workflows/hfr-product-comparison.yml.
- All three datasets returned the exact common timestamp 2026-11-13T04:00:00Z over 24.0–28.5°N, 83.5–78.0°W. No nearest-time substitution occurred and no product retrieval failures were reported.
- Native-grid paired-vector counts: 1 km 0/285,069 (0.000%); 2 km 1,640/71,535 (2.293%); 6 km 753/7,980 (9.436%). These are native-grid valid-cell fractions, not directly comparable ocean-area estimates; the rectangular denominators include cells without radar coverage and products have different native grid spacings.
- Approximate subregion results: 2 km Keys 0%, Biscayne Bay 10.732%, offshore 5.701%; 6 km Keys 0.337%, Biscayne Bay 24.554%, offshore 10.811%. 1 km returned no paired vectors in any of the three boxes.
- Median quality diagnostics over valid vectors: 2 km HDOP 0.56, sites 2, radials 35; 6 km HDOP 0.30, sites 2, radials 100. These are descriptive medians, not proof that 6 km is more accurate. The 1 km product has no valid vectors to summarize.
- Product depths differ (approximately 0.5/1.0/2.4 m for 1/2/6 km). The results therefore compare distinct surface layers as well as distinct grid resolutions.
- The first report's half-degree denominator varied with each product's returned coordinate edges. This was corrected in commit 0ad8726 to use a fixed shared set of 99 half-degree bins across the requested region; a regression test was added in commit 57fe6d7. The first artifact predates this correction, so its tile-occupancy denominator should not be used for cross-product comparison. Rerun the manual diagnostic to obtain corrected shared-bin counts.
- Python CI [run #43725728118](https://github.com/markeetox/LUPITA/actions/runs/43725728118) passed the initial utility tests. The subsequent shared-bin test change triggers the normal Python CI workflow separately.

**Interpretation:** 6 km has the strongest apparent spatial availability in this one timestamp, especially around Biscayne Bay and offshore, while both 2 km and 6 km have almost no valid Keys coverage. This is a promising candidate for further evaluation, not grounds to switch production sources. The 1 km zero result needs a second-time check before concluding that the dataset is generally unavailable in South Florida.

**Boundary:** no production source configuration, Pull Ocean Data run, prediction logic, species biology, or weights were changed.


## HF Radar comparison validation | 2026-11-15 | corrected spatial bins

The corrected read-only comparison workflow completed successfully on [run #43731442828](https://github.com/markeetox/LUPITA/actions/runs/43731442828); artifact [14168636243](https://github.com/markeetox/LUPITA/actions/runs/43731442828/artifacts/14168636243) was retrieved and inspected. This run includes the shared fixed half-degree geographic-bin denominator introduced in commits `0ad8726` and `57fe6d7`.

At the exact common timestamp `2026-11-13T04:00:00Z`, the 1 km product had 0 paired vectors (0/285,069 native cells; 0/99 shared half-degree tiles), 2 km had 1,640 (2.293%; 6/99 tiles), and 6 km had 753 (9.436%; 19/99 tiles). Approximate subregion results for 2 km vs 6 km: Florida Keys 0% vs 0.337%, Biscayne Bay 10.732% vs 24.554%, offshore 5.701% vs 10.811%. Median HDOP was 0.56 for 2 km and 0.30 for 6 km; median radial counts were 35 and 100. The 1 km product returned the full grid but no valid paired vectors.

This is one timestamp, and native-grid percentages are not ocean-area coverage estimates. The products represent different nominal resolutions and depths (1/2/6 km; approximately 0.5/1.0/2.4 m). The 6 km product is the leading availability candidate for this snapshot only; no production source change is approved or implied.

**Next:** run a second exact timestamp shared by all three products, then compare temporal consistency. Evaluate a common ocean-only mask before making area-coverage claims. Keep source selection, ingestion configuration, scoring, and biology unchanged.


## Production refresh check | 2026-11-16

Latest inspected scheduled run: [Pull Ocean Data #43840037456](https://github.com/markeetox/LUPITA/actions/runs/43840037456), generated at `2026-11-16T09:29:14Z`. The full test step, catalog generation, prediction pipeline, publication, and final health evaluation completed. Predictions were refreshed and published; pipeline health is **degraded**, not healthy.

- SST `jplMURSST41`: observation `2026-11-14T09:00Z`, age 48.5h, delayed against the provisional 36h warning threshold; 55.2% valid aligned cells.
- Chlorophyll `nesdisVHNnoaa20chlaDaily`: observation `2026-11-13T12:00Z`, age 69.5h, still within the provisional 72h warning threshold; valid source fraction 7.94% (aligned 7.93%). Gap-filled source remains disabled.
- HF Radar `ucsdHfrE2`: failed with HTTP 404 from the Upwell ERDDAP fallback: `Currently unknown datasetID=ucsdHfrE2`. No current vectors were selected; query-region HFR coverage 0/10,101. The primary observation time is unknown.
- Satellite altimetry `nesdisSSH1day`: observation `2026-09-28T00:00Z`, age about 1,185.5h, correctly excluded from current-vector use by the 72h guard despite 75.9% aligned validity in the query region.
- No critical issues were recorded; optional currents layer failed. The published prediction snapshot was refreshed from this run.

This confirms the stale-altimetry guard is working, but the configured fallback host currently cannot resolve the HFR dataset ID. Treat this as a source-endpoint/dataset-availability issue requiring read-only verification before any code/configuration change. Do not substitute stale altimetry, alter source selection, or change prediction/scoring behavior without explicit review.

The separate read-only 1/2/6 km comparison remains open. Its corrected first snapshot was at `2026-11-13T04:00:00Z`; a second exact common timestamp is still required. No second comparison run was present in the inspected workflow history as of this review.


### HF Radar endpoint metadata cross-check | 2026-11-16

A read-only public metadata check after production run #43840037456 found that NOAA's Upwell ERDDAP still serves a page identifying `ucsdHfrE2` as the 2 km East/Gulf Coast HF Radar product. However, the inspected Upwell metadata snapshot reports `time_coverage_end=2026-11-10T17:00:00Z` and `date_created=2026-11-10T17:35:18Z`, several days before the production 404 on 2026-11-16. CoastWatch's public page also identifies the same dataset, but its inspected metadata snapshot is older (2026-09-30). These public pages are not proof that the exact bounded CSV endpoint was healthy at the time of the production request. The production 404 ("Currently unknown datasetID") and older metadata pages conflict; root cause remains unresolved. Verify live `.das`/dataset catalog and bounded CSV access on both hosts before changing source configuration.


## HF Radar second timestamp comparison | 2026-11-16

The manual read-only comparison [run #43893775875](https://github.com/markeetox/LUPITA/actions/runs/43893775875) requested the exact common timestamp `2026-11-12T04:00:00Z` but completed with an incomplete-product failure. The report artifact was generated before the nonzero exit:

- 1 km `ucsdHfrE1`: 0 valid paired vectors across 285,069 native-grid cells; 0/99 shared half-degree tiles.
- 2 km `ucsdHfrE2`: 1,201 valid paired vectors across 71,535 cells (1.679%); 8/99 shared tiles. Median HDOP 0.46, median sites 2, median radials 40.
- 6 km `ucsdHfrE6`: unavailable. Both configured ERDDAP attempts returned HTTP 404. The Upwell attempt's error reports a CoastWatch final response URL, indicating a redirect; this is not proof of two independent backend failures.

The diagnostic intentionally exits nonzero unless all three products are retrieved. This preserves the distinction between a complete comparison and a partial report. The workflow's artifact-upload step runs even after comparison failure, so the partial JSON/Markdown report remains available. No nearest-time substitution occurred.

**Interpretation:** the 2 km product is available at this second timestamp, with lower valid fraction than its November 13 sample (1.679% vs 2.293%). The 1 km product again has zero valid vectors. The 6 km product cannot be ranked at this timestamp because retrieval failed. The 6 km result from November 13 remains a single-snapshot observation, not a source-selection basis.

The report generator's invalid Python escape sequences before Markdown backticks were cleaned up in commit `cd3fbf0`, with a regression test in `dd38768`. This removes noisy SyntaxWarnings; it does not change retrieval, comparison, or exit behavior. Production HFR configuration, Pull Ocean Data, data publication, predictions, biology, and scoring remain unchanged.

**Next:** investigate the 6 km dataset ID and endpoint metadata using read-only checks; separately determine whether the 404 is a removed dataset, stale catalog, redirect/backend issue, or endpoint-specific behavior. Do not change production source selection until this is established.


### NOAA metadata clarification | 2026-11-16

A live read-only inspection of the [Upwell 6 km dataset form](https://upwell.pfeg.noaa.gov/erddap/griddap/ucsdHfrE6.html) clarifies the November 12 HTTP 404: the dataset ID `ucsdHfrE6` still exists on Upwell, but its current time-axis metadata ends at `2026-11-10T08:00:00Z` (time-axis `actual_range` 1786395600-1794297600 seconds since 1970-01-01). The requested `2026-11-12T04:00:00Z` is outside the published 6 km time range. The Upwell page identifies the expected variables and confirms 6 km grid spacing; its metadata says last dataset creation was 2026-11-10 09:00Z. Therefore the November 12 404 is consistent with an out-of-range timestamp, not evidence that the dataset ID was removed. A successful bounded CSV retrieval at an in-range time has not yet been confirmed.

The 1 km Upwell metadata currently reports a time-axis end of 2026-11-14 21:00Z. The 2 km HTML metadata snapshot is stale, so use actual successful bounded retrievals rather than that cached time range. Next comparison candidate: `2026-11-10T04:00:00Z`, which is within the 6 km published time range and earlier than its endpoint. Confirm all three products return that exact time before interpreting it as a valid three-way comparison. Production source selection remains unchanged.


## HF Radar comparison retry and CI fixture correction | 2026-11-16

The second candidate comparison [run #43894680887](https://github.com/markeetox/LUPITA/actions/runs/43894680887) requested `2026-11-10T04:00:00Z` and again could not retrieve `ucsdHfrE6`. Partial results: 1 km 0/285,069 vectors (0.000%); 2 km 1,614/71,535 (2.256%), 10/99 shared half-degree tiles, median HDOP 0.60, median sites 2, median radials 33; 6 km HTTP 404. Artifact ID `14237663318` was reviewed.

**Correction to prior metadata interpretation:** a newer live Upwell 6 km metadata page now reports `date_created=2026-11-16T13:42:13Z`, `time_coverage_end=2026-11-16T13:00:00Z`, and source history from the 2026-11-16 12:00 UTC HFR cycle. Therefore November 10 04:00 UTC is within the currently advertised time range. The prior metadata snapshot ending November 10 was stale by the time of this retry. The repeated 404 cannot be explained by the timestamp being outside the currently advertised range. The dataset page still advertises `ucsdHfrE6`, variables `water_u`, `water_v`, `hdop`, `number_of_sites`, and `number_of_radials`, and the expected 6 km grid. Root cause remains unresolved. The retry's Upwell request ultimately reports a CoastWatch URL after redirect, but the full redirect chain and response body were not captured by the previous utility.

The read-only comparison utility now records HTTP redirect chains, final response status/URL, and a short response body excerpt in retrieval failures (commit `87b8f75`), with a regression test (commit `43360cb`). This is diagnostic-only and does not change source endpoints or production behavior.

Python CI runs exposed two age-sensitive tests in `tests/test_currents_sources.py`: the fixture hard-coded satellite altimetry at 2026-11-13 11:00 UTC, which crossed the production 72-hour eligibility limit on November 16. The tests incorrectly assumed it remained eligible. The fixture now uses a timestamp one hour before test execution, while stale-fallback cases still explicitly use 2026-09-28 (commit `4b9e6b3`). Production current-source logic was not changed. CI must be rerun to confirm the fixture correction and diagnostic regression.

No Pull Ocean Data run, production source change, data publication, scoring, prediction, or biology change was made.


The final stale-fixture correction is commit `afb59bc`: one remaining stale-fallback test still replaced the old literal timestamp rather than the new relative fixture timestamp. That test now explicitly rewrites `ALT_TIME` to the September 28 stale observation. The resulting full-suite run [#43897319861](https://github.com/markeetox/LUPITA/actions/runs/43897319861) is pending at last inspection.


**Validation complete:** Python CI [#43897319861](https://github.com/markeetox/LUPITA/actions/runs/43897319861), commit `afb59bc7ae6e23f48b05f3a6c700ff86dbdd5ded`, passed **286 tests, 0 failures, 115 warnings**. Species profile audit and artifact upload also succeeded.


## HF Radar comparison blocked by NOAA ERDDAP request blacklist | 2026-11-16

The updated read-only comparison [workflow #43935416361](https://github.com/markeetox/LUPITA/actions/runs/43935416361) retried the previously successful common timestamp `2026-11-13T04:00:00Z`. It failed before producing any product measurements. The uploaded [artifact 14258784849](https://github.com/markeetox/LUPITA/actions/runs/43935416361/artifacts/14258784849) was retrieved and inspected.

All three products (`ucsdHfrE1`, `ucsdHfrE2`, `ucsdHfrE6`) returned HTTP 403 from both CoastWatch and Upwell ERDDAP hosts. The response body explicitly states that the requesting IP address is on the ERDDAP request blacklist and suggests excessive concurrent, repeated-identical, or invalid requests as possible triggers. The same 403 occurred on both hosts for all three products. This supersedes the current working theory that the latest failure is a 6 km-only HTTP 404 or timestamp issue. The diagnostic run provides no new coverage comparison values.

**Interpretation:** the comparison workflow's GitHub-hosted runner IP appears to have been blocked by NOAA ERDDAP. This is an access/rate-limit condition, not evidence that the three datasets are missing or that any product has zero coverage. Do not keep retrying identical requests from the same runner; that risks extending the block. Pause manual comparison runs and do not alter production source selection or endpoints based on this artifact. Resume only after NOAA access is restored or an approved, low-rate retrieval path is established.

No production ingestion, data publication, source configuration, prediction, biology, scoring, or weights changed. Python CI remains green at 286 passed, 0 failed, 115 warnings on run #43897319861.

## Species model-to-data audit | 2026-11-16

Completed a static end-to-end review of grid/site factor dispatch, source/layer construction, missing-data semantics, and confidence/evidence handling. The report is [MODEL_TO_DATA_AUDIT_2026-11-16.md](MODEL_TO_DATA_AUDIT_2026-11-16.md). Key confirmed contracts: grid scoring skips missing optional factors and renormalizes available weights; its scorer does not enforce factor-level `required`; site scoring does enforce `required`; and a site gate without `required` can be skipped when missing. Grid SST is foundational. Site `distance_to_inlet` remains a constant-zero placeholder and must stay inactive. Environmental coverage, source freshness, and biological evidence quality remain distinct. No scoring, biology, weights, source configuration, ingestion, or published data changed.

**Next:** add regression tests for existing runtime contracts and a factor-to-layer dispatch contract. Keep HFR comparison paused while the NOAA ERDDAP runner blacklist is active.

## Runtime model/data contract tests | 2026-11-16

Added regression coverage for grid/site missing-data semantics and catalog-to-runtime factor contracts. Tests exercise actual grid/site factor scoring with deterministic synthetic values and validate layer-builder keys using fake NOAA/FWC fixtures. Seasonal month context is injected by `build_fish_json`, so tests check it at the prediction boundary rather than expecting it from `load_layers`. Final commit `909fad3` passed Python CI, species-profile audit, and artifact upload: [run #43941668108](https://github.com/markeetox/LUPITA/actions/runs/43941668108). No production behavior, scoring, biology, weights, source configuration, ingestion, or publication changed.


## Prediction-level source lineage diagnostics | 2026-11-16

Added factor-level environmental source lineage to every generated prediction. Each active factor now reports source kind, location-level availability, mapped layer status, dataset/observation metadata, freshness where configured, and the species profile's evidence references. The mapping is regression-tested against every active factor in the species catalog. API v1 passes the extended diagnostics through unchanged.

Grid and named-site models are both covered. Named-site SST records the actual NDBC water-temperature observation time; tide diagnostics include station and prediction event times. Static layers remain static rather than receiving fake ages. HF Radar/altimetry and primary/gap-filled chlorophyll are explicitly reported as composite or multi-source where cell-level source attribution is not retained. NDBC freshness remains unconfigured, and tide retrieval freshness remains not assessed.

Validation: [Python CI #43944587159](https://github.com/markeetox/LUPITA/actions/runs/43944587159) passed **304 tests, 0 failures, 115 warnings**; species profile audit and artifact upload succeeded.

No prediction scores, confidence labels, biology, weights, source selection, missing-data behavior, ingestion, or publication logic changed.

**Next:** implement a separate evidence-quality summary. It must assess the strength and specificity of biological support, not merely count URLs or conflate source freshness with evidence quality. HFR comparison remains paused while NOAA ERDDAP blocks the comparison runner.


## Prediction-level evidence quality diagnostics | 2026-11-16

Added per-factor `evidence_diagnostics` and per-spot `evidence_summary`, both passed through API v1. These fields report the species profile's declared evidence status separately from the quality of its references. Homepage-only, specific path-based, missing, and malformed references are distinguished. A specific citation paired with `sourced` is labeled `declared_sourced_unverified`, not scientifically validated. Profile `value_notes` are included so limitations remain visible.

Per-spot summaries aggregate active factor weights by declared status and reference quality independently. These are configuration weight totals, not probabilities or scientific-confidence scores. No factor was automatically upgraded/downgraded, and no proposed confidence cap was activated.

Validation: [Python CI #43945487955](https://github.com/markeetox/LUPITA/actions/runs/43945487955) passed **307 tests, 0 failures, 115 warnings**; species audit and artifact upload succeeded.

No scores, confidence labels, biological values, weights, active flags, gates, minimum coverage, source selection, ingestion, or publication behavior changed.

**Next:** manually review the 20 homepage-only site SST factors and the 12 profiles with elevated active evidence risk. Replace references or change declared statuses only after checking whether the cited source supports the exact factor claim, numeric band, population, and life stage.


## Named-site SST evidence review | 2026-11-16

Completed source discovery and claim-fit review for all 20 named-site profiles whose active SST factor previously cited only the generic NOAA Fisheries homepage. Findings and source register: `docs/NAMED_SITE_SST_EVIDENCE_REVIEW_2026-11-16.md`.

The review found one profile with close support for both the configured outer range and ideal interval (Spanish mackerel). Eleven profiles have useful but incomplete evidence that supports broad occurrence, migration, or selected life stages without validating the exact ideal band (Atlantic croaker, blacktip shark, bluefish, bull shark, ladyfish, lane snapper, scup, spotted seatrout, striped bass, summer flounder, winter flounder). Eight remain provisional/needs-source candidates because the available material does not support the configured numeric band (American shad, false albacore, spinner shark, spot, tautog, tripletail, weakfish, white grunt).

Important limitations include bottom-vs-surface temperature mismatch, life-stage/stock differences, regional transferability, modeled vs observed temperature associations, and occurrence vs preference. All 20 are single-factor site pilots with SST both required and a gate, so the quality of this one input controls site eligibility.

No species profile, source list, status, numeric range, ideal band, weight, active flag, gate, required flag, score, confidence, or ingestion behavior changed. The report contains recommendations for owner approval only. Next: agree on the conservative evidence-status recommendations, then apply approved source/reference/note changes without changing numerical biology.


### Named-site SST evidence metadata updated | 2026-11-16

Owner-approved source review was applied to all 20 homepage-only named-site SST profiles. Statuses: 1 `sourced` (Spanish mackerel), 11 `partly_sourced`, 5 `provisional`, and 3 `needs_source`. Profile and active-factor references now point to species-specific sources; `value_notes` document claim-fit limitations. No numeric bands, ideal intervals, weights, gates, required flags, timing, scoring, confidence behavior, ingestion, or data publication changed. See [named-site SST evidence review](NAMED_SITE_SST_EVIDENCE_REVIEW_2026-11-16.md).


### Follow-up SST evidence review | 2026-11-16

Completed a second source review for spot, weakfish, and white grunt. Each now has species-specific references and conservative `partly_sourced` evidence status with explicit caveats. Updated totals for the 20 named-site SST profiles: 1 sourced, 14 partly sourced, 5 provisional, 0 needs-source. No numeric bands, ideal intervals, weights, gates, required flags, timing, scoring, confidence behavior, ingestion, or publication changed. See [review report](NAMED_SITE_SST_EVIDENCE_REVIEW_2026-11-16.md).


## All-species evidence audit inventory | 2026-11-17

Completed a master inventory of all 130 profiles using the species audit artifact from [Python CI #43952010312](https://github.com/markeetox/LUPITA/actions/runs/43952010312). All 130 JSON files parsed and were structurally valid, with zero model-compatibility issues. The catalog contains 105 grid models and 25 site models: 23 temperature-only site pilots, 27 other single-factor models, and 80 multi-factor models.

The audit identifies 64 profiles with elevated active-evidence risk, 14 with partial risk, and 52 with no active uncertain weight under current metadata checks. Combined active uncertain factor weight is 37.4 across profiles; this is not a probability or calibrated evidence score. The validator recorded 96 generic-homepage source findings across 48 profiles and 3 missing factor-source findings across two profiles (sailfish and tarpon). It also flagged 27 grid profiles whose `required` flag is ignored by the grid scorer. These are prioritization signals, not proof of biological invalidity.

The 20 reviewed named-site SST profiles are now 1 sourced, 14 partly sourced, and 5 provisional. Three temperature-only site pilots remain for source-by-source review: bonefish, great barracuda, and Permit. Next sequence: finish those three; review all 27 other single-factor profiles; then review the 80 multi-factor profiles by factor family, prioritizing the 29 with elevated active-evidence risk. Timing claims and profile-level biological narratives will be audited separately.

Full scope, counts, review standard, and guardrails: [all-species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md). No species values, weights, gates, required flags, scoring, confidence, source selection, ingestion, or publication behavior changed.


## Temperature-only site pilot evidence review: Batch A | 2026-11-17

Completed source research for the three remaining temperature-only site pilots: bonefish, great barracuda, and Permit. Bonefish adult studies provide laboratory performance optima (26.7–28.0 °C) and broad field exposure/critical-temperature data in the Bahamas, but not a South Florida habitat-preference curve. Great barracuda has South Florida archival-tag exposure data from only two large adults (17.8–31.3 °C), plus a model-derived FishBase estimate; neither establishes a preferred interval. Permit has a FishBase model estimate, a 2026 Texas juvenile-presence association above 25 °C, and a 1972 South Carolina juvenile occurrence range of 12.8–38.5 °C; none validates adult South Florida SST preference.

Recommended metadata: bonefish and great barracuda may move from provisional to partly_sourced with strict caveats; Permit remains provisional. No profile JSON or prediction setting has been changed pending review. Full sources and reasoning: [all-species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).


## Other single-factor species SST evidence review | 2026-11-17

Completed source research for the 27 non-site single-factor grid profiles. All had one active `sst_c` factor with a gate and generic NOAA Fisheries homepage-only citation. Review recommendations: 20 partly_sourced, 3 provisional (great hammerhead, ocean triggerfish, pollock), and 4 needs_source for the active SST claim (misty grouper, rainbow runner, Warsaw grouper, yellowedge grouper). Many demersal/deep-water species have source evidence describing bottom temperature or habitat at 30–370 m; that does not validate satellite SST as the gating input. This is a model-to-data mismatch requiring a separate design review, not a reason to silently substitute bottom temperature. No species JSON or model setting changed. Details and source register: [all-species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).


## Multi-factor evidence review | first four profiles | 2026-11-17

Completed the first four elevated-risk multi-factor profile reviews: African pompano, Almaco jack, black grouper, and black sea bass. Replaced generic homepage-only factor citations with traceable species-specific sources where available and revised active factor evidence statuses/notes. African pompano and Almaco jack SST claims are now needs_source; black grouper factors are partly_sourced; black sea bass structure is sourced while SST and depth remain partly_sourced. The main limitation is claim fit: occurrence is not preference, bottom temperature is not satellite SST, and documented habitat does not validate numeric category score weights. No numeric bands, ideal intervals, category maps, factor weights, active flags, gates, required flags, scoring, confidence, source selection, ingestion, or publication behavior changed. Full rationale and source register: [all-species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).


## Multi-factor evidence review | second four profiles | 2026-11-17

Completed the second multi-factor evidence batch: cubera snapper, gag grouper, red grouper, and red snapper. Replaced generic homepage-only factor references and updated evidence statuses/notes across 12 active factors. All factors remain partly_sourced because the available sources support broad occurrence, habitat, or life-stage relationships but do not validate every configured interval or numeric category score. Gag bottom-curvature evidence is especially indirect: terrain ruggedness is not identical to the runtime bottom_curvature variable. No numeric bands, category maps, weights, active flags, gates, required flags, scoring, confidence, source selection, ingestion, or publication behavior changed. Details: [all-species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).


## Multi-factor evidence review | third four profiles | 2026-11-17

Completed the third multi-factor batch: gray triggerfish, gray (mangrove) snapper, scamp grouper, and snowy grouper. Replaced generic homepage factor references with species-specific sources and updated 12 active factor statuses/notes. Gray triggerfish, gray snapper, and scamp factors are partly_sourced; snowy grouper SST is needs_source because available temperature records are deep bottom-water spawning observations, not SST, while slope and depth remain partly_sourced. No numeric bands, weights, active flags, gates, required flags, scoring, confidence, source selection, ingestion, or publication behavior changed. Details: [all-species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).


## Multi-factor evidence review | third four profiles | 2026-11-17

Completed the third multi-factor batch: gray triggerfish, gray (mangrove) snapper, scamp grouper, and snowy grouper. Replaced generic homepage factor references with species-specific sources and updated 12 active factor statuses/notes. Gray triggerfish, gray snapper, and scamp factors are partly_sourced; snowy grouper SST is needs_source because available temperature records are deep bottom-water spawning observations, not SST, while slope and depth remain partly_sourced. No numeric bands, weights, active flags, gates, required flags, scoring, confidence, source selection, ingestion, or publication behavior changed. Details: [all-species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).


## All-species validator refresh after 12 multi-factor reviews | 2026-11-17

Latest Python CI [#44123016856](https://github.com/markeetox/LUPITA/actions/runs/44123016856) passed: all 130 species profiles parsed and were structurally valid, with zero model compatibility issues and zero validator errors. After the first 12 elevated-risk multi-factor profiles were metadata-updated, elevated active-evidence risk decreased from 64 to 55 profiles, partial risk increased from 14 to 23, and combined uncertain active weight decreased from 37.4 to 26.4. Generic homepage-only findings decreased from 96 across 48 profiles to 59 across 36 profiles. The updated multi-factor risk distribution is 20 elevated, 9 partial, and 51 documented. These are validator classifications, not biological-quality scores. No numeric model settings or prediction behavior changed. See [all-species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).


## Pelagic multi-factor evidence review | 2026-11-17

Reviewed Atlantic blue marlin, Atlantic bluefin tuna, sailfish, and tarpon. Replaced generic factor references for blue marlin/bluefin with tagging, NOAA, ICCAT, and habitat-model sources; updated source-fit notes and conservative statuses. Blue marlin SST, SST-gradient, current-convergence, depth, and season are partly_sourced; Gulf Stream edge remains provisional. Bluefin active factors are partly_sourced, with explicit separation of fish dive depth from seafloor bathymetry. Sailfish current convergence was downgraded to partly_sourced; inactive cold_front now has angler references but remains provisional. Tarpon inactive salinity now has an EFH source and remains partly_sourced; bridges_lights remains needs_source. No numeric values, active flags, weights, gates, required flags, season months, scoring, or runtime behavior changed. Details: [all-species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).


## Coastal pelagic multi-factor evidence review | 2026-11-17

Reviewed blackfin tuna, cobia, common snook, and Florida pompano. Updated evidence sources/notes across active factors while preserving all numeric model settings. Blackfin SST and bottom-slope factors are partly_sourced; gradient/chlorophyll gradient and Gulf Stream distance remain provisional, and its bathymetric depth band is only partly supported. Cobia SST and seasonal presence are partly_sourced; depth remains provisional because tag depth is fish vertical depth, not seafloor bathymetry. Snook temperature notes now include 2025 field/lab studies; tide and time-of-day remain provisional. Florida pompano SST, depth, and season are partly_sourced with life-stage and surf-zone caveats. No numeric ranges, weights, active flags, gates, required flags, season months, scoring, or runtime behavior changed. Details: [all-species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).


## Batch A/B evidence metadata implementation | 2026-11-17

Applied metadata-only source/status/note updates to all 30 remaining single-factor profiles. Great barracuda moved from provisional to partly_sourced; bonefish and Permit remain provisional because available evidence does not validate their numeric SST bands. Of the 27 other single-factor grid profiles, 20 are now partly_sourced, three provisional, and four needs_source. The four needs_source profiles retain no factor-level SST references because available habitat sources do not validate numeric surface-temperature claims. No numeric model settings or runtime behavior changed. CI validation is running in [#44124511157](https://github.com/markeetox/LUPITA/actions/runs/44124511157). Details: [all-species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).



## Batch C evidence review | 2026-11-17

Reviewed Hogfish, Jack crevalle, King mackerel, and Red drum across 13 active factors. Added specific sources and conservative claim-fit notes. Hogfish SST and king mackerel SST-gradient factors are needs_source; the remaining reviewed factors are partly_sourced. Broad thermal occurrence, depth/habitat records, spawning timing, and migration evidence were not treated as validated preferred-value or catch-response curves. No numeric model settings or runtime behavior changed. Details: [all-species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).


## Batch C completed | 2026-11-17

Completed source-by-source review of all 29 profiles originally classified as elevated active-evidence risk. The final five reviewed were Mahi-mahi, Mutton snapper, Sheepshead, Southern flounder, and Wahoo (26 active factors). Evidence metadata was updated without changing numeric ranges, ideal intervals, weights, active flags, gates, required flags, month lists, scoring, confidence, ingestion, or publication behavior.

Important open issue: a 2023 fisheries assessment cites southern flounder as absent from southern Florida between the Loxahatchee and Caloosahatchee rivers. The profile now carries a regional-applicability warning; no factor was disabled and no prediction behavior changed. See [SPECIES_EVIDENCE_AUDIT_2026-11-17.md](SPECIES_EVIDENCE_AUDIT_2026-11-17.md) for source-by-source findings.

Next: refresh/review the validator artifact after these metadata updates, then continue the remaining partial-risk multi-factor profiles and documented profiles. Keep regional species applicability, biological evidence, environmental source freshness, and prediction confidence as separate concerns.


## Validator reconciliation | 2026-11-17

Batch C validation [#44127699186](https://github.com/markeetox/LUPITA/actions/runs/44127699186) passed 307 tests, with 0 failures and 115 warnings. The species audit inspected 130 profiles: 130 structurally valid, 0 compatibility issues, 0 JSON parse errors. Current evidence-risk counts are 30 elevated, 48 partial, and 52 documented; among multi-factor models, 16 are elevated, 13 partial, and 51 documented. Combined active uncertain factor weight is 10.34, not a probability or percentage.

The 29 originally elevated-risk multi-factor profiles have all been source-reviewed. The current elevated and partial classifications do not mean those profiles are unreviewed; they reflect the conservative status of the evidence. Next queue: source-by-source claim-fit review of the 51 documented multi-factor profiles. “Documented” is a validator metadata category, not proof that every numeric biological claim is scientifically validated. Keep the southern flounder South Florida distribution caveat open. Details: [species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).


## Documented multi-factor evidence review started | 2026-11-17

Started claim-fit review of the 51 multi-factor profiles currently classified as documented by the validator. First batch: Black rockfish, Blue rockfish, Bocaccio rockfish, Canary rockfish, and Copper rockfish across 11 active factors. Specific species/habitat references replaced generic regulations pages. Important findings include unsupported numeric SST claims, life-stage limitations, and bottom-temperature evidence that cannot validate satellite SST. Five of 51 documented multi-factor profiles reviewed. No numeric or runtime behavior changed. See [species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).


## Documented multi-factor review | second Pacific nearshore batch

Reviewed Gopher rockfish, Kelp rockfish, Olive rockfish, Treefish, and Halfmoon across 10 active factors. Replaced generic regulation-page references with specific CDFW, ODFW, NOAA, Smithsonian Tropical Research Institute, FishBase and aquarium sources. All five SST bands are now marked needs_source because the reviewed evidence did not substantiate the configured numeric SST preferences; depth/habitat evidence is partly_sourced with range and life-stage caveats. No numeric or runtime changes. Total documented multi-factor review progress: 10 of 51 profiles across 21 active factors. See [species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).


## Documented multi-factor review | third California coastal batch

Reviewed Kelp bass, California yellowtail, Giant sea bass, Opaleye, and Spotted sand bass across 10 active factors. Replaced generic regulation-page citations with specific CDFW, Smithsonian, FishBase, USGS and research sources. Kelp bass SST has qualitative recruitment support but no numeric optimum; California yellowtail has broad thermal evidence but bathymetry is only a weak proxy; Giant sea bass SST remains needs_source; Opaleye's broad temperature envelope is provisional; Spotted sand bass has a model-derived temperature estimate, not field-validated preference. All depth/habitat factors are partly supported with caveats. No numeric or runtime changes. Progress: 15 of 51 documented multi-factor profiles across 31 active factors. See [species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).


## Documented multi-factor review | fourth demersal flatfish/cod batch

Reviewed California halibut, Pacific halibut, Petrale sole, Starry flounder, and Pacific cod across 10 active factors. Added NOAA, USGS, IPHC, WDFW, ODFW and DFO evidence. California halibut has life-stage-specific thermal evidence; Pacific halibut, Petrale sole and Pacific cod bottom-temperature records do not validate satellite SST; Starry flounder temperature evidence is broad occurrence only. Depth factors are partly sourced with seasonal and life-stage caveats. No numeric or runtime changes. Progress: 20 of 51 documented multi-factor profiles across 41 active factors. See [species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).


## Documented multi-factor review | Pacific salmon thermal-habitat batch

Reviewed Chinook, Coho, Chum, Pink and Sockeye salmon across 10 active factors. Added the 2024 North Pacific species-specific SST distribution study, NOAA species pages, Chinook telemetry, and chum migration-corridor evidence. The modeled preferred SST ranges are generally colder than the configured bands; pink salmon estimates differ by brood-cycle parity. All five bathymetry factors are marked weak_factor because fish vertical depth is not seafloor depth. No numeric or runtime changes. Progress: 25 of 51 documented multi-factor profiles across 51 active factors. See [species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).


## Documented multi-factor review | fifth Pacific rocky-reef batch

Reviewed Lingcod, Cabezon, Kelp greenling, Ocean whitefish and Yelloweye rockfish across 11 active factors. Replaced generic regulation-page citations with WDFW, ODFW, CDFW, NOAA AFSC, IUCN and Smithsonian sources. SST factors are needs_source across all five; depth and lingcod bottom-curvature are partly_sourced with life-stage/range/metric caveats. No numeric or runtime changes. Progress: 30 of 51 documented multi-factor profiles across 62 active factors. See [species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).


## Documented multi-factor review | sixth sharks/rays/tuna batch

Reviewed Bat ray, Common thresher shark, Leopard shark, Soupfin shark, and Pacific bluefin tuna across 10 active factors. Added California Sea Grant, Florida Museum, WDFW/CDFG, NOAA and peer-reviewed tagging sources. Bat ray and soupfin shark SST remain needs_source; other thermal claims are partly sourced with population/region caveats. Bathymetry is weak_factor for common thresher and Pacific bluefin because their tag depths are vertical water-column occupancy. No numeric or runtime changes. Progress: 35 of 51 documented multi-factor profiles across 72 active factors. See [species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).


## Documented multi-factor review | seventh pelagic species batch

Reviewed Opah, Pacific barracuda, Pacific bonito, Pacific hake and Striped marlin across 10 active factors. Added California Sea Grant, NOAA, Aquarium of the Pacific, Smithsonian, peer-reviewed tagging and fisheries sources. Opah now has a taxonomic open issue: the Pacific opah complex was split in 2018, while the profile remains Lampris guttatus. Pacific barracuda/hake SST remain needs_source; pelagic vertical depth is distinguished from bathymetry. No numeric or runtime changes. Progress: 40 of 51 documented multi-factor profiles across 82 active factors. See [species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).


## Documented multi-factor review | eighth California coastal batch

Reviewed Barred sand bass, Barred surfperch, Redtail surfperch, Rock greenling and White seabass across 10 active factors. Added CDFW, NOAA, WDFW, DFO and peer-reviewed thermal/habitat sources. Barred surfperch physiological data support a thermal response but not a catch curve; redtail surfperch has broad occurrence temperatures; rock greenling bottom temperatures do not validate SST; white seabass tags show ambient temperatures centered below the configured ideal. No numeric or runtime changes. Progress: 45 of 51 documented multi-factor profiles across 92 active factors. See [species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).


## Documented multi-factor evidence review complete | 2026-11-17

Completed source-by-source claim-fit review of all 51 profiles that were classified as documented multi-factor models by the validator, covering 105 active factors. The final six reviewed were Dungeness crab (reference), Sablefish, Steelhead, Vermilion rockfish, White sturgeon and Yellowtail snapper. Sources were upgraded to species-specific NOAA, WDFW, CDFW, OPC, USGS, SEDAR and peer-reviewed research. The review identified remaining needs_source SST factors, weak bathymetry proxies, life-stage/region mismatches, and two taxonomic open items (Opah and Dungeness crab naming). No numeric ranges, ideal intervals, weights, active flags, gates, required flags, scoring, confidence, ingestion or publication behavior changed. Fresh validator reconciliation is next. See [species evidence audit](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).


## Final species evidence review checkpoint | 2026-11-17

All 130 species profiles have received source-by-source evidence review. Final CI [#44131162206](https://github.com/markeetox/LUPITA/actions/runs/44131162206) passed 307 tests, 0 failures, 115 warnings. Final validator: 130 parsed, 130 structurally valid, 0 JSON errors, 0 model-compatibility issues, 0 validator errors, 590 warnings and 120 informational findings.

Evidence risk is 68 elevated, 61 partial, and 1 documented. Combined active uncertain factor weight is 29.84 (not probability or percentage). The validator classifies 127 profiles NEEDS MODEL REBUILD and 3 NEEDS RESEARCH; this is biological-completeness prioritization, not runtime breakage. The 51 initially documented multi-factor profiles have now been reviewed across 105 active factors; many were correctly reclassified after claim-fit review. See [SPECIES_EVIDENCE_AUDIT_2026-11-17.md](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).

Next phase is a controlled model-rebuild plan, not another broad citation pass. Resolve Southern flounder regional applicability, Opah and Dungeness crab taxonomy, White sturgeon ocean-grid scope, bottom-temperature versus SST mismatches, and bathymetry versus fish vertical-depth proxies. No numerical biology, factor weights, active flags, gates, scoring, confidence or runtime behavior changed in this evidence review.


## Controlled model-rebuild planning started | 2026-11-17

Phase 0 identified a geographic eligibility issue: 25 of 130 grid profiles have no `lat_range`, and the grid scorer therefore applies only their broad longitude bound. The source envelope is 15–60°N, 138°W–50°W. No guessed bounds were added.

Taxonomy metadata was normalized for Eastern North Pacific opah (`Lampris incognitus`, supported by the 2018 revision and NOAA Monterey Bay checklist) and Dungeness crab (`Metacarcinus magister`, accepted name; `Cancer magister` retained as synonym). Southern flounder has a discontinuous Florida distribution; white sturgeon is primarily riverine/estuarine and only occasionally marine. Both need explicit scope decisions.

The plan separates surface SST from bottom temperature and ETOPO seafloor bathymetry from fish vertical depth. No prediction formulas, numeric bands, weights, gates, active flags, environmental source selection, ingestion or publication behavior changed. See [MODEL_REBUILD_PLAN_2026-11-17.md](MODEL_REBUILD_PLAN_2026-11-17.md).

## Geographic scope research update | 2026-11-17

Completed a first source pass for all 25 grid profiles that lack latitude bounds. NOAA, state, council, museum, VIMS, WoRMS and FishBase sources now document range statements in the model-rebuild plan. These are not yet translated into numeric bounds: several include stock boundaries, seasonal migration, island absences or disjoint Florida distribution. Black sea bass, king mackerel, cobia, sheepshead and southern flounder need regional treatment rather than a guessed rectangle. No geographic bounds or scoring behavior changed.


## Measurement-alignment audit | 2026-11-17

Confirmed that runtime `sst_c` is NOAA MUR sea-surface temperature and `depth_m` is ETOPO seafloor bathymetry sampled at stride 15 (broad regional context, not reef scale). Five demersal profiles (Pacific halibut, Petrale sole, Pacific cod, Sablefish, Rock greenling) have active SST factors marked `needs_source` because the cited temperature evidence is bottom-water or fish-depth data, not validated SST. Pelagic examples (bluefin tuna, blue marlin, mahi-mahi, opah, steelhead) show fish vertical depth must not be treated as seafloor depth; bluefin and blue marlin depth factors are active gates, while mahi-mahi and steelhead are weak proxies.

Next design work: evaluate a validated bottom-temperature input and decide whether fish vertical depth merits a separate variable. No environmental source, factor, gate, weight, numeric range, score or confidence behavior changed. CI after taxonomy/scope metadata passed 307 tests on #44134514836.
