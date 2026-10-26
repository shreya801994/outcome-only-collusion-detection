from simulator.adaptive_agents import (
    AdaptiveCompetitiveAgent,
)


def test_base_price_at_reference_market_size():

    agent = AdaptiveCompetitiveAgent(
        cost=1.0,
        firm_id=1,
        noise_std=0.0,
    )

    agent.reset()

    price = agent.choose_price(
        market_size=1.0
    )

    assert price == 1.472927


def test_positive_demand_shock_increases_target_price():

    agent = AdaptiveCompetitiveAgent(
        cost=1.0,
        firm_id=1,
        shock_sensitivity=0.5,
        noise_std=0.0,
    )

    target = agent.target_price(
        market_size=1.2
    )

    assert target > agent.base_price


def test_negative_demand_shock_decreases_target_price():

    agent = AdaptiveCompetitiveAgent(
        cost=1.0,
        firm_id=1,
        shock_sensitivity=0.5,
        noise_std=0.0,
    )

    target = agent.target_price(
        market_size=0.8
    )

    assert target < agent.base_price


def test_price_moves_toward_target():

    agent = AdaptiveCompetitiveAgent(
        cost=1.0,
        firm_id=1,
        shock_sensitivity=0.5,
        adjustment_speed=0.5,
        noise_std=0.0,
    )

    agent.reset()

    old_price = agent.current_price

    new_price = agent.choose_price(
        market_size=1.2
    )

    target = agent.target_price(
        market_size=1.2
    )

    assert old_price < new_price < target


def test_noise_is_reproducible_with_seed():

    agent_1 = AdaptiveCompetitiveAgent(
        cost=1.0,
        firm_id=1,
        noise_std=0.01,
        seed=42,
    )

    agent_2 = AdaptiveCompetitiveAgent(
        cost=1.0,
        firm_id=1,
        noise_std=0.01,
        seed=42,
    )

    prices_1 = [
        agent_1.choose_price(1.2)
        for _ in range(10)
    ]

    prices_2 = [
        agent_2.choose_price(1.2)
        for _ in range(10)
    ]

    assert prices_1 == prices_2


def test_different_seeds_can_generate_different_paths():

    agent_1 = AdaptiveCompetitiveAgent(
        cost=1.0,
        firm_id=1,
        noise_std=0.01,
        seed=42,
    )

    agent_2 = AdaptiveCompetitiveAgent(
        cost=1.0,
        firm_id=1,
        noise_std=0.01,
        seed=43,
    )

    prices_1 = [
        agent_1.choose_price(1.2)
        for _ in range(10)
    ]

    prices_2 = [
        agent_2.choose_price(1.2)
        for _ in range(10)
    ]

    assert prices_1 != prices_2


def test_price_bounds_are_respected():

    agent = AdaptiveCompetitiveAgent(
        cost=1.0,
        firm_id=1,
        price_min=0.5,
        price_max=4.0,
        noise_std=0.0,
    )

    for _ in range(20):

        price = agent.choose_price(
            market_size=2.0
        )

        assert 0.5 <= price <= 4.0


def test_reset_restores_base_price():

    agent = AdaptiveCompetitiveAgent(
        cost=1.0,
        firm_id=1,
        noise_std=0.0,
    )

    agent.choose_price(1.2)

    assert agent.current_price != agent.base_price

    agent.reset()

    assert agent.current_price == agent.base_price