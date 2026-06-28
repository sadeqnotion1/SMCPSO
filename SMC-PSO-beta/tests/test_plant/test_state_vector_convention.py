#======================================================================================
#=================== tests/test_plant/test_state_vector_convention.py ==================
#======================================================================================
"""Guard test that PINS the canonical state-vector convention (M4 / Trap A).

If someone changes the canonical layout or breaks the adapters, this test fails
loudly instead of letting a silent ordering bug into the controller<->plant path.
"""
import numpy as np
import pytest

from src.plant.state_convention import (
    STATE_DIM,
    STATE_LAYOUT,
    grouped_to_interleaved,
    interleaved_to_grouped,
)


def test_canonical_layout_is_grouped():
    assert STATE_DIM == 6
    assert STATE_LAYOUT == (
        "x",
        "theta1",
        "theta2",
        "x_dot",
        "theta1_dot",
        "theta2_dot",
    )


def test_interleaved_to_grouped_mapping():
    # interleaved: [x, x_dot, theta1, theta1_dot, theta2, theta2_dot]
    s = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
    g = interleaved_to_grouped(s)
    # grouped: [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]
    assert np.allclose(g, [0.0, 2.0, 4.0, 1.0, 3.0, 5.0])


def test_adapters_are_inverses():
    s = np.array([1.1, -2.2, 3.3, -4.4, 5.5, -6.6])
    assert np.allclose(grouped_to_interleaved(interleaved_to_grouped(s)), s)
    assert np.allclose(interleaved_to_grouped(grouped_to_interleaved(s)), s)


def test_batched_states_supported():
    s = np.arange(12.0).reshape(2, 6)
    g = interleaved_to_grouped(s)
    assert g.shape == (2, 6)
    assert np.allclose(grouped_to_interleaved(g), s)


@pytest.mark.parametrize("bad", [np.zeros(5), np.zeros(7), np.zeros((3, 4))])
def test_wrong_dimension_raises(bad):
    with pytest.raises(ValueError):
        interleaved_to_grouped(bad)
