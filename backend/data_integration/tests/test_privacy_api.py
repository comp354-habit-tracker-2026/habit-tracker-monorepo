from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import DatabaseError
from rest_framework import status
from rest_framework.test import APIClient

from data_integration.models import PrivacyAuditLog, PrivacyStatus

User = get_user_model()

@pytest.fixture
def service_token():
    payload = {
        "service_name": "provider-service",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


@pytest.fixture
def service_client(service_token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {service_token}")
    return client


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        username="privacy_user",
        email="privacy@test.com",
        password="TestPass123!",
    )


@pytest.mark.django_db
def test_tc23_valid_request_with_active_privacy_record(service_client, test_user):
    PrivacyStatus.objects.create(
        user=test_user,
        provider_id="strava",
        scope="activities.read",
        is_enabled=False,
    )

    response = service_client.post(
        "/api/privacy/verify",
        {"userId": test_user.id, "providerId": "strava", "scope": "activities.read"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["allowed"] is True
    assert response.data["reason"] == "PRIVACY_DISABLED"
    assert len(response.data["history"]) >= 1


@pytest.mark.django_db
def test_tc24_valid_request_no_privacy_record(service_client, test_user):
    response = service_client.post(
        "/api/privacy/verify",
        {"userId": test_user.id, "providerId": "strava", "scope": "activities.read"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["allowed"] is False
    assert response.data["reason"] == "PRIVACY_RECORD_NOT_FOUND"
    assert PrivacyAuditLog.objects.count() == 1


@pytest.mark.django_db
def test_tc25_invalid_jwt_returns_401_no_db_query_no_audit(test_user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Bearer invalid-token")

    with patch("data_integration.presentation.privacy_views.PrivacyStatus.objects.filter") as mock_filter:
        response = client.post(
            "/api/privacy/verify",
            {"userId": test_user.id, "providerId": "strava", "scope": "activities.read"},
            format="json",
        )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert PrivacyAuditLog.objects.count() == 0
    mock_filter.assert_not_called()


@pytest.mark.django_db
def test_tc26_missing_parameters_returns_400(service_client, test_user):
    response = service_client.post(
        "/api/privacy/verify",
        {"userId": test_user.id, "providerId": "strava"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_tc27_database_failure_returns_500(service_client, test_user):
    with patch(
        "data_integration.presentation.privacy_views.PrivacyStatus.objects.filter",
        side_effect=DatabaseError("db unavailable"),
    ):
        response = service_client.post(
            "/api/privacy/verify",
            {"userId": test_user.id, "providerId": "strava", "scope": "activities.read"},
            format="json",
        )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.django_db
def test_tc28_retrieve_history_only(service_client, test_user):
    PrivacyAuditLog.objects.create(
        caller_service="provider-service",
        requested_user_id=test_user.id,
        provider_id="strava",
        scope="activities.read",
        decision=PrivacyAuditLog.Decision.DENY,
        reason="PRIVACY_ENABLED",
        action=PrivacyAuditLog.Action.VERIFY,
    )

    response = service_client.get(f"/api/privacy/history?userId={test_user.id}")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 1
    assert response.data[0]["requested_user_id"] == test_user.id


@pytest.mark.django_db
def test_update_privacy_status_creates_or_updates_record(service_client, test_user):
    response = service_client.post(
        "/api/privacy/update",
        {
            "userId": test_user.id,
            "providerId": "strava",
            "scope": "activities.read",
            "privacyEnabled": True,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    record = PrivacyStatus.objects.get(user_id=test_user.id, provider_id="strava", scope="activities.read")
    assert record.is_enabled is True
