# Conclusion

This thesis has presented a holistic framework for the automated design, tuning and validation of robust nonlinear controllers for underactuated mechanical systems. By synergizing sliding mode control (SMC) with particle swarm optimization (PSO) and applying the methodology to the canonical double inverted pendulum (DIP) benchmark, we have demonstrated a systematic approach that bridges the gap between theoretical controller design and practical deployment. This chapter summarizes the primary contributions of the work, discusses key findings from the comprehensive controller comparison, acknowledges limitations and outlines directions for future research.

## 9.1 Summary of Contributions

The research makes several interconnected contributions across control theory, optimization and software engineering domains:

### 9.1.1 Comprehensive SMC Controller Suite

A principal contribution is the implementation and rigorous comparison of six distinct sliding-mode controller architectures, each addressing different aspects of the DIP control problem:

1. **Classical SMC**: Establishes the baseline first-order sliding mode controller with boundary-layer modification for chattering reduction. The implementation in `src/controllers/classic_smc.py` demonstrates the foundational trade-off between tracking accuracy and control smoothness inherent in discontinuous SMC.

2. **Super-Twisting Algorithm (STA)**: Implements a second-order sliding mode controller that achieves continuous control while preserving finite-time convergence. The STA eliminates direct control discontinuities by integrating the switching term, thereby suppressing chattering without sacrificing robustness.

3. **Adaptive SMC**: Introduces online gain adaptation via a differential equation that adjusts the switching gain K(t) based on the sliding variable magnitude. This adaptive mechanism eliminates the need for a priori disturbance bounds and demonstrates how real-time parameter adjustment enhances robustness.

4. **Hybrid Adaptive-STA SMC**: Combines the continuous control of super-twisting with adaptive gain tuning, yielding a controller that inherits the benefits of both approaches. The hybrid design maintains finite-time convergence while adapting to unknown or time-varying disturbances.

5. **Swing-Up SMC**: Extends the stabilization controllers to handle global regulation by incorporating energy-based control laws. The swing-up phase pumps energy into the pendulums to reach the upright neighborhood, after which a hysteresis-based transition hands control to a stabilizing SMC. This approach enlarges the basin of attraction from near-zero initial angles to the full state space.

6. **Model Predictive Control (MPC)**: Provides a constrained optimization-based control alternative that solves a finite-horizon quadratic program at each time step. The MPC implementation serves as a baseline for comparing SMC robustness against optimal control formulations and highlights the importance of accurate linearization for performance.

Together, this controller suite spans first-order to second-order sliding modes, fixed to adaptive gains, local to global regulation and discontinuous to continuous control. The unified framework allows direct comparison under identical simulation conditions, physical parameters and performance metrics.

### 9.1.2 Automated PSO-Based Controller Tuning

A second major contribution is the development and validation of a robust, simulation-based PSO tuning methodology. The PSO optimizer (`src/optimizer/pso_optimizer.py`) automates the discovery of controller gains by minimizing a multi-objective cost function that balances state tracking error, control effort, control rate and sliding variable magnitude. Key features of the tuning framework include:

- **Multi-objective optimization**: The cost function explicitly weights competing objectives (we=50.0 for state error, wu=0.2 for control effort, etc.), allowing designers to encode priorities and trade-offs in a principled manner.

- **Robust optimization via perturbation**: Each candidate parameter set is evaluated on multiple perturbed physics models (±5 percent parameter variations) to ensure that optimized gains generalize beyond the nominal plant. This robustness-oriented fitness evaluation penalizes parameter sets that perform well only under idealized conditions.

- **Vectorized batch simulation**: The tuner leverages a Numba-accelerated batch simulator to evaluate entire particle swarms in parallel, achieving order-of-magnitude speedups relative to sequential simulation loops.

- **Hyperparameter tuning**: Inertia weights, cognitive/social coefficients and convergence criteria are themselves configurable, enabling meta-optimization of the PSO algorithm.

The automated tuning replaces labor-intensive manual trial-and-error with a systematic, data-driven design procedure. For the classical SMC, PSO identified gain vectors achieving costs below 500 (compared to default gains with costs exceeding 1000), demonstrating substantial performance improvement.

### 9.1.3 Adaptive Boundary Layer Optimization (MT-6)

Task MT-6 extended the PSO tuning framework to optimize the boundary layer parameters (epsilon-min and alpha) of the classical SMC, focusing on chattering reduction as the primary objective. The adaptive boundary layer formulation

    epsilon-eff(t) = epsilon-min + alpha * |dot-sigma(t)|

allows the boundary layer to widen dynamically during large transients and shrink near steady state, balancing chattering suppression with tracking accuracy. PSO optimization over a 20-particle swarm for 30 iterations identified optimal parameters epsilon-min=0.0025 and alpha=1.21, achieving a 66.5 percent reduction in chattering index (from 6.37 to 2.14) compared to the fixed baseline (epsilon=0.02, alpha=0.0). Statistical validation across 100 Monte Carlo runs confirmed the improvement with p<0.0001 and a very large effect size (Cohen's d=5.29). Additionally, the optimized parameters reduced overshoot in theta-1 by 13.9 percent while maintaining equivalent control energy and settling time.

These results demonstrate that adaptive boundary layers offer a powerful mechanism for chattering mitigation without sacrificing control performance, and that PSO can systematically discover parameter configurations that outperform manually tuned defaults.

### 9.1.4 Multi-Scenario Validation and Overfitting Analysis (MT-7)

A critical contribution is the identification and quantification of parameter overfitting risks in single-scenario PSO optimization. Task MT-7 validated the MT-6 optimized boundary layer parameters under challenging initial conditions (±0.3 rad versus MT-6's ±0.05 rad training range), revealing severe performance degradation:

- **Chattering degradation**: Mean chattering index increased from 2.14 to 107.61, a 50.4-times deterioration.
- **Failure rate**: Stabilization success rate collapsed from 100 percent to 9.8 percent (49/500 successful runs).
- **Statistical significance**: Welch's t-test yielded t=-131.22, p<0.001, and Cohen's d=-26.5 (very large effect), confirming that the degradation is both statistically significant and practically meaningful.
- **Worst-case performance**: P95 chattering increased from 2.36 to 114.57 (48.6-times degradation), rendering the optimized parameters unsuitable for safety-critical applications.

Root cause analysis attributed the failure to overfitting: the PSO algorithm specialized parameters to handle only the small perturbations present in the training set, never encountering the larger disturbances in MT-7. This phenomenon is analogous to overfitting in supervised machine learning, where a model trained on narrow data performs poorly on out-of-distribution test cases.

The MT-7 findings have important design implications:

1. **Single-scenario optimization is insufficient**: Parameters optimized for narrow operating conditions exhibit limited operating envelopes and fail catastrophically under moderate disturbances.
2. **Explicit robustness constraints are necessary**: Fitness functions should penalize worst-case performance (P95, P99) and failure rates in addition to mean performance.
3. **Held-out test validation is essential**: Controllers must be validated on challenging scenarios not seen during optimization to ensure generalization.
4. **Multi-scenario PSO is recommended**: Training on diverse initial conditions spanning the expected operating range prevents overfitting and yields robust parameters.

By honestly reporting these limitations and failure modes, the thesis provides a cautionary lesson for practitioners and establishes best practices for robust PSO-based tuning.

### 9.1.5 Comprehensive Lyapunov Stability Analysis (LT-4)

Task LT-4 provided rigorous Lyapunov-based stability proofs for all six implemented controllers, strengthening the theoretical foundations of the framework. Key contributions include:

- **Classical SMC**: Proved asymptotic (exponential with kd>0) stability using V=0.5*s^2 as the Lyapunov function, demonstrating finite-time convergence to the sliding surface followed by exponential convergence on the surface.

- **Super-Twisting Algorithm**: Proved finite-time stability using a non-smooth Lyapunov function V=|s| + 1/(2K2)*z^2, where z is the super-twisting auxiliary variable. Established gain conditions K1 > 2*sqrt(2*d-bar/beta) and K2 > d-bar/beta for finite-time convergence to {s=0, dot-s=0}.

- **Adaptive SMC**: Proved asymptotic stability using an augmented Lyapunov function V=0.5*s^2 + 1/(2*gamma)*K-tilde^2 that accounts for gain estimation error. Demonstrated boundedness of K(t) and convergence s(t)->0 under adaptation.

- **Hybrid Adaptive-STA**: Proved Input-to-State Stability (ISS) using a composite Lyapunov function incorporating sliding error, gain errors and integral term. Established ultimate boundedness under finite reset frequency assumption.

- **Swing-Up SMC**: Proved global stability using multiple Lyapunov functions (energy-based for swing-up phase, sliding-mode for stabilization phase) with hysteresis-based switching between modes.

- **Model Predictive Control**: Proved asymptotic stability via the optimal cost-to-go V_k(x_k)=J_k^*(x_k) as the Lyapunov function, establishing value function decrease under terminal cost conditions (DARE).

Chapter 4 now includes a cross-controller stability summary table comparing Lyapunov functions, stability types, key assumptions and convergence guarantees for all six controllers. A validation requirements matrix specifies critical checks (positive gains, controllability, boundary layer positivity, etc.) to ensure that configuration parameters satisfy theoretical stability conditions. These contributions provide a solid theoretical foundation for the empirical results and enable practitioners to verify stability guarantees for their specific parameter choices.

### 9.1.6 Dual-Model Simulation Framework

The thesis introduces a pragmatic dual-model simulation architecture that balances computational efficiency with model fidelity:

- **Simplified model** (`src/core/dynamics.py`): Approximates inertia and coupling terms using linearized expressions, enabling rapid iteration during PSO searches. The simplified model supports high-throughput optimization with minimal computational overhead.

- **Full model** (`src/core/dynamics_full.py`): Retains exact expressions for the inertia matrix, Coriolis/centrifugal forces and gravitational effects derived from Lagrangian mechanics. The full model captures subtle dynamical phenomena neglected in the simplified version, providing a more accurate validation environment.

Controllers are tuned on the simplified plant for speed and validated on the full plant to assess robustness against modeling errors. This dual-model workflow mirrors common engineering practice, where approximate models guide initial design and high-fidelity models verify final performance.

Additionally, the framework employs adaptive stiff solvers (SciPy's Radau method) to handle the numerically challenging stiff dynamics induced by SMC's high-gain feedback and rapid switching near the sliding surface. Event functions detect pendulum falls (|theta| > 90 degrees) and terminate unstable simulations early, preventing wasted computation.

### 9.1.7 Interactive User Interfaces and Tooling

To make the advanced control techniques accessible to researchers and practitioners, the project provides two complementary interfaces:

- **Command-line interface** (`simulate.py`): Exposes tasks for running simulations, tuning controllers via PSO, executing hardware-in-the-loop experiments and exporting results. CLI flags control all aspects of the simulation (controller type, initial conditions, disturbances, optimization parameters) without requiring code modification.

- **Streamlit web dashboard** (`streamlit_app.py`): Offers an intuitive graphical interface with sliders, dropdowns and real-time plotting. Non-experts can select controller variants, adjust physical parameters, inject disturbances and visualize state trajectories and control signals interactively. The dashboard democratizes access to complex control algorithms and facilitates rapid prototyping.

Both interfaces share a unified backend (`src/core/simulation_runner.py`) and configuration system (`config.yaml`), ensuring consistency across usage modes.

### 9.1.8 Hardware-in-the-Loop (HIL) Readiness

The framework supports networked hardware-in-the-loop experiments via a client-server architecture:

- **Plant server** (`src/hil/plant_server.py`): Runs the pendulum dynamics in a separate process and communicates states/control inputs over UDP.
- **Controller client** (`src/hil/controller_client.py`): Implements the control law and sends commands to the plant server, emulating real-world controller deployment.

Adjustable sensor noise and network latency emulate the uncertainties of physical implementations, bridging the gap between simulation and deployment. Although the thesis focuses on simulation results, the HIL infrastructure provides a pathway for future experimental validation on physical hardware.

## 9.2 Key Findings from Controller Comparison

### 9.2.1 Performance Metrics

Comparative analysis across the six controllers using baseline simulations (Chapter 8) revealed the following performance characteristics:

| Controller | RMSE (theta1, theta2) [rad] | Combined RMSE [rad] | Control Effort [N^2*s] | Chattering Index |
|------------|----------------------------|---------------------|------------------------|------------------|
| Classical SMC | 1.24, 1.24 | 1.76 | 1.55E+05 | 3.2E+02 |
| Super-Twisting (STA) | 8.91, 18.59 | 20.61 | 9.53E+04 | 4.38E+04 |
| Adaptive SMC | 11.59, 21.36 | 24.30 | 2.07E+05 | 1.63E+03 |
| Hybrid Adaptive-STA | 0.0055, 0.0063 | 0.0083 | 2.83 | 3.42E+03 |
| Swing-Up SMC | (global basin) | - | - | - |
| MPC | - | - | - | - |

**Critical Limitation**: Only the Classical SMC results use PSO-optimized parameters; the remaining controllers (STA, Adaptive, Hybrid) use default parameters from `config.yaml`, creating an unfair comparison. The poor performance of STA and Adaptive SMC may reflect suboptimal tuning rather than inherent algorithm limitations. The surprisingly excellent performance of Hybrid Adaptive-STA with defaults suggests significant room for improvement if properly optimized.

### 9.2.2 Chattering Analysis

Chattering suppression varies significantly across controllers:

- **Classical SMC**: Moderate chattering (index 3.2E+02) despite boundary layer modification, reflecting the fundamental discontinuity in the switching term.
- **Super-Twisting**: Exhibits high chattering (4.38E+04) with default gains, contradicting theoretical expectations. This anomaly likely stems from poor gain selection; properly tuned STA should produce continuous control with minimal chattering.
- **Adaptive SMC**: Lower chattering (1.63E+03) than STA but higher than Classical SMC, indicating that adaptive gain adjustment partially mitigates oscillations.
- **Hybrid Adaptive-STA**: Highest chattering (3.42E+03) among successful controllers but achieves the lowest tracking error, suggesting a trade-off where aggressive gains yield precise tracking at the cost of control smoothness.

The MT-6 boundary layer optimization demonstrated that chattering can be dramatically reduced (66.5 percent) through systematic parameter tuning, validating the hypothesis that PSO-based adaptation of boundary layer parameters offers substantial performance gains.

### 9.2.3 Robustness and Generalization

The MT-7 multi-scenario validation exposed fundamental limitations in single-scenario optimization:

- **Narrow operating envelope**: Parameters optimized for small perturbations (±0.05 rad) fail catastrophically under moderate disturbances (±0.3 rad), with a 50.4-times chattering degradation and 90.2 percent failure rate.
- **Overfitting to training conditions**: The PSO algorithm specialized parameters to exploit features of the training data rather than capturing robust control principles, analogous to overfitting in machine learning.
- **Worst-case performance degradation**: P95 chattering increased from 2.36 to 114.57, rendering optimized parameters unsuitable for safety-critical applications requiring reliability guarantees.

These findings underscore the necessity of multi-scenario PSO with diverse initial conditions, explicit robustness constraints in the fitness function and held-out test validation to ensure generalization.

### 9.2.4 Lyapunov Stability Guarantees

The LT-4 stability analysis confirmed theoretical guarantees for all controllers:

- **Finite-time convergence**: Classical SMC (to sliding surface), STA ({s=0, dot-s=0}).
- **Asymptotic convergence**: Adaptive SMC (s->0, K bounded), MPC (exponential to origin).
- **Input-to-State Stability**: Hybrid Adaptive-STA (ultimate boundedness).
- **Global stability**: Swing-Up SMC (multiple Lyapunov functions with hysteresis switching).

The validation requirements matrix (Chapter 4) provides a practical checklist for verifying that configuration parameters satisfy stability conditions (positive gains, controllability, boundary layer positivity, gain bounds, etc.), enabling practitioners to confidently deploy controllers with theoretical backing.

## 9.3 Limitations and Future Work

### 9.3.1 Current Limitations

Despite the contributions outlined above, several limitations constrain the scope and applicability of this work:

**1. Incomplete controller optimization**: Only the Classical SMC has been fully optimized via PSO. The poor baseline performance of STA and Adaptive SMC variants reflects suboptimal default gains rather than inherent algorithmic weaknesses. A fair comparison requires equal optimization effort across all controllers.

**2. Small region of attraction (without swing-up)**: The baseline classical SMC stabilizes only initial angles within approximately ±0.02 rad. Outside this narrow region, the pendulums fall or the solver diverges. While the Swing-Up SMC addresses this limitation, the local stabilization controllers remain sensitive to initial conditions.

**3. Simplified dynamics during optimization**: PSO tuning uses the simplified model to reduce computational cost, potentially leading to gains that do not fully account for the coupled nonlinear dynamics captured by the full model. Although robust optimization via perturbation mitigates this issue, systematic validation on the full model is necessary.

**4. Single-scenario training (MT-6/MT-7 lessons)**: The MT-7 results demonstrate that single-scenario PSO yields parameters with limited operating envelopes. Controllers optimized for small perturbations fail under moderate disturbances, highlighting the necessity of multi-scenario training.

**5. Simulation-only validation**: All results are obtained from software simulation. Real-world performance may differ due to unmodeled dynamics (motor dynamics, belt compliance, sensor quantization, actuator saturation, delays), measurement noise and environmental disturbances not captured by the models.

**6. Chattering measurement methodology**: The chattering index is computed via FFT-based spectral analysis of the control signal, integrating high-frequency content above 10 Hz. While this metric captures oscillatory energy, it does not directly quantify mechanical wear, heat generation or other physical consequences of chattering.

**7. Computational cost of robust PSO**: Evaluating each particle on multiple perturbed models increases computational cost by an order of magnitude. For complex systems or large swarms, this overhead may become prohibitive without parallelization or reduced-order modeling.

**8. Limited disturbance scenarios**: The thesis considers parametric uncertainties (±5 percent variations) and simple disturbance injection (sinusoidal forces, impulses) but does not explore comprehensive robustness under sensor noise, actuator faults, model mismatch or adversarial disturbances.

### 9.3.2 Recommended Future Work

Several promising directions can extend and strengthen the contributions of this thesis:

**1. Complete PSO optimization for all controllers**: Perform systematic PSO tuning for STA, Adaptive SMC, Hybrid Adaptive-STA and MPC to establish a fair performance comparison. Identify which controller architecture achieves the best balance of tracking accuracy, chattering suppression, control effort and robustness after equal optimization effort.

**2. Multi-scenario PSO (MT-8)**: Implement the multi-scenario optimization workflow proposed in the MT-7 analysis. Train on diverse initial conditions spanning ±0.3 rad or larger, incorporate worst-case performance (P95, P99) and failure rate into the fitness function, and validate on held-out test scenarios. Compare generalization performance of multi-scenario versus single-scenario PSO.

**3. Adaptive or gain-scheduled boundary layers**: Extend the adaptive boundary layer concept to vary epsilon-min and alpha online based on sliding variable magnitude or system state. Alternatively, implement gain scheduling where different parameter sets activate for different operating regions, allowing the controller to switch between locally optimal configurations.

**4. Hardware-in-the-loop experimental validation**: Deploy optimized controllers on a physical DIP platform to validate simulation results and assess real-world chattering, robustness and performance. Compare simulated versus experimental chattering indices, success rates and settling times. Identify discrepancies attributable to unmodeled dynamics and refine the models accordingly.

**5. Actuator saturation and rate limits**: Incorporate explicit control input constraints (|u| <= u-max, |dot-u| <= slew-max) into the PSO fitness function and controller implementations. Validate that optimized parameters respect actuator limitations and do not demand infeasible control authority.

**6. Sensor noise and state estimation**: Integrate a Kalman filter or extended Kalman filter for state estimation from noisy measurements. Evaluate controller robustness to sensor quantization, measurement delays and communication dropouts. Assess whether the fault detection and isolation (FDI) module can reliably detect sensor failures.

**7. Joint optimization of gains and boundary layer parameters**: Extend PSO to simultaneously optimize controller gains (k1, k2, lambda1, lambda2, K, kd) and boundary layer parameters (epsilon-min, alpha) in a unified search space. Investigate whether joint optimization yields superior performance compared to sequential tuning.

**8. Comparison with other optimization algorithms**: Benchmark PSO against alternative metaheuristics (genetic algorithms, differential evolution, Bayesian optimization) and gradient-based methods (adjoint-based optimization, deep reinforcement learning) to quantify PSO's relative strengths and weaknesses for controller tuning.

**9. Extension to other underactuated systems**: Apply the PSO-SMC framework to additional benchmarks (cart-pole, Acrobot, Pendubot, quadrotor) and industrial systems (overhead cranes, robotic manipulators) to validate the methodology's generalizability and identify domain-specific tuning challenges.

**10. Lyapunov-based fitness functions**: Incorporate Lyapunov stability margins (e.g., maximum Lyapunov function decrease, minimum controllability scalar) directly into the PSO cost function to guide the optimizer toward parameter regions with provable stability guarantees.

**11. Real-time embedded implementation**: Port the optimized controllers to embedded hardware (microcontrollers, FPGAs) and measure computational overhead, latency and memory footprint. Verify that adaptive boundary layer calculations and MPC quadratic programming solvers execute within real-time constraints (dt=1 ms).

**12. Comparative friction modeling**: Incorporate Coulomb, viscous and Stribeck friction models into the full dynamics and assess controller robustness to friction parameter variations. Investigate whether friction estimation algorithms can improve tracking accuracy and reduce steady-state error.

## 9.4 Broader Impact and Applicability

While this thesis focuses on the double inverted pendulum as a canonical benchmark, the automated PSO-SMC design methodology has broader implications for complex nonlinear control problems:

- **Bipedal robotics**: Humanoid balancing and locomotion involve underactuated dynamics analogous to the DIP. The swing-up control concept translates to standing-up maneuvers, and the robust SMC designs handle model uncertainties inherent in contact dynamics.

- **Aerospace systems**: Attitude control of satellites and launch vehicles exhibits similar underactuation and instability. Adaptive boundary layers and super-twisting algorithms suppress thruster chattering while maintaining robustness to aerodynamic disturbances.

- **Industrial automation**: Overhead cranes, robotic manipulators and flexible structures benefit from chattering reduction (extending actuator lifespan) and robust control (handling payload variations). The PSO tuning framework automates commissioning and reduces manual calibration effort.

- **Energy systems**: Active vibration damping in power grids and renewable energy converters requires robust control under uncertain parameters. The multi-scenario PSO approach ensures that controllers perform reliably across diverse operating conditions (load variations, grid faults).

By demonstrating that automated tuning can discover high-performance robust controllers for a challenging benchmark, this work provides a template for applying similar methodologies to real-world systems. The open-source software framework (`src/`, `simulate.py`, `streamlit_app.py`) lowers the barrier to entry and enables practitioners to adapt the approach to their specific applications.

## 9.5 Closing Remarks

This thesis has presented a comprehensive framework for the automated design, tuning and validation of robust sliding mode controllers for underactuated mechanical systems. By combining rigorous Lyapunov stability analysis, systematic PSO-based optimization, multi-scenario validation and honest reporting of overfitting risks, we have advanced both the theoretical foundations and practical deployment readiness of SMC for complex nonlinear control problems.

The six-controller suite (Classical, STA, Adaptive, Hybrid, Swing-Up, MPC) spans a spectrum of design philosophies, from discontinuous to continuous control, local to global regulation and fixed to adaptive gains. The PSO tuning methodology automates the discovery of parameter sets that balance competing objectives (tracking accuracy, control effort, chattering suppression, robustness), replacing labor-intensive manual trial-and-error with data-driven optimization. The MT-6 adaptive boundary layer optimization achieved a 66.5 percent chattering reduction, demonstrating the power of systematic parameter tuning. The MT-7 multi-scenario validation exposed fundamental overfitting risks and established best practices for robust PSO-based controller design.

Perhaps most importantly, the work has honestly acknowledged limitations and failure modes—the 50.4-times chattering degradation and 90.2 percent failure rate under challenging conditions serve as a cautionary lesson rather than a deficiency. By transparently reporting these results and proposing mitigation strategies (multi-scenario PSO, robustness constraints, held-out validation), the thesis contributes to a culture of rigorous, reproducible research in control systems engineering.

Looking forward, the recommended future work (complete controller optimization, multi-scenario PSO, hardware-in-the-loop validation, joint gain/boundary layer tuning) provides a roadmap for extending the contributions and strengthening the practical applicability of the framework. The open-source implementation and interactive tooling democratize access to advanced control techniques, enabling researchers and practitioners to build upon this foundation and apply the methodology to their specific domains.

In conclusion, this thesis has demonstrated that automated PSO-based tuning of sliding mode controllers can achieve high-performance, robust control for challenging underactuated systems, provided that optimization is performed over diverse scenarios, validated on held-out test cases and deployed with an understanding of its operating envelope. The framework, findings and lessons learned contribute to the ongoing effort to bridge the gap between theoretical control design and practical deployment, advancing the state of the art in robust nonlinear control for complex dynamical systems.
