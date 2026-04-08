import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

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

@pytest.mark.django_db
class TestAuthentication:
    def test_user_registration_success(self, api_client):
        """Test successful user registration"""
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        response = api_client.post('/api/v1/auth/register/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username='newuser').exists()
        assert 'password' not in response.data
        
    def test_user_registration_password_mismatch(self, api_client):
        """Test registration fails with mismatched passwords"""
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'TestPass123!',
            'password2': 'DifferentPass123!'
        }
        response = api_client.post('/api/v1/auth/register/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_returns_token(self, api_client, create_user):
        """Test login returns JWT tokens"""
        create_user()
        data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        response = api_client.post('/api/v1/auth/login/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_protected_route_without_token_fails(self, api_client):
        """Test accessing protected route without token fails"""
        response = api_client.get('/api/v1/goals/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_oauth_fields_moved_to_connected_account(self):
        """oauth_provider and oauth_provider_id no longer live on User.
        External provider links are stored in ConnectedAccount (activities app)
        so that a user can connect more than one platform at a time.
        """
        user = User.objects.create_user(
            username='oauth_user',
            email='oauth@test.com',
            password='unused_password',
        )
        assert not hasattr(user, 'oauth_provider')
        assert not hasattr(user, 'oauth_provider_id')
        
    def test_token_refresh(self, api_client, create_user):
        """Test refreshing access token"""
        create_user()
        # Login first
        login_data = {'username': 'testuser', 'password': 'TestPass123!'}
        login_response = api_client.post('/api/v1/auth/login/', login_data, format='json')
        refresh_token = login_response.data['refresh']
        
        # Use refresh token
        refresh_data = {'refresh': refresh_token}
        refresh_response = api_client.post('/api/v1/auth/refresh/', refresh_data, format='json')
        assert refresh_response.status_code == status.HTTP_200_OK
        assert 'access' in refresh_response.data
