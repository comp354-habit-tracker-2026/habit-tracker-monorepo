#chatgpt was used 

import pytest

from core.business.eval import  (
    EvaluationResult,
    FunctionForecastModelWrapper,
    evaluate_model,
    save_report,
    print_results,
)


def fake_success_predict(x_last=None, horizon=1):
    return {
        "status": "success",
        "horizon": horizon,
        "predictions": [200.0] * horizon,
    }


def fake_failure_predict(x_last=None, horizon=1):
    return {
        "status": "error",
        "message": "Model failed",
    }


def fake_missing_predictions_predict(x_last=None, horizon=1):
    return {
        "status": "success",
        "horizon": horizon,
    }


def fake_wrong_length_predict(x_last=None, horizon=1):
    return {
        "status": "success",
        "horizon": horizon,
        "predictions": [123.0],
    }


def fake_invalid_value_predict(x_last=None, horizon=1):
    return {
        "status": "success",
        "horizon": horizon,
        "predictions": ["bad_value"] * horizon,
    }


def test_wrapper_returns_predictions_on_success() -> None:
    model = FunctionForecastModelWrapper(
        predict_function=fake_success_predict,
        model_label="Test model",
    )

    predictions = model.predict(inputs=[10.0, 20.0, 30.0], horizon=3)

    assert predictions == [200.0, 200.0, 200.0]


def test_wrapper_raises_on_failure_status() -> None:
    model = FunctionForecastModelWrapper(
        predict_function=fake_failure_predict,
        model_label="Test model",
    )

    with pytest.raises(ValueError, match="failed"):
        model.predict(inputs=[10.0, 20.0], horizon=2)


def test_wrapper_raises_when_predictions_missing() -> None:
    model = FunctionForecastModelWrapper(
        predict_function=fake_missing_predictions_predict,
        model_label="Test model",
    )

    with pytest.raises(ValueError, match="did not return predictions"):
        model.predict(inputs=[10.0, 20.0], horizon=2)


def test_wrapper_raises_on_prediction_length_mismatch() -> None:
    model = FunctionForecastModelWrapper(
        predict_function=fake_wrong_length_predict,
        model_label="Test model",
    )

    with pytest.raises(ValueError, match="expected 3"):
        model.predict(inputs=[10.0, 20.0, 30.0], horizon=3)


def test_wrapper_raises_on_invalid_prediction_values() -> None:
    model = FunctionForecastModelWrapper(
        predict_function=fake_invalid_value_predict,
        model_label="Test model",
    )

    with pytest.raises(ValueError, match="invalid prediction values"):
        model.predict(inputs=[10.0, 20.0], horizon=2)


def test_wrapper_raises_on_empty_inputs() -> None:
    model = FunctionForecastModelWrapper(
        predict_function=fake_success_predict,
        model_label="Test model",
    )

    with pytest.raises(ValueError, match="inputs must not be empty"):
        model.predict(inputs=[], horizon=2)


def test_wrapper_raises_on_non_positive_horizon() -> None:
    model = FunctionForecastModelWrapper(
        predict_function=fake_success_predict,
        model_label="Test model",
    )

    with pytest.raises(ValueError, match="horizon must be positive"):
        model.predict(inputs=[10.0, 20.0], horizon=0)


def test_evaluate_model_computes_metrics() -> None:
    model = FunctionForecastModelWrapper(
        predict_function=fake_success_predict,
        model_label="Test model",
    )

    result = evaluate_model(
        model_name="Wrapped model",
        model=model,
        inputs=[100.0, 110.0, 120.0],
        y_true=[190.0, 210.0, 205.0],
    )

    assert result.model_name == "Wrapped model"
    assert "MAE" in result.metrics
    assert "RMSE" in result.metrics
    assert "MAPE" in result.metrics

    # predictions = [200, 200, 200]
    # absolute errors = [10, 10, 5]
    expected_mae = (10 + 10 + 5) / 3
    assert result.metrics["MAE"] == pytest.approx(expected_mae)


def test_evaluate_model_raises_when_y_true_empty() -> None:
    model = FunctionForecastModelWrapper(
        predict_function=fake_success_predict,
        model_label="Test model",
    )

    with pytest.raises(ValueError, match="y_true must not be empty"):
        evaluate_model(
            model_name="Wrapped model",
            model=model,
            inputs=[100.0, 110.0],
            y_true=[],
        )


def test_save_report_creates_markdown_file(tmp_path) -> None:
    results = [
        EvaluationResult(
            model_name="Baseline",
            metrics={"MAE": 1.0, "RMSE": 2.0, "MAPE": 3.0},
        ),
        EvaluationResult(
            model_name="Trained",
            metrics={"MAE": 0.5, "RMSE": 1.5, "MAPE": 2.5},
        ),
    ]

    output_file = tmp_path / "REPORT.md"
    save_report(results, output_path=str(output_file))

    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")
    assert "# Forecast Comparison Report" in content
    assert "| Model | MAE | RMSE | MAPE |" in content
    assert "| Baseline | 1.0000 | 2.0000 | 3.0000 |" in content
    assert "| Trained | 0.5000 | 1.5000 | 2.5000 |" in content

def test_print_results_outputs_expected_text(capsys) -> None:
    results = [
        EvaluationResult(
            model_name="Baseline",
            metrics={"MAE": 1.0, "RMSE": 2.0, "MAPE": 3.0},
        ),
        EvaluationResult(
            model_name="Trained",
            metrics={"MAE": 0.5, "RMSE": 1.5, "MAPE": 2.5},
        ),
    ]

    print_results(results)
    captured = capsys.readouterr()

    assert "Forecast Evaluation Results" in captured.out
    #assert "Model: Baseline" in captured.out
    assert "MAE: 1.0000" in captured.out
    assert "RMSE: 2.0000" in captured.out
    assert "MAPE: 3.0000" in captured.out

    assert "Model: Trained" in captured.out
    assert "MAE: 0.5000" in captured.out
    assert "RMSE: 1.5000" in captured.out
    assert "MAPE: 2.5000" in captured.out