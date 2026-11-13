# NOAA CMP project shoreline and FDEP overlay audit (November 2026)

## Scope and result

The official NOAA Shoreline Data Explorer project archives for FL1808A-TB-N, FL1808C-TB-N, and FL2317-CS-N were retrieved, ZIP-validated, converted to GeoJSON, and persisted on this research branch.

The raw project ZIPs are retained under `data/spatial/research/noaa_cmp/source/`. Derived WGS84 GeoJSON and feature-class subsets are under `data/spatial/research/noaa_cmp/geojson/`. The audit summary is `data/spatial/research/noaa_cmp/noaa_cmp_project_geometry_audit.json`.

Source coordinate reference is NAD83 (EPSG:4269 per NOAA InPort metadata). The output GeoJSON is transformed to EPSG:4326. All source attributes, feature IDs, source dates, horizontal accuracy fields, source IDs, and class/attribute fields are retained with LUPITA provenance properties.

## Project extraction inventory

| NOAA project | Line features | Point features | Natural MHW features | MLLW depth-contour features |
|---|---:|---:|---:|---:|
| FL1808A-TB-N | 680 | 38 | 58 | 118 |
| FL1808C-TB-N | 969 | 215 | 70 | 54 |
| FL2317-CS-N | 19 | 0 | 0 | 0 |

Project source records:

- FL1808A: https://www.fisheries.noaa.gov/inport/item/74866
- FL1808C: https://www.fisheries.noaa.gov/inport/item/73241
- FL2317: https://www.fisheries.noaa.gov/inport/item/76789

### FL1808A-TB-N

- Survey/image source dates in project metadata: 2018-07-26 to 2019-04-16.
- All 58 Natural.Mean High Water features are dated 2018-07-26 and carry feature horizontal accuracy 2.3 m.
- MHW feature line length: 39.440 km.
- 118 Depth Contour features carry `INFORM=MLLW`, feature horizontal accuracy 3.0 m, and total 13.989 km of linework.

### FL1808C-TB-N

- Survey/image source dates in project metadata: 2018-07-26 to 2019-04-13.
- 70 Natural.Mean High Water features total 18.029 km.
- 65 MHW features are dated 2018-07-26 with 2.3 m horizontal accuracy.
- Five MHW features are dated 2019-04-12/13 with 1.3 m horizontal accuracy.
- 54 Depth Contour features carry `INFORM=MLLW`, feature horizontal accuracy 3.0 m, and total 11.830 km of linework.

### FL2317-CS-N

- Port of Miami project imagery date: 2023-10-21.
- All 19 line features carry 1.2 m horizontal accuracy.
- Four features have `CLASS=SHORELINE`, but they are man-made shoreline features: three Man-made.Bulkhead Or Sea Wall and one Man-made.Wharf Or Quay.
- Remaining records are fenders, piers, floating piers, a building, and cartographic/source limits.
- No Natural.Mean High Water shoreline features or MLLW depth contours were present.

FL2317 is useful recent port-structure context around the Government Cut vicinity. It is not a natural shoreline source and does not provide a Government Cut channel centerline or controlling-depth boundary.

## Datum and feature-class guardrails

- The Natural.Mean High Water subset is selected only when `CLASS=SHORELINE` and `ATTRIBUTE=Natural.Mean High Water`.
- The MLLW subset is selected only when `CLASS=CONTOUR`, `ATTRIBUTE=Depth Contour`, and `INFORM=MLLW`.
- The MLLW features are depth-contour linework referenced to MLLW. The source attribute tables contain no numeric contour-depth value. They are not MLLW shoreline boundaries and cannot be used as numeric bathymetry.
- Apparent mangrove shoreline, mangrove extent, man-made shoreline structures, alongshore features, transportation, obstructions, and cartographic limits remain in the full source linework. They are not merged into the Natural.Mean High Water subset.
- MHW and MLLW remain separate reference concepts. No datum conversion or synthetic shoreline was created.

## MHW line topology review

Topology metrics were computed in EPSG:26917 using exact geometric union and endpoint counts. No snapping, gap bridging, or forced joining was performed.

| Metric | FL1808A | FL1808C |
|---|---:|---:|
| MHW source features | 58 | 70 |
| Components after exact union | 51 | 69 |
| Open endpoint coordinates | 64 | 128 |
| Shared endpoint coordinates | 26 | 6 |
| Branch endpoint coordinates | 0 | 0 |
| Sum of source feature length | 39.440 km | 18.029 km |
| Exact union length | 39.440 km | 18.029 km |
| Measured overlap length | 0 km | 0 km |

The nearest separation between the two retrieved project MHW linework unions is 17.691 km. These are distinct project areas. This measured separation is not proof of missing shoreline data; do not bridge it.

The MLLW depth-contour linework is similarly segmented:
- FL1808A: 118 features, 117 exact-union components, 102 open endpoint coordinates, 67 shared endpoint coordinates.
- FL1808C: 54 features, 53 exact-union components, 78 open endpoint coordinates, 15 shared endpoint coordinates.

Open endpoints are reported as source geometry characteristics, not automatically classified as defects. The source products may intentionally contain separate shoreline and contour segments.

## Overlay against NOAA ENC and FDEP preserve geometry

FDEP preserve geometries were retrieved separately and persisted under `data/spatial/research/noaa_cmp/overlay/`:

- Biscayne Bay Aquatic Preserve, OBJECTID 43, 64,607.580491 acres.
- Biscayne Bay-Cape Florida to Monroe County Line, OBJECTID 25, 4,163.903858 acres.

The two statutory preserve designations remain separate. FDEP's GIS boundaries are approximate management mapping, not legal survey or enforcement geometry.

### NOAA charted Biscayne Bay area vs FDEP preserve OBJECTID 43

| Measure | Area |
|---|---:|
| NOAA ENC Biscayne Bay union (37 source polygons) | 512.865 km² |
| FDEP Biscayne Bay preserve OBJECTID 43 | 261.411 km² |
| Intersection | 180.106 km² |
| NOAA union area within FDEP preserve | 35.12% |
| FDEP preserve area within NOAA union | 68.90% |

These are overlay statistics between different source concepts, not boundary accuracy scores. The NOAA charted union still has two connected components, including a very small isolated chart fragment. No gap was bridged.

### MHW line length inside the comparison polygons

| Project | Total MHW linework | Inside NOAA charted Bay polygons | Inside FDEP Biscayne Bay preserve |
|---|---:|---:|---:|
| FL1808A | 39.440 km | 12.315 km (31.23%) | 6.251 km (15.85%) |
| FL1808C | 18.029 km | 2.624 km (14.55%) | 7.392 km (41.00%) |
| FL2317 | 0 km | No Natural MHW features | No Natural MHW features |

These percentages describe how much project MHW line length falls inside each polygon. They do not measure shoreline accuracy. The charted water polygons and management preserve polygons are not interchangeable shoreline boundaries; portions of the MHW linework outside either polygon are not automatically errors.

The separate Cape Florida-to-Monroe County Line preserve (OBJECTID 25) did not contain any of the FL1808A/FL1808C MHW line length in this overlay.

## Government Cut status

FL2317 is the newest of the retrieved projects and its geographic extent includes the Port of Miami/Government Cut vicinity. However, it provides port structures and man-made shoreline features, not a natural MHW shoreline or channel centerline. The exact Government Cut channel geometry remains unresolved.

The three NOAA Harbour fairway polygons and 44 maintained-channel records already extracted remain broader Miami Harbor Channel project context, not a direct Government Cut subgeometry.

## Validation

- NOAA NSDE project archive download, ZIP validation, CRS conversion, GeoJSON extraction, and research-branch persistence succeeded:
  https://github.com/markeetox/LUPITA/actions/runs/43358686177
- NOAA CMP/FDEP overlay, geometry retrieval, and research-branch persistence succeeded:
  https://github.com/markeetox/LUPITA/actions/runs/43359017113
- Repository Python suite: 208 passed, 60 warnings:
  https://github.com/markeetox/LUPITA/actions/runs/43359016919
- NOAA hydrography and NOAA shoreline comparison workflows also passed on the same research head.

## Guardrails and next review

- These files remain research data on the PR #70 branch; they are not production scoring inputs.
- No final ecological or statutory Biscayne Bay boundary is declared.
- No MHW/MLLW conflation, numeric depth inference, or shoreline continuity assumption is made.
- No fish presence, habitat suitability, or species occupancy is inferred from shoreline geometry.
- Next spatial review should inspect MHW segment placement against source imagery/metadata, chart-cell seams, local benthic habitat and bathymetry, and the unresolved Government Cut/Norris Cut channel crosswalk before assigning feature IDs to species contexts.
