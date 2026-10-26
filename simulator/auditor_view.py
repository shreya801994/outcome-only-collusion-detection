import pandas as pd


AUDITOR_COLUMNS = [
    "period",
    "price_1",
    "price_2",
    "quantity_1",
    "quantity_2",
]


def create_auditor_view(data: pd.DataFrame) -> pd.DataFrame:
    missing_columns = [
        column
        for column in AUDITOR_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required auditor columns: "
            + ", ".join(missing_columns)
        )

    return data[AUDITOR_COLUMNS].copy()