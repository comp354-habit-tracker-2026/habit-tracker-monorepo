# Generated with assistance from Claude (Anthropic AI).
# Source: Claude Sonnet 4.6 via Claude Code CLI (Anthropic, 2026).
# Required disclosure per COMP 354 AI-generated code traceability policy.
#
# Sanjitt Kanagalingam — GitHub: sanjitt-k
# Issue #146: G14 Baseline Forecasting (Moving Avg + Fallback, Horizon H, method="baseline")
# Branch: feature/group-14-baseline-forecasting

"""Baseline Forecasting Module — Group 14 Forecasting Engine.

Implements Issue #146: a deterministic baseline forecaster using a moving average
(when enough history is available) or last-value fallback (when history is too short).

Public API
----------
generate_baseline_forecast(history, horizon, window_k=7, method="baseline") -> dict

Input contract (aligned with Arthur's /forecast endpoint and ForecastPoint model)
----------------------------------------------------------------------------------
    history  : list of {"date": "YYYY-MM-DD", "value": float}
               Must be sorted ascending by date, non-empty, values numeric.
    horizon  : int > 0  — number of future points to predict (H)
    window_k : int > 0  — moving average window size k (default 7)
    method   : str      — must be "baseline"

Output contract (ForecastPoint-compatible: {date, predictedValue})
-------------------------------------------------------------------
    {
        "status":   "success",
        "forecast": [{"date": "YYYY-MM-DD", "predictedValue": float}, ...],
        "metadata": {
            "methodUsed":   "moving_average" | "fallback",
            "windowK":      int,
            "fallbackUsed": bool
        }
    }

Selection logic
---------------
    fallback_used = len(history) < window_k
    - moving_average : recursive multi-step — mean of last k values appended each step
    - fallback        : repeats the last observed value for all H points

Raises
------
    ValueError  : invalid horizon, window_k, method, missing fields, empty history,
                  or history dates not in strictly ascending order
    TypeError   : non-numeric value in history
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _validate_inputs(
    history: List[Dict[str, Any]],
    horizon: int,
    window_k: int,
    method: str,
) -> None:
    """Raise ValueError/TypeError with a clear message if any input is invalid."""
    if method != "baseline":
        raise ValueError(
            f"method must be 'baseline', got '{method}'. "
            "Only baseline forecasting is supported by this module."
        )
    if not history:
        raise ValueError("history must not be empty")
    if not isinstance(horizon, int) or horizon <= 0:
        raise ValueError(
            f"horizon must be a positive integer, got {horizon!r}"
        )
    if not isinstance(window_k, int) or window_k <= 0:
        raise ValueError(
            f"window_k must be a positive integer, got {window_k!r}"
        )
    for i, entry in enumerate(history):
        if "date" not in entry:
            raise ValueError(
                f"history[{i}] is missing required field 'date'"
            )
        if "value" not in entry:
            raise ValueError(
                f"history[{i}] is missing required field 'value'"
            )
        if not isinstance(entry["value"], (int, float)):
            raise TypeError(
                f"history[{i}]['value'] must be numeric (int or float), "
                f"got {type(entry['value']).__name__!r}"
            )
        try:
            datetime.strptime(str(entry["date"]), "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                f"history[{i}]['date'] must be in 'YYYY-MM-DD' format, "
                f"got '{entry['date']}'"
            )

    # Enforce strictly ascending date order (required by the input contract).
    for i in range(1, len(history)):
        prev_date = datetime.strptime(str(history[i - 1]["date"]), "%Y-%m-%d")
        curr_date = datetime.strptime(str(history[i]["date"]), "%Y-%m-%d")
        if curr_date <= prev_date:
            raise ValueError(
                f"history dates must be in strictly ascending order, "
                f"but history[{i - 1}]['date'] '{history[i - 1]['date']}' "
                f">= history[{i}]['date'] '{history[i]['date']}'"
            )


# ---------------------------------------------------------------------------
# Date generation
# ---------------------------------------------------------------------------

def _generate_future_dates(last_date_str: str, horizon: int) -> List[str]:
    """Return *horizon* daily date strings (YYYY-MM-DD) following *last_date_str*."""
    last = datetime.strptime(last_date_str, "%Y-%m-%d")
    return [
        (last + timedelta(days=i + 1)).strftime("%Y-%m-%d")
        for i in range(horizon)
    ]


# ---------------------------------------------------------------------------
# Forecast algorithms
# ---------------------------------------------------------------------------

def _moving_average_forecast(
    values: List[float],
    horizon: int,
    window_k: int,
) -> List[float]:
    """Recursive multi-step moving average.

    For each of the H steps:
      1. Take the last k values from the working sequence.
      2. Compute their mean → next predicted value.
      3. Append the prediction to the working sequence.

    This means each new prediction is based on the previous predictions
    once the original history is exhausted within the window.
    """
    working = list(values)
    predictions: List[float] = []
    for _ in range(horizon):
        window = working[-window_k:]
        next_val = sum(window) / len(window)
        predictions.append(next_val)
        working.append(next_val)
    return predictions


def _fallback_forecast(values: List[float], horizon: int) -> List[float]:
    """Fallback: repeat the last observed value for all H future points."""
    return [float(values[-1])] * horizon


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_baseline_forecast(
    history: List[Dict[str, Any]],
    horizon: int,
    window_k: int = 7,
    method: str = "baseline",
) -> Dict[str, Any]:
    """Generate a deterministic baseline forecast from historical activity data.

    Selects the moving average strategy when ``len(history) >= window_k``;
    otherwise falls back to repeating the last observed value.

    Args:
        history:  List of ``{"date": "YYYY-MM-DD", "value": float}`` dicts,
                  sorted ascending by date.
        horizon:  Number of future points to generate (H > 0).
        window_k: Moving average window size (k > 0, default 7).
        method:   Must be ``"baseline"`` — routes the request to this forecaster.

    Returns:
        A dict with keys:

        * ``"status"``   — ``"success"``
        * ``"forecast"`` — list of H ``{"date", "predictedValue"}`` items
        * ``"metadata"`` — ``{"methodUsed", "windowK", "fallbackUsed"}``

    Raises:
        ValueError: On invalid ``horizon``, ``window_k``, ``method``,
                    missing history fields, empty history, bad date format,
                    or history dates not in strictly ascending order.
        TypeError:  When a history value is not numeric.

    Examples:
        Moving average (history >= k)::

            result = generate_baseline_forecast(
                history=[{"date": "2024-01-01", "value": 3.0},
                         {"date": "2024-01-02", "value": 5.0},
                         {"date": "2024-01-03", "value": 7.0}],
                horizon=2,
                window_k=3,
            )
            # methodUsed="moving_average", first pred = mean([3,5,7]) = 5.0

        Fallback (history < k)::

            result = generate_baseline_forecast(
                history=[{"date": "2024-01-01", "value": 5.0}],
                horizon=3,
                window_k=7,
            )
            # methodUsed="fallback", all predictedValue=5.0
    """
    _validate_inputs(history, horizon, window_k, method)

    values = [float(entry["value"]) for entry in history]
    last_date = str(history[-1]["date"])

    fallback_used = len(history) < window_k
    if fallback_used:
        raw_predictions = _fallback_forecast(values, horizon)
        method_used = "fallback"
    else:
        raw_predictions = _moving_average_forecast(values, horizon, window_k)
        method_used = "moving_average"

    future_dates = _generate_future_dates(last_date, horizon)

    forecast = [
        {"date": date, "predictedValue": val}
        for date, val in zip(future_dates, raw_predictions)
    ]

    return {
        "status": "success",
        "forecast": forecast,
        "metadata": {
            "methodUsed": method_used,
            "windowK": window_k,
            "fallbackUsed": fallback_used,
        },
    }
