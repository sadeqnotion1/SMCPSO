#=====================================================================================
#========== tests/test_interfaces/test_data_exchange_streaming_async.py ===============
#=====================================================================================
"""Regression test for M7-S2-3: streaming async-hang.

The StreamingSerializer/Deserializer processing loops consume a thread-safe
StreamBuffer whose get()/get_batch() block on threading.Condition.wait().
Before the fix those blocking calls ran directly on the event loop thread,
freezing the whole loop (heartbeat tasks, asyncio.wait_for timers, and even
stop() could never be scheduled).

This test asserts the event loop stays responsive while a streaming component
is idle (empty buffer, long flush_interval). It is designed to FAIL FAST (not
hang) if the regression returns: the whole asyncio scenario runs in a daemon
thread guarded by a join() timeout, so a frozen loop surfaces as an assertion
failure rather than an indefinite hang.
"""
import asyncio
import threading

from src.interfaces.data_exchange.streaming import StreamingSerializer, StreamConfig


class _MockSerializer:
    def serialize(self, item):
        return b"mock"

    def deserialize(self, item):
        return {}


def _run_scenario(result):
    async def scenario():
        # Long flush_interval + empty buffer => the processing loop parks inside
        # StreamBuffer.get_batch (Condition.wait). The loop must stay alive.
        config = StreamConfig(flush_interval=5.0, buffer_size=10)
        serializer = StreamingSerializer(_MockSerializer(), config)
        await serializer.start()

        ticks = 0

        async def heartbeat():
            nonlocal ticks
            for _ in range(5):
                await asyncio.sleep(0.1)
                ticks += 1

        hb = asyncio.create_task(heartbeat())
        # If the loop is blocked, this wait_for can never fire and the heartbeat
        # never ticks; the scenario coroutine then never returns.
        await asyncio.wait_for(hb, timeout=3.0)

        # stop() must also be schedulable and complete promptly.
        await asyncio.wait_for(serializer.stop(), timeout=3.0)

        result["ticks"] = ticks

    try:
        asyncio.run(scenario())
    except Exception as exc:  # surface timeouts/errors to the assertions below
        result["error"] = repr(exc)


def test_streaming_serializer_does_not_block_event_loop():
    result = {}
    t = threading.Thread(target=_run_scenario, args=(result,), daemon=True)
    t.start()
    t.join(timeout=15.0)

    assert not t.is_alive(), (
        "event loop hung: streaming processing loop blocked the loop thread "
        "(regression of M7-S2-3)"
    )
    assert "error" not in result, f"scenario raised: {result.get('error')}"
    assert result.get("ticks") == 5, (
        f"heartbeat did not run concurrently (ticks={result.get('ticks')}); "
        "event loop was starved"
    )
