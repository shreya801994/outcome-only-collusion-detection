import numpy as np

from detectors.implied_cost import implied_costs, score
from simulator.equilibrium import nash, shares


def _path(prices, a1, a2, q):
    s1, s2, _ = shares(prices[:, 0], prices[:, 1], a1, a2)
    return np.column_stack([q * s1, q * s2])


def test_competitive_prices_have_constant_implied_cost_under_share_shocks():
    t = np.arange(200)
    a1 = 2.0 + 0.2 * np.sin(t / 10.0)
    a2 = 2.0 + 0.2 * np.cos(t / 7.0)
    p1, p2 = nash(1.0, 1.3, a1, a2)
    prices = np.column_stack([p1, p2])
    qty = _path(prices, a1, a2, np.ones_like(a1))
    c_hat = implied_costs(prices, qty, 0.25, market_size=np.ones_like(a1))
    assert np.allclose(c_hat[:, 0], 1.0, atol=1e-9) and np.allclose(c_hat[:, 1], 1.3, atol=1e-9)
    assert score(prices, qty, 0.25, market_size=np.ones_like(a1)) < 1e-9


def test_fixed_collusive_prices_move_implied_cost_under_share_shocks():
    t = np.arange(200)
    a1 = 2.0 + 0.2 * np.sin(t / 10.0)
    a2 = 2.0 + 0.2 * np.cos(t / 7.0)
    prices = np.column_stack([np.full(200, 1.9), np.full(200, 1.9)])
    qty = _path(prices, a1, a2, np.ones_like(a1))
    assert score(prices, qty, 0.25, market_size=np.ones_like(a1)) > 0.02


def test_fixed_collusive_prices_without_shocks_look_competitive():
    prices = np.column_stack([np.full(100, 1.9), np.full(100, 1.9)])
    qty = _path(prices, 2.0, 2.0, np.ones(100))
    assert score(prices, qty, 0.25) < 1e-12


def test_unknown_market_size_creates_spurious_instability():
    t = np.arange(200)
    q = np.exp(0.2 * np.sin(t / 9.0))
    p1, p2 = nash(1.0, 1.0)
    prices = np.column_stack([np.full(200, p1), np.full(200, p2)])
    qty = _path(prices, 2.0, 2.0, q)
    assert score(prices, qty, 0.25, market_size=q) < 1e-9          # shares known: stable
    assert score(prices, qty, 0.25) > 0.01                          # market size assumed 1: unstable


def test_batch_and_single_run_agree():
    rng = np.random.default_rng(1)
    prices = rng.uniform(1.4, 1.9, size=(3, 50, 2))
    qty = rng.uniform(0.2, 0.4, size=(3, 50, 2))
    batch = score(prices, qty, 0.25)
    single = np.array([score(prices[i], qty[i], 0.25) for i in range(3)])
    assert np.allclose(batch, single)
