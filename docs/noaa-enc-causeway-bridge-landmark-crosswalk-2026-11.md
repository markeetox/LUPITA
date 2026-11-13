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

This is a charted land-area polygon and can serve as a named landmark anchor for reviewing the published North/Central Biscayne Bay division. It is not a cross-bay ecological boundary line.

An independent Miami-Dade County source confirms that the Rickenbacker Causeway is a 3.6-mile corridor containing 1.2 miles of bridge structures, with the Bear Cut Bridge at the eastern end: https://www.miamidade.gov/global/transportation/public-works/rickenbacker-causeway.page

Miami-Dade's Bear Cut Bridge project identifies Bridge No. 874544 and describes the bridge as part of County Road 913 / Rickenbacker Causeway: https://www.miamidade.gov/resources/transportation_publicworks/documents/bear-cut-bridge-fact-sheet.pdf

NOAA Coast Pilot 4 also describes the fixed span at Rickenbacker Causeway and the highway bridge over Bear Cut. These official sources establish the named structure crosswalk, but they do not supply a digitized bridge geometry in the extracted Harbour ENC bridge layer. The bridge-line extraction did not return an identified Rickenbacker bridge feature.

## Card Sound crossing candidates

Four unnamed fixed-bridge features cluster around the Card Sound crossing area:

| OBJECTID | Bounding box (WGS84) | Source |
|---:|---|---|
| 20577 | `[-80.385574, 25.292068, -80.380112, 25.29693]` | Chart 11463, 2003-04 |
| 20578 | `[-80.37268, 25.285029, -80.362802, 25.288915]` | Chart 11463, 2003-04 |
| 20579 | `[-80.388294, 25.298303, -80.385953, 25.303169]` | Chart 11463, 2003-04 |
| 20580 | `[-80.358911, 25.283319, -80.356186, 25.284038]` | Chart 11463, 2003-04 |

FDOT independently identifies the Card Sound Bridge as Bridge Identification Number **904990**, a high-level fixed bridge on CR 905A / Card Sound Road crossing the Atlantic Intracoastal Waterway: https://pdaexternal.fdot.gov/Pub/AdvertisementPublic/StreamExternalEDMSDocument?EdmsDocumentNumber=17977642

FDOT's current project page places the project between south of Milepost 5 / Mile Marker 4 and Milepost 6.242 / Mile Marker 5 at the Miami-Dade / Monroe County line: https://www.fdotmiamidade.com/project/329/453765-1-22-01

The NOAA bridge cluster is geographically consistent with the Card Sound crossing, but the ENC attributes do not name the four objects and this review has not compared them to an authoritative bridge centerline or surveyed structure footprint. Keep OBJECTIDs 20577, 20578, 20579, and 20580 as **candidate matches only**, not confirmed geometry for Bridge 904990. Do not use them to draw a bay boundary or infer water connectivity.

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

The NOAA extraction adds a named Rickenbacker Causeway land-area anchor and a set of unnamed Card Sound-area bridge candidates. Independent county and FDOT references identify the Rickenbacker/Bear Cut and Card Sound bridge structures. This does **not** establish cross-bay dividing lines at any of these limits. Featherbed Bank and Black Point remain separately supported by named-water/chart context and literature, not by this bridge/landmark layer extraction.

Keep all three subregion geometries null until cross-bay boundaries are digitized from defensible source geometry and independently reviewed. Do not snap bridge candidates, extend causeway polygons across water, or infer ecological boundaries from a nearby chart object.

## Reproducibility and guardrails

- Source service: NOAA ENC Harbour MapServer, layers 118, 87, 26, and 233.
- Extraction summary: `noaa_hydrography_summary.json` in the workflow artifact.
- Output CRS: EPSG:4326.
- The source is chart-derived. Preserve source chart/date metadata and do not treat it as a current navigation product.
- No production scoring, species profiles, thresholds, weights, or API behavior were changed.
