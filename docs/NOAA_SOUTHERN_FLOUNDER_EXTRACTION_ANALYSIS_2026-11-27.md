# NOAA Southern Flounder DisMAP extraction analysis

**Date:** 2026-11-27  
**Status:** first-pass data audit complete; research only; no model or profile changes  
**Target:** Southern flounder (*Paralichthys lethostigma*)  
**Workflow run:** [46019958931](https://github.com/markeetox/LUPITA/actions/runs/46019958931)  
**Artifact:** `noaa-southern-flounder-survey-extraction` (artifact ID `15206869499`)  
**Artifact SHA-256:** `dc005fc8558889844f2ad2b8240ed882240d085339e1d2606b7a23f20b9282f7`  
**Artifact retention:** through 2026-12-11 15:00:24 UTC

## Extraction result

The manual workflow completed successfully on `main` at commit `36f529e73a6a96c475aa4ce95cdb933b53c5ec83`. The artifact contains the JSON extraction report, four target-observation CSVs, and four same-`SampleID` context CSVs. The ZIP is 58,180,821 bytes. Raw records are not committed to the repository.

All four source layers matched the exact common name and scientific name. Across the layers there are **13,703 target-species sample records**:
- Gulf of Mexico: 4,805
- Southeast US Fall: 3,045
- Southeast US Spring: 2,865
- Southeast US Summer: 2,988

All target records have non-null latitude, longitude, depth, and WTCPUE. The target records use `TransformUnit=cuberoot`; analysis below uses the untransformed `WTCPUE` field, not `MapValue`.

## Sample-level catch results

NOAA's June 2026 DisMAP technical report states that the compiled dataset is expanded with zeroes when a species known from a region is not caught in a particular trawl (section 3), and defines survey presence as WTCPUE greater than zero in its Species Persistence methods (section 6.2). Therefore, an explicit zero WTCPUE row is meaningful as a no-catch result for that survey sample. It is not evidence of absence outside the sampled tow or survey footprint.

| Survey layer | Sample records | WTCPUE > 0 | WTCPUE = 0 | Positive sample rate |
|---|---:|---:|---:|---:|
| Gulf of Mexico | 4,805 | 277 | 4,528 | 5.76% |
| Southeast Fall | 3,045 | 564 | 2,481 | 18.52% |
| Southeast Spring | 2,865 | 454 | 2,411 | 15.85% |
| Southeast Summer | 2,988 | 363 | 2,625 | 12.15% |
| **Total** | **13,703** | **1,658** | **12,045** | **12.10%** |

These are survey-sample records, not 13,703 independent geographic locations. The Gulf layer has 4,805 unique coordinates. Southeast seasonal layers reuse stations across years and seasons: Fall has 537 unique coordinates (272 ever positive), Spring 532 (234 ever positive), and Summer 578 (203 ever positive). The union of Southeast seasonal coordinates is 706. Coordinates overlap across seasons (454 Fall/Spring, 452 Fall/Summer, 459 Spring/Summer).

NOAA describes WTCPUE as biomass weight catch per unit effort standardized to kg/ha. The technical report says WTCPUE is calculated from catch weight divided by swept area for the Southeast and Gulf datasets. The values should not be compared naively across different survey designs/seasons without reviewing their protocols.

## Geographic and depth observations

### Gulf of Mexico

- All sample records: 24.4901–30.3745°N, 97.3279–81.3310°W; depth 3.0–181.1 m.
- Positive WTCPUE records: 26.0134–30.3292°N, 97.3158–83.2316°W; depth 7.3–105.7 m.
- The southernmost positive sample is `004-290-00072`, 2010, at 26.0134°N, 97.0138°W, depth 26.0 m, WTCPUE 0.05207.
- There are 572 sample records south of 26°N; all 572 have WTCPUE = 0. Their depths range 4.3–103.2 m (median 43.0 m; mean 44.9 m) and span 2010–2025.
- Within the eastern Gulf sample area east of 85°W, there are 1,816 records and 11 positive samples. East of 84°W there are 1,400 records and 4 positive samples.

This is meaningful offshore/shelf survey no-catch evidence at sampled trawl locations, especially south of 26°N. It does **not** establish absence in Florida Bay, the Keys' nearshore waters, tidal creeks, bays, or the Caloosahatchee estuary. The sampling footprint and depth distribution are not a substitute for estuarine sampling.

### Southeast US seasonal surveys

| Survey | All-record latitude | All-record longitude | Depth range | Unique coordinates | Sites ever positive |
|---|---|---|---:|---:|---:|
| Fall | 28.75–34.69°N | 81.44–76.49°W | 3–13 m | 537 | 272 |
| Spring | 28.76–34.69°N | 81.44–76.49°W | 3–12 m | 532 | 234 |
| Summer | 28.76–35.23°N | 81.44–75.59°W | 2–13 m | 578 | 203 |

The southernmost positive Southeast records are near 28.76°N, 80.70–80.71°W. The survey domain does not extend into South Florida. These seasonal layers provide Atlantic shelf survey context, not a survey of the entire Florida Atlantic coast or its estuaries.

## Important data-quality and interpretation notes

1. **Zero values are useful, but local to a valid survey sample.** The DisMAP technical report explicitly says the regional species dataset is expanded with zeroes for trawls where a regionally recorded species was not caught. A zero can therefore be treated as a sample-level no-catch result for this dataset. It must not be propagated into an unsampled grid cell or treated as proof of ecological absence.
2. **The context CSV is not a separate effort table.** It contains other species rows sharing the target SampleID. It is useful for understanding the sample record structure, but does not independently provide tow validity, tow duration, gear configuration, or complete effort metadata.
3. **Southern flounder is marked `CoreSpecies=No` in every extracted target row.** NOAA's technical report defines core species using a frequency threshold of at least 5% of tows in all survey years. This means these records should not be confused with the restricted core-species set used in some DisMAP summary products.
4. **Metadata time extents lag some extracted records.** The current InPort metadata describes Gulf and Southeast Fall/Spring extents ending in 2024, while the current point layers returned 2025 records for those three layers. Southeast Summer ends in 2022 in both the extracted data and metadata. Preserve the actual record years, and verify the source release/metadata mismatch before longitudinal modeling.
5. The Southeast layers are seasonal and use repeated station coordinates. Sample rows must not be counted as independent sites or independent years without the correct grouping.
6. The NOAA DisMAP interpolated surfaces are not raw occupancy boundaries. The technical report describes IDW interpolation over a 200 km search radius using 10–15 sites and a five-year time window. Do not convert those surfaces into a hard geographic mask.

## What this supports now

- Confirms real Southern flounder catch observations in both Gulf and Southeast shelf survey products.
- Confirms explicit sample-level zero-CPUE records in the same products, including 572 Gulf survey samples south of 26°N with no recorded catch.
- Shows that Gulf positive samples extend to 26.0134°N in the western Gulf, while the sampled Gulf points south of 26°N have zero CPUE.
- Shows that Southeast positive survey samples extend south to approximately 28.76°N, but that survey footprint does not cover South Florida.
- Supports a more detailed comparison with museum voucher records and published Florida range descriptions.

## What this does not support

- A South Florida absence polygon.
- A hard cutoff at 26°N or any other latitude.
- Exclusion of Florida Bay, the Keys, Caloosahatchee, or any estuary.
- A claim that the species is absent from all unsampled shallow/estuarine habitat.
- A production profile, scoring, confidence, ingestion, or publication change.

## Next research steps

1. Obtain the original Gulf SEAMAP and Southeast SEAMAP survey haul/effort metadata for the relevant years. Confirm valid tow flags, tow duration/distance, gear, swept-area calculations, depth, stratum and station inclusion.
2. Inspect the 572 zero-CPUE Gulf samples south of 26°N spatially and by year, depth and stratum, distinguishing Florida shelf points from Texas/western Gulf points.
3. Compare these survey points with Florida Museum georeferenced voucher records and authoritative Florida estuary/coastal range sources.
4. Check the 2025-versus-2024 metadata extent discrepancy with the current DisMAP release information.
5. Only after those checks, evaluate whether any coastal/estuarine geometry is scientifically defensible. Keep all model and profile changes gated for explicit approval.

## Sources

- NOAA Fisheries, [DisMAP Technical Report, June 2026](https://apps-st.fisheries.noaa.gov/dismap/docs/DisMAP_Tech_Report_06_2026.pdf), especially sections 3, 4, 6.2 and Table 1.
- NOAA Fisheries, [Survey Catch-per-unit-effort CURRENT, InPort 69743](https://www.fisheries.noaa.gov/inport/item/69743).
- NOAA Fisheries, [DisMAP portal](https://apps-st.fisheries.noaa.gov/dismap/DisMAP.html).
- NOAA current layers: [Gulf](https://services2.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/GMEX_Sample_Locations_CURRENT/FeatureServer), [Southeast Fall](https://services2.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/SEUS_FAL_Sample_Locations_CURRENT/FeatureServer), [Southeast Spring](https://services2.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/SEUS_SPR_Sample_Locations_CURRENT/FeatureServer), [Southeast Summer](https://services2.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/SEUS_SUM_Sample_Locations_CURRENT/FeatureServer).
- Workflow artifact: [run 46019958931](https://github.com/markeetox/LUPITA/actions/runs/46019958931).

No raw NOAA data was committed. No species profile, geographic mask, scoring factor, weight, gate, confidence logic, ingestion, production source, or publishing behavior changed.
