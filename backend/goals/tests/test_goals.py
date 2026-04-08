import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from goals.models import Goal, ProgressLog
from activities.models import Activity, ConnectedAccount
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
def admin_client(api_client, create_user):
    admin = create_user(
        username='adminuser',
        email='admin@test.com',
        is_staff=True,
        is_superuser=True,
    )
    refresh = RefreshToken.for_user(admin)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    api_client.user = admin
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

    def test_progress_log_links_activity_to_goal(self, authenticated_client, create_goal):
        """Test that a ProgressLog entry correctly links an activity to a goal"""
        goal = create_goal(authenticated_client.user)
        account = ConnectedAccount.objects.create(
            user=authenticated_client.user,
            provider='strava',
            external_user_id='pl_ext_123',
        )
        activity = Activity.objects.create(
            account=account,
            activity_type='Running',
            duration=30,
            date=date.today(),
        )
        log = ProgressLog.objects.create(goal=goal, activity=activity)

        assert log.goal == goal
        assert log.activity == activity
        assert str(log) == f"Activity {activity.id} → Goal {goal.id}"

    def test_progress_log_prevents_duplicates(self, authenticated_client, create_goal):
        """Test that the same activity cannot be linked to the same goal twice"""
        from django.db import IntegrityError

        goal = create_goal(authenticated_client.user)
        account = ConnectedAccount.objects.create(
            user=authenticated_client.user,
            provider='strava',
            external_user_id='pl_ext_456',
        )
        activity = Activity.objects.create(
            account=account,
            activity_type='Running',
            duration=30,
            date=date.today(),
        )
        ProgressLog.objects.create(goal=goal, activity=activity)

        with pytest.raises(IntegrityError):
            ProgressLog.objects.create(goal=goal, activity=activity)

    def test_admin_can_list_all_users_goals(self, admin_client, create_user, create_goal):
        """Test admin can list goals from all users."""
        user_one = create_user(username='goalsuser1', email='goals1@example.com')
        user_two = create_user(username='goalsuser2', email='goals2@example.com')
        create_goal(user_one, title='User 1 Goal')
        create_goal(user_two, title='User 2 Goal')

        response = admin_client.get('/api/v1/goals/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_admin_can_delete_other_users_goal(self, admin_client, create_user, create_goal):
        """Test admin can delete another user's goal."""
        regular_user = create_user(username='goalsregular', email='goalsregular@example.com')
        goal = create_goal(regular_user, title='Delete Goal')

        response = admin_client.delete(f'/api/v1/goals/{goal.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Goal.objects.filter(id=goal.id).exists()

