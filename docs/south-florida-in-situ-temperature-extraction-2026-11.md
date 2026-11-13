# South Florida in-situ temperature extraction: initial review

**Prepared:** 2026-11-13  
**Scope:** South Florida pilot; environmental validation only  
**Status:** In-situ extraction complete; MUR pairing pending mirror validation  
**Workflow:** GitHub Actions run 43344621387  
**Artifact:** `south-florida-temperature-audit` (30-day retention)

## Executive summary

The first live extraction successfully retrieved the USGS CREST Version 9 archive and three FWC-FWRI / SECOORA FLKEYS Array station time series. It normalized the observations, retained FWC aggregate and individual QC flags, and generated station-level summaries.

The selected stations cover a useful spread of sensor depths:

- USGS Biscayne reef loggers: approximately 3.35–3.96 m.
- FWC HFA04: 11 m.
- FWC LKA57: 23 m, within the 15–40 m Permit reef-tract depth context.
- FWC RHA54: 43 m, slightly deeper than that context.

The first NOAA CoastWatch MUR point queries returned HTTP 403. No paired logger-versus-MUR result is claimed from this run. A follow-up workflow revision adds fallback to other ERDDAP mirrors exposing the same NASA JPL dataset ID; that run is pending.

## Sources and sampling details

### USGS CREST Version 9

- Source DOI: https://doi.org/10.5066/F71C1TZK
- Metadata: https://cmgds.marine.usgs.gov/catalog/spcmsc/FL_coral_underwater_temps_metadata_v9.html
- Archive: https://coastal.er.usgs.gov/data-release/doi-F71C1TZK/data/FL_coral_underwater_temps_to_Jul2024.zip
- Measurements are recorded every 15 minutes.
- Loggers are mounted approximately 2–4 inches above the reef substrate at 7–16 feet of seawater depth.
- Reported site values are means of duplicate loggers where both were available.
- This release does not provide per-observation QARTOD quality flags. Do not imply that its records have the same QC treatment as the FWC data.

The extraction retained all USGS site columns with observations in the 2020–2024 analysis window:

| USGS site | Sensor depth (m) | Normalized observations |
|---|---:|---:|
| Pulaski Light | 4.88 | 152,901 |
| Sombrero | 4.27 | 93,178 |
| Fowey | 3.96 | 102,601 |
| Crocker | 3.96 | 93,006 |
| Pulaski West | 3.66 | 152,893 |
| Garden Key | 2.13 | 69,503 |
| Shadow | 3.66 | 40,227 |
| Brewster | 3.96 | 40,302 |
| Ball Buoy North | 3.35 | 40,012 |

Molasses Reef is not represented in this 2020–2024 extraction window because its published record ended in 2013.

### FWC-FWRI / SECOORA FLKEYS Array

Portal: https://erddap.secoora.org/erddap/index.html

The extracted variables include time, coordinates, sensor vertical coordinate z, sea-water temperature, aggregate QC and individual QC-test flags. The vertical coordinate is positive up; the report stores sensor depth as absolute metres below the datum.

| Station | Coordinates | Sensor depth | Available record window | Total observations |
|---|---|---:|---|---:|
| HFA04 | 24.6687, -82.8926 | 11 m | 2020-12-11 to 2022-08-12 | 10,805 |
| LKA57 | 24.4373, -81.9493 | 23 m | 2021-07-26 to 2024-06-25 | 17,740 |
| RHA54 | 24.5056, -83.1305 | 43 m | 2023-09-22 to 2024-08-14 | 7,848 |

Full-record aggregate QC counts:

| Station | PASS | SUSPECT | FAIL |
|---|---:|---:|---:|
| HFA04 | 10,637 | 161 | 7 |
| LKA57 | 16,948 | 639 | 153 |
| RHA54 | 7,436 | 342 | 70 |

Primary FWC summaries include only aggregate QC PASS records. All raw observations and flags remain in the artifact.

## Trailing 90-day station comparison

Each station uses its own final 90-day observation window. These windows are not simultaneous, and station locations differ. The table is descriptive only; it is not a controlled vertical temperature profile.

| Site | Sensor depth | QC-pass observations | Mean °C | P95 °C | Min °C | Max °C |
|---|---:|---:|---:|---:|---:|---:|
| Fowey | 3.96 m | 8,545 | 28.245 | 30.419 | 24.569 | 31.548 |
| Brewster | 3.96 m | 8,545 | 28.271 | 30.318 | 24.617 | 31.510 |
| Shadow | 3.66 m | 8,545 | 28.545 | 30.710 | 24.690 | 32.510 |
| Ball Buoy North | 3.35 m | 8,545 | 28.307 | 30.356 | 24.520 | 31.944 |
| HFA04 | 11 m | 2,108 | 29.266 | 30.294 | 27.256 | 30.616 |
| LKA57 | 23 m | 2,067 | 25.428 | 28.808 | 22.459 | 29.883 |
| RHA54 | 43 m | 2,117 | 27.140 | 30.023 | 22.746 | 30.445 |

For the 90-day windows, the four USGS Biscayne loggers each supplied 8,545 of 8,640 expected 15-minute records (about 98.9%). FWC supplied 2,137 of 2,160 expected hourly records at each station before QC filtering; QC PASS counts were 2,108 at HFA04, 2,067 at LKA57, and 2,117 at RHA54.

## MUR SST comparison status

The first point requests to the primary NOAA CoastWatch ERDDAP endpoint returned HTTP 403 for all seven selected locations. Therefore:

- No MUR values were included in the first artifact.
- No paired daily differences, bias, MAE or RMSE are available yet.
- The extraction must not be described as a completed surface-versus-subsurface comparison.

A follow-up revision tries alternate ERDDAP mirrors that independently expose the same dataset ID, `jplMURSST41`, with the same `analysed_sst` variable and degree-Celsius units:

- NOAA CoastWatch: https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41.html
- University of South Florida ERDDAP: https://erddap.marine.usf.edu/erddap/griddap/jplMURSST41.html
- Brown University RI Data Discovery Center: https://erddap.riddc.brown.edu/erddap/griddap/jplMURSST41.html
- EMODnet ERDDAP: https://erddap.emodnet.eu/erddap/info/jplMURSST41/index.html

The follow-up run records the host used for each MUR series and preserves source errors. Even if a mirror succeeds, the comparison is native-grid MUR at the nearest 0.01-degree coordinate, not a reconstruction of LUPITA's stride-5 production sample.

## Interpretation and safeguards

1. The 23 m LKA57 station is the strongest current FWC depth match for the Permit reef-tract context. RHA54 is deeper than the cited 15–40 m band; HFA04 is shallower.
2. The USGS Biscayne loggers are shallow reef sensors, not sensors on tidal flats. They are useful nearshore shallow-water references, not direct measurements of Permit exposure across all flats.
3. Differences between stations cannot be attributed to depth alone because sites, geography, deployment periods and seasons differ.
4. Sensor temperature distributions describe the logger environment. They do not establish Permit thermal preference, acclimation, physiological tolerance, habitat selection, or catch probability.
5. Do not derive bottom temperature from SST and bathymetry.
6. Missing records or failed sources remain unknown; they are not zero suitability or confirmed absence.
7. No production species profile, thermal threshold, scoring weight, gate, formula, ranking, API field, or prediction output was changed.

## Reproducibility

The manual research workflow is `.github/workflows/south-florida-temperature-audit.yml`. It stores the raw USGS archive, normalized USGS observations, raw and normalized FWC CSVs, MUR point extracts when available, daily paired comparisons, and summary report in a GitHub Actions artifact. The artifact is not published to the production data branch.
