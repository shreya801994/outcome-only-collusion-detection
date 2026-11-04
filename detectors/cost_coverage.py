"""Belal's (2026) constant-cost identified-set statistic, ported to continuous prices.

Source: `costid.py` in github.com/alibelal-lang/algorithmic_collusion (MIT licence,
commit 23867f3), which computes, for every observation, the interval of constant marginal
costs c under which the observed action is a static best response to the rival's action
against a discrete grid of alternative prices:

    (p - c) s(p)  >=  (p' - c) s(p')   for every alternative p'
    s(p) > s(p')  ->  c <= (p s(p) - p' s(p')) / (s(p) - s(p'))
    s(p) < s(p')  ->  c >= (p s(p) - p' s(p')) / (s(p) - s(p'))

and then the coverage curve cov(c) = share of periods whose interval contains c.  Its peak
is "the largest fraction of behaviour any single constant cost can rationalise".

Port (our changes, stated):
  * our prices are continuous; the observed price is compared with a fixed grid of
    alternatives ALT_GRID (spacing 0.04, close to the spacing of the Calvano et al. 2020
    15-point grid used by Belal);
  * Belal gives the regulator the true demand state; here the auditor recovers it from
    observed shares by the logit inversion (level L3, mu known), which is exact;
  * costs may differ across firms, so the curve is computed per firm and the score uses the
    firm with the lower peak.
Score = 1 - min over firms of peak coverage (higher = less rationalisable by one constant cost).
"""
import numpy as np

ALT_GRID = np.round(np.arange(0.5, 4.0001, 0.04), 4)
C_GRID = np.round(np.arange(-1.0, 3.0001, 0.0025), 5)
TOL = 1e-12


def _share_own(p_own, p_rival, a_own, a_rival, mu, a0=0.0):
    u0 = a0 / mu
    u1 = (a_own - p_own) / mu
    u2 = (a_rival - p_rival) / mu
    m = np.maximum(np.maximum(u0, u1), u2)
    e0, e1, e2 = np.exp(u0 - m), np.exp(u1 - m), np.exp(u2 - m)
    return e1 / (e0 + e1 + e2)


def intervals(p, p_rival, a_own, a_rival, mu, alt=ALT_GRID):
    """Rationalising cost interval [lo, hi] for each period (arrays of shape (T,))."""
    s_a = _share_own(p, p_rival, a_own, a_rival, mu)[:, None]
    s_alt = _share_own(alt[None, :], p_rival[:, None], a_own[:, None], a_rival[:, None], mu)
    den = s_a - s_alt
    num = p[:, None] * s_a - alt[None, :] * s_alt
    with np.errstate(divide="ignore", invalid="ignore"):
        bound = num / den
    hi = np.where(den > TOL, bound, np.inf).min(axis=1)
    lo = np.where(den < -TOL, bound, -np.inf).max(axis=1)
    return lo, hi


def peak_coverage(lo, hi, cgrid=C_GRID):
    G = len(cgrid)
    diff = np.zeros(G + 1)
    ok = lo <= hi
    i0 = np.searchsorted(cgrid, lo[ok], side="left")
    i1 = np.searchsorted(cgrid, hi[ok], side="right")
    np.add.at(diff, np.clip(i0, 0, G), 1.0)
    np.add.at(diff, np.clip(i1, 0, G), -1.0)
    cov = np.cumsum(diff)[:G] / len(lo)
    k = int(np.argmax(cov))
    return float(cov[k]), float(cgrid[k])


def score_run(price, quantity, market_size, mu=0.25, start=50):
    price = np.asarray(price, float)[start:]
    share = np.clip(np.asarray(quantity, float)[start:] / np.asarray(market_size, float)[start:, None], 1e-12, 1)
    s0 = np.clip(1 - share.sum(axis=1, keepdims=True), 1e-12, 1)
    a_hat = price + mu * np.log(share / s0)
    peaks, argmax = [], []
    for i in (0, 1):
        j = 1 - i
        lo, hi = intervals(price[:, i], price[:, j], a_hat[:, i], a_hat[:, j], mu)
        pk, c = peak_coverage(lo, hi)
        peaks.append(pk)
        argmax.append(c)
    return {"score": 1.0 - min(peaks), "peak_1": peaks[0], "peak_2": peaks[1], "c_at_peak_1": argmax[0],
            "c_at_peak_2": argmax[1]}
