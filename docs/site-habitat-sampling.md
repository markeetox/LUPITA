# Site-Level Habitat Sampling

The FWC Unified Reef Map v2.2 Level 0 layer is a regional benthic habitat map. LUPITA uses it to add descriptive habitat context to configured site predictions.

## Sampling method

- Source queries are restricted to a Florida reef-tract bounding box: latitude 24-28° N, longitude 83-79° W.
- Each configured site is sampled inside its existing approximate `radius_km` buffer.
- The local sample grid is approximately 250 metres. Polygon cover is supersampled within each cell.
- The returned categories are broad Level 0 classes: seagrass, coral reef and hardbottom, unconsolidated sediment, artificial, and dredged/excavated.
- Category percentages describe mapped polygon cover inside the approximate site buffer. They are not fish suitability weights.

## Unknown is not absent

The FWC map does not cover every habitat type or every configured fishing location. If no polygons intersect a site buffer, LUPITA reports the habitat as unknown. It must not infer that seagrass, reef, or other habitat is absent.

The total mapped coverage is reported separately from classified category coverage. Unknown classes remain part of mapped coverage even when LUPITA cannot normalize them.

## Prediction boundary

Site habitat summaries are added to the prediction output as descriptive context only. They do not currently change:
- species scores or rankings;
- confidence labels;
- active factors or factor weights;
- site eligibility or filtering;
- bite timing.

The current site scores remain based on their existing factors. Habitat-based scoring requires species-specific evidence, regional applicability, missing-data rules, and separate tests before activation.

## Source limitations

The Unified Reef Map v2.2 was released in January 2025, but its component maps have different source dates, mapping scales, and survey methods. Level 0 is intentionally broad. It cannot distinguish sand from mud or continuous from patchy seagrass. A site-buffer summary also smooths over fine-scale habitat mosaics.

Source: [FWC Unified Reef Map](https://myfwc.com/research/gis/fisheries/unified-reef-map/).
