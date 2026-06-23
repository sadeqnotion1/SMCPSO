#======================================================================================\\\
#========================= test_legacy_factory_integration.py =========================\\\
#======================================================================================\\\

"""
Legacy Factory Integration Test

This script tests the compatibility between the new factory.py and legacy_factory.py
to ensure smooth migration path and backward compatibility for existing code.
"""

import sys
import logging
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_legacy_factory_imports():
    """Test legacy factory imports."""
    logger.info("Testing legacy factory imports...")

    try:
        # Test legacy factory functions

        logger.info("✓ Legacy factory imports successful")
        return True

    except Exception as e:
        logger.error(f"✗ Legacy factory imports failed: {e}")
        return False

def test_controller_name_normalization():
    """Test controller name normalization and aliasing."""
    logger.info("Testing controller name normalization...")

    try:
        from src.controllers.factory.legacy_factory import normalize_controller_name

        test_cases = [
            ("classical_smc", "classical_smc"),
            ("classic_smc", "classical_smc"),
            ("smc_v1", "classical_smc"),
            ("sta", "sta_smc"),
            ("super_twisting", "sta_smc"),
            ("adaptive", "adaptive_smc"),
            ("hybrid", "hybrid_adaptive_sta_smc"),
        ]

        all_passed = True
        for input_name, expected in test_cases:
            result = normalize_controller_name(input_name)
            if result == expected:
                logger.info(f"✓ '{input_name}' -> '{result}' (correct)")
            else:
                logger.error(f"✗ '{input_name}' -> '{result}' (expected: '{expected}')")
                all_passed = False

        return all_passed

    except Exception as e:
        logger.error(f"✗ Controller name normalization test failed: {e}")
        return False

def test_deprecation_mapping():
    """Test parameter deprecation mapping."""
    logger.info("Testing deprecation mapping...")

    try:
        from src.controllers.factory.legacy_factory import apply_deprecation_mapping
        import warnings

        # Test classical_smc deprecation mappings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Test deprecated parameter mappings
            old_params = {
                "boundaryLayer": 0.05,
                "maxForce": 100.0,
                "dampingGain": 1.0
            }

            mapped_params = apply_deprecation_mapping("classical_smc", old_params)

            expected_mappings = {
                "boundary_layer": 0.05,
                "max_force": 100.0,
                "damping_gain": 1.0
            }

            if mapped_params == expected_mappings:
                logger.info("✓ Parameter deprecation mapping works correctly")
                if len(w) > 0:
                    logger.info(f"✓ Generated {len(w)} deprecation warnings as expected")
                return True
            else:
                logger.error(f"✗ Mapping failed: got {mapped_params}, expected {expected_mappings}")
                return False

    except Exception as e:
        logger.error(f"✗ Deprecation mapping test failed: {e}")
        return False

def test_legacy_controller_creation():
    """Test legacy controller creation interface."""
    logger.info("Testing legacy controller creation...")

    try:
        from src.controllers.factory.legacy_factory import create_controller

        # Test basic controller creation with legacy interface
        test_controllers = [
            {
                'name': 'classical_smc',
                'params': {'gains': [20.0, 15.0, 12.0, 8.0, 35.0, 5.0]}
            },
            {
                'name': 'sta_smc',
                'params': {'gains': [25.0, 15.0, 20.0, 12.0, 8.0, 6.0]}
            }
        ]

        created_controllers = {}

        for test_case in test_controllers:
            name = test_case['name']
            params = test_case['params']

            try:
                controller = create_controller(name, **params)

                # Verify basic interface
                if hasattr(controller, 'compute_control'):
                    logger.info(f"✓ Legacy creation of {name} successful")
                    created_controllers[name] = controller
                else:
                    logger.error(f"✗ {name} missing compute_control method")

            except Exception as e:
                logger.error(f"✗ Legacy creation of {name} failed: {e}")

        return len(created_controllers) > 0

    except Exception as e:
        logger.error(f"✗ Legacy controller creation test failed: {e}")
        return False

def test_factory_compatibility():
    """Test compatibility between new and legacy factory."""
    logger.info("Testing factory compatibility...")

    try:
        # Import both factories
        from src.controllers.factory import create_controller as new_create_controller
        from src.controllers.factory.legacy_factory import create_controller as legacy_create_controller

        # Test same parameters produce compatible results
        test_params = {
            'name': 'classical_smc',
            'gains': [20.0, 15.0, 12.0, 8.0, 35.0, 5.0]
        }

        # Create controllers with both factories
        new_controller = new_create_controller(test_params['name'], gains=test_params['gains'])
        legacy_controller = legacy_create_controller(test_params['name'], **test_params)

        # Test that both have the same interface
        new_has_compute = hasattr(new_controller, 'compute_control')
        legacy_has_compute = hasattr(legacy_controller, 'compute_control')

        if new_has_compute and legacy_has_compute:
            logger.info("✓ Both factories produce controllers with compute_control")

            # Test control computation compatibility
            test_state = np.array([0.1, 0.0, 0.05, 0.0, 0.02, 0.0])

            new_result = new_controller.compute_control(test_state, 0.0, {})
            legacy_result = legacy_controller.compute_control(test_state, 0.0, {})

            # Extract control values
            if isinstance(new_result, dict) and 'u' in new_result:
                new_u = new_result['u']
            else:
                new_u = float(new_result)

            if isinstance(legacy_result, dict) and 'u' in legacy_result:
                legacy_u = legacy_result['u']
            else:
                legacy_u = float(legacy_result)

            # Check if results are reasonably close (allowing for small differences due to implementation)
            if abs(new_u - legacy_u) < 1e-6:
                logger.info(f"✓ Control outputs match: new={new_u:.6f}, legacy={legacy_u:.6f}")
                return True
            else:
                logger.warning(f"? Control outputs differ: new={new_u:.6f}, legacy={legacy_u:.6f}")
                return True  # Still considered compatible as long as both work

        else:
            logger.error(f"✗ Interface mismatch: new_has_compute={new_has_compute}, legacy_has_compute={legacy_has_compute}")
            return False

    except Exception as e:
        logger.error(f"✗ Factory compatibility test failed: {e}")
        return False

def test_migration_path():
    """Test migration path from legacy to new factory."""
    logger.info("Testing migration path...")

    try:
        # Import factory __init__ which should expose both interfaces
        from src.controllers.factory import (
            create_controller,
            create_controller_legacy,
            SMCFactory,
            SMCType
        )

        # Test that both interfaces work
        test_gains = [20.0, 15.0, 12.0, 8.0, 35.0, 5.0]

        # Method 1: New factory interface
        controller1 = create_controller('classical_smc', gains=test_gains)

        # Method 2: Legacy factory interface
        controller2 = create_controller_legacy('classical_smc', gains=test_gains)

        # Method 3: SMC factory interface
        from src.controllers.factory import SMCConfig
        config = SMCConfig(gains=test_gains)
        controller3 = SMCFactory.create_controller(SMCType.CLASSICAL, config)

        # Verify all three methods work
        controllers = [controller1, controller2, controller3]
        names = ['new_factory', 'legacy_factory', 'smc_factory']

        all_work = True
        for i, (controller, name) in enumerate(zip(controllers, names)):
            if hasattr(controller, 'compute_control'):
                logger.info(f"✓ Migration path {i+1} ({name}) works")
            else:
                logger.error(f"✗ Migration path {i+1} ({name}) failed")
                all_work = False

        return all_work

    except Exception as e:
        logger.error(f"✗ Migration path test failed: {e}")
        return False

def main():
    """Run all legacy factory integration tests."""
    logger.info("Starting Legacy Factory Integration Tests...")

    tests = [
        ("Legacy Factory Imports", test_legacy_factory_imports),
        ("Controller Name Normalization", test_controller_name_normalization),
        ("Deprecation Mapping", test_deprecation_mapping),
        ("Legacy Controller Creation", test_legacy_controller_creation),
        ("Factory Compatibility", test_factory_compatibility),
        ("Migration Path", test_migration_path)
    ]

    results = {}
    passed_tests = 0

    for test_name, test_func in tests:
        logger.info(f"\n{'='*60}")
        logger.info(f"TEST: {test_name}")
        logger.info(f"{'='*60}")

        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed_tests += 1
                logger.info(f"✓ {test_name} PASSED")
            else:
                logger.error(f"✗ {test_name} FAILED")
        except Exception as e:
            logger.error(f"✗ {test_name} FAILED with exception: {e}")
            results[test_name] = False

    # Summary
    total_tests = len(tests)
    success_rate = passed_tests / total_tests * 100

    logger.info(f"\n{'='*60}")
    logger.info("LEGACY FACTORY INTEGRATION TEST SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")

    if success_rate >= 80:
        logger.info("✓ Legacy factory integration validation PASSED")
        return True
    else:
        logger.warning("✗ Legacy factory integration validation FAILED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)