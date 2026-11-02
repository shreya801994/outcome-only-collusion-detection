"""Numerical and symbolic checks for docs/PROPOSITION_v3.md (no simulation of any design).

1. Finite-difference check of the joint-profit first-order condition (1000 random points).
2. Global-maximum check: joint profit at the closed-form common-markup prices vs a dense grid,
   for several (a, c) configurations including asymmetric ones.
3. Lemma 1: f'(p) < 0 on a grid; sign of f at the boundaries.
4. Proposition 3 coupling: the cost-padding parameter is drawn after every other per-run draw,
   so the competitive twin consumes identical random streams (checked on 50 runs, E2).

    python -m experiments.audit_propositions
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from simulator.batch_sim import AgentParams, simulate_batch  # noqa: E402
from simulator.demand_shocks import ENVIRONMENTS, simulate_shocks  # noqa: E402
from simulator.equilibrium import joint_profit, shares  # noqa: E402

# 1. FOC identity, checked by central finite differences at random points
def joint(p_1, p_2, c_1, c_2, a_1, a_2, mu_=0.25):
    s_1, s_2, _ = shares(p_1, p_2, a_1, a_2, 0.0, mu_)
    return (p_1 - c_1) * s_1 + (p_2 - c_2) * s_2


rng0 = np.random.default_rng(1)
errs = []
for _ in range(1000):
    P1_, P2_, C1_, C2_ = rng0.uniform(0.5, 3, 4)
    A1_, A2_ = rng0.uniform(1.5, 2.5, 2)
    h = 1e-6
    num = (joint(P1_ + h, P2_, C1_, C2_, A1_, A2_) - joint(P1_ - h, P2_, C1_, C2_, A1_, A2_)) / (2 * h)
    s_1, s_2, _ = shares(P1_, P2_, A1_, A2_)
    m1_, m2_ = P1_ - C1_, P2_ - C2_
    claim = s_1 * (1 - (m1_ - (m1_ * s_1 + m2_ * s_2)) / 0.25)
    errs.append(abs(num - claim))
print("1) max |finite-difference dPi/dp1 - s1[1-(m1-sum m s)/mu]| over 1000 random points:", f"{max(errs):.1e}")

# 2. global maximum vs grid
rng = np.random.default_rng(0)
worst = -np.inf
for a_1, a_2, c_1, c_2 in [(2, 2, 1, 1), (2, 2, 0.85, 1.45), (2.3, 1.8, 1, 1.2), (1.7, 2.4, 0.7, 1.1), (2, 2, 1.5, 1.5)]:
    m1, m2 = joint_profit(c_1, c_2, a_1, a_2)
    S1, S2, _ = shares(m1, m2, a_1, a_2)
    best_closed = (m1 - c_1) * S1 + (m2 - c_2) * S2
    g = np.linspace(0, 5, 1201)
    P1, P2 = np.meshgrid(g, g)
    G1, G2, _ = shares(P1, P2, a_1, a_2)
    grid = (P1 - c_1) * G1 + (P2 - c_2) * G2
    gap = grid.max() - best_closed
    worst = max(worst, gap)
    print(f"2) a=({a_1},{a_2}) c=({c_1},{c_2}): closed-form prices ({float(m1):.4f},{float(m2):.4f}), "
          f"markups equal: {abs((m1-c_1)-(m2-c_2))<1e-12}, grid max - closed-form = {gap:.2e}")
print("   worst grid excess over closed form (should be <= 0):", f"{worst:.2e}")

# 3. Lemma 1 on a grid
for c, rival in [(1.0, 1.5), (0.3, 2.5), (1.6, 1.0)]:
    p = np.linspace(c + 1e-6, c + 20, 200001)
    s, _, _ = shares(p, rival)
    f = 1 / (p - c) - (1 - s) / 0.25
    fprime = -1 / (p - c) ** 2 - s * (1 - s) / 0.25 ** 2
    print(f"3) c={c}, rival={rival}: max f' = {fprime.max():.3e} (<0), f at p=c+1e-6: {f[0]:.1e}, f at p=c+20: {f[-1]:.4f}, "
          f"sign changes: {int(np.sum(np.diff(np.sign(f)) != 0))}")

# 4. coupling of random streams
n = 50
costs = np.column_stack([np.full(n, 0.9), np.full(n, 1.2)])
k = np.random.SeedSequence(99).spawn(4)
a, q = simulate_shocks(np.random.default_rng(k[0]), n, 300, ENVIRONMENTS["E2"])
k = np.random.SeedSequence(99).spawn(4)
cart = simulate_batch(costs, a, q, "collusive_cost_padding", AgentParams(), *(np.random.default_rng(x) for x in k[1:]))
k = np.random.SeedSequence(99).spawn(4)
twin = simulate_batch(costs + cart["cost_pad"][:, None], a, q, "competitive", AgentParams(),
                      *(np.random.default_rng(x) for x in k[1:]))
print("4) adjustment speeds identical:", bool(np.array_equal(cart["adjust_speed"], twin["adjust_speed"])),
      "| max |price diff|:", float(np.abs(cart["price"] - twin["price"]).max()))
