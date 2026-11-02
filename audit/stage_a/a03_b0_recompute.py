"""Stage A: recompute B0 threshold, scores and false-positive rates from raw
trajectories (not from the stored summaries), with run-level Wilson intervals.

Inputs (read-only): data/b0_calibration_runs.csv, data/reactive_auditor_trajectories.csv,
data/reactive_researcher_trajectories.csv (labels joined only after scoring),
results/b0_threshold.txt, results/b0_hard_negative_results.csv, results/b0_fpr_summary.csv,
evaluation/competitive_equilibrium_reference.csv.
Run from the repository root:  python audit/stage_a/a03_b0_recompute.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import beta, norm

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from detectors.price_level import score as repo_b0  # noqa: E402


def wilson(x, n, conf=0.95):
    z = norm.ppf(1 - (1 - conf) / 2)
    p = x / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, centre - half), min(1.0, centre + half)


def clopper_pearson(x, n, conf=0.95):
    a = 1 - conf
    lo = 0.0 if x == 0 else beta.ppf(a / 2, x, n - x + 1)
    hi = 1.0 if x == n else beta.ppf(1 - a / 2, x + 1, n - x)
    return lo, hi


def own_b0(g):
    return float(((g["price_1"] + g["price_2"]) / 2).mean())


# ---------------- calibration ----------------
cal = pd.read_csv(ROOT / "data" / "b0_calibration_runs.csv")
cal_scores = cal.groupby("run_id").apply(own_b0, include_groups=False)
thr_recomputed = float(np.quantile(cal_scores, 0.95))
thr_stored = float((ROOT / "results" / "b0_threshold.txt").read_text().strip())
print("CALIBRATION (data/b0_calibration_runs.csv)")
print(f"  runs={cal_scores.size}  mean={cal_scores.mean():.7f}  sd(ddof=1)={cal_scores.std(ddof=1):.7f}  "
      f"min={cal_scores.min():.7f}  max={cal_scores.max():.7f}")
print(f"  95th percentile (np.quantile, linear) = {thr_recomputed:.10f}; stored threshold = {thr_stored:.10f}; "
      f"diff = {thr_recomputed - thr_stored:.2e}")
ref = pd.read_csv(ROOT / "evaluation" / "competitive_equilibrium_reference.csv")
nash_sym = ref.loc[ref.cost_gap == 0, ["equilibrium_price_1", "equilibrium_price_2"]].to_numpy().mean()
print(f"  threshold - symmetric Nash mean price ({nash_sym:.6f}) = {thr_stored - nash_sym:.6f}")
print(f"  calibration scores above stored threshold: {(cal_scores > thr_stored).sum()} / {cal_scores.size} "
      f"(in-sample, by construction about 5)")

# ---------------- evaluation ----------------
aud = pd.read_csv(ROOT / "data" / "reactive_auditor_trajectories.csv")
rows = []
for rid, g in aud.groupby("run_id"):
    g = g.sort_values("period")
    rows.append({"run_id": rid, "b0_own": own_b0(g), "b0_repo": repo_b0(g)})
sc = pd.DataFrame(rows)
meta = pd.read_csv(ROOT / "data" / "reactive_researcher_trajectories.csv",
                   usecols=["run_id", "cost_gap", "condition"]).drop_duplicates("run_id")
sc = sc.merge(meta, on="run_id", how="left", validate="one_to_one")
print(f"\nEVALUATION (data/reactive_auditor_trajectories.csv): runs={len(sc)}; "
      f"max |own - repo B0| = {np.abs(sc.b0_own - sc.b0_repo).max():.2e}")
stored = pd.read_csv(ROOT / "results" / "b0_hard_negative_results.csv")
cmp_ = sc.merge(stored[["run_id", "b0_score", "flagged"]], on="run_id")
print(f"  max |recomputed - stored b0_score| = {np.abs(cmp_.b0_own - cmp_.b0_score).max():.2e}; "
      f"flag mismatches = {((cmp_.b0_own > thr_stored) != cmp_.flagged).sum()}")

sc["flag"] = sc.b0_own > thr_stored
cal_sd = cal_scores.std(ddof=1)
out = []
for gap, g in sc.groupby("cost_gap"):
    x, n = int(g.flag.sum()), len(g)
    wl, wh = wilson(x, n)
    cl, ch = clopper_pearson(x, n)
    nash_mean = ref.loc[np.isclose(ref.cost_gap, gap), ["equilibrium_price_1", "equilibrium_price_2"]].to_numpy().mean()
    out.append({
        "cost_gap": gap, "runs": n, "flagged": x, "FPR": x / n,
        "wilson_lo": wl, "wilson_hi": wh, "cp_lo": cl, "cp_hi": ch,
        "b0_mean": g.b0_own.mean(), "b0_sd": g.b0_own.std(ddof=1),
        "b0_min": g.b0_own.min(), "b0_max": g.b0_own.max(),
        "nash_mean_price": nash_mean,
        "nash_mean_minus_thr": nash_mean - thr_stored,
        "min_score_minus_thr_in_cal_sd": (g.b0_own.min() - thr_stored) / cal_sd,
    })
res = pd.DataFrame(out)
pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 30)
print(res.to_string(index=False, float_format=lambda v: f"{v:.6g}"))
summ = pd.read_csv(ROOT / "results" / "b0_fpr_summary.csv")
m = res.merge(summ, on="cost_gap")
print(f"\nvs stored results/b0_fpr_summary.csv: max |FPR diff| = {np.abs(m.FPR - m.fpr).max():.2e}, "
      f"max |Wilson lo diff| = {np.abs(m.wilson_lo - m.ci_low).max():.2e}, "
      f"max |Wilson hi diff| = {np.abs(m.wilson_hi - m.ci_high).max():.2e}")

# gap-0 evaluation runs vs calibration runs: same data-generating process?
g0 = sc[sc.cost_gap == 0].b0_own
print(f"\nGap-0 evaluation scores: mean={g0.mean():.7f} sd={g0.std(ddof=1):.7f} (calibration mean={cal_scores.mean():.7f})")
# runs whose first-period price pair is identical across calibration/evaluation (shared trajectories?)
cal_paths = {tuple(np.round(g.sort_values('period')[['price_1','price_2']].to_numpy().ravel(), 12)) for _, g in cal.groupby('run_id')}
ev_paths = {tuple(np.round(g.sort_values('period')[['price_1','price_2']].to_numpy().ravel(), 12)) for _, g in aud.groupby('run_id')}
print(f"Identical full trajectories shared by calibration and evaluation: {len(cal_paths & ev_paths)}")
res.to_csv(ROOT / "audit" / "stage_a" / "out" / "a03_b0_fpr_recomputed.csv", index=False)
