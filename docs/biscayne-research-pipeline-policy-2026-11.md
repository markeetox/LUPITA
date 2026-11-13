# Biscayne Bay research pipeline and source-freeze policy

## Decision

The research branch will stop treating every analysis milestone as a reason to rerun every extraction workflow. Persisted source datasets are versioned research snapshots. Analysis is rerun only when an input, script, or documented QA condition requires it.

The source inventory is maintained in `data/spatial/research/biscayne-source-manifest.json`.

## Operating rules

1. **Acquire once, preserve provenance.** Keep original source geometry, attributes, chart cells, survey dates, coordinate reference systems, and source metadata.
2. **Reuse frozen inputs.** Do not redownload a source merely because another workflow ran.
3. **Target validation.** Run focused unit tests and the directly affected spatial audit after a code or input change. Run the full Python suite only for broad integration milestones or before merging.
4. **Separate extraction from interpretation.** A successful download is not a verified ecological feature. Keep source geometry, derived overlays, and interpretation records distinct.
5. **No production promotion.** All current work remains on the research branch and draft PR. No production scoring, thresholds, API behavior, or species files are changed by this policy.

## Current evidence already persisted

- NOAA ENC named-water source polygons, topology audit, and hydrography index.
- NOAA NGS CMP project MHW geometry for FL1808A and FL1808C, plus separate MLLW depth-contour subsets and topology/overlay audits.
- Separate FDEP preserve geometries for OBJECTID 43 and 25.
- Individually preserved FWC/NPS tidal-flat source patches.
- NOAA composite MHW and predicted MHHW screening comparison geometry, kept separate.
- Miami-Dade bridge inventory and NOAA ENC bridge/landmark candidates.

These datasets are not interchangeable. Their distinct roles and limitations are recorded in the source manifest.

## Next research milestone: landmark and feature reconciliation

The next task is not another extraction batch. It is to resolve the source-backed locations and spatial context of the published ecological segmentation landmarks:

- Dumfoundling Bay
- Rickenbacker Causeway
- Featherbed Bank / Black Point
- Card Sound / Jewfish Creek

For each landmark, record the source, geometry type, source date, accuracy where available, and whether the location is a point, line, named-water polygon, or descriptive place reference. Compare existing NOAA chart contexts, shoreline vectors, bridge records, and benthic patches against those landmarks.

A landmark is not automatically a cross-bay boundary. Do not create North/Central/South polygons until authoritative or defensible geometry supports the separating line and its uncertainty is documented.

## Validation policy

| Change | Required validation |
|---|---|
| Documentation or manifest only | JSON parse/schema sanity if applicable; no GIS extraction |
| Catalog relationship edit | Catalog schema and relationship integrity tests |
| Geometry transformation | Focused geometry tests plus source-specific topology/overlay audit |
| Source refresh | Source metadata, geometry validity, CRS, feature-count, and change comparison |
| Broad integration milestone | Full Python suite once, after targeted checks |

## Explicitly out of scope

- Re-running all NOAA workflows on every commit.
- Treating a green workflow as proof of ecological correctness.
- Snapping or bridging source geometries to force continuity.
- Inferring inlet, tidal-exchange, or fish-passage connectivity from proximity.
- Changing production species scores or model weights.
