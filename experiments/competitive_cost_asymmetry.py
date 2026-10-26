from pathlib import Path

from simulator.market import BertrandMarket, MarketConfig
from simulator.agents import CompetitiveAgent
from simulator.simulation import (
    RepeatedSimulation,
    SimulationConfig,
)


def run_condition(cost_1, cost_2, output_name):

    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    # -----------------------------------------
    # Market configuration
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
    # Repeated simulation
    # -----------------------------------------

    config = SimulationConfig(
        periods=300,
        initial_price_1=1.472927,
        initial_price_2=1.472927,
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
    print(f"Costs: c1={cost_1}, c2={cost_2}")
    print("=" * 60)

    print("\nPeriods:")
    print(len(data))

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

    print("\nPrice range:")
    print(
        data[
            ["price_1", "price_2"]
        ].agg(["min", "max"])
    )

    print("\nSaved to:")
    print(output_path)


def main():

    cost_gaps = [0.0, 0.1, 0.3, 0.6]

    for gap in cost_gaps:

        run_condition(
            cost_1=1.0,
            cost_2=1.0 + gap,
            output_name=f"competitive_cost_gap_{gap:.1f}_new.csv",
        )


if __name__ == "__main__":
    main()