"""Stage A: (1) what run counts does the committed B0 figure imply? (2) data behind the
hard-negative figure; (3) formula check: do competitive Nash prices move with Q, with a
common attractiveness change, or with the outside option?  (no trajectories simulated)
Run from the repository root: python audit/stage_a/a08_figures_and_attractiveness.py
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.optimize import fsolve
from scipy.stats import norm
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from simulator.market import BertrandMarket, MarketConfig
def wilson(x, n, z=1.96):
    p = x/n; den = 1+z*z/n; c = (p+z*z/(2*n))/den; h = z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return round(max(0,c-h),4), round(min(1,c+h),4)
print("Wilson 95% for x/n:", {f"{x}/{n}": wilson(x, n) for x, n in [(0,5),(5,5),(2,100),(100,100)]})
rr = pd.read_csv(ROOT/"data/reactive_researcher_trajectories.csv")
print("reactive mean prices by gap (data behind hard_negative_cost_asymmetry.png):")
print(rr.groupby("cost_gap")[["price_1","price_2"]].mean().round(4).to_string())
def nash(cfg, c=(1.0, 1.0), Q=1.0):
    m = BertrandMarket(cfg)
    def foc(p):
        q1, q2 = m.demand(p[0], p[1], Q); s1, s2 = q1/Q, q2/Q
        return [p[0]-c[0]-cfg.mu/(1-s1), p[1]-c[1]-cfg.mu/(1-s2)]
    return fsolve(foc, [1.5, 1.5], xtol=1e-13)
for label, cfg, Q in [("baseline", MarketConfig(), 1.0), ("Q=1.2", MarketConfig(), 1.2), ("Q=0.8", MarketConfig(), 0.8),
                      ("a1=a2=2.2 (common attractiveness +0.2)", MarketConfig(a1=2.2, a2=2.2), 1.0),
                      ("a1=a2=1.8", MarketConfig(a1=1.8, a2=1.8), 1.0),
                      ("a0=0.2 (outside option +0.2)", MarketConfig(a0=0.2), 1.0),
                      ("a1=2.2 only (product-specific)", MarketConfig(a1=2.2), 1.0)]:
    p = nash(cfg, Q=Q); print(f"Nash prices, {label:40s}: ({p[0]:.6f}, {p[1]:.6f})")
