# Biscayne Bay subregion and habitat-candidate audit (November 2026)

## Executive result

The research catalog now separates three published ecological sections of Biscayne Bay:

| Region | Published landmark limits | Geometry status |
|---|---|---|
| North Biscayne Bay | Dumfoundling Bay to Rickenbacker Causeway | Landmark limits identified; cross-bay boundary line pending |
| Central Biscayne Bay | Rickenbacker Causeway to Featherbed Bank / Black Point | Landmark limits identified; cross-bay boundary line pending |
| South Biscayne Bay | Featherbed Bank / Black Point to Card Sound / Jewfish Creek | Landmark limits identified; cross-bay boundary line pending |

These extents are described in the 2022 peer-reviewed study by Ellery Lennon and Sullivan Sealey, which cites the earlier ecological segmentation literature. The source gives geographic landmarks, not ready-made GIS polygons. LUPITA therefore stores the three named contexts with null geometry rather than fabricating boundary lines.

Source: https://doi.org/10.3389/fmars.2022.894663

## Source data

The current FWC Unified Reef Map Level 1 extraction returned 7,222 benthic polygons:

- 5,886 attributed to Biscayne Bay NPS.
- 1,336 attributed to Biscayne Bay FWC.
- 602 Seagrass (Continuous).
- 828 Seagrass (Discontinuous).
- 500 Unconsolidated Sediment at Level 1.
- 5,122 Individual or Aggregated Patch Reef.
- 219 Tidal Flats in the union of the two source-map footprints.
- Other classes include Not Classified, scattered coral/rock, artificial, and dredged/excavated.

Source service:
https://gis.myfwc.com/hosting/rest/services/Projects_FWC/UnifiedReefMapProject_v2_2/MapServer/7

The source mapping footprints describe the coverage of the mapping projects. They are not a legal, statutory, or ecological bay boundary. The source mapping dates are 2005-2013.

## Tidal-flat patch inventory

The extraction identified 219 individual FWC/NPS source polygons classified as Tidal Flats within the combined source-map footprints.

- Combined unique mapped area: approximately 0.833 km².
- 186 source patches intersect the FDEP Biscayne Bay Aquatic Preserve OBJECTID 43.
- 33 source patches do not intersect that preserve polygon.

All 219 original source geometries are preserved individually in:

- `data/spatial/biscayne-tidal-flat-patches.geojson`

No dissolve, clustering, gap filling, or invented named-flat boundary is performed. The 33 patches outside the preserve polygon are not automatically outside Biscayne Bay; the preserve is a management boundary, not the ecological bay limit.

## Named NOAA chart context and benthic overlay

The audit intersects the FWC/NPS benthic source polygons with individually preserved NOAA Harbour ENC named-water polygons. Areas are measured in NAD83 / UTM zone 17N (EPSG:26917). The table reports counts of intersecting source features, not fish habitat quality.

| NOAA chart context | Chart polygons | Intersecting benthic polygons | Mapped Tidal Flats | Key mapped classes |
|---|---:|---:|---:|---|
| Biscayne Bay | 37 | 1,453 | 186 | 500 continuous seagrass; 549 discontinuous seagrass; 129 unconsolidated sediment; 89 not classified |
| Safety Valve | 4 | 219 | 0 | 160 discontinuous seagrass; 55 unconsolidated sediment; 2 continuous seagrass |
| Biscayne Flats | 3 | 54 | 0 | 35 discontinuous seagrass; 17 unconsolidated sediment; 1 continuous seagrass; 1 artificial |
| Bear Cut | 1 | 31 | 7 | 10 continuous seagrass; 11 discontinuous seagrass |
| Norris Cut | 1 | 27 | 6 | 8 continuous seagrass; 10 discontinuous seagrass |
| Black Ledge | 3 | 3 | 0 | 1 continuous; 2 discontinuous seagrass |
| Featherbed Bank | 1 | 1 | 0 | 1 continuous-seagrass polygon |
| Lewis Cut | 1 | 2 | 0 | 1 continuous seagrass; 1 unconsolidated sediment |
| Biscayne Channel | 2 | 0 | 0 | No intersecting polygons returned in this benthic source |
| Sands Cut | 1 | 2 | 0 | 1 continuous seagrass; 1 unconsolidated sediment |
| Snapper Creek Canal | 1 | 1 | 0 | 1 not-classified polygon |
| Goulds Canal | 1 | 2 | 0 | 1 continuous seagrass; 1 unconsolidated sediment |
| Deering Channel | 1 | 11 | 0 | 5 continuous; 5 discontinuous seagrass |
| Cape Florida Channel | 2 | 17 | 1 | 9 continuous; 6 discontinuous seagrass |

### Important interpretation

The chart label "Biscayne Flats" is classified as mud flats in the old NOAA ENC source. The FWC/NPS mapping overlay does not return any polygons classified as Tidal Flats inside those three chart polygons. It does return mapped seagrass and unconsolidated-sediment features.

That does not prove that the named area contains no flats today. It shows that the old chart classification and the later benthic map do not match one-to-one. Keep the chart name, chart category, and later benthic classes as separate evidence.

Similarly, Safety Valve is described in NOAA literature as a broad grass-flat and tidal-channel water-exchange area, but the FWC/NPS overlay contains no polygons classified as Tidal Flats inside the four NOAA charted Safety Valve polygons. The overlay does show extensive mapped seagrass and sediment features. This is not a contradiction: "Tidal Flats" is one mapped benthic class, not a synonym for all shallow grass flats.

The Biscayne Channel chart polygons have no intersecting benthic polygons in this extraction. This is a source coverage result, not evidence that the channel is unvegetated or ecologically empty.

NOAA chart geometry source:
https://encdirect.noaa.gov/arcgis/rest/services/encdirect/enc_harbour/MapServer/237

## Geometry QA

Two benthic source polygons (OBJECTIDs 6548 and 7142) were invalid under the geometry validity check. The analysis uses Shapely `make_valid()` only for overlay calculations. Original source geometries are not overwritten or substituted in the preserved source records.

The 219 tidal-flat polygons passed the polygon validity checks and are preserved individually. The source polygons are not merged into named flat complexes because spatial proximity alone is not enough to justify ecological grouping.

## Data products

- `data/spatial/biscayne-subregion-habitat-audit.json`: subregion definitions, named-context overlays, source IDs, class counts, and overlay areas.
- `data/spatial/biscayne-tidal-flat-patches.geojson`: 219 original mapped tidal-flat polygons.
- `data/spatial/feature-catalog.json`: North/Central/South contexts and links from 14 named chart contexts to their habitat-overlay audit entries.

## Next GIS milestone

1. Digitize cross-bay boundary lines using the published landmarks: Rickenbacker Causeway, Featherbed Bank / Black Point, and Card Sound / Jewfish Creek.
2. Verify each landmark against NOAA shoreline, ENC, FWC/FDEP, and other authoritative geometry. Do not use the old charted named-water polygons as substitutes for causeway or shoreline boundary lines.
3. Build candidate mangrove-edge features from a current, authoritative mangrove source, keeping them separate from vegetation labels in old ENC chart data.
4. Reconcile charted depth contours and depth areas with NCEI S200 and available modern BAG surveys. Vertical datums and depth units must be resolved before combining values.
5. Only after geometry QA, attach geographic context IDs to Bonefish and Permit species profiles. The overlay counts are not species-suitability scores.

## Guardrails

- No complete ecological bay polygon is asserted.
- No legal or FDEP management boundary is used as an ecological boundary.
- No inlet or channel connection is inferred from adjacency or polygon proximity.
- No old chart category is promoted to current habitat condition.
- No mapped habitat class is treated as proof of Bonefish or Permit presence.
- No species profiles, prediction weights, thresholds, production spatial layers, or API behavior are changed.
