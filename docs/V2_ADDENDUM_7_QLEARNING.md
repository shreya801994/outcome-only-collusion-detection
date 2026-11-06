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

## Deviation (recorded before any screening result was seen)
The first run trained all sessions (all converged), then **crashed while scoring Option B**: converged Q-learners often sit at a rest point, so many price changes are exactly zero and the Huber regression matrix is singular. No screening output was produced or seen.

Fix in `detectors/adjustment_test.py`:
1. On a singular matrix, the solver falls back to the pseudo-inverse.
2. When the restricted-model residuals have no variation at all, the lag-1 and Box–Pierce statistics are set to 0 ("no evidence"), because the autocorrelation is undefined.

Non-degenerate inputs take exactly the original code path. Re-scoring the stored addendum-4 calibration runs reproduces their scores to within 2.2e-16. The experiment is then rerun from the same seeds; training is deterministic.

## Results (NEW, added after the run; nothing above was changed)
Runtime 589 s on 2 CPUs. Outputs: `results_v2/addendum7_sessions.csv`, `addendum7_metrics.csv`, `addendum7_criteria.json`, `addendum7_output.txt`.
- **Training:** all 450 sessions converged; the slowest arm needed 3.15 million periods.
- **Determinism:** the rerun after the deviation reproduced the first run's training exactly (same period counts in all three arms).

### Validation of the engine
| ID | Result (QC, c = 1, 50 sessions) | Verdict |
|---|---|---|
| V1 | mean Δ = **0.828** (SE 0.018); Calvano et al. ≈ 0.85; Belal's replication 0.862 | **pass** |
| V2 | convergence rate **1.00**; median convergence at 1.81 million periods (Belal 1.8 million) | **pass** |
| V3 | rival's price falls after a forced deviation in **94%** of sessions (Belal 100%) | **pass** |

The engine is a faithful reproduction of the baseline.

| Arm and cost | 0.85 | 1.00 | 1.15 |
|---|---|---|---|
| **Δ** QC (δ = 0.95) | 0.868 | 0.828 | 0.889 |
| **Δ** QM (δ = 0) | 0.219 | 0.217 | 0.219 |
| **Mean price** QC | 1.741 | 1.766 | 1.867 |
| **Mean price** QM | 1.418 | 1.540 | 1.659 |

### Screens: collusive learners (QC) vs myopic learners (QM), 150 vs 150, thresholds from QM_cal
| Screen | Pooled AUC [95% CI] | Within-cost AUC | TPR | FPR |
|---|---|---|---|---|
| B0 price level | **0.970** [0.955, 0.982] | 1.000 | 0.860 | 0.033 |
| B1 synchronisation | 0.207 | 0.202 | 0.013 | 0.113 |
| B2 lead-lag | 0.808 | 0.809 | 0.493 | 0.067 |
| B3 deviation response | 0.736 | 0.736 | 0.000 | 0.000 |
| D_L3 implied-cost stability | 0.393 | 0.394 | 0.307 | 0.100 |
| **Score_B (Option B)** | **0.658** [0.599, 0.718] | 0.657 | 0.300 | 0.133 |
| BC Belal coverage | 0.268 | 0.265 | 0.027 | 0.053 |
| V1 variance (CV) | 0.382 | 0.366 | 0.027 | 0.073 |
| V2 SD(Δp) | 0.506 | 0.516 | 0.060 | 0.107 |
| V3 KS | 0.786 | 0.792 | 0.253 | 0.093 |
| **Probe, before/after (regulator-feasible)** | **0.929** [0.895, 0.958] | 0.929 | 0.853 | 0.093 |
| Probe, causal (counterfactual) | 0.908 [0.870, 0.940] | 0.906 | 0.773 | 0.053 |

**Report-only items:**
- **Option B out of class.** At the addendum-4 frozen threshold (1.448, set on scripted fast competitors), it flags **17.3%** of myopic learners and **38.7%** of collusive learners.
- **Belal's sign rule (causal R < 0):** fires in **90.7%** of collusive learners and **48.7%** of myopic learners (QM_cal 51.3%). The before/after version gives 93.3% and 50.7%.

### Reading
1. **Belal's probe works on learning agents** (AUC 0.93; R < 0 in 91% of collusive sessions), as he reports. Collusive Q-learners do punish a forced *increase*; our scripted cartels do not (addendum 6).
   - But the sign rule also fires for about half of the myopic learners. That is far above the 8% Belal reports for his myopic regime and close to his memoryless regime (51%).
   - We do not know what produces the difference; the regime definitions may differ (REPORTED from his repository, not investigated). As a standalone rule it is a sieve, not a verdict.
2. **Option B does not transfer to learning agents** (AUC 0.658; 17% false positives at its frozen threshold). Grid-valued learned strategies are outside its partial-adjustment null class, exactly as stated before the run.
3. **Every structure-based passive screen fails** in Calvano's stationary environment, as Propositions 1–2 predict without share-moving demand: D 0.393, BC 0.268, V1 0.382, V2 0.506.
4. **Price level (B0) separates well** (0.970 pooled). The hidden-cost range (±0.15) is small relative to the learners' markup gap (about 0.2–0.35). The confirmatory C1 result shows B0's pooled power falls when cost uncertainty is wider.
5. **No single test dominates.** The adjustment-robust test (Option B) works for scripted partial adjusters and fails for learners. The intervention probe works for learners and fails for slow scripted firms when only before/after data are available (addendum 6). Each test is a test of its own null class.
