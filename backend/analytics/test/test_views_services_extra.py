import unittest
from unittest.mock import MagicMock, patch

from analytics.business.services import AnalyticsService


class TestAnalyticsServiceExtra(unittest.TestCase):
    def test_inactivity_evaluation_calls_repository(self):
        service = AnalyticsService()
        service.repository = MagicMock()
        service.repository.inactivity_evaluation.return_value = {
            "inactive": True,
            "severity": "mild",
        }

        result = service.inactivity_evaluation("user123")

        self.assertEqual(result, {"inactive": True, "severity": "mild"})
        service.repository.inactivity_evaluation.assert_called_once_with("user123")