# V2 simulation results (draft for verification)

Design and pass/fail criteria were frozen before running (`docs/V2_DESIGN.md`).

| Setting | Value |
|---|---|
| Unit of analysis | one 300-period run (scored on periods 50-299) |
| Runs | 4,180 in the main design (270 per class per environment, 200 per class in the symmetric-cost cell); 13,500 more in the exploratory analyses |
| Compute | CPU, about 35 s for the main design and about 2.5 min for the exploratory analyses |

Regenerate everything with:
```
python -m experiments.v2_run_all
python -m experiments.v2_make_tables
python -m pytest -q
```

## Pass/fail criteria (pre-registered)

| ID | Rule | Result | Pass? |
|---|---|---|---|
| K1 | E2 share shocks, auditor sees market size: AUC of implied-cost screen D (tracking cartel) ≥ 0.80 | 1.000 | **pass** |
| K2 | No share variation (E0, E1): AUC of D (rigid cartel) ≤ 0.65 | 0.612 and 0.588 | **pass** |
| K3 | E0: B0 AUC within a cost cell minus pooled AUC ≥ 0.10 | 0.010 | **fail** |
| K4 | E3: AUC of D with market size minus without ≥ 0.10 | 0.189 | **pass** |
| K5 | Symmetric-cost B0 false-positive rate is near 5% (Wilson CI contains 0.05) | 12/200 = 0.060, CI [0.035, 0.102] | **pass** |

**K3 failed, so the claim that hidden costs confound price-level screens must be qualified.** The design's cost spread (mean cost 0.85-1.15) was small relative to the cartel's markup (κ ≥ 0.5), so the cartels' prices sit far above competitive prices in every cost cell. The exploratory analysis S3 (below) shows the confounding appears once cost uncertainty is wider.

## Main design: AUC, collusive vs. competitive

Pooled over the hidden cost grid. The 95% bootstrap CIs are in `results_v2/auc.csv`.

| Screen (information) | E0 none | E1 market size | E2 share-moving | E3 both |
|---|---|---|---|---|
| B0 price level (prices) | 0.990 | 0.993 | 0.987 | 0.985 |
| B1 synchronisation (prices) | 1.000 | 1.000 | 0.999 | 0.999 |
| B2 lead-lag (prices) | 0.646 | 0.643 | 0.837 | 0.782 |
| B3 deviation response (prices) | 0.363 | 0.378 | 0.456 | 0.455 |
| D implied cost, no market size (+ quantities) | 0.612 | 0.546 | 1.000 | 0.812 |
| D implied cost, with market size | 0.612 | 0.588 | 1.000 | 1.000 |
| D, μ misspecified by ±20% | 0.60-0.63 | 0.58-0.60 | 1.000 | 1.000 |

Rigid cartel shown. The demand-tracking cartel (E2/E3) gives almost the same values; see `auc.csv`.

## Frozen-threshold rates

Thresholds are the 95th percentile of separate calibration runs.

**B0 calibrated on symmetric costs (the v1 protocol):** competitive runs with hidden costs are flagged at a false-positive rate of 0.57-0.60 in every environment (e.g. E0: 154/270, Wilson [0.51, 0.63]).

**Thresholds calibrated on matched environments:**

| | Competitive FPR | Collusive TPR |
|---|---|---|
| All screens | 0.03-0.07 (target 0.05) | see below |
| B0 | | 0.92-0.96 |
| B1 | | 0.99-1.00 |
| D (with market size), E0/E1 | | 0.23-0.26 |
| D (with market size), E2/E3 | | 1.00 (270/270, Wilson [0.986, 1]) |

## Exploratory analyses (not pre-registered; `results_v2/sensitivity.csv`)

- **S1, share-shock size:** D's AUC rises from about 0.60 with no share shocks, to 0.77-0.82 at 0.1× the design shock size, to ≥ 0.97 at 0.25×.
- **S2, price-cut frequency:**
  - With no price cuts at all, D's AUC is 0.455 in E0, which is chance.
  - B3 never exceeds 0.53.
  - B1's perfect score relies on the joint punishment episodes that price cuts trigger.
- **S3, hidden-cost spread:** B0's pooled AUC falls 0.991 → 0.889 → 0.792 as the spread w goes 0.15 → 0.30 → 0.45. Its AUC within a cost cell stays at 1.000. This is the hidden-cost confounding effect.
- **S4, collusion intensity:** at κ in [0.1, 0.3], B0's AUC is 0.70. D stays at 0.95 in E2.
- **S5/S6, alternative competitors:** here competitive firms target the current Nash price.
  - With no price cuts in E0, B1, B2, B3 and D are all at chance (0.50, 0.51, 0.50, 0.46). Only price level separates, and only through the bounded cost range. This is the observational-equivalence case.
  - In E2, D still separates (≥ 0.999).
  - B1-B3's power depends on which competitive dynamics are assumed: B2 rises to 0.99 and B3 to 0.88-0.92 with these competitors.

## What the results support

1. **Without share-moving demand variation, the implied-cost screen does no better than chance on stationary collusion** (K2; S6). This matches the static equivalence result and the classic identification argument (Bresnahan 1982).
2. **Share-moving variation identifies conduct when the auditor knows the shares.** K1 passes, and K4 shows that market size or the outside share is needed when market size also varies. D's AUC is near 1 under ±20% misspecified μ.
3. **A price-level screen calibrated on known symmetric costs has false-positive rates around 0.57-0.60 once costs are hidden.** Its discriminating power falls as cost uncertainty grows relative to the collusive markup (S3). The pre-registered K3 failed at the design's cost spread, so this point rests on the exploratory S3.
4. **The power of the synchronisation, lead-lag and deviation screens depends on the assumed punishment episodes and competitor dynamics** (S2, S5, S6). It should not be read as general detection ability.

## What the results do not support

- No claim about learning algorithms (Q-learning, LLM agents): all conduct is scripted.
- No claim about real markets, or beyond this logit specification.
- No claim that D is a new detector. It is a conduct-consistency check in the tradition of Bresnahan (1982), Lau (1982) and Hespanhol & Aswani (2020).
