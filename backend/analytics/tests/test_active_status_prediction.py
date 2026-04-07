from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from activities.models import Activity
from analytics.business import AnalyticsService


User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def _create_user(**kwargs):
        defaults = {
            "username": "analytics_user",
            "email": "analytics@test.com",
            "password": "StrongPass123!",
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


@pytest.fixture
def create_activity():
    def _create_activity(user, **kwargs):
        defaults = {
            "activity_type": "Running",
            "duration": 30,
            "date": date.today(),
            "provider": "manual",
        }
        defaults.update(kwargs)
        return Activity.objects.create(user=user, **defaults)

    return _create_activity


@pytest.mark.django_db
def test_predict_activity_status_inactive_when_no_activity(create_user):
    user = create_user(username="noactivity", email="noactivity@test.com")

    result = AnalyticsService().predict_activity_status(user)

    assert result["is_active"] is False
    assert result["probability_active"] < 0.5
    assert 1 <= result["activity_score"] <= 100
    assert result["activity_score"] < 50
    assert result["signals"]["total_activity_count"] == 0


@pytest.mark.django_db
def test_predict_activity_status_active_with_recent_consistent_activity(create_user, create_activity):
    user = create_user(username="veryactive", email="veryactive@test.com")

    create_activity(user, duration=60, date=date.today())
    create_activity(user, duration=45, date=date.today() - timedelta(days=1))
    create_activity(user, duration=35, date=date.today() - timedelta(days=2))

    result = AnalyticsService().predict_activity_status(user)

    assert result["is_active"] is True
    assert result["probability_active"] >= 0.75
    assert 1 <= result["activity_score"] <= 100
    assert result["activity_score"] >= 75
    assert result["signals"]["weekly_sessions"] == 3


@pytest.mark.django_db
def test_overview_includes_active_status_prediction(authenticated_client):
    response = authenticated_client.get("/api/v1/analytics/overview/")

    assert response.status_code == status.HTTP_200_OK
    assert "active_status_prediction" in response.data
    assert "is_active" in response.data["active_status_prediction"]
    assert "probability_active" in response.data["active_status_prediction"]
    assert "activity_score" in response.data["active_status_prediction"]


@pytest.mark.django_db
def test_overview_prediction_uses_only_request_user_data(authenticated_client, create_user, create_activity):
    other_user = create_user(username="otheruser", email="otheruser@test.com")
    create_activity(other_user, duration=120, date=date.today())

    response = authenticated_client.get("/api/v1/analytics/overview/")

    assert response.status_code == status.HTTP_200_OK
    prediction = response.data["active_status_prediction"]
    assert prediction["signals"]["total_activity_count"] == 0
    assert prediction["is_active"] is False


@pytest.mark.django_db
def test_health_indicators_returns_score_and_metrics(authenticated_client, create_activity):
    user = authenticated_client.user
    create_activity(user, duration=40, date=date.today() - timedelta(days=2))
    create_activity(user, duration=30, date=date.today() - timedelta(days=1))

    start_date = (date.today() - timedelta(days=7)).isoformat()
    end_date = date.today().isoformat()

    response = authenticated_client.get(
        f"/api/v1/analytics/health-indicators/?userId={user.id}&window=weekly&from={start_date}&to={end_date}"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["userId"] == str(user.id)
    assert response.data["window"] == "weekly"
    assert response.data["range"]["from"] == start_date
    assert response.data["range"]["to"] == end_date
    assert "healthScore" in response.data
    assert 0 <= response.data["healthScore"] <= 100
    assert "indicators" in response.data
    assert "volume" in response.data["indicators"]
    assert "consistency" in response.data["indicators"]
    assert "alerts" in response.data
    assert "inactive" in response.data["alerts"]
    assert "reason" in response.data["alerts"]
    assert "explanations" in response.data
    assert len(response.data["explanations"]) == 3


@pytest.mark.django_db
def test_health_indicators_rejects_missing_query_params(authenticated_client):
    response = authenticated_client.get("/api/v1/analytics/health-indicators/")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "errors" in response.data
    assert "userId" in response.data["errors"]
    assert "from" in response.data["errors"]
    assert "to" in response.data["errors"]


@pytest.mark.django_db
def test_health_indicators_rejects_other_user_id(authenticated_client, create_user):
    other_user = create_user(username="another", email="another@test.com")
    start_date = (date.today() - timedelta(days=7)).isoformat()
    end_date = date.today().isoformat()

    response = authenticated_client.get(
        f"/api/v1/analytics/health-indicators/?userId={other_user.id}&from={start_date}&to={end_date}"
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "errors" in response.data


@pytest.mark.django_db
def test_health_indicators_rejects_invalid_date_range(authenticated_client):
    user = authenticated_client.user
    from_date = date.today().isoformat()
    to_date = (date.today() - timedelta(days=2)).isoformat()

    response = authenticated_client.get(
        f"/api/v1/analytics/health-indicators/?userId={user.id}&from={from_date}&to={to_date}"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "errors" in response.data


@pytest.mark.django_db
def test_health_indicators_rejects_invalid_window(authenticated_client):
    user = authenticated_client.user
    start_date = (date.today() - timedelta(days=7)).isoformat()
    end_date = date.today().isoformat()

    response = authenticated_client.get(
        f"/api/v1/analytics/health-indicators/?userId={user.id}&window=yearly&from={start_date}&to={end_date}"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "errors" in response.data
    assert "window" in response.data["errors"]
