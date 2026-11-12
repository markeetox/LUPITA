# South Florida Bonefish and Permit Habitat Audit

**Snapshot:** 2026-11-12 18:17:34 UTC  
**Production run:** [Pull ocean data #189](https://github.com/markeetox/LUPITA/actions/runs/43278160498)  
**Species records:** 15 Bonefish areas + 15 Permit areas  
**Distinct site locations:** 15 (the same site set is currently reused by both profiles)

## Executive findings

- FWC Unified Reef Map v2.2 ingestion returned **49,903 polygon features**, all with geometry.
- The 15 named site buffers average **76.7% mapped coverage**. Nine are at least 80% mapped; five are below 60%.
- Coverage gaps are **unknown**, not evidence that a habitat is absent.
- Bonefish flat sites show strong mapped seagrass cover, which is directionally consistent with shallow-flat foraging evidence. It does not establish fish presence, feeding activity, or a calibrated suitability score.
- Permit's current sites represent inshore flats, cuts, and inlets. They do not adequately represent the deeper 15–40 m reef-tract habitat documented in the lower-Keys telemetry study.
- The FWC Level 0 classification is broad. It does not distinguish sand from mud, patch from continuous seagrass, or reef types at the resolution needed for a species model.
- NOAA chlorophyll and ETOPO bathymetry failed in this production run. No conclusions below rely on those layers.
- Existing Bonefish and Permit scores remain single-factor SST outputs. They are not the multi-factor models proposed by the pilot framework.

## Site-level habitat coverage

The percentages below are shares of the entire site buffer. The mapped-coverage column is the fraction of the buffer intersecting mapped FWC polygons. Category percentages therefore do not have to sum to 100%; the remainder can include unmapped area or mapped classes not represented by the five displayed fishing-habitat categories.

| Site | Type | Mapped coverage | Mapped category cover |
|---|---|---:|---|
| Government Cut | Inlet | 93% | Soft bottom 57%, hard bottom 19%, seagrass 11% |
| Haulover Inlet | Inlet | 91% | Soft bottom 78%, seagrass 14%, hard bottom 7% |
| Port Everglades | Inlet | 48% | Hard bottom 63%, soft bottom 21%, dredged 8% |
| Hillsboro Inlet | Inlet | 46% | Soft bottom 74%, hard bottom 21%, dredged 5% |
| Boca Raton Inlet | Inlet | 63% | Soft bottom 80%, hard bottom 20% |
| Boynton Inlet | Inlet | 33% | Soft bottom 92%, dredged 5%, hard bottom 3% |
| Lake Worth Inlet | Inlet | 53% | Soft bottom 80%, artificial 10%, hard bottom 7% |
| Bear Cut | Inlet | 90% | Seagrass 53%, soft bottom 47%, hard bottom 1% |
| Norris Cut | Cut | 91% | Seagrass 76%, soft bottom 12%, hard bottom 12% |
| Biscayne Channel (Stiltsville) | Cut | 93% | Seagrass 98%, soft bottom 2% |
| Safety Valve Flats | Flat | 92% | Seagrass 82%, soft bottom 18% |
| Soldier Key Flats | Flat | 100% | Seagrass 100% |
| Featherbed Bank | Flat | 100% | Seagrass 100% |
| Caesar Creek | Cut | 59% | Seagrass 96%, soft bottom 3%, hard bottom 2% |
| Broad Creek | Cut | 98% | Seagrass 99%, hard bottom 1% |

**Coverage triage**
- Highest priority for map-gap review: Boynton Inlet (33%), Hillsboro Inlet (46%), Port Everglades (48%), Lake Worth Inlet (53%), and Caesar Creek (59%).
- These sites should not be removed or down-ranked solely because mapped coverage is low.
- A site with 100% mapped coverage is not automatically biologically suitable. Coverage measures map availability, not ecological quality.

## Bonefish evidence comparison

The pilot framework describes Bonefish (*Albula vulpes*) as a shallow-water flats forager with a distinct offshore spawning migration. Northern Florida Keys acoustic telemetry supports use of shallow foraging habitats and suggests deeper channels can provide refuge from rapid temperature changes. The study's limited observed site fidelity does not justify assuming fixed home ranges.

**What the current map supports**
- Safety Valve Flats, Soldier Key Flats, and Featherbed Bank show 82–100% seagrass cover and 92–100% mapped coverage. These are strong descriptive examples of mapped shallow-flat habitat.
- Biscayne Channel (Stiltsville), Norris Cut, Caesar Creek, and Broad Creek also show substantial seagrass cover, but these are cuts/channels rather than interchangeable flat habitat.
- The northern inlet sites are predominantly soft bottom or hard bottom. Their mapped labels alone do not tell us whether those sediments are suitable feeding grounds.

**What remains unmeasured**
- The current Level 0 map does not resolve sand versus mud or seagrass density/patch structure.
- The current site-kind labels do not measure actual channel depth, refuge depth, or access between flats and channels.
- Offshore spawning habitat and seasonal migration are not represented by a flat-habitat percentage.
- The generic SST-only Bonefish profile must not be treated as validated adult thermal preference evidence.

**Pilot implication:** define a shallow-flat foraging habitat dimension and a separate channel/refuge and spawning-movement context. Do not collapse them into one score.

## Permit evidence comparison

The pilot framework cites lower-Florida-Keys acoustic telemetry of 45 Permit (*Trachinotus falcatus*). Tagged fish used both nearshore flats shallower than 3 m and Florida Reef Tract habitat around 15–40 m; approximately 75% were detected in both habitat types. Reef occupancy peaked March–September, especially April–May. The study interprets flats primarily as foraging habitat and reefs as spawning habitat.

**What the current map supports**
- The same shallow flats and inshore cuts can be retained as candidate foraging-context sites.
- Mapped hard-bottom at some inlet sites is descriptive context, not proof that the buffer intersects a spawning reef.
- Seagrass and soft-bottom cover can describe flats, but cannot represent the deeper reef occupancy dimension.

**Critical sampling gap**
- The current 15 sites contain no explicit offshore reef-tract station set designed around the 15–40 m habitat described in the telemetry study.
- The current broad FWC Level 0 categories do not identify reef depth or spawning aggregation use.
- The ETOPO layer failed in this run, so we currently lack a verified depth surface for separating shallow flats from deeper reef habitat.

**Pilot implication:** keep the flats-foraging dimension separate from reef occupancy/spawning context. Add a distinct reef-tract site sample set and a depth source with documented coverage before evaluating a Permit multi-factor model.

## Source and model limitations

### FWC habitat ingestion

Source: FWC Unified Reef Map v2.2, MapServer Layer 10, Level 0 class field `FIRST_ClassLv0`. The source release is January 2025, while component source dates vary.

Production diagnostics:
- 49,903 total features
- 49,903 geometry features
- 23,412 Coral Reef and Hardbottom
- 12,509 Seagrass
- 9,394 Unconsolidated Sediment
- 942 Artificial
- 70 Dredged/Excavated
- 892 Land, 1,957 Mangrove, and 727 Not Classified features were present but are not among the five displayed fishing-habitat categories

Source: https://myfwc.com/research/gis/fisheries/unified-reef-map/

### Missing environmental inputs

The same production run recorded HTTP 404 errors for:
- NOAA-20 VIIRS daily chlorophyll: `nesdisVHNnoaa20chlaDaily`
- NOAA NCEI ETOPO 2022 15-arc-second relief: `ETOPO_2022_v1_15s`

These are ingestion failures, not evidence that the datasets are unavailable. NOAA's CoastWatch ERDDAP metadata confirms both dataset IDs exist:
- https://coastwatch.pfeg.noaa.gov/erddap/info/nesdisVHNnoaa20chlaDaily/index.html
- https://coastwatch.pfeg.noaa.gov/erddap/griddap/ETOPO_2022_v1_15s.html

### Existing scores are not validated models

The production Bonefish and Permit records currently report:
- `active_factor_count = 1`
- only SST is active
- confidence is Low
- scores are 1.0 at the listed sites

The displayed environmental coverage of 100% only means the sole active SST factor had an input. It does not mean the species model has complete biological or environmental coverage. The 1.0 values must not be interpreted as probability of presence, catch probability, or validated habitat suitability.

## Recommended model-development gates

1. Restore chlorophyll and bathymetry ingestion, then inspect source timestamps, valid fractions, spatial coverage, and missing-data behavior.
2. Add or validate a Permit reef-tract site sample set. Keep the existing flats/inlet sites as a separate habitat role.
3. Define candidate dimensions separately:
   - Bonefish: shallow-flat foraging habitat; channel/refuge context; seasonal spawning movement; current environmental conditions.
   - Permit: flats-foraging habitat; reef-tract occupancy/spawning habitat; seasonal reef occupancy; connectivity between flats and reefs; current environmental conditions.
4. Attach an evidence record to each factor: source, geography, life stage, season, measurement scale, evidence class, and known limitations.
5. Implement shadow-mode candidate outputs and diagnostics only. Do not change production scores, weights, gates, ranking, or eligibility until independent validation is complete.

## Research references

- Bonefish northern Florida Keys telemetry: https://doi.org/10.3354/meps291237
- NOAA-hosted Bahamas bonefish home-range/spawning linkage research: https://www.fisheries.noaa.gov/resource/peer-reviewed-research/bonefish-albula-vulpes-home-range-spawning-site-linkages-support
- Permit flats-to-reef telemetry and seasonal occupancy: https://pubmed.ncbi.nlm.nih.gov/31823365/
- Florida Museum Permit profile: https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/permit/
- FWC Unified Reef Map: https://myfwc.com/research/gis/fisheries/unified-reef-map/
- NOAA ETOPO 2022 metadata: https://www.ncei.noaa.gov/metadata/geoportal/rest/metadata/item/gov.noaa.ngdc.mgg.dem%3Aetopo_2022/html
