# Alternative in-situ temperature validation datasets | 2026-11-21

## Purpose

Identify independent observations with stronger published measurement provenance than the USF Sam 2024 Slocum glider product, for validating Copernicus modeled seafloor potential temperature. This is a source-screening assessment, not a validation result. No observations have yet been downloaded or paired from the candidates below.

## Candidate 1 — NOAA OMAO CTD archive, NOAA Ship Nancy Foster, 2022

- NCEI accession 0283250: https://www.ncei.noaa.gov/archive/accession/0283250
- Metadata: https://www.ncei.noaa.gov/metadata/granule/geoportal/rest/metadata/item/OMAO-CTD.0283250/html
- Cruise period: 2022-08-18 to 2022-08-27.
- Geographic extent: 27.11–28.93°N, 91.17–88.17°W.
- Platform: NOAA Ship Nancy Foster.
- Distribution format: Sea-Bird CTD, SBE 9.
- Metadata lists originator variables: t090C (ITS-90 temperature), prDM (Digiquartz pressure, dbar), sal00 (practical salinity), altM (altimeter), depSM (depth in salt water metres), plus bottom-depth and observation-depth fields.
- NCEI describes the distributed CTD suite as raw originator data, not a final processed reference product. Processing and QC must therefore be audited before use.
- Strong candidate for traceable temperature-scale/pressure provenance and near-bottom screening because altimeter and bottom-depth fields are available. Its geography is western Gulf, not the current Gulf candidate box, so it would represent a separate validation stratum unless Copernicus extraction is expanded.
- This is currently the strongest technical-provenance candidate identified, subject to raw file inspection and processing/QC review.

## Candidate 2 — NOAA SEFSC SEFIS CTD 2010–2024

- InPort metadata: https://www.fisheries.noaa.gov/inport/item/75595
- Archive CSV: https://www.ncei.noaa.gov/archive/accession/0172443/3.3/data/0-data/SEFIS_CTD_2010-2024.csv
- Metadata says archive is from 2025 and covers 2010–2024.
- Includes date, GMT start time, start latitude/longitude, depth, pressure, temperature, salinity, instrument and comments.
- Temperature is explicitly documented as ITS-90 °C.
- Pressure is documented in psi; depth in metres.
- Temperature, pressure and salinity values are averaged to 1-metre bins.
- This is attractive for regional coverage and a documented ITS-90 scale. Limitations: 1-metre binning, pressure conversion needed, only start position/time is described in the metadata, and the published schema does not expose per-observation QC flags or an explicit bottom-altimeter field.
- Metadata page marks this 2010–2024 record superseded, but identifies it as the archive from 2025. Check the InPort hierarchy for a newer replacement before treating it as the latest release.
- Candidate for broad regional inventory and near-bottom screening only after checking station/collection joins, instrument mix, comments, spatial/time precision and whether a newer release exists.

## Candidate 3 — NOAA SEFSC processed CTD cast archive / bottom-longline surveys

- CTD_PROC_CAST metadata: https://www.fisheries.noaa.gov/inport/item/31656
- Survey context: https://www.fisheries.noaa.gov/inport/item/28636
- Metadata describes standardized fisheries-independent bottom-longline surveys in the Gulf of Mexico and South Atlantic, annually since 1995.
- Processed CTD cast table includes depth, temperature, practical salinity, density and number of scans per bin. It links to station metadata through STATIONKEY.
- Potentially valuable because the surveys are bottom-oriented and spatially relevant to demersal habitat.
- The processed table metadata does not itself establish ITS-90, detailed QC, exact per-row timestamp/position, pressure or bottom clearance. Those must be recovered through linked station/cast tables and original processing documentation.
- Treat as a high-value discovery candidate, not yet a qualified reference dataset.

## Candidate 4 — Argo delayed-mode core profiles

- Argo file guide: https://argo.ucsd.edu/data/how-to-use-argo-files/
- Argo data FAQ: https://argo.ucsd.edu/data/data-faq/
- Highest-quality core profile selection is delayed-mode DATA_MODE='D', using TEMP_ADJUSTED, PRES_ADJUSTED and PSAL_ADJUSTED with each adjusted QC flag equal to '1' and retaining adjusted error fields.
- Argo documents expert delayed-mode review and salinity adjustment, with uncertainty estimates. This is a strong global quality-control framework.
- Limitation for this task: profiling floats generally sample open-ocean water columns and are not deliberately stationed over shallow shelf bottoms; their profiles may not reach the seabed and floats drift. Argo is useful as a regional water-column/thermodynamic cross-check where suitable profiles exist, but not the default near-bottom reference for coastal shelf validation.

## Candidate 5 — CCHDO / GO-SHIP shipboard CTD

- CCHDO data-submission and QA guidance: https://learning.cchdo.io/submitting_data/detailed_guide
- CCHDO requires clear units, encourages parameter-specific quality flags, and describes CTD data and WOCE flags. Its legacy CTD guidance explicitly asks temperature scale ITS-90 or IPTS-68 to be specified when known.
- GO-SHIP-quality CTDs can be highly traceable, but cruise coverage is sparse and generally open-ocean. Use when a cast is geographically/time appropriate and has near-bottom coverage; do not assume a GO-SHIP cast is near the seabed simply because it is a full-depth profile.

## Candidate ranking and recommended route

1. **First inspect NOAA Nancy Foster accession 0283250.** It exposes the most useful combination of explicit temperature scale, pressure variable, salinity, altimeter and bottom-depth fields, with a traceable SBE-9 raw archive. Audit the actual raw files, calibration/processing documentation, flags, station positions, and whether casts reach close to bottom.
2. **In parallel, inventory SEFIS 2010–2024.** It has explicit ITS-90 metadata and a broad regional survey record. Verify latest release, data rows, instrument mix, station linkage and near-bottom suitability.
3. **Investigate SEFSC CTD_PROC_CAST and its station/cast joins.** It may supply many bottom-oriented Gulf/South Atlantic observations, but its measurement provenance is not yet sufficient.
4. Keep **USF Sam glider** as supplementary high-density observations, pending provider response.
5. Use **Argo delayed-mode** and **CCHDO/GO-SHIP** as supplementary independent cross-checks where geographic, temporal and bottom-depth conditions fit.

## Mandatory qualification before any Copernicus error metric

For each candidate, inspect original variable names/units, temperature scale, pressure units, calibration/processing provenance, QC semantics, position/time provenance, bottom-depth or altimeter evidence, vertical reference, and source-level identifiers. Deduplicate overlapping archives. Convert in-situ temperature to potential temperature only after inputs are qualified. Pair only observations within a predeclared spatial/time window and report near-bottom sensitivity bands without choosing a cutoff to optimize agreement.

No data have yet been downloaded from these alternative candidates. No TEOS-10 conversion, Copernicus matchup, species-profile edit, scoring change, ingestion change or production change has been made.
