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
- Variable: `tob`
- Standard name: `sea_water_potential_temperature_at_sea_floor`
- Units: °C
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

1. Query the daily `tob` dataset for a recent operational window and, separately, historical dates overlapping independent observations.
2. Inspect returned metadata before interpreting values: variable name, units, coordinate names, time axis, grid spacing, fill values, and product/version.
3. Build regional observation inventories first. Pair each eligible observation to the nearest valid Copernicus wet grid cell, retaining horizontal separation and bathymetric mismatch.
4. Stratify results by region and shelf-depth class. Initial classes: inner shelf (10-50 m), middle shelf (50-200 m), and outer shelf (200-500 m). These are validation strata, not claims that every region has all classes.
5. Use time-matched daily means. Report observation-to-model time difference and reject pairs outside the predeclared tolerance; do not compare a CTD cast to an unrelated forecast day.
6. Report both all-valid coverage and observation-paired coverage. A global wet-cell fraction must not conceal missing nearshore shelf cells.
7. Keep South Florida shallow bays/reef flats separate from the open continental shelf. An 8 km model cell cannot resolve many local channels, reefs, or shallow flats.

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

- The Copernicus catalog and PUM confirm that the daily dataset contains `tob`, defined as sea-bottom potential temperature in °C.
- The service catalog lists the daily dataset's operational temporal extent and daily availability.
- NOAA AOML provides relevant South Florida survey and mooring programs. Its survey description distinguishes underway surface thermosalinograph measurements from CTD casts; only qualifying near-bottom CTD/sensor records can validate `tob`.
- NOAA SEFSC's GoMMAPPS CTD archive provides an independent Gulf/Southeast profile collection from summer 2017, with a stated maximum profile depth of 500 m.
- NOAA GTSPP is the strongest initial global profile archive candidate for Atlantic and Pacific coverage; individual profile quality, depth, and bottom proximity still require filtering.
- NOAA NEFSC's near-bottom observations are useful for the northern Atlantic shelf but do not represent the entire Atlantic coast.
- No Copernicus subset has yet been downloaded or sampled in this phase. No coverage fraction, freshness result, or model-vs-observation error statistic is claimed.

## Next execution step

Run a small, read-only pilot extraction of `tob` for one recent date and one historical date, using compact bounding boxes around the four regional observation inventories. Confirm authentication/access method, actual response variables and coordinates, fill-value semantics, and wet-cell behavior. Then acquire and quality-filter matching independent profiles. Do not add a recurring workflow or production ingestion path at this stage.

## Change-control boundary

This protocol and source inventory are documentation only. No production configuration, source ingestion, species profiles, numerical factors, scoring, confidence, publication, or app behavior is changed.
