import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    def _create_user(username="testuser", password="TestPass123!", email="test@test.com"):
        return User.objects.create_user(username=username, password=password, email=email)
    return _create_user


@pytest.fixture
def create_goal(db):
    def _create_goal(user, title="Test Goal"):
        from goals.models import Goal
        return Goal.objects.create(
            user=user,
            title=title,
            description="Test description",
            target_value=100,
            current_value=50,
            goal_type="custom",
            status="active",
            start_date="2026-01-01",
            end_date="2026-12-31",
        )
    return _create_goal


@pytest.mark.django_db
class TestGoalDetailViewing:

    def test_retrieve_goal_success(self, api_client, create_user, create_goal):
        """200 OK - authenticated user retrieves their own goal"""
        user = create_user()
        goal = create_goal(user)
        api_client.force_authenticate(user=user)

        response = api_client.get(f"/api/v1/goals/{goal.id}/")

        assert response.status_code == 200
        assert response.data["id"] == goal.id
        assert response.data["title"] == goal.title
        assert response.data["description"] == goal.description
        assert response.data["goal_type"] == goal.goal_type
        assert response.data["status"] == goal.status
        assert response.data["start_date"] == str(goal.start_date)
        assert response.data["end_date"] == str(goal.end_date)
        assert "created_at" in response.data
        assert "updated_at" in response.data
        assert "progress_percentage" in response.data
        assert float(response.data["progress_percentage"]) == 50.0

    def test_retrieve_other_user_goal_returns_404(self, api_client, create_user, create_goal):
        """404 Not Found - user cannot access another user's goal"""
        owner = create_user(username="owner", email="owner@test.com")
        other = create_user(username="other", email="other@test.com")
        goal = create_goal(owner)
        api_client.force_authenticate(user=other)

        response = api_client.get(f"/api/v1/goals/{goal.id}/")

        assert response.status_code == 404

    def test_retrieve_nonexistent_goal_returns_404(self, api_client, create_user):
        """404 Not Found - goal does not exist"""
        user = create_user()
        api_client.force_authenticate(user=user)

        response = api_client.get("/api/v1/goals/99999/")

        assert response.status_code == 404

    def test_retrieve_goal_unauthenticated_returns_401(self, api_client, create_user, create_goal):
        """401 Unauthorised - no authentication provided"""
        user = create_user()
        goal = create_goal(user)

        response = api_client.get(f"/api/v1/goals/{goal.id}/")

        assert response.status_code == 401