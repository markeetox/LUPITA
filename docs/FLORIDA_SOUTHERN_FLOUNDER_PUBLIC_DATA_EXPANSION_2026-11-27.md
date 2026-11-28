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

The dataset is public domain (CC0). During the initial source-discovery review, the CSV download endpoint returned an unsupported content type and the files were not ingested at that stage. They were subsequently acquired and audited in the 2026-11-28 workflow run documented below.

When acquired, analyze species identity, catch disposition, fishing area, date, number of anglers, trip duration/effort, and QA/QC flags. This is fisheries-dependent evidence and must remain separate from standardized FIM or NOAA survey evidence. Angler target, access, gear, effort, and reporting affect detection.

## 5. Florida Museum Ichthyology occurrence archive

The Florida Museum's UF FLMNH Ichthyology IPT resource publishes a Darwin Core Archive and metadata, is updated daily, and carries a CC-BY-NC 4.0 license. The archive is a reproducible public source for expanding the voucher review beyond the currently reviewed catalog records.

During the initial source-discovery review, the resource page and archive endpoint were verified but the archive had not yet been downloaded. The archive was subsequently acquired and reprocessed in the 2026-11-28 workflow run documented below. The earlier catalog-level findings for UF 164232, UF 142820, and UF 233907 remain as previously documented. A resource-wide record count is not a substitute for verifying target taxon records and catalog-level metadata.

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


## NOAA/AOML Florida Bay raw-data audit | workflow run 46158258337 | 2026-11-28

### Acquisition result

The expanded [South Florida Public Evidence Acquisition workflow](https://github.com/markeetox/LUPITA/actions/runs/46158258337) completed successfully on `main` at source commit `d9fd5caaa696951a8b6ec9d49b5e423617eb2b8d`. Artifact: `south-florida-public-evidence`, ID `15268192641`, 28,887,077 bytes, expires 2026-12-12.

Both NOAA/AOML ERDDAP source CSVs and their metadata pages were acquired:
- Main species-sample table: 11,473 rows.
- Collection-station individual-measurement table: 65,454 rows.
- No acquisition source failures were recorded.

### Main species-sample table: nine exact Southern flounder rows

Exact `ScientificName = Paralichthys lethostigma` extraction returned **9 rows**, each with `SpeciesCount = 1`. The rows have nine unique `Keyfield` values and represent nine recorded individuals in this table.

| Date (UTC) | Station | Zone | Latitude | Longitude | IndividualLength (mm) | Salinity (PSU) | Temperature (°C) |
|---|---:|---|---:|---:|---:|---:|---:|
| 2005-11-11 | 70 | West | 25.132 | -80.941 | not reported | 34.00 | 25.00 |
| 2008-07-13 | 323 | Crocodile | 25.137 | -80.705 | 84 | 40.40 | 29.10 |
| 2008-09-17 | 621 | Crocodile | 25.167 | -80.664 | 120 | 38.30 | 30.50 |
| 2008-10-11 | 70 | West | 25.132 | -80.941 | 255 | 33.30 | 30.70 |
| 2009-07-11 | 67 | West | 25.134 | -80.967 | 72 | 37.70 | 32.30 |
| 2011-07-17 | 174 | West | 25.128 | -80.889 | 180 | 34.90 | 30.39 |
| 2016-09-04 | 70 | West | 25.132 | -80.941 | not reported | 38.40 | 32.00 |
| 2016-09-04 | 176 | West | 25.100 | -80.866 | not reported | 38.70 | 31.00 |
| 2016-11-10 | 237 | Rankin | 25.126 | -80.863 | not reported | 35.64 | 23.61 |

Summary:
- Dates: 2005-11-11 through 2016-11-10.
- Coordinates: 25.100–25.167°N, 80.967–80.664°W.
- Zones: West (6 records), Crocodile (2), Rankin (1).
- Nine rows, nine unique sample keyfields, nine individuals according to `SpeciesCount`.
- Five records have an `IndividualLength` value: 72, 84, 120, 180, and 255 mm. Four rows have no individual length recorded. Do not treat missing length as zero or infer fish size from other fields.
- Salinity: 33.3–40.4 PSU; mean 36.82 PSU; sample standard deviation 2.43 PSU.
- Temperature: 23.61–32.30 °C.

### Reconciliation with NOAA 2021 report Table 5

The 2021 NOAA report's Table 5 reports `n = 12` site samples for Southern flounder, salinity range 33.3–40.4 PSU, and mean 36.7 ± 2.31 PSU. The nine raw-table rows audited here reproduce the reported salinity minimum and maximum, and their mean (36.82) is close to the report's rounded mean (36.7). Their sample standard deviation (2.43) is not identical to the reported ±2.31, and the raw extract contains nine rows rather than the report's 12 site samples.

This is a material but unresolved discrepancy. The nine records may not represent the same aggregation unit or complete source extraction used for Table 5, or three site samples may be absent from this ERDDAP export. Do not assert that the nine rows fully reproduce the report's n=12. Follow-up should inspect the report's underlying table/definitions and source data provenance, and check for alternate taxonomic spellings, duplicate/aggregated observations, and any report-only records. The observed similarity of salinity range and mean is a consistency clue, not proof of a one-to-one match.

### Collection-station measurement table

The 65,454-row collection-station table produced **zero exact-name `Paralichthys lethostigma` rows** under its `Genus_sp` field. A broader text check also found no `Paralichthys` or flounder strings. This does not negate the nine main-table detections: the collection-station dataset is a subset of 12 stations per month, not the full species-sample table, and the two tables have different inclusion/measurement designs. The main table itself has five individual length values.

### Evidence interpretation

This is direct, georeferenced, fishery-independent survey evidence of Southern flounder in Florida Bay from 2005 through 2016, with recorded salinity and temperature at each sample. It is much more useful than a generalized range point because each row has a date, location, sample key, count, and environmental measurements.

It still does not establish population abundance, current occupancy after 2016, a complete zero-catch denominator, or a southern range boundary. It is also not yet fully reconciled with the NOAA report's n=12. Keep the nine rows as raw-source observations and the report's 12 as a separate published summary until the discrepancy is resolved.

### Reproducibility

The workflow artifact contains:
- `noaa_florida_bay/species_samples.csv` (full 11,473-row main source table)
- `noaa_florida_bay/species_samples_southern_flounder_candidates.csv` (nine exact-name rows)
- `noaa_florida_bay/species_samples_erddap_metadata.html`
- `noaa_florida_bay/collection_station.csv` (full 65,454-row subset table)
- `noaa_florida_bay/collection_station_southern_flounder_candidates.csv` (header only; zero target rows)
- `noaa_florida_bay/collection_station_erddap_metadata.html`

No raw source files were committed to the repository. No species profile, geographic mask, scoring, confidence, ingestion, production source, or publishing behavior changed.


## 2026-11-28 follow-up | NOAA report-versus-ERDDAP coverage reconciliation

A fresh inspection of the primary NOAA report and current ERDDAP metadata identified a concrete coverage gap that may explain the unresolved count difference:

- NOAA Technical Report OAR-AOML-48 covers monitoring results from 2004 through 2019. Table 5 reports Southern flounder at **12 site samples**.
- The main NOAA/AOML ERDDAP species-sample table advertises temporal coverage only from **2004-09-21 through 2016-11-12**. Its nine exact-name Southern flounder rows therefore cannot, by themselves, represent the full 2004–2019 report period.
- The NOAA/AOML public data page links a historical Excel workbook titled **Juvenile Sportfish Survey Data**. A 2023 peer-reviewed paper's reference list identifies the downloadable workbook as `Master-Juvenile-Sportfish-NOAA-updated-06.11.19.xlsx`, hosted at:
  https://www.aoml.noaa.gov/wp-content/uploads/2019/06/Master-Juvenile-Sportfish-NOAA-updated-06.11.19.xlsx
- The workbook is a newly identified acquisition target, not yet an audited data source in this repository. Its actual sheet structure, coverage, taxonomic fields, and Southern flounder rows have not yet been inspected. Do not assume it contains the three missing site samples until it is downloaded and cross-checked.

The report's Methods section also clarifies two different sampling products: all sizes of other sportfish caught were identified, measured, and counted in every tow; separately, a subset of 12 stations per month beginning in 2009 had all organisms under 100 mm total length preserved and measured in the lab. The ERDDAP collection-station table describes this latter subset, not the complete main survey species table. Its zero exact-name rows therefore do not contradict the nine detections in the main table.

### Reconciliation status and next action

The most defensible current explanation is that the ERDDAP export's 2016 endpoint may omit later survey records included in the report's 2004–2019 summary. This is a hypothesis supported by the difference in coverage periods, not a verified reconciliation. Other differences in aggregation or data processing remain possible.

The manual acquisition script now downloads the NOAA/AOML June 2019 workbook into the same expiring research artifact as the ERDDAP files. On the next dispatch, inspect workbook sheets, row counts, date coverage, species/code columns, and all exact `Paralichthys lethostigma` / `Pal` records. Compare unique sample keys and salinity values with both the nine ERDDAP rows and Table 5. Keep the workbook separate from the ERDDAP extract until provenance and inclusion rules are established.

Sources:
- NOAA report: https://doi.org/10.25923/sec9-mf34
- Main ERDDAP metadata and coverage: https://gcoos4.geos.tamu.edu/erddap/tabledap/juvenile_sportfish.html
- Collection-station ERDDAP metadata and subset definition: https://gcoos4.geos.tamu.edu/erddap/tabledap/juvenile_sportfish_collection_stn.html
- NOAA/AOML data portal: https://www.aoml.noaa.gov/data-products/
- 2019 workbook URL cited by James et al. (2023): https://www.aoml.noaa.gov/wp-content/uploads/2019/06/Master-Juvenile-Sportfish-NOAA-updated-06.11.19.xlsx

No raw workbook was committed. No species profile, geographic mask, scoring, confidence, ingestion, production source, or publishing behavior changed.


### 2026-11-28 follow-up | NOAA workbook acquisition attempt

Manual workflow [run 46160840439](https://github.com/markeetox/LUPITA/actions/runs/46160840439) completed successfully on `main`, source SHA `92491226ff379597cb50b1cfcf3b05873f355a4f`. Artifact ID `15269970886` (`south-florida-public-evidence`, 28,887,271 bytes; expires 2026-12-12). The existing ERDDAP, NPS, FWC, and Florida Museum downloads completed and were retained in the artifact.

The newly added NOAA/AOML 2019 workbook request was attempted four times by the acquisition script but failed with HTTP 403 Forbidden at the cited direct URL. The workbook is not present in this artifact and has not been audited. The failure is explicitly recorded in `acquisition_summary.json`; it is not a failure of the overall acquisition job.

NOAA/AOML's current public data-products page still advertises a downloadable Juvenile Sportfish Survey Data workbook, confirming that a workbook download remains an official acquisition route. However, the current page's link target could not be independently recovered in this run, and the previously cited 2019 URL remains blocked to the workflow client. Next step: resolve the current official download URL or test a browser-style request with an appropriate referer before repeating the manual acquisition. Do not infer workbook contents or use the report's n=12 to fill the three-row gap until the underlying records are inspected.

Sources: https://www.aoml.noaa.gov/data-products/ ; https://www.aoml.noaa.gov/juvenile-sportfish-survey/ ; https://www.aoml.noaa.gov/wp-content/uploads/2019/06/Master-Juvenile-Sportfish-NOAA-updated-06.11.19.xlsx

No raw data were committed. No species profile, geographic mask, scoring, confidence, ingestion, production source, or publishing behavior changed.


### 2026-11-28 follow-up | workbook HTTP 403 and fallback request

The subsequent manual acquisition run [46160840439](https://github.com/markeetox/LUPITA/actions/runs/46160840439) completed successfully overall, but the NOAA/AOML 2019 workbook request returned HTTP 403 after the standard request retries. The workbook is not in artifact 15269970886 and has not been audited. The other NOAA ERDDAP, NPS, FWC, and Florida Museum sources were acquired normally.

The acquisition script now retries this workbook alone after a standard-request failure, using a conventional browser User-Agent, an Accept header for an XLSX download, and the official NOAA/AOML data-products page as the Referer. This is a compatibility retry against the same public URL; it does not bypass authentication or change source content. The first request's error and the fallback request's error are both retained in the artifact summary if both fail.

**Next:** manually dispatch the acquisition workflow again. If the fallback succeeds, inspect workbook sheets, date coverage, taxonomic fields/aliases, unique sample keys, and Southern flounder rows before reconciling the nine ERDDAP records with Table 5's n=12. If it still returns 403, identify the current official NOAA workbook link or another publicly accessible NOAA-hosted copy. Do not treat the workbook as acquired until it appears in the artifact and passes file-format/integrity checks.

No raw data were committed. No species profile, range mask, scoring, confidence, ingestion, production source, or publishing behavior changed.


### 2026-11-28 follow-up | acquisition run 5: browser fallback also blocked

Manual acquisition [run 46168260876](https://github.com/markeetox/LUPITA/actions/runs/46168260876) completed successfully on `main` at `97d1c7419d31ae2f1c8aaaa717b67cb83681aa92`. Artifact ID `15272448030` (28,887,331 bytes; expires 2026-12-12). The NOAA/AOML 2019 workbook was attempted using both the standard request and the browser-header fallback (User-Agent, XLSX Accept header, and official data-products Referer). Both attempts returned HTTP 403. The workbook is absent from the artifact and remains unaudited.

The current NOAA/AOML [Data Products page](https://www.aoml.noaa.gov/data-products/) still advertises a downloadable Juvenile Sportfish Survey .xlsx workbook, but indexed page content does not expose a different verified download URL. The NOAA ERDDAP main species dataset remains available in the artifact: 11,473 rows, nine exact `Paralichthys lethostigma` records, each with SpeciesCount=1. Searching distinct scientific/common-name combinations in the full table found only `Paralichthys lethostigma` (Southern Flounder) and `Paralichthys albigutta` (Gulf Flounder); no alternate Southern Flounder spelling or common-name alias was found in this export.

This does not resolve the difference between the nine accessible ERDDAP rows and report Table 5's n=12 site samples. The ERDDAP table advertises coverage ending 2016-11-12, while the report summarizes 2004–2019; the later workbook remains the most direct public lead, but its current advertised link is blocked from automated retrieval. Do not infer that the three-row difference represents later years without row-level evidence. No raw data were committed and no species/model behavior changed.

**Next:** investigate the NOAA/AOML page's actual current link target through another public, verifiable source or accessible browser route. If no public route exposes the file, retain the documented limitation and continue using the nine ERDDAP records as a distinct, bounded evidence set. Do not add inferred rows or reconcile n=12 by assumption.


### 2026-11-28 follow-up | clarify what Table 5 n represents

A closer review of the primary NOAA report clarifies the denominator terminology. Table 5 is explicitly captioned as reporting “site sample size (n)” for the listed species; Southern flounder is listed as `n=12`, salinity range 33.3–40.4 ppt, mean 36.7 ± 2.31. This is a count of site samples, not a count of individual fish. The report's methods state that all sizes of other sportfish caught in every tow were identified, measured, and counted; a separate subset of 12 stations per month beginning in 2009 was used to preserve and lab-identify all organisms under 100 mm. These are different concepts and should not be conflated. See the [NOAA report](https://repository.library.noaa.gov/view/noaa/28764/noaa_28764_DS1.pdf), especially its Methods section and Table 5.

The accessible ERDDAP main species table contains nine exact Southern flounder sample rows, each with `SpeciesCount=1`, and its advertised coverage ends 2016-11-12. The report covers 2004–2019. Later-year records are one possible explanation for the difference, but this remains unverified; no three records are imputed. The 12-station collection-measurement subset is not a substitute for the full species-sample table.

### 2026-11-28 follow-up | NOAA/AOML 2024 annual report extends Florida Bay evidence through 2023

Located and reviewed the NOAA/AOML 2024 annual report, *Juvenile Sportfish Monitoring in Florida Bay, Everglades National Park: Monitoring and Assessment Plan Results from 2004 through 2023* (SeFSC-PEMD-HEB 2024-02; August 1, 2024). Public report: https://cerp-sfwmd.dataone.org/metacat/d1/mn/v2/object/urn:uuid:8e477b75-cc15-49c4-b009-2d3d5408abae.

The report's Table 1 is captioned as the list of 26 target species observed in the study area since the project's inception in 2004; Southern Flounder is included in the report's species list. Table 5 also includes Southern Flounder among the 26 taxa and describes salinity ranges, means, standard deviations, and sample size. Figure 14 is explicitly based on all MAP observations from 2004–2023. This is a more recent program-level source than the 2004–2019 report and confirms that Southern Flounder remains part of the Florida Bay monitoring record through the report's 2023 reporting period. It does not provide event-level Southern flounder dates, coordinates, or sample identifiers in the extracted report text.

The 2024 report's Methods section clarifies that juvenile spotted seatrout were the main target, but all sizes of other sportfish and additional fish/macroinvertebrate species caught in every tow were identified, measured, and counted. Separately, from 2009 onward, a subset of 12 stations per month (five West, two Rankin, two Whipray, three Crocodile Dragover) had all organisms under 100 mm preserved and identified/measured in the lab. This 12-station monthly subset is a laboratory-processing design, not the Southern flounder sample count in the 2021 report.

**Important denominator distinction:** the 2021 OAR-AOML-48 Table 5 caption explicitly calls its n a *site sample size*; Southern Flounder is reported as n=12. The 2024 report's Table 5 caption instead describes n as the *number of individuals sampled*. These are not interchangeable denominators. The nine ERDDAP records are nine species-sample rows, each with SpeciesCount=1, and the accessible table ends in 2016. The newer report's table values were not independently extracted from its rendered table graphic in this review. Do not compare its n directly with the 2021 n=12, and do not infer that the three-row ERDDAP difference represents 2017–2019 records.

The 2018 OAR-AOML-54 report's Table 4 caption says it covers 25 species enumerated since inception in 2004, but the extracted searchable text does not expose the individual species rows. The absence of a searchable “Southern Flounder” or “Paralichthys” hit in that PDF is therefore not evidence that the taxon was absent from the table or program. No species-list change between the 2018 and 2019 reports is established here.

### Current reconciliation status

- 2021 OAR-AOML-48: Southern Flounder listed; n=12 site samples; salinity 33.3–40.4 ppt; mean 36.7 ± 2.31 ppt.
- Public NOAA/AOML ERDDAP main table: nine exact Southern Flounder sample rows, each SpeciesCount=1; dates 2005-11-11 to 2016-11-10; salinity 33.3–40.4 PSU, mean 36.82, sample SD 2.43.
- 2024 SeFSC-PEMD-HEB 2024-02 report: Southern Flounder remains in the species list; report covers MAP observations 2004–2023; Table 5 defines n as individuals sampled rather than site sample size. Event-level dates/coordinates and the rendered table's Southern Flounder numeric row were not extracted.
- NOAA 2019 workbook: still blocked with HTTP 403 on both standard and browser-header attempts in acquisition run 46168260876.

This adds stronger program-level occurrence evidence but does not resolve the row-count/denominator discrepancy. The correct status remains **unresolved, not contradictory**. Do not impute three records or change any species model/profile/mask/scoring behavior.

Sources:
- 2024 NOAA/AOML annual report: https://cerp-sfwmd.dataone.org/metacat/d1/mn/v2/object/urn:uuid:8e477b75-cc15-49c4-b009-2d3d5408abae
- 2021 OAR-AOML-48 report: https://repository.library.noaa.gov/view/noaa/28764/noaa_28764_DS1.pdf
- 2018 OAR-AOML-54 report: https://repository.library.noaa.gov/view/noaa/32734/noaa_32734_DS1.pdf
- Main ERDDAP dataset: https://gcoos4.geos.tamu.edu/erddap/tabledap/juvenile_sportfish.html

No raw data were committed. No species profile, geographic mask, scoring, confidence, ingestion, production source, or publishing behavior changed.

### 2026-11-28 follow-up | FWC full FIM data portal and SECOORA ERDDAP alternative assessed

Located the Florida SEACAR Data Discovery record for FWC Fisheries-Independent Monitoring Program 69: https://data.florida-seacar.org/programs/details/69.

The current program record (updated 2026-08-31) describes a monthly stratified-random program beginning in 1989 and continuing to the present, with approximately 10,000 net deployments annually. It says all collected nekton are identified to the lowest practical taxonomic level and records include species, size, sex, catch numbers, temperature, salinity, dissolved oxygen, pH, conductivity, habitat, coordinates, weather, tide, Secchi depth, and depth. SEACAR lists standardized Nekton and Discrete Water Quality exports updated September 2026, plus a GIS export and source documentation.

This is a promising route to a fuller FWC sample/event denominator than the positive-catch-only ArcGIS layer previously audited. However, the SEACAR page also states that the underlying data location is by request from the FWC FIM program director and that downloads require a valid email address, first/last name, organization, occupation, and purpose. No form was submitted, no personal contact information was supplied, and no FWC export was downloaded. This route is therefore recorded as an access-gated lead, not as acquired public data. It also does not yet establish whether the full export includes Florida Bay special-program sampling; the 2023 core FIM report and current SEACAR managed-area list must not be treated as proof of a Florida Bay sampling frame.

A separate public SECOORA ERDDAP dataset, FIMMAP_Counts, was assessed as a possible no-form alternative: https://erddap.secoora.org/erddap/tabledap/FIMMAP_Counts.html. Its metadata describes a limited large-haul-seine monitoring subset in Tampa Bay, Charlotte Harbor, Northern and Southern Indian River Lagoon, Cedar Key, Apalachicola Bay, and Jacksonville. Florida Bay is not in the dataset summary's listed coverage, so this is not a suitable substitute for the Florida Bay survey denominator. Its IOOS schema states that individualCount=0 represents absence only when the methodology for establishing absence is documented; positive values represent presence. No species-specific South Florida query or count is claimed from this dataset.

**Conclusion:** the SEACAR FIM export is a potentially valuable source for a later, authorized download, but it is not currently accessible without submitting identifying contact information. The SECOORA ERDDAP alternative is openly queryable but does not cover Florida Bay in its documented summary. Neither source changes the existing Florida Bay evidence assessment. Continue to keep FWC positive-catch records, Florida Bay NOAA trawl records, NPS reported catch, and museum vouchers separate.

Sources:
- FWC/SEACAR Program 69: https://data.florida-seacar.org/programs/details/69
- SECOORA FIMMAP_Counts ERDDAP: https://erddap.secoora.org/erddap/tabledap/FIMMAP_Counts.html
- FWC 2023 FIM annual report: https://archive.myfwc.com/archive/Research/Saltwater/FIM/fim-annual-report-2023.pdf

No download form was submitted, no contact information was used, and no raw data were acquired. No species profile, geographic mask, scoring, confidence, ingestion, production source, or publishing behavior changed.

### 2026-11-28 follow-up | Florida Bay acoustic telemetry network identified as a supplementary lead

Located the FACT/SECOORA project *How are Fish using Florida Bay: Impacts and Effects of Seagrass Distribution*: https://secoora.org/fact/projects/how-are-fish-using-florida-bay-impacts-and-effects-of-seagrass-distribution/.

The project page describes a Florida Bay acoustic telemetry study using 70 listening stations and 250 internal fish tags to investigate recreational sportfish movement in relation to seagrass distribution and the 2015 seagrass die-off. Lead organizations include Florida International University, NOAA, FWC/FWRI, with Everglades National Park as a partner. The project is marked ongoing and identifies FACT code CELASE.

The Ocean Tracking Network public data discovery catalog lists a corresponding project dataset, V2LCELASE, titled *Sportfish movement in Florida Bay*. The catalog reports 20,730,746 records and a last-modified date of 2026-10-16. Its public listing identifies 100 stations and 478 deployments. These are catalog record/deployment counts, not unique fish counts, detections of Southern Flounder, or proof of a target-species occurrence.

This is a strong candidate supplementary source for Florida Bay habitat connectivity and movement context. However, the public project description does not name the tagged species, and a species-specific Southern Flounder inclusion/detection has not been verified. Do not treat the large telemetry record count as abundance or occupancy evidence. Before using this source for Southern Flounder, the tagged-animal metadata and species list must be inspected and any individual tag/detection records must be taxonomically confirmed. If the target species is not among the tagged animals, the dataset may still be relevant only as general ecosystem/movement context, not target-species evidence.

The OTN/FACT telemetry dataset is distinct from NOAA's juvenile sportfish otter-trawl monitoring and from FWC FIM sampling. Keep those data streams separate. No OTN data were downloaded or incorporated in this review.

Sources:
- FACT/SECOORA project description: https://secoora.org/fact/projects/how-are-fish-using-florida-bay-impacts-and-effects-of-seagrass-distribution/
- OTN public data discovery listing: https://members.oceantrack.org/data/discovery/bypublic.htm

No species-specific Southern Flounder telemetry record is claimed. No model/profile/mask/scoring/production change.

### 2026-11-28 follow-up | Two additional Southern Flounder telemetry catalog leads

The Ocean Tracking Network/FACT catalog also lists two species-specific data projects associated with East Carolina University:
- SOFLOAR — *Southern Flounder on Artificial Reefs*
- SOFLONC — *ECU Southern Flounder Spawning Study*

The catalog lists both as data projects but reports Records=NA and LastModified=NA. This establishes that the projects are cataloged, not that downloadable event-level data are available or that either study covers South Florida. Their geographic coverage, methods, dates, sample sizes, and public data accessibility remain unverified. They may provide useful species ecology or movement context after their project metadata/publications are identified, but they must not be treated as Florida Bay occurrence evidence. No outreach or direct contact was initiated.

Sources:
- OTN catalog collection listing: https://members.oceantrack.org/data/discovery/bycollection.htm
- OTN catalog contact/institution listing: https://members.oceantrack.org/data/discovery/bycontact.htm

No data were downloaded; no new Southern Flounder locations or occurrences are claimed.

### 2026-11-28 follow-up | Acoustic telemetry species crosswalk and Carolinas Southern Flounder studies

#### Florida Bay CELASE project: tagged species identified

The FACT/SECOORA project page for *How are Fish using Florida Bay: Impacts and Effects of Seagrass Distribution* (project code CELASE) describes 70 listening stations and 250 internal fish tags, with FIU, NOAA, FWC, and Everglades National Park involvement. Project page: https://secoora.org/fact/projects/how-are-fish-using-florida-bay-impacts-and-effects-of-seagrass-distribution/.

A related Coastal Fisheries Research Lab / 3D Fish Telemetry project page, *How do Fish use Seascapes? (US)*, explicitly identifies the study species as:
- Spotted Seatrout (*Cynoscion nebulosus*)
- Goliath Grouper (*Epinephelus itajara*)
- Grey Snapper (*Lutjanus griseus*)

It describes two fine-scale acoustic telemetry arrays: one investigating spotted seatrout habitat use in patchy habitat, and one investigating juvenile habitat use by goliath grouper and grey snapper. It names the Coastal Fisheries Research Lab, Jonathan Rodemann, Jennifer Rehage, and Rolando Santos, and studies Florida Bay submerged aquatic vegetation and the seagrass die-off. This combination of matching personnel, geography, habitat question, and project framing strongly indicates that this is the species crosswalk for the CELASE Florida Bay work, although the two public pages use different project titles. Project page: https://telemetry.fish/project/florida_keys/.

**Finding:** the three species named above are supported as the targets of the related Florida Bay telemetry study. Southern Flounder is not named as a tagged target on that page. Therefore CELASE is currently habitat/movement-context evidence for the Florida Bay ecosystem, not a Southern Flounder telemetry occurrence source. Do not interpret its receiver count or project record count as evidence that Southern Flounder was tagged or detected.

The OTN public listing for CELASE/V2LCELASE exposes 100 station locations and 478 receiver deployments, but does not list a public Animal release product for this collection. The OTN catalog describes Animal products as tagged-animal release records including taxonomy and release metadata. Since no Animal product is listed for CELASE, the public catalog does not provide the species-level release file needed to independently enumerate all tagged individuals. OTN public listing: https://members.oceantrack.org/data/discovery/bypublic.htm.

#### South Carolina: Charleston Harbor / Ashley River acoustic telemetry

A 2016 Flatfish Biology Conference abstract, *Acoustic Tracking of Southern Flounder (Paralichthys lethostigma) in the Charleston Harbor System*, reports that 119 Southern Flounder larger than 275 mm total length were acoustically tagged and released into the Ashley River, Charleston, South Carolina. The study tested tag attachment methods, then monitored fish using fixed receivers and active tracking. Preliminary results reported 96% of tagged fish detected, 88% remaining within the river of release, and 12% moving into the Atlantic Ocean in fall months. Source: NOAA-hosted 11th Flatfish Biology Conference proceedings, https://repository.library.noaa.gov/view/noaa/12670/noaa_12670_DS1.pdf; also indexed in the 2016 conference abstract listing.

A later Gulf States Marine Fisheries Commission synthesis reports results for 118 acoustically tagged fish from the Ashley River study: 96% detected, 88% remaining within the release river, 12% entering the Atlantic in fall, and release-to-last-detection distances of 0–263 km, with movements greater than 100 km occurring only in December and January. The conference abstract's initial 119 tagged fish and later synthesis's 118 analyzed fish are preserved as source-specific counts; no explanation for the one-fish difference was found. Source: *Floundering Around*, GSMFC Number 310, https://www.gsmfc.org/publications/GSMFC%20Number%20310.pdf.

SCDNR's coastal receiver study describes a 120-receiver VR2W network spanning approximately 100 nautical miles of South Carolina coast, with Charleston arrays established in December 2013, southern coastal arrays expanded in April 2015, Port Royal Sound coverage from spring 2014, and additional St. Helena Sound coverage from summer 2016. Its other-finfish results describe Southern Flounder as one of the species detected in South Carolina and Georgia coastal waters; two-thirds of Southern Flounder detection days occurred within five miles of shore. The partnership listing names Frederick Scharf, Morgan Hart, and Steve Arnott for Southern Flounder. Sources:
- Methods: https://dnr.sc.gov/marine/receiverstudy/methods.html
- Results: https://www.dnr.sc.gov/marine/receiverstudy/finfish.html
- Researcher listing: https://www.dnr.sc.gov/marine/receiverstudy/partnerships.html

OTN's FACT catalog separately lists SCSOFL as a Southern Flounder tracking project associated with the South Carolina DNR institution, but shows Records=NA and LastModified=NA. This is a cataloged project lead, not an accessible event-level detection dataset. The matching species and research group make it a likely catalog representation of the South Carolina telemetry work, but an exact project-to-publication identifier crosswalk has not been independently verified.

#### North Carolina: 210-fish acoustic migration project

The North Carolina Southern Flounder Symposium page (March 20, 2024) summarizes an ECU-led acoustic telemetry study. Researchers captured and acoustically tagged 210 adult female Southern Flounder in Albemarle, Pamlico, and Core Sounds in fall 2020 and 2021. The 2022 NOAA Flatfish Biology Conference abstract reports that 85 of the 210 tagged fish had been detected at that time. Some fish moved offshore to the shelf break between January and March; others moved south along nearshore waters between Cape Lookout and Cape Fear. Seven fish showed potential skip-spawning behavior, eight returned to North Carolina sounds, and one made consecutive multiyear offshore migrations.

The 2024 symposium summary reports that some exploratory tagged fish moved south in later years as far as Georgetown and Charleston, South Carolina, and Savannah, Georgia. It separately reports that a hydrodynamic larval dispersal model suggested episodic connectivity with populations as far south as Florida. These are different evidence types:
- Adult telemetry detections documented southward movement to South Carolina and Georgia, not Florida.
- Florida connectivity is a model-based larval-dispersal inference, not a direct adult-tag detection or a verified Florida occurrence.
- The 2024 symposium page also summarizes five Southern Flounder eggs identified by DNA barcoding from offshore North Carolina collections; those eggs are North Carolina reproductive evidence, not Florida observations.

Sources:
- NC DEQ Southern Flounder Symposium, including the project summary and presentation abstracts: https://www.deq.nc.gov/about/divisions/marine-fisheries/hot-topics/flounder/southern-flounder-symposium
- NOAA 17th Flatfish Biology Conference 2022 proceedings, especially the McGarigal et al. abstract: https://repository.library.noaa.gov/view/noaa/48077/noaa_48077_DS1.pdf
- ECU 2024 dissertation by Brian Bartlett on modeled Southern Flounder spawning habitat near Beaufort Inlet, NC: https://thescholarship.ecu.edu/items/d3015a0c-fe38-4580-9df0-195eec3e578e

OTN's public catalog lists SOFLONC (ECU Southern Flounder Spawning Study) and SOFLOAR (Southern Flounder on Artificial Reefs), both associated with East Carolina University and Rebecca Asch, but both show Records=NA and LastModified=NA. Their exact relationship to the publications above, geographic coverage, and availability of underlying tag-level data remain unverified. They are research metadata leads, not acquired data.

#### Interpretation for LUPITA

These sources add credible Southern Flounder movement evidence from South Carolina and North Carolina and help frame migration variability, estuarine residency, offshore movement, and possible larval connectivity. They do **not** add a verified Southern Flounder telemetry detection in Florida Bay or elsewhere in South Florida. The Florida Bay CELASE work names other target species and should remain a separate ecosystem-context stream.

No telemetry raw data or individual tag detections were downloaded. No new South Florida locations were added. No occupancy inference, geographic mask, species profile, scoring, confidence, ingestion, production source, or publishing behavior changed.

### 2026-11-28 follow-up | Additional northern Gulf acoustic telemetry projects assessed

#### Galveston Bay Complex, Texas (2016–2018)

Steffen et al. (2023), *Estuarine-coastal connectivity and partial migration of southern flounder in the Gulf of Mexico*, provides a fully accessible peer-reviewed acoustic telemetry study. Sixty adult Southern Flounder were acoustically tagged in the Galveston Bay Complex from November 2016 to December 2017 and monitored by a 42-receiver array. The array recorded 370,918 detections from November 2016 through July 2018. Twenty-one fish were classified as migrators (maximum distance detected >5 km; mean 13.8 km), 11 as residents (<5 km; mean 0.6 km), 26 as unclassified due to short tracking duration, and two were never detected. Migrators generally moved through tidal passes in November–December, peaking in mid-to-late December; residents often remained in the bay through winter and spring. No tagged fish that exited the Galveston Bay Complex were detected returning to it during the study. Conventional tagging of more than 1,350 fish complemented the acoustic study; one conventional-tag recapture moved 221 km south to Espiritu Santo Bay, Texas, about three weeks after release. That conventional recapture is not an acoustic detection.

The study area is the upper Texas coast, not Florida. It supports Gulf estuarine/coastal movement and partial-migration context but does not document a Florida or South Florida detection. Source: https://www.tamug.edu/grihms/pdf/Steffen%20et%20al.%202023%20ECSS.pdf (DOI 10.1016/j.ecss.2023.108545).

#### Saint Louis Bay, Mississippi (2021 tagging; 2025 publication)

Chee, Graham, and Leaf (2025), *Development of a spatiotemporally integrated per-recruit model for Southern Flounder in the northern Gulf of America*, reports 80 Southern Flounder tagged with acoustic transmitters in Saint Louis Bay, Mississippi. The analysis classified 11 individuals as migrators moving to offshore spawning locations and 16 as residents overwintering in inshore habitats. The movement information was incorporated into a spatiotemporally integrated per-recruit model. The university repository abstract does not provide receiver-level detections, exact dates, or evidence of movement into Florida waters. This is northern Gulf movement evidence, not a Florida occurrence record. Source: https://aquila.usm.edu/fac_pubs/22320/ (Fisheries Research 288, August 2025; DOI 10.1016/j.fishres.2025.107444).

#### Mobile Bay / coastal Alabama acoustic monitoring

The Dauphin Island Sea Lab's Coastal Alabama Acoustic Monitoring Program (CAAMP) page states that the program was redesigned in 2019 to study Southern Flounder. Its stated objective is to determine female offshore migration during late fall/winter. The described array contains 68 acoustic receivers throughout Mobile Bay and its tidal rivers; fish are tagged in early fall and monitored through fall, winter, and spring. The page does not report the number of Southern Flounder tagged, event-level detections, study years with complete results, or any Florida detections. Treat this as a confirmed project and receiver-array design, not as an acquired occurrence dataset. Source: https://www.disl.edu/who-we-are/spowers/projects/caamp/.

A 2025 Alabama Department of Conservation and Natural Resources article describes a longer-running University of South Alabama / Alabama Marine Resources Division effort using conventional and acoustic tags, with tagging and tracking over approximately five years and Gulf coastal hydrophone arrays. The article discusses offshore residency and potential spawning-related movement but provides no Southern Flounder tag-level data or Florida detections. Source: https://www.outdooralabama.com/articles/research-inshore-species-yields-interesting-revelations.

#### Gulf telemetry synthesis

The Gulf studies now identified include Galveston Bay (60 acoustic-tagged fish, 2016–2018), Saint Louis Bay (80 tagged fish, 2021 tagging reported in a 2025 paper), and Mobile Bay (CAAMP project, 68-receiver array, redesigned for Southern Flounder in 2019). These studies provide useful Gulf-wide evidence that adult Southern Flounder can show both estuarine residency and offshore migration. They do not currently provide verified event-level Southern Flounder detections in Florida or South Florida. Do not extrapolate a Gulf-wide migration corridor from receiver arrays in Texas, Mississippi, and Alabama, and do not treat offshore egress as a Florida detection.

No raw telemetry detections or individual-tag files were downloaded. No Florida occurrence points were added. No occupancy inference, geographic mask, species profile, scoring, confidence, ingestion, production source, or publishing behavior changed.

