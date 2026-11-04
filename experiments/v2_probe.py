"""Addendum 6: Belal's upward price probe on our agents (rules in docs/V2_ADDENDUM_6_PROBE.md).

    python -m experiments.v2_probe

Fresh seeds (base 20261108).  Writes new files only:
    results_v2/addendum6_scores.csv, addendum6_metrics.csv, addendum6_criteria.json
"""
import json
import sys
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluation.metrics import bootstrap_auc, wilson  # noqa: E402
from experiments.v2_hard_negatives import SLOW  # noqa: E402
from experiments.v2_run_all import COST_GAPS, COST_MEANS, PARAMS, PERIODS  # noqa: E402
from simulator.batch_sim import simulate_batch  # noqa: E402
from simulator.demand_shocks import ENVIRONMENTS, simulate_shocks  # noqa: E402

BASE_SEED = 20261108
OUT = ROOT / "results_v2"
N_BOOT = 2000
N_PROBES, SIZES, WINDOW, MIN_GAP = 5, np.array([0.04, 0.08, 0.12, 0.16]), (80, 280), 15
ARMS = {"CAL": ("competitive", PARAMS), "FC": ("competitive", PARAMS), "SC": ("competitive", SLOW),
        "FR": ("collusive_rigid", PARAMS), "SR": ("collusive_rigid", SLOW),
        "FT": ("collusive_tracking", PARAMS), "ST": ("collusive_tracking", SLOW),
        "NT": ("competitive_nash", PARAMS), "CP": ("collusive_cost_padding", PARAMS)}


def grid():
    rows, cells = [], []
    for i, m in enumerate(COST_MEANS):
        for j, g in enumerate(COST_GAPS):
            rows += [(m - g / 2, m + g / 2)] * 30
            cells += [i * len(COST_GAPS) + j] * 30
    return np.array(rows), np.array(cells)


def schedule(n_runs):
    rng = np.random.default_rng(np.random.SeedSequence(BASE_SEED, spawn_key=(zlib.crc32(b"probe-schedule"),)))
    times = np.empty((n_runs, N_PROBES), int)
    for r in range(n_runs):
        while True:
            t = np.sort(rng.choice(np.arange(WINDOW[0], WINDOW[1] + 1), N_PROBES, replace=False))
            if np.all(np.diff(t) >= MIN_GAP):
                break
        times[r] = t
    sizes = rng.choice(SIZES, size=(n_runs, N_PROBES))
    mandate = np.zeros((n_runs, PERIODS))
    for r in range(n_runs):
        mandate[r, times[r]] = sizes[r]
    return times, sizes, mandate


def run(arm, env, costs, mandate, key_arm=None):
    conduct, params = ARMS[arm] if arm in ARMS else ("competitive", PARAMS)
    s = np.random.SeedSequence(BASE_SEED, spawn_key=(zlib.crc32(f"P|{env}|{key_arm or arm}".encode()),)).spawn(4)
    a, q = simulate_shocks(np.random.default_rng(s[0]), len(costs), PERIODS, ENVIRONMENTS[env])
    return simulate_batch(costs, a, q, conduct, params, *(np.random.default_rng(x) for x in s[1:]), mandate=mandate)


def responses(probed, unprobed, times, sizes):
    p2, u2 = probed["price"][:, :, 1], unprobed["price"][:, :, 1]
    idx = np.arange(len(times))[:, None]
    after = p2[idx, times + 1]
    before = np.stack([p2[idx, times - k] for k in range(1, 6)], axis=-1).mean(-1)
    naive = ((after - before) / sizes).mean(1)
    causal = ((after - u2[idx, times + 1]) / sizes).mean(1)
    return naive, causal


def metrics(pos, neg, stat, thr, tag):
    seed = zlib.crc32(f"add6|{tag}|{stat}".encode())
    pooled = bootstrap_auc(pos[stat], neg[stat], pos.cost_cell.values, neg.cost_cell.values, N_BOOT, seed)
    within = bootstrap_auc(pos[stat], neg[stat], pos.cost_cell.values, neg.cost_cell.values, N_BOOT, seed + 1,
                           within=True)
    tp, fp = int((pos[stat] > thr).sum()), int((neg[stat] > thr).sum())
    return {"contrast": tag, "statistic": stat, "threshold": thr, "auc_pooled": pooled[0], "auc_lo": pooled[1],
            "auc_hi": pooled[2], "auc_within": within[0], "TPR": tp / len(pos), "FPR": fp / len(neg),
            "FPR_lo": wilson(fp, len(neg))[0], "FPR_hi": wilson(fp, len(neg))[1]}


def main():
    costs, cells = grid()
    times, sizes, mandate = schedule(len(costs))
    frames, checks = {}, {}
    for env in ["E2", "E0"]:
        for arm in list(ARMS) + ["CP_twin"]:
            if arm == "CP_twin":
                cp = frames[(env, "CP")]["_res"]
                c_twin = costs + cp["cost_pad"][:, None]
                pr = run("CP_twin", env, c_twin, mandate, key_arm="CP")
                un = run("CP_twin", env, c_twin, None, key_arm="CP")
                checks[f"{env}_twin_max_abs_price_diff_probed"] = float(np.abs(pr["price"] - cp["price"]).max())
            else:
                pr, un = run(arm, env, costs, mandate), run(arm, env, costs, None)
            naive, causal = responses(pr, un, times, sizes)
            df = pd.DataFrame({"env": env, "arm": arm, "cost_cell": cells, "R_naive": naive, "R_causal": causal,
                               "Score_P": -naive, "Score_Pc": -causal})
            frames[(env, arm)] = {"df": df, "_res": pr}
        print(env, "simulated", flush=True)
    scores = pd.concat([v["df"] for v in frames.values()], ignore_index=True)
    scores.to_csv(OUT / "addendum6_scores.csv", index=False)

    rows, thr = [], {}
    for env in ["E2", "E0"]:
        cal = frames[(env, "CAL")]["df"]
        thr[env] = {s: float(np.percentile(cal[s], 95)) for s in ["Score_P", "Score_Pc"]}
        g = lambda a: frames[(env, a)]["df"]  # noqa: E731
        for tag, p, n in [("SR vs SC", "SR", "SC"), ("ST vs SC", "ST", "SC"), ("FR vs FC", "FR", "FC"),
                          ("FT vs FC", "FT", "FC"), ("NT vs FC", "NT", "FC"), ("CP vs CP_twin", "CP", "CP_twin"),
                          ("CP vs FC", "CP", "FC"), ("SC vs FC [dynamics contrast]", "SC", "FC")]:
            for s in ["Score_P", "Score_Pc"]:
                rows.append({"env": env, **metrics(g(p), g(n), s, thr[env][s], tag)})
    met = pd.DataFrame(rows)
    met.to_csv(OUT / "addendum6_metrics.csv", index=False)

    def m(env, tag, stat):
        return met[(met.env == env) & (met.contrast == tag) & (met.statistic == stat)].iloc[0]

    p1, p3n, p3c = m("E2", "SR vs SC", "Score_P"), m("E2", "CP vs CP_twin", "Score_P"), m("E2", "CP vs CP_twin", "Score_Pc")
    cp_df, tw_df = frames[("E2", "CP")]["df"], frames[("E2", "CP_twin")]["df"]
    share_neg = {f"{env}|{arm}": {"naive": float((frames[(env, arm)]["df"].R_naive < 0).mean()),
                                  "causal": float((frames[(env, arm)]["df"].R_causal < 0).mean()),
                                  "causal_eq_0": float((np.abs(frames[(env, arm)]["df"].R_causal) < 1e-12).mean())}
                 for env in ["E2", "E0"] for arm in list(ARMS) + ["CP_twin"]}
    criteria = {
        "thresholds": thr,
        "P1": {"rule": "AUC(Score_P) SR vs SC (E2) >= 0.90", "value": [p1.auc_pooled, p1.auc_lo, p1.auc_hi],
               "pass": bool(p1.auc_pooled >= 0.90)},
        "P2": {"rule": "FPR of SC at frozen Score_P threshold <= 0.10", "value": [p1.FPR, p1.FPR_lo, p1.FPR_hi],
               "pass": bool(p1.FPR <= 0.10)},
        "P3": {"rule": "CP vs CP_twin identical responses; AUC 0.500 for both statistics",
               "max_abs_response_diff": float(max(np.abs(cp_df.R_naive - tw_df.R_naive).max(),
                                                  np.abs(cp_df.R_causal - tw_df.R_causal).max())),
               "auc_naive": p3n.auc_pooled, "auc_causal": p3c.auc_pooled,
               "pass": bool(abs(p3n.auc_pooled - 0.5) < 1e-12 and abs(p3c.auc_pooled - 0.5) < 1e-12)},
        "share_R_negative": share_neg, "checks": checks,
    }
    (OUT / "addendum6_criteria.json").write_text(json.dumps(criteria, indent=2))
    pd.set_option("display.width", 220)
    print(met.round(3).to_string(index=False))
    print(json.dumps({k: criteria[k] for k in ["thresholds", "P1", "P2", "P3", "checks"]}, indent=1))
    print(pd.DataFrame(share_neg).T.round(3).to_string())


if __name__ == "__main__":
    main()
