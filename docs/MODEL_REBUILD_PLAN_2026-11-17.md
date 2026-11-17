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


## Phase 0.5: source-backed geographic review of the 25 missing latitude bounds

The first source pass located distribution evidence for all 25 profiles. These statements are retained as source summaries, not converted directly into latitude coordinates. Named endpoints such as Massachusetts, Nova Scotia, Brazil, or the Yucatan are not exact coordinate boundaries, and some species have separate stocks, seasonal movements, or disjoint distributions.

| Profile | Source-backed range statement | Scope caveat / source |
|---|---|---|
| African pompano | Western Atlantic from North Truro, Massachusetts to Santos, Brazil; Gulf and Caribbean included. | WoRMS distribution record: https://www.marinespecies.org/aphia.php?id=159629&p=taxdetails |
| Almaco jack | Western Atlantic from Massachusetts to Brazil; rarely caught north of the Carolinas. | South Atlantic Fishery Management Council: https://safmc.net/species/jack-almaco/ |
| Black grouper | Western Atlantic Massachusetts to Brazil; Gulf and Caribbean; U.S. stock primarily Florida Keys. | NOAA Fisheries: https://www.fisheries.noaa.gov/species/black-grouper/seafood |
| Black sea bass | U.S. East Coast from Cape Cod to Gulf of Mexico. | NOAA identifies Mid-Atlantic and South Atlantic stocks, divided at Cape Hatteras; separate assessment and management contexts. South Florida occurrence is exceptional in some accounts, not a simple continuous range. https://www.fisheries.noaa.gov/species/black-sea-bass and https://www.fisheries.noaa.gov/s3/2026-04/sg_regam37_202604_final.pdf |
| Blackfin tuna | Western Atlantic from Cape Cod to Brazil, including Gulf and Caribbean. | NOAA western Atlantic tuna guide: https://media.fisheries.noaa.gov/dam-migration/guide-to-tunas-of-the-western-atlantic-ocean.pdf |
| Blue marlin | Atlantic occurrence reported approximately 44°N to 30°S. | Florida Museum: https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/blue-marlin/ |
| Bluefin tuna | Western Atlantic Labrador to northern Brazil, including Gulf; the species also occurs in the eastern Atlantic and Pacific. | Florida Museum: https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/bluefin-tuna/ |
| Cobia | Western Atlantic Nova Scotia to Argentina; U.S. waters most abundant Virginia south through Gulf; seasonal movement into South Florida in winter. | NOAA Fisheries: https://www.fisheries.noaa.gov/species/cobia |
| Florida pompano | Western Atlantic Massachusetts to Brazil. | Virginia Institute of Marine Science species page: https://www.vims.edu/research/departments/fisheries/programs/mrg_draft/speciesofinterest/species_gridpages/florida-pompano.php |
| Gag grouper | Western Atlantic primarily North Carolina to Yucatan Peninsula, including Gulf. | NOAA Fisheries: https://www.fisheries.noaa.gov/species/gag-grouper/overview |
| Gray triggerfish | Western Atlantic Nova Scotia to Argentina, including Bermuda and Gulf. | NOAA Fisheries: https://www.fisheries.noaa.gov/species/gray-triggerfish |
| Jack crevalle | Western Atlantic Nova Scotia to Uruguay; also throughout Gulf. | Florida Museum: https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/crevalle-jack/ |
| King mackerel | Western Atlantic Massachusetts to Rio de Janeiro, including Gulf and Caribbean. | NOAA/Florida Museum report two stocks that mix in South Florida; stock boundary and season matter. https://www.fisheries.noaa.gov/species/king-mackerel/seafood and https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/king-mackerel/ |
| Mahi-mahi | Atlantic, Gulf, and Caribbean; NOAA reports U.S. catch from Massachusetts to Texas. | This is the U.S. fishery range, not the species' full tropical/subtropical global range. https://www.fisheries.noaa.gov/species/atlantic-mahi-mahi |
| Mangrove snapper | FishBase gives 42°N–9°N and 98°W–59°W; Brazilian records are flagged as possible misidentifications. | Do not extend to Brazil on older broad range claims without taxonomic/record validation. https://www.fishbase.org/summary/Lutjanus-griseus |
| Mutton snapper | Western Atlantic Massachusetts to Brazil; Gulf included; most common in tropical Florida, Bahamas and Caribbean. | Florida Museum: https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/mutton-snapper/ |
| Red drum | Atlantic historic range Massachusetts through Florida; Gulf range Florida to northern Mexico. | Atlantic and Gulf stocks are managed separately; recent Atlantic distribution/catch differs from historic range. https://asmfc.org/species/red-drum/ and https://gulfcouncil.org/species/drum-red/ |
| Red grouper | Western Atlantic Massachusetts through Gulf and south to Brazil. | NOAA Fisheries: https://www.fisheries.noaa.gov/species/red-grouper |
| Red snapper | Western Atlantic New England to Yucatan Peninsula, throughout Gulf. | NOAA NCEI atlas: https://www.ncei.noaa.gov/waf/data-atlas-waf/products/originalAtlas/lmrPlates/RedSnapper-3_36.pdf |
| Sailfish | Western Atlantic approximately 40°N to 40°S; highest abundance in Gulf, Atlantic Florida, and Caribbean. | Florida Museum: https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/sailfish/ |
| Scamp grouper | Continental shelf from Campeche Banks to Florida and north along East Coast to North Carolina. | South Atlantic Fishery Management Council: https://safmc.net/species/grouper-scamp/ |
| Sheepshead | Western Atlantic Nova Scotia through Gulf, with records south to Brazil; densest populations off southwest Florida. | Florida Museum reports absences in Bahamas, West Indies, Grenada and Bermuda, so a simple continuous envelope overstates occurrence. https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/sheepshead/ |
| Snowy grouper | Western Atlantic Massachusetts to Brazil, including Gulf, Lesser Antilles and northern Cuba. | South Atlantic Fishery Management Council: https://safmc.net/species/grouper-snowy/ |
| Southern flounder | Atlantic range Albemarle Sound to Loxahatchee River; absent south of Loxahatchee and around Florida peninsula tip, but occurs in Caloosahatchee River Estuary; Gulf range extends to northern Mexico. | Disjoint Florida distribution; keep regional mask/profile-split decision open. https://www.dnr.sc.gov/marine/species/assets/SpeciesProfileSouthernGulfSummerFlounder.pdf |
| Wahoo | Western Atlantic from about 35°N to 38°S; Gulf included; abundance is seasonal in the Carolinas and Bermuda. | Florida Museum: https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/wahoo/ |

### What this source pass does and does not establish

- It establishes that all 25 missing-latitude profiles have traceable distribution references to guide a formal geographic review.
- It does **not** establish that a single min/max latitude rectangle is the correct model mask for every species.
- Stock boundaries, seasonal migration, discontinuous Florida distribution, island absences, and life-stage differences must be preserved.
- Do not automatically convert city/country endpoints into arbitrary decimal degrees. If the source provides coordinates or a mapped polygon, use that. Otherwise keep the evidence as a documented range statement and decide whether a coarse box is defensible.
- The strongest regional-scope flags from this pass are black sea bass (separate Mid-Atlantic/South Atlantic stocks), king mackerel (Atlantic/Gulf stock mixing in South Florida), cobia (seasonal migration), sheepshead (documented regional absences), and southern flounder (discontinuous Florida distribution).


## Phase 1.1: physical measurement alignment audit

### Runtime variables

| Runtime parameter | Actual measurement | Current source / limitation |
|---|---|---|
| `sst_c` | Sea-surface temperature | NOAA CoastWatch MUR `jplMURSST41`, variable `analysed_sst`. This is not bottom temperature. |
| `depth_m` | Seafloor bathymetric depth | NOAA NCEI ETOPO 2022 `z`, sign converted to positive water depth. Source is 15-arc-second but sampled at stride 15 (about 3.75 arc-minutes); config explicitly says broad regional context, not reef-scale bathymetry. |
| Fish tag depth | Vertical position of an animal in the water column | Not a current runtime grid layer and not interchangeable with `depth_m`. |
| Bottom-water temperature | Temperature near the seabed | Not currently supplied by the configured MUR SST layer. Must not be silently substituted with surface temperature. |

### 1.1.a Demersal temperature mismatch: confirmed active SST factors

The following five active SST factors are already marked `needs_source` after the source-by-source review because their cited evidence is bottom-water temperature or demersal context, not a validated surface-temperature response:

| Profile | Active SST range / ideal | Evidence mismatch |
|---|---|---|
| Pacific halibut | 5–13 °C / 7–11 °C | IPHC bottom-water occupancy around 3–8 °C; no direct support for the configured satellite-SST curve. |
| Petrale sole | 7–15 °C / 9–13 °C | DFO bottom-temperature tolerance; no species-specific preferred SST interval. |
| Pacific cod | 4–12 °C / 6–10 °C | NOAA Bering Sea trawl bottom temperatures, not surface temperature or a preference curve. |
| Sablefish | 4–12 °C / 6–10 °C | NOAA tag temperatures measured at fish depth (typically 3.9–5.0 °C); not satellite SST. |
| Rock greenling | 6–14 °C / 8–12 °C | Bering Sea near-bottom observations (0.5–3.8 °C), not SST. |

The existing ranges are retained unchanged. These profiles are not ready for SST recalibration until a surface-temperature relationship is directly supported or an appropriate bottom-temperature input is evaluated.

### 1.1.b Pelagic fish depth versus seafloor bathymetry

The evidence review identifies a second mismatch. Tagging studies report fish vertical depth, while the runtime factor scores ETOPO seafloor depth.

| Profile | Active `depth_m` weight | Gate? | Current evidence interpretation |
|---|---:|:---:|---|
| Bluefin tuna | 0.15 | Yes | NOAA/archival tags report dives to 500–1,000 m; these are fish depths, not seabed depths. |
| Blue marlin | 0.05 | Yes | Tags report upper-water-column occupancy and occasional deep dives; not bathymetric preference. |
| Mahi-mahi | 0.05 | Yes | Fish occupy surface water and dive in the water column; factor is classified `weak_factor`, a bathymetric proxy only. |
| Opah (`Lampris incognitus`) | 0.50 | Yes | Pre-revision Hawaii tags report fish vertical occupancy; NOAA California catch analysis provides a separate bathymetric association, but species attribution and numeric response remain limited. |
| Steelhead | 0.50 | Yes | Tags show mostly upper-5-m fish depth; factor is classified `weak_factor`, and does not establish seabed preference. |

This is not an exhaustive list. Other pelagic tunas, billfish, sharks and salmonids with active `depth_m` factors need the same check. All five listed pelagic `depth_m` factors are active gates. This is a high-priority eligibility risk: each can exclude a cell regardless of its small contribution to the weighted average. The weak-factor status does not neutralize gate behavior.

### 1.1.c Design decisions to evaluate (not yet implemented)

1. **Surface SST:** retain as a surface environmental variable and only use evidence that measures surface temperature or demonstrates a validated relationship between surface and target-habitat temperature.
2. **Bottom temperature:** investigate a gridded, depth-resolved source with documented temporal coverage, depth levels, resolution, regional coverage, and operational freshness. Do not enable a source until these are validated.
3. **Bathymetry:** retain `depth_m` only when evidence describes seabed depth, demersal habitat occupancy, or a demonstrated catch-location relationship with bathymetry. Do not use fish vertical-depth observations as direct evidence for this factor.
4. **Fish vertical depth:** if the product needs this dimension, design it as a separate parameter with a suitable data source and semantics; do not overload `depth_m`.
5. **Resolution:** ETOPO's current stride is suitable only as broad shelf/slope context. Reef-scale or shallow-flat predictions need higher-resolution regional bathymetry and independent validation.

No source selection, new data layer, factor activation, gate, weight, numeric band, scoring equation or confidence behavior is approved by this audit.

### Validation checkpoint

Taxonomy and scope metadata commit `b77bd890cc687b0405d3ecbb3edabdde052d337e` passed CI run [#44134514836](https://github.com/markeetox/LUPITA/actions/runs/44134514836): 307 tests passed, 0 failed, 115 warnings. The generated species audit reports 130 profiles parsed and structurally valid, 0 JSON parse errors, and 0 model-compatibility issues. No prediction behavior changed.
