# Pricing policies as implemented (from `simulator/batch_sim.py`, `simulator/demand_shocks.py`)

Written out as equations at the reviewer's request. The code is authoritative; this document describes it.

## Market and timing
- **Demand** (logit with an outside good; μ = 0.25, a₀ = 0):

  sᵢₜ = exp((aᵢₜ − pᵢₜ)/μ) / [exp(a₀/μ) + Σⱼ exp((aⱼₜ − pⱼₜ)/μ)],  qᵢₜ = Qₜ·sᵢₜ.

- **Shocks** (`demand_shocks.py`): aᵢₜ = 2 + ζₜ + ξᵢₜ and ln Qₜ = ηₜ.
  - ζ, ξ₁, ξ₂ and η are independent stationary AR(1) processes with ρ = 0.95. Their stationary SDs are 0.25 (ζ), 0.15 (ξ) and 0.20 (η), and each is switched on or off by environment E0-E3.
  - Firms observe (aₜ, Qₜ) before pricing in period t; the auditor never observes aₜ.
- **Timing within period t:**
  1. The shocks are realised.
  2. Each firm computes its target Tᵢₜ from aₜ, its own cost and the rival's **previous** realised price pⱼ,ₜ₋₁.
  3. Prices are set simultaneously.
  4. The outcome (pₜ, qₜ, Qₜ) is recorded.

## Common price-update rule (all conducts)
eᵢₜ = pᵢ,ₜ₋₁ + λᵢ·(Tᵢₜ − pᵢ,ₜ₋₁)  (expected, noise-free price)

pᵢₜ = clip(eᵢₜ + εᵢₜ − Bᵢₜ·δᵢₜ, 0.5, 4)

| Term | Distribution | Default | Slow (addenda 2-3) |
|---|---|---|---|
| λᵢ (adjustment speed, per firm and run) | uniform | U[0.5, 1] | U[0.05, 0.20] |
| εᵢₜ (price noise) | N(0, σ²) | σ = 0.01 | σ = 0.02 |
| Bᵢₜ (exogenous price cut occurs) | Bernoulli(0.01) | same | same |
| δᵢₜ (size of price cut) | U[0.10, 0.25] | same | same |

The noise and price-cut streams are drawn identically for every conduct, and the rule is the same for competitors and cartels; only the target Tᵢₜ differs.

## Targets by conduct
Notation:
- BRᵢ(pⱼ; a, c) is the static best response (closed form via Lambert W).
- pᴺ(a, c) is the static Nash price vector.
- pᴹ(a, c) is the joint-profit price vector (common markup μ/s₀).
- ā = (2, 2) is mean attractiveness.

| Conduct | Target Tᵢₜ (cooperative phase) | Target during punishment | Initial price pᵢ₀ |
|---|---|---|---|
| `competitive` | BRᵢ(pⱼ,ₜ₋₁; aₜ, cᵢ) | not applicable | pᴺᵢ(a₀, c) |
| `competitive_nash` (S5, S6, C2, C3) | pᴺᵢ(aₜ, c) | not applicable | pᴺᵢ(a₀, c) |
| `collusive_rigid` | p̄ᵢ = pᴺᵢ(ā, c) + κ·[pᴹᵢ(ā, c) − pᴺᵢ(ā, c)], **fixed for the run** (does not respond to aₜ) | pᴺᵢ(aₜ, c) | p̄ᵢ |
| `collusive_tracking` | pᴺᵢ(aₜ, c) + κ·[pᴹᵢ(aₜ, c) − pᴺᵢ(aₜ, c)] | pᴺᵢ(aₜ, c) | cooperative target at a₀ |
| `collusive_cost_padding` (H2) | BRᵢ(pⱼ,ₜ₋₁; aₜ, cᵢ + m) | not applicable | pᴺᵢ(a₀, c + m) |

Parameters: κ ~ U[0.5, 1] per run; m ~ U[0.2, 0.5] per run.

## Punishment state (rigid and tracking cartels only)
There is a shared counter kₜ ≥ 0, with k₀ = 0. The cartel is in its punishment phase at t if and only if kₜ > 0.

- If kₜ = 0 and (p₁ₜ < e₁ₜ − τ or p₂ₜ < e₂ₜ − τ), then kₜ₊₁ = K.
- Otherwise kₜ₊₁ = max(kₜ − 1, 0).

Parameters: τ = 0.05 and K ~ U{3, …, 8} per run.

**Consequences for interpretation:**
- A punishment phase is triggered by any exogenous price cut (δ ≥ 0.10 > τ). It is also triggered by noise larger than τ: rarely with σ = 0.01 (5σ), more often with σ = 0.02 (2.5σ).
- In the punishment phase both firms move toward the current Nash price at their own speed λᵢ.
- The cartel never best-responds to the rival's price in its cooperative phase.

## What "matched dynamics" means in addendum 3
Both arms draw λᵢ ~ U[0.05, 0.20] and σ = 0.02, use the same price-cut process, the same 3 × 3 hidden-cost grid and the same E2 shock process, with T = 300 and burn-in 50. They differ **only** in the target rule:
- slow competitors: BRᵢ(pⱼ,ₜ₋₁; aₜ, cᵢ);
- slow rigid cartel: a fixed p̄ᵢ plus punishment.

The two arms use independent seed streams (different spawn keys under base 20261106), so the comparison is not paired.
