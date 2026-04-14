import pytest
from activities.data.repositories import ActivityRepository
from activities.models import Activity
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestActivityRepository:
    def test_get_by_id_returns_activity(self):
        # ARRANGE
        user = User.objects.create_user(username='test', password='test')
        activity = Activity.objects.create(
            user=user,
            activity_type='Running',
            duration=30,
            date='2024-01-01',
            provider='manual'
        )
        repo = ActivityRepository()

        # ACT
        result = repo.get_by_id(activity.id)

        # ASSERT
        assert result == activity

    def test_get_by_id_returns_none_when_not_found(self):
        # ARRANGE
        repo = ActivityRepository()

        # ACT
        result = repo.get_by_id(99999)

        # ASSERT
        assert result is None