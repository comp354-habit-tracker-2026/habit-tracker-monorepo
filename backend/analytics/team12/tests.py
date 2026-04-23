import pytest
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model

from activities.models import Activity
from analytics.team12.services import Team12AnalyticsService
from django.db.models.signals import post_save
from activities.models import Activity
from gamification.signals import evaluate_achievements_on_activity


@pytest.fixture(autouse=True)
def disable_activity_signals():
    post_save.disconnect(evaluate_achievements_on_activity, sender=Activity)
    yield
    post_save.connect(evaluate_achievements_on_activity, sender=Activity)


User = get_user_model()


@pytest.fixture
def create_user(db):
    def _create_user(**kwargs):
        defaults = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)

    return _create_user


@pytest.fixture
def team12_service():
    return Team12AnalyticsService()


@pytest.fixture
def create_activity():
    def _create_activity(user, **kwargs):
        defaults = {
            "activity_type": "Running",
            "duration": 30,
            "date": date.today(),
            "provider": "manual",
        }
        defaults.update(kwargs)
        return Activity.objects.create(user=user, **defaults)

    return _create_activity


@pytest.mark.django_db
class TestTeam12AnalyticsService:
    def test_activity_statistics(self, create_user, create_activity, team12_service):
        user = create_user(username="team12user", email="team12@example.com")
        create_activity(user, duration=45, distance=5.5, calories=300)
        create_activity(user, duration=60, distance=18.2, calories=550)

        result = team12_service.activity_statistics(user)

        assert result["activity_count"] == 2
        assert result["total_distance"] == Decimal("23.7")
        assert result["total_calories"] == 850
        assert result["average_duration"] == pytest.approx(52.5)

    def test_personal_records(self, create_user, create_activity, team12_service):
        user = create_user(username="team12user2", email="team12b@example.com")
        create_activity(user, duration=45, distance=5.5, calories=300)
        create_activity(user, duration=60, distance=18.2, calories=550)

        result = team12_service.personal_records(user)

        assert result["best_distance"] == pytest.approx(18.2)
        assert result["best_duration"] == 60
        assert result["best_calories"] == 550

    def test_activity_type_breakdown(self, create_user, create_activity, team12_service):
        user = create_user(username="team12user3", email="team12c@example.com")
        create_activity(user, activity_type="Running", duration=45, distance=5.5, calories=300)
        create_activity(user, activity_type="Running", duration=60, distance=18.2, calories=550)
        create_activity(user, activity_type="Cycling", duration=30, distance=12.0, calories=200)

        result = team12_service.activity_type_breakdown(user)

        assert len(result) == 2
        running_row = next(row for row in result if row["activity_type"] == "Running")
        cycling_row = next(row for row in result if row["activity_type"] == "Cycling")

        assert running_row["activity_count"] == 2
        assert running_row["total_distance"] == Decimal("23.7")
        assert running_row["total_calories"] == 850
        assert running_row["total_duration"] == 105

        assert cycling_row["activity_count"] == 1
        assert cycling_row["total_distance"] == Decimal("12")
        assert cycling_row["total_calories"] == 200
        assert cycling_row["total_duration"] == 30

    def test_weekly_summary(self, create_user, create_activity, team12_service):
        user = create_user(username="team12user4", email="team12d@example.com")
        create_activity(
            user,
            activity_type="Running",
            duration=30,
            distance=5000,
            date=date(2026, 1, 6),
        )
        create_activity(
            user,
            activity_type="Running",
            duration=60,
            distance=10000,
            date=date(2026, 1, 8),
        )
        create_activity(
            user,
            activity_type="Cycling",
            duration=45,
            distance=15000,
            date=date(2026, 1, 15),
        )

        result = team12_service.weekly_summary(user, "2026-01", "2026-01")

        assert len(result) == 5

        week_1 = next(row for row in result if row["weekStart"] == "2026-01-05")
        week_2 = next(row for row in result if row["weekStart"] == "2026-01-12")
        empty_week = next(row for row in result if row["weekStart"] == "2026-01-19")

        assert week_1["workoutCount"] == 2
        assert week_1["totalDuration"] == 90
        assert week_1["totalDistance"] == pytest.approx(15000.0)
        assert week_1["avgSpeed"] == pytest.approx(6.0)
        assert week_1["avgHR"] is None

        assert week_2["workoutCount"] == 1
        assert week_2["totalDuration"] == 45
        assert week_2["totalDistance"] == pytest.approx(15000.0)
        assert week_2["avgSpeed"] == pytest.approx(3.0)
        assert week_2["avgHR"] is None

        assert empty_week["workoutCount"] == 0
        assert empty_week["totalDuration"] == 0
        assert empty_week["totalDistance"] == 0
        assert empty_week["avgSpeed"] == 0
        assert empty_week["avgHR"] is None

    def test_weekly_summary_with_activity_type_filter(self, create_user, create_activity, team12_service):
        user = create_user(username="team12user5", email="team12e@example.com")
        create_activity(
            user,
            activity_type="Running",
            duration=30,
            distance=5000,
            date=date(2026, 1, 6),
        )
        create_activity(
            user,
            activity_type="Running",
            duration=60,
            distance=10000,
            date=date(2026, 1, 8),
        )
        create_activity(
            user,
            activity_type="Cycling",
            duration=45,
            distance=15000,
            date=date(2026, 1, 15),
        )

        result = team12_service.weekly_summary(user, "2026-01", "2026-01", activity_type="Running")

        week_1 = next(row for row in result if row["weekStart"] == "2026-01-05")
        week_2 = next(row for row in result if row["weekStart"] == "2026-01-12")

        assert week_1["workoutCount"] == 2
        assert week_1["totalDuration"] == 90
        assert week_1["totalDistance"] == pytest.approx(15000.0)
        assert week_1["avgSpeed"] == pytest.approx(6.0)
        assert week_1["avgHR"] is None

        assert week_2["workoutCount"] == 0
        assert week_2["totalDuration"] == 0
        assert week_2["totalDistance"] == 0
        assert week_2["avgSpeed"] == 0
        assert week_2["avgHR"] is None

    def test_weekly_summary_invalid_date_format(self, create_user, team12_service):
        user = create_user(username="team12user6", email="team12f@example.com")

        with pytest.raises(ValueError, match="Invalid date format YYYY-MM"):
            team12_service.weekly_summary(user, "2026/01", "2026-01")

    def test_weekly_summary_invalid_date_range(self, create_user, team12_service):
        user = create_user(username="team12user7", email="team12g@example.com")

        with pytest.raises(ValueError, match="'to' must be >= 'from'"):
            team12_service.weekly_summary(user, "2026-03", "2026-01")

    def test_monthly_summary_basic(self, create_user, create_activity, team12_service):
        user = create_user(username="team12user12", email="team12l@example.com")

        # Two activities in January 2026
        create_activity(
            user,
            activity_type="Running",
            duration=30,
            distance=5000,
            date=date(2026, 1, 6),
        )
        create_activity(
            user,
            activity_type="Running",
            duration=60,
            distance=10000,
            date=date(2026, 1, 8),
        )

        # One activity in February 2026
        create_activity(
            user,
            activity_type="Cycling",
            duration=45,
            distance=15000,
            date=date(2026, 2, 15),
        )

        result = team12_service.monthly_summary(user, "2026-01", "2026-02")

        assert len(result) == 2

        jan = next(row for row in result if row["monthStart"] == "2026-01-01")
        feb = next(row for row in result if row["monthStart"] == "2026-02-01")

        assert jan["workoutCount"] == 2
        assert jan["totalDuration"] == 90
        assert jan["totalDistance"] == pytest.approx(15000.0)
        assert jan["avgSpeed"] == pytest.approx(6.0)
        assert jan["avgHR"] is None

        assert feb["workoutCount"] == 1
        assert feb["totalDuration"] == 45
        assert feb["totalDistance"] == pytest.approx(15000.0)
        assert feb["avgSpeed"] == pytest.approx(3.0)
        assert feb["avgHR"] is None

    def test_monthly_summary_with_activity_type_filter(
            self, create_user, create_activity, team12_service
    ):
        user = create_user(username="team12user13", email="team12m@example.com")

        create_activity(
            user,
            activity_type="Running",
            duration=30,
            distance=5000,
            date=date(2026, 1, 6),
        )
        create_activity(
            user,
            activity_type="Running",
            duration=60,
            distance=10000,
            date=date(2026, 1, 8),
        )
        create_activity(
            user,
            activity_type="Cycling",
            duration=45,
            distance=15000,
            date=date(2026, 2, 15),
        )

        result = team12_service.monthly_summary(
            user, "2026-01", "2026-02", activity_type="Running"
        )

        jan = next(row for row in result if row["monthStart"] == "2026-01-01")
        feb = next(row for row in result if row["monthStart"] == "2026-02-01")

        assert jan["workoutCount"] == 2
        assert jan["totalDuration"] == 90
        assert jan["totalDistance"] == pytest.approx(15000.0)
        assert jan["avgSpeed"] == pytest.approx(6.0)
        assert jan["avgHR"] is None

        # February is in range but filtered out by activity_type
        assert feb["workoutCount"] == 0
        assert feb["totalDuration"] == 0
        assert feb["totalDistance"] == 0
        assert feb["avgSpeed"] == 0
        assert feb["avgHR"] is None

    def test_monthly_summary_invalid_date_format(self, create_user, team12_service):
        user = create_user(username="team12user14", email="team12n@example.com")

        with pytest.raises(ValueError, match="Invalid date format YYYY-MM"):
            team12_service.monthly_summary(user, "2026/01", "2026-01")

    def test_monthly_summary_invalid_date_range(self, create_user, team12_service):
        user = create_user(username="team12user15", email="team12o@example.com")

        with pytest.raises(ValueError, match="'to' must be >= 'from'"):
            team12_service.monthly_summary(user, "2026-03", "2026-01")

    def test_activity_streaks_no_activities(self, create_user, team12_service):
        user = create_user(username="team12user8", email="team12h@example.com")

        result = team12_service.activity_streaks(user)

        assert result["current_streak"] == 0
        assert result["longest_streak"] == 0

    def test_activity_streaks_multiple_same_day_count_once(self, create_user, create_activity, team12_service):
        user = create_user(username="team12user9", email="team12i@example.com")
        today = date.today()

        create_activity(user, date=today, duration=20)
        create_activity(user, date=today, duration=40)
        create_activity(user, date=today, duration=60)

        result = team12_service.activity_streaks(user)

        assert result["current_streak"] == 1
        assert result["longest_streak"] == 1

    def test_activity_streaks_consecutive_days(self, create_user, create_activity, team12_service):
        user = create_user(username="team12user10", email="team12j@example.com")
        today = date.today()

        create_activity(user, date=today - timedelta(days=2), duration=30)
        create_activity(user, date=today - timedelta(days=1), duration=30)
        create_activity(user, date=today, duration=30)

        result = team12_service.activity_streaks(user)

        assert result["current_streak"] == 3
        assert result["longest_streak"] == 3

    def test_activity_streaks_broken_current_but_longer_historical(self, create_user, create_activity, team12_service):
        user = create_user(username="team12user11", email="team12k@example.com")
        today = date.today()

        create_activity(user, date=today - timedelta(days=6), duration=30)
        create_activity(user, date=today - timedelta(days=5), duration=30)
        create_activity(user, date=today - timedelta(days=4), duration=30)
        create_activity(user, date=today - timedelta(days=1), duration=30)

        result = team12_service.activity_streaks(user)

        assert result["current_streak"] == 0
        assert result["longest_streak"] == 3

    def test_personal_record_for_habit(self, create_user, create_activity, team12_service):
        user = create_user()

        create_activity(user, duration=30, activity_type="running")
        create_activity(user, duration=60, activity_type="running")
        create_activity(user, duration=50, activity_type="running")

        result = team12_service.personal_record_for_habit(
            user=user,
            activity_type="running",
            metric_type="DURATION"
        )

        assert result["currentPersonalBest"] == 60
        assert result["previousBest"] == 50
        assert result["improved"] is True

    # #Made with LLM
    # def test_personal_record_custom(self, create_user, create_activity, team12_service):
    #     user = create_user()

    #     # Just create activities with duration (the simplest valid field)
    #     create_activity(user, duration=30, activity_type="running")
    #     create_activity(user, duration=60, activity_type="running")

    #     # Basic smoke test - just verify it doesn't crash
    #     try:
    #         result = team12_service.personal_record_for_habit(
    #             user=user,
    #             activity_type="running",
    #             metric_type="CUSTOM"
    #         )
    #         # Test passes if the method executes
    #         assert True
    #     except Exception:
    #         pytest.fail("Method should not raise an exception")