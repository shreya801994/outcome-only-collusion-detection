from simulator.collusion_agents import (
    RewardPunishmentAgent,
)


def test_agent_starts_at_high_price():

    agent = RewardPunishmentAgent(
        cost=1.0
    )

    price = agent.choose_price(
        competitor_price=1.90,
        previous_competitor_price=1.90,
    )

    assert price == 1.90


def test_agent_detects_downward_deviation():

    agent = RewardPunishmentAgent(
        cost=1.0
    )

    price = agent.choose_price(
        competitor_price=1.40,
        previous_competitor_price=1.90,
    )

    assert price == 1.10


def test_agent_does_not_punish_small_change():

    agent = RewardPunishmentAgent(
        cost=1.0,
        deviation_tolerance=0.05,
    )

    price = agent.choose_price(
        competitor_price=1.87,
        previous_competitor_price=1.90,
    )

    assert price == 1.90


def test_punishment_has_fixed_duration():

    agent = RewardPunishmentAgent(
        cost=1.0,
        punishment_periods=3,
    )

    prices = []

    # First observation detects deviation.
    prices.append(
        agent.choose_price(
            competitor_price=1.40,
            previous_competitor_price=1.90,
        )
    )

    # Two additional punishment periods.
    prices.append(
        agent.choose_price(
            competitor_price=1.10,
            previous_competitor_price=1.40,
        )
    )

    prices.append(
        agent.choose_price(
            competitor_price=1.10,
            previous_competitor_price=1.10,
        )
    )

    # Punishment is now finished.
    prices.append(
        agent.choose_price(
            competitor_price=1.10,
            previous_competitor_price=1.10,
        )
    )

    assert prices == [
        1.10,
        1.10,
        1.10,
        1.90,
    ]


def test_punishment_does_not_restart():

    agent = RewardPunishmentAgent(
        cost=1.0,
        punishment_periods=3,
    )

    # Start punishment.
    agent.choose_price(
        competitor_price=1.40,
        previous_competitor_price=1.90,
    )

    # Finish punishment.
    agent.choose_price(
        competitor_price=1.10,
        previous_competitor_price=1.40,
    )

    agent.choose_price(
        competitor_price=1.10,
        previous_competitor_price=1.10,
    )

    # This must restore cooperation.
    price = agent.choose_price(
        competitor_price=1.10,
        previous_competitor_price=1.10,
    )

    assert price == 1.90

    # And it should remain cooperative.
    price = agent.choose_price(
        competitor_price=1.10,
        previous_competitor_price=1.10,
    )

    assert price == 1.90


def test_reset_clears_punishment_state():

    agent = RewardPunishmentAgent(
        cost=1.0,
        punishment_periods=5,
    )

    agent.choose_price(
        competitor_price=1.40,
        previous_competitor_price=1.90,
    )

    assert agent.in_punishment is True

    agent.reset()

    assert agent.in_punishment is False
    assert agent.punishment_remaining == 0

    price = agent.choose_price(
        competitor_price=1.90,
        previous_competitor_price=1.90,
    )

    assert price == 1.90