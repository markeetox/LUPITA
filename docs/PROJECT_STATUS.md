# LUPITA project status

**Last reviewed:** 2026-11-14  
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
