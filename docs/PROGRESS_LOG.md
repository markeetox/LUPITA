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
