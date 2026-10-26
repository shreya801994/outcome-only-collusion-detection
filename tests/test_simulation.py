from simulator.market import BertrandMarket, MarketConfig
from simulator.agents import CompetitiveAgent
from simulator.simulation import RepeatedSimulation, SimulationConfig


def test_simulation_returns_expected_number_of_periods():
    market = BertrandMarket(MarketConfig())

    agent_1 = CompetitiveAgent(
        cost=1.0,
        firm_id=1
    )

    agent_2 = CompetitiveAgent(
        cost=1.0,
        firm_id=2
    )

    config = SimulationConfig(periods=20)

    simulation = RepeatedSimulation(
        market=market,
        agent_1=agent_1,
        agent_2=agent_2,
        config=config
    )

    data = simulation.run()

    assert len(data) == 20


def test_simulation_contains_required_observables():
    market = BertrandMarket(MarketConfig())

    agent_1 = CompetitiveAgent(
        cost=1.0,
        firm_id=1
    )

    agent_2 = CompetitiveAgent(
        cost=1.0,
        firm_id=2
    )

    config = SimulationConfig(periods=5)

    simulation = RepeatedSimulation(
        market=market,
        agent_1=agent_1,
        agent_2=agent_2,
        config=config
    )

    data = simulation.run()

    required_columns = {
        "period",
        "price_1",
        "price_2",
        "quantity_1",
        "quantity_2",
        "profit_1",
        "profit_2",
        "cost_1",
        "cost_2"
    }

    assert required_columns.issubset(data.columns)


def test_competitive_prices_converge_toward_nash():
    market = BertrandMarket(MarketConfig())

    agent_1 = CompetitiveAgent(
        cost=1.0,
        firm_id=1
    )

    agent_2 = CompetitiveAgent(
        cost=1.0,
        firm_id=2
    )

    config = SimulationConfig(
        periods=50,
        initial_price_1=1.0,
        initial_price_2=2.5
    )

    simulation = RepeatedSimulation(
        market=market,
        agent_1=agent_1,
        agent_2=agent_2,
        config=config
    )

    data = simulation.run()

    final_price_1 = data.iloc[-1]["price_1"]
    final_price_2 = data.iloc[-1]["price_2"]

    assert abs(final_price_1 - 1.472927) < 1e-3
    assert abs(final_price_2 - 1.472927) < 1e-3