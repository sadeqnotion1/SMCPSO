# Controller Memory Management Quick Reference

**Quick guide for developers using DIP-SMC-PSO controllers**



## The 3 Golden Rules

1. **Short-lived controllers:** No action needed (automatic cleanup via `__del__`)
2. **Long-running controllers:** Call `history = controller.initialize_history()` periodically (every hour)
3. **Batch operations:** Call `controller.cleanup()` + `del controller` + `gc.collect()` every 100 iterations



## Pattern Quick Reference

### Pattern 1: Single Simulation (Simple)

```python
from src.controllers.smc import ClassicalSMC

controller = ClassicalSMC(
    gains=[10, 8, 15, 12, 50, 5],
    max_force=100,
    boundary_layer=0.01
)
result = simulate(controller, duration=5.0)
# Done - automatic cleanup
```

## Pattern 2: Server Deployment (Production)

```python
from src.controllers.smc import HybridAdaptiveSTASMC
import gc
import time

controller = HybridAdaptiveSTASMC(
    gains=[15, 12, 18, 15],
    dt=0.01,
    max_force=100,
    k1_init=10,
    k2_init=8,
    gamma1=0.5,
    gamma2=0.5,
    dead_zone=0.01
)

history = controller.initialize_history()
state_vars = controller.initialize_state()
last_cleanup = time.time()

while running:
    control, state_vars, history = controller.compute_control(state, state_vars, history)

    # Hourly cleanup
    if time.time() - last_cleanup > 3600:
        history = controller.initialize_history()
        gc.collect()
        last_cleanup = time.time()

    # Memory monitoring (optional)
    memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
    if memory_mb > 500:
        logger.warning(f"High memory usage: {memory_mb:.1f}MB")
        history = controller.initialize_history()
        gc.collect()
```

### Pattern 3: PSO Optimization (Batch)

```python
from src.controllers.smc import AdaptiveSMC
import gc

for i in range(10000):
    controller = AdaptiveSMC(
        gains=candidates[i],
        dt=0.01,
        max_force=100,
        k1_init=10,
        k2_init=8,
        gamma1=0.5,
        gamma2=0.5,
        dead_zone=0.01
    )
    fitness[i] = evaluate(controller)

    if i % 100 == 99:
        controller.cleanup()
        del controller
        gc.collect()
```



## Memory Monitoring

### Quick Check

```python
import psutil
import os

process = psutil.Process(os.getpid())
memory_mb = process.memory_info().rss / 1024 / 1024
print(f"Memory usage: {memory_mb:.1f}MB")
```

### Production Monitor

```python
# example-metadata:
# runnable: false

class MemoryMonitor:
    def __init__(self, threshold_mb=500):
        self.threshold_mb = threshold_mb
        self.process = psutil.Process(os.getpid())

    def check(self):
        memory_mb = self.process.memory_info().rss / 1024 / 1024
        if memory_mb > self.threshold_mb:
            return f"Memory alert: {memory_mb:.1f}MB > {self.threshold_mb}MB"
        return None

monitor = MemoryMonitor(threshold_mb=500)
if alert := monitor.check():
    logger.warning(alert)
    # Take action: clear history, reset controller, etc.
```



## Validation Command

```bash
# Quick memory leak test (1000 instantiations)
pytest tests/test_integration/test_memory_management/test_memory_resource_deep.py::TestMemoryUsage::test_memory_leak_detection -v

# 8-hour stress test
pytest tests/test_integration/test_memory_management/ -m stress -v

# All memory tests
pytest tests/test_integration/test_memory_management/ -v
```



## Controller-Specific Notes

### ClassicalSMC

- **Memory:** ~1KB per instance
- **Cleanup:** Automatic (stateless)
- **History:** External tracking only

### HybridAdaptiveSTASMC

- **Memory:** ~5KB per instance
- **Cleanup:** Clear history hourly
- **History:** Tracks k1, k2, u_int, s

### AdaptiveSMC

- **Memory:** ~4KB per instance
- **Cleanup:** Clear gain history hourly
- **History:** Tracks adaptive gains

### STASMC

- **Memory:** ~2KB per instance
- **Cleanup:** Reset integral state hourly
- **History:** Tracks u_int, s



## Common Issues

### Issue: Memory grows despite cleanup

**Solution:** Check external history tracking
```python
# Clear history dict periodically
if iteration % 1000 == 999:
    history = controller.initialize_history()
```

## Issue: PSO optimization OOM

**Solution:** Cleanup every 100 evaluations
```python
if i % 100 == 99:
    controller.cleanup()
    del controller
    gc.collect()
```

### Issue: Long server runs crash

**Solution:** Hourly cleanup + monitoring
```python
if time.time() - last_cleanup > 3600:
    history = controller.initialize_history()
    gc.collect()
```



## Need Help?

- **Full guide:** `docs/memory_management_patterns.md`
- **Test examples:** `tests/test_integration/test_memory_management/test_memory_resource_deep.py`
- **Issue tracker:** GitHub Issue #15 (CRIT-006)



**Last Updated:** 2025-10-01
