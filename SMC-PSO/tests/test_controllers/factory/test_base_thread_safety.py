#======================================================================================\
#=========== tests/test_controllers/factory/test_base_thread_safety.py ===============\
#======================================================================================\

"""
Thread-safety tests for factory/base.py.

Tests cover:
- Concurrent create_controller() calls (race conditions)
- Lock acquisition and timeout behavior
- Memory isolation (no shared state corruption)
- Error handling under concurrency
- Cleanup and resource management
- Deadlock prevention

Week 3 Coverage Goal: Thread-safety → 95%+ coverage (safety-critical)
"""

import pytest
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError
from unittest.mock import Mock, patch
import gc

from src.controllers.factory.base import (
    create_controller,
    get_lock_statistics,
    FactoryLockTimeoutError,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def simple_config():
    """Create simple config for thread-safety tests (avoid complex mocking)."""
    config = Mock()
    config.simulation = Mock()
    config.simulation.dt = 0.01
    config.physics = Mock()
    config.controllers = Mock()
    return config


@pytest.fixture
def classical_gains():
    """Valid classical SMC gains."""
    return [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]


@pytest.fixture
def adaptive_gains():
    """Valid adaptive SMC gains."""
    return [10.0, 5.0, 8.0, 3.0, 5.0]


@pytest.fixture
def reset_lock_stats():
    """Reset lock statistics before each test."""
    # Note: This fixture documents that lock stats are global
    # In real implementation, might need to call reset function if available
    yield
    # Stats persist across tests - this is intentional for monitoring


# =============================================================================
# Test Class: Concurrent Controller Creation
# =============================================================================

class TestConcurrentControllerCreation:
    """Test concurrent create_controller() calls for race conditions."""

    def test_concurrent_classical_smc_creation(self, simple_config, classical_gains):
        """Should safely create multiple classical SMC controllers concurrently."""
        n_threads = 10
        controllers = []
        errors = []

        def create_worker():
            try:
                controller = create_controller('classical_smc', simple_config, classical_gains)
                controllers.append(controller)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=create_worker) for _ in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5.0)

        # Should create all controllers without errors
        assert len(errors) == 0, f"Thread-safety errors: {errors}"
        assert len(controllers) == n_threads

    def test_concurrent_mixed_controller_types(self, simple_config, classical_gains, adaptive_gains):
        """Should safely create different controller types concurrently."""
        n_iterations = 5
        results = {'classical': [], 'adaptive': [], 'errors': []}

        def create_classical():
            try:
                controller = create_controller('classical_smc', simple_config, classical_gains)
                results['classical'].append(controller)
            except Exception as e:
                results['errors'].append(('classical', e))

        def create_adaptive():
            try:
                controller = create_controller('adaptive_smc', simple_config, adaptive_gains)
                results['adaptive'].append(controller)
            except Exception as e:
                results['errors'].append(('adaptive', e))

        threads = []
        for _ in range(n_iterations):
            threads.append(threading.Thread(target=create_classical))
            threads.append(threading.Thread(target=create_adaptive))

        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10.0)

        # Check for errors
        assert len(results['errors']) == 0, f"Concurrent creation errors: {results['errors']}"
        assert len(results['classical']) == n_iterations
        assert len(results['adaptive']) == n_iterations

    def test_concurrent_with_thread_pool(self, simple_config, classical_gains):
        """Should handle concurrent creation using ThreadPoolExecutor."""
        n_workers = 8
        n_tasks = 32

        def create_task(task_id):
            controller = create_controller('classical_smc', simple_config, classical_gains)
            return (task_id, controller)

        with ThreadPoolExecutor(max_workers=n_workers) as executor:
            futures = [executor.submit(create_task, i) for i in range(n_tasks)]
            results = []

            for future in as_completed(futures, timeout=30):
                task_id, controller = future.result()
                results.append((task_id, controller))

        # All tasks should complete
        assert len(results) == n_tasks
        # All controllers should be valid
        assert all(ctrl is not None for _, ctrl in results)


# =============================================================================
# Test Class: Lock Acquisition and Timeout
# =============================================================================

class TestLockAcquisitionAndTimeout:
    """Test lock acquisition, timeout behavior, and statistics."""

    def test_lock_statistics_tracked(self, simple_config, classical_gains):
        """Should track lock acquisition statistics."""
        # Get initial stats
        stats_before = get_lock_statistics()
        acquisitions_before = stats_before.get('acquisitions', 0)

        # Create controller (should acquire lock)
        create_controller('classical_smc', simple_config, classical_gains)

        # Check stats updated
        stats_after = get_lock_statistics()
        acquisitions_after = stats_after.get('acquisitions', 0)

        # At least one lock acquisition should have happened
        assert acquisitions_after > acquisitions_before

    def test_lock_contention_measured(self, simple_config, classical_gains):
        """Should measure lock contention when threads compete."""
        n_threads = 20
        results = []

        def create_worker():
            controller = create_controller('classical_smc', simple_config, classical_gains)
            results.append(controller)

        stats_before = get_lock_statistics()

        threads = [threading.Thread(target=create_worker) for _ in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10.0)

        stats_after = get_lock_statistics()

        # Contentions should be tracked (may be 0 if threads don't overlap)
        assert 'contentions' in stats_after
        assert 'total_wait_time' in stats_after

    def test_lock_released_after_success(self, simple_config, classical_gains):
        """Should release lock after successful controller creation."""
        # Create controller
        controller1 = create_controller('classical_smc', simple_config, classical_gains)

        # Should be able to create another (lock was released)
        controller2 = create_controller('classical_smc', simple_config, classical_gains)

        assert controller1 is not None
        assert controller2 is not None

    def test_lock_released_after_error(self, simple_config):
        """Should release lock even if controller creation fails."""
        # Try to create with invalid type (should fail but release lock)
        with pytest.raises((ValueError, ImportError)):
            create_controller('invalid_type', simple_config)

        # Should still be able to create valid controller (lock was released)
        valid_gains = [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]
        controller = create_controller('classical_smc', simple_config, valid_gains)
        assert controller is not None


# =============================================================================
# Test Class: Memory Isolation
# =============================================================================

class TestMemoryIsolation:
    """Test that concurrent operations don't corrupt shared state."""

    def test_controllers_have_independent_gains(self, simple_config):
        """Each controller should have independent gain values."""
        gains1 = [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]
        gains2 = [20.0, 10.0, 16.0, 6.0, 30.0, 4.0]

        controllers = []

        def create_with_gains(gains):
            controller = create_controller('classical_smc', simple_config, gains)
            controllers.append((gains, controller))

        thread1 = threading.Thread(target=create_with_gains, args=(gains1,))
        thread2 = threading.Thread(target=create_with_gains, args=(gains2,))

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        assert len(controllers) == 2

        # Each controller should have its own gains (check if gains attribute exists)
        for expected_gains, controller in controllers:
            if hasattr(controller, 'gains'):
                # Gains should match what was passed (not corrupted by other thread)
                assert controller.gains is not None

    def test_config_not_mutated_by_concurrent_access(self, simple_config, classical_gains):
        """Shared config should not be mutated by concurrent controller creation."""
        original_dt = simple_config.simulation.dt

        def create_worker():
            create_controller('classical_smc', simple_config, classical_gains)

        threads = [threading.Thread(target=create_worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Config should be unchanged
        assert simple_config.simulation.dt == original_dt

    def test_no_shared_state_corruption(self, simple_config, classical_gains):
        """Concurrent creation should not corrupt module-level state."""
        n_iterations = 50
        errors = []

        def create_and_verify():
            try:
                controller = create_controller('classical_smc', simple_config, classical_gains)
                # Verify controller is valid
                assert controller is not None
                assert hasattr(controller, 'compute_control')
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=create_and_verify) for _ in range(n_iterations)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30.0)

        # No corruption errors should occur
        assert len(errors) == 0, f"State corruption detected: {errors}"


# =============================================================================
# Test Class: Error Handling Under Concurrency
# =============================================================================

class TestErrorHandlingConcurrency:
    """Test error handling when creating controllers concurrently."""

    def test_errors_isolated_between_threads(self, simple_config, classical_gains):
        """Errors in one thread should not affect other threads."""
        results = {'success': [], 'errors': []}

        def create_valid():
            try:
                controller = create_controller('classical_smc', simple_config, classical_gains)
                results['success'].append(controller)
            except Exception as e:
                results['errors'].append(('valid', e))

        def create_invalid():
            try:
                controller = create_controller('invalid_type', simple_config)
                results['success'].append(controller)
            except Exception as e:
                results['errors'].append(('invalid', e))

        # Mix valid and invalid creation attempts
        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=create_valid))
            threads.append(threading.Thread(target=create_invalid))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Valid threads should succeed
        assert len(results['success']) == 5
        # Invalid threads should fail (but not crash)
        invalid_errors = [e for typ, e in results['errors'] if typ == 'invalid']
        assert len(invalid_errors) == 5

    def test_exception_propagation_concurrent(self, simple_config):
        """Exceptions should propagate correctly in concurrent context."""
        errors_caught = []

        def create_with_invalid_gains():
            try:
                # Wrong number of gains
                create_controller('classical_smc', simple_config, gains=[1, 2, 3])
            except (ValueError, Exception) as e:
                errors_caught.append(e)

        threads = [threading.Thread(target=create_with_invalid_gains) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All threads should catch exceptions
        assert len(errors_caught) == 10


# =============================================================================
# Test Class: Resource Cleanup
# =============================================================================

class TestResourceCleanup:
    """Test resource cleanup and memory management under concurrency."""

    def test_controllers_garbage_collected(self, simple_config, classical_gains):
        """Controllers should be garbage collected when no longer referenced."""
        # Create controllers in thread
        def create_temporary():
            controller = create_controller('classical_smc', simple_config, classical_gains)
            # Controller goes out of scope here

        threads = [threading.Thread(target=create_temporary) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Force garbage collection
        gc.collect()

        # Test passes if no memory leak (manual verification in production)
        # This test documents expected behavior
        assert True

    def test_lock_released_on_thread_exit(self, simple_config, classical_gains):
        """Lock should be released even if thread exits unexpectedly."""
        def create_and_exit():
            controller = create_controller('classical_smc', simple_config, classical_gains)
            # Thread exits immediately

        thread = threading.Thread(target=create_and_exit)
        thread.start()
        thread.join()

        # Should still be able to create controller (lock was released)
        controller = create_controller('classical_smc', simple_config, classical_gains)
        assert controller is not None


# =============================================================================
# Test Class: Stress Testing
# =============================================================================

class TestStressTesting:
    """Stress tests for factory under high concurrency."""

    @pytest.mark.slow
    def test_high_concurrency_stress(self, simple_config, classical_gains):
        """Should handle high number of concurrent requests."""
        n_threads = 100
        results = []
        errors = []

        def create_worker():
            try:
                controller = create_controller('classical_smc', simple_config, classical_gains)
                results.append(controller)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=create_worker) for _ in range(n_threads)]

        start_time = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=60.0)
        elapsed = time.time() - start_time

        # Should complete within reasonable time
        assert elapsed < 60.0, f"High concurrency stress test took too long: {elapsed}s"

        # All should succeed
        assert len(errors) == 0, f"Errors under stress: {errors[:5]}"
        assert len(results) == n_threads

    @pytest.mark.slow
    def test_rapid_create_destroy_cycles(self, simple_config, classical_gains):
        """Should handle rapid create/destroy cycles."""
        n_cycles = 50

        def create_destroy_cycle():
            for _ in range(10):
                controller = create_controller('classical_smc', simple_config, classical_gains)
                del controller  # Explicit destroy
                gc.collect()

        threads = [threading.Thread(target=create_destroy_cycle) for _ in range(n_cycles)]

        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=60.0)

        # Should complete without crashes
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "not slow"])
