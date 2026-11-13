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
