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
