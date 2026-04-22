import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestGoogleOAuth:
    """Tests for the Google OAuth login feature (issue #83)."""

    def test_get_google_auth_url(self, api_client, settings):
        """GET /api/v1/auth/oauth/google/ returns a valid Google authorization URL."""
        settings.GOOGLE_CLIENT_ID = "test-client-id"
        settings.GOOGLE_REDIRECT_URI = "http://localhost/callback/"

        response = api_client.get("/api/v1/auth/oauth/google/")

        assert response.status_code == status.HTTP_200_OK
        assert "authorization_url" in response.data
        assert "accounts.google.com" in response.data["authorization_url"]
        assert "test-client-id" in response.data["authorization_url"]

    def test_callback_missing_code_returns_400(self, api_client):
        """GET /callback/ without a code query param returns 400."""
        response = api_client.get("/api/v1/auth/oauth/google/callback/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("users.business.services.OAuthService._get_user_info")
    @patch("users.business.services.OAuthService._exchange_code")
    def test_callback_creates_new_user(self, mock_exchange, mock_userinfo, api_client, settings):
        """A valid OAuth code for a brand-new user creates the account and returns JWTs."""
        settings.GOOGLE_CLIENT_ID = "test-client-id"
        settings.GOOGLE_CLIENT_SECRET = "test-secret"
        settings.GOOGLE_REDIRECT_URI = "http://localhost/callback/"

        mock_exchange.return_value = {"access_token": "fake-token"}
        mock_userinfo.return_value = {
            "id": "google-user-id-123",
            "email": "newuser@gmail.com",
            "given_name": "New",
            "family_name": "User",
        }

        response = api_client.get("/api/v1/auth/oauth/google/callback/?code=fake-code")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

        user = User.objects.get(email="newuser@gmail.com")
        assert user.oauth_provider == "google"
        assert user.oauth_provider_id == "google-user-id-123"
        assert not user.has_usable_password()  # OAuth user should have no password

    @patch("users.business.services.OAuthService._get_user_info")
    @patch("users.business.services.OAuthService._exchange_code")
    def test_callback_links_existing_user(self, mock_exchange, mock_userinfo, api_client, settings):
        """A valid OAuth code matching an existing user's email links the account."""
        settings.GOOGLE_CLIENT_ID = "test-client-id"
        settings.GOOGLE_CLIENT_SECRET = "test-secret"
        settings.GOOGLE_REDIRECT_URI = "http://localhost/callback/"

        existing_user = User.objects.create_user(
            username="existing",
            email="existing@gmail.com",
            password="TestPass123!",
        )

        mock_exchange.return_value = {"access_token": "fake-token"}
        mock_userinfo.return_value = {
            "id": "google-user-id-456",
            "email": "existing@gmail.com",
            "given_name": "Existing",
            "family_name": "User",
        }

        response = api_client.get("/api/v1/auth/oauth/google/callback/?code=fake-code")

        assert response.status_code == status.HTTP_200_OK
        existing_user.refresh_from_db()
        assert existing_user.oauth_provider == "google"
        assert existing_user.oauth_provider_id == "google-user-id-456"

    @patch("users.business.services.OAuthService._exchange_code")
    def test_callback_invalid_code_returns_400(self, mock_exchange, api_client, settings):
        """An invalid/expired authorization code returns 400."""
        settings.GOOGLE_CLIENT_ID = "test-client-id"
        settings.GOOGLE_CLIENT_SECRET = "test-secret"
        settings.GOOGLE_REDIRECT_URI = "http://localhost/callback/"

        mock_exchange.side_effect = ValueError("Invalid or expired authorization code")

        response = api_client.get("/api/v1/auth/oauth/google/callback/?code=bad-code")
        assert response.status_code == status.HTTP_400_BAD_REQUEST