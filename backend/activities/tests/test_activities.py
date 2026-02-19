import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from activities.models import Activity
from datetime import date
import json

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    def _create_user(**kwargs):
        defaults = {
            'username': 'testuser',
            'email': 'test@example.com',
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
def create_activity():
    def _create_activity(user, **kwargs):
        defaults = {
            'activity_type': 'Running',
            'duration': 30,
            'date': date.today(),
            'provider': 'manual'
        }
        defaults.update(kwargs)
        return Activity.objects.create(user=user, **defaults)
    return _create_activity

@pytest.mark.django_db
class TestActivities:
    def test_create_manual_activity(self, authenticated_client):
        """Test creating a manual activity entry"""
        data = {
            'activity_type': 'Running',
            'duration': 45,
            'date': date.today().isoformat(),
            'distance': '10.5',
            'calories': 450
        }
        response = authenticated_client.post('/api/v1/activities/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Activity.objects.filter(activity_type='Running').exists()
        
        activity = Activity.objects.get(activity_type='Running')
        assert activity.provider == 'manual'  # Default provider
        assert activity.distance is not None
        assert float(activity.distance) == 10.5
        assert activity.calories == 450
        
    def test_create_external_activity(self, authenticated_client):
        """Test creating an activity from external provider"""
        raw_strava_data = {
            'id': 12345,
            'name': 'Morning Run',
            'distance': 5000,
            'moving_time': 1800,
            'total_elevation_gain': 50
        }
        
        data = {
            'activity_type': 'Running',
            'duration': 30,
            'date': date.today().isoformat(),
            'provider': 'strava',
            'external_id': '12345',
            'distance': '5.0',
            'raw_data': raw_strava_data  # Send as dict, not JSON string
        }
        response = authenticated_client.post('/api/v1/activities/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        
        activity = Activity.objects.get(external_id='12345')
        assert activity.provider == 'strava'
        assert activity.raw_data['id'] == 12345
        
    def test_prevent_duplicate_external_activity(self, authenticated_client):
        """Test that duplicate external activities are prevented"""
        data = {
            'activity_type': 'Running',
            'duration': 30,
            'date': date.today().isoformat(),
            'provider': 'strava',
            'external_id': '12345'
        }
        
        # Create first activity
        response1 = authenticated_client.post('/api/v1/activities/', data, format='json')
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Try to create duplicate
        response2 = authenticated_client.post('/api/v1/activities/', data, format='json')
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        
    def test_list_activities_with_pagination(self, authenticated_client, create_activity):
        """Test activities list is paginated"""
        # Create 25 activities
        for i in range(25):
            create_activity(
                authenticated_client.user,
                activity_type=f'Activity {i}',
                date=date.today()
            )
            
        response = authenticated_client.get('/api/v1/activities/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert 'count' in response.data
        assert 'next' in response.data
        assert len(response.data['results']) == 20  # Default page size
        
    def test_list_activities_only_own(self, authenticated_client, create_user, create_activity):
        """Test user can only see their own activities"""
        other_user = create_user(username='otheruser', email='other@example.com')
        
        # Create activities for different users
        create_activity(other_user, activity_type='Swimming')
        create_activity(authenticated_client.user, activity_type='Running')
        
        response = authenticated_client.get('/api/v1/activities/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['activity_type'] == 'Running'
        
    def test_filter_activities_by_provider(self, authenticated_client, create_activity):
        """Test filtering activities by provider"""
        create_activity(authenticated_client.user, provider='manual')
        create_activity(authenticated_client.user, provider='strava', external_id='123')
        create_activity(authenticated_client.user, provider='mapmyrun', external_id='456')
        
        response = authenticated_client.get('/api/v1/activities/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
        
    def test_activity_date_filtering(self, authenticated_client, create_activity):
        """Test activities can be filtered by date range"""
        from datetime import timedelta
        
        today = date.today()
        create_activity(authenticated_client.user, date=today - timedelta(days=7))
        create_activity(authenticated_client.user, date=today)
        create_activity(authenticated_client.user, date=today + timedelta(days=7))
        
        response = authenticated_client.get('/api/v1/activities/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
