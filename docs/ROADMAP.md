# LUPITA engineering roadmap

**Last updated:** 2026-11-15 | **Code:** `main` | **Generated-data export:** `data` only

This is the handoff record for future sessions. Read it with [Project Status](PROJECT_STATUS.md) and [Progress Log](PROGRESS_LOG.md). Do not restart completed work or repeat expensive research workflows without a specific reason.

## Project contract
- Run app, tests, pipeline and source configuration from `main`; publish generated JSON/API/PNG assets to `data`.
- Keep unapproved GIS interpretations and candidate geometry out of production inputs.
- Preserve source timestamps, provenance, missing coverage and quality limitations.
- Do not change species biology, prediction weights or scoring gates without evidence and regression tests.
- Make production changes directly on `main` in coherent batches. Update README, Project Status, Progress Log and this roadmap.
- Run focused tests first, full tests for integration milestones, and no unrelated NOAA/FWC extraction workflows.

## Verified baseline
- Freshness diagnostics: `536984e0af96ddf0cc0c7a8edd344a2b4050568c`; chlorophyll fallback correction: `9c7ed75a739652e54f1989b0a224d1a0d3419cb8`.
- Last pre-upgrade production refresh: [workflow #202](https://github.com/markeetox/LUPITA/actions/runs/43469532292), success with predictions refreshed, but currents about 1,121 hours old and health degraded.
- Last pre-upgrade Python tests: [run #404](https://github.com/markeetox/LUPITA/actions/runs/43467354619).
- First HF Radar integration suite after fixture corrections: [run #407](https://github.com/markeetox/LUPITA/actions/runs/43475604949), **254 passed, 0 failed, 115 warnings**.
- Run #408 added per-feed freshness assertions; 254 passed and 1 health-test assertion failed because the minimal fixture omitted a separate primary freshness object. The fallback comparison was corrected.
- Final suite: [run #409](https://github.com/markeetox/LUPITA/actions/runs/43476053350), **255 passed, 0 failed, 115 warnings**.
- HF Radar source/loader commit: `a4e7bcf633a84238723dd250df9f5a1e3f87e159`.

## Environmental sources
| Layer | Primary | Fallback / support | Freshness |
|---|---|---|---|
| SST | NOAA CoastWatch `jplMURSST41` | ERDDAP host fallback | warning 36h, stale 72h |
| Chlorophyll | NOAA-20 VIIRS `nesdisVHNnoaa20chlaDaily` | gap-filled product disabled | warning 72h, stale 120h |
| Coastal currents | NOAA/NESDIS HF Radar `ucsdHfrE2`, hourly 2 km | `nesdisSSH1day` only when timestamp-qualified (max age 72h); NOAA RTOFS model ingestion is next | warning 12h, stale 24h (provisional) |
| Gulf Stream edge | NOAA CoastWatch `nesdisSSH1day`, daily 25 km | no alternate model | warning 36h, stale 72h |
| Bathymetry | NOAA NCEI ETOPO 2022 15s, stride 15 | none | static |

HF Radar request window: 24.0-28.5°N, 83.5-78.0°W. It represents near-surface coastal flow, not full-depth or complete offshore circulation. `hdop`, contributing-site and radial-count metrics are reported but not hard quality gates. Satellite altimetry supplies approximate Gulf Stream-edge context. It may fill current-vector gaps only when its timestamp is known, non-future, and no older than 72 hours; otherwise it is excluded from current vectors. HF Radar remains the observation overlay. NOAA S-111 RTOFS East is the preferred broad-area model candidate: public HDF5 tiles, 6-hourly forecast values over a 72-hour horizon, approximately 8.5 km resolution, and currents at 4.5 m depth or half the water column where shallower. The S-111 service is described as preliminary; South Florida tile coverage, catalog freshness, file size, and HDF5 decoding must be validated before use. Raw RTOFS HTTPS/GRIB remains a fallback implementation route. Each source's timestamp, forecast lead, eligibility and coverage must remain distinct.

## Active milestone: validate regional currents and replace stale broad-area fallback
**Status:** HFR live retrieval confirmed, but its spatial contribution is sparse. Production #203 loaded HFR at 7.85 hours old; only 2.006% of requested HFR source cells contained valid vectors. The 0.0123% aligned fraction is calculated against the entire North America grid and is not a useful local percentage. Satellite altimetry supplied most of the 53.4818% combined current coverage but was 1,121.85 hours old. A new fail-closed age guard excludes altimetry older than 72 hours from current vectors while retaining its Gulf Stream-edge role. NOAA RTOFS is the preferred broad-area model candidate; direct NOMADS OPeNDAP was retired in February 2026, so production ingestion must use supported HTTPS model files or GRIB filtering.

Acceptance criteria:
1. Report HFR, fallback and combined valid fractions inside the South Florida HFR request window, alongside whole-grid fractions.
2. Compare HFR 1 km, 2 km and 6 km products on the same South Florida window, including timestamps, valid-cell coverage and quality metrics.
3. Identify a machine-readable broad-area current source with current observation/model initialization time, forecast lead, spatial coverage and units.
4. Evaluate NOAA Global RTOFS NetCDF fields and USF EFCOM coastal FVCOM output. EFCOM is geographically relevant but its public interface currently exposes visual products and labels results research-grade; machine-readable access is not yet verified.
5. Keep satellite altimetry as Gulf Stream-edge context and permit current-vector fallback only when timestamp-qualified (<=72h); never silently present stale data as current.
6. Implement NOAA RTOFS using its supported HTTPS model-file or GRIB-filter route; record model initialization time and forecast lead separately from observation age.
7. Keep HF Radar as a high-value observation overlay where valid, not a full-coverage regional model.
8. Keep Gulf Stream-edge provenance separate from the selected nearshore current source.
9. Do not change scoring weights or biology during source evaluation.

## Next sequence
1. Inspect the next production refresh for query-region coverage metrics.
2. Test candidate data access and subset sizes for NOAA RTOFS and EFCOM before adding production dependencies.
3. Compare model fields against HF Radar and local NOAA buoy/current observations where available.
4. Choose a broad-area fallback only after live timestamp and coverage validation.
5. Calibrate freshness thresholds after multiple production observations.
6. Add source-quality/coverage context to species explanations without implying catch probability.
7. Audit species evidence before any scoring changes.
8. Continue Biscayne shoreline/inlet work from persisted evidence; do not infer connectivity or mix MHW/MHHW/MLLW geometry.

## Verification
```bash
python -m pytest -q
python -m pipeline.check_sources
python -m pipeline.run
```
A metadata check is not a substitute for inspecting the actual production CSV pull and coverage.


## Active milestone: upstream outage resilience and truthful publication
1. Use NOAA CoastWatch `jplMURSST41` first and the documented `upwell` ERDDAP mirror second.
2. Report dependent layers as `not_attempted` when SST prevents their requests from starting.
3. Separate current refresh health from last-known-good prediction data with `latest.json` and `api/v1/refresh.json`.
4. Restore prior `data` branch prediction files/API when a refresh fails.
5. Validate with focused/full tests and a manual production pull. Do not change scoring weights or species biology.


**Milestone status:** SST host fallback, truthful `not_attempted` diagnostics, and separate refresh/prediction publication are implemented. Full Python suite passes (**262 passed, 0 failed**) on [run #43493987730](https://github.com/markeetox/LUPITA/actions/runs/43493987730). Remaining acceptance test is one live Pull Ocean Data run to verify mirror response and published snapshot behavior.


**Latest validation:** **262 passed, 0 failed, 115 warnings** on [run #43494256052](https://github.com/markeetox/LUPITA/actions/runs/43494256052). SST diagnostics now expose the selected ERDDAP endpoint. Only the live production pull remains before closing this resilience milestone.


## Active milestone: South Florida species profile accuracy
**Status:** batch 1 committed on 2026-11-14. Updated black grouper, great barracuda, gray/mangrove snapper and yellowtail snapper profiles and regional regulation summaries using FWC, NOAA Fisheries, NPS and regional fisheries references.

Next:
1. Continue species-by-species review, prioritizing generic or weakly sourced records.
2. Keep Atlantic/Gulf, state/federal, Monroe County and Biscayne National Park rules distinct.
3. Preserve unknowns and mark unsupported numeric biology as provisional rather than inventing precision.
4. Run `python scripts/validate_species.py` and focused/full tests at the next authorized validation checkpoint; no NOAA ingestion workflow is required for this work.
5. Do not change prediction weights or active scoring factors without separate evidence and explicit review.


## Species profile accuracy milestone | progress update 2026-11-14
**Completed:** 10 South Florida species records across two batches: black grouper, great barracuda, mangrove snapper, yellowtail snapper, common snook, Atlantic tarpon, Permit, bonefish, hogfish and mutton snapper. Biology, habitat, life history and regional harvest guidance were reviewed against FWC, NOAA/Florida Museum and relevant research sources. Unsupported numeric habitat preferences are labelled provisional; scoring configuration remains unchanged.

**Next:** continue with unreviewed South Florida species, prioritizing generic/placeholder regulations and weak biological evidence. Maintain a reviewed-species list in `docs/PROGRESS_LOG.md` and do not repeat completed records. Run the species audit and relevant tests at a dedicated validation checkpoint. This work remains independent of the paused NOAA ingestion troubleshooting.


## Species catalog audit | 2026-11-14

**Status:** static audit of all 130 species profiles completed. See [full audit report](SPECIES_CATALOG_AUDIT_2026-11-14.md).

Key findings:
- 130 profiles parsed; 105 grid models and 25 site models.
- No unsupported active parameter/kind combinations, unknown registry parameters, duplicate factor parameters within profiles, or active weight overflow found in the static cross-check.
- Twelve profiles have 33 active provisional/estimated/unsourced factors; eight active factors lack source references.
- 23 of 25 site models are temperature-only, with one active SST factor.
- Confidence calculation does not incorporate active biological evidence status.
- Grid and site scorers have different missing `required` / `gate` semantics.
- The existing validator needs additional checks for coverage bounds, category maps, evidence diagnostics, and flag behavior.

### Next acceptance criteria
1. Extend the species validator and tests without changing prediction scoring semantics.
2. Validate `min_coverage` bounds, category map values/keys, and required/gate combinations against both engines.
3. Add an evidence-aware confidence diagnostic and agree on the policy before changing user-facing confidence.
4. Explicitly label the 23 one-factor site models as temperature-only pilots; expand only with evidence-backed site inputs.
5. Run the species validator and focused tests from a local checkout or authorized non-NOAA test path.
6. Keep NOAA ingestion/source troubleshooting paused until explicit clearance.

**Audit boundary:** no NOAA endpoint, data workflow, prediction weight, threshold, or scoring behavior was changed or tested.


## Species validator follow-up | 2026-11-14

**Implementation committed and validated on 2026-11-14.** Full Python suite: **272 passed, 0 failed, 115 warnings**. Species validator: **130 profiles parsed, 130 structurally valid, 0 active compatibility issues, 0 validator errors**. See [run #43622006765](https://github.com/markeetox/LUPITA/actions/runs/43622006765) and the [full audit](SPECIES_CATALOG_AUDIT_2026-11-14.md).**

- Validate coverage thresholds, category maps, and factor flags.
- Explicitly report model-specific `required` / `gate` behavior.
- Report active evidence risk separately from environmental coverage.
- Label one-factor SST-only site models as temperature-only pilots in audit output.
- Run the full test suite and species validator on main whenever species profiles or the parameter registry change; publish audit reports as workflow artifacts.
- Review [proposed confidence policy](SPECIES_MODEL_CONFIDENCE_POLICY.md) before changing user-facing confidence. No prediction scoring or confidence output is changed yet.
- NOAA ingestion/source troubleshooting remains paused pending explicit clearance.


## Active factor evidence review | 2026-11-14

Eight active factors across six profiles previously lacked factor-level source references. They now have sources and explicit caveats. All remain `provisional`; no numeric values, weights, activation flags, or scoring behavior changed. See [Active Factor Evidence Review](ACTIVE_FACTOR_EVIDENCE_REVIEW_2026-11-14.md).

**Validated:** final full suite passed (272 passed, 0 failed, 115 warnings) and the species audit completed successfully on [run #43622573953](https://github.com/markeetox/LUPITA/actions/runs/43622573953). All eight reviewed active factors have source references but remain provisional. **Next:** review and approve the proposed evidence-aware confidence policy before making user-facing confidence changes. NOAA ingestion remains paused.


## Category-map scorer contract | 2026-11-14

**Status:** code and regression tests committed; CI pending.

- Align grid category scoring with the validator's accepted map-only configuration and the site scorer.
- Preserve preferred-list-only scoring.
- Keep missing grid values as NaN and unmapped categories at score 0 when an explicit map exists.
- Validate with the automatic Python suite before considering the fix complete.
- No NOAA work or biological profile changes are part of this item.


## Named-site model quality | 2026-11-15

**Status:** static triage completed; validator improvements and tests committed; CI pending.

1. Inspect updated full catalog audit for generic homepage-only source references and active placeholder factors.
2. Review the 20 homepage-only SST factors species by species; only retain `sourced` when a specific reference supports the configured biological claim.
3. Keep bonefish, great barracuda, and Permit SST bands provisional pending direct species-specific evidence.
4. Review snook/tarpon structure-kind scoring across inlet, cut, channel-bridge, and flat sites; the validator now reports unreachable preferred categories and allowed kinds that receive the fallback zero score.
5. The validator now blocks active `distance_to_inlet` use until a real input is implemented and tested.
6. Assess tide-station distance/local-regime suitability without changing NOAA ingestion during the current pause.

Full findings: [Named-site model triage](SITE_MODEL_TRIAGE_2026-11-15.md). NOAA remains paused.


## Production refresh recovery | 2026-11-15

**Latest inspected run:** [Pull Ocean Data #211](https://github.com/markeetox/LUPITA/actions/runs/43664658831). The scheduled run on `main` completed the full test step, catalog, pipeline, and publication to `data`. Predictions refreshed from the current run with no recorded errors or critical issues.

**Health is degraded, not fully healthy:** SST was delayed at 40.8h (warning threshold 36h, stale threshold 72h); chlorophyll was 61.8h old with 15.8% valid source coverage; HF Radar was 5.8h old but covered only 0.93% of its South Florida query window (94/10,101 cells). Stale altimetry (1,153.8h) was correctly excluded from current vectors. Other inspected layers, including buoy observations, ETOPO, reef structure, benthic habitat and closures, loaded.

### Next acceptance checks
1. Compare SST freshness across subsequent scheduled runs before calibrating its provisional thresholds.
2. Investigate HF Radar's very low regional valid-cell coverage; do not interpret successful retrieval as adequate coverage.
3. Continue tracking chlorophyll valid fraction and scene age; retain cloud/missing cells as unknown.
4. Keep stale altimetry excluded from current vectors until a timestamp-qualified observation is available.
5. Do not change prediction weights, species biology, or scoring gates based on this one run.

The NOAA ingestion pause is cleared for normal scheduled operation and explicitly authorized checks. No additional run was triggered during this inspection.


## HF Radar spatial coverage investigation | 2026-11-15

**Status:** first-pass diagnosis complete; source comparison remains open. No source/configuration change or ingestion run was performed.

- Production #211: `ucsdHfrE2` was fresh (5.79h) but yielded 94 valid aligned vectors from 10,101 target cells in the South Florida request window (0.9306%). Raw source-grid valid fraction was 0.9059%, so the initial evidence points to limited upstream valid spatial footprint rather than substantial loss during alignment.
- The 2 km HFR product is derived from coastal radar radial measurements; its rectangular geographic bounds do not imply continuous coverage throughout the box. Treat HFR as a coastal observation layer, not a broad-area ocean-current field.
- NOAA's 6 km hourly product `ucsdHfrE6` is available and should be compared with the 2 km product. NOAA's THREDDS catalog also lists 1 km, 2 km, and 6 km East/Gulf Coast hourly products. Compare exact same time/window and retain valid-vector coverage, observation timestamp, and quality fields.
- Do not promote a coarser product simply because its grid is coarser; it must demonstrate better useful coverage and acceptable quality in the intended South Florida fishing areas.
- Stale satellite altimetry remains excluded from current-vector filling. Keep Gulf Stream-edge context separate from nearshore observed-current coverage.

**Next:** read-only comparison of 1 km/2 km/6 km product availability and a controlled same-window data-quality comparison when explicitly authorized. Evaluate a timestamped broad-area model-current product separately. No prediction weights, biology, or scoring gates change during this work.

Validation: Python CI [run #462](https://github.com/markeetox/LUPITA/actions/runs/43669158015), **279 passed, 0 failed, 115 warnings**.


### HFR resolution comparison | metadata reconnaissance 2026-11-15

NOAA metadata lists East/Gulf Coast hourly products at 1 km (`ucsdHfrE1`), 2 km (`ucsdHfrE2`) and 6 km (`ucsdHfrE6`). Latest catalog observation times in the inspected snapshots were 2026-11-13 10:00Z, 2026-11-13 04:00Z and 2026-11-14 05:00Z respectively. These unequal timestamps cannot support a coverage ranking. The products also represent nominal depths of approximately 0.5 m, 1.0 m and 2.4 m, so resolution changes also change the measured surface layer.

**Still required:** retrieve exact common-time bounded u/v and quality subsets over 24.0-28.5°N, 83.5-78.0°W; compute paired-vector valid coverage and inspect spatial distribution. The current research environment exposed metadata but could not retrieve those griddap subsets, so no resolution is recommended yet. Production source configuration remains unchanged.

See [Progress Log](PROGRESS_LOG.md) for detailed caveats and NOAA links.


## HF Radar product comparison | first result and next validation | 2026-11-15

The read-only comparison utility and manual workflow are implemented. First same-time comparison [run #43727859776](https://github.com/markeetox/LUPITA/actions/runs/43727859776) succeeded; its [artifact](https://github.com/markeetox/LUPITA/actions/runs/43727859776/artifacts/14166714348) was retrieved.

**First result at 2026-11-13T04:00:00Z:** 1 km returned 0 valid paired vectors; 2 km returned 1,640/71,535 (2.293%); 6 km returned 753/7,980 (9.436%). Approximate subregion coverage for 2 km vs 6 km was Keys 0% vs 0.337%, Biscayne Bay 10.732% vs 24.554%, and offshore 5.701% vs 10.811%. Median HDOP was 0.56 for 2 km and 0.30 for 6 km; median radial counts were 35 and 100 respectively. These are descriptive results, not an accuracy verdict.

**Important limitations:** native-grid fractions include all cells in each rectangular bounding grid, including areas with no radar coverage. They are not ocean-area coverage estimates. Products represent different depths (about 0.5/1.0/2.4 m), so they are not interchangeable. The 1 km zero result needs another common timestamp before it can be treated as a persistent limitation.

**Diagnostic correction:** the first report's half-degree occupied-tile denominator varied with product coordinate edges. Commit 0ad8726 corrected this to a fixed shared set of bins across the requested region; commit 57fe6d7 added a regression test. The existing artifact predates this correction, so rerun the manual workflow before using tile occupancy as a cross-product comparison.

**Next acceptance checks:**
1. Verify the new shared-bin calculation in the next artifact.
2. Run a second exact common timestamp supported by all three products to test whether 1 km remains empty and whether the 2 km/6 km pattern persists.
3. Evaluate a shared ocean-only mask/coastline denominator before making cross-product area-coverage claims.
4. Review spatial distribution and HDOP/site/radial diagnostics together; do not create hard quality thresholds from one snapshot.
5. Keep production source selection unchanged until results across more than one timestamp are reviewed and a separate decision is made.

The manual workflow remains read-only and separate from Pull Ocean Data. No ingestion, source configuration, production data, biology, scoring, or prediction weights changed.
