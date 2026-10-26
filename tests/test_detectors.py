import pandas as pd
import pytest

from detectors import (
    price_level_score,
    flag_price_level,
    synchronization_score,
    flag_synchronization,
    directional_dependence_score,
    flag_directional_dependence,
    deviation_response_score,
    flag_deviation_response,
)


def make_auditor_data():

    return pd.DataFrame(
        {
            "period": [0, 1, 2],
            "price_1": [1.0, 2.0, 3.0],
            "price_2": [1.0, 2.0, 3.0],
            "quantity_1": [0.5, 0.4, 0.3],
            "quantity_2": [0.5, 0.4, 0.3],
        }
    )


def test_price_level_score():

    data = make_auditor_data()

    score = price_level_score(data)

    assert score == pytest.approx(2.0)


def test_price_level_flags_above_threshold():

    data = make_auditor_data()

    assert flag_price_level(
        data,
        threshold=1.9,
    )


def test_price_level_does_not_flag_below_threshold():

    data = make_auditor_data()

    assert not flag_price_level(
        data,
        threshold=2.1,
    )


def test_synchronization_score():

    data = pd.DataFrame({
        "period": [0, 1, 2, 3, 4],
        "price_1": [1.0, 1.1, 1.0, 1.2, 1.1],
        "price_2": [1.0, 1.2, 1.1, 1.3, 1.2],
        "quantity_1": [0.5, 0.4, 0.5, 0.3, 0.4],
        "quantity_2": [0.5, 0.4, 0.5, 0.3, 0.4],
    })

    score = synchronization_score(data)

    assert score > 0.9


def test_synchronization_flags_above_threshold():

    data = pd.DataFrame({
        "period": [0, 1, 2, 3, 4],
        "price_1": [1.0, 1.1, 1.0, 1.2, 1.1],
        "price_2": [1.0, 1.2, 1.1, 1.3, 1.2],
        "quantity_1": [0.5, 0.4, 0.5, 0.3, 0.4],
        "quantity_2": [0.5, 0.4, 0.5, 0.3, 0.4],
    })

    assert flag_synchronization(
        data,
        threshold=0.8,
    )


def test_synchronization_does_not_flag_low_correlation():

    data = pd.DataFrame({
        "period": [0, 1, 2, 3, 4],
        "price_1": [1.0, 1.1, 1.0, 1.1, 1.0],
        "price_2": [1.0, 1.0, 1.1, 1.0, 1.1],
        "quantity_1": [0.5, 0.4, 0.5, 0.4, 0.5],
        "quantity_2": [0.5, 0.5, 0.4, 0.5, 0.4],
    })

    assert not flag_synchronization(
        data,
        threshold=0.8,
    )


def test_detector_rejects_missing_columns():

    data = pd.DataFrame(
        {
            "period": [0],
            "price_1": [1.5],
        }
    )

    with pytest.raises(ValueError):

        price_level_score(data)