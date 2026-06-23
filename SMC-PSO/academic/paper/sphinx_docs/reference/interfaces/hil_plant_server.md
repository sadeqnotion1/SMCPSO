# interfaces.hil.plant_server

**Source:** `src\interfaces\hil\plant_server.py`

## Module Overview

*No module docstring available.*


## Mathematical Foundation

### Real-Time Dynamics Simulation

The plant server runs high-fidelity dynamics simulation with real-time constraints:

```{math}
\dot{\vec{x}}(t) = f(\vec{x}(t), u(t))
```

Where:
- $\vec{x} \in \mathbb{R}^6$: Full state (cart position, pendulum angles, velocities)
- $u \in \mathbb{R}$: Control input from remote controller
- $f$: Nonlinear dynamics function with all coupling effects

### Communication Protocol

TCP socket communication with message framing:

```{math}
\text{Message} = \text{Header}(\text{size}, \text{type}) || \text{Payload}(\vec{x}, t)
```

**Message Format:**
1. **Header**: 8 bytes (4-byte size + 4-byte type)
2. **Payload**: State vector + timestamp (56 bytes)
3. **Total**: 64 bytes per message

### Latency Model

Total round-trip latency components:

```{math}
T_{\text{total}} = T_{\text{serialize}} + T_{\text{network}} + T_{\text{process}} + T_{\text{deserialize}}
```

Where:
- $T_{\text{serialize}}$: JSON serialization time (~0.5 ms)
- $T_{\text{network}}$: TCP round-trip time (configurable, default 5 ms)
- $T_{\text{process}}$: Controller computation time (variable)
- $T_{\text{deserialize}}$: JSON deserialization time (~0.5 ms)

**Timing Constraint:**
```{math}
T_{\text{total}} < \Delta t \quad \text{(Control period constraint)}
```

### Sensor Noise Model

Additive Gaussian noise on state measurements:

```{math}
\tilde{\vec{x}}(t) = \vec{x}(t) + \vec{\eta}(t), \quad \vec{\eta} \sim \mathcal{N}(0, \sigma^2 I)
```

Where:
- $\tilde{\vec{x}}$: Noisy measurement
- $\vec{\eta}$: Gaussian noise vector
- $\sigma$: Standard deviation (configurable, default 0.01)

### Server Architecture

**Thread-Safe State Management:**
- Main dynamics thread: Runs simulation at fixed timestep
- Network thread: Handles TCP connections and message exchange
- Shared state: Protected by locks for thread safety

**Graceful Degradation:**
- Connection timeout: 10 seconds
- Maximum steps: Prevents infinite loops
- Failsafe shutdown: Clean resource cleanup on errors

## Architecture Diagram

```{mermaid}
graph TD
    A[TCP Socket Listener] --> B[Accept Connection]
    B --> C[Spawn Server Thread]
    C --> D{Receive Request}
    D --> E[Deserialize Message]
    E --> F[Extract Control Input]
    F --> G[Step Dynamics]
    G --> H[Add Sensor Noise]
    H --> I[Serialize State]
    I --> J[Send Response]
    J --> K{Connection Active?}
    K -->|Yes| D
    K -->|No| L[Cleanup & Exit]

    G --> M[Dynamics Model]
    M --> N[Compute Derivatives]
    N --> O[Integrate Step]
    O --> P[Update State]

    style G fill:#9cf
    style H fill:#ff9
    style M fill:#f9f
    style L fill:#9f9
```

**Data Flow:**
1. Listen for client connections on TCP socket
2. Receive control input from client
3. Step dynamics simulation with control
4. Add configurable sensor noise
5. Send noisy state back to client
6. Repeat until simulation complete

## Usage Examples

### Example 1: Basic HIL Server Setup

```python
from src.interfaces.hil import PlantServer
from src.config import load_config

# Load configuration
config = load_config("config.yaml")

# Initialize server
server = PlantServer(
    cfg=config,
    bind_addr=("127.0.0.1", 5555),
    dt=0.01,  # 10 ms control period
    extra_latency_ms=5,  # 5 ms network latency
    sensor_noise_std=0.01,  # 1% sensor noise
    max_steps=5000  # 50 seconds simulation
)

# Start server (blocks until client connects)
server.start()

# Server runs until

client disconnects or max_steps reached
server.close()
```

## Example 2: Custom Dynamics Configuration

```python
from src.interfaces.hil import PlantServer
from src.plant.models.full import FullDIPDynamics

# Create high-fidelity dynamics model
dynamics = FullDIPDynamics(
    config=config,
    enable_monitoring=True,
    enable_validation=True
)

# Server with custom dynamics
server = PlantServer(
    cfg=config,
    bind_addr=("0.0.0.0", 5555),  # Listen on all interfaces
    dt=0.01
)

# Override dynamics model
server._dynamics = dynamics

server.start()
```

## Example 3: Multi-Client Testing

```python
from threading import Thread
from src.interfaces.hil import PlantServer

def run_server(port, max_steps):
    server = PlantServer(
        cfg=config,
        bind_addr=("127.0.0.1", port),
        dt=0.01,
        max_steps=max_steps
    )
    server.start()
    server.close()

# Run multiple servers for parallel testing
threads = []
for port in [5555, 5556, 5557]:
    t = Thread(target=run_server, args=(port, 5000))
    t.start()
    threads.append(t)

# Wait for all servers to complete
for t in threads:
    t.join()

print("All parallel tests complete")
```

## Example 4: Server

with Logging and Monitoring

```python
# example-metadata:
# runnable: false

from src.interfaces.hil import PlantServer
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='hil_server.log'
)

# Server with logging
server = PlantServer(
    cfg=config,
    bind_addr=("127.0.0.1", 5555),
    dt=0.01,
    extra_latency_ms=5,
    sensor_noise_std=0.01
)

# Enable detailed monitoring
logger = logging.getLogger('HIL.PlantServer')
logger.info("Starting HIL plant server...")

try:
    server.start()
except Exception as e:
    logger.error(f"Server error: {e}")
finally:
    server.close()
    logger.info("Server shutdown complete")
```

## Example 5: Performance Profiling

```python
from src.interfaces.hil import PlantServer
import time
import psutil

# Metrics collection
metrics = {
    'step_times': [],
    'memory_usage': [],
    'cpu_usage': []
}

# Custom server with profiling
server = PlantServer(cfg=config, bind_addr=("127.0.0.1", 5555), dt=0.01)

# Override step function for profiling
original_step = server._step
def profiled_step(control):
    start = time.time()
    result = original_step(control)
    metrics['step_times'].append(time.time() - start)
    metrics['memory_usage'].append(psutil.Process().memory_info().rss / 1024**2)
    metrics['cpu_usage'].append(psutil.cpu_percent())
    return result

server._step = profiled_step
server.start()
server.close()

# Analyze performance
print(f"Mean step time: {np.mean(metrics['step_times']):.4f} s")
print(f"Max memory: {max(metrics['memory_usage']):.1f} MB")
print(f"Mean CPU: {np.mean(metrics['cpu_usage']):.1f}%")
```

## Complete Source Code

```{literalinclude} ../../../src/interfaces/hil/plant_server.py
:language: python
:linenos:
```



## Classes

### `PlantServer`

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/plant_server.py
:language: python
:pyobject: PlantServer
:linenos:
```

#### Methods (4)

##### `__init__(self, cfg, bind_addr, dt, extra_latency_ms, sensor_noise_std, max_steps, server_ready_event)`

[View full source →](#method-plantserver-__init__)

##### `start(self)`

[View full source →](#method-plantserver-start)

##### `close(self)`

[View full source →](#method-plantserver-close)

##### `stop(self)`

[View full source →](#method-plantserver-stop)



## Functions

### `_load_config(cfg_path)`

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/plant_server.py
:language: python
:pyobject: _load_config
:linenos:
```



### `_get(cfg, dotted, default)`

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/plant_server.py
:language: python
:pyobject: _get
:linenos:
```



### `_build_dynamics(cfg)`

Build the dynamics model using the project's light/full models if present.

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/plant_server.py
:language: python
:pyobject: _build_dynamics
:linenos:
```



### `start_server(cfg_path, max_steps)`

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/plant_server.py
:language: python
:pyobject: start_server
:linenos:
```



### `main(argv)`

#### Source Code

```{literalinclude} ../../../src/interfaces/hil/plant_server.py
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
- `import threading`
- `import time`
- `import logging`
- `from pathlib import Path`
- `from typing import Optional, Tuple`

*... and 1 more*
