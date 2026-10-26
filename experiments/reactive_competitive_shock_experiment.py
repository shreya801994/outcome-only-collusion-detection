import os
import pandas as pd

from simulator.market import BertrandMarket, MarketConfig
from simulator.reactive_agents import ReactiveCompetitiveAgent
from simulator.shocks import DemandShockConfig, CommonDemandShockGenerator


PERIODS = 300
RUNS_PER_GAP = 5

COST_GAPS = [0.0, 0.1, 0.3, 0.6]

BASE_COST_1 = 1.0

MARKET_CONFIG = MarketConfig(
    Q=1.0,
    a0=0.0,
    a1=2.0,
    a2=2.0,
    mu=0.25,
)

SHOCK_CONFIG = DemandShockConfig(
    base_market_size=1.0,
    shock_probability=0.10,
    positive_shock=0.20,
    negative_shock=-0.20,
)


def run_single_simulation(cost_gap: float, run_id: int):
    market = BertrandMarket(MARKET_CONFIG)

    cost_1 = BASE_COST_1
    cost_2 = BASE_COST_1 + cost_gap

    agent_1 = ReactiveCompetitiveAgent(
        cost=cost_1,
        firm_id=1,
        response_strength=0.50,
        adjustment_speed=0.40,
        noise_std=0.01,
        reaction_threshold=0.05,
        seed=1000 + run_id * 2,
    )

    agent_2 = ReactiveCompetitiveAgent(
        cost=cost_2,
        firm_id=2,
        response_strength=0.50,
        adjustment_speed=0.40,
        noise_std=0.01,
        reaction_threshold=0.05,
        seed=1000 + run_id * 2 + 1,
    )

    shock_generator = CommonDemandShockGenerator(
        DemandShockConfig(
            base_market_size=SHOCK_CONFIG.base_market_size,
            shock_probability=SHOCK_CONFIG.shock_probability,
            positive_shock=SHOCK_CONFIG.positive_shock,
            negative_shock=SHOCK_CONFIG.negative_shock,
            seed=5000 + run_id,
        )
    )

    reference_price = 1.472927

    price_1 = agent_1.competitive_best_response(
        competitor_price=reference_price,
        market=market,
        Q=1.0,
    )

    price_2 = agent_2.competitive_best_response(
        competitor_price=reference_price,
        market=market,
        Q=1.0,
    )

    previous_price_1 = price_1
    previous_price_2 = price_2

    researcher_records = []

    for period in range(PERIODS):

        market_size = shock_generator.next_market_size()

        result = market.step(
            p1=price_1,
            p2=price_2,
            c1=cost_1,
            c2=cost_2,
            Q=market_size,
        )

        researcher_records.append(
            {
                "run_id": run_id,
                "period": period,
                "cost_gap": cost_gap,
                "price_1": price_1,
                "price_2": price_2,
                "quantity_1": result["quantity_1"],
                "quantity_2": result["quantity_2"],
                "profit_1": result["profit_1"],
                "profit_2": result["profit_2"],
                "cost_1": cost_1,
                "cost_2": cost_2,
                "market_size": market_size,
            }
        )

        next_price_1 = agent_1.choose_price(
            competitor_price=price_2,
            previous_competitor_price=previous_price_2,
            market=market,
            Q=market_size,
        )

        next_price_2 = agent_2.choose_price(
            competitor_price=price_1,
            previous_competitor_price=previous_price_1,
            market=market,
            Q=market_size,
        )

        previous_price_1 = price_1
        previous_price_2 = price_2

        price_1 = next_price_1
        price_2 = next_price_2

    return researcher_records


def main():

    os.makedirs("data", exist_ok=True)

    all_records = []

    run_counter = 0

    for cost_gap in COST_GAPS:

        for local_run in range(RUNS_PER_GAP):

            run_counter += 1

            records = run_single_simulation(
                cost_gap=cost_gap,
                run_id=run_counter,
            )

            all_records.extend(records)

    researcher_data = pd.DataFrame(all_records)

    auditor_columns = [
        "run_id",
        "period",
        "price_1",
        "price_2",
        "quantity_1",
        "quantity_2",
    ]

    auditor_data = researcher_data[auditor_columns].copy()

    researcher_path = "data/reactive_shock_researcher_trajectories.csv"
    auditor_path = "data/reactive_shock_auditor_trajectories.csv"

    researcher_data.to_csv(
        researcher_path,
        index=False,
    )

    auditor_data.to_csv(
        auditor_path,
        index=False,
    )

    print("Reactive competitive shock experiment completed.")
    print(f"Researcher data: {researcher_path}")
    print(f"Auditor data:    {auditor_path}")

    summary = (
        researcher_data
        .groupby("cost_gap")
        .agg(
            mean_price_1=("price_1", "mean"),
            mean_price_2=("price_2", "mean"),
            mean_profit_1=("profit_1", "mean"),
            mean_profit_2=("profit_2", "mean"),
            mean_market_size=("market_size", "mean"),
        )
        .reset_index()
    )

    print("\nSummary:")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()