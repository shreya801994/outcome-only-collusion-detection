"""Descriptive: how much do the demand environments move the quantities that Proposition 2 depends on?
(EXPLORATORY, post hoc; reads stored trajectories in data_v2/, no simulation.)

For each environment E0-E3 and conduct, over the scoring window (periods 50-299), per run:
  - within-run SD of each firm's inside share s_i,t
  - within-run SD of the joint-profit ratio r_i,t = s_j,t / (s0,t (1 - s_i,t))   (Proposition 2b)
  - within-run SD of 1/(1 - s_i,t), the term that enters the implied cost       (Proposition 2c)
Reported as medians over runs (max over the two firms).  Writes
results_v2/review3_share_movement.csv and results_v2/fig4_share_movement.png/.pdf.

    python -m experiments.review3_share_movement
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CELLS = [("E0", "competitive"), ("E0", "collusive_rigid"), ("E1", "competitive"), ("E1", "collusive_rigid"),
         ("E2", "competitive"), ("E2", "collusive_rigid"), ("E2", "collusive_tracking"),
         ("E3", "competitive"), ("E3", "collusive_rigid"), ("E3", "collusive_tracking")]
rows = []
example = {}
for env, conduct in CELLS:
    z = np.load(ROOT / "data_v2" / f"test_{env}_{conduct}_grid.npz")
    q = z["quantity"][:, 50:, :].astype(float)
    Q = z["market_size"][:, 50:].astype(float)
    s = q / Q[..., None]
    s0 = 1 - s.sum(axis=-1)
    r = np.stack([s[..., 1] / (s0 * (1 - s[..., 0])), s[..., 0] / (s0 * (1 - s[..., 1]))], axis=-1)
    inv = 1 / (1 - s)
    rows.append({"env": env, "conduct": conduct, "runs": s.shape[0],
                 "median_sd_share": float(np.median(s.std(axis=1).max(axis=1))),
                 "median_sd_ratio_2b": float(np.median(r.std(axis=1).max(axis=1))),
                 "median_sd_inv_1_minus_s": float(np.median(inv.std(axis=1).max(axis=1))),
                 "median_sd_outside_share": float(np.median(s0.std(axis=1)))})
    if conduct == "competitive":
        example[env] = s[0, :, 0]
tab = pd.DataFrame(rows)
tab.to_csv(ROOT / "results_v2" / "review3_share_movement.csv", index=False)
pd.set_option("display.width", 200)
print(tab.round(4).to_string(index=False))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.4))
colors = {"E0": "#52514e", "E1": "#eb6834", "E2": "#2a78d6", "E3": "#1baf7a"}
for env, path in example.items():
    ax1.plot(np.arange(50, 300), path, color=colors[env], linewidth=1.6, label=env)
ax1.set_xlabel("period", fontsize=9)
ax1.set_ylabel("firm 1 inside share (one competitive run)", fontsize=9)
ax1.set_title("(a) Shares move far more under attractiveness shocks (E2, E3)", fontsize=9, loc="left")
ax1.legend(fontsize=8, frameon=False, ncol=4)
comp = tab[tab.conduct == "competitive"]
x = np.arange(len(comp))
ax2.bar(x - 0.2, comp.median_sd_share, width=0.38, color="#2a78d6", label="SD of inside share")
ax2.bar(x + 0.2, comp.median_sd_ratio_2b / 10, width=0.38, color="#eb6834", label="SD of ratio in Prop. 2(b) / 10")
ax2.set_xticks(x)
ax2.set_xticklabels(comp.env)
ax2.set_title("(b) Within-run variation, competitive runs (median)", fontsize=9, loc="left")
ax2.legend(fontsize=8, frameon=False)
for ax in (ax1, ax2):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="y", color="#e4e3df")
    ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(ROOT / "results_v2" / "fig4_share_movement.png", dpi=200)
fig.savefig(ROOT / "results_v2" / "fig4_share_movement.pdf")
