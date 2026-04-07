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

        login_data = {'username': 'testuser', 'password': 'TestPass123!'}
        login_response = api_client.post('/api/v1/auth/login/', login_data, format='json')
        refresh_token = login_response.data['refresh']

        refresh_data = {'refresh': refresh_token}
        refresh_response = api_client.post('/api/v1/auth/refresh/', refresh_data, format='json')
        assert refresh_response.status_code == status.HTTP_200_OK
        assert 'access' in refresh_response.data

    def test_password_reset_request_existing_user(self, api_client, create_user):
        user = create_user(email='reset@test.com')

        response = api_client.post(
            '/api/v1/auth/password-reset/request/',
            {'email': user.email},
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK
        assert 'uid' in response.data
        assert 'token' in response.data

    def test_password_reset_request_nonexistent_user(self, api_client):
        response = api_client.post(
            '/api/v1/auth/password-reset/request/',
            {'email': 'doesnotexist@test.com'},
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data

    def test_password_reset_confirm_success(self, api_client, create_user):
        user = create_user(email='resetconfirm@test.com')

        request_response = api_client.post(
            '/api/v1/auth/password-reset/request/',
            {'email': user.email},
            format='json'
        )

        response = api_client.post(
            '/api/v1/auth/password-reset/confirm/',
            {
                'uid': request_response.data['uid'],
                'token': request_response.data['token'],
                'password': 'NewStrongPass123!'
            },
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.check_password('NewStrongPass123!')

    def test_password_reset_confirm_invalid_token(self, api_client, create_user):
        user = create_user(email='invalidtoken@test.com')

        response = api_client.post(
            '/api/v1/auth/password-reset/confirm/',
            {
                'uid': user.pk,
                'token': 'invalid-token',
                'password': 'NewStrongPass123!'
            },
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_password_reset_confirm_invalid_user(self, api_client):
        response = api_client.post(
            '/api/v1/auth/password-reset/confirm/',
            {
                'uid': 999999,
                'token': 'some-token',
                'password': 'NewStrongPass123!'
            },
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
