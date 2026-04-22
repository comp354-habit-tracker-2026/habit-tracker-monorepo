# Written by Elissar Fadel; Claude (Anthropic AI) assisted with fixing tests to pass on GitHub CI.
# Source: Claude Sonnet 4.6 via Claude Code CLI (Anthropic, 2026).
# Required disclosure per COMP 354 AI-generated code traceability policy.
#
# Elissar Fadel — GitHub: elissarff
# Issue #196: Progress series unit tests
# Branch: feature/group-15-health-indicators
from __future__ import annotations
from rest_framework.test import APIRequestFactory, force_authenticate

import json
from unittest.mock import MagicMock, patch

from django.test import RequestFactory, SimpleTestCase

from analytics.progress_series.service import (
    InvalidGranularityError,
    ProgressSeriesError,
    UnsupportedGoalTypeError,
)
from analytics.views import GoalProgressSeriesView
from analytics.progress_series.models import ProgressPoint

def _mock_result_with_points(count=65):
    mock_result = MagicMock()
    mock_result.goal_id = 1
    mock_result.goal_title = "Mock Goal"
    mock_result.goal_type = "distance"
    mock_result.granularity = "daily"
    mock_result.start_date = "2026-03-01"
    mock_result.end_date = "2026-05-04"
    mock_result.target_value = 100.0
    mock_result.actual_value = 65.0
    mock_result.percent_complete = 65.0
    mock_result.no_data = False
    mock_result.pagination = None
    mock_result.points = [
        ProgressPoint(
            label=f"2026-03-{(i % 30) + 1:02d}",
            value=1.0,
            cumulative=float(i + 1),
        )
        for i in range(count)
    ]

    mock_result.to_dict.side_effect = lambda: {
        "goal_id": mock_result.goal_id,
        "goal_title": mock_result.goal_title,
        "goal_type": mock_result.goal_type,
        "granularity": mock_result.granularity,
        "start_date": mock_result.start_date,
        "end_date": mock_result.end_date,
        "target_value": mock_result.target_value,
        "actual_value": mock_result.actual_value,
        "percent_complete": mock_result.percent_complete,
        "no_data": mock_result.no_data,
        "pagination": (
            mock_result.pagination.to_dict()
            if mock_result.pagination is not None
            else None
        ),
        "points": [
            {
                "label": p.label,
                "value": p.value,
                "cumulative": p.cumulative,
            }
            for p in mock_result.points
        ],
    }

    return mock_result

class GoalProgressSeriesViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = GoalProgressSeriesView.as_view()
        self.user = MagicMock()
        self.user.is_authenticated = True

    def _get(self, goal_id=1, **query_params):
        request = self.factory.get(f"/progress-series/{goal_id}/", data=query_params)
        force_authenticate(request, user=self.user)
        return self.view(request, goal_id=goal_id)
    def test_demo_mode_returns_200(self):
        response = self._get(goal_id=1, demo="true")
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertIn("goal_id", payload)
        self.assertIn("goal_title", payload)
        self.assertIn("goal_type", payload)
        self.assertIn("granularity", payload)
        self.assertIn("start_date", payload)
        self.assertIn("end_date", payload)
        self.assertIn("target_value", payload)
        self.assertIn("actual_value", payload)
        self.assertIn("percent_complete", payload)
        self.assertIn("no_data", payload)
        self.assertIn("points", payload)
        self.assertIsInstance(payload["points"], list)

    def test_demo_mode_defaults_to_daily(self):
        response = self._get(goal_id=1, demo="true")
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertEqual(payload["granularity"], "daily")

    def test_demo_mode_daily_returns_points(self):
        response = self._get(goal_id=1, demo="true", granularity="daily")
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertTrue(len(payload["points"]) > 0)

    def test_demo_mode_weekly_returns_points(self):
        response = self._get(goal_id=1, demo="true", granularity="weekly")
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertTrue(len(payload["points"]) > 0)
        self.assertTrue(payload["points"][0]["label"].startswith("week_of_"))

    def test_demo_mode_invalid_granularity_returns_400(self):
        response = self._get(goal_id=1, demo="true", granularity="monthly")
        self.assertEqual(response.status_code, 400)

        payload = json.loads(response.content)
        self.assertEqual(payload["error"], "Invalid granularity parameter.")

    @patch("analytics.presentation.views.Goal.objects.get")
    @patch("analytics.presentation.views.Activity.objects.filter")
    @patch("analytics.presentation.views.generate_progress_series")
    def test_success_returns_200(self, mock_generate, mock_filter, mock_get):
        mock_goal = MagicMock()
        mock_goal.user = MagicMock()
        mock_goal.start_date = "2026-03-01"
        mock_goal.end_date = "2026-03-07"
        mock_get.return_value = mock_goal

        mock_filter.return_value.order_by.return_value = []

        mock_result = MagicMock()
        mock_result.to_dict.return_value = {
            "goal_id": 1,
            "goal_title": "Mock Goal",
            "goal_type": "distance",
            "granularity": "daily",
            "start_date": "2026-03-01",
            "end_date": "2026-03-07",
            "target_value": 20.0,
            "actual_value": 10.0,
            "percent_complete": 50.0,
            "no_data": False,
            "points": [],
        }
        mock_generate.return_value = mock_result

        response = self._get(goal_id=1)
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertEqual(payload["goal_id"], 1)
        self.assertEqual(payload["goal_title"], "Mock Goal")

    @patch("analytics.presentation.views.Goal.objects.get")
    def test_goal_not_found_returns_404(self, mock_get):
        from goals.models import Goal

        mock_get.side_effect = Goal.DoesNotExist

        response = self._get(goal_id=999)
        self.assertEqual(response.status_code, 404)

        payload = json.loads(response.content)
        self.assertEqual(payload["error"], "Goal not found.")
        self.assertIn("hint", payload)

    @patch("analytics.presentation.views.Goal.objects.get")
    @patch("analytics.presentation.views.Activity.objects.filter")
    @patch(
        "analytics.presentation.views.generate_progress_series",
        side_effect=InvalidGranularityError("bad granularity"),
    )
    def test_invalid_granularity_returns_400(self, mock_generate, mock_filter, mock_get):
        mock_goal = MagicMock()
        mock_goal.user = MagicMock()
        mock_goal.start_date = "2026-03-01"
        mock_goal.end_date = "2026-03-07"
        mock_get.return_value = mock_goal

        mock_filter.return_value.order_by.return_value = []

        response = self._get(goal_id=1)
        self.assertEqual(response.status_code, 400)

        payload = json.loads(response.content)
        self.assertEqual(payload["error"], "Invalid granularity parameter.")

    @patch("analytics.presentation.views.Goal.objects.get")
    @patch("analytics.presentation.views.Activity.objects.filter")
    @patch(
        "analytics.presentation.views.generate_progress_series",
        side_effect=UnsupportedGoalTypeError("bad goal type"),
    )
    def test_unsupported_goal_type_returns_400(self, mock_generate, mock_filter, mock_get):
        mock_goal = MagicMock()
        mock_goal.user = MagicMock()
        mock_goal.start_date = "2026-03-01"
        mock_goal.end_date = "2026-03-07"
        mock_get.return_value = mock_goal

        mock_filter.return_value.order_by.return_value = []

        response = self._get(goal_id=1)
        self.assertEqual(response.status_code, 400)

        payload = json.loads(response.content)
        self.assertEqual(payload["error"], "Unsupported goal type for progress series.")

    @patch("analytics.presentation.views.Goal.objects.get")
    @patch("analytics.presentation.views.Activity.objects.filter")
    @patch(
        "analytics.presentation.views.generate_progress_series",
        side_effect=ProgressSeriesError("cannot compute"),
    )
    def test_progress_series_error_returns_400(self, mock_generate, mock_filter, mock_get):
        mock_goal = MagicMock()
        mock_goal.user = MagicMock()
        mock_goal.start_date = "2026-03-01"
        mock_goal.end_date = "2026-03-07"
        mock_get.return_value = mock_goal

        mock_filter.return_value.order_by.return_value = []

        response = self._get(goal_id=1)
        self.assertEqual(response.status_code, 400)

        payload = json.loads(response.content)
        self.assertEqual(payload["error"], "Unable to compute progress series.")

    @patch("analytics.presentation.views.Goal.objects.get")
    @patch("analytics.presentation.views.Activity.objects.filter")
    @patch(
        "analytics.presentation.views.generate_progress_series",
        side_effect=RuntimeError("unexpected failure"),
    )
    def test_unexpected_error_returns_500(self, mock_generate, mock_filter, mock_get):
        mock_goal = MagicMock()
        mock_goal.user = MagicMock()
        mock_goal.start_date = "2026-03-01"
        mock_goal.end_date = "2026-03-07"
        mock_get.return_value = mock_goal

        mock_filter.return_value.order_by.return_value = []

        response = self._get(goal_id=1)
        self.assertEqual(response.status_code, 500)

        payload = json.loads(response.content)
        self.assertEqual(payload["error"], "Unexpected server error.")

    @patch("analytics.presentation.views.Goal.objects.get")
    @patch("analytics.presentation.views.Activity.objects.filter")
    @patch("analytics.presentation.views.generate_progress_series")
    def test_default_pagination_applies_page_1_size_30(self, mock_generate, mock_filter, mock_get):
        mock_goal = MagicMock()
        mock_goal.user = MagicMock()
        mock_goal.user_id = 1
        mock_goal.start_date = "2026-03-01"
        mock_goal.end_date = "2026-05-04"
        mock_get.return_value = mock_goal
        mock_filter.return_value.order_by.return_value = []

        mock_generate.return_value = _mock_result_with_points(65)

        response = self._get(goal_id=1)
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertEqual(len(payload["points"]), 30)
        self.assertEqual(payload["pagination"]["page"], 1)
        self.assertEqual(payload["pagination"]["page_size"], 30)
        self.assertEqual(payload["pagination"]["total_items"], 65)
        self.assertEqual(payload["pagination"]["total_pages"], 3)
        self.assertTrue(payload["pagination"]["has_next"])
        self.assertFalse(payload["pagination"]["has_previous"])
    
    @patch("analytics.presentation.views.Goal.objects.get")
    @patch("analytics.presentation.views.Activity.objects.filter")
    @patch("analytics.presentation.views.generate_progress_series")
    def test_custom_page_and_page_size_return_expected_slice(self, mock_generate, mock_filter, mock_get):
        mock_goal = MagicMock()
        mock_goal.user = MagicMock()
        mock_goal.user_id = 1
        mock_goal.start_date = "2026-03-01"
        mock_goal.end_date = "2026-05-04"
        mock_get.return_value = mock_goal
        mock_filter.return_value.order_by.return_value = []

        mock_generate.return_value = _mock_result_with_points(65)

        response = self._get(goal_id=1, page=2, page_size=10)
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertEqual(len(payload["points"]), 10)
        self.assertEqual(payload["pagination"]["page"], 2)
        self.assertEqual(payload["pagination"]["page_size"], 10)
        self.assertEqual(payload["pagination"]["total_items"], 65)
        self.assertEqual(payload["pagination"]["total_pages"], 7)
        self.assertTrue(payload["pagination"]["has_next"])
        self.assertTrue(payload["pagination"]["has_previous"])

        # second page should start from original index 10
        self.assertEqual(payload["points"][0]["cumulative"], 11.0)
    
    @patch("analytics.presentation.views.Goal.objects.get")
    @patch("analytics.presentation.views.Activity.objects.filter")
    @patch("analytics.presentation.views.generate_progress_series")
    def test_page_size_is_capped_to_max_page_size(self, mock_generate, mock_filter, mock_get):
        mock_goal = MagicMock()
        mock_goal.user = MagicMock()
        mock_goal.user_id = 1
        mock_goal.start_date = "2026-03-01"
        mock_goal.end_date = "2026-08-31"
        mock_get.return_value = mock_goal
        mock_filter.return_value.order_by.return_value = []

        mock_generate.return_value = _mock_result_with_points(150)

        response = self._get(goal_id=1, page=1, page_size=1000)
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertEqual(len(payload["points"]), 100)
        self.assertEqual(payload["pagination"]["page_size"], 100)
        self.assertEqual(payload["pagination"]["total_items"], 150)
        self.assertEqual(payload["pagination"]["total_pages"], 2)

    @patch("analytics.presentation.views.Goal.objects.get")
    @patch("analytics.presentation.views.Activity.objects.filter")
    @patch("analytics.presentation.views.generate_progress_series")
    def test_invalid_page_returns_400(self, mock_generate, mock_filter, mock_get):
        mock_goal = MagicMock()
        mock_goal.user = MagicMock()
        mock_goal.user_id = 1
        mock_goal.start_date = "2026-03-01"
        mock_goal.end_date = "2026-05-04"
        mock_get.return_value = mock_goal
        mock_filter.return_value.order_by.return_value = []

        mock_generate.return_value = _mock_result_with_points(20)

        response = self._get(goal_id=1, page=0, page_size=10)
        self.assertEqual(response.status_code, 400)

        payload = json.loads(response.content)
        self.assertEqual(payload["error"], "Page must be >= 1.")

    @patch("analytics.presentation.views.Goal.objects.get")
    @patch("analytics.presentation.views.Activity.objects.filter")
    @patch("analytics.presentation.views.generate_progress_series")
    def test_invalid_page_size_returns_400(self, mock_generate, mock_filter, mock_get):
        mock_goal = MagicMock()
        mock_goal.user = MagicMock()
        mock_goal.user_id = 1
        mock_goal.start_date = "2026-03-01"
        mock_goal.end_date = "2026-05-04"
        mock_get.return_value = mock_goal
        mock_filter.return_value.order_by.return_value = []

        mock_generate.return_value = _mock_result_with_points(20)

        response = self._get(goal_id=1, page=1, page_size=0)
        self.assertEqual(response.status_code, 400)

        payload = json.loads(response.content)
        self.assertEqual(payload["error"], "Page size must be >= 1.")

    @patch("analytics.presentation.views.Goal.objects.get")
    @patch("analytics.presentation.views.Activity.objects.filter")
    @patch("analytics.presentation.views.generate_progress_series")
    def test_page_beyond_total_pages_returns_empty_points(self, mock_generate, mock_filter, mock_get):
        mock_goal = MagicMock()
        mock_goal.user = MagicMock()
        mock_goal.user_id = 1
        mock_goal.start_date = "2026-03-01"
        mock_goal.end_date = "2026-05-04"
        mock_get.return_value = mock_goal
        mock_filter.return_value.order_by.return_value = []

        mock_generate.return_value = _mock_result_with_points(15)

        response = self._get(goal_id=1, page=5, page_size=10)
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content)
        self.assertEqual(payload["points"], [])
        self.assertEqual(payload["pagination"]["page"], 5)
        self.assertEqual(payload["pagination"]["page_size"], 10)
        self.assertEqual(payload["pagination"]["total_items"], 15)
        self.assertEqual(payload["pagination"]["total_pages"], 2)
        self.assertFalse(payload["pagination"]["has_next"])
        self.assertTrue(payload["pagination"]["has_previous"])