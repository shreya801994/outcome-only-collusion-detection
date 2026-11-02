# V2 simulation design (frozen before any v2 run)

Frozen on 2026-11-02, before any v2 simulation was run. Any change after the first run must be listed under "Deviations" at the end, with its reason.

## Question
Can an auditor who sees only market outcomes tell algorithmic collusion from competition when marginal costs are hidden and possibly asymmetric? And which demand variation, and which auditor information, make that possible?

## Model (unchanged from the repository)
- **Demand:** logit duopoly with an outside good. μ = 0.25, a0 = 0, base attractiveness a1 = a2 = 2, base market size Q = 1. These are the Calvano et al. (2020) baseline values.
- **Horizon:** T = 300 periods. Periods 0-49 are burn-in, so every score uses periods 50-299 (250 periods).

## Hidden costs (3 × 3 grid, firm 2 is the high-cost firm)
- Mean cost c̄ ∈ {0.85, 1.00, 1.15} and gap g ∈ {0.0, 0.3, 0.6}. Then c1 = c̄ − g/2 and c2 = c̄ + g/2.
- This separates the cost level from the asymmetry (the v1 design confounded them).
- 30 runs per cost cell gives 270 runs per environment-conduct cell and split.

## Demand environments
| Code | Shock | Process |
|---|---|---|
| E0 | none | a1 = a2 = 2, Q = 1 |
| E1 | market size only | ln Qₜ is AR(1) with ρ = 0.95 and stationary SD 0.20 |
| E2 | share-moving | aᵢ,ₜ = 2 + ζₜ + ξᵢ,ₜ. The common shock ζ is AR(1) with ρ = 0.95 and stationary SD 0.25; the product-specific shocks ξᵢ are AR(1) with ρ = 0.95 and stationary SD 0.15. |
| E3 | both | E1 + E2 |

Firms observe the current shocks before pricing. The auditor never observes the attractiveness shocks.

## Conduct

| | Competitive | Rigid cartel | Tracking cartel |
|---|---|---|---|
| **Target** | best response to the rival's last price under current demand and own cost | fixed cooperative prices, computed once at mean demand (a = 2) | recomputed every period from current demand |
| **Cooperative price** | not applicable | Nash + κ·(joint-profit − Nash) | Nash + κ·(joint-profit − Nash) |
| **Price update** | pₜ = pₜ₋₁ + λ(target − pₜ₋₁) + N(0, 0.01²) | same | same |

**Common to both cartels:**
- **Cooperative price parameter:** κ ~ U[0.5, 1] per run.
- **Trigger:** any firm pricing more than τ = 0.05 below its expected (noise-free) price starts a joint punishment.
- **Punishment:** K ~ U{3, …, 8} periods at the current-demand static Nash price, then a return to cooperation. The state is shared, so there are no echo loops.
- **Applicability:** the tracking cartel appears only in E2 and E3. In E0 and E1 its prices equal the rigid cartel's, because optimal prices do not depend on Q.

**Common to all runs:**
- **Adjustment speed:** λ ~ U[0.5, 1] per firm.
- **Price cuts:** each firm-period, with probability 0.01, the price is cut by δ ~ U[0.10, 0.25] for one period. These cuts are identical in both conduct types, so B3 has events under both.
- **Price bounds:** prices are clipped to [0.5, 4].

## Cells and runs

| Use | Environment | Conducts | Runs |
|---|---|---|---|
| Naive calibration (v1-style) | E0, symmetric c = 1 | competitive | 200 calibration + 200 test |
| Matched calibration | E0-E3 | competitive | 270 each |
| Test | E0, E1 | competitive, rigid | 270 each |
| Test | E2, E3 | competitive, rigid, tracking | 270 each |

- Seeds come from `numpy.random.SeedSequence(20261102)`, with one fixed spawn key per (split, environment, conduct). The shock, agent-noise and price-cut streams are independent, and no seed is shared between the calibration and test splits.
- The unit of analysis is a complete run.

## Scores (labels joined only after scoring)
- B0-B3: the repository's own detectors, computed on the scoring window.
- **D (implied-cost stability):**
  - For each firm and period, compute ĉᵢ,ₜ = pᵢ,ₜ − μ̂/(1 − ŝᵢ,ₜ).
  - D = max over firms of 1.4826·MAD over t of ĉᵢ,ₜ.
  - Shares are clipped to [1e-6, 1 − 1e-6].

## Auditor information ladder

| Level | Auditor sees | Scores available |
|---|---|---|
| L1 | prices only | B0-B3 |
| L2 | prices and quantities; market size unknown, assumed to be 1 (ŝ = q) | D, with μ̂ = μ |
| L3 | prices, quantities and market size (equivalently the outside share), so ŝ = q/Q | D, with μ̂ = μ |
| L3m | as L3, but with μ misspecified | D, with μ̂ = 0.20 and μ̂ = 0.30 |

## Metrics
- **AUC** (Mann-Whitney) for each positive conduct against the competitive runs, within each environment. Reported pooled over cost cells, and as the mean of the 9 within-cost-cell AUCs.
- **Confounding** = within-cell AUC − pooled AUC.
- **Uncertainty:** 2,000 stratified bootstrap resamples (percentile 95% CI).
- **FPR and TPR** at thresholds frozen as the 95th percentile of calibration scores (flag if score > threshold). Two calibrations are used: (a) naive (E0, symmetric costs) and (b) matched (same environment, hidden costs). Wilson 95% intervals, with counts per condition.

## Pass/fail criteria (fixed now)
| ID | Criterion | If it fails |
|---|---|---|
| K1 | E2, L3, μ known: pooled AUC(D) ≥ 0.80 for the tracking cartel vs. competitive | Drop the claim that share-moving variation identifies conduct |
| K2 | E0 and E1 (L3): pooled AUC(D) ≤ 0.65 for the rigid cartel | Do not claim empirical support for the equivalence result until the separating channel is identified |
| K3 | E0: within-cell AUC(B0) − pooled AUC(B0) ≥ 0.10 (rigid vs. competitive) | Drop the quantitative claim that hidden costs confound price-level screens |
| K4 | E3, tracking: AUC(D, L3) − AUC(D, L2) ≥ 0.10 | Drop the claim that market size or outside share is a necessary rung |
| K5 (sanity) | Equilibrium solver within 1e-5 of the reference CSV; naive-baseline B0 test FPR's Wilson CI contains 0.05; no hidden field in auditor arrays | Stop and fix before reporting anything |

Power: with 270 runs per class, the 95% CI half-width of an AUC near 0.8 is about ±0.05. Per-cell AUCs use 30 against 30 runs and are reported only averaged across cells.

## Deviations
Recorded after the frozen design ran. The design, seeds and K1-K5 were not changed.

1. **Exploratory sensitivity analyses S1-S6** (`experiments/v2_sensitivity.py`) were added after seeing the main results. They are not pre-registered and must be reported as exploratory. They use fresh seeds (base 20261103).
2. **New competitive conduct** `competitive_nash` (firms target the current static Nash price) was added for S5 and S6. After the addition, re-running the main design reproduced `results_v2/scores.csv` byte-for-byte.
3. **Data storage:** trajectories are stored as float32 in `data_v2/*.npz`. Scores are computed in float64 before saving. Recomputing scores from the stored arrays differs by at most 3.3e-7.
