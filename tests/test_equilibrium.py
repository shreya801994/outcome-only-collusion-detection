import numpy as np
import pandas as pd
from pathlib import Path

from simulator.agents import CompetitiveAgent
from simulator.equilibrium import best_response, implied_cost, joint_profit, nash, shares
from simulator.market import BertrandMarket, MarketConfig

ROOT = Path(__file__).resolve().parents[1]


def test_shares_match_market_module():
    market = BertrandMarket(MarketConfig())
    for p1, p2 in [(1.5, 1.7), (1.9, 1.9), (1.2, 2.5)]:
        q1, q2 = market.demand(p1, p2)
        s1, s2, s0 = shares(p1, p2)
        assert abs(s1 - q1) < 1e-14 and abs(s2 - q2) < 1e-14
        assert abs(s0 + s1 + s2 - 1.0) < 1e-14


def test_closed_form_best_response_matches_numerical_optimiser():
    market = BertrandMarket(MarketConfig())
    rng = np.random.default_rng(0)
    for _ in range(20):
        cost = rng.uniform(0.6, 1.6)
        rival = rng.uniform(1.2, 2.2)
        numerical = CompetitiveAgent(cost=cost, firm_id=1).best_response(rival, market, (1.0,))
        closed = best_response(cost, 2.0, rival, 2.0)
        assert abs(numerical - closed) < 1e-4  # optimiser tolerance is about 1e-5


def test_nash_matches_reference_table():
    ref = pd.read_csv(ROOT / "evaluation" / "competitive_equilibrium_reference.csv")
    for _, row in ref.iterrows():
        p1, p2 = nash(row.cost_1, row.cost_2)
        assert abs(p1 - row.equilibrium_price_1) < 1e-5
        assert abs(p2 - row.equilibrium_price_2) < 1e-5


def test_joint_profit_symmetric_baseline_and_first_order_condition():
    p1, p2 = joint_profit(1.0, 1.0)
    assert abs(p1 - 1.92498) < 1e-4 and abs(p2 - 1.92498) < 1e-4
    _, _, s0 = shares(p1, p2)
    assert abs((p1 - 1.0) - 0.25 / s0) < 1e-10


def test_any_admissible_price_pair_is_a_nash_equilibrium_for_its_implied_costs():
    """Observational equivalence: rationalise each outcome with c_hat and check best responses."""
    grid = [(1.9, 1.9), (1.6, 1.8), (2.1, 1.7), (1.47, 1.47)]
    for p1, p2 in grid:
        s1, s2, _ = shares(p1, p2)
        c1, c2 = implied_cost(p1, s1), implied_cost(p2, s2)
        assert c1 >= 0 and c2 >= 0
        assert abs(best_response(c1, 2.0, p2, 2.0) - p1) < 1e-12
        assert abs(best_response(c2, 2.0, p1, 2.0) - p2) < 1e-12
        n1, n2 = nash(c1, c2)
        assert abs(n1 - p1) < 1e-10 and abs(n2 - p2) < 1e-10


def test_market_size_does_not_enter_prices():
    # shares (hence best responses and Nash prices) do not depend on market size
    s_small = shares(1.6, 1.7)
    market = BertrandMarket(MarketConfig())
    q_big = market.demand(1.6, 1.7, Q=1.7)
    assert abs(q_big[0] / 1.7 - s_small[0]) < 1e-14
