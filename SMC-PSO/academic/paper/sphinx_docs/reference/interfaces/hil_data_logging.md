# interfaces.hil.data_logging

**Source:** `src\interfaces\hil\data_logging.py`

## Module Overview Data

logging system for HIL applications

.


This module provides data logging features including
high-frequency data collection, buffering, compression, and export
for HIL system analysis and validation. ## Mathematical Foundation ### Data Logging Architecture Capture simulation data: ```{math}
\mathcal{D} = \{(t_k, \vec{x}_k, u_k, \vec{m}_k)\}_{k=0}^{N}
``` Where:
- $t_k$: Timestamp
- $\vec{x}_k$: State vector
- $u_k$: Control input
- $\vec{m}_k$: Metadata (controller state, diagnostics) ### Sampling Strategies **1. Fixed-Rate Sampling:**
```{math}

t_{k+1} = t_k + \Delta t_{\text{log}}
``` **2. Event-Triggered Sampling:**
```{math}

\text{Log}(t) \Leftrightarrow \|\vec{x}(t) - \vec{x}(t_{\text{last}})\| > \epsilon
``` **3. Adaptive Sampling:**
```{math}

\Delta t_{\text{log}} = \begin{cases}
\Delta t_{\text{min}} & \text{if } \|\dot{\vec{x}}\| > v_{\text{thresh}} \\
\Delta t_{\text{max}} & \text{otherwise}
\end{cases}
``` ### Data Compression **Lossless Compression:**
- Delta encoding: Store differences instead of absolute values
- Run-length encoding: Compress repeated values ```{math}
\Delta \vec{x}_k = \vec{x}_k - \vec{x}_{k-1}
``` **Lossy Compression:**

- Quantization: Reduce precision
- Downsampling: Reduce temporal resolution ```{math}
\vec{x}_{\text{quantized}} = \text{round}\left(\frac{\vec{x}}{q}\right) \cdot q
``` ### Storage Formats **1. CSV (Human-Readable):**
```

time,x,theta1,theta2,x_dot,theta1_dot,theta2_dot,control
0.000,0.0,0.1,-0.05,0.0,0.0,0.0,0.0
0.010,0.0,0.099,-0.049,0.05,0.01,0.02,12.5
``` **2. HDF5 (High-Performance):**
- Hierarchical structure
- Chunked storage for efficient I/O
- Built-in compression (gzip, lzf) **3. Parquet (Columnar):**
- Efficient for analytical queries
- Schema evolution support
- Good compression ratios ### Replay Functionality **State Reconstruction:**
```{math}

\vec{x}(t) = \vec{x}(t_k) + \int_{t_k}^{t} f(\vec{x}(\tau), u(\tau)) d\tau
``` **Control Reconstruction:**
```{math}

u(t) = u(t_k), \quad \forall t \in [t_k, t_{k+1})
``` Zero-order hold interpolation. ### Performance Metrics **1. Logging Overhead:**
```{math}

\text{Overhead} = \frac{T_{\text{logging}}}{T_{\text{total}}} \times 100\%
``` **2. Storage Efficiency:**
```{math}

\text{Compression Ratio} = \frac{\text{Raw Size}}{\text{Compressed Size}}
``` **3. I/O Throughput:**
```{math}

\text{Throughput} = \frac{\text{Data Volume}}{\text{Write Time}} \quad [\text{MB/s}]
``` ### Real-Time Constraints **Logging Deadline:**
```{math}

T_{\text{write}} < \Delta t_{\text{control}}
``` **Buffer Management:**
- Ring buffer: Fixed-size circular buffer
- Double buffering: Write while logging
- Flush policy: Periodic or threshold-based **Buffering Strategy:**
```{math}

\text{Flush} \Leftrightarrow (\text{Buffer Full}) \lor (t - t_{\text{last\_flush}} > T_{\text{flush}})
``` ## Architecture Diagram ```{mermaid}
graph TD A[Simulation Data] --> B{Sampling Strategy} B -->|Fixed Rate| C[Fixed Sampler] B -->|Event Trigger| D[Event Sampler] B -->|Adaptive| E[Adaptive Sampler] C --> F[Data Buffer] D --> F E --> F F --> G{Buffer Full?} G -->|Yes| H[Flush to Disk] G -->|No| F H --> I{Format} I -->|CSV| J[CSV Writer] I -->|HDF5| K[HDF5 Writer] I -->|Parquet| L[Parquet Writer] J --> M[File Storage] K --> M L --> M M --> N[Replay System] N --> O[State Reconstruction] N --> P[Control Reconstruction] style F fill:#9cf style H fill:#ff9 style M fill:#f9f
``` **Logging Pipeline:**

1. **Data Sampling**: Choose sampling strategy based on requirements
2. **Buffering**: Store data in memory buffer for efficiency
3. **Flushing**: Write to disk when buffer full or timeout
4. **Serialization**: Convert to chosen format (CSV, HDF5, Parquet)
5. **Storage**: Save to disk for later analysis
6. **Replay**: Reconstruct simulation from logged data ## Usage Examples ### Example 1: Basic CSV Logging ```python
from src.interfaces.hil.data_logging import DataLogger # Create logger
logger = DataLogger( output_path="hil_data.csv", format="csv", sample_rate=100.0 # 100 Hz
) # Simulation with logging
for t in np.arange(0, 10, 0.01): state = plant.get_state() control = controller.compute(state) # Log data logger.log(time=t, state=state, control=control) # Close logger
logger.close()
print("Data saved to hil_data.csv")
``` ### Example 2: HDF5 High-Performance Logging ```python
from src.interfaces.hil.data_logging import HDF5Logger # HDF5 logger with compression
logger = HDF5Logger( output_path="hil_data.h5", compression="gzip", compression_opts=9 # Maximum compression
) # Create datasets
logger.create_dataset("time", dtype=np.float64)
logger.create_dataset("state", shape=(6,), dtype=np.float64)
logger.create_dataset("control", dtype=np.float64) # Log simulation data
for t in np.arange(0, 10, 0.01): state = plant.get_state() control = controller.compute(state) logger.append("time", t) logger.append("state", state) logger.append("control", control) logger.close()
``` ### Example 3: Event-Triggered Logging ```python

from src.interfaces.hil.data_logging import EventLogger # Event-based logger
logger = EventLogger( output_path="events.csv", threshold=0.1 # Log when state changes > 0.1
) last_state = None for t in np.arange(0, 10, 0.01): state = plant.get_state() # Check if significant change if last_state is not None: state_change = np.linalg.norm(state - last_state) if state_change > logger.threshold: logger.log(time=t, state=state) last_state = state logger.close()
print(f"Logged {logger.event_count} events")
``` ### Example 4: Multi-Format Logging ```python
from src.interfaces.hil.data_logging import MultiLogger # Log to multiple formats simultaneously
logger = MultiLogger( outputs=[ ("hil_data.csv", "csv"), ("hil_data.h5", "hdf5"), ("hil_data.parquet", "parquet") ]
) for t in np.arange(0, 10, 0.01): state = plant.get_state() control = controller.compute(state) # Log to all formats logger.log_all(time=t, state=state, control=control) logger.close_all()
``` ### Example 5: Replay from Logged Data ```python

from src.interfaces.hil.data_logging import DataLogger, Replay # Log data
logger = DataLogger("original.csv", format="csv")
for t in np.arange(0, 10, 0.01): state = plant.get_state() control = controller.compute(state) logger.log(time=t, state=state, control=control)
logger.close() # Replay simulation
replay = Replay("original.csv") for entry in replay: t = entry["time"] state = entry["state"] control = entry["control"] # Reconstruct dynamics reconstructed_state = plant.step(control) # Compare original vs reconstructed error = np.linalg.norm(state - reconstructed_state) if error > 0.01: print(f"Reconstruction error at t={t:.2f}: {error:.4f}") print("Replay complete")
``` ## Complete Source Code ```{literalinclude} ../../../src/interfaces/hil/data_logging.py
:language: python
:linenos:
```

---

## Classes

### `LogFormat`

**Inherits from:** `Enum` Data logging format enumeration.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/data_logging.py

:language: python
:pyobject: LogFormat
:linenos:
```

### `CompressionType`

**Inherits from:** `Enum` Data compression type enumeration.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/data_logging.py
:language: python
:pyobject: CompressionType
:linenos:
```

### `LoggingConfig`

HIL data logging configuration.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/data_logging.py

:language: python
:pyobject: LoggingConfig
:linenos:
```

### `LogEntry`

Individual log entry.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/data_logging.py
:language: python
:pyobject: LogEntry
:linenos:
```

### `HILDataLogger`

High-performance data logger for HIL systems. Provides efficient data collection, buffering, and storage

with support for multiple formats and real-time compression. #### Source Code ```{literalinclude} ../../../src/interfaces/hil/data_logging.py
:language: python
:pyobject: HILDataLogger
:linenos:
``` #### Methods (20) ##### `__init__(self, config)` Initialize HIL data logger. [View full source →](#method-hildatalogger-__init__) ##### `initialize(self)` Initialize data logger. [View full source →](#method-hildatalogger-initialize) ##### `start(self)` Start data logging. [View full source →](#method-hildatalogger-start) ##### `stop(self)` Stop data logging. [View full source →](#method-hildatalogger-stop) ##### `log_data(self, data, timestamp)` Log data entry. [View full source →](#method-hildatalogger-log_data) ##### `log_batch(self, batch_data)` Log batch of data entries. [View full source →](#method-hildatalogger-log_batch) ##### `get_statistics(self)` Get logging statistics. [View full source →](#method-hildatalogger-get_statistics) ##### `export_data(self, output_file, start_time, end_time, channels)` Export logged data to file. [View full source →](#method-hildatalogger-export_data) ##### `_flush_loop(self)` Background flush loop. [View full source →](#method-hildatalogger-_flush_loop) ##### `_flush_buffer(self)` Flush buffer to file. [View full source →](#method-hildatalogger-_flush_buffer) ##### `_write_entries(self, entries)` Write entries to current file. [View full source →](#method-hildatalogger-_write_entries) ##### `_write_hdf5_entries(self, entries)` Write entries to HDF5 file. [View full source →](#method-hildatalogger-_write_hdf5_entries) ##### `_write_csv_entries(self, entries)` Write entries to CSV file. [View full source →](#method-hildatalogger-_write_csv_entries) ##### `_write_json_entries(self, entries)` Write entries to JSON file. [View full source →](#method-hildatalogger-_write_json_entries) ##### `_create_new_file(self)` Create new log file. [View full source →](#method-hildatalogger-_create_new_file) ##### `_close_current_file(self)` Close current log file. [View full source →](#method-hildatalogger-_close_current_file) ##### `_rotate_file(self)` Rotate to new log file. [View full source →](#method-hildatalogger-_rotate_file) ##### `_cleanup_old_files(self)` Clean up old log files. [View full source →](#method-hildatalogger-_cleanup_old_files) ##### `_get_current_filename(self)` Get current log filename. [View full source →](#method-hildatalogger-_get_current_filename) ##### `_setup_output_directory(self)` Setup output directory. [View full source →](#method-hildatalogger-_setup_output_directory)

---

## Functions

### `load_hdf5_data(filepath, channels, start_time, end_time)`

Load data from HDF5 log file.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/data_logging.py
:language: python
:pyobject: load_hdf5_data
:linenos:
```

### `analyze_log_performance(log_stats)`

Analyze logging performance.

#### Source Code ```

{literalinclude} ../../../src/interfaces/hil/data_logging.py

:language: python
:pyobject: analyze_log_performance
:linenos:
```

---

## Dependencies This module imports: - `import asyncio`
- `import time`
- `import csv`
- `import json`
- `import h5py`
- `import numpy as np`
- `from dataclasses import dataclass, field`
- `from typing import Dict, Any, Optional, List, Union, BinaryIO`
- `from enum import Enum`
- `import logging` *... and 1 more*
