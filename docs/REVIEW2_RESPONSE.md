# Response to the second external review

*2 November 2026, branch `review/gap-closing`.*

**What was done.** No new design was simulated, and no earlier data, result, threshold or kill criterion changed (SHA-256 check before and after). New analyses are post hoc re-analyses of stored data and are labelled EXPLORATORY: `experiments/review2_reanalysis.py`, with outputs `results_v2/review2_*` and `results_v2/fig3_b0_fpr_by_cost.*`.

**New documents:**
- `docs/PROPOSITION_v2.md`: the corrected theory. The original `PROPOSITION.md` is kept unchanged.
- `docs/SIMULATION_POLICIES.md`: the pricing rules as equations.

## Point by point

### 1. Option B's kill criterion: has it been triggered? No.
The criterion as written in `FINAL_AUDIT.md` §5, unchanged: *"stop if, after estimating adjustment speed, AUC(slow cartel vs slow competitors) < 0.90 or FPR at a frozen threshold > 0.10."*
- It applies to a test that **estimates adjustment speed from auditor-visible data**.
- Addendum 3 evaluated screen D, which estimates no adjustment speed. S1/S2 (AUC 0.854, FPR 1.000) are therefore the baseline that an Option B test would have to beat, not an evaluation of Option B.
- So the criterion has not been applied, and it is not met or failed. I am not redefining it.

**Recommendation: do not pursue Option B anyway.** The reason is not the kill rule. Belal's abstract (below) reports that even an exact constant-cost identified set "measures the precision of optimization rather than the objective": it rejects myopic and memoryless learners just as decisively. An Option B test that estimates a partial-adjustment speed would be robust only to the partial-adjustment class we chose to model. Against learners outside that class, it would very likely fail in the same way. And if implemented, it must use only auditor-visible data, never the simulator's true λ.

**Status: UNRUN.**

### 2. AUC versus the operating point
Agreed, and this is now central.
- **D in addendum 3:** AUC 0.854, but FPR 1.000 at its frozen threshold.
- **B2:** AUC 0.942 but TPR 0.044.
- **B3:** a frozen threshold of 1.0, which no score can exceed, so it never flags.

Precision depends on prevalence (EXPLORATORY, `review2_precision_by_prevalence.csv`; point estimates from addendum-3 TPR/FPR):

| Screen | Prevalence 50% | 10% | 5% | 1% |
|---|---|---|---|---|
| B0 | 0.964 | 0.748 | 0.585 | 0.213 |
| B1 | 0.501 | 0.100 | 0.050 | 0.010 |
| B2* | 1.000 | 1.000 | 1.000 | 1.000 |
| D | 0.500 | 0.100 | 0.050 | 0.010 |

\* Based on TPR 0.044 with zero false positives in 270 runs; the Wilson upper bound on its FPR is 0.014.

### 3. Why is B0 strong in addendum 3?
EXPLORATORY: `fig3_b0_fpr_by_cost.png`, `review2_b0_fpr_by_cost.csv`. Naive threshold 1.4722 (calibrated at c = 1, symmetric).

- **B0's false-positive rate is governed by the hidden mean cost relative to the calibration cost:**
  - **Mean cost below the calibration cost (0.55 or 0.85):** FPR 0.00.
  - **Mean cost 1.00:** asymmetry alone raises the FPR. For fast competitors it is 0.13 at gap 0, 1.00 at gap 0.3 and 1.00 at gap 0.6. For slow competitors it is 0.07, 0.45 and 0.95.
  - **Mean cost 1.15 or more:** FPR 1.00 for every gap and both speeds.
- **The asymmetry effect.** With the mean cost held fixed, a cost gap still raises the mean Nash price, which is why B0 flags asymmetric markets.
- **Addendum 3 used the matched threshold, not the naive one.** The matched threshold (1.6625) is calibrated on competitors across the 0.85-1.15 grid, and cartel prices (median 1.80) sit above it. So B0's strength there reflects a cost range that is narrow relative to the cartel markup. Under wider cost uncertainty, B0's pooled AUC falls (0.779 in C1).

### 4. Outside share and market size: exactly what the auditor observes
- In every experiment the L3 auditor is **given Qₜ directly** (case 1 of the reviewer's three). It is not given the outside quantity, and nothing is estimated from a demand model.
- The identity Q = (q₁ + q₂)/(1 − s₀) shows that observing the outside share s₀ (case 2) carries the same information. Without an independent measurement of s₀ or Q, it cannot be computed.
- Estimating s₀ from the demand model (case 3) would require the attractiveness values; it was not used.
- `docs/AUDITOR_INFORMATION_SPEC.md` should be read with this clarification.

### 5. μ misspecification under share-moving shocks
The reviewer's algebra is correct: ĉ − c = −(μ̂ − μ)/(1 − sᵢₜ) varies with shares. EXPLORATORY results, re-scoring stored E2 runs (`review2_mu_misspecification.csv`):

| μ̂ (true 0.25) | FPR, threshold at true μ | FPR, threshold recalibrated with μ̂ | AUC |
|---|---|---|---|
| 0.15 (−40%) | 0.196 | 0.048 | 1.000 |
| 0.20 (−20%) | 0.019 | 0.044 | 1.000 |
| 0.225 (−10%) | 0.033 | 0.048 | 1.000 |
| 0.25 | 0.052 | 0.052 | 1.000 |
| 0.275 (+10%) | 0.104 | 0.048 | 1.000 |
| 0.30 (+20%) | 0.215 | 0.041 | 1.000 |
| 0.35 (+40%) | 0.559 | 0.041 | 0.999 |

- **Correction:** the claim "D tolerates ±20% error in μ" holds for its ranking only. A frozen threshold does not tolerate it: FPR 0.22 at +20%.
- **The recalibration column has a strong assumption.** It assumes the auditor can score labelled competitive markets drawn from the true data-generating process with its own μ̂, which an auditor generally cannot.
- E3 is similar (FPR 0.16 at +20%). In E0, D's AUC is about 0.6 at every μ̂.

### 6. Pricing-rule equations
Written out in full in `docs/SIMULATION_POLICIES.md`. These include:
- the rigid cartel's fixed target p̄ = pᴺ(ā) + κ(pᴹ(ā) − pᴺ(ā)) and its punishment trigger, τ = 0.05 below the noise-free expected price;
- the partial-adjustment rule, noise and exogenous price cuts shared by all conducts;
- the fact that competitors respond to the rival's previous price.

### 7. Per-cost-cell AUCs with uncertainty
EXPLORATORY: `review2_cell_auc_addendum3.csv`. The "within-cell AUC" is defined as the **unweighted mean of the nine per-cell AUCs**, each computed on 30 cartel runs vs 30 competitive runs. The cells are equal-sized, so it equals the weighted mean. Its CI resamples runs within each cell and class.

For D in addendum 3, the per-cell AUCs range from **0.843** [0.734, 0.930] (mean cost 1.15, gap 0) to **0.983** [0.953, 1.000] (mean cost 0.85, gap 0.6), with mean 0.931. B0 is 1.000 in every cell.

### 8. Paired identity, published
`review2_padding_identity.json`: 270 runs × 300 periods, maximum absolute paired difference **0.0** for prices, quantities and market size.

### 9. SSRN identifier
**Unresolved.** The reviewer reports that both 7266558 and 7267038 show the same title and author. Cite the identifier that appears in the author's own citation or on the PDF's first page once obtained. Until then, cite as "Belal (2026), SSRN working paper, August 2026".

### 10. PROPOSITION.md
All eight corrections are implemented in `PROPOSITION_v2.md`:
- existence of the best response;
- observed shares instead of known attractiveness;
- the scope of contemporaneous Nash;
- the joint-profit derivation;
- the "generic" qualifier;
- the scope of the κ-blend;
- the on-path-only limitation and the "cost-mimicking high-price policy" naming;
- the comparison group behind AUC 0.38;
- the Lau caveat.

The original file is untouched.

## Belal: comparison using the full abstract (REPORTED: abstract supplied by the team; full text still unread)
The abstract confirms the repository-based comparison and adds one central point we lacked.

| Belal (abstract) | Ours | Overlap |
|---|---|---|
| Passive toolkit "cannot recover conduct" | Same conclusion | Full |
| Collusive path rationalisable period by period under unrestricted costs | Proposition 1 | Full |
| A constant-cost restriction yields a genuine identified set, which rejects the collusive panel | Proposition 2 + screen D (a dispersion statistic, cruder than his inequality set) | Full; his method is sharper |
| That test "measures the precision of optimization rather than the objective" | Addenda 2-3 (slow competitors, dynamics contrast) | Full; we replicate with partial-adjustment agents |
| A screen with 99% held-out accuracy flags benign menu-cost competitors in 97% of markets | B0 naive FPR 0.57 and above | Full |
| **Intervention:** a mandated price displacement; sign test of whether the rival follows an increase, valid at every marginal cost because prices are strategic complements; AUC 1.00 against a menu-cost defendant | None | **His alone**. This is the key constructive idea. |
| Policy effects (tax, transparency mandate) measured well by DiD; staggered-adoption failures | None | His alone |
| Punishment dissolves under function approximation while prices stay high | None (scripted agents) | His alone |

**Verdict on novelty: unchanged and confirmed.** Our contribution is small and incremental: an operating-point decomposition of screen errors (cost level vs asymmetry, market-size vs share shocks, adjustment speed, μ misspecification), with pre-registered rules and scripted agents. We must not claim to be first to show that passive screens fail under hidden costs.

## Revised abstract (provisional; the full Belal text is still pending)
> Regulators screening for algorithmic collusion may observe prices and quantities but not marginal costs or pricing policies. Using scripted pricing agents in a repeated logit duopoly with hidden, possibly asymmetric costs and demand shocks, we evaluate price-level, synchronization, lead-lag, deviation-response and implied-cost stability screens at decision thresholds frozen in advance, across 7,420 pre-registered runs and 16,200 separately reported exploratory runs. A price-level screen calibrated on symmetric costs flags 57% of competitive markets once costs are hidden, and its false-positive rate is governed by the hidden cost level and asymmetry. An implied-cost screen separates fast-adjusting competitors from fixed-markup cartels when demand shocks move market shares. But its frozen threshold flags 100% of slowly adjusting competitors, and when adjustment speed is matched its ranking power falls to AUC 0.85 while its operating point stays unusable. A 20% error in the demand parameter raises its false-positive rate from 5% to 22%. A high-price policy that mimics competition at higher costs produces observationally identical prices and quantities. Consistent with Belal (2026), outcome screens are best read as tests of a specified competitive benchmark; we quantify how their operating performance depends on hidden costs, demand information and adjustment dynamics that the auditor does not observe.

## Remaining limitations
1. **Belal's full text is unread**, and the SSRN identifier is unresolved.
2. **Lau (1982) is cited through Matsumura & Otani (2024);** the full text is unread.
3. **Scripted agents only.** Nothing here speaks to Q-learning or LLM agents.
4. **One logit specification and parameter set.**
5. **Slide 4, 5, 9 and 10, plus `V2_RESULTS.md`, contain superseded statements** and stale run counts. They are unchanged, per your instruction not to overwrite the presentation; they should be updated before reuse.
6. **The μ-recalibration result assumes labelled competitive markets** from the true data-generating process.
7. **Option B: UNRUN.** Its kill criterion is unchanged, and I recommend not pursuing it.
