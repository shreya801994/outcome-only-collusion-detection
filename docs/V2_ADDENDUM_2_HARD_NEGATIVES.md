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

## Results (added after the run; the rules above are unchanged)

13 s of CPU. Outputs: `results_v2/addendum2_scores.csv`, `addendum2_criteria.json`, `operating_points.csv`.

| ID | Result | Pass? |
|---|---|---|
| H1a | Slow competitors flagged at the frozen E2 threshold: **270/270, FPR 1.00**, Wilson [0.986, 1.000] | **fail** |
| H1b | Slow tracking cartel vs slow competitors: AUC(D) **0.822** [0.795, 0.850] | pass |
| H2 | Cost-padding cartel, pooled AUC: D **0.378**, B3 0.412, B2 **0.346**, B1 **0.836** | **fail** (B1 and B2 outside [0.35, 0.65]) |
| H2 (B0, report only) | pooled 0.960 [0.950, 0.969]; within cost cell 1.000 | none |

### What the failures mean
1. **H1a: the 1.00 AUC of D was partly an artefact of fast competitors.** A D threshold calibrated on fast best responders flags every slow, noisy competitor. D tests consistency with *immediately adjusting* static competition at constant cost. Its false-positive rate depends on an adjustment speed the auditor does not observe. When cartel and competitors adjust equally slowly, D still separates them, but only at AUC 0.82.
2. **H2: D cannot detect a cartel that mimics higher-cost competition** (AUC 0.38, below chance). The prediction that every behavioural screen would be at chance was wrong for B1 (0.84) and, marginally, B2 (0.35).
   - An exploratory check (`experiments/v2_check_padding_identity.py`) shows the cost-padding cartel's price and quantity paths are **identical** (max difference 0.0) to those of competitive firms whose true costs are c + m, under the same random streams.
   - So B1's 0.84 does not detect conduct. It responds to the higher effective cost level: pass-through of common shocks depends on markups. **B1 and B2 are themselves confounded by hidden cost levels.**
   - The paper must not present B1's separation in H2 as detection.

### Consequence for the paper's claims
The defensible statement is: **outcome-only screens detect departures from a specific competitive model (constant cost, fast static best response, known demand), not collusion as such.** Two things follow:
- Any cartel that behaves like competition at higher costs is unidentifiable without cost information.
- D's error rates depend on how fast competitors adjust, which the auditor does not know.
