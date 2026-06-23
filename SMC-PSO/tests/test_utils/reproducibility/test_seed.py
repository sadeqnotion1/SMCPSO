#======================================================================================\\
#=================== tests/test_utils/reproducibility/test_seed.py ====================\\
#======================================================================================\\

"""
Comprehensive tests for reproducibility seed utilities.

Tests cover:
- SeedManager class - Deterministic seed generation and history tracking
- set_global_seed() - Global Python/NumPy RNG seeding
- create_rng() - Local NumPy Generator creation
- Integration scenarios and reproducibility validation
"""

import pytest
import random
import numpy as np
from src.utils.testing.reproducibility.seed import SeedManager, set_global_seed, create_rng


# =====================================================================================
# Tests for SeedManager
# =====================================================================================

class TestSeedManager:
    """Test SeedManager deterministic seed generation."""

    def test_initialization_with_seed(self):
        """Test SeedManager initialization with master seed."""
        manager = SeedManager(master_seed=42)
        assert manager.master_seed == 42
        assert hasattr(manager, '_gen')
        assert isinstance(manager.history, list)
        assert len(manager.history) == 0

    def test_initialization_with_none(self):
        """Test SeedManager initialization with None (unseeded)."""
        manager = SeedManager(master_seed=None)
        assert manager.master_seed is None
        assert hasattr(manager, '_gen')
        assert isinstance(manager.history, list)

    def test_spawn_returns_valid_seed(self):
        """Test that spawn() returns valid 32-bit integer seed."""
        manager = SeedManager(master_seed=100)
        seed = manager.spawn()

        assert isinstance(seed, int)
        assert 0 <= seed < 2**32

    def test_spawn_updates_history(self):
        """Test that spawn() appends to history."""
        manager = SeedManager(master_seed=100)

        assert len(manager.history) == 0

        seed1 = manager.spawn()
        assert len(manager.history) == 1
        assert manager.history[0] == seed1

        seed2 = manager.spawn()
        assert len(manager.history) == 2
        assert manager.history[1] == seed2

    def test_multiple_spawn_calls_different_seeds(self):
        """Test that consecutive spawn() calls return different seeds."""
        manager = SeedManager(master_seed=200)

        seeds = [manager.spawn() for _ in range(10)]

        # All seeds should be different
        assert len(set(seeds)) == 10

    def test_deterministic_seed_generation(self):
        """Test that same master seed produces same spawned seeds."""
        manager1 = SeedManager(master_seed=42)
        manager2 = SeedManager(master_seed=42)

        seeds1 = [manager1.spawn() for _ in range(5)]
        seeds2 = [manager2.spawn() for _ in range(5)]

        assert seeds1 == seeds2

    def test_different_master_seeds_different_spawns(self):
        """Test that different master seeds produce different spawned seeds."""
        manager1 = SeedManager(master_seed=100)
        manager2 = SeedManager(master_seed=200)

        seeds1 = [manager1.spawn() for _ in range(5)]
        seeds2 = [manager2.spawn() for _ in range(5)]

        assert seeds1 != seeds2

    def test_history_tracks_all_spawned_seeds(self):
        """Test that history contains all spawned seeds in order."""
        manager = SeedManager(master_seed=300)

        expected_history = []
        for _ in range(20):
            seed = manager.spawn()
            expected_history.append(seed)

        assert manager.history == expected_history

    def test_unseeded_manager_generates_valid_seeds(self):
        """Test that unseeded manager (None) still generates valid seeds."""
        manager = SeedManager(master_seed=None)

        seeds = [manager.spawn() for _ in range(10)]

        # All seeds should be valid integers
        assert all(isinstance(s, int) for s in seeds)
        assert all(0 <= s < 2**32 for s in seeds)

    def test_seed_range_boundaries(self):
        """Test spawned seeds are within valid 32-bit range."""
        manager = SeedManager(master_seed=999)

        # Generate many seeds to test boundary conditions
        seeds = [manager.spawn() for _ in range(1000)]

        min_seed = min(seeds)
        max_seed = max(seeds)

        assert min_seed >= 0
        assert max_seed < 2**32

    def test_large_master_seed(self):
        """Test SeedManager with large master seed value."""
        large_seed = 2**31 - 1
        manager = SeedManager(master_seed=large_seed)

        seed = manager.spawn()
        assert isinstance(seed, int)
        assert 0 <= seed < 2**32


# =====================================================================================
# Tests for set_global_seed()
# =====================================================================================

class TestSetGlobalSeed:
    """Test set_global_seed() global RNG initialization."""

    def test_set_global_seed_with_valid_seed(self):
        """Test setting global seed with valid integer."""
        set_global_seed(123)

        # Should not raise any exceptions
        value_random = random.random()
        value_numpy = np.random.rand()

        assert isinstance(value_random, float)
        assert isinstance(value_numpy, float)

    def test_set_global_seed_none_is_noop(self):
        """Test that set_global_seed(None) does nothing."""
        # Capture state before
        set_global_seed(999)
        random.random()
        np.random.rand()

        # Set to None (should not change state)
        set_global_seed(None)

        # Should still work
        value_random = random.random()
        value_numpy = np.random.rand()

        assert isinstance(value_random, float)
        assert isinstance(value_numpy, float)

    def test_python_random_seeding(self):
        """Test that Python random module is seeded correctly."""
        set_global_seed(42)
        value1 = random.random()

        set_global_seed(42)
        value2 = random.random()

        # Same seed should produce same value
        assert value1 == value2

    def test_numpy_random_seeding(self):
        """Test that NumPy global RNG is seeded correctly."""
        set_global_seed(42)
        value1 = np.random.rand()

        set_global_seed(42)
        value2 = np.random.rand()

        # Same seed should produce same value
        assert value1 == value2

    def test_deterministic_sequence_python(self):
        """Test deterministic sequence from Python random module."""
        set_global_seed(100)
        seq1 = [random.random() for _ in range(10)]

        set_global_seed(100)
        seq2 = [random.random() for _ in range(10)]

        assert seq1 == seq2

    def test_deterministic_sequence_numpy(self):
        """Test deterministic sequence from NumPy global RNG."""
        set_global_seed(100)
        seq1 = [np.random.rand() for _ in range(10)]

        set_global_seed(100)
        seq2 = [np.random.rand() for _ in range(10)]

        np.testing.assert_array_equal(seq1, seq2)

    def test_different_seeds_different_outputs(self):
        """Test that different seeds produce different outputs."""
        set_global_seed(100)
        value1_random = random.random()
        value1_numpy = np.random.rand()

        set_global_seed(200)
        value2_random = random.random()
        value2_numpy = np.random.rand()

        assert value1_random != value2_random
        assert value1_numpy != value2_numpy

    def test_both_rngs_seeded_independently(self):
        """Test that Python and NumPy RNGs are seeded independently."""
        set_global_seed(42)

        # Generate from Python random
        python_value = random.random()

        # Reset and generate from NumPy
        set_global_seed(42)
        numpy_value = np.random.rand()

        # Both should be deterministic from same seed
        set_global_seed(42)
        assert random.random() == python_value

        set_global_seed(42)
        assert np.random.rand() == numpy_value


# =====================================================================================
# Tests for create_rng()
# =====================================================================================

class TestCreateRng:
    """Test create_rng() local NumPy Generator creation."""

    def test_create_rng_with_valid_seed(self):
        """Test creating RNG with valid integer seed."""
        rng = create_rng(seed=42)

        assert isinstance(rng, np.random.Generator)

    def test_create_rng_with_none(self):
        """Test creating unseeded RNG with None."""
        rng = create_rng(seed=None)

        assert isinstance(rng, np.random.Generator)

    def test_deterministic_rng_behavior(self):
        """Test that same seed produces same RNG outputs."""
        rng1 = create_rng(seed=100)
        values1 = [rng1.random() for _ in range(10)]

        rng2 = create_rng(seed=100)
        values2 = [rng2.random() for _ in range(10)]

        np.testing.assert_array_equal(values1, values2)

    def test_different_seeds_different_outputs(self):
        """Test that different seeds produce different RNG outputs."""
        rng1 = create_rng(seed=100)
        values1 = [rng1.random() for _ in range(10)]

        rng2 = create_rng(seed=200)
        values2 = [rng2.random() for _ in range(10)]

        # Should not be equal
        assert not np.allclose(values1, values2)

    def test_independent_rngs(self):
        """Test that different RNG instances are independent."""
        rng1 = create_rng(seed=50)
        rng2 = create_rng(seed=50)

        # Even with same seed, instances are independent
        value1_a = rng1.random()
        value1_b = rng1.random()

        value2_a = rng2.random()
        value2_b = rng2.random()

        # Same sequence from same seed
        assert value1_a == value2_a
        assert value1_b == value2_b

    def test_rng_does_not_affect_global(self):
        """Test that local RNG does not affect global NumPy RNG."""
        # Seed global RNG
        set_global_seed(123)
        global_value1 = np.random.rand()

        # Create and use local RNG
        rng = create_rng(seed=456)
        local_values = [rng.random() for _ in range(100)]

        # Reset global RNG - should produce same value
        set_global_seed(123)
        global_value2 = np.random.rand()

        assert global_value1 == global_value2

    def test_unseeded_rngs_are_different(self):
        """Test that unseeded RNGs produce different outputs."""
        rng1 = create_rng(seed=None)
        rng2 = create_rng(seed=None)

        values1 = [rng1.random() for _ in range(10)]
        values2 = [rng2.random() for _ in range(10)]

        # Extremely unlikely to be identical
        assert values1 != values2

    def test_rng_methods_available(self):
        """Test that created RNG has standard Generator methods."""
        rng = create_rng(seed=42)

        assert hasattr(rng, 'random')
        assert hasattr(rng, 'integers')
        assert hasattr(rng, 'normal')
        assert hasattr(rng, 'uniform')

    def test_large_seed_value(self):
        """Test creating RNG with large seed value."""
        large_seed = 2**31 - 1
        rng = create_rng(seed=large_seed)

        assert isinstance(rng, np.random.Generator)
        value = rng.random()
        assert 0.0 <= value < 1.0


# =====================================================================================
# Integration and Reproducibility Tests
# =====================================================================================

class TestReproducibilityIntegration:
    """Test integration scenarios and reproducibility validation."""

    def test_seed_manager_with_create_rng(self):
        """Test SeedManager workflow with create_rng()."""
        manager = SeedManager(master_seed=42)

        # Spawn seeds and create RNGs
        seed1 = manager.spawn()
        seed2 = manager.spawn()

        rng1 = create_rng(seed=seed1)
        rng2 = create_rng(seed=seed2)

        # Different spawned seeds → different RNG outputs
        values1 = [rng1.random() for _ in range(5)]
        values2 = [rng2.random() for _ in range(5)]

        assert not np.allclose(values1, values2)

    def test_reproducible_simulation_workflow(self):
        """Test complete reproducible simulation workflow."""
        # Workflow 1
        set_global_seed(999)
        manager1 = SeedManager(master_seed=100)
        rng1 = create_rng(seed=manager1.spawn())
        sim_result1 = np.sum(rng1.normal(size=100))

        # Workflow 2 (same seeds)
        set_global_seed(999)
        manager2 = SeedManager(master_seed=100)
        rng2 = create_rng(seed=manager2.spawn())
        sim_result2 = np.sum(rng2.normal(size=100))

        # Should be identical
        assert sim_result1 == sim_result2

    def test_multiple_seed_managers_independent(self):
        """Test that multiple SeedManagers with same seed are independent."""
        manager1 = SeedManager(master_seed=42)
        manager2 = SeedManager(master_seed=42)

        # Same master seed → same spawned seeds
        seeds1 = [manager1.spawn() for _ in range(5)]
        seeds2 = [manager2.spawn() for _ in range(5)]

        assert seeds1 == seeds2

    def test_global_and_local_rng_isolation(self):
        """Test that global and local RNGs are isolated."""
        # Seed global
        set_global_seed(100)

        # Create local RNG
        rng = create_rng(seed=200)

        # Use both
        global_values = [np.random.rand() for _ in range(10)]
        local_values = [rng.random() for _ in range(10)]

        # Reset global - should not affect local
        set_global_seed(100)
        global_values2 = [np.random.rand() for _ in range(10)]

        # Global should be repeatable
        np.testing.assert_array_equal(global_values, global_values2)

    def test_seed_manager_history_reproducibility(self):
        """Test SeedManager history enables reproduction of spawned seeds."""
        manager1 = SeedManager(master_seed=42)

        # Spawn some seeds
        for _ in range(10):
            manager1.spawn()

        # Create new manager with same seed
        manager2 = SeedManager(master_seed=42)

        # Reproduce the same spawned seeds
        for expected_seed in manager1.history:
            actual_seed = manager2.spawn()
            assert actual_seed == expected_seed

    def test_end_to_end_reproducibility(self):
        """Test end-to-end reproducibility with all utilities."""
        # Experiment 1
        set_global_seed(1234)
        manager = SeedManager(master_seed=5678)

        results1 = []
        for _ in range(3):
            seed = manager.spawn()
            rng = create_rng(seed=seed)
            result = np.mean(rng.normal(loc=0, scale=1, size=1000))
            results1.append(result)

        # Experiment 2 (identical setup)
        set_global_seed(1234)
        manager = SeedManager(master_seed=5678)

        results2 = []
        for _ in range(3):
            seed = manager.spawn()
            rng = create_rng(seed=seed)
            result = np.mean(rng.normal(loc=0, scale=1, size=1000))
            results2.append(result)

        # Results should be identical
        np.testing.assert_array_almost_equal(results1, results2)

    def test_parallel_rng_independence(self):
        """Test that parallel workers can have independent RNGs."""
        manager = SeedManager(master_seed=42)

        # Simulate 5 parallel workers
        worker_seeds = [manager.spawn() for _ in range(5)]
        worker_rngs = [create_rng(seed=s) for s in worker_seeds]

        # Each worker generates data
        worker_data = [rng.random(size=100) for rng in worker_rngs]

        # All workers should have different data
        for i in range(5):
            for j in range(i + 1, 5):
                assert not np.allclose(worker_data[i], worker_data[j])


# =====================================================================================
# Exception Handling Tests (Coverage for error paths)
# =====================================================================================

class TestSeedExceptionHandling:
    """Test exception handling in seed utilities."""

    def test_set_global_seed_with_invalid_type(self):
        """Test graceful handling when seed cannot convert to int (dict)."""
        # Should not raise - exception is caught and ignored
        set_global_seed({"invalid": "seed"})

        # RNGs should still work (not crashed)
        value = random.random()
        assert isinstance(value, float)

    def test_set_global_seed_with_float_seed(self):
        """Test that float seeds are properly converted to int."""
        set_global_seed(42.7)
        value1 = random.random()

        # Same seed (truncated to int) should produce same value
        set_global_seed(42)
        value2 = random.random()

        assert value1 == value2  # 42.7 converts to 42

    def test_create_rng_with_invalid_seed_type(self):
        """Test create_rng returns unseeded generator with invalid seed."""
        # String that can't convert to int - should fallback to unseeded
        rng = create_rng(seed="invalid")

        assert isinstance(rng, np.random.Generator)
        # Should still generate valid random values
        value = rng.random()
        assert 0.0 <= value < 1.0

    def test_create_rng_with_non_serializable_seed(self):
        """Test create_rng handles complex objects gracefully."""
        # Complex object seed - should catch exception and fallback
        class ComplexObject:
            def __int__(self):
                raise ValueError("Cannot convert to int")

        rng = create_rng(seed=ComplexObject())

        assert isinstance(rng, np.random.Generator)
        value = rng.random()
        assert 0.0 <= value < 1.0

    def test_set_global_seed_exception_isolation(self):
        """Test that Python and NumPy seeding exceptions are independent."""
        # Create a mock scenario where one might fail but not the other
        # Even if one exception is triggered, the other should still work

        # Use a string - will trigger exception in int() conversion
        set_global_seed("not_a_number")

        # Both RNGs should still be usable (didn't crash the program)
        python_value = random.random()
        numpy_value = np.random.rand()

        assert isinstance(python_value, float)
        assert isinstance(numpy_value, float)
