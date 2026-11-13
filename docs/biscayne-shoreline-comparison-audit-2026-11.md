# Biscayne shoreline comparison audit (November 2026)

## Scope

This is a research-only extraction of Florida-hosted NOAA-derived shoreline comparison layers for the South Florida pilot. It does not create a final Biscayne Bay boundary and does not change production scoring, species profiles, thresholds, or API v1.

Query extent (WGS84): `[-80.45, 25.25, -80.05, 26.00]`.

The extraction preserves the original ArcGIS source records in the workflow artifact and creates separate AOI-clipped GeoJSON copies for inspection. The clip is a rectangular review window, not a Biscayne Bay polygon.

## Retrieved layers

| Layer | Product/datum | Source records | Clipped features | Status |
|---|---|---:|---:|---|
| NOAA Composite Shoreline, layer 41 | Historic T-sheet-derived MHW shoreline context | 7 | 7 | Retrieved |
| NOAA Mean Higher High Water, layer 40 | Screening-level predicted MHHW extent | 2 | 2 | Retrieved |

Both layers returned complete source records with no failed object IDs in workflow run 43356033077:
https://github.com/markeetox/LUPITA/actions/runs/43356033077

The source files are retained in that workflow artifact. The repository stores only the rectangularly clipped review geometries and metadata.

## NOAA Composite Shoreline (MHW context)

Florida DEP's Map_Direct/Program_Support MapServer layer 41 is described as NOAA Office for Coastal Management composite shoreline derived from historic NOAA shoreline manuscripts (T-sheets). Its metadata warns that shoreline position may have changed through erosion, accretion, and human alteration since the source surveys.

Seven original source features intersected the query extent. Their `F_NAME` counts were:

| F_NAME | Features |
|---|---:|
| Apparent shore | 2 |
| Approx. Shore | 1 |
| Gen. manmade object | 1 |
| SPOR | 2 |
| User added line | 1 |

NOAA's C-COAST attribute definitions clarify that these are not interchangeable shoreline classes:

- **Apparent shore:** charted linework visible to a mariner where vegetation obscures the natural shoreline.
- **Approx. Shore:** approximate linework where man-made features obscure the shoreline.
- **SPOR:** Shoreline Plane of Reference linework delineating natural and man-made shoreline.
- **Gen. manmade object:** man-made objects forming a shore or waterline, including seawalls, wharves, revetments, wrecks, and similar features.
- **User added line:** operator-added linework that may be an artificial closure or connection, not a surveyed shoreline.

Source: NOAA C-COAST attribute dictionary, InPort item 49160:
https://www.fisheries.noaa.gov/inport/item/49160/full-list

The clipped review copy contains about 1,206.7 km of linework across 2,480 parts and 135,156 vertices. **This is not a coastline-length estimate.** It includes man-made objects, SPOR, approximate/apparent linework, and user-added connections. Do not dissolve or treat all seven source features as one boundary.

The layer exposes only `OBJECTID`, `F_NAME`, and shape length. It does not expose project source ID, T-sheet identifier, survey date, or an attribute that can crosswalk these records to FL1808A, FL1808C, or FL2317. It is therefore a historical comparison layer, not a substitute for those project-specific vectors.

## NOAA MHHW screening line

Florida DEP layer 40 is NOAA's predicted Mean Higher High Water extent derived from tidal and elevation data. NOAA describes it as a screening-level tool.

Two source records intersected the review extent and were retrieved. The clipped geometry contains about 2,779.7 km of linework across 13,314 parts and 342,477 vertices. This reflects an extensive network of predicted tidal-water extents inside the rectangular review window, not a shoreline-length estimate.

MHHW is not MHW. The MHHW line is not a surveyed shoreline, not a direct observation, and not a legal or navigation boundary. It remains a separate comparison layer and must never be merged with the historic MHW composite.

## Persisted research files

- `data/spatial/research/noaa_composite_shoreline_mhw_biscayne.geojson`: clipped MHW-context source features, with source OBJECTID and layer ID attached.
- `data/spatial/research/noaa_mhhw_screening_line_biscayne.geojson`: clipped MHHW screening features, separately identified.
- `data/spatial/research/noaa-shoreline-comparison-audit.json`: query extent, layer provenance, counts, and limitations.
- `data/spatial/research/noaa_composite_shoreline_mhw_metadata.json`: ArcGIS layer metadata.
- `data/spatial/research/noaa_mhhw_screening_line_metadata.json`: ArcGIS layer metadata.

The original un-clipped source records are retained in the workflow artifact rather than committed to the repository.

## Project-specific NOAA shoreline candidates still pending

The next source acquisition remains the actual project vectors:

- **FL1808C-TB-N:** Rickenbacker Island to Snapper Creek Canal, imagery/lidar dates 2018-07-26 to 2019-04-13.
- **FL1808A-TB-N:** Fender Point to Card Sound, imagery/lidar dates 2018-07-26 to 2019-04-16.
- **FL2317-CS-N:** Port of Miami, imagery date 2023-10-21, reported horizontal accuracy 1.2 m at 95% confidence.

NOAA InPort records link these projects to the Shoreline Data Explorer for vector downloads:

- FL1808C: https://www.fisheries.noaa.gov/inport/item/73241
- FL1808A: https://www.fisheries.noaa.gov/inport/item/74866
- FL2317: https://www.fisheries.noaa.gov/inport/item/76789

The project-specific MHW and MLLW linework must be retrieved and retained as separate datums. Their source metadata, survey dates, geographic-cell coverage, and seam/topology behavior must be checked before using them to reconcile Biscayne Bay, inlets, or harbor shorelines.

## Rejected service candidate

A hosted NOAA CUSP FeatureServer copy returned no features for the South Florida query extent and declared EPSG:6416 (NAD83(2011) / California zone 1, US survey feet) as its latest spatial reference. It was excluded from the South Florida extraction rather than force-reprojected or treated as authoritative.

The older NSDE GeoServer WFS endpoint documented in historical material returned HTTP 404 from the GitHub runner. The Florida DEP MapServer layers above were used only as comparison sources.

## Validation and artifact

- NOAA MHW/MHHW extraction, geometry validation, clipping, and research-branch persistence succeeded:
  https://github.com/markeetox/LUPITA/actions/runs/43356355642
- Artifact ID: `14005603545`, containing the original un-clipped source records, clipped outputs, layer metadata, and audit JSON.
- Focused shoreline tests: 3 passed.
- Repository-wide Python suite on the same code revision before the data-only persistence commit: 205 passed, 54 warnings:
  https://github.com/markeetox/LUPITA/actions/runs/43356355591

## Guardrails

- The query rectangle is a review window, not the bay boundary.
- Historic T-sheet shoreline is not necessarily current.
- Apparent, approximate, SPOR, man-made, and user-added linework remain distinguishable.
- MHW and MHHW remain separate products.
- Neither comparison layer proves habitat, salinity, flow, ecological connectivity, fish movement, or fish presence.
- No Government Cut or Norris Cut channel boundary is inferred from these shorelines.
- No production scoring, weights, thresholds, species profile values, or API v1 behavior changed.
