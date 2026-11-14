# Species evidence and confidence policy

**Status:** proposed policy for project-owner review  
**Date:** 2026-11-14  
**Applies to:** species profile audit, grid predictions, and named-site predictions

## Purpose

Keep three different concepts separate:

1. **Environmental coverage:** how much of the configured active factor weight had usable input for a cell or named site.
2. **Biological evidence quality:** how well the active factor values and assumptions are supported for the species and region.
3. **Prediction confidence:** a conservative communication label about the model's support. It is not a probability that fish are present or will be caught.

A high environmental coverage value must never be interpreted as proof that the biological model is well supported.

## Evidence accounting

The species validator reports active factor evidence by configured weight:

- `sourced`: the factor is explicitly marked sourced and has usable source references.
- `partly_sourced`: the profile explicitly says the evidence is partial.
- `provisional`, `estimated`, or `unsourced`: the active factor is not established strongly enough to treat its numeric setting as a validated species preference.
- Missing or unrecognized evidence status, or missing/invalid source references: incomplete evidence metadata.

The audit reports uncertain active weight and partly sourced active weight separately. These are diagnostic weight totals, not probabilities or estimates of scientific accuracy. A source URL is not proof that the source supports the exact numeric value or local population.

## Proposed confidence policy (not yet active)

1. Preserve environmental coverage as its own numeric field. Do not fold evidence status into coverage.
2. A prediction should not receive Medium confidence if any active factor with material weight is marked provisional, estimated, unsourced, or lacks usable source references. The conservative default proposal is to cap such a result at Low until the project owner approves a more nuanced threshold.
3. Partly sourced factors must be surfaced as a caveat. They should not automatically be treated as fully sourced.
4. Existing profile-level Low caps and existing Low-confidence conditions remain in force.
5. A single-factor site model must remain explicitly identified as a temperature-only pilot and Low confidence. It must not be described as validated habitat suitability.
6. Do not introduce a High confidence label until LUPITA has calibration data demonstrating that a higher category is meaningful.
7. Confidence labels must not be described as catch probability, fish-presence probability, or a guarantee.

## Approval and validation required before activation

This policy is **not wired into prediction output yet**. Before changing user-facing confidence:

- Review the proposed conservative cap and decide whether any weight threshold or exception is justified.
- Add regression tests for grid and site predictions with sourced, partly sourced, provisional, missing-source, and mixed-evidence factors.
- Confirm the confidence basis is included in the published prediction payload and explanations.
- Compare outputs across representative South Florida species, especially the one-factor site pilots and profiles with mixed evidence.
- Keep all prediction weights, biological ranges, gates, and minimum coverage thresholds unchanged unless separately reviewed and approved.

## Current implementation

The read-only species validator now emits `evidence_risk`, `active_evidence_status_weight`, `active_uncertain_weight`, `active_partly_sourced_weight`, `model_scope`, and `min_coverage`. These fields are audit diagnostics only. No production score or confidence label is changed by this policy document.

## Boundaries

This policy and validator work are static species/model work. They do not require NOAA endpoint requests or Pull Ocean Data workflow runs. Environmental ingestion remains paused until explicit project-owner clearance.
