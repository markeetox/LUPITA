# IOOS Glider DAC regional profile inventory plan | 2026-11-19

## Why this route

NCEI's GTSPP interactive query returned Service Unavailable to the user on 2026-11-19. NCEI's public service status currently reports intermittent degraded order fulfillment during cloud migration and warns that many access portals and data folders are unavailable. Do not keep retrying GTSPP or WODSelect while this service condition persists.

The IOOS National Glider Data Assembly Center (NGDAC) is a separate public distribution path for underwater-glider observations. The DAC publishes trajectory/profile datasets through ERDDAP and THREDDS; it includes historical missions dating to 2005 and contributions from NOAA AOML, universities, and regional IOOS associations. This is not a replacement for WOD as a whole: glider observations are a subset of platforms and can be spatially/temporally clustered.

Official entry points:
- IOOS Glider DAC: https://gliders.ioos.us/
- ERDDAP catalog: https://gliders.ioos.us/erddap/info/index.html
- THREDDS catalog: https://gliders.ioos.us/thredds/catalog.html
- NGDAC documentation: https://ioos.github.io/glider-dac/
- IOOS data access overview: https://ioos.noaa.gov/data/access-ioos-data/

## Initial verified candidate: USF Sam deployment

The NGDAC catalog exposes dataset `usf-sam-20240216T0000`, a University of South Florida / GCOOS Slocum-glider deployment.

Verified metadata:
- Time coverage: 2024-02-16T16:25:06Z to 2024-03-15T10:51:35Z.
- Geographic bounds: 27.5879888–28.0393764°N, -84.5671611 to -83.1217124°E.
- Maximum recorded depth: 140.6833 m; minimum: 0.5761 m.
- Instrument: CTD.
- Data structure: trajectory-profile.
- Dataset carries profile identifiers, WMO ID 4801942, CTD depth/pressure, and QARTOD temperature/pressure flags.
- Temperature variable `temperature`: measured by the CTD, Celsius; metadata reports accuracy 0.004°C, precision/resolution 0.001°C, and observed dataset range 16.8621–21.7797°C.
- Depth variable `depth`: positive down in metres, alias for `m_depth`, calculated from the CTD source sensor, sea-surface reference datum; metadata reports accuracy 0.01 m.
- Pressure variable `pressure`: measured, positive down, sea-surface reference datum, units bar; comment says alias for `sci_water_pressure`, multiplied by 10 to convert from bar to dbar. Preserve original units and document any conversion.
- Point-level coordinates/time are `precise_lat`, `precise_lon`, and `precise_time`; metadata describes them as interpolated at each point in the time series, not direct raw GPS/time observations. Profile-level `latitude`, `longitude`, and `time` are also calculated/interpolated to the profile midpoint.
- Temperature QARTOD variables include flat-line, gross-range, rate-of-change, spike, and primary flags. The primary flag's metadata range is 1–4, and its flag values mean 1=PASS, 2=NOT_EVALUATED, 3=SUSPECT, 4=FAIL, 9=MISSING. The actual distribution/counts per flag have not yet been retrieved.
- Regional association: GCOOS-RA; sea area: Gulf of Mexico.
- Dataset is marked as completed in the DAC, but its license/metadata warns data are provided as-is without an implied QA/QC assurance. Apply the supplied QC flags rather than assuming all observations pass.

This deployment is geographically outside the existing Gulf Copernicus candidate box (-89.0 to -87.5°W, 29.0 to 30.0°N). It is therefore a candidate for a **separate West Florida shelf/slope validation stratum**, not a match to the existing Gulf pilot. Its maximum depth does not establish near-bottom coverage; ETOPO separation must be calculated for individual profiles.

Dataset references:
- NGDAC metadata: https://gliders.ioos.us/erddap/info/usf-sam-20240216T0000/index.html
- ERDDAP data form: https://gliders.ioos.us/erddap/tabledap/usf-sam-20240216T0000.html
- Aggregated USF quarterly listing: https://erddap.aoml.noaa.gov/hdb/erddap/tabledap/GLIDERS_2024_01_03.subset

## Screening protocol

1. Search the NGDAC ERDDAP catalog and deployment metadata for profiles whose actual coordinate bounds intersect the four existing candidate boxes. Do not select deployments based only on broad global bounding boxes.
2. Preserve deployment ID, WMO ID, profile ID, profile time, point-level `precise_time`/`precise_lat`/`precise_lon`, depth, pressure, temperature, units, sensor/instrument metadata, all QARTOD flags, and original provenance.
3. Treat profile position/time fields separately from point-level fields. Both profile-level and point-level position/time metadata are described as calculated/interpolated; do not label them as direct raw observations. Preserve both where available.
4. Apply the documented QARTOD flag meanings. Keep PASS, NOT_EVALUATED, SUSPECT, FAIL, and MISSING distinct; do not silently treat NOT_EVALUATED as PASS.
5. Join each observation to ETOPO and calculate continuous bottom separation. Keep negative separation visible. No near-bottom cutoff is chosen yet.
6. Compare actual glider observation timestamps and locations with Copernicus analysis/forecast fields. The glider's temperature is measured in-situ; Copernicus bottomT/tob is sea-floor potential temperature. Thermodynamic comparability and time/space interpolation uncertainty must be resolved before residual metrics.
7. Deduplicate against WOD/GTSPP/other glider archives by deployment, WMO, profile, time, and position where possible. A profile mirrored in multiple archives is one observation.

## Current status and boundaries

- NCEI GTSPP query returned Service Unavailable; no station count was obtained.
- IOOS NGDAC/ERDDAP catalog and individual deployment metadata are discoverable. One Gulf of Mexico USF Sam deployment has been verified from metadata.
- Dataset variable metadata has been inspected. The temperature is measured; depth is calculated from the CTD depth sensor; pressure is measured in bar; point-level precise position/time are interpolated. QARTOD temperature primary flags span 1–4 in metadata, but actual per-flag observation counts have not yet been retrieved.
- No glider profile data have yet been downloaded, ETOPO-joined, or paired to Copernicus.
- The USF Sam deployment is outside the current Gulf pilot box and is not yet accepted as near-bottom eligible.
- No validation sample size, bias, MAE, RMSE, or Copernicus accuracy result is claimed.

This is research-only. No production ingestion, species profile, SST factor, numerical range, weight, gate, score, confidence, or publication behavior changes.


## Profile-row retrieval implementation | 2026-11-19

Added a manual, read-only GitHub Actions workflow and downloader:
- Workflow: `.github/workflows/ioos-usf-sam-profile-inventory.yml`
- Script: `scripts/download_ioos_glider_profile_inventory.py`
- Artifact name: `ioos-usf-sam-profile-inventory`

The script discovers variables from the live ERDDAP `info/{dataset}/index.csv` metadata endpoint, verifies required identifiers/time/position/depth/pressure/temperature columns, then downloads source observation rows from the ERDDAP `.csvp` endpoint. It includes every available QARTOD variable whose name begins with temperature, pressure, depth, or location prefixes. It writes the source metadata CSV, raw observation CSV, and JSON summary containing row count, unique profile IDs, WMO IDs, nonmissing core values, and QC flag counts.

The workflow is manual-only. It has been committed but has not yet been run; the live source download and the exact number of rows/QC counts remain unverified until the user dispatches it and the run succeeds. No ETOPO join or Copernicus matching occurs in this step.



## First workflow attempt and parser correction | 2026-11-19

The first manual inventory run failed before the observation query. GitHub Actions run [44534528629](https://github.com/markeetox/LUPITA/actions/runs/44534528629) successfully checked out the repository and set up Python, but the script reported every required variable missing and `available=[]`. Inspection of the script showed it expected compact metadata keys `rowName` and `variableName`; the ERDDAP `info/{dataset}/index.csv` response uses the standard labels `Row Type` and `Variable Name`. This was a client-side CSV-header parsing defect, not evidence that the dataset lacks variables or that the data endpoint is unavailable.

Corrected the metadata parser to normalize header labels and accept the standard ERDDAP header, while retaining compatibility with compact legacy labels. Added unit tests for standard headers, legacy headers, unrecognized headers, and empty responses. The fix is on `main`; the Python CI workflow will verify it. The inventory workflow has not yet been rerun, so no profile rows or QC counts are available. Next: wait for CI, then manually rerun the inventory workflow.

The parser correction passed the repository Python test suite in runs [44534825300](https://github.com/markeetox/LUPITA/actions/runs/44534825300) and [44534837360](https://github.com/markeetox/LUPITA/actions/runs/44534837360). These validate the code/tests only; they do not establish live ERDDAP metadata availability or download any observations. The manual inventory workflow can now be rerun.

## Second workflow attempt and CSVp header correction | 2026-11-19

The rerun [44535135692](https://github.com/markeetox/LUPITA/actions/runs/44535135692) passed ERDDAP metadata discovery and completed the observation request, but failed when the script required a literal `temperature` CSV header. The request uses ERDDAP `.csvp`, whose documented header format is `name (units)`, for example `temperature (degree_C)`, rather than the bare variable name. This is confirmed by ERDDAP tabledap documentation: https://www.ncei.noaa.gov/erddap/tabledap/documentation.html. The response file was downloaded but the workflow stopped before artifact upload; no row/QC inventory was produced.

Updated the downloader to normalize `.csvp` headers by removing the parenthesized unit annotation while preserving the original raw response file. Added tests for unit-annotated and bare CSV headers. This preserves original values and units in the raw file; the JSON inventory records the normalized field names. Python CI must pass before the next manual run. No ETOPO join, Copernicus pairing, or production change.

The CSVp header normalization and tests passed Python CI in runs [44535325946](https://github.com/markeetox/LUPITA/actions/runs/44535325946) and [44535361351](https://github.com/markeetox/LUPITA/actions/runs/44535361351). These validate parser fixtures only; live inventory still requires a manual workflow dispatch.

## First successful live profile inventory | 2026-11-20

Successful manual workflow run: [44737352618](https://github.com/markeetox/LUPITA/actions/runs/44737352618). Both the observation download and artifact upload completed. Artifact: `ioos-usf-sam-profile-inventory`, ID `14628762755`, SHA-256 `15e4149e892813a398187987bda6eddaef96e7aef0b14f03e20bb1bb5ba97a1f`. The ZIP contains `dataset_info.csv`, `inventory_summary.json`, and the unmodified ERDDAP `.csvp` observation CSV.

Inventory results:
- Dataset: `usf-sam-20240216T0000`; WMO ID 4801942.
- 201,645 total ERDDAP rows and 2,387 unique profile IDs.
- 72,426 rows contain temperature, depth, and pressure; all 2,387 profiles have at least some such observations.
- Temperature range 16.8621–21.7797 °C; depth range 0.5761–140.6833 m; pressure range 0.58–141.67 bar.
- Observation period 2024-02-16T16:23:37Z through 2024-03-15T10:52:41Z.
- Point-field precise coordinates span 27.58795–28.03947°N and -84.56762 to -83.12165°W. These fields are documented as calculated/interpolated, not direct raw sensor positions.
- Per-profile maximum depth median 35.09 m; 90th percentile 59.42 m; 95th percentile 68.83 m; maximum 140.68 m. Thus the dataset's maximum depth is not representative of every profile and cannot be treated as seabed reach.
- Temperature primary QARTOD on 72,426 temperature rows: 72,382 PASS, 43 SUSPECT, 1 FAIL. PASS is 99.939% of temperature-bearing rows. Do not equate this with independent calibration validation.
- Temperature spike flag: 9,954 PASS, 4,774 NOT_EVALUATED, 18 SUSPECT, 1 FAIL; remaining 57,679 rows have no spike flag. NOT_EVALUATED and absent flags are not PASS.
- Temperature flat-line: 72,401 PASS and 25 SUSPECT. Gross-range and rate-of-change flags report PASS for all 72,426 temperature-bearing rows.
- 129,219 of the 201,645 ERDDAP rows have no temperature/depth/pressure values. They remain in the raw artifact; the inventory must distinguish total table rows from usable temperature-bearing observations. The dataset uses profile/subset variables, so row count is not the usable sample count.
- The inventory did not calculate ETOPO bottom separation or pair to Copernicus.

Next: obtain ETOPO 2022 30-arc-second bathymetry covering the actual glider footprint, join each temperature observation using documented position/time fields and preserve coordinate provenance, inspect per-profile seabed separation and near-bottom sensitivity bands. Do not select a cutoff or pair Copernicus until this is complete. The deployment remains a separate West Florida shelf/slope candidate, not a direct sample of the existing Copernicus Gulf pilot box.

### Additional screening from the downloaded observation rows | 2026-11-20

The downloaded raw CSV was independently re-read, rather than relying only on the workflow summary. Profile maximum-depth screening across all 2,387 profiles with valid temperature/depth rows:

- At least 10 m: 2,376 profiles
- At least 20 m: 2,242
- At least 50 m: 512
- At least 75 m: 112
- At least 100 m: 52
- At least 125 m: 10
- At least 140 m: 4

These are profile maximum-depth counts, not counts of near-bottom profiles. Seafloor depth is not yet known at each profile position, so none of these thresholds can be interpreted as bottom proximity.

The temperature-bearing rows have 72,382 primary-QC PASS, 43 SUSPECT, and 1 FAIL. For the spike test specifically, only 9,954 are PASS, 4,774 are NOT_EVALUATED, 18 are SUSPECT, 1 is FAIL, and 57,679 have no spike-test value. The high primary-PASS count must not conceal missing individual-test coverage.

**Pressure metadata discrepancy requiring resolution:** raw observation values span 0.58–141.67, while ERDDAP metadata labels pressure as bar and its comment says it is an alias for sci_water_pressure, multiplied by 10 to convert from bar to dbar. Values near 141 at a reported depth near 140 m look numerically like dbar, but that is not sufficient evidence to relabel or convert the variable. Preserve the source values and units as published; do not use pressure in bathymetry matching until the source-sensor units and transformation are verified. The separate depth field is documented as calculated from the CTD m_depth sensor and is the candidate vertical coordinate for the preliminary ETOPO separation screen.

For the ETOPO join, use point-level precise_lat/precise_lon as the dataset's interpolated position estimates, preserve that provenance, and report nearest-grid-cell offset. ETOPO 2022 30-arc-second z is height positive up in the EGM2008 vertical CRS; converting negative ocean elevations to positive seafloor depth and subtracting the glider depth is only a screening estimate because the glider depth is sea-surface referenced and the vertical datums are not demonstrated to be identical. Retain negative separations and do not clip them.

Next: acquire ETOPO 2022 30-arc-second cells covering the actual track, join every temperature-bearing row, and report per-profile minimum/maximum bottom separation plus sensitivity counts at 5/10/20/50 m. No near-bottom cutoff is selected in advance.

## IOOS-to-ETOPO screening implementation | 2026-11-20

Added research-only script `scripts/join_ioos_glider_etopo.py`, workflow `.github/workflows/ioos-usf-sam-etopo-screening.yml`, and unit tests `tests/test_join_ioos_glider_etopo.py`.

The manual workflow accepts the successful inventory run ID, downloads that run's `ioos-usf-sam-profile-inventory` artifact through the GitHub Actions artifact API, requests the ETOPO 2022 30-arc-second grid subset covering the observed glider track from NOAA ERDDAP, and joins every temperature-bearing observation to its nearest grid center. West longitudes are converted to the ETOPO ERDDAP 0–360 longitude convention. It preserves original observation values, interpolated coordinate provenance, QARTOD temperature primary flag, ETOPO grid cell, nearest-cell offset, and signed bottom-separation estimate. It outputs the raw ETOPO subset, per-observation join CSV, and JSON summary with 5/10/20/50m sensitivity counts split by all rows and primary-QC PASS rows.

The script writes a second per-profile CSV with signed minimum/median/maximum separation, negative-separation counts, minimum nonnegative separation, and 5/10/20/50m observation counts split by primary-QC PASS. The script deliberately excludes pressure because of the unresolved source metadata unit/transformation conflict. It classifies ETOPO cells using the established thresholds: z < -1m ocean, z > +1m land, and -1m through +1m coastal ambiguous. Negative separations are retained. It labels separation as screening-only because ETOPO z is EGM2008 height positive up while glider depth is sea-surface referenced; equivalence of vertical datums is not established. No near-bottom cutoff is selected and no Copernicus pairing occurs.

The workflow is manual-only. It completed successfully in [run 44740669528](https://github.com/markeetox/LUPITA/actions/runs/44740669528), using inventory run `44737352618`; artifact ID 14631270203 contains the ETOPO grid, observation join, profile summary, and JSON summary. See the results section below. No production behavior changed.


## IOOS USF Sam ETOPO screening results | 2026-11-20

Successful live run [44740669528](https://github.com/markeetox/LUPITA/actions/runs/44740669528), job `join`, artifact `ioos-usf-sam-etopo-screening` ID 14631270203 (ZIP SHA-256 `42f2ab838d22946e72f14bbc27874cb28e028fb88cffe06bfe4d66d04e560022`). The workflow downloaded the exact inventory artifact from run 44737352618, requested ETOPO_2022_v1_30s for the glider track, joined the rows, and uploaded all four outputs.

The join contains 201,645 coordinate-bearing rows across 2,387 profiles. All 201,645 mapped to ETOPO ocean-class cells; no land or coastal-ambiguous point assignments occurred in this track. This does not mean every row has usable temperature/depth: 72,426 rows have finite depth and temperature, and 129,219 do not. Among the usable rows, temperature primary QARTOD is 72,382 PASS, 43 SUSPECT, and 1 FAIL.

For the 72,426 finite temperature/depth observations, nearest-cell ETOPO screening separation is -4.852 to 143.988m, with median 20.044m and mean 25.234m. There are 1,062 negative separations (1,061 PASS and 1 SUSPECT); these remain visible and are excluded from nonnegative near-bottom bands. Nearest ETOPO grid-center offset has median about 351m and maximum about 618m.

Nonnegative separation sensitivity (not an adopted cutoff):
- 0–5m: 8,446 observations, 2,180 profiles; 8,445 PASS observations and 2,180 PASS-represented profiles.
- 0–10m: 17,261 observations, 2,212 profiles; 17,260 PASS observations and 2,212 PASS-represented profiles.
- 0–20m: 35,075 observations, 2,250 profiles; 35,074 PASS observations and 2,250 PASS-represented profiles.
- 0–50m: 63,765 observations, 2,298 profiles; 63,743 PASS observations and 2,297 PASS-represented profiles.

All profile counts are nested within one glider deployment and are not independent samples. The glider precise position fields are interpolated estimates, not raw GPS fixes. ETOPO height uses EGM2008 and is not established as vertically equivalent to the sea-surface-referenced glider depth. Negative separation may reflect vertical reference, bathymetry, sensor depth, or position uncertainty; its cause is unresolved. Pressure remains excluded due to the unresolved source metadata units/transformation issue. This is bathymetric screening only, not Copernicus accuracy validation. The deployment is outside the existing Copernicus Gulf candidate box and would require a separate West Florida regional Copernicus extraction and time-matched comparison.

A defect was identified in the first output summary: missing depth/temperature values were represented as NaN, causing the all-row separation median (and some per-profile medians) to serialize as NaN. The observation-level CSV and sensitivity counts still supported the finite-row calculations above; medians were independently recomputed from the 72,426 finite observations. Fixed the join to retain position-only rows while calculating separation only for finite depth+temperature values, report valid observation/QC counts, and calculate medians from finite values. Added a regression test. A separate pre-existing URL test expected longitude 275 for -83.3°; corrected it to 276.7° (0–360 convention). The missing-value fix, regression test, and corrected longitude assertion passed the full Python test workflow in [run 44741832591](https://github.com/markeetox/LUPITA/actions/runs/44741832591).

No Copernicus pairing, production scoring/source changes, species profile changes, or ingestion changes.


## Preparing like-for-like temperature comparison with Copernicus | 2026-11-20

Copernicus `bottomT` is documented as sea-floor **potential temperature**, standard name `sea_water_potential_temperature_at_sea_floor`, independent of the vertical depth dimension. The global reanalysis daily dataset covers the 2024 glider deployment period; its P1D-m values are daily means. References: [Copernicus bottomT definition](https://help.marine.copernicus.eu/en/articles/4877597-depth-selection-when-downloading-the-bottomt-variable), [GLOBAL_MULTIYEAR_PHY_001_030 product description](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/description), [dataset temporal resolution](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/services), and [dataset nomenclature / daily mean definition](https://help.marine.copernicus.eu/en/articles/6820094-how-copernicus-marine-data-nomenclature-is-defined).

The glider `temperature` field is measured CTD in-situ temperature, so it must not be compared directly to Copernicus potential temperature as if the variables were identical. The IOOS dataset metadata also exposes `salinity` as calculated practical salinity with QARTOD primary flags. The first inventory did not download salinity. Updated the research inventory downloader to include `salinity` and all `qartod_salinity_*` flags, plus nonmissing counts, so a later TEOS-10 conversion can be assessed. This is a code change only; no salinity observations have yet been downloaded or converted. CI for the salinity inventory extension is running in [44742300164](https://github.com/markeetox/LUPITA/actions/runs/44742300164) and [44742308838](https://github.com/markeetox/LUPITA/actions/runs/44742308838).

Next sequence: wait for CI; rerun the manual IOOS inventory workflow to acquire salinity and QC; inspect salinity QC/completeness and its relation to temperature/depth; resolve the pressure metadata inconsistency without silently using pressure values; evaluate deriving sea pressure from CTD depth and latitude; convert measured in-situ temperature to potential temperature using TEOS-10 only after inputs and assumptions are documented; then extract daily Copernicus reanalysis `bottomT` for the West Florida deployment footprint and compare only time-matched, near-bottom observations. Use multiple separation bands and spatial-cell sensitivity rather than choosing one cutoff prematurely. The glider deployment is outside the existing Gulf pilot box, so this requires a separate West Florida subset. No production changes.

## Salinity inventory extension passed CI | 2026-11-20

The salinity acquisition extension and its tests both passed the full Python CI workflow:
- Script/dependency CI: [44742300164](https://github.com/markeetox/LUPITA/actions/runs/44742300164), job `pytest` ID 136308729869, success.
- Test update CI: [44742308838](https://github.com/markeetox/LUPITA/actions/runs/44742308838), job `pytest` ID 136308758566, success.

The downloader now requests the calculated practical-salinity variable and all available `qartod_salinity_*` fields, and includes salinity plus its primary QC in the nonmissing summary. CI validates code and fixtures only. No new salinity observations have been downloaded, and no TEOS-10 conversion has been performed.

Next action: manually rerun [the IOOS USF Sam profile inventory workflow](https://github.com/markeetox/LUPITA/actions/workflows/ioos-usf-sam-profile-inventory.yml). Then inspect salinity completeness, primary and individual QARTOD distributions, and row-level alignment with temperature/depth before considering any potential-temperature conversion. Pressure remains unresolved and must not be silently used. No Copernicus pairing or production change.
