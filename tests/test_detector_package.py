import pandas as pd

from detectors import (
    price_level_score,
    synchronization_score,
)


def test_price_level_score():

    data = pd.DataFrame(
        {
            "period": [0, 1, 2],
            "price_1": [1.0, 2.0, 3.0],
            "price_2": [1.0, 2.0, 3.0],
        }
    )

    score = price_level_score(data)

    assert score == 2.0


def test_synchronization_score():

    data = pd.DataFrame(
        {
            "period": [0, 1, 2, 3],
            "price_1": [1.0, 1.1, 1.0, 1.2],
            "price_2": [1.0, 1.2, 1.1, 1.3],
        }
    )

    score = synchronization_score(data)

    assert -1.0 <= score <= 1.0


def test_price_level_score_uses_only_observable_prices():

    data = pd.DataFrame(
        {
            "period": [0, 1, 2],
            "price_1": [1.0, 2.0, 3.0],
            "price_2": [1.0, 2.0, 3.0],
            "cost_1": [1.0, 1.0, 1.0],
            "cost_2": [1.0, 1.3, 1.6],
            "market_size": [1.0, 1.2, 0.8],
        }
    )

    score = price_level_score(data)

    assert score == 2.0

def test_directional_dependence_returns_bounded_score():

    from detectors import (
        directional_dependence_score,
    )

    data = pd.DataFrame(
        {
            "period": [0, 1, 2, 3, 4, 5],
            "price_1": [
                1.0,
                1.1,
                1.0,
                1.2,
                1.1,
                1.3,
            ],
            "price_2": [
                1.0,
                1.0,
                1.1,
                1.0,
                1.2,
                1.1,
            ],
        }
    )

    score = directional_dependence_score(
        data
    )

    assert -1.0 <= score <= 1.0


def test_directional_dependence_uses_only_prices():

    from detectors import (
        directional_dependence_score,
    )

    data = pd.DataFrame(
        {
            "period": [0, 1, 2, 3, 4],
            "price_1": [
                1.0,
                1.1,
                1.0,
                1.2,
                1.1,
            ],
            "price_2": [
                1.0,
                1.0,
                1.1,
                1.0,
                1.2,
            ],
            "cost_1": [
                1.0,
                1.0,
                1.0,
                1.0,
                1.0,
            ],
            "cost_2": [
                1.0,
                1.3,
                1.3,
                1.3,
                1.3,
            ],
            "market_size": [
                1.0,
                1.2,
                0.8,
                1.0,
                1.2,
            ],
        }
    )

    score = directional_dependence_score(
        data
    )

    assert -1.0 <= score <= 1.0


def test_directional_dependence_requires_enough_data():

    from detectors import (
        directional_dependence_score,
    )

    data = pd.DataFrame(
        {
            "period": [0, 1, 2],
            "price_1": [1.0, 1.1, 1.0],
            "price_2": [1.0, 1.0, 1.1],
        }
    )

    try:
        directional_dependence_score(data)
    except ValueError:
        assert True
    else:
        assert False

def test_deviation_response_detects_response():

    from detectors import (
        deviation_response_score,
    )

    data = pd.DataFrame(
        {
            "period": [0, 1, 2, 3, 4],
            "price_1": [
                1.90,
                1.90,
                1.40,
                1.40,
                1.40,
            ],
            "price_2": [
                1.90,
                1.90,
                1.90,
                1.10,
                1.10,
            ],
        }
    )

    score = deviation_response_score(
        data,
        deviation_threshold=0.10,
    )

    assert score == 1.0


def test_deviation_response_returns_zero_without_events():

    from detectors import (
        deviation_response_score,
    )

    data = pd.DataFrame(
        {
            "period": [0, 1, 2, 3],
            "price_1": [
                1.90,
                1.91,
                1.90,
                1.91,
            ],
            "price_2": [
                1.90,
                1.90,
                1.91,
                1.90,
            ],
        }
    )

    score = deviation_response_score(
        data,
        deviation_threshold=0.10,
    )

    assert score == 0.0


def test_deviation_response_ignores_private_columns():

    from detectors import (
        deviation_response_score,
    )

    data = pd.DataFrame(
        {
            "period": [0, 1, 2, 3],
            "price_1": [
                1.90,
                1.90,
                1.40,
                1.90,
            ],
            "price_2": [
                1.90,
                1.90,
                1.90,
                1.10,
            ],
            "cost_1": [
                1.0,
                1.0,
                1.0,
                1.0,
            ],
            "cost_2": [
                1.0,
                1.0,
                1.0,
                1.0,
            ],
            "market_size": [
                1.0,
                1.2,
                0.8,
                1.0,
            ],
        }
    )

    score = deviation_response_score(
        data,
        deviation_threshold=0.10,
    )

    assert 0.0 <= score <= 1.0