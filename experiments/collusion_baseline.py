from pathlib import Path

from simulator.market import BertrandMarket, MarketConfig
from simulator.collusion_agents import RewardPunishmentAgent
from simulator.simulation import (
    RepeatedSimulation,
    SimulationConfig,
)


def main():

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
    # Controlled collusive agents
    # -----------------------------------------

    agent_1 = RewardPunishmentAgent(
        cost=1.0,
        high_price=1.90,
        punishment_price=1.10,
        deviation_tolerance=0.05,
        punishment_periods=5,
    )

    agent_2 = RewardPunishmentAgent(
        cost=1.0,
        high_price=1.90,
        punishment_price=1.10,
        deviation_tolerance=0.05,
        punishment_periods=5,
    )

    # -----------------------------------------
    # Simulation
    # -----------------------------------------

    config = SimulationConfig(
        periods=300,
        initial_price_1=1.90,
        initial_price_2=1.90,
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

    output_path = (
        output_dir / "collusive_reward_punishment.csv"
    )

    data.to_csv(
        output_path,
        index=False,
    )

    # -----------------------------------------
    # Summary
    # -----------------------------------------

    print("Periods:", len(data))

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

    print("\nFirst 20 periods:")
    print(
        data[
            [
                "period",
                "price_1",
                "price_2",
            ]
        ].head(20)
    )

    print("\nSaved to:")
    print(output_path)


if __name__ == "__main__":
    main()