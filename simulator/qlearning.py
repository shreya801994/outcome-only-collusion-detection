"""Tabular Q-learning duopoly of Calvano, Calzolari, Denicolo & Pastorello (2020, AER 110(10)).

Baseline specification (their Section III), vectorised over S independent sessions in numpy:
  * logit demand a = 2, a0 = 0, mu = 0.25, symmetric marginal cost c (may differ by session);
  * m = 15 equally spaced prices on [pN - xi (pM - pN), pM + xi (pM - pN)], xi = 0.1, where pN and
    pM are the static Nash and joint-profit prices at cost c;
  * one-period memory (k = 1): the state is last period's price pair (m^2 = 225 states);
  * Q-learning with learning rate alpha = 0.15, discount delta, epsilon-greedy exploration
    eps_t = exp(-beta t), beta = 4e-6;
  * Q initialised at the discounted payoff of each action against a uniformly random rival;
  * convergence: the greedy strategy of both agents unchanged for 100,000 consecutive periods.
Profit gain Delta = (pi_bar - pi_N) / (pi_M - pi_N), pi_bar = mean per-firm profit on the limit
path of greedy play.
"""
import numpy as np

from simulator.equilibrium import joint_profit, nash, shares

M_PRICES, XI = 15, 0.1


def price_grid(c, m=M_PRICES, xi=XI, a=2.0, a0=0.0, mu=0.25):
    c = np.atleast_1d(np.asarray(c, float))
    pn, _ = nash(c, c, a, a, a0, mu)
    pm, _ = joint_profit(c, c, a, a, a0, mu)
    lo, hi = pn - xi * (pm - pn), pm + xi * (pm - pn)
    return lo[:, None] + (hi - lo)[:, None] * np.linspace(0, 1, m)[None, :], pn, pm


def profit_table(grid, c, a=2.0, a0=0.0, mu=0.25):
    """(S, m, m, 2): profit of each firm for own/rival grid actions (a1, a2)."""
    p1 = grid[:, :, None]
    p2 = grid[:, None, :]
    s1, s2, _ = shares(p1, p2, a, a, a0, mu)
    c = np.asarray(c, float)[:, None, None]
    return np.stack([(p1 - c) * s1, (p2 - c) * s2], axis=-1)


def static_profits(c, a=2.0, a0=0.0, mu=0.25):
    c = np.asarray(c, float)
    pn, _ = nash(c, c, a, a, a0, mu)
    pm, _ = joint_profit(c, c, a, a, a0, mu)
    sn, _, _ = shares(pn, pn, a, a, a0, mu)
    sm, _, _ = shares(pm, pm, a, a, a0, mu)
    return (pn - c) * sn, (pm - c) * sm


def train(c, delta, rng, alpha=0.15, beta=4e-6, conv_window=100_000, max_periods=8_000_000, report=None):
    """Train S sessions (len(c) == len(delta)); returns dict with greedy policies and diagnostics."""
    c = np.asarray(c, float)
    delta = np.asarray(delta, float)
    S, m = len(c), M_PRICES
    grid, pn, pm = price_grid(c)
    prof = profit_table(grid, c)                                 # (S, m, m, 2)
    n_states = m * m
    # Q0(s, a) = sum_{a_j} pi_i(a, a_j) / ((1 - delta) m), identical across states
    q0_1 = prof[:, :, :, 0].mean(axis=2) / (1 - delta)[:, None]  # (S, m): own action a1, rival uniform
    q0_2 = prof[:, :, :, 1].mean(axis=1) / (1 - delta)[:, None]  # (S, m): own action a2
    Q = np.empty((2, S, n_states, m))
    Q[0] = q0_1[:, None, :]
    Q[1] = q0_2[:, None, :]
    greedy = Q.argmax(axis=-1)                                   # (2, S, n_states)
    state = rng.integers(0, n_states, S)
    stable = np.zeros(S, dtype=np.int64)
    converged_at = np.full(S, -1, dtype=np.int64)
    active = np.arange(S)
    t = 0
    while active.size and t < max_periods:
        A = active
        st = state[A]
        eps = np.exp(-beta * t)
        explore = rng.random((A.size, 2)) < eps
        rand_act = rng.integers(0, m, (A.size, 2))
        g1 = greedy[0, A, st]
        g2 = greedy[1, A, st]
        a1 = np.where(explore[:, 0], rand_act[:, 0], g1)
        a2 = np.where(explore[:, 1], rand_act[:, 1], g2)
        nxt = a1 * m + a2
        pi = prof[A, a1, a2]                                     # (A, 2)
        changed = np.zeros(A.size, dtype=bool)
        for i, ai in ((0, a1), (1, a2)):
            target = pi[:, i] + delta[A] * Q[i, A, nxt].max(axis=-1)
            Q[i, A, st, ai] = (1 - alpha) * Q[i, A, st, ai] + alpha * target
            new_g = Q[i, A, st].argmax(axis=-1)
            ch = new_g != greedy[i, A, st]
            greedy[i, A, st] = new_g
            changed |= ch
        stable[A] = np.where(changed, 0, stable[A] + 1)
        state[A] = nxt
        t += 1
        done = stable[A] >= conv_window
        if done.any():
            converged_at[A[done]] = t
            active = A[~done]
        if report and t % 500_000 == 0:
            report(t, active.size)
    return {"c": c, "delta": delta, "grid": grid, "prof": prof, "greedy": greedy, "Q": Q, "state": state,
            "converged": converged_at >= 0, "t_converged": converged_at, "periods_run": t,
            "pn": pn, "pm": pm}


def play(res, start_state, periods, rng=None, tremble_prob=0.0, forced=None):
    """Greedy play from start_state for `periods` periods (no learning).

    tremble_prob : each firm-period, with this probability the firm plays a uniformly random grid
                   action (an exogenous price error, the analogue of the scripted agents' price cuts).
    forced       : optional (S, periods) int array; where >= 0, firm 1's action is replaced by it.
    Returns action indices (S, periods, 2) and prices (S, periods, 2).
    """
    greedy, grid = res["greedy"], res["grid"]
    S, m = grid.shape
    sidx = np.arange(S)
    st = np.asarray(start_state).copy()
    acts = np.empty((S, periods, 2), dtype=np.int64)
    if tremble_prob > 0:
        tr = rng.random((S, periods, 2)) < tremble_prob
        tr_act = rng.integers(0, m, (S, periods, 2))
    for t in range(periods):
        a1, a2 = greedy[0, sidx, st], greedy[1, sidx, st]
        if tremble_prob > 0:
            a1 = np.where(tr[:, t, 0], tr_act[:, t, 0], a1)
            a2 = np.where(tr[:, t, 1], tr_act[:, t, 1], a2)
        if forced is not None:
            a1 = np.where(forced[:, t] >= 0, forced[:, t], a1)
        acts[:, t, 0], acts[:, t, 1] = a1, a2
        st = a1 * m + a2
    prices = grid[sidx[:, None, None], acts]
    return acts, prices


def profit_gain(res, horizon=1000):
    """Calvano's Delta from greedy play started at the final training state (limit path average)."""
    acts, _ = play(res, res["state"], horizon)
    S = acts.shape[0]
    tail = acts[:, horizon // 2:, :]
    pi = res["prof"][np.arange(S)[:, None], tail[:, :, 0], tail[:, :, 1]]   # (S, T, 2)
    pi_bar = pi.mean(axis=(1, 2))
    pin, pim = static_profits(res["c"])
    return (pi_bar - pin) / (pim - pin), pi_bar
