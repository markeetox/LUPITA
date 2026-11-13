# South Florida spatial context schema v1

## Purpose

LUPITA needs to represent coastal environments as spatial entities, not only as named point sites. A bay, subregion, inlet, pass, channel, flat, nearshore zone, reef tract, and monitoring station have different geometry and environmental support.

This first implementation is a **descriptive geographic foundation only**. It does not feed the production scoring pipeline, change species thresholds, or alter API v1 output.

## Files

- `data/spatial/schema-v1.json`: JSON Schema for the version 1 catalog.
- `data/spatial/catalog.json`: initial South Florida catalog.
- `pipeline/spatial_context.py`: dependency-free structural and GeoJSON validation.
- `tests/test_spatial_context.py`: regression tests for IDs, geometry, provenance shape, and relationships.

The catalog uses WGS84 longitude/latitude coordinates (`EPSG:4326`). GeoJSON positions are stored as `[longitude, latitude]`.

## Feature types

| Feature type | Intended geometry | Meaning |
| --- | --- | --- |
| `bay` | Polygon or MultiPolygon | Named coastal waterbody |
| `bay_subregion` | Polygon or MultiPolygon | A bounded sub-area of a bay |
| `inlet`, `pass` | LineString or MultiLineString | Tidal connection between waterbodies |
| `channel` | LineString or Polygon | Channel corridor or mapped channel area |
| `flat` | Polygon or MultiPolygon | Shallow flat habitat area |
| `nearshore_zone` | Polygon or MultiPolygon | Coastal transition area |
| `reef`, `reef_tract` | Polygon or MultiPolygon | Reef feature or larger reef context |
| `monitoring_station` | Point | Observation location, never a habitat polygon |

Geometry types are validated for GeoJSON structure and coordinate ranges. Feature-type-specific geometry restrictions will be tightened only when the source inventory establishes the authoritative geometry conventions for each class.

## Identity, hierarchy, and connectivity

Every feature has a stable lowercase ID, a type, region ID, geometry status, and provenance. Relationships are explicit:

- `part_of`: a subregion or feature belongs to a larger context.
- `connects_to`: an inlet or pass links named waterbodies.
- `overlaps`: two mapped contexts overlap.
- `near`: proximity context, not a topological connection.

Relationships must resolve to existing feature IDs. Names alone never imply connectivity.

## Geometry and unknown states

A feature may temporarily have `geometry: null` only when its `geometry_status` is `pending_authoritative_geometry` or `not_applicable`. This means its boundary is not ready for spatial analysis. It does **not** mean the environment is absent.

The initial Biscayne Bay record reserves a stable identity but deliberately has no polygon yet. We will select and document an authoritative boundary before creating subregions or using point-in-polygon membership. The entire bay must not be treated as one homogeneous habitat.

Two monitoring-station records are included because their locations and sensor depths are documented in the temperature-source audit:

- USGS CREST Brewster Reef logger: 13 ft deployment depth (3.9624 m), reef-fixed logger.
- FWC-FWRI FLKEYS Array LKA57: 23 m sensor depth, reported by SECOORA ERDDAP as z = -23 m in a positive-up convention.

A monitoring station is not a fish-presence observation, and its temperature is not automatically representative of nearby flats, channels, or reef-bottom habitat.

## Species profile integration

Species profiles use an additive `habitat_contexts` section. Each context describes a species' ecological association with one or more feature types and a habitat role. Context records carry evidence references, evidence status, and a local-validation state.

The initial Bonefish and Permit entries are descriptive-only. They do not activate scoring factors, alter `site_kinds`, or change the current model.

Evidence status is intentionally conservative:

- `supported_general_association`: supported by cited ecological evidence, but not necessarily validated for all South Florida sites.
- `candidate_association`: plausible association requiring additional local evidence.
- `local_validation_required`: explicit validation state, not a claim of absence.

## Environmental support

Future observations must retain their actual spatial, vertical, and temporal support. For example:

- Daily satellite foundation SST is a surface product.
- In-situ station temperature is tied to the station coordinates and sensor depth.
- Salinity, tides, currents, bathymetry, benthic habitat, and closures have their own geometry, time coverage, resolution, and missingness.

Do not substitute offshore satellite SST for shallow-bay or bottom temperature without a validated transformation and appropriate evidence.

## Next implementation steps

1. Inventory authoritative Biscayne Bay, bay-subregion, inlet/pass, channel, flat, and reef geometries.
2. Add selected geometries with source version/date, CRS, native resolution, and processing history.
3. Add explicit bay membership and inlet connectivity relationships.
4. Extend validators to enforce geometry-type conventions and relationship semantics after source selection.
5. Add source coverage and spatial/vertical/temporal support metadata for environmental observations.
6. Build candidate habitat-context matching in shadow mode; do not change production scoring until independently validated.


## Initial authoritative source inventory

The following sources are candidates for geometry and habitat layers. They are not interchangeable, and each must be clipped, versioned, and assessed for coverage before being used.

| Source | Potential use | Important limitation |
| --- | --- | --- |
| [Florida Statutes §258.397](https://www.flsenate.gov/Laws/Statutes/2026/258.397) | Legal description of the Biscayne Bay Aquatic Preserve boundary | This is a legal preserve boundary, not automatically the ecological shoreline or a suitable bay-subregion partition. It includes Card Sound and excludes submerged lands conveyed for Biscayne National Park. Do not silently label it as the complete bay polygon. |
| [FWC Unified Reef Map v2.2](https://myfwc.com/research/gis/fisheries/unified-reef-map/) | Benthic habitat polygons and monitoring context | The detailed Biscayne Bay/National Park layers include historical mapping clipped to the park boundary. They are valuable local habitat evidence but do not cover the entire bay as one uniform dataset. |
| [FWC Seagrass Statewide, layer 15](https://gis.myfwc.com/hosting/rest/services/Open_Data/Seagrass_Statewide/MapServer/15) | Continuous and patchy seagrass polygons | A statewide compilation from multiple source agencies, dates, scales, and methods. Not all areas are mapped; not suitable for treating unmapped cells as seagrass absence or for unqualified time-series comparisons. |
| [FWC Tidal Flats, layer 21](https://gis.myfwc.com/hosting/rest/services/Open_Data/Tidal_Flats/MapServer/21) | Unvegetated tidal-flat polygons | Compiled from best available source mapping and NWI inputs. Source dates and mapping scales must be retained. |
| [FWC SIMM reports](https://myfwc.com/research/habitat/seagrasses/simm/simm-reports/) | Regional seagrass mapping and monitoring context, including Biscayne Bay | Reports and map vintages are region-specific; inspect each underlying source and publication date. |
| [Miami-Dade DERM Benthic Habitat Monitoring Program](https://data.florida-seacar.org/programs/details/4018) | Local seagrass/benthic monitoring observations | Monitoring/quadrat data are not automatically continuous habitat polygons; retain station, quadrat, sampling date, and method. |

### Source-selection rule

Use a legal boundary only for the legal context it actually represents. Use habitat polygons for the habitat classes and mapped dates they actually support. Preserve original source geometry, CRS, source date, mapping method, and coverage. Do not fill mapping gaps by drawing plausible-looking polygons.

The next geometry pass should compare the statutory preserve boundary with the FWC/NPS Biscayne Bay benthic mapping footprints and select a defensible waterbody boundary or explicitly represent separate legal/ecological extents. Only then should bay subregions, flats, and inlet relationships be materialized in the catalog.
