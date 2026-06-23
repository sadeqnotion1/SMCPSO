#======================================================================================#===================== src/controllers/factory/types.py ==============================#======================================================================================
"""
Type Definitions and Protocols for Controller Factory

Consolidates type definitions from core/protocols.py and factory_new/types.py
during Week 1 aggressive factory refactoring (18 files → 6 files).

Provides:
- Type aliases (StateVector, ControlOutput, GainsArray, etc.)
- Protocols (ControllerProtocol, ConfigurationProtocol, etc.)
- Exceptions (ConfigValueError)
- Enums (SMCType)
"""

# Standard library imports
from enum import Enum
from typing import Any, Dict, List, Protocol, TypeVar, Union

# Third-party imports
import numpy as np
from numpy.typing import NDArray

# =============================================================================
# TYPE ALIASES
# =============================================================================

# Type aliases for better type safety
StateVector = NDArray[np.float64]
ControlOutput = Union[float, NDArray[np.float64]]
GainsArray = Union[List[float], NDArray[np.float64]]
ConfigDict = Dict[str, Any]

# Generic type for controller instances
ControllerT = TypeVar('ControllerT')

# =============================================================================
# EXCEPTIONS
# =============================================================================

class ConfigValueError(ValueError):
    """Exception raised for invalid configuration values."""
    pass

# =============================================================================
# PROTOCOLS
# =============================================================================

class ControllerProtocol(Protocol):
    """Protocol defining the standard controller interface."""

    def compute_control(
        self,
        state: StateVector,
        last_control: float,
        history: ConfigDict
    ) -> ControlOutput:
        """Compute control output for given state."""
        ...

    def reset(self) -> None:
        """Reset controller internal state."""
        ...

    @property
    def gains(self) -> List[float]:
        """Return controller gains."""
        ...

    @property
    def max_force(self) -> float:
        """Return maximum force limit."""
        ...


class ConfigurationProtocol(Protocol):
    """Protocol for controller configuration objects."""

    @property
    def gains(self) -> List[float]:
        """Controller gains."""
        ...

    @property
    def max_force(self) -> float:
        """Maximum force limit."""
        ...

    @property
    def dt(self) -> float:
        """Time step."""
        ...


# =============================================================================
# ENUMS
# =============================================================================

class SMCType(Enum):
    """SMC Controller types enumeration."""
    CLASSICAL = "classical_smc"
    ADAPTIVE = "adaptive_smc"
    SUPER_TWISTING = "sta_smc"
    HYBRID = "hybrid_adaptive_sta_smc"


# =============================================================================
# CONFIGURATION CLASSES
# =============================================================================

class SMCConfig:
    """Configuration class for SMC controllers."""
    def __init__(self, gains: List[float], max_force: float = 150.0, dt: float = 0.001, **kwargs: Any) -> None:
        self.gains = gains
        self.max_force = max_force
        self.dt = dt
        for key, value in kwargs.items():
            setattr(self, key, value)
