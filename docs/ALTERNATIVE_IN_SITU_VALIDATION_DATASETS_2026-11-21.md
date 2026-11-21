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


## Priority reassessment after cruise-depth check | 2026-11-21

### Important correction: Nancy Foster accession 0283250 is not the primary shelf candidate

The cruise report for NF-22-06 documents CTD casts at approximately 1,043–1,862 m water depth (the listed cast depths are around 1,000–1,862 m). Although accession 0283250 has excellent documented originator variables (t090C ITS-90, prDM dbar, sal00, altM), this is a deep-water / deep-benthic dataset, not a suitable primary validation source for the current shelf-focused Copernicus candidate regions. Retain only as a possible deep-water reference. Sources: https://repository.library.noaa.gov/view/noaa/55612/noaa_55612_DS1.pdf and https://www.ncei.noaa.gov/metadata/granule/geoportal/rest/metadata/item/OMAO-CTD.0283250/html.

### New highest-priority candidate: NOAA Pulley Ridge / Dry Tortugas near-bottom moorings

- NCEI accession 0181331: Moored ADCP time series, 2012-08-15 to 2015-06-24. Data.gov catalogue description reports bottom-mounted upward-facing ADCPs at Northern Dry Tortugas, Southern Dry Tortugas and Pulley Ridge, hourly velocity and bottom-temperature measurements. Catalogue entry indicates 239 files: https://catalog.data.gov/?q=Loggers (search accession 0181331); NOAA project listing: https://products.coastalscience.noaa.gov/collections/regional/pulleyridge/.
- Independent peer-reviewed methods paper: https://www.sciencedirect.com/science/article/pii/S0079661117303385 and accessible NOAA-hosted PDF https://www.aoml.noaa.gov/phod/docs/Kourafalou_etal_POCEAN_2018.pdf.
- Paper states near-bottom temperature recorders were positioned 0.5 m above the seafloor at all three sites; bottom depths: Pulley Ridge 69.5 m, Northern Dry Tortugas 54.5 m, Southern Dry Tortugas 66.7 m. Time series: 34 months for Pulley Ridge and Northern Dry Tortugas, 27 months for Southern Dry Tortugas. This is unusually strong direct near-bottom evidence for bottomT validation, although it is a small fixed-site sample and old (2012–2015).
- Important: the published paper describes the near-bottom temperature recorders separately from the ADCP velocity bins. Confirm whether accession 0181331 includes the actual near-bottom temperature recorder series or only ADCP time series; inspect related accession 0190271 and source file manifests before coding. Do not assume all variables are in one archive.
- NOAA report for Pulley Ridge deployment 2013–2014 shows bottom temperature summary plot (mean 22.2°C, SD 2.0°C), but plot is not a substitute for raw time-series data: https://www.aoml.noaa.gov/ftp/pub/phod/rsmith/Pulley_Ridge/NCEI/mADCP/Pulley_Ridge_ADCP_02.pdf.
- The study sites lie near 24.47–24.77°N, 83.09–83.67°W and 54.5–69.5 m bottom depth. These are Southwest Florida Shelf / shelf-slope reef strata, not the existing Gulf/Atlantic/Pacific Copernicus pilot boxes. Extract matching Copernicus daily bottomT at exact site coordinates and dates if the sensor series can be obtained.

### Related NOAA Pulley Ridge datasets to inspect together

- Accession 0190533: CTD casts at mooring sites across Northern Dry Tortugas, Southern Dry Tortugas and Pulley Ridge, August 2013 and August 2014; includes conductivity, temperature, depth, salinity and oxygen. Metadata says raw data were processed with manufacturer standard routines, with details in each data-file header. Data.gov record reports accessLevel non-public while exposing an NCEI download URL, so access availability must be tested rather than assumed. https://catalog.data.gov/dataset/coral-ecosystem-connectivity-from-pulley-ridge-to-the-florida-keys-conductivity-temperatur.
- Accession 0190271: associated temperature logger time series, 2012-07-20 to 2014-08-13, for deep shelf (20–30 m) and shallow shelf (0–10 m) lower Florida Keys sites. This is valuable shallow-shelf temperature context, but it is not necessarily near-bottom. https://doi.org/10.25921/hhjr-bm33.
- Accession 0181331 is ADCP data; 0190271 is a distinct temperature time-series accession; 0190533 is CTD casts. Keep source roles separate and deduplicate where series overlap.

### Additional regional candidate: SEAMAP 2009–2015 CTD archive

- NCEI accession 0131259; 1,761 observations; Gulf of Mexico extent 24–31°N, 81–98°W; CTD casts from SEAMAP fishery-independent cruises, 2009-06-08 to 2015-07-16.
- InPort lists seven annual Oregon II cruise child datasets (2009–2015), a 27.984 MB tar.gz archive, sampling map and sampling-point documentation. This is a useful broad Gulf inventory candidate, with cruise-specific station coverage and fishery-independent survey context.
- It does not yet establish temperature scale, per-level QC, near-bottom distance, or processing details. Inspect raw files and their headers before qualifying it. Metadata: https://www.fisheries.noaa.gov/inport/item/67849 and archive landing: https://www.ncei.noaa.gov/archive/accession/0131259.

### Revised work order

1. Inspect NOAA Pulley Ridge/Dry Tortugas accessions 0181331, 0190271 and 0190533 together, starting with the direct near-bottom recorder series and file manifests. Confirm public file availability, exact sensor positions, logger depth above seabed, sampling interval, units, calibration and QC.
2. Extract Copernicus daily reanalysis bottomT for the three fixed mooring sites and exact observation dates. This provides a direct model-versus-measured-bottom-temperature pilot without needing to infer near-bottom status from a full water-column profile.
3. Inspect SEAMAP accession 0131259 for regional CTD coverage and possible additional near-bottom casts; only include casts with defensible bottom proximity.
4. Keep Nancy Foster 0283250 as a deep-water-only candidate, not the shelf pilot.
5. Preserve USF Sam as supplementary until its instrument provenance response arrives.

No files from these NOAA accessions have yet been retrieved or parsed in this reassessment. The published literature and metadata establish a promising candidate design, not validation results. No TEOS-10 conversion, Copernicus matchup, species-profile change, score/gate change, or production change has occurred.


## Archive role clarification and retrieval probe | 2026-11-21

Clarified the Pulley Ridge data roles from NOAA project records. Accession 0181331 is the moored ADCP time series and its description explicitly says hourly near-surface/near-bottom velocity and bottom temperature at Northern Dry Tortugas, Southern Dry Tortugas and Pulley Ridge. This is the direct fixed-site bottom-temperature candidate to prioritize. Accession 0190533 is CTD cast profiles at those mooring sites in August 2013 and 2014; raw data are manufacturer-standard processed and headers contain processing details. Accession 0190271 is a separate temperature-logger time series for shallow (0–10 m) and deep shelf (20–30 m) locations in the lower Florida Keys; it must not be described as the same 0.5 m-above-bottom mooring sensor series without checking metadata. The published near-bottom 0.5 m positioning applies to the specific near-bottom recorders discussed in the methods, while archive membership/variable content must be confirmed directly.

Added read-only discovery script scripts/probe_noaa_archive_access.py and manual workflow .github/workflows/noaa-archive-access-probe.yml. It probes NCEI landing/download endpoints and legacy NODC directory listings for 0181331, 0190271, 0190533 and SEAMAP 0131259, recording response status, redirects, content type, size and short previews. It does not download archive payloads. Workflow must be manually dispatched; no live probe has run yet. No NOAA data files have been retrieved, no Copernicus matchups or production changes.
