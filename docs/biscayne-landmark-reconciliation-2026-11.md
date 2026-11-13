# Biscayne Bay ecological landmark reconciliation: candidate inventory

**Status:** candidate references partially resolved; cross-bay separator geometry pending.  
**Coordinate system:** EPSG:4326 for listed point coordinates and bounding boxes.  
**Scope:** research-only. No subregion polygon or separator line is created.

## Literature-defined extents

The 2022 peer-reviewed ecological segmentation describes:
- North Biscayne Bay: Dumfoundling Bay to Rickenbacker Causeway.
- Central Biscayne Bay: Rickenbacker Causeway to Featherbed Bank / Black Point.
- South Biscayne Bay: Featherbed Bank / Black Point to Card Sound / Jewfish Creek.

Source: [Frontiers in Marine Science (2022)](https://doi.org/10.3389/fmars.2022.894663).

These are landmark limits, not digitized cross-bay boundary lines. The paired names and their spatial meaning must be resolved before a cross-bay separator can be drawn.

## Candidate landmark evidence

### Dumfoundling Bay

A GNIS-derived feature page reports GNIS Feature ID 281852 at 25.9452653, -80.1298124. This is a candidate named-feature reference point only. The coordinate has not yet been verified against a direct current USGS GNIS record, so it is not promoted as an authoritative geometry.

Sources: [GNIS-derived feature reference](https://geo.mytopo.com/feature/florida/miami-dade/bay/281852/dumfoundling-bay/), [USGS GNIS overview](https://www.usgs.gov/tools/geographic-names-information-system-gnis).

### Rickenbacker Causeway

Miami-Dade County describes the causeway as a 3.6-mile corridor with multiple roadway and bridge segments. The County's persisted bridge inventory contains separate bridge lines, including Bear Cut Bridge (Bridge 874544) and the east/west Biscayne Bay bridges (874541/874542). These provide source-backed local crossing geometry, but they do not reconstruct the entire causeway corridor or independently define the ecological separator.

Sources: [Miami-Dade Rickenbacker Causeway](https://www.miamidade.gov/global/transportation/public-works/rickenbacker-causeway.page), [Bear Cut Bridge fact sheet](https://www.miamidade.gov/resources/transportation_publicworks/documents/bear-cut-bridge-fact-sheet.pdf).

### Featherbed Bank

NOAA ENC Harbour named-water layer 237 contains Featherbed Bank, OBJECTID 246301, chart cell US5FL5LN.000, source date 2002-10-05. The persisted source index records it as a charted bank. Its verified bounding box is:

`[-80.235417, 25.516618, -80.218433, 25.531581]`

This is a charted named-feature polygon, not a boundary line or current habitat survey.

### Black Point

Miami-Dade County's Black Point Marina page gives the outer channel marker position as 25°31.5′ N, 80°17.9′ W (25.525, -80.298333). This is a navigation approach marker offshore of the marina, not the Black Point shoreline and not a regional boundary.

Source: [Miami-Dade Black Point Park and Marina](https://www.miamidade.gov/parks/black-point-marina.asp).

Featherbed Bank and Black Point remain distinct references. We should not average them into a midpoint or assume they describe one precise cross-bay line.

### Card Sound

NOAA ENC source index records six Card Sound named-water polygons:
- OBJECTIDs 246233, 246243, 246247, 246258, 246267, 246284.
- Five chart cells: US5FL5IL.000, US5FL5IM.000, US5FL5IN.000, US5FL5JM.000, US5FL5JN.000.
- Source date: 2003-04.

The exact source IDs are known, but these six geometries are not yet in the curated named-water GeoJSON. Retrieve them by exact OBJECTID and preserve their chart-cell provenance before attempting a mosaic or topology review.

### Jewfish Creek

NOAA CO-OPS identifies station 8723613 as **JEWFISH CREEK, BARNES SOUND, FL**, at 25.18330 N, 80.39000 W, on NOAA Chart 11462. This is an official tidal benchmark reference point, not the creek centerline, mouth, or ecological boundary.

NOAA Coast Pilot describes Card Sound, Little Card Sound, Barnes Sound, and Jewfish Creek as distinct waterway reaches. Therefore, the paired literature label "Card Sound / Jewfish Creek" should not be collapsed into one point.

Sources: [NOAA CO-OPS benchmark 8723613](https://tidesandcurrents.noaa.gov/benchmarks/8723613.html), [NOAA Coast Pilot 4](https://nauticalcharts.noaa.gov/publications/coast-pilot/files/cp4/CPB4_WEB.pdf).

## Decisions and next work

1. Retrieve direct USGS GNIS data for Dumfoundling Bay.
2. Reconstruct the Rickenbacker Causeway corridor from county roadway, bridge, and land geometry.
3. Retrieve all six Card Sound NOAA ENC polygons by exact OBJECTID.
4. Retrieve chart/hydrographic geometry for Jewfish Creek, keeping it separate from the tidal station.
5. Resolve the paired Featherbed Bank / Black Point and Card Sound / Jewfish Creek landmark meaning.
6. Test candidate feature membership only after these references are spatially represented.

**No cross-bay boundary lines or North/Central/South polygons are created in this pass.** The machine-readable candidate inventory is `data/spatial/research/biscayne-landmark-candidates.json`.
