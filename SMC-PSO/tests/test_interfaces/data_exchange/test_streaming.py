#======================================================================================\\
#======== tests/test_interfaces/data_exchange/test_streaming.py =======================\\
#======================================================================================\\

"""
Comprehensive tests for streaming serialization module.

Tests cover buffer management, backpressure strategies, serialization/deserialization
pipelines, async stream processing, and error handling.
"""

import pytest
import asyncio
import time
import threading
from typing import Any, List
from unittest.mock import Mock, patch

from src.interfaces.data_exchange.streaming import (
    StreamBuffer,
    BackpressureStrategy,
    StreamConfig,
    StreamMetrics,
    StreamingSerializer,
    StreamingDeserializer,
    StreamState,
)
from src.interfaces.data_exchange.serializers import SerializerInterface
from src.interfaces.data_exchange.data_types import DataMessage, MessageType


# =============================================================================
# TEST FIXTURES
# =============================================================================

class DummySerializer(SerializerInterface):
    """Dummy serializer for testing that records calls."""

    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.serialize_calls = []
        self.deserialize_calls = []

    @property
    def format_type(self) -> str:
        """Return format type."""
        return "dummy"

    @property
    def content_type(self) -> str:
        """Return content type."""
        return "application/dummy"

    def serialize(self, data: Any) -> bytes:
        """Serialize data to bytes."""
        self.serialize_calls.append(data)
        if self.should_fail:
            raise ValueError("Serialization failed")
        # Simple serialization: convert to string and encode
        return str(data).encode('utf-8')

    def deserialize(self, data: bytes) -> Any:
        """Deserialize bytes to data."""
        self.deserialize_calls.append(data)
        if self.should_fail:
            raise ValueError("Deserialization failed")
        # Simple deserialization: decode and eval (unsafe but fine for tests)
        return data.decode('utf-8')


@pytest.fixture
def dummy_serializer():
    """Provide a dummy serializer for testing."""
    return DummySerializer()


@pytest.fixture
def failing_serializer():
    """Provide a serializer that always fails."""
    return DummySerializer(should_fail=True)


@pytest.fixture
def sample_data_message():
    """Provide a sample DataMessage for testing."""
    return DataMessage(
        type=MessageType.CONTROLLER_STATE,
        timestamp=time.time(),
        data={"state": [1.0, 2.0, 3.0]},
        metadata={"source": "test"}
    )


@pytest.fixture
def stream_config_small():
    """Provide a small stream config for fast tests."""
    return StreamConfig(
        buffer_size=10,
        batch_size=5,
        flush_interval=0.1,  # Short interval for fast tests
        backpressure_strategy=BackpressureStrategy.BLOCK
    )


# =============================================================================
# STREAM BUFFER TESTS
# =============================================================================

class TestStreamBuffer:
    """Test suite for StreamBuffer with backpressure handling."""

    def test_buffer_put_and_get_fifo_order(self):
        """Test buffer maintains FIFO order for put/get operations."""
        buffer = StreamBuffer(max_size=10, backpressure_strategy=BackpressureStrategy.BLOCK)

        # Put items
        assert buffer.put(1) is True
        assert buffer.put(2) is True
        assert buffer.put(3) is True

        # Get items in FIFO order
        assert buffer.get(timeout=0.1) == 1
        assert buffer.get(timeout=0.1) == 2
        assert buffer.get(timeout=0.1) == 3

    def test_buffer_block_strategy_when_full(self):
        """Test BLOCK strategy waits when buffer is full."""
        buffer = StreamBuffer(max_size=2, backpressure_strategy=BackpressureStrategy.BLOCK)

        # Fill buffer
        assert buffer.put(1) is True
        assert buffer.put(2) is True
        assert buffer.is_full() is True

        # Try to put with zero timeout should fail (can't wait)
        result = buffer.put(3, timeout=0.0)
        assert result is False

        # Buffer still has original items
        assert buffer.size() == 2

    def test_buffer_drop_oldest_strategy(self):
        """Test DROP_OLDEST strategy drops oldest item when full."""
        buffer = StreamBuffer(max_size=2, backpressure_strategy=BackpressureStrategy.DROP_OLDEST)

        # Fill buffer
        assert buffer.put(1) is True
        assert buffer.put(2) is True

        # Add third item should drop oldest (1)
        assert buffer.put(3) is True

        # Buffer should have 2 and 3
        assert buffer.get(timeout=0.1) == 2
        assert buffer.get(timeout=0.1) == 3

    def test_buffer_drop_newest_strategy(self):
        """Test DROP_NEWEST strategy rejects new item when full."""
        buffer = StreamBuffer(max_size=2, backpressure_strategy=BackpressureStrategy.DROP_NEWEST)

        # Fill buffer
        assert buffer.put(1) is True
        assert buffer.put(2) is True

        # Try to add third item should be rejected
        assert buffer.put(3) is False

        # Buffer should still have 1 and 2
        assert buffer.get(timeout=0.1) == 1
        assert buffer.get(timeout=0.1) == 2

    def test_buffer_expand_strategy_grows_beyond_max(self):
        """Test BUFFER_EXPAND strategy allows buffer to grow."""
        buffer = StreamBuffer(max_size=2, backpressure_strategy=BackpressureStrategy.BUFFER_EXPAND)

        # Fill buffer beyond max_size
        assert buffer.put(1) is True
        assert buffer.put(2) is True
        assert buffer.put(3) is True  # Should succeed despite max_size=2
        assert buffer.put(4) is True

        # All items should be in buffer
        assert buffer.size() == 4

    def test_buffer_get_batch_returns_requested_size(self):
        """Test get_batch returns requested number of items."""
        buffer = StreamBuffer(max_size=10, backpressure_strategy=BackpressureStrategy.BLOCK)

        # Add items
        for i in range(5):
            buffer.put(i)

        # Get batch of 3
        batch = buffer.get_batch(batch_size=3, timeout=0.1)
        assert len(batch) == 3
        assert batch == [0, 1, 2]

        # Remaining items
        assert buffer.size() == 2

    def test_buffer_get_batch_timeout_returns_partial(self):
        """Test get_batch returns partial batch on timeout."""
        buffer = StreamBuffer(max_size=10, backpressure_strategy=BackpressureStrategy.BLOCK)

        # Add only 2 items
        buffer.put(1)
        buffer.put(2)

        # Request 5 items with short timeout
        batch = buffer.get_batch(batch_size=5, timeout=0.1)

        # Should get partial batch
        assert len(batch) == 2
        assert batch == [1, 2]

    def test_buffer_close_unblocks_waiting_operations(self):
        """Test close() unblocks waiting get() operations."""
        buffer = StreamBuffer(max_size=10, backpressure_strategy=BackpressureStrategy.BLOCK)

        # Close buffer
        buffer.close()

        # Get on closed empty buffer should return None immediately
        result = buffer.get(timeout=1.0)
        assert result is None

    def test_buffer_put_on_closed_returns_false(self):
        """Test put() on closed buffer returns False."""
        buffer = StreamBuffer(max_size=10, backpressure_strategy=BackpressureStrategy.BLOCK)

        buffer.close()

        # Put on closed buffer should fail
        assert buffer.put(1) is False

    def test_buffer_size_and_is_full_accurate(self):
        """Test size() and is_full() report accurate state."""
        buffer = StreamBuffer(max_size=3, backpressure_strategy=BackpressureStrategy.BLOCK)

        assert buffer.size() == 0
        assert buffer.is_full() is False

        buffer.put(1)
        assert buffer.size() == 1
        assert buffer.is_full() is False

        buffer.put(2)
        buffer.put(3)
        assert buffer.size() == 3
        assert buffer.is_full() is True


# =============================================================================
# STREAMING SERIALIZER TESTS
# =============================================================================

class TestStreamingSerializer:
    """Test suite for StreamingSerializer async pipeline."""

    @pytest.mark.asyncio
    async def test_serializer_start_stop_lifecycle(self, dummy_serializer, stream_config_small):
        """Test serializer starts and stops correctly."""
        serializer = StreamingSerializer(dummy_serializer, stream_config_small)

        # Start should succeed
        assert await serializer.start() is True

        # Starting again should fail (already running)
        assert await serializer.start() is False

        # Stop should succeed
        assert await serializer.stop() is True

        # Stopping again should succeed (already stopped)
        assert await serializer.stop() is True

    @pytest.mark.asyncio
    async def test_serializer_processes_data_and_calls_handlers(self, dummy_serializer, stream_config_small):
        """Test serializer processes data and invokes output handlers."""
        serializer = StreamingSerializer(dummy_serializer, stream_config_small)

        # Add output handler
        output_received = []
        def handler(data: bytes):
            output_received.append(data)

        serializer.add_output_handler(handler)

        # Start serializer
        await serializer.start()

        # Add data
        test_data = [1, 2, 3]
        for item in test_data:
            serializer.add_data(item)

        # Wait for processing
        await asyncio.sleep(0.2)

        # Stop serializer
        await serializer.stop()

        # Verify handler received serialized data
        assert len(output_received) == 3
        assert dummy_serializer.serialize_calls == test_data

    @pytest.mark.asyncio
    async def test_serializer_rejects_add_data_when_not_running(self, dummy_serializer, stream_config_small):
        """Test add_data returns False when serializer not running."""
        serializer = StreamingSerializer(dummy_serializer, stream_config_small)

        # Add data before starting
        assert serializer.add_data(1) is False

        # Start, add, stop
        await serializer.start()
        assert serializer.add_data(2) is True
        await serializer.stop()

        # Add data after stopping
        assert serializer.add_data(3) is False

    @pytest.mark.asyncio
    async def test_serializer_handles_output_handler_exceptions(self, dummy_serializer, stream_config_small):
        """Test serializer continues processing when output handler raises."""
        serializer = StreamingSerializer(dummy_serializer, stream_config_small)

        # Add handler that raises exception
        def failing_handler(data: bytes):
            raise RuntimeError("Handler error")

        # Add normal handler
        output_received = []
        def normal_handler(data: bytes):
            output_received.append(data)

        serializer.add_output_handler(failing_handler)
        serializer.add_output_handler(normal_handler)

        await serializer.start()
        serializer.add_data(1)

        # Wait for processing
        await asyncio.sleep(0.2)
        await serializer.stop()

        # Normal handler should still receive data despite failing handler
        assert len(output_received) == 1

    @pytest.mark.asyncio
    async def test_serializer_updates_metrics(self, dummy_serializer, stream_config_small):
        """Test serializer updates metrics after processing."""
        serializer = StreamingSerializer(dummy_serializer, stream_config_small)

        await serializer.start()

        # Add data
        serializer.add_data(1)
        serializer.add_data(2)

        # Wait for processing
        await asyncio.sleep(0.2)
        await serializer.stop()

        # Check metrics
        metrics = serializer.get_metrics()
        assert metrics.items_processed == 2
        assert metrics.bytes_processed > 0

    @pytest.mark.asyncio
    async def test_serializer_increments_error_count_on_exception(self, failing_serializer, stream_config_small):
        """Test serializer increments error count when serialization fails."""
        serializer = StreamingSerializer(failing_serializer, stream_config_small)

        await serializer.start()
        serializer.add_data(1)

        # Wait for processing (will fail)
        await asyncio.sleep(0.2)
        await serializer.stop()

        # Check error count
        metrics = serializer.get_metrics()
        assert metrics.errors >= 1


# =============================================================================
# STREAMING DESERIALIZER TESTS
# =============================================================================

class TestStreamingDeserializer:
    """Test suite for StreamingDeserializer async pipeline."""

    @pytest.mark.asyncio
    async def test_deserializer_start_stop_lifecycle(self, dummy_serializer, stream_config_small):
        """Test deserializer starts and stops correctly."""
        deserializer = StreamingDeserializer(dummy_serializer, stream_config_small)

        # Start should succeed
        assert await deserializer.start() is True

        # Starting again should fail (already running)
        assert await deserializer.start() is False

        # Stop should succeed
        assert await deserializer.stop() is True

        # Stopping again should succeed (already stopped)
        assert await deserializer.stop() is True

    @pytest.mark.asyncio
    async def test_deserializer_processes_data_and_calls_handlers(self, dummy_serializer, stream_config_small):
        """Test deserializer processes data and invokes output handlers."""
        deserializer = StreamingDeserializer(dummy_serializer, stream_config_small)

        # Add output handler
        output_received = []
        def handler(data: Any):
            output_received.append(data)

        deserializer.add_output_handler(handler)

        # Start deserializer
        await deserializer.start()

        # Add serialized data
        test_data = [b"1", b"2", b"3"]
        for item in test_data:
            deserializer.add_serialized_data(item)

        # Wait for processing
        await asyncio.sleep(0.2)

        # Stop deserializer
        await deserializer.stop()

        # Verify handler received deserialized data
        assert len(output_received) == 3
        assert dummy_serializer.deserialize_calls == test_data

    @pytest.mark.asyncio
    async def test_deserializer_rejects_add_data_when_not_running(self, dummy_serializer, stream_config_small):
        """Test add_serialized_data returns False when deserializer not running."""
        deserializer = StreamingDeserializer(dummy_serializer, stream_config_small)

        # Add data before starting
        assert deserializer.add_serialized_data(b"test") is False

        # Start, add, stop
        await deserializer.start()
        assert deserializer.add_serialized_data(b"test") is True
        await deserializer.stop()

        # Add data after stopping
        assert deserializer.add_serialized_data(b"test") is False

    @pytest.mark.asyncio
    async def test_deserializer_handles_output_handler_exceptions(self, dummy_serializer, stream_config_small):
        """Test deserializer continues processing when output handler raises."""
        deserializer = StreamingDeserializer(dummy_serializer, stream_config_small)

        # Add handler that raises exception
        def failing_handler(data: Any):
            raise RuntimeError("Handler error")

        # Add normal handler
        output_received = []
        def normal_handler(data: Any):
            output_received.append(data)

        deserializer.add_output_handler(failing_handler)
        deserializer.add_output_handler(normal_handler)

        await deserializer.start()
        deserializer.add_serialized_data(b"test")

        # Wait for processing
        await asyncio.sleep(0.2)
        await deserializer.stop()

        # Normal handler should still receive data despite failing handler
        assert len(output_received) == 1

    @pytest.mark.asyncio
    async def test_deserializer_updates_metrics(self, dummy_serializer, stream_config_small):
        """Test deserializer updates metrics after processing."""
        deserializer = StreamingDeserializer(dummy_serializer, stream_config_small)

        await deserializer.start()

        # Add data
        deserializer.add_serialized_data(b"1")
        deserializer.add_serialized_data(b"2")

        # Wait for processing
        await asyncio.sleep(0.2)
        await deserializer.stop()

        # Check metrics
        metrics = deserializer.get_metrics()
        assert metrics.items_processed == 2
        assert metrics.bytes_processed > 0

    @pytest.mark.asyncio
    async def test_deserializer_increments_error_count_on_exception(self, failing_serializer, stream_config_small):
        """Test deserializer increments error count when deserialization fails."""
        deserializer = StreamingDeserializer(failing_serializer, stream_config_small)

        await deserializer.start()
        deserializer.add_serialized_data(b"test")

        # Wait for processing (will fail)
        await asyncio.sleep(0.2)
        await deserializer.stop()

        # Check error count
        metrics = deserializer.get_metrics()
        assert metrics.errors >= 1


# =============================================================================
# STREAM METRICS TESTS
# =============================================================================

class TestStreamMetrics:
    """Test suite for StreamMetrics calculations."""

    def test_metrics_update_accumulates_values(self):
        """Test metrics update accumulates items and bytes."""
        metrics = StreamMetrics()

        # Update with first batch
        metrics.update(items=10, bytes_count=1000, processing_time=0.1)
        assert metrics.items_processed == 10
        assert metrics.bytes_processed == 1000

        # Update with second batch
        metrics.update(items=5, bytes_count=500, processing_time=0.05)
        assert metrics.items_processed == 15
        assert metrics.bytes_processed == 1500

    def test_metrics_calculates_rates(self):
        """Test metrics calculates items_per_second and bytes_per_second."""
        # Create metrics with fixed start time
        metrics = StreamMetrics()

        # Mock time to simulate 1 second elapsed
        with patch('time.time', return_value=metrics.start_time + 1.0):
            metrics.update(items=100, bytes_count=10000, processing_time=0.5)

        # Rates should be items/bytes per second
        assert metrics.items_per_second == pytest.approx(100.0)
        assert metrics.bytes_per_second == pytest.approx(10000.0)

    def test_metrics_handles_zero_elapsed_time(self):
        """Test metrics doesn't divide by zero with zero elapsed time."""
        metrics = StreamMetrics()

        # Update immediately (zero elapsed time)
        with patch('time.time', return_value=metrics.start_time):
            metrics.update(items=10, bytes_count=1000, processing_time=0.1)

        # Should not crash, rates stay at 0
        assert metrics.items_per_second == 0.0
        assert metrics.bytes_per_second == 0.0
