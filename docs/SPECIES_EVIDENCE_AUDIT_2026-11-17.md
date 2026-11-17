# LUPITA all-species evidence audit: master inventory

**Audit date:** 2026-11-17  
**Branch / audited commit:** `main` / `866dc4a44ea3e7a2ae819bd14c77ed5b1ccd70c0`  
**Source:** species-profile audit artifact from [Python CI run #43952010312](https://github.com/markeetox/LUPITA/actions/runs/43952010312)  
**Scope:** all JSON profiles in `data/species/`; read-only inventory and prioritization  
**Boundary:** this inventory does not change species biology, factor values, scoring, or production behavior.

## Executive result

The current catalog contains **130 species profiles**, not just the 20 named-site SST profiles reviewed on November 16. The existing validator has already inspected all 130:

- 130 parsed; 0 JSON parse errors.
- 130 structurally valid; 0 model-compatibility issues.
- 105 grid models and 25 named-site models.
- 23 temperature-only named-site pilots, 27 other single-factor models, and 80 multi-factor models.
- 64 profiles have elevated active-evidence risk, 14 have partial active-evidence risk, and 52 have no active uncertain weight under the validator's current metadata rules.
- The combined active uncertain factor weight is 37.4. This is a sum of configured factor weights across profiles, **not** a probability, percentage of fish presence, or calibrated scientific-quality score.
- The validator classifies 127 profiles as NEEDS MODEL REBUILD and 3 as NEEDS RESEARCH. These are structural review classifications, not a scientific verdict that 127 species profiles are unusable.

The audit artifact and validator findings are useful for prioritization, but they are not a substitute for source-by-source biological review. A `sourced` label or a specific URL does not prove that the source supports the configured value, population, life stage, region, or model use.

## Catalog breakdown

| Model scope | Profiles | Elevated active-evidence risk | Partial risk | Documented by current metadata |
|---|---:|---:|---:|---:|
| Temperature-only site pilot | 23 | 8 | 14 | 1 |
| Other single-factor model | 27 | 27 | 0 | 0 |
| Multi-factor model | 80 | 29 | 0 | 51 |
| **Total** | **130** | **64** | **14** | **52** |

The 20 named-site SST profiles reviewed and updated on November 16 are part of the 23 temperature-only pilots. Their current declared statuses are 1 `sourced`, 14 `partly_sourced`, and 5 `provisional`. The three remaining temperature-only site profiles are **bonefish, great barracuda, and Permit**.

## Validator findings that guide the review

The November 16 audit artifact recorded:

| Finding | Count | Interpretation |
|---|---:|---|
| Generic homepage-only source warnings | 96 findings across 48 profiles | These references are not traceable enough to substantiate a factor claim. Findings include configured factors whether active or inactive. |
| Missing factor-source warnings | 3 findings across 2 profiles | Sailfish and tarpon need factor-level source inspection. |
| Active evidence uncertainty | 64 profiles | At least some active factor weight is provisional, has incomplete reference metadata, or otherwise fails the validator's current source checks. |
| Partly sourced active evidence | 19 profiles | Declared partial support needs claim-fit review. |
| Grid `required` flag ignored | 27 profiles | The grid scorer does not enforce factor-level `required`; the effective behavior must be reviewed against `gate` and runtime contracts. |
| Single-factor models | 50 profiles | Full data coverage does not establish biological completeness. |
| Limited biological dimensions | 50 profiles | Only one of six structural review dimensions is represented. |
| Partial biological dimensions | 75 profiles | Two or three of six dimensions are represented. |
| Provisional timing | 128 profiles | Timing maps are hypotheses/angler guidance, not empirically calibrated feeding probabilities. |

The 96 generic-reference findings are **not 96 species** and do not imply all 96 are active. The 3 missing-source findings occur in two profiles. These distinctions matter when prioritizing work.

## Review standard

Every configured factor will be assessed separately. The profile-level status alone is not sufficient.

For each factor, record:

1. Species identity and scientific name.
2. Factor parameter, model type, active state, weight, gate, and required flag.
3. The exact configured claim: numeric range, ideal interval, category, season, or other behavior.
4. Source type and traceability: primary study, fisheries assessment, agency species account, dataset, synthesis, or angler guidance.
5. What the source actually measures: occurrence, abundance, physiological tolerance, preference, migration cue, spawning, juvenile habitat, or adult habitat.
6. Population, geographic region, life stage, depth/measurement type, and study period.
7. Whether the source supports the configured claim directly, partially, or not at all.
8. Limitations, conflicting evidence, and what additional evidence is needed.

Use conservative statuses:

- `sourced`: specific, traceable evidence directly supports the factor's intended use.
- `partly_sourced`: relevant evidence exists but has material limitations.
- `provisional`: plausible starting assumption without sufficient direct validation.
- `needs_source`: no defensible supporting reference found.
- `not_applicable`: the factor does not belong in that model or is not intended for use.

A source can be authoritative and still be a poor fit for a specific factor claim. For example, a spawning temperature does not automatically establish year-round adult habitat preference; bottom temperature is not interchangeable with satellite SST; and an occurrence range is not a preferred interval.

## Execution order

### Batch A: finish the temperature-only site pilots

Review bonefish, great barracuda, and Permit using the same source-by-source standard as the prior 20. These models have a single SST input that is both required and a gate, so weak thermal evidence directly affects site eligibility.

### Batch B: the 27 other single-factor models

These are all currently elevated-risk profiles. Review the actual factor claim and the specific source rather than assuming a generic species page validates the configured range. Confirm whether each is SST-only or another single-factor design and whether the active gate matches the runtime contract.

### Batch C: the 80 multi-factor models

Review active factors in coherent parameter groups (SST/gradients, depth/bathymetry, structure/habitat, currents/convergence/Gulf Stream edge, chlorophyll, and seasonal presence). Reuse a source assessment across species only when its taxon, geography, life stage, and measured variable genuinely apply. The 29 multi-factor profiles with elevated active-evidence risk receive priority within this batch.

### Batch D: timing and profile-level biology

Review timing maps, spawning/migration narratives, habitat descriptions, and open research items separately from environmental factor evidence. Angler guidance may be retained as guidance, but must not be represented as a measured probability or established biological optimum.

### Batch E: approved metadata updates and validation

After each research batch is reviewed, apply only approved source references, evidence statuses, and explanatory notes. Then run the species validator and full tests. Keep a progress register so completed species/factors are not researched twice.

## Guardrails

- No changes to numeric temperature/depth ranges or ideal intervals during evidence discovery.
- No changes to factor weights, active flags, gates, required flags, minimum coverage, scoring, confidence, or source selection without a separate evidence-backed approval.
- Do not infer South Florida applicability from a distant population without stating the transfer limitation.
- Do not equate a specific URL, number of citations, or a `sourced` declaration with scientific validation.
- Preserve uncertainty and conflicting evidence rather than forcing a confident label.
- Keep data freshness, environmental input availability, and biological evidence quality as separate concepts.

## Immediate next action

Start Batch A with bonefish, great barracuda, and Permit, then move to the 27 other single-factor profiles. The master inventory should be refreshed from the current `main` branch after each completed batch so new changes are reflected accurately.

## Audit artifact

The source audit JSON, Markdown, and CSV were generated by the existing CI workflow and uploaded as artifact `lupita-species-audit` on run #43952010312. Run `python scripts/validate_species.py` to regenerate them locally.
