# LUPITA Species Profile Validator

The validator is a read-only engineering audit of species profiles in data/species against the current scoring implementation and data/parameters.json.

## Run

```bash
python scripts/validate_species.py
```

The command writes reports/species-audit.json, reports/species-audit.md, and reports/species-audit.csv. Use --output-dir PATH to choose another destination.

## Checks

- Profile structure, identifiers, geographic bounds, factor definitions, weights, ranges, and timing configuration.
- Active-factor compatibility with the current grid and site scoring implementations.
- Registry status conflicts, category vocabulary mismatches, and provisional evidence.
- Whether the current pipeline can supply active factors, including conditional data inputs.
- Representation of six review dimensions: temperature, depth, structure, seasonality, tides, and light.

## Interpretation

- Passing schema checks does not establish scientific validity.
- A supported factor may still be unavailable during a particular data run.
- The biological-dimension count is a review aid, not a completeness score.
- Source metadata does not prove source credibility or correct interpretation.
- Prediction scores and confidence are not calibrated probabilities of fish presence.
- The tool never edits profiles, creates biological values, or invents sources.

The engine capability maps in pipeline/species_validator.py must be updated when pipeline/scoring.py, pipeline/sites.py, or pipeline/layers.py changes. The parameter registry alone is not proof that a factor is implemented.
