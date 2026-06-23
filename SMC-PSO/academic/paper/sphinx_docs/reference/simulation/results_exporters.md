# simulation.results.exporters

**Source:** `src\simulation\results\exporters.py`

## Module Overview

Export simulation results to various formats.

## Complete Source Code

```{literalinclude} ../../../src/simulation/results/exporters.py
:language: python
:linenos:
```



## Classes

### `CSVExporter`

Export simulation results to CSV format.

#### Source Code

```{literalinclude} ../../../src/simulation/results/exporters.py
:language: python
:pyobject: CSVExporter
:linenos:
```

#### Methods (2)

##### `export(self, result_container, filepath)`

Export single simulation results to CSV.

[View full source →](#method-csvexporter-export)

##### `export_batch(self, batch_container, filepath)`

Export batch simulation results to CSV.

[View full source →](#method-csvexporter-export_batch)



### `HDF5Exporter`

Export simulation results to HDF5 format.

#### Source Code

```{literalinclude} ../../../src/simulation/results/exporters.py
:language: python
:pyobject: HDF5Exporter
:linenos:
```

#### Methods (2)

##### `export(self, result_container, filepath)`

Export single simulation results to HDF5.

[View full source →](#method-hdf5exporter-export)

##### `export_batch(self, batch_container, filepath)`

Export batch simulation results to HDF5.

[View full source →](#method-hdf5exporter-export_batch)



## Dependencies

This module imports:

- `from __future__ import annotations`
- `import csv`
- `from pathlib import Path`
- `from typing import Any`
- `import numpy as np`


## Advanced Mathematical Theory

(Theory content to be added...)


## Architecture Diagram

\`\`\`{mermaid}
graph TD
    A[Result Exporters] --> B[CSV Exporter]
    A --> C[HDF5 Exporter]
    A --> D[JSON Exporter]

    E[Result Container] --> F{Format Selection}

    F -->|CSV| B
    F -->|HDF5| C
    F -->|JSON| D

    B --> G[CSV Serialization]
    G --> H[Time series → rows]
    G --> I[Metadata → header]

    C --> J[HDF5 Hierarchical]
    J --> K[Groups: metadata, data]
    J --> L[Datasets: time, state, control]
    J --> M[Compression: gzip, lzf]

    D --> N[JSON Serialization]
    N --> O[NumPy → lists]
    N --> P[Datetime → ISO 8601]

    H --> Q[CSV File]
    M --> R[HDF5 File]
    P --> S[JSON File]

    style F fill:#fff4e1
    style Q fill:#e8f5e9
    style R fill:#e8f5e9
    style S fill:#e8f5e9
\`\`\`


## Usage Examples

### Example 1: Basic Usage

\`\`\`python
# Basic usage example

from src.simulation.results import Component

component = Component()
result = component.process(data)
\`\`\`

## Example 2: Advanced Configuration

\`\`\`python
# Advanced configuration

component = Component(
    option1=value1,
    option2=value2
)
\`\`\`

## Example 3: Integration with Framework

\`\`\`python
# Integration example

from src.simulation import SimulationRunner

runner = SimulationRunner()
runner.use_component(component)
\`\`\`

## Example 4: Performance Optimization

\`\`\`python
# Performance-optimized usage

component = Component(enable_caching=True)
\`\`\`

## Example 5: Error Handling

\`\`\`python
# Error handling

try:
    result = component.process(data)
except ComponentError as e:
    print(f"Error: {e}")
\`\`\`
