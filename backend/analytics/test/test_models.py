# ============================================================
# G13 - FadyRizkalla - Health Score Model - PR #296
# ============================================================
import unittest

from backend.analytics.business.models import HealthScoreModel, HealthScoreResult


class TestHealthScoreModel(unittest.TestCase):
    """Unit tests for the HealthScoreModel."""

    def setUp(self):
        """Create model instance before each test."""
        self.model = HealthScoreModel()

    def test_compute_health_score_all_indicators_present(self):
        """Computes score correctly when all indicators are available."""
        indicators = {
            "volume": 300.0,
            "consistency": 80.0,
            "inactive": 0,
        }

        result = self.model.compute_health_score(indicators)

        self.assertIsInstance(result, HealthScoreResult)
        self.assertIsNotNone(result.score)
        self.assertGreaterEqual(result.score, 0)
        self.assertLessEqual(result.score, 100)
        self.assertIn(result.score_range, ["Excellent", "Good", "Fair", "Low"])
        self.assertIn("Final score", result.explanation)

    def test_compute_health_score_missing_volume(self):
        """Reweights remaining indicators when volume is missing."""
        indicators = {
            "volume": None,
            "consistency": 75.0,
            "inactive": 0,
        }

        result = self.model.compute_health_score(indicators)

        self.assertIsNotNone(result.score)
        self.assertGreaterEqual(result.score, 0)
        self.assertLessEqual(result.score, 100)

    def test_compute_health_score_missing_consistency(self):
        """Reweights remaining indicators when consistency is missing."""
        indicators = {
            "volume": 400.0,
            "consistency": None,
            "inactive": 1,
        }

        result = self.model.compute_health_score(indicators)

        self.assertIsNotNone(result.score)
        self.assertGreaterEqual(result.score, 0)
        self.assertLessEqual(result.score, 100)

    def test_compute_health_score_all_missing(self):
        """Returns no score when all indicators are missing."""
        indicators = {
            "volume": None,
            "consistency": None,
            "inactive": None,
        }

        result = self.model.compute_health_score(indicators)

        self.assertIsNone(result.score)
        self.assertEqual(result.score_range, "No Score")
        self.assertEqual(
            result.explanation,
            "No sufficient data available to compute health score."
        )

    def test_compute_health_score_inactive_penalty(self):
        """Inactive user should receive lower score than active user."""
        active_indicators = {
            "volume": 300.0,
            "consistency": 80.0,
            "inactive": 0,
        }

        inactive_indicators = {
            "volume": 300.0,
            "consistency": 80.0,
            "inactive": 1,
        }

        active_result = self.model.compute_health_score(active_indicators)
        inactive_result = self.model.compute_health_score(inactive_indicators)

        self.assertIsNotNone(active_result.score)
        self.assertIsNotNone(inactive_result.score)
        self.assertGreater(active_result.score, inactive_result.score)

    def test_compute_health_score_volume_capped_at_100(self):
        """Very large volume should still result in score <= 100."""
        indicators = {
            "volume": 10000.0,
            "consistency": 90.0,
            "inactive": 0,
        }

        result = self.model.compute_health_score(indicators)

        self.assertIsNotNone(result.score)
        self.assertLessEqual(result.score, 100)

    def test_get_score_range_excellent(self):
        """Classifies excellent score correctly."""
        self.assertEqual(self.model._get_score_range(85), "Excellent")

    def test_get_score_range_good(self):
        """Classifies good score correctly."""
        self.assertEqual(self.model._get_score_range(65), "Good")

    def test_get_score_range_fair(self):
        """Classifies fair score correctly."""
        self.assertEqual(self.model._get_score_range(45), "Fair")

    def test_get_score_range_low(self):
        """Classifies low score correctly."""
        self.assertEqual(self.model._get_score_range(20), "Low")


if __name__ == "__main__":
    unittest.main()