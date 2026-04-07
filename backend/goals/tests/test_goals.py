import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from goals.business import GoalService
from goals.models import Goal
from datetime import date, timedelta

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    def _create_user(**kwargs):
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
def create_goal():
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
        return Goal.objects.create(user=user, **defaults)
    return _create_goal

@pytest.mark.django_db
class TestGoals:
    def test_create_goal_with_all_fields(self, authenticated_client):
        """Test creating a goal with all new fields"""
        data = {
            'title': 'Run 100km',
            'description': 'Run 100km in a month',
            'target_value': '100.00',
            'goal_type': 'distance',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=30)).isoformat()
        }
        response = authenticated_client.post('/api/v1/goals/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Goal.objects.filter(title='Run 100km').exists()
        
        goal = Goal.objects.get(title='Run 100km')
        assert goal.goal_type == 'distance'
        assert goal.status == 'active'  # Default status
        assert goal.current_value == 0  # Default current_value
        
    def test_list_goals_with_pagination(self, authenticated_client, create_goal):
        """Test goals list is paginated"""
        # Create 25 goals
        for i in range(25):
            create_goal(authenticated_client.user, title=f'Goal {i}')
            
        response = authenticated_client.get('/api/v1/goals/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert 'count' in response.data
        assert 'next' in response.data
        assert len(response.data['results']) == 20  # Default page size
        
    def test_goal_progress_percentage(self, authenticated_client, create_goal):
        """Test goal progress percentage calculation"""
        goal = create_goal(
            authenticated_client.user,
            target_value=100,
            current_value=25
        )
        assert goal.progress_percentage == 25
        
        goal.current_value = 150
        assert goal.progress_percentage == 100  # Capped at 100%
        
    def test_list_goals_only_own(self, authenticated_client, create_user, create_goal):
        """Test user can only see their own goals"""
        other_user = create_user(username='otheruser', email='other@example.com')
        create_goal(other_user, title='Other Goal')
        create_goal(authenticated_client.user, title='My Goal')
        
        response = authenticated_client.get('/api/v1/goals/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['title'] == 'My Goal'
        
    def test_user_cannot_access_another_users_goal(self, authenticated_client, create_user, create_goal):
        """Test user cannot access another user's specific goal"""
        other_user = create_user(username='otheruser', email='other@example.com')
        other_goal = create_goal(other_user, title='Private Goal')
        
        response = authenticated_client.get(f'/api/v1/goals/{other_goal.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_update_goal_status(self, authenticated_client, create_goal):
        """Test updating goal status"""
        goal = create_goal(authenticated_client.user)
        
        data = {
            'status': 'completed',
            'current_value': '100.00'
        }
        response = authenticated_client.patch(f'/api/v1/goals/{goal.id}/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'completed'
        assert float(response.data['current_value']) == 100.00
        
    def test_filter_goals_by_status(self, authenticated_client, create_goal):
        """Test filtering goals by status"""
        create_goal(authenticated_client.user, title='Active Goal', status='active')
        create_goal(authenticated_client.user, title='Completed Goal', status='completed')
        create_goal(authenticated_client.user, title='Paused Goal', status='paused')
        
        # Would need to implement filtering in the viewset
        # This is a placeholder for when filtering is added
        response = authenticated_client.get('/api/v1/goals/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3

    @pytest.mark.parametrize(
        "actual,target,deadline_offset,expected_percent,expected_status",
        [
            (0, 100, 7, 0.00, "AT_RISK"),
            (80, 100, 7, 80.00, "ON_TRACK"),
            (100, 100, 7, 100.00, "ACHIEVED"),
            (150, 100, 7, 150.00, "ACHIEVED"),
            (60, 100, -1, 60.00, "MISSED"),
            (0, 0, 7, 100.00, "ACHIEVED"),
        ],
    )
    def test_goal_status_summary_acceptance_matrix(
        self,
        authenticated_client,
        create_goal,
        actual,
        target,
        deadline_offset,
        expected_percent,
        expected_status,
    ):
        goal = create_goal(
            authenticated_client.user,
            target_value=target,
            current_value=actual,
            end_date=date.today() + timedelta(days=deadline_offset),
        )

        response = authenticated_client.get(f'/api/v1/goals/{goal.id}/status/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['goalId'] == goal.id
        assert response.data['status'] == expected_status
        assert response.data['percentComplete'] == pytest.approx(expected_percent, abs=0.01)
        assert 'evaluatedAt' in response.data

    def test_goal_status_summary_metrics_failure_returns_partial_response(
        self,
        authenticated_client,
        create_goal,
        monkeypatch,
    ):
        goal = create_goal(authenticated_client.user, target_value=100, current_value=20)

        def _raise_metrics_failure(*args, **kwargs):
            raise RuntimeError("metrics unavailable")

        monkeypatch.setattr(GoalService, 'get_actual_value', _raise_metrics_failure)

        response = authenticated_client.get(f'/api/v1/goals/{goal.id}/status/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['percentComplete'] == pytest.approx(0.00, abs=0.01)
        assert response.data['status'] == 'AT_RISK'
        assert 'notes' in response.data
        assert 'Actual value unavailable' in response.data['notes']

    def test_goal_status_summary_negative_actual_clamped(
        self,
        authenticated_client,
        create_goal,
    ):
        goal = create_goal(
            authenticated_client.user,
            target_value=100,
            current_value=-25,
            end_date=date.today() + timedelta(days=10),
        )

        response = authenticated_client.get(f'/api/v1/goals/{goal.id}/status/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['actualValue'] == pytest.approx(0.00, abs=0.01)
        assert response.data['percentComplete'] == pytest.approx(0.00, abs=0.01)
        assert response.data['status'] == 'AT_RISK'
        assert 'clamped to 0' in response.data.get('notes', '')

    def test_goal_status_summary_now_equals_deadline_not_missed(
        self,
        authenticated_client,
        create_goal,
    ):
        goal = create_goal(
            authenticated_client.user,
            target_value=100,
            current_value=60,
            end_date=date.today(),
        )

        response = authenticated_client.get(f'/api/v1/goals/{goal.id}/status/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'AT_RISK'

    def test_goal_status_summary_goal_not_found_returns_error_code(self, authenticated_client):
        response = authenticated_client.get('/api/v1/goals/999999/status/')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['errorCode'] == 'GOAL_NOT_FOUND'

    def test_goal_status_summary_invalid_target_returns_422(self, authenticated_client, create_goal):
        goal = create_goal(authenticated_client.user, target_value=-10, current_value=5)

        response = authenticated_client.get(f'/api/v1/goals/{goal.id}/status/')

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.data['errorCode'] == 'GOAL_INVALID'
