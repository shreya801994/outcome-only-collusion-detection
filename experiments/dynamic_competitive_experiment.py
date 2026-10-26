from pathlib import Path

import pandas as pd

from simulator.market import BertrandMarket, MarketConfig
from simulator.adaptive_agents import AdaptiveCompetitiveAgent
from simulator.shocks import (
    CommonDemandShockGenerator,
    DemandShockConfig,
)
from simulator.auditor_view import create_auditor_view


OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)

COST_GAPS = [0.0, 0.1, 0.3, 0.6]
RUNS_PER_GAP = 5
PERIODS = 300


def run_single_simulation(
    run_id: int,
    cost_gap: float,
    seed: int,
):
    market = BertrandMarket(
        MarketConfig()
    )

    agent_1 = AdaptiveCompetitiveAgent(
        cost=1.0,
        firm_id=1,
        shock_sensitivity=0.40,
        adjustment_speed=0.40,
        noise_std=0.01,
        seed=seed,
    )

    agent_2 = AdaptiveCompetitiveAgent(
        cost=1.0 + cost_gap,
        firm_id=2,
        shock_sensitivity=0.60,
        adjustment_speed=0.40,
        noise_std=0.01,
        seed=seed + 1000,
    )

    shock_config = DemandShockConfig(
        base_market_size=1.0,
        shock_probability=0.10,
        positive_shock=0.20,
        negative_shock=-0.20,
        seed=seed + 2000,
    )

    shock_generator = CommonDemandShockGenerator(
        shock_config
    )

    records = []

    agent_1.reset()
    agent_2.reset()

    for t in range(PERIODS):

        market_size = shock_generator.next_market_size()

        price_1 = agent_1.choose_price(
            market_size
        )

        price_2 = agent_2.choose_price(
            market_size
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
                "run_id": run_id,
                "cost_gap": cost_gap,
                "condition": "dynamic_competitive",
            }
        )

    return pd.DataFrame(records)


def main():

    all_runs = []

    run_id = 0

    for cost_gap in COST_GAPS:

        for _ in range(RUNS_PER_GAP):

            run_id += 1

            seed = 10000 + run_id

            df = run_single_simulation(
                run_id=run_id,
                cost_gap=cost_gap,
                seed=seed,
            )

            all_runs.append(df)

    researcher_data = pd.concat(
        all_runs,
        ignore_index=True,
    )

    auditor_data = create_auditor_view(
        researcher_data
    )

    researcher_path = (
        OUTPUT_DIR
        / "dynamic_researcher_trajectories.csv"
    )

    auditor_path = (
        OUTPUT_DIR
        / "dynamic_auditor_trajectories.csv"
    )

    researcher_data.to_csv(
        researcher_path,
        index=False,
    )

    auditor_data["run_id"] = researcher_data[
        "run_id"
    ]

    auditor_data.to_csv(
        auditor_path,
        index=False,
    )

    print(
        f"Generated {run_id} independent dynamic runs."
    )

    print(
        "\nResearcher columns:"
    )

    print(
        list(researcher_data.columns)
    )

    print(
        "\nAuditor columns:"
    )

    print(
        list(auditor_data.columns)
    )

    print(
        "\nCost-gap counts:"
    )

    print(
        researcher_data[
            ["run_id", "cost_gap"]
        ]
        .drop_duplicates()
        .groupby("cost_gap")
        .size()
    )


if __name__ == "__main__":
    main()