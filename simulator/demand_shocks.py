"""Persistent demand shocks for the v2 experiments.

Two kinds of shock, either or both of which can be switched on:

* share-moving shocks to product attractiveness,
      a_i,t = base_a + zeta_t + xi_i,t,
  with a common AR(1) component zeta and product-specific AR(1) components xi_i.
  These move market shares and therefore competitive prices.
* market-size shocks, ln Q_t AR(1).  Under logit demand these scale quantities
  and profits but leave shares and every profit-maximising price unchanged.

Every AR(1) process x_t = rho * x_{t-1} + sqrt(1 - rho^2) * sd * e_t starts from
its stationary distribution N(0, sd^2).  Firms observe the current shock before
pricing; the auditor never observes the attractiveness shocks.
"""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ShockSpec:
    common_sd: float = 0.0      # stationary SD of the common attractiveness shock
    idio_sd: float = 0.0        # stationary SD of each product-specific shock
    log_size_sd: float = 0.0    # stationary SD of log market size
    rho: float = 0.95
    base_a: float = 2.0
    base_q: float = 1.0


ENVIRONMENTS = {
    "E0": ShockSpec(),
    "E1": ShockSpec(log_size_sd=0.20),
    "E2": ShockSpec(common_sd=0.25, idio_sd=0.15),
    "E3": ShockSpec(common_sd=0.25, idio_sd=0.15, log_size_sd=0.20),
}


def _ar1(rng, n_runs, periods, sd, rho, n_series=1):
    out = np.zeros((n_runs, periods, n_series))
    if sd == 0.0:
        return out
    out[:, 0, :] = rng.normal(0.0, sd, size=(n_runs, n_series))
    innov_sd = np.sqrt(1.0 - rho ** 2) * sd
    eps = rng.normal(0.0, innov_sd, size=(n_runs, periods, n_series))
    for t in range(1, periods):
        out[:, t, :] = rho * out[:, t - 1, :] + eps[:, t, :]
    return out


def simulate_shocks(rng, n_runs, periods, spec):
    """Return attractiveness a (n_runs, periods, 2) and market size Q (n_runs, periods)."""
    common = _ar1(rng, n_runs, periods, spec.common_sd, spec.rho, 1)
    idio = _ar1(rng, n_runs, periods, spec.idio_sd, spec.rho, 2)
    log_q = _ar1(rng, n_runs, periods, spec.log_size_sd, spec.rho, 1)[:, :, 0]
    a = spec.base_a + common + idio
    q = spec.base_q * np.exp(log_q)
    return a, q
