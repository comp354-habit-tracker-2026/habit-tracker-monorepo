# ============================================================
# G13 - MMingQwQ - Unit Tests for analytics.business.__init__
# and analytics.presentation.views
# ============================================================

import importlib
import sys
import types
import unittest
from unittest.mock import patch, MagicMock


class DummyResponse:
    """Simple stand-in for DRF Response used in unit tests."""
    def __init__(self, data):
        self.data = data


class DummyAPIView:
    """Simple stand-in for DRF APIView."""
    pass


class DummyUser:
    """Simple authenticated user object for tests."""
    is_authenticated = True


class DummyRequest:
    """Simple request object with a user field."""
    def __init__(self, user=None):
        self.user = user or DummyUser()


class TestBusinessInit(unittest.TestCase):
    """Tests for analytics.business.__init__."""

    def test_business_init_exports_analytics_service_when_services_import_works(self):
        """
        Verifies AnalyticsService is exported in __all__
        when services import succeeds.
        """
        module_name = "analytics.business"

        fake_services = types.ModuleType("analytics.business.services")

        class FakeAnalyticsService:
            pass

        fake_services.AnalyticsService = FakeAnalyticsService

        with patch.dict(sys.modules, {
            "analytics.business.services": fake_services
        }):
            if module_name in sys.modules:
                del sys.modules[module_name]

            business_module = importlib.import_module(module_name)
            business_module = importlib.reload(business_module)

            self.assertIn("AnalyticsService", business_module.__all__)
            self.assertTrue(hasattr(business_module, "AnalyticsService"))

    def test_business_init_allows_missing_django_import(self):
        """
        Verifies module does not crash when services import fails
        because Django is unavailable.
        """
        module_name = "analytics.business"

        original_import = __import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name.endswith(".services") or name == "analytics.business.services":
                raise ModuleNotFoundError("No module named 'django'")
            return original_import(name, globals, locals, fromlist, level)

        with patch("builtins.__import__", side_effect=fake_import):
            if module_name in sys.modules:
                del sys.modules[module_name]

            business_module = importlib.import_module(module_name)
            business_module = importlib.reload(business_module)

            self.assertEqual(business_module.__all__, [])


class TestPresentationViews(unittest.TestCase):
    """Tests for analytics.presentation.views."""

    @classmethod
    def setUpClass(cls):
        """
        Inject minimal fake rest_framework modules so the view module
        can be imported even if DRF is not installed locally.
        """
        permissions_module = types.ModuleType("rest_framework.permissions")
        permissions_module.IsAuthenticated = object

        response_module = types.ModuleType("rest_framework.response")
        response_module.Response = DummyResponse

        views_module = types.ModuleType("rest_framework.views")
        views_module.APIView = DummyAPIView

        cls.patcher = patch.dict(
            sys.modules,
            {
                "rest_framework.permissions": permissions_module,
                "rest_framework.response": response_module,
                "rest_framework.views": views_module,
            },
        )
        cls.patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()

    def test_analytics_overview_view_get_returns_expected_keys(self):
        """
        Verifies AnalyticsOverviewView.get returns activity stats,
        trend analysis, and forecast.
        """
        module_name = "analytics.presentation.views"
        if module_name in sys.modules:
            del sys.modules[module_name]

        view_module = importlib.import_module(module_name)

        fake_service = MagicMock()
        fake_service.activity_statistics.return_value = {"total": 10}
        fake_service.trend_snapshot.return_value = {"trend": "up"}
        fake_service.forecast_preview.return_value = {"forecast": []}

        with patch.object(view_module, "AnalyticsService", return_value=fake_service):
            view = view_module.AnalyticsOverviewView()
            request = DummyRequest()

            response = view.get(request)

            self.assertIn("activity_statistics", response.data)
            self.assertIn("trend_analysis", response.data)
            self.assertIn("forecast", response.data)

            self.assertEqual(response.data["activity_statistics"], {"total": 10})
            self.assertEqual(response.data["trend_analysis"], {"trend": "up"})
            self.assertEqual(response.data["forecast"], {"forecast": []})

            fake_service.activity_statistics.assert_called_once_with(request.user)
            fake_service.trend_snapshot.assert_called_once_with(request.user)
            fake_service.forecast_preview.assert_called_once_with(request.user)

    def test_health_indicators_view_get_returns_expected_keys(self):
        """
        Verifies HealthIndicatorsView.get returns activity stats
        and inactivity evaluation.
        """
        module_name = "analytics.presentation.views"
        if module_name in sys.modules:
            del sys.modules[module_name]

        view_module = importlib.import_module(module_name)

        fake_service = MagicMock()
        fake_service.activity_statistics.return_value = {"total": 4}
        fake_service.inactivity_evaluation.return_value = {
            "inactive": True,
            "severity": "mild",
        }

        with patch.object(view_module, "AnalyticsService", return_value=fake_service):
            view = view_module.HealthIndicatorsView()
            request = DummyRequest()

            response = view.get(request)

            self.assertIn("activity_statistics", response.data)
            self.assertIn("inactivity_evaluation", response.data)

            self.assertEqual(response.data["activity_statistics"], {"total": 4})
            self.assertEqual(
                response.data["inactivity_evaluation"],
                {"inactive": True, "severity": "mild"},
            )

            fake_service.activity_statistics.assert_called_once_with(request.user)
            fake_service.inactivity_evaluation.assert_called_once_with(request.user)


if __name__ == "__main__":
    unittest.main()