# E017: Memory Management and Performance

**Hosts**: Dr. Sarah Chen (Control Systems) & Alex Rivera (Software Engineering)

---

## Opening Hook

**Alex**: Picture this: It's 10 PM. You start an overnight PSO optimization—10 hours, 50 particles, thousands of simulations. You go home. Sleep soundly. Wake up excited to see the results.

**Sarah**: You check your computer. It's frozen. Blue screen. **Crashed at hour 9.**

**Alex**: Nine hours of computation—**gone**. What happened?

**Sarah**: RAM usage ballooned from 50 MB to 5 GB. The system ran out of memory and killed your process.

**Alex**: **Memory leak.** The controller was hoarding every state it ever saw. For nine hours straight. Until the system said "enough" and pulled the plug.

**Sarah**: Before fix:
```python
self.state_history = []
self.state_history.append(state)  # Grows forever!
```

After fix:
```python
from collections import deque
self.state_history = deque(maxlen=1000)  # Bounded circular buffer
```

**Alex**: This episode covers:
- **Memory leak detection**: Tools and techniques (tracemalloc, pytest)
- **Controller memory patterns**: Weakref, bounded buffers, cleanup methods
- **Performance profiling**: Finding memory hotspots
- **Production validation**: CA-02 audit results (100% passing)

**Sarah**: Let's make sure your controller doesn't eat all your RAM!

---

## The Problem: Memory Leaks in Controllers

**Sarah**: Let's start with a real example from our early development.

**Original implementation** (classical_smc.py, v0.1):
```python
class ClassicalSMC:
    def __init__(self, config):
        self.state_history = []  # Unbounded list!
        self.control_history = []
        self.sliding_surface_history = []

    def compute_control(self, state, last_control, history):
        # Compute control...
        self.state_history.append(state)  # Grows forever
        self.control_history.append(control)
        self.sliding_surface_history.append(s)
        return control
```

**Alex**: **What happens?**
- **10-second simulation**: 1000 timesteps, ~50 KB memory
- **100-second simulation**: 10,000 timesteps, ~500 KB memory
- **10-hour overnight experiment**: 3.6 million timesteps, **180 MB per controller!**
- **50 Monte Carlo runs**: 50 controllers × 180 MB = **9 GB RAM**

**Sarah**: System crashes with `MemoryError`. We lost 8 hours of overnight PSO optimization!

**Alex**: **The fix**:
```python
from collections import deque

class ClassicalSMC:
    def __init__(self, config):
        # Bounded circular buffers
        self.state_history = deque(maxlen=1000)  # Only last 1000 states
        self.control_history = deque(maxlen=1000)
        self.sliding_surface_history = deque(maxlen=1000)
```

**Sarah**: Now memory usage is **constant** - doesn't matter if you run for 1 hour or 100 hours!

---

## Memory Leak Detection: tracemalloc

**Alex**: Python's built-in `tracemalloc` module is our first line of defense against memory leaks.

**Example detection script**:
```python
import tracemalloc
from src.controllers.factory import create_controller

def test_memory_leak():
    tracemalloc.start()

    controller = create_controller('classical_smc', config=cfg)
    snapshot1 = tracemalloc.take_snapshot()

    # Run 10,000 iterations
    for i in range(10000):
        state = np.random.randn(6)
        control = controller.compute_control(state, 0.0, {})

    snapshot2 = tracemalloc.take_snapshot()

    # Compare snapshots
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    for stat in top_stats[:10]:
        print(stat)
```

**Output (BEFORE fix)**:
```
src/controllers/classical_smc.py:45: size=180 MiB (+180 MiB), count=3600000 (+3600000)
```

**Output (AFTER fix)**:
```
src/controllers/classical_smc.py:45: size=52 KiB (+0 KiB), count=1000 (+0)
```

**Sarah**: Notice the memory growth is **ZERO** after the fix!

---

## Controller Memory Patterns

**Alex**: We use 3 core patterns to prevent memory leaks:

### Pattern 1: Bounded Circular Buffers

**Use case**: Controllers that need recent history for derivative/integral terms.

**Implementation**:
```python
from collections import deque

class AdaptiveSMC:
    def __init__(self, config):
        # Only need last N samples
        self.error_history = deque(maxlen=10)  # For numerical derivative
        self.integral_history = deque(maxlen=100)  # For integral term
```

**Sarah**: **Why bounded?**
- Derivative: only need 2-10 samples for finite difference
- Integral: bounded buffer prevents windup
- No reason to store entire simulation history!

### Pattern 2: Weakref—The Sticky Note, Not the Leash

**Sarah**: Here's the problem: Controllers need to reference the dynamics object. But if you hold a **strong reference**, you create a circular dependency.

**Alex**: The controller points to dynamics. Dynamics points back to the controller. Neither can be garbage collected. They're stuck together like magnets.

**Sarah**: Solution? **Weakref**—a weak reference. Think of it like this:

**Alex**: A **strong reference** is a **leash**. You're holding the object. It can't go anywhere. Even if you're done with it, it stays in memory because **you're holding on**.

**Sarah**: A **weakref** is a **sticky note**. It says "the object is over there" without actually holding it. If the object gets deleted, the sticky note just says "object not found." You know **where** it was, but you're not **keeping it alive**.

**Bad approach (strong reference - the leash)**:
```python
class HybridAdaptiveSTA:
    def __init__(self, config, dynamics):
        self.dynamics = dynamics  # Strong reference - holding tight!
```

**Good approach (weakref - the sticky note)**:
```python
import weakref

class HybridAdaptiveSTA:
    def __init__(self, config, dynamics):
        self._dynamics_ref = weakref.ref(dynamics)  # Sticky note!

    @property
    def dynamics(self):
        dyn = self._dynamics_ref()  # Check if object still exists
        if dyn is None:
            raise RuntimeError("Dynamics object has been deleted")
        return dyn
```

**Alex**: **Why this matters:**
- When the simulation ends, dynamics can be garbage collected **immediately**
- No circular references—controller and dynamics can be freed independently
- CA-02 audit: 100% of controllers use the weakref pattern

**Sarah**: Sticky note, not a leash. Remember that!

### Pattern 3: Explicit Cleanup Methods

**Sarah**: All controllers implement `cleanup()` for deterministic resource release.

**Implementation**:
```python
class ClassicalSMC:
    def cleanup(self):
        """Release memory and resources."""
        self.state_history.clear()
        self.control_history.clear()
        self.sliding_surface_history.clear()
        if hasattr(self, '_dynamics_ref'):
            self._dynamics_ref = None
```

**Usage**:
```python
try:
    for t in range(num_steps):
        control = controller.compute_control(state, ...)
finally:
    controller.cleanup()  # Always cleanup, even on error!
```

**Alex**: We also use Python's context manager protocol:
```python
class ClassicalSMC:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

# Usage
with create_controller('classical_smc', config=cfg) as controller:
    pass  # cleanup() called automatically!
```

---

## Memory Testing with pytest

**Alex**: We have 11 dedicated memory management tests.

**Test 1: No memory leak during long simulation**
```python
import tracemalloc
import pytest

@pytest.mark.parametrize("controller_type", [
    "classical_smc", "sta_smc", "adaptive_smc"
])
def test_no_memory_leak_long_simulation(controller_type):
    """Verify memory doesn't grow during 10,000 iterations."""
    tracemalloc.start()

    controller = create_controller(controller_type, config=test_config)
    snapshot1 = tracemalloc.take_snapshot()

    for i in range(10000):
        state = np.random.randn(6)
        control = controller.compute_control(state, 0.0, {})

    snapshot2 = tracemalloc.take_snapshot()
    stats = snapshot2.compare_to(snapshot1, 'lineno')
    total_growth = sum(stat.size_diff for stat in stats)

    assert total_growth < 1_000_000, f"Memory leak: {total_growth / 1e6:.1f} MB growth"
    controller.cleanup()
```

**Test 2: Cleanup releases memory**
```python
def test_cleanup_releases_memory():
    """Verify cleanup() releases controller memory."""
    controller = create_controller('classical_smc', config=test_config)

    for i in range(1000):
        controller.compute_control(np.random.randn(6), 0.0, {})

    snapshot1 = tracemalloc.take_snapshot()
    controller.cleanup()
    snapshot2 = tracemalloc.take_snapshot()

    stats = snapshot2.compare_to(snapshot1, 'lineno')
    total_change = sum(stat.size_diff for stat in stats)
    assert total_change < 0, "cleanup() did not release memory"
```

**Sarah**: **Test results (CA-02 audit)**:
```
tests/test_integration/test_memory_management/ ..... [ 100%]
11 tests passed in 2.34s
```

All 11 memory management tests: **PASSING**

---

## Performance Benchmarks: CA-02 Audit Results

**Sarah**: Our comprehensive audit validated all performance requirements.

### Memory Usage Benchmarks

**Test**: 10-hour simulation (3.6 million timesteps)

```
Controller Type          Peak Memory    Growth Rate    Status
-------------------------------------------------------------------
Classical SMC            52 KB          0.0 KB/hour    [OK]
STA-SMC                  68 KB          0.0 KB/hour    [OK]
Adaptive SMC             94 KB          0.0 KB/hour    [OK]
Hybrid Adaptive STA      118 KB         0.0 KB/hour    [OK]
-------------------------------------------------------------------
ALL CONTROLLERS: ZERO memory growth
```

**Alex**: **Zero growth rate** equals no memory leaks!

### CPU Performance Benchmarks

**Test**: Control computation time (1000 samples)

```
Controller Type          Mean Time    95th %ile    Max Time    Status
------------------------------------------------------------------------
Classical SMC            23 μs        28 μs        34 μs       [OK]
STA-SMC                  31 μs        38 μs        45 μs       [OK]
Adaptive SMC             47 μs        56 μs        67 μs       [OK]
Hybrid Adaptive STA      62 μs        74 μs        89 μs       [OK]
------------------------------------------------------------------------
ALL CONTROLLERS: < 100 μs (within 10 ms deadline)
```

**Sarah**: **Fastest**: Classical SMC (23 μs) - simplest algorithm
**Slowest**: Hybrid Adaptive STA (62 μs) - still **600× faster than deadline**!

---

## Garbage Collection: Taking Out the Trash (On Your Schedule)

**Alex**: Python's garbage collector—**GC** for short—is like a janitor for your computer's memory.

**Sarah**: When objects are no longer needed, the GC **takes out the trash**. Frees up memory. Keeps things clean.

**Alex**: But here's the problem: The janitor comes by **randomly**. And when they show up, they **stop everything** to clean. For 10 to 50 milliseconds!

### Problem: The Janitor Shows Up at the Worst Time

**Sarah**: You're running a real-time control loop. Deadline: 10 milliseconds. Everything's humming along smoothly—controller computes in 60 microseconds. Then, randomly, at iteration 734...

**Alex**: **The janitor shows up.** Garbage collection kicks in. Takes 45 milliseconds. **You miss the deadline.** Your control loop stutters. In a real robot, the pendulum might fall.

**Before tuning**:
```python
for t in range(num_steps):
    control = controller.compute_control(state, ...)
    # Random GC pauses every ~700 iterations (10-50 ms!)
```

### Solution: Take Out the Trash on YOUR Schedule

**Sarah**: We don't want the janitor showing up randomly. We want them on **our schedule**. During breaks. When it's safe.

**Alex**: So we **disable automatic garbage collection** during the critical real-time loop. Then we **manually trigger it** every 1,000 iterations—when we know we have time.

```python
import gc

gc.disable()  # Janitor takes a break—we'll call you when we need you

try:
    for t in range(num_steps):
        control = controller.compute_control(state, ...)

        # Manual GC every 1000 iterations—trash day!
        if t % 1000 == 0:
            gc.collect()  # Take out the trash NOW
finally:
    gc.enable()  # Re-enable automatic GC after loop ends
```

**Sarah**: Now garbage collection happens **predictably** every 1,000 iterations. No surprises. No missed deadlines.

**Alex**: **The results:**
- **Before**: 99th percentile latency = 45 ms (random GC pauses killed us)
- **After**: 99th percentile latency = 89 μs (no pauses in the control loop!)

**Sarah**: We went from **missing deadlines** to being **500× faster than the deadline**. All by controlling **when** the trash gets taken out.

---

## Summary: Three Patterns That Prevent Memory Nightmares

**Sarah**: Remember the opening story? Nine hours of computation lost to a memory leak. Let's make sure that **never** happens to you.

**Alex**: Three simple patterns prevent 99% of memory problems:

### Pattern 1: Bounded Buffers (Not Infinite Lists)

**Sarah**: **Bad**: `self.history = []` — grows forever, eats all your RAM

**Alex**: **Good**: `self.history = deque(maxlen=1000)` — fixed size, constant memory

**Sarah**: You don't need the entire simulation history. You need the **last N samples**. Bound it. Move on.

### Pattern 2: Weakrefs (Sticky Notes, Not Leashes)

**Alex**: **Bad**: `self.dynamics = dynamics` — strong reference, can't be garbage collected

**Sarah**: **Good**: `self._dynamics_ref = weakref.ref(dynamics)` — weak reference, garbage collectable

**Alex**: A sticky note says "object is over there" without holding it hostage. When the simulation ends, memory gets freed **immediately**.

### Pattern 3: Manual Garbage Collection (Your Schedule, Not Python's)

**Sarah**: **Bad**: Let Python's GC run randomly—45 ms pauses kill real-time deadlines

**Alex**: **Good**: `gc.disable()` during critical loops, `gc.collect()` at safe points every 1,000 iterations

**Sarah**: Take out the trash on **your** schedule. Not when the janitor randomly shows up.

---

**Alex**: **The proof these patterns work**—CA-02 audit results:
- **Memory leak tests**: 11 out of 11 passing
- **Memory growth rate**: 0.0 KB per hour (all 4 controllers)
- **Peak memory**: 52–118 KB (constant, bounded)
- **CPU performance**: 23–62 microseconds (600× faster than deadline)

**Sarah**: **Production readiness:**
- Thread-safe: 100%
- Memory-safe: 100% (zero leaks, zero growth)
- Real-time capable: Yes (under 100 microseconds)

**Alex**: These three patterns let your controller run for **days, weeks, months** without eating RAM. No crashes. No leaks. No surprises.

**Sarah**: Bounded buffers. Sticky notes. Scheduled trash day. **Remember these, and you'll never lose nine hours of computation again.**

---

## Resources

- **Repository:** https://github.com/theSadeQ/dip-smc-pso.git
- **Documentation:** `docs/` directory
- **Getting Started:** `docs/guides/getting-started.md`
- **Memory Management Guide:** `.ai_workspace/config/controller_memory.md`
- **CA-02 Audit Report:** `academic/dev/quality/CA-02_comprehensive_audit.md`

---

*Educational podcast episode generated from comprehensive presentation materials*
