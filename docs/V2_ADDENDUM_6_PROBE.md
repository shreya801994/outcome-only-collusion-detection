# V2 addendum 6: Belal's upward price probe applied to our agents (frozen before running)

Written on 4 November 2026 and pushed before running `experiments/v2_probe.py`. Nothing earlier is changed.

## Purpose
Belal (2026) proposes an **intervention**: the regulator mandates a one-week price increase by one firm and checks whether the rival follows. In a game of strategic complements a static best responder must follow (R ≥ 0) at every marginal cost, so R < 0 falsifies static best response without a cost benchmark. His repository's `part16_probe_causal.md` (MIT licence, commit 23867f3) reports AUC 1.00 between his Q-learning collusive regime and his menu-cost best responders, measured with an exact unprobed counterfactual.

We apply the same probe to our scripted agents, so his method is benchmarked on our markets, and ask three questions:
1. Does the probe survive **slow, noisy adjustment** when the regulator has only the before/after contrast?
2. Does it flag **honest competitors that do not best-respond to the rival's actual price** (Nash-tracking competitors)?
3. Does it detect the **cost-mimicking policy**? Proposition 3 predicts it cannot.

## Simulator change
`simulate_batch(..., mandate=None)` gains an optional displacement for firm 1's price.
- **Default behaviour is unchanged.** With the edited simulator, the addendum-3 runs regenerate to the stored scores within 1.1e-16, and all 71 tests pass.
- In a mandated period, firm 1's price is the rule's price plus Δ. The rule's expected price, the cartel trigger and every random stream are untouched. So a probed run and its unprobed twin (same seeds, mandate None) differ only through the probe.

## Design
- **Environment:** E2 (primary), with the design grid of hidden costs, T = 300, burn-in 50, and 270 runs per arm. E0 is reported as secondary.
- **Seeds:** base **20261108**, used nowhere before.
- **Probes:** 5 per run.
  - Probe periods are drawn per run without replacement from {80, …, 280}, at least 15 periods apart.
  - Sizes Δ are drawn from {0.04, 0.08, 0.12, 0.16}, i.e. 1–4 steps of 0.04, approximating Belal's 1–4 grid steps.
  - One schedule stream (spawn key "probe-schedule") is shared by all arms, so run r has the same schedule in every arm.
- **Arms:**

  | Arm | Conduct | Dynamics |
  |---|---|---|
  | CAL | competitive (fresh seeds, threshold source) | fast (design) |
  | FC | competitive | fast |
  | SC | competitive | slow (λ ~ U[0.05, 0.20], noise SD 0.02) |
  | FR | collusive_rigid | fast |
  | SR | collusive_rigid | slow |
  | FT | collusive_tracking | fast |
  | ST | collusive_tracking | slow |
  | NT | competitive_nash (targets current Nash; ignores the rival's actual price) | fast |
  | CP | collusive_cost_padding | fast |
  | CP-twin | competitive at true costs c + m, streams coupled to CP | fast |

  Each arm is run probed and unprobed.

## Statistics (rival = firm 2; it can respond one period after the probe, because targets use the rival's previous price)
- **Regulator-feasible, before/after** (Belal's Part 9 statistic adapted to our lag):

  Rₖⁿ = p₂(tₖ + 1) − mean p₂(tₖ − 5 … tₖ − 1).

  Per run, R̄ⁿ = meanₖ Rₖⁿ/Δₖ. **Score_P = −R̄ⁿ.** Not following an increase is suspicious.
- **Causal (researcher-only, Belal's Part 16 estimand):**

  Rₖᶜ = p₂ᵖʳᵒᵇᵉᵈ(tₖ + 1) − p₂ᵘⁿᵖʳᵒᵇᵉᵈ(tₖ + 1),  R̄ᶜ = meanₖ Rₖᶜ/Δₖ,  Score_Pc = −R̄ᶜ.
- **Belal's falsification rule:** the share of runs with R̄ < 0, reported for both versions.
- **Threshold:** the 95th percentile of Score_P on CAL. Flag if Score_P exceeds it.

## Decision rules (fixed now)

| ID | Rule |
|---|---|
| **P1** | AUC(Score_P), SR vs SC (E2) ≥ 0.90 |
| **P2** | FPR of SC at the frozen Score_P threshold ≤ 0.10 |
| **P3** (theory prediction) | CP vs CP-twin: identical causal responses, max \|difference\| = 0, AUC(Score_P) = AUC(Score_Pc) = 0.500 |

These mirror the Option B criteria, so the two methods face the same test.
- **If P1 or P2 fails:** the paper states that the regulator-feasible probe loses power or calibration under slow adjustment at this probe budget (5 probes).
- **If P3 fails:** Proposition 3's extension to interventions is wrong, and the paper says so.

**Report only:**
- all other contrasts, for both statistics and both environments;
- NT's flag rate (expected high: NT does not respond to the rival's price, so the probe "falsifies static best response" for an honest firm, which is Belal's own "sieve, not verdict" caveat);
- AUC with bootstrap CIs, pooled and within cost cell.

## Expectations, written down before running (not rules)
- **Causal R:** competitors have R > 0, cartels have R = 0 exactly, for any speed.
- **Before/after R:** noise of SD 0.02 and λ ≈ 0.1 make the slow competitors' response small relative to noise, so P1 and P2 may fail with only 5 probes.
- **Cost padding:** best-responds at padded costs, so it follows increases and looks competitive.

## Results
To be added below after the run.
