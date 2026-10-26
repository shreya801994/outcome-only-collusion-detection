import pandas as pd

from simulator.auditor_view import create_auditor_view


def test_auditor_view_contains_only_public_outcomes():

    data = pd.DataFrame(
        {
            "period": [0, 1],
            "price_1": [1.5, 1.6],
            "price_2": [1.5, 1.7],
            "quantity_1": [0.4, 0.3],
            "quantity_2": [0.4, 0.3],
            "profit_1": [0.2, 0.1],
            "profit_2": [0.2, 0.1],
            "cost_1": [1.0, 1.0],
            "cost_2": [1.3, 1.3],
            "market_size": [1.0, 1.2],
            "agent_type": ["competitive", "competitive"],
        }
    )

    auditor_data = create_auditor_view(data)

    assert list(auditor_data.columns) == [
        "period",
        "price_1",
        "price_2",
        "quantity_1",
        "quantity_2",
    ]


def test_private_costs_are_hidden():

    data = pd.DataFrame(
        {
            "period": [0],
            "price_1": [1.5],
            "price_2": [1.6],
            "quantity_1": [0.4],
            "quantity_2": [0.3],
            "cost_1": [1.0],
            "cost_2": [1.3],
        }
    )

    auditor_data = create_auditor_view(data)

    assert "cost_1" not in auditor_data.columns
    assert "cost_2" not in auditor_data.columns


def test_market_size_is_hidden():

    data = pd.DataFrame(
        {
            "period": [0],
            "price_1": [1.5],
            "price_2": [1.6],
            "quantity_1": [0.4],
            "quantity_2": [0.3],
            "market_size": [1.2],
        }
    )

    auditor_data = create_auditor_view(data)

    assert "market_size" not in auditor_data.columns