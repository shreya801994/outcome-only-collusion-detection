# Auditor information specification (corrected, 2 Nov 2026)

This supersedes the L1/L2/L3 wording in `docs/V2_DESIGN.md`, `docs/V2_RESULTS.md` and the deck (slide 5). The code and results are unchanged. Evidence: `experiments/audit_information_boundary.py`, output in `results_v2/audit_information_boundary_output.txt`. All VERIFIED.

## What each detector actually receives

| Detector | Inputs actually used (code) | Demand parameters used | Uses hidden fields? |
|---|---|---|---|
| B0 price level | `price` only (`score_runs` builds a frame of period and the two prices) | none | no |
| B1 synchronisation | `price` only | none | no |
| B2 lead-lag | `price` only | none | no |
| B3 deviation response | `price` only (event size 0.10 is a detector constant) | none | no |
| D_L2 | `price`, `quantity`; shares computed as **q / 1**, i.e. market size *assumed* equal to its baseline value 1 | μ (true value 0.25) | no |
| D_L3 | `price`, `quantity`, `market_size`; shares computed as **q / Q** | μ (0.25) | no |
| D_L3_mu020 / mu030 | as D_L3 | μ misspecified as 0.20 / 0.30 | no |

No detector receives costs, attractiveness (a₀, a₁, a₂, or the shock paths), conduct labels, agent parameters, seeds or run identifiers.

## What D needs, precisely

Formula: ĉᵢₜ = pᵢₜ − μ / (1 − sᵢₜ), with sᵢₜ the firm's **inside share of total market size**, outside good included.

| Item | Needed? | Note |
|---|---|---|
| Prices | yes | |
| Shares sᵢₜ | yes | Either observed directly, or as quantities plus total market size: sᵢₜ = qᵢₜ / Qₜ. Equivalently, quantities plus the outside share s₀ₜ: Qₜ = (q₁ₜ + q₂ₜ) / (1 − s₀ₜ), verified to 2e-7. |
| μ | yes | D's power under share shocks was unchanged with μ misspecified by ±20% (E2/E3). |
| Attractiveness a₀, a₁, a₂ and their shock paths | **no** | With shares observed, D does not use them. D from observed shares q/Q equals D from the model shares s(p; aₜ) to within float32 storage error (≤ 1.2e-6). The auditor never needs to know or estimate attractiveness. |
| Costs | no | They are what D tests against |

**Correction to `docs/FINAL_AUDIT.md` §6, item 5.** That item said the ladder "assumes known attractiveness levels". This was wrong: D uses shares, not attractiveness. The correct statement is that D assumes μ is known and shares are observed (or computable from quantities and Q).

## Corrected information levels

| Level | Auditor observes | Screens | Valid when |
|---|---|---|---|
| L1 | prices | B0-B3 | always (but see their confounds) |
| L2 | prices and quantities; **total market size not observed**, assumed at its baseline value (Q = 1) | D_L2 | Only if market size really is constant at the assumed value. In E0 and E2 (Q ≡ 1), D_L2 = D_L3 exactly. In E1 and E3 (Q varies) the computed "shares" are wrong; D_L2 differs from D_L3 by up to 3.2 and loses power (E3 AUC 0.81 vs 1.00). |
| L3 | prices, quantities and total market size (or, equivalently, the outside share) | D_L3 | when μ is known (roughly) |

**Wording to use in the paper.** "L2 assumes the total market size is known and constant; L3 observes it each period." Do not write "L2 assumes market size is constant". Even a constant but unknown Q ≠ 1 mis-scales every share, so the implied costs vary with shares under competition too.

## Scope of the equivalence result with respect to demand knowledge
For Proposition 1, the auditor need not know attractiveness either. Under logit, any interior prices and shares are matched by the attractiveness values aᵢₜ = pᵢₜ + μ·log(sᵢₜ / s₀ₜ) + a₀. So the competitive rationalisation at ĉ needs only μ, which pins the markup μ/(1 − s). This is a derivation and should be stated in `PROPOSITION.md` (see the theory audit).
