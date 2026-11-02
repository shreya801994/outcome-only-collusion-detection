"""Entry point 1 of 2: generate every v2 simulation cell and score it.

    python -m experiments.v2_run_all            # frozen design (docs/V2_DESIGN.md) + exploratory sensitivity
    python -m experiments.v2_run_all --quick    # 3 runs per cost cell, for smoke tests (no sensitivity)
    python -m experiments.v2_run_all --skip-sensitivity

Then run entry point 2:  python -m experiments.v2_make_tables

Writes
    data_v2/<split>_<env>_<conduct>_<costs>.npz   trajectories (auditor + researcher arrays)
    data_v2/manifest.json                         seeds, parameters, code hashes, versions
    results_v2/scores.csv                         one row per run; labels joined after scoring

Detectors receive auditor arrays only.  Hidden fields (costs, conduct, shocks,
agent parameters) are attached to the score table after scoring.
"""

import argparse
import hashlib
import json
import platform
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from detectors import (  # noqa: E402
    deviation_response_score,
    directional_dependence_score,
    price_level_score,
    synchronization_score,
)
from detectors import implied_cost  # noqa: E402
from simulator.batch_sim import CONDUCTS, AgentParams, auditor_view, simulate_batch  # noqa: E402
from simulator.demand_shocks import ENVIRONMENTS, simulate_shocks  # noqa: E402

BASE_SEED = 20261102
PERIODS = 300
BURN_IN = 50
MU = 0.25
COST_MEANS = (0.85, 1.00, 1.15)
COST_GAPS = (0.0, 0.3, 0.6)
RUNS_PER_COST_CELL = 30
NAIVE_RUNS = 200
SPLITS = ("calibration", "test")
ENVS = ("E0", "E1", "E2", "E3")
COST_MODES = ("naive", "grid")
TEST_CONDUCTS = {
    "E0": ("competitive", "collusive_rigid"),
    "E1": ("competitive", "collusive_rigid"),
    "E2": ("competitive", "collusive_rigid", "collusive_tracking"),
    "E3": ("competitive", "collusive_rigid", "collusive_tracking"),
}
PARAMS = AgentParams()

CELLS = (
    [("calibration", "E0", "competitive", "naive"), ("test", "E0", "competitive", "naive")]
    + [("calibration", env, "competitive", "grid") for env in ENVS]
    + [("test", env, conduct, "grid") for env in ENVS for conduct in TEST_CONDUCTS[env]]
)

DATA_DIR = ROOT / "data_v2"
RESULTS_DIR = ROOT / "results_v2"


def cell_name(split, env, conduct, mode):
    return f"{split}_{env}_{conduct}_{mode}"


def cell_seed(split, env, conduct, mode):
    key = (SPLITS.index(split), ENVS.index(env), CONDUCTS.index(conduct), COST_MODES.index(mode))
    return np.random.SeedSequence(BASE_SEED, spawn_key=key)


def cost_design(mode, runs_per_cell):
    """Return costs (R, 2) and the cost-cell index of each run."""
    if mode == "naive":
        n = NAIVE_RUNS if runs_per_cell == RUNS_PER_COST_CELL else 10 * runs_per_cell
        return np.ones((n, 2)), np.full(n, -1)
    rows, cells = [], []
    for i, c_mean in enumerate(COST_MEANS):
        for j, gap in enumerate(COST_GAPS):
            for _ in range(runs_per_cell):
                rows.append((c_mean - gap / 2.0, c_mean + gap / 2.0))
                cells.append(i * len(COST_GAPS) + j)
    return np.array(rows), np.array(cells)


def score_runs(view_l3):
    """Scores from auditor arrays only (prices, quantities, market size), scoring window only."""
    price = view_l3["price"][:, BURN_IN:, :]
    qty = view_l3["quantity"][:, BURN_IN:, :]
    size = view_l3["market_size"][:, BURN_IN:]
    n = price.shape[0]
    periods = np.arange(price.shape[1])
    out = {name: np.empty(n) for name in ("B0", "B1", "B2", "B3")}
    for r in range(n):
        frame = pd.DataFrame({"period": periods, "price_1": price[r, :, 0], "price_2": price[r, :, 1]})
        out["B0"][r] = price_level_score(frame)
        out["B1"][r] = synchronization_score(frame)
        out["B2"][r] = directional_dependence_score(frame)
        out["B3"][r] = deviation_response_score(frame)
    out["D_L2"] = implied_cost.score(price, qty, MU)                      # market size unknown (assumed 1)
    out["D_L3"] = implied_cost.score(price, qty, MU, market_size=size)    # shares known
    out["D_L3_mu020"] = implied_cost.score(price, qty, 0.20, market_size=size)
    out["D_L3_mu030"] = implied_cost.score(price, qty, 0.30, market_size=size)
    return pd.DataFrame(out)


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="3 runs per cost cell (smoke test)")
    parser.add_argument("--skip-sensitivity", action="store_true", help="skip exploratory analyses S1-S6")
    args = parser.parse_args()
    runs_per_cell = 3 if args.quick else RUNS_PER_COST_CELL
    data_dir = DATA_DIR / "quick" if args.quick else DATA_DIR
    results_dir = RESULTS_DIR / "quick" if args.quick else RESULTS_DIR
    data_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    tables, manifest_cells = [], []
    start = time.time()
    for split, env, conduct, mode in CELLS:
        name = cell_name(split, env, conduct, mode)
        seq = cell_seed(split, env, conduct, mode)
        s_shock, s_params, s_noise, s_tremble = seq.spawn(4)
        costs, cost_cell = cost_design(mode, runs_per_cell)
        n = len(costs)
        a, q = simulate_shocks(np.random.default_rng(s_shock), n, PERIODS, ENVIRONMENTS[env])
        result = simulate_batch(costs, a, q, conduct, PARAMS,
                                np.random.default_rng(s_params), np.random.default_rng(s_noise),
                                np.random.default_rng(s_tremble), mu=MU)

        scores = score_runs(auditor_view(result, "L3"))  # detectors see auditor arrays only

        # researcher labels are attached only after scoring
        labels = pd.DataFrame({
            "cell": name, "split": split, "env": env, "conduct": conduct, "cost_mode": mode,
            "run": np.arange(n), "cost_1": costs[:, 0], "cost_2": costs[:, 1],
            "cost_mean": costs.mean(axis=1).round(10), "cost_gap": (costs[:, 1] - costs[:, 0]).round(10),
            "cost_cell": cost_cell, "kappa": result["kappa"],
            "adjust_1": result["adjust_speed"][:, 0], "adjust_2": result["adjust_speed"][:, 1],
            "punish_len": result["punish_len"],
            "n_trembles": result["tremble"][:, BURN_IN:, :].sum(axis=(1, 2)),
            "punish_share": result["punishing"][:, BURN_IN:].mean(axis=1),
        })
        tables.append(pd.concat([labels, scores], axis=1))

        np.savez_compressed(
            data_dir / f"{name}.npz",
            price=result["price"].astype(np.float32),
            quantity=result["quantity"].astype(np.float32),
            market_size=result["market_size"].astype(np.float32),
            cost=result["cost"], cost_cell=cost_cell,
            attractiveness=result["attractiveness"].astype(np.float32),
            adjust_speed=result["adjust_speed"], kappa=result["kappa"],
            punish_len=result["punish_len"], punishing=result["punishing"], tremble=result["tremble"],
        )
        manifest_cells.append({"cell": name, "split": split, "env": env, "conduct": conduct,
                               "cost_mode": mode, "runs": int(n), "base_seed": BASE_SEED,
                               "spawn_key": list(seq.spawn_key)})
        print(f"{name:45s} runs={n:4d}  elapsed={time.time() - start:6.1f}s", flush=True)

    scores = pd.concat(tables, ignore_index=True)
    scores.to_csv(results_dir / "scores.csv", index=False)

    code_files = ["simulator/equilibrium.py", "simulator/demand_shocks.py", "simulator/batch_sim.py",
                  "detectors/implied_cost.py", "detectors/price_level.py", "detectors/synchronization.py",
                  "detectors/directional_dependence.py", "detectors/deviation_response.py",
                  "experiments/v2_run_all.py"]
    import scipy  # noqa: E402
    manifest = {
        "design": "docs/V2_DESIGN.md", "periods": PERIODS, "burn_in": BURN_IN, "mu": MU,
        "cost_means": COST_MEANS, "cost_gaps": COST_GAPS, "runs_per_cost_cell": runs_per_cell,
        "agent_params": asdict(PARAMS), "environments": {k: asdict(v) for k, v in ENVIRONMENTS.items()},
        "cells": manifest_cells, "code_sha256_16": {f: file_hash(ROOT / f) for f in code_files},
        "python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
        "scipy": scipy.__version__, "runtime_seconds": round(time.time() - start, 1),
    }
    (data_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"total runs={len(scores)}  saved {results_dir / 'scores.csv'}")

    if not (args.quick or args.skip_sensitivity):
        from experiments.v2_sensitivity import main as run_sensitivity  # exploratory, not pre-registered
        run_sensitivity()


if __name__ == "__main__":
    main()
