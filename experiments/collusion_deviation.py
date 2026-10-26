from pathlib import Path

import pandas as pd

from simulator.market import (
    BertrandMarket,
    MarketConfig,
)
from simulator.collusion_agents import (
    RewardPunishmentAgent,
)
from simulator.auditor_view import (
    create_auditor_view,
)


OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)

PERIODS = 80
DEVIATION_PERIOD = 30


def main():

    market = BertrandMarket(
        MarketConfig()
    )

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

    agent_1.reset()
    agent_2.reset()

    price_1 = agent_1.high_price
    price_2 = agent_2.high_price

    previous_price_1 = price_1
    previous_price_2 = price_2

    records = []

    for t in range(PERIODS):

        forced_deviation = (
            t == DEVIATION_PERIOD
        )

        result = market.step(
            p1=price_1,
            p2=price_2,
            c1=agent_1.cost,
            c2=agent_2.cost,
        )

        records.append(
            {
                "period": t,
                "price_1": price_1,
                "price_2": price_2,
                "quantity_1": result[
                    "quantity_1"
                ],
                "quantity_2": result[
                    "quantity_2"
                ],
                "profit_1": result[
                    "profit_1"
                ],
                "profit_2": result[
                    "profit_2"
                ],

                # Researcher-side metadata.
                # NEVER supplied to the auditor.
                "forced_deviation": (
                    forced_deviation
                ),
                "cost_1": agent_1.cost,
                "cost_2": agent_2.cost,
                "condition": (
                    "scripted_collusion"
                ),
            }
        )

        # Firm 1 deviates once.
        if forced_deviation:

            next_price_1 = 1.40

        else:

            next_price_1 = (
                agent_1.choose_price(
                    competitor_price=price_2,
                    previous_competitor_price=(
                        previous_price_2
                    ),
                )
            )

        next_price_2 = (
            agent_2.choose_price(
                competitor_price=price_1,
                previous_competitor_price=(
                    previous_price_1
                ),
            )
        )

        previous_price_1 = price_1
        previous_price_2 = price_2

        price_1 = next_price_1
        price_2 = next_price_2

    researcher_data = pd.DataFrame(
        records
    )

    auditor_data = create_auditor_view(
        researcher_data
    )

    researcher_path = (
        OUTPUT_DIR
        / "collusion_deviation_researcher.csv"
    )

    auditor_path = (
        OUTPUT_DIR
        / "collusion_deviation_auditor.csv"
    )

    researcher_data.to_csv(
        researcher_path,
        index=False,
    )

    auditor_data.to_csv(
        auditor_path,
        index=False,
    )

    print(
        "Saved researcher trajectory:"
    )
    print(researcher_path)

    print(
        "\nSaved auditor trajectory:"
    )
    print(auditor_path)

    print(
        "\nPrice trajectory around deviation:"
    )

    print(
        researcher_data[
            [
                "period",
                "price_1",
                "price_2",
                "forced_deviation",
            ]
        ].iloc[25:40].to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()