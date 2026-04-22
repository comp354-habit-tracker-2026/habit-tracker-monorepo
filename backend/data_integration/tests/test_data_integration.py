import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    def _create_user(**kwargs):
        defaults = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)

    return _create_user


@pytest.fixture
def authenticated_client(api_client, create_user):
    user = create_user(
        username="integrationuser",
        email="integration@test.com",
        password="TestPass123!",
    )
    api_client.user = user
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.mark.django_db
def test_list_data_integrations_returns_business_data(authenticated_client):
    response = authenticated_client.get("/api/v1/data-integrations/")

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    assert len(response.data) >= 1
    assert "provider" in response.data[0]
    assert "is_synced" in response.data[0]
    assert "consent_granted" in response.data[0]


@pytest.mark.django_db
def test_grant_and_revoke_data_integration_consent(authenticated_client):
    grant_response = authenticated_client.post(
        "/api/v1/data-integrations/consent/",
        {"provider": "strava", "consent_granted": True},
        format="json",
    )

    assert grant_response.status_code == status.HTTP_200_OK
    assert grant_response.data["provider"] == "strava"
    assert grant_response.data["consent_granted"] is True
    assert grant_response.data["status"] == "active"

    revoke_response = authenticated_client.post(
        "/api/v1/data-integrations/consent/",
        {"provider": "strava", "consent_granted": False},
        format="json",
    )

    assert revoke_response.status_code == status.HTTP_200_OK
    assert revoke_response.data["provider"] == "strava"
    assert revoke_response.data["consent_granted"] is False
    assert revoke_response.data["status"] == "revoked"


@pytest.mark.django_db
def test_privacy_history_records_each_user_status_change(authenticated_client):
    authenticated_client.post(
        "/api/v1/data-integrations/consent/",
        {"provider": "strava", "consent_granted": True},
        format="json",
    )
    authenticated_client.post(
        "/api/v1/data-integrations/consent/",
        {"provider": "strava", "consent_granted": False},
        format="json",
    )

    history_response = authenticated_client.get("/api/v1/data-integrations/privacy-history/")

    assert history_response.status_code == status.HTTP_200_OK
    assert len(history_response.data) == 2
    assert history_response.data[0]["provider"] == "strava"
    assert history_response.data[0]["consent_granted"] is False
    assert history_response.data[1]["consent_granted"] is True


@pytest.mark.django_db
def test_privacy_history_is_personal_to_authenticated_user(api_client, create_user):
    user_one = create_user(username="userone", email="userone@test.com", password="TestPass123!")
    user_two = create_user(username="usertwo", email="usertwo@test.com", password="TestPass123!")

    user_one_client = APIClient()
    user_one_refresh = RefreshToken.for_user(user_one)
    user_one_client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_one_refresh.access_token}")

    user_two_client = APIClient()
    user_two_refresh = RefreshToken.for_user(user_two)
    user_two_client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_two_refresh.access_token}")

    user_one_client.post(
        "/api/v1/data-integrations/consent/",
        {"provider": "strava", "consent_granted": False},
        format="json",
    )
    user_two_client.post(
        "/api/v1/data-integrations/consent/",
        {"provider": "mapmyrun", "consent_granted": False},
        format="json",
    )

    user_one_history = user_one_client.get("/api/v1/data-integrations/privacy-history/")

    assert user_one_history.status_code == status.HTTP_200_OK
    assert len(user_one_history.data) == 1
    assert user_one_history.data[0]["provider"] == "strava"

