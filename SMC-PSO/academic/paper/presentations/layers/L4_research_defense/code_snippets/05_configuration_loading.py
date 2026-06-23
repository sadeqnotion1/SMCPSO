# ============================================================================
# Configuration Loading: Type-Safe YAML Parsing
# ============================================================================
# Demonstrates Pydantic-validated configuration loading from YAML

from pydantic import BaseModel, Field, validator
from typing import List, Optional
import yaml


class PhysicsConfig(BaseModel):
    """Physics parameters for double-inverted pendulum."""
    m0: float = Field(1.0, description="Cart mass (kg)")
    m1: float = Field(0.1, description="Link 1 mass (kg)")
    m2: float = Field(0.1, description="Link 2 mass (kg)")
    l1: float = Field(0.5, description="Link 1 length (m)")
    l2: float = Field(0.5, description="Link 2 length (m)")
    g: float = Field(9.81, description="Gravitational acceleration (m/s^2)")

    @validator('m0', 'm1', 'm2', 'l1', 'l2', 'g')
    def must_be_positive(cls, v, field):
        if v <= 0:
            raise ValueError(f"{field.name} must be positive, got {v}")
        return v


class ControllerConfig(BaseModel):
    """Controller parameters."""
    type: str = Field(..., description="Controller type (classical_smc, sta_smc, etc.)")
    max_force: float = Field(20.0, description="Maximum control force (N)")
    gains: List[float] = Field(..., description="Controller gain vector")

    @validator('gains')
    def validate_gains_length(cls, v, values):
        if 'type' in values:
            if values['type'] == 'classical_smc' and len(v) != 6:
                raise ValueError("classical_smc requires 6 gains: [k1, k2, lambda1, lambda2, K, epsilon]")
        return v


class PSOConfig(BaseModel):
    """PSO optimization parameters."""
    n_particles: int = Field(30, description="Number of particles in swarm")
    n_iterations: int = Field(100, description="Number of optimization iterations")
    c1: float = Field(2.0, description="Cognitive parameter")
    c2: float = Field(2.0, description="Social parameter")
    w: float = Field(0.9, description="Inertia weight")

    @validator('n_particles', 'n_iterations')
    def must_be_positive_int(cls, v, field):
        if v <= 0:
            raise ValueError(f"{field.name} must be positive integer, got {v}")
        return v


class SimulationConfig(BaseModel):
    """Simulation parameters."""
    dt: float = Field(0.01, description="Time step (s)")
    duration: float = Field(10.0, description="Simulation duration (s)")
    integrator: str = Field('RK45', description="ODE integrator method")

    @validator('dt', 'duration')
    def must_be_positive_float(cls, v, field):
        if v <= 0:
            raise ValueError(f"{field.name} must be positive, got {v}")
        return v


class ProjectConfig(BaseModel):
    """Complete project configuration."""
    physics: PhysicsConfig
    controller: ControllerConfig
    pso: Optional[PSOConfig] = None
    simulation: SimulationConfig


def load_config(config_path: str) -> ProjectConfig:
    """
    Load and validate configuration from YAML file.

    Parameters:
        config_path: Path to config.yaml

    Returns:
        Validated ProjectConfig instance

    Raises:
        ValidationError: If configuration is invalid
    """
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)

    # Pydantic validates automatically
    config = ProjectConfig(**config_dict)

    print("[OK] Configuration loaded and validated successfully")
    print(f"Physics: m0={config.physics.m0} kg, m1={config.physics.m1} kg")
    print(f"Controller: {config.controller.type}, max_force={config.controller.max_force} N")
    print(f"Simulation: dt={config.simulation.dt} s, duration={config.simulation.duration} s")

    return config


# Example YAML structure
EXAMPLE_YAML = """
physics:
  m0: 1.0
  m1: 0.1
  m2: 0.1
  l1: 0.5
  l2: 0.5
  g: 9.81

controller:
  type: classical_smc
  max_force: 20.0
  gains: [10.0, 5.0, 8.0, 3.0, 15.0, 0.05]

pso:
  n_particles: 30
  n_iterations: 100
  c1: 2.0
  c2: 2.0
  w: 0.9

simulation:
  dt: 0.01
  duration: 10.0
  integrator: RK45
"""


# Example usage
if __name__ == "__main__":
    # Write example YAML
    with open('example_config.yaml', 'w') as f:
        f.write(EXAMPLE_YAML)

    # Load configuration
    config = load_config('example_config.yaml')

    # Access validated parameters
    print(f"\n[INFO] Accessing validated parameters:")
    print(f"Cart mass: {config.physics.m0} kg")
    print(f"Controller gains: {config.controller.gains}")
    print(f"PSO particles: {config.pso.n_particles if config.pso else 'N/A'}")
