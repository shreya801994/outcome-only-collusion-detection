"""Vectorised repeated-pricing simulator for the v2 experiments.

Simulates many independent runs at once (arrays indexed [run, period, firm]).
Market: logit duopoly with outside good (see simulator/equilibrium.py), with
optional persistent shocks to attractiveness and market size
(simulator/demand_shocks.py).  Firms observe the current shocks before pricing.

Conduct
-------
competitive         target = static best response to the rival's last price
                    under current demand and own cost.
competitive_nash    target = static Nash price of the current demand (an
                    alternative competitive dynamic: no reaction to the rival's
                    last price; used in the exploratory analysis S5).
collusive_cost_padding
                    both firms best-respond as if each marginal cost were
                    c_i + m, with m ~ U[pad_low, pad_high] per run: a cartel that
                    mimics higher-cost competition (no punishment).  By the
                    equivalence result no outcome screen can separate it from
                    competition at costs c_i + m (addendum 2, H2).
collusive_rigid     target = fixed cooperative prices Nash + kappa*(joint - Nash)
                    computed once at mean demand (a = base attractiveness).
collusive_tracking  same cooperative rule recomputed every period at current demand.

Both cartels share one public state: if either firm prices more than
`tolerance` below its expected (noise-free) price while cooperating, both firms
price at the current-demand static Nash for K periods, then cooperate again.

All conducts: p_t = p_{t-1} + lambda * (target - p_{t-1}) + N(0, noise_sd^2);
with probability `tremble_prob` per firm-period the price is additionally cut by
U[tremble_low, tremble_high] for that period (identical across conducts).
Prices are clipped to [price_min, price_max].

Hidden state (costs, attractiveness, conduct, kappa, lambda, K, phase, trembles)
is returned for the researcher only; `auditor_view` returns what an auditor may see.
"""

from dataclasses import dataclass

import numpy as np

from simulator.equilibrium import best_response, joint_profit, nash, shares

CONDUCTS = ("competitive", "collusive_rigid", "collusive_tracking", "competitive_nash", "collusive_cost_padding")
COMPETITIVE = ("competitive", "competitive_nash")
PUNISHING = ("collusive_rigid", "collusive_tracking")


@dataclass(frozen=True)
class AgentParams:
    adjust_low: float = 0.5
    adjust_high: float = 1.0
    noise_sd: float = 0.01
    tremble_prob: float = 0.01
    tremble_low: float = 0.10
    tremble_high: float = 0.25
    kappa_low: float = 0.5
    kappa_high: float = 1.0
    punish_low: int = 3
    punish_high: int = 8
    pad_low: float = 0.2
    pad_high: float = 0.5
    tolerance: float = 0.05
    price_min: float = 0.5
    price_max: float = 4.0


def _cooperative(c1, c2, a1, a2, kappa, a0, mu):
    n1, n2 = nash(c1, c2, a1, a2, a0, mu)
    m1, m2 = joint_profit(c1, c2, a1, a2, a0, mu)
    return n1 + kappa * (m1 - n1), n2 + kappa * (m2 - n2), n1, n2


def simulate_batch(costs, a, q, conduct, params, rng_params, rng_noise, rng_tremble,
                   mu=0.25, a0=0.0, base_a=2.0):
    """Simulate len(costs) runs.

    costs : (R, 2) hidden marginal costs.
    a     : (R, T, 2) attractiveness paths.   q : (R, T) market-size paths.
    The three generators must be independent; all of them are consumed
    identically for every conduct, so conducts can share noise streams.
    """
    if conduct not in CONDUCTS:
        raise ValueError(f"unknown conduct {conduct!r}")
    costs = np.asarray(costs, dtype=float)
    n_runs, periods, _ = a.shape
    c1, c2 = costs[:, 0], costs[:, 1]

    lam = rng_params.uniform(params.adjust_low, params.adjust_high, size=(n_runs, 2))
    kappa = rng_params.uniform(params.kappa_low, params.kappa_high, size=n_runs)
    punish_len = rng_params.integers(params.punish_low, params.punish_high + 1, size=n_runs)
    if conduct == "collusive_cost_padding":  # drawn last, so other conducts' streams are unchanged
        pad = rng_params.uniform(params.pad_low, params.pad_high, size=n_runs)
        c1, c2 = c1 + pad, c2 + pad
    noise =rng_noise.normal(0.0, params.noise_sd, size=(n_runs, periods, 2))
    tremble = rng_tremble.random(size=(n_runs, periods, 2)) < params.tremble_prob
    tremble_size = rng_tremble.uniform(params.tremble_low, params.tremble_high, size=(n_runs, periods, 2))

    price = np.empty((n_runs, periods, 2))
    quantity = np.empty((n_runs, periods, 2))
    expected = np.empty((n_runs, periods, 2))
    punishing = np.zeros((n_runs, periods), dtype=bool)

    collusive = conduct in PUNISHING
    if conduct == "collusive_rigid":
        coop_static_1, coop_static_2, _, _ = _cooperative(c1, c2, base_a, base_a, kappa, a0, mu)

    a1_0, a2_0 = a[:, 0, 0], a[:, 0, 1]
    if conduct in COMPETITIVE or conduct == "collusive_cost_padding":
        prev1, prev2 = nash(c1, c2, a1_0, a2_0, a0, mu)
    elif conduct == "collusive_rigid":
        prev1, prev2 = coop_static_1.copy(), coop_static_2.copy()
    else:
        prev1, prev2, _, _ = _cooperative(c1, c2, a1_0, a2_0, kappa, a0, mu)

    punish_left = np.zeros(n_runs, dtype=int)
    for t in range(periods):
        a1t, a2t = a[:, t, 0], a[:, t, 1]
        if conduct in ("competitive", "collusive_cost_padding"):
            tgt1 = best_response(c1, a1t, prev2, a2t, a0, mu)
            tgt2 = best_response(c2, a2t, prev1, a1t, a0, mu)
        elif conduct == "competitive_nash":
            tgt1, tgt2 = nash(c1, c2, a1t, a2t, a0, mu)
        else:
            if conduct == "collusive_rigid":
                coop1, coop2 = coop_static_1, coop_static_2
                n1, n2 = nash(c1, c2, a1t, a2t, a0, mu)
            else:
                coop1, coop2, n1, n2 = _cooperative(c1, c2, a1t, a2t, kappa, a0, mu)
            in_punishment = punish_left > 0
            punishing[:, t] = in_punishment
            tgt1 = np.where(in_punishment, n1, coop1)
            tgt2 = np.where(in_punishment, n2, coop2)

        exp1 = prev1 + lam[:, 0] * (tgt1 - prev1)
        exp2 = prev2 + lam[:, 1] * (tgt2 - prev2)
        p1 = exp1 + noise[:, t, 0] - tremble[:, t, 0] * tremble_size[:, t, 0]
        p2 = exp2 + noise[:, t, 1] - tremble[:, t, 1] * tremble_size[:, t, 1]
        p1 = np.clip(p1, params.price_min, params.price_max)
        p2 = np.clip(p2, params.price_min, params.price_max)

        s1, s2, _ = shares(p1, p2, a1t, a2t, a0, mu)
        price[:, t, 0], price[:, t, 1] = p1, p2
        quantity[:, t, 0], quantity[:, t, 1] = q[:, t] * s1, q[:, t] * s2
        expected[:, t, 0], expected[:, t, 1] = exp1, exp2

        if collusive:
            cooperating = punish_left == 0
            deviation = cooperating & ((p1 < exp1 - params.tolerance) | (p2 < exp2 - params.tolerance))
            punish_left = np.where(punish_left > 0, punish_left - 1, 0)
            punish_left = np.where(deviation, punish_len, punish_left)

        prev1, prev2 = p1, p2

    return {
        "price": price,
        "quantity": quantity,
        "market_size": np.asarray(q, dtype=float),
        # researcher-only fields
        "cost": costs,  # true costs (before any padding)
        "cost_pad": pad if conduct == "collusive_cost_padding" else np.zeros(n_runs),
        "attractiveness": a,
        "conduct": conduct,
        "adjust_speed": lam,
        "kappa": kappa if collusive else np.full(n_runs, np.nan),
        "punish_len": punish_len if collusive else np.zeros(n_runs, dtype=int),
        "punishing": punishing,
        "tremble": tremble,
        "expected_price": expected,
    }


AUDITOR_LEVELS = {
    "L1": ("price",),
    "L2": ("price", "quantity"),
    "L3": ("price", "quantity", "market_size"),
}


def auditor_view(result, level):
    """Return only the arrays an auditor at `level` may see (no labels, no costs)."""
    if level not in AUDITOR_LEVELS:
        raise ValueError(f"unknown auditor level {level!r}")
    return {key: result[key] for key in AUDITOR_LEVELS[level]}
