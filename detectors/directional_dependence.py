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


def directional_scores(
    data: pd.DataFrame,
) -> tuple[float, float]:

    validate_price_data(data)

    price_change_1 = (
        data["price_1"].diff()
    )

    price_change_2 = (
        data["price_2"].diff()
    )

    lagged_change_1 = (
        price_change_1.shift(1)
    )

    lagged_change_2 = (
        price_change_2.shift(1)
    )

    valid_1_to_2 = (
        lagged_change_1.notna()
        & price_change_2.notna()
    )

    valid_2_to_1 = (
        lagged_change_2.notna()
        & price_change_1.notna()
    )

    if valid_1_to_2.sum() < 2:
        raise ValueError(
            "At least four observations "
            "are required for directional "
            "dependence."
        )

    score_1_to_2 = (
        lagged_change_1[valid_1_to_2]
        .corr(
            price_change_2[valid_1_to_2]
        )
    )

    score_2_to_1 = (
        lagged_change_2[valid_2_to_1]
        .corr(
            price_change_1[valid_2_to_1]
        )
    )

    if pd.isna(score_1_to_2):
        score_1_to_2 = 0.0

    if pd.isna(score_2_to_1):
        score_2_to_1 = 0.0

    return (
        float(score_1_to_2),
        float(score_2_to_1),
    )


def score(
    data: pd.DataFrame,
) -> float:

    score_1_to_2, score_2_to_1 = (
        directional_scores(data)
    )

    return max(
        score_1_to_2,
        score_2_to_1,
    )


def flag(
    data: pd.DataFrame,
    threshold: float,
) -> bool:

    return score(data) > threshold