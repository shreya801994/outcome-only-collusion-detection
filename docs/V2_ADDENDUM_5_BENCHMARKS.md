# V2 addendum 5: benchmark against published screens (frozen before running)

Written on 4 November 2026 and pushed before running `experiments/v2_benchmark_passive.py`. Nothing earlier is changed.

## Purpose
A journal referee will ask how our screens compare with **established screens from the literature** and with the **closest recent method**, Belal (2026). This addendum evaluates them on exactly the markets already used. It is a **benchmark, report only**: there are no pass/fail rules, and the definitions and thresholds are frozen here.

## Screens added (definitions in `detectors/classic_screens.py`, `detectors/cost_coverage.py`)

| ID | Screen | Source | Auditor information | Suspicious when |
|---|---|---|---|---|
| V1 | Variance screen: coefficient of variation of price, averaged over firms | Abrantes-Metz, Froeb, Geweke & Taylor (2006), *IJIO* 24(3): 467–486. VERIFIED from the FTC working-paper version (WP 275): "standard deviation of price normalized by its mean, or the coefficient of variation"; low variation marks collusion. | L1 | low CV |
| V2 | SD of price changes, averaged over firms | Lower price variance during collusion is the hypothesis of Bolotova, Connor & Miller (2008), *IJIO* 26(6): 1290–1307 (VERIFIED, conference version). Their ARCH test needs a known cartel period, so their test itself is not usable as a screen. | L1 | low SD |
| V3 | Kolmogorov–Smirnov distance between a firm's price-change distribution and the pooled competitive price changes of the calibration split; max over firms | Adapted from Blanckenburg, Geist & Kholodilin (2012), *German Economic Review* 13(3): 245–256 (VERIFIED, abstract): they find mean, skewness and kurtosis unreliable and use a KS test. **Adaptation:** a calibration reference replaces the market's own non-cartel period. | L1 + calibration data | large distance |
| BC | Belal's constant-cost identified-set coverage | `costid.py` from github.com/alibelal-lang/algorithmic_collusion (MIT licence, commit 23867f3). For each period, the interval of constant costs under which the observed price is a static best response to the rival's current price against a grid of alternatives; peak coverage = the largest share of periods one constant cost rationalises. **Port:** continuous prices compared with an alternative grid of spacing 0.04 on [0.5, 4] (close to the spacing of his 15-point Calvano grid); demand state recovered from shares (L3, μ known) instead of given; per firm because our costs can differ. Score = 1 − min over firms of peak coverage. | L3 | low coverage |

The port was checked before freezing: exact Nash prices under demand shocks give peak coverage 1.000 at the true costs, and a fixed price of 1.7 gives 0.20–0.26.

## Data (no new random draws)
- **Main design:**
  - test split E0–E3, stored in `data_v2/`;
  - thresholds = 95th percentile of each screen on the stored **matched calibration split** of the same environment;
  - V3's reference distribution is the same calibration split.
- **Addendum 2, H1 and H2; addendum 3; confirmatory C1–C3:** regenerated from their original seeds. Each regeneration is checked by recomputing D_L3 and comparing it with the stored score files; this is reported in `addendum5_checks.json`. Thresholds come from the calibration split of the contrast's environment (E2 for addenda 2–3 and C3; E0 for C1 and C2), as in those addenda.
- **Cost-padding twin:** the competitive twin at costs c + m with coupled random streams. Proposition 3 predicts identical paths, so every screen scores AUC 0.500.

## Reported for each screen × contrast
- pooled AUC with a 2,000-resample stratified bootstrap 95% CI;
- within-cost-cell AUC;
- TPR and FPR at the frozen threshold, with a Wilson CI for FPR.

D_L3 is re-scored alongside for direct comparison.

## Expectations, written down before running (not rules)
- V1 and V2 will be confounded like B0 by cost level and adjustment speed. Slow competitors have smoother prices, so V1 and V2 may flag them.
- BC uses the contemporaneous best-response restriction, like D. It should share D's weakness with slow competitors.
- No screen can beat 0.500 against the cost-padding twin.

## The intervention benchmark (Belal's probe) and the learning-agent benchmark
These need new simulations. They are pre-registered separately (addenda 6 and 7) before they are run.

## Results (NEW, added after the run; nothing above was changed)
Outputs: `results_v2/addendum5_scores.csv`, `addendum5_metrics.csv`, `addendum5_checks.json`, `addendum5_output.txt`.
- **Regeneration check:** every regenerated arm reproduces its stored D_L3 scores to within 1.1e-16.
- **Twin:** maximum price difference 0.0.

### Pooled AUC (positive vs negative). FPR at the frozen threshold in brackets where it matters.
| Contrast | V1 variance (CV) | V2 SD(Δp) | V3 KS | BC Belal coverage | D_L3 |
|---|---|---|---|---|---|
| main E0: rigid vs competitive | **0.008** | 0.037 | 0.609 | 0.554 | 0.612 |
| main E1: rigid vs competitive | 0.004 | 0.046 | 0.537 | 0.538 | 0.588 |
| main E2: rigid vs competitive | 0.408 | 0.126 | 0.946 | **1.000** | 1.000 |
| main E2: tracking vs competitive | 0.009 | 0.016 | 0.842 | 1.000 | 1.000 |
| main E3: rigid vs competitive | 0.425 | 0.157 | 0.949 | 1.000 | 1.000 |
| main E3: tracking vs competitive | 0.009 | 0.023 | 0.886 | 1.000 | 1.000 |
| slow tracking vs slow competitive (add. 2) | 0.081 | 0.161 | 0.429 | 0.930 [FPR **1.000**] | 0.822 [FPR 1.000] |
| slow rigid vs slow competitive (add. 3) | 0.621 | 0.306 | 0.407 | 0.930 [FPR **1.000**] | 0.854 [FPR 1.000] |
| cost padding vs competitive at true costs | 0.796 | 0.634 | 0.558 | 0.527 | 0.378 |
| **cost padding vs coupled twin** | **0.500** | **0.500** | **0.500** | **0.500** | **0.500** |
| C1 wide costs: rigid vs competitive | 0.050 | 0.104 | 0.601 | 0.543 | 0.619 |
| C2: rigid vs Nash-tracking, no price cuts | **0.971** | 0.504 | 0.470 | 0.382 | 0.466 |
| C3: tracking vs Nash-tracking, no price cuts | 0.028 | 0.000 | 0.664 | 1.000 | 1.000 |

### Reading
1. **The classic variance screen points the wrong way when cartels punish.**
   - It flags low price variation. Our cartels' punishment episodes, triggered by exogenous price cuts, make collusive prices *more* variable than competitive ones, so V1 and V2 have AUC far below 0.5 (0.004–0.05) in E0, E1 and C1.
   - V1 works only where there are no punishment episodes (C2: 0.971).
   - Bolotova et al. (2008) already found the variance effect has opposite signs in their two cartels (lower for lysine, higher for citric acid). Our result shows the sign depends on whether deviations and punishments occur on path.
2. **V3 (KS)** separates fast markets under share shocks (0.84–0.95) but fails against slow competitors (0.41–0.43).
3. **Belal's constant-cost coverage (BC) behaves like our D.**
   - It is perfect in E2/E3 against fast competitors.
   - It is at chance with stationary demand (E0 0.554, consistent with Proposition 1).
   - It ranks slow cartels against slow competitors somewhat better than D (0.930 vs 0.854/0.822).
   - But its frozen threshold flags **100%** of slow competitors.
   - So his identified-set test shares the adjustment-speed calibration failure. This replicates his own "precision of optimization" reading with an explicit operating point.
4. **No passive screen beats 0.500 against the cost-mimicking twin**, as Proposition 3 predicts.
5. **Comparison with Option B** (addendum 4: AUC 0.977, FPR 0.048 on slow competitors). Option B is the only screen benchmarked that keeps its false-positive rate at the nominal level when competitors' adjustment speed differs from the calibration population.
