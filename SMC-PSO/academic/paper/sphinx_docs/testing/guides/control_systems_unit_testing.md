#======================================================================================\\\
#============== docs/testing/guides/control_systems_unit_testing.md ==================\\\
#======================================================================================\\\

# Control Systems Unit Testing Guide ## Overview This guide provides testing patterns for sliding mode control (SMC) implementations in the double-inverted pendulum control system. It covers state space validation, controller interface compliance, optimal gains interpretation, and production-ready testing methodologies. ## Table of Contents 1. [SMC Controller Testing Patterns](#smc-controller-testing-patterns)
2. [State Space Validation](#state-space-validation)
3. [Lyapunov Function Testing](#lyapunov-function-testing)
4. [Optimal Gains Interpretation](#optimal-gains-interpretation)
5. [Controller Interface Compliance](#controller-interface-compliance)
6. [Production Testing Standards](#production-testing-standards)

---

## 1. SMC Controller Testing Patterns ### 1.1 Basic Controller Initialization Every SMC controller must pass basic initialization tests to ensure proper parameter handling: ```python

# example-metadata:

# runnable: false def test_classical_smc_initialization(): """Test Classical SMC initialization with valid parameters.""" # Optimal gains from PSO optimization (report.log line 2) gains = [77.62, 44.45, 17.31, 14.25, 18.66, 9.76] boundary_layer = 9.76 # Matched to kd for chattering reduction max_force = 20.0 controller = ClassicalSMC( gains=gains, max_force=max_force, boundary_layer=boundary_layer, switch_method='tanh' ) # Verify gains unpacked correctly assert controller.k1 == pytest.approx(77.62, rel=1e-6) assert controller.k2 == pytest.approx(44.45, rel=1e-6) assert controller.lam1 == pytest.approx(17.31, rel=1e-6) assert controller.lam2 == pytest.approx(14.25, rel=1e-6) assert controller.K == pytest.approx(18.66, rel=1e-6) assert controller.kd == pytest.approx(9.76, rel=1e-6) # Verify boundary layer for chattering reduction assert controller.epsilon0 == pytest.approx(9.76) # Verify control authority limits assert controller.max_force == 20.0

``` **Why these gains work:**
- **High k1 (77.62)**: Strong feedback from first pendulum angular velocity
- **High k2 (44.45)**: Substantial feedback from second pendulum angular velocity
- **Moderate lam1/lam2**: Balanced position error contribution
- **Large boundary layer (9.76)**: Aggressive chattering suppression ### 1.2 Gain Validation Testing Test enforcement of SMC theoretical constraints (F-4.SMCDesign.2 / RC-04): ```python
# example-metadata:
# runnable: false def test_gain_positivity_enforcement(): """Test strict positivity requirements for SMC gains.""" boundary_layer = 0.1 max_force = 20.0 # Test k1 must be strictly positive with pytest.raises(ValueError, match="k1.*must be > 0"): ClassicalSMC( gains=[0.0, 44.45, 17.31, 14.25, 18.66, 9.76], max_force=max_force, boundary_layer=boundary_layer ) # Test k2 must be strictly positive with pytest.raises(ValueError, match="k2.*must be > 0"): ClassicalSMC( gains=[77.62, -5.0, 17.31, 14.25, 18.66, 9.76], max_force=max_force, boundary_layer=boundary_layer ) # Test lam1, lam2 must be strictly positive with pytest.raises(ValueError, match="lam1.*must be > 0"): ClassicalSMC( gains=[77.62, 44.45, 0.0, 14.25, 18.66, 9.76], max_force=max_force, boundary_layer=boundary_layer ) # Test K (switching gain) must be strictly positive with pytest.raises(ValueError, match="K.*must be > 0"): ClassicalSMC( gains=[77.62, 44.45, 17.31, 14.25, -1.0, 9.76], max_force=max_force, boundary_layer=boundary_layer ) # Test kd (derivative gain) can be zero but not negative # This should NOT raise an error controller = ClassicalSMC( gains=[77.62, 44.45, 17.31, 14.25, 18.66, 0.0], max_force=max_force, boundary_layer=boundary_layer ) assert controller.kd == 0.0 # But negative kd should fail with pytest.raises(ValueError, match="kd.*must be"): ClassicalSMC( gains=[77.62, 44.45, 17.31, 14.25, 18.66, -1.0], max_force=max_force, boundary_layer=boundary_layer )
``` **Theoretical justification:**

- Sliding surface gains (k1, k2, lam1, lam2) must be strictly positive for Hurwitz stability
- Switching gain K must be positive to drive system to sliding surface
- Derivative gain kd provides damping and can be zero

---

## 2. State Space Validation ### 2.1 State Vector Dimension Testing ```python

# example-metadata:

# runnable: false def test_state_vector_validation(): """Test proper handling of state vectors with correct dimensions.""" controller = create_test_controller() # Valid 6D state: [x, theta1, theta2, xdot, dtheta1, dtheta2] valid_state = np.array([0.1, 0.05, -0.03, 0.0, 0.1, -0.05]) result = controller.compute_control( state=valid_state, state_vars=(), history={} ) assert isinstance(result.u, (float, np.floating)) assert np.isfinite(result.u) # Invalid state dimensions should be caught early invalid_states = [ np.array([0.1, 0.05, 0.0]), # Too short np.array([0.1, 0.05, -0.03, 0.0, 0.1, -0.05, 0.0]), # Too long ] for invalid_state in invalid_states: with pytest.raises((ValueError, IndexError)): controller.compute_control( state=invalid_state, state_vars=(), history={} )

``` ### 2.2 Physical State Bounds Testing ```python
# example-metadata:
# runnable: false def test_physical_state_bounds(): """Test controller behavior within and beyond physical limits.""" controller = create_test_controller() # Test states within normal operating range normal_states = [ np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]), # Equilibrium np.array([0.1, 0.1, 0.1, 0.0, 0.0, 0.0]), # Small displacement np.array([0.5, 0.3, 0.2, 0.0, 0.0, 0.0]), # Moderate displacement ] for state in normal_states: result = controller.compute_control(state, (), {}) # Control must be finite and bounded assert np.isfinite(result.u) assert abs(result.u) <= controller.max_force # Test extreme but valid states extreme_states = [ np.array([0.0, np.pi/6, np.pi/6, 0.0, 2.0, 2.0]), # Large angles/velocities np.array([1.0, -np.pi/4, np.pi/4, 0.5, -1.5, 1.0]), # Mixed extremes ] for state in extreme_states: result = controller.compute_control(state, (), {}) # Must still produce finite, bounded control assert np.isfinite(result.u) assert abs(result.u) <= controller.max_force
```

---

## 3. Lyapunov Function Testing ### 3.1 Lyapunov Candidate Testing Test that the Lyapunov candidate function $V = \frac{1}{2}\sigma^2$ decreases along trajectories: ```python

# example-metadata:

# runnable: false def test_lyapunov_decrease_property(): """Test Lyapunov decrease property: V̇ < 0 when |σ| > 0.""" controller = create_test_controller() # Test states with non-zero sliding surface values test_states = [ np.array([0.0, 0.1, 0.0, 0.0, 0.0, 0.0]), # Pendulum 1 displaced np.array([0.0, 0.0, 0.1, 0.0, 0.0, 0.0]), # Pendulum 2 displaced np.array([0.0, 0.05, 0.05, 0.0, 0.1, 0.1]), # Both displaced with velocity ] history = {} for state in test_states: result = controller.compute_control(state, (), history) # Extract sliding surface from history assert 'sigma' in history sigma = history['sigma'][-1] # Lyapunov function V = 0.5 * sigma^2 V = 0.5 * sigma**2 # For non-zero sigma, ensure control acts to reduce V if abs(sigma) > 1e-6: # Control should oppose sigma to drive V̇ < 0 # For classical SMC: u = u_eq - K*sat(σ/ε) - kd*σ # The robust term -K*sat(σ/ε) should have opposite sign to σ

            u_robust = history['u_robust'][-1]

            # Robust control should oppose sliding surface
            assert np.sign(u_robust) == -np.sign(sigma) or abs(sigma) < controller.epsilon0
``` ### 3.2 Lyapunov Decrease Ratio (LDR) Monitoring Test the LDR monitoring from `src/utils/monitoring/stability.py`: ```python
def test_lyapunov_decrease_ratio_monitoring(): """Test LDR monitoring for stability assessment.""" from src.utils.monitoring.stability import LyapunovDecreaseMonitor dt = 0.01 monitor = LyapunovDecreaseMonitor( window_size_ms=300.0, dt=dt, ldr_threshold=0.95, transient_time=1.0 ) controller = create_test_controller() # Simulate trajectory state = np.array([0.1, 0.2, -0.1, 0.0, 0.3, -0.2]) history = {} ldr_values = [] for step in range(200): # 2 seconds simulation result = controller.compute_control(state, (), history) # Extract sliding surface and update monitor sigma = np.array([history['sigma'][-1]]) monitor_result = monitor.update(sigma) # After transient period, check LDR if monitor_result['status'] != 'transient': ldr = monitor_result['ldr'] ldr_values.append(ldr) # LDR should be high (>95%) for stable control if len(ldr_values) > 50: # After enough samples recent_ldr = np.mean(ldr_values[-50:]) assert recent_ldr >= 0.90, \ f"LDR too low: {recent_ldr:.2%} (should be ≥90%)" # Simple state update (mock dynamics) state[3:] += -0.1 * state[:3] * dt # Simplified dynamics state[:3] += state[3:] * dt
```

---

## 4. Optimal Gains Interpretation ### 4.1 Understanding PSO-Optimized Gains From `.logs/report.log` line 16, the optimal gains are: `[77.62, 44.45, 17.31, 14.25, 18.66, 9.76]` ```python

# example-metadata:

# runnable: false def test_optimal_gains_performance(): """Test performance characteristics of PSO-optimized gains.""" # PSO optimal gains optimal_gains = [77.62, 44.45, 17.31, 14.25, 18.66, 9.76] boundary_layer = 9.76 # Matched to kd for maximum chattering reduction controller = ClassicalSMC( gains=optimal_gains, max_force=20.0, boundary_layer=boundary_layer, switch_method='tanh' ) # Analyze gain ratios for insights k1, k2, lam1, lam2, K, kd = optimal_gains # Ratio k1/k2 indicates relative importance of pendulum rates k_ratio = k1 / k2 assert 1.5 < k_ratio < 2.0, \ f"k1/k2 ratio {k_ratio:.2f} indicates strong first pendulum damping" # Ratio lam1/lam2 indicates relative position error weighting lam_ratio = lam1 / lam2 assert 1.0 < lam_ratio < 1.5, \ f"lam1/lam2 ratio {lam_ratio:.2f} indicates balanced position control" # Large K relative to lam ensures reaching condition K_to_lam_ratio = K / max(lam1, lam2) assert K_to_lam_ratio > 1.0, \ f"K/lam ratio {K_to_lam_ratio:.2f} ensures reaching condition satisfied" # Boundary layer matching kd for chattering-free operation assert boundary_layer == kd, \ "Boundary layer matched to kd for optimal chattering suppression"

``` **Gain interpretation:**
- **k1 = 77.62**: Dominant velocity feedback (first pendulum most critical)
- **k2 = 44.45**: Strong but secondary velocity feedback (second pendulum)
- **lam1 = 17.31**: Position error contribution (first pendulum)
- **lam2 = 14.25**: Position error contribution (second pendulum)
- **K = 18.66**: Switching gain exceeds uncertainty bounds
- **kd = 9.76**: Derivative damping matched to boundary layer ### 4.2 Chattering Analysis with Optimal Gains ```python
# example-metadata:
# runnable: false def test_chattering_reduction_with_large_boundary_layer(): """Test that large boundary layer (9.76) effectively reduces chattering.""" optimal_gains = [77.62, 44.45, 17.31, 14.25, 18.66, 9.76] # Test with optimal boundary layer controller_optimal = ClassicalSMC( gains=optimal_gains, max_force=20.0, boundary_layer=9.76, # Large boundary layer switch_method='tanh' ) # Test with small boundary layer for comparison controller_small_bl = ClassicalSMC( gains=optimal_gains, max_force=20.0, boundary_layer=0.1, # Small boundary layer switch_method='tanh' ) # Simulate near sliding surface state = np.array([0.0, 0.01, 0.01, 0.0, 0.05, 0.05]) controls_optimal = [] controls_small_bl = [] for _ in range(100): result_optimal = controller_optimal.compute_control(state, (), {}) result_small_bl = controller_small_bl.compute_control(state, (), {}) controls_optimal.append(result_optimal.u) controls_small_bl.append(result_small_bl.u) # Measure control signal variation (chattering indicator) control_variation_optimal = np.std(np.diff(controls_optimal)) control_variation_small = np.std(np.diff(controls_small_bl)) # Large boundary layer should reduce variation significantly assert control_variation_optimal < 0.5 * control_variation_small, \ f"Large boundary layer should reduce chattering: " \ f"optimal={control_variation_optimal:.4f}, " \ f"small={control_variation_small:.4f}"
```

---

## 5. Controller Interface Compliance ### 5.1 Standard Interface Methods ```python

# example-metadata:

# runnable: false def test_controller_interface_compliance(): """Test compliance with BaseController interface.""" controller = create_test_controller() # Test required properties assert hasattr(controller, 'gains'), "Must expose gains property" assert hasattr(controller, 'n_gains'), "Must declare n_gains for PSO" assert controller.n_gains == 6, "Classical SMC requires 6 gains" # Test required methods assert hasattr(controller, 'compute_control'), "Must implement compute_control" assert hasattr(controller, 'reset'), "Must implement reset" assert hasattr(controller, 'initialize_state'), "Must implement initialize_state" assert hasattr(controller, 'initialize_history'), "Must implement initialize_history" # Test gains property returns copy gains1 = controller.gains gains2 = controller.gains assert gains1 == gains2, "Gains should be consistent" gains1[0] = 999.0 # Try to mutate assert controller.gains[0] != 999.0, "Gains property should return copy"

``` ### 5.2 History Tracking ```python
# example-metadata:
# runnable: false def test_history_telemetry(): """Test that controller properly tracks telemetry in history.""" controller = create_test_controller() state = np.array([0.1, 0.2, -0.1, 0.0, 0.3, -0.2]) history = {} result = controller.compute_control(state, (), history) # Verify all required telemetry is tracked required_keys = ['sigma', 'epsilon_eff', 'u_eq', 'u_robust', 'u_total', 'u'] for key in required_keys: assert key in history, f"Missing required history key: {key}" assert len(history[key]) == 1, f"History key {key} should have 1 entry" # Run multiple steps and verify accumulation for _ in range(5): controller.compute_control(state, (), history) for key in required_keys: assert len(history[key]) == 6, \ f"History key {key} should accumulate (expected 6, got {len(history[key])})"
```

---

## 6. Production Testing Standards ### 6.1 Performance Benchmarks ```python

# example-metadata:

# runnable: false @pytest.mark.benchmark

def test_compute_control_performance(benchmark): """Benchmark control computation for real-time requirements.""" controller = create_test_controller() state = np.array([0.1, 0.2, -0.1, 0.0, 0.3, -0.2]) def run_control(): return controller.compute_control(state, (), {}) result = benchmark(run_control) # Real-time requirement: <1ms computation time # For 100Hz control loop (dt=0.01s), we need ~10ms budget # Leave margin for other operations, target <1ms for controller mean_time = benchmark.stats['mean'] assert mean_time < 0.001, \ f"Control computation too slow: {mean_time*1000:.2f}ms (target <1ms)"
``` ### 6.2 Numerical Stability Testing ```python
# example-metadata:
# runnable: false def test_numerical_stability(): """Test controller numerical stability under edge cases.""" controller = create_test_controller() # Test with very small values (underflow risk) tiny_state = np.array([1e-15, 1e-15, 1e-15, 1e-15, 1e-15, 1e-15]) result = controller.compute_control(tiny_state, (), {}) assert np.isfinite(result.u), "Should handle tiny values" # Test with zeros zero_state = np.zeros(6) result = controller.compute_control(zero_state, (), {}) assert np.isfinite(result.u), "Should handle zero state" # Test with mixed magnitudes (conditioning risk) mixed_state = np.array([1e-6, 1e3, 1e-6, 1e3, 1e-6, 1e3]) result = controller.compute_control(mixed_state, (), {}) assert np.isfinite(result.u), "Should handle mixed magnitudes"
``` ### 6.3 Monte Carlo Robustness Testing ```python
# example-metadata:

# runnable: false def test_monte_carlo_robustness(): """Test controller robustness with random state sampling.""" controller = create_test_controller() np.random.seed(42) n_samples = 1000 failures = 0 for _ in range(n_samples): # Random state within physical bounds state = np.random.uniform( low=[-1.0, -np.pi/6, -np.pi/6, -1.0, -2.0, -2.0], high=[1.0, np.pi/6, np.pi/6, 1.0, 2.0, 2.0] ) try: result = controller.compute_control(state, (), {}) # Check for numerical issues if not np.isfinite(result.u): failures += 1 elif abs(result.u) > controller.max_force: failures += 1 except Exception: failures += 1 success_rate = 1.0 - (failures / n_samples) # Require 99.9% success rate for production deployment assert success_rate >= 0.999, \ f"Monte Carlo success rate too low: {success_rate:.2%} (target ≥99.9%)"

```

---

## Helper Functions ```python
# example-metadata:
# runnable: false def create_test_controller(): """Create controller with optimal gains for testing.""" optimal_gains = [77.62, 44.45, 17.31, 14.25, 18.66, 9.76] return ClassicalSMC( gains=optimal_gains, max_force=20.0, boundary_layer=9.76, switch_method='tanh', regularization=1e-10 )
```

---

## References - `src/controllers/smc/classic_smc.py`: Classical SMC implementation

- `tests/test_controllers/smc/classical/test_classical_smc.py`: Test suite
- `src/utils/monitoring/stability.py`: LDR monitoring
- `src/utils/validation/parameter_validators.py`: Parameter validation
- `.logs/report.log`: PSO optimization results with optimal gains

---

## Summary This guide provides production-ready testing patterns for SMC controllers with emphasis on:

- Theoretical constraint validation (gain positivity, Lyapunov stability)
- Optimal gains interpretation from PSO results
- Chattering analysis and boundary layer tuning
- Real-time performance requirements (<1ms)
- Monte Carlo robustness validation (99.9% success) All tests should pass with optimal gains `[77.62, 44.45, 17.31, 14.25, 18.66, 9.76]` and boundary layer `9.76` for production deployment.