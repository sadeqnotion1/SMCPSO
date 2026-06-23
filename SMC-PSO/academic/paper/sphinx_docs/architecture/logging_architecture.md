# Logging Architecture

**Version:** 1.0
**Status:** Production
**Last Updated:** 2025-11-11

## Executive Summary

This document defines the comprehensive structured logging architecture for the DIP-SMC-PSO project. The system provides JSON-based, machine-parseable, searchable logs with async I/O, rotation, and component-level configuration.

**Key Design Principles:**
- Structured JSON format for machine parseability
- Hierarchical component naming for filtering
- Context injection for rich debugging information
- Async writing to prevent blocking control loops
- Rotation strategies for long-running operations
- Performance-first design (sub-millisecond overhead)

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Log Format Specification](#log-format-specification)
3. [Component Hierarchy](#component-hierarchy)
4. [Context Injection](#context-injection)
5. [Async Writing](#async-writing)
6. [Rotation Strategy](#rotation-strategy)
7. [Log Levels](#log-levels)
8. [Integration Points](#integration-points)
9. [Example Logs](#example-logs)
10. [Performance Considerations](#performance-considerations)

---

## 1. Architecture Overview

### 1.1 System Design

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│  (Controllers, PSO, Simulation, Plant)                       │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                  StructuredLogger API                        │
│  - log_event(event_name, **data)                            │
│  - log_performance(operation, duration_ms)                   │
│  - log_exception(exception, context)                         │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    Formatters Layer                          │
│  - JSON Formatter (structured output)                        │
│  - Console Formatter (human-readable)                        │
│  - Metric Formatter (performance data)                       │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                     Handlers Layer                           │
│  - FileHandler (rotating files)                              │
│  - JSONHandler (structured JSON)                             │
│  - AsyncHandler (non-blocking I/O)                           │
│  - ConsoleHandler (real-time output)                         │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                      Storage Layer                           │
│  - .logs/test/controller_YYYY-MM-DD.log                      │
│  - .logs/pso/pso_YYYY-MM-DD.json                             │
│  - .logs/test/simulation_YYYY-MM-DD.log                      │
│  - Centralized via src/utils/logging/paths.py                │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Key Components

| Component | Responsibility | File Location |
|-----------|---------------|---------------|
| `StructuredLogger` | Main logging API | `src/utils/logging/structured_logger.py` |
| `Handlers` | Output destinations | `src/utils/logging/handlers.py` |
| `Formatters` | Log formatting | `src/utils/logging/formatters.py` |
| `Config` | Configuration management | `src/utils/logging/config.py` |
| `Schema` | JSON validation | `src/utils/logging/schema.json` |

---

## 2. Log Format Specification

### 2.1 Standard JSON Format

Every log entry follows this structure:

```json
{
  "timestamp": "2025-11-11T14:23:45.123456Z",
  "level": "INFO",
  "component": "Controller.ClassicalSMC",
  "event": "control_computed",
  "data": {
    "state_norm": 0.025,
    "control_signal": 15.3,
    "error": [0.01, 0.02, 0.005, 0.003],
    "sliding_surface": 0.0023
  },
  "duration_ms": 1.23,
  "metadata": {
    "run_id": "abc123",
    "iteration": 100,
    "thread_id": "MainThread"
  }
}
```

### 2.2 Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `timestamp` | ISO 8601 string | Yes | Precise event timestamp with microseconds |
| `level` | Enum | Yes | Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `component` | String | Yes | Hierarchical component path (dot-separated) |
| `event` | String | Yes | Event identifier (snake_case) |
| `data` | Object | No | Event-specific structured data |
| `duration_ms` | Float | No | Operation duration in milliseconds |
| `metadata` | Object | Yes | Contextual information (run_id, iteration, etc.) |

### 2.3 Console Format (Human-Readable)

For real-time monitoring, console output uses abbreviated format:

```
[2025-11-11 14:23:45.123] [INFO] [Controller.ClassicalSMC] control_computed: state_norm=0.025 u=15.3 (1.23ms)
```

---

## 3. Component Hierarchy

### 3.1 Naming Convention

Components follow hierarchical dot-separated naming:

```
Domain.SubDomain.Component.Method
```

**Examples:**
- `Controller.ClassicalSMC.compute_control`
- `Controller.AdaptiveSMC.update_gains`
- `Optimizer.PSO.evaluate_swarm`
- `Simulation.Runner.step`
- `Plant.FullModel.update_state`

### 3.2 Component Registry

| Component Path | Description | Log File |
|----------------|-------------|----------|
| `Controller.*` | All controllers | `.logs/test/controller_YYYY-MM-DD.log` |
| `Controller.ClassicalSMC` | Classical SMC | `.logs/test/controller_YYYY-MM-DD.log` |
| `Controller.AdaptiveSMC` | Adaptive SMC | `.logs/test/controller_YYYY-MM-DD.log` |
| `Controller.STASMC` | Super-twisting SMC | `.logs/test/controller_YYYY-MM-DD.log` |
| `Controller.HybridAdaptiveSTA` | Hybrid adaptive STA | `.logs/test/controller_YYYY-MM-DD.log` |
| `Controller.SwingUpSMC` | Swing-up controller | `.logs/test/controller_YYYY-MM-DD.log` |
| `Controller.MPC` | Model predictive controller | `.logs/test/controller_YYYY-MM-DD.log` |
| `Optimizer.PSO` | PSO optimization | `.logs/pso/pso_YYYY-MM-DD.json` |
| `Simulation.Runner` | Simulation execution | `.logs/test/simulation_YYYY-MM-DD.log` |
| `Plant.*` | Plant models | `.logs/test/plant_YYYY-MM-DD.log` |
| `HIL.PlantServer` | HIL plant server | `.logs/monitoring/hil_YYYY-MM-DD.log` |
| `HIL.ControllerClient` | HIL controller client | `logs/hil_YYYY-MM-DD.log` |

### 3.3 Filtering by Component

The hierarchical structure enables powerful filtering:

```python
# Get all controller logs
filter_component("Controller.*")

# Get specific controller logs
filter_component("Controller.ClassicalSMC")

# Get all optimization logs
filter_component("Optimizer.*")
```

---

## 4. Context Injection

### 4.1 Automatic Context

The logger automatically injects contextual information:

```python
{
  "metadata": {
    "run_id": "abc123",          # Unique simulation run ID
    "iteration": 100,            # Current iteration number
    "thread_id": "MainThread",   # Thread identifier
    "hostname": "research-01",   # Machine hostname
    "pid": 12345                 # Process ID
  }
}
```

### 4.2 Custom Context

Applications can inject custom context:

```python
logger = StructuredLogger("Controller.ClassicalSMC")

# Set global context for all subsequent logs
logger.set_context(
    controller_type="classical_smc",
    gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
    boundary_layer=0.1
)

# Context appears in all logs automatically
logger.log_event("control_computed", state_norm=0.025)
# Result includes: {"data": {...}, "metadata": {"controller_type": "classical_smc", ...}}
```

### 4.3 Temporary Context

Use context managers for temporary context:

```python
with logger.context(experiment="stability_test", trial=5):
    # All logs within this block include experiment and trial metadata
    logger.log_event("test_started")
    # ... test execution ...
    logger.log_event("test_completed")
```

---

## 5. Async Writing

### 5.1 Non-Blocking Design

Logging operations MUST NOT block control loops. Async writing ensures:
- Control loop timing unaffected (<0.1ms overhead)
- Logs buffered in memory queue
- Background thread writes to disk
- Automatic flush on critical events

### 5.2 Implementation

```python
# Async handler automatically queues logs
async_handler = AsyncHandler(
    base_handler=FileHandler("logs/controller.log"),
    queue_size=10000,
    flush_interval_ms=100
)

logger.add_handler(async_handler)

# log_event returns immediately (non-blocking)
logger.log_event("control_computed", state_norm=0.025)  # <0.1ms
```

### 5.3 Flush Guarantees

Automatic flush occurs on:
- ERROR or CRITICAL level logs (immediate flush)
- Every 100ms (periodic flush)
- Application shutdown (graceful flush)
- Manual `logger.flush()` call

---

## 6. Rotation Strategy

### 6.1 Daily Rotation

Log files rotate daily at midnight (local time):

```
.logs/test/controller_2025-11-11.log
.logs/test/controller_2025-11-12.log
.logs/test/controller_2025-11-13.log
```

### 6.2 Size-Based Rotation

If a log file exceeds 100MB, it rotates immediately:

```
.logs/test/controller_2025-11-11.log       (current)
.logs/archive/2025-11-11/controller.log.gz  (archived + compressed)
```
**Note:** Archival uses centralized `.logs/archive/YYYY-MM-DD/` structure (see `docs/guides/logs_migration_guide.md`)

### 6.3 Retention Policy

- Keep 30 days of logs (automatic cleanup)
- Archive older logs to `logs/archive/`
- Compress archived logs (gzip)

### 6.4 Configuration

```yaml
rotation:
  strategy: "daily_and_size"
  max_bytes: 104857600  # 100MB
  backup_count: 5
  retention_days: 30
  compress: true
```

---

## 7. Log Levels

### 7.1 Level Definitions

| Level | Value | Usage | Example |
|-------|-------|-------|---------|
| `DEBUG` | 10 | Detailed debugging information | Parameter updates, intermediate calculations |
| `INFO` | 20 | Normal operation events | Control computed, optimization started |
| `WARNING` | 30 | Warning conditions | High chattering, slow convergence |
| `ERROR` | 40 | Error conditions | Invalid state, computation failure |
| `CRITICAL` | 50 | Critical failure | System crash, safety violation |

### 7.2 Level Selection Guide

**When to use DEBUG:**
- Internal state changes
- Parameter adjustments
- Detailed algorithm steps
- Intermediate calculations

**When to use INFO:**
- Major operational events
- Successful completions
- Performance metrics
- Normal state transitions

**When to use WARNING:**
- Degraded performance
- Recoverable errors
- Boundary conditions
- Unusual but valid states

**When to use ERROR:**
- Computation failures
- Invalid inputs
- Recoverable failures
- Exception catches

**When to use CRITICAL:**
- System crashes
- Safety violations
- Unrecoverable errors
- Immediate shutdown needed

### 7.3 Per-Component Level Configuration

```yaml
log_levels:
  default: INFO
  components:
    Controller.*: DEBUG           # All controllers at DEBUG
    Controller.ClassicalSMC: INFO # Override for specific controller
    Optimizer.PSO: INFO
    Simulation.Runner: WARNING
```

---

## 8. Integration Points

### 8.1 Controller Integration

Every controller MUST log at these points:

**Initialization:**
```python
def __init__(self, gains, boundary_layer, ...):
    self.logger = StructuredLogger(f"Controller.{self.__class__.__name__}")
    self.logger.log_event("initialized",
                          gains=gains,
                          boundary_layer=boundary_layer)
```

**Control Computation:**
```python
def compute_control(self, state, last_control, history):
    start = time.perf_counter()

    # ... control computation ...

    duration_ms = (time.perf_counter() - start) * 1000
    self.logger.log_event("control_computed",
                          state_norm=np.linalg.norm(state),
                          control_signal=u,
                          error=error.tolist(),
                          sliding_surface=s,
                          duration_ms=duration_ms)
    return u
```

**Error Handling:**
```python
try:
    u = self._compute_control_internal(state)
except Exception as e:
    self.logger.log_exception(e, context={"state": state.tolist()})
    raise
```

### 8.2 PSO Optimizer Integration

**Optimization Start:**
```python
def optimize(self, objective_function):
    self.logger.log_event("pso_optimization_started",
                          num_particles=self.n_particles,
                          generations=self.max_gen,
                          bounds=self.bounds)
```

**Per-Generation:**
```python
def _generation_step(self, gen):
    # ... generation computation ...

    self.logger.log_event("pso_generation_complete",
                          generation=gen,
                          best_fitness=self.best_fitness,
                          avg_fitness=avg_fitness,
                          diversity=self._compute_diversity(),
                          duration_ms=gen_time_ms)
```

**Optimization Complete:**
```python
def optimize(self, objective_function):
    # ... optimization loop ...

    self.logger.log_event("pso_optimization_complete",
                          best_fitness=self.best_fitness,
                          best_params=self.best_params.tolist(),
                          total_duration_ms=total_time,
                          converged=self._check_convergence())
```

### 8.3 Simulation Runner Integration

**Run Start:**
```python
def run(self, controller, plant, duration):
    self.logger.log_event("simulation_started",
                          controller_type=controller.__class__.__name__,
                          plant_type=plant.__class__.__name__,
                          duration=duration)
```

**Step:**
```python
def step(self, state, t):
    # ... simulation step ...

    if t % 100 == 0:  # Log every 100 steps
        self.logger.log_event("simulation_step",
                              time=t,
                              state_norm=np.linalg.norm(state),
                              control_effort=np.linalg.norm(u))
```

**Run Complete:**
```python
def run(self, controller, plant, duration):
    # ... simulation loop ...

    self.logger.log_event("simulation_complete",
                          total_steps=total_steps,
                          final_state_norm=np.linalg.norm(state),
                          total_duration_ms=total_time)
```

---

## 9. Example Logs

### 9.1 Classical SMC Controller

**Initialization:**
```json
{
  "timestamp": "2025-11-11T14:23:45.123456Z",
  "level": "INFO",
  "component": "Controller.ClassicalSMC",
  "event": "initialized",
  "data": {
    "gains": [10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
    "boundary_layer": 0.1,
    "n_states": 6
  },
  "metadata": {
    "run_id": "abc123",
    "thread_id": "MainThread"
  }
}
```

**Control Computation:**
```json
{
  "timestamp": "2025-11-11T14:23:45.234567Z",
  "level": "INFO",
  "component": "Controller.ClassicalSMC.compute_control",
  "event": "control_computed",
  "data": {
    "state_norm": 0.025,
    "control_signal": 15.3,
    "error": [0.01, 0.02, 0.005, 0.003, 0.001, 0.002],
    "sliding_surface": 0.0023,
    "chattering_metric": 0.15
  },
  "duration_ms": 1.23,
  "metadata": {
    "run_id": "abc123",
    "iteration": 100,
    "thread_id": "MainThread"
  }
}
```

**Error Condition:**
```json
{
  "timestamp": "2025-11-11T14:23:45.345678Z",
  "level": "ERROR",
  "component": "Controller.ClassicalSMC.compute_control",
  "event": "computation_failed",
  "data": {
    "error_type": "ValueError",
    "error_message": "Invalid state vector dimension",
    "state_shape": [4],
    "expected_shape": [6]
  },
  "metadata": {
    "run_id": "abc123",
    "iteration": 150,
    "thread_id": "MainThread"
  }
}
```

### 9.2 PSO Optimizer

**Optimization Start:**
```json
{
  "timestamp": "2025-11-11T14:30:00.000000Z",
  "level": "INFO",
  "component": "Optimizer.PSO",
  "event": "pso_optimization_started",
  "data": {
    "num_particles": 50,
    "generations": 100,
    "bounds": [[0, 50], [0, 30], [0, 50], [0, 30], [0, 50], [0, 30]],
    "objective": "minimize_iae"
  },
  "metadata": {
    "run_id": "pso_run_456",
    "thread_id": "MainThread"
  }
}
```

**Generation Complete:**
```json
{
  "timestamp": "2025-11-11T14:30:05.123456Z",
  "level": "INFO",
  "component": "Optimizer.PSO",
  "event": "pso_generation_complete",
  "data": {
    "generation": 10,
    "best_fitness": 2.34,
    "avg_fitness": 5.67,
    "worst_fitness": 12.34,
    "diversity": 0.45,
    "best_params": [12.3, 8.9, 15.2, 7.8, 18.9, 4.5]
  },
  "duration_ms": 5123.45,
  "metadata": {
    "run_id": "pso_run_456",
    "thread_id": "MainThread"
  }
}
```

**Convergence Detected:**
```json
{
  "timestamp": "2025-11-11T14:35:00.000000Z",
  "level": "INFO",
  "component": "Optimizer.PSO",
  "event": "pso_optimization_complete",
  "data": {
    "best_fitness": 1.23,
    "best_params": [10.5, 7.2, 14.8, 6.9, 17.3, 3.8],
    "total_generations": 75,
    "converged": true,
    "convergence_criterion": "diversity_threshold",
    "final_diversity": 0.05
  },
  "duration_ms": 300000.0,
  "metadata": {
    "run_id": "pso_run_456",
    "thread_id": "MainThread"
  }
}
```

### 9.3 Simulation Runner

**Simulation Started:**
```json
{
  "timestamp": "2025-11-11T14:40:00.000000Z",
  "level": "INFO",
  "component": "Simulation.Runner",
  "event": "simulation_started",
  "data": {
    "controller_type": "ClassicalSMC",
    "plant_type": "FullNonlinearDynamics",
    "duration": 10.0,
    "dt": 0.01,
    "initial_state": [0.1, 0.2, 0.05, 0.03, 0.01, 0.02]
  },
  "metadata": {
    "run_id": "sim_789",
    "thread_id": "MainThread"
  }
}
```

**Simulation Step (periodic):**
```json
{
  "timestamp": "2025-11-11T14:40:01.000000Z",
  "level": "DEBUG",
  "component": "Simulation.Runner.step",
  "event": "simulation_step",
  "data": {
    "time": 1.0,
    "iteration": 100,
    "state_norm": 0.025,
    "control_effort": 15.3,
    "energy": 0.123
  },
  "duration_ms": 1.23,
  "metadata": {
    "run_id": "sim_789",
    "iteration": 100,
    "thread_id": "MainThread"
  }
}
```

**Simulation Complete:**
```json
{
  "timestamp": "2025-11-11T14:40:10.000000Z",
  "level": "INFO",
  "component": "Simulation.Runner",
  "event": "simulation_complete",
  "data": {
    "total_steps": 1000,
    "final_state_norm": 0.001,
    "settling_time": 5.23,
    "iae": 2.34,
    "tvr": 150.23,
    "success": true
  },
  "duration_ms": 10000.0,
  "metadata": {
    "run_id": "sim_789",
    "thread_id": "MainThread"
  }
}
```

---

## 10. Performance Considerations

### 10.1 Overhead Targets

| Operation | Target Overhead | Measurement |
|-----------|----------------|-------------|
| `log_event()` call | <0.1ms | Per-call latency |
| Async queue write | <0.01ms | Queue insertion time |
| Disk flush | <10ms | Background flush operation |
| Memory overhead | <10MB | Logger instance + queue |

### 10.2 Optimization Strategies

**Lazy Formatting:**
```python
# Don't format unless log level is enabled
if logger.is_enabled(DEBUG):
    logger.log_event("debug_info", data=expensive_computation())
```

**Sampling:**
```python
# Log every Nth iteration for high-frequency events
if iteration % 100 == 0:
    logger.log_event("simulation_step", state_norm=norm)
```

**Batch Logging:**
```python
# Accumulate logs and write in batches
with logger.batch_mode():
    for i in range(1000):
        logger.log_event("step", i=i)
# Batch written on exit
```

### 10.3 Performance Monitoring

The logging system monitors its own performance:

```json
{
  "timestamp": "2025-11-11T15:00:00.000000Z",
  "level": "INFO",
  "component": "Logging.Performance",
  "event": "performance_summary",
  "data": {
    "logs_written": 10000,
    "avg_latency_ms": 0.05,
    "max_latency_ms": 2.3,
    "queue_depth_avg": 50,
    "queue_depth_max": 500,
    "flush_count": 100,
    "flush_duration_ms_avg": 8.5
  }
}
```

---

## Summary

This logging architecture provides:

1. **Structured, machine-parseable logs** (JSON format)
2. **Hierarchical component organization** (easy filtering)
3. **Rich contextual information** (automatic + custom)
4. **Async, non-blocking I/O** (<0.1ms overhead)
5. **Intelligent rotation** (daily + size-based)
6. **Flexible log levels** (per-component configuration)
7. **Comprehensive integration** (all 7 controllers + PSO)
8. **Performance monitoring** (self-observing system)

The system is designed for:
- Real-time debugging during development
- Post-hoc analysis of experiments
- Performance profiling
- Error diagnosis
- Research reproducibility

**Next Steps:**
1. Implement core logging module (Task 1.2.2)
2. Integrate into controllers (Task 1.2.3)
3. Add PSO logging (Task 1.2.4)
4. Build analysis tools (Task 1.2.5)

---

**Document Status:** COMPLETE
**Checkpoint:** CHECKPOINT_1_2_1_DOCS_COMPLETE
