# Copernicus bottom-temperature validation protocol

**Started:** 2026-11-17  
**Branch:** `main`  
**Status:** source inventory and validation design; no Copernicus samples downloaded yet  
**Scope:** read-only research and validation only  
**Guardrail:** do not modify production source configuration, MUR SST, species profiles, numeric bands, weights, gates, scoring, confidence, ingestion, or publication behavior.

## Objective

Determine whether Copernicus Marine's global daily sea-bottom temperature field is sufficiently available, timely, and accurate across representative continental-shelf environments to justify a separate bottom-temperature input in a later design phase.

A global product extent is not evidence of valid coastal coverage or scientific accuracy. Validation must compare the gridded model field with independent in-situ observations and preserve the difference between the model's seafloor value and a sensor's actual measurement depth.

## Candidate product and variable

- Product: `GLOBAL_ANALYSISFORECAST_PHY_001_024`
- Dataset: `cmems_mod_glo_phy_anfc_0.083deg_P1D-m`
- Candidate physical field: sea-water potential temperature at the sea floor.
- Forecast variable: `tob`; reanalysis variable: `bottomT`. Both live catalogue records identify the standard name `sea_water_potential_temperature_at_sea_floor`, units `degrees_C`, and coordinates `time`, `latitude`, `longitude`. These identifiers are dataset-specific and must remain separate in extraction code.
- Horizontal resolution: 0.083° (approximately 8 km)
- Temporal resolution: daily mean
- Operational time coverage: rolling archive, with daily analysis/forecast updates and a 10-day forecast
- Historical companion: `GLOBAL_MULTIYEAR_PHY_001_030`, for retrospective analysis, not operational freshness.

Official references:
- Product services and dataset temporal extent: https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_PHY_001_024/services
- Product User Manual (daily `tob` definition): https://documentation.marine.copernicus.eu/PUM/CMEMS-GLO-PUM-001-024.pdf
- Product/dataset ID distinction and Toolbox access: https://help.marine.copernicus.eu/en/articles/4703373-differences-between-copernicus-marine-products-and-datasets-and-their-identifiers
- Subset options: https://help.marine.copernicus.eu/en/articles/7972861-copernicus-marine-toolbox-cli-subset

The operational product is a numerical ocean analysis/forecast, not an in-situ observation at every grid cell. Product documentation notes higher near-real-time uncertainty due to reduced observational availability. Do not treat a successful subset response as proof of local accuracy.

## Regional validation strata

The initial geographic sample must cover four separate regions and multiple shelf depths. Select Copernicus grid cells only after assembling independent observation records, so each model sample can be paired with an actual observation in space and time.

| Region | Initial independent-observation sources | Important limitation |
|---|---|---|
| South Florida / Florida Keys | NOAA AOML South Florida Coastal Ocean Program shipboard surveys and moored time series; NOAA SEFSC GoMMAPPS 2017 CTD archive; NCEI GTSPP | AOML's underway thermosalinograph is surface water. Only CTD profiles or moored sensors with documented depth near the seabed qualify as bottom observations. |
| Gulf of Mexico shelf | NOAA SEFSC GoMMAPPS CTD profiles; NCEI GTSPP; regional IOOS/COMPS records where the sensor depth is documented | A buoy's surface-temperature channel is not a bottom-temperature observation. Verify each station's instrument depth and variable metadata. |
| Atlantic shelf | NCEI GTSPP and NOAA CTD archives; NOAA NEFSC near-bottom observations where geographically applicable | The NEFSC bottom-temperature program is strongest from Cape Hatteras northward and cannot alone validate the South Atlantic shelf. |
| Pacific West Coast shelf | NCEI GTSPP and regional NOAA/state CTD or fisheries-survey profiles | Verify actual bottom proximity and avoid treating offshore Argo profiles or fish vertical-depth tags as seabed measurements. |

Source discovery:
- NOAA AOML South Florida Coastal Ocean Program data access: https://www.aoml.noaa.gov/phod/sfp/data/index.php
- AOML shipboard surveys: https://www.aoml.noaa.gov/phod/sfp/data/ship_obs.php
- AOML moored observations: https://www.aoml.noaa.gov/phod/sfp/data/moored_obs.php
- NOAA SEFSC CTD Data (NCEI accession 0243654; GoMMAPPS 2017; 2017-06-29 to 2017-08-17): https://www.fisheries.noaa.gov/inport/item/66006
- NOAA GTSPP global temperature/salinity profiles (1990-present interface and quality-controlled archive): https://www.ncei.noaa.gov/products/global-temperature-and-salinity-profile-programme
- NOAA NEFSC in-situ bottom-temperature documentation: https://noaa-edab.github.io/tech-doc/bottom_temp_insitu.html
- NOAA NEFSC bottom-temperature product metadata (Northeast shelf only; 1959-2020): https://www.fisheries.noaa.gov/inport/item/73770

### Observation eligibility

A record is eligible as an independent bottom-temperature comparison only when metadata establishes:
1. Position and observation timestamp.
2. Temperature value and units.
3. Sensor/sample depth.
4. Local water depth, or sufficient profile information to determine proximity to the seabed.
5. Quality-control flag or documented processing status.
6. Platform/instrument/source identity, to identify duplicates and correlated datasets.

For CTD profiles, use the deepest valid temperature observation only when it is within a defined near-bottom tolerance of measured bottom depth. Record the actual vertical separation; do not silently call a deep mid-water sample "bottom temperature." For moorings, use the documented sensor depth and bathymetry. Exclude surface-only sensors.

Potential duplicate CTD records across NCEI/GTSPP and agency archives must be detected using cruise/platform, timestamp, position, and profile identifiers before statistics are computed.

## Sampling and pairing design

1. Live catalogue metadata has now confirmed `tob` for the forecast dataset and `bottomT` for the reanalysis dataset. Their standard name, units, and horizontal/time coordinates agree.
2. Forecast catalogue time coordinates span 2022-06-01 through 2026-11-26; reanalysis spans 1993-01-01 through 2026-10-06. These are catalogue coordinate extrema, not a claim that all cells/dates contain valid values. The forecast endpoint extends into the forecast horizon; it must not be mistaken for the latest observed/analysis date.
3. The `geoseries` and `timeseries` services expose explicit coordinate metadata. The native-file and WMTS service records list variables but do not expose coordinate arrays in this response. Use a supported Toolbox subset path and inspect the returned file's actual dimensions and fill values.
4. Build regional observation inventories first. Pair each eligible observation to the nearest valid Copernicus wet grid cell, retaining horizontal separation and bathymetric mismatch.
5. Stratify results by region and shelf-depth class. Initial classes: inner shelf (10-50 m), middle shelf (50-200 m), and outer shelf (200-500 m). These are validation strata, not claims that every region has all classes.
6. Use time-matched daily means. Report observation-to-model time difference and reject pairs outside the predeclared tolerance; do not compare a CTD cast to an unrelated forecast day.
7. Report both all-valid coverage and observation-paired coverage. A global wet-cell fraction must not conceal missing nearshore shelf cells.
8. Keep South Florida shallow bays/reef flats separate from the open continental shelf. An 8 km model cell cannot resolve many local channels, reefs, or shallow flats.

## Metrics to report

### Coverage and freshness
- Requested grid cells, valid wet cells, and valid fraction by region/depth class.
- Number of eligible independent observations and matched pairs.
- Missing/land-masked cells, coastal gaps, and distance from each observation to matched model cell.
- Latest available model date, analysis/forecast designation, age at retrieval, and update delay.
- Time-axis continuity and missing-day frequency.

### Agreement
- Bias (model minus observation).
- Mean absolute error (MAE).
- Root mean square error (RMSE).
- Median absolute error and robust spread.
- Correlation only where sample size and temporal/spatial structure make it meaningful.
- Error by region, depth class, season, observation type, and model lead time.
- Sample counts and uncertainty intervals for every metric.

Do not combine regions into one headline accuracy score until regional sample balance and error structure are understood. Do not compare potential temperature and in-situ temperature as if identical without documenting the thermodynamic conversion/approximation; at typical shelf conditions the distinction may be small, but it must be assessed rather than assumed.

## Acceptance gates for a later design decision

No numeric pass threshold is approved yet. Establish sample sufficiency and regional representativeness before choosing error tolerances. A region with no qualifying observations is **unvalidated**, not passed.

A separate bottom-temperature factor can be proposed only if:
- the product returns valid values across useful shelf areas, not just offshore;
- nearshore and shallow-water mask gaps are quantified;
- freshness and forecast lead are explicit and operationally reproducible;
- enough independent bottom-near observations exist to estimate regional error;
- agreement is acceptable for the intended species/habitat use, with no hidden regional failure;
- the model/observation depth mismatch is controlled and reported.

Even a successful source validation would not validate existing species temperature ranges or preference curves. It would establish only that a physical bottom-temperature input is available with characterized quality. Species-specific response evidence and factor design remain separate work.

## Current findings and limits

- Live metadata retrieved on 2026-11-17 confirms the forecast daily dataset exposes `tob` and the reanalysis daily dataset exposes `bottomT`. Both use standard name `sea_water_potential_temperature_at_sea_floor` and units `degrees_C`; both are three-dimensional in `time`, `latitude`, and `longitude`, with no vertical depth coordinate for these bottom fields.
- The service catalog lists the daily dataset's operational temporal extent and daily availability.
- NOAA AOML provides relevant South Florida survey and mooring programs. Its survey description distinguishes underway surface thermosalinograph measurements from CTD casts; only qualifying near-bottom CTD/sensor records can validate the sea-floor temperature field.
- NOAA SEFSC's GoMMAPPS CTD archive provides an independent Gulf/Southeast profile collection from summer 2017, with a stated maximum profile depth of 500 m.
- NOAA GTSPP is the strongest initial global profile archive candidate for Atlantic and Pacific coverage; individual profile quality, depth, and bottom proximity still require filtering.
- NOAA NEFSC's near-bottom observations are useful for the northern Atlantic shelf but do not represent the entire Atlantic coast.
- The metadata-only workflow passed and its artifact was inspected on 2026-11-17. Forecast coordinate extrema are 2022-06-01 to 2026-11-26; reanalysis extrema are 1993-01-01 to 2026-10-06. No Copernicus temperature subset has yet been downloaded or sampled. No coverage fraction, freshness result, or model-vs-observation error statistic is claimed.

## Access prerequisite

Copernicus Marine Toolbox subsetting requires a free Copernicus Marine account and valid credentials. The Toolbox reads `COPERNICUSMARINE_SERVICE_USERNAME` and `COPERNICUSMARINE_SERVICE_PASSWORD` from environment variables or a local credentials file. Do not commit credentials, place them in workflow YAML, or paste them into repository files. If the pilot is run in GitHub Actions, use repository Actions secrets; if run locally, use environment variables. Official guidance: https://toolbox-docs.marine.copernicus.eu/en/stable/installation.html and https://help.marine.copernicus.eu/en/articles/8185007-copernicus-marine-toolbox-credentials-configuration.

## Next execution step

With credentials and live metadata now confirmed, a manual-only, read-only subset pilot has been added. It uses `tob` for forecast and `bottomT` for reanalysis, samples one date per dataset, and requests compact bounding boxes around four regional strata. Inspect actual returned variables, coordinates, fill-value semantics, wet-cell behavior, and data-file metadata. Then acquire and quality-filter matching independent profiles. Do not add a recurring workflow or production ingestion path at this stage.

## Change-control boundary

This protocol and source inventory are documentation only. No production configuration, source ingestion, species profiles, numerical factors, scoring, confidence, publication, or app behavior is changed.


## Credentials-check automation | 2026-11-17

Added `.github/workflows/copernicus-credentials-check.yml` as a manual-only GitHub Actions workflow (`workflow_dispatch`). It installs the Copernicus Marine Toolbox 2.4.0, reads the two repository Actions secrets through environment variables, checks that both are present without printing their values, and runs `copernicusmarine login --check-credentials-valid`. It does not download data, write repository files, publish exports, or run on a schedule.

The workflow was dispatched on 2026-11-17 and passed, confirming that the configured repository secrets authenticate successfully. It remains manual-only and does not download data.


## Metadata-first correction | 2026-11-17

Before downloading samples, variable naming was rechecked against current Copernicus documentation. Copernicus explicitly documents `bottomT` as sea-water potential temperature at the sea floor and states that it is independent of the vertical depth coordinate. The earlier protocol's `tob` identifier is therefore provisional, not assumed correct for both products. Live dataset metadata must decide the exact short name and dimensions for forecast and reanalysis separately.

Added the manual-only workflow `.github/workflows/copernicus-bottom-temperature-metadata.yml` to retrieve complete live metadata JSON for the daily forecast and reanalysis dataset IDs and upload the files as a seven-day artifact. This is metadata-only: no temperature data is downloaded and no production behavior changes. The workflow has been committed but not yet run.


## Live metadata inspection completed | 2026-11-17

The manual workflow `.github/workflows/copernicus-bottom-temperature-metadata.yml` passed. Its artifact contained valid catalogue JSON for both requested datasets.

| Dataset | Version | Bottom-temperature variable | Standard name | Units | Catalogue time-coordinate extrema |
|---|---|---|---|---|---|
| `cmems_mod_glo_phy_anfc_0.083deg_P1D-m` | `202406` | `tob` | `sea_water_potential_temperature_at_sea_floor` | `degrees_C` | 2022-06-01 to 2026-11-26 |
| `cmems_mod_glo_phy_my_0.083deg_P1D-m` | `202311` | `bottomT` | `sea_water_potential_temperature_at_sea_floor` | `degrees_C` | 1993-01-01 to 2026-10-06 |

Both bottom fields expose `time`, `latitude`, and `longitude` coordinates, with no vertical depth coordinate. The horizontal increment is approximately 0.0833333 degrees. The catalogue reports global coordinate bounds, which do not establish valid coastal coverage or non-missing values.

The forecast catalogue maximum is a future forecast-horizon coordinate and must not be reported as the latest observation/analysis time. Actual per-cell validity, fill values, and the analysis-versus-forecast time semantics remain to be checked in subset output. The reanalysis time maximum is the catalogue coordinate endpoint, not a measured freshness result.

The metadata artifact also lists `geoseries` and `timeseries` Zarr services with explicit coordinate metadata; native-file and WMTS entries list variables but no coordinate arrays in this response. No temperature samples were downloaded. No model, species, scoring, ingestion, or publication behavior changed.


## Read-only subset pilot staged | 2026-11-17

Added `scripts/copernicus_bottom_temperature_pilot.py` and manual-only workflow `.github/workflows/copernicus-bottom-temperature-pilot.yml`.

The workflow performs eight small requests: four regional boxes from the forecast dataset using `tob` for the selected forecast date, and the same four boxes from reanalysis using `bottomT` for the selected historical date. Defaults are 2026-11-17 (forecast) and 2017-07-15 (reanalysis); both are editable workflow inputs and must remain within the corresponding dataset's live time extent. Dataset versions are pinned to the exact catalogue versions inspected (`202406` and `202311`). No depth range is supplied because the confirmed bottom fields have no vertical depth coordinate.

Regions: South Florida/Florida Keys, Gulf shelf, Atlantic shelf, and Pacific West Coast shelf. The script writes the NetCDF subsets and a JSON summary containing dimensions, coordinate extents, valid/missing counts, valid fraction, value range, units/standard name, fill-value encoding, and available global metadata. This is a coverage/structure smoke test only, not a model-accuracy comparison. The bounding boxes are broad sampling windows, not approved ecological regions or observation-matched stations.

The workflow is manual-only, read-only, does not commit artifacts, does not run on a schedule, and does not change production ingestion or model behavior. It has been committed but **has not yet been dispatched**. After it passes, inspect the artifact before making any coverage or quality claims.
