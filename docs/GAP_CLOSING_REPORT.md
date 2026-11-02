# Gap-closing report

*2 November 2026. Branch `review/gap-closing`, built on `review/final-audit` and `v2-identification-benchmark`. No existing data file, result file, pre-registered threshold or kill criterion was changed; earlier `results_v2/` files were checked unchanged with SHA-256 before and after the new run.*

**Labels used below.**
- **NEW:** produced today.
- **VERIFIED:** I ran or read it.
- **REPORTED:** from a secondary source or from the team, not checked by me.
- **BLOCKED:** could not be done, with the reason given.
- **UNRUN:** deliberately not run.

---

## 1. Updated experiment results (Task 1, NEW)

Pre-registered in `docs/V2_ADDENDUM_3_SLOW_RIGID.md` and pushed before running (commit `e1df209`). Results in commit `841ff15`.

**Design:**
- Slow rigid cartel vs slow competitors in E2 (share-moving shocks).
- Matched dynamics: adjustment speed λ ~ U[0.05, 0.20], noise SD 0.02, price-cut probability 0.01.
- Matched 3 × 3 hidden-cost grid, T = 300 with burn-in 50; 270 runs per arm.
- Fresh seeds (base 20261106); thresholds frozen from the main-design calibration split (base 20261102).

| Screen | AUC pooled [95% CI] | AUC within cost cell | TPR [CI] | FPR [CI] | Precision* | F1* |
|---|---|---|---|---|---|---|
| B0 | 0.983 [0.977, 0.989] | 1.000 | 0.893 [0.867, 0.922] | 0.033 [0.015, 0.052] | 0.964 | 0.927 |
| B1 | 0.953 [0.936, 0.968] | 0.950 | 1.000 | **0.996** [0.989, 1.000] | 0.501 | 0.667 |
| B2 | 0.942 [0.923, 0.959] | 0.938 | 0.044 [0.022, 0.070] | 0.000 | 1.000 | 0.085 |
| B3 | 0.798 [0.762, 0.834] | 0.800 | 0.000 | 0.000 | undefined | undefined |
| D (L3) | 0.854 [0.831, 0.876] | 0.931 | 1.000 | **1.000** [0.986, 1.000]† | 0.500 | 0.667 |

\* At an assumed 50% prevalence. CIs are run-level stratified bootstrap (2,000 resamples), except †, which is a Wilson interval; full CIs are in `results_v2/addendum3_metrics.csv`.

B3's frozen threshold (1.0) cannot be exceeded, so B3 flags nothing at any operating point. Its AUC is the only informative number for it.

**Pre-registered checks:**

| ID | Rule | Result | Pass? |
|---|---|---|---|
| S1 | AUC(D) ≥ 0.80 for slow rigid vs slow competitors | 0.854 | pass |
| S2 | FPR of slow competitors ≤ 0.10 at the frozen D threshold | 1.000 | **fail** |
| S3 | Dynamics contrast < conduct contrast | Slow vs fast *competitors*: AUC(D) **1.000** [1.000, 1.000]; slow cartel vs slow competitors: **0.854** | **fail** |

**Conduct or adjustment dynamics? Mostly dynamics.** VERIFIED.
- Changing only competitors' adjustment speed moves D's median about five-fold (0.033 → 0.159) and is detected perfectly.
- Changing conduct with dynamics matched is detected less well (0.854).
- At the frozen threshold, D flags every slow competitor, so its precision is at chance.
- D carries a secondary conduct signal only if its null is calibrated on competitors with the correct adjustment speed, which the auditor does not observe.
- B1's frozen threshold fails the same way.
- B0 still separates here because the cartel markup is large relative to the design's cost range; its confounding under wider cost uncertainty is in addendum 1 (C1).

This replicates, with scripted agents, Belal's (2026) reading that such tests measure "precision of optimisation, not the objective" (REPORTED from his repository; see §3).

## 2. Corrected auditor information specification (Task 2, VERIFIED)
Full specification: `docs/AUDITOR_INFORMATION_SPEC.md`. Evidence: `experiments/audit_information_boundary.py`.

- **B0-B3** receive prices only.
- **D** receives prices and quantities, plus market size at L3. It uses **observed shares** sᵢ = qᵢ/Q, never the demand model's shares.
- **D does not use attractiveness parameters.** It uses μ only. D from q/Q equals D from the model shares s(p; aₜ) to within ≤ 1.2e-6 (float32 storage).
- **L2 is corrected to:** "quantities observed; total market size not observed and *assumed known and constant* at its baseline value (Q = 1)." In E0/E2, D_L2 = D_L3 exactly; in E1/E3 they differ by up to 3.2. L2 is not valid under an unknown constant Q ≠ 1, because every share is then mis-scaled.
- **L3:** market size observed, or equivalently the outside share. Q = (q₁ + q₂)/(1 − s₀) is recovered to 2e-7.
- **Errata:**
  - `FINAL_AUDIT.md` §6, item 5 wrongly said the ladder "assumes known attractiveness levels".
  - The deck's slide 5 says "market size assumed constant"; the correct wording is "assumed known and constant".
  - `PROPOSITION.md`, line 12 is ambiguous (see §4).

## 3. Belal comparison (Task 3: full paper BLOCKED)

**Record.** Ali Belal, *Intervention, Not Inference: The Identification of Algorithmic Collusion*, SSRN abstract ID 7266558, 30-page versions of 13 and 15 August 2026. REPORTED by the team: my direct fetch is refused, and the SSRN page loaded in the Claude app's browser on your computer stops at a "verify you are not a bot" check. I did not try to bypass it.

**What was read.** The public replication repository [alibelal-lang/algorithmic_collusion](https://github.com/alibelal-lang/algorithmic_collusion) (single branch, commit 23867f3, 11 Aug 2026):
- `part3_identification_critique.md`, `part6_screen.md`, `part10_cost_ladder.md`, `part15_assumption_ladder.md` and `part18_cost_intervals.md`, all in full;
- `REPRODUCING.md`, which maps the paper's tables to scripts;
- `env.py`.

The repository references `paper/paper.pdf`, but that file is not in the upload.

**Therefore Task 3 is not complete.** The comparison below rests on the replication write-ups, not the paper's text. Do not cite proposition numbers, wording or the final framing until the PDF has been read.

| Topic | Belal (from repository) | Ours | Assessment |
|---|---|---|---|
| Environment | Calvano logit duopoly, μ = 0.25, a = 2, c = 1; Markov demand states shifting attractiveness | Same logit, same parameters; AR(1) attractiveness and market-size shocks | **Same** |
| Agents | Tabular Q-learning, bandits, myopic and memoryless learners, menu-cost best responders, function approximation | Scripted: partial-adjustment best response, rigid/tracking/cost-padding cartels | Different; **his are more realistic** |
| Pointwise rationalisation c = p − μ/(1 − q) | Stated as a proposition (part10) | Proposition 1 | **Same result** |
| Constant cost as the identifying restriction | Cost-restriction ladder; calibrated dispersion null; grid-inequality cost intervals (parts 10, 18) | Proposition 2 + screen D | **Same idea**; his inequality method is more rigorous |
| Tests flag imprecise but honest optimisers | Myopic and memoryless learners fail 100%; "precision of optimisation, not the objective" | Slow competitors flagged 270/270 (H1a, S2); dynamics contrast 1.000 (S3) | **Same finding**; ours is an independent replication with a different competitor model (partial adjustment) |
| Passive screens convict benign high-cost firms | 97% of high-cost menu-cost competitors labelled collusive (part6) | B0 naive FPR 0.57; cost-spread confounding 0.22 (C1) | **Same finding** |
| Parallel pricing uninformative | Cross-firm correlation 0.94-1.00 in all regimes | B1 confounded by cost level and dynamics | **Same conclusion** |
| Exact identity of a cost-mimicking cartel with higher-cost competition | High-cost menu-cost competitor plays this role; exact identity not stated in the write-ups | Proposition 3; paired differences 0.0 | Ours is a sharper construction of the same point. **Small.** |
| Auditor's demand information | Regulator given the exact demand system and the true demand state (part18) | Ladder: shares needed (market size or outside share); attractiveness not needed; μ ±20% tolerated | **Possibly distinct**, small |
| Market-size-only shocks | Not found | Shown to carry no identifying variation (E1; K2) | **Possibly distinct**; theoretically immediate |
| Cost level vs asymmetry | One asymmetric case (0.9/1.1), out of taxonomy | 3 × 3 grid separating level from gap | **Possibly distinct**, small |
| Interventions (probes) | Main constructive result: single-market detection by mandated undercuts | None | **His alone** |
| Policy-evaluation econometrics (DiD, staggered adoption) | Extensive | None | **His alone** |
| Pre-registration | Not found | Every addendum pre-registered and pushed before running | Ours (method, not science) |

**Remaining novelty, stated without invention:** small and incremental. Section 5 has the defensible statement.

## 4. Theory and reference audit (Task 4)

| Item | Status | Finding |
|---|---|---|
| Lau (1982), *On identifying the degree of competitiveness from industry price and output data*, Economics Letters 10(1-2): 93-99 | Full text **BLOCKED** (ScienceDirect shows a CAPTCHA in your browser; no open copy found) | Its theorem as restated by Matsumura & Otani (2024, [arXiv 2410.16998](https://arxiv.org/html/2410.16998v1)), REPORTED: with inverse demand P = f(Q, Xᵈ) and a conduct parameter θ, θ is *not* identified iff demand is separable in Xᵈ and not of the form P = Q^(−1/θ) r(Xᵈ) + s(Q). Matsumura & Otani give a separable log-linear counterexample that *is* identified. **Implication:** cite Lau only for the general idea that identification needs demand rotation or non-separability, and note that Matsumura & Otani dispute one direction of it. Lau is a homogeneous-goods conduct-parameter result, not a logit-Bertrand result. |
| Mizuno (2003), *On the existence of a unique price equilibrium for models of product differentiation*, IJIO 21(6): 761-793 | Full text **BLOCKED** (paywall; no abstract on RePEc) | Secondary source (Sándor, [EUR working paper](https://repub.eur.nl/pub/1828/ei200450.pdf)), REPORTED: Mizuno extends Caplin & Nalebuff (1991) uniqueness results for **single-product** firms. Its exact conditions (log-concavity or log-supermodularity, outside good, costs) could not be checked. The same source attributes uniqueness for single-product logit to Milgrom & Roberts (1990). **Decision: do not cite Mizuno.** Uniqueness is no longer used (`FINAL_AUDIT.md` §3). |
| Bresnahan (1982) | VERIFIED (reprint) | Rotations, not parallel shifts, identify conduct when cost is unknown. Use as the main identification citation. |

**Unsupported or imprecise claims remaining in `docs/PROPOSITION.md`.** The file is unchanged; corrections are proposed here.

1. **Lemma 1, existence of the stationary point is not shown.** Add: f(p) = 1/(p − c) − (1 − s)/μ is continuous and strictly decreasing on (c, ∞), tends to +∞ as p → c⁺ and to −1/μ < 0 as p → ∞, so it has exactly one root. (The concavity argument itself is correct.)
2. **Proposition 1 assumes known attractiveness ("Fix (a, a₀, μ)").** It is stronger than needed. With shares observed, aᵢ = pᵢ + μ·log(sᵢ/s₀) + a₀ rationalises them for any a₀, so only μ is needed. Restate with observed shares.
3. **Proposition 2(a), "competition ⇒ ĉ constant", holds only for contemporaneous static Nash prices.** Our simulated competitors best-respond to the rival's *previous* price and adjust partially. Then ĉᵢₜ ≠ cᵢ even without noise, which is why fast competitors have D ≈ 0.033 > 0 and slow ones fail (S2). The proposition must say "under contemporaneous static Nash pricing" and must not be cited as describing the simulated competitors.
4. **Proposition 2(b): the joint-profit markup μ/s₀ is asserted without derivation, and "varies whenever shares vary" is too strong.**
   - Derivation to add: the joint first-order condition gives mᵢ − Σₖ mₖsₖ = μ for each i, hence equal markups m = μ/s₀.
   - Replace "whenever shares vary" with "except along share paths on which sⱼ/(s₀(1 − sᵢ)) is constant".
   - Our tracking cartel uses a κ-blend of Nash and joint-profit prices, which 2(b) does not cover.
5. **Proposition 3 must state that it concerns on-path outcomes only.** It does not show that a cost-padding cartel is sustainable: no incentive constraint is checked, and each firm's static best response at its true cost is lower. It also requires that no punishment or off-path behaviour is ever observed.
6. **Remark 1 cites "AUC 0.38" without its comparison group.** It should say: against competitors at the true cost; against the matched twin the AUC is exactly 0.500 (`results_v2/audit_h2_output.txt`).
7. **Line 3 cites Lau (1982) as support.** Add the Matsumura & Otani caveat (above).
8. **Line 12 says the auditor knows "the attractiveness levels only where stated".** Replace with the specification in §2: μ known; shares observed; attractiveness not needed.

## 5. Revised abstract and contribution statement

**Contribution statement (defensible).**
> In the Calvano et al. (2020) logit duopoly, we provide an independent, pre-registered replication, with scripted agents, of the result that passive outcome-based screens for algorithmic collusion test consistency with a specific competitive benchmark rather than conduct (Belal 2026). We add three things. (i) A specification of the demand information an implied-cost screen needs: shares (via market size or the outside share) and the demand parameter μ, but not attractiveness; shocks to market size alone carry no identifying variation. (ii) A decomposition of hidden-cost confounding into level and asymmetry. (iii) Evidence that the screen's error rates are governed more by competitors' unobserved adjustment speed than by conduct.

**Revised abstract.**
> Regulators screening for algorithmic collusion typically observe prices and quantities but not marginal costs. In a logit duopoly with hidden, possibly asymmetric costs, we test common outcome screens in 7,420 pre-registered simulation runs, plus 16,200 exploratory runs reported separately. A price-level screen calibrated on symmetric costs flags 57% of competitive firms once costs are hidden. An implied-cost stability screen separates fast-adjusting competitors from fixed-markup cartels under demand shocks that move market shares, but not under shocks to market size alone. Its frozen threshold flags every slowly adjusting competitor. When cartel and competitors adjust equally slowly, separation falls to AUC 0.82-0.85, while adjustment speed alone separates honest competitors perfectly. A cartel that prices as competition at higher costs is indistinguishable from it. The screen needs observed shares and the demand parameter, but not product attractiveness. Consistent with Belal (2026), outcome screens are best read as tests of a stated competitive benchmark whose error rates depend on unobserved costs and adjustment dynamics.

**Run counts, VERIFIED from the result files:**

| Set | Runs |
|---|---|
| Main design | 4,180 |
| Confirmatory (addendum 1) | 1,620 |
| Addendum 2 | 1,080 |
| Addendum 3 | 540 |
| **Pre-registered total** | **7,420** |
| Exploratory sensitivity (S1-S6) | 16,200 |
| **All runs** | **23,620** |

**Erratum:** `docs/V2_RESULTS.md` and the deck say 13,500 exploratory runs. That figure predates the S5/S6 analyses; the correct number is 16,200.

## 6. Unresolved limitations
1. **Belal full text unread (BLOCKED).** The comparison rests on his replication write-ups. Someone must download the 15 August version and check §3.
2. **Lau (1982) and Mizuno (2003) full texts unread (BLOCKED).** Lau is cited via Matsumura & Otani (2024); Mizuno is dropped.
3. **Scripted agents only.** No learning agents; Belal's learners are more realistic.
4. **One demand family (logit) and one parameter set** (μ = 0.25, a = 2).
5. **Thresholds are calibrated on fast competitors.** No calibration exists that is robust to unknown adjustment speed. That is what Option B would address.
6. **`PROPOSITION.md` needs the eight corrections in §4** before it can go into a paper.
7. **The deck (slides 4, 5, 9, 10) contains statements superseded** by `FINAL_AUDIT.md` and this report. It is unchanged, as instructed.
8. **Run counts in `V2_RESULTS.md` and the deck are stale** (13,500 exploratory, now 16,200); corrected in §5 here.
9. **Option B: UNRUN.** Its pre-registered kill criterion (`FINAL_AUDIT.md` §5) is unchanged: stop if, after estimating adjustment speed, AUC(slow cartel vs slow competitors) < 0.90 or FPR at a frozen threshold > 0.10. **It is not reported as completed.**
