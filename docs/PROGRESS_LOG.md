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
- Corrected the unmatched parenthesis in the Jewfish Creek depth-context expression.
- Replaced literal escaped newline sequences between Jewfish Creek assertions with actual source line breaks.
- Added a focused `py_compile` preflight before tests and extraction in the landmark evidence workflow.

### Validation

- The original topology expression was independently confirmed to raise a Python `SyntaxError` because a closing parenthesis appeared before the list-comprehension bracket.
- The repository workflow must now run focused compilation before pytest and network extraction.
- **Current-head GitHub Actions validation is pending.** Do not mark the workflow repair complete until the focused workflow passes.

### Decisions and guardrails retained

- Keep all NOAA/FDEP/FWC/county research geometry separate from production prediction inputs.
- Do not infer Government Cut, inlet connectivity, or cross-bay separators from proximity.
- Keep MHW, MHHW, and MLLW concepts separate.
- Reuse persisted research sources; do not repeat extraction unless inputs or logic change.

### Next action

Run the focused Biscayne landmark evidence workflow once the commit is pushed, then inspect its artifact and update this log with the actual run URL and test counts.
