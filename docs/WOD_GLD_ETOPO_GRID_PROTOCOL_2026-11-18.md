# WOD GLD South Florida ETOPO grid export protocol | 2026-11-18

## Purpose

Prepare a full-resolution local bathymetry grid for the 861-cast South Florida WOD GLD sample. The existing Copernicus bathymetry artifact samples ETOPO at the Copernicus 0.083-degree grid spacing. That is too coarse to assign seabed depth confidently to individual glider observations, especially near the shelf break.

## Source

- NOAA NCEI ETOPO 2022
- ERDDAP dataset: `ETOPO_2022_v1_30s`
- Resolution: 30 arc-seconds (0.008333333 degrees)
- Variable: `z`, meters, positive up
- NOAA ERDDAP: https://oceanwatch.pifsc.noaa.gov/erddap/griddap/ETOPO_2022_v1_30s.html

## Requested bounding box

The export includes a margin around the verified GLD coordinate envelope:

- Latitude: 24.45 to 26.55°N
- Longitude: -81.05 to -79.45° (converted to 278.95 to 280.55° for ERDDAP)

The query uses stride 1. It must not reuse the stride-10 / approximately 0.083-degree sampling from the earlier Copernicus bathymetry assessment.

## Output and validation

The manual workflow `.github/workflows/wod-gld-etopo-grid.yml` creates artifact `wod-gld-south-florida-etopo-30s` containing:

- `wod_gld_south_florida_etopo_30s.csv`: every returned ETOPO grid cell, normalized to -180..180 longitude, with elevation, seafloor depth, and land/ocean/coast classification
- `metadata.json`: source URL, requested bounds, grid dimensions, resolution, missing-cell count, vertical sign, and output checksum

The script validates regular 30-arc-second spacing, duplicate coordinates, and complete rectangular coverage. ETOPO ocean depth is `-z` only where elevation is below -1 m. Values between -1 and +1 m remain coastal-ambiguous; elevation above +1 m is land. Fill values remain missing.

## Next join

After the workflow artifact is inspected, join each GLD observation level to the nearest 30-arc-second ETOPO cell using:
- per-observation latitude/longitude codes 30/31 for the 116 casts that carry them;
- primary-header cast coordinates for the remaining 745 casts.

Keep the coordinate-source field in every joined row. Compute continuous bottom separation as `seafloor_depth_m - observation_depth_m`. Do not impose a near-bottom cutoff until the full distribution and spatial sensitivity are reviewed. ETOPO is a global relief model, not a navigation chart, and a nearest-cell join is still an approximation.

No production species data, scoring, gates, weights, confidence, ingestion, or publication behavior may change in this research workflow.


## CI status | 2026-11-18

The initial Python CI attempt failed because the test module imported pandas, which is not part of the repository's core requirements. The exporter and tests were refactored to use the Python standard library; `requests` is imported only inside the network execution path. The full repository Python test suite passed in [run 44409583591](https://github.com/markeetox/LUPITA/actions/runs/44409583591). The manual export workflow has not yet been dispatched, so no full-resolution ETOPO grid artifact exists yet.
