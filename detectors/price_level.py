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

    average_price = (
        data["price_1"]
        + data["price_2"]
    ) / 2.0

    return float(
        average_price.mean()
    )


def flag(
    data: pd.DataFrame,
    threshold: float,
) -> bool:

    return score(data) > threshold