# LUPITA engineering roadmap

**Last updated:** 2026-11-17 | **Code:** `main` | **Generated-data export:** `data` only

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


## HF Radar comparison | corrected run completed | 2026-11-15

The corrected shared-bin comparison completed successfully: [workflow #43731442828](https://github.com/markeetox/LUPITA/actions/runs/43731442828), [artifact 14168636243](https://github.com/markeetox/LUPITA/actions/runs/43731442828/artifacts/14168636243). All three products returned the exact requested time `2026-11-13T04:00:00Z`.

| Product | Valid paired vectors | Native-grid fraction | Shared half-degree bins |
|---|---:|---:|---:|
| 1 km | 0 / 285,069 | 0.000% | 0 / 99 |
| 2 km | 1,640 / 71,535 | 2.293% | 6 / 99 |
| 6 km | 753 / 7,980 | 9.436% | 19 / 99 |

The 6 km product leads on apparent availability in this snapshot. It also has higher reported median radial count (100 vs 35) and lower median HDOP (0.30 vs 0.56) than 2 km. Approximate Keys coverage remains negligible for all products. Native-grid percentages are not ocean-area coverage; each product has a different grid and representative depth.

**Remaining acceptance checks:**
1. Run a second exact common timestamp to test whether the 1 km zero result and 2 km/6 km pattern persist.
2. Compare a shared ocean-only mask or coastline-aware denominator before interpreting coverage as area.
3. Review the intended fishing-area footprint, spatial clustering, and quality diagnostics together.
4. Keep production source selection and all prediction/scoring behavior unchanged until multi-time evidence is reviewed and separately approved.

The comparison workflow is read-only and does not touch Pull Ocean Data or the `data` branch.


## Production source health update | 2026-11-16

Scheduled [Pull Ocean Data #43840037456](https://github.com/markeetox/LUPITA/actions/runs/43840037456) completed tests, catalog, prediction generation and publication. Prediction snapshot refreshed, but health is degraded:

- SST is delayed at 48.5h (provisional warning 36h).
- Chlorophyll is 69.5h old and technically within its 72h warning limit, but only 7.94% of the source grid is valid; gap-filled input remains disabled.
- HF Radar `ucsdHfrE2` failed on the Upwell fallback with HTTP 404 / unknown dataset ID. No current vectors were available.
- Altimetry is about 1,185.5h old and remains correctly excluded from current-vector use.

**Next source-health checks:** verify the CoastWatch and Upwell dataset catalogs/endpoints read-only; establish whether the 404 is host-specific, catalog availability, or a dataset identifier issue. Do not change endpoints, production source configuration, stale-data rules, or scoring until the cause is established and explicitly reviewed.

**HF Radar comparison remains open:** corrected common-time snapshot at `2026-11-13T04:00:00Z` favors 6 km availability in that one sample. Run a second exact common timestamp before any source-selection recommendation. The manual workflow has not yet been rerun for the second timestamp.


## HF Radar comparison update | 2026-11-16

Second timestamp `2026-11-12T04:00:00Z` produced a partial report in [workflow #43893775875](https://github.com/markeetox/LUPITA/actions/runs/43893775875): 1 km 0/285,069 vectors (0.000%, 0/99 shared tiles); 2 km 1,201/71,535 (1.679%, 8/99 tiles; median HDOP 0.46, sites 2, radials 40); 6 km unavailable due HTTP 404. The workflow correctly remained failed because a three-product comparison was incomplete, while still uploading its partial artifact.

The 1 km zero-vector result has repeated across two timestamps. The 2 km fraction is lower at the second timestamp than the first. The 6 km product has no second-time measurement, so the first timestamp's apparent advantage cannot be treated as a robust ranking.

**Next acceptance checks:**
1. Verify current `ucsdHfrE6` dataset metadata and endpoint behavior read-only, including redirect destinations and whether the dataset is currently served.
2. Keep 1 km, 2 km and 6 km production selection unchanged until retrieval is stable and comparable multi-time evidence exists.
3. Consider a common ocean-only mask only after the retrieval problem is understood.

The report-formatting SyntaxWarnings were fixed in commits `cd3fbf0` and `dd38768`; no retrieval or production behavior changed.


### 2026-11-16 | 6 km timestamp-range clarification

The 6 km dataset ID is still present on Upwell. Its live metadata time range ends at 2026-11-10 08:00Z, so the failed November 12 04:00Z request was outside the available time axis. This is not evidence that the dataset was removed. See [Upwell 6 km metadata](https://upwell.pfeg.noaa.gov/erddap/griddap/ucsdHfrE6.html).

Next comparison candidate is `2026-11-10T04:00:00Z`; run only after confirming the exact time is returned by all three products. A candidate timestamp is not itself a successful comparison. Production source configuration remains unchanged.


### HF Radar retrieval and test-fixture update | 2026-11-16

The retry [#43894680887](https://github.com/markeetox/LUPITA/actions/runs/43894680887) at `2026-11-10T04:00:00Z` returned 1 km 0/285,069, 2 km 1,614/71,535 (2.256%, 10/99 shared tiles), and 6 km HTTP 404. A newer live Upwell metadata page reports 6 km observations through 2026-11-16 13:00Z, so the requested Nov 10 time was within the currently published range. The previous Nov 10 endpoint snapshot was stale. The 404 root cause remains unresolved.

The comparison utility now captures redirect chains and response excerpts for the next diagnostic attempt. Production source selection is unchanged.

Two CI failures were caused by hard-coded Nov 13 altimetry test data aging past the existing 72-hour eligibility threshold. Tests now use a recent relative timestamp for eligible fallback cases and a deliberately stale timestamp for stale cases; production logic is unchanged.

**Next:** confirm Python CI passes, then rerun one read-only HFR comparison to capture the 6 km redirect chain and response body. Do not change production endpoints or source selection until the failure is explained.


The relative-time test fixture was corrected once more in commit `afb59bc` so the stale-only case converts the generated `ALT_TIME` rather than the former fixed date. Full CI [#43897319861](https://github.com/markeetox/LUPITA/actions/runs/43897319861) is pending; confirm before considering the test cleanup complete.


Validation complete: Python CI [#43897319861](https://github.com/markeetox/LUPITA/actions/runs/43897319861) passed **286 tests, 0 failures, 115 warnings** on commit `afb59bc7ae6e23f48b05f3a6c700ff86dbdd5ded`; species profile audit and artifact upload succeeded. Next step remains a read-only comparison rerun to capture the 6 km endpoint redirect chain and response body.


## HF Radar comparison paused | NOAA ERDDAP request blacklist | 2026-11-16

The latest comparison [run #43935416361](https://github.com/markeetox/LUPITA/actions/runs/43935416361), at the previously successful exact timestamp `2026-11-13T04:00:00Z`, returned HTTP 403 for all three HFR products on both CoastWatch and Upwell. The response body explicitly reports that the requesting IP address is on NOAA ERDDAP's request blacklist. [Artifact 14258784849](https://github.com/markeetox/LUPITA/actions/runs/43935416361/artifacts/14258784849) confirms this across 1 km, 2 km, and 6 km.

**Decision:** pause further manual comparison runs from the same GitHub-hosted runner. Do not interpret this as a dataset-specific failure or a coverage result. Do not change production HFR source selection, endpoints, or ingestion behavior. Resume only when NOAA access is restored or an approved low-rate retrieval path is available.

## Species model-to-data audit | 2026-11-16

Completed static audit: [MODEL_TO_DATA_AUDIT_2026-11-16.md](MODEL_TO_DATA_AUDIT_2026-11-16.md). The immediate engineering priority is to make existing contracts executable as tests: grid/site missing, `required`, `gate`, coverage, normalization, and factor-to-layer dispatch. Keep environmental coverage, source freshness, and biological evidence quality separate in prediction explanations. Do not activate the site `distance_to_inlet` placeholder or expand models with unsupported factors. No scoring or biology changes were made. HF Radar product comparison remains paused while the GitHub runner is blocked by NOAA ERDDAP.

## Runtime model/data contract tests | 2026-11-16

Completed regression coverage for grid/site missing-data semantics and active profile factor dispatch/input contracts. See [MODEL_TO_DATA_AUDIT_2026-11-16.md](MODEL_TO_DATA_AUDIT_2026-11-16.md). Final test commit `909fad3` passed CI and species-profile audit. Next milestone: build prediction-level diagnostics that report factor availability, environmental coverage, source freshness, and evidence quality separately. Keep scoring semantics unchanged until a separately reviewed design is approved.


## Prediction-level environmental source lineage | 2026-11-16

**Completed:** prediction diagnostics now carry factor-level environmental source lineage for all active species factors. Grid and named-site factors identify source type, availability at the prediction, source/layer status, dataset and observation metadata, and freshness when operational thresholds exist. Actual species-profile source references are preserved and exposed through API v1.

**Validation:** [Python CI #43944587159](https://github.com/markeetox/LUPITA/actions/runs/43944587159) passed **304 tests, 0 failures, 115 warnings**. The species profile audit and artifact upload succeeded. Regression coverage includes source map completeness across all active factors, composite-current limitations, satellite-altimetry attribution for Gulf Stream edge, primary/gap-filled chlorophyll, NDBC water-temperature observation timestamps, tide station/prediction metadata, and unknown/unconfigured freshness.

**Boundaries preserved:** no scores, confidence labels, biological assumptions, weights, source selection, missing-data semantics, ingestion, or data publication changed. NOAA ERDDAP HFR comparison remains paused due to the runner IP blacklist.

**Next milestone: evidence-quality summary.** Build a transparent per-factor classification from the actual profile evidence metadata and references. It must distinguish specific, relevant support from generic/homepage citations, provisional assumptions, and unsupported factors. It must not infer scientific support from URL count, and it must remain separate from source freshness and environmental coverage. Keep score/confidence behavior unchanged.


## Per-prediction biological evidence diagnostics | 2026-11-16

**Completed:** predictions now expose per-factor `evidence_diagnostics` and per-spot `evidence_summary`. Declared status and reference quality are separate. Specific citations with a `sourced` declaration are still labeled unverified; homepage-only references do not masquerade as species-specific evidence. Factor notes and per-reference classifications are retained through API v1.

The summary aggregates configured active-factor weight by evidence status and reference quality. It is diagnostic only, not a probability or calibrated scientific-quality score. The proposed confidence policy remains inactive.

**Validation:** [Python CI #43945487955](https://github.com/markeetox/LUPITA/actions/runs/43945487955) passed **307 tests, 0 failures, 115 warnings**. Species audit and artifact upload succeeded.

**Boundaries preserved:** no score, confidence, species status, numeric band, weight, active flag, gate, minimum coverage, source selection, ingestion, or publication behavior changed.

**Next milestone: source-by-source biological evidence review.** Prioritize the 20 homepage-only named-site SST references and the 12 profiles with elevated active evidence risk. Verify whether each citation actually supports the configured claim for the relevant species, population, life stage, region, and numeric range. Only then decide whether to replace a reference, keep a factor provisional/partly sourced, mark it weak, or leave it as needs-source.


## Source-by-source review of 20 named-site SST factors | 2026-11-16

**Completed:** reviewed all 20 homepage-only named-site SST factors against species-specific fisheries, research, and regional sources. Full findings: `docs/NAMED_SITE_SST_EVIDENCE_REVIEW_2026-11-16.md`.

**Result:** Spanish mackerel is the only profile in this batch whose cited evidence closely supports both its configured outer range and ideal interval. Eleven profiles have partial support but important limitations. Eight do not yet have evidence supporting their configured numeric band. The report separates observed occurrence, migration cues, spawning/juvenile temperatures, model-derived associations, and adult thermal preference rather than treating them as interchangeable.

**Next:** owner review of recommended evidence statuses, then update approved references and value notes. Do not change numeric ranges, ideal bands, weights, gates, required flags, or scoring in this step.


### Apply reviewed named-site SST evidence metadata | completed 2026-11-16

Completed the owner-approved metadata-only update across all 20 named-site SST profiles. Specific source references and conservative evidence statuses are now recorded, with factor notes explaining limitations. Classification: 1 sourced, 11 partly sourced, 5 provisional, 3 needs-source. Next work should prioritize a separate evidence search for the three needs-source profiles and regional/life-stage validation for provisional profiles. Do not adjust numeric bands, weights, gates, or scoring without a separate evidence review and approval. Details: [named-site SST evidence review](NAMED_SITE_SST_EVIDENCE_REVIEW_2026-11-16.md).


### Named-site SST evidence follow-up | completed 2026-11-16

Reviewed the final three needs-source profiles. All now have specific references and `partly_sourced` status, with notes distinguishing occurrence, migration, bottom temperature, and model-derived estimates from validated SST preference. Next priority: resolve geographic/species-identity caveats for spot and weakfish, then assess the five remaining provisional profiles. Do not adjust numeric bands or model behavior without a separate review and approval. See [evidence review](NAMED_SITE_SST_EVIDENCE_REVIEW_2026-11-16.md).


## Active milestone: all-species biological evidence review | 2026-11-17

**Inventory complete; source-by-source review queued.** The current catalog has 130 profiles: 105 grid and 25 site models; 23 temperature-only site pilots, 27 other single-factor models, and 80 multi-factor models. CI species audit #43952010312 parsed and validated all 130 profiles with zero compatibility issues. It identified 64 elevated-risk, 14 partial-risk, and 52 documented-by-current-metadata profiles. The combined active uncertain weight is 37.4 and is not a probability. There are 96 generic-homepage findings across 48 profiles, 3 missing factor-source findings across sailfish and tarpon, and 27 grid `required`-flag warnings.

Sequence:
1. Review bonefish, great barracuda, and Permit, the three remaining temperature-only site pilots.
2. Review all 27 other single-factor models; these are currently all elevated active-evidence risk.
3. Review the 80 multi-factor models by factor family; prioritize the 29 elevated-risk profiles.
4. Audit timing and profile-level biological narratives separately from environmental factor evidence.
5. Apply only approved source/status/note updates and validate after each coherent batch.

Use [SPECIES_EVIDENCE_AUDIT_2026-11-17.md](SPECIES_EVIDENCE_AUDIT_2026-11-17.md) as the master scope and interpretation record. Do not change numeric biology, weights, active flags, gates, required flags, scoring, confidence, source selection, ingestion, or publication during evidence discovery. A specific URL or `sourced` declaration is not proof of claim fit.


### Batch A research complete | 2026-11-17

Reviewed bonefish, great barracuda, and Permit, the three remaining temperature-only site pilots. Recommended great barracuda moves to `partly_sourced` with N=2 telemetry caveats; bonefish and Permit remain `provisional` because available evidence does not validate their numeric SST bands. Research findings and sources are recorded in the master evidence audit. No species JSON or numeric/model setting changed. Apply metadata only after review.

Next: Batch B, the 27 other single-factor profiles, prioritized by gate/required semantics and traceability of their active factor sources.


### Batch B research complete | 2026-11-17

Reviewed the 27 other single-factor grid SST profiles. Research recommendations: 20 partly_sourced, 3 provisional, and 4 needs_source for the active SST claim. The most important finding is that several deep demersal species have bottom-temperature evidence while the model gates on satellite SST. This is a model-to-data design issue to assess separately; no SST values or scoring were changed. Full review is in the master evidence audit.

Next: review metadata recommendations for Batches A and B, then continue with the 80 multi-factor profiles grouped by parameter family and elevated active-evidence risk. Start with factors whose source references are generic or absent and whose weights/gates materially affect eligibility.


## 2026-11-17 | Multi-factor evidence review underway

Batch C has started. Four elevated-risk profiles (African pompano, Almaco jack, black grouper, black sea bass) have been reviewed and their active factor source/status/note metadata updated. Next priority is the remaining elevated-risk multi-factor profiles, grouped by ecological factor family. Preserve all numeric ranges, category maps, weights, gates, required flags, scoring, and confidence behavior until separately supported and approved. See SPECIES_EVIDENCE_AUDIT_2026-11-17.md.


## 2026-11-17 | Multi-factor evidence review update

Eight elevated-risk multi-factor profiles are now reviewed and metadata-updated: African pompano, Almaco jack, black grouper, black sea bass, cubera snapper, gag grouper, red grouper, and red snapper. Continue with the remaining elevated-risk profiles, grouped by habitat/factor family. Preserve all numerical model settings and runtime behavior during evidence review. See SPECIES_EVIDENCE_AUDIT_2026-11-17.md.


## 2026-11-17 | Multi-factor evidence review update

Twelve of the 29 elevated-risk multi-factor profiles have now been reviewed across 36 active factors. Seventeen elevated-risk multi-factor profiles remain, plus 51 other multi-factor profiles. Continue with the remaining high-risk models by ecological factor family, with special attention to SST-vs-bottom-temperature mismatches and proxies that do not match the runtime variable. See SPECIES_EVIDENCE_AUDIT_2026-11-17.md.


## 2026-11-17 | Multi-factor evidence review update

Twelve of the 29 elevated-risk multi-factor profiles have now been reviewed across 36 active factors. Seventeen elevated-risk multi-factor profiles remain, plus 51 other multi-factor profiles. Continue with the remaining high-risk models by ecological factor family, with special attention to SST-vs-bottom-temperature mismatches and proxies that do not match the runtime variable. See SPECIES_EVIDENCE_AUDIT_2026-11-17.md.


## 2026-11-17 | Current all-species evidence review status

Twelve of 29 elevated-risk multi-factor profiles have been reviewed and updated across 36 active factors. Latest validator run #44123016856 passed for all 130 profiles. Current evidence-risk distribution is 55 elevated, 23 partial, 52 documented; combined uncertain active factor weight is 26.4. Remaining work: implement reviewed metadata for Batches A/B, complete the remaining 17 elevated-risk multi-factor profiles and nine partial-risk multi-factor profiles, then review the 51 documented multi-factor profiles and timing/profile narratives. Preserve numeric model settings and runtime behavior.


## 2026-11-17 | Pelagic species evidence review

Reviewed Atlantic blue marlin, Atlantic bluefin tuna, sailfish, and tarpon. Sixteen of the 29 elevated-risk multi-factor profiles have now received source-by-source review; continue with the remaining 13 elevated-risk models, then nine partial-risk and 51 documented multi-factor profiles. Maintain explicit separation between vertical fish dive depth and bathymetric seafloor depth. See SPECIES_EVIDENCE_AUDIT_2026-11-17.md.


## 2026-11-17 | Multi-factor evidence review progress

Twenty of the 29 originally elevated-risk multi-factor profiles have now been reviewed across 77 active factors. Nine elevated-risk multi-factor profiles remain, plus nine partial-risk and 51 documented multi-factor profiles. Continue with the remaining elevated-risk profiles, then review partial/documented profiles and timing/profile-level narratives. Preserve numerical settings and runtime behavior.


## 2026-11-17 | Batch A/B metadata updates applied

Completed metadata implementation for the three remaining temperature-only site pilots and all 27 other single-factor grid profiles. Batch B status distribution is 20 partly_sourced, 3 provisional, and 4 needs_source. All numeric settings and runtime behavior remain unchanged. CI validation: #44124511157. Continue Batch C high-risk multi-factor models after the validator refresh.



## 2026-11-17 | Batch C fourth multi-factor review

Reviewed Hogfish, Jack crevalle, King mackerel, and Red drum across 13 active factors. Continue with the remaining elevated-risk multi-factor profiles, then partial/documented models and timing/profile narratives. The exact remaining profile list will be reconciled against the refreshed validator artifact before the next batch. Preserve numeric settings and runtime behavior. See SPECIES_EVIDENCE_AUDIT_2026-11-17.md.


## 2026-11-17 | Batch C elevated-risk review complete

Completed source-by-source review of all 29 originally elevated-risk multi-factor profiles. The final five were Mahi-mahi, Mutton snapper, Sheepshead, Southern flounder, and Wahoo (26 active factors). Source/status/value-note metadata only; all numerical and runtime behavior remains unchanged.

Next: run/inspect the refreshed species-profile validator, then review remaining partial-risk and documented multi-factor profiles. Resolve the southern flounder South Florida distribution caveat separately before any model-scope or activation decision. See [SPECIES_EVIDENCE_AUDIT_2026-11-17.md](SPECIES_EVIDENCE_AUDIT_2026-11-17.md).


## 2026-11-17 | Validator checkpoint and next evidence queue

Batch C is complete and validated by CI #44127699186 (307 passed, 0 failed). The species audit reports 130 structurally valid profiles and zero compatibility issues. Current evidence risk: 30 elevated, 48 partial, 52 documented; multi-factor subset: 16 elevated, 13 partial, 51 documented. The previously elevated/partial multi-factor profiles have already received source-by-source review. Next focus is the 51 documented multi-factor profiles, verifying actual claim fit rather than treating the validator's documented category as scientific validation. No numerical or runtime changes.


## 2026-11-17 | Documented multi-factor review underway

The first five of 51 documented multi-factor profiles have been reviewed: Black rockfish, Blue rockfish, Bocaccio rockfish, Canary rockfish, and Copper rockfish (11 active factors). Source-reference presence was not treated as scientific validation; SST, bottom-temperature, life-stage and depth-proxy mismatches were recorded. Continue the remaining documented profiles by ecological/factor family. No numeric or runtime changes. See SPECIES_EVIDENCE_AUDIT_2026-11-17.md.


## 2026-11-17 | Documented Pacific nearshore review, batch 2

Reviewed Gopher rockfish, Kelp rockfish, Olive rockfish, Treefish, and Halfmoon (10 active factors). Species-specific habitat and depth sources support broad occurrence, but no reviewed source validated their numeric SST suitability bands. Those factors are now marked needs_source; depth remains partly_sourced with regional/life-stage caveats. Progress: 10/51 profiles, 21 active factors. No numeric or runtime changes.


## 2026-11-17 | Documented California coastal review, batch 3

Reviewed Kelp bass, California yellowtail, Giant sea bass, Opaleye, and Spotted sand bass (10 active factors). Added species-specific sources and conservative claim-fit notes. Numeric tolerance, model-derived preferred-temperature estimates, spawning temperature and SST preference are kept distinct. California yellowtail bathymetry is a weak proxy; Giant sea bass SST remains needs_source. Progress: 15/51 profiles, 31 active factors. No numeric or runtime changes.


## 2026-11-17 | Documented demersal review, batch 4

Reviewed California halibut, Pacific halibut, Petrale sole, Starry flounder, and Pacific cod (10 active factors). Added species-specific agency and research sources. Bottom-temperature records were not used to validate satellite SST; life-stage and seasonal depth differences were documented. Progress: 20/51 profiles, 41 active factors. No numeric or runtime changes.


## 2026-11-17 | Documented salmon thermal-habitat review

Reviewed Chinook, Coho, Chum, Pink and Sockeye (10 active factors). Species-specific North Pacific SST models indicate the configured bands are generally too warm; pink salmon has even/odd-year differences. Bathymetry is only a weak proxy for pelagic salmon and is not equivalent to fish vertical depth. Progress: 25/51 profiles, 51 active factors. No numeric or runtime changes.


## 2026-11-17 | Documented Pacific rocky-reef review, batch 5

Reviewed Lingcod, Cabezon, Kelp greenling, Ocean whitefish and Yelloweye rockfish (11 active factors). Added species-specific habitat/depth sources; SST bands lack numeric preference evidence. Depth and bottom-curvature support is partial, not a validated scoring curve. Progress: 30/51 profiles, 62 active factors. No numeric or runtime changes.


## 2026-11-17 | Documented elasmobranch/tuna review, batch 6

Reviewed Bat ray, Common thresher shark, Leopard shark, Soupfin shark, and Pacific bluefin tuna (10 active factors). Added species-specific sources and recorded vertical-depth versus bathymetry mismatches. Bat ray/soupfin SST remain needs_source; other thermal evidence is partial with region/size caveats. Progress: 35/51 profiles, 72 active factors. No numeric or runtime changes.


## 2026-11-17 | Documented pelagic review, batch 7

Reviewed Opah, Pacific barracuda, Pacific bonito, Pacific hake and Striped marlin (10 active factors). Added species-specific tagging and habitat sources. Flagged unresolved Pacific opah taxonomy; separated pelagic vertical depth from bathymetry. No numeric or runtime changes. Progress: 40/51 profiles, 82 active factors.


## 2026-11-17 | Documented California coastal review, batch 8

Reviewed Barred sand bass, Barred surfperch, Redtail surfperch, Rock greenling and White seabass (10 active factors). Added species-specific sources and conservative temperature/depth notes. Distinguished physiology, ambient fish-depth temperature and bottom-water temperature from preferred satellite SST. Progress: 45/51 profiles, 92 active factors. No numeric or runtime changes.


## 2026-11-17 | All documented multi-factor profiles reviewed

Completed all 51 documented multi-factor profiles across 105 active factors. Final batch included Dungeness crab, Sablefish, Steelhead, Vermilion rockfish, White sturgeon and Yellowtail snapper. Source metadata and evidence notes only; no numerical model or runtime behavior changed. Run a fresh validator and reconcile all remaining elevated/partial evidence and taxonomy/region open items before any model rebuild.


## 2026-11-17 | Transition from evidence review to model-rebuild planning

All 130 profiles have been source-reviewed. Final validator reports 68 elevated, 61 partial, 1 documented; 130 structurally valid, 0 compatibility issues, 0 validator errors. The 51 initially documented multi-factor profiles were reviewed across 105 active factors. Many were reclassified because source presence did not substantiate numeric preference curves or runtime proxy relationships.

Next work is to resolve scope/taxonomy first (Southern flounder, Pacific Opah, Dungeness crab, White sturgeon), then design a source/measurement plan for bottom temperature versus SST and bathymetry versus fish vertical depth. Only after those decisions should model rebuild candidates, numerical bands, factor weights or gates be considered. No such model changes were made.


## 2026-11-17 | Model-rebuild plan, Phase 0 underway

Started scope/identity before factor recalibration. Found 25 grid profiles without latitude bounds; missing `lat_range` means no latitude eligibility filter in the grid scorer. Corrected opah and Dungeness crab accepted taxonomic metadata. Flagged Southern flounder's discontinuous Florida distribution and White sturgeon's freshwater/estuarine scope. The next work is a source-backed geographic register, followed by measurement alignment (SST vs bottom temperature; seafloor depth vs fish vertical depth). No score, numeric band, weight, gate, active flag, or runtime change.

## 2026-11-17 | Phase 0 geographic source pass

Located traceable distribution sources for all 25 grid profiles missing latitude bounds. Do not translate textual endpoints into guessed coordinates; review stock splits, seasonal migration, island absences and disjoint distributions before choosing rectangular bounds or masks. See the geographic register in `docs/MODEL_REBUILD_PLAN_2026-11-17.md`. No model or runtime changes.


## 2026-11-17 | Phase 1 measurement alignment

Documented surface SST versus bottom temperature and ETOPO seafloor bathymetry versus fish vertical depth. Five demersal SST factors are not supported by the cited bottom-water evidence. Pelagic depth factors require scrutiny, especially where they are gates. Next: evaluate candidate bottom-temperature sources and a separate fish-vertical-depth variable. No model or source changes.


Priority correction: all five reviewed pelagic `depth_m` factors are active gates, including mahi-mahi, opah and steelhead. Review gate semantics before any model rebuild; no gates changed.


## 2026-11-17 | Bottom-temperature source evaluation

Copernicus Marine global physics forecast is the leading candidate for a bottom-temperature layer: 0.083° grid, 50 levels, daily sea-floor temperature `tob`, 10-day forecast. Keep research-only until coastal coverage, latency, and independent bottom observations are validated. Do not replace MUR SST or change species factors yet.


## 2026-11-17 | Copernicus bottom-temperature validation protocol

Confirmed daily `tob` sea-bottom potential temperature in the official Copernicus dataset documentation. Identified independent observation candidates across South Florida, Gulf, Atlantic, and Pacific regions, with important sensor-depth and geographic-coverage caveats. Added a read-only protocol covering data pairing, coastal coverage, freshness, and error metrics. No dataset sample has been downloaded yet and no accuracy result is claimed. Next: run a compact recent/historical subset pilot, inspect returned metadata and coastal wet-cell behavior, then match qualifying in-situ profiles. Do not add production ingestion or alter SST/species factors.
