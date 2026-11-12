# Benthic Habitat Data Layer

Status: first ingestion layer. It is available to the pipeline but is not yet used to change species scores.

## Source

LUPITA uses the Florida Fish and Wildlife Conservation Commission (FWC) / Fish and Wildlife Research Institute (FWRI) Unified Reef Map v2.2, Unified Classification Level 0.

- Service: [FWC Unified Reef Map v2.2 Level 0](https://gis.myfwc.com/hosting/rest/services/Projects_FWC/UnifiedReefMapProject_v2_2/MapServer/10)
- Project overview: [FWC Unified Reef Map](https://myfwc.com/research/gis/fisheries/unified-reef-map/)
- Release: January 2025.
- Coverage: Martin County through the Florida Keys and Dry Tortugas.
- The map integrates partner datasets with different source dates, scales, and mapping methods. A single release date does not mean every polygon was surveyed in January 2025.

## Normalized broad classes

| FWC Unified Class Level 0 | LUPITA category |
|---|---|
| Coral Reef and Hardbottom | `hard_bottom` |
| Seagrass | `seagrass` |
| Unconsolidated Sediment | `soft_bottom` |
| Artificial | `artificial` |
| Dredged/Excavated | `dredged` |

The layer preserves fractional polygon cover on the SST grid. It also tracks total mapped coverage and unknown source classes.

## Critical interpretation rules

- A zero value in a habitat category outside mapped coverage means **unknown**, not confirmed absence.
- `mapped_cover` records where the source contains mapped polygons, including classes LUPITA does not yet normalize.
- Level 0 is deliberately broad. It cannot distinguish sand from mud, continuous from patchy seagrass, or specific reef forms.
- The Unified Reef Map is not a real-time environmental layer. Source dates vary by partner and region.
- The new layer is kept separate from the existing reef/wreck `structure_type` grid. It does not replace that layer.
- This ingestion step does not change any species profile, score, gate, weight, or recommendation.

## Next integration step

Use these habitat layers to build evidence-backed site attributes and habitat suitability inputs. Before activation, validate source coverage, coordinate alignment, resolution, and the meaning of missing polygons for each region. The site-kind field (inlet, cut, flat, channel bridge) must remain distinct from ecological habitat features.
