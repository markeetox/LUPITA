# WOD GLD to ETOPO observed-level join protocol | 2026-11-19

## Purpose and scope

Join the South Florida WOD GLD temperature observations to NOAA NCEI ETOPO 2022 at 30-arc-second resolution. This is a research-only bathymetry context step. It does not select a near-bottom cutoff, pair Copernicus temperature, or change production behavior.

## Inputs

1. Complete South Florida GLD Q-format ASCII archive from WODSelect.
2. `wod_gld_south_florida_etopo_30s.csv` from the manual workflow `.github/workflows/wod-gld-etopo-grid.yml`.
3. Pinned IQuOD `wodpy` parser source commit `116480b257a227ce38281d3836c40812246e5156`, installed only from `requirements-research-wod.txt`.

## Join rules

- Parse with IQuOD `WodProfile`; do not invent a WOD decoder or drop original QC metadata.
- For the 116 GLD casts carrying per-level variable codes 30/31, use those per-observation latitude/longitude values.
- For the remaining 745 casts, use the primary-header cast coordinates.
- Join each observed temperature level to the nearest ETOPO grid cell and retain the nearest-cell distance.
- Also calculate bilinear interpolation only when all four surrounding ETOPO cells are ocean. This is a sensitivity estimate, not a separate data source.
- Calculate continuous bottom separation as `seafloor_depth_m - observation_depth_m`. Negative values remain visible and require investigation.
- Preserve WOD profile, temperature-level, depth-level, and originator QC flags.

## Sensitivity reporting

Report counts for nonnegative separations in 0–5, 0–10, 0–20, and 0–50 m bands, both across all levels and in a strict WOD-QC subset (temperature profile QC 0, temperature level QC 0, depth level QC 0). These are descriptive sensitivity bands only. Do not choose a cutoff or treat levels as independent samples.

## Reproducibility

Run:

```bash
python -m pip install -r requirements-research-wod.txt
python scripts/join_wod_gld_etopo.py \
  --gld /path/to/GLD.gz-or-ASCII \
  --etopo /path/to/wod_gld_south_florida_etopo_30s.csv \
  --output /path/to/wod_gld_etopo_join.csv \
  --metadata /path/to/wod_gld_etopo_join_metadata.json
```

The script writes a joined level CSV and a metadata JSON with input checksums, parser identification, counts, distance/separation distributions, and caveats.

## Scientific limitations

- ETOPO is a global relief model, not a navigation chart or local survey.
- Nearest-cell and bilinear results are two treatments of the same ETOPO grid, not independent confirmation.
- Negative separation is not clipped or silently excluded.
- Glider levels within casts and repeated trajectories are autocorrelated.
- WOD temperature variable 1 is in degrees Celsius and has not been established as potential temperature. No Copernicus residual or accuracy metric is permitted until thermodynamic comparability is resolved.
- No species-factor, gate, weight, scoring, confidence, ingestion, or publication behavior changes.


## Preliminary local join results | 2026-11-19

The ETOPO export workflow completed in [run 44524228011](https://github.com/markeetox/LUPITA/actions/runs/44524228011), producing artifact ID 14529482014. The 30-arc-second grid contains 48,829 cells (253 × 193), zero missing elevations, and CSV SHA-256 `e9e66d915e6dd82403785a2e5f90a9a008127557391e3ec1be8a79ddfa754739`.

A preliminary local join used source-derived IQuOD parser-core logic (not an installed-package parity test). It joined 84,099 levels from 861 casts. 71,816 levels use cast-header coordinates and 12,283 use per-observation coordinates. All mapped nearest cells are ETOPO ocean class. Median nearest-cell offset 349.25 m; maximum 625.86 m. Negative bottom separation counts: 184 using nearest cell, 145 using bilinear interpolation; bilinear negatives occur in 38 casts. Median bilinear separation 171.75 m.

Bilinear nonnegative sensitivity counts, levels/casts (strict WOD QC levels/casts): 0–5 m 107/69 (24/22); 0–10 m 310/120 (78/36); 0–20 m 1,279/322 (555/139); 0–50 m 6,767/637 (3,842/338). Strict WOD QC requires profile, temperature-level, and depth-level flags all zero. These are descriptive counts only; no threshold is adopted.

The repository join adapter, pinned parser dependency, tests, and manual package-import workflow are now in place. The new tests passed in [run 44526729327](https://github.com/markeetox/LUPITA/actions/runs/44526729327). Actual package-level parse parity is pending the manual workflow. Full result interpretation and limitations are appended to the GLD reference parse audit.


Latest follow-up CI after the joiner metadata/QC reporting changes also passed: [run 44527038522](https://github.com/markeetox/LUPITA/actions/runs/44527038522). This validates the repository Python test suite; the separate manual workflow still needs to verify installation/import of the pinned `wodpy` package.
