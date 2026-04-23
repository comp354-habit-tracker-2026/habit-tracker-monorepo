"""
Group 16 – Analytics API & Export
Tests for analytics/presentation/views.py

Run with:
    python manage.py test analytics.presentation.tests
or:
    pytest backend/analytics/presentation/test_views.py
"""

from unittest.mock import MagicMock, patch, PropertyMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user(username="testuser"):
    """Return an unsaved User instance – enough for force_authenticate."""
    return User(username=username, id=1)


def make_authenticated_request(factory, user, query_params=None):
    """Build a GET request that is already force-authenticated."""
    url = "/"
    if query_params:
        qs = "&".join(f"{k}={v}" for k, v in query_params.items())
        url = f"/?{qs}"
    request = factory.get(url)
    force_authenticate(request, user=user)
    return request


# ---------------------------------------------------------------------------
# AnalyticsOverviewView
# ---------------------------------------------------------------------------

class AnalyticsOverviewViewTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = make_user()
        self.view = AnalyticsOverviewView.as_view()

    @patch("analytics.presentation.views.AnalyticsService")
    def test_returns_200_with_expected_keys(self, MockService):
        svc = MockService.return_value
        svc.activity_statistics.return_value = {"steps": 1000}
        svc.trend_snapshot.return_value = {"trend": "up"}
        svc.forecast_preview.return_value = {"forecast": []}

        request = make_authenticated_request(self.factory, self.user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("activity_statistics", response.data)
        self.assertIn("trend_analysis", response.data)
        self.assertIn("forecast", response.data)

    @patch("analytics.presentation.views.AnalyticsService")
    def test_requires_authentication(self, MockService):
        request = self.factory.get("/")  # intentionally unauthenticated
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
# ---------------------------------------------------------------------------
# Team 12 views
# ---------------------------------------------------------------------------

# class Team12ViewTests(TestCase):
#
#     def setUp(self):
#         self.factory = APIRequestFactory()
#         self.user = make_user()
#
#     @patch("analytics.presentation.views.Team12AnalyticsService")
#     def test_activity_statistics_view(self, MockService):
#         MockService.return_value.activity_statistics.return_value = {"distance": 42}
#         request = make_request(self.factory, None, self.user)
#         response = ActivityStatisticsView.as_view()(request)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data, {"distance": 42})
#
#     @patch("analytics.presentation.views.Team12AnalyticsService")
#     def test_personal_records_view(self, MockService):
#         MockService.return_value.personal_records.return_value = {"longest_run": 21}
#         request = make_request(self.factory, None, self.user)
#         response = PersonalRecordsView.as_view()(request)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#     @patch("analytics.presentation.views.Team12AnalyticsService")
#     def test_activity_type_breakdown_view(self, MockService):
#         MockService.return_value.activity_type_breakdown.return_value = {"Running": 5}
#         request = make_request(self.factory, None, self.user)
#         response = ActivityTypeBreakdownView.as_view()(request)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#     @patch("analytics.presentation.views.Team12AnalyticsService")
#     def test_activity_streaks_view(self, MockService):
#         MockService.return_value.activity_streaks.return_value = {"current_streak": 3}
#         request = make_request(self.factory, None, self.user)
#         response = ActivityStreaksView.as_view()(request)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#     @patch("analytics.presentation.views.Team12AnalyticsService")
#     def test_weekly_summary_passes_query_params(self, MockService):
#         svc = MockService.return_value
#         svc.weekly_summary.return_value = {"total": 10}
#         params = {"from": "2026-03-01", "to": "2026-03-07", "activity_type": "Running"}
#         request = make_request(self.factory, None, self.user, query_params=params)
#         response = WeeklySummaryView.as_view()(request)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         svc.weekly_summary.assert_called_once_with(
#             user=self.user,
#             from_param="2026-03-01",
#             to_param="2026-03-07",
#             activity_type="Running",
#         )
#
#     @patch("analytics.presentation.views.Team12AnalyticsService")
#     def test_weekly_summary_missing_params_defaults_to_none(self, MockService):
#         MockService.return_value.weekly_summary.return_value = {}
#         request = make_request(self.factory, None, self.user)
#         WeeklySummaryView.as_view()(request)
#         MockService.return_value.weekly_summary.assert_called_once_with(
#             user=self.user,
#             from_param=None,
#             to_param=None,
#             activity_type=None,
#         )


# ---------------------------------------------------------------------------
# Team 13 views
# ---------------------------------------------------------------------------

class HealthIndicatorsViewTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = make_user()

    @patch("analytics.presentation.views.AnalyticsService")
    def test_returns_200(self, MockService):
        svc = MockService.return_value
        svc.activity_statistics.return_value = {"steps": 500}
        svc.inactivity_evaluation.return_value = {"inactive": False}

        request = make_authenticated_request(self.factory, self.user)
        response = HealthIndicatorsView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("analytics.presentation.views.AnalyticsService")
    def test_requires_auth(self, MockService):
        request = self.factory.get("/")
        response = HealthIndicatorsView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class InactivitiesViewTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = make_user()

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_returns_expected_fields(self, MockRepo):
        MockRepo.return_value.inactivity_evaluation.return_value = {
            "days_since_last_activity": 5,
            "inactive": True,
            "severity": "high",
            "extra_field": "ignored",
        }
        request = make_authenticated_request(self.factory, self.user)
        response = InactivitiesView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["days_since_last_activity"], 5)
        self.assertTrue(response.data["inactive"])
        self.assertEqual(response.data["severity"], "high")
        self.assertNotIn("extra_field", response.data)

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_requires_auth(self, MockRepo):
        request = self.factory.get("/")
        response = InactivitiesView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_service_called_with_user(self, MockRepo):
        """Ensure the view passes request.user into the repository call."""
        repo = MockRepo.return_value
        repo.inactivity_evaluation.return_value = {
            "days_since_last_activity": 0,
            "inactive": False,
            "severity": "none",
        }
        request = make_authenticated_request(self.factory, self.user)
        InactivitiesView.as_view()(request)
        repo.inactivity_evaluation.assert_called_once_with(self.user)


class HealthTrackingViewTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = make_user()

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_returns_200_with_weekly_goal_completion(self, MockRepo):
        MockRepo.return_value.trend_snapshot.return_value = {"completion": 80}

        request = make_authenticated_request(self.factory, self.user)
        response = HealthTrackingView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("weekly_goal_completion", response.data)

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_weekly_goal_completion_value(self, MockRepo):
        MockRepo.return_value.trend_snapshot.return_value = {"completion": 75}

        request = make_authenticated_request(self.factory, self.user)
        response = HealthTrackingView.as_view()(request)

        self.assertEqual(response.data["weekly_goal_completion"], {"completion": 75})

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_requires_auth(self, MockRepo):
        request = self.factory.get("/")
        response = HealthTrackingView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class HealthForecastViewTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = make_user()

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_returns_200_with_next_week_prediction(self, MockRepo):
        MockRepo.return_value.forecast_preview.return_value = {"next": [1, 2, 3]}

        request = make_authenticated_request(self.factory, self.user)
        response = HealthForecastView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("next_week_prediction", response.data)

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_next_week_prediction_value(self, MockRepo):
        MockRepo.return_value.forecast_preview.return_value = {"next": ["a", "b"]}

        request = make_authenticated_request(self.factory, self.user)
        response = HealthForecastView.as_view()(request)

        self.assertEqual(response.data["next_week_prediction"], {"next": ["a", "b"]})

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_requires_auth(self, MockRepo):
        request = self.factory.get("/")
        response = HealthForecastView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ---------------------------------------------------------------------------
# Team 14 views
# ---------------------------------------------------------------------------

class ActivityForecastViewTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = make_user()

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_returns_200_with_metadata(self, MockRepo):
        MockRepo.return_value.forecast_preview.return_value = {
            "predictions": [{"date": "2026-04-01", "predictedValue": 5.0}],
            "fallbackUsed": False,
        }
        request = make_authenticated_request(
            self.factory, self.user,
            query_params={"method": "linear", "windowK": "5"},
        )
        response = ActivityForecastView.as_view()(request)

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
        request = make_authenticated_request(self.factory, self.user)
        response = ActivityForecastView.as_view()(request)

        self.assertEqual(response.data["metadata"]["methodUsed"], "baseline")
        self.assertEqual(response.data["metadata"]["windowK"], 3)
        self.assertTrue(response.data["metadata"]["fallbackUsed"])

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_returns_500_on_exception(self, MockRepo):
        MockRepo.return_value.forecast_preview.side_effect = Exception("DB down")

        request = make_authenticated_request(self.factory, self.user)
        response = ActivityForecastView.as_view()(request)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Forecasting Engine Error", response.data)

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_fallback_false_when_not_set(self, MockRepo):
        MockRepo.return_value.forecast_preview.return_value = {
            "predictions": [],
            # "fallbackUsed" deliberately absent → defaults to False
        }
        request = make_authenticated_request(self.factory, self.user)
        response = ActivityForecastView.as_view()(request)

        self.assertFalse(response.data["metadata"]["fallbackUsed"])

    @patch("analytics.presentation.views.AnalyticsRepository")
    def test_requires_auth(self, MockRepo):
        request = self.factory.get("/")
        response = ActivityForecastView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GoalsAnalyticsSummaryViewTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = make_user()

    @patch("analytics.presentation.views.GoalService")
    def test_counts_and_average(self, MockGoalService):
        svc = MockGoalService.return_value
        svc.get_user_queryset.return_value = [MagicMock(), MagicMock(), MagicMock()]
        svc.get_status_summary.side_effect = [
            {"status": "ACHIEVED", "percentComplete": 100},
            {"status": "ON_TRACK", "percentComplete": 70},
            {"status": "AT_RISK", "percentComplete": 40},
        ]
        request = make_authenticated_request(self.factory, self.user)
        response = GoalsAnalyticsSummaryView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["totalGoals"], 3)
        self.assertEqual(response.data["achieved"], 1)
        self.assertEqual(response.data["onTrack"], 1)
        self.assertEqual(response.data["atRisk"], 1)
        self.assertAlmostEqual(response.data["averageCompletion"], 70.0)

    @patch("analytics.presentation.views.GoalService")
    def test_empty_queryset_returns_zero_average(self, MockGoalService):
        MockGoalService.return_value.get_user_queryset.return_value = []

        request = make_authenticated_request(self.factory, self.user)
        response = GoalsAnalyticsSummaryView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["averageCompletion"], 0)
        self.assertEqual(response.data["totalGoals"], 0)

    @patch("analytics.presentation.views.GoalService")
    def test_requires_auth(self, MockGoalService):
        request = self.factory.get("/")
        response = GoalsAnalyticsSummaryView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("analytics.presentation.views.GoalService")
    def test_all_achieved(self, MockGoalService):
        svc = MockGoalService.return_value
        svc.get_user_queryset.return_value = [MagicMock(), MagicMock()]
        svc.get_status_summary.side_effect = [
            {"status": "ACHIEVED", "percentComplete": 100},
            {"status": "ACHIEVED", "percentComplete": 100},
        ]
        request = make_authenticated_request(self.factory, self.user)
        response = GoalsAnalyticsSummaryView.as_view()(request)

        self.assertEqual(response.data["achieved"], 2)
        self.assertEqual(response.data["onTrack"], 0)
        self.assertEqual(response.data["atRisk"], 0)
        self.assertAlmostEqual(response.data["averageCompletion"], 100.0)


class AtRiskGoalsViewTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = make_user()

    @patch("analytics.presentation.views.GoalService")
    def test_filters_at_risk_goals(self, MockGoalService):
        svc = MockGoalService.return_value
        goals = [MagicMock(), MagicMock()]
        svc.get_user_queryset.return_value = goals
        svc.get_status_summary.side_effect = [
            {"status": "AT_RISK", "percentComplete": 30},
            {"status": "ACHIEVED", "percentComplete": 100},
        ]
        request = make_authenticated_request(self.factory, self.user)
        response = AtRiskGoalsView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["goals"]), 1)

    @patch("analytics.presentation.views.GoalService")
    def test_no_at_risk_goals(self, MockGoalService):
        svc = MockGoalService.return_value
        svc.get_user_queryset.return_value = [MagicMock()]
        svc.get_status_summary.return_value = {"status": "ON_TRACK", "percentComplete": 80}

        request = make_authenticated_request(self.factory, self.user)
        response = AtRiskGoalsView.as_view()(request)

        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["goals"]), 0)

    @patch("analytics.presentation.views.GoalService")
    def test_requires_auth(self, MockGoalService):
        request = self.factory.get("/")
        response = AtRiskGoalsView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GoalCompletionRateViewTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = make_user()

    @patch("analytics.presentation.views.GoalService")
    def test_completion_rate_calculation(self, MockGoalService):
        svc = MockGoalService.return_value
        svc.get_user_queryset.return_value = [MagicMock(), MagicMock()]
        svc.get_status_summary.side_effect = [
            {"status": "ACHIEVED", "percentComplete": 100},
            {"status": "MISSED", "percentComplete": 10},
        ]
        request = make_authenticated_request(self.factory, self.user)
        response = GoalCompletionRateView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertAlmostEqual(response.data["completionRate"], 50.0)

    @patch("analytics.presentation.views.GoalService")
    def test_zero_total_returns_zero(self, MockGoalService):
        MockGoalService.return_value.get_user_queryset.return_value = []

        request = make_authenticated_request(self.factory, self.user)
        response = GoalCompletionRateView.as_view()(request)

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
        request = make_authenticated_request(self.factory, self.user)
        response = GoalCompletionRateView.as_view()(request)

        self.assertAlmostEqual(response.data["completionRate"], 100.0)

    @patch("analytics.presentation.views.GoalService")
    def test_requires_auth(self, MockGoalService):
        request = self.factory.get("/")
        response = GoalCompletionRateView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GoalInsightsViewTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = make_user()

    @patch("analytics.presentation.views.GoalService")
    def test_at_risk_and_missed_insights(self, MockGoalService):
        svc = MockGoalService.return_value
        svc.get_user_queryset.return_value = [MagicMock(), MagicMock(), MagicMock()]
        svc.get_status_summary.side_effect = [
            {"status": "AT_RISK", "percentComplete": 20},
            {"status": "MISSED", "percentComplete": 0},
            {"status": "MISSED", "percentComplete": 5},
        ]
        request = make_authenticated_request(self.factory, self.user)
        response = GoalInsightsView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        insights = response.data["insights"]
        self.assertTrue(any("at risk" in i for i in insights))
        self.assertTrue(any("missed" in i for i in insights))
        self.assertTrue(any("below 50%" in i for i in insights))

    @patch("analytics.presentation.views.GoalService")
    def test_empty_goals_returns_empty_insights(self, MockGoalService):
        MockGoalService.return_value.get_user_queryset.return_value = []

        request = make_authenticated_request(self.factory, self.user)
        response = GoalInsightsView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["insights"], [])

    @patch("analytics.presentation.views.GoalService")
    def test_no_insight_when_all_on_track_above_50(self, MockGoalService):
        """When everything is healthy, insights list should be empty."""
        svc = MockGoalService.return_value
        svc.get_user_queryset.return_value = [MagicMock(), MagicMock()]
        svc.get_status_summary.side_effect = [
            {"status": "ON_TRACK", "percentComplete": 80},
            {"status": "ON_TRACK", "percentComplete": 90},
        ]
        request = make_authenticated_request(self.factory, self.user)
        response = GoalInsightsView.as_view()(request)

        self.assertEqual(response.data["insights"], [])

    @patch("analytics.presentation.views.GoalService")
    def test_below_50_avg_triggers_insight_without_at_risk_or_missed(self, MockGoalService):
        """Average below 50% should produce an insight even with no AT_RISK/MISSED."""
        svc = MockGoalService.return_value
        svc.get_user_queryset.return_value = [MagicMock()]
        svc.get_status_summary.return_value = {"status": "ON_TRACK", "percentComplete": 30}

        request = make_authenticated_request(self.factory, self.user)
        response = GoalInsightsView.as_view()(request)

        self.assertTrue(any("below 50%" in i for i in response.data["insights"]))

    @patch("analytics.presentation.views.GoalService")
    def test_response_includes_at_risk_goals_and_missed_goals_lists(self, MockGoalService):
        svc = MockGoalService.return_value
        g1, g2 = MagicMock(), MagicMock()
        svc.get_user_queryset.return_value = [g1, g2]
        svc.get_status_summary.side_effect = [
            {"status": "AT_RISK", "percentComplete": 10},
            {"status": "MISSED", "percentComplete": 0},
        ]
        request = make_authenticated_request(self.factory, self.user)
        response = GoalInsightsView.as_view()(request)

        self.assertIn("atRiskGoals", response.data)
        self.assertIn("missedGoals", response.data)
        self.assertEqual(len(response.data["atRiskGoals"]), 1)
        self.assertEqual(len(response.data["missedGoals"]), 1)

    @patch("analytics.presentation.views.GoalService")
    def test_requires_auth(self, MockGoalService):
        request = self.factory.get("/")
        response = GoalInsightsView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)