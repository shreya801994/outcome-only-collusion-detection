# Abstract and novelty statement (draft for the journal paper)

*6 November 2026, branch `review/option-b`. Every number below comes from a committed result file; the mapping is in §3.*

**Read §4 before submitting.** It lists the claims we must not make, and the one check still needed: Belal's full text, which is unread.

---

## 1. Title options
1. *What Do Outcome Screens for Algorithmic Collusion Test? Hidden Costs, Adjustment Speed, and an Adjustment-Robust Alternative*
2. *Screening Algorithmic Collusion Without Costs: Operating Points, Adjustment Dynamics, and the Limits of Interventions*

## 2. Abstract

### 2a. Detailed abstract (about 330 words)
> Competition authorities increasingly screen markets for algorithmic collusion using outcomes they can observe (prices, quantities, sometimes market size) without seeing firms' costs or pricing rules. We study what such screens actually test, in a repeated logit duopoly with hidden and possibly asymmetric costs, demand shocks that either move market shares or only market size, and pricing agents that are either scripted partial adjusters or Q-learning algorithms in the environment of Calvano et al. (2020). Across 19,570 pre-registered simulated markets and 450 Q-learning sessions, with every decision threshold frozen in advance, we find three things. First, standard screens test a narrow competitive benchmark rather than collusion. A price-level screen calibrated at the wrong cost flags 57% of competitive markets. Implied-cost stability tests, including a constant-cost identified-set test ported from recent work, rank collusion perfectly only against fast-adjusting competitors, and at their frozen thresholds they flag every slowly adjusting honest firm. Classic variance screens reverse sign once punishments occur on path. Second, we propose a test that estimates each firm's cost and adjustment speed from outcomes, by inverting logit shares, and then tests the residuals for serial dependence. Its null distribution does not depend on adjustment speed. In a pre-registered evaluation it separates slow cartels from slow competitors (AUC 0.977) while keeping a 4.8% false-positive rate under a threshold calibrated on fast competitors, where the cost-stability screens reach 100%. Third, we show that the limits are structural. A regulator-feasible version of a mandated price-increase probe loses its power under slow, noisy adjustment (AUC 0.50), although it works well against Q-learners (AUC 0.93), against which our test fails (AUC 0.66). And any high-price policy that applies a competitive rule at inflated costs is exactly indistinguishable from competition, both in outcomes and in responses to any intervention. No outcome-based or interventional test, ours included, can detect it without cost information. Screens should therefore be reported as tests of an explicit null class of competitive behaviour, with their operating points under realistic uncertainty about costs, demand and dynamics.

### 2b. Short abstract (about 150 words, for conference systems)
> Outcome screens for algorithmic collusion are usually evaluated by ranking power. We evaluate them at frozen operating points in a logit duopoly with hidden costs, share- or size-moving demand shocks, scripted partial adjusters and Calvano-style Q-learners (19,570 pre-registered markets; 450 learning sessions). Cost-stability screens, including a ported identified-set test, flag every slowly adjusting honest firm, and variance screens reverse sign under on-path punishments. An adjustment-robust test, which estimates cost and adjustment speed from outcomes and tests residual dependence, keeps a 4.8% false-positive rate across adjustment speeds while separating slow cartels (AUC 0.977). A regulator-feasible price-increase probe fails for slow firms but works for Q-learners, where our test fails. A high-price policy applying a competitive rule at inflated costs is exactly undetectable by any outcome or intervention test. Screens are tests of a stated competitive class, not of collusion.

## 3. Contributions, each mapped to its evidence

**Novelty labels.**
- **NEW-likely:** not found in Belal's abstract or public repository, nor in the screening papers we checked. Belal's full text is unread, so this must be confirmed before submission.
- **REPLICATION:** confirms a known result with an explicit operating point.

| # | Claim | Evidence (pre-registered unless marked) | Key numbers | Novelty |
|---|---|---|---|---|
| C1 | **An adjustment-robust competitive-consistency test.** It estimates cost and adjustment speed from outcomes by logit inversion; the residual-dependence statistic is speed-invariant under the partial-adjustment null. | Addendum 4 (`V2_ADDENDUM_4_OPTION_B.md`; kill criterion fixed earlier in `FINAL_AUDIT.md` §5) | AUC 0.977 [0.964, 0.987] slow rigid vs slow competitors; FPR 0.048 [0.028, 0.081] at a threshold calibrated on fast competitors; slow vs fast honest competitors 0.518 (D 1.000); tracking cartel 0.996; μ estimated: AUC 0.964, FPR 0.004 | **NEW-likely.** It answers, within one class, Belal's point that constant-cost tests measure "precision of optimization" |
| C2 | **Cost-stability screens fail at the operating point, not in ranking.** This holds for our D and for Belal's identified-set coverage. | Addenda 2, 3, 5 | Slow competitors flagged at the frozen threshold: D 1.000, BC 1.000. AUC slow rigid: D 0.854–0.857, BC 0.930 | REPLICATION of Belal's qualitative point, plus a new explicit operating point and a direct comparison |
| C3 | **The regulator-feasible probe fails under slow adjustment; the sign rule R < 0 misses cartels that do not punish increases; honest Nash-trackers fail the probe too.** | Addendum 6 | Before/after AUC 0.495, FPR 0.207 (slow); counterfactual AUC 0.974 but FPR 0.878 at the fast-calibrated threshold; R < 0 in ≤ 0.4% of scripted cartels; Nash-trackers R = 0 in 100% | **NEW-likely** stress test of Belal's intervention |
| C4 | **On learning agents the ranking reverses:** the probe works and the adjustment-robust test does not. No single test dominates. | Addendum 7 (validated Calvano engine: Δ 0.828, 100% convergence, 94% punish) | Probe 0.929; Option B 0.658 (17% FPR at its frozen threshold); D 0.393; BC 0.268; B0 0.970 | **NEW-likely** (comparison across agent classes) |
| C5 | **Interventions cannot cross the cost-identification boundary.** A policy applying a competitive rule at inflated costs is pathwise identical to honest firms with those costs, under every outcome and every intervention, provided its rule uses no true-cost profit (condition S). | Proposition 3 (`PROPOSITION_v3.md`); addenda 4–6 twin checks | Max difference 0.0; AUC 0.500 for every passive screen, for Option B and for both probe statistics | Passive version: overlaps Belal's pointwise rationalisation. **Intervention extension: NEW-likely** |
| C6 | **Classic variance screens reverse sign when punishments occur on path.** | Addendum 5 | CV screen AUC 0.004–0.050 (E0, E1, wide costs); 0.971 without price cuts or punishments | Small. It is consistent with the mixed signs in Bolotova et al. (2008); framing it as on-path punishment is our addition |
| C7 | **Operating-point decomposition of screen errors.** | Main design, confirmatory, addenda 2–3; exploratory re-analyses | B0 naive FPR 0.57 (confirmed 0.567); FPR governed by hidden cost level and asymmetry; D needs share-moving (not size) shocks; μ +20% gives FPR 0.215 | Incremental (this was the original contribution) |

**Run counts (VERIFIED from code):**

| Block | Count |
|---|---|
| Main design | 4,180 |
| Confirmatory | 1,620 |
| Addendum 2 | 1,080 |
| Addendum 3 | 540 |
| Addendum 4 | 1,350 |
| Addendum 6 | 10,800 (5,400 probed and unprobed twins per environment) |
| **Pre-registered scripted runs** | **19,570** |
| Addendum 7 | 450 Q-learning sessions |
| Exploratory sensitivity (reported separately) | 16,200 |
| Addendum 5 | no new draws |

### 3a. Closest work checked on 6 November 2026 (VERIFIED from abstracts)
- **Hespanhol & Aswani (2020), arXiv 2003.09967.** A hypothesis test of competitive conduct from prices and *observed* shocks.
  - It assumes ε-approximate Nash play each period and explicitly does not model learning or how prices are reached.
  - C1 differs: partial adjustment toward the best response is modelled, adjustment speed is estimated, and shocks are recovered from shares rather than observed.
- **Xu, Wu, Lu, Tan, Tao & Hong (2026), arXiv 2607.26385,** "Collusion with Competitive Marginals: Price-Level Audits Are Blind by Construction".
  - A different blindness result: agents coupled only through the joint law of their residuals, with each agent's own price law competitive, so single-agent audits have power equal to size.
  - It is related to C5 but uses a different mechanism (cross-agent coupling rather than cost mimicking) and does not cover interventions. **Cite it next to C5.**
- **Eschenbaum & Meylahn (2026), arXiv 2608.07098,** "Auditing Algorithmic Collusion from Strategy Graphs".
  - It audits by querying the frozen policy (graph metrics on Q-learning policies). That requires policy access, which is outside our outcome-only setting.
  - It complements C4: when outcome tests disagree across agent classes, policy access is one way out.

## 4. Claims we must not make
1. **Not "first to show passive screens fail under hidden costs".** Belal (2026) shows it.
2. **Not "Option B detects algorithmic collusion".** It tests the partial-adjustment best-response class. It fails on Q-learners (0.658), and its weakest scripted case is the fast rigid cartel (0.790).
3. **Not "the probe does not work".** It works on learners (0.929) and with the counterfactual. What fails is the *regulator-feasible* version under slow, noisy adjustment with 5 probes.
4. **Not "the cost-mimicking policy is a cartel".** No incentive constraint is modelled; it is a high-price policy.
5. **Do not cite Belal's numbers as verified.** His AUC 1.00 and myopic R < 0 rate of 8% are REPORTED from his repository. The difference between his myopic rate and ours (49%) is unexplained.
6. **Do not describe any finite-sample AUC as "non-identification".** Use the taxonomy in `PROPOSITION_v3.md`.

## 5. Before submission
1. **Belal's full text.** Read it when available and recheck C1, C3, C4 and C5 for prior statements. In particular, check whether he already discusses the intervention version of cost mimicking, or adjustment-speed-robust passive tests.
2. **Literature search for adjustment-speed or partial-adjustment conduct tests,** in empirical IO (dynamic pricing with adjustment costs) and in screening. A first check (§3a) found none; a full search is still needed. If one exists, C1 becomes "applying X to algorithmic screening".
3. **Venue.**
   - Primary journals: *Computational Economics*, *Journal of Economic Interaction and Coordination*.
   - Stretch: *International Journal of Industrial Organization*, a natural home for screening papers (Abrantes-Metz et al. 2006; Bolotova et al. 2008).
   - Conferences: IIOC 2027 (call expected in December) or an AAMAS 2027 workshop.

## 6. Verification (VERIFIED, 6 November 2026)
- **Clean-clone reproduction.** A fresh clone of `review/option-b` at `d832403` ran addenda 4–7 from scratch: probe 46 s, Q-learning 588 s, passive benchmark 282 s, Option B 724 s, on 2 CPUs.
  - Every score, metric and check file is **byte-identical** to the committed one.
  - The only differences are the `runtime_seconds` fields in two criteria files.
  - The probe and passive-benchmark printed outputs are identical.
  - 71 tests pass.
- **The degenerate-path fix changed no addendum-4 result.** Addendum 4 was first run before the fix; it reproduces identically with the fixed code.
- **Earlier results are untouched.** All 66 `results_v2/` and `data_v2/` files that existed before addendum 4 match their SHA-256 fingerprints.
- **Numbers in §2–§3** were checked against `addendum4_metrics.csv`, `addendum5_metrics.csv`, `addendum6_metrics.csv`, `addendum7_metrics.csv`, the criteria JSON files and `rates.csv`.
