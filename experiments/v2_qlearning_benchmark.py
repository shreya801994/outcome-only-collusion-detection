"""Addendum 7: Calvano et al. (2020) Q-learning benchmark (rules in docs/V2_ADDENDUM_7_QLEARNING.md).

    python -m experiments.v2_qlearning_benchmark

Fresh seeds (base 20261109).  Writes new files only:
    results_v2/addendum7_sessions.csv, addendum7_metrics.csv, addendum7_criteria.json
"""
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

from detectors import adjustment_test, classic_screens as cs, cost_coverage  # noqa: E402
from evaluation.metrics import bootstrap_auc, wilson  # noqa: E402
from experiments.v2_run_all import score_runs  # noqa: E402
from simulator.equilibrium import shares  # noqa: E402
from simulator.qlearning import play, profit_gain, train  # noqa: E402

BASE_SEED = 20261109
OUT = ROOT / "results_v2"
COSTS = (0.85, 1.00, 1.15)
PER_COST = 50
T_OBS, TREMBLE = 300, 0.01
N_PROBES, WINDOW, MIN_GAP = 5, (80, 280), 15
OPTION_B_FROZEN = 1.4479041375946575  # addendum-4 threshold (scripted fast competitors)
ARMS = {"QC": 0.95, "QM": 0.0, "QM_cal": 0.0}
N_BOOT = 2000


def rng(label):
    return np.random.default_rng(np.random.SeedSequence(BASE_SEED, spawn_key=(zlib.crc32(label.encode()),)))


def _train(arm):
    c = np.repeat(COSTS, PER_COST)
    t0 = time.time()
    res = train(c, np.full(len(c), ARMS[arm]), rng(f"train|{arm}"))
    res["seconds"] = time.time() - t0
    return arm, res


def schedule(n):
    g = rng("probe-schedule")
    times = np.empty((n, N_PROBES), int)
    for r in range(n):
        while True:
            t = np.sort(g.choice(np.arange(WINDOW[0], WINDOW[1] + 1), N_PROBES, replace=False))
            if np.all(np.diff(t) >= MIN_GAP):
                break
        times[r] = t
    steps = g.integers(1, 5, size=(n, N_PROBES))
    return times, steps


def observe(res, forced=None):
    # identical tremble draws for session r in every arm (shared stream "obs")
    return play(res, res["state"], T_OBS, rng("obs"), TREMBLE, forced)


def punished_share(res, horizon=10):
    """Forced one-period deviation of firm 1 to its one-shot best response at tau = 0."""
    S, m = res["grid"].shape
    sidx = np.arange(S)
    acts0, _ = play(res, res["state"], 50)
    st = acts0[:, -1, 0] * m + acts0[:, -1, 1]
    rival = res["greedy"][1, sidx, st]
    br = res["prof"][sidx, :, rival, 0].argmax(axis=1)
    forced = np.full((S, horizon), -1)
    forced[:, 0] = br
    base_a, base_p = play(res, st, horizon)
    dev_a, dev_p = play(res, st, horizon, forced=forced)
    return dev_p[:, 1, 1] < base_p[:, 1, 1] - 1e-12, br != base_a[:, 0, 0]


def screens(res, ref, times, steps):
    acts, price = observe(res)
    S, m = res["grid"].shape
    sidx = np.arange(S)
    s1, s2, _ = shares(price[:, :, 0], price[:, :, 1], 2.0, 2.0, 0.0, 0.25)
    q = np.stack([s1, s2], axis=-1)
    msize = np.ones(price.shape[:2])
    df = score_runs({"price": price, "quantity": q, "market_size": msize})[["B0", "B1", "B2", "B3", "D_L3"]]
    ob = [adjustment_test.score_run(price[r], q[r], msize[r]) for r in range(S)]
    df["Score_B"] = [o["score_ac1"] for o in ob]
    df["BC_belal_coverage"] = [cost_coverage.score_run(price[r], q[r], msize[r])["score"] for r in range(S)]
    p = price[:, 50:, :]
    df["V1_cv"] = [cs.cv_screen(p[r]) for r in range(S)]
    df["V2_sd_change"] = [cs.sd_change_screen(p[r]) for r in range(S)]
    df["V3_ks"] = [cs.ks_screen(p[r], ref) for r in range(S)]
    # upward probe: firm 1 forced k grid steps above its intended action for one period
    forced = np.full((S, T_OBS), -1)
    intended = acts[:, :, 0]
    for r in range(S):
        for t, k in zip(times[r], steps[r]):
            forced[r, t] = min(intended[r, t] + k, m - 1)
    pacts, pprice = observe(res, forced)
    idx = sidx[:, None]
    disp = pprice[idx, times, 0] - price[idx, times, 0]
    ok = disp > 1e-12
    after_p, after_u = pprice[idx, times + 1, 1], price[idx, times + 1, 1]
    before = np.stack([pprice[idx, times - k, 1] for k in range(1, 6)], -1).mean(-1)
    with np.errstate(invalid="ignore", divide="ignore"):
        rn = np.where(ok, (after_p - before) / disp, np.nan)
        rc = np.where(ok, (after_p - after_u) / disp, np.nan)
    df["R_naive"], df["R_causal"] = np.nanmean(rn, 1), np.nanmean(rc, 1)
    df["Score_P"], df["Score_Pc"] = -df.R_naive, -df.R_causal
    df["mean_price"] = p.mean(axis=(1, 2))
    return df


STATS = ["B0", "B1", "B2", "B3", "D_L3", "Score_B", "BC_belal_coverage", "V1_cv", "V2_sd_change", "V3_ks",
         "Score_P", "Score_Pc"]


def main():
    t0 = time.time()
    with Pool(2) as pool:
        trained = dict(pool.map(_train, list(ARMS)))
    print({a: (round(r["seconds"]), r["periods_run"], float(r["converged"].mean())) for a, r in trained.items()},
          flush=True)
    n = len(trained["QC"]["c"])
    times, steps = schedule(n)
    _, cal_price = observe(trained["QM_cal"])
    ref = cs.reference_changes(cal_price[:, 50:, :])
    sess, sc = [], {}
    for arm, res in trained.items():
        d, _ = profit_gain(res)
        pun, moved = punished_share(res)
        df = screens(res, ref, times, steps)
        df["arm"], df["cost"], df["delta_gain"] = arm, res["c"], d
        df["converged"], df["t_converged"] = res["converged"], res["t_converged"]
        df["punished_after_deviation"], df["deviation_changes_action"] = pun, moved
        df["cost_cell"] = np.searchsorted(COSTS, res["c"])
        sc[arm] = df
        sess.append(df)
        print(arm, "scored", f"{time.time() - t0:.0f}s", flush=True)
    allsc = pd.concat(sess, ignore_index=True)
    allsc.to_csv(OUT / "addendum7_sessions.csv", index=False)

    rows = []
    for s in STATS:
        thr = float(np.nanpercentile(sc["QM_cal"][s], 95))
        pos, neg = sc["QC"], sc["QM"]
        seed = zlib.crc32(f"add7|{s}".encode())
        pooled = bootstrap_auc(pos[s].fillna(0), neg[s].fillna(0), pos.cost_cell.values, neg.cost_cell.values,
                               N_BOOT, seed)
        within = bootstrap_auc(pos[s].fillna(0), neg[s].fillna(0), pos.cost_cell.values, neg.cost_cell.values,
                               N_BOOT, seed + 1, within=True)
        tp, fp = int((pos[s] > thr).sum()), int((neg[s] > thr).sum())
        rows.append({"screen": s, "threshold_QM_cal": thr, "auc_pooled": pooled[0], "auc_lo": pooled[1],
                     "auc_hi": pooled[2], "auc_within": within[0], "TPR": tp / len(pos), "FPR": fp / len(neg),
                     "FPR_lo": wilson(fp, len(neg))[0], "FPR_hi": wilson(fp, len(neg))[1]})
    met = pd.DataFrame(rows)
    met.to_csv(OUT / "addendum7_metrics.csv", index=False)

    v = sc["QC"][sc["QC"].cost == 1.0]
    crit = {
        "V1": {"rule": "mean Delta (QC, c = 1) in [0.80, 0.90]", "value": float(v.delta_gain.mean()),
               "se": float(v.delta_gain.std(ddof=1) / np.sqrt(len(v))),
               "pass": bool(0.80 <= v.delta_gain.mean() <= 0.90)},
        "V2": {"rule": "convergence rate (QC, c = 1) >= 0.90", "value": float(v.converged.mean()),
               "pass": bool(v.converged.mean() >= 0.90)},
        "V3": {"rule": "share of QC (c = 1) sessions in which the rival's price falls after a forced deviation >= 0.80",
               "value": float(v.punished_after_deviation.mean()), "pass": bool(v.punished_after_deviation.mean() >= 0.80)},
        "report_only": {
            "Delta_by_arm_cost": allsc.groupby(["arm", "cost"]).delta_gain.mean().round(4).to_dict().__repr__(),
            "median_t_converged": allsc.groupby("arm").t_converged.median().to_dict(),
            "convergence_rate": allsc.groupby("arm").converged.mean().to_dict(),
            "mean_price_by_arm_cost": allsc.groupby(["arm", "cost"]).mean_price.mean().round(4).to_dict().__repr__(),
            "OptionB_FPR_myopic_at_addendum4_threshold": float((sc["QM"].Score_B > OPTION_B_FROZEN).mean()),
            "OptionB_TPR_collusive_at_addendum4_threshold": float((sc["QC"].Score_B > OPTION_B_FROZEN).mean()),
            "share_R_causal_negative": {a: float((sc[a].R_causal < 0).mean()) for a in sc},
            "share_R_naive_negative": {a: float((sc[a].R_naive < 0).mean()) for a in sc},
        },
        "runtime_seconds": round(time.time() - t0, 1),
    }
    (OUT / "addendum7_criteria.json").write_text(json.dumps(crit, indent=2, default=float))
    pd.set_option("display.width", 200)
    print(met.round(3).to_string(index=False))
    print(json.dumps(crit, indent=1, default=float))


if __name__ == "__main__":
    main()
