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



## NOAA DisMAP survey coverage and data-access review | 2026-11-27

### Species coverage confirmed

The June 2026 DisMAP technical report's Appendix I lists Southern flounder (Paralichthys lethostigma) for the Gulf of Mexico survey and all three Southeast U.S. Shelf seasonal survey products (Fall, Spring, Summer). The survey inventory table documents the following retained coverage and filtering:

- **Gulf of Mexico, Summer:** survey series 1982–2025; the DisMAP analysis retains years from 2010 onward, drops 2022, and retains strata sampled in 13 of the years from 2010–2025.
- **Southeast U.S. Shelf, Fall:** 1989–2025; retained strata sampled in more than 33 years.
- **Southeast U.S. Shelf, Spring:** 1989–2025; drops 1989 because of inconsistent sampling protocol and retains strata sampled in at least 30 years.
- **Southeast U.S. Shelf, Summer:** 1989–2025; drops 2021 because it was poorly sampled.

The report states that taxa are included in the Species Persistence module when caught in at least 5% of tows per year in at least two survey years, and in the Single Species Shift module when caught in at least 5% of tows in at least three quarters of survey years. The survey data are expanded with zeroes for tows where a regionally recorded species was not caught. These are survey/module inclusion rules, not proof of absence outside survey coverage. The Gulf survey inventory links to SEAMAP; the Southeast shelf source is identified as direct data from the survey steward.

Sources:
- NOAA Fisheries DisMAP Technical Report, June 2026: https://apps-st.fisheries.noaa.gov/dismap/docs/DisMAP_Tech_Report_06_2026.pdf
- NOAA DisMAP portal: https://apps-st.fisheries.noaa.gov/dismap/DisMAP.html

### Public point-level survey layers identified

NOAA InPort's current Survey Catch-per-unit-effort dataset (record 69743) explicitly describes point-level survey observations: locations where species were caught and standardized biomass weight catch-per-unit-effort (kg/ha). It links to current ArcGIS Feature Services for Gulf of Mexico and Southeast US Fall, Spring, and Summer sample locations. Dataset metadata lists CC0-1.0 for these data.

The published point-layer schema includes:
- survey identity/context: DatasetCode, Region, Season, DistributionProjectName, SummaryProduct, SampleID, Year, StdTime;
- species/catch: Species, CommonName, SpeciesCommonName, CommonNameSpecies, WTCPUE, MapValue, TransformUnit, CoreSpecies;
- sampling/spatial context: Stratum, StratumArea, Latitude, Longitude, Depth; and point geometry.

Layer endpoints:
- Gulf of Mexico: https://services2.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/GMEX_Sample_Locations_CURRENT/FeatureServer
- Southeast Fall: https://services2.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/SEUS_FAL_Sample_Locations_CURRENT/FeatureServer
- Southeast Spring: https://services2.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/SEUS_SPR_Sample_Locations_CURRENT/FeatureServer
- Southeast Summer: https://services2.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/SEUS_SUM_Sample_Locations_CURRENT/FeatureServer
- Dataset metadata: https://www.fisheries.noaa.gov/inport/item/69743

Important distinction: the separate DisMAP Indicators service is a summary table (species/region/season/year and distribution metrics), not the underlying tow-level point layer. The Survey Catch-per-unit-effort service is the correct point-level target.

### Limitations and retrieval status

The ArcGIS layer metadata and field schemas were inspected, but the ArcGIS REST query endpoints could not be retrieved through the current web session. No point records, species-specific counts, or map were downloaded or calculated in this pass. The Florida Museum archive is still not acquired; its current IPT page reports 241,689 occurrence records and a CC-BY-NC 4.0 license, but that collection remains a voucher-occurrence source rather than a standardized survey.

DisMAP's interpolated biomass surface uses inverse-distance weighting with a 200 km search radius and 10–15 nearby sampling locations, with a five-year temporal window and 2 km grid cells for bottom-trawl data. This is useful for broad survey-informed context but fills unsampled spaces by interpolation; it must not be converted directly into a species occupancy mask. NOAA's portal also flags the Species Persistence module as a pilot with preliminary results not yet intended for analysis.

### Revised next research step

1. Query the four current ArcGIS point layers for the Southern flounder Species value resolved against the current Species Filter table and obtain all matching survey observations, using pagination/record limits and preserving original fields.
2. Separately retrieve the all-species tow/sample footprint or survey effort records for the same seasons/years so zero catch can be interpreted only where a valid tow occurred.
3. Audit species counts by region, season, year, stratum, coordinates, depth, WTCPUE, and sample ID. Check duplicates, null coordinates, and any taxonomic code mapping in the current Species Filter table.
4. Compare actual survey points with Florida Museum voucher records and the published Florida range summaries. Report sampled locations and non-detections separately; do not convert sparse records or unbalanced sampling into hard exclusion boundaries.
5. Only after the evidence review, assess whether candidate estuary/coastal polygons are justified and calculate the before/after eligible-cell impact.

No raw occurrence/survey records were downloaded or committed. No profile, mask, scoring, confidence, ingestion, or production behavior changed.


## Read-only NOAA extraction workflow implemented | 2026-11-27

Added `scripts/extract_noaa_southern_flounder.py`, `.github/workflows/noaa-southern-flounder-extraction.yml`, and `tests/test_noaa_dismap_extractor.py`.

The extractor reads the canonical common/scientific name from `data/species/southern-flounder.json`, inspects the distinct values in NOAA's `Species`, `CommonName`, `SpeciesCommonName`, and `CommonNameSpecies` fields, and matches the full target name. The generic alias "flounder" is deliberately not used as a match, to avoid pulling in unrelated species. The repository did not expose a separate species-filter table in the reviewed tree; the existing species profile is the canonical target-name source.

For each of the four current Gulf/Southeast seasonal layers, the script writes:
- target-species observation CSV;
- same-`SampleID` context CSV;
- extraction report with matched NOAA name combinations, year/season/stratum counts, coordinates/depth/WTCPUE null counts, and basic WTCPUE summaries.

Same-`SampleID` context is explicitly not represented as complete tow effort or verified non-detection coverage. The script does not infer absences, generate occupancy polygons, or create masks. Output is temporary and intended for a 14-day Actions artifact, not committed raw data.

Workflow is manual-dispatch only: https://github.com/markeetox/LUPITA/actions/workflows/noaa-southern-flounder-extraction.yml

Commits: extractor `d48a6d6d13f041f1bd6b2a7245943790c0f4808b`; matching/pagination hardening `5932d4cad7a31b9be562ead6ab0e2b37a91db532`; workflow `2190ff34d86e9f5869a45af72650c5bd48ad1f0a`; CI inclusion `d0a3b7100211e012b22e662e1321affc9fad3df0`.

The Python CI workflow was triggered by the commits and was still running at documentation time (runs `46018349544` and `46018358533`). The extraction workflow has not yet been manually dispatched, so no NOAA target records have been downloaded. No production code, species profile, scoring, confidence, mask, ingestion, or published data changed.


### Implementation follow-up | 2026-11-27

Matching was hardened after the first CI run exposed that the profile's one-word alias `flounder` would admit false positives. Generic one-word aliases are now excluded; a combined common-name plus taxon string is accepted when it begins with the full target common name. Distinct-query pagination now uses the returned name fields rather than assuming an ObjectID exists in a distinct-value result. If no target rows match, the extractor preserves and uploads its diagnostic JSON rather than failing before artifact upload.

The earlier corrected CI run `46018358533` completed the test suite with **335 passed, 0 failed** and completed the species audit/artifact steps successfully. A later run including the added compound-name regression test and the current script hardening was still in progress at the time of this note. The first run on the pre-fix code failed the generic-alias regression test as expected; that issue was corrected in subsequent commits. Latest extractor hardening commit: `848ad0fbcbd375742da8dbcad7637bfaa72226c2`.
