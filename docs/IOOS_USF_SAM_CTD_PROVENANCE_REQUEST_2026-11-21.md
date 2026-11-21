# USF Sam GPCTD provenance request | 2026-11-21

## Purpose

Obtain the instrument- and deployment-specific evidence needed before converting the USF Sam 2024-02-16 to 2024-03-15 glider observations from measured in-situ temperature to TEOS-10 potential temperature for comparison with Copernicus bottomT.

This is a research-only provenance gate. Do not infer configuration from a generic GPCTD manual or from sensor model alone.

## Verified public record

Dataset: `usf-sam-20240216T0000`, WMO 4801942, University of South Florida / GCOOS.

Public ERDDAP record:
https://gliders.ioos.us/erddap/tabledap/usf-sam-20240216T0000.html

- CTD metadata: Sea-Bird Scientific GPCTD, serial 9013.
- Listed calibration date: 2012-07-08.
- Factory calibrated: True; user calibrated: False.
- Source merged DBA: `/data/gandalf/deployments/usf/usf-sam/processed_data/dba/merged/0000339.dba`.
- Source sensor file example: `usf-sam-2024-046-1-344-sbd(02140344)`.
- The public record's history states that `dba_to_ngdac_profile_nc.py` generated the profile NetCDF from the merged DBA file.
- Temperature: measured, Celsius; published metadata does not specify ITS-90 vs IPTS-68.
- Salinity: calculated practical salinity.
- Pressure: published units say bar, but the comment says the alias for `sci_water_pressure` is multiplied by 10 to convert from bar to dbar. This leaves the actual exported pressure units ambiguous.
- Public ERDDAP product is marked processing level Level 0 and product version 0.0.

IOOS NGDAC documentation says provider-submitted profile NetCDF files are aggregated and served publicly, while original submitted files are archived but not publicly accessible in their original form. GANDALF documentation says mission files are permanently archived, but raw-data access is password-controlled and limited to the PIs who generated the data.

## Exact items requested from USF / GCOOS

1. **Temperature scale**
   - Confirm whether the temperature values in the merged DBA / public NetCDF are ITS-90 or IPTS-68.
   - If conversion occurred, identify where and provide the exact conversion.
   - Provide the serial-9013 temperature calibration certificate or calibration sheet corresponding to the 2012-07-08 calibration date, if available.

2. **GPCTD configuration**
   - Provide the instrument configuration/setup file and the relevant temperature, conductivity, and pressure calibration coefficients used during the deployment.
   - Confirm firmware/configuration and whether any calibration coefficients or settings changed after the listed factory calibration.

3. **Pressure units and processing**
   - Confirm whether the public ERDDAP `pressure` values (range approximately 0.58–141.67) are in dbar or bar.
   - Explain the metadata comment stating that `sci_water_pressure` was multiplied by 10 to convert from bar to dbar, while the published variable units remain `bar`.
   - Confirm whether the merged DBA values are raw sensor output, converted engineering units, or further processed values.
   - Identify the exact source and conversion used for `depth` / `m_depth`.

4. **Salinity and CTD processing**
   - Confirm how practical salinity was calculated (conductivity/temperature/pressure inputs and algorithm/software version).
   - State whether thermal-lag correction, conductivity alignment, despiking, bin averaging, or other CTD processing was applied before the merged DBA / NetCDF was generated.
   - Identify any known processing limitations relevant to temperature/salinity pairing.

5. **Source files and provenance**
   - If releasable, provide the merged source file `0000339.dba`, the relevant source SBD/EBD files, and associated mission/configuration/log files.
   - If raw files cannot be shared, provide a small representative extract plus the configuration/calibration records and a written explanation of the transformations.
   - Confirm whether the source DBA and the ERDDAP NetCDF represent the same delayed-mode processing state.

## Why these details matter

- GSW TEOS-10 calculations require in-situ temperature on ITS-90 and sea pressure in dbar.
- Sea-Bird documents the scale relationship as IPTS-68 = 1.00024 × ITS-90. The difference is small but material for careful oceanographic comparison.
- The generic GPCTD product documentation describes expected instrument capabilities, not the configuration of serial 9013 on this deployment.
- A depth-derived pressure estimate using GSW `p_from_z(-depth, latitude)` can be evaluated as a separately labelled sensitivity path if measured pressure provenance cannot be resolved. It must not silently replace the measured variable.
- No potential-temperature conversion or Copernicus accuracy metric should be produced until the temperature scale is established or explicitly treated as an unresolved sensitivity.

## Current disposition

- Public metadata lineage is identified.
- Exact sensor serial and listed calibration date are known.
- Temperature scale is **unresolved**.
- Pressure output units are **unresolved**.
- Calibration certificate/configuration and source DBA are **not publicly retrievable from the documented IOOS/GANDALF access routes**.
- No TEOS-10 conversion, Copernicus pairing, or production behavior change has been performed.

## Sources

- IOOS dataset metadata: https://gliders.ioos.us/erddap/info/usf-sam-20240216T0000/index.html
- IOOS NGDAC overview: https://ioos.github.io/glider-dac/
- GANDALF data access description: https://gandalf.gcoos.org/about/gandalf
- USF Glider Deployments: https://www.usf.edu/marine-science/research/partners-and-groups/center-for-red-tide-tracking-and-forecasting/project-activities/glider-deployments.aspx
- Sea-Bird ITS-90 / IPTS-68 relationship: https://www.seabird.com/faqs/faq000010
- Sea-Bird GPCTD product page: https://www.seabird.com/products/glider-payload-ctd-gpctd?id=60762467712
- GSW-Python conversions: https://teos-10.github.io/GSW-Python/conversions.html


## Additional instrument-manual and pressure/depth evidence | 2026-11-21

A manufacturer GPCTD User's Manual, revision 004 (2013-09-26), was inspected. It states that GPCTD OutputFormat 0 and 1 provide engineering-unit output with temperature explicitly in ITS-90 °C and pressure in decibars. OutputFormat 2 is raw sensor counts. The same manual says calibration coefficients are factory-set and should agree with the instrument's calibration certificate. This is stronger than generic product marketing, but the public USF dataset does not expose the deployed OutputFormat setting or the serial-9013 calibration certificate. Therefore it supports a plausible ITS-90 interpretation only if the glider was configured for engineering-unit output; do not yet treat the setting as deployment-verified. Manual: https://misclab.umeoce.maine.edu/ftp/instruments/CTD%2019%2B/seabird%20website%20disc%20Dec%202016/website/pdf_documents/manuals/GliderPayloadCTD_004.pdf

A direct row-level check of the refreshed 72,426 paired pressure/depth values shows pressure/depth correlation 0.9999999964, mean ratio pressure/depth 1.006743, median ratio 1.006735, and observed pressure range 0.58–141.67 paired with depth 0.576–140.683 m. These values are physically consistent with pressure in dbar and depth in metres, not pressure in bar. The public pressure metadata comment says the source sensor sci_water_pressure is multiplied by 10 to convert bar to dbar, which aligns with the numeric evidence; the units attribute 'bar' is therefore likely stale/incorrect. This is a strong empirical unit diagnosis, not yet a replacement for the provider's explicit confirmation of the exact source transformation. The pressure data can now be treated as a candidate measured-dbar input for a research-only sensitivity analysis, while retaining the published units and documenting the conflict. Do not silently rewrite the source file's units.

The exact provider request is narrowed: confirm the configured GPCTD OutputFormat (0, 1, or 2) during this deployment, whether the public temperature is the GPCTD engineering output (ITS-90 under formats 0/1), confirm the pressure conversion to dbar and why ERDDAP units remain bar, and provide the serial-9013 calibration certificate/configuration or coefficient readout. Raw mission files remain PI-restricted through GANDALF. Until the deployment setting is confirmed, ITS-90 remains strongly supported but not fully proven.
