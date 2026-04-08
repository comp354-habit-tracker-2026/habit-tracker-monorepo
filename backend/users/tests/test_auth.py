import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken

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

    def test_login_access_token_contains_user_claims(self, api_client, create_user):
        """Test login access token includes expected user claims."""
        user = create_user(email='claims@test.com')
        data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }

        response = api_client.post('/api/v1/auth/login/', data, format='json')
        assert response.status_code == status.HTTP_200_OK

        access = response.data['access']
        token = AccessToken(access)
        assert token['user_id'] == user.id
        assert token['username'] == user.username
        assert token['email'] == user.email
        assert token['is_staff'] is False
        assert token['is_superuser'] is False

    def test_protected_route_without_token_fails(self, api_client):
        """Test accessing protected route without token fails"""
        response = api_client.get('/api/v1/goals/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_oauth_user_creation(self):
        """Test creating user with OAuth provider info"""
        user = User.objects.create_user(
            username='oauth_user',
            email='oauth@test.com',
            password='unused_password',
            oauth_provider='strava',
            oauth_provider_id='strava_12345'
        )
        assert user.oauth_provider == 'strava'
        assert user.oauth_provider_id == 'strava_12345'
        
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

    def test_logout_blacklists_refresh_token(self, api_client, create_user):
        """Test logout blacklists the refresh token"""
        create_user()
        login_data = {'username': 'testuser', 'password': 'TestPass123!'}
        login_response = api_client.post('/api/v1/auth/login/', login_data, format='json')
        refresh_token = login_response.data['refresh']

        logout_response = api_client.post('/api/v1/auth/logout/', {'refresh': refresh_token}, format='json')
        assert logout_response.status_code == status.HTTP_200_OK

    def test_logout_invalidates_refresh_token(self, api_client, create_user):
        """Test that a blacklisted refresh token cannot be reused"""
        create_user()
        login_data = {'username': 'testuser', 'password': 'TestPass123!'}
        login_response = api_client.post('/api/v1/auth/login/', login_data, format='json')
        refresh_token = login_response.data['refresh']

        api_client.post('/api/v1/auth/logout/', {'refresh': refresh_token}, format='json')

        # Attempt to use the blacklisted token
        refresh_response = api_client.post('/api/v1/auth/refresh/', {'refresh': refresh_token}, format='json')
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_without_token_fails(self, api_client):
        """Test logout without a refresh token returns 400"""
        response = api_client.post('/api/v1/auth/logout/', {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
