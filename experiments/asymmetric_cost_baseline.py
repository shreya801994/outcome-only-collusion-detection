from pathlib import Path

from simulator.market import BertrandMarket, MarketConfig
from simulator.agents import CompetitiveAgent
from simulator.simulation import RepeatedSimulation, SimulationConfig


def run_cost_gap_experiment(cost_2):
    market = BertrandMarket(MarketConfig())

    agent_1 = CompetitiveAgent(
        cost=1.0,
        firm_id=1
    )

    agent_2 = CompetitiveAgent(
        cost=cost_2,
        firm_id=2
    )

    config = SimulationConfig(
        periods=300,
        initial_price_1=1.472927,
        initial_price_2=1.472927
    )

    simulation = RepeatedSimulation(
        market=market,
        agent_1=agent_1,
        agent_2=agent_2,
        config=config
    )

    return simulation.run()


def main():
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    cost_1 = 1.0
    cost_values = [1.0, 1.1, 1.3, 1.6]

    for cost_2 in cost_values:
        cost_gap = abs(cost_2 - cost_1)

        data = run_cost_gap_experiment(cost_2)

        filename = (
            f"competitive_cost_gap_{cost_gap:.1f}.csv"
        )

        output_path = output_dir / filename
        data.to_csv(output_path, index=False)

        print("=" * 60)
        print(f"Cost 1: {cost_1}")
        print(f"Cost 2: {cost_2}")
        print(f"Cost gap: {cost_gap:.1f}")
        print(f"Periods: {len(data)}")

        print("\nAverage prices:")
        print(data[["price_1", "price_2"]].mean())

        print("\nAverage quantities:")
        print(data[["quantity_1", "quantity_2"]].mean())

        print("\nAverage profits:")
        print(data[["profit_1", "profit_2"]].mean())

        print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()