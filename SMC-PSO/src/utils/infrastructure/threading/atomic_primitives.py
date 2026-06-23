#======================================================================================\\\
#================= src/utils/thread_safety/atomic_primitives.py =======================\\\
#======================================================================================\\\

"""
Thread-safe atomic primitives for production-safe concurrent operations.

Provides lock-free and lock-based atomic operations for counters, flags,
and collections that need thread-safe access without race conditions.

Production Safety:
- All operations guaranteed atomic via threading.Lock
- No race conditions on increment/decrement/set operations
- Minimal overhead for single-threaded use
- Compatible with Python's GIL but doesn't rely on it

Usage:
    counter = AtomicCounter(initial_value=0)
    counter.increment()  # Thread-safe
    value = counter.get()  # Thread-safe read

    flag = AtomicFlag(initial=False)
    flag.set(True)  # Thread-safe
    if flag.get():  # Thread-safe check
        pass
"""

import threading
from typing import Any, Dict, Optional, TypeVar, Generic


T = TypeVar('T')


class AtomicCounter:
    """
    Thread-safe atomic counter with increment/decrement operations.

    Uses a Lock to guarantee atomicity. While Python's GIL provides some
    protection for simple operations, explicit locking ensures correctness
    across all Python implementations and prevents subtle race conditions.

    Examples:
        >>> counter = AtomicCounter()
        >>> counter.increment()
        1
        >>> counter.increment(5)
        6
        >>> counter.decrement(2)
        4
        >>> counter.get()
        4
    """

    def __init__(self, initial_value: int = 0):
        """Initialize atomic counter with optional initial value.

        Parameters
        ----------
        initial_value : int
            Starting value for the counter (default: 0)
        """
        self._value = initial_value
        self._lock = threading.Lock()

    def increment(self, amount: int = 1) -> int:
        """Atomically increment counter and return new value.

        Parameters
        ----------
        amount : int
            Amount to increment by (default: 1)

        Returns
        -------
        int
            New value after increment
        """
        with self._lock:
            self._value += amount
            return self._value

    def decrement(self, amount: int = 1) -> int:
        """Atomically decrement counter and return new value.

        Parameters
        ----------
        amount : int
            Amount to decrement by (default: 1)

        Returns
        -------
        int
            New value after decrement
        """
        with self._lock:
            self._value -= amount
            return self._value

    def get(self) -> int:
        """Atomically read current value.

        Returns
        -------
        int
            Current counter value
        """
        with self._lock:
            return self._value

    def set(self, value: int) -> None:
        """Atomically set counter to new value.

        Parameters
        ----------
        value : int
            New value to set
        """
        with self._lock:
            self._value = value

    def compare_and_set(self, expected: int, new_value: int) -> bool:
        """Atomically compare current value and set if equal.

        This is a compare-and-swap (CAS) operation useful for lock-free algorithms.

        Parameters
        ----------
        expected : int
            Expected current value
        new_value : int
            Value to set if current equals expected

        Returns
        -------
        bool
            True if value was updated, False otherwise
        """
        with self._lock:
            if self._value == expected:
                self._value = new_value
                return True
            return False

    def reset(self) -> int:
        """Atomically reset counter to zero and return old value.

        Returns
        -------
        int
            Previous value before reset
        """
        with self._lock:
            old_value = self._value
            self._value = 0
            return old_value

    def __repr__(self) -> str:
        """String representation of counter."""
        return f"AtomicCounter(value={self.get()})"


class AtomicFlag:
    """
    Thread-safe boolean flag with atomic set/get operations.

    Useful for signaling between threads or tracking state that
    multiple threads need to check/modify safely.

    Examples:
        >>> flag = AtomicFlag(initial=False)
        >>> flag.set(True)
        >>> flag.get()
        True
        >>> flag.test_and_set()
        True
        >>> flag.clear()
        >>> flag.get()
        False
    """

    def __init__(self, initial: bool = False):
        """Initialize atomic flag.

        Parameters
        ----------
        initial : bool
            Initial flag state (default: False)
        """
        self._value = initial
        self._lock = threading.Lock()

    def set(self, value: bool = True) -> None:
        """Atomically set flag to specified value.

        Parameters
        ----------
        value : bool
            Value to set (default: True)
        """
        with self._lock:
            self._value = value

    def get(self) -> bool:
        """Atomically read current flag state.

        Returns
        -------
        bool
            Current flag value
        """
        with self._lock:
            return self._value

    def clear(self) -> None:
        """Atomically clear flag (set to False)."""
        with self._lock:
            self._value = False

    def test_and_set(self) -> bool:
        """Atomically read current value and set to True.

        Returns
        -------
        bool
            Previous value before setting to True
        """
        with self._lock:
            old_value = self._value
            self._value = True
            return old_value

    def compare_and_set(self, expected: bool, new_value: bool) -> bool:
        """Atomically compare and swap flag value.

        Parameters
        ----------
        expected : bool
            Expected current value
        new_value : bool
            Value to set if current equals expected

        Returns
        -------
        bool
            True if value was updated, False otherwise
        """
        with self._lock:
            if self._value == expected:
                self._value = new_value
                return True
            return False

    def __repr__(self) -> str:
        """String representation of flag."""
        return f"AtomicFlag(value={self.get()})"

    def __bool__(self) -> bool:
        """Allow flag to be used in boolean contexts."""
        return self.get()


class ThreadSafeDict(Generic[T]):
    """
    Thread-safe dictionary wrapper with atomic operations.

    Provides thread-safe access to dictionary operations. For complex
    multi-step operations, use the lock() context manager.

    Examples:
        >>> d = ThreadSafeDict()
        >>> d['key'] = 'value'
        >>> d.get('key')
        'value'
        >>> with d.lock():
        ...     # Multiple operations are atomic as a group
        ...     if 'key' in d:
        ...         d['key'] += '_modified'
    """

    def __init__(self, initial_dict: Optional[Dict[str, T]] = None):
        """Initialize thread-safe dictionary.

        Parameters
        ----------
        initial_dict : dict, optional
            Initial dictionary contents
        """
        self._dict: Dict[str, T] = initial_dict.copy() if initial_dict else {}
        self._lock = threading.RLock()  # Reentrant lock for nested operations

    def __getitem__(self, key: str) -> T:
        """Thread-safe dictionary get."""
        with self._lock:
            return self._dict[key]

    def __setitem__(self, key: str, value: T) -> None:
        """Thread-safe dictionary set."""
        with self._lock:
            self._dict[key] = value

    def __delitem__(self, key: str) -> None:
        """Thread-safe dictionary delete."""
        with self._lock:
            del self._dict[key]

    def __contains__(self, key: str) -> bool:
        """Thread-safe dictionary membership test."""
        with self._lock:
            return key in self._dict

    def __len__(self) -> int:
        """Thread-safe dictionary length."""
        with self._lock:
            return len(self._dict)

    def get(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """Thread-safe get with default.

        Parameters
        ----------
        key : str
            Dictionary key
        default : T, optional
            Default value if key not found

        Returns
        -------
        T or None
            Value for key, or default if not found
        """
        with self._lock:
            return self._dict.get(key, default)

    def set(self, key: str, value: T) -> None:
        """Thread-safe set (alias for __setitem__).

        Parameters
        ----------
        key : str
            Dictionary key
        value : T
            Value to store
        """
        with self._lock:
            self._dict[key] = value

    def setdefault(self, key: str, default: T) -> T:
        """Thread-safe setdefault operation.

        Parameters
        ----------
        key : str
            Dictionary key
        default : T
            Default value if key doesn't exist

        Returns
        -------
        T
            Existing value or newly set default
        """
        with self._lock:
            return self._dict.setdefault(key, default)

    def pop(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """Thread-safe pop operation.

        Parameters
        ----------
        key : str
            Dictionary key
        default : T, optional
            Default if key not found

        Returns
        -------
        T or None
            Popped value or default
        """
        with self._lock:
            return self._dict.pop(key, default)

    def keys(self):
        """Thread-safe keys view (returns copy)."""
        with self._lock:
            return list(self._dict.keys())

    def values(self):
        """Thread-safe values view (returns copy)."""
        with self._lock:
            return list(self._dict.values())

    def items(self):
        """Thread-safe items view (returns copy)."""
        with self._lock:
            return list(self._dict.items())

    def update(self, other: Dict[str, T]) -> None:
        """Thread-safe dictionary update.

        Parameters
        ----------
        other : dict
            Dictionary to merge in
        """
        with self._lock:
            self._dict.update(other)

    def clear(self) -> None:
        """Thread-safe dictionary clear."""
        with self._lock:
            self._dict.clear()

    def copy(self) -> Dict[str, T]:
        """Thread-safe dictionary copy.

        Returns
        -------
        dict
            Shallow copy of dictionary
        """
        with self._lock:
            return self._dict.copy()

    def lock(self):
        """Return lock for manual context management of complex operations.

        Returns
        -------
        threading.RLock
            The underlying reentrant lock

        Examples
        --------
        >>> d = ThreadSafeDict()
        >>> with d.lock():
        ...     # Multiple operations are atomic as a group
        ...     if 'counter' in d:
        ...         d['counter'] += 1
        ...     else:
        ...         d['counter'] = 1
        """
        return self._lock

    def __repr__(self) -> str:
        """String representation."""
        with self._lock:
            return f"ThreadSafeDict({self._dict})"
