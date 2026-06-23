#==========================================================================================\\\
#================= scripts/optimization/test_hybrid_emergency_reset.py ===================\\\
#==========================================================================================\\\

"""Test if hybrid controller's emergency reset is causing failures."""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import numpy as np  # noqa: E402
from src.config import load_config  # noqa: E402
from src.controllers.factory import create_controller  # noqa: E402
from src.plant.models.dynamics import DoubleInvertedPendulum  # noqa: E402

# Load config
config = load_config('config.yaml', allow_unknown=False)

# Test with PSO bounds: [c1, λ1, c2, λ2]
test_gains = [
    [5.0, 0.5, 5.0, 0.1],  # Lower bound
    [30.0, 10.0, 30.0, 5.0],  # Upper bound
    [15.0, 5.0, 15.0, 2.5],  # Middle
]

dynamics = DoubleInvertedPendulum(config=config.physics)
dt = 0.01
initial_state = np.array([0.0, 0.02, 0.02, 0.0, 0.0, 0.0])

for i, gains in enumerate(test_gains):
    print(f"\nTest {i+1}: gains={gains}")

    # Create controller
    temp_config = config.model_copy(deep=True)
    ctrl_cfg = getattr(temp_config.controllers, 'hybrid_adaptive_sta_smc')
    updated = ctrl_cfg.model_copy(update={'gains': gains})
    setattr(temp_config.controllers, 'hybrid_adaptive_sta_smc', updated)

    controller = create_controller('hybrid_adaptive_sta_smc', config=temp_config)

    # Initialize
    state_vars = controller.initialize_state()
    history = controller.initialize_history()
    state = initial_state.copy()

    # Simulate first 10 steps
    emergency_resets = 0
    for step in range(10):
        result = controller.compute_control(state, state_vars, history)

        control = result.u if hasattr(result, 'u') else result[0]
        state_vars = result.state if hasattr(result, 'state') else (result[1] if len(result) > 1 else state_vars)

        # Check for emergency reset (control=0 is suspicious)
        if abs(control) < 1e-6 and step > 0:
            emergency_resets += 1
            print(f"  Step {step}: control=0 (likely emergency reset)")

        # Update state
        dyn_result = dynamics.compute_dynamics(state, np.array([control]))
        if dyn_result.success:
            state = state + dyn_result.state_derivative * dt
        else:
            print(f"  Step {step}: Dynamics failed!")
            break

        if step == 0:
            print(f"  Step 0: s={result.s:.2f}, k1={state_vars[0]:.2f}, control={control:.2f}")

    print(f"  Emergency resets: {emergency_resets}/10")
    print(f"  Final state norm: {np.linalg.norm(state[:3]):.4f}")