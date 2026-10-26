from pathlib import Path

from simulator.market import BertrandMarket, MarketConfig
from simulator.agents import CompetitiveAgent
from simulator.simulation import (
    RepeatedSimulation,
    SimulationConfig,
)
from simulator.shocks import DemandShockConfig


def run_condition(
    cost_1,
    cost_2,
    shock_probability,
    positive_shock,
    negative_shock,
    seed,
    output_name,
):

    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    # -----------------------------------------
    # Market
    # -----------------------------------------

    market = BertrandMarket(
        MarketConfig(
            Q=1.0,
            a0=0.0,
            a1=2.0,
            a2=2.0,
            mu=0.25,
        )
    )

    # -----------------------------------------
    # Competitive agents
    # -----------------------------------------

    agent_1 = CompetitiveAgent(
        cost=cost_1,
        firm_id=1,
    )

    agent_2 = CompetitiveAgent(
        cost=cost_2,
        firm_id=2,
    )

    # -----------------------------------------
    # Common demand shock
    # -----------------------------------------

    shock_config = DemandShockConfig(
        base_market_size=1.0,
        shock_probability=shock_probability,
        positive_shock=positive_shock,
        negative_shock=negative_shock,
        seed=seed,
    )

    # -----------------------------------------
    # Simulation
    # -----------------------------------------

    config = SimulationConfig(
        periods=300,
        initial_price_1=1.472927,
        initial_price_2=1.472927,
        demand_shocks_enabled=True,
        demand_shock_config=shock_config,
    )

    simulation = RepeatedSimulation(
        market=market,
        agent_1=agent_1,
        agent_2=agent_2,
        config=config,
    )

    data = simulation.run()

    # -----------------------------------------
    # Save
    # -----------------------------------------

    output_path = output_dir / output_name

    data.to_csv(
        output_path,
        index=False,
    )

    # -----------------------------------------
    # Summary
    # -----------------------------------------

    print("=" * 60)
    print(
        f"Costs: c1={cost_1}, c2={cost_2}"
    )
    print(
        f"Shock probability: {shock_probability}"
    )
    print(
        f"Positive shock: +{positive_shock:.2f}"
    )
    print(
        f"Negative shock: {negative_shock:.2f}"
    )
    print("=" * 60)

    print("\nPeriods:")
    print(len(data))

    print("\nMarket-size distribution:")
    print(
        data[
            "market_size"
        ].value_counts().sort_index()
    )

    print("\nAverage prices:")
    print(
        data[
            ["price_1", "price_2"]
        ].mean()
    )

    print("\nAverage quantities:")
    print(
        data[
            ["quantity_1", "quantity_2"]
        ].mean()
    )

    print("\nAverage profits:")
    print(
        data[
            ["profit_1", "profit_2"]
        ].mean()
    )

    print("\nSaved to:")
    print(output_path)


def main():

    run_condition(
        cost_1=1.0,
        cost_2=1.0,
        shock_probability=0.10,
        positive_shock=0.20,
        negative_shock=-0.20,
        seed=42,
        output_name="competitive_demand_shocks.csv",
    )


if __name__ == "__main__":
    main()