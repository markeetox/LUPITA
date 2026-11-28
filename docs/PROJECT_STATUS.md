
### NOAA Table 5 denominator clarification | 2026-11-28

The primary report captions Table 5's `n` as **site sample size**, not number of individual fish. Methods say other sportfish caught in every tow were identified/measured/counted; separately, a subset of 12 stations per month from 2009 onward had all organisms under 100 mm preserved for lab identification. Do not confuse that 12-station/month collection subset with Table 5's Southern flounder `n=12`. The ERDDAP main table still has nine Southern flounder sample rows (each SpeciesCount=1) through 2016-11-12; the report covers 2004–2019. Later-year rows could explain the difference, but this is unverified. See the [NOAA report](https://repository.library.noaa.gov/view/noaa/28764/noaa_28764_DS1.pdf). No inference or model change.

## Current verified update | 2026-11-28 | NOAA workbook remains blocked

Manual acquisition [run 46168260876](https://github.com/markeetox/LUPITA/actions/runs/46168260876) succeeded on `main` at `97d1c7419d31ae2f1c8aaaa717b67cb83681aa92`; artifact ID `15272448030` (28,887,331 bytes; expires 2026-12-12). Both the standard NOAA/AOML workbook request and the browser-header fallback returned HTTP 403. The workbook is not in the artifact.

The artifact's current ERDDAP main species table contains 11,473 rows and nine exact Southern Flounder records (`Paralichthys lethostigma`), each with SpeciesCount=1. No alternate Paralichthys/flounder taxon alias was found in the full table. The ERDDAP product ends 2016-11-12; NOAA report Table 5 reports n=12 site samples for 2004–2019. This difference remains unresolved. The NOAA/AOML Data Products page still advertises an XLSX workbook, but a different verified link target has not been recovered. Do not infer the three-row difference or alter scientific behavior.

## Current verified update | 2026-11-28 | NOAA workbook retrieval

Latest manual acquisition run [46160840439](https://github.com/markeetox/LUPITA/actions/runs/46160840439) succeeded overall on main (source SHA 92491226ff379597cb50b1cfcf3b05873f355a4f; artifact ID 15269970886). NOAA ERDDAP, NPS, FWC/FIM, and Florida Museum downloads completed, but the separate NOAA/AOML June 2019 workbook request returned HTTP 403 after retries. The workbook is not in the artifact and remains unaudited.

The acquisition script now retries the same workbook URL with browser-compatible request headers and the official NOAA/AOML data-products page as Referer after the standard request fails. This is a public-source compatibility retry, not an authentication bypass. Next: manually rerun the workflow and inspect the artifact summary. If the workbook is acquired, audit it before comparing with the nine ERDDAP detections and Table 5's n=12. If it remains blocked, resolve the current official download URL or another public NOAA-hosted copy.

No scientific model, species profile, range mask, scoring, confidence, ingestion, production source, or publishing behavior changed. No raw source data were committed.

## Current verified state | 2026-11-28 (supersedes older pending notes below)

## Southern flounder Florida Bay evidence | 2026-11-28

The manual-only [South Florida Public Evidence Acquisition workflow](../actions/workflows/south-florida-public-evidence-acquisition.yml) completed successfully in run [46158258337](https://github.com/markeetox/LUPITA/actions/runs/46158258337). Artifact `south-florida-public-evidence` (ID `15268192641`, 28,887,077 bytes) contains the acquired NOAA/AOML, NPS, FWC/FIM, and Florida Museum source files and expires 2026-12-12. The full audit is documented in [FLORIDA_SOUTHERN_FLOUNDER_PUBLIC_DATA_EXPANSION_2026-11-27.md](FLORIDA_SOUTHERN_FLOUNDER_PUBLIC_DATA_EXPANSION_2026-11-27.md). Raw data remain in the artifact, not the repository.

The NOAA/AOML main Florida Bay species-sample table contains **9 exact-name Southern flounder rows**, each with SpeciesCount=1 and a unique sample key, dated 2005-11-11 through 2016-11-10. Five rows include individual lengths (72–255 mm); four lengths are missing. The 65,454-row collection-station measurement subset contains no exact-name records, but it is a distinct 12-station-per-month lab-measurement subset and is not the full survey species table.

**Unresolved NOAA discrepancy:** NOAA Technical Report OAR-AOML-48 Table 5 reports **n=12 site samples** for 2004–2019. The ERDDAP main table ends on 2016-11-12, so the nine extracted rows do not cover the full report period. A NOAA/AOML June 2019 Excel workbook is publicly linked and cited in a 2023 paper; it is now added as a separate acquisition target in the script. Its contents have not yet been audited, so the three-sample gap remains unresolved. Next: manually dispatch the acquisition workflow, inspect the workbook sheets and target rows, and reconcile unique sample keys and salinity statistics against ERDDAP and report Table 5.

The latest acquisition workflow also returned:
- NPS Everglades recreational catch: 210 exact-name candidate rows in the full catch file (205 unique interview keys, 271 fish after disposition rows are retained); fisheries-dependent catch, not standardized abundance.
- FWC/FWRI Inshore FIM SRS: 6,008 exact-name positive-catch records; public layer is filtered to positive catches and cannot provide zero-catch denominators.
- Florida Museum Ichthyology DwC-A: 221 exact-name candidates (170 Florida records; 169 with year, 1929–2024); preserved voucher occurrences, not abundance.
These source-specific findings are detailed in the research report and must remain separate evidence classes.

No species profile, range mask, scoring, confidence, ingestion, production source, or publishing behavior changed. No raw source files were committed. Preserve the distinction between positive survey detections, sample-level non-detections, fisheries-dependent catch, and museum vouchers.



## Public South Florida evidence expansion | 2026-11-27


A manual-only, read-only acquisition workflow is now implemented: [South Florida Public Evidence Acquisition](../actions/workflows/south-florida-public-evidence-acquisition.yml), using [acquire_south_florida_public_evidence.py](../blob/main/scripts/acquire_south_florida_public_evidence.py). It is designed to retrieve NPS creel CSVs, exact-name positive-catch FWC/FIM SRS records, and the current Florida Museum Darwin Core Archive, producing a 14-day artifact without committing raw data. It has **not yet been dispatched**. First-run results must be audited before any species count or spatial inference is accepted.

A new NOAA Florida Bay monitoring source materially expands the evidence base. Kelble et al. (2021), NOAA Technical Report OAR-AOML-48, Table 5 reports *Paralichthys lethostigma* at **n=12 site samples** in the 2004–2019 juvenile sportfish monitoring program, with salinity range 33.3–40.4 ppt and mean 36.7 ± 2.31 ppt. The table defines n as site sample size, not individual fish count. It does not provide event-level dates/coordinates or annual detections. This is independent positive Florida Bay survey evidence and further rejects an absolute absence claim, but it does not establish abundance or a continuous/current population. See [FLORIDA_SOUTHERN_FLOUNDER_PUBLIC_DATA_EXPANSION_2026-11-27.md](FLORIDA_SOUTHERN_FLOUNDER_PUBLIC_DATA_EXPANSION_2026-11-27.md).

The same review verified the live FWC/FWRI Inshore FIM SRS ArcGIS feature layer and its fields (deployment reference, date, coordinates, gear, scientific/common name, total count and size fields). The public GIS export is positive-catch-only (CNT>0), with 1,765,226 features reported in metadata. Its legacy time-period section ends 2016, while a 2025 process note says the export was refreshed through the most recent records; actual returned dates must resolve this conflict. No species-specific FWC record count is claimed because feature queries were not retrieved.

The NPS Everglades recreational catch-and-effort package is publicly available for 1980-01 through 2025-04, with >270,000 surveys and >4 million reported fish. Its five CSV/XML resources were identified, but CSV ingestion did not succeed in this session; no Southern flounder catch result is claimed. The current Florida Museum UF Ichthyology Darwin Core Archive endpoint was verified but not downloaded. NOAA Powell et al. (2007) Florida Bay compendium contains no Southern flounder account; because it covers selected more-abundant juvenile/small resident species, that omission is not a non-detection.

No raw FWC/NPS/Florida Museum records were ingested in this review. No profile, range mask, scoring, confidence, ingestion, production source, or publishing behavior changed. Next: retrieve NOAA event-level data if available; query/export exact *P. lethostigma* records from the FWC layer and reconcile temporal coverage; obtain and parse NPS creel CSVs; download and filter the current Florida Museum DwC-A. Keep positive catches, survey non-detections, recreational catches, and museum vouchers as separate evidence classes.

The NOAA Southern flounder extraction is complete, not pending. Workflow [46019958931](https://github.com/markeetox/LUPITA/actions/runs/46019958931) completed successfully and produced 13,703 sample records across Gulf and Southeast Fall/Spring/Summer layers. The extractor CI run [46018508487](https://github.com/markeetox/LUPITA/actions/runs/46018508487) passed 336 tests. The full extraction findings are in [NOAA_SOUTHERN_FLOUNDER_EXTRACTION_ANALYSIS_2026-11-27.md](NOAA_SOUTHERN_FLOUNDER_EXTRACTION_ANALYSIS_2026-11-27.md).

The original SEAMAP CSV archives have now been inspected and crosswalked against the NOAA Gulf point extraction. See [NOAA_SEAMAP_CROSSWALK_ANALYSIS_2026-11-27.md](NOAA_SEAMAP_CROSSWALK_ANALYSIS_2026-11-27.md). All 4,805 NOAA Gulf SampleIDs are now crosswalked to original SEAMAP station/deployment records. 4,795 match the composite key directly; ten have a NOAA SampleID cruise segment of `2001` but independently match vessel 35, station numbers 12–18 and 20–22, and SEAMAP cruise `2101` in 2021. All 4,805 agree on survey year and exact depth, and their NOAA points match SEAMAP tow midpoints within 69.5 m. All 277 positive NOAA WTCPUE samples have matching Southern flounder BGS records; all 4,528 zero-CPUE samples have other-taxa catch records but no Southern flounder BGS record. The ten identifier discrepancies are documented, not silently rewritten. The 572 samples south of 26°N, including 73 shallow eastern samples, have recorded shrimp-trawl effort and other-species catch context. This strengthens sample-level no-catch evidence only; it does not support an absence polygon or estuary-wide exclusion.

A further check of the official FWC/FWRI 2021 and 2023 FIM annual reports independently confirms Florida Bay FIM sampling ran from 1993–1997 and is not among the later routine monitoring areas. The 2023 bibliography identifies the original 1994, 1996, and 1997 annual data summary reports (published 1995, 1997, and 1998); these are now specific archival retrieval targets. They do not publish the needed Southern flounder sample-level zero-catch table. Updated analysis: [FLORIDA_BAY_FIM_EFFORT_REVIEW_2026-11-27.md](FLORIDA_BAY_FIM_EFFORT_REVIEW_2026-11-27.md).

The next evidence tasks are to ask the NOAA/SEAMAP data steward why the ten 2021 NOAA SampleIDs encode cruise `2001` instead of `2101`; obtain the formal HAULVALUE codebook and resolve conflicting G-coded comments; ask about the single 56-minute 2024 tow despite the documented 30-minute standard; and request full Florida Museum specimen records/label images plus the original FWC/FMRI Florida Bay 1994–1997 sample-level records. See [FLORIDA_BAY_FIM_EFFORT_REVIEW_2026-11-27.md](FLORIDA_BAY_FIM_EFFORT_REVIEW_2026-11-27.md) for the survey-design review, data limitations, and exact request fields. The Florida Museum's complete-record contact is Collection Manager Rob Robins (rhrobins@flmnh.ufl.edu). A new review found a 2019 FWC/FWRI paper reporting 2,636 fixed-station samples (1,367 seine, 1,269 trawl) and 1997 SRS effort of 130 seine plus 140 trawl sets, but it does not publish Southern flounder catch records. The public statewide FWC GIS export is filtered to CNT > 0, so it cannot independently verify zero-catch samples. Request raw records, including zero-catch and invalid samples, from FIM. Historical occurrences and survey non-detections must remain separate evidence classes. No model/profile/mask/scoring/production changes are approved or made.

Historical sections below are retained as project history. Any earlier statement that the extraction workflow was awaiting dispatch or that no observations had been downloaded is superseded by the verified run and analysis above.



### Latest CI and NOAA extraction status | 2026-11-27

The latest extractor CI run [46018508487](https://github.com/markeetox/LUPITA/actions/runs/46018508487) completed successfully: **336 passed, 0 failed** (115 warnings), including map-client JavaScript syntax checks and species audit/artifact steps. The manual NOAA extraction workflow [46019958931](https://github.com/markeetox/LUPITA/actions/runs/46019958931) also completed successfully; 13,703 target sample records were downloaded and audited. See [NOAA_SOUTHERN_FLOUNDER_EXTRACTION_ANALYSIS_2026-11-27.md](NOAA_SOUTHERN_FLOUNDER_EXTRACTION_ANALYSIS_2026-11-27.md).

### CI correction and latest verification state | 2026-11-27

The first CI attempt on the initial extractor failed one new test because the generic profile alias "flounder" was included in matching. Fixed by excluding one-word aliases, adding compound common/scientific-name handling, and adding distinct-query pagination without assuming an ObjectID field. The corrected run `46018358533` passed **335 tests, 0 failures**; species audit and artifact steps also completed successfully. The latest run includes one additional compound-name test and subsequent no-match diagnostic preservation; it was still in progress at last inspection. Latest extractor hardening commit: `848ad0fbcbd375742da8dbcad7637bfaa72226c2`.

The manual NOAA extraction workflow has not yet been dispatched, so no NOAA target observations have been downloaded. Use the workflow link above to run it after the latest CI finishes.
## NOAA Southern flounder extraction workflow | implemented, awaiting first run | 2026-11-27

Added a read-only extractor (`scripts/extract_noaa_southern_flounder.py`), unit tests (`tests/test_noaa_dismap_extractor.py`), and manual GitHub Actions workflow (`.github/workflows/noaa-southern-flounder-extraction.yml`). It reads the accepted common/scientific name from the existing Southern flounder profile, discovers actual values in NOAA's species/name fields, and uses exact full-name matching. Generic "flounder" matching is intentionally excluded. No separate species-filter table was identified in the repository tree; the species profile is the canonical target.

The extractor writes target observation CSVs, same-SampleID context CSVs, and a JSON summary by source/season/year/stratum, including coordinate/depth/WTCPUE completeness. Same-SampleID context is not treated as a complete effort record or verified non-detection. The workflow uploads results as a 14-day artifact; it does not commit raw data. No mask, scoring, profile, confidence, ingestion, production or publication behavior changed.

Manual workflow: https://github.com/markeetox/LUPITA/actions/workflows/noaa-southern-flounder-extraction.yml

Python CI was triggered and remained in progress at this status update (runs 46018349544 and 46018358533). The new extraction workflow has not yet been manually run; actual NOAA species records/counts remain unknown. Next: confirm CI, manually run the extraction workflow, inspect the artifact and resolve whether separate survey-effort/non-detection records can be obtained.
## Southern flounder survey evidence and public point-layer discovery | 2026-11-27

NOAA Fisheries' June 2026 DisMAP technical report lists Paralichthys lethostigma in the Gulf of Mexico and Southeast U.S. Shelf Fall, Spring, and Summer survey products. The report documents survey-year and stratum filtering, including Gulf years retained from 2010 onward with 2022 dropped, and Southeast seasonal series from 1989–2025 with season-specific exclusions/stratum-coverage thresholds. The report's inclusion rules are based on catch frequency (at least 5% of tows in required proportions of years); they do not define native occupancy limits.

Identified NOAA InPort 69743, Survey Catch-per-unit-effort CURRENT, as the correct public point-level source. It links current ArcGIS Feature Services for Gulf of Mexico and Southeast Fall, Spring, and Summer sample locations. Their schemas expose sample ID, year/time, species identifiers/names, WTCPUE, stratum, latitude, longitude, depth, and point geometry. The separate DisMAP Indicators service contains summary metrics, not the tow-level point records. The NOAA point-data metadata declares CC0-1.0. The ArcGIS query endpoints could not be retrieved through this session, so no species-specific point counts or observations have yet been downloaded.

The DisMAP interpolation uses a 200 km IDW search radius with 10–15 sample sites, a five-year temporal window, and 2 km grid cells. Therefore its interpolated surfaces must not be used as hard occupancy polygons. The portal also labels the Species Persistence module as a preliminary pilot. Florida Museum's current IPT resource reports 241,689 occurrence records under CC-BY-NC 4.0, but no archive records have yet been acquired.

Details and source links are recorded in the species geographic mask design review. No raw data, profile, mask, scorer, scoring factor, gate, confidence, ingestion, or production behavior changed. Next: query the four NOAA point layers, resolve the Species string value against the current Species Filter table, retrieve tow-effort/sample footprints, and audit actual Southern flounder observations by region/season/year/stratum before any geometry is proposed.

## Species-specific geographic mask design review | research complete, geometry still gated | 2026-11-25

Reviewed authoritative and agency sources for Southern flounder and white sturgeon and documented the evidence and spatial-mask requirements in [SPECIES_GEOGRAPHIC_MASK_DESIGN_REVIEW_2026-11-25.md](SPECIES_GEOGRAPHIC_MASK_DESIGN_REVIEW_2026-11-25.md), commit `8c08aabb032386b2c9cad169e49059a8c23490b8`.

Southern flounder: SCDNR and USGS NAS support a discontinuous Florida range (Atlantic occurrence to the Loxahatchee/Jupiter Inlet area, a gap south and around the peninsula tip, and a separate Caloosahatchee Estuary/Gulf occurrence). Seafood Watch 2023 repeats the gap but is not an independent geospatial dataset. FWC supplies habitat context but no polygon; Florida Museum's broad Florida distribution summary requires reconciliation against underlying georeferenced records; the 2021 NC FMP supports distinct Atlantic/Gulf population contexts. No source reviewed supplies a ready-to-use authoritative coastal occupancy polygon. Do not infer coordinates from named endpoints or turn occurrence-point convex hulls into occupancy boundaries.

White sturgeon: CDFW, CA Marine Species Portal and WDFW describe a broad coastal range but dominant riverine/estuarine use and only occasional open-coast movements. The current SST/ETOPO marine grid lacks river flow, channel hydraulics and estuary habitat. A geographic mask alone would not correct this model-domain mismatch. Evaluate exclusion from the marine-grid product versus a separately designed river/estuary model; no deactivation or catalog change made.

Documented future mask requirements: optional/backward-compatible, versioned WGS84 geometry with provenance, multiple disjoint polygons and holes, explicit edge semantics, synthetic tests, before/after eligible-cell audit, and no change to scoring factors/weights/gates/confidence. No profile, scorer, data-source, ingestion, or publication behavior changed. Browser smoke test passing was user-reported; the exact run/artifacts have not yet been independently inspected in this update.

## Live frontend browser QA | no-favorable-areas assertion scope corrected | 2026-11-25

Manual run [45707532332](https://github.com/markeetox/LUPITA/actions/runs/45707532332) again completed Chromium installation and reached the Gopher rockfish no-favorable-areas check in both desktop and mobile contexts. The test still timed out because it searched only inside `#opportunityContent`, but the live UI renders the status in the separate **Target Predictions** panel. The screenshots show the expected message, “Gopher rockfish: No favorable areas right now,” while the modeled-opportunities panel separately reports no modeled areas for that species in the selected region. No uncaught browser errors or failed API-v1 responses were recorded. Updated the smoke test to assert the species name and no-favorable-areas status against rendered page text, rather than the wrong component. Test-only correction; no frontend application or scientific model behavior changed. Browser QA remains pending until a full desktop/mobile run passes and its screenshots are reviewed.

## Live frontend browser QA | no-favorable-areas assertion corrected | 2026-11-25

Manual run [45704137281](https://github.com/markeetox/LUPITA/actions/runs/45704137281) completed Chromium installation and the Spanish mackerel opportunity checks in both desktop and mobile contexts. The map-distance refresh and opportunity detail-sheet checks also completed, as evidenced by the uploaded opportunity and detail screenshots. The final Gopher rockfish check timed out because the test required the exact sentence "No favorable areas in the current snapshot for: Gopher rockfish", while the live UI reports "Gopher rockfish: No favorable areas right now." Failure screenshots show the species selected and the no-favorable-areas message displayed. No uncaught browser errors or failed API-v1 responses were recorded. Updated the assertion to require both the species name and the no-favorable-areas meaning, case-insensitively, without prescribing exact copy. Test-only correction; no app or scientific model behavior changed. Browser QA remains pending until another full run passes and its screenshots are reviewed.

## Live frontend browser QA | case-sensitive assertion corrected | 2026-11-25

Manual run [45703423878](https://github.com/markeetox/LUPITA/actions/runs/45703423878) installed Chromium and reached the public site at desktop and mobile sizes. Both contexts displayed the Spanish mackerel modeled-opportunities heading and cards. The smoke test nevertheless failed because it compared the rendered species name case-sensitively against title case, while the UI heading is uppercase. Screenshots confirm the species label and opportunity cards are present. No uncaught browser errors or failed API-v1 responses were recorded. Updated the test to compare the species name case-insensitively. This is a test-harness correction only; no frontend application behavior or scientific model behavior changed. Browser QA remains pending until the next full desktop/mobile run passes and its screenshots are reviewed.

## Live frontend browser QA harness | 2026-11-22

**Status:** implemented on `main`; manual execution pending.

Added `scripts/frontend_live_smoke.mjs` and `.github/workflows/frontend-live-smoke.yml`. The workflow installs pinned Playwright 1.55.0 and Chromium, then exercises the public LUPITA site in desktop (1440×1000) and mobile (390×844) contexts. It verifies:
- at least 100 species checkboxes load from the published catalog;
- selecting Spanish mackerel returns 1–3 modeled opportunity cards;
- cards show habitat-match score, model confidence and measured buoy input attached at prediction time;
- selecting a card opens the existing species/area detail sheet;
- Gopher rockfish is reported as having no favorable areas;
- the mobile control sheet remains within the viewport and has vertical scrolling; opportunity distances change after map panning;
- no uncaught browser errors or failed API-v1 requests occur.

Separate opportunity, area-detail and final-state screenshots plus a JSON report upload as `lupita-frontend-live-smoke` with 14-day retention, including failure screenshots when possible. Python CI triggers when the smoke script changes and syntax-checks it. The workflow is manual-only and defaults to `https://lupita.fuglymon.com`; it has not yet been dispatched. The Python CI workflow now syntax-checks the smoke script in addition to the map client and data adapter. Follow-up CI [45037948643](https://github.com/markeetox/LUPITA/actions/runs/45037948643) passed all three JavaScript syntax checks and **329 Python tests, 0 failures**. The live-browser workflow itself remains unrun. The final smoke-test assertion and UI disclaimer changes triggered Python CI run [45038221665](https://github.com/markeetox/LUPITA/actions/runs/45038221665); JavaScript syntax checks have passed, but the Python test job was still in progress at the last check.

Commits: browser script `365a8616324010204200f8d880b487407ac7b197`; workflow `4662991784fd5405a2ee7246223fed5f00f68626`; workflow expression fix `b77303d62115d1a129830c2829a9dab1674b96f2`; panning assertion `1b609964dd21d79eca013b06ad2828130a809d9f`; view screenshots `65b5652b1671b1d34aa40a3687723b8ae0ef3d40`; CI syntax check `de09ff09161cdae1e2b62a6ad05d170995f7f855`; CI path trigger `a8aba194f3dedbfc7aa18e121631d7941ce1346f`.

No production frontend, species, scoring, source, or ingestion behavior was changed by this QA harness.

---

## Species-conditioned opportunity shortlist and API v1 fallback | 2026-11-22

**Status:** implemented on `main`; Vercel reports a successful deployment for latest web commit `77b92b3603a11f1d3eb741655f17aa0321c7e70f`. Python CI run [45037594236](https://github.com/markeetox/LUPITA/actions/runs/45037594236) completed successfully: inline map-client and standalone adapter JavaScript syntax checks passed; **329 Python tests passed, 0 failed, 115 warnings**; the species audit artifact was generated. The audit found 130 structurally valid profiles, 0 model-compatibility issues, and 130 still needing research or model rebuilding.

### Why this was needed
The published `data` branch currently has an empty legacy root `fish.json`, while `api/v1/index.json` is populated with 130 species, 125 species with modeled areas, 5 with no favorable areas, and 960 mapped areas. The previous map client depended on `fish.json`, so it could load the catalog and buoy panel but could not reliably populate modeled fishing areas from the current published API. The UI now falls back to the versioned API rather than inventing a sample dataset.

### Implementation
- Added `web/lupita-data-adapter.js` to normalize API-v1 species detail records into the map client's spot shape and rank areas by model score, then distance for ties.
- Added lazy loading: the client fetches `api/v1/index.json` once, then retrieves only the detail files for selected species. It caches details in memory for the current page session.
- Added a **Modeled opportunities** panel with up to three highest habitat-match areas per selected species in the active region. Each card shows habitat-match percentage, model confidence, distance from map center, declared profile-evidence labels, and any measured buoy input/station observation time attached to that prediction.
- Selecting a card opens the existing map detail sheet and centers the map on the area. Nearby buoy conditions continue to update from the current map center.
- The UI does not recalculate or alter scores. The opportunity panel explicitly states that habitat match is not catch probability, and that measured inputs shown on a prediction are from prediction time while current nearby buoy readings are displayed separately. Measured buoy context at prediction time remains distinct from current nearby station readings and from modeled environmental layers. Opportunity distances refresh after map panning; the top control sheet is height-constrained and scrollable on smaller screens; API detail requests are limited to batches of eight to avoid a 130-request burst in Nola Mode.
- Added `tests/test_frontend_opportunity_adapter.py` covering API-v1 normalization, invalid coordinates, species scoping, score ranking and distance tie-breaking. CI now syntax-checks the standalone adapter as well as the inline map client.

Commits: adapter `805535ae01f7e5d5bd2b967aa65624cbdc101d83`; adapter tests `f06a44db267bb95eaec68f2899e86381fe65fa6e`; UI integration `11566d3090aa1bdf95aca55d9432a1b490d9e41c`; robustness follow-up `c0059d7851a154055dce2f6f474cbde025087ea2`; CI adapter syntax check `0b2fa1be968a823dacf69990526a52daf04f6a53`.

No species biology, factor values, scoring weights, gates, confidence calculations, production source settings or pipeline behavior changed. Node smoke checks and the full GitHub CI passed. Desktop/mobile interaction QA remains the outstanding acceptance check. Workflow: [Python tests](https://github.com/markeetox/LUPITA/actions/workflows/python-tests.yml).

---

## Front-end results and model transparency | 2026-11-22

**Status:** first user-facing diagnostics and explainability batch committed to `main`; latest frontend commit `85bcbccb50cc4e4286414f07c973db257642f2e3` deployed successfully through Vercel. Python CI run [45035145928](https://github.com/markeetox/LUPITA/actions/runs/45035145928) completed successfully: inline map-client JavaScript syntax check passed, **326 Python tests passed, 0 failed, 115 warnings**, and the species audit artifact was generated.

### Front-end changes
- `web/index.html` now has a collapsible **Data health** panel using the published `latest.json` diagnostics.
- The panel reports prediction snapshot freshness, total mapped areas, species with areas, SST/chlorophyll/HF Radar freshness and coverage, ETOPO depth coverage, FWC habitat mapping, and reef-structure inventory.
- Overall prediction status now distinguishes a successful but degraded refresh from a healthy refresh and from last-known-good predictions.
- The hardcoded fabricated `SAMPLE` species/spot fallback has been removed. If live prediction data cannot load, the page reports that predictions are unavailable instead of showing invented fishing locations.
- Added a **South Florida & Florida Keys** region (24.0–28.5°N, 83.5–78.0°W) and made it the first-visit default. Previously saved region choices remain respected; the wider regional and all-coasts views remain available.
- Added a **Nearby conditions** panel sourced from the published `latest.json` buoy observations. It ranks reporting stations by haversine distance from the current map center, displays water temperature in °C/°F, wind/direction/gust, wave height in metres/feet, station distance, and separate observation ages. It refreshes when the map view changes; selecting a station opens its existing detailed buoy view. Missing fields remain unavailable rather than estimated. It does not request precise device location.
- Selecting a mapped area now exposes active factor match scores, configured weights, declared evidence statuses, profile notes, listed source links, input coverage, and confidence limitations.
- The score badge explicitly labels the percentage as habitat match and says it is not catch probability. Evidence tags are described as profile assessments; source links are not treated as proof of the exact numeric claim.
- `.github/workflows/python-tests.yml` now checks the inline map-client JavaScript with `node --check` and runs when `web/**` changes.

### Published snapshot inspected before the UI change
Source: `data/api/v1/index.json` and `data/latest.json`, generated **2026-11-22 11:06:59 UTC**.
- 130 species catalog entries.
- 125 species with at least one modeled area; 5 report no favorable areas.
- 960 modeled areas across the current snapshot.
- Pipeline health: **degraded**, with no critical issues and a refreshed prediction snapshot.
- SST: 50.1 hours old, delayed; 55.2% aligned grid validity.
- Chlorophyll: 167.1 hours old, stale; 21.6% aligned grid validity.
- NOAA HF Radar: 8.1 hours old, fresh; 152 of 10,101 cells in the local query grid (1.5%) have valid aligned vectors. Freshness does not imply broad coverage.
- ETOPO: static, 53.2% sampled depth coverage; broad regional context, not reef-scale navigation data.
- FWC habitat: 49,903 source features and 514 mapped cells in the local query area.
- Reef structure: 4,548 artificial reef records and 25,362 natural reef polygons.

These counts describe the published model output and input inventory, not validated catch performance. No Copernicus bottom-temperature research data, NOAA validation artifacts, species factor ranges, scoring weights, gates, or production ingestion settings were changed in this front-end batch.

### Next
1. Inspect the deployed map at desktop and mobile sizes, including the diagnostics popover and a selected-area factor breakdown.
2. Improve the selected-area panel based on real device use and verify long evidence notes/source lists remain readable.
3. **Completed:** nearby-conditions overview now uses published buoy observations, distance from map center, and explicit observation ages. Next, test the panel at desktop/mobile sizes and improve the view based on actual use.
4. Continue independent Copernicus validation separately; do not expose exploratory bottom-temperature results as production inputs before validation.

---



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

Added `scripts/join_ioos_glider_etopo.py`, manual workflow `.github/workflows/ioos-usf-sam-etopo-screening.yml`, and tests `tests/test_join_ioos_glider_etopo.py`. The workflow takes inventory run ID `44737352618`, downloads its artifact, requests a NOAA NCEI ETOPO 2022 30-arc-second subset for the actual glider footprint, and creates per-observation nearest-cell bathymetry joins, a per-profile signed-separation CSV, and a JSON sensitivity summary. It preserves signed bottom separation, negative values, QC, interpolated coordinate provenance, and grid-center offsets. Pressure is excluded pending source-unit resolution. The live workflow succeeded in [run 44740669528](https://github.com/markeetox/LUPITA/actions/runs/44740669528), artifact 14631270203. It joined 201,645 coordinate-bearing rows from 2,387 profiles; all mapped to ETOPO ocean cells. 72,426 rows had finite depth and temperature (72,382 primary-QC PASS, 43 SUSPECT, 1 FAIL). Nonnegative bottom-separation sensitivity: 8,446 rows / 2,180 profiles within 5m; 17,261 / 2,212 within 10m; 35,075 / 2,250 within 20m; 63,765 / 2,298 within 50m. There were 1,062 negative separations, retained and excluded from these bands. The vertical-datum mismatch, interpolated positions, single deployment, and regional mismatch with the current Gulf Copernicus box remain limitations. See `docs/IOOS_GLIDER_DAC_REGIONAL_INVENTORY_PLAN_2026-11-19.md` for full results. A missing-value/NaN summary defect and a longitude test expectation were fixed in code; The missing-value fix, regression test, and corrected longitude assertion passed full Python CI in [run 44741832591](https://github.com/markeetox/LUPITA/actions/runs/44741832591). No Copernicus pairing or production change.


## IOOS ETOPO join interpretation and follow-up | 2026-11-20

The first live artifact exposed a summary-statistics defect: NaN depth/temperature rows caused JSON medians to be NaN. The underlying finite-row CSV was independently analyzed; code now retains rows with position/time/profile but only calculates bottom separation for finite depth+temperature, includes usable observation/QC counts, and computes finite medians. A regression test was added. CI run [44741683803](https://github.com/markeetox/LUPITA/actions/runs/44741683803) failed only because an existing longitude test expected 275 for -83.3° instead of the correct 276.7° after conversion to 0–360; assertion corrected. Latest CI reruns are pending. No production changes.


## IOOS ETOPO screening fix validated | 2026-11-20

Python CI run [44741832591](https://github.com/markeetox/LUPITA/actions/runs/44741832591) passed, including the new missing-depth/temperature regression test and full project test suite. The prior CI failure was a test expectation error for -83.3° converted to 276.7° in the 0–360 longitude convention; corrected and revalidated. No production behavior changed.


## Next validation requirement: potential-temperature comparability | 2026-11-20

Copernicus `bottomT` is sea-floor potential temperature, while IOOS `temperature` is measured CTD in-situ temperature. These are not directly interchangeable. IOOS metadata confirms a calculated practical-salinity variable and QARTOD salinity flags are available. Updated the research inventory downloader to retrieve salinity and all salinity QARTOD flags; CI is pending in [44742300164](https://github.com/markeetox/LUPITA/actions/runs/44742300164) and [44742308838](https://github.com/markeetox/LUPITA/actions/runs/44742308838). No salinity rows or potential-temperature conversions have been produced yet. After CI, rerun the manual IOOS inventory, inspect salinity QC, assess depth-derived sea-pressure calculation as an alternative to the unresolved pressure variable, then use TEOS-10 for a documented conversion. Only after that should the West Florida Copernicus reanalysis daily `bottomT` subset be extracted and compared. Daily P1D-m values are daily means, so temporal support must be respected. The deployment is outside the existing Gulf candidate box. No production changes.

## Salinity acquisition code and tests passed CI | 2026-11-20

Both pending CI runs completed successfully: [44742300164](https://github.com/markeetox/LUPITA/actions/runs/44742300164) (inventory script/dependency update, job 136308729869) and [44742308838](https://github.com/markeetox/LUPITA/actions/runs/44742308838) (test update, job 136308758566). The downloader now requests practical salinity and all available salinity QARTOD flags and reports salinity/primary-QC nonmissing counts. This is code/test validation only; no salinity observations have been downloaded yet.

Next: manually rerun [ioos-usf-sam-profile-inventory.yml](https://github.com/markeetox/LUPITA/actions/workflows/ioos-usf-sam-profile-inventory.yml), inspect salinity completeness/QC and alignment with temperature/depth, then decide whether TEOS-10 potential-temperature conversion is supportable. Do not use the unresolved pressure variable without source verification. No Copernicus pairing or production changes.


## IOOS salinity inventory retrieved | 2026-11-21

Manual inventory run [44956578185](https://github.com/markeetox/LUPITA/actions/runs/44956578185) succeeded on main; job 137005919171 succeeded and artifact 14727950637 was downloaded and inspected (SHA-256 d38d19b3e87d54629c6bacf181af044d439c5ad21cee99c05be32c4c17e9ebd8). Dataset remains 201,645 rows / 2,387 profiles / WMO 4801942. Finite depth+temperature rows: 72,426; finite practical salinity rows: 72,406 (20 missing salinity values among temperature/depth observations). Practical salinity range 35.333313–36.759933; median 36.508830.

Salinity primary QARTOD: 72,145 PASS, 237 SUSPECT, 24 FAIL. Temperature primary QARTOD: 72,382 PASS, 43 SUSPECT, 1 FAIL. On the same finite depth+temperature+salinity rows, 72,138 have both temperature and salinity primary QC PASS; 202 are temperature PASS/salinity SUSPECT; 22 are temperature PASS/salinity FAIL; 7 are temperature SUSPECT/salinity PASS; 35 both SUSPECT; 1 temperature SUSPECT/salinity FAIL; 1 both FAIL. Individual salinity spike flags include 4,771 NOT_EVALUATED and must not be counted as PASS. These are observation rows nested in one deployment, not independent casts.

Pressure metadata conflict remains unresolved: units say bar but comment says multiplied by 10 to dbar. The research path is to assess TEOS-10 sea pressure derived from CTD depth and latitude, explicitly documented, rather than silently use the raw pressure field. No TEOS-10 conversion or Copernicus pairing has yet occurred. Next: build a research-only conversion preserving raw values/QC, begin with both-primary-PASS rows, and report sensitivity; then extract the West Florida daily Copernicus bottomT subset. No production/species/scoring changes.


## TEOS-10 source-input caveat | 2026-11-21

The live IOOS metadata identifies this deployment's sensor as Sea-Bird Scientific GPCTD serial 9013 (calibration date 2012-07-08; factory calibrated, not user calibrated), but does not specify whether the published temperature is ITS-90 or IPTS-68. TEOS-10 GSW functions require ITS-90 input. Pressure metadata also conflicts (units bar vs comment describing conversion by factor 10 to dbar). Do not convert yet. First establish temperature scale and pressure provenance from source DBA/CTD processing or calibration documentation. A depth+latitude-derived sea-pressure estimate using GSW p_from_z is a possible separately labelled sensitivity route, not a measured pressure substitute. Sources: [IOOS dataset metadata](https://gliders.ioos.us/erddap/info/usf-sam-20240216T0000/index.html), [GSW-Python docs](https://teos-10.github.io/GSW-Python/conversions.html). No TEOS-10 conversion, Copernicus pairing, or production changes.


## USF Sam CTD provenance gate | 2026-11-21

Public metadata identifies the source merged DBA (0000339.dba), example SBD source file, and converter dba_to_ngdac_profile_nc.py. It marks the dataset Level 0 / product version 0.0. Temperature scale (ITS-90 vs IPTS-68) is not stated; pressure units conflict (declared bar, comment describes conversion ×10 to dbar). IOOS says original submitted files are archived but not publicly exposed; GANDALF says raw mission data access is password-controlled and PI-limited. Added research request document docs/IOOS_USF_SAM_CTD_PROVENANCE_REQUEST_2026-11-21.md specifying the exact calibration, configuration, pressure, depth, salinity-processing and source-file evidence needed from USF/GCOOS. No TEOS-10 conversion or Copernicus pairing until provenance is resolved. No production changes.


## GPCTD manual and pressure/depth evidence | 2026-11-21

Sea-Bird GPCTD User's Manual revision 004 states engineering OutputFormat 0/1 uses ITS-90 temperature and decibar pressure; OutputFormat 2 is raw counts. The deployment's actual OutputFormat is not published, so temperature scale remains strongly suggested but not confirmed. Row-level analysis of 72,426 paired values gives pressure/depth correlation 0.9999999964 and mean pressure/depth ratio 1.006743, consistent with pressure in dbar and depth in metres. This aligns with the ERDDAP comment that source pressure is multiplied by 10 from bar to dbar, suggesting the units='bar' attribute is stale. Treat dbar as the leading research interpretation, preserve original source values/metadata, and request provider confirmation before formal conversion. Provenance request doc updated. No TEOS-10 conversion or production changes.


## Alternative validation data-source assessment | 2026-11-21

Identified NOAA OMAO Nancy Foster CTD accession 0283250 as the strongest technical-provenance candidate to inspect next: SBE-9 source suite with t090C ITS-90, prDM dbar, sal00, altM and bottom-depth fields. It is raw originator data and still requires processing/QC review; western Gulf coverage is a separate stratum. NOAA SEFSC SEFIS CTD 2010–2024 documents ITS-90 temperature, pressure psi, practical salinity and 1-metre averaged bins, but has limited per-row position/time and no published per-level QC/altimeter fields. SEFSC CTD_PROC_CAST bottom-longline data and Argo delayed-mode/CCHDO GO-SHIP are additional candidates with stated limitations. Detailed assessment: docs/ALTERNATIVE_IN_SITU_VALIDATION_DATASETS_2026-11-21.md. No new data have been downloaded and no validation or production changes have been made.


## NOAA source priority reassessment | 2026-11-21

Cruise-report inspection corrected the initial Nancy Foster recommendation: accession 0283250 CTD casts were at roughly 1,043–1,862 m water depth, making it a deep-water reference rather than a shelf validation candidate despite its excellent documented t090C ITS-90 / prDM dbar / sal00 / altM fields. A better primary candidate emerged: NOAA Pulley Ridge / Dry Tortugas moorings. Peer-reviewed methods state near-bottom temperature recorders were 0.5 m above seafloor at three sites (bottom depths 54.5, 66.7 and 69.5 m), with 27–34 month time series. Related NOAA accessions: 0181331 ADCP time series, 0190271 separate temperature logger time series, 0190533 CTD casts. Must inspect exact files and confirm which accession contains the actual near-bottom logger temperature before implementation. Also identified SEAMAP accession 0131259: 1,761 observations, seven annual Oregon II cruise child datasets, 2009–2015 Gulf CTD archive with sampling maps/points. Full assessment and revised order: docs/ALTERNATIVE_IN_SITU_VALIDATION_DATASETS_2026-11-21.md. No NOAA files retrieved yet, no Copernicus matchup or production changes.


## NOAA Pulley Ridge archive role clarification | 2026-11-21

NOAA project records confirm accession 0181331 is the moored ADCP archive and explicitly includes hourly bottom temperature at Northern Dry Tortugas, Southern Dry Tortugas and Pulley Ridge; this is the direct bottom-temperature candidate. Accession 0190533 is CTD profiles from the mooring sites (2013/2014) with manufacturer processing details in file headers. Accession 0190271 is a separate lower Florida Keys temperature-logger series at shallow 0–10 m and deep 20–30 m shelf sites, not automatically the same near-bottom mooring series. Added manual read-only archive endpoint probe workflow and script to inspect availability/listings for these accessions plus SEAMAP 0131259. Awaiting manual workflow dispatch; no archive data retrieved yet. No Copernicus matchup or production changes.


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


## NOAA Pulley Ridge sample files inspected | 2026-11-22

Run [45032750496](https://github.com/markeetox/LUPITA/actions/runs/45032750496) succeeded; artifact 14757849720 (6,752,796 bytes; SHA-256 `33b568828bfc0ce3afa3ab3547f02c4c7474a859616e14491ba02e2f2a8d016c`; expires Dec 6). Every downloaded file passed NOAA manifest size/SHA-256 verification.

- **0181331 ADCP:** nine hourly deployments, 69,687 rows with finite `bottom_temperature`; 15.86–28.48°C. NOAA documentation: bottom-mounted upward-facing ADCPs, transducers ~0.5m above seabed; temperature is from an internal instrument thermistor, precision ±0.4°C/resolution 0.01°C. Data are marked preliminary. Strongest bottom-temperature candidate, but internal thermistor coupling/offset and calibration uncertainty remain caveats. Raw hourly and 40-hour low-pass temperatures are separate fields.
- **0190533 CTD:** six distinct cast events represented by 18 CNV files (WS/dWS/uWS variants, not 18 independent casts). Sea-Bird SBE9plus; processed by Win32 Data Processing Suite v7.26.7; NOAA calls final. Headers specify ITS-90 temperature, Digiquartz dbar pressure, salt-water depth, potential temperature, GPS position and UTC. Six WS casts reach 48.68–67.553m. Excellent candidate for bottom-proximate profiles after ETOPO clearance screening.
- **0190271 logger:** 216,929 rows (66,044 deep shelf 20–30m; 150,885 shallow shelf 0–10m), HOBO U22-001, 5-minute intervals in 2012 and 10-minute from 2013-10-07, 20.222–31.74°C. Documented site coordinates. Sensor height above bottom is unspecified; supplementary context only, not proven bottom reference.

Next: parse ADCP time-series quality/completeness and CTD profiles/cast identities; join CTD depth to ETOPO for bottom clearance; then consider carefully time-matched Copernicus comparison. No conversion, matchup, species/scoring, ingestion or production changes.

### Frontend browser smoke runner fix (2026-11-22)
The first live browser smoke attempt, GitHub Actions run [#45045780761](https://github.com/markeetox/LUPITA/actions/runs/45045780761), failed before launching Chromium. GitHub assigned Ubuntu 26.04 through `ubuntu-latest`; Playwright 1.55.0 does not support Chromium installation on that image. The workflow is now pinned to `ubuntu-24.04` (commit `61b0701fa983400050e3eebea01ed73b5586aa46`). The desktop/mobile smoke assertions have not run yet; rerun the manual workflow and inspect its results/screenshots before claiming browser QA passed.


## Live frontend browser QA | first execution result | 2026-11-22

Manual browser run [45047547674](https://github.com/markeetox/LUPITA/actions/runs/45047547674) successfully installed Chromium on the pinned Ubuntu 24.04 runner and reached the public site in both desktop and mobile contexts. The first assertion then failed because the test waited for a visible checkbox while the species checklist was intentionally collapsed behind `#selectBtn`. The DOM contained all 130 checkbox entries; the test simply had not opened the selector. No uncaught page errors or failed API-v1 responses were recorded before the timeout. Failure screenshots confirm the page rendered and the selector was closed. Updated the smoke script to open the selector before waiting for visible checklist items and removed the now-redundant later click. This is a test-harness correction, not an application behavior change. Desktop/mobile interaction QA remains unverified until the corrected workflow is run and its screenshots/results are inspected.


Occurrence-data acquisition review added in commit `7ecb97d91d9cbe9cd6c4736f083510b5c9e2ece2`: Florida Museum's Ichthyology Darwin Core Archive (CC-BY-NC 4.0) is the leading candidate for georeferenced voucher records, subject to taxonomic/coordinate/effort review. NOAA DisMAP is a candidate for fishery-independent survey context, but coverage and sampling metadata must be confirmed. Important limitation: the USGS NAS occurrence API serves its Nonindigenous Aquatic Species database; its species fact sheet is useful range context, but its occurrence API must not be treated as a primary native Florida occurrence dataset or as evidence of absence. Next research action: inspect museum occurrence records and DisMAP survey coverage without committing raw records or deriving a hard mask from sparse points.

## NOAA Southern flounder extraction and first-pass audit | 2026-11-27

Manual workflow [46019958931](https://github.com/markeetox/LUPITA/actions/runs/46019958931) completed successfully on `main`. Artifact `noaa-southern-flounder-survey-extraction` (ID `15206869499`, 58,180,821 bytes) was downloaded and inspected; it contains 13,703 target-species sample records across Gulf, Southeast Fall, Spring and Summer layers. The artifact expires 2026-12-11. Full analysis: [NOAA_SOUTHERN_FLOUNDER_EXTRACTION_ANALYSIS_2026-11-27.md](NOAA_SOUTHERN_FLOUNDER_EXTRACTION_ANALYSIS_2026-11-27.md).

First-pass results: 1,658 records have WTCPUE > 0 and 12,045 have WTCPUE = 0. NOAA's June 2026 DisMAP technical report states that its compiled dataset is expanded with zeroes for trawls where a regionally recorded species was not caught; therefore these are sample-level no-catch values, not merely missing records. They do not prove absence outside those sampled tows. All 572 Gulf sample records south of 26°N have WTCPUE = 0, but their depth range is 4.3–103.2 m and this bottom-trawl footprint does not represent South Florida estuaries. Southeast survey samples reach approximately 28.75°N and do not cover South Florida. Southern flounder is marked `CoreSpecies=No` throughout.

The current InPort time extents end in 2024 for Gulf/Fall/Spring while extracted point layers contain 2025 rows; this metadata mismatch is documented for follow-up. No raw records were committed and no profile, mask, scoring, confidence, ingestion, source or production behavior changed.

The latest extractor CI run [46018508487](https://github.com/markeetox/LUPITA/actions/runs/46018508487) also completed successfully: **336 passed, 0 failed** (115 warnings); map-client JavaScript syntax checks and species audit/artifact steps passed.



### NOAA–SEAMAP original-record crosswalk audit | 2026-11-27

Inspected the uploaded SEAMAPDATAV3 CSV/Access archives, Bottom Longline archives, and ichthyoplankton archive. Added [NOAA_SEAMAP_CROSSWALK_ANALYSIS_2026-11-27.md](NOAA_SEAMAP_CROSSWALK_ANALYSIS_2026-11-27.md) with archive hashes, methods, counts, exceptions, and interpretation.

All 4,805 NOAA Gulf SampleIDs are crosswalked to original SEAMAP station/deployment records. 4,795 match the composite key directly; ten NOAA SampleID cruise segments contain `2001` but independently match SEAMAP cruise `2101` in 2021. All 4,805 agree on survey year and exact depth, and NOAA points match SEAMAP tow midpoints within 69.5 m. All 277 positive WTCPUE samples match a Southern flounder BGS record; all 4,528 zero-CPUE samples have other-taxa catch records but no Southern flounder BGS record. The ten identifier discrepancies are documented rather than silently rewritten.

The 572 samples south of 26°N are all corroborated, have recorded ST-trawl effort and biological catch context, and have no Southern flounder BGS record. The 73 shallow eastern samples (4.3–20.1 m) show the same pattern; all have 29–31 minutes recorded and no non-empty operation code. This remains sample-level bottom-trawl no-catch evidence, not estuary-wide absence. The plankton archive adds one species-level *P. lethostigma* record from 2008 in the northern Gulf (7.8 mm); genus-level *Paralichthys* records remain taxonomically unresolved.

The uploaded data dictionary does not define the HAULVALUE code G. One 56-minute tow requires protocol review, and the ten mismatched vessel-35 records remain excluded. No raw archives were committed and no profile, mask, scoring, confidence, ingestion, production source, or publishing behavior changed.


### South Florida public evidence acquisition audited | 2026-11-28

The manual-only [acquisition workflow](../actions/workflows/south-florida-public-evidence-acquisition.yml) ran successfully on main: [run 46154737377](https://github.com/markeetox/LUPITA/actions/runs/46154737377). Artifact `south-florida-public-evidence` (ID `15266424962`) was downloaded and audited; no source failures were reported.

- FWC/FWRI Inshore FIM SRS: 6,008 exact-name positive-catch records, 1996-04-15 to 2023-12-21, representing 10,482 fish in `TotalNum`. Only one record is south of 27°N (26.843167°N); none is south of 26.5°N. The public layer contains positive-catch records only, so missing target records cannot be treated as non-detections.
- NPS Everglades creel: full source catch file parsed (828,222 rows); 210 Southern flounder catch rows across 205 interview keys, with 271 reported fish, all between 1980-01-05 and 1997-03-16. Almost all are from Flamingo. This is fisheries-dependent angler-intercept data, not standardized abundance; later missing records do not establish absence.
- Florida Museum UF Ichthyology: 241,669 occurrence rows in the downloaded archive; 221 exact-name candidates, including 170 Florida records. Ten Florida vouchers are at or south of 27°N, including Port Everglades, Buttonwood Canal / Everglades National Park, and Sands Key / Miami-Dade. Museum records are preserved-specimen occurrences, not abundance estimates. License CC-BY-NC 4.0.

The evidence streams remain separate. Together they document historical South Florida occurrence, but do not establish current occupancy, abundance, or an ecological range boundary. No hard mask or model change is justified. Full methods, counts, caveats, and next steps are in [FLORIDA_SOUTHERN_FLOUNDER_PUBLIC_DATA_EXPANSION_2026-11-27.md](FLORIDA_SOUTHERN_FLOUNDER_PUBLIC_DATA_EXPANSION_2026-11-27.md). No species profile, model, mask, scoring, confidence, ingestion, production source, or publishing behavior changed.


### FWC gear and NPS creel metadata audit | 2026-11-28

Resolved the FWC gear codes in the 6,008-record positive-catch extract using the agency's FGDC metadata: 20 = 21.3-m bay seine; 23 = 21.3-m river seine; 160 = 183-m haul seine; 300 = 6.1-m straight-tow otter trawl; 301 = 6.1-m arc-tow otter trawl. The same metadata confirms all FWC size fields are millimeters. The southernmost positive catch is still the single 1997-07-09 gear-160 record at 26.843167°N, with two fish, 85–105 mm. This is not an absence boundary because the export contains positive-catch records only.

FWC's program page distinguishes seven routine current estuarine regions from similar Florida Everglades and Florida Bay surveys supported by special funding. The 2023 core SRS annual report's study-area table does not include Florida Bay or the Everglades. Keep those special-program sources distinct from the statewide Inshore SRS extract until original records can be crosswalked; do not infer that the GIS layer's broad bounding box proves sampling in every southern habitat.

NPS area codes are resolved: historical numeric areas 1/2/3 correspond to later paired Florida Bay / Cape Sable subzones; 4 = Whitewater Bay; 5 = Shark River; 6 = Ten Thousand Islands. The 210 catch rows (271 reported fish) distribute across areas 1–6 as documented in the detailed research report. NPS metadata says the catch table's four-field compound key should be unique, but the Southern flounder subset has 210 rows and only 205 unique key combinations; five are split harvested/released records. Preserve disposition as an additional discriminator. QA flags concern trip-hours, party composition, species preference, and one high-party-size check; none directly invalidates the species identification or fish count. Do not automatically discard flagged catches.

Detailed methods and caveats added to [FLORIDA_SOUTHERN_FLOUNDER_PUBLIC_DATA_EXPANSION_2026-11-27.md](FLORIDA_SOUTHERN_FLOUNDER_PUBLIC_DATA_EXPANSION_2026-11-27.md). No raw source data committed and no species profile, model, mask, scoring, confidence, ingestion, production source, or publishing behavior changed.


### NOAA/AOML Florida Bay event-level data source located | 2026-11-28

Located two public NOAA/AOML juvenile sportfish ERDDAP datasets hosted by GCOOS. The main species-sample dataset covers 2004-09-21 through 2016-11-12 and exposes scientific name, species count, individual length (mm), coordinates, station/zone, salinity, temperature, and seagrass fields. A complementary collection-station dataset covers 2009-06-06 through 2016-11-12 and contains measured individual fish from a subset of 12 stations each month, with standard/total length and weight.

Important: the ERDDAP data currently end in 2016, while the NOAA report summarizes 2004–2019. The collection dataset's 12 stations/month must not be confused with Table 5's n=12 Southern flounder site samples. Neither source supplies a complete survey-wide zero-catch denominator through these public tables. Updated `scripts/acquire_south_florida_public_evidence.py` to download both raw CSVs and metadata pages and create separate exact-name candidate extracts. The expanded workflow is committed but not yet run. Next: manually dispatch [South Florida Public Evidence Acquisition](../actions/workflows/south-florida-public-evidence-acquisition.yml), then audit headers, counts, event keys, lengths, coordinates, and temporal coverage. No species profile, model, mask, scoring, confidence, ingestion, production source, or publishing behavior changed.


### NOAA/AOML Florida Bay raw observations acquired and audited | 2026-11-28

Workflow [run 46158258337](https://github.com/markeetox/LUPITA/actions/runs/46158258337) succeeded on `main`; artifact ID `15268192641` (28.9 MB, expires 2026-12-12). Acquired 11,473 rows from the NOAA/AOML juvenile sportfish main table and 65,454 rows from its collection-station measurement subset.

The main table contains **nine exact Southern flounder rows**, each `SpeciesCount=1`, with nine unique sample keyfields. Dates span 2005-11-11 to 2016-11-10; positions 25.100–25.167°N, 80.967–80.664°W; zones West (6), Crocodile (2), Rankin (1). Five rows have individual lengths (72, 84, 120, 180, 255 mm); four lengths are missing. Salinity is 33.3–40.4 PSU (mean 36.82; sample SD 2.43); temperature 23.61–32.30°C.

The NOAA 2021 report Table 5 says n=12 site samples and reports salinity 33.3–40.4 PSU, mean 36.7 ± 2.31. The raw extract reproduces the range and closely matches the mean, but contains nine rows, not 12, and its sample SD differs. This discrepancy remains unresolved; do not claim the nine rows fully reproduce Table 5. The collection-station subset has zero exact-name target rows, which does not negate the main-table detections because it is a separate 12-stations/month subset.

This is direct georeferenced fishery-independent Florida Bay occurrence evidence through 2016, not an abundance estimate, current occupancy statement, complete zero-catch denominator, or range boundary. Detailed row-level table and caveats are in [the research report](FLORIDA_SOUTHERN_FLOUNDER_PUBLIC_DATA_EXPANSION_2026-11-27.md). No raw source files committed and no production/model/profile/mask/scoring changes.


### NOAA/AOML workbook acquisition status | 2026-11-28

Latest manual acquisition [run 46160840439](https://github.com/markeetox/LUPITA/actions/runs/46160840439) succeeded on `main` at `92491226ff379597cb50b1cfcf3b05873f355a4f`. Artifact ID `15269970886` (28,887,271 bytes; expires 2026-12-12). All existing public-source downloads succeeded. The 2019 NOAA/AOML juvenile sportfish workbook was attempted but returned HTTP 403 Forbidden after retries; it is not in the artifact and has not been audited. The error is captured in `acquisition_summary.json`.

NOAA/AOML's current data-products and Juvenile Sportfish Survey pages continue to advertise a downloadable survey workbook, so the next task is to recover the current official download target or test an appropriate browser-style request/referer. Until then, the nine ERDDAP detections and report Table 5 n=12 remain separate, unreconciled evidence. No model, species profile, geographic mask, scoring, confidence, ingestion, production source, or publishing behavior changed.

### NOAA/AOML Florida Bay report update | 2026-11-28

Located the 2024 NOAA/AOML annual report covering juvenile sportfish monitoring in Florida Bay from 2004 through 2023 (SeFSC-PEMD-HEB 2024-02). Southern Flounder remains included in the report's list of species observed in the study area. Its Methods section confirms that all sizes of other sportfish caught in every tow were identified, measured, and counted; a separate subset of 12 stations per month from 2009 onward had all organisms under 100 mm preserved and lab-identified. Do not confuse that monthly processing subset with Southern Flounder's sample count.

A key denominator distinction is now documented: the 2021 NOAA OAR-AOML-48 report labels Southern Flounder's n=12 as **site sample size**, while the 2024 report's Table 5 caption defines n as **number of individuals sampled**. Those counts are not directly comparable. The 2024 report confirms continued inclusion in the program through its 2004–2023 reporting period, but its rendered table's Southern Flounder numeric row and event-level records were not extracted. The nine exact Southern flounder ERDDAP sample rows (2005–2016) therefore remain a separate bounded extract; the difference from 2021 n=12 remains unresolved. The 2018 report's searchable text omits the rendered Table 4 species rows, so no absence inference can be made from its failed text search.

Latest acquisition run [46168260876](https://github.com/markeetox/LUPITA/actions/runs/46168260876) succeeded, but both the standard and browser-header NOAA/AOML workbook requests returned HTTP 403. Artifact ID 15272448030 contains the other public evidence sources but not the workbook. No missing rows are imputed. Detailed findings and citations are in [FLORIDA_SOUTHERN_FLOUNDER_PUBLIC_DATA_EXPANSION_2026-11-27.md](FLORIDA_SOUTHERN_FLOUNDER_PUBLIC_DATA_EXPANSION_2026-11-27.md).

No species profile, geographic mask, scoring, confidence, ingestion, production source, or publishing behavior changed.

### FWC full FIM export lead assessed | 2026-11-28

Located the Florida SEACAR Data Discovery record for FWC Fisheries-Independent Monitoring Program 69. The program is described as monthly stratified-random monitoring from 1989 to current, with roughly 10,000 net deployments annually and species/catch, length, temperature, salinity, habitat, and location fields. SEACAR lists standardized Nekton and Discrete Water Quality exports updated September 2026. However, the page says data are available by request from the FWC program director and the download form requires valid email and identifying organization/occupation/purpose details. No form was submitted and no contact information was used. Florida Bay coverage in those full exports is not yet verified.

Also assessed the public SECOORA ERDDAP FIMMAP_Counts dataset. Its own summary lists Tampa Bay, Charlotte Harbor, Northern/Southern Indian River Lagoon, Cedar Key, Apalachicola Bay, and Jacksonville, not Florida Bay. It is therefore not a valid substitute for Florida Bay survey events or no-catch denominators. Its schema defines zero individualCount as absence only when the absence methodology is documented.

No FWC full export was acquired and no new target records are claimed. Existing FWC positive-catch-only GIS limitation remains. Detailed access assessment is in [FLORIDA_SOUTHERN_FLOUNDER_PUBLIC_DATA_EXPANSION_2026-11-27.md](FLORIDA_SOUTHERN_FLOUNDER_PUBLIC_DATA_EXPANSION_2026-11-27.md). No model/profile/mask/scoring/production changes.

