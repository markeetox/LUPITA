# NOAA CMP MHW topology audit (November 2026)

## Purpose and method

This research-only audit compares NOAA Coastal Mapping Program (CMP) mean-high-water (MHW) line features from four project extracts. All distances are measured after transforming WGS84 coordinates to NAD83 / UTM zone 17N (EPSG:26917). The audit counts components using exact shared endpoint coordinates and measures pairwise line geometry and endpoint distances. It does not snap, bridge, dissolve, or infer missing shoreline.

Inputs are persisted under `data/spatial/research/noaa_cmp/geojson/`; the reusable implementation is `scripts/audit_noaa_cmp_mhw_topology.py`. The machine-readable output is generated at `artifacts/noaa-cmp-mhw-topology-audit.json`.

## Project-level results

| NOAA project | MHW features | Exact-endpoint components | MHW line length |
|---|---:|---:|---:|
| `FL1603A-CM-N` | 11 | 11 | 3.006 km |
| `FL1808A-TB-N` | 58 | 51 | 39.440 km |
| `FL1808C-TB-N` | 70 | 69 | 18.029 km |
| `FL2317-CS-N` | 0 | 0 | 0 km |

FL1603A-CM-N contains 11 `Natural.Mean High Water` features within its 78-line source layer. Its other features include apparent mangrove, mangrove extent, piers, jetties, shoreline/alongshore boundary, and other structures. They remain separate classes. The survey project polygon is approximately 10.233 km²; all 3.006 km of extracted MHW linework lies inside it, with the nearest MHW line 187.18 m from the project polygon boundary. This is a project extent, not a Biscayne Bay boundary.

FL1808A-TB-N (GC12021) has 58 MHW features forming 51 exact-endpoint components. FL1808C-TB-N (GC12023) has 70 MHW features forming 69 components. FL2317-CS-N (GC12001) has no `Natural.Mean High Water` features in the downloaded project extract; its 19 line features are mostly piers, fenders, wharves, and related man-made features. Its absence of MHW features must not be interpreted as absence of shoreline.

## Cross-project seam findings

| Project pair | Minimum line geometry distance | Minimum endpoint distance | Closest feature IDs (geometry / endpoints) |
|---|---:|---:|---|
| `FL1603A-CM-N ↔ FL1808A-TB-N` | 0.00 m | 0.18 m | [1442038, 2077580] / [1442040, 2077583] |
| `FL1603A-CM-N ↔ FL1808C-TB-N` | 21,793.35 m | 21,825.45 m | [1442033, 1983664] / [1442033, 1983664] |
| `FL1808A-TB-N ↔ FL1808C-TB-N` | 17,690.77 m | 17,690.77 m | [2077140, 1983664] / [2077140, 1983664] |
| `FL1603A-CM-N ↔ FL2317-CS-N` | Not comparable | Not comparable | No MHW features in one project |
| `FL1808A-TB-N ↔ FL2317-CS-N` | Not comparable | Not comparable | No MHW features in one project |
| `FL1808C-TB-N ↔ FL2317-CS-N` | Not comparable | Not comparable | No MHW features in one project |

### Interpretation

- **GC11552 / FL1603A-CM-N to GC12021 / FL1808A-TB-N:** the nearest MHW geometries touch/intersect (0.00 m minimum geometry distance). Their nearest endpoints are 0.18 m apart (feature IDs 1442040 and 2077583). This is a promising local tie-in candidate, but it is not yet an accepted seam: source dates differ (2017 vs. 2018/2019), and the closest geometry pair and closest endpoint pair are not the same pair. Review the local feature geometry and source metadata before any conflation.
- **GC12021 / FL1808A-TB-N to GC12023 / FL1808C-TB-N:** the closest MHW line geometries and endpoints are 17,690.77 m apart (feature IDs 2077140 and 1983664). This is a substantial separation in the extracted MHW coverage. It is a **dataset coverage gap**, not proof that the physical shoreline or a water connection is absent. Do not draw a connector across it.
- **GC11552 to GC12023:** the nearest MHW geometry distance is 21,793.35 m and nearest endpoint distance is 21,825.45 m. These projects are not adjacent in this extract.
- **GC12001 / FL2317-CS-N:** no MHW linework was supplied, so it cannot be used to establish a shoreline seam with GC12023 despite its geographic proximity.

## Decisions

1. Keep each NOAA CMP project and source feature ID distinct in the research catalog.
2. Mark the FL1603A-CM-N / FL1808A-TB-N contact as a **candidate local seam for manual review**, not a verified merged shoreline.
3. Mark the GC12021 / GC12023 separation as an **uncovered interval in the extracted MHW datasets**. Do not bridge or interpolate it.
4. Do not use FL2317-CS-N as shoreline evidence until a separate authoritative shoreline source is found for that area.
5. Keep MHW, mangrove extent, apparent mangrove, depth contours, piers, jetties, and other structures as distinct feature classes.
6. Continue using NOAA ENC named-water geometry and FDEP preserve geometry as separate contextual layers; neither is a substitute for a complete ecological or statutory bay boundary.

## Limitations

- Exact endpoint matching is strict coordinate topology. Near matches are measured but never snapped.
- The distance between two extracted line sets describes their source coverage, not the distance between physical coastlines or channels in the real world.
- MHW linework is not a bathymetric channel centerline and does not prove tidal exchange, fish passage, habitat, or navigation safety.
- NOAA CMP project survey dates and accuracies vary by feature and source. Preserve feature-level metadata.
- No production scoring, species profiles, API contracts, or production spatial layers were changed.

## Next GIS milestone

Acquire and validate authoritative shoreline / hydrographic coverage for the uncovered GC12021-to-GC12023 interval, then inspect actual inlet and channel geometries against NOAA ENC and other authoritative hydrography. Only after those source checks should the team define candidate subregions, flats, channels, and inlet connections.
