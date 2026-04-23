"""
Group 16 – Analytics API & Export
Tests for analytics/presentation/views.py
"""

from unittest.mock import MagicMock, patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status

from analytics.presentation.views import (
    AnalyticsOverviewView,
    HealthIndicatorsView,
    InactivitiesView,
    HealthTrackingView,
    HealthForecastView,
    ActivityForecastView,
    GoalsAnalyticsSummaryView,
    AtRiskGoalsView,
    GoalCompletionRateView,
    GoalInsightsView,
)

User = get_user_model()


def make_user(username="testuser"):
    return User(username=username, id=1)


def make_request(user, query_params=None):
    """MagicMock request with exactly what views need — no DRF dispatch."""
    request = MagicMock()
    request.user = user
    request.query_params = query_params or {}
    return request


# ---------------------------------------------------------------------------
# AnalyticsOverviewView
# ---------------------------------------------------------------------------

class AnalyticsOverviewViewTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.view = AnalyticsOverviewView()

    @patch("analytics.presentation.views.AnalyticsService")
    def test_returns_200_with_expected_keys(self, MockService):
        svc = MockService.return_value
        svc.activity_statistics.return_value = {"steps": 1000}
        svc.trend_snapshot.return_value = {"trend": "up"}
        svc.forecast_preview.return_value = {"forecast": []}

        response = self.view.get(make_request(self.user))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("activity_statistics", response.data)
        self.assertIn("trend_analysis", response.data)
        self.assertIn("forecast", response.data)


# ---------------------------------------------------------------------------
# Team 13 views
# ---------------------------------------------------------------------------

class HealthIndicatorsViewTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.view = HealthIndicatorsView()

    @patch("analytics.presentation.views.AnalyticsService")
    def test_returns_200(self, MockService):
        svc = MockService.return_value
        svc.activity_statistics.return_value = {"steps": 500}
        svc.inactivity_evaluation.return_value = {"inactive": False}

        response = self.view.get(make_request(self.user))

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class InactivitiesViewTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.view = InactivitiesView()

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_returns_expected_fields(self, MockRepo):
        MockRepo.return_value.inactivity_evaluation.return_value = {
            "days_since_last_activity": 5,
            "inactive": True,
            "severity": "high",
            "extra_field": "ignored",
        }
        response = self.view.get(make_request(self.user))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["days_since_last_activity"], 5)
        self.assertTrue(response.data["inactive"])
        self.assertEqual(response.data["severity"], "high")
        self.assertNotIn("extra_field", response.data)

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_service_called_with_user(self, MockRepo):
        repo = MockRepo.return_value
        repo.inactivity_evaluation.return_value = {
            "days_since_last_activity": 0,
            "inactive": False,
            "severity": "none",
        }
        self.view.get(make_request(self.user))
        repo.inactivity_evaluation.assert_called_once_with(self.user)


class HealthTrackingViewTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.view = HealthTrackingView()

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_returns_200_with_weekly_goal_completion(self, MockRepo):
        MockRepo.return_value.trend_snapshot.return_value = {"completion": 80}

        response = self.view.get(make_request(self.user))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("weekly_goal_completion", response.data)

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_weekly_goal_completion_value(self, MockRepo):
        MockRepo.return_value.trend_snapshot.return_value = {"completion": 75}

        response = self.view.get(make_request(self.user))

        self.assertEqual(response.data["weekly_goal_completion"], {"completion": 75})


class HealthForecastViewTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.view = HealthForecastView()

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_returns_200_with_next_week_prediction(self, MockRepo):
        MockRepo.return_value.forecast_preview.return_value = {"next": [1, 2, 3]}

        response = self.view.get(make_request(self.user))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("next_week_prediction", response.data)

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_next_week_prediction_value(self, MockRepo):
        MockRepo.return_value.forecast_preview.return_value = {"next": ["a", "b"]}

        response = self.view.get(make_request(self.user))

        self.assertEqual(response.data["next_week_prediction"], {"next": ["a", "b"]})


# ---------------------------------------------------------------------------
# Team 14 views
# ---------------------------------------------------------------------------

class ActivityForecastViewTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.view = ActivityForecastView()

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_returns_200_with_metadata(self, MockRepo):
        MockRepo.return_value.forecast_preview.return_value = {
            "predictions": [{"date": "2026-04-01", "predictedValue": 5.0}],
            "fallbackUsed": False,
        }
        response = self.view.get(make_request(
            self.user, query_params={"method": "linear", "windowK": "5"}
        ))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("predictions", response.data)
        self.assertEqual(response.data["metadata"]["methodUsed"], "linear")
        self.assertEqual(response.data["metadata"]["windowK"], "5")

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_defaults_method_and_window(self, MockRepo):
        MockRepo.return_value.forecast_preview.return_value = {
            "predictions": [],
            "fallbackUsed": True,
        }
        response = self.view.get(make_request(self.user))

        self.assertEqual(response.data["metadata"]["methodUsed"], "baseline")
        self.assertEqual(response.data["metadata"]["windowK"], 3)
        self.assertTrue(response.data["metadata"]["fallbackUsed"])

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_returns_500_on_exception(self, MockRepo):
        MockRepo.return_value.forecast_preview.side_effect = Exception("DB down")

        response = self.view.get(make_request(self.user))

        self.assertEqual(response.status_code, 500)
        self.assertIn("Forecasting Engine Error", response.data)

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_fallback_false_when_not_set(self, MockRepo):
        MockRepo.return_value.forecast_preview.return_value = {"predictions": []}

        response = self.view.get(make_request(self.user))

        self.assertFalse(response.data["metadata"]["fallbackUsed"])


class GoalsAnalyticsSummaryViewTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.view = GoalsAnalyticsSummaryView()

    @patch("analytics.presentation.views.GoalService")
    def test_counts_and_average(self, MockGoalService):
        svc = MockGoalService.return_value
        svc.get_user_queryset.return_value = [MagicMock(), MagicMock(), MagicMock()]
        svc.get_status_summary.side_effect = [
            {"status": "ACHIEVED", "percentComplete": 100},
            {"status": "ON_TRACK", "percentComplete": 70},
            {"status": "AT_RISK",  "percentComplete": 40},
        ]
        response = self.view.get(make_request(self.user))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["totalGoals"], 3)
        self.assertEqual(response.data["achieved"], 1)
        self.assertEqual(response.data["onTrack"], 1)
        self.assertEqual(response.data["atRisk"], 1)
        self.assertAlmostEqual(response.data["averageCompletion"], 70.0)

    @patch("analytics.presentation.views.GoalService")
    def test_empty_queryset_returns_zero_average(self, MockGoalService):
        MockGoalService.return_value.get_user_queryset.return_value = []

        response = self.view.get(make_request(self.user))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["averageCompletion"], 0)
        self.assertEqual(response.data["totalGoals"], 0)

    @patch("analytics.presentation.views.GoalService")
    def test_all_achieved(self, MockGoalService):
        svc = MockGoalService.return_value
        svc.get_user_queryset.return_value = [MagicMock(), MagicMock()]
        svc.get_status_summary.side_effect = [
            {"status": "ACHIEVED", "percentComplete": 100},
            {"status": "ACHIEVED", "percentComplete": 100},
        ]
        response = self.view.get(make_request(self.user))

        self.assertEqual(response.data["achieved"], 2)
        self.assertEqual(response.data["onTrack"], 0)
        self.assertEqual(response.data["atRisk"], 0)
        self.assertAlmostEqual(response.data["averageCompletion"], 100.0)


class AtRiskGoalsViewTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.view = AtRiskGoalsView()

    @patch("analytics.presentation.views.GoalService")
    def test_filters_at_risk_goals(self, MockGoalService):
        svc = MockGoalService.return_value
        svc.get_user_queryset.return_value = [MagicMock(), MagicMock()]
        svc.get_status_summary.side_effect = [
            {"status": "AT_RISK",  "percentComplete": 30},
            {"status": "ACHIEVED", "percentComplete": 100},
        ]
        response = self.view.get(make_request(self.user))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["goals"]), 1)

    @patch("analytics.presentation.views.GoalService")
    def test_no_at_risk_goals(self, MockGoalService):
        svc = MockGoalService.return_value
        svc.get_user_queryset.return_value = [MagicMock()]
        svc.get_status_summary.return_value = {"status": "ON_TRACK", "percentComplete": 80}

        response = self.view.get(make_request(self.user))

        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["goals"]), 0)


class GoalCompletionRateViewTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.view = GoalCompletionRateView()

    @patch("analytics.presentation.views.GoalService")
    def test_completion_rate_calculation(self, MockGoalService):
        svc = MockGoalService.return_value
        svc.get_user_queryset.return_value = [MagicMock(), MagicMock()]
        svc.get_status_summary.side_effect = [
            {"status": "ACHIEVED", "percentComplete": 100},
            {"status": "MISSED",   "percentComplete": 10},
        ]
        response = self.view.get(make_request(self.user))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertAlmostEqual(response.data["completionRate"], 50.0)

    @patch("analytics.presentation.views.GoalService")
    def test_zero_total_returns_zero(self, MockGoalService):
        MockGoalService.return_value.get_user_queryset.return_value = []

        response = self.view.get(make_request(self.user))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["completionRate"], 0)

    @patch("analytics.presentation.views.GoalService")
    def test_all_achieved_is_100_percent(self, MockGoalService):
        svc = MockGoalService.return_value
        svc.get_user_queryset.return_value = [MagicMock(), MagicMock()]
        svc.get_status_summary.side_effect = [
            {"status": "ACHIEVED", "percentComplete": 100},
            {"status": "ACHIEVED", "percentComplete": 100},
        ]
        response = self.view.get(make_request(self.user))

        self.assertAlmostEqual(response.data["completionRate"], 100.0)


class GoalInsightsViewTests(TestCase):

    def setUp(self):
        self.user = make_user()
        self.view = GoalInsightsView()

    @patch("analytics.presentation.views.GoalService")
    def test_at_risk_and_missed_insights(self, MockGoalService):
        svc = MockGoalService.return_value
        svc.get_user_queryset.return_value = [MagicMock(), MagicMock(), MagicMock()]
        svc.get_status_summary.side_effect = [
            {"status": "AT_RISK", "percentComplete": 20},
            {"status": "MISSED",  "percentComplete": 0},
            {"status": "MISSED",  "percentComplete": 5},
        ]
        response = self.view.get(make_request(self.user))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        insights = response.data["insights"]
        self.assertTrue(any("at risk" in i for i in insights))
        self.assertTrue(any("missed" in i for i in insights))
        self.assertTrue(any("below 50%" in i for i in insights))

    @patch("analytics.presentation.views.GoalService")
    def test_empty_goals_returns_empty_insights(self, MockGoalService):
        MockGoalService.return_value.get_user_queryset.return_value = []

        response = self.view.get(make_request(self.user))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["insights"], [])

    @patch("analytics.presentation.views.GoalService")
    def test_no_insight_when_all_on_track_above_50(self, MockGoalService):
        svc = MockGoalService.return_value
        svc.get_user_queryset.return_value = [MagicMock(), MagicMock()]
        svc.get_status_summary.side_effect = [
            {"status": "ON_TRACK", "percentComplete": 80},
            {"status": "ON_TRACK", "percentComplete": 90},
        ]
        response = self.view.get(make_request(self.user))

        self.assertEqual(response.data["insights"], [])

    @patch("analytics.presentation.views.GoalService")
    def test_below_50_avg_triggers_insight(self, MockGoalService):
        svc = MockGoalService.return_value
        svc.get_user_queryset.return_value = [MagicMock()]
        svc.get_status_summary.return_value = {"status": "ON_TRACK", "percentComplete": 30}

        response = self.view.get(make_request(self.user))

        self.assertTrue(any("below 50%" in i for i in response.data["insights"]))

    @patch("analytics.presentation.views.GoalService")
    def test_response_includes_at_risk_and_missed_lists(self, MockGoalService):
        svc = MockGoalService.return_value
        g1, g2 = MagicMock(), MagicMock()
        svc.get_user_queryset.return_value = [g1, g2]
        svc.get_status_summary.side_effect = [
            {"status": "AT_RISK", "percentComplete": 10},
            {"status": "MISSED",  "percentComplete": 0},
        ]
        response = self.view.get(make_request(self.user))

        self.assertIn("atRiskGoals", response.data)
        self.assertIn("missedGoals", response.data)
        self.assertEqual(len(response.data["atRiskGoals"]), 1)
        self.assertEqual(len(response.data["missedGoals"]), 1)