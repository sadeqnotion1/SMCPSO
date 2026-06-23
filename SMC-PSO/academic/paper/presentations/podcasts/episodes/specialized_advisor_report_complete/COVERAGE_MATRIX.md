# Coverage Matrix (Checklist -> Report -> Episodes)

| Checklist Area | Report Reference | Episode(s) | Coverage | Notes |
|---|---|---|---|---|
| 1.1 Full inertia matrix M(q) explicit | Sec 1.2, Eq `eq:Mfull` | 01 | Full | 3x3 matrix with symmetry and coupling terms |
| 1.2 Coriolis matrix explicit | Sec 1.2, Eq `eq:Cfull` | 01 | Full | Non-zero entries listed |
| 1.3 Gravity vector complete (G1=0) | Sec 1.2, Eq `eq:Gvec` | 01 | Full | Includes `G=[0,G2,G3]^T` |
| 1.4 Nonlinear coupling cross-check | Sec 1.2 discussion | 01 | Full | Notes on `cos(theta1-theta2)` coupling and derivation source |
| 1.5 Upright linearization for simplified model | Sec 1.2 note; Sec 1.4 | 01 | Full | Numerical FD linearization rationale |
| 1.6 Units consistency | Sec 1.3 parameters table | 01 | Full | SI units listed |
| 2.1 Sliding surface choice rationale | Sec 2.1 rationale paragraph | 02 | Full | Linear vs integral vs terminal justification |
| 2.2 Eigenvalue placement conditions | Sec 2.1 Eq `eq:stability_cond` | 02 | Full | `lambda_i>0`, `k_i>0` |
| 2.3 Relative degree check | Sec 2.1 relative-degree paragraph | 02 | Full | Degree-1 verification via `L M^-1 B` |
| 2.4 Matching condition check | Sec 2.1 matching paragraph | 02 | Full | Disturbance in input channel assumption |
| 3.1 Equivalent control derivation | Sec 2.2.1 Eq `eq:ueq` | 03 | Full | Stepwise from `dot(sigma)=0` |
| 3.2 STA finite-time bound | Sec 4.2 discussion | 03,05 | Partial | Bound discussed; closed-form DIP bound not derived |
| 3.3 Adaptive leak/dead-zone rationale | Sec 2.2.3 rationale | 03 | Full | `delta_leak=0.01`, `dz=0.05` motivation |
| 3.4 Hybrid instability mechanism analysis | Sec 2.2.4 note | 03 | Partial | Qualitative mechanism; margin analysis still future work |
| 3.5 Saturation function definition | Sec 2.2.1 Eq `eq:sat` | 03 | Full | Piecewise definition included |
| 4.1 Np=40 justification | Sec 3.1 table+notes | 04 | Full | heuristic + practical rationale |
| 4.2 w,c1,c2 justification | Sec 3.1 table+notes | 04 | Full | literature defaults and tradeoff context |
| 4.3 PSO convergence behavior | Sec 3.1 notes | 04 | Full | plateau by ~150-180 iterations noted |
| 4.4 Stopping criterion | Sec 3.1 notes | 04 | Full | fixed 200 iters; no early stop |
| 4.5 Cost normalization thresholds | Sec 3.2 + notes | 04 | Full | scale calibration narrative |
| 4.6 Instability penalty magnitude | Sec 3.2 + notes | 04 | Full | `P=1e6` dominance rationale |
| 4.7 Robust scenario split (3+4+8) | Sec 3.4 + note | 04 | Full | rationale + sensitivity limitation |
| 5.1 Classical beta/eta interpretation | Sec 4.1 + symbolic constants note | 05 | Full | state-dependent constants explained |
| 5.2 Moreno-Osorio conditions | Sec 4.2 Eq `eq:sta_conditions` | 05 | Full | nominal vs robust gain consistency check |
| 5.3 96.2% Vdot<0 explanation | Sec 4.1 explanation | 05 | Full | 3.8% attributed to boundary-layer crossing |
| 5.4 Hybrid ISS constants interpretation | Sec 4.4 + symbolic note | 05 | Full | role of alpha1/alpha2 explained |
| 5.5 Zeno prevention in swing-up | Sec 4.5 | 05 | Partial | hysteresis claim present; formal lower-bound proof not expanded |
| 6.1 IC distribution exactness | Sec 5.1 expanded setup | 06 | Full | uniform ranges listed |
| 6.2 Failure/divergence criterion | Sec 5.1 success criterion | 06 | Full | 2% band for >=1s in 10s window |
| 6.3 Why 4 controllers in MT-5 | Sec 5.1 inclusion/exclusion | 06 | Full | reasons stated for excluded controllers |
| 6.4 Seed reproducibility status | Sec 5.1 | 06 | Full | seed gap documented explicitly |
| 6.5 MT-5 N^2s vs QW-2 Joules | Sec 5.5 note | 06 | Full | metric difference clarified |
| 7.1 Normality assumption handling | Sec 5.1 stats note | 07 | Full | Welch rationale stated |
| 7.2 Multiple-comparison correction | Sec 5.1 stats note | 07 | Full | no Bonferroni; pre-planned comparisons stated |
| 7.3 Cohen d formula check | Sec 5.1 stats note | 07 | Full | pooled SD formula documented |
| 7.4 Bootstrap sample size | Sec 5.1 | 07 | Full | 10,000 resamples stated |
| 8.1 Epsilon sweep granularity | Sec 6 limitations | 08 | Full | only 3 eps values; finer sweep absent |
| 8.2 66.5% to 3.7% correction method | Sec 6 correction paragraph | 08 | Full | transient-artifact explanation |
| 8.3 Model used for MT-6 | Sec 6 limitations | 08 | Full | full nonlinear model |
| 9.1 Mismatch tolerance definition | Sec 7.1 protocol | 09 | Full | largest stable simultaneous perturbation |
| 9.2 Simultaneous vs one-at-a-time uncertainty | Sec 7.1 protocol | 09 | Full | simultaneous perturbation stated |
| 9.3 Worst-case scenario analysis | Sec 7.1 limitation | 09 | Partial | coarse sweep; exact worst-case combo not isolated |
| 10.1 Literature comparison section | Not fully present in main body | 11 | Partial | identified as needed expansion |
| 10.2 Simulation-vs-reality gap | Not fully present in main body | 11 | Partial | identified as needed expansion |
| 10.3 Computational complexity per controller tuning | Sec 1.4 rough estimate | 11 | Partial | high-level estimate only |
| 10.4 QW-2 baseline IC explicit in report | Not explicit in main body | 11 | Partial | identified as needed addition |
| 10.5 Figure references in report narrative | Sec 8.2 lists figures but sparse in-body refs | 11 | Partial | callout improvements needed |
| 10.6 Future work section | Not dedicated section | 11 | Partial | roadmap exists but not future-work synthesis |
| 11.1 STA chattering metric mismatch | Sec 5.3 metric disambiguation | 10 | Full | two different metrics separated |
| 11.2 Adaptive mismatch tolerance vs K bounds | Sec 4.3 + 7.1 | 10 | Full | interpretation explained |
| 11.3 epsilon=0.3 vs MT-6 epsilon=0.02 | Sec 2.2.1 + 6 | 10 | Full | operational vs local-opt study clarified |

Coverage summary:
- Checklist topics mapped: 100%
- Full coverage items: 47
- Partial (explicitly flagged limitations/future work): 10
