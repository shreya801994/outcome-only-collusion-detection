"""Audit of the auditor information boundary (no new simulation; reads data_v2/).

1. Which arrays reach each detector (from simulator.batch_sim.AUDITOR_LEVELS and score_runs).
2. D_L3 uses observed shares q/Q; check it equals D computed from the TRUE model shares
   s(p; a_t), which an auditor could only compute if it knew the attractiveness path.
3. Where market size is constant at 1 (E0, E2), D_L2 == D_L3 exactly; where it moves (E1, E3) they differ.
4. The outside share s0 = 1 - (q1+q2)/Q carries the same information as Q.

    python -m experiments.audit_information_boundary
"""
import inspect
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from detectors import implied_cost  # noqa: E402
from experiments import v2_run_all  # noqa: E402
from simulator.batch_sim import AUDITOR_LEVELS  # noqa: E402
from simulator.equilibrium import shares  # noqa: E402

print("1) AUDITOR_LEVELS:", AUDITOR_LEVELS)
src = inspect.getsource(v2_run_all.score_runs)
print("   score_runs reads keys:", sorted({k for k in ("price", "quantity", "market_size", "cost", "attractiveness")
                                          if f'"{k}"' in src}))
print("   implied_cost.score signature:", inspect.signature(implied_cost.score))

print("\n2) D from observed shares q/Q vs D from model shares s(p; a_t)")
for cell in ["test_E2_competitive_grid", "test_E2_collusive_tracking_grid", "test_E3_collusive_rigid_grid"]:
    z = np.load(ROOT / "data_v2" / f"{cell}.npz")
    p = z["price"][:, 50:, :].astype(float)
    q = z["quantity"][:, 50:, :].astype(float)
    Q = z["market_size"][:, 50:].astype(float)
    a = z["attractiveness"][:, 50:, :].astype(float)
    d_obs = implied_cost.score(p, q, 0.25, market_size=Q)
    s1, s2, _ = shares(p[..., 0], p[..., 1], a[..., 0], a[..., 1])
    d_model = implied_cost.score(p, np.stack([s1, s2], -1), 0.25, market_size=np.ones_like(Q))
    print(f"   {cell:34s} max |D(q/Q) - D(s(p;a))| = {np.abs(d_obs - d_model).max():.1e} (float32 storage)")

print("\n3) D_L2 (market size assumed 1) vs D_L3 (market size observed)")
s = pd.read_csv(ROOT / "results_v2" / "scores.csv")
for env, g in s.groupby("env"):
    print(f"   {env}: max |D_L2 - D_L3| = {np.abs(g.D_L2 - g.D_L3).max():.2e}")

print("\n4) Outside share reconstructs market size")
z = np.load(ROOT / "data_v2" / "test_E3_competitive_grid.npz")
q = z["quantity"].astype(float); Q = z["market_size"].astype(float); p = z["price"].astype(float)
a = z["attractiveness"].astype(float)
_, _, s0 = shares(p[..., 0], p[..., 1], a[..., 0], a[..., 1])
Q_from_s0 = (q[..., 0] + q[..., 1]) / (1 - s0)
print(f"   max relative error of Q = (q1+q2)/(1-s0): {np.abs(Q_from_s0 / Q - 1).max():.1e}")
