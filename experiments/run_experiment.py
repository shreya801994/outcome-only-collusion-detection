from pathlib import Path

import pandas as pd

from simulator.market import BertrandMarket, MarketConfig
from simulator.agents import CompetitiveAgent
from simulator.simulation import RepeatedSimulation, SimulationConfig
from simulator.auditor_view import create_auditor_view


OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)


def run_single_experiment(
    run_id: int,
    cost_1: float,
    cost_2: float,
    periods: int = 300,
):
    market = BertrandMarket(
        MarketConfig()
    )

    agent_1 = CompetitiveAgent(
        cost=cost_1,
        firm_id=1,
    )

    agent_2 = CompetitiveAgent(
        cost=cost_2,
        firm_id=2,
    )

    config = SimulationConfig(
        periods=periods,
        initial_price_1=1.472927,
        initial_price_2=1.472927,
        competitor_cost_beliefs_1=(
            1.0,
            1.1,
            1.3,
            1.6,
        ),
        competitor_cost_beliefs_2=(
            1.0,
            1.1,
            1.3,
            1.6,
        ),
        demand_shocks_enabled=False,
    )

    simulation = RepeatedSimulation(
        market=market,
        agent_1=agent_1,
        agent_2=agent_2,
        config=config,
    )

    data = simulation.run()

    data["run_id"] = run_id
    data["cost_gap"] = abs(cost_2 - cost_1)
    data["condition"] = "competitive"

    return data


def main():

    all_runs = []

    cost_gaps = [
        0.0,
        0.1,
        0.3,
        0.6,
    ]

    runs_per_condition = 5

    run_id = 0

    for cost_gap in cost_gaps:

        cost_1 = 1.0
        cost_2 = 1.0 + cost_gap

        for _ in range(runs_per_condition):

            run_id += 1

            data = run_single_experiment(
                run_id=run_id,
                cost_1=cost_1,
                cost_2=cost_2,
            )

            all_runs.append(data)

    researcher_data = pd.concat(
        all_runs,
        ignore_index=True,
    )

    researcher_path = (
        OUTPUT_DIR / "researcher_trajectories.csv"
    )

    researcher_data.to_csv(
        researcher_path,
        index=False,
    )

    auditor_runs = []

    for run_id, run_data in researcher_data.groupby(
        "run_id"
    ):

        auditor_data = create_auditor_view(
            run_data
        )

        auditor_data["run_id"] = run_id

        auditor_runs.append(
            auditor_data
        )

    auditor_data = pd.concat(
        auditor_runs,
        ignore_index=True,
    )

    auditor_path = (
        OUTPUT_DIR / "auditor_trajectories.csv"
    )

    auditor_data.to_csv(
        auditor_path,
        index=False,
    )

    print(
        f"Generated {run_id} independent runs."
    )

    print(
        f"Researcher dataset: {researcher_path}"
    )

    print(
        f"Auditor dataset: {auditor_path}"
    )

    print(
        "\nRuns by cost gap:"
    )

    print(
        researcher_data[
            ["run_id", "cost_gap", "condition"]
        ]
        .drop_duplicates()
        .groupby(
            ["cost_gap", "condition"]
        )
        .size()
    )


if __name__ == "__main__":
    main()