from __future__ import annotations

import math
from typing import Sequence

NumberSequence = Sequence[float]


def _validate_inputs(y_true: NumberSequence, y_pred: NumberSequence) -> None:
    if len(y_true) == 0:
        raise ValueError("y_true must not be empty")
    if len(y_pred) == 0:
        raise ValueError("y_pred must not be empty")
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")


def mae(y_true: NumberSequence, y_pred: NumberSequence) -> float:
    _validate_inputs(y_true, y_pred)
    return sum(abs(t - p) for t, p in zip(y_true, y_pred)) / len(y_true)


def rmse(y_true: NumberSequence, y_pred: NumberSequence) -> float:
    _validate_inputs(y_true, y_pred)
    mse = sum((t - p) ** 2 for t, p in zip(y_true, y_pred)) / len(y_true)
    return math.sqrt(mse)


def mape(y_true: NumberSequence, y_pred: NumberSequence) -> float:
    _validate_inputs(y_true, y_pred)

    if any(t == 0 for t in y_true):
        raise ValueError("MAPE is undefined when y_true contains 0")

    return (
        sum(abs((t - p) / t) for t, p in zip(y_true, y_pred)) / len(y_true)
    ) * 100.0


def compute_all_metrics(y_true: NumberSequence, y_pred: NumberSequence) -> dict[str, float]:
    return {
        "MAE": mae(y_true, y_pred),
        "RMSE": rmse(y_true, y_pred),
        "MAPE": mape(y_true, y_pred),
    }