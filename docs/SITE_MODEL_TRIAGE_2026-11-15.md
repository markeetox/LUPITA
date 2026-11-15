# LUPITA named-site model triage

**Date:** 2026-11-15  
**Branch:** `main`  
**Scope:** static review of all 25 `model: sites` profiles, site scoring inputs in `pipeline/sites.py`, and evidence-reference validation.  
**Operational boundary:** no NOAA endpoints, data ingestion workflows, production refreshes, scoring weights, or species factor values were changed.

## Executive result

The 25 named-site profiles split into:
- **23 temperature-only pilots:** one active `sst_c` factor each.
- **2 multi-factor models:** common snook and Atlantic tarpon, with five active factors each.

The 23 one-factor models are not equivalent in evidence quality:
- **20** mark their active SST factor `sourced`, but cite only the generic NOAA Fisheries homepage (`https://www.fisheries.noaa.gov/`). That is not a traceable species page, study, dataset, or temperature-preference source.
- **3** explicitly remain provisional: bonefish, great barracuda, and Permit.

The earlier validator treated any non-empty URL as usable evidence metadata. That allowed generic homepages to inflate sourced-weight accounting. This pass corrects that diagnostic gap. It does not prove that every non-homepage source is scientifically adequate; source presence and source quality remain separate questions.

## 23 temperature-only site pilots

### Provisional South Florida priorities

| Species | Configured SST range | Configured ideal | Evidence limitation |
|---|---:|---:|---|
| Bonefish | 20–35 °C | 25–31 °C | Bahamas adult thermal-performance findings are not a South Florida habitat-preference curve; configured band remains provisional. |
| Great barracuda | 20–32 °C | 24–30 °C | Cited FWC species profile does not validate the configured numeric thermal band. |
| Permit | 20–34 °C | 24–30 °C | FishBase's 23.2–28.0 °C estimate is model-derived; cited telemetry concerns habitat use/seasonal occupancy, not a validated thermal-preference curve. |

These three profiles should remain explicitly provisional. No numeric range, weight, active flag, gate, or confidence output was changed.

### Homepage-only source references

The following 20 active SST factors currently carry `value_status: sourced` but cite only the generic NOAA Fisheries homepage rather than a traceable species-specific resource:

American shad, Atlantic croaker, blacktip shark, bluefish, bull shark, false albacore, ladyfish, lane snapper, scup, Spanish mackerel, spinner shark, spot, spotted seatrout, striped bass, summer flounder, tautog, tripletail, weakfish, white grunt, and winter flounder.

The configured temperature bands should not be treated as independently validated merely because a homepage URL is present. Their source status requires species-by-species review before these profiles are described as evidence-backed temperature models.

## Two multi-factor site models

### Common snook

Five active factors:
- SST (partly sourced)
- structure type (sourced)
- tide stage (provisional)
- time of day (provisional)
- spawning season (sourced)

The structure factor maps only `inlet` to a positive score, while the profile allows `inlet`, `cut`, `channel_bridge`, and `flat` site kinds. The scorer uses the site's `kind` as the structure value. Consequently, non-inlet site kinds currently receive zero for this factor. This may be an intentional inlet preference, but it should be made explicit and reviewed against the intended role of each site kind. The profile's preferred list also includes habitat categories that the current named-site catalog does not directly supply. The validator now warns about both unreachable preferred categories and allowed site kinds that fall through to the default zero score.

### Atlantic tarpon

Five active factors:
- SST (partly sourced)
- season presence (partly sourced)
- tide stage (provisional)
- structure type (partly sourced)
- time of day (provisional)

The structure factor likewise awards a positive score only to `inlet`, although the profile also permits cuts, channel bridges, and flats. The validator now reports those unmapped site kinds. The time-of-day evidence is a small juvenile telemetry study outside South Florida; the profile correctly retains this factor as provisional and does not treat it as validated adult feeding preference.

## Site-engine input capabilities and limitations

The site engine currently exposes:
- `sst_c`: nearest qualifying buoy within 40 km, otherwise a nearby gridded SST value within 8 km.
- `tide_stage`: nearest usable tide station within 120 km.
- `time_of_day`: astronomical light phase computed from date and site coordinates.
- `spawning_season` / `season_presence`: calendar-month lookup.
- `structure_type`: the site's static `kind`.
- `distance_to_inlet`: currently a placeholder that returns constant `0.0` for every site.

The constant distance placeholder is especially important: activating it would make every site appear to be at zero distance from an inlet. The validator now rejects an active use as an error, marks the model incompatible, and counts its active weight as uncertain if a site profile attempts to activate it. It must not be used until a real distance dataset/calculation is implemented and tested.

The 120 km tide-station search radius is also broad. A nearest station can be far from a site or represent a different local tidal regime. A future site-quality review should expose station distance and reject or qualify inappropriate matches before treating the tide value as locally representative. This review does not change tide retrieval or any NOAA-related workflow.

## Validator improvements committed

- A bare website homepage no longer counts as a specific source reference for active evidence accounting.
- The validator emits `generic_source_reference` when a factor cites only a generic homepage.
- Homepage URLs with query strings or fragments remain generic; adding tracking parameters does not turn a homepage into a scientific citation.
- Active factors whose only source is a homepage count as uncertain for evidence-risk diagnostics.
- A site `distance_to_inlet` factor is an error if active because the current input is a constant-zero placeholder; the model is marked incompatible and its active weight is counted as uncertain.
- Regression tests cover generic homepages, specific species/source pages, query-string homepages, the constant-distance placeholder, and unreachable/unmapped site structure categories.

These are validator/reporting changes only. They do not alter scoring, prediction confidence, source ingestion, species values, or weights.

## Recommended sequence

1. Run and inspect the new full Python suite and catalog audit. Record the actual warning count and the number of generic homepage-only factors across the full 130-profile catalog.
2. Review the 20 homepage-only SST factors species by species. Replace references only with sources that directly support the relevant species and the claim being made; otherwise mark the factor provisional or needs-source.
3. Keep bonefish, great barracuda, and Permit SST bands provisional until species-specific evidence supports the numeric values.
4. Review snook/tarpon structure-kind mapping and explain whether non-inlet site kinds are intentionally scored zero.
5. Keep `distance_to_inlet` inactive until a real, independently testable input exists.
6. Review tide-station distance and local-regime suitability as a separate site-data-quality task.
7. Do not expand active factors merely to increase model complexity. Each factor must have both a supported engine input and species-specific biological justification.

## Explicit non-actions

- No NOAA endpoint was contacted.
- No Pull Ocean Data or other data-ingestion workflow was run.
- No NOAA source configuration or operational threshold was changed.
- No species range, ideal band, factor weight, active flag, gate, required flag, or user-facing confidence output was changed.
