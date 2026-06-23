# interfaces.hil.controller_client

**Source:** `src\interfaces\hil\controller_client.py`

## Module Overview

*No module docstring available.*


## Mathematical Foundation

### Remote Controller Execution

The client executes control law remotely with network delay:

```{math}
u(t) = \pi(\tilde{\vec{x}}(t - \tau))
```

Where:
- $\pi$: Controller policy (SMC, MPC, etc.)
- $\tilde{\vec{x}}$: Noisy state measurement from plant server
- $\tau$: Network latency (round-trip delay)

### Request-Response Cycle

Synchronous communication pattern:

```{math}
\begin{align}
t_0 &: \text{Send state request} \\
t_1 &= t_0 + \tau_{\text{req}}: \text{Receive state from server} \\
t_2 &= t_1 + \Delta t_{\text{compute}}: \text{Compute control} \\
t_3 &= t_2 + \tau_{\text{resp}}: \text{Send control to server}
\end{align}
```

**Timing Budget:**
```{math}
\tau_{\text{req}} + \Delta t_{\text{compute}} + \tau_{\text{resp}} < \Delta t_{\text{control}}
```

### Control Delay Effects

Delayed control input affects stability margins:

```{math}
\dot{\vec{x}}(t) = f(\vec{x}(t), u(t - \tau))
```

**Smith Predictor Compensation:**
```{math}
u(t) = \pi(\hat{\vec{x}}(t + \tau))
```

Where $\hat{\vec{x}}$ is predicted state accounting for delay.

### Fallback Controller

PD controller for emergency scenarios:

```{math}
u_{\text{fallback}} = -K_p \theta_1 - K_d \dot{\theta}_1
```

**Failover Conditions:**
1. Network timeout (>1 second)
2. Server connection lost
3. Controller computation failure

### Message Serialization

JSON-based state representation:

```json
{
  "state": [x, theta1, theta2, x_dot, theta1_dot, theta2_dot],
  "time": 0.123,
  "step": 123,
  "control": 12.5
}
```

**Serialization Performance:**
- Encode time: ~0.3 ms
- Decode time: ~0.2 ms
- Message size: ~150 bytes

### Client Architecture

**Event Loop Pattern:**
1. Request state from server
2. Wait for response (with timeout)
3. Compute control action
4. Send control to server
5. Log data and metrics
6. Repeat until simulation complete

**Error Recovery:**
- Retry policy: 3 attempts with exponential backoff
- Graceful degradation: Switch to fallback controller
- Clean shutdown: Save partial results on failure

## Architecture Diagram

```{mermaid}
graph TD
    A[Connect to Server] --> B[Initialize Controller]
    B --> C{Simulation Loop}
    C --> D[Request State]
    D --> E[Receive State]
    E --> F[Compute Control]
    F --> G[Send Control]
    G --> H[Log Data]
    H --> I{More Steps?}
    I -->|Yes| C
    I -->|No| J[Disconnect]
    J --> K[Save Results]

    E --> L{Timeout?}
    L -->|Yes| M[Fallback Controller]
    L -->|No| F
    M --> G

    F --> N[Controller Logic]
    N --> O[SMC/MPC/PID]

    style F fill:#9cf
    style M fill:#ff9
    style N fill:#f9f
    style K fill:#9f9
```

**Control Loop:**
1. Request current state from plant server
2. Wait for state response (with timeout)
3. Compute control action using controller
4. Send control input to server
5. Log data for analysis
6. Repeat until simulation complete

**Fault Tolerance:**
- Timeout detection: Switch to fallback PD controller
- Retry logic: 3 attempts with exponential backoff
- Graceful degradation: Save partial results on failure

## Usage Examples

### Example 1: Basic Controller Client

```python
from src.interfaces.hil import HILControllerClient
from src.config import load_config

# Load configuration
config = load_config("config.yaml")

# Connect to HIL server
client = HILControllerClient(
    cfg=config,
    plant_addr=("127.0.0.1", 5555),
    bind_addr=("127.0.0.1", 0),  # Auto-assign port
    dt=0.01,
    steps=5000,
    results_path="hil_results.json"
)

# Run HIL simulation
client.run()

print("HIL simulation complete, results saved to hil_results.json")
```

## Example 2: Custom Controller Integration

```python
from src.interfaces.hil import HILControllerClient
from src.controllers import ClassicalSMC

# Create custom controller
controller = ClassicalSMC(
    gains=[10, 8, 15, 12, 50, 5],
    max_force=100.0,
    boundary_layer=0.01
)

# Client with custom controller
client = HILControllerClient(
    cfg=config,
    plant_addr=("192.168.1.100", 5555),  # Remote server
    bind_addr=("0.0.0.0", 6666),
    dt=0.01,
    steps=10000
)

# Override controller
client._controller = controller

# Run simulation
client.run()
```

## Example 3: Fallback Controller Testing

```python
from src.interfaces.hil import HILControllerClient
import time

# Client with aggressive timeout
client = HILControllerClient(
    cfg=config,
    plant_addr=("127.0.0.1", 5555),
    bind_addr=("127.0.0.1", 0),
    dt=0.01,
    steps=5000,
    recv_timeout_s=0.5  # 500 ms timeout
)

# Monitor fallback activations
fallback_count = 0
original_run = client.run

def monitored_run():
    global fallback_count
    # Count timeout events
    try:
        original_run()
    except TimeoutError:
        fallback_count += 1
        print(f"Fallback controller activated: {fallback_count} times")

client.run = monitored_run
client.run()

print(f"Total fallback activations: {fallback_count}")
```

### Example 4: Latency Measurement

```python
from src.interfaces.hil import HILControllerClient
import time

# Latency tracking
latencies = []

# Override communication for measurement
original_send_receive = client._send_receive

def measured_send_receive(msg):
    start = time.time()
    result = original_send_receive(msg)
    latency = (time.time() - start) * 1000  # ms
    latencies.append(latency)
    return result

client._send_receive = measured_send_receive
client.run()

# Analyze latencies
print(f"Mean latency: {np.mean(latencies):.2f} ms")
print(f"P95 latency: {np.percentile(latencies, 95):.2f} ms")
print(f"P99 latency: {np.percentile(latencies, 99):.2f} ms")
```

## Example 5: Robust

Client with Retry Logic

```python
# example-metadata:
# runnable: false

from src.interfaces.hil import HILControllerClient
import time

def run_client_with_retry(max_retries=3):
    for attempt in range(max_retries):
        try:
            client = HILControllerClient(
                cfg=config,
                plant_addr=("127.0.0.1", 5555),
                bind_addr=("127.0.0.1", 0),
                dt=0.01,
                steps=5000
            )
            client.run()
            print(f"Success on attempt {attempt + 1}")
            return
        except ConnectionError as e:
            print(f"Connection failed (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

    print("All retry attempts failed")

run_client_with_retry()
```

## Complete Source Code

```{literalinclude} ../../../src/interfaces/hil/controller_client.py
:language: python
:linenos:
```



## Classes

### `_FallbackPDController`

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/controller_client.py
:language: python
:pyobject: _FallbackPDController
:linenos:
```

#### Methods (4)

##### `__init__(self)`

[View full source →](#method-_fallbackpdcontroller-__init__)

##### `initialize_state(self)`

[View full source →](#method-_fallbackpdcontroller-initialize_state)

##### `initialize_history(self)`

[View full source →](#method-_fallbackpdcontroller-initialize_history)

##### `compute_control(self, state, state_vars, history)`

[View full source →](#method-_fallbackpdcontroller-compute_control)



### `HILControllerClient`

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/controller_client.py
:language: python
:pyobject: HILControllerClient
:linenos:
```

#### Methods (2)

##### `__init__(self, cfg, plant_addr, bind_addr, dt, steps, results_path, loop_sleep, recv_timeout_s)`

[View full source →](#method-hilcontrollerclient-__init__)

##### `run(self)`

[View full source →](#method-hilcontrollerclient-run)



## Functions

### `_load_config(cfg_path)`

Prefer validated loading; fallback to YAML only if project loader unavailable.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/controller_client.py
:language: python
:pyobject: _load_config
:linenos:
```



### `_get(cfg, dotted, default)`

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/controller_client.py
:language: python
:pyobject: _get
:linenos:
```



### `_build_controller(cfg)`

Instantiate the configured controller or raise an error.

In earlier versions this function silently fell back to a built‑in
PD controller when the factory failed.  Such silent fallbacks can
obscure configuration errors (e.g., mis‑spelling a controller name)
and lead to unexpected behaviour.  We now raise a ``RuntimeError``
when the controller cannot be created.  Failing fast on
misconfiguration prevents experiments from silently using an
unintended controller.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/controller_client.py
:language: python
:pyobject: _build_controller
:linenos:
```



### `run_client(cfg_path, steps, results_path)`

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/controller_client.py
:language: python
:pyobject: run_client
:linenos:
```



### `main(argv)`

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/controller_client.py
:language: python
:pyobject: main
:linenos:
```



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import argparse`
- `import socket`
- `import struct`
- `import zlib`
- `import time`
- `from pathlib import Path`
- `from typing import Optional, Tuple`
- `import numpy as np`
