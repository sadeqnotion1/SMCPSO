# Sliding Mode Control for a Double‑Inverted Pendulum: Bridging Theory and Implementation

## Introduction – Why Sliding Mode Control?

The double‑inverted pendulum (DIP) is widely recognised as a **canonical benchmark** for the study of nonlinear, under‑actuated control systems. Inverted‑pendulum experiments have been used for decades to teach and validate control techniques; variants such as the rotational single‑arm pendulum, the cart pendulum and the **double inverted pendulum** offer escalating control challenges, and the inverted pendulum is often described as the most fundamental benchmark for robotics and control education \[1\]. In the DIP, two pendula are attached in series to a horizontally moving cart and only the cart is actuated. Consequently the system has fewer actuators than degrees of freedom and is both **under‑actuated** and **strongly nonlinear** \[2\]. Conventional linear controllers struggle with large deflections, parameter variations and model uncertainty.

Sliding Mode Control (SMC) addresses these issues by forcing the system state onto a pre‑defined **sliding manifold**. When the state reaches this manifold, the resulting closed‑loop dynamics become insensitive to matched disturbances and uncertainties \[3\]. The control law compensates modelling errors through the control input channel so that the plant behaves according to the reduced‑order dynamics on the manifold \[3\]. This robustness and finite‑time convergence make SMC attractive for under‑actuated systems such as the DIP. However, the discontinuous switching law of classic SMC induces **chattering**, a high‑frequency oscillation caused by rapid control switching when the state crosses the sliding surface. Chattering increases control effort, excites unmodelled high‑frequency modes and can cause wear in actuators. Introducing a boundary layer around the sliding surface alleviates chattering but enlarges the tracking error and slows the response \[4\].

To explore different trade‑offs between robustness, smoothness and complexity, this project implements four SMC variants – **classic (first‑order)**, **super‑twisting algorithm (STA)**, **adaptive SMC**, and **hybrid adaptive–STA**. Each variant is implemented in the provided Python code (`classic_smc.py`, `sta_smc.py`, `adaptive_smc.py`, `hybrid_adaptive_sta_smc.py`), and the following sections link the theory to these implementations.

### Structure of the report

The report is organised as follows. Each controller variant is presented with a concise theoretical background, a description of its implementation in the project, and an analysis of its practical implications. New sections map configuration parameters to mathematical symbols and discuss robustness issues such as singularity handling. A glossary of symbols and tables summarise the key results.

------------------------------------------------------------------------

## Variant I: Classic Sliding Mode Control (SMC)

### Principles and sliding surface

Classic SMC designs a linear **sliding surface** that combines position and velocity errors. For second‑order systems such as the DIP, the surface is typically a linear combination of the tracking error and its first derivative \[5\]. In this report the sliding surface is

    \sigma = \lambda_{1}\,\theta_{1} + \lambda_{2}\,\theta_{2} + k_{1}\,\dot{\theta}_{1} + k_{2}\,\dot{\theta}_{2},

where \(\theta_{i}\) are the pendulum angles, \(\dot{\theta}_{i}\) their angular velocities, and \(\lambda_{i}>0\) are design gains. The implementation computes the sliding variable in the `_compute_sliding_surface` method of `classic_smc.py`:

*“sigma = self.lam1 \* theta1 + self.lam2 \* theta2 + self.k1 \* dtheta1 + self.k2 \* dtheta2”* (see `classic_smc.py`), directly matching the equation above.

### Control law: equivalent and switching parts

The control input \u\ is decomposed into an **equivalent control** \u\_{\mathrm{eq}} that cancels the nominal dynamics and a **robust switching** term \u\_{\mathrm{sw}} that drives \(\sigma\) toward zero. This decomposition, often written as \(u = u_{eq} + u_{sw}\), is standard in sliding‑mode design \[5\]:

    u = u_{eq} - K\, sat\left( \frac{\sigma}{\epsilon} \right) - k_{d}\,\sigma.

#### Equivalent control computation

In `classic_smc.py` the `_compute_equivalent_control` method solves the dynamic equation of the DIP:

    M(q)\ddot{q} + C\left( q,\dot{q} \right)\dot{q} + G(q) = B\, u,

for the **cart force** \u\ required to satisfy \(\dot{\sigma}=0\). The inertia matrix \M(q)\ is computed from the physics parameters and then **regularised** by adding a small diagonal term. Before inversion the code checks the condition number of \M(q)\; if it is ill‑conditioned the method resorts to the pseudo‑inverse (`np.linalg.pinv`) to avoid numerical singularities. This careful handling prevents blow‑ups when the pendulum angles approach singular configurations. The resulting \u\_{\mathrm{eq}} is limited by the `max_force` parameter in the configuration.

#### Boundary layer and saturation

The switching term uses a **saturation function** to approximate the discontinuous sign function within a small **boundary layer** of width \(\epsilon\). Such smoothing reduces the chattering inherent in the discontinuous sign function, but it comes at a cost: introducing a boundary layer increases the tracking error and slows the response \[4\]. In the code, the `saturate` utility implements two approximations—a hyperbolic tangent (`method='tanh'`) and a linear clipping (`method='linear`)—that smooth the sign function. Figure 4.1 plots the ideal sign function alongside these saturations. Notice how both approximations approach the discontinuous sign outside the boundary layer and produce smoother transitions inside.

Saturation function approximations

*Figure 4.1 – Approximation of the sign function by the hyperbolic‑tangent and linear saturation methods. The boundary layer width \(\epsilon\) determines where the output transitions between −1 and 1.*

### Numerical robustness

The classic controller includes several robustness enhancements:
- **Condition‑number checking and regularisation:** The inertia matrix \M(q)\ is checked for ill‑conditioning and regularised by adding a small diagonal term (\(\varepsilon I\)). When ill‑conditioned, a pseudo‑inverse is used to compute the equivalent control.
- **Fallback control:** If the matrix inversion still fails due to singularity, the controller saturates the output to zero and returns an error flag, preventing instability.
- **Actuator saturation:** The control input is saturated by `max_force` to respect actuator limits.
These features make the classic SMC implementation stable and safe even when the model parameters deviate from their nominal values.

### Lyapunov Stability Analysis

The stability of classic SMC is rigorously established through Lyapunov theory. We use the simple quadratic Lyapunov function

$$V(s) = \frac{1}{2}s^{2},$$

which is positive definite and radially unbounded. Taking its time derivative along system trajectories yields

$$\dot{V} = s\,\dot{s}.$$

Outside the boundary layer \(|s| > \epsilon\), the saturation function becomes \(\mathrm{sat}(s/\epsilon) = \mathrm{sign}(s)\), and the control reduces to the discontinuous switching law. Assuming the equivalent control perfectly cancels the nominal dynamics and disturbances enter through the control channel (matched disturbances), the closed‑loop sliding‑surface dynamics satisfy

$$\dot{s} = \beta\,[-K\,\mathrm{sign}(s) - k_{d}\,s + d_{u}(t)],$$

where \(\beta = L\,M^{-1}B > 0\) is the controllability scalar and \(d_{u}(t)\) represents matched disturbances bounded by \(\bar{d}\). Substituting into \(\dot{V}\) and using \(s\,\mathrm{sign}(s) = |s|\), we obtain

$$\dot{V} \leq \beta\,[-K|s| + |s|\,\bar{d}] - \beta\,k_{d}\,s^{2}.$$

**Theorem (Classical SMC Asymptotic Stability):** If the switching gain satisfies \(K > \bar{d}\), then the sliding surface \(s\) converges asymptotically to zero. With \(k_{d} > 0\), convergence becomes exponential.

*Proof sketch:* Choosing \(K = \bar{d} + \eta\) for some \(\eta > 0\) ensures

$$\dot{V} \leq -\beta\,\eta\,|s| - \beta\,k_{d}\,s^{2} < 0 \quad \forall\,s \neq 0.$$

This strict negativity guarantees asymptotic stability by Lyapunov's direct method. The term \(-\beta\,\eta\,|s|\) provides a finite‑time reaching phase, driving the state onto the sliding surface in time \(t_{\mathrm{reach}} \leq |s(0)|/(\eta\beta)\). Once on the surface, the reduced‑order dynamics \(\dot{\theta}_{i} + \lambda_{i}\,\theta_{i} = 0\) guarantee exponential convergence of the pendulum angles to zero with rate \(\lambda_{i}\).

Inside the boundary layer \(|s| \leq \epsilon\), the saturation replaces the discontinuity with a continuous approximation, introducing a small steady‑state error. Standard boundary‑layer analysis shows that the ultimate bound satisfies

$$\limsup_{t \to \infty} |s(t)| \leq \frac{\bar{d}\,\epsilon}{K}.$$

Thus, reducing \(\epsilon\) tightens the tracking accuracy at the cost of increased chattering. The detailed proof and validation tests appear in `docs/theory/lyapunov_stability_proofs.md`.

**Key Conditions:**
- **Switching gain dominance:** \(K > \bar{d}\) ensures robustness to matched disturbances.
- **Controllability:** \(\beta = L\,M^{-1}B > 0\) must remain bounded away from zero to avoid singularity.
- **Positive sliding gains:** \(\lambda_{i}, k_{i} > 0\) define an attractive sliding manifold with exponential error dynamics.

These conditions are checked at runtime via the `controllability_threshold` parameter and enforced by gain validation in `config.yaml`.

------------------------------------------------------------------------

## Variant II: Super‑Twisting Algorithm (STA) SMC

### Theory and formulation

The **super‑twisting algorithm** (STA) is a second‑order sliding mode technique that suppresses chattering by applying the discontinuity on the **derivative** of the control signal rather than on the control itself. By moving the discontinuity to the derivative, the control input becomes continuous, which greatly reduces high‑frequency oscillations while preserving the robustness of sliding‑mode control and guaranteeing finite‑time convergence to the sliding set \[6\]. The sliding variable \(\sigma\) for the STA controller is similar to the classic one but is scaled by separate gains. In `sta_smc.py` it is computed as

    \sigma = k_{1}\,\left( {\dot{\theta}}_{1} + \lambda_{1}\,\theta_{1} \right) + k_{2}\,\left( {\dot{\theta}}_{2} + \lambda_{2}\,\theta_{2} \right).

The STA control comprises two components:

1.  **Continuous term** \(u_{c}=-K_{1}\sqrt{\|\sigma\|}\,\mathrm{sgn}(\sigma)\); this term acts like a damping force proportional to \(\sqrt{\|\sigma\|}\).
2.  **Integral term** \(u_{i}\) generated by integrating the sign of \(\sigma\): the internal state \(z\) is updated as \(z\leftarrow z - K_{2}\,\mathrm{sgn}(\sigma)\,\mathrm{d}t\). The integral of the discontinuity produces a continuous control signal, effectively moving the discontinuity to its derivative.

The total control is \(u = u_{\mathrm{eq}} + u_{c} + z\). Because the discontinuity is applied to the derivative rather than to the control itself, the resulting control law is continuous and enforces finite‑time convergence of both the sliding variable and its derivative \[6\].  In our implementation the internal integrator for \(z\) is updated explicitly using the time step `dt`; the previously supported `semi_implicit` configuration key has been removed from the code and should not appear in `config.yaml`.

### Lyapunov stability and numerical verification

A Lyapunov function \(V=\tfrac12\sigma^{2}\) can be shown to decrease along system trajectories under the STA law, guaranteeing finite‑time convergence of both \(\sigma\) and \(\dot{\sigma}\) to zero. The project includes a test, `test_lyapunov_decrease_sta` in `tests/test_core/test_lyapunov.py`, that numerically confirms this property. The test evaluates \(V\) at successive time steps and asserts that \(V(t_{i+1}) < V(t_{i})\). This demonstrates that the implementation adheres to the theoretical stability proof and that the STA drives the system to the origin in the \((\sigma,\dot{\sigma})\)-plane more aggressively than classic SMC.

### Tuning guidance

Tuning the STA gains \(K_{1}\) and \(K_{2}\) is crucial. In practice:

- **\(K_{1}\)** determines the magnitude of the continuous term. It should be larger than the maximum possible derivative of the disturbance to ensure finite‑time convergence. Increasing \(K_{1}\) accelerates convergence but can amplify control effort.
- **\(K_{2}\)** governs the integral action. A higher \(K_{2}\) increases the speed of the integral term, improving sliding accuracy, but excessive \(K_{2}\) may cause oscillations. Selecting \(K_{2}\approx K_{1}\) is common to balance the proportional and integral actions.

The configuration file allows setting `K1_init` and `K2_init` for the hybrid controller and similar parameters for the pure STA controller under the `gains` entry. The `dt` parameter controls integration accuracy.

### Formal Stability Guarantees

The STA controller achieves stronger convergence properties than classic SMC by enforcing second‑order sliding mode, which drives both the sliding variable and its derivative to zero in finite time. The stability proof relies on a non‑smooth Lyapunov function that accommodates the square‑root nonlinearity in the control law. We use the generalised Lyapunov candidate

$$V(s,z) = |s| + \frac{1}{2K_{2}}\,z^{2},$$

where \(z\) is the internal integrator state. This function is continuous everywhere but has an undefined classical derivative at \(s=0\); hence we employ Clarke's generalised gradient to analyse its evolution. For \(s \neq 0\), the ordinary derivative exists and satisfies

$$\dot{V} = \mathrm{sign}(s)\,\dot{s} + \frac{z}{K_{2}}\,\dot{z}.$$

Substituting the STA dynamics \(\dot{s} = \beta\,[-K_{1}\sqrt{|s|}\,\mathrm{sign}(s) + z + d_{u}(t)]\) and \(\dot{z} = -K_{2}\,\mathrm{sign}(s)\), and assuming the disturbance derivative satisfies a Lipschitz bound \(|\dot{d}_{u}| \leq L\), one can show that

$$\dot{V} \leq -c_{1}\,\|\xi\|^{3/2} + c_{2}\,L,$$

where \(\xi = [|s|^{1/2}\,\mathrm{sign}(s),\,z]^{T}\) is an augmented state vector and \(c_{1},c_{2}\) are positive constants determined by \(K_{1}\) and \(K_{2}\). This inequality establishes finite‑time convergence to a residual neighbourhood of the origin whose size depends on the disturbance Lipschitz constant.

**Theorem (STA Finite‑Time Convergence):** If the algorithmic gains satisfy the conditions

$$K_{1} > \frac{2\sqrt{2\bar{d}}}{\sqrt{\beta}}, \quad K_{2} > \frac{\bar{d}}{\beta},$$

then the super‑twisting algorithm drives the pair \((s,\dot{s})\) to zero in finite time, achieving exact second‑order sliding mode in the absence of unmatched disturbances.

*Proof sketch:* The gain conditions ensure that the negative term \(-c_{1}\|\xi\|^{3/2}\) dominates the disturbance contribution when the state is far from the origin. The homogeneity property of the STA dynamics guarantees that the settling time is bounded and independent of initial conditions beyond a certain threshold. A detailed proof using strict Lyapunov functions appears in Moreno and Osorio (2012) and is summarised in `docs/theory/lyapunov_stability_proofs.md`.

The boundary‑layer approximation used in the implementation introduces a small neighbourhood around \(s=0\) where the sign function is replaced by a saturation. This regularisation preserves finite‑time convergence outside the boundary layer and ensures continuous control, but it incurs a steady‑state error of order \(\mathcal{O}(\epsilon)\). The numerical test `test_lyapunov_decrease_sta` in `tests/test_core/test_lyapunov.py` verifies that \(V(t_{i+1}) < V(t_{i})\) throughout the simulation, confirming that the implementation adheres to the theoretical stability guarantees.

**Key Conditions:**
- **Gain dominance:** \(K_{1}\) and \(K_{2}\) must exceed the disturbance bounds scaled by the controllability factor \(\beta\).
- **Gain ordering:** Typically \(K_{1} \approx K_{2}\) or \(K_{1} > K_{2}\) to balance proportional and integral actions.
- **Lipschitz disturbances:** The disturbance derivative must be bounded to ensure finite settling time.

These conditions are enforced through parameter validation in `config.yaml` and runtime monitoring of the controllability scalar.

------------------------------------------------------------------------

## Variant III: Adaptive SMC

### Adaptation law and dead zone

Adaptive SMC adjusts the switching gain \(K\) on‑line to compensate for unknown disturbance bounds. Rather than fixing \(K\) using the worst‑case disturbance, the controller updates \(K(t)\) according to an adaptation law that increases the gain when the system is far from the sliding manifold and decreases it when the state enters a neighbourhood of the manifold. This approach eliminates the need for a priori knowledge of the disturbance bound and avoids overly conservative gains \[7\]. In `adaptive_smc.py`, the `compute_control` method implements the adaptation:

1. When \(|\sigma|\) exceeds a specified **dead zone** (parameter `dead_zone`), the switching gain grows proportionally to \(|\sigma|\).  Increasing the gain outside the dead zone enlarges the disturbance bound and improves robustness when the state is far from the sliding manifold.  This piece‑wise adaptation strategy is supported by nonlinear control theory: adaptive sliding‑mode controllers that allow the gain to increase until the sliding mode occurs and then decrease once the state enters a neighbourhood of the manifold achieve semi‑global stability without requiring a priori disturbance bounds \[8\].
2. Inside the dead zone the gain is held constant or allowed to decay slowly.  Decreasing the gain in this neighbourhood prevents unnecessary wind‑up and reduces chattering caused by measurement noise.  The nominal gain value is recovered through a leak term (`leak_rate`) and the growth rate is limited by `adapt_rate_limit` to avoid abrupt changes.

The gain is confined between `K_min` and `K_max` to prevent unbounded growth. A leak term (`leak_rate`) pulls the gain back toward its nominal value and prevents indefinite wind‑up. An additional limit (`adapt_rate_limit`) restricts how quickly the gain can change, avoiding abrupt jumps during adaptation.

### Practical considerations

Adaptive SMC eliminates the need for prior knowledge of disturbance bounds and produces a continuous control signal, reducing chattering. However, it introduces additional parameters (adaptation rate, leak rate, dead zone) that require tuning and may yield slower transient response compared to fixed‑gain SMC if tuned conservatively.

### Lyapunov-Based Stability Proof

The adaptive switching gain \(K(t)\) evolves online to compensate for unknown disturbance bounds, and the stability analysis must account for both the sliding error \(s\) and the parameter estimation error \(\tilde{K} = K(t) - K^{*}\), where \(K^{*}\) is the ideal (but unknown) gain satisfying \(K^{*} \geq \bar{d}\). We employ a composite Lyapunov function that penalises both tracking error and parameter mismatch:

$$V(s,\tilde{K}) = \frac{1}{2}s^{2} + \frac{1}{2\gamma}\,\tilde{K}^{2},$$

where \(\gamma > 0\) is the adaptation rate. The first term measures the distance from the sliding surface, and the second term quantifies the estimation error scaled by the inverse adaptation rate. Taking the time derivative yields

$$\dot{V} = s\,\dot{s} + \frac{1}{\gamma}\,\tilde{K}\,\dot{\tilde{K}}.$$

Outside the dead zone \(|s| > \delta\), the adaptation law updates the gain as \(\dot{K} = \gamma\,|s| - \lambda(K - K_{\mathrm{init}})\), where the leak term \(-\lambda(K - K_{\mathrm{init}})\) prevents unbounded growth. Substituting the closed‑loop dynamics \(\dot{s} = \beta\,[-K(t)\,\mathrm{sign}(s) - \alpha\,s + d_{u}(t)]\) and using \(\tilde{K} = K - K^{*}\), we obtain

$$\dot{V} = -\beta\,K^{*}\,|s| - \beta\,\alpha\,s^{2} + \beta\,s\,d_{u}(t) + \tilde{K}\,|s| - \frac{\lambda}{\gamma}\,\tilde{K}(K - K_{\mathrm{init}}).$$

The cross‑term \(\tilde{K}\,|s|\) arises from the parameter error coupling with the sliding variable; it cancels the corresponding term in \(s\,\dot{s}\), leaving

$$\dot{V} \leq -\beta(K^{*} - \bar{d})\,|s| - \beta\,\alpha\,s^{2} - \frac{\lambda}{\gamma}\,\tilde{K}^{2} + \frac{\lambda}{\gamma}\,|\tilde{K}|\,|K - K_{\mathrm{init}}|.$$

**Theorem (Adaptive SMC Asymptotic Stability):** If an ideal gain \(K^{*} \geq \bar{d}\) exists and the parameters satisfy \(\gamma,\lambda,\alpha > 0\), then all signals \((s,K)\) remain bounded and the sliding variable converges to zero asymptotically: \(\lim_{t \to \infty} s(t) = 0\).

*Proof sketch:* The Lyapunov derivative is negative definite when \((s,\tilde{K})\) are sufficiently large, establishing boundedness by standard Lyapunov arguments. The integral of \(\dot{V}\) over \([0,\infty)\) is finite, so \(V(t)\) converges to a limit. Applying Barbalat's lemma, \(\dot{V} \to 0\) implies \(s(t) \to 0\) as \(t \to \infty\). The parameter \(K(t)\) may not converge to \(K^{*}\) (persistent excitation is absent), but it remains bounded within \([K_{\min}, K_{\max}]\). A detailed proof appears in Roy (2020) and is reproduced in `docs/theory/lyapunov_stability_proofs.md`.

Inside the dead zone \(|s| \leq \delta\), adaptation is frozen (\(\dot{K} = 0\)), and the Lyapunov derivative reduces to \(s\,\dot{s}\), which remains negative as long as \(K(t) > \bar{d}\). This condition is guaranteed by proper initialisation and the adaptation law's monotonic increase when needed.

**Key Conditions:**
- **Ideal gain existence:** There must exist \(K^{*} \geq \bar{d}\) to ensure the disturbance can be rejected.
- **Positive adaptation rate:** \(\gamma > 0\) enables the gain to grow in response to large errors.
- **Leak rate:** \(\lambda > 0\) prevents unbounded growth and pulls \(K\) back toward the nominal value.
- **Gain bounds:** \(K_{\min} \leq K_{\mathrm{init}} \leq K_{\max}\) confine the adaptation to a safe interval.

These parameters are specified in `config.yaml` and validated at runtime to ensure the stability conditions hold throughout the simulation.

------------------------------------------------------------------------

## Variant IV: Hybrid Adaptive–STA SMC

### Unified sliding surface and recentering

The hybrid controller combines the adaptive law with the super‑twisting algorithm using a **single sliding surface** that captures both pendulum dynamics and cart recentering.  By default the sliding surface uses absolute joint coordinates:

\[
\sigma = c_{1}\,(\dot{\theta}_{1} + \lambda_{1}\,\theta_{1}) + c_{2}\,(\dot{\theta}_{2} + \lambda_{2}\,\theta_{2}) + k_{c}\,(\dot{x} + \lambda_{c}\,x),
\]

where \(c_{i}>0\) and \(\lambda_{i}>0\) weight the pendulum angle and velocity errors, and \(k_{c}\), \(\lambda_{c}\) weight the cart velocity and position in the sliding manifold.  Selecting **positive coefficients** ensures that the sliding manifold is attractive and defines a stable reduced‑order error surface—this is a standard requirement in sliding‑mode design【895515998216162†L326-L329】.  The terms involving the cart state encourage the cart to recenter without destabilising the pendula.  The implementation also supports a **relative formulation** in which the second pendulum is represented by \(\theta_{2}-\theta_{1}\) and \(\dot{\theta}_{2}-\dot{\theta}_{1}\); users can enable this mode with `use_relative_surface=True` to study coupled pendulum dynamics.  Keeping both options accessible avoids hard‑coding a specific manifold and lets users explore alternative designs.

The PD recentering behaviour is further reinforced by separate proportional–derivative gains \(p_{\mathrm{gain}}\) and \(p_{\lambda}\) applied to the cart velocity and position.  These gains shape the transient response of the cart and are exposed as `cart_p_gain` and `cart_p_lambda` in the configuration.

### Super‑twisting with adaptive gains

The hybrid control input consists of an equivalent part, a **super‑twisting continuous term** and an **integral term**.  The continuous term uses the square‑root law from the STA, \(-k_{1}\sqrt{\|\sigma\|}\,\mathrm{sgn}(\sigma)\), while the integral term \(z\) obeys \(\dot{z} = -k_{2}\,\mathrm{sgn}(\sigma)\).  Both gains \(k_{1}\) and \(k_{2}\) adapt online according to the same dead‑zone logic as in the adaptive SMC: when \(|\sigma|\) exceeds the dead‑zone threshold, the gains increase proportionally to \(|\sigma|\); inside the dead zone they are held constant or allowed to decay slowly.  To prevent runaway adaptation the gains are clipped at configurable maxima ``k1_max`` and ``k2_max``, and the integral term ``u_int`` is limited by ``u_int_max``.  Separating these bounds from the actuator saturation ensures that adaptation can proceed even when the actuator saturates【895515998216162†L326-L329】.  The equivalent control term \(u_{\mathrm{eq}}\) is **enabled by default**; it can be disabled via `enable_equivalent=False` if a purely sliding‑mode law is desired.  This piece‑wise adaptation law is supported by recent research showing that the gain should increase until sliding occurs and then decrease once the trajectory enters a neighbourhood of the manifold to avoid over‑estimation【462167782799487†L186-L195】.

### Advantages and tuning

The hybrid adaptive–STA controller inherits the robustness of second‑order sliding mode and the flexibility of adaptive gain scheduling while remaining simpler than earlier dual‑surface designs.  Its unified sliding surface ensures consistent dynamics across all modes, and the adaptive gains allow the controller to handle unknown disturbance bounds without a priori tuning.  However, this comes at the expense of additional parameters: the sliding surface weights \(c_{1},c_{2},\lambda_{1},\lambda_{2},k_{c},\lambda_{c}\), the PD recentering gains \(p_{\mathrm{gain}},p_{\lambda}\), adaptation rates and dead‑zone widths.  Careful tuning of these parameters is essential to balance response speed, robustness and chattering.

### Stability Analysis via Input-to-State Framework

The hybrid controller's stability analysis is more involved than the previous variants because of the emergency reset logic implemented in `hybrid_adaptive_sta_smc.py`. When the system detects singularity or actuator saturation, it can reset the control input to zero and drastically reduce the adaptive gains \(k_{1}\) and \(k_{2}\). These resets introduce discontinuities in the Lyapunov function that preclude monotonic decrease, so we adopt an Input‑to‑State Stability (ISS) framework that treats emergency resets as exogenous disturbances.

We define the composite Lyapunov candidate

$$V(s,k_{1},k_{2},u_{\mathrm{int}}) = \frac{1}{2}s^{2} + \frac{1}{2\gamma_{1}}(k_{1} - k_{1}^{*})^{2} + \frac{1}{2\gamma_{2}}(k_{2} - k_{2}^{*})^{2} + \frac{1}{2}u_{\mathrm{int}}^{2},$$

where \(k_{1}^{*}\) and \(k_{2}^{*}\) are ideal super‑twisting gains satisfying the stability conditions from Variant II, and \(u_{\mathrm{int}}\) is the integral term. Between emergency resets, the adaptation laws \(\dot{k}_{1} = \gamma_{1}\,|s|\,\mathrm{taper}(|s|) - \lambda_{\mathrm{leak}}\) and \(\dot{k}_{2} = \gamma_{2}\,|s|\,\mathrm{taper}(|s|) - \lambda_{\mathrm{leak}}\) cause the Lyapunov derivative to satisfy

$$\dot{V} \leq -\alpha_{1}\,V + \alpha_{2}\,\|\mathbf{d}(t)\|,$$

for positive constants \(\alpha_{1},\alpha_{2}\), establishing exponential decay toward a disturbance‑dependent neighbourhood. At reset instants, \(V\) may jump upward by an amount \(\Delta V_{\mathrm{reset}}\) bounded by the initial gain values and integrator state.

**Theorem (Hybrid SMC Input‑to‑State Stability):** If emergency resets occur at most \(N_{\mathrm{reset}}\) times per unit time (finite reset frequency) and the super‑twisting gain conditions hold between resets, then the closed‑loop system is Input‑to‑State Stable and all signals remain bounded.

*Proof sketch:* Using a comparison lemma, the Lyapunov function satisfies

$$V(t) \leq e^{-\alpha_{1}t}\,V(0) + \sum_{i=1}^{N_{\mathrm{reset}}} \Delta V_{\mathrm{reset}}\,e^{-\alpha_{1}(t - t_{i})},$$

where \(t_{i}\) are the reset times. If the reset frequency is bounded, the sum remains finite and \(V(t)\) is uniformly bounded for all \(t \geq 0\). This ISS property is weaker than asymptotic stability but appropriate for systems with safety resets. The key requirement is that resets do not occur infinitely often in finite time (no Zeno behaviour); the hysteresis in the dead‑zone logic and the tapering function \(\mathrm{taper}(|s|) = |s|/(|s| + \epsilon_{\mathrm{taper}})\) prevent rapid oscillations near the origin and ensure finite switching. A complete ISS proof using dwell‑time arguments appears in Khalil (2002) and is adapted to the hybrid controller in `docs/theory/lyapunov_stability_proofs.md`.

In practice, the reset logic is invoked only during transient phases or under severe disturbances; during normal operation the controller behaves like a standard adaptive STA with exponential convergence. Logging emergency reset events during simulation allows verification that the finite‑frequency assumption holds.

**Key Conditions:**
- **Finite reset frequency:** Resets must not occur infinitely often, ensured by dead‑zone hysteresis and tapering.
- **Gain dominance:** Between resets, \(k_{1}\) and \(k_{2}\) must satisfy the STA stability conditions.
- **Positive parameters:** \(c_{1},c_{2},\lambda_{1},\lambda_{2},\gamma_{1},\gamma_{2},k_{d} > 0\) and proper initialisation within \([k_{i,\min}, k_{i,\max}]\).

These conditions are validated through runtime monitoring and parameter checks in `config.yaml`.

------------------------------------------------------------------------

## New Section: Controller Configuration and `config.yaml`

The `config.yaml` file defines tunable parameters for each controller. Mapping these keys to the mathematical symbols used in the theory clarifies how to adjust the controllers in practice. Table 1–4 summarise the mappings for each variant.

### Classical SMC

| `config.yaml` key | Mathematical symbol(s) | Description |
|----|----|----|
| `gains` (in `controller_defaults`) | \(\lambda_{1},\lambda_{2},k_{1},k_{2},K,k_{\mathrm{d}}\) | Initial values for sliding surface weights (\(\lambda_{1},\lambda_{2}\)), velocity gains (\(k_{1},k_{2}\)), switching gain \(K\) and damping gain \(k_{\mathrm{d}}\). They appear in \(\sigma\) and \(u_{\mathrm{sw}}\). |
| `boundary_layer` | \(\epsilon\) | Half‑width of the boundary layer used in the saturation function. |
| `max_force` | Saturation limit | Maximum magnitude of the control input \(u\). |
| `controllability_threshold` | – | Lower bound on \(|L\cdot M^{-1}\cdot B|\) used to decide when to compute the equivalent control. If \(|L\cdot M^{-1}\cdot B|\) falls below this threshold, the feedforward term is disabled to avoid amplification of ill‑conditioned inversions.  Defaults to \(10^{-4}\) when omitted. |
<!-- Removed `rate_weight` and `use_adaptive_boundary` rows as these parameters are no longer used in the implementation. -->

### Super‑Twisting SMC

| `config.yaml` key | Mathematical symbol(s) | Description |
|----|----|----|
| `gains` | \(\lambda_{1},\lambda_{2},k_{1},K_{1},K_{2},k_{\mathrm{d}}\) | Sliding surface weights, velocity gains, super‑twisting proportional gain \(K_{1}\), integral gain \(K_{2}\) and optional damping gain. |
| `damping_gain` | \(k_{\mathrm{d}}\) | Linear damping added to the control law. |
| `dt` | \(\mathrm{d}t\) | Integration time step for updating the internal state \(z\). |
| `max_force` | Saturation limit | Maximum control magnitude. |
<!-- Removed `semi_implicit` and `rate_weight` parameters as they are no longer used. -->

### Adaptive SMC

| `config.yaml` key | Mathematical symbol(s) | Description |
|----|----|----|
| `gains` | \(\lambda_{1},\lambda_{2},k_{1},k_{2},K_{0}\) | Initial sliding surface and switching gain values. |
<!-- Removed `rate_weight` row; the updated controller does not include a control‑rate term. -->
| `leak_rate` | \(\alpha\) | Forgetting factor that allows the adaptive gain to decay when disturbances subside. |
| `dead_zone` | \(\delta\) | Dead‑zone width for suppressing gain growth when \(|\sigma|\) is small. |
| `adapt_rate_limit` | \(\Gamma_{\max}\) | Upper limit on how fast the gain can grow. |
| `K_{\min}`, `K_{\max}` | \(K_{\min},K_{\max}\) | Hard bounds on the adaptive gain. |
| `dt` | \(\mathrm{d}t\) | Time step for numerical integration. |
| `smooth_switch` | – | If true, uses a smooth transition function to improve continuity near switching events. |
| `boundary_layer` | \(\epsilon\) | Boundary layer width for the saturation function. |

### Hybrid Adaptive–STA SMC

| `config.yaml` key | Mathematical symbol(s) | Description |
|----|----|----|
| `gains` (in `controller_defaults`) | \(c_{1},\lambda_{1},c_{2},\lambda_{2}\) | Gains defining the sliding surfaces: \(c_{1}\), \(c_{2}\) scale the velocity terms and \(\lambda_{1},\lambda_{2}\) the position terms. |
| `max_force` | Saturation limit | Maximum cart force. |
| `dt` | \(\mathrm{d}t\) | Time step used for updating adaptive gains and the STA integrator. |
| `k1_init`, `k2_init` | \(k_{1}(0),k_{2}(0)\) | Initial values for the adaptive super‑twisting gains. |
| `gamma1`, `gamma2` | \(\gamma_{1},\gamma_{2}\) | Adaptation rates for \(k_{1}\) and \(k_{2}\) respectively. Larger values yield faster adaptation but can increase oscillatory behaviour. |
| `dead_zone` | \(\delta\) | Dead‑zone width preventing gain wind‑up due to noise. |
| `enable_equivalent` | – | If true, includes an equivalent control term computed from the system dynamics.  This option replaces the deprecated `use_equivalent` flag, which is still accepted as an alias.  The equivalent control is **enabled by default** in the revised implementation. |
| `use_relative_surface` | – | When true, defines the sliding surface using relative coordinates \(\theta_{2}-\theta_{1}\) and \(\dot{\theta}_{2}-\dot{\theta}_{1}\).  When false (default), uses absolute angles.  This switch allows users to explore alternative manifold definitions without modifying code. |
| `k1_max`, `k2_max` | – | Maximum allowed values for the adaptive gains \(k_{1}\) and \(k_{2}\).  Bounding these gains independently of the actuator limit prevents runaway adaptation and preserves stability【895515998216162†L326-L329】. |
| `u_int_max` | – | Maximum absolute value of the integral term in the super‑twisting algorithm.  Decoupling this bound from `max_force` avoids overly conservative integral clipping and improves robustness. |
| `damping_gain` | \(k_{\mathrm{d}}\) | Linear damping gain applied to the super‑twisting control. |
| `adapt_rate_limit` | \(\Gamma_{\max}\) | Maximum rate of change allowed for the adaptive super‑twisting gains. |
| `sat_soft_width` | \(\delta_{\mathrm{soft}}\) | Width of the soft saturation used in the adaptation law to smooth transitions near the dead zone. |
| `cart_gain` | \(k_{c}\) | Weight applied to the cart velocity and position in the sliding surface for recentering. |
| `cart_lambda` | \(\lambda_{c}\) | Rate applied to the cart position term in the sliding surface. |
| `cart_p_gain` | \(p_{\mathrm{gain}}\) | Proportional gain for the cart recentering term. |
| `cart_p_lambda` | \(p_{\lambda}\) | Derivative gain for the cart recentering term. |

These tables enable practitioners to relate the theoretical parameters (gains, boundary layer, adaptation rates) to the YAML file used to configure the controllers.

------------------------------------------------------------------------

## New Section: Robustness and Singularity Handling

High‑performance control of the DIP requires careful handling of numerical issues and singularities inherent in the dynamic model. The inertia matrix \M(q)\ can become ill‑conditioned when the pendulum angles approach certain configurations, leading to large rounding errors in its inversion. The implementation addresses these problems as follows:

- **Condition‑number checking:** The `_compute_equivalent_control` method in both `classic_smc.py` and `sta_smc.py` computes the condition number of \M(q)\ (`np.linalg.cond`). If the condition number exceeds a threshold (`singularity_cond_threshold` in `config.yaml`), the method logs a warning and uses a pseudo‑inverse instead of the standard inverse.
- **Matrix regularisation:** To prevent singularities due to modelling uncertainties, a small regularisation term \(\varepsilon I\) is added to \M(q)\ before inversion. This ensures that \(M(q)+\varepsilon I\) is always invertible, albeit with some approximation error.
- **Safe inversion with pseudo‑inverse:** When the matrix is ill‑conditioned, the code uses `np.linalg.pinv`, which computes the Moore–Penrose pseudo‑inverse and yields a least‑squares solution that minimises the effect of noise.
- **Regularisation justification:**  Adding a positive constant to the diagonal of a symmetric matrix shifts all of its eigenvalues upward and can convert an indefinite matrix into a positive‑definite one【385796022798831†L145-L149】.  This mathematical result justifies the use of the diagonal regularisation term \(\varepsilon I\): by perturbing \(M(q)\) in this way, \(M(q)+\varepsilon I\) remains invertible even when \(M(q)\) is nearly singular, though at the cost of a small approximation error.
- **Fallback control:** If the pseudo‑inverse computation still fails (for example, if the system becomes uncontrollable), the controller saturates the output to zero and reports failure rather than producing unbounded values. This conservative action prevents destabilisation.

By systematically checking for singularities and regularising the matrix inversion, the project ensures that the control law remains well‑defined even when the physical system operates near its limits or when the model parameters are uncertain.

------------------------------------------------------------------------

## Variant V: Model Predictive Control (MPC)

### Formulation and System Model

Model Predictive Control (MPC) is an optimal control strategy that solves a finite‑horizon optimization problem at each time step. Unlike the sliding‑mode controllers, MPC uses a **linearised model** of the DIP dynamics around the upright equilibrium and optimizes a quadratic cost subject to state and input constraints. The linearisation is obtained by computing Jacobians of the nonlinear dynamics:

    A_c = ∂f/∂x|(x_eq, u_eq),    B_c = ∂f/∂u|(x_eq, u_eq),

where x_eq = [q_eq, 0] and q_eq = [x_0, π, π] is the upright configuration. The continuous‑time system is then discretised using zero‑order hold or forward Euler with sampling period Δt, yielding the discrete‑time model

    x_{k+1} = A_d x_k + B_d u_k.

At each time step k, the MPC solves the optimization

    min_{U} J_k(x_k, U) = Σ_{i=0}^{N-1} ℓ(x_{k+i|k}, u_{k+i|k}) + V_f(x_{k+N|k}),

where the **stage cost** ℓ(x, u) = x^T Q x + u^T R u penalises deviation from the upright equilibrium and control effort, the **terminal cost** V_f(x) = x^T Q_f x encourages convergence at the end of the horizon, and N is the prediction horizon (typically N ≥ 10 for the DIP). The weighting matrices Q, Q_f and R are positive definite. The optimizer returns a control sequence U = [u_{k|k}, u_{k+1|k}, ..., u_{k+N-1|k}], and the MPC applies the first element u_k^* = u_{k|k}^* (receding horizon).

**Implementation:** See `src/controllers/mpc/mpc_controller.py`, lines 301–429.

### Lyapunov Function: Optimal Cost-to-Go

For MPC, the natural Lyapunov function is the **optimal cost‑to‑go**:

    V_k(x_k) = J_k^*(x_k) = min_{U} J_k(x_k, U).

This function measures the minimum cost achievable from state x_k over the prediction horizon. It is positive definite (V_k(0) = 0 and V_k(x) > 0 for x ≠ 0) and radially unbounded (V_k(x) → ∞ as ||x|| → ∞) due to the quadratic structure of Q, R and Q_f.

**Theorem (MPC Stability via Value Function Decrease):** If the MPC optimization is feasible at time k and the terminal cost Q_f satisfies a Lyapunov decrease condition, then the closed‑loop system is asymptotically stable at the origin.

*Proof sketch:* At time k, let U_k^* be the optimal control sequence. At time k+1, consider the **shifted candidate** Ũ_{k+1} = [u_{k+1|k}^*, u_{k+2|k}^*, ..., u_{k+N-1|k}^*, u_term], where u_term stabilises the terminal state (e.g., an LQR gain). The cost achieved by this suboptimal sequence satisfies

    J_{k+1}(x_{k+1}, Ũ_{k+1}) = Σ_{j=1}^{N} ℓ + V_f(x_{k+N+1|k}).

If the terminal cost satisfies V_f(x_{k+N+1|k}) - V_f(x_{k+N|k}^*) ≤ -ℓ(x_{k+N|k}^*, u_term) (Lyapunov decrease), then

    J_{k+1}(x_{k+1}, Ũ_{k+1}) ≤ V_k(x_k) - ℓ(x_k, u_k^*).

Since the optimal cost V_{k+1}(x_{k+1}) ≤ J_{k+1}(x_{k+1}, Ũ_{k+1}), we obtain

    V_{k+1}(x_{k+1}) - V_k(x_k) ≤ -ℓ(x_k, u_k^*) ≤ -λ_min(Q)||x_k||^2 < 0   ∀ x_k ≠ 0.

This proves **asymptotic stability** of the origin. A detailed proof with DARE (Discrete Algebraic Riccati Equation) terminal cost design appears in Mayne et al. (2000) and in `docs/theory/lyapunov_stability_proofs.md`.

### Practical Considerations

The MPC implementation includes a **fallback controller** (ClassicalSMC) invoked if the optimization fails. This ensures stability even when the linearisation becomes invalid or constraints render the problem infeasible. The hybrid approach guarantees robustness across the full operating range, from large‑angle swings (SMC) to small‑perturbation regulation (MPC).

**Key Conditions:**
- **Linearisation validity:** The linearised model must approximate the true dynamics near the upright equilibrium.
- **Positive definite weights:** Q, Q_f ≻ 0 and R > 0 ensure positive definite cost.
- **Recursive feasibility:** The horizon N must be long enough that the problem remains feasible at each time step.
- **Solver reliability:** The QP solver (cvxpy with OSQP) must converge to the optimal solution within numerical tolerance.

These conditions are validated through config file checks and runtime monitoring of solver status.

------------------------------------------------------------------------

## Cross-Controller Stability Summary

The table below compares the Lyapunov functions, stability types and key assumptions for all six implemented controllers.

| Controller | Lyapunov Function | Stability Type | Key Assumptions | Convergence |
|------------|-------------------|----------------|-----------------|-------------|
| **Classical SMC** | V = ½s² | Asymptotic (exponential with k_d > 0) | K > d̄, controllability | Finite-time to surface, exponential on surface |
| **STA** | V = \|s\| + 1/(2K₂)z² | Finite-time | K₁ > 2√(2d̄/β), K₂ > d̄/β, Lipschitz disturbance | Finite-time to {s=0, ṡ=0} |
| **Adaptive SMC** | V = ½s² + 1/(2γ)K̃² | Asymptotic | K* ≥ d̄, γ, λ > 0 | s(t) → 0, K(t) bounded |
| **Hybrid Adaptive STA** | V = ½s² + 1/(2γ₁)k̃₁² + 1/(2γ₂)k̃₂² + ½u_int² | ISS (Input-to-State Stable) | Finite reset frequency, positive gains | Bounded (ultimate boundedness) |
| **Swing-Up SMC** | V_swing = E_total - E_bottom OR V_stabilize = ½s² | Multiple Lyapunov | Energy barrier reachable, finite switching | Global stability with convergence to upright |
| **MPC** | V_k(x_k) = J_k*(x_k) (optimal cost-to-go) | Asymptotic | Linearisation validity, Q, Q_f ≻ 0, R > 0, recursive feasibility | Exponential convergence to origin |

This summary reveals a common thread: all controllers rely on positive-definite Lyapunov candidates whose derivatives are negative along closed‑loop trajectories. The classic and adaptive SMC use quadratic functions of the sliding variable; the STA employs a non‑smooth absolute‑value function to capture finite‑time behaviour; the hybrid controller combines multiple error terms in an ISS framework; the swing‑up uses energy-based and SMC Lyapunov functions depending on the mode; and MPC exploits the optimal cost as its Lyapunov measure. Together, these proofs guarantee that the implemented controllers stabilise the DIP under their respective operating assumptions.

### Validation Requirements Matrix

The following matrix lists critical validation checks for each controller. These checks ensure that the configuration parameters satisfy the theoretical stability conditions and that runtime behaviour adheres to the proofs.

| Validation Check | Classical SMC | STA | Adaptive SMC | Hybrid | Swing-Up | MPC |
|------------------|---------------|-----|--------------|--------|----------|-----|
| Positive sliding gains (k_i, λ_i > 0) | ✓ | ✓ | ✓ | ✓ | N/A | N/A |
| Switching gain dominance (K > d̄) | ✓ | ✓ (via K₁, K₂) | ✓ (via adaptation) | ✓ (adaptive) | N/A | N/A |
| Controllability (L M⁻¹ B > 0) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ (linearised) |
| Boundary layer positivity (ε > 0) | ✓ | ✓ | ✓ | ✓ | N/A | N/A |
| Gain bounds (K_min ≤ K_init ≤ K_max) | N/A | N/A | ✓ | ✓ | N/A | N/A |
| Hysteresis deadband | N/A | N/A | N/A | N/A | ✓ | N/A |
| Positive definite cost matrices (Q, R > 0) | N/A | N/A | N/A | N/A | N/A | ✓ |
| Linearisation validity near equilibrium | N/A | N/A | N/A | N/A | N/A | ✓ |
| Recursive feasibility (horizon N sufficient) | N/A | N/A | N/A | N/A | N/A | ✓ |

Use this matrix to cross-check `config.yaml` parameters against the theoretical requirements before running simulations. Runtime monitoring should verify that the controllability scalar remains above threshold, that emergency resets (for the hybrid controller) do not occur infinitely often, and that the MPC solver reports feasibility at each time step.

------------------------------------------------------------------------

## Comparative Summary and Recommendations

The six implemented controllers offer a spectrum of robustness, smoothness and complexity. **Classic SMC** provides a simple and effective baseline; it achieves finite‑time convergence but suffers from chattering and requires known disturbance bounds. **Super‑twisting SMC** adds a second‑order sliding mechanism that reduces chattering and yields continuous control; it demands tuning of two gains and a higher computational cost. **Adaptive SMC** learns the disturbance bound on‑line, eliminating the need to specify \(K\) a priori; its continuous control avoids chattering but involves more parameters and possible slower response. **Hybrid adaptive–STA** combines adaptive gain adjustment with the super‑twisting algorithm while relying on a **single sliding surface**.  This unified approach retains the robustness and smoothness of second‑order sliding mode, allows the gains to adapt to unknown disturbances, and simplifies the switching logic compared with earlier dual‑surface designs.  The trade‑off is a larger set of tunable parameters (sliding surface weights, adaptation rates, dead‑zone widths and recentering gains), making careful tuning essential. **Swing-Up SMC** extends classic SMC with energy-based control to lift the pendula from the down-down configuration to the upright position before engaging stabilisation, enabling global basin of attraction. **MPC** offers optimal trajectory tracking and explicit constraint handling by solving a quadratic program at each time step; it provides smooth control and predictive behaviour but depends on accurate linearisation and reliable solver performance.

For a given DIP application, the choice among these controllers should consider the available actuator bandwidth, desired response speed, tolerance to chattering, knowledge of disturbance bounds, and whether constraints must be enforced explicitly.  The configuration tables provide a starting point for tuning, and the reliable implementation ensures safe operation even under parameter variations and modelling uncertainties.

------------------------------------------------------------------------

## References

\[1\] A. Boubaker, “The inverted pendulum: a fundamental benchmark in control theory and robotics,” *International Journal of Automation & Control*, vol. 8, no. 2, pp. 94–115, 2014.

\[2\] I. Irfan, U. Irfan, M. W. Ahmad and A. Saleem, “Control strategies for a double inverted pendulum system,” *PLOS ONE*, vol. 18, no. 3, p. e0282522, 2023.

\[3\] H. Dong, M. Zhu and S. Cui, “Integral sliding mode control for nonlinear systems with matched and unmatched perturbations,” *IEEE Transactions on Automatic Control*, vol. 57, no. 11, pp. 2986–2991, 2012.

\[4\] S. Saha and S. Banerjee, “Methodologies of chattering attenuation in sliding mode controller,” *International Journal of Hybrid Information Technology*, vol. 9, no. 2, pp. 221–232, 2016.

\[5\] A. Parvat, P. G. Kadam and V. R. Prasanna, “Design and implementation of sliding mode controller for level control,” in *Proc. Int. Conf. Control, Instrumentation, Energy and Communication*, 2013, pp. 71–75.

\[6\] S. u. Din, A. Hussain, M. F. Iftikhar and M. A. Rahman, “Smooth super‑twisting sliding mode control for the class of underactuated systems,” *PLOS ONE*, vol. 13, no. 9, p. e0204095, 2018.

\[7\] R. Roy, “Adaptive sliding mode control without knowledge of uncertainty bounds,” *International Journal of Control*, vol. 93, no. 12, pp. 3051–3062, 2020.

\[8\] Y. Sun, Y. Wang and B. Wu, “Adaptive gain sliding mode control for uncertain nonlinear systems using barrier‑like functions,” *Nonlinear Dynamics*, vol. 99, no. 4, pp. 2775–2787, 2020.

\[9\] A. Levant and V. Orlov, “Sliding mode manifolds and their design,” in *Recent Advances in Sliding Modes: Theory and Applications*, IOP Publishing, 2017, ch. 1, pp. 1–31.

\[10\] S. Li and M. Hibi, “Positive definiteness via off‑diagonal scaling of a symmetric indefinite matrix,” *Applied Mathematics and Computation*, vol. 371, p. 124959, 2020.

[11] D. Q. Mayne, J. B. Rawlings, C. V. Rao and P. O. M. Scokaert, "Constrained model predictive control: Stability and optimality," *Automatica*, vol. 36, no. 6, pp. 789–814, 2000.
