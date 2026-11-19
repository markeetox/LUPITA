

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
