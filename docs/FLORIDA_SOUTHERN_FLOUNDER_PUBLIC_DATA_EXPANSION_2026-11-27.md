# Southern Flounder Public Data Expansion: Florida Bay and Statewide FIM

**Review date:** 2026-11-27  
**Taxon:** Southern flounder (*Paralichthys lethostigma*)  
**Scope:** Public Florida Bay monitoring, FWC/FWRI fisheries-independent monitoring, Everglades National Park recreational catch data, and Florida Museum occurrence archives.  
**Change type:** Research and documentation only. No profile, range mask, scoring, confidence, ingestion, or production behavior changed.

## Executive finding

A newly located NOAA report provides independent positive Florida Bay evidence. Kelble et al. (2021), *Juvenile Sportfish Monitoring in Florida Bay, Everglades National Park: Monitoring and Assessment Plan Results from 2004–2019* (NOAA Technical Report OAR-AOML-48), includes Southern flounder in Table 5. The table reports **n = 12 site samples**, observed salinity range **33.3–40.4 ppt**, and mean **36.7 ± 2.31 ppt**. The table heading defines n as site sample size. This is not a count of 12 individual fish. The published table does not provide the 12 sample dates, coordinates, individual fish lengths, or year-by-year detections.

The report says the project began enumerating other sportfish in 2009, while a smaller subset had been enumerated since the program began in 2004. All sizes of other sportfish caught in each tow were identified, measured, and counted. Routine sampling was monthly from May through October, or November when conditions warranted, with some additional off-season sampling after Hurricane Irma. The 12 site-sample records are a useful independent detection signal, but exact sampling events and size distribution remain unresolved.

This source reinforces that Southern flounder cannot be treated as categorically absent from Florida Bay. It does not establish a large, stable, self-sustaining, or currently abundant population.

## 1. NOAA Florida Bay juvenile sportfish monitoring, 2004–2019

**Primary source:** Kelble, C., J. Browder, C. Quenée-Stewart, I. Smith, K. Montenero, L. Visser, and J. Contillo. 2021. *Juvenile Sportfish Monitoring in Florida Bay, Everglades National Park: Monitoring and Assessment Plan Results from 2004–2019*. NOAA Technical Report OAR-AOML-48. DOI: https://doi.org/10.25923/sec9-mf34.

### Directly reported evidence

Table 5, titled “Salinity ranges and means with 95% confidence intervals and site sample size (n) for the 25 species that have been enumerated since the project’s inception in 2004,” reports:

| Field | Southern flounder result |
|---|---:|
| Scientific name | *Paralichthys lethostigma* |
| Common name | Southern Flounder |
| Salinity range at sampled sites | 33.3–40.4 ppt |
| Mean salinity ± standard deviation | 36.7 ± 2.31 ppt |
| Site sample size (n) | 12 |

The Methods section states that, beginning in 2009, the project expanded collection of information on other sportfish. A smaller subset of species had been enumerated since the project began in 2004. All sizes of other sportfish caught in each tow were identified, measured, and counted. Routine juvenile spotted seatrout sampling was monthly from May through October, or through November when October conditions indicated November sampling would be productive. Additional winter sampling was conducted in 2017 after Hurricane Irma.

### Interpretation limits

- The table's n is explicitly a **site sample size**, not a number of individual Southern flounder.
- The table pools the study period and does not show the 12 positive sample dates, coordinates, zones, or annual distribution.
- The monitoring design primarily targeted juvenile spotted seatrout. Southern flounder were part of the other-sportfish observations; the report does not establish that the gear or seasonal design was optimized for Southern flounder.
- The reported salinity statistics describe sites where the species was observed. They are not a species salinity preference curve or validated suitability interval.
- The report does not supply a complete zero-catch denominator for Southern flounder in the published table.
- Do not translate the 12 site samples into a population estimate, occupancy polygon, abundance index, or year-round habitat boundary.

### Immediate follow-up

Locate raw data or a data supplement for NOAA repository record 28764. Determine whether sample-level records include Southern flounder event dates, coordinates, zone, tow identifier, fish counts, lengths, and environmental measurements. If unavailable, the report remains a reliable aggregate occurrence source but cannot support a spatially explicit layer.

## 2. NOAA Florida Bay resident-fish compendium, 1984–2001

Powell et al. (2007), NOAA Professional Paper NMFS 6, documents Florida Bay sampling with basin otter trawls in 1984–1985 and 1994–2001, plus surface trawls in 1984–1985. The publication presents accounts for 46 more abundant juvenile and small resident species.

A full-text search found no match for “Paralichthys” or “flounder,” and Southern flounder is not among the species accounts in its contents. This is **not** a verified non-detection: the report is scoped to selected more-abundant juvenile/small resident species, and lack of a species account does not show absence from all underlying tows.

The report does provide historical Florida Bay sampling-design context. It documents changes to the sampling design in 1999 and cautions against unqualified comparisons between the earlier and later periods. Any raw-data reconstruction must preserve gear, habitat, period, and design differences.

## 3. FWC/FWRI statewide Inshore FIM SRS public GIS layer

The live FWC ArcGIS service exposes a point feature layer named **Inshore Saltwater FIM Stratified-Random Sampling**. Its service schema includes:

- Reference: unique alphanumeric identifier for each FIM gear deployment.
- Sampling_Date.
- Latitude and Longitude.
- Gear.
- Scientificname and Commonname.
- TotalNum.
- avg_size, min_size, and max_size.

The service metadata describes the FIM stratified-random design: sampling sites are selected monthly from geographic and habitat strata, including depth, seagrass, and shore type. The live service advertises query capability and JSON/GeoJSON formats.

The associated FGDC metadata reports 1,765,226 point features. It states that the public GIS export was restricted to records with CNT > 0, meaning the export contains positive-catch species records and cannot reconstruct all zero-catch deployments or the full sampling denominator. The metadata's stated content range ends 2016-12-27, but a later process step dated 2025-04-11 says the export was updated from 1996 through the most recent available records. This internal date-range inconsistency must be resolved against actual returned records before temporal coverage is claimed.

The GIS service schema and metadata were inspected, but species-specific feature queries and a full data export were not successfully retrieved in this review. **No FWC Southern flounder record count or point list is claimed here.**

### Extraction requirements

1. Query exact scientific name Paralichthys lethostigma; do not use generic “flounder.”
2. Preserve gear-deployment Reference, date, coordinates, gear, total number, and size fields.
3. Verify date coverage from returned records, not just the legacy metadata range.
4. Separate gear types and estuaries/regions.
5. Treat only positive catches as occurrence evidence. Missing species records in this export are not zero catches.
6. Crosswalk positive records to original deployment/sample records if a full denominator or no-catch interpretation is needed.

## 4. Everglades National Park recreational catch and effort dataset, 1980–2025

The National Park Service published a public data package on 2026-06-24 covering January 1980 through April 2025. The package reports more than 270,000 angler-intercept surveys and over four million individual fish reported. The survey interviews a subset of anglers returning from marine and estuarine fishing trips at boat ramps within or near Everglades National Park. It includes catch, fishing effort, fishing-area geography, boat-trailer counts, and QA/QC flags.

The Data.gov package lists five downloadable resources:
- EVER_creel_rec_catch.csv
- EVER_creel_rec_catch_flags.csv
- EVER_creel_fishing_areas.csv
- EVER_creel_rec_trailer_count.csv
- EVER_creel_rec_metadata.xml

The dataset is public domain (CC0). The files were identified and package metadata reviewed, but the CSV download endpoint returned an unsupported content type in this research session and the files were not successfully ingested. **No Southern flounder recreational catch count or absence claim is made.**

When acquired, analyze species identity, catch disposition, fishing area, date, number of anglers, trip duration/effort, and QA/QC flags. This is fisheries-dependent evidence and must remain separate from standardized FIM or NOAA survey evidence. Angler target, access, gear, effort, and reporting affect detection.

## 5. Florida Museum Ichthyology occurrence archive

The Florida Museum's UF FLMNH Ichthyology IPT resource publishes a Darwin Core Archive and metadata, is updated daily, and carries a CC-BY-NC 4.0 license. The archive is a reproducible public source for expanding the voucher review beyond the currently reviewed catalog records.

The current resource page and archive endpoint were verified, but the archive was not downloaded and reprocessed in this review. The earlier catalog-level findings for UF 164232, UF 142820, and UF 233907 remain as previously documented. A resource-wide record count is not a substitute for verifying target taxon records and catalog-level metadata.

When acquired, query accepted and verbatim scientific names, synonyms, catalog numbers, event dates, locality, decimal coordinates, georeference uncertainty, basis of record, identification history, collector, and multimedia references. Retain source record identifiers and do not interpret collection density as survey abundance.

## 6. Evidence synthesis

| Evidence stream | New result | Evidence class | Current limitation |
|---|---|---|---|
| NOAA Florida Bay juvenile sportfish monitoring, 2004–2019 | Southern flounder reported at n=12 site samples; salinity range 33.3–40.4 ppt | Standardized survey detections | No individual dates/coordinates or year-by-year distribution in published table |
| NOAA Florida Bay compendium, 1984–2001 | No Southern flounder species account found | Literature/survey-program context | Selected 46-species compendium; no species account is not a zero-catch result |
| FWC statewide Inshore FIM SRS GIS | Live positive-catch point layer and fields verified; 1,765,226 features in metadata | Standardized survey positive catches | Export restricted to CNT>0; target records not yet queried; temporal metadata conflict |
| NPS Everglades creel, 1980–2025 | Public downloadable package verified | Fisheries-dependent catch/effort | Raw files not yet ingested; no target species result |
| Florida Museum UF Ichthyology | Current public Darwin Core Archive endpoint verified | Museum voucher occurrences | Current archive not downloaded; previous priority records still need full metadata |

## Current scientific conclusion

The 2021 NOAA Florida Bay monitoring report supplies independent positive evidence that Southern flounder was detected in the Florida Bay monitoring program during 2004–2019. This strengthens earlier museum and historical literature evidence against an absolute South Florida absence claim. The reported n=12 is a count of site samples, not fish. The report does not establish broad or current abundance, and its published summary lacks event-level locations.

The NOAA 2007 compendium's omission of Southern flounder is not evidence of absence. The FWC GIS layer is promising for positive catches but cannot provide no-catch denominators because the published export is filtered to positive catch. The NPS creel dataset may add a useful independent fisheries-dependent occurrence stream after raw-file ingestion. The museum archive remains a reproducible route to additional historical specimens.

**No species mask, range boundary, scoring factor, confidence level, profile, ingestion behavior, or production source has been changed.** All findings remain research evidence pending raw data and event-level verification.

## Sources

- Kelble, C. et al. 2021. [Juvenile Sportfish Monitoring in Florida Bay, Everglades National Park: Monitoring and Assessment Plan Results from 2004–2019](https://repository.library.noaa.gov/view/noaa/28764/noaa_28764_DS1.pdf). NOAA Technical Report OAR-AOML-48. DOI: https://doi.org/10.25923/sec9-mf34. Especially Methods, pp. 2–3, and Table 5, p. 20.
- Powell, A.B., G. Thayer, M. Lacroix, and R. Cheshire. 2007. [Juvenile and Small Resident Fishes of Florida Bay](https://library.oarcloud.noaa.gov/noaa_documents.lib/NMFS/PP_NMFS/PP_NMFS_6.pdf). NOAA Professional Paper NMFS 6.
- FWC/FWRI. [Inshore Saltwater FIM Stratified-Random Sampling ArcGIS service](https://gis.myfwc.com/hosting/rest/services/Open_Data/Inshore_Saltwater_FIM_Stratified_Random_Sampling/MapServer).
- FWC/FWRI. [FGDC metadata for Florida's Inshore Saltwater FIM SRS records](https://www.arcgis.com/sharing/rest/content/items/68fb6774b58a40a08a6f87959aaa53c4/info/metadata/metadata.xml?format=default&output=html).
- National Park Service. 2026. [Recreational fishing catch and effort in Everglades National Park, 1980–2025, data package](https://catalog.data.gov/dataset/recreational-fishing-catch-and-effort-in-everglades-national-park-1980-2025-data-package). DOI: https://doi.org/10.57830/2318429.
- Florida Museum of Natural History. [UF FLMNH Ichthyology IPT resource and Darwin Core Archive](https://ipt.floridamuseum.ufl.edu/ipt/resource.do?r=ichthyology).
- Florida Museum of Natural History. [Darwin Core Archive download endpoint](https://ipt.floridamuseum.ufl.edu/ipt/archive.do?r=ichthyology).


## Reproducible acquisition workflow added

Added a manual-only, read-only GitHub Actions workflow:
- Workflow: [South Florida Public Evidence Acquisition](../actions/workflows/south-florida-public-evidence-acquisition.yml)
- Script: [scripts/acquire_south_florida_public_evidence.py](../blob/main/scripts/acquire_south_florida_public_evidence.py)

The workflow is designed to download the NPS creel package, query exact-name positive-catch records from the FWC/FWRI ArcGIS layer, and download/filter the Florida Museum Darwin Core Archive. It writes raw source files, exact-name candidate extracts, metadata, and a summary to a 14-day Actions artifact. It does not commit raw source data or modify LUPITA's model or species profiles.

The workflow and script have been committed to main but **have not yet been run**. The first run must be inspected for source failures, returned date coverage, target record counts, field names, taxonomy, QA flags, and spatial plausibility before any result is treated as validated.


## First acquisition run audited | 2026-11-28

The manual workflow completed successfully on `main`:
- Run: [46154737377](https://github.com/markeetox/LUPITA/actions/runs/46154737377)
- Source commit: `ab405884935af33b53434725af7d779d8ed9c06b`
- Artifact: `south-florida-public-evidence`, ID `15266424962`, 27,709,716 bytes; expires 2026-12-12.
- All workflow steps, including script syntax check, acquisition, and artifact upload, succeeded. The artifact summary reports no source failures.

### FWC/FWRI Inshore FIM SRS positive-catch extract

- Exact-name query returned and retrieved all 6,008 matching feature records (the service query's expected count and retrieved count agree).
- Dates: 1996-04-15 through 2023-12-21.
- Coordinates: 26.843167–30.745200°N, 87.048500–80.042667°W.
- 10,482 fish represented by the `TotalNum` field across 6,008 positive-catch records.
- Only one record is south of 27°N (26.843167°N, 1997-07-09, Reference `TQM1997070901`); none is south of 26.5°N. There are 251 records south of 28°N.
- Gear codes returned: 20 (151 records), 23 (1,365), 160 (1,562), 300 (2,723), 301 (207). Gear-code interpretation still requires the FWC codebook.
- Crucial limitation: the public layer is filtered to positive-catch species records (`CNT > 0`). It contains no zero-catch denominator. The absence of Southern flounder rows south of the southernmost positive record cannot be called a survey non-detection or biological absence. It does establish that this public target extract has virtually no positive records in the lower South Florida latitude band; survey frame/coverage and source export limitations must be resolved before interpretation.

### NPS Everglades recreational creel catch extract

- Full catch file parsed: 828,222 rows; source package covers 1980-01 through 2025-04.
- Exact-name candidate extract: 210 catch rows, 205 unique interview keys, 271 fish summed from `individualCount`.
- All candidates are from Flamingo (209 rows) except one Everglades City row. Candidate dates run 1980-01-05 through 1997-03-16.
- Recorded disposition: 150 harvested rows and 60 released rows. Five interview keys have separate harvested/released rows; these must not be mistaken for duplicate interview events.
- The candidate flags extract has 538 rows across 179 of the 205 candidate interview keys. The most frequent flag descriptions concern trip-hours and party-composition / species-preference fields. These are interview-level QA flags, not proof that the species identification or catch count is invalid. Retain flags for review; do not automatically discard catches.
- This is fisheries-dependent angler-intercept information. Counts are reported catch among sampled returning anglers, not standardized abundance, and the lack of later target rows is not evidence of no catch after 1997.

### Florida Museum UF Ichthyology vouchers

- Current downloaded Darwin Core Archive contains 241,669 occurrence rows; 221 exact-name candidate occurrences were extracted.
- 170 candidates have stateProvince = Florida; other records are from additional Gulf/Southeastern states and must remain outside Florida-only summaries.
- Florida occurrence years with a usable year field: 1929–2024 (169 records with year values).
- Ten Florida records have coordinates at or south of 27°N. They include Port Everglades (UF 142820, 1960; UF 233907, 1959), Buttonwood Canal / Everglades National Park (UF 164232, 1962), Sands Key / Miami-Dade (UF 193180, 1963), and additional offshore southwest Florida / eastern Gulf records. These are preserved-specimen occurrence records, not population estimates.
- Recent Florida vouchers include Tampa Bay / Pinellas records from 2020 and 2024; these do not imply recent South Florida occupancy.
- The archive's license is CC-BY-NC 4.0. Preserve attribution and non-commercial restrictions in any downstream use.

### Combined interpretation and next research step

The acquisition adds three distinct evidence streams: FWC standardized positive-catch survey records, NPS fisheries-dependent reported catches, and Florida Museum preserved vouchers. They must remain separate in any analysis. FWC has a large positive-catch extract but almost no target positives south of 27°N and no public zero-catch denominator; NPS documents historical reported catches around Flamingo through 1997; museum vouchers independently document historical South Florida occurrences, including Miami-Dade, Broward, and Everglades National Park.

This strengthens the conclusion that South Florida is not an absolute historical biological void, while leaving contemporary distribution, abundance, and habitat-specific occupancy unresolved. Do not create a hard range boundary or mask from these data. Next: inspect the NPS metadata/code definitions and FWC gear/survey-zone documentation; then spatially reconcile the voucher and creel localities with the existing NOAA sample-level evidence. No model, species profile, geographic mask, scoring, confidence, ingestion, production source, or publishing behavior was changed.

### Artifact contents

The complete read-only artifact contains source CSV/XML files, the FWC ArcGIS metadata and 6,008-row positive-catch extract (CSV and GeoJSON), the Florida Museum Darwin Core Archive and 221-row candidate extract, NPS source files and candidate extracts, plus `acquisition_summary.json`. No raw data were committed to the repository.


## FWC gear-code and NPS creel metadata audit | 2026-11-28

### FWC/FWRI gear codes resolved

The FWC FGDC metadata explicitly defines every gear code present in the 6,008-record Southern flounder positive-catch extract. The previous open question about gear-code meaning is resolved:

| Gear code | FWC definition | Southern flounder positive-catch rows | Fish represented by TotalNum |
|---:|---|---:|---:|
| 20 | 21.3-m seine (bay set) | 151 | 284 |
| 23 | 21.3-m seine (river set) | 1,365 | 2,194 |
| 160 | 183-m haul seine | 1,562 | 3,338 |
| 300 | 6.1-m trawl (straight tow) | 2,723 | 4,135 |
| 301 | 6.1-m trawl (arc tow) | 207 | 531 |
| **Total** | | **6,008** | **10,482** |

The metadata defines `avg_size`, `min_size`, and `max_size` in **millimeters**. This resolves the unit uncertainty for the previously extracted FWC size fields. `Reference` is a unique alphanumeric identifier for each gear deployment.

The southernmost positive record remains:
- Reference: `TQM1997070901`
- Date: 1997-07-09
- Position: 26.843167°N, 80.042667°W
- Gear: 160, 183-m haul seine
- `TotalNum`: 2
- Size: average 95 mm, range 85–105 mm

Across the target extract, only this one positive record is south of 27°N; no positive record is south of 26.5°N. The metadata also confirms the export is filtered to `CNT > 0`, and that the export's 2025 processing step selected only gear types 5, 20, 23, 160, 300, and 301. The 6,008 records therefore describe positive catches within this selected gear domain, not every FIM deployment.

### FWC sampling-frame qualification

FWC's public SRS overview states that routine FIM sampling is currently conducted in seven estuarine regions: Apalachicola Bay, Cedar Key, Tampa Bay, Sarasota Bay, Charlotte Harbor, Indian River Lagoon, and Northeast Florida. It separately says similar surveys are conducted with special funding in St. Andrew's Bay, the Florida Everglades, and Florida Bay.

The 2023 FIM Annual Data Summary's core SRS methods/table lists routine study areas and gears, but does not list Florida Bay or the Everglades among the ten routine SRS areas in its 2023 table. This supports treating the public Inshore SRS layer and the separate Florida Bay/Everglades special-funded monitoring programs as potentially distinct evidence streams until their source records are crosswalked. It does **not** prove that no Florida Bay data exist in FWC systems.

The layer's metadata bounding box extends south to 24.5°N, but a broad geographic bounding box is not proof that each estuary or habitat stratum was sampled. Likewise, a lack of Southern flounder rows in a positive-catch-only export is not a zero-catch result. The target's southernmost positive point is an observation boundary in this extract only, not a species range boundary.

### NPS Everglades creel fishing-area codes resolved

The NPS metadata states that `areaFished` refers to the polygons in `EVER_creel_fishing_areas.csv`. Before 1998, the dataset used numeric fishing areas 1–6; in 1998 these were subdivided into alphanumeric zones. The 210 Southern flounder catch rows map to:

| Recorded area code | Interpreted area from NPS area file | Catch rows | Reported fish |
|---:|---|---:|---:|
| 1 | Northeastern / Northwestern Florida Bay (later 1E / 1W) | 86 | 110 |
| 2 | Southeastern / Southwestern Florida Bay (later 2E / 2W) | 8 | 11 |
| 3 | Eastern / Western Cape Sable (later 3E / 3W) | 39 | 44 |
| 4 | Whitewater Bay | 34 | 36 |
| 5 | Shark River | 42 | 69 |
| 6 | Ten Thousand Islands (later 6N / 6C / 6S) | 1 | 1 |
| **Total** | | **210** | **271** |

The 209 Flamingo rows and one Everglades City row are all retained. The one Everglades City catch row is in area 4. The NPS polygon file supplies the current alphanumeric zone names and geometries; historical numeric records can only be resolved to the corresponding grouped geography, not to a more precise subzone.

### NPS key and QA/QC qualification

The NPS metadata describes the catch table's compound primary key as `interviewLocation + eventDate + interviewNumber + scientificName_catch`, and says it joins to the flags table. The Southern flounder subset has 210 rows but only 205 unique combinations of those four fields. Five combinations occur twice, once as `harvested` and once as `released`. Thus the documented four-field key is **not unique in this target subset**. Preserve disposition as an additional row discriminator when retaining the 210 catch records; do not collapse the split harvested/released records or treat them as duplicate fish observations. The metadata's stated key needs a broader source-level uniqueness audit before it is relied on as a strict primary key.

The metadata defines `disposition` as harvested or released, and says it is NA for a non-fishing vessel or when no fish were caught. It defines `interviewNumber` as a survey number assigned at the interview location and date, generally incrementing through the weekend. The `flags` field is the number of unique automated QA/QC flags assigned to a data record; detailed descriptions are in the separate flags file.

The 538 flag rows associated with the Southern flounder candidate set occur across 179 of the 205 interview combinations. The flag descriptions are:
- `trip_hours should be >= 0` (179)
- `Party composition should be 0; 1; 2; 3; or 4` (179)
- `Species preference valid?` (179)
- `Number of people fishing seems high (>8) for rec trip` (1)

These descriptions concern interview-level trip-hours, party-composition, species-preference, and party-size checks. None directly states that the Southern flounder identification or its catch count is invalid. Keep the flags attached as QA context; do not automatically discard the catch records. Because the catch subset contains repeated four-field keys, the join must preserve disposition and must not imply that each flag is uniquely tied to one disposition row unless the source data establish that.

The NPS catch records are angler-intercept reports from sampled returning anglers, not standardized fishery-independent survey catches. They document reported historical catches in the named fishing areas through 1997; they do not estimate abundance or establish that the species was absent after the last recorded candidate.

### Updated evidence interpretation

This audit resolves FWC gear meanings and size units, and resolves the broad geographic interpretation of NPS area codes. It also finds a source metadata inconsistency: the NPS-declared four-field compound primary key is not unique for the Southern flounder candidate rows because five interview/species combinations are split into separate harvest and release records. Preserve all 210 rows and add disposition when constructing a working key.

The FWC extract still cannot provide a South Florida non-detection denominator, and its sampling coverage must not be conflated with separate Florida Bay/Everglades projects. The NPS dataset adds historically localized angler-reported catches across Florida Bay, Cape Sable, Whitewater Bay, Shark River, and one Ten Thousand Islands record. These findings strengthen historical occurrence evidence but do not support a current occupancy boundary or a production mask.

### Additional sources

- FWC/FWRI. [Inshore Saltwater FIM SRS FGDC metadata](https://www.arcgis.com/sharing/rest/content/items/68fb6774b58a40a08a6f87959aaa53c4/info/metadata/metadata.xml?format=default&output=html), especially gear-code domain, size units, filtering, and quality statements.
- FWC/FWRI. [Fisheries-Independent Monitoring Using Stratified-Random Sampling](https://myfwc.com/research/saltwater/fim/stratified/), current routine regions and separately funded Florida Everglades / Florida Bay surveys.
- FWC/FWRI. [2023 FIM Annual Data Summary Report](https://archive.myfwc.com/archive/Research/Saltwater/FIM/fim-annual-report-2023.pdf), Methods and Table 1–2, routine 2023 SRS study areas and gear usage.
- National Park Service. [Everglades recreational catch and effort data package](https://catalog.data.gov/dataset/recreational-fishing-catch-and-effort-in-everglades-national-park-1980-2025-data-package), source metadata, fishing-area polygons, catch/flags definitions.


## NOAA/AOML Florida Bay juvenile sportfish raw-data source located | 2026-11-28

A further public source was located beyond the 2021 aggregate report: NOAA/AOML's Florida Bay juvenile sportfish observations are exposed through two GCOOS ERDDAP datasets with downloadable CSV source files. This creates a path to event-level target observations and individual measurements.

### Main species-sample dataset

**Dataset:** [Juvenile Sportfish Monitoring in Florida Bay, Everglades National Park](https://gcoos4.geos.tamu.edu/erddap/tabledap/juvenile_sportfish.html)  
**Dataset ID:** `juvenile_sportfish`  
**Source CSV:** [juvenilefish_sportfishlengths.csv](https://gcoos4.geos.tamu.edu/erddap/files/juvenile_sportfish/juvenilefish_sportfishlengths.csv)

The ERDDAP metadata reports:
- Coverage: 2004-09-21 through 2016-11-12.
- Coordinates: 24.999–25.167°N, -81.063 to -80.642°W.
- Instrument: otter trawl.
- Fields include time, coordinates, station, location, zone, area towed, scientific/common name, species count, individual length, salinity, temperature, and seagrass metrics.
- `SpeciesCount` is the number of individuals of a species collected in a sample.
- `IndividualLength` is the measured length of a collected individual, in millimeters.
- Salinity is in PSU; water temperature is in degrees Celsius.
- The ERDDAP metadata identifies the source as a component of the CERP RECOVER Monitoring and Assessment Plan and displays a CC0 public-domain license.

### Collection-station individual-measurement dataset

**Dataset:** [Collection station measurements of the Juvenile Sportfish Monitoring in Florida Bay](https://gcoos4.geos.tamu.edu/erddap/tabledap/juvenile_sportfish_collection_stn.html)  
**Dataset ID:** `juvenile_sportfish_collection_stn`  
**Source CSV:** [juvenilefish_CollectionStnData.csv](https://gcoos4.geos.tamu.edu/erddap/files/juvenile_sportfish_collection_stn/juvenilefish_CollectionStnData.csv)

Its metadata reports:
- Coverage: 2009-06-06 through 2016-11-12.
- The dataset complements the main species-sample table.
- At a subset of 12 stations each month, all fish in the tow were collected, preserved in alcohol, and taken to the laboratory for measurement and identification.
- Fields include time, coordinates, keyfield, station, subregion, scientific name (`Genus_sp`), common name, standard length, total length, weight, and species code.
- Lengths are in millimeters; weight is in grams.
- The keyfield is described as a concatenation of year, month, and station number.
- The ERDDAP metadata displays a CC0 public-domain license.

### Critical interpretation limits

These datasets are not a complete replacement for the 2004–2019 report:
- The main ERDDAP dataset currently advertises data only through November 2016, while the NOAA report summarizes a 2004–2019 period.
- The collection-station dataset begins in June 2009 and covers only the subset of 12 stations sampled each month.
- The phrase “12 stations each month” describes the collection-station design. It is **not** the same statistic as Table 5's `n = 12` Southern flounder site samples in the NOAA report. Do not conflate those two uses of 12.
- The collection-station dataset contains measured individual specimens from a subset of stations, not a complete survey-wide zero-catch denominator.
- The raw CSVs and candidate rows have not yet been downloaded and audited in GitHub Actions. No Southern flounder row count, dates, coordinates, or length result is claimed from these ERDDAP files yet.

### Reproducible acquisition added

Updated `scripts/acquire_south_florida_public_evidence.py` to download both ERDDAP source CSVs and their metadata pages, preserve the raw files in the temporary artifact, and produce exact-scientific-name candidate extracts. The two datasets are recorded separately so sample-level species counts are not confused with individual specimen measurements.

The existing manual-only workflow remains the acquisition entry point:
[South Florida Public Evidence Acquisition](../actions/workflows/south-florida-public-evidence-acquisition.yml).

The script update is committed on `main`, but this expanded workflow has **not yet been run**. After dispatch, inspect source failures, CSV headers, exact-name candidate counts, repeated sample keys, species counts versus individual lengths, date/coordinate coverage, and agreement with the NOAA report before treating any target rows as verified.

### Additional sources

- NOAA/AOML + GCOOS. [Main juvenile sportfish ERDDAP dataset](https://gcoos4.geos.tamu.edu/erddap/tabledap/juvenile_sportfish.html).
- NOAA/AOML + GCOOS. [Collection-station individual-measurement ERDDAP dataset](https://gcoos4.geos.tamu.edu/erddap/tabledap/juvenile_sportfish_collection_stn.html).
- NOAA/AOML. [Juvenile Sportfish Survey project overview](https://www.aoml.noaa.gov/juvenile-sportfish-survey/), describing the ongoing Florida Bay monitoring project and its May–November sampling window.
