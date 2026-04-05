#chatgpt was used

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from core.business.metrics import compute_all_metrics
from core.business.predict_model import predict as trained_predict
from core.business.baseline_model import predict as baseline_predict


class ForecastModel(Protocol):
    def predict(self, inputs: list[float], horizon: int) -> list[float]:
        ...


@dataclass
class EvaluationResult:
    model_name: str
    metrics: dict[str, float]


class FunctionForecastModelWrapper:
    def __init__(
        self,
        predict_function: Callable[..., dict],
        model_label: str,
    ) -> None:
        self.predict_function = predict_function
        self.model_label = model_label

    def predict(self, inputs: list[float], horizon: int) -> list[float]:
        if not inputs:
            raise ValueError("inputs must not be empty")

        if horizon <= 0:
            raise ValueError("horizon must be positive")

        result = self.predict_function(x_last=inputs, horizon=horizon)

        if not isinstance(result, dict):
            raise ValueError(f"{self.model_label} returned unexpected result type")

        if result.get("status") != "success":
            raise ValueError(f"{self.model_label} failed: {result}")

        predictions = result.get("predictions")
        if predictions is None:
            raise ValueError(f"{self.model_label} did not return predictions")

        try:
            predictions = [float(value) for value in predictions]
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{self.model_label} returned invalid prediction values"
            ) from exc

        if len(predictions) != horizon:
            raise ValueError(
                f"{self.model_label} returned {len(predictions)} predictions, expected {horizon}"
            )

        return predictions


def evaluate_model(
    model_name: str,
    model: ForecastModel,
    inputs: list[float],
    y_true: list[float],
) -> EvaluationResult:
    horizon = len(y_true)

    if horizon == 0:
        raise ValueError("y_true must not be empty")

    y_pred = model.predict(inputs, horizon)
    metrics = compute_all_metrics(y_true, y_pred)

    return EvaluationResult(model_name=model_name, metrics=metrics)


def print_results(results: list[EvaluationResult]) -> None:
    print("\n=== Forecast Evaluation Results ===")
    for result in results:
        print(f"\nModel: {result.model_name}")
        print(f"  MAE:  {result.metrics['MAE']:.4f}")
        print(f"  RMSE: {result.metrics['RMSE']:.4f}")
        print(f"  MAPE: {result.metrics['MAPE']:.4f}")


def save_report(
    results: list[EvaluationResult],
    output_path: str = "REPORT.md",
) -> None:
    with open(output_path, "w", encoding="utf-8") as file:
        file.write("# Forecast Comparison Report\n\n")
        file.write("| Model | MAE | RMSE | MAPE |\n")
        file.write("|-------|-----|------|------|\n")

        for result in results:
            file.write(
                f"| {result.model_name} "
                f"| {result.metrics['MAE']:.4f} "
                f"| {result.metrics['RMSE']:.4f} "
                f"| {result.metrics['MAPE']:.4f} |\n"
            )


def evaluate_all(
    inputs: list[float],
    y_true: list[float],
) -> list[EvaluationResult]:
    baseline_model = FunctionForecastModelWrapper(
        predict_function=baseline_predict,
        model_label="Baseline model",
    )

    trained_model = FunctionForecastModelWrapper(
        predict_function=trained_predict,
        model_label="Trained model",
    )

    return [
        evaluate_model("Baseline", baseline_model, inputs, y_true),
        evaluate_model("Trained", trained_model, inputs, y_true),
    ]


def main() -> None:
    # Example data only. Replace with real test-set loading later.
    inputs = [100.0, 120.0, 130.0, 125.0]
    y_true = [128.0, 131.0, 135.0]

    results = evaluate_all(inputs, y_true)
    print_results(results)
    save_report(results)


if __name__ == "__main__":
    main()