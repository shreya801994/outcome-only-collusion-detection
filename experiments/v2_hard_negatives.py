"""Addendum 2 (rules frozen in docs/V2_ADDENDUM_2_HARD_NEGATIVES.md).

    python -m experiments.v2_hard_negatives

H1  slow, noisy competitors as hard negatives (E2)
H2  cost-padding cartel: the identification boundary (E2)
H3  operating-point table (TPR, FPR, precision, F1) from the main design

Writes results_v2/addendum2_scores.csv, addendum2_criteria.json, operating_points.csv.
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
from experiments.v2_run_all import COST_GAPS, COST_MEANS, PARAMS, PERIODS, score_runs  # noqa: E402
from simulator.batch_sim import auditor_view, simulate_batch  # noqa: E402
from simulator.demand_shocks import ENVIRONMENTS, simulate_shocks  # noqa: E402

BASE_SEED = 20261105
RUNS_PER_COST_CELL = 30
N_BOOT = 2000
OUT = ROOT / "results_v2"
SLOW = replace(PARAMS, adjust_low=0.05, adjust_high=0.20, noise_sd=0.02)
DETECTORS = ["B0", "B1", "B2", "B3", "D_L3"]


def run(tag, conduct, params, env="E2"):
    rows, cells = [], []
    for i, m in enumerate(COST_MEANS):
        for j, g in enumerate(COST_GAPS):
            rows += [(m - g / 2, m + g / 2)] * RUNS_PER_COST_CELL
            cells += [i * len(COST_GAPS) + j] * RUNS_PER_COST_CELL
    costs = np.array(rows)
    key = zlib.crc32(f"{tag}|{conduct}".encode())
    s_shock, s_par, s_noise, s_tr = np.random.SeedSequence(BASE_SEED, spawn_key=(key,)).spawn(4)
    a, q = simulate_shocks(np.random.default_rng(s_shock), len(costs), PERIODS, ENVIRONMENTS[env])
    res = simulate_batch(costs, a, q, conduct, params, np.random.default_rng(s_par),
                         np.random.default_rng(s_noise), np.random.default_rng(s_tr))
    sc = score_runs(auditor_view(res, "L3"))
    sc["cost_cell"], sc["test"], sc["conduct"] = cells, tag, conduct
    sc["cost_1"], sc["cost_2"], sc["cost_pad"] = costs[:, 0], costs[:, 1], res["cost_pad"]
    return sc


def aucs(pos, neg, tag):
    out = {}
    for det in DETECTORS:
        seed = zlib.crc32(f"add2|{tag}|{det}".encode())
        p = bootstrap_auc(pos[det], neg[det], pos.cost_cell.values, neg.cost_cell.values, N_BOOT, seed)
        w = bootstrap_auc(pos[det], neg[det], pos.cost_cell.values, neg.cost_cell.values, N_BOOT, seed + 1, within=True)
        out[det] = {"pooled": p, "within": w}
    return out


def operating_points():
    rates = pd.read_csv(OUT / "rates.csv")
    m = rates[(rates.calibration == "matched") & (rates.cost_mode == "grid")]
    rows = []
    for (env, det), df in m.groupby(["env", "detector"]):
        neg = df[df.conduct == "competitive"].iloc[0]
        for _, pos in df[df.conduct != "competitive"].iterrows():
            tpr, fpr = pos.rate, neg.rate
            prec = tpr / (tpr + fpr) if tpr + fpr > 0 else float("nan")  # 50% prevalence
            f1 = 2 * prec * tpr / (prec + tpr) if prec + tpr > 0 else float("nan")
            rows.append({"env": env, "detector": det, "positive": pos.conduct, "threshold": pos.threshold,
                         "TPR": tpr, "TPR_lo": pos.wilson_lo, "TPR_hi": pos.wilson_hi, "n_pos": pos.runs,
                         "FPR": fpr, "FPR_lo": neg.wilson_lo, "FPR_hi": neg.wilson_hi, "n_neg": neg.runs,
                         "precision_at_50pct": prec, "F1_at_50pct": f1})
    return pd.DataFrame(rows)


def main():
    thr = pd.read_csv(OUT / "thresholds.csv")
    d_thr = float(thr[(thr.calibration == "matched") & (thr.env == "E2") & (thr.detector == "D_L3")].threshold.item())

    slow_neg = run("H1", "competitive", SLOW)
    slow_pos = run("H1", "collusive_tracking", SLOW)
    fp = int((slow_neg.D_L3 > d_thr).sum())
    h1a = [fp, len(slow_neg), fp / len(slow_neg), *wilson(fp, len(slow_neg))]
    h1_auc = aucs(slow_pos, slow_neg, "H1")

    pad_neg = run("H2", "competitive", PARAMS)
    pad_pos = run("H2", "collusive_cost_padding", PARAMS)
    h2_auc = aucs(pad_pos, pad_neg, "H2")

    h2_vals = {d: h2_auc[d]["pooled"][0] for d in ("B1", "B2", "B3", "D_L3")}
    criteria = {
        "H1a": {"rule": "slow competitors: FPR at frozen E2 D threshold <= 0.10", "threshold": d_thr,
                "value": h1a, "pass": bool(h1a[2] <= 0.10)},
        "H1b": {"rule": "slow tracking cartel vs slow competitors: pooled AUC(D) >= 0.80",
                "value": h1_auc["D_L3"]["pooled"], "pass": bool(h1_auc["D_L3"]["pooled"][0] >= 0.80)},
        "H2": {"rule": "cost-padding cartel: B1,B2,B3,D pooled AUC in [0.35,0.65]", "value": h2_vals,
               "pass": bool(all(0.35 <= v <= 0.65 for v in h2_vals.values()))},
        "H2_B0_report": {"pooled": h2_auc["B0"]["pooled"], "within": h2_auc["B0"]["within"]},
        "auc_detail": {"H1": h1_auc, "H2": h2_auc},
    }
    pd.concat([slow_neg, slow_pos, pad_neg, pad_pos], ignore_index=True).to_csv(OUT / "addendum2_scores.csv", index=False)
    (OUT / "addendum2_criteria.json").write_text(json.dumps(criteria, indent=2, default=float))
    ops = operating_points()
    ops.to_csv(OUT / "operating_points.csv", index=False)
    print(json.dumps({k: v for k, v in criteria.items() if k != "auc_detail"}, indent=1, default=float))
    print({t: {d: round(v["pooled"][0], 3) for d, v in a.items()} for t, a in criteria["auc_detail"].items()})
    print(ops[ops.detector.isin(["B0", "B1", "D_L3"])].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
