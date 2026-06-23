"""
Debug: Check k1/k2 extraction from controller output.
"""

import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import load_config
from src.controllers.factory import create_controller
from src.plant.core.dynamics import DIPDynamics

# Test with SCALED gains (the problematic case)
scaled_gains = [5.075, 12.839, 3.408, 2.750]
print(f"Creating controller with SCALED gains: {scaled_gains}")

config = load_config()
controller = create_controller(
    'hybrid_adaptive_sta_smc',
    config=config,
    gains=scaled_gains
)

print(f"\nController properties:")
print(f"  c1 = {controller.c1}")
print(f"  c2 = {controller.c2}")
print(f"  lambda1 = {controller.lambda1}")
print(f"  lambda2 = {controller.lambda2}")
print(f"  k1_init = {controller.k1_init}")
print(f"  k2_init = {controller.k2_init}")

# Initialize
if hasattr(controller, 'initialize_state'):
    state_vars = controller.initialize_state()
    print(f"\nInitialize_state() returns: {state_vars}")
    print(f"  Type: {type(state_vars)}")
    print(f"  Length: {len(state_vars)}")
    if len(state_vars) >= 2:
        print(f"  state_vars[0] (k1_init): {state_vars[0]}")
        print(f"  state_vars[1] (k2_init): {state_vars[1]}")

if hasattr(controller, 'initialize_history'):
    history = controller.initialize_history()
else:
    history = {}

# One step
initial_state = np.array([0.0, 0.05, 0.05, 0.0, 0.0, 0.0])
last_u = 0.0

output = controller.compute_control(initial_state, last_u, history)

print(f"\nController output:")
print(f"  Type: {type(output)}")
print(f"  Has 'u': {hasattr(output, 'u')}")

if hasattr(output, 'u'):
    print(f"  output.u = {output.u}")
    print(f"  output.state = {output.state}")
    print(f"  output.state type: {type(output.state)}")
    print(f"  output.state length: {len(output.state)}")
    print(f"  output.sigma = {output.sigma}")

    # Extract
    k1, k2, u_int = output.state
    print(f"\nExtracted values:")
    print(f"  k1 = {k1}")
    print(f"  k2 = {k2}")
    print(f"  u_int = {u_int}")

print("\n[OK] Debug complete!")
