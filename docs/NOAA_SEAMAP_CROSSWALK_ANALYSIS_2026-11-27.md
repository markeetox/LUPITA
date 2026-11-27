# NOAA DisMAP–SEAMAP original-record crosswalk

**Date:** 2026-11-27  
**Status:** read-only data audit complete; 10 identifier matches quarantined for unresolved record mismatch  
**Target:** Southern flounder (*Paralichthys lethostigma*)  
**NOAA point extraction:** [workflow run 46019958931](https://github.com/markeetox/LUPITA/actions/runs/46019958931)  
**Related analysis:** [NOAA Southern flounder extraction analysis](NOAA_SOUTHERN_FLOUNDER_EXTRACTION_ANALYSIS_2026-11-27.md)

## Executive finding

The uploaded SEAMAP archives provide the original station, gear-deployment, and biological-catch tables needed to audit the NOAA DisMAP Gulf of Mexico point records.

All **4,805 NOAA Gulf SampleIDs** have an identifier-level match to a SEAMAP station key using vessel, cruise number, and station number. Identifier matching alone is not sufficient: 10 records from one cruise fail independent date, depth, and tow-location checks and are quarantined.

The remaining **4,795 records** have strong cross-source agreement:
- NOAA survey year matches the SEAMAP station start-date year.
- NOAA depth matches the SEAMAP start-station depth exactly.
- NOAA point coordinates match the midpoint of the SEAMAP tow start/end coordinates within 69.5 meters (median 27.8 meters; 99th percentile 61.3 meters).
- All 277 NOAA samples with WTCPUE > 0 have a corresponding Southern flounder biological record in SEAMAP.
- All 4,518 NOAA samples with WTCPUE = 0 have no Southern flounder biological record in SEAMAP. Every one of these 4,518 samples has biological records for other taxa, so the catch table is populated rather than simply absent.

This is strong independent confirmation of sample-level no-catch records for the matched bottom-trawl samples. It is not evidence of absence from unsampled places or habitats.

## Input archives and provenance

The following uploaded archives were inspected. SHA-256 values are included so the exact input versions can be identified. The archives and raw CSV records were not committed to the repository.

| Archive | Contents / role | ZIP size | SHA-256 |
|---|---|---:|---|
| SEAMAPDATAV3CSV.zip | Parsed master trawl/station/biological database export | 113,562,965 bytes | 1c5c3b7512a5d514592888b19d4132635421f04c33462fb5b98f02ff538477b7 |
| SEAMAPDATAV3Access.zip | Access-format counterpart of the master database | 145,834,479 bytes | 82155b714ac536434b68ac17b2bc6d0101699aa9ef1247a678f194b4d8c7a577 |
| SEAMAPBLCSV.zip | Bottom Longline survey CSV export | 985,658 bytes | 230ecba31ed2d1d021357186886c902afa4ba425d6b2740366f42824a61dd6fc |
| SEAMAPBL.zip | Access-format Bottom Longline database | 1,425,956 bytes | fb12c8dcba47d78318370e26a40a85c5a5af8201be510f83c45dc85a10e9c173 |
| SEAMAPPlanktonCSV.zip | Ichthyoplankton, station, environmental and CTD CSV tables and documentation | 61,467,250 bytes | 34f14d24a9050f1d51a6a6534abedcea2915362440d5466da6a0ab7d304e2a26 |

The parsed SEAMAPDATAV3 CSV export contains 1,024 cruise records, 61,980 station records, 39,418 gear-deployment records, 907,661 biological general survey records, and 14,411 taxonomic biocode records. Its March 2026 data dictionary describes:
- STAREC as station/tow records, including start/end positions, dates, depths, and haul metadata.
- INVREC as one record per gear deployment, including gear type, mesh, minutes fished, operation code, and catch weights.
- BGSREC as one record per species per station/gear deployment.
- INVRECID as the link between BGSREC and the corresponding INVREC deployment.

The analysis used the CSV export and its included data dictionary. The Access-format counterpart was retained as a provenance input but was not independently queried.

## Crosswalk method

NOAA SampleID uses a vessel-cruise-station structure. For example:

- NOAA SampleID: 004-290-00072
- SEAMAP VESSEL: 04
- SEAMAP CRUISE_NO: 0290
- SEAMAP P_STA_NO: 00072

The crosswalk was built against the composite station key, then independently checked against:
1. NOAA Year versus SEAMAP START_DATE year.
2. NOAA Depth versus SEAMAP DEPTH_SSTA.
3. NOAA Latitude/Longitude versus the midpoint calculated from SEAMAP DECSLAT/DECSLON and DECELAT/DECELON.
4. SEAMAP gear-deployment records and biological catch records.

The documented relationship was followed: BGSREC was joined to INVREC by INVRECID, and station metadata was joined through the deployment's station/cruise identifiers. A station-only join was not used to assign biological records to gear deployments.

## Crosswalk results

### 4,795 corroborated records

Of the 4,805 identifier matches, 4,795 also agree on survey year, depth, and tow midpoint:
- 4,795 / 4,795 have matching calendar year between NOAA Year and SEAMAP START_DATE.
- 4,795 / 4,795 have exact depth agreement between NOAA Depth and SEAMAP DEPTH_SSTA.
- Tow-midpoint separation ranges from 0 to 0.0695 km; median 0.0278 km; 99th percentile 0.0613 km.
- All 4,795 have at least one SEAMAP BGS biological record.

Within this corroborated set:

| NOAA WTCPUE result | Samples | Matching Southern flounder BGS record |
|---|---:|---|
| Positive (> 0) | 277 | 277 |
| Zero (= 0) | 4,518 | 0 |
| **Total** | **4,795** | **277 positive matches** |

All 277 positive NOAA samples match one Southern flounder BGS record under current biocode 183072404. The source-agency breakdown is:
- US / NMFS: 231
- Louisiana: 28
- Mississippi: 13
- Alabama: 3
- Florida: 2

All 4,518 corroborated zero-CPUE samples have BGS records for other taxa but no Southern flounder BGS record. This is a much stronger sample-level no-catch check than relying on a missing NOAA target row alone.

### Ten unresolved identifier matches

Ten records match the composite key but fail the independent spatial/depth/date checks. All ten are NOAA Year 2021 records with SEAMAP station dates from 2020-12-09 through 2020-12-11, all use vessel 35 / cruise 2001, and all have NOAA WTCPUE = 0.

For these ten:
- NOAA points are 24.7–140.0 km from the midpoint of the matched SEAMAP start/end coordinates.
- NOAA depth differs from SEAMAP DEPTH_SSTA for every record.
- NOAA Year does not match the SEAMAP station date year.
- Two have Southern flounder BGS rows, but those rows have SAMPLE_BGS null/zero and SELECT_BGS positive (0.209 kg and 0.380 kg); counts are 1 and 2.
- One has no BGS records, zero total live catch, and operation code B (gear bogged).
- The remaining seven have other-taxa BGS records but no Southern flounder BGS row.

These records are excluded from the cross-source concordance calculation. The pattern is consistent with a reused identifier, source-version mismatch, or incorrect station linkage; the exact cause is unresolved. Do not treat the two target BGS rows as contradictions of the NOAA zero-CPUE result until the underlying 2020/2021 cruise records are reconciled.

SampleIDs in this exception group:
- 035-2001-00012
- 035-2001-00013
- 035-2001-00014
- 035-2001-00015
- 035-2001-00016
- 035-2001-00017
- 035-2001-00018
- 035-2001-00020
- 035-2001-00021
- 035-2001-00022

## Effort and tow-quality audit

All 4,805 NOAA Gulf SampleIDs have a matching STAREC station and at least one INVREC deployment. Every matched deployment is coded GEAR_TYPE = ST (shrimp trawl). There are 4,806 deployment rows because one station has two deployments; 4,804 stations have one deployment and one station has two.

For station-level effort using the longest recorded deployment:
- 4,559 stations report 30 minutes fished.
- 4,804 of 4,805 are between 20 and 40 minutes.
- One station reports 56 minutes.

The NOAA InPort Station Data metadata describes ST as shrimp trawl and states that gear size 40 represents a 42-foot trawl. The uploaded database records gear size 40 and mesh size 1.63 for the matched ST deployments.

The 2001 SEAMAP Field Operations Manual says MINUTES FISHED is actual bottom time and documents a 55-minute maximum for SEAMAP trawl stations. The single 56-minute record (SampleID 017-2401-00018, 2024) should be checked against the current survey protocol; it is flagged for review, not automatically rejected.

Two deployments have non-empty operation codes:
- Sample 004-340-00043 has a 4-minute deployment with code M and a second 30-minute deployment without an operation code. The station comment documents a retow. The 4-minute deployment has zero total catch; the 30-minute deployment has 3.9 kg total live catch. NOAA WTCPUE is zero and there is no Southern flounder BGS record.
- Sample 035-2001-00012 has code B, zero total live catch, and a station comment noting a mud tow. It belongs to the ten-record unresolved identifier group.

The manual defines B as gear bogged and M as miscellaneous, with details to be recorded in comments. It also says operation codes are entered only for unsuccessful or abnormal stations. No operation code means no abnormal operation was recorded in that field; it does not independently certify every tow as valid.

The STAREC HAULVALUE field is described in the uploaded data dictionary only as a one-character haul-quality value. It contains G for 161 of the 4,805 matched stations and is null for 4,644. No code list defining G was present in the uploaded dictionary, so HAULVALUE was not interpreted as a good/bad flag. It is null for all 572 southern Gulf samples and all 73 shallow eastern samples discussed below.

## South of 26°N: stronger evidence for sampled no-catch

The 572 Gulf NOAA samples south of 26°N all have WTCPUE = 0. All 572 are within the 4,795 corroborated crosswalk records:
- Exact depth agreement with SEAMAP.
- Tow-midpoint separation no greater than approximately 68 meters.
- All 572 have ST shrimp-trawl gear deployments.
- Recorded effort is 29–32 minutes (551 at 30 minutes).
- No non-empty operation code.
- Every station has other-species BGS records and positive total live catch.
- 307 of the 572 have positive finfish catch weight.
- None has a Southern flounder BGS record.

This confirms that these are not simply missing target rows or empty biological records. They are sampled bottom-trawl stations with recorded catch processing and no Southern flounder record.

### Shallow eastern subset near southwest Florida

Seventy-three of the 572 southern samples are in the easternmost slice (approximately 25.0031–25.9421°N and 81.9985–81.3310°W). They are 4.3–20.1 meters deep (median 13.2 meters).

All 73:
- Have WTCPUE = 0.
- Match the SEAMAP tow midpoint within approximately 68 meters.
- Have exact depth agreement.
- Have ST gear and 29–31 minutes fished (67 at 30 minutes).
- Have no non-empty operation code.
- Have other-species BGS records and positive total live catch; 41 have positive finfish catch.
- Have no Southern flounder BGS record.

This is meaningful shallow coastal/shelf bottom-trawl no-catch evidence. It is not estuary-wide coverage and does not establish absence in Florida Bay, tidal creeks, bays, or the Caloosahatchee.

## Ichthyoplankton archive: one species-level record

The uploaded SEAMAPPlanktonCSV archive contains one species-level Southern flounder ichthyoplankton record:
- Taxon: *Paralichthys lethostigma*.
- Original biocode: 183012404; current biocode: 183072404.
- Vessel 04, cruise 280, station 00080, sample 35258.
- Catalog number: SML365919-000.
- Date: 2008-02-22.
- Station position: 28°57.33′N, 89°33.16′W (approximately 28.9555, -89.5527).
- Station depth: 26 meters.
- One specimen recorded as measured; the matching length-frequency record reports 7.8 mm.
- LIFE_STAGE is blank, so no more specific life-stage label is assigned here.

The archive also contains 84 genus-level *Paralichthys* ISARWK records and 135 genus-level ILFRWK length records. Those genus-level records are not assigned to Southern flounder. The species-level record is a positive northern Gulf occurrence, not South Florida evidence and not a basis for a geographic mask.

## Bottom Longline archive

The separate SEAMAPBL archive is a Bottom Longline dataset. Its CSV export contains 70 cruises, 2,674 station records, and 46,439 individual catch records spanning 2007-09-26 through 2025-09-29. No *Paralichthys* or *P. lethostigma* catch records were found. This gear-specific absence is not evidence of Southern flounder absence and is not used to validate bottom-trawl zeros.

## Interpretation and next steps

Supported now:
- The NOAA Gulf SampleID structure can be crosswalked to original SEAMAP station and gear records.
- For 4,795 records, independent date, depth, and tow-midpoint checks strongly corroborate the identifier match.
- All 277 positive NOAA WTCPUE samples in that corroborated set have matching Southern flounder biological records.
- All 4,518 zero-CPUE samples in that set have other biological catch records but no Southern flounder biological record.
- The 572 southern Gulf zero-CPUE samples, including the 73 shallow eastern samples, have matching effort and biological catch context.
- The ichthyoplankton archive contains one additional species-level northern Gulf specimen record.

Still unresolved:
1. Reconcile the ten vessel-35 / cruise-2001 records with their 2020 SEAMAP station records and 2021 NOAA point-layer labels. Keep them excluded until the source mismatch is resolved.
2. Obtain the current codebook/metadata for HAULVALUE and confirm current survey rules for the one 56-minute record.
3. Compare the new survey evidence with Florida Museum voucher records and authoritative Florida estuary/coastal sources.
4. Keep bottom-trawl non-detections local to sampled tows. Do not generate an absence polygon, hard latitude cutoff, or estuary exclusion from these data.

## Sources

- Uploaded SEAMAPDATAV3CSV and SEAMAPDATAV3Access archives and their included March 2026 data dictionary.
- Uploaded SEAMAPPlanktonCSV archive and its ichthyoplankton database documentation.
- Uploaded SEAMAPBLCSV and SEAMAPBL archives and their Bottom Longline data dictionary.
- NOAA Fisheries, [SEAMAP Field Operations Manual for Collection of Data, October 2001 revision](https://sedarweb.org/documents/sedar-38-rd-15-seamap-gulf-of-mexico-field-operations-manual-for-collection-of-data/), especially the biological/trawling station instructions and Appendix 4 operation codes.
- NOAA Fisheries InPort, [Station Data, item 53364](https://www.fisheries.noaa.gov/inport/item/53364), for the station key, start/end coordinates, gear type, gear size, and fishing-time fields.
- NOAA Fisheries, [DisMAP Technical Report, June 2026](https://apps-st.fisheries.noaa.gov/dismap/docs/DisMAP_Tech_Report_06_2026.pdf).
- NOAA Fisheries, [Survey Catch-per-unit-effort CURRENT, InPort 69743](https://www.fisheries.noaa.gov/inport/item/69743).

No raw archives or raw CSV records were committed. No species profile, geographic mask, scoring factor, weight, gate, confidence logic, ingestion, production source, or publishing behavior changed.
