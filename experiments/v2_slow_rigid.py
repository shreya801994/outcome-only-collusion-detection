"""Addendum 3 (rules frozen in docs/V2_ADDENDUM_3_SLOW_RIGID.md).

    python -m experiments.v2_slow_rigid

Slow rigid cartel vs slow competitors in E2, matched dynamics, frozen main-design
thresholds, fresh seeds (base 20261106).  Writes (new files only):
    results_v2/addendum3_scores.csv
    results_v2/addendum3_metrics.csv
    results_v2/addendum3_criteria.json
"""

import json
import sys
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluation.metrics import auc, bootstrap_auc, wilson  # noqa: E402
from experiments.v2_hard_negatives import SLOW  # noqa: E402
from experiments.v2_run_all import COST_GAPS, COST_MEANS, PERIODS, score_runs  # noqa: E402
from simulator.batch_sim import auditor_view, simulate_batch  # noqa: E402
from simulator.demand_shocks import ENVIRONMENTS, simulate_shocks  # noqa: E402

BASE_SEED = 20261106
RUNS_PER_COST_CELL = 30
N_BOOT = 2000
OUT = ROOT / "results_v2"
DETECTORS = ["B0", "B1", "B2", "B3", "D_L2", "D_L3"]


def run(conduct):
    rows, cells = [], []
    for i, m in enumerate(COST_MEANS):
        for j, g in enumerate(COST_GAPS):
            rows += [(m - g / 2, m + g / 2)] * RUNS_PER_COST_CELL
            cells += [i * len(COST_GAPS) + j] * RUNS_PER_COST_CELL
    costs = np.array(rows)
    key = zlib.crc32(f"S|{conduct}".encode())
    s_shock, s_par, s_noise, s_tr = np.random.SeedSequence(BASE_SEED, spawn_key=(key,)).spawn(4)
    a, q = simulate_shocks(np.random.default_rng(s_shock), len(costs), PERIODS, ENVIRONMENTS["E2"])
    res = simulate_batch(costs, a, q, conduct, SLOW, np.random.default_rng(s_par),
                         np.random.default_rng(s_noise), np.random.default_rng(s_tr))
    sc = score_runs(auditor_view(res, "L3"))
    sc["cost_cell"], sc["conduct"] = cells, conduct
    sc["cost_1"], sc["cost_2"] = costs[:, 0], costs[:, 1]
    sc["punish_share"] = res["punishing"][:, 50:].mean(axis=1)
    return sc


def rates(pos_flags, neg_flags):
    tpr, fpr = pos_flags.mean(), neg_flags.mean()
    prec = tpr / (tpr + fpr) if tpr + fpr > 0 else np.nan
    f1 = 2 * prec * tpr / (prec + tpr) if (prec + tpr) > 0 else np.nan
    return tpr, fpr, prec, f1


def bootstrap_rates(pos, neg, det, thr, seed):
    rng = np.random.default_rng(seed)
    pf = (pos[det].to_numpy() > thr)
    nf = (neg[det].to_numpy() > thr)
    pc, nc = pos.cost_cell.to_numpy(), neg.cost_cell.to_numpy()
    out = np.empty((N_BOOT, 4))
    p_idx = [np.flatnonzero(pc == c) for c in np.unique(pc)]
    n_idx = [np.flatnonzero(nc == c) for c in np.unique(nc)]
    for b in range(N_BOOT):
        ps = np.concatenate([rng.choice(ix, len(ix)) for ix in p_idx])
        ns = np.concatenate([rng.choice(ix, len(ix)) for ix in n_idx])
        out[b] = rates(pf[ps], nf[ns])
    return np.nanpercentile(out, [2.5, 97.5], axis=0)


def main():
    thr = pd.read_csv(OUT / "thresholds.csv")
    thr = thr[(thr.calibration == "matched") & (thr.env == "E2")].set_index("detector").threshold
    pos, neg = run("collusive_rigid"), run("competitive")

    rows = []
    for det in DETECTORS:
        seed = zlib.crc32(f"add3|{det}".encode())
        pooled = bootstrap_auc(pos[det], neg[det], pos.cost_cell.values, neg.cost_cell.values, N_BOOT, seed)
        within = bootstrap_auc(pos[det], neg[det], pos.cost_cell.values, neg.cost_cell.values, N_BOOT, seed + 1,
                               within=True)
        t = float(thr[det])
        pf, nf = pos[det] > t, neg[det] > t
        tpr, fpr, prec, f1 = rates(pf.to_numpy(), nf.to_numpy())
        ci = bootstrap_rates(pos, neg, det, t, seed + 2)
        rows.append({"detector": det, "threshold": t, "n_pos": len(pos), "n_neg": len(neg),
                     "auc_pooled": pooled[0], "auc_pooled_lo": pooled[1], "auc_pooled_hi": pooled[2],
                     "auc_within": within[0], "auc_within_lo": within[1], "auc_within_hi": within[2],
                     "TPR": tpr, "TPR_lo": ci[0, 0], "TPR_hi": ci[1, 0],
                     "TPR_wilson_lo": wilson(int(pf.sum()), len(pos))[0], "TPR_wilson_hi": wilson(int(pf.sum()), len(pos))[1],
                     "FPR": fpr, "FPR_lo": ci[0, 1], "FPR_hi": ci[1, 1],
                     "FPR_wilson_lo": wilson(int(nf.sum()), len(neg))[0], "FPR_wilson_hi": wilson(int(nf.sum()), len(neg))[1],
                     "precision_50": prec, "precision_50_lo": ci[0, 2], "precision_50_hi": ci[1, 2],
                     "F1_50": f1, "F1_50_lo": ci[0, 3], "F1_50_hi": ci[1, 3]})
    metrics = pd.DataFrame(rows)

    # diagnostic: dynamics contrast (slow vs fast competitors, both competitive)
    main_scores = pd.read_csv(OUT / "scores.csv")
    fast = main_scores[(main_scores.split == "test") & (main_scores.env == "E2")
                       & (main_scores.conduct == "competitive")]
    dyn = bootstrap_auc(neg.D_L3, fast.D_L3, neg.cost_cell.values, fast.cost_cell.values, N_BOOT,
                        zlib.crc32(b"add3|dynamics"))
    conduct = metrics.set_index("detector").loc["D_L3"]
    criteria = {
        "S1": {"rule": "AUC(D) slow rigid vs slow competitors >= 0.80",
               "value": [conduct.auc_pooled, conduct.auc_pooled_lo, conduct.auc_pooled_hi],
               "pass": bool(conduct.auc_pooled >= 0.80)},
        "S2": {"rule": "FPR of slow competitors at frozen D threshold <= 0.10",
               "value": [conduct.FPR, conduct.FPR_wilson_lo, conduct.FPR_wilson_hi],
               "pass": bool(conduct.FPR <= 0.10)},
        "S3": {"rule": "dynamics-contrast AUC(D) < conduct-contrast AUC(D)",
               "dynamics_contrast": list(dyn), "conduct_contrast": conduct.auc_pooled,
               "pass": bool(dyn[0] < conduct.auc_pooled)},
        "descriptives": {
            "D_median_slow_rigid": float(pos.D_L3.median()), "D_median_slow_comp": float(neg.D_L3.median()),
            "D_median_fast_comp": float(fast.D_L3.median()),
            "punish_share_slow_rigid_mean": float(pos.punish_share.mean()),
            "B0_median_slow_rigid": float(pos.B0.median()), "B0_median_slow_comp": float(neg.B0.median()),
        },
    }
    pd.concat([pos, neg], ignore_index=True).to_csv(OUT / "addendum3_scores.csv", index=False)
    metrics.to_csv(OUT / "addendum3_metrics.csv", index=False)
    (OUT / "addendum3_criteria.json").write_text(json.dumps(criteria, indent=2, default=float))
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    print(metrics[["detector", "auc_pooled", "auc_pooled_lo", "auc_pooled_hi", "auc_within", "TPR", "TPR_lo",
                   "TPR_hi", "FPR", "FPR_lo", "FPR_hi", "precision_50", "F1_50"]].round(3).to_string(index=False))
    print(json.dumps(criteria, indent=1, default=float))


if __name__ == "__main__":
    main()
