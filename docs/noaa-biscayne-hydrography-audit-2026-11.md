# NOAA ENC hydrography audit for Biscayne Bay (November 2026)

## Purpose

Extract chart-derived hydrographic geometries for the South Florida pilot and determine which named bays, flats, channels, and cuts have directly attributable source geometry. This is a research-only source audit. It does not alter production scoring or species profiles.

## Source services

- NOAA ENC Harbour MapServer: https://encdirect.noaa.gov/arcgis/rest/services/encdirect/enc_harbour/MapServer
- NOAA Harbour ENC service description: large-scale Harbour compilation, nominal 1:5,000 to 1:50,000; refreshed weekly; explicitly not intended for navigation.
- NOAA Harbour ENC named water areas: layer 237, polygon geometry.
- NOAA Harbour ENC dredged areas: layer 228, polygon geometry.
- NOAA Harbour ENC canal areas: layer 170, polygon geometry.
- NOAA Harbour ENC tideway areas: layer 205, polygon geometry.
- NOAA Harbour ENC named-water label points: layer 41, point geometry.
- NOAA Harbour ENC navigation lines: layer 132, line geometry.
- NOAA Harbour ENC fairway areas: layer 208, polygon geometry.
- NOAA Harbour ENC deep-water route parts: layer 207, polygon geometry.
- NOAA Harbour ENC two-way route parts: layer 216, polygon geometry.
- NOAA Harbour ENC recommended-route centerlines: layer 133, line geometry.
- NOAA Coastal Maintained Channels theme layer: https://encdirect.noaa.gov/arcgis/rest/services/NavigationChartData/MarineTransportation/MapServer/1

NOAA documentation explains that the GIS service is derived from NOAA ENCs, organized by S-57 object classes, refreshed weekly, and not certified for navigation:
https://www.nauticalcharts.noaa.gov/learn/encdirect/

## Extraction area and workflow

Query envelope (EPSG:4326): longitude -80.55 to -80.05, latitude 25.20 to 26.10.

Successful expanded extraction and persistence workflow:
https://github.com/markeetox/LUPITA/actions/runs/43353615332

Artifact ID: 14004372911  
Artifact name: `noaa-biscayne-hydrography-review`

All extracted geometries passed coordinate-range and geometry-type validation.

## Results by layer

| Source layer | Returned features | Geometry | Notes |
|---|---:|---|---|
| Coastal Maintained Channels | 149 | 136 Polygon, 13 MultiPolygon | Includes Miami Harbor Channel, Dinner Key Channel, Deering Bay Channel, Turkey Point Channel, Miami River segments, and Intracoastal Waterway segments |
| Harbour Dredged Areas | 161 | Polygon | Charted dredged-area polygons |
| Harbour Named Water Areas | 189 | Polygon | Includes Biscayne Bay, Card Sound, Safety Valve, Biscayne Flats, Bear Cut, and Norris Cut |
| Harbour Canal Areas | 13 | Polygon | Includes Mowry Canal, Florida City Canal, Military Canal, North Canal, and Little River |
| Harbour Tideway Areas | 0 | None | No features returned in this query area |
| Harbour Fairway Areas | 62 | Polygon | Includes three named Miami Harbor Channel fairway polygons across three ENC cells |
| Harbour Deep Water Route Parts | 0 | None | No features returned in this query area |
| Harbour Two-Way Route Parts | 0 | None | No features returned in this query area |
| Harbour Recommended Route Centerlines | 0 | None | No features returned in this query area |
| Harbour Named Water Area Points | 0 | None | No point label anchors returned |
| Harbour Navigation Lines | 8 | LineString | All returned features were unnamed |

The result geometry extents can extend beyond the query envelope because features intersecting the envelope are returned in full.

## Named water-area findings

### Biscayne Bay

- 37 charted named-water polygons across 17 ENC cells.
- Feature source dates range from 2002-10-05 through 2011-02.
- These are chart-cell fragments, not a single continuous bay boundary.
- Preserve the source polygons separately until edge matching, overlap/gap review, and shoreline reconciliation are complete.
- Do not use this charted label mosaic as a substitute for the FDEP preserve polygon or as a final ecological boundary.

### Card Sound

- Six charted polygons across five ENC cells.
- Source date 2003-04.
- Keep Card Sound distinct from Biscayne Bay, while retaining its geographic relationship in the broader South Florida context.

### Safety Valve

- Four charted named-water polygons across four ENC cells.
- Source date 2002-10-05.
- The S-57 feature class is named water area. It is not classified as a flat or channel habitat by this layer.
- Do not continue to describe Safety Valve as a validated flat/channel complex solely from this source.

### Biscayne Flats

- Three charted polygons across two ENC cells.
- Source category: `mud flats`.
- Source date 2002-10-05.
- This is a useful named flat candidate, but the old chart classification does not prove current substrate condition, seagrass, fish use, or species suitability.

### Bear Cut

- One directly named polygon was returned: OBJECTID 253451.
- Chart cell: `US5MIACC.000`; source chart: NOAA Chart 11465.
- Source date: 2002-10-05.
- Geometry bounds: [-80.1646204, 25.725, -80.1506732, 25.7362954].
- The polygon passed geometry validation and is now persisted as feature 253451 in data/spatial/noaa-biscayne-named-water-areas.geojson.
- Its topology precheck passed as a single valid component.
- It represents a charted named-water area, not a surveyed channel centerline or current controlling-depth boundary.

NOAA Coast Pilot 4, Chapter 11, paragraph 39 describes the Rickenbacker Causeway bridge over Bear Cut:
https://nauticalcharts.noaa.gov/publications/coast-pilot/files/cp4/CPB4_WEB.pdf

## Channel and inlet findings

### Miami Harbor Channel fairway

The maintained-channel theme returned 44 features with `FAIRWAY = Miami Harbor Channel` across five ENC cells. Individual feature names include Cut-1 through Cut-4, Fisher Island Turning Basin, Fishermans Channel, Dodge Island Cut, and Miami Harbor Channel.

These must remain separate source features. A shared fairway attribute does not mean every segment is Government Cut.

Some returned features carry source information warning that the depiction is minimal and does not support safe navigation. Do not use the source depth attributes as current controlling depths.

### Government Cut

The structured feature layers queried here did not return a directly named Government Cut polygon or line. NOAA Harbour layer 208 returns three named Miami Harbor Channel fairway polygons across cells US5MIACB.000, US5MIACC.000, and US5MIACD.000. The maintained-channel theme also returns 44 features with FAIRWAY = Miami Harbor Channel across five ENC cells. These are project-channel context, not a direct Government Cut feature crosswalk. The expanded route-layer query returned no deep-water route-part, two-way route-part, or recommended-route centerline features in the query area.

NOAA Coast Pilot 4, Chapter 10, paragraph 414 describes the federal project channel from the sea buoy to inside Government Cut, then onward to Fisher Island Turning Basin and Fishermans Channel. This provides a textual crosswalk target, but the exact ENC feature-to-Government-Cut assignment still needs review.

### Norris Cut

NOAA Coast Pilot 4, Chapter 11, paragraph 38 describes Norris Cut as a shallow inlet just south of the Main Channel to Miami Harbor between Fisher Island and Virginia Key.

The expanded NOAA Harbour ENC extraction found one directly named Norris Cut polygon in layer 237:

- OBJECTID 253447.
- Chart cell US5MIACC.000; source chart NOAA Chart 11468.
- Source date 2004-01.
- Geometry type Polygon; valid geometry.
- Bounds: [-80.1498818, 25.7503267, -80.1396955, 25.7620415].

This source polygon is now included in the curated named-water GeoJSON and feature catalog. It is a charted named-water area, not a surveyed channel centerline or current controlling-depth boundary. It establishes a directly attributable chart feature, not the full physical inlet channel or its ecological connectivity.

## Catalog changes in this PR

The research feature catalog now records:

- 37 Biscayne Bay chart fragments as a source set, not a dissolved boundary.
- Six Card Sound chart fragments.
- Four Safety Valve named-water polygons, correctly typed as a named-water complex rather than a validated flat/channel complex.
- Three Biscayne Flats mud-flat polygons as a candidate named flat complex.
- Bear Cut and Norris Cut as directly named NOAA charted water-area features, with source OBJECTIDs, chart cells, source dates, and bounds.
- The 44 maintained-channel features carrying FAIRWAY = Miami Harbor Channel, plus three separately named Miami Harbor Channel fairway polygons from Harbour layer 208.
- Norris Cut as a directly named charted named-water polygon, OBJECTID 253447, with channel-centerline and current controlling-depth status still unverified.
- Government Cut as a named feature with its exact subgeometry still pending; nearby Miami Harbor Channel features are not assigned to it by guesswork.

The source index is stored in `data/spatial/noaa-biscayne-hydrography-index.json`.

## Persisted source geometries and topology precheck

The research workflow now runs scripts/curate_noaa_named_water_geometries.py after extraction and persists:

- data/spatial/noaa-biscayne-named-water-areas.geojson: 46 original source polygons, preserving each NOAA OBJECTID and source attributes.
- data/spatial/noaa-biscayne-named-water-topology-audit.json: source IDs, chart cells, source dates, geometry validity, overlap checks, union component counts, and bounds.
- data/spatial/feature-catalog.json: links five named-water contexts (Biscayne Bay, Safety Valve, Biscayne Flats, Bear Cut, and Norris Cut) to the persisted source set and records the current validation state.

The initial topology precheck found:

| Named feature | Source polygons | Connected components | Material overlap pairs |
|---|---:|---:|---:|
| Biscayne Bay | 37 | 2 | 0 |
| Safety Valve | 4 | 1 | 0 |
| Biscayne Flats | 3 | 1 | 0 |
| Bear Cut | 1 | 1 | 0 |
| Norris Cut | 1 | 1 | 0 |

The Biscayne Bay union's second component is a very small isolated chart fragment (bounds approximately -80.3250 to -80.3239 longitude and 25.5342 to 25.5355 latitude). It is retained as a source feature and is not bridged to the main component.

Safety Valve and Biscayne Flats each form one connected component, but that does not prove ecological connectivity, current habitat condition, or a complete boundary. All source polygons remain separate in the GeoJSON; no dissolved geometry is persisted.

The curator, persisted-catalog validation, and branch persistence ran successfully in NOAA hydrography workflow run:
https://github.com/markeetox/LUPITA/actions/runs/43353615332

The workflow ran 5 NOAA extraction/curation tests and 8 post-curation spatial-catalog tests successfully. The repository-wide Python test workflow passed 201 tests, with 1 optional Shapely-dependent test skipped and 54 warnings.

## Limitations and next review

1. NOAA's weekly service refresh does not make old source feature dates current. Several named-water features retain source dates from 2002 to 2011.
2. NOAA ENC Direct to GIS is not a navigation product. Use current official ENC products and local authorities for navigation.
3. Named chart polygons do not establish habitat, salinity, flow, tidal exchange, fish movement, or ecological suitability.
4. The charted Biscayne Bay fragments do not form a complete ecological or statutory boundary. Reconcile them against FDEP management geometry, authoritative shoreline, and tidal connections.
5. Government Cut still needs an exact chart-feature crosswalk. Norris Cut now has a directly named charted polygon, but its full inlet channel centerline and current controlling-depth boundary remain unverified.
6. No production scores, thresholds, weights, species profiles, or API v1 contracts were changed.

## Immediate next milestone

- Reconcile the 37 Biscayne Bay fragments against the FDEP preserve geometry and authoritative shoreline evidence, without conflating ecological and statutory boundaries.
- Review Safety Valve and Biscayne Flats against benthic habitat and bathymetry sources before assigning ecological feature types.
- Crosswalk the Miami Harbor Channel fairway and maintained-channel features to Government Cut without assigning segments by proximity.
- For Norris Cut, retain the named-water polygon and investigate separate centerline/depth evidence if those attributes are needed.
- Then connect verified spatial feature IDs to Bonefish and Permit species context without changing production scoring.
