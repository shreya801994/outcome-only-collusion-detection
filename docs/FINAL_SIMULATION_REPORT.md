# Final simulation report: outcome-only screening for algorithmic collusion under hidden costs

*Shreya Dubey, Justin Santosh, Tanmay Kumar; supervisor Dr. Om Prakash Vyas, IIIT Naya Raipur.*
*Written 4 November 2026. Branch `review/gap-closing` of `shreya801994/outcome-only-collusion-detection`.*

This document collects, in one place, everything the simulation study did: how the simulator works, every experiment that was run, every result, what it means, and what is still open. It replaces nothing. The earlier documents, data, thresholds, pre-registrations and results are unchanged (§10 has the reproduction check). Where this report and an older document disagree, this report and `docs/PROPOSITION_v3.md` are current. `docs/V2_RESULTS.md` and slides 4, 5, 9 and 10 of the progress deck are **stale** (§9).

**Labels.**
- **PRE-REGISTERED:** the design and pass/fail rule were committed and pushed before the run.
- **EXPLORATORY:** run or analysed after seeing earlier results.
- **VERIFIED:** I ran or read it myself.
- **REPORTED:** from a secondary source or the team, not checked by me.
- **UNRUN:** deliberately not done.

---

## 1. The question and the short answer

**Question.** A regulator sees market outcomes (prices, perhaps quantities and market size) but not marginal costs or the firms' pricing rules. Can outcome-only screens tell algorithmic collusion from competition? What demand variation and what auditor information does that require?

**Short answer (VERIFIED, scripted agents in a logit duopoly):**
1. **Hidden costs break price-level screens at a fixed threshold.** With costs hidden, a price-level screen calibrated on symmetric unit costs flags 57% of honest competitive markets. Its false-positive rate is set mainly by the hidden cost level and cost asymmetry.
2. **Behavioural screens carry little conduct signal when demand is stationary.** In E0 with no exogenous price cuts, synchronisation, lead-lag, deviation-response and implied-cost screens are all at chance (AUC 0.46–0.52, confirmed on fresh seeds). Their apparent power in the main design comes from punishment episodes triggered by exogenous price cuts.
3. **An implied-cost screen (D) needs share-moving demand shocks, and then it separates fast competitors from cartels almost perfectly** (AUC ≈ 1.00). This is classic conduct-identification logic (Bresnahan 1982), not a new idea.
4. **D mostly measures adjustment dynamics, not conduct.**
   - Its frozen threshold flags **100%** of slowly adjusting honest competitors.
   - Slow and fast honest competitors are separated perfectly (AUC 1.000).
   - With adjustment speed matched, a slow cartel is separated from slow competitors at only AUC 0.854.
   - A 20% error in the demand parameter μ raises D's false-positive rate from 5% to 22%.
5. **A cost-mimicking high-price policy is exactly undetectable.** Its prices and quantities are identical (difference 0.0) to those of honest competitors with higher costs. Every screen scores AUC 0.500 against that twin.

**Scorecard of all 15 pre-registered rules.** 10 pass and 5 fail. Every failure is reported as a failure, and no rule or threshold was changed after its run.

| Block | Pass | Fail |
|---|---|---|
| Main design | K1, K2, K4, K5 | K3 (cost confounding too small at the narrow cost range; confirmed later by C1 on a wider range) |
| Confirmatory | C1, C1b, C2, C3 | none |
| Addendum 2 | H1b | H1a (slow competitors all flagged), H2 (B1 and B2 respond to the higher cost level) |
| Addendum 3 | S1 | S2 (slow competitors all flagged), S3 (D more sensitive to dynamics than to conduct) |

**Overall reading.** Outcome screens test a *specific competitive benchmark* (constant cost, fast static best response, known μ), not collusion as such. Our contribution is a quantified operating-point decomposition of when that benchmark fails. Belal (2026) reaches the same headline conclusion with a sharper method (§8). The contribution is small and incremental, and must be presented that way.

---

## 2. How the simulation works

### 2.1 Market
Two single-product firms face **logit demand with an outside good**, in each period t:

  sᵢₜ = exp((aᵢₜ − pᵢₜ)/μ) / [exp(a₀/μ) + exp((a₁ₜ − p₁ₜ)/μ) + exp((a₂ₜ − p₂ₜ)/μ)],  qᵢₜ = Qₜ·sᵢₜ.

| Parameter | Value | Source |
|---|---|---|
| μ (horizontal differentiation) | 0.25 | Calvano et al. (2020) baseline |
| a₀ (outside good) | 0 | same |
| base attractiveness a₁ = a₂ | 2 | same |
| base market size Q | 1 | same |
| Static Nash price at c = 1 | 1.472927 | `simulator/equilibrium.py`; checked against the repository's reference CSV to 1e-5 (K5) |
| Joint-profit price at c = 1 | 1.92498 | same |

- **Stage profit** is (pᵢ − cᵢ)·Qₜ·sᵢₜ, with constant marginal cost.
- **Best responses** are computed in closed form with the Lambert W function.
- **Nash prices** come from best-response iteration.
- **Joint-profit prices** have a common markup μ/s₀ (Lemma 2, §7).
- Prices are clipped to [0.5, 4].

### 2.2 Hidden costs
Costs are drawn on a **3 × 3 grid**, fixed for a run and never shown to the auditor:
- mean cost c̄ ∈ {0.85, 1.00, 1.15};
- gap g ∈ {0, 0.3, 0.6};
- c₁ = c̄ − g/2 and c₂ = c̄ + g/2.

The grid separates cost **level** from cost **asymmetry**; the original v1 design confounded them. There are 30 runs per cell, so 270 runs per condition. The confirmatory cell C1 widens the means to {0.55, 1.00, 1.45}.

### 2.3 Demand environments
Each shock is an AR(1) process with persistence 0.95. Firms see the current shocks before pricing. The auditor never sees attractiveness.

| Code | What moves | Process | Do shares move? |
|---|---|---|---|
| E0 | nothing | a = 2, Q = 1 | only through price changes |
| E1 | market size | ln Qₜ is AR(1), stationary SD 0.20 | no: logit shares and optimal prices do not depend on Q |
| E2 | attractiveness | aᵢₜ = 2 + ζₜ + ξᵢₜ; common ζ has SD 0.25, product-specific ξᵢ has SD 0.15 | **yes** |
| E3 | both | E1 + E2 | yes |

**How much shares move (NEW, EXPLORATORY, stored data only; `results_v2/review3_share_movement.csv`, `fig4_share_movement.png`).** Values are medians over 270 runs of the within-run SD over periods 50–299, taking the maximum over the two firms:

| Env | Conduct | SD of inside share | SD of 1/(1 − s), which enters ĉ | SD of outside share |
|---|---|---|---|---|
| E0 | competitive | 0.026 | 0.158 | 0.004 |
| E0 | rigid cartel | 0.042 | 0.199 | 0.035 |
| E1 | competitive | 0.026 | 0.165 | 0.004 |
| E1 | rigid cartel | 0.043 | 0.175 | 0.035 |
| E2 | competitive | 0.077 | 0.402 | 0.057 |
| E2 | rigid cartel | 0.163 | **1.407** | 0.152 |
| E2 | tracking cartel | 0.108 | 0.704 | 0.075 |
| E3 | competitive | 0.076 | 0.418 | 0.060 |
| E3 | rigid cartel | 0.159 | **1.345** | 0.147 |
| E3 | tracking cartel | 0.111 | 0.685 | 0.074 |

- Attractiveness shocks triple share variation for competitors.
- They raise the variation of 1/(1 − s) about seven-fold for the rigid cartel. Through Proposition 2(c) (§7), this is the term that makes a fixed-price cartel's implied cost move.
- In E0 and E1, shares move only because of price cuts and punishments.
- The SD of the Proposition 2(b) ratio sⱼ/(s₀(1 − sᵢ)) is heavy-tailed (s₀ can be small): median 1.4 in E0 vs 23 in E2 for competitors. It is reported in the CSV but is not a useful summary statistic.

### 2.4 Pricing agents (scripted, no learning)
Every conduct uses the same price-update rule. Only the **target** Tᵢₜ differs:

  eᵢₜ = pᵢ,ₜ₋₁ + λᵢ(Tᵢₜ − pᵢ,ₜ₋₁)    (expected price)
  pᵢₜ = clip(eᵢₜ + εᵢₜ − Bᵢₜδᵢₜ, 0.5, 4)

| Term | Meaning | Default | "Slow" (addenda 2–3) |
|---|---|---|---|
| λᵢ | adjustment speed, per firm and run | U[0.5, 1] | U[0.05, 0.20] |
| εᵢₜ | price noise | N(0, 0.01²) | N(0, 0.02²) |
| Bᵢₜ·δᵢₜ | exogenous one-period price cut | probability 0.01, size U[0.10, 0.25] | same |

| Conduct | Target in normal phase | Punishment? |
|---|---|---|
| `competitive` | static best response to the rival's **previous** price, at current demand and own cost | no |
| `competitive_nash` (S5, S6, C2, C3) | current static Nash price | no |
| `collusive_rigid` | fixed price p̄ = pᴺ + κ(pᴹ − pᴺ), computed once at mean demand (a = 2) | yes |
| `collusive_tracking` (E2, E3 only) | the same κ-blend, recomputed each period at current demand | yes |
| `collusive_cost_padding` (H2) | competitive best response computed **as if** each cost were cᵢ + m, m ~ U[0.2, 0.5] | no |

- **Cartel parameter:** κ ~ U[0.5, 1] per run.
- **Punishment:** if either firm prices more than τ = 0.05 below its expected price, both firms move toward current Nash for K ~ U{3, …, 8} periods, then return to the cooperative target.
- Every exogenous price cut (δ ≥ 0.10 > τ) triggers a punishment. That is how deviation behaviour shows up on path.
- **No profit or reward is used in pricing.** The only profit function is used to compute cartel targets (VERIFIED, `simulator/batch_sim.py`; `docs/PROPOSITION_AUDIT.md` §4).

Full equations: `docs/SIMULATION_POLICIES.md`.

**What a run looks like** (`results_v2/fig5_example_runs.png`, NEW, descriptive). One competitive run and one rigid-cartel run, both at cost 1.0 (symmetric):
- **E0:** the cartel prices at about 1.71 against the competitor's 1.47. Its implied cost is flat at about 1.26, above the true cost of 1.0, so a stability screen cannot tell it apart. This is Proposition 1 in action: a wrong but constant cost rationalises it.
- **E2:** the competitor's implied cost stays at 1.0 while the cartel's swings between about −0.5 and 1.4 as shocks move shares. This is Proposition 2(c), and it is what screen D detects.

### 2.5 The auditor and its information
| Level | Auditor observes | Screens |
|---|---|---|
| L1 | prices | B0–B3 |
| L2 | prices and quantities; total market size **assumed known and constant** at 1 | D_L2 |
| L3 | prices, quantities and total market size (equivalent to observing the outside share) | D_L3 |
| L3m | as L3 with μ misspecified (0.20, 0.30; finer grid in re-analysis) | D_L3_mu |

- No screen receives costs, attractiveness, conduct labels, agent parameters or seeds (VERIFIED, `audit_information_boundary.py`).
- D uses **observed** shares qᵢ/Q and μ. It does not need attractiveness. D from observed shares equals D from model shares to within 1.2e-6.
- Spec: `docs/AUDITOR_INFORMATION_SPEC.md`.

### 2.6 Screens
All are computed on periods 50–299; periods 0–49 are burn-in. Higher score = more suspicious.

| Screen | Score | Source |
|---|---|---|
| B0 price level | mean over t of (p₁ₜ + p₂ₜ)/2 | repository |
| B1 synchronisation | correlation of Δp₁ₜ and Δp₂ₜ | repository |
| B2 lead-lag | max over directions of corr(Δpᵢ,ₜ₋₁, Δpⱼ,ₜ) | repository |
| B3 deviation response | share of rival price drops > 0.10 that are followed by an own price drop next period | repository |
| D implied-cost stability | ĉᵢₜ = pᵢₜ − μ/(1 − sᵢₜ); D = max over firms of 1.4826·MAD over t of ĉᵢₜ | added in v2 |

### 2.7 Experimental design and evaluation
- **Unit of analysis:** one complete run, T = 300 periods.
- **Splits:**
  - naive calibration: E0, symmetric c = 1, 200 runs;
  - matched calibration: same environment, hidden-cost grid, 270 runs;
  - test: 270 runs per conduct and environment.
- **Thresholds:** the 95th percentile of calibration scores, frozen before testing. A run is flagged if its score exceeds the threshold.
- **Seeds:** `numpy.random.SeedSequence` with a separate base per experiment:

  | Experiment | Base seed |
  |---|---|
  | main | 20261102 |
  | sensitivity | 20261103 |
  | confirmatory | 20261104 |
  | addendum 2 | 20261105 |
  | addendum 3 | 20261106 |

  Each experiment spawns fixed keys per split, environment and conduct. Shock, noise and price-cut streams are independent, and no seed is shared between calibration and test.
- **Metrics:**
  - Mann–Whitney AUC, both pooled over cost cells and within cost cell (unweighted mean of the 9 per-cell AUCs).
  - Confounding = within-cell AUC − pooled AUC.
  - Stratified run-level bootstrap with 2,000 resamples; Wilson intervals for rates.
  - TPR/FPR at frozen thresholds; precision at several prevalences.

### 2.8 Run counts (VERIFIED)
| Block | Runs | Status |
|---|---|---|
| Main design (calibration + test) | 4,180 | PRE-REGISTERED |
| Confirmatory replication | 1,620 | PRE-REGISTERED |
| Addendum 2 (hard negatives) | 1,080 | PRE-REGISTERED |
| Addendum 3 (slow rigid cartel) | 540 | PRE-REGISTERED |
| **Pre-registered total** | **7,420** | |
| Sensitivity S1–S6 | 16,200 | EXPLORATORY |
| **All simulated runs** | **23,620** | |
| Post-hoc re-analyses | 0 new runs (stored data) | EXPLORATORY |

---

## 3. Main pre-registered design (`docs/V2_DESIGN.md`)

### 3.1 Pass/fail rules (fixed before the run)
| ID | Rule | Result | Verdict |
|---|---|---|---|
| K1 | E2, L3: AUC(D) for tracking cartel ≥ 0.80 | 1.000 | **pass** |
| K2 | E0 and E1, L3: AUC(D) for rigid cartel ≤ 0.65 | 0.612 / 0.588 | **pass** |
| K3 | E0: within-cell − pooled AUC(B0) ≥ 0.10 | 0.010 | **fail** |
| K4 | E3, tracking: AUC(D, L3) − AUC(D, L2) ≥ 0.10 | 0.189 | **pass** |
| K5 | solver, naive-threshold sanity, no hidden fields | B0 FPR 0.06, Wilson [0.035, 0.102], contains 0.05 | **pass** |

The K3 failure means the main design's cost range (0.85–1.15) is too narrow relative to the cartel markup to show cost confounding in AUC. That claim was tested again with a wider range in C1 and confirmed (§5).

### 3.2 Pooled AUC, test split (`results_v2/auc.csv`; positive class vs competitive, 270 vs 270)
| Env | Positive class | B0 | B1 | B2 | B3 | D_L2 | D_L3 |
|---|---|---|---|---|---|---|---|
| E0 | rigid | 0.990 | 1.000 | 0.646 | 0.363 | 0.612 | 0.612 |
| E1 | rigid | 0.993 | 1.000 | 0.643 | 0.378 | 0.546 | 0.588 |
| E2 | rigid | 0.987 | 0.999 | 0.837 | 0.456 | 1.000 | 1.000 |
| E2 | tracking | 0.984 | 1.000 | 0.768 | 0.308 | 1.000 | 1.000 |
| E3 | rigid | 0.985 | 0.999 | 0.782 | 0.455 | 0.812 | 1.000 |
| E3 | tracking | 0.984 | 1.000 | 0.753 | 0.281 | 0.811 | 1.000 |

How to read it:
- **D needs share-moving shocks.** It is at about 0.6 in E0/E1 and about 1.0 in E2/E3.
- **D needs market size when Q varies.** In E3, L2 falls to 0.81 because the computed shares are mis-scaled.
- **B1's near-perfect AUC is not robust.** It comes from joint punishments triggered by exogenous price cuts: both prices fall and recover together. Without price cuts (S6, §4) B1 is at chance in E0 (0.498).
- **B3's AUC is below 0.5.** B3 scores competitors as *more* responsive. Its frozen threshold is 1.0, which no score exceeds, so it never flags anything.

### 3.3 Operating points at frozen thresholds (`results_v2/rates.csv`)
| | Threshold | Competitive FPR | Cartel TPR |
|---|---|---|---|
| B0, naive threshold (symmetric c = 1), E0 | 1.472 | **0.570** (154/270) | 1.000 |
| B0, matched threshold (hidden-cost grid), E0 | 1.663 | 0.041 | 0.941 |
| D_L3, matched, E2 | 0.053 | 0.052 | 1.000 (rigid and tracking) |
| D_L2, matched, E3 | 0.411 | 0.041 | 0.263 (rigid), 0.122 (tracking) |

---

## 4. Sensitivity analyses S1–S6 (EXPLORATORY, 16,200 runs, seed base 20261103; `results_v2/sensitivity.csv`, `fig2_sensitivity.png`)

All rows are positive class vs competitive, AUC(D_L3) unless stated.

| ID | Varied | Main finding |
|---|---|---|
| S1 | E2 shock scale 0 → 1× | AUC(D) for the rigid cartel is 0.596 at 0×, then 0.816 (0.1×), 0.967 (0.25×), 1.000 (0.5×) and 1.000 (1×). A quarter of the design's shock size is enough. |
| S2 | price-cut probability, E0 | D stays near chance (0.45–0.60) until probability 0.03 (0.841). B2 is 0.004 at probability 0: with no cuts, cartel price changes are pure noise and *less* lagged-correlated than competitors' best-response chasing. |
| S3 | hidden-cost spread w, E0 | Pooled AUC(B0) falls 0.991 → 0.889 → 0.792 as w goes 0.15 → 0.30 → 0.45. Within-cell AUC stays 1.000: **cost confounding of the price level**. |
| S4 | cartel strength κ | At weak κ ∈ [0.1, 0.3], pooled B0 falls to 0.70 (E0) while within-cell stays about 1.0. D in E2 stays at 0.95 or above. |
| S5 | Nash-tracking competitors | Every screen separates more easily, because these competitors do not chase the rival's lagged price. |
| S6 | Nash-tracking competitors with **no price cuts** | E0: B1 0.498, B2 0.509, B3 0.500, D 0.458, i.e. all at chance; only B0 (0.996) separates. E2: D 0.999–1.000. |

Two of these exploratory findings (S3, S6) were then re-tested on fresh seeds (§5).

---

## 5. Confirmatory replication (PRE-REGISTERED, 1,620 runs, seed base 20261104; `docs/V2_ADDENDUM_CONFIRMATORY.md`)

| ID | Cell | Rule | Result | Verdict |
|---|---|---|---|---|
| C1 | E0, wide cost grid (mean 0.55–1.45) | within − pooled AUC(B0) ≥ 0.10 | **0.221** (pooled 0.779, within 1.000) | **pass** |
| C1b | same | naive-threshold B0 competitive FPR ≥ 0.30 | **0.567** (153/270), Wilson [0.507, 0.624] | **pass** |
| C2 | E0, rigid vs Nash-tracking, no cuts | B1, B2, B3, D all in [0.35, 0.65] | 0.522, 0.492, 0.500, 0.466 | **pass** |
| C3 | E2, tracking vs Nash-tracking, no cuts | AUC(D) ≥ 0.95 | **1.000** | **pass** |

**Confirmed.**
- Hidden cost spread confounds the price-level screen.
- With stationary demand and no deviation events, no behavioural screen separates conduct.
- Share-moving demand makes D work against fast competitors.

C3 also showed B1 (1.000) and B2 (0.982) separating under share shocks. So D is **not** the only screen that works there.

---

## 6. Harder tests: hard negatives and the slow rigid cartel

### 6.1 Addendum 2 (PRE-REGISTERED, 1,080 runs, seed base 20261105)
| ID | Test | Result | Verdict |
|---|---|---|---|
| H1a | Slow, noisy competitors at the frozen E2 D threshold (0.0535): FPR ≤ 0.10 | **270/270 flagged, FPR 1.000**, Wilson [0.986, 1.000] | **fail** |
| H1b | Slow tracking cartel vs slow competitors: AUC(D) ≥ 0.80 | 0.822 [0.795, 0.850] | pass |
| H2 | Cost-padding policy vs competitors at true cost: B1, B2, B3, D all in [0.35, 0.65] | D 0.378, B3 0.412, B2 0.346, **B1 0.836** | **fail** |
| H2, B0 (report only) | | pooled 0.960, within cell 1.000 | none |

The H2 failure is explained by the **twin check** (VERIFIED, `review2_padding_identity.json`). The cost-padding policy's paths are identical (maximum difference 0.0 over 270 runs × 300 periods) to honest competitors whose true costs are c + m.
- Against that twin, every screen scores exactly 0.500.
- The 0.38 and 0.84 above compare against competitors at the *lower true* costs, so they measure a cost-level difference, not conduct.
- B1 and B2 are therefore themselves confounded by the cost level, through pass-through.

### 6.2 Addendum 3: slow rigid cartel vs slow competitors (PRE-REGISTERED, 540 runs, seed base 20261106)
Both arms use λ ~ U[0.05, 0.20] and noise SD 0.02 in E2, with thresholds frozen from the main design.

| ID | Rule | Result | Verdict |
|---|---|---|---|
| S1 | AUC(D) conduct contrast ≥ 0.80 | **0.854** [0.831, 0.876] | pass |
| S2 | slow competitors' FPR at frozen D threshold ≤ 0.10 | **1.000** (270/270) | **fail** |
| S3 | dynamics contrast < conduct contrast | slow vs fast competitors **1.000** vs 0.854 | **fail** |

| Screen | AUC pooled | AUC within cell | TPR | FPR | Precision at 50% prevalence |
|---|---|---|---|---|---|
| B0 | 0.983 | 1.000 | 0.893 | 0.033 | 0.964 |
| B1 | 0.953 | 0.950 | 1.000 | **0.996** | 0.501 |
| B2 | 0.942 | 0.938 | 0.044 | 0.000 | 1.000 (4% recall) |
| B3 | 0.798 | 0.800 | 0.000 | 0.000 | undefined |
| D (L3) | 0.854 | 0.931 | 1.000 | **1.000** | 0.500 |

- **Median D:** slow cartel 0.282, slow competitors 0.159, fast competitors 0.033; the threshold is 0.053.
- Changing only honest firms' adjustment speed moves D five-fold. **D measures adjustment dynamics at least as much as conduct.**
- B0's strength here reflects the design's narrow cost range (C1 shows the wider case).

---

## 7. Post-hoc re-analyses of stored data (EXPLORATORY, no new runs)

### 7.1 B0 false positives by hidden cost (`review2_b0_fpr_by_cost.csv`, `fig3_b0_fpr_by_cost.png`)
Naive threshold 1.4722:
- **Mean cost below 1:** FPR 0.
- **Mean cost 1.00:**
  - fast competitors: 0.13 (gap 0), 1.00 (gap 0.3), 1.00 (gap 0.6);
  - slow competitors: 0.07, 0.45, 0.95.
- **Mean cost 1.15 or more:** FPR 1.00.

Cost asymmetry raises the average Nash price even at a fixed mean cost.

### 7.2 μ misspecification, E2 (`review2_mu_misspecification.csv`)
| μ̂ (true 0.25) | FPR, threshold frozen at true μ | FPR, recalibrated with μ̂* | AUC |
|---|---|---|---|
| 0.15 | 0.196 | 0.048 | 1.000 |
| 0.20 | 0.019 | 0.044 | 1.000 |
| 0.225 | 0.033 | 0.048 | 1.000 |
| 0.25 | 0.052 | 0.052 | 1.000 |
| 0.275 | 0.104 | 0.048 | 1.000 |
| 0.30 | **0.215** | 0.041 | 1.000 |
| 0.35 | 0.559 | 0.041 | 0.999 |

\*Recalibration assumes the auditor has labelled competitive markets from the true process, which it usually does not.

The ranking is robust to errors in μ; a frozen threshold is not.

### 7.3 Precision depends on prevalence (addendum-3 operating points)
| Screen | 50% | 10% | 5% | 1% |
|---|---|---|---|---|
| B0 | 0.964 | 0.748 | 0.585 | 0.213 |
| B1 | 0.501 | 0.100 | 0.050 | 0.010 |
| D | 0.500 | 0.100 | 0.050 | 0.010 |

### 7.4 Per-cost-cell AUC of D, addendum 3 (`review2_cell_auc_addendum3.csv`)
D's per-cell AUC ranges from 0.843 [0.734, 0.930] (mean cost 1.15, gap 0) to 0.983 [0.953, 1.000] (0.85, 0.6), with mean 0.931. B0 is 1.000 in every cell.

### 7.5 Share movement (NEW, `review3_share_movement.csv`, `fig4_share_movement.png`)
See §2.3. Attractiveness shocks are what move shares, so they are what activates Proposition 2.

---

## 8. What the results mean

### 8.1 Identification versus classification
Each result must be described in the right category:

| Category | Our results | Do not call it |
|---|---|---|
| Exact observational equivalence | Proposition 1 (one stationary outcome); Proposition 3 / cost-mimicking twin, AUC 0.500 | none |
| Finite-sample discrimination | D: 0.854 (slow rigid), 0.822 (slow tracking), about 0.61 in E0 | "non-identification" |
| Threshold-calibration failure | D FPR 1.000 for slow competitors; B0 naive FPR 0.57; D FPR 0.22 at μ̂ +20% | "non-identification" |
| Distribution shift from a latent parameter | slow vs fast competitors: AUC(D) 1.000 | proof that λ cannot be estimated (untested: Option B, UNRUN) |

### 8.2 Theory summary (`docs/PROPOSITION_v3.md`; these support the benchmark and are not claimed as new theory)
- **Lemma 1.** Unique best response, solving p − c = μ/(1 − s).
- **Lemma 2.** The joint-profit maximiser is unique, with equal markups μ/s₀. It is proved by a change of variables, an inner concave problem and an outer single crossing, and checked numerically.
  - Li & Huh (2011, *MSOM* 13(4): 549–563) prove concavity of multiproduct logit profit in market shares. VERIFIED from the abstract only; the abstract does not state the equal-markup or uniqueness results, so we keep our own proof.
- **Proposition 1.** Any single interior outcome is rationalised as static Nash at ĉ = p − μ/(1 − s), with attractiveness inverted from shares. This holds pointwise only.
- **Proposition 2.**
  - Contemporaneous static Nash at constant cost gives constant ĉ.
  - Joint-profit pricing gives ĉ = c + μsⱼ/(s₀(1 − sᵢ)).
  - Fixed prices give ĉ = p̄ − μ/(1 − s).
  - Our simulated competitors are *not* contemporaneous Nash: they chase lagged rival prices and adjust partially.
- **Proposition 3.** A policy that applies the competitive rule at padded costs c + m is pathwise identical to honest competitors at c + m, provided (S) the rule uses no true-cost profit or reward and (C) randomness is coupled. It is **not** an equilibrium cartel, and it says nothing about learning agents whose rewards use true costs.

### 8.3 Novelty relative to Belal (2026)
Belal (2026) is an SSRN working paper (identifier 7266558 / 7267038 unresolved). REPORTED: we compared against the abstract supplied by the team and his public repository; the full text is unread, and we are not seeking it now.

**Overlap with Belal:**
- passive screens cannot recover conduct;
- pointwise rationalisation;
- the constant-cost restriction;
- such tests "measure precision of optimisation, not the objective";
- naive screens flag benign competitors.

**His alone:**
- an intervention-based sign test;
- policy-effect estimation;
- learning agents.

**Ours alone, small:**
- a pre-registered operating-point decomposition of screen errors by hidden cost level and asymmetry, market-size vs share shocks, adjustment speed and μ error;
- the exact cost-mimicking twin check;
- the auditor-information ladder.

We must not claim to be first to show that passive screens fail.

---

## 9. Limitations and open items
1. **Scripted agents only.** There are no Q-learning, bandit or LLM agents, so nothing here speaks to learning algorithms (and Proposition 3 explicitly does not).
2. **One model.** A logit duopoly with one parameter set and T = 300.
3. **Belal's full text is unread.** The comparison rests on the abstract and repository.
4. **Lau (1982) is unread.** It is cited only through Matsumura & Otani (2024), with a caveat. Mizuno (2003) is not cited.
5. **The μ-recalibration result** assumes labelled competitive data.
6. **Option B (estimating adjustment speed from trajectories): UNRUN.**
   - Its kill criterion is unchanged: "stop if, after estimating adjustment speed, AUC(slow cartel vs slow competitors) < 0.90 or FPR at a frozen threshold > 0.10".
   - It has not been triggered, because nothing tested it.
   - I recommend not pursuing it, because a fix tuned to partial-adjustment agents would probably not generalise to other learners.
7. **Stale documents, left unchanged as instructed.** `docs/V2_RESULTS.md` (old run counts, pre-addenda claims) and deck slides 4, 5, 9 and 10. Update them before reuse.

---

## 10. Reproduction

### 10.1 Commands (from the repository root, Python 3 with numpy, scipy, pandas, matplotlib)
```bash
python -m experiments.v2_run_all              # main design + S1–S6 sensitivity
python -m experiments.v2_make_tables          # auc.csv, rates.csv, thresholds.csv, kill_criteria.json, fig1
python -m experiments.v2_figures              # fig2
python -m experiments.v2_confirm              # confirmatory C1–C3
python -m experiments.v2_hard_negatives       # addendum 2 H1–H3
python -m experiments.v2_check_padding_identity
python -m experiments.v2_slow_rigid           # addendum 3
python -m experiments.audit_h2_auc
python -m experiments.audit_information_boundary
python -m experiments.review2_reanalysis      # §7.1–7.4, fig3
python -m experiments.audit_propositions      # theory checks
python -m experiments.review3_share_movement  # §7.5, fig4
python -m experiments.report_example_runs     # fig5
python -m pytest -q
```

### 10.2 Clean-clone reproduction check
VERIFIED on 4 November 2026. Method:
- Fresh `git clone` of `review/gap-closing` at commit `fd0a47b`, run in a scratch directory.
- Every command in §10.1 run in order, except `report_example_runs` (added after that commit).
- Outputs compared with the committed files. CSV, JSON and text files were compared by SHA-256. `.npz` files were compared array by array with NaN-aware equality, because competitive runs store κ and punishment length as NaN.

| Script | Wall time (2 CPUs) |
|---|---|
| `v2_run_all` (4,180 main + 16,200 sensitivity runs) | 277 s |
| `v2_make_tables` | 11 s |
| `v2_confirm` (1,620 runs) | 30 s |
| `v2_hard_negatives` (1,080 runs) | 13 s |
| `v2_slow_rigid` (540 runs) | 13 s |
| all re-analyses, audits and figures | 22 s |
| test suite | 71 passed, 3 s |
| **Total** | **about 6.5 minutes**, ₹0 compute |

**Result.**
- **42 of 43 non-figure output files are identical:** all 17 data files and every results CSV/JSON. This includes `scores.csv`, `sensitivity.csv`, `kill_criteria.json`, `confirmatory_criteria.json`, `addendum2_criteria.json` and `addendum3_criteria.json`.
- **The five audit and re-analysis text outputs match** the committed `*_output.txt` files exactly.
- **The one difference is `data_v2/manifest.json`, which is metadata.** It contains:
  - the runtime;
  - two new parameter fields (`pad_low`, `pad_high`);
  - new code hashes for `simulator/batch_sim.py` and `experiments/v2_run_all.py`.

  Those two files were extended in commit `3f5ea53` (addendum 2: the cost-padding conduct). That the data stay identical confirms the extension did not change any main-design output.
- **Figures:** the PNGs are identical; the PDFs differ only in embedded creation timestamps.

**So every number in this report is reproducible from the repository on a 2-CPU machine in under 7 minutes, with the seeds given in §2.7.**

---

## 11. File index
| What | Where |
|---|---|
| Frozen designs and addenda | `docs/V2_DESIGN.md`, `docs/V2_ADDENDUM_CONFIRMATORY.md`, `docs/V2_ADDENDUM_2_HARD_NEGATIVES.md`, `docs/V2_ADDENDUM_3_SLOW_RIGID.md` |
| Pricing equations | `docs/SIMULATION_POLICIES.md` |
| Auditor information | `docs/AUDITOR_INFORMATION_SPEC.md` |
| Theory | `docs/PROPOSITION_v3.md` (current); `PROPOSITION_AUDIT.md` |
| Reviews and audits | `docs/STAGE_A_REPORT.md`, `FINAL_AUDIT.md`, `GAP_CLOSING_REPORT.md`, `REVIEW2_RESPONSE.md` |
| Data | `data_v2/*.npz` (float32 trajectories) |
| Results | `results_v2/*.csv`, `*.json`, `*_output.txt`; figures `fig1`–`fig5` |
| Simulator | `simulator/equilibrium.py`, `demand_shocks.py`, `batch_sim.py` |
| Screens and metrics | `detectors/`, `evaluation/metrics.py` |
