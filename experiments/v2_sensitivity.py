"""EXPLORATORY sensitivity analyses (added after the frozen design ran; not pre-registered).

    python -m experiments.v2_sensitivity

Each analysis varies one design parameter and reports pooled (and, for B0,
within-cost-cell) AUC of collusive vs competitive runs, 30 runs per cost cell
per conduct, fresh seeds (base 20261103) that do not overlap the main design.

S1  share-shock scale        E2 shock SDs x {0, 0.1, 0.25, 0.5, 1}       tracking and rigid vs competitive
S2  price-cut probability    E0, tremble prob {0, 0.001, 0.003, 0.01, 0.03}   rigid vs competitive
S3  hidden-cost uncertainty  E0, mean costs {1-w, 1, 1+w}, w in {0.15, 0.30, 0.45}   rigid vs competitive
S4  collusion intensity      kappa ranges [0.1,0.3], [0.3,0.5], [0.5,1] in E0 and E2
S5  competitor dynamics      competitors target the current static Nash price
                             (no reaction to the rival's last price), E0 and E2
S6  as S5 without price cuts (no punishment episodes), E0 and E2

Writes results_v2/sensitivity.csv.
"""

import sys
import zlib
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluation.metrics import bootstrap_auc  # noqa: E402
from experiments.v2_run_all import COST_GAPS, PARAMS, PERIODS, score_runs  # noqa: E402
from simulator.batch_sim import auditor_view, simulate_batch  # noqa: E402
from simulator.demand_shocks import ENVIRONMENTS, simulate_shocks  # noqa: E402

BASE_SEED = 20261103
RUNS_PER_COST_CELL = 30
N_BOOT = 1000
DETECTORS = ["B0", "B1", "B2", "B3", "D_L3"]


def grid_costs(cost_means):
    rows, cells = [], []
    for i, c_mean in enumerate(cost_means):
        for j, gap in enumerate(COST_GAPS):
            rows += [(c_mean - gap / 2.0, c_mean + gap / 2.0)] * RUNS_PER_COST_CELL
            cells += [i * len(COST_GAPS) + j] * RUNS_PER_COST_CELL
    return np.array(rows), np.array(cells)


def simulate_and_score(analysis, point, conduct, shock_spec, params, cost_means):
    key = zlib.crc32(f"{analysis}|{point}|{conduct}".encode())
    s_shock, s_par, s_noise, s_tr = np.random.SeedSequence(BASE_SEED, spawn_key=(key,)).spawn(4)
    costs, cells = grid_costs(cost_means)
    a, q = simulate_shocks(np.random.default_rng(s_shock), len(costs), PERIODS, shock_spec)
    result = simulate_batch(costs, a, q, conduct, params, np.random.default_rng(s_par),
                            np.random.default_rng(s_noise), np.random.default_rng(s_tr))
    scores = score_runs(auditor_view(result, "L3"))
    scores["cost_cell"] = cells
    return scores


def evaluate(analysis, point, value, positive, shock_spec, params, cost_means, negative="competitive"):
    neg = simulate_and_score(analysis, point, negative, shock_spec, params, cost_means)
    pos = simulate_and_score(analysis, point, positive, shock_spec, params, cost_means)
    rows = []
    for det in DETECTORS:
        seed = zlib.crc32(f"{analysis}|{point}|{positive}|{det}".encode())
        pooled = bootstrap_auc(pos[det], neg[det], pos.cost_cell.values, neg.cost_cell.values, N_BOOT, seed)
        within = bootstrap_auc(pos[det], neg[det], pos.cost_cell.values, neg.cost_cell.values, N_BOOT,
                               seed + 1, within=True)
        rows.append({"analysis": analysis, "point": point, "value": value, "positive": positive,
                     "negative": negative, "detector": det, "auc_pooled": pooled[0], "pooled_lo": pooled[1], "pooled_hi": pooled[2],
                     "auc_within": within[0], "within_lo": within[1], "within_hi": within[2]})
    return rows


def main():
    rows = []
    e2 = ENVIRONMENTS["E2"]
    design_means = (0.85, 1.00, 1.15)
    for scale in (0.0, 0.1, 0.25, 0.5, 1.0):
        spec = replace(e2, common_sd=e2.common_sd * scale, idio_sd=e2.idio_sd * scale)
        for positive in ("collusive_tracking", "collusive_rigid"):
            rows += evaluate("S1_shock_scale", f"scale={scale}", scale, positive, spec, PARAMS, design_means)
        print(f"S1 scale={scale} done", flush=True)
    for prob in (0.0, 0.001, 0.003, 0.01, 0.03):
        params = replace(PARAMS, tremble_prob=prob)
        rows += evaluate("S2_price_cut_prob", f"prob={prob}", prob, "collusive_rigid",
                         ENVIRONMENTS["E0"], params, design_means)
        print(f"S2 prob={prob} done", flush=True)
    for width in (0.15, 0.30, 0.45):
        means = (1.0 - width, 1.0, 1.0 + width)
        rows += evaluate("S3_cost_uncertainty", f"w={width}", width, "collusive_rigid",
                         ENVIRONMENTS["E0"], PARAMS, means)
        print(f"S3 w={width} done", flush=True)
    for low, high in ((0.1, 0.3), (0.3, 0.5), (0.5, 1.0)):
        params = replace(PARAMS, kappa_low=low, kappa_high=high)
        rows += evaluate("S4_kappa_E0", f"kappa=[{low},{high}]", (low + high) / 2, "collusive_rigid",
                         ENVIRONMENTS["E0"], params, design_means)
        rows += evaluate("S4_kappa_E2", f"kappa=[{low},{high}]", (low + high) / 2, "collusive_tracking",
                         ENVIRONMENTS["E2"], params, design_means)
        print(f"S4 kappa=[{low},{high}] done", flush=True)
    # S5: alternative competitive dynamic (target = current static Nash, no reaction to rival's last price)
    for env, positive in (("E0", "collusive_rigid"), ("E2", "collusive_tracking"), ("E2", "collusive_rigid")):
        rows += evaluate("S5_nash_tracking_competitors", env, 0.0, positive, ENVIRONMENTS[env], PARAMS,
                         design_means, negative="competitive_nash")
        print(f"S5 {env} {positive} done", flush=True)
    # S6: as S5 but with no price cuts, so no punishment episodes ("stationary" collusion)
    quiet = replace(PARAMS, tremble_prob=0.0)
    for env, positive in (("E0", "collusive_rigid"), ("E2", "collusive_tracking"), ("E2", "collusive_rigid")):
        rows += evaluate("S6_nash_competitors_no_price_cuts", env, 0.0, positive, ENVIRONMENTS[env], quiet,
                         design_means, negative="competitive_nash")
        print(f"S6 {env} {positive} done", flush=True)
    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "results_v2" / "sensitivity.csv", index=False)
    pd.set_option("display.width", 250)
    print(out.pivot_table(index=["analysis", "point", "positive"], columns="detector",
                          values="auc_pooled").round(3).to_string())


if __name__ == "__main__":
    main()
