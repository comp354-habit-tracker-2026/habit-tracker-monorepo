# Written by Gorav-K; Claude (Anthropic AI) assisted with fixing tests to pass on GitHub CI.
# Source: Claude Sonnet 4.6 via Claude Code CLI (Anthropic, 2026).
# Required disclosure per COMP 354 AI-generated code traceability policy.
#
# Gorav-K — GitHub: Gorav-K
# Issue #196: Progress series unit tests
# Branch: feature/group-15-health-indicators

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from activities.models import Activity, ConnectedAccount
from goals.models import Goal
from analytics.progess_series.service import (
    InvalidGranularityError,
    ProgressSeriesError,
    UnsupportedGoalTypeError,
    generate_progress_series,
)
from analytics.progess_series.views import GoalProgressSeriesView


User = get_user_model()


class GoalProgressSeriesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="elissar",
            email="elissar@example.com",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            username="other-user",
            email="other@example.com",
            password="testpass123",
        )

        self.strava_account = ConnectedAccount.objects.create(
            user=self.user, provider="strava", external_user_id="strava_user_1"
        )
        self.mapmyrun_account = ConnectedAccount.objects.create(
            user=self.user, provider="mapmyrun", external_user_id="mapmyrun_user_1"
        )
        self.other_strava_account = ConnectedAccount.objects.create(
            user=self.other_user, provider="strava", external_user_id="strava_other_1"
        )

        self.goal = Goal.objects.create(
            title="Run 20 km this week",
            description="Weekly running distance goal",
            target_value=20,
            current_value=0,
            goal_type="distance",
            status="active",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 7),
            user=self.user,
        )

    def test_daily_series_basic_case(self):
        Activity.objects.create(
            activity_type="running",
            duration=30,
            date=date(2026, 3, 1),
            account=self.strava_account,
            distance=2.5,
            calories=200,
        )
        Activity.objects.create(
            activity_type="running",
            duration=40,
            date=date(2026, 3, 2),
            account=self.strava_account,
            distance=3.5,
            calories=250,
        )
        Activity.objects.create(
            activity_type="running",
            duration=50,
            date=date(2026, 3, 4),
            account=self.mapmyrun_account,
            distance=4.0,
            calories=300,
        )

        activities = Activity.objects.filter(account__user=self.user).order_by("date")
        result = generate_progress_series(self.goal, activities, "daily")

        self.assertEqual(result.actual_value, 10.0)
        self.assertEqual(result.percent_complete, 50.0)
        self.assertEqual(len(result.points), 7)
        self.assertEqual(result.points[0].value, 2.5)
        self.assertEqual(result.points[1].cumulative, 6.0)
        self.assertEqual(result.points[2].value, 0.0)

    def test_weekly_series_basic_case(self):
        Activity.objects.create(
            activity_type="running",
            duration=30,
            date=date(2026, 3, 1),
            account=self.strava_account,
            distance=2.0,
            calories=200,
        )
        Activity.objects.create(
            activity_type="running",
            duration=30,
            date=date(2026, 3, 2),
            account=self.strava_account,
            distance=3.0,
            calories=220,
        )
        Activity.objects.create(
            activity_type="running",
            duration=45,
            date=date(2026, 3, 6),
            account=self.mapmyrun_account,
            distance=5.0,
            calories=350,
        )

        activities = Activity.objects.filter(account__user=self.user).order_by("date")
        result = generate_progress_series(self.goal, activities, "weekly")

        self.assertEqual(result.actual_value, 10.0)
        self.assertGreaterEqual(len(result.points), 1)
        self.assertTrue(result.points[0].label.startswith("week_of_"))

    def test_no_activities_returns_zero_series(self):
        activities = Activity.objects.filter(account__user=self.user)
        result = generate_progress_series(self.goal, activities, "daily")

        self.assertEqual(result.actual_value, 0.0)
        self.assertTrue(result.no_data)
        self.assertEqual(len(result.points), 7)

    def test_activities_outside_timeframe_are_ignored(self):
        Activity.objects.create(
            activity_type="running",
            duration=20,
            date=date(2026, 2, 28),
            account=self.strava_account,
            distance=100,
            calories=100,
        )
        Activity.objects.create(
            activity_type="running",
            duration=20,
            date=date(2026, 3, 3),
            account=self.strava_account,
            distance=4,
            calories=100,
        )
        Activity.objects.create(
            activity_type="running",
            duration=20,
            date=date(2026, 3, 8),
            account=self.strava_account,
            distance=100,
            calories=100,
        )

        activities = Activity.objects.filter(account__user=self.user).order_by("date")
        result = generate_progress_series(self.goal, activities, "daily")

        self.assertEqual(result.actual_value, 4.0)

    def test_frequency_goal_counts_activities(self):
        frequency_goal = Goal.objects.create(
            title="Exercise 3 times this week",
            description="Frequency goal",
            target_value=3,
            current_value=0,
            goal_type="frequency",
            status="active",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 7),
            user=self.user,
        )

        Activity.objects.create(
            activity_type="running",
            duration=30,
            date=date(2026, 3, 1),
            account=self.strava_account,
            distance=2,
            calories=200,
        )
        Activity.objects.create(
            activity_type="cycling",
            duration=45,
            date=date(2026, 3, 2),
            account=self.mapmyrun_account,
            distance=10,
            calories=300,
        )

        activities = Activity.objects.filter(account__user=self.user).order_by("date")
        result = generate_progress_series(frequency_goal, activities, "daily")

        self.assertEqual(result.actual_value, 2.0)
        self.assertEqual(result.percent_complete, 66.67)

    def test_invalid_granularity_raises_error(self):
        activities = Activity.objects.filter(account__user=self.user).order_by("date")

        with self.assertRaises(InvalidGranularityError):
            generate_progress_series(self.goal, activities, "monthly")

    def test_unsupported_goal_type_raises_error(self):
        unsupported_goal = Goal.objects.create(
            title="Unsupported goal",
            description="Unsupported metric",
            target_value=3,
            current_value=0,
            goal_type="pace",
            status="active",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 7),
            user=self.user,
        )

        Activity.objects.create(
            activity_type="running",
            duration=30,
            date=date(2026, 3, 1),
            account=self.strava_account,
            distance=2,
            calories=200,
        )

        activities = Activity.objects.filter(account__user=self.user).order_by("date")

        with self.assertRaises(UnsupportedGoalTypeError):
            generate_progress_series(unsupported_goal, activities, "daily")

    def test_other_users_activities_are_ignored(self):
        Activity.objects.create(
            activity_type="running",
            duration=30,
            date=date(2026, 3, 1),
            account=self.other_strava_account,
            distance=25,
            calories=200,
        )

        activities = Activity.objects.all().order_by("date")
        result = generate_progress_series(self.goal, activities, "daily")

        self.assertEqual(result.actual_value, 0.0)
        self.assertTrue(result.no_data)


class GoalProgressSeriesViewTests(TestCase):
    """Unit tests for GoalProgressSeriesView using RequestFactory."""

    def setUp(self):
        self.factory = RequestFactory()
        self.view = GoalProgressSeriesView.as_view()

    def _get(self, goal_id=1, **query_params):
        qs = "&".join(f"{k}={v}" for k, v in query_params.items())
        request = self.factory.get(f"/progress-series/{goal_id}/", query_params)
        return self.view(request, goal_id=goal_id)

    def test_demo_mode_returns_200(self):
        response = self._get(goal_id=1, demo="true")
        self.assertEqual(response.status_code, 200)

    def test_demo_mode_with_invalid_granularity_returns_400(self):
        response = self._get(goal_id=1, demo="true", granularity="monthly")
        self.assertEqual(response.status_code, 400)

    @patch("analytics.progess_series.views.Goal.objects.get")
    @patch("analytics.progess_series.views.Activity.objects.filter")
    @patch("analytics.progess_series.views.generate_progress_series")
    def test_non_demo_success_returns_200(self, mock_gen, mock_filter, mock_get):
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"points": []}
        mock_gen.return_value = mock_result
        mock_filter.return_value.order_by.return_value = []
        response = self._get(goal_id=1)
        self.assertEqual(response.status_code, 200)

    @patch("analytics.progess_series.views.Goal.objects.get", side_effect=Goal.DoesNotExist)
    def test_goal_not_found_returns_404(self, _):
        response = self._get(goal_id=999)
        self.assertEqual(response.status_code, 404)

    @patch("analytics.progess_series.views.Goal.objects.get")
    @patch("analytics.progess_series.views.Activity.objects.filter")
    @patch("analytics.progess_series.views.generate_progress_series", side_effect=InvalidGranularityError("bad"))
    def test_invalid_granularity_returns_400(self, mock_gen, mock_filter, mock_get):
        mock_filter.return_value.order_by.return_value = []
        response = self._get(goal_id=1)
        self.assertEqual(response.status_code, 400)

    @patch("analytics.progess_series.views.Goal.objects.get")
    @patch("analytics.progess_series.views.Activity.objects.filter")
    @patch("analytics.progess_series.views.generate_progress_series", side_effect=UnsupportedGoalTypeError("bad"))
    def test_unsupported_goal_type_returns_400(self, mock_gen, mock_filter, mock_get):
        mock_filter.return_value.order_by.return_value = []
        response = self._get(goal_id=1)
        self.assertEqual(response.status_code, 400)

    @patch("analytics.progess_series.views.Goal.objects.get")
    @patch("analytics.progess_series.views.Activity.objects.filter")
    @patch("analytics.progess_series.views.generate_progress_series", side_effect=ProgressSeriesError("bad"))
    def test_progress_series_error_returns_400(self, mock_gen, mock_filter, mock_get):
        mock_filter.return_value.order_by.return_value = []
        response = self._get(goal_id=1)
        self.assertEqual(response.status_code, 400)

    @patch("analytics.progess_series.views.Goal.objects.get")
    @patch("analytics.progess_series.views.Activity.objects.filter")
    @patch("analytics.progess_series.views.generate_progress_series", side_effect=RuntimeError("unexpected"))
    def test_unexpected_error_returns_500(self, mock_gen, mock_filter, mock_get):
        mock_filter.return_value.order_by.return_value = []
        response = self._get(goal_id=1)
        self.assertEqual(response.status_code, 500)
