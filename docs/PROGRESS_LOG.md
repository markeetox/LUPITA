# LUPITA progress log

This is the chronological engineering record. Keep entries concise but reproducible: date, branch/commit, change, reason, validation, result, and next action. Add a new entry for every meaningful implementation batch. Do not rewrite old entries to make historical results look current.

## 2026-11-13 | Establish repository progress records and repair landmark workflow preflight

**Branch:** `research/biscayne-noaa-enc-hydrography`  
**Starting commit:** `85afcff7cf4ee18e926a8accd29946b600018be0`  
**Related PR:** [#70](https://github.com/markeetox/LUPITA/pull/70), stacked on [#69](https://github.com/markeetox/LUPITA/pull/69)

### Repository review

- Confirmed the active research branch and its open PR dependency chain.
- Reviewed the current README, research pipeline policy, landmark reconciliation notes, focused workflow, topology script, and topology tests.
- Confirmed that the README did not adequately describe the active GIS research architecture and that its scheduled pipeline cadence text was stale.

### Changes in this batch

- Added this progress log and a current project-status record.
- Updated README architecture, operational process, workflow cadence, and documentation links.
- Corrected the unmatched parenthesis in the Jewfish Creek depth-context expression. The first automated correction retained one extra closing parenthesis; the new compile preflight caught it before extraction.
- Replaced literal escaped newline sequences between Jewfish Creek assertions with actual source line breaks.
- Added a focused `py_compile` preflight before tests and extraction in the landmark evidence workflow.

### Validation

- The original topology expression was independently confirmed to raise a Python `SyntaxError` because a closing parenthesis appeared before the list-comprehension bracket.
- The repository workflow must now run focused compilation before pytest and network extraction.
- First validation attempt: [focused landmark workflow run #31](https://github.com/markeetox/LUPITA/actions/runs/43448214612) failed at the compile preflight because the first correction retained one extra closing parenthesis. No source extraction ran.
- The repository-wide Python test run also failed during collection for the same syntax error: [Python tests run](https://github.com/markeetox/LUPITA/actions/runs/43448214278).
- The test file's escaped assertion separators were replaced with real line breaks and are present correctly in the branch.
- A follow-up syntax correction is now committed; focused validation on the current head remains required.

### Decisions and guardrails retained

- Keep all NOAA/FDEP/FWC/county research geometry separate from production prediction inputs.
- Do not infer Government Cut, inlet connectivity, or cross-bay separators from proximity.
- Keep MHW, MHHW, and MLLW concepts separate.
- Reuse persisted research sources; do not repeat extraction unless inputs or logic change.

### Next action

Run the focused Biscayne landmark evidence workflow once the commit is pushed, then inspect its artifact and update this log with the actual run URL and test counts.


## 2026-11-13 | Begin single-main consolidation and isolate data publication

**Production target:** `main`  
**Staging branch:** `integration/main-consolidation`  
**Excluded branch:** `data`

### Repository and branch audit

- Confirmed `main` at `c91e091155f816449713726226ee120c945fd951` and the separate `data` publication branch.
- Audited branch comparisons for spatial-context, Biscayne GIS, NOAA hydrography, in-situ temperature, species framework/validation, habitat, prediction reliability, data-quality, ERDDAP, and pipeline-health work.
- Identified several stale or duplicate branches and several branches that modify overlapping core files. These require content-level consolidation rather than blind merges.
- Confirmed the hourly pipeline executes from the checked-out application branch and publishes generated app-facing files to `data`. The previous-`data` checkout is optional and used only to retain last-known-good exports.

### Staging changes

- Created `integration/main-consolidation` from `main`.
- Squash-merged PR #69 (Biscayne GIS foundation) and PR #66 (South Florida in-situ temperature audit) into the staging branch. Neither was merged into production `main`.
- Retargeted PRs #68, #69, and #66 to the staging branch before merging.
- Corrected PR #68's unknown-geometry test to assert the catalog's actual explicit no-spatial-membership guard. Commit: `b96ec913e62f0333e7b6ca56466a35acb4f7daf0`. A fresh run on the updated head is pending.

### GIS workflow reliability

- Fixed Jewfish Creek shared-boundary measurement: evaluate exact topology in source coordinates, then project the shared line to EPSG:26917 for metre measurement. This avoids projection-segmentation artifacts that produced a false zero in the synthetic fixture.
- Changed five expensive source-acquisition workflows to manual-only: Biscayne GIS audit, NOAA Biscayne hydrography, NOAA shoreline audit, NOAA CMP/FDEP alignment, and NOAA NSDE project discovery.
- Kept the focused landmark evidence workflow available for PR validation, with compile preflight before tests and extraction.
- Purpose: prevent PR synchronize events from repeatedly launching network extraction and committing generated data back to the same branch.

### Validation state

- PR #69 Python tests and GIS extraction workflow passed before squash merge.
- PR #66 Python tests and in-situ temperature audit passed before squash merge.
- PR #68 previously had 193 passed and one failed test; the failure was a brittle phrase assertion, now corrected. Rerun pending.
- Jewfish Creek source-coordinate topology correction and manual-only workflow changes are committed to the research branch; focused validation is pending.
- Vercel status checks on earlier PR heads reported deployment rate limiting, not application test failures.

### Next actions

1. Run the current PR #68 Python suite and focused PR #70 landmark workflow.
2. Retarget PR #70 to the staging branch after confirming the #69 foundation is already present.
3. Review remaining unique branches against the staged tree, preserving only changes not superseded by main or other selected branches.
4. Implement and validate the final main-to-data export boundary, then prepare one consolidated PR to `main`.


## 2026-11-13 | Consolidate Biscayne research and resolve superseded PRs

**Staging branch:** `integration/main-consolidation`  
**Consolidation commit:** `4c84158bac5bc18efe780c4487a119b26865f510`

### Changes

- Merged PR #68 after its corrected current-head Python tests and species validator both passed:
  - Python tests: https://github.com/markeetox/LUPITA/actions/runs/43450291705
  - Species validator: https://github.com/markeetox/LUPITA/actions/runs/43450292042
- Imported 85 added/updated paths from the NOAA hydrography research branch into the integration tree in one consolidated commit. This preserves the GIS scripts, source geometry, audits, topology reports, research documentation, and manual-only workflows without importing 444 branch commits.
- Preserved integration-specific files from the spatial-context and in-situ work rather than replacing them with older versions from the stacked NOAA branch.
- Retargeted PR #70 to the staging branch, then closed it as superseded after its content was imported. Its old branch dependency on PR #69 is no longer required.
- Reviewed PR #71 against the current integration tree. The confidence basis, API data-quality fields, site-kind labels, and regression test were already present; closed it as superseded rather than merging stale core files.
- The five expensive source-acquisition workflows remain manual-only. The focused landmark workflow remains the PR validation path.

### Validation

- PR #68: 193 passed, 0 failed on the corrected head; the species validator also passed.
- Local Shapely/pyproj reproduction of the Jewfish Creek synthetic fixture measured a 100.7629 m shared boundary when topology is evaluated in source coordinates and only the resulting line is projected for length.
- The previous PR #70 workflow attempts returned `action_required` with no jobs, so they are not counted as successful validation. A fresh full-suite and focused GIS run is still required on the consolidated staging tree.
- Production `main` and the separate `data` branch have not been modified by these consolidation operations.

### Next actions

1. Audit remaining branches for genuinely unique code versus changes already present in current `main`.
2. Keep only useful, non-superseded changes in staging; do not import stale profile or pipeline files.
3. Run one full Python suite and one focused GIS validation pass on the consolidated tree.
4. Prepare the final single PR into `main`, keeping `data` as the generated export destination only.


## 2026-11-13 | Fix consolidated CI dependencies and stop research extraction fan-out

**Staging branch:** `integration/main-consolidation`

### Validation findings

- The focused Biscayne landmark workflow passed on the consolidated PR:
  https://github.com/markeetox/LUPITA/actions/runs/43452278652
  - Python compile preflight passed.
  - Focused extraction tests passed.
  - Card Sound/Jewfish Creek/Rickenbacker extraction passed.
  - Topology reconciliation and all focused topology tests passed.
- The species-validator workflow failed during test collection because the full suite now includes GIS research tests importing Shapely, PyProj, and PyShp, but that workflow installed only `requirements.txt`.
- The main Python test workflow already installed those packages directly and was still running when this entry was written.

### Changes

- Added `requirements-research.txt` for optional GIS/research QA dependencies. These are not part of production runtime requirements.
- Updated Python tests, species validation, and the scheduled production workflow to install the research requirements before running the full suite.
- Enabled pip caching in the scheduled workflow to reduce repeated hourly installation overhead.
- Changed the South Florida in-situ temperature extraction workflow to manual-only. It had an unexpected pull-request trigger and started downloading logger observations during the consolidation PR.
- Updated README and project status to explain the distinction between production runtime dependencies and optional research/test dependencies.

### Next actions

1. Verify the new full-suite and species-validator runs pass on the updated PR #72 head.
2. Confirm only lightweight validation workflows run automatically on PRs.
3. Complete the final branch inventory, then merge PR #72 only after all required checks pass.


## 2026-11-13 | Consolidated validation passes; data branch verified as export-only

**Final PR:** [#72](https://github.com/markeetox/LUPITA/pull/72)  
**Validated head:** `161e54781396970839a88f2393282ffd1d54121e`

### Validation results

- Full Python suite: **248 passed, 115 warnings**  
  https://github.com/markeetox/LUPITA/actions/runs/43452687288
- Species profile validator: **248 passed, 115 warnings**; inspected 130 profiles, 127 structurally valid, 0 model compatibility issues, 127 requiring additional research/model rebuilding  
  https://github.com/markeetox/LUPITA/actions/runs/43452687083
- Focused Biscayne landmark evidence: extraction and topology reconciliation succeeded; **4 topology tests passed, 50 warnings**  
  https://github.com/markeetox/LUPITA/actions/runs/43452687098
- The South Florida in-situ temperature audit completed successfully on the prior PR head. Its pull-request trigger has since been removed so future PRs do not repeat source downloads.

### CI and workflow corrections

- Added `requirements-research.txt` for Shapely, PyProj, and PyShp. These are optional research/test dependencies and are not added to production `requirements.txt`.
- Updated Python tests, species validation, and the scheduled pipeline to install research dependencies before the full test suite.
- Added pip caching to the scheduled workflow.
- Made the in-situ temperature audit manual-only, alongside the five FWC/NOAA acquisition workflows.
- The initial species-validator run failed because those packages were missing; the corrected workflow now passes.

### Data branch verification

- Inspected the current `data` branch tree: 725 paths.
- Top-level contents are generated API/data outputs: `api/`, `species/`, `heat/`, and JSON exports such as `fish.json`, `latest.json`, `closures.json`, `stream.json`, and `species_catalog.json`.
- No Python, JavaScript, TypeScript, YAML, or Markdown source files are present.
- This confirms `data` is currently an export/publication branch, not a code branch. It remains excluded from PR #72.

### Remaining external status

- Vercel's PR preview status is red because the account is rate-limited for 24 hours. This is an external deployment quota, not a failing test or build result. No frontend source changes are included in this consolidation.

### Next action

Merge PR #72 into `main` after reviewing the Vercel preview limitation. Then archive/delete obsolete branches, leaving `main` and `data` as the active branch pair.


## 2026-11-13 | Merge single-main consolidation into production

**Merged PR:** [#72](https://github.com/markeetox/LUPITA/pull/72)  
**Production merge commit:** `1526aecd12c0561b6c3cf9fc8250110fb8de0a11`

### Result

- PR #72 successfully merged into `main` using a squash merge.
- `main` is now the authoritative application, prediction, research, test, documentation, and workflow branch.
- The separate `data` branch remains the generated publication target and was not modified by the consolidation.
- The `data` branch was verified at head `ba3194b19a235bc4859c623ee9fda9f6b19075b7`: 725 generated JSON/API/PNG paths, no source-code files.
- The old stacked NOAA PR and the superseded prediction-reliability PR were closed. Their useful changes are either in `main` or already present in the current codebase.

### Final validation on the consolidated code tree

- Python suite: 248 passed, 115 warnings.
- Species validator: 248 passed, 115 warnings; 130 profiles inspected, 127 structurally valid, 0 model compatibility issues.
- Focused Biscayne extraction/topology: extraction succeeded; 4 topology tests passed.
- The Vercel PR preview was rate-limited for 24 hours. This did not affect Python tests or the merge, and the PR contained no frontend source changes.

### Remaining operational cleanup

- `integration/main-consolidation` is no longer needed after the merge.
- Several old feature/fix/research branch references remain in GitHub. Their useful changes have been checked against `main`; redundant branches can now be deleted after a final inventory.
- Verify the next scheduled hourly pipeline run from `main` publishes successfully to `data`.

### Architecture decision

Keep exactly two active branch roles:
1. `main`: all maintained application and research source code.
2. `data`: generated publication output only.

No application logic, tests, or workflow source belongs on `data`.


## 2026-11-13 | Add source freshness diagnostics

**Branch:** `main`  
**Starting commit:** `e6d437eb170baf07177e2147c2887d5fdc02ac59`

### Changes

- Added timestamp-age diagnostics for dynamic SST, chlorophyll and satellite-altimetry current inputs.
- Added explicit `fresh`, `delayed`, `stale`, `unknown`, `future` and `unconfigured` states; missing timestamps are not interpreted as fresh.
- Surfaced the current observation timestamp in the quality report.
- Added provisional source-specific warning/stale thresholds in `config/sources.json`; thresholds are operational monitoring policy, not biological cutoffs.
- Degraded pipeline health when dynamic input freshness cannot be established or exceeds configured warning thresholds. Prediction scoring and species weights remain unchanged.
- Propagated freshness metadata to `fish.json` and `api/v1/index.json`.
- Added regression tests for freshness classification and health reporting.
- Updated README and project status to record the new contract and next validation step.

### Validation

- Pending targeted Python tests and production refresh. No NOAA/FWC research extraction workflows are required for this code-only change.

### Next action

Compare source age across multiple scheduled refreshes, then calibrate operational thresholds before introducing any scoring gates.


## 2026-11-13 | Correct chlorophyll freshness summary timestamp fallback

**Branch:** `main`  
**Parent commit:** `536984e0af96ddf0cc0c7a8edd344a2b4050568c`

### Finding

- The first full Python suite after source-freshness diagnostics completed with **250 passed, 1 failed**.
- The failing test was `tests/test_layer_data_quality.py::test_data_quality_reports_loaded_layers_and_gapfilled_usage`.
- Chlorophyll metadata supplied `primary_time`, but no top-level aggregate `time` or `layers.times.chlorophyll`. The summary freshness field therefore reported `unknown` despite a valid primary-scene timestamp.

### Correction

- Use the primary chlorophyll scene timestamp as the summary freshness fallback when an aggregate timestamp is unavailable.
- Keep primary and gap-filled freshness diagnostics separate; do not infer one scene's timestamp from the other.
- No scoring weights, source thresholds, or prediction behavior changed.

### Validation

- The existing regression test covers the fixture that exposed the missing fallback.
- Full-suite rerun is required on this correction commit.

### Next action

- Confirm the Python suite passes, then inspect the next scheduled production export for the freshness fields.


## 2026-11-13 | Add NOAA HF Radar coastal currents with altimetry spatial fallback

**Branch:** `main`  
**Configuration/loader commit:** `a4e7bcf633a84238723dd250df9f5a1e3f87e159`

- Production refresh #202 exposed currents about 1,121 hours old despite a successful pipeline run.
- NOAA ERDDAP metadata confirms `ucsdHfrE2` is the near-real-time hourly 2 km HF Radar product with `water_u`, `water_v`, `hdop`, `number_of_sites`, and `number_of_radials`.
- Configured HF Radar as primary over 24.0-28.5°N, 83.5-78.0°W. Retained `nesdisSSH1day` altimetry as spatial fallback and the Gulf Stream-edge source.
- Current vectors use HF Radar where valid and altimetry elsewhere. Fill values are masked. Source timestamps, valid coverage, blend mode and available quality metrics are recorded independently. Quality metrics are diagnostic only; no unvalidated cutoff was introduced.
- Pipeline health checks both the selected HF Radar freshness and fallback altimetry freshness. Predictions continue when one usable source remains.
- Updated README, Project Status, API attribution/index, tests and roadmap. Species scoring and weights remain unchanged.
- The SoFlo Fish Finder Render page could not be inspected; no assumptions about its implementation were imported.

**Validation:** NOAA metadata confirms dataset dimensions, variable names and units. Mocked tests cover blend/fallback behavior and stale fallback health. Live CSV retrieval and South Florida coverage remain unverified until the next production refresh.

**Next:** inspect the first post-change Pull Ocean Data run. Confirm HFR timestamp, source and aligned valid fractions, quality diagnostics, altimetry timestamp, blend mode, and stream-edge provenance before treating the new feed as production-validated.


### Validation update

- Initial Python run #405 exposed three integration fixtures that still mocked only the previous altimetry request. The test fixtures were updated to return the HF Radar vector and quality fields, and the no-currents fixture now disables both sources.
- Masked the HF Radar product fill sentinel across velocity and diagnostic grids so missing HDOP/site/radial values cannot distort summary statistics.
- Corrected full-suite run #407: **254 passed, 0 failed, 115 warnings**. [Python tests run #407](https://github.com/markeetox/LUPITA/actions/runs/43475604949).
- Added explicit assertions that HF Radar and altimetry observation ages remain separate. The suite result above predates this final additional assertion and health-reporting refinement; a fresh run is required.


- Follow-up run #408 found one regression in the health test: the fallback freshness check was being skipped in a minimal fixture without a separate primary_freshness object. Updated the health check to compare selected and fallback observation status/age directly, avoiding duplicate warnings when the fallback is itself the selected source.
- Run #408: 254 passed, 1 failed. Correction committed separately; next suite run is the acceptance check.


- Final health-comparison correction passed the full Python suite: **255 passed, 0 failed, 115 warnings** on [run #409](https://github.com/markeetox/LUPITA/actions/runs/43476053350). The extra test verifies independent HF Radar and altimetry ages. The remaining acceptance gate is live production retrieval and coverage inspection.


## 2026-11-13 | First live validation of HF Radar and current-source gap

**Production:** [Pull Ocean Data #203](https://github.com/markeetox/LUPITA/actions/runs/43476661499), success, prediction refreshed, zero pipeline errors.

- HF Radar `ucsdHfrE2` loaded with observation time 2026-11-13T10:00:00Z (7.85 hours old).
- Raw valid fraction within the configured South Florida request window: 0.02006 (2.006%).
- Aligned valid fraction over the full 901x1761 North America prediction grid: 0.000123 (0.0123%). This global denominator hides the local footprint; the next code change adds explicit counts/fractions inside the HFR request window.
- HF Radar quality diagnostics: median HDOP 0.51, median 2 contributing sites, median 39 radials.
- Satellite altimetry fallback timestamp: 2026-09-28T00:00:00Z (1,121.85 hours old), stale. Its aligned coverage was 53.4818%, so most available current cells still came from the stale broad-area product.
- Chlorophyll remained delayed at 77.85 hours. SST was fresh at 32.85 hours. Prediction refreshed; health degraded for delayed chlorophyll and stale altimetry fallback.
- `stream.json` correctly labels the Gulf Stream edge as satellite altimetry, but its timestamp is also 2026-09-28 and stale.
- The generated `api/v1/index.json` and `latest.json` contain the source diagnostics. `fish.json` returned an empty response through the GitHub file reader and was not independently verified.

**Decision:** HFR live retrieval works, but current coverage is too sparse to rely on it as the regional current field. Preserve it as a measured coastal observation overlay, not as a claim of broad coverage. Do not let the 53.5% combined coverage statistic conceal the stale source that supplies most of those cells.

**Candidate source research:**
- NOAA Global RTOFS offers daily updated global ocean nowcast/forecast fields, 1/12-degree resolution and forecasts up to eight days, with NetCDF output. It is a promising broad-area model fallback, but ingestion and timestamp/forecast-lead provenance need implementation and validation.
- USF Ocean Circulation Lab's East Florida Coastal Ocean Model (EFCOM) is geographically attractive: East Florida from Jekyll Island to the Florida Keys, daily update, 1-day hindcast and 3.5-day forecast. It nests FVCOM within Global HYCOM with tides. Its public page currently exposes maps/animations and labels the product research-grade; a machine-readable production feed has not yet been identified.
- NOAA/AOML near-real-time geostrophic currents at 0.2 degrees were also checked; the live ERDDAP metadata showed the dataset several days behind, so it is not a strong freshness improvement.
- NOAA HF Radar 1 km and 6 km alternatives have different spatial resolutions and latest observation times; compare their actual South Florida coverage before switching resolutions.

**Next:** add query-region-specific coverage diagnostics, then investigate machine-readable EFCOM and NOAA RTOFS data access. Keep HFR as an observation layer and replace the stale broad-area fallback only after a real production data pull and coverage test. No scoring weights changed.


## 2026-11-13 | Exclude stale satellite altimetry from current-vector fallback

**Branch:** `main`  
**Reason:** Production refresh #203 used satellite altimetry that was 1,121.85 hours old to fill most current-grid cells. A successful data download is not evidence that the vectors still represent current ocean conditions.

### Changes

- Added a fail-closed 72-hour maximum age for satellite-altimetry current-vector fallback. Missing, invalid, future-dated, or older timestamps make the feed ineligible for current-vector filling.
- Retained satellite altimetry for the approximate Gulf Stream-edge calculation, with its timestamp and freshness metadata kept separate.
- HF Radar remains the observation source wherever valid. When altimetry is stale, missing HF Radar cells remain unknown instead of being filled with old velocities.
- Added explicit fallback eligibility/use metadata and ensured pipeline health only treats fallback freshness as a current-layer issue when the fallback was actually used.
- Added regression tests for stale altimetry being excluded both from HF Radar gaps and from a current layer when HF Radar is unavailable.
- Documented NOAA RTOFS as the preferred broad-area model candidate. NOAA retired NOMADS OPeNDAP in February 2026; implementation must use supported HTTPS model-file downloads or GRIB filtering. No unverified endpoint is enabled in production.

### Validation

- The prior regional coverage change passed **255 tests, 0 failures** on [run #410](https://github.com/markeetox/LUPITA/actions/runs/43483859099).
- Full Python suite passed **257 tests, 0 failures, 115 warnings** on [run #415](https://github.com/markeetox/LUPITA/actions/runs/43484934310). The regression tests verify that stale altimetry cannot fill HF Radar gaps or create a current layer on its own.
- No prediction weights or biological scoring rules changed.

### Next

- Inspect the next production refresh to verify stale altimetry is excluded from current vectors.
- Implement and validate the NOAA RTOFS operational HTTPS/GRIB ingestion path, preserving model initialization time and forecast lead separately from observation age.


## 2026-11-13 | Select NOAA S-111 RTOFS East as broad-area current model candidate

### Source assessment

- Identified NOAA's S-111 surface-current product derived from Global RTOFS, with Atlantic output published as `rtofs_east` in the public `noaa-s111-pds` S3 bucket.
- S-111 provides HDF5 tiles in a standard designed for marine navigation. RTOFS East guidance is updated once daily, contains 72 hours of forecast guidance at 6-hour intervals, and is approximately 8.5 km resolution.
- Currents are represented at 4.5 m below the surface, or half the water depth where shallower. This is more relevant to vessel movement than satellite-altimetry geostrophic flow and complements the near-surface HF Radar observation layer.
- NOAA's S-111 README describes the delivery service as preliminary. The bucket's static RTOFS East catalog is intended to be overwritten with each new run, and the tile naming scheme supports downloading only geographic cells of interest.

### Decision

- Prefer NOAA S-111 RTOFS East tiles over downloading full global RTOFS NetCDF files. The tiled HDF5 product should avoid repeatedly transferring very large global files and already expresses current guidance in a vessel-oriented standard.
- Do not enable it yet. First verify current catalog contents, identify the tile(s) covering South Florida, inspect actual HDF5 structure/variables/time groups, and compare forecast values against HF Radar and available local observations.
- Keep the 72-hour altimetry age guard active. Stale altimetry remains excluded from current vectors; its separate Gulf Stream-edge role remains visible.
- If S-111 tile coverage or availability is inadequate, use NOAA's supported RTOFS HTTPS/GRIB output as the alternate ingestion path.

**Sources:** NOAA S-111 AWS README; NOAA Office of Coast Survey developer documentation; NOAA RTOFS Open Data registry.


## 2026-11-13 | Diagnose production refresh #204 and add SST failover

- Run [#204](https://github.com/markeetox/LUPITA/actions/runs/43486365838) passed 257 tests but failed its final health gate because NOAA CoastWatch ERDDAP returned HTTP 503 for required `jplMURSST41` SST after four attempts.
- HF Radar was not tested in that run: `load_layers` exits immediately after SST failure, before downstream gridded requests. The missing currents timestamp was therefore not a separate HF Radar error.
- Add NOAA's `upwell.pfeg.noaa.gov/erddap` host as a fallback for the same MUR dataset. Keep CoastWatch primary and do not substitute another SST product.
- Mark downstream layers `not_attempted` and freshness `not_assessed` when SST prevents their requests.
- Add publication preparation to restore last-known-good prediction/API files after failed refreshes and publish current diagnostics at `api/v1/refresh.json`, with snapshot timestamp in `latest.json`.
- Focused/full validation and live production confirmation remain pending. No prediction weights or biology rules changed.


### Validation completed
- The first full-suite run caught one regression: `build_data_quality(None, ...)` without an SST error must continue to mean `unavailable`, not `not_attempted`. The guard now requires an explicit `layers sst:` error before downstream layers receive `not_attempted`.
- Corrected Python suite: **262 passed, 0 failed, 115 warnings** on [run #43493987730](https://github.com/markeetox/LUPITA/actions/runs/43493987730), commit `735f888b02ab3ddb8065277c4758e00097778ce6`.
- Next validation: manually dispatch Pull Ocean Data and inspect SST source selected, timestamp, `api/v1/refresh.json`, `latest.json` snapshot metadata, and last-known-good prediction timestamps.


### Final code validation and source provenance
- Added `source_endpoint` to SST diagnostics and verified the fallback loader records the actual selected host.
- Latest full Python suite: **262 passed, 0 failed, 115 warnings** on [run #43494256052](https://github.com/markeetox/LUPITA/actions/runs/43494256052), commit `5da0dc56470975216e032b98b0f230a586d8102c`.
- Live Pull Ocean Data verification remains outstanding. Inspect `latest.json` for `sst.source_endpoint` and `data_quality.layers.sst.source_endpoint`, and `api/v1/refresh.json` for refresh health and the prediction snapshot timestamp.


## 2026-11-14 | South Florida species profile accuracy batch 1

**Branch:** `main`  
**Scope:** static species JSON only; no NOAA ingestion, workflow, prediction-weight, scoring, or publication changes.

### Species records updated
- `data/species/black-grouper.json`: replaced generic profile text with NOAA Fisheries life history, diet, habitat and depth context. Replaced placeholder regulation text with current FWC Atlantic/Monroe rules, including the 24-inch total-length minimum, combined gag/black daily and vessel limits, May 1-December 31 season, and for-hire captain/crew restriction. Added explicit Biscayne National Park caveat.
- `data/species/great-barracuda.json`: replaced generic profile and unsupported spawning/migration claims with FWC-documented appearance-independent biology, habitat and diet. Added the South Florida county slot and bag limits. Retained the existing SST numeric bounds and scoring configuration but downgraded their evidence status to provisional because no traceable species-specific thermal-preference source was present.
- `data/species/mangrove-snapper.json`: added FWC-supported size, habitat, diet and June-August spawning information. Added separate Atlantic state and federal size/bag limits and the Biscayne National Park caveat.
- `data/species/yellowtail-snapper.json`: refreshed the profile against FWC/NOAA/South Atlantic Council sources and replaced generic regulations with the 12-inch total-length minimum, 10-fish snapper aggregate limit and year-round season, with the Biscayne National Park caveat.

### Evidence and interpretation rules
- Regulatory summaries are region-specific. Atlantic state waters, federal waters, Gulf waters, Monroe County and Biscayne National Park are not interchangeable.
- Profile source URLs point to FWC, NOAA Fisheries, NPS or regional fisheries science sources. Angler guidance is not promoted to scientific fact.
- Legacy scoring weights, active flags, factor ranges and prediction logic were not changed. The barracuda SST evidence label was changed to `provisional`; its numeric bounds and scoring weight remain untouched.
- Species JSON updates were committed individually: initial commits: `8a2021914ae84bc104416d689de74eb3e79e9071`, `646fe74762ebceda4efad8faaddea0789e50814b`, `428ecd69232e1446941c3211f225159e96d4a281`, `55df25cce8afb503c8fe144a682d80bc519c3868`; final regulation-date metadata corrections: `d8505620b8ecc3b38a75baff228ec0d1b58c1235`, `902afe9e1f007a9401d01951f0ee54a3a34f87db`, `479f8bbe3ac6ea883d6310a58aea3773a3efe206`, `8edaea60a6ecb150490ec423160ecaf7126617ce`.

### Validation
- Each changed record was parsed as JSON before its update was committed; the four committed files were then fetched again and parsed for a post-commit integrity check.
- The repository's `scripts/validate_species.py` audit and Python test suite have **not** been run in this batch. No workflow was dispatched.
- No NOAA endpoint was contacted or tested as part of this species-data work.

### Next action
Continue the audit with additional South Florida species, prioritizing profiles with generic regulation placeholders or unsupported biological claims. Keep park-specific rules explicit and leave prediction scoring unchanged until evidence is independently reviewed.


## 2026-11-14 | South Florida species profile accuracy batch 2

**Branch:** `main`  
**Scope:** six static species JSON records only. No NOAA ingestion, workflow, prediction weights, scoring logic, or data-branch publication changes.

### Species records completed
- `data/species/snook.json`: refreshed size, diet, estuarine habitat, ontogenetic sex change, spawning ecology and overwintering movement using FWC biology/research. Replaced generic harvest notes with Southeast Management Region limits: 28-32 in total length, one per person, closed Dec. 15-Jan. 31 and June 1-Aug. 31. Explicitly separated Southwest-region dates and Biscayne National Park caveats.
- `data/species/tarpon.json`: corrected statewide spawning window to May-September and separated that from the South Florida/Keys seasonal adult concentration. Added FWC size, habitat, diet and migration context. Replaced vague regulations with Florida catch-and-release rules, the narrow state/world-record tag exception, 40-inch in-water handling rule and gear restrictions.
- `data/species/permit.json`: completed size, benthic diet, flats/reef habitat use and maturity/life-history context using Florida Museum and FWC. Added the South Florida Special Permit Zone limits: 22 in fork length, one per harvester, two per vessel, closed April 1-July 31. Documented the distinct general statewide limits and exact zone caveats.
- `data/species/bonefish.json`: completed FWC-supported size, flats habitat, prey, schooling and spawning information. Added Florida catch-and-release-only regulations and handling/temporary-possession constraints. Bahamas telemetry findings remain explicitly non-transferable without South Florida validation.
- `data/species/hogfish.json`: replaced generic profile with FWC life history, ontogenetic habitat shift, benthic feeding and protogynous sex change. Added Atlantic waters south of Cape Sable rules, including the Florida Keys: 16 in fork length, one per harvester, May 1-Oct. 31 season. Marked unsupported legacy SST and depth scoring ranges provisional without changing numeric values or weights.
- `data/species/mutton-snapper.json`: corrected maximum size and spawning summary using FWC; added documented Florida Keys spawning aggregation context and its spatial caveats. Corrected current harvest rule to 18 in total length and five per person within the 10-snapper aggregate. Documented Western Dry Rocks closure (April 1-July 31). Legacy SST and depth scoring bands remain unchanged but are marked provisional.

### Evidence standards applied
- FWC recreational rules were checked as displayed on 2026-11-14. Regulation fields now use `verified_date`; this is the verification date, not a claim that every rule became effective on that date.
- South Florida-specific management areas are kept distinct: snook management regions, the Permit Special Permit Zone, Atlantic hogfish waters south of Cape Sable, Biscayne National Park and Florida Keys protected/closed areas.
- Tarpon and bonefish are documented as catch-and-release fisheries, not generic year-round harvest species.
- Mutton snapper spawning aggregations are spatially discrete. A generic reef map cell is not evidence that an aggregation is present.
- Unsupported legacy numeric SST/depth preferences for hogfish and mutton snapper are labelled provisional. Existing scoring values, active flags, weights and model logic were not changed. Permit and bonefish pilot scoring values likewise remain unchanged and provisional.
- Sources are recorded in each profile. Primary agency and research sources take priority; angler guidance is not promoted to scientific fact.

### Source references
- FWC snook biology and regulations: https://myfwc.com/wildlifehabitats/profiles/saltwater/snook/snook/ ; https://myfwc.com/research/saltwater/fish/snook/sketch-common-snook/ ; https://myfwc.com/fishing/saltwater/recreational/snook/
- FWC and Florida Museum tarpon biology/regulations: https://myfwc.com/wildlifehabitats/profiles/saltwater/tarpon/tarpon/ ; https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/tarpon/ ; https://myfwc.com/fishing/saltwater/recreational/tarpon/
- Permit biology and SPZ: https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/permit/ ; https://myfwc.com/research/saltwater/fish/permit/fishery/ ; https://myfwc.com/fishing/saltwater/recreational/permit/
- Bonefish biology and catch-and-release rules: https://myfwc.com/wildlifehabitats/profiles/saltwater/bonefish/ ; https://myfwc.com/fishing/saltwater/recreational/bonefish/
- Hogfish biology/research and Atlantic rules: https://myfwc.com/wildlifehabitats/profiles/saltwater/hogfish/ ; https://myfwc.com/research/saltwater/hogfish/ ; https://myfwc.com/fishing/saltwater/recreational/hogfish/
- Mutton snapper biology, harvest limits and spawning-site protection: https://myfwc.com/wildlifehabitats/profiles/saltwater/snapper/mutton-snapper/ ; https://myfwc.com/fishing/saltwater/recreational/snappers/ ; https://myfwc.com/research/saltwater/wdr/ ; https://www.sciencedirect.com/science/article/abs/pii/S0165783618300560

### Commits
- Snook: `8a752d8fe83978a0b1c210d40eab4cb6aa47aecc`
- Tarpon: `1a55a94d3af6eff9bb88ce7c94559d9066ddef10`
- Permit: `44e9e0eebd503087e054365ed72d0eebe8eeeb15`
- Bonefish: `8c157e82db749405a282f72f5a044746bc102770`
- Hogfish: `10b4d8cf2802b9873f6302435aa59dd021625f16`
- Mutton snapper: `46152ec2c5750c8b9fa6a3c85d1eaa45801ee530`

### Validation and next action
- Each changed file was parsed as JSON before update and fetched/parsed again after commit. The six records retain their existing factor arrays and prediction model configuration; no active scoring weight or threshold was intentionally modified.
- The dedicated species audit and Python test suite have not been run for this JSON-only batch. No Actions workflow was dispatched and no NOAA endpoint was contacted.
- These six species are now marked reviewed in the catalog. Do not repeat this batch in future work; continue with unreviewed South Florida species, keeping a per-species record here and in `docs/PROJECT_STATUS.md`.


## 2026-11-14 | Full species catalog and scoring audit

**Branch:** `main`  
**Scope:** read-only inspection of all 130 `data/species/*.json` profiles, the parameter registry, species validator, grid scorer, site scorer, and prediction confidence logic.

### Results
- Fetched and parsed all 130 species profiles: 105 grid models and 25 site models.
- Static cross-check found no missing core identity/model fields, duplicate factor parameters within a profile, unregistered parameters, unsupported active parameter/kind combinations, or active weight overflow.
- Default minimum coverage is 0.70; mahi-mahi is the only observed explicit override at 0.60.
- Twelve profiles contain 33 active factors marked provisional, estimated, or unsourced. Eight active factors have no source references across six profiles.
- Twenty-three of 25 site models currently have only one active factor (SST). Snook and tarpon are the two five-factor site models. These single-factor scores are normalized over SST alone and are temperature-screening outputs, not multi-factor habitat assessments.
- Confidence output does not directly account for active factor evidence status. High environmental coverage can coexist with provisional biological inputs without those inputs lowering confidence.
- Grid and site engines differ in how they interpret missing `required` and `gate` factors. Both skip optional missing inputs and enforce minimum coverage, but their gate/required contracts are not identical.
- The existing validator does not yet validate coverage bounds, full category-map shape/registry alignment, or evidence-aware confidence behavior.

### Validation limits and boundary
- This was a static GitHub file inspection and cross-check. `python scripts/validate_species.py` and the Python test suite were not executed because no local checkout was available in this session.
- No NOAA endpoint was contacted, no Pull Ocean Data workflow was run, and no prediction weights, thresholds, factor activation flags, or scoring behavior were changed.

### Audit report
- Full findings and prioritized recommendations: [Species Catalog Audit](SPECIES_CATALOG_AUDIT_2026-11-14.md).

### Next action
Extend the validator and tests for coverage bounds, category maps, evidence diagnostics, and required/gate semantics. Agree on evidence-aware confidence policy before changing prediction output. Then label and prioritize the 23 temperature-only site pilots for evidence-backed expansion. NOAA ingestion work remains paused pending explicit clearance.


## 2026-11-14 | Species validator and evidence diagnostics

### Implementation
- Extended `pipeline/species_validator.py` with minimum-coverage bounds, category-map validation, boolean factor-flag validation, and explicit warnings for ineffective/ambiguous `required` and `gate` combinations across grid and site models.
- Added active evidence-weight accounting. The audit now distinguishes fully sourced, partly sourced, provisional, estimated, unsourced, and incomplete metadata; uncertain weight is not double-counted when both evidence status and source references are missing.
- Added `evidence_risk`, `active_uncertain_weight`, `active_partly_sourced_weight`, `active_evidence_status_weight`, `min_coverage`, and `model_scope` fields to species audit results.
- Added catalog-level counts for temperature-only site pilots and profiles with elevated active evidence risk.
- Added ten regression tests covering coverage bounds, category maps, factor flags, engine-specific missing-data contracts, evidence accounting, malformed evidence metadata, inactive incomplete factors, `needs_source` status, and catalog summaries.
- Updated `python-tests.yml` so changes to `data/species/**` and `data/parameters.json` run the full suite and species validator on `main`; JSON/Markdown/CSV audit outputs are uploaded as a workflow artifact.
- Added [proposed species confidence policy](SPECIES_MODEL_CONFIDENCE_POLICY.md). It is a review proposal only; prediction confidence is not changed until approved.

### Profile regression corrections
- Restored the qualified Bahamas research context in the bonefish spawning description while explicitly warning against transferring those findings to South Florida.
- Restored the study-area depth detail and exact March-through-September wording in the Permit profile to satisfy the existing profile regression guard. These are descriptive text changes only; no scoring factors or values changed.

### Validation
- Intermediate CI attempts caught and corrected malformed evidence-status handling, inactive-factor validation severity, and stale bonefish/Permit wording assertions.
- Final full Python suite and species-validator workflow passed: **272 passed, 0 failed, 115 warnings** on [run #43622006765](https://github.com/markeetox/LUPITA/actions/runs/43622006765). The validator parsed all 130 profiles, marked all 130 structurally valid, and reported 0 active model compatibility issues and 0 validator errors.
- Executed species audit: **130 profiles parsed, 130 structurally valid, 0 active model compatibility issues, 0 validator errors**. It reports 23 temperature-only site pilots, 27 other one-factor models, 80 multi-factor models, and 12 profiles with elevated active evidence risk. Audit artifact was uploaded by CI.
- No NOAA endpoint was contacted and no Pull Ocean Data workflow was run. No prediction scoring or confidence output was changed.


## 2026-11-14 | Review of eight active factor evidence gaps

Reviewed the eight active factors that had no factor-level source references across six species: blackfin tuna (3), bonefish (1), hogfish (1), mutton snapper (1), Permit (1), and tarpon (1).

- Added source references and explicit evidence limitations to all eight factors.
- Blackfin references support warm-water distribution and broad plankton/upwelling associations, but do not validate the configured SST-gradient, chlorophyll-gradient, or Gulf Stream distance relationships.
- Bonefish thermal physiology studies provide performance optima around 26.7–28.0 °C in Bahamas adults, but do not validate the existing South Florida screening band.
- Hogfish sources describe distribution/habitat but no species-specific thermal preference band was identified in this review.
- Mutton snapper telemetry found no evidence of selection for specific temperature ranges in the St. Thomas study population; this is negative evidence, not support for the existing SST range.
- Permit FishBase preferred-temperature output is model-derived (23.2–28.0 °C based on 624 cells), not a controlled thermal-preference experiment.
- Tarpon diel evidence is from four juvenile fish in St. Thomas; it does not establish adult feeding-time preference in South Florida.

All eight factors remain marked `provisional`. No numeric ranges, ideal ranges, weights, active flags, gate/required flags, or scoring logic changed. Explanatory text was made more explicit about uncertainty.

Full review: [Active Factor Evidence Review](ACTIVE_FACTOR_EVIDENCE_REVIEW_2026-11-14.md).

All six JSON profiles parsed after update and all eight previously source-missing active factors now have source references. Final full-suite and species-audit CI is pending for the profile batch: [latest run #43622375109](https://github.com/markeetox/LUPITA/actions/runs/43622375109).


## 2026-11-14 | Align grid category-map scoring with validator contract

**Branch:** `main`  
**Commits:** `8cabaa7c9dab8034388980fd096d471cb6aff21a` (scorer); `e0c0512643b68ed703d22d914a9d4ab34fcc58a5` (tests)

### Finding
- The species validator accepts a non-empty category `map` as a complete scoring definition without requiring a redundant `preferred` list.
- The site scorer already evaluates map-only category factors.
- The grid scorer previously returned no score when `preferred` was absent, even when a valid `map` was supplied. This contradicted the validator contract and site scorer behavior.

### Correction
- Grid category scoring now uses an explicit map directly; categories absent from the map score 0, and missing grid values remain NaN.
- Preferred-list-only category factors retain their existing behavior.
- Added regression tests for map-only factors and preferred-list factors.
- No species profile, active factor, weight, biological range, or current prediction output was intentionally changed. Existing profiles were not edited.

### Validation
- The commits trigger the `Python tests` workflow on push to `main`.
- Full-suite and species-audit result: **pending verification**. Do not treat this fix as CI-validated until the run completes.

### Boundaries
- No NOAA endpoints or ingestion workflows were contacted or run.
- The proposed evidence-aware confidence policy remains inactive.


## 2026-11-15 | Named-site model triage and source-reference validator hardening

**Branch:** `main`  
**Scope:** static review of all 25 named-site species profiles, `pipeline/sites.py`, and evidence-reference handling.  
**Full review:** [Named-site model triage](SITE_MODEL_TRIAGE_2026-11-15.md).

### Findings
- 23 of 25 site models have only one active factor: SST.
- Three South Florida pilots (bonefish, great barracuda, Permit) have explicitly provisional SST bands.
- Twenty other temperature-only profiles mark SST as sourced but cite only the generic NOAA Fisheries homepage. This is not a traceable species-specific evidence reference.
- Snook and tarpon are the only five-factor site models. Their structure maps score only `inlet` positively even though their site-kind lists also include cuts, channel bridges, and flats; this needs explicit design review.
- `distance_to_inlet_value` currently returns constant 0.0 for every site. It is a placeholder, not a measured distance.

### Validator changes
- Generic homepage-only URLs now produce `generic_source_reference` warnings and do not count as specific source metadata for active evidence accounting.
- Homepage query strings/fragments do not make a generic homepage specific.
- Active `distance_to_inlet` site factors produce a `placeholder_site_factor` error, mark the model incompatible, and count as uncertain active weight.
- Regression tests cover these behaviors.

### Commits
- `2de3ceb`: detect homepage-only source references.
- `1b805ef`, `37e4eb5`: source-reference regression tests.
- `3578e27`: ensure query-string homepages remain generic.
- `229f021`, `582c3ea`: flag constant-distance placeholder and test it.
- `d68a393`, `93cb030`: reject active use of the constant-distance placeholder and assert the model is incompatible.
- `1eec34e`, `da84cab`, `f8ae658`: warn when active site structure categories cannot be returned by the site's allowed kinds or allowed kinds fall through to zero.
- `dac1ddd`, `ee25d79`: make the new structure check resilient to malformed preferred-category values and add a regression test.
- `fc64cf6`: add named-site triage report.

### Validation
The automatic Python workflow should run for the validator and test commits. Full suite and updated 130-profile audit results remain pending verification. Do not treat the new checks as CI-validated until the run is inspected.

### Boundaries
No NOAA endpoints, data workflows, production refreshes, species values, factor weights, active flags, gates, or prediction confidence were changed.


## 2026-11-15 | Production refresh #211 confirms pipeline recovery

**Workflow:** [Pull Ocean Data #211](https://github.com/markeetox/LUPITA/actions/runs/43664658831)  
**Run ID:** `43664658831`  
**Branch / commit:** `main` / `16ae66cd6247ce8eb30b05770f16f605423cc16c`  
**Event:** scheduled  
**Result:** workflow and publication succeeded; pipeline health is `degraded`, not `healthy`.

### Execution and publication
- All workflow steps completed successfully, including the full `python -m pytest -q` suite, catalog generation, `pipeline.run`, publication preparation, data-branch publish, and the final health evaluation.
- The generated `latest.json` was published to the `data` branch at `2026-11-15T01:47:27Z`; the data branch head advanced to `3cdc4ea26817eff5e321868f7c66190aab625b11`.
- Predictions refreshed from the current run; `errors=[]` and `critical_issues=[]`.

### Observed layer health
- SST: loaded from CoastWatch `jplMURSST41`, observation time `2026-11-13T09:00Z`, 40.79 hours old at load; classified delayed against the provisional 36h warning / 72h stale thresholds.
- Chlorophyll: loaded from NOAA-20 `nesdisVHNnoaa20chlaDaily`, observation time `2026-11-12T12:00Z`, 61.79 hours old; classified fresh against the provisional 72h / 120h thresholds. Valid source fraction was 15.8%; cloud/data gaps remain material.
- HF Radar: loaded from `ucsdHfrE2`, observation time `2026-11-14T20:00Z`, 5.79 hours old; classified fresh. However, only 94 of 10,101 cells in the configured South Florida query window were valid (0.9306%). This is a major coverage limitation despite successful retrieval.
- Altimetry fallback `nesdisSSH1day` was 1,153.8 hours old, exceeded the 72h current-use limit, and was correctly excluded from current vectors. HF Radar remained the selected current source.
- ETOPO bathymetry, reef structure, FWC benthic habitat, closures, and buoy observations were loaded. The snapshot contains 4,548 artificial reef records, 25,362 natural reef polygons, 49,903 habitat features, and 199 closure areas.

### Health interpretation
- `pipeline_health.status=degraded` solely reports the SST delayed freshness issue; there are no critical issues, optional-layer issues, or recorded errors.
- `prediction_refreshed=true`; `prediction_snapshot.status=refreshed` and source is `current_refresh`.
- A successful workflow is not proof of complete or uniformly high-quality coverage. In particular, HFR coverage is sparse and chlorophyll coverage is limited.
- This is the first inspected successful scheduled production refresh after the NOAA service interruption. It confirms the actual ingestion/publication path works again, while retaining the source-quality caveats above.

### Boundary and next actions
- This run was scheduled, not manually dispatched. No additional ingestion run was triggered for this review.
- No code, configuration, species biology, scoring weights, or prediction logic changed as part of this inspection.
- Continue monitoring subsequent scheduled refreshes. Compare SST latency and HFR query-window valid coverage across runs before declaring sustained recovery or adjusting any source/quality policy.


## 2026-11-15 | HF Radar coverage diagnosis and CI verification

**Scope:** read-only source/configuration inspection. No NOAA ingestion workflow was started; no code, source configuration, prediction logic, biology, or scoring weights were changed.

### Code validation
- Python Actions run [#462](https://github.com/markeetox/LUPITA/actions/runs/43669158015), commit `ee25d79c163323f5fa17b35471a147730e22a7ff`, completed successfully. This run includes the latest species-validator hardening and its tests.
- The Vercel status is separate from Python CI and is not used as evidence of Python test success.

### HF Radar findings from production refresh #211
- Published `latest.json` reports NOAA/NESDIS HF Radar `ucsdHfrE2` loaded at `2026-11-14T20:00:00Z`, with freshness age 5.79 hours.
- The configured request window is 24.0-28.5°N, 83.5-78.0°W. It contains 10,101 cells on LUPITA's target grid; 94 had valid aligned HF Radar vectors (0.9306%).
- The fetched HFR source grid was 251 x 285 with 0.9059% valid vector cells. The aligned valid fraction over the entire North America grid was 0.0059%; this whole-grid denominator must not be confused with local query-window coverage.
- Source and aligned valid fractions are close (0.9059% vs 0.9306% within the regional window), so the observed sparsity is not currently pointing to a major resampling-loss bug. The main limitation appears to originate in the valid spatial footprint of the upstream HFR field for this broad request window.
- NOAA metadata identifies `ucsdHfrE2` as an hourly 2 km HFR product assembled from available coastal radar radial measurements. Its global bounding rectangle is not a promise of continuous ocean coverage. NOAA IOOS explains that HFR coverage is coastal and spatially variable; its coverage maps distinguish occasional availability from typical coverage.
- A NOAA 6 km hourly product, `ucsdHfrE6`, is publicly exposed with the same broad East/Gulf Coast network footprint and coarser grid. Its existence makes it a valid comparison candidate, not evidence that it will improve South Florida coverage. No product switch or source request was made.

### Fallback and safety behavior
- Satellite altimetry `nesdisSSH1day` had 76% valid cells in the same query window but was 1,153.8 hours old, beyond the configured 72-hour current-use limit. The pipeline correctly excluded it from current-vector filling.
- Keep stale altimetry excluded. Its broader footprint must not be used to disguise missing current observations.

### Next checks
1. Compare NOAA 1 km, 2 km, and 6 km HFR products over the identical South Florida region and same observation times, recording valid vector coverage and quality diagnostics.
2. Separate nearshore HFR coverage from offshore gaps; do not treat the full bounding rectangle as an expected continuous coverage area.
3. Evaluate a timestamped broad-area model-current source separately from observed HFR vectors. NOAA RTOFS remains a candidate already documented in the roadmap.
4. Keep all source changes, data pulls, scoring gates, biology, and prediction weights unchanged until evidence is reviewed.

**Sources:** [NOAA 2 km HFR dataset](https://upwell.pfeg.noaa.gov/erddap/griddap/ucsdHfrE2.html); [NOAA 6 km HFR dataset](https://coastwatch.pfeg.noaa.gov/erddap/griddap/ucsdHfrE6.html); [NOAA IOOS HF Radar coverage and program notes](https://ioos.noaa.gov/project/hf-radar/).


## 2026-11-15 | NOAA HF Radar resolution comparison: metadata reconnaissance

**Status:** metadata comparison completed; same-time spatial coverage comparison remains incomplete. Read-only public catalog inspection only. No raw data was ingested, no Pull Ocean Data workflow was started, and no source/configuration/code/prediction changes were made.

### Product metadata
NOAA CoastWatch ERDDAP currently lists three East Coast/Gulf of Mexico hourly HF Radar products:
- 1 km: `ucsdHfrE1`, nominal grid spacing 0.00899° latitude / 0.0096792° longitude; latest catalog observation reported as 2026-11-13 10:00 UTC.
- 2 km: `ucsdHfrE2`, nominal grid spacing 0.01798° / 0.0193584°; latest catalog observation reported as 2026-11-13 04:00 UTC.
- 6 km: `ucsdHfrE6`, nominal grid spacing 0.05394° / 0.0580752°; latest catalog observation reported as 2026-11-14 05:00 UTC.

The metadata snapshots therefore show different update times. The 6 km product is newest in this snapshot, but that does not establish better South Florida spatial coverage. The three products have a common historical time range, so a fair test should request one exact common timestamp and the identical 24.0-28.5°N, 83.5-78.0°W region, then compare valid paired u/v vectors, source-grid coverage, and quality fields. Do not compare different timestamps or infer better coverage from nominal grid spacing.

### Important comparison caveat
- NOAA describes these products as near-real-time coastal radar surface-current solutions assembled from available radar radial measurements. The 1 km, 2 km and 6 km products represent different grid resolutions and nominal surface depths (about 0.5 m, 1.0 m and 2.4 m respectively); they are not interchangeable measurements at identical depth.
- Metadata pages and time-coverage fields were accessible, but this inspection environment could not retrieve the bounded griddap vector subsets needed to calculate same-time South Florida valid-cell fractions. Therefore no 1 km vs 2 km vs 6 km coverage ranking is claimed.
- NOAA's metadata also shows source radial-file lists differ between product snapshots. That is another reason to compare exact common timestamps and inspect the contributing station/radial diagnostics rather than assume the grids are identical apart from resolution.

### Next action
Obtain the same-time bounded `water_u`, `water_v`, `hdop`, `number_of_sites`, and `number_of_radials` subsets for all three datasets, calculate paired-vector valid fractions inside the same South Florida window, and inspect where valid cells cluster. Only then recommend a source or resolution change. Keep current production configuration unchanged.

**NOAA references:** [1 km dataset](https://coastwatch.pfeg.noaa.gov/erddap/griddap/ucsdHfrE1.html), [2 km dataset](https://coastwatch.pfeg.noaa.gov/erddap/griddap/ucsdHfrE2.html), [6 km dataset](https://coastwatch.pfeg.noaa.gov/erddap/griddap/ucsdHfrE6.html), [griddap request documentation](https://coastwatch.pfeg.noaa.gov/erddap/griddap/documentation.html).


## 2026-11-15 | Implement standalone HF Radar product comparison

**Implementation:** added scripts/compare_hfr_products.py, tests/test_hfr_product_comparison.py, and manual-only workflow .github/workflows/hfr-product-comparison.yml.

- Requests NOAA CoastWatch HF Radar products ucsdHfrE1 (1 km), ucsdHfrE2 (2 km), and ucsdHfrE6 (6 km) over the identical 24.0–28.5°N, 83.5–78.0°W window.
- Uses a single exact timestamp, defaulting to 2026-11-13T04:00:00Z. The parser rejects returned timestamps that differ from the requested time; no nearest-time substitution is permitted.
- Measures valid vectors only when both eastward water_u and northward water_v are finite and not known fill values. Reports each native grid's cell denominator and actual returned coordinate-pair count.
- Reports median HDOP, number of contributing sites, number of radials, diagnostic-field availability, 0.5-degree occupied-tile distribution, and approximate Florida Keys, Biscayne Bay, and offshore subregion coverage.
- Preserves each product's nominal grid spacing and representative depth metadata. No regridding is performed because the products differ in both resolution and represented surface depth.
- CoastWatch is tried first, with the documented Upwell ERDDAP host as fallback. Each product is handled independently so one unavailable product does not erase successful results.
- The manual workflow has read-only repository permissions and uploads JSON/Markdown output as a 30-day artifact. It does not invoke Pull Ocean Data, alter config/sources.json, or publish to data.
- README, Project Status, and Roadmap were updated with the run instructions and acceptance criteria.

**Validation:** Python CI [run #43725728118](https://github.com/markeetox/LUPITA/actions/runs/43725728118) passed on code/test commit 3112bbb2a830960e1d032e9f2f57ab4463addae1. The NOAA comparison itself has not yet run, so no numerical ranking or source recommendation is claimed. Production source selection, data ingestion, species biology, prediction weights, and scoring behavior remain unchanged.

**Next:** run Actions → Compare NOAA HF Radar products using the default exact timestamp. Review all three products' retrieval status, native-grid coverage, quality diagnostics, and subregion distribution before proposing any production change.

## 2026-11-15 | First same-time NOAA HF Radar comparison completed

Manual diagnostic workflow [#43727859776](https://github.com/markeetox/LUPITA/actions/runs/43727859776) completed successfully for exact timestamp 2026-11-13T04:00:00Z. The [JSON/Markdown artifact](https://github.com/markeetox/LUPITA/actions/runs/43727859776/artifacts/14166714348) was retrieved and reviewed. All three datasets returned the exact timestamp and all requested grid coordinates; no retrieval failures were recorded.

### Results

| Product | Native grid cells | Valid paired u/v | Native-grid valid fraction | Median HDOP | Median sites | Median radials |
|---|---:|---:|---:|---:|---:|---:|
| 1 km (`ucsdHfrE1`) | 285,069 | 0 | 0.000% | n/a | n/a | n/a |
| 2 km (`ucsdHfrE2`) | 71,535 | 1,640 | 2.293% | 0.56 | 2 | 35 |
| 6 km (`ucsdHfrE6`) | 7,980 | 753 | 9.436% | 0.30 | 2 | 100 |

Approximate subregion results:

| Product | Florida Keys | Biscayne Bay | Offshore grounds |
|---|---:|---:|---:|
| 1 km | 0.000% | 0.000% | 0.000% |
| 2 km | 0.000% | 10.732% | 5.701% |
| 6 km | 0.337% | 24.554% | 10.811% |

The 6 km product has the strongest apparent spatial availability in this snapshot, especially in Biscayne Bay and the offshore box. Both 2 km and 6 km have very sparse Keys coverage. The 1 km product returned no valid paired vectors anywhere in the requested region at this time; this must be checked at another common timestamp before treating it as a persistent product limitation.

### Interpretation limits and follow-up

- Native-grid valid fractions are descriptive. Their denominators include all coordinate cells in the rectangular request, including cells with no radar coverage; they are not direct ocean-area coverage estimates.
- Products have different nominal depths (about 0.5 m, 1.0 m, 2.4 m for 1/2/6 km). They are not interchangeable vertical observations.
- Median HDOP/site/radial values are descriptive only. No new quality thresholds have been adopted.
- The first artifact's half-degree tile denominator varied with native coordinate edges. Fixed-region binning was corrected in commit `0ad8726`, with a regression test in `57fe6d7`. The first artifact predates this correction; rerun the manual diagnostic before using tile-occupancy comparisons.
- Next: rerun after the fixed-bin correction, and perform a second exact-common-time comparison to check whether the 1 km zero-coverage result is persistent. Consider adding an ocean-only denominator using a shared coastline/mask before making any cross-product area-coverage claim.
- No Pull Ocean Data run, source/configuration change, production data publication, biology edit, or prediction-weight change was made.

**Artifact:** `hfr-comparison-20261113T040000Z.json` and `.md`, GitHub Actions artifact ID `14166714348`.


## 2026-11-15 | Corrected HF Radar product comparison

- User reran the manual read-only comparison after the shared geographic-bin correction.
- Workflow [#43731442828](https://github.com/markeetox/LUPITA/actions/runs/43731442828) completed successfully on main; artifact [14168636243](https://github.com/markeetox/LUPITA/actions/runs/43731442828/artifacts/14168636243) was downloaded and reviewed.
- Requested and returned timestamp for all three products: `2026-11-13T04:00:00Z`. Region: 24.0-28.5°N, 83.5-78.0°W. Native grids retained; paired finite `water_u` and `water_v` required. No interpolation or regridding.
- 1 km `ucsdHfrE1`: 0/285,069 valid vectors (0.000%); 0/99 shared half-degree tiles.
- 2 km `ucsdHfrE2`: 1,640/71,535 (2.293%); 6/99 shared tiles. Median HDOP 0.56; median sites 2; median radials 35.
- 6 km `ucsdHfrE6`: 753/7,980 (9.436%); 19/99 shared tiles. Median HDOP 0.30; median sites 2; median radials 100.
- Approximate subregion coverage: Keys 0/0.337%, Biscayne Bay 0/10.732% vs 6 km 24.554%, offshore 5.701% vs 10.811% (2 km vs 6 km). Keys remain effectively uncovered by both coarser products in this snapshot.
- The corrected half-degree denominator is fixed at 99 geographic bins across all products. This is a broad clustering diagnostic, not continuous coverage or an ocean-only area fraction.
- Interpretation: 6 km has the strongest apparent availability and diagnostic quality in this one snapshot, but the 1 km zero result and 2 km/6 km pattern need a second common timestamp. Different representative depths (0.5/1.0/2.4 m) prevent treating the products as interchangeable.
- Next: perform a second exact common-time comparison; then consider a shared ocean-only mask/coastline denominator. Do not change production source selection, source configuration, scoring, or species biology based on one snapshot.
- Validation of corrected code: Python CI runs [#43730941774](https://github.com/markeetox/LUPITA/actions/runs/43730941774) and [#43730946716](https://github.com/markeetox/LUPITA/actions/runs/43730946716) succeeded before the manual comparison.


## 2026-11-16 | Scheduled production refresh inspection

- Inspected scheduled [Pull Ocean Data #43840037456](https://github.com/markeetox/LUPITA/actions/runs/43840037456), run on main commit `57cb230045be2fddc3f49aa74208907006ddc334`.
- Full test step, catalog generation, prediction pipeline, data publication and health evaluation all completed. Prediction snapshot refreshed at `2026-11-16T09:29:14Z`; health remained degraded with no critical issues.
- SST: `jplMURSST41`, `2026-11-14T09:00Z`, 48.49h old (delayed); aligned valid fraction about 55.2%.
- Chlorophyll: `nesdisVHNnoaa20chlaDaily`, `2026-11-13T12:00Z`, 69.49h old (fresh under provisional 72h warning); source valid fraction 7.94%; gap-filled dataset remains disabled.
- HF Radar `ucsdHfrE2`: failed on the Upwell fallback with HTTP 404, response says the dataset ID is currently unknown. HFR valid cells 0/10,101; no current source selected; freshness unknown.
- Altimetry `nesdisSSH1day` was about 1,185.5h old and correctly excluded from current vectors despite 75.9% aligned valid fraction in the request region. This verifies the stale-current fail-closed guard remains effective.
- Do not infer that NOAA as a whole is down from this response; the inspected evidence identifies the Upwell fallback's dataset lookup failure. Need separately verify CoastWatch response and current dataset catalog availability before diagnosing root cause or changing configuration.
- No production code, source configuration, data, prediction weights, or species biology changed during this inspection.
- The separate HF Radar product comparison still needs a second exact common timestamp. No newer run of the manual comparison workflow was present in the inspected latest 20 workflow runs.


## 2026-11-16 | Second HF Radar timestamp: partial report, 6 km retrieval failure

- User ran the manual comparison for exact requested timestamp `2026-11-12T04:00:00Z`. Workflow [#43893775875](https://github.com/markeetox/LUPITA/actions/runs/43893775875) ended with failure because not all three products were retrieved; JSON and Markdown reports were still written and uploaded by the workflow's unconditional artifact step.
- 1 km `ucsdHfrE1`: 0/285,069 valid paired vectors (0.000%); 0/99 fixed shared half-degree tiles.
- 2 km `ucsdHfrE2`: 1,201/71,535 valid paired vectors (1.679%); 8/99 shared tiles. Median HDOP 0.46, median sites 2, median radials 40.
- 6 km `ucsdHfrE6`: failed with HTTP 404 on both configured host attempts. The Upwell attempt's requests error identifies a CoastWatch final URL, consistent with a redirect; do not treat these as proven independent backend failures.
- The script returns exit code 1 when any product is missing by design. This prevents an incomplete three-product comparison from being marked successful; the artifact remains available for partial-result inspection. No timestamp substitution occurred.
- Compared with the November 13 sample, the 2 km valid fraction decreased from 2.293% to 1.679%; its valid-vector count changed from 1,640 to 1,201. This is descriptive and should not be interpreted as a persistent trend from two snapshots. The 1 km zero-vector result has now repeated at two timestamps. 6 km cannot be compared at the second timestamp.
- Fixed report Markdown generation by removing unnecessary backslashes before backticks (commit `cd3fbf0`) and added a regression test (commit `dd38768`). These are formatting/test-only changes; comparison and failure semantics are unchanged.
- No production source configuration, ingestion, data publication, prediction logic, biology, or weights changed.
- Next: read-only investigation of current NOAA metadata and endpoint behavior for `ucsdHfrE6`; no source promotion or production edits pending evidence and explicit review.


### 2026-11-16 | NOAA metadata explains the 6 km November 12 retrieval failure

- Live read-only [Upwell 6 km dataset metadata](https://upwell.pfeg.noaa.gov/erddap/griddap/ucsdHfrE6.html) confirms `ucsdHfrE6` still exists. Its time-axis `actual_range` converts to 2026-08-10 21:00Z through 2026-11-10 08:00Z; metadata `date_created` is 2026-11-10 09:00Z.
- The failed comparison requested 2026-11-12 04:00Z, which is after the 6 km dataset's published latest time. The 404 is therefore consistent with an out-of-range timestamp, not a missing/removed dataset ID. The earlier interpretation that the two host attempts established an endpoint/dataset outage is superseded by this metadata evidence.
- Upwell's 1 km dataset form currently reports a time-axis end of 2026-11-14 21:00Z. Its 2 km HTML page appears cached/stale relative to the successful November 12 CSV retrieval, so do not use its metadata snapshot to infer current range.
- Candidate next exact common time: `2026-11-10T04:00:00Z`, within the 6 km published range. This remains a candidate until all three bounded CSV requests return that exact time.
- Sources: [Upwell 6 km metadata](https://upwell.pfeg.noaa.gov/erddap/griddap/ucsdHfrE6.html), [Upwell 1 km metadata](https://upwell.pfeg.noaa.gov/erddap/griddap/ucsdHfrE1.html). No production source change or ingestion run was made.


## 2026-11-16 | HF Radar retry, live metadata correction, and deterministic CI fixtures

- User reran the comparison at `2026-11-10T04:00:00Z`. [Run #43894680887](https://github.com/markeetox/LUPITA/actions/runs/43894680887) failed because 6 km `ucsdHfrE6` retrieval returned HTTP 404; artifact `14237663318` was downloaded and reviewed.
- Partial results: 1 km 0/285,069 (0.000%); 2 km 1,614/71,535 (2.256%), 10/99 fixed half-degree tiles, median HDOP 0.60, sites 2, radials 33; 6 km unavailable. No nearest-time substitution occurred.
- **Supersedes prior timestamp-range explanation:** live Upwell metadata now shows 6 km dataset created 2026-11-16 13:42:13Z, time coverage through 2026-11-16 13:00Z, and HFR source cycle at 12:00Z. The November 10 requested timestamp is within the currently published time range. The previous metadata snapshot ending Nov 10 was stale. The 404 therefore remains unexplained by time range alone.
- The Upwell request's final error URL points to CoastWatch, consistent with a redirect, but the previous diagnostic discarded the redirect chain and response body. Updated `fetch_product` to capture redirect statuses/locations, final URL/status, and response body excerpt (commit `87b8f75`); added regression coverage (commit `43360cb`). No endpoint preference or production source was changed.
- CI runs [#43894349535](https://github.com/markeetox/LUPITA/actions/runs/43894349535) and [#43894357067](https://github.com/markeetox/LUPITA/actions/runs/43894357067) both reported 2 failed, 282 passed, 115 warnings. The failures were the current-source tests using a fixed Nov 13 11:00 UTC altimetry fixture; at Nov 16 CI time it was older than the 72-hour use limit, so production code correctly refused to blend/use it. Updated fixture to generate a timestamp one hour before test execution; explicit stale cases remain pinned to Sep 28 (commit `4b9e6b3`). No production logic changed.
- Next: confirm CI passes with deterministic fixtures; rerun the comparison only after the new redirect diagnostics are present, then use response chain/body to isolate the 6 km data access failure. Keep production selection unchanged.


- Follow-up test-fixture correction: one stale-only test still replaced the old literal timestamp after the initial relative-time conversion. Updated it to replace `ALT_TIME` consistently (commit `afb59bc`). Full Python CI [#43897319861](https://github.com/markeetox/LUPITA/actions/runs/43897319861) was still running at last inspection; no passing result is claimed yet.


- Final Python CI [#43897319861](https://github.com/markeetox/LUPITA/actions/runs/43897319861) passed on commit `afb59bc7ae6e23f48b05f3a6c700ff86dbdd5ded`: **286 passed, 0 failed, 115 warnings**. Species profile audit and artifact upload both succeeded. This validates the age-relative fixtures and the new ERDDAP redirect-diagnostic regression test.


## 2026-11-16 | NOAA ERDDAP request blacklist confirmed by comparison artifact

- User reran the read-only comparison at the known-good timestamp `2026-11-13T04:00:00Z`. [Workflow #43935416361](https://github.com/markeetox/LUPITA/actions/runs/43935416361) failed and uploaded [artifact 14258784849](https://github.com/markeetox/LUPITA/actions/runs/43935416361/artifacts/14258784849); the JSON and Markdown reports were downloaded and reviewed.
- This is no longer a 6 km-only 404: all three products (`ucsdHfrE1`, `ucsdHfrE2`, `ucsdHfrE6`) returned HTTP 403 on both CoastWatch and Upwell ERDDAP hosts. NOAA's response body explicitly says the requesting IP is on the ERDDAP request blacklist, with excessive concurrent requests, repeated identical requests, or invalid requests listed as possible causes.
- No product measurements were returned. The previous 2026-11-13 04:00Z comparison results remain historical results from the earlier successful artifact; this latest run does not invalidate them, but it also adds no new evidence.
- Most likely scope is the GitHub-hosted workflow runner egress IP, not an individual HFR product. This is an access restriction, not proof of dataset removal, missing vectors, or bad product coverage.
- Stop repeated manual comparisons from the same runner while the block is active. Do not rotate hosts or issue more identical requests as a workaround. Resume only after access is restored or a low-rate, approved retrieval route is established.
- No production endpoint/configuration, Pull Ocean Data workflow, data branch publication, prediction logic, species biology, scoring, or weights changed. Python CI remains green: [run #43897319861](https://github.com/markeetox/LUPITA/actions/runs/43897319861), 286 passed, 0 failed, 115 warnings.

## 2026-11-16 | Species model-to-data audit

- Completed static review of `config/sources.json`, layer construction, grid/site scoring, derived layers, source handling, validator mappings, and validator tests.
- Added [MODEL_TO_DATA_AUDIT_2026-11-16.md](MODEL_TO_DATA_AUDIT_2026-11-16.md), documenting factor-to-input mappings, availability limits, and missing-data behavior.
- Confirmed grid and site engines have different contracts: grid `required` is not read by the scorer; site `required` makes a missing factor unscorable; site gate without `required` can be skipped when missing. Both engines renormalize over available weights subject to minimum coverage.
- Confirmed grid SST is foundational; chlorophyll, bathymetry, currents, structures and derived factors are conditional; seasonal factors are calendar lookups. Site SST uses buoy/grid fallback, tide uses a station within 120 km, light is astronomical, structure is static site kind, and site `distance_to_inlet` is still constant zero.
- Carried forward the existing 130-profile audit results and 25-site-model findings without claiming a new catalog validator run.
- No NOAA endpoint contacted, no Pull Ocean Data run, no data publication, and no changes to scoring, biology, weights, profile flags, or source configuration.
- Next: add regression tests around runtime missing-data contracts and factor-to-layer dispatch without changing scoring semantics.

## 2026-11-16 | Runtime factor contract tests

- Added `tests/test_model_data_contracts.py` for grid/site missing, required, gate, coverage, and normalization semantics.
- Added `tests/test_factor_data_contracts.py` to cross-check every active profile factor against grid/site dispatch maps, call the actual scoring functions using synthetic values, and verify all declared non-calendar grid inputs are exposed by `load_layers` using fake source responses.
- Corrected the seasonal test boundary: month is added by `build_fish_json` when current conditions are provided, not by the raw layer loader.
- Final test commit `909fad31b635b3a0c65a3256fdfcd7203d526f45` passed CI, species audit, and artifact upload in [run #43941668108](https://github.com/markeetox/LUPITA/actions/runs/43941668108). An earlier successful contract-test run reported 294 passed and 115 warnings; final run conclusion is success.
- No production scoring, biology, weights, source configuration, ingestion, or data publication changed.


## 2026-11-16 | Prediction-level environmental source lineage

- Added `environmental_source` to each active factor diagnostic. The object identifies source kind, whether the input was available at the prediction, mapped layer status, dataset and observation metadata, configured freshness, and relevant coverage information.
- Retained each factor's actual `sources` references as well as `source_count`, so clients can inspect the cited evidence rather than seeing only a count.
- Added a source map covering every active grid and site factor in the species catalog, with a regression test to prevent unmapped active factors.
- Explicitly documented composite-source limits: current fields can blend HF Radar and satellite altimetry without retaining exact per-cell provider attribution; chlorophyll can combine primary and gap-filled products without retaining exact per-cell origin. Both source timelines are reported separately.
- Gulf Stream edge is attributed to satellite altimetry specifically. Static ETOPO/FWC layers are identified as static, not assigned fabricated freshness ages.
- Named-site SST now retains the exact NDBC water-temperature measurement timestamp, not simply the newest buoy row. NDBC freshness is marked unconfigured until an operational threshold is established.
- Named-site tide diagnostics now retain station identity, distance, and predicted event times; retrieval freshness remains explicitly not assessed.
- Added regression coverage for source lineage, layer freshness, altimetry attribution, site catalog metadata, tide prediction metadata, buoy timestamps, and unknown timestamps.
- Final code/test commit `49fb892686be1675325c47b5c593610215b7513b` passed [Python CI #43944587159](https://github.com/markeetox/LUPITA/actions/runs/43944587159): **304 passed, 0 failed, 115 warnings**. Species audit and artifact upload succeeded.
- No score, confidence, biology, weight, source-selection, ingestion, or publication behavior changed.
- Next: build an evidence-quality summary that evaluates biological support separately from environmental freshness and data availability. Do not treat the presence of a URL as proof of support for the exact factor value.


## 2026-11-16 | Per-prediction biological evidence diagnostics

- Added `value_notes` to grid and named-site factor diagnostics so the profile's actual caveats travel with the prediction.
- Added `evidence_diagnostics` per active factor: declared profile status, per-reference classification, reference-quality category, explanatory notes, and a warning that source presence does not establish the exact numeric claim.
- Added `evidence_summary` per recommended spot. It aggregates configured active-factor weight independently by declared evidence status and reference quality. The values are not probabilities or calibrated scientific-quality scores.
- Classification distinguishes declared-sourced-but-unverified, generic-homepage-only, partly sourced, provisional/estimated/unsourced/needs-source, weak factor, missing/invalid references, and unknown statuses.
- API v1 exposes both the per-factor and per-spot evidence diagnostics.
- No profile status or source was automatically upgraded/downgraded. No confidence cap, score, weight, range, active flag, gate, or minimum coverage changed.
- Tests cover generic homepage vs specific reference, sourced-but-unverified vs provisional, partly sourced, missing/invalid evidence metadata, malformed URLs, active weight aggregation, and API v1 serialization.
- Final code/test commit `d46fbcae9cbf9343d0490cb5cf05d08a0cd77dd5` passed [Python CI #43945487955](https://github.com/markeetox/LUPITA/actions/runs/43945487955): **307 passed, 0 failed, 115 warnings**. Species audit and artifact upload succeeded.
- Next: manually review homepage-only source references and elevated-risk profiles against their exact species, life stage, region, and configured numeric claim before changing any evidence status.


## 2026-11-16 | Source-by-source review of 20 named-site SST factors

- Reviewed the 20 named-site profiles previously marked `sourced` while citing only the generic NOAA Fisheries homepage.
- Created `docs/NAMED_SITE_SST_EVIDENCE_REVIEW_2026-11-16.md` with configured range/ideal values, species-specific sources, life-stage and regional caveats, claim-fit assessments, recommended statuses, and a source register.
- Found close support for configured range and ideal interval for Spanish mackerel; partial but incomplete support for 11 profiles; and insufficient numeric support for 8 profiles.
- Key mismatches documented: bottom temperature vs site SST; spawning or juvenile evidence vs year-round adult suitability; broad observed occurrence vs preferred interval; model-derived vs measured evidence; and regional populations not transferable without qualification.
- All 20 profiles are single-factor SST models with `gate: true` and `required: true`; SST determines site eligibility.
- No profile or prediction behavior was changed. Status and reference updates await owner approval.
- Next: apply only the accepted evidence-status, source-reference, and explanatory-note changes. Keep all numeric ranges, ideal bands, weights, gates, and required flags unchanged in that pass.


## Owner-approved named-site SST evidence metadata update | 2026-11-16

Applied the source-by-source review to all 20 named-site SST profiles. Replaced generic NOAA homepage references in each profile-level and active `sst_c` source list with species-specific references, assigned conservative evidence statuses, and rewrote factor `value_notes` to state exactly what the evidence supports and where it does not transfer. Final classification: 1 sourced, 11 partly sourced, 5 provisional, 3 needs-source. No numeric values, model structure, weights, gates, required flags, timing, scoring, confidence behavior, ingestion, or data publication changed. See [review report](NAMED_SITE_SST_EVIDENCE_REVIEW_2026-11-16.md).


## Follow-up review of spot, weakfish, and white grunt | 2026-11-16

Found species-specific evidence for all three previously needs-source named-site SST profiles and applied conservative metadata updates. All three are now `partly_sourced`, not `sourced`: spot has Mississippi bottom-temperature/catch evidence but conflicting South Florida distribution references; weakfish has ASMFC occurrence/migration evidence but southern Florida hybridization/identity concerns; white grunt has adult occurrence temperatures and a FishBase model-derived preferred-temperature estimate. Updated overall 20-profile totals: 1 sourced, 14 partly sourced, 5 provisional, 0 needs-source. Numeric settings and all prediction behavior remain unchanged. Details and references: [evidence review](NAMED_SITE_SST_EVIDENCE_REVIEW_2026-11-16.md).


## 2026-11-17 | Master evidence inventory for all 130 species profiles

- Retrieved and reviewed the species audit artifact from [CI #43952010312](https://github.com/markeetox/LUPITA/actions/runs/43952010312), generated from main commit `866dc4a`.
- Confirmed 130 profiles parsed, 130 structurally valid, zero JSON parse errors, and zero model-compatibility issues.
- Catalog model scope: 105 grid / 25 sites; 23 temperature-only site pilots / 27 other single-factor / 80 multi-factor.
- Current evidence-risk classification: 64 elevated, 14 partial, 52 documented by current active-factor metadata. Combined uncertain active weight is 37.4, a configuration-weight sum, not a probability or calibrated scientific-quality measure.
- Validator recorded 96 generic-homepage source findings across 48 profiles, 3 missing factor-source findings across sailfish and tarpon, and 27 grid `required`-flag mismatch warnings.
- The 20 named-site SST profiles already reviewed are now 1 sourced, 14 partly sourced, and 5 provisional. Three remaining temperature-only site profiles are bonefish, great barracuda, and Permit.
- Created `docs/SPECIES_EVIDENCE_AUDIT_2026-11-17.md` with the complete scope, interpretation, review standard, batch sequence, and guardrails.
- Next: source-by-source review of the remaining three temperature-only site pilots, then the 27 other single-factor models, followed by the 80 multi-factor models grouped by factor family and risk.
- No species biology, numeric ranges, ideal bands, weights, active flags, gates, required flags, scoring, confidence, source selection, ingestion, or publication changed.


## 2026-11-17 | Batch A: remaining temperature-only site pilot research

- Reviewed bonefish, great barracuda, and Permit source-by-source. All three have a single active SST factor with gate and required flags, so this input determines site eligibility.
- Bonefish: peer-reviewed adult thermal-performance optima of 26.7–28.0 °C and broad critical-temperature/field exposure data from Bahamian studies; regional transfer and habitat-preference interpretation remain limitations. Recommend partly_sourced, not sourced.
- Great barracuda: South Florida archival-tag thesis reports 17.8–31.3 °C for only two large adults; FishBase model estimate 21.7–28.9 °C based on 2,020 cells. Recommend partly_sourced with strong sample-size and model caveats.
- Permit: FishBase modeled estimate 23.2–28.0 °C; 2026 Texas juvenile study associates presence with >25 °C; 1972 South Carolina survey observed 26 juvenile fish at 12.8–38.5 °C. These do not establish adult South Florida thermal preference. Retain provisional.
- Added complete source-fit review to `docs/SPECIES_EVIDENCE_AUDIT_2026-11-17.md`.
- No species JSON or prediction settings changed. Proposed status/source/note updates await review.


## 2026-11-17 | Batch B: 27 other single-factor grid SST profiles

- Reviewed all 27 single-factor grid profiles, each with one active SST factor, `gate: true`, `required: true`, and a generic NOAA Fisheries homepage-only citation.
- Research recommendations: 20 partly_sourced, 3 provisional (great hammerhead, ocean triggerfish, pollock), and 4 needs_source for the active SST claim (misty grouper, rainbow runner, Warsaw grouper, yellowedge grouper).
- Key findings include species-specific temperature ranges for albacore, cod, halibut, bigeye, cusk, tilefish, haddock, mako, tuna, billfish, swordfish, thresher shark, and snapper species. Several sources report bottom temperatures for deep demersal fish, not surface temperature.
- Identified a systematic model-to-data concern: SST is being used as the sole gating input for some species whose documented habitat is deep bottom water. Surface and bottom temperature must not be treated as interchangeable.
- Full per-profile configured intervals, evidence, caveats, sources, and recommendations are in `docs/SPECIES_EVIDENCE_AUDIT_2026-11-17.md`.
- No species JSON, numeric interval, weight, active flag, gate, required flag, scoring, confidence, source configuration, ingestion, or publication behavior changed. Metadata recommendations await review.


## 2026-11-17 | Batch C first four elevated-risk multi-factor profiles

- Reviewed African pompano, Almaco jack, black grouper, and black sea bass across 12 active factors.
- Replaced generic homepage-only factor citations with traceable species-specific sources where available; added claim-fit notes and conservative evidence statuses.
- African pompano and Almaco jack SST factors are needs_source; their depth/structure factors are partly_sourced.
- Black grouper SST, structure, and depth factors are partly_sourced; available evidence supports broad occurrence/habitat but not exact preference curves or category score rankings.
- Black sea bass structure remains sourced; SST and depth are partly_sourced because key numeric records are seasonal bottom-water observations and the species is uncommon in extreme South Florida.
- No numerical values, category maps, weights, active flags, gates, required flags, scoring, confidence, ingestion, or publication behavior changed.
- Full source-fit details are recorded in docs/SPECIES_EVIDENCE_AUDIT_2026-11-17.md.


## 2026-11-17 | Batch C second four multi-factor profiles

- Reviewed cubera snapper, gag grouper, red grouper, and red snapper across 12 active factors.
- Replaced generic FWC homepage-only factor citations with traceable species-specific sources and added conservative claim-fit notes/statuses.
- Cubera snapper: SST model estimate and reef/depth occurrence evidence are partly sourced, not a calibrated local preference.
- Gag grouper: adult/juvenile temperature, hardbottom habitat, depth, and terrain ruggedness evidence is documented; terrain ruggedness is not the same as the runtime bottom_curvature variable.
- Red grouper: SST association differs by life stage; shallow Florida Bay solution-hole use and broad offshore adult habitat must not be conflated.
- Red snapper: temperature and depth sources include bottom-water/juvenile or regional studies; structure sources support artificial reef/reef association but not exact category scores.
- No numeric values, category maps, weights, active flags, gates, required flags, scoring, confidence, ingestion, or publication behavior changed.
- Full findings and source register are in docs/SPECIES_EVIDENCE_AUDIT_2026-11-17.md.


## 2026-11-17 | Batch C third four multi-factor profiles

- Reviewed gray triggerfish, gray (mangrove) snapper, scamp grouper, and snowy grouper across 12 active factors.
- Added species-specific NOAA, FWC, SAFMC, Florida Museum, SEDAR, and peer-reviewed references; replaced generic factor homepage citations.
- Gray triggerfish: 2026 tag-return analysis (N=3,744) and spawning observations support partial SST/depth context, not a preference curve.
- Gray snapper: adult occurrence spans 13.4–32.5 °C and 0–180 m; configured factor bands represent a subset, not full species preference.
- Scamp: spawning bottom temperatures and low-profile live-bottom/depth studies partially support factors, but not year-round SST preference.
- Snowy grouper: numeric thermal observations are deep bottom-water spawning data, so active SST remains needs_source; bottom slope and depth remain partly_sourced.
- No numeric values, weights, active flags, gates, required flags, scoring, confidence, ingestion, or publication behavior changed.
- Full findings and source register are in docs/SPECIES_EVIDENCE_AUDIT_2026-11-17.md.


## 2026-11-17 | Batch C third four multi-factor profiles

- Reviewed gray triggerfish, gray (mangrove) snapper, scamp grouper, and snowy grouper across 12 active factors.
- Added species-specific NOAA, FWC, SAFMC, Florida Museum, SEDAR, and peer-reviewed references; replaced generic factor homepage citations.
- Gray triggerfish: 2026 tag-return analysis (N=3,744) and spawning observations support partial SST/depth context, not a preference curve.
- Gray snapper: adult occurrence spans 13.4–32.5 °C and 0–180 m; configured factor bands represent a subset, not full species preference.
- Scamp: spawning bottom temperatures and low-profile live-bottom/depth studies partially support factors, but not year-round SST preference.
- Snowy grouper: numeric thermal observations are deep bottom-water spawning data, so active SST remains needs_source; bottom slope and depth remain partly_sourced.
- No numeric values, weights, active flags, gates, required flags, scoring, confidence, ingestion, or publication behavior changed.
- Full findings and source register are in docs/SPECIES_EVIDENCE_AUDIT_2026-11-17.md.


## 2026-11-17 | All-species validator refresh after 12 multi-factor reviews

- Python CI #44123016856 passed with 130 profiles parsed, 130 structurally valid, 0 compatibility issues, and 0 validator errors.
- Elevated active-evidence risk: 55 profiles (down from 64 baseline).
- Partial active-evidence risk: 23 profiles (up from 14 baseline).
- Combined active uncertain factor weight: 26.4 (down from 37.4 baseline; not a probability or percentage).
- Generic homepage-only findings: 59 across 36 profiles (down from 96 across 48 profiles).
- Multi-factor risk distribution: 20 elevated, 9 partial, 51 documented.
- The validator's classifications reflect current metadata quality, not a scientific verdict. Numeric model settings and runtime behavior remain unchanged.


## 2026-11-17 | Pelagic multi-factor evidence review

- Reviewed Atlantic blue marlin, Atlantic bluefin tuna, sailfish, and tarpon.
- Blue marlin: added North Atlantic/Southwest Atlantic satellite-tagging and Gulf movement studies; marked SST, SST-gradient, convergence, bathymetry, and season partly_sourced; Gulf Stream distance remains provisional.
- Bluefin tuna: added NOAA/ICCAT/archival-tag sources for SST, fronts, vertical habitat, and seasonal migration; all active factors are partly_sourced.
- For both billfish/tuna profiles, explicitly distinguished vertical fish dive depth from seafloor bathymetry used by the pipeline's depth_m factor.
- Sailfish current_convergence was downgraded to partly_sourced; inactive cold_front now has local angler references but remains provisional.
- Tarpon inactive salinity now has an EFH source and remains partly_sourced; inactive bridges_lights remains needs_source.
- No numeric values, weights, active flags, gates, required flags, season months, scoring, confidence, ingestion, or publication behavior changed.
- Full source-fit notes are in docs/SPECIES_EVIDENCE_AUDIT_2026-11-17.md.


## 2026-11-17 | Coastal pelagic multi-factor evidence review

- Reviewed blackfin tuna, cobia, common snook, and Florida pompano.
- Blackfin tuna: nine-fish Gulf tag study supports 21.9–26.6 °C use and shallow vertical habitat; shelf-slope association partially supports bathymetry, but not direct gradient or Gulf Stream distance preferences.
- Cobia: 2026 Gulf satellite tagging supports seasonal thermal/depth behavior and southward/offshore dispersal; fish vertical depth was explicitly separated from seafloor bathymetry.
- Common snook: added 2025 Everglades abundance and juvenile thermal-tolerance studies; retained tide/time-of-day as provisional due angler-guidance limitations.
- Florida pompano: added NOAA-hosted life-history synthesis and FWC species profile; temperature, depth, and seasonal evidence are partial because physiological/juvenile data do not establish adult local catch curves.
- No numeric ranges, ideal bands, weights, active flags, gates, required flags, month lists, scoring, confidence, ingestion, or publication behavior changed.
- Full evidence notes and sources are in docs/SPECIES_EVIDENCE_AUDIT_2026-11-17.md.

