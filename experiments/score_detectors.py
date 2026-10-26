from pathlib import Path

import pandas as pd

from detectors import (
    price_level_score,
    synchronization_score,
)


DATA_PATH = Path("data/auditor_trajectories.csv")
OUTPUT_PATH = Path("results/detector_scores.csv")


def main():

    auditor_data = pd.read_csv(DATA_PATH)

    scores = []

    for run_id, run_data in auditor_data.groupby("run_id"):

        run_data = run_data.sort_values("period")

        b0_score = price_level_score(run_data)

        b1_score = synchronization_score(run_data)

        scores.append(
            {
                "run_id": run_id,
                "B0_price_level": b0_score,
                "B1_synchronization": b1_score,
            }
        )

    scores = pd.DataFrame(scores)

    researcher_data = pd.read_csv(
        "data/researcher_trajectories.csv"
    )

    run_metadata = (
        researcher_data[
            [
                "run_id",
                "cost_gap",
                "condition",
            ]
        ]
        .drop_duplicates()
    )

    scores = scores.merge(
        run_metadata,
        on="run_id",
        how="left",
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    scores.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("Detector scoring completed.")
    print(f"Saved to: {OUTPUT_PATH}")

    print("\nDetector scores:")
    print(scores.to_string(index=False))


if __name__ == "__main__":
    main()