import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from goals.models import Goal

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

@pytest.mark.django_db
class TestGoals:
    def test_create_goal(self, authenticated_client):
        """Test authenticated user can create a goal"""
        data = {
            'title': 'Learn Python',
            'description': 'Complete Python course',
            'target_value': '100.00'
        }
        response = authenticated_client.post('/api/goals/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Goal.objects.filter(title='Learn Python').exists()
        
    def test_list_goals_only_own(self, authenticated_client, create_user):
        """Test user can only see their own goals"""
        # Create another user with a goal
        other_user = create_user(username='otheruser', email='other@example.com')
        Goal.objects.create(
            user=other_user,
            title='Other Goal',
            description='Not visible',
            target_value=50.00
        )
        
        # Create own goal
        Goal.objects.create(
            user=authenticated_client.user,
            title='My Goal',
            description='Should be visible',
            target_value=100.00
        )
        
        response = authenticated_client.get('/api/goals/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == 'My Goal'
        
    def test_user_cannot_access_another_users_goal(self, authenticated_client, create_user):
        """Test user cannot access another user's specific goal"""
        other_user = create_user(username='otheruser', email='other@example.com')
        other_goal = Goal.objects.create(
            user=other_user,
            title='Private Goal',
            description='Should not be accessible',
            target_value=100.00
        )
        
        response = authenticated_client.get(f'/api/goals/{other_goal.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_update_goal(self, authenticated_client):
        """Test user can update their own goal"""
        goal = Goal.objects.create(
            user=authenticated_client.user,
            title='Original Title',
            description='Original',
            target_value=100.00
        )
        
        data = {'title': 'Updated Title'}
        response = authenticated_client.patch(f'/api/goals/{goal.id}/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Title'
