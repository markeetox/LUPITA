# LUPITA species catalog and scoring audit

**Date:** 2026-11-14  
**Branch inspected:** `main`  
**Scope:** 130 files in `data/species/`, `data/parameters.json`, `pipeline/species_validator.py`, `pipeline/scoring.py`, `pipeline/sites.py`, and `pipeline/predict.py`.

## Executive result

The 130 species JSON files were fetched and parsed individually. A static cross-check found no missing core identity/model fields, duplicate factor parameters within a profile, unregistered factor parameters, unsupported active parameter/kind combinations, or active-weight sums above 1.0.

That is a useful structural result, not a clean bill of health. The audit found important limitations in biological evidence quality, site-model depth, confidence calculation, and the consistency of missing-data semantics. The existing validator catches some of these issues, but it does not yet test all of the behavior that matters.

No species factor values, weights, active flags, scoring thresholds, prediction code, NOAA source configuration, or workflows were changed during this audit.

## Catalog inventory

- **130** species JSON files inspected and parsed.
- **105** use the grid model.
- **25** use the named-site model.
- The core fields checked across every profile were `id`, `common_name`, `scientific_name`, `factors`, `profile`, and `habitat_zone`.
- No unsupported active factors or unknown registry parameters were found in the static cross-check.
- No duplicate factor parameter keys within a profile or active weight overflow were found.
- The normal minimum coverage is **0.70**. Mahi-mahi is the only profile observed with an explicit override, **0.60**.

## Findings requiring attention

### 1. Active biological evidence is not reflected directly in prediction confidence

Twelve profiles contain **33 active factors** marked `provisional`, `estimated`, or `unsourced`:

| Species | Active factors with provisional/estimated/unsourced status |
|---|---:|
| Blackfin tuna | 3 |
| Bonefish | 1 |
| Cobia | 2 |
| Great barracuda | 1 |
| Hogfish | 2 |
| Mahi-mahi | 4 |
| Mutton snapper | 3 |
| Permit | 1 |
| Sailfish | 5 |
| Snook | 2 |
| Tarpon | 2 |
| Wahoo | 7 |
| **Total** | **33** |

Eight of those active factors have no source references recorded, across blackfin tuna, bonefish, hogfish, mutton snapper, Permit, and tarpon.

The prediction confidence logic currently considers active-factor count, environmental coverage, gap-filled chlorophyll, and an optional Low confidence cap. It does not inspect active factor `value_status` or the share of active weight supported by sourced evidence. A profile can therefore have high environmental coverage while relying on provisional biological assumptions and still receive Medium confidence if no Low cap is configured.

Examples needing review include blackfin tuna, hogfish, mahi-mahi, and mutton snapper. Their factor evidence labels already disclose uncertainty, but the output confidence calculation does not incorporate that uncertainty.

**Recommendation:** define an evidence-aware confidence policy and add regression tests before changing confidence output. Do not automatically disable every provisional factor; first distinguish provisional hypotheses from factors that are essential to the model.

### 2. Most named-site species models are temperature-only

Of the **25** site-model profiles, **23** have exactly one active factor: sea-surface temperature. Only snook and tarpon currently have five active factors each.

This means the other 23 named-site models are temperature-screening models, not multi-factor habitat models. Their active SST weight is 0.35, but the scorer normalizes by the weight of factors actually available. With SST as the only active factor, the displayed score is effectively the SST factor score, not 35% of a larger complete model. The confidence code correctly marks a one-factor model Low, but the product description and explanations should make the temperature-only limitation clear.

Permit, bonefish, and great barracuda are especially important South Florida examples: each currently has one active, provisional SST factor. Their site recommendations must not be interpreted as validated habitat suitability.

**Recommendation:** treat these as explicitly limited pilot models. Expand only when a site-level input is both available in the engine and supported by species-specific evidence. Do not activate factors merely to increase the count.

### 3. Missing-data semantics differ between grid and site scoring

Both engines skip missing optional factors and normalize scores over available factor weights. Both enforce the profile's minimum coverage threshold (default 0.70).

However, the `required` and `gate` flags do not have identical behavior:

- **Grid scorer:** `required` is not read by `score_species`. A missing factor marked `gate` makes the entire species unavailable; a gate with non-positive or missing cell values excludes those cells. Missing non-gate factors are skipped.
- **Site scorer:** a missing factor marked `required` makes that site unscored. A gate rejects a site when its evaluated score is non-positive. A missing gate that is not also required is skipped like another optional factor.

Current SST gates generally carry both flags, so the principal safety gate is represented in both modes. Still, the meaning of the two fields is not a single shared contract. Future profile edits could create surprising behavior if a maintainer assumes `required` works the same way in both engines.

**Recommendation:** document the intended model-specific contract, add tests for all combinations of missing / required / gate, and make the validator flag contradictory or ineffective flag combinations. Do not change scorer behavior until those tests and intended semantics are agreed.

### 4. The existing species validator needs additional checks

The existing `pipeline/species_validator.py` already checks core fields, factor kinds and parameter compatibility, weights, range/season shape, source metadata, evidence labels, and basic biological dimensions. It also identifies one-factor models.

The current validator does not fully check:

- Whether `min_coverage` is numeric and within the allowed 0–1 interval.
- Whether `required` and `gate` are booleans and whether their combination matches the engine's behavior.
- Whether category `map` values are numeric and map keys align with the parameter registry. It currently warns when `preferred` is absent even though the site scorer can validly score a category from `map` alone.
- Whether active evidence quality should lower the confidence ceiling.
- Whether a parameter is technically callable but implemented as a placeholder rather than a real site-specific measurement.

The validator's supported-factor tables are manually maintained copies of scorer capabilities. They should be regression-tested against the actual scoring dispatch so they cannot silently drift.

The validator and its unit tests were inspected during the initial static review. A subsequent follow-up added validator coverage and ran the full suite plus the validator in GitHub Actions; the executed results are recorded below.

## Missing-data behavior confirmed from code

- Grid factors that are missing or non-finite are excluded from the available weight at each cell.
- Grid coverage is calculated per cell; cells below the configured minimum coverage are not eligible.
- A missing grid gate makes the species unavailable; a failed gate excludes affected cells.
- Site factors that are missing are skipped unless marked `required`, in which case that site is not scored.
- Site coverage is calculated per site; sites below the configured minimum are excluded.
- Prediction confidence is currently Low or Medium, not a calibrated probability of fish presence. There is no High confidence state.

## Next work, in order

1. Extend `pipeline/species_validator.py` and its tests to cover coverage bounds, category maps, evidence-aware confidence diagnostics, and required/gate semantics.
2. Agree on the evidence-to-confidence policy before changing prediction confidence.
3. Label the 23 single-factor site models clearly as temperature-only pilots; prioritize South Florida models for evidence-backed expansion.
4. Review the 12 profiles with active provisional/estimated/unsourced factors, starting with the eight active factors that lack source references.
5. Run `python scripts/validate_species.py` and the focused species/scoring tests from a local checkout or an authorized non-NOAA test workflow.
6. Keep the NOAA ingestion investigation paused until explicitly cleared by the project owner.

## Files inspected

- `data/species/*.json` (130 profiles)
- `data/parameters.json`
- `pipeline/species_validator.py`
- `pipeline/scoring.py`
- `pipeline/sites.py`
- `pipeline/predict.py`
- `tests/test_species_validator.py`

**Boundary:** this was a static catalog and scoring-code audit. No NOAA endpoint was contacted, no Pull Ocean Data workflow was run, and no production scoring behavior was changed.


## Validator follow-up implementation | 2026-11-14

The read-only validator and its tests were strengthened after the catalog review:

- Validates `min_coverage` as a finite number from 0 through 1.
- Validates category `map` shape, finite 0–1 scores, and registry category keys. A valid `map` no longer incorrectly requires a separate `preferred` list.
- Validates `active`, `required`, and `gate` as booleans.
- Warns when grid profiles use `required`, which the grid scorer does not read, and when a site gate is not also required, meaning a missing site value is skipped.
- Reports active evidence weight by status, uncertain active weight, partly sourced active weight, and an evidence-risk diagnostic.
- Labels one-factor SST-only site models as `temperature_only_pilot` in audit output and summarizes their count.
- Adds regression tests for each new validator behavior and for evidence-weight aggregation.

These evidence and model-scope fields are diagnostics only. Prediction confidence, score calculation, factor weights, thresholds, and active flags remain unchanged.

A proposed confidence policy is documented separately in [Species Model Confidence Policy](SPECIES_MODEL_CONFIDENCE_POLICY.md). It is explicitly not active; user-facing confidence changes require review and approval.

The main Python workflow now runs the species validator after the test suite whenever Python code, species profiles, or the parameter registry changes, and uploads the JSON/Markdown/CSV audit reports as a workflow artifact.

**Validation:** full CI run is pending on the current profile-fix commit. Earlier runs exposed a malformed evidence-status handling bug in the new validator and stale phrase assertions in the existing bonefish/permit profile regression test. Both were corrected; the current run must pass before this milestone is marked validated.


## Executed validator results | 2026-11-14

The updated validator ran against the complete repository catalog in GitHub Actions and generated JSON, Markdown, and CSV reports.

| Metric | Result |
|---|---:|
| Profiles inspected | 130 |
| Profiles parsed | 130 |
| JSON parse errors | 0 |
| Structurally valid under active/inactive factor rules | 130 |
| Active model compatibility issues | 0 |
| Validator errors | 0 |
| Validator warnings | 406 |
| Validator informational findings | 123 |
| Temperature-only named-site pilots | 23 |
| Other one-factor models | 27 |
| Multi-factor models | 80 |
| Profiles with elevated active evidence risk | 12 |
| Combined uncertain active factor weight across profiles | 5.70 |

The 5.70 value is the sum of uncertain active factor weights across species profiles. It is not a probability, a coverage percentage, or a single model's score.

The validator classifies 127 profiles as **NEEDS MODEL REBUILD** and 3 as **NEEDS RESEARCH**. This classification is driven partly by the validator's six-dimension structural review proxy and single-factor warnings. It is a prioritization signal for further research and model design, not an independent scientific finding that every one of those species profiles is unusable.

The follow-up also recognized `needs_source` as a valid evidence workflow status and downgraded incomplete numeric definitions on inactive factors to warnings. Active factors with incomplete range/ideal definitions remain errors. This preserves incomplete future/planned factors without pretending they are ready for scoring.

**Final executed run:** [Python tests and species audit #43622006765](https://github.com/markeetox/LUPITA/actions/runs/43622006765): **272 passed, 0 failed, 115 warnings**. The species validator completed successfully and uploaded the `lupita-species-audit` artifact. The final validator summary was 130 profiles parsed, 130 structurally valid, 0 active model compatibility issues, and 0 validator errors.


## Active factor source review | 2026-11-14

The eight active factors that previously lacked factor-level source references have now been reviewed across six profiles. Each now has source references and explicit limitations in `value_notes` or the reason text. All eight remain `provisional`; no source was treated as proof that its configured numeric values are validated.

Detailed species-by-species findings: [Active Factor Evidence Review](ACTIVE_FACTOR_EVIDENCE_REVIEW_2026-11-14.md).

The six updated JSON profiles parsed successfully after commit. The final full-suite and validator run for these profile changes is pending. No factor values, weights, active flags, gates, required flags, or NOAA configuration changed.


## Final evidence-review validation

After the six-profile source/notes update, the validator still reports 130 profiles parsed, 130 structurally valid, 0 active model compatibility issues, and 0 errors. Catalog warnings decreased from 406 to **398**. The eight reviewed active factors no longer produce missing-source findings; remaining missing-source warnings include inactive/planned factors.

The catalog still reports 12 profiles with elevated active evidence risk and 5.70 total uncertain active factor weight across profiles. This is expected: the reviewed factors remain provisional. Source references document context and limitations; they do not validate the configured numerical preferences.

Final full suite and species audit: [run #43622573953](https://github.com/markeetox/LUPITA/actions/runs/43622573953), **272 passed, 0 failed, 115 warnings**.
