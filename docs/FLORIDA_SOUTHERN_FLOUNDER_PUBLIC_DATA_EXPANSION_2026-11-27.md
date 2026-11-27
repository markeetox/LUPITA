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
