# South Florida pilot thermal evidence review: Bonefish and Permit

**Status:** research review, not a model change  
**Prepared:** 2026-11-12  
**Scope:** adult Bonefish and Permit in the South Florida pilot, with clearly labeled adjacent-region evidence

## Executive decision

The current SST screening bands remain unsupported as species-specific preference or tolerance ranges. New evidence improves the Bonefish thermal evidence base, but it does not justify replacing the current band with a single ideal range. For Permit, the reviewed evidence supports a temperature association in Texas estuarine survey data, but does not establish an adult South Florida thermal preference or physiological tolerance curve.

**Do not change production SST ranges, ideal ranges, weights, active flags, gates, required flags, or scoring formulas from this review.** Keep the existing values labeled provisional until evidence is comparable to the model's intended use and local validation is available.

## Bonefish (*Albula vulpes*)

### Primary evidence A: adult thermal performance and field exposure

Nowell et al. (2015), *Environmental Biology of Fishes* 98:2133–2146. DOI: https://doi.org/10.1007/s10641-015-0420-6

- Study system: Eleuthera, The Bahamas.
- Methods: swim-tunnel laboratory measurements across temperatures plus implanted thermal loggers in wild adult fish.
- Reported performance optima: 28.0 °C for critical swimming speed and 26.7 °C for scope for activity.
- Reported critical temperatures: 14.5 °C minimum and 37.9 °C maximum.
- Field logger caveat: 138 fish were implanted, but only eight were recaptured with functional loggers; more than 55% of recaptured tagged fish had expelled loggers after 220 days.
- Field temperatures varied substantially: up to 8 °C diel fluctuation and 14 °C seasonally. Fish exceeded the reported Topt about 54% of the time and rarely exceeded Tcrit (0.51% of the time).

**Interpretation:** This is direct species-specific adult thermal-performance evidence and is materially stronger than a generic agency homepage. However, Topt is task-specific laboratory performance, not a universal habitat-preference interval. Tcrit is not a routine habitat boundary. The study is from Eleuthera, not South Florida, and the limited functional logger recaptures constrain field generalization.

**Model implication:** Add these measurements to the evidence ledger as separate performance endpoints, not as a replacement ideal interval or hard gate. A future candidate model may test a continuous performance-response curve, but only after matching the model's environmental variable and temporal/spatial scale to the study measurements and validating locally.

### Primary evidence B: thermal tolerance and tidal-creek behavior

Murchie et al. (2011), *Journal of Thermal Biology* 36:38–48. DOI: https://doi.org/10.1016/j.jtherbio.2010.10.005

- Study system: Cape Eleuthera, The Bahamas, including laboratory acclimation and adjacent tidal creeks.
- CTmax was 36.4 ± 0.5 °C for fish acclimated to 27.3 ± 1.3 °C and 37.9 ± 0.5 °C for fish acclimated to 30.2 ± 1.4 °C.
- Field telemetry showed a positive relationship between maximum creek temperature and time spent in upper creek portions.
- The authors discuss feeding/metabolic demands and predator avoidance as possible explanations; the observation should not be simplified into a universal temperature-driven movement rule.
- Temperatures in the shallow tidal habitat reached 40.6 °C, illustrating that fish can encounter temperatures above laboratory CTmax in spatially and temporally variable microhabitats.

**Interpretation:** Supports the importance of thermal exposure, acclimation, microhabitat and behavior. CTmax is an acute critical endpoint, not an ideal temperature or a safe operating threshold for an SST suitability score.

## Permit (*Trachinotus falcatus*)

### Evidence A: Florida Keys habitat telemetry does not establish thermal thresholds

Brownscombe et al. (2020), *Journal of Fish Biology* 96:469–479. DOI: https://doi.org/10.1111/jfb.14227

- Study system: lower Florida Keys; 45 tagged Permit, March 2017 to June 2018.
- 75% of individuals were detected in both nearshore flats (<3 m) and Florida Reef Tract habitat (15–40 m).
- Reef occupancy peaked March–September, with the highest counts in April and May.
- The study is important for habitat connectivity and seasonal reef use, but its abstracted results do not establish a physiological thermal optimum or tolerance range.

**Interpretation:** Keep this source attached to habitat, connectivity and seasonal occupancy claims. Do not use it as support for numeric SST thresholds.

### Evidence B: Texas estuarine temperature association, not a South Florida adult thermal curve

Beadle & Getz (2026), *Environmental Biology of Fishes* 109, article 125. DOI: https://doi.org/10.1007/s10641-026-01896-8

- Study system: ten Texas coastal bays, fishery-independent monitoring from 1983–2024.
- Sampling used bag seines and gill nets; the sampled fish were predominantly juvenile/subadult (12–519 mm TL), with the authors noting few, if any, mature adults.
- A boosted regression tree associated Permit observations with warmer temperatures (>22 °C), moderate salinity (20–40 ppt), proximity to Gulf passes, higher dissolved oxygen and lower turbidity.
- Temperature accounted for 19.1% of relative variable importance in the reported model.
- The authors explicitly note that their sampling was insufficient to describe the adult population.

**Interpretation:** This is useful, recent, fishery-independent evidence that temperature covaries with juvenile/subadult Permit occurrence in Texas estuaries. It is not a laboratory thermal-performance experiment, it is not adult South Florida evidence, and the reported association is not a physiological threshold. The >22 °C relationship must not be copied into the South Florida adult Permit profile as an ideal range or gate.

## Cross-species evidence classification

| Evidence | Species / stage | Geography | Supports | Does not support |
|---|---|---|---|---|
| Nowell et al. 2015 | Adult Bonefish | Eleuthera, Bahamas | Task-specific swimming/activity optima; critical endpoints; field exposure variability | A universal SST preference band or South Florida-calibrated threshold |
| Murchie et al. 2011 | Adult Bonefish | Eleuthera, Bahamas | CTmax under two acclimation conditions; thermal exposure and creek-use relationship | Ideal habitat range or simple movement rule |
| Brownscombe et al. 2020 | Adult Permit telemetry | Lower Florida Keys | Flats-to-reef connectivity and seasonal reef occupancy | Numeric thermal optimum/tolerance |
| Beadle & Getz 2026 | Mostly juvenile/subadult Permit | Texas estuaries | Field association between occurrence and environmental variables, including temperature | Adult Permit thermal physiology or South Florida threshold |

## Required next research

1. Retrieve and review full methods/results for the Bonefish thermal studies before considering any quantitative candidate response curve.
2. Identify whether the Bonefish thermal endpoints can be related to the LUPITA input variable. Satellite SST is not interchangeable with shallow tidal-creek microhabitat temperature or an implanted fish logger.
3. Search for direct adult Permit thermal-performance, acclimation, critical-temperature, or field logger studies. Current reviewed sources do not establish those endpoints.
4. Review Florida Keys Permit telemetry and long-term fishery-independent datasets for temperature covariates, while distinguishing correlation, life stage, season, depth and sampling effort.
5. Keep candidate curves in shadow mode. Validate against independent observations and report uncertainty and coverage.

## Production safeguards

- Existing Bonefish SST range 20–35 °C and ideal 25–31 °C remain unchanged and provisional.
- Existing Permit SST range 20–34 °C and ideal 24–30 °C remain unchanged and provisional.
- No factor weights, active states, gates, required flags, timing maps, prediction formulas, site rankings or API fields are changed by this review.
- Do not label laboratory performance optima, CTmax values, or regional occurrence associations as fish-presence probability, catch probability, or universal preferred temperatures.
- Distinguish water-column / microhabitat temperature from gridded satellite SST, including resolution, depth, time averaging and exposure mismatch.
- Missing evidence remains unknown; it must not be converted to zero suitability or confirmed absence.

## References

- Nowell, L.B. et al. (2015). https://doi.org/10.1007/s10641-015-0420-6
- Murchie, K.J. et al. (2011). https://doi.org/10.1016/j.jtherbio.2010.10.005
- Brownscombe, J.W. et al. (2020). https://doi.org/10.1111/jfb.14227
- Beadle, K.N. & Getz, E.T. (2026). https://doi.org/10.1007/s10641-026-01896-8
