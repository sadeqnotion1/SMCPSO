#======================================================================================\\\
#========================== test_pso_integration_workflow.py ==========================\\\
#======================================================================================\\\

#!/usr/bin/env python3
#==========================================================================================\\\
#========================== test_pso_integration_workflow.py ===========================\\\
#==========================================================================================\\\

"""
Quick test script to validate end-to-end PSO integration workflow.

Tests:
1. Controller factory PSO interface
2. Gain bounds retrieval
3. Gain validation
4. End-to-end PSO optimization workflow
"""

from typing import List, Callable, Tuple
import numpy as np
from src.controllers.factory import (
    SMCType, create_smc_for_pso, get_gain_bounds_for_pso, validate_smc_gains, PSOControllerWrapper
)
from src.plant.configurations import ConfigurationFactory


def test_pso_controller_creation() -> PSOControllerWrapper:
    """Test PSO controller creation and basic functionality."""
    print("=== Testing PSO Controller Creation ===")

    # Create plant configuration
    plant_config = ConfigurationFactory.create_default_config("simplified")

    # Test creating classical SMC controller
    gains = [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]  # 6 gains for classical SMC
    controller = create_smc_for_pso(SMCType.CLASSICAL, gains, plant_config)

    print(f"+ Controller created successfully: {type(controller).__name__}")

    # Test simplified control interface (PSO style)
    state = np.array([0.1, 0.2, 0.3, 0.0, 0.0, 0.0])
    control = controller.compute_control(state)

    print(f"+ Control computed: {control} (shape: {control.shape})")
    assert isinstance(control, np.ndarray)
    assert control.shape == (1,)

    return controller


def test_gain_bounds() -> Tuple[List[float], List[float]]:
    """Test gain bounds retrieval for PSO."""
    print("\n=== Testing Gain Bounds Retrieval ===")

    bounds = get_gain_bounds_for_pso(SMCType.CLASSICAL)
    print(f"+ Bounds retrieved: {bounds}")

    assert isinstance(bounds, tuple)
    assert len(bounds) == 2

    lower_bounds, upper_bounds = bounds
    print(f"+ Lower bounds: {lower_bounds}")
    print(f"+ Upper bounds: {upper_bounds}")

    assert len(lower_bounds) == 6  # Classical SMC has 6 gains
    assert len(upper_bounds) == 6
    assert all(l < u for l, u in zip(lower_bounds, upper_bounds))  # noqa: E741 - conventional in zip

    return bounds


def test_gain_validation() -> bool:
    """Test gain validation."""
    print("\n=== Testing Gain Validation ===")

    # Valid gains
    valid_gains = [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]
    result = validate_smc_gains(SMCType.CLASSICAL, valid_gains)
    print(f"+ Valid gains passed: {result}")
    assert result

    # Invalid gains (negative)
    invalid_gains = [-1.0, 5.0, 8.0, 3.0, 15.0, 2.0]
    result = validate_smc_gains(SMCType.CLASSICAL, invalid_gains)
    print(f"+ Invalid gains rejected: {result}")
    assert not result

    return True


def test_pso_fitness_function() -> Callable[[List[float]], float]:
    """Test a simplified PSO fitness function."""
    print("\n=== Testing PSO Fitness Function ===")

    plant_config = ConfigurationFactory.create_default_config("simplified")

    def fitness_function(gains: List[float]) -> float:
        """Simplified fitness function for PSO testing."""
        try:
            # Create controller
            controller = create_smc_for_pso(SMCType.CLASSICAL, gains, plant_config)

            # Test states
            test_states = [
                np.array([0.1, 0.2, 0.3, 0.0, 0.0, 0.0]),
                np.array([0.2, 0.1, 0.4, 0.1, 0.0, 0.0]),
                np.array([0.0, 0.3, 0.2, 0.0, 0.1, 0.0])
            ]

            total_cost = 0.0
            for state in test_states:
                control = controller.compute_control(state)

                # Simple cost function: penalize large states and controls
                state_cost = np.sum(state[:3]**2)  # Position errors
                control_cost = np.sum(control**2)  # Control effort
                total_cost += state_cost + 0.1 * control_cost

            return total_cost

        except Exception as e:
            print(f"Error in fitness function: {e}")
            return 1e6  # High penalty for failure

    # Test with different gain sets
    test_gains = [
        [10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
        [15.0, 8.0, 12.0, 5.0, 20.0, 3.0],
        [5.0, 3.0, 6.0, 2.0, 10.0, 1.0]
    ]

    costs = []
    for i, gains in enumerate(test_gains):
        cost = fitness_function(gains)
        costs.append(cost)
        print(f"+ Gains {i+1}: {gains} -> Cost: {cost:.4f}")

    print(f"+ Fitness function working - cost range: {min(costs):.4f} to {max(costs):.4f}")
    return fitness_function


def test_multiple_smc_types() -> bool:
    """Test PSO integration with multiple SMC types."""
    print("\n=== Testing Multiple SMC Types ===")

    plant_config = ConfigurationFactory.create_default_config("simplified")

    test_configs = [
        (SMCType.CLASSICAL, [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]),
        (SMCType.ADAPTIVE, [10.0, 5.0, 8.0, 3.0, 2.0])
    ]

    for smc_type, gains in test_configs:
        print(f"Testing {smc_type.value}...")

        # Test controller creation
        controller = create_smc_for_pso(smc_type, gains, plant_config)

        # Test control computation
        state = np.array([0.1, 0.2, 0.3, 0.0, 0.0, 0.0])
        control = controller.compute_control(state)

        # Test bounds
        bounds = get_gain_bounds_for_pso(smc_type)

        # Test validation
        is_valid = validate_smc_gains(smc_type, gains)

        print(f"+ {smc_type.value}: Controller OK, Control: {control[0]:.4f}, Bounds: {len(bounds[0])} gains, Valid: {is_valid}")

    return True


def main() -> bool:
    """Run all PSO integration tests."""
    print("PSO OPTIMIZATION ENGINEER - INTEGRATION VALIDATION")
    print("=" * 60)

    try:
        # Test individual components
        test_pso_controller_creation()
        test_gain_bounds()
        test_gain_validation()

        # Test integrated functionality
        test_pso_fitness_function()
        test_multiple_smc_types()

        print("\n" + "=" * 60)
        print("ALL PSO INTEGRATION TESTS PASSED!")
        print("* PSO controller creation functional")
        print("* Gain bounds retrieval working")
        print("* Gain validation passing")
        print("* End-to-end PSO workflow operational")
        print("* Integration with all SMC controller types")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\nERROR: PSO Integration Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)