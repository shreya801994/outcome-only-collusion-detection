from pathlib import Path

import pandas as pd

from detectors import (
    price_level_score,
    synchronization_score,
    directional_dependence_score,
)


INPUT_PATH = Path(
    "data/dynamic_auditor_trajectories.csv"
)

RESEARCHER_PATH = Path(
    "data/dynamic_researcher_trajectories.csv"
)

OUTPUT_PATH = Path(
    "results/dynamic_detector_scores.csv"
)

OUTPUT_PATH.parent.mkdir(
    exist_ok=True
)


def main():

    auditor_data = pd.read_csv(
        INPUT_PATH
    )

    researcher_data = pd.read_csv(
        RESEARCHER_PATH
    )

    rows = []

    for run_id, group in auditor_data.groupby(
        "run_id"
    ):

        group = group.sort_values(
            "period"
        )

        b0 = price_level_score(
            group
        )

        b1 = synchronization_score(
            group
        )

        b2 = directional_dependence_score(
            group
        )

        metadata = (
            researcher_data[
                researcher_data["run_id"]
                == run_id
            ][
                [
                    "run_id",
                    "cost_gap",
                    "condition",
                ]
            ]
            .drop_duplicates()
            .iloc[0]
        )

        rows.append(
            {
                "run_id": run_id,
                "cost_gap": metadata[
                    "cost_gap"
                ],
                "condition": metadata[
                    "condition"
                ],
                "B0_price_level": b0,
                "B1_synchronization": b1,
                "B2_directional_dependence": b2,
            }
        )

    results = pd.DataFrame(
        rows
    )

    results.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        "Saved:"
    )

    print(
        OUTPUT_PATH
    )

    print(
        "\nDetector summary:"
    )

    print(
        results.groupby("cost_gap")[
            [
                "B0_price_level",
                "B1_synchronization",
                "B2_directional_dependence",
            ]
        ].mean()
    )


if __name__ == "__main__":
    main()