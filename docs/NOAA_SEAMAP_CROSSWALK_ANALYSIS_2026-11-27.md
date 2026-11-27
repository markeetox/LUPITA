# NOAA DisMAP–SEAMAP original-record crosswalk

**Date:** 2026-11-27  
**Status:** read-only data audit complete; all 4,805 Gulf records independently crosswalked; ten NOAA SampleIDs contain a mismatched cruise-number segment  
**Target:** Southern flounder (*Paralichthys lethostigma*)  
**NOAA point extraction:** [workflow run 46019958931](https://github.com/markeetox/LUPITA/actions/runs/46019958931)  
**Related analysis:** [NOAA Southern flounder extraction analysis](NOAA_SOUTHERN_FLOUNDER_EXTRACTION_ANALYSIS_2026-11-27.md)

## Executive finding

The uploaded SEAMAP archives provide the original station, gear-deployment, and biological-catch tables needed to audit the NOAA DisMAP Gulf of Mexico point records.

All **4,805 NOAA Gulf SampleIDs** are now crosswalked to SEAMAP station/deployment records. For 4,795 records, the vessel-cruise-station composite key matches directly and year, exact depth, and tow midpoint independently agree. Ten additional records have a cruise-number discrepancy in the NOAA SampleID (`2001`) but independently match vessel 35, station numbers 12–18 and 20–22, and SEAMAP cruise `2101` in 2021. Those ten also agree on year, exact depth, and tow midpoint (maximum 61.7 meters). The discrepancy is isolated to the cruise-number segment; it does not invalidate the underlying station matches.

All **4,805 records** therefore have strong cross-source agreement:
- NOAA survey year matches the SEAMAP station start-date year.
- NOAA depth matches the SEAMAP start-station depth exactly.
- NOAA point coordinates match the midpoint of the SEAMAP tow start/end coordinates within 69.5 meters (median 27.8 meters; 99th percentile 61.3 meters).
- All 277 NOAA samples with WTCPUE > 0 have a corresponding Southern flounder biological record in SEAMAP.
- All 4,528 NOAA samples with WTCPUE = 0 have no Southern flounder biological record in the corrected SEAMAP station/deployment records. Every one of these 4,528 samples has biological records for other taxa, so the catch table is populated rather than simply absent.

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
4. SEAMAP gear-deployment records and biological catch records. For the ten cruise-component exceptions, the crosswalk was independently resolved using vessel, station number, survey year, exact depth, and tow midpoint, rather than accepting the malformed cruise component.

The documented relationship was followed: BGSREC was joined to INVREC by INVRECID, and station metadata was joined through the deployment's station/cruise identifiers. A station-only join was not used to assign biological records to gear deployments.

## Crosswalk results

### All 4,805 corroborated records

Of the 4,805 NOAA records, 4,795 match the vessel-cruise-station composite key directly. The remaining ten have the cruise-number segment discrepancy described below, but are independently matched to the correct 2021 cruise 2101 stations using vessel, station number, year, exact depth, and tow midpoint:
- 4,805 / 4,805 have matching calendar year between NOAA Year and the corrected SEAMAP START_DATE.
- 4,805 / 4,805 have exact depth agreement between NOAA Depth and SEAMAP DEPTH_SSTA.
- Tow-midpoint separation ranges from 0 to 0.0695 km; median 0.0278 km; maximum 0.0695 km.
- All 4,805 have at least one SEAMAP BGS biological record.

Within all 4,805 corrected station matches:

| NOAA WTCPUE result | Samples | Matching Southern flounder BGS record |
|---|---:|---|
| Positive (> 0) | 277 | 277 |
| Zero (= 0) | 4,528 | 0 |
| **Total** | **4,805** | **277 positive matches** |

All 277 positive NOAA samples match one Southern flounder BGS record under current biocode 183072404. The ten corrected cruise-2101 stations are zero-CPUE samples and have no Southern flounder BGS record; each has other-taxa biological records. The source-agency breakdown is:
- US / NMFS: 231
- Louisiana: 28
- Mississippi: 13
- Alabama: 3
- Florida: 2

All 4,528 corrected zero-CPUE samples have BGS records for other taxa but no Southern flounder BGS record. This is a much stronger sample-level no-catch check than relying on a missing NOAA target row alone.

### Ten NOAA SampleIDs with a mismatched cruise-number segment

Ten NOAA records carry SampleIDs beginning `035-2001-`, but the matching original SEAMAP records are vessel 35 / cruise `2101` (2021), not cruise `2001` (December 2020). The first crosswalk used the complete SampleID composite literally and therefore attached these records to the wrong 2020 cruise. The mismatch was resolved by searching the same vessel and station numbers and checking independent survey year, exact depth, and tow-midpoint position.

For all ten:
- NOAA Year is 2021 and SEAMAP START_DATE is June 3–4, 2021.
- NOAA depth matches SEAMAP DEPTH_SSTA exactly.
- NOAA coordinates match the SEAMAP tow midpoint within 18.5–61.7 meters.
- SEAMAP gear is ST shrimp trawl; recorded effort is 30 minutes; no operation code is present.
- Each has positive total live catch (3.3–33.6 kg) and 7–38 BGS rows for other taxa.
- None has a Southern flounder BGS row.

This resolves the biological and station crosswalk for all ten records. The NOAA SampleID cruise segment remains a source-quality discrepancy and should be reported as such; do not silently rewrite the source identifier. The corrected station mapping uses SEAMAP cruise 2101 and is supported by independent spatial, depth, year, gear, and catch evidence.

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

The 2001 SEAMAP Field Operations Manual says MINUTES FISHED is actual bottom time and documents a 55-minute maximum under that manual. A later SEDAR 87 data-workshop report (August 2024) says the SEAMAP design changed in 2008 to standardized 30-minute tows; NOAA InPort's current Groundfish and Shrimp Survey description also says 30 minutes. The single 56-minute record (SampleID 017-2401-00018, 2024) is one recorded tow (TOW_NO=1, one INVREC deployment); its recorded start/end timestamps span 56 minutes 21 seconds. It is outside the documented 30-minute standard and just beyond the old 55-minute maximum. Flag it for data-steward review, not automatic rejection.

One station has non-empty operation codes across its deployments: Sample 004-340-00043 has a 4-minute deployment with code M and a second 30-minute deployment without an operation code. The station comment documents a retow. The 4-minute deployment has zero total catch; the 30-minute retow has 3.9 kg total live catch. NOAA WTCPUE is zero and there is no Southern flounder BGS record. The ten corrected vessel-35 / cruise-2101 stations have no non-empty operation codes.

The manual defines B as gear bogged and M as miscellaneous, with details to be recorded in comments. It also says operation codes are entered only for unsuccessful or abnormal stations. No operation code means no abnormal operation was recorded in that field; it does not independently certify every tow as valid.

The STAREC HAULVALUE field is described in the uploaded data dictionary as a one-character haul-quality value. In the full archive it contains G (38,220 records), B (39), or null (23,721); within the 4,805 NOAA Gulf matches, 161 are G and 4,644 are null, with no B values. GSMFC's March 2010 SEAMAP Subcommittee minutes state that the field indicates whether a trawl was good or bad and that comments should explain the value. The 39 B records are consistent with a bad-tow flag: 36 have comments, many describing torn/lost gear, repeated tows, lost catch, or unrepresentative hauls, and two explicitly say “BAD TOW.” However, some G records also have comments describing serious gear/tow problems, including “TOW NOT REPRESENTATIVE” and lost/torn nets. The source dictionary still lacks the formal code list, so HAULVALUE must not be treated as a standalone validity gate; G is not accepted as proof that a tow was valid. The field is null for all 572 southern Gulf samples and all 73 shallow eastern samples discussed below.

## South of 26°N: stronger evidence for sampled no-catch

The 572 Gulf NOAA samples south of 26°N all have WTCPUE = 0. All 572 are within the 4,805 corrected crosswalk records:
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
- All 4,805 records are crosswalked to original station/deployment records; 4,795 match the composite key directly and ten are resolved through the independent vessel/station/year/depth/tow-midpoint fallback.
- All 277 positive NOAA WTCPUE samples have matching Southern flounder biological records.
- All 4,528 zero-CPUE samples have other biological catch records but no Southern flounder biological record.
- The 572 southern Gulf zero-CPUE samples, including the 73 shallow eastern samples, have matching effort and biological catch context.
- The ichthyoplankton archive contains one additional species-level northern Gulf specimen record.

Still unresolved:
1. Ask the NOAA/SEAMAP data steward why the ten 2021 NOAA SampleIDs encode cruise `2001` while the original station records identify cruise `2101`. The station crosswalk itself is resolved; the source identifier discrepancy remains.
2. Obtain the formal HAULVALUE codebook and ask the data steward how to interpret conflicting G-coded comments. Confirm whether the single 56-minute 2024 tow is a protocol exception, a recording issue, or an actual extended tow; current public sources describe a 30-minute standard, but do not explain this record.
3. Compare the survey evidence with Florida Museum voucher records and authoritative Florida estuary/coastal sources.
4. Keep bottom-trawl non-detections local to sampled tows. Do not generate an absence polygon, hard latitude cutoff, or estuary exclusion from these data.

## Sources

- Uploaded SEAMAPDATAV3CSV and SEAMAPDATAV3Access archives and their included March 2026 data dictionary.
- Uploaded SEAMAPPlanktonCSV archive and its ichthyoplankton database documentation.
- Uploaded SEAMAPBLCSV and SEAMAPBL archives and their Bottom Longline data dictionary.
- NOAA Fisheries, [SEAMAP Field Operations Manual for Collection of Data, October 2001 revision](https://sedarweb.org/documents/sedar-38-rd-15-seamap-gulf-of-mexico-field-operations-manual-for-collection-of-data/), especially the biological/trawling station instructions and Appendix 4 operation codes.
- NOAA Fisheries InPort, [Station Data, item 53364](https://www.fisheries.noaa.gov/inport/item/53364), for the station key, start/end coordinates, gear type, gear size, and fishing-time fields.
- NOAA Fisheries, [DisMAP Technical Report, June 2026](https://apps-st.fisheries.noaa.gov/dismap/docs/DisMAP_Tech_Report_06_2026.pdf).
- NOAA Fisheries, [Survey Catch-per-unit-effort CURRENT, InPort 69743](https://www.fisheries.noaa.gov/inport/item/69743).
- NOAA Fisheries, [Groundfish and Shrimp Survey, InPort 20890](https://www.fisheries.noaa.gov/inport/item/20890), for the current 30-minute survey description.
- SEDAR 87, [Gulf of Mexico White, Pink, and Brown Shrimp Data Workshop Report, August 2024](https://sedarweb.org/documents/sedar-87-gulf-of-mexico-white-pink-and-brown-shrimp-data-workshop-report/), section 4.4.1, for the 2008 change to standardized 30-minute tows.
- Gulf States Marine Fisheries Commission, [TCC SEAMAP Subcommittee Minutes, March 8, 2010](https://www.gsmfc.org/publications/minutes/2010/2010%20minutes.pdf), which describes the haul-value field as indicating whether a trawl was good or bad.

No raw archives or raw CSV records were committed. No species profile, geographic mask, scoring factor, weight, gate, confidence logic, ingestion, production source, or publishing behavior changed.
