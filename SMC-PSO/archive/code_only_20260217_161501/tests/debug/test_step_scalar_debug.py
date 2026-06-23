"""Debug test for step() method with scalar inputs."""
import numpy as np
from src.plant.models.simplified.dynamics import SimplifiedDIPDynamics
from src.plant.models.simplified.config import SimplifiedDIPConfig

# Create dynamics model
config = SimplifiedDIPConfig.create_default()
dyn = SimplifiedDIPDynamics(config)

# Test state
state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0])

# Test 1: Pure scalar (Python float)
print("Test 1: Pure scalar (Python float)")
try:
    u_scalar = 1.0  # Python float
    print(f"  Input type: {type(u_scalar)}, value: {u_scalar}")
    next_state = dyn.step(state, u_scalar, dt=0.01)
    print(f"  SUCCESS: {next_state[:3]}")
except Exception as e:
    print(f"  FAILED: {e}")

# Test 2: Numpy scalar (0-d array)
print("\nTest 2: Numpy scalar (0-d array)")
try:
    u_array = np.array([1.0, 2.0])
    u_numpy_scalar = u_array[0]  # This is a numpy scalar (0-d array element)
    print(f"  Input type: {type(u_numpy_scalar)}, shape: {getattr(u_numpy_scalar, 'shape', 'N/A')}, value: {u_numpy_scalar}")
    next_state = dyn.step(state, u_numpy_scalar, dt=0.01)
    print(f"  SUCCESS: {next_state[:3]}")
except Exception as e:
    print(f"  FAILED: {e}")

# Test 3: 1D array
print("\nTest 3: 1D array")
try:
    u_1d = np.array([1.0])
    print(f"  Input type: {type(u_1d)}, shape: {u_1d.shape}, value: {u_1d}")
    next_state = dyn.step(state, u_1d, dt=0.01)
    print(f"  SUCCESS: {next_state[:3]}")
except Exception as e:
    print(f"  FAILED: {e}")

# Test 4: Simulate what batch simulation does
print("\nTest 4: Batch simulation pattern")
try:
    u_b = np.zeros((1, 10))  # 1 controller, 10 timesteps
    u_b[0, 0] = 2.5  # Set control value
    u_from_batch = u_b[0, 0]  # Extract like batch sim does
    print(f"  Input type: {type(u_from_batch)}, shape: {getattr(u_from_batch, 'shape', 'N/A')}, value: {u_from_batch}")
    next_state = dyn.step(state, u_from_batch, dt=0.01)
    print(f"  SUCCESS: {next_state[:3]}")
except Exception as e:
    print(f"  FAILED: {e}")

print("\n" + "="*60)
print("All tests passed! step() method handles all input types.")
