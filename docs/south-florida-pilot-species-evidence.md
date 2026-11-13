# South Florida pilot species evidence notes: Bonefish and Permit

Status: research documentation for the South Florida pilot. This document does not validate the current scoring factors and does not change production scoring behavior.

## Why these profile edits were made

The previous Bonefish and Permit records used generic NOAA homepage links to label numeric SST ranges as sourced. Those links did not establish the specific temperature thresholds. The profiles also contained near-identical generic diet, behavior, spawning, overwintering, and timing descriptions.

The revised records distinguish source-supported habitat observations from hypotheses and unresolved parameters. Their existing active scoring configuration is deliberately preserved for compatibility while the evidence is investigated.

## Evidence matrix

| Species | Claim | Evidence class | Geographic / temporal scope | What it supports | What it does not support |
|---|---|---|---|---|---|
| Bonefish (*Albula vulpes*) | Shallow foraging habitat and use of deeper channels | Peer-reviewed acoustic telemetry | Northern Florida Keys | Distinct shallow foraging and deeper channel/refuge context | Numeric SST preference, universal site fidelity, or catch probability |
| Bonefish | Linkage between home ranges and spawning sites | NOAA-hosted peer-reviewed research | Bahamas study system | Seasonal offshore spawning movement is relevant to the life-history model | Exact South Florida migration timing, routes, or population-wide thresholds |
| Permit (*Trachinotus falcatus*) | Use of shallow flats and deeper reef-tract habitat | Peer-reviewed acoustic telemetry | Lower Florida Keys | Both shallow flats (<3 m) and deeper reef habitat (~15–40 m) belong in the pilot's habitat representation | Every mapped hard-bottom polygon being spawning habitat |
| Permit | Seasonal reef occupancy | Same lower Florida Keys telemetry study | Study period and study area | Reef occupancy peaked March–September, especially April–May, in that study | A universal calendar rule for all South Florida Permit or a feeding-activity probability |
| Permit | General species identification and natural history | Florida Museum species profile | Florida species account | General biological context | Site-specific occupancy, numeric model weights, or local thermal preference |

## Explicitly unsupported model values

The legacy SST bounds remain in both files solely to avoid changing the existing production model while this research is completed.

| Species | Current allowed range (°C) | Current ideal range (°C) | Weight | State |
|---|---:|---:|---:|---|
| Bonefish | 20–35 | 25–31 | 0.35 | Active, provisional, required gate |
| Permit | 20–34 | 24–30 | 0.35 | Active, provisional, required gate |

These values are not established by the telemetry sources above. They must not be described as validated thermal preferences, physiological tolerance limits, or probabilities. The factor source arrays are intentionally empty until a direct source for the numeric thresholds is identified. The factor notes explain the limitation.

## Timing

Both profiles retain their existing timing maps and weights for backward compatibility. Their status remains angler_lore, and the source arrays are empty because the previous generic agency homepage did not support the numeric light, tide, or front scores.

These values are hypotheses, not calibrated feeding probabilities. A future calibration dataset should include timestamped observations, fishing effort, location, gear/method where available, and unsuccessful trips. Catch-only records without effort information would introduce substantial sampling bias.

## Permit sampling requirement

The current shared site set is dominated by inshore flats, cuts, and inlets. It does not adequately represent the deeper reef-tract habitat documented in the telemetry study.

Add a distinct reef-tract validation sample set. Do not replace the shallow-flat sample set, and do not classify reef habitat from broad hard-bottom labels alone. Before using bathymetry for this purpose, document source resolution, vertical datum, coverage, and freshness.

## Non-goals and safeguards

- No changes to active factors, weights, numeric ranges, ideal ranges, gates, or required flags.
- No changes to timing numeric maps or timing weights.
- No production scoring formula or ranking changes.
- No claim that suitable habitat means fish are present.
- No claim that environmental suitability means fish are feeding.
- Missing or unmapped habitat remains unknown, not absent.
- Candidate multi-dimension outputs remain shadow-only until independently validated.

## References

- Bonefish northern Florida Keys telemetry: https://doi.org/10.3354/meps291237
- NOAA-hosted Bahamas bonefish home-range/spawning linkage research: https://www.fisheries.noaa.gov/resource/peer-reviewed-research/bonefish-albula-vulpes-home-range-spawning-site-linkages-support
- Permit flats-to-reef telemetry and seasonal occupancy: https://pubmed.ncbi.nlm.nih.gov/31823365/
- Florida Museum Permit profile: https://www.floridamuseum.ufl.edu/discover-fish/species-profiles/permit/
