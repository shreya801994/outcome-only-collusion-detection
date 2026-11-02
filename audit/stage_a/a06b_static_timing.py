"""Stage A: which update timing generated each static competitive CSV?
Checks every period against two conventions using the committed best-response code:
  simultaneous: p1[t+1]=BR1(p2[t]),   p2[t+1]=BR2(p1[t])      (committed simulation.py)
  sequential:   p1[t+1]=BR1(p2[t]),   p2[t+1]=BR2(p1[t+1])
Run from the repository root: python audit/stage_a/a06b_static_timing.py
"""
import sys
from functools import lru_cache
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from simulator.market import BertrandMarket, MarketConfig
from simulator.agents import CompetitiveAgent
mkt = BertrandMarket(MarketConfig())
@lru_cache(maxsize=None)
def br(firm, cost, rival):
    return CompetitiveAgent(cost=cost, firm_id=firm).best_response(rival, mkt, (1.0, 1.1, 1.3, 1.6))
def check(g):
    c1, c2 = float(g.cost_1.iloc[0]), float(g.cost_2.iloc[0])
    p1, p2 = g.price_1.to_numpy(), g.price_2.to_numpy()
    sim = max(max(abs(p1[t+1]-br(1,c1,float(p2[t]))), abs(p2[t+1]-br(2,c2,float(p1[t])))) for t in range(len(p1)-1))
    seq = max(max(abs(p1[t+1]-br(1,c1,float(p2[t]))), abs(p2[t+1]-br(2,c2,float(p1[t+1])))) for t in range(len(p1)-1))
    return sim, seq
for f in ["competitive_baseline.csv","competitive_cost_gap_0.1.csv","competitive_cost_gap_0.3.csv","competitive_cost_gap_0.6.csv","competitive_demand_shocks.csv"]:
    sim, seq = check(pd.read_csv(ROOT/"data"/f))
    print(f"{f:34s} max error simultaneous={sim:.2e}  sequential={seq:.2e}")
rt = pd.read_csv(ROOT/"data/researcher_trajectories.csv")
for rid in [1, 6, 11, 16]:
    sim, seq = check(rt[rt.run_id==rid].reset_index(drop=True))
    print(f"researcher_trajectories run {rid:2d}            max error simultaneous={sim:.2e}  sequential={seq:.2e}")
