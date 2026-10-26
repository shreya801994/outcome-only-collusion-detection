from simulator.market import BertrandMarket, MarketConfig
from simulator.reactive_agents import ReactiveCompetitiveAgent


def test_reactive_agent_returns_valid_price():
    market = BertrandMarket(MarketConfig())

    agent = ReactiveCompetitiveAgent(
        cost=1.0,
        firm_id=1,
        seed=42,
    )

    price = agent.choose_price(
        competitor_price=1.40,
        previous_competitor_price=1.90,
        market=market,
    )

    assert 0.5 <= price <= 4.0


def test_reactive_agent_responds_to_price_cut():
    market = BertrandMarket(MarketConfig())

    agent = ReactiveCompetitiveAgent(
        cost=1.0,
        firm_id=1,
        response_strength=0.5,
        adjustment_speed=1.0,
        noise_std=0.0,
        seed=42,
    )

    initial_price = agent.competitive_best_response(
        competitor_price=1.47,
        market=market,
    )

    agent.current_price = initial_price

    new_price = agent.choose_price(
        competitor_price=1.20,
        previous_competitor_price=1.47,
        market=market,
    )

    assert 0.5 <= new_price <= 4.0


def test_high_cost_agent_does_not_start_below_cost():
    market = BertrandMarket(MarketConfig())

    agent = ReactiveCompetitiveAgent(
        cost=1.6,
        firm_id=2,
        noise_std=0.0,
        seed=42,
    )

    price = agent.competitive_best_response(
        competitor_price=1.47,
        market=market,
    )

    assert price >= agent.cost


def test_reactive_agent_reset():
    market = BertrandMarket(MarketConfig())

    agent = ReactiveCompetitiveAgent(
        cost=1.0,
        firm_id=1,
        seed=42,
    )

    agent.choose_price(
        competitor_price=1.47,
        previous_competitor_price=1.47,
        market=market,
    )

    assert agent.current_price is not None

    agent.reset()

    assert agent.current_price is None