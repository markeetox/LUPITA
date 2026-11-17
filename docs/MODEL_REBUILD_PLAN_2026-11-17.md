# LUPITA controlled model-rebuild plan

**Started:** 2026-11-17  
**Branch:** `main`  
**Status:** Phase 0 scope and identity audit in progress  
**Guardrail:** no prediction weights, biological numeric bands, active flags, gates, score equations, confidence behavior, source selection, ingestion, or publication changes without a separate evidence-backed approval.

## Objective

Turn the completed 130-profile evidence review into a staged rebuild plan. First ensure every profile represents the correct taxon and is only scored inside a defensible geographic and ecological scope. Next ensure each factor matches the physical variable the runtime actually measures. Only then should numeric response curves or weights be considered.

## Phase 0: species identity and geographic applicability

### 0.1 Runtime geographic contract

The configured production source envelope in `config/sources.json` is 15–60°N and 138°W–50°W (`north_america_coastlines`). The grid scorer in `pipeline/scoring.py::score_species` applies a profile's `lat_range` and `lon_range` to eligible cells. If `lat_range` is absent, no latitude restriction is applied. The marine mask removes inland cells but does not represent species-specific coastal distribution or habitat.

**Audit result:** 25 of 130 grid profiles have no `lat_range`. All 25 currently have a longitude range but no latitude restriction:

1. African pompano
2. Almaco jack
3. Black grouper
4. Black sea bass
5. Blackfin tuna
6. Blue marlin
7. Bluefin tuna
8. Cobia
9. Florida pompano
10. Gag grouper
11. Gray triggerfish
12. Jack crevalle
13. King mackerel
14. Mahi-mahi
15. Mangrove snapper
16. Mutton snapper
17. Red drum
18. Red grouper
19. Red snapper
20. Sailfish
21. Scamp grouper
22. Sheepshead
23. Snowy grouper
24. Southern flounder
25. Wahoo

These profiles can currently be scored anywhere in the source envelope that passes their longitude filter and other factor rules, including latitudes outside their documented species distribution. This is a geographic eligibility risk, not a JSON or CI failure.

The existing longitude boxes are broad rectangles (Western Atlantic/Gulf and Eastern Pacific). A bounding rectangle is a coarse first filter, not a coastal distribution polygon. It can include offshore, estuarine, or coast segments where a species is absent.

**Action:** do not fill the 25 missing latitude bounds by guessing. For each profile, research a defensible population/region range and record the source, life stage, and known discontinuities. Where distribution is disjoint or coastline-specific, use a regional mask or separate regional profile rather than forcing a misleading rectangle.

### 0.2 Resolved taxonomic metadata

| Profile | Prior name | Current decision | Evidence and limitation |
|---|---|---|---|
| Opah, Eastern North Pacific | `Lampris guttatus` | `Lampris incognitus` (smalleye Pacific opah) | The 2018 taxonomic revision split the former complex. NOAA's Monterey Bay National Marine Sanctuary checklist identifies `L. incognitus` as the only known opah in the Eastern North Pacific. California Sea Grant describes the coastal North Pacific form as likely `L. incognitus`. Pre-revision Hawaii tagging and California catch studies are not automatically species-specific. |
| Dungeness crab reference | `Cancer magister` | `Metacarcinus magister` | OBIS identifies `Metacarcinus magister` as the accepted name and `Cancer magister` as a superseded combination; the FDA Seafood List uses `Metacarcinus magister`. Historical name retained as an alias. |

These are identity/metadata corrections only. No numeric factor or scoring behavior changed.

### 0.3 Regional and ecological scope decisions still open

**Southern flounder (*Paralichthys lethostigma*)**

The cited distribution account reports the species from Albemarle Sound south to the Loxahatchee River on Florida's Atlantic coast, absent south of Loxahatchee and around the peninsula tip, but present in the Caloosahatchee River Estuary on the southwest coast. The current profile has no latitude bound, so the scorer uses only its broad longitude range. A single latitude rectangle cannot express this disjoint Florida distribution.

Decision needed before South Florida predictions are treated as valid: use a coastal distribution mask, create separate Atlantic/Gulf regional profiles, or exclude the South Florida Atlantic subregion. The Caloosahatchee estuary occurrence should not be erased by an overly broad "absent from South Florida" statement.

**White sturgeon (*Acipenser transmontanus*)**

CDFW describes white sturgeon as primarily resident in large rivers and associated estuaries, with occasional coastal-ocean occurrence. The current model is a marine grid using satellite SST and ETOPO seafloor depth; it has no river flow, channel-depth, or estuary-specific habitat inputs.

Decision needed: exclude it from ocean-grid predictions or design a separate freshwater/estuary model. Do not solve this by merely changing its latitude/longitude box.

### 0.4 Phase 0 next work

1. Build a source-backed geographic-scope register for the 25 profiles without latitude bounds.
2. Review the remaining 105 profiles' rectangular bounds for obvious region, life-stage, and coastline mismatches.
3. Identify profiles whose ranges are disjoint or require estuarine/freshwater polygons.
4. Approve geographic masks or profile splits before changing the scorer.
5. Add tests for any new spatial eligibility contract only after the design is approved.

## Phase 1: measurement and environmental-layer alignment

### Surface temperature versus bottom temperature

The production SST input is NOAA CoastWatch MUR `jplMURSST41` (`analysed_sst`). It is a sea-surface field. A source reporting demersal bottom-water temperature does not directly validate a satellite-SST response curve. Candidate demersal profiles already flagged in the evidence audit include Pacific halibut, Petrale sole, Pacific cod, sablefish, and rock greenling.

**Design options:** retain SST only as an explicitly labelled surface proxy; add a validated bottom-temperature source and independent freshness/coverage diagnostics; or disable/replace SST factors for species whose biology requires bottom temperature. No source switch is approved.

### Seafloor bathymetry versus fish vertical depth

The production `depth_m` layer is ETOPO 2022 seafloor elevation converted to water depth. The source configuration samples 15-arc-second ETOPO at stride 15, approximately 3.75 arc-minutes, and explicitly warns that it is broad regional context, not reef-scale bathymetry.

Fish-tag vertical depth measures where an animal is in the water column. It is not the seafloor depth at its horizontal position. Pelagic and vertically migrating species therefore need factor review before a fish-depth source is used to justify `depth_m`. Candidate profiles include steelhead, tunas, marlin, sharks, opah, and other midwater species. Demersal species can use bathymetry, but their evidence must describe seafloor depth or habitat occupancy rather than only capture depth without context.

**Design options:** keep bathymetry as a coarse habitat proxy with explicit limitations; improve resolution for reef/nearshore applications; or separate fish vertical-depth and seabed-depth variables if both are needed. No layer or factor changes are approved.

## Phase 2: evidence-backed model rebuild queue

Rank candidate rebuilds using:

1. Species identity and geographic eligibility.
2. Whether the factor measures the same physical quantity as the evidence.
3. Active uncertain factor weight and whether the factor is a hard gate.
4. Whether sources support a numeric response curve (not merely occurrence or tolerance).
5. Population, life-stage, season, and fishery relevance.
6. Input coverage, resolution, and freshness in the intended region.

A candidate is not ready for numeric recalibration until its target population, geographic scope, measured variable, and evidence-supported response form are explicit.

## Change-control boundary

Allowed in this planning phase: source-backed taxonomic names, explanatory notes, open-item tracking, and planning documentation.

Not allowed without separate approval: changing numeric ranges/ideals, factor weights, active flags, gates, minimum coverage, scoring equations, confidence labels/caps, environmental source selection, ingestion, or publication behavior.

## Research references

- Opah 2018 taxonomic revision: https://doi.org/10.11646/zootaxa.4413.3.9
- NOAA Monterey Bay National Marine Sanctuary fish checklist (Eastern North Pacific opah identification): https://repository.library.noaa.gov/view/noaa/23850/noaa_23850_DS1.pdf
- California Sea Grant opah profile: https://caseagrant.ucsd.edu/seafood-profiles/opah
- ITIS `Lampris incognitus`: https://www.itis.gov/servlet/SingleRpt/SingleRpt?search_topic=Scientific_Name&search_value=Lampris+incognitus
- OBIS accepted Dungeness crab name: https://obis.org/taxon/452271
- FDA Seafood List `Metacarcinus magister`: https://hfpappexternal.fda.gov/scripts/fdcc/index.cfm?id=Metacarcinus_magister&set=SeafoodList
- Southern flounder distribution: https://www.dnr.sc.gov/marine/species/assets/SpeciesProfileSouthernGulfSummerFlounder.pdf
- CDFW white sturgeon distribution: https://wildlife.ca.gov/Conservation/Fishes/Sturgeon/White-Sturgeon
- Production region and layer definitions: `config/sources.json`
- Geographic scoring behavior: `pipeline/scoring.py::score_species`
