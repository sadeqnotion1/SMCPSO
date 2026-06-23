#======================================================================================\\\
#========== tests/test_utils/test_thread_safety/test_atomic_primitives.py =============\\\
#======================================================================================\\\

"""
Tests for thread-safe atomic primitives.

Tests cover:
- Single-threaded correctness
- Multi-threaded race condition prevention
- Performance characteristics
- Edge cases
"""

import pytest
import threading
import time
from src.utils.infrastructure.threading import AtomicCounter, AtomicFlag, ThreadSafeDict


class TestAtomicCounter:
    """Tests for AtomicCounter class."""

    def test_initial_value(self):
        """Test counter initialization with default and custom values."""
        counter_default = AtomicCounter()
        assert counter_default.get() == 0

        counter_custom = AtomicCounter(initial_value=42)
        assert counter_custom.get() == 42

    def test_increment_single_thread(self):
        """Test increment in single-threaded context."""
        counter = AtomicCounter()

        result = counter.increment()
        assert result == 1
        assert counter.get() == 1

        result = counter.increment(5)
        assert result == 6
        assert counter.get() == 6

    def test_decrement_single_thread(self):
        """Test decrement in single-threaded context."""
        counter = AtomicCounter(10)

        result = counter.decrement()
        assert result == 9
        assert counter.get() == 9

        result = counter.decrement(5)
        assert result == 4
        assert counter.get() == 4

    def test_set_and_get(self):
        """Test setting and getting counter value."""
        counter = AtomicCounter()
        counter.set(100)
        assert counter.get() == 100

    def test_reset(self):
        """Test resetting counter to zero."""
        counter = AtomicCounter(50)
        old_value = counter.reset()
        assert old_value == 50
        assert counter.get() == 0

    def test_compare_and_set_success(self):
        """Test successful compare-and-set operation."""
        counter = AtomicCounter(10)
        success = counter.compare_and_set(10, 20)
        assert success is True
        assert counter.get() == 20

    def test_compare_and_set_failure(self):
        """Test failed compare-and-set when value doesn't match."""
        counter = AtomicCounter(10)
        success = counter.compare_and_set(15, 20)
        assert success is False
        assert counter.get() == 10  # Unchanged

    def test_concurrent_increments(self):
        """Test that concurrent increments are atomic (no race conditions)."""
        counter = AtomicCounter()
        num_threads = 10
        increments_per_thread = 1000

        def worker():
            for _ in range(increments_per_thread):
                counter.increment()

        threads = [threading.Thread(target=worker) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        expected = num_threads * increments_per_thread
        assert counter.get() == expected, \
            f"Race condition detected: expected {expected}, got {counter.get()}"

    def test_concurrent_mixed_operations(self):
        """Test mixed increments and decrements concurrently."""
        counter = AtomicCounter(5000)
        num_threads = 10
        operations_per_thread = 500

        def incrementer():
            for _ in range(operations_per_thread):
                counter.increment()

        def decrementer():
            for _ in range(operations_per_thread):
                counter.decrement()

        inc_threads = [threading.Thread(target=incrementer) for _ in range(num_threads // 2)]
        dec_threads = [threading.Thread(target=decrementer) for _ in range(num_threads // 2)]
        all_threads = inc_threads + dec_threads

        for t in all_threads:
            t.start()
        for t in all_threads:
            t.join()

        # Result should be initial value + (inc - dec)
        expected = 5000 + (num_threads // 2) * operations_per_thread - (num_threads // 2) * operations_per_thread
        assert counter.get() == expected

    def test_repr(self):
        """Test string representation."""
        counter = AtomicCounter(42)
        assert "42" in repr(counter)


class TestAtomicFlag:
    """Tests for AtomicFlag class."""

    def test_initial_state(self):
        """Test flag initialization."""
        flag_false = AtomicFlag()
        assert flag_false.get() is False

        flag_true = AtomicFlag(initial=True)
        assert flag_true.get() is True

    def test_set_and_get(self):
        """Test setting and getting flag state."""
        flag = AtomicFlag()
        flag.set(True)
        assert flag.get() is True

        flag.set(False)
        assert flag.get() is False

    def test_clear(self):
        """Test clearing flag."""
        flag = AtomicFlag(initial=True)
        flag.clear()
        assert flag.get() is False

    def test_test_and_set(self):
        """Test test-and-set operation."""
        flag = AtomicFlag(initial=False)
        old_value = flag.test_and_set()
        assert old_value is False
        assert flag.get() is True

        old_value = flag.test_and_set()
        assert old_value is True
        assert flag.get() is True

    def test_compare_and_set_success(self):
        """Test successful compare-and-set."""
        flag = AtomicFlag(initial=False)
        success = flag.compare_and_set(False, True)
        assert success is True
        assert flag.get() is True

    def test_compare_and_set_failure(self):
        """Test failed compare-and-set."""
        flag = AtomicFlag(initial=True)
        success = flag.compare_and_set(False, True)
        assert success is False
        assert flag.get() is True  # Unchanged

    def test_boolean_context(self):
        """Test using flag in boolean context."""
        flag = AtomicFlag(initial=True)
        assert flag  # Should evaluate to True

        flag.clear()
        assert not flag  # Should evaluate to False

    def test_concurrent_test_and_set(self):
        """Test that only one thread wins test-and-set race."""
        flag = AtomicFlag(initial=False)
        winners = []

        def racer(thread_id):
            old_value = flag.test_and_set()
            if not old_value:  # Was False before setting to True
                winners.append(thread_id)

        threads = [threading.Thread(target=racer, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Only one thread should have won the race
        assert len(winners) == 1
        assert flag.get() is True

    def test_repr(self):
        """Test string representation."""
        flag = AtomicFlag(initial=True)
        assert "True" in repr(flag)


class TestThreadSafeDict:
    """Tests for ThreadSafeDict class."""

    def test_initial_empty(self):
        """Test initialization with empty dict."""
        d = ThreadSafeDict()
        assert len(d) == 0

    def test_initial_with_data(self):
        """Test initialization with initial data."""
        initial = {'a': 1, 'b': 2}
        d = ThreadSafeDict(initial_dict=initial)
        assert len(d) == 2
        assert d['a'] == 1
        assert d['b'] == 2

    def test_set_and_get(self):
        """Test setting and getting values."""
        d = ThreadSafeDict()
        d['key'] = 'value'
        assert d['key'] == 'value'
        assert d.get('key') == 'value'

    def test_get_with_default(self):
        """Test get with default value."""
        d = ThreadSafeDict()
        assert d.get('missing', 'default') == 'default'

    def test_contains(self):
        """Test membership testing."""
        d = ThreadSafeDict()
        d['key'] = 'value'
        assert 'key' in d
        assert 'missing' not in d

    def test_delete(self):
        """Test deleting keys."""
        d = ThreadSafeDict()
        d['key'] = 'value'
        del d['key']
        assert 'key' not in d

    def test_setdefault(self):
        """Test setdefault operation."""
        d = ThreadSafeDict()
        result = d.setdefault('key', 'default')
        assert result == 'default'
        assert d['key'] == 'default'

        result = d.setdefault('key', 'other')
        assert result == 'default'  # Unchanged

    def test_pop(self):
        """Test pop operation."""
        d = ThreadSafeDict()
        d['key'] = 'value'
        result = d.pop('key')
        assert result == 'value'
        assert 'key' not in d

        result = d.pop('missing', 'default')
        assert result == 'default'

    def test_keys_values_items(self):
        """Test keys, values, and items methods."""
        d = ThreadSafeDict(initial_dict={'a': 1, 'b': 2})
        assert set(d.keys()) == {'a', 'b'}
        assert set(d.values()) == {1, 2}
        assert set(d.items()) == {('a', 1), ('b', 2)}

    def test_update(self):
        """Test update operation."""
        d = ThreadSafeDict(initial_dict={'a': 1})
        d.update({'b': 2, 'c': 3})
        assert len(d) == 3
        assert d['b'] == 2
        assert d['c'] == 3

    def test_clear(self):
        """Test clearing dictionary."""
        d = ThreadSafeDict(initial_dict={'a': 1, 'b': 2})
        d.clear()
        assert len(d) == 0

    def test_copy(self):
        """Test copying dictionary."""
        d = ThreadSafeDict(initial_dict={'a': 1, 'b': 2})
        copy = d.copy()
        assert copy == {'a': 1, 'b': 2}
        copy['c'] = 3
        assert 'c' not in d  # Original unchanged

    def test_lock_context(self):
        """Test using lock for atomic multi-step operations."""
        d = ThreadSafeDict()

        with d.lock():
            if 'counter' not in d:
                d['counter'] = 0
            d['counter'] += 1

        assert d['counter'] == 1

    def test_concurrent_updates(self):
        """Test concurrent dictionary updates."""
        d = ThreadSafeDict()
        num_threads = 10
        updates_per_thread = 100

        def worker(thread_id):
            for i in range(updates_per_thread):
                key = f"thread_{thread_id}_item_{i}"
                d[key] = thread_id

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have all keys
        expected_keys = num_threads * updates_per_thread
        assert len(d) == expected_keys

    def test_concurrent_increment(self):
        """Test atomic counter increment using lock."""
        d = ThreadSafeDict(initial_dict={'counter': 0})
        num_threads = 10
        increments_per_thread = 1000

        def worker():
            for _ in range(increments_per_thread):
                with d.lock():
                    d['counter'] += 1

        threads = [threading.Thread(target=worker) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        expected = num_threads * increments_per_thread
        assert d['counter'] == expected


# Performance benchmarks (not run by default)
@pytest.mark.slow
@pytest.mark.benchmark
class TestPerformance:
    """Performance tests for atomic primitives."""

    def test_atomic_counter_overhead(self):
        """Measure overhead of AtomicCounter vs plain int."""
        iterations = 100000

        # Plain int
        start = time.perf_counter()
        x = 0
        for _ in range(iterations):
            x += 1
        plain_time = time.perf_counter() - start

        # AtomicCounter
        start = time.perf_counter()
        counter = AtomicCounter()
        for _ in range(iterations):
            counter.increment()
        atomic_time = time.perf_counter() - start

        # Atomic should be slower but reasonable (< 10x overhead)
        overhead = atomic_time / plain_time
        assert overhead < 10, f"AtomicCounter overhead too high: {overhead:.2f}x"
        print(f"\\nAtomicCounter overhead: {overhead:.2f}x (plain: {plain_time*1000:.2f}ms, atomic: {atomic_time*1000:.2f}ms)")
