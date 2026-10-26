from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


INPUT_PATH = Path(
    "results/b0_fpr_summary.csv"
)

OUTPUT_PATH = Path(
    "results/b0_fpr_vs_cost_gap.png"
)


def main():

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"FPR summary not found: {INPUT_PATH}"
        )

    data = pd.read_csv(INPUT_PATH)

    required_columns = {
        "cost_gap",
        "fpr",
        "ci_low",
        "ci_high",
    }

    missing = required_columns - set(data.columns)

    if missing:
        raise ValueError(
            f"Missing columns: {sorted(missing)}"
        )

    data = data.sort_values(
        "cost_gap"
    )

    plt.figure(figsize=(8, 5))

    plt.errorbar(
        data["cost_gap"],
        data["fpr"] * 100,
        yerr=[
            (data["fpr"] - data["ci_low"]) * 100,
            (data["ci_high"] - data["fpr"]) * 100,
        ],
        marker="o",
        capsize=5,
        linewidth=2,
        label="B0 observed FPR",
    )

    plt.axhline(
        5,
        linestyle="--",
        linewidth=1.5,
        label="5% calibration target",
    )

    plt.xlabel(
        "Hidden Cost Gap (Δc)"
    )

    plt.ylabel(
        "False Positive Rate (%)"
    )

    plt.title(
        "B0 False Positive Rate Under Hidden Cost Asymmetry"
    )

    plt.xticks(
        data["cost_gap"]
    )

    plt.ylim(
        0,
        105,
    )

    plt.grid(
        True,
        alpha=0.3,
    )

    plt.legend()

    plt.tight_layout()

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.savefig(
        OUTPUT_PATH,
        dpi=300,
        bbox_inches="tight",
    )

    plt.show()

    print(
        f"Graph saved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()