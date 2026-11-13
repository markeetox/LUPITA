# LUPITA project status

**Last reviewed:** 2026-11-13  
**Active research branch:** `research/biscayne-noaa-enc-hydrography`  
**Branch head at initial record:** `85afcff7cf4ee18e926a8accd29946b600018be0`  
**Production branch:** `main`

## Executive status

LUPITA's production prediction pipeline and map client remain separate from the current Biscayne Bay spatial-research work. The active research branch extends the GIS evidence base; it does not change production species scoring, thresholds, weights, or API behavior.

The current research branch is the head of [PR #70](https://github.com/markeetox/LUPITA/pull/70), which targets [PR #69's research branch](https://github.com/markeetox/LUPITA/pull/69), rather than targeting `main` directly. PR #69 is itself open against `main`. This is a stacked pull-request sequence. Review and merge dependencies in order; do not merge the child branch directly into production.

## Current workstreams

### 1. Biscayne Bay geographic foundation

**Status:** research evidence assembled; final ecological boundary and subregion geometry not approved.

Persisted research includes:

- NOAA ENC named-water features, original source attributes, and topology audits.
- NOAA NGS Coastal Mapping Program project vectors for FL1808A and FL1808C, with MHW shoreline and MLLW depth-contour subsets kept distinct.
- NOAA composite MHW and predicted MHHW screening layers, kept separate.
- FDEP Aquatic Preserve geometries and spatial overlays.
- FWC/NPS benthic habitat patches and supporting GIS inventories.
- Miami-Dade bridge inventory and NOAA ENC bridge/landmark context.
- Candidate landmark references for Dumfoundling Bay, Rickenbacker Causeway, Featherbed Bank, Black Point, Card Sound, and Jewfish Creek.

Key persisted locations:

- `data/spatial/noaa-biscayne-named-water-areas.geojson`
- `data/spatial/noaa-biscayne-named-water-topology-audit.json`
- `data/spatial/noaa-biscayne-hydrography-index.json`
- `data/spatial/feature-catalog.json`
- `data/spatial/research/noaa_cmp/`
- `data/spatial/research/noaa_enc/`
- `data/spatial/research/transportation/`
- `data/spatial/research/biscayne-landmark-candidates.json`
- `data/spatial/research/biscayne-source-manifest.json`

### 2. Landmark and inlet reconciliation

**Status:** active review; source extraction is not equivalent to verified channel geometry.

- Bear Cut and Norris Cut have directly named NOAA ENC water polygons in the curated set. These are charted named-water areas, not surveyed channel centerlines.
- Card Sound has six exact NOAA ENC OBJECTIDs identified for detailed source-feature review.
- Jewfish Creek has two named-water polygons identified for geometry and depth-context analysis. NOAA CO-OPS station 8723613 remains a tidal benchmark reference, not a creek centerline or mouth.
- Rickenbacker Causeway has a named land polygon plus separate bridge and coastline context. Bridge proximity does not establish a crossing or water connection.
- Government Cut remains unresolved. Broader Miami Harbor Channel fairway and maintained-channel features are not an acceptable substitute for an exact Government Cut crosswalk.

No inferred inlet connections, snapped seams, or synthetic channel centerlines are approved.

### 3. Production fishing prediction system

**Status:** existing production pipeline remains the live app data path.

- The scheduled workflow is `.github/workflows/pipeline.yml`, hourly at 10 minutes past the hour UTC.
- The workflow runs tests, catalog generation, and the prediction pipeline, then publishes app-facing JSON to the `data` branch.
- The README's prediction, species, bite-timing, boat-condition, closures, and API sections describe the production pipeline. Changes to those processes must be reflected here and in the README.
- Spatial research must not be described as affecting fish predictions until it is deliberately integrated, tested, and promoted.

## Open review dependencies

| Pull request | Purpose | Base | State |
|---|---|---|---|
| [#70](https://github.com/markeetox/LUPITA/pull/70) | NOAA hydrography and Biscayne inlet review | `research/biscayne-bay-gis-foundation` | Open |
| [#69](https://github.com/markeetox/LUPITA/pull/69) | Biscayne GIS geometry foundation | `main` | Open |
| [#68](https://github.com/markeetox/LUPITA/pull/68) | South Florida spatial-context schema and species habitat contexts | `main` | Open |
| [#66](https://github.com/markeetox/LUPITA/pull/66) | South Florida in-situ temperature audit | `main` | Open |

PR #70 is stacked on the #69 branch. The PR list and branch heads must be rechecked before each merge decision.

## Known limitations and blockers

1. A defensible continuous ecological Biscayne Bay boundary has not been established.
2. NOAA ENC, FDEP preserve, benthic habitat, MHW, MHHW, and MLLW products represent different concepts and datums; they must not be blended as interchangeable geometry.
3. The 17.691 km nearest separation between FL1808A and FL1808C MHW linework is a measured separation between project vectors, not proof of a missing coastline or permission to interpolate.
4. Government Cut requires an exact source-feature crosswalk.
5. Candidate subregions, flats, channels, and inlet connections must retain confidence/provenance and must not be promoted based on proximity alone.
6. The latest topology workflow failure exposed a missing syntax preflight and a malformed Jewfish Creek expression/test block. The first correction was incomplete and failed the compile preflight before extraction. A follow-up correction removes the remaining extra parenthesis; current-head focused validation is still required.

## Next implementation milestones

1. Stabilize and validate the focused landmark extraction/topology workflow.
2. Review its generated Card Sound, Jewfish Creek, and Rickenbacker evidence artifact.
3. Reconcile authoritative landmark references and candidate subregions without inventing separator lines.
4. Build a source-backed spatial entity model that can later link named places, habitat patches, depth context, and species profiles.
5. Define explicit promotion criteria from research artifacts to production map/prediction inputs.
6. Evaluate the prediction system separately against observed catches or other independent evidence before making accuracy claims.

## Validation policy

See [Biscayne research pipeline policy](biscayne-research-pipeline-policy-2026-11.md). In short: syntax and focused tests first; source-specific geometry QA only when inputs or logic change; full-suite validation at broad integration and pre-merge checkpoints. Do not rerun every NOAA extraction for an unrelated code or documentation change.
