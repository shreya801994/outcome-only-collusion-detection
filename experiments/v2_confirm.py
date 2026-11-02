"""Confirmatory replication (rules frozen in docs/V2_ADDENDUM_CONFIRMATORY.md).

    python -m experiments.v2_confirm

Fresh seeds (base 20261104).  Writes results_v2/confirmatory.csv and
results_v2/confirmatory_criteria.json.
"""

import json
import sys
import zlib
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluation.metrics import bootstrap_auc, wilson  # noqa: E402
from experiments.v2_run_all import COST_GAPS, PARAMS, PERIODS, score_runs  # noqa: E402
from simulator.batch_sim import auditor_view, simulate_batch  # noqa: E402
from simulator.demand_shocks import ENVIRONMENTS, simulate_shocks  # noqa: E402

BASE_SEED = 20261104
RUNS_PER_COST_CELL = 30
N_BOOT = 2000
NAIVE_B0_THRESHOLD_FILE = ROOT / "results_v2" / "thresholds.csv"
DETECTORS = ["B0", "B1", "B2", "B3", "D_L3"]

CELLS = {
    "C1": dict(env="E0", positive="collusive_rigid", negative="competitive",
               means=(0.55, 1.00, 1.45), params=PARAMS),
    "C2": dict(env="E0", positive="collusive_rigid", negative="competitive_nash",
               means=(0.85, 1.00, 1.15), params=replace(PARAMS, tremble_prob=0.0)),
    "C3": dict(env="E2", positive="collusive_tracking", negative="competitive_nash",
               means=(0.85, 1.00, 1.15), params=replace(PARAMS, tremble_prob=0.0)),
}


def run(cell, conduct, spec):
    rows, cells = [], []
    for i, m in enumerate(spec["means"]):
        for j, g in enumerate(COST_GAPS):
            rows += [(m - g / 2, m + g / 2)] * RUNS_PER_COST_CELL
            cells += [i * len(COST_GAPS) + j] * RUNS_PER_COST_CELL
    costs = np.array(rows)
    key = zlib.crc32(f"{cell}|{conduct}".encode())
    s_shock, s_par, s_noise, s_tr = np.random.SeedSequence(BASE_SEED, spawn_key=(key,)).spawn(4)
    a, q = simulate_shocks(np.random.default_rng(s_shock), len(costs), PERIODS, ENVIRONMENTS[spec["env"]])
    res = simulate_batch(costs, a, q, conduct, spec["params"], np.random.default_rng(s_par),
                         np.random.default_rng(s_noise), np.random.default_rng(s_tr))
    scores = score_runs(auditor_view(res, "L3"))
    scores["cost_cell"] = cells
    scores["cell"], scores["conduct"] = cell, conduct
    scores["cost_1"], scores["cost_2"] = costs[:, 0], costs[:, 1]
    return scores


def main():
    thr = pd.read_csv(NAIVE_B0_THRESHOLD_FILE)
    naive_b0 = float(thr[(thr.calibration == "naive") & (thr.detector == "B0")].threshold.item())
    all_scores, auc_rows = [], {}
    for cell, spec in CELLS.items():
        pos, neg = run(cell, spec["positive"], spec), run(cell, spec["negative"], spec)
        all_scores += [pos, neg]
        auc_rows[cell] = {}
        for det in DETECTORS:
            seed = zlib.crc32(f"confirm|{cell}|{det}".encode())
            p = bootstrap_auc(pos[det], neg[det], pos.cost_cell.values, neg.cost_cell.values, N_BOOT, seed)
            w = bootstrap_auc(pos[det], neg[det], pos.cost_cell.values, neg.cost_cell.values, N_BOOT, seed + 1,
                              within=True)
            auc_rows[cell][det] = {"pooled": p, "within": w}
        if cell == "C1":
            fp = int((neg.B0 > naive_b0).sum())
            auc_rows[cell]["naive_B0_fpr"] = [fp, len(neg), fp / len(neg), *wilson(fp, len(neg))]
        print(cell, {d: round(v["pooled"][0], 3) for d, v in auc_rows[cell].items() if isinstance(v, dict)},
              flush=True)

    c1 = auc_rows["C1"]["B0"]["within"][0] - auc_rows["C1"]["B0"]["pooled"][0]
    c1b = auc_rows["C1"]["naive_B0_fpr"][2]
    c2 = {d: auc_rows["C2"][d]["pooled"][0] for d in ("B1", "B2", "B3", "D_L3")}
    c3 = auc_rows["C3"]["D_L3"]["pooled"][0]
    criteria = {
        "C1": {"rule": "within - pooled AUC(B0) >= 0.10", "value": c1, "pass": bool(c1 >= 0.10)},
        "C1b": {"rule": "naive B0 competitive FPR >= 0.30", "value": auc_rows["C1"]["naive_B0_fpr"],
                "pass": bool(c1b >= 0.30)},
        "C2": {"rule": "B1,B2,B3,D_L3 pooled AUC in [0.35,0.65]", "value": c2,
               "pass": bool(all(0.35 <= v <= 0.65 for v in c2.values()))},
        "C3": {"rule": "AUC(D_L3) >= 0.95", "value": c3, "pass": bool(c3 >= 0.95)},
        "auc_detail": auc_rows,
    }
    out = ROOT / "results_v2"
    pd.concat(all_scores, ignore_index=True).to_csv(out / "confirmatory.csv", index=False)
    (out / "confirmatory_criteria.json").write_text(json.dumps(criteria, indent=2, default=float))
    print(json.dumps({k: v for k, v in criteria.items() if k != "auc_detail"}, indent=2, default=float))


if __name__ == "__main__":
    main()
