# Final audit: identification, robustness and novelty

*2 November 2026. Written on the separate branch `review/final-audit`. No existing result, data file or slide was changed.*

## Evidence labels
- **VERIFIED:** I ran or read it (script or file named).
- **REPORTED:** from someone else's summary, unchecked.
- **READ (repo):** taken from Belal's public replication repository, not from the paper PDF. That PDF is not in the repository, and SSRN blocks automated access.

---

## 1. Observational-equivalence audit (AUC 0.38)

Script: `experiments/audit_h2_auc.py`. It re-runs the existing code with the addendum-2 seeds.

| Check | Result | Label |
|---|---|---|
| Cartel vs competitors at the **same** true costs (c + m), shared random streams | Every paired score difference for B0, B1, B2, B3 and D is **0.0**; every AUC is **0.500** | VERIFIED |
| Stored H2 cartel scores reproduced | yes | VERIFIED |
| Label orientation | positive = `collusive_cost_padding`; a higher score means more suspicious | VERIFIED |
| Pre-registered H2 comparison | cartel at effective mean cost **1.351** vs competitors at true mean cost **1.000** | VERIFIED |
| Cost level alone, honest competitors only (main design, E2) | Mean cost 1.15 vs 0.85: AUC(D) **0.399**, AUC(B1) **0.762**. The same direction as H2's 0.378 and 0.836. | VERIFIED |

**Why AUC 0.38 is not 0.50.** H2 compared the cartel with competitors at a *different* cost level, not with its observational twin. My earlier write-up said "identical" without naming the comparison group; that was the error, not the data.

**Why D falls with cost level.** A higher price means a lower share. The slope of μ/(1 − s) in s is smaller at low shares, so the same price noise moves the implied cost less.

**B1 = 0.836 is a cost-level effect, not conduct.** Honest competitors alone reproduce it (0.762), and against the matched twin B1 scores exactly 0.500.

**Scope.** This shows exact equivalence in this model (logit, constant costs, the simulated dynamics) between a cartel that prices as Nash at cost c + m and competitors at c + m. It is **not** a universal impossibility theorem. See Proposition 3 for the exact scope.

## 2. Hard-negative audit

| Item | Result | Label |
|---|---|---|
| Why D flags all 270 slow competitors | Median D for slow competitors is **0.165** (min 0.087), against the frozen threshold of **0.054**. Fast competitors have a median of 0.033. With adjustment speed 0.05-0.20, prices lag the moving best-response target, so p − μ/(1 − s) ≠ c and swings with the persistent shocks. | VERIFIED (addendum-2 scores) |
| Matched slow cartel vs slow competitors | AUC(D) 0.822 [0.795, 0.850]: separation survives but weakens. Only the tracking cartel was run slow; a slow rigid cartel was not. | VERIFIED; gap noted |
| What D exploits | Departures from *immediate* static best response at constant cost: the adjustment lag, the cartel markup, and noise. That is precision of optimisation, not conduct. | VERIFIED (H1a + H2) |
| Strategy-specific main results | Rigid and tracking cartels are each reported separately with CIs (`results_v2/auc.csv`) and at operating points (`results_v2/operating_points.csv`) | VERIFIED |

## 3. Theory: what the proposition needs, and the uniqueness question

**Uniqueness is not needed.** Observational equivalence requires only that the observed prices *are an* equilibrium of a competitive game with some admissible costs. Whether that game has other equilibria is irrelevant to "competition could have produced this." I therefore drop the uniqueness claim from `docs/PROPOSITION.md`; see the corrected statement below.

**Proposition (pointwise rationalisation, logit duopoly).**

*Assumptions:*
- **(A1)** Shares follow multinomial logit with an outside good, with known (a₀, a₁, a₂, μ), μ > 0.
- **(A2)** Profit is (pᵢ − cᵢ)·Q·sᵢ, with constant unobserved marginal cost cᵢ.
- **(A3)** The auditor observes (p₁, p₂) and the shares (or quantities and Q).
- **(A4)** The admissible cost set is 𝒞 ⊆ ℝ.

*Claim:* If ĉᵢ := pᵢ − μ/(1 − sᵢ) ∈ 𝒞 for i = 1, 2, then:
- (p₁, p₂) is a static Nash equilibrium of the game with costs (ĉ₁, ĉ₂);
- repeating it every period is a subgame-perfect equilibrium of the repeated game.

*Proof:*
1. For p ≤ ĉᵢ profit is ≤ 0. On p > ĉᵢ, log πᵢ = log(p − ĉᵢ) + log sᵢ + const.
2. ∂² log sᵢ/∂pᵢ² = −sᵢ(1 − sᵢ)/μ² < 0, so log πᵢ is strictly concave and its stationary point is the global maximiser.
3. The stationary point satisfies p − ĉᵢ = μ/(1 − sᵢ), which holds at pᵢ by construction, so each pᵢ is a best response to pⱼ.
4. Repeating a static equilibrium is subgame perfect. ∎

*Corollaries:*
- **(i) Testable restriction.** With constant costs and share variation, competition implies ĉᵢₜ constant over t, while a fixed-markup cartel does not satisfy it (Proposition 2 in `PROPOSITION.md`).
- **(ii) Boundary.** A cartel that plays the static Nash prices of costs cᵢ + m is identical, as an outcome process, to competition at cᵢ + m (Proposition 3). It is never identified without cost information.

*It does not cover:* non-logit demand, cost that varies over time, learning or partially adjusting competitors (H1 shows these break the constant-ĉ restriction), capacity constraints, or estimated μ beyond ±20%.

**This is not new.** Bresnahan (1982) and Lau (1982) give the general identification logic. Belal (2026) states the same pointwise proposition for the same logit environment (§4).

## 4. Closest work: claim-by-claim comparison

Belal's material was read from the public replication repository `alibelal-lang/algorithmic_collusion` (commit 23867f3, 11 Aug 2026): write-ups part3, part6, part10, part15, part18, and `env.py`. The SSRN record ID is **unresolved**: search results give 7267038, the external review gives 7266558, and a fetch of 7266558 returned an unrelated paper. Verify before citing.

| Our claim | Belal 2026 | Others | Verdict |
|---|---|---|---|
| Collusive prices are rationalisable as competition at hidden cost ĉ = p − μ/(1 − s) | **Same formula, same logit/Calvano environment** (μ = 0.25, a = 2). Example: c′ = 1.272 rationalises a collusive panel. Pointwise proposition stated. READ (repo) | Bresnahan 1982; Lau 1982 (general) | **Remove as a contribution**; cite |
| A constant-cost restriction makes conduct testable | **Done**: "cost-restriction ladder"; within-market implied-cost dispersion against a calibrated null; grid inequality intervals. READ (repo) | Bresnahan 1982 (rotations) | **Remove**; cite |
| Implied-cost stability flags non-collusive slow or imprecise optimisers (our H1a) | **Done**: the test "measures precision of optimisation, not the objective"; myopic and memoryless learners are flagged 100%. READ (repo) | none | **Remove as new**; our H1a is an independent replication with scripted agents |
| Price-level / passive screens convict benign high-cost firms | **Done**: a 99%-accurate screen labels high-cost menu-cost competitors collusive in 97% of markets. READ (repo) | Wang, Zhang & Hartline 2025 (cost claims defeat regret audits) | **Remove as new**; our B0 numbers are a replication |
| Parallel pricing (B1) is uninformative | **Done**: cross-firm correlation is 0.94-1.00 in all regimes. READ (repo) | Harrington (screens), REPORTED | **Remove** |
| Share-moving vs market-size demand variation | Belal uses Markov demand states that shift attractiveness (share-moving). No market-size-only comparison found. READ (repo, `env.py`) | none | **Narrow:** our explicit market-size-only null (E1) is a small addition; theoretically immediate |
| Auditor information ladder: market size / outside share needed; μ misspecified ±20% | Belal gives the regulator exact demand-system knowledge and the true demand state (part18). No market-size or μ-misspecification ladder found. READ (repo) | Hespanhol & Aswani 2020 assume observed shocks | **Possibly retainable**, but small |
| Hidden cost level vs asymmetry, separated on a 3×3 grid | Belal tests one asymmetric case (0.9/1.1) out of taxonomy | none | **Possibly retainable**, small |
| Exact identity of a cost-mimicking cartel and higher-cost competition | Belal's high-cost menu-cost competitor (c = 1.272) plays the same role; exactness not stated | none | **Narrow** to a clarifying construction |
| Pre-registered, replicated benchmark with frozen thresholds | Belal: market-level bootstrap and calibrated nulls; no pre-registration found | none | **Retainable as method**, not as a scientific contribution |
| Active probing / interventions | **Belal's main constructive result** | Courthoud 2021; de Moraes & De Losso 2026 | Not ours |

Other closest work, VERIFIED unless marked:

| Paper | Relation to us |
|---|---|
| [Xu et al. 2026, arXiv 2607.26385](https://arxiv.org/abs/2607.26385) | Price-level audits blind, via coupled noise in auctions. Different mechanism. |
| [Hespanhol & Aswani 2020, arXiv 2003.09967](https://arxiv.org/abs/2003.09967) | Equilibrium-consistency test with observed shocks, linear demand, no error rates. |
| [Wang, Zhang & Hartline 2025, arXiv 2501.09740](https://arxiv.org/abs/2501.09740) | Regret audit; cost claims can defeat it. |
| [Kim, Kim & Hong 2025, arXiv 2501.05022](https://arxiv.org/abs/2501.05022) | Instrument-based conduct test (Rivers-Vuong); not algorithmic pricing. |
| [Courthoud 2021](https://matteocourthoud.github.io/files/Algorithmic_Collusion_Detection.pdf) | Retraining test; needs access to the algorithms. |
| [Eschenbaum & Meylahn 2026, arXiv 2608.07098](https://arxiv.org/abs/2608.07098) | Audits frozen strategy graphs, not outcomes. |
| [de Moraes & De Losso 2026, arXiv 2610.21867](https://arxiv.org/html/2610.21867) | Drop-and-return after a forced cut is not evidence of punishment. |
| [Bresnahan 1982](https://ideas.repec.org/a/eee/ecolet/v10y1982i1-2p87-92.html) | Conduct identified by demand rotations, not parallel shifts. VERIFIED from a reprint. |
| [Lau 1982](https://ideas.repec.org/a/eee/ecolet/v10y1982i1-2p93-99.html) | General identification conditions. **Bibliographic record only; full text not read.** |

## 5. Verdict on novelty and publication

**Candidly: the identification-plus-negative-benchmark paper is too close to Belal (2026) to submit as novel.**
- Belal covers our core proposition, our implied-cost test, our two strongest negative findings (slow optimisers flagged; high-cost competitors convicted) and the parallelism point.
- Belal does so in the same environment, with more realistic agents (Q-learning, bandits) and an additional constructive tool (active probing).
- What remains distinct is small:
  - an auditor demand-information ladder (market size or outside share; ±20% misspecified μ);
  - a cost-level vs asymmetry decomposition;
  - an explicit market-size-only null;
  - a pre-registered, independent replication in a separate codebase.

### Revised novelty statement (the most we can defend)
> We independently replicate, with scripted agents and pre-registered decision rules, the finding that passive implied-cost and price-level screens for algorithmic collusion test consistency with constant-cost, precisely optimising static competition rather than conduct (Belal 2026). We add a characterisation of the demand information such a screen needs: market size or the outside share when market size varies, and the demand parameter only to within ±20%. We also show that variation in market size alone provides no identifying power under logit demand.

### Options

| Option | Contribution | Effort | Fit |
|---|---|---|---|
| **A. Short replication-and-extension note** | The statement above, framed explicitly around Belal 2026 | 1-2 weeks of writing, no new experiments | Workshop or short-paper venue; replication-friendly outlets |
| **B. Pivot to a question Belal leaves open** | A test that is robust to *partial adjustment* (or unknown μ). It would jointly estimate cost, adjustment speed and μ from share variation, and ask whether slow competitors can then be told apart from cartels. | 1-2 weeks of CPU work plus writing; uncertain | If it works: a genuine constructive contribution. **Kill criterion, fixed now:** stop if, after estimating adjustment speed, AUC(slow cartel vs slow competitors) < 0.90 or FPR at a frozen threshold > 0.10 |
| **C. Stop or park** | none | none | If neither A nor B suits the team's goals |

**Recommendation:** A as the safe minimum. B only if the supervisor wants a stronger paper and accepts that it may fail. Either way, cite Belal prominently, and email the author: it is courteous, and it checks that the work is not already being extended.

### Revised abstract (Option A)
> Regulators screening for algorithmic collusion usually see prices and quantities but not marginal costs. In a logit duopoly with hidden, possibly asymmetric costs, we replicate in a pre-registered simulation (17,000+ runs) the result that passive outcome screens test consistency with a particular competitive model, not conduct. A price-level screen calibrated on symmetric costs flags 57% of competitive firms once costs are hidden. An implied-cost stability screen separates fixed-markup cartels perfectly under share-moving demand shocks, but flags all slowly adjusting competitors at a frozen threshold. A cartel that prices as competition at higher costs is indistinguishable from it. We add the demand information such screens need: shocks to market size alone carry no identifying variation; market size or the outside share must be observed when market size varies; and the screen tolerates a ±20% error in the demand parameter. Outcome screens are therefore best read as tests of a stated competitive benchmark, with error rates that depend on unobserved adjustment dynamics.

## 6. Remaining gaps
1. Read Belal's **full paper** once the PDF is available. The repository write-ups may differ from the final text.
2. Verify the correct SSRN ID and the title; check for a newer version.
3. Read Lau (1982) in full; add one verified citation for logit-Bertrand equilibrium uniqueness only if the paper still mentions uniqueness.
4. Run a slow **rigid** cartel against slow competitors (only the tracking cartel was run slow).
5. The auditor ladder assumes known attractiveness levels: D uses the shares themselves, but the paper must state this assumption.
6. Option B is unrun; its kill criterion is fixed above.
