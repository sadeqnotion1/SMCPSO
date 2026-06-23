"""Minimal import test."""
print("Starting imports...")

print("1. Importing SuperTwistingSMC...")
from src.controllers.smc.sta_smc import SuperTwistingSMC  # noqa: E402
print("   Done")

print("2. Importing SimplifiedDIPDynamics...")
from src.plant.models.simplified.dynamics import SimplifiedDIPDynamics  # noqa: E402
print("   Done")

print("3. Importing SimplifiedDIPConfig...")
from src.plant.models.simplified.config import SimplifiedDIPConfig  # noqa: E402
print("   Done")

print("4. Creating config...")
config = SimplifiedDIPConfig.create_default()
print(f"   Config: {type(config)}")

print("5. Creating dynamics...")
dyn = SimplifiedDIPDynamics(config)
print(f"   Dynamics: {type(dyn)}")

print("6. Creating controller...")
ctrl = SuperTwistingSMC(gains=[1.0, 2.0], dt=0.01, dynamics_model=dyn)
print(f"   Controller: {type(ctrl)}")

print("7. Checking dynamics_model property...")
dyn_from_prop = ctrl.dynamics_model
print(f"   dynamics_model: {type(dyn_from_prop)}")
print(f"   Same object: {dyn_from_prop is dyn}")

print("\nAll imports and creations successful!")
