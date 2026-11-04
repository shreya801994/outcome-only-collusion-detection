"""Illustration for the final simulation report: what single simulated runs look like.
(EXPLORATORY, descriptive; reads stored trajectories in data_v2/, no simulation, no new scores.)

Shows one competitive and one rigid-cartel run from the same hidden-cost cell
(mean cost 1.00, gap 0) in E0 (no shocks) and E2 (share-moving shocks):
  top row    - firm 1 price
  bottom row - firm 1 implied cost c_hat = p - mu / (1 - q/Q), the input to screen D
Writes results_v2/fig5_example_runs.png/.pdf.

    python -m experiments.report_example_runs
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
MU = 0.25
CELL = 3  # cost-cell index for mean 1.00, gap 0.0 in the 3 x 3 grid (asserted below)


def first_run(env, conduct):
    z = np.load(ROOT / "data_v2" / f"test_{env}_{conduct}_grid.npz")
    idx = int(np.flatnonzero(z["cost_cell"] == CELL)[0])
    cost = z["cost"][idx]
    p = z["price"][idx, :, 0].astype(float)
    s = z["quantity"][idx, :, 0].astype(float) / z["market_size"][idx].astype(float)
    return cost, p, p - MU / (1 - s), z["punishing"][idx].astype(bool)


fig, axes = plt.subplots(2, 2, figsize=(10, 5.6), sharex=True)
colors = {"competitive": "#2a78d6", "collusive_rigid": "#eb6834"}
labels = {"competitive": "competitive", "collusive_rigid": "rigid cartel"}
t = np.arange(300)
for col, env in enumerate(["E0", "E2"]):
    for conduct in ["competitive", "collusive_rigid"]:
        cost, p, chat, pun = first_run(env, conduct)
        assert abs(cost.mean() - 1.0) < 1e-9 and abs(cost[1] - cost[0]) < 1e-9, cost
        axes[0, col].plot(t, p, color=colors[conduct], linewidth=1.3, label=labels[conduct])
        axes[1, col].plot(t, chat, color=colors[conduct], linewidth=1.3, label=labels[conduct])
        if conduct == "collusive_rigid" and pun.any():
            axes[0, col].scatter(t[pun], p[pun], s=6, color="#52514e", zorder=3,
                                 label="cartel punishment period")
    axes[1, col].axhline(1.0, color="#52514e", linestyle=":", linewidth=1, label="true cost")
    for r in range(2):
        axes[r, col].axvspan(0, 50, color="#e4e3df", alpha=0.6, linewidth=0)
    name = {"E0": "E0: no demand shocks", "E2": "E2: share-moving attractiveness shocks"}[env]
    axes[0, col].set_title(f"({'ab'[col]}) {name}", fontsize=9, loc="left")
axes[0, 0].set_ylabel("firm 1 price", fontsize=9)
axes[1, 0].set_ylabel("firm 1 implied cost ĉ", fontsize=9)
for ax in axes[1]:
    ax.set_xlabel("period (grey = burn-in, not scored)", fontsize=9)
handles, names = [], []
for ax in (axes[0, 0], axes[1, 1]):
    for h, n in zip(*ax.get_legend_handles_labels()):
        if n not in names:
            handles.append(h)
            names.append(n)
fig.legend(handles, names, fontsize=8, frameon=False, loc="lower center", ncol=4)
for ax in axes.flat:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="y", color="#e4e3df")
    ax.set_axisbelow(True)
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(ROOT / "results_v2" / "fig5_example_runs.png", dpi=200)
fig.savefig(ROOT / "results_v2" / "fig5_example_runs.pdf")
print("wrote fig5_example_runs")
