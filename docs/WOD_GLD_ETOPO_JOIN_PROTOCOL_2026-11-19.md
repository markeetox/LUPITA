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
