from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


DATA_PATH = Path(
    "data/reactive_researcher_trajectories.csv"
)

OUTPUT_PATH = Path(
    "results/hard_negative_cost_asymmetry.png"
)


def main():

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Simulation data not found: {DATA_PATH}"
        )

    data = pd.read_csv(DATA_PATH)

    required_columns = {
        "run_id",
        "period",
        "price_1",
        "price_2",
        "cost_gap",
    }

    missing = required_columns - set(data.columns)

    if missing:
        raise ValueError(
            f"Missing columns in researcher data: "
            f"{sorted(missing)}"
        )

    summary = (
        data
        .groupby("cost_gap")[["price_1", "price_2"]]
        .mean()
        .reset_index()
    )

    print("\nSimulation-derived results:")
    print(summary.to_string(index=False))

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.figure(figsize=(8, 5))

    plt.plot(
        summary["cost_gap"],
        summary["price_1"],
        marker="o",
        label="Firm 1",
    )

    plt.plot(
        summary["cost_gap"],
        summary["price_2"],
        marker="o",
        label="Firm 2",
    )

    plt.xlabel("Hidden Cost Gap (Δc)")
    plt.ylabel("Mean Competitive Price")

    plt.title(
        "Non-Collusive Price Response to Hidden Cost Asymmetry"
    )

    plt.xticks(
        summary["cost_gap"]
    )

    plt.grid(
        True,
        alpha=0.3,
    )

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        OUTPUT_PATH,
        dpi=300,
        bbox_inches="tight",
    )

    plt.show()

    print(
        f"\nGraph saved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()