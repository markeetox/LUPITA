# Copernicus bottom-temperature validation protocol

**Started:** 2026-11-17  
**Branch:** `main`  
**Status:** read-only extraction pilot completed; independent observation validation pending  
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

The workflow is manual-only, read-only, does not commit artifacts, does not run on a schedule, and does not change production ingestion or model behavior. It was dispatched on 2026-11-17 (run 44144656207) and passed. The uploaded artifact was downloaded and inspected; results and limitations are recorded below.


## Read-only subset pilot inspected | 2026-11-17

GitHub Actions run [44144656207](https://github.com/markeetox/LUPITA/actions/runs/44144656207) completed successfully on `main` (commit `1a45bab6bab75355b6e28f657679d7c953be0f79`). All eight subset requests and the artifact-upload step passed. Artifact: `copernicus-bottom-temperature-pilot` (8 NetCDF files plus `pilot-summary.json`).

### Extraction and data-file checks

- All eight files were present: four regions from forecast `tob` on 2026-11-17 and the same four from reanalysis `bottomT` on 2017-07-15.
- Each file contains the expected bottom-temperature variable and `time`, `latitude`, and `longitude` dimensions; no vertical depth axis is present.
- Decoded time coordinates match the requested dates (00:00 UTC): forecast 2026-11-17 and reanalysis 2017-07-15.
- Both variables use standard name `sea_water_potential_temperature_at_sea_floor` and units `degrees_C`.
- Forecast NetCDF values are stored as float32 with fill value approximately `9.96921e36`; reanalysis values are packed int16 with fill value `-32767`, `scale_factor=0.00073244`, and `add_offset=21`. The packed reanalysis values must be decoded before physical interpretation. After decoding and excluding fill values, the recomputed counts and statistics match the pilot JSON summary.
- No obvious out-of-range values were found in the decoded samples relative to the product metadata's broad valid ranges. This is a basic sanity check, not independent validation.

### Valid grid-cell counts

| Region | Forecast `tob` | Reanalysis `bottomT` |
|---|---:|---:|
| South Florida / Florida Keys | 321 / 475 (67.6%) | 321 / 475 (67.6%) |
| Gulf shelf | 325 / 325 (100%) | 325 / 325 (100%) |
| Atlantic shelf | 625 / 625 (100%) | 625 / 625 (100%) |
| Pacific West Coast | 132 / 625 (21.1%) | 132 / 625 (21.1%) |

These percentages are valid cells divided by all grid cells in each rectangular bounding box. They are **not ocean-only coverage rates**. Missing values may represent land masking, coastal geometry, or missing ocean data. The pilot does not include an independent wet-cell mask or bathymetric classification, so no claim about ocean-only coverage or coastal completeness is justified.

### Decoded sample ranges

| Region | Forecast 2026-11-17 min–max °C | Reanalysis 2017-07-15 min–max °C |
|---|---:|---:|
| South Florida / Keys | 5.75–27.70 | 5.28–30.89 |
| Gulf shelf | 4.07–26.20 | 4.02–30.18 |
| Atlantic shelf | 1.76–21.01 | 1.85–21.37 |
| Pacific West Coast | 2.16–18.79 | 2.15–18.36 |

The ranges are broad because each request covers a rectangular region with mixed depths and potentially offshore cells. The forecast and reanalysis samples are from different dates and different model products; their values must not be treated as a matched inter-product comparison or accuracy test. The low Atlantic means/ranges warrant spatial inspection against the actual bathymetry and station locations before interpreting them as shelf conditions.

### What this pilot establishes, and what it does not

Established: authentication, dataset access, dataset-specific variable identifiers, successful small-area extraction, coordinate/time decoding, fill-value handling, packed-value decoding, and basic numerical plausibility.

Not established: ocean-only valid coverage, nearshore completeness, operational freshness/update latency, forecast lead-time semantics beyond the returned daily timestamp, accuracy against observations, suitability for any species, or usefulness as a fishing-prediction factor.

Next: create a wet-cell/bathymetry-aware coverage assessment for the four boxes, then assemble quality-controlled independent CTD and mooring observations with documented near-bottom sample/sensor depth. Pair only time- and location-eligible observations and report regional bias/MAE/RMSE with sample counts. Keep the workflow manual-only and preserve the production change-control boundary.


## NOAA ETOPO ocean-mask and spatial-pattern assessment staged | 2026-11-17

The first pilot artifact was inspected directly. The Pacific valid cells form a west-side coastal/ocean pattern while missing cells dominate the eastern/southern portion of the rectangular box. This suggests the raw 21.1% all-grid valid fraction may be heavily affected by land masking, but that is not yet a measured ocean-only coverage result.

The Atlantic forecast and reanalysis samples both show a strong spatial gradient: most of the grid is approximately 1.8–3°C, while warmer values cluster along the western/southwestern edge. The similar pattern in both products makes a simple decoding error less likely. The rectangle may mix deep offshore water with shelf cells; depth classification is required before describing the sample as representative shelf temperature.

Added:
- `scripts/assess_copernicus_bottom_temperature_bathymetry.py`
- `.github/workflows/copernicus-bottom-temperature-bathymetry.yml`

The manual-only workflow reuses the existing pilot artifact by run ID; it does not re-download Copernicus data. It samples NOAA NCEI ETOPO 2022 30-arc-second global relief through the NOAA ERDDAP grid service, taking every tenth ETOPO cell to approximate the Copernicus 0.083333-degree grid. It validates grid dimensions and coordinate offsets before pairing cells. The per-cell outputs retain ETOPO elevation, estimated seafloor depth, bottom temperature, wet/land/ambiguous classification, and depth class.

Classification is deliberately conservative: ETOPO elevation above +1 m is land; below -1 m is ocean; the ±1 m band is coastal-ambiguous and excluded from the ocean-only denominator. Ocean cells are stratified into 0–10, 10–50, 50–200, 200–500, 500–2000, and >2000 m depth classes. The output reports ocean-only coverage and temperature statistics by depth class for forecast and reanalysis separately. This is a grid-mask diagnostic, not a navigation product or accuracy validation. ETOPO is a global relief model and nearshore values can be generalized; see NOAA's ETOPO documentation: https://www.ncei.noaa.gov/products/etopo-global-relief-model and the ERDDAP dataset metadata: https://oceanwatch.pifsc.noaa.gov/erddap/griddap/ETOPO_2022_v1_30s.html.

The workflow is manual-only, uses the existing artifact from run 44144656207 by default, produces a 14-day assessment artifact, and does not alter Copernicus data, MUR SST, production ingestion, species profiles, numeric bands, weights, gates, scoring, or publication behavior. It is staged but has not yet been dispatched. Next: run it, inspect ocean-only coverage and depth-stratified spatial patterns, then build the independent CTD/mooring inventory.

## Bathymetry workflow failure diagnosed and artifact-download fix committed | 2026-11-17

The first bathymetry assessment dispatch failed at step 4, before Python dependencies were installed or the assessment script ran. GitHub Actions log for run [44157956072](https://github.com/markeetox/LUPITA/actions/runs/44157956072) reports `Unable to download artifact(s): Bad credentials`. The log shows the `repository`, `run-id`, and `github-token` expressions were passed with literal leading backslashes (for example, `\${{ github.repository }}`), so GitHub Actions did not evaluate them. This was a workflow interpolation defect, not a NOAA response, grid-shape, or coordinate-alignment failure; the bathymetry script never executed.

Corrected the three expressions in `.github/workflows/copernicus-bottom-temperature-bathymetry.yml` and committed the fix. The source pilot artifact remains the same run 44144656207. The workflow is still manual-only and read-only. The corrected workflow has not yet been dispatched, so artifact access and the subsequent ETOPO parsing/alignment remain unverified. Next: rerun the workflow, inspect the first executed assessment step, then address any actual data/grid issue based on its logs.

## Bathymetry assessment completed and artifact inspected | 2026-11-17

The corrected manual workflow succeeded in run [44158655908](https://github.com/markeetox/LUPITA/actions/runs/44158655908). All seven steps passed, including cross-run artifact download, ETOPO assessment, and artifact upload. The generated artifact `copernicus-bottom-temperature-bathymetry-assessment` was downloaded and inspected; it contains one JSON summary and eight per-cell CSV grids.

Preliminary ocean-only coverage, using ETOPO elevation < -1 m as ocean and excluding the ±1 m coastal-ambiguous band:
- South Florida / Florida Keys: 302 ocean cells, 302 valid; 100%.
- Gulf sample: 323 ocean cells, 323 valid; 100%.
- Atlantic sample: 625 ocean cells, 625 valid; 100%.
- Pacific West Coast: 113 ocean cells, 98 valid; 86.7%.

This explains much of the Pacific's raw 21.1% valid/all-grid figure: 495 of 625 grid cells are classified as land, with 17 coastal-ambiguous cells. Fifteen of 113 ocean cells are missing temperature values. All 15 are in the 0–10 m depth class: 7/22 shallow ocean cells are valid (31.8%), while all sampled ocean cells in the 10–50, 50–200, 200–500, and 500–2000 m classes are valid. The sample box is therefore broadly covered offshore but has a notable very-shallow coastal gap.

The assessment also flags valid Copernicus temperatures at ETOPO-classified land points: 4 in the South Florida sample and 32 in the Pacific sample. These are excluded from ocean-only coverage. They may reflect coastal grid/land-mask resolution differences or model extrapolation; they are not silently counted as ocean. The ETOPO-to-model coordinate offsets are at most about 0.00417° in latitude and longitude, consistent with nearest sampled ETOPO grid centers at roughly half a model-cell spacing. This is a coarse screening mask, not a high-resolution shoreline validation.

Important sampling-design finding: the box labeled Atlantic shelf is not shelf-dominated. 572/625 cells (91.5%) are deeper than 2,000 m; only 26 cells are in the 10–200 m classes. Its all-cell mean near 2.86°C is therefore dominated by abyssal water and must not be interpreted as an Atlantic shelf temperature. The Gulf sample also includes substantial slope/deep-water area (37 cells >2,000 m and 186 cells at 500–2,000 m). The regional boxes need refinement/renaming before regional shelf statistics are used.

Forecast samples are dated 2026-11-17 and reanalysis samples 2017-07-15. They are separate product/date snapshots, not a matched forecast-vs-reanalysis comparison. Results establish preliminary data availability and depth context only; they do not establish accuracy, freshness, or suitability for species scoring. Next: inspect spatial patterns and revise the regional sampling boxes, especially the Atlantic shelf box; then inventory qualifying independent CTD and mooring observations. No production behavior changed.


## Spatial review and refined candidate sampling boxes | 2026-11-17

Inspected all eight per-cell CSV grids from bathymetry assessment run [44158655908](https://github.com/markeetox/LUPITA/actions/runs/44158655908), not only the aggregate JSON.

### Pacific shallow-gap diagnosis

The 15 missing ocean-classified cells are all 0–10 m deep and cluster at approximately 37.83–38.25°N, 121.42–122.08°W. Their coordinates lie in the Sacramento–San Joaquin Delta / upper San Francisco Bay estuarine system, not on the exposed Pacific continental shelf. The original `pacific_west_coast` rectangle therefore mixed open-coast, bay, delta, and land cells. Its 86.7% ocean-only coverage is not a defensible Pacific shelf coverage estimate.

The 32 valid temperature values at ETOPO-classified land points are concentrated around the San Francisco Bay/coastal grid transition, with several ETOPO elevations from only about 1–30 m and some higher terrain values. This points to a model-vs-bathymetry wet-mask/resolution disagreement that needs a local mask comparison; it does not establish that the Copernicus values are valid over land. Exclude these cells from ocean coverage pending resolution.

### South Florida mask disagreement

The four valid Copernicus cells classified as ETOPO land occur near 25.58°N, 80.33°W and 26.33–26.50°N, 80.08°W. ETOPO elevations are approximately 2.0–4.5 m. These are coastal-grid disagreements, not verified ocean observations. Keep them excluded from ocean-only coverage and inspect the local shoreline/mask before any later use.

### Revised exploratory boxes

Updated the pilot's four regional requests while retaining the South Florida reference box:

| Sample | Longitude | Latitude | Reason |
|---|---:|---:|---|
| South Florida / Keys | -81.0 to -79.5 | 24.5 to 26.5 | Retain as existing reference |
| Gulf shelf candidate | -89.0 to -87.5 | 29.0 to 30.0 | Shift north/east toward the northern Gulf shelf and away from the previous deep-water-heavy rectangle |
| Atlantic shelf candidate | -75.5 to -74.5 | 35.0 to 36.0 | Narrow around the shallow western edge of the previous box; verify depth mix before calling it shelf-representative |
| Pacific outer-shelf candidate | -124.5 to -123.5 | 37.0 to 39.0 | Move west of San Francisco Bay/Delta to sample exposed Pacific coast rather than estuarine cells |

These are hypotheses for a second coverage pass, not approved ecological boundaries. The next manual pilot will produce eight new subsets (four regions x forecast/reanalysis); the bathymetry workflow will classify them against ETOPO. Retain the original artifacts as the baseline rather than overwriting them.

### Guardrails and next step

The existing ETOPO classification is coarse (30-arc-second relief sampled at approximately the Copernicus grid spacing) and the ±1 m coast-ambiguous band is not a substitute for a high-resolution wet mask. No land-classified temperature is accepted as ocean data. No accuracy, freshness, or species relevance is inferred from these diagnostics.

Next: run the revised manual pilot, inspect the depth distribution and coastal-mask mismatches again, then select qualifying NOAA CTD/mooring profiles for independent matched validation. All work remains read-only; no production ingestion, MUR SST, species profiles, factors, weights, gates, scoring, confidence, or publication behavior changes.


## Workflow input correction | 2026-11-17

Bathymetry workflow run [44161453015](https://github.com/markeetox/LUPITA/actions/runs/44161453015) failed at the artifact-download step because the supplied `source_run_id` was the literal string `source_run_id`, not a numeric Actions run ID. The first-pass revised pilot itself succeeded as run [44160953510](https://github.com/markeetox/LUPITA/actions/runs/44160953510), and its artifact was produced successfully. No assessment code ran and no data was lost.

Updated the bathymetry workflow's default source run ID to `44160953510`, clarified the input description, and added a preflight numeric-ID validation step so placeholder text fails with a clear message before artifact download. This is a workflow usability fix only; assessment logic and production behavior are unchanged.


## Refined ETOPO bathymetry assessment | 2026-11-17

The revised read-only bathymetry assessment completed successfully in [run 44162223743](https://github.com/markeetox/LUPITA/actions/runs/44162223743), using the successful revised pilot artifact from run [44160953510](https://github.com/markeetox/LUPITA/actions/runs/44160953510). All workflow steps passed, including numeric source-run validation, artifact download, ETOPO classification, and artifact upload. Artifact: `copernicus-bottom-temperature-bathymetry-assessment` (9 files: summary JSON plus eight per-cell CSV grids).

Ocean-only coverage after excluding ETOPO land (>+1 m) and coast-ambiguous cells (-1 to +1 m):

| Region | ETOPO ocean cells | Forecast valid | Reanalysis valid | Coverage |
|---|---:|---:|---:|---:|
| South Florida / Keys | 302 | 302 | 302 | 100% |
| Gulf shelf candidate | 246 | 246 | 246 | 100% |
| Atlantic shelf candidate | 166 | 165 | 165 | 99.4% |
| Pacific outer-shelf candidate | 316 | 316 | 316 | 100% |

The revised rectangles substantially improve the test: the Gulf, Atlantic, and Pacific boxes now avoid the original estuary/land-dominated samples. However, 100% valid-cell coverage is not proof of accuracy or shelf representativeness. Depth composition matters:

- Gulf: 193/246 ocean cells (78.5%) are 10–200 m; 33 cells are 500–2000 m. This is the strongest current shelf-oriented candidate.
- Atlantic: 91/166 cells (54.8%) are 10–200 m; 38 are >2000 m and 29 are 500–2000 m. This is a mixed shelf-to-deep-ocean box, not a clean shelf-only sample.
- Pacific: 253/316 cells (80.1%) are >2000 m; only 22 are 50–500 m. Despite 100% ocean-only data coverage, this box is abyssal-dominated and must not be described as a representative outer-shelf sample.
- South Florida / Keys: 53/302 cells (17.5%) are 0–50 m, while 150/302 (49.7%) are 500–2000 m. This is a broad shelf/slope reference, not a shallow-coastal-only sample.

One Atlantic ocean-classified cell is missing temperature in both product subsets. All other ocean-classified cells are valid. The small number of Copernicus-valid/ETOPO-land disagreements remains visible in the per-cell CSVs and is not counted as ocean coverage.

Forecast subset date is 2026-11-17; reanalysis subset date is 2017-07-15. These are not matched dates and must not be compared as a controlled forecast-vs-reanalysis accuracy test. The current assessment establishes sampled-grid coverage and bathymetric context only. It does not validate temperature accuracy, freshness, or fish/species relevance.

### Next step

Refine the Atlantic and especially Pacific sampling geometry using the per-cell depth coordinates, aiming for explicit bathymetric strata rather than rectangular regions that accidentally include abyssal water. Keep Gulf as the best current shelf candidate and retain South Florida as a broad regional reference. Then build the independent NOAA CTD/mooring observation inventory and matched validation design. Continue to keep all work read-only: no production ingestion, MUR SST, species profiles, factors, weights, gates, scoring, confidence, or publication behavior changes.


## Candidate box refinement v2 | 2026-11-17

Inspected the successful assessment's per-cell CSVs rather than relying only on regional aggregate percentages. The prior Atlantic rectangle showed a strong west-to-east depth transition: its western longitudes are predominantly 10–200 m, while the eastern edge quickly transitions through 200–500 m into 500–2000 m and abyssal depths. The Pacific rectangle was overwhelmingly abyssal; the easternmost sampled longitudes and northern latitudes showed the only meaningful approach to the continental margin, but the existing rectangle did not extend far enough east to map a shelf-oriented sample.

Updated `scripts/copernicus_bottom_temperature_pilot.py` with two exploratory candidate v2 boxes:
- Atlantic: longitude -75.5 to -75.0°W, latitude 35.0 to 36.0°N (narrowed to the shallower western portion).
- Pacific: longitude -123.75 to -123.25°W, latitude 38.0 to 39.0°N (shifted east/north toward the continental margin).

These are sampling hypotheses, not validated shelf strata. The next manual pilot must be followed by the ETOPO bathymetry assessment. Land and coast-ambiguous cells must remain excluded from ocean coverage; depth composition, valid coverage, and mask disagreement must all be reviewed before accepting either box. Gulf and South Florida boxes remain unchanged. No production data or scoring behavior changed.


## Candidate v2 code check and next-run guard | 2026-11-17

Python tests passed on the candidate-v2 sampling-box commit in [run 44163056720](https://github.com/markeetox/LUPITA/actions/runs/44163056720). The pilot remains manual-only. The bathymetry workflow input no longer defaults to the older pilot run ID; it now requires an explicit numeric run ID from the newly completed candidate-v2 pilot. This prevents accidentally assessing the previous boxes. Next: dispatch the read-only pilot with the existing dates, then pass that new run ID to the bathymetry workflow. No production behavior changed.


## Candidate v2 Copernicus extraction completed | 2026-11-17

The candidate-v2 manual read-only pilot succeeded in [run 44164227216](https://github.com/markeetox/LUPITA/actions/runs/44164227216). All eight subset requests completed and the artifact `copernicus-bottom-temperature-pilot` was uploaded. The extracted forecast field is `tob` from dataset version `202406`; the historical reanalysis field is `bottomT` from version `202311`. Both expose the expected sea-floor potential-temperature standard name and `degrees_C` units, with time/latitude/longitude coordinates and no vertical depth axis.

| Region | Forecast valid / total | Reanalysis valid / total | Raw all-grid fraction |
|---|---:|---:|---:|
| South Florida / Keys | 321 / 475 | 321 / 475 | 67.6% |
| Gulf candidate | 247 / 247 | 247 / 247 | 100% |
| Atlantic candidate v2 | 90 / 91 | 90 / 91 | 98.9% |
| Pacific candidate v2 | 73 / 91 | 73 / 91 | 80.2% |

These are valid counts over each rectangular extraction grid. They are not ocean-only coverage rates: land and coast-ambiguous cells must be classified and excluded from the denominator. The improved raw Pacific fraction is encouraging as an extraction result, but it does not establish that the box is shelf-representative. ETOPO depth composition and coastal-mask disagreements remain unreviewed for candidate v2.

Forecast values are from 2026-11-17 and reanalysis values from 2017-07-15. The snapshots are not time-matched; differences between their ranges or means are not an accuracy or inter-product validation result. The pilot establishes successful access, extraction, metadata consistency, and basic numerical plausibility only.

Next: run `.github/workflows/copernicus-bottom-temperature-bathymetry.yml` with explicit `source_run_id=44164227216`; inspect ocean-only coverage, depth classes, and all per-cell mask disagreements before accepting or revising either candidate box. Continue the read-only boundary: no production ingestion, MUR SST, species profiles, factors, weights, gates, scoring, confidence, or publication behavior changes.


## Candidate v2 ETOPO assessment completed | 2026-11-17

The revised Copernicus pilot [44164227216](https://github.com/markeetox/LUPITA/actions/runs/44164227216) was classified against NOAA NCEI ETOPO 2022 in successful bathymetry assessment [44166772711](https://github.com/markeetox/LUPITA/actions/runs/44166772711). The artifact contains the JSON summary and eight forecast/reanalysis per-cell CSV grids. The assessment uses ETOPO elevation > +1 m as land, < -1 m as ocean, and -1 m through +1 m as coastal-ambiguous; ETOPO is a global relief model, not a navigation chart, and near-zero coastal cells remain ambiguous.

Ocean-only valid coverage:
- South Florida / Keys: 302/302 ocean cells (100%); 4 additional Copernicus-valid cells are ETOPO-land disagreements.
- Gulf shelf candidate: 246/246 (100%); no Copernicus-valid ETOPO-land cells.
- Atlantic shelf candidate v2: 87/88 (98.9%); no Copernicus-valid ETOPO-land cells. The single missing ocean cell is in the 0–10 m class; only 1 of 2 cells in that class is valid.
- Pacific shelf candidate v2: 65/65 (100%); 8 additional Copernicus-valid cells are ETOPO-land disagreements.

Depth composition (forecast/reanalysis share the same ETOPO classification):
- Gulf: 15 cells at 0–10 m, 121 at 10–50 m, 57 at 50–200 m, 20 at 200–500 m, and 33 at 500–2000 m. The 178/246 cells at 10–200 m (72.4%) make this the strongest broad shelf-oriented candidate.
- Atlantic v2: 2 cells at 0–10 m, 68 at 10–50 m, 10 at 50–200 m, 3 at 200–500 m, 3 at 500–2000 m, and 2 deeper than 2000 m. This is a focused shallow-shelf sample, but its inner-shelf class is tiny and one of its two 0–10 m cells is missing.
- Pacific v2: 4 cells at 10–50 m, 33 at 50–200 m, 10 at 200–500 m, 13 at 500–2000 m, and 5 deeper than 2000 m. The 43/65 cells at 50–500 m (66.2%) are useful for a shelf/slope transition sample, but the total is small and the eight land-mask disagreements need spatial review.
- South Florida / Keys: 46 cells at 0–10 m, 7 at 10–50 m, 34 at 50–200 m, 65 at 200–500 m, and 150 at 500–2000 m. Retain as a broad shelf/slope reference, not a shallow-coastal-only stratum.

The forecast sample date is 2026-11-17 and reanalysis sample date is 2017-07-15. They are not matched in time and must not be compared as a controlled product or accuracy test. These results establish subset extraction, ETOPO-classified wet-cell coverage, and bathymetric context only. They do not establish temperature accuracy, operational freshness, or species relevance. The Pacific and South Florida Copernicus-valid/ETOPO-land disagreements remain excluded from ocean coverage and require mask/resolution interpretation.

### Current disposition and next work

- Retain Gulf as the primary broad shelf validation candidate.
- Retain Atlantic v2 as a focused shallow-shelf candidate, while noting its small 0–10 m sample and one missing shallow cell.
- Retain Pacific v2 provisionally as a shelf/slope-transition candidate; inspect the eight land-mask disagreements before accepting the region.
- Retain South Florida / Keys as a broad shelf/slope reference.
- Proceed to an independent NOAA in-situ observation inventory. Prioritize NCEI World Ocean Database / GTSPP profiles and NOAA regional CTD archives; include moorings only where instrument depth is documented near the seabed. Surface-only buoy and underway thermosalinograph records are ineligible.
- Do not begin matched accuracy statistics until eligible observation records, near-bottom tolerances, spatial/time matching limits, QC rules, and duplicate handling are explicitly defined.

No production source configuration, MUR SST, species profiles, numerical factors, weights, gates, scoring, confidence, ingestion, or publication behavior changed.


## Independent observation inventory: source discovery | 2026-11-17

Initial source discovery was completed after the candidate-v2 ETOPO assessment. This is a metadata/source inventory only; no observation files have yet been downloaded, parsed, counted, or accepted as matched validation pairs.

### Primary profile archives

- **NOAA NCEI World Ocean Database (WOD23):** NCEI describes WOD as a quality-controlled global collection of ocean profiles. WOD23 contains more than 18.6 million casts and 3.13 billion profile measurements. WODSelect supports geographic coordinates, dates, dataset/probe type, measured variables, deepest measurement, ship/platform, cruise, accession, project, and QC-flag exclusion. It can deliver WOD native, CSV, or NetCDF. This is the primary discovery source for all four regions, but profile-level bottom proximity and local bathymetry must still be established.
  - Landing page: https://www.ncei.noaa.gov/products/world-ocean-database
  - WODSelect: https://www.ncei.noaa.gov/access/world-ocean-database-select/dbsearch.html
- **NOAA NCEI GTSPP:** The interface supports geographic and date filtering from 1990 to present. NCEI maintains a long-term best-copy archive that replaces lower-resolution real-time records with delayed-mode full-resolution shipboard CTD/XBT or quality-controlled source submissions. Prefer best-copy/delayed-mode data for retrospective validation; preserve platform and duplicate identifiers.
  - Landing page: https://www.ncei.noaa.gov/products/global-temperature-and-salinity-profile-programme
  - Data access documentation: https://www.nodc.noaa.gov/gtspp/access_data/index.html

### Strong regional candidate: GoMMAPPS GU1703 CTD

NOAA SEFSC/NCEI accession 0243654 provides processed and unprocessed CTD profiles from NOAA Ship Gordon Gunter's 2017 GoMMAPPS survey. The CTD record describes vertical temperature, salinity, and oxygen profiles to a maximum depth of 500 m. Metadata extent is 2017-06-29 through 2017-08-17 and approximately 23.823–29.955°N, 96.472–81.839°W. This geographically overlaps much of the Gulf candidate box and parts of the South Florida region. Its survey period also includes the reanalysis pilot date 2017-07-15, making it a particularly useful first archive to inspect for retrospective matching. It is not yet known how many casts have valid deepest levels near the seabed within our exact Copernicus grid cells; no sample count or validation coverage is claimed.
  - InPort CTD metadata: https://www.fisheries.noaa.gov/inport/item/66006
  - Direct NCEI CTD directory: https://www.ncei.noaa.gov/archive/accession/0243654/1.1/data/0-data/NOAA_SEFSC_GoMMAPPS_GU1703_CTD/NOAA_SEFSC_GoMMAPPS_GU1703_CTD/
  - Parent accession overview: https://www.ncei.noaa.gov/archive/accession/GOMMAPPS

### Regional coverage cautions

- **South Florida / Keys:** WOD/GTSPP and NOAA AOML CTD/mooring programs remain candidates. AOML underway thermosalinograph observations are surface measurements and are not eligible as bottom validation. Moorings require sensor depth and local bathymetry metadata.
- **Gulf:** GoMMAPPS GU1703 CTD is the first regional archive to inspect, followed by WOD/GTSPP. Its 500 m maximum profile depth means deep cells may have no near-bottom sample.
- **Atlantic:** WOD/GTSPP plus NOAA NEFSC near-bottom records may help, but NEFSC coverage is concentrated on the Northeast shelf and cannot be generalized to the entire Atlantic sample.
- **Pacific:** WOD/GTSPP and regional NOAA/state CTD or fisheries-survey profiles remain candidates. Actual station coverage, depth, QC, and near-bottom proximity must be demonstrated.

### Inventory implementation sequence

1. Obtain the GoMMAPPS processed and unprocessed CTD file listing and inspect its data dictionary/readme before choosing a representation. Avoid mixing processed and raw casts without a documented preference.
2. Parse cast-level metadata and profile measurements into a normalized, source-attributed inventory. Preserve original accession, cruise/platform, cast/station ID, timestamp, position, measured depth, temperature, units, and all available QC fields.
3. Obtain WODSelect/GTSPP regional subsets for the candidate boxes and broad historical windows. Request temperature profiles and retain the relevant quality flags and instrument/platform metadata.
4. Join casts to ETOPO local water depth and calculate deepest-valid-sample separation from the seabed. Keep the raw separation; apply no arbitrary near-bottom cutoff until it is specified and justified.
5. Detect duplicates across GoMMAPPS, WOD, GTSPP, and other agency copies using platform/cruise, timestamp, location, and profile identity.
6. Report inventory counts by region, source, year/season, platform, QC status, deepest sample depth, seabed separation, and Copernicus grid-cell matchability before calculating any error metric.

NCEI's WOD page currently warns that WODSelect is slow and that cloud migration/maintenance may delay data access. This is an access caveat, not a reason to substitute unverified data. The first concrete data-inspection target is the GoMMAPPS CTD directory and its processed-file metadata; WOD/GTSPP discovery follows once its exact subset workflow and output fields are confirmed.

No observations have been downloaded or paired yet. No bias, MAE, RMSE, matched sample count, or model accuracy result is claimed. No production behavior changed.
