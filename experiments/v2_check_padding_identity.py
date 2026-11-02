"""Exploratory check after addendum 2 (not pre-registered).

Claim: a cost-padding cartel (best response at costs c + m) produces exactly the
same price and quantity paths as competitive firms whose true costs are c + m,
given the same random streams.  So any screen that separates it from
competition at costs c is responding to the cost level, not to conduct.

    python -m experiments.v2_check_padding_identity
"""
import sys
import zlib
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from experiments.v2_hard_negatives import BASE_SEED, RUNS_PER_COST_CELL  # noqa: E402
from experiments.v2_run_all import COST_GAPS, COST_MEANS, PARAMS, PERIODS  # noqa: E402
from simulator.batch_sim import simulate_batch  # noqa: E402
from simulator.demand_shocks import ENVIRONMENTS, simulate_shocks  # noqa: E402

costs = np.array([(m - g / 2, m + g / 2) for m in COST_MEANS for g in COST_GAPS for _ in range(RUNS_PER_COST_CELL)])


def streams():
    key = zlib.crc32("H2|collusive_cost_padding".encode())
    return np.random.SeedSequence(BASE_SEED, spawn_key=(key,)).spawn(4)


s = streams()
a, q = simulate_shocks(np.random.default_rng(s[0]), len(costs), PERIODS, ENVIRONMENTS["E2"])
cartel = simulate_batch(costs, a, q, "collusive_cost_padding", PARAMS, *(np.random.default_rng(x) for x in s[1:]))
s = streams()
a2, q2 = simulate_shocks(np.random.default_rng(s[0]), len(costs), PERIODS, ENVIRONMENTS["E2"])
padded = costs + cartel["cost_pad"][:, None]
comp = simulate_batch(padded, a2, q2, "competitive", PARAMS, *(np.random.default_rng(x) for x in s[1:]))
print("max |price difference|    :", float(np.abs(cartel["price"] - comp["price"]).max()))
print("max |quantity difference| :", float(np.abs(cartel["quantity"] - comp["quantity"]).max()))
