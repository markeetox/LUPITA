# Active factor evidence review: six South Florida species

**Date:** 2026-11-14  
**Branch:** `main`  
**Scope:** eight active factors that previously had no factor-level source references, across six species.

## Executive result

All eight factors now have source references and explicit evidence notes. This does **not** mean all eight are validated. Each remains marked `provisional`; the numerical settings and scoring behavior are unchanged.

- 8 factors reviewed and given source references.
- 6 species updated.
- 0 numeric ranges, ideal ranges, weights, active flags, gates, or required flags changed.
- The evidence notes now distinguish direct species evidence from contextual, model-derived, age-specific, or geographically limited evidence.
- The validator will continue to flag these factors as active evidence uncertainty until their numerical settings are independently validated.

## Findings by species

### Blackfin tuna: 3 factors

**Factors:** `sst_gradient` (0.20), `chl_gradient` (0.15), `gulf_stream_edge` (0.15).

Sources added:
- Florida Museum species account: https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/blackfin-tuna/
- 2023 population-structure paper: https://academic.oup.com/icesjms/article/80/4/941/7058011
- FAO biological synopsis: https://www.fao.org/4/ap895e/ap895e.pdf

The sources support a warm-water, oceanic blackfin distribution and discuss relationships with plankton concentrations, upwelling/runoff, and the Florida Current. They do not establish a preferred SST-gradient magnitude, chlorophyll-gradient response, or preferred distance from the Gulf Stream edge. All three remain provisional ecological proxies. The user-facing reason text now says so explicitly.

### Bonefish: 1 factor

**Factor:** `sst_c` (0.35).

Sources added:
- Murchie et al. (2011), *Thermal biology of bonefish*: https://doi.org/10.1016/j.jtherbio.2010.10.005
- Nowell et al. (2015), *Swimming energetics and thermal ecology of adult bonefish*: https://doi.org/10.1007/s10641-015-0420-6

The adult Bahamas study measured performance optima around 26.7–28.0 °C and critical thermal limits. These are useful species-specific physiological findings, but they are not a South Florida habitat-preference curve and do not validate the configured 20–35 °C range or 25–31 °C ideal. The factor remains provisional.

### Hogfish: 1 factor

**Factor:** `sst_c` (0.35).

Context sources added:
- FWC species profile: https://myfwc.com/wildlifehabitats/profiles/saltwater/hogfish/
- FishBase species summary: https://www.fishbase.org/summary/1071

The reviewed species-account sources describe hogfish distribution and habitat but do not establish a species-specific thermal preference or tolerance band. No direct thermal study supporting the configured 22–30 °C range or 24–28 °C ideal was identified in this review. The values remain provisional; the explanation no longer describes them as a known comfortable range.

### Mutton snapper: 1 factor

**Factor:** `sst_c` (0.15).

Source added:
- Heidmann et al. (2021), *Home range characteristics and diel patterns in space use of mutton snapper*: https://doi.org/10.1186/s40317-021-00237-z

The St. Thomas adult telemetry study found no evidence that mutton snapper selected specific temperature ranges; tagged individuals used available temperatures equitably. This is important negative evidence. It does not support the configured 19–31 °C range or 22–29.5 °C ideal. The factor remains provisional and its explanation explicitly avoids calling the range a validated tolerance.

### Permit: 1 factor

**Factor:** `sst_c` (0.35).

Sources added:
- FishBase species summary: https://www.fishbase.se/country/CountrySpeciesSummary.php?c_code=660&genusname=Trachinotus&speciesname=falcatus
- Lower Florida Keys habitat telemetry paper: https://pubmed.ncbi.nlm.nih.gov/31823365/

FishBase reports a model-derived preferred-temperature estimate of 23.2–28.0 °C based on 624 cells. This is a model-based association, not a controlled thermal-preference experiment. The telemetry paper supports habitat use and seasonal reef occupancy, not the configured 20–34 °C screening range or 24–30 °C ideal. The factor remains provisional.

### Atlantic tarpon: 1 factor

**Factor:** `time_of_day` (0.10).

Source added:
- Duffing Romero et al. (2021), *Movement patterns of juvenile Atlantic tarpon*: https://doi.org/10.1186/s40317-021-00239-x

The St. Thomas study tracked four juvenile tarpon (80–95 cm fork length) and found greater daytime activity, crepuscular peaks, and distinct day/night space use. This does not establish adult feeding-time preference or validate the configured category scores for South Florida. The factor remains provisional, and its explanatory text now identifies the limitation.

## Decisions

1. Keep all eight factors active and retain their current ranges, ideal ranges, weights, and flags for compatibility.
2. Keep every reviewed factor marked `provisional`. Adding a contextual source is not the same as validating its numeric values.
3. Do not convert the current settings to `sourced` or `partly_sourced` merely because a relevant paper or species account exists.
4. Prioritize direct South Florida validation for hogfish and permit thermal bands, and a direct thermal-selection study for mutton snapper.
5. For blackfin, validate the gradient and Gulf Stream distance proxies against species-specific presence/effort observations before interpreting them as predictive relationships.
6. For tarpon, separate juvenile diel movement evidence from adult feeding behavior before changing category scores.
7. For bonefish, distinguish physiological performance temperatures from habitat preference and validate any local screening band independently.

## Validation and boundaries

All six updated JSON files were parsed after commit. All eight previously source-missing active factors now contain source references. Their provisional status is unchanged.

The current main-branch full-suite and species-validator workflow is validating the final profile updates: https://github.com/markeetox/LUPITA/actions/workflows/python-tests.yml

No NOAA endpoint was contacted. No Pull Ocean Data workflow was run. No scoring logic, numeric factor values, weights, active flags, gates, required flags, or minimum coverage thresholds were changed.
