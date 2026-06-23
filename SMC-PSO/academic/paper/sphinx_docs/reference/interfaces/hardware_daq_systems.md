# interfaces.hardware.daq_systems

**Source:** `src\interfaces\hardware\daq_systems.py`

## Module Overview

Data acquisition (DAQ) system interfaces for control systems.
This module provides standardized interfaces for various DAQ systems
including National Instruments DAQ, ADC converters, and multi-channel
data acquisition hardware commonly used in control applications.

## Complete Source Code

```{literalinclude} ../../../src/interfaces/hardware/daq_systems.py
:language: python
:linenos:
```



## Classes

### `DAQMode`

**Inherits from:** `Enum`

DAQ operation mode enumeration.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/daq_systems.py
:language: python
:pyobject: DAQMode
:linenos:
```



### `ChannelType`

**Inherits from:** `Enum`

DAQ channel type enumeration.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/daq_systems.py
:language: python
:pyobject: ChannelType
:linenos:
```



### `ChannelConfig`

DAQ channel configuration.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/daq_systems.py
:language: python
:pyobject: ChannelConfig
:linenos:
```



### `DAQSample`

DAQ sample data structure.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/daq_systems.py
:language: python
:pyobject: DAQSample
:linenos:
```



### `DAQBuffer`

DAQ buffer for storing samples.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/daq_systems.py
:language: python
:pyobject: DAQBuffer
:linenos:
```

#### Methods (3)

##### `add_sample(self, sample)`

Add sample to buffer.

[View full source →](#method-daqbuffer-add_sample)

##### `get_latest(self, count)`

Get latest samples.

[View full source →](#method-daqbuffer-get_latest)

##### `clear(self)`

Clear buffer.

[View full source →](#method-daqbuffer-clear)



### `DAQInterface`

**Inherits from:** `DeviceDriver`, `ABC`

Abstract base class for DAQ system interfaces.

This class defines the standard interface for all DAQ systems,
providing common functionality for multi-channel data acquisition,
configuration management, and synchronization.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/daq_systems.py
:language: python
:pyobject: DAQInterface
:linenos:
```

#### Methods (16)

##### `__init__(self, config)`

Initialize DAQ interface.

[View full source →](#method-daqinterface-__init__)

##### `is_acquiring(self)`

Check if DAQ is currently acquiring data.

[View full source →](#method-daqinterface-is_acquiring)

##### `sample_rate(self)`

Get current sample rate.

[View full source →](#method-daqinterface-sample_rate)

##### `channels(self)`

Get channel configurations.

[View full source →](#method-daqinterface-channels)

##### `configure_channel(self, channel_config)`

Configure a DAQ channel.

[View full source →](#method-daqinterface-configure_channel)

##### `read_channel(self, channel_name)`

Read single sample from channel.

[View full source →](#method-daqinterface-read_channel)

##### `write_channel(self, channel_name, value)`

Write value to output channel.

[View full source →](#method-daqinterface-write_channel)

##### `start_acquisition(self, mode)`

Start data acquisition.

[View full source →](#method-daqinterface-start_acquisition)

##### `stop_acquisition(self)`

Stop data acquisition.

[View full source →](#method-daqinterface-stop_acquisition)

##### `add_channel(self, channel_config)`

Add channel to DAQ system.

[View full source →](#method-daqinterface-add_channel)

##### `remove_channel(self, channel_name)`

Remove channel from DAQ system.

[View full source →](#method-daqinterface-remove_channel)

##### `read_all_channels(self)`

Read from all configured channels.

[View full source →](#method-daqinterface-read_all_channels)

##### `get_buffer_data(self, channel_name, count)`

Get buffered data from channel.

[View full source →](#method-daqinterface-get_buffer_data)

##### `clear_buffers(self)`

Clear all channel buffers.

[View full source →](#method-daqinterface-clear_buffers)

##### `set_sample_rate(self, sample_rate)`

Set DAQ sample rate.

[View full source →](#method-daqinterface-set_sample_rate)

##### `_store_sample(self, sample)`

Store sample in buffer.

[View full source →](#method-daqinterface-_store_sample)



### `NIDAQInterface`

**Inherits from:** `DAQInterface`

National Instruments DAQ interface implementation.

Provides integration with NI-DAQmx for high-performance data
acquisition using National Instruments hardware.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/daq_systems.py
:language: python
:pyobject: NIDAQInterface
:linenos:
```

#### Methods (12)

##### `__init__(self, config)`

Initialize NI-DAQ interface.

[View full source →](#method-nidaqinterface-__init__)

##### `initialize(self)`

Initialize NI-DAQ interface.

[View full source →](#method-nidaqinterface-initialize)

##### `shutdown(self)`

Shutdown NI-DAQ interface.

[View full source →](#method-nidaqinterface-shutdown)

##### `read_data(self, channel)`

Read data from NI-DAQ.

[View full source →](#method-nidaqinterface-read_data)

##### `write_data(self, data)`

Write data to NI-DAQ output channels.

[View full source →](#method-nidaqinterface-write_data)

##### `self_test(self)`

Perform NI-DAQ self-test.

[View full source →](#method-nidaqinterface-self_test)

##### `configure_channel(self, channel_config)`

Configure NI-DAQ channel.

[View full source →](#method-nidaqinterface-configure_channel)

##### `read_channel(self, channel_name)`

Read single sample from NI-DAQ channel.

[View full source →](#method-nidaqinterface-read_channel)

##### `write_channel(self, channel_name, value)`

Write value to NI-DAQ output channel.

[View full source →](#method-nidaqinterface-write_channel)

##### `start_acquisition(self, mode)`

Start NI-DAQ continuous acquisition.

[View full source →](#method-nidaqinterface-start_acquisition)

##### `stop_acquisition(self)`

Stop NI-DAQ acquisition.

[View full source →](#method-nidaqinterface-stop_acquisition)

##### `_acquisition_loop(self, input_channels)`

Continuous acquisition loop.

[View full source →](#method-nidaqinterface-_acquisition_loop)



### `AdcInterface`

**Inherits from:** `DAQInterface`

Generic ADC interface implementation.

Provides basic analog-to-digital conversion functionality
for simple ADC chips and modules.

#### Source Code

```{literalinclude} ../../../src/interfaces/hardware/daq_systems.py
:language: python
:pyobject: AdcInterface
:linenos:
```

#### Methods (14)

##### `__init__(self, config)`

Initialize ADC interface.

[View full source →](#method-adcinterface-__init__)

##### `initialize(self)`

Initialize ADC interface.

[View full source →](#method-adcinterface-initialize)

##### `shutdown(self)`

Shutdown ADC interface.

[View full source →](#method-adcinterface-shutdown)

##### `read_data(self, channel)`

Read data from ADC.

[View full source →](#method-adcinterface-read_data)

##### `write_data(self, data)`

Write data to ADC (configuration only).

[View full source →](#method-adcinterface-write_data)

##### `self_test(self)`

Perform ADC self-test.

[View full source →](#method-adcinterface-self_test)

##### `configure_channel(self, channel_config)`

Configure ADC channel.

[View full source →](#method-adcinterface-configure_channel)

##### `read_channel(self, channel_name)`

Read single sample from ADC channel.

[View full source →](#method-adcinterface-read_channel)

##### `write_channel(self, channel_name, value)`

Write value to ADC channel (not applicable).

[View full source →](#method-adcinterface-write_channel)

##### `start_acquisition(self, mode)`

Start ADC continuous acquisition.

[View full source →](#method-adcinterface-start_acquisition)

##### `stop_acquisition(self)`

Stop ADC acquisition.

[View full source →](#method-adcinterface-stop_acquisition)

##### `_read_adc_raw(self, channel_name)`

Read raw ADC value.

[View full source →](#method-adcinterface-_read_adc_raw)

##### `_adc_acquisition_loop(self)`

ADC acquisition loop.

[View full source →](#method-adcinterface-_adc_acquisition_loop)

##### `_init_adc_channels(self)`

Initialize default ADC channels.

[View full source →](#method-adcinterface-_init_adc_channels)



## Dependencies

This module imports:

- `import asyncio`
- `import time`
- `import numpy as np`
- `from abc import ABC, abstractmethod`
- `from dataclasses import dataclass, field`
- `from typing import Dict, Any, Optional, List, Tuple, Union`
- `from enum import Enum`
- `import logging`
- `from .device_drivers import DeviceDriver, DeviceConfig, DeviceCapability, DeviceState`
