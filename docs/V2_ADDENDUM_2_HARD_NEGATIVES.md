# V2 addendum 2: harder negatives and the identification boundary (frozen before running)

Written on 2026-11-02, before running `experiments/v2_hard_negatives.py`. It responds to an external review of the progress deck, which raised two concerns:

1. **Possibly artificial AUC of 1.00.** The competitive agents may be too responsive. Slow, noisy competitors could have moving implied costs and be flagged falsely.
2. **Detection may depend on how the cartel is programmed.** A cartel that adjusts to demand might keep implied costs stable and escape detection.

Seeds: base 20261105, used nowhere else. Each class has 270 runs (30 per cost cell, on the design grid). Auditor level L3 (shares known; μ known), unless stated. All other settings are as in `V2_DESIGN.md`.

## H1: slow, noisy competitors as hard negatives (E2, share-moving shocks)

Both arms use adjustment speed λ ~ U[0.05, 0.20] (the design used U[0.5, 1]) and price noise SD 0.02 (the design used 0.01).

| ID | Rule | Pass condition |
|---|---|---|
| H1a | FPR of the slow competitors at the frozen main-design E2 threshold for D (0.0535, from `results_v2/thresholds.csv`) | FPR ≤ 0.10 |
| H1b | Pooled AUC(D), slow tracking cartel vs slow competitors | ≥ 0.80 |

**If H1a fails:** the paper states that D's false-positive rate depends on how fast competitors adjust, and that a threshold calibrated on fast best responders does not transfer to slow ones.

## H2: the identification boundary (E2)

The positive class is a "cost-padding" cartel. Both firms best-respond as if each cost were cᵢ + m, with m ~ U[0.2, 0.5] per run; there is no punishment. It is compared against design competitors (fast best response).

Prediction from the equivalence result: no outcome screen should separate it, even under share-moving shocks.

| ID | Rule |
|---|---|
| H2 | B1, B2, B3 and D all have pooled AUC in [0.35, 0.65] |

B0 is reported both pooled and within cost cell, with no pass rule. Within a cell it should separate, because prices are higher at the same true cost. Pooled across hidden costs, it is expected to be weaker.

**If H2 passes:** the paper states that D tests consistency with constant-cost static competition, not collusion as such. A cartel that mimics higher-cost competition cannot be identified from outcomes without cost information.

## H3: operating-point reporting

This is not a test. From the existing main-design results, the following are reported for every screen × positive conduct × environment at the frozen matched thresholds:
- TPR and FPR with Wilson 95% CIs;
- precision and F1 at an assumed 50% prevalence;
- the run counts.
