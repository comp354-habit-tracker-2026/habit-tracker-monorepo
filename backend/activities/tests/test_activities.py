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

    def test_retrieve_activity_detail_success(self, authenticated_client, create_activity):
        """Test retrieving full details of an owned activity (Acceptance Criteria: 200 OK)"""
        raw_data = {"heart_rate": 160, "steps": 5000}
        activity = create_activity(
            authenticated_client.user, 
            activity_type='Cycling', 
            raw_data=raw_data
        )
        
        response = authenticated_client.get(f'/api/v1/activities/{activity.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == activity.id
        assert response.data['activity_type'] == 'Cycling'
        # Verification of "Full activity details including raw_data"
        assert response.data['raw_data'] == raw_data


    def test_retrieve_other_user_activity_returns_404(self, authenticated_client, create_user, create_activity):
        """Test ownership validation (Acceptance Criteria: 404 Not Found)"""
        other_user = create_user(username='other_person', email='otherp@example.com')
        other_activity = create_activity(other_user, activity_type='Private Run')
        
        # Try to access an existing ID that belongs to someone else
        response = authenticated_client.get(f'/api/v1/activities/{other_activity.id}/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_activity_unauthorized(self, api_client, create_user, create_activity):
        """Test unauthenticated access (Acceptance Criteria: 401 Unauthorized)"""
        user = create_user(username='auth_user', email='auth@example.com')
        activity = create_activity(user)
        
        # Use the unauthenticated api_client
        response = api_client.get(f'/api/v1/activities/{activity.id}/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_activity_unauthorized(self, api_client):
     data = {
        'activity_type': 'Running',
        'duration': 45,
        'date': date.today().isoformat(),
        'distance': '10.5',
        'calories': 450
     }

     response = api_client.post('/api/v1/activities/', data, format='json')
     assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_activity_missing_activity_type(self, authenticated_client):
     data = {
        'activity_type': '',
        'duration': 45,
        'date': date.today().isoformat(),
        'distance': '10.5',
        'calories': 450
     }

     response = authenticated_client.post('/api/v1/activities/', data, format='json')
     assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_activity_invalid_duration(self, authenticated_client):
     data = {
        'activity_type': 'Running',
        'duration': -10,
        'date': date.today().isoformat(),
        'distance': '10.5',
        'calories': 450
     }

     response = authenticated_client.post('/api/v1/activities/', data, format='json')
     assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_activity_invalid_date_format(self, authenticated_client):
     data = {
        'activity_type': 'Running',
        'duration': 45,
        'date': 'invalid-date',
        'distance': '10.5',
        'calories': 450
     }

     response = authenticated_client.post('/api/v1/activities/', data, format='json')
     assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_activity_negative_distance(self, authenticated_client):
     data = {
        'activity_type': 'Cycling',
        'duration': 30,
        'date': date.today().isoformat(),
        'distance': '-5.0',
        'calories': 300
     }

     response = authenticated_client.post('/api/v1/activities/', data, format='json')
     assert response.status_code == status.HTTP_400_BAD_REQUEST

