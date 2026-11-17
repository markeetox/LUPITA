# LUPITA all-species evidence audit: master inventory

**Audit date:** 2026-11-17  
**Branch:** `main`  
**Latest validator snapshot:** [Python CI run #44123016856](https://github.com/markeetox/LUPITA/actions/runs/44123016856), profile commit `c7e3243cf118dfcf11d26f905ac2db22dda4dc7b`  
**Scope:** all JSON profiles in `data/species/`; master inventory, prioritization, and source-by-source review tracking  
**Boundary:** evidence references, statuses, and explanatory notes are being updated in approved batches. Numeric biology, weights, active flags, gates, scoring, confidence, ingestion, and publication behavior remain unchanged.

## Executive result

The current catalog contains **130 species profiles**, not just the 20 named-site SST profiles reviewed on November 16. The existing validator has already inspected all 130:

- 130 parsed; 0 JSON parse errors.
- 130 structurally valid; 0 model-compatibility issues.
- 105 grid models and 25 named-site models.
- 23 temperature-only named-site pilots, 27 other single-factor models, and 80 multi-factor models.
- 55 profiles have elevated active-evidence risk, 23 have partial active-evidence risk, and 52 have no active uncertain weight under the validator's current metadata rules.
- The combined active uncertain factor weight is 26.4. This is a sum of configured factor weights across profiles, **not** a probability, percentage of fish presence, or calibrated scientific-quality score.
- The validator classifies 127 profiles as NEEDS MODEL REBUILD and 3 as NEEDS RESEARCH. These are structural review classifications, not a scientific verdict that 127 species profiles are unusable.

The audit artifact and validator findings are useful for prioritization, but they are not a substitute for source-by-source biological review. A `sourced` label or a specific URL does not prove that the source supports the configured value, population, life stage, region, or model use.

## Catalog breakdown

| Model scope | Profiles | Elevated active-evidence risk | Partial risk | Documented by current metadata |
|---|---:|---:|---:|---:|
| Temperature-only site pilot | 23 | 8 | 14 | 1 |
| Other single-factor model | 27 | 27 | 0 | 0 |
| Multi-factor model | 80 | 20 | 9 | 51 |
| **Total** | **130** | **55** | **23** | **52** |

The 20 named-site SST profiles reviewed and updated on November 16 are part of the 23 temperature-only pilots. Their current declared statuses are 1 `sourced`, 14 `partly_sourced`, and 5 `provisional`. The three remaining temperature-only site profiles are **bonefish, great barracuda, and Permit**.

## Validator findings that guide the review

The latest validator artifact from run #44123016856 records:

| Finding | Count | Interpretation |
|---|---:|---|
| Generic homepage-only source warnings | 59 findings across 36 profiles | These references are not traceable enough to substantiate a factor claim. Findings include configured factors whether active or inactive. |
| Missing factor-source warnings | 6 findings across 5 profiles | African pompano, Almaco jack, sailfish, snowy grouper, and tarpon need factor-level source inspection. |
| Active evidence uncertainty | 55 profiles | At least some active factor weight is provisional, has incomplete reference metadata, or otherwise fails the validator's current source checks. |
| Partly sourced active evidence | 31 profiles | Declared partial support needs claim-fit review. |
| Grid `required` flag ignored | 27 profiles | The grid scorer does not enforce factor-level `required`; the effective behavior must be reviewed against `gate` and runtime contracts. |
| Single-factor models | 50 profiles | Full data coverage does not establish biological completeness. |
| Limited biological dimensions | 50 profiles | Only one of six structural review dimensions is represented. |
| Partial biological dimensions | 75 profiles | Two or three of six dimensions are represented. |
| Provisional timing | 128 profiles | Timing maps are hypotheses/angler guidance, not empirically calibrated feeding probabilities. |

The 59 generic-reference findings are **not 59 species** and do not imply all 59 are active. The six missing-source findings occur across five profiles. These distinctions matter when prioritizing work.

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

Research review is complete for bonefish, great barracuda, and Permit. Metadata application and validator refresh remain to be completed after this research batch is reviewed. These models have a single SST input that is both required and a gate, so weak thermal evidence directly affects site eligibility.

### Batch B: the 27 other single-factor models

Research review is complete for all 27. Metadata application and validator refresh remain pending. The review found 20 partly_sourced, three provisional, and four needs_source SST claims; several demersal species rely on bottom-temperature evidence while the active runtime gate uses SST.

### Batch C: the 80 multi-factor models

Review active factors in coherent parameter groups (SST/gradients, depth/bathymetry, structure/habitat, currents/convergence/Gulf Stream edge, chlorophyll, and seasonal presence). Reuse a source assessment across species only when its taxon, geography, life stage, and measured variable genuinely apply. The 20 multi-factor profiles with elevated active-evidence risk and nine with partial risk receive priority within this batch. Twelve elevated-risk profiles have been reviewed so far.

### Batch D: timing and profile-level biology

Review timing maps, spawning/migration narratives, habitat descriptions, and open research items separately from environmental factor evidence. Angler guidance may be retained as guidance, but must not be represented as a measured probability or established biological optimum.

### Batch E: approved metadata updates and validation

After each research batch is reviewed, apply only approved source references, evidence statuses, and explanatory notes. Then run the species validator and full tests. Keep a progress register so completed species/factors are not researched twice. Batches A and B metadata implementation is now complete; Batch C metadata updates are underway.

## Guardrails

- No changes to numeric temperature/depth ranges or ideal intervals during evidence discovery.
- No changes to factor weights, active flags, gates, required flags, minimum coverage, scoring, confidence, or source selection without a separate evidence-backed approval.
- Do not infer South Florida applicability from a distant population without stating the transfer limitation.
- Do not equate a specific URL, number of citations, or a `sourced` declaration with scientific validation.
- Preserve uncertainty and conflicting evidence rather than forcing a confident label.
- Keep data freshness, environmental input availability, and biological evidence quality as separate concepts.

## Immediate next action

Batch A and Batch B metadata changes have been applied to all 30 profiles. The next action is to verify the full CI validator result and refresh the inventory, then continue Batch C with remaining elevated-risk multi-factor profiles.

## Audit artifact

The source audit JSON, Markdown, and CSV were generated by the existing CI workflow and uploaded as artifact `lupita-species-audit` on run #43952010312. Run `python scripts/validate_species.py` to regenerate them locally.


## Batch A research: remaining temperature-only site pilots | 2026-11-17

Reviewed the three remaining temperature-only site pilots: bonefish (`Albula vulpes`), great barracuda (`Sphyraena barracuda`), and Permit (`Trachinotus falcatus`). Each has one active `sst_c` factor with `gate: true` and `required: true`; therefore the thermal input controls site eligibility.

### Bonefish

Configured range: 20–35 °C; ideal: 25–31 °C; current status: `provisional`.

- A peer-reviewed adult study in Eleuthera, The Bahamas, measured laboratory performance optima of 28.0 °C for critical swimming speed and 26.7 °C for scope for activity. Field loggers showed a broad adult exposure profile (14.5–37.9 °C), but only eight fish were recaptured with functional loggers from 138 implanted fish. Fish spent about 54% of observed time above the laboratory performance optimum.
- A separate integrated field/laboratory study found critical thermal maxima of 36.4 ± 0.5 °C and 37.9 ± 0.5 °C at two acclimation temperatures, and recorded habitat temperatures up to 40.6 °C. These are tolerance/performance results, not preferred SST or catch-response curves.
- Geographic transfer from Bahamian tidal creeks to South Florida remains unvalidated. The evidence supports a central adult performance-temperature association, but not the configured outer band or full ideal interval.

**Recommendation:** change status to `partly_sourced` only if the note clearly distinguishes laboratory performance optima and physiological limits from habitat preference. Keep 20–35 and 25–31 unchanged. Add the 2015 adult study DOI `10.1007/s10641-015-0420-6` and 2011 thermal-biology study DOI `10.1016/j.jtherbio.2010.10.005`.

### Great barracuda

Configured range: 20–32 °C; ideal: 24–30 °C; current status: `provisional`.

- A Nova Southeastern University master's thesis reports South Florida pop-up archival tagging of only two large adults (>100 cm). Those fish experienced 17.8–31.3 °C and used depths greater than 175 m; deeper use was more frequent at night. This is geographically relevant empirical exposure, but the sample is extremely small and does not establish preference.
- FishBase reports a model-derived preferred-temperature estimate of 21.7–28.9 °C (mean 27.2 °C) based on 2,020 spatial cells. This is a modeled distribution association, not a controlled physiological experiment.
- The evidence supports a broad South Florida exposure context and a model-derived central association. It does not validate the configured ideal interval or distinguish adult and juvenile thermal responses.

**Recommendation:** change status to `partly_sourced` with explicit small-sample, adult-only, and model-derived caveats. Keep 20–32 and 24–30 unchanged. Add the NSU thesis record `https://nsuworks.nova.edu/occ_stuetd/32` and the species-specific FishBase estimate `https://www.fishbase.se/country/CountrySpeciesSummary.php?c_code=690&id=1235`.

### Permit

Configured range: 20–34 °C; ideal: 24–30 °C; current status: `provisional`.

- FishBase reports a model-derived preferred-temperature estimate of 23.2–28.0 °C (mean 26.1 °C) based on 624 cells. This is not a direct physiological preference experiment.
- A 2026 Texas estuary study used fishery-independent samples from 1983–2024 and found juvenile permit presence associated with high temperatures (>25 °C), alongside salinity, dissolved oxygen, and turbidity. The study is useful but is Texas-specific and primarily informs juvenile occurrence, not adult South Florida preference.
- A 1972 South Carolina surf-zone survey recorded 26 juvenile permit (16–104 mm standard length) at 12.8–38.5 °C. The report explicitly notes seine-gear selectivity toward juveniles; this is occurrence, not a preferred interval.
- A 1969 Florida study of young-of-year permit in Tampa Bay and St. Augustine discusses occurrence relative to water temperature, but the accessible abstract does not expose numeric temperature results.
- None of these sources validates the configured adult/site SST band or a 24–30 °C ideal interval for South Florida.

**Recommendation:** retain `provisional`. Add the 2026 juvenile study, 1972 survey, and the existing FishBase model reference to the source record only with notes that distinguish juvenile occurrence and modeled association from adult thermal preference. Keep 20–34 and 24–30 unchanged.

### Batch A disposition

All three reviews are complete at the research level. No species JSON was modified. The proposed metadata-only actions are:
- Bonefish: remains `provisional`; adult performance/tolerance studies do not validate its numeric SST suitability band.
- Great barracuda: `provisional` → `partly_sourced`, with N=2 adult South Florida telemetry and model-derived caveats.
- Permit: remain `provisional`; add better traceable juvenile/model sources with explicit life-stage and geographic limitations.

No numeric range, ideal interval, weight, active flag, gate, required flag, site kind, scoring, confidence, ingestion, or publication behavior changed.


## Batch B research: 27 other single-factor grid profiles | 2026-11-17

All 27 profiles in this batch have one active `sst_c` factor, `gate: true`, and `required: true`. The grid scorer ignores `required`, but the gate still controls cell eligibility. Every profile cited only the generic NOAA Fisheries homepage while declaring `sourced`. The review therefore tests whether species-specific evidence supports the configured SST claim, not merely whether temperature matters to the species.

### Profile-by-profile findings

| Species | Configured range / ideal (°C) | Evidence found | Recommended status |
|---|---|---|---|
| Acadian redfish | 3–14 / 5–10 | DFO/COSEWIC reports adult preferred temperatures around 4.5–7 °C in Gulf of Maine and cool deep habitat; this is bottom/deep habitat evidence, not surface SST. [COSEWIC assessment](https://www.canada.ca/en/environment-climate-change/services/species-risk-public-registry/cosewic-assessments-status-reports/deepwater-redfish-acadian-complex-2010.html); [NOAA climate vulnerability profile](https://www.st.nmfs.noaa.gov/Assets/ecosystems/climate/images/species-results/pdfs/Acadian_Redfish.pdf) | `partly_sourced`, with surface-vs-bottom caveat |
| Albacore tuna | 14–24 / 16–21 | ICCAT reports a 10–20 °C thermal preferendum and North American occurrence mainly 14–20 °C. NOAA HMS EFH reports surface waters generally 15.6–19.4 °C, with larger fish using a wider 13.5–25.2 °C range. [ICCAT habitat profile](https://www.iccat.int/documents/scrs/manual/ch2/albbio/iccat/habitat.htm); [NOAA HMS EFH](https://repository.library.noaa.gov/view/noaa/66210/noaa_66210_DS1.pdf) | `partly_sourced`; upper configured range needs qualification |
| Atlantic cod | 0–16 / 4–12 | Gulf of Maine catch-temperature analysis reports bottom-temperature associations around 5.34–6.26 °C in spring and 8.43–9.08 °C in fall; NOAA describes the species as cold-water and demersal. Stock and season matter. [ICES Journal study](https://academic.oup.com/icesjms/article/75/4/1329/4803072); [NOAA species profile](https://www.fisheries.noaa.gov/species/atlantic-cod) | `partly_sourced`; bottom temperature is not SST |
| Atlantic halibut | 1–15 / 3–9 | DFO's 2025 Gulf of St. Lawrence review reports halibut rarely below 2 °C and regularly observed up to at least 12 °C, with reduced catch in the cold intermediate layer. These are bottom-trawl and depth-related observations. [DFO data review](https://publications.gc.ca/collections/collection_2025/mpo-dfo/fs70-5/Fs70-5-2025-028-eng.pdf) | `partly_sourced`; bottom-vs-surface mismatch |
| Bigeye tuna | 15–28 / 18–24 | ICCAT reports an optimum around 17–22 °C and broad tolerance, with deep dives exposing fish to much colder subsurface water. [ICCAT biological review](https://repository.library.noaa.gov/view/noaa/66210/noaa_66210_DS1.pdf); [Brill et al. tagging/physiology paper](https://www.soest.hawaii.edu/pfrp/reprints/iccat_bigeye.pdf) | `partly_sourced`; ideal band slightly broad/warm and depth matters |
| Blueline tilefish | 12–24 / 15–21 | SAFMC reports bottom temperatures of 59–73 °F (about 15–23 °C) and habitat at 240–780 ft. The evidence is demersal bottom temperature, not satellite SST. [SAFMC species profile](https://safmc.net/species/tilefish-blueline/) | `partly_sourced`; strong measurement-depth mismatch |
| Cusk | 2–14 / 4–10 | COSEWIC reports 2–12 °C on the Scotian Shelf and 1–10 °C in the Gulf of Maine, with preferred bottom temperatures around 6–10 °C. [COSEWIC habitat assessment](https://www.canada.ca/en/environment-climate-change/services/species-risk-public-registry/cosewic-assessments-status-reports/cusk-2012/chapter-8.html) | `partly_sourced`; bottom-vs-surface mismatch |
| Golden tilefish | 8–18 / 10–15 | IUCN reports 8–17 °C preference; a Florida east-coast study observed burrow habitat at 8.6–15.4 °C and depths 150–290 m. [IUCN assessment](https://doi.org/10.2305/IUCN.UK.2015-4.RLTS.T16545046A16546277.en); [USGS Florida study](https://pubs.usgs.gov/publication/70135742) | `partly_sourced` for bottom habitat; SST is not a validated proxy |
| Great hammerhead shark | 20–32 / 24–30 | NOAA Florida survey recorded only two juveniles (24.6–27.5 °C) and one adult (27.1 °C) in the northern Gulf. This sample is too small to validate an optimum or broad range. [NOAA nursery/EFH report](https://repository.library.noaa.gov/view/noaa/49034/noaa_49034_DS1.pdf) | `provisional` |
| Greater amberjack | 18–30 / 22–28 | A 2025 juvenile growth experiment found 22–26 °C optimal for on-growing juveniles; FishBase's model-derived estimate is 16.9–29 °C (mean 27.1 °C; 3,486 cells). Neither establishes an adult wild SST preference. [2025 physiology study](https://doi.org/10.1016/j.aquaculture.2024.742011); [FishBase model estimate](https://www.fishbase.org/country/CountrySpeciesSummary.php?c_code=533&genusname=Seriola&lang=English&speciesname=dumerili) | `partly_sourced`; juvenile-performance and model limitations |
| Haddock | 1–14 / 4–10 | A 1972–2013 southern Newfoundland survey found predominant temperatures around 4–8 °C; NOAA EFH reports adult temperatures 0–13 °C and general preference 2–9 °C. Georges Bank studies report preferred bottom temperatures 4–7 °C. [Survey study](https://pubmed.ncbi.nlm.nih.gov/27716923/); [NOAA EFH](https://repository.library.noaa.gov/view/noaa/4105/noaa_4105_DS1.pdf); [NAFO study](https://journalstaging.nafo.int/Volumes/Articles/id/95/Factors-Relating-to-the-Reproductive-Biology-of-Georges-Bank-Haddock-emMelanogrammus-aeglefinusem-in-1977-83) | `partly_sourced`; bottom temperature, stock, and season limitations |
| Longbill spearfish | 20–29 / 23–28 | Only two fish have high-resolution archival-tag data. Off Ascension Island, SST was 23.2–25.2 °C; one fish spent 97% and the other 82% of monitored time in 22–26 °C. The study explicitly calls for more monitoring and geographic coverage. [Kerstetter et al. 2009](https://billfish.org/wp-content/uploads/2023/09/movements-and-habitat-utilization-of-two-longbill-spearfish-tetrapturus-pfluegeri-in-the-eastern-tropical-south-atlantic-ocean.pdf) | `partly_sourced`; N=2 and South Atlantic study area |
| Misty grouper | 12–24 / 15–20 | The species is deep reef-associated (12–439 m); a 2024 lander study reported a single observation at 470 m and 15.79 °C. This is not a thermal preference study and does not support a surface SST band. [Caribbean species account](https://biogeodb.stri.si.edu/caribbean/en/thefishes/species/1126); [2024 deep-sea lander study](https://www.mdpi.com/2410-3888/9/4/114) | `needs_source` for SST preference |
| Ocean pout | 1–16 / 4–11 | NOAA/NEFSC and NAFO accounts describe a demersal cool-water fish, commonly in 6–9 °C water; spawning habitat is below 10 °C. The evidence is bottom habitat and spawning context, not SST preference. [NOAA climate profile](https://www.st.nmfs.noaa.gov/Assets/ecosystems/climate/images/species-results/pdfs/Ocean_Pout.pdf); [NAFO species account](https://www.nafo.int/Portals/0/PDFs/fahay/p1286-1311.pdf) | `partly_sourced`; bottom-vs-surface mismatch |
| Ocean triggerfish | 20–30 / 23–28 | FishBase reports a model-derived preferred temperature of 22.7–28.6 °C (mean 27.3 °C; 770 cells). No independent field or physiological study validating the configured range was located. [FishBase model estimate](https://fishbase.org/summary/Canthidermis-sufflamen) | `provisional` |
| Pollock | 2–16 / 5–12 | FishBase reports a model-derived estimate of 0.5–10.2 °C (mean 7 °C; 292 cells). This does not independently validate the configured interval or establish a local SST response. [FishBase model estimate](https://fishbase.se/Country/CountrySpeciesSummary.php?c_code=616&genusname=Pollachius&lang=English&speciesname=virens) | `provisional` |
| Rainbow runner | 22–31 / 25–30 | Species accounts describe a circumtropical, near-surface pelagic fish (0–150 m), but no traceable numeric thermal-preference or tolerance evidence was located in this review. [Smithsonian Caribbean species account](https://biogeodb.stri.si.edu/caribbean/en/thefishes/species/1277) | `needs_source` |
| Shortfin mako shark | 14–26 / 17–22 | COSEWIC reports preferred water temperature 17–22 °C and satellite-tag temperatures 10.4–28.6 °C, with shelf entry when SST exceeds 17 °C. This closely supports the ideal interval but is a North Atlantic synthesis. [COSEWIC assessment](https://www.canada.ca/en/environment-climate-change/services/species-risk-public-registry/cosewic-assessments-status-reports/shortfin-mako-2017.html) | `partly_sourced`; strong broad support, local calibration absent |
| Silk snapper | 16–28 / 20–26 | NOAA regional survey records show a broad 13–27 °C range, with means of 19, 25, and 25 °C in only three zones; fish occurred at 28–340 m (zone means 55–225 m). This is occurrence data, not a preferred range, and is deep-water context. [NOAA regional report](https://repository.library.noaa.gov/view/noaa/39425/noaa_39425_DS1.pdf) | `partly_sourced`; limited regional temperature records, depth mismatch |
| Skipjack tuna | 18–30 / 20–28 | NOAA EFH reports all-occurrence SST 15–30 °C and abundant occurrence 20–29 °C; an Atlantic/Indian habitat study reports 18–30 °C association and 23–28 °C preference. [NOAA EFH tuna habitat](https://library.oarcloud.noaa.gov/noaa_documents.lib/Digitization_Scans/FY23_Scans/Essential_Fish_Habitat_Descriptions_for_Pacific_Pelagic_Fishery_Ecosystem_Plan_Management_Unit_Species.pdf); [habitat study](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2017.00315/full) | `partly_sourced`; good broad support, ocean-basin differences |
| Swordfish | 12–28 / 18–26 | Swordfish tolerate broad vertical temperatures and use deep cool water by day and warmer surface water at night. Atlantic tagging found SST 10.1–28.6 °C; NOAA EFH reports 5–27 °C overall and usually SST above 13 °C. These data do not establish a single preferred SST interval. [Atlantic tagging study](https://www.sciencedirect.com/science/article/pii/S0165783614002793); [NOAA EFH](https://repository.library.noaa.gov/view/noaa/12864/noaa_12864_DS1.pdf) | `partly_sourced`; diel depth use makes single SST optimum misleading |
| Thresher shark | 12–24 / 15–20 | Western North Atlantic tagging reports wide SST use but greatest capture association around 12–18 °C and commonly 10–22 °C; Southern California adult/subadult tags report 16–21 °C SST. Geography and prey-driven vertical behavior vary. [NOAA WNA study](https://repository.library.noaa.gov/view/noaa/29562/noaa_29562_DS1.pdf); [archival-tag study](https://pmc.ncbi.nlm.nih.gov/articles/PMC3873052/) | `partly_sourced` |
| Vermilion snapper | 18–29 / 21–27 | A South Atlantic shelf survey recorded 395 fish at 19.7–25.7 °C and depths 20–86 m. This supports broad occurrence but not a validated preferred interval. [South Carolina technical report](https://mrl.charleston.edu/wp-content/uploads/pdf/tr30s/Techreport33.pdf) | `partly_sourced` |
| Warsaw grouper | 12–26 / 16–22 | SAFMC reports a deep shelf-break species, commonly 350–650 ft, and a warm-temperate/cool-water description, but no numeric thermal preference. SST is not a validated proxy for its deep habitat. [SAFMC SAFE report](https://safmc.net/wp-content/uploads/2025/01/SG-FMP-SAFE-Report-for-html.html); [SAFMC species profile](https://safmc.net/species/grouper-warsaw/) | `needs_source` for SST preference |
| White marlin | 20–30 / 23–28 | Yucatán PSAT study of 18 fish found experienced temperatures 10.0–33.6 °C, with most time above 24 °C and apparent use around 24–30 °C. A western North Atlantic PSAT study (28 fish) found greatest time around 26 °C. This closely supports the ideal interval, but not the exact outer range everywhere. [Yucatán study](https://doi.org/10.1093/icesjms/fsx176); [western North Atlantic study](https://academic.oup.com/icesjms/article/72/8/2364/2458701) | `partly_sourced`; strong support, regional and life-stage caveats |
| Yellowedge grouper | 12–24 / 15–20 | Species accounts place the fish mainly at 64–370 m on deep reefs and sand/mud bottoms; no numeric thermal preference was found. Surface SST is not a defensible substitute for deep bottom temperature. [Smithsonian Caribbean species account](https://biogeodb.stri.si.edu/caribbean/en/thefishes/species/3489); [Caribbean Reef Fish Foundation](https://caribreef.org/reef-fish-guide/yellowedge-grouper) | `needs_source` for SST preference |
| Yellowfin tuna | 18–31 / 22–28 | NOAA EFH reports all-occurrence SST 15–31 °C and abundant occurrence 20–30 °C; fish up to 100 cm share an optimal average temperature of 27–29 °C with skipjack. Gulf of Mexico archival tagging confirms strong mixed-layer/thermocline use and diel vertical movement. [NOAA tuna habitat synthesis](https://repository.library.noaa.gov/view/noaa/17936/noaa_17936_DS1.pdf); [Gulf tagging study](https://pubmed.ncbi.nlm.nih.gov/20735644/) | `partly_sourced`; size and vertical habitat matter |

### Batch B synthesis

Recommended evidence-status distribution for these 27 profiles:
- **20 partly_sourced:** specific evidence exists, but often for bottom temperature, occurrence rather than preference, a particular stock/life stage, or a distant region.
- **3 provisional:** great hammerhead, ocean triggerfish, pollock. Available evidence is very small-sample or model-derived and does not independently validate the configured interval.
- **4 needs_source for the active SST claim:** misty grouper, rainbow runner, Warsaw grouper, yellowedge grouper. Species/habitat references exist, but no adequate numeric thermal evidence was located; for three deep grouper profiles, the more fundamental issue is that SST may be the wrong environmental variable.

**Critical model-design observation:** several demersal/deep-water profiles cite bottom temperatures or inhabit depths of roughly 30–370 m, while the active runtime input is satellite sea-surface temperature. Those sources may support species thermal ecology, but they do not validate a surface-temperature gate for fish occupying deep bottom habitat. This should become a separate model-to-data design review; do not silently replace SST with an inferred bottom temperature.

No numeric range, ideal interval, weight, active flag, gate, required flag, source configuration, score, confidence, ingestion, or publication behavior changed. Metadata-only source/status/note updates have been applied to all 27 profiles.


## Batch C research and metadata implementation: first four multi-factor profiles | 2026-11-17

The first four elevated-risk multi-factor profiles were reviewed factor by factor. Their prior factor-level citations pointed only to the generic FWC homepage. Species-specific sources were added and active-factor evidence statuses/notes were updated. No numeric intervals, ideal bands, category maps, weights, active flags, gates, required flags, timing scores, or runtime behavior changed.

### African pompano (Alectis ciliaris)
- SST: needs_source. The STRI Greater Caribbean account describes tropical distribution and habitat but does not provide a numeric thermal preference. The configured 22–29 °C range and 24–27 °C ideal remain unvalidated screening assumptions.
- Structure: partly_sourced. The STRI account supports coastal, reef-associated/benthopelagic habitat but does not validate the exact wreck/artificial-reef/natural-reef/ledge ranking or map scores.
- Depth: partly_sourced. STRI reports 0–100 m, which supports broad depth use but not the configured 20–120 m band or 35–80 m ideal; the configured upper limit exceeds the cited range. Depth is an active gate.
- Source: [STRI Greater Caribbean species account](https://biogeodb.stri.si.edu/caribbean/en/thefishes/species/1243).

### Almaco jack (Seriola rivoliana)
- SST: needs_source. No wild-population thermal preference evidence was found to validate 20–28 °C / 22–26 °C. UF/IFAS reports 26 °C for captive broodstock conditioning, which is not wild habitat preference.
- Structure: partly_sourced. NOAA and UF/IFAS support rocky outcrops, reef structures, artificial reefs, wrecks, and high-relief structures, but not the exact category score ordering.
- Depth: partly_sourced. NOAA reports 15–110 m; UF/IFAS reports 3–35 m in subtropical regions and artificial-reef/wreck use to 245 m; STRI reports 3–340 m. These broad ranges do not validate the exact 30–200 m / 40–120 m configured band for South Florida. Depth is an active gate.
- Sources: [NOAA Almaco jack science profile](https://www.fisheries.noaa.gov/species/almaco-jack/science); [UF/IFAS FA249](https://ask.ifas.ufl.edu/publication/FA249); [STRI Greater Caribbean species account](https://biogeodb.stri.si.edu/caribbean/en/thefishes/species/1283).

### Black grouper (Mycteroperca bonaci)
- SST: partly_sourced. Reef Life Survey reports a broad observed sea-temperature range of 20.9–31.1 °C. This is reef occurrence, not a physiological optimum or locally calibrated catch-response curve, and does not validate 20–29 °C / 23–27 °C as preferred SST.
- Structure: partly_sourced. NOAA, Florida Museum, and FDACS support rocky bottoms, coral/natural reefs, drop-offs, ledges, caves, crevices, and artificial reefs. The exact category score ordering remains heuristic.
- Depth: partly_sourced. Florida Museum reports 6–33 m as common habitat; NOAA/FDACS describe adults extending to about 200 m. This supports broad depth use but not the exact 10–110 m / 20–60 m band as a local preference. Depth remains an active gate.
- Sources: [Reef Life Survey](https://reeflife.org/species/mycteroperca-bonaci/); [NOAA black grouper profile](https://www.fisheries.noaa.gov/species/black-grouper); [Florida Museum profile](https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/black-grouper/); [FDACS grouper types](https://www.fdacs.gov/Consumer-Resources/Buy-Fresh-From-Florida/Seafood-Products/Grouper/Grouper-Types).

### Black sea bass (Centropristis striata)
- SST: partly_sourced. NOAA/NEFSC trawl surveys report seasonal adult bottom-water occurrence of roughly 3–21 °C in spring (most 9–12 °C) and 8–28 °C in fall (most 16–27 °C); a warming study reports seasonal exposure around 6–27 °C. These are bottom-water/northern-stock observations, not a universal SST preference curve. Florida Museum describes the species as mainly north of northeastern Florida, with extreme South Florida records during cold winters.
- Structure: sourced. NOAA life-history documents and Florida Museum support rocky bottoms, reefs, wrecks, jetties, pilings, and other complex habitat. The category score ordering remains a model heuristic.
- Depth: partly_sourced. NOAA sources describe summer use around 2–38 m and deeper offshore winter habitat; Florida Museum reports occurrences to about 130 m. The configured 5–60 m / 10–35 m band captures part of summer habitat but not full seasonal depth use. South Florida occurrence is uncommon and associated with cold winters.
- Sources: [NOAA NMFS-NE-143](https://repository.library.noaa.gov/view/noaa/3145/noaa_3145_DS1.pdf); [NOAA NMFS-NE-200 / SEDAR life-history review](https://sedarweb.org/documents/s25rd22-black-sea-bass-centropristis-striata-life-history-and-habitat-characteristics-second-edition/); [NOAA warming study](https://repository.library.noaa.gov/view/noaa/24450/noaa_24450_DS1.pdf); [Florida Museum profile](https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/black-seabass/).

### Batch C first-pass disposition
Four profiles reviewed; 12 active factors updated with factor-specific source references, evidence statuses, and limitations. No numerical model settings or scoring behavior changed. This is not the completion of Batch C: the remaining 25 elevated-risk multi-factor profiles and the other 51 multi-factor profiles still require grouped review. Timing and profile-level narratives remain separate review work.


## Batch C research and metadata implementation: second four multi-factor profiles | 2026-11-17

The second multi-factor batch covers cubera snapper, gag grouper, red grouper, and red snapper. Their generic FWC factor references were replaced with species-specific fisheries, habitat, and research sources. All active factors were assigned conservative statuses and claim-fit notes. No numeric intervals, ideal bands, category maps, weights, active flags, gates, required flags, or runtime behavior changed.

### Cubera snapper (Lutjanus cyanopterus)
- SST: partly_sourced. FishBase reports a model-derived preferred-temperature estimate of 21.7–27.6 °C (mean 25.5 °C; 100 cells), overlapping the configured band but not a direct physiological or local catch-response study.
- Structure: partly_sourced. Florida Museum and BOEM support reef, rocky ledge/overhang, deep reef, and wreck associations; exact category scores remain heuristic.
- Depth: partly_sourced. Florida Museum reports to about 55 m; BOEM reports adults to about 85 m and spawning aggregations at 67–85 m. The configured 18–90 m / 30–60 m band is not a validated general preference.
- Sources: [Florida Museum](https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/cubera-snapper/); [BOEM Gulf EIS](https://www.boem.gov/sites/default/files/documents/environment/BOEM-EIS-2016-049-v2_0.pdf); [FishBase model estimate](https://www.fishbase.se/Country/CountrySpeciesSummary.php?c_code=076&id=1427).

### Gag grouper (Mycteroperca microlepis)
- SST: partly_sourced. NOAA's Gulf climate vulnerability synthesis cites a FishBase model-derived preferred range of 18–27 °C (mean 23 °C); a Florida estuary study recorded juvenile gag at 14.5–33.5 °C; an adult metabolic study tested 15, 22, and 30 °C. These do not validate a wild adult South Florida SST preference.
- Structure: partly_sourced. NOAA, Florida Museum, and SAFMC support adult use of rocky/hard bottom, reefs, wrecks, live bottom, depressions, and ledges, and juvenile use of structured estuarine habitat. Exact category scores remain heuristic.
- Bottom curvature: partly_sourced. A regional habitat analysis reports adult gag encounter probability increasing with terrain ruggedness index and associates spawning aggregations with rocky ridges. Terrain ruggedness is related to relief but is not the same measurement as the pipeline's bottom_curvature variable; this remains a proxy.
- Depth: partly_sourced. A regional analysis reports adult gag across 0–135 m, with encounter probability peaking near 85 m; NOAA/SAFMC describe adults offshore and juveniles in shallow estuarine habitat. The configured 8–80 m / 15–45 m band does not represent all life stages.
- Sources: [NOAA gag profile](https://www.fisheries.noaa.gov/species/gag-grouper); [Florida Museum](https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/gag-grouper/); [SAFMC SAFE report](https://safmc.net/wp-content/uploads/2025/01/SG-FMP-SAFE-Report-for-html.html); [NOAA climate vulnerability synthesis](https://repository.library.noaa.gov/view/noaa/55544/noaa_55544_DS1.pdf); [juvenile gag field study](https://sedarweb.org/documents/s10dw25-habitat-use-by-juvenile-gag-in-subtropical-charlotte-harbor-fl/); [adult metabolic study](https://ufdcimages.uflib.ufl.edu/UF/E0/00/89/25/00001/UFE0008925.pdf); [ecosystem-based habitat analysis](https://academic.oup.com/mcf/article/10/1/40/7827023).

### Red grouper (Epinephelus morio)
- SST: partly_sourced. A southeastern Gulf study reports SST influences abundance and that thermal relationships differ by life stage. The Gulf States life-history table reports juvenile occurrence at 16.1–31.2 °C and larval optimum estimates of 27.4–28.5 °C. These do not establish adult South Florida preference or validate 18–28 °C / 21–25 °C.
- Structure: partly_sourced. NOAA/BOEM document rocky limestone reefs, hardbottom, ledges, crevices, caverns, and wrecks; a NOAA Florida Bay study documents use and excavation of shallow limestone solution holes. The exact numeric category ranking is not calibrated.
- Depth: partly_sourced. NOAA describes common shallow habitat around 3–18 m; BOEM reports a broad 3–200 m occurrence range with many fish at 30–120 m; juveniles use shallower habitats. The configured 10–120 m / 20–60 m band collapses life-stage differences.
- Sources: [NOAA red grouper profile](https://www.fisheries.noaa.gov/species/red-grouper); [BOEM distribution and abundance report](https://espis.boem.gov/Final%20Reports/4770.pdf); [NOAA Florida Bay solution-hole study](https://repository.library.noaa.gov/view/noaa/51241/noaa_51241_DS1.pdf); [GSMFC life-history table](https://www.gsmfc.org/pubs/Habitat/tables/redgrouper.pdf); [southeastern Gulf abundance study](https://pmc.ncbi.nlm.nih.gov/articles/PMC10666610/).

### Red snapper (Lutjanus campechanus)
- SST: partly_sourced. A juvenile northwestern Gulf habitat-suitability study found high-value habitat at bottom temperatures of 24–26 °C; NOAA telemetry off North Carolina found movement related to bottom-water temperature and vertical thermotaxis. These are juvenile/regional bottom-water relationships, not a universal SST preference.
- Structure: partly_sourced. A study of 693 female red snapper off Mississippi examined selection among platforms, artificial reefs, and rigs-to-reefs; BOEM/NOAA document association with reefs, rocky bottoms, and underwater objects. This does not validate the exact South Florida category ranking.
- Depth: partly_sourced. BOEM/NOAA report adults across broad depths including about 7–146 m; the artificial-structure study sampled shallow, mid-depth, and deep habitats. The configured 15–90 m / 30–60 m band does not establish a single preferred depth across life stages and regions.
- Sources: [NOAA Amendment 22 life-history table](https://repository.library.noaa.gov/view/noaa/19625/noaa_19625_DS1.pdf); [BOEM red snapper habitat report](https://www.govinfo.gov/content/pkg/GOVPUB-I-440faa3fb76f06e85b7b62c8e556e1c2/pdf/GOVPUB-I-440faa3fb76f06e85b7b62c8e556e1c2.pdf); [artificial habitat selection study](https://academic.oup.com/mcf/article/13/4/332/7819929); [juvenile temperature HSI study](https://academic.oup.com/tafs/article-abstract/128/4/713/7891354); [NOAA movement study](https://www.fisheries.noaa.gov/resource/peer-reviewed-research/environmental-conditions-diel-period-and-fish-size-influence).

### Batch C cumulative disposition
Eight elevated-risk multi-factor profiles have now been reviewed: African pompano, Almaco jack, black grouper, black sea bass, cubera snapper, gag grouper, red grouper, and red snapper. Twenty-four active factors were reviewed across the first two batches. The remaining 21 elevated-risk multi-factor profiles and 51 other multi-factor profiles still require review. Timing and profile-level biological narratives remain separate work.


## Batch C research and metadata implementation: third four multi-factor profiles | 2026-11-17

The third multi-factor batch covers gray triggerfish, gray (mangrove) snapper, scamp grouper, and snowy grouper. Their factor citations were replaced or supplemented with specific fisheries, agency, and research sources, and active factor statuses/notes were updated. No numeric intervals, ideal bands, weights, active flags, gates, required flags, or runtime behavior changed.

### Gray triggerfish (Balistes capriscus)
- SST: partly_sourced. A 2026 Florida Panhandle tag-return analysis of 3,744 released fish recorded capture SST of 15–31 °C (median 22 °C) and lower recapture proportions with increasing SST, especially above 20 °C. A southeastern U.S. spawning survey recorded spawning females at 15–27 °C (mean 22.7 °C). These are release/recapture and spawning observations, not a validated South Florida habitat-preference curve.
- Structure: partly_sourced. NOAA and Florida Museum support natural/artificial reefs, hardbottom, and ledges; they do not validate wreck preference or exact category scores.
- Depth: partly_sourced. NOAA reports adult depth around 10–55 m, Florida Museum to about 55 m, and the 2026 dataset sampled 20–67 m. These sources do not validate the full 10–100 m configured outer band.
- Sources: [NOAA Gray Triggerfish Layer Guidance](https://www.ncei.noaa.gov/waf/data-atlas-waf/products/html/lmrPlates/GrayTriggerfishLayerGuidance.htm); [Florida Museum](https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/gray-triggerfish/); [2026 tag-return study](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2026.1743605/full); [southeastern U.S. spawning survey](https://repository.library.noaa.gov/view/noaa/17687/noaa_17687_DS1.pdf).

### Gray (mangrove) snapper (Lutjanus griseus)
- SST: partly_sourced. A regional EFH assessment reports adult occurrence at 13.4–32.5 °C across estuarine, nearshore, and offshore environments. This is a broad occurrence envelope, not a preferred interval or South Florida SST response curve.
- Structure: partly_sourced. Florida Museum and the EFH assessment describe mangrove, coral/rocky ledge, reef, hardbottom, and soft-bottom use. They do not validate every configured category, especially wrecks/artificial reefs, or the score ordering.
- Depth: partly_sourced. The EFH assessment reports adult occurrence from 0–180 m; the configured 0.5–50 m band represents a shallow coastal subset rather than the full distribution.
- Sources: [Florida Museum gray snapper profile](https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/gray-snapper/); [regional essential fish habitat assessment](https://www.swg.usace.army.mil/Portals/26/docs/Planning/Public%20Notices-Civil%20Works/HSC-ECIP%20FIFR-EIS/App%20L%20-%20Essential%20Fish%20Habitat%20Assessment%20%2818%20Nov%202019%29.pdf); [FWC gray snapper profile](https://myfwc.com/wildlifehabitats/profiles/saltwater/snapper/gray-snapper/).

### Scamp grouper (Mycteroperca phenax)
- SST: partly_sourced. Southeastern U.S. spawning observations report bottom temperatures of 16–27 °C (mean 21 °C); SEDAR describes Carolina spawning at 22–25 °C. These are seasonal bottom-water/spawning observations, not a year-round SST preference.
- Structure: partly_sourced. SEDAR and SAFMC describe low-profile live-bottom areas, Oculina coral, ledges, high-relief rocky bottoms, wrecks, and outcrops. This supports the broad association but not exact category score values.
- Depth: partly_sourced. SAFMC reports preferred low-profile live-bottom habitat at 75–300 ft (about 23–91 m); FishBase reports 30–100 m. This overlaps the configured 25–100 m / 40–80 m band but does not validate the exact ideal interval.
- Sources: [SEDAR scamp assessment](https://sedarweb.org/documents/s19rd28-population-assessment-of-the-scamp-mycteroperca-phenax-from-the-southeastern-united-states/); [SAFMC scamp profile](https://safmc.net/species/grouper-scamp/); [FishBase field guide](https://fishbase.se/Fieldguide/FieldGuideSummary.php?c_code=840&genusname=Mycteroperca&speciesname=phenax); [southeastern U.S. spawning survey](https://pmc.ncbi.nlm.nih.gov/articles/PMC5338871/).

### Snowy grouper (Hyporthodus niveatus)
- SST: needs_source. Available numeric temperatures are spawning-condition females at deep bottom depths (175–223 m), with 9–15 °C observations. These do not validate the configured 12–24 °C surface-temperature range or 14–20 °C ideal. Surface SST is not established as a valid proxy for this deep-water species.
- Bottom slope: partly_sourced. SAFMC describes outer-shelf/upper-slope habitat with ridges, terraces, and steep cliffs. This supports broad slope/relief association but does not validate the continuous bottom_slope metric or a monotonic higher-is-better response.
- Depth: partly_sourced. SAFMC reports adult depths of 116–259 m; spawning females were observed at 175–223 m (N=48); FWC describes rocky/reef habitat to 1,700 ft. This supports the configured deep-water context but not a locally calibrated optimum.
- Sources: [SAFMC Amendment 51](https://safmc.net/documents/snapper-grouper-amendment-51-final-03-02-2023/); [SAFMC species profile](https://safmc.net/species/grouper-snowy/); [FWC snowy grouper profile](https://myfwc.com/wildlifehabitats/profiles/saltwater/grouper/snowy-grouper/); [spawning survey](https://pmc.ncbi.nlm.nih.gov/articles/PMC5338871/); [BOEM habitat assessment](https://www.boem.gov/sites/default/files/documents/environment/BOEM-EIS-2016-049-v2_0.pdf).

### Batch C cumulative disposition
Twelve elevated-risk multi-factor profiles have now been reviewed across 36 active factors: African pompano, Almaco jack, black grouper, black sea bass, cubera snapper, gag grouper, red grouper, red snapper, gray triggerfish, gray snapper, scamp grouper, and snowy grouper. Seventeen of the original 29 elevated-risk multi-factor profiles remain, along with 51 other multi-factor profiles. Timing and profile-level narratives remain separate review work.


## Batch C research and metadata implementation: third four multi-factor profiles | 2026-11-17

The third multi-factor batch covers gray triggerfish, gray (mangrove) snapper, scamp grouper, and snowy grouper. Their factor citations were replaced or supplemented with specific fisheries, agency, and research sources, and active factor statuses/notes were updated. No numeric intervals, ideal bands, weights, active flags, gates, required flags, or runtime behavior changed.

### Gray triggerfish (Balistes capriscus)
- SST: partly_sourced. A 2026 Florida Panhandle tag-return analysis of 3,744 released fish recorded capture SST of 15–31 °C (median 22 °C) and lower recapture proportions with increasing SST, especially above 20 °C. A southeastern U.S. spawning survey recorded spawning females at 15–27 °C (mean 22.7 °C). These are release/recapture and spawning observations, not a validated South Florida habitat-preference curve.
- Structure: partly_sourced. NOAA and Florida Museum support natural/artificial reefs, hardbottom, and ledges; they do not validate wreck preference or exact category scores.
- Depth: partly_sourced. NOAA reports adult depth around 10–55 m, Florida Museum to about 55 m, and the 2026 dataset sampled 20–67 m. These sources do not validate the full 10–100 m configured outer band.
- Sources: [NOAA Gray Triggerfish Layer Guidance](https://www.ncei.noaa.gov/waf/data-atlas-waf/products/html/lmrPlates/GrayTriggerfishLayerGuidance.htm); [Florida Museum](https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/gray-triggerfish/); [2026 tag-return study](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2026.1743605/full); [southeastern U.S. spawning survey](https://repository.library.noaa.gov/view/noaa/17687/noaa_17687_DS1.pdf).

### Gray (mangrove) snapper (Lutjanus griseus)
- SST: partly_sourced. A regional EFH assessment reports adult occurrence at 13.4–32.5 °C across estuarine, nearshore, and offshore environments. This is a broad occurrence envelope, not a preferred interval or South Florida SST response curve.
- Structure: partly_sourced. Florida Museum and the EFH assessment describe mangrove, coral/rocky ledge, reef, hardbottom, and soft-bottom use. They do not validate every configured category, especially wrecks/artificial reefs, or the score ordering.
- Depth: partly_sourced. The EFH assessment reports adult occurrence from 0–180 m; the configured 0.5–50 m band represents a shallow coastal subset rather than the full distribution.
- Sources: [Florida Museum gray snapper profile](https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/gray-snapper/); [regional essential fish habitat assessment](https://www.swg.usace.army.mil/Portals/26/docs/Planning/Public%20Notices-Civil%20Works/HSC-ECIP%20FIFR-EIS/App%20L%20-%20Essential%20Fish%20Habitat%20Assessment%20%2818%20Nov%202019%29.pdf); [FWC gray snapper profile](https://myfwc.com/wildlifehabitats/profiles/saltwater/snapper/gray-snapper/).

### Scamp grouper (Mycteroperca phenax)
- SST: partly_sourced. Southeastern U.S. spawning observations report bottom temperatures of 16–27 °C (mean 21 °C); SEDAR describes Carolina spawning at 22–25 °C. These are seasonal bottom-water/spawning observations, not a year-round SST preference.
- Structure: partly_sourced. SEDAR and SAFMC describe low-profile live-bottom areas, Oculina coral, ledges, high-relief rocky bottoms, wrecks, and outcrops. This supports the broad association but not exact category score values.
- Depth: partly_sourced. SAFMC reports preferred low-profile live-bottom habitat at 75–300 ft (about 23–91 m); FishBase reports 30–100 m. This overlaps the configured 25–100 m / 40–80 m band but does not validate the exact ideal interval.
- Sources: [SEDAR scamp assessment](https://sedarweb.org/documents/s19rd28-population-assessment-of-the-scamp-mycteroperca-phenax-from-the-southeastern-united-states/); [SAFMC scamp profile](https://safmc.net/species/grouper-scamp/); [FishBase field guide](https://fishbase.se/Fieldguide/FieldGuideSummary.php?c_code=840&genusname=Mycteroperca&speciesname=phenax); [southeastern U.S. spawning survey](https://pmc.ncbi.nlm.nih.gov/articles/PMC5338871/).

### Snowy grouper (Hyporthodus niveatus)
- SST: needs_source. Available numeric temperatures are spawning-condition females at deep bottom depths (175–223 m), with 9–15 °C observations. These do not validate the configured 12–24 °C surface-temperature range or 14–20 °C ideal. Surface SST is not established as a valid proxy for this deep-water species.
- Bottom slope: partly_sourced. SAFMC describes outer-shelf/upper-slope habitat with ridges, terraces, and steep cliffs. This supports broad slope/relief association but does not validate the continuous bottom_slope metric or a monotonic higher-is-better response.
- Depth: partly_sourced. SAFMC reports adult depths of 116–259 m; spawning females were observed at 175–223 m (N=48); FWC describes rocky/reef habitat to 1,700 ft. This supports the configured deep-water context but not a locally calibrated optimum.
- Sources: [SAFMC Amendment 51](https://safmc.net/documents/snapper-grouper-amendment-51-final-03-02-2023/); [SAFMC species profile](https://safmc.net/species/grouper-snowy/); [FWC snowy grouper profile](https://myfwc.com/wildlifehabitats/profiles/saltwater/grouper/snowy-grouper/); [spawning survey](https://pmc.ncbi.nlm.nih.gov/articles/PMC5338871/); [BOEM habitat assessment](https://www.boem.gov/sites/default/files/documents/environment/BOEM-EIS-2016-049-v2_0.pdf).

### Batch C cumulative disposition
Twelve elevated-risk multi-factor profiles have now been reviewed across 36 active factors: African pompano, Almaco jack, black grouper, black sea bass, cubera snapper, gag grouper, red grouper, red snapper, gray triggerfish, gray snapper, scamp grouper, and snowy grouper. Seventeen of the original 29 elevated-risk multi-factor profiles remain, along with 51 other multi-factor profiles. Timing and profile-level narratives remain separate review work.


## Latest validator refresh after Batch C third profile update | 2026-11-17

Python CI [#44123016856](https://github.com/markeetox/LUPITA/actions/runs/44123016856) passed and regenerated the full 130-profile audit after the gray triggerfish, gray snapper, scamp grouper, and snowy grouper metadata changes.

- 130 profiles parsed and structurally valid; 0 JSON parse errors; 0 model compatibility issues; 0 validator errors.
- Active evidence risk changed from the original baseline of 64 elevated / 14 partial / 52 documented to **55 elevated / 23 partial / 52 documented**.
- Combined active uncertain factor weight declined from 37.4 to **26.4**. This is a sum of configured factor weights across profiles, not a probability or percentage.
- Generic homepage-only findings declined from 96 across 48 profiles to **59 across 36 profiles**.
- Missing factor-source findings are now 6 across five profiles: African pompano SST, Almaco jack SST, sailfish cold_front, snowy grouper SST, and tarpon salinity/bridges_lights.
- Across the 80 multi-factor profiles, current risk distribution is 20 elevated, 9 partial, and 51 documented by current metadata. The 27 other single-factor grid profiles remain elevated-risk; the 23 temperature-only site pilots remain 8 elevated, 14 partial, and 1 documented.

The updated audit is a metadata-quality diagnostic, not a biological-quality verdict. Numeric model settings and runtime behavior remain unchanged.


## Batch C research and metadata implementation: pelagic species | 2026-11-17

Reviewed Atlantic blue marlin, Atlantic bluefin tuna, sailfish, and tarpon. Replaced generic references for blue marlin and bluefin tuna, tightened sailfish current-convergence evidence, and documented inactive sailfish/tarpon factors. No numeric ranges, ideal bands, factor weights, active flags, gates, required flags, season months, or runtime behavior changed.

### Atlantic blue marlin (Makaira nigricans)
- SST: partly_sourced. North Atlantic and Southwest Atlantic satellite-tag studies report most time in warm surface waters, commonly 26–30 °C; a 21-fish Southwest Atlantic study reports most time at 26–28 °C. Supports broad 23–31 °C / 26–29 °C association, not a South Florida catch-probability curve.
- SST gradient: partly_sourced. Tagging and Gulf movement studies describe seasonal shifts with SST, production, fronts/eddies, and temperature/oxygen structure. They do not calibrate the pipeline's scalar SST-gradient magnitude.
- Current convergence: partly_sourced. Shelf-edge and productive oceanographic features are supported, but studies do not directly measure current convergence or validate a higher-is-better score.
- Gulf Stream edge: provisional. Seasonal shelf-edge/offshore movements are documented, but no species-specific distance-response curve validates the configured -20 to 50 km / 0 to 25 km bands.
- Depth: partly_sourced. Tag records describe fish vertical dive depths, not seafloor bathymetry. The configured 100–4,000 m bathymetric range and 200–2,000 m ideal remain unvalidated as a seabed-depth preference; this factor is an active gate.
- Season presence: partly_sourced. Gulf tagging documents summer use of northern Gulf shelf-edge waters during spawning and overwintering in the Bay of Campeche. The configured May–September window is a broad Gulf seasonal proxy, not a South Florida monthly catch curve.
- Sources: [NOAA-hosted North Atlantic tag study](https://repository.library.noaa.gov/view/noaa/58935); [USGS Gulf movement study](https://www.usgs.gov/publications/horizontal-movements-atlantic-blue-marlin-makaira-nigricans-gulf-mexico); [Southwest Atlantic satellite-tag study](https://doi.org/10.3390/fishes10050201); [North Atlantic seasonal/diel habitat study](https://academic.oup.com/icesjms/article/80/4/1002/7067461).

### Atlantic bluefin tuna (Thunnus thynnus)
- SST: partly_sourced. Archival-tag data report 10–23 °C for most occupancy, with peak occupancy around 13–20 °C; ICCAT documents broad adult/juvenile temperature tolerances. Supports broad 12–24 °C / 16–22 °C context, but use varies by stock, stage, season, and dive depth.
- SST gradient: partly_sourced. NOAA habitat guidance describes feeding along productive frontal features, including chlorophyll-a fronts, and tracking temperature/currents. A chlorophyll front is not identical to runtime SST-gradient magnitude.
- Depth: partly_sourced. NOAA reports frequent dives to 500–1,000 m, but these are fish vertical dive depths, not seafloor bathymetry. The configured 100–3,000 m / 200–1,500 m bathymetric range remains unvalidated as a seabed-depth preference; depth is an active gate.
- Season presence: partly_sourced. NOAA reports western Atlantic spawning from mid-April through June, mainly in the Gulf, while tagging summaries describe seasonal movements. The configured January–May window may represent migration/availability but does not capture the full spawning period or establish a South Florida monthly catch curve.
- Sources: [NOAA western Atlantic bluefin profile](https://cd1-www.fisheries.noaa.gov/species/western-atlantic-bluefin-tuna); [NOAA HMS EFH Amendment 10](https://www.habitat.noaa.gov/application/efhinventory/docs/a10_hms_efh.pdf); [archival-tag study](https://pmc.ncbi.nlm.nih.gov/articles/PMC2701635/); [ICCAT temperature analysis](https://www.iccat.int/Documents/CVSP/CV075_2018/n_6/CV075061494.pdf); [NOAA habitat guidance](https://www.ncei.noaa.gov/waf/data-atlas-waf/products/html/lmrPlates/HabitatSuitability_BluefinTunaLayerGuidance.htm).

### Atlantic sailfish (Istiophorus platypterus)
- Existing factor research and notes were retained. The current-convergence factor was downgraded from sourced to partly_sourced because its evidence is primarily Florida angler reporting of bait/weed lines and shelf-edge current features, not a direct current-convergence study.
- The inactive cold_front factor now has traceable Florida angler references and remains provisional; it is not detected by the pipeline and has zero scoring weight.
- Existing provisional SST-gradient, chlorophyll, chlorophyll-gradient, depth, and Gulf Stream-edge claims remain provisional pending stronger direct studies/calibration. Existing South Florida tagging and seasonal evidence for SST and season presence remains partly_sourced.
- Sources: [Nova Southeastern sailfish habitat research](https://nsuworks.nova.edu/mako/vol2021/iss1/1); [ICCAT sailfish habitat report](https://www.iccat.int/Documents/CVSP/CV065_2010/n_5/CV065051740.pdf); [Florida Sportsman local guidance](https://floridasportsman.com/editorial/features_florida_sailfish_fishing_basics/397320).

### Atlantic tarpon (Megalops atlanticus)
- Existing active-factor statuses/notes were retained: SST, season, and inlet structure remain partly_sourced; tide stage and time-of-day remain provisional.
- The inactive salinity factor now cites a regional EFH assessment and Florida Museum species account. Broad euryhaline tolerance supports partial biological context but does not establish a predictive salinity suitability curve; weight remains zero.
- The inactive bridges_lights factor remains needs_source until traceable evidence and a usable dataset exist.
- Sources: [regional essential fish habitat assessment](https://www.swg.usace.army.mil/Portals/26/docs/Planning/Public%20Notices-Civil%20Works/HSC-ECIP%20FIFR-EIS/App%20L%20-%20Essential%20Fish%20Habitat%20Assessment%20%2818%20Nov%202019%29.pdf); [Florida Museum tarpon profile](https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/tarpon/).

### Batch C cumulative disposition
Sixteen elevated-risk multi-factor profiles have now been reviewed across 59 active factors. The four pelagic profiles above complete this batch's source updates; inactive sailfish cold_front and tarpon salinity were also documented. The remaining multi-factor profiles continue to be prioritized by active evidence risk and runtime relevance.


## Batch C research and metadata implementation: coastal pelagic species | 2026-11-17

Reviewed blackfin tuna, cobia, common snook, and Florida pompano. Updated factor sources/statuses/notes where source fit justified it. No numeric intervals, ideal bands, weights, active flags, gates, required flags, month lists, or runtime behavior changed.

### Blackfin tuna (Thunnus atlanticus)
- SST: partly_sourced. A northern Gulf satellite-tag study of nine fish found 89% of time at 21.9–26.6 °C; ICCAT describes a lower distribution limit near 20 °C. This supports broad 20–29 °C / 22–27 °C context, but the tag sample was small and geographically limited.
- SST gradient and chlorophyll gradient: provisional. Literature links distribution to upwelling, runoff, plankton concentrations, and water clarity, but does not calibrate remotely sensed gradient magnitude or a higher-is-better score.
- Bottom slope: partly_sourced. Published summaries link Florida distribution to shelf-slope edges and continental shelf steepness, but do not validate the runtime bottom_slope metric or monotonic score.
- Depth: partly_sourced. Fish tags report vertical dive depths; fisheries sources describe shelf-slope-edge occurrence and typical depths. Vertical fish depth is not seafloor bathymetry, so the configured 30–1,500 m / 60–800 m bathymetric band is only partly supported and likely broader than common habitat.
- Gulf Stream edge: provisional. Warm-water/pelagic and shelf-edge associations do not establish a preferred distance from the Gulf Stream edge.
- Sources: [NSU satellite-tag study](https://nsuworks.nova.edu/occ_facarticles/485/); [ICCAT blackfin manual](https://www.iccat.int/Documents/SCRS/Manual/CH2/2_1_10_7_BLF_ENG.pdf); [NOAA-hosted 2023 distribution/genetics paper](https://repository.library.noaa.gov/view/noaa/62951/noaa_62951_DS1.pdf); [Florida Museum](https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/blackfin-tuna/); [NOAA/NMFS longline synthesis](https://www.govinfo.gov/content/pkg/GOVPUB-I-8ed8af2f8d903e3b3d038f3ad79d44c4/pdf/GOVPUB-I-8ed8af2f8d903e3b3d038f3ad79d44c4.pdf).

### Cobia (Rachycentron canadum)
- Structure: existing sourced status retained; NOAA and Florida Museum directly document buoys, debris, wrecks, artificial reefs, and other structure.
- SST: partly_sourced. Florida Museum reports 20–30 °C; SEDAR documents temperature-related movement; 2026 Gulf tagging recorded 13.3–34.5 °C with seasonal thermal shifts. This supports broad context but not a single preferred year-round SST curve.
- Depth: provisional. A 2026 tagging study reports fish vertical use from surface to 121 m, but vertical fish depth is not seafloor bathymetry. Available sources do not validate the configured 3–120 m / 9–45 m bathymetric preference.
- Season presence: partly_sourced. NOAA/ASMFC describe seasonal northward/inshore movement in warm months and wintering farther south/offshore; 2026 Gulf tagging recorded south-southwest/offshore dispersal from September through April. This supports a broad South Florida winter/spring window, not exact monthly catch scores.
- Sources: [NOAA cobia profile](https://www.fisheries.noaa.gov/species/cobia); [2026 Gulf satellite-tag study](https://repository.library.noaa.gov/view/noaa/77073); [ASMFC cobia life history](https://asmfc.org/species/cobia/); [GSMFC cobia life-history table](https://www.gsmfc.org/pubs/Habitat/tables/COBIA.pdf).

### Common snook (Centropomus undecimalis)
- SST: partly_sourced. FWC and lab studies support cold-stress boundaries around 14–16 °C; a 2025 Everglades analysis found a positive relationship between relative abundance and temperature; a 2025 juvenile thermal-tolerance study shows body size and salinity affect cold tolerance. These sources do not validate a universal adult optimum or the full 15.6–35 °C / 24–32 °C ideal band.
- Structure: existing sourced status retained; FWC/Florida Museum document mangroves and broad inshore habitat, although not all configured categories are represented as separate runtime values.
- Tide stage and time of day: provisional status retained. Outgoing-tide preference and night dock-light feeding are largely angler guidance; FWC spawning timing supports late afternoon/evening activity only during spawning.
- Spawning season: existing sourced status retained with FWC seasonal window and spawning-site research.
- Sources: [2025 Everglades abundance study](https://academic.oup.com/mcf/article/17/5/vtaf026/8256747); [2025 juvenile thermal-tolerance study](https://academic.oup.com/mcf/article/17/4/vtaf023/8233615); [snook spawning-site study](https://pmc.ncbi.nlm.nih.gov/articles/PMC4084985/); [FWC profile](https://myfwc.com/wildlifehabitats/profiles/saltwater/snook/snook/).

### Florida pompano (Trachinotus carolinus)
- SST: partly_sourced. A life-history/aquaculture synthesis reports avoidance below about 20 °C, mortality at 10–12 °C, and 25–30 °C optima for spawning, larval development, and juvenile growth. These are physiological/early-life-stage data, not an adult surf-zone catch curve.
- Depth: partly_sourced. FWC documents inshore/nearshore sandy beaches, oyster bars, and seagrass, with records to about 40 m; the life-history synthesis describes juvenile surf-zone use and offshore movement below 20 °C. This supports shallow coastal use but not the exact 0.5–20 m / 1–8 m ideal across all stages and seasons.
- Season presence: partly_sourced. FWC reports offshore spawning March–September; a synthesis suggests February–October in southeastern waters with peaks in April–May and September–October, while Gulf/Caribbean spawning may occur year-round. The configured month window is not a validated monthly catch curve.
- Sources: [FWC Florida pompano profile](https://myfwc.com/wildlifehabitats/profiles/saltwater/jacks/florida-pompano/); [NOAA-hosted life-history review](https://repository.library.noaa.gov/view/noaa/49230/noaa_49230_DS1.pdf); [open-access review](https://onlinelibrary.wiley.com/doi/full/10.1111/jwas.12809); [Florida Museum](https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/florida-pompano/).

### Batch C cumulative disposition
Twenty of the 29 originally elevated-risk multi-factor profiles have now been reviewed across 77 active factors. Nine elevated-risk multi-factor profiles remain, plus nine partial-risk and 51 documented multi-factor profiles. The review continues to distinguish environmental suitability from fish vertical behavior and from post-release survival; evidence for one is not automatically evidence for another.


## Batch A/B metadata implementation | 2026-11-17

Applied metadata-only evidence updates to all 30 profiles covered by Batch A and Batch B.

### Batch A: remaining temperature-only site pilots
- Bonefish: remains provisional. Added adult performance-temperature and thermal-tolerance sources with explicit N=8 recapture limitation and Bahamas-to-South-Florida transfer caveat; these do not validate preferred SST.
- Great barracuda: provisional → partly_sourced. Added South Florida archival-tag thesis (N=2 adults) and FishBase model estimate with explicit small-sample/model caveats.
- Permit: remains provisional. Added the 2026 Texas juvenile occupancy study, 1972 South Carolina juvenile survey, and FishBase model estimate; notes distinguish juvenile occurrence and modeled association from adult South Florida preference.

### Batch B: 27 other single-factor grid profiles
Applied the recommended status/source/note classifications:
- 20 partly_sourced: Acadian redfish, albacore tuna, Atlantic cod, Atlantic halibut, bigeye tuna, blueline tilefish, cusk, golden tilefish, greater amberjack, haddock, longbill spearfish, ocean pout, shortfin mako, silk snapper, skipjack tuna, swordfish, thresher shark, vermilion snapper, white marlin, yellowfin tuna.
- 3 provisional: great hammerhead, ocean triggerfish, pollock.
- 4 needs_source: misty grouper, rainbow runner, Warsaw grouper, yellowedge grouper.

All 30 profile-level source lists and active SST factor source/status/value_notes fields were updated. The four needs_source profiles retain empty factor-level SST source lists because species/habitat references do not substantiate a numeric surface-temperature claim. No numeric ranges, ideal intervals, weights, active flags, gates, required flags, scoring, confidence, source selection, ingestion, or publication behavior changed. CI run #44124511157 is validating the updated catalog.



## Batch C evidence review: next four multi-factor profiles | 2026-11-17

Reviewed Hogfish, Jack crevalle, King mackerel, and Red drum across 13 active factors. Added traceable species-specific sources and claim-fit notes; kept evidence statuses conservative. No numeric ranges, ideal intervals, weights, active flags, gates, required flags, scoring, confidence, or runtime behavior changed.

### Hogfish (*Lachnolaimus maximus*)
- SST: needs_source. FWC and Florida Museum accounts describe distribution and habitat but do not establish a species-specific thermal preference/tolerance band; removed non-supporting references from the factor-level source list while retaining them at profile level.
- Structure: partly_sourced. FWC, Florida Museum, and NOAA sanctuary research support adult reef/rock/ledge/hard-bottom association and juvenile seagrass nursery use, but not exact map-class score ranking or individual polygon occupancy.
- Depth: partly_sourced. Florida Museum reports 3–30 m occurrence, matching the configured outer range; it does not validate the 8–25 m ideal or a single depth preference across life stages.

### Jack crevalle (*Caranx hippos*)
- SST: partly_sourced. Florida Museum reports adult occurrence around 18–33.6 °C and larval occurrence around 20.4–29.4 °C; occurrence is not a preferred-temperature curve.
- Depth: partly_sourced. Florida Museum reports shelf habitat to about 100 m and SCDNR describes offshore and estuarine use; the sources do not validate the configured shallow range as universal preference.
- Season presence: partly_sourced. FWC reports March–September offshore spawning and SCDNR describes seasonal migration. These do not validate the full configured monthly presence window or peak catch scores in South Florida.

### King mackerel (*Scomberomorus cavalla*)
- SST: partly_sourced. NOAA/SAFMC report warm-water affinity and rare occurrence below about 20 °C, but do not establish the full configured range or ideal interval as a preferred-temperature curve.
- SST gradient: needs_source. Generic FWC homepage citation does not establish that stronger satellite SST gradients increase king mackerel suitability.
- Depth: partly_sourced. NOAA, Florida Museum, and FishBase report coastal-pelagic shelf depths, but published depth ranges differ and do not validate the configured band/ideal as a single preference.
- Season presence: partly_sourced. NOAA documents the South Florida winter mixing zone south of the Keys from November–March and seasonal migration; this supports winter presence but not the exact month/peak scores as catch probabilities.

### Red drum (*Sciaenops ocellatus*)
- SST: partly_sourced. Florida Museum, NOAA-hosted habitat account, and GSMFC synthesis document broad thermal tolerance and stage-specific associations, not a preferred adult South Florida SST curve.
- Depth: partly_sourced. Sources support shallow estuarine nursery habitat and adult coastal/nearshore use, but not a universal 0.3–15 m adult range or 0.5–5 m ideal across life stages.
- Season presence: partly_sourced. FWC tagging and Florida Museum sources support late-August–November fall spawning/migration, but not the exact August–December monthly score or a catch-rate model.

### Batch C cumulative disposition
Twenty-four of the 29 originally elevated-risk multi-factor profiles have now been reviewed across 90 active factors. Five elevated-risk multi-factor profiles remain for the next review: Mahi-mahi, Mutton snapper, Sheepshead, Southern flounder, and Wahoo. This is the remaining set after removing the four profiles covered in this batch from the nine-profile remainder.


## Batch C evidence review: final five elevated-risk multi-factor profiles | 2026-11-17

Reviewed Mahi-mahi, Mutton snapper, Sheepshead, Southern flounder, and Wahoo across 26 active factors. Updated only profile/factor sources, evidence statuses, explanatory notes, review metadata, and the Southern flounder regional-applicability open item. No numeric ranges, ideal intervals, weights, active flags, gates, required flags, month lists, scoring, confidence, source selection, ingestion, or publication behavior changed.

### Mahi-mahi (*Coryphaena hippurus*)
- SST: partly_sourced. Satellite tags from 19 wild fish (2 off Louisiana, 17 off Miami) recorded 95% of observed time in 25-29 °C SST. The narrower 26.7-27.8 °C association applies during northward migration, not a universal South Florida catch optimum.
- Current convergence: partly_sourced. Sargassum/flotsam association is documented, but no reviewed source directly validates the runtime current-convergence calculation or its response curve.
- Bottom depth: weak_factor. Fish vertical dive depth is not seafloor bathymetry; bathymetry remains only an offshore/nearshore proxy.
- SST gradient, chlorophyll, chlorophyll gradient, and Gulf Stream-edge distance remain provisional because their numeric/relative response curves are not calibrated by the reviewed species-specific evidence.
- Sources: [NC Sea Grant satellite-tag summary](https://ncseagrant.ncsu.edu/hooklinescience/what-depth-and-water-temperature-do-mahi-mahi-prefer/); [Frontiers tagging study](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2021.626082/full).

### Mutton snapper (*Lutjanus analis*)
- Structure: partly_sourced. Florida Keys telemetry supports adult reef home-site fidelity and migration to discrete Riley's Hump spawning grounds; generic reef polygons do not identify aggregation sites, and category score ranking is unvalidated.
- Bottom curvature: partly_sourced. Reef-edge habitat context is plausible, but the runtime curvature metric and higher-is-better response are not directly measured.
- Depth and SST remain provisional. The existing numeric bands are not validated depth preference or temperature selection curves.
- Season presence: partly_sourced. Telemetry of 55 fish in the Dry Tortugas (2008-2012) documented spawning migrations April-August, linked to lunar timing and warming from 25-30 °C. This is local spawning-migration evidence, not a catch-rate curve; the configured May-August interval omits observed April movements and June-July peak scores are not independently validated.
- Sources: [NOAA repository, Feeley et al. 2018](https://repository.library.noaa.gov/view/noaa/62684); [FWC mutton snapper profile](https://myfwc.com/wildlifehabitats/profiles/saltwater/snapper/mutton-snapper/); [adult temperature-selection study](https://link.springer.com/article/10.1186/s40317-021-00237-z).

### Sheepshead (*Archosargus probatocephalus*)
- SST: provisional. A federal species account reports broad environmental temperatures of about 8-30 °C, not a preferred SST curve; the configured 12-28 °C / 16-24 °C bands remain unvalidated.
- Depth: partly_sourced. FWC and Florida Museum support coastal structure, tidal-creek, estuarine, seagrass and mud-bottom habitat across life stages, but not the exact 0.5-15 m / 1-8 m bathymetric preference.
- Season presence: partly_sourced. FWC reports nearshore spawning movement and March-April spawning; Florida Museum records early-spring spawning and Gulf larvae January-May. The configured December-April window and January-March peak scores are not a validated catch curve.
- Replaced generic homepage-only citations with specific FWC, Florida Museum and federal environmental-account sources.
- Sources: [FWC sheepshead profile](https://myfwc.com/wildlifehabitats/profiles/saltwater/porgy/sheepshead/); [Florida Museum sheepshead profile](https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/sheepshead/); [federal environmental account](https://www.govinfo.gov/content/pkg/GOVPUB-I-c8f81a7f04971b438a7ada229aea835f/pdf/GOVPUB-I-c8f81a7f04971b438a7ada229aea835f.pdf).

### Southern flounder (*Paralichthys lethostigma*)
- SST: provisional. The reported broad 5-35 °C tolerance is not a preferred SST curve and does not validate the configured 14-28 °C / 18-25 °C intervals.
- Depth: partly_sourced. Sources support shallow muddy/silty estuarine and tidal-creek habitat, juvenile soft-bottom nursery areas, and adult offshore spawning migrations; these life-stage and seasonal habitats do not validate one universal 0.5-25 m / 1-10 m preference.
- Season presence: partly_sourced. SCDNR and Gulf spawning sources support fall offshore migration and winter spawning (Gulf profile October-January), but not a South Florida catch curve.
- **Regional applicability warning:** a 2023 fisheries assessment cites evidence that southern flounder are absent from southern Florida between the Loxahatchee and Caloosahatchee rivers. This conflicts with treating the species as a routine South Florida target. The issue is recorded for a separate geographic/model-scope decision; no factor was disabled and no score changed.
- Sources: [SCDNR species account](https://www.dnr.sc.gov/marine/species/southernflounder.html); [GCOOS Gulf spawning profile](https://geo.gcoos.org/restore/species_profiles/Southern%20Flounder/); [Seafood Watch 2023 assessment](https://www.seafoodwatch.org/globalassets/sfw/pdf/expert-review/030623/seafood-watch-southern-flounder-us-27899.pdf); [federal species account](https://www.govinfo.gov/content/pkg/GOVPUB-HS4_100-PURL-gpo255991/pdf/GOVPUB-HS4_100-PURL-gpo255991.pdf).

### Wahoo (*Acanthocybium solandri*)
- SST: partly_sourced. Florida Straits tags from four fish recorded over 90% of time in approximately 17.5-27.5 °C water; ICCAT summarizes a broader 20-30 °C preference. This supports broad thermal context, not a South Florida catch-probability curve.
- Bottom slope: partly_sourced. Banks, drop-offs and pelagic features are documented, but the 2 km bathymetric slope metric and monotonic score are not calibrated.
- SST gradient and chlorophyll gradient remain provisional; reviewed sources do not validate their runtime magnitudes as suitability responses.
- Current convergence: partly_sourced. Association with current lines and floating objects is supported, but not the exact current-convergence calculation.
- Bottom depth: weak_factor. Tag-derived vertical fish depth is not seafloor bathymetry; retain only as a weak offshore screen.
- Season presence: partly_sourced. ICCAT reports year-round Gulf/Caribbean presence and northwest Atlantic summer spawning; Florida Museum reports western-central Atlantic spawning mainly May-August. Neither validates the configured October-March angler-derived fishing window or November-February peaks.
- Gulf Stream edge: partly_sourced. East Florida movements may be associated with the Gulf Stream, but no distance-response curve validates the configured band.
- Sources: [NC Sea Grant Florida Straits tagging summary](https://ncseagrant.ncsu.edu/hooklinescience/where-do-wahoo-spend-time-in-the-water-column/); [ICCAT Wahoo Manual](https://www.iccat.int/Documents/SCRS/Manual/CH2/2_1_10_10_WAH_ENG.pdf); [Florida Museum wahoo profile](https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/wahoo/); [ICCAT western North Atlantic tagging synthesis](https://www.iccat.int/Documents/CVSP/CV073_2017/n_9/CV073093163.pdf).

### Batch C cumulative disposition
All 29 of the originally elevated-risk multi-factor profiles have now received source-by-source review. Across the five profiles in this final batch, 26 active factors were examined. The 29-profile review is complete; the next step is to reconcile the refreshed validator artifact and proceed to the remaining partial-risk and documented multi-factor profiles. Southern flounder's regional distribution conflict must remain an explicit open issue until separately resolved.


## Validator reconciliation after Batch C | 2026-11-17

Python CI [#44127699186](https://github.com/markeetox/LUPITA/actions/runs/44127699186) passed **307 tests, 0 failures, 115 warnings**. The species validator inspected 130 profiles: 130 parsed, 130 structurally valid, 0 model-compatibility issues, 0 JSON parse errors. The audit artifact is [lupita-species-audit #14347289280](https://github.com/markeetox/LUPITA/actions/runs/44127699186/artifacts/14347289280).

Current validator distribution:
- Evidence risk: 30 elevated, 48 partial, 52 documented.
- Multi-factor subset: 16 elevated, 13 partial, 51 documented.
- Other single-factor subset: 7 elevated, 20 partial, 0 documented.
- Temperature-only site subset: 7 elevated, 15 partial, 1 documented.
- Combined active uncertain factor weight: 10.34 (weight sum, not probability or percentage).
- Classification: 127 NEEDS MODEL REBUILD and 3 NEEDS RESEARCH. This is the validator's biological-completeness prioritization, not a count of malformed profiles or runtime incompatibilities.
- Findings: 0 errors, 488 warnings, 122 informational findings.

The 16 currently elevated multi-factor profiles are African pompano, Almaco jack, Atlantic blue marlin, Atlantic sailfish, Atlantic tarpon, Blackfin tuna, Cobia, Common snook, Hogfish, King mackerel, Mahi-mahi, Mutton snapper, Sheepshead, Snowy grouper, Southern flounder, and Wahoo. They are already included in the completed 29-profile source review; their remaining elevated classification reflects unresolved evidence limits, not an unreviewed queue.

The 13 partial-risk multi-factor profiles are Atlantic bluefin tuna, Black grouper, Black sea bass, Cubera snapper, Florida pompano, Gag grouper, Gray (mangrove) snapper, Gray triggerfish, Jack crevalle, Red drum, Red grouper, Red snapper, and Scamp grouper. These are also already covered by the earlier source-by-source reviews.

**Next review queue:** the 51 documented multi-factor profiles. “Documented” means the current metadata passes the validator's source-reference/documentation criteria; it does not mean every biological claim or numeric response curve has been independently validated. Continue checking factor-by-factor claim fit, region, life stage, runtime-variable match, and whether occurrence/tolerance is being mistaken for preference. Keep numerical model behavior unchanged.


## Documented multi-factor review: first Pacific rockfish batch | 2026-11-17

Started source-by-source claim-fit review of the 51 multi-factor profiles currently classified as documented by the validator. “Documented” means the current source metadata meets validator criteria; it is not independent proof that each biological value is valid.

Reviewed five Pacific rockfish profiles across 11 active factors. Replaced generic fishing-regulations-page citations with species-specific agency and research sources. No numeric ranges, ideal intervals, weights, active flags, gates, required flags, score behavior, confidence behavior, or data ingestion changed.

### Black rockfish (*Sebastes melanops*)
- SST: partly_sourced. Early-life studies report young fish in nearshore/estuarine thermal environments around 8-18 °C in summer and offshore winter/spring waters around 14-15 °C. These are juvenile observations, not adult preferred SST or a universal catch curve.
- Depth: partly_sourced. WDFW reports most fish shallower than about 73 m, with a broad maximum to 366 m; ODFW describes common occurrence from 0-40 fathoms. This supports the outer 5-80 m screen but not the 7-75 m ideal.
- Bottom curvature: partly_sourced. Rocky reef/pinnacle/kelp association is documented, but not a quantitative response to the runtime curvature metric.
- Sources: [WDFW black rockfish](https://wdfw.wa.gov/species-habitats/species/sebastes-melanops); [ODFW black rockfish](https://nrimp.dfw.state.or.us/MRP/default.aspx?pagename=SgfSpeciesInfoBlack+Rockfish); [NOAA early-life growth/temperature research](https://repository.library.noaa.gov/view/noaa/39580/noaa_39580_DS1.pdf).

### Blue rockfish (*Sebastes mystinus*)
- SST: needs_source. NOAA's California climate assessment describes SST/upwelling effects on prey and recruitment, but does not establish a numeric preferred SST interval. The configured 9-17 °C / 11-15 °C values remain unsupported.
- Depth: partly_sourced. WDFW describes near-surface to roughly 300-foot habitat over reefs, pinnacles and kelp; ODFW reports broad occurrence with common use of the upper 50 fathoms. This supports habitat context, not the 7-85 m ideal.
- Sources: [WDFW blue rockfish](https://wdfw.wa.gov/species-habitats/species/sebastes-mystinus); [ODFW blue rockfish](https://nrimp.dfw.state.or.us/mrp/default.aspx?pagename=SgfSpeciesInfoBlue+Rockfish); [NOAA climate vulnerability assessment](https://repository.library.noaa.gov/view/noaa/13953/noaa_13953_DS1.pdf).

### Bocaccio rockfish (*Sebastes paucispinis*)
- SST: needs_source. Reviewed NOAA/WDFW/COSEWIC sources describe habitat and depth but do not support a numeric preferred SST curve. Pelagic juvenile and demersal/midwater adult stages are not interchangeable.
- Depth: partly_sourced. NOAA reports adult rocky habitat at 130-980 feet (about 40-299 m); WDFW reports 20-475 m, with highest abundance around 95-225 m. Juveniles settle shallower and move deeper with age; adults can also be midwater. The configured 20-200 m / 22-195 m intervals are not universal preferences.
- Sources: [NOAA Fisheries bocaccio](https://www.fisheries.noaa.gov/species/bocaccio); [WDFW bocaccio](https://wdfw.wa.gov/species-habitats/species/sebastes-paucispinis); [COSEWIC assessment](https://www.canada.ca/en/environment-climate-change/services/species-risk-public-registry/cosewic-assessments-status-reports/bocaccio-2013.html).

### Canary rockfish (*Sebastes pinniger*)
- SST: needs_source. A Washington/Oregon trawl study reports bottom temperatures of 6.2-9.0 °C where canary rockfish were caught, but temperature was not significant in the presence model and was highly correlated with bottom depth. Bottom-trawl temperature is not satellite SST and does not support the configured 7-15 °C / 9-13 °C SST suitability curve.
- Depth: partly_sourced. NOAA reports adult habitat primarily 160-820 feet (about 49-250 m), sometimes to 1400 feet; a trawl analysis found 57-307 m, with over 90% of catch tows between 57 and 199 m. The configured 20-150 m / 22-145 m ranges omit much of observed adult habitat.
- Sources: [NOAA Fisheries canary rockfish](https://www.fisheries.noaa.gov/species/canary-rockfish/overview); [FAO AGRIS record of Vestfals 2009 habitat analysis](https://agris.fao.org/search/en/providers/122415/records/6473683a08fd68d54605dee0).

### Copper rockfish (*Sebastes caurinus*)
- SST: partly_sourced. A NOAA Puget Sound status review reports environmental temperatures around 7-13 °C, and a young-of-year thermal-performance study documents temperature effects on recruit behavior, growth and survival. These are regional/early-life findings, not an adult preferred satellite-SST curve.
- Depth: partly_sourced. ODFW describes a shallow rocky-water species occurring to 100 fathoms; NOAA documents adults on rocky reefs and rock-sand bottoms, with marked regional depth variation. This supports broad habitat context but not one universal 5-100 m / 7-95 m ideal.
- Sources: [ODFW copper rockfish](https://nrimp.dfw.state.or.us/mrp/default.aspx?pagename=SgfSpeciesInfoCopper+Rockfish); [NOAA Puget Sound copper rockfish status review](https://repository.library.noaa.gov/view/noaa/29024/noaa_29024_DS1.pdf); [Schaal and Lotterhos 2021 thermal-performance study](https://academic.oup.com/icesjms/article/78/5/1684/6237190).

### Documented-profile review progress
Five of 51 documented multi-factor profiles reviewed across 11 active factors. This first batch shows why source-path validation alone is not enough: species-specific depth and habitat evidence can coexist with unsupported SST bands, bottom-temperature/SST mismatches, or unvalidated ideal intervals. Continue by ecological/factor family; preserve numeric and runtime behavior until separately reviewed and approved.


## Documented multi-factor review: second Pacific nearshore batch | 2026-11-17

Reviewed Gopher rockfish, Kelp rockfish, Olive rockfish, Treefish, and Halfmoon across 10 active factors. Replaced generic CDFW sport-regulations citations with species-specific CDFW, ODFW, NOAA, Smithsonian Tropical Research Institute, FishBase and aquarium species accounts. No numeric ranges, ideal intervals, weights, active flags, gates, required flags, scoring, confidence or runtime behavior changed.

### Gopher rockfish (*Sebastes carnatus*)
- SST: needs_source. Species/habitat sources do not establish a numeric preferred SST range.
- Depth: partly_sourced. CDFW reports adults up to about 80 m, most common at 10-35 m; ODFW reports rocky areas to 40 fathoms. This supports broad occurrence, not the 4-45 m ideal.
- Sources: [CDFW distribution account](https://nrm.dfg.ca.gov/FileHandler.ashx?DocumentID=33871); [ODFW species account](https://nrimp.dfw.state.or.us/MRP/default.aspx?p=113).

### Kelp rockfish (*Sebastes atrovirens*)
- SST: needs_source. Reviewed sources do not establish numeric adult SST preference.
- Depth: partly_sourced. FishBase reports demersal occurrence 9-46 m in kelp beds and rocky areas; California coastal survey appendix reports 0-46 m. This supports the broad configured range, not the ideal interval.
- Sources: [FishBase species summary](https://fishbase.org/FieldGuide/FieldGuideSummary.php?GenusName=Sebastes&SpeciesName=atrovirens&pda=1&sps=); [California Water Boards coastal survey appendix](https://www.waterboards.ca.gov/water_issues/programs/swamp/docs/coast_study/bog2012may/apx1.pdf).

### Olive rockfish (*Sebastes serranoides*)
- SST: needs_source. Reviewed sources document habitat and depth but no numeric preferred SST curve.
- Depth: partly_sourced. NOAA's 2026 groundfish synthesis reports all life stages in kelp forests to 172 m; AFSC guide reports common 0-16 fathoms and maximum around 146 m. The configured 5-80 m band is not a complete species depth envelope.
- Sources: [NOAA Pacific groundfish amendment analysis](https://www.fisheries.noaa.gov/s3/2026-02/am-37-fpa-analysis-01-2026.pdf); [NOAA AFSC guide to Northeast Pacific rockfishes](https://apps-afsc.fisheries.noaa.gov/Publications/AFSC-TM/NOAA-TM-AFSC-117.pdf).

### Treefish (*Sebastes serriceps*)
- SST: needs_source. A subtropical climate label is not a measured thermal preference and does not validate the configured SST band.
- Depth: partly_sourced. NOAA describes high-relief habitat shallower than 60 m; California accounts describe shallow rocky reefs/caves to about 46 m and limited home ranges. The outer band is plausible but the ideal is not a quantified preference.
- Sources: [NOAA Pacific groundfish amendment analysis](https://www.fisheries.noaa.gov/s3/2026-02/am-37-fpa-analysis-01-2026.pdf); [California Department of Fish and Game species account](https://nrm.dfg.ca.gov/FileHandler.ashx?DocumentID=33928); [NOAA AFSC guide](https://apps-afsc.fisheries.noaa.gov/Publications/AFSC-TM/NOAA-TM-AFSC-95.pdf).

### Halfmoon (*Medialuna californiensis*)
- SST: needs_source. Species sources describe warm-region distribution and seasonal occurrence but no numeric preferred SST or validated thermal-response curve; historical warm-period range expansion is not a preference band.
- Depth: partly_sourced. STRI reports 0-44 m over rocky bottoms/algal beds; Aquarium of the Pacific describes use high in the water column over rocks and at mid-depth over kelp. The configured 1-30 m range excludes some reported depth and ideal is not a measured preference.
- Sources: [Smithsonian Tropical Research Institute species account](https://biogeodb.stri.si.edu/sftep/en/thefishes/species/1579); [Aquarium of the Pacific](https://www.aquariumofpacific.org/onlinelearningcenter/species/halfmoon); [Georgia Aquarium](https://www.georgiaaquarium.org/animal/halfmoon/).

### Documented-profile review progress
Ten of 51 profiles reviewed across 21 active factors. The second batch reinforces the same distinction: specific species sources often support habitat and depth occurrence, but do not establish numeric SST preference or ideal intervals. “Documented” source metadata is not equivalent to a validated numeric suitability curve.


## Documented multi-factor review: third California coastal batch | 2026-11-17

Reviewed Kelp bass, California yellowtail, Giant sea bass, Opaleye, and Spotted sand bass across 10 active factors. Replaced generic sport-regulation citations with CDFW enhanced status/species reports, Smithsonian Tropical Research Institute, FishBase, USGS and peer-reviewed temperature/tagging sources. No numeric ranges, ideal intervals, weights, active flags, gates, required flags, scoring, confidence or runtime behavior changed.

### Kelp bass (*Paralabrax clathratus*)
- SST: partly_sourced. CDFW reports larval survival is highest during extended warmer-than-average SST and that local temperature/current regimes influence recruitment. This supports relevance, not a numeric adult/larval optimum or the configured range.
- Depth: partly_sourced. CDFW reports surface to 46 m, most abundant 2.7-21.3 m; FishBase reports most occurrence around 2.4-21 m. The configured outer band is broadly plausible, but ideal extends beyond the best-documented abundance band.
- Sources: [CDFW 2019 Enhanced Status Report](https://nrm.dfg.ca.gov/FileHandler.ashx?DocumentID=174760); [Smithsonian Eastern Pacific species account](https://biogeodb.stri.si.edu/sftep/en/thefishes/species/1167/on).

### California yellowtail (*Seriola lalandi*)
- SST: partly_sourced. FishBase reports warmer-water affinity around 18-24 °C; California spawning temperatures have been reported at 16.5-22.0 °C. A 2026 Tasman Sea satellite-tagging study of adult S. lalandi reports broad thermal occupancy and core use around 17.4-20.8 °C, but is geographically distinct. This is broad thermal context, not a universal California SST catch curve.
- Depth: weak_factor. The fish is mobile and pelagic/benthopelagic, using coastal and oceanic waters, reefs, kelp beds and islands; reported vertical depths extend well beyond the configured 0-50 m. Runtime bathymetry is seafloor depth, not fish vertical depth, so retain only as a weak nearshore/reef proxy.
- Sources: [California yellowtail spawning study](https://pmc.ncbi.nlm.nih.gov/articles/PMC5027219/); [2026 adult satellite-tagging study](https://doi.org/10.1139/cjfas-2025-0343); [FishBase species summary](https://www.fishbase.org/summary/382).

### Giant sea bass (*Stereolepis gigas*)
- SST: needs_source. Reviewed species sources do not establish a numeric preferred SST or validated thermal response curve.
- Depth: partly_sourced. STRI reports 5-45 m rocky-bottom/algal habitat; Aquarium of the Pacific describes adults near rocky drop-offs deeper than 30 m, juveniles on sand/mud around 21 m, and seasonal summer-shallow/winter-deeper movement. Other accounts report deeper ridges around 70-80 m. One universal band across stages/seasons is not established.
- Sources: [Smithsonian Eastern Pacific species account](https://biogeodb.stri.si.edu/sftep/en/thefishes/species/1098/on); [Aquarium of the Pacific giant sea bass](https://www.aquariumofpacific.org/onlinelearningcenter/species/giant_sea_bass).

### Opaleye (*Girella nigricans*)
- SST: provisional. FishBase's broad 0-33 °C environmental envelope and climate labels are not a preferred SST curve.
- Depth: partly_sourced. STRI reports 1-32 m on rocky shores; FishBase reports 2-30 m, commonly 2-6 m, and resident intertidal/kelp behavior. This supports shallow habitat but not the configured ideal interval.
- Sources: [Smithsonian Eastern Pacific species account](https://biogeodb.stri.si.edu/sftep/en/thefishes/species/1566); [FishBase opaleye](https://fishbase.se/summary/girella-nigricans).

### Spotted sand bass (*Paralabrax maculatofasciatus*)
- SST: partly_sourced. FishBase reports broad 7.5-32 °C tolerance and a model-derived preferred-temperature estimate of 18.1-26.8 °C (mean 22.3 °C, 42 cells). CDFG describes shallow southern California bays/harbors as warm-water refuges. The model estimate is not field-validated and does not establish a catch curve.
- Depth: partly_sourced. CDFG describes shallow sandy/muddy bays, harbors and lagoons with eelgrass/surfgrass/rock relief; FishBase reports 1-61 m. The configured shallow band is plausible for localized bay populations, not a universal depth preference.
- Sources: [CDFG spotted sand bass account](https://nrm.dfg.ca.gov/FileHandler.ashx?DocumentID=34355&inline=); [FishBase spotted sand bass](https://www.fishbase.org/summary/3336); [USGS species profile](https://nas.er.usgs.gov/queries/factsheet.aspx?SpeciesID=972).

### Documented-profile review progress
Fifteen of 51 profiles reviewed across 31 active factors. The audit continues to separate numeric temperature tolerance, modeled temperature estimates, spawning temperature, and observed habitat use. None is silently promoted to a universal preferred SST curve.


## Documented multi-factor review: fourth demersal flatfish/cod batch | 2026-11-17

Reviewed California halibut, Pacific halibut, Petrale sole, Starry flounder, and Pacific cod across 10 active factors. Added NOAA, USGS, IPHC, WDFW, ODFW and DFO sources. No numeric ranges, ideal intervals, weights, active flags, gates, required flags, scoring, confidence or runtime behavior changed.

### California halibut (*Paralichthys californicus*)
- SST: partly_sourced. NOAA's egg-suitability analysis uses 12-20 °C; USGS laboratory work found eggs hatch at 12, 16 and 20 °C, while juvenile thermal preference varies with acclimation (final preferendum 18.4 °C). This is life-stage-specific thermal evidence, not a universal adult catch curve.
- Depth: partly_sourced. NOAA reports most mature fish shallower than 30 m, though mature fish occur to about 100 m; juveniles rely on estuaries/embayments. The configured 2-60 m interval and 4-55 m ideal are not life-stage-specific.
- Sources: [NOAA SST assessment](https://repository.library.noaa.gov/view/noaa/48188/noaa_48188_DS1.pdf); [USGS early-life temperature study](https://pubs.usgs.gov/publication/70180738); [NOAA habitat synthesis](https://storage.googleapis.com/nmfs_odp_swfsc/Publications/Files/CR/2025/2025Purcell2.pdf).

### Pacific halibut (*Hippoglossus stenolepis*)
- SST: needs_source. IPHC reports adult bottom-water temperatures around 3-8 °C; this cannot validate the model's satellite SST factor.
- Depth: partly_sourced. IPHC reports summer feeding to about 500 m, most frequent catches around 30-270 m, and deeper offshore winter spawning. Juveniles use shallower habitat; the configured band does not represent all life stages/seasons.
- Sources: [IPHC stock status and biology](https://www.iphc.int/research/pacific-halibut-stock-status-biology/); [USGS depth synthesis](https://pubs.usgs.gov/sir/2016/5038/sir20165038_profiles11.pdf); [NOAA commercial fishery species account](https://repository.library.noaa.gov/view/noaa/10936/noaa_10936_DS1.pdf).

### Petrale sole (*Eopsetta jordani*)
- SST: needs_source. DFO documents tolerance of varying bottom temperatures, not preferred satellite SST.
- Depth: partly_sourced. WDFW reports 18-550 m, with seasonal abundance shifting from 55-128 m in April-October to 274-457 m in winter. The configured 20-200 m band omits much of the winter spawning distribution.
- Sources: [WDFW petrale sole](https://wdfw.wa.gov/species-habitats/species/eopsetta-jordani); [ODFW petrale sole](https://nrimp.dfw.state.or.us/mrp/default.aspx?page=109); [DFO petrale sole](https://www.dfo-mpo.gc.ca/species-especes/profiles-profils/petrale-sole-plie-californie-eng.html).

### Starry flounder (*Platichthys stellatus*)
- SST: provisional. San Francisco Bay age-0 observations span roughly 8-23 °C, but this is broad occurrence, not a preferred adult SST curve.
- Depth: partly_sourced. WDFW reports 0-375 m, most commonly above 146 m, nearshore and sometimes brackish/fresh; ODFW reports most fish above 80 fathoms and juveniles intertidal. The configured 1-50 m band captures only shallow nearshore habitat.
- Sources: [WDFW starry flounder](https://wdfw.wa.gov/species-habitats/species/platichthys-stellatus); [ODFW starry flounder](https://nrimp.dfw.state.or.us/mrp/default.aspx?page=114); [California nursery synthesis](https://www.pacificfishhabitat.org/wp-content/uploads/2017/09/tnc_ca_fishnurseries_lowres_min.pdf).

### Pacific cod (*Gadus macrocephalus*)
- SST: needs_source. NOAA survey values of -1.6 to 8.4 °C (eastern Bering Sea) and -1.6 to 11 °C (northern Bering Sea) are bottom-trawl temperatures, not satellite SST or preferred temperature.
- Depth: partly_sourced. NOAA describes winter spawning on the outer/upper shelf and summer movement to shallower shelf feeding grounds; the configured 20-200 m range is a shelf screen, not a universal depth preference.
- Sources: [NOAA Pacific cod](https://www.fisheries.noaa.gov/species/pacific-cod); [NOAA 2022 Bering Sea trawl survey](https://repository.library.noaa.gov/view/noaa/50154/noaa_50154_DS1.pdf); [NOAA species depth record](https://repository.library.noaa.gov/view/noaa/5807/noaa_5807_DS1.pdf).

### Documented-profile review progress
Twenty of 51 profiles reviewed across 41 active factors. The review continues to distinguish surface temperature from bottom temperature and life-stage thermal response, and to preserve seasonal depth migrations rather than compressing them into a single universal preference interval.


## Documented multi-factor review: Pacific salmon thermal-habitat batch | 2026-11-17

Reviewed Chinook, Coho, Chum, Pink and Sockeye salmon across 10 active factors. Replaced generic regulation-page citations with the 2024 North Pacific salmon temperature-distribution study, NOAA species sources and telemetry/migration research. No numeric ranges, ideal intervals, weights, active flags, gates, required flags, scoring, confidence or runtime behavior changed.

### Shared interpretation
Langan et al. (2024) used North Pacific coastal/high-seas survey data from 1953-2022 to model species-specific marine preferred SST. These are modeled distribution-based thermal ranges, not laboratory physiological optima and not stock-specific coastal catch curves. The profiles' configured SST intervals are generally shifted warmer than the modeled preferences. All five species are pelagic during the marine phase; runtime bathymetry is seafloor depth, not fish vertical depth, so it is retained as a weak shelf/coastal context proxy rather than a direct preference factor.

### Chinook salmon (*Oncorhynchus tshawytscha*)
- SST: partly_sourced. Modeled preferred SST 3.6-12.3 °C (80% HDI), core 5.8-10.3 °C, median 8.3 °C, mode 8.7 °C. Hinke et al. archival tags off Oregon/California found persistent use of 8-12 °C water. Configured 8-16 °C / 10-14 °C is warmer and misses much of the modeled interval.
- Depth: weak_factor. Fish vertical occupancy ranges from surface to hundreds of metres; it is not seabed depth. Nearshore shelf association does not establish a universal bottom-depth band.
- Sources: [Langan et al. 2024](https://onlinelibrary.wiley.com/doi/full/10.1111/faf.12825); [Hinke et al. 2005](https://www.int-res.com/articles/meps2005/304/m304p207.pdf); [NOAA 2024 nearshore Chinook study](https://repository.library.noaa.gov/view/noaa/69517).

### Coho salmon (*Oncorhynchus kisutch*)
- SST: partly_sourced. Modeled preferred SST 6.1-13.2 °C, core 7.2-11.0 °C, median 9.5 °C, mode 8.9 °C. Configured 7-15 °C / 9-13 °C overlaps but is weighted toward the warm edge.
- Depth: weak_factor. Marine coho may remain coastal or migrate long distances; seafloor depth is not fish vertical depth and no universal 0-60 m bottom-depth preference is established.
- Sources: [Langan et al. 2024](https://onlinelibrary.wiley.com/doi/full/10.1111/faf.12825); [NOAA coho science](https://www.fisheries.noaa.gov/species/coho-salmon/science); [USFWS coho account](https://www.fws.gov/species/coho-salmon-oncorhynchus-kisutch).

### Chum salmon (*Oncorhynchus keta*)
- SST: partly_sourced. Modeled preferred SST 1.3-12.6 °C, core 2.8-9.3 °C, median 7.1 °C, mode 5.8 °C. A 2025 NOAA-authored western Alaska migration-corridor study also models SST thermal suitability. Configured 6-14 °C / 8-12 °C is warmer and excludes much of the colder modeled preference.
- Depth: weak_factor. Chum migrate across estuarine, coastal and open-ocean habitats; bathymetry is not fish vertical depth and no universal 0-60 m bottom-depth preference is established.
- Sources: [Langan et al. 2024](https://onlinelibrary.wiley.com/doi/full/10.1111/faf.12825); [Lemagie et al. 2025](https://repository.library.noaa.gov/view/noaa/71046/noaa_71046_DS1.pdf); [NOAA chum science](https://www.fisheries.noaa.gov/species/chum-salmon/science).

### Pink salmon (*Oncorhynchus gorbuscha*)
- SST: partly_sourced. Modeled preferred SST differs by brood-cycle parity: even-year 3.0-12.6 °C (core 4.3-9.4, median 7.9, mode 6.6); odd-year 3.0-11.8 °C (core 4.3-8.9, median 7.5, mode 6.4). Configured 6-15 °C / 8-13 °C is warmer and omits much of the modeled cold-side preference.
- Depth: weak_factor. Pink salmon are pelagic during marine feeding; NOAA notes fishing gear rarely contacts the ocean floor. Bathymetry is only a weak coastal/shelf proxy.
- Sources: [Langan et al. 2024](https://onlinelibrary.wiley.com/doi/full/10.1111/faf.12825); [NOAA pink salmon](https://www.fisheries.noaa.gov/species/pink-salmon).

### Sockeye salmon (*Oncorhynchus nerka*)
- SST: partly_sourced. Modeled preferred SST 1.0-11.5 °C, core 2.2-7.6 °C, median 6.1 °C, mode 5.0 °C, the coldest modeled niche among the six species. A separate juvenile Bering Sea study found strongest positive density effects around 11 °C and a threshold near 12 °C, demonstrating life-stage differences. Configured 6-14 °C / 8-12 °C is shifted warm.
- Depth: weak_factor. Pelagic migration and vertical occupancy vary by life stage, season and region; bathymetry is not fish vertical depth.
- Sources: [Langan et al. 2024](https://onlinelibrary.wiley.com/doi/full/10.1111/faf.12825); [NOAA sockeye](https://www.fisheries.noaa.gov/species/sockeye-salmon); [juvenile Bering Sea study](https://pmc.ncbi.nlm.nih.gov/articles/PMC10999952/).

### Documented-profile review progress
Twenty-five of 51 profiles reviewed across 51 active factors. Salmon profiles expose a systematic model limitation: the SST layer is a surface proxy for a marine-phase species whose experienced temperature can differ by depth, while the active bathymetry factor is not the fish's vertical depth. Preserve these distinctions and do not change model weights or numeric bands in this evidence-only pass.


## Documented multi-factor review: fifth Pacific rocky-reef batch | 2026-11-17

Reviewed Lingcod, Cabezon, Kelp greenling, Ocean whitefish and Yelloweye rockfish across 11 active factors. Replaced generic regulation-page references with WDFW, ODFW, CDFW, NOAA AFSC, IUCN and Smithsonian sources. No numeric ranges, ideal intervals, weights, active flags, gates, required flags, scoring, confidence or runtime behavior changed.

### Lingcod (*Ophiodon elongatus*)
- SST: needs_source. Species accounts describe temperature tolerance but do not establish a numeric preferred SST curve.
- Depth: partly_sourced. WDFW reports most adults on rocky bottom at 10-100 m, with records to 427 m; ODFW reports adults near rocks and juveniles in bays. Configured 10-150 m / 12-145 m is not a universal stage-specific preference.
- Bottom curvature: partly_sourced. Rocky reef/complex hard-bottom association supports habitat relevance but not a direct quantitative response to the runtime curvature metric.
- Sources: [WDFW lingcod](https://wdfw.wa.gov/species-habitats/species/ophiodon-elongatus); [ODFW lingcod](https://nrimp.dfw.state.or.us/mrp/default.aspx?pagename=SgfSpeciesInfoLingcod).

### Cabezon (*Scorpaenichthys marmoratus*)
- SST: needs_source. Reviewed species sources provide no numeric preferred SST evidence.
- Depth: partly_sourced. CDFG reports adults intertidal-110 m (most common intertidal-30 m), juveniles in tidepools, and egg nests intertidal-15 m; adults associate with hard bottom. Configured 2-50 m / 4-45 m is not life-stage-specific.
- Sources: [CDFG cabezon life-stage distribution](https://nrm.dfg.ca.gov/FileHandler.ashx?DocumentID=33887); [ODFW cabezon](https://nrimp.dfw.state.or.us/mrp/default.aspx?page=89).

### Kelp greenling (*Hexagrammos decagrammus*)
- SST: needs_source. Habitat sources do not establish a numeric preferred SST curve.
- Depth: partly_sourced. WDFW reports rocky inshore/kelp habitat to about 46 m; ODFW reports 25 fathoms; IUCN describes intertidal/subtidal rocky reefs, kelp and eelgrass typically to 50 m. A Farallon survey reports 0-100 m. Configured 1-40 m / 3-35 m is plausible shallow habitat, not a universal preference.
- Sources: [WDFW kelp greenling](https://wdfw.wa.gov/species-habitats/species/hexagrammos-decagrammus); [ODFW greenling](https://nrimp.dfw.state.or.us/mrp/default.aspx?p=74); [IUCN assessment](https://doi.org/10.2305/IUCN.UK.2020-2.RLTS.T158882453A158883838.en).

### Ocean whitefish (*Caulolatilus princeps*)
- SST: needs_source. Reviewed species accounts do not establish a numeric preferred SST or validated thermal response curve.
- Depth: partly_sourced. STRI reports bottom-associated rock/sand habitat from 3-160 m, including 80-160 m observations at Isla del Coco. Configured 10-100 m / 12-95 m is not a complete species depth envelope.
- Sources: [Smithsonian Eastern Pacific species account](https://biogeodb.stri.si.edu/sftep/en/thefishes/species/1220); [2018 Isla del Coco reef-fish synthesis](https://stri-apps.si.edu/docs/publications/pdfs/Sanchez-Jimenez_A_et_al.2018-Rev_Biol_Trop.66-Suplemento_5_S1-S113.pdf).

### Yelloweye rockfish (*Sebastes ruberrimus*)
- SST: needs_source. Climate sensitivity through prey availability does not establish a numeric SST preference.
- Depth: partly_sourced. WDFW reports 11-549 m, adults typically 91-180 m, and juveniles shallower; adults use deep, high-relief complex rock. NOAA AFSC gives common depths around 50-400 m. Configured 30-200 m overlaps adult habitat but not the full ontogenetic range.
- Sources: [WDFW yelloweye rockfish](https://wdfw.wa.gov/species-habitats/species/sebastes-ruberrimus); [ODFW yelloweye](https://nrimp.dfw.state.or.us/MRP/default.aspx?pagename=SgfSpeciesInfoYelloweye+Rockfish); [NOAA AFSC rockfish guide](https://apps-afsc.fisheries.noaa.gov/Publications/AFSC-TM/NOAA-TM-AFSC-95.pdf).

### Documented-profile review progress
Thirty of 51 profiles reviewed across 62 active factors. The same evidence rule holds: a specific species page can substantiate habitat/depth occurrence without supporting an SST optimum, and habitat relief does not automatically validate a numerical bottom-curvature response.
