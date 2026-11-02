"""Stage A: market-formula checks for earlier findings 1, 2, 6, 7, 8, 9 (read-only).

Uses only the repository's own market and agent code to evaluate formulas
(no trajectories are simulated).  Run from the repository root:
    python audit/stage_a/a02_market_checks.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq, fsolve, minimize

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from simulator.market import BertrandMarket, MarketConfig  # noqa: E402
from simulator.agents import CompetitiveAgent  # noqa: E402
from simulator.reactive_agents import ReactiveCompetitiveAgent  # noqa: E402

cfg = MarketConfig()
mkt = BertrandMarket(cfg)
MU = cfg.mu


def shares(p1, p2, Q=1.0):
    q1, q2 = mkt.demand(p1, p2, Q)
    return q1 / Q, q2 / Q


def implied_costs(p1, p2, s1, s2, mu=MU):
    return p1 - mu / (1 - s1), p2 - mu / (1 - s2)


def foc_residual(p, c):
    s1, s2 = shares(p[0], p[1])
    return [p[0] - c[0] - MU / (1 - s1), p[1] - c[1] - MU / (1 - s2)]


def nash_foc(c, guess=(1.5, 1.5)):
    sol, info, ier, msg = fsolve(foc_residual, guess, args=(c,), xtol=1e-14, full_output=True)
    return sol, ier


def br_repo(firm_id, cost, rival_price, Q=1.0):
    agent = CompetitiveAgent(cost=cost, firm_id=firm_id)
    return agent.best_response(rival_price, mkt, competitor_cost_beliefs=(1.0,), Q=Q)


def profit_own(firm_id, p, rival_p, c, Q=1.0):
    if firm_id == 1:
        return mkt.profits(p, rival_p, c, 0.0, Q)[0]
    return mkt.profits(rival_p, p, 0.0, c, Q)[1]


print("=" * 90)
print("Item 1: MarketConfig defaults")
print(cfg)
s1, s2 = shares(1.5, 1.7)
q1, q2 = mkt.demand(1.5, 1.7, Q=1.0)
print(f"shares at (1.5,1.7): s1={s1:.6f} s2={s2:.6f} outside={1-s1-s2:.6f}  (outside share > 0 => outside good included)")
print(f"manual logit: e1={np.exp((2-1.5)/MU):.6f} e2={np.exp((2-1.7)/MU):.6f} e0={np.exp(0/MU):.6f} "
      f"s1={np.exp((2-1.5)/MU)/(np.exp(0)+np.exp((2-1.5)/MU)+np.exp((2-1.7)/MU)):.6f}")

print("=" * 90)
print("Item 2: implied cost c_hat = p - mu/(1-s) at reference equilibrium prices")
ref = pd.read_csv(ROOT / "evaluation" / "competitive_equilibrium_reference.csv")
rows = []
for _, r in ref.iterrows():
    p1, p2 = r.equilibrium_price_1, r.equilibrium_price_2
    s1, s2 = shares(p1, p2)
    c1h, c2h = implied_costs(p1, p2, s1, s2)
    (n1, n2), ier = nash_foc((r.cost_1, r.cost_2))
    # iterated best response with the repository's own optimizer
    a, b = 1.472927, 1.472927
    for _ in range(200):
        a, b = br_repo(1, r.cost_1, b), br_repo(2, r.cost_2, a)
    rows.append({
        "cost_gap": r.cost_gap, "c1": r.cost_1, "c2": r.cost_2,
        "ref_p1": p1, "ref_p2": p2,
        "c1_hat": c1h, "c2_hat": c2h,
        "err_c1": c1h - r.cost_1, "err_c2": c2h - r.cost_2,
        "foc_nash_p1": n1, "foc_nash_p2": n2,
        "ref_minus_foc_p1": p1 - n1, "ref_minus_foc_p2": p2 - n2,
        "iterBR_p1": a, "iterBR_p2": b,
        "mean_nash_price": (n1 + n2) / 2,
    })
tab = pd.DataFrame(rows)
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 30)
print(tab.to_string(index=False, float_format=lambda x: f"{x:.7g}"))
print(f"max |implied-cost error| = {np.abs(tab[['err_c1','err_c2']].to_numpy()).max():.3e}")
print(f"max |ref - FOC Nash| = {np.abs(tab[['ref_minus_foc_p1','ref_minus_foc_p2']].to_numpy()).max():.3e}")

print("=" * 90)
print("Items 6/7: collusive outcome p=(1.9,1.9)")
p = 1.9
s, _ = shares(p, p)
chat, _ = implied_costs(p, p, s, s)
print(f"share at 1.9 = {s:.6f}; implied cost c_hat = {chat:.6f}")
(n1, n2), ier = nash_foc((chat, chat), guess=(1.8, 1.8))
print(f"FOC Nash at c_hat (symmetric): ({n1:.6f}, {n2:.6f}), solver flag={ier}")
br = br_repo(1, chat, 1.9)
print(f"repo best_response(firm1, cost=c_hat, rival=1.9) = {br:.6f}")
grid = np.linspace(chat + 1e-6, 10.0, 2_000_001)
prof = np.array([profit_own(1, g, 1.9, chat) for g in grid[::100]])
gbest = grid[::100][prof.argmax()]
print(f"grid argmax of firm-1 profit on (c_hat, 10], step {grid[100]-grid[0]:.1e}: {gbest:.5f}; "
      f"profit at 1.9 = {profit_own(1, 1.9, 1.9, chat):.8f}, max on grid = {prof.max():.8f}")
h = 1e-4
d2 = (profit_own(1, 1.9 + h, 1.9, chat) - 2 * profit_own(1, 1.9, 1.9, chat) + profit_own(1, 1.9 - h, 1.9, chat)) / h**2
print(f"second derivative of own profit at 1.9 (finite diff) = {d2:.5f}")
print(f"profit at prices <= c_hat is <= 0: profit(c_hat-0.1) = {profit_own(1, chat-0.1, 1.9, chat):.5f}")
# at the true cost c=1, is 1.9 a static NE?  (deviation incentive)
br_true = br_repo(1, 1.0, 1.9)
print(f"true cost c=1: best response to rival 1.9 = {br_true:.6f}; profit(1.9)={profit_own(1,1.9,1.9,1.0):.6f}, "
      f"profit(BR)={profit_own(1,br_true,1.9,1.0):.6f}")
# joint-profit maximisation at c=1 (context)
jp = minimize(lambda x: -(mkt.profits(x[0], x[1], 1.0, 1.0)[0] + mkt.profits(x[0], x[1], 1.0, 1.0)[1]),
              x0=[1.8, 1.8], method="Nelder-Mead", options={"xatol": 1e-10, "fatol": 1e-14, "maxiter": 10000})
print(f"joint-profit-maximising symmetric price at c=1: {jp.x}")
print(f"Item 7: reference firm-2 price at gap 0.6 = {ref.loc[ref.cost_gap==0.6,'equilibrium_price_2'].item()} vs collusive 1.9")

print("=" * 90)
print("Admissibility: implied cost from any interior price pair")
for pp in [(1.2, 1.2), (1.0, 1.0), (0.6, 0.6), (0.3, 0.3), (2.5, 1.2)]:
    a1, a2 = shares(*pp)
    print(f"p={pp}: shares=({a1:.4f},{a2:.4f}) c_hat=({pp[0]-MU/(1-a1):.4f},{pp[1]-MU/(1-a2):.4f})")

print("=" * 90)
print("Items 8/9: market size Q")
for Q in [0.8, 1.0, 1.2]:
    print(f"Q={Q}: shares at (1.6,1.7) = {shares(1.6, 1.7, Q)}, "
          f"repo BR(firm1,c=1,rival=1.4729)={br_repo(1, 1.0, 1.472928, Q):.7f}, "
          f"reactive BR={ReactiveCompetitiveAgent(cost=1.0, firm_id=1).competitive_best_response(1.472928, mkt, Q):.7f}")
sd = pd.read_csv(ROOT / "data" / "competitive_demand_shocks.csv")
s1_true = sd.quantity_1 / sd.market_size
s1_noQ = sd.quantity_1  # what an auditor without Q would use if it assumed Q=1
c_true = sd.price_1 - MU / (1 - s1_true)
c_noQ = sd.price_1 - MU / (1 - s1_noQ)
s1_from_prices = np.array([shares(a, b)[0] for a, b in zip(sd.price_1, sd.price_2)])
print("competitive_demand_shocks.csv, firm 1 implied cost:")
print(f"  using q/Q (true shares): min {c_true.min():.6f} max {c_true.max():.6f}")
print(f"  using q with Q assumed 1: min {c_noQ.min():.6f} max {c_noQ.max():.6f}")
print(f"  shares rebuilt from prices with known (a,a0,mu): max |s - q/Q| = {np.abs(s1_from_prices - s1_true).max():.2e}")
cr = pd.read_csv(ROOT / "data" / "collusive_reward_punishment.csv")
cs = cr.quantity_1 / cr.market_size
print(f"collusive_reward_punishment.csv: implied cost firm 1 from data: unique {np.unique(np.round(cr.price_1 - MU/(1-cs), 6))}")
