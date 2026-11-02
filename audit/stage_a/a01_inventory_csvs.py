"""Stage A, task: data inventory (read-only).

For every CSV under data/, results/ and evaluation/, report rows, columns,
run structure, conditions, cost gaps, costs, market sizes, labels, and how
many distinct trajectories exist (to detect runs that duplicate one another).
Also reports byte-identical files.

Run from the repository root:  python audit/stage_a/a01_inventory_csvs.py
Writes nothing inside the source tree; output goes to stdout and
audit/stage_a/out/a01_inventory.json.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "audit" / "stage_a" / "out"
OUT.mkdir(parents=True, exist_ok=True)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def summarize(path):
    df = pd.read_csv(path)
    info = {
        "file": str(path.relative_to(ROOT)),
        "sha256_16": sha(path),
        "rows": len(df),
        "columns": list(df.columns),
    }
    if "run_id" in df.columns:
        runs = df["run_id"].unique()
        info["n_run_ids"] = int(len(runs))
        info["run_id_min_max"] = [int(df["run_id"].min()), int(df["run_id"].max())]
        per_run = df.groupby("run_id").size()
        info["rows_per_run_min_max"] = [int(per_run.min()), int(per_run.max())]
    if "period" in df.columns:
        info["period_min_max"] = [int(df["period"].min()), int(df["period"].max())]
    for col in ["condition", "cost_gap", "cost_1", "cost_2", "market_size", "forced_deviation"]:
        if col in df.columns:
            vals = pd.unique(df[col])
            info[f"unique_{col}"] = [v.item() if hasattr(v, "item") else v for v in vals[:12]]
            info[f"n_unique_{col}"] = int(len(vals))
    # distinct trajectories: hash of rounded price series per run
    if {"run_id", "price_1", "price_2"}.issubset(df.columns):
        hashes = (
            df.sort_values(["run_id", "period"]) if "period" in df.columns else df
        ).groupby("run_id")[["price_1", "price_2"]].apply(
            lambda g: hashlib.md5(np.round(g.to_numpy(), 12).tobytes()).hexdigest()
        )
        info["n_distinct_price_trajectories"] = int(hashes.nunique())
    elif {"price_1", "price_2"}.issubset(df.columns):
        p = df[["price_1", "price_2"]]
        info["price_1_min_max"] = [float(p["price_1"].min()), float(p["price_1"].max())]
        info["price_2_min_max"] = [float(p["price_2"].min()), float(p["price_2"].max())]
        info["n_distinct_price_pairs_rounded_1e-9"] = int(
            p.round(9).drop_duplicates().shape[0]
        )
    return info


def main():
    files = sorted(
        list((ROOT / "data").glob("*.csv"))
        + list((ROOT / "results").glob("*.csv"))
        + list((ROOT / "evaluation").glob("*.csv"))
    )
    all_info = [summarize(f) for f in files]
    for info in all_info:
        print("=" * 100)
        for k, v in info.items():
            print(f"{k}: {v}")
    # byte-identical files
    by_hash = {}
    for info in all_info:
        by_hash.setdefault(info["sha256_16"], []).append(info["file"])
    print("=" * 100)
    print("Byte-identical file groups:")
    for h, group in by_hash.items():
        if len(group) > 1:
            print(f"  {h}: {group}")
    (OUT / "a01_inventory.json").write_text(json.dumps(all_info, indent=2, default=str))


if __name__ == "__main__":
    main()
