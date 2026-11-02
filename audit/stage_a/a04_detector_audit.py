"""Stage A: detector audit (B0-B3) on existing CSVs plus edge cases (read-only).

1. Recompute B0-B3 with the repository's detector functions on every auditor
   dataset and compare with the stored score files.
2. Summarise scores by cost gap (finding 10).
3. Score the only positive-control series (collusive CSVs).
4. Count how often the reactive rule's trigger (rival cut > 0.05) and B3's event
   (cut > 0.10) occur in the recorded reactive data.
5. Edge cases on tiny synthetic inputs (constant prices, identical jitter,
   unsorted rows, single event).
Run from the repository root:  python audit/stage_a/a04_detector_audit.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from detectors import (  # noqa: E402
    price_level_score as B0,
    synchronization_score as B1,
    directional_dependence_score as B2,
    deviation_response_score as B3,
)
from detectors.directional_dependence import directional_scores  # noqa: E402

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 30)
fmt = lambda v: f"{v:.6g}"  # noqa: E731


def score_all(df):
    rows = []
    for rid, g in df.groupby("run_id"):
        g = g.sort_values("period").reset_index(drop=True)
        rows.append({"run_id": rid, "B0": B0(g), "B1": B1(g), "B2": B2(g), "B3": B3(g)})
    return pd.DataFrame(rows)


def compare(name, rec, stored, mapping):
    m = rec.merge(stored, on="run_id")
    diffs = {k: float(np.abs(m[k] - m[v]).max()) for k, v in mapping.items()}
    print(f"{name}: rows={len(m)}; max |recomputed - stored| per score: {diffs}")


print("=" * 100)
print("1) Recompute vs stored")
aud = pd.read_csv(ROOT / "data/auditor_trajectories.csv")
rec_static = score_all(aud)
compare("detector_scores.csv", rec_static, pd.read_csv(ROOT / "results/detector_scores.csv"),
        {"B0": "B0_price_level", "B1": "B1_synchronization"})
raud = pd.read_csv(ROOT / "data/reactive_auditor_trajectories.csv")
rec_react = score_all(raud)
st_react = pd.read_csv(ROOT / "results/reactive_detector_scores.csv")
compare("reactive_detector_scores.csv", rec_react, st_react,
        {"B0": "B0_price_level", "B1": "B1_synchronization", "B2": "B2_directional_dependence", "B3": "B3_deviation_response"})
daud = pd.read_csv(ROOT / "data/dynamic_auditor_trajectories.csv")
rec_dyn = score_all(daud)
st_dyn = pd.read_csv(ROOT / "results/dynamic_detector_scores.csv")
compare("dynamic_detector_scores.csv", rec_dyn, st_dyn,
        {"B0": "B0_price_level", "B1": "B1_synchronization", "B2": "B2_directional_dependence"})
saud = pd.read_csv(ROOT / "data/reactive_shock_auditor_trajectories.csv")
rec_shock = score_all(saud)
print("reactive_shock_auditor_trajectories.csv: no stored score file contains these runs "
      "(results/reactive_detector_scores.csv has 400 rows, condition='reactive_competitive' only)")

print("=" * 100)
print("2) Score summaries by cost gap (labels joined after scoring)")
labels = {
    "static (auditor_trajectories)": (rec_static, pd.read_csv(ROOT / "data/researcher_trajectories.csv")),
    "reactive (reactive_auditor_trajectories)": (rec_react, pd.read_csv(ROOT / "data/reactive_researcher_trajectories.csv")),
    "reactive+shock (reactive_shock_auditor_trajectories)": (rec_shock, pd.read_csv(ROOT / "data/reactive_shock_researcher_trajectories.csv")),
    "adaptive+shock (dynamic_auditor_trajectories)": (rec_dyn, pd.read_csv(ROOT / "data/dynamic_researcher_trajectories.csv")),
}
for name, (rec, res) in labels.items():
    meta = res[["run_id", "cost_gap"]].drop_duplicates("run_id")
    meta["cost_gap"] = meta["cost_gap"].round(10)
    m = rec.merge(meta, on="run_id")
    print(f"--- {name}")
    print(m.groupby("cost_gap")[["B0", "B1", "B2", "B3"]].agg(["mean", "std", "min", "max"]).to_string(float_format=fmt))

print("=" * 100)
print("3) Positive-control series (single trajectories, no run_id)")
for f in ["collusive_reward_punishment.csv", "collusion_deviation_auditor.csv", "collusive_deviation_response.csv"]:
    g = pd.read_csv(ROOT / "data" / f).sort_values("period").reset_index(drop=True)
    print(f"{f}: periods={len(g)} B0={B0(g):.6f} B1={B1(g):.6f} B2={B2(g):.6f} "
          f"B2(1->2,2->1)={tuple(round(x, 6) for x in directional_scores(g))} B3={B3(g):.6f}")
a = pd.read_csv(ROOT / "data/collusion_deviation_researcher.csv")
b = pd.read_csv(ROOT / "data/collusive_deviation_response.csv")
same = np.allclose(a[["price_1", "price_2", "quantity_1", "quantity_2"]], b[["price_1", "price_2", "quantity_1", "quantity_2"]])
print(f"collusion_deviation_researcher.csv vs collusive_deviation_response.csv: identical prices/quantities = {same}; "
      f"forced_deviation periods: {a.index[a.forced_deviation].tolist()} vs {b.index[b.forced_deviation].tolist()}")
print("price path around the deviation (periods 28-40):")
print(a.loc[28:40, ["period", "price_1", "price_2"]].T.to_string(header=False))

print("=" * 100)
print("4) Reactive trigger and B3 event frequency in recorded reactive data")
for name, df in [("reactive", raud), ("reactive+shock", saud)]:
    df = df.sort_values(["run_id", "period"])
    d1 = df.groupby("run_id")["price_1"].diff()
    d2 = df.groupby("run_id")["price_2"].diff()
    n = int(d1.notna().sum())
    print(f"{name}: firm-price changes observed={2*n}; "
          f"changes < -0.05 (reactive trigger): {int((d1 < -0.05).sum() + (d2 < -0.05).sum())}; "
          f"changes < -0.10 (B3 event): {int((d1 < -0.10).sum() + (d2 < -0.10).sum())}; "
          f"SD of changes firm1={d1.std():.5f} firm2={d2.std():.5f}")
dd = daud.sort_values(["run_id", "period"])
d1 = dd.groupby("run_id")["price_1"].diff(); d2 = dd.groupby("run_id")["price_2"].diff()
print(f"adaptive+shock: changes < -0.10: {int((d1 < -0.10).sum() + (d2 < -0.10).sum())} of {2*int(d1.notna().sum())}")

print("=" * 100)
print("5) Edge cases with the repository's detector functions")
T = 50
const = pd.DataFrame({"period": range(T), "price_1": 1.9, "price_2": 1.9})
print(f"constant prices: B0={B0(const)} B1={B1(const)} B2={B2(const)} B3={B3(const)}")
jit = const.copy()
rng = np.random.default_rng(0)
e = rng.normal(0, 1e-12, T)
jit["price_1"] = 1.9 + e
jit["price_2"] = 1.9 + e
print(f"constant + identical 1e-12 jitter on both firms: B1={B1(jit):.6f}")
jit2 = const.copy(); jit2["price_1"] = 1.9 + rng.normal(0, 1e-12, T); jit2["price_2"] = 1.9 + rng.normal(0, 1e-12, T)
print(f"constant + independent 1e-12 jitter: B1={B1(jit2):.6f}")
one = const.copy(); one.loc[10:, "price_1"] = 1.7
print(f"single permanent cut by firm 1 (0.2) with no rival response: B3={B3(one)}")
one2 = one.copy(); one2.loc[11, "price_2"] = 1.9 - 1e-9
print(f"same, rival lowers price by 1e-9 next period: B3={B3(one2)}")
shuf = raud[raud.run_id == 1].sample(frac=1, random_state=0)
srt = shuf.sort_values("period")
print(f"run 1 reactive, rows shuffled vs sorted: B1 {B1(shuf):.4f} vs {B1(srt):.4f}; B2 {B2(shuf):.4f} vs {B2(srt):.4f}")
two = pd.DataFrame({"period": [0, 1], "price_1": [1, 2], "price_2": [1, 2]})
for f, nm in [(B1, "B1"), (B2, "B2"), (B3, "B3")]:
    try:
        print(f"2 observations: {nm}={f(two)}")
    except Exception as ex:  # noqa: BLE001
        print(f"2 observations: {nm} raises {type(ex).__name__}: {ex}")
