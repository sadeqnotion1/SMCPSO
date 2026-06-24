#======================================================================================
#======================= tests/test_utils/test_control_types.py =======================
#======================================================================================

"""Tests for utils.control.types.control_outputs NamedTuples (M3 slice 1)."""

from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from utils.control.types.control_outputs import (
    ClassicalSMCOutput,
    AdaptiveSMCOutput,
    STAOutput,
    HybridSTAOutput,
)


def test_classical_fields_and_tuple_compat():
    out = ClassicalSMCOutput(u=1.5, state=(), history={})
    assert out.u == 1.5
    assert out.state == ()
    assert out.history == {}
    # backward-compatible tuple unpacking
    u, state, history = out
    assert u == 1.5
    assert isinstance(out, tuple)
    assert out[0] == 1.5


def test_adaptive_exposes_sigma():
    out = AdaptiveSMCOutput(u=2.0, state=(0.1,), history={"k": [1]}, sigma=-0.3)
    assert out.sigma == -0.3
    assert out.state == (0.1,)
    assert len(out) == 4


def test_sta_exposes_sigma():
    out = STAOutput(u=0.0, state=(0.0, 0.0), history={}, sigma=0.0)
    assert out.sigma == 0.0
    u, state, history, sigma = out
    assert state == (0.0, 0.0)


def test_hybrid_state_triplet():
    out = HybridSTAOutput(u=-1.0, state=(1.0, 2.0, 3.0), history={}, sigma=0.5)
    assert out.state == (1.0, 2.0, 3.0)
    assert out.sigma == 0.5
    assert out[1] == (1.0, 2.0, 3.0)
