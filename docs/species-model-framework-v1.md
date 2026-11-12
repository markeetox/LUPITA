# LUPITA Species Model Framework v1

Status: design proposal. This document does not change prediction behavior or species profiles.

## Why this change is needed

The species audit inspected 130 profiles. It found 127 profiles needing biological research or model rebuilding, including 125 classified as needing a model rebuild. Three profiles have structural errors. The current model also mixes several different questions into one score:

- Is this habitat suitable for the species?
- Is the species likely to be present in this region at this time of year?
- Do current environmental conditions suit it?
- Is this a favorable time for feeding activity?

Those are related, but they are not interchangeable. A fish can occupy suitable habitat while not being seasonally present, and it can be present without actively feeding.

The grid and site scorers should be treated as spatial execution methods, not as biological model types.

## 1. Four separate prediction dimensions

### A. Habitat suitability

Describes whether a location has the physical and ecological features the species uses.

Potential inputs:
- Habitat features: seagrass, mangrove edge, sand, mud, hard bottom, natural reef, artificial reef, wreck, channel edge, beach, estuary.
- Depth and bathymetry.
- Salinity regime, where measured or modeled.
- Site geomorphology and proximity to connected habitats.

This dimension changes slowly and should not be presented as a real-time feeding forecast.

### B. Seasonal presence and movement

Describes when a species is expected to occupy a region or move between habitats.

Potential inputs:
- Region-specific seasonal occupancy.
- Spawning and migration periods.
- Temperature trends and thresholds supported by movement studies.
- Freshwater flow, water level, and salinity changes where relevant.
- Life stage and size class.

A spawning aggregation model must not be treated as a general year-round habitat model.

### C. Current environmental suitability

Describes whether the current water conditions are favorable at the location.

Potential inputs:
- Sea-surface temperature and its gradient.
- Currents, convergence, and current boundaries.
- Chlorophyll and water-color boundaries.
- Depth, bottom type, and structure.
- Salinity, dissolved oxygen, and water clarity when dependable data becomes available.

Every input must carry its observation time, source, spatial resolution, and availability state.

### D. Feeding activity

Describes short-term changes in likely feeding activity, separately from where fish live.

Potential inputs:
- Light phase.
- Tide stage and current flow.
- Moon phase, only where supported for the species and region.
- Weather fronts and local conditions.

Angler-derived timing remains explicitly provisional. It must not silently become a biological fact because it has a tidy JSON object.

## 2. Do not collapse the four dimensions into one score yet

The first framework release should expose separate dimension scores and their supporting evidence.

Do not label any score as probability of fish presence or probability of catching a fish.

A combined ranking may be explored later, but only after calibration against independent observations such as catch logs with effort information, standardized surveys, or acoustic telemetry. Validation should include held-out periods and locations, not only the same observations used to tune the model.

Until then:
- Scores are normalized model-match indices.
- Confidence is a qualitative description of model and input limitations.
- Missing data is unknown, not neutral.
- A high environmental data coverage value does not mean the biology is well modeled.
- A gate is reserved for a well-supported exclusion condition, not a convenient way to force a score to zero.

## 3. Separate site kind from habitat features

This is a critical data-model correction.

The current site scorer returns the configured site kind as the value for the `structure_type` factor. These are different concepts.

- `site_kind` describes the geographic feature used to organize a fishing location: inlet, cut, flat, channel bridge, bay, or similar.
- `habitat_features` describes the ecological attributes present there: seagrass, mangrove edge, sand, mud, hard bottom, reef, wreck, oyster habitat, and similar.

For example, a flat can contain seagrass, sand, mud, or a mixture. Calling every flat the same structure type loses the information needed to distinguish habitat suitability.

Proposed site record:

```json
{
  "id": "safety-valve-flats",
  "name": "Safety Valve Flats",
  "kind": "flat",
  "habitat_features": [],
  "lat": 25.67,
  "lon": -80.165,
  "radius_km": 2.5,
  "region": "biscayne_bay",
  "evidence": []
}
```

The empty arrays are intentional. Habitat attributes must be populated from mapped or documented sources, not guessed from a place name.

A site may have multiple habitat features. Scoring must define whether the feature is present, absent, unknown, or represented by a measured proportion.

## 4. Evidence requirements for every factor

Each active factor must document:

| Field | Purpose |
|---|---|
| Parameter and scoring type | What is being measured and how it is scored |
| Weight | Relative contribution within its own prediction dimension |
| Active state | Whether the factor currently affects output |
| Evidence status | Sourced, partly sourced, provisional, estimated, or unsourced |
| Source references | Direct source links, not a generic agency homepage |
| Geographic scope | Where the evidence applies |
| Life stage | Juvenile, adult, or unspecified |
| Season or conditions | When the evidence applies |
| Value notes | What the source actually supports and what is inferred |
| Input requirements | Which live or static data layer supplies the value |
| Missing-data behavior | Whether the dimension is unavailable, partial, or safely evaluable |

Numeric ranges must identify whether they describe tolerance, observed occupancy, physiological limits, or an inferred preferred band. These are not synonyms.

Where studies disagree, preserve the disagreement and lower evidence confidence rather than averaging numbers into an invented consensus.

## 5. Reliability and output semantics

Keep the following independent:

1. **Environmental input coverage:** available active input weight divided by total active input weight for the evaluated location.
2. **Biological model scope:** the ecological dimensions represented by the model. This is a review aid, not a percentage or probability.
3. **Evidence support:** how much of the active model is backed by geographically and biologically applicable evidence.
4. **Confidence basis:** explicit reasons for a Low or Medium confidence label, such as limited active inputs, missing inputs, provisional factors, gap-filled layers, or a profile cap.

No High confidence label should be introduced until there is a defensible validation method.

Every dynamic input should expose:
- source or dataset identifier;
- observation timestamp;
- spatial resolution or station distance, where available;
- whether it is measured, modeled, static, or estimated;
- whether it was missing or gap-filled.

Do not invent universal freshness limits. Freshness thresholds should be defined per dataset based on its update cycle and intended use.

## 6. API compatibility

API v1 remains additive. Existing fields such as `score`, `confidence`, and `data_coverage` remain available for current clients.

New consumers should use the explicit metadata:
- `environmental_data_coverage`
- `active_factor_count`
- `confidence_basis`
- `data_quality.input_times`
- `data_quality.datasets`

A future API v2 may expose the four prediction dimensions explicitly. Do not repurpose the existing v1 `score` field to mean something different.

## 7. Pilot implementation order

1. Correct the site data model so `kind` and `habitat_features` are separate.
2. Define dimension-specific factor groups and data requirements.
3. Rebuild the pilot species profiles using evidence specific to the region and life stage.
4. Add regression tests for missing inputs, mixed habitat features, seasonal changes, and confidence explanations.
5. Compare outputs against independent observations where available.
6. Expand to additional species only after the pilot's assumptions and limitations are documented.

The initial pilot covers:
- Common snook: estuarine, structure-associated, seasonal movement.
- Atlantic tarpon: migratory inshore and coastal species with strong seasonal movement.
- Bonefish: shallow flats foraging habitat and offshore spawning migration.
- Permit: flats foraging connected to offshore reef spawning habitat.
- Mahi-mahi: offshore pelagic habitat, currents, fronts, and floating habitat.

## 8. Explicit non-goals

This framework does not:
- claim to predict exact catch locations;
- convert angler lore into scientific evidence;
- invent temperature, depth, salinity, or seasonal thresholds;
- assume a species is present because a habitat is suitable;
- change all 130 profiles in one bulk operation;
- change the live scoring formulas before the new dimensions are defined and tested.
