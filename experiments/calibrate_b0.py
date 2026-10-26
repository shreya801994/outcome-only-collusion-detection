from pathlib import Path

import pandas as pd
import numpy as np

from simulator.market import BertrandMarket, MarketConfig
from simulator.reactive_agents import ReactiveCompetitiveAgent


PERIODS = 300
CALIBRATION_RUNS = 100

OUTPUT_PATH = Path(
    "data/b0_calibration_runs.csv"
)

THRESHOLD_PATH = Path(
    "results/b0_threshold.txt"
)


def run_single_calibration(run_id: int, seed: int):

    market = BertrandMarket(
        MarketConfig()
    )

    cost_1 = 1.0
    cost_2 = 1.0

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

    prices = []

    for period in range(PERIODS):

        prices.append(
            {
                "run_id": run_id,
                "period": period,
                "price_1": price_1,
                "price_2": price_2,
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

    return pd.DataFrame(prices)


def main():

    all_runs = []

    for run_id in range(1, CALIBRATION_RUNS + 1):

        seed = 5000 + run_id

        run_data = run_single_calibration(
            run_id=run_id,
            seed=seed,
        )

        all_runs.append(run_data)

        print(
            f"Completed calibration run {run_id}/"
            f"{CALIBRATION_RUNS}"
        )

    data = pd.concat(
        all_runs,
        ignore_index=True,
    )

    run_scores = (
        data
        .assign(
            average_price=(
                data["price_1"] +
                data["price_2"]
            ) / 2.0
        )
        .groupby("run_id")["average_price"]
        .mean()
        .reset_index()
    )

    threshold = np.quantile(
        run_scores["average_price"],
        0.95,
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    THRESHOLD_PATH.write_text(
        f"{threshold:.10f}\n",
        encoding="utf-8",
    )

    print("\nB0 calibration completed.")

    print(
        f"Calibration runs: "
        f"{CALIBRATION_RUNS}"
    )

    print(
        f"Calibration score mean: "
        f"{run_scores['average_price'].mean():.6f}"
    )

    print(
        f"Calibration score std: "
        f"{run_scores['average_price'].std():.6f}"
    )

    print(
        f"B0 threshold (95th percentile): "
        f"{threshold:.6f}"
    )

    print(
        f"\nCalibration data saved to: "
        f"{OUTPUT_PATH}"
    )

    print(
        f"Threshold saved to: "
        f"{THRESHOLD_PATH}"
    )


if __name__ == "__main__":
    main()