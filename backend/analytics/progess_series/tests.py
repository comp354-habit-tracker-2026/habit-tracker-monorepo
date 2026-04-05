from __future__ import annotations

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from activities.models import Activity
from goals.models import Goal
from analytics.progess_series.service import (
    InvalidGranularityError,
    UnsupportedGoalTypeError,
    generate_progress_series,
)


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
            user=self.user,
            provider="strava",
            distance=2.5,
            calories=200,
        )
        Activity.objects.create(
            activity_type="running",
            duration=40,
            date=date(2026, 3, 2),
            user=self.user,
            provider="strava",
            distance=3.5,
            calories=250,
        )
        Activity.objects.create(
            activity_type="running",
            duration=50,
            date=date(2026, 3, 4),
            user=self.user,
            provider="mapmyrun",
            distance=4.0,
            calories=300,
        )

        activities = Activity.objects.filter(user=self.user).order_by("date")
        result = generate_progress_series(self.goal, activities, "daily")

        self.assertEqual(result["actual_value"], 10.0)
        self.assertEqual(result["percent_complete"], 50.0)
        self.assertEqual(len(result["points"]), 7)
        self.assertEqual(result["points"][0]["value"], 2.5)
        self.assertEqual(result["points"][1]["cumulative"], 6.0)
        self.assertEqual(result["points"][2]["value"], 0.0)

    def test_weekly_series_basic_case(self):
        Activity.objects.create(
            activity_type="running",
            duration=30,
            date=date(2026, 3, 1),
            user=self.user,
            provider="strava",
            distance=2.0,
            calories=200,
        )
        Activity.objects.create(
            activity_type="running",
            duration=30,
            date=date(2026, 3, 2),
            user=self.user,
            provider="strava",
            distance=3.0,
            calories=220,
        )
        Activity.objects.create(
            activity_type="running",
            duration=45,
            date=date(2026, 3, 6),
            user=self.user,
            provider="mapmyrun",
            distance=5.0,
            calories=350,
        )

        activities = Activity.objects.filter(user=self.user).order_by("date")
        result = generate_progress_series(self.goal, activities, "weekly")

        self.assertEqual(result["actual_value"], 10.0)
        self.assertGreaterEqual(len(result["points"]), 1)
        self.assertTrue(result["points"][0]["label"].startswith("week_of_"))

    def test_no_activities_returns_zero_series(self):
        activities = Activity.objects.filter(user=self.user)
        result = generate_progress_series(self.goal, activities, "daily")

        self.assertEqual(result["actual_value"], 0.0)
        self.assertTrue(result["no_data"])
        self.assertEqual(len(result["points"]), 7)

    def test_activities_outside_timeframe_are_ignored(self):
        Activity.objects.create(
            activity_type="running",
            duration=20,
            date=date(2026, 2, 28),
            user=self.user,
            provider="strava",
            distance=100,
            calories=100,
        )
        Activity.objects.create(
            activity_type="running",
            duration=20,
            date=date(2026, 3, 3),
            user=self.user,
            provider="strava",
            distance=4,
            calories=100,
        )
        Activity.objects.create(
            activity_type="running",
            duration=20,
            date=date(2026, 3, 8),
            user=self.user,
            provider="strava",
            distance=100,
            calories=100,
        )

        activities = Activity.objects.filter(user=self.user).order_by("date")
        result = generate_progress_series(self.goal, activities, "daily")

        self.assertEqual(result["actual_value"], 4.0)

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
            user=self.user,
            provider="strava",
            distance=2,
            calories=200,
        )
        Activity.objects.create(
            activity_type="cycling",
            duration=45,
            date=date(2026, 3, 2),
            user=self.user,
            provider="mapmyrun",
            distance=10,
            calories=300,
        )

        activities = Activity.objects.filter(user=self.user).order_by("date")
        result = generate_progress_series(frequency_goal, activities, "daily")

        self.assertEqual(result["actual_value"], 2.0)
        self.assertEqual(result["percent_complete"], 66.67)

    def test_invalid_granularity_raises_error(self):
        activities = Activity.objects.filter(user=self.user).order_by("date")

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
            user=self.user,
            provider="strava",
            distance=2,
            calories=200,
        )

        activities = Activity.objects.filter(user=self.user).order_by("date")

        with self.assertRaises(UnsupportedGoalTypeError):
            generate_progress_series(unsupported_goal, activities, "daily")

    def test_other_users_activities_are_ignored(self):
        Activity.objects.create(
            activity_type="running",
            duration=30,
            date=date(2026, 3, 1),
            user=self.other_user,
            provider="strava",
            distance=25,
            calories=200,
        )

        activities = Activity.objects.all().order_by("date")
        result = generate_progress_series(self.goal, activities, "daily")

        self.assertEqual(result["actual_value"], 0.0)
        self.assertTrue(result["no_data"])
