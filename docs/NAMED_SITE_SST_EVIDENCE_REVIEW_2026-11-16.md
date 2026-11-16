# Named-site SST evidence review: 20 homepage-only profiles

**Date:** 2026-11-16  
**Branch:** `main`  
**Scope:** all 20 named-site species profiles whose active `sst_c` factor was marked `sourced` but cited only the generic NOAA Fisheries homepage.  
**Review type:** source discovery and claim-fit assessment.  
**Boundary:** no species profile, evidence status, source list, numeric range, ideal band, weight, active flag, gate, required flag, or scoring behavior was changed.

## Executive result

The generic homepage citations were not adequate factor-level evidence. A species page or study can improve traceability, but it still does not automatically validate the exact configured temperature band.

This review located species-specific evidence for most of the 20 profiles. The evidence varies substantially in what it actually measures:

- adult field occupancy or observed temperature ranges;
- juvenile or spawning-stage temperatures;
- migration timing correlated with seasonal temperature;
- modeled distribution-derived temperature associations;
- broad collection/occurrence ranges;
- habitat descriptions without numerical thermal evidence.

**One profile has a particularly strong match:** Spanish mackerel has authoritative species-specific sources that closely support both the configured lower range and ideal interval.

**Several profiles have useful partial evidence but not a validated optimum:** Atlantic croaker, blacktip shark, bluefish, bull shark, ladyfish, lane snapper, scup, spotted seatrout, striped bass, summer flounder, tautog, and winter flounder.

**Several remain unsupported for their configured numeric band:** American shad (only stage-specific spawning/preference evidence), false albacore (model-derived range only), spinner shark (very small juvenile sample and no adult data), spot, tripletail, weakfish, and white grunt.

The classifications below are recommendations for owner review, not automatic profile edits. The existing `sourced` labels should not remain unqualified simply because new URLs can be found.

## Review standard

A reference was evaluated against five questions:

1. Is the source specific to the species?
2. Does it report temperature measurements, preference, tolerance, or only seasonal movement/habitat?
3. Which life stage, stock, and region does it describe?
4. Does it support the configured outer range, the ideal interval, both, or neither?
5. Is the input actually SST, or is the evidence about bottom water, spawning water, laboratory tolerance, or an unrelated life stage?

**Observed occurrence is not preference.** A species caught at a temperature does not prove it prefers that temperature. A lethal threshold is not an ideal range. A spawning temperature is not a year-round adult habitat preference. A modeled distribution estimate is not a controlled thermal preference experiment.

## Species-by-species findings

| Species | Configured range °C | Configured ideal °C | Evidence found | Assessment and recommended status |
|---|---:|---:|---|---|
| American shad | 8–24 | 12–19 | USFWS reports peak spawning at 65.3°F (about 18.5°C). Ontario life-history data list a preferred range of 13–18°C and spawning at 12–21°C. | **Partial, life-stage/region mismatch.** The preferred range is freshwater/river context and spawning is stage-specific; neither validates a year-round coastal SST suitability band for all named sites. Recommend `provisional` unless the profile is explicitly scoped to the appropriate stock, season, and life stage. |
| Atlantic croaker | 10–30 | 16–26 | UF/IFAS reports bottom temperatures of 9–32°C and greatest abundance above 24°C. NOAA/NCEI describes temperature-dependent seasonal inshore/offshore movement. | **Partly supported.** The outer range is close to a reported bottom-temperature occurrence range, but the configured ideal midpoint/interval does not match the reported abundance signal, and bottom temperature is not necessarily surface temperature. Recommend `partly_sourced`; review ideal band and input-depth mismatch before any numeric change. |
| Blacktip shark | 18–32 | 22–30 | NOAA/NMFS Florida nursery-ground surveys report field temperatures by life stage in the northern Gulf of Florida: juveniles 17.4–31.7°C (mean 29.1; N=81), adults 17.4–31.7°C (mean 26.8; N=30), and YOY 28.2–30.8°C (N=20). | **Partly supported.** The outer band overlaps measured Florida habitat temperatures, but the study area is St. George Sound to Anclote Keys, not South Florida, and the data do not validate the configured ideal interval. Recommend `partly_sourced`. |
| Bluefish | 12–28 | 18–25 | NOAA essential-fish-habitat documentation reports adults usually in water above 14–16°C and observed tolerance from 11.8–30.4°C, with stress at extremes. NOAA species material describes seasonal migration with water temperature. | **Partly supported.** The broad range overlaps adult field/life-history observations, but the ideal interval is not established by the cited evidence and bluefish are migratory across a large latitudinal range. Recommend `partly_sourced`. |
| Bull shark | 18–34 | 22–31 | A University of Miami Biscayne Bay telemetry study reports a preferred local range of 24–26°C for tagged bull sharks. A juvenile Gulf study reports high-temperature habitat associations and notes southern Florida juvenile preference estimates of 27–37.3°C from earlier work. | **Strong regional partial evidence, life-stage sensitive.** This is unusually relevant to South Florida, but adult/subadult Biscayne Bay findings and juvenile thermal habitat are not interchangeable. The configured ideal 22–31°C is much broader than the reported Biscayne Bay preference. Recommend `partly_sourced`, with explicit life-stage and regional notes. |
| False albacore | 16–30 | 20–27 | FishBase displays a model-derived preferred-temperature estimate of 11.5–27.8°C (mean 23.3°C) based on 1,094 cells. | **Model-derived, not direct validation.** The estimate is directionally relevant but is a spatial/model association, not a physiological preference study or a South Florida calibration. It does not support the current 30°C upper limit or exact ideal band. Recommend `provisional` or an explicitly documented `partly_sourced` status only if model-derived distribution evidence is accepted as partial support. Conservative recommendation: `provisional`. |
| Ladyfish | 18–32 | 22–30 | Florida Museum of Natural History reports ladyfish as thermophilic, notes cold-related fish kills in Florida, and records collections from 11–35°C. | **Partly supported for broad occurrence only.** A collection range is not an optimum or preference curve; the configured ideal interval is not established. Recommend `partly_sourced` only if the profile notes that the source supports occurrence/tolerance context, not ideal preference. |
| Lane snapper | 18–31 | 22–29 | Gulf of Mexico life-history/EFH documentation reports adult lane snapper at 16–29°C and notes mortality at low temperatures around 8–10°C. | **Partly supported.** The recorded adult range overlaps much of the configured band, but it does not validate the 22–29°C ideal interval or a precise South Florida surface-temperature response. Recommend `partly_sourced`. |
| Scup | 8–24 | 12–20 | NOAA life-history documentation reports adult summer temperatures around 7–25°C and notes acclimation/critical maxima separately. ASMFC reports scup are most frequently encountered at 55–77°F (about 12.8–25°C). | **Partly supported.** Adult occurrence supports much of the configured range; the ideal interval is narrower and cooler than the ASMFC most-frequent range. Scup are a northern/mid-Atlantic species, with southern range near Cape Hatteras. Recommend `partly_sourced`; review geographic relevance for each named site. |
| Spanish mackerel | 18–30 | 21–27 | NOAA Fisheries says Spanish mackerel prefer water above 68°F (20°C). ASMFC habitat factsheet reports preference for 21–27°C and rare occurrence below 18°C. | **Best-supported profile in this review.** These sources closely match the configured 18°C lower edge and 21–27°C ideal interval. Recommend retaining `sourced` after replacing the generic homepage citation with these specific references and documenting that the evidence is a broad species-level habitat association, not a calibrated local catch curve. |
| Spinner shark | 18–32 | 22–30 | NOAA/NMFS Florida nursery survey reports YOY at 27.3–27.8°C (N=3), one juvenile at 25.6°C (N=1), and no adult observations in that table. A separate northern Gulf juvenile habitat model identified preference for temperatures above 30°C. | **Very limited, stage-specific partial evidence.** The local field sample is tiny and has no adult data; the model concerns juvenile habitat. Neither validates the broad adult/site ideal interval. Recommend `provisional` pending better sample coverage. |
| Spot | 10–30 | 16–26 | NOAA/EPA life-history material describes seasonal movement associated with cooling but provides no numerical temperature preference in the reviewed species table. ASMFC documents seasonal offshore movement as temperatures decrease. FishBase notes spot are absent in southern Florida. | **Not supported for numeric band; geographic caution.** The references establish seasonal behavior, not the configured interval. The southern-Florida distribution note is a potential site applicability issue. Recommend `needs_source` or `provisional`; do not present the range as preferred thermal habitat. |
| Spotted seatrout | 10–32 | 18–28 | Southwest Florida RECON reports preferred temperatures around 69–80°F (20.6–26.7°C), cooler-water seeking above 88°F, and possible mortality below 48°F. | **Partly supported and locally relevant.** The reported preference supports the central portion of the ideal band, while the outer limits are broader than the cited preferred range. This is regional field/extension information rather than a controlled thermal-performance study. Recommend `partly_sourced`. |
| Striped bass | 2–26 | 12–20 | NOAA/EPA life-history sources report spawning temperatures of 10–23°C with peak spawning around 15–20°C. Striped bass include distinct Atlantic and Gulf populations and are anadromous. | **Partial, stage-specific evidence.** The peak spawning interval overlaps the configured ideal but does not validate year-round adult habitat preference. Recommend `partly_sourced` only with spawning-stage caveat; otherwise `provisional` for a general site-SST model. |
| Summer flounder | 8–26 | 14–22 | NOAA reports seasonal inshore/offshore migration with temperature. A species-level synthesis reports inshore occurrence around 9–27°C and offshore winter occurrence around 4–13°C. | **Partly supported for seasonal occurrence, not ideal preference.** The broad range overlaps reported seasonal occupancy, but the ideal interval is not established as a general preference curve. Recommend `partly_sourced` with season and life-stage caveats. |
| Tautog | 6–24 | 10–18 | Massachusetts DMF reports inshore migration as water approaches 48°F (8.9°C) in spring and offshore movement when temperatures fall below 52°F (11.1°C) in autumn. | **Partial behavioral evidence only.** These are migration cues, not a preferred thermal range or optimum. The species is distributed from Nova Scotia to Georgia and is strongly northern in abundance. Recommend `provisional` unless additional species-specific thermal data support the numeric band. |
| Tripletail | 20–32 | 24–30 | Florida Museum reports larvae are usually found above 84°F (28.8°C); species accounts describe tropical/subtropical habitat and seasonal movement. | **Insufficient adult evidence.** A larval occurrence temperature cannot validate an adult year-round site-SST range. Recommend `provisional` or `needs_source`; do not infer an adult ideal from larval data. |
| Weakfish | 10–28 | 16–24 | EPA life-history material describes seasonal inshore/offshore movements and juvenile/adult habitat but does not provide a numerical thermal preference in the reviewed table. NOAA field sampling in Newark Bay provides local hydrographic observations, not a species-specific temperature-preference curve. | **Not supported for numeric band.** Seasonal movement alone does not establish the configured interval. Recommend `needs_source` or `provisional` until a species-specific temperature analysis is identified. |
| White grunt | 18–31 | 22–29 | South Atlantic Fishery Management Council and Florida Museum describe tropical/warm-temperate reef habitat, but the reviewed sources do not establish a numeric preferred-temperature band for adults. | **Not supported for numeric band.** Habitat and biogeography do not validate the 22–29°C ideal. Recommend `needs_source` or `provisional`. |
| Winter flounder | 1–20 | 6–15 | NOAA/NEFSC habitat documentation reports adult preferred habitat around 12–15°C and adult occurrence from about 0.6–23°C; NOAA describes the species as cold-water adapted and most common north of Delaware Bay. | **Partly supported, but configured ideal is too broad/cold relative to adult preference.** The current range overlaps adult observations, while 6–15°C extends well below the cited 12–15°C adult preference. The species' range extends to Georgia but abundance is concentrated farther north. Recommend `partly_sourced` with explicit adult/life-stage and regional limitations. |

## Important interpretation issues

### 1. Surface temperature is not interchangeable with bottom temperature

Several supporting references report bottom temperatures, habitat-capture temperatures at depth, spawning temperatures, or laboratory acclimation. The named-site engine's `sst_c` is a buoy measurement or gridded sea-surface temperature. These sources can provide ecological context, but they do not always validate the same physical quantity.

### 2. The ideal interval is a stronger claim than the outer range

A broad observed temperature interval may support an occurrence envelope. It does not automatically support the configured ideal interval. For many profiles, the current reason text says “preferred thermal range” even though the available evidence is only seasonal occurrence or broad tolerance. That language should eventually be made more conservative, but this review does not edit it.

### 3. Life stage and stock matter

Shark nursery studies are juvenile-focused; American shad and striped bass evidence may describe spawning; tripletail temperature observations are larval; bull shark thermal relationships differ between juveniles and adults. A single year-round site SST band collapses these distinctions.

### 4. Geographic relevance matters

Several sources concern northern Gulf Florida, Newark Bay, the Mid-Atlantic, or northern Atlantic waters. They may be useful for species-level context but are not direct South Florida calibration. Spot may be absent from southern Florida according to FishBase. Scup, tautog, winter flounder, and striped bass require particular care when a named site is outside their typical abundance range.

### 5. All 20 are single-factor named-site models

Each profile has only active `sst_c` as its named-site factor, and that factor is both `gate: true` and `required: true`. Temperature therefore determines whether the site can be scored at all. This makes evidence limitations more consequential than an ordinary low-weight optional factor. These models should continue to be described as temperature-only pilots, not complete habitat-suitability models.

## Recommended owner decisions

The conservative status recommendations are:

- **Retain `sourced` with specific references:** Spanish mackerel only.
- **Change to `partly_sourced` after owner approval:** Atlantic croaker, blacktip shark, bluefish, bull shark, ladyfish, lane snapper, scup, spotted seatrout, striped bass, summer flounder, winter flounder.
- **Keep `provisional` or change to `needs_source` after owner approval:** American shad, false albacore, spinner shark, spot, tautog, tripletail, weakfish, white grunt.

These are not automatic edits. The project owner should decide whether `partly_sourced` is appropriate for broad occurrence/migration evidence that does not validate the exact ideal band. For a strict interpretation of `sourced` as support for the actual configured values, only Spanish mackerel currently meets that standard in this review.

## Source register

- American shad: [USFWS species account](https://www.fws.gov/species/american-shad-alosa-sapidissima); [Ontario Fishes life-history record](https://www.ontariofishes.ca/fish_detail.php?FID=15).
- Atlantic croaker: [UF/IFAS Extension FA148](https://ask.ifas.ufl.edu/publication/FA148); [NOAA/NCEI Atlantic Croaker Layer Guidance](https://www.ncei.noaa.gov/waf/data-atlas-waf/products/html/lmrPlates/AtlanticCroakerLayerGuidance.htm).
- Blacktip shark: [NOAA/NMFS Florida shark nursery survey FY22](https://repository.library.noaa.gov/view/noaa/56522/noaa_56522_DS1.pdf); [FWC species profile](https://myfwc.com/research/saltwater/sharks-rays/shark-species/blacktip/).
- Bluefish: [NOAA essential fish habitat source document](https://repository.library.noaa.gov/view/noaa/22659/noaa_22659_DS1.pdf); [NOAA Fisheries species profile](https://www.fisheries.noaa.gov/species/bluefish).
- Bull shark: [Rider et al. (2021), adult/subadult bull shark movements and Biscayne Bay temperature associations](https://sharkresearch.earth.miami.edu/wp-content/uploads/2021/03/Rider-et-al_2021_Bull-Shark-Movements_Aquatic-Ecology.pdf); [juvenile bull shark warming/habitat study](https://pmc.ncbi.nlm.nih.gov/articles/PMC10940676/).
- False albacore: [FishBase species summary, model-derived preferred temperature](https://www.fishbase.org/country/CountrySpeciesSummary.php?c_code=620&id=97).
- Ladyfish: [Florida Museum species profile](https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/ladyfish/).
- Lane snapper: [Gulf of Mexico life-history requirements report](https://www.govinfo.gov/content/pkg/GOVPUB-I-bf4c67cc4207c6e1ea2af8e6166ac54f/pdf/GOVPUB-I-bf4c67cc4207c6e1ea2af8e6166ac54f.pdf); [USACE/FWS EFH assessment](https://www.fws.gov/doiddata/dwh-ar-documents/4103/DWH-ARZ010938.pdf).
- Scup: [NOAA scup life-history source document](https://repository.library.noaa.gov/view/noaa/3154/noaa_3154_DS1.pdf); [ASMFC species profile](https://asmfc.org/species/scup/).
- Spanish mackerel: [NOAA Fisheries species profile](https://www.fisheries.noaa.gov/species/spanish-mackerel); [ASMFC Spanish mackerel habitat factsheet](https://archive.asmfc.org/files/Habitat/SpeciesFactsheets/SpanishMackerel.pdf).
- Spinner shark: [NOAA/NMFS Florida shark nursery survey FY21](https://repository.library.noaa.gov/view/noaa/49034/noaa_49034_DS1.pdf); [juvenile shark habitat preference study](https://onlinelibrary.wiley.com/doi/10.1111/maec.12151).
- Spot: [EPA technical support manual, spot life-history table](https://www.epa.gov/sites/default/files/2020-08/documents/uaa-vol123.pdf); [ASMFC species profile](https://asmfc.org/species/spot/); [FishBase field guide](https://www.fishbase.se/Fieldguide/FieldGuideSummary.php?c_code=840&genusname=Leiostomus&speciesname=xanthurus).
- Spotted seatrout: [SCCF-RECON spotted seatrout profile](https://recon.sccf.org/sport-fishing/spotted-seatrout); [EPA species life-history table](https://www.epa.gov/sites/default/files/2020-08/documents/uaa-vol123.pdf).
- Striped bass: [NOAA/NMFS biological synopsis](https://repository.library.noaa.gov/view/noaa/2955/noaa_2955_DS1.pdf); [USFWS species profile](https://www.fws.gov/species/striped-bass-morone-saxatilis).
- Summer flounder: [NOAA Fisheries science profile](https://www.fisheries.noaa.gov/species/summer-flounder/science); [NOAA essential fish habitat source document](https://repository.library.noaa.gov/view/noaa/3149/noaa_3149_DS1.pdf).
- Tautog: [Massachusetts Division of Marine Fisheries species profile](https://www.mass.gov/info-details/learn-about-tautog).
- Tripletail: [Florida Museum species profile](https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/tripletail/); [Texas Parks and Wildlife profile](https://tpwd.texas.gov/huntwild/wild/species/tripletail/).
- Weakfish: [EPA technical support manual, weakfish life-history table](https://www.epa.gov/sites/default/files/2020-08/documents/uaa-vol123.pdf); [NOAA/NMFS Newark Bay hydrographic and fisheries survey](https://repository.library.noaa.gov/view/noaa/3488/noaa_3488_DS1.pdf).
- White grunt: [South Atlantic Fishery Management Council species profile](https://safmc.net/species/grunt-white/); [Florida Museum species profile](https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/white-grunt/).
- Winter flounder: [NOAA/NEFSC winter flounder habitat source document](https://repository.library.noaa.gov/view/noaa/20209/noaa_20209_DS1.pdf); [NOAA cold-water habitat feature](https://www.fisheries.noaa.gov/feature-story/cold-water-good-sole).

## Final disposition

This review improves traceability but does not justify automatic numerical changes. The next owner-approved action should be to update only the source references and evidence notes/statuses that the owner accepts. Numeric ranges, ideal bands, gates, and weights should be reviewed separately with stronger life-stage and geographic alignment.


## Owner approval and profile metadata implementation | 2026-11-16

The project owner approved applying the conservative source-by-source recommendations. The 20 named-site SST profiles were updated on `main` with species-specific source references, evidence statuses, and explanatory `value_notes`:

- **Retained `sourced`:** Spanish mackerel.
- **Set to `partly_sourced`:** Atlantic croaker, blacktip shark, bluefish, bull shark, ladyfish, lane snapper, scup, spotted seatrout, striped bass, summer flounder, and winter flounder.
- **Set to `provisional`:** American shad, false albacore, spinner shark, tautog, and tripletail.
- **Set to `needs_source`:** spot, weakfish, and white grunt.

Both the profile-level biological `sources` list and active `sst_c` factor `sources` list now contain the reviewed species-specific references. Explanatory notes distinguish occurrence from preference and record depth, life-stage, region, or model-derived limitations. The original source-review findings above remain the evidence basis for these decisions.

**Scope boundary:** no temperature range or ideal interval, factor weight, active flag, gate, required flag, reason template, timing model, scoring behavior, confidence policy, ingestion, or published data was changed. `needs_source` and `provisional` remain explicitly uncertain; adding a URL does not promote a factor to scientifically validated.
