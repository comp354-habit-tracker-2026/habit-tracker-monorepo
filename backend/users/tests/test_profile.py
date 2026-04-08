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
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!",
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)
    return _create_user


@pytest.fixture
def authenticated_client(api_client, create_user):
    user = create_user()
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    api_client.user = user
    return api_client


@pytest.mark.django_db
class TestUserProfileViewing:
    def test_authenticated_user_can_view_profile(self, authenticated_client):
        response = authenticated_client.get("/api/v1/auth/profile/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == authenticated_client.user.username
        assert response.data["email"] == authenticated_client.user.email

    def test_unauthenticated_user_cannot_view_profile(self, api_client):
        response = api_client.get("/api/v1/auth/profile/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_sensitive_fields_not_exposed(self, authenticated_client):
        response = authenticated_client.get("/api/v1/auth/profile/")

        assert response.status_code == status.HTTP_200_OK
        assert "password" not in response.data