from simulator.market import BertrandMarket, MarketConfig
from simulator.agents import CompetitiveAgent


COST_BELIEFS = [1.0, 1.1, 1.3, 1.6]


def test_competitive_agent_finds_nash_price_under_known_cost():
    market = BertrandMarket(MarketConfig())

    agent_1 = CompetitiveAgent(
        cost=1.0,
        firm_id=1
    )

    agent_2 = CompetitiveAgent(
        cost=1.0,
        firm_id=2
    )

    equilibrium_price = 1.472927

    best_response_1 = agent_1.best_response(
        competitor_price=equilibrium_price,
        market=market,
        competitor_cost_beliefs=[1.0]
    )

    best_response_2 = agent_2.best_response(
        competitor_price=equilibrium_price,
        market=market,
        competitor_cost_beliefs=[1.0]
    )

    assert abs(best_response_1 - equilibrium_price) < 1e-4
    assert abs(best_response_2 - equilibrium_price) < 1e-4


def test_own_private_cost_affects_best_response():
    market = BertrandMarket(MarketConfig())

    low_cost_agent = CompetitiveAgent(
        cost=1.0,
        firm_id=1
    )

    high_cost_agent = CompetitiveAgent(
        cost=1.6,
        firm_id=1
    )

    competitor_price = 1.5

    low_cost_price = low_cost_agent.best_response(
        competitor_price=competitor_price,
        market=market,
        competitor_cost_beliefs=[1.0]
    )

    high_cost_price = high_cost_agent.best_response(
        competitor_price=competitor_price,
        market=market,
        competitor_cost_beliefs=[1.0]
    )

    assert high_cost_price > low_cost_price


def test_belief_probabilities_are_normalized():
    market = BertrandMarket(MarketConfig())

    agent = CompetitiveAgent(
        cost=1.0,
        firm_id=1
    )

    price_equal_weights = agent.best_response(
        competitor_price=1.5,
        market=market,
        competitor_cost_beliefs=[1.0, 1.6],
        belief_probabilities=[0.5, 0.5]
    )

    price_scaled_weights = agent.best_response(
        competitor_price=1.5,
        market=market,
        competitor_cost_beliefs=[1.0, 1.6],
        belief_probabilities=[1.0, 1.0]
    )

    assert abs(
        price_equal_weights - price_scaled_weights
    ) < 1e-8


def test_invalid_beliefs_are_rejected():
    market = BertrandMarket(MarketConfig())

    agent = CompetitiveAgent(
        cost=1.0,
        firm_id=1
    )

    try:
        agent.best_response(
            competitor_price=1.5,
            market=market,
            competitor_cost_beliefs=[]
        )
        assert False
    except ValueError:
        pass


def test_unilateral_deviation_does_not_improve_profit():
    market = BertrandMarket(MarketConfig())

    equilibrium_price = 1.472927

    equilibrium_profit, _ = market.profits(
        p1=equilibrium_price,
        p2=equilibrium_price,
        c1=1.0,
        c2=1.0
    )

    deviation_profit, _ = market.profits(
        p1=equilibrium_price + 0.1,
        p2=equilibrium_price,
        c1=1.0,
        c2=1.0
    )

    assert deviation_profit < equilibrium_profit