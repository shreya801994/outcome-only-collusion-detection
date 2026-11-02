"""Closed-form equilibrium tools for the logit duopoly with an outside good.

Demand (per unit of market size):
    s_i = exp((a_i - p_i)/mu) / (exp(a0/mu) + exp((a_1 - p_1)/mu) + exp((a_2 - p_2)/mu))

All functions are vectorised: arguments may be floats or numpy arrays that
broadcast against each other.

Best response.  Own log-profit is strictly concave in own price above cost, so
the first-order condition p_i - c_i = mu / (1 - s_i) characterises the unique
best response, which has the closed form
    p_i = c_i + mu * (1 + W(exp((a_i - c_i)/mu - 1) / A_i)),
    A_i = exp(a0/mu) + exp((a_j - p_j)/mu),
where W is the principal branch of the Lambert W function.

Joint-profit (two-product monopoly) prices carry a common markup
    m = mu / s_0 = mu * (1 + W(B / e)),   B = sum_i exp((a_i - c_i - a0)/mu).
"""

import numpy as np
from scipy.special import lambertw


def shares(p1, p2, a1=2.0, a2=2.0, a0=0.0, mu=0.25):
    """Return (s1, s2, s0): inside and outside shares (sum to one)."""
    u0 = np.asarray(a0, dtype=float) / mu
    u1 = (np.asarray(a1, dtype=float) - p1) / mu
    u2 = (np.asarray(a2, dtype=float) - p2) / mu
    m = np.maximum(np.maximum(u0, u1), u2)
    e0, e1, e2 = np.exp(u0 - m), np.exp(u1 - m), np.exp(u2 - m)
    d = e0 + e1 + e2
    return e1 / d, e2 / d, e0 / d


def best_response(c_i, a_i, p_j, a_j, a0=0.0, mu=0.25):
    """Unique profit-maximising price of firm i given the rival's price p_j."""
    log_a = np.logaddexp(np.asarray(a0, dtype=float) / mu, (np.asarray(a_j, dtype=float) - p_j) / mu)
    z = np.exp((np.asarray(a_i, dtype=float) - c_i) / mu - 1.0 - log_a)
    return c_i + mu * (1.0 + np.real(lambertw(z)))


def nash(c1, c2, a1=2.0, a2=2.0, a0=0.0, mu=0.25, tol=1e-13, max_iter=1000):
    """Static Bertrand-Nash prices by best-response iteration (a contraction here)."""
    c1, c2, a1, a2 = np.broadcast_arrays(*(np.asarray(x, dtype=float) for x in (c1, c2, a1, a2)))
    p1 = c1 + 2.0 * mu
    p2 = c2 + 2.0 * mu
    err = np.inf
    for _ in range(max_iter):
        n1 = best_response(c1, a1, p2, a2, a0, mu)
        n2 = best_response(c2, a2, p1, a1, a0, mu)
        err = max(float(np.max(np.abs(n1 - p1))), float(np.max(np.abs(n2 - p2))))
        p1, p2 = n1, n2
        if err < tol:
            return p1, p2
    raise RuntimeError(f"Nash iteration did not converge (last change {err:.2e})")


def joint_profit(c1, c2, a1=2.0, a2=2.0, a0=0.0, mu=0.25):
    """Prices that maximise the sum of both firms' profits (common markup)."""
    log_b = np.logaddexp((np.asarray(a1, dtype=float) - c1 - a0) / mu,
                         (np.asarray(a2, dtype=float) - c2 - a0) / mu)
    markup = mu * (1.0 + np.real(lambertw(np.exp(log_b - 1.0))))
    return np.asarray(c1, dtype=float) + markup, np.asarray(c2, dtype=float) + markup


def implied_cost(price, share, mu=0.25):
    """Marginal cost that makes `price` a static best response at inside share `share`."""
    return price - mu / (1.0 - share)
