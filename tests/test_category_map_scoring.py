import numpy as np

from pipeline.scoring import factor_score


def test_grid_category_factor_uses_map_without_preferred_values():
    grid = np.array([["reef", "wreck", "sand", None]], dtype=object)
    factor = {
        "param": "structure_type",
        "kind": "category",
        "map": {"reef": 1.0, "wreck": 0.4},
    }

    result = factor_score(factor, {"structure_type": grid}, {})

    assert result is not None
    np.testing.assert_allclose(result[0, :3], [1.0, 0.4, 0.0])
    assert np.isnan(result[0, 3])


def test_grid_category_factor_without_map_still_uses_preferred_values():
    grid = np.array([["reef", "sand", None]], dtype=object)
    factor = {
        "param": "structure_type",
        "kind": "category",
        "preferred": ["reef"],
    }

    result = factor_score(factor, {"structure_type": grid}, {})

    assert result is not None
    np.testing.assert_allclose(result[0, :2], [1.0, 0.0])
    assert np.isnan(result[0, 2])
