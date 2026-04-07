# ============================================================
# G13 - MMingQwQ - Unit Tests for Validation & Explainability
# ============================================================

import unittest

from backend.analytics.business.validation_explainability import (
    validate_explainability_inputs,
    ExplainabilityBuilder,
    format_error_response,
    format_success_response,
)


class TestValidateExplainabilityInputs(unittest.TestCase):
    """Unit tests for input validation."""

    def test_valid_inputs(self):
        """Accepts valid inputs without raising errors."""
        indicators = {"volume": 300.0, "consistency": 75.0, "inactive": 0}
        health_score = 82.5
        score_range = "Excellent"
        alerts = ["No inactivity alert triggered"]

        validate_explainability_inputs(
            indicators=indicators,
            health_score=health_score,
            score_range=score_range,
            alerts=alerts,
        )

    def test_invalid_indicators_type(self):
        """Raises error if indicators is not a dictionary."""
        with self.assertRaises(ValueError) as context:
            validate_explainability_inputs(
                indicators=["bad", "input"],
                health_score=80,
                score_range="Good",
                alerts=[],
            )

        self.assertEqual(str(context.exception), "Indicators must be a dictionary.")

    def test_invalid_indicator_value_type(self):
        """Raises error if an indicator value is not numeric or None."""
        with self.assertRaises(ValueError) as context:
            validate_explainability_inputs(
                indicators={"volume": "high"},
                health_score=80,
                score_range="Good",
                alerts=[],
            )

        self.assertEqual(
            str(context.exception),
            "Indicator 'volume' must be numeric or None."
        )

    def test_invalid_health_score_type(self):
        """Raises error if health score is not numeric."""
        with self.assertRaises(ValueError) as context:
            validate_explainability_inputs(
                indicators={"volume": 200},
                health_score="bad",
                score_range="Good",
                alerts=[],
            )

        self.assertEqual(str(context.exception), "Health score must be numeric.")

    def test_health_score_out_of_range_low(self):
        """Raises error if health score is below 0."""
        with self.assertRaises(ValueError) as context:
            validate_explainability_inputs(
                indicators={"volume": 200},
                health_score=-1,
                score_range="Low",
                alerts=[],
            )

        self.assertEqual(
            str(context.exception),
            "Health score must be between 0 and 100."
        )

    def test_health_score_out_of_range_high(self):
        """Raises error if health score is above 100."""
        with self.assertRaises(ValueError) as context:
            validate_explainability_inputs(
                indicators={"volume": 200},
                health_score=120,
                score_range="Excellent",
                alerts=[],
            )

        self.assertEqual(
            str(context.exception),
            "Health score must be between 0 and 100."
        )

    def test_invalid_alerts_type(self):
        """Raises error if alerts is not a list."""
        with self.assertRaises(ValueError) as context:
            validate_explainability_inputs(
                indicators={"volume": 200},
                health_score=80,
                score_range="Good",
                alerts="bad alerts",
            )

        self.assertEqual(
            str(context.exception),
            "Alerts must be a list of strings."
        )

    def test_invalid_alert_item_type(self):
        """Raises error if one alert is not a string."""
        with self.assertRaises(ValueError) as context:
            validate_explainability_inputs(
                indicators={"volume": 200},
                health_score=80,
                score_range="Good",
                alerts=["ok", 123],
            )

        self.assertEqual(
            str(context.exception),
            "Each alert must be a string."
        )


class TestExplainabilityBuilder(unittest.TestCase):
    """Unit tests for explanation generation."""

    def setUp(self):
        """Create builder instance before each test."""
        self.builder = ExplainabilityBuilder()

    def test_build_explanation_with_complete_data(self):
        """Builds explanation list with full input data."""
        indicators = {"volume": 300.0, "consistency": 75.0, "inactive": 0}
        health_score = 82.5
        score_range = "Excellent"
        alerts = ["No inactivity alert triggered"]

        result = self.builder.build_explanation(
            indicators=indicators,
            health_score=health_score,
            score_range=score_range,
            alerts=alerts,
        )

        self.assertIsInstance(result, list)
        self.assertIn("Volume value is 300.0.", result)
        self.assertIn("Consistency value is 75.0.", result)
        self.assertIn("Inactive value is 0.", result)
        self.assertIn("Health score is 82.5.", result)
        self.assertIn("Score range: Excellent.", result)
        self.assertIn("Alert: No inactivity alert triggered", result)

    def test_build_explanation_with_missing_indicator(self):
        """Explains missing indicator values clearly."""
        indicators = {"volume": None}

        result = self.builder.build_explanation(
            indicators=indicators,
            health_score=None,
            score_range=None,
            alerts=None,
        )

        self.assertIn("Volume data is missing.", result)
        self.assertIn(
            "Health score could not be computed due to missing data.",
            result
        )

    def test_build_explanation_without_alerts(self):
        """Builds explanation correctly when alerts are absent."""
        indicators = {"volume": 100.0}

        result = self.builder.build_explanation(
            indicators=indicators,
            health_score=45.0,
            score_range="Fair",
            alerts=[],
        )

        self.assertIn("Volume value is 100.0.", result)
        self.assertIn("Health score is 45.0.", result)
        self.assertIn("Score range: Fair.", result)

        alert_lines = [item for item in result if item.startswith("Alert:")]
        self.assertEqual(len(alert_lines), 0)


class TestResponseFormatting(unittest.TestCase):
    """Unit tests for response formatting helpers."""

    def test_format_error_response(self):
        """Formats error response correctly."""
        result = format_error_response("Invalid input")

        expected = {
            "status": "error",
            "message": "Invalid input",
        }

        self.assertEqual(result, expected)

    def test_format_success_response(self):
        """Formats success response correctly."""
        payload = {"health_score": 80}
        result = format_success_response(payload)

        expected = {
            "status": "success",
            "data": payload,
        }

        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()