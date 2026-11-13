# Biscayne Bay boundary reconciliation research note (November 2026)

## Purpose

Compare the NOAA ENC named-water fragments with the separate FDEP Biscayne Bay Aquatic Preserve management geometry, and identify a stronger shoreline source for building a defensible Biscayne Bay ecological-waterbody geometry.

This is a research-only boundary audit. It does not select a final bay boundary or alter production scoring, species profiles, or API v1.

## Current source geometry sets

### NOAA ENC named-water fragments

The curated source set is stored in:

- `data/spatial/noaa-biscayne-named-water-areas.geojson`
- `data/spatial/noaa-biscayne-named-water-topology-audit.json`

The 37 NOAA Harbour ENC polygons named Biscayne Bay span 17 ENC cells and source dates from 2002-10-05 through 2011-02. Their geometric union has two connected components, including one very small isolated chart fragment. The source polygons are preserved individually; no dissolved boundary is stored.

### FDEP Biscayne Bay Aquatic Preserve

PR #69's extracted FDEP geometry artifact contains the distinct Biscayne Bay preserve feature, OBJECTID 43, reported as 64,607.58 acres. This is an approximate management GIS boundary associated with the aquatic-preserve designation. It is not a legal survey and is not interchangeable with the ecological waterbody boundary.

Source service:
https://ca.dep.state.fl.us/arcgis/rest/services/OpenData/AQUATIC_PRESERVES/MapServer/0

## Overlay precheck

The NOAA Biscayne Bay named-water union and FDEP OBJECTID 43 were transformed to NAD83 / UTM zone 17N (EPSG:26917) for area calculations.

| Measure | Area |
|---|---:|
| NOAA charted named-water union | 512.865 km² |
| FDEP Biscayne Bay preserve polygon | 261.411 km² |
| Geometric intersection | 180.106 km² |
| NOAA union outside FDEP polygon | 332.759 km² |
| FDEP polygon outside NOAA union | 81.306 km² |

Directional coverage ratios:

- Intersection / FDEP preserve area: 68.9%.
- Intersection / NOAA charted named-water union area: 35.1%.

These are geometric overlay statistics, not accuracy scores. The source layers describe different things: NOAA's old charted named-water features and FDEP's approximate statutory management area. Their mismatch is expected and neither layer should be forced to match the other. The NOAA chart fragments are not a complete bay boundary, and the FDEP preserve is not the ecological bay boundary.

## Stronger shoreline source candidates

NOAA National Geodetic Survey Coastal Mapping Program has two project datasets directly relevant to Biscayne Bay:

### FL1808C-TB-N / GC12023

- Coverage description: Rickenbacker Island southward to Snapper Creek Canal.
- Compilation completed June 2024; final quality-control review completed June 2024.
- Provides mean-high-water (MHW) shoreline and mean-lower-low-water (MLLW) vectors, plus MHW/MLLW 1 m DEM products.
- Reported 95% horizontal accuracy: 2.3 m for MHW lidar-derived shoreline, 3.0 m for MLLW lidar-derived shoreline, and 1.3 m for well-defined imagery-derived cartographic features.
- NOAA Shoreline Data Explorer is listed as the shapefile and metadata distribution point.

Project report:
https://www.ngs.noaa.gov/desc_reports/FL1808C-TB-N.PDF

InPort metadata:
https://www.fisheries.noaa.gov/inport/item/73241

### FL1808A-TB-N / GC12021

- Coverage description: Fender Point to Card Sound.
- Compilation completed May 2024; final quality-control review completed July 2024.
- Provides MHW and MLLW shoreline vectors and 1 m DEM products.
- Reported 95% horizontal accuracy: 2.3 m for MHW lidar-derived shoreline, 3.0 m for MLLW lidar-derived shoreline, and 1.3 m for well-defined imagery-derived cartographic features.
- The project used 2018 topobathy lidar and April 2019 imagery; the report records a 0.14 m imagery ground-sample distance.
- NOAA Shoreline Data Explorer is listed as the shapefile and metadata distribution point.

Project report:
https://www.ngs.noaa.gov/desc_reports/FL1808A-TB-N.pdf

InPort metadata:
https://www.fisheries.noaa.gov/inport/item/74866

These projects are promising high-accuracy shoreline sources, but their footprints must be inspected before assuming they provide complete, seamless coverage of Biscayne Bay. Their MHW and MLLW lines represent different tidal datums and must not be mixed as if they were one shoreline.

### Supplemental local and historical shoreline sources

Two additional NOAA NGS records are relevant, but they should not be treated as a seamless current shoreline:

- **FL1603A-CM-N, Convoy Point:** small local coverage around Convoy Point (metadata extent approximately 25.4464–25.4782 N), based on imagery from 2017-03-19. Metadata reports 1.9 m horizontal accuracy at 95% confidence. It is useful as a local comparison source, not a bay-wide boundary.
  - InPort metadata: https://www.fisheries.noaa.gov/inport/item/61478
  - Completion report: https://www.ngs.noaa.gov/desc_reports/FL1603A-CM-N.PDF
- **FL1934E, Biscayne Bay historical shoreline rescue:** vectorized historic shoreline from survey maps dated 1934-08-01 through 1935-01-25. This is valuable for historical shoreline-change context, not current shoreline geometry.
  - InPort metadata: https://www.fisheries.noaa.gov/inport/item/63718

The published rectangular metadata extents for FL1808A and FL1808C also deserve a coverage check. FL1808A spans approximately 25.3252–25.5119 N, while FL1808C spans approximately 25.6345–25.7729 N. This leaves an apparent latitude interval between the two project extents. NOAA metadata warns that rectangular geographic limits are for data management and do not imply complete surveyed coverage, so this is not yet proof of an actual shoreline gap. The exact geographic-cell geometries must be retrieved and inspected before describing coverage as continuous.

### NOAA CUSP as a secondary check

NOAA's Continually Updated Shoreline Product (CUSP) is intended to provide the most up-to-date shoreline and incorporates contemporary NOAA and non-NOAA sources. NOAA explicitly states that CUSP has less stringent acquisition and quality-control requirements than the project-based National Shoreline. Use CUSP as a currency/completeness comparison, not as a substitute for the project-specific MHW/MLLW vectors without reviewing its source and quality metadata.

NOAA Shoreline Data Explorer:
https://nsde.ngs.noaa.gov/

NOAA explanation of CUSP and National Shoreline:
https://nsde.ngs.noaa.gov/more.html

## Recommended next extraction

1. Retrieve GC12023 and GC12021 shoreline shapefiles and metadata through the NOAA Shoreline Data Explorer.
2. Preserve source project, geographic cell, MHW/MLLW datum, source dates, and feature attributes.
3. Compare project footprints for overlap and gaps before merging.
4. Inspect topological continuity and shoreline classification at the project seam.
5. Use the shoreline as a land-water constraint only. Define the bay's open-water boundary, inlets, and tidal connections using separate hydrographic and ecological evidence.
6. Keep the FDEP preserve as a separate management-boundary feature and retain the NOAA ENC named-water fragments as chart-derived context.

## Guardrails

- Do not dissolve NOAA chart fragments into a final bay boundary.
- Do not equate the FDEP aquatic preserve with the full ecological waterbody.
- Do not treat MHW and MLLW shoreline vectors as interchangeable.
- Do not infer inlet connectivity from proximity.
- Do not interpret charted mud-flat labels as current habitat observations.
- No production scoring, thresholds, species profiles, or API v1 fields were changed.
