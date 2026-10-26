import pandas as pd


REQUIRED_COLUMNS = [
    "period",
    "price_1",
    "price_2",
]


def validate_price_data(
    data: pd.DataFrame,
) -> None:

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )


def score(
    data: pd.DataFrame,
) -> float:

    validate_price_data(data)

    price_change_1 = data[
        "price_1"
    ].diff()

    price_change_2 = data[
        "price_2"
    ].diff()

    valid = (
        price_change_1.notna()
        & price_change_2.notna()
    )

    price_change_1 = (
        price_change_1[valid]
    )

    price_change_2 = (
        price_change_2[valid]
    )

    if len(price_change_1) < 2:
        raise ValueError(
            "At least three observations "
            "are required to calculate "
            "synchronization."
        )

    correlation = (
        price_change_1.corr(
            price_change_2
        )
    )

    if pd.isna(correlation):
        return 0.0

    return float(correlation)


def flag(
    data: pd.DataFrame,
    threshold: float,
) -> bool:

    return score(data) > threshold