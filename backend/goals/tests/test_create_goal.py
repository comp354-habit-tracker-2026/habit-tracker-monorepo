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

import pytest
from datetime import date, timedelta
from goals.models import Goal

@pytest.mark.django_db
class TestCreateGoal:
    
    def test_create_goal_returns_201(self, authenticated_client):
        """Tests that the API successfully creates a goal and saves it to the DB."""
        payload = {
            'title': 'New API Goal',
            'description': 'Test Description',
            'target_value': '20.00',
            'current_value': '0.00',
            'goal_type': 'distance', 
            'status': 'active',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=60)).isoformat()
        }
        response = authenticated_client.post('/api/v1/goals/', data=payload, format='json')
        
        assert response.status_code == 201, f"API rejected payload with: {response.data}"
        assert response.data['title'] == 'New API Goal'
        assert Goal.objects.filter(title='New API Goal').exists()

    def test_create_goal_unauthenticated_returns_401(self, api_client):
        """Unauthenticated requests are rejected"""
        payload = {'title': 'New Goal'}
        response = api_client.post('/api/v1/goals/', data=payload, format='json')
        
        assert response.status_code == 401

    def test_create_goal_returns_400_on_validation_error(self, authenticated_client):
        """Triggers a 400 error by sending bad data"""
        bad_payload = {
            'title': 'Bad Goal',
            'target_value': 25.00,
            'goal_type': 'weight',
            'start_date': 'invalid_date' 
        }
        response = authenticated_client.post('/api/v1/goals/', data=bad_payload, format='json')
        
        assert response.status_code == 400
        assert response.data['type'] == 'ValidationError'
        assert 'start_date' in response.data['detail']

    def test_create_goal_returns_500_on_database_error(self, authenticated_client, mocker):
        """Database crash when request to create a goal - returns 500"""
        mocker.patch(
            'goals.business.services.GoalService.create_goal', 
            return_value={"error": "DatabaseError", "msg": "Database connection failed."}
        )
        response = authenticated_client.post('/api/v1/goals/', data={'title': 'DB Fail'}, format='json')
        
        assert response.status_code == 500
        assert response.data['detail'] == 'Database connection failed.'
        assert response.data['type'] == 'DatabaseError'