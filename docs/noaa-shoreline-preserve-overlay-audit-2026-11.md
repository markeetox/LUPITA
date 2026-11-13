# NOAA shoreline overlay screening audit (November 2026)

## Purpose and scope

This is a geometry-screening overlay of the newly persisted Florida DEP-hosted NOAA comparison linework against the two distinct FDEP Biscayne-area aquatic-preserve polygons. It checks spatial distribution and line-length accounting only. It does **not** establish an ecological Biscayne Bay boundary, shoreline accuracy, tidal connectivity, navigability, or fish habitat.

All measurements were calculated after transforming EPSG:4326 geometries to NAD83 / UTM zone 17N (EPSG:26917). The source geometries were not modified.

## Inputs

- `data/spatial/research/noaa_composite_shoreline_mhw_biscayne.geojson`: NOAA Composite Shoreline, layer 41, historic T-sheet-derived MHW context.
- `data/spatial/research/noaa_mhhw_screening_line_biscayne.geojson`: NOAA MHHW predicted screening extent, layer 40.
- `data/spatial/research/noaa_cmp/overlay/fdep_biscayne_aquatic_preserves.geojson`: FDEP preserve features OBJECTID 43 and 25, kept separate.

The NOAA comparison geometries were clipped to the rectangular review extent `[-80.45, 25.25, -80.05, 26.00]`, not to the Biscayne Bay polygon. The FDEP features are management boundaries and are not ecological shoreline boundaries.

## Geometry validation and scale

| Product | Features | MultiLineString parts | Geodesic length in review rectangle |
|---|---:|---:|---:|
| NOAA Composite Shoreline (MHW context) | 7 | 2,480 | 1,207.14 km |
| NOAA MHHW screening line | 2 | 13,314 | 2,780.63 km |

All 9 feature geometries are valid line geometries. The large lengths and part counts reflect extensive segmented line networks inside the rectangular review window. They are not coastline-length estimates.

## Overlay against FDEP Biscayne Bay Aquatic Preserve (OBJECTID 43)

FDEP reports an area of approximately 261.411 km² for OBJECTID 43.

| NOAA product/class | Line length inside preserve |
|---|---:|
| MHW context: Apparent shore (2 source features) | 69.306 km |
| MHW context: Approx. Shore | 3.114 km |
| MHW context: Gen. manmade object | 139.532 km |
| MHW context: SPOR (2 source features) | 93.620 km |
| MHW context: User added line | 0.052 km |
| **MHW context total, classes kept distinct** | **305.624 km** |
| **MHHW screening line, separate product** | **377.169 km** |

The 139.532 km of linework classified as `Gen. manmade object` and 93.620 km classified as `SPOR` demonstrate why the composite layer cannot be treated as one natural shoreline. The `User added line` class is retained as a separate source category and is not accepted as a surveyed closure or water connection.

The MHHW result is a screening network, not a shoreline trace. It remains separate from the MHW product.

## Overlay against FDEP Cape Florida to Monroe County Line Aquatic Preserve (OBJECTID 25)

FDEP reports an area of approximately 16.840 km² for OBJECTID 25.

- MHW composite linework inside: approximately 0.009 km, all from a man-made-object feature.
- MHHW screening linework inside: approximately 0.942 km.

This is a separate preserve feature and must not be silently merged with OBJECTID 43 or treated as a missing segment of the ecological bay boundary.

## Interpretation

1. The overlay confirms that both comparison products intersect the FDEP management polygon, but the intersecting linework is heterogeneous and highly segmented.
2. The historic composite's source classes include apparent, approximate, man-made, SPOR, and user-added linework. Those classes have different meanings and cannot be dissolved into a single boundary.
3. The MHHW product is a predicted screening extent. Its intersections do not prove current water connectivity or a surveyed shoreline.
4. The rectangular query extent is broader than the bay and clips features at its edges. It is not a study-area polygon.
5. The FDEP aquatic-preserve polygons are management overlays. Their geometry is not a substitute for an ecological waterbody boundary, and the two preserve features remain separate.
6. These overlays do not validate inlet connections, channels, or cross-bay ecological subregion boundaries.

## Next defensible step

Use the project-specific NOAA NGS MHW vectors from FL1808A / GC12021 and FL1808C / GC12023 as the primary modern shoreline candidates. Inspect their actual line geometry and project-neatline footprints against the separate FDEP preserve and NOAA ENC named-water context. Keep MLLW depth contours, MHW shoreline, historic T-sheet linework, MHHW screening lines, and management polygons as distinct layers. Do not bridge gaps or infer inlet connectivity from proximity.

## Guardrails

- No final Biscayne Bay boundary is created by this audit.
- No linework is dissolved across source classes or tidal products.
- No shoreline or channel geometry is inferred from nearest-neighbor proximity.
- No production scoring, species profiles, thresholds, or API behavior changed.
