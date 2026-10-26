from simulator.shocks import (
    CommonDemandShockGenerator,
    DemandShockConfig
)


def test_shock_generator_returns_valid_market_sizes():
    config = DemandShockConfig(
        base_market_size=1.0,
        shock_probability=0.2,
        positive_shock=0.2,
        negative_shock=-0.2,
        seed=42
    )

    generator = CommonDemandShockGenerator(config)

    values = [
        generator.next_market_size()
        for _ in range(100)
    ]

    assert all(
        value in {0.8, 1.0, 1.2}
        for value in values
    )


def test_shock_generator_is_reproducible():
    config = DemandShockConfig(seed=42)

    generator_1 = CommonDemandShockGenerator(config)
    generator_2 = CommonDemandShockGenerator(config)

    values_1 = [
        generator_1.next_market_size()
        for _ in range(20)
    ]

    values_2 = [
        generator_2.next_market_size()
        for _ in range(20)
    ]

    assert values_1 == values_2


def test_positive_and_negative_shocks_are_possible():
    config = DemandShockConfig(
        shock_probability=1.0,
        seed=42
    )

    generator = CommonDemandShockGenerator(config)

    values = {
        generator.next_market_size()
        for _ in range(100)
    }

    assert 0.8 in values
    assert 1.2 in values