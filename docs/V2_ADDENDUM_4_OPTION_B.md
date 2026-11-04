# V2 addendum 4: Option B, a competitive test that estimates adjustment speed (frozen before running)

Written on 4 November 2026 and pushed before running `experiments/v2_option_b.py`. Nothing in `V2_DESIGN.md` or addenda 1–3 is changed.

## Why
Addenda 2 and 3 showed that screen D tests consistency with *immediately adjusting* static competition:
- a D threshold calibrated on fast competitors flags 100% of slow competitors;
- at matched slow dynamics, D separates a cartel from competitors at only AUC 0.854.

Option B (`docs/FINAL_AUDIT.md` §5) asks whether a test that **estimates cost and adjustment speed from auditor-visible data** fixes this.

**Kill criterion, quoted unchanged from `FINAL_AUDIT.md` §5:**
> "stop if, after estimating adjustment speed, AUC(slow cartel vs slow competitors) < 0.90 or FPR at a frozen threshold > 0.10"

## The test (`detectors/adjustment_test.py`; code committed with this file)
Auditor information is level L3: prices, quantities and market size, with μ known (as in every earlier experiment). No cost, attractiveness, agent parameter, seed or label is used.

1. **Recover the demand state each period** by the logit inversion âᵢₜ = pᵢₜ + μ ln(sᵢₜ/s₀ₜ) (Proposition 1). The competitive target is then computable for any candidate cost c:

   BRᵢₜ(c) = BR(pⱼ,ₜ₋₁; âₜ, c).
2. **Estimate cost and adjustment speed** per firm from the null model

   Δpᵢₜ = λᵢ(BRᵢₜ(cᵢ) − pᵢ,ₜ₋₁) + eᵢₜ

   using Huber regression through the origin. ĉ minimises the robust residual scale (grid −0.5 to 2.5 in steps of 0.02, then golden-section refinement), and λ̂ is the fitted slope.
3. **Primary statistic.** Under the null the residuals êᵢₜ are white noise *for any λ*, because the simulator's noise and price cuts are i.i.d.
   - Compute zᵢ = √n · ρ̂₁(êᵢ), the lag-1 autocorrelation of the residuals, after winsorising them at 3 robust SDs.
   - **Score_B = maxᵢ zᵢ.** Higher means less consistent with competitive partial adjustment.
   - A rule whose target ignores the competitive target (a cartel) leaves a persistent omitted component in êᵢₜ.
4. **Secondary statistics (report only):**
   - −t for H₀: γ + β = 0 in the Huber regression Δp = α + βpₜ₋₁ + γBRₜ(ĉ), with sandwich SE;
   - the Box–Pierce statistic over lags 1–5 of êᵢ.

**Disclosure: how the primary statistic was chosen.** The three statistics were compared on **development seeds** (base 20261199; 45 runs per arm; never used for evaluation) before this file was written. Development results, threshold = 95th percentile of fast competitors (development):

| Statistic | FPR, slow competitors | AUC, slow rigid vs slow competitors | AUC, slow tracking vs slow competitors |
|---|---|---|---|
| γ + β test | 0.07 | 0.874 | 0.424 |
| lag-1 residual autocorrelation (**chosen**) | 0.04 | 0.959 | 0.998 |
| Box–Pierce(5) | 0.04 | 0.839 | 0.980 |

Development check of the μ-estimated variant (same seeds, grid 0.150–0.350 in steps of 0.025):
- μ̂ has median 0.225 for fast competitors but sits at the **grid floor 0.15** for slow competitors and the slow rigid cartel, so μ is poorly identified under slow adjustment;
- with a threshold from fast competitors: FPR(slow competitors) 0.00, TPR(slow rigid) 0.60, AUC 0.942.

This is why the μ-estimated variant is report-only.

The development sample is small (45 per arm), so these numbers are not evidence. Only the fresh-seed results below count.

## Design
- **Environment:** E2 (share-moving shocks), with the design's shock process, T = 300, burn-in 50, and the 3 × 3 hidden-cost grid. 30 runs per cost cell gives 270 per arm.
- **Seeds:** base **20261107**, used nowhere before.
- **Threshold, frozen:** the 95th percentile of Score_B on the **main-design E2 matched calibration split**: stored fast competitors, `data_v2/calibration_E2_competitive_grid.npz`, seed base 20261102. Flag a run if its score exceeds the threshold. Secondary statistics get their thresholds the same way.
- **Fresh arms** (SLOW = λ ~ U[0.05, 0.20], noise SD 0.02, as in addenda 2–3):

  | Arm | Conduct | Dynamics |
  |---|---|---|
  | SC | competitive | SLOW |
  | SR | collusive_rigid | SLOW |
  | ST | collusive_tracking | SLOW |
  | CP | collusive_cost_padding | design defaults |
  | CP-twin | competitive at true costs c + m, with random streams coupled to CP | design defaults |

- **Stored arms**, never scored by Option B before: the main-design E2 test split (seed 20261102) for fast competitive, fast rigid and fast tracking.
- **Comparison:** D_L3 is scored on the same fresh arms with its frozen main-design threshold (0.05346).

## Decision rules (fixed now)

| ID | Rule | Part of kill criterion? |
|---|---|---|
| **B1** | AUC(Score_B), SR vs SC ≥ 0.90 (pooled over cost cells) | yes |
| **B2** | FPR of SC at the frozen Score_B threshold ≤ 0.10 | yes |

- **If B1 or B2 fails:** Option B is stopped and reported as failed. No further tuning is done on these seeds.
- **If both pass:** Option B is reported as a constructive result. Its stated scope is a test of the partial-adjustment best-response class that is robust to unknown adjustment speed. It is **not** a test of competition in general.

**Report only, no pass rule:**
- AUC/TPR for ST vs SC;
- FPR on the stored fast test competitors;
- TPR on the stored fast rigid and tracking cartels;
- the CP-twin comparison. Proposition 3 predicts identical paths, hence identical scores and AUC exactly 0.500;
- CP vs SC;
- the secondary statistics;
- accuracy of ĉ and λ̂ against the true values (used for reporting only);
- **μ-estimated variant.** μ is profiled over {0.150, 0.175, …, 0.350} with costs re-estimated at each μ; the threshold comes from the same calibration split scored the same way. Run on calibration, SC and SR only, for CPU budget.

**Uncertainty:**
- AUC: stratified run-level bootstrap (2,000 resamples), pooled and within cost cell;
- rates: Wilson intervals.

## Known limits, stated before running
- The null model is the simulator's own competitive rule. A competitor that learns, uses a different target or has serially correlated noise would violate the null, and the test would flag it. Belal's (2026, abstract) point, that such tests measure "precision of optimization rather than the objective", applies with full force outside this class.
- A cartel that mimics partial-adjustment competition at padded costs is undetectable by construction (Proposition 3).
- The test needs share-moving demand (E2) and observed market size.

## Results
To be added below after the run, without changing anything above.
