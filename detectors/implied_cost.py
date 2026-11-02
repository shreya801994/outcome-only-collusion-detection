"""Implied-cost stability screen (a conduct-consistency check, not a new idea).

Under static competition with constant marginal cost, the logit first-order
condition p_i - c_i = mu / (1 - s_i) implies that the implied cost
    c_hat_i,t = p_i,t - mu / (1 - s_i,t)
stays constant over time even when demand shocks move shares.  Under collusion,
or any other pricing rule, it generally moves with shares.  This is the
classic conduct-identification logic (Bresnahan 1982; see also tests of
consistency with competitive equilibrium such as Hespanhol and Aswani 2020).

Score = max over firms of the robust SD (1.4826 * MAD over time) of c_hat.
Higher = less consistent with static competition = more suspicious.

Information required: prices, quantities, the demand parameter mu and the
market size (or outside share) to turn quantities into shares.  Without market
size the auditor must assume one (default 1), which is exact only if market
size is constant and equal to the assumed value up to a constant factor.
"""

import numpy as np

SHARE_CLIP = (1e-6, 1.0 - 1e-6)


def implied_costs(price, quantity, mu, market_size=None, assumed_market_size=1.0):
    """Implied costs array with the same shape as `price` ((T, 2) or (R, T, 2))."""
    price = np.asarray(price, dtype=float)
    quantity = np.asarray(quantity, dtype=float)
    if market_size is None:
        size = assumed_market_size
    else:
        size = np.asarray(market_size, dtype=float)[..., None]
    share = np.clip(quantity / size, *SHARE_CLIP)
    return price - mu / (1.0 - share)


def robust_sd(x, axis):
    med = np.median(x, axis=axis, keepdims=True)
    return 1.4826 * np.median(np.abs(x - med), axis=axis)


def score(price, quantity, mu=0.25, market_size=None, assumed_market_size=1.0):
    """Implied-cost instability for one run ((T, 2) arrays) or many runs ((R, T, 2))."""
    c_hat = implied_costs(price, quantity, mu, market_size, assumed_market_size)
    period_axis = c_hat.ndim - 2
    return np.max(robust_sd(c_hat, axis=period_axis), axis=-1)
