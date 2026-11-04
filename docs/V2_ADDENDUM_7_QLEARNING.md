# V2 addendum 7: learning-agent benchmark, the Calvano et al. (2020) Q-learning duopoly (frozen before running)

Written on 4 November 2026 and pushed before running `experiments/v2_qlearning_benchmark.py`. Nothing earlier is changed.

## Purpose
Every earlier result uses scripted agents. A journal referee will ask whether the conclusions hold for **learning** algorithms, and the standard testbed is Calvano, Calzolari, Denicolò & Pastorello (2020, *AER* 110(10)). This addendum:
1. reproduces their baseline with our own engine and checks it against their published numbers;
2. runs every screen, including Option B and Belal's probe, on converged collusive learners against myopic learners.

## Engine (`simulator/qlearning.py`, written from the paper's specification; numpy, no numba)
- **Demand and grid:** logit with a = 2, a₀ = 0, μ = 0.25; m = 15 prices on [pᴺ − ξ(pᴹ − pᴺ), pᴹ + ξ(pᴹ − pᴺ)], ξ = 0.1.
- **Agents:** memory k = 1 (225 states); α = 0.15; ε-greedy with εₜ = exp(−βt), β = 4e-6.
- **Initialisation and convergence:** Q is initialised at the discounted payoff against a uniformly random rival. A session has converged when the greedy strategy has been unchanged for 100,000 periods; training is capped at 8 million periods.
- **Profit gain:** Δ = (π̄ − πᴺ)/(πᴹ − πᴺ), computed on the greedy limit path.
- **Development check** (seeds 20261199; not evidence):
  - 30 sessions with δ = 0.95 gave mean Δ = 0.861 (SD 0.106), median convergence at 1.76 million periods, all converged;
  - 10 myopic sessions (δ = 0) gave Δ = 0.230.
- **Reference values:**
  - Calvano et al. report Δ ≈ 0.85 for the symmetric duopoly (REPORTED: authors' FTC presentation slides);
  - Belal's independent replication reports Δ = 0.862, mean price 1.795 and median convergence 1.8 million (REPORTED: `part1_validation.md` in his repository).

## Design
- **Seeds:** base **20261109**, used nowhere before.
- **Hidden cost:** symmetric, c ∈ {0.85, 1.00, 1.15}. Each cost has its own Calvano grid, so the cost is hidden from the auditor exactly as in our design. 50 sessions per cost per arm.
- **Arms:**
  - **QC:** collusive learners (δ = 0.95);
  - **QM:** myopic learners (δ = 0), the competitive-side benchmark;
  - **QM_cal:** a second independent set of myopic learners, the threshold source.
- **Observation phase**, after training:
  - 300 periods of greedy play from the final training state, learning switched off;
  - exogenous price errors: each firm-period, with probability 0.01, a uniformly random grid price;
  - the error draws for session r are identical in every arm;
  - burn-in 50, market size 1, no demand shocks (Calvano's environment).
- **Screens:** B0–B3, D_L3, Score_B (Option B, μ known), BC (Belal coverage), V1–V3, and the upward probe.
  - **Probe:** firm 1 is forced 1–4 grid steps above its intended price for one period, 5 times per session, on the same random schedule rules as addendum 6.
  - **Probe statistics:** the regulator-feasible before/after response (Score_P) and the causal response against the unprobed counterfactual (Score_Pc). Both use the rival's price in the next period, normalised by the realised displacement.
- **Thresholds:** the 95th percentile on QM_cal. Contrast: QC vs QM, pooled over costs and within cost. Bootstrap CIs (2,000 resamples).

## Decision rules: validation of the engine (fixed now)

| ID | Rule (QC, c = 1, 50 sessions) |
|---|---|
| **V1** | mean Δ ∈ [0.80, 0.90] |
| **V2** | convergence rate ≥ 0.90 |
| **V3** | share of sessions in which the rival's price falls in the period after a forced one-period deviation (firm 1 to its one-shot best response) ≥ 0.80 |

If any V rule fails, the engine is not a faithful reproduction. The screening results below are then reported only as "Calvano-like learners".

## Report only (no pass rules)
- the AUC/TPR/FPR table for every screen;
- **Option B out of class:** its FPR on myopic learners at the *addendum-4 frozen threshold* (1.448, calibrated on scripted fast competitors), and its TPR on collusive learners at the same threshold;
- the share of sessions with R < 0 (Belal's falsification rule), for both probe statistics and each arm;
- Δ and mean price by arm and cost.

## Expectations, written down before running (not rules)
- **The environment is stationary**, so by Propositions 1–2, D, BC and Option B have little to work with. D was at chance for scripted agents in E0.
- **B0 should separate QC from QM** within a cost, but less well pooled across hidden costs.
- **Option B treats learners as out-of-class:** grid-valued learning is not partial adjustment. Its FPR on myopic learners may be far above 0.05.
- **The causal probe should separate** if collusive learners punish an increase (Belal reports R < 0 in 100% of his k = 1 collusive markets).

## Results
To be added below after the run.
