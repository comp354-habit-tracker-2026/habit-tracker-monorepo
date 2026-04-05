import pytest
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model

from activities.models import Activity
from analytics.team12.services import Team12AnalyticsService


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
