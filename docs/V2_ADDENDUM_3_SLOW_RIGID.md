# V2 addendum 3: slow rigid cartel vs slow competitors (frozen before running)

Written on 2026-11-02, before running `experiments/v2_slow_rigid.py`. This closes the gap listed in `docs/FINAL_AUDIT.md` §6, item 4: only the *tracking* cartel had been run with slow adjustment (addendum 2, H1b). Nothing in earlier addenda is changed.

## Design
- **Environment:** E2 (share-moving shocks), same shock process, horizon (T = 300, burn-in 50) and 3 × 3 hidden-cost grid as `V2_DESIGN.md`.
- **Dynamics, matched in both arms:** the addendum-2 `SLOW` parameters, i.e. adjustment speed λ ~ U[0.05, 0.20] per firm, price noise SD 0.02, price-cut probability 0.01. All other agent parameters are the design defaults.
- **Arms** (each 270 runs, 30 per cost cell):
  - `collusive_rigid` under `SLOW`
  - `competitive` under `SLOW`
- **Seeds:** base **20261106**, used nowhere else. Every threshold comes from the main-design calibration split (base 20261102), so calibration and evaluation seeds are independent.
- **Thresholds:** frozen at the main-design matched-E2 values in `results_v2/thresholds.csv`. B0 1.66247, B1 −0.22115, B2 0.41647, B3 1.00000, D_L2 0.05346, D_L3 0.05346. Flag if score > threshold. B3's threshold of 1.0 can never be exceeded, so B3 flags nothing by construction; it is reported anyway.
- **Auditor level:** L3 (prices, quantities, market size; μ known).

## Metrics (all reported, unit = run)
- AUC pooled over cost cells, and the mean of within-cost-cell AUCs.
- TPR and FPR at the frozen thresholds.
- Precision and F1 at an assumed 50% prevalence.
- Run-level stratified bootstrap 95% CIs for every metric: 2,000 resamples, resampling runs within class × cost cell. Wilson intervals for TPR and FPR as well.

## Diagnostic: conduct versus adjustment dynamics
Two contrasts for D (D_L3), each a pooled AUC:
- **Conduct contrast:** slow rigid cartel vs slow competitors (dynamics matched).
- **Dynamics contrast:** slow competitors vs fast competitors. Fast = the main-design E2 competitive test runs (seed base 20261102, test split). Conduct is matched (both competitive); only adjustment dynamics differ.

## Decision rules (fixed now)

| ID | Rule | Reading |
|---|---|---|
| S1 | AUC(D) conduct contrast ≥ 0.80 | A conduct signal survives matched slow dynamics for the rigid cartel |
| S2 | FPR of slow competitors at the frozen D threshold ≤ 0.10 | The frozen threshold transfers to slow competitors (addendum 2 predicts a fail) |
| S3 | dynamics contrast AUC(D) < conduct contrast AUC(D) | D is *more* sensitive to conduct than to adjustment speed. If it fails, D is at least as sensitive to dynamics as to conduct. |

No other new experiment is part of this addendum. **Option B (`docs/FINAL_AUDIT.md` §5) remains unrun, and its kill criterion is unchanged.**

## Results (NEW, added after the run; the rules above are unchanged)

The run took 11 s of CPU. Outputs: `results_v2/addendum3_scores.csv`, `addendum3_metrics.csv`, `addendum3_criteria.json`. All earlier `results_v2/` files were checked unchanged (SHA-256).

| ID | Result | Pass? |
|---|---|---|
| S1 | AUC(D), slow rigid vs slow competitors: **0.854** [0.831, 0.876] | pass |
| S2 | Slow competitors flagged at the frozen D threshold: **270/270, FPR 1.000**, Wilson [0.986, 1.000] | **fail** |
| S3 | Dynamics contrast AUC(D) **1.000** [1.000, 1.000] vs conduct contrast **0.854** | **fail** |

Full metrics (frozen E2 thresholds; run-level bootstrap 95% CIs in `addendum3_metrics.csv`):

| Screen | AUC pooled | AUC within cell | TPR | FPR | Precision (50% prev.) | F1 (50% prev.) |
|---|---|---|---|---|---|---|
| B0 | 0.983 [0.977, 0.989] | 1.000 | 0.893 [0.867, 0.922] | 0.033 [0.015, 0.052] | 0.964 | 0.927 |
| B1 | 0.953 [0.936, 0.968] | 0.950 | 1.000 | **0.996** [0.989, 1.000] | 0.501 | 0.667 |
| B2 | 0.942 [0.923, 0.959] | 0.938 | 0.044 [0.022, 0.070] | 0.000 | 1.000 | 0.085 |
| B3 | 0.798 [0.762, 0.834] | 0.800 | 0.000 (threshold 1.0 is unreachable) | 0.000 | undefined (no flags) | undefined |
| D (L2) | 0.854 [0.831, 0.877] | 0.931 | 1.000 | **1.000** | 0.500 | 0.667 |
| D (L3) | 0.854 [0.831, 0.876] | 0.931 | 1.000 | **1.000** | 0.500 | 0.667 |

Medians of D: slow rigid cartel 0.282, slow competitors 0.159, fast competitors 0.033; the frozen threshold is 0.053.

### Conduct or adjustment dynamics?
**Mostly dynamics.**
- Changing only the adjustment speed of honest competitors moves D's median about five-fold (0.033 → 0.159) and separates them almost perfectly (AUC 1.000).
- Changing conduct at matched slow dynamics separates less (AUC 0.854).
- At a threshold calibrated on fast competitors, D flags every slow competitor, so precision at 50% prevalence is 0.50, which is chance.

D carries a real but secondary conduct signal *only if* the auditor's null is calibrated on competitors with the right adjustment speed, and the auditor does not observe that speed. B1's frozen threshold fails the same way (FPR 0.996).

B0 keeps its power here only because the cartel's markup is large relative to the design's hidden-cost range. Its failure under wider cost uncertainty is documented in addendum 1 (C1).
