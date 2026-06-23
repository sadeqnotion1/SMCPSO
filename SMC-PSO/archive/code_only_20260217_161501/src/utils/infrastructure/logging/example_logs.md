# Example Log Entries by Component

**Version:** 1.0
**Last Updated:** 2025-11-11

This document provides comprehensive examples of log entries for all major components in the DIP-SMC-PSO system.

---

## Table of Contents

1. [Classical SMC Controller](#1-classical-smc-controller)
2. [Super-Twisting SMC Controller](#2-super-twisting-smc-controller)
3. [Adaptive SMC Controller](#3-adaptive-smc-controller)
4. [Hybrid Adaptive STA-SMC Controller](#4-hybrid-adaptive-sta-smc-controller)
5. [Swing-Up SMC Controller](#5-swing-up-smc-controller)
6. [MPC Controller](#6-mpc-controller)
7. [PSO Optimizer](#7-pso-optimizer)
8. [Simulation Runner](#8-simulation-runner)
9. [Plant Models](#9-plant-models)
10. [HIL System](#10-hil-system)

---

## 1. Classical SMC Controller

### 1.1 Initialization

```json
{
  "timestamp": "2025-11-11T14:23:45.123456Z",
  "level": "INFO",
  "component": "Controller.ClassicalSMC",
  "event": "initialized",
  "data": {
    "gains": [10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
    "boundary_layer": 0.1,
    "n_states": 6,
    "saturation_limit": 50.0
  },
  "metadata": {
    "run_id": "abc123",
    "thread_id": "MainThread",
    "pid": 12345
  }
}
```

### 1.2 Control Computation (Normal)

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
    "chattering_metric": 0.15,
    "saturation_active": false
  },
  "duration_ms": 1.23,
  "metadata": {
    "run_id": "abc123",
    "iteration": 100,
    "thread_id": "MainThread"
  }
}
```

### 1.3 Control Computation (Saturation Active)

```json
{
  "timestamp": "2025-11-11T14:23:45.345678Z",
  "level": "WARNING",
  "component": "Controller.ClassicalSMC.compute_control",
  "event": "control_saturated",
  "data": {
    "state_norm": 0.15,
    "control_signal_requested": 65.3,
    "control_signal_actual": 50.0,
    "saturation_limit": 50.0,
    "sliding_surface": 0.15,
    "chattering_metric": 0.35
  },
  "duration_ms": 1.45,
  "metadata": {
    "run_id": "abc123",
    "iteration": 150,
    "thread_id": "MainThread"
  }
}
```

### 1.4 High Chattering Detected

```json
{
  "timestamp": "2025-11-11T14:23:45.456789Z",
  "level": "WARNING",
  "component": "Controller.ClassicalSMC.compute_control",
  "event": "high_chattering_detected",
  "data": {
    "chattering_metric": 0.85,
    "chattering_threshold": 0.5,
    "control_signal_variance": 25.3,
    "recommendation": "Consider increasing boundary layer"
  },
  "metadata": {
    "run_id": "abc123",
    "iteration": 200,
    "thread_id": "MainThread"
  }
}
```

### 1.5 Computation Error

```json
{
  "timestamp": "2025-11-11T14:23:45.567890Z",
  "level": "ERROR",
  "component": "Controller.ClassicalSMC.compute_control",
  "event": "computation_failed",
  "data": {
    "state_shape": [4],
    "expected_shape": [6]
  },
  "error": {
    "error_type": "ValueError",
    "error_message": "Invalid state vector dimension: expected 6, got 4",
    "traceback": [
      "Traceback (most recent call last):",
      "  File \"src/controllers/smc/classic_smc.py\", line 123, in compute_control",
      "    self._validate_state(state)",
      "ValueError: Invalid state vector dimension"
    ],
    "context": {
      "state": [0.1, 0.2, 0.05, 0.03]
    }
  },
  "metadata": {
    "run_id": "abc123",
    "iteration": 250,
    "thread_id": "MainThread"
  }
}
```

---

## 2. Super-Twisting SMC Controller

### 2.1 Initialization

```json
{
  "timestamp": "2025-11-11T14:25:00.000000Z",
  "level": "INFO",
  "component": "Controller.STASMC",
  "event": "initialized",
  "data": {
    "alpha": 1.5,
    "beta": 2.0,
    "lambda_param": 10.0,
    "n_states": 6
  },
  "metadata": {
    "run_id": "sta_run_001",
    "thread_id": "MainThread"
  }
}
```

### 2.2 Control Computation

```json
{
  "timestamp": "2025-11-11T14:25:00.123456Z",
  "level": "INFO",
  "component": "Controller.STASMC.compute_control",
  "event": "control_computed",
  "data": {
    "state_norm": 0.032,
    "control_signal": 18.5,
    "sliding_surface": 0.0015,
    "integral_term": 5.2,
    "proportional_term": 13.3,
    "chattering_metric": 0.05
  },
  "duration_ms": 1.56,
  "metadata": {
    "run_id": "sta_run_001",
    "iteration": 100,
    "thread_id": "MainThread"
  }
}
```

---

## 3. Adaptive SMC Controller

### 3.1 Initialization

```json
{
  "timestamp": "2025-11-11T14:26:00.000000Z",
  "level": "INFO",
  "component": "Controller.AdaptiveSMC",
  "event": "initialized",
  "data": {
    "initial_gains": [10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
    "adaptation_rate": 0.01,
    "gain_bounds": [[1.0, 50.0], [1.0, 30.0], [1.0, 50.0], [1.0, 30.0], [1.0, 50.0], [1.0, 30.0]],
    "boundary_layer": 0.1
  },
  "metadata": {
    "run_id": "adaptive_run_001",
    "thread_id": "MainThread"
  }
}
```

### 3.2 Gain Update

```json
{
  "timestamp": "2025-11-11T14:26:01.000000Z",
  "level": "INFO",
  "component": "Controller.AdaptiveSMC.update_gains",
  "event": "gains_updated",
  "data": {
    "old_gains": [10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
    "new_gains": [10.5, 5.2, 8.3, 3.1, 15.4, 2.1],
    "gain_deltas": [0.5, 0.2, 0.3, 0.1, 0.4, 0.1],
    "sliding_surface_norm": 0.025,
    "adaptation_triggered_by": "high_tracking_error"
  },
  "duration_ms": 0.85,
  "metadata": {
    "run_id": "adaptive_run_001",
    "iteration": 500,
    "thread_id": "MainThread"
  }
}
```

### 3.3 Gain Saturation

```json
{
  "timestamp": "2025-11-11T14:26:02.000000Z",
  "level": "WARNING",
  "component": "Controller.AdaptiveSMC.update_gains",
  "event": "gain_saturated",
  "data": {
    "gain_index": 0,
    "requested_gain": 55.0,
    "actual_gain": 50.0,
    "gain_limit": 50.0,
    "recommendation": "System may be underactuated or disturbance too large"
  },
  "metadata": {
    "run_id": "adaptive_run_001",
    "iteration": 750,
    "thread_id": "MainThread"
  }
}
```

---

## 4. Hybrid Adaptive STA-SMC Controller

### 4.1 Initialization

```json
{
  "timestamp": "2025-11-11T14:27:00.000000Z",
  "level": "INFO",
  "component": "Controller.HybridAdaptiveSTA",
  "event": "initialized",
  "data": {
    "alpha": 1.5,
    "beta": 2.0,
    "lambda_param": 10.0,
    "adaptation_rate": 0.01,
    "initial_gains": [10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
    "hybrid_mode": "adaptive_sta"
  },
  "metadata": {
    "run_id": "hybrid_run_001",
    "thread_id": "MainThread"
  }
}
```

### 4.2 Mode Switch

```json
{
  "timestamp": "2025-11-11T14:27:05.000000Z",
  "level": "INFO",
  "component": "Controller.HybridAdaptiveSTA",
  "event": "mode_switched",
  "data": {
    "old_mode": "classical_smc",
    "new_mode": "super_twisting",
    "reason": "high_chattering_detected",
    "chattering_metric": 0.75,
    "chattering_threshold": 0.5
  },
  "metadata": {
    "run_id": "hybrid_run_001",
    "iteration": 300,
    "thread_id": "MainThread"
  }
}
```

---

## 5. Swing-Up SMC Controller

### 5.1 Initialization

```json
{
  "timestamp": "2025-11-11T14:28:00.000000Z",
  "level": "INFO",
  "component": "Controller.SwingUpSMC",
  "event": "initialized",
  "data": {
    "energy_target": 15.0,
    "swing_up_gains": [5.0, 2.0],
    "stabilization_gains": [10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
    "switch_threshold": 0.2
  },
  "metadata": {
    "run_id": "swingup_run_001",
    "thread_id": "MainThread"
  }
}
```

### 5.2 Phase Transition

```json
{
  "timestamp": "2025-11-11T14:28:05.000000Z",
  "level": "INFO",
  "component": "Controller.SwingUpSMC",
  "event": "phase_transition",
  "data": {
    "old_phase": "swing_up",
    "new_phase": "stabilization",
    "energy": 14.8,
    "energy_target": 15.0,
    "angle_1": 3.05,
    "angle_2": 3.10,
    "time_in_swing_up": 5.23
  },
  "metadata": {
    "run_id": "swingup_run_001",
    "iteration": 523,
    "thread_id": "MainThread"
  }
}
```

---

## 6. MPC Controller

### 6.1 Initialization

```json
{
  "timestamp": "2025-11-11T14:29:00.000000Z",
  "level": "INFO",
  "component": "Controller.MPC",
  "event": "initialized",
  "data": {
    "prediction_horizon": 10,
    "control_horizon": 5,
    "Q_matrix_diag": [10.0, 10.0, 1.0, 1.0, 0.1, 0.1],
    "R_matrix_diag": [0.1],
    "solver": "quadprog"
  },
  "metadata": {
    "run_id": "mpc_run_001",
    "thread_id": "MainThread"
  }
}
```

### 6.2 Optimization Solved

```json
{
  "timestamp": "2025-11-11T14:29:01.000000Z",
  "level": "INFO",
  "component": "Controller.MPC.solve",
  "event": "optimization_solved",
  "data": {
    "cost": 12.34,
    "iterations": 15,
    "control_sequence": [15.3, 14.8, 14.2, 13.5, 12.9],
    "predicted_states_norm": [0.025, 0.020, 0.015, 0.010, 0.005]
  },
  "duration_ms": 8.45,
  "metadata": {
    "run_id": "mpc_run_001",
    "iteration": 100,
    "thread_id": "MainThread"
  }
}
```

### 6.3 Optimization Failed

```json
{
  "timestamp": "2025-11-11T14:29:02.000000Z",
  "level": "ERROR",
  "component": "Controller.MPC.solve",
  "event": "optimization_failed",
  "data": {
    "reason": "solver_timeout",
    "iterations": 100,
    "max_iterations": 100,
    "fallback_control": 15.0
  },
  "error": {
    "error_type": "SolverTimeoutError",
    "error_message": "Optimization did not converge within 100 iterations"
  },
  "duration_ms": 50.0,
  "metadata": {
    "run_id": "mpc_run_001",
    "iteration": 150,
    "thread_id": "MainThread"
  }
}
```

---

## 7. PSO Optimizer

### 7.1 Optimization Started

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
    "objective": "minimize_iae",
    "inertia_weight": 0.7,
    "cognitive_coeff": 1.5,
    "social_coeff": 1.5
  },
  "metadata": {
    "run_id": "pso_run_456",
    "thread_id": "MainThread"
  }
}
```

### 7.2 Generation Complete

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
    "best_params": [12.3, 8.9, 15.2, 7.8, 18.9, 4.5],
    "convergence_rate": 0.15
  },
  "duration_ms": 5123.45,
  "metadata": {
    "run_id": "pso_run_456",
    "thread_id": "MainThread"
  }
}
```

### 7.3 Stagnation Detected

```json
{
  "timestamp": "2025-11-11T14:32:00.000000Z",
  "level": "WARNING",
  "component": "Optimizer.PSO",
  "event": "stagnation_detected",
  "data": {
    "generation": 50,
    "best_fitness": 2.34,
    "fitness_improvement_last_10_gen": 0.02,
    "improvement_threshold": 0.05,
    "diversity": 0.08,
    "diversity_threshold": 0.1,
    "recommendation": "Consider restarting with different initial conditions"
  },
  "metadata": {
    "run_id": "pso_run_456",
    "thread_id": "MainThread"
  }
}
```

### 7.4 Optimization Complete

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
    "final_diversity": 0.05,
    "total_evaluations": 3750
  },
  "duration_ms": 300000.0,
  "metadata": {
    "run_id": "pso_run_456",
    "thread_id": "MainThread"
  }
}
```

---

## 8. Simulation Runner

### 8.1 Simulation Started

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
    "initial_state": [0.1, 0.2, 0.05, 0.03, 0.01, 0.02],
    "disturbances_enabled": true
  },
  "metadata": {
    "run_id": "sim_789",
    "thread_id": "MainThread"
  }
}
```

### 8.2 Simulation Step (Periodic)

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
    "energy": 0.123,
    "tracking_error_norm": 0.015
  },
  "duration_ms": 1.23,
  "metadata": {
    "run_id": "sim_789",
    "iteration": 100,
    "thread_id": "MainThread"
  }
}
```

### 8.3 Simulation Complete

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
    "max_overshoot": 0.15,
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

## 9. Plant Models

### 9.1 State Update

```json
{
  "timestamp": "2025-11-11T14:41:00.123456Z",
  "level": "DEBUG",
  "component": "Plant.FullNonlinearDynamics.update_state",
  "event": "state_updated",
  "data": {
    "old_state": [0.1, 0.2, 0.05, 0.03, 0.01, 0.02],
    "new_state": [0.095, 0.19, 0.048, 0.028, 0.009, 0.018],
    "control_input": 15.3,
    "disturbance": [0.01, 0.02],
    "dt": 0.01
  },
  "duration_ms": 0.56,
  "metadata": {
    "run_id": "sim_789",
    "iteration": 100,
    "thread_id": "MainThread"
  }
}
```

---

## 10. HIL System

### 10.1 HIL Server Started

```json
{
  "timestamp": "2025-11-11T14:50:00.000000Z",
  "level": "INFO",
  "component": "HIL.PlantServer",
  "event": "server_started",
  "data": {
    "host": "localhost",
    "port": 8080,
    "plant_type": "FullNonlinearDynamics",
    "dt": 0.01
  },
  "metadata": {
    "run_id": "hil_run_001",
    "thread_id": "MainThread",
    "pid": 12345
  }
}
```

### 10.2 HIL Client Connected

```json
{
  "timestamp": "2025-11-11T14:50:05.000000Z",
  "level": "INFO",
  "component": "HIL.ControllerClient",
  "event": "client_connected",
  "data": {
    "server_host": "localhost",
    "server_port": 8080,
    "controller_type": "ClassicalSMC"
  },
  "metadata": {
    "run_id": "hil_run_001",
    "thread_id": "MainThread",
    "pid": 12346
  }
}
```

### 10.3 HIL Communication Latency Warning

```json
{
  "timestamp": "2025-11-11T14:50:10.000000Z",
  "level": "WARNING",
  "component": "HIL.PlantServer",
  "event": "high_latency_detected",
  "data": {
    "latency_ms": 15.3,
    "latency_threshold_ms": 10.0,
    "dt_ms": 10.0,
    "recommendation": "Network latency exceeds control loop period"
  },
  "metadata": {
    "run_id": "hil_run_001",
    "iteration": 500,
    "thread_id": "MainThread"
  }
}
```

---

## Summary

This document provides 30+ example log entries covering:

1. **7 Controllers** (Classical SMC, STA-SMC, Adaptive, Hybrid, Swing-Up, MPC, Factory)
2. **PSO Optimizer** (start, generation, stagnation, completion)
3. **Simulation Runner** (start, step, completion)
4. **Plant Models** (state updates)
5. **HIL System** (server, client, latency)

Each example includes:
- Proper JSON structure per schema
- Realistic data values
- Appropriate log levels
- Complete metadata

**Status:** COMPLETE
**Checkpoint:** CHECKPOINT_1_2_1_EXAMPLES_COMPLETE
