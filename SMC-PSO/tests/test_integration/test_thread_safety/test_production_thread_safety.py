#==========================================================================================\\\
#== tests/test_integration/test_thread_safety/test_production_thread_safety.py ============\\\
#==========================================================================================\\\

"""
Production Thread Safety Tests - Phase 4.2 (Codex-Written)

Comprehensive thread safety tests for production scenarios:
- 100+ concurrent controller creations
- PSO multi-threading validation
- Factory registry stress tests
- Deadlock detection
- Memory leak prevention
"""

from __future__ import annotations

import concurrent.futures
import gc
import os
import tempfile
import threading
import time
import weakref
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Dict, List, Set
from unittest.mock import patch

import numpy as np
import psutil
import pytest
import yaml

from src.config import ConfigSchema, load_config
from src.controllers.factory import create_controller, list_available_controllers
# NOTE: thread_safety module was consolidated into factory/base.py during Week 1 reorganization
# This test file needs refactoring to use new factory architecture (with_factory_lock, etc.)
# from src.controllers.factory.thread_safety import get_thread_safety_enhancement
from src.optimization.algorithms.pso_optimizer import PSOTuner

# Temporary skip until test is refactored for new factory architecture
pytest_skip_module = pytest.skip(
    "Test module needs refactoring for Week 1 factory consolidation. "
    "Thread safety API changed: thread_safety module -> factory/base.py with_factory_lock()",
    allow_module_level=True
)


def _sanitise_config_payload(path: str | Path = "config.yaml") -> Dict[str, Any]:
    """Load YAML config and drop unknown root keys for strict schema validation."""
    raw_data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    allowed_keys = set(ConfigSchema.model_fields.keys())
    return {key: value for key, value in raw_data.items() if key in allowed_keys}


@lru_cache(maxsize=1)
def _load_production_config() -> ConfigSchema:
    """Load configuration once, allowing reuse across concurrent tests."""
    payload = _sanitise_config_payload()

    tmp_file: tempfile.NamedTemporaryFile[str] | None = None
    try:
        tmp_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".yaml",
            delete=False,
            encoding="utf-8"
        )
        yaml.safe_dump(payload, tmp_file)  # type: ignore[arg-type]
        tmp_file.flush()
        config = load_config(tmp_file.name, allow_unknown=True)
    finally:
        if tmp_file is not None:
            tmp_path = Path(tmp_file.name)
            tmp_file.close()
            if tmp_path.exists():
                tmp_path.unlink()

    return config


def _config_copy() -> ConfigSchema:
    """Return a deep copy of cached config to avoid cross-test mutation."""
    return _load_production_config().model_copy(deep=True)  # type: ignore[return-value]


def _make_simulation_stub(callback: Callable[[Dict[str, Any]], None] | None = None) -> Callable[..., Any]:
    """Factory for lightweight simulation stubs used in PSO tests."""

    def _simulate_system_batch(**kwargs: Any) -> Any:
        if callback:
            callback(kwargs)

        particles = np.asarray(kwargs.get("particles"))
        if particles.ndim != 2:
            raise ValueError("particles must be a 2D array")

        num_particles, gain_dims = particles.shape
        steps = max(10, int(kwargs.get("sim_time", 1.0) / max(kwargs.get("dt", 0.01), 1e-3)))
        steps = min(steps, 50)

        t = np.linspace(0.0, float(kwargs.get("sim_time", 1.0)), steps, dtype=float)
        base_profile = np.linspace(0.0, 1.0, steps, dtype=float)
        states = np.tile(base_profile[None, :, None], (num_particles, 1, gain_dims))
        controls = np.tile((base_profile ** 2)[None, :], (num_particles, 1))
        sigma = np.tile(np.abs(np.sin(base_profile))[None, :], (num_particles, 1))

        time.sleep(0.002)
        return [(t, states, controls, sigma)]

    return _simulate_system_batch


def _make_controller_factory(controller_type: str, config: ConfigSchema) -> Callable[[np.ndarray], Any]:
    """Return controller factory callable for PSOTuner tests."""

    def _factory(gains: np.ndarray) -> Any:
        return create_controller(controller_type, config=config, gains=gains.tolist())

    return _factory


@pytest.mark.concurrent
class TestProductionThreadSafety:
    """Production-grade thread safety tests."""

    def test_concurrent_classical_smc_creation_100(self) -> None:
        """Test 100 simultaneous classical SMC controller creations."""
        config = _config_copy()

        def create_controller_task(task_id: int) -> bool:
            try:
                controller = create_controller(
                    "classical_smc",
                    config=config,
                    gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0]
                )
                assert controller is not None, f"Task {task_id} failed to create controller"
                return True
            except Exception as exc:  # pragma: no cover - diagnostic path
                print(f"Task {task_id} error: {exc}")
                return False

        num_tasks = 100
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(create_controller_task, i) for i in range(num_tasks)]
            results = [f.result(timeout=20) for f in concurrent.futures.as_completed(futures)]

        duration = time.time() - start_time

        assert all(results), f"Some controller creations failed: {results.count(False)}/{num_tasks}"
        assert duration < 10.0, f"Creation took too long: {duration:.2f}s (expected <10s)"

    def test_concurrent_mixed_controller_types(self) -> None:
        """Test concurrent creation of different controller types."""
        config = _config_copy()

        available = list_available_controllers()
        required_types = [
            ("classical_smc", "classical_smc"),
            ("sta_smc", "sta_smc"),
            ("adaptive_smc", "adaptive_smc"),
            ("hybrid_adaptive_sta_smc", "hybrid_adaptive_sta_smc"),
        ]
        controller_types = [
            (alias, name)
            for alias, name in required_types
            if name in available
        ]
        assert len(controller_types) == len(required_types), "Missing required controller types"

        def create_mixed_controller(task_id: int) -> Dict[str, Any]:
            ctrl_type = controller_types[task_id % len(controller_types)][1]
            try:
                # Extract gains from config (fix for CA-01 audit finding)
                if ctrl_type == "classical_smc":
                    gains = config.controller_defaults.classical_smc.gains
                elif ctrl_type == "sta_smc":
                    gains = config.controller_defaults.sta_smc.gains
                elif ctrl_type == "adaptive_smc":
                    gains = config.controller_defaults.adaptive_smc.gains
                elif ctrl_type == "hybrid_adaptive_sta_smc":
                    gains = config.controller_defaults.hybrid_adaptive_sta_smc.gains
                else:
                    gains = [1.0, 1.0, 1.0, 1.0]  # Fallback
                controller = create_controller(ctrl_type, config=config, gains=gains)
                assert controller is not None
                return {"success": True, "type": ctrl_type, "id": task_id}
            except Exception as exc:  # pragma: no cover - diagnostic path
                return {"success": False, "type": ctrl_type, "id": task_id, "error": str(exc)}

        num_tasks = 80
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
            futures = [executor.submit(create_mixed_controller, i) for i in range(num_tasks)]
            results = [f.result(timeout=20) for f in concurrent.futures.as_completed(futures)]

        successful = [result for result in results if result["success"]]
        failed = [result for result in results if not result["success"]]

        assert failed == [], f"Failures: {failed}"
        assert len(successful) == num_tasks, f"Too many failures: {len(failed)}/{num_tasks}"

        type_counts: Dict[str, int] = {}
        for result in successful:
            type_counts[result["type"]] = type_counts.get(result["type"], 0) + 1

        assert all(count >= 18 for count in type_counts.values()), f"Uneven type distribution: {type_counts}"

    def test_concurrent_create_destroy_cycles(self) -> None:
        """Test rapid controller creation and destruction for memory leaks."""
        config = _config_copy()
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        def create_and_destroy_controller(task_id: int) -> bool:
            # Extract gains from config (fix for CA-01 audit finding)
            gains = config.controller_defaults.classical_smc.gains
            controller = create_controller("classical_smc", config=config, gains=gains)
            local_rng = np.random.default_rng(42 + task_id)
            state = local_rng.normal(0, 0.1, 6)
            _ = controller.compute_control(state, None, None)
            del controller
            return True

        num_cycles = 1000
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(create_and_destroy_controller, i) for i in range(num_cycles)]
            results = [f.result(timeout=30) for f in concurrent.futures.as_completed(futures)]

        gc.collect()
        time.sleep(1.0)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        assert all(results), "Some create-destroy cycles failed"
        assert memory_increase < 50, f"Possible memory leak: {memory_increase:.1f}MB increase"

    def test_pso_concurrent_fitness_evaluations(self) -> None:
        """Test PSO optimizer handling concurrent fitness evaluations."""
        config = _config_copy()
        controller_factory = _make_controller_factory("classical_smc", config)

        call_threads: Set[int] = set()
        call_lock = threading.Lock()

        def on_simulation_call(kwargs: Dict[str, Any]) -> None:
            with call_lock:
                call_threads.add(threading.current_thread().ident or 0)

        with patch(
            "src.optimization.algorithms.pso_optimizer.simulate_system_batch",
            new=_make_simulation_stub(on_simulation_call),
        ):
            tuner = PSOTuner(
                controller_factory=controller_factory,
                config=config,
                seed=123
            )

            particles = np.abs(np.random.default_rng(2025).normal(1.0, 0.1, size=(16, 6)))

            def evaluate_batch() -> np.ndarray:
                return tuner._fitness(particles)

            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(evaluate_batch) for _ in range(4)]
                results = [f.result(timeout=15) for f in futures]

        assert len(call_threads) >= 2, f"Too few threads used for simulation: {call_threads}"
        for result in results:
            assert result.shape == (particles.shape[0],)
            assert np.all(np.isfinite(result)), "Non-finite fitness values detected"

    def test_pso_particle_isolation(self) -> None:
        """Verify PSO particle evaluations do not leak state across threads."""
        config = _config_copy()
        controller_factory = _make_controller_factory("classical_smc", config)

        particle_states: Dict[int, List[np.ndarray]] = {}
        lock = threading.Lock()

        def on_simulation_call(kwargs: Dict[str, Any]) -> None:
            thread_id = threading.current_thread().ident or 0
            with lock:
                particle_states.setdefault(thread_id, []).append(np.array(kwargs["particles"], copy=True))

        with patch(
            "src.optimization.algorithms.pso_optimizer.simulate_system_batch",
            new=_make_simulation_stub(on_simulation_call),
        ):
            tuner = PSOTuner(
                controller_factory=controller_factory,
                config=config,
                seed=456
            )

            def evaluate_particles(batch_id: int) -> np.ndarray:
                local_rng = np.random.default_rng(7 + batch_id)
                batch_particles = local_rng.normal(1.0, 0.2, size=(12, 6)) + batch_id * 0.01
                return tuner._fitness(batch_particles)

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(evaluate_particles, i) for i in range(5)]
                results = [f.result(timeout=15) for f in futures]

        assert len(particle_states) >= 3, f"Too few threads recorded: {len(particle_states)}"
        for thread_id, states in particle_states.items():
            assert len(states) >= 1, f"No states captured for thread {thread_id}"
            for i in range(len(states) - 1):
                assert not np.array_equal(states[i], states[i + 1]), "Particle state not updating across evaluations"

        for result in results:
            assert np.all(np.isfinite(result))

    def test_factory_registry_concurrent_reads_1000(self) -> None:
        """Test factory registry under heavy concurrent read load."""
        thread_safety = get_thread_safety_enhancement()
        registry = {
            "classical_smc": {"class": "ClassicalSMC", "file": "classical_smc.py"},
            "sta_smc": {"class": "STASMC", "file": "sta_smc.py"},
            "adaptive_smc": {"class": "AdaptiveSMC", "file": "adaptive_smc.py"},
        }
        thread_safety.initialize_registry(registry)

        def concurrent_read(task_id: int) -> bool:
            ctrl_type = ["classical_smc", "sta_smc", "adaptive_smc"][task_id % 3]
            info = thread_safety.get_controller_info_safe(ctrl_type)
            return info is not None

        num_reads = 1000
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(concurrent_read, i) for i in range(num_reads)]
            results = [f.result(timeout=10) for f in concurrent.futures.as_completed(futures)]

        duration = time.time() - start_time

        assert all(results), "Some registry reads failed"
        assert duration < 2.0, f"Registry reads too slow: {duration:.2f}s (expected <2s)"

    def test_factory_registry_mixed_read_write(self) -> None:
        """Test registry with concurrent reads and occasional writes."""
        thread_safety = get_thread_safety_enhancement()
        initial_registry = {"classical_smc": {"class": "ClassicalSMC"}}
        thread_safety.initialize_registry(initial_registry)

        read_count = 0
        write_count = 0
        lock = threading.Lock()

        def mixed_operation(task_id: int) -> str:
            nonlocal read_count, write_count
            if task_id % 10 == 0:
                new_registry = {
                    "classical_smc": {"class": "ClassicalSMC"},
                    f"test_controller_{task_id}": {"class": f"TestCtrl{task_id}"},
                }
                thread_safety.lock_free_registry.update_registry(new_registry)
                with lock:
                    write_count += 1
                return "write"

            info = thread_safety.get_controller_info_safe("classical_smc")
            with lock:
                read_count += 1
            return "read" if info else "fail"

        num_ops = 500
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(mixed_operation, i) for i in range(num_ops)]
            results = [f.result(timeout=10) for f in concurrent.futures.as_completed(futures)]

        reads = results.count("read")
        writes = results.count("write")
        fails = results.count("fail")

        assert fails == 0, f"Failed operations: {fails}"
        assert reads >= 400, f"Too few reads: {reads}"
        assert writes >= 40, f"Too few writes: {writes}"

    def test_no_deadlock_creation_and_pso(self) -> None:
        """Test no deadlock when creating controllers while PSO runs."""
        config = _config_copy()
        controller_factory = _make_controller_factory("classical_smc", config)
        timeout_seconds = 10.0

        results: List[np.ndarray] = []
        result_lock = threading.Lock()

        def pso_worker() -> None:
            with patch(
                "src.optimization.algorithms.pso_optimizer.simulate_system_batch",
                new=_make_simulation_stub(),
            ):
                tuner = PSOTuner(
                    controller_factory=controller_factory,
                    config=config,
                    seed=99
                )
                outcome = tuner.optimise(
                    n_particles_override=6,
                    iters_override=6
                )
                with result_lock:
                    results.append(outcome["best_pos"])

        def creation_worker(task_id: int) -> bool:
            # Extract gains from config (fix for CA-01 audit finding)
            gains = config.controller_defaults.classical_smc.gains
            controller = create_controller("classical_smc", config=config, gains=gains)
            assert controller is not None
            return True

        pso_thread = threading.Thread(target=pso_worker, daemon=True)
        start_time = time.time()
        pso_thread.start()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(creation_worker, i) for i in range(50)]
            creation_results = [f.result(timeout=timeout_seconds) for f in concurrent.futures.as_completed(futures)]

        pso_thread.join(timeout=timeout_seconds)
        duration = time.time() - start_time

        if pso_thread.is_alive():  # pragma: no cover - failure diagnostic
            pytest.fail(f"Possible deadlock: PSO thread still alive after {duration:.2f}s")

        assert all(creation_results), "Some controller creations failed during PSO execution"
        assert duration < timeout_seconds, f"Operations took too long: {duration:.2f}s"
        assert results, "PSO worker did not produce results"

    def test_no_deadlock_multiple_factory_operations(self) -> None:
        """Test no deadlock with multiple factory operations simultaneously."""
        config = _config_copy()
        timeout_seconds = 8.0

        def factory_operation(op_type: str, task_id: int) -> str:
            try:
                if op_type == "create":
                    ctrl_type = ["classical_smc", "sta_smc"][task_id % 2]
                    # Extract gains from config (fix for CA-01 audit finding)
                    if ctrl_type == "classical_smc":
                        gains = config.controller_defaults.classical_smc.gains
                    else:  # sta_smc
                        gains = config.controller_defaults.sta_smc.gains
                    controller = create_controller(ctrl_type, config=config, gains=gains)
                    return "created" if controller else "failed"
                if op_type == "get_info":
                    thread_safety = get_thread_safety_enhancement()
                    info = thread_safety.get_controller_info_safe("classical_smc")
                    return "info" if info else "no_info"
                if op_type == "list_controllers":
                    controllers = list_available_controllers()
                    return "listed" if controllers else "empty"
                return "unknown"
            except Exception as exc:  # pragma: no cover - diagnostic path
                return f"error: {exc}"

        operations = ["create", "get_info", "list_controllers", "create"]
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures: List[concurrent.futures.Future[str]] = []
            for i in range(100):
                op_type = operations[i % len(operations)]
                futures.append(executor.submit(factory_operation, op_type, i))

            results = [future.result(timeout=timeout_seconds) for future in concurrent.futures.as_completed(futures)]

        duration = time.time() - start_time
        errors = [result for result in results if result.startswith("error")]

        assert not errors, f"Factory operation errors: {errors[:5]}"
        assert duration < timeout_seconds, f"Possible deadlock: took {duration:.2f}s"

    def test_memory_safety_1000_creation_cycles(self) -> None:
        """Test for memory leaks in 1000 concurrent controller creation cycles."""
        config = _config_copy()
        process = psutil.Process(os.getpid())

        gc.collect()
        time.sleep(0.5)
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        def create_use_destroy(task_id: int) -> bool:
            # Extract gains from config (fix for CA-01 audit finding)
            gains = config.controller_defaults.classical_smc.gains
            controller = create_controller("classical_smc", config=config, gains=gains)
            local_rng = np.random.default_rng(314 + task_id)
            state = local_rng.normal(0, 0.1, 6)
            _ = controller.compute_control(state, None, None)
            del controller
            return True

        num_cycles = 1000
        batch_size = 50

        for batch in range(num_cycles // batch_size):
            with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
                futures = [
                    executor.submit(create_use_destroy, batch * batch_size + i)
                    for i in range(batch_size)
                ]
                results = [f.result(timeout=10) for f in concurrent.futures.as_completed(futures)]
                assert all(results), f"Batch {batch} had failures"

            if batch % 5 == 0:
                gc.collect()

        gc.collect()
        time.sleep(0.5)
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        assert memory_increase < 100, f"Memory leak detected: {memory_increase:.1f}MB increase"

    def test_weakref_cleanup_concurrent(self) -> None:
        """Verify weakref cleanup works correctly in concurrent controller creation."""
        config = _config_copy()
        weak_refs: List[weakref.ReferenceType[Any]] = []
        lock = threading.Lock()
        def create_and_track_controller(task_id: int) -> bool:
            # Extract gains from config (fix for CA-01 audit finding)
            gains = config.controller_defaults.classical_smc.gains
            controller = create_controller("classical_smc", config=config, gains=gains)
            weak_ref = weakref.ref(controller)
            with lock:
                weak_refs.append(weak_ref)
            local_rng = np.random.default_rng(512 + task_id)
            state = local_rng.normal(0, 0.05, 6)
            _ = controller.compute_control(state, None, None)
            del controller
            return True

        num_controllers = 200
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(create_and_track_controller, i) for i in range(num_controllers)]
            results = [f.result(timeout=15) for f in concurrent.futures.as_completed(futures)]

        assert all(results), "Some controller creations failed"

        gc.collect()
        time.sleep(1.0)

        alive_refs = [ref for ref in weak_refs if ref() is not None]
        assert not alive_refs, f"Weakref cleanup failed: {len(alive_refs)}/{num_controllers} controllers still alive"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "concurrent"])
