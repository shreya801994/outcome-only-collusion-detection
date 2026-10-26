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
    deviation_threshold: float = 0.10,
) -> float:

    validate_price_data(data)

    price_1 = data[
        "price_1"
    ].reset_index(drop=True)

    price_2 = data[
        "price_2"
    ].reset_index(drop=True)

    changes_1 = price_1.diff()
    changes_2 = price_2.diff()

    events = 0
    responses = 0

    t = 1

    while t < len(data) - 1:

        firm_1_deviation = (
            changes_1.iloc[t]
            < -deviation_threshold
        )

        firm_2_deviation = (
            changes_2.iloc[t]
            < -deviation_threshold
        )

        # Firm 1 deviates.
        if firm_1_deviation:

            events += 1

            if changes_2.iloc[t + 1] < 0:
                responses += 1

                # The next-period movement of Firm 2
                # is already accounted for as the response.
                t += 2
                continue

        # Firm 2 deviates.
        if firm_2_deviation:

            events += 1

            if changes_1.iloc[t + 1] < 0:
                responses += 1

                # The next-period movement of Firm 1
                # is already accounted for as the response.
                t += 2
                continue

        t += 1

    if events == 0:
        return 0.0

    return responses / events


def flag(
    data: pd.DataFrame,
    threshold: float,
    deviation_threshold: float = 0.10,
) -> bool:

    return (
        score(
            data,
            deviation_threshold,
        )
        > threshold
    )