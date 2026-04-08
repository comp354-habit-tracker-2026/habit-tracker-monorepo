import unittest
from unittest.mock import MagicMock

from analytics.business.services import AnalyticsService


class TestAnalyticsService(unittest.TestCase):
    def test_inactivity_evaluation_calls_repository(self):
        service = AnalyticsService()
        service.repository = MagicMock()

        service.repository.inactivity_evaluation.return_value = {
            "inactive": True
        }

        result = service.inactivity_evaluation("user123")

        self.assertEqual(result, {"inactive": True})
        service.repository.inactivity_evaluation.assert_called_once_with("user123")