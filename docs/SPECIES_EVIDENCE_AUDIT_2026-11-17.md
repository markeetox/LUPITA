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
- Bonefish: `provisional` → `partly_sourced`, with adult performance-vs-preference caveats.
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

No numeric range, ideal interval, weight, active flag, gate, required flag, source configuration, score, confidence, ingestion, or publication behavior changed in this research batch. These are research recommendations awaiting approval before profile metadata is edited.


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

