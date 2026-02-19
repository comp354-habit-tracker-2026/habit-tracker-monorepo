import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from activities.models import Activity
from datetime import date

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
class TestActivities:
    def test_create_activity(self, authenticated_client):
        """Test authenticated user can create an activity"""
        data = {
            'activity_type': 'Running',
            'duration': 30,
            'date': date.today().isoformat()
        }
        response = authenticated_client.post('/api/activities/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Activity.objects.filter(activity_type='Running').exists()
        
    def test_list_activities_only_own(self, authenticated_client, create_user):
        """Test user can only see their own activities"""
        # Create another user with an activity
        other_user = create_user(username='otheruser', email='other@example.com')
        Activity.objects.create(
            user=other_user,
            activity_type='Swimming',
            duration=45,
            date=date.today()
        )
        
        # Create own activity
        Activity.objects.create(
            user=authenticated_client.user,
            activity_type='Running',
            duration=30,
            date=date.today()
        )
        
        response = authenticated_client.get('/api/activities/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['activity_type'] == 'Running'
