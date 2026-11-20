

## Actual pinned parser attempt blocked by NCEI delivery outage | 2026-11-19

GitHub Actions run [44531684748](https://github.com/markeetox/LUPITA/actions/runs/44531684748) successfully checked out the repository and installed the exact pinned IQuOD wodpy commit 116480b257a227ce38281d3836c40812246e5156 (package wodpy==2.0.0b0; the built wheel hash is omitted because the commit pin is the stable provenance identifier). The run failed at the NOAA WODSelect GLD download: NCEI returned HTTP 503 on all retry attempts. Consequently the ETOPO artifact download, actual parsing, join, and comparison steps were skipped. No parser parity result exists yet.

NCEI's public Alerts page currently reports WODSelect performance issues (Nov 5–7, 2026) and broader data-access delays through Nov 30 associated with its cloud migration, including intermittent degraded order-fulfillment services. This is consistent with the observed service-side failure but does not prove the specific cause of this 503. Sources: https://www.ncei.noaa.gov/alerts and https://www.ncei.noaa.gov/access.

Next: retry the same exact GLD download after NCEI service recovery, preserving the expected source SHA-256 c75b110c4eba09c0a55aed34cf31d12f2693d3053fad09216d2794ff370fb0e3. Do not replace the requested GLD archive with a different dataset or accept the preliminary parser transcription as parity. The pinned parser installation is now verified; the real archive execution remains blocked solely at source delivery. No production behavior changed.


## Actual parser run: package installed; NOAA output endpoint unavailable from runner | 2026-11-19

The first actual-run attempt, [run 44531684748](https://github.com/markeetox/LUPITA/actions/runs/44531684748), installed the exact pinned IQuOD `wodpy` commit successfully, but NOAA's WODSelect output URL returned HTTP 503 on all download retries. A second attempt confirmed the same response. This does not prove the file expired; the user-submitted WODSelect files were still within the stated 72-hour availability window at the time. The actual GLD archive remains available in the ChatGPT working upload, but the GitHub runner cannot directly access that session-local file.

Prepared a controlled fallback branch `research-wod-gld-input-20261119` from `main`. Its workflow copy listens only for the original GLD gzip being uploaded to `research-inputs/ocldb1794949360.1820758.GLD.gz`, then verifies the expected source SHA-256 `c75b110c4eba09c0a55aed34cf31d12f2693d3053fad09216d2794ff370fb0e3`, downloads the exact ETOPO artifact, runs the installed pinned parser, and uploads the join output. The branch is temporary and must be deleted after the run and results are captured. Upload page: `https://github.com/markeetox/LUPITA/upload/research-wod-gld-input-20261119/research-inputs`.

The `main` workflow remains manual-only; no production data or prediction behavior changed. Full parser parity remains pending until the original archive is available to the GitHub runner and the resulting CSV can be compared with the preliminary local join.


## Alternate NOAA profile inventory route identified | 2026-11-19

Rather than repeatedly retrying the WODSelect GLD output URL during the current NCEI access disruption, a parallel GTSPP inventory route has been documented in [NOAA_GTSPP_REGIONAL_INVENTORY_PLAN_2026-11-19.md](NOAA_GTSPP_REGIONAL_INVENTORY_PLAN_2026-11-19.md). NCEI's GTSPP query interface supports regional boxes, a 1990-present date range, Best Copy / Real Time / Delayed modes, data-type selection, station counts, DBID lists, and downloadable data. NCEI describes Best Copy as a curated archive that can replace real-time lower-resolution records with delayed-mode full-resolution CTD/XBT or fully processed QC submissions.

The GTSPP query page was reachable during reconnaissance, but no query has yet been submitted and no counts or files have been retrieved. GTSPP is a parallel candidate source, not a substitute proven equivalent to the original WODSelect GLD extraction. Overlap with WOD and other archives must be deduplicated before counting independent observations. The four candidate regional boxes and query protocol are recorded in the new plan. NCEI currently reports cloud-migration access delays and intermittent degraded order fulfillment.

Next: obtain regional GTSPP Best Copy station counts, beginning with South Florida to establish comparability, then Gulf, Atlantic, and Pacific. Capture exact data-type selections and query receipts. Download only after the station inventory is understood. Keep the preliminary South Florida GLD-to-ETOPO join unverified against the installed parser until exact parser parity is completed. No production behavior changed.


## GTSPP interface unavailable; IOOS Glider DAC alternative identified | 2026-11-19

The user attempted the GTSPP regional query interface and received Service Unavailable. NCEI's Alerts page currently reports intermittent degraded order fulfillment during its cloud migration, and the NCEI Access page warns that many access portals/data folders are unavailable. No GTSPP station count or data file was obtained. Do not keep retrying the interactive form while the service notice remains active.

A separate IOOS National Glider DAC route has been investigated. Its ERDDAP and THREDDS catalogs distribute measured glider profiles outside the GTSPP query interface. A candidate University of South Florida/GCOOS deployment, `usf-sam-20240216T0000`, has metadata coverage 2024-02-16 to 2024-03-15, 27.588–28.039°N, -84.567 to -83.122°W, and maximum observed depth 140.68 m. It is in the Gulf of Mexico but outside the existing Copernicus Gulf pilot box; treat it as a possible separate West Florida shelf/slope stratum only. Its per-profile bottom separation and QARTOD flags have not yet been inspected. No glider data have been downloaded or paired to Copernicus.

Protocol: [IOOS_GLIDER_DAC_REGIONAL_INVENTORY_PLAN_2026-11-19.md](IOOS_GLIDER_DAC_REGIONAL_INVENTORY_PLAN_2026-11-19.md). No production behavior changed.


The USF Sam dataset metadata was inspected more deeply. Temperature is measured CTD data in Celsius (accuracy 0.004°C; precision/resolution 0.001°C). Depth is calculated from the CTD m_depth sensor, positive down in metres, referenced to sea surface (accuracy 0.01 m). Pressure is measured in bar; metadata says the alias is multiplied by 10 to convert bar to dbar. Both profile-level coordinates/time and point-level precise_lat/precise_lon/precise_time are described as calculated/interpolated, not raw direct observations. Temperature QARTOD primary flag values are PASS=1, NOT_EVALUATED=2, SUSPECT=3, FAIL=4, MISSING=9; metadata range is 1–4, but actual observation counts by flag are not yet retrieved. No actual profile rows downloaded or paired.


## IOOS USF Sam raw profile inventory workflow added | 2026-11-19

Added manual-only research workflow `.github/workflows/ioos-usf-sam-profile-inventory.yml` and script `scripts/download_ioos_glider_profile_inventory.py`. It discovers the dataset variables from live ERDDAP metadata, downloads the raw observation CSV including all available temperature/pressure/depth/location QARTOD fields, and produces a JSON summary with row counts, distinct profile IDs, WMO IDs, missingness, and QC flag counts. Artifact: `ioos-usf-sam-profile-inventory`.

The workflow has not yet been dispatched. Actual rows and QC counts are not yet retrieved. No ETOPO join, Copernicus pairing, or production behavior change.



## IOOS inventory workflow failure diagnosed and parser fix committed | 2026-11-19

The first manual IOOS inventory run [44534528629](https://github.com/markeetox/LUPITA/actions/runs/44534528629) failed in the downloader before requesting observations. The script looked for compact CSV dictionary keys `rowName` and `variableName`, but ERDDAP's standard `info/{dataset}/index.csv` format uses headers `Row Type` and `Variable Name`. The resulting empty variable list caused the required-variable check to fail. This is a script parsing bug, not evidence of missing dataset variables or a failed observation download.

Fixed `scripts/download_ioos_glider_profile_inventory.py` to normalize ERDDAP metadata headers and support both standard and compact variants. Added `tests/test_ioos_glider_profile_inventory.py` covering standard headers, legacy headers, invalid headers, and empty responses. The changes are on main; automated Python CI will validate them. The inventory has not yet been rerun, and no observation rows or QC counts have been retrieved. No ETOPO/Copernicus analysis or production behavior changed.

The ERDDAP header correction and new parser tests passed full Python CI in runs [44534825300](https://github.com/markeetox/LUPITA/actions/runs/44534825300) and [44534837360](https://github.com/markeetox/LUPITA/actions/runs/44534837360). This confirms the parser behavior against fixtures, not the live dataset or observation download. Next step is a fresh manual dispatch of the IOOS inventory workflow. No data/QC results exist yet.

## IOOS inventory second failure diagnosed; CSVp header fix committed | 2026-11-19

The second manual run [44535135692](https://github.com/markeetox/LUPITA/actions/runs/44535135692) passed metadata discovery and downloaded the ERDDAP observation response, then failed because the script expected the literal header `temperature`. ERDDAP `.csvp` uses `variable (units)` headers, e.g. `temperature (degree_C)`, as documented at https://www.ncei.noaa.gov/erddap/tabledap/documentation.html. The downloaded response was not uploaded because the workflow stopped before the artifact step. No observations/QC counts have been inventoried yet.

Committed a normalizer that strips unit annotations only for in-memory column keys while preserving the original downloaded CSV unchanged. Added unit tests for CSVp headers with and without units. Await Python CI, then rerun the manual inventory. No ETOPO/Copernicus analysis or production behavior changed.

The CSVp header normalizer and unit tests passed Python CI in [44535325946](https://github.com/markeetox/LUPITA/actions/runs/44535325946) and [44535361351](https://github.com/markeetox/LUPITA/actions/runs/44535361351). This validates the parser against fixtures, not the live data download. The IOOS inventory workflow is ready for another manual run; no observation/QC results exist yet.

## IOOS USF Sam first live inventory completed | 2026-11-20

Successful run [44737352618](https://github.com/markeetox/LUPITA/actions/runs/44737352618); artifact [ioos-usf-sam-profile-inventory](https://github.com/markeetox/LUPITA/actions/runs/44737352618/artifacts/14628762755), ID 14628762755. Artifact includes raw observations, dataset metadata, and JSON summary.

Results: 201,645 total ERDDAP rows; 2,387 unique profiles; 72,426 rows with temperature/depth/pressure; all 2,387 profiles have some temperature-bearing observations. Temperature 16.8621–21.7797 °C; depth 0.5761–140.6833 m; pressure 0.58–141.67 bar. Period 2024-02-16T16:23:37Z to 2024-03-15T10:52:41Z. Temperature primary QARTOD: 72,382 PASS, 43 SUSPECT, 1 FAIL. Temperature spike flag has only 9,954 PASS, 4,774 NOT_EVALUATED, 18 SUSPECT, 1 FAIL; 57,679 temperature rows have no spike flag. Do not treat missing or NOT_EVALUATED as PASS.

Per-profile maximum depth median 35.09 m, 90th percentile 59.42 m, 95th percentile 68.83 m, maximum 140.68 m. Therefore maximum deployment depth does not establish typical near-bottom coverage. 129,219 of the 201,645 ERDDAP rows contain no temperature/depth/pressure; keep total table rows separate from usable observations.

Next: export ETOPO 2022 30-arc-second bathymetry for the actual glider footprint, join observations with coordinate provenance, calculate per-profile bottom separation and sensitivity bands. No Copernicus pairing, accuracy claim, or production behavior change yet. Full protocol/results: [IOOS_GLIDER_DAC_REGIONAL_INVENTORY_PLAN_2026-11-19.md](IOOS_GLIDER_DAC_REGIONAL_INVENTORY_PLAN_2026-11-19.md).

## IOOS USF Sam depth-distribution and pressure-metadata screening | 2026-11-20

A second pass over the raw artifact from [run 44737352618](https://github.com/markeetox/LUPITA/actions/runs/44737352618) found that profile maximum depth is highly uneven: 512/2,387 profiles reach at least 50 m; 112 reach 75 m; 52 reach 100 m; 10 reach 125 m; and 4 reach 140 m. These are maximum-depth counts only, not bottom-proximity counts. No seabed separation can be inferred without local bathymetry.

A pressure metadata inconsistency must be resolved before using pressure: observed values span 0.58–141.67, but ERDDAP labels units as bar while its comment says the variable is multiplied by 10 to convert from bar to dbar. Values near 141 at depths near 140 m appear dbar-like, but that is not enough to override source metadata. Preserve the original values; do not use pressure for the ETOPO join until source-sensor units/transformation are verified. Use the separate depth variable, documented as calculated from CTD m_depth, as the candidate depth coordinate.

ETOPO join caveat: ETOPO 2022 30-arc-second z is height positive up with EGM2008 vertical CRS, while glider depth is sea-surface referenced. Bottom separation is therefore a preliminary screening estimate unless vertical-datum equivalence is established. Keep negative separations visible. Point coordinates are interpolated estimates. No Copernicus pairing, accuracy claim, or production change.

## IOOS USF Sam ETOPO screening workflow implemented | 2026-11-20

Added `scripts/join_ioos_glider_etopo.py`, manual workflow `.github/workflows/ioos-usf-sam-etopo-screening.yml`, and tests `tests/test_join_ioos_glider_etopo.py`. The workflow takes inventory run ID `44737352618`, downloads its artifact, requests a NOAA NCEI ETOPO 2022 30-arc-second subset for the actual glider footprint, and creates per-observation nearest-cell bathymetry joins, a per-profile signed-separation CSV, and a JSON sensitivity summary. It preserves signed bottom separation, negative values, QC, interpolated coordinate provenance, and grid-center offsets. Pressure is excluded pending source-unit resolution. The live workflow succeeded in [run 44740669528](https://github.com/markeetox/LUPITA/actions/runs/44740669528), artifact 14631270203. It joined 201,645 coordinate-bearing rows from 2,387 profiles; all mapped to ETOPO ocean cells. 72,426 rows had finite depth and temperature (72,382 primary-QC PASS, 43 SUSPECT, 1 FAIL). Nonnegative bottom-separation sensitivity: 8,446 rows / 2,180 profiles within 5m; 17,261 / 2,212 within 10m; 35,075 / 2,250 within 20m; 63,765 / 2,298 within 50m. There were 1,062 negative separations, retained and excluded from these bands. The vertical-datum mismatch, interpolated positions, single deployment, and regional mismatch with the current Gulf Copernicus box remain limitations. See `docs/IOOS_GLIDER_DAC_REGIONAL_INVENTORY_PLAN_2026-11-19.md` for full results. A missing-value/NaN summary defect and a longitude test expectation were fixed in code; Python CI rerun is pending. No Copernicus pairing or production change.


## IOOS ETOPO join interpretation and follow-up | 2026-11-20

The first live artifact exposed a summary-statistics defect: NaN depth/temperature rows caused JSON medians to be NaN. The underlying finite-row CSV was independently analyzed; code now retains rows with position/time/profile but only calculates bottom separation for finite depth+temperature, includes usable observation/QC counts, and computes finite medians. A regression test was added. CI run [44741683803](https://github.com/markeetox/LUPITA/actions/runs/44741683803) failed only because an existing longitude test expected 275 for -83.3° instead of the correct 276.7° after conversion to 0–360; assertion corrected. Latest CI reruns are pending. No production changes.
