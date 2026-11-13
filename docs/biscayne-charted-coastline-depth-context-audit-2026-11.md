# Biscayne Bay charted coastline and depth-context audit (November 2026)

## Purpose

This research-only pass expands the NOAA Harbour ENC extraction beyond named-water polygons. It inventories charted coastline, depth contours, depth areas, unsurveyed areas, land areas, seabed areas, and vegetation in the South Florida pilot extent.

The purpose is to characterize source coverage and data quality before defining shoreline subregions, flats, channels, or inlet connections. These features are not production model inputs and are not navigation products.

## Extraction and validation

NOAA ENC Direct to GIS Harbour-scale service:

- Service: https://encdirect.noaa.gov/arcgis/rest/services/encdirect/enc_harbour/MapServer
- Coastline line: layer 84, `Harbor.Coastline_line`
- Depth contour line: layer 104, `Harbor.Depth_Contour_line`
- Land area: layer 233, `Harbor.Land_Area`
- Depth area: layer 227, `Harbor.Depth_Area`
- Unsurveyed area: layer 230, `Harbor.Unsurveyed_Area`
- Seabed area: layer 200, `Harbor.Seabed_Area`
- Vegetation area: layer 239, `Harbor.Vegetation_area`
- Named-water polygons remain layer 237.

The extraction workflow completed successfully on research commit `7d2d34d14a196be97ea57d40cf4e705e5fac1b00`. All returned geometries passed coordinate validation, and no layer extraction errors were reported.

Review artifact: [NOAA hydrography review artifact](https://github.com/markeetox/LUPITA/actions/runs/43363005067)

## Full extraction inventory

| Layer | Features | Geometry |
|---|---:|---|
| Harbour coastline lines | 1,080 | LineString |
| Harbour depth contours | 1,894 | LineString |
| Harbour depth areas | 1,965 | Polygon |
| Harbour unsurveyed areas | 41 | Polygon |
| Harbour land areas | 518 | Polygon |
| Harbour vegetation areas | 143 | Polygon |
| Harbour seabed areas | 0 | No features returned |
| Harbour named-water areas | 189 | Polygon |

Other existing extracted navigation-context layers remain separate: 149 coastal maintained-channel features, 161 dredged areas, 62 fairway areas, 13 canal areas, and 8 unnamed navigation lines. Empty tideway, deep-water-route, two-way-route, and recommended-route-centerline layers are not evidence that no such features exist.

## Intervening geographic review window

A rectangular review window around the latitude band between the two CMP project extents was used for inventory only: approximately `[-80.43, 25.49, -80.10, 25.67]` in WGS84. This rectangle is not a shoreline, bay, habitat, or legal boundary.

Within that window:

| Layer | Intersecting features | Findings |
|---|---:|---|
| Coastline lines | 47 | 36 unclassified `CATCOA`, 8 mangrove, 3 marshy shore |
| Depth contours | 294 | Raw `VALDCO` values include 0, 0.9, 1.8, 3.6, and 5.4 |
| Depth areas | 320 | `DRVAL1` / `DRVAL2` ranges are present |
| Unsurveyed areas | 1 | Chart cell `US5FL5LN.000`, source date 2008-06 |
| Vegetation areas | 7 | All charted as mangroves, source date 2005-02-01 |
| Land areas | 27 | Includes charted islands and land polygons |
| Named-water areas | 41 | Includes Biscayne Bay, Safety Valve, Black Ledge, Biscayne Flats, and Biscayne Channel |

The 47 coastline features are distributed across multiple ENC chart cells. Their recorded source dates in this review window are predominantly 2003-04 and 2005-02, with some 2002-10 and 2004-11 records. The 7 vegetation polygons are all mangroves, not seagrass. Their chart date is 2005-02-01.

## Interpretation and guardrails

### Coastline

The Harbour coastline layer provides useful chart-derived linework in the area where the CMP project MHW sets are separated. It is not a modern, project-specific MHW survey. Coastline features carry chart-cell and source metadata; some are explicitly classified as mangrove or marshy shore, while many have blank `CATCOA`.

The coastline linework also lies on or very near portions of the FL1808A and FL1808C MHW geometry. This is not independent validation: chart features can derive from overlapping source surveys and chart compilation. Do not use the apparent overlap to upgrade the chart data's accuracy.

### Depth contours and depth areas

The extracted depth contours and depth-area polygons provide charted depth context. Preserve `VALDCO`, `DRVAL1`, `DRVAL2`, `VERDAT`, `DSNM`, `SORDAT`, and `SORIND` exactly as supplied.

In the reviewed depth contour and depth-area records, `VERDAT` is not populated. Until the source chart-cell metadata establishes the applicable vertical datum and depth units, do not merge these values with CMP MLLW depth contours, NOAA BAG data, or other bathymetry as if they shared a common datum.

### Unsurveyed areas

The one unsurveyed-area polygon intersecting the review window must be retained as a data-quality warning. It does not mean the area is dry, has zero depth, or contains no water.

### Vegetation and seabed

The 7 vegetation polygons are charted mangroves, with 2005 source dates. They are not a current mangrove survey and do not establish seagrass or fish habitat. The seabed-area layer returned zero features for the full extraction extent; that is a source-layer result, not evidence of a uniform seabed.

## NCEI bathymetry candidates

### Biscayne Bay S200 estuarine bathymetry DEM

- Metadata: https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ngdc.mgg.dem%3Abiscayne_bay_S200_2018
- DOI: https://doi.org/10.7289/V5GM85N8
- Grid: 1/3 arc-second, MLLW
- Bounding box: west -80.432361, east -80.120787, south 25.177176, north 25.930139
- Published 2018; last modified 2018-06-06.

Its footprint covers the intervening review window and makes it a useful broad bathymetric reference candidate. However, NCEI states that the DEM is primarily based on antiquated historical data and does not include many modern high-resolution BAG surveys. Treat it as background context until its source lineage and local coverage are compared with newer hydrographic surveys.

### Recent Port of Miami survey F00854

- Survey report: https://data.ngdc.noaa.gov/platforms/ocean/nos/coast/F00001-F02000/F00854/DR/F00854_DR.pdf
- Survey date: 2022-04-17
- Product: 0.5 m CUBE BAG, MLLW; reported depth range 2.41 m to 16.89 m.
- Survey purpose: obstruction investigation along the pier on the south side of Dodge Island.

This is a recent, high-resolution source, but its survey limits are local to the Port of Miami / Dodge Island pier. It does not fill the wider inter-project shoreline area.

### Historic Biscayne Bay surveys

NCEI also lists historic surveys including:

- H10493, Key Biscayne to Biscayne Flats, 1993-08-12 to 1993-09-20; MLLW / NAD83.
- H10473, vicinity of Soldiers Key, 1993-05-19 to 1993-08-11; MLLW / NAD83.
- H10474, vicinity of Sand Key, 1993-05-19 to 1993-08-12; MLLW / NAD83.

These are potential historical sounding and bottom-sample references, not current bathymetry. Retrieve and inspect their survey footprints and products before assigning any feature to a modern subregion.

## Correction to the 17.69 km MHW separation

The 17,690.77 m minimum separation between FL1808A and FL1808C MHW linework is a diagonal nearest-feature distance between shoreline features on different sides of the bay. It is not an along-shore gap measurement and must not be described as a missing 17.69 km coastline segment.

See the corrected interpretation in [the CMP MHW topology audit](noaa-cmp-mhw-topology-audit-2026-11.md).

## Decisions

1. Keep NOAA CMP MHW, Harbour ENC coastline, depth contours, depth areas, unsurveyed areas, vegetation, and named-water polygons as distinct feature classes.
2. Preserve chart-cell IDs and all source attributes; never merge features across chart cells without topology and source review.
3. Do not promote old charted coastline or mangrove polygons to current habitat or legal shoreline boundaries.
4. Resolve vertical datums before combining chart depth values with MLLW or other bathymetry.
5. Inspect NCEI S200 and historic survey products as separate bathymetric references; use the 2022 F00854 BAG only within its documented local survey limits.
6. Keep all findings research-only. No species profile, prediction score, production spatial layer, or API behavior is changed.

## Validation

- Python test suite passed on the extraction update: https://github.com/markeetox/LUPITA/actions/runs/43363005046
- NOAA hydrography extraction and curation passed: https://github.com/markeetox/LUPITA/actions/runs/43363005067
- NOAA shoreline service audit passed: https://github.com/markeetox/LUPITA/actions/runs/43363005066
- NOAA NSDE project discovery passed: https://github.com/markeetox/LUPITA/actions/runs/43363005049
- NOAA CMP/FDEP spatial alignment audit passed: https://github.com/markeetox/LUPITA/actions/runs/43363005166
