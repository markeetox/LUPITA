

## 2026-11-19 | Pinned wodpy installation succeeded; NOAA source delivery returned HTTP 503

Dispatched actual-parser workflow [44531684748](https://github.com/markeetox/LUPITA/actions/runs/44531684748). GitHub Actions successfully installed the exact IQuOD wodpy commit 116480b257a227ce38281d3836c40812246e5156 (wodpy==2.0.0b0; the built wheel hash is omitted because the commit pin is the stable provenance identifier). The NOAA GLD download step then received HTTP 503 on every retry. The ETOPO download, actual package parser run, full join, and comparison were skipped. This is not parser parity and produced no scientific join result.

The NCEI Alerts page reports broader data-access delays through Nov 30 during its cloud migration, including intermittent degraded order fulfillment; this is consistent with the observed failure but does not establish its specific cause. Sources: https://www.ncei.noaa.gov/alerts and https://www.ncei.noaa.gov/access.

Next: retry the exact original WODSelect GLD archive after NCEI recovery, verify its expected SHA-256 c75b110c4eba09c0a55aed34cf31d12f2693d3053fad09216d2794ff370fb0e3, then run the exact pinned parser and compare every cast/level to the preliminary join. Do not substitute another dataset or call the preliminary transcription verified. No production behavior changed.


## 2026-11-19 | Actual parser runner installed pinned wodpy; NOAA file transfer blocked

GitHub Actions successfully installed IQuOD `wodpy` at commit `116480b257a227ce38281d3836c40812246e5156` in actual-run [44531684748](https://github.com/markeetox/LUPITA/actions/runs/44531684748), but the NCEI WODSelect output URL returned HTTP 503 on repeated attempts. The run did not reach the ETOPO download or actual GLD parsing stages. This is a transfer/service failure, not a parser failure, and does not establish that the WODSelect file expired.

Created temporary branch `research-wod-gld-input-20261119` with a branch-specific workflow that will run automatically when the original GLD gzip is uploaded to `research-inputs/ocldb1794949360.1820758.GLD.gz`. The workflow validates the uploaded file against its known SHA-256 before parsing. Upload page: `https://github.com/markeetox/LUPITA/upload/research-wod-gld-input-20261119/research-inputs`. After the workflow completes, download artifact `wod-gld-actual-parser-parity`, compare actual output to the preliminary local join, and delete the temporary branch. Main workflow is manual-only; no production changes.


## 2026-11-19 | GTSPP identified as parallel NOAA observation-inventory route

After the exact WODSelect GLD output URL repeatedly returned HTTP 503, inspected the official NCEI GTSPP product and user-specified query interface. The interface supports geographic boxes, dates from 1990-present, Best Copy / Real Time / Delayed modes, data-type selection, Argo exclusion, station counts, station DBID lists, and downloadable data files. NCEI documents Best Copy as a curated archive that may replace lower-resolution real-time records with delayed-mode full-resolution CTD/XBT or fully processed QC data.

Created `docs/NOAA_GTSPP_REGIONAL_INVENTORY_PLAN_2026-11-19.md` with the four existing Copernicus candidate boxes, a conservative query protocol, and screening/deduplication requirements. The query page was reachable, but no GTSPP query was submitted and no counts or data files have been retrieved. GTSPP may overlap WOD/IQuOD/other archives and must not be counted as independent until deduplicated. This is a parallel candidate acquisition route, not an asserted equivalent replacement for the original WODSelect GLD file.

Corrected the project record to omit a non-stable built-wheel SHA claim; the exact IQuOD source commit remains the reproducible parser provenance. No production behavior changed.


## 2026-11-19 | GTSPP query unavailable; IOOS Glider DAC alternate source reconnaissance

The user attempted the GTSPP regional query form and received Service Unavailable. NCEI Alerts currently reports intermittent degraded order fulfillment during its cloud migration; the NCEI Access page warns that many portals and data folders are unavailable. No query count or GTSPP file was retrieved. Stop retrying the query interface while the outage notice remains active.

Investigated the independently hosted IOOS National Glider DAC ERDDAP/THREDDS distribution. The DAC catalogs historical and current glider missions and provides profile-level datasets. Verified one University of South Florida/GCOOS deployment, `usf-sam-20240216T0000`: 2024-02-16 through 2024-03-15; 27.588–28.039°N, -84.567 to -83.122°W; maximum depth 140.68 m; CTD; trajectory-profile; QARTOD flags available. It is outside the existing Gulf Copernicus box, so it is only a candidate for a separate West Florida shelf/slope stratum. Maximum depth alone does not prove near-bottom coverage. No observations downloaded, no ETOPO join, no Copernicus pairs or metrics.

Added `docs/IOOS_GLIDER_DAC_REGIONAL_INVENTORY_PLAN_2026-11-19.md` with source metadata, screening requirements, and limits. No production changes.


Inspected the USF Sam ERDDAP variable metadata in detail. Confirmed temperature is measured CTD Celsius (accuracy 0.004°C, resolution 0.001°C); depth is calculated from m_depth, positive down, sea-surface reference, 0.01m accuracy; pressure is measured in bar with documented x10 conversion to dbar. Profile-level and point-level precise time/coordinates are described as calculated/interpolated. Temperature QARTOD primary flags use 1 PASS, 2 NOT_EVALUATED, 3 SUSPECT, 4 FAIL, 9 MISSING; actual row counts by flag not yet retrieved. This corrects an earlier plan statement that described point-level precise fields as measured. No profile data download, ETOPO join, or Copernicus pairing yet.


## 2026-11-19 | IOOS USF Sam profile row inventory workflow

Added `scripts/download_ioos_glider_profile_inventory.py` and manual workflow `.github/workflows/ioos-usf-sam-profile-inventory.yml`. Script dynamically discovers dataset variables from ERDDAP info metadata, verifies required core fields, downloads raw observation rows plus all available QARTOD variables for temperature/pressure/depth/location, and summarizes row count, unique profile IDs, WMO IDs, nonmissing core fields, and QC counts. It preserves the raw CSV and metadata CSV as workflow artifacts with a JSON inventory summary. Workflow has not yet been run; no actual row counts/QC distributions are claimed. No ETOPO or Copernicus join and no production changes.



## 2026-11-19 | IOOS inventory failure traced to ERDDAP metadata header parsing

Inspected failed run [44534528629](https://github.com/markeetox/LUPITA/actions/runs/44534528629). Checkout and Python setup succeeded; downloader failed at the required-variable check because it parsed `rowName`/`variableName`, while standard ERDDAP `info/index.csv` uses `Row Type`/`Variable Name`. The script therefore produced an empty available-variable list before the observation data request. This is a client-side metadata parsing defect, not a dataset or observation-download failure.

Committed a normalized header parser in `scripts/download_ioos_glider_profile_inventory.py` and added `tests/test_ioos_glider_profile_inventory.py` for standard ERDDAP headers, compact legacy headers, invalid headers, and empty responses. Python CI will verify the fix. Next: after CI passes, rerun the manual IOOS inventory workflow. No actual glider rows/QC counts retrieved yet; no ETOPO join, Copernicus pairing, or production behavior change.

The ERDDAP metadata parser fix and test suite passed in Python CI runs [44534825300](https://github.com/markeetox/LUPITA/actions/runs/44534825300) and [44534837360](https://github.com/markeetox/LUPITA/actions/runs/44534837360). The fixture tests confirm standard ERDDAP spaced headers and compact legacy headers are handled. CI does not verify live ERDDAP access or retrieve glider observations. Manual inventory workflow is ready for a fresh run.

## 2026-11-19 | IOOS second run reached data response; CSVp unit header mismatch fixed

Run [44535135692](https://github.com/markeetox/LUPITA/actions/runs/44535135692) passed ERDDAP metadata discovery and fetched the observation response, but the downloader rejected its header because it expected `temperature` exactly. ERDDAP documents `.csvp` as using `name (units)` headers (e.g. `temperature (degree_C)`): https://www.ncei.noaa.gov/erddap/tabledap/documentation.html. The workflow did not upload artifacts and no observation/QC counts were generated.

Updated the downloader to normalize unit-annotated CSVp headers for analysis while preserving the raw response exactly. Added tests for unit-annotated and bare CSV headers. Wait for Python CI before another manual dispatch. No ETOPO join, Copernicus pairing, or production changes.

CSVp header normalization passed Python CI in runs [44535325946](https://github.com/markeetox/LUPITA/actions/runs/44535325946) and [44535361351](https://github.com/markeetox/LUPITA/actions/runs/44535361351). Fixture tests cover unit-annotated and bare headers. This does not itself retrieve observations; manual inventory workflow remains the next step.

## 2026-11-20 | First live IOOS USF Sam profile inventory succeeded

Inspected successful workflow [44737352618](https://github.com/markeetox/LUPITA/actions/runs/44737352618), its job logs, and downloaded artifact ID 14628762755 (`ioos-usf-sam-profile-inventory`; ZIP SHA-256 `15e4149e892813a398187987bda6eddaef96e7aef0b14f03e20bb1bb5ba97a1f`). The workflow successfully downloaded source observations and uploaded all three expected files: dataset metadata CSV, JSON inventory summary, and raw ERDDAP observation CSV.

Counts: 201,645 total ERDDAP rows; 2,387 unique profile IDs; 72,426 rows with temperature/depth/pressure; all 2,387 profiles have some temperature-bearing observations. Temperature 16.8621–21.7797°C; depth 0.5761–140.6833m; pressure 0.58–141.67bar. Time coverage 2024-02-16T16:23:37Z through 2024-03-15T10:52:41Z. Temperature primary QARTOD: 72,382 PASS, 43 SUSPECT, 1 FAIL. Temperature spike QC: 9,954 PASS, 4,774 NOT_EVALUATED, 18 SUSPECT, 1 FAIL, 57,679 absent. NOT_EVALUATED and absent are not PASS. Per-profile max-depth median 35.09m, 90th percentile 59.42m, 95th percentile 68.83m, max 140.68m; maximum deployment depth does not imply typical near-bottom sampling. 129,219 table rows have no temperature/depth/pressure values, so total ERDDAP rows must not be mistaken for usable temperature observations.

No ETOPO join, near-bottom classification, Copernicus pairing, accuracy metrics, or production change. Next action: obtain ETOPO 2022 30-arc-second bathymetry for the glider footprint and calculate per-observation/per-profile bottom separation with coordinate provenance and sensitivity bands before any Copernicus comparison.

## 2026-11-20 | IOOS depth distribution and pressure metadata caveat

Re-read the raw observation CSV from successful IOOS run [44737352618](https://github.com/markeetox/LUPITA/actions/runs/44737352618). Profile maximum-depth counts: 2,376 profiles >=10m; 2,242 >=20m; 512 >=50m; 112 >=75m; 52 >=100m; 10 >=125m; 4 >=140m. These are not near-bottom counts; local ETOPO bathymetry is still required.

Flagged a pressure metadata inconsistency: raw values span 0.58–141.67, ERDDAP says units=bar, and its comment says alias sci_water_pressure is multiplied by 10 to convert bar to dbar. The values look dbar-like relative to depth, but we will not infer a unit correction. Preserve raw pressure and exclude it from bottom-separation calculations pending source-sensor verification. Use the separate depth field (documented as calculated from CTD m_depth) for the preliminary join.

The ETOPO screening will also carry a vertical-datum caveat: ETOPO z uses EGM2008 and is positive up; glider depth is sea-surface referenced. Do not claim exact vertical-datum equivalence. Preserve negative separations and report them rather than clipping. No near-bottom cutoff, Copernicus pairing, or production change.

## 2026-11-20 | Implemented IOOS-to-ETOPO screening workflow

Added research-only `scripts/join_ioos_glider_etopo.py`, manual workflow `.github/workflows/ioos-usf-sam-etopo-screening.yml`, and unit tests `tests/test_join_ioos_glider_etopo.py`. The workflow downloads the prior inventory artifact by run ID, requests ETOPO 2022 30-arc-second cells for the glider track through NOAA ERDDAP, and joins temperature-bearing observations to nearest grid centers. Output includes raw ETOPO subset, joined observations, a per-profile signed min/median/max separation CSV, nearest-cell offsets, signed bottom separation, and 5/10/20/50m sensitivity counts by all rows and primary-QC PASS rows. Pressure is intentionally excluded because source metadata is internally inconsistent. Negative separations are preserved; EGM2008 versus sea-surface vertical datum difference is explicitly a limitation. The workflow is manual-only and has not yet been dispatched, so no live join result is claimed. Input inventory run ID: `44737352618`. No Copernicus pairing or production changes.
