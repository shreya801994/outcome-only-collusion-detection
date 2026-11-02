"""Final audit of the H2 result (AUC(D) = 0.38 although trajectories are 'identical').

Re-runs only existing, deterministic code with the addendum-2 seeds (no new design):
1. Score competitive firms whose TRUE costs equal the cartel's padded costs, using the
   cartel's random streams, and compare run by run with the cost-padding cartel.
2. Check label orientation in addendum2_scores.csv.
3. From the main design (E2 competitive runs only), show how D and B1 vary with the
   hidden cost level: a cost-level effect inside purely competitive data.

    python -m experiments.audit_h2_auc
"""
import sys
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evaluation.metrics import auc  # noqa: E402
from experiments.v2_hard_negatives import BASE_SEED, RUNS_PER_COST_CELL  # noqa: E402
from experiments.v2_run_all import COST_GAPS, COST_MEANS, PARAMS, PERIODS, score_runs  # noqa: E402
from simulator.batch_sim import auditor_view, simulate_batch  # noqa: E402
from simulator.demand_shocks import ENVIRONMENTS, simulate_shocks  # noqa: E402

costs = np.array([(m - g / 2, m + g / 2) for m in COST_MEANS for g in COST_GAPS for _ in range(RUNS_PER_COST_CELL)])


def streams():
    key = zlib.crc32("H2|collusive_cost_padding".encode())
    return np.random.SeedSequence(BASE_SEED, spawn_key=(key,)).spawn(4)


s = streams()
a, q = simulate_shocks(np.random.default_rng(s[0]), len(costs), PERIODS, ENVIRONMENTS["E2"])
cartel = simulate_batch(costs, a, q, "collusive_cost_padding", PARAMS, *(np.random.default_rng(x) for x in s[1:]))
s = streams()
a2, q2 = simulate_shocks(np.random.default_rng(s[0]), len(costs), PERIODS, ENVIRONMENTS["E2"])
comp_hi = simulate_batch(costs + cartel["cost_pad"][:, None], a2, q2, "competitive", PARAMS,
                         *(np.random.default_rng(x) for x in s[1:]))
sc_cartel = score_runs(auditor_view(cartel, "L3"))
sc_comp_hi = score_runs(auditor_view(comp_hi, "L3"))

stored = pd.read_csv(ROOT / "results_v2" / "addendum2_scores.csv")
h2_pos = stored[(stored.test == "H2") & (stored.conduct == "collusive_cost_padding")].reset_index(drop=True)
h2_neg = stored[(stored.test == "H2") & (stored.conduct == "competitive")].reset_index(drop=True)

print("1) Matched comparison: cartel vs competitors at the SAME (padded) true costs")
for det in ["B0", "B1", "B2", "B3", "D_L3"]:
    d = np.abs(sc_cartel[det].to_numpy() - sc_comp_hi[det].to_numpy()).max()
    print(f"   {det:5s} max |paired score difference| = {d:.1e}   AUC = {auc(sc_cartel[det], sc_comp_hi[det]):.3f}")
print("   stored H2 cartel scores reproduced:", bool(np.allclose(h2_pos.D_L3, sc_cartel.D_L3)))

print("\n2) Pre-registered H2 comparison: cartel (effective cost c+m) vs competitors at TRUE cost c")
print("   positive label = collusive_cost_padding; higher score = more suspicious (D, B1, B2, B3)")
print(f"   mean cost: cartel effective {np.mean(costs.mean(1) + cartel['cost_pad']):.3f} vs competitors {costs.mean():.3f}")
for det in ["D_L3", "B1"]:
    print(f"   {det}: cartel median {h2_pos[det].median():.4f}, competitors median {h2_neg[det].median():.4f}, "
          f"AUC {auc(h2_pos[det], h2_neg[det]):.3f}")

print("\n3) Main design, E2 competitive runs only: score by hidden mean cost (no collusion anywhere)")
m = pd.read_csv(ROOT / "results_v2" / "scores.csv")
c = m[(m.split == "test") & (m.env == "E2") & (m.conduct == "competitive")]
print(c.groupby("cost_mean")[["D_L3", "B1"]].median().round(4).to_string())
lo, hi = c[c.cost_mean == 0.85], c[c.cost_mean == 1.15]
print(f"   AUC(high-cost vs low-cost competitors): D {auc(hi.D_L3, lo.D_L3):.3f}, B1 {auc(hi.B1, lo.B1):.3f}")
