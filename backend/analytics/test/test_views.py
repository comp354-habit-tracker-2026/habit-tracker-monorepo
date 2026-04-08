import unittest
from unittest.mock import patch, MagicMock
from rest_framework.test import APIRequestFactory, force_authenticate

from analytics.presentation.views import HealthIndicatorsView


class DummyUser:
    is_authenticated = True


class TestHealthIndicatorsView(unittest.TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = HealthIndicatorsView.as_view()
        self.user = DummyUser()

    @patch("analytics.presentation.views.AnalyticsService")
    def test_get_success(self, mock_service_class):
        mock_service = MagicMock()
        mock_service.activity_statistics.return_value = {"total": 5}
        mock_service.inactivity_evaluation.return_value = {"inactive": False}
        mock_service_class.return_value = mock_service

        request = self.factory.get("/health-indicators/")
        force_authenticate(request, user=self.user)

        response = self.view(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("activity_statistics", response.data)
        self.assertIn("inactivity_evaluation", response.data)