import math
import pytest

from analytics.presentation.metrics import  (
    mae,
    rmse,
    mape,
    compute_all_metrics,
)

def test_mae_basic() -> None:
    y_true = [10.0, 20.0, 30.0]
    y_pred = [12.0, 18.0, 33.0]

    expected = (2.0 + 2.0 + 3.0) / 3.0
    assert mae(y_true, y_pred) == pytest.approx(expected)


def test_rmse_basic() -> None:
    y_true = [10.0, 20.0, 30.0]
    y_pred = [12.0, 18.0, 33.0]

    expected = math.sqrt((4.0 + 4.0 + 9.0) / 3.0)
    assert rmse(y_true, y_pred) == pytest.approx(expected)


def test_mape_basic() -> None:
    y_true = [10.0, 20.0, 40.0]
    y_pred = [11.0, 18.0, 44.0]

    expected = ((1.0 / 10.0) + (2.0 / 20.0) + (4.0 / 40.0)) / 3.0 * 100.0
    assert mape(y_true, y_pred) == pytest.approx(expected)


def test_compute_all_metrics_returns_expected_keys() -> None:
    result = compute_all_metrics([10.0, 20.0], [11.0, 19.0])

    assert set(result.keys()) == {"MAE", "RMSE", "MAPE"}


def test_compute_all_metrics_returns_correct_values() -> None:
    y_true = [100.0, 200.0]
    y_pred = [110.0, 190.0]

    result = compute_all_metrics(y_true, y_pred)

    expected_mae = 10.0
    expected_rmse = math.sqrt((100.0 + 100.0) / 2.0)
    expected_mape = ((10.0 / 100.0) + (10.0 / 200.0)) / 2.0 * 100.0

    assert result["MAE"] == pytest.approx(expected_mae)
    assert result["RMSE"] == pytest.approx(expected_rmse)
    assert result["MAPE"] == pytest.approx(expected_mape)


def test_mae_is_zero_for_perfect_predictions() -> None:
    y_true = [5.0, 10.0, 15.0]
    y_pred = [5.0, 10.0, 15.0]

    assert mae(y_true, y_pred) == pytest.approx(0.0)


def test_rmse_is_zero_for_perfect_predictions() -> None:
    y_true = [5.0, 10.0, 15.0]
    y_pred = [5.0, 10.0, 15.0]

    assert rmse(y_true, y_pred) == pytest.approx(0.0)


def test_mape_is_zero_for_perfect_predictions() -> None:
    y_true = [5.0, 10.0, 15.0]
    y_pred = [5.0, 10.0, 15.0]

    assert mape(y_true, y_pred) == pytest.approx(0.0)


def test_mae_raises_on_empty_input() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        mae([], [])


def test_rmse_raises_on_empty_input() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        rmse([], [])


def test_mape_raises_on_empty_input() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        mape([], [])


def test_mae_raises_on_mismatched_lengths() -> None:
    with pytest.raises(ValueError, match="same length"):
        mae([1.0, 2.0], [1.0])


def test_rmse_raises_on_mismatched_lengths() -> None:
    with pytest.raises(ValueError, match="same length"):
        rmse([1.0, 2.0], [1.0])


def test_mape_raises_on_mismatched_lengths() -> None:
    with pytest.raises(ValueError, match="same length"):
        mape([1.0, 2.0], [1.0])


def test_mape_raises_when_y_true_contains_zero() -> None:
    with pytest.raises(ValueError, match="contains 0"):
        mape([10.0, 0.0, 20.0], [9.0, 1.0, 21.0])
