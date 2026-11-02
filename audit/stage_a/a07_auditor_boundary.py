"""Stage A: auditor-boundary checks (read-only).
1. Columns of every auditor-facing CSV.
2. Does run_id (present in auditor files) encode the hidden condition / seed?
3. Can 'hidden' market size be recovered from public prices and quantities when
   the demand parameters (a, a0, mu) are known?  Q_hat = q_i / s_i(p).
4. Which columns do the detector modules read?
Run from the repository root: python audit/stage_a/a07_auditor_boundary.py
"""
import re, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from simulator.market import BertrandMarket, MarketConfig
mkt = BertrandMarket(MarketConfig())
pairs = {
    "data/auditor_trajectories.csv": "data/researcher_trajectories.csv",
    "data/reactive_auditor_trajectories.csv": "data/reactive_researcher_trajectories.csv",
    "data/reactive_shock_auditor_trajectories.csv": "data/reactive_shock_researcher_trajectories.csv",
    "data/dynamic_auditor_trajectories.csv": "data/dynamic_researcher_trajectories.csv",
    "data/collusion_deviation_auditor.csv": "data/collusion_deviation_researcher.csv",
}
for aud, res in pairs.items():
    a = pd.read_csv(ROOT/aud); r = pd.read_csv(ROOT/res)
    msg = f"{aud}: columns={list(a.columns)}"
    if "run_id" in a.columns and "cost_gap" in r.columns:
        m = r[["run_id","cost_gap"]].drop_duplicates("run_id").sort_values("run_id")
        blocks = m.groupby(m.cost_gap.round(6)).run_id.agg(["min","max","count"])
        contiguous = all(b["max"]-b["min"]+1 == b["count"] for _, b in blocks.iterrows())
        msg += f"\n    run_id blocks by hidden cost gap: {blocks.to_dict('index')}; contiguous={contiguous}"
    # public columns identical to researcher columns?
    common = [c for c in ["period","price_1","price_2","quantity_1","quantity_2"] if c in a.columns]
    same = np.allclose(a[common].to_numpy(dtype=float), r[common].to_numpy(dtype=float))
    msg += f"\n    public columns equal to researcher file row-by-row: {same}"
    print(msg)
print()
for f in ["data/dynamic_researcher_trajectories.csv", "data/reactive_shock_researcher_trajectories.csv", "data/competitive_demand_shocks.csv"]:
    d = pd.read_csv(ROOT/f)
    s1 = np.array([mkt.demand(p1, p2, 1.0)[0] for p1, p2 in zip(d.price_1, d.price_2)])
    q_hat = d.quantity_1 / s1
    print(f"{f}: max |Q_hat - market_size| using known demand parameters = {np.abs(q_hat - d.market_size).max():.2e}")
print()
for f in sorted((ROOT/"detectors").glob("*.py")):
    cols = sorted(set(re.findall(r'"(price_[12]|quantity_[12]|period|market_size|cost_[12]|run_id|condition|cost_gap)"', f.read_text())))
    print(f"{f.relative_to(ROOT)} reads columns: {cols}")
