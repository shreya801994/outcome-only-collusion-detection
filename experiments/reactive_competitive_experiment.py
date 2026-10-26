from pathlib import Path

import pandas as pd

from simulator.market import BertrandMarket, MarketConfig
from simulator.reactive_agents import ReactiveCompetitiveAgent
from simulator.auditor_view import create_auditor_view


PERIODS = 300
RUNS_PER_COST_GAP = 100

COST_GAPS = [0.0, 0.1, 0.3, 0.6]

RESEARCHER_OUTPUT = Path(
    "data/reactive_researcher_trajectories.csv"
)

AUDITOR_OUTPUT = Path(
    "data/reactive_auditor_trajectories.csv"
)


def run_single_experiment(
    run_id: int,
    cost_gap: float,
    seed: int,
):

    market = BertrandMarket(
        MarketConfig()
    )

    cost_1 = 1.0
    cost_2 = 1.0 + cost_gap

    agent_1 = ReactiveCompetitiveAgent(
        cost=cost_1,
        firm_id=1,
        response_strength=0.50,
        adjustment_speed=0.40,
        noise_std=0.01,
        seed=seed,
    )

    agent_2 = ReactiveCompetitiveAgent(
        cost=cost_2,
        firm_id=2,
        response_strength=0.50,
        adjustment_speed=0.40,
        noise_std=0.01,
        seed=seed + 1000,
    )

    price_1 = agent_1.competitive_best_response(
        competitor_price=1.472927,
        market=market,
        Q=1.0,
    )

    price_2 = agent_2.competitive_best_response(
        competitor_price=1.472927,
        market=market,
        Q=1.0,
    )

    previous_price_1 = price_1
    previous_price_2 = price_2

    records = []

    for period in range(PERIODS):

        result = market.step(
            p1=price_1,
            p2=price_2,
            c1=cost_1,
            c2=cost_2,
            Q=1.0,
        )

        records.append(
            {
                "run_id": run_id,
                "period": period,
                "price_1": price_1,
                "price_2": price_2,
                "quantity_1": result["quantity_1"],
                "quantity_2": result["quantity_2"],
                "profit_1": result["profit_1"],
                "profit_2": result["profit_2"],
                "cost_1": cost_1,
                "cost_2": cost_2,
                "market_size": 1.0,
                "cost_gap": cost_gap,
                "condition": "reactive_competitive",
            }
        )

        next_price_1 = agent_1.choose_price(
            competitor_price=price_2,
            previous_competitor_price=previous_price_2,
            market=market,
            Q=1.0,
        )

        next_price_2 = agent_2.choose_price(
            competitor_price=price_1,
            previous_competitor_price=previous_price_1,
            market=market,
            Q=1.0,
        )

        previous_price_1 = price_1
        previous_price_2 = price_2

        price_1 = next_price_1
        price_2 = next_price_2

    return pd.DataFrame(records)


def main():

    all_runs = []

    run_id = 1

    for cost_gap in COST_GAPS:

        for repetition in range(RUNS_PER_COST_GAP):

            seed = 1000 + run_id

            run_data = run_single_experiment(
                run_id=run_id,
                cost_gap=cost_gap,
                seed=seed,
            )

            all_runs.append(run_data)

            print(
                f"Completed run {run_id}: "
                f"Δc={cost_gap}"
            )

            run_id += 1

    researcher_data = pd.concat(
        all_runs,
        ignore_index=True,
    )

    auditor_data = create_auditor_view(
        researcher_data
    )

    auditor_data.insert(
        0,
        "run_id",
        researcher_data["run_id"].values,
    )

    RESEARCHER_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    researcher_data.to_csv(
        RESEARCHER_OUTPUT,
        index=False,
    )

    auditor_data.to_csv(
        AUDITOR_OUTPUT,
        index=False,
    )

    print("\nExperiment completed.")

    print(
        f"Researcher data: {RESEARCHER_OUTPUT}"
    )

    print(
        f"Auditor data: {AUDITOR_OUTPUT}"
    )

    print(
        f"\nTotal runs: "
        f"{researcher_data['run_id'].nunique()}"
    )


if __name__ == "__main__":
    main()