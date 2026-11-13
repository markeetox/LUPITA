# NOAA ENC Causeway, Bridge, and Landmark Crosswalk Audit

**Generated:** 2026-11-13  
**Scope:** Research-only NOAA Harbour ENC extraction for the South Florida query extent  
**Workflow artifact:** `noaa-biscayne-hydrography-review` (artifact ID `14009922820`)  
**Query extent:** `[-80.55, 25.2, -80.05, 26.1]` (WGS84)

## Summary

The latest NOAA Harbour ENC extraction completed successfully and returned valid GeoJSON for the selected layers. The results are useful as landmark crosswalk evidence, but they do not provide a complete set of named cross-bay structures.

| Layer | NOAA layer ID | Features | Finding |
|---|---:|---:|---|
| Harbor.Causeway_line | 118 | 0 | No causeway line features returned in the query extent |
| Harbor.Bridge_line | 87 | 71 | Bridge geometries returned; most are unnamed |
| Harbor.Landmark_point | 26 | 49 | 48 unnamed; one named feature, Cape Florida Light |
| Harbor.Land_Area | 233 | 518 | Includes a named Rickenbacker Causeway land-area polygon |

The extraction summary reports no layer errors. An empty causeway-line result is a source-layer result, not evidence that a causeway is absent.

## Rickenbacker Causeway

The named `Rickenbacker Causeway` feature is in `Harbor.Land_Area`, not `Harbor.Causeway_line`:

- Source OBJECTID: `691847`
- Chart cell: `US5MIACB.000`
- Bounding box (WGS84): `[-80.200988, 25.745429, -80.1892736, 25.747347]`

This is a charted land-area polygon and can serve as a named landmark anchor for reviewing the published North/Central Biscayne Bay division. It is not a cross-bay ecological boundary line. The bridge-line extraction did not return an identified Rickenbacker bridge feature.

## Card Sound crossing candidates

Four unnamed fixed-bridge features cluster around the Card Sound crossing area:

| OBJECTID | Bounding box (WGS84) | Source |
|---:|---|---|
| 20577 | `[-80.385574, 25.292068, -80.380112, 25.29693]` | Chart 11463, 2003-04 |
| 20578 | `[-80.37268, 25.285029, -80.362802, 25.288915]` | Chart 11463, 2003-04 |
| 20579 | `[-80.388294, 25.298303, -80.385953, 25.303169]` | Chart 11463, 2003-04 |
| 20580 | `[-80.358911, 25.283319, -80.356186, 25.284038]` | Chart 11463, 2003-04 |

Their positions make them candidates for a Card Sound crossing crosswalk, but the ENC attributes do not name them. They must remain **unconfirmed bridge candidates** until independently matched to an authoritative named bridge/road source. Do not use these features to draw a boundary or infer water connectivity.

Two additional unnamed fixed-bridge features occur farther north in the southern query area:

- OBJECTID 20581, bbox `[-80.2619913, 25.346594, -80.2616764, 25.3466606]`
- OBJECTID 20582, bbox `[-80.262518, 25.327411, -80.262115, 25.32751]`

They are not assigned to Card Sound or another named crossing by proximity.

## Landmark points

The 49 extracted landmark points contain one named object: **Cape Florida Light**, OBJECTID 62971, at approximately `(-80.155861, 25.666638)`. The remaining 48 points are unnamed in the returned ENC attributes. No point directly identifies Black Point, Featherbed Bank, or the Rickenbacker Causeway.

## Implications for Biscayne Bay subregions

The literature-based subregion limits remain:

- North Biscayne Bay: Dumfoundling Bay to Rickenbacker Causeway.
- Central Biscayne Bay: Rickenbacker Causeway to Featherbed Bank / Black Point.
- South Biscayne Bay: Featherbed Bank / Black Point to Card Sound / Jewfish Creek.

The NOAA extraction adds a named Rickenbacker Causeway land-area anchor and a set of unnamed Card Sound-area bridge candidates. It does **not** establish cross-bay dividing lines at any of these limits. Featherbed Bank and Black Point remain separately supported by named-water/chart context and literature, not by this bridge/landmark layer extraction.

Keep all three subregion geometries null until cross-bay boundaries are digitized from defensible source geometry and independently reviewed. Do not snap bridge candidates, extend causeway polygons across water, or infer ecological boundaries from a nearby chart object.

## Reproducibility and guardrails

- Source service: NOAA ENC Harbour MapServer, layers 118, 87, 26, and 233.
- Extraction summary: `noaa_hydrography_summary.json` in the workflow artifact.
- Output CRS: EPSG:4326.
- The source is chart-derived. Preserve source chart/date metadata and do not treat it as a current navigation product.
- No production scoring, species profiles, thresholds, weights, or API behavior were changed.
