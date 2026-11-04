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

### Results (NEW, added after the run; nothing above was changed)
Outputs: `results_v2/addendum6_scores.csv`, `addendum6_metrics.csv`, `addendum6_criteria.json`, `addendum6_output.txt`. Runtime about 3 minutes.

| ID | Result | Verdict |
|---|---|---|
| **P1** | AUC(Score_P, before/after), slow rigid vs slow competitors (E2) = **0.495** [0.448, 0.541] | **fail** |
| **P2** | FPR of slow competitors at the frozen Score_P threshold = **0.207** [0.163, 0.260] | **fail** |
| **P3** | cost padding vs coupled twin: max \|response difference\| **0.0**; AUC 0.500 for both statistics | **pass** |

**Pooled AUC, E2.** "Causal" uses the exact unprobed counterfactual, which a regulator cannot run.

| Contrast | Before/after (regulator-feasible) | Causal (counterfactual) |
|---|---|---|
| slow rigid vs slow competitors | 0.495 | 0.974; but FPR 0.878 at the fast-calibrated threshold |
| slow tracking vs slow competitors | 0.485 | 0.978 |
| fast rigid vs fast competitors | 0.669 | 0.985 |
| fast tracking vs fast competitors | 0.612 | 0.987 |
| Nash-tracking *honest* competitors vs fast competitors | 0.790 | **1.000** (honest firms look exactly like cartels) |
| cost padding vs its twin | 0.500 | 0.500 |
| slow vs fast competitors (dynamics contrast) | 0.734 | 0.959 |

E0 gives the same pattern (`addendum6_metrics.csv`).

**Belal's falsification rule (causal R < 0) applied to our agents** (`addendum6_criteria.json`, share_R_negative):
- **Cartels:** causal R is exactly 0 in 95.9–98.5% of runs, and R < 0 in at most 0.4%. Our scripted cartels do not *punish* an upward deviation; they simply ignore it.
- **Competitors:** R > 0 in every run, as the theory requires.
- **Nash-tracking honest competitors:** R = 0 in 100% of runs.

### Reading
1. **The regulator-feasible probe fails under slow, noisy adjustment.** With 5 one-period probes, a slow competitor's response (about λ × pass-through × Δ) is buried in price noise. The before/after contrast is at chance for cartel vs competitor (0.495), and its frozen threshold flags 21% of honest slow firms. Belal's AUC of 1.00 relies on the exact counterfactual and on his learners' price dynamics.
2. **With the counterfactual, the probe separates well**, but its *threshold* inherits the same adjustment-speed problem as D (FPR 0.878).
3. **The sign rule R < 0 detects almost none of our cartels.** Our cartels respond with R = 0, not R < 0. The rule falsifies *punishment of increases*, a feature of his Q-learning collusive regime, not of collusion in general. A rule of R ≤ 0 would separate them, but it would also flag every honest competitor that does not best-respond to the rival's actual price (Nash trackers: R = 0 in 100% of runs). This confirms Belal's own "sieve, not verdict" reading.
4. **Proposition 3 extends to interventions.** The cost-mimicking policy responds to the mandated increase exactly as its higher-cost competitive twin does (difference 0.0). It is invisible to the probe, as to every passive screen. Any price policy satisfying condition (S) has this property, whatever intervention is applied.
