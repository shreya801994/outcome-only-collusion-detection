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
