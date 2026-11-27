# NOAA / SEAMAP haul-metadata review for Southern flounder | 2026-11-27

**Status:** source and access-path review complete; original haul-level data not yet acquired  
**Scope:** interpret the zero-WTCPUE Southern flounder records from DisMAP's Gulf and Southeast seasonal products  
**Target:** *Paralichthys lethostigma*  
**Control:** research only. No raw records, species profiles, masks, scoring, confidence, ingestion, production sources, or publishing behavior changed.

## Executive finding

The four DisMAP point products do not contain the original tow-level effort and quality-control fields needed to independently audit every zero-catch observation. However, the source survey methods are now identifiable:

- **Gulf of Mexico:** SEAMAP Gulf Summer Shrimp/Groundfish bottom-trawl survey. The documented protocol uses a 30-minute bottom-time tow, a 42-foot SEAMAP trawl, and a target vessel speed of 2.5–3 knots. Stations are selected with a random design and proportional allocation by bottom area within shrimp statistical zones.
- **Southeast US Fall/Spring/Summer:** SEAMAP South Atlantic Coastal Trawl Survey (CTS), administered by SCDNR. Standardized sampling since 1989 has used daytime 20-minute tows, target speed 2.5 knots, and paired 75-foot mongoose-type Falcon trawls. Its official methods describe how swept area is calculated and explicitly say to omit a tow from analyses if swept area cannot be estimated accurately.

This is a substantial improvement over treating the DisMAP points as an opaque survey product. It is **not yet a validation of each of the 13,703 extracted sample records**. We still need the original haul/station records and their quality-control fields, plus an explicit mapping from DisMAP `SampleID` to source survey identifiers.

## 1. Gulf of Mexico: SEAMAP Gulf Summer Shrimp/Groundfish

### Published protocol evidence

The SEAMAP trawl protocol documents the following design:

- Since the 2010 protocol change, Summer and Fall Shrimp/Groundfish surveys use a fixed 30-minute bottom-time tow rather than the older tow design across a fathom stratum.
- Stations use a random design with proportional allocation by bottom area within shrimp statistical zones.
- Standard gear is a 42-foot semi-balloon trawl with 8-foot by 40-inch chain doors.
- Target towing speed is 2.5–3 knots.
- The protocol's station data requirements include vessel and station identifiers, cruise, date, gear type, surface/bottom temperature where collected, vessel speed, station start/end time, position and depth. Trawl processing records total live catch and catch weights by finfish/crustacean/other groups and taxon-level sample/select weights.

Source: [SEAMAP Trawl Protocol, SEDAR27-RD-05](https://sedarweb.org/docs/wsupp/S27_RD_05_SEAMAP%20TRAWL%20PROTOCOL.pdf), especially the design/methods and data-requirements sections.

### Data access and limitations

The Gulf SEAMAP Information System is managed by the Gulf States Marine Fisheries Commission (GSMFC) with NOAA Fisheries-SEFSC. GSMFC annual-report material says raw data are edited by the collecting agency and verified by the SEAMAP Data Manager before entry; verified, non-confidential data are conditionally available to requesters, with priority assigned to SEAMAP participants. The current NOAA InPort source record links the Gulf DisMAP product to the SEAMAP Gulf system: [SEAMAP Gulf](https://seamap.gsmfc.org/).

Sources:
- [GSMFC Annual Report No. 321](https://www.gsmfc.org/publications/GSMFC%20Number%20321.pdf), Information Services / SEAMAP Information System.
- [NOAA InPort, Survey Catch-per-unit-effort 20260201](https://www.fisheries.noaa.gov/inport/item/79360/full-list), Gulf source citation and lineage.

The public protocol establishes standardized effort, but it does not provide the actual tow-specific validity flag, tow distance, measured net spread, swept-area value, or operation/comment codes for each extracted DisMAP sample. The protocol document is a published reference, not proof that every protocol detail remained unchanged for every vessel/year in the 2010–2025 extracted records. The current operations manual and original haul records are still needed.

### Required Gulf request

Request original station/haul and species-catch records for the DisMAP Gulf survey years represented in the extraction (2010–2025), including:

1. Source station/haul/cruise identifiers and the crosswalk to DisMAP `SampleID`.
2. Tow start/end date-time and start/end coordinates.
3. Actual bottom time, vessel speed, distance towed, and any tow interruption or deviation.
4. Gear code and configuration, net/door mensuration where available, and swept-area value or calculation inputs.
5. Tow validity, accepted/rejected status, quality flags, operation codes, comments, and reasons for excluded or compromised tows.
6. Full species catch table with Southern flounder weight/count and explicit zero-catch representation.
7. Survey year, cruise, statistical zone, stratum, depth, and any changes in sampling protocol or vessel/gear.

Ask GSMFC/SEAMAP whether the zero rows used by DisMAP represent only accepted valid fishing tows, and whether zero catch can be distinguished from a missing, invalid, or non-fishing station in the source data.

## 2. Southeast US: SEAMAP South Atlantic Coastal Trawl Survey

### Published survey design

SEAMAP-SA identifies the Southeast seasonal point layers with the SCDNR Coastal Trawl Survey. The survey covers the Atlantic coastal zone between Cape Hatteras, North Carolina, and Cape Canaveral, Florida. Its inner shallow strata have been sampled since 1989 and are bounded by the 4.6 m and 9.1 m depth contours. Outer strata were discontinued in 2001.

The published standardized method states:

- Daylight sampling, from one hour after sunrise to one hour before sunset.
- Twenty-minute tow time, excluding wire-out and haul-back.
- Target towing speed of 2.5 knots relative to ground.
- A pair of 75-foot mongoose-type Falcon trawl nets; catches were historically processed separately and pooled at the station/tow level.
- Beginning in 2021, only one net's catch was processed while the other net's tail bag was fished untied.
- Since 2001, stations have been selected randomly from the trawlable station pool within 24 inner strata, with optimal allocation; annual station allocations vary with funding and survey priorities.
- Beginning in 2023, cruises changed from three seasonal windows (spring, summer, fall) to two combined windows (spring/summer and summer/fall).

The official survey page says swept area is estimated as average net-opening width (13.5 m) multiplied by distance trawled, divided by 10,000 m²/ha. It explicitly says a tow should be omitted from analyses when swept area cannot be accurately estimated (for example, a U-turn to avoid a gill net).

Sources:
- [SEAMAP-SA Coastal Trawl Survey methods](https://seamap.org/seamap-sa-coastal-trawl/), especially survey design, data collection, data analysis, and data availability.
- [SEAMAP-SA Data Portal](https://seamap.org/data-portal/).

### Data access and limits

The SEAMAP-SA portal requires users to read the survey design/caveats and Intellectual Property Protocol, then create an account to query the database. The official survey page says field data are made available within one year of collection and that station location, depth, date, and time are recorded. The public methods page does not expose the full record-level quality-control fields or the actual source-to-DisMAP identifier crosswalk.

The 2021 one-net processing change and 2023 seasonal-window change are material time-series breaks to preserve in any year/season analysis. They do not invalidate the data, but they mean the source methods and processing version must accompany any comparison across those periods.

### Required Southeast request

Through the [SEAMAP-SA Data Portal](https://seamap.org/data-portal/), request the original Coastal Trawl Survey station/tow and species-catch data for the sample years represented in the DisMAP extraction, including:

1. Source station, cruise, collection, and tow identifiers, plus a crosswalk to DisMAP `SampleID`.
2. Tow start/end time and position, tow duration, speed, distance, and start/end depth.
3. Net mensuration, net-opening width, swept-area calculation inputs/value, and whether the tow passed the survey's swept-area validity rule.
4. Tow acceptance/exclusion flags, operation codes, comments, and any reason for an invalid or compromised tow.
5. Full species catch/biomass records with Southern flounder explicit zero values.
6. Net-level versus pooled station-level catch fields, especially around the 2021 one-net processing change.
7. Stratum, region, season, sampling design version, vessel, gear configuration, and any vessel/gear changes.

Ask the data steward to confirm whether the DisMAP zero WTCPUE records correspond only to accepted CTS tows and how the source's two-net/one-net handling is represented in the DisMAP biomass and swept-area calculation.

## 3. Implications for the extracted zero records

The NOAA DisMAP technical report explains that the regional data are expanded with zeros for trawls where a species known from the region was not caught. Thus, a zero WTCPUE row is a meaningful no-catch result in the compiled survey data, rather than merely a missing species row.

The newly identified survey protocols add important context:

- A valid accepted tow has a standardized target duration and gear design, making the zero meaningful as a survey-specific non-detection.
- For SEAMAP-SA, the official analysis protocol explicitly excludes tows whose swept area cannot be estimated accurately. We must still verify that this exclusion was applied to the particular records in the DisMAP extraction.
- For Gulf SEAMAP, the published protocol establishes fixed tow time and standardized gear, but the actual per-haul validity and effort fields still need to be obtained.
- Neither survey samples all habitat types. The South Atlantic CTS is a coastal trawl survey within a defined trawlable depth/stratum design; it is not a survey of Florida Bay, tidal creeks, or the Caloosahatchee estuary.
- A zero at a valid trawl station is not evidence of absence at unsampled places, in non-trawlable habitat, or outside the survey season.

Therefore, retain the existing interpretation: **sample-level no-catch evidence only**. Do not create an absence polygon, latitude cutoff, or species-profile change from these data.

## 4. Metadata and identifier reconciliation

The NOAA InPort 20260201 metadata lists Gulf sample locations through 2024, Southeast Fall and Spring through 2024, and Southeast Summer through 2022. The current extracted point layers contain Gulf/Fall/Spring records dated 2025, while Summer ends in 2022. This remains an unresolved metadata-versus-current-layer extent discrepancy.

Before longitudinal analysis, request the DisMAP release build date, source extract date, and exact source survey record versions used for each layer. The source identifier crosswalk is especially important: matching a DisMAP `SampleID` to the original source haul is a prerequisite for attaching tow validity, distance, swept area, and operation codes without accidentally joining to the wrong net-level or collection-level record.

## 5. Recommended acquisition sequence

1. **Southeast first:** create a SEAMAP-SA portal account after reading its Intellectual Property Protocol, then request CTS station/tow, effort, validity, and catch exports with the DisMAP SampleID crosswalk. Its published methods already expose the swept-area rule and the 2021 gear-processing change.
2. **Gulf second:** submit a targeted data request through GSMFC/SEAMAP for Gulf Summer Shrimp/Groundfish haul-level effort, quality-control, and catch data for 2010–2025. Include the DisMAP Gulf SampleID list/crosswalk request.
3. Preserve source files outside the repository until license/access terms and data stewardship are confirmed. Record data release, retrieval date, and checksums.
4. Join only through verified source identifiers. Audit valid/invalid tow counts, missing effort, zero-catch rows, and any changes by year, stratum, gear, and survey.
5. Reassess the southern Gulf zero pattern only after the valid-tow denominator and habitat/survey footprint are understood.

## Sources

- NOAA Fisheries, [DisMAP Technical Report, June 2026](https://apps-st.fisheries.noaa.gov/dismap/docs/DisMAP_Tech_Report_06_2026.pdf).
- NOAA Fisheries, [Survey Catch-per-unit-effort 20260201, InPort 79360](https://www.fisheries.noaa.gov/inport/item/79360/full-list).
- SEAMAP South Atlantic, [Coastal Trawl Survey](https://seamap.org/seamap-sa-coastal-trawl/).
- SEAMAP South Atlantic, [Data Portal](https://seamap.org/data-portal/).
- SEAMAP Gulf, [SEAMAP Information System](https://seamap.gsmfc.org/).
- Gulf States Marine Fisheries Commission, [Annual Report No. 321](https://www.gsmfc.org/publications/GSMFC%20Number%20321.pdf).
- SEAMAP, [Trawl Protocol, SEDAR27-RD-05](https://sedarweb.org/docs/wsupp/S27_RD_05_SEAMAP%20TRAWL%20PROTOCOL.pdf).

No raw survey haul data were acquired in this review. No species profile, geographic mask, scoring factor, weight, gate, confidence logic, ingestion, production source, or publishing behavior changed.
