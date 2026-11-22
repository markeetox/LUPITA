import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_node(script: str) -> None:
    subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )


def test_api_v1_species_detail_normalizes_into_map_spots():
    run_node(r"""
const assert = require("node:assert/strict");
const adapter = require("./web/lupita-data-adapter.js");
const detail = {
  id: "spanish-mackerel",
  name: "Spanish mackerel",
  today: {
    status: "ok",
    areas: [{
      id: "spanish-mackerel-1",
      title: "Government Cut (inlet)",
      score: 0.91,
      confidence: "Low",
      confidence_basis: ["limited_model_inputs"],
      coords: [-80.135, 25.767],
      zone: { type: "Polygon", coordinates: [[[-80.1, 25.7], [-80.2, 25.7], [-80.1, 25.8], [-80.1, 25.7]]] },
      reasons: [{ tag: "measured", text: "Buoy temperature observation." }],
      details: [{ label: "Water temp", value: "25.7 C" }],
      factor_diagnostics: [{ param: "sst_c", value_status: "sourced" }]
    }]
  }
};
const normalized = adapter.normalizeSpeciesDetail(detail);
assert.equal(normalized.status, "ok");
assert.equal(normalized.areas.length, 1);
const spot = normalized.areas[0];
assert.equal(spot.species, "spanish-mackerel");
assert.equal(spot.title, "Government Cut (inlet)");
assert.equal(spot.score, 0.91);
assert.deepEqual(spot.reasons, [["measured", "Buoy temperature observation."]]);
assert.deepEqual(spot.location, [["Water temp", "25.7 C"]]);
assert.equal(spot.ring.length, 4);
assert.equal(spot.api_v1, true);
""")

def test_area_without_valid_coordinates_is_not_mapped():
    run_node(r"""
const assert = require("node:assert/strict");
const adapter = require("./web/lupita-data-adapter.js");
const normalized = adapter.normalizeSpeciesDetail({
  id: "test-fish",
  today: { status: "ok", areas: [{ id: "bad", score: 0.9, coords: [null, 25] }] }
});
assert.equal(normalized.areas.length, 0);
""")

def test_opportunity_ranking_is_species_scoped_and_score_then_distance():
    run_node(r"""
const assert = require("node:assert/strict");
const adapter = require("./web/lupita-data-adapter.js");
const spots = [
  { id: "far-high", species: "a", score: 0.9, coords: [-80.5, 25.5] },
  { id: "near-high", species: "a", score: 0.9, coords: [-80.1, 25.1] },
  { id: "near-low", species: "a", score: 0.7, coords: [-80.0, 25.0] },
  { id: "other", species: "b", score: 1.0, coords: [-80.0, 25.0] }
];
const groups = adapter.rankOpportunities(spots, ["a"], { lat: 25, lng: -80 }, 2);
assert.equal(groups.length, 1);
assert.deepEqual(groups[0].spots.map(spot => spot.id), ["near-high", "far-high"]);
assert.ok(groups[0].spots[0].distance_km < groups[0].spots[1].distance_km);
""")
