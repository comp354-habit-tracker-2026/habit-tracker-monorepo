import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

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
    def test_logout_success(self, api_client, create_user):
            """Test successful logout blacklists refresh token"""
            user = create_user()
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
            response = api_client.post(
                '/api/v1/auth/logout/',
                {'refresh': str(refresh)},
                format='json'
            )

            assert response.status_code == status.HTTP_200_OK
            assert response.data['message'] == 'Logout successful'

    def test_logout_requires_authentication(self, api_client, create_user):
        """Test logout fails without access token"""
        user = create_user()
        refresh = RefreshToken.for_user(user)

        response = api_client.post(
            '/api/v1/auth/logout/',
            {'refresh': str(refresh)},
            format='json'
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_with_invalid_refresh_token_fails(self, api_client, create_user):
        """Test logout fails with invalid refresh token"""
        user = create_user()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.post(
            '/api/v1/auth/logout/',
            {'refresh': 'invalid-token'},
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_blacklisted_refresh_token_cannot_be_reused(self, api_client, create_user):
        """Test blacklisted refresh token cannot be used again"""
        user = create_user()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        logout_response = api_client.post(
            '/api/v1/auth/logout/',
            {'refresh': str(refresh)},
            format='json'
        )
        assert logout_response.status_code == status.HTTP_200_OK

        reuse_response = api_client.post(
            '/api/v1/auth/refresh/',
            {'refresh': str(refresh)},
            format='json'
        )

        assert reuse_response.status_code == status.HTTP_401_UNAUTHORIZED
