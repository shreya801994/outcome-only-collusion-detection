"""Figures for the v2 results (called by experiments/v2_make_tables.py).

Fig 1  AUC (rigid cartel vs competitive) for each screen, one panel per demand environment.
Fig 2  Exploratory sensitivity: (a) implied-cost screen vs share-shock size,
       (b) price-level screen vs hidden-cost uncertainty, pooled vs within cost cell.
Static figures for a paper; colours from a CVD-validated categorical palette.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
ENV_TITLES = {"E0": "E0: no demand shocks", "E1": "E1: market-size shocks only",
              "E2": "E2: share-moving shocks", "E3": "E3: both shocks"}
SCREENS = [("B0", "B0 price level"), ("B1", "B1 synchronisation"), ("B2", "B2 lead-lag"),
           ("B3", "B3 deviation response"), ("D_L2", "D implied cost, no market size"),
           ("D_L3", "D implied cost, with market size")]


def _style(ax):
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=8)


def figure_auc_by_environment(auc, out_dir):
    fig, axes = plt.subplots(1, 4, figsize=(11, 3.2), sharey=True)
    for ax, env in zip(axes, ["E0", "E1", "E2", "E3"]):
        df = auc[(auc.env == env) & (auc.positive == "collusive_rigid")].set_index("detector")
        for y, (det, _) in enumerate(SCREENS):
            row = df.loc[det]
            ax.plot([row.pooled_lo, row.pooled_hi], [y, y], color=BLUE, linewidth=2, solid_capstyle="round")
            ax.plot(row.auc_pooled, y, "o", color=BLUE, markersize=6, markeredgecolor="white", markeredgewidth=1.2)
        ax.axvline(0.5, color=INK2, linewidth=0.8)
        ax.set_xlim(0, 1.02)
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_title(ENV_TITLES[env], fontsize=9, color=INK, loc="left")
        _style(ax)
    axes[0].set_yticks(range(len(SCREENS)))
    axes[0].set_yticklabels([label for _, label in SCREENS], fontsize=8, color=INK)
    axes[0].invert_yaxis()
    fig.supxlabel("AUC, rigid cartel vs competitive runs (pooled over hidden costs; 0.5 = chance)",
                  fontsize=9, color=INK2)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out_dir / f"fig1_auc_by_environment.{ext}", dpi=200)
    plt.close(fig)


def figure_sensitivity(sens, out_dir):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.4))
    s1 = sens[(sens.analysis == "S1_shock_scale") & (sens.detector == "D_L3")]
    for positive, color, label in (("collusive_tracking", BLUE, "demand-tracking cartel"),
                                   ("collusive_rigid", ORANGE, "rigid cartel")):
        d = s1[s1.positive == positive].sort_values("value")
        ax1.errorbar(d.value, d.auc_pooled, yerr=[d.auc_pooled - d.pooled_lo, d.pooled_hi - d.auc_pooled],
                     color=color, linewidth=2, marker="o", markersize=5, capsize=0, label=label)
    ax1.set_xlabel("share-moving shock size (multiple of E2 design)", fontsize=9, color=INK2)
    ax1.set_ylabel("AUC vs competitive", fontsize=9, color=INK2)
    ax1.set_title("(a) Implied-cost screen D needs share variation", fontsize=9, color=INK, loc="left")
    s3 = sens[(sens.analysis == "S3_cost_uncertainty") & (sens.detector == "B0")].sort_values("value")
    ax2.errorbar(s3.value, s3.auc_within, yerr=[s3.auc_within - s3.within_lo, s3.within_hi - s3.auc_within],
                 color=ORANGE, linewidth=2, marker="o", markersize=5, label="within a cost cell (costs known)")
    ax2.errorbar(s3.value, s3.auc_pooled, yerr=[s3.auc_pooled - s3.pooled_lo, s3.pooled_hi - s3.auc_pooled],
                 color=BLUE, linewidth=2, marker="o", markersize=5, label="pooled (costs hidden)")
    ax2.set_xlabel("hidden mean-cost spread w (mean cost in {1-w, 1, 1+w})", fontsize=9, color=INK2)
    ax2.set_title("(b) Price-level screen B0 loses power as cost uncertainty grows", fontsize=9, color=INK,
                  loc="left")
    for ax in (ax1, ax2):
        ax.axhline(0.5, color=INK2, linewidth=0.8)
        ax.set_ylim(0.4, 1.02)
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(colors=INK2, labelsize=8)
        ax.legend(fontsize=8, frameon=False, loc="lower right", labelcolor=INK)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out_dir / f"fig2_sensitivity.{ext}", dpi=200)
    plt.close(fig)


def make_figures(results_dir):
    results_dir = Path(results_dir)
    auc = pd.read_csv(results_dir / "auc.csv")
    figure_auc_by_environment(auc, results_dir)
    sens_path = results_dir / "sensitivity.csv"
    if sens_path.exists():
        figure_sensitivity(pd.read_csv(sens_path), results_dir)
