## 2026-11-22 | South Florida first-visit map region

Added a dedicated **South Florida & Florida Keys** region to the map selector (24.0–28.5°N, 83.5–78.0°W) and made it the default for first-time visitors. Existing saved region preferences are retained, and the broader US Southeast, Gulf, Pacific, Northeast, Canada, and all-coasts options remain available. No scoring, species, or environmental data behavior changed. Frontend commit: `85bcbccb50cc4e4286414f07c973db257642f2e3`. JavaScript CI and Vercel deployment checks are running.

---

## 2026-11-22 | First user-facing model diagnostics and factor explanations

Inspected the actual published `data` branch snapshot before editing the map. The API index generated at 2026-11-22T11:06:59Z reports 130 catalog species, 125 with modeled areas, 5 with no favorable areas, and 960 modeled areas. The paired `latest.json` snapshot reports a degraded refresh with predictions refreshed, SST delayed by 50.1 hours (55.2% aligned grid validity), chlorophyll stale by 167.1 hours (21.6% aligned grid validity), and NOAA HF Radar fresh by 8.1 hours but covering only 1.5% of its local query grid (152/10,101 cells). ETOPO depth coverage is 53.2%; FWC habitat inventory contains 49,903 source features and 514 mapped query cells; reef inventory contains 4,548 artificial reef records and 25,362 natural reef polygons.

Updated `web/index.html`:
- Added a collapsible Data health panel driven by published `latest.json` diagnostics, with prediction snapshot counts, freshness, and spatial coverage.
- Corrected prediction status messaging so a degraded refresh is not presented as fully healthy.
- Removed the fabricated hardcoded sample species/spot fallback. When live prediction data is unavailable, the UI now reports that rather than inventing fishing areas.
- Added factor-level detail to mapped-area cards: factor match score, model weight, declared evidence status, notes, source links, input coverage, and confidence limitations.
- Clarified that the percentage is a habitat-match score, not catch probability, and that evidence status/source links do not establish that every numeric claim is validated.

Updated `.github/workflows/python-tests.yml` so changes under `web/**` run the CI workflow and the inline map JavaScript is checked with `node --check`. The syntax-check step passed and the full suite completed with **326 passed, 0 failed, 115 warnings** on [run 45034880374](https://github.com/markeetox/LUPITA/actions/runs/45034880374). The species audit artifact was also generated. Vercel reported successful deployment for frontend commit `febb87d59fe111eca570b975e9371b7079ccf225`.

Updated README, Project Status, and Roadmap. No prediction/scoring behavior, species biology, factor ranges, weights, gates, production environmental sources, or experimental Copernicus research inputs were changed.

Next: inspect the deployed UI at desktop/mobile sizes, refine the selected-area panel from actual use, then prioritize region-first navigation and a compact nearby-conditions view. Continue scientific validation as a separate workstream.

---



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


## 2026-11-20 | Live IOOS USF Sam ETOPO join completed and reviewed

Successful workflow [44740669528](https://github.com/markeetox/LUPITA/actions/runs/44740669528); artifact ID 14631270203, ZIP SHA-256 `42f2ab838d22946e72f14bbc27874cb28e028fb88cffe06bfe4d66d04e560022`. Job logs confirm the prior inventory artifact (run 44737352618) downloaded with matching SHA, ETOPO_2022_v1_30s subset request completed, join completed, and all four output files uploaded.

The join contains 201,645 coordinate-bearing rows and 2,387 profiles. All point coordinates mapped to ETOPO ocean-class cells. Only 72,426 rows contain finite depth and temperature; 129,219 rows lack those values. For the usable observations, primary temperature QARTOD = 72,382 PASS, 43 SUSPECT, 1 FAIL. Finite-row signed separation range -4.852 to 143.988m, median 20.044m, mean 25.234m. 1,062 negative separations (1,061 PASS, 1 SUSPECT) are preserved and excluded from nonnegative near-bottom sensitivity. Nearest grid-center offset median ~351m, max ~618m.

Nonnegative separation bands: 0–5m = 8,446 observations / 2,180 profiles (8,445 PASS rows); 0–10m = 17,261 / 2,212 (17,260 PASS); 0–20m = 35,075 / 2,250 (35,074 PASS); 0–50m = 63,765 / 2,298 (63,743 PASS, 2,297 profiles). These are nested observations in one deployment, not independent samples or an adopted bottom-proximity cutoff. ETOPO EGM2008 versus sea-surface-referenced glider depth is not established as vertically equivalent; positions are interpolated. Pressure remains excluded. The deployment is outside the current Copernicus Gulf pilot box, so no direct pairing or accuracy validation yet.

Detected NaN summary defect in initial artifact: missing depth/temperature rows were serialized as NaN and contaminated JSON median fields. Finite-row values above were independently calculated from the downloaded joined CSV. Fixed the script to retain coordinate rows but calculate separations only for finite depth+temperature, report finite counts/QC counts, and calculate finite medians; added regression test. First CI run [44741683803](https://github.com/markeetox/LUPITA/actions/runs/44741683803) passed 323 tests and failed one existing longitude assertion because -83.3° converts to 276.7°, not 275°; corrected assertion. Python CI reruns [44741719287](https://github.com/markeetox/LUPITA/actions/runs/44741719287) and [44741832591](https://github.com/markeetox/LUPITA/actions/runs/44741832591) were pending at time of this entry. No Copernicus pairing, species/scoring changes, ingestion changes, or production behavior changes.


## 2026-11-20 | IOOS ETOPO missing-value fix and test suite passed

Full Python CI passed in [run 44741832591](https://github.com/markeetox/LUPITA/actions/runs/44741832591) after fixing the longitude test expectation and adding regression coverage for missing depth/temperature rows. The test confirms position rows remain in the join, missing physical observations produce null separation, finite-only median is calculated correctly, and profile-level counts distinguish joined rows from usable temperature/depth observations. The first failed CI run [44741683803](https://github.com/markeetox/LUPITA/actions/runs/44741683803) had 323 passing tests and one failure in an existing test assertion (expected 275 instead of 276.7 for -83.3° converted to 0–360). The corrected complete test run is green. No production changes.


## 2026-11-20 | Added salinity acquisition for potential-temperature conversion

Reviewed official Copernicus documentation: `bottomT` is sea-floor potential temperature, standard name `sea_water_potential_temperature_at_sea_floor`, and is independent of the vertical depth axis ([Copernicus Help Center](https://help.marine.copernicus.eu/en/articles/4877597-depth-selection-when-downloading-the-bottomt-variable); [GLOBAL_MULTIYEAR_PHY_001_030 product](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/description)). The daily dataset covers the 2024 deployment period; P1D-m denotes daily means ([dataset services](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/services); [dataset nomenclature](https://help.marine.copernicus.eu/en/articles/6820094-how-copernicus-marine-data-nomenclature-is-defined)).

The IOOS dataset metadata exposes `salinity` as calculated practical salinity with a `qartod_salinity_primary_flag` and other salinity QC flags. The original inventory did not request salinity. Updated `scripts/download_ioos_glider_profile_inventory.py` to include salinity and all `qartod_salinity_*` fields, include salinity and its primary QC in nonmissing counts, and document that no conversion is performed by the inventory. Added a test asserting salinity and salinity-QC inclusion. CI runs [44742300164](https://github.com/markeetox/LUPITA/actions/runs/44742300164) and [44742308838](https://github.com/markeetox/LUPITA/actions/runs/44742308838) were pending when this entry was written. No salinity data downloaded yet.

Next: after CI passes, rerun manual IOOS inventory; inspect salinity completeness/QC; resolve whether sea pressure can be derived from CTD depth and latitude without using the unresolved pressure field; evaluate TEOS-10 conversion from in-situ temperature to potential temperature; then extract West Florida Copernicus daily `bottomT` and compare with time-matched near-bottom observations across multiple separation bands. This glider deployment is outside the existing Gulf pilot region. No production changes.

## 2026-11-20 | Salinity inventory extension passed CI

Both salinity-related Python CI runs completed successfully: [44742300164](https://github.com/markeetox/LUPITA/actions/runs/44742300164), job 136308729869, and [44742308838](https://github.com/markeetox/LUPITA/actions/runs/44742308838), job 136308758566. Each job completed the full test suite successfully. The downloader extension to request calculated practical salinity, all available `qartod_salinity_*` fields, and salinity/primary-QC nonmissing counts is now CI-validated.

This does not mean salinity observations have been retrieved. Next action is a manual rerun of [the IOOS USF Sam profile inventory workflow](https://github.com/markeetox/LUPITA/actions/workflows/ioos-usf-sam-profile-inventory.yml), followed by inspection of salinity completeness, QARTOD distributions, and row-level alignment with temperature/depth. The pressure metadata conflict remains unresolved; no pressure-based conversion, TEOS-10 conversion, Copernicus pairing, or production change has occurred.


## 2026-11-21 | Salinity inventory retrieved and QC screened

Manual IOOS inventory run [44956578185](https://github.com/markeetox/LUPITA/actions/runs/44956578185) succeeded. Job 137005919171 succeeded. Downloaded artifact 14727950637, ZIP SHA-256 d38d19b3e87d54629c6bacf181af044d439c5ad21cee99c05be32c4c17e9ebd8. Refreshed inventory: 201,645 rows, 2,387 profile IDs, WMO 4801942. Finite depth+temperature: 72,426; finite salinity: 72,406, leaving 20 rows without salinity. Practical salinity range 35.333313–36.759933, median 36.508830.

Salinity primary QARTOD counts: PASS 72,145; SUSPECT 237; FAIL 24. Temperature primary QC: PASS 72,382; SUSPECT 43; FAIL 1. Same-row intersection among finite depth+temperature+salinity observations: both primary flags PASS 72,138; temperature PASS / salinity SUSPECT 202; temperature PASS / salinity FAIL 22; temperature SUSPECT / salinity PASS 7; both SUSPECT 35; temperature SUSPECT / salinity FAIL 1; both FAIL 1. Salinity spike flag includes 4,771 NOT_EVALUATED; not treated as PASS. All counts are row counts, nested in a single 2,387-profile deployment.

Metadata confirms salinity is calculated practical salinity (sea_water_practical_salinity, unit 1). Pressure remains ambiguous: metadata declares bar but comment says multiplied by 10 to dbar. Do not use raw pressure without resolving this. Candidate TEOS-10 conversion will derive sea pressure from CTD depth and latitude, with explicit assumptions and sensitivity, and begin with the 72,138 rows where both primary temperature and salinity QC pass. Preserve all raw fields and QC flags. No conversion, Copernicus pairing, accuracy claims, or production changes yet.


## 2026-11-21 | TEOS-10 input provenance gate

Checked the exact IOOS deployment metadata: CTD is Sea-Bird Scientific GPCTD serial 9013, calibration date 2012-07-08, factory_calibrated=True, user_calibrated=False; source references a merged DBA file. Published temperature metadata does not identify ITS-90 vs IPTS-68. Since GSW TEOS-10 conversion expects ITS-90, instrument model alone is insufficient to assert the scale. Pressure metadata conflict also remains: declared units bar, comment says multiply by 10 to dbar. Do not convert yet. Obtain source DBA/CTD processing or calibration records; if pressure remains unclear, test a separately labelled GSW p_from_z(-depth,lat) estimate as sensitivity while retaining raw pressure. Docs: [IOOS metadata](https://gliders.ioos.us/erddap/info/usf-sam-20240216T0000/index.html), [GSW-Python conversions](https://teos-10.github.io/GSW-Python/conversions.html). No production changes.


## 2026-11-21 | USF Sam CTD source provenance investigated

Confirmed public ERDDAP lineage: merged DBA path 0000339.dba; example source SBD file usf-sam-2024-046-1-344-sbd(02140344); processing script dba_to_ngdac_profile_nc.py; dataset processing_level Level 0 and product_version 0.0. Public metadata does not identify the temperature scale. Pressure metadata is contradictory (declares bar, comment says multiply by 10 to dbar). IOOS NGDAC states original provider files are archived but not public in original form; GANDALF states raw data access is password-controlled and limited to the PIs. Generic GPCTD docs do not establish the exact configuration of serial 9013. Added docs/IOOS_USF_SAM_CTD_PROVENANCE_REQUEST_2026-11-21.md documenting the evidence needed from USF/GCOOS. Hold TEOS-10 conversion pending temperature-scale evidence and pressure clarification/sensitivity design. No Copernicus comparison or production changes.


## 2026-11-21 | GPCTD manual and pressure/depth consistency

Sea-Bird GPCTD manual revision 004 specifies that engineering OutputFormat 0/1 outputs temperature in ITS-90 °C and pressure in dbar; OutputFormat 2 outputs raw counts. Deployment OutputFormat is not published, so ITS-90 remains unconfirmed for this dataset. Row-level pressure/depth check over 72,426 pairs: correlation 0.9999999964; mean ratio 1.006743; median ratio 1.006735. This is physically consistent with pressure in dbar, not bar, and matches the metadata comment describing multiplication by 10 from bar to dbar. Likely stale ERDDAP units attribute; preserve it as published and obtain provider confirmation. Updated provenance request document with exact confirmation items. No TEOS-10 conversion, Copernicus pairing or production changes.


## 2026-11-21 | Alternative in-situ validation datasets screened

Identified NOAA OMAO Nancy Foster CTD accession 0283250 as the first alternative to inspect: SBE-9 originator data with documented t090C ITS-90, prDM dbar, sal00, altimeter and bottom-depth fields; raw suite requires processing/QC audit and covers western Gulf. Identified SEFSC SEFIS CTD 2010–2024 with explicit ITS-90, psi pressure, PSU salinity and 1-metre bins; station/time/QC/bottom-proximity limitations need review and latest release check. Also recorded SEFSC bottom-longline CTD_PROC_CAST, Argo delayed-mode and CCHDO/GO-SHIP as secondary routes. See docs/ALTERNATIVE_IN_SITU_VALIDATION_DATASETS_2026-11-21.md. No alternative observations downloaded, no TEOS-10 or Copernicus comparison, no production changes.


## 2026-11-21 | NOAA candidate depth audit and reprioritization

Checked NOAA Nancy Foster accession 0283250 against the published cruise report: casts were deep-water stations around 1,043–1,862 m, so this is not appropriate as the primary shelf validation sample. Identified a stronger direct near-bottom NOAA source at Pulley Ridge / Northern and Southern Dry Tortugas: published study documents near-bottom temperature recorders 0.5 m above seafloor at sites with 54.5, 66.7 and 69.5 m bottom depths, with 27–34 months of hourly records. Related accessions 0181331 (ADCP), 0190271 (temperature logger series), 0190533 (CTD casts) must be inspected separately to identify exact raw near-bottom logger file. Also identified SEAMAP 0131259 (1,761 observations, Gulf CTD 2009–2015) for broader regional inventory. See docs/ALTERNATIVE_IN_SITU_VALIDATION_DATASETS_2026-11-21.md. No source files retrieved, no conversion/matchup, no production changes.


## 2026-11-21 | NOAA archive roles clarified and access probe added

Confirmed 0181331 is the direct bottom-temperature candidate: moored ADCP time series explicitly includes hourly bottom temperature at three southwest Florida shelf sites. 0190533 is CTD cast profiles at those mooring sites from 2013/2014; processing details are in file headers. 0190271 is a separate lower Florida Keys shallow (0–10 m) and deep (20–30 m) shelf temperature-logger series, not assumed to be the near-bottom mooring sensor record. Added scripts/probe_noaa_archive_access.py and manual workflow .github/workflows/noaa-archive-access-probe.yml to probe NCEI/legacy NODC endpoints and directory listings for 0181331, 0190271, 0190533 and SEAMAP 0131259. It records status/redirect/content-type/previews only, not payloads. Awaiting user-dispatched workflow; no data retrieved or production changes.


## Legacy archive access result and nested-listing probe | 2026-11-21

Manual workflow [44958887218](https://github.com/markeetox/LUPITA/actions/runs/44958887218) completed successfully and produced artifact `noaa-archive-access-probe` (ID 14728881660; expires 2026-12-05). The report was downloaded and inspected.

The modern NCEI routes remain unavailable or unstable: accession landing pages for 0181331 and 0190271 returned HTTP 503; their modern download routes returned timeout/503. The 0190533 landing and download routes timed out. SEAMAP 0131259 landing timed out and its OAS download returned HTTP 503.

Crucially, all three legacy NODC parent directory listings returned HTTP 206 with complete 1,114-byte HTML indexes. They expose an `1.1/` data directory and an accession XML metadata file:
- 0181331: `https://www.nodc.noaa.gov/archive/arc0139/0181331/1.1/` and `0181331.1.1.xml`
- 0190271: `https://www.nodc.noaa.gov/archive/arc0139/0190271/1.1/` and `0190271.1.1.xml`
- 0190533: `https://www.nodc.noaa.gov/archive/arc0141/0190533/1.1/` and `0190533.1.1.xml`

The 206 responses confirm that legacy directory listings are reachable, but no data files have yet been listed or downloaded. Expanded `scripts/probe_noaa_archive_access.py` to probe each nested `1.1/` directory and XML metadata header using bounded HTTP Range requests; it remains read-only and does not retrieve archive payloads. Commit: 9720d80122387f5f55365c6fadd40018f3b220dd. Next: manually rerun the same workflow and inspect nested file names, sizes, and metadata. Prioritize identifying the actual bottom-temperature logger series within 0181331; keep 0190271 and 0190533 distinct. No Copernicus matchups, conversion, species/scoring, ingestion or production changes.


## Legacy archive discovery update | 2026-11-21

Manual probe run [44962696916](https://github.com/markeetox/LUPITA/actions/runs/44962696916) succeeded; artifact ID 14730466940 (expires 2026-12-05). The artifact confirms that legacy NODC 1.1/ directories and full accession manifests can be read with HTTP Range requests (HTTP 206). The modern NCEI landing/download routes remain unavailable (503/timeouts).

Manifest facts:
- **0181331 (ADCP bottom-temperature candidate):** 42 files, 35,389,302 bytes; manifest 0181331.1.1.xml is 54,374 bytes. The 1.1/ root lists NCEI-Readme.txt, about/, and data/.
- **0190271 (separate temperature-logger series):** 18 files, 8,027,615 bytes; manifest is 22,051 bytes. Its 1.1/ root likewise lists NCEI-Readme.txt, about/, and data/.
- **0190533 (separate CTD profile archive):** 95 files, 48,033,891 bytes; manifest is 121,058 bytes. Its 1.1/ root likewise lists NCEI-Readme.txt, about/, and data/.

These are archive inventory facts, not yet sensor-level metadata or evidence of near-bottom suitability. No scientific data payloads were downloaded. The first probe's nested root listing was not the actual data/ listing; therefore the next probe now checks each accession's 1.1/data/, 1.1/about/, and README, and retrieves complete manifest XML (bounded at 200 KB) so we can identify exact data filenames, sizes, formats, and checksums before downloading anything. Script update commit: 59ab59318e014034e1b6c5148606a32f0f06ffb7. Next: manually rerun the NOAA archive probe workflow at https://github.com/markeetox/LUPITA/actions/workflows/noaa-archive-access-probe.yml. Prioritize 0181331 and keep 0190271/0190533 distinct. No Copernicus matchup, temperature conversion, species/scoring, ingestion or production changes.


## Legacy archive probe follow-up | 2026-11-22

Probe run [44965485719](https://github.com/markeetox/LUPITA/actions/runs/44965485719) succeeded; artifact ID 14730589826 (expires 2026-12-06; SHA-256 `c7f74a5d1a22bd1a2cdb74767d43f3b5eeddc06e4716203536a61e5ef38b6fc9`). The modern NCEI endpoints timed out again. Legacy NODC listings are reachable for all three accessions. The probe confirmed each `1.1/data/` directory contains `0-data/`, and each `1.1/about/` directory contains accession documentation. The generic NCEI README explains `0-data/` contains originator files unmodified; this is archive structure documentation, not proof of the data formats or sensor fields. The current probe had only listed `data/`, not descended into `data/0-data/`, and the JSON stored only a 3,000-character manifest preview despite retrieving full manifests. No scientific payloads downloaded. Script updated in commit `588668c762b65b2709e907ca995d54e786990d25` to inspect `0-data/`, fetch accession journals, and retain complete XML manifest text in the temporary artifact. Next action: manually rerun [the NOAA archive probe workflow](https://github.com/markeetox/LUPITA/actions/workflows/noaa-archive-access-probe.yml), then inspect exact original filenames and journal provenance before choosing a small 0181331 download. Keep 0190271 and 0190533 separate. No Copernicus matchup, conversion, scoring, ingestion, or production changes.


## NOAA Pulley Ridge archive discovery | 2026-11-22

Run [45030930943](https://github.com/markeetox/LUPITA/actions/runs/45030930943) succeeded (artifact 14757504132). Complete legacy NODC manifests and `data/0-data/` listings identify the actual files: accession 0181331 has nine 2012–2015 ASCII ADCP time-series files and a data documentation PDF; 0190271 has one 7.47 MB Florida Keys temperature-logger CSV, documentation PDF and separate coordinate text; 0190533 has 18 processed CTD CNVs, six headers, six XMLCON configuration files and documentation PDF. Journals confirm archive copies were made from provider submissions; they do not themselves establish sensor calibration or near-bottom placement. Added checksum-verified targeted download script and manual workflow (commits 677d336aba0f73f4cf461a7e5b183ca471ab1e4d, fccac6919722c4342ef5e8c7614d50986f0c1f38). It downloads selected source files to a 14-day Actions artifact and verifies byte size/SHA-256 against NOAA manifests; no raw data committed. Next: manually run [NOAA Pulley Ridge Targeted Source Download](https://github.com/markeetox/LUPITA/actions/workflows/noaa-pulley-ridge-source-download.yml), then inspect docs/headers and qualify each source separately. No Copernicus matchup, conversion, species/scoring, ingestion or production changes.


## 2026-11-22: NOAA Pulley Ridge sample inspection
- Verified targeted artifact from run [45032750496](https://github.com/markeetox/LUPITA/actions/runs/45032750496), ID 14757849720, 6,752,796 bytes, SHA-256 `33b568828bfc0ce3afa3ab3547f02c4c7474a859616e14491ba02e2f2a8d016c`; all selected source files passed manifest size/SHA-256 checks.
- Inspected ADCP documentation and nine hourly ASCII deployments. Confirmed `bottom_temperature` and `bottom_40hr_low_pass_temperature` columns; 69,687 finite raw hourly rows; 15.86–28.48°C. Sensor is an internal ADCP thermistor, precision ±0.4°C, resolution 0.01°C. ADCP documentation says bottom-mounted, transducers ~0.5m above seabed, and data preliminary. Treat as promising but not gold-standard until sensor thermal coupling/calibration limitations addressed.
- Inspected CTD documentation and headers. Six unique casts across three mooring sites/two cruises, each represented as WS/dWS/uWS variants (18 files are not 18 independent casts). Sea-Bird SBE9plus; final processed output; ITS-90 temperature, Digiquartz dbar pressure, salt-water depth, potential temperature, GPS position and UTC. WS profile maximum depths 48.68–67.553m. Next parse cast identity and down/upcast, then ETOPO bottom-clearance screening.
- Inspected logger documentation/data: 216,929 records, deep shelf 66,044 (20–30m), shallow shelf 150,885 (0–10m), HOBO U22-001, 5/10-minute cadence, 20.222–31.74°C; sensor bottom clearance unspecified. Supplementary context only.
- Updated alternative dataset and project continuity docs. No Copernicus matchup, TEOS-10 conversion, scoring, ingestion or production changes.
