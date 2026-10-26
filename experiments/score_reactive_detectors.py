
from pathlib import Path

import pandas as pd

from detectors import (
    price_level_score,
    synchronization_score,
    directional_dependence_score,
    deviation_response_score,
)

AUDITOR_PATH = Path(
    "data/reactive_auditor_trajectories.csv"
)

RESEARCHER_PATH = Path(
    "data/reactive_researcher_trajectories.csv"
)

OUTPUT_PATH = Path(
    "results/reactive_detector_scores.csv"
)


def main():
    if not AUDITOR_PATH.exists():
        raise FileNotFoundError(AUDITOR_PATH)

    if not RESEARCHER_PATH.exists():
        raise FileNotFoundError(RESEARCHER_PATH)

    auditor_data = pd.read_csv(AUDITOR_PATH)
    researcher_data = pd.read_csv(RESEARCHER_PATH)

    required_auditor_columns = {
        "run_id",
        "period",
        "price_1",
        "price_2",
        "quantity_1",
        "quantity_2",
    }

    missing = required_auditor_columns - set(auditor_data.columns)

    if missing:
        raise ValueError(
            f"Missing auditor columns: {sorted(missing)}"
        )

    required_metadata_columns = {
        "run_id",
        "cost_gap",
        "condition",
    }

    missing = required_metadata_columns - set(researcher_data.columns)

    if missing:
        raise ValueError(
            f"Missing researcher columns: {sorted(missing)}"
        )

    metadata = researcher_data[
        ["run_id", "cost_gap", "condition"]
    ].drop_duplicates()

    if metadata["run_id"].duplicated().any():
        raise ValueError(
            "A run_id maps to conflicting researcher metadata."
        )

    auditor_ids = set(auditor_data["run_id"].unique())
    metadata_ids = set(metadata["run_id"].unique())

    if auditor_ids != metadata_ids:
        raise ValueError(
            "Auditor and researcher run IDs do not match."
        )

    scores = []

    for run_id, run_data in auditor_data.groupby("run_id"):
        run_data = (
            run_data.sort_values("period")
            .reset_index(drop=True)
        )

        scores.append({
            "run_id": run_id,
            "B0_price_level": price_level_score(run_data),
            "B1_synchronization": synchronization_score(run_data),
            "B2_directional_dependence": directional_dependence_score(run_data),
            "B3_deviation_response": deviation_response_score(run_data),
        })

    scores = pd.DataFrame(scores)

    # Attach researcher-only labels only after detector scoring.
    scores = scores.merge(
        metadata,
        on="run_id",
        how="left",
        validate="one_to_one",
    )

    if scores[["cost_gap", "condition"]].isna().any().any():
        raise ValueError(
            "Some detector scores have missing ground-truth metadata."
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    scores.to_csv(OUTPUT_PATH, index=False)

    detector_columns = [
        "B0_price_level",
        "B1_synchronization",
        "B2_directional_dependence",
        "B3_deviation_response",
    ]

    print("\nDetector scores with researcher labels:")
    print(scores.to_string(index=False))

    print("\nMean detector scores by cost gap:")
    print(
        scores.groupby("cost_gap")[detector_columns]
        .mean()
        .to_string()
    )

    print(f"\nSaved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
