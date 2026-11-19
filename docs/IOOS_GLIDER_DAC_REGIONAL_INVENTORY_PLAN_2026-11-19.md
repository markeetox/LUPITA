# IOOS Glider DAC regional profile inventory plan | 2026-11-19

## Why this route

NCEI's GTSPP interactive query returned Service Unavailable to the user on 2026-11-19. NCEI's public service status currently reports intermittent degraded order fulfillment during cloud migration and warns that many access portals and data folders are unavailable. Do not keep retrying GTSPP or WODSelect while this service condition persists.

The IOOS National Glider Data Assembly Center (NGDAC) is a separate public distribution path for underwater-glider observations. The DAC publishes trajectory/profile datasets through ERDDAP and THREDDS; it includes historical missions dating to 2005 and contributions from NOAA AOML, universities, and regional IOOS associations. This is not a replacement for WOD as a whole: glider observations are a subset of platforms and can be spatially/temporally clustered.

Official entry points:
- IOOS Glider DAC: https://gliders.ioos.us/
- ERDDAP catalog: https://gliders.ioos.us/erddap/info/index.html
- THREDDS catalog: https://gliders.ioos.us/thredds/catalog.html
- NGDAC documentation: https://ioos.github.io/glider-dac/
- IOOS data access overview: https://ioos.noaa.gov/data/access-ioos-data/

## Initial verified candidate: USF Sam deployment

The NGDAC catalog exposes dataset `usf-sam-20240216T0000`, a University of South Florida / GCOOS Slocum-glider deployment.

Verified metadata:
- Time coverage: 2024-02-16T16:25:06Z to 2024-03-15T10:51:35Z.
- Geographic bounds: 27.5879888–28.0393764°N, -84.5671611 to -83.1217124°E.
- Maximum recorded depth: 140.6833 m; minimum: 0.5761 m.
- Instrument: CTD.
- Data structure: trajectory-profile.
- Dataset carries profile identifiers, WMO ID 4801942, CTD depth/pressure, and QARTOD temperature/pressure flags.
- Temperature is a measured CTD variable in Celsius; metadata reports sensor accuracy 0.004°C and observed dataset range 16.8621–21.7797°C.
- Depth is reported positive down in metres, calculated from the CTD source sensor; metadata reports accuracy 0.01 m. Pressure is separately reported in bar.
- The QARTOD temperature primary flag has observed values spanning 1–4, so the deployment includes PASS through FAIL outcomes; flags use 1=PASS, 2=NOT_EVALUATED, 3=SUSPECT, 4=FAIL, 9=MISSING.
- Regional association: GCOOS-RA; sea area: Gulf of Mexico.
- Dataset is marked as completed in the DAC, but its license/metadata warns data are provided as-is without an implied QA/QC assurance. Apply the supplied QC flags rather than assuming all observations pass.

This deployment is geographically outside the existing Gulf Copernicus candidate box (-89.0 to -87.5°W, 29.0 to 30.0°N). It is therefore a candidate for a **separate West Florida shelf/slope validation stratum**, not a match to the existing Gulf pilot. Its maximum depth does not establish near-bottom coverage; ETOPO separation must be calculated for individual profiles.

Dataset references:
- NGDAC metadata: https://gliders.ioos.us/erddap/info/usf-sam-20240216T0000/index.html
- ERDDAP data form: https://gliders.ioos.us/erddap/tabledap/usf-sam-20240216T0000.html
- Aggregated USF quarterly listing: https://erddap.aoml.noaa.gov/hdb/erddap/tabledap/GLIDERS_2024_01_03.subset

## Screening protocol

1. Search the NGDAC ERDDAP catalog and deployment metadata for profiles whose actual coordinate bounds intersect the four existing candidate boxes. Do not select deployments based only on broad global bounding boxes.
2. Preserve deployment ID, WMO ID, profile ID, profile time, point-level time/coordinates, depth, pressure, temperature, units, sensor/instrument metadata, all QARTOD flags, and original provenance.
3. Treat profile position/time fields separately from point-level interpolated position/time. The dataset's profile-level position/time fields are calculated/interpolated; point-level precise position/time fields are measured. Record which representation is used for each observation and preserve both where available.
4. Apply the documented QARTOD flag meanings. Keep PASS, NOT_EVALUATED, SUSPECT, FAIL, and MISSING distinct; do not silently treat NOT_EVALUATED as PASS.
5. Join each observation to ETOPO and calculate continuous bottom separation. Keep negative separation visible. No near-bottom cutoff is chosen yet.
6. Compare actual glider observation timestamps and locations with Copernicus analysis/forecast fields. The glider's temperature is measured in-situ; Copernicus bottomT/tob is sea-floor potential temperature. Thermodynamic comparability and time/space interpolation uncertainty must be resolved before residual metrics.
7. Deduplicate against WOD/GTSPP/other glider archives by deployment, WMO, profile, time, and position where possible. A profile mirrored in multiple archives is one observation.

## Current status and boundaries

- NCEI GTSPP query returned Service Unavailable; no station count was obtained.
- IOOS NGDAC/ERDDAP catalog and individual deployment metadata are discoverable. One Gulf of Mexico USF Sam deployment has been verified from metadata.
- No glider profile data have yet been downloaded, ETOPO-joined, or paired to Copernicus.
- The USF Sam deployment is outside the current Gulf pilot box and is not yet accepted as near-bottom eligible.
- No validation sample size, bias, MAE, RMSE, or Copernicus accuracy result is claimed.

This is research-only. No production ingestion, species profile, SST factor, numerical range, weight, gate, score, confidence, or publication behavior changes.
