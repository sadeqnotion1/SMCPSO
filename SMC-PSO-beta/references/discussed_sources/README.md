# Discussed Reference Sources

This directory is designated for the reference papers and manuals that were explicitly discussed and verified during the configuration calibration and moment of inertia physical validation proof.

Due to publisher paywalls, copyright restrictions, and portal authentication gates (such as IEEE Xplore and ResearchGate), these PDFs are not retrieved automatically. They must be downloaded manually and placed in this folder.

Below is the manifest of these discussed sources along with their retrieval links and context in the project.

---

## 1. Physical Model Reference (Prasad et al., 2012)

*   **Citation Key:** `Prasad2012` (configured in [config.bib](file:///E:/University/SMC-PSO-beta/references/config.bib))
*   **Authors:** Lal Bahadur Prasad, Barjeev Tyagi, and Hari Om Gupta
*   **Title:** *Modelling and Simulation for Optimal Control of Nonlinear Inverted Pendulum Dynamical System Using PID Controller and LQR*
*   **Proceedings:** *2012 Sixth Asia Modelling Symposium*, pp. 138--143, 2012.
*   **DOI:** [10.1109/ams.2012.21](https://doi.org/10.1109/ams.2012.21)
*   **Project Context:** Establishes the nominal physical parameters for the double-inverted pendulum system (cart mass $m_0 = 1.5$ kg, link masses $m_1 = 0.2$ kg, $m_2 = 0.15$ kg, link lengths $l_1 = 0.4$ m, $l_2 = 0.3$ m, and center of mass distances $d_1 = 0.2$ m, $d_2 = 0.15$ m).
*   **Inertia Mismatch Note:** The paper uses center-of-mass moment of inertia values ($I_1 \approx 0.00265\,\text{kg}\cdot\text{m}^2$ and $I_2 \approx 0.00115\,\text{kg}\cdot\text{m}^2$). These must be scaled up in `config.yaml` to $0.0081$ and $0.0034$ to satisfy the Parallel Axis Theorem point-mass limit ($I \ge m d^2$) checked by the codebase validation engine.
*   **Retrieval Links:**
    *   [Google Scholar Citation Link](https://scholar.google.com/citations?view_op=view_citation&hl=en&user=KIQNSh4AAAAJ&citation_for_view=KIQNSh4AAAAJ:W7OEmFMy1HYC)
    *   [IEEE Xplore Portal](https://ieeexplore.ieee.org/document/6253457)

---

## 2. Super-Twisting Lyapunov Stability Reference (Moreno & Osorio, 2008)

*   **Citation Key:** `Moreno2008` (configured in [controllers.bib](file:///E:/University/SMC-PSO-beta/references/controllers.bib))
*   **Authors:** Jaime A. Moreno and Marisol Osorio
*   **Title:** *A Lyapunov approach to second-order sliding mode controllers and observers*
*   **Proceedings:** *47th IEEE Conference on Decision and Control (CDC)*, pp. 2856--2861, 2008.
*   **DOI:** [10.1109/CDC.2008.4739356](https://doi.org/10.1109/CDC.2008.4739356)
*   **Project Context:** Establishes the strict mathematical proof of finite-time convergence for the Super-Twisting Algorithm (STA) using a strong Lyapunov function. Dictates that the proportional gain $K_1$ must exceed the integral gain $K_2$ ($K_1 > K_2 > 0$) to guarantee stability under bounded disturbances, which regulates the default STA gains in `config.yaml`.
*   **Retrieval Links:**
    *   [IEEE Xplore Portal](https://ieeexplore.ieee.org/document/4739356)
    *   [ResearchGate PDF Download](https://www.researchgate.net/publication/224599540_A_Lyapunov_approach_to_second-order_sliding_mode_controllers_and_observers)

---

## 3. Sliding Surface Design Reference (Slotine & Li, 1991)

*   **Citation Key:** `Slotine1991` (configured in [config.bib](file:///E:/University/SMC-PSO-beta/references/config.bib))
*   **Authors:** Jean-Jacques E. Slotine and Weiping Li
*   **Title:** *Applied Nonlinear Control*
*   **Publisher:** Prentice Hall, 1991
*   **Project Context:** Establishes the theoretical foundation for boundary layer sliding control, defining the use of a saturation function with boundary layer thickness $\Phi$ (mapped to `sat_soft_width` in the codebase) to eliminate chattering. Regulates the requirement that the boundary layer must be sufficiently wide (i.e., $\text{sat\_soft\_width} \ge \text{dead\_zone}$) to envelop switching delays and dead-zones, preventing high-frequency chattering.
