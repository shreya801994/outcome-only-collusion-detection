"""Stage A: does the existing shock design move prices? (read-only, existing CSVs only)

For every dataset with varying market_size: shock frequencies, persistence,
and the association between market-size changes and price changes,
contemporaneous and one-period lagged (static/reactive agents set p_{t+1}
after seeing Q_t; adaptive agents see Q_t before setting p_t).
Run from the repository root:  python audit/stage_a/a05_shock_analysis.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def corr(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = ~(np.isnan(a) | np.isnan(b))
    if ok.sum() < 3 or a[ok].std() == 0 or b[ok].std() == 0:
        return float("nan")
    return float(np.corrcoef(a[ok], b[ok])[0, 1])


def analyse(name, df):
    if "run_id" not in df.columns:
        df = df.assign(run_id=0)
    df = df.sort_values(["run_id", "period"])
    out = []
    for rid, g in df.groupby("run_id"):
        Q = g["market_size"].to_numpy()
        p1, p2 = g["price_1"].to_numpy(), g["price_2"].to_numpy()
        dQ = np.diff(Q)
        d1, d2 = np.diff(p1), np.diff(p2)
        out.append({
            "run_id": rid,
            "share_periods_shocked": float(np.mean(Q != 1.0)),
            "lag1_autocorr_Q": corr(Q[:-1], Q[1:]),
            "corr(dQ_t, dp1_t)": corr(dQ, d1),
            "corr(dQ_t, dp2_t)": corr(dQ, d2),
            "corr(dQ_t, dp1_t+1)": corr(dQ[:-1], d1[1:]),
            "corr(dQ_t, dp2_t+1)": corr(dQ[:-1], d2[1:]),
            "corr(dp1_t, dp2_t)": corr(d1, d2),
            "max|p1 - mean p1|": float(np.abs(p1 - p1.mean()).max()),
        })
    r = pd.DataFrame(out)
    print(f"--- {name}: runs={len(r)}; market_size values={sorted(df.market_size.unique())}")
    print(r.drop(columns="run_id").agg(["mean", "min", "max"]).to_string(float_format=lambda v: f"{v:.4g}"))


pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 30)
for f in [
    "data/competitive_demand_shocks.csv",
    "data/reactive_shock_researcher_trajectories.csv",
    "data/dynamic_researcher_trajectories.csv",
    "data/adaptive_competitive_demand_shocks.csv",
    "data/adaptive_heterogeneous_demand_shocks.csv",
]:
    analyse(f, pd.read_csv(ROOT / f))

# Shock runs: how long does a shock last?  (consecutive periods with Q != 1 and same value)
d = pd.read_csv(ROOT / "data/reactive_shock_researcher_trajectories.csv").sort_values(["run_id", "period"])
lengths = []
for _, g in d.groupby("run_id"):
    q = g.market_size.to_numpy()
    run = 0
    for i in range(len(q)):
        if q[i] != 1.0 and (i == 0 or q[i] == q[i - 1]):
            run += 1
        elif q[i] != 1.0:
            if run:
                lengths.append(run)
            run = 1
        else:
            if run:
                lengths.append(run)
            run = 0
    if run:
        lengths.append(run)
print(f"\nreactive shock data: shock spell lengths (periods) distribution: {pd.Series(lengths).value_counts().sort_index().to_dict()}")
