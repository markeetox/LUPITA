# NOAA WODSelect regional profile inventory plan | 2026-11-17

## Purpose

Obtain an auditable inventory of independent in-situ temperature profiles in the four exploratory Copernicus bottom-temperature regions. This is a discovery step, not a validation result. Do not report cast counts until WODSelect has actually returned them.

## Exact current candidate boxes

Use the same longitude/latitude bounds as `scripts/copernicus_bottom_temperature_pilot.py`:

| Region | West longitude | East longitude | South latitude | North latitude |
|---|---:|---:|---:|---:|
| South Florida / Keys | -81.0 | -79.5 | 24.5 | 26.5 |
| Gulf shelf reference | -89.0 | -87.5 | 29.0 | 30.0 |
| Atlantic shelf candidate v2 | -75.5 | -75.0 | 35.0 | 36.0 |
| Pacific shelf candidate v2 | -123.75 | -123.25 | 38.0 | 39.0 |

These are exploratory sample boxes based on the current Copernicus/ETOPO pilot. They are not yet accepted representative validation strata.

## WODSelect access and query sequence

- WODSelect: https://www.ncei.noaa.gov/access/world-ocean-database-select/dbsearch.html
- NCEI WOD overview: https://www.ncei.noaa.gov/products/world-ocean-database

Run one independent query per region. On the initial inventory pass:

1. Geographic Coordinates: enter the exact bounds from the table above.
2. Observation Dates: leave all years selected for the first historical inventory. Do not limit to the Copernicus forecast date; the reanalysis and regional CTD records are historical.
3. Dataset: first run the broad profile inventory with all profile datasets retained, then run a focused CTD/OSD subset if the interface permits. Do not silently exclude other profile types before their depth reach is known.
4. Measured Variables: Temperature.
5. Deepest Measurement: leave unrestricted on the first pass so shallow and deep profiles can be counted separately after retrieval. A second pass may use a documented depth threshold if needed.
6. Data Exclusion Using WOD Quality Control Flags: do not exclude records in the initial inventory. Preserve flags so the effects of later QC filtering can be reported rather than hidden.
7. Data Additions: use the current WOD23 released data default.
8. Build the query and record the returned cast count and distribution map for the region before requesting extraction.

For each regional extraction, prefer NetCDF ragged-array output with observed-level data. Preserve WOD quality flags and IQuOD flags/uncertainties if the interface allows both. If the output options require a choice between combined and separate instrument files, prefer separate instrument files for provenance and instrument-specific interpretation. Do not use standard-level-only data for the near-bottom comparison because interpolation to standard depths can obscure the actual deepest observed sample.

WODSelect's documented extraction workflow emails the requester when the data are ready and provides a link to the generated files. The extraction links are temporary; NOAA's documentation says files are removed from the FTP site after three days. Save the returned files and query settings promptly.

## Required inventory record per query

Record:
- query date/time and WOD release/version shown by the interface;
- region name and exact bounding coordinates;
- observation date range;
- selected datasets/instrument types;
- selected measured variables;
- deepest-measurement setting;
- QC exclusion setting;
- returned cast count;
- selected export format, observed/standard level option, flag types, and instrument-file grouping;
- extraction request identifier or email receipt date, without storing personal email in the repository;
- downloaded filenames and checksums once files are obtained.

## Follow-up profile screening

Do not equate cast count with eligible near-bottom observations. For every retrieved profile, retain source/cast identifiers, platform, cruise, date/time, position, measured depth or pressure, temperature variable and units, all available QC flags, and actual deepest valid sample.

Join profile location to ETOPO local seabed depth. Calculate and retain the signed/absolute vertical separation between the deepest valid temperature sample and local seabed. Keep this as a continuous value first; do not apply an arbitrary near-bottom cutoff until a threshold is predeclared and justified. Deduplicate WOD, GTSPP, GoMMAPPS, and other archive copies using platform/cruise, timestamp, location, and profile identity.

## GoMMAPPS accession 0243654 access findings

NOAA InPort confirms:
- CTD child record 66006 describes separate processed and unprocessed CTD folders;
- profiles are described as vertical temperature, salinity, and oxygen measurements to a maximum depth of 500 m;
- platform is NOAA Ship Gordon Gunter (ICES code 33GG);
- CTD-specific extent is 2017-06-29 through 2017-08-17, distinct from the broader parent survey extent 2017-07-03 through 2017-08-23.

The cataloged 23 KB Word item 65961 is titled “GU1703 NOAA SEFSC GoMMAPPS Additional Information and Data Dictionary,” but its metadata describes it only as additional project metadata provided by the collection team. Its contents have not been retrieved, so it must not yet be treated as a CTD column schema.

A separate 28 KB CSV dictionary item 66003 is explicitly distributed under the `NOAA_SEFSC_GoMMAPPS_GU1703_VisualSightingData` directory. It describes column-level metadata for that visual-sighting data table, not the CTD profiles. Do not use it to infer CTD field names or units.

The official NCEI archive/legacy NODC file URLs for the CTD directory, Word document, and sampling-location file returned cache-miss, redirect-loop, or inaccessible responses during this inspection. The OAS accession detail page is discoverable, but its live page timed out. No CTD filenames, file listing, cast count, CTD data columns, units, QC/scan flags, or near-bottom eligibility have therefore been verified. No parser should be written against assumed Sea-Bird CNV conventions.

Useful NOAA records:
- CTD child metadata: https://www.fisheries.noaa.gov/inport/item/66006
- Parent accession overview: https://www.ncei.noaa.gov/metadata/granule/geoportal/rest/metadata/item/GOMMAPPS.0243654/html
- Additional project metadata / Word document: https://www.fisheries.noaa.gov/inport/item/65961
- Visual-sighting dictionary (not CTD): https://www.fisheries.noaa.gov/inport/item/66003
- Sampling-location file metadata: https://www.fisheries.noaa.gov/inport/item/65963
- NCEI OAS accession detail: https://www.ncei.noaa.gov/archive/archive-management-system/OAS/bin/prd/jquery/accession/details/243654

## Immediate next action

Run the four WODSelect queries and capture the regional cast counts and query settings. Separately obtain the GoMMAPPS CTD directory listing, one processed profile plus header, and the investigator Word document through a working NOAA download path or NOAA contact. Once these source files are available, inspect their actual schema before writing any parser.

No independent observations have yet been accepted or paired. No bias, MAE, RMSE, matched-pair count, or model accuracy result is claimed. No production behavior changed.


## First regional WODSelect inventory: South Florida / Keys | 2026-11-17

WODSelect query completed at 2026-11-17 21:02:40 UTC (timestamp shown in the user's copied results). Query bounds: longitude -81.0000 to -79.5000; latitude 26.5000 to 24.5000. Selected datasets: OSD, CTD, XBT, MBT, PFL, DRB, MRB, APB, UOR, SUR, GLD. Required and extracted measured variable: Temperature. No observation-date restriction or deepest-measurement restriction is shown in the returned criteria. The copied criteria do not show the QC-exclusion setting or WOD release/version, so those remain unrecorded rather than assumed.

Returned WODSelect counts:

| Dataset | Casts |
|---|---:|
| OSD | 663 |
| CTD | 649 |
| XBT | 2,286 |
| MBT | 3,725 |
| PFL | 200 |
| DRB | 0 |
| MRB | 3 |
| APB | 0 |
| UOR | 0 |
| SUR | 0 cruises |
| GLD | 861 |
| **TOTAL** | **8,387 casts** |

This is a regional inventory count across selected WOD dataset types, not a count of unique, quality-screened, near-bottom observations. The instrument groups have different profile characteristics; actual profile depths, bottom separation, timestamps, position, QC, duplicate status, and eligibility must be assessed after extraction. Do not use 8,387 as the validation sample size.

Next: record the export options shown by WODSelect and request observed-level NetCDF with available QC/IQuOD flags retained, preferably separate instrument files. Preserve the query receipt and downloaded filenames/checksums. Continue with Gulf, Atlantic, and Pacific regional inventory queries using the exact bounds above. No profiles have yet been accepted or paired; no bias/MAE/RMSE or model-accuracy result is claimed. No production behavior changed.


## South Florida WOD extraction request submitted | 2026-11-17

WODSelect confirmed successful submission of the South Florida/Keys extraction request. NOAA states that generated files will be available in the WODSelect output directory for up to 72 hours after they are prepared, after which they are removed. Output location: https://www.ncei.noaa.gov/access/world-ocean-database-select/OCLdb_output

Submission confirmation is not evidence that files are ready or downloaded. Readiness time, file names, formats, export options actually applied, file sizes, and checksums remain pending. Next: check the output directory until the request is prepared, download all generated files within the 72-hour availability window, preserve the request/query receipt, and inspect file metadata/schema before writing any parser. Do not assume the selected output format or flag retention until verified from the actual files/receipt. No profiles have been screened or paired; no accuracy metrics are claimed. No production behavior changed.


## South Florida extraction file audit | 2026-11-17

Five user-uploaded gzip archives were inspected: GLD, MRB, PFL, MBT, and XBT. All decompressed fully and passed gzip integrity checks. Each contains 80-byte fixed-width ASCII records followed by CRLF. Cast-start counts exactly match the WODSelect inventory for those datasets: GLD 861, MRB 3, PFL 200, MBT 3,725, XBT 2,286; total 7,075. OSD (663) and CTD (649), 1,312 casts combined, were not among the five uploaded files. It is unknown whether WODSelect generated those files or they remain in the output directory.

The observed first byte of every cast-start line is `Q`. The WOD23 User Manual states that the first byte of WOD23/WOD18 native ASCII casts is `C` (with `B` for WOD09/WOD05 and `A` for WOD01). Because the WODSelect release/version and actual export setting were not recorded in the copied query criteria, the format and marker discrepancy are unresolved. Do not parse the files or assume WOD23 native format until the exact export setting/reader behavior is confirmed. NOAA references and all file sizes/checksums are in `docs/WOD_SOUTH_FLORIDA_EXTRACTION_AUDIT_2026-11-17.md`.

No cast metadata or profile measurements have yet been interpreted: date/time, coordinates, depth/pressure, temperature values/units, QC flags, deepest valid sample, seabed separation, and near-bottom eligibility remain unknown. No observation has been paired with Copernicus. Next: obtain OSD/CTD archives if generated; verify the export/version and `Q` marker using NOAA's documentation/sample reader; then parse while retaining all available QC/originator flags. No production behavior changed.
