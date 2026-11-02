"""Entry point 2 of 2: turn results_v2/scores.csv into the paper's tables and checks.

    python -m experiments.v2_make_tables

Writes to results_v2/:
    auc.csv               pooled and within-cost-cell AUC with bootstrap 95% CIs
    rates.csv             flag rates at frozen thresholds (naive and matched calibration), Wilson CIs
    thresholds.csv        the frozen thresholds
    b0_by_cost_cell.csv   B0 flag rates by hidden cost cell (naive threshold)
    kill_criteria.json    K1-K5 as fixed in docs/V2_DESIGN.md
    fig1_auc_by_environment.png/.pdf, fig2_sensitivity.png/.pdf (fig 2 needs sensitivity.csv)
"""

import json
import sys
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluation.metrics import bootstrap_auc, threshold_95, wilson  # noqa: E402

RESULTS = ROOT / "results_v2"
DETECTORS = ["B0", "B1", "B2", "B3", "D_L2", "D_L3", "D_L3_mu020", "D_L3_mu030"]
INFO_LEVEL = {"B0": "L1", "B1": "L1", "B2": "L1", "B3": "L1", "D_L2": "L2", "D_L3": "L3",
              "D_L3_mu020": "L3 (mu -20%)", "D_L3_mu030": "L3 (mu +20%)"}
N_BOOT = 2000


def auc_table(scores):
    rows = []
    test = scores[(scores.split == "test") & (scores.cost_mode == "grid")]
    for env, env_df in test.groupby("env"):
        neg = env_df[env_df.conduct == "competitive"]
        for positive in sorted(set(env_df.conduct) - {"competitive"}):
            pos = env_df[env_df.conduct == positive]
            for k, det in enumerate(DETECTORS):
                seed = zlib.crc32(f"{env}|{positive}|{det}".encode())  # deterministic across runs
                pooled = bootstrap_auc(pos[det], neg[det], pos.cost_cell.values, neg.cost_cell.values,
                                       n_boot=N_BOOT, seed=seed)
                within = bootstrap_auc(pos[det], neg[det], pos.cost_cell.values, neg.cost_cell.values,
                                       n_boot=N_BOOT, seed=seed + 1, within=True)
                rows.append({"env": env, "positive": positive, "detector": det, "info": INFO_LEVEL[det],
                             "n_pos": len(pos), "n_neg": len(neg),
                             "auc_pooled": pooled[0], "pooled_lo": pooled[1], "pooled_hi": pooled[2],
                             "auc_within": within[0], "within_lo": within[1], "within_hi": within[2],
                             "confounding": within[0] - pooled[0]})
    return pd.DataFrame(rows)


def thresholds(scores):
    rows = []
    naive = scores[(scores.split == "calibration") & (scores.cost_mode == "naive")]
    for det in DETECTORS:
        rows.append({"calibration": "naive", "env": "E0 (c=1)", "detector": det,
                     "threshold": threshold_95(naive[det]), "n_calibration": len(naive)})
    matched = scores[(scores.split == "calibration") & (scores.cost_mode == "grid")]
    for env, df in matched.groupby("env"):
        for det in DETECTORS:
            rows.append({"calibration": "matched", "env": env, "detector": det,
                         "threshold": threshold_95(df[det]), "n_calibration": len(df)})
    return pd.DataFrame(rows)


def rate_table(scores, thr):
    rows = []
    test = scores[scores.split == "test"]
    for (env, conduct, mode), df in test.groupby(["env", "conduct", "cost_mode"]):
        for det in DETECTORS:
            for cal in ("naive", "matched"):
                key = "E0 (c=1)" if cal == "naive" else env
                t = thr[(thr.calibration == cal) & (thr.env == key) & (thr.detector == det)].threshold.item()
                flagged = int((df[det] > t).sum())
                lo, hi = wilson(flagged, len(df))
                rows.append({"env": env, "conduct": conduct, "cost_mode": mode, "detector": det,
                             "calibration": cal, "threshold": t, "runs": len(df), "flagged": flagged,
                             "rate": flagged / len(df), "wilson_lo": lo, "wilson_hi": hi,
                             "metric": "FPR" if conduct == "competitive" else "TPR"})
    return pd.DataFrame(rows)


def b0_by_cost_cell(scores, thr):
    t = thr[(thr.calibration == "naive") & (thr.detector == "B0")].threshold.item()
    test = scores[(scores.split == "test") & (scores.cost_mode == "grid")]
    rows = []
    for (env, conduct, c_mean, gap), df in test.groupby(["env", "conduct", "cost_mean", "cost_gap"]):
        flagged = int((df.B0 > t).sum())
        lo, hi = wilson(flagged, len(df))
        rows.append({"env": env, "conduct": conduct, "cost_mean": c_mean, "cost_gap": gap, "runs": len(df),
                     "flagged": flagged, "rate": flagged / len(df), "wilson_lo": lo, "wilson_hi": hi,
                     "mean_B0": df.B0.mean()})
    return pd.DataFrame(rows)


def kill_criteria(auc, rates):
    def get(env, positive, det, col="auc_pooled"):
        return float(auc[(auc.env == env) & (auc.positive == positive) & (auc.detector == det)][col].item())

    k1 = get("E2", "collusive_tracking", "D_L3")
    k2 = {"E0": get("E0", "collusive_rigid", "D_L3"), "E1": get("E1", "collusive_rigid", "D_L3")}
    k3 = get("E0", "collusive_rigid", "B0", "auc_within") - get("E0", "collusive_rigid", "B0")
    k4 = get("E3", "collusive_tracking", "D_L3") - get("E3", "collusive_tracking", "D_L2")
    naive_fpr = rates[(rates.env == "E0") & (rates.conduct == "competitive") & (rates.cost_mode == "naive")
                      & (rates.detector == "B0") & (rates.calibration == "naive")].iloc[0]
    return {
        "K1": {"rule": "E2 L3 pooled AUC(D) tracking vs competitive >= 0.80", "value": k1, "pass": k1 >= 0.80},
        "K2": {"rule": "E0 and E1 L3 pooled AUC(D) rigid vs competitive <= 0.65", "value": k2,
               "pass": all(v <= 0.65 for v in k2.values())},
        "K3": {"rule": "E0 within-cell minus pooled AUC(B0), rigid vs competitive >= 0.10", "value": k3,
               "pass": k3 >= 0.10},
        "K4": {"rule": "E3 AUC(D,L3) - AUC(D,L2), tracking >= 0.10", "value": k4, "pass": k4 >= 0.10},
        "K5_naive_B0_fpr": {"rule": "naive-baseline B0 test FPR Wilson CI contains 0.05",
                            "value": [naive_fpr.rate, naive_fpr.wilson_lo, naive_fpr.wilson_hi],
                            "pass": bool(naive_fpr.wilson_lo <= 0.05 <= naive_fpr.wilson_hi)},
    }


def main():
    scores = pd.read_csv(RESULTS / "scores.csv")
    auc = auc_table(scores)
    thr = thresholds(scores)
    rates = rate_table(scores, thr)
    b0 = b0_by_cost_cell(scores, thr)
    kills = kill_criteria(auc, rates)
    auc.to_csv(RESULTS / "auc.csv", index=False)
    thr.to_csv(RESULTS / "thresholds.csv", index=False)
    rates.to_csv(RESULTS / "rates.csv", index=False)
    b0.to_csv(RESULTS / "b0_by_cost_cell.csv", index=False)
    (RESULTS / "kill_criteria.json").write_text(json.dumps(kills, indent=2, default=float))
    from experiments.v2_figures import make_figures  # noqa: E402
    make_figures(RESULTS)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    print(auc.round(3).to_string(index=False))
    print(json.dumps(kills, indent=2, default=float))


if __name__ == "__main__":
    main()
