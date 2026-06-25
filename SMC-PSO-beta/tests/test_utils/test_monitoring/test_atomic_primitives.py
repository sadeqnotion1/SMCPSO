#======================================================================================
# tests/test_utils/test_monitoring/test_atomic_primitives.py
#======================================================================================
"""Unit tests for thread-safe atomic primitives (monitoring slice dependency)."""
import threading

from src.utils.infrastructure.threading import AtomicCounter, AtomicFlag, ThreadSafeDict


def test_counter_basic_ops():
    c = AtomicCounter()
    assert c.get() == 0
    assert c.increment() == 1
    assert c.increment(5) == 6
    assert c.decrement(2) == 4
    c.set(10)
    assert c.get() == 10
    assert c.reset() == 10
    assert c.get() == 0


def test_counter_compare_and_set():
    c = AtomicCounter(3)
    assert c.compare_and_set(3, 9) is True
    assert c.get() == 9
    assert c.compare_and_set(3, 100) is False
    assert c.get() == 9
    assert "AtomicCounter" in repr(c)


def test_counter_thread_safety():
    c = AtomicCounter()
    n_threads, per = 16, 5000

    def work():
        for _ in range(per):
            c.increment()

    threads = [threading.Thread(target=work) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert c.get() == n_threads * per


def test_flag():
    f = AtomicFlag()
    assert f.get() is False
    assert bool(f) is False
    f.set(True)
    assert f.get() is True
    assert f.test_and_set() is True
    f.clear()
    assert f.get() is False
    assert f.compare_and_set(False, True) is True
    assert f.get() is True


def test_threadsafe_dict():
    d = ThreadSafeDict()
    d['a'] = 1
    assert d['a'] == 1
    assert d.get('missing') is None
    assert d.get('missing', 7) == 7
    assert d.setdefault('b', 2) == 2
    assert d.setdefault('b', 99) == 2
    assert 'a' in d
    assert len(d) == 2
    assert sorted(d.keys()) == ['a', 'b']
    assert d.pop('a') == 1
    assert 'a' not in d
    d.update({'c': 3, 'd': 4})
    assert set(d.copy().keys()) == {'b', 'c', 'd'}
    with d.lock():
        d['e'] = 5
    assert d['e'] == 5
    d.clear()
    assert len(d) == 0
