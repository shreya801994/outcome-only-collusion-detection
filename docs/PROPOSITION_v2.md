# Formal results, version 2 (corrected; supersedes `docs/PROPOSITION.md`, which is kept unchanged)

All eight corrections listed in `docs/GAP_CLOSING_REPORT.md` §4 are implemented here. These results are applications of known conduct-identification logic (Bresnahan 1982; for Lau 1982 see the caveat in §R). They are **not** claimed as new theory: Belal (2026) states the pointwise rationalisation (Proposition 1) for the same logit environment.

## Setting and information
- **(A1) Demand.** Two single-product firms face logit demand with an outside good:

  sᵢ(p; a) = exp((aᵢ − pᵢ)/μ) / [exp(a₀/μ) + Σⱼ exp((aⱼ − pⱼ)/μ)],  μ > 0.

  Shares are interior: 0 < sᵢ < 1 and s₀ = 1 − s₁ − s₂ > 0.
- **(A2) Profit.** πᵢ = (pᵢ − cᵢ)·Q·sᵢ, with constant marginal cost cᵢ, no fixed or capacity costs, and prices unrestricted on ℝ.
- **(A3) Auditor information.** The auditor observes prices pᵢₜ and inside shares sᵢₜ, either directly or as qᵢₜ/Qₜ with Qₜ observed. It knows μ. It does **not** need a₀, a₁, a₂ or their paths. It never observes cᵢ. (See `docs/AUDITOR_INFORMATION_SPEC.md`.)
- **(A4) Admissible costs.** The auditor's admissible cost set is 𝒞 ⊆ ℝ, for example 𝒞 = [0, ∞).

## Lemma 1 (existence and uniqueness of the best response)
Under (A1)-(A2), for any rival price pⱼ, firm i's profit has exactly one maximiser over p ∈ ℝ. It lies in (cᵢ, ∞) and is the unique solution of p − cᵢ = μ / (1 − sᵢ(p, pⱼ)).

*Proof.*
1. If p ≤ cᵢ then πᵢ ≤ 0, while every p > cᵢ gives πᵢ > 0. So any maximiser lies in (cᵢ, ∞).
2. On (cᵢ, ∞), let g(p) = log πᵢ = log(p − cᵢ) + log sᵢ + log Q.
3. Using ∂sᵢ/∂pᵢ = −sᵢ(1 − sᵢ)/μ, g′(p) = f(p) := 1/(p − cᵢ) − (1 − sᵢ)/μ.
4. f is continuous and strictly decreasing on (cᵢ, ∞): 1/(p − cᵢ) is strictly decreasing, and −(1 − sᵢ)/μ is strictly decreasing because sᵢ falls in pᵢ.
5. f(p) → +∞ as p → cᵢ⁺. As p → ∞, sᵢ → 0, so f(p) → −1/μ < 0.
6. Hence f has exactly one root p*. g increases on (cᵢ, p*) and decreases on (p*, ∞), so p* is the unique global maximiser of g, and therefore of πᵢ. ∎

## Proposition 1 (pointwise competitive rationalisation)
Under (A1)-(A3), take any observed prices (p₁, p₂) with interior shares (s₁, s₂, s₀), and let

ĉᵢ := pᵢ − μ/(1 − sᵢ).

Then ĉᵢ < pᵢ. Moreover, define the attractiveness values âᵢ := pᵢ + μ·log(sᵢ/s₀) + a₀, for any a₀. The logit model with (â, a₀, μ) reproduces the observed shares exactly at prices p. If ĉᵢ ∈ 𝒞 for i = 1, 2, then:
1. p is a static Nash equilibrium of the game with demand (â, a₀, μ) and costs (ĉ₁, ĉ₂);
2. playing p every period is a subgame-perfect equilibrium of the repeated game, for any discount factor.

*Proof.*
1. ĉᵢ < pᵢ because μ/(1 − sᵢ) > 0.
2. The logit inversion gives sᵢ(p; â)/s₀(p; â) = exp((âᵢ − pᵢ − a₀)/μ) = sᵢ/s₀, so the model with â reproduces the observed shares.
3. By Lemma 1, pᵢ is the unique best response to pⱼ at cost ĉᵢ, because it solves the first-order condition. So p is a Nash equilibrium.
4. A static Nash equilibrium played in every period is subgame perfect.

Uniqueness of the equilibrium is **not** claimed and not needed. ∎

*Example (VERIFIED, `audit/stage_a/a02_market_checks.py`).* p = (1.9, 1.9) with true cost 1.0 and a = 2 has s = 0.3745 and ĉ = 1.5003. At cost 1.5003 the best response to 1.9 is 1.9000.

*What it does not show.* It does not show that outcome-only detection is impossible. It shows that a single stationary outcome cannot separate conduct unless 𝒞 excludes ĉ. It says nothing about non-stationary paths (Propositions 2-3).

## Proposition 2 (constant implied cost under share variation)
Let shares vary over t through attractiveness shocks while costs stay constant, under (A1)-(A3).

- **(a) Contemporaneous static Nash.** If pₜ is the static Nash price vector of period t's demand, then ĉᵢₜ = cᵢ for all t.
  - This is *not* satisfied by our simulated competitors. They target a best response to the rival's **previous** price and adjust partially (`docs/SIMULATION_POLICIES.md`), so ĉᵢₜ ≠ cᵢ in general even without noise.
  - The observed consequences: fast competitors have D ≈ 0.033 > 0; slow competitors are flagged (addenda 2-3).
- **(b) Joint-profit maximisation.** If pₜ maximises joint profit each period, then pᵢₜ − cᵢ = μ/s₀ₜ for both firms, and

  ĉᵢₜ = cᵢ + μ·sⱼₜ / (s₀ₜ·(1 − sᵢₜ)).

  ĉᵢₜ is constant only along share paths on which sⱼₜ/(s₀ₜ(1 − sᵢₜ)) is constant. In particular it is not constant under generic shocks that move shares.

  *Derivation.* With mₖ = pₖ − cₖ, the first-order condition for pᵢ of Σₖ mₖsₖ, using ∂sᵢ/∂pᵢ = −sᵢ(1 − sᵢ)/μ and ∂sₖ/∂pᵢ = sₖsᵢ/μ (k ≠ i), is

  sᵢ·[1 − (mᵢ − Σₖ mₖsₖ)/μ] = 0, hence mᵢ − Σₖ mₖsₖ = μ for each i.

  The right-hand side is common, so m₁ = m₂ = m, and m(1 − s₁ − s₂) = μ gives m = μ/s₀. Substituting into ĉ = p − μ/(1 − s) gives the expression above.

  Scope: our tracking cartel uses the blend pᴺ + κ(pᴹ − pᴺ) with κ ∈ [0.5, 1], to which (b) applies only at κ = 1. Its implied cost was not derived in closed form; its behaviour is reported empirically.
- **(c) Fixed prices.** If pᵢₜ = p̄ᵢ, then ĉᵢₜ = p̄ᵢ − μ/(1 − sᵢₜ), which varies whenever sᵢₜ varies.

*Proof.* Substitute each conduct's price into ĉ = p − μ/(1 − s): (a) by Lemma 1; (b) by the derivation; (c) directly. ∎

**Scope.** A constant implied cost is a testable restriction of *contemporaneous static Nash at constant cost*. It is not a restriction of competition in general. Partial adjustment, learning, or responses to lagged rival prices violate it without any collusion.

## Proposition 3 (on-path observational equivalence of cost-mimicking prices)
Fix m₁, m₂ > 0. Consider a price policy that, in every period and demand state, sets each firm's price by the competitive rule (for example, `competitive` in `SIMULATION_POLICIES.md`) evaluated at costs cᵢ + mᵢ instead of cᵢ.

Then, for every realisation of the demand path and noise, its observable outcome path (prices, quantities, market size) is identical to that of competitive firms with true costs cᵢ + mᵢ following the same rule. Hence the two are indistinguishable by any function of the observables, unless 𝒞 excludes cᵢ + mᵢ.

*Proof.* The observables are deterministic functions of (prices, demand), and prices are generated by the same rule from the same inputs. ∎

*Numerical check (VERIFIED, `results_v2/review2_padding_identity.json`).* 270 runs × 300 periods under shared random streams give a maximum absolute paired difference of **0.0** for prices, quantities and market size. Against this matched twin, every screen's AUC is exactly 0.500 (`results_v2/audit_h2_output.txt`).

*What it does not show.* It concerns on-path outcomes only.
- It does **not** show that the policy is a sustainable collusive equilibrium: no incentive constraint, deviation payoff, punishment or recovery is modelled. Each firm's static best response at its true cost is lower, so absent a punishment threat each firm would gain by deviating.
- Call it a "cost-mimicking high-price policy", not a "cartel equilibrium".

## Remarks
- **R1 (What screen D tests).** D tests consistency with contemporaneous, fully adjusting static competition at constant cost (Proposition 2a). It responds at least as strongly to adjustment dynamics as to conduct (addendum 3: dynamics contrast AUC 1.000 vs conduct contrast 0.854).
- **R2 (Information).**
  - D needs observed shares and μ, and does not need attractiveness (Proposition 1, (A3)).
  - With μ misspecified, ĉᵢₜ − cᵢ = −(μ̂ − μ)/(1 − sᵢₜ) under static Nash, which varies with shares.
  - Empirically (exploratory, `results_v2/review2_mu_misspecification.csv`): with the threshold calibrated at the true μ, D's FPR under share shocks (E2) rises from 0.05 (μ̂ = μ) to 0.10, 0.22 and 0.56 at μ̂ = +10%, +20% and +40%; at μ̂ = −40% it is 0.20.
  - Recalibrating the threshold with the same μ̂ on labelled competitive calibration runs restores the FPR to about 0.05, and the AUC stays at about 1.00 throughout.
  - The earlier claim "μ known to ±20% suffices" holds for ranking, not for a frozen threshold.
- **R3 (The AUC of 0.38 in addendum 2, H2).** It compares the cost-mimicking policy with competitors at the *true* costs (mean cost 1.351 vs 1.000), so it reflects a cost-level difference. Against the matched twin of Proposition 3 the AUC is 0.500.

## References: status
- **Bresnahan (1982),** *Economics Letters* 10: 87-92. VERIFIED (reprint). Rotations, not parallel shifts, identify conduct when cost is unknown.
- **Lau (1982),** *Economics Letters* 10: 93-99. Full text not read (paywall and CAPTCHA). Its theorem as restated by Matsumura & Otani (2024, arXiv 2410.16998), REPORTED: in homogeneous-goods conduct-parameter models, θ is not identified iff inverse demand is separable in the demand shifters and not of the form P = Q^(−1/θ)·r(Xᵈ) + s(Q). Matsumura & Otani give a separable counterexample that is identified. Cite Lau only for this general idea, with that caveat; it is not a logit-Bertrand result.
- **Mizuno (2003),** *IJIO* 21: 761-793. Not cited. Its exact conditions are unverified, and uniqueness is no longer used.
- **Belal (2026),** SSRN. The abstract was supplied by the team (REPORTED); the full text is unread. There is an ID discrepancy (7266558 vs 7267038), so check the author's own citation.
