# Discussed Reference Sources

This directory is designated for the reference papers and manuals that were explicitly discussed and verified during the configuration calibration and moment of inertia physical validation proof.

Due to publisher paywalls, copyright restrictions, and portal authentication gates (such as IEEE Xplore and ResearchGate), these PDFs are not retrieved automatically. They must be downloaded manually and placed in this folder.

Below is the manifest of these discussed sources along with their retrieval links and context in the project.

---

## 1. Physical Model Reference (Bogdanov, 2004)

*   **Citation Key:** `Bogdanov2004` (configured in [config.bib](file:///E:/University/SMC-PSO-beta/references/config.bib))
*   **Author:** Alexander Bogdanov
*   **Title:** *Optimal Control of a Double Inverted Pendulum on a Cart*
*   **Institution:** OGI School of Science and Engineering, Oregon Health and Science University, Tech Report CSE-04-006, 2004.
*   **Project Context:** Establishes the mathematical derivation of absolute-angle equations of motion and physical parameters for the double inverted pendulum on a cart.
*   **Provenance and Inertia Note:** The masses and lengths of the cart and links represent the standard benchmark configurations. The moments of inertia represent center-of-mass moment of inertia values ($I_{1,\mathrm{com}} \approx 0.00265\,\text{kg}\cdot\text{m}^2$ and $I_{2,\mathrm{com}} \approx 0.00115\,\text{kg}\cdot\text{m}^2$), which match the uniform rod approximation ($I_{\mathrm{com}} = \frac{1}{12} m L^2$).
*   **Retrieval Links:**
    *   [OGI School Technical Reports Archive](https://digitalcommons.ohsu.edu/csci_tech/)


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
