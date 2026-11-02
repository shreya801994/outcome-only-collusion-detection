# V2 addendum: confirmatory replication (frozen before running)

Written on 2026-11-02, before running `experiments/v2_confirm.py`.

## Purpose
Two findings in `docs/V2_RESULTS.md` came from the exploratory analyses, not from the pre-registered design:
- **S3:** hidden-cost spread confounds the price-level screen.
- **S6:** without demand variation that moves shares, no screen except price level separates stationary collusion.

This addendum re-tests both, plus the identification result, on **fresh seeds** (base 20261104, not used anywhere before). The rules below are fixed now and will not be changed after the run.

## Design (all other settings as in `V2_DESIGN.md`)

| Cell | Environment | Conducts | Costs | Price cuts |
|---|---|---|---|---|
| C1 | E0 | rigid cartel vs best-response competitors | mean ∈ {0.55, 1.00, 1.45}, gap ∈ {0, 0.3, 0.6} | p = 0.01 (as designed) |
| C2 | E0 | rigid cartel vs Nash-tracking competitors | design grid (mean 0.85-1.15) | none |
| C3 | E2 | tracking cartel vs Nash-tracking competitors | design grid | none |

Each cell has 30 runs per cost cell per conduct (270 per class).

## Pass/fail rules

| ID | Rule |
|---|---|
| C1 | AUC(B0) within a cost cell minus pooled AUC(B0) ≥ 0.10 |
| C1b | B0 with the naive symmetric-cost threshold (from the main design, 1.4722) gives competitive FPR ≥ 0.30 |
| C2 | B1, B2, B3 and D (with market size) all have pooled AUC in [0.35, 0.65] |
| C3 | AUC of D (with market size) ≥ 0.95 |

## How results will be reported
- **If all pass:** the cost-spread and equivalence findings are reported as **confirmed**.
- **If any fails:** that finding is reported as **not confirmed**, and the paper does not claim it.

## Results (added after the run; the rules above are unchanged)

The run took 28 s of CPU, with 270 runs per class per cell. Outputs: `results_v2/confirmatory.csv` and `confirmatory_criteria.json`.

| ID | Result | Pass? |
|---|---|---|
| C1 | within − pooled AUC(B0) = **0.221** (pooled 0.779, within 1.000) | **pass** |
| C1b | naive-threshold B0 FPR on competitive runs = 153/270 = **0.567**, Wilson [0.507, 0.624] | **pass** |
| C2 | pooled AUC: B1 0.522, B2 0.492, B3 0.500, D 0.466 (all at chance) | **pass** |
| C3 | AUC(D) = **1.000** | **pass** |

Both exploratory findings are therefore **confirmed** on fresh seeds.

Observation (not a pre-registered rule): in C3, B1 (1.000) and B2 (0.982) also separate the tracking cartel from Nash-tracking competitors under share-moving shocks. The paper should therefore not claim that D is the only screen that works under share variation. The supported claim is narrower: without share variation, nothing except price level separates, and price level is confounded by hidden costs.
