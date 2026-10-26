import os
import pandas as pd

from detectors.price_level import score as b0_score
from detectors.synchronization import score as b1_score
from detectors.directional_dependence import score as b2_score
from detectors.deviation_response import score as b3_score


DATASETS = {
    "no_shock": "data/reactive_auditor_trajectories.csv",
    "common_shock": "data/reactive_shock_auditor_trajectories.csv",
}


def score_runs(data):
    records = []

    for run_id, run_data in data.groupby("run_id"):
        run_data = run_data.sort_values("period").reset_index(drop=True)

        cost_gap = None

        # The auditor does not see cost_gap.
        # We recover it only for analysis by matching run IDs
        # to the researcher dataset outside the detector itself.

        records.append(
            {
                "run_id": run_id,
                "B0_price_level": b0_score(run_data),
                "B1_synchronization": b1_score(run_data),
                "B2_directional_dependence": b2_score(run_data),
                "B3_deviation_response": b3_score(run_data),
            }
        )

    return pd.DataFrame(records)


def main():

    os.makedirs("results", exist_ok=True)

    all_results = []

    for condition, path in DATASETS.items():

        data = pd.read_csv(path)

        scores = score_runs(data)
        scores["condition"] = condition

        all_results.append(scores)

    results = pd.concat(all_results, ignore_index=True)

    output_path = "results/reactive_detector_scores.csv"
    results.to_csv(output_path, index=False)

    print("\nDetector scores:")
    print(results.to_string(index=False))

    print("\nMean detector scores by condition:")

    summary = (
        results
        .groupby("condition")
        [
            [
                "B0_price_level",
                "B1_synchronization",
                "B2_directional_dependence",
                "B3_deviation_response",
            ]
        ]
        .mean()
        .reset_index()
    )

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()