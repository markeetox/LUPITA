# NOAA GTSPP regional inventory plan | 2026-11-19

## Purpose

Continue the independent in-situ temperature-profile inventory while the WODSelect order/download service is degraded. GTSPP is a parallel NOAA archive and query route, not an automatic replacement for the user's exact WODSelect GLD extraction. Its records may overlap WOD and other archives, so station/cast identity and provenance must be retained and duplicates reconciled before any validation sample is counted.

## Official access and what is verified

- NCEI GTSPP product page: https://www.ncei.noaa.gov/products/global-temperature-and-salinity-profile-programme
- User-specified GTSPP query interface: https://www.ncei.noaa.gov/access/global-temperature-salinity-profile-programme/gwi.html
- Interface supports geographic bounding boxes, dates from 1990-01-01 to present, seasonal filters, data mode (Best Copy, Real Time, Delayed), data type selection, optional Argo exclusion, platform/call-sign filters, and products including diagnostics, station count, station DBID list, HTML retrieval, and downloadable data file.
- NCEI describes Best Copy as a curated archive in which lower-resolution real-time records can be replaced by delayed-mode, full-resolution shipboard XBT/CTD or fully processed quality-controlled submissions.
- NCEI's current access notice reports cloud-migration delays and intermittent degraded order fulfillment. The GTSPP query page was retrievable during reconnaissance, but this does not prove that a query or download will complete successfully.

## Regional boxes

Use the same candidate regions as the Copernicus/ETOPO pilot:

| Region | West | East | South | North |
|---|---:|---:|---:|---:|
| South Florida / Keys | -81.0 | -79.5 | 24.5 | 26.5 |
| Gulf shelf | -89.0 | -87.5 | 29.0 | 30.0 |
| Atlantic shelf | -75.5 | -75.0 | 35.0 | 36.0 |
| Pacific shelf | -123.75 | -123.25 | 38.0 | 39.0 |

## Query protocol

For each region, run a separate query and preserve the exact settings and returned receipt:

1. Enter the regional bounds above.
2. Leave date range at the full available GTSPP period (1990-01-01 to present) for the initial inventory. Record the actual end date displayed by the interface.
3. Select **Best Copy** as the initial mode. Do not combine Best Copy, Real Time, and Delayed in the first inventory because those modes can contain overlapping versions of the same station.
4. Leave the data-type selector blank for the initial broad inventory; the interface says blank optional fields use default parameters. Record the visible selector options for later instrument-specific splits, but do not guess which codes correspond to WOD instrument labels.
5. Leave **Exclude all Argo data** unchecked for the first broad inventory. If useful, run a separate Argo-excluded count as a sensitivity query rather than silently removing a source class.
6. Leave date fields blank for the initial full-period inventory; the interface states the GTSPP date range is 1990-01-01 to present. Record the actual end date shown when the query is submitted.
7. Request **Station count** first. If the result is tractable, request a DBID list and then the downloadable data file. The interface documents a maximum of 100,000 stations per selection.
8. Record query timestamp, bounds, date range, mode, data-type selector state (blank/default), Argo setting, output type, returned station count, receipt/DBID list, filenames, sizes, checksums, and any service errors.
9. Do not interpret station count as unique casts, temperature levels, QC-passing observations, or near-bottom eligible samples.

## Scientific screening after retrieval

For every profile, preserve source DBID and original identifiers, platform, cruise, timestamp, coordinates, instrument/type, temperature variable and units, depth/pressure and units, profile/level QC, and provenance. Determine whether values are in-situ temperature or potential temperature; do not assume thermodynamic equivalence with Copernicus potential temperature. Join coordinates to ETOPO bathymetry, retain negative bottom-separation values for investigation, and report continuous separation before any near-bottom sensitivity bands.

Deduplicate GTSPP against WOD, IQuOD, and the NOAA GoMMAPPS CTD accession using stable identifiers and source provenance. A record appearing in two archives is not two independent observations. Keep instrument classes separate where their depth accuracy, vertical resolution, and QC differ.

## Decision boundary

GTSPP is a candidate alternate acquisition path and a potentially useful supplementary archive. It is not yet accepted as an independent validation dataset. No regional counts have been retrieved, no profiles have been downloaded or screened, and no Copernicus pairs or error metrics exist from this plan.

No production source, species profile, numeric factor, weight, gate, scoring, confidence, ingestion, or publication behavior is changed by this research.


## Exact first query prepared | South Florida / Keys

The current NCEI form confirms that optional criteria may be left blank to use defaults, its date coverage begins 1990-01-01 and extends to present, and it exposes Best Copy / Real Time / Delayed modes plus Diagnostic / Station count / DBID list / HTML / Downloadable data products. For the first broad station inventory, use:

- North: 26.5
- West: -81.0
- East: -79.5
- South: 24.5
- Date begin/end: leave blank (full available period)
- Season: leave blank (Jan 01–Dec 31 default)
- Data mode: Best Copy only
- Data types: leave blank (default selection; do not guess codes)
- Exclude all Argo: unchecked
- Platform/call sign: blank
- Product: Station count only

The user must submit this form in a browser; the assistant's available web retrieval can inspect the form but cannot submit its interactive query. Capture the resulting count and any receipt/result text before proceeding to DBID list or data download. The form itself is at https://www.ncei.noaa.gov/access/global-temperature-salinity-profile-programme/gwi.html.

GTSPP Best Copy files are updated on or about the 7th of each month, per NCEI's access-data page. Record the release context; do not equate the catalog's update date with observation freshness.
