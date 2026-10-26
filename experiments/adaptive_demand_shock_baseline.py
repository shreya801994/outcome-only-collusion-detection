from pathlib import Path

from simulator.market import BertrandMarket, MarketConfig
from simulator.adaptive_agents import AdaptiveCompetitiveAgent
from simulator.shocks import (
    CommonDemandShockGenerator,
    DemandShockConfig,
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
    # Independent adaptive agents
    # -----------------------------------------

    agent_1 = AdaptiveCompetitiveAgent(
        cost=1.0,
        firm_id=1,
        base_price=1.472927,
        reference_market_size=1.0,
        shock_sensitivity=0.40,
    )

    agent_2 = AdaptiveCompetitiveAgent(
        cost=1.0,
        firm_id=2,
        base_price=1.472927,
        reference_market_size=1.0,
        shock_sensitivity=0.60,
    )

    # -----------------------------------------
    # Common demand shocks
    # -----------------------------------------

    shock_config = DemandShockConfig(
        base_market_size=1.0,
        shock_probability=0.20,
        positive_shock=0.20,
        negative_shock=-0.20,
        seed=42,
    )

    shock_generator = CommonDemandShockGenerator(
        shock_config
    )

    records = []

    # -----------------------------------------
    # Simulation
    # -----------------------------------------

    for t in range(300):

        market_size = (
            shock_generator.next_market_size()
        )

        price_1 = agent_1.choose_price(
            market_size=market_size
        )

        price_2 = agent_2.choose_price(
            market_size=market_size
        )

        result = market.step(
            p1=price_1,
            p2=price_2,
            c1=agent_1.cost,
            c2=agent_2.cost,
            Q=market_size,
        )

        records.append(
            {
                "period": t,
                "price_1": price_1,
                "price_2": price_2,
                "quantity_1": result["quantity_1"],
                "quantity_2": result["quantity_2"],
                "profit_1": result["profit_1"],
                "profit_2": result["profit_2"],
                "cost_1": agent_1.cost,
                "cost_2": agent_2.cost,
                "market_size": market_size,
            }
        )

    # -----------------------------------------
    # Save
    # -----------------------------------------

    import pandas as pd

    data = pd.DataFrame(records)

    output_path = (
        output_dir
        / "adaptive_competitive_demand_shocks.csv"
    )

    data.to_csv(
        output_path,
        index=False,
    )

    # -----------------------------------------
    # Summary
    # -----------------------------------------

    print("=" * 60)
    print("Adaptive Competitive Agents + Common Demand Shocks")
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

    # -----------------------------------------
    # Price synchronization
    # -----------------------------------------

    price_difference = (
        data["price_1"]
        - data["price_2"]
    ).abs()

    print("\nAverage absolute price difference:")
    print(price_difference.mean())

    print("\nMaximum absolute price difference:")
    print(price_difference.max())

    print("\nFirst 20 observations:")
    print(
        data[
            [
                "period",
                "market_size",
                "price_1",
                "price_2",
            ]
        ].head(20)
    )

    print("\nSaved to:")
    print(output_path)


if __name__ == "__main__":
    main()