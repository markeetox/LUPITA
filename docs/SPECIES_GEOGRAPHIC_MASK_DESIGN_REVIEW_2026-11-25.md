# Species-specific geographic eligibility: evidence and geometry design review

**Date:** 2026-11-25  
**Status:** research/design only; no implementation or profile changes approved  
**Scope:** Southern flounder (*Paralichthys lethostigma*) and white sturgeon (*Acipenser transmontanus*)

## Why this review exists

The current grid scorer supports a global marine mask plus optional rectangular latitude/longitude limits. It does not support species-specific coastal polygons, estuary boundaries, disconnected range regions, or habitat-specific eligibility masks. The existing Southern flounder profile has only a broad longitude range and no latitude range. The white sturgeon profile is included in a marine-grid model even though its dominant habitat is riverine and estuarine.

This review evaluates whether the available sources support immediate geometry construction. They do not yet support a production mask.

## Southern flounder: source comparison

### Sources that support a discontinuous Florida range

1. **South Carolina Department of Natural Resources, Southern Flounder species profile.** Its geographic-range summary places the Atlantic range from Albemarle Sound to the Loxahatchee River, reports absence south of Loxahatchee and around the Florida peninsula tip, then reports occurrence in the Caloosahatchee River Estuary and westward around the Gulf to northern Mexico. It also notes occurrence in low-salinity and freshwater habitats.  
   Source: https://www.dnr.sc.gov/marine/species/assets/SpeciesProfileSouthernGulfSummerFlounder.pdf

2. **USGS Nonindigenous Aquatic Species profile.** Its native-range summary similarly describes Atlantic coastal/estuarine waters from Albemarle Sound to Jupiter Inlet, Florida, and a separate range from the Caloosahatchee Estuary to northern Mexico; it says South Florida is not included in the intervening gap. This is a useful independent summary, but the page is a range synopsis, not a geospatial boundary product.  
   Source: https://nas.er.usgs.gov/queries/FactSheet.aspx?speciesID=803

3. **Seafood Watch 2023 assessment.** The report concerns Texas Gulf-caught southern flounder and repeats the southern Florida gap between Loxahatchee and Caloosahatchee, citing Enge and Mulholland (1985). It is corroboration, but not an independent GIS boundary and not a Florida distribution survey.  
   Source: https://www.seafoodwatch.org/globalassets/sfw/pdf/expert-review/030623/seafood-watch-southern-flounder-us-27899.pdf

### Sources that add nuance or create a boundary caution

4. **Florida Fish and Wildlife Conservation Commission species profile.** FWC describes habitat as brackish bays and estuaries, tidal creeks, and sometimes freshwater. It does not provide a precise geographic range polygon.  
   Source: https://myfwc.com/wildlifehabitats/profiles/saltwater/flounder/southern-flounder/

5. **Florida Museum of Natural History.** Its summary lists Florida distribution in western and north-central drainages and the Atlantic Coast. This is broader than the simplified Loxahatchee/Caloosahatchee endpoint summary and should be reconciled with underlying collection records before a hard mask is drawn.  
   Source: https://www.floridamuseum.ufl.edu/discover-fish/florida-fishes-gallery/southern-flounder/

6. **North Carolina Southern Flounder Fishery Management Plan (2021).** It describes Atlantic coastal habitat from North Carolina to Cape Canaveral and Gulf distribution from northern Mexico to Tampa, and notes genetic evidence for little/no movement between Gulf and Atlantic populations because the Florida peninsula acts as an ecological barrier. This supports treating Atlantic and Gulf population contexts separately, but does not by itself define a South Florida raster mask.  
   Source: https://files.nc.gov/ncdeq/March-2021-Southern-Flounder-FMP.pdf

### Geometry conclusion

- A single rectangular latitude/longitude range is unsuitable.
- The documented gap should not be converted into a hard coastline cut using approximate city/river coordinates.
- A presence point is not proof of continuous occupancy; absence of records is not proof of absence.
- The Caloosahatchee estuary occurrence must not be erased by a blanket South Florida exclusion.
- A defensible mask likely needs separate Atlantic and Gulf coastal/estuarine regions, with the Caloosahatchee exception represented explicitly. However, the exact boundary source and treatment of offshore spawning habitat remain unresolved.
- Candidate occurrence sources (museum/USGS collection records or NOAA survey observations) must be examined with dates, coordinate uncertainty, life stage, and survey effort. Survey non-detection can only inform absence when sampling effort is documented.

### Recommended next research step

Obtain and inspect georeferenced occurrence/survey data and authoritative estuary/coastal geometry before defining any polygon. Compare Florida Museum collection records, USGS NAS point data, and available fishery-independent survey records. Keep records as observations with provenance; do not automatically turn a convex hull of points into an occupancy polygon.

## White sturgeon: marine-grid scope

1. **California Department of Fish and Wildlife.** White sturgeon occur in coastal waters from Ensenada to Alaska, but primarily reside in large rivers and associated estuaries, including Sacramento-San Joaquin, Fraser, and Columbia systems. Ocean excursions occur but are occasional.  
   Source: https://wildlife.ca.gov/Conservation/Fishes/Sturgeon/White-Sturgeon

2. **California Marine Species Portal enhanced status report.** It describes limited movements into marine waters, dominant freshwater/estuarine use, river spawning habitat, and estuarine/riverine dependence on flow, depth, substrate, and related conditions.  
   Source: https://marinespecies.wildlife.ca.gov/white-sturgeon/true/

3. **Washington Department of Fish and Wildlife.** It describes amphidromous movement and states most fish spend most of their time in freshwater, with some moving into coastal bays and estuaries.  
   Source: https://wdfw.wa.gov/species-habitats/species/acipenser-transmontanus

### Scope conclusion

The species' broad coastal range does not make an ocean-only SST/ETOPO model a suitable representation of its dominant habitat. The current runtime lacks river flow, channel hydraulics, estuary-specific habitat, and a freshwater/estuary grid. A simple lat/lon mask would not solve that mismatch.

### Recommended decision to evaluate

Treat white sturgeon as out of scope for the current marine-grid prediction product unless the product explicitly intends to model only occasional coastal excursions and can support that narrow claim. A separate river/estuary model would require its own data, spatial grid, and validation. No profile deactivation or catalog change is made in this review.

## Spatial-mask design requirements (future implementation)

Any future species-specific eligibility feature should:

- Be optional and backward-compatible; profiles without a mask must retain current behavior until explicitly migrated.
- Use versioned GeoJSON or another documented spatial format with explicit CRS (WGS84 longitude/latitude), provenance, source date, and review status.
- Support multiple disjoint polygons and holes; do not assume one continuous polygon.
- Distinguish coastal/estuarine occurrence regions from broad marine range and from seasonal offshore spawning habitat.
- Define point-in-polygon boundary behavior and handle polygon edges consistently.
- Apply only to eligibility, not alter factor scores, weights, gates, confidence, or source data.
- Include synthetic unit tests for inside/outside, disjoint regions, holes, boundaries, invalid geometry, and backward compatibility.
- Include a profile-level audit showing how many grid cells become eligible before and after a proposed mask. No production mask should be enabled without reviewing that impact.
- Avoid treating survey non-detections as absences without documented sampling effort.

## Change-control record

No species JSON, geographic bounds, scorer code, data source, model activation state, score, weight, gate, confidence behavior, ingestion, or publication behavior changed as part of this review.

## Research references

- SCDNR Southern Flounder geographic range: https://www.dnr.sc.gov/marine/species/assets/SpeciesProfileSouthernGulfSummerFlounder.pdf
- USGS NAS Southern Flounder profile: https://nas.er.usgs.gov/queries/FactSheet.aspx?speciesID=803
- Seafood Watch 2023 Southern Flounder assessment: https://www.seafoodwatch.org/globalassets/sfw/pdf/expert-review/030623/seafood-watch-southern-flounder-us-27899.pdf
- FWC Southern Flounder profile: https://myfwc.com/wildlifehabitats/profiles/saltwater/flounder/southern-flounder/
- Florida Museum Southern Flounder profile: https://www.floridamuseum.ufl.edu/discover-fish/florida-fishes-gallery/southern-flounder/
- NC Southern Flounder Fishery Management Plan (2021): https://files.nc.gov/ncdeq/March-2021-Southern-Flounder-FMP.pdf
- CDFW White Sturgeon: https://wildlife.ca.gov/Conservation/Fishes/Sturgeon/White-Sturgeon
- CA Marine Species Portal White Sturgeon report: https://marinespecies.wildlife.ca.gov/white-sturgeon/true/
- WDFW White Sturgeon: https://wdfw.wa.gov/species-habitats/species/acipenser-transmontanus
- Runtime geographic contract: `pipeline/scoring.py::score_species` and `config/sources.json`

## Occurrence-data acquisition review

A follow-up source-discovery pass identified these practical routes:

- **Florida Museum of Natural History Ichthyology IPT / Darwin Core Archive.** The museum publishes a downloadable occurrence archive under CC-BY-NC 4.0. The resource contains georeferenced fish collection records and is updated frequently. It is a strong candidate for inspecting Florida-vouchered *P. lethostigma* specimens, provided each record is filtered by accepted scientific name/synonyms and reviewed for coordinate uncertainty, event date, basis of record, identification verification, and duplicate lots. It is a museum collection, not a standardized survey; collection density must not be interpreted as abundance or absence. Dataset: https://ipt.floridamuseum.ufl.edu/ipt/resource?r=ichthyology ; archive: https://ipt.floridamuseum.ufl.edu/ipt/archive.do?r=ichthyology ; GBIF dataset DOI: https://doi.org/10.15468/8mjsel
- **USGS NAS API.** The API documentation says its machine-readable occurrence API serves spatially referenced observations in the Nonindigenous Aquatic Species database. Although the NAS fact sheet provides a useful native-range summary for southern flounder, the NAS occurrence API is not a suitable primary source for native Florida distribution because its occurrence collection is designed around nonindigenous records. Do not treat the lack of NAS Florida occurrence records as evidence of absence. API documentation: https://nas.er.usgs.gov/api/documentation.aspx
- **NOAA Fisheries DisMAP.** This is a useful candidate for fishery-independent survey context and temporal distribution shifts. It exposes survey-informed distribution analyses, range limits, biomass interpolation, and links to regional survey datasets/metadata. Before use, confirm that southern flounder is represented in the relevant Atlantic/Gulf survey domain and inspect the underlying survey effort and model metadata. Its interpolated biomass surface is not automatically an occupancy polygon. Portal: https://apps-st.fisheries.noaa.gov/dismap/DisMAP.html

### Acquisition priority

1. Inspect the Florida Museum archive for verified *P. lethostigma* records in Florida and adjacent states. Preserve the raw Darwin Core fields and archive version/DOI; do not publish raw records in the repository.
2. Check NOAA DisMAP and underlying survey metadata for southern flounder coverage, years, gear, sampling footprint, and non-detection/effort treatment.
3. Compare museum records and survey evidence by region (Atlantic Florida, Caloosahatchee, other Gulf Florida, Florida Keys/Florida Bay). Explicitly report sample counts and temporal coverage, but do not convert sparse records or unbalanced sampling into hard exclusion boundaries.
4. Only then evaluate candidate estuary/coastal polygons and the effect on LUPITA's eligible grid cells.

