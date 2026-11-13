# Permit thermal evidence and SST scale audit: South Florida pilot

**Status:** research audit; no production model changes  
**Prepared:** 2026-11-13  
**Scope:** Permit (*Trachinotus falcatus*) thermal evidence and the configured South Florida SST input

## Executive decision

**Do not build or activate a Permit thermal-preference curve from the currently reviewed evidence.** The focused literature search did not identify a primary adult Permit thermal-physiology study establishing a thermal performance curve, acclimation response, critical thermal limits, or a South Florida adult temperature preference. This is a bounded search finding, not proof that no such study exists.

LUPITA's configured SST source is NASA JPL MUR v4.1 daily analysed sea-surface foundation temperature, nominally 0.01° (~1 km) native grid. However, the production configuration requests every fifth source cell. The effective sampled spacing is therefore 0.05°: approximately 5.6 km north-south and about 5.0 km east-west near 25.5°N. This is regional context, not a measurement of the temperature experienced by an individual Permit at a shallow flat, in the water column, or at a 15–40 m reef site.

**Recommendation:** SST may remain a broad regional environmental-context input, but it must not be represented as direct fish-experienced temperature or a validated Permit preference/tolerance feature. Keep current production profile values provisional and unchanged. Any refined thermal feature should remain shadow-only until the data scale and independent biological validation are addressed.

## 1. What the primary Permit evidence establishes

### Brownscombe et al. (2020): lower Florida Keys telemetry

Brownscombe et al., *Journal of Fish Biology* 96:469–479. DOI: https://doi.org/10.1111/jfb.14227

- 45 Permit were tagged within 16 km of the lower Florida Keys and monitored from March 2017 to June 2018.
- 75% of tagged individuals were detected in both nearshore flats (<3 m) and Florida Reef Tract habitat (15–40 m).
- Reef-tract occupancy peaked March–September, with highest detections in April and May.
- The work supports habitat connectivity and seasonal occupancy. It does not establish a thermal optimum, CTmax, acclimation curve, or numeric SST threshold.

### Brownscombe et al. / Florida Keys resource ecology (2022)

"Application of telemetry and stable isotope analyses to inform the resource ecology and management of a marine fish." DOI: https://doi.org/10.1111/1365-2664.14123

- Combines telemetry, stable isotopes and integrated modelling for Permit in the Florida Keys.
- Reports frequent movement among distinct habitat types and variation in resource use associated with habitat use and home-range size.
- Supports a habitat/resource-use interpretation, not a physiological temperature threshold.

### Florida Keys predator-prey telemetry

"Predator–prey landscapes of large sharks and game fishes in the Florida Keys." DOI: https://doi.org/10.1002/eap.2584

- The study identifies environmental variation in predator/prey overlap, including location, habitat, time of year, lunar cycle, depth and water temperature.
- Temperature is one contextual covariate in a spatial overlap analysis. It is not a Permit thermal-performance experiment and does not establish a preferred or tolerated temperature range.

### FishBase modeled preferred temperature

The FishBase species summary currently reports an estimated preferred temperature of 23.2–28.0 °C (mean 26.1 °C), based on 624 cells and a modeled estimate (reference 123201).

- This is a model-derived ecological estimate, not a direct controlled thermal-preference experiment or adult South Florida validation.
- The underlying reference/method and spatial and life-stage representativeness must be traced before using it in a species profile.
- Do not silently substitute this estimate for the existing Permit SST ideal range or treat it as a physiological tolerance boundary.

### Direct physiology evidence search outcome

Focused searches for *Trachinotus falcatus* critical thermal maximum, thermal acclimation, thermal performance, metabolic performance and field temperature loggers did not surface a primary adult Permit physiology study with usable quantitative endpoints.

This does not establish that no such work exists. It establishes that no defensible species-specific adult thermal curve has yet been verified for this pilot. The next search should include theses, older aquaculture literature, regional technical reports, and studies under alternate common names/taxonomic indexing.

## 2. Actual LUPITA SST input audit

### Source and native product

The configured source in `config/sources.json` is:

- Dataset: `jplMURSST41`
- Variable: `analysed_sst`
- Host: NOAA CoastWatch ERDDAP
- Product: NASA JPL MUR SST Analysis fv04.1
- Native spatial coordinate spacing: 0.01° latitude and longitude, commonly described as approximately 1 km.
- Time: daily analysed fields.
- Variable semantics: analysed sea-surface foundation temperature, not temperature at arbitrary depth.
- Product history describes a nominal four-day latency for the final analysis; recent fields may be revised daily.

Primary product metadata: https://podaac.jpl.nasa.gov/dataset/MUR-JPL-L4-GLOB-v4.1  
ERDDAP metadata: https://coastwatch.pfeg.noaa.gov/erddap/info/jplMURSST41/index.html

### Effective production sampling

The current production configuration sets:

```json
"stride": {
  "latitude": 5,
  "longitude": 5
}
```

The ERDDAP request builder applies these stride values directly to source grid indices. Therefore, LUPITA does not ingest the full nominal 0.01° MUR grid. It samples every fifth source cell:

- Latitude spacing: 0.05° ≈ 5.56 km.
- Longitude spacing: 0.05° × cos(latitude); at 25.5°N ≈ 5.04 km.
- Effective sample spacing near the South Florida pilot: roughly 5 km, not 1 km.

This is sampling, not evidence that the underlying MUR product itself has a 5 km native resolution. The production grid's effective spacing is determined by the configured stride.

### How site SST is selected

The current `pipeline/sites.py` implementation:

1. First searches for a successful buoy observation with water temperature within 40 km of the site and selects the nearest qualifying buoy.
2. If no such buoy is available, searches the SST grid for finite cells within 8 km of the site and selects the nearest cell.
3. Labels the satellite value as modeled and reports the distance to the selected cell.

Consequences:

- A site may receive a buoy measurement from as far as 40 km away. That value is measured at the station, not necessarily at the fishing site or at the fish's depth.
- The satellite fallback can select a sampled grid cell up to 8 km away. Given approximately 5 km cell spacing, the nearest usable cell can be several kilometres from the site.
- The site value is not a local in-situ measurement. The distance label is essential context, not decorative metadata.

### Temporal support

The ERDDAP request asks for the latest available time index, not a time series or an hourly observation. The value is a daily analysed field. It cannot resolve short-lived tidal-flat heating, daily thermal extremes, or the precise temperature encountered during a Permit movement between habitats.

## 3. Why this matters for Permit habitat use

The Florida Keys telemetry evidence distinguishes at least two important contexts:

- Nearshore flats: less than 3 m depth, used primarily for foraging.
- Florida Reef Tract: approximately 15–40 m depth, with seasonal occupancy and spawning relevance.

A daily surface-foundation temperature sampled at roughly 5 km spacing cannot be assumed to represent:

- shallow water temperature over a sun-heated flat;
- bottom temperature at a reef site 15–40 m deep;
- temperature gradients across channels, banks, reef edges or depth strata;
- the thermal exposure of a moving fish over the period represented by a daily composite.

The mismatch is both spatial and vertical, and also temporal. A more precise coordinate grid would not by itself solve the vertical or temporal mismatch.

## 4. Recommendations

### Retain, but narrow the meaning of, SST

SST can remain useful as a broad regional ocean-temperature context layer, especially for regional-scale conditions and fronts. It should not be described as direct Permit habitat temperature or a validated Permit thermal-preference factor.

### Do not infer an ideal range from weak proxies

- Do not use the FishBase modeled 23.2–28.0 °C estimate as a production ideal range until its underlying method/reference and population/life-stage relevance are traced.
- Do not convert a temperature covariate from a predator/prey overlap model into a Permit thermal preference.
- Do not derive a thermal gate from a habitat telemetry study that did not estimate physiological thermal endpoints.

### Improve evidence and measurement alignment before modelling

1. Search theses, technical reports, aquaculture studies and older literature for direct adult Permit thermal physiology.
2. Trace FishBase reference 123201 and assess its method, input data, geography and life-stage scope.
3. Investigate available South Florida moored temperature observations with known depth and sampling interval near representative flats and reef-tract sites.
4. Audit whether the buoy fallback can report station depth, sensor depth, station distance and observation timestamp consistently in site output.
5. Consider retaining the native MUR 0.01° grid for a South Florida-only extraction only if the product's true spatial support, request reliability and validation benefit justify the operational cost. Higher grid density does not equal independent 1 km biological detail.
6. If a depth-aware thermal context is needed, identify an independently validated subsurface temperature product or in-situ network. Do not manufacture bottom temperature by adjusting SST with bathymetry.
7. Keep any new candidate feature in shadow mode and compare it against independent observations before any production scoring change.

## 5. Production safeguards

- No production species JSON, temperature ranges, ideal ranges, factor weights, active flags, gates, required flags, prediction formulas, site rankings or API fields are changed by this audit.
- Existing Permit SST values remain provisional.
- Occurrence association, thermal preference, physiological performance and acute thermal tolerance remain distinct concepts.
- SST remains a surface product; it is not a proxy for bottom temperature without independent evidence.
- Missing or unmapped subsurface temperature remains unknown, not zero suitability or confirmed absence.
- The South Florida pilot remains the only validation region.

## References

- Brownscombe et al. (2020), Florida Keys Permit telemetry: https://doi.org/10.1111/jfb.14227
- Brownscombe et al. (2022), Permit resource ecology: https://doi.org/10.1111/1365-2664.14123
- Florida Keys predator-prey telemetry: https://doi.org/10.1002/eap.2584
- FishBase Permit species summary (modeled preferred temperature; trace reference 123201): https://www.fishbase.se/country/CountrySpeciesSummary.php?c_code=660&genusname=Trachinotus&speciesname=falcatus
- NASA JPL MUR SST v4.1 product: https://podaac.jpl.nasa.gov/dataset/MUR-JPL-L4-GLOB-v4.1
- NOAA CoastWatch ERDDAP dataset metadata: https://coastwatch.pfeg.noaa.gov/erddap/info/jplMURSST41/index.html
- Ern, Andreassen & Jutfelt (2023), general review of acute upper thermal tolerance mechanisms in fish: https://doi.org/10.1152/physiol.00027.2022


## 6. South Florida in-situ temperature source audit

The source review identified two particularly useful public data streams. They answer different parts of the scale problem and should not be treated as interchangeable.

### USGS CREST Florida Keys underwater temperature release (Version 9)

**Source:** Kuffner, I.B. (2024), USGS data release, DOI: https://doi.org/10.5066/F71C1TZK  
**Landing page:** https://coastal.er.usgs.gov/data-release/doi-F71C1TZK/  
**Direct archive:** https://coastal.er.usgs.gov/data-release/doi-F71C1TZK/data/FL_coral_underwater_temps_to_Jul2024.zip  
**Metadata:** https://cmgds.marine.usgs.gov/catalog/spcmsc/FL_coral_underwater_temps_metadata_v9.html

Verified source characteristics:

- Ten offshore reef sites across Biscayne National Park, Florida Keys National Marine Sanctuary and Dry Tortugas National Park.
- Measurements every 15 minutes.
- HOBO Water Temp Pro V2 loggers deployed in duplicate, attached to reef-fixed concrete blocks.
- Logger depths are 7–16 feet of seawater (approximately 2.1–4.9 m).
- Version 9 includes data through July 2024. Some site records began in 2009; the three Biscayne National Park sites (Ball Buoy North, Shadow Reef, Brewster Reef) began in May 2023.
- This is direct in-water logger temperature at shallow reef sites, not satellite SST.

The metadata reports these observed ranges for the three Biscayne sites:

| Site | Coordinates | Logger depth | Data period | Reported temperature range |
|---|---|---:|---|---:|
| Brewster Reef | 25.56676, -80.09974 | 13 ft / 4.0 m | May 2023–Jul 2024 | 21.569–32.549 °C |
| Shadow Reef | 25.47775, -80.14088 | 12 ft / 3.7 m | May 2023–Jul 2024 | 20.138–33.261 °C |
| Ball Buoy North | 25.31877, -80.18426 | 11 ft / 3.4 m | May 2023–Jul 2024 | 20.591–33.248 °C |

**Interpretation boundary:** these are site-level extrema reported in dataset metadata, not a substitute for a row-level time-series analysis. The sites are shallow reef locations, not 15–40 m reef-tract stations. They are useful for shallow nearshore reef context and for comparing high-frequency in-water temperatures against daily satellite SST. They do not directly characterize Permit thermal exposure on the deeper reef tract.

### FWC-FWRI FLKEYS Array via SECOORA ERDDAP

**Source portal:** https://erddap.secoora.org/erddap/index.html  
**Provider:** Florida Fish and Wildlife Conservation Commission, Fish and Wildlife Research Institute (FWC-FWRI), distributed through SECOORA.  
**Example station:** RHA54, https://erddap.secoora.org/erddap/tabledap/org_secoora_flkeys_rha54.html

The station metadata exposes time, latitude, longitude, vertical coordinate (z, metres, positive up), water temperature, aggregate QARTOD quality flag and individual QC-test flags. The example RHA54 station metadata reports:

- Position: 24.5056°N, 83.1305°W.
- Sensor vertical coordinate: z = -43 m (43 m below the datum).
- Available period in the inspected metadata: 2023-09-22 14:00 UTC to 2024-08-14 13:00 UTC.
- Reported temperature range: 20.653–30.844 °C.
- Aggregate quality flags include values 1–4. The ERDDAP metadata defines 1=PASS, 2=NOT_EVALUATED, 3=SUSPECT, 4=FAIL, and 9=MISSING. These flags must be applied before calculating any summary statistics; do not treat every returned value as valid.

A second example, station HFA04, reports 24.6687°N, 82.8926°W and z = -11 m, with an available period from 2020-12-11 to 2022-08-12 and a reported temperature range of 20.561–31.217 °C. This is useful as a shallower comparison station, but its time coverage is older and should be checked before any comparison with current MUR fields.

**Interpretation boundary:** RHA54 is deeper than the 15–40 m Permit reef-tract range documented by the telemetry study. It can contribute regional deep-water context, but it is not a direct habitat-matched proxy for every Permit reef site. Station HFA04 is much shallower. Station selection must be based on actual coordinates, sensor depth, temporal overlap and habitat context, not just a station's broad “Florida Keys” label.

The ERDDAP pages expose a public tabledap interface for requesting timestamped rows and their QC flags. However, the row-level CSV request could not be retrieved in this research session. Therefore, the values above are metadata-reported station ranges and coverage, **not a claimed extraction of individual observations**. A row-level extract remains a required next validation step. A reproducible query should request at least:
`time, latitude, longitude, z, sea_water_temperature, sea_water_temperature_qc_agg, sea_water_temperature_qc_tests`
with a narrow time window and explicit QC filtering. Preserve raw timestamps and QC flags in the research extract.

### Biscayne Bay Aquatic Preserves continuous monitoring

**Program:** Florida DEP / Biscayne Bay Aquatic Preserves Continuous Water Quality Monitoring (SEACAR program 5077).  
**Program page:** https://data.florida-seacar.org/programs/details/5077  
**Data portal:** https://www.floridaapdata.org/

- Five fixed stations: BBBB14, BBJT71, BBLR03, BBMRSC and BBMRDW.
- 15-minute observations, beginning in 2019 and continuing.
- Includes water temperature, depth, salinity, dissolved oxygen, pH, turbidity and other parameters.
- Current methods use YSI EXO2 sondes, with earlier instrument models at some stations.
- The program describes its habitat as water column and provides yearly CSV files through the Florida Aquatic Preserve Data Portal.
- The portal requires a valid email for data download, so this is not as frictionless as the public ERDDAP source.

This network is valuable for Biscayne Bay shallow-estuary context, especially where salinity and depth covary with temperature. It is not an offshore reef-tract substitute and must not be generalized to deeper Permit habitat.

## 7. Source ranking and next data-validation step

For the South Florida pilot, use the sources according to their actual sampling support:

1. **FWC-FWRI FLKEYS Array / SECOORA ERDDAP:** best candidate for depth-labelled, timestamped bottom-temperature observations and QC-aware station extraction. Select stations only after matching their location and sensor depth to the target habitat context.
2. **USGS CREST Version 9:** strong high-frequency in-water reference at shallow reef sites in Biscayne National Park and the Florida Keys. Particularly useful for comparing daily MUR surface SST with shallow reef logger temperature; it does not cover the 15–40 m reef depth band.
3. **Biscayne Bay Aquatic Preserves:** useful 15-minute estuarine water-column temperature and co-variable context; data download requires portal registration/email and the network is not offshore reef habitat.

The next validation extract should contain, for each selected station:

- station identifier, provider and dataset version;
- latitude, longitude, sensor vertical coordinate and documented sensor/deployment depth;
- timestamp and timezone;
- raw temperature and units;
- aggregate and individual QC flags;
- data coverage, missingness and temporal gaps;
- distance to representative South Florida flats and reef-tract pilot sites;
- concurrent MUR daily SST values and the exact MUR cell/time selected by LUPITA.

Summaries should be calculated only from QC-passing observations, with non-passing and unevaluated counts reported separately. Compare seasonal distributions, daily ranges, diel variability and surface-to-bottom differences only where timestamps and locations support a valid match. Do not convert any of these environmental distributions into a Permit preference or tolerance curve.

**Current extraction status:** source discovery and metadata-level station screening completed; individual-row CSV extraction and QC-aware statistical summaries remain pending. No production model or species profile values were changed.
