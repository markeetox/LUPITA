# Biscayne Bay & Adjacent Waters: Habitat Prediction Audit & Expansion Guide

## Executive Summary

This document provides a comprehensive technical audit of the Lupita fish habitat modeling platform, focusing on **Biscayne Bay** and its adjacent bodies of water (Biscayne National Park, Card Sound, Barnes Sound, and nearshore Atlantic barrier reef tracts).

It details:
1. The **current architecture** and its limitations when scoring inshore and estuarine bay habitats.
2. An actionable **technical roadmap** for adding predictions inside the bay (site-based & grid-based adaptations).
3. Recommended **new fish species** that naturally inhabit Biscayne Bay and adjacent waters but are currently missing from the catalog, including their ecological profiles, factors, and FWC regulatory limits.

---

## 1. System & Architecture Audit: Current Status in Biscayne Bay

### 1.1 Oceanographic & Meteorological Infrastructure
The platform ingests live ocean and weather data from several sources:
- **NDBC Inshore & Coastal Buoys**:
  - `VAKF1` (Virginia Key, FL - lat 25.73, lon -80.16, coastal): Measures water temperature, wind, and atmospheric pressure. Located right at the northern entrance to Biscayne Bay (Bear Cut/Norris Cut vicinity).
  - `THRF1` (Thursday Point, FL - lat 25.20, lon -80.37, inshore): Located in southern Biscayne Bay / Card Sound.
  - `MNBF1` (Manatee Bay, FL - lat 25.24, lon -80.42, inshore): Located in Barnes Sound / Manatee Bay.
  - `41122` (Hollywood Beach, FL - lat 26.00, lon -80.10, ocean): Open ocean wave height and period reference.
- **NOAA CO-OPS Tide Prediction Stations**:
  - `8723214` (Virginia Key, FL - lat 25.731, lon -80.162): Critical harmonic tide predictions for Central and North Biscayne Bay.
  - `8722956` (Port Everglades, FL - lat 26.092, lon -80.117): Secondary tide station north of the bay.
- **Satellite & Geophysical Grids (`config/sources.json`)**:
  - JPL MUR SST (Sea Surface Temperature): ~1 km native resolution, strided on the pipeline grid.
  - NOAA-20 VIIRS Chlorophyll-a: 4 km resolution.
  - NOAA ETOPO 2022 Bathymetry: 15 arc-second (~450 m).
  - NOAA CoastWatch Geostrophic Currents: 25 km grid (only effective offshore in the Florida Current / Gulf Stream).
  - ArcGIS Unified Florida Reef Tract Benthic Habitat (FWC): Hard bottom and coral reef shapefiles.
  - NOAA MPA Inventory (2023 edition): Protected areas and marine sanctuaries (Biscayne National Park, Legare Anchorage, Bill Baggs State Park, etc.).

### 1.2 Identified Limitations for In-Bay Predictions
1. **Grid Resolution vs. Bay Scale**:
   - The primary prediction grid is configured for broad coastal and offshore waters (2-km cells). Biscayne Bay is a shallow, narrow lagoon-type estuary (length ~56 km, width 5-16 km, average depth 2-3 m). Coarse satellite cells frequently overlap land and mangroves, resulting in missing or contaminated satellite SST/chlorophyll pixels near the shore.
2. **Offshore-Biased Depth Filters & Gates**:
   - In `pipeline/scoring.py`, `OFFSHORE_MIN_DEPTH_M` is set to 50.0 m. Temperature breaks (`sst_gradient`) use this floor, meaning surface thermal breaks inside shallow bay waters are disregarded.
   - Multiple species profiles (e.g. `mutton-snapper`, `red-drum`, `jack-crevalle`) have rigid depth gates (`gate: true`) or depth ranges that heavily discount or disqualify waters shallower than 5–15 meters.
3. **Restricted Site Kinds in `pipeline/sites.py`**:
   - Site-based species (such as `snook`, `tarpon`, `bonefish`, `permit`, and `spotted-seatrout`) currently query `config/places.json` filtered to `site_kinds: ["inlet"]`.
   - In `config/places.json`, the only Biscayne Bay locations defined are:
     - `Government Cut` (lat 25.767, lon -80.135)
     - `Haulover Inlet` (lat 25.903, lon -80.123)
     - `Bear Cut` (lat 25.738, lon -80.156)
   - Iconic inshore fishing grounds inside the bay—such as **Stiltsville / Biscayne Channel**, **Safety Valve**, **Soldier Key flats**, **Featherbed Bank**, **Black Point**, **Matheson Hammock**, and **Convoy Point**—are completely absent.
4. **Missing Estuarine Habitat Parameters**:
   - Bay gamefish and predators concentrate based on benthic vegetation (seagrass meadows like *Thalassia testudinum*), tidal current flow through cuts, and salinity gradients (freshwater canal discharges from the SFWMD canals vs. oceanic tidal flushing). The existing pipeline lacks a seagrass/flat layer.

---

## 2. Technical Roadmap: Adding In-Bay Fish Species & Predictions

To generate accurate predictions inside Biscayne Bay, two complementary approaches should be implemented:

### 2.1 Approach A: Expanding the Site-Based Modeling Engine (Fastest & Most Accurate for Estuaries)
The site model in `pipeline/sites.py` calculates bite conditions and habitat matches using real-time local buoy water temperature (`VAKF1`, `THRF1`), tide predictions (`8723214 Virginia Key`), sun phase, and seasonal spawning.

1. **Expand `config/places.json` with In-Bay Hotspots**:
   Add named places with appropriate `kind` tags:
   - `"kind": "inlet"` or `"cut"`:
     - `Norris Cut` (lat 25.753, lon -80.146, radius 1.2 km)
     - `Biscayne Channel / Stiltsville` (lat 25.688, lon -80.170, radius 2.0 km)
     - `Caesar Creek` (lat 25.390, lon -80.240, radius 1.5 km)
     - `Broad Creek` (lat 25.324, lon -80.288, radius 1.5 km)
     - `Angelfish Creek` (lat 25.328, lon -80.330, radius 1.5 km)
   - `"kind": "flat"`:
     - `Safety Valve Flats` (lat 25.670, lon -80.165, radius 2.5 km)
     - `Soldier Key & Ragged Keys Flats` (lat 25.590, lon -80.175, radius 2.0 km)
     - `Sands Cut & Flats` (lat 25.512, lon -80.185, radius 1.8 km)
     - `Elliott Key East Flats` (lat 25.450, lon -80.200, radius 2.5 km)
     - `Featherbed Bank` (lat 25.515, lon -80.250, radius 2.0 km)
   - `"kind": "channel_bridge"`:
     - `Rickenbacker Causeway Bridge & Reliefs` (lat 25.747, lon -80.190, radius 1.5 km)
     - `Julia Tuttle & Venetian Causeways` (lat 25.805, lon -80.175, radius 1.8 km)
     - `Black Point Channel` (lat 25.534, lon -80.320, radius 1.5 km)

2. **Update Species Profiles to Target In-Bay Habitats**:
   - In `data/species/bonefish.json` and `data/species/permit.json`:
     Change `"site_kinds": ["inlet"]` to `"site_kinds": ["inlet", "flat", "cut"]`.
   - In `data/species/snook.json` and `data/species/tarpon.json`:
     Change `"site_kinds": ["inlet"]` to `"site_kinds": ["inlet", "cut", "channel_bridge", "flat"]`.
   - In `data/species/spotted-seatrout.json` and `data/species/great-barracuda.json`:
     Change `"site_kinds": ["inlet"]` to `"site_kinds": ["inlet", "flat", "bay"]`.

3. **Enhance `pipeline/sites.py` with Bay Structure Scoring**:
   Allow `structure_value(site, ctx)` to reward flats for flats species (bonefish, permit) and structure/bridges for snook and tarpon.

### 2.2 Approach B: Adapting the Grid Scorer for Shallow Inshore Waters
For grid-scored species (`mangrove-snapper`, `red-drum`, `sheepshead`, `florida-pompano`, `jack-crevalle`):
1. **Marine Mask & Land Proximity**:
   - Ensure `build_marine_mask` in `pipeline/grid.py` does not disconnect the bay through shallow bank thresholds.
2. **Sub-Grid Bathymetric Allowance**:
   - Set `min_cells: 3` and relax depth gates for inshore species:
     - `mangrove-snapper`: ideal `[1, 15]` m, range `[0.3, 40]` m.
     - `red-drum`: ideal `[0.5, 4]` m, range `[0.2, 12]` m.
3. **FWC Benthic Habitat (Seagrass) Layer Integration**:
   - Ingest FWC Unified Reef Map or Benthic Seagrass layer (`Continuous Seagrass`, `Discontinuous Seagrass`) into `pipeline/layers.py` to assign positive structure scores for grassbed flats.

---

## 3. High-Priority Fish Species to Add for Biscayne Bay

The following prominent sport and food fish thrive in Biscayne Bay and adjacent waters but are currently missing from `data/species/*.json`:

### 3.1 Cero Mackerel (*Scomberomorus regalis*)
- **Habitat**: Coral reefs, sandy bottom channels, patch reefs, and grass flats throughout South Biscayne Bay and Key Largo border.
- **Model**: `grid` or `sites` (reef patches, cuts).
- **Ideal Temperature**: 24.0°C – 28.5°C (range 20.0°C – 31.0°C).
- **Depth**: 1 to 20 m (ideal 2 to 10 m).
- **FWC Regulations**: No minimum size limit; included in the 20-fish aggregate bag limit for reef and nearshore fish.

### 3.2 Schoolmaster Snapper (*Lutjanus apodus*)
- **Habitat**: Mangrove roots, bridge pilings, patch reefs, and rock ledges in central/southern bay and Biscayne National Park.
- **Model**: `sites` (`["inlet", "cut", "channel_bridge", "flat"]`) or `grid`.
- **Ideal Temperature**: 23.0°C – 29.0°C (range 18.0°C – 32.0°C).
- **Depth**: 1 to 15 m (ideal 1 to 6 m).
- **FWC Regulations**: 10" minimum total length; 10 per harvester within the 10-snapper aggregate.

### 3.3 Bluestriped Grunt (*Haemulon sciurus*) & French Grunt (*Haemulon flavolineatum*)
- **Habitat**: High abundance over seagrass beds, patch reefs, and channel cuts across Biscayne Bay. Crucial recreational light-tackle species.
- **Model**: `grid` or `sites`.
- **Ideal Temperature**: 22.0°C – 29.5°C.
- **Depth**: 1 to 12 m.
- **FWC Regulations**: No size limit; 100 lb or 2 fish bag limit (aggregate food fish).

### 3.4 Inshore Sharks: Bonnethead Shark (*Sphyrna tiburo*), Nurse Shark (*Ginglymostoma cirratum*), Lemon Shark (*Negaprion brevirostris*)
- **Habitat**: Shallow grass flats (Bonnethead feeding on blue crabs/shrimp), channel edges, mangrove creeks (juvenile Lemon & Nurse sharks).
- **Model**: `sites` (`["flat", "cut", "inlet"]`).
- **Ideal Temperature**: 22.0°C – 30.5°C.
- **FWC Regulations**: Bonnethead: 1 per harvester / 2 per vessel, no minimum size. Nurse & Lemon: Prohibited from harvest in Florida state waters (catch-and-release only).

### 3.5 Pinfish (*Lagodon rhomboides*)
- **Habitat**: Vast seagrass meadows (*Thalassia* / *Halodule*) throughout the entire expanse of Biscayne Bay. Primary forage species and popular family target.
- **Model**: `sites` (`["flat", "bay"]`) or `grid`.
- **Ideal Temperature**: 18.0°C – 30.0°C.
- **Depth**: 0.5 to 5 m.
- **FWC Regulations**: Unregulated for recreational hook-and-line.

### 3.6 Spotted Eagle Ray (*Aetobatus narinari*) & Southern Stingray (*Hypanus americanus*)
- **Habitat**: Cruising shallow sandbars, oyster bars, and grass flats in Biscayne National Park.
- **Model**: `sites` (`["flat", "cut"]`).
- **Ideal Temperature**: 22.0°C – 30.0°C.
- **FWC Regulations**: Spotted Eagle Ray is a protected species in Florida state waters (prohibited harvest).

### 3.7 Lookdown (*Selene vomer*) & Atlantic Spadefish (*Chaetodipterus faber*)
- **Habitat**: Sandy cuts, bridge pilings, navigation channels (Biscayne Channel, Port of Miami / Government Cut).
- **Model**: `sites` (`["channel_bridge", "inlet", "cut"]`).
- **Ideal Temperature**: 21.0°C – 29.0°C.
- **Depth**: 2 to 15 m.
- **FWC Regulations**: Included in general aggregate limits.

---

## 4. Example Species Profile Implementation: Cero Mackerel

Below is the verified JSON schema to create `data/species/cero-mackerel.json`:

```json
{
  "id": "cero-mackerel",
  "common_name": "Cero mackerel",
  "scientific_name": "Scomberomorus regalis",
  "description": "A fast, streamlined predator common over the coral reefs and clear shallow waters of Biscayne Bay and the Florida Keys.",
  "model": "grid",
  "environment": "saltwater",
  "lat_range": [18.0, 27.5],
  "lon_range": [-100.0, -50.0],
  "min_cells": 4,
  "confidence_cap": "Medium",
  "display": {
    "color": "#38bdf8"
  },
  "profile": {
    "size": "Common 18 to 24 in (2 to 5 lb), can reach over 10 lb",
    "diet": "Silversides, pilchards, anchovies, ballyhoo, and squid",
    "swimming_depth": "Surface to midwater over patch reefs and hard bottom",
    "behavior": "Fast-moving hunter solitary or in small schools over clear reef flats and channels",
    "spawning": "Spring through summer in offshore reef waters",
    "lifespan": "Up to 8 years"
  },
  "regulations": {
    "summary": "No size limit; part of 20-fish aggregate bag limit",
    "min_size": "None",
    "max_size": "None",
    "bag_limit": "20 fish aggregate per harvester / day",
    "season": "Open year-round",
    "jurisdiction": "Florida State Waters (FWC)",
    "source_name": "MyFWC Saltwater Regulations",
    "source_url": "https://myfwc.com/fishing/saltwater/recreational/"
  },
  "factors": [
    {
      "param": "sst_c",
      "kind": "range",
      "range": [20.0, 31.0],
      "ideal": [24.0, 28.5],
      "weight": 0.40,
      "gate": true,
      "active": true,
      "value_status": "sourced",
      "reason_template": "Water temperature is {value} C, within the preferred {ideal_min}-{ideal_max} C range."
    },
    {
      "param": "depth_m",
      "kind": "range",
      "range": [1.0, 35.0],
      "ideal": [2.0, 15.0],
      "weight": 0.35,
      "gate": false,
      "active": true,
      "value_status": "sourced",
      "reason_template": "Depth of {value} m matches the shallow reef and channel flats where cero hunt."
    },
    {
      "param": "structure_type",
      "kind": "category",
      "preferred": ["natural_reef", "artificial_reef"],
      "weight": 0.25,
      "active": true,
      "value_status": "sourced"
    }
  ],
  "timing": {
    "light": {
      "dawn": 0.95,
      "day": 0.85,
      "dusk": 0.95,
      "night": 0.20
    },
    "why": [
      "Cero mackerel are visual sight feeders that feed aggressively in bright daylight, especially during morning and evening tide movement."
    ],
    "evidence": "angler_lore"
  }
}
```

---

## 5. Verification Checklist & Action Items

To activate in-bay predictions in production:
1. **Places Configuration**:
   - Add the Biscayne Bay cuts and flats into `config/places.json`.
2. **Species Profile Alignment**:
   - Update `data/species/bonefish.json`, `permit.json`, `snook.json`, and `tarpon.json` with `"site_kinds": ["inlet", "flat", "cut", "channel_bridge"]`.
3. **Add Candidate Species**:
   - Add `cero-mackerel.json`, `schoolmaster-snapper.json`, and `bonnethead-shark.json`.
   - Provide artwork SVGs in `tools/fish-svg/` and PNGs in `web/fish/`.
4. **Automated Verification**:
   - Run `python3 -m pytest -q` to guarantee all schema validations, scoring routines, and API builders pass cleanly.
