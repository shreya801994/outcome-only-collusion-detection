"""Summary figure for the paper: every test across the four agent settings (descriptive; no new runs).

Reads committed result files only and writes results_v2/fig6_benchmark_matrix.png/.pdf and
results_v2/fig6_benchmark_matrix.csv (the plotted numbers, so the figure has a table view).

    python -m experiments.report_benchmark_figure
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results_v2"
sys.path.insert(0, str(ROOT))

auc = pd.read_csv(R / "auc.csv")
rates = pd.read_csv(R / "rates.csv")
a3 = pd.read_csv(R / "addendum3_metrics.csv").set_index("detector")
a4 = pd.read_csv(R / "addendum4_metrics.csv")
a5 = pd.read_csv(R / "addendum5_metrics.csv")
a6 = pd.read_csv(R / "addendum6_metrics.csv")
a7 = pd.read_csv(R / "addendum7_metrics.csv").set_index("screen")


def main_e2(det):
    a = auc[(auc.env == "E2") & (auc.positive == "collusive_rigid") & (auc.detector == det)].auc_pooled.iloc[0]
    f = rates[(rates.env == "E2") & (rates.conduct == "competitive") & (rates.cost_mode == "grid")
              & (rates.calibration == "matched") & (rates.detector == det)].rate.iloc[0]
    return a, f


def a5v(contrast, screen):
    r = a5[(a5.contrast == contrast) & (a5.screen == screen)].iloc[0]
    return r.auc_pooled, r.FPR


def a4v(contrast, stat="score_ac1"):
    r = a4[(a4.contrast == contrast) & (a4.statistic == stat)].iloc[0]
    return r.auc_pooled, r.FPR


def a6v(contrast, stat):
    r = a6[(a6.env == "E2") & (a6.contrast == contrast) & (a6.statistic == stat)].iloc[0]
    return r.auc_pooled, r.FPR


COLS = ["Scripted, fast\n(rigid cartel vs\ncompetitors, E2)", "Scripted, slow\n(rigid cartel vs\ncompetitors, E2)",
        "Cost-mimicking\npolicy vs its\nhigher-cost twin", "Q-learning\n(collusive vs\nmyopic learners)"]
TWIN = "twin: cost padding vs competitive at c+m (coupled)"
rows = {
    "B0 price level": [main_e2("B0"), (a3.loc["B0", "auc_pooled"], a3.loc["B0", "FPR"]), (0.5, np.nan),
                       (a7.loc["B0", "auc_pooled"], a7.loc["B0", "FPR"])],
    "D implied-cost stability": [main_e2("D_L3"), (a3.loc["D_L3", "auc_pooled"], a3.loc["D_L3", "FPR"]),
                                 (a5v(TWIN, "D_L3")[0], np.nan), (a7.loc["D_L3", "auc_pooled"], a7.loc["D_L3", "FPR"])],
    "Belal identified-set coverage": [a5v("main E2: collusive_rigid vs competitive", "BC_belal_coverage"),
                                      a5v("add3: slow rigid vs slow competitive", "BC_belal_coverage"),
                                      (a5v(TWIN, "BC_belal_coverage")[0], np.nan),
                                      (a7.loc["BC_belal_coverage", "auc_pooled"], a7.loc["BC_belal_coverage", "FPR"])],
    "Variance screen (CV)": [a5v("main E2: collusive_rigid vs competitive", "V1_cv"),
                             a5v("add3: slow rigid vs slow competitive", "V1_cv"), (a5v(TWIN, "V1_cv")[0], np.nan),
                             (a7.loc["V1_cv", "auc_pooled"], a7.loc["V1_cv", "FPR"])],
    "Adjustment-robust test (ours)": [a4v("fast rigid vs fast comp (test)"), a4v("SR vs SC"),
                                      (a4v("CP vs CP_twin")[0], np.nan),
                                      (a7.loc["Score_B", "auc_pooled"], a7.loc["Score_B", "FPR"])],
    "Probe, before/after": [a6v("FR vs FC", "Score_P"), a6v("SR vs SC", "Score_P"),
                            (a6v("CP vs CP_twin", "Score_P")[0], np.nan),
                            (a7.loc["Score_P", "auc_pooled"], a7.loc["Score_P", "FPR"])],
    "Probe, counterfactual": [a6v("FR vs FC", "Score_Pc"), a6v("SR vs SC", "Score_Pc"),
                              (a6v("CP vs CP_twin", "Score_Pc")[0], np.nan),
                              (a7.loc["Score_Pc", "auc_pooled"], a7.loc["Score_Pc", "FPR"])],
}
A = np.array([[v[0] for v in r] for r in rows.values()], float)
F = np.array([[v[1] for v in r] for r in rows.values()], float)
table = pd.DataFrame([{"test": t, "setting": c.replace("\n", " "), "auc": A[i, j], "fpr_at_frozen_threshold": F[i, j]}
                      for i, t in enumerate(rows) for j, c in enumerate(COLS)])
table.to_csv(R / "fig6_benchmark_matrix.csv", index=False)

cmap = LinearSegmentedColormap.from_list("div", ["#e34948", "#f0efec", "#2a78d6"])
fig, ax = plt.subplots(figsize=(9.2, 5.6))
ax.imshow(A, cmap=cmap, vmin=0.0, vmax=1.0, aspect="auto")
for i in range(A.shape[0]):
    for j in range(A.shape[1]):
        ink = "#ffffff" if abs(A[i, j] - 0.5) > 0.38 else "#1f1f1d"
        ax.text(j, i - 0.12, f"AUC {A[i, j]:.2f}", ha="center", va="center", fontsize=9.5, color=ink,
                fontweight="bold")
        bad = (not np.isnan(F[i, j])) and F[i, j] > 0.10
        sub = "exactly identical paths" if np.isnan(F[i, j]) else f"FPR {F[i, j]:.2f}" + ("  (> 0.10)" if bad else "")
        ax.text(j, i + 0.22, sub, ha="center", va="center", fontsize=8, color=ink,
                fontweight="bold" if bad else "normal")
ax.set_xticks(range(len(COLS)))
ax.set_xticklabels(COLS, fontsize=8.5)
ax.set_yticks(range(len(rows)))
ax.set_yticklabels(list(rows), fontsize=9)
ax.tick_params(length=0)
ax.xaxis.tick_top()
for s in ax.spines.values():
    s.set_visible(False)
ax.set_xticks(np.arange(-0.5, len(COLS)), minor=True)
ax.set_yticks(np.arange(-0.5, len(rows)), minor=True)
ax.grid(which="minor", color="#fcfcfb", linewidth=2)
ax.tick_params(which="minor", length=0)
notes = ["Cell colour: AUC (blue = separates, grey = chance 0.5, red = reversed).",
         "FPR = share of honest markets flagged at the frozen threshold (nominal 0.05); bold = above 0.10.",
         "Scripted columns: thresholds from the fast-competitor calibration split, so the slow column tests transfer",
         "to slower honest firms. Q-learning column: thresholds from an independent set of myopic learners."]
for k, line in enumerate(notes):
    fig.text(0.01, 0.075 - 0.02 * k, line, fontsize=7.5, color="#52514e")
fig.tight_layout(rect=(0, 0.1, 1, 1))
fig.savefig(R / "fig6_benchmark_matrix.png", dpi=200)
fig.savefig(R / "fig6_benchmark_matrix.pdf")
print(table.round(3).to_string(index=False))
