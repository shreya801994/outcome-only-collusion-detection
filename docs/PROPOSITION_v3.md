# Formal results, version 3 (supersedes v2 for the paper; `PROPOSITION.md` and `PROPOSITION_v2.md` are kept unchanged)

**Scope.** These results support the empirical benchmark. They are not a new theory of collusion identification:
- The pointwise rationalisation (Proposition 1) is also stated by Belal (2026).
- The constant-cost restriction is classic conduct-identification logic (Bresnahan 1982).

**Checks.** Numerical checks are in `experiments/audit_propositions.py` (output `results_v2/audit_propositions_output.txt`) and `results_v2/review2_padding_identity.json`.

## Environment (assumptions used throughout)
- **(E1) Demand.** Two single-product firms face logit demand with an outside good:

  sᵢ(p; a) = exp((aᵢ − pᵢ)/μ) / [exp(a₀/μ) + Σⱼ exp((aⱼ − pⱼ)/μ)],

  with μ > 0 and attractiveness a = (a₀, a₁, a₂) ∈ ℝ³. Shares are always interior: 0 < sᵢ < 1, s₀ > 0.
- **(E2) Payoff.** Stage profit is πᵢ = (pᵢ − cᵢ)·Q·sᵢ, with Q > 0, constant marginal cost cᵢ, no capacity constraints, no fixed costs, and prices unrestricted on ℝ. The simulator clips prices to [0.5, 4]; no reported equilibrium price lies outside that interval.
- **(E3) Auditor.** The auditor observes prices and inside shares sᵢₜ (directly, or as qᵢₜ/Qₜ with Qₜ observed). It knows μ, but not cᵢ and not a. It has an admissible cost set 𝒞 ⊆ ℝ.
- **(E4) Repeated game,** used only in Proposition 1(ii). A fixed stage game is repeated infinitely with discount factor δ ∈ [0, 1).

## Lemma 1 (best response: existence, uniqueness, global optimality)
For any rival price pⱼ, profit has exactly one maximiser over p ∈ ℝ. It lies in (cᵢ, ∞) and is the unique solution of p − cᵢ = μ/(1 − sᵢ(p, pⱼ)).

*Proof.*
1. For p ≤ cᵢ, profit is ≤ 0; for p > cᵢ, profit is > 0.
2. On (cᵢ, ∞), let g(p) = log πᵢ, with g′(p) = f(p) := 1/(p − cᵢ) − (1 − sᵢ)/μ.
3. Using ∂sᵢ/∂pᵢ = −sᵢ(1 − sᵢ)/μ, f′(p) = −1/(p − cᵢ)² − sᵢ(1 − sᵢ)/μ² < 0.
4. f(p) → +∞ as p → cᵢ⁺, and f(p) → −1/μ < 0 as p → ∞.
5. So f has exactly one root p*. g increases before it and decreases after it, so p* is the unique global maximiser. ∎

(Numerically: f′ < 0 on dense grids, with exactly one sign change.) This is uniqueness of the **best response**, not uniqueness of the duopoly's Nash equilibrium, which is neither claimed nor needed.

## Lemma 2 (joint-profit maximum: existence, uniqueness, equal markups)
Under (E1)-(E2), joint profit Q·Σᵢ(pᵢ − cᵢ)sᵢ has a unique global maximiser over ℝ². At the maximiser both markups equal μ/s₀.

*Proof.*
1. **Change of variables.** Let bᵢ = aᵢ − cᵢ, e₀ = exp(a₀/μ), and xᵢ = exp((aᵢ − pᵢ)/μ) ∈ (0, ∞). This is a bijection with pᵢ ∈ ℝ. Then pᵢ − cᵢ = bᵢ − μ·ln xᵢ, and with X = x₁ + x₂, joint profit divided by Q is

   Π = N(x)/(e₀ + X),  where N(x) = Σᵢ (bᵢ − μ·ln xᵢ)·xᵢ.
2. **Inner problem.** For fixed X > 0, maximise N over {xᵢ > 0, Σ xᵢ = X}. Each term bᵢxᵢ − μxᵢ ln xᵢ is strictly concave in xᵢ > 0, so N is strictly concave on this convex set.
   - Stationarity, bᵢ − μ ln xᵢ − μ = λ for all i, gives xᵢ = X·wᵢ with wᵢ = e^(bᵢ/μ)/B and B = Σₖ e^(bₖ/μ).
   - This interior point is therefore the unique maximiser. There bᵢ − μ ln xᵢ = μ ln(B/X) for both i, so the markups are equal. The maximal value is N* = μX·ln(B/X).
3. **Outer problem.** Maximise h(X) = μX·ln(B/X)/(e₀ + X) over X > 0.
   - h′(X) has the sign of r(X) = e₀·ln(B/X) − e₀ − X. Here r′(X) = −e₀/X − 1 < 0, r(X) → +∞ as X → 0⁺, and r(X) → −∞ as X → ∞.
   - So r has a unique root X*, and h is maximised uniquely there.
4. **Markup at the optimum.** ln(B/X*) = 1 + X*/e₀, so the common markup is m = μ(1 + X*/e₀) = μ(e₀ + X*)/e₀ = μ/s₀. ∎

*Numerical check:* the first-order identity holds to 5e-10 at 1,000 random points. On five (a, c) configurations, including asymmetric costs and attractiveness, a dense price grid never exceeds the closed-form optimum.

*Caveat:* this is believed to be a standard result for logit multiproduct pricing, but a verified citation has not been located. Either keep the proof or cite a source after checking it.

## Proposition 1 (pointwise competitive rationalisation)
Take any observed prices p = (p₁, p₂) ∈ ℝ² with interior shares (s₁, s₂, s₀). Define

ĉᵢ := pᵢ − μ/(1 − sᵢ),  âᵢ := pᵢ + μ·ln(sᵢ/s₀) + a₀ (for any a₀ ∈ ℝ).

Then:
1. The logit model with (â₁, â₂, a₀, μ) reproduces the observed shares at p.
2. ĉᵢ < pᵢ.
3. If ĉ ∈ 𝒞², then p is a static Nash equilibrium of the stage game with demand (â, a₀, μ) and costs ĉ.
4. Under (E4), playing p after every history is a subgame-perfect equilibrium of that repeated game, for every δ ∈ [0, 1).

*Proof.*
1. (1) follows from the logit inversion sᵢ/s₀ = exp((âᵢ − pᵢ − a₀)/μ). (2) holds because μ/(1 − sᵢ) > 0.
2. (3): each pᵢ satisfies the first-order condition at ĉᵢ, so by Lemma 1 it is the unique best response to pⱼ.
3. (4): a stage-game Nash equilibrium played after every history is subgame perfect. ∎

*Scope.*
- This is **rationalisability of a single outcome** by suitably chosen (ĉ, â). It does not show that the actual firms have those costs, and it is not evidence of competitive conduct.
- It is **pointwise.** Applied to a non-stationary path {pₜ, sₜ}, it yields period-specific (ĉₜ, âₜ). It does **not** show that one fixed cost vector rationalises an arbitrary path; Proposition 2 is about exactly that restriction.
- (4) concerns a stationary repeated game with fixed demand. It is not a statement about our simulations, where demand changes every period.

## Proposition 2 (implications of three pricing rules for the implied cost)
Let costs be constant and demand vary over t, so shares vary, under (E1)-(E3). Write ĉᵢₜ = pᵢₜ − μ/(1 − sᵢₜ).

- **(a) Contemporaneous static Nash.** If pₜ is the static Nash equilibrium of period t's stage game, then ĉᵢₜ = cᵢ for all t (Lemma 1).
- **(b) Joint-profit maximisation.** If pₜ is the joint-profit maximiser of period t (Lemma 2), then pᵢₜ − cᵢ = μ/s₀ₜ and

  ĉᵢₜ = cᵢ + μ·sⱼₜ / (s₀ₜ(1 − sᵢₜ)).

  ĉᵢₜ is constant over t if and only if sⱼₜ/(s₀ₜ(1 − sᵢₜ)) is constant along the realised share path.
- **(c) Fixed prices.** If pᵢₜ = p̄ᵢ, then ĉᵢₜ = p̄ᵢ − μ/(1 − sᵢₜ). It is constant if and only if sᵢₜ is constant.

*Proof.* Substitute each rule's price into the definition of ĉ. ∎

*Scope.*
- (a) is a **necessary implication of contemporaneous static Nash at constant cost**. It is not an implication of competition in general.
- Our simulated competitors best-respond to the rival's previous price and adjust partially (`SIMULATION_POLICIES.md`; `simulator/batch_sim.py`, lines 119-121 and 135-139). They do not satisfy (a): ĉᵢₜ moves without collusion.
- (b) covers the pure joint-profit rule only. The tracking cartel's blend pᴺ + κ(pᴹ − pᴺ), with κ < 1, is not covered.
- Whether the E2/E3 shock processes move the ratio in (b) or the share in (c) by enough is an empirical matter, shown only through the screen results. A descriptive plot of these quantities has not been made.

## Proposition 3 (pathwise observational equivalence of a cost-mimicking high-price policy)
**Policy class.** Firm i's price at t is pᵢₜ = Φᵢ(pₜ₋₁, aₜ; θᵢ, ωᵢₜ), with initial price pᵢ₀ = Ψᵢ(a₀; θ), where:
- θᵢ is a cost parameter *supplied to the rule*;
- ωᵢₜ is exogenous randomness: adjustment speed, noise, price cuts.

**Condition (S), state.** Φ and Ψ take no other inputs. In particular there are no realised profits, rewards, accumulated payoffs, learning states, or anything else computed from the firm's **true** cost.

**Condition (C), coupling.** The demand paths (aₜ, Qₜ) and the randomness ωᵢₜ are the same in the two systems compared.

**Claim.** Let system M ("cost-mimicking") have true costs c and use θ = c + m, with m ∈ ℝ²₊₊. Let system K ("competitive twin") have true costs c + m and use θ = c + m. If (S) and (C) hold, then (pₜ, qₜ, Qₜ) is identical in M and K for every t. If additionally c + m ∈ 𝒞², then no function of the observables distinguishes M from K.

*Proof, by induction on t.*
1. **Base case.** p₀ᴹ = Ψ(a₀; c + m) = p₀ᴷ.
2. **Inductive step.** If pₜ₋₁ᴹ = pₜ₋₁ᴷ, then by (S) and (C) the inputs to Φ coincide, so pₜᴹ = pₜᴷ.
3. Quantities are qᵢₜ = Qₜ·sᵢ(pₜ; aₜ), which are identical by (C).
4. Every observable is a function of (pₜ, qₜ, Qₜ). ∎

**Corollary (detectors).**
- Under (S) with independent but identically distributed demand and randomness, the two observable processes have the same law. Every detector T has the same score distribution under M and K, and its population AUC is 1/2.
- Under (S) and (C), paired scores are identical, and the empirical AUC on the pooled sample is exactly 0.5.

**When (S) fails.** Suppose a policy updates on realised profit computed with the true cost, πᵢₜ = (pᵢₜ − cᵢ)qᵢₜ, for example Q-learning rewards.
- System M's agent receives (pᵢₜ − cᵢ)qᵢₜ, while K's receives (pᵢₜ − cᵢ − mᵢ)qᵢₜ. Their subsequent prices can differ, and the proposition does **not** apply.
- It applies again only if M's agent computes its reward signal with the padded cost c + m. The proposition therefore says nothing about learning agents unless that is specified.

**Code support (VERIFIED) that our simulator satisfies (S) and (C):**
- `simulator/batch_sim.py`, lines 87-94: the true costs are replaced by c + m before any use. m is drawn **last** from the parameter stream, so the adjustment speeds drawn before it coincide with the twin's.
- Lines 109-110: initial price = Nash at a₀ for the supplied costs.
- Lines 119-121: target = BR(θᵢ; aₜ, rival's previous price).
- Lines 135-139: partial-adjustment update with exogenous noise and price cuts.
- Lines 142-144: quantities from prices and demand only.
- No profit or reward is computed anywhere in the pricing loop. The only profit function, `joint_profit`, is called only to set cartel targets (line 70).
- Lines 147-151: the punishment state applies to rigid and tracking cartels only.
- Numerically: identical adjustment speeds and maximum paired differences of 0.0 in prices, quantities and market size (270 runs × 300 periods).

**What it does not show.** That system M is a collusive equilibrium. No coordination mechanism, incentive constraint, deviation payoff, punishment or recovery is modelled. Each firm's static best response at its true cost is lower, so absent a punishment threat each firm would deviate. **Name:** "cost-mimicking high-price policy", not "cartel".

## Identification versus classification (how each result must be described)

| Category | Meaning | Our results in this category | Must not be described as |
|---|---|---|---|
| **Exact observational equivalence** | Identical observable law; no detector beats chance at any sample size | Proposition 1 (single stationary outcome, pointwise). Proposition 3 (pathwise, under S and C); empirical twin AUC = 0.500 | none |
| **Imperfect finite-sample discrimination** | Different laws, overlapping score distributions in finite T and n | D: AUC 0.854 (slow rigid vs slow competitors), 0.822 (slow tracking), about 0.61 in E0 | non-identification (it might improve with longer T or more information) |
| **Threshold calibration failure** | A threshold calibrated on one population is applied to another | D: FPR 1.000 for slow competitors (H1a, S2). B0: FPR 0.57 with the naive threshold. D: FPR 0.22 at μ̂ = +20% | non-identification, or a property of D's ranking |
| **Distribution shift from a latent parameter** | The competitive score distribution depends on unobserved adjustment speed λ | Slow vs fast competitors: AUC(D) 1.000 (S3) | proof that λ cannot be estimated. λ is latent but may be estimable from trajectories; this is untested (Option B, UNRUN) |

## References
- **Bresnahan (1982),** *Economics Letters* 10: 87-92. VERIFIED (reprint).
- **Lau (1982),** *Economics Letters* 10: 93-99. Full text unread. Matsumura & Otani (arXiv 2410.16998; a revised 2026 version is reported by the reviewer, unverified by me) argue that Lau's characterisation is incorrect. Both concern homogeneous-goods conduct parameters, and **neither implies our logit results**.
- **Mizuno (2003):** not cited.
- **Belal (2026),** SSRN 7266558 / 7267038 (same title; the version is unresolved). The abstract was supplied by the team; the full text is unread.
