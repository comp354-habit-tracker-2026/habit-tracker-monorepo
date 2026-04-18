import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
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
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)
    return _create_user

@pytest.fixture
def auth_token(create_user):
    user = create_user()
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

@pytest.mark.django_db
class TestJWTAuthenticationMiddleware:

    def test_valid_bearer_token_passes(self, api_client, auth_token):
        """Valid Bearer token should pass through middleware"""
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_token}')
        response = api_client.get('/api/v1/activities/')
        assert response.status_code == status.HTTP_200_OK

    def test_no_auth_header_passes_to_simplejwt(self, api_client):
        """No auth header on protected endpoint — middleware passes, DRF returns 401"""
        response = api_client.get('/api/v1/activities/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_malformed_header_missing_token(self, api_client):
        """Authorization: Bearer with no token → 400"""
        api_client.credentials(HTTP_AUTHORIZATION='Bearer')
        response = api_client.get('/api/v1/activities/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.json()

    def test_wrong_auth_scheme(self, api_client, auth_token):
        """Authorization: Basic <token> → 400"""
        api_client.credentials(HTTP_AUTHORIZATION=f'Basic {auth_token}')
        response = api_client.get('/api/v1/activities/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.json()

    def test_too_many_parts_in_header(self, api_client, auth_token):
        """Authorization: Bearer <token> extra → 400"""
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_token} extra')
        response = api_client.get('/api/v1/activities/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.json()

    def test_login_endpoint_is_exempt(self, api_client):
        """Login endpoint should skip middleware validation"""
        response = api_client.post('/api/v1/auth/login/', {
            'username': 'nobody',
            'password': 'wrongpass'
        }, format='json')
        # should get 401 from SimpleJWT, not 400 from middleware
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_register_endpoint_is_exempt(self, api_client):
        """Register endpoint should skip middleware validation"""
        response = api_client.post('/api/v1/auth/register/', {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!'
        }, format='json')
        # should get 201, not 400 from middleware
        assert response.status_code == status.HTTP_201_CREATED