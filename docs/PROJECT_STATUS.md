# LUPITA project status

**Last reviewed:** 2026-11-13  
**Production branch:** `main`  
**Consolidation staging branch:** `integration/main-consolidation`  
**Active GIS research branch:** `research/biscayne-noaa-enc-hydrography`

## Executive status

LUPITA is being consolidated around one authoritative application branch: `main`. The temporary `integration/main-consolidation` branch is a pre-production staging area only. The `data` branch is reserved for generated application exports and is excluded from code consolidation. GIS research remains separate from production scoring until reviewed and promoted.

PRs #66, #68, and #69 have been squash-merged into `integration/main-consolidation`. The 85 unique/updated paths from PR #70 have also been imported into staging as a consolidated tree commit, removing its stacked dependency. Original PRs #70 and #71 are closed as superseded. Consolidated PR #72 targets `main`; its Python suite, species validator, and focused Biscayne workflow all pass. Only the Vercel preview status is failing due to an external 24-hour deployment rate limit.

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
- The workflow runs from `main`, executes tests, catalog generation, and the prediction pipeline, then exports app-facing JSON to the `data` branch.
- The optional checkout of the previous `data` publication is only a last-known-good export fallback; it is not required for prediction generation. The intended contract is that `main` can run without `data` and export to it when available.
- The README's prediction, species, bite-timing, boat-condition, closures, and API sections describe the production pipeline. Changes to those processes must be reflected here and in the README.
- Spatial research must not be described as affecting fish predictions until it is deliberately integrated, tested, and promoted.

## Open review dependencies

| Pull request | Purpose | Base | State |
|---|---|---|---|
| [#70](https://github.com/markeetox/LUPITA/pull/70) | NOAA hydrography and Biscayne inlet review | imported into integration staging | Closed, superseded |
| [#69](https://github.com/markeetox/LUPITA/pull/69) | Biscayne GIS geometry foundation | integration staging | Merged |
| [#68](https://github.com/markeetox/LUPITA/pull/68) | South Florida spatial-context schema and species habitat contexts | integration staging | Merged |
| [#66](https://github.com/markeetox/LUPITA/pull/66) | South Florida in-situ temperature audit | integration staging | Merged |
| [#71](https://github.com/markeetox/LUPITA/pull/71) | Prediction reliability changes | already present in current codebase | Closed, superseded |
| [#72](https://github.com/markeetox/LUPITA/pull/72) | Single-main runtime and data-export consolidation | `main` | Open, checks passed |

PR #70 originated as a stacked branch on #69. Its resulting file tree is now in the staging branch without the old commit chain. PR #71 was reviewed against the current tree and its meaningful API/confidence changes were already present, so it was closed without importing stale versions of core files.

## Known limitations and blockers

1. A defensible continuous ecological Biscayne Bay boundary has not been established.
2. NOAA ENC, FDEP preserve, benthic habitat, MHW, MHHW, and MLLW products represent different concepts and datums; they must not be blended as interchangeable geometry.
3. The 17.691 km nearest separation between FL1808A and FL1808C MHW linework is a measured separation between project vectors, not proof of a missing coastline or permission to interpolate.
4. Government Cut requires an exact source-feature crosswalk.
5. Candidate subregions, flats, channels, and inlet connections must retain confidence/provenance and must not be promoted based on proximity alone.
6. The Jewfish Creek shared-boundary test exposed projection-induced false zero measurements. The implementation now evaluates shared-edge topology in source coordinates and projects the resulting line only for metric length. The focused GitHub workflow now passes all 4 topology tests; the synthetic shared edge measures 100.763 m.
7. Five expensive FWC/NOAA source-acquisition workflows and the in-situ temperature extraction workflow are manual-only so PR synchronization cannot repeatedly trigger downloads and branch-write loops.
8. The first consolidated species-validator run failed during test collection because the full suite now includes GIS tests but the workflow installed only production requirements. Added `requirements-research.txt` and wired it into all full-suite CI workflows; rerun is pending.

## Next implementation milestones

1. Merge consolidated PR #72 into `main`; the required Python, species, and focused GIS checks pass.
2. Retain `data` as the generated export branch. Its current 725 paths are JSON/API/PNG assets only, with no source-code files.
3. Archive or delete superseded feature/fix/research branches after the merge; keep only `main` and `data` as active branches.
4. Verify the next scheduled `main` pipeline run exports successfully to `data`.
5. Continue Biscayne boundary and inlet reconciliation as research within `main`, without promoting unverified geometry.

## Validation policy

See [Biscayne research pipeline policy](biscayne-research-pipeline-policy-2026-11.md). In short: syntax and focused tests first; source-specific geometry QA only when inputs or logic change; full-suite validation at broad integration and pre-merge checkpoints. Do not rerun every NOAA extraction for an unrelated code or documentation change.
