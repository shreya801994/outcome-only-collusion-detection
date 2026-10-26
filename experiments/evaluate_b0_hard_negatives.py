from pathlib import Path

import pandas as pd
import numpy as np

from detectors.price_level import score as price_level_score


HARD_NEGATIVE_DATA = Path(
    "data/reactive_auditor_trajectories.csv"
)

RESEARCHER_DATA = Path(
    "data/reactive_researcher_trajectories.csv"
)

THRESHOLD_PATH = Path(
    "results/b0_threshold.txt"
)

RESULTS_PATH = Path(
    "results/b0_hard_negative_results.csv"
)

SUMMARY_PATH = Path(
    "results/b0_fpr_summary.csv"
)


def wilson_interval(
    successes: int,
    total: int,
    z: float = 1.96,
):
    if total == 0:
        return 0.0, 0.0

    p = successes / total

    denominator = 1 + (z ** 2 / total)

    center = (
        p + (z ** 2 / (2 * total))
    ) / denominator

    margin = (
        z
        * np.sqrt(
            (
                p * (1 - p) / total
            )
            + (
                z ** 2 / (4 * total ** 2)
            )
        )
        / denominator
    )

    return (
        max(0.0, center - margin),
        min(1.0, center + margin),
    )


def main():

    if not HARD_NEGATIVE_DATA.exists():
        raise FileNotFoundError(
            f"Hard-negative data not found: "
            f"{HARD_NEGATIVE_DATA}"
        )

    if not RESEARCHER_DATA.exists():
        raise FileNotFoundError(
            f"Researcher data not found: "
            f"{RESEARCHER_DATA}"
        )

    if not THRESHOLD_PATH.exists():
        raise FileNotFoundError(
            f"B0 threshold not found: "
            f"{THRESHOLD_PATH}"
        )

    threshold = float(
        THRESHOLD_PATH.read_text(
            encoding="utf-8"
        ).strip()
    )

    auditor_data = pd.read_csv(
        HARD_NEGATIVE_DATA
    )

    researcher_data = pd.read_csv(
        RESEARCHER_DATA
    )

    required_auditor_columns = {
        "run_id",
        "period",
        "price_1",
        "price_2",
        "quantity_1",
        "quantity_2",
    }

    missing = (
        required_auditor_columns
        - set(auditor_data.columns)
    )

    if missing:
        raise ValueError(
            "Missing auditor columns: "
            f"{sorted(missing)}"
        )

    metadata = (
        researcher_data[
            [
                "run_id",
                "cost_gap",
                "condition",
            ]
        ]
        .drop_duplicates("run_id")
    )

    run_results = []

    for run_id, run_data in auditor_data.groupby(
        "run_id"
    ):

        detector_score = price_level_score(
            run_data
        )

        run_results.append(
            {
                "run_id": run_id,
                "b0_score": detector_score,
                "threshold": threshold,
                "flagged": (
                    detector_score > threshold
                ),
            }
        )

    results = pd.DataFrame(
        run_results
    )

    results = results.merge(
        metadata,
        on="run_id",
        how="left",
    )

    if results["cost_gap"].isna().any():
        raise ValueError(
            "Some runs could not be matched "
            "to researcher metadata."
        )

    results["false_positive"] = (
        results["flagged"]
    )

    SUMMARY = []

    for cost_gap, group in results.groupby(
        "cost_gap"
    ):

        total = len(group)

        false_positives = int(
            group["false_positive"].sum()
        )

        fpr = false_positives / total

        ci_low, ci_high = wilson_interval(
            false_positives,
            total,
        )

        SUMMARY.append(
            {
                "cost_gap": cost_gap,
                "total_runs": total,
                "false_positives": false_positives,
                "fpr": fpr,
                "ci_low": ci_low,
                "ci_high": ci_high,
            }
        )

    summary = pd.DataFrame(
        SUMMARY
    ).sort_values(
        "cost_gap"
    )

    RESULTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    results.to_csv(
        RESULTS_PATH,
        index=False,
    )

    summary.to_csv(
        SUMMARY_PATH,
        index=False,
    )

    print("\nB0 hard-negative evaluation")
    print("--------------------------------")

    print(
        f"Frozen threshold: "
        f"{threshold:.6f}"
    )

    print(
        f"\n{summary.to_string(index=False)}"
    )

    print(
        f"\nDetailed results saved to:"
        f"\n{RESULTS_PATH}"
    )

    print(
        f"\nFPR summary saved to:"
        f"\n{SUMMARY_PATH}"
    )


if __name__ == "__main__":
    main()