# Stage A report: repository and data verification

**Study:** Outcome-only collusion screens under hidden costs and demand shocks (Dubey, Santosh, Kumar; supervisor Dr. O. P. Vyas)
**Repository:** https://github.com/shreya801994/outcome-only-collusion-detection
**Audited commit:** `b04f66d5f1afce94ea6eb9ade31b8f8f71386853` (HEAD of `main`, 2026-10-27 16:21 +0530, "Add detailed research README"). This is the same commit as the earlier audit.
**Audit date:** 2026-11-02. Facts only: no literature and no recommendations in this stage.

**Labels.** `VERIFIED` = I ran or read it. `REPORTED` = taken from the brief or README, not checked. `HYPOTHESIS` and `ASSUMPTION` as defined in the brief.
**Evidence convention.** `aNN` refers to `audit/stage_a/aNN_*.py`, run from the repository root as `python -I audit/stage_a/aNN_*.py` in the audit environment (section 3). Each script's printed output is saved as `audit/stage_a/out/aNN_output.txt`. Code citations give the file and line numbers at the audited commit.

---

## 0. Status of the research work

| Finding | Label and evidence |
|---|---|
| No manuscript, draft section, LaTeX, BibTeX, Word, PDF or notebook exists, either in the working tree or anywhere in the history. | **VERIFIED**: `git ls-files`; `git log --all --name-only \| grep -Ei '\.(tex\|bib\|docx?\|pdf\|ipynb\|odt\|rtf\|pptx)$'` returns nothing. |
| The only prose document is `README.md` (1,846 lines). It describes its own results as "preliminary" (§12, §19.9). | **VERIFIED** (read). |
| The work is therefore at the research-development stage. Below, its claims are taken from the README and checked against code and data. | **VERIFIED** (follows from the two rows above). |
| The history has two commits. `2e3b30d` adds all code and data in one commit (76 files) and `b04f66d` adds the README. No file was ever deleted, so git history does not show how any dataset evolved. | **VERIFIED**: `git log`, `git log --diff-filter=D`. |

## 1. Access and inventory

| Path | Tracked contents | Label |
|---|---|---|
| `simulator/` | `market.py`, `simulation.py`, `agents.py`, `reactive_agents.py`, `adaptive_agents.py`, `collusion_agents.py`, `shocks.py`, `auditor_view.py`, empty `__init__.py` | VERIFIED |
| `detectors/` | `price_level.py` (B0), `synchronization.py` (B1), `directional_dependence.py` (B2), `deviation_response.py` (B3), `__init__.py` | VERIFIED |
| `experiments/` | 20 scripts: 11 generate trajectories (including `run_experiment.py`), 5 score detectors, 2 calibrate or evaluate B0, 2 plot | VERIFIED |
| `evaluation/` | `competitive_equilibrium_reference.csv` only. No script. | VERIFIED |
| `tests/` | 10 files, 52 tests | VERIFIED |
| `data/` | 21 CSVs | VERIFIED |
| `results/` | 5 CSV, 1 TXT, 2 PNG | VERIFIED |
| root | `README.md`, `requirements.txt` (5 exact pins), `.gitignore`. 77 tracked files in total. | VERIFIED |

- **The seven paths you listed all exist.** They are `results/detector_scores.csv`, `reactive_detector_scores.csv`, `dynamic_detector_scores.csv`, `b0_fpr_summary.csv`, `b0_hard_negative_results.csv`, `b0_threshold.txt` and `evaluation/competitive_equilibrium_reference.csv`. **VERIFIED.**
- **Referenced elsewhere but absent at this commit** (**VERIFIED**):
  - `evaluation/check_implied_cost.py`, which the earlier audit cites;
  - every `competitive_cost_gap_*_new.csv`. The script that writes them, `experiments/competitive_cost_asymmetry.py:126`, exists, but README §16.3 and §18.3 say the files are in the repository and they are not;
  - any equilibrium-solver script.

## 2. Re-verification of earlier findings 1 to 11

| # | Status | Evidence | Correction or addition |
|---|---|---|---|
| 1 | **VERIFIED** | `simulator/market.py:5-11` sets Q=1.0, a0=0.0, a1=a2=2.0, mu=0.25. `demand()` (L19-43) puts exp(a0/μ) in the denominator. a02: the outside share at p=(1.5, 1.7) is 0.0854. | none |
| 2 | **VERIFIED** (the result); the script is missing | a02: ĉᵢ = pᵢ − μ/(1−sᵢ) at the reference prices gives a maximum \|ĉ − c\| of **2.67e-6** across the four gaps. An independent FOC solve agrees with the reference CSV to 1.7e-6, consistent with its 6-decimal rounding, and iterated repository best responses reproduce it too. | `check_implied_cost.py` is not in any commit. a02 replaces it. |
| 3 | **VERIFIED**, one number refined | a03: the threshold **1.4763064258** is reproduced, to 9e-12, as `np.quantile(·, 0.95)` (linear interpolation) of 100 calibration run means. Calibration mean **1.4730067**, SD **0.0017807**. The threshold sits **0.00338** above the symmetric Nash mean of 1.472928. The gap-0.1 Nash mean is 1.520148, which is **0.0472** above the symmetric Nash mean and 0.0438 above the threshold. The lowest gap-0.1 run score is **22.4 calibration SDs** above the threshold. | "about 0.0035" should read 0.0034. The "mechanical" reading is confirmed (§7). |
| 4 | **VERIFIED** | a01: the static scores file has 20 rows, the reactive file 400 and the dynamic file 20, all competitive. No results file contains a collusive run. | The 20 static rows are only **4 distinct trajectories**, each copied five times. |
| 5 | **PARTIALLY** | a01 and a09 find **three** collusive series, all deterministic, single, with costs 1.0/1.0 and no `run_id` or seed. (a) `collusive_reward_punishment.csv`: 300 periods, constant 1.9. (b) `collusion_deviation_{researcher,auditor}.csv`: 80 periods, firm 1 forced to 1.40, recorded at t=31. (c) `collusive_deviation_response.csv`: 80 periods, firm 2 deviates, recorded at t=30, no generating script. The values 1.90, 1.10, 0.05 and 5 are hard-coded defaults in `collusion_agents.py:7-10` and repeated in the scripts; 1.40 is hard-coded at `collusion_deviation.py:104`. | "One trajectory" should read "three single deterministic trajectories, no replicates". |
| 6 | **VERIFIED**, strengthened | a02, at p=(1.9, 1.9): share 0.374487, ĉ = **1.500328**. Facts about p = 1.9 at cost ĉ:<br>• the FOC-Nash price is (1.900000, 1.900000);<br>• the repository's best response to 1.9 is 1.900000;<br>• a grid of own profit on (ĉ, 10] finds no higher value;<br>• ∂²π/∂p² = −1.50 at 1.9.<br>At the true cost of 1.0, the best response to 1.9 is 1.6526, earning profit 0.4026 against 0.3370 at 1.9, so (1.9, 1.9) is not a static Nash equilibrium of the true market. The joint-profit price at c = 1 is 1.92498. | The grid check shows a global best response, not just a satisfied FOC. The formal statement is left for Stage C. |
| 7 | **VERIFIED** | Reference CSV: firm 2 at gap 0.6 prices at **1.920246**, above 1.9. | none |
| 8 | **VERIFIED**; the untraced part is now traced | `shocks.py:20-32` changes only Q, i.i.d. per period and common to both firms. a02: the static and reactive best responses are unchanged for Q ∈ {0.8, 1.0, 1.2}. a05: corr(ΔQ, Δp) ≈ 0 in the static and reactive shock data. Adaptive agents follow a hard-coded rule, target = 1.472927 + s·(Q−1) with s = 0.4/0.6 (`adaptive_agents.py:42-58`). | Reactive agents do not respond to Q. Adaptive agents respond only by assumption. |
| 9 | **PARTIALLY** | `auditor_view.py:4-10` exposes period, prices and quantities, with no `market_size`, and `tests/test_auditor_view.py:55` enforces this. Whether the auditor needs Q depends on whether it knows the demand parameters:<br>• if it knows (a1, a2, a0, μ), shares follow from prices alone (max error 5e-16) and Q can itself be recovered as qᵢ/sᵢ(p) (error 1e-15; a02, a07);<br>• otherwise Q matters: assuming Q = 1 shifts ĉ by up to about 0.10 in `competitive_demand_shocks.csv` (a02). | The "needs Q" claim holds only if demand parameters are unknown. No implied-cost screen exists in the code. |
| 10 | **PARTIALLY** | **Reactive data (a04):**<br>• B3 = 0 in all 400 runs, because no one-period price drop exceeds 0.10 in any of 239,200 changes;<br>• from gap 0 to 0.6, the B1 mean moves from −0.106 to −0.057 and the B2 mean from 0.142 to 0.124.<br>**Static data:**<br>• B1 = 1.000 only at gap 0 (five copies of one run), and −0.0046/−0.0043/−0.0038 at gaps 0.1/0.3/0.6;<br>• prices are not constant: B1 comes from the convergence transient and from the same ~1e-6 jitter in both firms. | "B1 = 1.0 for static runs with constant prices" is true only for symmetric runs, and for a numerical reason. |
| 11 | **PARTIALLY** | **52 passed in 0.82 s** (§3), but with pandas 3.0.5 instead of the pinned 3.0.6. | The test count is confirmed. The exact pinned environment is not. |

## 3. Test suite and environment

| Item | Finding | Label |
|---|---|---|
| Environment | A fresh venv (Python 3.13.18) with numpy 2.5.3, scipy 1.18.1, matplotlib 3.11.2 and pytest 9.1.1, all matching the pins, and **pandas 3.0.5 against the pin of 3.0.6**. | VERIFIED |
| Why the pin was not met | This workspace's network policy blocks PyPI: direct DNS fails, and the proxy returns 403. The four matching packages were preinstalled. | VERIFIED |
| Result | `pytest -q` on a throwaway copy: **52 passed in 0.82 s**. Afterwards `git status` showed only ignored caches. | VERIFIED |
| README environment | Python 3.13.11 and "No broken requirements found" (README §13, §17). | REPORTED |
| What the tests cover | Market and demand basics, agent rules, auditor columns (costs and Q hidden), detector arithmetic and seed reproducibility. | VERIFIED (collected) |
| What the tests do not cover | No test touches an experiment script, a data file, the reference CSV, the B0 calibration/evaluation pipeline, the Wilson function, or whether shocks move prices. | VERIFIED |

## 4. Code trace

### 4.1 Market (`simulator/market.py`), VERIFIED
- **Demand:** qᵢ = Q·exp((aᵢ−pᵢ)/μ) / [exp(a0/μ) + Σⱼ exp((aⱼ−pⱼ)/μ)], computed with max-subtraction for numerical stability.
- **Shares and outside good:** sᵢ = qᵢ/Q and s₀ = 1 − s₁ − s₂.
- **Profit:** πᵢ = (pᵢ − cᵢ)·qᵢ. There is no fixed cost, no capacity limit and no discounting anywhere in the code.
- **Parameters:** no script changes a0, a1, a2 or μ. Only Q varies, through shocks.
- **Implied first-order condition:** pᵢ − cᵢ = μ/(1−sᵢ) (a02 confirms it at the reference prices).

### 4.2 Equilibrium and reference solver, VERIFIED
- **No solver exists in the repository.** The reference CSV has no generating script, and Nash enters the code as the hard-coded constant 1.472927 (initial and base prices, tests).
- **Best responses** use `scipy.optimize.minimize_scalar(method="bounded")` with the default xatol of 1e-5:
  - `CompetitiveAgent` searches [0.5, 4.0];
  - the reactive agent searches [max(0.5, cᵢ), 4.0].
- **Tolerances:** iterated repository best responses reproduce the reference CSV, and an independent FOC solve agrees to 1.7e-6 (a02). The tests accept a best response within 1e-4 of Nash and convergence within 1e-3 after 50 periods.

### 4.3 Agents, VERIFIED

| Agent (file) | Decision rule | Observes | Does not use | Used for |
|---|---|---|---|---|
| `CompetitiveAgent` (`agents.py`) | pᵢ,ₜ₊₁ = argmax over [0.5, 4] of the expected (p − cᵢ)·qᵢ(p, pⱼ,ₜ), averaged over a list of rival-cost beliefs | Own cost, rival's last price, the **exact demand model** (calls `market.profits`), Qₜ | The rival-cost beliefs are **inert**: own profit does not depend on the rival's cost. Qₜ does not move the argmax. | Static runs, demand-shock baseline |
| `ReactiveCompetitiveAgent` (`reactive_agents.py`) | target = BR(pⱼ,ₜ). If the rival cut by more than 0.05, target = 0.5·BR + 0.5·(pᵢ,ₜ + 0.5·Δpⱼ). Then pᵢ,ₜ₊₁ = pᵢ,ₜ + 0.4·(target − pᵢ,ₜ) + N(0, 0.01²), clipped to [0.5, 4]. | Own cost, rival's last two prices, exact demand model, Qₜ | Qₜ (no effect on BR). In the recorded data the "match the cut" branch **never fired**: 0 of 251,160 changes fell below −0.05 (a04). | B0 calibration, 400 hard negatives, reactive + shock runs |
| `AdaptiveCompetitiveAgent` (`adaptive_agents.py`) | pᵢ,ₜ = pᵢ,ₜ₋₁ + 0.4·(1.472927 + sᵢ·(Qₜ − 1) − pᵢ,ₜ₋₁) + N(0, 0.01²), with s = 0.4 for firm 1 and 0.6 for firm 2 | Qₜ, before it prices | **Its own cost**, rival prices and the demand model | Dynamic runs |
| `RewardPunishmentAgent` (`collusion_agents.py`) | Prices at 1.90 unless the rival's price fell by more than 0.05 since the previous period. Then 1.10 for 5 periods, counting the current one. | Rival's last two prices | Own cost, Q, demand, any profit calculation. No discount factor or incentive check. | All collusive series |

### 4.4 Timing, VERIFIED
- **Static, reactive, collusive and calibration runs** (`simulation.py:76-164` and the reactive scripts):
  - in period t, Qₜ is drawn (when shocks are on) and the outcome at (pₜ, Qₜ) is recorded;
  - pₜ₊₁ is then chosen from pₜ (and pₜ₋₁);
  - so responses come with a one-period lag, and moves are **simultaneous** in the committed `simulation.py`.
- **Adaptive runs:** Qₜ is drawn, pₜ is chosen knowing Qₜ, and the outcome is recorded. The response is contemporaneous.
- **Reactive start:**
  - pᵢ,₀ = BRᵢ(1.472927);
  - at the first update, the internal state is BRᵢ(pⱼ,₀) rather than the recorded pᵢ,₀. The two differ when the gap is above 0.
  - Noise reconstruction confirms both points (a06).
- **Scripted deviation:** decided at t = 30 and recorded at t = 31, with the flag on row 30.
- **Stale static files:** `competitive_baseline.csv` and `competitive_cost_gap_*.csv` follow **sequential** moves, with firm 2 answering firm 1's same-period price, which the committed code cannot produce. Their maximum error is ≤ 7e-13 under sequential timing against up to 2.7e-2 under simultaneous timing (a06b). They were made by an earlier version of `simulation.py`.

### 4.5 Shock generator (`shocks.py`, `DemandShockConfig`), VERIFIED
- **What changes:** only the market size Q, and it is common to both products.
- **Distribution:** each period independently, Q = 1.2 with probability p/2, 0.8 with probability p/2, and 1.0 otherwise. p = 0.10 in the shock baseline, the reactive-shock runs and the dynamic runs; p = 0.20 in the adaptive baseline.
- **Persistence:** none. In the reactive-shock data, 510 of 540 shock spells last one period, and the lag-1 autocorrelation of Q is about 0 (a05).
- **Effect on firms:**
  - static and reactive agents receive Q, but their best responses are invariant to it;
  - adaptive agents see Qₜ before pricing and respond through the hard-coded rule.
- **Effect on the auditor:** `market_size` is absent from every auditor file. It can be recovered exactly from public prices and quantities if the demand parameters are known (§5).

## 5. Auditor boundary

| Channel | Finding | Label |
|---|---|---|
| Costs, cost gap, condition, profits, Q, seeds | Absent from all five auditor CSVs. Their public columns equal the researcher files row by row. | VERIFIED (a07) |
| When labels are joined | `evaluate_b0_hard_negatives.py` and `score_reactive_detectors.py` merge labels **after** scoring. `score_dynamic_detectors.py` looks labels up inside the loop, but passes only the auditor frame to the detectors. | VERIFIED (code) |
| Detector inputs | All four detectors read only `period`, `price_1` and `price_2`. **No detector uses quantities.** | VERIFIED (a07, grep) |
| `run_id` in auditor files | Present in all of them. Run IDs come in **contiguous blocks by hidden cost gap** (1-100 = gap 0, …, 301-400 = gap 0.6), and in the reactive runs the seed is 1000 + run_id. No detector reads it. | VERIFIED (a07, a06) |
| Market size Q | Excluded, but **recoverable** as qᵢ/sᵢ(p) to 1e-15 if (a, a0, μ) are known. | VERIFIED (a07) |
| Auditor's knowledge of the demand parameters | Never specified in code or README, although the agents use the exact model. | VERIFIED (absence) |

## 6. Data audit

**What the suitability columns mean:**
- *AUC* is ROC/AUC.
- *FPR/TPR* is a run-level rate.
- *CI* means a run-level interval is meaningful.
- *Paired* means either detector vs. detector on the same runs (D), or condition vs. condition on matched seeds (C).

All rows are **VERIFIED** (a01, a06, a06b).

| Dataset | Unit and size | Agent and conditions | Run IDs and seeds | Labels | Generator and provenance check | AUC | FPR/TPR | CI | Paired |
|---|---|---|---|---|---|---|---|---|---|
| `reactive_{auditor,researcher}_trajectories.csv` | period; 120,000 rows = 400 runs × 300 | reactive; gaps 0, 0.1, 0.3, 0.6 (100 runs each); Q = 1 | 1-400; seeds 1000+r and 2000+r (400/400 match, ≤1.4e-6) | `cost_gap`, `condition` (researcher file) | `reactive_competitive_experiment.py`, consistent | ✗ no positives | FPR ✓, TPR ✗ | ✓ | D ✓; C ✗ (different seeds per gap) |
| `b0_calibration_runs.csv` | period; 30,000 = 100 × 300; prices only | reactive; gap 0; Q = 1 | 1-100; seeds 5000+r and 6000+r (100/100 match) | none (implicitly gap 0) | `calibrate_b0.py`, consistent | ✗ | calibration only | ✓ (quantiles) | ✗ |
| `reactive_shock_{auditor,researcher}_trajectories.csv` | period; 6,000 = 20 × 300 | reactive; 5 runs per gap; Q shocks, p = 0.10 | 1-20, **reused from the reactive set**. Agent seeds 1000+2r and 1000+2r+1 are the reactive firm-1 seeds of runs 2-41. Shock seeds 5000+r are the calibration firm-1 seeds. (20/20 match) | `cost_gap`; **no `condition` column** | `reactive_competitive_shock_experiment.py`, consistent | ✗ | descriptive only | very wide (0/5 gives [0, 0.43]) | ✗ |
| `dynamic_{auditor,researcher}_trajectories.csv` | period; 6,000 = 20 × 300 | adaptive; 5 runs per gap; Q shocks | 1-20; seeds 10000+r, 11000+r; shocks 12000+r (20/20 match) | `cost_gap`, `condition` | `dynamic_competitive_experiment.py`, consistent. **The cost gap does not enter prices.** | ✗ | descriptive only | wide | ✗ |
| `{auditor,researcher}_trajectories.csv` | period; 6,000 = 20 × 300 | static; 5 runs per gap; Q = 1 | 1-20; deterministic, so only **4 distinct trajectories** | `cost_gap` (stored as 0.6000000000000001), `condition` | `run_experiment.py`, consistent (simultaneous moves) | ✗ | ✗ (effective n = 1 per gap) | ✗ | ✗ |
| `competitive_baseline.csv`, `competitive_cost_gap_{0.0,0.1,0.3,0.6}.csv` | period; 300 each, one run | static; one gap each | none | cost columns | `asymmetric_cost_baseline.py`, `baseline_simulation.py`. **Stale: made with sequential moves.** The baseline and gap-0.0 files are byte-identical. | ✗ | ✗ | ✗ | ✗ |
| `competitive_demand_shocks.csv` | period; 300, one run | static; gap 0; Q shocks (seed 42) | none | cost, Q | `demand_shock_baseline.py`, consistent | ✗ | ✗ | ✗ | ✗ |
| `adaptive_competitive_demand_shocks.csv` | period; 300, one run | prices equal exactly 1.472927 + s·(Q−1) with s = 0.4/0.6; no adjustment lag, no noise | none | cost, Q | **Stale.** The committed rule (adjustment 0.4, noise 0.01) cannot produce a path with three values. Q matches seed 42 with p = 0.20. | ✗ | ✗ | ✗ | ✗ |
| `adaptive_heterogeneous_demand_shocks.csv` | period; 300, one run | same Q sequence; s = 0.5/0.5; costs 1.0/1.0 | none | cost, Q | **Orphan** (no script). **The name does not match the content**: nothing in it is heterogeneous. | ✗ | ✗ | ✗ | ✗ |
| `collusive_reward_punishment.csv` | period; 300, one run | collusive; constant 1.9; Q = 1 | none | none | `collusion_baseline.py`, consistent | ✗ | TPR n = 1 | ✗ | ✗ |
| `collusion_deviation_{researcher,auditor}.csv` | period; 80, one run | collusive; firm 1 deviates at t = 31 | none | `forced_deviation`, `condition` | `collusion_deviation.py`, consistent | ✗ | n = 1 | ✗ | ✗ |
| `collusive_deviation_response.csv` | period; 80, one run | collusive; **firm 2** deviates at t = 30 | none | `forced_deviation` | **Orphan.** It is not a mirror of the file above: the timing convention differs. | ✗ | n = 1 | ✗ | ✗ |
| `results/b0_hard_negative_results.csv` | run; 400 | reactive | 1-400 | `cost_gap`, `flagged` | reproduced exactly (a03) | ✗ | FPR ✓ | ✓ | ✗ (B0 only) |
| `results/b0_fpr_summary.csv` | aggregate; 4 rows | none | none | none | reproduced; Wilson bounds differ by ≤1.4e-6 because the code uses z = 1.96 | none | none | none | none |
| `results/detector_scores.csv` | run; 20 (4 distinct); B0, B1 | static | 1-20 | `cost_gap`, `condition` | reproduced (≤3e-15) | ✗ | ✗ | ✗ | ✗ |
| `results/reactive_detector_scores.csv` | run; 400; B0-B3 | reactive | 1-400 | `cost_gap`, `condition` | Reproduced. The schema matches `score_reactive_detectors.py`. **`score_reactive_conditions.py` writes the same path with a different schema** (420 rows, no `cost_gap`). | ✗ | B1-B3 have **no thresholds** anywhere | ✓ | D ✓ |
| `results/dynamic_detector_scores.csv` | run; 20; B0-B2 | adaptive | 1-20 | `cost_gap`, `condition` | reproduced | ✗ | descriptive | wide | ✗ |
| `evaluation/competitive_equilibrium_reference.csv` | aggregate; 4 rows | none | none | none | **Orphan.** Values are reproduced by an independent solve (≤1.7e-6). | n/a | n/a | n/a | n/a |

**Seed overlap and shared trajectories** (all VERIFIED):
- **Calibration vs. evaluation:**
  - their seeds do not overlap (5001-5100/6001-6100 against 1001-1400/2001-2400, confirmed by matching the implied noise to seeded draws, a06);
  - no full trajectory is shared (a03);
  - calibration and gap-0 evaluation come from the same data-generating process, with means 1.4730067 and 1.4730536.
- **Static data:** 20 "runs" are 4 trajectories.
- **Unit of analysis:** every repository FPR is computed per run, which is the correct unit (`evaluate_b0_hard_negatives.py:132-199`).

## 7. B0 false-positive rates recomputed from raw trajectories (a03)

The threshold, 1.4763064258, was recomputed from `b0_calibration_runs.csv`. Scores were computed from `reactive_auditor_trajectories.csv`, and labels were joined after scoring. Intervals are 95% at the run level.

| Cost gap | Runs | Flagged | FPR | Wilson 95% | Clopper-Pearson 95% | Mean B0 (SD) | Nash mean price | Nash mean − threshold |
|---|---|---|---|---|---|---|---|---|
| 0.0 | 100 | 2 | 0.02 | [0.0055, 0.0700] | [0.0024, 0.0704] | 1.47305 (0.00177) | 1.47293 | −0.0034 |
| 0.1 | 100 | 100 | 1.00 | [0.9630, 1.0000] | [0.9638, 1.0000] | 1.52033 (0.00168) | 1.52015 | +0.0438 |
| 0.3 | 100 | 100 | 1.00 | [0.9630, 1.0000] | [0.9638, 1.0000] | 1.62263 (0.00150) | 1.62308 | +0.1468 |
| 0.6 | 100 | 100 | 1.00 | [0.9630, 1.0000] | [0.9638, 1.0000] | 1.78950 (0.00140) | 1.79012 | +0.3138 |

- **VERIFIED:** the recomputation matches `b0_hard_negative_results.csv` exactly (0 flag mismatches) and `b0_fpr_summary.csv`. At gap 0, 2/100 is consistent with the nominal 5%.
- **VERIFIED: the 100% rates are mechanical.**
  - Every gap-0.1 run is at least 22.4 calibration SDs above the threshold, so no 95th-percentile-type threshold rule would change the result.
  - Every script fixes c₁ = 1.0 and sets c₂ = 1.0 + gap, so mean cost rises with the gap. No condition varies asymmetry while holding mean cost fixed, which means the flags cannot be attributed to asymmetry as such.
- **VERIFIED: the committed figure `results/b0_fpr_vs_cost_gap.png` is stale.**
  - It shows 0% at gap 0 with an interval up to about 43%, and 100% elsewhere with lower bounds of about 57%.
  - Those are Wilson intervals for **n = 5**: 0/5 gives [0, 0.435] and 5/5 gives [0.566, 1] (a08, plus a reading of the image).
  - They contradict the committed n = 100 summary, so the figure must be replotted. That requires no new simulation.

## 8. Detector audit

| | Statistic (code) | Window | Threshold | Information used | Edge cases (a04, VERIFIED) |
|---|---|---|---|---|---|
| **B0** (`price_level.py`) | Mean over periods of (p₁+p₂)/2 | All T periods, including period 0; no burn-in | 1.4763064258. Flags on `score > τ`; README §9.10 writes ≥. | Prices | Constant prices behave correctly. |
| **B1** (`synchronization.py`) | Pearson corr(Δp₁,ₜ, Δp₂,ₜ) | Whole run | **None stored** | Prices | Zero variance gives NaN, which is returned as **0.0**.<br>Identical 1e-12 jitter on both firms gives **1.0**; independent jitter gives 0.27, so the score is scale-free.<br>Needs ≥ 3 rows.<br>**Depends on row order**: run 1 shuffled scores 0.42 against −0.13 sorted. |
| **B2** (`directional_dependence.py`) | max(corr(Δp₁,ₜ₋₁, Δp₂,ₜ), corr(Δp₂,ₜ₋₁, Δp₁,ₜ)) | Whole run | **None** | Prices | NaN is returned as 0.0.<br>Needs ≥ 4 rows.<br>Depends on row order.<br>Deterministic static runs score ≈ 1.0 from their transient. |
| **B3** (`deviation_response.py`) | An event is a one-period drop > 0.10 by either firm. A response is any next-period rival change < 0. Score = responses/events; two periods are skipped after a counted response. | Whole run | Event size fixed at 0.10; **no score threshold** | Prices | 0 events gives **0.0**, the same score as "never punished".<br>A rival decrease of 1e-9 counts as a response (score 1.0).<br>On the scripted deviation run, the counter-punishment counts as a second, unanswered event, giving **0.5**. |

**Observed scores** (a04, VERIFIED; labels joined after scoring):

| Data | B0 | B1 | B2 | B3 |
|---|---|---|---|---|
| Static, gap 0 (5 copies) | 1.4729 | 1.000 | 1.000 | 0 |
| Static, gaps 0.1-0.6 | 1.520 / 1.622 / 1.789 | −0.005 to −0.004 | ≈1.000 | 0 |
| Reactive, 400 runs (mean by gap) | 1.473 / 1.520 / 1.623 / 1.790 | −0.106 to −0.057 | 0.142 to 0.124 | 0 (all runs) |
| Reactive + shock, 20 runs | 1.471 to 1.790 | −0.120 to −0.066 | 0.110 to 0.172 | 0 |
| Adaptive + shock, 20 runs | 1.471 to 1.474 at **every** gap | 0.58 to 0.63 | −0.10 to −0.08 | 0 |
| **Collusive, constant 1.9** | 1.900 | **0** | **0** | **0** |
| Collusive with deviation (80 periods) | 1.847 | −0.265 | 0.848 | 0.5 |

**VERIFIED:** on the only steady-state collusive series, B1, B2 and B3 all score 0, which is *below* the static competitive runs (B1 = 1 at gap 0, B2 ≈ 1).

## 9. Can the current shock design create competitive price synchronization?

**Answer: no, except through an assumed agent rule.**

| Evidence | Label |
|---|---|
| With logit shares independent of Q and profits proportional to Q, best responses and Nash prices do not depend on Q. Best responses at Q = 0.8, 1, 1.2 are 1.4729281 (static) and 1.4729270 (reactive); the Nash price at Q = 0.8 and Q = 1.2 is 1.472927 (a02, a08). | VERIFIED |
| In the data, the static shock run's prices stay within 1.1e-6 of their mean. In the reactive + shock runs, the mean corr(ΔQₜ, Δpₜ) is −0.02/0.01 and the mean corr(Δp₁, Δp₂) is −0.10, so there is no synchronization (a05). | VERIFIED |
| Synchronization appears only in the adaptive runs (corr(Δp₁, Δp₂) = 0.60, B1 ≈ 0.6). It comes from the hard-coded target 1.472927 + s·(Q−1), which also ignores cost, which is why B0 is flat across gaps. Under this demand model, the profit-maximizing price response to Q is zero. | VERIFIED |
| The same model's competitive prices *do* move when demand shares shift:<br>• common attractiveness +0.2 gives a Nash price of 1.4864;<br>• a0 + 0.2 gives 1.4505;<br>• a₁ + 0.2 alone gives (1.5528, 1.4245).<br>FOC residuals are ≤ 6e-7 (a08, a09). No experiment uses such shifts. | VERIFIED |

## 10. Tables, figures and README claims

**Reproducible from existing data:**

| Item | Status | Label |
|---|---|---|
| README §12 FPR table, `b0_fpr_summary.csv`, `b0_hard_negative_results.csv`, `b0_threshold.txt` | Reproduced exactly from raw data | VERIFIED |
| The three detector-score CSVs | Reproduced to ≤ 3e-15 | VERIFIED |
| `hard_negative_cost_asymmetry.png` | The underlying means are reproduced (at gap 0.6: 1.6593 and 1.9197). I did not regenerate the image. | VERIFIED (data) |
| `competitive_equilibrium_reference.csv` | Values reproduced; the generating script is missing | VERIFIED |

**Stale:**

| Item | Status | Label |
|---|---|---|
| `b0_fpr_vs_cost_gap.png` | Built from n = 5 per gap. Replot only. | VERIFIED |
| `competitive_baseline.csv`, `competitive_cost_gap_*.csv`, `adaptive_competitive_demand_shocks.csv` | Generated by older code than the committed code | VERIFIED |

**Data exist, but extra processing is needed (no new simulation):**

| Item | What is needed | Label |
|---|---|---|
| B1-B3 FPRs | Thresholds can be calibrated on `b0_calibration_runs.csv` (prices only) and applied to the 400 reactive runs | VERIFIED (inputs exist) |
| Detector table for the reactive + shock runs | Score the existing 20 runs (n = 5 per gap). The output of `score_reactive_conditions.py` is not committed. | VERIFIED |
| B3 on the dynamic runs | `score_b3_dynamic.py` only prints. All values are 0. | VERIFIED |

**No supporting data:**

| Item | Status | Label |
|---|---|---|
| Any TPR, ROC/AUC, or comparison of detectors against collusion | No replicated collusive runs exist | VERIFIED |
| RQ2: common shocks cause competitive synchronization | Supported only through the hard-coded adaptive rule | VERIFIED |
| RQ5: quantities improve screening | No detector reads quantities, and no results exist | VERIFIED |
| RQ6: robustness across parameters and agents | One parameter set, no sweeps | VERIFIED |

**README statements that are false at this commit:**

| Statement | Status | Label |
|---|---|---|
| README §18.3 says "older and newer cost-asymmetry files" exist | Only one set is present | VERIFIED |

## 11. The three most serious problems

1. **There is no evaluable positive class.**
   - All collusive evidence is three deterministic single trajectories with hard-coded prices, so TPR, ROC/AUC and any claim about detecting collusion cannot be computed for any detector.
   - On the steady-state collusive series, B1, B2 and B3 score 0, lower than static competitive runs.
   - B0 flags it only because 1.9 is far above the symmetric Nash price. Yet the same outcome is the exact competitive equilibrium for a hidden cost of 1.5003, and a competitive firm at gap 0.6 prices above it (1.920). (§2 items 4-7, §8; VERIFIED.)
2. **The headline B0 result is mechanical, confounded and misreported in its figure.**
   - 100% FPR follows from the Nash mean price shifting at least 22 calibration SDs past a threshold set on symmetric costs.
   - Asymmetry is confounded with a rising mean cost.
   - The committed figure shows an n = 5 version of the result that contradicts the n = 100 summary. (§7; VERIFIED.)
3. **The designs for RQ2 and RQ3 cannot produce the confounders they are meant to test.**
   - Q-only shocks leave every profit-maximizing price unchanged, so synchronization appears only where it is hard-coded (adaptive agents, which also ignore cost).
   - The reactive "retaliation" branch never fired in 251,160 recorded changes, so the reactive hard negatives are noisy partial-adjustment best responders.
   - B3 found zero events on every competitive run. (§4.3, §8, §9; VERIFIED.)

Other problems found, all VERIFIED:
- **Provenance:** three orphan files, plus six stale files made by older code (the static baseline, the four cost-gap files and the adaptive baseline).
- **Duplicated runs:** 20 static "runs" are 4 trajectories.
- **Missing thresholds:** B1-B3 have none.
- **Output collision:** two scripts write `reactive_detector_scores.csv`.
- **Detector behaviour:** scores depend on row order, are scale-free, and default to 0.
- **Auditor boundary:** the auditor's knowledge of demand parameters is unspecified, even though that knowledge makes Q recoverable; run IDs encode the hidden condition and the seed.
- **README inaccuracy:** the `_new` datasets it describes are absent.
- **Environment:** pandas is one patch version off the pin.

## 12. What I could not verify

| Item | Why | Consequence |
|---|---|---|
| The exact pinned environment (pandas 3.0.6) | PyPI is blocked in this workspace (proxy 403) | The 52-pass result was obtained with pandas 3.0.5 |
| How the orphan files were generated (reference CSV, `adaptive_heterogeneous_demand_shocks.csv`, `collusive_deviation_response.csv`), and the earlier audit's `check_implied_cost.py` | No script exists in any commit | Their values are checked, but not where they came from |
| Byte-level regeneration of data and figures | The brief forbids new simulations; plotting scripts write into `results/` | Instead I matched every stochastic run to its stated seed through the update rules, and checked deterministic runs step by step |
| Python 3.13.11 and the "No broken requirements" run | Taken from the README | Remains REPORTED |
| Whether the 1.9/1.1/5-period strategy is incentive-compatible for any discount factor | The code has no discount factor; out of scope for Stage A | Deferred to Stage C (HYPOTHESIS-level question) |
| The authors' intended paper claims | No manuscript exists | Claims taken from the README only |

## Appendix: files I created

All are in the untracked folder `audit/stage_a/`. `git status --porcelain` shows only `?? audit/stage_a/`, and no tracked file changed.

| Script | Purpose | Output |
|---|---|---|
| `a01_inventory_csvs.py` | Rows, columns, runs, conditions, distinct trajectories, identical files | `out/a01_output.txt`, `out/a01_inventory.json` |
| `a02_market_checks.py` | Items 1, 2, 6, 7, 8, 9: shares, implied cost, Nash at ĉ, Q invariance | `out/a02_output.txt` |
| `a03_b0_recompute.py` | Threshold, B0 scores, FPR, Wilson and Clopper-Pearson intervals | `out/a03_output.txt`, `out/a03_b0_fpr_recomputed.csv` |
| `a04_detector_audit.py` | B0-B3 recomputation, summaries, positive controls, trigger counts, edge cases | `out/a04_output.txt` |
| `a05_shock_analysis.py` | Shock frequency, persistence, price-Q association | `out/a05_output.txt` |
| `a06_provenance_seeds.py` | Seed policy via implied noise; adaptive and static rule checks | `out/a06_output.txt` |
| `a06b_static_timing.py` | Simultaneous vs. sequential update timing per static file | `out/a06b_output.txt` |
| `a07_auditor_boundary.py` | Auditor columns, run_id blocks, Q recoverability, detector inputs | `out/a07_output.txt` |
| `a08_figures_and_attractiveness.py` | Wilson intervals implied by the figure; Nash prices under demand shifts | `out/a08_output.txt` |
| `a09_inline_checks.py` | Static file comparison, deviation files, FOC residuals | `out/a09_output.txt` |

The audit environment is a venv at `/home/claude/audit_env` (Python 3.13.18, using the preinstalled packages), outside the repository. Tests ran on a separate copy at `/home/claude/pytest_copy`.
