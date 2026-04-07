# Generated with assistance from Claude (Anthropic AI).
# Source: Claude Sonnet 4.6 via Claude Code CLI (Anthropic, 2026).
# Required disclosure per COMP 354 AI-generated code traceability policy.
#
# Sanjitt Kanagalingam — GitHub: sanjitt-k
# Issue #146: Unit tests for baseline_forecaster.py
# Branch: feature/group-14-baseline-forecasting

"""Unit tests for analytics.business.baseline_forecaster.

Coverage:
  - Moving average forecast (basic case + first predicted value)
  - Fallback triggered when history is shorter than window_k
  - Exact horizon count (both paths)
  - Dates are sequential and start the day after last history entry
  - All validation errors (empty history, bad horizon, bad window_k, bad method,
    non-numeric value, missing fields)
  - Output structure (required keys in forecast points and metadata)
  - Boundary: len(history) == window_k uses moving average, not fallback
"""

from datetime import datetime, timedelta

import pytest

from baseline_forecaster import generate_baseline_forecast


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def short_history():
    """3 entries — shorter than default window_k=7, triggers fallback."""
    return [
        {"date": "2024-01-01", "value": 3.0},
        {"date": "2024-01-02", "value": 5.0},
        {"date": "2024-01-03", "value": 7.0},
    ]


@pytest.fixture
def long_history():
    """10 entries with values 1–10 — sufficient for window_k=3 moving average."""
    return [
        {"date": f"2024-01-{i + 1:02d}", "value": float(i + 1)}
        for i in range(10)
    ]


# ---------------------------------------------------------------------------
# Moving average tests
# ---------------------------------------------------------------------------

def test_moving_average_basic(long_history):
    """window_k=3, history has 10 entries → moving average path is taken."""
    result = generate_baseline_forecast(long_history, horizon=3, window_k=3)
    assert result["status"] == "success"
    assert result["metadata"]["methodUsed"] == "moving_average"
    assert result["metadata"]["fallbackUsed"] is False


def test_moving_average_first_prediction(long_history):
    """First predicted value must equal the mean of the last k history values.

    long_history values are 1..10; last 3 are [8, 9, 10] → mean = 9.0.
    """
    result = generate_baseline_forecast(long_history, horizon=1, window_k=3)
    assert abs(result["forecast"][0]["predictedValue"] - 9.0) < 1e-9


# ---------------------------------------------------------------------------
# Fallback tests
# ---------------------------------------------------------------------------

def test_fallback_triggered_when_history_too_short(short_history):
    """len(history)=3 < window_k=7 → fallback must be selected."""
    result = generate_baseline_forecast(short_history, horizon=3, window_k=7)
    assert result["metadata"]["fallbackUsed"] is True
    assert result["metadata"]["methodUsed"] == "fallback"


def test_fallback_repeats_last_value(short_history):
    """Every predicted value must equal the last observed history value (7.0)."""
    result = generate_baseline_forecast(short_history, horizon=4, window_k=7)
    for point in result["forecast"]:
        assert point["predictedValue"] == 7.0


# ---------------------------------------------------------------------------
# Horizon count tests
# ---------------------------------------------------------------------------

def test_exact_horizon_count_moving_average(long_history):
    """Forecast list must contain exactly H items (moving average path)."""
    for h in [1, 3, 7]:
        result = generate_baseline_forecast(long_history, horizon=h, window_k=3)
        assert len(result["forecast"]) == h, f"Expected {h} points, got {len(result['forecast'])}"


def test_exact_horizon_count_fallback(short_history):
    """Forecast list must contain exactly H items (fallback path)."""
    for h in [1, 5, 10]:
        result = generate_baseline_forecast(short_history, horizon=h, window_k=7)
        assert len(result["forecast"]) == h, f"Expected {h} points, got {len(result['forecast'])}"


# ---------------------------------------------------------------------------
# Date generation tests
# ---------------------------------------------------------------------------

def test_dates_are_sequential(long_history):
    """Each consecutive pair of forecast dates must differ by exactly 1 day."""
    result = generate_baseline_forecast(long_history, horizon=5, window_k=3)
    dates = [
        datetime.strptime(p["date"], "%Y-%m-%d")
        for p in result["forecast"]
    ]
    for i in range(1, len(dates)):
        assert (dates[i] - dates[i - 1]).days == 1, (
            f"Dates not consecutive: {dates[i - 1].date()} → {dates[i].date()}"
        )


def test_first_date_follows_last_history_date(long_history):
    """First forecast date must be last history date + 1 day."""
    result = generate_baseline_forecast(long_history, horizon=3, window_k=3)
    last_history = datetime.strptime(long_history[-1]["date"], "%Y-%m-%d")
    first_forecast = datetime.strptime(result["forecast"][0]["date"], "%Y-%m-%d")
    assert first_forecast == last_history + timedelta(days=1)


# ---------------------------------------------------------------------------
# Validation error tests
# ---------------------------------------------------------------------------

def test_empty_history_raises():
    """Empty history list must raise ValueError."""
    with pytest.raises(ValueError, match="history must not be empty"):
        generate_baseline_forecast([], horizon=3, window_k=3)


def test_invalid_horizon_zero(short_history):
    """horizon=0 must raise ValueError mentioning 'horizon'."""
    with pytest.raises(ValueError, match="horizon"):
        generate_baseline_forecast(short_history, horizon=0, window_k=3)


def test_invalid_horizon_negative(short_history):
    """Negative horizon must raise ValueError mentioning 'horizon'."""
    with pytest.raises(ValueError, match="horizon"):
        generate_baseline_forecast(short_history, horizon=-5, window_k=3)


def test_invalid_window_k_zero(short_history):
    """window_k=0 must raise ValueError mentioning 'window_k'."""
    with pytest.raises(ValueError, match="window_k"):
        generate_baseline_forecast(short_history, horizon=3, window_k=0)


def test_invalid_method_raises(short_history):
    """method != 'baseline' must raise ValueError mentioning 'method'."""
    with pytest.raises(ValueError, match="method"):
        generate_baseline_forecast(short_history, horizon=3, window_k=3, method="trained")


def test_non_numeric_value_raises():
    """String value in history must raise TypeError."""
    history = [{"date": "2024-01-01", "value": "five"}]
    with pytest.raises((ValueError, TypeError)):
        generate_baseline_forecast(history, horizon=1, window_k=1)


def test_missing_date_field_raises():
    """History entry without 'date' must raise ValueError."""
    history = [{"value": 5.0}]
    with pytest.raises(ValueError, match="missing required field 'date'"):
        generate_baseline_forecast(history, horizon=1, window_k=1)


def test_missing_value_field_raises():
    """History entry without 'value' must raise ValueError."""
    history = [{"date": "2024-01-01"}]
    with pytest.raises(ValueError, match="missing required field 'value'"):
        generate_baseline_forecast(history, horizon=1, window_k=1)


# ---------------------------------------------------------------------------
# Output structure tests
# ---------------------------------------------------------------------------

def test_forecast_output_has_required_keys(short_history):
    """Top-level result must have 'status', 'forecast', and 'metadata'."""
    result = generate_baseline_forecast(short_history, horizon=2, window_k=7)
    assert "status" in result
    assert "forecast" in result
    assert "metadata" in result


def test_each_forecast_point_has_date_and_predicted_value(short_history):
    """Every item in forecast list must have 'date' and 'predictedValue'."""
    result = generate_baseline_forecast(short_history, horizon=2, window_k=7)
    for point in result["forecast"]:
        assert "date" in point
        assert "predictedValue" in point


def test_metadata_has_required_keys(short_history):
    """Metadata dict must have 'methodUsed', 'windowK', and 'fallbackUsed'."""
    result = generate_baseline_forecast(short_history, horizon=2, window_k=7)
    meta = result["metadata"]
    assert "methodUsed" in meta
    assert "windowK" in meta
    assert "fallbackUsed" in meta


# ---------------------------------------------------------------------------
# Boundary test
# ---------------------------------------------------------------------------

def test_boundary_len_equals_window_k_uses_moving_average(short_history):
    """When len(history) == window_k, moving average must be used (not fallback).

    short_history has 3 entries; setting window_k=3 sits exactly on the boundary.
    """
    result = generate_baseline_forecast(short_history, horizon=2, window_k=3)
    assert result["metadata"]["fallbackUsed"] is False
    assert result["metadata"]["methodUsed"] == "moving_average"
