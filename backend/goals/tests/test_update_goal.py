import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from goals.models import Goal
from datetime import date, timedelta

User = None  

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user(db):
    def _create_user(**kwargs):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        defaults = {
            'username': 'testuser',
            'email': 'test@test.com',
            'password': 'TestPass123!'
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)
    return _create_user

@pytest.fixture
def authenticated_client(api_client, create_user):
    user = create_user()
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    api_client.user = user
    return api_client

@pytest.fixture
def create_goal(db):
    def _create_goal(user, **kwargs):
        defaults = {
            'title': 'Test Goal',
            'description': 'Test Description',
            'target_value': 100.00,
            'current_value': 0.00,
            'goal_type': 'distance',
            'status': 'active',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=30)
        }
        defaults.update(kwargs)
        return Goal.objects.create(user=user, **defaults) # pylint: disable=no-member
    return _create_goal

@pytest.mark.django_db
class TestUpdateGoal:

    def test_update_goal_returns_200(self, authenticated_client, create_goal):
        """Returns 200 OK when updating own goal successfully."""
        goal = create_goal(authenticated_client.user)
        data = {'title': 'Updated Title'}
        response = authenticated_client.put(f'/api/v1/goals/{goal.id}/', data)
        assert response.status_code == 200
        assert response.data['title'] == 'Updated Title'

    def test_update_goal_success_message(self, authenticated_client, create_goal):
        """Response body contains updated fields."""
        goal = create_goal(authenticated_client.user)
        data = {'description': 'Updated Description'}
        response = authenticated_client.put(f'/api/v1/goals/{goal.id}/', data)
        assert response.data['description'] == 'Updated Description'

    def test_update_goal_in_db(self, authenticated_client, create_goal):
        """Goal is updated in the database after update."""
        goal = create_goal(authenticated_client.user)
        data = {'current_value': 50.0}
        authenticated_client.put(f'/api/v1/goals/{goal.id}/', data)
        goal.refresh_from_db()
        assert goal.current_value == 50.0

    def test_update_nonexistent_goal_returns_404(self, authenticated_client):
        """Returns 404 when goal ID does not exist."""
        data = {'title': 'Does not matter'}
        response = authenticated_client.put('/api/v1/goals/99999/', data)
        assert response.status_code == 404

    def test_update_other_users_goal_returns_403(self, authenticated_client, create_goal):
        """Returns 403 when attempting to update another user's goal."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@test.com',
            password='TestPass123!'
        )
        other_goal = create_goal(other_user)
        data = {'title': 'Hacked'}
        response = authenticated_client.put(f'/api/v1/goals/{other_goal.id}/', data)
        assert response.status_code == 403

    def test_update_invalid_id_format_returns_400(self, authenticated_client):
        """Returns 400 when goal ID is not a valid integer."""
        data = {'title': 'Invalid'}
        response = authenticated_client.put('/api/v1/goals/abc/', data)
        assert response.status_code == 400

    def test_update_unauthenticated_returns_401(self, api_client, create_goal):
        """Unauthenticated requests are rejected with 401."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            username='tempuser',
            email='temp@test.com',
            password='TestPass123!'
        )
        goal = create_goal(user)
        data = {'title': 'Should not update'}
        response = api_client.put(f'/api/v1/goals/{goal.id}/', data)
        assert response.status_code == 401
