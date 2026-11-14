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

The validator and its unit tests were inspected, but the validator command and Python test suite were **not run** in this audit because no local repository checkout was available in the session. The GitHub file inspection and static cross-check are not a substitute for executing the repository test suite.

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
