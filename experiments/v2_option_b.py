"""Addendum 4: Option B (rules frozen in docs/V2_ADDENDUM_4_OPTION_B.md).

    python -m experiments.v2_option_b            # primary + report-only analyses
    python -m experiments.v2_option_b --no-mu    # skip the (slow) mu-estimated variant

Fresh seeds (base 20261107).  Threshold frozen from the stored main-design E2 calibration
split (base 20261102).  Writes new files only:
    results_v2/addendum4_scores.csv, addendum4_metrics.csv, addendum4_criteria.json
"""
import argparse
import json
import sys
import time
import zlib
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from detectors.adjustment_test import score_run  # noqa: E402
from evaluation.metrics import bootstrap_auc, wilson  # noqa: E402
from experiments.v2_hard_negatives import SLOW  # noqa: E402
from experiments.v2_run_all import COST_GAPS, COST_MEANS, PARAMS, PERIODS, score_runs  # noqa: E402
from simulator.batch_sim import auditor_view, simulate_batch  # noqa: E402
from simulator.demand_shocks import ENVIRONMENTS, simulate_shocks  # noqa: E402

BASE_SEED = 20261107
RUNS_PER_COST_CELL = 30
N_BOOT = 2000
OUT = ROOT / "results_v2"
MU_GRID = np.round(np.arange(0.15, 0.3501, 0.025), 4)
STATS = {"score_ac1": "Score_B (primary: lag-1 residual autocorrelation)",
         "score": "secondary: -t of gamma+beta", "score_bp": "secondary: Box-Pierce(5)"}
D_THRESHOLD = 0.05346  # frozen main-design E2 matched threshold for D_L3 (results_v2/thresholds.csv)


def grid():
    rows, cells = [], []
    for i, m in enumerate(COST_MEANS):
        for j, g in enumerate(COST_GAPS):
            rows += [(m - g / 2, m + g / 2)] * RUNS_PER_COST_CELL
            cells += [i * len(COST_GAPS) + j] * RUNS_PER_COST_CELL
    return np.array(rows), np.array(cells)


def streams(label):
    return np.random.SeedSequence(BASE_SEED, spawn_key=(zlib.crc32(f"B|{label}".encode()),)).spawn(4)


def simulate(label, conduct, params, costs):
    s = streams(label)
    a, q = simulate_shocks(np.random.default_rng(s[0]), len(costs), PERIODS, ENVIRONMENTS["E2"])
    return simulate_batch(costs, a, q, conduct, params, *(np.random.default_rng(x) for x in s[1:]))


def _score(args):
    price, quantity, msize, est_mu = args
    if est_mu:
        return score_run(price, quantity, msize, estimate_mu=True, mu_grid=MU_GRID)
    return score_run(price, quantity, msize)


def score_all(price, quantity, msize, est_mu=False, pool=None):
    jobs = [(price[r], quantity[r], msize[r], est_mu) for r in range(len(price))]
    return pd.DataFrame(pool.map(_score, jobs, chunksize=4))


def frame(arm, res, costs, cells, pool, est_mu=False, add_d=True):
    sc = score_all(res["price"], res["quantity"], res["market_size"], est_mu, pool)
    sc["arm"], sc["cost_cell"] = arm, cells
    sc["cost_1"], sc["cost_2"] = costs[:, 0], costs[:, 1]
    if "adjust_speed" in res:
        sc["lambda_1"], sc["lambda_2"] = res["adjust_speed"][:, 0], res["adjust_speed"][:, 1]
    if add_d:
        view = {k: res[k] for k in ("price", "quantity", "market_size")}
        sc["D_L3"] = score_runs(auditor_view(view, "L3"))["D_L3"].to_numpy()
    return sc


def stored(name):
    z = np.load(ROOT / "data_v2" / f"{name}.npz")
    return {k: z[k].astype(float) if z[k].dtype.kind == "f" else z[k] for k in z.files}


def metrics(pos, neg, stat, thr, tag):
    seed = zlib.crc32(f"add4|{tag}|{stat}".encode())
    pooled = bootstrap_auc(pos[stat], neg[stat], pos.cost_cell.values, neg.cost_cell.values, N_BOOT, seed)
    within = bootstrap_auc(pos[stat], neg[stat], pos.cost_cell.values, neg.cost_cell.values, N_BOOT, seed + 1,
                           within=True)
    tp, fp = int((pos[stat] > thr).sum()), int((neg[stat] > thr).sum())
    return {"contrast": tag, "statistic": stat, "threshold": thr, "n_pos": len(pos), "n_neg": len(neg),
            "auc_pooled": pooled[0], "auc_pooled_lo": pooled[1], "auc_pooled_hi": pooled[2],
            "auc_within": within[0], "auc_within_lo": within[1], "auc_within_hi": within[2],
            "TPR": tp / len(pos), "TPR_lo": wilson(tp, len(pos))[0], "TPR_hi": wilson(tp, len(pos))[1],
            "FPR": fp / len(neg), "FPR_lo": wilson(fp, len(neg))[0], "FPR_hi": wilson(fp, len(neg))[1]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-mu", action="store_true")
    args = ap.parse_args()
    t0 = time.time()
    costs, cells = grid()
    with Pool(2) as pool:
        # calibration: stored main-design E2 fast competitors (threshold source)
        cal = stored("calibration_E2_competitive_grid")
        cal_sc = frame("CAL_fast_comp", cal, cal["cost"], cal["cost_cell"], pool, add_d=False)
        thr = {s: float(np.percentile(cal_sc[s], 95)) for s in STATS}
        print("frozen thresholds:", thr, flush=True)

        arms = {"CAL_fast_comp": cal_sc}
        for arm, conduct in [("SC", "competitive"), ("SR", "collusive_rigid"), ("ST", "collusive_tracking")]:
            arms[arm] = frame(arm, simulate(arm, conduct, SLOW, costs), costs, cells, pool)
            print(f"{arm} scored ({time.time() - t0:.0f}s)", flush=True)
        cp = simulate("CP", "collusive_cost_padding", PARAMS, costs)
        arms["CP"] = frame("CP", cp, costs, cells, pool)
        twin_costs = costs + cp["cost_pad"][:, None]
        s = streams("CP")  # coupled: identical streams to CP
        a, q = simulate_shocks(np.random.default_rng(s[0]), len(costs), PERIODS, ENVIRONMENTS["E2"])
        twin = simulate_batch(twin_costs, a, q, "competitive", PARAMS, *(np.random.default_rng(x) for x in s[1:]))
        arms["CP_twin"] = frame("CP_twin", twin, twin_costs, cells, pool)
        twin_max_diff = float(np.abs(cp["price"] - twin["price"]).max())
        for arm, conduct in [("TEST_fast_comp", "competitive"), ("TEST_fast_rigid", "collusive_rigid"),
                             ("TEST_fast_tracking", "collusive_tracking")]:
            z = stored(f"test_E2_{conduct}_grid")
            arms[arm] = frame(arm, z, z["cost"], z["cost_cell"], pool)
        print(f"primary scoring done ({time.time() - t0:.0f}s)", flush=True)

        mu_rows = {}
        if not args.no_mu:
            mu_rows["CAL_fast_comp"] = frame("CAL_fast_comp", cal, cal["cost"], cal["cost_cell"], pool, True, False)
            for arm, conduct in [("SC", "competitive"), ("SR", "collusive_rigid")]:
                mu_rows[arm] = frame(arm, simulate(arm, conduct, SLOW, costs), costs, cells, pool, True, False)
                print(f"mu-estimated {arm} ({time.time() - t0:.0f}s)", flush=True)

    allsc = pd.concat(arms.values(), ignore_index=True)
    allsc.to_csv(OUT / "addendum4_scores.csv", index=False)

    rows = []
    for stat in STATS:
        for tag, p, n in [("SR vs SC", "SR", "SC"), ("ST vs SC", "ST", "SC"), ("CP vs CP_twin", "CP", "CP_twin"),
                          ("CP vs SC", "CP", "SC"), ("fast rigid vs fast comp (test)", "TEST_fast_rigid", "TEST_fast_comp"),
                          ("fast tracking vs fast comp (test)", "TEST_fast_tracking", "TEST_fast_comp"),
                          ("SC vs fast comp (test) [dynamics contrast]", "SC", "TEST_fast_comp")]:
            rows.append(metrics(arms[p], arms[n], stat, thr[stat], tag))
    for tag, p, n in [("SR vs SC", "SR", "SC"), ("ST vs SC", "ST", "SC"), ("CP vs CP_twin", "CP", "CP_twin"),
                      ("SC vs fast comp (test) [dynamics contrast]", "SC", "TEST_fast_comp")]:
        rows.append(metrics(arms[p], arms[n], "D_L3", D_THRESHOLD, tag))
    mu_info = {}
    if mu_rows:
        thr_mu = float(np.percentile(mu_rows["CAL_fast_comp"]["score_ac1"], 95))
        m = metrics(mu_rows["SR"], mu_rows["SC"], "score_ac1", thr_mu, "SR vs SC (mu estimated)")
        rows.append(m)
        mu_info = {"threshold": thr_mu, "auc_pooled": m["auc_pooled"], "FPR_SC": m["FPR"], "TPR_SR": m["TPR"],
                   "mu_hat_median": {k: float(v.mu_hat.median()) for k, v in mu_rows.items()},
                   "mu_hat_iqr": {k: [float(v.mu_hat.quantile(0.25)), float(v.mu_hat.quantile(0.75))]
                                  for k, v in mu_rows.items()}}
        pd.concat(mu_rows.values(), ignore_index=True).to_csv(OUT / "addendum4_scores_mu_estimated.csv", index=False)
    met = pd.DataFrame(rows)
    met.to_csv(OUT / "addendum4_metrics.csv", index=False)

    prim = met[(met.statistic == "score_ac1") & (met.contrast == "SR vs SC")].iloc[0]
    fpr_fast = float((arms["TEST_fast_comp"].score_ac1 > thr["score_ac1"]).mean())

    def est(arm):
        d = arms[arm]
        return {"c_abs_err_median": float(np.median(np.abs(np.r_[d.c_hat_1 - d.cost_1, d.c_hat_2 - d.cost_2]))),
                "lambda_corr": float(np.corrcoef(np.r_[d.lambda_hat_1, d.lambda_hat_2],
                                                 np.r_[d.lambda_1, d.lambda_2])[0, 1]),
                "lambda_err_median": float(np.median(np.r_[d.lambda_hat_1 - d.lambda_1, d.lambda_hat_2 - d.lambda_2]))}

    criteria = {
        "kill_criterion": "stop if, after estimating adjustment speed, AUC(slow cartel vs slow competitors) < 0.90 "
                          "or FPR at a frozen threshold > 0.10",
        "threshold_score_B": thr["score_ac1"],
        "B1": {"rule": "AUC(Score_B) SR vs SC >= 0.90",
               "value": [prim.auc_pooled, prim.auc_pooled_lo, prim.auc_pooled_hi], "pass": bool(prim.auc_pooled >= 0.90)},
        "B2": {"rule": "FPR of SC at frozen Score_B threshold <= 0.10",
               "value": [prim.FPR, prim.FPR_lo, prim.FPR_hi], "pass": bool(prim.FPR <= 0.10)},
        "kill_triggered": bool(not (prim.auc_pooled >= 0.90 and prim.FPR <= 0.10)),
        "report_only": {"FPR_fast_test_competitors": fpr_fast,
                        "CP_twin_max_price_difference": twin_max_diff,
                        "estimation_accuracy": {a: est(a) for a in ["SC", "TEST_fast_comp", "SR"]},
                        "mu_estimated_variant": mu_info},
        "runtime_seconds": round(time.time() - t0, 1),
    }
    (OUT / "addendum4_criteria.json").write_text(json.dumps(criteria, indent=2))
    pd.set_option("display.width", 220)
    print(met[["contrast", "statistic", "threshold", "auc_pooled", "auc_pooled_lo", "auc_pooled_hi", "auc_within",
               "TPR", "FPR"]].round(3).to_string(index=False))
    print(json.dumps({k: criteria[k] for k in ["threshold_score_B", "B1", "B2", "kill_triggered"]}, indent=1))
    print(json.dumps(criteria["report_only"], indent=1))


if __name__ == "__main__":
    main()
