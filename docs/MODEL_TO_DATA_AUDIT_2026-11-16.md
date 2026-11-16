# LUPITA model-to-data audit

**Date:** 2026-11-16  
**Branch:** `main`  
**Scope:** static review of model dispatch, layer construction, source configuration, missing-data behavior, and confidence semantics.  
**Boundary:** no NOAA requests, ingestion, publication, source changes, species biology, weights, active flags, scoring behavior, or prediction output changes.

## Executive result

A structurally valid species profile is not automatically an end-to-end supported model. Each active factor needs three checks: (1) a compatible scoring implementation, (2) a real pipeline input, and (3) understood missing-data behavior.

Grid and named-site models have different runtime contracts. Grid models score layers on the SST grid; named-site models use nearby buoy/tide observations, astronomical calculations, calendar lookups, and static site metadata. Their `required` and `gate` semantics are not interchangeable.

## 1. Factor-to-input contract

### Grid models

| Factor | Runtime input | Availability and limitation |
|---|---|---|
| `sst_c` | NOAA CoastWatch MUR SST, `jplMURSST41` | Foundational grid; same-product Upwell host fallback. If both hosts fail, layer construction cannot produce a prediction grid. |
| `sst_gradient` | Derived from SST; shallow cells masked when bathymetry is available | Computed front/gradient layer, not an independent observation. |
| `chlorophyll` | NOAA-20 VIIRS daily chlorophyll, `nesdisVHNnoaa20chlaDaily` | Optional and cloud-gapped. Gap-filled product is disabled. |
| `chl_gradient` | Derived from chlorophyll | Only available when chlorophyll loads. |
| `depth_m` | NOAA ETOPO 2022 15-arc-second | Sampled at stride 15 over a broad region; regional context, not reef-scale bathymetry. |
| `current_speed`, `current_dir` | NOAA HF Radar 2 km surface vectors; age-qualified satellite-altimetry fallback | HFR is limited to the South Florida query window. Represents near-surface coastal flow; quality fields are diagnostics, not hard gates. |
| `current_convergence` | Derived from paired east/north current components | Requires both usable vector components. |
| `gulf_stream_edge` | Derived from satellite-altimetry geostrophic flow | Approximate inshore-edge estimate, not a direct fish-presence measurement. |
| `distance_to_inlet` | Derived from inlet/pass coordinates in `config/places.json` | Real grid-distance calculation exists; requires inlet locations. |
| `structure_type` | FWC artificial reef and natural reef/hard-bottom layers | Rasterized onto the common grid. No mapped feature does not prove structure is absent. |
| `bottom_slope`, `bottom_curvature` | Derived from ETOPO depth | Both depend on optional, coarsely sampled bathymetry. |
| `spawning_season`, `season_presence` | Current calendar month | Deterministic calendar lookup. Biological month ranges are model assumptions, not live environmental feeds. |

### Named-site models

| Factor | Runtime input | Availability and limitation |
|---|---|---|
| `sst_c` | Nearest qualifying buoy within 40 km, otherwise SST grid within 8 km | Buoy preferred; missing required value makes that site unscored. |
| `tide_stage` | Nearest usable CO-OPS tide station within 120 km | A station inside this broad radius may represent a different local tidal regime. Missing optional input is skipped. |
| `time_of_day` | Astronomical light phase from time and site coordinates | Computed, not fetched as an observation. |
| `spawning_season`, `season_presence` | Current calendar month | Calendar-derived; biological assumptions still need evidence. |
| `structure_type` | Static `site.kind` | Only site kinds actually present in the site catalog can be scored. Configured categories can be unreachable or unmapped. |
| `distance_to_inlet` | **Constant 0.0 returned for every site** | Placeholder, not a measurement. Validator rejects active use; keep inactive until a real site-distance input exists. |

## 2. Missing-data behavior

### Grid scorer

- Missing/non-finite factor values are excluded from available weight at each cell.
- Scores are normalized by the weight of factors actually available at that cell.
- Coverage is per cell; cells below profile `min_coverage` (default 0.70) are ineligible.
- A missing factor marked `gate` makes the species unavailable; a gate that evaluates to zero or is missing at a cell excludes that cell.
- The grid scorer does **not** read factor-level `required`. The validator warns when a grid factor sets it. `required: true` is not an enforced grid requirement.
- SST remains foundational independently: grid shape, final eligibility, and prediction refresh depend on the SST layer.

### Named-site scorer

- Missing factors are skipped unless `required`; a missing required value makes that site unscored.
- A gate rejects a site when its evaluated score is non-positive.
- A site gate without `required: true` can be skipped when its input is missing; the validator warns.
- Coverage is per site and compared with `min_coverage` (default 0.70).
- Available weights are renormalized. A partial model's score is therefore not equivalent to a complete model evaluated with every intended input.

These contracts are documented, not unified. Changing them would change prediction behavior and needs separate design approval and regression tests.

## 3. Confidence and evidence

Current confidence is Low or Medium, not a calibrated probability of catching or finding a fish. The site scorer lowers confidence for fewer than three active factors, coverage below 90%, or a profile-level Low cap. The current confidence calculation does not directly incorporate factor `value_status` or the share of active weight supported by specific sources.

Environmental coverage, source freshness, and biological evidence quality are separate dimensions. A source URL may be specific without supporting the exact configured temperature band or habitat claim. Calendar inputs can be technically available while their biological assumptions remain provisional.

## 4. Catalog context carried forward

The previously executed 130-profile audit remains the catalog baseline, not a newly rerun validator in this pass:

- 130 profiles parsed and structurally valid; 0 active model compatibility issues and 0 validator errors in that recorded run.
- 25 named-site profiles: 23 temperature-only pilots and 2 multi-factor models (snook and tarpon).
- 12 profiles had elevated active evidence risk.
- The 20 homepage-only SST references identified in the site triage are not traceable species-specific evidence. Bonefish, great barracuda, and Permit remain provisional South Florida SST pilots.
- Snook/tarpon structure maps need an explicit decision about allowed site kinds that currently map to zero.
- The site `distance_to_inlet` placeholder must remain inactive.

## 5. Prioritized next actions

1. Add runtime contract tests for grid/site missing, required, gate, coverage, and normalization combinations without changing current semantics.
2. Add a factor-to-layer contract test comparing active profile parameters against engine dispatch and layer construction, preventing validator/runtime drift.
3. Expose per-prediction factor availability and evidence separately. Environmental coverage, source freshness, and biological evidence are not interchangeable.
4. Review site tide-station distance/local regime, snook/tarpon site-kind mappings, and the three provisional South Florida SST bands.
5. Do not activate site `distance_to_inlet` until a real input is implemented and tested.
6. Keep HFR comparison paused while NOAA ERDDAP blocks the comparison runner. Do not use the access failure as evidence for a product switch.

## Files inspected

`config/sources.json`, `pipeline/layers.py`, `pipeline/scoring.py`, `pipeline/sites.py`, `pipeline/derive.py`, `pipeline/currents.py`, `pipeline/structure.py`, `pipeline/predict.py`, `pipeline/species_validator.py`, `docs/SITE_MODEL_TRIAGE_2026-11-15.md`, `docs/SPECIES_CATALOG_AUDIT_2026-11-14.md`, and `tests/test_species_validator.py`.

**Conclusion:** the next safe engineering step is tests and diagnostics around existing contracts, not more active factors or changed biological weights. No external NOAA access was attempted during this audit.

## 6. Runtime contract tests added

Added `tests/test_model_data_contracts.py` to lock down the existing grid/site missing, required, gate, coverage, and normalization behavior. Added `tests/test_factor_data_contracts.py` to compare all active species factors against grid/site dispatch maps, exercise the actual grid and site factor scorers with deterministic synthetic inputs, and verify the grid layer builder exposes every declared non-calendar factor input using fake NOAA/FWC responses. Seasonal month context is correctly tested at the prediction/scoring boundary because `build_fish_json` injects it; it is not a raw layer-loader output.

The final test run for commit `909fad31b635b3a0c65a3256fdfcd7203d526f45` completed successfully, including the species profile audit and artifact upload: [Python tests run #43941668108](https://github.com/markeetox/LUPITA/actions/runs/43941668108). An earlier successful run on the same test set before the open-ended range fixture hardening reported **294 passed, 115 warnings**. No production code or model behavior was changed.
