"""Post-hoc re-analysis requested by the second external review (EXPLORATORY, not pre-registered).

No new simulation of any design: (a)-(d) read existing result files and stored
trajectories (data_v2/*.npz); (e) re-executes the existing deterministic identity
check and saves its output.

(a) Precision at several assumed prevalences for addendum 3 (point estimates).
(b) Per-cost-cell AUCs for addendum 3 (D_L3, B0) with run-level bootstrap CIs.
(c) mu misspecification: D_L3 re-scored on stored E0/E2/E3 trajectories with mu_hat in a grid.
    i. threshold fixed at the true-mu calibration value;
    ii. threshold recalibrated on the stored calibration runs scored with the same mu_hat.
(d) B0 false-positive rate at the naive symmetric-cost threshold, by hidden mean cost,
    cost gap and competitor speed; figure results_v2/fig3_b0_fpr_by_cost.png.
(e) Max absolute paired price/quantity difference, cost-padding cartel vs higher-cost twin.

    python -m experiments.review2_reanalysis
"""
import json
import sys
import zlib
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from detectors import implied_cost  # noqa: E402
from evaluation.metrics import auc, threshold_95, wilson  # noqa: E402

R = ROOT / "results_v2"
out = {}

# (a) precision at prevalences
m3 = pd.read_csv(R / "addendum3_metrics.csv")
rows = []
for _, r in m3.iterrows():
    for pi in (0.5, 0.1, 0.05, 0.01):
        num, den = pi * r.TPR, pi * r.TPR + (1 - pi) * r.FPR
        rows.append({"detector": r.detector, "prevalence": pi, "TPR": r.TPR, "FPR": r.FPR,
                     "precision": num / den if den > 0 else float("nan")})
prec = pd.DataFrame(rows)
prec.to_csv(R / "review2_precision_by_prevalence.csv", index=False)
print("(a) precision by prevalence\n", prec.pivot(index="detector", columns="prevalence", values="precision").round(3))

# (b) per-cell AUC with bootstrap CI
a3 = pd.read_csv(R / "addendum3_scores.csv")
rng = np.random.default_rng(20261107)
cells = []
for det in ("D_L3", "B0"):
    for c, g in a3.groupby("cost_cell"):
        pos = g[g.conduct == "collusive_rigid"][det].to_numpy()
        neg = g[g.conduct == "competitive"][det].to_numpy()
        boots = [auc(rng.choice(pos, len(pos)), rng.choice(neg, len(neg))) for _ in range(2000)]
        cm = g.cost_1.iloc[0] / 2 + g.cost_2.iloc[0] / 2
        cells.append({"detector": det, "cost_cell": c, "cost_mean": round(cm, 3),
                      "cost_gap": round(g.cost_2.iloc[0] - g.cost_1.iloc[0], 3),
                      "n_pos": len(pos), "n_neg": len(neg), "auc": auc(pos, neg),
                      "lo": np.percentile(boots, 2.5), "hi": np.percentile(boots, 97.5)})
cells = pd.DataFrame(cells)
cells.to_csv(R / "review2_cell_auc_addendum3.csv", index=False)
print("\n(b) per-cell AUC (addendum 3)\n", cells.round(3).to_string(index=False))
print("    mean of per-cell AUCs:", cells.groupby("detector").auc.mean().round(3).to_dict())


# (c) mu misspecification on stored trajectories
def d_scores(cell, mu):
    z = np.load(ROOT / "data_v2" / f"{cell}.npz")
    return implied_cost.score(z["price"][:, 50:, :].astype(float), z["quantity"][:, 50:, :].astype(float), mu,
                              market_size=z["market_size"][:, 50:].astype(float))


mus = [0.15, 0.20, 0.225, 0.25, 0.275, 0.30, 0.35]
rows = []
for env, positive in (("E0", "collusive_rigid"), ("E2", "collusive_tracking"), ("E3", "collusive_tracking")):
    t_true = threshold_95(d_scores(f"calibration_{env}_competitive_grid", 0.25))
    for mu in mus:
        neg = d_scores(f"test_{env}_competitive_grid", mu)
        pos = d_scores(f"test_{env}_{positive}_grid", mu)
        t_re = threshold_95(d_scores(f"calibration_{env}_competitive_grid", mu))
        for label, t in (("fixed_true_mu_threshold", t_true), ("recalibrated_with_mu_hat", t_re)):
            fp, tp = int((neg > t).sum()), int((pos > t).sum())
            rows.append({"env": env, "positive": positive, "mu_hat": mu, "threshold_rule": label,
                         "threshold": t, "FPR": fp / len(neg), "FPR_lo": wilson(fp, len(neg))[0],
                         "FPR_hi": wilson(fp, len(neg))[1], "TPR": tp / len(pos), "AUC": auc(pos, neg)})
mis = pd.DataFrame(rows)
mis.to_csv(R / "review2_mu_misspecification.csv", index=False)
print("\n(c) mu misspecification (FPR / TPR / AUC)")
print(mis.pivot_table(index=["env", "mu_hat"], columns="threshold_rule", values=["FPR", "TPR"]).round(3).to_string())
print(mis[mis.threshold_rule == "fixed_true_mu_threshold"].pivot(index="mu_hat", columns="env", values="AUC").round(3))

# (d) B0 FPR at the naive threshold
thr = pd.read_csv(R / "thresholds.csv")
b0_naive = float(thr[(thr.calibration == "naive") & (thr.detector == "B0")].threshold.item())
s = pd.read_csv(R / "scores.csv")
fast = s[(s.split == "test") & (s.cost_mode == "grid") & (s.env == "E0") & (s.conduct == "competitive")]
fast = fast.assign(speed="fast (E0, main design)")
c = pd.read_csv(R / "confirmatory.csv")
wide = c[(c.cell == "C1") & (c.conduct == "competitive")].assign(speed="fast (E0, wide cost range, C1)")
a2 = pd.read_csv(R / "addendum2_scores.csv")
slow = pd.concat([a2[(a2.test == "H1") & (a2.conduct == "competitive")],
                  a3[a3.conduct == "competitive"]]).assign(speed="slow (E2, addenda 2-3)")
frames = []
for df in (fast, wide, slow):
    df = df.assign(cost_mean=((df.cost_1 + df.cost_2) / 2).round(3), cost_gap=(df.cost_2 - df.cost_1).round(3))
    frames.append(df[["speed", "cost_mean", "cost_gap", "B0"]])
b0 = pd.concat(frames)
tab = (b0.assign(flag=b0.B0 > b0_naive).groupby(["speed", "cost_mean", "cost_gap"])
       .agg(runs=("flag", "size"), flagged=("flag", "sum")).reset_index())
tab["FPR"] = tab.flagged / tab.runs
tab[["lo", "hi"]] = [wilson(int(f), int(n)) for f, n in zip(tab.flagged, tab.runs)]
tab.to_csv(R / "review2_b0_fpr_by_cost.csv", index=False)
print(f"\n(d) B0 FPR at naive threshold {b0_naive:.4f}\n", tab.round(3).to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)
colors = {0.0: "#2a78d6", 0.3: "#eb6834", 0.6: "#1baf7a"}
styles = {0.0: "-", 0.3: "--", 0.6: ":"}
for ax, speeds in zip(axes, (["fast (E0, main design)", "fast (E0, wide cost range, C1)"], ["slow (E2, addenda 2-3)"])):
    for gap, col in colors.items():
        d = tab[tab.speed.isin(speeds) & np.isclose(tab.cost_gap, gap)].groupby("cost_mean").agg(
            flagged=("flagged", "sum"), runs=("runs", "sum")).reset_index()
        if d.empty:
            continue
        f = d.flagged / d.runs
        ci = np.array([wilson(int(a), int(b)) for a, b in zip(d.flagged, d.runs)])
        ax.errorbar(d.cost_mean, f, yerr=[np.maximum(f - ci[:, 0], 0), np.maximum(ci[:, 1] - f, 0)], color=col, marker="o", linewidth=2, linestyle=styles[gap],
                    capsize=0, label=f"cost gap {gap}")
    ax.axhline(0.05, color="#52514e", linewidth=0.8)
    ax.set_xlabel("hidden mean marginal cost", fontsize=9)
    ax.set_title(("(a) fast competitors" if "fast" in speeds[0] else "(b) slow competitors"), fontsize=9, loc="left")
    ax.grid(axis="y", color="#e4e3df")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
axes[0].set_ylabel("B0 false-positive rate\n(threshold calibrated at c = 1, symmetric)", fontsize=9)
axes[0].legend(fontsize=8, frameon=False)
fig.tight_layout()
fig.savefig(R / "fig3_b0_fpr_by_cost.png", dpi=200)
fig.savefig(R / "fig3_b0_fpr_by_cost.pdf")

# (e) paired identity
from experiments.v2_hard_negatives import BASE_SEED, RUNS_PER_COST_CELL  # noqa: E402
from experiments.v2_run_all import COST_GAPS, COST_MEANS, PARAMS, PERIODS  # noqa: E402
from simulator.batch_sim import simulate_batch  # noqa: E402
from simulator.demand_shocks import ENVIRONMENTS, simulate_shocks  # noqa: E402

costs = np.array([(mm - g / 2, mm + g / 2) for mm in COST_MEANS for g in COST_GAPS for _ in range(RUNS_PER_COST_CELL)])


def streams():
    return np.random.SeedSequence(BASE_SEED, spawn_key=(zlib.crc32(b"H2|collusive_cost_padding"),)).spawn(4)


st = streams()
a_, q_ = simulate_shocks(np.random.default_rng(st[0]), len(costs), PERIODS, ENVIRONMENTS["E2"])
cart = simulate_batch(costs, a_, q_, "collusive_cost_padding", PARAMS, *(np.random.default_rng(x) for x in st[1:]))
st = streams()
a_, q_ = simulate_shocks(np.random.default_rng(st[0]), len(costs), PERIODS, ENVIRONMENTS["E2"])
twin = simulate_batch(costs + cart["cost_pad"][:, None], a_, q_, "competitive", PARAMS,
                      *(np.random.default_rng(x) for x in st[1:]))
identity = {"runs": int(len(costs)), "periods": PERIODS,
            "max_abs_price_diff": float(np.abs(cart["price"] - twin["price"]).max()),
            "max_abs_quantity_diff": float(np.abs(cart["quantity"] - twin["quantity"]).max()),
            "max_abs_market_size_diff": float(np.abs(cart["market_size"] - twin["market_size"]).max())}
(R / "review2_padding_identity.json").write_text(json.dumps(identity, indent=2))
print("\n(e) paired identity:", identity)
