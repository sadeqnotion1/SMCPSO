#=====================================================================================
#=========================== src/optimization/__init__.py ============================
#=====================================================================================

"""Optimization package (beta).

Minimal, beta-native package surface. Exposes the PSO tuner ported in M6.
Additional optimizers and bridges are introduced in later slices.
"""

from __future__ import annotations

from .algorithms.pso_optimizer import PSOTuner

__all__ = ["PSOTuner"]
