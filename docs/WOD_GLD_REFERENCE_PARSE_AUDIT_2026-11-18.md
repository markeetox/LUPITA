# South Florida GLD IQuOD-format parse audit | 2026-11-18

## Scope

Research-only inspection of the user-supplied GLD archive from the South Florida WODSelect delivery. This audit validates file structure, decoded cast/profile completeness, metadata, temperature/depth observations, uncertainty fields, and QC flags. It does not establish near-bottom eligibility or model accuracy.

## Source archive identity

- File: `ocldb1794949360.1820758.GLD.gz` (re-uploaded as `ocldb1794949360.1820758.GLD(1).gz`)
- Compressed bytes: 837,608
- Decompressed bytes: 4,036,532
- SHA-256: `c75b110c4eba09c0a55aed34cf31d12f2693d3053fad09216d2794ff370fb0e3`
- Gzip decompression/CRC: passed
- Decompressed records: 49,226 fixed-width 80-character records with CRLF line endings
- Cast-start records: 861; all 861 begin with `Q`

The SHA-256 matches the earlier GLD audit exactly.

## Parser source and execution qualification

The IQuOD `wodpy` reference source explicitly recognizes a first-byte `Q` as IQuOD formatting. The reviewed source is pinned to repository commit `116480b257a227ce38281d3836c40812246e5156`; the `wodpy/wod.py` blob SHA is `c65b39c295443aa13690a15b5216a7e1e36486b6`.

The local execution used a faithful transcription of the reference `WodProfile` core decoding routines: Q-format primary header, character/PI section, secondary and biological headers, per-level depth/variable values and flags, IQuOD uncertainty fields, and byte-based profile navigation. The published `wodpy` package itself was not installed in this environment, so this is source-derived parser-core execution, not an independent package-import/parity test. No `wodpy` runtime dependency was added to LUPITA.

### Structural result

- 861 of 861 casts decoded without parser exceptions
- 861 unique WOD cast UIDs; no duplicate UID within this GLD file
- Every decoded profile advanced to the exact next byte boundary calculated from its declared profile byte count
- 0 per-profile byte-accounting mismatches
- Sum of expected profile byte spans equals the decompressed file size exactly: 4,036,532 bytes
- Parser reached EOF after cast 861
- Declared and decoded level counts agree for every cast
- 84,099 total levels
- All 84,099 levels contain both a depth and a temperature value; no missing depth or temperature values were found

This establishes successful decoding of this GLD archive with the Q-format parser logic. It does not prove that every metadata field has been semantically interpreted correctly.

## Decoded profile inventory

- Dataset: GLD
- Country code: US for all 861 casts
- Profile type: 0 for all 861 casts. NOAA defines 0 as observed levels and 1 as standard/interpolated levels.
- Probe type: code 15 (glider) for all 861 casts
- Ocean vehicle metadata:
  - 703 Spray Glider: 521 casts
  - 701 Seaglider: 262 casts
  - 702 Slocum Glider: 78 casts
- 44 distinct cruise numbers
- 44 distinct NCEI accession values
- 13 distinct platform codes; 11 resolve to named gliders in the currently inspected NCEI platform table, while codes 12331 and 12333 were not found in that table
- Project code 821 (Gliders in the Gulf Stream): 218 casts
- Project code absent: 643 casts
- Temperature instrument metadata (variable-specific code 5):
  - 456 (SBE 41/41CP CTD module): 823 casts
  - 495 (Glider Payload CTD / GPCTD): 38 casts

The instrument metadata is preserved as supplied. The 456 instrument description references an autonomous profiling-float CTD module, while all casts are classified as glider profiles; this is not silently reconciled and should remain visible in provenance review.

### Dates and coordinates

- Cast date range: 2015-04-09 through 2026-01-08
- Primary-header latitude range: 24.504 to 26.498°N
- Primary-header longitude range: 80.719 to 79.604°W
- All 861 primary-header positions fall within the requested South Florida/Keys box (-81.0 to -79.5°W, 24.5 to 26.5°N)

### Temperature and depth

- Temperature variable code: 1
- WOD standard unit: degrees Celsius
- Temperature range: 5.941 to 31.690°C
- Depth range: 0.11 to 715.84 m
- Median reported depth: 118.88 m

These are profile observation depths, not seafloor depths and not fish vertical-depth preferences. The maximum observed depth of 715.84 m does not establish that a cast reached the seabed.

## Uncertainty fields

- Latitude uncertainty: absent in all 861 cast headers
- Longitude uncertainty: absent in all 861 cast headers
- Depth uncertainty: absent at all 84,099 decoded levels
- Temperature value uncertainty: present at all 84,099 temperature levels, with the encoded value 0.002 throughout

The raw temperature uncertainty value is recorded as supplied. Its exact interpretation/units should be confirmed from the IQuOD metadata specification before using it as an uncertainty weight. No depth or coordinate uncertainty should be fabricated.

## WOD and originator QC

### WOD cast/profile QC for temperature

| WOD flag | Casts | Definition |
|---:|---:|---|
| 0 | 511 | Accepted cast/profile |
| 1 | 15 | Failed annual standard-deviation check |
| 4 | 4 | Failed seasonal standard-deviation check |
| 5 | 16 | Failed monthly standard-deviation check |
| 6 | 27 | Failed annual and seasonal checks |
| 7 | 10 | Bullseye or annual and monthly check |
| 8 | 15 | Failed seasonal and monthly checks |
| 9 | 263 | Failed annual, seasonal, and monthly checks |
| **Total** | **861** | |

Thus 511 casts have cast/profile flag 0 and 350 have a nonzero cast/profile flag. NOAA cautions that WOD quality flags describe passed/failed tests and do not by themselves classify values as good or erroneous. Retain the flags; do not silently delete all 350 nonzero-flag casts.

### WOD observed-level QC

- Temperature: 84,064 levels flag 0; 35 levels flag 3 (failed gradient check)
- Depth: 84,066 levels flag 0; 33 levels flag 2 (density inversion)

Among the 48,889 levels belonging to the 511 cast/profile-flag-0 casts:
- 48,867 have temperature level flag 0
- 48,874 have depth flag 0
- 48,852 have both temperature level flag 0 and depth flag 0

The 48,852 count is a provisional strict WOD-QC-only level subset (cast/profile flag 0 plus temperature/depth level flags 0). It is not yet a near-bottom-eligible sample and is not a final scientific inclusion rule.

### Originator QC metadata

- 712 casts carry secondary-header originator flag-set code 3 (GTSPP/IODE).
- 149 casts have no secondary-header code 96, so their originator-flag scheme is not identified by this file metadata.
- Across all temperature levels: 66,109 originator flags are code 1 and 177 are code 8, all in the 712 casts with flag-set code 3. Under the GTSPP/IODE definition, code 1 is good and code 8 is interpolated.
- The remaining 17,813 temperature originator flags are code 0 in casts without a recorded flag-set code. Do not interpret those zeros as a known QC outcome without the missing flag-set definition.

## GLD position/time variable discrepancy

The decoded headers show:
- 745 casts contain temperature (code 1) and Julian year-day (code 32)
- 116 casts contain temperature (code 1), latitude (code 30), longitude (code 31), and Julian year-day (code 32)

For the 116 casts with codes 30/31, the parser reads 12,283 per-level coordinate pairs; all are within the requested geographic box. The values vary along the profile rather than remaining constant.

However, the WOD23 manual describes latitude, longitude, and Julian year-day variables as available in SUR, APB, and UOR datasets, not GLD. The code tables identify codes 30, 31, and 32 as latitude, longitude, and Julian year-day, but their appearance as per-level arrays in this GLD file is a dataset-specific discrepancy requiring confirmation. Do not use these per-level coordinates/times for model-observation matching until the GLD-specific semantics are verified. The 745 casts without per-level latitude/longitude currently have only primary-header coordinates available.

## Interpretation and limitations

1. The `Q` prefix identifies the IQuOD layout used by the reference parser; it does not identify the underlying WOD release/version. The original WODSelect release/export settings remain unknown.
2. The GLD archive is a glider dataset. Casts from the same platform/cruise are not necessarily statistically independent; spatial/temporal autocorrelation and duplicate overlap with GTSPP or other archives must be assessed.
3. WOD temperature is variable code 1 in °C. It has not been shown to be potential temperature. Copernicus `tob`/`bottomT` are potential-temperature products, so direct numerical comparison is not approved without resolving thermodynamic comparability (including pressure and salinity requirements).
4. Depth is the observation's depth below the surface, not the local seabed depth. Near-bottom eligibility requires a location-specific ETOPO seabed-depth join and a documented separation rule.
5. The five-file NOAA delivery contains GLD, MRB, PFL, MBT, and XBT. OSD and CTD were absent from the complete delivered package; the 1,312-cast inventory/delivery discrepancy remains unresolved with NOAA.
6. No cast has yet been accepted as a near-bottom observation or paired with Copernicus. No bias, MAE, RMSE, validation sample size, or accuracy claim is made.

## Next steps

1. Verify the GLD-specific meaning and units of per-level codes 30/31/32 with NOAA/IQuOD documentation before using them for position/time matching.
2. Join cast/level observation depths to ETOPO seabed depths, using only geolocation fields whose semantics are verified. Report bottom separation continuously before choosing any threshold.
3. Preserve raw WOD cast, level, and originator flags. Build separate sensitivity subsets rather than silently dropping all nonzero flags.
4. Resolve in-situ temperature versus Copernicus potential-temperature comparability before calculating model-observation residuals.
5. Deduplicate WOD/GTSPP/GoMMAPPS records before pairing and account for repeated glider trajectories.
6. Keep all work research-only. Do not alter production species factors, ranges, gates, weights, scoring, confidence, ingestion, or publication behavior.

## References

- IQuOD parser source: https://github.com/IQuOD/wodpy/blob/116480b257a227ce38281d3836c40812246e5156/wodpy/wod.py
- IQuOD parser README/API: https://github.com/IQuOD/wodpy
- NOAA WOD23 User Manual: https://repository.library.noaa.gov/view/noaa/66124/noaa_66124_DS1.pdf
- NOAA WOD QC flag table: https://www.ncei.noaa.gov/access/world-ocean-database/CODES/definition-quality-flags.html
- NOAA originator flag-set table: https://www.ncei.noaa.gov/access/world-ocean-database/CODES/s_96_origflagset.html
- NOAA glider vehicle table: https://www.ncei.noaa.gov/access/world-ocean-database/CODES/s_74_ocean_vehicle.html
- NOAA probe type table: https://www.ncei.noaa.gov/access/world-ocean-database/CODES/s_29_probe_type.html
- NOAA temperature instrument table: https://www.ncei.noaa.gov/access/world-ocean-database/CODES/v_5_instrument.html


## Clarification: current NOAA code table confirms GLD auxiliary position/time variables | 2026-11-18

A follow-up check of the current NCEI online depth-dependent-variable code table resolves the apparent dataset-availability discrepancy. Unlike the 2024 WOD23 manual's prose summary, the current online table explicitly lists codes 30 (latitude), 31 (longitude), and 32 (Julian year-day) for GLD as well as SUR/APB/UOR. Its footnote says these codes are not depth-dependent variables and are not selectable in WODSelect.

Therefore their presence in the GLD archive is supported by the current code table and is not a format error. In this archive, 116 casts carry these values aligned with profile levels, and the decoded latitude/longitude values vary along the glider trajectory. Treat them as per-observation position/time metadata, not physical variables that depend on depth. The 745 remaining casts contain code 32 but no per-level latitude/longitude, so their primary-header coordinates remain the available spatial locator. Use the per-observation coordinates for the 116 casts after basic consistency checks; retain the source distinction in the normalized data.

Reference: https://www.ncei.noaa.gov/access/world-ocean-database/CODES/depth-dependent-variables.html


## Full-resolution ETOPO join preparation | 2026-11-18

The earlier Copernicus bathymetry artifact samples ETOPO on the approximately 0.083-degree Copernicus grid. That is useful for broad regional context but too coarse to assign seabed depth confidently to individual GLD measurements. Added a manual-only exporter for the NOAA NCEI ETOPO 2022 30-arc-second grid (0.008333 degrees) over the verified GLD coordinate envelope. The exporter preserves raw positive-up elevation, derives positive seafloor depth only for elevation below -1 m, keeps the -1 to +1 m coast band ambiguous, and validates full grid spacing/coverage. No GLD level has yet been joined to this grid.

Protocol: [WOD GLD ETOPO grid export](WOD_GLD_ETOPO_GRID_PROTOCOL_2026-11-18.md). Workflow: `.github/workflows/wod-gld-etopo-grid.yml`. Next: inspect the Python CI result, manually run the export workflow, then join the resulting grid to GLD observations and calculate continuous bottom separation. No near-bottom threshold or production behavior has changed.
