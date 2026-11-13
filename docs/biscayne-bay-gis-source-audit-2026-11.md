# Biscayne Bay GIS source and boundary audit

**Status:** Initial source audit and extraction tooling. Geometry review is pending the first successful GitHub Actions artifact.  
**Scope:** Research-only. No production pipeline, species scoring, thresholds, or API v1 behavior changes.

## 1. Boundary decisions

LUPITA must not use one polygon as though it simultaneously represented the ecological bay, the aquatic preserve, the national park, and benthic-map coverage.

The first catalog therefore distinguishes:

1. **Biscayne Bay Aquatic Preserve:** a statutory management boundary described by Florida Statute 258.397. The statute says the preserve includes Card Sound, includes natural waterways tidally connected to Biscayne Bay, extends across mouths of artificial waterways, and excludes submerged lands conveyed for Biscayne National Monument. This is the strongest legal boundary definition found in the initial review. The statute is a boundary description, not a ready-made GIS polygon.
2. **Biscayne Bay ecological context:** a broader ecological waterbody concept. It must be reconciled against shoreline, islands, Card Sound, Biscayne National Park, and tidal connections rather than assumed identical to the preserve.
3. **Biscayne National Park boundary:** a federal management boundary. FWC's detailed BNP benthic mapping layer is clipped to this boundary and does not cover the entire bay.
4. **Benthic mapping footprints:** source-map coverage and habitat polygons. These describe where habitat was mapped, not the legal or ecological edge of the bay.

## 2. Verified GIS source inventory

### FWC Unified Reef Map v2.2

- Landing page: https://myfwc.com/research/gis/fisheries/unified-reef-map/
- ArcGIS REST service: https://gis.myfwc.com/hosting/rest/services/Projects_FWC/UnifiedReefMapProject_v2_2/MapServer
- Source footprint layer: layer 0, polygon geometry, source attribute Source. It identifies individual source-map footprints, including Biscayne Bay NPS and Biscayne Bay FWC.
- BNP detailed habitat layers: layers 3 and 4, polygon geometry. Metadata says the inshore map represents benthic habitats in Biscayne Bay, produced from 2005–2008 imagery, and the NPS-clipped source data were produced in 2009. This is not bay-wide coverage.
- Unified Reef Map Level 1: layers 6 and 7, polygon geometry, with FIRST_Source and FIRST_ClassLv0 through FIRST_ClassLv4. Metadata reports the integrated map was simplified with a 10 m Douglas-Peucker tolerance. Level 1 preserves more habitat detail than Level 0, but class semantics vary by source map.
- Output geometry is requested in EPSG:4326. Source service metadata reports NAD 1983 (2011) Florida GDL Albers, WKID 6439.
- The extraction workflow queries Biscayne-related source records, preserves attributes and geometry, paginates, and validates polygon coordinate bounds. It uploads review artifacts and does not publish production data.

Important caution: FWC's map is a regional reef-tract benthic map. Its source footprints and benthic polygons must not be re-labelled as bay boundaries, flats, channels, or species habitat suitability without further evidence.

### Florida statutory boundary

- Florida Statute 258.397: https://www.flsenate.gov/Laws/Statutes/2026/258.397
- The legal description is authoritative for the Aquatic Preserve's statutory scope.
- The GIS polygon still needs to be obtained from an authoritative FDEP/FWC preserve boundary layer or independently digitized from the legal description and reviewed. Do not hand-draw an approximate polygon for production.

### NOAA hydrographic geometry

- NOAA Office of Coast Survey GIS data and services: https://www.nauticalcharts.noaa.gov/data/gis-data-and-services.html
- NOAA ENC Direct to GIS: https://www.nauticalcharts.noaa.gov/learn/encdirect/
- NOAA ENC features are derived from S-57 chart data and can provide channel, shoreline, depth, and marine feature geometry. NOAA notes that coverage is organized by ENC cell and updated regularly.
- Use chart features as hydrographic/navigation evidence, not as a complete ecological channel or fish habitat map. Validate chart edition/update dates and feature object classes before import.

### Ecological subregions and named features

- NOAA Biscayne Bay Stock assessment: https://www.fisheries.noaa.gov/s3/2026-04/biscayne-bay-stock-508gw.pdf
- The assessment describes the northern bay as more developed and less well flushed, and central/southern portions as less influenced by development and better flushed.
- It describes the Safety Valve as a broad area of grass flats and tidal channels near the center of the bay that exchanges water with the Atlantic.
- These descriptions support provisional named contexts, not exact polygon boundaries. The first catalog records Northern Biscayne Bay, Central and Southern Biscayne Bay, and Safety Valve with geometry explicitly pending.

## 3. Initial feature catalog

The file data/spatial/feature-catalog.json is intentionally conservative:

| Feature | Initial status | What is actually supported |
|---|---|---|
| Biscayne Bay Aquatic Preserve | Legal boundary definition verified; GIS geometry pending | Florida Statute 258.397 |
| Northern Biscayne Bay | Named ecological context supported; boundary pending | NOAA stock assessment regional description |
| Central and Southern Biscayne Bay | Combined named ecological context supported; boundary pending | NOAA stock assessment regional description |
| Safety Valve | Named flat/channel complex supported; geometry pending | NOAA description of grass flats and tidal channels |
| Government Cut | Named navigation feature; geometry pending | NOAA ENC is the planned geometry source |
| Bear Cut | Named navigation feature; geometry pending | NOAA ENC is the planned geometry source |

Government Cut and Bear Cut currently exist in config/places.json as approximate point locations with display radii. Those are not authoritative channel or inlet geometries and are not copied into the spatial catalog as polygons or lines. Connectivity links remain hypotheses until verified against hydrographic geometry and shoreline/waterbody topology.

## 4. Extraction and review procedure

Run the **Biscayne Bay GIS geometry audit** workflow manually or through a pull request. The artifact contains:

- source_footprints.geojson
- unified_benthic_polygons.geojson
- summary.json

Review must record:
- actual feature count and source attribution;
- class distribution and map source;
- geometry types, CRS, bounds, and coordinate validity;
- spatial extent relative to the statutory preserve, BNP boundary, and bay shoreline;
- gaps, overlap, source vintage, and mapping scale;
- whether a feature is suitable to become a named subregion, flat, channel, or inlet.

Do not promote candidate features to verified boundaries just because their names appear in a source or map.

## 5. Next GIS tasks

1. Run and inspect the first FWC geometry extraction artifact.
2. Obtain the statutory aquatic-preserve polygon from an authoritative FDEP/FWC GIS service and compare it with the legal description.
3. Obtain NOAA ENC Direct to GIS features for the Miami/Biscayne Bay harbor cells. Identify channel and inlet object classes and inspect chart update metadata.
4. Use benthic habitat polygons, bathymetry, and shoreline geometry together to delineate candidate flat complexes. A seagrass polygon is evidence of mapped seagrass, not automatically a named fishing flat.
5. Define north/central/south subregion polygons only after a reproducible boundary rule is documented. Preserve the source and method for every boundary.
6. Add inlet connectivity only after the waterbody polygons, channel centerlines/polygons, and endpoints have been topologically checked.
7. Extend species files later through habitat_contexts references to stable feature IDs. This GIS milestone does not alter species files or scoring.

## 6. Non-goals

- No production scoring changes.
- No automatic fish-presence or catch-probability claims.
- No nationwide GIS ingestion.
- No use of approximate place-radius circles as real inlet, flat, or channel geometry.
- No treating missing mapped coverage as absence.


## 7. First geometry extraction results

**GitHub Actions run:** https://github.com/markeetox/LUPITA/actions/runs/43347704537  
**Artifact:** biscayne-bay-gis-review  
**Extraction timestamp:** 2026-11-13 01:49:40 UTC  
**Result:** extraction and polygon-coordinate validation succeeded.

### Source-map footprints (layer 0)

Two actual source-footprint geometries were returned:

| Source | Date range | Geometry | WGS84 bounds |
|---|---|---|---|
| Biscayne Bay NPS | 2005–2013 | Polygon | -80.35156 to -80.09104 longitude; 25.29254 to 25.66869 latitude |
| Biscayne Bay FWC | 2005–2008 | MultiPolygon | -80.31724 to -80.12051 longitude; 25.38613 to 25.94960 latitude |

Combined footprint bounds: **-80.35156, 25.29254 to -80.09104, 25.94960**.

These are verified source-map coverage geometries, not the bay boundary. They are useful for understanding where mapped benthic evidence came from and where source coverage changes.

### Integrated benthic polygons (layer 7)

The query returned **7,222 polygon features** across 15 pages:

- Biscayne Bay FWC source: 1,336 polygons.
- Biscayne Bay NPS source: 5,886 polygons.

Class counts:

| Unified Level 1 class | Feature count |
|---|---:|
| Individual or Aggregated Patch Reef | 5,122 |
| Seagrass (Discontinuous) | 828 |
| Seagrass (Continuous) | 602 |
| Unconsolidated Sediment | 500 |
| Not Classified | 162 |
| Scattered Coral/Rock in Unconsolidated Sediment | 6 |
| Artificial | 1 |
| Dredged/Excavated | 1 |

The seagrass and unconsolidated-sediment classes provide **1,930 mapped habitat polygons** that may help identify candidate shallow-flat complexes. They are not, by themselves, named flats or proof of fish habitat suitability.

### Spatial QA finding

A first overlay check found **69 of the 7,222 benthic polygons do not intersect the union of the two source-footprint geometries**. Most are NPS patch-reef or unclassified features, but 15 are seagrass polygons (14 continuous, one discontinuous). Do not silently discard or treat these as valid coverage. The next review must inspect their source attribution and location, and decide whether this reflects footprint-layer semantics, source-map seams, or genuine out-of-footprint records.

### What this establishes, and what it does not

Established:
- FWC v2.2 provides actual Biscayne-labelled polygon geometries and source attribution.
- The northern FWC mapping footprint and the NPS mapping footprint overlap in latitude but have different spatial extents and source dates.
- Continuous/discontinuous seagrass and unconsolidated sediment are present as mapped polygon classes.

Not established:
- The legal aquatic-preserve polygon.
- A bay-wide ecological boundary.
- Exact northern/central/southern subregion boundaries.
- Named flat perimeters such as Safety Valve.
- Channel centerlines, inlet polygons, or validated inlet-to-waterbody topology.
- Species-specific suitability or fish presence.

The next step is to overlay these footprints with the statutory preserve GIS layer, shoreline, bathymetry, and NOAA ENC channel features. Only then should named subregions, flat complexes, or inlet connections receive verified geometries.
