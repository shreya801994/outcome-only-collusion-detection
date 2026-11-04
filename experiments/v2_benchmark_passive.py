"""Addendum 5: passive benchmark against published screens (rules in docs/V2_ADDENDUM_5_BENCHMARKS.md).

    python -m experiments.v2_benchmark_passive

No new random draws: every trajectory is either stored (data_v2/) or regenerated bit-for-bit
from the seeds of addenda 1-3 (checked by recomputing D_L3 against the stored score files).
Writes new files only: results_v2/addendum5_scores.csv, addendum5_metrics.csv, addendum5_checks.json
"""
import json
import sys
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from detectors import classic_screens as cs  # noqa: E402
from detectors import cost_coverage  # noqa: E402
from detectors import implied_cost  # noqa: E402
from evaluation.metrics import bootstrap_auc, wilson  # noqa: E402
from experiments import v2_confirm, v2_hard_negatives  # noqa: E402
from experiments.v2_hard_negatives import SLOW  # noqa: E402
from experiments.v2_run_all import BURN_IN, COST_GAPS, COST_MEANS, MU, PARAMS, PERIODS  # noqa: E402
from simulator.batch_sim import simulate_batch  # noqa: E402
from simulator.demand_shocks import ENVIRONMENTS, simulate_shocks  # noqa: E402

OUT = ROOT / "results_v2"
N_BOOT = 2000
SCREENS = ["V1_cv", "V2_sd_change", "V3_ks", "BC_belal_coverage"]


def regenerate(base_seed, key_str, conduct, params, env, means=COST_MEANS, costs=None):
    if costs is None:
        rows, cells = [], []
        for i, m in enumerate(means):
            for j, g in enumerate(COST_GAPS):
                rows += [(m - g / 2, m + g / 2)] * 30
                cells += [i * len(COST_GAPS) + j] * 30
        costs, cells = np.array(rows), np.array(cells)
    else:
        cells = None
    s = np.random.SeedSequence(base_seed, spawn_key=(zlib.crc32(key_str.encode()),)).spawn(4)
    a, q = simulate_shocks(np.random.default_rng(s[0]), len(costs), PERIODS, ENVIRONMENTS[env])
    res = simulate_batch(costs, a, q, conduct, params, *(np.random.default_rng(x) for x in s[1:]))
    res["cost"], res["cost_cell"] = costs, cells
    return res


def stored(name):
    z = np.load(ROOT / "data_v2" / f"{name}.npz")
    return {k: z[k] for k in z.files}


def d_l3(res):
    return implied_cost.score(res["price"][:, BURN_IN:, :].astype(float), res["quantity"][:, BURN_IN:, :].astype(float),
                              MU, market_size=res["market_size"][:, BURN_IN:].astype(float))


def score(res, reference):
    p = res["price"][:, BURN_IN:, :].astype(float)
    rows = []
    for r in range(p.shape[0]):
        bc = cost_coverage.score_run(res["price"][r].astype(float), res["quantity"][r].astype(float),
                                     res["market_size"][r].astype(float), MU, BURN_IN)
        rows.append({"V1_cv": cs.cv_screen(p[r]), "V2_sd_change": cs.sd_change_screen(p[r]),
                     "V3_ks": cs.ks_screen(p[r], reference), "BC_belal_coverage": bc["score"],
                     "BC_peak_1": bc["peak_1"], "BC_peak_2": bc["peak_2"]})
    df = pd.DataFrame(rows)
    df["D_L3"] = d_l3(res)
    df["cost_cell"] = res["cost_cell"]
    return df


def metrics(pos, neg, stat, thr, tag):
    seed = zlib.crc32(f"add5|{tag}|{stat}".encode())
    pooled = bootstrap_auc(pos[stat], neg[stat], pos.cost_cell.values, neg.cost_cell.values, N_BOOT, seed)
    within = bootstrap_auc(pos[stat], neg[stat], pos.cost_cell.values, neg.cost_cell.values, N_BOOT, seed + 1,
                           within=True)
    tp, fp = int((pos[stat] > thr).sum()), int((neg[stat] > thr).sum())
    return {"contrast": tag, "screen": stat, "threshold": thr, "n_pos": len(pos), "n_neg": len(neg),
            "auc_pooled": pooled[0], "auc_pooled_lo": pooled[1], "auc_pooled_hi": pooled[2],
            "auc_within": within[0], "TPR": tp / len(pos), "FPR": fp / len(neg),
            "FPR_lo": wilson(fp, len(neg))[0], "FPR_hi": wilson(fp, len(neg))[1]}


def main():
    checks, frames, rows = {}, [], []
    cal = {}
    for env in ["E0", "E1", "E2", "E3"]:
        c = stored(f"calibration_{env}_competitive_grid")
        ref = cs.reference_changes(c["price"][:, BURN_IN:, :])
        cal[env] = (ref, score(c, ref))
    thr = {env: {s: float(np.percentile(cal[env][1][s], 95)) for s in SCREENS + ["D_L3"]} for env in cal}
    checks["thresholds"] = thr

    def add(tag, env, pos, neg):
        for s in SCREENS + ["D_L3"]:
            rows.append(metrics(pos, neg, s, thr[env][s], tag))
        for name, df in (("pos", pos), ("neg", neg)):
            d = df.copy()
            d["contrast"], d["role"] = tag, name
            frames.append(d)

    # 1. main-design test split (stored)
    for env in ["E0", "E1", "E2", "E3"]:
        ref = cal[env][0]
        neg = score(stored(f"test_{env}_competitive_grid"), ref)
        for pos_c in (["collusive_rigid"] + (["collusive_tracking"] if env in ("E2", "E3") else [])):
            add(f"main {env}: {pos_c} vs competitive", env, score(stored(f"test_{env}_{pos_c}_grid"), ref), neg)
        print(env, "done", flush=True)

    ref2 = cal["E2"][0]
    a2 = pd.read_csv(OUT / "addendum2_scores.csv")
    a3 = pd.read_csv(OUT / "addendum3_scores.csv")
    # 2. addendum 2 (H1 slow tracking vs slow comp; H2 cost padding vs comp), regenerated
    regen = {}
    for tag, conduct, params in [("H1", "competitive", SLOW), ("H1", "collusive_tracking", SLOW),
                                 ("H2", "competitive", PARAMS), ("H2", "collusive_cost_padding", PARAMS)]:
        res = regenerate(v2_hard_negatives.BASE_SEED, f"{tag}|{conduct}", conduct, params, "E2")
        stored_d = a2[(a2.test == tag) & (a2.conduct == conduct)].D_L3.to_numpy()
        checks[f"regen_add2_{tag}_{conduct}_max_abs_D_diff"] = float(np.abs(d_l3(res) - stored_d).max())
        regen[(tag, conduct)] = res
    add("add2 H1: slow tracking vs slow competitive", "E2", score(regen[("H1", "collusive_tracking")], ref2),
        score(regen[("H1", "competitive")], ref2))
    cp = score(regen[("H2", "collusive_cost_padding")], ref2)
    add("add2 H2: cost padding vs competitive (true costs)", "E2", cp, score(regen[("H2", "competitive")], ref2))
    # twin of the cost-padding arm: competitive at c + m, coupled streams (as v2_check_padding_identity)
    cpres = regen[("H2", "collusive_cost_padding")]
    twin = regenerate(v2_hard_negatives.BASE_SEED, "H2|collusive_cost_padding", "competitive", PARAMS, "E2",
                      costs=cpres["cost"] + cpres["cost_pad"][:, None])
    twin["cost_cell"] = cpres["cost_cell"]
    checks["twin_max_abs_price_diff"] = float(np.abs(twin["price"] - cpres["price"]).max())
    add("twin: cost padding vs competitive at c+m (coupled)", "E2", cp, score(twin, ref2))
    # 3. addendum 3 (slow rigid vs slow comp), regenerated
    a3res = {}
    for conduct in ["competitive", "collusive_rigid"]:
        res = regenerate(20261106, f"S|{conduct}", conduct, SLOW, "E2")
        checks[f"regen_add3_{conduct}_max_abs_D_diff"] = float(np.abs(d_l3(res) - a3[a3.conduct == conduct].D_L3.to_numpy()).max())
        a3res[conduct] = score(res, ref2)
    add("add3: slow rigid vs slow competitive", "E2", a3res["collusive_rigid"], a3res["competitive"])
    # 4. confirmatory C1-C3, regenerated
    conf = pd.read_csv(OUT / "confirmatory.csv")
    for cell, spec in v2_confirm.CELLS.items():
        ref = cal[spec["env"]][0]
        sc = {}
        for role in ("positive", "negative"):
            conduct = spec[role]
            res = regenerate(v2_confirm.BASE_SEED, f"{cell}|{conduct}", conduct, spec["params"], spec["env"],
                             means=spec["means"])
            stored_d = conf[(conf.cell == cell) & (conf.conduct == conduct)].D_L3.to_numpy()
            checks[f"regen_{cell}_{conduct}_max_abs_D_diff"] = float(np.abs(d_l3(res) - stored_d).max())
            sc[role] = score(res, ref)
        add(f"confirm {cell}: {spec['positive']} vs {spec['negative']}", spec["env"], sc["positive"], sc["negative"])
        print(cell, "done", flush=True)

    pd.concat(frames, ignore_index=True).to_csv(OUT / "addendum5_scores.csv", index=False)
    met = pd.DataFrame(rows)
    met.to_csv(OUT / "addendum5_metrics.csv", index=False)
    (OUT / "addendum5_checks.json").write_text(json.dumps(checks, indent=2))
    pd.set_option("display.width", 250)
    piv = met.pivot_table(index="contrast", columns="screen", values="auc_pooled", sort=False).round(3)
    print("pooled AUC\n", piv.to_string())
    fpr = met.pivot_table(index="contrast", columns="screen", values="FPR", sort=False).round(3)
    print("FPR at frozen threshold\n", fpr.to_string())
    tpr = met.pivot_table(index="contrast", columns="screen", values="TPR", sort=False).round(3)
    print("TPR at frozen threshold\n", tpr.to_string())
    print(json.dumps({k: v for k, v in checks.items() if k != "thresholds"}, indent=1))


if __name__ == "__main__":
    main()
