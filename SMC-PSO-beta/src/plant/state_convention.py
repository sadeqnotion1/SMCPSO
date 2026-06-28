#======================================================================================
#============================= src/plant/state_convention.py ==========================
#======================================================================================
"""Canonical state-vector convention for dip-smc-pso (M4 / Trap A pin).

DECISION (see .agents/brain/STATE_VECTOR_CONVENTION.md):
The **GROUPED** ordering is canonical for the beta codebase, because the now-live
corrected plant physics (`physics_matrices.py`, wired in to resolve Finding #2)
operates in grouped order:

    CANONICAL (grouped):   [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]

The legacy controller code documented an INTERLEAVED order:

    legacy (interleaved):  [x, x_dot, theta1, theta1_dot, theta2, theta2_dot]

Any controller or legacy consumer that speaks interleaved MUST convert at the
plant boundary using the adapters below. This module is additive and depends on
nothing in the project, so it cannot break existing code.
"""
from __future__ import annotations

import numpy as np

# Canonical (grouped) component layout.
STATE_LAYOUT = ("x", "theta1", "theta2", "x_dot", "theta1_dot", "theta2_dot")
STATE_DIM = 6

# Canonical indices into a grouped state vector.
IDX_X, IDX_THETA1, IDX_THETA2, IDX_X_DOT, IDX_THETA1_DOT, IDX_THETA2_DOT = range(6)

# Permutations act on the LAST axis, so both a single (6,) state and a batched
# (..., 6) array of states are handled.
_INTERLEAVED_TO_GROUPED = (0, 2, 4, 1, 3, 5)
_GROUPED_TO_INTERLEAVED = (0, 3, 1, 4, 2, 5)


def _reorder(state, perm):
    arr = np.asarray(state, dtype=float)
    if arr.shape[-1] != STATE_DIM:
        raise ValueError(
            f"state must have last dimension {STATE_DIM}; got shape {arr.shape}"
        )
    return arr[..., list(perm)]


def interleaved_to_grouped(state):
    """Convert legacy interleaved order -> canonical grouped order.

    in :  [x, x_dot, theta1, theta1_dot, theta2, theta2_dot]
    out:  [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]
    """
    return _reorder(state, _INTERLEAVED_TO_GROUPED)


def grouped_to_interleaved(state):
    """Convert canonical grouped order -> legacy interleaved order.

    in :  [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]
    out:  [x, x_dot, theta1, theta1_dot, theta2, theta2_dot]
    """
    return _reorder(state, _GROUPED_TO_INTERLEAVED)


__all__ = [
    "STATE_LAYOUT",
    "STATE_DIM",
    "IDX_X",
    "IDX_THETA1",
    "IDX_THETA2",
    "IDX_X_DOT",
    "IDX_THETA1_DOT",
    "IDX_THETA2_DOT",
    "interleaved_to_grouped",
    "grouped_to_interleaved",
]
