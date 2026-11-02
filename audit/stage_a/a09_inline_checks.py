"""Stage A: small checks first run inline, saved here so every reported number has a script.
1. Static researcher_trajectories runs vs single competitive_cost_gap_*.csv files.
2. First periods of the gap-0.6 static runs under the two files (update timing).
3. The two collusive deviation files around the deviation.
4. FOC residuals at the Nash prices reported in a08 for shifted demand parameters.
Run from the repository root: python audit/stage_a/a09_inline_checks.py
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from simulator.market import BertrandMarket, MarketConfig
rt = pd.read_csv(ROOT/"data/researcher_trajectories.csv")
for gap, tag in [(0.0,"0.0"),(0.1,"0.1"),(0.3,"0.3"),(0.6,"0.6")]:
    s = pd.read_csv(ROOT/f"data/competitive_cost_gap_{tag}.csv")
    runs = rt[np.isclose(rt.cost_gap, gap)]
    d = max(np.abs(r[["price_1","price_2"]].to_numpy()-s[["price_1","price_2"]].to_numpy()).max() for _, r in runs.groupby("run_id"))
    print(f"1) gap {gap}: max |researcher_trajectories run - competitive_cost_gap_{tag}.csv| = {d:.2e}")
s = pd.read_csv(ROOT/"data/competitive_cost_gap_0.6.csv")
r = rt[(rt.run_id==16)].reset_index(drop=True)
print("2) gap 0.6, periods 0-5:")
print(pd.DataFrame({"t":range(6),"researcher_p1":r.price_1[:6],"researcher_p2":r.price_2[:6],"gapfile_p1":s.price_1[:6],"gapfile_p2":s.price_2[:6]}).round(6).to_string(index=False))
a = pd.read_csv(ROOT/"data/collusion_deviation_researcher.csv"); b = pd.read_csv(ROOT/"data/collusive_deviation_response.csv")
print("3) collusion_deviation_researcher.csv periods 28-40:"); print(a.loc[28:40,["period","price_1","price_2","forced_deviation"]].T.to_string(header=False))
print("   collusive_deviation_response.csv periods 28-40:"); print(b.loc[28:40,["period","price_1","price_2","forced_deviation"]].T.to_string(header=False))
for label,cfg,p in [("base",MarketConfig(),(1.472927,1.472927)),("a1=a2=2.2",MarketConfig(a1=2.2,a2=2.2),(1.486387,1.486387)),
                    ("a1=a2=1.8",MarketConfig(a1=1.8,a2=1.8),(1.450471,1.450471)),("a0=0.2",MarketConfig(a0=0.2),(1.450471,1.450471)),
                    ("a1=2.2 only",MarketConfig(a1=2.2),(1.552790,1.424528))]:
    q1,q2 = BertrandMarket(cfg).demand(*p)
    print(f"4) {label:12s} FOC residuals at reported Nash prices: {p[0]-1-0.25/(1-q1):.1e}, {p[1]-1-0.25/(1-q2):.1e}")
